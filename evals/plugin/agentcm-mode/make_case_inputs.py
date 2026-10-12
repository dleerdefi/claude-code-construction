#!/usr/bin/env python3
"""Write the synthetic documents three agentcm-mode cases bring with them: the skill's own inputs, not AgentCM's.

Run:  bin/construction-python evals/plugin/agentcm-mode/make_case_inputs.py
Deterministic: fixed PDF creation dates, a core font, no randomness; the same bytes every run.

The fixture's one manual AgentCM read holds 08 11 13 (hollow metal doors and frames: "Floor Anchors: not
less than 0.042 inch thick") and 09 30 00. Its A-601 door schedule lists D101 to D115, every frame HM, the
doors HM at D102, D104, ..., D114 (7). So the package is BP-08 Hollow Metal Frames and Doors, 08 11 13.
Everything else (the GC, bidders, people, prices) is invented.

Writes, under each case's inputs/ (its setup.sh copies them into the workspace):
  agentcm-mode-bid-evaluator/inputs/project/03 - Subcontractor Bids/BP-08 Hollow Metal/  scope sheet, 3 bids
  agentcm-mode-bid-evaluator/inputs/tabulated/<slug>.json      as bid-tabulator writes them (the repository
                                                               ignores .construction/, so setup puts them there)
  agentcm-mode-subcontract-writer/inputs/project/03 - Subcontractor Bids/BP-08 Hollow Metal/  scope sheet,
                                                               the awarded bid (A)
  agentcm-mode-submittal-review/inputs/project/06 - Submittals/08 11 13-001 R0 ... Product Data.pdf

Planted (the ground truth):
  Bids: A Lakeside Door & Frame Co. is clean (floor anchors 0.042 in, per 08 11 13), the highest bid and the
  one awarded. B Northgate Metal Openings LLC, the low bid, qualifies 20 gauge (0.0359 in) floor anchors,
  thinner than 08 11 13 allows. C Ridgeline Hollow Metal Inc. excludes floor anchors ("by others").
  Submittal (from A): S1 floor anchors 20 ga (0.036 in), below the 0.042 in of 08 11 13 1.1 B;
  S2 the frame schedule lists D101 to D114, so D115 (on A-601) is not submitted.
"""
import json
import re
from datetime import datetime
from pathlib import Path

from fpdf import FPDF

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent
FIXED_DATE = datetime(2026, 10, 1, 12, 0, 0)
PROJECT = "Smoke project"
PACKAGE = "BP-08 Hollow Metal Frames and Doors"
FOLDER = "03 - Subcontractor Bids/BP-08 Hollow Metal"
GC = "Example Builders, Inc."
DOORS = [f"D{n}" for n in range(101, 116)]
HM_DOORS = [d for i, d in enumerate(DOORS) if i % 2 == 1]  # D102, D104, ... D114, as A-601 says


def doc():
    d = FPDF(format="Letter")
    d.set_creation_date(FIXED_DATE)
    d.set_margins(18, 16, 18)
    d.set_auto_page_break(True, 16)
    d.add_page()
    return d


def text(d, s, bold=False, size=10, gap=0.0):
    d.set_font("Helvetica", "B" if bold else "", size)
    d.multi_cell(0, size * 0.5, s, new_x="LMARGIN", new_y="NEXT")
    d.ln(gap)


def table(d, rows, widths, bold_first=True):
    for n, row in enumerate(rows):
        d.set_font("Helvetica", "B" if bold_first and n == 0 else "", 9)
        for v, w in zip(row, widths):
            d.cell(w, 6, str(v), border=1)
        d.ln(6)
    d.ln(2)


def money(x):
    return f"${x:,.2f}"


BIDS = [
    {"key": "A", "company_name": "Lakeside Door & Frame Co.", "file": "01 - Lakeside Door and Frame Co.pdf",
     "contact_name": "Dana Whitfield", "contact_phone": "(555) 010-2201", "contact_email": "bids@lakesidedoor.example",
     "bid_date": "September 22, 2026", "anchor": ("Floor anchors, 0.042 in steel, 2 per frame", 30, 12.0, "per 08 11 13 1.1 B"),
     "frame": 485.0, "door": 640.0, "exclusions": ["Door hardware (by others)", "Field painting"],
     "qualifications": ["Frames 16 gauge, welded, factory primed"]},
    {"key": "B", "company_name": "Northgate Metal Openings LLC", "file": "02 - Northgate Metal Openings LLC.pdf",
     "contact_name": "Priya Raman", "contact_phone": "(555) 010-2202", "contact_email": "estimating@northgatemetal.example",
     "bid_date": "September 23, 2026", "anchor": ("Floor anchors, 20 gauge, 2 per frame", 30, 9.0, "20 ga (0.0359 in)"),
     "frame": 455.0, "door": 610.0, "exclusions": ["Door hardware (by others)", "Field painting"],
     "qualifications": ["Frames 16 gauge, knock-down", "Floor anchors 20 gauge (0.0359 in), manufacturer's standard"]},
    {"key": "C", "company_name": "Ridgeline Hollow Metal Inc.", "file": "03 - Ridgeline Hollow Metal Inc.pdf",
     "contact_name": "Tomas Ferreira", "contact_phone": "(555) 010-2203", "contact_email": "office@ridgelinehm.example",
     "bid_date": "September 23, 2026", "anchor": None,
     "frame": 470.0, "door": 625.0, "exclusions": ["Door hardware (by others)", "Floor anchors (by others)", "Field painting"],
     "qualifications": ["Frames 16 gauge, welded"]},
]


def lines(b):
    out = [{"spec_section": "08 11 13", "description": "Hollow metal frame, 3'-0\" x 7'-0\", for D101 to D115",
            "qty": 15, "unit": "EA", "unit_price": b["frame"], "extended_price": 15 * b["frame"], "notes": ""},
           {"spec_section": "08 11 13", "description": "Hollow metal door, 3'-0\" x 7'-0\" x 1-3/4\", where A-601 says HM",
            "qty": 7, "unit": "EA", "unit_price": b["door"], "extended_price": 7 * b["door"], "notes": ""}]
    if b["anchor"]:
        desc, qty, price, note = b["anchor"]
        out.append({"spec_section": "08 11 13", "description": desc, "qty": qty, "unit": "EA", "unit_price": price,
                    "extended_price": qty * price, "notes": note})
    return out


def tabulated(b):
    items = lines(b)
    return {"company_name": b["company_name"], "contact_name": b["contact_name"], "contact_phone": b["contact_phone"],
            "contact_email": b["contact_email"], "bid_date": b["bid_date"], "bid_validity_period": "60 days",
            "base_bid_amount": sum(i["extended_price"] for i in items), "bond_included": True,
            "schedule_duration": "6 weeks from approved submittals", "payment_terms": "Net 30 from approved pay application",
            "addenda_acknowledged": [], "line_items": items, "alternates": [],
            "scope_inclusions": ["Furnish and install hollow metal frames and doors per 08 11 13 and the A-601 door schedule"],
            "scope_exclusions": b["exclusions"], "qualifications": b["qualifications"], "allowances": [],
            "insurance_confirmed": True}


def bid_pdf(b, out):
    t = tabulated(b)
    d = doc()
    text(d, b["company_name"], bold=True, size=14)
    text(d, f"{b['contact_name']}  |  {b['contact_phone']}  |  {b['contact_email']}", size=9, gap=3)
    text(d, f"To: {GC}    Project: {PROJECT}    Date: {b['bid_date']}", gap=1)
    text(d, f"BID: {PACKAGE} (Section 08 11 13)", bold=True, gap=2)
    rows = [["Section", "Description", "Qty", "Unit", "Unit price", "Extended"]]
    rows += [[i["spec_section"], i["description"][:46], i["qty"], i["unit"], money(i["unit_price"]), money(i["extended_price"])]
             for i in t["line_items"]]
    table(d, rows, [18, 82, 12, 12, 24, 28])
    text(d, f"BASE BID: {money(t['base_bid_amount'])}", bold=True, gap=2)
    text(d, "Qualifications:", bold=True)
    for q in t["qualifications"]:
        text(d, f"- {q}")
    text(d, "Exclusions:", bold=True)
    for x in t["scope_exclusions"]:
        text(d, f"- {x}")
    d.ln(2)
    text(d, "Bid valid 60 days. Performance and payment bond included. Insurance certificate on request. "
            "Schedule: 6 weeks from approved submittals. Payment: net 30 from approved pay application.")
    out.parent.mkdir(parents=True, exist_ok=True)
    d.output(str(out))


def scope_sheet(out):
    d = doc()
    text(d, f"{GC} - Bid Package Scope Sheet", bold=True, size=14, gap=2)
    text(d, f"Project: {PROJECT}    Package: {PACKAGE}    Section: 08 11 13", gap=2)
    text(d, "Scope: furnish and install hollow metal frames for all 15 doors on the A-601 door schedule (D101 to D115) "
            "and hollow metal doors where the schedule says HM (D102, D104, D106, D108, D110, D112, D114), with floor "
            "anchors, all per Section 08 11 13.", gap=1)
    text(d, "Excluded from this package: door hardware (by the hardware supplier), wood doors, field painting.", gap=1)
    text(d, "Bid form: unit and extended prices per line, base bid, qualifications and exclusions stated.")
    out.parent.mkdir(parents=True, exist_ok=True)
    d.output(str(out))


def submittal(out):
    d = doc()
    text(d, "SUBMITTAL TRANSMITTAL", bold=True, size=14, gap=2)
    table(d, [["Field", "Value"], ["Project", PROJECT], ["Submittal no.", "08 11 13-001, revision 0"],
              ["Section", "08 11 13 Hollow Metal Doors and Frames"], ["Type", "Product data and frame schedule"],
              ["From", "Lakeside Door & Frame Co. (subcontractor)"], ["To", f"{GC} for review"],
              ["Date", "October 1, 2026"]], [45, 120])
    text(d, "Contents: product data (page 2), frame schedule (page 3).")
    d.add_page()
    text(d, "PRODUCT DATA - LDF SERIES HOLLOW METAL FRAMES AND DOORS", bold=True, size=12, gap=2)
    table(d, [["Item", "Lakeside standard"], ["Frame", "16 gauge cold-rolled steel, welded, factory primed"],
              ["Door", "1-3/4 in, 18 gauge face sheets, honeycomb core"], ["Jamb anchors", "Wall anchors, 3 per jamb"],
              ["Floor anchors", "20 ga (0.036 in) steel clip, 2 per frame"], ["Finish", "Rust-inhibitive primer"]], [45, 120])
    d.add_page()
    text(d, "FRAME SCHEDULE", bold=True, size=12, gap=2)
    rows = [["Mark", "Size", "Frame", "Door"]]
    rows += [[m, "3'-0\" x 7'-0\"", "HM", "HM" if m in HM_DOORS else "by others"] for m in DOORS[:-1]]  # S2: no D115
    table(d, rows, [25, 45, 30, 40])
    out.parent.mkdir(parents=True, exist_ok=True)
    d.output(str(out))


def slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def main():
    ev = PLUGIN / "agentcm-mode-bid-evaluator" / "inputs"
    for b in BIDS:
        bid_pdf(b, ev / "project" / FOLDER / b["file"])
        p = ev / "tabulated" / f"{slug(b['company_name'])}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(tabulated(b), indent=2) + "\n", encoding="utf-8", newline="\n")
    scope_sheet(ev / "project" / FOLDER / "00 - Bid Package Scope Sheet.pdf")
    sw = PLUGIN / "agentcm-mode-subcontract-writer" / "inputs" / "project" / FOLDER
    scope_sheet(sw / "00 - Bid Package Scope Sheet.pdf")
    bid_pdf(BIDS[0], sw / BIDS[0]["file"])
    submittal(PLUGIN / "agentcm-mode-submittal-review" / "inputs" / "project" / "06 - Submittals"
              / "08 11 13-001 R0 Hollow Metal Frames and Doors Product Data.pdf")
    print("written: bid-evaluator (3 bids, scope sheet, tabulated), subcontract-writer (scope sheet, bid A), "
          "submittal-review (08 11 13-001 R0)")


if __name__ == "__main__":
    main()
