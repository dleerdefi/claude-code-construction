#!/usr/bin/env python3
"""Query the skills' findings (.construction/skills/<skill>/findings/). Filter by skill, type, sheet, or date."""

import argparse
import glob
import json
import os


def finding_files(findings_dir=None, skill=None):
    if findings_dir is not None:
        return glob.glob(os.path.join(findings_dir, "*.json"))
    base = os.path.join(os.getcwd(), ".construction", "skills")
    return glob.glob(os.path.join(base, skill or "*", "findings", "*.json"))


def query_findings(findings_dir=None, finding_type=None, sheet=None, since=None, limit=20, skill=None):
    entries = []
    for path in finding_files(findings_dir, skill):
        with open(path, encoding="utf-8") as f:
            entries.append(json.load(f))
    entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)  # newest first, across skills

    results = []
    for entry in entries:
        if finding_type and entry.get("type") != finding_type:
            continue
        if sheet and sheet not in entry.get("source_sheets", []):
            continue
        if since:
            entry_date = entry.get("timestamp", "")[:10]
            if entry_date < since:
                continue

        results.append(entry)
        if len(results) >= limit:
            break

    print(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the skills' findings")
    parser.add_argument("--skill", help="Only this skill's findings")
    parser.add_argument("--type", help="Filter by finding type")
    parser.add_argument("--sheet", help="Filter by source sheet")
    parser.add_argument("--since", help="Filter by date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--dir", help="Findings directory override")
    args = parser.parse_args()
    query_findings(args.dir, args.type, args.sheet, args.since, args.limit, args.skill)
