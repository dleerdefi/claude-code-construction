"""Code researcher eval runner.

Scores pre-extracted gap analysis artifacts against ground truth.

The code-researcher skill produces YAML/markdown artifacts in a
`.construction/skills/code-researcher/` directory. This runner loads those
artifacts from run_dir and scores them against a ground truth YAML.

Scoring philosophy: measure what the engineer cares about — correct
jurisdiction, complete topic coverage, accurate code citations, proper
gap classification, and no compliance determinations.
"""

import json
import re
import sys
from pathlib import Path

from evals.runners.helpers import (
    PROJECT_ROOT,
    write_graph_entry,
    write_eval_result,
    get_project_dir,
)


# ---------------------------------------------------------------------------
# Ground truth loading
# ---------------------------------------------------------------------------

def _load_ground_truth(gt_path):
    """Load and return the ground truth YAML."""
    import yaml

    with open(gt_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_yaml(path):
    """Load a YAML file, return empty dict on failure."""
    import yaml

    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _collect_all_text(run_dir):
    """Collect all text from YAML and markdown files in run_dir for framing checks."""
    texts = []
    for f in run_dir.rglob("*"):
        if f.suffix in (".yaml", ".yml", ".md"):
            try:
                texts.append(f.read_text(encoding="utf-8"))
            except Exception:
                pass
    return " ".join(texts)


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def _score_jurisdiction_accuracy(jurisdiction_data, gt):
    """Score: did the skill identify the correct jurisdiction and code editions?"""
    gt_jurisdiction = gt.get("required_jurisdiction", {})
    gt_keywords = gt_jurisdiction.get("keywords_any", [])

    if not gt_keywords:
        return 1.0 if jurisdiction_data else 0.0

    # Flatten jurisdiction data to text for keyword matching
    juris_text = json.dumps(jurisdiction_data).lower()

    matched = sum(1 for kw in gt_keywords if kw.lower() in juris_text)

    if matched == 0:
        print("    Jurisdiction: no keywords matched")
        for kw in gt_keywords:
            print(f"      Missing: {kw}")
        return 0.0

    score = min(matched / 3.0, 1.0)  # Need at least 3 keywords for full score
    if matched < 3:
        missing = [kw for kw in gt_keywords if kw.lower() not in juris_text]
        print(f"    Jurisdiction: {matched} keywords matched (need 3+), missing: {missing[:3]}")

    return round(score, 3)


def _score_topic_coverage(scope_data, topics_dir, gt):
    """Score: are all required research topics present in the outline?"""
    gt_topics = gt.get("required_topics", [])
    if not gt_topics:
        return 1.0

    # Collect topic text from scope_definition and topic files
    all_topic_text = json.dumps(scope_data).lower()

    # Also check topic files
    if topics_dir.is_dir():
        for tf in topics_dir.glob("*.yaml"):
            data = _load_yaml(tf)
            all_topic_text += " " + json.dumps(data).lower()

    found = 0
    for gt_topic in gt_topics:
        keywords = gt_topic.get("keywords", [])
        # Topic is covered if any keyword matches
        if any(kw.lower() in all_topic_text for kw in keywords):
            found += 1
        else:
            print(f"    Topic missing: {gt_topic.get('title', gt_topic.get('slug', '?'))}")

    # Also give partial credit for optional topics
    gt_optional = gt.get("optional_topics", [])
    optional_found = 0
    for opt in gt_optional:
        keywords = opt.get("keywords", [])
        if any(kw.lower() in all_topic_text for kw in keywords):
            optional_found += 1

    # Base score from required topics, bonus from optional
    base_score = found / max(len(gt_topics), 1)
    if gt_optional:
        bonus = 0.1 * (optional_found / len(gt_optional))
        base_score = min(base_score + bonus, 1.0)

    return round(base_score, 3)


def _score_code_citation_accuracy(topics_dir, gap_data, gt):
    """Score: are code section references correct?"""
    gt_citations = gt.get("expected_citations", [])
    if not gt_citations:
        return 1.0

    # Collect all text from topic files and gap analysis
    all_text = json.dumps(gap_data).lower()
    if topics_dir.is_dir():
        for tf in topics_dir.glob("*.yaml"):
            data = _load_yaml(tf)
            all_text += " " + json.dumps(data).lower()

    found = 0
    for citation in gt_citations:
        section = citation.get("section", "")
        # Normalize section reference for matching
        section_lower = section.lower()
        # Try exact match and common variations
        if section_lower in all_text:
            found += 1
        elif section.replace("Table ", "table ").lower() in all_text:
            found += 1
        elif re.sub(r"\s+", "", section_lower) in re.sub(r"\s+", "", all_text):
            found += 1
        else:
            print(f"    Citation missing: {citation.get('code', '')} {section} ({citation.get('topic', '')})")

    return round(found / max(len(gt_citations), 1), 3)


def _score_research_framing(run_dir, gt):
    """Score: are there zero compliance determinations?"""
    gt_framing = gt.get("framing_violations", {})
    forbidden = gt_framing.get("forbidden_terms", [])
    if not forbidden:
        return 1.0

    all_text = _collect_all_text(run_dir).lower()
    violations = []
    for term in forbidden:
        # Search for the term as a word boundary match
        pattern = r'\b' + re.escape(term.lower()) + r'\b'
        if re.search(pattern, all_text):
            violations.append(term)

    if violations:
        print(f"    Framing violations found: {violations}")
        # Deduct proportionally but never go below 0
        score = max(0.0, 1.0 - (len(violations) * 0.25))
        return round(score, 3)

    return 1.0


def _score_pass1_extraction(pass1_summary, pass1_inventory, gt):
    """Score: were project documents read before web research?"""
    gt_pass1 = gt.get("pass1_expectations", {})

    checks = 0
    total = 2

    # Check that inventory exists and has content
    if gt_pass1.get("inventory_should_exist", False):
        if pass1_inventory or pass1_summary:
            checks += 1
        else:
            print("    Pass 1: no inventory or summary found")

    # Check that expected documents were read
    expected_docs = gt_pass1.get("documents_should_be_read", [])
    if expected_docs:
        read_text = json.dumps(pass1_inventory).lower() + " " + json.dumps(pass1_summary).lower()
        docs_found = sum(1 for doc in expected_docs if doc.lower() in read_text)
        if docs_found >= len(expected_docs):
            checks += 1
        else:
            missing = [d for d in expected_docs if d.lower() not in read_text]
            print(f"    Pass 1: documents not read: {missing}")
    else:
        checks += 1  # No specific docs required

    return round(checks / max(total, 1), 3)


def _score_gap_classification(gap_data, gt):
    """Score: are gaps classified with severity and confidence?"""
    gt_classification = gt.get("gap_classification", {})
    required_fields = gt_classification.get("required_fields", [])
    severity_values = [v.lower() for v in gt_classification.get("severity_values", [])]
    confidence_values = [v.lower() for v in gt_classification.get("confidence_values", [])]

    if not required_fields:
        return 1.0

    gaps = gap_data.get("gaps", [])
    if not gaps:
        # No gaps found — check if there's at least an already_addressed section
        if gap_data.get("already_addressed"):
            print("    Gap classification: no gaps but already_addressed present — partial credit")
            return 0.5
        print("    Gap classification: no gaps or already_addressed found")
        return 0.0

    classified = 0
    for gap in gaps:
        has_all_fields = True
        for field in required_fields:
            val = str(gap.get(field, "")).lower()
            if not val:
                has_all_fields = False
                break
            # Validate values
            if field == "severity" and severity_values and val not in severity_values:
                has_all_fields = False
            if field == "confidence" and confidence_values and val not in confidence_values:
                has_all_fields = False
        if has_all_fields:
            classified += 1
        else:
            print(f"    Gap {gap.get('id', '?')}: missing or invalid classification fields")

    return round(classified / max(len(gaps), 1), 3)


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_code_researcher(case, run_dir):
    """Load pre-extracted research artifacts, score against GT.

    Expects code research artifacts in run_dir:
    - scope_definition.yaml
    - pass1_project_inventory.yaml
    - pass1_summary.yaml
    - jurisdiction.yaml
    - topics/*.yaml
    - gap_analysis.yaml
    - report_*.md
    """
    print(f"\n{'='*60}")
    print(f"SKILL: code-researcher")
    print(f"Output: {run_dir}")
    print(f"{'='*60}")

    # Load artifacts
    print(f"\n[Step 1] Loading pre-extracted artifacts...")

    scope_path = run_dir / "scope_definition.yaml"
    pass1_inv_path = run_dir / "pass1_project_inventory.yaml"
    pass1_sum_path = run_dir / "pass1_summary.yaml"
    juris_path = run_dir / "jurisdiction.yaml"
    topics_dir = run_dir / "topics"
    gap_path = run_dir / "gap_analysis.yaml"

    scope_data = _load_yaml(scope_path) if scope_path.exists() else {}
    pass1_inventory = _load_yaml(pass1_inv_path) if pass1_inv_path.exists() else {}
    pass1_summary = _load_yaml(pass1_sum_path) if pass1_sum_path.exists() else {}
    jurisdiction_data = _load_yaml(juris_path) if juris_path.exists() else {}
    gap_data = _load_yaml(gap_path) if gap_path.exists() else {}

    # Find report file
    report_files = list(run_dir.glob("report_*.md"))
    report_path = report_files[0] if report_files else None

    # Count topic files
    topic_count = len(list(topics_dir.glob("*.yaml"))) if topics_dir.is_dir() else 0

    # Summary
    artifacts_found = []
    if scope_data:
        artifacts_found.append("scope_definition")
    if pass1_inventory:
        artifacts_found.append("pass1_inventory")
    if pass1_summary:
        artifacts_found.append("pass1_summary")
    if jurisdiction_data:
        artifacts_found.append("jurisdiction")
    if topic_count:
        artifacts_found.append(f"topics({topic_count})")
    if gap_data:
        artifacts_found.append("gap_analysis")
    if report_path:
        artifacts_found.append("report")

    print(f"  Artifacts: {', '.join(artifacts_found) or 'NONE'}")

    if not artifacts_found:
        print("  ERROR: No artifacts found. Run Claude Code extraction first.")
        return None

    # Write graph entry
    print(f"\n[Step 2] Writing graph entry...")
    gaps = gap_data.get("gaps", [])
    graph_data = {
        "topics_researched": topic_count,
        "gaps_found": len(gaps),
        "gaps_high": sum(1 for g in gaps if str(g.get("severity", "")).upper() == "HIGH"),
        "gaps_medium": sum(1 for g in gaps if str(g.get("severity", "")).upper() == "MEDIUM"),
        "gaps_low": sum(1 for g in gaps if str(g.get("severity", "")).upper() == "LOW"),
    }
    graph_path = write_graph_entry(
        run_dir,
        "code_gap_analysis",
        f"Code gap analysis — {len(gaps)} gaps identified",
        graph_data,
        project_dir=get_project_dir(case),
    )
    print(f"  Graph: {graph_path.name}")

    # Score against ground truth
    print(f"\n[Step 3] Scoring against ground truth...")
    scores = {}
    gt_rel = case.get("ground_truth")
    if gt_rel:
        gt_path = PROJECT_ROOT / "evals" / "cases" / case["skill"] / gt_rel
        if gt_path.exists():
            gt = _load_ground_truth(gt_path)

            scores["jurisdiction_accuracy"] = _score_jurisdiction_accuracy(jurisdiction_data, gt)
            scores["topic_coverage"] = _score_topic_coverage(scope_data, topics_dir, gt)
            scores["code_citation_accuracy"] = _score_code_citation_accuracy(topics_dir, gap_data, gt)
            scores["research_framing"] = _score_research_framing(run_dir, gt)
            scores["pass1_extraction"] = _score_pass1_extraction(pass1_summary, pass1_inventory, gt)
            scores["gap_classification"] = _score_gap_classification(gap_data, gt)

            print(f"\n  --- SCORES ---")
            for metric, value in scores.items():
                weight = case.get("scoring", {}).get(metric, {}).get("weight", 0)
                print(f"  {metric}: {value:.3f} (weight={weight})")

            weighted = sum(
                scores.get(m, 0)
                * case.get("scoring", {}).get(m, {}).get("weight", 0)
                for m in scores
            )
            print(f"\n  WEIGHTED TOTAL: {weighted:.3f}")
        else:
            print(f"  Ground truth not found: {gt_path}")

    artifacts = {
        "scope_definition": str(scope_path) if scope_data else None,
        "pass1_inventory": str(pass1_inv_path) if pass1_inventory else None,
        "pass1_summary": str(pass1_sum_path) if pass1_summary else None,
        "jurisdiction": str(juris_path) if jurisdiction_data else None,
        "topic_count": topic_count,
        "gap_analysis": str(gap_path) if gap_data else None,
        "report": str(report_path) if report_path else None,
        "graph_entry": str(graph_path),
    }
    result_path = write_eval_result(
        case, run_dir, scores, artifacts,
        f"Code gap analysis — {len(gaps)} gaps",
    )
    print(f"\n  Result: {result_path}")
    return json.loads(result_path.read_text())
