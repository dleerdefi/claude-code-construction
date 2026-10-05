> **Provenance.** This audit was run on branch `feat/csi-knowledge-layer` at commit `265bdef` (2026-10-03). It audited the CSI knowledge layer, which was not merged; that layer and every file this report cites under `reference/csi/` and `scripts/csi/` exist only on that branch and on the `csi/*` branches. This copy keeps the report, the classification protocol and the twelve classification tables (`docs/audit/csi-layer/marginal-value/`). Those tables list every compiled item with its verdict, including the roughly 60 items that changed a review. The other evidence (closed-book baselines, compiled contexts, ablation fixtures and reviews, the eval results, the correctness sample, and the gate and code reviews) is at `docs/audit/csi-layer/` on commit `265bdef`. What was decided as a result is in `docs/SUBMITTAL_REVIEW_DECISIONS.md`.

# Audit: CSI knowledge layer and submittal-review skill (PRs #5–#13)

Scope: pull requests #5 through #13 in `dleerdefi/claude-code-construction`, audited at the merged head of `feat/csi-knowledge-layer` (`640ab78`; one later resolver commit, `cca1d6f`, landed during the audit and is noted at R6). Read-and-test audit; nothing in the PRs was changed. Date: 2026-10-03.

Everything below is separated into **measured** (a number produced by a script, an eval run or a blind scorer) and **judged** (an opinion formed from reading). Subagent runs used this session's model; a weaker model might lean on a checklist more than this one did, and that caveat applies to every behavioral result here.

---

## 1. Verdict

The knowledge layer is 94% restatement of what Claude already produces closed-book, 5% genuinely new, and under 1% wrong; in blind ablation on three realistic submittals the reviews run **without** the layer caught the same planted defects and were preferred by the blind scorer in all three cases for carrying less noise, and the shipped eval passes 9/9 graders with the layer emptied down to `_global.yaml`. The value in this stack is the review **procedure** (trace the CDs first, inventory the package both ways, cite both sides of every finding, keep code questions open, route to trades with a gate) and that procedure works without the 290 YAML files. Merge the skill (PR #13) after fixing its gate bugs and its eval; do not merge the knowledge PRs as they stand, and rebuild them as a much smaller "delta" layer of the roughly 60 items this audit found to change a review.

---

## 2. Per-PR verdict

| PR | Content | Verdict | Evidence | What to cut or fix |
|---|---|---|---|---|
| #5 | Schema, resolver, milestones, Division 07 | **Rework** | Resolver has three high-severity defects (R1–R3 below); `validate` takes 25–34 s; 07 54 00 compiles with 7% new items and misses the thermoplastic-specific checks the baseline had; all 293 files are `status: draft` | Keep cascade, gates and two-sided edges. Delete `legacy_numbers` (used once), `same_as` (hides the alias's division baseline), `applies_if` (34 uses, 28 in one file), `escalate`, `override/merge` (13 uses). Fix upward edge matching (R3) instead of adding edge `suppress`. Memoise `lineage()`/`normalize()` (measured 22.7 s → 11.5 s) and cache the edge-failure index (resolve 1.9 s → ~0.1 s) |
| #6 | Divisions 01, 02, 31–33 | **Trim** | Division 01 global checks are the only thing the empty-layer eval had, and it passed 9/9; the 01 25 00 / 01 78 00 profiles cover substitutions and closeout that the skill itself never uses; 31–33 were not exercised by any test here and keep non-standard id prefixes that AUTHORING §4 was widened to legitimise | Keep `_global.yaml` and the 01 25 00 / 01 33 00 / 01 78 00 profiles only if the skill grows a substitution or closeout path. Hold 02 and 31–33 until a sitework submittal case exists |
| #7 | Divisions 03, 04, 05 | **Trim** | Best section in the marginal test is 03 30 00 at 10.4% new, almost all of it cross-trade cast-in edges (`if.03-cold-storage-floors`, `if.03-grounding-electrode`, `if.03-pile-caps`, `03cip.rc.depressions`). 05 51 00 is 3.9% new, inherits a column anchor-rod edge that is wrong for stairs (`if.03-steel-anchorage`), and needs 16 `suppress` lines to be readable | Keep `interfaces/div-03.yaml` and the 03 30 00 reconciliations. Stop deriving stairs and railings from 05 50 00 |
| #8 | Divisions 06, 08, 09, 10, 12 | **Trim hard** | 12 35 53 compiles 97 items of which **1** is new (`edu.agency-approvals`, from an overlay) and one is wrong for the section (`if.10-counter-dispensers`, a vanity routing). 08 71 00: 6% new, mis-titles BHMA A156.28, and over-states power operators in `08hw.accessible-operation`. 09 21 16: 6% new | Keep the six 09 21 16 (b) items (rated-wall continuity hook, acoustic adjacency reconciliation, return-air transfers, recessed items in rated walls, access doors, operable-partition barrier) and the 08 71 00 `if.08-door-airflow` and `d08.rc.rated-openings`. Everything else in 12 30 00 / 12 35 53 is already in Claude's baseline |
| #9 | Divisions 11, 13, 14 | **Trim** | 11 40 00: 5.4% new, zero wrong, the new items are scope-orphan interfaces (freezer underfloor heat, sprinklers inside walk-ins, who pipes indirect waste, hand-sink accessories). All 12 regulatory hooks were already in the baseline. In the foodservice ablation the layer did not change what was caught | Keep the five 11 40 00 (b) items and `if.11-stage-fly-space`, `if.11-stage-fire-curtain`. Drop the rest |
| #10 | Divisions 21, 22, 23 | **Rework** | 21 13 13: 3.9% new, and a clean-agent releasing-panel edge (`if.21-release-control`) leaks into a wet-pipe review. 22 40 00: 1.5% new, two education-overlay items about cladding risk category land in a plumbing fixture package. 23 74 13 has no profile; it compiles under the 23 70 00 title with AHRI 1350 (a central-station casing standard) listed for packaged RTUs; in the RTU ablation the with-layer review had more false findings and 18.8% noise rows versus 1.5% | Write real profiles for the three most-submitted sections (22 40 00 fixtures, 23 74 13 RTUs, 21 13 13) with the reverse-gap items from §5 of each classification, or drop the division until then |
| #11 | Divisions 26, 27, 28 | **Trim** | 26 24 16: 6% new, but all six come from division-level hooks and interfaces (ERRCS circuit, telecom room power, feeder GFP, arc-energy reduction, isolated neutral, plans-vs-schedule). 28 46 00: 4.7% new, all four are routings (stage curtain release, ERRCS monitoring, releasing panels, coiling fire doors). `28 31 00` resolves to intrusion detection with a prose warning | Keep `interfaces/div-26.yaml`, `div-27.yaml`, `div-28.yaml` and the five 26 hooks. Add a hard alias for the 2004-numbered fire alarm section |
| #12 | 15 facility overlays | **Rework** | `education.k12` leaks into every section: storm-shelter and risk-category items appeared in concrete, stairs, plumbing fixture, door hardware and RTU compiles (two of the eight (c) items). The foodservice overlay's hooks were all already in the baseline. The one overlay item that changed a review (`edu.agency-approvals`) appears three times (check, hook, failure mode) | Keep `healthcare*`, `foodservice`, `laboratory` with per-item `sections` globs tightened to the trades they affect. Hold the other eleven until a test case needs them |
| #13 | `submittal-review` skill, scripts, eval | **Keep, with fixes before merge** | SOP-compliant (196 lines, frontmatter, allowlist, quoted paths, no `/tmp`, `agents/openai.yaml`, deliverables outside `.construction/`). Eval passes 9/9 with and without the layer. `check_coverage.py` reports 100% coverage on rows still `todo`; context is compiled before the facility-type checkpoint and a re-run writes `context_v2.yaml` that the gate never reads. PR body's claim "tree identical to the original feature branch" was false at `640ab78` (11-line resolver diff) and is true again at `cca1d6f` | Fix C1 and C7, add validation of row/element/finding ids (C2–C4), add an eval case whose graders need a layer item, and make the empty-layer run a reported baseline arm |

---

## 3. Test results

### 3.1 Marginal value of the knowledge (measured; classification judged by a blind subagent per section)

Method: for each of 12 sections a fresh subagent with no file access wrote an expert closed-book checklist; the section was compiled with `csi_knowledge.py resolve --facility education.k12` (plus `foodservice` for 11 40 00); a third subagent classified every compiled item as (a) already in the baseline, (b) new, correct and review-changing, (c) wrong or misleading, (d) true but would not change a review.

| Section | Compiled items | a | b | c | d | b share | (a)+(d) share |
|---|---|---|---|---|---|---|---|
| 03 30 00 Cast-in-place concrete | 106 | 74 | 11 | 0 | 21 | 10.4% | 89.6% |
| 05 51 00 Metal stairs | 77 | 56 | 3 | 1 | 17 | 3.9% | 94.8% |
| 07 54 00 Thermoplastic roofing (via 07 50 00) | 71 | 52 | 5 | 0 | 14 | 7.0% | 93.0% |
| 08 71 00 Door hardware | 84 | 60 | 5 | 2 | 17 | 6.0% | 91.7% |
| 09 21 16 Gypsum board assemblies | 100 | 66 | 6 | 0 | 28 | 6.0% | 94.0% |
| 11 40 00 Foodservice equipment | 92 | 82 | 5 | 0 | 5 | 5.4% | 94.6% |
| 12 35 53 Laboratory casework | 97 | 80 | 1 | 1 | 15 | 1.0% | 97.9% |
| 21 13 13 Wet-pipe sprinklers | 128 | 91 | 5 | 1 | 31 | 3.9% | 95.3% |
| 22 40 00 Plumbing fixtures | 66 | 52 | 1 | 2 | 11 | 1.5% | 95.5% |
| 23 74 13 Packaged RTUs (via 23 70 00) | 98 | 68 | 5 | 1 | 24 | 5.1% | 93.9% |
| 26 24 16 Panelboards (via 26 24 00) | 100 | 62 | 6 | 0 | 32 | 6.0% | 94.0% |
| 28 46 00 Fire detection and alarm | 86 | 66 | 4 | 0 | 16 | 4.7% | 95.3% |
| **Total** | **1,105** | **809** | **57** | **8** | **231** | **5.2%** | **94.1%** |

(a)+(d) dominate in every section. The 57 (b) items cluster in three kinds: cross-trade interface edges a specialist reviewer does not think of (freezer underfloor heat, Ufer ground, sprinklers inside walk-ins, return-air transfers through rated walls, ERRCS power and monitoring), code questions phrased as questions (rated-wall continuity, feeder GFP, arc-energy reduction, energy-recovery trigger, refrigerant GWP by install date), and a few constructability checks (galvanizing vent holes, feature-stair vibration, ELD conductive layer).

Best (b) items, quoted from the compiled output:

- `03cip.rc.depressions`: "Every area with a thicker floor assembly (thick-set tile, tile over a waterproofing or crack-isolation membrane, terrazzo, recessed entrance mats, shower floors and sloped beds to floor drains, walk-in coolers) has a structural depression equal to the full assembly depth over its full extent."
- `if.03-cold-storage-floors`: "Underfloor heat under freezers on grade — typical furnish 11 41 00 or 13 21 26 / install the electrical or refrigeration trade … If missed: Freezer built on grade without underfloor heat, or with heating cable never energized or monitored."
- `if.11-walk-in-sprinklers`: "Heads inside each box where required (dry type in freezers) and above the box, located before panels are cut."
- `09gb.rh.rated-wall-continuity`: "For each kind of rated wall on this project … must it run to the floor or roof deck above under the adopted code, or may it stop at a rated ceiling membrane?"
- `if.08-door-airflow`: "Doors the air design relies on for transfer or return air, room pressure relationships, and stair and smoke-zone pressure differences that set door opening and closing forces."
- `26ds.grounding-neutral`: "The neutral is bonded to ground only at the service and at each separately derived system; downstream panelboards have isolated neutrals."
- `21wb.component-pressure`: "Where static pressure, fire pump churn or fire department pumping through the connection can exceed standard component ratings, the submittal shows high-pressure rated pipe, fittings, valves and sprinklers."
- `d05.galvanizing-fabrication`: "Items to be hot-dip galvanized are detailed for the process: vent and drain holes in every closed section … assemblies sized for the galvanizer's kettle or split with bolted field splices."

Every (c) item:

1. `if.10-counter-dispensers` in 12 35 53: a restroom vanity / toilet-accessory routing (names "the vanity", stone tops, 12 36 00) inherited unfiltered into laboratory casework.
2. `if.21-release-control` in 21 13 13: clean-agent releasing panel, interlock logic and abort switch in a wet-pipe compile; names 21 22 00 as a furnish option.
3. `if.03-steel-anchorage` in 05 51 00: the 05 12 00 column anchor-rod edge, gated at `foundation_pour`, reaching a stair package that has no anchor rods or base plates.
4. `edu.risk-category-delegated` and 5. `edu.fm.default-risk-category` in 22 40 00: cladding, curtain wall, joist and truss delegated design in a plumbing fixture package (overlay glob too wide).
6. `08hw.accessible-operation`: states that where opening force cannot be met at exterior doors and pressurized stairs "a power operator is in the set"; as a conformance check this over-states the accessibility standard, which exempts exterior and fire doors from the interior force limit. The paired hook asks the question correctly.
7. `ANSI/BHMA A156.28` titled "Recommended Practices for Mechanical Keying Systems"; the published title is "Recommended Practices for Keying Systems".
8. `AHRI 1350` listed as a standard to verify 23 74 13 RTU claims against; it rates central-station AHU casings, not packaged rooftop units.

Reverse gaps (judged): in 10 of 12 sections the classifier listed things the closed-book baseline had that the compiled context lacks entirely. The pattern is consistent: the layer is thin on section-specific product and engineering depth (rebar and mix-design review in 03 30 00; hinges, lock functions by room, closer arms, handing in 08 71 00; seismic bracing, hangers, pipe standards and calc internals in 21 13 13; floor drains, trap primers, carrier-vs-slab coordination and vandal resistance in 22 40 00; sensible capacity, SCCR, gas-heat data in 23 74 13; SLC loop calcs, pull stations, lockdown priority in 28 46 00). Standards lists are 2–11 entries where the baseline listed 10–24.

### 3.2 Behavioral ablation (measured by a blind scorer)

Three prose mini-submittals with planted defects were written by subagents that had not seen the layer: an 11 40 00 foodservice brochure package (186 "pages", 13 defects), a 23 74 13 RTU package (95 "pages", 13 defects) and an 08 71 00 door hardware package (140 "pages", 14 defects). Each was reviewed twice by subagents following `SKILL.md`, once with the compiled `context.md` and the 37-item `reflexes.md`, once with a scratch knowledge base holding only `_global.yaml` and `milestones.yaml` (which compiles to 8 global checks, no hooks, no interfaces, `review_mode: package`). A third subagent scored both reviews blind (A/B labels assigned at random) against the sealed key.

| Case | Arm | Caught / partial / missed | False findings | Bonus findings | Owner correct | Trade named | Need-by stated | Code question left open | Noise rows (na, not relevant, unverifiable) | Blind scorer preferred |
|---|---|---|---|---|---|---|---|---|---|---|
| 23 74 13 RTUs (13) | with layer | 11 / 2 / 0 | 2 | 7 | 11/11 | 9/11 | 9/11 | yes | 19/101 = 18.8% | |
| | without | 11 / 2 / 0 | 1 | 9 | 11/11 | 8/11 | 9/11 | yes | 2/134 = 1.5% | **without** |
| 08 71 00 hardware (14) | with layer | 14 / 0 / 0 | 2 | 5 | 13/14 | 11/14 | 11/14 | yes | 45/120 = 37.5% | |
| | without | 14 / 0 / 0 | 2 | 5 | 14/14 | 11/14 | 11/14 | yes | 56/241 = 23.2% | **without** (small margin) |
| 11 40 00 foodservice (13) | with layer | 13 / 0 / 0 | 0 | 10 (one speculative: freezer frost heave placed on the pre-pour hold list at high) | 12/13 | 9/9 | 9/9 | yes (3 of 3) | 155/243 = 64% | |
| | without | 13 / 0 / 0 | 0 | 7 | 12/13 | 9/9 | 9/9 | yes (3 of 3) | 65/272 = 24% | **without** (small margin) |

No review in any arm fabricated a reference or answered a code question from memory. The scorer's reasons for preferring the no-layer RTU review: the with-layer review raised two requirements the documents do not contain (octave-band sound data tied to a classroom criterion; condensate trap height), carried fourteen hook-driven compliance questions, and spent a fifth of its ledger and routing rows on wood trusses, metal buildings, foodservice and housekeeping pads. For hardware the scorer's reasons were the same in kind: storm shelters, wind-borne debris and energy-code questions in a hardware package.

The measurable things the layer changed in the ablation: the with-layer hardware review put the GC rather than the sub on the misrepresented transmittal; the with-layer RTU review attached a milestone to the warranty item; the with-layer foodservice review raised freezer-floor frost heave (the layer's `if.03-cold-storage-floors` edge, one of the best (b) items in §3.1) and a consolidated pre-pour hold list. The scorer rated the frost-heave finding speculative because the documents give it no basis, which is the two-sided nature of the (b) items: they prompt the right question and also prompt findings the CDs cannot support. In every case the noise share with the layer was higher (18.8% vs 1.5%, 37.5% vs 23.2%, 64% vs 24%).

### 3.3 The shipped eval (measured)

`claude plugin eval . --case submittal-review --scaffold --allow-tools Bash Write Edit --judge-model sonnet --ablation none` was run twice on clean exports of the head: once as shipped, once with `reference/csi/` reduced to `_global.yaml` + `milestones.yaml`.

| Arm | Graders passed | Turns | Wall time | Cost (eval's accounting) | Findings reported | Coverage rows | Unverifiable rows |
|---|---|---|---|---|---|---|---|
| Full layer | 9/9 (every judge vote unanimous) | 20 | 277 s | $1.01 | 15 | 78 | 41 (53%) |
| Empty layer | 9/9 (every judge vote unanimous) | 21 | 136 s | $0.66 | 10 | not stated | 3 checks |

Both runs found all four planted defects, routed the brackets to the framer before second-side board, left the accessibility requirement open, suggested "return, incomplete", wrote the workbook and the markup PDF. The empty-layer run even added the accessibility question itself ("the knowledge layer compiled no hooks for this section, so I added this question myself"). The eval therefore tests the procedure, the fixture and the scripts, not the layer. Its nine graders check four defects that the spec text and three sheets state outright, plus five mechanical outcomes. The PR body's "1.00 on both runs" is reproduced here, and it is equally true with the layer removed.

### 3.4 Correctness sample (measured, verified online where the verifier was unsure)

40 items drawn with a fixed seed from 4,538 (15 checks, 10 failure modes, 7 hooks, 5 edges, 3 standards; 32 profiles, 5 interface files, 3 overlays), verified for technical correctness, current MasterFormat numbers and titles, standards against publishers, gates and the layer's own no-bare-number rules.

| Result | Count |
|---|---|
| Correct | 34 |
| Minor issue | 6 |
| Error | 0 |

Minor issues: `if.08-dock-equipment` conflates the vendor-furnished control panel with the field wiring 26 05 00 furnishes; `11fh.hood-types` lacks `drawings.mechanical` in `trace_to` for perchloric exhaust; `if.06-av-backing` routes only to wood sections, not metal-stud backing under 09 22 16 / 05 40 00; `08hw.egress-hardware` says "every door without a key" (code permits key-operated main-door locks) and has no gate; `22in.rh.flame-smoke` cites only `mechanical_code` where the non-plenum limit is in the building code; `01sch.fm.manufactured-recovery` says "no credible baseline" where only the update record is lost. Every MasterFormat number in the sample is current; every standard designation and title checked exists and is current (BHMA A156.9-2020, BCSI 2025, 33 52 16, 28 42 00). One note: `if.32-permeable-paving-stormwater` uses the MasterFormat 2020 title for 33 46 00.

So the facts are right. The errors found in this audit (the eight (c) items) are errors of **context**: correct facts delivered to the wrong section by inheritance or by an overlay glob.

### 3.5 Gates (measured counts; sample judged)

| Measure | Value |
|---|---|
| Gated items (checks + reconciliations + edges) | 1,035 |
| Ungated checks | 624 of 1,260 (49.5%), including 34 critical and 320 high |
| Share of all gates on `procurement_release` | 389 (37.6%); Division 04 85%, 05 71%, 08 62% |
| Milestones never used | 0 (but `sheathing_cover` 1, `overburden_placement` 1, `precast_erection` 2) |
| Seeded sample of 30 gated items | 24 defensible, 2 too late (`if.06-openings-in-framing`, `if.food-grease-duct-enclosure`), 1 too early (`23vs.restraint-design`), 2 wrong or homeless (`if.23-controls-wiring` needs buyout, `27rc.need-determined` needs permit) |
| Inconsistent families (same hand-off, different gate in different divisions) | 9, e.g. `22in.firestop-match` at `above_ceiling_close_in` vs `23in.firestop-match` at `procurement_release` |
| `milestone --id wall_close_in` view | 178 lines, about 7k tokens, usable; 33 failure modes restate the backing miss eight ways |
| `milestone --id procurement_release` view | 1,206 lines, 35.7k words, unusable |

Judged: rigor at the physical-cover milestones (17 of 18 sampled correct), theater at `procurement_release`, which is used to mean buyout, submittal approval, fabrication release, permit and "early". The milestone list lacks buyout, permit/AHJ approval, a fabrication-release-versus-approval split, rough framing, ceiling grid, and owner move-in. `backfill` and `overburden_placement` have empty `inspect_before` where the industry has standard hold points (waterproofing inspection; flood test).

### 3.6 Cost (measured)

| Measure | Value |
|---|---|
| Layer | 293 files, 2.8 MB, 4,538 keyed items; 226 section profiles, 23 division baselines, 15 overlays, 274 edges; all 293 at `status: draft`, `reviewed_by: []` |
| `validate` wall time | 25–34 s (4,233 resolves; `lineage()` called 9.4M times unmemoised) |
| `resolve` wall time | 2.0 s per section (95% parsing all 292 files for the edge-failure index) |
| Compiled `context.md`, no overlay, all 226 sections (tokens ≈ chars/4) | min 2.1k, median 4.8k, max 13.3k (03 35 00), mean 5.3k; 39 sections above 7.5k, 7 above 10k |
| Compiled `context.md` for the 12 test sections with `education.k12` | 6.3k (22 40 00) to 13.6k (21 13 13) tokens |
| `reflexes.md` | 37 entries, 23 KB, about 5.7k tokens, not filtered by section (`reflexes --project` returns 0 when the project has one section) |
| Fixed prompt a review worker reads before any document | `context.md` 8–13k + `reflexes.md` 5.7k + `review-data.md` 1.8k + `review-writing.md` 0.8k + worker prompt 0.9k ≈ 17–22k tokens, per worker |
| Interfaces compiled per section | median 5, max 44 (26 05 00), 41 (23 30 00); 18 sections with 15 or more; 374 of 1,641 edge matches (23%) reach a section only through a descendant |
| Element-scope checks (63 `per_element` sections) | median 6, max 19 (12 35 53); 12 35 53 with 20 elevations → about 380 element rows plus 14 package rows plus 11 routing rows plus 5 compliance rows |
| Busywork in the shipped eval fixture (4 elevations) | 78 coverage rows, 41 unverifiable (53%); 2 of 11 routing rows "not relevant" |
| Busywork in the ablation | with layer 18.8% and 37.5% of ledger + routing rows were na / not relevant / unverifiable one-liners, vs 1.5% and 23.2% without |

Estimated cost of one real review (judged from the measurements): the shipped eval's 4-elevation fixture cost $1.01 and 277 s with the layer versus $0.66 and 136 s without, on the eval's own accounting. A 20-elevation casework or 25-item foodservice package fans out to 3–5 workers, each carrying about 20k tokens of fixed context plus pages, and the main context carries the same again plus the gate loop. Order of magnitude: 30–60 minutes and $10–30 per review, of which the layer's fixed context is roughly a third. The attention cost is the bigger one: compiled contexts above 8k tokens with 25–30 checks, 20–30 failure modes and 10–40 interfaces are what produced the off-topic routing rows and invented requirements the blind scorer penalised.

### 3.7 Resolver and script correctness (measured by probe; file:line in `scripts/csi/csi_knowledge.py` and `skills/submittal-review/scripts/check_coverage.py`)

| Id | Severity | Finding |
|---|---|---|
| R1 | high | A profile that suppresses an edge carrying `facility_types` makes `resolve` and `validate` fail: edges are filtered by facility (`:526-527`) before the suppression check (`:536`), and `validate` always resolves with no facilities |
| R2 | high | Suppressing an edge leaves a false `caught_by` warning when the failure mode has another live catcher (`:583-589`); `--strict` turns it into a failure, so authors suppress whole failure modes instead |
| R3 | high | `related()` (`:159`) is symmetric, so edges match **upward**: 23% of all edge matches reach a section only via a strict descendant (`26 05 00` gets 45 of 45 edges this way). SCHEMA §6 and AUTHORING §5 contradict each other on the direction. This is why the layer carries 235 `suppress` entries |
| R4 | medium | `same_as` silently drops the alias's own division baseline (`01 57 13` never loads `profiles/01/_division.yaml`) and `coverage.missing` does not say so |
| R5 | medium | `legacy_numbers` (used in 1 of 293 files) cannot express the 2004→2016 renumbering; `--section "28 31 00"` compiles intrusion detection |
| R6 | medium | At `640ab78` suppress-of-undefined-edge was an error, so a typo'd id got the same message as a real unreached edge; commit `cca1d6f`, pushed during this audit, restores the warning and makes the tree match the PR #13 head again (the PR body's "identical tree" claim was false only between `640ab78` and `cca1d6f`) |
| C1 | high | `coverage_pct` and the summary line (`:147`) count `todo` rows as covered: four todo rows print `Coverage 4/4 (100.0%)` and the workbook Summary repeats it while the gate says INCOMPLETE |
| C2–C4 | medium | Coverage rows for unknown elements or checks, duplicate rows, findings on elements not in the inventory, routing rows naming nonexistent findings, and compliance rows for hooks not in the context are all accepted silently |
| C7 | medium | SKILL.md compiles `context.yaml` (step 2) before facility types are confirmed (step 3); a re-run writes `context_v2.yaml` (`shared.py` versioning) that the gate never reads |

The gate's documented behaviors (scaffold, todo gate, missing-`action` gate, export refusal) work. Provenance (`_from`, `_status`, `_patched_by`) is correct; the confidence floor is a constant because every file is draft.

---

## 4. Top ten problems, ranked by impact on review quality

1. **The compiled context is mostly what Claude already knows, and it is big.** 94.1% of 1,105 classified items were (a) or (d); the median section compiles to 4.8k tokens, the test sections with an overlay to 6–14k, plus 5.7k of reflexes, per worker. Measured consequence: more noise rows (18.8% and 37.5% vs 1.5% and 23.2%) and more false findings in the with-layer RTU review, and a blind preference for the no-layer review in two of three cases. Files: every `profiles/*/*.yaml`; `scripts/csi/csi_knowledge.py` `--format md`.
2. **Inheritance and overlay leakage put wrong items in front of the reviewer.** All eight (c) items are correct facts in the wrong section: `if.10-counter-dispensers` (12 35 53), `if.21-release-control` (21 13 13), `if.03-steel-anchorage` (05 51 00), `edu.risk-category-delegated` and `edu.fm.default-risk-category` (22 40 00), AHRI 1350 (23 74 13). Root causes: R3 upward edge matching and 287 per-item overlay `sections` globs. The 235 `suppress` entries are the symptom.
3. **The layer is thinner than the baseline on section-specific depth, and the worker prompt anchors workers on the layer.** `worker-prompt.md` says "Your checks are the ones marked Scope: element"; the classifier found 10 reverse gaps per section (sprinkler seismic bracing, hinge rules, floor drains and trap primers, RTU sensible capacity and SCCR, SLC loop calcs). A worker that obeys the prompt skips what the layer omits.
4. **The eval does not test the layer.** 9/9 with the layer emptied. `evals/plugin/submittal-review/graders/*.md` grade four defects that `12_35_53.txt`, A-501, A-521 and P-601 state outright. No case exercises any (b) item, any other division, a PDF of real size, a resubmittal, or a bound hook.
5. **Coverage ledger rows are busywork at scale, and the gate's summary lies.** 12 35 53 has 19 element-scope checks; a 20-elevation job is about 380 rows. In the shipped fixture 53% of rows were unverifiable. `check_coverage.py:147` reports 100% on rows still `todo` (C1); bogus rows pass (C2–C4). Files: `skills/submittal-review/scripts/check_coverage.py`, `references/review-data.md`.
6. **Health-department and other regulatory questions are flagged, never performed.** `regulatory_hooks` bind only to `.construction/skills/code-researcher/topics/<slug>.yaml` written by a separate interactive skill; unattended runs always leave them open (both eval runs did). The foodservice hooks (`foodservice-plan-review`, `11fs.rh.accessible-service`) never name a serving-counter or tray-slide height as a health-department question. Files: `reference/csi/overlays/foodservice.yaml`, `profiles/11/11-40-00.yaml`, `SKILL.md` steps 3 and 8.
7. **Gates are half theater.** 49.5% of checks have no gate (34 critical); `procurement_release` carries 37.6% of all gates and means five different moments; need-by dates are "the gate milestone mapped to the project schedule where one exists", but no script maps anything and both eval runs reported "need-by TBD". Files: `reference/csi/milestones.yaml`, every `gate:`.
8. **No tooling for a large brochure.** Step 5 says "identify pages from titles, tags and headers" with `rasterize_page.py`, `crop_region.py` and `extract_text_region.py` as the only readers; there is no text index or page finder, so a 400-page PDF means roughly 400 rasterizations or a guess. The foodservice ablation was prose, so this path was not exercised. Files: `SKILL.md` step 5, `scripts/pdf/`.
9. **Commonly submitted sections have no profile and compile under the wrong title.** 23 74 13 compiles as "Central HVAC Equipment", 26 24 16 as "Switchboards and Panelboards", 21 13 13 as "Fire-Suppression Sprinkler Systems"; 80 of 226 profiles report a missing ancestor; `28 31 00` on a pre-2016 spec compiles as intrusion detection (R5). Files: `profiles/23/23-70-00.yaml`, `profiles/26/26-24-00.yaml`, `profiles/28/28-30-00.yaml:17`.
10. **Maintenance and trust.** 4,538 items, 1,555 `caught_by` references (303 cross-file), 765 gate references, 235 suppressions, 160 edge endpoints with no profile; renaming one section number silently changes edge matching. Every file is `status: draft` with no reviewer, and the PR review notes' "I would let a junior PE rely on it" lines are self-assessments by the same drafting pipeline. The compiled report shows "draft" as one line, which a reader will stop seeing. `validate` at 25–34 s discourages the authoring loop the docs prescribe.

---

## 5. Against the original goal

The PE asked for expert submittal reviews for any CSI scope, with four real misses to catch and outputs that name the subs, the rules to validate, and the validation itself.

| Goal item | Status | Evidence |
|---|---|---|
| Casework shops checked against every detail and elevation | **Partly solved, by the procedure** | `SKILL.md` step 4 ("Follow every detail or section cut drawn on an elevation") plus `cw.detail-trace` and `d12.element-coverage`. Both eval arms caught the missing elevation 4; the empty-layer arm did it from Part 1 of the spec. Nothing verifies that every cut on a sheet was opened; `trace.json` is self-reported |
| State health-department counter-height requirement | **Not solved** | No hook asks it. `11fs.rh.accessible-service` asks about accessibility of tray slides and counters; `foodservice-plan-review` asks whether plan approval is in hand. Both are left `unbound` → "open" unless a user says yes at the checkpoint and `code-researcher` runs; unattended runs never research. In the foodservice ablation both arms caught the 36 in vs 34 in tray-slide mismatch, named the Maryland Accessibility Code and the Howard County Health Department as the authorities, and left the governing rule open; neither validated it. The layer made no difference to this item |
| In-wall backing and brackets coordinated with framing, plumbing, electrical | **Partly solved** | `cw.in-wall-support` (critical, `wall_close_in`), `if.casework-backing`, the `06rc.blocking-master-list` reflex, and the routing row. The empty-layer eval caught the same defect from `g.by-others-mapped` and spec 1.2.A, and routed it to the framer "before second-side gypsum board". Need-by date is never computed |
| Huge foodservice brochures | **Not solved** | Element fan-out (`equipment_item`), 5–8 elements per worker and a both-ways inventory exist on paper. No page index, no text search across a package, no rule for a 400-page PDF beyond "identify pages from titles". The 11 40 00 context is 10.5k tokens before a page is read |
| Name which subs to coordinate with and by when | **Partly solved** | Routing rows name trade, section, what to send, what to get back and a gate; every ablation review with or without the layer produced them. "By when" is a milestone name, never a date: no script maps gates to the schedule, and both eval runs said "TBD" |
| Perform the validation, not just flag it | **Not solved** | The skill never researches; `code-researcher` is interactive and separate; binding is tested only by a resolver probe. In six ablation reviews and two eval runs, every regulatory question was left open |

What an expert PE does on submittals that this stack does not do at all (judged):

- Process a substitution request (Division 01 form, comparison data, cost and schedule impact, A/E concurrence). `g.basis-of-design` flags; `01 25 00` has a profile; the skill has no path.
- Track deferred submittals and AHJ plan-review status per package.
- Close approved-as-noted markups across resubmittals as a running list with the A/E's stamp language; `prior.json` tracks the GC's own findings only.
- Assess lead-time and procurement impact against the schedule (`g.lead-time` is a one-line check with no schedule read).
- Review closeout submittals (O&M, warranties, record documents, attic stock, training) as a submittal class; `01 78 00` has a profile; the skill's taxonomy stops at action submittals.
- Review physical samples and mock-ups (color range, field mock-up acceptance, approved-sample custody).
- Update the submittal log and the distribution (the eval project has no log; the skill reads one if present and writes nothing).
- Hold a keying meeting, a pre-installation meeting, a coordination-drawing review (01 31 00 has no profile, admitted in PR #6).
- Decide stamp language and disposition codes per the contract, not a four-row table.
- Price and schedule the consequence of a finding (change-order exposure, hold on fabrication).

---

## 6. Recommendations, cheapest first

**Delete (hours):**
- `legacy_numbers`, `same_as`, `applies_if`, `escalate`, `override`/`merge` and edge `suppress` from the schema and resolver; replace each with a sentence in the profile. Together they touch under 2% of ids and exist to patch inheritance.
- Overlays other than `healthcare*`, `foodservice` and `laboratory` until a test case needs them; the `education.k12` overlay produced two of the eight wrong-in-context items and the only (b) item in 12 35 53, so keep `edu.agency-approvals` as a single hook.
- The eight (c) items listed in §3.1, and the `failure` text duplicated across the eight backing failure modes the `wall_close_in` view restates.
- The 231 (d) items in the twelve audited sections, using the classification tables (kept with the archived branch, tag `archive/feat/csi-knowledge-layer`, under `docs/audit/csi-layer/marginal-value/classification/`) as the cut list; apply the same test to the other 214 sections before keeping them.

**Fix before merging PR #13 (a day):**
- `check_coverage.py:147` C1 (todo rows counted as covered); validate element, check, finding, hook and interface ids on every row (C2–C4); name the file in JSON parse errors (C5).
- Move "compile knowledge" after the facility checkpoint, or re-compile after it and read the newest context file (C7).
- Default `scope: package` for every inherited global and division check in `per_element` sections, and cap element rows: a check that is `na` for every element should be one package row, not N.
- Make `reflexes` section-filtered and drop it from the worker prompt; 5.7k tokens of other divisions' red flags per worker is where the storm-shelter rows came from.
- Add a second eval case whose graders can only pass with a layer item (freezer underfloor heat on an 11 41 00 walk-in; return-air transfer through a rated wall on 09 21 16), and report the empty-layer arm in the eval output so the PR body's score means something.
- Fix the section title in the compiled header when the section has no profile; add the hard alias for 2004-numbered fire alarm (28 31 00 → 28 46 00) and intrusion detection.
- Memoise `lineage()` and `normalize()` and cache the edge-failure index (`validate` 25 s → ~11 s measured; resolve 2 s → ~0.1 s).

**Fix before merging any knowledge PR (a week):**
- Make edge matching one-directional (declared section and its ancestors only) and remove the 235 `suppress` entries that compensate for it; re-run the twelve classifications and confirm the (c) count goes to zero.
- Tighten every overlay item's `sections` glob to the trades it touches; `edu.storm-shelter` belongs to 03, 04, 05, 07, 08 and 26, not every section.
- Gate or mark `gate: none` on the 34 critical and 320 high ungated checks; split `procurement_release` into buyout, submittal approval and fabrication release; add `permit_approval`; reconcile the nine inconsistent families (`docs/audit/csi-layer/gates.md` lists them).
- Write real profiles for 22 40 00, 23 74 13, 21 13 13, 26 24 16 and 07 54 00 from the reverse-gap lists, or stop claiming those divisions are covered.
- Get one named PE to review one division and move it to `pe_reviewed`, so that `status` means something. Until then, print the draft warning on every finding the layer sourced, not once at the top.

**Build next (what the original goal still needs):**
- A `find_pages.py` for packages: text-extract a PDF once, index page titles, tags and item numbers, and return the pages per element, so a 400-page brochure costs one pass, not 400 rasterizations.
- A health-department hook family that names the actual questions (serving-counter and tray-slide heights, hand-sink placement, floor-sink sizing, finish and lighting rules) and an unattended path that runs `code-researcher` with web access when the checkpoint cannot be answered, so "open" is the exception.
- A schedule read for need-by: map each gate milestone to the nearest activity in the extracted schedule (`schedule-extractor` already exists) and print a date, not a milestone name.
- A per-section "delta" format: 5–15 lines per section of the (b) kind (cross-trade edges, question-shaped hooks, constructability traps) that compile to under 2k tokens, instead of 80–130 items that restate the baseline.
- Resubmittal, substitution and closeout paths in the skill, since those are where a PE's time goes after R0.

**Stop doing:**
- Counting items, files and divisions as progress; the measured value is 5% of items and it is concentrated in cross-trade edges and question-shaped hooks.
- Compiling every inherited check into every section and then suppressing; write the general rule once in `_global.yaml` and let the procedure apply it.
- Presenting "independent review" by the same drafting pipeline, and "verified against the publisher" lists that were confirmed from memory, as evidence of correctness.
- Scoring the eval only with a non-default judge and reporting the number without the artifact; commit `aggregate-result.json` or do not cite the score.
- Asking workers for one row per element × check; ask for findings with both sides cited and a list of what could not be verified, which is what the blind scorer rewarded.

---

## Appendix: what was run

Evidence files were removed from the repository with the layer itself on 2026-10-04 (they remain in git history and on the tag `archive/feat/csi-knowledge-layer`, under `docs/audit/csi-layer/`): the 12 closed-book baselines, compiled contexts and classification tables (`marginal-value/`), the 40-item sample and verifier results (`correctness/`), the three fixtures with keys, both reviews, the with-layer context and the blind score for each (`ablation/`), both eval result JSONs and final messages (`eval/`), `gates.md`, `code-review.md`, `pr-claims.md`, `section-metrics.jsonl` and the compiled `reflexes-compiled.md`.

- `bin/construction-python scripts/csi/csi_knowledge.py validate` (and `--strict`): 293 files, 0 errors, 0 warnings, 0 lint, 293 at draft; 25–34 s.
- `resolve --format md` and `--format yaml` for all 226 section profiles (token and item counts in §3.6); `resolve --facility education.k12 [--facility foodservice]` for the 12 test sections; `reflexes --format md`; `milestone --format md` and `--id wall_close_in`.
- 12 closed-book baseline agents, 12 blind classification agents (protocol: strict (a)/(b)/(c)/(d), ties to (a) or (d)), 4 verification agents over a seeded sample of 40 items, 1 gate audit agent, 1 resolver and script review agent, 1 PR-claims extraction agent, 3 fixture authors, 6 reviewer agents (3 cases × with/without), 3 blind scorers.
- `claude plugin eval . --case submittal-review --scaffold --allow-tools Bash Write Edit --judge-model sonnet --trust-plugin --ablation none --json` on two clean exports of the head (full layer; `reference/csi/` reduced to `_global.yaml` and `milestones.yaml`). The eval's sandbox needed `bubblewrap` and `socat` installed and a pre-built venv copied into `.eval-home` because the sandbox has no network.
- Repository PR bodies #5–#13 via the GitHub REST API; the folded review notes were treated as claims and checked against the head (13 overstated or stale claims found, listed in `docs/audit/csi-layer/pr-claims.md`; the ones that matter are in §2).
