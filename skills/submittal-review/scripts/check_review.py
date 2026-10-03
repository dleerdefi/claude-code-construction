#!/usr/bin/env python3
"""Completeness gate for a submittal review.

Proves the review accounted for every element in the contract documents, read every
document that governs each element, answered every package question, backed every
finding with both sources and an action, routed every coordination finding, kept code
questions open unless code-researcher answered them, and closed out every prior
finding on a resubmittal. Exits 1 if anything is missing.

    check_review.py --review-dir .construction/skills/submittal-review/<review_id> [--json report.json]

Before reviewing, write the records a batch owes, then fill each one in:

    check_review.py --review-dir <dir> --scaffold 01 --elements "1/A-501,2/A-501"
    check_review.py --review-dir <dir> --scaffold 90 --package

File formats: ../references/review-data.md
"""

import argparse
import glob
import json
import re
import sys
from pathlib import Path

import yaml

SEVERITIES = {"critical", "high", "medium", "low"}
OWNERS = {"subcontractor", "gc", "design_team", "owner"}
KINDS = {"completeness", "conformance", "coordination", "constructability", "absence", "compliance"}
GRADES = {"CONFLICTING", "NOT FOUND", "OPEN"}
REF_STATUS = {"read", "unavailable"}
PACKAGE_STATUS = {"pass", "finding", "na", "unverifiable"}
PRIOR_STATUS = {"closed", "partially_closed", "open"}
TODO = "todo"
PACKAGE_ITEMS = ["pk.current-documents", "pk.basis-of-design", "pk.products-marked", "pk.deviations",
                 "pk.by-others", "pk.field-verify", "pk.delegated-design", "pk.lead-time"]
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SKILL_DIR = Path(__file__).resolve().parent.parent


class GateError(Exception):
    pass


def load_json(path, default):
    p = Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise GateError(f"{p.name} is not valid JSON: {e}") from None


def load_batches(review_dir, prefix):
    rows = []
    for path in sorted(glob.glob(str(Path(review_dir) / f"{prefix}_*.json"))):
        data = load_json(path, [])
        if not isinstance(data, list):
            raise GateError(f"{Path(path).name} must be a JSON array")
        rows.extend(data)
    return rows


def milestone_ids():
    data = yaml.safe_load((SKILL_DIR / "references" / "milestones.yaml").read_text(encoding="utf-8")) or {}
    return set((data.get("milestones") or {}).keys())


def project_root(review_dir):
    """<root>/.construction/skills/submittal-review/<id> -> <root>"""
    d = Path(review_dir).resolve()
    for parent in d.parents:
        if parent.name == ".construction":
            return parent.parent
    return Path.cwd()


def check(review_dir):
    d = Path(review_dir)
    gaps, notes = [], []
    try:
        return _check(d, gaps, notes)
    except GateError as e:
        return {"ok": False, "gaps": gaps + [str(e)], "notes": notes, "stats": {}}


def _check(d, gaps, notes):
    state_path = d / "state.yaml"
    if not state_path.exists():
        raise GateError("Missing state.yaml (Step 1)")
    state = yaml.safe_load(state_path.read_text(encoding="utf-8")) or {}
    files = (state.get("submittal") or {}).get("files") or []
    if not files:
        gaps.append("state.yaml: submittal.files is empty")

    trace = load_json(d / "trace.json", None)
    inventory = load_json(d / "inventory.json", None)
    if trace is None:
        raise GateError("Missing trace.json (Step 2)")
    if inventory is None:
        raise GateError("Missing inventory.json (Step 3)")
    trace_el = {e.get("id"): e for e in trace.get("elements", [])}
    if not trace_el:
        gaps.append("trace.json lists no elements")

    findings = load_batches(d, "findings")
    records = load_batches(d, "review")
    package = load_json(d / "package_review.json", None)
    routing = load_json(d / "routing.json", None)
    compliance = load_json(d / "compliance.json", None)

    fids = {}
    for f in findings:
        fid = f.get("id")
        if not fid:
            gaps.append(f"Finding without id: {str(f)[:80]}")
        elif fid in fids:
            gaps.append(f"Duplicate finding id {fid}")
        else:
            fids[fid] = f

    # ── Trace ↔ inventory, both ways
    inv = {}
    for e in inventory.get("elements", []):
        if e.get("id") in inv:
            gaps.append(f"Inventory lists {e.get('id')} twice")
        inv[e.get("id")] = e
    for eid in trace_el:
        if eid not in inv:
            gaps.append(f"Element {eid} is in the trace but not in the inventory")
    for eid, e in inv.items():
        if eid not in trace_el:
            gaps.append(f"Inventory element {eid} is not in the trace (put submittal-only items in extra_items)")
        if e.get("status") not in ("submitted", "partial", "missing"):
            gaps.append(f"Inventory {eid}: status must be submitted, partial or missing")
        for p in e.get("pages", []) or []:
            if not isinstance(p.get("file"), int) or p["file"] >= len(files):
                gaps.append(f"Inventory {eid}: page reference {p} names no submittal file")
    completeness = {f.get("element") for f in fids.values() if f.get("kind") == "completeness"}
    missing = [eid for eid, e in inv.items() if e.get("status") == "missing"]
    for eid in missing:
        if eid not in completeness:
            gaps.append(f"Element {eid} is missing from the submittal but has no completeness finding")
    for item in inventory.get("package_items", []):
        if item.get("status") == "missing" and "package" not in completeness:
            gaps.append(f"Package requirement {item.get('ref')} is missing but there is no package completeness finding")
    for item in inventory.get("extra_items", []):
        if not item.get("note"):
            gaps.append(f"Extra submittal item {item.get('label')!r} needs a note (what it is, what to do)")

    # ── One record per reviewed element; every governing reference accounted for
    reviewed = [eid for eid, e in inv.items() if e.get("status") in ("submitted", "partial")]
    rec = {}
    for r in records:
        eid = r.get("element")
        if eid in rec:
            gaps.append(f"Element {eid} has two review records")
        rec[eid] = r
        if eid not in trace_el:
            gaps.append(f"Review record for {eid!r}, which is not in the trace")
            continue
        refs = {x.get("ref"): x for x in r.get("refs", []) or []}
        for ref in trace_el[eid].get("cd_refs", []) or []:
            x = refs.get(ref)
            if x is None:
                gaps.append(f"{eid}: governing reference {ref!r} is not accounted for")
            elif x.get("status") == TODO:
                gaps.append(f"{eid}: {ref!r} is still todo")
            elif x.get("status") not in REF_STATUS:
                gaps.append(f"{eid}: {ref!r} status must be read or unavailable")
            elif x.get("status") == "unavailable" and not x.get("note"):
                gaps.append(f"{eid}: {ref!r} is unavailable but says nothing about why")
        for fid in r.get("findings", []) or []:
            if fid not in fids:
                gaps.append(f"{eid}: finding {fid} does not exist")
        for u in r.get("unverifiable", []) or []:
            if not (u.get("what") and u.get("missing")):
                gaps.append(f"{eid}: unverifiable items need what and missing")
    for eid in reviewed:
        if eid not in rec:
            gaps.append(f"Element {eid} was submitted but has no review record")

    # ── Package questions and reconciliations
    if package is None:
        gaps.append("Missing package_review.json (Step 6)")
        package = []
    seen_pk = set()
    for row in package:
        item, status = row.get("item"), row.get("status")
        seen_pk.add(item)
        if status == TODO:
            gaps.append(f"Package {item!r} is still todo")
        elif status not in PACKAGE_STATUS:
            gaps.append(f"Package {item!r}: status must be one of {sorted(PACKAGE_STATUS)}")
        elif status in ("na", "unverifiable") and not row.get("note"):
            gaps.append(f"Package {item!r}: {status} needs a note")
        elif status == "finding" and row.get("finding") not in fids:
            gaps.append(f"Package {item!r}: finding {row.get('finding')!r} does not exist")
    for item in PACKAGE_ITEMS:
        if item not in seen_pk:
            gaps.append(f"Package question {item} has no row")

    # ── Findings: both sources, an action, a real element and file
    for fid, f in fids.items():
        where = f"Finding {fid}"
        for field, allowed in (("severity", SEVERITIES), ("owner", OWNERS), ("kind", KINDS), ("grade", GRADES)):
            if f.get(field) not in allowed:
                gaps.append(f"{where}: {field} must be one of {sorted(allowed)}")
        if f.get("element") != "package" and f.get("element") not in trace_el:
            gaps.append(f"{where}: element {f.get('element')!r} is not in the trace (or use 'package')")
        if not (f.get("requirement") or {}).get("source"):
            gaps.append(f"{where}: requirement.source is required")
        if not f.get("action"):
            gaps.append(f"{where}: action is required")
        sp = f.get("submittal") or {}
        if f.get("kind") not in ("absence", "completeness"):
            if not isinstance(sp.get("page"), int):
                gaps.append(f"{where}: submittal file and page are required")
        if sp and isinstance(sp.get("file"), int) and sp["file"] >= len(files):
            gaps.append(f"{where}: submittal file index {sp['file']} names no file in state.yaml")
        if f.get("owner") == "design_team" and f.get("rfi_candidate") is None:
            notes.append(f"{where}: design-team finding without rfi_candidate set")

    # ── Compliance: questions stay open unless code-researcher answered them
    if compliance is None:
        gaps.append("Missing compliance.json (Step 7); write [] if the scope raises no code or authority question")
        compliance = []
    root = project_root(d)
    for i, row in enumerate(compliance, 1):
        q = str(row.get("question") or "").strip()
        where = f"Compliance question {i}"
        if len(q.split()) < 8 or not q.endswith("?"):
            gaps.append(f"{where}: write the full question, ending with '?', not a topic name")
        for eid in row.get("affects", []) or []:
            if eid != "package" and eid not in trace_el:
                gaps.append(f"{where}: affects {eid!r}, which is not in the trace")
        if row.get("severity") not in SEVERITIES:
            gaps.append(f"{where}: severity must be one of {sorted(SEVERITIES)}")
        status = row.get("status")
        if status == "open":
            if not row.get("research"):
                gaps.append(f"{where}: open questions need the research command")
        elif status == "researched":
            src = row.get("source") or ""
            if not src or not (root / src).exists():
                gaps.append(f"{where}: researched questions need source = an existing code-researcher topic file "
                            f"(got {src!r}); never answered from memory")
            if row.get("result") not in ("consistent", "finding"):
                gaps.append(f"{where}: result must be consistent or finding")
            if row.get("result") == "finding" and row.get("finding") not in fids:
                gaps.append(f"{where}: finding {row.get('finding')!r} does not exist")
        else:
            gaps.append(f"{where}: status must be open or researched")
    asked = {q for r in records for q in (r.get("questions") or [])}
    if asked and not compliance:
        gaps.append(f"Reviewers raised {len(asked)} code or authority question(s) but compliance.json is empty")

    # ── Routing: every coordination finding goes to a trade, with a gate and a need-by
    if routing is None:
        gaps.append("Missing routing.json (Step 7)")
        routing = []
    gates = milestone_ids()
    routed = set()
    for i, row in enumerate(routing, 1):
        where = f"Routing row {i} ({row.get('trade') or 'no trade'})"
        if not (row.get("trade") and row.get("ask")):
            gaps.append(f"{where}: trade and ask are required")
        if row.get("gate") not in gates:
            gaps.append(f"{where}: gate {row.get('gate')!r} is not in milestones.yaml")
        need = str(row.get("need_by") or "")
        if not (DATE.match(need) or need == "no schedule"):
            gaps.append(f"{where}: need_by must be a date from the schedule (YYYY-MM-DD) or 'no schedule'")
        if DATE.match(need) and not row.get("schedule_activity"):
            gaps.append(f"{where}: a need_by date needs the schedule_activity it came from")
        if need == "no schedule" and state.get("schedule"):
            gaps.append(f"{where}: the project has a schedule ({state['schedule']}); read the date from it")
        for fid in row.get("findings", []) or []:
            if fid not in fids:
                gaps.append(f"{where}: finding {fid} does not exist")
            routed.add(fid)
    for fid, f in fids.items():
        if f.get("kind") == "coordination" and fid not in routed:
            gaps.append(f"Coordination finding {fid} is not routed (add it to a routing row's findings)")

    # ── Resubmittal: every prior finding accounted for
    prior_id = state.get("prior_review")
    if prior_id:
        prior_dir = d.parent / str(prior_id)
        if not prior_dir.exists():
            gaps.append(f"Prior review directory {prior_dir} not found")
            prior_findings = set()
        else:
            prior_findings = {f.get("id") for f in load_batches(prior_dir, "findings")}
        accounted = {}
        for row in load_json(d / "prior.json", []):
            accounted[row.get("prior_finding")] = row
            if row.get("status") not in PRIOR_STATUS:
                gaps.append(f"Prior {row.get('prior_finding')}: status must be one of {sorted(PRIOR_STATUS)}")
            if row.get("status") in ("open", "partially_closed") and row.get("finding") not in fids:
                gaps.append(f"Prior {row.get('prior_finding')}: still open, so it needs a new finding id")
        for pf in sorted(prior_findings):
            if pf not in accounted:
                gaps.append(f"Prior finding {pf} is not accounted for in prior.json")

    refs_total = sum(len(trace_el[e].get("cd_refs", []) or []) for e in reviewed if e in trace_el)
    refs_read = sum(1 for r in rec.values() for x in r.get("refs", []) or [] if x.get("status") == "read")
    refs_unavailable = sum(1 for r in rec.values() for x in r.get("refs", []) or [] if x.get("status") == "unavailable")
    unverifiable = [(r.get("element"), u) for r in rec.values() for u in r.get("unverifiable", []) or []]
    unverifiable += [("package", {"what": row.get("item"), "missing": row.get("note")})
                     for row in package if row.get("status") == "unverifiable"]
    stats = {
        "elements_in_trace": len(trace_el),
        "elements_reviewed": sum(1 for e in reviewed if e in rec),
        "elements_submitted": len(reviewed),
        "elements_missing": len(missing),
        "refs_governing": refs_total,
        "refs_read": refs_read,
        "refs_unavailable": refs_unavailable,
        "unverifiable": len(unverifiable),
        "findings": len(fids),
        "open_questions": sum(1 for r in compliance if r.get("status") == "open"),
        "researched_questions": sum(1 for r in compliance if r.get("status") == "researched"),
        "trades_routed": len(routing),
    }
    return {"ok": not gaps, "gaps": gaps, "notes": notes, "stats": stats, "unverifiable": unverifiable}


def scaffold(review_dir, batch, elements, package):
    """Write review_{batch}.json (element records) or package_review.json with todo entries."""
    d = Path(review_dir)
    trace = load_json(d / "trace.json", None)
    if trace is None:
        raise SystemExit("trace.json is missing; trace the contract documents first (Step 2)")
    if package:
        out = d / "package_review.json"
        if out.exists():
            raise SystemExit(f"{out.name} already exists; fill it in or delete it first")
        rows = [{"item": item, "status": TODO, "note": ""} for item in PACKAGE_ITEMS]
        out.write_text(json.dumps(rows, indent=1), encoding="utf-8")
        print(f"Wrote {out.name}: {len(rows)} package questions as todo. Add a row for each reconciliation you perform.")
    if elements:
        out = d / f"review_{batch}.json"
        if out.exists():
            raise SystemExit(f"{out.name} already exists; fill it in or delete it first")
        by_id = {e.get("id"): e for e in trace.get("elements", [])}
        done = {r.get("element") for r in load_batches(d, "review")}
        unknown = [e for e in elements if e not in by_id]
        if unknown:
            raise SystemExit(f"Not in trace.json: {', '.join(unknown)}")
        inv = {e.get("id"): e for e in (load_json(d / "inventory.json", {}) or {}).get("elements", [])}
        recs = [{"element": eid,
                 "refs": [{"ref": r, "status": TODO} for r in by_id[eid].get("cd_refs", []) or []],
                 "pages": (inv.get(eid) or {}).get("pages", []),
                 "findings": [], "unverifiable": [], "questions": []}
                for eid in elements if eid not in done]
        out.write_text(json.dumps(recs, indent=1, ensure_ascii=False), encoding="utf-8")
        n_refs = sum(len(r["refs"]) for r in recs)
        print(f"Wrote {out.name}: {len(recs)} element records, {n_refs} governing references as todo. "
              f"Mark each read or unavailable (with a note).")


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review-dir", required=True)
    ap.add_argument("--json", help="Also write the report as JSON")
    ap.add_argument("--scaffold", metavar="NN", help="Write review_NN.json records (with --elements) or package_review.json (with --package)")
    ap.add_argument("--elements", default="", help="With --scaffold: comma-separated element ids")
    ap.add_argument("--package", action="store_true", help="With --scaffold: the package questions")
    args = ap.parse_args()
    if args.scaffold:
        elements = [e.strip() for e in args.elements.split(",") if e.strip()]
        if not elements and not args.package:
            ap.error("--scaffold needs --elements, --package or both")
        scaffold(args.review_dir, args.scaffold, elements, args.package)
        return 0
    report = check(args.review_dir)
    s = report["stats"]
    if s:
        print(f"Elements: {s['elements_reviewed']} of {s['elements_submitted']} submitted reviewed, "
              f"{s['elements_missing']} missing, {s['elements_in_trace']} in the contract documents · "
              f"References: {s['refs_read']} read, {s['refs_unavailable']} unavailable of {s['refs_governing']} · "
              f"{s['findings']} findings · {s['unverifiable']} unverifiable · "
              f"{s['open_questions']} open and {s['researched_questions']} researched code questions · "
              f"{s['trades_routed']} trades routed")
    for g in report["gaps"]:
        print(f"GAP   {g}")
    for n in report["notes"]:
        print(f"NOTE  {n}")
    print("PASS — review complete" if report["ok"] else f"FAIL — {len(report['gaps'])} gaps")
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
