"""Poppler for the agentcm-mode cases: AgentCM's real crop.sh and crop.ps1 render the fixture's PDFs with
pdfinfo and pdftoppm.

The harness takes the Poppler folder from its own setting, the AGENTCM_POPPLER_BIN environment variable of the
harness run, and passes it into every agentcm-mode case's setup, session and teardown, that folder first on PATH:
Git Bash ships Xpdf tools under the same names. The path is never written into the fixture or the repository.
Unset, the crop scripts take pdfinfo and pdftoppm from PATH.

Before any case starts, preflight() runs the fixture's crop.sh (and crop.ps1 on Windows) once on a known box in a
copy of the fixture and checks a PNG comes back; it also checks the pdfinfo it finds is Poppler's. A failure stops
the whole run with a setup error naming what was missing, rather than letting the cases go red one by one.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VAR = "AGENTCM_POPPLER_BIN"
TAG = "agentcm-mode"
FIXTURE = Path(__file__).resolve().parents[1] / "plugin" / "agentcm-mode"
PNG = b"\x89PNG\r\n\x1a\n"
TIMEOUT = 120


class PopplerError(Exception):
    """What the preflight found missing; the run stops on it."""


def case_env(base: dict | None = None) -> dict:
    """The variables an agentcm-mode case adds to its environment: AGENTCM_POPPLER_BIN, and PATH with that folder
    first; nothing when the harness run has no AGENTCM_POPPLER_BIN."""
    base = os.environ if base is None else base
    folder = base.get(VAR, "").strip()
    if not folder:
        return {}
    return {VAR: folder, "PATH": folder + os.pathsep + base.get("PATH", "")}


def known_box(fixture: Path = FIXTURE) -> tuple[str, float, float, float, float]:
    """A box to crop: the first entry of the fixture's drawn-marks.json, else the first line of its first sheet
    file. Either lies on its sheet, so a crop of it must render."""
    marks = fixture / "drawn-marks.json"
    if marks.is_file():
        data = json.loads(marks.read_text(encoding="utf-8"))
        entries = data if isinstance(data, list) else data.get("marks", [])
        for m in entries:
            box = m.get("box")
            if isinstance(box, str):
                box = box.split()
            if isinstance(box, dict):
                box = [box.get(k) for k in ("x", "y", "w", "h")]
            if m.get("sheet") and box and len(box) == 4:
                return (str(m["sheet"]), *(float(v) for v in box))
    for tsv in sorted((fixture / "construction" / "sheets").glob("*.tsv")):
        if tsv.name.endswith(".groups.tsv"):
            continue
        rows = tsv.read_text(encoding="utf-8").splitlines()
        head = rows[0].split("\t") if rows else []
        for row in rows[1:]:
            cells = dict(zip(head, row.split("\t")))
            try:
                return (tsv.stem, *(float(cells[k]) for k in ("x", "y", "w", "h")))
            except (KeyError, ValueError):
                continue
    raise PopplerError(f"no box to crop: {fixture} has neither drawn-marks.json nor a sheet file with a line")


def _bash(bash: str, script: str, cwd: Path, env: dict) -> subprocess.CompletedProcess:
    return subprocess.run([bash, "-c", script], cwd=cwd, env=env, capture_output=True, text=True, timeout=TIMEOUT)


def find_tools(bash: str, cwd: Path, env: dict) -> dict[str, str]:
    """{tool: path} for pdfinfo and pdftoppm as the crop scripts find them: in AGENTCM_POPPLER_BIN when it is set,
    else on the PATH Git Bash sees. PopplerError names the ones missing."""
    folder = env.get(VAR, "").strip()
    found, missing = {}, []
    for tool in ("pdfinfo", "pdftoppm"):
        if folder:
            hit = next((str(Path(folder) / n) for n in (tool, tool + ".exe") if (Path(folder) / n).is_file()), "")
        else:
            hit = _bash(bash, f"command -v {tool}", cwd, env).stdout.strip()
        if hit:
            found[tool] = hit
        else:
            missing.append(tool)
    if missing:
        where = f"in {VAR} ({folder})" if folder else f"on PATH (set {VAR} to Poppler's bin folder)"
        raise PopplerError(f"{' and '.join(missing)} not found {where}: AgentCM's crop scripts need Poppler")
    return found


def check_poppler(bash: str, pdfinfo: str, cwd: Path, env: dict) -> str:
    """pdfinfo's version line; PopplerError when it is not Poppler's (Git Bash and MiKTeX ship Xpdf's)."""
    p = _bash(bash, f'"{pdfinfo}" -v', cwd, env)
    out = (p.stdout + p.stderr).strip()
    if not re.search(r"poppler", out, re.IGNORECASE):
        first = out.splitlines()[0] if out else "(no output)"
        raise PopplerError(f"the pdfinfo found ({pdfinfo}) is not Poppler's: {first}. Set {VAR} to Poppler's bin "
                           "folder; it goes first on PATH")
    return next((l for l in out.splitlines() if "version" in l.lower()), out.splitlines()[0])


def _png(out: str, cwd: Path) -> Path | None:
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    if not lines:
        return None
    p = Path(lines[-1])
    p = p if p.is_absolute() else cwd / p
    try:
        return p if p.is_file() and p.read_bytes()[:8] == PNG else None
    except OSError:
        return None


def preflight(bash: str, fixture: Path = FIXTURE, env: dict | None = None) -> list[str]:
    """Copy the fixture, find Poppler, crop a known box with crop.sh (and crop.ps1 on Windows). Returns what it
    checked, as lines to print; raises PopplerError on the first thing missing."""
    env = dict(os.environ if env is None else env)
    env.update(case_env(env))
    box = known_box(fixture)
    with tempfile.TemporaryDirectory(prefix="agentcm-preflight-") as tmp:
        ws = Path(tmp)
        shutil.copytree(fixture / "construction", ws / ".construction")
        if (fixture / "project").is_dir():
            shutil.copytree(fixture / "project", ws, dirs_exist_ok=True)
        tools = find_tools(bash, ws, env)
        version = check_poppler(bash, tools["pdfinfo"], ws, env)
        args = [box[0]] + [f"{v:.3f}" for v in box[1:]]
        lines = [f"Poppler: {version} ({tools['pdfinfo']})"]
        p = _bash(bash, "sh .construction/crop.sh " + " ".join(f'"{a}"' for a in args), ws, env)
        png = _png(p.stdout, ws)
        if p.returncode != 0 or not png:
            raise PopplerError(f"crop.sh {' '.join(args)} gave no PNG (exit {p.returncode}): "
                               f"{(p.stdout + p.stderr).strip()[-400:]}")
        lines.append(f"crop.sh {' '.join(args)}: {png.name}")
        if sys.platform == "win32":
            p = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                                str(ws / ".construction" / "crop.ps1"), *args],
                               cwd=ws, env=env, capture_output=True, text=True, timeout=TIMEOUT)
            png = _png(p.stdout, ws)
            if p.returncode != 0 or not png:
                raise PopplerError(f"crop.ps1 {' '.join(args)} gave no PNG (exit {p.returncode}): "
                                   f"{(p.stdout + p.stderr).strip()[-400:]}")
            lines.append(f"crop.ps1 {' '.join(args)}: {png.name}")
    return lines
