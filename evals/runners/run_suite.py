#!/usr/bin/env python3
"""Run all eval cases for a skill or for all skills.

Usage:
  python evals/runners/run_suite.py --skill schedule-extractor
  python evals/runners/run_suite.py --all
  python evals/runners/run_suite.py --list
"""

import argparse
import glob
import json
import os
import sys

# Add parent to path
sys.path.insert(0, os.path.dirname(__file__))
from run_eval import run_eval

EVALS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)))
CASES_DIR = os.path.join(EVALS_DIR, "cases")

SKILL_PRIORITIES = {
    "project-onboarding": ("P0", 3.0),
    "sheet-index-builder": ("P0", 3.0),
    "drawing-reader": ("P0", 3.0),
    "drawing-conventions": ("P0", 3.0),
    "spec-parser": ("P1", 2.0),
    "schedule-extractor": ("P1", 2.0),
    "code-compliance-checker": ("P1", 2.0),
    "submittal-log-generator": ("P1", 2.0),
    "cross-reference-navigator": ("P2", 1.5),
}

def list_skills():
    print("\nAvailable skills with eval cases:\n")
    print(f"{'Skill':<30} {'Priority':<8} {'Weight':<8} {'Cases':<6}")
    print("-" * 55)
    for skill_dir in sorted(os.listdir(CASES_DIR)):
        cases = glob.glob(os.path.join(CASES_DIR, skill_dir, "case_*.json"))
        if not cases:
            continue
        priority, weight = SKILL_PRIORITIES.get(skill_dir, ("?", 1.0))
        print(f"{skill_dir:<30} {priority:<8} {weight:<8.1f} {len(cases):<6}")

def run_skill(skill_name):
    skill_cases_dir = os.path.join(CASES_DIR, skill_name)
    if not os.path.isdir(skill_cases_dir):
        print(f"ERROR: No eval cases found for skill '{skill_name}'")
        print(f"Expected directory: {skill_cases_dir}")
        return []

    cases = sorted(glob.glob(os.path.join(skill_cases_dir, "case_*.json")))
    if not cases:
        print(f"No case files found in {skill_cases_dir}")
        return []

    print(f"\n{'#'*60}")
    print(f"SUITE: {skill_name} ({len(cases)} cases)")
    print(f"{'#'*60}")

    results = []
    for case_path in cases:
        result = run_eval(case_path)
        results.append(result)

    # Summary
    docs_ready = sum(1 for r in results if r.get("docs_present"))
    missing = sum(1 for r in results if r.get("status") == "missing_docs")
    print(f"\n--- SUITE SUMMARY: {skill_name} ---")
    print(f"Total cases: {len(results)}")
    print(f"Docs ready: {docs_ready}")
    print(f"Missing docs: {missing}")

    return results

def run_all():
    all_results = {}
    for skill_dir in sorted(os.listdir(CASES_DIR)):
        cases = glob.glob(os.path.join(CASES_DIR, skill_dir, "case_*.json"))
        if cases:
            all_results[skill_dir] = run_skill(skill_dir)

    # Overall summary
    total = sum(len(v) for v in all_results.values())
    ready = sum(1 for v in all_results.values()
                for r in v if r.get("docs_present"))
    print(f"\n{'='*60}")
    print(f"OVERALL: {total} cases across {len(all_results)} skills")
    print(f"Docs ready: {ready} / {total}")
    print(f"{'='*60}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run eval suites")
    parser.add_argument("--skill", help="Run all cases for a specific skill")
    parser.add_argument("--all", action="store_true", help="Run all cases for all skills")
    parser.add_argument("--list", action="store_true", help="List available skills and case counts")
    args = parser.parse_args()

    if args.list:
        list_skills()
    elif args.skill:
        run_skill(args.skill)
    elif args.all:
        run_all()
    else:
        parser.print_help()
