#!/usr/bin/env python3
"""Dump the text layer of a PDF, page by page, with a per-page quality verdict.

Usage:
    pdf_text.py "<file.pdf>"                       every page
    pdf_text.py "<file.pdf>" --pages 1-3,7          a page selection (1-based)
    pdf_text.py "<file.pdf>" --output "<dir>/bid.txt"
    pdf_text.py "<file.pdf>" --summary              verdicts only, no text

Each page is headed by "=== page N/M: TEXT (chars)" or "=== page N/M: VISION (chars)".
VISION means the page holds fewer than --min-chars characters of text (default 50)
and must be rasterized and read with vision; a scanned bid or an image-only sheet
shows VISION on every page. The verdicts are what the skills' "text first, vision
if the text is thin" rule is decided on.
"""

import argparse
import sys


def parse_pages(spec, total):
    """"1-3,7" -> [1, 2, 3, 7], clipped to the document."""
    if not spec:
        return list(range(1, total + 1))
    pages = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            pages.extend(range(int(a), int(b) + 1))
        elif part:
            pages.append(int(part))
    return [p for p in pages if 1 <= p <= total]


def page_texts(pdf_path, pages):
    """(page number, text) for each requested page; pymupdf first, pdfplumber if it is missing."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        total = len(doc)
        selected = parse_pages(pages, total)
        out = [(n, doc[n - 1].get_text() or "") for n in selected]
        doc.close()
        return total, out
    except ImportError:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            total = len(pdf.pages)
            selected = parse_pages(pages, total)
            return total, [(n, pdf.pages[n - 1].extract_text() or "") for n in selected]


def main():
    parser = argparse.ArgumentParser(description="Dump a PDF's text layer page by page")
    parser.add_argument("pdf", help="Path to PDF")
    parser.add_argument("--pages", help="Pages to dump, 1-based, e.g. 1-3,7 (default: all)")
    parser.add_argument("--min-chars", type=int, default=50,
                        help="Below this many characters a page is marked VISION (default 50)")
    parser.add_argument("--output", "-o", help="Write to this file instead of stdout")
    parser.add_argument("--summary", action="store_true", help="Print the per-page verdicts only")
    args = parser.parse_args()

    try:
        total, texts = page_texts(args.pdf, args.pages)
    except Exception as e:  # missing file, encrypted PDF, no text library
        print(f"ERROR: {e}")
        sys.exit(1)

    lines = []
    vision_pages = []
    for n, text in texts:
        chars = len(text.strip())
        verdict = "TEXT" if chars >= args.min_chars else "VISION"
        if verdict == "VISION":
            vision_pages.append(n)
        lines.append(f"=== page {n}/{total}: {verdict} ({chars} chars)")
        if not args.summary:
            lines.append(text.rstrip())
            lines.append("")
    footer = (f"{len(texts)} page(s); {len(texts) - len(vision_pages)} TEXT, {len(vision_pages)} VISION"
              + (f" (rasterize pages {','.join(map(str, vision_pages))})" if vision_pages else ""))
    lines.append(footer)

    body = "\n".join(lines)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(body + "\n")
        print(f"OK: {args.output} — {footer}")
    else:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(body)


if __name__ == "__main__":
    main()
