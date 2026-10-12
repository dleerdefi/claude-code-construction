#!/usr/bin/env python3
"""Record every file under .construction/ outside skills/ and crops/ with its hash, as setup left it, in
.eval-api/fixture-baseline.json: the writes check compares the run's end state against it."""
import hashlib
import json
import sys
from pathlib import Path

ws = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
base = ws / ".construction"
files = {}
for p in sorted(base.rglob("*")):
    rel = p.relative_to(base).as_posix()
    if p.is_file() and not rel.startswith(("skills/", "crops/")):
        files[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
out = ws / ".eval-api" / "fixture-baseline.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(files, indent=1), encoding="utf-8")
print(f"baseline: {len(files)} file(s) under .construction/")
