"""The outside-write check reads what a run left on disk, not its commands. The planted write is Python run from a
shell command, the case the command check in guard.py cannot see. Run:
bin/construction-python -m unittest discover evals/harness/tests"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import leftovers  # noqa: E402
from graders import grade_blockers  # noqa: E402
from guard import shell_write_targets  # noqa: E402
from runner import RunResult, find_bash  # noqa: E402


class Machine:
    """A small stand-in for the machine: a project's parent with the workspace and run temp folder, a system temp
    folder, a home folder and C:\\tmp, all inside one temporary directory."""

    def __init__(self, root: Path):
        self.parent = root / "construction-eval"
        self.ws = self.parent / "case-r1"
        self.run_tmp = leftovers.run_temp_for(self.ws)
        self.temp, self.home, self.c_tmp = root / "Temp", root / "home", root / "c_tmp"
        for d in (self.ws, self.run_tmp, self.temp, self.home, self.c_tmp):
            d.mkdir(parents=True)
        (self.home / ".claude.json").write_text("{}")
        (self.home / ".cache").mkdir()
        self.where = leftovers.places(self.ws, self.run_tmp, system_temp=self.temp, home=self.home, c_tmp=self.c_tmp)

    def before(self):
        return leftovers.snapshot(self.where)

    def hits(self, before):
        return leftovers.diff(self.where, before, leftovers.snapshot(self.where), own={self.ws.name, self.run_tmp.name})

    def shell(self, command):
        env = dict(os.environ, TMP=str(self.run_tmp), TEMP=str(self.run_tmp), TMPDIR=str(self.run_tmp))
        subprocess.run([find_bash(), "-c", command], cwd=self.ws, env=env, check=True, capture_output=True, timeout=60)


def py(code: str) -> str:
    """A shell command a run might issue: Python with its write inside the quotes."""
    return f'"{Path(sys.executable).as_posix()}" -c "{code}"'


class PlantedPythonWrite(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.m = Machine(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_python_write_to_the_temp_folder_is_caught_and_the_command_check_misses_it(self):
        target = (self.m.temp / "page.png").as_posix()
        command = py(f"open('{target}', 'wb').write(b'x')")
        self.assertEqual(shell_write_targets(command, str(self.m.ws)), [])  # what the command check sees: nothing
        before = self.m.before()
        self.m.shell(command)
        hits = self.m.hits(before)
        self.assertEqual([(h["place"], h["name"], h["change"], h["hard"]) for h in hits], [("temp", "page.png", "new", False)])

    def test_python_writes_to_the_hard_places(self):
        before = self.m.before()
        self.m.shell(py("import tempfile, os; open(os.path.join(tempfile.gettempdir(), 'scratch.json'), 'w').write('{}')"))
        self.m.shell(py(f"open('{(self.m.c_tmp / 'a.txt').as_posix()}', 'w').write('x')"))
        self.m.shell(py("open('../stray.png', 'wb').write(b'x')"))  # from the workspace, into the project's parent
        got = {(h["place"], h["name"], h["hard"]) for h in self.m.hits(before)}
        self.assertEqual(got, {("run temp", "scratch.json", True), ("C:/tmp", "a.txt", True), ("project parent", "stray.png", True)})

    def test_a_changed_file_and_a_new_folder_count_but_a_folders_time_does_not(self):
        (self.m.home / "notes.txt").write_text("a")
        before = self.m.before()
        time.sleep(0.05)
        self.m.shell(py(f"open('{(self.m.home / 'notes.txt').as_posix()}', 'a').write('b')"))
        self.m.shell(py(f"import os; os.makedirs('{(self.m.temp / 'w').as_posix()}')"))
        (self.m.home / ".cache" / "x").write_text("x")  # below the top of a shared place: not listed
        got = {(h["place"], h["name"], h["change"]) for h in self.m.hits(before)}
        self.assertEqual(got, {("home", "notes.txt", "changed"), ("temp", "w", "new")})

    def test_the_measured_noise_is_left_out_of_shared_places_only(self):
        before = self.m.before()
        guid = "0bb32162-768f-4f56-a7b3-88ab95039d43.tmp"
        (self.m.temp / guid).write_text("x")
        (self.m.home / ".claude.json").write_text('{"changed": true}')
        (self.m.parent / guid).write_text("x")  # the same name in a hard place is a hit
        (self.m.temp / ".claude.json").write_text("x")  # a home pattern does not cover the temp folder
        got = {(h["place"], h["name"]) for h in self.m.hits(before)}
        self.assertEqual(got, {("project parent", guid), ("temp", ".claude.json")})
        for _, rx, why in leftovers.SHARED_NOISE:
            self.assertIn("baseline", why)  # every pattern says where it was measured

    def test_claude_codes_own_entries_in_the_run_temp_folder_and_nothing_else(self):
        before = self.m.before()
        (self.m.run_tmp / "claude" / "proj" / "tasks").mkdir(parents=True)
        (self.m.run_tmp / "claude" / "proj" / "tasks" / "b1.output").write_text("x")
        (self.m.run_tmp / "claude-1a2b-cwd").write_text("x")
        (self.m.run_tmp / "claudette.txt").write_text("x")  # not Claude Code's: a hard hit
        (self.m.run_tmp / "page.png").write_bytes(b"x")
        got = {(h["place"], h["name"]) for h in self.m.hits(before)}
        self.assertEqual(got, {("run temp", "claudette.txt"), ("run temp", "page.png")})

    def test_an_idle_interval_is_clean(self):
        before = self.m.before()
        self.m.shell("echo nothing > /dev/null; true")
        self.assertEqual(self.m.hits(before), [])


class ActiveRuns(unittest.TestCase):
    def test_runs_that_overlap_are_named(self):
        with tempfile.TemporaryDirectory() as d:
            reg = Path(d) / "eval-runs.jsonl"
            lines = [{"event": "start", "t": 100, "pid": 1, "case": "a", "run": 1, "workspace": "/w/a"},
                     {"event": "start", "t": 105, "pid": 2, "case": "b", "run": 2, "workspace": "/w/b"},
                     {"event": "end", "t": 110, "pid": 2, "case": "b", "run": 2, "workspace": "/w/b"},
                     {"event": "start", "t": 200, "pid": 3, "case": "c", "run": 1, "workspace": "/w/c"},
                     {"event": "end", "t": 210, "pid": 3, "case": "c", "run": 1, "workspace": "/w/c"}]
            reg.write_text("\n".join(json.dumps(x) for x in lines))
            self.assertEqual(leftovers.overlapping(Path("/w/a"), 100, 150, reg), ["b run-2 (pid 2)"])


def run(outside, trace=(), overlapping=()):
    return RunResult(case="t", run_index=1, workspace=Path("/ws"), trace=list(trace), outside_files=outside,
                     overlapping_runs=list(overlapping))


def hit(name, place="temp", hard=False):
    return {"place": place, "name": name, "path": f"/x/{name}", "change": "new", "hard": hard, "dir": False}


class Reports(unittest.TestCase):
    def blocker(self, r):
        return next(g for g in grade_blockers(r) if g.name == "writes-inside-project")

    def test_a_hit_is_a_blocker_and_says_whether_the_run_named_it(self):
        trace = [{"type": "tool_use", "name": "Bash", "input": {"command": "python -c \"open('/tmp/page.png','wb')\""}},
                 {"type": "tool_result", "content": "saved scratch.json"}]
        g = self.blocker(run([hit("page.png"), hit("scratch.json", "run temp", True), hit("other.tmp")], trace))
        self.assertFalse(g.passed)
        self.assertIn("temp: page.png (new; named in the run's commands)", g.detail)
        self.assertIn("run temp: scratch.json (new, hard place; named in the run's output)", g.detail)
        self.assertIn("temp: other.tmp (new; not named by the run)", g.detail)

    def test_it_names_the_runs_active_at_the_same_time(self):
        self.assertIn("other runs active at the time: ['b run-2 (pid 2)']",
                      self.blocker(run([hit("x.png")], overlapping=["b run-2 (pid 2)"])).detail)

    def test_the_command_check_is_the_second_signal(self):
        trace = [{"type": "tool_use", "name": "Bash", "input": {"command": "cp a.png /tmp/a.png"}}]
        g = self.blocker(run([], trace))
        self.assertFalse(g.passed)
        self.assertIn("commands that wrote outside", g.detail)
        self.assertTrue(self.blocker(run([])).passed)

    def test_a_run_from_before_the_check_says_so(self):
        self.assertIn("not recorded", self.blocker(run(None)).detail)


if __name__ == "__main__":
    unittest.main()
