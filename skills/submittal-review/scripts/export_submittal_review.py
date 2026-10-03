#!/usr/bin/env python3
"""Export a submittal review to Excel, compute the suggested GC disposition, and write
markup items for annotate_pdf.py.

    export_submittal_review.py --review-dir <dir> --output "<folder>/<no> R0 - GC Review.xlsx"
                               [--annotations <dir>/markup] [--allow-gaps]

Refuses to export while check_coverage.py reports gaps, unless --allow-gaps (the
workbook is then marked INCOMPLETE). Never overwrites: existing outputs get _v2, _v3.
Rules for the disposition: ../references/review-writing.md
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_coverage import check, load_batches, load_json  # noqa: E402
from shared import safe_output_path  # noqa: E402

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
SEV_FILL = {"critical": "F4B6B6", "high": "F8D7A8", "medium": "FBEFB5", "low": "E3EEF7"}
STATUS_FILL = {"finding": "F8D7A8", "unverifiable": "FBEFB5", "na": "EEEEEE", "pass": "D9EFD9"}


def suggest_disposition(findings, inventory, compliance, ctx, coverage):
    sub = [f for f in findings if f.get("owner") == "subcontractor"]
    missing = [e for e in inventory.get("elements", []) if e.get("status") == "missing"]
    missing += [p for p in inventory.get("package_items", []) if p.get("status") == "missing"]
    if missing:
        action = "Return to subcontractor — incomplete; revise and resubmit"
        why = f"{len(missing)} required element(s) or Part 1 item(s) not submitted"
    elif any(f.get("severity") in ("critical", "high") for f in sub):
        action = "Return to subcontractor — revise and resubmit"
        n = sum(1 for f in sub if f.get("severity") in ("critical", "high"))
        why = f"{n} critical/high finding(s) for the subcontractor to correct"
    elif sub:
        action = "Forward to design team with GC comments"
        why = f"{len(sub)} medium/low finding(s) noted for correction"
    else:
        action = "Forward to design team — no GC exceptions"
        why = "No subcontractor findings"
    extras = []
    design = [f for f in findings if f.get("owner") == "design_team"]
    if design:
        extras.append(f"plus {len(design)} RFI candidate(s) for the design team")
    hooks = {h["id"]: h for h in ctx.get("regulatory_hooks", [])}
    open_serious = [r for r in compliance if r.get("result") == "open"
                    and hooks.get(r.get("hook"), {}).get("severity") in ("critical", "high")]
    if open_serious:
        extras.append(f"{len(open_serious)} high/critical compliance question(s) open: research before release for fabrication")
    unver = [r for r in coverage if r.get("status") == "unverifiable"]
    if unver:
        extras.append(f"{len(unver)} item(s) could not be verified")
    return action, why, extras


def _style_header(ws, row, ncols):
    from openpyxl.styles import Font, PatternFill
    for col in range(1, ncols + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="3A4A5C")


def _table(ws, headers, rows, widths, fill_col=None, fills=None):
    from openpyxl.styles import Alignment, PatternFill
    ws.append(headers)
    _style_header(ws, ws.max_row, len(headers))
    start = ws.max_row + 1
    for r in rows:
        ws.append(r)
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + i)].width = w
    for row in ws.iter_rows(min_row=start, max_row=ws.max_row):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        if fill_col is not None and fills:
            key = str(row[fill_col].value or "").lower()
            if key in fills:
                row[fill_col].fill = PatternFill("solid", fgColor=fills[key])
    ws.freeze_panes = ws.cell(row=start, column=1)


def build_workbook(d, state, ctx, findings, coverage, inventory, routing, compliance, prior, report, disposition):
    from openpyxl import Workbook
    from openpyxl.styles import Font

    files = (state.get("submittal") or {}).get("files") or []
    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    sub = state.get("submittal") or {}
    action, why, extras = disposition
    s = report["stats"]
    lines = [
        ("GC SUBMITTAL REVIEW — DRAFT FOR PE DECISION", None),
        ("Submittal", f"{sub.get('number', '')} R{sub.get('revision', 0)} — {sub.get('title', '')}"),
        ("Subcontractor", sub.get("subcontractor", "")),
        ("Spec section(s)", ", ".join(state.get("sections", []))),
        ("Submittal types", ", ".join(sub.get("types", []))),
        ("Facility types", ", ".join(state.get("facility_types", [])) or "none"),
        ("Suggested GC action", action),
        ("Because", why),
        ("Also", "; ".join(extras) or "—"),
        ("Findings", ", ".join(f"{sev}: {sum(1 for f in findings if f.get('severity') == sev)}"
                               for sev in SEV_ORDER)),
        ("By owner", ", ".join(f"{o}: {sum(1 for f in findings if f.get('owner') == o)}"
                               for o in ("subcontractor", "gc", "design_team", "owner"))),
        ("Coverage", f"{s.get('coverage_rows_present')}/{s.get('coverage_rows_expected')} element × check rows "
                     f"({s.get('coverage_pct')}%); {s.get('unverifiable')} unverifiable"),
        ("Elements", f"{s.get('elements_reviewed')} reviewed, {s.get('elements_missing')} missing, "
                     f"of {s.get('elements_in_trace')} in the contract documents"),
        ("Open compliance questions", str(s.get("open_compliance"))),
        ("Knowledge confidence", f"{ctx.get('confidence_floor')} (knowledge layer status for this section)"),
        ("Coverage gate", "PASSED" if report["ok"] else f"INCOMPLETE — {len(report['gaps'])} gaps"),
    ]
    for note in state.get("notes", []) or []:
        lines.append(("Assumption", note))
    for k, v in lines:
        ws.append([k, v])
    ws["A1"].font = Font(bold=True, size=13)
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=1):
        row[0].font = Font(bold=True)
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 110

    def page_ref(f):
        sp = f.get("submittal") or {}
        if not isinstance(sp.get("page"), int):
            return ""
        name = Path(files[sp.get("file", 0)]).name if files and sp.get("file", 0) < len(files) else "file"
        return f"{name} p{sp['page']}"

    ws = wb.create_sheet("Findings")
    rows = []
    for f in sorted(findings, key=lambda f: (SEV_ORDER.get(f.get("severity"), 9), f.get("id", ""))):
        req = f.get("requirement") or {}
        rows.append([f.get("id"), f.get("severity"), f.get("owner"), f.get("kind"), f.get("grade"),
                     f.get("element"), f.get("finding"), f"{req.get('source', '')}: {req.get('text', '')}".strip(": "),
                     page_ref(f), f.get("action"), "yes" if f.get("rfi_candidate") else "", f.get("check")])
    _table(ws, ["ID", "Severity", "Owner", "Kind", "Grade", "Element", "Finding", "Governing requirement",
                "Submittal", "Action", "RFI candidate", "Check"],
           rows, [8, 10, 14, 15, 13, 14, 60, 50, 22, 50, 10, 26], fill_col=1, fills=SEV_FILL)

    ws = wb.create_sheet("Routing")
    rel = [r for r in routing if r.get("relevant")]
    rows = [[r.get("interface"), r.get("trade"), ", ".join(r.get("sections", [])), r.get("send"), r.get("ask"),
             r.get("confirm", ""), r.get("gate", ""), r.get("need_by") or "", ", ".join(r.get("findings", []) or [])]
            for r in sorted(rel, key=lambda r: (r.get("need_by") or "9999", r.get("interface")))]
    _table(ws, ["Interface", "Trade", "Sections", "Send them", "Ask", "Confirm who", "Gate", "Need by", "Findings"],
           rows, [26, 22, 18, 40, 50, 40, 20, 12, 16])
    ws.append([])
    ws.append(["Not relevant to this submittal"])
    ws.cell(row=ws.max_row, column=1).font = Font(bold=True)
    for r in routing:
        if not r.get("relevant"):
            ws.append([r.get("interface"), r.get("reason")])

    ws = wb.create_sheet("Compliance")
    hooks = {h["id"]: h for h in ctx.get("regulatory_hooks", [])}
    rows = []
    for r in compliance:
        h = hooks.get(r.get("hook"), {})
        rows.append([r.get("hook"), h.get("severity"), r.get("binding"), r.get("result"),
                     " ".join(str(h.get("question", "")).split()), ", ".join(r.get("affects", []) or []),
                     r.get("finding") or "", r.get("note", "")])
    _table(ws, ["Hook", "Severity", "Research", "Result", "Question", "Affects", "Finding", "Note"],
           rows, [32, 10, 18, 12, 70, 18, 10, 60], fill_col=3, fills={"open": "FBEFB5", "finding": "F8D7A8"})

    ws = wb.create_sheet("Coverage")
    rows = [[r.get("element"), r.get("check"), r.get("status"), r.get("finding") or "",
             ", ".join(r.get("evidence", []) or []), r.get("note", "")] for r in coverage]
    _table(ws, ["Element", "Check", "Status", "Finding", "Evidence", "Note"], rows, [16, 34, 13, 10, 40, 60],
           fill_col=2, fills=STATUS_FILL)

    ws = wb.create_sheet("Elements")
    inv = {e.get("id"): e for e in inventory.get("elements", [])}
    trace = load_json(d / "trace.json", {})
    rows = []
    for e in trace.get("elements", []):
        i = inv.get(e.get("id"), {})
        pages = ", ".join(f"p{p.get('page')}" for p in i.get("pages", []) or [])
        rows.append([e.get("id"), e.get("type"), e.get("label"), "; ".join(e.get("cd_refs", []) or []),
                     i.get("status", "not inventoried"), pages])
    for x in inventory.get("extra_items", []):
        rows.append(["(not in CDs)", "", x.get("label"), "", "extra", x.get("note", "")])
    _table(ws, ["Element", "Type", "Description", "Contract document references", "Submittal", "Pages"],
           rows, [16, 20, 40, 70, 14, 20])

    if prior:
        ws = wb.create_sheet("Prior comments")
        rows = [[p.get("prior_finding"), p.get("status"), p.get("evidence", ""), p.get("finding") or ""] for p in prior]
        _table(ws, ["Prior finding", "Status", "Evidence", "New finding"], rows, [14, 16, 80, 12])

    if not report["ok"]:
        ws = wb.create_sheet("Coverage gaps")
        _table(ws, ["Gap"], [[g] for g in report["gaps"]], [140])
    return wb


def markup_items(findings, files, project_root):
    """One JSON list per submittal file, in annotate_pdf.py's item format."""
    try:
        import fitz
    except ImportError:
        fitz = None
    per_file = {}
    stack = {}
    for f in sorted(findings, key=lambda f: (SEV_ORDER.get(f.get("severity"), 9), f.get("id", ""))):
        sp = f.get("submittal") or {}
        page = (f.get("markup") or {}).get("page") or sp.get("page")
        if not isinstance(page, int):
            continue
        idx = sp.get("file", 0)
        if idx >= len(files):
            continue
        color = "red" if f.get("severity") in ("critical", "high") else "orange"
        text = f"{f.get('id')} [{f.get('severity')}] {f.get('finding')} ACTION: {f.get('action')}"
        items = per_file.setdefault(idx, [])
        rect = (f.get("markup") or {}).get("rect")
        if rect:
            items.append({"page": page, "shape": "cloud", "rect": rect, "color": color,
                          "label": f.get("id"), "content": text, "subject": "GC review (draft)"})
        width, height = 612.0, 792.0
        if fitz is not None:
            path = Path(files[idx])
            path = path if path.is_absolute() else project_root / path
            if path.exists():
                with fitz.open(path) as doc:
                    if 0 < page <= len(doc):
                        width, height = doc[page - 1].rect.width, doc[page - 1].rect.height
        n = stack.get((idx, page), 0)
        stack[(idx, page)] = n + 1
        box_w = min(260.0, width * 0.32)
        x1 = width - 18
        y0 = 18 + n * 58
        if y0 + 54 > height - 18:
            y0 = height - 72
        items.append({"page": page, "shape": "text", "rect": [x1 - box_w, y0, x1, y0 + 54], "color": color,
                      "fontsize": 7, "label": text[:400], "content": text, "subject": "GC review (draft)"})
    return per_file


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review-dir", required=True)
    ap.add_argument("--output", required=True, help="Excel file to write (never overwritten)")
    ap.add_argument("--annotations", help="Folder for markup item files, one per submittal file")
    ap.add_argument("--allow-gaps", action="store_true", help="Export even though coverage is incomplete")
    args = ap.parse_args()

    d = Path(args.review_dir).resolve()
    report = check(d)
    if not report["ok"] and not args.allow_gaps:
        print(f"Coverage gate failed ({len(report['gaps'])} gaps). Run check_coverage.py and fix them first.")
        for g in report["gaps"][:20]:
            print(f"GAP   {g}")
        return 1

    state = yaml.safe_load((d / "state.yaml").read_text(encoding="utf-8")) or {}
    ctx = yaml.safe_load((d / "context.yaml").read_text(encoding="utf-8")) or {}
    findings = load_batches(d, "findings")
    coverage = load_batches(d, "coverage")
    inventory = load_json(d / "inventory.json", {})
    routing = load_json(d / "routing.json", [])
    compliance = load_json(d / "compliance.json", [])
    prior = load_json(d / "prior.json", [])

    disposition = suggest_disposition(findings, inventory, compliance, ctx, coverage)
    wb = build_workbook(d, state, ctx, findings, coverage, inventory, routing, compliance, prior, report, disposition)
    out = safe_output_path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    print(f"Wrote {out}")

    if args.annotations:
        project_root = d.parents[3] if len(d.parents) > 3 else Path.cwd()
        files = (state.get("submittal") or {}).get("files") or []
        folder = Path(args.annotations)
        folder.mkdir(parents=True, exist_ok=True)
        for idx, items in markup_items(findings, files, project_root).items():
            path = folder / f"{Path(files[idx]).stem}.json"
            path.write_text(json.dumps(items, indent=2), encoding="utf-8")
            print(f"Wrote {path} ({len(items)} markups)")

    action, why, extras = disposition
    print(f"Suggested GC action: {action} — {why}" + (f"; {'; '.join(extras)}" if extras else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
