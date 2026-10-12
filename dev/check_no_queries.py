#!/usr/bin/env python3
"""Fail when a skill, reference or script still reaches AgentCM's database.

Skills read AgentCM's files and never query its database: no query.sh or query.ps1, no
query_command from database.yaml, no query wrapper, no psql. Writes go through AgentCM's API.
This scans everything the plugin ships (skills/, reference/, scripts/, bin/) for those names,
so a regression fails the commit gate (dev/gate). The one exception is the refusal itself,
"never run `query.sh` or `query.ps1`": AgentCM's own guide offers query.sh, so the skills name it
to refuse it. Any other mention on the same line still fails.

Usage: bin/construction-python dev/check_no_queries.py [repo root]
Exit 0 when clean; 1 with one line per finding.
"""
import re
import sys
from pathlib import Path

SHIPPED = ("skills", "reference", "scripts", "bin")
SUFFIXES = {".md", ".yaml", ".yml", ".json", ".py", ".sh", ".ps1", ".txt", ""}
QUERY = re.compile(r"query\.(sh|ps1)\b|query_command|query[-_]wrapper|\bpsql\b", re.IGNORECASE)
REFUSAL = re.compile(r"\bnever run `query\.sh` or `query\.ps1`", re.IGNORECASE)


def files(root):
    for top in SHIPPED:
        for p in sorted((root / top).rglob("*")):
            if p.is_file() and p.suffix in SUFFIXES and "__pycache__" not in p.parts:
                yield p


def scan(root):
    findings = []
    for p in files(root):
        text = p.read_text(encoding="utf-8", errors="replace")
        for n, line in enumerate(text.splitlines(), start=1):
            m = QUERY.search(REFUSAL.sub("", line))
            if m:
                findings.append((p.relative_to(root).as_posix(), n, m.group(0), line))
    return findings


def main(argv=None):
    root = Path((argv or sys.argv[1:] or [Path(__file__).resolve().parents[1]])[0]).resolve()
    findings = scan(root)
    for rel, n, hit, line in findings:
        print(f"{rel}:{n}: names '{hit}'\n    {line.strip()[:200]}")
    if findings:
        print(f"FAIL: {len(findings)} reference(s) to AgentCM's database; skills read its files instead")
        return 1
    print("PASS: no skill, reference or script queries AgentCM's database")
    return 0


if __name__ == "__main__":
    sys.exit(main())
