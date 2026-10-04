#!/usr/bin/env python3
"""Split a bound drawing set PDF into individual page PDFs.

Each page becomes its own PDF named by page number. Sheet number and title
identification is delegated to Claude Code vision (the SKILL.md instructs
Claude to rasterize title blocks and read them).

Usage:
  python split_drawing_set.py <drawings.pdf> [--output-dir <sheets/>]
  python split_drawing_set.py <drawings.pdf> --dry-run

Output:
  sheets/page_001.pdf
  sheets/page_002.pdf
  ...
  sheets/sheet_index.yaml
"""

import argparse
import sys
from pathlib import Path

import fitz  # PyMuPDF


def _same_as_source(src, new, first_page):
    """True if every page of `new` renders and reads like its source page."""
    for i, page in enumerate(new):
        orig = src[first_page + i]
        if sorted(w[4] for w in orig.get_text("words")) != sorted(w[4] for w in page.get_text("words")):
            return False
        a, b = orig.get_pixmap(dpi=30), page.get_pixmap(dpi=30)
        if (a.width, a.height, a.n) != (b.width, b.height, b.n):
            return False
        if a.samples != b.samples:
            differing = sum(1 for x, y in zip(a.samples, b.samples) if abs(x - y) > 32)
            if differing > len(a.samples) * 0.001:
                return False
    return True


def save_pages(src, first_page, last_page, out_path, clean=True):
    """Write pages first_page..last_page of `src` to out_path, as small as possible.

    insert_pdf copies each page's resource dictionary, and bound sets often
    share one dictionary listing every sheet's fonts and images, so each split
    file came out nearly as large as the whole set. clean_contents(sanitize=True)
    drops resources the page never uses. It rewrites the page's content stream,
    so cleaned pages are checked against the source (low-res render and words)
    and the uncleaned pages are kept if anything differs. Saving with
    garbage=4/deflate is lossless. Returns True if the cleaned pages were kept.
    """
    def extract(do_clean):
        new = fitz.open()
        new.insert_pdf(src, from_page=first_page, to_page=last_page)
        if do_clean:
            for page in new:
                page.clean_contents(sanitize=True)
        return new

    new, cleaned = extract(clean), clean
    if clean and not _same_as_source(src, new, first_page):
        new.close()
        new, cleaned = extract(False), False
        print(f"  NOTE: kept {Path(out_path).name} uncleaned (cleaned copy did not match the source)")
    new.save(str(out_path), garbage=4, deflate=True)
    new.close()
    return cleaned


def split_pages(pdf_path, output_dir, dry_run=False, clean=True):
    """Split PDF into one file per page."""
    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)
    output_dir = Path(output_dir)

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    sheets = []

    for page_idx in range(total_pages):
        page = doc[page_idx]
        rect = page.rect
        filename = f"page_{page_idx + 1:03d}.pdf"

        info = {
            "filename": filename,
            "page_index": page_idx,
            "page_size": f"{rect.width:.0f}x{rect.height:.0f}",
            "page_size_inches": f"{rect.width/72:.1f}x{rect.height/72:.1f}",
        }
        sheets.append(info)

        if not dry_run:
            out_path = output_dir / filename
            save_pages(doc, page_idx, page_idx, out_path, clean=clean)

        print(f"  {page_idx + 1:3d}/{total_pages}: {filename}")

    doc.close()
    return sheets


def write_index(sheets, output_dir, source_pdf):
    """Write/merge a YAML index of split sheets.

    Merges new entries into an existing index if one exists, keyed by
    filename. Supports multi-set projects where architectural, MEP, etc.
    are split separately — all pages end up in a single combined index.
    """
    import yaml

    index_path = Path(output_dir) / "sheet_index.yaml"

    # Load existing index if present
    existing = {}
    if index_path.exists():
        try:
            with open(index_path) as f:
                existing = yaml.safe_load(f) or {}
        except (yaml.YAMLError, OSError):
            existing = {}

    # Merge sources list (track all source PDFs)
    sources = existing.get("sources", [])
    # Migrate legacy single-source format
    if not sources and "source" in existing:
        sources.append(existing["source"])
    source_str = str(source_pdf)
    if source_str not in sources:
        sources.append(source_str)

    # Merge pages by filename (new entries win on conflict)
    existing_pages = {p["filename"]: p for p in existing.get("pages", [])}
    for s in sheets:
        entry = {
            "filename": s["filename"],
            "page_index": s["page_index"],
            "page_size": s["page_size"],
            "source_pdf": source_str,
            "sheet_number": "needs_identification",
            "title": "needs_identification",
        }
        existing_pages[s["filename"]] = entry

    merged_pages = sorted(existing_pages.values(), key=lambda p: p["filename"])

    index = {
        "sources": sources,
        "total_pages": len(merged_pages),
        "note": "Sheet numbers and titles are identified from the title blocks by the sheet-splitter skill (vision)",
        "pages": merged_pages,
    }

    with open(index_path, "w") as f:
        yaml.dump(index, f, default_flow_style=False, sort_keys=False)
    return index_path


def main():
    parser = argparse.ArgumentParser(description="Split a bound drawing set into individual page PDFs")
    parser.add_argument("pdf", help="Path to the bound drawing set PDF")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: sheets/ next to PDF)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be split without writing files")
    parser.add_argument("--no-clean", action="store_true", help="Skip removing unused resources from each page (larger files)")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"ERROR: PDF not found: {pdf_path}")
        sys.exit(1)

    output_dir = args.output_dir or str(pdf_path.parent / "sheets")

    doc = fitz.open(str(pdf_path))
    total = len(doc)
    page_size = f"{doc[0].rect.width/72:.1f}x{doc[0].rect.height/72:.1f} in" if total > 0 else "unknown"
    doc.close()

    print(f"Source: {pdf_path.name}")
    print(f"Pages: {total} ({page_size})")
    print(f"Output: {output_dir}")

    print(f"\n{'='*50}")
    sheets = split_pages(pdf_path, output_dir, dry_run=args.dry_run, clean=not args.no_clean)

    if not args.dry_run:
        try:
            index_path = write_index(sheets, output_dir, pdf_path)
            print(f"\nIndex: {index_path}")
        except ImportError:
            print("\n(PyYAML not installed - index skipped)")

    print(f"\n{'='*50}")
    print(f"COMPLETE: {len(sheets)} pages split")
    print(f"Next: identify each sheet number and title from its title block and rename the files")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
