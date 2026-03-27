#!/usr/bin/env python3
"""Write a structured finding to the agent findings directory for graph retention."""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime

def write_finding(finding_type, title, data=None, source_sheet=None, source_sheets=None,
                  output_file=None, output_files=None, findings_dir=None):
    if findings_dir is None:
        # Look for .construction directory
        root = os.getcwd()
        findings_dir = os.path.join(root, ".construction", "agent_findings")

    os.makedirs(findings_dir, exist_ok=True)

    finding_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()

    entry = {
        "id": finding_id,
        "type": finding_type,
        "title": title,
        "timestamp": timestamp,
        "source_sheets": source_sheets or ([source_sheet] if source_sheet else []),
        "output_files": output_files or ([output_file] if output_file else []),
        "data": json.loads(data) if isinstance(data, str) else (data or {}),
    }

    filename = f"{timestamp[:10]}_{finding_type}_{finding_id}.json"
    filepath = os.path.join(findings_dir, filename)

    with open(filepath, "w") as f:
        json.dump(entry, f, indent=2)

    print(f"OK: Finding written → {filepath}")
    return filepath

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write a finding to the graph")
    parser.add_argument("--type", required=True, help="Finding type")
    parser.add_argument("--title", required=True, help="Finding title")
    parser.add_argument("--data", help="JSON data string")
    parser.add_argument("--source-sheet", help="Source sheet number")
    parser.add_argument("--source-sheets", help="JSON array of source sheets")
    parser.add_argument("--output-file", help="Output file path")
    parser.add_argument("--output-files", help="JSON array of output file paths")
    parser.add_argument("--dir", help="Findings directory override")
    args = parser.parse_args()

    source_sheets = json.loads(args.source_sheets) if args.source_sheets else None
    output_files = json.loads(args.output_files) if args.output_files else None

    write_finding(args.type, args.title, args.data, args.source_sheet, source_sheets,
                  args.output_file, output_files, args.dir)
