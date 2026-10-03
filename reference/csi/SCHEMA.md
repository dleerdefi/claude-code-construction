# CSI Knowledge Layer — Profile Schema and Merge Rules

**Status:** Draft v1 (`schema_version: 1`)
**Location:** `reference/csi/` (shared domain knowledge, read via `${CLAUDE_PLUGIN_ROOT}/reference/csi/`)
**Resolver:** `scripts/csi/csi_knowledge.py` (`resolve` and `validate`)

The knowledge layer holds what an expert PE knows about each CSI section, independent of any project. Any skill (submittal review, RFI drafting, bid evaluation, subcontract writing, code research) asks the resolver for a section and gets one compiled context: what to check, where the requirement lives in the project documents, how it usually goes wrong, who it touches, and which regulatory questions must be answered for this facility type and jurisdiction.

---

## 1. Three layers, never mixed

| Layer | Holds | Lives in | Authority |
|---|---|---|---|
| **Procedure** | The SOP: how to review, extract, draft | `skills/<skill>/SKILL.md` | How to work |
| **Domain knowledge** | What to check for each section, typical failures, interfaces, regulatory questions | `reference/csi/` (this layer) | What to ask |
| **Project facts** | Specs, drawings, registers, jurisdiction, code research | Project folder + `.construction/skills/` | What is required |

**Rule K1 — Knowledge never becomes a requirement.** A profile says *what to verify and where to look*. The answer always comes from the project documents (`trace_to`) or from jurisdiction research (`regulatory_hooks`). If a profile assumption conflicts with the project spec, the spec governs and the conflict is surfaced, never silently resolved. Profiles therefore contain questions and verification targets, not code thresholds or dimensions.

---

## 2. Files

```
reference/csi/
├── SCHEMA.md                    ← this file
├── profiles/
│   ├── _global.yaml             ← rules for every submittal (Division 01 practice)
│   └── 12/
│       ├── _division.yaml       ← Division 12 baseline
│       ├── 12-30-00.yaml        ← Casework
│       └── 12-35-53.yaml        ← Laboratory Casework
├── overlays/
│   └── healthcare.yaml          ← facility-type requirements that cut across divisions
└── interfaces/
    └── div-12.yaml              ← coordination edges between sections
```

File name = section id with hyphens (`12 35 53` → `12-35-53.yaml`; `12 35 53.13` → `12-35-53.13.yaml`). Division baselines are `profiles/<DD>/_division.yaml`. Overlay file name = facility type (`healthcare.hospital.yaml`). Interface files are grouped for authoring convenience only; the resolver loads all of them.

---

## 3. Common header (every file)

```yaml
schema_version: 1
kind: global | division | section | overlay | interfaces
id: "12 35 53"            # "global" | "12" | "12 35 53" | "healthcare" | "div-12"
title: Laboratory Casework
status: draft             # draft | pe_reviewed | field_validated
maintainers: [dleerdefi]
reviewed_by: []           # PEs who reviewed this file
last_reviewed: null       # YYYY-MM-DD
```

`status` is the trust signal. It travels with every item into the compiled output, and the compiled context reports a **confidence floor** (the lowest status that contributed). A review built on `draft` knowledge says so.

---

## 4. Section profiles (`kind: global | division | section`)

| Field | Type | Merge | Purpose |
|---|---|---|---|
| `scope_summary` | text | most specific wins | What this section covers, in a PE's words |
| `equivalents` | list of ids | not inherited | Other numbers the same scope is often specified under (e.g. casework in 06 41 00 vs 12 30 00). Taken from the queried section's own profile only, and surfaced so the skill checks which number the project uses |
| `legacy_numbers` | list | not inherited | MasterFormat 1995 numbers that map to this profile (`"12300"`). The resolver accepts them as input |
| `legacy_scope_file` | path | n/a | Division only. Bridge to `reference/pe_expertise/scope-*.md` until it is migrated |
| `review_mode` | `per_element` \| `package` | most specific wins | Whether the review skill fans out one worker per element (elevation, item, tag) or reviews the package whole |
| `element_types` | list | union | The units of fan-out (`casework_elevation`, `equipment_item`, …) |
| `submittals` | keyed list | by `id` | Submittal types expected and what each must show |
| `review_checks` | keyed list | by `id` | Verification targets (see 4.1) |
| `failure_modes` | keyed list | by `id` | How this scope goes wrong in the field |
| `standards` | keyed list | by `id` | Industry standards to verify against — references, never text |
| `regulatory_hooks` | keyed list | by `id` | Compliance questions bound to jurisdiction research (see 4.2) |
| `extract_fields` | keyed list | by `id` | Data to pull from the submittal for reconciliation |
| `suppress` | list | n/a | Turn off inherited items, with a reason (rule M4) |

### 4.1 `review_checks`

```yaml
review_checks:
  - id: cw.in-wall-support
    kind: constructability       # completeness | conformance | coordination | constructability | absence
    submittal_types: [Shop Drawings]   # labels from submittal-log-generator's taxonomy; omit = all
    check: >
      Wall-hung casework and countertop supports show support type, location,
      height and load, with in-wall components flagged for install before close-in.
    trace_to: [drawings.details, drawings.interior_elevations, spec.part3]
    severity: critical           # critical | high | medium | low
    owner: gc                    # gc | subcontractor | design_team | owner
```

**`kind`** maps to the four review passes:

| kind | Question | Typical outcome |
|---|---|---|
| `completeness` | Did they submit everything required, for every element? | Resubmit / incomplete |
| `conformance` | Does it match the contract documents? | Correction or rejection |
| `coordination` | What does it mean for other trades? | Routing to a sub |
| `constructability` | Can it be built, in sequence, as shown? | Field action / GC action |
| `absence` | Are the *contract documents* missing something? | Issue → RFI candidate |

Compliance is not a check kind: it lives in `regulatory_hooks`, because its answer comes from jurisdiction research, not from the drawings.

**`trace_to`** names where the requirement lives in the project documents. Use this vocabulary so the review skill (and AgentCM queries) can resolve it:

`spec.part1`, `spec.part1_submittals`, `spec.part2`, `spec.part2_manufacturers`, `spec.part3`, `drawings.plans`, `drawings.interior_elevations`, `drawings.details`, `drawings.material_legend`, `drawings.plumbing`, `drawings.electrical`, `drawings.mechanical`, `drawings.lab_gas`, `drawings.structural`, `schedule.casework`, `schedule.casework_hardware`, `schedule.finish`, `schedule.equipment`, `schedule.plumbing_fixture`, `schedule.master`, `register.submittal_log`, `register.rfi_log`, `register.asi_bulletin_log`, `register.substitutions`, `drawings.revision_blocks`.

The validator warns on anything else; add new terms here first.

**`owner`** says who resolves a finding. It is how the output separates "sub must fix" from "design team must answer" (an RFI candidate).

### 4.2 `regulatory_hooks`

```yaml
regulatory_hooks:
  - id: cw.rh.accessibility-work-surfaces
    topic: accessibility-work-surfaces     # = code-researcher topic slug
    question: >
      Do designated accessible work surfaces, sinks and service counters meet the
      adopted accessibility standard for height, knee/toe clearance and reach?
    applies_when: Any casework with accessible units or public service counters
    source_families: [accessibility]
    severity: high
```

A hook is a compliance **question**, never an answer. The resolver binds each hook to code-researcher's findings for the same `topic` slug (`.construction/skills/code-researcher/topics/<topic>.yaml`):

| Binding status | Meaning | Review output |
|---|---|---|
| `bound` | Findings exist and every edition is confirmed | Check submittal against the cited requirement |
| `bound_unconfirmed` | Findings exist but at least one edition is unconfirmed | Check, and mark **verify with AHJ** |
| `unbound` | No research yet | Listed as an open compliance item with the command to research it |

**Rule K2 — Hooks are never dropped.** Every applicable hook appears in the compiled output in one of these three states. This is how a health-department requirement that no drawing mentions still reaches the reviewer.

`source_families` seeds code-researcher's Pass 2: `accessibility`, `building_code`, `building_code_seismic`, `fire_code`, `health_facility_licensing`, `fgi_guidelines`, `food_code`, `pharmacy`, `occupational_safety`, `environmental`, `energy`.

### 4.3 Other keyed lists

```yaml
submittals:
  - id: shop_drawings
    type: Shop Drawings                  # submittal-log-generator taxonomy label
    must_show:
      - "Elevations keyed to every CD elevation tag, with counter heights AFF"

failure_modes:
  - id: cw.fm.in-wall-brackets-missed
    what_happens: In-wall brackets not identified or not sent to the framer before close-in
    consequence: Walls reopened, patch and paint, casework install slips
    caught_by: [cw.in-wall-support]      # check ids that catch it
    source: field_experience             # field_experience | industry_practice | project_incident
    incident: null                       # optional project/RFI reference

standards:
  - id: cw.std.bhma-a156-9
    name: ANSI/BHMA A156.9
    title: Cabinet Hardware
    verify: Hardware grade and function claims on product data
    note: Confirm the edition the spec cites

extract_fields:
  - id: cw.xf.counter-height
    label: Counter / work-surface height AFF
    type: number                         # number | string | boolean | enum | list
    unit: in
    per: element                         # element | item | package
    reconcile_against: [drawings.interior_elevations]
```

`failure_modes` is the most valuable field in the layer. It is what turns a checklist into expertise. Write them from real misses.

---

## 5. Overlays (`kind: overlay`)

Overlays hold requirements driven by **facility type** rather than by section — the healthcare rule that touches casework, finishes, door hardware and plumbing fixtures at once. Writing them once, keyed by facility, keeps them from being copied into every section profile (and forgotten in one of them).

```yaml
kind: overlay
id: healthcare
facility_type: healthcare
sections: ["12 3*", "06 41*"]        # default scope for items without their own
review_checks: [...]                 # each item may carry its own `sections`
failure_modes: [...]
regulatory_hooks: [...]
escalate:
  - target: cw.counter-heights       # id from the section chain
    severity: critical
    reason: Health facility rules can govern heights beyond what the drawings show
```

- **Facility types are dotted** and inherit: a project typed `healthcare.hospital` loads `healthcare.yaml`, then `healthcare.hospital.yaml` if it exists.
- **`sections` patterns** are globs matched against the query's lineage: `"12 3*"` hits 12 30 00 and 12 35 53; `"09"` hits every Division 09 section.
- A project gets its facility types from `.construction/skills/project_context.yaml` → `building.facility_types` (or `--facility` on the command line). A hospital with a kitchen and labs lists all three.

---

## 6. Interfaces (`kind: interfaces`)

Coordination is a relationship between two scopes, so it is stored once as an **edge** and read from either side.

```yaml
kind: interfaces
id: div-12
edges:
  - id: if.casework-backing
    a: ["12 30 00", "06 41 00"]
    a_trade: Casework
    b: ["06 10 53", "09 22 16", "05 50 00"]
    b_trade: Framing / rough carpentry / misc. metals
    a_provides: In-wall support and backing locations, heights, loads and bracket types per elevation
    b_provides: Backing type per wall assembly; confirmation installed before close-in
    responsibility:
      - item: In-wall brackets for wall-hung counters
        typical: {furnish: "12 30 00", install: "06 10 53 or 09 22 16"}
        confirm_in: [spec.part1, drawings.details]
    gate: {milestone: wall_close_in, note: Before second-side gypsum board}
    severity: critical
    failure: Backing missed; walls reopened after drywall
    facility_types: []          # optional: edge applies only to these facility types
```

- An endpoint matches the query if either is an ancestor of the other: an edge declared on 06 10 53 still reaches a project that specifies blocking in 06 10 00.
- The resolver orients each edge from the queried side: `counterpart_sections`, `counterpart_trade`, `send_them` (what this scope provides), `need_from_them`.
- `responsibility.typical` is a **prompt to confirm**, never an answer — furnish / install / connect splits are project-specific and are where coordination money is lost.
- Gate milestones: `procurement_release`, `underslab_rough_in`, `slab_pour`, `in_wall_rough_in`, `wall_close_in`, `above_ceiling_close_in`, `equipment_set`, `final_connection`.

---

## 7. Cascade and merge rules

### 7.1 Load order (lowest → highest precedence)

```
1. profiles/_global.yaml
2. profiles/<DD>/_division.yaml
3. section ancestors, general → specific:   12 30 00 → 12 35 00 → 12 35 53 → 12 35 53.13
4. overlays, by facility type (parent → child), filtered by `sections`
5. interfaces whose endpoints match the lineage (and facility filter)
6. project bindings (not merged): code-researcher findings, spec text location
```

Missing ancestors are allowed. They are listed under `coverage.missing` so a gap in the knowledge base is visible, not silent.

### 7.2 Rules

**M1 — Identity.** Keyed lists merge by `id`. Ids are unique within a file. Ids are scoped per list, but prefix them with the scope and list (`cw.` checks, `cw.fm.` failure modes, `cw.rh.` hooks, `cw.std.` standards, `cw.xf.` extract fields; `g.`, `d12.`, `lc.`, `hc.` likewise) so they never collide by accident and stay readable in findings.

**M2 — No accidental shadowing.** If a more specific layer reuses an inherited id without `override: true`, validation fails. Reusing an id is always a deliberate act.

**M3 — Override.** A section may restate an inherited item with `override: true`. Default `merge: patch`: the fields given replace the parent's, the rest are inherited. `merge: replace` swaps the whole item.

**M4 — Suppress, with a reason.** A section may turn off an inherited item with `suppress: [{id, reason}]`. The reason is required, and suppressed items stay visible in the compiled output under `suppressed`, so the reviewer sees what was turned off and why.

**M5 — Overlays only tighten.** Overlays add items and may `escalate` the severity of section items (upward only). They cannot override or suppress section items. A child overlay may override its parent overlay's items.

**M6 — Scalars.** `scope_summary` and `review_mode`: the most specific section layer that defines them wins. `element_types`: union down the lineage. `equivalents` and `legacy_numbers` are not inherited — what is true of casework in general is not true of laboratory casework.

**M7 — Provenance.** Every compiled item carries `_from` (the layer that defined it), `_status`, and `_patched_by` when overridden. A patched item takes the lower of the two statuses. Provenance tells a PE which file to edit when an item is wrong.

**M8 — Determinism.** The same inputs always produce the same output, ordered by layer and then by file order.

**K1, K2** (above) apply to every compiled context.

### 7.3 Compiled context (resolver output)

```yaml
query: {section: "12 35 53", facility_types: [healthcare.hospital]}
lineage: [global, "12", "12 30 00", "12 35 00", "12 35 53"]
coverage: {loaded: [...], missing: ["12 35 00"], overlays_loaded: [healthcare], overlays_missing: [healthcare.hospital]}
confidence_floor: draft
equivalents: [...]
scope_summary: ...
review_mode: per_element
element_types: [...]
submittals: [...]
review_checks: [...]          # each with _from, _status, _chain
failure_modes: [...]
standards: [...]
regulatory_hooks: [...]       # each with binding: {status, findings | instruction}
extract_fields: [...]
interfaces: [...]             # oriented to the queried section
suppressed: [...]
escalations: [...]
project: {spec_text: path or null, jurisdiction: summary or null}
warnings: [...]
```

`--format md` renders the same content compactly for a subagent prompt.

---

## 8. Where a lesson goes

When a PE flags a miss, the fix lands in the most general place where it is always true:

| The lesson is true… | Put it in |
|---|---|
| for every submittal | `_global.yaml` |
| for every section in the division | `_division.yaml` |
| for this scope anywhere | the section profile |
| only for a facility type | that overlay |
| only in a jurisdiction | code-researcher findings (not this layer) |
| only on this project | the project's issue registry |

Record it as a `failure_mode` with `source: project_incident` and the RFI or issue id, link it to the check that catches it (`caught_by`), and add the check if none exists. A miss with no catching check is a hole in the layer.

---

## 9. Migrating `reference/pe_expertise/scope-*.md`

Each scope file maps onto a division baseline:

| Scope file section | Profile field |
|---|---|
| Cross-Reference Triggers | `trace_to` on checks; `equivalents` |
| Absence Detection Checklist | `review_checks` with `kind: absence` |
| Sequencing Context | interface `gate`s |
| Coordination Overlaps | `interfaces` edges |

Until a division is migrated, its `_division.yaml` points at the scope file through `legacy_scope_file`, and the resolver returns that path so skills can still load it.

---

## 10. Validation

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/csi/csi_knowledge.py" validate
```

Errors (non-zero exit): YAML parse, missing required fields, bad enums, file name ≠ id, duplicate ids in a file, M2 shadowing, override or suppress of an id that isn't inherited, suppress without a reason, overlay override or suppress of section items, malformed section numbers.

Warnings: unknown `trace_to` terms, unknown submittal types and source families, `caught_by` ids that don't resolve to a check in the compiled context, `escalate` targets that exist nowhere in the layer. The summary line also counts files still at `draft`; `--strict` turns warnings into a failing exit for CI.
