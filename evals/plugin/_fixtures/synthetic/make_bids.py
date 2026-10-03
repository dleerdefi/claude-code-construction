#!/usr/bin/env python3
"""Generate the synthetic BP-09 Flooring bid package for bid-tabulator / bid-evaluator evals.

Run:  bin/construction-python evals/plugin/_fixtures/synthetic/make_bids.py
Deterministic: no randomness, fixed PDF creation dates, same bytes every run.

Writes (next to this file):
  bids/00 - Bid Package Scope Sheet.pdf   GC scope sheet (also bids_ground_truth/scope_sheet.md)
  bids/01..05 - <bidder>.pdf              the five bids
  bids_ground_truth/bids/<slug>.json      per-bid bid-tabulator JSON (what a perfect extraction returns)
  bids_ground_truth/defects.json          planted-defect manifest

Project facts (Sanibel Fire and Rescue Station 172, CD set dated January 5, 2024, the six spec
sections, the ASTM F 1869 / F 2170 moisture-testing requirement of 09 65 40) are real. The GC
("Example Builders, Inc."), all bidders, people, licences, quantities and prices are invented.

Planted defects (A is the clean control; it is the bid awarded in a later eval):
  A Gulfshore Resilient Floors LLC  text PDF, 2 pp, bid-form layout. Clean.
  B Island Tile & Surface, Inc.     text PDF, 1 p.  09 65 13 silently omitted (no line, no mention);
                                    stated base bid is $4,200 higher than the sum of its lines.
  C Palmetto Surface Systems Corp.  text PDF, 3 pp, proposal letter. Moisture mitigation / ASTM F 1869
                                    / F 2170 testing excluded only in qualification #7; "budgetary only,
                                    not a firm offer"; alternates stated only inside qualifications;
                                    $5,000 substrate-patching allowance; 09 30 00 unit prices > 2x others.
                                    (Its Alternate B deduct of $8,000 is dictated by the brief, not an
                                    extra planted defect.)
  D Sandbar Flooring Contractors    IMAGE-ONLY PDF (150 dpi raster, no text layer). The 09 67 10 extended
                                    price is hidden under an opaque smudge; addenda acknowledgement blank.
  E Mangrove Interiors Group        text PDF, 1 p, narrative letter, no table. 15-day validity; bond not
                                    mentioned; 09 65 67 priced "per plans dated December 1, 2023" (stale).
"""
import io
import json
import re
from datetime import datetime
from pathlib import Path

import fitz
from fpdf import FPDF
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
BIDS_DIR = HERE / "bids"
GT_DIR = HERE / "bids_ground_truth"
GT_BIDS = GT_DIR / "bids"

FOOTER = ("EVAL FIXTURE \u2014 fictional bid for a synthetic evaluation; "
          "not a real company, person or offer")
FIXED_DATE = datetime(2024, 2, 1, 12, 0, 0)
UNCLEAR = "[unclear: smudged on scan]"

PROJECT = "Sanibel Fire and Rescue Station 172, Sanibel, Florida"
OWNER = "Sanibel Fire and Rescue District"
ARCHITECT = "Schenkel Shultz Architecture"
PROJECT_NO = "2023820"
CD_SET = "100% Construction Documents dated January 5, 2024"
GC = "Example Builders, Inc."
PACKAGE = "BP-09 Flooring"
SECTIONS = [
    ("09 30 00", "TILING"),
    ("09 65 13", "RESILIENT BASE AND ACCESSORIES"),
    ("09 65 40", "LUXURY VINYL TILE"),
    ("09 65 67", "RESILIENT ATHLETIC FINISHES"),
    ("09 67 00", "RESINOUS FLAKE FLOORING - EPX-2"),
    ("09 67 10", "RESINOUS QUARTZ FLOORING - EPX-3 AND EPX-4"),
]
ALT_A = ("Alternate A", "Polished concrete in lieu of luxury vinyl tile (09 65 40)")
ALT_B = ("Alternate B", "Delete resilient athletic finishes (09 65 67)")
MOISTURE_INCL = ("Moisture testing of concrete substrates per ASTM F 1869 and "
                 "ASTM F 2170 before installation (09 65 40)")
GENERIC_INCL = "Furnish and install all materials, labor and equipment for the priced sections"

# Bidder take-off lines, shared by all bidders: key, spec, description, qty, unit
LINES = [
    ("T1", "09 30 00", "Porcelain floor tile, installed", 4200, "SF"),
    ("T2", "09 30 00", "Ceramic wall tile, installed", 2600, "SF"),
    ("R1", "09 65 13", "Rubber base, 4 inch, with accessories", 6800, "LF"),
    ("V1", "09 65 40", "Luxury vinyl tile, installed", 9500, "SF"),
    ("A1", "09 65 67", "Resilient athletic flooring, installed", 3800, "SF"),
    ("E2", "09 67 00", "Resinous flake flooring EPX-2", 2900, "SF"),
    ("E3", "09 67 10", "Resinous quartz flooring EPX-3 and EPX-4", 3100, "SF"),
]
PRICES = {  # unit price per line key; None = line not bid at all
    "A": dict(T1=21.00, T2=14.50, R1=3.25, V1=8.75, A1=28.50, E2=12.50, E3=18.00),
    "B": dict(T1=22.00, T2=15.00, R1=None, V1=9.10, A1=27.00, E2=13.25, E3=17.50),
    "C": dict(T1=48.00, T2=33.00, R1=3.40, V1=8.60, A1=29.00, E2=12.00, E3=18.50),
    "D": dict(T1=20.50, T2=14.00, R1=3.10, V1=8.90, A1=26.50, E2=12.80, E3=17.00),
    "E": dict(T1=20.00, T2=14.50, R1=3.30, V1=9.00, A1=27.50, E2=12.25, E3=18.25),
}


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def make_bid(key, company, street, phone, email, lic, contact, proposal, bid_date, validity,
             bond, schedule, payment, addenda, alts, inclusions, exclusions, quals,
             stated_delta=0, allowance=None, notes=None):
    items = []
    for k, spec, desc, qty, unit in LINES:
        up = PRICES[key][k]
        if up is not None:
            items.append(dict(spec_section=spec, description=desc, qty=qty, unit=unit,
                              unit_price=up, extended_price=round(qty * up, 2),
                              notes=(notes or {}).get(k, "")))
    allowances = []
    if allowance:
        at = next(n for n, i in enumerate(items) if i["spec_section"] == "09 65 40") + 1
        items.insert(at, dict(spec_section="09 65 40", description="Allowance - substrate patching",
                              qty=1, unit="LS", unit_price=allowance,
                              extended_price=float(allowance), notes="Allowance"))
        allowances = [dict(description="Substrate patching", amount=allowance)]
    total = round(sum(i["extended_price"] for i in items), 2)
    return dict(
        key=key, company_name=company, street=street, contact_name=contact, contact_phone=phone,
        contact_email=email, license=lic, proposal_no=proposal, bid_date=bid_date,
        bid_validity_period=validity, base_bid_amount=round(total + stated_delta, 2),
        bond_included=bond, schedule_duration=schedule, payment_terms=payment,
        addenda_acknowledged=addenda, line_items=items,
        alternates=[dict(name=n, description=d, amount=a) for (n, d), a in zip((ALT_A, ALT_B), alts)],
        scope_inclusions=inclusions, scope_exclusions=exclusions, qualifications=quals,
        allowances=allowances, insurance_confirmed=True)


ADDENDA = ["Addendum 1", "Addendum 2"]
INSURANCE = "Insurance: required coverage confirmed"
BIDS = [
    make_bid("A", "Gulfshore Resilient Floors LLC", "4410 Metro Parkway, Fort Myers, FL 33916",
             "(239) 555-0141", "estimating@gulfshoreresilient.example", "CFC1428831", "Marisol Vega",
             "GRF-2024-0217", "February 19, 2024", "60 days", True, "12 weeks from notice to proceed",
             "Net 30 from approved pay application", ADDENDA, (38500, -102000),
             [GENERIC_INCL, MOISTURE_INCL, "Bid and performance bond"],
             ["Patching of substrate beyond 1/8 inch", "Work outside normal hours",
              "Permit fees"],
             ["Quantities are based on bidder's take-off from the 100% Construction Documents "
              "dated January 5, 2024"]),
    make_bid("B", "Island Tile & Surface, Inc.", "1209 Periwinkle Way, Sanibel, FL 33957",
             "(239) 555-0178", "bids@islandtileandsurface.example", "CGC1519462", "Daniel Okafor",
             "ITS-24-311", "February 20, 2024", "60 days", True, "14 weeks from notice to proceed",
             "Net 30", ADDENDA, (41000, -99500),
             [GENERIC_INCL, MOISTURE_INCL],
             ["Work outside normal hours", "Permit fees"],
             ["Pricing is based on the Construction Documents dated January 5, 2024"],
             stated_delta=4200),
    make_bid("C", "Palmetto Surface Systems Corp.", "7780 Daniels Road, Fort Myers, FL 33912",
             "(239) 555-0192", "proposals@palmettosurface.example", "CGC1523907", "Renee Castellano",
             "PSS-0224-58", "February 16, 2024", "60 days", True, "11 weeks from notice to proceed",
             "Net 45 from approved pay application", ADDENDA, (12500, -8000),
             [GENERIC_INCL, "Layout and cleaning of own work"],
             ["Work outside normal hours", "Painting or sealing of non-flooring surfaces"],
             ["Pricing assumes a single mobilization for each section",
              "Pricing is budgetary only and not a firm offer",
              "Alternate A: ADD $12,500 (polished concrete in lieu of luxury vinyl tile, 09 65 40)",
              "Alternate B: DEDUCT $8,000 (delete resilient athletic finishes, 09 65 67)",
              "An allowance of $5,000 is included for substrate patching; actual cost will be "
              "billed against the allowance",
              "Material price increases after the validity period will be passed through",
              "Moisture mitigation and ASTM F 1869 / F 2170 substrate testing are excluded"],
             allowance=5000),
    make_bid("D", "Sandbar Flooring Contractors", "311 Cleveland Avenue, Fort Myers, FL 33901",
             "(239) 555-0116", "office@sandbarflooring.example", "CFC1330754", "Tomas Reyes",
             "SFC-1873", "February 18, 2024", "60 days", True, "13 weeks from notice to proceed",
             "Net 30", [], (36000, -95000),
             [GENERIC_INCL, MOISTURE_INCL],
             ["Patching of substrate beyond 1/8 inch", "Overtime and premium time"],
             ["Pricing is based on the Construction Documents dated January 5, 2024"]),
    make_bid("E", "Mangrove Interiors Group", "905 Sanibel-Captiva Road, Sanibel, FL 33957",
             "(239) 555-0163", "hello@mangroveinteriors.example", "CGC1611288", "Priya Raman",
             "MIG-0219-A", "February 19, 2024", "15 days", False, "10 weeks from notice to proceed",
             "Net 30", ADDENDA, (39500, -97500),
             [GENERIC_INCL, MOISTURE_INCL],
             ["Patching of substrate beyond 1/8 inch", "Work outside normal hours"],
             ["Section 09 65 67 is priced per plans dated December 1, 2023"],
             notes={"A1": "Priced per plans dated December 1, 2023"}),
]
BY_KEY = {b["key"]: b for b in BIDS}
for _b in BIDS:
    _b["slug"] = slugify(_b["company_name"])


def money(x):
    return f"${x:,.2f}"


def signed(a):
    return f"ADD {money(a)}" if a >= 0 else f"DEDUCT {money(-a)}"


def ext_of(b, spec):
    return next(i for i in b["line_items"] if i["spec_section"] == spec)["extended_price"]


# ---------------------------------------------------------------- PDF plumbing
def font_dir():
    for d in (Path("C:/Windows/Fonts"), Path("/usr/share/fonts/truetype/msttcorefonts")):
        if (d / "arial.ttf").exists():
            return d
    raise SystemExit("arial.ttf not found; needed for the em dash in the footer")


class Doc(FPDF):
    footer_text = FOOTER

    def footer(self):
        self.set_y(-12)
        self.set_font("F", "", 7)
        self.set_text_color(90, 90, 90)
        self.cell(0, 4, self.footer_text, align="C")
        self.set_text_color(0, 0, 0)


def new_doc(footer=FOOTER, size=9):
    d = Doc(format="Letter")
    d.footer_text = footer
    fd = font_dir()
    d.add_font("F", "", str(fd / "arial.ttf"))
    d.add_font("F", "B", str(fd / "arialbd.ttf"))
    d.set_creation_date(FIXED_DATE)
    d.set_margins(15, 14, 15)
    d.set_auto_page_break(True, 16)
    d.add_page()
    d.set_font("F", "", size)
    d.base = size
    return d


def text(d, s, bold=False, size=None, h=None, gap=0):
    d.set_font("F", "B" if bold else "", size or d.base)
    d.multi_cell(0, h or (size or d.base) * 0.5, s, new_x="LMARGIN", new_y="NEXT")
    d.ln(gap)


def bullets(d, title, items, h=None):
    text(d, title, bold=True, h=h)
    for i in items:
        text(d, "\u2022 " + i, h=h)
    d.ln(1.5)


def letterhead(d, b):
    text(d, b["company_name"], bold=True, size=15, h=7)
    text(d, b["street"], h=4.2)
    text(d, f"Tel {b['contact_phone']}  |  {b['contact_email']}  |  FL License {b['license']}", h=4.2)
    d.ln(2)


def info_block(d, b, h=4.2):
    for s in (f"To: {GC}", f"Project: {PROJECT} (Owner: {OWNER}; Architect: {ARCHITECT}; "
              f"Project No. {PROJECT_NO})", f"Bid package: {PACKAGE}",
              f"Proposal No.: {b['proposal_no']}    Bid date: {b['bid_date']}    "
              f"Bid validity: {b['bid_validity_period']}",
              f"Contact: {b['contact_name']}"):
        text(d, s, h=h)
    d.ln(2)


W = [18, 74, 17, 12, 25, 34]


def trow(d, vals, h=5, bold=False, fill=False, span=False):
    d.set_font("F", "B" if bold else "", d.base)
    if fill:
        d.set_fill_color(225, 232, 240)
    if span:
        d.cell(sum(W), h, vals, border=1, fill=fill, new_x="LMARGIN", new_y="NEXT")
        return
    for i, (w, v) in enumerate(zip(W, vals)):
        d.cell(w, h, str(v), border=1, fill=fill, align="L" if i < 2 else "R",
               new_x="RIGHT", new_y="TOP")
    d.ln(h)


def line_table(d, b, h=5):
    trow(d, ["Spec", "Description", "Qty", "Unit", "Unit price", "Extended"], h, True, True)
    titles = dict(SECTIONS)
    done = set()
    for i in b["line_items"]:
        if i["spec_section"] not in done and i["notes"] != "Allowance":
            done.add(i["spec_section"])
            trow(d, f"{i['spec_section']} {titles[i['spec_section']]}", h, True, span=True)
        trow(d, [i["spec_section"], i["description"], f"{i['qty']:,}", i["unit"],
                 money(i["unit_price"]), money(i["extended_price"])], h)
    trow(d, ["", "BASE BID TOTAL", "", "", "", money(b["base_bid_amount"])], h, True, True)
    d.ln(3)


def alt_lines(b):
    return [f"{a['name']}: {a['description']} \u2014 {signed(a['amount'])}" for a in b["alternates"]]


def terms(d, b, addenda_blank=False, h=4.2):
    text(d, "Terms", bold=True, h=h)
    rows = [f"Bid validity: {b['bid_validity_period']}"]
    if b["bond_included"]:
        rows.append("Bond: bid and performance bond included")
    rows += [f"Schedule: {b['schedule_duration']}", f"Payment terms: {b['payment_terms']}"]
    rows.append("Addenda acknowledged: ____________________" if addenda_blank else
                "Addenda acknowledged: " + ", ".join(b["addenda_acknowledged"]))
    rows.append(INSURANCE)
    for r in rows:
        text(d, "\u2022 " + r, h=h)
    d.ln(1.5)


# ---------------------------------------------------------------- renderers
def render_form(b, two_page=False, addenda_blank=False, size=9):
    """Bid-form layout (A: 2 pages; B and D: 1 page)."""
    d = new_doc(size=size)
    h = 5 if two_page else 4.4
    letterhead(d, b)
    text(d, "SUBCONTRACTOR BID FORM", bold=True, size=11, h=6)
    info_block(d, b, h=4.2 if two_page else 3.8)
    line_table(d, b, h)
    if two_page:
        d.add_page()
    bullets(d, "Alternates (every bidder must price both)", alt_lines(b), h=h - 0.6)
    bullets(d, "Inclusions", b["scope_inclusions"], h=h - 0.6)
    bullets(d, "Exclusions", b["scope_exclusions"], h=h - 0.6)
    bullets(d, "Qualifications", b["qualifications"], h=h - 0.6)
    terms(d, b, addenda_blank, h=h - 0.6)
    text(d, f"Submitted by: {b['contact_name']}, Estimator", h=h)
    return d


def render_letter_c(b):
    """3-page proposal letter; numbered qualifications on page 3."""
    d = new_doc(size=10)
    letterhead(d, b)
    text(d, b["bid_date"], gap=3, h=5)
    text(d, f"{GC}\nAttn: Estimating\n", h=5)
    text(d, f"RE: Proposal {b['proposal_no']} \u2014 {PACKAGE}, {PROJECT}", bold=True, h=5, gap=2)
    text(d, "Dear Estimating Team:\n\nPalmetto Surface Systems Corp. is pleased to submit this proposal "
         f"for {PACKAGE} on the {CD_SET}. Our base bid for the six specification sections "
         f"is {money(b['base_bid_amount'])}. A priced schedule follows on page 2, and our "
         "qualifications and conditions are on page 3.\n\nSections covered:", h=5)
    for n, t in SECTIONS:
        text(d, f"\u2022 {n} {t}", h=5)
    text(d, f"\nThis proposal is valid for {b['bid_validity_period']}. Schedule: "
         f"{b['schedule_duration']}. Payment terms: {b['payment_terms']}. Bond: bid and performance "
         "bond included. Addenda acknowledged: Addendum 1, Addendum 2. "
         f"{INSURANCE}.\n\nSincerely,\n\n{b['contact_name']}\nSenior Estimator", h=5)
    d.add_page()
    text(d, "PRICING SCHEDULE", bold=True, size=11, h=6)
    line_table(d, b)
    bullets(d, "Inclusions", b["scope_inclusions"])
    bullets(d, "Exclusions", b["scope_exclusions"])
    d.add_page()
    text(d, "QUALIFICATIONS AND CONDITIONS", bold=True, size=11, h=6, gap=2)
    for n, q in enumerate(b["qualifications"], 1):
        text(d, f"{n}. {q}", h=5.5, gap=1)
    text(d, f"\nSubmitted by: {b['contact_name']}, Senior Estimator", h=5)
    return d


def render_letter_e(b):
    """1-page narrative business letter; prices in sentences, no table."""
    d = new_doc(size=9)
    letterhead(d, b)
    text(d, b["bid_date"], gap=2, h=4.4)
    text(d, f"{GC}, Attn: Estimating", h=4.4)
    text(d, f"RE: {PACKAGE}, {PROJECT}, Proposal {b['proposal_no']}", bold=True, h=4.4, gap=2)
    text(d, f"Dear Estimating Team: Thank you for inviting Mangrove Interiors Group to bid {PACKAGE} on the "
         f"{CD_SET}, Project No. {PROJECT_NO}. Our base bid for the work is "
         f"{money(b['base_bid_amount'])}, made up as follows.", h=4.4, gap=1.5)
    titles = dict(SECTIONS)
    for i in b["line_items"]:
        tail = (f" {b['qualifications'][0]}."
                if i["spec_section"] == "09 65 67" else "")
        text(d, f"Section {i['spec_section']} ({titles[i['spec_section']]}): "
             f"{i['description']}, {i['qty']:,} {i['unit']} at {money(i['unit_price'])} per {i['unit']}, "
             f"for {money(i['extended_price'])}.{tail}", h=4.4, gap=1)
    a, bb = b["alternates"]
    text(d, f"\nWe have priced both alternates. {a['name']}: {a['description']} \u2014 "
         f"{signed(a['amount'])}. {bb['name']}: {bb['description']} \u2014 {signed(bb['amount'])}.",
         h=4.4, gap=1.5)
    text(d, "Our price includes " + b["scope_inclusions"][0].lower() + ", and " +
         b["scope_inclusions"][1][0].lower() + b["scope_inclusions"][1][1:] + ". We exclude "
         + b["scope_exclusions"][0].lower() + " and " + b["scope_exclusions"][1].lower() + ".",
         h=4.4, gap=1.5)
    text(d, f"This proposal is valid for {b['bid_validity_period']} from the bid date. We can complete "
         f"the work in {b['schedule_duration'].replace(' from', ', measured from')}. Payment terms "
         f"are {b['payment_terms']}. We acknowledge Addendum 1 and Addendum 2. "
         f"Required insurance coverage is confirmed.", h=4.4, gap=3)
    text(d, f"Sincerely,\n\n{b['contact_name']}\nEstimator, {b['company_name']}", h=4.4)
    return d


def render_pdf_d(b, out):
    """Image-only PDF: render the form at 150 dpi, smudge the 09 67 10 extended price, embed."""
    d = render_form(b, addenda_blank=True)
    src = fitz.open(stream=bytes(d.output()), filetype="pdf")
    page = src[0]
    true_ext = ext_of(b, "09 67 10")
    hits = page.search_for(money(true_ext))
    assert len(hits) == 1, "09 67 10 extended price must be unique on the page"
    r = hits[0]
    pix = page.get_pixmap(dpi=150)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    k = 150 / 72
    x0, y0, x1, y1 = r.x0 * k - 3, r.y0 * k - 3, r.x1 * k + 1, r.y1 * k + 3
    cover = x0 + (x1 - x0) * 0.78  # hide ~78% of the digits, leave the tail visible
    g = ImageDraw.Draw(img)
    g.rectangle([x0, y0, cover, y1], fill=(35, 35, 35))
    g.ellipse([x0 - 4, y0 - 4, cover - 20, y1 + 4], fill=(55, 55, 55))
    g.ellipse([cover - 40, y0 - 5, cover + 12, y1 + 3], fill=(45, 45, 45))
    g.ellipse([x0 + 20, y1 - 7, cover - 10, y1 + 5], fill=(60, 60, 60))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    scan = FPDF(format="Letter")  # fpdf2 output is byte-stable; fitz writes a random file ID
    scan.set_creation_date(FIXED_DATE)
    scan.set_auto_page_break(False)
    scan.add_page()
    scan.image(buf, x=0, y=0, w=scan.w, h=scan.h)
    scan.output(out)
    return true_ext


def scope_sheet_blocks():
    blocks = [("h", f"BID PACKAGE SCOPE SHEET \u2014 {PACKAGE}"),
              ("p", f"From: {GC} (General Contractor)"),
              ("p", f"Project: {PROJECT}"),
              ("p", f"Owner: {OWNER}. Architect: {ARCHITECT}. Project No. {PROJECT_NO}."),
              ("p", f"Documents: {CD_SET}."),
              ("p", "Bids due: February 20, 2024."),
              ("s", "Specification sections in this package")]
    blocks += [("b", f"{n} {t}") for n, t in SECTIONS]
    blocks += [("s", "Alternates (every bidder must price both)"),
               ("b", f"{ALT_A[0]}: {ALT_A[1]}"), ("b", f"{ALT_B[0]}: {ALT_B[1]}"),
               ("p", "State each alternate as an ADD (positive) or DEDUCT (negative) amount from the base bid."),
               ("s", "Provided by the GC (do not price)"),
               ("b", "Temporary floor protection"), ("b", "Final cleaning"), ("b", "Dumpsters"),
               ("s", "Bid requirements"),
               ("b", "Acknowledge Addenda 1 and 2."),
               ("b", "Bid validity of 60 days is required."),
               ("b", "A bond is required for awards over $250,000."),
               ("b", "Section 09 65 40 requires moisture testing of concrete substrates per "
                     "ASTM F 1869 and ASTM F 2170 before installation."),
               ("b", "Quantities are each bidder's own take-offs; state any exclusion in writing.")]
    return blocks


def write_scope_sheet():
    blocks = scope_sheet_blocks()
    md = []
    for kind, t in blocks:
        md.append({"h": f"# {t}\n", "s": f"\n## {t}\n", "p": t + "\n", "b": f"- {t}"}[kind])
    (GT_DIR / "scope_sheet.md").write_text("\n".join(md).replace("\n\n\n", "\n\n") + "\n", encoding="utf-8")
    d = new_doc(size=10)
    for kind, t in blocks:
        if kind == "h":
            text(d, t, bold=True, size=14, h=8, gap=3)
        elif kind == "s":
            d.ln(2)
            text(d, t, bold=True, size=11, h=6)
        else:
            text(d, ("\u2022 " if kind == "b" else "") + t, h=5.5)
    d.output(str(BIDS_DIR / "00 - Bid Package Scope Sheet.pdf"))


def defect(bid, dtype, where, tab, ev):
    b = BY_KEY[bid]
    return dict(bid=bid, slug=b["slug"], company_name=b["company_name"], defect_type=dtype,
                where=where, expected_tabulator_behaviour=tab, expected_evaluator_behaviour=ev)


def defects():
    return [
        defect("B", "silent_omission", "09 65 13 Resilient Base and Accessories: no line item and no "
               "exclusion or mention anywhere in the bid",
               "Extract only the lines present; do not invent a 09 65 13 line.",
               "coverage_map 09 65 13 = SILENT (most dangerous); exclusion_scores CRITICAL (spec-required, "
               "uncarried, >1% of bid / >$5K); value it from another bidder's 09 65 13 line item and add it "
               "to the adjusted total as a documented adjustment."),
        defect("B", "math_error", "Stated base bid is $4,200 higher than the sum of the line items",
               "Record base_bid_amount as stated; flag [MATH ERROR: line items sum to $X, bid states $Y]; "
               "workbook reconciliation row shows DISCREPANCY of -$4,200.",
               "Flag the discrepancy, do not correct it; request clarification before award."),
        defect("C", "buried_exclusion", "Qualification #7 (page 3): moisture mitigation and ASTM F 1869 / "
               "F 2170 substrate testing excluded; absent from the exclusions list",
               "Capture qualification #7 verbatim in qualifications; do not drop it for not being in the "
               "exclusions list.",
               "coverage_map for moisture testing (09 65 40) = EXCLUDED; exclusion_scores CRITICAL if "
               "estimated >1% of bid or >$5K, otherwise SIGNIFICANT; spec requires the testing, so add its "
               "value (professional judgment, flagged as estimated) to the adjusted price."),
        defect("C", "budget_pricing", "Qualification #2: pricing is budgetary only and not a firm offer",
               "Capture the qualification verbatim; do not present the base bid as firm.",
               "Budget pricing is not a firm bid: not awardable. Segregate from firm bids with a caveat "
               "and do not rank it as an award candidate on price."),
        defect("C", "alternate_in_qualifications", "Qualifications #3 and #4: 'Alternate A: ADD $12,500' "
               "and 'Alternate B: DEDUCT $8,000'",
               "Populate alternates[] with signed amounts (+12500, -8000) and keep the qualification text; "
               "the xlsx VE parser also picks them up.",
               "Preserve the sign; never mix alternate amounts into the base bid; compare both alternates "
               "against the other bidders."),
        defect("C", "allowance", "Line 'Allowance - substrate patching' $5,000 (included in the base bid)",
               "Record in allowances[] and as a line item with notes 'Allowance'.",
               "Track as an allowance, not firm scope; adjust for allowance overrun risk and confirm units."),
        defect("C", "unit_price_outlier", "09 30 00 tiling unit prices ($48.00 and $33.00/SF vs $20.00 to "
               "$22.00 and $14.00 to $15.00/SF for the others)",
               "Extract unit prices and units exactly as written.",
               "Flag unit price outlier (>2x median) on 09 30 00 and calculate the exposure range."),
        defect("D", "unclear_value", "09 67 10 extended price is hidden under an opaque smudge on the scan",
               f"Record extended_price as '{UNCLEAR}' (never guess, never 0); text layer is empty so "
               "vision is required; true value is in ground_truth_hidden.",
               "Flag the value as unclear, request clarification, and do not treat it as zero or silently "
               "back-solve it from the base bid."),
        defect("D", "missing_addenda", "Addenda acknowledgement line is blank",
               "addenda_acknowledged = [] (not acknowledged).",
               "Flag no addenda acknowledgment (red flag / bid completeness); obtain written "
               "acknowledgement of Addenda 1 and 2 before award."),
        defect("E", "short_validity", "Proposal valid for only 15 days (60 days required)",
               "bid_validity_period = '15 days'.",
               "Flag validity below 30 days and below the 60 days required; expires before a typical award "
               "date; request extension."),
        defect("E", "no_bond", "Bond not mentioned (required for awards over $250,000)",
               "bond_included = false.",
               "Flag no bond on a bonded award (red flag); require a bond or exclude from award."),
        defect("E", "stale_drawing_date", "09 65 67 priced 'per plans dated December 1, 2023'; current set "
               "is dated January 5, 2024",
               "Capture the phrase verbatim in the line note and qualifications.",
               "Flag wrong drawing date: the price may not reflect the current set; verify against "
               "Addenda 1 and 2 and the January 5, 2024 documents."),
    ]


def to_json(b, hidden=None):
    out = {k: b[k] for k in (
        "company_name", "contact_name", "contact_phone", "contact_email", "bid_date",
        "bid_validity_period", "base_bid_amount", "bond_included", "schedule_duration",
        "payment_terms", "addenda_acknowledged", "line_items", "alternates", "scope_inclusions",
        "scope_exclusions", "qualifications", "allowances", "insurance_confirmed")}
    out["line_items"] = [dict(i) for i in b["line_items"]]
    if hidden:
        out["ground_truth_hidden"] = hidden
        for i in out["line_items"]:
            if i["spec_section"] == "09 67 10":
                i["extended_price"] = UNCLEAR
    return out


def main():
    BIDS_DIR.mkdir(parents=True, exist_ok=True)
    GT_BIDS.mkdir(parents=True, exist_ok=True)
    write_scope_sheet()
    for n, b in enumerate(BIDS, 1):
        fname = re.sub(r"[^A-Za-z0-9 ]", "", b["company_name"].replace("&", "and"))
        out = BIDS_DIR / f"{n:02d} - {fname}.pdf"
        hidden = None
        if b["key"] == "D":
            true_ext = render_pdf_d(b, str(out))
            hidden = {"spec_section": "09 67 10", "field": "extended_price", "value": true_ext}
        else:
            doc = {"A": lambda: render_form(b, two_page=True, size=9.5),
                   "B": lambda: render_form(b, size=9),
                   "C": lambda: render_letter_c(b),
                   "E": lambda: render_letter_e(b)}[b["key"]]()
            doc.output(str(out))
        (GT_BIDS / f"{b['slug']}.json").write_text(
            json.dumps(to_json(b, hidden), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("wrote", out.name)
    (GT_DIR / "defects.json").write_text(
        json.dumps(defects(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
