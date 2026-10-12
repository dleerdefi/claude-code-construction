#!/usr/bin/env python3
"""Write a structured finding to the skill's own findings folder.

A finding goes to .construction/skills/<skill>/findings/<date>_<type>_<id>.json, in
both modes: it is the skill's working data, which is the plugin's to write in every
project. Writing it creates nothing else under .construction/ and never
.construction/project.yaml, which only AgentCM writes, so it does not change the
mode the next skill detects.

Usage:
  write_finding.py --skill bid-tabulator --type bid_tabulation --title "..." [--data '{...}']
"""

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime

SKILL_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def findings_dir_for(root, skill):
    if not SKILL_NAME.match(skill or ""):
        raise ValueError(f"--skill must be the skill's folder name (lowercase letters, digits, hyphens), got {skill!r}")
    return os.path.join(root, ".construction", "skills", skill, "findings")


def write_finding(finding_type, title, data=None, source_sheet=None, source_sheets=None,
                  output_file=None, output_files=None, findings_dir=None, skill=None):
    if findings_dir is None:
        findings_dir = findings_dir_for(os.getcwd(), skill)

    os.makedirs(findings_dir, exist_ok=True)

    finding_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()

    entry = {
        "id": finding_id,
        "skill": skill,
        "type": finding_type,
        "title": title,
        "timestamp": timestamp,
        "source_sheets": source_sheets or ([source_sheet] if source_sheet else []),
        "output_files": output_files or ([output_file] if output_file else []),
        "data": json.loads(data) if isinstance(data, str) else (data or {}),
    }

    filename = f"{timestamp[:10]}_{finding_type}_{finding_id}.json"
    filepath = os.path.join(findings_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(entry, f, indent=2)

    print(f"OK: Finding written → {filepath}")
    return filepath


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):  # a Windows pipe is cp1252: the arrow below would raise
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description="Write a finding to .construction/skills/<skill>/findings/")
    parser.add_argument("--skill", required=True, help="The skill writing it: its folder name, e.g. bid-tabulator")
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

    try:
        write_finding(args.type, args.title, args.data, args.source_sheet, source_sheets,
                      args.output_file, output_files, args.dir, args.skill)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(2)
