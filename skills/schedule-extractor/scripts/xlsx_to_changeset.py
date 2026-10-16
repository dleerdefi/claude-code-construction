#!/usr/bin/env python3
"""Parse an anchored schedule Excel file and compute a reconciliation changeset.

Reads the _agentcm_meta sheet for anchor IDs, reads the data sheet with _row_key
column, reads the schedule's stored rows from AgentCM's API
(GET {api_url}/projects/{project_id}/schedules/{schedule_id}/rows), and outputs a JSON
changeset suitable for POST to /api/projects/:id/schedules/reconcile.

Usage:
    python xlsx_to_changeset.py --excel edited.xlsx [--database-yaml .construction/database.yaml]
                                [--api-url URL --project-id ID] [--output changeset.json]

project_id and api_url come from --project-id/--api-url, or else from database.yaml, of which
nothing else is read. If --output is omitted, prints JSON to stdout.

Exit codes: 0 changeset written; 1 bad input or AgentCM refused the read; 3 AgentCM is not
answering at api_url (start it and rerun: nothing was computed).
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PAGE = 500  # the rows endpoint's largest page
NOT_ANSWERING = 3


def read_meta(wb):
    """Extract reconciliation anchors from the _agentcm_meta sheet."""
    if "_agentcm_meta" not in wb.sheetnames:
        print("ERROR: No _agentcm_meta sheet found. This Excel was not exported by AgentCM.", file=sys.stderr)
        sys.exit(1)

    meta_ws = wb["_agentcm_meta"]
    meta = {}
    for row in meta_ws.iter_rows(min_row=1, max_col=2, values_only=True):
        if row[0] and row[1]:
            meta[str(row[0]).strip()] = str(row[1]).strip()

    required = ["schedule_id", "schedule_type"]
    for key in required:
        if key not in meta or not meta[key]:
            print(f"ERROR: _agentcm_meta missing required field: {key}", file=sys.stderr)
            sys.exit(1)

    return meta


def read_data(wb, meta):
    """Read the data sheet, returning headers and rows keyed by _row_key."""
    # Data sheet is the first visible sheet
    data_ws = None
    for name in wb.sheetnames:
        if name != "_agentcm_meta":
            data_ws = wb[name]
            break

    if data_ws is None:
        print("ERROR: No data worksheet found.", file=sys.stderr)
        sys.exit(1)

    # Find header row (row with _row_key in column A)
    header_row = None
    for row_idx, row in enumerate(data_ws.iter_rows(min_row=1, max_col=1, values_only=True), 1):
        if row[0] and str(row[0]).strip() == "_row_key":
            header_row = row_idx
            break

    if header_row is None:
        print("ERROR: Could not find _row_key header in column A.", file=sys.stderr)
        sys.exit(1)

    # Read column headers (B onward)
    headers = []
    for col_idx in range(2, data_ws.max_column + 1):
        val = data_ws.cell(row=header_row, column=col_idx).value
        if val is not None:
            headers.append(str(val).strip())
        else:
            break

    # Read data rows
    excel_rows = {}  # row_key -> {col: value}
    new_rows = []    # rows with empty _row_key (PE-added rows)

    for row_idx in range(header_row + 1, data_ws.max_row + 1):
        row_key = data_ws.cell(row=row_idx, column=1).value

        cells = {}
        has_data = False
        for col_offset, header in enumerate(headers):
            val = data_ws.cell(row=row_idx, column=col_offset + 2).value
            cell_str = str(val).strip() if val is not None else None
            cells[header] = cell_str
            if cell_str:
                has_data = True

        if not has_data:
            continue  # skip fully empty rows

        if row_key and str(row_key).strip():
            excel_rows[str(row_key).strip()] = cells
        else:
            new_rows.append(cells)

    return headers, excel_rows, new_rows


class AgentCMNotAnswering(Exception):
    """No connection to api_url: AgentCM is not running, or not at that address."""


class AgentCMRefused(Exception):
    """AgentCM answered, with an error or something other than a list of rows."""


def agentcm_address(database_yaml, api_url=None, project_id=None):
    """project_id and api_url: the arguments, else database.yaml's two promised keys, nothing else."""
    if not (api_url and project_id):
        import yaml
        path = Path(database_yaml)
        if not path.is_file():
            raise AgentCMRefused(f"{database_yaml} not found: give --api-url and --project-id")
        conf = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        api_url = api_url or conf.get("api_url")
        project_id = project_id or conf.get("project_id")
    if not (api_url and project_id):
        raise AgentCMRefused(f"{database_yaml} has no api_url or project_id")
    return str(api_url).rstrip("/"), str(project_id)


def http_get_json(url, timeout=30):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        raise AgentCMRefused(f"GET {url} answered {e.code}: {body}") from e
    except urllib.error.URLError as e:
        raise AgentCMNotAnswering(f"no answer from {url}: {e.reason}") from e
    except (ConnectionError, TimeoutError) as e:
        raise AgentCMNotAnswering(f"no answer from {url}: {e}") from e
    except json.JSONDecodeError as e:
        raise AgentCMRefused(f"GET {url} did not return JSON: {e}") from e


def stored_row_key(row):
    """A row's id, or the whole row when it has none."""
    return row.get("id") or json.dumps(row, sort_keys=True)


def fetch_rows(api_url, project_id, schedule_id, get=http_get_json, page=PAGE):
    """Every stored row of the schedule, a page at a time until a short page.

    Rows are keyed by their id, so an endpoint that ignores limit/offset (and returns every row
    each time) ends the loop instead of repeating it.
    """
    base = (f"{api_url}/projects/{urllib.parse.quote(project_id)}"
            f"/schedules/{urllib.parse.quote(schedule_id)}/rows")
    rows, seen, offset = [], set(), 0
    while True:
        batch = get(f"{base}?limit={page}&offset={offset}")
        if not isinstance(batch, list):
            raise AgentCMRefused(f"GET {base} returned {type(batch).__name__}, not a list of rows")
        new = [r for r in batch if stored_row_key(r) not in seen]
        for r in new:
            seen.add(stored_row_key(r))
        rows.extend(new)
        if len(batch) < page or not new:
            return rows
        offset += len(batch)


def db_state(rows):
    """entityIdentifier -> {column key: value}, and every column key a row holds."""
    db_rows, db_columns = {}, set()
    for r in rows:
        key = r.get("entityIdentifier")
        if key is None:
            raise AgentCMRefused(f"a stored row has no entityIdentifier: {json.dumps(r)[:200]}")
        cells = {}
        for col, val in (r.get("data") or {}).items():
            cells[col] = None if val is None else str(val)
            db_columns.add(col)
        db_rows[str(key)] = cells
    return db_rows, db_columns


def compute_changeset(meta, excel_headers, excel_rows, new_rows, db_rows, db_columns):
    """Compute the diff between Excel state and DB state."""
    changeset = {
        "scheduleId": meta["schedule_id"],
        "sourceFile": meta.get("source_file", ""),
        "cellUpdates": [],
        "rowAdds": [],
        "rowDeletes": [],
        "columnAdds": [],
        "columnHides": [],
    }

    excel_header_set = set(excel_headers)

    # --- Cell updates: compare matching rows ---
    for row_key, excel_cells in excel_rows.items():
        if row_key not in db_rows:
            continue  # new row (handled below)

        db_cells = db_rows[row_key]
        for col, excel_val in excel_cells.items():
            if col not in db_columns:
                continue  # new column (handled below)
            db_val = db_cells.get(col)

            # Normalize for comparison (treat None and empty string as equivalent)
            norm_excel = (excel_val or "").strip()
            norm_db = (db_val or "").strip()

            if norm_excel != norm_db:
                changeset["cellUpdates"].append({
                    "rowKey": row_key,
                    "columnKey": col,
                    "newValue": excel_val,
                })

    # --- New rows: row_key in Excel but not in DB ---
    for row_key, excel_cells in excel_rows.items():
        if row_key not in db_rows:
            changeset["rowAdds"].append({
                "entityIdentifier": row_key,
                "cells": excel_cells,
            })

    # --- PE-added rows (empty _row_key) ---
    # These need natural key inference — include the first non-empty cell as identifier
    for cells in new_rows:
        # Use first non-empty value as entity identifier
        entity_id = ""
        for header in excel_headers:
            if cells.get(header):
                entity_id = cells[header]
                break
        if entity_id:
            changeset["rowAdds"].append({
                "entityIdentifier": entity_id,
                "cells": cells,
            })

    # --- Deleted rows: row_key in DB but not in Excel ---
    for row_key in db_rows:
        if row_key not in excel_rows:
            changeset["rowDeletes"].append({"rowKey": row_key})

    # --- New columns: in Excel headers but not in DB ---
    for header in excel_headers:
        if header not in db_columns:
            changeset["columnAdds"].append({
                "key": header,
                "header": header,
            })

    # --- Hidden columns: in DB but not in Excel headers ---
    for col in db_columns:
        if col not in excel_header_set:
            changeset["columnHides"].append({"key": col})

    return changeset


def main():
    parser = argparse.ArgumentParser(description="Parse anchored Excel and compute reconciliation changeset")
    parser.add_argument("--excel", required=True, help="Path to the edited Excel file")
    parser.add_argument("--database-yaml", default=".construction/database.yaml",
                        help="Where project_id and api_url are (default: .construction/database.yaml)")
    parser.add_argument("--api-url", help="AgentCM's API address (default: api_url in database.yaml)")
    parser.add_argument("--project-id", help="The project's id (default: project_id in database.yaml)")
    parser.add_argument("--output", "-o", help="Output JSON file (default: stdout)")
    args = parser.parse_args()

    try:
        from openpyxl import load_workbook
    except ImportError:
        print("ERROR: openpyxl not installed. Run: pip install openpyxl", file=sys.stderr)
        sys.exit(1)

    # Read Excel
    wb = load_workbook(args.excel, data_only=True)
    meta = read_meta(wb)
    if meta["schedule_id"].lower() == "none":
        print("ERROR: this table was never ingested into AgentCM (schedule_id=none), so there is nothing to "
              "reconcile: ingest it first (Step 6).", file=sys.stderr)
        sys.exit(1)
    if not meta.get("source_file"):
        meta["source_file"] = Path(args.excel).name  # AgentCM's change log: "Reconciled from <file>"
    excel_headers, excel_rows, new_rows = read_data(wb, meta)

    # The schedule's stored rows, from AgentCM's API
    try:
        api_url, project_id = agentcm_address(args.database_yaml, args.api_url, args.project_id)
        db_rows, db_columns = db_state(fetch_rows(api_url, project_id, meta["schedule_id"]))
    except AgentCMNotAnswering as e:
        print(f"AgentCM is not answering ({e}). Start AgentCM and rerun this step: nothing was computed.",
              file=sys.stderr)
        sys.exit(NOT_ANSWERING)
    except AgentCMRefused as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Compute changeset
    changeset = compute_changeset(meta, excel_headers, excel_rows, new_rows, db_rows, db_columns)

    # Summary
    summary = {
        "cellUpdates": len(changeset["cellUpdates"]),
        "rowAdds": len(changeset["rowAdds"]),
        "rowDeletes": len(changeset["rowDeletes"]),
        "columnAdds": len(changeset["columnAdds"]),
        "columnHides": len(changeset["columnHides"]),
    }
    total = sum(summary.values())

    if total == 0:
        print("No changes detected between Excel and AgentCM's stored rows.", file=sys.stderr)

    # Output
    output_json = json.dumps(changeset, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output_json, encoding="utf-8")
        print(f"OK: {args.output} ({total} changes: {summary})", file=sys.stderr)
    else:
        print(output_json)
        print(f"({total} changes: {summary})", file=sys.stderr)


if __name__ == "__main__":
    main()
