#!/usr/bin/env python3
"""Derive ground truth for the real-document eval cases from the Sanibel PDFs.

Run with: bin/construction-python evals/plugin/_fixtures/sanibel/derive_ground_truth.py

Writes to ground_truth/ next to this script (committed, so cases can grade
without the downloads present at review time):

  mech_sheets.json          sheet number and title of each page of the mechanical set
  manual_div09_sections.json  the sections in the Division 09 trimmed manual
  a500_door_schedule.csv    the A500 door schedule, one row per door
  submittals.json           Part 1 submittal items of 09 30 00, 09 65 13 and 09 65 40
  a101_door_tags.json       ground-floor door numbers from A500 and how often each is printed on A101
  g010_text.txt             the text of the code summary sheet, for the code-researcher facts
  qa_pairs.json             known-answer questions from the door schedule

Everything is read from the documents; nothing is typed in by hand. Review the
output once by eye (see the README) before relying on it.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

import fitz

from make_fixtures import FOOTER, MANUALS, section_pages, sheet_numbers, sheet_title, source_files, toc_titles

HERE = Path(__file__).resolve().parent
OUT = HERE / "ground_truth"
SUBMITTAL_SECTIONS = ["09 30 00", "09 65 13", "09 65 40"]
QA_DOORS = ["220", "001", "004A"]
ARTICLE = re.compile(r"^(1\.\d+)\s*$")
SUBMITTAL_ARTICLES = ("ACTION SUBMITTALS", "INFORMATIONAL SUBMITTALS", "CLOSEOUT SUBMITTALS",
                      "MAINTENANCE MATERIAL SUBMITTALS", "SUBMITTALS")


def clean(cell) -> str:
    return re.sub(r"\s+", " ", str(cell)).strip() if cell is not None else ""


def door_schedule(page: fitz.Page) -> list[dict]:
    tbl = max(page.find_tables().tables, key=lambda t: t.row_count)
    rows = tbl.extract()
    top, sub = [clean(c) for c in rows[0]], [clean(c) for c in rows[1]]
    # Two header rows: a group name spans several sub-columns (e.g. DOOR PANEL -> WIDTH, HEIGHT, TYPE, MATERIAL).
    headers, group = [], ""
    for g, s in zip(top, sub):
        group = g or group
        headers.append(f"{group} {s}".strip() if s else group)
    out = []
    for r in rows[2:]:
        cells = [clean(c) for c in r]
        if not any(cells):
            continue
        out.append(dict(zip(headers, cells)))
    return headers, out


def submittal_items(doc: fitz.Document, pages: list[int]) -> dict:
    """First-level items (A., B., ...) under each Part 1 submittal article."""
    lines = []
    for p in pages:
        lines += [l.strip() for l in doc[p].get_text().splitlines() if l.strip()]
    articles, current, items = {}, None, []
    i = 0
    while i < len(lines):
        l = lines[i]
        if ARTICLE.match(l) and i + 1 < len(lines):
            title = lines[i + 1].upper()
            if current:
                articles[current] = items
            current, items = (f"{l} {title}" if title in SUBMITTAL_ARTICLES else None), []
            i += 2
            continue
        if l.startswith(("PART 2", "PART 3")):
            break
        if current and re.match(r"^[A-Z]\.$", l) and i + 1 < len(lines):
            # item text runs until the next lettered/numbered marker
            j, text = i + 1, []
            while j < len(lines) and not re.match(r"^([A-Z]|\d+|[a-z])\.$", lines[j]) and not ARTICLE.match(lines[j]) and not lines[j].startswith("PART "):
                text.append(lines[j]); j += 1
            items.append(" ".join(text).split(" 1. ")[0][:200])
            i = j
            continue
        i += 1
    if current:
        articles[current] = items
    return articles


def main() -> None:
    files = source_files()
    arch, mech, vol1 = fitz.open(files["arch"]), fitz.open(files["mech"]), fitz.open(files["vol1"])
    OUT.mkdir(exist_ok=True)

    # 1. mechanical sheet list
    numbers = sheet_numbers(mech)
    sheets = [{"page": p + 1, "number": n, "title": sheet_title(mech[p], n)} for n, p in sorted(numbers.items(), key=lambda kv: kv[1])]
    (OUT / "mech_sheets.json").write_text(json.dumps(sheets, indent=1), encoding="utf-8")

    # 2. sections of the trimmed Division 09 manual
    titles = toc_titles(vol1)
    sec = [{"number": s, "title": titles.get(s, "")} for s in MANUALS["Project Manual - Division 09 Flooring.pdf"]]
    (OUT / "manual_div09_sections.json").write_text(json.dumps(sec, indent=1), encoding="utf-8")

    # 3. A500 door schedule
    a500 = arch[sheet_numbers(arch)["A500"]]
    headers, rows = door_schedule(a500)
    with (OUT / "a500_door_schedule.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)

    # 4. submittal items
    pages = section_pages(vol1)
    subs = {s: {"title": titles.get(s, ""), "articles": submittal_items(vol1, pages[s])} for s in SUBMITTAL_SECTIONS}
    (OUT / "submittals.json").write_text(json.dumps(subs, indent=1), encoding="utf-8")

    # 5. door tags on A101 (the first-floor plan). The schedule calls that level "GROUND FLOOR (13' NAVD)".
    # A door number printed twice is usually the door tag plus the room of the same number, so the
    # count of distinct door numbers present is the useful figure, not the word count.
    a101 = arch[sheet_numbers(arch)["A101"]]
    words = Counter(w[4].strip() for w in a101.get_text("words"))
    level_col = headers[0]
    number_col = next(h for h in headers if "NUMBER" in h.upper())
    ground = [r[number_col] for r in rows if r[level_col].upper().startswith("GROUND FLOOR")]
    others = [r[number_col] for r in rows if not r[level_col].upper().startswith("GROUND FLOOR")]
    tags = {"sheet": "A101", "level_in_schedule": "GROUND FLOOR (13' NAVD)", "doors_in_schedule": len(ground),
            "printed_on_sheet": {d: words.get(d, 0) for d in ground},
            "other_level_doors_printed_on_sheet": [d for d in others if words.get(d, 0)]}
    tags["doors_printed_at_least_once"] = sum(1 for d in ground if words.get(d, 0))
    (OUT / "a101_door_tags.json").write_text(json.dumps(tags, indent=1), encoding="utf-8")

    # 6. G010 text for the code facts
    g010 = arch[sheet_numbers(arch)["G010"]]
    (OUT / "g010_text.txt").write_text("\n".join(l.strip() for l in g010.get_text().splitlines() if l.strip()), encoding="utf-8")

    # 7. known-answer questions from the door schedule
    qa = []
    for d in QA_DOORS:
        r = next((r for r in rows if r[number_col] == d), None)
        if r:
            qa.append({"door": d, "row": r})
    (OUT / "qa_pairs.json").write_text(json.dumps(qa, indent=1), encoding="utf-8")

    print(f"mech sheets: {[s['number'] for s in sheets]}")
    print(f"door schedule: {len(rows)} rows, headers: {headers}")
    print(f"submittals: " + ", ".join(f"{s}: {sum(len(v) for v in subs[s]['articles'].values())} items in {list(subs[s]['articles'])}" for s in SUBMITTAL_SECTIONS))
    print(f"A101: {tags['doors_in_schedule']} ground-floor doors in schedule, {tags['doors_printed_at_least_once']} printed on A101, "
          f"plus other-level doors {tags['other_level_doors_printed_on_sheet']}")


if __name__ == "__main__":
    main()
