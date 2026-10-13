"""Policy guard for harness runs: decides every shell and file-writing tool call.

On native Windows the harness runs without an OS sandbox, so this is the
confinement: shell commands may only touch the workspace, the plugin, the
toolkit's venv and the system temp dir, and may not reach the network or install
software. The same rules apply on every platform so runs behave the same.

`decide()` is a pure function so it can be unit-tested without an agent; the
runner wraps it in a PreToolUse hook.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

SHELL_TOOLS = ("Bash", "PowerShell")
WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
GUARDED_TOOLS = SHELL_TOOLS + WRITE_TOOLS

NETWORK = r"\b(curl|wget|ssh|scp|sftp|telnet|nc|ncat|psql)\b"
# (pattern, why) — matched against the whole shell command, case-insensitive.
DENY_PATTERNS = [
    (NETWORK, "network or database command"),
    (r"\b(Invoke-WebRequest|iwr|Invoke-RestMethod|irm|Start-BitsTransfer|Invoke-Expression|iex)\b",
     "PowerShell network or eval command"),
    (r"\bpip3?\s+(install|download|uninstall)\b", "package installation"),
    (r"\bnpm\s+(install|i|exec|x|uninstall)\b|\bnpx\b", "package installation"),
    (r"\bgit\s+(push|clone|fetch|pull|remote)\b", "git network command"),
    (r"\b(sudo|runas|shutdown|reboot|diskpart)\b", "privileged command"),
]
# A case may let curl reach listed addresses (harness.yaml `allow_urls`: the agentcm-mode cases'
# stand-in for AgentCM's API). These curl options would send a request somewhere else.
HTTP_URL = re.compile(r"\bhttps?://[^\s\"'|&;<>()]+", re.IGNORECASE)
CURL_ELSEWHERE = re.compile(  # -K config file, -x proxy (also inside -sSx); -X, the method, is fine
    r"(^|\s)(-[A-Za-z]*[Kx][A-Za-z]*|--config|--proxy|--socks\S*|--connect-to|--resolve|--next|-:)(\s|=|$)")
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
    allow_urls: tuple[str, ...] = ()  # address prefixes curl may reach, e.g. "http://127.0.0.1:47817/"

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


_HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n[ \t]*\2[ \t]*(?=\n|$)", re.DOTALL)


def shell_paths(command: str) -> list[str]:
    """Absolute and home-relative paths named in a shell command (quoted or bare).

    Heredoc bodies are data (YAML, JSON, prose), not paths the shell opens, so they are skipped,
    and so are http(s) addresses (`//127.0.0.1:47817/api/...` is not a path from the root).
    """
    command = HTTP_URL.sub(" ", _HEREDOC.sub(" ", command))
    found: list[str] = []
    for q in _QUOTED.finditer(command):
        text = q.group(1) if q.group(1) is not None else q.group(2)
        if _QUOTED_PATH.match(text):
            found.append(text.strip())
    unquoted = _QUOTED.sub(" ", command)
    found += [m.group(1) for m in _PATH_TOKEN.finditer(unquoted)]
    return [p for p in found if p not in ("/", "~")] + ([p for p in found if p in ("/", "~")])


def curl_allowed(command: str, policy: Policy) -> bool:
    """curl, and no other network command, with every address it names under one of the case's
    allow_urls and no option that would send it elsewhere."""
    if not policy.allow_urls:
        return False
    if {m.group(0).lower() for m in re.finditer(NETWORK, command, re.IGNORECASE)} != {"curl"}:
        return False
    if CURL_ELSEWHERE.search(command):
        return False
    urls = HTTP_URL.findall(command)
    return bool(urls) and all(any(u.startswith(p) for p in policy.allow_urls) for u in urls)


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
            if m and pattern == NETWORK and curl_allowed(command, policy):
                continue
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


# --- after the run: writes outside the project folder ----------------------------------------------
# The guard lets shell commands touch the temp dir and the plugin (the toolkit needs them), so a skill
# that writes a page image to /tmp is not stopped. These find such writes in the trace afterwards.

_REDIRECT = re.compile(r"(?<![<>])(?:\d|&)?>>?\s*(\"[^\"]*\"|'[^']*'|[^\s;&|<>()]+)")
_OUTPUT_OPTION = re.compile(r"(?:^|\s)(?:--output-dir|--output|--annotations|-o)(?:\s+|=)(\"[^\"]*\"|'[^']*'|[^\s;&|<>()]+)")
_ASSIGNMENT = re.compile(r"^([A-Za-z_]\w*)=(.*)$", re.DOTALL)
_VAR = re.compile(r"\$\{(\w+)\}|\$(\w+)|%(\w+)%")
_TEMP_VARS = {"TMP", "TEMP", "TMPDIR"}
WRITE_COMMANDS = {"mkdir", "touch", "rm", "rmdir", "tee"}  # every operand is written
LAST_OPERAND = {"cp", "mv"}  # the destination
READ_ONLY = {"grep", "egrep", "fgrep", "rg", "head", "tail", "cut", "awk", "tr", "wc", "ls", "cat", "find", "jq", "uniq"}


def _unquote(s: str) -> str:
    return s[1:-1] if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'" else s


def _segments(command: str) -> list[tuple[str, str]]:
    """The command's simple commands, split at ; && || | and newlines outside quotes. Each comes with a
    mask of the same length whose quoted characters are blanked, so a `>` inside a string is not a redirect."""
    out, seg, mask = [], [], []
    quote, i = "", 0
    while i < len(command):
        c = command[i]
        if quote:
            seg.append(c); mask.append(" " if c != quote else c)
            if c == "\\" and quote == '"' and i + 1 < len(command):
                seg.append(command[i + 1]); mask.append(" "); i += 1
            elif c == quote:
                quote = ""
        elif c in "\"'":
            quote = c; seg.append(c); mask.append(c)
        elif c == "\\" and i + 1 < len(command):
            seg += [c, command[i + 1]]; mask += [" ", " "]; i += 1
        elif c in ";|\n" or (c == "&" and command[i + 1:i + 2] == "&"):
            out.append(("".join(seg), "".join(mask))); seg, mask = [], []
            if command[i + 1:i + 2] in ("&", "|") and c in "&|":
                i += 1
        else:
            seg.append(c); mask.append(c)
        i += 1
    out.append(("".join(seg), "".join(mask)))
    return [(s, m) for s, m in out if s.strip()]


def _words(segment: str) -> list[str]:
    try:
        return shlex.split(segment, posix=True)
    except ValueError:
        return segment.split()


def _expand(word: str, variables: dict[str, str]) -> str | None:
    """The word with known variables put in; None when it names one we cannot know (the target is then unknown)."""
    unknown = False

    def sub(m):
        nonlocal unknown
        name = m.group(1) or m.group(2) or m.group(3)
        if name.upper() in _TEMP_VARS:
            return tempfile.gettempdir()
        if name in ("HOME", "USERPROFILE"):
            return str(Path.home())
        if name in variables:
            return variables[name]
        unknown = True
        return ""

    out = _VAR.sub(sub, word)
    return None if unknown else out


def _absolute(p: str) -> bool:
    return p.startswith(("/", "~", "\\")) or bool(re.match(r"^[A-Za-z]:", p))


def shell_write_targets(command: str, workspace: str) -> list[str]:
    """Paths a shell command writes (redirects, -o/--output, mkdir, touch, rm, tee, cp/mv destinations,
    sed -i) that lie outside the workspace. Relative paths follow the command's own cd; a path behind a
    variable the command never sets is skipped rather than guessed."""
    ws = normalize(workspace)
    cwd: str | None = ws
    variables: dict[str, str] = {}
    outside: list[str] = []
    body = _HEREDOC.sub(" ", command)

    def check(raw: str) -> None:
        word = _expand(_unquote(raw.strip()), variables)
        if not word or word.startswith("&") or word == "-":
            return
        if _absolute(word):
            target = normalize(word)
        elif cwd is None:
            return
        else:
            target = normalize(cwd + "/" + word)
        if target.lower().startswith("/dev/") or target.lower() in ("/dev/null", "nul"):
            return
        if not _is_under(target, ws):
            outside.append(target)

    for seg, mask in _segments(body):
        redirects = list(_REDIRECT.finditer(mask))
        for m in redirects:
            check(seg[m.start(1):m.end(1)])
        bare = seg
        for m in reversed(redirects):
            bare = bare[:m.start()] + " " + bare[m.end():]
        words = _words(bare.strip())
        first = next((w for w in words if not _ASSIGNMENT.match(w)), "")
        if os.path.basename(first) not in READ_ONLY:  # grep -o is not an output file
            for m in _OUTPUT_OPTION.finditer(mask):
                check(seg[m.start(1):m.end(1)])
        while words and _ASSIGNMENT.match(words[0]):
            name, value = _ASSIGNMENT.match(words[0]).groups()
            expanded = _expand(value, variables)
            if expanded is not None:
                variables[name] = expanded
            else:
                variables.pop(name, None)
            words = words[1:]
        if not words:
            continue
        cmd, args = os.path.basename(words[0]), words[1:]
        operands = [a for a in args if not a.startswith("-")]
        if cmd == "cd":
            target = _expand(operands[0], variables) if operands else str(Path.home())
            if target is None:
                cwd = None
            elif _absolute(target):
                cwd = normalize(target)
            elif cwd is not None:
                cwd = normalize(cwd + "/" + target)
        elif cmd in WRITE_COMMANDS:
            for a in operands:
                check(a)
        elif cmd in LAST_OPERAND and len(operands) >= 2:
            check(operands[-1])
        elif cmd == "sed" and any(a == "-i" or a.startswith("-i") for a in args) and operands:
            check(operands[-1])
    return outside


def outside_writes(tool_uses: list[dict], guard_log: list[dict], workspace: str) -> list[str]:
    """Every shell write outside the workspace in a run, skipping the calls the guard refused (they never ran).
    The Write tools need no check here: the guard refuses any of them outside the workspace."""
    refused = {json.dumps(g.get("input"), sort_keys=True, default=str) for g in guard_log if not g.get("allow", True)}
    found: list[str] = []
    for e in tool_uses:
        if e.get("name") != "Bash":
            continue
        if json.dumps(e.get("input"), sort_keys=True, default=str) in refused:
            continue
        found += shell_write_targets(str((e.get("input") or {}).get("command", "")), workspace)
    return found
