# Review: `reference/pe_expertise/`

**Scope:** 25 files, 2,733 lines, ~39k tokens (`pe_behavior.md` 8.5k; 23 `scope-*.md` 0.5–3.5k each; `rfi_template.md`), plus the fork in `skills/pe-review/references/` (7 files, 358 lines).
**Question:** does this corpus make Claude Code act like an expert PE on any project, at the lowest token cost?
**Date:** 2026-10-03 · Branch: `feat/csi-knowledge-layer`

---

## 1. Verdict

The corpus has real expertise in it, but roughly a fifth of it. The rest is MasterFormat listings Claude already knows, the same rule restated per division, and code numbers stated as facts with no edition or jurisdiction behind them. Structurally it is dead: nothing in the plugin loads it, and the live copy (`pe-review/references/`) is a fork that has already drifted in both directions.

Recommendation: do not revise the files in place. Harvest the ~600 lines of genuine knowledge into the CSI knowledge layer (`reference/csi/`), retire `pe_expertise/` and the `pe-review` duplicates, and fill the gaps the corpus never had: failure modes, facility-type overlays for every common building type, contractor-designed-system handling, schedule-to-schedule reconciliations, and inspection gates. Details and a phased plan follow.

---

## 2. The grading test

Each line was sorted into one of four buckets:

| Bucket | Test | Verdict |
|---|---|---|
| **A. Behavior** | Something a PE *does* reflexively that Claude won't do unprompted (check submittal status before citing it; ask what gets buried) | Keep as procedure |
| **B. Tacit knowledge** | How a scope actually goes wrong, who typically furnishes/installs what, what is routinely missing from drawings, what must be inspected before cover | Keep, as structured data |
| **C. Already known** | MasterFormat numbers, what a trade does, which drawing shows what, code thresholds Claude can recall | Cut; costs tokens, adds nothing |
| **D. Risky as written** | Numbers unbound to code edition or jurisdiction; brand names; one project's condition stated as a universal rule; volatile figures (lead times) | Convert to a question bound to jurisdiction research, or cut |

---

## 3. Findings

### F1 — Orphaned, and forked

- No `SKILL.md`, script, or doc references `reference/pe_expertise/` (only the bridge added in the CSI layer yesterday). `pe_behavior.md` says it is "always loaded"; nothing loads it.
- `skills/pe-review/references/` is a condensed fork of `pe_behavior.md` §4–§7. It has **gained** items that never went back (STC box offset, fire-rated deflection track, VFD heat, NEC 700 vs 702, T-rated firestop, walk-in cooler, ICF embeds, PV flashing) and **lost** the most valuable column of §7, *Typical Split* (who usually furnishes / installs), keeping only the "common gap" question.
- `rfi_template.md` exists in three places (`pe_expertise/`, `pe-review/references/`, `templates/`), and `rfi-drafter` has its own `rfi-format.md`.
- Stale pointers: `scope-07` cites "the always-loaded CLAUDE.md" (replaced by `construction-guide`); `pe_behavior.md` §1/§8 point to a parent CLAUDE.md that no longer ships; §9 writes markdown to `.construction/agent_findings/`, which the current rules reserve for AgentCM's JSON findings; §8 is missing entirely (§7 → §9).

### F2 — About half the volume is bucket C

Measured across the 23 scope files (2,153 lines):

| Content | Lines | Share | Bucket |
|---|---|---|---|
| "Cross-Reference Triggers" sections | 488 | 23% | mostly C |
| of which `- Spec NN NN NN — Title` listings | 208 | 10% | C |
| "Sequencing Context" sections | 490 | 23% | B, but duplicated (F3) |
| "Absence Detection" checklists | 352 | 16% | B/D mix |
| "Coordination Overlaps" sections | 114 | 5% | B, duplicated (F3) |
| Headers, load-when boilerplate, blank | ~710 | 33% | — |

Specific redundancies:
- 208 lines list canonical MasterFormat section numbers. Claude knows them, and on a real project the spec index (`spec_index.yaml`) is the only list that matters; a canonical list anchors Claude to numbers the project may not use (casework in 06 41 00 vs 12 30 00 is the obvious case).
- "Check the submittal register / check the RFI log" is restated **86 times** (59 + 27). It is one global rule (`pe_review_rules.md` already states it once).
- The "Load when: query references brick, CMU, mortar…" blocks are keyword routing for a router that does not exist.

### F3 — No single home for a fact

The same gate or rule is written out in many files, so every load re-pays for it and edits land in one copy:

| Item | Files it appears in |
|---|---|
| Blocking before close-in | 11 |
| Mechanical ↔ electrical V/Ph/A match | 9 |
| Embeds / anchor bolts before pour | 8 |
| Hangers before fireproofing | 7 |
| Access-control wiring to frame before closure | 6 |
| Sill pan flashing | 6 |
| Perimeter firesafing at curtain wall | 6 |
| Floor drain in mech / elevator pit / WH room | 6 |

The coordination matrix exists three times (`pe_behavior` §5: 24 rows; `pe-review/coordination-matrix.md`: 29 rows; per-division "Coordination Overlaps" prose). The five sequencing chains in `pe_behavior` §3.2 are re-narrated in nearly every scope file.

### F4 — Hard numbers stated as facts (bucket D)

The files embed code thresholds, standards figures, and market figures with no edition, jurisdiction, or date. Claude can recall these anyway; writing them down creates a second source of truth that competes with `code-researcher`'s edition-bound findings, and some are wrong as written:

| As written | Problem |
|---|---|
| "Countertop exceeding 34" AFF without accessible section" (red flag §4.6) | 34" is the ADA work-surface / lavatory limit; sales and service counters are 36"; state codes and facility licensing can differ. This is exactly the class of miss that prompted this work: the number that governed came from a health-facility rule, not the drawings or ADA. |
| "Ungrouted single-wythe CMU does NOT achieve 2-hour fire rating" (pe-review red flags) | Depends on unit equivalent thickness and aggregate per the adopted code table; an 8" lightweight hollow unit can. A one-project condition promoted to a universal rule. |
| "Hot water recirculation (required per code for most commercial buildings)" | Energy codes limit dead-leg length/volume; recirculation is one way to comply. Overclaim. |
| "15-mil per ASTM E1745" (`pe_behavior`, `scope-03`, and the fork) | E1745 is the classification standard (Class A/B/C); 15-mil is a practice recommendation. Conflated. |
| "Steel 12–16 weeks", "CW 16–24 weeks", "switchgear 16–24 weeks", "elevators 16–24 weeks" | Market figures; switchgear has run far longer recently. Will mislead a schedule check. |
| "Movement joints sealed after minimum 28 days" | Not a standard; manufacturer cure times govern. |
| "Fire Trak or equal", "DensArmor or equal" (pe-review) | Brand names are spec-writing idioms, not knowledge. |
| "Spare panel capacity (typically 20%)" | Design convention; not checkable against anything. |
| Duct detectors ">2000 CFM", extinguishers "75' travel", GFP ">1000A", mirrors "40" max", grab bars "33–36"", cross-slope "≤2%" | Mostly right for a given edition, but unbound. |

The correct form for every one of these is a **question** whose number is resolved per project: *"Duct smoke detectors shown on every air handler above the adopted code's capacity threshold?"* → `regulatory_hook` → `code-researcher` finding with edition and citation. The static tables in `reference/ada_requirements.yaml` and `ibc_egress_tables.yaml` are the only place numbers belong, and they are at least labelled by edition.

### F5 — What the corpus never had

These are the gaps between "a good checklist" and "an expert PE", and none of them is facility-specific:

1. **Failure modes.** There is no field anywhere for *how this scope actually goes wrong in the field*. The closest things are the matrix's "What Fails" column and the 17 "Critical rule / Critical timing" paragraphs (PT tendon coring, roof drains before the roofer, AV rough-in missed at close-in, telecom skeleton in a design-build scope, existing conditions never as drawn). Those paragraphs are the best writing in the corpus and should become structured failure modes linked to the check that catches them.
2. **Facility-type overlays.** Requirements driven by building type cut across divisions (health licensing touches casework, finishes, plumbing, doors; a commercial kitchen touches 11, 21, 22, 23, 26, 09). The corpus has no mechanism for this at all. Needed for any project, not just healthcare: foodservice, laboratory, K-12 / higher-ed, multifamily residential (acoustic separation, Type A/B units, FHA), occupied-building renovation and phasing, high-rise, industrial / warehouse (ESFR, racks, docks), parking structures, data center / mission critical, public-works and federal (Buy American, prevailing wage, agency AHJs), historic (SHPO).
3. **Contractor-designed systems.** Sprinklers, fire alarm, structured cabling, curtain wall, PEMB, precast, cold-formed framing, MEP seismic bracing, shoring, SFRM thickness, elevators, rooftop supports, trusses are usually performance-specified and deferred submittals. A PE treats them differently (EOR acceptance, AHJ deferred-submittal list, permit timing). The corpus mentions delegated design in five files and never as a rule.
4. **Schedule-to-schedule reconciliations as data.** Mech ↔ elec equipment data, arch ↔ plumbing fixture counts, door schedule ↔ hardware sets ↔ plans, equipment ↔ utilities, lighting schedule ↔ RCP, civil ↔ plumbing at the building line. These are the checks Claude can actually *compute* (and AgentCM can query), and the MEP files describe them only in prose. The MEP files are the thinnest relative to risk, which matches where PEs have the least first-hand knowledge.
5. **Inspection and cover gates.** What must be inspected or tested before it is covered (special inspections, rough-in, above-ceiling, firestop, flood test, roofing manufacturer's inspection for warranty). Scattered as asides; never a list.
6. **Delivery-method context.** Design-build vs design-bid-build vs CM-at-risk changes who answers an RFI, who owns a coordination miss, and whether a "design gap" is the contractor's problem. Absent.
7. **Commercial consequence.** A PE classifies every finding by who pays and whether it blocks procurement or installation. `pe_review_rules.md` has Severity/Type/Priority; the knowledge layer has `owner`. Nothing teaches the classification.

### F6 — Format can't serve the use

- Prose organized by division can't be queried by section. A review of **12 35 53** gets the 53-line furnishings file with nothing lab-specific; a review of **07 84 00** firestopping gets all 251 lines of Division 07.
- No status or provenance. A reader can't tell a field-validated rule from a drafted one, or which file to edit when an item is wrong.
- No place for a project's lesson to land (§9's findings log is a session log, not a knowledge update), so the corpus can't get smarter.

### F7 — What is genuinely good (keep)

- `pe_behavior` §2 (RFI response classification; submittal status gates; "per contract documents" rule; substitution cascade; delegated design without EOR stamp) — bucket A, the best section in the corpus. Already condensed in `pe_review_rules.md`.
- §3.1 point-of-no-return framing and §3.3 look-back / look-forward — bucket A.
- §6 global verification (unresolved references, dimensional consistency, addenda check) — bucket A.
- §7 scope-gap tables **with** the Typical Split column — bucket B.
- About 60% of absence-checklist items, once numbers are stripped: slab depression depth = full assembly; waterstop at below-grade CJs; through-wall flashing with end dams at every horizontal interruption; soft joint under shelf angles; head-of-wall per partition type; firestopping installer named; every door mark → schedule → hardware set; sill pan before window; air barrier sealed before window; access panels at concealed devices; hazmat survey referenced; utility sizes/inverts matching at the building line; telecom rooms with power and cooling in the base design; AV rough-in before close-in.
- Red flags (§4) as a reflex list — bucket A/B — once de-duplicated against division content and stripped of numbers and brands.
- The "Critical rule" paragraphs — bucket B — as failure modes.

---

## 4. Determination

| Content | Lines (approx.) | Decision | Destination |
|---|---|---|---|
| Spec-number listings | 208 | **Cut** | Project `spec_index.yaml` is the list |
| Drawing-type cross-reference lines | ~190 | **Fold** into `trace_to` on checks | `profiles/*` |
| "Check register / RFI log" restatements | 86 | **Cut** | One rule in `pe_review_rules.md` |
| "Load when" keyword blocks | 23 | **Cut** | Resolver takes a section number |
| Absence checklists | 352 | **Keep ~60%**, numbers → hooks | `review_checks` (kind: absence), `regulatory_hooks` |
| Sequencing chains / POINT OF NO RETURN | 490 (+137 in `pe_behavior` §3.2) | **Keep ~25 gates once** | `interfaces/*` edge `gate`s + one `milestones.yaml` |
| Coordination overlaps + matrix ×3 | 114 + 24 + 29 rows | **Keep once** | `interfaces/*` edges |
| Scope-gap tables (§7) | 20 rows | **Keep with Typical Split** | `interfaces/*` `responsibility` |
| Red flags (§4 + pe-review) | 71 + 60 bullets | **Keep, dedupe, strip numbers/brands** | checks with `reflex: true` |
| RFI/submittal authority, global checks (§2, §6) | ~110 | **Keep** | `pe_review_rules.md` (procedure) |
| "Critical rule" paragraphs | 17 | **Convert** | `failure_modes` |
| Lead times, brand names, universalized one-offs | ~15 | **Cut** | — |
| §9 project learning | 67 | **Cut** | Superseded by `pe-findings` + issue registry |
| `rfi_template.md` ×3 | 75 | **Cut** | `rfi-drafter/references/rfi-format.md` |
| Sub-scope structure in 07/08/09/28 | — | **Becomes** section profiles | Cascade handles it |

Net: ~39k tokens of prose → a layer whose compiled context for one section is 1.5–4k tokens, loaded only for the section under review, with every number bound to a jurisdiction finding or absent.

---

## 5. Target structure

Everything lands in `reference/csi/` (schema in `reference/csi/SCHEMA.md`), with four additions to the schema:

1. **`reflex: true`** on a check. The resolver gains a `reflexes` command that compiles every reflex check across the layer into the always-on red-flag list. Red flags keep their home in the division that owns them; the list is a view, not a second copy.
2. **`milestones.yaml`** — the ordered construction sequence (`underslab_rough_in` → `slab_pour` → … → `final_connection`), each with `covers:` (what becomes inaccessible) and `inspect_before:` (what must pass first). Interface edges already carry `gate.milestone`; the resolver gains `milestone <name>` to emit "everything that must be verified before this cover", replacing §3.2's hand-written chains.
3. **`reconciliations`** on a section profile — pairs of documents and the fields that must agree (`schedule.mechanical_equipment ↔ schedule.electrical_panel: voltage, phase, mca, mocp`). This is the MEP depth the corpus lacks, and it is computable.
4. **`contractor_designed: typical | sometimes | never`** on a section, with a global check that fires on `typical`: EOR acceptance, deferred-submittal list, permit timing.

Two resolver conveniences: `--only checks,hooks,interfaces` so a skill loads only the slice its step needs (SOP §4 JIT rule), and a `dedupe` lint that flags near-identical check text across files (the "one home" rule, enforced).

Procedure stays in `skills/pe-review/references/pe_review_rules.md` (precedence, verification gates, output grading). `red-flags.md`, `coordination-matrix.md`, `absence-checklists.md`, `scope-gaps.md` are retired once their content is in the layer; `pe-review/SKILL.md` calls the resolver.

---

## 6. Additions (any project)

Priority order, by how often a PE meets it and how expensive the miss is:

| # | Addition | Form | Why it is not already in Claude |
|---|---|---|---|
| 1 | Failure modes for every migrated section | `failure_modes` seeded from Critical rules and matrix "What Fails"; PE-authored thereafter | Field-specific; the single highest-value field |
| 2 | Reconciliation pairs for Div 22/23/26/21/28/08/09/11 | `reconciliations` | Claude won't systematically cross-check schedules unless told which fields |
| 3 | Overlays: foodservice, laboratory, education, multifamily, occupied-renovation, high-rise, industrial, parking, data-center, public-works, historic | `overlays/*.yaml` | Cross-division requirements by building type have no home in any division file |
| 4 | Contractor-designed systems rule + per-section flag | `_global` check + `contractor_designed` | Deferred-submittal handling is procedural, not recalled |
| 5 | Milestones with `covers` and `inspect_before` | `milestones.yaml` | Makes point-of-no-return computable instead of narrated |
| 6 | Delivery-method field in project context + one `_global` note on how DB / DBB / CMAR change RFI and gap ownership | `project_context.yaml`, `_global` | Changes who a finding goes to |
| 7 | Finding classification (who pays; blocks procurement / install?) | `pe_review_rules.md` | Turns a list of findings into a PE's priorities |
| 8 | Division 00/01 as rulebook: substitution windows, submittal review periods, warranty start, allowances/alternates | `profiles/01/` | Already decent in `scope-01`; keep as the one division that is procedural |

Not added, deliberately: definitions, trade descriptions, MasterFormat tables, code section numbers (those come from `code-researcher`, bound to the project's edition), lead times.

---

## 7. Worked example — Division 07 firestopping

**Before** (`scope-07-thermal-moisture.md` §07F, 36 lines, loaded with the other 215 lines of Division 07): a spec listing, a six-item checklist with "Approved submittal (check register)", a four-step sequence, and one good sentence about trade assignment.

**After** (`profiles/07/07-84-00.yaml`, excerpt):

```yaml
review_checks:
  - id: fs.installer-named
    kind: absence
    reflex: true
    check: >
      The installing trade for firestopping is named in the contract documents
      (07 84 00 Part 1, Division 01, or the MEP sections). If no section names
      it, this is a scope gap, not an assumption.
    trace_to: [spec.part1, spec.part3]
    severity: high
    owner: gc
  - id: fs.listed-system-per-penetration
    kind: conformance
    submittal_types: [Product Data, Shop Drawings]
    check: >
      A listed system is identified for every penetration type that exists on
      the project (pipe, insulated pipe, conduit, cable tray, duct, combined),
      for each rated assembly type it passes through; through-penetration and
      membrane-penetration conditions are distinguished.
    trace_to: [drawings.plans, spec.part2]
    severity: high
    owner: subcontractor

regulatory_hooks:
  - id: fs.rh.t-rating
    topic: firestop-t-rating-threshold
    question: >
      Which penetrations require a T rating in addition to an F rating under
      the adopted building code, and does the submittal provide it there?
    source_families: [building_code]
    severity: medium

failure_modes:
  - id: fs.fm.closed-before-firestop
    what_happens: Second-side gypsum board closes rated walls before firestopping is installed and inspected
    consequence: Destructive investigation of finished walls to verify or install; one of the costliest rework patterns
    caught_by: [fs.installer-named]
    source: industry_practice
```

and one edge in `interfaces/div-07.yaml`:

```yaml
  - id: if.firestop-close-in
    a: ["07 84 00"]
    a_trade: Firestopping
    b: ["09 29 00", "09 22 16"]
    b_trade: Gypsum board / framing
    a_provides: Confirmation each rated-wall penetration is firestopped and inspected
    b_provides: Close-in schedule by area; no second-side board until confirmed
    gate: {milestone: wall_close_in, inspect_before: [firestop_inspection]}
    severity: critical
    failure: Rated walls closed over unfirestopped penetrations
```

What changed: the T-rating threshold became a question bound to the project's code edition instead of ">4 inch / >16 sq in" stated as fact; "who installs" became an interface responsibility the review routes to a sub; the failure mode is linked to the check that catches it; "check register" is gone because it is global; and a 07 84 00 review loads ~40 lines instead of 251.

---

## 8. Migration plan

| Phase | Work | Acceptance |
|---|---|---|
| 0 | Retire the duplicates: delete two `rfi_template.md` copies; add `reference/pe_expertise/README.md` marking the directory deprecated in favor of `reference/csi/`; fix the three stale pointers | `grep` finds one RFI template |
| 1 | Schema additions (§5): `reflex`, `milestones.yaml`, `reconciliations`, `contractor_designed`; resolver `reflexes`, `milestone`, `--only`, `dedupe`; `_global` gains the contractor-designed check | `validate` passes; `reflexes` emits the de-duplicated red-flag list |
| 2 | Migrate divisions in risk order, one PR each: **07, 03, 08, 09**, then **22, 23, 26** (with reconciliations), then 05, 04, 06, 10, 11, 21, 28, 14, 27, 31/32/33, 01, 02, 13. Each: `_division.yaml`, 2–6 section profiles, interface edges, Critical rules → failure modes, every number → hook or cut. All at `status: draft` | `validate --strict` passes; zero bare numbers (lint); A/B eval per SOP §7 on the Holabird set: `pe-review` with the compiled context vs. with the old scope file |
| 3 | Overlays (§6 #3), two or three per PR, starting with foodservice and laboratory | Each overlay's hooks resolve to `code-researcher` topics on a real project |
| 4 | `pe-review` and the submittal-review skill read from the resolver; delete `pe_expertise/` and the four retired `pe-review` reference files | Nothing references the deleted paths; evals unchanged or better |
| 5 | PE review passes per division → `status: pe_reviewed`; real misses become `source: project_incident` failure modes and eval regression cases | Confidence floor on compiled output rises from `draft` |

Rough effort: Phase 1 is a day; each division in Phase 2 is a few hours of migration plus PE review time; overlays are half a day each for a draft.

---

## 9. Authoring rules going forward

1. **One home.** A fact lives in the most general file where it is always true, and nowhere else. The `dedupe` lint enforces it.
2. **No bare numbers.** A threshold, dimension, or duration appears only as a `regulatory_hook` question or in an edition-labelled table under `reference/`. Lead times never.
3. **Questions, not answers.** A check says what to verify and where (`trace_to`). The project documents answer; a conflict is surfaced, never resolved.
4. **Every failure mode is caught.** `caught_by` must resolve; a miss with no catching check is a hole to fill, not a note.
5. **Status travels.** Nothing leaves `draft` without a named PE reviewer; compiled output always shows the floor.
6. **Project lessons go up, not sideways.** A miss on one project becomes a failure mode in the most general true place, tagged with its source, never a universal rule by default.
7. **The value test.** Before adding a line: would an expert PE do this and would Claude not do it unprompted? If Claude already knows it, leave it out.
