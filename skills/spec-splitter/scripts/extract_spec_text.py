#!/usr/bin/env python3
"""Batch extract text from spec section PDFs using pdfplumber.

RIGID script — called by spec-splitter and submittal-log-generator.
Extracts text from each spec section PDF, assesses quality, and writes
persistent .txt files with a manifest for downstream skills.

Usage:
    construction-python extract_spec_text.py --specs-dir path/to/sections
    construction-python extract_spec_text.py --specs-dir path/to/sections --output-dir .construction/spec_text
    construction-python extract_spec_text.py --specs-dir path/to/sections --force
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pdfplumber


# ── Quality Assessment ────────────────────────────────────────────

# Known short tokens that are valid (not evidence of split-word artifacts)
VALID_SHORT_TOKENS = {
    'a', 'i', 'or', 'an', 'as', 'at', 'be', 'by', 'do', 'if', 'in', 'is',
    'it', 'no', 'of', 'on', 'so', 'to', 'up', 'we', 'gc', 'cm', 'pe', 'qa',
    'qc', 'sf', 'lf', 'cy', 'ea', 'ls', 'ga', 'a.', 'b.', 'c.', 'd.', 'e.',
    'f.', 'g.', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '&',
}

# Common Unicode chars that are legitimate in construction specs
VALID_NON_ASCII = set('°²³±×÷–—\u2018\u2019\u201c\u201d\u2022\u2026½¼¾')


def assess_quality(text, pages_text):
    """Assess extraction quality. Returns (rating, failure_modes)."""
    if not text or len(text.strip()) < 100:
        return "POOR", ["Empty or near-empty extraction"]

    words = text.split()
    total_words = len(words)
    if total_words == 0:
        return "POOR", ["No words extracted"]

    failures = []

    # Split words: >10% of tokens are ≤2 chars (excluding known valid short tokens)
    short_tokens = sum(
        1 for w in words
        if len(w) <= 2 and w.lower() not in VALID_SHORT_TOKENS
    )
    if short_tokens / total_words > 0.10:
        failures.append(f"Split words: {short_tokens}/{total_words} short tokens")

    # Garbled characters: >5% non-ASCII (excluding legitimate Unicode)
    non_ascii = sum(1 for c in text if ord(c) > 127 and c not in VALID_NON_ASCII)
    if len(text) > 0 and non_ascii / len(text) > 0.05:
        failures.append(f"Garbled characters: {non_ascii} non-ASCII chars")

    # Missing pages: >30% of pages have <100 chars
    empty_pages = sum(1 for pt in pages_text if len(pt.strip()) < 100)
    if pages_text and empty_pages / len(pages_text) > 0.3:
        failures.append(f"Missing text: {empty_pages}/{len(pages_text)} pages near-empty")

    if not failures:
        return "GOOD", []

    # Severity: POOR if >50% pages empty, DEGRADED otherwise
    if any("Missing text" in f for f in failures) and empty_pages / max(len(pages_text), 1) > 0.5:
        return "POOR", failures
    if len(failures) >= 2:
        return "DEGRADED", failures
    return "DEGRADED" if "Split words" in str(failures) else "GOOD", failures


# ── Extraction ────────────────────────────────────────────────────

def extract_section(pdf_path):
    """Extract text from a spec section PDF.

    Returns (full_text, pages_text, quality, failures).
    """
    pages_text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages_text.append(text)
    except Exception as e:
        return None, [], "POOR", [f"PDF error: {e}"]

    full_text = "\n\n".join(pages_text)
    quality, failures = assess_quality(full_text, pages_text)
    return full_text, pages_text, quality, failures


# ── Main ──────────────────────────────────────────────────────────

def run(specs_dir, output_dir, force=False):
    """Extract text from all spec PDFs in specs_dir."""
    specs_dir = Path(specs_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(specs_dir.glob("*.pdf"))
    if not pdfs:
        print(f"WARNING: No PDFs found in {specs_dir}")
        return

    # Load existing manifest for incremental mode
    manifest_path = output_dir / "manifest.json"
    manifest = {}
    if manifest_path.exists():
        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)
        except (json.JSONDecodeError, OSError):
            manifest = {}

    results = {"good": 0, "degraded": 0, "poor": 0, "skipped": 0, "total": len(pdfs)}

    for pdf_path in pdfs:
        # Parse section number from filename
        match = re.match(r'^(\d[\d .]+\d)', pdf_path.stem)
        if not match:
            print(f"  SKIP: {pdf_path.name} (no section number)")
            results["skipped"] += 1
            continue

        section_num = match.group(1).strip()
        section_key = section_num.replace(" ", "_").replace(".", "_")
        title = pdf_path.stem[len(match.group(0)):].strip(" -")

        # Incremental: skip if already extracted (unless --force)
        out_file = output_dir / f"{section_key}.txt"
        if out_file.exists() and not force:
            results["skipped"] += 1
            continue

        print(f"  {section_num} - {title}...", end=" ", flush=True)

        full_text, pages_text, quality, failures = extract_section(pdf_path)

        if full_text is not None:
            out_file.write_text(full_text, encoding="utf-8")

        manifest[section_key] = {
            "spec_title": title,
            "extraction_method": "pdfplumber",
            "quality_rating": quality,
            "repair_attempted": False,
            "pages_extracted": len(pages_text),
            "character_count": len(full_text) if full_text else 0,
            "failure_modes": failures,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
        }

        results[quality.lower()] += 1
        print(f"{quality} ({len(pages_text)} pages, {len(full_text) if full_text else 0} chars)")

    # Write manifest (merge into existing)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    extracted = results["good"] + results["degraded"] + results["poor"]
    print(f"\nOK: {extracted} sections extracted, {results['skipped']} skipped")
    print(f"  GOOD: {results['good']}  DEGRADED: {results['degraded']}  POOR: {results['poor']}")
    print(f"  Text: {output_dir}/")
    print(f"  Manifest: {manifest_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract text from spec section PDFs with quality assessment"
    )
    parser.add_argument(
        "--specs-dir", required=True,
        help="Directory containing split spec section PDFs"
    )
    parser.add_argument(
        "--output-dir", default=".construction/spec_text",
        help="Output directory for .txt files and manifest.json (default: .construction/spec_text)"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-extract sections that already have .txt files"
    )
    args = parser.parse_args()

    if not Path(args.specs_dir).is_dir():
        print(f"ERROR: Specs directory not found: {args.specs_dir}")
        sys.exit(1)

    run(args.specs_dir, args.output_dir, force=args.force)
