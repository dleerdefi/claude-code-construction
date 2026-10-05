# Construction skills: gap analysis and candidate new skills

**Status:** findings, with the first-skill decision made (section 8) · **Written:** 2026-10-02, facts refreshed 2026-10-04 · **Repo:** `claude-code-construction` (plugin v0.4.0, branch `integrate/skills-foundation`)

The question: which additional skills would be most valuable to a construction PE or PM, given that Claude Code works on construction documents rather than a code repository?

---

## 1. Where the plugin stands

There are 14 production skills (viewport-highlighter was deprecated on 2026-10-04 and submittal-review added), and every one has a passing eval case in `evals/plugin/` (one run each through the harness on Windows, 2026-10-02 to 2026-10-04; the 366-page foodservice case has only been measured under `claude plugin eval`). See `evals/plugin/README.md` for what each case checks and the suite's known issues.

| Phase | Skills today | Missing |
|---|---|---|
| Setup / builders | project-setup, sheet-splitter, spec-splitter | per-sheet drawing text index (no equivalent of `spec_text/`) |
| Precon / buyout | bid-tabulator, bid-evaluator, subcontract-writer, submittal-log-generator | trade scope packages (exist only inside bid-evaluator), procurement log |
| Document reading / review | schedule-extractor, tag-audit-and-takeoff, code-researcher, pe-review, rfi-drafter, submittal-review, construction-guide | cross-reference resolution / set audit |
| **Construction administration** | rfi-drafter (drafting, no tracking), submittal-review | revisions/addenda/bulletins, change events, Div 01 obligations, meetings, pay apps, RFI log tracking |
| **Closeout** | none | warranties, O&M, attic stock, training, tests & inspections, record documents |

**Main finding:** the plugin is strong on setup and precon but has almost nothing for what happens after the documents are issued. That is where PEs and PMs spend most of their time. The Sanibel test set ships blank RFI-log, procurement-log, punch-list, daily-report and rough-in-inspection templates, and no skill uses any of them.

### Existing plumbing problems (these affect the value of any new skill)
- **The issue registry has almost no producers.** Only rfi-drafter and submittal-review call `scripts/issue_manager.py`. pe-review, tag-audit, code-researcher and submittal-log are documented as producers (`skills/rfi-drafter/references/issue-schema.md:110-116`, `skills/construction-guide/SKILL.md:258`), but none of them writes issues.
- **Findings sit in three separate stores that nothing connects:** the issue registry (JSON), pe-review's markdown memory (`rfi_candidates.md` etc.) and AgentCM's `agent_findings/`, which nothing reads. `query_findings.py` is unused.
- **Two capabilities were lost and never replaced:**
  - **spec-parser**, removed in `5ab70df`: product requirements, manufacturers and QA criteria per spec section.
  - **sheet-index-builder's revision tracking**, also removed in `5ab70df`: scale and revision fields per sheet.
- **Shared scripts with no current user:** `pdf/extract_annotations.py` (Bluebeam markups), `vision/analyze_title_block.py`, `graph/query_findings.py`, `bulk/consolidate_extraction.py` (`pdf/extract_text_region.py` is now used by submittal-review).
- **`reference/pe_expertise/`** (trade-scope notes and `pe_behavior.md`) is gitignored and, since 2026-10-04, untracked; nothing in the shipped skills reads it. It remains a candidate knowledge base for scope or buyout skills if it is ever brought back.
- **Open bugs** (tracked in `evals/plugin/README.md`, Known issues):
  - subcontract-writer appends to the template instead of filling its placeholders;
  - bid-tab is missing its totals and highlighting;
  - subcontract-writer (531 lines) and submittal-log (504) are over the 500-line limit.

---

## 2. Evidence

- **The author's forum study** (unpublished; 9,361 threads across construction-software forums). It classified 9,361 threads across Bluebeam, Autodesk and Procore.
  - #1 gap is **Document Management** (versioning, organization), score 749.
  - **Markup** is #2 (709.7) and **UX** #3 (702.7).
  - On Bluebeam, users value **Overlay & Comparison** (838) and **Batch & Automation** (700) most.
  - Users ask for *automation*, not chat. The thesis: "treat your documents like a codebase."
  - Relevant individual requests:
    - export text-search results to Excel;
    - batch link fails to recognize callouts;
    - title block to CSV;
    - spec TOC parsing errors;
    - checklist templates reused across projects;
    - milestone tracking across jobs.
- **Autodesk/FMI "Construction Disconnected" (2020):**
  - 35% of time goes to non-optimal activities, about 5.5 hours a week of it hunting for information such as revised drawings;
  - 48% of rework traces to bad data or communication.
- **Market validation** (web research; vendor performance numbers unverified):
  - **Submittal vs spec compliance** is crowded: Trunk Tools, Procore Submittal Review Agent, BuildSync, Kojo ($49M Series C). It is the most-cited PE time sink.
  - **Contract and notice risk:** Document Crunch, acquired by Trimble. AIA A201-2017 sets a 21-day claim notice and 14 days for concealed conditions, and work done without notice can be waived.
  - **Spec to closeout / tests & inspections registers:** Pype AutoSpecs and Pype Closeout.
  - **Overlay:** Bluebeam Max Smart Overlay, launched May 2026.
  - **Meeting minutes and RFIs:** Procore AI agents.
  - **Cross-reference checking that verifies references resolve:** no product found, so likely whitespace.
- **An earlier idea backlog** (a prior draft of the SOP):
  - **Chains:** RFI → schedule impact → RFI-ASI reconciliation → resubmittal; bid leveling → scope matrix → CO pricing → lead times; closeout chain (punchlist → O&M verification → closeout tracking).
  - **Planned references:** `submittal_routing_rules.md`, `division_scope_matrix.md`, `conflict_escalation_protocol.md`, `critical_path_definitions.md`, `closeout_checklist_schema.md`.
- **Unshipped `_dev` skills from an earlier checkout:** bulk-sheet-extraction, construction-browse, coordination-report, qa-qc-auditor, quantity-takeoff, scale-measurement, plus an old rfi-drafter. The qa-qc-auditor is a 113-line checklist prompt with no scripts, and it overlaps pe-review.

---

## 3. Seeing a drawing set as a codebase

Claude Code's advantage over SaaS tools comes from four things:
- it works on the local files themselves;
- it runs deterministic scripts and vision in batch;
- it keeps state in the project folder;
- it writes into the firm's own Excel and Word formats.

Each candidate below maps to a repo analogy. A candidate without one is a weaker fit for Claude Code.

| Repo concept | Construction equivalent | Covered today? |
|---|---|---|
| Codebase / files | Drawing set / sheets, spec sections | ✅ splitters |
| Imports, links | Detail/section callouts, spec cross-references | ❌ no resolver or linter |
| Commits / PRs | Addenda, bulletins, ASIs, reissues | ❌ |
| `git diff` / changelog | Overlay compare, revision log | ❌ (revision fields lost) |
| `main` branch | Conformed set | ❌ |
| Issues | RFIs, issue registry | ⚠️ the registry has no producers |
| PR review against requirements/tests | Submittal review against the spec section | ✅ submittal-review |
| CONTRIBUTING / CI rules | Div 01 procedures, contract notice terms | ❌ |
| Release checklist | Closeout: warranties, O&M, attic stock, training | ❌ |
| CODEOWNERS | Trade scope packages | ⚠️ inside bid-evaluator only |
| Project memory | CLAUDE.md, `.construction/skills/` state | ✅ |

---

## 4. Candidate skills, ranked

These criteria decide what can ship under the repo's rules: an eval must pass before `_dev/` → production, skills stay under 500 lines, and nothing may be fabricated.

**What the Sanibel test set can support** (checked 2026-10-02):
- **Drawings:** A, C, E and M sets. All 90 A-sheets have a vector text layer, with about 165 distinct sheet-reference tokens.
- **Specs:** complete. Division 01 includes 01 26 00 Contract Modification, 01 29 00 Payment, 01 31 00 PM & Coordination, 01 32 00 Progress Documentation, 01 33 00 Submittals, 01 40 00 Quality, 01 77 00 Closeout, 01 78 23 O&M, 01 78 39 Record Documents and 01 79 00 Training.
- **Not in the set:** prime contract or general conditions (Division 00 has only 00 04 00, 00 05 00 and 00 31 32), addenda, submittals or product data, a CPM schedule, pay apps, minutes. Of these, only synthetic fixtures exist: Addendum 01 (`evals/plugin/_fixtures/addendum/`) and the two generated submittal projects (`_fixtures/submittal-project/`, `_fixtures/foodservice-project/`).

| # | Candidate | PE/PM value | Testable on Sanibel | Reuses | Market | Fabrication/legal risk |
|---|---|---|---|---|---|---|
| 1 | **revision-compare** | High | Synthetic bulletin (planted edits give exact ground truth) | `rasterize_page.py`, `crop_region.py`, `annotate_pdf.py`, `sheet_index.yaml`, `spec_text/`, `issue_manager.py` | Overlay exists; diff + impact routing + log is whitespace | Low (diff is deterministic; vision only describes) |
| 2 | **document-set-audit** | Med-High | **Now** | `sheet_index.yaml`, `spec_index.yaml`, `issue_manager.py` | Whitespace | Low (deterministic) |
| 3 | **closeout-qc-register** | Med-High | **Now** | submittal-log batch/state/confidence pattern, `spec_text/` | Pype | Low (cite section and paragraph) |
| 4 | **project-requirements-digest** | Med-High (PM) | **Now** (full Div 01) | `spec_text/` | Thin | Medium (surface, never interpret) |
| 5 | **submittal-reviewer** (built as `submittal-review`) | **Highest time sink** | Synthetic (public product data with planted deviations) | `spec_text/`, schedule-extractor output, `annotate_pdf.py` | Crowded | Medium (GC pre-review, never the A/E's approval) |
| 6 | **change-event-manager** | High (PM) | Synthetic (needs a contract and #1's output) | #1 and #4 outputs, registry | Procore change events | High (code-researcher's "surface, never conclude" rule) |
| 7 | **scope-package-writer** | Medium (buyout) | Now | `reference/pe_expertise/scope-NN` | Thin | Low-Med |

**Tier 3 (one line each):**
- **OAC meeting minutes** with carry-forward open items. Crowded, and not document-driven.
- **Pay-app reviewer** (G702/G703 vs the schedule of values, retainage math, lien waivers). PM value, but data-centric and testable only with synthetic data.
- **Procurement log / lookahead.** Extends the submittal log with lead times and need dates; there is a Procurement-Log template in Sanibel. Needs a schedule input.
- **RFI log tracker** (aging, ball in court, folding responses back in). Best as a mode of rfi-drafter.
- **Daily report, punch list.** Field and mobile workflows, so a weak fit at a desk.
- **Area/linear takeoff** (`_dev/quantity-takeoff`, `scale-measurement`). An estimator workflow, with risk in vision-based measurement accuracy.
- **Prime-contract review.** Fold into #4 as an optional input when the user supplies a contract.

---

## 5. Sketches of the top candidates

### 1. revision-compare → specified as two skills
Superseded by the full spec in [`docs/specs/revision-history.md`](specs/revision-history.md) (design chosen 2026-10-02, implementation deferred). Revision history isn't stored anywhere a script can read, including Bluebeam, so:
- **`revision-history`** (new builder): Claude's record of every formal change (Addenda, Bulletins, ASIs, PRs, CCDs, COs). It's built cheaply from revision blocks, change-document covers, existing logs and `.bex` files, then refreshed as new files arrive. It raises discrepancies such as a document naming a sheet whose revision block wasn't updated, or a cited ASI that isn't on file.
- **`revision-compare`** (comparing only): compares a new package against the PE's current set. Reports text-based before/after values, unclouded changes, impact and contract status. Never slip-sheets, stamps or edits the PE's set; the PE's Bluebeam set stays the record of what's current.

### 2. document-set-audit ("lint for the drawing set")
This replaces `_dev/qa-qc-auditor`.
- **Checks:** deterministic, via a new `extract_sheet_text.py` that writes per-sheet text with coordinates to `.construction/skills/sheet_text/`. This is shared infrastructure with #1.
  - the cover sheet index against the sheets actually present;
  - each callout (`3/A510`), to confirm its target sheet exists and the detail number exists on that sheet;
  - spec sections cited on drawings, against `spec_index.yaml`;
  - "Section XX XX XX" references inside specs that point to sections missing from the manual.
- **Outputs:** `Document_Audit.xlsx`, plus every finding written to the issue registry. That makes it the registry's first real producer, feeding rfi-drafter. An optional hyperlinked set (PyMuPDF `insert_link`) answers the forum complaints about Batch Link.
- **Caveat:** Sanibel's cover sheet indexes 172 sheets and only 125 are present. That gap comes from disciplines missing from the test set, not from a design defect. References into absent disciplines must be classified as "discipline not in set", not "broken".

### 3 + 4. Spec registers (two sibling skills sharing scripts)
They are separate because the 500-line rule rules out one combined skill and the two extract different shapes of data.
- **closeout-qc-register:** line items from every section across all divisions, with tabs:
  - Warranties (duration, start trigger)
  - Extra Materials / attic stock
  - O&M
  - Training/Demo
  - Mockups
  - Field Tests & Inspections
  - Certifications
  - Record Docs

  It reuses submittal-log-generator's batch, state and confidence pattern.
- **project-requirements-digest:** Division 01 procedural obligations, as an Obligations / Deadlines / Responsibilities workbook plus a one-page summary:
  - submittal review periods and format
  - meeting cadence
  - schedule update frequency
  - pay-app timing and contents
  - change-procedure time limits
  - substitution windows
  - closeout sequence

  Every row cites section and paragraph. Later it can take a prime contract as an optional input.

### 5. submittal-reviewer (built on 2026-10-03 as `skills/submittal-review`; the sketch below predates it)
This restores spec-parser: per-section product requirements, manufacturers, standards and performance criteria, cached as JSON.
- **Steps:** read the submittal by rasterizing it and using vision on the cut sheets to detect the selected options. Build a compliance matrix (Complies / Deviation / Not demonstrated / N/A) that cites the spec paragraph and the submittal page. Cross-check against extracted schedules, e.g. hardware against the A500 door schedule.
- **Outputs:** a review-comments docx, markups via `annotate_pdf.py`, and a status update in the submittal log. Framed as a GC pre-review before the submittal goes to the architect.

---

## 6. Prerequisites (existing plumbing, not new skills)
1. **Issue registry producers.** New audit and review skills write to the registry from day one. Separately, wire up pe-review, tag-audit and code-researcher.
2. **Living-register convention.** Logs are updated in place, keyed by ID, without overwriting the user's edits. Generalize schedule-extractor's `_row_key` + `xlsx_to_changeset.py` round-trip into a shared `scripts/registers/` helper, used by #1, #3, #5 and #6.
3. **Per-sheet drawing text index** (`sheet_text/`), shared by #1 and #2.

## 7. Suggested order
1. **revision-compare** (now `revision-history` + a compare-only `revision-compare`, see `docs/specs/revision-history.md`). Highest value among the whitespace candidates, and the clearest codebase analogy. Planted-edit fixtures meet the SOP's "100% of seeded conflicts" bar.
2. **document-set-audit.** Testable today, becomes the registry's first producer, and shares `sheet_text/` with #1.
3. **closeout-qc-register** and **project-requirements-digest.** Cheap, and testable today.
4. **submittal-reviewer.** Highest raw value, but needs a fixture and faces crowded competition.
5. **change-event-manager.** Depends on #1 and #4.

## 8. Decisions to make
- [x] Which skill(s) to build first: revision-compare, specified in `docs/specs/revision-history.md` as two skills. document-set-audit is next.
- [ ] Whether to fix the prerequisites (registry producers, register helper) before or alongside the first new skill.
- [x] Whether `reference/pe_expertise/` should ship: no, it was removed from the repo on 2026-10-04.
- [x] Whether to write this roadmap into the repo and fix the SOP's stale "planned" list: both done.
- [ ] How to eval `_dev` skills. The harness loads only `skills/` from the repo that holds `run.py`. Options: copy the skill into `skills/` in a scratch git worktree and run the harness there, or add a harness option for extra skill directories.

## 9. Eval bar for every new skill (`docs/CM_SKILLS_SOP.md`)
- **Location and structure:** develop in `.claude/skills/_dev/<name>/` with `SKILL.md` under 500 lines, `agents/openai.yaml` and an exhaustive script allowlist.
- **Cross-platform rules:** double-quote all paths, run scripts via `bin/construction-python`, never write to `/tmp`.
- **Fixtures and cases:** fixtures in `evals/plugin/_fixtures/`, cases in `evals/plugin/<skill>/` with `harness.yaml` Python checks for xlsx and docx deliverables.
- **Pass bar:**
  - 3–5 PE-checkpoint assertions, at least 80% passing;
  - 100% of planted changes or broken references found;
  - 0 fabricated sheet or section citations;
  - token and time baselines recorded.
- **Promotion:** `claude plugin validate --strict .claude-plugin/plugin.json` must pass before a skill moves to `skills/`.

## Sources
- **Repo inventory:** `skills/*/SKILL.md`, `scripts/`, `reference/`, `docs/CM_SKILLS_SOP.md`, `evals/EVAL_SUITE_PLAN.md`, `evals/plugin/README.md`, git history (`ce8376a`, `5ab70df`).
- **The author's research:** the forum study and the earlier SOP draft and `_dev` skills cited in section 2 (not in this repo).
- **Web:**
  - Autodesk/FMI Construction Disconnected: https://www.autodesk.com/blogs/construction/construction-disconnected-fmi-report/
  - TrunkSubmittal: https://trunktools.com/trunksubmittal/
  - Document Crunch: https://www.documentcrunch.com/construction-contract-review
  - Pype AutoSpecs: https://pype.io/autospecs/
  - Bluebeam Max: https://press.bluebeam.com/2026/05/bluebeam-max-launches-globally-bringing-ai-powered-productivity-to-aec-teams-everywhere/
  - Procore AI agents: https://www.procore.com/ai/agents
  - A201-2017 notice provisions: https://www.amundsendavislaw.com/alert-notice-requirements-under-the-revised-a201-2017-aia-document-series-revisions-to-the-core-contract-documents-part-2
- **Caveat:** most of the time and cost figures are vendor claims, so treat them as directional.
