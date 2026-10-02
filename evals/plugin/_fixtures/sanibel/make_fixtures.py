#!/usr/bin/env python3
"""Derive small eval fixtures from the downloaded Sanibel Fire and Rescue Station 172 documents.

Run with: bin/construction-python evals/plugin/_fixtures/sanibel/make_fixtures.py [--list]

Reads the PDFs users download into evals/test_docs/SANIBEL FIRE AND RESCUE STATION 172/
(see docs/RUNNING_EVALS.md) and writes to generated/ next to this script (gitignored):

  drawings/<Mechanical set>.pdf                      the 8-sheet mechanical set, as downloaded
  drawings/A500 - <title>.pdf, A101 - ..., G010 - ... single sheets from the architectural set
  specs/Project Manual - Division 09 Flooring.pdf    cover, title page and 9 sections
  specs/Project Manual - Three Sections.pdf          cover, title page and 3 sections
  specs/sections/<number> - <TITLE>.pdf              the flooring sections, already split
  manifest.json                                      what was written, with page ranges

The real-document eval cases copy from here (prepare-real-workspace.sh). Nothing
here is hand-written: every file is pages of the originals.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parents[3]
SOURCE = PLUGIN / "evals" / "test_docs" / "SANIBEL FIRE AND RESCUE STATION 172"
OUT = HERE / "generated"

SHEETS = ["A500", "A101", "G010"]
MANUALS = {
    "Project Manual - Division 09 Flooring.pdf": ["01 10 00", "01 23 00", "01 33 00", "09 30 00", "09 65 13",
                                                   "09 65 40", "09 65 67", "09 67 00", "09 67 10"],
    "Project Manual - Three Sections.pdf": ["01 33 00", "09 30 00", "09 65 40"],
}
SPLIT_SECTIONS = ["09 30 00", "09 65 13", "09 65 40", "09 65 67", "09 67 00", "09 67 10"]
FRONT_MATTER_PAGES = 2  # cover and title page of Volume 1

SHEET_NO = re.compile(r"^[A-Z]{1,3}\d{2,4}(-[A-Z])?$")
FOOTER = re.compile(r"(\d{2} \d{2} \d{2})\s*[-–]\s*\d+")
TOC_NUMBER = re.compile(r"^\d{2} \d{2} \d{2}$")


def source_files() -> dict[str, Path]:
    d = SOURCE / "01 - Drawings"
    s = SOURCE / "02 - Specifications"
    files = {
        "arch": next(iter(d.glob("*Architectural*.pdf")), None),
        "mech": next(iter(d.glob("*Mechanical*.pdf")), None),
        "vol1": next(iter(s.glob("*VOL-1.pdf")), None),
    }
    missing = [k for k, v in files.items() if v is None]
    if missing:
        sys.exit(f"missing source PDFs ({', '.join(missing)}) under {SOURCE}. Download them first: docs/RUNNING_EVALS.md")
    return files


def sheet_numbers(doc: fitz.Document) -> dict[str, int]:
    """Sheet number -> 0-based page, from the largest sheet-number-like text on each page."""
    out = {}
    for i, page in enumerate(doc):
        best = ("", 0.0)
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    t = s["text"].strip()
                    if SHEET_NO.match(t) and s["size"] > best[1]:
                        best = (t, s["size"])
        if best[0] and best[0] not in out:
            out[best[0]] = i
    return out


def sheet_title(page: fitz.Page, number: str) -> str:
    """The sheet title: the largest text block that is not the number or the project name."""
    spans = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                t = s["text"].strip()
                if t and t != number and "SANIBEL" not in t.upper() and "STATION" not in t.upper():
                    spans.append((s["size"], t))
    # Title block text is ~23.6pt; drawing titles are ~24.9pt. Prefer the 23-24pt band.
    band = [t for sz, t in spans if 23.0 <= sz <= 24.0]
    return " ".join(band[:2]) if band else max(spans)[1]


def toc_titles(doc: fitz.Document) -> dict[str, str]:
    titles, lines = {}, []
    for i in range(2, 12):
        lines += [l.strip() for l in doc[i].get_text().splitlines() if l.strip()]
    for i, l in enumerate(lines):
        if TOC_NUMBER.match(l) and i + 1 < len(lines) and l not in titles:
            titles[l] = lines[i + 1]
    return titles


def section_pages(doc: fitz.Document) -> dict[str, list[int]]:
    pages: dict[str, list[int]] = {}
    for i, page in enumerate(doc):
        m = FOOTER.search(page.get_text()[:400])
        if m:
            pages.setdefault(m.group(1), []).append(i)
    return pages


def write_pages(src: fitz.Document, page_lists: list[list[int]], dest: Path) -> int:
    out = fitz.open()
    n = 0
    for pages in page_lists:
        for p in pages:
            out.insert_pdf(src, from_page=p, to_page=p)
            n += 1
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(str(dest), garbage=4, deflate=True)
    return n


def safe(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "-", name).strip()


def main(list_only: bool) -> None:
    files = source_files()
    arch, mech, vol1 = fitz.open(files["arch"]), files["mech"], fitz.open(files["vol1"])
    numbers = sheet_numbers(arch)
    titles = toc_titles(vol1)
    sections = section_pages(vol1)
    manifest = {"source": str(SOURCE), "drawings": {}, "specs": {}, "sections": {}}

    if list_only:
        print("sheets:", {n: numbers.get(n) for n in SHEETS})
        for s in sorted(set(sum(MANUALS.values(), [])) | set(SPLIT_SECTIONS)):
            p = sections.get(s, [])
            print(f"  {s} {titles.get(s, '?')}: pages {p[0] + 1 if p else '?'}-{p[-1] + 1 if p else '?'} ({len(p)})")
        return

    OUT.mkdir(parents=True, exist_ok=True)
    # drawings
    mech_dest = OUT / "drawings" / mech.name
    mech_dest.parent.mkdir(parents=True, exist_ok=True)
    mech_dest.write_bytes(mech.read_bytes())
    manifest["drawings"][mech.name] = {"pages": len(fitz.open(mech)), "from": "Mechanical set, unchanged"}
    for n in SHEETS:
        if n not in numbers:
            sys.exit(f"sheet {n} not found in the architectural set")
        title = sheet_title(arch[numbers[n]], n)
        name = safe(f"{n} - {title}.pdf")
        write_pages(arch, [[numbers[n]]], OUT / "drawings" / name)
        manifest["drawings"][name] = {"pages": 1, "from": f"architectural set page {numbers[n] + 1}"}
    # manuals
    for name, wanted in MANUALS.items():
        missing = [s for s in wanted if s not in sections]
        if missing:
            sys.exit(f"sections not found in Volume 1: {missing}")
        lists = [list(range(FRONT_MATTER_PAGES))] + [sections[s] for s in wanted]
        n = write_pages(vol1, lists, OUT / "specs" / name)
        manifest["specs"][name] = {"pages": n, "sections": {s: {"title": titles.get(s, ""), "source_pages": [sections[s][0] + 1, sections[s][-1] + 1]} for s in wanted}}
    for s in SPLIT_SECTIONS:
        name = safe(f"{s} - {titles.get(s, 'SECTION')}.pdf")
        n = write_pages(vol1, [sections[s]], OUT / "specs" / "sections" / name)
        manifest["sections"][s] = {"file": name, "title": titles.get(s, ""), "pages": n}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            print(f"{p.relative_to(OUT)}  ({p.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main(list_only="--list" in sys.argv)
