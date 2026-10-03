#!/usr/bin/env python3
"""Find pages in a large PDF without reading every page.

Indexes the text layer once, then answers "which pages cover this element?" for
submittal packages, equipment brochures and spec books.

    find_pages.py index --pdf "<file.pdf>" --output "<dir>/pages_0.json"
    find_pages.py find  --index "<dir>/pages_0.json" --terms "EQ-14" "walk-in cooler" [--top 10]
    find_pages.py map   --index "<dir>/pages_0.json" --elements "<dir>/element_terms.json" --output "<dir>/page_map_0.json"

`map` reads [{"id": "EQ-14", "terms": ["EQ-14", "Item 14", "walk-in cooler"]}, ...] and returns,
per element, the pages where it is a heading (where its tab or cut sheet starts), the
pages that follow it until the next element's heading, and other pages that mention it.
Pages that look like a table of contents are reported, not assigned. Pages with no
text layer are listed as image-only: rasterize those to read them.
"""

import argparse
import json
import re
import sys
from pathlib import Path

TAG_PATTERNS = [
    r"\b(?:ITEM|EQ|EQUIP|MARK|TAG)\.?\s*(?:NO\.?|#)?\s*-?\s*\d{1,4}[A-Z]?\b",
    r"\b[A-Z]{1,4}-\d{1,4}[A-Z]?\b",
]
MIN_TEXT_CHARS = 25          # fewer characters than this and the page has no usable text layer
TOC_ELEMENT_COUNT = 5        # a page mentioning this many different elements is treated as an index


def open_pdf(path):
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    return fitz.open(path)


def page_entry(page, number):
    data = page.get_text("dict")
    height = page.rect.height or 792.0
    lines = []
    for block in data.get("blocks", []):
        for line in block.get("lines", []):
            text = " ".join(s.get("text", "") for s in line.get("spans", [])).strip()
            if len(text) < 2:
                continue
            size = max((s.get("size", 0) for s in line.get("spans", [])), default=0)
            y = line.get("bbox", [0, 0, 0, 0])[1]
            lines.append((size, y, text))
    text = " ".join(t for _, _, t in sorted(lines, key=lambda l: l[1]))
    text = re.sub(r"\s+", " ", text).strip()
    top = [l for l in lines if l[1] < height * 0.35] or lines
    top.sort(key=lambda l: (-round(l[0], 1), l[1]))
    title_size = round(top[0][0], 1) if top else 0
    headings = []
    for _, _, t in top:
        if t not in headings:
            headings.append(t)
        if len(headings) == 3:
            break
    tags = sorted({re.sub(r"\s+", " ", m.group(0)).upper()
                   for pat in TAG_PATTERNS for m in re.finditer(pat, text, re.I)})
    return {
        "page": number,
        "chars": len(text),
        "image_only": len(text) < MIN_TEXT_CHARS,
        "has_images": bool(page.get_images()),
        "title": headings[0] if headings else "",
        "title_size": title_size,
        "headings": headings,
        "tags": tags[:40],
        "text": text,
    }


def build_index(pdf):
    doc = open_pdf(pdf)
    pages = [page_entry(doc[i], i + 1) for i in range(len(doc))]
    doc.close()
    return {"file": str(pdf), "pages": len(pages),
            "image_only_pages": [p["page"] for p in pages if p["image_only"]],
            "entries": pages}


def term_regex(term):
    """Match a term as a whole token; 'EQ-14' also matches 'EQ 14' and 'EQ14', never 'EQ-140'."""
    t = term.strip()
    parts = re.split(r"[\s\-_.#]+", t)
    body = r"[\s\-_.#]*".join(re.escape(p) for p in parts if p)
    return re.compile(rf"(?<![A-Za-z0-9]){body}(?![A-Za-z0-9])", re.I)


def score_page(entry, regexes):
    head = " | ".join(entry["headings"])
    score, hits = 0, []
    for term, rx in regexes:
        n_text = len(rx.findall(entry["text"]))
        n_head = len(rx.findall(head))
        if n_text or n_head:
            hits.append(term)
            score += min(n_text, 3) + 5 * min(n_head, 1)
    return score, hits, bool(head) and any(rx.search(head) for _, rx in regexes)


def snippet(text, regexes, width=90):
    for _, rx in regexes:
        m = rx.search(text)
        if m:
            a = max(0, m.start() - width // 2)
            return ("…" if a else "") + text[a:a + width].strip() + "…"
    return text[:width] + ("…" if len(text) > width else "")


def find(index, terms, top=10):
    regexes = [(t, term_regex(t)) for t in terms if t.strip()]
    results = []
    for e in index["entries"]:
        score, hits, in_head = score_page(e, regexes)
        if score:
            results.append({"page": e["page"], "score": score, "heading_hit": in_head, "terms": hits,
                            "title": e["title"], "snippet": snippet(e["text"], regexes)})
    results.sort(key=lambda r: (-r["score"], r["page"]))
    return results[:top]


def map_elements(index, elements):
    compiled = [(el["id"], [(t, term_regex(t)) for t in el.get("terms", []) if t.strip()]) for el in elements]
    per_page = {}
    for e in index["entries"]:
        per_page[e["page"]] = {eid: score_page(e, rx) for eid, rx in compiled}
    toc = [p for p, scores in per_page.items()
           if sum(1 for s in scores.values() if s[0]) >= TOC_ELEMENT_COUNT]
    # A heading page starts an element's section; following pages with no other heading continue it.
    # A tab page (title set much larger than usual) that matches no element ends the section: it is
    # something the element list doesn't have, and its pages are reported as unassigned.
    sizes = sorted(e.get("title_size", 0) for e in index["entries"] if not e["image_only"])
    median = sizes[len(sizes) // 2] if sizes else 0
    tab_size = max(median * 1.4, median + 4) if median else float("inf")
    starts, breaks = {}, set()
    for e in index["entries"]:
        p = e["page"]
        if p in toc:
            continue
        heads = [(s[0], eid) for eid, s in per_page[p].items() if s[2]]
        if heads:
            starts[p] = max(heads)[1]
        elif e.get("title_size", 0) >= tab_size:
            breaks.add(p)
    owner, current = {}, None
    image_only = set(index.get("image_only_pages", []))
    for p in sorted(per_page):
        if p in toc:
            current = None
            continue
        if p in starts:
            current = starts[p]
        elif p in breaks:
            current = None
        if current:
            owner[p] = current
    out = []
    for eid, _ in compiled:
        heading = sorted(p for p, o in starts.items() if o == eid)
        section = sorted(p for p, o in owner.items() if o == eid)
        mentions = sorted(p for p, s in per_page.items()
                          if s[eid][0] and p not in section and p not in toc)
        out.append({"id": eid, "heading_pages": heading, "section_pages": section,
                    "image_only_in_section": sorted(set(section) & image_only),
                    "other_mentions": mentions,
                    "status": "found" if heading else ("mentioned" if mentions or section else "not_found")})
    assigned = set(owner)
    unassigned = [p for p in sorted(per_page) if p not in assigned and p not in toc]
    return {"file": index.get("file"), "pages": index.get("pages"), "toc_pages": sorted(toc),
            "unmatched_tabs": [{"page": p, "title": next(e["title"] for e in index["entries"] if e["page"] == p)}
                               for p in sorted(breaks)],
            "unassigned_pages": unassigned, "image_only_pages": sorted(image_only), "elements": out}


def ranges(pages):
    """[1,2,3,7,9,10] -> '1-3, 7, 9-10'"""
    out, start, prev = [], None, None
    for p in pages:
        if start is None:
            start = prev = p
        elif p == prev + 1:
            prev = p
        else:
            out.append(f"{start}-{prev}" if prev != start else str(start))
            start = prev = p
    if start is not None:
        out.append(f"{start}-{prev}" if prev != start else str(start))
    return ", ".join(out)


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    a = sub.add_parser("index", help="Index a PDF's text layer once")
    a.add_argument("--pdf", required=True)
    a.add_argument("--output", required=True)
    b = sub.add_parser("find", help="Pages matching search terms, best first")
    b.add_argument("--index", required=True)
    b.add_argument("--terms", nargs="+", required=True)
    b.add_argument("--top", type=int, default=10)
    c = sub.add_parser("map", help="Pages per element, from a list of element ids and search terms")
    c.add_argument("--index", required=True)
    c.add_argument("--elements", required=True, help='JSON: [{"id": "EQ-14", "terms": ["EQ-14", "walk-in cooler"]}]')
    c.add_argument("--output", required=True)
    args = ap.parse_args()

    if args.command == "index":
        idx = build_index(args.pdf)
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")
        n_img = len(idx["image_only_pages"])
        print(f"Indexed {idx['pages']} pages → {out}")
        if n_img:
            print(f"{n_img} page(s) have no text layer and need rasterizing to read: {ranges(idx['image_only_pages'])}")
        return 0

    idx = json.loads(Path(args.index).read_text(encoding="utf-8"))
    if args.command == "find":
        for r in find(idx, args.terms, args.top):
            flag = " [heading]" if r["heading_hit"] else ""
            print(f"p{r['page']:<5} score {r['score']:<3}{flag} {r['title'][:60]!r} — {r['snippet']}")
        if idx.get("image_only_pages"):
            print(f"(not searchable, image-only: {ranges(idx['image_only_pages'])})")
        return 0

    elements = json.loads(Path(args.elements).read_text(encoding="utf-8"))
    result = map_elements(idx, elements)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    for el in result["elements"]:
        where = ranges(el["section_pages"]) or "—"
        extra = f"; also mentioned p{ranges(el['other_mentions'])}" if el["other_mentions"] else ""
        img = f"; image-only p{ranges(el['image_only_in_section'])}" if el["image_only_in_section"] else ""
        print(f"{el['id']:<14} {el['status']:<10} pages {where}{extra}{img}")
    if result["toc_pages"]:
        print(f"Index or contents pages (not assigned): {ranges(result['toc_pages'])}")
    for tab in result["unmatched_tabs"]:
        print(f"Tab on p{tab['page']} matches no element: {tab['title']!r} (an extra item, or a missing search term)")
    if result["unassigned_pages"]:
        print(f"Pages matching no element (cover, transmittal, extras?): {ranges(result['unassigned_pages'])}")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
