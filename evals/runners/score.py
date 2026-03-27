#!/usr/bin/env python3
"""Score a completed eval result or summarize all results.

Usage:
  python evals/runners/score.py results/20250601_schedule-extractor-01.json
  python evals/runners/score.py --summary
  python evals/runners/score.py --summary --skill schedule-extractor
"""

import argparse
import glob
import json
import os
import sys
from collections import defaultdict

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")

SKILL_WEIGHTS = {
    "project-onboarding": 3.0,
    "sheet-index-builder": 3.0,
    "drawing-reader": 3.0,
    "bulk-sheet-extraction": 2.0,
    "spec-parser": 2.0,
    "schedule-extractor": 2.0,
    "quantity-takeoff": 2.0,
    "code-compliance-checker": 2.0,
    "submittal-log-generator": 2.0,
    "cross-reference-navigator": 1.5,
    "scale-measurement": 1.5,
    "rfi-drafter": 1.5,
    "qa-qc-auditor": 1.0,
    "coordination-report": 1.0,
}

def score_result(result_path):
    with open(result_path) as f:
        result = json.load(f)

    scores = result.get("scores", {})
    weighted_sum = 0.0
    total_weight = 0.0
    all_scored = True

    print(f"\nScoring: {result['id']}")
    print(f"Skill: {result['skill']}")
    print(f"-" * 50)

    for name, data in scores.items():
        value = data.get("value")
        weight = data.get("weight", 0)
        if value is None:
            print(f"  {name}: NOT SCORED (weight {weight})")
            all_scored = False
        else:
            weighted_sum += value * weight
            total_weight += weight
            bar = "█" * int(value * 20) + "░" * (20 - int(value * 20))
            print(f"  {name}: {value:.2f} [{bar}] (weight {weight})")

    if all_scored and total_weight > 0:
        final = weighted_sum / total_weight
        result["weighted_total"] = round(final, 4)
        result["status"] = "scored"

        interpretation = (
            "Production-ready" if final >= 0.9 else
            "Useful with human review" if final >= 0.7 else
            "Needs iteration" if final >= 0.5 else
            "Fundamental rework needed"
        )

        print(f"\n  WEIGHTED TOTAL: {final:.3f} — {interpretation}")

        # Write back
        with open(result_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"  Updated: {result_path}")
    else:
        print(f"\n  INCOMPLETE — fill in all scores and re-run")

    return result

def summarize(skill_filter=None):
    result_files = sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json")))
    if not result_files:
        print("No results found in evals/results/")
        return

    by_skill = defaultdict(list)
    for rf in result_files:
        with open(rf) as f:
            r = json.load(f)
        skill = r.get("skill", "unknown")
        if skill_filter and skill != skill_filter:
            continue
        by_skill[skill].append(r)

    print(f"\n{'='*60}")
    print(f"EVALUATION SUMMARY")
    print(f"{'='*60}\n")

    overall_weighted = 0.0
    overall_weight = 0.0

    for skill in sorted(by_skill.keys()):
        results = by_skill[skill]
        scored = [r for r in results if r.get("weighted_total") is not None]
        pending = len(results) - len(scored)

        if scored:
            avg = sum(r["weighted_total"] for r in scored) / len(scored)
            skill_w = SKILL_WEIGHTS.get(skill, 1.0)
            overall_weighted += avg * skill_w
            overall_weight += skill_w
            bar = "█" * int(avg * 20) + "░" * (20 - int(avg * 20))
            print(f"  {skill:<30} {avg:.3f} [{bar}] ({len(scored)} scored, {pending} pending)")
        else:
            print(f"  {skill:<30} --- ({pending} pending)")

    if overall_weight > 0:
        overall = overall_weighted / overall_weight
        interpretation = (
            "Production-ready" if overall >= 0.9 else
            "Useful with human review" if overall >= 0.7 else
            "Needs iteration" if overall >= 0.5 else
            "Fundamental rework needed"
        )
        print(f"\n{'─'*60}")
        print(f"  OVERALL SCORE: {overall:.3f} — {interpretation}")
        print(f"{'─'*60}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Score eval results")
    parser.add_argument("result_file", nargs="?", help="Path to result JSON file")
    parser.add_argument("--summary", action="store_true", help="Summarize all results")
    parser.add_argument("--skill", help="Filter summary by skill")
    args = parser.parse_args()

    if args.summary:
        summarize(args.skill)
    elif args.result_file:
        score_result(args.result_file)
    else:
        parser.print_help()
