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
from graders import GraderResult, grade_blockers, mark, score  # noqa: E402
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
        (self.home / ".editor-state.json").write_text("{}")
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
        guid = "00000000-0000-4000-8000-000000000000.tmp"
        with tempfile.TemporaryDirectory() as d:  # the machine's list is read from a file outside the repository
            noise_file = Path(d) / "eval-noise.jsonl"
            noise_file.write_text(json.dumps({"place": "temp", "pattern": r"^[0-9a-f-]{36}\.tmp$", "reason": "test baseline"}) + "\n"
                                  + json.dumps({"place": "home", "pattern": r"^\.editor-state\.json$", "reason": "test baseline"}) + "\n")
            noise = leftovers.load_noise(noise_file)
        saved, leftovers.SHARED_NOISE[:] = list(leftovers.SHARED_NOISE), noise
        try:
            before = self.m.before()
            (self.m.temp / guid).write_text("x")
            (self.m.home / ".editor-state.json").write_text('{"changed": true}')
            (self.m.parent / guid).write_text("x")  # the same name in a hard place is a hit
            (self.m.temp / ".editor-state.json").write_text("x")  # a home pattern does not cover the temp folder
            got = {(h["place"], h["name"]) for h in self.m.hits(before)}
        finally:
            leftovers.SHARED_NOISE[:] = saved
        self.assertEqual(got, {("project parent", guid), ("temp", ".editor-state.json")})
        self.assertEqual(leftovers.load_noise(Path(self.tmp.name) / "missing.jsonl"), [])  # no file: nothing left out

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


class UserFolders(unittest.TestCase):
    """Desktop, Documents and Downloads are walked whole: a file saved inside a folder that already exists counts."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.m = Machine(Path(self.tmp.name))
        self.docs = self.m.home / "Documents"
        (self.docs / "Existing Project").mkdir(parents=True)
        old = self.docs / "Existing Project" / "plan.pdf"
        old.write_bytes(b"%PDF")
        past = time.time() - 3600
        os.utime(old, (past, past))

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_python_write_inside_an_existing_folder_is_caught_and_the_command_check_misses_it(self):
        target = (self.docs / "Existing Project" / "x.png").as_posix()
        command = py(f"open('{target}', 'wb').write(b'x')")
        self.assertEqual(shell_write_targets(command, str(self.m.ws)), [])
        t0 = self.start()
        self.assertEqual(leftovers.changed_since([("Documents", self.docs)], t0), [])  # the old file is not a hit
        self.m.shell(command)
        hits = leftovers.changed_since([("Documents", self.docs)], t0)
        self.assertEqual([(h["place"], h["name"]) for h in hits], [("Documents", "Existing Project/x.png")])
        self.assertEqual(self.m.hits(self.m.before()), [])  # the top-level listing alone would not have seen it

    def start(self):
        """The session's start, with room on both sides: the fixture's files are older (os.utime cannot move a
        Windows creation time back), the run's files newer, past the file clock's coarse ticks."""
        time.sleep(0.1)
        t0 = time.time()
        time.sleep(0.1)
        return t0

    def test_a_changed_file_counts_and_listed_noise_does_not(self):
        t0 = self.start()
        self.m.shell(py(f"open('{(self.docs / 'Existing Project' / 'plan.pdf').as_posix()}', 'ab').write(b'1')"))
        (self.docs / "sync.tmp").write_text("x")
        noise = [("Documents", leftovers.re.compile(r"^sync\.tmp$"), "a test pattern")]
        saved, leftovers.SHARED_NOISE[:] = list(leftovers.SHARED_NOISE), noise
        try:
            names = [h["name"] for h in leftovers.changed_since([("Documents", self.docs)], t0)]
        finally:
            leftovers.SHARED_NOISE[:] = saved
        self.assertEqual(names, ["Existing Project/plan.pdf"])

    def test_the_folders_are_found_under_home(self):
        (self.m.home / "Desktop").mkdir()
        (self.m.home / "Documents").mkdir(exist_ok=True)
        self.assertEqual([label for label, _ in leftovers.user_folders(home=self.m.home)], ["Desktop", "Documents"])


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

    def test_a_run_stopped_without_an_end_counts_only_while_its_process_lives(self):
        with tempfile.TemporaryDirectory() as d:
            reg = Path(d) / "eval-runs.jsonl"
            dead = subprocess.run([sys.executable, "-c", "import os; print(os.getpid())"], capture_output=True, text=True)
            lines = [{"event": "start", "t": 100, "pid": int(dead.stdout), "case": "killed", "run": 3, "workspace": "/w/k"},
                     {"event": "start", "t": 100, "pid": os.getpid(), "case": "live", "run": 1, "workspace": "/w/l"}]
            reg.write_text("\n".join(json.dumps(x) for x in lines))
            self.assertEqual(leftovers.overlapping(Path("/w/a"), 200, 300, reg), [f"live run-1 (pid {os.getpid()})"])
            self.assertTrue(leftovers.pid_alive(os.getpid()))


def run(outside, trace=(), overlapping=()):
    return RunResult(case="t", run_index=1, workspace=Path("/ws"), trace=list(trace), outside_files=outside,
                     overlapping_runs=list(overlapping))


def hit(name, place="temp", hard=False, root="C:/Users/u/AppData/Local/Temp"):
    return {"place": place, "name": name, "path": f"{root}/{name}", "change": "new", "hard": hard, "dir": False}


class Reports(unittest.TestCase):
    """Hard places block; a shared place blocks only when the run names the file or its folder, else it is reviewed."""

    def results(self, r):
        return {g.name: g for g in grade_blockers(r)}

    def test_hard_places_block_named_shared_files_block_the_rest_is_reviewed(self):
        trace = [{"type": "tool_use", "name": "Bash", "input": {"command": "python -c \"open('/tmp/page.png','wb')\""}},
                 {"type": "tool_result", "content": "saved scratch.json"}]
        r = run([hit("page.png"), hit("scratch.json", "run temp", True, "C:/eval/case-r1-tmp"),
                 hit("tmp3k2j9x1a"), hit("cache.bin", "C:/tmp", True, "C:/tmp")], trace)
        g = self.results(r)
        self.assertFalse(g["writes-inside-project"].passed)
        self.assertIn("temp: page.png (new; named in the run's commands)", g["writes-inside-project"].detail)
        self.assertIn("run temp: scratch.json (new; hard place; named in the run's output)", g["writes-inside-project"].detail)
        self.assertIn("C:/tmp: cache.bin (new; hard place; not named by the run)", g["writes-inside-project"].detail)
        self.assertNotIn("tmp3k2j9x1a", g["writes-inside-project"].detail)
        self.assertEqual(mark(g["outside-review"]), "REVIEW")
        self.assertIn("temp: tmp3k2j9x1a (new; not named by the run)", g["outside-review"].detail)

    def test_an_unnamed_shared_file_is_reviewed_not_scored(self):
        g = self.results(run([hit("tmp3k2j9x1a"), hit("Report.docx", "Documents", root="C:/Users/u/Documents")]))
        self.assertTrue(g["writes-inside-project"].passed)
        self.assertFalse(g["outside-review"].passed)
        self.assertEqual(score([GraderResult("deliverable", "file_exists", 1, True)] + list(g.values())), 1.0)

    def test_naming_the_folder_counts(self):
        trace = [{"type": "tool_use", "name": "Bash",
                  "input": {"command": 'cd "C:/Users/u/Documents/Existing Project" && python make.py'}}]
        g = self.results(run([hit("Existing Project/x", "Documents", root="C:/Users/u/Documents")], trace))
        self.assertFalse(g["writes-inside-project"].passed)
        # the temp folder itself is not "its folder": every run names it, the workspace is inside
        trace = [{"type": "tool_use", "name": "Bash", "input": {"command": 'cd "C:/Users/u/AppData/Local/Temp/construction-eval/case-r1"'}}]
        self.assertTrue(self.results(run([hit("tmp3k2j9x1a")], trace))["writes-inside-project"].passed)

    def test_it_names_the_runs_active_at_the_same_time(self):
        self.assertIn("other runs active at the time: ['b run-2 (pid 2)']",
                      self.results(run([hit("tmp3k2j9x1a")], overlapping=["b run-2 (pid 2)"]))["outside-review"].detail)

    def blocker(self, r):
        return self.results(r)["writes-inside-project"]

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
