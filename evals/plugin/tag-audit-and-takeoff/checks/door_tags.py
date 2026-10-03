"""Compare the door tags detected on A101 with the door numbers printed on the sheet.

Ground truth: the 17 ground-floor doors in the A500 schedule, of which 16 are printed on
A101, plus three apparatus-level doors that also appear on A101. The check reads the
QTO JSON (instance tag text and line-item designations) and scores recall of the 16.
"""
import glob
import json
import os
import re
import sys
from pathlib import Path

WORKSPACE = Path(os.environ["EVAL_WORKSPACE"])
GT = Path(os.environ["EVAL_CASE_DIR"]).parent / "_fixtures" / "sanibel" / "ground_truth" / "a101_door_tags.json"


def tags_in(data) -> set[str]:
    found = set()

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ("tag_text", "designation", "tag", "door_number", "mark") and isinstance(v, (str, int)):
                    found.add(str(v).strip().upper())
                else:
                    walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(data)
    return {t for t in found if re.fullmatch(r"\d{3}[A-Z]?", t)}


def main() -> int:
    truth = json.loads(GT.read_text(encoding="utf-8"))
    printed = {d for d, n in truth["printed_on_sheet"].items() if n}
    also = set(truth.get("other_level_doors_printed_on_sheet", []))
    files = sorted(glob.glob(str(WORKSPACE / ".construction" / "skills" / "tag-audit-and-takeoff" / "qto" / "*.json")))
    if not files:
        print("no QTO JSON under .construction/skills/tag-audit-and-takeoff/qto/"); print("score: 0"); return 1
    data = json.loads(Path(files[-1]).read_text(encoding="utf-8"))
    detected = tags_in(data)
    hits = printed & detected
    extra = detected - printed - also
    recall = len(hits) / len(printed)
    precision = (len(detected) - len(extra)) / len(detected) if detected else 0
    keys = sorted(data.keys()) if isinstance(data, dict) else []
    print(f"QTO file: {Path(files[-1]).name}; top-level keys: {keys}")
    print(f"detected door numbers: {sorted(detected)}")
    print(f"recall {len(hits)}/{len(printed)} ({recall:.2f}); not in schedule for this sheet: {sorted(extra)} (precision {precision:.2f})")
    score = round(0.7 * recall + 0.3 * precision, 3)
    print(f"score: {score}")
    return 0 if recall >= 0.8 and precision >= 0.7 else 1


if __name__ == "__main__":
    sys.exit(main())
