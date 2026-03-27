"""Vision-dependent skill runners (Tier 2).

These skills rasterize PDFs to PNGs for Claude Code vision analysis.
"""

import csv
import json
from collections import Counter
from pathlib import Path

from evals.runners.helpers import (
    PROJECT_ROOT, write_graph_entry, write_eval_result, get_project_dir,
    rasterize_pdf,
)

def run_vision_skill(case, run_dir, skill_name, analysis_fn=None):
    """Generic runner for Tier 2 skills that need rasterization + vision.

    1. Rasterizes all input PDFs to PNGs
    2. Runs any programmatic pre-analysis (analysis_fn)
    3. Saves everything to run_dir
    4. Flags for Claude vision completion
    """
    evals_dir = PROJECT_ROOT / "evals"
    input_files = case["inputs"]["files"]

    print(f"\n{'='*60}")
    print(f"SKILL: {skill_name}")
    print(f"Input: {len(input_files)} file(s)")
    print(f"Output: {run_dir}")
    print(f"{'='*60}")

    # Step 1: Rasterize all input PDFs
    print("\n[Step 1] Rasterizing input PDFs...")
    png_files = []
    for pdf_rel in input_files:
        pdf_path = evals_dir / pdf_rel
        if not pdf_path.exists():
            print(f"  MISSING: {pdf_path}")
            continue

        sheet_name = pdf_path.stem.split(" - ")[0].replace(" ", "_")
        try:
            png_150, w, h = rasterize_pdf(pdf_path, 0, run_dir, dpi=150, prefix=sheet_name)
            print(f"  {pdf_path.name} -> {png_150.name} ({w}x{h})")
            png_files.append(png_150)

            # Also do 300 DPI for the primary sheet
            if len(png_files) == 1:
                png_300, w2, h2 = rasterize_pdf(pdf_path, 0, run_dir, dpi=300, prefix=f"{sheet_name}_hires")
                print(f"  {pdf_path.name} -> {png_300.name} ({w2}x{h2}) [hi-res]")
                png_files.append(png_300)
        except Exception as e:
            print(f"  ERROR rasterizing {pdf_path.name}: {e}")

    # Step 2: Run programmatic pre-analysis if provided
    scores = {}
    pre_analysis = {}
    if analysis_fn:
        print(f"\n[Step 2] Running programmatic analysis...")
        pre_analysis, scores = analysis_fn(case, run_dir, evals_dir)

    # Step 3: Write pre-analysis results
    if pre_analysis:
        analysis_path = run_dir / "pre_analysis.json"
        with open(analysis_path, "w") as f:
            json.dump(pre_analysis, f, indent=2)
        print(f"\n  Pre-analysis: {analysis_path.name}")

    # Step 4: Write graph entry
    graph_path = write_graph_entry(run_dir, f"{skill_name}_eval",
                                   f"{skill_name} eval",
                                   {"sheets_rasterized": len(png_files), **pre_analysis.get("summary", {})},
                                   project_dir=get_project_dir(case))

    # Step 5: Print vision prompt
    print(f"\n[Step 3] Vision analysis needed.")
    print(f"  PNG files ready for Claude Code vision:")
    for p in png_files:
        size_kb = p.stat().st_size // 1024
        print(f"    {p.name} ({size_kb}KB)")
    print(f"\n  To complete this eval, read the PNG files and perform the {skill_name} analysis.")

    artifacts = {
        "png_files": [str(p) for p in png_files],
        "graph_entry": str(graph_path),
    }
    if pre_analysis:
        artifacts["pre_analysis"] = str(run_dir / "pre_analysis.json")

    result_path = write_eval_result(case, run_dir, scores, artifacts,
                                    f"Rasterized {len(png_files)} PNGs. Vision analysis needed.")
    print(f"  Result: {result_path}")
    return json.loads(result_path.read_text())


# ─── TIER 2 PRE-ANALYSIS FUNCTIONS ──────────────────────────────────────────

def _code_compliance_analysis(case, run_dir, evals_dir):
    """Programmatic pre-analysis for code compliance: load project context + door schedule data."""
    # Load door schedule ground truth for analysis
    gt_door = PROJECT_ROOT / "evals" / "cases" / "schedule-extractor" / "expected" / "door_schedule_ground_truth.csv"
    door_data = {}
    if gt_door.exists():
        with open(gt_door, encoding="utf-8") as f:
            doors = list(csv.DictReader(f))
        door_data = {
            "total_doors": len(doors),
            "fire_rated": len([d for d in doors if d.get("FIRE_RATING", "").strip()]),
            "door_types": dict(Counter(d.get("TYPE", "") for d in doors if d.get("TYPE"))),
            "stair_doors": [d["DOOR_NO"] for d in doors if d["DOOR_NO"].startswith("ST")],
            "exterior_doors": [d["DOOR_NO"] for d in doors if d["DOOR_NO"].startswith("X")],
        }

    analysis = {
        "project": {
            "name": "Holabird Academy PK-8",
            "location": "Baltimore, Maryland",
            "occupancy": "E (Educational) / A-2 (Assembly - Gym, Dining)",
            "sprinklered": True,
            "stories": 2,
        },
        "door_schedule_summary": door_data,
        "applicable_codes": ["IBC 2015 (Maryland)", "ADA/ANSI A117.1", "NFPA 101"],
        "summary": {"doors_analyzed": len(doors) if gt_door.exists() else 0},
    }
    return analysis, {}


# ─── PRODUCTION SKILL WRAPPERS ───────────────────────────────────────────────

def run_cross_reference_navigator(case, run_dir):
    return run_vision_skill(case, run_dir, "cross-reference-navigator")

def run_code_compliance_checker(case, run_dir):
    return run_vision_skill(case, run_dir, "code-compliance-checker", _code_compliance_analysis)
