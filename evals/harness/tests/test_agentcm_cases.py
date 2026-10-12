"""The generated agentcm-mode cases grade what they claim: every check compiles, and the path graders see a
file read whichever separator the path has (Windows runs read `.construction\\specs\\...`, JSON-escaped in
the trace)."""
import py_compile
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from cases import load_cases  # noqa: E402
from graders import grade_regex  # noqa: E402
from runner import RunResult  # noqa: E402

EVALS = HERE.parent / "plugin"
# grader name -> the parts of a path it must see read
READS = {
    "agentcm-mode": (".construction", "project.yaml"),
    "agentcm-files": (".construction", "sheets", "A-101.tsv"),
    "reads-specs": (".construction", "specs", "08-11-13.txt"),
    "reads-sheet-index": (".construction", "index", "sheet_index.yaml"),
}
# grader name -> the parts of a path it must see as a violation
FORBIDS = {"no-graph-export": (".construction", "rasters", "A-101.png")}


class Checks(unittest.TestCase):
    def test_every_case_check_compiles(self):
        checks = sorted(EVALS.glob("*/checks/*.py"))
        self.assertTrue(checks)
        with tempfile.TemporaryDirectory() as tmp:
            for i, f in enumerate(checks):
                with self.subTest(check=f.relative_to(EVALS).as_posix()):
                    py_compile.compile(str(f), cfile=str(Path(tmp) / f"{i}.pyc"), doraise=True)


def reading(path):
    return RunResult(case="t", run_index=1, workspace=Path("."),
                     trace=[{"type": "tool_use", "name": "Read", "input": {"file_path": path}}])


def both_ways(parts):
    return {"posix": "/ws/" + "/".join(parts), "windows": "C:\\ws\\" + "\\".join(parts)}


class PathGraders(unittest.TestCase):
    def setUp(self):
        self.graders = [(c.name, g) for c in load_cases(EVALS) if "agentcm-mode" in c.tags for g in c.graders
                        if g.type == "regex" and g.name in {**READS, **FORBIDS}]

    def test_every_path_grader_is_covered(self):
        self.assertEqual({g.name for _, g in self.graders}, set(READS) | set(FORBIDS))

    def test_a_read_passes_with_either_separator(self):
        for case, g in self.graders:
            if g.name in READS:
                for sep, path in both_ways(READS[g.name]).items():
                    with self.subTest(case=case, grader=g.name, sep=sep):
                        self.assertTrue(grade_regex(g, reading(path)).passed)
                with self.subTest(case=case, grader=g.name, sep="nothing read"):
                    self.assertFalse(grade_regex(g, reading("/ws/README.md")).passed)

    def test_a_forbidden_path_fails_with_either_separator(self):
        for case, g in self.graders:
            if g.name in FORBIDS:
                for sep, path in both_ways(FORBIDS[g.name]).items():
                    with self.subTest(case=case, grader=g.name, sep=sep):
                        self.assertFalse(grade_regex(g, reading(path)).passed)
                self.assertTrue(grade_regex(g, reading("/ws/README.md")).passed)


if __name__ == "__main__":
    unittest.main()
