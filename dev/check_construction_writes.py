#!/usr/bin/env python3
"""Fail when a skill's instructions or a script write under .construction/ outside skills/.

AgentCM is the only writer of .construction/, apart from .construction/skills/ (the plugin's
working data, both modes) and .construction/crops/, which AgentCM's own crop.sh writes. This
scans every SKILL.md, reference and script for writes anywhere else, so a regression fails the
commit gate (dev/gate) instead of reaching an eval or a user.

It is a static check, so it looks for the written forms that occur in this repo:
- Markdown and YAML: a write verb followed, within the same sentence, by a disallowed path
  ("write ... to `.construction/spec_text/`"); and any "move" on a line that names a disallowed
  path, since moving takes files out of AgentCM's area. Sentences that say never, not, don't or
  describe older versions are skipped.
- Python: a write, rename or delete on a disallowed path, followed through simple assignments
  (LEGACY = ".construction/issues"; legacy = Path(LEGACY); legacy.rename(...)).
- Shell: redirection, mkdir, cp/mv/rm and tee onto a disallowed path.

Usage: bin/construction-python dev/check_construction_writes.py [repo root]
Exit 0 when clean; 1 with one line per finding.
"""
import re
import sys
from pathlib import Path

ALLOWED_PREFIXES = ("skills/", "crops/")

# Known lines waiting for a queued change, each with why. A test fails when one no longer matches.
KNOWN = []

PATH = re.compile(r"\.construction/([A-Za-z0-9_.{}<>*\[\]-][^\s`'\"),;]*)?")
WRITE_VERB = re.compile(
    r"\b(write|writes|writing|written|save|saves|saved|put|puts|store|stores|stored|create|creates|created|"
    r"append|appends|appended|add|adds|record|records|output|outputs|mkdir|copy|copies|copied|goes|go)\b"
    r"|--output(?:-dir|-file)?\b|--dir\b", re.IGNORECASE)
MOVE = re.compile(r"\bmov(e|es|ed|ing)\b", re.IGNORECASE)
NEGATION = re.compile(
    r"\b(never|not|don't|do not|doesn't|does not|nothing|no skill|isn't|aren't|cannot|can't|mustn't|only agentcm|"
    r"agentcm writes|agentcm regenerates|agentcm is the only writer|read it|leave the old|left as it is)\b",
    re.IGNORECASE)
HISTORICAL = re.compile(r"\b(older versions?|before v0|previously|used to)\b", re.IGNORECASE)
NOUN_BEFORE = re.compile(r"\b(a|an|the|each|every|one|no)\s+$", re.IGNORECASE)  # "a write names ..." is a noun
NOUN_AFTER = re.compile(r"^\s+endpoints?\b", re.IGNORECASE)  # "its write endpoints" names the API
NEGATED_MOVE = re.compile(r"\b(never|not|don't|do not|no need to)\s+(\w+\s+){0,2}$", re.IGNORECASE)


def disallowed(rest):
    """`rest` is what follows `.construction/`: allowed only under skills/ or crops/."""
    return not (rest or "").startswith(ALLOWED_PREFIXES)


def sentences(line):
    return re.split(r"(?<=[.;:!?])\s+(?=[A-Z`*(\-])", line)


def scan_text(rel, text):
    findings = []
    for n, line in enumerate(text.splitlines(), start=1):
        bad_paths = [m for m in PATH.finditer(line) if disallowed(m.group(1))]
        if not bad_paths:
            continue
        moves = [m for m in MOVE.finditer(line) if not NEGATED_MOVE.search(line[:m.start()])]
        if moves:
            findings.append((rel, n, "moves files out of .construction/ (copy them into .construction/skills/ instead)", line))
            continue
        for s in sentences(line):
            if NEGATION.search(s) or HISTORICAL.search(s):
                continue
            for verb in WRITE_VERB.finditer(s):
                if NOUN_BEFORE.search(s[:verb.start()]) or NOUN_AFTER.search(s[verb.end():]):
                    continue
                if any(disallowed(p.group(1)) for p in PATH.finditer(s[verb.end():])):
                    findings.append((rel, n, f"writes under .construction/ outside skills/ ('{verb.group(0)}')", line))
                    break
            else:
                continue
            break
    return findings


PY_STRING_PATH = re.compile(r"""["']\.construction/([^"']*)["']""")
PY_JOIN_PATH = re.compile(r"""["']\.construction["']\s*[,/]\s*["']([^"']+)["']""")
PY_ASSIGN = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$")
PY_WRITE_ON_NAME = r"(?:\b{n}\s*\.\s*(?:rename|replace|unlink|rmdir|write_text|write_bytes|mkdir|touch)\s*\(|" \
                   r"\b(?:os\.(?:rename|replace|remove|unlink|rmdir|makedirs|mkdir)|shutil\.(?:move|rmtree))\s*\(\s*{n}\b|" \
                   r"\bopen\s*\(\s*{n}\b[^)]*['\"][wax]|" \
                   r"\bshutil\.(?:copy|copy2|copyfile|copytree)\s*\([^,]+,\s*{n}\b)"
PY_WRITE_LITERAL = re.compile(
    r"\b(open\s*\([^)]*['\"][wax]|\.write_text|\.write_bytes|\.mkdir|makedirs|\.rename|\.replace\(|"
    r"os\.rename|os\.remove|shutil\.(move|rmtree|copy|copy2|copyfile|copytree))")


def scan_python(rel, text):
    lines = text.splitlines()
    tracked = set()
    changed = True
    while changed:  # names holding a disallowed path, followed through simple assignments
        changed = False
        for line in lines:
            m = PY_ASSIGN.match(line)
            if not m or m.group(1) in tracked:
                continue
            rhs = m.group(2)
            hit = any(disallowed(p) for p in PY_STRING_PATH.findall(rhs)) or \
                any(disallowed(p + "/") for p in PY_JOIN_PATH.findall(rhs)) or \
                any(re.search(rf"\b{re.escape(t)}\b", rhs) for t in tracked)
            if hit:
                tracked.add(m.group(1)); changed = True
    findings = []
    for n, line in enumerate(lines, start=1):
        code = line.split("#", 1)[0]
        literal_bad = any(disallowed(p) for p in PY_STRING_PATH.findall(code)) or \
            any(disallowed(p + "/") for p in PY_JOIN_PATH.findall(code))
        if literal_bad and PY_WRITE_LITERAL.search(code):
            findings.append((rel, n, "writes under .construction/ outside skills/", line))
            continue
        for t in tracked:
            if re.search(PY_WRITE_ON_NAME.format(n=re.escape(t)), code):
                findings.append((rel, n, f"writes, moves or deletes {t} (a path under .construction/ outside skills/)", line))
                break
    return findings


SH_WRITE = re.compile(r"(>>?|\btee\b(\s+-a)?|\bmkdir\b(\s+-p)?|\b(cp|mv|rm)\b[^|;&]*?)\s*[\"']?(?:\./)?\.construction/(\S*)")


def scan_shell(rel, text):
    findings = []
    for n, line in enumerate(text.splitlines(), start=1):
        code = line.split("#", 1)[0]
        for m in SH_WRITE.finditer(code):
            if disallowed(m.group(5).strip("\"'")):
                findings.append((rel, n, "writes under .construction/ outside skills/", line))
                break
    return findings


def files(root):
    for pattern in ("skills/*/SKILL.md", "skills/*/references/**/*", "reference/**/*",
                    "scripts/**/*.py", "scripts/**/*.sh", "skills/*/scripts/**/*.py", "skills/*/scripts/**/*.sh"):
        for p in sorted(root.glob(pattern)):
            if p.is_file() and p.suffix in (".md", ".yaml", ".yml", ".json", ".py", ".sh") and "__pycache__" not in p.parts:
                yield p


def scan(root):
    findings = []
    for p in files(root):
        rel = p.relative_to(root).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace")
        if p.suffix == ".py":
            findings += scan_python(rel, text)
        elif p.suffix == ".sh":
            findings += scan_shell(rel, text)
        else:
            findings += scan_text(rel, text)
    known = [f for f in findings if any(f[0] == k[0] and k[1] in f[3] for k in KNOWN)]
    return [f for f in findings if f not in known], known


def main(argv=None):
    root = Path((argv or sys.argv[1:] or [Path(__file__).resolve().parents[1]])[0]).resolve()
    findings, known = scan(root)
    for rel, n, why, line in findings:
        print(f"{rel}:{n}: {why}\n    {line.strip()[:200]}")
    for rel, n, why, line in known:
        reason = next(k[2] for k in KNOWN if k[0] == rel and k[1] in line)
        print(f"(known, waiting) {rel}:{n}: {reason}")
    if findings:
        print(f"FAIL: {len(findings)} write(s) under .construction/ outside skills/")
        return 1
    print("PASS: no writes under .construction/ outside skills/ (crops/ is crop.sh's)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
