"""Check the code-researcher working files against the facts printed on sheet G010.

G010 states: Florida Building Code 8th Edition (2023); mixed occupancy B, R-2 and S-2;
Type V-B construction, sprinklered; AHJ City of Sanibel. Offline, adoption cannot be
verified online, so no code may be marked confirmed.
"""
import glob
import os
import re
import sys
from pathlib import Path

import yaml

WORKSPACE = Path(os.environ["EVAL_WORKSPACE"])
DIR = WORKSPACE / ".construction" / "skills" / "code-researcher"


def load(name):
    p = DIR / name
    if not p.exists():
        return None
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        print(f"{name}: not valid YAML ({e})")
        return None


def text_of(data) -> str:
    return yaml.safe_dump(data, default_flow_style=False) if data is not None else ""


def main() -> int:
    ctx = load("project_context.yaml")
    jur = load("jurisdiction.yaml")
    ctx_text, jur_text = text_of(ctx), text_of(jur)
    report_files = glob.glob(str(WORKSPACE / "Code_Research_Report*.md"))
    report = Path(report_files[0]).read_text(encoding="utf-8", errors="replace") if report_files else ""
    everything = ctx_text + jur_text + report

    checks = {
        "project_context.yaml exists and parses": ctx is not None,
        "jurisdiction is Sanibel / Florida": bool(re.search(r"sanibel", ctx_text, re.I)) and bool(re.search(r"\bflorida\b|\bFL\b", ctx_text, re.I)),
        "Florida Building Code named": bool(re.search(r"florida building code|\bFBC\b", everything, re.I)),
        "edition read from G010 (8th / 2023)": bool(re.search(r"8th|2023", ctx_text + jur_text, re.I)),
        "occupancies from G010 (B, R-2, S-2 or mixed)": bool(re.search(r"\bR-?2\b|\bS-?2\b|mixed", ctx_text, re.I)),
        "construction type V-B": bool(re.search(r"\bV-?B\b|type\s*5B", ctx_text, re.I)),
        "sprinklered noted": bool(re.search(r"sprinkler", ctx_text, re.I)),
        "nothing marked confirmed offline": not re.search(r"confidence:\s*confirmed", jur_text, re.I),
        "uncertainty expressed in the report": bool(re.search(r"uncertain|needs_review|needs review|could not (be )?verif", report, re.I)) if report else False,
    }
    passed = sum(checks.values())
    for name, ok in checks.items():
        print(f"  {'PASS' if ok else 'FAIL'} {name}")
    score = round(passed / len(checks), 3)
    print(f"score: {score}")
    return 0 if score >= 0.85 else 1


if __name__ == "__main__":
    sys.exit(main())
