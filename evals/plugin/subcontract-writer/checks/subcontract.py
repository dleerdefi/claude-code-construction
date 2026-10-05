"""Check the subcontract against the awarded bid and the template's planted defects."""
import glob
import json
import os
import re
import sys
from pathlib import Path

import docx

WORKSPACE = Path(os.environ["EVAL_WORKSPACE"])
GT = Path(os.environ["EVAL_CASE_DIR"]).parent / "_fixtures" / "synthetic" / "bids_ground_truth" / "bids" / "gulfshore_resilient_floors_llc.json"


def docx_text(path: Path) -> str:
    d = docx.Document(path)
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for r in t.rows:
            parts += [c.text for c in r.cells]
    return "\n".join(parts)


def main() -> int:
    files = sorted(glob.glob(str(WORKSPACE / "Subcontract_Gulfshore_EB-24009*.docx")))
    if not files:
        print("no Subcontract_Gulfshore_EB-24009*.docx"); print("score: 0"); return 1
    text = docx_text(Path(files[-1]))
    low = text.lower()
    bid = json.loads(GT.read_text(encoding="utf-8"))
    tdata = {}
    tfiles = sorted(glob.glob(str(WORKSPACE / "template_data*.json")))
    if tfiles:
        try:
            tdata = json.loads(Path(tfiles[-1]).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    flags = json.dumps(tdata, default=str).lower()
    exclusions_hit = sum(1 for e in bid["scope_exclusions"] if e.split()[0].lower() in low and e.split()[-1].lower() in low)
    checks = {
        "subcontractor named from the bid": "gulfshore resilient floors" in low,
        "contract sum from the bid ($431,475)": "431,475" in text,
        "subcontract number": "EB-24009" in text,
        "indemnity fixed to 'sole negligence'": "sole negligence" in low,
        "indemnity defect flagged in template_data legal_flags": "legal_flags" in flags and ("sole" in flags or "indemn" in flags),
        "no stale example parties carried over": not any(s in low for s in ("oldco drywall", "harbor view office", "eb-21001")),
        "no unfilled placeholders": not re.search(r"\[(CONTRACT SUM|SUBCONTRACTOR|DATE|SUBCONTRACT NUMBER|SCHEDULE|SUBMITTALS|WARRANTY|INSERT)\]|<<SCOPE>>|\[Article \d+ content not provided\]", text),
        "spec sections referenced": "09 65 40" in text and "09 30 00" in text,
        "bid exclusions carried into the scope": exclusions_hit >= 2,
        "liquidated damages rate": "1,500" in text,
        "warranty article not a placeholder": re.search(r"(?i)article 11", text) is not None and "one year" in low or "1 year" in low or "one-year" in low,
    }
    passed = sum(checks.values())
    for k, ok in checks.items():
        print(f"  {'PASS' if ok else 'FAIL'} {k}")
    score = round(passed / len(checks), 3)
    print(f"score: {score}")
    return 0 if score >= 0.85 else 1


if __name__ == "__main__":
    sys.exit(main())
