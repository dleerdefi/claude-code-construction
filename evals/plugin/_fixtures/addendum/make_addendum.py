#!/usr/bin/env python3
"""Write the synthetic Addendum 01 used by the pe-review and rfi-drafter eval cases.

Run with: bin/construction-python evals/plugin/_fixtures/addendum/make_addendum.py

The addendum revises one door on the real A500 door schedule (door 220: leaf
width 3'-0" to 3'-6", hardware set 10 to 11) so a review of door 220 has a
known conflict with a known resolution (the addendum governs). It is clearly
labelled as an eval fixture and names no architect.
"""
from pathlib import Path

from fpdf import FPDF

OUT = Path(__file__).resolve().parent / "Addendum 01 (eval fixture).pdf"

LINES = [
    ("B", 14, "ADDENDUM NO. 1"),
    ("", 10, "Project: Sanibel Fire and Rescue Station 172 - 100% Construction Documents dated January 5, 2024"),
    ("", 10, "Commission No. 2023820"),
    ("", 10, "Date of Addendum: January 19, 2024"),
    ("", 9, "EVAL FIXTURE - fictional addendum written for a synthetic evaluation. It was not issued by the"),
    ("", 9, "project's architect and changes nothing about the real project."),
    ("", 10, ""),
    ("B", 11, "This Addendum forms part of the Contract Documents and modifies them as follows."),
    ("", 10, ""),
    ("B", 11, "ITEM 1 - DRAWINGS, SHEET A500 DOOR SCHEDULE"),
    ("", 10, "Door 220 (Second Floor): revise the door panel leaf width from 3'-0\" to 3'-6\" and revise the"),
    ("", 10, "door hardware set from 10 to 11. The leaf height (8'-0\"), leaf type (F), leaf material (WD),"),
    ("", 10, "frame type (1), frame material (HM), door/frame rating (20) and detail references are unchanged."),
    ("", 10, ""),
    ("B", 11, "ITEM 2 - BIDDING"),
    ("", 10, "Bidders shall acknowledge receipt of this Addendum on the Bid Form."),
    ("", 10, ""),
    ("", 10, "END OF ADDENDUM NO. 1"),
]


class Addendum(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 6, "EVAL FIXTURE - fictional addendum for a synthetic evaluation; not issued by the architect.", align="C")


def main() -> None:
    pdf = Addendum()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    for style, size, text in LINES:
        pdf.set_font("Helvetica", style, size)
        pdf.cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(OUT))
    print(f"wrote {OUT.name} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
