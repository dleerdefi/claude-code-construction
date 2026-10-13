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
of a shared place is not listed. Every hit is a blocker; grade_blockers says whether the run's commands or output
mention the file, and names the other runs that were active at the same time (REGISTRY).
"""
from __future__ import annotations

import json
import os
import re
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

# Names that change at the top of a shared place with nothing running: (place, pattern, reason). Only patterns
# measured in an idle baseline belong here (evals/harness/README.md, "Outside writes").
SHARED_NOISE = [
    ("temp", re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.tmp$", re.I),
     "GUID-named .tmp files a Windows program creates and deletes about once a minute "
     "(idle baseline 2026-10-13: 3 new and 4 gone in 150 s)"),
    ("temp", re.compile(r"^unleash-.*codeium.*\.json$", re.I),
     "the Codeium editor extension's feature-flag cache, rewritten while idle (baseline 2026-10-13)"),
    ("home", re.compile(r"^\.claude\.json$"),
     "Claude Code's own settings file, rewritten by every Claude Code session (baseline 2026-10-13)"),
    ("home", re.compile(r"^ntuser\.dat\.log\d$", re.I),
     "Windows' log of the user's registry hive, rewritten while idle (baseline 2026-10-13)"),
]

# Claude Code's own entries in a temp folder: the run's (its session gets the run's TEMP, and Claude Code passes its
# environment to every command) and the shared one. Anything else in the run's temp folder is a hard hit. (David,
# 2026-10-13; the names are confirmed from the idle control run, evals/plugin/_control-idle.)
CLAUDE_CODE_OWN = (re.compile(r"^claude(-[^/]*)?(/|$)"),
                   "Claude Code's own working files (claude/ and claude-*), as in this session's Temp/claude/")

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


# --- which runs were active ------------------------------------------------------------------------

def register(event: str, case: str, run_index: int, workspace: Path) -> None:
    try:
        REGISTRY.parent.mkdir(parents=True, exist_ok=True)
        with REGISTRY.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"event": event, "t": time.time(), "pid": os.getpid(), "case": case,
                                "run": run_index, "workspace": str(workspace)}) + "\n")
    except OSError:
        pass


def overlapping(workspace: Path, t0: float, t1: float, registry: Path | None = None) -> list[str]:
    """The other runs whose span touched [t0, t1], from the registry: "case run-N (pid P)"."""
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
        end = s["end"] if s["end"] is not None else time.time()
        if s["start"] <= t1 and end >= t0:
            out.append(f"{s['case']} run-{s['run']} (pid {s['pid']})")
    return out
