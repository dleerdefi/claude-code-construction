# CSI Knowledge Layer — Profile Schema and Merge Rules

**Status:** Draft v1 (`schema_version: 1`)
**Location:** `reference/csi/` (shared domain knowledge, read via `${CLAUDE_PLUGIN_ROOT}/reference/csi/`)
**Resolver:** `scripts/csi/csi_knowledge.py` (`resolve`, `reflexes`, `milestone`, `validate` — §11)

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
├── milestones.yaml              ← what each construction milestone covers or locks (§6.1)
├── profiles/
│   ├── _global.yaml             ← rules for every submittal (Division 01 practice)
│   ├── 07/
│   │   ├── _division.yaml       ← Division 07 baseline
│   │   ├── 07-10-00.yaml        ← Dampproofing and Waterproofing
│   │   ├── 07-20-00.yaml        ← Thermal Protection (wall assembly as a tested whole)
│   │   ├── 07-27-00.yaml        ← Air Barriers
│   │   ├── 07-50-00.yaml        ← Membrane Roofing
│   │   ├── 07-81-00.yaml        ← Applied Fireproofing
│   │   ├── 07-84-00.yaml        ← Firestopping
│   │   └── 07-92-00.yaml        ← Joint Sealants
│   └── 12/
│       ├── _division.yaml       ← Division 12 baseline (seeded)
│       ├── 12-30-00.yaml        ← Casework
│       └── 12-35-53.yaml        ← Laboratory Casework
├── overlays/
│   └── healthcare.yaml          ← facility-type requirements that cut across divisions
└── interfaces/
    ├── div-07.yaml              ← coordination edges between sections
    └── div-12.yaml
```

File name = section id with hyphens (`12 35 53` → `12-35-53.yaml`; `12 35 53.13` → `12-35-53.13.yaml`). Division baselines are `profiles/<DD>/_division.yaml`. Overlay file name = facility type (`healthcare.hospital.yaml`). Interface files are grouped for authoring convenience only; the resolver loads all of them.

---

## 3. Common header (every file)

```yaml
schema_version: 1
kind: global | division | section | overlay | interfaces | milestones
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
| `same_as` | section id | n/a | Section only. The same scope specified under another number (`06 41 00` → `12 30 00`): `resolve` compiles the target's lineage, then this file's own items, and matches interfaces on both numbers |
| `legacy_numbers` | list | not inherited | MasterFormat 1995 numbers that map to this profile (`"12300"`). The resolver accepts them as input |
| `legacy_scope_file` | path | n/a | Division only. Bridge to the archived `reference/pe_expertise/scope-*.md` until the division is migrated |
| `review_mode` | `per_element` \| `package` | most specific wins | Whether the review skill fans out one worker per element (elevation, item, tag) or reviews the package whole |
| `contractor_designed` | `typical` \| `sometimes` \| `never` | most specific wins | Whether this scope is usually performance-specified and designed or selected by the contractor. Unset compiles as `unknown`. Drives `applies_if` (§4.5) |
| `element_types` | list | union | The units of fan-out (`casework_elevation`, `equipment_item`, …) |
| `submittals` | keyed list | by `id` | Submittal types expected and what each must show |
| `review_checks` | keyed list | by `id` | Verification targets (see 4.1) |
| `reconciliations` | keyed list | by `id` | Documents that must agree, field by field (see 4.4) |
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
    gate: wall_close_in          # optional: milestone by which it must be resolved (§6.1)
    reflex: false                # optional: true = always on, even when unrelated to the question
    scope: element               # optional: element | package (see below)
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

| Group | Terms |
|---|---|
| Contract | `contract.general_conditions`, `spec.division_01` |
| Spec | `spec.part1`, `spec.part1_submittals`, `spec.part2`, `spec.part2_manufacturers`, `spec.part3` |
| Drawings | `drawings.plans`, `drawings.enlarged_plans`, `drawings.interior_elevations`, `drawings.exterior_elevations`, `drawings.building_sections`, `drawings.wall_sections`, `drawings.details`, `drawings.material_legend`, `drawings.roof_plan`, `drawings.rcp`, `drawings.life_safety`, `drawings.demolition`, `drawings.site`, `drawings.civil`, `drawings.landscape`, `drawings.foundation`, `drawings.structural`, `drawings.fire_protection`, `drawings.plumbing`, `drawings.mechanical`, `drawings.controls`, `drawings.electrical`, `drawings.single_line`, `drawings.riser_diagrams`, `drawings.fire_alarm`, `drawings.technology`, `drawings.security`, `drawings.lab_gas`, `drawings.foodservice`, `drawings.equipment`, `drawings.storage_racks`, `drawings.revision_blocks` |
| Schedules | `schedule.casework`, `schedule.casework_hardware`, `schedule.finish`, `schedule.partition_type`, `schedule.door`, `schedule.door_hardware`, `schedule.window`, `schedule.signage`, `schedule.toilet_accessories`, `schedule.equipment`, `schedule.foodservice_equipment`, `schedule.plumbing_fixture`, `schedule.mechanical_equipment`, `schedule.electrical_panel`, `schedule.lighting_fixture`, `schedule.structural`, `schedule.lintel`, `schedule.master` |
| Reports | `report.geotechnical`, `report.energy_compliance`, `report.hazmat_survey`, `report.existing_conditions`, `report.commissioning`, `report.acoustical`, `report.stormwater`, `report.utility_requirements`, `report.radiation_shielding`, `report.chemical_inventory`, `report.risk_assessment`, `report.basis_of_design`, `report.wind_tunnel`, `report.preservation_approval` |
| Registers | `register.submittal_log`, `register.rfi_log`, `register.asi_bulletin_log`, `register.substitutions`, `register.special_inspections` |
| Other submittals | `submittals.approved`: another section's approved shop drawings or product data this submittal must fit (the approved sink a casework top is cut for, the embed plan a steel connection lands on) |

The validator warns on anything else; add new terms here first.

**`owner`** says who resolves a finding. It is how the output separates "sub must fix" from "design team must answer" (an RFI candidate).

**`gate`** names the milestone by which the finding has to be resolved: the last moment it is still cheap. It must be an id in `milestones.yaml`. `milestone --id <gate>` lists every check gated there (§11).

**`scope`** says whether the check is answered once per element (each elevation, item, mark) or once for the whole package. Unset, it compiles as `package` for global and division checks and as `element` for section and overlay checks when the section's `review_mode` is `per_element`. Set it when that default is wrong. `submittal-review`'s coverage gate expects one answer per element × element-scope check.

**`reflex: true`** marks the red flags: checks a PE notices while looking at a drawing for an unrelated reason. They stay in the profile that owns them; `reflexes` compiles them into the always-on list (§11), so the list is a view, never a second copy. Use it sparingly: the list loses its value if it grows past what a reviewer can hold in mind.

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

`source_families` seeds code-researcher's Pass 2:

| Group | Families |
|---|---|
| Model codes | `building_code`, `building_code_seismic`, `fire_code`, `plumbing_code`, `mechanical_code`, `fuel_gas_code`, `electrical_code`, `elevator_code`, `energy`, `accessibility` |
| Agencies | `health_facility_licensing`, `fgi_guidelines`, `food_code`, `public_health` (pools and other local health rules), `pharmacy`, `radiation_control`, `occupational_safety`, `boiler_pressure_vessel`, `environmental`, `historic_preservation` |
| Utilities and public works | `public_works` (municipal utility and right-of-way standards), `utility_service_rules` (the serving utility's service requirements) |
| Owner and funding | `owner_insurer_standards`, `public_funding` (conditions attached to public money), `federal_security_criteria` |

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
    caught_by: [cw.in-wall-support]      # check, reconciliation or interface ids that catch it
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

### 4.4 `reconciliations`

Documents that must agree, field by field. These are the checks Claude can compute rather than read: two schedules, a schedule and a plan, a roof plan and the plumbing drawings. Each one names the documents, the key that pairs their rows, and the fields that must match.

```yaml
reconciliations:
  - id: rf.rc.drains
    between: [drawings.roof_plan, drawings.plumbing]     # two or more trace_to terms
    key: Drain or scupper location                       # what pairs a row in one with a row in the other
    fields: [count, location, size, primary or overflow, discharge route]
    check: >
      Each primary and overflow drain on the roof plan appears on the plumbing
      drawings at the same location and size, with overflow routed independently.
    severity: high
    owner: design_team
    gate: roof_membrane           # optional
    reflex: true                  # optional
```

A mismatch is a finding with both sources cited; which document governs is the design team's call (K1). Mechanical ↔ electrical equipment data (`schedule.mechanical_equipment` ↔ `schedule.electrical_panel`: voltage, phase, MCA, MOCP) is the canonical example for the MEP divisions.

### 4.5 `applies_if`

Any keyed item may carry a condition on the compiled section's facts. Items whose condition fails are dropped from the compiled context and listed under `not_applicable`.

```yaml
  - id: g.contractor-designed
    applies_if: {contractor_designed: [typical, sometimes]}
```

Supported keys: `contractor_designed` (`typical`, `sometimes`, `never`, `unknown`) and `review_mode` (`per_element`, `package`). This keeps a global rule in one place while it fires only on the sections it concerns.

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
- `gate.milestone` must be an id in `milestones.yaml`. `gate.inspect_before` (optional) lists inspections specific to this interface, on top of the milestone's own.
- `reflex: true` on an edge puts it in the always-on list.
- `failure` is for an interface no failure mode covers. When a profile's failure mode names the edge in `caught_by`, leave `failure` off the edge so the consequence has one home; `resolve` attaches that failure mode's text to the edge when the review comes from the other side, and `validate` lints an edge that repeats it.
- An endpoint matches its own lineage: `26 05 00` reaches `26 05 33` but not `26 24 16`. Use the division (`26`) when the edge concerns the whole trade, or name the specific sections.

### 6.1 Milestones (`milestones.yaml`)

One ordered list of the moments that cover work or lock a decision. Each has `covers` (what becomes inaccessible or fixed) and `inspect_before` (what has to pass first). Checks, reconciliations and interface edges point at a milestone through `gate`; nothing is listed under a milestone by hand. This replaces narrated sequencing chains: `milestone --id wall_close_in` compiles the edges, checks, reconciliations and failure modes due before close-in, from wherever they live.

```yaml
milestones:
  - id: wall_close_in
    title: Second-side wall board
    covers: [In-wall piping, conduit, low-voltage cabling and boxes, ...]
    inspect_before: [In-wall rough-in inspections by the AHJ, ...]
```

The order is approximate and applies within one area of the building. Add a milestone only when an existing one cannot carry the gate.

`inspect_before` lists formal hold points only: AHJ inspections, special inspections, third-party and manufacturer inspections, surveys. Coordination items compile from gates and are never restated here. Concealment is literal: penetration firestopping in gypsum walls is installed after both faces are boarded and is concealed at `above_ceiling_close_in`, not at `wall_close_in`.

---

## 7. Cascade and merge rules

### 7.1 Load order (lowest → highest precedence)

```
1. profiles/_global.yaml
2. profiles/<DD>/_division.yaml
3. section ancestors, general → specific:   12 30 00 → 12 35 00 → 12 35 53 → 12 35 53.13
4. overlays, by facility type (parent → child), filtered by `sections`
5. interfaces whose endpoints match the lineage (and facility filter)
6. applies_if filtering against the compiled section facts
7. project bindings (not merged): code-researcher findings, spec text location
```

Missing ancestors are allowed. They are listed under `coverage.missing` so a gap in the knowledge base is visible, not silent.

### 7.2 Rules

**M1 — Identity.** Keyed lists merge by `id`. Ids are global: one id, one file (an `override` restates an inherited id on purpose), and edge ids are unique across interface files. Conventions for new divisions are in `AUTHORING.md` §4. Ids are scoped per list, but prefix them with the scope and list (`cw.` checks, `cw.fm.` failure modes, `cw.rh.` hooks, `cw.std.` standards, `cw.xf.` extract fields; `g.`, `d12.`, `lc.`, `hc.` likewise) so they never collide by accident and stay readable in findings.

**M2 — No accidental shadowing.** If a more specific layer reuses an inherited id without `override: true`, validation fails. Reusing an id is always a deliberate act.

**M3 — Override.** A section may restate an inherited item with `override: true`. Default `merge: patch`: the fields given replace the parent's, the rest are inherited. `merge: replace` swaps the whole item.

**M4 — Suppress, with a reason.** A section may turn off an inherited item with `suppress: [{id, reason}]`. The reason is required, and suppressed items stay visible in the compiled output under `suppressed`, so the reviewer sees what was turned off and why.

**M5 — Overlays only tighten.** Overlays add items and may `escalate` the severity of section items (upward only). They cannot override or suppress section items. A child overlay may override its parent overlay's items.

**M6 — Scalars.** `scope_summary`, `review_mode` and `contractor_designed`: the most specific section layer that defines them wins. `element_types`: union down the lineage. `equivalents` and `legacy_numbers` are not inherited — what is true of casework in general is not true of laboratory casework.

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
contractor_designed: unknown
element_types: [...]
submittals: [...]
review_checks: [...]          # each with _from, _status, _chain
reconciliations: [...]
failure_modes: [...]
standards: [...]
regulatory_hooks: [...]       # each with binding: {status, findings | instruction}
extract_fields: [...]
interfaces: [...]             # oriented to the queried section
suppressed: [...]
escalations: [...]
not_applicable: [...]         # ids dropped by applies_if
project: {spec_text: path or null, jurisdiction: summary or null}
warnings: [...]
```

`--format md` renders the same content compactly for a subagent prompt. `--only checks,hooks,interfaces` keeps just the slices a step needs (§11).

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

## 9. Migrating the `reference/pe_expertise/` archive

The archive stays untouched as the A/B baseline (`docs/PE_EXPERTISE_REVIEW.md`). Each division is harvested into the layer:

| Archive content | Destination |
|---|---|
| Spec-number listings in Cross-Reference Triggers | Dropped: the project's spec index is the list |
| Drawing types in Cross-Reference Triggers | `trace_to` on checks |
| Absence Detection Checklist | `review_checks` (`kind: absence`); numbers become `regulatory_hooks` |
| Sequencing Context, POINT OF NO RETURN | `gate` on checks and edges, against `milestones.yaml` |
| Coordination Overlaps, matrix rows, scope-gap tables | `interfaces` edges with `responsibility` |
| "Critical rule" paragraphs | `failure_modes` linked by `caught_by` |
| Red flags | checks with `reflex: true`, in the division that owns them |
| Lead times, brand names | Dropped |

Until a division is migrated, its `_division.yaml` may point at the archived scope file through `legacy_scope_file`, and the resolver returns that path. Division 07 is migrated; Division 12 is seeded and still bridged.

---

## 10. Validation

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/csi/csi_knowledge.py" validate
```

Errors (non-zero exit): YAML parse, missing required fields, bad enums, file name ≠ id, duplicate ids in a file, M2 shadowing, override or suppress of an id that isn't inherited, suppress without a reason, overlay override or suppress of section items, malformed section numbers, unknown gate milestones, `reflex` or `gate` on lists other than checks and reconciliations, unsupported `applies_if` keys or values, reconciliations naming fewer than two documents.

Warnings: unknown `trace_to` terms, unknown submittal types and source families, `caught_by` ids that don't resolve to a check, reconciliation or interface in the compiled context, `escalate` targets that exist nowhere in the layer.

Lint (authoring rules, §12):
- **Bare numbers.** A dimension, rating, duration, percentage, ratio or R-value in authored text (checks, questions, failure modes, edges, milestones). Section numbers and standard designations are ignored. Turn the number into a `regulatory_hook` question, or point at the project document that states it.
- **Near-duplicates.** Two checks, reconciliations, failure modes or hooks whose wording is nearly the same. Keep one home.

The summary line counts errors, warnings, lint and files still at `draft`. `--strict` fails on warnings and lint too; use it in CI.

---

## 11. Commands

```bash
PY="${CLAUDE_PLUGIN_ROOT}/bin/construction-python"; KB="${CLAUDE_PLUGIN_ROOT}/scripts/csi/csi_knowledge.py"

"$PY" "$KB" resolve --section "07 84 00" --project . --format md              # one section, full context
"$PY" "$KB" resolve --section "07 84 00" --project . --only checks,hooks       # just the slices a step needs
"$PY" "$KB" reflexes --project . --format md                                   # always-on checks for this project
"$PY" "$KB" milestone --format md                                              # the milestone list
"$PY" "$KB" milestone --id wall_close_in --project . --format md               # everything due before close-in
"$PY" "$KB" topics                                                             # hook topics in use: reuse before inventing
"$PY" "$KB" validate --strict
"$PY" "$KB" validate --strict --focus "profiles/08/" --focus "div-08"         # only messages about these files
```

- `--only` slices: `checks`, `reconciliations`, `hooks`, `interfaces`, `failures`, `submittals`, `standards`, `extract`.
- `--types "Shop Drawings,Product Data"` drops checks that apply only to other submittal types (labels from `submittal-log-generator`'s taxonomy).
- `reflexes` and `milestone` are cross-layer views. They list each item where it lives; overrides and suppressions only apply inside `resolve`.
- With `--project`, both views keep only what the project specifies: profiles related to a section in `.construction/skills/spec_text/`, and interfaces whose two trades are both on the project. Without extracted spec text they show the whole layer and say so.
- `--output <file>` writes a versioned file instead of printing.

---

## 12. Authoring rules

The full process for writing a division is in `AUTHORING.md`. In short:

1. **One home.** A fact lives in the most general file where it is always true, and nowhere else.
2. **No bare numbers.** Thresholds, dimensions and durations are `regulatory_hook` questions or come from the project documents. Lead times never appear.
3. **Questions, not answers.** A check says what to verify and where (`trace_to`); the project documents answer it.
4. **Every failure mode is caught.** `caught_by` must resolve. A miss with no catching check is a hole to fill.
5. **Status travels.** Nothing leaves `draft` without a named PE reviewer.
6. **The value test.** Add a line only if an expert PE would do it and Claude would not do it unprompted.
