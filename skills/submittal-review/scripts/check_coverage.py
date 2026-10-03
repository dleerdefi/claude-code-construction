#!/usr/bin/env python3
"""Coverage gate for a submittal review.

Proves the review answered every applicable check for every element, recorded every
regulatory hook and interface, backed every finding with sources and an action, and
accounted for every prior finding on a resubmittal. Exits 1 if anything is missing.

    check_coverage.py --review-dir .construction/skills/submittal-review/<review_id> [--json report.json]

File formats: ../references/review-data.md
"""

import argparse
import glob
import json
import sys
from pathlib import Path

import yaml

SEVERITIES = {"critical", "high", "medium", "low"}
OWNERS = {"subcontractor", "gc", "design_team", "owner"}
KINDS = {"completeness", "conformance", "coordination", "constructability", "absence", "compliance"}
GRADES = {"CONFLICTING", "NOT FOUND", "OPEN"}
COVERAGE_STATUS = {"pass", "finding", "na", "unverifiable"}
HOOK_RESULTS = {"open", "consistent", "finding"}
PRIOR_STATUS = {"closed", "partially_closed", "open"}


def load_json(path, default):
    p = Path(path)
    if not p.exists():
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_batches(review_dir, prefix):
    rows = []
    for path in sorted(glob.glob(str(Path(review_dir) / f"{prefix}_*.json"))):
        data = load_json(path, [])
        if not isinstance(data, list):
            raise ValueError(f"{Path(path).name} must be a JSON array")
        rows.extend(data)
    return rows


def applies(check, types):
    wanted = check.get("submittal_types") or []
    return not wanted or not types or bool(set(wanted) & set(types))


def check(review_dir):
    d = Path(review_dir)
    gaps, notes = [], []

    state_path = d / "state.yaml"
    if not state_path.exists():
        return {"ok": False, "gaps": [f"Missing {state_path.name}"], "notes": [], "stats": {}}
    state = yaml.safe_load(state_path.read_text(encoding="utf-8")) or {}
    types = (state.get("submittal") or {}).get("types") or []

    ctx_path = d / "context.yaml"
    if not ctx_path.exists():
        return {"ok": False, "gaps": ["Missing context.yaml (Step 2)"], "notes": [], "stats": {}}
    ctx = yaml.safe_load(ctx_path.read_text(encoding="utf-8")) or {}
    checks = [c for c in ctx.get("review_checks", []) if applies(c, types)]
    element_checks = [c["id"] for c in checks if c.get("scope") == "element"]
    package_checks = [c["id"] for c in checks if c.get("scope") != "element"]
    recon_ids = [r["id"] for r in ctx.get("reconciliations", [])]
    hook_ids = [h["id"] for h in ctx.get("regulatory_hooks", [])]
    hook_binding = {h["id"]: (h.get("binding") or {}).get("status") for h in ctx.get("regulatory_hooks", [])}
    interface_ids = [e["id"] for e in ctx.get("interfaces", [])]
    known_ids = set(c["id"] for c in ctx.get("review_checks", [])) | set(recon_ids) | set(hook_ids)

    trace = load_json(d / "trace.json", None)
    inventory = load_json(d / "inventory.json", None)
    if trace is None:
        gaps.append("Missing trace.json (Step 4)")
        trace = {}
    if inventory is None:
        gaps.append("Missing inventory.json (Step 5)")
        inventory = {}

    try:
        findings = load_batches(d, "findings")
        coverage = load_batches(d, "coverage")
    except ValueError as e:
        return {"ok": False, "gaps": [str(e)], "notes": [], "stats": {}}
    finding_ids = {}
    for f in findings:
        fid = f.get("id")
        if not fid:
            gaps.append(f"Finding without id: {str(f)[:80]}")
            continue
        if fid in finding_ids:
            gaps.append(f"Duplicate finding id {fid}")
        finding_ids[fid] = f

    # ── Trace ↔ inventory, both ways
    trace_ids = [e.get("id") for e in trace.get("elements", [])]
    inv = {e.get("id"): e for e in inventory.get("elements", [])}
    for eid in trace_ids:
        if eid not in inv:
            gaps.append(f"Element {eid} is in the trace but not in the inventory")
    for eid in inv:
        if eid not in trace_ids:
            gaps.append(f"Inventory element {eid} is not in the trace (put submittal-only items in extra_items)")
    completeness_for = {f.get("element") for f in findings if f.get("kind") == "completeness"}
    missing = [eid for eid, e in inv.items() if e.get("status") == "missing"]
    for eid in missing:
        if eid not in completeness_for:
            gaps.append(f"Element {eid} is missing from the submittal but has no completeness finding")
    for item in inventory.get("package_items", []):
        if item.get("status") == "missing" and "package" not in completeness_for:
            gaps.append(f"Package requirement {item.get('ref')} is missing but there is no package completeness finding")
    for item in inventory.get("extra_items", []):
        if not item.get("note"):
            gaps.append(f"Extra submittal item {item.get('label')!r} needs a note (what it is, what to do)")

    # ── Coverage matrix
    rows = {}
    for r in coverage:
        key = (r.get("element"), r.get("check"))
        status = r.get("status")
        if status not in COVERAGE_STATUS:
            gaps.append(f"Coverage {key}: status must be one of {sorted(COVERAGE_STATUS)}")
        if status in ("na", "unverifiable") and not r.get("note"):
            gaps.append(f"Coverage {key}: {status} needs a note")
        if status == "finding" and r.get("finding") not in finding_ids:
            gaps.append(f"Coverage {key}: finding {r.get('finding')!r} does not exist")
        rows[key] = r
    reviewed = [eid for eid, e in inv.items() if e.get("status") in ("submitted", "partial")]
    expected = [(eid, c) for eid in reviewed for c in element_checks]
    expected += [("package", c) for c in package_checks + recon_ids]
    for key in expected:
        if key not in rows:
            gaps.append(f"No coverage row for element {key[0]} × check {key[1]}")
    covered = sum(1 for key in expected if key in rows)
    unverifiable = [k for k, r in rows.items() if r.get("status") == "unverifiable"]

    # ── Findings quality
    for fid, f in finding_ids.items():
        where = f"Finding {fid}"
        for field, allowed in (("severity", SEVERITIES), ("owner", OWNERS), ("kind", KINDS), ("grade", GRADES)):
            if f.get(field) not in allowed:
                gaps.append(f"{where}: {field} must be one of {sorted(allowed)}")
        if not (f.get("requirement") or {}).get("source"):
            gaps.append(f"{where}: requirement.source is required")
        if not f.get("action"):
            gaps.append(f"{where}: action is required")
        if f.get("kind") != "absence" and not isinstance((f.get("submittal") or {}).get("page"), int) \
                and f.get("kind") != "completeness":
            gaps.append(f"{where}: submittal file and page are required")
        cid = f.get("check", "")
        if cid not in known_ids and not str(cid).startswith("obs."):
            gaps.append(f"{where}: check {cid!r} is not in context.yaml (use obs.<slug> for observations)")
        if f.get("owner") == "design_team" and f.get("rfi_candidate") is None:
            notes.append(f"{where}: design-team finding without rfi_candidate set")

    # ── Compliance: every hook, unbound ones stay open
    compliance = load_json(d / "compliance.json", None)
    if compliance is None:
        gaps.append("Missing compliance.json (Step 8)")
        compliance = []
    seen_hooks = {}
    for row in compliance:
        hid = row.get("hook")
        seen_hooks[hid] = row
        if row.get("result") not in HOOK_RESULTS:
            gaps.append(f"Compliance {hid}: result must be one of {sorted(HOOK_RESULTS)}")
        if hook_binding.get(hid) == "unbound" and row.get("result") != "open":
            gaps.append(f"Compliance {hid}: hook is unbound (no code research), so result must be open — "
                        f"never decided from memory")
        if row.get("result") == "finding" and row.get("finding") not in finding_ids:
            gaps.append(f"Compliance {hid}: finding {row.get('finding')!r} does not exist")
    for hid in hook_ids:
        if hid not in seen_hooks:
            gaps.append(f"Regulatory hook {hid} has no compliance row")
    open_hooks = [h for h, r in seen_hooks.items() if r.get("result") == "open"]

    # ── Routing: every interface decided
    routing = load_json(d / "routing.json", None)
    if routing is None:
        gaps.append("Missing routing.json (Step 8)")
        routing = []
    seen_if = {}
    for row in routing:
        iid = row.get("interface")
        seen_if[iid] = row
        if row.get("relevant") is None or not row.get("reason"):
            gaps.append(f"Routing {iid}: relevant (true/false) and reason are required")
        if row.get("relevant") and not (row.get("trade") and row.get("ask")):
            gaps.append(f"Routing {iid}: relevant interfaces need trade and ask")
    for iid in interface_ids:
        if iid not in seen_if:
            gaps.append(f"Interface {iid} has no routing row")
    routed_findings = {fid for row in routing for fid in (row.get("findings") or [])}
    for fid, f in finding_ids.items():
        if f.get("kind") == "coordination" and fid not in routed_findings:
            gaps.append(f"Coordination finding {fid} is not routed (add it to a routing row's findings)")

    # ── Resubmittal: every prior finding accounted for
    prior_id = state.get("prior_review")
    if prior_id:
        prior_dir = d.parent / str(prior_id)
        prior_findings = {f.get("id") for f in load_batches(prior_dir, "findings")} if prior_dir.exists() else set()
        if not prior_dir.exists():
            gaps.append(f"Prior review directory {prior_dir} not found")
        prior = load_json(d / "prior.json", [])
        accounted = {}
        for row in prior:
            accounted[row.get("prior_finding")] = row
            if row.get("status") not in PRIOR_STATUS:
                gaps.append(f"Prior {row.get('prior_finding')}: status must be one of {sorted(PRIOR_STATUS)}")
            if row.get("status") in ("open", "partially_closed") and row.get("finding") not in finding_ids:
                gaps.append(f"Prior {row.get('prior_finding')}: still open, so it needs a new finding id")
        for pf in sorted(prior_findings):
            if pf not in accounted:
                gaps.append(f"Prior finding {pf} is not accounted for in prior.json")

    stats = {
        "elements_in_trace": len(trace_ids),
        "elements_reviewed": len(reviewed),
        "elements_missing": len(missing),
        "coverage_rows_expected": len(expected),
        "coverage_rows_present": covered,
        "coverage_pct": round(100 * covered / len(expected), 1) if expected else 100.0,
        "unverifiable": len(unverifiable),
        "findings": len(finding_ids),
        "open_compliance": len(open_hooks),
        "interfaces_relevant": sum(1 for r in routing if r.get("relevant")),
    }
    return {"ok": not gaps, "gaps": gaps, "notes": notes, "stats": stats}


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review-dir", required=True)
    ap.add_argument("--json", help="Also write the report as JSON")
    args = ap.parse_args()
    report = check(args.review_dir)
    s = report["stats"]
    if s:
        print(f"Elements: {s['elements_reviewed']} reviewed, {s['elements_missing']} missing of "
              f"{s['elements_in_trace']} · Coverage {s['coverage_rows_present']}/{s['coverage_rows_expected']} "
              f"({s['coverage_pct']}%) · {s['findings']} findings · {s['unverifiable']} unverifiable · "
              f"{s['open_compliance']} open compliance · {s['interfaces_relevant']} interfaces routed")
    for g in report["gaps"]:
        print(f"GAP   {g}")
    for n in report["notes"]:
        print(f"NOTE  {n}")
    print("PASS — coverage complete" if report["ok"] else f"FAIL — {len(report['gaps'])} gaps")
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
