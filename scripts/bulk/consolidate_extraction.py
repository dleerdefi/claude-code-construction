#!/usr/bin/env python3
"""Consolidate individual sheet extraction findings into a unified semantic index."""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime

def consolidate(findings_dir, finding_type="sheet_extraction", output="semantic_index.yaml"):
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML not installed. Run: pip install PyYAML")
        sys.exit(1)

    if not os.path.isdir(findings_dir):
        print(f"ERROR: Findings directory not found: {findings_dir}")
        sys.exit(1)

    # Collect all sheet extraction findings
    sheets = {}
    cross_refs = defaultdict(set)
    materials_index = defaultdict(list)
    schedules_found = []
    disciplines = defaultdict(lambda: defaultdict(int))
    errors = []

    for filename in sorted(os.listdir(findings_dir)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(findings_dir, filename)
        try:
            with open(filepath) as f:
                entry = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            errors.append({"file": filename, "error": str(e)})
            continue

        if entry.get("type") != finding_type:
            continue

        data = entry.get("data", {})
        sheet_num = data.get("sheet_number", "")
        if not sheet_num:
            # Try source_sheets
            source = entry.get("source_sheets", [])
            sheet_num = source[0] if source else filename

        # Build compact sheet entry
        sheet_entry = {
            "title": data.get("sheet_title", ""),
            "type": data.get("drawing_type", "unknown"),
            "summary": data.get("content_summary", ""),
            "rooms": [r.get("name", r.get("number", "")) if isinstance(r, dict) else r
                      for r in data.get("rooms", [])],
            "key_dimensions": data.get("dimensions", []),
            "materials": data.get("materials_called_out", []),
            "outbound_refs": data.get("references_to_other_sheets", []),
            "schedules": [s.get("type", s) if isinstance(s, dict) else s
                         for s in data.get("schedules_present", [])],
            "flags": data.get("coordination_flags", []),
            "revision_clouds": data.get("revision_clouds", []),
        }
        sheets[sheet_num] = sheet_entry

        # Build cross-reference index
        for ref in sheet_entry["outbound_refs"]:
            cross_refs[sheet_num].add(ref)

        # Build materials index
        for mat in sheet_entry["materials"]:
            materials_index[mat].append(sheet_num)

        # Collect schedules
        for s in data.get("schedules_present", []):
            if isinstance(s, dict):
                s["sheet"] = sheet_num
                schedules_found.append(s)

        # Tally discipline stats
        prefix = sheet_num.split("-")[0] if "-" in sheet_num else "?"
        drawing_type = sheet_entry["type"]
        disc_name = _prefix_to_discipline(prefix)
        disciplines[disc_name]["sheet_count"] += 1
        disciplines[disc_name][drawing_type] = disciplines[disc_name].get(drawing_type, 0) + 1

    # Build inbound references
    inbound = defaultdict(list)
    for src, targets in cross_refs.items():
        for tgt in targets:
            inbound[tgt].append(src)
    for sheet_num in sheets:
        sheets[sheet_num]["inbound_refs"] = inbound.get(sheet_num, [])

    # Assemble output
    index = {
        "generated": datetime.now().isoformat(),
        "sheets_processed": len(sheets),
        "extraction_method": "vision",
        "sheets": sheets,
        "cross_references": {k: sorted(v) for k, v in cross_refs.items()},
        "disciplines": dict(disciplines),
        "materials_index": {k: sorted(set(v)) for k, v in materials_index.items()},
        "schedules_found": schedules_found,
        "errors": errors,
    }

    with open(output, "w") as f:
        yaml.dump(index, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"OK: {output} ({len(sheets)} sheets consolidated)")

def _prefix_to_discipline(prefix):
    mapping = {
        "G": "General", "C": "Civil", "L": "Landscape", "S": "Structural",
        "A": "Architectural", "I": "Interiors", "E": "Electrical",
        "M": "Mechanical", "P": "Plumbing", "FP": "Fire Protection",
        "F": "Fire Protection", "T": "Telecommunications",
    }
    return mapping.get(prefix.upper(), f"Other ({prefix})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolidate sheet extraction findings")
    parser.add_argument("--findings-dir", required=True, help="Agent findings directory")
    parser.add_argument("--type", default="sheet_extraction", help="Finding type to filter")
    parser.add_argument("--output", "-o", default="semantic_index.yaml")
    args = parser.parse_args()
    consolidate(args.findings_dir, args.type, args.output)
