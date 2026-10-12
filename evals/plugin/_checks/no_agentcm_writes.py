#!/usr/bin/env python3
"""Nothing under .construction/ outside .construction/skills/: that is AgentCM's (a check every flat-file case runs).

Writes under .construction/skills/ are the plugin's own working data and are allowed in both
modes; anything else under .construction/ fails. A flat-file case's setup puts nothing there,
so every such file was written by the run. Run by the harness, from a case's harness.yaml,
with EVAL_WORKSPACE set to the run's workspace (or its snapshot on a regrade).
"""
import os
import sys
from pathlib import Path

workspace = Path(os.environ.get("EVAL_WORKSPACE", "."))
base = workspace / ".construction"
outside = []
if base.is_dir():
    for p in sorted(base.rglob("*")):
        rel = p.relative_to(base).as_posix()
        if p.is_file() and not rel.startswith("skills/"):
            outside.append(f".construction/{rel}")

if outside:
    print(f"FAIL: {len(outside)} file(s) under .construction/ outside skills/: {outside[:10]}")
    sys.exit(1)
print("PASS: nothing under .construction/ outside .construction/skills/")
