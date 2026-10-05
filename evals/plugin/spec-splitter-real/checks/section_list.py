"""Compare the split spec sections and extracted text with the sections of the trimmed manual."""
import glob
import json
import os
import re
import sys
from pathlib import Path

WORKSPACE = Path(os.environ["EVAL_WORKSPACE"])
GT = Path(os.environ["EVAL_CASE_DIR"]).parent / "_fixtures" / "sanibel" / "ground_truth" / "manual_div09_sections.json"


def key(s: str) -> str:
    """'09 65 40' / '09_65_40' / '096540' -> '096540'."""
    return re.sub(r"\D", "", s)


def main() -> int:
    expected = {key(s["number"]): s for s in json.loads(GT.read_text(encoding="utf-8"))}
    pdfs = [Path(p) for p in glob.glob(str(WORKSPACE / "02 - Specifications" / "**" / "*.pdf"), recursive=True)
            if "Project Manual" not in Path(p).name]
    found = {}
    for p in pdfs:
        m = re.match(r"^\s*(\d{2}[ _]?\d{2}[ _]?\d{2})", p.stem)
        if m:
            found[key(m.group(1))] = p.stem
    hit = [k for k in expected if k in found]
    extra = [v for k, v in found.items() if k not in expected]
    txts = {key(Path(t).stem): t for t in glob.glob(str(WORKSPACE / ".construction" / "skills" / "spec_text" / "*.txt"))}
    txt_hit = [k for k in expected if k in txts]
    manifest = WORKSPACE / ".construction" / "skills" / "spec_text" / "manifest.json"
    poor = []
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        poor = [k for k, v in data.items() if isinstance(v, dict) and str(v.get("quality_rating", "")).upper() == "POOR"]
    n = len(expected)
    score = round(0.5 * len(hit) / n + 0.4 * len(txt_hit) / n + (0.1 if not poor and manifest.exists() else 0), 3)
    print(f"section PDFs: {len(pdfs)}; expected sections found: {len(hit)}/{n}; unexpected: {extra[:5]}")
    print(f"spec text files for expected sections: {len(txt_hit)}/{n}; manifest: {'present' if manifest.exists() else 'missing'}; POOR ratings: {poor}")
    missing = [expected[k]['number'] for k in expected if k not in found]
    if missing:
        print("  missing sections:", missing)
    print(f"score: {score}")
    return 0 if score >= 0.95 else 1


if __name__ == "__main__":
    sys.exit(main())
