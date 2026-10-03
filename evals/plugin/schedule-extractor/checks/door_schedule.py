"""Compare the extracted door schedule workbook with the transcription of sheet A500.

Finds the header row in the workbook by its DOOR NUMBER (or MARK) column, matches rows
by door number, and checks width, height, hardware set and leaf material per door.
Prints `score: x` (0-1) and exits 0 only at full marks.
"""
import csv
import glob
import os
import re
import sys
from pathlib import Path

import openpyxl

WORKSPACE = Path(os.environ["EVAL_WORKSPACE"])
GT = Path(os.environ["EVAL_CASE_DIR"]).parent / "_fixtures" / "sanibel" / "ground_truth" / "a500_door_schedule.csv"
CHECK_COLUMNS = {  # ground-truth column -> keywords that identify it in the workbook header
    "DOOR PANEL LEAF WIDTH": ("WIDTH",),
    "DOOR PANEL LEAF HEIGHT": ("HEIGHT",),
    "DOOR HARDWARE": ("HARDWARE",),
    "DOOR PANEL LEAF MATERIAL": ("MATERIAL",),
}


def norm(v) -> str:
    s = "" if v is None else str(v)
    s = s.replace("″", '"').replace("’", "'").replace("'", "'").replace("ft", "'").replace("in", '"')
    s = re.sub(r"\s*-\s*", "-", s)           # 3' - 0"  ->  3'-0"
    s = re.sub(r"\s+", " ", s).strip().upper()
    return s.lstrip("0") or "0" if re.fullmatch(r"\d+", s) else s  # hardware "06" == "6"


def find_table(wb):
    """(header list, rows) for the first sheet whose header has a door-number column."""
    for ws in wb.worksheets:
        for r_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=min(ws.max_row, 15), values_only=True), start=1):
            cells = [norm(c) for c in row]
            if any(re.search(r"DOOR\s*(NUMBER|NO\.?|MARK)|^MARK$|^NUMBER$", c) for c in cells):
                data = [list(r) for r in ws.iter_rows(min_row=r_idx + 1, values_only=True) if any(c is not None for c in r)]
                return cells, data
    return None, []


def main() -> int:
    files = sorted(glob.glob(str(WORKSPACE / "Door_Schedule_A500*.xlsx")))
    if not files:
        print("no Door_Schedule_A500*.xlsx in the workspace"); print("score: 0"); return 1
    wb = openpyxl.load_workbook(files[-1], data_only=True)
    headers, rows = find_table(wb)
    if not headers:
        print("no header row with a door-number column found"); print("score: 0"); return 1
    num_i = next(i for i, h in enumerate(headers) if re.search(r"DOOR\s*(NUMBER|NO\.?|MARK)|^MARK$|^NUMBER$", h))
    col_i = {}
    for gt_col, keys in CHECK_COLUMNS.items():
        hits = [i for i, h in enumerate(headers) if any(k in h for k in keys) and "FRAME" not in h]
        col_i[gt_col] = hits[0] if hits else None

    truth = {r["DOOR NUMBER"]: r for r in csv.DictReader(GT.open(encoding="utf-8"))}
    found = {norm(r[num_i]): r for r in rows if r[num_i] is not None}
    present = [d for d in truth if norm(d) in found]
    recall = len(present) / len(truth)
    checks, ok = 0, 0
    mismatches = []
    for d in present:
        row = found[norm(d)]
        for gt_col, i in col_i.items():
            if i is None:
                continue
            checks += 1
            want, got = norm(truth[d][gt_col]), norm(row[i])
            if want == got:
                ok += 1
            elif len(mismatches) < 8:
                mismatches.append(f"door {d} {gt_col}: want {want!r} got {got!r}")
    accuracy = ok / checks if checks else 0.0
    score = round(0.5 * recall + 0.5 * accuracy, 3)
    print(f"workbook: {Path(files[-1]).name}; header: {headers[:8]}...")
    print(f"doors found: {len(present)}/{len(truth)} (recall {recall:.2f}); cell accuracy {ok}/{checks} ({accuracy:.2f}) over {[c for c, i in col_i.items() if i is not None]}")
    for m in mismatches:
        print("  " + m)
    print(f"score: {score}")
    return 0 if recall >= 0.95 and accuracy >= 0.95 else 1


if __name__ == "__main__":
    sys.exit(main())
