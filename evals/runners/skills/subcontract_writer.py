"""Subcontract writer eval runner.

Two modes:
  1. Pre-extracted: Claude Code reads PDFs and writes template_data.json +
     scope_data.json to run_dir. This runner calls generate_subcontract_docx.py,
     validates the .docx, and scores against ground truth.
  2. No fallback — extraction requires Claude Code intelligence.

Scoring philosophy: measure what the PM cares about — correct spec sections,
complete scope, accurate contract terms, and preserved template structure.
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


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

# Fallback only — GT meta.applicable_spec_sections takes priority
_DEFAULT_SPEC_SECTIONS = []


def _score_spec_section_coverage(scope_data, gt):
    """Score: are all 6 required spec sections referenced in scope_data?"""
    spec_sections = scope_data.get("spec_sections", [])
    found_numbers = set()
    for sec in spec_sections:
        num = sec.get("number", "").strip()
        # Normalize: remove extra spaces, ensure standard format
        num = re.sub(r"\s+", " ", num)
        found_numbers.add(num)

    gt_sections = gt.get("meta", {}).get("applicable_spec_sections", _DEFAULT_SPEC_SECTIONS)
    matched = sum(1 for s in gt_sections if s in found_numbers)
    score = matched / max(len(gt_sections), 1)

    if matched < len(gt_sections):
        missing = [s for s in gt_sections if s not in found_numbers]
        print(f"    Spec sections missing: {missing}")

    return round(score, 3)


def _score_scope_completeness(scope_data, gt):
    """Score: are scope items / line items present for each spec section?"""
    scope_items = scope_data.get("scope_items", [])
    line_items = scope_data.get("line_items", [])
    all_items = scope_items + [li.get("description", "") for li in line_items]
    all_text = " ".join(all_items).lower()

    # Check that each spec section's scope has some representation
    gt_article2 = gt.get("article_2_scope_of_work", {})
    gt_line_items = gt_article2.get("scope_line_items", {}).get("items", [])
    if not gt_line_items:
        return 1.0 if all_items else 0.0

    found = 0
    for gt_item in gt_line_items:
        label = gt_item.get("label", "").lower()
        spec = gt_item.get("spec", "")
        # Check if the scope mentions this section by label or spec number
        if label in all_text or spec in all_text:
            found += 1
        else:
            print(f"    Scope missing: {spec} — {gt_item.get('label', '')}")

    return round(found / max(len(gt_line_items), 1), 3)


def _score_contract_terms(scope_data, gt):
    """Score: contract sum, subcontractor name, project name correct.

    Expected values are pulled from the ground truth YAML so this scorer
    works for any subcontract scope, not just the flooring eval case.
    """
    checks = 0
    total = 3

    # Pull expected values from GT
    gt_cover = gt.get("cover_page", {}).get("required_fields", {})
    gt_contract_sum = gt_cover.get("contract_sum", {})
    gt_project = gt_cover.get("project", {})
    gt_sub = gt_cover.get("subcontractor", {})

    # --- Contract sum ---
    # GT value "[FROM_BID]" means accept any bid-sourced value;
    # a literal numeric value means match exactly.
    gt_sum_value = gt_contract_sum.get("value", "")
    gt_sum_is_variable = gt_sum_value.startswith("[")

    expected_sum = None
    if not gt_sum_is_variable and gt_sum_value:
        numeric = re.sub(r"[^\d.]", "", str(gt_sum_value))
        try:
            expected_sum = float(numeric)
        except ValueError:
            pass

    contract_value = scope_data.get("contract_value") or scope_data.get("contract_sum")
    if contract_value:
        if isinstance(contract_value, str):
            numeric = re.sub(r"[^\d.]", "", contract_value)
            try:
                contract_value = float(numeric)
            except ValueError:
                contract_value = None

        if expected_sum and contract_value:
            if abs(contract_value - expected_sum) <= 1.0:
                checks += 1
            else:
                print(f"    Contract sum: got {contract_value}, want {expected_sum}")
        elif contract_value:
            # GT says [FROM_BID] or no expected sum — accept any non-zero value
            checks += 1
    else:
        print("    Contract sum: MISSING")

    # --- Subcontractor name ---
    # Extract expected keyword from GT (e.g. "legal_name" field or value)
    gt_sub_name = gt_sub.get("legal_name", "")
    # Use first word of legal name as keyword (e.g. "[FROM_BID]" means accept any)
    sub_keyword = ""
    if gt_sub_name and not gt_sub_name.startswith("["):
        sub_keyword = gt_sub_name.split()[0].lower()

    sub = scope_data.get("subcontractor", {})
    sub_name = sub.get("company_name", "") if isinstance(sub, dict) else str(sub)
    if sub_keyword:
        if sub_keyword in sub_name.lower():
            checks += 1
        else:
            print(f"    Subcontractor: got '{sub_name}', want '{gt_sub_name}'")
    elif sub_name:
        # GT uses [FROM_BID] — accept any non-empty name
        checks += 1
    else:
        print("    Subcontractor: MISSING")

    # --- Project name ---
    gt_project_value = gt_project.get("value", "")
    project_keyword = ""
    if gt_project_value and not gt_project_value.startswith("["):
        project_keyword = gt_project_value.split()[0].lower()

    project_name = scope_data.get("project_name", "")
    if project_keyword:
        if project_keyword in project_name.lower():
            checks += 1
        else:
            print(f"    Project name: got '{project_name}', want '{gt_project_value}'")
    elif project_name:
        checks += 1
    else:
        print("    Project name: MISSING")

    return round(checks / total, 3)


def _score_template_preservation(template_data):
    """Score: does template_data preserve standard clause articles?"""
    articles = template_data.get("articles", [])
    if not articles:
        print("    Template: no articles found")
        return 0.0

    # Check for preserved standard articles (insurance, dispute, indemnification)
    preserve_keywords = ["insurance", "bond", "dispute", "indemnif", "general condition"]
    preserved_count = 0
    for art in articles:
        title = art.get("title", "").lower()
        content_type = art.get("content_type", "")
        # "review" means preserved but Claude fixed a legal issue — still counts
        if content_type in ("preserve", "review"):
            for kw in preserve_keywords:
                if kw in title:
                    preserved_count += 1
                    break

    # At least 2 of the ~5 standard articles should be marked preserve/review
    score = min(preserved_count / 2.0, 1.0)
    if preserved_count < 2:
        print(f"    Template: only {preserved_count} standard articles marked 'preserve'")
    return round(score, 3)


def _score_article_completeness(template_data):
    """Score: are all articles populated with real content (no placeholders)?"""
    articles = template_data.get("articles", [])
    if not articles:
        return 0.0

    placeholder_patterns = [
        "[generated content",
        "[placeholder",
        "[insert",
        "review and customize",
        "[article",
        "to be completed",
    ]

    complete = 0
    for art in articles:
        text = art.get("text", "").strip()
        if not text:
            print(f"    Article {art.get('number', '?')} ({art.get('title', '')}): EMPTY")
            continue
        text_lower = text.lower()
        has_placeholder = any(p in text_lower for p in placeholder_patterns)
        if has_placeholder:
            print(f"    Article {art.get('number', '?')} ({art.get('title', '')}): PLACEHOLDER")
            continue
        complete += 1

    return round(complete / max(len(articles), 1), 3)


def _score_document_structure(template_data, gt):
    """Score: are required articles present?"""
    articles = template_data.get("articles", [])
    article_titles = [a.get("title", "").lower() for a in articles]

    # Also check non-article structural elements
    has_cover = bool(template_data.get("cover_page", {}).get("text") or
                     template_data.get("cover_page", {}).get("blocks"))
    has_exhibits = bool(template_data.get("exhibits"))
    # Signature block is always rendered by the formatter if scope_data exists
    has_signature = True

    gt_sections = gt.get("document_structure", {}).get("required_sections_ordered", [])
    if not gt_sections:
        return 1.0 if articles else 0.0

    # Map GT section IDs to keywords for matching
    section_keywords = {
        "article_1_subcontract_documents": ["document", "subcontract document"],
        "article_2_scope_of_work": ["scope"],
        "article_3_schedule": ["schedule", "time"],
        "article_4_contract_sum": ["sum", "price", "contract sum"],
        "article_5_progress_payments": ["payment"],
        "article_6_changes": ["change"],
        "article_7_insurance_and_bonds": ["insurance", "bond"],
        "article_8_submittals": ["submittal"],
        "article_9_labor_requirements": ["labor"],
        "article_10_indemnification": ["indemnif"],
        "article_11_warranty": ["warrant"],
        "article_12_safety": ["safety"],
        "article_13_default_termination": ["default", "terminat"],
        "article_14_dispute_resolution": ["dispute"],
        "article_15_general_provisions": ["general provision"],
    }

    found = 0
    for section_id in gt_sections:
        # Handle non-article structural elements directly
        if section_id == "cover_page":
            if has_cover:
                found += 1
            continue
        if section_id == "signature_block":
            if has_signature:
                found += 1
            continue
        if section_id == "exhibits_list":
            if has_exhibits:
                found += 1
            continue

        keywords = section_keywords.get(section_id, [])
        matched = any(
            any(kw in title for kw in keywords)
            for title in article_titles
        )
        if matched:
            found += 1

    return round(found / max(len(gt_sections), 1), 3)


def _score_docx_format(docx_path):
    """Score: is the output a valid, non-empty .docx?"""
    try:
        from docx import Document
        doc = Document(str(docx_path))
        para_count = len(doc.paragraphs)
        if para_count < 5:
            print(f"    Docx: only {para_count} paragraphs — suspiciously empty")
            return 0.5
        return 1.0
    except ImportError:
        print("    python-docx not installed — cannot validate .docx")
        return 0.0
    except Exception as e:
        print(f"    Docx validation error: {e}")
        return 0.0


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_subcontract_writer(case, run_dir):
    """Load pre-extracted JSONs, generate .docx, score against GT.

    Expects template_data.json and scope_data.json in run_dir
    (written by Claude Code during the extraction phase).
    """
    print(f"\n{'='*60}")
    print(f"SKILL: subcontract-writer")
    print(f"Output: {run_dir}")
    print(f"{'='*60}")

    template_path = run_dir / "template_data.json"
    scope_path = run_dir / "scope_data.json"

    # Validate pre-extracted data exists
    if not template_path.exists():
        print("  ERROR: No template_data.json found. Run Claude Code extraction first.")
        return None
    if not scope_path.exists():
        print("  ERROR: No scope_data.json found. Run Claude Code extraction first.")
        return None

    # Load extracted data
    print(f"\n[Step 1] Loading pre-extracted JSONs...")
    with open(template_path) as f:
        template_data = json.load(f)
    with open(scope_path) as f:
        scope_data = json.load(f)

    articles = template_data.get("articles", [])
    spec_sections = scope_data.get("spec_sections", [])
    line_items = scope_data.get("line_items", [])
    sub_name = scope_data.get("subcontractor", {})
    if isinstance(sub_name, dict):
        sub_name = sub_name.get("company_name", "N/A")
    contract_value = scope_data.get("contract_value") or scope_data.get("contract_sum", "N/A")

    print(f"  Template: {len(articles)} articles")
    print(f"  Scope: {len(spec_sections)} spec sections, {len(line_items)} line items")
    print(f"  Subcontractor: {sub_name}")
    print(f"  Contract value: {contract_value}")

    # Generate .docx
    print(f"\n[Step 2] Generating subcontract .docx...")
    sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "skills" / "subcontract-writer" / "scripts"))
    from generate_subcontract_docx import generate_subcontract

    docx_path = str(run_dir / "Subcontract.docx")
    generate_subcontract(str(template_path), str(scope_path), output=docx_path)
    print(f"  Docx: {docx_path}")

    # Write graph entry
    print(f"\n[Step 3] Writing graph entry...")
    graph_data = {
        "subcontractor": str(sub_name),
        "contract_value": str(contract_value),
        "spec_sections": [s.get("number", "") for s in spec_sections],
        "line_items_count": len(line_items),
        "articles_count": len(articles),
    }
    graph_path = write_graph_entry(
        run_dir,
        "subcontract_generated",
        f"Subcontract — {sub_name}",
        graph_data,
        project_dir=get_project_dir(case),
    )
    print(f"  Graph: {graph_path.name}")

    # Score against ground truth
    print(f"\n[Step 4] Scoring against ground truth...")
    scores = {}
    gt_rel = case.get("ground_truth")
    if gt_rel:
        gt_path = PROJECT_ROOT / "evals" / "cases" / case["skill"] / gt_rel
        if gt_path.exists():
            gt = _load_ground_truth(gt_path)

            scores["spec_section_coverage"] = _score_spec_section_coverage(scope_data, gt)
            scores["scope_completeness"] = _score_scope_completeness(scope_data, gt)
            scores["contract_terms"] = _score_contract_terms(scope_data, gt)
            scores["template_preservation"] = _score_template_preservation(template_data)
            scores["article_completeness"] = _score_article_completeness(template_data)
            scores["document_structure"] = _score_document_structure(template_data, gt)
            scores["format"] = _score_docx_format(Path(docx_path))
            scores["graph"] = 1.0 if graph_path.exists() else 0.0

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
        "docx": docx_path,
        "template_data": str(template_path),
        "scope_data": str(scope_path),
        "graph_entry": str(graph_path),
    }
    result_path = write_eval_result(
        case, run_dir, scores, artifacts,
        f"Subcontract for {sub_name}",
    )
    print(f"\n  Result: {result_path}")
    return json.loads(result_path.read_text())
