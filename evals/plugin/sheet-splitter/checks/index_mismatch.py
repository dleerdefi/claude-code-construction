"""The drawing index's planted mismatches are in sheet-splitter's findings and, where an RFI is due, in the issue
registry; the summary names the finding's file.

G-001's drawing index (make_fixtures.py, DRAWING_INDEX) lists A-101 as FIRST FLOOR REFLECTED CEILING PLAN, while its
title block says FIRST FLOOR PLAN; writes S-101 as S101; lists S-201 ROOF FRAMING PLAN, the one S sheet the folder
lacks (S-101 is there); lists A-301 and A-401, two of its four A sheets, which the folder lacks; and lists L-101 and
L-501, a discipline with no sheet in the folder. A-201 and G-001 match their title blocks (A-201's bookmark is
abbreviated, but a bookmark is not the index).

David's rule (2026-10-28): a missing sheet is an RFI only when every other sheet of its discipline on the index is in
the folder. Two or more missing, or the whole discipline, is one folder finding per discipline listing them, with no
RFI and no issue.

The run passes when a finding under .construction/skills/sheet-splitter/findings/ holds the mismatches; the A-101 title
and the missing S-201 each carry a suggested RFI and an issue in .construction/skills/issues/ from sheet-splitter;
S-101's number is a note, with neither; A-301 with A-401 ("2 of 4") and L-101 with L-501 ("2 of 2") are each one folder
finding, with no RFI and no issue; neither matching sheet is flagged; and the final message names the finding's file.
"""
import json
import os
import re
import sys
from pathlib import Path

WORKSPACE = Path(os.environ["EVAL_WORKSPACE"])
FINDINGS = WORKSPACE / ".construction" / "skills" / "sheet-splitter" / "findings"
ISSUES = WORKSPACE / ".construction" / "skills" / "issues"


def key(number) -> str:
    """A sheet number with spaces, hyphens and periods dropped: S101 and S-101 are the same sheet."""
    return re.sub(r"[\s.\-]+", "", str(number or "")).upper()


def field(entry, side, name):
    part = entry.get(side)
    return str(part.get(name) or "") if isinstance(part, dict) else ""


def sheet_of(entry) -> str:
    return key(entry.get("sheet") or field(entry, "title_block", "number") or field(entry, "index", "number"))


def has_rfi(entry) -> bool:
    return bool(str(entry.get("suggested_rfi") or "").strip())


def mentions(issue, sheet_key) -> bool:
    """The issue names the sheet in its sheets, description or RFI subject (S-101 matches S101, not S-201)."""
    sheets = (issue.get("location") or {}).get("sheets") or []
    if any(key(s) == sheet_key for s in sheets):
        return True
    text = " ".join(str(issue.get(f) or "") for f in ("description", "potential_rfi_subject"))
    letters, digits = re.match(r"([A-Z]+)(.*)", sheet_key).groups()
    return bool(re.search(rf"\b{letters}[\s.\-]?{re.escape(digits)}\b", text, re.I))


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


def folder_finding(entries, issues, discipline, numbers, listed, words=None) -> bool:
    """The discipline's missing sheets are one entry naming them all and the count ("2 of 4"), with no RFI on it or
    on any entry for those sheets, and no issue from sheet-splitter about them."""
    about = [m for m in entries if re.search(rf"\b{discipline}[\s.\-]?({'|'.join(numbers)})\b", json.dumps(m))]
    whole = [m for m in about if all(re.search(rf"\b{discipline}[\s.\-]?{n}\b", json.dumps(m)) for n in numbers)
             and re.search(rf"\b{len(numbers)}\s+of\s+(?:the\s+)?{listed}\b", json.dumps(m))]
    gap = re.compile(rf"\b{discipline} sheets\b" + (rf"|{words}" if words else ""), re.I)
    return (len(about) == 1 and len(whole) == 1 and not any(has_rfi(m) for m in about)
            and not any(any(mentions(i, f"{discipline}{n}") for n in numbers) or gap.search(json.dumps(i))
                        for i in issues))


def load(folder, pattern):
    out = {}
    for f in sorted(folder.glob(pattern)) if folder.is_dir() else []:
        try:
            out[f.name] = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
    return out


def main() -> int:
    files = {}
    for name, finding in load(FINDINGS, "*.json").items():
        data = finding.get("data") if isinstance(finding, dict) else None
        entries = [m for m in (data or {}).get("mismatches") or [] if isinstance(m, dict)] if isinstance(data, dict) else []
        if entries:
            files[name] = entries
    entries = [m for ms in files.values() for m in ms]
    issues = [i for i in load(ISSUES, "ISS-*.json").values() if isinstance(i, dict) and i.get("source_skill") == "sheet-splitter"]

    number = [m for m in entries if sheet_of(m) == "S101" and field(m, "index", "number").strip().upper() == "S101"]
    title = [m for m in entries if sheet_of(m) == "A101" and "REFLECTED" in field(m, "index", "title").upper()]
    missing = [m for m in entries if sheet_of(m) == "S201" and not field(m, "title_block", "number")]
    spurious = sorted({sheet_of(m) for m in entries if sheet_of(m) in ("G001", "A201")})
    arch_gap = folder_finding(entries, issues, "A", ("301", "401"), 4)
    landscape = folder_finding(entries, issues, "L", ("101", "501"), 2, r"landscape")
    message = final_message()

    parts = {  # name: (passed, weight)
        "S-101 number (index S101)": (bool(number), 0.1),
        "S-101 is a note: no suggested RFI, no issue": (bool(number) and not any(has_rfi(m) for m in number)
                                                       and not any(mentions(i, "S101") for i in issues), 0.05),
        "A-101 title (index REFLECTED CEILING PLAN)": (bool(title), 0.1),
        "suggested RFI on the A-101 title": (any(has_rfi(m) for m in title), 0.1),
        "S-201 listed but not in the set, with a suggested RFI": (any(has_rfi(m) for m in missing), 0.1),
        "issues from sheet-splitter for A-101 and S-201": (any(mentions(i, "A101") for i in issues)
                                                          and any(mentions(i, "S201") for i in issues), 0.1),
        "A-301 and A-401: one folder finding (2 of 4), no RFI, no issue": (arch_gap, 0.15),
        "L-101 and L-501: one folder finding (2 of 2), no RFI, no issue": (landscape, 0.1),
        "no mismatch on G-001 or A-201": (not spurious, 0.05),
        "final message names the finding's file": (bool(files) and all(n in message for n in files), 0.15),
    }
    print(f"finding files with mismatches: {sorted(files) or 'none'}; entries: {len(entries)}; "
          f"sheet-splitter issues: {len(issues)}")
    for name, (ok, _) in parts.items():
        print(f"  {'PASS' if ok else 'FAIL'} {name}")
    if spurious:
        print(f"  flagged sheets that match the index: {spurious}")
    print(f"score: {round(sum(w for ok, w in parts.values() if ok), 3)}")
    return 0 if all(ok for ok, _ in parts.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
