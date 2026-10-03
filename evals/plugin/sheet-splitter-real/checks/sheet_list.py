"""Compare the split mechanical sheets and sheet_index.yaml with the sheet list read from the title blocks."""
import glob
import json
import os
import re
import sys
from pathlib import Path

import yaml

WORKSPACE = Path(os.environ["EVAL_WORKSPACE"])
GT = Path(os.environ["EVAL_CASE_DIR"]).parent / "_fixtures" / "sanibel" / "ground_truth" / "mech_sheets.json"


def norm(s: str) -> str:
    return re.sub(r"[^A-Z0-9]+", " ", str(s).upper()).strip()


def main() -> int:
    expected = json.loads(GT.read_text(encoding="utf-8"))
    pdfs = [Path(p) for p in glob.glob(str(WORKSPACE / "**" / "sheets" / "*.pdf"), recursive=True)]
    names = {p.stem for p in pdfs}
    by_number = {s["number"]: s for s in expected}
    files_ok = [n for n in by_number if any(stem.upper().startswith(n) for stem in names)]
    titles_ok = [n for n in by_number if any(stem.upper().startswith(n) and norm(by_number[n]["title"]) in norm(stem) for stem in names)]

    index_files = glob.glob(str(WORKSPACE / "**" / "sheets" / "sheet_index.yaml"), recursive=True)
    index_ok, index_total = 0, 0
    if index_files:
        idx = yaml.safe_load(Path(index_files[0]).read_text(encoding="utf-8")) or {}
        entries = idx.get("pages") or idx.get("sheets") or []
        index_total = len(entries)
        for e in entries:
            num = str(e.get("sheet_number", "")).upper()
            if num in by_number and norm(by_number[num]["title"]) in norm(e.get("title", "")):
                index_ok += 1
    n = len(by_number)
    score = round(0.4 * len(files_ok) / n + 0.3 * len(titles_ok) / n + 0.3 * (index_ok / n if index_files else 0), 3)
    print(f"sheet PDFs: {len(pdfs)} (expected {n}); numbered correctly: {len(files_ok)}/{n}; titled from title block: {len(titles_ok)}/{n}")
    print(f"sheet_index.yaml: {'found' if index_files else 'missing'}; entries with correct number and title: {index_ok}/{index_total}")
    missing = [n_ for n_ in by_number if n_ not in titles_ok]
    if missing:
        print("  not matched by number+title:", missing, "| files:", sorted(names)[:10])
    print(f"score: {score}")
    return 0 if score >= 0.95 else 1


if __name__ == "__main__":
    sys.exit(main())
