"""Compare the per-bid JSON the tabulator wrote with the synthetic bids' ground truth.

Bidders are matched by the first word of the company name. Checks: every bidder found,
base bids as stated (within $1, including the planted wrong total), alternates with the
right sign and amount, the buried exclusion and budget qualification captured, the
smudged value flagged as unclear, and the as-submitted line items of the math-error bid.
"""
import glob
import json
import os
import re
import sys
from pathlib import Path

WORKSPACE = Path(os.environ["EVAL_WORKSPACE"])
GT_DIR = Path(os.environ["EVAL_CASE_DIR"]).parent / "_fixtures" / "synthetic" / "bids_ground_truth" / "bids"


def first_word(name: str) -> str:
    return re.sub(r"[^a-z]", "", str(name).lower().split()[0]) if str(name).strip() else ""


def num(v):
    try:
        return float(str(v).replace("$", "").replace(",", ""))
    except (TypeError, ValueError):
        return None


def text_of(d) -> str:
    return json.dumps(d, default=str).lower()


def main() -> int:
    truth = {first_word(json.loads(p.read_text(encoding="utf-8"))["company_name"]): json.loads(p.read_text(encoding="utf-8"))
             for p in GT_DIR.glob("*.json")}
    files = glob.glob(str(WORKSPACE / ".construction" / "skills" / "bid-tabulator" / "bids" / "*.json"))
    got = {}
    for f in files:
        try:
            d = json.loads(Path(f).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        key = first_word(d.get("company_name", Path(f).stem))
        if key:
            got[key] = d
    checks = {}
    for key, gt in truth.items():
        d = got.get(key)
        name = gt["company_name"]
        checks[f"{name}: extracted"] = d is not None
        if d is None:
            continue
        checks[f"{name}: base bid as stated"] = num(d.get("base_bid_amount")) is not None and abs(num(d["base_bid_amount"]) - gt["base_bid_amount"]) <= 1
        alts = {str(a.get("name", "")).upper().replace("ALTERNATE", "ALT").replace(".", "").strip(): num(a.get("amount")) for a in d.get("alternates", [])}
        for a in gt["alternates"]:
            short = a["name"].upper().replace("ALTERNATE", "ALT")
            val = alts.get(short) or alts.get(short.replace("ALT ", "ALT"))
            if val is None:  # match loosely on the letter
                val = next((v for k, v in alts.items() if k.endswith(short[-1])), None)
            checks[f"{name}: {a['name']} amount and sign"] = val is not None and abs(val - a["amount"]) <= 1
    t = {k: text_of(v) for k, v in got.items()}
    if "palmetto" in t:
        checks["Palmetto: buried moisture-testing exclusion captured"] = "moisture" in t["palmetto"]
        checks["Palmetto: budget-only pricing captured"] = "budget" in t["palmetto"]
        checks["Palmetto: allowance captured"] = "allowance" in t["palmetto"]
    if "sandbar" in t:
        checks["Sandbar: smudged value flagged unclear"] = "unclear" in t["sandbar"] or "illegible" in t["sandbar"] or "unreadable" in t["sandbar"]
    if "island" in got:
        items = [num(l.get("extended_price") or l.get("amount")) for l in got["island"].get("line_items", [])]
        total = sum(v for v in items if v is not None)
        checks["Island: line items kept as submitted (sum 413,125, not the stated total)"] = abs(total - 413125) <= 1
        checks["Island: no 09 65 13 line invented"] = not any("09 65 13" in str(l.get("spec_section", "")) for l in got["island"].get("line_items", []))
    if "mangrove" in t:
        checks["Mangrove: 15-day validity captured"] = "15" in str(got["mangrove"].get("bid_validity_period", ""))
    passed = sum(checks.values())
    for k, ok in checks.items():
        print(f"  {'PASS' if ok else 'FAIL'} {k}")
    score = round(passed / len(checks), 3) if checks else 0
    print(f"bidders found: {sorted(got)} (expected {sorted(truth)})")
    print(f"score: {score}")
    return 0 if score >= 0.85 else 1


if __name__ == "__main__":
    sys.exit(main())
