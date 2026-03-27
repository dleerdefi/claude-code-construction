#!/usr/bin/env python3
"""Split a bound project manual PDF into individual spec section PDFs.

Parses the Table of Contents to identify section boundaries, then splits
the PDF into one file per specification section.

Usage:
  python split_spec_manual.py <project_manual.pdf> [--output-dir <specs/>]
  python split_spec_manual.py <project_manual.pdf> --dry-run

Output:
  specs/01 10 00 - SUMMARY.pdf
  specs/03 30 00 - CAST-IN-PLACE CONCRETE.pdf
  specs/08 71 00 - DOOR HARDWARE.pdf
  ...
  specs/spec_index.yaml
"""

import argparse
import os
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF


def parse_toc(pdf_path, max_pages=15):
    """Parse the Table of Contents to extract section → page mapping.

    Returns list of (section_number, section_title, page_number) sorted by page.
    """
    doc = fitz.open(str(pdf_path))
    entries = []

    # Strategy: In many PDFs, PyMuPDF extracts TOC entries as:
    #   "01 10 00\n"  (section number on one line)
    #   "SUMMARY\n"   (title on the next line)
    # OR as single-line: "01 10 00    SUMMARY"
    # Handle both formats.

    single_line_pattern = re.compile(
        r"(?:SECTION\s+)?(\d{2}\s+\d{2}\s+\d{2}(?:\.\d+)?)\s+([\w][\w\s,/&()\-]+)",
    )
    section_num_pattern = re.compile(
        r"^(\d{2}\s+\d{2}\s+\d{2}(?:\.\d+)?)$",
    )

    for page_idx in range(min(max_pages, len(doc))):
        page = doc[page_idx]
        text = page.get_text()
        lines = [l.strip() for l in text.split("\n")]

        i = 0
        while i < len(lines):
            line = lines[i]

            # Try single-line match first
            m = single_line_pattern.match(line)
            if m:
                sec = m.group(1).strip()
                title = m.group(2).strip()
                if len(title) > 3 and not title.replace(".", "").replace(" ", "").isdigit():
                    entries.append((sec, title, None))
                i += 1
                continue

            # Try two-line match: section number alone, title on next line
            m = section_num_pattern.match(line)
            if m and i + 1 < len(lines):
                sec = m.group(1).strip()
                next_line = lines[i + 1].strip()
                # Next line should be a title (alpha characters, not a number or header)
                if (next_line and len(next_line) > 3
                        and next_line[0].isalpha()
                        and not next_line.startswith("DIVISION")
                        and not next_line.startswith("VOLUME")
                        and not next_line.startswith("TABLE")
                        and not next_line.startswith("Grimm")):
                    entries.append((sec, next_line, None))
                    i += 2
                    continue

            i += 1

    doc.close()

    # Deduplicate by section number (keep first occurrence)
    seen = set()
    unique = []
    for sec, title, pg in entries:
        if sec not in seen:
            seen.add(sec)
            unique.append((sec, title, pg))

    return sorted(unique, key=lambda x: x[0])


def find_section_pages(pdf_path, toc_entries):
    """Find actual page numbers for each section by searching for section headers.

    Scans all pages for lines matching "SECTION XX XX XX" to get precise boundaries.
    Filters out TOC/index pages that list many section numbers but aren't actual content.
    """
    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)

    # Strategy: find section starts using multiple methods
    # Method A: "SECTION XX XX XX" headers (standard CSI format)
    # Method B: Page headers with section numbers like "05 1200 - 1" (page 1 of section)
    # Filter out TOC/index pages that list many sections

    section_pages = {}
    sections_per_page = {}

    # Pattern A: SECTION keyword — matches spaced (03 30 00), compact (033000), and mixed (03 3000)
    section_keyword = re.compile(
        r"SECTION\s+(\d{2}\s*\d{2}\s*\d{2}(?:\.\d+)?)\b",
        re.MULTILINE,
    )
    # Pattern B: Page header with section number and page count (e.g., "05 1200 - 1")
    page_header = re.compile(
        r"^(\d{2}\s+\d{2}\s*\d{2})\s*-\s*1\s*$",
        re.MULTILINE,
    )

    for page_idx in range(total_pages):
        text = doc[page_idx].get_text()

        # Count SECTION keyword occurrences (for TOC detection)
        keyword_matches = section_keyword.findall(text)
        sections_per_page[page_idx] = len(keyword_matches)

        # Method A: SECTION keyword on non-TOC pages
        if len(keyword_matches) < 5:  # Not a TOC page
            for sec_num in keyword_matches:
                sec = sec_num.strip()
                if sec not in section_pages:
                    section_pages[sec] = page_idx

        # Method B: Page header format "XX XXXX - 1" (page 1 = section start)
        for m in page_header.finditer(text):
            sec = m.group(1).strip()
            if sec not in section_pages:
                section_pages[sec] = page_idx

    doc.close()

    # Build ordered list
    toc_dict = {sec: title for sec, title, _ in toc_entries}
    ordered = sorted(section_pages.items(), key=lambda x: x[1])

    sections = []
    for i, (sec, start_page) in enumerate(ordered):
        end_page = ordered[i + 1][1] - 1 if i + 1 < len(ordered) else total_pages - 1
        page_count = end_page - start_page + 1
        if page_count <= 0:
            continue
        sections.append({
            "number": sec,
            "title": toc_dict.get(sec, sec),
            "start_page": start_page,
            "end_page": end_page,
            "page_count": page_count,
        })

    return sections


def split_pdf(pdf_path, sections, output_dir):
    """Split the PDF into individual section files."""
    doc = fitz.open(str(pdf_path))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    created_files = []

    for sec in sections:
        # Sanitize filename
        safe_title = re.sub(r'[<>:"/\\|?*]', "", sec["title"])
        safe_title = safe_title.strip()[:80]  # Limit length
        filename = f"{sec['number']} - {safe_title}.pdf"
        out_path = output_dir / filename

        # Extract pages
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=sec["start_page"], to_page=sec["end_page"])
        new_doc.save(str(out_path))
        new_doc.close()

        created_files.append({
            "number": sec["number"],
            "title": sec["title"],
            "filename": filename,
            "pages": sec["page_count"],
        })

    doc.close()
    return created_files


def write_index(created_files, output_dir, source_pdf):
    """Write a YAML index of the split spec sections."""
    import yaml

    index = {
        "source": str(source_pdf),
        "total_sections": len(created_files),
        "sections": created_files,
    }

    index_path = Path(output_dir) / "spec_index.yaml"
    with open(index_path, "w") as f:
        yaml.dump(index, f, default_flow_style=False, sort_keys=False)

    return index_path


def extract_title_from_page(pdf_path, page_idx):
    """Extract the section title from the SECTION header line on a given page."""
    doc = fitz.open(str(pdf_path))
    if page_idx >= len(doc):
        doc.close()
        return ""

    text = doc[page_idx].get_text()
    doc.close()

    # Look for: SECTION XX XX XX - TITLE or SECTION XX XX XX\nTITLE
    m = re.search(
        r"SECTION\s+\d{2}\s+\d{2}\s*\d{2}(?:\.\d+)?\s*[-\u2013\u2014]\s*(.+)",
        text,
    )
    if m:
        title = m.group(1).strip()
        # Clean up: take first line only, remove page numbers
        title = title.split("\n")[0].strip()
        if len(title) > 3:
            return title

    # Try two-line format: SECTION number on one line, title on next
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for i, line in enumerate(lines):
        if re.match(r"SECTION\s+\d{2}\s+\d{2}", line) and i + 1 < len(lines):
            candidate = lines[i + 1].strip()
            if (candidate and len(candidate) > 3
                    and candidate[0].isalpha()
                    and not candidate.startswith("PART")
                    and not candidate.startswith("SECTION")):
                return candidate

    return ""


def main():
    parser = argparse.ArgumentParser(description="Split a bound project manual into individual spec section PDFs")
    parser.add_argument("pdf", help="Path to the bound project manual PDF")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: specs/ next to PDF)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be split without writing files")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"ERROR: PDF not found: {pdf_path}")
        sys.exit(1)

    output_dir = args.output_dir or str(pdf_path.parent / "specs")

    print(f"Source: {pdf_path.name}")
    print(f"Output: {output_dir}")

    # Step 1: Find section boundaries by scanning ALL pages (primary method)
    # This works regardless of TOC location or format
    print("\n[Step 1] Scanning for SECTION headers across all pages...")
    sections = find_section_pages(pdf_path, [])
    print(f"  Sections found: {len(sections)}")

    if not sections:
        print("  ERROR: No SECTION headers found in PDF. Cannot split.")
        sys.exit(1)

    # Step 2: Enrich with TOC titles (optional, best-effort)
    print("\n[Step 2] Looking for Table of Contents to enrich titles...")
    toc = parse_toc(pdf_path, max_pages=100)  # scan more pages than default
    print(f"  TOC entries found: {len(toc)}")
    toc_dict = {sec: title for sec, title, _ in toc}

    enriched = 0
    for sec in sections:
        if sec["number"] in toc_dict:
            sec["title"] = toc_dict[sec["number"]]
            enriched += 1
    print(f"  Enriched from TOC: {enriched}/{len(sections)}")

    # Step 3: For sections still without titles, extract from page text
    missing_titles = [s for s in sections if not s.get("title") or s["title"] == s["number"]]
    if missing_titles:
        print(f"\n[Step 3] Extracting titles from page text for {len(missing_titles)} sections...")
        for sec in missing_titles:
            title = extract_title_from_page(pdf_path, sec["start_page"])
            if title:
                sec["title"] = title
        still_missing = sum(1 for s in sections if not s.get("title") or s["title"] == s["number"])
        print(f"  Still missing titles: {still_missing}")

    # Show preview
    for sec in sections[:5]:
        title = sec.get("title", sec["number"])[:50]
        print(f"    {sec['number']} - {title} (pp. {sec['start_page']+1}-{sec['end_page']+1}, {sec['page_count']} pages)")
    if len(sections) > 5:
        print(f"    ... ({len(sections) - 5} more)")

    if args.dry_run:
        print(f"\n[Dry run] Would create {len(sections)} files in {output_dir}/")
        for sec in sections:
            title = sec.get("title", sec["number"])
            safe_title = re.sub(r'[<>:"/\\|?*]', "", title).strip()[:80]
            print(f"  {sec['number']} - {safe_title}.pdf ({sec['page_count']} pages)")
        return

    # Step 4: Split
    print(f"\n[Step 4] Splitting PDF into {len(sections)} section files...")
    created = split_pdf(pdf_path, sections, output_dir)
    print(f"  Created: {len(created)} files")

    # Step 5: Write index
    print("\n[Step 5] Writing spec index...")
    try:
        index_path = write_index(created, output_dir, pdf_path)
        print(f"  Index: {index_path}")
    except ImportError:
        print("  (PyYAML not installed - index skipped)")

    # Summary
    total_pages = sum(c["pages"] for c in created)
    print(f"\n{'='*50}")
    print(f"COMPLETE: {len(created)} spec sections extracted ({total_pages} total pages)")
    print(f"Output: {output_dir}/")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
