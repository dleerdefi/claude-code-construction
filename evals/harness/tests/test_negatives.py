"""Negative examples: a case's negatives/*.md are judged with the named llm grader and must get their expected verdict."""
import asyncio
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

import negatives  # noqa: E402
from cases import Case, Grader  # noqa: E402
from graders import JudgeOptions  # noqa: E402


def make_case(tmp: Path) -> Case:
    (tmp / "negatives").mkdir()
    (tmp / "negatives" / "confirmed.md").write_text(
        "---\ngrader: answer\nexpect: FAIL\nnote: a known-wrong answer\n---\nAll values CONFIRMED from one sheet.\n",
        encoding="utf-8")
    grader = Grader(name="answer", type="llm", fields={"weight": 3}, body="Grades must fit the evidence.")
    return Case(name="demo", dir=tmp, prompt="", meta={}, scaffold=None, add_dirs=[], graders=[grader])


class Negatives(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.case = make_case(Path(tmp.name))
        self.real = negatives._judge_once
        self.addCleanup(setattr, negatives, "_judge_once", self.real)
        self.seen = []

    def judge_says(self, verdicts):
        it = iter(verdicts)

        async def fake(rubric, material, model):
            self.seen.append((rubric, material))
            return next(it), "reason"
        negatives._judge_once = fake

    def test_loads_the_grader_name_the_expectation_and_only_the_body(self):
        [neg] = negatives.load_negatives(self.case)
        self.assertEqual((neg.grader, neg.expect, neg.material), ("answer", "FAIL", "All values CONFIRMED from one sheet."))

    def test_a_fail_verdict_is_as_expected(self):
        self.judge_says([False, False, True])
        ok, detail = asyncio.run(negatives.check_negative(self.case, negatives.load_negatives(self.case)[0],
                                                          JudgeOptions(votes=3)))
        self.assertTrue(ok, detail)
        self.assertEqual(self.seen[0], ("Grades must fit the evidence.", "All values CONFIRMED from one sheet."))

    def test_a_rubric_that_lets_it_pass_is_reported(self):
        self.judge_says([True, True, False])
        ok, detail = asyncio.run(negatives.check_negative(self.case, negatives.load_negatives(self.case)[0],
                                                          JudgeOptions(votes=3)))
        self.assertFalse(ok)
        self.assertIn("expected FAIL", detail)

    def test_an_unknown_grader_is_reported(self):
        self.case.graders = []
        ok, detail = asyncio.run(negatives.check_negative(self.case, negatives.load_negatives(self.case)[0], JudgeOptions()))
        self.assertFalse(ok)
        self.assertIn("no llm grader named 'answer'", detail)


if __name__ == "__main__":
    unittest.main()
