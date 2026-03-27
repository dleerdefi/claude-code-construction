#!/usr/bin/env python3
"""Query agent findings from the graph directory. Filter by type, sheet, or date."""

import argparse
import json
import os
import sys
from datetime import datetime

def query_findings(findings_dir=None, finding_type=None, sheet=None, since=None, limit=20):
    if findings_dir is None:
        root = os.getcwd()
        findings_dir = os.path.join(root, ".construction", "agent_findings")

    if not os.path.isdir(findings_dir):
        print("[]")
        return []

    results = []
    for filename in sorted(os.listdir(findings_dir), reverse=True):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(findings_dir, filename)) as f:
            entry = json.load(f)

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
    parser = argparse.ArgumentParser(description="Query agent findings")
    parser.add_argument("--type", help="Filter by finding type")
    parser.add_argument("--sheet", help="Filter by source sheet")
    parser.add_argument("--since", help="Filter by date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--dir", help="Findings directory override")
    args = parser.parse_args()
    query_findings(args.dir, args.type, args.sheet, args.since, args.limit)
