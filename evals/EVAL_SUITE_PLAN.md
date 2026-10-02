# Eval Suite Plan: All Skills (draft for review)

Status: draft, 2026-10-01. Nothing here is built yet. This document sets the direction for the new eval suite, classifies each skill by what it needs to be evaluated, inventories the synthetic data and hand-made ground truth we have to produce, and lists the open decisions.

It replaces the "Planned coverage" table in [`evals/plugin/README.md`](plugin/README.md) and the earlier runner-based eval framework, which has been removed.

## 1. Decisions and requirements

| | |
|---|---|
| **Test set** | Sanibel Fire and Rescue Station 172, at `evals/test_docs/SANIBEL FIRE AND RESCUE STATION 172/`. The folder is tracked except `01 - Drawings` and `02 - Specifications`, whose PDFs are downloaded separately. |
| **Platforms** | The suite must run on Windows, macOS and Linux. |
| **Direction (recommended)** | Build two layers (section 2). |

## 2. Architecture: two layers

**Layer 1: script tests.** Python tests with fixtures and ground-truth JSON, no LLM, no cost, no network. They cover the deterministic code: the xlsx and docx exporters, the PDF splitters, `issue_manager.py`, the markup scripts, `safe_output_path`. They run on all three platforms through `bin/construction-python`, and they catch most of the script/doc mismatches in section 6.

The earlier runner-based framework was this kind of test in spirit. It was removed on 2026-10-02: it pointed at skill paths and skill names that no longer exist, and its expected files came from a different project than its cases. Layer 1 is a rebuild, not a revival.

**Layer 2: agent evals.** Run the real skill through Claude Code on a prepared workspace, then grade what it produced. Existing smoke cases in `evals/plugin/` already work this way with `claude plugin eval`.

### Windows finding (tested)

On this machine (Windows 11, Claude Code 2.1.287):

```
claude plugin eval . --case project-setup --runs 1 --ablation none --allow-tools Bash Write Edit
```

was refused at $0.00 with:

> sandbox required but unavailable: sandbox is enabled but the Windows sandbox is not active on this session (feature gate off)

The plugin-evals docs say the same: native Windows has no sandbox backend, so shell-granting suites need WSL2. The error says "feature gate off", so this may change in a later release. Every skill runs its scripts through Bash, so this blocks all of Layer 2 on native Windows.

### Layer 2 on Windows: decision needed

| Option | Meets "runs on Windows"? | Cost |
|---|---|---|
| **A.** `claude plugin eval` only (mac, Linux, WSL2); native Windows gets Layer 1 plus the manual checks in `docs/VALIDATING.md` | No, for agent evals | None. Already built. |
| **B.** A thin driver on `claude -p` (`--plugin-dir`, `--allowedTools`, `--output-format stream-json`, `--max-budget-usd`) that reads the same case files and grades with Python validators | Yes | A custom harness to build and maintain. Gives up plugin-eval's graders, HTML report and with/without-plugin comparison. **On Windows the agent's shell commands run unconfined**, which is exactly what `plugin eval` refuses to do. |
| **C.** Wait for the Windows sandbox to leave its feature gate | Eventually | Not in our control. |

Recommendation: build Layer 1 first, since it is needed under every option. For Layer 2, B is the only option that meets the cross-platform requirement today. If it is built, make it the one Layer 2 harness on all three platforms, not a Windows-only fallback beside `plugin eval`: two harnesses with two grading systems would double the maintenance. Its Python validators can open the real `.xlsx` and `.docx` deliverables and compare them with ground-truth files, which removes the JSON workarounds in section 7. Choose B only if you accept unconfined shell commands on Windows, with mitigations: a throwaway workspace under the temp directory, a restricted `--allowedTools`, a hard `--max-budget-usd`, and the plugin under test being our own. Keep the four existing `plugin eval` smoke cases as they are.

Prove the harness on one skill before fanning out. schedule-extractor on sheet A500 is the natural first slice: one sheet, a clean table, and ground truth that is quick to make (section 3).

Before building B, run one smoke case through `claude -p` on Windows. That checks that `--plugin-dir` loads the plugin, that `/construction:<skill>` runs, and that the stream-json trace has the tool calls we need to grade.

## 3. The test set (checked against the PDFs)

| File | Contents | Size | Text layer |
|---|---|---|---|
| Architectural Set (2024.01.05) | 90 sheets, 42 x 30 in | 58 MB | 100% of pages |
| Civil (2023.12.22) | 11 sheets, 36 x 24 in | 12 MB | 100% |
| Electrical (2024.01.05) | 16 sheets, 42 x 30 in | 11 MB | 100% |
| Mechanical (2024.01.05) | 8 sheets, 42 x 30 in | 3.3 MB | 100% |
| Project Manual Vol 1 | 798 pages, Divisions 01-14 | 6.5 MB | 96% (771 pages) |
| Project Manual Vol 2 | 694 pages | 6.8 MB | 97% (678 pages) |

Project facts from the project manual title pages: Sanibel Fire and Rescue Station 172, 100% Construction Documents, issued January 5, 2024, commission no. 2023820. Owner: Sanibel Fire and Rescue District. Architect: Schenkel Shultz Architecture. Structural: TRC Worldwide Engineering. MEP/FP/technology: OCI Associates. Civil: RESPEC. Landscape: "Costal Vista Design" (spelled as printed). The architectural project summary describes a new two-story fire station built after demolition of an existing building.

What this means for the suite:

- **"Smaller set" holds for drawings only.** 125 sheets across four PDFs. The specs are 1,492 pages with well over 100 sections, so spec-splitter on the whole manual followed by submittal-log-generator on every section will exceed the run limits (`timeout_seconds` is capped at 3,600). Scope the spec cases to one division or a pre-split subset of sections.
- **Five disciplines are not in the set.** The cover sheet (G000) indexes 172 sheets. The four PDFs hold 125. Structural (S, 16 sheets), plumbing (P, 12), fire protection (F, 7), technology (T, 5) and landscape (LP, 8) are indexed but absent. If this is deliberate, it limits pe-review's cross-discipline checks to architectural, electrical, mechanical and civil, and it rules out the plumbing and structural schedules (P601, S201). Open question in section 8.
- **The door schedule is confirmed.** Sheet A500 (page 64 of the architectural set) holds a 55-row by 16-column table with a text layer: two header rows (DOOR PANEL spans width, height, type and material) and about 53 doors. It is the schedule-extractor target. Secondary candidates, not yet checked: E003 (lighting fixtures), E701 (panels), M601 (HVAC), A460 (toilet accessories), A171 (furniture and equipment). The finish material is on A160, which mixes code schedules and legends and is a poor first pick.
- **The sheet list can be derived by script.** The title-block sheet number is the largest text on every architectural, electrical and mechanical page, and G000 carries number and title for every sheet. One thing needs a manual check: the civil set, whose title block is not readable this way. Sheet numbers are not all plain letter-plus-digits (page 32 of the architectural set is `A160-A`), which is a useful case for sheet-splitter.
- **Keyword hits in the spec PDFs are cross-references, not schedules.**
- **Jurisdiction.** The civil sheet says City of Sanibel, Florida, so code-researcher ground truth is the Florida Building Code, not the IBC directly, while the offline reference tables in `reference/` are IBC 2021. The adopted code edition, occupancy and construction type are ground-truth items to pull from sheet G010 (Code Summary & Calculations), not to write from memory.
- **Bid scope.** Division 09 has a workable flooring package: 09 30 00 Tiling, 09 65 13 Resilient Base, 09 65 40 Luxury Vinyl Tile, 09 65 67 Resilient Athletic Finishes, 09 67 00 and 09 67 10 Resinous Flooring. The only owner alternate in 01 23 00 is a roofing one (Alternate No. 1, training roof make-up), so flooring bids must carry their own alternates, defined in a synthetic bid-package scope sheet.
- **Run cost.** sheet-splitter makes one vision call per sheet, so Layer 2 cases should use a trimmed sheet subset rather than all 125.

## 4. Skill classification

| Skill | Verdict | Condition |
|---|---|---|
| project-setup | Yes (plans+specs) | In the smoke tier. The real set adds ground truth: document locations and disciplines. |
| sheet-splitter | Yes (plans) | In the smoke tier. The real set adds the sheet list. Use a subset. |
| spec-splitter | Yes (specs) | Text layer is present. Scope to a subset of sections. |
| submittal-log-generator | Yes (specs) | Scope to one division or a pre-split subset. Needs ground-truth items for 2-3 sections. |
| schedule-extractor | Yes | Target: the A500 door schedule. Standalone output is only the xlsx. |
| tag-audit-and-takeoff | Yes, to confirm | Flat mode only (vision, no OCR). Door tags on the floor plans against the A500 schedule gives a completeness check. The floor plan sheets are not yet looked at. Hand-count ground truth. |
| pe-review | Yes | Needs real conflicts found by someone with PE judgment (section 5). Limited to the four disciplines in the set. |
| rfi-drafter | **Partial** | Needs a seeded issue, and the prompt must supply RFI number, from-party and dates. Template mode needs a synthetic template. Registry operations are deterministic (Layer 1). |
| code-researcher | **Partial** | Offline it can only do Pass 1 and mark the rest `uncertain`. Grade the project inventory, the framing rule (no COMPLIANT / NON-COMPLIANT) and `uncertain` handling. It stops at checkpoint 1c. |
| construction-guide | Partial | A behavior skill. Grade from traces (no direct PDF read, rasterize first, `[Sheet X]` citations, confidence labels) plus 3-5 known-answer questions. |
| viewport-highlighter | **No** | Needs AgentCM. Testable: the refusal message and `markup_viewports.py` with a hand-made items file. A mocked API is deferred. |
| bid-tabulator | No | Needs synthetic bid PDFs. |
| bid-evaluator | No | Needs tabulator JSON from synthetic bids, plus a real spec section for the scope baseline. |
| subcontract-writer | No | Needs an awarded bid, a firm template and spec sections (a missing awarded bid stops it at Phase 1). |

Corrections to the earlier planned-coverage table:

- bid-tabulator only reads PDFs, so the "different format" bid is a letter-style PDF, not Excel.
- bid-evaluator never renders `scope_baseline.alternates` in its xlsx, so a "missing alternate" defect is only gradable in its JSON.
- A Baltimore or Maryland reference in code-researcher output is contamination from the worked example shipped inside that skill (see section 8). Add it as a grader to the code-researcher cases.

## 5. Data we have to produce

### Synthetic documents

| Artifact | Serves |
|---|---|
| **5-bid package** on one real Sanibel spec section (table below) | bid-tabulator, bid-evaluator, subcontract-writer |
| Per-bid ground-truth JSON in the tabulator schema, plus a planted-defect manifest | bid-tabulator, bid-evaluator |
| Firm subcontract template `.docx`: 15 articles, one legally flawed indemnity (see fix 4 first), stale example party names | subcontract-writer |
| Firm RFI template `.docx` plus mapping JSON, with a distinctive firm marker and without the generic "RESPONSE" heading | rfi-drafter template mode |
| Prompt text: seeded RFI issues, GC name, subcontract number, LD rate, pre-answered scope questions | rfi-drafter, subcontract-writer, bid-evaluator, bid-tabulator |

The bids must be written against a real Sanibel section whose Part 1 has submittal and warranty text (subcontract-writer blocks without it). The folder's `16 - Templates/` holds generic bid-form, bid-tab and procurement-log templates that could shape the bid layouts; not yet reviewed for fit.

| Bid | Format | Planted defect or feature |
|---|---|---|
| A | Text-layer PDF | Clean. Becomes the awarded bid for subcontract-writer. |
| B | Text-layer PDF | Silent scope omission, plus a line-item sum that does not match the stated total. |
| C | Multi-page text PDF | Exclusion buried in a qualification, a budget-only qualification, an add and a deduct alternate (same names across bidders), unit prices with units, an allowance. Alternates on page 2 or later. |
| D | Image-only PDF | Scanned copy, to exercise the vision path. One ambiguous value that should be flagged `[unclear]`. |
| E | Letter-style text PDF | Different layout from the owner bid form. |

Generation notes: write `ADD $x` / `DEDUCT $x` inside qualifications in exactly that form (the tabulator parses it with a regex). Bidder names must match between tabulator and evaluator JSON. Other evaluator defects worth planting: explicit exclusion of a spec-required item, inclusion of a GC-provided item (should give a negative adjustment), a unit price over 2x the median, more than 5 qualifications, a missing addenda acknowledgement. The evaluator should flag a math error without correcting it.

### Ground truth from the real set (hand-made, except the sheet list)

| Artifact | Serves |
|---|---|
| Page count and sheet list (number and title): script-derived from the title blocks and G000, with a manual check of the civil set (section 3) | sheet-splitter, project-setup |
| Spec section list for the chosen subset | spec-splitter |
| Submittal items for 2-3 sections | submittal-log-generator |
| One transcribed schedule | schedule-extractor |
| Tag counts per sheet | tag-audit-and-takeoff |
| City/state, occupancy, construction type, sprinklered status, adopted code edition, citations present in 1-2 sections, known absences | code-researcher |
| 3-5 factual Q&A pairs | construction-guide |
| **Real drawing-vs-spec conflicts and gaps** | pe-review, rfi-drafter seed issues |

You cannot plant a conflict in a real PDF drawing set. Either someone with PE judgment finds real conflicts in the Sanibel set, or we add a synthetic addendum sheet that introduces one. Recommendation: real finds, plus at most one synthetic addendum.

## 6. Fix before eval

These make graders fail by construction. All five were re-checked directly against the files on 2026-10-01. They are bugs users hit today, with or without evals.

1. **schedule-extractor** `SKILL.md:236-237` uses `--source_sheet` and `--output_file`; `write_finding.py:56,58` takes `--source-sheet` and `--output-file`.
2. **tag-audit-and-takeoff** needs `rasterize_page.py` (`SKILL.md:40`) but does not allow-list it (`:348-350`). Its output path is contradictory between `:288` and `:302`.
3. **pe-review** never writes to the issue registry, but `rfi-drafter` and `issue-schema.md:111-115` say it does. Fix the docs or add the step.
4. **subcontract-writer** appends its output after the template's existing body instead of filling placeholders (`generate_subcontract_docx.py:32-37`). Template-mode grading and the template design depend on this.
5. **bid-tabulator** promises lowest/highest highlighting and a Total row (`SKILL.md:140-142`) that the script does not build. There is also no "Base Bid" row, and allowances are never rendered.

Secondary:

- **bid-evaluator** has no converter from tabulator JSON to its own input schema. The LLM re-derives it, so the transform is what gets graded.
- **sheet-splitter** does not say how `sheet_index.yaml` follows a rename, and a re-run re-adds `page_NNN` entries (`split_drawing_set.py:135`).
- **spec-splitter** says it skips existing sections (`SKILL.md:184`), but `split_pdf` always overwrites.
- **submittal-log-generator** merges batch files with `jq` (`:405`), which may not exist on Windows.

## 7. Harness constraints (`claude plugin eval`)

1. **No custom graders, and no direct `.xlsx` / `.docx` grading.** The grader types are `regex`, `tool_used`, `tool_order`, `file_exists`, `llm` and `baseline`, and the LLM judge refuses binary files. All seven xlsx/docx-producing skills write a text JSON before exporting, so grade that JSON.
   - The path is fixed for submittal-log-generator, bid-tabulator and tag-audit-and-takeoff.
   - It is not fixed for schedule-extractor, bid-evaluator, rfi-drafter and subcontract-writer, so those prompts must pin it.
   - Renderer behavior (tab names, formulas, highlighting) belongs to Layer 1.
   - Ground truth lives inside `llm` grader rubric text, so large tables are awkward, and numeric tolerance is only judgeable by the LLM. A Layer 2 driver with Python validators (option B) removes this limit.
2. **Six skills have user-confirmation gates:** tag-audit-and-takeoff, code-researcher, rfi-drafter, bid-tabulator, bid-evaluator, subcontract-writer. The only mechanism is pre-answers via `append_system_prompt`, so the evals do not test whether a skill actually stops to ask. The docs do not say what `AskUserQuestion` does in an eval run.
3. **No network from tools.** code-researcher cannot verify codes online. The first run of `bin/construction-python` pip-installs, so the venv must be pre-built (the existing `prepare-workspace.sh` does this).
4. **Limits:** `max_turns` default 10, cap 200. `timeout_seconds` default 300, cap 3600. The scaffold script has a 120-second limit.
5. **Workspaces:** `--keep-temp` preserves each run's workspace and `trace.jsonl`, so an out-of-harness Python scorer can read the output files. Not yet tested on a passing run.

## 8. Open items

**Needs your decision:**

1. **Missing disciplines.** Structural, plumbing, fire protection, technology and landscape sheets are in the cover index but not in the set (section 3). Deliberate, or are there more PDFs to add?
2. **Layer 2 on Windows:** option A or B (section 2).
3. **Download links** for the six PDFs (placeholders are in `docs/RUNNING_EVALS.md`).
4. **Permission to share the set.** Sanibel was previously kept as an internal-only test project, and the sheets carry the architect's copyright notice. Publishing download links makes the set public, so confirm that is intended.

**Still to change:** code-researcher's worked example (`SKILL.md`, `references/schemas.yaml`, `references/gap_report_template.md`) describes a Baltimore, Maryland project. Moving it to Florida needs verified code citations, so it belongs with the code-researcher ground-truth work.

**Not yet verified:** whether `claude -p` loads the plugin and runs a skill unattended on Windows; whether a `claude -p` driver can turn the sandbox on where the OS has one (macOS, Linux); what `AskUserQuestion` does inside an eval run; whether granting only `Write` (no Bash) avoids the Windows restriction; whether symlinks are allowed in case folders (the existing scaffold avoids them).

## 9. Build order

1. Resolve the open decisions above.
2. Layer 1 script tests, and the fix-before-eval list.
3. Ground truth and the trimmed subsets.
4. Synthetic bids, templates and prompts.
5. Layer 2 cases, starting with the plans-and-specs skills.
