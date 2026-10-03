#!/usr/bin/env python3
"""Resolve and validate the CSI knowledge layer in reference/csi/.

Compile one section's knowledge (cascade + overlays + interfaces + project bindings):
    csi_knowledge.py resolve --section "12 35 53" [--facility healthcare.hospital]
                             [--project <project_root>] [--format yaml|md] [--output <file>]

Check every profile, overlay and interface file against the schema and merge rules:
    csi_knowledge.py validate [--strict]

Schema and merge rules: reference/csi/SCHEMA.md
"""

import argparse
import fnmatch
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared import safe_output_path  # noqa: E402

SCHEMA_VERSION = 1
PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_KB = PLUGIN_ROOT / "reference" / "csi"

KINDS = {"global", "division", "section", "overlay", "interfaces"}
STATUS_ORDER = ["draft", "pe_reviewed", "field_validated"]
SEVERITIES = ["low", "medium", "high", "critical"]
CHECK_KINDS = ["completeness", "conformance", "coordination", "constructability", "absence"]
OWNERS = {"gc", "subcontractor", "design_team", "owner"}
REVIEW_MODES = {"per_element", "package"}
FIELD_TYPES = {"number", "string", "boolean", "enum", "list"}
FIELD_PER = {"element", "item", "package"}
FM_SOURCES = {"field_experience", "industry_practice", "project_incident"}
SUBMITTAL_TYPES = {
    "Shop Drawings", "Product Data", "Samples", "Design Data", "Test Reports", "Certificates",
    "Delegated Design", "Manufacturer's Instructions", "Manufacturer's Field Reports",
    "Qualification Statements", "Warranty", "O&M Data", "LEED Submittals", "Record Documents",
    "Schedule",
}
TRACE_TERMS = {
    "spec.part1", "spec.part1_submittals", "spec.part2", "spec.part2_manufacturers", "spec.part3",
    "drawings.plans", "drawings.interior_elevations", "drawings.details", "drawings.material_legend",
    "drawings.plumbing", "drawings.electrical", "drawings.mechanical", "drawings.lab_gas",
    "drawings.structural", "drawings.revision_blocks", "schedule.casework",
    "schedule.casework_hardware", "schedule.finish", "schedule.equipment",
    "schedule.plumbing_fixture", "schedule.master", "register.submittal_log", "register.rfi_log",
    "register.asi_bulletin_log", "register.substitutions",
}
SOURCE_FAMILIES = {
    "accessibility", "building_code", "building_code_seismic", "fire_code",
    "health_facility_licensing", "fgi_guidelines", "food_code", "pharmacy",
    "occupational_safety", "environmental", "energy",
}
GATE_MILESTONES = {
    "procurement_release", "underslab_rough_in", "slab_pour", "in_wall_rough_in",
    "wall_close_in", "above_ceiling_close_in", "equipment_set", "final_connection",
}
KEYED_LISTS = ["submittals", "review_checks", "failure_modes", "standards",
               "regulatory_hooks", "extract_fields"]
OVERLAY_LISTS = ["review_checks", "failure_modes", "regulatory_hooks"]
REQUIRED_ITEM_FIELDS = {
    "submittals": ["id", "type"],
    "review_checks": ["id", "kind", "check", "severity", "owner"],
    "failure_modes": ["id", "what_happens", "consequence"],
    "standards": ["id", "name"],
    "regulatory_hooks": ["id", "topic", "question", "severity"],
    "extract_fields": ["id", "label", "type"],
}
CONTROL_KEYS = {"override", "merge", "sections"}

SECTION_RE = re.compile(r"^(\d{2})[\s\-_.]?(\d{2})[\s\-_.]?(\d{2})(?:\.(\d{2}))?$")


class ResolveError(Exception):
    """A merge-rule violation: the knowledge layer is inconsistent."""


# ── Section numbers ─────────────────────────────────────────────

def normalize(raw):
    """'123553' / '12-35-53' / '12 35 53.13' / '12' -> canonical id, or None."""
    s = str(raw).strip()
    if re.fullmatch(r"\d{2}", s):
        return s
    m = SECTION_RE.match(s)
    if not m:
        return None
    dd, ab, cc, ee = m.groups()
    if ab == "00" and cc == "00" and not ee:
        return dd
    return f"{dd} {ab} {cc}" + (f".{ee}" if ee else "")


def lineage(sid):
    """Ancestors general -> specific, starting with 'global'."""
    if len(sid) == 2:
        return ["global", sid]
    base, _, ee = sid.partition(".")
    dd, ab, cc = base.split(" ")
    chain = ["global", dd]
    if ab[0] != "0":
        chain.append(f"{dd} {ab[0]}0 00")
    if ab[1] != "0":
        chain.append(f"{dd} {ab} 00")
    if cc != "00":
        chain.append(f"{dd} {ab} {cc}")
    if ee:
        chain.append(sid)
    seen, out = set(), []
    for node in chain:
        if node not in seen:
            seen.add(node)
            out.append(node)
    return out


def related(a, b):
    """True if either section is an ancestor of (or equal to) the other."""
    return a in lineage(b) or b in lineage(a)


def profile_path(kb, layer_id):
    if layer_id == "global":
        return kb / "profiles" / "_global.yaml"
    if len(layer_id) == 2:
        return kb / "profiles" / layer_id / "_division.yaml"
    return kb / "profiles" / layer_id[:2] / (layer_id.replace(" ", "-") + ".yaml")


def facility_chain(facilities):
    """['healthcare.hospital'] -> ['healthcare', 'healthcare.hospital'] (deduped, ordered)."""
    out = []
    for fac in facilities:
        parts = fac.split(".")
        for i in range(1, len(parts) + 1):
            f = ".".join(parts[:i])
            if f not in out:
                out.append(f)
    return out


def facility_matches(edge_types, project_types):
    if not edge_types:
        return True
    return any(p == e or p.startswith(e + ".") for e in edge_types for p in project_types)


def status_min(a, b):
    return a if STATUS_ORDER.index(a) <= STATUS_ORDER.index(b) else b


# ── Loading ─────────────────────────────────────────────────────

_cache = {}


def load_yaml(path):
    path = Path(path)
    if path not in _cache:
        with open(path, encoding="utf-8") as f:
            _cache[path] = yaml.safe_load(f) or {}
    return _cache[path]


def legacy_index(kb):
    idx = {}
    for path in sorted((kb / "profiles").rglob("*.yaml")):
        doc = load_yaml(path)
        for num in doc.get("legacy_numbers", []) or []:
            idx[str(num)] = doc.get("id")
    return idx


def resolve_section_id(kb, raw):
    sid = normalize(raw)
    if sid:
        return sid
    legacy = legacy_index(kb).get(str(raw).strip())
    if legacy:
        return legacy
    raise ResolveError(f"Not a MasterFormat number (and no profile lists it as legacy): {raw!r}")


# ── Resolve ─────────────────────────────────────────────────────

def _clean(item):
    return {k: v for k, v in item.items() if k not in CONTROL_KEYS}


def _find(compiled, item_id, lists=KEYED_LISTS):
    for name in lists:
        if item_id in compiled[name]:
            return name, compiled[name][item_id]
    return None, None


def _add_or_override(compiled, list_name, item, layer, status, chain):
    item_id = item.get("id")
    existing = compiled[list_name].get(item_id)
    if existing is None:
        if item.get("override"):
            raise ResolveError(f"{layer}: override of {list_name} '{item_id}', which is not inherited")
        new = _clean(item)
        new.update({"_from": layer, "_status": status, "_chain": chain})
        compiled[list_name][item_id] = new
        return
    if not item.get("override"):
        raise ResolveError(f"{layer}: {list_name} id '{item_id}' already defined by "
                           f"{existing['_from']} (M2 — set override: true to replace it deliberately)")
    if chain == "overlay" and existing["_chain"] == "section":
        raise ResolveError(f"{layer}: overlays cannot override section item '{item_id}' "
                           f"(M5 — use escalate to raise severity)")
    if item.get("merge", "patch") == "replace":
        new = _clean(item)
    else:
        new = {k: v for k, v in existing.items() if not k.startswith("_")}
        new.update(_clean(item))
    new.update({
        "_from": existing["_from"],
        "_status": status_min(existing["_status"], status),
        "_chain": existing["_chain"],
        "_patched_by": existing.get("_patched_by", []) + [layer],
    })
    compiled[list_name][item_id] = new


def _pattern_hit(patterns, chain):
    return any(fnmatch.fnmatchcase(node, pat) for pat in patterns for node in chain if node != "global")


def bind_hook(hook, project):
    topic = hook.get("topic")
    instruction = f'Run /construction:code-researcher with research topic "{topic}" (seed it with this hook\'s question)'
    if project is None:
        return {"status": "unbound", "instruction": instruction, "note": "No project given"}
    topic_file = project / ".construction" / "skills" / "code-researcher" / "topics" / f"{topic}.yaml"
    if not topic_file.exists():
        return {"status": "unbound", "instruction": instruction}
    data = load_yaml(topic_file)
    tf = data.get("topic_findings", data)
    findings = []
    for f in tf.get("research_findings", []) or []:
        req = " ".join(str(f.get("requirement") or "").split())
        findings.append({
            "code": f.get("code"), "section": f.get("section"),
            "edition_confirmed": bool(f.get("edition_confirmed")),
            "requirement": req[:240] + ("…" if len(req) > 240 else ""),
            "source_url": f.get("source_url") or None,
        })
    confirmed = bool(findings) and all(f["edition_confirmed"] for f in findings)
    out = {"status": "bound" if confirmed else "bound_unconfirmed",
           "source": str(topic_file.relative_to(project)), "findings": findings}
    if not confirmed:
        out["verify_with_ahj"] = True
    if tf.get("gaps_identified"):
        out["gaps_identified"] = tf["gaps_identified"]
    return out


def project_facilities(project):
    if project is None:
        return []
    ctx = project / ".construction" / "skills" / "project_context.yaml"
    if not ctx.exists():
        return []
    building = (load_yaml(ctx).get("building") or {})
    return [f for f in (building.get("facility_types") or []) if f]


def spec_text_path(project, sid):
    if project is None:
        return None
    p = project / ".construction" / "skills" / "spec_text" / (sid.replace(" ", "_").replace(".", "_") + ".txt")
    return str(p.relative_to(project)) if p.exists() else None


def resolve(kb, section, facilities=(), project=None):
    kb = Path(kb)
    project = Path(project).resolve() if project else None
    sid = resolve_section_id(kb, section)
    chain = lineage(sid)
    facilities = list(dict.fromkeys(list(facilities) + project_facilities(project)))
    warnings = []
    compiled = {name: {} for name in KEYED_LISTS}
    suppressed, escalations = [], []
    scalars = {"title": None, "scope_summary": None, "review_mode": None}
    unions = {"element_types": []}
    equivalents = []
    legacy_files, loaded, missing = [], [], []
    floor = STATUS_ORDER[-1]

    # 1-3. Section cascade
    for layer in chain:
        path = profile_path(kb, layer)
        if not path.exists():
            missing.append(layer)
            continue
        doc = load_yaml(path)
        status = doc.get("status", "draft")
        floor = status_min(floor, status)
        loaded.append({"layer": layer, "status": status})
        for key in scalars:
            if doc.get(key):
                scalars[key] = doc[key]
        for key in unions:
            for v in doc.get(key, []) or []:
                if v not in unions[key]:
                    unions[key].append(v)
        if layer == sid:
            equivalents = [normalize(v) or v for v in doc.get("equivalents", []) or []]
        if doc.get("legacy_scope_file"):
            legacy_files.append(doc["legacy_scope_file"])
        for s in doc.get("suppress", []) or []:
            sup_id = s.get("id")
            if not s.get("reason"):
                raise ResolveError(f"{layer}: suppress of '{sup_id}' has no reason (M4)")
            list_name, item = _find(compiled, sup_id)
            if item is None:
                raise ResolveError(f"{layer}: suppress of '{sup_id}', which is not inherited")
            del compiled[list_name][sup_id]
            suppressed.append({"id": sup_id, "list": list_name, "defined_by": item["_from"],
                               "suppressed_by": layer, "reason": s["reason"]})
        for list_name in KEYED_LISTS:
            for item in doc.get(list_name, []) or []:
                _add_or_override(compiled, list_name, item, layer, status, "section")

    if sid not in [entry["layer"] for entry in loaded]:
        warnings.append(f"No profile for {sid}; compiled from ancestors only")
    for layer in missing:
        if layer == "global" or len(layer) == 2:
            warnings.append(f"Missing {'global rules' if layer == 'global' else 'division baseline ' + layer}")

    # 4. Overlays
    overlays_loaded, overlays_missing = [], []
    for ov in facility_chain(facilities):
        path = kb / "overlays" / f"{ov}.yaml"
        if not path.exists():
            overlays_missing.append(ov)
            continue
        doc = load_yaml(path)
        status = doc.get("status", "draft")
        layer = f"overlay:{ov}"
        if doc.get("suppress"):
            raise ResolveError(f"{layer}: overlays cannot suppress (M5)")
        default_sections = doc.get("sections", []) or []
        applied = 0
        for list_name in OVERLAY_LISTS:
            for item in doc.get(list_name, []) or []:
                if _pattern_hit(item.get("sections", default_sections), chain):
                    _add_or_override(compiled, list_name, item, layer, status, "overlay")
                    applied += 1
        for esc in doc.get("escalate", []) or []:
            if esc.get("sections") and not _pattern_hit(esc["sections"], chain):
                continue
            list_name, item = _find(compiled, esc.get("target"), ["review_checks", "regulatory_hooks"])
            if item is None:
                continue
            old, new = item.get("severity", "low"), esc.get("severity")
            if new not in SEVERITIES:
                raise ResolveError(f"{layer}: escalate '{esc.get('target')}' has invalid severity {new!r}")
            if SEVERITIES.index(new) > SEVERITIES.index(old):
                item["severity"] = new
                item["_escalated_by"] = layer
                escalations.append({"target": esc["target"], "from": old, "to": new,
                                    "by": layer, "reason": esc.get("reason")})
                applied += 1
        overlays_loaded.append({"overlay": ov, "status": status, "items_applied": applied})
        if applied:
            floor = status_min(floor, status)

    # 5. Interfaces
    interfaces = []
    for path in sorted((kb / "interfaces").glob("*.yaml")):
        doc = load_yaml(path)
        status = doc.get("status", "draft")
        for edge in doc.get("edges", []) or []:
            if not facility_matches(edge.get("facility_types"), facilities):
                continue
            a = [normalize(x) for x in edge.get("a", [])]
            b = [normalize(x) for x in edge.get("b", [])]
            if any(x and related(x, sid) for x in a):
                this, other = "a", "b"
            elif any(x and related(x, sid) for x in b):
                this, other = "b", "a"
            else:
                continue
            interfaces.append({
                "id": edge["id"],
                "this_trade": edge.get(f"{this}_trade"),
                "counterpart_trade": edge.get(f"{other}_trade"),
                "counterpart_sections": edge.get(other, []),
                "send_them": edge.get(f"{this}_provides"),
                "need_from_them": edge.get(f"{other}_provides"),
                "responsibility": edge.get("responsibility", []),
                "gate": edge.get("gate"),
                "severity": edge.get("severity"),
                "failure": edge.get("failure"),
                "_from": f"interfaces:{doc.get('id')}",
                "_status": status,
            })
            floor = status_min(floor, status)

    # Failure modes must be catchable by a check in this compiled context
    for fm in compiled["failure_modes"].values():
        for cid in fm.get("caught_by", []) or []:
            if cid not in compiled["review_checks"]:
                warnings.append(f"Failure mode {fm['id']} is caught by '{cid}', "
                                f"which is not a check for {sid} — add a check or fix caught_by")

    # 6. Project bindings (not merged)
    hooks = []
    for hook in compiled["regulatory_hooks"].values():
        hook = dict(hook)
        hook["binding"] = bind_hook(hook, project)
        hooks.append(hook)
    project_info = None
    if project is not None:
        jur_file = project / ".construction" / "skills" / "code-researcher" / "jurisdiction.yaml"
        jur = None
        if jur_file.exists():
            j = load_yaml(jur_file)
            j = j.get("jurisdiction", j)
            jur = {"state": j.get("state"), "jurisdiction": j.get("jurisdiction"),
                   "confidence": j.get("confidence")}
        spec_hits = {s: spec_text_path(project, s) for s in [sid] + equivalents}
        spec_hits = {k: v for k, v in spec_hits.items() if v}
        project_info = {"spec_text": spec_hits or None, "jurisdiction": jur}
        if sid not in spec_hits and spec_hits:
            warnings.append(f"Project spec text found for {', '.join(spec_hits)} but not {sid} — "
                            f"this scope may be specified there; resolve that section too")

    drafts = [e["layer"] for e in loaded if e["status"] == "draft"]
    if drafts:
        warnings.append(f"Draft knowledge in use ({', '.join(drafts)}) — not yet PE-reviewed")

    return {
        "query": {"section": sid, "title": scalars["title"], "facility_types": facilities,
                  "project": str(project) if project else None},
        "note": ("Knowledge, not requirements: each check names where to look (trace_to). "
                 "The project documents govern; surface conflicts, never resolve them silently."),
        "lineage": chain,
        "coverage": {"loaded": loaded, "missing": missing, "overlays_loaded": overlays_loaded,
                     "overlays_missing": overlays_missing, "legacy_scope_files": legacy_files},
        "confidence_floor": floor,
        "equivalents": equivalents,
        "scope_summary": " ".join((scalars["scope_summary"] or "").split()) or None,
        "review_mode": scalars["review_mode"] or "package",
        "element_types": unions["element_types"],
        "submittals": list(compiled["submittals"].values()),
        "review_checks": list(compiled["review_checks"].values()),
        "failure_modes": list(compiled["failure_modes"].values()),
        "standards": list(compiled["standards"].values()),
        "regulatory_hooks": hooks,
        "extract_fields": list(compiled["extract_fields"].values()),
        "interfaces": interfaces,
        "suppressed": suppressed,
        "escalations": escalations,
        "project": project_info,
        "warnings": warnings,
    }


# ── Markdown rendering ──────────────────────────────────────────

def _txt(value):
    return " ".join(str(value or "").split())


def _sev_key(item):
    return -SEVERITIES.index(item.get("severity", "low")) if item.get("severity") in SEVERITIES else 0


def to_markdown(ctx):
    q, cov = ctx["query"], ctx["coverage"]
    loaded = {e["layer"] for e in cov["loaded"]}
    chain = " → ".join(n if n in loaded else f"[{n} missing]" for n in ctx["lineage"])
    out = [f"# Compiled knowledge — {q['section']} {q['title'] or ''}".rstrip(), ""]
    out.append(f"Facility types: {', '.join(q['facility_types']) or 'none'} · "
               f"Confidence floor: **{ctx['confidence_floor']}** · Review mode: {ctx['review_mode']}")
    out.append(f"Lineage: {chain}")
    ovs = [o["overlay"] for o in cov["overlays_loaded"]]
    if ovs or cov["overlays_missing"]:
        out.append(f"Overlays: {', '.join(ovs) or 'none'}"
                   + (f" (no file: {', '.join(cov['overlays_missing'])})" if cov["overlays_missing"] else ""))
    if ctx["equivalents"]:
        out.append(f"Also specified as: {', '.join(ctx['equivalents'])}")
    if cov["legacy_scope_files"]:
        out.append(f"Legacy scope file: {', '.join(cov['legacy_scope_files'])}")
    out += ["", f"> {ctx['note']}", ""]
    if ctx["scope_summary"]:
        out += ["## Scope", ctx["scope_summary"], ""]

    checks = ctx["review_checks"]
    out.append(f"## Review checks ({len(checks)})")
    for kind in CHECK_KINDS:
        group = sorted([c for c in checks if c.get("kind") == kind], key=_sev_key)
        if not group:
            continue
        out.append(f"### {kind}")
        for c in group:
            types = f" · Types: {', '.join(c['submittal_types'])}" if c.get("submittal_types") else ""
            esc = " (escalated)" if c.get("_escalated_by") else ""
            out.append(f"- **[{c.get('severity')}{esc}] {c['id']}** — {_txt(c.get('check'))}  ")
            out.append(f"  Trace: {', '.join(c.get('trace_to', []))} · Owner: {c.get('owner')}{types} · _{c['_from']}_")
    out.append("")

    hooks = sorted(ctx["regulatory_hooks"], key=_sev_key)
    out.append(f"## Compliance — regulatory hooks ({len(hooks)})")
    for h in hooks:
        b = h["binding"]
        out.append(f"- **[{h.get('severity')}] {h['id']}** (`{h.get('topic')}`) — {_txt(h.get('question'))}  ")
        if b["status"] == "unbound":
            out.append(f"  **Unbound** → {b['instruction']}")
        else:
            flag = " — **verify with AHJ**" if b.get("verify_with_ahj") else ""
            cites = "; ".join(f"{f['code']} {f['section'] or ''}".strip() for f in b["findings"]) or "no findings recorded"
            out.append(f"  **{b['status']}**{flag}: {cites} ({b['source']})")
    out.append("")

    ifs = sorted(ctx["interfaces"], key=_sev_key)
    out.append(f"## Coordination routing ({len(ifs)})")
    for e in ifs:
        gate = e.get("gate") or {}
        gate_txt = f" · Gate: {gate.get('milestone')}" + (f" — {gate['note']}" if gate.get("note") else "") if gate else ""
        out.append(f"- **[{e.get('severity')}] {e['id']}** → {e['counterpart_trade']} "
                   f"({', '.join(e['counterpart_sections'])}){gate_txt}")
        out.append(f"  - Send them: {_txt(e.get('send_them'))}")
        out.append(f"  - Need from them: {_txt(e.get('need_from_them'))}")
        for r in e.get("responsibility") or []:
            split = " / ".join(f"{k} {v}" for k, v in (r.get("typical") or {}).items())
            out.append(f"  - Confirm who: {r.get('item')} — typical {split}")
        if e.get("failure"):
            out.append(f"  - If missed: {_txt(e['failure'])}")
    out.append("")

    out.append(f"## Failure modes to watch ({len(ctx['failure_modes'])})")
    for fm in ctx["failure_modes"]:
        caught = ", ".join(fm.get("caught_by", []) or []) or "no check"
        out.append(f"- **{fm['id']}** — {_txt(fm.get('what_happens'))} → {_txt(fm.get('consequence'))} "
                   f"(caught by {caught}; {fm.get('source', 'n/a')})")
    out.append("")

    if ctx["submittals"]:
        out.append("## Expected submittal contents")
        for s in ctx["submittals"]:
            out.append(f"- **{s.get('type')}**")
            for line in s.get("must_show", []) or []:
                out.append(f"  - {_txt(line)}")
        out.append("")
    if ctx["extract_fields"]:
        out.append("## Extract for reconciliation")
        for x in ctx["extract_fields"]:
            unit = f", {x['unit']}" if x.get("unit") else ""
            out.append(f"- {x['id']} — {x.get('label')} ({x.get('type')}{unit}, per {x.get('per', 'element')}) "
                       f"→ {', '.join(x.get('reconcile_against', []) or [])}")
        out.append("")
    if ctx["standards"]:
        out.append("## Standards to verify against")
        for s in ctx["standards"]:
            note = f" — {_txt(s['note'])}" if s.get("note") else ""
            out.append(f"- {s.get('name')}: {_txt(s.get('title'))}{note}")
        out.append("")
    if ctx["escalations"]:
        out.append("## Escalations")
        for e in ctx["escalations"]:
            out.append(f"- {e['target']}: {e['from']} → {e['to']} by {e['by']} — {_txt(e.get('reason'))}")
        out.append("")
    if ctx["suppressed"]:
        out.append("## Suppressed")
        for s in ctx["suppressed"]:
            out.append(f"- {s['id']} (from {s['defined_by']}) by {s['suppressed_by']} — {_txt(s['reason'])}")
        out.append("")
    if ctx["project"]:
        out.append("## Project")
        spec = ctx["project"]["spec_text"]
        jur = ctx["project"]["jurisdiction"]
        out.append("- Spec text: " + ("; ".join(f"{k} → {v}" for k, v in spec.items()) if spec else "not extracted"))
        out.append("- Jurisdiction: " + (", ".join(f"{k} {v}" for k, v in jur.items() if v) if jur
                                         else "not researched (run /construction:code-researcher)"))
        out.append("")
    if ctx["warnings"]:
        out.append("## Warnings")
        out += [f"- {w}" for w in ctx["warnings"]]
    return "\n".join(out).rstrip() + "\n"


# ── Validate ────────────────────────────────────────────────────

def _expected_id(kb, path):
    rel = path.relative_to(kb)
    if rel.parts[0] == "profiles":
        if path.name == "_global.yaml":
            return "global", "global"
        if path.name == "_division.yaml":
            return rel.parts[1], "division"
        return path.stem.replace("-", " "), "section"
    if rel.parts[0] == "overlays":
        return path.stem, "overlay"
    return path.stem, "interfaces"


def validate(kb):
    kb = Path(kb)
    errors, warnings = [], []
    files = sorted(list((kb / "profiles").rglob("*.yaml")) + list((kb / "overlays").glob("*.yaml"))
                   + list((kb / "interfaces").glob("*.yaml")))
    all_check_ids, escalate_targets, section_ids, overlay_ids, drafts = set(), [], [], [], 0

    def err(path, msg):
        errors.append(f"{path.relative_to(kb)}: {msg}")

    def warn(path, msg):
        warnings.append(f"{path.relative_to(kb)}: {msg}")

    for path in files:
        try:
            doc = load_yaml(path)
        except yaml.YAMLError as e:
            err(path, f"YAML parse error: {e}")
            continue
        exp_id, exp_kind = _expected_id(kb, path)
        if doc.get("schema_version") != SCHEMA_VERSION:
            err(path, f"schema_version must be {SCHEMA_VERSION}")
        if doc.get("kind") != exp_kind:
            err(path, f"kind is {doc.get('kind')!r}; this location requires {exp_kind!r}")
        if str(doc.get("id")) != exp_id:
            err(path, f"id {doc.get('id')!r} does not match file name (expected {exp_id!r})")
        for field in ("title", "status"):
            if not doc.get(field):
                err(path, f"missing {field}")
        if doc.get("status") and doc["status"] not in STATUS_ORDER:
            err(path, f"status must be one of {STATUS_ORDER}")
        if doc.get("status") == "draft":
            drafts += 1
        kind = doc.get("kind")

        if kind == "section" and normalize(exp_id) != exp_id:
            err(path, f"file name is not a canonical section number: {exp_id!r}")
        if kind in ("global", "division", "section"):
            section_ids.append(str(doc.get("id")))
        if kind == "overlay":
            overlay_ids.append(str(doc.get("id")))
            if doc.get("facility_type") != doc.get("id"):
                err(path, "facility_type must equal id")
            if doc.get("suppress"):
                err(path, "overlays cannot suppress (M5)")
            for pat in doc.get("sections", []) or []:
                if not re.fullmatch(r"[\d\s*?]+", str(pat)):
                    err(path, f"bad sections pattern {pat!r}")
            for esc in doc.get("escalate", []) or []:
                if esc.get("severity") not in SEVERITIES:
                    err(path, f"escalate {esc.get('target')!r}: invalid severity")
                if not esc.get("reason"):
                    err(path, f"escalate {esc.get('target')!r}: reason required")
                escalate_targets.append((path, esc.get("target")))
        if kind in ("global", "division", "section"):
            if doc.get("review_mode") and doc["review_mode"] not in REVIEW_MODES:
                err(path, f"review_mode must be one of {sorted(REVIEW_MODES)}")
            for v in doc.get("equivalents", []) or []:
                if not normalize(v):
                    err(path, f"equivalents: bad section number {v!r}")
            for s in doc.get("suppress", []) or []:
                if not s.get("id") or not s.get("reason"):
                    err(path, "suppress entries need id and reason (M4)")
            if doc.get("legacy_scope_file") and not (PLUGIN_ROOT / doc["legacy_scope_file"]).exists():
                warn(path, f"legacy_scope_file not found: {doc['legacy_scope_file']}")

        lists = KEYED_LISTS if kind in ("global", "division", "section") else (
            OVERLAY_LISTS if kind == "overlay" else [])
        for list_name in lists:
            seen = set()
            for item in doc.get(list_name, []) or []:
                item_id = item.get("id")
                if not item_id:
                    err(path, f"{list_name}: item without id")
                    continue
                if item_id in seen:
                    err(path, f"{list_name}: duplicate id {item_id!r}")
                seen.add(item_id)
                if not item.get("override"):
                    for field in REQUIRED_ITEM_FIELDS[list_name]:
                        if field not in item:
                            err(path, f"{list_name} {item_id}: missing {field}")
                if item.get("merge") not in (None, "patch", "replace"):
                    err(path, f"{list_name} {item_id}: merge must be patch or replace")
                if "severity" in item and item["severity"] not in SEVERITIES:
                    err(path, f"{list_name} {item_id}: invalid severity {item['severity']!r}")
                if list_name == "review_checks":
                    all_check_ids.add(item_id)
                    if "kind" in item and item["kind"] not in CHECK_KINDS:
                        err(path, f"check {item_id}: kind must be one of {CHECK_KINDS}")
                    if "owner" in item and item["owner"] not in OWNERS:
                        err(path, f"check {item_id}: owner must be one of {sorted(OWNERS)}")
                    for t in item.get("submittal_types", []) or []:
                        if t not in SUBMITTAL_TYPES:
                            warn(path, f"check {item_id}: unknown submittal type {t!r}")
                for t in item.get("trace_to", []) or []:
                    if t not in TRACE_TERMS:
                        warn(path, f"{item_id}: unknown trace_to term {t!r} (add it to SCHEMA.md §4.1)")
                for t in item.get("reconcile_against", []) or []:
                    if t not in TRACE_TERMS:
                        warn(path, f"{item_id}: unknown reconcile_against term {t!r}")
                if list_name == "submittals" and item.get("type") not in SUBMITTAL_TYPES:
                    warn(path, f"submittal {item_id}: unknown type {item.get('type')!r}")
                if list_name == "regulatory_hooks":
                    if "topic" in item and not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", str(item["topic"])):
                        err(path, f"hook {item_id}: topic must be a lowercase slug")
                    for fam in item.get("source_families", []) or []:
                        if fam not in SOURCE_FAMILIES:
                            warn(path, f"hook {item_id}: unknown source family {fam!r}")
                if list_name == "failure_modes" and item.get("source") and item["source"] not in FM_SOURCES:
                    err(path, f"failure mode {item_id}: source must be one of {sorted(FM_SOURCES)}")
                if list_name == "extract_fields":
                    if "type" in item and item["type"] not in FIELD_TYPES:
                        err(path, f"field {item_id}: type must be one of {sorted(FIELD_TYPES)}")
                    if item.get("per") and item["per"] not in FIELD_PER:
                        err(path, f"field {item_id}: per must be one of {sorted(FIELD_PER)}")

        if kind == "interfaces":
            seen = set()
            for edge in doc.get("edges", []) or []:
                eid = edge.get("id")
                if not eid or eid in seen:
                    err(path, f"edge id missing or duplicate: {eid!r}")
                seen.add(eid)
                for field in ("a", "b", "a_trade", "b_trade", "a_provides", "b_provides", "severity"):
                    if not edge.get(field):
                        err(path, f"edge {eid}: missing {field}")
                for side in ("a", "b"):
                    for v in edge.get(side, []) or []:
                        if not normalize(v):
                            err(path, f"edge {eid}: bad section number {v!r} in {side}")
                if edge.get("severity") and edge["severity"] not in SEVERITIES:
                    err(path, f"edge {eid}: invalid severity")
                gate = edge.get("gate") or {}
                if gate and gate.get("milestone") not in GATE_MILESTONES:
                    warn(path, f"edge {eid}: unknown gate milestone {gate.get('milestone')!r}")
                for r in edge.get("responsibility", []) or []:
                    extra = set((r.get("typical") or {})) - {"furnish", "install", "connect"}
                    if extra:
                        err(path, f"edge {eid}: responsibility keys must be furnish/install/connect, got {sorted(extra)}")

    for path, target in escalate_targets:
        if target not in all_check_ids and not any(
                target == h.get("id") for p in files for h in (load_yaml(p).get("regulatory_hooks") or [])):
            warn(path, f"escalate target {target!r} exists nowhere in the knowledge layer")

    # Cascade check: every profile must resolve, alone and under every overlay
    facility_sets = [[]] + [[o] for o in overlay_ids] + ([overlay_ids] if len(overlay_ids) > 1 else [])
    for sid in section_ids:
        if sid == "global":
            continue
        for facs in facility_sets:
            try:
                ctx = resolve(kb, sid, facs)
            except ResolveError as e:
                errors.append(f"resolve {sid} {facs or ''}: {e}".replace(" []", ""))
                continue
            for w in ctx["warnings"]:
                if "caught by" in w:
                    warnings.append(f"resolve {sid} {facs}: {w}")

    return errors, sorted(set(warnings)), drafts, len(files)


# ── CLI ─────────────────────────────────────────────────────────

def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # Windows consoles default to a legacy code page
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--kb", default=str(DEFAULT_KB), help="Knowledge layer root (default: reference/csi)")
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("resolve", help="Compile the knowledge for one section")
    r.add_argument("--section", required=True, help='e.g. "12 35 53", 123553, or a legacy number like 12300')
    r.add_argument("--facility", action="append", default=[], help="Facility type, repeatable (healthcare.hospital)")
    r.add_argument("--project", help="Project root: reads project_context facility types, code-researcher findings, spec text")
    r.add_argument("--format", choices=["yaml", "md"], default="yaml")
    r.add_argument("--output", help="Write to this file (versioned, never overwrites) instead of stdout")
    v = sub.add_parser("validate", help="Validate every file and merge rule")
    v.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    if args.command == "resolve":
        try:
            ctx = resolve(args.kb, args.section, args.facility, args.project)
        except ResolveError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
        text = to_markdown(ctx) if args.format == "md" else yaml.safe_dump(
            ctx, sort_keys=False, allow_unicode=True, width=100)
        if args.output:
            out = safe_output_path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
            print(f"Wrote {out}")
        else:
            sys.stdout.write(text)
        return 0

    errors, warnings, drafts, count = validate(args.kb)
    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"WARNING {w}")
    print(f"\n{count} files · {len(errors)} errors · {len(warnings)} warnings · {drafts} at draft status")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
