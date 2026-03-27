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

def run_sheet_index_builder(case, run_dir):
    """Execute sheet-index-builder: rasterize title blocks + text extraction."""
    import pdfplumber
    import yaml

    evals_dir = PROJECT_ROOT / "evals"
    input_files = case["inputs"]["files"]

    print(f"\n{'='*60}")
    print(f"SKILL: sheet-index-builder")
    print(f"Input: {len(input_files)} sheets")
    print(f"Output: {run_dir}")
    print(f"{'='*60}")

    DISCIPLINE_MAP = {
        "A": "Architectural", "S": "Structural", "M": "Mechanical",
        "E": "Electrical", "P": "Plumbing", "C": "Civil",
        "L": "Landscape", "K": "Food Service", "TS": "Title Sheet",
    }

    sheets = []
    tb_dir = run_dir / "title_blocks"
    tb_dir.mkdir(exist_ok=True)

    for pdf_rel in input_files:
        pdf_path = evals_dir / pdf_rel
        if not pdf_path.exists():
            print(f"  MISSING: {pdf_path}")
            continue

        fname = pdf_path.stem  # e.g., "A-1.1 - PARTIAL FIRST FLOOR PLAN AREA A"

        print(f"\n  Processing: {fname}")

        # Extract sheet number and title from filename
        # Pattern: "A-1.1 - PARTIAL FIRST FLOOR PLAN AREA A" or "S-1.1H - FOUNDATION..."
        match = re.match(r"^([A-Z]{1,2}-[\d.]+[A-Z]?)\s*[-–]\s*(.+)$", fname)
        if match:
            sheet_num = match.group(1)
            sheet_title = match.group(2).strip()
        else:
            sheet_num = fname.split(" ")[0] if " " in fname else fname
            sheet_title = fname

        # Determine discipline from prefix
        prefix = sheet_num.split("-")[0] if "-" in sheet_num else sheet_num[0]
        discipline = DISCIPLINE_MAP.get(prefix, "Unknown")

        # Rasterize title block region
        try:
            tb_path = rasterize_title_block(pdf_path, 0, tb_dir, prefix="tb")
            print(f"    Title block: {tb_path.name}")
        except Exception as e:
            print(f"    Title block rasterize failed: {e}")
            tb_path = None

        # Try pdfplumber text extraction for scale/revision
        scale = "varies"
        revision = ""
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                page = pdf.pages[0]
                # Extract text from bottom-right region (title block area)
                tb_bbox = (page.width * 0.65, page.height * 0.75, page.width, page.height)
                cropped = page.within_bbox(tb_bbox)
                text = cropped.extract_text() or ""
                # Look for scale patterns
                scale_match = re.search(r'(?:SCALE|Scale)[:=]?\s*([\d/]+["\']?\s*=\s*[\d\'-]+|NTS|AS NOTED)', text)
                if scale_match:
                    scale = scale_match.group(1).strip()
                # Look for revision
                rev_match = re.search(r'(?:REV|Revision|Rev)\.?\s*(\d+)', text)
                if rev_match:
                    revision = rev_match.group(1)
        except Exception as e:
            print(f"    Text extraction failed: {e}")

        sheets.append({
            "number": sheet_num,
            "title": sheet_title,
            "discipline": discipline,
            "scale": scale,
            "revision": revision,
            "file_path": pdf_rel,
        })
        print(f"    {sheet_num} | {discipline} | {sheet_title[:50]}")

    # Write sheet index YAML
    index_path = run_dir / "sheet_index.yaml"
    with open(index_path, "w") as f:
        yaml.dump({"sheets": sheets}, f, default_flow_style=False, sort_keys=False)

    # Write graph entry
    graph_path = write_graph_entry(run_dir, "sheet_index_built", "Sheet index created",
                                   {"sheet_count": len(sheets), "disciplines": list(set(s["discipline"] for s in sheets))},
                                   project_dir=get_project_dir(case))

    print(f"\n  Index: {index_path.name} ({len(sheets)} sheets)")
    print(f"  Graph: {graph_path.name}")
    print(f"  Title blocks: {len(list(tb_dir.iterdir()))} PNGs")

    # Auto-score all metrics
    scores = {}
    gt_rel = case.get("ground_truth")
    if gt_rel:
        gt_path = PROJECT_ROOT / "evals" / "cases" / case["skill"] / gt_rel
        if gt_path.exists():
            with open(gt_path) as f:
                gt = yaml.safe_load(f)
            gt_sheets = gt.get("sheets", [])
            gt_nums = {s["number"] for s in gt_sheets}
            ext_nums = {s["number"] for s in sheets}
            gt_by_num = {s["number"]: s for s in gt_sheets}
            ext_by_num = {s["number"]: s for s in sheets}

            # Sheet number exact match
            num_match = len(gt_nums & ext_nums) / max(len(gt_nums), 1)
            scores["sheet_number"] = round(num_match, 3)
            print(f"\n  Sheet number match: {len(gt_nums & ext_nums)}/{len(gt_nums)} = {num_match:.1%}")

            # Sheet title fuzzy match
            title_matches = 0
            title_total = 0
            for num in gt_nums & ext_nums:
                gt_title = gt_by_num[num].get("title", "").upper()
                ext_title = ext_by_num[num].get("title", "").upper()
                title_total += 1
                # Check if >80% of words match
                gt_words = set(gt_title.split())
                ext_words = set(ext_title.split())
                if gt_words and len(gt_words & ext_words) / len(gt_words) >= 0.8:
                    title_matches += 1
            scores["sheet_title"] = round(title_matches / max(title_total, 1), 3)
            print(f"  Sheet title match: {title_matches}/{title_total}")

            # Discipline accuracy
            disc_matches = 0
            disc_total = 0
            for num in gt_nums & ext_nums:
                gt_disc = gt_by_num[num].get("discipline", "").upper()
                ext_disc = ext_by_num[num].get("discipline", "").upper()
                disc_total += 1
                if gt_disc == ext_disc:
                    disc_matches += 1
            scores["discipline"] = round(disc_matches / max(disc_total, 1), 3)
            print(f"  Discipline match: {disc_matches}/{disc_total}")

            # Scale (check if any scale was extracted — not "varies")
            scales_found = sum(1 for s in sheets if s.get("scale") and s["scale"] != "varies")
            scores["scale"] = round(scales_found / max(len(sheets), 1), 3)
            print(f"  Scales extracted: {scales_found}/{len(sheets)}")

            # Completeness
            expected = case.get("expected_outputs", {}).get("expected_sheet_count", len(sheets))
            scores["completeness"] = round(len(sheets) / max(expected, 1), 3)

    artifacts = {"sheet_index": str(index_path), "graph_entry": str(graph_path), "title_blocks_dir": str(tb_dir)}
    result_path = write_eval_result(case, run_dir, scores, artifacts, f"{len(sheets)} sheets indexed")
    print(f"  Result: {result_path}")
    return json.loads(result_path.read_text())


# ─── TIER 2: RASTERIZE + VISION SKILLS ──────────────────────────────────────
