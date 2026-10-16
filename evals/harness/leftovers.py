"""What a run left outside its project folder, read from the filesystem rather than from its commands.

A write made inside Python code (`python -c "open('/tmp/x.png', 'wb')..."`) never shows as a shell redirect, so
the command check in guard.py cannot see it. This one looks at what is there before and after the session:

- Each run gets a temp folder of its own, next to its workspace; TMP, TEMP and TMPDIR point at it.
- Hard places, where nothing but the run writes: the run's temp folder (every file in it), C:\\tmp on Windows and
  the project folder's parent (construction-eval/, one workspace per run). Anything new or changed there is a hit.
- Shared places, which every program on the machine writes to: the system temp folder (on Windows, Git Bash's /tmp
  is this folder whatever TEMP says), /tmp elsewhere, and the top of the home folder. A new entry or a changed file
  is a hit unless its name matches SHARED_NOISE, measured with nothing running (each pattern says when and what).

Directories are compared by their entries, not their times: a folder whose contents changed below the top level
of a shared place is not listed. The user's own folders (Desktop, Documents, Downloads) are the exception: they are
walked whole for files created or changed since the session started (changed_since). A hit in a hard place is a
blocker; in a shared place, only when the run's commands or output name the file or its folder, and otherwise it is
listed for review, unscored (graders._outside). Each report names the other runs that were active at the same
time (REGISTRY).
"""
from __future__ import annotations

import json
import os
import re
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

# Names that change in a shared place with nothing running on this machine: (place, pattern, reason), place one of
# temp, home, Desktop, Documents, Downloads. They are this machine's file names, so they live on the machine, never in
# the repository: one JSON object per line in NOISE_FILE ({"place", "pattern", "reason"}). Only names an idle baseline
# showed changing belong there, each with that baseline (README, "Outside writes"; probe_leftovers.py --idle prints
# what changed). Without the file nothing is left out.
NOISE_FILE = Path.home() / ".construction-skills" / "eval-noise.jsonl"


def load_noise(path: Path = NOISE_FILE) -> list[tuple[str, re.Pattern, str]]:
    out = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return out
    for line in lines:
        if line.strip():
            e = json.loads(line)
            out.append((e["place"], re.compile(e["pattern"], re.I), e["reason"]))
    return out


SHARED_NOISE = load_noise()

# Claude Code's own entries in a temp folder: the run's (its session gets the run's TEMP, and Claude Code passes its
# environment to every command) and the shared one. Anything else in the run's temp folder is a hard hit. (David,
# 2026-10-13; confirmed by name from the idle control run, evals/plugin/control-idle: claude/<project>/<session>/tasks.)
CLAUDE_CODE_OWN = (re.compile(r"^claude(-[^/]*)?(/|$)"), "Claude Code's own working files (claude/ and claude-*)")

# Start and end of every harness run, so a hit in a shared place can name every run that was active then.
REGISTRY = Path.home() / ".construction-skills" / "eval-runs.jsonl"


@dataclass(frozen=True)
class Place:
    label: str
    path: Path
    hard: bool
    recursive: bool = False


def run_temp_for(workspace: Path) -> Path:
    return workspace.with_name(workspace.name + "-tmp")


def places(workspace: Path, run_tmp: Path, system_temp: Path | None = None, home: Path | None = None,
           c_tmp: Path | None = None) -> list[Place]:
    system_temp = system_temp or Path(tempfile.gettempdir())
    out = [Place("run temp", run_tmp, True, recursive=True)]
    if c_tmp is not None or os.name == "nt":
        out.append(Place("C:/tmp", c_tmp or Path("C:/tmp"), True))
    out.append(Place("project parent", workspace.parent, True))
    out.append(Place("temp", system_temp, False))
    if os.name != "nt" and Path("/tmp").resolve() != system_temp.resolve():
        out.append(Place("/tmp", Path("/tmp"), False))
    out.append(Place("home", home or Path.home(), False))
    return out


def _entries(place: Place) -> dict[str, tuple[bool, int, int]]:
    out: dict[str, tuple[bool, int, int]] = {}
    if place.recursive:
        if place.path.is_dir():
            for p in place.path.rglob("*"):
                try:
                    st = p.stat()
                except OSError:
                    continue
                out[p.relative_to(place.path).as_posix()] = (p.is_dir(), 0 if p.is_dir() else st.st_size, st.st_mtime_ns)
        return out
    try:
        with os.scandir(place.path) as it:
            for e in it:
                try:
                    st = e.stat(follow_symlinks=False)
                except OSError:
                    continue
                d = e.is_dir(follow_symlinks=False)
                out[e.name] = (d, 0 if d else st.st_size, st.st_mtime_ns)
    except OSError:
        pass
    return out


def snapshot(where: list[Place]) -> dict[str, dict]:
    return {p.label: _entries(p) for p in where}


def noise_reason(place: Place, name: str) -> str | None:
    if place.label in ("run temp", "temp", "/tmp") and CLAUDE_CODE_OWN[0].search(name):
        return CLAUDE_CODE_OWN[1]
    if place.hard:
        return None
    label = "temp" if place.label in ("temp", "/tmp") else place.label
    return next((why for where, rx, why in SHARED_NOISE if where == label and rx.search(name)), None)


def diff(where: list[Place], before: dict, after: dict, own: set[str] = frozenset()) -> list[dict]:
    """Hits: a new entry, or a file whose size or time changed. `own` holds the names the run itself was given in
    the project's parent (its workspace and temp folder)."""
    hits = []
    for p in where:
        b, a = before.get(p.label, {}), after.get(p.label, {})
        for name, (is_dir, size, mtime) in sorted(a.items()):
            if p.label == "project parent" and name in own:
                continue
            old = b.get(name)
            if old is None:
                change = "new"
            elif not is_dir and (size, mtime) != old[1:]:
                change = "changed"
            else:
                continue
            if noise_reason(p, name):
                continue
            hits.append({"place": p.label, "name": name, "path": str(p.path / name), "change": change,
                         "hard": p.hard, "dir": is_dir})
    return hits


# --- the user's own folders: Desktop, Documents, Downloads, all the way down ------------------------
# A file saved inside a folder that already exists (Documents\Project\x.png) changes nothing at the top. These
# three are walked whole after the session, once, for every file created or changed since it started: on
# Windows the directory listing carries both times (st_ctime is the creation time), so about half a million
# files take some 8 seconds. A file moved in from the same volume keeps its old times and is not seen.

# Windows stamps files with a coarser clock than time.time(): a file written just after the session started can
# carry a time a little before it. Seconds to look back.
CLOCK_SLACK = 2.0

_SHELL_FOLDERS = {"Desktop": "Desktop", "Documents": "Personal", "Downloads": "{374DE290-123F-4565-9164-39C4925E467B}"}


def user_folders(home: Path | None = None) -> list[tuple[str, Path]]:
    """Desktop, Documents and Downloads where this user's shell keeps them (OneDrive may have moved them)."""
    out = []
    for label, value in _SHELL_FOLDERS.items():
        path = None
        if os.name == "nt" and home is None:
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                    r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as k:
                    path = Path(os.path.expandvars(winreg.QueryValueEx(k, value)[0]))
            except OSError:
                path = None
        path = path or (home or Path.home()) / label
        if path.is_dir():
            out.append((label, path))
    return out


def changed_since(folders: list[tuple[str, Path]], t0: float) -> list[dict]:
    """Every file below the folders created or changed at or after t0, unless the machine's noise list says why it changes."""
    hits = []
    for label, root in folders:
        stack = [str(root)]
        while stack:
            d = stack.pop()
            try:
                with os.scandir(d) as it:
                    for e in it:
                        try:
                            if e.is_dir(follow_symlinks=False):
                                stack.append(e.path)
                                continue
                            st = e.stat(follow_symlinks=False)
                        except OSError:
                            continue
                        if max(st.st_mtime, st.st_ctime) < t0:
                            continue
                        rel = Path(e.path).relative_to(root).as_posix()
                        if any(where == label and rx.search(rel) for where, rx, _ in SHARED_NOISE):
                            continue
                        hits.append({"place": label, "name": rel, "path": e.path, "change": "new or changed",
                                     "hard": False, "dir": False})
            except OSError:
                continue
    return hits


# --- which runs were active ------------------------------------------------------------------------

def register(event: str, case: str, run_index: int, workspace: Path) -> None:
    try:
        REGISTRY.parent.mkdir(parents=True, exist_ok=True)
        with REGISTRY.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"event": event, "t": time.time(), "pid": os.getpid(), "case": case,
                                "run": run_index, "workspace": str(workspace)}) + "\n")
    except OSError:
        pass


def pid_alive(pid: int) -> bool:
    """Whether a process with this id is still running."""
    if os.name == "nt":
        import ctypes
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, int(pid))  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        code = ctypes.c_ulong()
        ok = ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
        ctypes.windll.kernel32.CloseHandle(handle)
        return bool(ok) and code.value == 259  # STILL_ACTIVE
    try:
        os.kill(int(pid), 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def overlapping(workspace: Path, t0: float, t1: float, registry: Path | None = None) -> list[str]:
    """The other runs whose span touched [t0, t1], from the registry: "case run-N (pid P)". A run with no end is
    active only while its harness process lives: one stopped mid-run (a memory stop) never wrote its end."""
    spans: dict[str, dict] = {}
    try:
        lines = (registry or REGISTRY).read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        s = spans.setdefault(e["workspace"], {"case": e["case"], "run": e["run"], "pid": e["pid"], "start": None, "end": None})
        s["start" if e["event"] == "start" else "end"] = e["t"]
    out = []
    own = os.path.normcase(os.path.normpath(str(workspace)))
    for ws, s in spans.items():
        if os.path.normcase(os.path.normpath(ws)) == own or s["start"] is None:
            continue
        if s["end"] is None and not pid_alive(s["pid"]):
            continue
        end = s["end"] if s["end"] is not None else time.time()
        if s["start"] <= t1 and end >= t0:
            out.append(f"{s['case']} run-{s['run']} (pid {s['pid']})")
    return out
