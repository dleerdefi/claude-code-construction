"""The drawing index's two planted mismatches are in sheet-splitter's findings, and the summary names the file.

G-001's drawing index (make_fixtures.py, DRAWING_INDEX) lists A-101 as FIRST FLOOR REFLECTED CEILING PLAN, while
its title block says FIRST FLOOR PLAN, and writes S-101 as S101. A-201 and G-001 match their title blocks (A-201's
bookmark is abbreviated, but a bookmark is not the index). The run passes when a finding under
.construction/skills/sheet-splitter/findings/ holds both mismatches, the title one with a suggested RFI, flags
neither matching sheet, and the final message names the finding's file.
"""
import json
import os
import re
import sys
from pathlib import Path

WORKSPACE = Path(os.environ["EVAL_WORKSPACE"])
FINDINGS = WORKSPACE / ".construction" / "skills" / "sheet-splitter" / "findings"


def key(number) -> str:
    """A sheet number with spaces, hyphens and periods dropped: S101 and S-101 are the same sheet."""
    return re.sub(r"[\s.\-]+", "", str(number or "")).upper()


def field(entry, side, name):
    part = entry.get(side)
    return str(part.get(name) or "") if isinstance(part, dict) else ""


def sheet_of(entry) -> str:
    return key(entry.get("sheet") or field(entry, "title_block", "number") or field(entry, "index", "number"))


def final_message() -> str:
    """The run's last answer: the result entry's text and the last assistant text, together, since the runner
    keeps only the first 4000 characters of the result (RESULT_TEXT_LIMIT) and a long sheet table can push the
    file's name past them."""
    result, last_text = "", ""
    for line in open(os.environ["EVAL_TRACE"], encoding="utf-8"):
        e = json.loads(line)
        if e.get("type") == "result":
            result = e.get("result") or ""
        elif e.get("type") == "assistant_text":
            last_text = e.get("text") or ""
    return result + "\n" + last_text


def main() -> int:
    files = {}
    for f in sorted(FINDINGS.glob("*.json")) if FINDINGS.is_dir() else []:
        try:
            data = json.loads(f.read_text(encoding="utf-8")).get("data") or {}
        except (ValueError, AttributeError):
            continue
        entries = [m for m in data.get("mismatches") or [] if isinstance(m, dict)] if isinstance(data, dict) else []
        if entries:
            files[f.name] = entries
    entries = [m for ms in files.values() for m in ms]

    number = any(sheet_of(m) == "S101" and field(m, "index", "number").strip().upper() == "S101" for m in entries)
    title = [m for m in entries if sheet_of(m) == "A101" and "REFLECTED" in field(m, "index", "title").upper()]
    rfi = any(str(m.get("suggested_rfi") or "").strip() for m in title)
    spurious = sorted({sheet_of(m) for m in entries if sheet_of(m) in ("G001", "A201")})
    message = final_message()
    named = bool(files) and all(name in message for name in files)

    parts = {
        "S-101 number (index S101)": number,
        "A-101 title (index REFLECTED CEILING PLAN)": bool(title),
        "suggested RFI on the A-101 title": rfi,
        "no mismatch on G-001 or A-201": not spurious,
        "final message names the finding's file": named,
    }
    weights = {"S-101 number (index S101)": 0.25, "A-101 title (index REFLECTED CEILING PLAN)": 0.25,
               "suggested RFI on the A-101 title": 0.2, "no mismatch on G-001 or A-201": 0.1,
               "final message names the finding's file": 0.2}
    print(f"finding files with mismatches: {sorted(files) or 'none'}; entries: {len(entries)}")
    for name, ok in parts.items():
        print(f"  {'PASS' if ok else 'FAIL'} {name}")
    if spurious:
        print(f"  flagged sheets that match the index: {spurious}")
    print(f"score: {round(sum(weights[n] for n, ok in parts.items() if ok), 3)}")
    return 0 if all(parts.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
