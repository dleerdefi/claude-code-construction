"""--no-skip: a skipped case fails the run; by default skips are shown, not failed."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from run import exit_code, parse_args  # noqa: E402


class NoSkip(unittest.TestCase):
    def test_default_counts_only_the_cases_that_ran(self):
        self.assertEqual(exit_code({"total": 3, "passed": 2, "skipped": 1}, no_skip=False), 0)
        self.assertEqual(exit_code({"total": 3, "passed": 1, "skipped": 1}, no_skip=False), 1)

    def test_no_skip_fails_on_any_skipped_case(self):
        self.assertEqual(exit_code({"total": 3, "passed": 2, "skipped": 1}, no_skip=True), 1)
        self.assertEqual(exit_code({"total": 3, "passed": 3, "skipped": 0}, no_skip=True), 0)

    def test_the_flag_parses(self):
        self.assertTrue(parse_args(["--no-skip", "--tag", "agentcm-mode"]).no_skip)
        self.assertFalse(parse_args([]).no_skip)


if __name__ == "__main__":
    unittest.main()
