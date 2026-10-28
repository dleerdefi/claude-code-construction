#!/usr/bin/env python3
"""Read a table AgentCM wrote in .construction/schedules/<sheet>-<n>.tsv into schedule_to_xlsx.py's data,
and, for a table not yet ingested, the schedules/ingest payload (AgentCM's contract).

AgentCM writes two kinds of table file (its .construction/CLAUDE.md):
- read from the sheet's text: a header line `y x0.100 x0.200 ...`, then one line per row of text, its
  position y first, the table's own header rows at the top (a title line may come before them);
- ingested into AgentCM: a header line `row <the drawing's column headers>`, then one line per row.
The comment line gives the sheet, the title, the table's box (x y w h, 0 to 1 from the top left) and
`schedule_id=` (`none` for a table read from the text).

--data writes [headers, row, row, ...], the list form schedule_to_xlsx.py reads, so two columns with one
header stay two. --payload writes the ingest payload: only for a table read from the text, since an
ingested table is already in AgentCM (its workbook takes --schedule-id instead). Row keys come from
schedule_to_xlsx.py's own rule, so the workbook's _row_key and the payload's entityIdentifier agree.
sourceMethod and rowEntityType take the values AgentCM's schedule types allow.

Usage:
    agentcm_schedule.py .construction/schedules/A-601-1.tsv --type door \\
        --data .construction/skills/schedule-extractor/A-601-1.json \\
        [--header-row 0.100] [--header-rows 1] [--row-key-column MARK] \\
        [--payload .construction/skills/schedule-extractor/outbox/schedules-ingest-A-601-<ts>.json \\
         --sheet-id <id from index/sheet_index.yaml> --row-entity-type door --source-method hybrid --confidence 0.9]
"""
import argparse
import json
import re
import sys
from pathlib import Path

from schedule_to_xlsx import _resolve_row_key_index, schedule_kind
from shared import safe_output_path

ROW_ENTITY_TYPES = ("room", "door", "window", "fixture", "equipment")  # AgentCM's RowEntityType
SOURCE_METHODS = ("pdfplumber", "vision", "hybrid", "manual")         # AgentCM's ScheduleSourceMethod
COMMENT = re.compile(r"^#\s*(\S+)\s+(.+?):\s.*?\bat\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\b")
SCHEDULE_ID = re.compile(r"schedule_id=(\S+)\s*$")


class TableError(ValueError):
    pass


def read_table(path, header_row=None, header_rows=1):
    """{sheet, title, box, schedule_id, headers, rows, notes} from one of AgentCM's table files."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    if len(lines) < 2 or not lines[0].startswith("#"):
        raise TableError(f"{path}: not one of AgentCM's table files (a comment line, then a header line)")
    m, sid = COMMENT.match(lines[0]), SCHEDULE_ID.search(lines[0])
    if not m or not sid:
        raise TableError(f"{path}: the comment line gives no sheet, title, box or schedule_id=")
    table = {"sheet": m.group(1), "title": m.group(2).strip(), "box": [float(v) for v in m.groups()[2:6]],
             "schedule_id": None if sid.group(1) == "none" else sid.group(1), "notes": []}
    head = lines[1].split("\t")
    body = [l.split("\t") for l in lines[2:] if l.strip()]
    if head[0] == "row":  # ingested: the drawing's column headers, each line a row after its number
        table["headers"] = head[1:]
        table["rows"] = [pad(r[1:], len(head) - 1) for r in body]
        return table
    if head[0] != "y":
        raise TableError(f"{path}: header line starts {head[0]!r}, neither 'y' (read from the text) nor 'row' (ingested)")
    width = len(head) - 1
    cells = [(r[0], pad(r[1:], width)) for r in body]
    if header_row is None:  # the first line with more than one cell: a title line holds one
        at = next((i for i, (_, c) in enumerate(cells) if sum(1 for v in c if v.strip()) > 1), None)
        if at is None:
            raise TableError(f"{path}: no line with more than one cell to take as the header row; give --header-row")
    else:
        at = next((i for i, (y, _) in enumerate(cells) if abs(float(y) - float(header_row)) < 1e-6), None)
        if at is None:
            raise TableError(f"{path}: no line at y={header_row}; the lines start at {[y for y, _ in cells[:6]]}")
    heads = cells[at:at + header_rows]
    headers = [" ".join(h[1][i].strip() for h in heads if h[1][i].strip()) for i in range(width)]
    keep = [i for i, h in enumerate(headers) if h]
    data = cells[at + header_rows:]
    lost = [i for i in range(width) if i not in keep and any(c[i].strip() for _, c in data)]
    if lost:
        table["notes"].append(f"columns {[head[i + 1] for i in lost]} have cells but no header: left out, check the crop")
    table["notes"].append(f"header row y={cells[at][0]}: {' | '.join(headers[i] for i in keep)}")
    if at:
        table["notes"].append(f"above it, left out: {[' '.join(v for v in c if v.strip()) for _, c in cells[:at]]}")
    table["headers"] = [headers[i] for i in keep]
    table["rows"] = [[c[i] for i in keep] for _, c in data]
    return table


def pad(cells, width):
    return (cells + [""] * width)[:width]


def column_keys(headers):
    """The payload's column keys: upper case, each run of other characters one underscore, unique."""
    keys, seen = [], {}
    for h in headers:
        k = re.sub(r"[^A-Z0-9]+", "_", h.upper()).strip("_") or "COLUMN"
        seen[k] = seen.get(k, 0) + 1
        keys.append(k if seen[k] == 1 else f"{k}_{seen[k]}")
    return keys


def payload(table, sheet_id, schedule_type, row_entity_type, source_method, confidence, row_key_column=""):
    """The schedules/ingest payload, and the lines left out for having no row key."""
    schedule_type = schedule_kind(schedule_type)
    if table["schedule_id"]:
        raise TableError(f"already ingested as {table['schedule_id']}: nothing to ingest (its workbook takes "
                         f"--schedule-id {table['schedule_id']})")
    keys = column_keys(table["headers"])
    k = _resolve_row_key_index(table["headers"], row_key_column, schedule_type)
    rows, keyless = [], []
    for r in table["rows"]:
        if not r[k].strip():
            keyless.append(" ".join(v for v in r if v.strip()))
            continue
        rows.append({"entityIdentifier": r[k].strip(), "cells": dict(zip(keys, r))})
    if not rows:
        raise TableError(f"no row has a {table['headers'][k]!r}: nothing to ingest")
    x, y, w, h = table["box"]
    return {"sheetId": sheet_id, "scheduleType": schedule_type, "title": table["title"], "rowEntityType": row_entity_type,
            "columns": [{"key": key, "header": hd} for key, hd in zip(keys, table["headers"])], "rows": rows,
            "sourceMethod": source_method, "confidence": confidence,
            "boundingRegion": {"x": x, "y": y, "width": w, "height": h}}, keyless


def main():
    for stream in (sys.stdout, sys.stderr):  # a Windows pipe is cp1252
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="AgentCM's table file to schedule_to_xlsx data and the ingest payload")
    ap.add_argument("table", help=".construction/schedules/<sheet>-<n>.tsv")
    ap.add_argument("--data", required=True, help="schedule_to_xlsx.py's data JSON to write")
    ap.add_argument("--type", required=True, help="schedule type, as schedule_to_xlsx.py --type takes it (door, window, finish, ...)")
    ap.add_argument("--header-row", help="y of the table's header row, as the file prints it (read-from-text tables)")
    ap.add_argument("--header-rows", type=int, default=1, help="header lines from --header-row, joined per column")
    ap.add_argument("--row-key-column", default="", help="the column whose cell is each row's key")
    ap.add_argument("--payload", help="the schedules/ingest payload to write (tables not yet ingested)")
    ap.add_argument("--sheet-id", help="the sheet's id from .construction/index/sheet_index.yaml")
    ap.add_argument("--row-entity-type", choices=ROW_ENTITY_TYPES)
    ap.add_argument("--source-method", choices=SOURCE_METHODS)
    ap.add_argument("--confidence", type=float)
    a = ap.parse_args()
    if a.payload and not (a.sheet_id and a.row_entity_type and a.source_method and a.confidence is not None):
        ap.error("--payload needs --sheet-id, --row-entity-type, --source-method and --confidence")
    stype = schedule_kind(a.type)  # the exporter's own rule: door_schedule, as Step 5 names it, is door
    try:
        table = read_table(a.table, a.header_row, a.header_rows)
        body, keyless = payload(table, a.sheet_id, stype, a.row_entity_type, a.source_method,
                                a.confidence, a.row_key_column) if a.payload else (None, [])
    except TableError as e:
        print(f"ERROR: {e}")
        sys.exit(2)
    out = safe_output_path(a.data)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps([table["headers"]] + table["rows"], indent=1), encoding="utf-8")
    sid = table["schedule_id"] or "none"
    print(f"OK: {out} ({len(table['rows'])} rows, {len(table['headers'])} columns; {table['sheet']} {table['title']}; schedule_id={sid})")
    for note in table["notes"]:
        print(f"  {note}")
    if body:
        p = safe_output_path(a.payload)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(body, indent=1), encoding="utf-8")
        print(f"OK: {p} ({len(body['rows'])} rows to ingest)")
        if keyless:
            print(f"  lines without a {table['headers'][_resolve_row_key_index(table['headers'], a.row_key_column, stype)]!r}, "
                  f"left out (a wrapped cell or a note? check the crop): {keyless}")


if __name__ == "__main__":
    main()
