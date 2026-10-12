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
from graders import grade_regex, grade_tool_used  # noqa: E402
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


class InlinePython(unittest.TestCase):
    PY = '"C:/plugin/bin/construction-python"'

    def graders(self):
        return [(c.name, g) for c in load_cases(EVALS) if "agentcm-mode" in c.tags for g in c.graders
                if g.name == "no-inline-python"]

    def running(self, command):
        return RunResult(case="t", run_index=1, workspace=Path("."),
                         trace=[{"type": "tool_use", "name": "Bash", "input": {"command": command}}])

    def test_every_case_has_it(self):
        cases = {c.name for c in load_cases(EVALS) if "agentcm-mode" in c.tags}
        self.assertEqual({name for name, _ in self.graders()}, cases)

    def test_inline_python_fails_and_the_toolkit_passes(self):
        inline = (f'cd "/ws"; {self.PY} -c "\nimport openpyxl\nwb=openpyxl.load_workbook(\'w.xlsx\')\n"',  # the 10:38 reconcile
                  '"$PY" -c \'import fitz\'', f"{self.PY} - <<'EOF'\nimport openpyxl\nEOF", "cat > peek.py <<'EOF'\nEOF")
        toolkit = (f'PYTHONUTF8=1 {self.PY} "C:/plugin/scripts/graph/write_finding.py" --skill s --type t --title "a -c b"',
                   f'{self.PY} "C:/plugin/scripts/pdf/pdf_text.py" "Specifications/Scanned Volume.pdf"',
                   "sh .construction/crop.sh A-601 0.1 0.06 0.44 0.346")
        for case, g in self.graders():
            for command in inline:
                with self.subTest(case=case, command=command[:40]):
                    self.assertFalse(grade_tool_used(g, self.running(command)).passed)
            for command in toolkit:
                with self.subTest(case=case, command=command[:40]):
                    self.assertTrue(grade_tool_used(g, self.running(command)).passed)


class OwnExtraction(unittest.TestCase):
    def test_the_check_takes_the_read_manuals_pages_in_no_section_from_index_md(self):
        # INDEX.md: "Specifications/Project Manual.pdf, pages in no section: 1"
        check = (EVALS / "agentcm-mode-code-researcher" / "checks" / "no_own_extraction.py").read_text(encoding="utf-8")
        self.assertIn("{'Specifications/Project Manual.pdf': [1]}", check)


class HelperScripts(unittest.TestCase):
    def writing(self, path):
        return RunResult(case="t", run_index=1, workspace=Path("."),
                         trace=[{"type": "tool_use", "name": "Write", "input": {"file_path": path, "content": "x"}}])

    def test_every_case_fails_a_python_file_written_by_the_model(self):
        cases = {c.name for c in load_cases(EVALS) if "agentcm-mode" in c.tags}
        graders = [(c.name, g) for c in load_cases(EVALS) if c.name in cases for g in c.graders if g.name == "no-helper-scripts"]
        self.assertEqual({name for name, _ in graders}, cases)
        for case, g in graders:
            with self.subTest(case=case):
                self.assertFalse(grade_tool_used(g, self.writing("C:\\ws\\work\\mk.py")).passed)
                self.assertTrue(grade_tool_used(g, self.writing("C:\\ws\\.construction\\skills\\s\\A-601-1.json")).passed)


if __name__ == "__main__":
    unittest.main()
