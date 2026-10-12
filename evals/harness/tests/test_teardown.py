"""harness.yaml `allow_urls` and `teardown`: read into the case; the teardown runs in the workspace and never raises."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cases import load_case  # noqa: E402
from runner import run_teardown  # noqa: E402


def make_case(root: Path, harness_yaml: str, teardown_sh: str | None = None) -> Path:
    case = root / "case"
    (case / "graders").mkdir(parents=True)
    (case / "prompt.md").write_text("---\nname: case\n---\n\n/construction:x\n", encoding="utf-8")
    (case / "harness.yaml").write_text(harness_yaml, encoding="utf-8")
    if teardown_sh is not None:
        (case / "teardown.sh").write_text(teardown_sh, encoding="utf-8", newline="\n")
    return case


class Teardown(unittest.TestCase):
    def test_fields_are_read(self):
        with tempfile.TemporaryDirectory() as d:
            case = load_case(make_case(Path(d), 'allow_urls: ["http://127.0.0.1:47817/"]\nteardown: teardown.sh\n', ""))
            self.assertEqual(case.allow_urls, ["http://127.0.0.1:47817/"])
            self.assertEqual(case.teardown, Path(d) / "case" / "teardown.sh")

    def test_absent_fields_mean_none(self):
        with tempfile.TemporaryDirectory() as d:
            case = load_case(make_case(Path(d), "checks: []\n"))
            self.assertEqual((case.allow_urls, case.teardown), ([], None))
            self.assertEqual(run_teardown(case, Path(d)), "")

    def test_it_runs_in_the_workspace(self):
        with tempfile.TemporaryDirectory() as d:
            case = load_case(make_case(Path(d), "teardown: teardown.sh\n", "echo stopped > marker.txt\necho done\n"))
            ws = Path(d) / "ws"
            ws.mkdir()
            out = run_teardown(case, ws)
            self.assertTrue(out.startswith("exit 0"), out)
            self.assertEqual((ws / "marker.txt").read_text().strip(), "stopped")

    def test_a_failing_teardown_is_reported_not_raised(self):
        with tempfile.TemporaryDirectory() as d:
            case = load_case(make_case(Path(d), "teardown: missing.sh\n"))
            out = run_teardown(case, Path(d))
            self.assertNotIn("exit 0", out)


if __name__ == "__main__":
    unittest.main()
