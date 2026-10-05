"""--regrade: a saved run is rebuilt from its folder and re-graded with the current graders."""
import asyncio
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from cases import Case, Grader  # noqa: E402
from graders import JudgeOptions  # noqa: E402
from regrade import KEPT, load_saved_run, regrade_run  # noqa: E402
from report import write_created  # noqa: E402


def _save_run(run_dir: Path, workspace: Path, stored: list[dict]) -> None:
    run_dir.mkdir(parents=True)
    trace = [
        {"type": "tool_use", "id": "1", "name": "Bash", "input": {"command": 'ls "02 - Specifications/Specification Sections"'}},
        {"type": "tool_use", "id": "2", "name": "Bash", "input": {"command": 'pdf_text.py "02 - Specifications/Specification Sections/09 30 00.pdf"'}},
        {"type": "tool_use", "id": "3", "name": "Write", "input": {"file_path": str(workspace / "out.json"), "content": "{}"}},
        {"type": "result", "subtype": "success", "result": "done"},
    ]
    (run_dir / "trace.jsonl").write_text("\n".join(json.dumps(e) for e in trace) + "\n", encoding="utf-8")
    (run_dir / "guard_log.json").write_text("[]", encoding="utf-8")
    (run_dir / "graders.json").write_text(json.dumps(stored), encoding="utf-8")
    (run_dir / "run.json").write_text(json.dumps({
        "case": "demo", "run_index": 1, "workspace": str(workspace), "score": 0.5, "elapsed_s": 10.0,
        "num_turns": 3, "cost_usd": 0.2, "subtype": "success", "is_error": False, "error": "",
        "created_files": ["out.json"], "guard_denials": []}), encoding="utf-8")


def _case(graders: list[Grader]) -> Case:
    return Case(name="demo", dir=Path("demo"), prompt="", meta={}, scaffold=None, add_dirs=[], graders=graders)


def _grader(name, type, weight=1, **fields) -> Grader:
    return Grader(name=name, type=type, fields={"weight": weight, **fields}, body="rubric")


class Regrade(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.workspace = self.tmp / "ws"
        self.workspace.mkdir()
        (self.workspace / "out.json").write_text("{}", encoding="utf-8")
        self.run_dir = self.tmp / "results" / "demo" / "run-1"
        _save_run(self.run_dir, self.workspace, [
            {"name": "output", "type": "file_exists", "weight": 1, "passed": True, "detail": "1 file", "score": None},
            {"name": "judged", "type": "llm", "weight": 1, "passed": False, "detail": "0/1 votes", "score": None},
        ])

    def _regrade(self, graders):
        run, stored, source = load_saved_run(self.run_dir, "demo")
        return asyncio.run(regrade_run(_case(graders), run, stored, JudgeOptions(), HERE.parents[1],
                                       self.run_dir / "trace.jsonl", rejudge=False, source=source))

    def test_saved_run_is_rebuilt(self):
        run, stored, source = load_saved_run(self.run_dir, "demo")
        self.assertEqual(source, "workspace")
        self.assertEqual(run.run_index, 1)
        self.assertEqual(run.created_files, ["out.json"])
        self.assertEqual(len(run.tool_uses), 3)
        self.assertEqual(set(stored), {"output", "judged"})

    def test_new_trace_grader_is_evaluated_from_the_saved_trace(self):
        results = self._regrade([
            _grader("reads-specs", "tool_used", 2, tool="Bash", input_match=r"Specification Sections[\s\S]*\.pdf"),
            _grader("no-helper", "tool_used", tool="Write", input_match=r"\.py\"", min=0, max=0),
        ])
        by_name = {r.name: r for r in results}
        self.assertTrue(by_name["reads-specs"].passed)
        self.assertTrue(by_name["no-helper"].passed)
        self.assertNotIn(KEPT, by_name["reads-specs"].detail)

    def test_workspace_grader_is_reevaluated_while_the_workspace_exists(self):
        results = self._regrade([_grader("output", "file_exists", path="out.json")])
        self.assertTrue(results[0].passed)
        self.assertNotIn(KEPT, results[0].detail)

    def test_workspace_grader_keeps_its_verdict_when_the_workspace_is_gone(self):
        os.remove(self.workspace / "out.json")
        self.workspace.rmdir()
        results = self._regrade([
            _grader("output", "file_exists", path="out.json"),
            _grader("brand-new", "file_exists", path="other.json"),
        ])
        self.assertTrue(results[0].passed)
        self.assertIn(KEPT, results[0].detail)
        self.assertFalse(results[1].passed)
        self.assertIn("not evaluated", results[1].detail)

    def test_snapshot_stands_in_for_a_deleted_workspace(self):
        run, _, _ = load_saved_run(self.run_dir, "demo")
        snap = write_created(self.tmp / "results", run)   # what write_run does before cleanup
        self.assertEqual(snap, self.run_dir / "workspace")
        self.assertTrue((snap / "out.json").is_file())
        os.remove(self.workspace / "out.json")
        self.workspace.rmdir()
        run, _, source = load_saved_run(self.run_dir, "demo")
        self.assertEqual(source, "snapshot")
        self.assertEqual(run.workspace, snap)
        results = self._regrade([
            _grader("output", "file_exists", path="out.json"),
            _grader("brand-new", "file_exists", path="other.json"),
        ])
        self.assertTrue(results[0].passed)
        self.assertIn("on the snapshot", results[0].detail)
        self.assertNotIn(KEPT, results[0].detail)
        self.assertEqual(run.modified_files, [])
        self.assertFalse(results[1].passed)          # evaluated, not kept: the file really is absent
        self.assertIn("on the snapshot", results[1].detail)

    def test_llm_grader_keeps_its_verdict_without_rejudge(self):
        results = self._regrade([_grader("judged", "llm")])
        self.assertFalse(results[0].passed)
        self.assertIn(KEPT, results[0].detail)


if __name__ == "__main__":
    unittest.main()
