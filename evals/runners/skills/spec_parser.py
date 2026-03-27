"""Spec parser eval runner.

Parses a single specification section PDF to extract structured data:
submittals, manufacturers, standards, quality assurance requirements.
"""

import csv
import json
import re
from pathlib import Path

from evals.runners.helpers import (
    PROJECT_ROOT, write_graph_entry, write_eval_result, get_project_dir,
)


def fix_missing_spaces(text):
    """Fix text extracted without spaces (common PDF text encoding issue)."""
    words = text.split()
    if len(words) > 3:
        if not any(len(w) > 30 for w in words):
            return text
    fixed = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    fixed = re.sub(r"\.([A-Za-z])", r". \1", fixed)
    fixed = re.sub(r",([A-Za-z])", r", \1", fixed)
    COMMON_WORDS = (
        r"(?<=[a-z])(for|and|the|of|to|in|by|or|with|from|per|as|on|at|"
        r"is|be|an|no|if|not|are|was|that|this|has|have|will|shall|may|"
        r"each|all|any|its|per|into|upon|than|also|such|must|only|"
        r"items|section|submit|provide|include|required|materials|"
        r"prior|during|after|before|under|above|below|between)"
    )
    fixed = re.sub(COMMON_WORDS, r" \1", fixed, flags=re.IGNORECASE)
    fixed = re.sub(r"  +", " ", fixed)
    return fixed


def run_spec_parser(case, run_dir):
    """Execute spec-parser: extract structured data from a spec section PDF."""
    import pdfplumber
    import yaml

    evals_dir = PROJECT_ROOT / "evals"
    pdf_rel = case["inputs"]["files"][0]
    pdf_path = evals_dir / pdf_rel

    print(f"\n{'='*60}")
    print(f"SKILL: spec-parser")
    print(f"Input: {pdf_path.name}")
    print(f"Output: {run_dir}")
    print(f"{'='*60}")

    # Step 1: Extract full text
    print("\n[Step 1] Extracting text...")
    with pdfplumber.open(str(pdf_path)) as pdf:
        full_text = ""
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"
    # Fix missing spaces from PDF text encoding (apply per-line)
    fixed_lines = [fix_missing_spaces(line) for line in full_text.split("\n")]
    full_text = "\n".join(fixed_lines)
    print(f"  Pages: {len(pdf.pages)}, Characters: {len(full_text)}")

    # Step 2: Parse section number and title
    print("\n[Step 2] Identifying section...")
    fname = pdf_path.stem
    sec_match = re.match(r"(\d{2}\s+\d{2}\s*\d{2}(?:\.\d+)?)\s*-\s*(.*)", fname)
    section_number = sec_match.group(1).strip() if sec_match else "unknown"
    section_title = sec_match.group(2).strip() if sec_match else fname
    print(f"  Section: {section_number} - {section_title}")

    # Step 3: Identify 3-part structure
    print("\n[Step 3] Parsing 3-part CSI structure...")
    lines = full_text.split("\n")

    parts = {"part_1": [], "part_2": [], "part_3": []}
    current_part = None

    for line in lines:
        stripped = line.strip()
        upper = stripped.upper()

        if re.match(r"PART\s*1\b", upper):
            current_part = "part_1"
        elif re.match(r"PART\s*2\b", upper):
            current_part = "part_2"
        elif re.match(r"PART\s*3\b", upper):
            current_part = "part_3"

        if current_part:
            parts[current_part].append(stripped)

    for part, content in parts.items():
        print(f"  {part}: {len(content)} lines")

    # Step 4: Extract submittals from Part 1
    print("\n[Step 4] Extracting submittals...")
    submittals = []
    in_submittals = False
    current_item = []

    for line in parts["part_1"]:
        upper = line.upper()
        if "SUBMITTALS" in upper and not in_submittals:
            in_submittals = True
            continue
        if in_submittals:
            # Stop at next numbered heading (e.g., "1.05 QUALITY ASSURANCE" or "1.05QUALITYASSURANCE")
            if re.match(r"\d+\.\d+\s*[A-Z]", line) and "SUBMITTAL" not in upper:
                if current_item:
                    submittals.append(" ".join(current_item))
                break
            # New lettered item
            m = re.match(r"([A-Z])\.\s+(.*)", line)
            if m:
                if current_item:
                    submittals.append(" ".join(current_item))
                current_item = [m.group(2).strip()]
            elif current_item and line.strip():
                current_item.append(line.strip())

    if current_item:
        submittals.append(" ".join(current_item))
    print(f"  Submittals found: {len(submittals)}")

    # Step 5: Extract manufacturers from Part 2
    print("\n[Step 5] Extracting manufacturers...")
    manufacturers = []
    for line in parts["part_2"]:
        # Common patterns: "Manufacturer: XYZ Corp" or "A. XYZ Corp" or "Basis of Design: XYZ"
        if any(kw in line.upper() for kw in ["MANUFACTURER", "BASIS OF DESIGN", "APPROVED"]):
            manufacturers.append(line.strip())
        # Also catch lines that look like company names (all caps, short)
        m = re.match(r"[A-Z]\.\s+([A-Z][A-Za-z\s&,.']+(?:Corp|Inc|LLC|Co\.|Ltd|Company))", line)
        if m:
            manufacturers.append(m.group(1).strip())
    print(f"  Manufacturers found: {len(manufacturers)}")

    # Step 6: Extract referenced standards
    print("\n[Step 6] Extracting standards...")
    standards = set()
    std_pattern = re.compile(
        r"(ANSI|ASTM|NFPA|UL|AAMA|AWS|ACI|AISC|ICC|ASHRAE|SMACNA|NEMA)\s*[A-Z]?\s*[\d./]+"
    )
    for line in lines:
        for m in std_pattern.finditer(line):
            standards.add(m.group(0).strip())
    standards = sorted(standards)
    print(f"  Standards found: {len(standards)}")

    # Step 7: Write outputs
    print("\n[Step 7] Writing outputs...")

    parsed_data = {
        "section_number": section_number,
        "section_title": section_title,
        "division": int(section_number[:2]) if section_number[:2].isdigit() else 0,
        "structure": {
            "part_1_lines": len(parts["part_1"]),
            "part_2_lines": len(parts["part_2"]),
            "part_3_lines": len(parts["part_3"]),
        },
        "submittals": submittals,
        "manufacturers": manufacturers,
        "standards": standards,
    }

    # YAML output
    yaml_path = run_dir / "parsed_spec.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(parsed_data, f, default_flow_style=False, sort_keys=False)
    print(f"  YAML: {yaml_path.name}")

    # JSON output
    json_path = run_dir / "parsed_spec.json"
    with open(json_path, "w") as f:
        json.dump(parsed_data, f, indent=2)

    # Graph entry
    graph_path = write_graph_entry(
        run_dir, "spec_parsed",
        f"Parsed {section_number} - {section_title}",
        {
            "section": section_number,
            "submittals": len(submittals),
            "manufacturers": len(manufacturers),
            "standards": len(standards),
        },
        project_dir=get_project_dir(case),
    )
    print(f"  Graph: {graph_path.name}")

    # Step 8: Auto-score
    print("\n[Step 8] Auto-scoring...")
    scores = {}
    scores["structure"] = 1.0 if all(len(v) > 0 for v in parts.values()) else 0.5
    scores["submittals"] = min(len(submittals) / 3.0, 1.0)  # Expect ~3+ submittals
    scores["manufacturers"] = min(len(manufacturers) / 2.0, 1.0)  # Expect ~2+ manufacturers
    scores["standards"] = min(len(standards) / 3.0, 1.0)  # Expect ~3+ standards
    scores["completeness"] = 1.0 if all(parsed_data[k] for k in ["submittals", "standards"]) else 0.5

    for k, v in scores.items():
        print(f"  {k}: {v:.2f}")

    artifacts = {"yaml": str(yaml_path), "json": str(json_path), "graph_entry": str(graph_path)}
    result_path = write_eval_result(case, run_dir, scores, artifacts,
                                    f"Parsed {section_number}: {len(submittals)} submittals, {len(manufacturers)} manufacturers, {len(standards)} standards")
    print(f"  Result: {result_path}")
    return json.loads(result_path.read_text())
