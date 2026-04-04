"""Bid tabulator eval runner.

Two modes:
  1. Pre-extracted: Claude Code reads PDFs and writes per-bidder JSON to
     run_dir/bids/. This runner loads those JSONs, generates Excel, and
     scores against ground truth.
  2. Fallback: pdfplumber text extraction + basic regex parsing (for
     automated CI runs without Claude Code in the loop).

Extraction philosophy: as-submitted, NO normalization.
"""

import json
import re
import sys
from pathlib import Path

from evals.runners.helpers import (
    PROJECT_ROOT,
    write_graph_entry,
    write_eval_result,
    get_project_dir,
)


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _fuzzy_match_company(extracted_name, gt_name):
    """Check if two company names refer to the same firm."""
    a = extracted_name.lower().strip()
    b = gt_name.lower().strip()
    if a in b or b in a:
        return True
    noise = {"llc", "inc", "co", "corp", "ltd", "the"}
    a_words = set(re.findall(r"[a-z]+", a)) - noise
    b_words = set(re.findall(r"[a-z]+", b)) - noise
    return len(a_words & b_words) >= 2


def _score_against_ground_truth(bids_data, gt_path):
    """Score extracted bids against ground truth YAML."""
    import yaml

    with open(gt_path, encoding="utf-8") as f:
        gt = yaml.safe_load(f)

    scores = {}
    gt_summary = gt.get("bid_summary", [])
    gt_bids = gt.get("bids", {})

    # 1. Bidder detection
    scores["bidder_detection"] = round(
        min(len(bids_data), len(gt_summary)) / max(len(gt_summary), 1), 3,
    )

    gt_by_company = {}
    for key, bid in gt_bids.items():
        gt_by_company[bid.get("company", "")] = bid

    # 2. Amount accuracy (penalizes missing totals)
    amount_ok = 0
    for bd in bids_data:
        name = bd.get("company_name", "")
        extracted_total = bd.get("base_bid_amount")
        for gt_name, gt_bid in gt_by_company.items():
            if _fuzzy_match_company(name, gt_name):
                gt_total = gt_bid.get("base_bid_total")
                if gt_total and extracted_total and abs(extracted_total - gt_total) <= 1.0:
                    amount_ok += 1
                elif gt_total:
                    diff = (
                        f"${abs(extracted_total - gt_total):.2f}"
                        if extracted_total
                        else "MISSING"
                    )
                    print(
                        f"    Amount: {name} "
                        f"got={'$'+f'{extracted_total:.2f}' if extracted_total else 'None'} "
                        f"want=${gt_total:.2f} diff={diff}",
                    )
                break
    scores["amount_accuracy"] = round(amount_ok / max(len(gt_bids), 1), 3)

    # 3. Line item completeness
    item_score = 0.0
    item_n = 0
    for bd in bids_data:
        name = bd.get("company_name", "")
        ext_count = len(bd.get("line_items", []))
        for gt_name, gt_bid in gt_by_company.items():
            if _fuzzy_match_company(name, gt_name):
                gt_count = len(gt_bid.get("line_items", []))
                item_n += 1
                item_score += min(ext_count, gt_count) / max(gt_count, 1)
                if ext_count != gt_count:
                    print(f"    Items: {name} got={ext_count} want={gt_count}")
                break
    scores["line_item_completeness"] = round(item_score / max(item_n, 1), 3)

    # 4. Exclusions & qualifications
    exc_score = 0.0
    exc_n = 0
    for bd in bids_data:
        name = bd.get("company_name", "")
        ext_count = (
            len(bd.get("scope_exclusions", []))
            + len(bd.get("qualifications", []))
        )
        for gt_name, gt_bid in gt_by_company.items():
            if _fuzzy_match_company(name, gt_name):
                gt_exc = gt_bid.get("exclusions", [])
                gt_qual = gt_bid.get(
                    "clarifications", gt_bid.get("qualifications", []),
                )
                gt_count = len(gt_exc) + len(gt_qual)
                exc_n += 1
                if gt_count == 0:
                    exc_score += 1.0 if ext_count == 0 else 0.5
                else:
                    exc_score += min(
                        min(ext_count, gt_count) / gt_count, 1.0,
                    )
                if ext_count != gt_count:
                    print(f"    Exc+qual: {name} got={ext_count} want={gt_count}")
                break
    scores["exclusions_qualifications"] = round(
        exc_score / max(exc_n, 1), 3,
    )

    return scores


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_bid_tabulator(case, run_dir):
    """Load pre-extracted bid JSONs, generate Excel, score against GT.

    Expects per-bidder JSON files in run_dir/bids/ (written by Claude Code).
    Falls back to discovering JSONs from the run_dir itself if bids/ is empty.
    """
    evals_dir = PROJECT_ROOT / "evals"

    print(f"\n{'='*60}")
    print(f"SKILL: bid-tabulator")
    print(f"Output: {run_dir}")
    print(f"{'='*60}")

    # Load pre-extracted bid JSONs
    bids_dir = run_dir / "bids"
    if not bids_dir.exists():
        print("  ERROR: No bids/ directory found. Run Claude Code extraction first.")
        return None

    json_files = sorted(bids_dir.glob("*.json"))
    if not json_files:
        print("  ERROR: No bid JSON files found in bids/. Run Claude Code extraction first.")
        return None

    print(f"\n[Step 1] Loading {len(json_files)} pre-extracted bid JSONs...")
    bids_data = []
    for jf in json_files:
        with open(jf) as f:
            bid = json.load(f)
        bids_data.append(bid)
        name = bid.get("company_name", jf.stem)
        total = bid.get("base_bid_amount")
        items = len(bid.get("line_items", []))
        exc = len(bid.get("scope_exclusions", []))
        qual = len(bid.get("qualifications", []))
        total_str = f"${total:,.2f}" if total else "N/A"
        print(f"  {name}: {total_str} | {items} items | {exc} exc | {qual} qual")

    # Generate comparison Excel
    print(f"\n[Step 2] Generating comparison Excel...")
    sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "skills" / "bid-tabulator" / "scripts"))
    from bid_comparison_to_xlsx import bid_comparison_to_xlsx

    xlsx_path = str(run_dir / "Bid_Comparison.xlsx")
    scope_matrix_path = run_dir / "scope_matrix.json"
    bid_comparison_to_xlsx(
        str(bids_dir),
        output=xlsx_path,
        scope="Flooring, Tiling & Concrete Finishing",
        project="Holabird Elementary / Middle School",
        scope_matrix=str(scope_matrix_path) if scope_matrix_path.exists() else None,
    )
    if scope_matrix_path.exists():
        print(f"  Scope matrix: {scope_matrix_path.name}")
    print(f"  Excel: {xlsx_path}")

    # Write graph entry
    print(f"\n[Step 3] Writing graph entry...")
    graph_data = {
        "bidder_count": len(bids_data),
        "bidders": [
            {
                "company": b.get("company_name", ""),
                "base_bid": b.get("base_bid_amount"),
                "line_items": len(b.get("line_items", [])),
                "exclusions": len(b.get("scope_exclusions", [])),
            }
            for b in bids_data
        ],
    }
    graph_path = write_graph_entry(
        run_dir,
        "bid_tabulation_complete",
        f"Bid tabulation — Flooring scope ({len(bids_data)} bids)",
        graph_data,
        project_dir=get_project_dir(case),
    )
    print(f"  Graph: {graph_path.name}")

    # Score against ground truth
    print(f"\n[Step 4] Scoring against ground truth...")
    scores = {}
    gt_rel = case.get("ground_truth")
    if gt_rel:
        gt_path = PROJECT_ROOT / "evals" / "cases" / case["skill"] / gt_rel
        if gt_path.exists():
            scores = _score_against_ground_truth(bids_data, gt_path)

            try:
                import openpyxl
                wb = openpyxl.load_workbook(xlsx_path)
                tab_names = [ws.title for ws in wb.worksheets]
                required = [
                    "Comparison Summary",
                    "Exclusions & Qualifications",
                    "Scope Gaps",
                ]
                scores["format"] = round(
                    sum(1 for r in required if r in tab_names) / len(required),
                    3,
                )
                print(f"  Excel tabs: {tab_names}")
                wb.close()
            except Exception as e:
                scores["format"] = 0.0
                print(f"  Excel validation error: {e}")

            scores["graph"] = 1.0 if graph_path.exists() else 0.0

            print(f"\n  --- SCORES ---")
            for metric, value in scores.items():
                weight = case.get("scoring", {}).get(metric, {}).get("weight", 0)
                print(f"  {metric}: {value:.3f} (weight={weight})")

            weighted = sum(
                scores.get(m, 0)
                * case.get("scoring", {}).get(m, {}).get("weight", 0)
                for m in scores
            )
            print(f"\n  WEIGHTED TOTAL: {weighted:.3f}")
        else:
            print(f"  Ground truth not found: {gt_path}")

    artifacts = {
        "xlsx": xlsx_path,
        "bids_dir": str(bids_dir),
        "graph_entry": str(graph_path),
    }
    result_path = write_eval_result(
        case, run_dir, scores, artifacts,
        f"{len(bids_data)} bids processed",
    )
    print(f"\n  Result: {result_path}")
    return json.loads(result_path.read_text())
