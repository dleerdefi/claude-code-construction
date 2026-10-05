"""Policy guard for harness runs: decides every shell and file-writing tool call.

On native Windows the harness runs without an OS sandbox, so this is the
confinement: shell commands may only touch the workspace, the plugin, the
toolkit's venv and the system temp dir, and may not reach the network or install
software. The same rules apply on every platform so runs behave the same.

`decide()` is a pure function so it can be unit-tested without an agent; the
runner wraps it in a PreToolUse hook.
"""
from __future__ import annotations

import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

SHELL_TOOLS = ("Bash", "PowerShell")
WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
GUARDED_TOOLS = SHELL_TOOLS + WRITE_TOOLS

# (pattern, why) — matched against the whole shell command, case-insensitive.
DENY_PATTERNS = [
    (r"\b(curl|wget|ssh|scp|sftp|telnet|nc|ncat|psql)\b", "network or database command"),
    (r"\b(Invoke-WebRequest|iwr|Invoke-RestMethod|irm|Start-BitsTransfer|Invoke-Expression|iex)\b",
     "PowerShell network or eval command"),
    (r"\bpip3?\s+(install|download|uninstall)\b", "package installation"),
    (r"\bnpm\s+(install|i|exec|x|uninstall)\b|\bnpx\b", "package installation"),
    (r"\bgit\s+(push|clone|fetch|pull|remote)\b", "git network command"),
    (r"\b(sudo|runas|shutdown|reboot|diskpart)\b", "privileged command"),
]
RECURSIVE_DELETE = re.compile(r"\brm\s+(-[a-zA-Z]*[rR][a-zA-Z]*|--recursive)\b|Remove-Item\b.*-Recurse|\b(rmdir|rd)\s+/s\b",
                              re.IGNORECASE)

# Locations outside the allowed roots that shell commands may still name.
SYSTEM_PREFIXES = ("/dev", "/tmp", "/usr", "/bin", "/etc", "/proc", "/mingw64", "/mingw32", "/opt",
                   "/Library", "/System", "/Applications", "/var", "/private",
                   "C:/Windows", "C:/Program Files", "C:/Program Files (x86)", "C:/ProgramData")

_WIN_ABS = r"[A-Za-z]:[\\/][^\s\"'|&;<>()]*"
_POSIX_ABS = r"/[^\s\"'|&;<>()]*"
_HOME_REL = r"(?:~|\$HOME|%USERPROFILE%)(?:[\\/][^\s\"'|&;<>()]*)?"
# A glob such as `ls */` or `sheets/*/` is not a path from the root.
_PATH_TOKEN = re.compile(rf"(?<![\w.*?-])({_WIN_ABS}|{_POSIX_ABS}|{_HOME_REL})")
# Inside quotes a path may contain spaces.
_QUOTED_PATH = re.compile(rf"^\s*([A-Za-z]:[\\/][^\"'|&;<>()]*|/[^\"'|&;<>()]*|(?:~|\$HOME|%USERPROFILE%)(?:[\\/][^\"'|&;<>()]*)?)\s*$")
_QUOTED = re.compile(r"\"([^\"]*)\"|'([^']*)'")


@dataclass(frozen=True)
class Decision:
    allow: bool
    reason: str = ""


@dataclass(frozen=True)
class Policy:
    workspace: str
    plugin_root: str
    extra_roots: tuple[str, ...] = ()

    def allowed_roots(self) -> tuple[str, ...]:
        roots = [self.workspace, self.plugin_root, tempfile.gettempdir(),
                 str(Path.home() / ".construction-skills"), sys.base_prefix, sys.prefix]
        roots += list(self.extra_roots)
        return tuple(normalize(r) for r in roots)


def normalize(path: str) -> str:
    """Canonical forward-slash form. Git Bash `/c/x` becomes `C:/x`; `~` expands."""
    p = path.strip()
    if p in ("~", "$HOME", "%USERPROFILE%") or p.startswith(("~/", "~\\", "$HOME/", "$HOME\\", "%USERPROFILE%/", "%USERPROFILE%\\")):
        tail = re.sub(r"^(~|\$HOME|%USERPROFILE%)", "", p)
        p = str(Path.home()) + tail
    m = re.match(r"^/([a-zA-Z])(/|$)", p)
    if m:
        p = m.group(1).upper() + ":/" + p[3:]
    p = p.replace("\\", "/")
    p = os.path.normpath(p).replace("\\", "/")
    if re.match(r"^[a-zA-Z]:", p):
        p = p[0].upper() + p[1:]
    return p


def _is_under(path: str, root: str) -> bool:
    a, b = path, root.rstrip("/")
    if os.name == "nt" or re.match(r"^[A-Z]:", a):
        a, b = a.lower(), b.lower()
    return a == b or a.startswith(b + "/")


def _path_allowed(path: str, policy: Policy) -> bool:
    n = normalize(path)
    if any(_is_under(n, r) for r in policy.allowed_roots()):
        return True
    if any(_is_under(n, normalize(p)) for p in SYSTEM_PREFIXES):
        return True
    # A bare drive or filesystem root is never a legitimate target.
    return False


def shell_paths(command: str) -> list[str]:
    """Absolute and home-relative paths named in a shell command (quoted or bare)."""
    found: list[str] = []
    for q in _QUOTED.finditer(command):
        text = q.group(1) if q.group(1) is not None else q.group(2)
        if _QUOTED_PATH.match(text):
            found.append(text.strip())
    unquoted = _QUOTED.sub(" ", command)
    found += [m.group(1) for m in _PATH_TOKEN.finditer(unquoted)]
    return [p for p in found if p not in ("/", "~")] + ([p for p in found if p in ("/", "~")])


def decide(tool_name: str, tool_input: dict, policy: Policy) -> Decision:
    if tool_name in WRITE_TOOLS:
        raw = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        target = raw if os.path.isabs(raw) or re.match(r"^[A-Za-z]:", raw) or raw.startswith("/") else os.path.join(policy.workspace, raw)
        if _is_under(normalize(target), normalize(policy.workspace)):
            return Decision(True)
        return Decision(False, f"Blocked by the eval guard: writes outside the workspace are not allowed ({raw})")

    if tool_name in SHELL_TOOLS:
        command = tool_input.get("command", "") or ""
        for pattern, why in DENY_PATTERNS:
            m = re.search(pattern, command, re.IGNORECASE)
            if m:
                return Decision(False, f"Blocked by the eval guard: {why} ({m.group(0)}) is not allowed in an eval run")
        for p in shell_paths(command):
            if p in ("/", "~") or normalize(p) in (normalize("~"),):
                return Decision(False, f"Blocked by the eval guard: the command names {p!r}, which is outside the workspace")
            if not _path_allowed(p, policy):
                return Decision(False, f"Blocked by the eval guard: the command names {p!r}, which is outside the workspace, "
                                       "the plugin and the temp dir")
        if RECURSIVE_DELETE.search(command) and re.search(r"(^|\s)\.\.(/|\\|\s|$)", command):
            return Decision(False, "Blocked by the eval guard: recursive delete above the workspace")
        return Decision(True)

    return Decision(True)
