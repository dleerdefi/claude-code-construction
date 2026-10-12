#!/usr/bin/env python3
"""Append one correction of AgentCM's data to .construction/skills/corrections.tsv (AgentCM mode only).

When a skill finds AgentCM wrong (a wrong text, a room name, a wrong zone), it uses the
document's value in the task at hand, says so, and records the correction here for the
project engineer to resolve in AgentCM. A missed tag or callout goes through
tag-detections/ingest instead. The file's format is AgentCM's contract:

  sheet  x  y  w  h  kind  crop  agentcm  drawing     (tab-separated, header line first)

- sheet: the sheet's number as INDEX.md names it (its file name in sheets/)
- x y w h: the box as the sheet files give it, 0 to 1 from the top left, the numbers crop.sh takes
- kind: text, room, tag, callout, zone, view, sheet or other
- crop: the PNG crop.sh printed for that box
- agentcm, drawing: AgentCM's value and the drawing's value (agentcm may be empty)

Each value is its own argument; the script checks them, turns tabs and line breaks into
spaces, writes the header when the file is new, appends one line (UTF-8, no BOM, LF) and
prints it. It never rewrites a line already there. A failed check writes nothing (exit 2).

Usage (from the project folder):
  corrections_append.py --sheet A-101 --x 0.41 --y 0.22 --w 0.08 --h 0.03 --kind room \\
      --crop ".construction/crops/A-101_0.41_0.22_0.08_0.03.png" \\
      --agentcm "EXISTING DT WOMEN'S RESTROOM" --drawing "EXISTING WOMEN'S RESTROOM"
"""
import argparse
import math
import re
import sys
from pathlib import Path

COLUMNS = ["sheet", "x", "y", "w", "h", "kind", "crop", "agentcm", "drawing"]
HEADER = "\t".join(COLUMNS)
KINDS = ("text", "room", "tag", "callout", "zone", "view", "sheet", "other")
SHEET_SECTIONS = ("## Drawing sheets", "## Pages not yet named")


class Refused(Exception):
    """A correction that cannot be recorded; the message says why."""


def clean(value):
    """One line: tabs and line breaks become spaces."""
    return re.sub(r"[\t\r\n]+", " ", value).strip()


def index_sheets(index_md):
    """The sheet numbers INDEX.md names, and their file names in sheets/."""
    names, in_table = set(), False
    for line in index_md.splitlines():
        if line.startswith("## "):
            in_table = line.startswith(SHEET_SECTIONS)
            continue
        if not in_table or not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
        if not cells or cells[0] == "Sheet":
            continue
        names.add(cells[0])
        for c in cells:
            m = re.fullmatch(r"sheets/(.+)\.txt", c)
            if m:
                names.add(m.group(1))
    return names


def check(args, root):
    if not (root / ".construction" / "project.yaml").is_file():
        raise Refused("no .construction/project.yaml: corrections are for AgentCM's data, and this is not an AgentCM project")
    index = root / ".construction" / "INDEX.md"
    if not index.is_file():
        raise Refused("no .construction/INDEX.md: AgentCM has not written its index here, so the sheet cannot be checked")
    sheet = clean(args.sheet)
    if sheet not in index_sheets(index.read_text(encoding="utf-8")):
        raise Refused(f"sheet {sheet!r} is not a sheet INDEX.md names (use its number as INDEX.md gives it)")
    box = []
    for name in ("x", "y", "w", "h"):
        raw = clean(getattr(args, name))
        try:
            v = float(raw)
        except ValueError:
            raise Refused(f"{name} must be a number from 0 to 1, got {raw!r}")
        if not math.isfinite(v) or not 0 <= v <= 1:
            raise Refused(f"{name} must be a number from 0 to 1, got {raw!r}")
        box.append(raw)
    kind = clean(args.kind)
    if kind not in KINDS:
        raise Refused(f"kind must be one of {', '.join(KINDS)}, got {kind!r}")
    crop, agentcm, drawing = clean(args.crop), clean(args.agentcm), clean(args.drawing)
    if not crop:
        raise Refused("crop is empty: give the PNG crop.sh printed for this box")
    if not drawing:
        raise Refused("drawing is empty: give the value the drawing shows")
    return [sheet, *box, kind, crop, agentcm, drawing]


def append(values, path):
    if path.exists() and path.stat().st_size > 0:
        with open(path, encoding="utf-8") as f:
            first = f.readline().rstrip("\r\n")
        if first != HEADER:
            raise Refused(f"{path} does not start with the header line {HEADER!r}; not appending to it")
        needs_newline = not path.read_bytes().endswith(b"\n")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(HEADER + "\n")
        needs_newline = False
    line = "\t".join(values)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(("\n" if needs_newline else "") + line + "\n")
    return line


def main(argv=None):
    p = argparse.ArgumentParser(description="Append one correction of AgentCM's data to .construction/skills/corrections.tsv")
    for name in COLUMNS:
        p.add_argument(f"--{name}", required=True)
    args = p.parse_args(argv)
    root = Path.cwd()
    try:
        values = check(args, root)
        line = append(values, root / ".construction" / "skills" / "corrections.tsv")
    except Refused as e:
        print(f"REFUSED, nothing written: {e}")
        return 2
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
