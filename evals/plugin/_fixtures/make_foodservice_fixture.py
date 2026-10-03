#!/usr/bin/env python3
"""Generate the large-brochure submittal-review eval project: a central kitchen with a
foodservice equipment schedule, an electrical connection schedule, the 11 40 00 spec
section, and a 300-plus-page equipment product data package with planted defects.

Run with: bin/construction-python evals/plugin/_fixtures/make_foodservice_fixture.py

Writes foodservice-project/ next to this script, prepared the way project-setup,
sheet-splitter and spec-splitter leave a project. The .construction/ folder is written
as dot-construction/ (the repository ignores .construction/); the case's setup.sh
renames it after copying.

Planted defects (the ground truth the graders check):
  D1  Item 17 hand sinks (ADV-7PS50, qty 3) are on FS-601 but not in the package.
  D2  Item 1 walk-in cooler: a cut sheet deep in its tab gives the remote condensing
      unit as 208V 1PH; FS-601 and E-601 schedule 208V 3PH.
  D3  Item 11 exhaust hood is submitted as CAP-KVEW96, 8'-0" long; FS-601 schedules
      CAP-KVEW120, 10'-0" long, over the cooking line.
  D4  The package includes item 20, a soft serve machine that is not on the schedule.
"""
import json
import random
from pathlib import Path

import pymupdf as fitz
import yaml

HERE = Path(__file__).resolve().parent
OUT = HERE / "foodservice-project"
PROJECT = "RIVERSIDE HIGH SCHOOL CENTRAL KITCHEN"
SPEC, SPEC_TITLE = "11 40 00", "FOODSERVICE EQUIPMENT"
SUBMITTAL = "11 40 00-001 R0 Foodservice Equipment Product Data.pdf"

# item, description, scheduled model, qty, electrical, plumbing
SCHEDULE = [
    (1, "Walk-in cooler with remote condensing unit", "KOLD-WC812", 1, "208V 3PH (condensing unit); 115V 1PH (evaporator)", "Indirect drain at evaporator"),
    (2, "Walk-in freezer with remote condensing unit", "KOLD-WF810", 1, "208V 3PH (condensing unit); 208V 1PH (evaporator)", "Indirect drain, heated line"),
    (3, "Reach-in refrigerator", "TRL-RHT132", 2, "115V 1PH", "-"),
    (4, "Convection oven, double stack", "BLD-ZEPH200", 1, "208V 3PH", "-"),
    (5, "Combi oven", "RAT-ICP101", 1, "208V 3PH", "CW (filtered), floor drain"),
    (6, "Tilting skillet", "GRP-SKT40", 1, "208V 3PH", "HW, CW, floor drain"),
    (7, "Steam kettle", "GRP-KET60", 1, "208V 3PH", "HW, CW, floor drain"),
    (8, "Fryer battery", "PIT-SSH55", 1, "120V 1PH (controls); gas", "-"),
    (9, "Griddle", "VUL-948RX", 1, "Gas", "-"),
    (10, "Charbroiler", "VUL-VCCB36", 1, "Gas", "-"),
    (11, "Exhaust hood, 10'-0\" long, over cooking line", "CAP-KVEW120", 1, "115V 1PH (lights, controls)", "-"),
    (12, "Hood fire suppression system", "ANS-R102", 1, "120V 1PH (release, shunt)", "-"),
    (13, "Dishmachine, conveyor", "HOB-CL44E", 1, "208V 3PH", "HW 140F, floor drain"),
    (14, "Booster heater", "HAT-SM40", 1, "208V 3PH", "HW in, 180F out"),
    (15, "Food waste disposer", "INS-SS500", 1, "208V 3PH", "CW, waste"),
    (16, "Ice machine with bin", "MAN-IYT1500", 1, "208V 1PH", "CW (filtered), indirect drain"),
    (17, "Hand sink, wall-mounted", "ADV-7PS50", 3, "-", "HW, CW, waste"),
    (18, "Three-compartment sink", "ADV-94-3-54", 1, "-", "HW, CW, indirect waste"),
    (19, "Pot washer", "ECO-ST", 1, "208V 3PH", "HW, CW, floor drain"),
]

SPEC_TEXT = [
    ("PART 1 - GENERAL", 11),
    ("1.1  SUMMARY", 10),
    ("A.  Section includes the foodservice equipment scheduled on Drawing FS-601, furnished, set and", 9),
    ("     made ready for final connection. Hand sinks and the hood fire suppression system are included.", 9),
    ("1.2  COORDINATION", 10),
    ("A.  Electrical characteristics of each item shall match the Kitchen Equipment Connection Schedule", 9),
    ("     on Drawing E-601. Report any difference before release for fabrication.", 9),
    ("B.  Exhaust hood length, model and capture area shall be as scheduled; coordinate duct collars with", 9),
    ("     Division 23 and the fire suppression system with the fire alarm system.", 9),
    ("1.3  ACTION SUBMITTALS", 10),
    ("A.  Product Data: For every item scheduled on FS-601, keyed to the item number, with the scheduled", 9),
    ("     model, options, accessories and electrical characteristics clearly marked.", 9),
    ("B.  Include wiring diagrams and utility connection data for each item.", 9),
    ("C.  Do not include items not scheduled unless submitted as a substitution under Section 01 25 00.", 9),
    ("1.4  REGULATORY REQUIREMENTS", 10),
    ("A.  Comply with the food code and plan review requirements of the health department having", 9),
    ("     jurisdiction. Equipment shall be listed to the applicable NSF/ANSI standards.", 9),
    ("PART 2 - PRODUCTS", 11),
    ("2.1  EQUIPMENT", 10),
    ("A.  As scheduled on FS-601. Substitutions only under Section 01 25 00.", 9),
    ("PART 3 - EXECUTION", 11),
    ("3.1  INSTALLATION", 10),
    ("A.  Set equipment level, seal to adjacent surfaces, and coordinate final connections.", 9),
    (f"END OF SECTION {SPEC}", 11),
]


def write_pdf(doc, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(path), garbage=4, deflate=True)


def title_block(page, number, title):
    tb = fitz.Rect(930, 600, 1200, 768)
    page.draw_rect(tb, width=1.5)
    page.insert_text((940, 625), PROJECT, fontsize=8)
    page.insert_text((940, 660), title, fontsize=10)
    page.insert_text((940, 700), "SHEET NUMBER", fontsize=7)
    page.insert_text((940, 745), number, fontsize=28)


def schedule_sheet(doc, number, title, header, rows, widths):
    page = doc.new_page(width=1224, height=792)
    page.draw_rect(fitz.Rect(18, 18, 1206, 774), width=2)
    page.insert_text((40, 50), title, fontsize=14)
    y = 80
    xs = [40]
    for w in widths[:-1]:
        xs.append(xs[-1] + w)
    for x, h in zip(xs, header):
        page.insert_text((x, y), h, fontsize=8)
    y += 6
    page.draw_line(fitz.Point(40, y), fitz.Point(40 + sum(widths), y), width=1)
    for row in rows:
        y += 16
        for x, cell in zip(xs, row):
            page.insert_text((x, y), str(cell), fontsize=7.5)
    title_block(page, number, title)


def drawings():
    folder = OUT / "01 - Drawings" / "Foodservice & MEP"
    sheets = {
        "FS-601": ("FOODSERVICE EQUIPMENT SCHEDULE",
                   ["ITEM", "DESCRIPTION", "MODEL (BASIS OF DESIGN)", "QTY", "ELECTRICAL", "PLUMBING"],
                   [(i, d, m, q, e, p) for i, d, m, q, e, p in SCHEDULE],
                   [40, 300, 150, 40, 300, 200]),
        "E-601": ("KITCHEN EQUIPMENT CONNECTION SCHEDULE",
                  ["FS ITEM", "EQUIPMENT", "VOLTAGE / PHASE", "CIRCUIT", "DISCONNECT"],
                  [(i, d.split(",")[0], e, f"KP-{2 * i - 1}", "Fused, by 26 28 16" if "3PH" in e else "Cord and plug")
                   for i, d, m, q, e, p in SCHEDULE if e not in ("-", "Gas")],
                  [60, 320, 330, 100, 200]),
    }
    bound, pages = fitz.open(), []
    for i, (number, (title, header, rows, widths)) in enumerate(sheets.items()):
        schedule_sheet(bound, number, title, header, rows, widths)
        single = fitz.open()
        schedule_sheet(single, number, title, header, rows, widths)
        name = f"{number} - {title}.pdf"
        write_pdf(single, folder / "sheets" / name)
        pages.append({"filename": name, "page_index": i, "page_size": "1224x792",
                      "source_pdf": "Kitchen Set.pdf", "sheet_number": number, "title": title})
    bound.set_toc([[1, f"{n} {v[0]}", i + 1] for i, (n, v) in enumerate(sheets.items())])
    write_pdf(bound, folder / "Kitchen Set.pdf")
    index = {"sources": ["Kitchen Set.pdf"], "total_pages": len(pages), "pages": pages}
    (folder / "sheets" / "sheet_index.yaml").write_text(yaml.safe_dump(index, sort_keys=False))


def spec():
    folder = OUT / "02 - Specifications"
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    y = 72
    page.insert_text((72, y), f"SECTION {SPEC} - {SPEC_TITLE}", fontsize=12)
    y += 28
    lines = [f"SECTION {SPEC} - {SPEC_TITLE}", ""]
    for text, size in SPEC_TEXT:
        if y > 740:
            page = doc.new_page(width=612, height=792)
            y = 72
        page.insert_text((72, y), text, fontsize=size)
        y += size + 7
        lines.append(text.strip())
    write_pdf(doc, folder / "Specification Sections" / f"{SPEC} - {SPEC_TITLE}.pdf")
    bound = fitz.open()
    bound.insert_pdf(doc)
    write_pdf(bound, folder / "Project Manual.pdf")
    spec_dir = OUT / "dot-construction" / "skills" / "spec_text"
    spec_dir.mkdir(parents=True, exist_ok=True)
    key = SPEC.replace(" ", "_")
    (spec_dir / f"{key}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest = {key: {"spec_title": SPEC_TITLE.title(), "extraction_method": "pdfplumber",
                      "quality_rating": "GOOD", "repair_attempted": False, "pages_extracted": len(doc),
                      "character_count": len("\n".join(lines)), "failure_modes": [],
                      "extracted_at": "2026-10-01T12:00:00+00:00"}}
    (spec_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))


FILLER = [
    "Construction: type 304 stainless steel exterior and interior, coved corners.",
    "Listings: NSF/ANSI 7 or 4 as applicable; UL listed; ENERGY STAR where noted.",
    "Installation: level on adjustable feet; seal to adjacent surfaces per manufacturer.",
    "Warranty: one year parts and labor; extended compressor warranty available.",
    "Options and accessories as marked on the order form. Specifications subject to change.",
]


def text_page(doc, heading, lines, size=15):
    p = doc.new_page(width=612, height=792)
    p.insert_text((50, 60), heading, fontsize=size)
    y = 92
    for line in lines:
        p.insert_text((50, y), line, fontsize=9)
        y += 14
    return p


def submittal():
    random.seed(11)
    doc = fitz.open()
    text_page(doc, "SUBMITTAL TRANSMITTAL", [
        f"Project: {PROJECT}", "Submittal No.: 11 40 00-001     Revision: 0",
        "Spec Section: 11 40 00 Foodservice Equipment", "Submittal Type: Product Data",
        "From: Example Kitchen Equipment Co.", "Date: 2026-09-28", "",
        "Contents: cut sheets, wiring diagrams and installation data for all scheduled equipment.",
        "Submitted for review. Contractor to verify utility connections in field."], size=22)
    in_package = [s for s in SCHEDULE if s[0] != 17] + [(20, "Soft serve machine", "XTR-500", 1, "208V 1PH", "-")]
    text_page(doc, "TABLE OF CONTENTS",
              [f"ITEM {i}   {d.split(',')[0]}   {m}   ....   tab {i}" for i, d, m, *_ in in_package], size=22)
    scans = []
    for i, desc, model, qty, elec, plumb in in_package:
        submitted_model = "CAP-KVEW96" if i == 11 else model
        name = desc.split(",")[0].upper()
        text_page(doc, f"ITEM {i} - {name}", [f"Model {submitted_model}", f"Quantity {qty}",
                                                f"Electrical: {elec}" if i != 1 else "Electrical: see condensing unit data",
                                                "Options as marked"], size=22)
        for k in range(random.randint(14, 21)):
            lines = [f"{submitted_model} - SPECIFICATION SHEET {k + 1}"] + random.sample(FILLER, 4)
            if i == 1 and k == 11:
                lines += ["", "REMOTE CONDENSING UNIT DATA",
                          "Condensing unit: 208V 1PH 60Hz, MCA 18.2 A, MOPD 30 A",
                          "Evaporator coil: 115V 1PH, 4.1 A"]
            if i == 11 and k == 7:
                lines += ["", "HOOD DIMENSIONS",
                          "Model CAP-KVEW96: overall length 8'-0\" (96 in), depth 54 in",
                          "Two duct collars, 12 x 20 in; integral light fixtures, 115V"]
            text_page(doc, f"{submitted_model} SERIES", lines)
            defect_page = (i == 1 and k == 11) or (i == 11 and k == 7)
            if not defect_page and random.random() < 0.05:
                scans.append(doc.page_count)
    for pno in scans:  # some vendor pages arrive as scans with no text layer
        pix = doc[pno - 1].get_pixmap(dpi=60)
        doc.delete_page(pno - 1)
        p = doc.new_page(pno - 1, width=612, height=792)
        p.insert_image(p.rect, pixmap=pix)
    write_pdf(doc, OUT / "06 - Submittals" / SUBMITTAL)
    return doc.page_count


def context():
    ctx = {"project": {"name": PROJECT, "location": {"city": "Columbia", "county": "Howard County", "state": "MD"}},
           "building": {"occupancy_type": "E", "building_use": "High school central kitchen",
                        "facility_types": ["education.k12", "foodservice"]}}
    path = OUT / "dot-construction" / "skills" / "project_context.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(ctx, sort_keys=False))
    (OUT / "CLAUDE.md").write_text(
        f"# {PROJECT}\n\nSample project used by the submittal-review eval.\n\n"
        "## Construction Project Context\n\n### Document Locations\n"
        "- Drawing set: 01 - Drawings/Foodservice & MEP/ (split sheets and sheet_index.yaml in sheets/)\n"
        "- Specifications: 02 - Specifications/Specification Sections/ (text in .construction/skills/spec_text/)\n"
        "- Submittals: 06 - Submittals/\n- Schedule: not found\n- RFI log: not found\n- Submittal log: not found\n\n"
        "### Status\n- Operational mode: Flat File\n- Sheets indexed: yes\n- Specs split: yes\n"
        "- Spec text extracted: yes\n")


if __name__ == "__main__":
    drawings()
    spec()
    pages = submittal()
    context()
    print(f"Submittal: {pages} pages")
    for f in sorted(OUT.rglob("*")):
        if f.is_file():
            print(f"{f.relative_to(OUT)}  ({max(1, f.stat().st_size // 1024)} KB)")
