"""sheet-splitter's index-mismatch check, against planted findings, issues and traces, and the fixture it expects."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[2] / "plugin"
CHECK = PLUGIN / "sheet-splitter" / "checks" / "index_mismatch.py"
ARCH_SET = PLUGIN / "_fixtures" / "sample-project" / "01 - Drawings" / "Architectural & Structural" / "Arch Set.pdf"
NAME = "2026-10-17_drawing_index_mismatch_0a1b2c3d.json"

NUMBER = {"sheet": "S-101", "kind": "number", "title_block": {"number": "S-101", "title": "FOUNDATION PLAN"},
          "index": {"number": "S101", "title": "FOUNDATION PLAN"}, "suggested_rfi": None, "issue_id": None}
TITLE = {"sheet": "A-101", "kind": "title", "title_block": {"number": "A-101", "title": "FIRST FLOOR PLAN"},
         "index": {"number": "A-101", "title": "FIRST FLOOR REFLECTED CEILING PLAN"},
         "suggested_rfi": "The drawing index on G-001 lists A-101 as FIRST FLOOR REFLECTED CEILING PLAN; its title block "
                          "reads FIRST FLOOR PLAN. Please confirm the correct title.", "issue_id": "ISS-2026-0001"}
MISSING = {"sheet": "S-201", "kind": "not_in_set", "title_block": None,
           "index": {"number": "S-201", "title": "ROOF FRAMING PLAN"},
           "suggested_rfi": "The drawing index on G-001 lists S-201 ROOF FRAMING PLAN, but the set does not include it.",
           "issue_id": "ISS-2026-0002"}
ARCH_GAP = {"kind": "sheets_not_in_folder", "discipline": "A", "sheets": ["A-301", "A-401"], "listed": 4,
            "note": "2 of 4 A sheets aren't in the folder: A-301, A-401. Check whether a PDF wasn't added.",
            "suggested_rfi": None, "issue_id": None}
LANDSCAPE = {"kind": "sheets_not_in_folder", "discipline": "L", "sheets": ["L-101", "L-501"], "listed": 2,
             "note": "2 of 2 L sheets aren't in the folder: L-101, L-501. Check whether a PDF wasn't added.",
             "suggested_rfi": None, "issue_id": None}
ALL = [NUMBER, TITLE, MISSING, ARCH_GAP, LANDSCAPE]
ARCH = "A-301 and A-401: one folder finding (2 of 4), no RFI, no issue"
LAND = "L-101 and L-501: one folder finding (2 of 2), no RFI, no issue"


def issue(n, sheets, description, source="sheet-splitter"):
    return {"id": f"ISS-2026-{n:04d}", "source_skill": source, "severity": "conflict", "status": "open",
            "description": description, "location": {"sheets": sheets}, "potential_rfi_subject": ""}


def not_in_set(number, title, rfi=True):
    return {"sheet": number, "kind": "not_in_set", "title_block": None, "index": {"number": number, "title": title},
            "suggested_rfi": f"The drawing index on G-001 lists {number} {title}, but the set does not include it."
            if rfi else None, "issue_id": None}


ISSUE_TITLE = issue(1, ["G-001", "A-101"], TITLE["suggested_rfi"])
ISSUE_MISSING = issue(2, ["G-001", "S-201"], MISSING["suggested_rfi"])


class IndexMismatch(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.ws = Path(tmp.name) / "ws"
        self.ws.mkdir()
        self.trace = Path(tmp.name) / "trace.jsonl"
        self.say(f"Findings: .construction/skills/sheet-splitter/findings/{NAME}")

    def finding(self, mismatches, name=NAME):
        d = self.ws / ".construction" / "skills" / "sheet-splitter" / "findings"
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(json.dumps({"id": "0a1b2c3d", "skill": "sheet-splitter", "type": "drawing_index_mismatch",
                                          "data": {"index_sheet": "G-001", "mismatches": mismatches}}), encoding="utf-8")

    def issues(self, *records):
        d = self.ws / ".construction" / "skills" / "issues"
        d.mkdir(parents=True, exist_ok=True)
        for r in records:
            (d / f"{r['id']}.json").write_text(json.dumps(r), encoding="utf-8")

    def complete(self):
        self.finding(ALL)
        self.issues(ISSUE_TITLE, ISSUE_MISSING)

    def say(self, final, result=True):
        lines = [{"type": "assistant_text", "text": final}]
        if result:
            lines.append({"type": "result", "subtype": "success", "result": final[:4000]})  # runner's RESULT_TEXT_LIMIT
        self.trace.write_text("\n".join(json.dumps(e) for e in lines) + "\n", encoding="utf-8")

    def run_check(self):
        return subprocess.run([sys.executable, str(CHECK)], capture_output=True, text=True,
                              env=dict(os.environ, EVAL_WORKSPACE=str(self.ws), EVAL_TRACE=str(self.trace)))

    def assert_fails_on(self, part):
        r = self.run_check()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn(f"FAIL {part}", r.stdout)

    def test_passes_with_every_mismatch_rfi_issue_folder_finding_and_the_file_named(self):
        self.complete()
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("score: 1.0", r.stdout)

    def test_passes_when_sheet_is_left_out_and_the_last_text_names_the_file(self):
        self.finding([{k: v for k, v in m.items() if k != "sheet"} for m in (NUMBER, TITLE, MISSING)]
                     + [ARCH_GAP, LANDSCAPE])
        self.issues(ISSUE_TITLE, ISSUE_MISSING)
        self.say(f"Wrote {NAME}", result=False)
        self.assertEqual(self.run_check().returncode, 0)

    def test_passes_when_the_name_is_past_the_cut_off_result(self):
        self.complete()
        self.say("| sheet | title |\n" * 400 + f"Findings: {NAME}")
        self.assertEqual(self.run_check().returncode, 0)

    def test_issue_found_by_its_description_alone(self):
        self.finding(ALL)
        self.issues(issue(1, [], "Index lists A101 with another title"), issue(2, [], "Sheet S 201 is not in the set"))
        self.assertEqual(self.run_check().returncode, 0)

    def test_folder_finding_counted_in_other_words_passes(self):
        self.finding([NUMBER, TITLE, MISSING, dict(ARCH_GAP, note="2 of the 4 A sheets on the index are not in the "
                                                                    "folder (A 301, A.401)."), LANDSCAPE])
        self.issues(ISSUE_TITLE, ISSUE_MISSING)
        self.assertEqual(self.run_check().returncode, 0)

    def test_fails_without_a_finding(self):
        r = self.run_check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("score: 0.05", r.stdout)  # only "no mismatch on G-001 or A-201" holds

    def test_fails_when_the_summary_does_not_name_the_file(self):
        self.complete()
        self.say("Split 4 sheets; the drawing index disagrees on three of them.")
        self.assert_fails_on("final message names the finding's file")

    def test_fails_without_the_title_rfi(self):
        self.finding([NUMBER, dict(TITLE, suggested_rfi=None), MISSING, ARCH_GAP, LANDSCAPE])
        self.issues(ISSUE_TITLE, ISSUE_MISSING)
        self.assert_fails_on("suggested RFI on the A-101 title")

    def test_one_sheet_missing_from_a_complete_discipline_needs_its_rfi(self):
        for mismatches in ([NUMBER, TITLE, ARCH_GAP, LANDSCAPE],
                           [NUMBER, TITLE, dict(MISSING, suggested_rfi=None), ARCH_GAP, LANDSCAPE]):
            with self.subTest(n=len(mismatches)):
                self.finding(mismatches)
                self.issues(ISSUE_TITLE, ISSUE_MISSING)
                self.assert_fails_on("S-201 listed but not in the set, with a suggested RFI")

    def test_fails_when_the_number_note_gets_an_rfi_or_an_issue(self):
        self.finding([dict(NUMBER, suggested_rfi="Please confirm the sheet number."), TITLE, MISSING, ARCH_GAP, LANDSCAPE])
        self.issues(ISSUE_TITLE, ISSUE_MISSING)
        self.assert_fails_on("S-101 is a note: no suggested RFI, no issue")
        self.finding(ALL)
        self.issues(issue(3, ["G-001", "S-101"], "The index writes S-101 as S101."))
        self.assert_fails_on("S-101 is a note: no suggested RFI, no issue")

    def test_fails_without_the_issues_or_with_another_skills(self):
        self.finding(ALL)
        self.assert_fails_on("issues from sheet-splitter for A-101 and S-201")
        self.issues(dict(ISSUE_TITLE, source_skill="pe-review"), dict(ISSUE_MISSING, source_skill="pe-review"))
        self.assert_fails_on("issues from sheet-splitter for A-101 and S-201")

    def test_half_a_discipline_missing_is_one_folder_finding_without_rfis(self):
        per_sheet_rfis = [not_in_set("A-301", "BUILDING SECTIONS"), not_in_set("A-401", "ENLARGED PLANS")]
        per_sheet_notes = [not_in_set("A-301", "BUILDING SECTIONS", rfi=False),
                           not_in_set("A-401", "ENLARGED PLANS", rfi=False)]
        summary_rfi = dict(ARCH_GAP, suggested_rfi="The drawing index on G-001 lists 2 sheets the set does not include: "
                                                   "A-301, A-401. Please issue them.")
        for name, arch in (("missing", []), ("one RFI per sheet", per_sheet_rfis), ("one note per sheet", per_sheet_notes),
                           ("a summary RFI", [summary_rfi]), ("no count", [dict(ARCH_GAP, note="A-301, A-401 missing")]),
                           ("the finding plus per-sheet notes", [ARCH_GAP] + per_sheet_notes)):
            with self.subTest(name):
                self.finding([NUMBER, TITLE, MISSING, LANDSCAPE] + arch)
                self.issues(ISSUE_TITLE, ISSUE_MISSING)
                self.assert_fails_on(ARCH)

    def test_fails_on_an_issue_for_half_a_discipline(self):
        self.finding(ALL)
        for extra in (issue(3, ["G-001", "A-301", "A-401"], "Two sheets the set does not include."),
                      issue(3, ["G-001"], "2 of 4 A sheets aren't in the folder.")):
            with self.subTest(description=extra["description"]):
                self.issues(ISSUE_TITLE, ISSUE_MISSING, extra)
                self.assert_fails_on(ARCH)

    def test_a_whole_discipline_missing_is_one_folder_finding_without_rfis(self):
        per_sheet = [not_in_set("L-101", "LANDSCAPE PLAN", rfi=False), not_in_set("L-501", "LANDSCAPE DETAILS", rfi=False)]
        for name, land in (("missing", []), ("one note per sheet", per_sheet),
                           ("an RFI", [dict(LANDSCAPE, suggested_rfi="Please issue the landscape sheets.")]),
                           ("no count", [dict(LANDSCAPE, note="L sheets not in the folder: not checked")])):
            with self.subTest(name):
                self.finding([NUMBER, TITLE, MISSING, ARCH_GAP] + land)
                self.issues(ISSUE_TITLE, ISSUE_MISSING)
                self.assert_fails_on(LAND)

    def test_fails_on_an_issue_for_the_absent_discipline(self):
        self.finding(ALL)
        for extra in (issue(3, ["G-001", "L-101", "L-501"], "Two sheets the set does not include."),
                      issue(3, ["G-001"], "The landscape sheets are not in the set.")):
            with self.subTest(description=extra["description"]):
                self.issues(ISSUE_TITLE, ISSUE_MISSING, extra)
                self.assert_fails_on(LAND)

    def test_fails_on_the_bookmark_reported_as_an_index_mismatch(self):
        bookmark = {"sheet": "A-201", "kind": "title", "title_block": {"number": "A-201", "title": "SECOND FLOOR PLAN"},
                    "index": {"number": "A-201", "title": "2ND FLR"}, "suggested_rfi": "Confirm the title."}
        self.finding(ALL + [bookmark])
        self.issues(ISSUE_TITLE, ISSUE_MISSING)
        r = self.run_check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("['A201']", r.stdout)

    def test_every_file_with_mismatches_must_be_named(self):
        other = "2026-10-17_drawing_index_mismatch_9f8e7d6c.json"
        self.finding([NUMBER, MISSING, ARCH_GAP, LANDSCAPE], name=NAME)
        self.finding([TITLE], name=other)
        self.issues(ISSUE_TITLE, ISSUE_MISSING)
        self.assertEqual(self.run_check().returncode, 1)
        self.say(f"Findings: {NAME} and {other}")
        self.assertEqual(self.run_check().returncode, 0)


class Fixture(unittest.TestCase):
    """The check's planted values are what the committed drawing set prints."""

    def test_cover_index_and_title_blocks(self):
        import fitz
        with fitz.open(ARCH_SET) as doc:
            cover, a101, a201, s101 = (page.get_text() for page in doc)
        for row in ("S101", "FIRST FLOOR REFLECTED CEILING PLAN", "A-201", "SECOND FLOOR PLAN", "S-201", "ROOF FRAMING PLAN",
                    "A-301", "A-401", "L-101", "L-501"):
            self.assertIn(row, cover)
        sheets = (a101, a201, s101)
        for absent in ("L-", "S-201", "A-301", "A-401"):
            self.assertFalse(any(absent in page for page in sheets), absent)
        self.assertIn("FIRST FLOOR PLAN", a101)
        self.assertNotIn("REFLECTED", a101)
        self.assertIn("SECOND FLOOR PLAN", a201)
        self.assertIn("S-101", s101)


if __name__ == "__main__":
    unittest.main()
