"""Check the exported RFI: template mode, fields filled, facts right, registry escalated."""
import glob
import json
import os
import re
import sys
from pathlib import Path

import docx

WORKSPACE = Path(os.environ["EVAL_WORKSPACE"])
MARKER = "EXAMPLE BUILDERS, INC. — REQUEST FOR INFORMATION — FORM EB-RFI-02"


def docx_text(path: Path) -> str:
    d = docx.Document(path)
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for r in t.rows:
            parts += [c.text for c in r.cells]
    return "\n".join(parts)


def main() -> int:
    files = sorted(glob.glob(str(WORKSPACE / "RFI-001*.docx")))
    if not files:
        print("no RFI-001*.docx"); print("score: 0"); return 1
    text = docx_text(Path(files[-1]))
    issues = [json.loads(Path(p).read_text(encoding="utf-8")) for p in glob.glob(str(WORKSPACE / ".construction/skills/issues/ISS-*.json"))]
    checks = {
        "template mode (firm marker present)": MARKER in text or "FORM EB-RFI-02" in text,
        "not the generic format": "RESPONSE (to be completed" not in text,
        "no unfilled placeholders": not re.search(r"\[(DESCRIPTION|SUGGESTED RESOLUTION|IMPACT IF NOT RESOLVED|ATTACHMENTS)\]", text),
        "project and number filled": "Sanibel Fire and Rescue Station 172" in text and "2023820" in text,
        "parties filled": "Example Builders" in text and "Schenkel Shultz" in text,
        "cites A500 and Addendum 01": "A500" in text and re.search(r"(?i)addendum\s*(no\.?\s*)?0?1", text) is not None,
        "states the revised width and hardware set": "3'-6\"" in text.replace("’", "'").replace("″", '"').replace(" ", "") or "3'-6" in text or "3' - 6\"" in text,
        "mentions hardware set 11": re.search(r"(?i)hardware\s*(set)?\s*(no\.?)?\s*11\b", text) is not None,
        "registry record exists": bool(issues),
        "registry record escalated to the RFI": any(str(i.get("status")) in ("escalated", "resolved") and "RFI-001" in json.dumps(i) for i in issues),
    }
    for name, ok in checks.items():
        print(f"  {'PASS' if ok else 'FAIL'} {name}")
    score = round(sum(checks.values()) / len(checks), 3)
    print(f"score: {score}")
    return 0 if score >= 0.9 else 1


if __name__ == "__main__":
    sys.exit(main())
