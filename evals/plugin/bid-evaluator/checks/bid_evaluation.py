"""Check that the evaluation JSON and workbook catch the planted defects.

Island Tile (B): silent omission of 09 65 13 and a stated total $4,200 above its line items.
Palmetto (C): moisture testing excluded in a buried qualification; budget-only pricing.
Sandbar (D): a smudged value on the scan; no addenda acknowledged.
Mangrove (E): 15-day validity, no bond. Gulfshore (A) is clean and the lowest responsive bid.
"""
import glob
import json
import os
import re
import sys
from pathlib import Path

import openpyxl

WORKSPACE = Path(os.environ["EVAL_WORKSPACE"])
EXPECTED_TABS = {"Bid Comparison", "Price Summary", "Exclusion Detail", "Qualification Summary", "Recommendation"}


def first_word(name: str) -> str:
    return re.sub(r"[^a-z]", "", str(name).lower().split()[0]) if str(name).strip() else ""


def main() -> int:
    files = sorted(glob.glob(str(WORKSPACE / "bid_evaluation*.json")))
    if not files:
        print("no bid_evaluation*.json"); print("score: 0"); return 1
    data = json.loads(Path(files[-1]).read_text(encoding="utf-8"))
    bidders = {first_word(b.get("company_name", "")): b for b in data.get("bidders", [])}
    rec = data.get("recommendation", {}) or {}
    whole = json.dumps(data, default=str).lower()

    def blob(key):
        return json.dumps(bidders.get(key, {}), default=str).lower()

    def silent_anywhere(key):
        return any(str(v).upper() == "SILENT" for v in (bidders.get(key, {}).get("coverage_map") or {}).values())

    checks = {
        "five bidders evaluated": len(bidders) == 5,
        "Island: a baseline item marked SILENT": silent_anywhere("island"),
        "Island: raw bid kept as stated (417,325), not corrected": abs(float(bidders.get("island", {}).get("raw_bid", 0) or 0) - 417325) <= 1,
        "Island: math discrepancy flagged": any(w in blob("island") + json.dumps(rec, default=str).lower() for w in ("4,200", "4200", "discrepan", "do not add", "does not add", "math", "reconcil")),
        "Palmetto: moisture testing exclusion scored": any("moisture" in json.dumps(x, default=str).lower() for x in bidders.get("palmetto", {}).get("exclusion_scores", []))
                                                       or "EXCLUDED" in json.dumps(bidders.get("palmetto", {}).get("coverage_map", {})).upper(),
        "Palmetto: budget pricing noted": "budget" in blob("palmetto"),
        "Palmetto: not the recommended bidder": "palmetto" not in str(rec.get("recommended_bidder", "")).lower(),
        "Island: not the recommended bidder": "island" not in str(rec.get("recommended_bidder", "")).lower(),
        "Gulfshore recommended": "gulfshore" in str(rec.get("recommended_bidder", "")).lower(),
        "Sandbar: unclear scan value or missing addenda noted": any(w in blob("sandbar") for w in ("unclear", "illegible", "smudg", "addend")),
        "Mangrove: short validity or missing bond noted": any(w in blob("mangrove") for w in ("15 day", "15-day", "validity", "bond")),
        "PE attention items present": bool(rec.get("pe_attention_items")),
        "no 'bust' verdict": "bust" not in whole,
    }
    xlsx = sorted(glob.glob(str(WORKSPACE / "Bid_Evaluation_BP-09*.xlsx")))
    if xlsx:
        tabs = set(openpyxl.load_workbook(xlsx[-1], read_only=True).sheetnames)
        checks["workbook has the five evaluation tabs"] = EXPECTED_TABS <= tabs
    else:
        checks["workbook has the five evaluation tabs"] = False
    passed = sum(checks.values())
    for k, ok in checks.items():
        print(f"  {'PASS' if ok else 'FAIL'} {k}")
    print(f"recommended: {rec.get('recommended_bidder')!r}; bidders: {sorted(bidders)}")
    score = round(passed / len(checks), 3)
    print(f"score: {score}")
    return 0 if score >= 0.8 else 1


if __name__ == "__main__":
    sys.exit(main())
