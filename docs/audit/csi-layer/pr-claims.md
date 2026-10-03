# Claims made in PRs #5–#13 (dleerdefi/claude-code-construction)

Source: `prs/bodies.md`. Repository checked at `feat/csi-knowledge-layer` (HEAD 640ab78) and at the stack branches `origin/csi/1-framework` … `origin/csi/9-submittal-review`.
Marks: **M** = measurable in the repository, **A** = only assertable (external verification, judgment, or an un-recorded run). Where I measured, the result follows "→".

---

## 1. Per-PR summaries and checkable claims

### PR #5 — Knowledge layer: schema, resolver, milestones, Division 07
Adds `reference/csi/` (SCHEMA.md, AUTHORING.md, milestones.yaml, profiles/_global.yaml) and the resolver `scripts/csi/csi_knowledge.py` with five commands.
Adds Division 07 as the worked example (baseline, 7 profiles, 28 edges) and `docs/PE_EXPERTISE_REVIEW.md`; retires pe-review's RFI template.
States the design rules: no code threshold stated as fact, K1 knowledge never becomes a requirement, K2 hooks are never dropped.

1. "`csi_knowledge.py` has five commands: resolve, reflexes, milestone, topics, validate" (M) → all five exist and run.
2. "`validate`: errors, warnings and lint, including bare numbers, near-duplicates, edges that repeat a failure, and id prefixes shared by two owners" (M; the shared-prefix lint was added in a later commit, 6aafe07).
3. "`resolve` … supports aliases (`same_as`), suppressions (including edges), `applies_if` and `--only`/`--types`" (M) → edge suppression present at HEAD; note PR #7's review requested it as a *missing* feature (see §3).
4. "`milestones.yaml` (29 gates)" (M) → 29.
5. "Division 07 … a baseline, 7 section profiles and 28 interface edges" (M) → 7 profiles + `_division.yaml`; div-07.yaml has 28 edges.
6. "`11 files · 0 errors · 0 warnings · 0 lint · 11 at draft status`" (M) → `origin/csi/1-framework` holds 11 yaml files under reference/csi.
7. "No code threshold is ever stated as fact" / "no bare numbers" (M via lint only; A as to substance) → lint 0.
8. "The archive stays untouched as the A/B baseline" (M) → `reference/pe_expertise/` untouched in stack.
9. "`pe-review`'s duplicate RFI template is retired" (M) → commit 40dd37f deletes `skills/pe-review/references/rfi_template.md`.
10. "SCHEMA.md and the code agree. The merge rules are M1–M8" (A; reviewer instruction, not a demonstrated fact).
11. "An edge endpoint matches only its own lineage"; "an alias whose target sits inside its own subtree doesn't drag its siblings along"; "an edge with no `failure` borrows the text of the failure mode that names it" (M by test, not measured here).

### PR #6 — Divisions 01, 02, 31, 32, 33
46 section profiles (5 aliases) plus baselines for general requirements, existing conditions and sitework.
Two commits: drafted/integrated state, then the independent reviewer (r1) changes.
Reviewer verified MasterFormat numbers against CSI's list and standards with publishers; fixed four gate/fact errors.

1. "46 section profiles (5 aliases) … 220 checks, 20 reconciliations, 223 failure modes, 55 code questions, 52 standards, 32 interface edges and 8 always-on red flags" (M) → every number matches HEAD exactly.
2. "Everything is `status: draft`" (M) → 293 at draft.
3. "`67 files · 0 errors · 10 warnings · 0 lint`" (M) → reproduced at `origin/csi/2-general-site`.
4. "The warnings are references to edges or checks that later pull requests in this stack add; they clear by PR 6" (M) → `origin/csi/6-fire-plumbing-hvac` shows 0 warnings.
5. "There are two commits … the second holds the independent reviewer's changes" (M) → yes on the stack branch (66e89f1, 166ce3d); **not** on `feat/csi-knowledge-layer`, which has one combined review commit (a2b35cd).
6. "Items the reviewer routed to files outside this group were applied in the integration pass, except where they appear above" (M partly) → 07 81 00 title now "Applied Fire Protection"; see §3 for the rest.
7. r1: "Final state: `validate --strict` reports 0 errors, 0 warnings and 0 lint for the whole layer" (M) → true of HEAD, not of this PR's head (10 warnings).
8. r1: "Every section number used in my files and in their edge endpoints is in [CSI's MasterFormat 2018 list]" (A).
9. r1: "Standards confirmed with the publisher … ASTM D5882-16 and D6760-16 were both withdrawn in 2025 … ASTM D4945-26 is current … ANSI Z60.2-2025 … NFPA 3 (2024 edition) …" (A).
10. r1: "ASTM D1556/D1556M-24 superseded the -15e1 edition"; "ACI SPEC-330.1-24"; "TIA-758-C was in recirculation ballot in September 2025" (A).
11. r1: "Lockdown sealer under new fireproofing: … I confirm it as a PE" (A).
12. r1: new alias files `01-57-13.yaml`, `01-57-23.yaml` `same_as: "31 25 00"` (M) → present.
13. r1: "Reflex count is at the cap of three" for Div 01 (M) → HEAD reflexes list shows Div 01: 2 (list was trimmed after r7).
14. r1: "Confidence: high. A junior PE can rely on it as a checklist; the numbers and standards are verified" (A).
15. Body: "Divisions 31–33 keep older short id prefixes (`ef.`, `wa.`, `dp.`...), allowed by AUTHORING §4" (M) → AUTHORING §4 at HEAD says "Divisions 07, 12 and 31–33 use older short prefixes"; the exception was widened (see §3).

### PR #7 — Divisions 03, 04, 05
26 section profiles (3 aliases) for concrete, masonry and metals.
Reviewer r2 added three precast edges, five standards, fixed the masonry fire-rating error and the shear-wall joint gate.
Flags the stair/railing edge noise and asks for a resolver edge-suppression feature.

1. "26 section profiles (3 aliases) … 140 checks, 15 reconciliations, 150 failure modes, 31 code questions, 75 standards, 51 interface edges and 7 always-on red flags" (M) → all match.
2. "`99 files · 0 errors · 8 warnings · 0 lint`" (M) → reproduced at `origin/csi/3-structure`.
3. "Stair and railing profiles (05 51 00, 05 52 00) suppress misc-metals edges … relies on edge suppression in the resolver (PR 1)" (M) → 05-51-00 suppresses 11 edge ids, 05-52-00 suppresses edges; text "(not a stair or railing item)" is gone from div-05.
4. r2: "`validate --strict` on the whole layer gives 293 files, 0 errors, 0 warnings, 0 lint. No ids were deleted or renamed" (M) → HEAD matches; this PR's head has 8 warnings.
5. r2: "Precast, architectural precast and tilt-up had **zero** interface edges" before (M by history; not checked).
6. r2: "PCI's site now says [PCI 135] was issued in 2025 and that it supersedes the tolerances in MNL-135" (A).
7. r2: "Verified — MasterFormat (designguide.com): every 03 number and title used"; ACI SPEC-301-20, SPEC-305.1-14(20), SPEC-306.1-90 historical, PRC-306-16, SPEC-117-10(R2015), SPEC-308.1-23, PRC-302.2-22, PRC-347-14(21), PRC-347.2-17(25), PRC-551.1-14, ACI 423.7-14 (A).
8. r2: "ACI 318 is not cited anywhere in my files" (M) → grep-able; not checked.
9. r2: "AISC 207-20 … the 2016 edition is inactive"; "ANSI/SJI 100-2020 full title from the SJI PDF"; "AISC DG11, 2nd edition: Chapter 4 includes monumental stairs … confirmed … through a secondary copy, not AISC directly" (A).
10. r2: "A stair review gets 15 edges and 3 apply … A railing review gets 14 edges and 2 apply" (M, pre-fix state).
11. r2: Counts — "Errors of fact or gate: 4. Standard designation or title corrections: 4. Gaps: 6 … plus 5 new standards. Noise: 8 suppress entries across 05 31 00 and 05 40 00, plus 1 … in 03 47 00. caught_by links: 6" (M) → 05-31-00 and 05-40-00 have 4 suppress entries each (8).
12. r2: "**I would let a junior PE rely on it**, with the draft caveat" (×3 divisions) (A).
13. r2: "ASTM C645 … belongs to 09 22 16, not here" (A).

### PR #8 — Divisions 06, 08, 09, 10, 12
60 section profiles (6 aliases) for wood, openings, finishes, specialties, furnishings.
Carries two review notes: r3 (06, 08, 09) and r4 (10–14; the same r4 text is repeated verbatim in PR #9).
r3 split 06 17 00 into trusses vs engineered wood, fixed the glulam fire-resistance and FRT-blocking errors, corrected many standard titles.

1. "60 section profiles (6 aliases) … 281 checks, 28 reconciliations, 250 failure modes, 100 code questions, 147 standards, 71 interface edges and 7 always-on red flags" (M) → all match.
2. "`169 files · 0 errors · 5 warnings · 0 lint`" (M) → reproduced at `origin/csi/4-interiors`.
3. r3: "`validate --strict` on the whole layer reports 0 errors, 0 warnings, 0 lint (291 files, all draft)" (M) → HEAD has 293 files (r2/r6/r7 say 293); r3 and r5 say 291. Snapshot inconsistency, not an error at HEAD.
4. r3: "MasterFormat numbers were checked against the CSI MasterFormat 2020 numbers-and-titles list … not ARCAT" (A).
5. r3: new `profiles/06/06-17-53.yaml` with truss ids moved; `if.06-truss-mep-loads` a-side → 06 17 53 (M) → file present.
6. r3: "The old claim is wrong for Type IV-A and IV-B mass timber" (A, PE judgment).
7. r3: "The previous title [AAMA 501.6] was invented" (A).
8. r3: "Standards and numbers verified — AWI 0620, 0622.0646, 0642, SMA 0643, 0400, 0641, 1232, 1236 … all correct"; BHMA A156.4/.19/.38/.10/.115W; DASMA 105/108; AAMA 501.6/502/1503; NFRC 100/200; ASTM C1087/C1401/E783/E2190; AMCA 500-L/511/550; UL 10D; WDMA I.S.1A; GA-214, GA-600, ASTM F1700, F793, TCNA A118.x, A137.x, A108.19, A326.3 (A).
9. r3: "Confirmed from my own knowledge of current titles, not re-fetched" — long lists for 06, 08 and 09 (A, explicitly unverified).
10. r3: "09 21 16 compiles 21 interface edges" (M).
11. r3: "grep for stencil or marking returned nothing" before adding `09pt.rated-wall-marking` (M by history).
12. r3: "No schema, milestone, `trace_to` or source-family additions are needed. Every new item uses existing terms" (M; validate passes).
13. r3 confidence: "Rough carpentry … good"; "Doors, frames, hardware and glazing: high"; "Gypsum assemblies, tile, flooring and ceilings: high"; "Mass timber: not covered" (A).
14. r4 (also in #9): "`validate --strict` passes for the whole layer (0 errors, 0 warnings, 0 lint). Every required resolve (all 18 sections …) compiles with no warnings other than the draft-status notice" (M) → HEAD passes.
15. r4: "Every number used in my profiles, `equivalents` and interface endpoints (116 numbers …) matches a current number and title in [MasterFormat 2018]" (A).
16. r4: "45 suppress entries across 7 Division 10 profiles" (M) → 5+6+7+8+8+6+5 = 45.
17. r4: "3 suppress entries in 12 30 00" (M) → 3.
18. r4: "Errors of fact or gate: 9"; "4 edge failures folded into failure modes"; "1 duplicate edge merged and deleted"; "Value test: 1 check cut (`d12.finish-selections`)" (M by diff).
19. r4: "SEFA titles corrected to the publisher's current list (sefalabs.com/standards)"; "ANSI MH30.1 … ANSI MH30.3-2022 … UL 1805 … NSF/ANSI 4 and 7" verified (A).
20. r4: "Elevator pit sprinkler shunt-trip exemption" is an error of fact in `14el.rc.fire-protection` (A, PE judgment).
21. r4: "11 31 00 is not in MasterFormat 2018; it is the 2004 number" (A).
22. r4 confidence: "High for signage … I would let a junior PE rely on it"; "High for foodservice … Yes for a junior PE"; "High for casework"; "High for metal building systems"; "High: elevators are the strongest profile" (A).

### PR #9 — Divisions 11, 13, 14
22 section profiles (0 aliases) for equipment, special construction, conveying.
Review notes are the same r4 document as in PR #8.
Walk-ins split by use (11 41 00 foodservice vs 13 21 26 specialty) because the resolver lacks `includes:`.

1. "22 section profiles (0 aliases) … 136 checks, 20 reconciliations, 117 failure modes, 55 code questions, 34 standards, 36 interface edges and 3 always-on red flags" (M) → all match.
2. "`197 files · 0 errors · 4 warnings · 0 lint`" (M) → reproduced at `origin/csi/5-equipment-conveying`.
3. "One home would need an `includes:` mechanism the resolver doesn't have" (M) → no `includes` in resolver.
4. r4: "The 11 41 00 profile suppresses 20 hood, gas and grease items inherited from 11 40 00" (M) → 20.
5. r4: "Division 11 still has three reflex items: `d11.furnished-by`, `11wi.freezer-underfloor` and the `if.11-hood-suppression` edge" (M) → HEAD reflex list has **no** Division 11 section (trimmed after r7).
6. Remaining r4 claims: see PR #8 items 14–22.

### PR #10 — Divisions 21, 22, 23
34 section profiles (0 aliases) for fire suppression, plumbing, HVAC.
Reviewer r5 fixed six errors of fact (cover-plate rating, closed meter loop, flushing, hold point, duplex ejectors, AHRI scope) and the 22 45 00 inheritance.
First stack PR with 0 warnings.

1. "34 section profiles (0 aliases) … 178 checks, 28 reconciliations, 206 failure modes, 96 code questions, 71 standards, 33 interface edges and 4 always-on red flags" (M) → all match.
2. "`237 files · 0 errors · 0 warnings · 0 lint`" (M) → reproduced at `origin/csi/6-fire-plumbing-hvac`.
3. "No 23 05 00 profile" (M) → absent.
4. r5: "`validate --strict` passes on the whole layer, with 291 files" (M) → 293 at HEAD.
5. r5: "the Viking VK202 data sheet pairs a 139 °F plate with a 155 °F sprinkler, and the Tyco RFII is similar" (A).
6. r5: "I verified [UL 218] (ULSE)"; "NFPA 24 and NFPA 2001 titles. Verified (ANSI webstore, 2025 editions)"; "NFPA 291 … still a separate recommended practice (2025 edition)"; "ASPE/ANSI 45 … a 2025 edition exists"; "NSF/ANSI/CAN 61 and 372"; "SMACNA released the 4th edition in 2024"; CTI STD-201 RS; NEBB title; ASHRAE 34, UL 181, ASME B31.5/B31.9/BPVC IV; MSS SP-58 (A).
7. r5: "Not re-checked online (titles match what I know)" — NFPA 13/14/20/25/70/80/96/99/105, ASSE 10xx, ASHRAE 15/52.2/62.1/70/111/135/188/G36, UL 555…, AHRI …, AMCA, HI 9.6.1 (A, explicitly unverified).
8. r5: "one suppress reason contained a comma inside a YAML flow mapping and was silently cut off. I quoted it. No other file in the layer has this problem" (M) → no suppress entry at HEAD has stray keys.
9. r5: "**No bare numbers** were introduced; lint is clean" (M) → lint 0.
10. r5: "The per_element items drop correctly from 23 05 29, 23 05 93, 23 07 13, 23 09 23, 23 21 13, 23 31 13 and 23 33 13 (I checked `not_applicable` in the YAML output)" (M).
11. r5: "23 31 13 compiles 23 edges" (M, pre-integration).
12. r5: Counts — "Errors of fact fixed: 6 … Gate: 1 … Standards: 3 corrected and 2 added … Gaps filled: 3, with 2 new checks and 3 new failure modes. Ids: none deleted or renamed"; "10 suppressions on 22 45 00" (M) → 22-45-00 has 10.
13. r5 confidence: "moderately high" (21), "moderate to high" (22), "high for equipment reconciliation; moderate overall" (23); "I would let a junior PE rely on [each] as a draft" (A).
14. r5: "Jockey pumps are 21 16 00 … in current MasterFormat" (A).

### PR #11 — Divisions 26, 27, 28
31 section profiles (1 alias) for electrical, communications, electronic safety and security.
Reviewer r6 gave 26 05 73 and 26 43 00 their own lineage, split 26 05 00 into four level-3 profiles, created 27 51 00 and the 28 05 37 alias.
Fixed `d26.emergency-separation`, the most consequential content error.

1. "31 section profiles (1 aliases) … 139 checks, 8 reconciliations, 107 failure modes, 42 code questions, 27 standards, 18 interface edges and 4 always-on red flags" (M) → all match.
2. "`274 files · 0 errors · 0 warnings · 0 lint`" (M) → `origin/csi/7-electrical` holds 274 yaml files (validate not rerun).
3. "28 05 37 is an alias of 27 53 19" (M) → present. "no project spec seen using it" (A).
4. r6: "Validate (whole layer, `--strict`): 293 files, 0 errors, 0 warnings, 0 lint" (M) → matches HEAD.
5. r6: "Nothing else was touched (`div-28.yaml` was not changed)" (M by diff).
6. r6: before/after counts — 26 05 73 "28→16 / 25→8"; 26 43 00 "22→13 / 25→0"; 26 27 26 "27→17 checks, 22→13 FMs, 13→7 hooks"; 27 52 23 hc "21→17"; 27 53 19 "22→18" (M).
7. r6: "Suppress 35 inherited 26ds items with reasons" in 26 27 26 (M) → HEAD has **34** suppress entries.
8. r6: "the model electrical code … lets legally required and optional standby wiring share raceways and panels with general wiring" (A, code judgment).
9. r6: "UL confirms that generator base tanks are certified under UL 142" (A).
10. r6: "Verified this session": ANSI/IES LM-63-19, UL 2524, NFPA 1225 (2022, consolidates NFPA 1221), UL 142/2085, UL 891/67 (A). "Checked from knowledge … not fetched": NFPA 70/72/110/780/70E, IEEE 1584, NETA ATS, UL 1449/1008/2200/924/96A/294/864/2196/2572/1069, TIA-568/569/606/607 (A, explicitly unverified).
11. r6: "NFPA 111 is not cited anywhere in my files" (M).
12. r6: "The move of fire alarm from 28 31 00 to 28 46 00 is confirmed by a VA spec … and by Construction Specifier's MasterFormat 2016 Division 28 article" (A).
13. r6: "Resolver docstring … uses 26 43 00 → 26 20 00 as its alias example. That alias no longer exists" (M) → no such text at HEAD; fixed.
14. r6: "`if.26-generator-fuel` … AUTHORING §5 puts 26↔23 edges in div-23 … integrator should decide whether to split it" (M) → now `if.23-generator-fuel` in div-23.yaml.
15. r6 confidence: "Division 26: yes, with the draft caveat"; "Division 27: yes"; "Division 28: yes … 28 05 37 alias is moderate confidence" (A).

### PR #12 — Facility overlays
15 overlays and 4 ov-edge files: 108 checks, 16 reconciliations, 113 failure modes, 71 code questions, 5 edges.
Reviewer r7 removed duplicates of division content, fixed six gates, eight MasterFormat section-scope errors, and merged three hook topics.
r7 Part 2 reviews the whole layer: reflex list (70, target 30–35), milestone order, mis-filed edge, broad endpoints, id-prefix collision, topic merges.

1. "15 facility overlays … 108 checks, 16 reconciliations, 113 failure modes, 71 code questions, 5 edges" (M) → all match.
2. "Overlays only add or escalate; they never suppress division items" (M) → no overlay file has a `suppress` key.
3. "`293 files · 0 errors · 0 warnings · 0 lint · 293 at draft status`" (M) → reproduced at HEAD (and 293 yaml at `origin/csi/8-overlays`).
4. r7: fix counts — "Duplication … removed 5; Wrong or missing gate 6; Unjustified escalation removed 1; MasterFormat number or section-scope fixes 8; Hook topics merged 3; Text trimmed 3" (M by diff).
5. r7: "`34 71 13` (Vehicle Barriers), not `34 71 00` (Roadway Construction). Verified via ARCAT/designguide"; "`11 11 36` (Vehicle Charging Equipment)"; "`14 91*` (Facility Chutes)"; "MasterFormat 28 45 00 *Water Detection and Alarm*" (A).
6. r7: "Verified: ASSE/IAPMO/ANSI Series 6000 (current edition 2024); ASHRAE 170; NFPA 99 and 110; ANSI/ASHRAE 110-2016 (RA2025); ANSI/ASSP Z9.5-2022; ANSI/NETA ATS (current 2025); ANSI/TIA-607-D; ASTM C1713" (A).
7. r7: "the IBC requires firestop special inspection in high-rise buildings" (A, code statement).
8. r7: "There are 70 [reflex] entries without `--facility` (72 with lab and data center) … Division 07 alone has 13" (M, pre-integration) → HEAD: 37 entries; Division 07: 3.
9. r7: "Hook topics (`topics`, 358)" (M, pre-integration).
10. r7: "`exterior-wall-nfpa-285` … is the only slug that names a standard or code section" (M) → renamed to `exterior-wall-fire-propagation-testing`; no slug at HEAD names a standard.
11. r7: "profiles/33/33-50-00.yaml uses `hc.` (hydrocarbon) for all its ids" (M) → now `33hc.`.
12. r7: "Most serious problem found: `hc.epss-acceptance` was … gated at substantial completion" (M by diff).
13. r7 confidence: "good" for every overlay; "I would let a junior PE rely on these with the hooks researched" (A).
14. Body: "`edu.storm-shelter` could add Division 26 to its sections" (M) → k12 default sections still exclude 26.

### PR #13 — submittal-review skill and eval
Adds `skills/submittal-review/` (SKILL.md, three references, `check_coverage.py`, `export_submittal_review.py`) plus an `annotate_pdf.py` fix and README pointers.
Adds `evals/plugin/submittal-review/` with a seeded-defect lab casework fixture (four planted defects) and nine graders.
Reports a 1.00 eval score on two runs with the sonnet judge.

1. "On this head it scored **1.00 on both runs**, every judge vote unanimous, judged by sonnet" (A) → `evals/plugin/results/` is gitignored and absent; no run record in the repo.
2. "The default judge model failed one run whose final message plainly contained every defect, so the README says to judge this case with sonnet" (A for the failure; M for the README) → `evals/plugin/README.md` line 16 says so.
3. "four planted defects: sink cutout … accessible station … in-wall brackets 'by others' … an elevation is missing" (M) → graders `sink-cutout`, `accessible-station`, `in-wall-brackets`, `missing-elevation` exist (plus `compliance-open`, `coverage-gate`, `disposition`, `no-agentcm`, `workbook` = 9 graders).
4. "SKILL.md (under 500 lines …)" (M) → 196 lines.
5. "Every step names its output file"; "Nothing is decided from memory"; "Unattended runs proceed and say what they assumed" (A/M by reading SKILL.md; not checked line by line).
6. "`check_coverage.py` must pass before anything is reported" (A, procedural).
7. "`--scaffold` never overwrites a file" (M) → script guards with `if not p.exists()`.
8. "It never approves, stamps or sends anything" (A).
9. "an `annotate_pdf.py` fix for current PyMuPDF" (M) → commit ad5828e, 3 insertions / 1 deletion.
10. "`293 files · 0 errors · 0 warnings · 0 lint · 293 at draft status`" (M) → reproduced.
11. "The tree at this head is identical to the original feature branch" (M) → **false**: `git diff origin/csi/9-submittal-review origin/feat/csi-knowledge-layer` shows an 11-line difference in `scripts/csi/csi_knowledge.py` (see §3).
12. "`evals/plugin/_fixtures/make_submittal_fixture.py` regenerates [the fixture]" (M) → script present.

### Cross-PR claims (all content PRs #6–#12)
- "The bar: every line should be something an expert PE would check and a capable model would not do reliably unprompted" (A).
- "Review against `AUTHORING.md` (the value test)" — AUTHORING §2 names the value test (M that it exists; A that it was applied).
- "Compiled output says so until a named PE reviews each file" (M) → every file `status: draft`, `reviewed_by: []`; **no file is PE-reviewed**.
- `claude plugin validate --strict .claude-plugin/plugin.json` (CLAUDE.md rule, not claimed in bodies) (M) → passes at HEAD.
- Resolver runtime (not claimed) (M) → `resolve --section "07 84 00"` 1.8 s; `validate --strict` 25 s.

---

## 2. What the review notes admit

**PR #5**
- Everything is `status: draft`; nothing is PE-reviewed. "Validation" means the resolver's own lint, not expert review.

**PR #6 (r1)**
- No 01 31 00 coordination-drawings profile ("I think the gap is real and costly"). Still absent at HEAD.
- 01 56 39 tree protection resolves to temporary facilities; needs a profile or alias with suppressions. Still absent.
- "Whether TIA-758-C has been published since its 2025 ballot" — not verified.
- Did not confirm the clause number of the consolidated ANSI A300.
- Divisions 31–33 keep non-standard short id prefixes (resolved by widening the AUTHORING rule, not by renaming).
- `01cp.patching-assigned` is "more a contract-scope item than a drawing red flag".
- Two overlapping topics (`adjoining-property-protection` ×2; `accessible-parking` ×2) — both since merged.
- `if.31-subgrade-paving` reaches 32 17 00 markings reviews: "minor noise".
- 07 81 00 title wrong ("Applied Fireproofing" vs "Applied Fire Protection") — fixed in integration.

**PR #7 (r2)**
- "The precast content is the least field-tested part."
- Stair and railing reviews "cluttered with 10–12 irrelevant edges until the resolver can exclude them" — resolver feature requested; since added (6aafe07) and applied.
- Hollow-core plank bearing on masonry has no edge (judged regional). 03 47 16 lift-slab inherits tilt-up content. `if.03-housekeeping-pads` endpoint was the whole of Division 11 — since narrowed.
- `04 20 00` inheritance note is incomplete (04 23 glass unit masonry picks up veneer checks). Division 04 baseline is heavy (9 checks).
- `if.01-structural-cutting` missed 03 23 00 / 03 41 00; `if.01-special-inspection-structure` missed 03 40 00 / 05 21 00 / 05 31 00; `if.park-barrier-anchorage` missed 03 23 00 — all since added.
- AISC DG11 2nd-edition content confirmed "through a secondary copy, not AISC directly".

**PR #8 (r3, r4)**
- Mass timber (06 17 19 CLT, 06 17 21 DLT) has no profile: "Do not rely on 06 17 19/21 until a profile exists." Still absent.
- Three pairs of near-duplicate items between 06 40 00 and 06 41 00 left in place; `06ac.site-conditions`/`06ac.cores` to be moved into 12 30 00 (ids no longer exist at HEAD; the acclimation text now sits in 12 30 00).
- Long lists of standards "confirmed from my own knowledge of current titles, not re-fetched" in 06, 08 and 09.
- 09 21 16 compiles 21 edges: partition-only submittals get ceiling edges ("noise, not error").
- Division 08 hooks compile into interior-only reviews ("noise, not error"); `if.08-radiation-shielding` reaches every door and glass review without a project filter; `08hm.frame-construction` wording "a PE should confirm it reads right"; coiling doors lack the spring-cycle check added to sectional doors.
- Confirm 08 35 13 covers fire-rated accordion doors some projects number 10 22 33 (still an open item in the body).
- `hc.headwall-conflicts` and `if.casework-headwall` describe the same exchange — still both present; the edge still carries `failure`.
- `if.06-accessory-backing` / `if.09-toilet-compartments` restate Division 10 failure modes ("acceptable as is", "minor").
- 11 41 00 has no panel-penetration check (near-copy of 13ce text avoided). 11 52 00 AV equipment unprofiled.
- Box-physics items duplicated across `11wi.*` and `13cs.*` ("the cost is maintenance"); needs an `includes:` resolver feature that does not exist.
- `14el.rh.communication` duplicates the Division 27 two-way-communication research (not split at HEAD). `14el.rail-supports` gate "late-ish".
- `if.05-suspended-equipment-supports` failure text appears in irrelevant Division 10/11 reviews — since resolved by suppression in 05 51 00/05 52 00 and dropping it from `caught_by`.

**PR #9**
- Same r4 admissions as above; walk-in split "would need an `includes:` mechanism the resolver doesn't have"; no 11 52 00 profile.

**PR #10 (r5)**
- `if.22-hvac-makeup` gate is "a judgment call"; left at `final_connection`.
- 22 45 00 still receives toilet-room edges through 22 40 00; "Edges cannot be suppressed" (true at the time; resolver now allows it).
- No 23 05 00 profile. `if.03-sleeves` landed on TAB and missed piping/duct — since repointed.
- Facility-specific edges from div-10/11/13 land on every sprinkler, duct and hanger review without facility filters (recommendation for other owners).
- 23 37 00 outlets and 23 34 00 fans "thinnest"; "moderate overall" confidence for Division 23.
- Many standards "not re-checked online".
- `28fa.fm.matrix-orphan` named `if.21-supervision` wrongly — since removed.

**PR #11 (r6)**
- New 26 05 19/26/33/43 profiles "deliberately lean"; a project with one combined 26 05 00 section depends on the reviewer following a scope-summary pointer.
- 28 05 37 alias: "Judgment call, moderate confidence … I found no project spec that actually uses 28 05 37 for ERRCS."
- 28 31 00 on pre-2016 projects compiles as intrusion detection; mitigated only by a note.
- Six edges naming "26 05 00" still land on studies/identification/seismic reviews; `if.03-housekeeping-pads` reached wiring devices (since narrowed).
- 26 20 00 checks still reach 26 27 13, 26 28 xx, 26 29 xx; division hooks reach wiring devices and lighting ("low priority").
- 26 05 73 level-4 titles "not verified, not used".
- Healthcare overlay ligature items omitted 27 52* and 26 27* — since added.

**PR #12 (r7)**
- Reflex list at 70 entries, "more than a reviewer can hold in mind"; about 30 items recommended for demotion — since trimmed to 37.
- Milestone order in milestones.yaml reads wrong in three places — partially reordered at HEAD (`hoistway_turnover` moved up; `interior_finish_start` now after `wall_close_in` but still before `above_ceiling_close_in` and `energization`).
- Three items gated wrong at the close-in milestones (`23tu.handing-access`, `14el.machine-room`, `11hc.shielding`) — all since regated to `procurement_release`.
- Building-line exchange has three homes (`if.22-building-line`, `22pp.rc.building-line`, `d33.rc.building-line`) — at HEAD only `22pp.rc.building-line` remains reflex; all three ids still exist.
- Recessed-in-rated-wall has three homes (`d10.recess-in-rated-walls`, `09gb.recessed-in-rated`, `if.09-recessed-specialties`) — all three still exist.
- `if.26-generator-fuel` in the wrong file — since moved to div-23.
- Broad `NN 05 00` and division-level endpoints in div-01/03/08/14 — since narrowed (checked: `if.03-sleeves`, `if.03-precast-mep-cast-in`, `if.01-cutting-patching-mep`, `if.08-access-doors-mep`, `if.14-conveying-power`, `if.03-housekeeping-pads`).
- Topic merges not made (admitted in the body): `foodservice-indirect-waste` vs `indirect-waste-receptors`; `laboratory-hazardous-materials-storage` vs `hazardous-materials-control-areas`; `fuel-storage-tank-requirements` vs `generator-air-and-fuel-permits` — all still separate at HEAD.
- `hc.ligature-resistant` (critical) reaches every healthcare review including clinics with no behavioral-health rooms; "a future `healthcare.behavioral` child overlay would be cleaner".
- `hc.agency-changes` runs across every trade (kept on purpose). `edu.maintenance-durable-finishes` is "the weakest item". `edu.storm-shelter` sections still exclude 26.
- `lab.eyewash-shower` partly repeats 22 45 00.
- "The remaining risk is in hook research quality, not in overlay content."

**PR #13**
- The default judge model fails a run that contains every defect; the score is reported only with `--judge-model sonnet`.
- No eval results are committed; the 1.00 score is a statement, not an artifact.
- The eval exercises one fixture (lab casework, 12 35 53) with four seeded defects; nothing exercises other divisions.

---

## 3. Claims that look overstated on their face

1. **PR #13: "The tree at this head is identical to the original feature branch."** False. `origin/csi/9-submittal-review` and `origin/feat/csi-knowledge-layer` differ in `scripts/csi/csi_knowledge.py` (11 lines): the feature branch raises `ResolveError` for any suppressed edge that does not reach the section, and drops the "no interface file defines" warning path that the stack branch has. Behaviour of `validate` differs between the two trees.

2. **PR #7 body vs r2 review on edge suppression.** The body says stair profiles "rely on edge suppression in the resolver (PR 1)" and PR #5 lists "suppressions (including edges)" as a resolver feature. r2 (inside PR #7) says the opposite: "Resolver feature (the most valuable fix): let a section profile `suppress` interface edge ids", and "Edges cannot be suppressed" (r5, PR #10). The feature was added after the reviews (commit 6aafe07) and back-ported into the stack, so the bodies describe the post-fix state while the folded review notes describe the pre-fix state. Not wrong at HEAD, but the "two commits: draft then review" narrative does not account for the integration changes that followed the reviews.

3. **Reviewer "final state" lines contradict the PR's own validation line.** r1 (PR #6), r2 (PR #7), r3 (PR #8), r4 (PR #8/#9), r5 (PR #10) each claim "`validate --strict` … 0 warnings for the whole layer" while the same PR body reports 10, 8, 5 or 4 warnings "at this stage". The reviewers ran against the full merged tree, not the stacked diff. Both are true of different trees; the review notes are not evidence about the PR as merged in order.

4. **File-count inconsistency inside the review notes.** r3 and r5 say the whole layer is 291 files; r2, r6, r7 and the bodies say 293. Reviewers worked at different snapshots. Harmless, but it shows the notes were not re-run at the published head.

5. **PR #6 body vs r7 on id prefixes.** PR #6 says the 31–33 short prefixes are "allowed by AUTHORING §4". r7 (PR #12) says the §4 exception covers "07 and 12 only" and that `wa.`, `sd.`, `dp.`, `pv.`, `es.`, `ef.`, `ps.`, `sa.`, `ir.` are not covered. At HEAD, AUTHORING §4 reads "Divisions 07, 12 and 31–33 use older short prefixes; leave them": the rule was widened to match the files rather than the files fixed. Only the `hc.` collision was renamed (`33hc.`).

6. **Reflex counts quoted in review notes are stale.** r1 "Reflex count is at the cap of three" (Div 01), r4 "Division 11 still has three reflex items", r7 "70 entries … Division 07 alone has 13". At HEAD the list has 37 entries, Division 01 has 2, Division 11 has none, Division 07 has 3. The body counts (8/7/7/3/4/4 "always-on red flags") do match the YAML `reflex: true` flags per group at HEAD, so the bodies were rewritten after trimming but the folded notes were not.

7. **r6 (PR #11) "Suppress 35 inherited 26ds items"** — 26-27-26.yaml has 34 suppress entries at HEAD. Off by one (likely an integration edit); nothing in the body notes the change.

8. **"Every standard verified against the publisher" is narrower than it reads.** Each reviewer separates "verified this session" from long "confirmed from knowledge, not fetched" lists (r3: ~60 designations in 06/08/09; r5: ~45 in 21/22/23; r6: ~25 in 26/27/28; r4: ~35 in 10–14). r2 confirmed AISC DG11 "through a secondary copy, not AISC directly". The review-checklist line "numbers and titles: current MasterFormat numbers and titles, and standard designations and titles" was therefore only partly executed against publishers.

9. **"I would let a junior PE rely on it" / "Confidence: high"** appears in every review note while every file is `status: draft`, `reviewed_by: []`, and the PRs say "Compiled output says so until a named PE reviews each file". The reviewer is the same drafting pipeline, not a named PE; the confidence statements are self-assessments.

10. **PR #13 eval claim ("1.00 on both runs, every judge vote unanimous")** has no artifact: `evals/plugin/results/` is gitignored and absent, the case is one fixture with nine graders, and the score is only reported with a non-default judge because the default judge "failed one run whose final message plainly contained every defect". The claim is also "on this head", which (item 1) is not the head that was published.

11. **PR #8 carries the r4 review notes for Divisions 10–14 verbatim, and PR #9 carries the identical text again.** Two PRs present the same review as their own evidence; the PR #8 body's "Divisions 06, 08, 09, 10, 12" scope does not match r4's "10, 11, 12, 13, 14".

12. **PR #5 "`validate` … including … id prefixes shared by two owners"** — that lint was added in commit 6aafe07 ("lint shared id prefixes"), after the content reviews that it would have caught (r7's `hc.` collision). The PR #5 body describes the final resolver, not what PR #5's stack branch contained when the reviews ran.

13. **Items the bodies say were "applied in the integration pass"** — verified applied: 07 81 00 title; `if.01-structural-cutting`/`if.01-special-inspection-structure`/`if.park-barrier-anchorage` endpoints; `23hs.fm.tendon-strike` caught_by + edge `failure` removed; "(not a stair or railing item)" removed; `if.03-sleeves`, `if.03-housekeeping-pads`, `if.14-conveying-power` narrowed; `28fa.fm.matrix-orphan` fixed; generator-fuel moved; `33hc.` rename; nfpa-285 slug renamed; three close-in gates fixed; `rf.roof-vapor-retarder` "kitchens" removed; healthcare ligature sections extended; two topic merges. **Not applied** (and not all listed as open in the bodies): the `hc.headwall-conflicts`/`if.casework-headwall` duplicate (listed), the three-home building-line and recessed-unit exchanges (not listed), `14el.rh.communication` split (not listed), full milestone reorder (not listed), `edu.storm-shelter` Division 26 (listed).
