#!/usr/bin/env python3
"""Generate the submittal-review eval project: a science lab with casework drawings,
the casework spec section, and a casework shop drawing submittal with planted defects.

Run with: bin/construction-python evals/plugin/_fixtures/make_submittal_fixture.py

Writes submittal-project/ next to this script, already prepared the way project-setup,
sheet-splitter and spec-splitter leave a project (split sheets with an index, spec text
extracted), so the eval exercises the review itself. The project's .construction/ folder
is written as dot-construction/ because the repository ignores .construction/;
the case's setup.sh renames it after copying.

Planted defects (the ground truth the graders check):
  D1  Elevation 1: sink cutout sized for ACME LS-1812; the plumbing fixture schedule
      (P-601) calls for S-1 = ACME LS-2416.
  D2  Elevation 2: accessible student station submitted at 36 in on a drawer base
      cabinet; A-501 elevation 2 calls for 34 in with open knee space.
  D3  Elevation 3: wall-hung counter shows "supports by others"; A-521 detail 5 calls
      for concealed steel brackets furnished by casework, installed by the framer
      before gypsum board (route to framing before close-in).
  D4  Elevation 4 (fume hood base, acid storage) is in the drawings but not submitted.
"""
from pathlib import Path

import pymupdf as fitz  # PyMuPDF
import yaml

HERE = Path(__file__).resolve().parent
OUT = HERE / "submittal-project"
PROJECT = "SAMPLE SCHOOL RENOVATION"
SPEC = "12 35 53"
SPEC_TITLE = "LABORATORY CASEWORK"
SUBMITTAL = "12 35 53-001 R0 Laboratory Casework Shop Drawings.pdf"

SHEETS = {
    "A-501": ("INTERIOR ELEVATIONS - SCIENCE LAB 104", [
        ("1", "NORTH WALL - SINK WALL", [
            "BASE CABINETS B-1, SINK BASE SB-1",
            "EPOXY RESIN TOP AT 36\" AFF",
            "SINK S-1 - SEE PLUMBING FIXTURE SCHEDULE P-601",
            "SEE 2/A-521 FOR SINK SECTION",
        ]),
        ("2", "WEST WALL - ACCESSIBLE STUDENT STATION", [
            "ACCESSIBLE WORK SURFACE AT 34\" AFF",
            "OPEN KNEE SPACE BELOW - NO BASE CABINET",
            "CASEWORK SCHEDULE TYPE AW-1",
        ]),
        ("3", "EAST WALL - WALL-HUNG COUNTER", [
            "EPOXY TOP AT 36\" AFF ON CONCEALED STEEL BRACKETS",
            "BRACKETS AT 48\" O.C. MAX - SEE 5/A-521",
            "NO BASE CABINETS - OPEN BELOW",
        ]),
        ("4", "SOUTH WALL - FUME HOOD BASE", [
            "FUME HOOD FH-1 (BY 11 53 13) ON ACID STORAGE BASE AB-1",
            "AB-1 VENTED TO HOOD EXHAUST",
            "TOP AT 36\" AFF",
        ]),
    ]),
    "A-521": ("CASEWORK DETAILS", [
        ("2", "SINK SECTION", [
            "UNDERMOUNT SINK S-1 IN EPOXY RESIN TOP",
            "CUTOUT PER SINK MANUFACTURER TEMPLATE FOR SCHEDULED MODEL",
        ]),
        ("5", "CONCEALED IN-WALL COUNTER BRACKET", [
            "STEEL BRACKET FURNISHED BY CASEWORK MANUFACTURER",
            "INSTALLED BY FRAMING CONTRACTOR BEFORE GYPSUM BOARD",
            "16 GA STEEL BACKING PLATE BLK-2 BETWEEN STUDS",
            "BRACKET CAPACITY 300 LB EACH",
        ]),
    ]),
    "P-601": ("PLUMBING SCHEDULES", [
        ("1", "PLUMBING FIXTURE SCHEDULE", [
            "S-1  LAB SINK, EPOXY RESIN, UNDERMOUNT - ACME LS-2416 (24 x 16 BOWL)",
            "S-2  HAND SINK, STAINLESS, DROP-IN - ACME HS-1512",
            "EW-1 EYEWASH, PEDESTAL - BY 22 45 00",
        ]),
    ]),
}

SPEC_TEXT = [
    ("PART 1 - GENERAL", 11),
    ("1.1  SUMMARY", 10),
    ("A.  Section includes metal laboratory casework, epoxy resin work surfaces and wall-hung counters.", 9),
    ("B.  Fume hoods are specified in Section 11 53 13. Sinks are furnished under Section 22 40 00.", 9),
    ("1.2  COORDINATION", 10),
    ("A.  Furnish concealed in-wall counter brackets to the framing contractor for installation", 9),
    ("     before gypsum board. Coordinate locations and heights shown on the Drawings.", 9),
    ("B.  Size sink cutouts to the sink models scheduled on the plumbing drawings.", 9),
    ("1.3  ACTION SUBMITTALS", 10),
    ("A.  Product Data: For casework, work surfaces and hardware.", 9),
    ("B.  Shop Drawings: Plans and elevations keyed to the Contract Drawings, sections, work", 9),
    ("     surface heights, in-wall supports, cutouts for sinks and fixtures furnished by others,", 9),
    ("     and service fixture locations. Include every elevation shown on the Drawings.", 9),
    ("C.  Samples: Work surface colors.", 9),
    ("PART 2 - PRODUCTS", 11),
    ("2.1  METAL CASEWORK", 10),
    ("A.  Steel laboratory casework conforming to SEFA 8-M.", 9),
    ("2.2  EPOXY RESIN WORK SURFACES", 10),
    ("A.  Epoxy resin, 1 inch thick, conforming to SEFA 3.", 9),
    ("2.3  ACCESSIBLE WORKSTATIONS", 10),
    ("A.  Provide accessible student stations where indicated on the Drawings, with open knee space.", 9),
    ("PART 3 - EXECUTION", 11),
    ("3.1  INSTALLATION", 10),
    ("A.  Install casework level and plumb. Anchor wall-hung counters to in-wall brackets.", 9),
    (f"END OF SECTION {SPEC}", 11),
]


def title_block(page, number, title):
    tb = fitz.Rect(930, 600, 1200, 768)
    page.draw_rect(tb, width=1.5)
    page.insert_text((940, 625), PROJECT, fontsize=9)
    page.insert_text((940, 660), title, fontsize=10)
    page.insert_text((940, 700), "SHEET NUMBER", fontsize=7)
    page.insert_text((940, 745), number, fontsize=28)


def drawing_sheet(doc, number, title, views):
    page = doc.new_page(width=1224, height=792)
    page.draw_rect(fitz.Rect(18, 18, 1206, 774), width=2)
    x, y = 40, 50
    for tag, view_title, notes in views:
        frame = fitz.Rect(x, y, x + 420, y + 250)
        page.draw_rect(frame, width=1)
        # a schematic run of casework: base cabinets, or open below with brackets
        open_below = any("OPEN" in n for n in notes)
        if not open_below:
            for k in range(4):
                page.draw_rect(fitz.Rect(x + 20 + k * 90, y + 140, x + 100 + k * 90, y + 200), width=0.8)
        elif any("BRACKET" in n for n in notes):
            for k in range(4):
                bx = x + 40 + k * 100
                page.draw_polyline([fitz.Point(bx, y + 138), fitz.Point(bx, y + 170),
                                    fitz.Point(bx + 30, y + 138)], width=0.8)
        page.draw_line(fitz.Point(x + 15, y + 135), fitz.Point(x + 395, y + 135), width=2)
        ty = y + 20
        for note in notes:
            page.insert_text((x + 12, ty), note, fontsize=7.5)
            ty += 12
        page.draw_circle(fitz.Point(x + 30, y + 228), 14, width=1)
        page.insert_text((x + 25, y + 226), tag, fontsize=10)
        page.insert_text((x + 22, y + 238), number, fontsize=5.5)
        page.insert_text((x + 52, y + 232), view_title, fontsize=9)
        x += 440
        if x > 800:
            x, y = 40, y + 280
    title_block(page, number, title)
    return page


FIXTURE_NOTICE = "EVAL FIXTURE - fictional document generated for a synthetic evaluation; not a real project, firm or submittal"


def write_pdf(doc, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    for page in doc:  # every page says what it is, in the bottom margin
        page.insert_text((12, page.rect.height - 8), FIXTURE_NOTICE, fontsize=6)
    doc.save(str(path), garbage=4, deflate=True)


def drawings():
    folder = OUT / "01 - Drawings" / "Architectural & Structural"
    bound = fitz.open()
    pages = []
    for i, (number, (title, views)) in enumerate(SHEETS.items()):
        drawing_sheet(bound, number, title, views)
        single = fitz.open()
        drawing_sheet(single, number, title, views)
        name = f"{number} - {title}.pdf"
        write_pdf(single, folder / "sheets" / name)
        pages.append({"filename": name, "page_index": i, "page_size": "1224x792",
                      "source_pdf": "Arch Set.pdf", "sheet_number": number, "title": title})
    bound.set_toc([[1, f"{n} {t}", i + 1] for i, (n, (t, _)) in enumerate(SHEETS.items())])
    write_pdf(bound, folder / "Arch Set.pdf")
    index = {"sources": ["Arch Set.pdf"], "total_pages": len(pages), "pages": pages}
    (folder / "sheets" / "sheet_index.yaml").write_text(yaml.safe_dump(index, sort_keys=False))


def spec():
    folder = OUT / "02 - Specifications"
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    y = 72
    page.insert_text((72, y), f"SECTION {SPEC} - {SPEC_TITLE}", fontsize=12)
    y += 28
    text_lines = [f"SECTION {SPEC} - {SPEC_TITLE}", ""]
    for text, size in SPEC_TEXT:
        if y > 740:
            page = doc.new_page(width=612, height=792)
            y = 72
        page.insert_text((72, y), text, fontsize=size)
        y += size + 7
        text_lines.append(text.strip())
    write_pdf(doc, folder / "Specification Sections" / f"{SPEC} - {SPEC_TITLE}.pdf")
    bound = fitz.open()
    bound.insert_pdf(doc)
    write_pdf(bound, folder / "Project Manual.pdf")
    spec_dir = OUT / "dot-construction" / "skills" / "spec_text"
    spec_dir.mkdir(parents=True, exist_ok=True)
    key = SPEC.replace(" ", "_")
    (spec_dir / f"{key}.txt").write_text("\n".join(text_lines) + "\n", encoding="utf-8")
    manifest = {key: {"spec_title": SPEC_TITLE.title(), "extraction_method": "pdfplumber",
                      "quality_rating": "GOOD", "repair_attempted": False, "pages_extracted": len(doc),
                      "character_count": len("\n".join(text_lines)), "failure_modes": [],
                      "extracted_at": "2026-10-01T12:00:00+00:00"}}
    import json
    (spec_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))


def submittal():
    doc = fitz.open()
    p = doc.new_page(width=612, height=792)
    lines = [
        ("SUBMITTAL TRANSMITTAL", 14), ("", 8),
        (f"Project: {PROJECT}", 10),
        ("Submittal No.: 12 35 53-001     Revision: 0", 10),
        ("Spec Section: 12 35 53 Laboratory Casework", 10),
        ("Submittal Type: Shop Drawings", 10),
        ("From: Example Lab Casework Co.", 10),
        ("Date: 2026-09-28", 10), ("", 8),
        ("Contents:", 10),
        ("  SD-1  Elevations (Lab 104)", 10),
        ("  SD-2  Sections and Details", 10), ("", 8),
        ("Submitted for review. Contractor to verify field dimensions.", 9),
    ]
    y = 72
    for text, size in lines:
        p.insert_text((72, y), text, fontsize=size)
        y += size + 8

    sd1 = doc.new_page(width=1224, height=792)
    sd1.draw_rect(fitz.Rect(18, 18, 1206, 774), width=2)
    sd1.insert_text((40, 45), "SD-1  ELEVATIONS - SCIENCE LAB 104", fontsize=14)
    elevations = [
        ("ELEV 1 (REF 1/A-501) NORTH WALL", ["BASE CABINETS B-1, SINK BASE SB-1",
                                              "EPOXY RESIN TOP AT 36\" AFF",
                                              "SINK CUTOUT FOR ACME LS-1812 (18 x 12)"]),
        ("ELEV 2 (REF 2/A-501) WEST WALL - STUDENT STATION", ["DRAWER BASE CABINET DB-2 (4 DRAWERS)",
                                                              "EPOXY RESIN TOP AT 36\" AFF"]),
        ("ELEV 3 (REF 3/A-501) EAST WALL", ["WALL-HUNG EPOXY COUNTER AT 36\" AFF",
                                             "SUPPORTS BY OTHERS"]),
    ]
    x = 40
    for title, notes in elevations:
        sd1.draw_rect(fitz.Rect(x, 80, x + 370, 420), width=1)
        for k in range(3):
            sd1.draw_rect(fitz.Rect(x + 30 + k * 105, 300, x + 120 + k * 105, 380), width=0.8)
        sd1.draw_line(fitz.Point(x + 25, 295), fitz.Point(x + 345, 295), width=2)
        sd1.insert_text((x + 10, 100), title, fontsize=9)
        ty = 120
        for note in notes:
            sd1.insert_text((x + 10, ty), note, fontsize=8)
            ty += 13
        x += 390
    sd1.insert_text((40, 460), "NOTE: ALL ELEVATIONS SHOWN. FIELD VERIFY DIMENSIONS BEFORE FABRICATION.", fontsize=8)

    sd2 = doc.new_page(width=1224, height=792)
    sd2.draw_rect(fitz.Rect(18, 18, 1206, 774), width=2)
    sd2.insert_text((40, 45), "SD-2  SECTIONS AND DETAILS", fontsize=14)
    sections = [
        ("SECTION A - SINK BASE SB-1", ["UNDERMOUNT SINK CUTOUT 18 x 12",
                                        "PER ACME LS-1812 TEMPLATE",
                                        "1\" EPOXY RESIN TOP, SEFA 3"]),
        ("SECTION B - BASE CABINET", ["18 GA STEEL, SEFA 8-M",
                                      "ACID-RESISTANT POWDER COAT"]),
        ("SECTION C - WALL-HUNG COUNTER", ["1\" EPOXY TOP",
                                           "ATTACHMENT TO WALL BY OTHERS"]),
    ]
    x = 40
    for title, notes in sections:
        sd2.draw_rect(fitz.Rect(x, 80, x + 370, 380), width=1)
        sd2.insert_text((x + 10, 100), title, fontsize=9)
        ty = 120
        for note in notes:
            sd2.insert_text((x + 10, ty), note, fontsize=8)
            ty += 13
        x += 390
    write_pdf(doc, OUT / "06 - Submittals" / SUBMITTAL)


def context():
    ctx = {
        "project": {"name": PROJECT, "location": {"city": "Example City", "state": "FL"}},
        "building": {"occupancy_type": "E", "building_use": "K-12 school renovation",
                     "facility_types": ["education.k12"]},
    }
    path = OUT / "dot-construction" / "skills" / "project_context.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(ctx, sort_keys=False))
    (OUT / "CLAUDE.md").write_text(
        f"# {PROJECT}\n\nSample project used by the submittal-review eval.\n\n"
        "## Construction Project Context\n\n### Document Locations\n"
        "- Drawing set: 01 - Drawings/Architectural & Structural/ (split sheets and sheet_index.yaml in sheets/)\n"
        "- Specifications: 02 - Specifications/Specification Sections/ (text in .construction/skills/spec_text/)\n"
        "- Submittals: 06 - Submittals/\n- Schedule: not found\n- RFI log: not found\n- Submittal log: not found\n\n"
        "### Status\n- Operational mode: Flat File\n- Sheets indexed: yes\n- Specs split: yes\n"
        "- Spec text extracted: yes\n")


if __name__ == "__main__":
    drawings()
    spec()
    submittal()
    context()
    for f in sorted(OUT.rglob("*")):
        if f.is_file():
            print(f"{f.relative_to(OUT)}  ({max(1, f.stat().st_size // 1024)} KB)")
