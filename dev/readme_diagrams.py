#!/usr/bin/env python3
"""Draw the README's diagrams as drawing sheets, in a light (whiteprint) and a dark (blueprint) version.

    bin/construction-python dev/readme_diagrams.py

Writes docs/images/<name>-light.svg and docs/images/<name>-dark.svg. Edit this script, not the SVGs.

Every label is checked against the room it has before anything is written. The SVGs are shown
through <img>, so only system fonts apply; the check budgets for DejaVu Sans, the widest common
fallback (about 10% wider than Segoe UI or Arial). A label that would overflow is named and the
script exits 1 without writing.

What the figures claim comes from the skills themselves; check a change against them:
- G-001: the skill list and outputs in README.md's Skills table; the phases are where each is used most.
- G-002: the hand-offs in skills/spec-splitter, submittal-log-generator, bid-tabulator, bid-evaluator,
  subcontract-writer and rfi-drafter; the issue producers are the skills whose SKILL.md lists issue_manager.py.
- G-003: the nine steps of skills/submittal-review/SKILL.md.
A hold point is drawn only where a skill's text stops for the user.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "images"

W = 900
INNER = 22          # inner border inset; the band outside it carries the zone labels
L, R = 40, W - 40   # the drawing's left and right edges inside the border
SANS = "'Segoe UI', -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'Cascadia Mono', Consolas, 'SF Mono', Menlo, 'DejaVu Sans Mono', monospace"
PROJECT = "Construction Skills for Claude Code"

PALETTES = {
    "light": {
        "paper": "#FBFAF6", "ink": "#1C2B3A", "ink2": "#56677A", "rule": "#CDD3DA", "band": "#F1EFE8",
        "head": "#E9E6DD", "bar": "#2F5D8A", "summary": "#1C2B3A", "hold": "#B3261E", "chip_fg": "#FFFFFF",
        "xlsx": "#1D6F42", "docx": "#2B579A", "pdf": "#A12A22", "neutral": "#56677A", "doc": "#E3EAF2",
    },
    "dark": {
        "paper": "#0F2C4C", "ink": "#EAF1F8", "ink2": "#A9BCD1", "rule": "#2F5276", "band": "#133457",
        "head": "#173B62", "bar": "#86B8E8", "summary": "#EAF1F8", "hold": "#FF8F80", "chip_fg": "#0F2C4C",
        "xlsx": "#5FCB93", "docx": "#93B8F2", "pdf": "#FF9486", "neutral": "#A9BCD1", "doc": "#1D4673",
    },
}

problems = []


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def est_width(s, size, mono=False, bold=False, caps=False, spacing=0.0):
    """A generous estimate of a label's drawn width, in the widest fallback font."""
    if mono:
        per = 0.602
    elif caps:
        per = 0.70 if bold else 0.66
    else:
        per = 0.58 if bold else 0.54
    w = len(s) * size * per + spacing * size * max(len(s) - 1, 0)
    return w if mono else w * 1.10


def text(x, y, s, size, fill, *, mono=False, bold=False, caps=False, upper=None, spacing=0.0,
         anchor="start", room=None, where=""):
    """A label. caps measures it as capitals and, unless upper=False, also writes it in capitals."""
    if room is not None:
        need = est_width(s, size, mono, bold, caps, spacing)
        if need > room:
            problems.append(f"{where}: '{s}' needs about {need:.0f}px, has {room:.0f}px")
    attrs = [f'x="{x:g}"', f'y="{y:g}"', f'font-size="{size:g}"', f'fill="{fill}"']
    if mono:
        attrs.append(f'font-family="{MONO}"')
    if bold:
        attrs.append('font-weight="700"')
    if spacing:
        attrs.append(f'letter-spacing="{spacing * size:.2f}"')
    if anchor != "start":
        attrs.append(f'text-anchor="{anchor}"')
    shown = s.upper() if caps and upper is not False else s
    return f'<text {" ".join(attrs)}>{esc(shown)}</text>'


def rect(x, y, w, h, *, fill="none", stroke=None, sw=1.0, rx=0, dash=None):
    a = f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}"'
    if stroke:
        a += f' stroke="{stroke}" stroke-width="{sw:g}"'
    if rx:
        a += f' rx="{rx:g}"'
    if dash:
        a += f' stroke-dasharray="{dash}"'
    return a + "/>"


def line(x1, y1, x2, y2, stroke, sw=1.0, dash=None):
    a = f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{stroke}" stroke-width="{sw:g}"'
    if dash:
        a += f' stroke-dasharray="{dash}"'
    return a + "/>"


def path(d, *, stroke, sw=1.0, fill="none", dash=None):
    a = f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:g}" stroke-linejoin="round"'
    if dash:
        a += f' stroke-dasharray="{dash}"'
    return a + "/>"


def polygon(points, fill):
    return f'<polygon points="{" ".join(f"{x:g},{y:g}" for x, y in points)}" fill="{fill}"/>'


def head_down(x, y, c):
    return polygon([(x - 4.5, y - 8), (x + 4.5, y - 8), (x, y)], c)


def head_up(x, y, c):
    return polygon([(x - 4.5, y + 8), (x + 4.5, y + 8), (x, y)], c)


def head_right(x, y, c):
    return polygon([(x - 8, y - 4.5), (x - 8, y + 4.5), (x, y)], c)


def head_left(x, y, c):
    return polygon([(x + 8, y - 4.5), (x + 8, y + 4.5), (x, y)], c)


CHIP_COLOR = {"XLSX": "xlsx", "DOCX": "docx", "PDF": "pdf"}


def chip_width(label):
    return est_width(label, 9.5, bold=True, caps=True, spacing=0.05) / 1.10 + 12


def chip(x, y_mid, label, pal):
    """A file-type tag whose left edge is at x. Returns (svg, width)."""
    w = chip_width(label)
    color = pal[CHIP_COLOR.get(label, "neutral")]
    return (rect(x, y_mid - 8, w, 16, fill=color, rx=3)
            + text(x + w / 2, y_mid + 3.4, label, 9.5, pal["chip_fg"], bold=True, caps=True, upper=False,
                   spacing=0.05, anchor="middle")), w


def stamp(cx, cy, pal, r=15):
    """A hold-point stamp: the place a skill stops for the PE."""
    c = pal["hold"]
    return (f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" fill="none" stroke="{c}" stroke-width="2"/>'
            f'<circle cx="{cx:g}" cy="{cy:g}" r="{r - 3.5:g}" fill="none" stroke="{c}" stroke-width="0.8"/>'
            + text(cx, cy + 4, "PE", 11 if r >= 14 else 9.5, c, bold=True, anchor="middle"))


def doc_shape(x, y, w, h, pal, fold=10):
    """A sheet of paper with a folded corner: a document that comes in."""
    ink = pal["ink"]
    return (path(f"M{x:g},{y:g} H{x + w - fold:g} L{x + w:g},{y + fold:g} V{y + h:g} H{x:g} Z",
                 stroke=ink, sw=1.1, fill=pal["doc"])
            + path(f"M{x + w - fold:g},{y:g} V{y + fold:g} H{x + w:g}", stroke=ink, sw=1.1))


def view_title(number, sheet_no, title, subtitle, pal, y=60):
    """The detail title in the drawing's top-left: a split bubble, an underlined title, a line below."""
    ink, ink2 = pal["ink"], pal["ink2"]
    cx, r = 58, 19
    title_room = W - INNER - 18 - 90
    return "".join([
        f'<circle cx="{cx}" cy="{y}" r="{r}" fill="none" stroke="{ink}" stroke-width="1.6"/>',
        line(cx - r, y, cx + r, y, ink, 1.0),
        text(cx, y - 5, str(number), 13, ink, bold=True, anchor="middle"),
        text(cx, y + 13, sheet_no, 9, ink, bold=True, anchor="middle"),
        text(90, y - 4, title, 17, ink, bold=True, caps=True, spacing=0.04, room=title_room, where="view title"),
        line(90, y + 4, W - INNER - 18, y + 4, ink, 1.4),
        text(90, y + 22, subtitle, 12.5, ink2, room=title_room, where="view subtitle"),
    ])


TITLE_BLOCK_H = 48


def sheet(name, sheet_title, sheet_no, H, body, pal, desc):
    """The full sheet: paper, double border with zone labels, the drawing, the title block."""
    ink, ink2 = pal["ink"], pal["ink2"]
    parts = [rect(0, 0, W, H, fill=pal["paper"]),
             rect(6, 6, W - 12, H - 12, stroke=ink, sw=2.2),
             rect(INNER, INNER, W - 2 * INNER, H - 2 * INNER, stroke=ink, sw=1.0)]
    cols = 6
    zw = (W - 2 * INNER) / cols
    for i in range(cols):
        x = INNER + i * zw
        if i:
            parts += [line(x, 6, x, INNER, ink, 0.8), line(x, H - INNER, x, H - 6, ink, 0.8)]
        parts += [text(x + zw / 2, 17.5, str(i + 1), 9.5, ink2, bold=True, anchor="middle"),
                  text(x + zw / 2, H - 10.5, str(i + 1), 9.5, ink2, bold=True, anchor="middle")]
    rows = max(3, round((H - 2 * INNER) / 160))
    zh = (H - 2 * INNER) / rows
    for j in range(rows):
        y = INNER + j * zh
        if j:
            parts += [line(6, y, INNER, y, ink, 0.8), line(W - INNER, y, W - 6, y, ink, 0.8)]
        letter = "ABCDEFGH"[j]
        parts += [text(14, y + zh / 2 + 3.5, letter, 9.5, ink2, bold=True, anchor="middle"),
                  text(W - 14, y + zh / 2 + 3.5, letter, 9.5, ink2, bold=True, anchor="middle")]
    parts.append(body)

    # Title block across the bottom: project, sheet title, scale, sheet number.
    y = H - INNER - TITLE_BLOCK_H
    cells = [("Project", PROJECT, 330, 14, False), ("Sheet title", sheet_title, 330, 14, False),
             ("Scale", "NTS", 76, 14, False), ("Sheet", sheet_no, W - 2 * INNER - 736, 18, True)]
    parts.append(line(INNER, y, W - INNER, y, ink, 1.6))
    x = INNER
    for k, (label, value, cw, size, bold) in enumerate(cells):
        if k:
            parts.append(line(x, y, x, H - INNER, ink, 1.0))
        parts.append(text(x + 9, y + 14, label, 9, ink2, bold=True, caps=True, spacing=0.08,
                          room=cw - 14, where="title block label"))
        parts.append(text(x + 9, y + 37, value, size, ink, bold=bold, room=cw - 16, where="title block"))
        x += cw

    return (f'<!-- Generated by dev/readme_diagrams.py. Edit that script, not this file. -->\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:g}" viewBox="0 0 {W} {H:g}" '
            f'role="img" aria-labelledby="{name}-title {name}-desc" font-family="{SANS}">\n'
            f'<title id="{name}-title">{esc(sheet_title)}</title>\n'
            f'<desc id="{name}-desc">{esc(desc)}</desc>\n'
            + "\n".join(parts) + "\n</svg>\n")


# ---------------------------------------------------------------------------------------------
# G-001  Skills by project phase: a bar chart in the shape of a project schedule.

PHASES = ["Setup", "Preconstruction", "Buyout", "Construction"]

# (group, [(skill, description, first phase, last phase, output chips)])
SCHEDULE = [
    ("Project setup", [
        ("project-setup", "Inventories and classifies your files", 0, 0, ["CLAUDE.md"]),
        ("sheet-splitter", "Splits the set, one PDF per sheet", 0, 0, ["PDF"]),
        ("spec-splitter", "Splits the manual into spec sections", 0, 0, ["PDF"]),
    ]),
    ("Document review", [
        ("schedule-extractor", "Door, finish, window, panel schedules", 1, 3, ["XLSX"]),
        ("tag-audit-and-takeoff", "Tag counts and tag completeness audit", 1, 2, ["XLSX", "PNG"]),
        ("code-researcher", "Codes and authorities that apply", 1, 3, ["MD"]),
        ("pe-review", "Coordination, scope gaps, what's missing", 1, 3, []),
    ]),
    ("Buyout", [
        ("submittal-log-generator", "Submittal register from every section", 2, 2, ["XLSX"]),
        ("bid-tabulator", "Bids side by side, as submitted", 2, 2, ["XLSX"]),
        ("bid-evaluator", "Scope gaps, exclusions, recommendation", 2, 2, ["XLSX"]),
        ("subcontract-writer", "Subcontract from your firm's template", 2, 2, ["DOCX"]),
    ]),
    ("Contract administration", [
        ("submittal-review", "Draft GC review of a submittal package", 3, 3, ["XLSX", "PDF"]),
        ("rfi-drafter", "RFIs from flagged issues, in your form", 3, 3, ["DOCX"]),
    ]),
]


def g001(pal):
    ink, ink2, rule = pal["ink"], pal["ink2"], pal["rule"]
    task_r = 352                       # right edge of the task column
    px0 = 362                          # left edge of the phase columns
    colw = (R - px0) / len(PHASES)
    group_h, task_h = 26, 36
    grid = []
    parts = [view_title(1, "G-001", "Skills by project phase",
                        "Where in the project each skill is used most, and the file it leaves in your project folder",
                        pal)]

    hy, hh = 100, 42
    parts.append(rect(L, hy, R - L, hh, fill=pal["head"]))
    parts.append(text(L + 8, hy + 26, "Skill", 10.5, ink2, bold=True, caps=True, spacing=0.08))
    parts.append(text(task_r - 6, hy + 26, "Output", 10.5, ink2, bold=True, caps=True, spacing=0.08, anchor="end"))
    for i, phase in enumerate(PHASES):
        cx = px0 + colw * (i + 0.5)
        parts.append(text(cx, hy + 16, f"Phase {i + 1}", 9.5, ink2, bold=True, caps=True, spacing=0.08,
                          anchor="middle", room=colw - 8, where="phase number"))
        parts.append(text(cx, hy + 34, phase, 12.5, ink, anchor="middle", room=colw - 8, where="phase name"))

    y = hy + hh + 4
    k = 0
    for group, tasks in SCHEDULE:
        first = min(t[2] for t in tasks)
        last = max(t[3] for t in tasks)
        parts.append(text(L + 8, y + 17, group, 11, ink, bold=True, caps=True, spacing=0.06,
                          room=task_r - L - 16, where="group"))
        # A summary bar, the way a schedule draws a group: a heavy bar with a point down at each end.
        x0, x1 = px0 + colw * first + 6, px0 + colw * (last + 1) - 6
        yc = y + 12
        parts.append(rect(x0, yc - 3.5, x1 - x0, 7, fill=pal["summary"]))
        parts.append(polygon([(x0, yc - 3.5), (x0 + 11, yc - 3.5), (x0 + 5.5, yc + 8)], pal["summary"]))
        parts.append(polygon([(x1 - 11, yc - 3.5), (x1, yc - 3.5), (x1 - 5.5, yc + 8)], pal["summary"]))
        y += group_h
        for skill, description, a, b, chips in tasks:
            if k % 2 == 0:
                parts.append(rect(L, y, R - L, task_h, fill=pal["band"]))
            k += 1
            xr = task_r - 6
            used = 0.0
            for label in reversed(chips):
                w = chip_width(label)
                svg, _ = chip(xr - w, y + 11, label, pal)
                parts.append(svg)
                xr -= w + 4
                used += w + 4
            parts.append(text(L + 8, y + 15, skill, 14, ink, mono=True,
                              room=task_r - L - 18 - used, where="skill name"))
            parts.append(text(L + 8, y + 30, description, 12.5, ink2, room=task_r - L - 14, where="description"))
            bx0, bx1 = px0 + colw * a + 8, px0 + colw * (b + 1) - 8
            parts.append(rect(bx0, y + 12, bx1 - bx0, 12, fill=pal["bar"], rx=2.5))
            y += task_h

    # The operating guide runs under everything.
    y += 8
    parts.append(line(L, y, R, y, ink, 1.0))
    gy = y + 4
    parts.append(text(L + 8, gy + 16, "construction-guide", 14, ink, mono=True))
    parts.append(text(L + 8, gy + 31, "Operating guide every skill loads first", 12.5, ink2,
                      room=task_r - L - 14, where="guide description"))
    gx0, gx1 = px0 + 8, R - 8
    parts.append(rect(gx0, gy + 8, gx1 - gx0, 22, fill=pal["ink2"], rx=3))
    parts.append(text((gx0 + gx1) / 2, gy + 23, "Document precedence, drawing conventions, data-access rules",
                      11.5, pal["paper"], bold=True, anchor="middle", room=gx1 - gx0 - 16, where="guide bar"))
    y = gy + 40

    for i in range(len(PHASES) + 1):
        x = px0 + colw * i
        grid.append(line(x, hy, x, y, rule, 0.9))
    parts[1:1] = grid

    H = y + 16 + TITLE_BLOCK_H + INNER
    desc = ("A schedule-style chart of the fourteen skills across four project phases: setup, "
            "preconstruction, buyout and construction. Setup splits the drawing set and project manual; "
            "document review extracts schedules, counts tags, researches codes and checks coordination; "
            "buyout builds the submittal register, tabulates and evaluates bids and writes the subcontract; "
            "contract administration reviews submittals and drafts RFIs. The operating guide underlies every phase.")
    return sheet("g001", "Skills by project phase", "G-001", H, "\n".join(parts), pal, desc)


# ---------------------------------------------------------------------------------------------
# G-002  How the skills hand work to each other: three chains, each ending in a file in the project folder.

LANE_W, LANE_GAP = 260, 20
NODE_W = 220


def lane_x(i):
    return L + i * (LANE_W + LANE_GAP)


def node_doc(x0, y, pal, title, detail):
    x = x0 + (LANE_W - NODE_W) / 2
    return (doc_shape(x, y, NODE_W, 40, pal)
            + text(x + 12, y + 17, title, 13, pal["ink"], bold=True, room=NODE_W - 30, where="input")
            + text(x + 12, y + 33, detail, 11.5, pal["ink2"], room=NODE_W - 24, where="input detail")), 40


def node_skill(x0, y, pal, name, detail):
    x = x0 + (LANE_W - NODE_W) / 2
    return (rect(x, y, NODE_W, 48, fill=pal["paper"], stroke=pal["ink"], sw=1.6, rx=4)
            + text(x + 12, y + 20, name, 13.5, pal["ink"], mono=True, room=NODE_W - 24, where="skill node")
            + text(x + 12, y + 38, detail, 11.5, pal["ink2"], room=NODE_W - 24, where="skill detail")), 48


def node_hold(x0, y, pal, detail):
    x = x0 + (LANE_W - NODE_W) / 2
    c = pal["hold"]
    return (rect(x, y, NODE_W, 44, fill=pal["paper"], stroke=c, sw=1.6, rx=22, dash="5 3")
            + stamp(x + 24, y + 22, pal)
            + text(x + 48, y + 18, "Hold point", 9.5, c, bold=True, caps=True, spacing=0.08)
            + text(x + 48, y + 34, detail, 12.5, pal["ink"], bold=True, room=NODE_W - 58, where="hold")), 44


def node_registry(x0, y, pal, title, detail):
    x = x0 + (LANE_W - NODE_W) / 2
    ink = pal["ink"]
    icon = [rect(x + 12, y + 9, 20, 26, fill=pal["doc"], stroke=ink, sw=1.1)]
    for j in range(4):
        icon.append(line(x + 16, y + 15 + j * 5, x + 28, y + 15 + j * 5, ink, 0.9))
    return (rect(x, y, NODE_W, 44, fill=pal["paper"], stroke=ink, sw=1.1, rx=4)
            + "".join(icon)
            + text(x + 42, y + 19, title, 13, ink, bold=True, room=NODE_W - 50, where="registry")
            + text(x + 42, y + 35, detail, 11.5, pal["ink2"], room=NODE_W - 50, where="registry detail")), 44


def node_producers(x0, y, pal, names):
    x = x0 + (LANE_W - NODE_W) / 2
    pill_h, gap, pad = 17, 3, 8
    h = len(names) * (pill_h + gap) - gap + 2 * pad
    out = [rect(x, y, NODE_W, h, stroke=pal["ink2"], sw=1.0, rx=4, dash="4 3")]
    for j, n in enumerate(names):
        py = y + pad + j * (pill_h + gap)
        out.append(rect(x + 14, py, NODE_W - 28, pill_h, fill=pal["paper"], stroke=pal["ink"], sw=1.0, rx=8.5))
        out.append(text(x + 24, py + 12.5, n, 11, pal["ink"], mono=True, room=NODE_W - 48, where="producer"))
    return "".join(out), h


def arrow_down(x, y1, y2, pal, label=None, chip_label=None, room=None):
    c = pal["ink"]
    out = [line(x, y1, x, y2 - 7, c, 1.3), head_down(x, y2, c)]
    if label:
        ly = (y1 + y2) / 2 + 4
        lx = x + 9
        if chip_label:
            # The chip goes first, at a fixed place, so no font's label width can push it off.
            svg, cw = chip(lx, ly - 4, chip_label, pal)
            out.append(svg)
            lx += cw + 5
            room = None if room is None else room - cw - 5
        out.append(text(lx, ly, label, 11.5, pal["ink2"], room=room, where="arrow label"))
    return "".join(out)


def side_input(x_arrow, y_mid, label, pal, room):
    """A document that joins a flow from the left, with a short arrow into the main line."""
    w = est_width(label, 11.5) + 22
    if w > room:
        problems.append(f"side input: '{label}' needs {w:.0f}px, has {room:.0f}px")
    x1 = x_arrow - 14
    x = x1 - w
    ink = pal["ink"]
    return (doc_shape(x, y_mid - 11, w, 22, pal, fold=7)
            + text(x + 8, y_mid + 4, label, 11.5, ink)
            + line(x1, y_mid, x_arrow - 7, y_mid, ink, 1.1) + head_right(x_arrow - 1, y_mid, ink))


def lane_header(i, letter, title, subtitle, pal, y=112):
    x0 = lane_x(i)
    ink = pal["ink"]
    return (f'<circle cx="{x0 + 12:g}" cy="{y:g}" r="12" fill="none" stroke="{ink}" stroke-width="1.4"/>'
            + text(x0 + 12, y + 4.5, letter, 12.5, ink, bold=True, anchor="middle")
            + text(x0 + 32, y - 1, title, 11.5, ink, bold=True, caps=True, upper=False, spacing=0.06,
                   room=LANE_W - 34, where="lane title")
            + text(x0 + 32, y + 14, subtitle, 11.5, pal["ink2"], room=LANE_W - 34, where="lane subtitle")
            + line(x0, y + 22, x0 + LANE_W, y + 22, ink, 1.0))


def file_card(x0, y, pal, name, detail, chip_label):
    x = x0 + (LANE_W - NODE_W) / 2
    ink = pal["ink"]
    svg = [rect(x, y, NODE_W, 52, fill=pal["band"], stroke=ink, sw=1.1, rx=4),
           doc_shape(x + 12, y + 8, 28, 36, pal, fold=8)]
    c, cw = chip(x + 12 + 14 - chip_width(chip_label) / 2, y + 36, chip_label, pal)
    svg.append(c)
    svg.append(text(x + 58, y + 22, name, 13.5, ink, bold=True, room=NODE_W - 66, where="file card"))
    svg.append(text(x + 58, y + 39, detail, 11.5, pal["ink2"], room=NODE_W - 66, where="file card detail"))
    return "".join(svg)


ISSUE_PRODUCERS = ["pe-review", "submittal-review", "tag-audit-and-takeoff", "code-researcher",
                   "submittal-log-generator", "spec-splitter"]


def g002(pal):
    ink = pal["ink"]
    parts = [view_title(2, "G-002", "How the skills hand off work",
                        "Each chain ends in a file in your project folder. The skill stops at every hold point until you decide.",
                        pal)]
    y_top, y_files = 150, 552
    lanes = [
        ("A", "SUBMITTAL REGISTER", "From the project manual",
         [("doc", "Project manual", "one bound PDF"),
          ("skill", "spec-splitter", "One PDF and text per section"),
          ("skill", "submittal-log-generator", "Every Part 1 submittal item")],
         ["bound PDF", "section text", "submittal items"],
         [None, None, None],
         ("Submittal log", "every section's items", "XLSX")),
        ("B", "BIDS TO SUBCONTRACT", "From bid day to an agreement",
         [("doc", "Subcontractor bids", "PDF, one per bidder"),
          ("skill", "bid-tabulator", "Flags errors, never corrects"),
          ("skill", "bid-evaluator", "Scope gaps, exclusion risk"),
          ("hold", "You choose the award"),
          ("skill", "subcontract-writer", "Scope from the bid and specs")],
         ["as submitted", "bid tab", "recommendation", "awarded bid", "subcontract"],
         [None, "XLSX", None, None, None],
         ("Subcontract", "+ bid tab, evaluation", "DOCX"),
         {2: "Contract docs", 4: "Firm template"}),
        ("C", "FLAGGED ISSUES TO RFIs", "From what the skills find",
         [("producers",),
          ("registry", "Issue registry", "conflicts and questions"),
          ("hold", "You pick the RFIs"),
          ("skill", "rfi-drafter", "Researches, then drafts")],
         ["log as they work", "open issues", "chosen issue", "RFI draft"],
         [None, None, None, None],
         ("RFI", "in your firm's form", "DOCX"),
         {3: "Firm RFI form"}),
    ]
    for i, lane in enumerate(lanes):
        letter, title, subtitle, nodes, labels, chips, card = lane[:7]
        side = lane[7] if len(lane) > 7 else {}
        x0 = lane_x(i)
        xc = x0 + LANE_W / 2
        parts.append(lane_header(i, letter, title, subtitle, pal))
        # Measure the nodes first, then share the height left over equally between the arrows.
        heights = []
        for n in nodes:
            heights.append({"doc": 40, "skill": 48, "hold": 44, "registry": 44,
                            "producers": len(ISSUE_PRODUCERS) * 20 - 3 + 16}[n[0]])
        gap = (y_files - y_top - sum(heights)) / len(nodes)
        if gap < 30:
            problems.append(f"lane {letter}: arrows only {gap:.0f}px long")
        y = y_top
        for j, n in enumerate(nodes):
            kind = n[0]
            if kind == "doc":
                svg, h = node_doc(x0, y, pal, n[1], n[2])
            elif kind == "skill":
                svg, h = node_skill(x0, y, pal, n[1], n[2])
            elif kind == "hold":
                svg, h = node_hold(x0, y, pal, n[1])
            elif kind == "registry":
                svg, h = node_registry(x0, y, pal, n[1], n[2])
            else:
                svg, h = node_producers(x0, y, pal, ISSUE_PRODUCERS)
            parts.append(svg)
            y_next = y + h + gap
            parts.append(arrow_down(xc, y + h, y_next, pal, labels[j], chips[j], room=x0 + LANE_W - xc - 9))
            if j + 1 in side:
                parts.append(side_input(xc, y + h + gap / 2, side[j + 1], pal, room=xc - 14 - x0))
            y = y_next
        parts.append(file_card(x0, y_files, pal, *card))

    fy = y_files + 52 + 18
    parts.append(line(L, fy, R, fy, ink, 1.0))
    parts.append(stamp(L + 18, fy + 22, pal, r=12))
    parts.append(text(L + 40, fy + 27, "Every file is a draft in your project folder. Nothing is sent, signed or approved for you.",
                      12.5, ink, bold=True, room=R - L - 48, where="footer"))
    H = fy + 44 + 12 + TITLE_BLOCK_H + INNER
    desc = ("Three chains. A: spec-splitter splits the bound project manual into sections and text, and "
            "submittal-log-generator turns every Part 1 submittal item into the submittal log. B: bid-tabulator "
            "tabulates the bids as submitted, bid-evaluator checks them against the contract documents and "
            "recommends, the PE chooses the award at a hold point, and subcontract-writer drafts the subcontract "
            "from the firm's template. C: pe-review, submittal-review, tag-audit-and-takeoff, code-researcher, "
            "submittal-log-generator and spec-splitter log issues as they work; the PE picks which become RFIs, "
            "and rfi-drafter drafts each in the firm's RFI form. Every file is a draft; nothing is sent, signed or "
            "approved for the PE.")
    return sheet("g002", "How the skills hand off work", "G-002", H, "\n".join(parts), pal, desc)


# ---------------------------------------------------------------------------------------------
# G-003  Inside a submittal review: nine steps, a checkpoint with the PE, and a gate before the report.

COL, BOX_W, BOX_H = 164, 148, 96


def col_x(i):
    return L + i * COL


STEPS = {
    # number: (title lines, detail lines, kind)
    1: (["Intake"], ["Number, sections,", "types, prior review"], "step"),
    2: (["Trace", "requirements"], ["From the contract", "documents, first"], "step"),
    3: (["Inventory"], ["Each element's", "pages, or missing"], "step"),
    4: (["Checkpoint"], ["Facility, authority", "and code research"], "hold"),
    5: (["Review each", "element"], ["Every governing", "reference, read"], "stack"),
    6: (["Package", "questions"], ["Reconcile what", "must agree"], "step"),
    7: (["Code and", "routing"], ["Who acts, and by", "which milestone"], "step"),
    8: (["Completeness", "gate"], ["Stops on any", "unaccounted item"], "gate"),
    9: (["Draft GC", "review"], ["Every finding", "cites both sources"], "step"),
}


def step_box(x, y, pal, number, titles, details, kind):
    ink, ink2, c = pal["ink"], pal["ink2"], pal["hold"]
    out = []
    if kind == "stack":
        for off in (8, 4):
            out.append(rect(x + off, y - off, BOX_W, BOX_H, fill=pal["paper"], stroke=ink, sw=1.0, rx=4))
    stroke, sw, dash = ink, 1.6, None
    if kind == "hold" or kind == "final":
        stroke, dash = c, "5 3"
    if kind == "gate":
        sw = 2.6
    out.append(rect(x, y, BOX_W, BOX_H, fill=pal["paper"], stroke=stroke, sw=sw, rx=4, dash=dash))
    if kind == "final":
        out.append(stamp(x + 20, y + 21, pal, r=12))
    elif kind == "gate":
        # A decision diamond carries the gate's number, as a flowchart draws a decision.
        gx, gy = x + 18, y + 21
        out.append(polygon([(gx, gy - 13), (gx + 13, gy), (gx, gy + 13), (gx - 13, gy)], ink))
        out.append(text(gx, gy + 4.5, str(number), 12, pal["paper"], bold=True, anchor="middle"))
    else:
        out.append(f'<circle cx="{x + 18:g}" cy="{y + 21:g}" r="10" fill="{ink}"/>')
        out.append(text(x + 18, y + 25.5, str(number), 12, pal["paper"], bold=True, anchor="middle"))
    if kind == "hold":
        out.append(stamp(x + BOX_W - 18, y + 20, pal, r=11))
    tx = x + (40 if kind == "final" else 34)
    title_room = x + BOX_W - tx - (30 if kind == "hold" else 8)
    for k, t in enumerate(titles):
        out.append(text(tx, y + 26 + k * 16, t, 12.5, ink, bold=True, room=title_room, where="step title"))
    for k, d in enumerate(details):
        out.append(text(x + 10, y + 66 + k * 15, d, 11.5, ink2, room=BOX_W - 16, where="step detail"))
    return "".join(out)


def g003(pal):
    ink, ink2 = pal["ink"], pal["ink2"]
    parts = [view_title(3, "G-003", "Inside a submittal review",
                        "Traces the contract documents before it opens the submittal; "
                        "reports only after its gate passes", pal)]
    in_y, r1, r2 = 102, 178, 318
    cy1, cy2 = r1 + BOX_H / 2, r2 + BOX_H / 2

    # What comes in: the contract documents feed step 2, the submittal feeds step 3. Each document spans
    # two columns so its name fits; its arrow drops onto the step it feeds.
    in_w = COL + BOX_W
    for x, target, title, detail in [
            (col_x(0), 1, "Contract documents", "drawings, specs, schedules, RFIs, ASIs"),
            (col_x(2), 2, "Submittal package", "shop drawings, product data, samples")]:
        parts.append(doc_shape(x, in_y, in_w, 42, pal))
        parts.append(text(x + 12, in_y + 18, title, 12.5, ink, bold=True, room=in_w - 30, where="input"))
        parts.append(text(x + 12, in_y + 34, detail, 11.5, ink2, room=in_w - 24, where="input detail"))
        ax = col_x(target) + BOX_W / 2
        parts.append(line(ax, in_y + 42, ax, r1 - 7, ink, 1.3))
        parts.append(head_down(ax, r1, ink))

    # Row 1: steps 1 to 5, left to right.
    for i, n in enumerate(range(1, 6)):
        titles, details, kind = STEPS[n]
        parts.append(step_box(col_x(i), r1, pal, n, titles, details, kind))
        if i < 4:
            x1, x2 = col_x(i) + BOX_W, col_x(i + 1)
            parts.append(line(x1, cy1, x2 - 7, cy1, ink, 1.3) + head_right(x2, cy1, ink))

    # The turn from step 5 back to the start of row 2.
    xr, xl = col_x(4) + BOX_W / 2, col_x(0) + BOX_W / 2
    ym = (r1 + BOX_H + r2) / 2
    parts.append(path(f"M{xr:g},{r1 + BOX_H:g} V{ym:g} H{xl:g} V{r2 - 7:g}", stroke=ink, sw=1.3))
    parts.append(head_down(xl, r2, ink))

    # Row 2: steps 6 to 9, then the PE's decision.
    for i, n in enumerate(range(6, 10)):
        titles, details, kind = STEPS[n]
        parts.append(step_box(col_x(i), r2, pal, n, titles, details, kind))
    parts.append(step_box(col_x(4), r2, pal, None, ["You decide", "and send"],
                          ["Disposition is a", "suggestion only"], "final"))
    for i in range(4):
        x1, x2 = col_x(i) + BOX_W, col_x(i + 1)
        parts.append(line(x1, cy2, x2 - 7, cy2, ink, 1.3) + head_right(x2, cy2, ink))

    # The gate re-runs until nothing is unaccounted for.
    gx = col_x(2)
    yb = r2 + BOX_H
    parts.append(path(f"M{gx + 112:g},{yb:g} V{yb + 22:g} H{gx + 36:g} V{yb + 8:g}", stroke=pal["ink"], sw=1.3,
                      dash="4 3"))
    parts.append(head_up(gx + 36, yb + 1, ink))
    parts.append(text(gx + BOX_W / 2, yb + 40, "fix the gap, re-run", 11.5, ink2, anchor="middle",
                      room=COL, where="gate loop"))

    # What step 9 leaves.
    ox = col_x(3)
    parts.append(line(ox + BOX_W / 2, yb, ox + BOX_W / 2, yb + 15, ink, 1.3) + head_down(ox + BOX_W / 2, yb + 22, ink))
    outs = [("XLSX", "GC Review"), ("PDF", "GC Markup"), (None, "Issues for RFIs")]
    oy = yb + 24
    for k, (kind, label) in enumerate(outs):
        y = oy + k * 28
        parts.append(rect(ox, y, BOX_W, 24, fill=pal["band"], stroke=ink, sw=1.0, rx=3))
        if kind:
            parts.append(chip(ox + 8, y + 12, kind, pal)[0])
            lx = ox + 8 + chip_width(kind) + 7
        else:
            parts.append(rect(ox + 10, y + 5, 12, 14, fill=pal["doc"], stroke=ink, sw=0.9))
            for j in range(3):
                parts.append(line(ox + 12.5, y + 9 + j * 3.5, ox + 19.5, y + 9 + j * 3.5, ink, 0.8))
            lx = ox + 30
        parts.append(text(lx, y + 16.5, label, 11.5, ink, bold=True, room=ox + BOX_W - 6 - lx, where="output"))

    # A key for the two marks this sheet adds.
    ky = yb + 34
    parts.append(stamp(col_x(0) + 16, ky, pal, r=11))
    parts.append(text(col_x(0) + 34, ky + 4, "Hold point: the skill stops for you", 11.5, ink2,
                      room=2 * COL - 40, where="key"))
    parts.append(polygon([(col_x(0) + 16, ky + 20), (col_x(0) + 25, ky + 29), (col_x(0) + 16, ky + 38),
                          (col_x(0) + 7, ky + 29)], ink))
    parts.append(text(col_x(0) + 34, ky + 33, "Gate: no report until it passes", 11.5, ink2,
                      room=2 * COL - 40, where="key"))

    H = oy + 3 * 28 + 14 + TITLE_BLOCK_H + INNER
    desc = ("The nine steps of a submittal review. The contract documents feed step 2, which traces every "
            "required element before the submittal is opened; the submittal feeds step 3, the inventory. Step 4 "
            "is a hold point where the PE confirms facility type, jurisdiction and code research. Step 5 reviews "
            "each element against every governing reference, in parallel for large packages. Steps 6 and 7 "
            "reconcile documents and route coordination to trades. Step 8 is a completeness gate that re-runs "
            "until nothing is unaccounted for. Step 9 drafts the GC review, a marked-up PDF and issues for RFIs; "
            "the PE decides the disposition and sends it.")
    return sheet("g003", "Inside a submittal review", "G-003", H, "\n".join(parts), pal, desc)


FIGURES = {
    "skills-by-phase": g001,
    "skill-handoffs": g002,
    "submittal-review-steps": g003,
}


def main():
    rendered = {}
    for name, draw in FIGURES.items():
        for variant, pal in PALETTES.items():
            rendered[f"{name}-{variant}.svg"] = draw(pal)
    if problems:
        for p in sorted(set(problems)):
            print("TOO LONG", p)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    for filename, svg in rendered.items():
        (OUT / filename).write_text(svg, encoding="utf-8", newline="\n")
        print("wrote", (OUT / filename).relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
