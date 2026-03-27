"""Auto-extracted skill runner module."""

import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from evals.runners.helpers import (
    PROJECT_ROOT, normalize_dimension, write_graph_entry, write_eval_result, get_project_dir,
    rasterize_pdf, rasterize_title_block,
)

def run_schedule_extractor(case, run_dir):
    """Execute the schedule-extractor skill pipeline.

    Steps:
    1. Open PDF with pdfplumber
    2. Extract all tables (auto-detect via line intersections)
    3. Identify the schedule table(s) by size and header patterns
    4. Parse into structured rows
    5. Write CSV and Excel output
    6. Write graph entry
    7. Auto-score against ground truth if available
    """
    import pdfplumber
    import openpyxl

    evals_dir = PROJECT_ROOT / "evals"
    pdf_rel = case["inputs"]["files"][0]
    pdf_path = evals_dir / pdf_rel

    print(f"\n{'='*60}")
    print(f"SKILL: schedule-extractor")
    print(f"Input: {pdf_path.name}")
    print(f"Output: {run_dir}")
    print(f"{'='*60}")

    # Step 1: Open PDF
    print("\n[Step 1] Opening PDF...")
    with pdfplumber.open(str(pdf_path)) as pdf:
        page_idx = case["inputs"].get("page", 1) - 1
        page = pdf.pages[page_idx]
        print(f"  Page size: {page.width:.0f} x {page.height:.0f} pts")

        # Step 2: Extract tables
        print("\n[Step 2] Extracting tables via pdfplumber...")
        tables = page.extract_tables()
        print(f"  Tables found: {len(tables)}")

        # Step 3: Identify schedule tables — pick tables with most columns AND rows
        schedule_tables = []
        for i, table in enumerate(tables):
            cols = max(len(r) for r in table) if table else 0
            if len(table) >= 10 and cols >= 3:
                print(f"  Table {i}: {len(table)} rows x {cols} cols — candidate schedule")
                schedule_tables.append((i, table))
            else:
                print(f"  Table {i}: {len(table)} rows x {cols} cols — skipped")

        if not schedule_tables:
            print("  WARNING: No schedule tables found by pdfplumber")

        # Step 4: Parse schedule data from candidates
        print(f"\n[Step 3] Parsing {len(schedule_tables)} schedule table(s)...")

        # Valid ID patterns for first column (door numbers, room numbers, equipment tags)
        ID_PREFIXES = (
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            "C1", "C2", "ST", "X1", "X2", "X3", "RA", "E1", "V1",
        )
        # Header keywords to detect where headers end and data begins
        HEADER_KEYWORDS = [
            "DOOR", "RM", "ROOM", "NAME", "WIDTH", "HEIGHT", "FLOOR",
            "BASE", "WALL", "CLG", "CEILING", "MARK", "TYPE", "SIZE",
            "NOMINAL", "FRAME", "SCHEDULE", "SECTIONS", "HARDWARE",
            "LABEL", "FIRE", "RATING", "THK", "MAT'L", "MATL",
            "COLOR", "SCHEME", "REMARKS",
        ]

        all_rows = []
        headers = None

        for table_idx, table in schedule_tables:
            # Strategy: scan rows top-down. Header rows contain HEADER_KEYWORDS.
            # Data rows start when col 0 matches an ID pattern AND the row is not a header.
            data_start = None
            for j, row in enumerate(table):
                if not row or not row[0]:
                    continue
                val = str(row[0]).strip().replace("\n", " ")
                row_text = " ".join(str(c) for c in row if c).upper()

                # Skip if this row contains header keywords
                if any(kw in row_text for kw in HEADER_KEYWORDS):
                    continue

                # Skip if first cell is empty or very short (sub-header artifact)
                if len(val) < 2:
                    continue

                # Check if first cell looks like a valid ID
                is_id = val[0].isdigit() or any(val.startswith(p) for p in ID_PREFIXES)
                if is_id:
                    data_start = j
                    break

            if data_start is None:
                print(f"  Table {table_idx}: No data rows found (no valid IDs in col 0)")
                continue

            # Extract data rows
            for row in table[data_start:]:
                if row and row[0] and row[0].strip():
                    cleaned = [normalize_dimension(str(c).replace("\n", " ")) if c else "" for c in row]
                    all_rows.append(cleaned)

            print(f"  Table {table_idx}: {len(table) - data_start} data rows extracted (start at row {data_start})")

        print(f"\n  Total rows extracted (Method A): {len(all_rows)}")

        # ── Quality Gate ──────────────────────────────────────────
        # Check if pdfplumber extraction succeeded
        method_a_ok = True
        if len(all_rows) < 10:
            print(f"\n  WARNING: QUALITY GATE FAILED: Only {len(all_rows)} rows extracted (need >=10)")
            method_a_ok = False
        elif all_rows:
            # Check column consistency
            col_counts = [len(r) for r in all_rows]
            mode_cols = max(set(col_counts), key=col_counts.count)
            consistency = col_counts.count(mode_cols) / len(col_counts)
            if consistency < 0.8:
                print(f"\n  WARNING: QUALITY GATE FAILED: Column consistency {consistency:.0%} (need >=80%)")
                method_a_ok = False
            # Check non-empty cells
            total_cells = sum(len(r) for r in all_rows)
            empty_cells = sum(1 for r in all_rows for c in r if not c.strip())
            nonempty_pct = 1 - (empty_cells / max(total_cells, 1))
            if nonempty_pct < 0.3:
                print(f"\n  WARNING: QUALITY GATE FAILED: Only {nonempty_pct:.0%} cells non-empty (need >=30%)")
                method_a_ok = False

        if method_a_ok:
            print(f"  OK: Quality gate passed: {len(all_rows)} rows, columns consistent, cells populated")
        else:
            # ── Method B: Rasterize for vision fallback ───────────
            print(f"\n[Fallback] Method A insufficient. Rasterizing for vision extraction...")
            import fitz
            doc = fitz.open(str(pdf_path))
            pg = doc[page_idx]

            # Full sheet at 150 DPI
            mat = fitz.Matrix(150 / 72, 150 / 72)
            pix = pg.get_pixmap(matrix=mat)
            overview_path = run_dir / "sheet_150dpi.png"
            pix.save(str(overview_path))
            print(f"  Rasterized overview: {overview_path.name} ({pix.width}x{pix.height})")

            # High-res at 300 DPI for text clarity
            mat2 = fitz.Matrix(300 / 72, 300 / 72)
            pix2 = pg.get_pixmap(matrix=mat2)
            hires_path = run_dir / "sheet_300dpi.png"
            pix2.save(str(hires_path))
            print(f"  Rasterized hi-res: {hires_path.name} ({pix2.width}x{pix2.height})")

            doc.close()

            # Try pdfplumber text extraction as secondary fallback
            print(f"\n  Attempting text-based extraction...")
            with pdfplumber.open(str(pdf_path)) as pdf2:
                pg2 = pdf2.pages[page_idx]
                text = pg2.extract_text() or ""
                lines = [l.strip() for l in text.split("\n") if l.strip()]

                # Parse text lines that look like schedule rows
                # A schedule row typically starts with a room/door number
                text_rows = []
                for line in lines:
                    parts = line.split()
                    if parts and (parts[0][0].isdigit() or any(parts[0].startswith(p) for p in ["C1", "C2", "ST", "V1", "RA", "E1"])):
                        # This line likely starts a schedule row
                        text_rows.append(parts)

                if len(text_rows) > len(all_rows):
                    print(f"  Text extraction found {len(text_rows)} rows (better than table: {len(all_rows)})")
                    # Use text rows — pad to consistent column count
                    if text_rows:
                        max_text_cols = max(len(r) for r in text_rows)
                        all_rows = [r + [""] * (max_text_cols - len(r)) for r in text_rows]
                else:
                    print(f"  Text extraction found {len(text_rows)} rows (not better)")

            print(f"\n  PNG files saved for Claude Code vision extraction.")
            print(f"  To extract via vision, read the PNG and ask Claude to parse the schedule.")
            print(f"  Files: {overview_path.name}, {hires_path.name}")

        # Determine column count and create headers
        if all_rows:
            max_cols = max(len(r) for r in all_rows)
            # Pad short rows
            all_rows = [r + [""] * (max_cols - len(r)) for r in all_rows]
        else:
            max_cols = 0

    # Step 5: Write outputs
    print(f"\n[Step 4] Writing outputs...")

    # Write CSV
    csv_path = run_dir / "extracted_data.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Write header based on column count
        if max_cols >= 15:
            writer.writerow(["DOOR_NO", "ROOM", "WIDTH", "HEIGHT", "THK", "TYPE",
                             "DOOR_MATL", "FRAME_MATL", "FRAME_TYPE", "JAMB", "HEAD",
                             "SILL", "DOOR_LABEL", "FIRE_RATING", "HARDWARE_SET"])
        elif max_cols >= 10:
            writer.writerow(["RM_NO", "NAME", "COLOR_SCHEME", "FLOOR", "BASE",
                             "WALL_A", "WALL_B", "WALL_C", "WALL_D", "CLG_MATL", "REMARKS"][:max_cols])
        else:
            writer.writerow([f"COL_{i}" for i in range(max_cols)])
        for row in all_rows:
            writer.writerow(row[:max_cols])
    print(f"  CSV: {csv_path.name} ({len(all_rows)} rows)")

    # Write Excel
    xlsx_path = run_dir / "output.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Schedule"

    # Headers
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row_idx, row in enumerate(reader, 1):
            for col_idx, val in enumerate(row, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                if row_idx == 1:
                    cell.font = openpyxl.styles.Font(bold=True)

    # Auto-size columns
    for col in ws.columns:
        max_len = max(len(str(c.value or "")) for c in col)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 30)

    wb.save(str(xlsx_path))
    print(f"  Excel: {xlsx_path.name}")

    # Step 6: Write graph entry
    print(f"\n[Step 5] Writing graph entry...")
    import yaml

    graph_path = write_graph_entry(
        run_dir,
        finding_type="schedule_extracted",
        title=f"Schedule extracted from {pdf_path.name}",
        data={
            "schedule_type": "door" if "door" in case["name"].lower() else "finish",
            "rows_extracted": len(all_rows),
            "columns": max_cols,
            "source_pdf": pdf_path.name,
        },
        source_sheets=[pdf_path.stem.split(" - ")[0]],
        project_dir=get_project_dir(case),
    )
    print(f"  Graph entry: {graph_path.name}")

    # Step 7: Auto-score against ground truth
    print(f"\n[Step 6] Auto-scoring...")
    gt_rel = case.get("ground_truth")
    scores = {}

    if gt_rel:
        skill = case["skill"]
        gt_path = PROJECT_ROOT / "evals" / "cases" / skill / gt_rel
        if gt_path.exists():
            # Load ground truth
            gt_rows = []
            with open(gt_path, encoding="utf-8") as f:
                reader = csv.reader(f)
                gt_header = next(reader)
                gt_rows = list(reader)

            # Row count accuracy
            row_accuracy = max(0, 1.0 - abs(len(all_rows) - len(gt_rows)) / max(len(gt_rows), 1))
            scores["completeness"] = round(row_accuracy, 3)
            print(f"  Completeness: {len(all_rows)}/{len(gt_rows)} rows = {row_accuracy:.3f}")

            # Cell accuracy (compare first column — primary key)
            extracted_keys = {r[0].strip().upper() for r in all_rows if r and r[0].strip()}
            gt_keys = {r[0].strip().upper() for r in gt_rows if r and r[0].strip()}
            key_overlap = len(extracted_keys & gt_keys)
            key_accuracy = key_overlap / max(len(gt_keys), 1)
            scores["accuracy"] = round(key_accuracy, 3)
            print(f"  Accuracy (key match): {key_overlap}/{len(gt_keys)} = {key_accuracy:.3f}")

            scores["format"] = 1.0  # Excel was written successfully
            scores["graph"] = 1.0  # Graph entry was written
        else:
            print(f"  Ground truth not found: {gt_path}")
    else:
        print("  No ground truth specified for this case")

    # Write result JSON
    result = {
        "id": case["id"],
        "skill": case["skill"],
        "name": case["name"],
        "timestamp": datetime.now().isoformat(),
        "status": "auto_scored",
        "docs_present": True,
        "ground_truth_present": bool(gt_rel),
        "scores": {},
        "artifacts": {
            "csv": str(csv_path),
            "xlsx": str(xlsx_path),
            "graph_entry": str(graph_path),
        },
        "notes": f"Auto-executed by run_skill.py. {len(all_rows)} rows extracted.",
    }

    # Merge scores with case scoring weights
    for metric_name, metric_def in case.get("scoring", {}).items():
        result["scores"][metric_name] = {
            "weight": metric_def["weight"],
            "metric": metric_def["metric"],
            "value": scores.get(metric_name),
        }

    result_path = run_dir / "result.json"
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n  Result: {result_path}")

    return result


# ─── PROJECT ONBOARDING ──────────────────────────────────────────────────────

