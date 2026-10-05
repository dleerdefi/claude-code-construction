#!/usr/bin/env python3
"""Generate the small synthetic project the plugin eval cases run against.

Run with: bin/construction-python evals/plugin/_fixtures/make_fixtures.py

Writes sample-project/ next to this script:
  01 - Drawings/Architectural & Structural/Arch Set.pdf   4 sheets, title blocks,
      bookmarks (the A-201 bookmark is deliberately abbreviated; the printed
      title block is authoritative)
  02 - Specifications/Project Manual.pdf                   TOC + 2 sections with
      PART 1 SUBMITTALS articles
The folder names contain spaces and "&" on purpose: they exercise path quoting.
"""
from pathlib import Path

import fitz  # PyMuPDF

OUT = Path(__file__).resolve().parent / "sample-project"
PROJECT = "SAMPLE OFFICE RENOVATION"
FIXTURE_NOTICE = "EVAL FIXTURE - fictional document generated for a synthetic evaluation; not a real project or firm"

SHEETS = [  # number, printed title, bookmark title
    ("G-001", "COVER SHEET AND DRAWING INDEX", "COVER SHEET AND DRAWING INDEX"),
    ("A-101", "FIRST FLOOR PLAN", "FIRST FLOOR PLAN"),
    ("A-201", "SECOND FLOOR PLAN", "2ND FLR"),
    ("S-101", "FOUNDATION PLAN", "FOUNDATION PLAN"),
]

SECTIONS = [
    ("03 30 00", "CAST-IN-PLACE CONCRETE", [
        "Product Data: For each type of manufactured material and product indicated.",
        "Design Mixtures: For each concrete mixture, including admixtures.",
        "Shop Drawings: Placing drawings for reinforcement, including bar schedules.",
        "Field Quality-Control Reports: Compressive strength test results.",
    ]),
    ("08 71 00", "DOOR HARDWARE", [
        "Product Data: Manufacturer's technical data for each item of door hardware.",
        "Door Hardware Schedule: Prepared by or under supervision of the Architect's Hardware Consultant.",
        "Keying Schedule: Prepared after a keying conference with the Owner.",
        "Warranty: Sample of special warranty.",
    ]),
]


def drawing_set(path):
    doc = fitz.open()
    toc = []
    for i, (number, title, bookmark) in enumerate(SHEETS):
        page = doc.new_page(width=1224, height=792)  # 17" x 11"
        page.draw_rect(fitz.Rect(18, 18, 1206, 774), width=2)
        # some "drawing" content: a grid of rooms
        for x in range(80, 800, 120):
            page.draw_rect(fitz.Rect(x, 120, x + 110, 300), width=1)
            page.insert_text((x + 10, 210), f"ROOM {100 * (i + 1) + x // 120}", fontsize=8)
        # title block, bottom right
        tb = fitz.Rect(930, 600, 1200, 768)
        page.draw_rect(tb, width=1.5)
        page.insert_text((940, 625), PROJECT, fontsize=9)
        page.insert_text((940, 660), title, fontsize=11)
        page.insert_text((940, 700), "SHEET NUMBER", fontsize=7)
        page.insert_text((940, 745), number, fontsize=28)
        toc.append([1, f"{number} {bookmark}", i + 1])
    doc.set_toc(toc)
    path.parent.mkdir(parents=True, exist_ok=True)
    for page in doc:  # every page says what it is, in the bottom margin
        page.insert_text((12, page.rect.height - 8), FIXTURE_NOTICE, fontsize=6)
    doc.save(str(path), garbage=4, deflate=True)


def project_manual(path):
    doc = fitz.open()

    def page_with(lines):
        page = doc.new_page(width=612, height=792)  # 8.5" x 11"
        y = 72
        for text, size in lines:
            page.insert_text((72, y), text, fontsize=size)
            y += size + 8
        return page

    page_with([(PROJECT, 12), ("PROJECT MANUAL", 14), ("", 10), ("TABLE OF CONTENTS", 12)]
              + [(f"{num}  {title}", 10) for num, title, _ in SECTIONS])
    for num, title, items in SECTIONS:
        page_with([(f"SECTION {num} - {title}", 12), ("", 10), ("PART 1 - GENERAL", 11),
                   ("1.1  SUMMARY", 10), (f"A.  Section includes {title.lower()}.", 10), ("", 10),
                   ("1.2  ACTION SUBMITTALS", 10)]
                  + [(f"{chr(65 + k)}.  {item}", 9) for k, item in enumerate(items)])
        page_with([("PART 2 - PRODUCTS", 11), ("2.1  MATERIALS", 10), ("A.  As specified.", 10), ("", 10),
                   ("PART 3 - EXECUTION", 11), ("3.1  INSTALLATION", 10),
                   ("A.  Install according to manufacturer's written instructions.", 10), ("", 10),
                   (f"END OF SECTION {num}", 11)])
    path.parent.mkdir(parents=True, exist_ok=True)
    for page in doc:  # every page says what it is, in the bottom margin
        page.insert_text((12, page.rect.height - 8), FIXTURE_NOTICE, fontsize=6)
    doc.save(str(path), garbage=4, deflate=True)


if __name__ == "__main__":
    drawing_set(OUT / "01 - Drawings" / "Architectural & Structural" / "Arch Set.pdf")
    project_manual(OUT / "02 - Specifications" / "Project Manual.pdf")
    (OUT / "CLAUDE.md").write_text(f"# {PROJECT}\n\nSample construction project used by the plugin evals.\n")
    for f in sorted(OUT.rglob("*")):
        if f.is_file():
            print(f"{f.relative_to(OUT)}  ({f.stat().st_size // 1024} KB)")
