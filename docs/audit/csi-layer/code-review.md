# Code review: CSI resolver and submittal-review scripts

Branch `feat/csi-knowledge-layer` @ 640ab78. All paths relative to `/home/user/claude-code-construction`.
Everything below was run with `bin/construction-python`; synthetic inputs are in the scratchpad (`minikb/`, `review/`, `proj/`).

## 1. Bugs and contract mismatches

### 1.1 Resolver (`scripts/csi/csi_knowledge.py`)

| # | Severity | What | Evidence |
|---|---|---|---|
| R1 | high | **Suppressing an edge that has `facility_types` breaks `resolve` and `validate`.** Edges are filtered by facility (`csi_knowledge.py:526-527`, `continue`) *before* the suppression check (`:536`), so a profile suppressing such an edge raises "does not reach this section" whenever the facility is absent. `validate` always resolves with `[]` facilities (`:1431`), so the KB can never validate. | Mini KB: `if.edge-fac` with `facility_types: [healthcare]` suppressed by 12 30 00 → `ERROR resolve 12 30 00 : 12 30 00: suppress of edge 'if.edge-fac', which does not reach this section`. Not yet triggered in the real KB only because the 6 facility-filtered edges happen not to be suppressed. |
| R2 | high | **Suppressing an edge leaves a false-positive `caught_by` warning when the failure mode has another live catcher.** `:583-589` checks catchers against the compiled lists after the edge is removed; SCHEMA M4 tells the author to "suppress any failure mode that names the edge along with it", which throws away the failure mode even when a check still catches it. `validate --strict` turns the warning into a failure (`:1441-1443`). | Mini KB: `d12.fm.x` caught by `[d12.b, if.edge-fac]`; after 12 30 00 suppresses the edge: `Failure mode d12.fm.x is caught by 'if.edge-fac', which is not a check…`. Real KB avoided it by suppressing whole failure modes (05 51 00 suppresses `05mf.fm.support-steel-orphan`). |
| R3 | high | **Edges match upward.** `related()` (`:159`) is symmetric, so an edge declared on `12 35 53` reaches a `12 30 00` or `12` review. SCHEMA §6 documents the direction "edge on 06 10 53 reaches 06 10 00" but AUTHORING §5 (`AUTHORING.md:62`) says the opposite ("An endpoint reaches its own lineage only"). Net effect: general-section reviews get specialised edges. | `resolve --section "12 30 00" --only interfaces` returns `if.lab-casework-fume-hoods`, `if.lab-casework-exhaust` (declared `a: ["12 35 53"]`, `interfaces/div-12.yaml:68-95`). Across the KB: 1 641 edge matches on 226 section profiles, **374 (23 %) exist only via a strict descendant**; `26 05 00` gets 45/45 edges this way, `23 30 00` 35/42, `26 20 00` 26/26. A division-level resolve of `23` gets 67 edges. |
| R4 | medium | **`same_as` silently drops the alias's own division baseline and intermediate ancestors; `coverage.missing` does not report them.** `:409-415` replaces the chain with the target's lineage plus the tail from the alias node. | `resolve --section "01 57 13"` → lineage `[global, 31, 31 20 00, 31 25 00, 01 57 13]`, `missing: []`; `profiles/01/_division.yaml` and `01-50-00.yaml` exist and are never loaded, with no warning. 06 41 00 likewise never loads `profiles/06/_division.yaml`. SCHEMA §4 ("compiles the target's lineage, then this file's own items") is technically honoured; M7/§7.1 "a gap in the knowledge base is visible, not silent" is not. |
| R5 | medium | **`legacy_numbers` cannot express MasterFormat 2004→2016 renumbering.** `resolve_section_id` (`:278-285`) consults the legacy index only when `normalize()` fails, i.e. only for non-6-digit inputs. Six-digit legacy numbers resolve to whatever lives at that number today. The only defence is prose in a `scope_summary`. | `resolve --section "28 31 00"` → title "Security Detection, Alarm, and Monitoring", lineage via `28 30 00`, and the scope_summary itself says "If the project's 28 31 00 … is fire alarm, this context is the wrong one: resolve 28 46 00 instead" (`profiles/28/28-30-00.yaml:17`). The mechanism is used exactly once in 293 files (`profiles/12/12-30-00.yaml:10`, `"12300"`). `--section 12300` works; `--section 078400` works. |
| R6 | medium | **Last commit on this branch changed suppress-of-edge semantics without a doc change.** `git diff origin/csi/9-submittal-review HEAD`: the other branch warns on a suppressed edge id that *no interface file defines* and errors only on a defined-but-unreached one; HEAD (`:560-561`) errors on both, and `validate` no longer filters the "no interface file defines" warning. HEAD is stricter and simpler, but a typo'd id and a legitimately-unreached id now get the same message ("does not reach this section"), which is wrong for the typo case. | Mini KB `if.edge-nowhere`: `ERROR … suppress of edge 'if.edge-nowhere', which does not reach this section` although nothing defines it. |
| R7 | low | **`--types` and `applies_if` drops are indistinguishable in `not_applicable`.** `filter_types` (`:663`) appends type-dropped checks to the same list, with no reason. | `resolve --section "12 35 53" --types "Product Data"` → `not_applicable` lists 15 ids mixing `g.contractor-designed` (applies_if) and `cw.counter-heights` (type). |
| R8 | low | **`confidence_floor` ignores borrowed failure text.** Edge `failure` text pulled from another profile's failure mode via `edge_failure_index` (`:552-554`) does not lower the floor; overlay status counts only when `applied > 0` (`:517`). Harmless today because all 293 files are `draft` (`grep -rh "^status:" reference/csi` → `293 status: draft`), so the floor is a constant. | — |
| R9 | low | `escalate` of a target that exists but is not in the compiled context is silently skipped (`:505-506`), and `escalate` can only target checks and hooks, not reconciliations (`:504`). SCHEMA §5 says "id from the section chain" without that restriction. | Mini KB `nonexistent.id` → warning only at validate time, nothing at resolve. |
| R10 | low | `--only` drops `suppressed` and `escalations` (`CONTENT_KEYS`, `:110-111`), so a sliced context cannot show the reviewer what was turned off, contradicting M4 ("suppressed items stay visible in the compiled output"). | `--only failures,extract` keys: no `suppressed`. |
| R11 | low | Facility order changes item order (`:484` iterates `facility_chain` in given order; overlay items are appended). M8 "ordered by layer and then by file order" is only true for a fixed argument order. Output is otherwise deterministic (two identical runs `cmp` equal). | `--facility foodservice --facility healthcare.hospital` vs reversed: `food.building-pressure` moves from position −5 to last. |

Things that worked as documented: `--types` rejects unknown labels with the full list; `--only` rejects unknown slices; two overlays load parent→child with `items_applied` counts and escalations recorded with from/to/by/reason; `--project` reads `education.k12` from `project_context.yaml`, binds hooks `unbound`, finds `spec_text/12_35_53.txt`; `06 41 00` is reviewed as `12 30 00` and `06 41 16` follows it; `milestone --id wall_close_in` lists position 21 of 29 and filters by project sections; bad milestone id lists the valid ones; `_from`, `_status`, `_chain`, `_patched_by`, `_escalated_by` are set correctly (mini KB, see §5).

### 1.2 `check_coverage.py`

Scaffold and the documented gates behave: `--scaffold 01 --elements` wrote 2 todo rows with `check_text`; `--scaffold 90 --package` wrote the package checks and reconciliations; re-scaffolding the same batch refuses; `--scaffold` without `--elements`/`--package` errors; one row left `todo` → `FAIL — 1 gaps`; a finding without `action` → `Finding F-001: action is required`; `export` refuses with the same gap list and exports with `--allow-gaps` marking the workbook `INCOMPLETE — 1 gaps`.

Silent acceptances (all in one run of the probe set; the gate reported exactly one gap):

| # | Severity | What | Evidence |
|---|---|---|---|
| C1 | high | **`coverage_pct` and the summary line count `todo` rows as present.** `:147` counts `key in rows`, regardless of status. The Excel Summary repeats it. | Four todo rows → `Coverage 4/4 (100.0%)`; workbook Summary: `4/4 element × check rows (100.0%)` while the gate says INCOMPLETE. |
| C2 | medium | Coverage rows for an element not in the inventory (`3/A-501`), for an unknown check (`bogus.check`), for an element-scope check at `package` level, and **duplicate rows** (last wins, `:140`) are all accepted. | Probe C: no gap for any of them. |
| C3 | medium | A finding whose `element` is not in the trace/inventory (`9/A-999`) is accepted; `submittal.file` out of range (7) is accepted (and `markup_items` later drops it silently, `export_submittal_review.py:218-219`). | Probe C. |
| C4 | medium | Routing rows naming a finding that does not exist (`F-999`) or an interface not in the context (`if.not-in-context`); compliance rows for hooks not in the context (`not.a.hook`) — all accepted. `check` ids on findings can be check/recon/hook but **not an interface id**, so a coordination finding tied to an edge must use `obs.<slug>` (review-data.md:98 agrees, but the edge id is the natural key). | Probe C: only gap was `Finding F-002: check 'if.edge-plain' is not in context.yaml`. |
| C5 | low | Malformed JSON in a batch file reports the parser message **without the file name** (`json.JSONDecodeError` is a `ValueError`, caught at `:94`). | `GAP   Expecting property name enclosed in double quotes: line 2 column 1 (char 2)`. |
| C6 | low | A `state.yaml` with no `submittal` block is accepted (types → `[]` → every check applies); nothing checks `sections`, `files`, `review_id`. | Probe F. |
| C7 | medium | **Stale `context.yaml` by design.** SKILL.md step 2 compiles the context *before* step 3 confirms facility types (`SKILL.md:82-84` then `:107`); re-running the resolve with `--output` writes `context_v2.yaml` (`safe_output_path`, `shared.py:6-19`) which `check_coverage` never reads (`:69`). | Second `resolve --output {dir}/context.yaml` → `Wrote …/context_v2.yaml`; `ls` shows both. |
| C8 | low | `applies()` (`:54-56`) re-filters by `state.submittal.types` although `context.yaml` was already produced with `--types`; harmless but means two sources of truth for "which checks apply". | — |

`export_submittal_review.py` ran on the synthetic dir with `--allow-gaps --annotations`: 7 sheets, one markup JSON; emits a PyMuPDF deprecation warning (`import fitz`, `:208`). Disposition logic is as documented.

## 2. Is the resolver the right abstraction?

Usage counts over 293 YAML files (250 profiles, 15 overlays, 27 interfaces, 1 milestones), 4 496 ids, 274 edges:

| Mechanism | Count | What it buys a reviewer | Lost with "one markdown per section" / flat YAML |
|---|---|---|---|
| Cascade global → division → section | every resolve; `_global` has 10+ checks, divisions ~15-20 | 18-19 inherited checks even for sections with no profile (`09 91 23`, `08 71 13`) | Flat: 226 copies of the global/division checks, or a convention "also read `_division.md`". Real value; a 3-file concatenation would deliver 90 % of it. |
| Overlays with glob `sections` | 15 overlays, 287 per-item `sections` globs, 12 `escalate` blocks / 29 targets | Healthcare adds 13 items to 12 35 53 without touching it | Markdown: an overlay file the reviewer reads next to the section. The glob matcher is small (`:331`), but per-item globs (287) mean the *author* decides reach per line; that is the same work as a table in a markdown file. |
| `equivalents` | 28 files | A warning when the project specs the scope under another number (requires `--project`) | Trivially a line of prose. |
| `same_as` | 15 files | 06 41 00 is reviewed as casework | Needs code (chain re-rooting), but it hides the alias's own division (R4). A markdown "see 12 30 00" costs nothing and loses nothing. |
| `legacy_numbers` | **1 file** | `--section 12300` | Dead weight; cannot express the renumbering that actually bites (R5). |
| `suppress` | 35 files, **235 entries**; 05-51-00 (16), 05-52-00 (19), 26-27-26 (34), 11-41-00 (20) | Removes inherited items; the last commit extended it to edges | 235 suppressions is the cost of inheritance, not a feature: 05 51 00 suppresses 11 edges because stairs sit under misc metals. A flat file simply would not list them. Edge suppression exists *because* of R3. |
| `override`/`merge` | 13 overrides (8 files), 7 `merge: replace` | Patch a parent's severity/wording | 13 uses in 4 496 ids: rounding error. Flat files restate the item. |
| `applies_if` | 34 items in **5 files** (28 of them in `profiles/23/_division.yaml`) | One global rule fires only on contractor-designed scopes | 2 keys only; a sentence "applies when contractor-designed" does the same for a reader. |
| `reflex` | 44 items (39 files) + 2 edges | `reflexes` view, 37 entries | A hand-kept list of 37 bullets would be shorter than the code that compiles it; the view is empty for a project filtered to one section (`reflexes --project` → 0). |
| `gate` / milestones | 765 item gates + 155 edge gates, 29 milestones | `milestone --id` compiles what is due before close-in | Genuine cross-cutting query; cannot be done with per-section markdown without grep. Keep. |
| `escalate` | 29 targets | Overlay raises severity without copying the check | Same as override, overlay-side; could be `override` if M5 were dropped. |
| Lint: bare numbers / near-duplicates / prefix ownership | 0 hits on current KB | Keeps K1 honest | Useful and cheap except near-duplicates (O(n²), ~2.5 s). Keep as a separate script. |

Verdict: the schema is overbuilt relative to its use. Three mechanisms carry the value: the cascade (inheritance of global/division checks), gates/milestones, and interfaces as edges read from both sides. `same_as`, `legacy_numbers`, `override/merge`, `applies_if`, `escalate` and edge-suppression together touch < 2 % of ids and exist mainly to patch consequences of inheritance (R3, R4). The cost shows in the compiled output: 12 35 53 for a hospital is 46 KB YAML / 33 KB markdown (35 checks, 17 failure modes, 10 hooks, 12 interfaces); `23 30 00` is 42 KB with **41 interfaces**, 35 of them reaching it only through descendants. A reviewer (or subagent) reads that in one prompt. A flatter design (one YAML per section with *explicit* `inherits: [global, 23]`, edges that name the sections that should see them, no upward matching, no suppress) would need ~⅓ of the resolver and would remove 235 suppress lines.

## 3. Performance

| Command | Wall time |
|---|---|
| `validate` | **24.5 s** |
| `resolve --section "12 35 53" --facility healthcare.hospital --format md` | 1.9 s |
| same with `--only checks,hooks,interfaces` | 2.3 s (slices after compile, no saving) |
| `python -c "import yaml"` | 0.04 s |

Where it goes (cProfile):
- `validate`: 4 233 `resolve()` calls (249 sections × 17 facility sets, `:1431-1437`) = 81 % of the time. Inside, edge matching dominates: `lineage()` is called **9.4 M times** (`:136`, no memoisation, 22.6 s self-time under profile), `normalize()` 4.7 M times. Adding `functools.lru_cache` to `lineage` and `normalize` alone cuts `validate` from 22.7 s to **11.5 s** (measured by monkey-patching). Pre-normalising edge endpoints once would remove most of the rest. `near_duplicates` is O(n²) over ~1 500 texts: 8.8 s profiled ≈ 2.5 s real. YAML parse of 293 files: ~2 s.
- `resolve`: 95 % is YAML parsing of **all 292 files**, because `edge_failure_index` (`:259-275`) loads every profile and overlay to find failure modes that name edges. A single-section resolve needs ~6 files. A cached index (or storing the failure text on the edge) would make resolve ~0.1 s.

25 s is tolerable for CI once per push but not for authoring (an author re-runs it after every edit; the SKILL docs tell them to). A 10× improvement is available with ~20 lines (memoise, pre-normalise, cache the index).

## 4. Maintenance

Finding a wrong item: `_from` gives the defining file for any compiled item, `_patched_by` the overriders, `_escalated_by` the overlay — adequate. Overlay items say `overlay:healthcare` not the path; interface items say `interfaces:div-12`. `validate --focus` narrows the 25 s run's *output*, not its runtime.

Cross-reference web (script over the KB): 4 496 ids; **1 555 `caught_by` references, 303 cross-file**; 765 gate references into 29 milestones; 235 suppress references; 29 escalate targets; 13 overrides; 349 distinct edge endpoints, **160 of which have no profile file**. Most-referenced files: `profiles/10/_division.yaml` (46 inbound), `interfaces/div-03.yaml` (36), `profiles/26/26-20-00.yaml` (34).

Renaming: ids are global strings with no tooling. Renaming `12-30-00.yaml`'s 38 ids would break 15 references in 6 other files (`overlays/{education,healthcare,healthcare.hospital,residential}.yaml`, `12-35-53.yaml`, `12-36-00.yaml`). Renaming a *section number* (e.g. moving a profile) changes 349-endpoint edge matching silently, since endpoints without a profile are legal. `validate` catches dangling `caught_by` only through per-resolve warnings (not when the catcher is on a facility-filtered edge, not for overlay failure modes whose globs hit no resolved section) and dangling `escalate` as a warning; dangling `suppress` is an error. Prefix ownership lint keys on the first dotted token, so `d23.` vs `23ad.` is fine but any two divisions sharing a mnemonic by accident collide only at lint time.

Brittleness driver: inheritance plus symmetric edge matching means a new edge on `26 05 33` appears in every `26 05 00` and `26` review without the author of those profiles knowing; the only remedy is a `suppress` line per affected profile.

## 5. Determinism and provenance

- `_from` / `_status` / `_chain` / `_patched_by` / `_escalated_by`: correct on the mini KB. `g.a` defined in `global` (field_validated), patched by `12 30 00` (draft) → `_from: global, _status: draft, _patched_by: ['12 30 00']` (M7 holds). `merge: replace` drops the parent's `gate` as expected. Child overlay overriding parent overlay works.
- `confidence_floor`: correct for layers, applied overlays and matched interface files; ignores borrowed failure text (R8). Moot while every file is `draft`.
- `coverage.missing`: lists chain nodes without a file (`09 91 23` → `['09 91 00', '09 91 23']`), but **omits ancestors dropped by `same_as` re-rooting** (R4) and never lists facility overlays as "loaded but 0 items applied" distinctly from missing (it does: `items_applied: 0`, fine).
- `not_applicable` conflates two reasons (R7).
- Determinism: two identical invocations produce byte-identical YAML; item order depends on `--facility` order (R11); `validate` output is sorted for warnings/lint but errors keep discovery order (fine, deterministic).
- `warnings` carries the only signal that a section has no profile ("compiled from ancestors only"); the title shown is the nearest ancestor's (`08 71 13` → "Door Hardware"), which a reader could mistake for a real profile.

## Recommended fixes, in order
1. Check suppression before the facility filter (`:526-540`), and distinguish "undefined id" from "does not reach" (R1, R6).
2. Make edge matching downward-only (or require explicit `reach: ancestors`), then delete most of the 235 suppress lines (R3).
3. Report dropped ancestors under `coverage` for `same_as` (R4).
4. Memoise `lineage`/`normalize`, pre-normalise edges, cache `edge_failure_index` on disk or inline the text (§3).
5. `check_coverage`: count only non-todo rows in `coverage_pct`; reject rows/findings/routing/compliance that reference unknown elements, checks, interfaces, hooks or findings; include the file name in JSON errors (C1-C5).
6. SKILL.md: re-resolve after the facility checkpoint and write to the fixed name (`context.yaml`) instead of a versioned one, or make `check_coverage` read the newest `context*.yaml` (C7).
