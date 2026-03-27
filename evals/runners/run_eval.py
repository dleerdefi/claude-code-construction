#!/usr/bin/env python3
"""Run a single eval case and produce a scored result.

This script orchestrates the eval by:
1. Loading the test case definition
2. Checking that required test documents exist
3. Running the skill (via Claude Code subprocess or manual invocation)
4. Collecting outputs
5. Scoring against ground truth (where automated scoring is possible)
6. Writing results to evals/results/

NOTE: Full automated execution requires Claude Code CLI integration.
For now, this script validates inputs, prepares the workspace, and
provides a scoring template that the user fills in after manual execution.
"""

import argparse
import json
import os
import sys
from datetime import datetime

def run_eval(case_path):
    with open(case_path) as f:
        case = json.load(f)

    case_id = case["id"]
    skill = case["skill"]
    print(f"\n{'='*60}")
    print(f"EVAL: {case_id}")
    print(f"Skill: {skill}")
    print(f"Name: {case['name']}")
    print(f"{'='*60}\n")

    # Validate test documents exist
    # Resolve evals/ root: go up from runners/ or cases/skill/ to evals/
    evals_dir = os.path.dirname(os.path.dirname(os.path.dirname(case_path)))
    missing = []
    for f_path in case.get("inputs", {}).get("files", []):
        full = os.path.join(evals_dir, f_path)
        if not os.path.exists(full):
            missing.append(f_path)

    if missing:
        print(f"MISSING TEST DOCUMENTS ({len(missing)}):")
        for m in missing:
            print(f"  - {m}")
        print(f"\nPlace test documents in evals/ directory and re-run.")
        print(f"See EVAL_SPEC.md for ground truth creation instructions.\n")
        return {"id": case_id, "status": "missing_docs", "missing": missing}

    print(f"All test documents present: {len(case['inputs']['files'])} files")

    # Check ground truth
    gt_path = case.get("ground_truth")
    gt_exists = False
    if gt_path:
        full_gt = os.path.join(evals_dir, "cases", skill, gt_path)
        gt_exists = os.path.exists(full_gt)
        if gt_exists:
            print(f"Ground truth found: {gt_path}")
        else:
            print(f"Ground truth NOT found: {gt_path}")
            print(f"  Create at: {full_gt}")

    # Print the prompt for manual execution
    print(f"\n--- EXECUTION ---")
    print(f"Prompt to give Claude Code:")
    print(f'  "{case["inputs"]["user_prompt"]}"')
    print(f"\nExpected behavior:")
    for i, b in enumerate(case["expected_behavior"], 1):
        print(f"  {i}. {b}")

    # Print scoring template
    print(f"\n--- SCORING TEMPLATE ---")
    scoring = case.get("scoring", {})
    result = {
        "id": case_id,
        "skill": skill,
        "name": case["name"],
        "timestamp": datetime.now().isoformat(),
        "status": "pending_manual_scoring",
        "docs_present": True,
        "ground_truth_present": gt_exists,
        "scores": {},
        "weighted_total": None,
        "notes": "",
    }

    total_weight = 0
    for metric_name, metric_def in scoring.items():
        weight = metric_def["weight"]
        total_weight += weight
        print(f"\n  {metric_name} (weight: {weight}):")
        print(f"    Metric: {metric_def['metric']}")
        print(f"    Description: {metric_def['description']}")
        print(f"    Score [0.0 - 1.0]: ___")
        result["scores"][metric_name] = {
            "weight": weight,
            "metric": metric_def["metric"],
            "value": None,  # Fill in after manual eval
        }

    # Write result template
    results_dir = os.path.join(evals_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_path = os.path.join(results_dir, f"{ts}_{case_id}.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n--- RESULT ---")
    print(f"Result template written to: {result_path}")
    print(f"After running the skill manually, edit the result file to fill in scores.")
    print(f"Then run: python evals/runners/score.py {result_path}")

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a single eval case")
    parser.add_argument("--case", required=True, help="Path to case JSON file")
    args = parser.parse_args()
    run_eval(args.case)
