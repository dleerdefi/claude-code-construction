#!/usr/bin/env python3
"""AgentCM mode: nothing written under .construction/ outside skills/ and crops/.

Setup records the fixture as it left it (.eval-api/fixture-baseline.json); a file outside skills/ and
crops/ that is new or differs from it fails. On a regrade the snapshot holds only files the run wrote,
so any such file there fails. crops/ is crop.sh's; that nothing else writes there is graded from the
trace (crops-through-crop-sh).
"""
import hashlib
import json
import os
import sys
from pathlib import Path

workspace = Path(os.environ.get("EVAL_WORKSPACE", "."))
base = workspace / ".construction"
baseline_file = workspace / ".eval-api" / "fixture-baseline.json"
baseline = json.loads(baseline_file.read_text(encoding="utf-8")) if baseline_file.is_file() else {}
bad = []
if base.is_dir():
    for p in sorted(base.rglob("*")):
        rel = p.relative_to(base).as_posix()
        if not p.is_file() or rel.startswith(("skills/", "crops/")):
            continue
        if baseline.get(rel) != hashlib.sha256(p.read_bytes()).hexdigest():
            bad.append(f".construction/{rel}")
if bad:
    print(f"FAIL: {len(bad)} file(s) under .construction/ written outside skills/ and crops/: {bad[:10]}")
    sys.exit(1)
print("PASS: nothing under .construction/ written outside skills/ and crops/")
