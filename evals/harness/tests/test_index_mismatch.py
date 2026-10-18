"""sheet-splitter's index-mismatch check, against planted findings and traces, and the fixture it expects."""
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
          "index": {"number": "S101", "title": "FOUNDATION PLAN"}, "suggested_rfi": None}
TITLE = {"sheet": "A-101", "kind": "title", "title_block": {"number": "A-101", "title": "FIRST FLOOR PLAN"},
         "index": {"number": "A-101", "title": "FIRST FLOOR REFLECTED CEILING PLAN"},
         "suggested_rfi": "The drawing index on G-001 lists A-101 as FIRST FLOOR REFLECTED CEILING PLAN; its title block "
                          "reads FIRST FLOOR PLAN. Please confirm the correct title."}


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

    def say(self, final, result=True):
        lines = [{"type": "assistant_text", "text": final}]
        if result:
            lines.append({"type": "result", "subtype": "success", "result": final[:4000]})  # runner's RESULT_TEXT_LIMIT
        self.trace.write_text("\n".join(json.dumps(e) for e in lines) + "\n", encoding="utf-8")

    def run_check(self):
        return subprocess.run([sys.executable, str(CHECK)], capture_output=True, text=True,
                              env=dict(os.environ, EVAL_WORKSPACE=str(self.ws), EVAL_TRACE=str(self.trace)))

    def test_passes_with_both_mismatches_the_rfi_and_the_file_named(self):
        self.finding([NUMBER, TITLE])
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("score: 1.0", r.stdout)

    def test_passes_when_sheet_is_left_out_and_the_last_text_names_the_file(self):
        self.finding([{k: v for k, v in NUMBER.items() if k != "sheet"}, {k: v for k, v in TITLE.items() if k != "sheet"}])
        self.say(f"Wrote {NAME}", result=False)
        self.assertEqual(self.run_check().returncode, 0)

    def test_passes_when_the_name_is_past_the_cut_off_result(self):
        self.finding([NUMBER, TITLE])
        self.say("| sheet | title |\n" * 400 + f"Findings: {NAME}")
        self.assertEqual(self.run_check().returncode, 0)

    def test_fails_without_a_finding(self):
        r = self.run_check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("score: 0.1", r.stdout)  # only "no mismatch on G-001 or A-201" holds

    def test_fails_when_the_summary_does_not_name_the_file(self):
        self.finding([NUMBER, TITLE])
        self.say("Split 4 sheets; the drawing index disagrees on two of them.")
        r = self.run_check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL final message names the finding's file", r.stdout)

    def test_fails_without_the_suggested_rfi(self):
        self.finding([NUMBER, dict(TITLE, suggested_rfi=None)])
        r = self.run_check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL suggested RFI on the A-101 title", r.stdout)

    def test_fails_on_the_bookmark_reported_as_an_index_mismatch(self):
        bookmark = {"sheet": "A-201", "kind": "title", "title_block": {"number": "A-201", "title": "SECOND FLOOR PLAN"},
                    "index": {"number": "A-201", "title": "2ND FLR"}, "suggested_rfi": "Confirm the title."}
        self.finding([NUMBER, TITLE, bookmark])
        r = self.run_check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("['A201']", r.stdout)

    def test_every_file_with_mismatches_must_be_named(self):
        other = "2026-10-17_drawing_index_mismatch_9f8e7d6c.json"
        self.finding([NUMBER], name=NAME)
        self.finding([TITLE], name=other)
        self.assertEqual(self.run_check().returncode, 1)
        self.say(f"Findings: {NAME} and {other}")
        self.assertEqual(self.run_check().returncode, 0)


class Fixture(unittest.TestCase):
    """The check's planted values are what the committed drawing set prints."""

    def test_cover_index_and_title_blocks(self):
        import fitz
        with fitz.open(ARCH_SET) as doc:
            cover, a101, a201, s101 = (page.get_text() for page in doc)
        for row in ("S101", "FIRST FLOOR REFLECTED CEILING PLAN", "A-201", "SECOND FLOOR PLAN"):
            self.assertIn(row, cover)
        self.assertIn("FIRST FLOOR PLAN", a101)
        self.assertNotIn("REFLECTED", a101)
        self.assertIn("SECOND FLOOR PLAN", a201)
        self.assertIn("S-101", s101)


if __name__ == "__main__":
    unittest.main()
