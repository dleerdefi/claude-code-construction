#!/usr/bin/env python3
"""Resolve and validate the CSI knowledge layer in reference/csi/.

Compile one section's knowledge (cascade + overlays + interfaces + project bindings):
    csi_knowledge.py resolve --section "07 84 00" [--facility healthcare.hospital]
                             [--project <project_root>] [--only checks,hooks,interfaces]
                             [--format yaml|md] [--output <file>]

Always-on checks across the whole layer (the red-flag list, compiled from where each lives):
    csi_knowledge.py reflexes [--facility ...] [--project <root>] [--format yaml|md]

What must be verified before a covering or committing milestone (omit --id to list them):
    csi_knowledge.py milestone [--id wall_close_in] [--facility ...] [--project <root>] [--format yaml|md]

Check every file against the schema, merge rules and authoring lint:
    csi_knowledge.py validate [--strict]

Schema and merge rules: reference/csi/SCHEMA.md
"""

import argparse
import difflib
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

KINDS = {"global", "division", "section", "overlay", "interfaces", "milestones"}
STATUS_ORDER = ["draft", "pe_reviewed", "field_validated"]
SEVERITIES = ["low", "medium", "high", "critical"]
CHECK_KINDS = ["completeness", "conformance", "coordination", "constructability", "absence"]
OWNERS = {"gc", "subcontractor", "design_team", "owner"}
REVIEW_MODES = {"per_element", "package"}
FIELD_TYPES = {"number", "string", "boolean", "enum", "list"}
FIELD_PER = {"element", "item", "package"}
FM_SOURCES = {"field_experience", "industry_practice", "project_incident"}
CONTRACTOR_DESIGNED = ["typical", "sometimes", "never"]
SCOPES = {"element", "package"}
APPLIES_IF = {"contractor_designed": set(CONTRACTOR_DESIGNED) | {"unknown"},
              "review_mode": {"per_element", "package"}}
SUBMITTAL_TYPES = {
    "Shop Drawings", "Product Data", "Samples", "Design Data", "Test Reports", "Certificates",
    "Delegated Design", "Manufacturer's Instructions", "Manufacturer's Field Reports",
    "Qualification Statements", "Warranty", "O&M Data", "LEED Submittals", "Record Documents",
    "Schedule",
}
TRACE_TERMS = {
    "spec.part1", "spec.part1_submittals", "spec.part2", "spec.part2_manufacturers", "spec.part3",
    "drawings.plans", "drawings.interior_elevations", "drawings.details", "drawings.material_legend",
    "drawings.wall_sections", "drawings.exterior_elevations", "drawings.roof_plan", "drawings.rcp",
    "drawings.life_safety", "drawings.foundation", "drawings.structural", "drawings.civil",
    "drawings.plumbing", "drawings.mechanical", "drawings.electrical", "drawings.single_line",
    "drawings.fire_alarm", "drawings.lab_gas", "drawings.revision_blocks",
    "schedule.casework", "schedule.casework_hardware", "schedule.finish", "schedule.partition_type",
    "schedule.door", "schedule.door_hardware", "schedule.equipment", "schedule.plumbing_fixture",
    "schedule.mechanical_equipment", "schedule.electrical_panel", "schedule.lighting_fixture",
    "schedule.master", "report.geotechnical", "report.energy_compliance",
    "register.submittal_log", "register.rfi_log", "register.asi_bulletin_log",
    "register.substitutions", "register.special_inspections",
    "drawings.demolition", "drawings.site", "drawings.landscape", "drawings.enlarged_plans",
    "drawings.building_sections", "drawings.fire_protection", "drawings.riser_diagrams",
    "drawings.technology", "drawings.security", "drawings.foodservice", "drawings.equipment",
    "schedule.window", "schedule.signage", "schedule.toilet_accessories",
    "schedule.foodservice_equipment", "schedule.structural", "schedule.lintel",
    "report.hazmat_survey", "report.existing_conditions", "report.commissioning",
    "report.acoustical", "report.stormwater", "report.utility_requirements", "spec.division_01",
    "contract.general_conditions", "submittals.approved", "drawings.controls", "drawings.storage_racks",
    "report.radiation_shielding", "report.chemical_inventory", "report.risk_assessment",
    "report.basis_of_design", "report.wind_tunnel", "report.preservation_approval",
}
SOURCE_FAMILIES = {
    "accessibility", "building_code", "building_code_seismic", "fire_code",
    "health_facility_licensing", "fgi_guidelines", "food_code", "pharmacy",
    "occupational_safety", "environmental", "energy", "plumbing_code", "mechanical_code",
    "electrical_code", "elevator_code", "fuel_gas_code", "boiler_pressure_vessel",
    "radiation_control", "public_health", "public_works", "utility_service_rules",
    "historic_preservation", "public_funding", "federal_security_criteria", "owner_insurer_standards",
}
KEYED_LISTS = ["submittals", "review_checks", "reconciliations", "failure_modes", "standards",
               "regulatory_hooks", "extract_fields"]
OVERLAY_LISTS = ["review_checks", "reconciliations", "failure_modes", "regulatory_hooks"]
GATED_LISTS = ["review_checks", "reconciliations"]   # lists whose items may carry reflex / gate
REQUIRED_ITEM_FIELDS = {
    "submittals": ["id", "type"],
    "review_checks": ["id", "kind", "check", "severity", "owner"],
    "reconciliations": ["id", "between", "fields", "check", "severity", "owner"],
    "failure_modes": ["id", "what_happens", "consequence"],
    "standards": ["id", "name"],
    "regulatory_hooks": ["id", "topic", "question", "severity"],
    "extract_fields": ["id", "label", "type"],
}
CONTROL_KEYS = {"override", "merge", "sections"}

SLICES = {
    "checks": "review_checks", "reconciliations": "reconciliations", "hooks": "regulatory_hooks",
    "interfaces": "interfaces", "failures": "failure_modes", "failure_modes": "failure_modes",
    "submittals": "submittals", "standards": "standards", "extract": "extract_fields",
    "extract_fields": "extract_fields", "review_checks": "review_checks",
    "regulatory_hooks": "regulatory_hooks",
}
CONTENT_KEYS = ["submittals", "review_checks", "reconciliations", "failure_modes", "standards",
                "regulatory_hooks", "extract_fields", "interfaces", "suppressed", "escalations"]

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


def load_milestones(kb):
    path = Path(kb) / "milestones.yaml"
    if not path.exists():
        return []
    return load_yaml(path).get("milestones", []) or []


def project_sections(project):
    """Sections the project actually specifies, from spec-splitter's extracted text files."""
    if project is None:
        return None
    spec_dir = project / ".construction" / "skills" / "spec_text"
    if not spec_dir.is_dir():
        return None
    found = {normalize(p.stem.replace("_", " ")) for p in spec_dir.glob("*.txt")}
    found.discard(None)
    return found or None


def layer_relevant(layer_id, sections):
    """Is a profile layer (global / division / section) relevant to a set of project sections?"""
    if sections is None or layer_id == "global":
        return True
    return any(related(layer_id, s) for s in sections)


def edge_in_project(edge, sections):
    """Both trades of an interface are specified on the project (by section or a related one)."""
    def hit(side):
        return any(x and layer_relevant(x, sections) for x in (normalize(v) for v in edge.get(side, []) or []))
    return hit("a") and hit("b")


def iter_files(kb, sub, pattern="*.yaml"):
    folder = Path(kb) / sub
    if not folder.is_dir():
        return []
    return sorted(folder.rglob(pattern) if sub == "profiles" else folder.glob(pattern))


_edge_failures = {}


def edge_failure_index(kb):
    """Edge id -> [(failure mode id, what_happens)] for failure modes that name the edge.

    An edge leaves `failure` off when a profile's failure mode names it, so the consequence
    has one home. The review from the other side of the edge still needs it: resolve
    attaches it from here.
    """
    key = str(Path(kb).resolve())
    if key not in _edge_failures:
        index = {}
        for path in iter_files(kb, "profiles") + iter_files(kb, "overlays"):
            for fm in load_yaml(path).get("failure_modes") or []:
                for cid in fm.get("caught_by", []) or []:
                    if str(cid).startswith("if."):
                        index.setdefault(cid, []).append((fm.get("id"), " ".join(str(fm.get("what_happens", "")).split())))
        _edge_failures[key] = index
    return _edge_failures[key]


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


def _find_alias(kb, sid):
    """(target, alias_node) for the nearest section-level alias at or above sid.

    An ancestor's alias is followed only when its target lies outside the ancestor's
    own subtree: 06 41 00 → 12 30 00 carries 06 41 16 with it, but 31 20 00 → 31 23 00
    does not drag its other children (31 25 00) into excavation and fill.
    """
    for node in reversed(lineage(sid)):
        if node == "global" or len(node) == 2:
            break
        path = profile_path(kb, node)
        if not path.exists():
            continue
        target = load_yaml(path).get("same_as")
        if not target:
            continue
        target = normalize(target)
        if node != sid and node in lineage(target):
            return None, None
        return target, node
    return None, None


def resolve(kb, section, facilities=(), project=None):
    kb = Path(kb)
    project = Path(project).resolve() if project else None
    sid = resolve_section_id(kb, section)
    chain = lineage(sid)
    reviewed_as, alias_node = _find_alias(kb, sid)
    if reviewed_as:
        # An alias: the same scope specified under another number (06 41 00 → 12 30 00).
        # Sections under an aliased level-2 number follow it (06 41 16 under 06 41 00).
        target_chain = lineage(reviewed_as)
        tail = chain[chain.index(alias_node):]
        chain = target_chain + [n for n in tail if n not in target_chain]

    def edge_hits(x):
        if not reviewed_as:
            return related(x, sid)
        # The target's edges, plus edges naming the alias number or something under it;
        # not the edges of the alias number's own parents (03 30 00 for 03 38 00).
        return related(x, reviewed_as) or (alias_node in lineage(x) and related(x, sid))
    facilities = list(dict.fromkeys(list(facilities) + project_facilities(project)))
    warnings = []
    compiled = {name: {} for name in KEYED_LISTS}
    suppressed, escalations = [], []
    suppressed_edges = {}
    scalars = {"title": None, "scope_summary": None, "review_mode": None, "contractor_designed": None}
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
            if str(sup_id).startswith("if."):
                # An edge whose endpoint is a parent number but never applies here
                # (a misc-metals edge on 05 50 00 reaching every stair review)
                suppressed_edges[sup_id] = (layer, s["reason"])
                continue
            list_name, item = _find(compiled, sup_id)
            if item is None:
                raise ResolveError(f"{layer}: suppress of '{sup_id}', which is not inherited")
            del compiled[list_name][sup_id]
            suppressed.append({"id": sup_id, "list": list_name, "defined_by": item["_from"],
                               "suppressed_by": layer, "reason": s["reason"]})
        for list_name in KEYED_LISTS:
            for item in doc.get(list_name, []) or []:
                _add_or_override(compiled, list_name, item, layer, status, "section")

    if reviewed_as and profile_path(kb, sid).exists():
        scalars["title"] = load_yaml(profile_path(kb, sid)).get("title") or scalars["title"]
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
            if any(x and edge_hits(x) for x in a):
                this, other = "a", "b"
            elif any(x and edge_hits(x) for x in b):
                this, other = "b", "a"
            else:
                continue
            if edge["id"] in suppressed_edges:
                layer, reason = suppressed_edges.pop(edge["id"])
                suppressed.append({"id": edge["id"], "list": "interfaces", "defined_by": f"interfaces:{doc.get('id')}",
                                   "suppressed_by": layer, "reason": reason})
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
                "reflex": bool(edge.get("reflex")),
                "failure": edge.get("failure") or "; ".join(
                    text for fid, text in edge_failure_index(kb).get(edge["id"], [])
                    if fid not in compiled["failure_modes"]) or None,
                "_from": f"interfaces:{doc.get('id')}",
                "_status": status,
            })
            floor = status_min(floor, status)

    for eid, (layer, _) in suppressed_edges.items():
        raise ResolveError(f"{layer}: suppress of edge '{eid}', which does not reach this section")

    # applies_if: drop items whose condition on the compiled section facts is not met
    facts = {"contractor_designed": scalars["contractor_designed"] or "unknown",
             "review_mode": scalars["review_mode"] or "package"}
    not_applicable = []
    for list_name in KEYED_LISTS:
        for item_id, item in list(compiled[list_name].items()):
            cond = item.pop("applies_if", None)
            if cond and not all(facts.get(k) in (v if isinstance(v, list) else [v]) for k, v in cond.items()):
                del compiled[list_name][item_id]
                not_applicable.append(item_id)

    # Effective scope: is the check answered once per element or once per package?
    per_element = (scalars["review_mode"] or "package") == "per_element"
    for item in compiled["review_checks"].values():
        if not item.get("scope"):
            general = item["_from"] == "global" or len(item["_from"]) == 2
            item["scope"] = "element" if per_element and not general else "package"
    for item in compiled["reconciliations"].values():
        item.setdefault("scope", "package")

    # Failure modes must be catchable by a check, reconciliation or interface in this context
    catchers = set(compiled["review_checks"]) | set(compiled["reconciliations"]) | {e["id"] for e in interfaces}
    for fm in compiled["failure_modes"].values():
        for cid in fm.get("caught_by", []) or []:
            if cid not in catchers:
                warnings.append(f"Failure mode {fm['id']} is caught by '{cid}', which is not a check, "
                                f"reconciliation or interface for {sid} — add one or fix caught_by")

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
                  "project": str(project) if project else None, "reviewed_as": reviewed_as},
        "note": ("Knowledge, not requirements: each check names where to look (trace_to). "
                 "The project documents govern; surface conflicts, never resolve them silently."),
        "lineage": chain,
        "coverage": {"loaded": loaded, "missing": missing, "overlays_loaded": overlays_loaded,
                     "overlays_missing": overlays_missing, "legacy_scope_files": legacy_files},
        "confidence_floor": floor,
        "equivalents": equivalents,
        "scope_summary": " ".join((scalars["scope_summary"] or "").split()) or None,
        "review_mode": scalars["review_mode"] or "package",
        "contractor_designed": scalars["contractor_designed"] or "unknown",
        "element_types": unions["element_types"],
        "submittals": list(compiled["submittals"].values()),
        "review_checks": list(compiled["review_checks"].values()),
        "reconciliations": list(compiled["reconciliations"].values()),
        "failure_modes": list(compiled["failure_modes"].values()),
        "standards": list(compiled["standards"].values()),
        "regulatory_hooks": hooks,
        "extract_fields": list(compiled["extract_fields"].values()),
        "interfaces": interfaces,
        "suppressed": suppressed,
        "escalations": escalations,
        "not_applicable": not_applicable,
        "project": project_info,
        "warnings": warnings,
    }


def filter_types(ctx, types):
    """Drop checks that name submittal types none of which are in this package."""
    if not types:
        return ctx
    wanted = set(types)
    unknown = wanted - SUBMITTAL_TYPES
    if unknown:
        raise ResolveError(f"--types: unknown submittal type(s) {sorted(unknown)} "
                           f"(choose from {', '.join(sorted(SUBMITTAL_TYPES))})")
    out = dict(ctx)
    kept, dropped = [], []
    for c in ctx.get("review_checks", []):
        (kept if not c.get("submittal_types") or wanted & set(c["submittal_types"]) else dropped).append(c)
    out["review_checks"] = kept
    out["submittals"] = [s for s in ctx.get("submittals", []) if s.get("type") in wanted]
    out["query"] = dict(ctx["query"], submittal_types=sorted(wanted))
    out["not_applicable"] = list(ctx.get("not_applicable", [])) + [c["id"] for c in dropped]
    return out


def slice_context(ctx, only):
    """Keep only the requested content lists (JIT loading); metadata always stays."""
    if not only:
        return ctx
    keep = set()
    for name in only:
        if name not in SLICES:
            raise ResolveError(f"--only: unknown slice {name!r} (choose from {', '.join(sorted(SLICES))})")
        keep.add(SLICES[name])
    out = dict(ctx)
    for key in CONTENT_KEYS:
        if key not in keep:
            out.pop(key, None)
    out["sliced"] = sorted(keep)
    return out


# ── Markdown rendering ──────────────────────────────────────────

def _txt(value):
    return " ".join(str(value or "").split())


def _sev_key(item):
    return -SEVERITIES.index(item.get("severity", "low")) if item.get("severity") in SEVERITIES else 0


def _check_line(c, home=None):
    tags = []
    if c.get("_escalated_by"):
        tags.append("escalated")
    if c.get("reflex"):
        tags.append("reflex")
    tag = f" ({', '.join(tags)})" if tags else ""
    return f"- **[{c.get('severity')}{tag}] {c['id']}** — {_txt(c.get('check'))}  "


def _check_meta(c, home):
    bits = [f"Trace: {', '.join(c.get('trace_to', []))}", f"Owner: {c.get('owner')}"]
    if c.get("scope"):
        bits.append(f"Scope: {c['scope']}")
    if c.get("submittal_types"):
        bits.append(f"Types: {', '.join(c['submittal_types'])}")
    if c.get("gate"):
        bits.append(f"Gate: {c['gate']}")
    bits.append(f"_{home}_")
    return "  " + " · ".join(bits)


def _recon_lines(r, home):
    return [
        f"- **[{r.get('severity')}{' (reflex)' if r.get('reflex') else ''}] {r['id']}** — {_txt(r.get('check'))}  ",
        "  " + " · ".join(filter(None, [
            f"Between: {' ↔ '.join(r.get('between', []))}",
            f"Key: {_txt(r['key'])}" if r.get("key") else None,
            f"Fields: {', '.join(r.get('fields', []))}",
            f"Owner: {r.get('owner')}",
            f"Gate: {r['gate']}" if r.get("gate") else None,
            f"_{home}_"])),
    ]


def _edge_lines(e, oriented=True):
    gate = e.get("gate") or {}
    gate_txt = ""
    if gate:
        gate_txt = f" · Gate: {gate.get('milestone')}" + (f" — {_txt(gate['note'])}" if gate.get("note") else "")
    if oriented:
        head = (f"- **[{e.get('severity')}] {e['id']}** → {e['counterpart_trade']} "
                f"({', '.join(e['counterpart_sections'])}){gate_txt}")
        lines = [head, f"  - Send them: {_txt(e.get('send_them'))}",
                 f"  - Need from them: {_txt(e.get('need_from_them'))}"]
    else:
        head = (f"- **[{e.get('severity')}] {e['id']}** — {e.get('a_trade')} ({', '.join(e.get('a', []))}) ↔ "
                f"{e.get('b_trade')} ({', '.join(e.get('b', []))}){gate_txt}")
        lines = [head, f"  - From {e.get('a_trade')}: {_txt(e.get('a_provides'))}",
                 f"  - From {e.get('b_trade')}: {_txt(e.get('b_provides'))}"]
    for item in gate.get("inspect_before", []) or []:
        lines.append(f"  - Inspect before: {_txt(item)}")
    for r in e.get("responsibility") or []:
        split = " / ".join(f"{k} {v}" for k, v in (r.get("typical") or {}).items())
        lines.append(f"  - Confirm who: {r.get('item')} — typical {split}")
    if e.get("failure"):
        lines.append(f"  - If missed: {_txt(e['failure'])}")
    return lines


def to_markdown(ctx):
    q, cov = ctx["query"], ctx["coverage"]
    loaded = {e["layer"] for e in cov["loaded"]}
    chain = " → ".join(n if n in loaded else f"[{n} missing]" for n in ctx["lineage"])
    out = [f"# Compiled knowledge — {q['section']} {q['title'] or ''}".rstrip(), ""]
    out.append(f"Facility types: {', '.join(q['facility_types']) or 'none'} · "
               f"Confidence floor: **{ctx['confidence_floor']}** · Review mode: {ctx['review_mode']} · "
               f"Contractor-designed: {ctx['contractor_designed']}")
    out.append(f"Lineage: {chain}")
    if q.get("reviewed_as"):
        out.append(f"Reviewed as {q['reviewed_as']} (same scope, specified under {q['section']})")
    ovs = [o["overlay"] for o in cov["overlays_loaded"]]
    if ovs or cov["overlays_missing"]:
        out.append(f"Overlays: {', '.join(ovs) or 'none'}"
                   + (f" (no file: {', '.join(cov['overlays_missing'])})" if cov["overlays_missing"] else ""))
    if ctx["equivalents"]:
        out.append(f"Also specified as: {', '.join(ctx['equivalents'])}")
    if cov["legacy_scope_files"]:
        out.append(f"Legacy scope file: {', '.join(cov['legacy_scope_files'])}")
    if ctx.get("sliced"):
        out.append(f"Slice: {', '.join(ctx['sliced'])}")
    out += ["", f"> {ctx['note']}", ""]
    if ctx["scope_summary"]:
        out += ["## Scope", ctx["scope_summary"], ""]

    if "review_checks" in ctx:
        checks = ctx["review_checks"]
        out.append(f"## Review checks ({len(checks)})")
        for kind in CHECK_KINDS:
            group = sorted([c for c in checks if c.get("kind") == kind], key=_sev_key)
            if not group:
                continue
            out.append(f"### {kind}")
            for c in group:
                out += [_check_line(c), _check_meta(c, c["_from"])]
        out.append("")

    if ctx.get("reconciliations"):
        recs = sorted(ctx["reconciliations"], key=_sev_key)
        out.append(f"## Reconciliations — documents that must agree ({len(recs)})")
        for r in recs:
            out += _recon_lines(r, r["_from"])
        out.append("")

    if "regulatory_hooks" in ctx:
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

    if "interfaces" in ctx:
        ifs = sorted(ctx["interfaces"], key=_sev_key)
        out.append(f"## Coordination routing ({len(ifs)})")
        for e in ifs:
            out += _edge_lines(e)
        out.append("")

    if "failure_modes" in ctx:
        out.append(f"## Failure modes to watch ({len(ctx['failure_modes'])})")
        for fm in ctx["failure_modes"]:
            caught = ", ".join(fm.get("caught_by", []) or []) or "no check"
            out.append(f"- **{fm['id']}** — {_txt(fm.get('what_happens'))} → {_txt(fm.get('consequence'))} "
                       f"(caught by {caught}; {fm.get('source', 'n/a')})")
        out.append("")

    if ctx.get("submittals"):
        out.append("## Expected submittal contents")
        for s in ctx["submittals"]:
            out.append(f"- **{s.get('type')}**")
            for line in s.get("must_show", []) or []:
                out.append(f"  - {_txt(line)}")
        out.append("")
    if ctx.get("extract_fields"):
        out.append("## Extract for reconciliation")
        for x in ctx["extract_fields"]:
            unit = f", {x['unit']}" if x.get("unit") else ""
            out.append(f"- {x['id']} — {x.get('label')} ({x.get('type')}{unit}, per {x.get('per', 'element')}) "
                       f"→ {', '.join(x.get('reconcile_against', []) or [])}")
        out.append("")
    if ctx.get("standards"):
        out.append("## Standards to verify against")
        for s in ctx["standards"]:
            note = f" — {_txt(s['note'])}" if s.get("note") else ""
            out.append(f"- {s.get('name')}: {_txt(s.get('title'))}{note}")
        out.append("")
    if ctx.get("escalations"):
        out.append("## Escalations")
        for e in ctx["escalations"]:
            out.append(f"- {e['target']}: {e['from']} → {e['to']} by {e['by']} — {_txt(e.get('reason'))}")
        out.append("")
    if ctx.get("suppressed"):
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


# ── Cross-layer views: reflexes and milestones ──────────────────

def _home_items(kb, facilities, sections):
    """Yield (home, list_name, item, doc) for every keyed item at the file that defines it.

    Views list items where they live; per-section overrides and suppressions apply only in resolve.
    """
    for path in iter_files(kb, "profiles"):
        doc = load_yaml(path)
        home = str(doc.get("id"))
        if not layer_relevant(home, sections):
            continue
        for list_name in GATED_LISTS:
            for item in doc.get(list_name, []) or []:
                if not item.get("override"):
                    yield home, list_name, item, doc
    chain = facility_chain(facilities)
    for path in iter_files(kb, "overlays"):
        doc = load_yaml(path)
        if str(doc.get("id")) not in chain:
            continue
        default = doc.get("sections", []) or []
        for list_name in GATED_LISTS:
            for item in doc.get(list_name, []) or []:
                pats = item.get("sections", default)
                if sections is not None and not any(
                        fnmatch.fnmatchcase(node, pat) for pat in pats for s in sections for node in lineage(s)):
                    continue
                yield f"overlay:{doc.get('id')}", list_name, item, doc


def _home_edges(kb, facilities, sections):
    for path in iter_files(kb, "interfaces"):
        doc = load_yaml(path)
        for edge in doc.get("edges", []) or []:
            if not facility_matches(edge.get("facility_types"), facilities):
                continue
            if sections is not None and not edge_in_project(edge, sections):
                continue
            yield f"interfaces:{doc.get('id')}", edge, doc


def _view_scope(kb, facilities, project):
    project = Path(project).resolve() if project else None
    facilities = list(dict.fromkeys(list(facilities) + project_facilities(project)))
    sections = project_sections(project)
    notes = []
    if project is not None and sections is None:
        notes.append("No extracted spec text in the project (run /construction:spec-splitter); "
                     "showing the whole layer")
    return facilities, sections, notes


def reflexes(kb, facilities=(), project=None):
    facilities, sections, notes = _view_scope(kb, facilities, project)
    groups = {}
    for home, list_name, item, doc in _home_items(kb, facilities, sections):
        if not item.get("reflex"):
            continue
        group = home if home.startswith("overlay:") or home == "global" else f"Division {home[:2]}"
        entry = {k: v for k, v in item.items() if k not in ("sections",)}
        entry.update({"_list": list_name, "_home": home, "_status": doc.get("status", "draft")})
        groups.setdefault(group, []).append(entry)
    for home, edge, doc in _home_edges(kb, facilities, sections):
        if edge.get("reflex"):
            entry = dict(edge)
            entry.update({"_list": "interfaces", "_home": home, "_status": doc.get("status", "draft")})
            groups.setdefault("Interfaces", []).append(entry)
    order = sorted(groups, key=lambda g: (g != "global", g.startswith("overlay:"), g == "Interfaces", g))
    return {"facility_types": facilities,
            "sections_filter": sorted(sections) if sections else None,
            "count": sum(len(v) for v in groups.values()),
            "groups": {g: sorted(groups[g], key=_sev_key) for g in order},
            "notes": notes}


def milestone_view(kb, mid, facilities=(), project=None):
    milestones = load_milestones(kb)
    ids = [m.get("id") for m in milestones]
    if mid not in ids:
        raise ResolveError(f"Unknown milestone {mid!r} (choose from {', '.join(ids)})")
    m = milestones[ids.index(mid)]
    facilities, sections, notes = _view_scope(kb, facilities, project)
    checks, recons, edges = [], [], []
    for home, list_name, item, doc in _home_items(kb, facilities, sections):
        if item.get("gate") == mid:
            entry = {k: v for k, v in item.items() if k not in ("sections",)}
            entry.update({"_home": home, "_status": doc.get("status", "draft")})
            (checks if list_name == "review_checks" else recons).append(entry)
    for home, edge, doc in _home_edges(kb, facilities, sections):
        if (edge.get("gate") or {}).get("milestone") == mid:
            entry = dict(edge)
            entry.update({"_home": home, "_status": doc.get("status", "draft")})
            edges.append(entry)
    catch_ids = {c["id"] for c in checks} | {r["id"] for r in recons} | {e["id"] for e in edges}
    failures = []
    for path in iter_files(kb, "profiles") + iter_files(kb, "overlays"):
        doc = load_yaml(path)
        for fm in doc.get("failure_modes", []) or []:
            if catch_ids & set(fm.get("caught_by", []) or []):
                failures.append(dict(fm, _home=str(doc.get("id"))))
    return {"milestone": {"id": mid, "title": m.get("title"), "position": f"{ids.index(mid) + 1} of {len(ids)}",
                          "covers": m.get("covers", []), "inspect_before": m.get("inspect_before", [])},
            "facility_types": facilities,
            "sections_filter": sorted(sections) if sections else None,
            "interfaces": sorted(edges, key=_sev_key),
            "review_checks": sorted(checks, key=_sev_key),
            "reconciliations": sorted(recons, key=_sev_key),
            "failure_modes": failures,
            "notes": notes}


def topics(kb):
    """Every regulatory hook topic in the layer, with the hooks that use it."""
    out = {}
    for path in iter_files(kb, "profiles") + iter_files(kb, "overlays"):
        doc = load_yaml(path)
        for h in doc.get("regulatory_hooks", []) or []:
            if h.get("topic"):
                out.setdefault(h["topic"], []).append(
                    {"hook": h.get("id"), "file": str(path.relative_to(kb)),
                     "families": h.get("source_families", [])})
    return dict(sorted(out.items()))


def reflexes_markdown(view):
    out = [f"# Reflex checks — always on ({view['count']})", ""]
    out.append("Notice these while looking at anything, even when they are unrelated to the question. "
               "Each lives in the file shown; resolve that section for the full context.")
    if view["sections_filter"]:
        out.append(f"Filtered to project sections: {', '.join(view['sections_filter'])}")
    out.append("")
    for group, items in view["groups"].items():
        out.append(f"## {group}")
        for it in items:
            if it["_list"] == "interfaces":
                out += _edge_lines(it, oriented=False)
            elif it["_list"] == "reconciliations":
                out += _recon_lines(it, it["_home"])
            else:
                out += [_check_line(it), _check_meta(it, it["_home"])]
        out.append("")
    for n in view["notes"]:
        out.append(f"- Note: {n}")
    return "\n".join(out).rstrip() + "\n"


def milestone_markdown(view):
    m = view["milestone"]
    title = m["title"][:1].lower() + m["title"][1:]
    out = [f"# Before {title} (`{m['id']}`, {m['position']})", ""]
    if view["sections_filter"]:
        out.append(f"Filtered to project sections: {', '.join(view['sections_filter'])}")
        out.append("")
    if m["covers"]:
        out.append("## What this covers or locks")
        out += [f"- {_txt(c)}" for c in m["covers"]]
        out.append("")
    if m["inspect_before"]:
        out.append("## Inspect or test first")
        out += [f"- {_txt(c)}" for c in m["inspect_before"]]
        out.append("")
    if view["interfaces"]:
        out.append(f"## Coordination to close ({len(view['interfaces'])})")
        for e in view["interfaces"]:
            out += _edge_lines(e, oriented=False)
        out.append("")
    if view["review_checks"]:
        out.append(f"## Checks due by this milestone ({len(view['review_checks'])})")
        for c in view["review_checks"]:
            out += [_check_line(c), _check_meta(c, c["_home"])]
        out.append("")
    if view["reconciliations"]:
        out.append(f"## Documents that must agree first ({len(view['reconciliations'])})")
        for r in view["reconciliations"]:
            out += _recon_lines(r, r["_home"])
        out.append("")
    if view["failure_modes"]:
        out.append("## What goes wrong if missed")
        for fm in view["failure_modes"]:
            out.append(f"- **{fm['id']}** — {_txt(fm.get('what_happens'))} → {_txt(fm.get('consequence'))}")
        out.append("")
    for n in view["notes"]:
        out.append(f"- Note: {n}")
    return "\n".join(out).rstrip() + "\n"


def milestones_markdown(kb):
    out = ["# Milestones (approximate order within an area)", ""]
    for i, m in enumerate(load_milestones(kb), 1):
        out.append(f"{i}. `{m['id']}` — {m.get('title')}")
    return "\n".join(out) + "\n"


# ── Validate and lint ───────────────────────────────────────────

SECTION_IN_TEXT = re.compile(r"\b\d{2} \d{2} \d{2}(?:\.\d{2})?\b")
STANDARD_IN_TEXT = re.compile(
    r"\b(?:ASTM|UL|NFPA|ANSI|ASHRAE|SEFA|AWI|BHMA|FM|ISEA|ICC|IBC|IFC|IECC|NEC|TIA|SPRI|AAMA|ACI|AISC|AWS|"
    r"NEMA|SMACNA|TCNA|IES|CSA|ASCE|ASME)\b[\s/A-Z.\-]*\d+[\w.\-/()]*")
BARE_NUMBER = re.compile(
    r"\d+(?:[.,/]\d+)?\s*(?:[\"”″'’°%]|-?\s*(?:in|inch|inches|ft|feet|foot|mils?|psi|psf|plf|cfm|gpm|"
    r"sf|sq\s*in|sq\s*ft|mm|cm|lbs?|kips?|amps?|volts?|kva|kw|hp|btuh?|degrees?|minutes?|mins?|hours?|"
    r"hrs?|days?|weeks?|months?|years?|yrs?)\b)|\bR-?\d+(?:\.\d+)?\b|\bL/\d+\b|\b\d+:\d+\b",
    re.I)
STOPWORDS = {"the", "and", "for", "are", "with", "that", "this", "from", "each", "every", "where",
             "into", "its", "their", "not", "any", "all", "has", "have", "per", "before", "after"}


def _texts(doc):
    """(where, text) for every authored sentence that the bare-number lint should see."""
    if doc.get("scope_summary"):
        yield "scope_summary", doc["scope_summary"]
    for list_name in KEYED_LISTS:
        if list_name == "standards":
            continue
        for item in doc.get(list_name, []) or []:
            for field in ("check", "question", "applies_when", "what_happens", "consequence", "label"):
                if item.get(field):
                    yield f"{item.get('id')}.{field}", item[field]
            for line in item.get("must_show", []) or []:
                yield f"{item.get('id')}.must_show", line
    for esc in doc.get("escalate", []) or []:
        if esc.get("reason"):
            yield f"escalate {esc.get('target')}", esc["reason"]
    for edge in doc.get("edges", []) or []:
        for field in ("a_provides", "b_provides", "failure"):
            if edge.get(field):
                yield f"{edge.get('id')}.{field}", edge[field]
        gate = edge.get("gate") or {}
        if gate.get("note"):
            yield f"{edge.get('id')}.gate", gate["note"]
        for line in gate.get("inspect_before", []) or []:
            yield f"{edge.get('id')}.gate", line
        for r in edge.get("responsibility", []) or []:
            if r.get("item"):
                yield f"{edge.get('id')}.responsibility", r["item"]
    for m in doc.get("milestones", []) or []:
        for line in [m.get("title", "")] + (m.get("covers", []) or []) + (m.get("inspect_before", []) or []):
            yield f"{m.get('id')}", line


def bare_numbers(text):
    clean = STANDARD_IN_TEXT.sub("§", SECTION_IN_TEXT.sub("§", str(text)))
    return [m.group(0).strip() for m in BARE_NUMBER.finditer(clean)]


def _tokens(text):
    return {w for w in re.findall(r"[a-z]{3,}", str(text).lower()) if w not in STOPWORDS}


def near_duplicates(entries, threshold=0.75):
    """entries: [(where, id, text)]. Pairs from different items whose wording is nearly the same."""
    found = []
    toks = [(w, i, t, _tokens(t), " ".join(str(t).lower().split())) for w, i, t in entries]
    for x in range(len(toks)):
        for y in range(x + 1, len(toks)):
            wa, ia, _, ta, na = toks[x]
            wb, ib, _, tb, nb = toks[y]
            if ia == ib or not ta or not tb:
                continue
            if len(ta & tb) / len(ta | tb) < 0.45:
                continue
            ratio = difflib.SequenceMatcher(None, na, nb).ratio()
            if ratio >= threshold:
                found.append((wa, ia, wb, ib, ratio))
    return found


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
    if rel.parts[0] == "milestones.yaml":
        return "milestones", "milestones"
    return path.stem, "interfaces"


def validate(kb):
    kb = Path(kb)
    errors, warnings, lint = [], [], []
    files = iter_files(kb, "profiles") + iter_files(kb, "overlays") + iter_files(kb, "interfaces")
    if (kb / "milestones.yaml").exists():
        files.append(kb / "milestones.yaml")
    all_check_ids, escalate_targets, section_ids, overlay_ids, drafts = set(), [], [], [], 0
    dup_entries = []

    def err(path, msg):
        errors.append(f"{path.relative_to(kb)}: {msg}")

    def warn(path, msg):
        warnings.append(f"{path.relative_to(kb)}: {msg}")

    # Milestones first: everything else validates gates against them
    milestone_ids = set()
    mpath = kb / "milestones.yaml"
    if mpath.exists():
        try:
            mdoc = load_yaml(mpath)
            for m in mdoc.get("milestones", []) or []:
                mid = m.get("id")
                if not mid or not re.fullmatch(r"[a-z0-9]+(_[a-z0-9]+)*", str(mid)):
                    err(mpath, f"milestone id must be a snake_case slug: {mid!r}")
                    continue
                if mid in milestone_ids:
                    err(mpath, f"duplicate milestone {mid!r}")
                milestone_ids.add(mid)
                if not m.get("title"):
                    err(mpath, f"milestone {mid}: missing title")
                for field in ("covers", "inspect_before"):
                    if not isinstance(m.get(field, []), list):
                        err(mpath, f"milestone {mid}: {field} must be a list")
        except yaml.YAMLError as e:
            err(mpath, f"YAML parse error: {e}")
    else:
        warnings.append("milestones.yaml missing: gates cannot be validated")

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

        for where, text in _texts(doc):
            hits = bare_numbers(text)
            if hits:
                lint.append(f"{path.relative_to(kb)}: {where}: bare number {', '.join(repr(h) for h in hits)} — "
                            f"make it a regulatory_hook question or cite the project document instead")

        if kind == "section" and normalize(exp_id) != exp_id:
            err(path, f"file name is not a canonical section number: {exp_id!r}")
        if kind in ("global", "division", "section"):
            section_ids.append(str(doc.get("id")))
            if doc.get("contractor_designed") and doc["contractor_designed"] not in CONTRACTOR_DESIGNED:
                err(path, f"contractor_designed must be one of {CONTRACTOR_DESIGNED}")
            if doc.get("legacy_scope_file") and kind != "division":
                err(path, "legacy_scope_file belongs on a division baseline only")
            if doc.get("same_as"):
                target = normalize(doc["same_as"])
                if kind != "section" or not target or len(target) == 2:
                    err(path, "same_as belongs on a section profile and must name another section")
                elif not profile_path(kb, target).exists():
                    err(path, f"same_as target {target} has no profile")
                elif load_yaml(profile_path(kb, target)).get("same_as"):
                    err(path, f"same_as target {target} is itself an alias; point at the real profile")
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
                    text = item.get("check") or item.get("question") or item.get("what_happens")
                    if text and list_name in ("review_checks", "reconciliations", "failure_modes",
                                              "regulatory_hooks"):
                        dup_entries.append((f"{path.relative_to(kb)} {list_name}", item_id, text))
                if item.get("merge") not in (None, "patch", "replace"):
                    err(path, f"{list_name} {item_id}: merge must be patch or replace")
                if "severity" in item and item["severity"] not in SEVERITIES:
                    err(path, f"{list_name} {item_id}: invalid severity {item['severity']!r}")
                if ("reflex" in item or "gate" in item) and list_name not in GATED_LISTS:
                    err(path, f"{list_name} {item_id}: reflex and gate belong on checks and reconciliations")
                if "reflex" in item and not isinstance(item["reflex"], bool):
                    err(path, f"{list_name} {item_id}: reflex must be true or false")
                if "scope" in item and (list_name != "review_checks" or item["scope"] not in SCOPES):
                    err(path, f"{list_name} {item_id}: scope belongs on checks and must be element or package")
                if item.get("gate") and milestone_ids and item["gate"] not in milestone_ids:
                    err(path, f"{list_name} {item_id}: unknown gate milestone {item['gate']!r}")
                for key, allowed in (item.get("applies_if") or {}).items():
                    values = allowed if isinstance(allowed, list) else [allowed]
                    if key not in APPLIES_IF:
                        err(path, f"{list_name} {item_id}: applies_if key {key!r} not supported "
                                  f"(use {', '.join(sorted(APPLIES_IF))})")
                    elif not set(values) <= APPLIES_IF[key]:
                        err(path, f"{list_name} {item_id}: applies_if {key} values must be from "
                                  f"{sorted(APPLIES_IF[key])}")
                if list_name in ("review_checks", "reconciliations"):
                    all_check_ids.add(item_id)
                    if "owner" in item and item["owner"] not in OWNERS:
                        err(path, f"{list_name} {item_id}: owner must be one of {sorted(OWNERS)}")
                if list_name == "review_checks":
                    if "kind" in item and item["kind"] not in CHECK_KINDS:
                        err(path, f"check {item_id}: kind must be one of {CHECK_KINDS}")
                    for t in item.get("submittal_types", []) or []:
                        if t not in SUBMITTAL_TYPES:
                            warn(path, f"check {item_id}: unknown submittal type {t!r}")
                if list_name == "reconciliations":
                    between = item.get("between", []) or []
                    if "between" in item and len(between) < 2:
                        err(path, f"reconciliation {item_id}: between needs at least two documents")
                    for t in between:
                        if t not in TRACE_TERMS:
                            warn(path, f"reconciliation {item_id}: unknown document term {t!r}")
                    if "fields" in item and not item.get("fields"):
                        err(path, f"reconciliation {item_id}: fields must list what has to agree")
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
                if "reflex" in edge and not isinstance(edge["reflex"], bool):
                    err(path, f"edge {eid}: reflex must be true or false")
                gate = edge.get("gate") or {}
                if gate and milestone_ids and gate.get("milestone") not in milestone_ids:
                    err(path, f"edge {eid}: unknown gate milestone {gate.get('milestone')!r}")
                if not isinstance(gate.get("inspect_before", []), list):
                    err(path, f"edge {eid}: gate.inspect_before must be a list")
                for r in edge.get("responsibility", []) or []:
                    extra = set((r.get("typical") or {})) - {"furnish", "install", "connect"}
                    if extra:
                        err(path, f"edge {eid}: responsibility keys must be furnish/install/connect, got {sorted(extra)}")

    # Ids are global: an id lives in one file (overrides restate an inherited id on purpose)
    homes = {}
    for path in files:
        doc = load_yaml(path)
        entries = []
        for list_name in KEYED_LISTS:
            entries += [(list_name, it) for it in doc.get(list_name, []) or [] if not it.get("override")]
        entries += [("edges", e) for e in doc.get("edges", []) or []]
        for list_name, item in entries:
            iid = item.get("id")
            if not iid:
                continue
            if iid in homes and homes[iid] != path:
                err(path, f"{list_name} id {iid!r} is already defined in {homes[iid].relative_to(kb)} — ids are global")
            homes.setdefault(iid, path)

    # One id prefix, one owner: `hc.` in a site-utility profile reads as healthcare in a finding
    prefix_owners = {}
    for path in files:
        rel = path.relative_to(kb).parts
        if rel[0] == "profiles" and len(rel) > 2:
            owner = rel[1]
        elif rel[0] == "overlays":
            owner = "overlay " + rel[1].split(".")[0]
        else:
            continue
        doc = load_yaml(path)
        for list_name in KEYED_LISTS:
            for item in doc.get(list_name, []) or []:
                if item.get("override") or not item.get("id"):
                    continue
                prefix_owners.setdefault(str(item["id"]).split(".")[0], set()).add(owner)
    for prefix, owners in sorted(prefix_owners.items()):
        if len(owners) > 1:
            lint.append(f"id prefix {prefix!r} is used by {', '.join(sorted(owners))} — one prefix, one owner (AUTHORING §4)")

    # An edge states its own failure only when no failure mode names it (SCHEMA, interface edges)
    named_by = {}
    for path in files:
        for fm in load_yaml(path).get("failure_modes") or []:
            for cid in fm.get("caught_by", []) or []:
                named_by.setdefault(cid, fm.get("id"))
    for path in files:
        for edge in load_yaml(path).get("edges") or []:
            if edge.get("failure") and edge.get("id") in named_by:
                lint.append(f"{path.relative_to(kb)}: edge {edge['id']} states a failure, but failure mode "
                            f"{named_by[edge['id']]} already names it — drop the edge's failure")

    for path, target in escalate_targets:
        if target not in all_check_ids and not any(
                target == h.get("id") for p in files for h in (load_yaml(p).get("regulatory_hooks") or [])):
            warn(path, f"escalate target {target!r} exists nowhere in the knowledge layer")

    for wa, ia, wb, ib, ratio in near_duplicates(dup_entries):
        lint.append(f"near-duplicate ({ratio:.0%}): {ia} [{wa}] and {ib} [{wb}] — keep one home")

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

    return errors, sorted(set(warnings)), sorted(set(lint)), drafts, len(files)


# ── CLI ─────────────────────────────────────────────────────────

def emit(text, output):
    if output:
        out = safe_output_path(output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"Wrote {out}")
    else:
        sys.stdout.write(text)


def dump(data):
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100)


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # Windows consoles default to a legacy code page
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--kb", default=str(DEFAULT_KB), help="Knowledge layer root (default: reference/csi)")
    sub = parser.add_subparsers(dest="command", required=True)

    def view_args(sp):
        sp.add_argument("--facility", action="append", default=[],
                        help="Facility type, repeatable (healthcare.hospital)")
        sp.add_argument("--project", help="Project root: reads facility types, code-researcher findings, spec text")
        sp.add_argument("--format", choices=["yaml", "md"], default="yaml")
        sp.add_argument("--output", help="Write to this file (versioned, never overwrites) instead of stdout")

    r = sub.add_parser("resolve", help="Compile the knowledge for one section")
    r.add_argument("--section", required=True, help='e.g. "07 84 00", 078400, or a legacy number like 12300')
    r.add_argument("--only", help=f"Comma list of slices to keep: {', '.join(sorted(set(SLICES)))}")
    r.add_argument("--types", help='Comma list of submittal types in the package, e.g. "Shop Drawings,Product Data"; '
                                   'drops checks that apply only to other types')
    view_args(r)
    x = sub.add_parser("reflexes", help="Always-on checks across the layer, grouped by where they live")
    view_args(x)
    m = sub.add_parser("milestone", help="What must be verified before a milestone (no --id lists them)")
    m.add_argument("--id", help="Milestone id, e.g. wall_close_in")
    view_args(m)
    t = sub.add_parser("topics", help="List regulatory hook topics (reuse one before inventing a new slug)")
    t.add_argument("--format", choices=["yaml", "md"], default="md")
    v = sub.add_parser("validate", help="Validate every file, merge rule and authoring lint")
    v.add_argument("--strict", action="store_true", help="Treat warnings and lint as errors")
    v.add_argument("--focus", action="append", default=[],
                   help="Only report messages containing this text (repeatable), e.g. profiles/03/ or div-03")
    args = parser.parse_args()

    try:
        if args.command == "resolve":
            ctx = resolve(args.kb, args.section, args.facility, args.project)
            ctx = filter_types(ctx, [t.strip() for t in args.types.split(",")] if args.types else None)
            ctx = slice_context(ctx, [s.strip() for s in args.only.split(",")] if args.only else None)
            emit(to_markdown(ctx) if args.format == "md" else dump(ctx), args.output)
            return 0
        if args.command == "reflexes":
            view = reflexes(args.kb, args.facility, args.project)
            emit(reflexes_markdown(view) if args.format == "md" else dump(view), args.output)
            return 0
        if args.command == "topics":
            data = topics(args.kb)
            if args.format == "yaml":
                emit(dump(data), None)
            else:
                lines = [f"# Regulatory hook topics ({len(data)})", ""]
                for topic, uses in data.items():
                    fams = sorted({f for u in uses for f in u["families"]})
                    lines.append(f"- `{topic}` — {', '.join(u['hook'] for u in uses)} ({', '.join(fams)})")
                emit("\n".join(lines) + "\n", None)
            return 0
        if args.command == "milestone":
            if not args.id:
                emit(milestones_markdown(args.kb) if args.format == "md"
                     else dump({"milestones": load_milestones(args.kb)}), args.output)
                return 0
            view = milestone_view(args.kb, args.id, args.facility, args.project)
            emit(milestone_markdown(view) if args.format == "md" else dump(view), args.output)
            return 0
    except ResolveError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    errors, warnings, lint, drafts, count = validate(args.kb)
    if args.focus:
        def keep(msg):
            return any(f in msg for f in args.focus)
        errors, warnings, lint = [e for e in errors if keep(e)], [w for w in warnings if keep(w)], \
            [x for x in lint if keep(x)]
    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"WARNING {w}")
    for item in lint:
        print(f"LINT    {item}")
    print(f"\n{count} files · {len(errors)} errors · {len(warnings)} warnings · {len(lint)} lint · "
          f"{drafts} at draft status")
    return 1 if errors or (args.strict and (warnings or lint)) else 0


if __name__ == "__main__":
    sys.exit(main())
