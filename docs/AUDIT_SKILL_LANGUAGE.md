# Audit: Skill Language

An audit of how the SKILL.md files on `feat/submittal-review` (PR #14, commit `b6015dc`) are written: whether their wording makes Claude do the right thing, reliably, at the lowest context cost. The rewrite tested in §3.4 is on this branch (`audit/skill-language`, commit `5e7f6f9`); nothing on `main` or `feat/submittal-review` was changed. Dated 2026-10-04.

**Measured** means a test was run and its output is cited. **Judged** means an opinion from reading. Every claim below is labelled one or the other.

## 1. Verdict

The procedure in `submittal-review` is sound and its own SKILL.md is the clearest file in the plugin, but every run loads `construction-guide` (6.6K tokens, about 64% of it inapplicable in a flat-file project), which contradicts it on document precedence, grading vocabulary, custom Python and what to do with a conflict. The defects most likely to make Claude do the wrong thing are mechanical and mostly silent: a 0-based `page_index` passed to a 1-based rasterizer renders the wrong sheet, skills tell Claude to invoke skills it cannot invoke, reference files carry path variables that are empty in Bash, and `code-researcher` resumes the previous scope and, through its own examples, teaches an IBC requirement that is not in the code, marked "confirmed". Descriptions are not the problem (2 defensible misses in 120 prompts on both Sonnet and Opus), and the A/B rewrite of `submittal-review` tied the original (1.00 on all eight runs, cost and turns within noise, rewrite means 2–3% higher), so by this audit's own rule it is not an improvement, although it did stop the inline Python, page-numbering errors and script reading the original showed.

## How this audit was done

### The standard, and where its sources disagree

1. **Anthropic.** [Agent Skills best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [Claude Code skills](https://code.claude.com/docs/en/skills), [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), [plugin evals](https://code.claude.com/docs/en/plugin-evals). The rules used: add only what Claude doesn't already know ("Default assumption: Claude is already very smart"); a description says what and when; references one level deep, loaded when needed; every step has an output; give the reason when it changes how Claude generalizes; current models over-apply "CRITICAL: You MUST…", so say "Use this tool when…".
2. **This repo.** `.claude/CLAUDE.md` and `docs/CM_SKILLS_SOP.md`.
3. **`docs/SUBMITTAL_REVIEW_DECISIONS.md`.** Text Claude already knows is cost, not value (the CSI layer was 94% restatement and caught no more defects).

Conflicts found, and which side this audit followed:

| Topic | One source | The other | Followed |
|---|---|---|---|
| Listing truncation | SOP:47 "Each skill's `description` is **truncated at 250 characters**" | Claude Code docs: "the combined `description` and `when_to_use` text is truncated at 1,536 characters" (re-fetched 2026-10-04) | The docs. No practical effect: the longest description here is 364 characters. |
| AgentCM detection | SOP:407 "Step 1: Check for .construction/ directory. → If present: AgentCM mode", SOP:497, SOP:600 | SOP:122 and `.claude/CLAUDE.md`: `.construction/project.yaml`, "never by the `.construction/` folder alone" | CLAUDE.md. The SOP contradicts itself. |
| Skills calling skills | SOP:591 "Skills that write files or modify project data use `disable-model-invocation: true`" | SOP:564 "Skills should be designed to invoke one another" | Neither can be followed as written: a user-only skill cannot be invoked by another skill (measured, §4 #7). This is the root cause of problem #7. |
| Spec text path | SOP:202, 271, 285 `.construction/spec_text/` | SOP:113, 136, 170 and every skill: `.construction/skills/spec_text/` | The skills. |
| Emphasis | Best-practices page, iterating with Claude: Claude A may suggest "stronger language such as 'MUST filter'" | Prompting page: "dial back any aggressive language" | Plain wording by default; strong wording only for a fragile step after an eval shows it being skipped. |
| Reasons | Prompting page: give the motivation, "Claude is smart enough to generalize from the explanation" | Claude Code skills page: "State what to do rather than narrating how or why" | A one-clause reason where it changes how a rule generalizes; no general explanation. |

### Tests run

| Test | How | Model |
|---|---|---|
| Cold read | 5 fresh subagents, each given only one SKILL.md plus the files it says to read (path variables substituted as Claude Code does) and a one-line task; asked for steps, files written, and every guess | Sonnet 5.5 |
| Contradiction sweep | A subagent read all 15 SKILL.md files, every reference, and the scripts' argparse definitions | Opus 5.5 |
| Description discrimination | 6 model-invocable skills × (10 should-trigger + 10 near-miss) = 120 prompts, shuffled, chosen from a listing that also held the real `pdf`, `xlsx`, `docx` and `code-review` skills | Sonnet 5.5 and Opus 5.5, separately |
| Mechanics probes | `claude -p --plugin-dir` probes of the Skill tool and the Bash environment; the page-numbering hand-off run against the eval fixture | Sonnet 5.5 |
| Trace mining | Every tool call in every eval run, classified (scripts read, inline Python, page errors, gate runs, skills loaded) | n/a |
| A/B eval | Original vs rewritten `submittal-review`, both eval cases, 2 runs each | Sonnet 5.5 agent, Sonnet 5.5 judge ×3 votes |

**The A/B command differs from the one requested, and why.** `claude plugin eval . --case "submittal-review*" --scaffold --allow-tools Bash Write Edit --judge-model sonnet` was run first on this Windows machine and every run was refused before starting: "A shell tool (Bash or PowerShell) was granted but this machine cannot confine it … the Windows sandbox is not active on this session (feature gate off)". WSL has no Linux `claude`, `bubblewrap` or `socat`, and installing them needs a sudo password. So both arms ran through the project's own cross-platform harness (`evals/harness/run.py` from `integrate/skills-foundation`, copied untracked into both worktrees and not committed here), which reads the same case folders and graders:

```
bin/construction-python evals/harness/run.py --case "submittal-review*" --runs 2 --model sonnet --judge-model sonnet --judge-votes 3 --budget-usd 6
```

Both arms used the same harness copy, model, judge, votes and budget. The no-plugin baseline was not re-run: the skill text cannot change it, and it was recorded on 2026-10-03 (`docs/evals/submittal-review-2026-10-03.json`).

## 2. Scorecard

Tokens are characters ÷ 4 (LF line endings). "At start" is the SKILL.md loaded on invocation. "Typical run" adds every reference and skill the SKILL.md tells Claude to read in a normal run, before any project document. Description quality comes from the discrimination test (§3.3) where the skill is model-invocable, otherwise from reading.

| Skill | Tokens at start | Tokens, typical run | Description | Instruction clarity | Mechanics problems | Grade (judged) |
|---|---:|---:|---|---|---|:-:|
| submittal-review | 3,979 | 16,384 (incl. construction-guide 6,644); +11.4K per worker | Good; user-only | Good own text; 25 cold-read guesses, 4 that matter | `status` never updated; `sheet-splitter` not invocable; issue severity unmapped; loads a guide that contradicts it; fan-out skipped in 4 of 4 runs with 19 elements (measured) | B |
| pe-review | 566 | 4,062 (+897 absence checklist, +6,644 if the guide loads) | Promises "RFI research, submittal analysis" the body never describes; 0 errors in test | Poor: no step reads the documents; rules apply "to every response" | Reference is a pasted CLAUDE.md that tells Claude to load the skill it is in | C |
| code-researcher | 4,818 | 9,797 | Good; 0 errors in test | Poor: three mandatory stops, no unattended path | Resumes the wrong scope; examples teach a wrong IBC citation marked `confirmed`; allowlist has no way to read a PDF | D |
| rfi-drafter | 2,755 | 7,326 (+923 issue types) | Good; 1 defensible miss | Fair: 18 guesses; example contradicts rules | Path variables in a reference file (empty in Bash); template mapping needs unscripted Python; no output folder | C |
| construction-guide | 6,644 | 6,644–7,768 (+ pe_review_rules for "PE-level" work) | Accurate; but co-loaded with another construction skill 0 of 120 times | Poor: 64% inapplicable in flat-file mode; contradicts itself and pe-review | Wrong `sheet_index.yaml` field names and page base; names user-only skills as invocable; `spec-parser` does not exist | D |
| bid-evaluator | 1,912 | ~5,500 (buyout-domain.md, drawing-review.md) | Fine for the menu (user-only) | Fair; "offload / release from context" instructions (:66, :93, :179-184) Claude cannot act on | :23 and :157 hand off to user-only skills; :54 "Read drawing sheets directly from PDF"; no output paths (:140-142) | B- |
| bid-tabulator | 2,511 | 2,511 | Overlaps bid-evaluator ("compare bids", "buyout analysis") | Fair; ">50 chars" (:54) vs "<100" (:109) text threshold | Every scope's bidders saved to one `bids/` folder, and the export globs `*.json`, so a second buyout pulls in the first (:113, :131); resume checks a `status` the state file never has (:191); "Try pdfplumber first" with no script | C |
| project-setup | 1,470 | 1,470 | Clear; names its side effect | Good; AgentCM branch skips spec classification (:44), the one thing AgentCM doesn't do | No else-branch for a missing CLAUDE.md; :136 "does not execute any external scripts" but Step 1 runs a database query | B |
| schedule-extractor | 3,825 | 3,825 | Good | Fair | Crop percentages read as pixels (#4); `--source_sheet`/`--output_file` rejected by `write_finding.py`; Step 6 POSTs to the AgentCM API with no AgentCM check (:177-186); `extract_tables()` with no script | C- |
| sheet-splitter | 1,739 | 1,739 | Good | Fair; index update after renaming unspecified (:95) | :58 sends every set to one `sheets/` folder, where set 2's `page_001.pdf` overwrites set 1's; the promised combined index (:141) is never written; points to nonexistent `/sheet-index-builder` (:21 and the script) | C |
| spec-splitter | 2,273 | 2,273 | Good; 0 errors in test | Good, except the repair step (:121-126) is an algorithm with no script | `spec-parser` (:16, :117) doesn't exist; no else-branch for a PDF that isn't a spec book when another skill calls it | B- |
| subcontract-writer | 6,694 | 6,694 | Good | Fair; 531 lines (over the 500-line guidance); "Do not leave this article as a placeholder under any circumstances" (:299, :305) pushes invention when the spec is silent | Wrong statute article (:178, verified); python-docx (:101) and .docx checks (:427) with no script; "output directory" undefined (:342) | C |
| submittal-log-generator | 6,375 | 7,734 (+schema, never referenced) | Good | Fair; 504 lines; 11 strong-emphasis markers; the same 01 33 00 text both flagged (:259) and excluded (:281); POOR/DEGRADED confidence rule worded three ways (:85, :239, :394) | Items accumulate "in memory" (:397) while resume reads a file (:416), so an interrupted run has nothing to resume; merge needs `jq` with no fallback (:344) | C+ |
| tag-audit-and-takeoff | 3,701 | ~9,300 (5 references) | Fine for the menu | Poor; 12 strong-emphasis markers and six confirmation gates around a flat-file path that contradicts itself (:46 vs :155) | `rasterize_page.py` used but not allowlisted (:40); `http://localhost:3001` hardcoded (:96, :279); markup coordinates in pixels passed as PDF points | C |
| viewport-highlighter | 4,363 | 4,363 | "find views" broad for a model-invocable skill; 0 errors in test | Fair; deprecated on `main` | Off-by-one page (#1); folder-based AgentCM test (#13); "Does NOT … delete viewports" (:21) vs "DELETE each existing viewport first" (:472); PATCHes a viewport id that Step 5 never creates (:352) | C |

## 3. Test results

### 3.1 Cold reads (measured)

Each reader got only the SKILL.md, the files it says to read, and a one-line task. Every guess is a finding; the count includes minor ones.

| Skill (task) | Guesses | Share of loaded text used | Guesses that would change the outcome |
|---|---:|---|---|
| submittal-review (the eval prompt, unattended) | 25 | construction-guide ~15%, pe_review_rules ~25% | `status` only ever written as `intake` and `complete` (SKILL:96, :216) although restart relies on it (SKILL:57); `issue_manager.py add` has no severity or description (SKILL:213) — "the biggest unknown"; page base for `rasterize_page.py` (it passed 0 for the cover); what counts as an element (SKILL:103), which decides solo review vs fan-out |
| pe-review ("Check the casework and plumbing coordination for Science Lab 104 — what's missing?") | 15 | red-flags 10–15%, coordination matrix ~10%, scope gaps ~15%, absence checklists ~5% (nothing for Div 12 or 22) | No step says to read the project documents or how; it found the rasterize rule only through construction-guide's listing description. Seven instructions add work nobody asked for (unrelated red flags, an RFI-ready block per finding, three files written, a verification paragraph) |
| code-researcher (invoked by submittal-review for `accessibility-work-surfaces`; a previous run left files) | 12 | schemas.yaml: key names only, ~20% | Followed literally, SKILL:439 "`gap_analysis.yaml` exists … go to Phase 5" reports yesterday's egress analysis; does not say which file submittal-review should cite as `source`; three stops with no unattended path; no permitted way to read a PDF |
| rfi-drafter (draft an RFI for a submittal-review issue, no template) | 18 | All four references read; issue-schema.md partly used; the example RFI "misleading" | No location or schema for `rfi_draft.json` or the .docx; "first RFI" can't be detected, so it re-asks for the template every time; rasterize commands only under the AgentCM heading; template mapping needs python-docx and a SHA-256 hash with no permitted script |
| construction-guide ("What does detail 5 on A-521 show … does the spec agree?", flat file) | 18 | 36% (150 of 418 lines) | `sheet_index.yaml` fields named `pageIndex`/`filePath` (real: `page_index`, `filename`, `source_pdf`); it passed `page_index` 1 to the 1-based rasterizer, which renders A-501, not A-521 (measured); the title-block crop size (construction-guide:280) fits a 30×42 sheet, not this 17×11 set |

One reader claim was discarded: the code-researcher reader reported that `reference/` holds no ADA or IBC data. That was an artifact of the test folder, which held only two of the shared reference files.

### 3.2 Contradictions (measured by sweep, confirmed by reading)

An independent subagent read all 15 SKILL.md files, every reference and the scripts' argparse definitions. It reported **18 direct conflicts, 23 rules covering the same situation in different words, 10 duplicated blocks (about 15,000 characters), 7 dangling references and 19 hand-off mismatches**. The rows below were re-checked against the files for this report; the rest are in the sweep's own notes and are listed in §6 where they need action.

**Direct conflicts (two rules that cannot both be followed)**

| Rule | Conflicts with | Effect |
|---|---|---|
| construction-guide:326-332 "1. Agreement … 6. Specifications 7. Drawings" | pe_review_rules.md:8-14 "1. Change Orders / CCDs 2. RFI Responses classified as Directives … 4. Approved Submittals …"; submittal-review:231 points to the second, while submittal-review:38 loads the first | Which document controls depends on which file Claude read last |
| construction-guide:390 "When conflicts/gaps are found, draft with the `rfi-drafter` skill"; pe_review_rules.md:66 "format as RFI-ready" | construction-guide:258 "No skill writes an RFI directly — only issue records"; rfi-drafter:16 "No RFI is ever created without explicit user instruction" | Three different actions for the same conflict |
| construction-guide:388 grades "CONFIRMED … PROBABLE … CONFLICTING … NOT FOUND" | pe_review_rules.md:53-56 "CONFIRMED … CONFLICTING … NOT FOUND … OPEN"; check_review.py:32 accepts only `CONFLICTING`, `NOT FOUND`, `OPEN` | A PROBABLE grade fails the submittal-review gate |
| submittal-review:82, construction-guide:103 and :175, bid-evaluator:23 tell Claude to run `sheet-splitter`, `schedule-extractor`, `bid-tabulator` | Those skills' frontmatter: `disable-model-invocation: true` | The Skill tool refuses (measured, §4 #7) |
| rfi-drafter:39 "Do NOT create custom scripts"; submittal-review:36; `.claude/CLAUDE.md` | construction-guide:284-289 pdfplumber snippet; rfi-drafter:55 "Read with python-docx"; research-checklist.md:53; code-researcher:208; schedule-extractor:100; subcontract-writer:101 | Inline Python (measured, §4 #8) |
| construction-guide:30 "A `.construction/` folder alone is not enough" | viewport-highlighter:32 "If `.construction/` is absent, **stop immediately**"; bid-tabulator:30; construction-guide:19 | Every project has `.construction/skills/`, so the folder test detects AgentCM where there is none |
| viewport-highlighter:21 "Does NOT: modify existing viewports, delete viewports" | viewport-highlighter:352 "PATCH the viewport to correct"; :472 "If replacing: DELETE each existing viewport first" | Claude either refuses its own steps or deletes viewports it promised not to touch |
| submittal-log-generator:259 lists "'submit in accordance with 01 33 00'" as a reason to FLAG | submittal-log-generator:281 "EXCLUDE entirely (do not even flag): 'Submit in accordance with Section 01 33 00'" | The same item is kept in one run and dropped in the next |

**Same situation, different wording** (examples): three "mandatory verification" lists (construction-guide:357-363 addenda, revisions, ASIs; pe_review_rules.md:21-26 addenda, RFIs, submittals; rfi-drafter:93-99 six checks); five severity scales (pe_review_rules Critical/High/Medium/Low; review-data critical…low; code-researcher HIGH/MEDIUM/LOW; bid-evaluator CRITICAL/SIGNIFICANT/MINOR/INFO; issue registry info/warning/conflict/safety) with no mapping between any two; two NIC definitions (construction-guide:374 "covered under a separate contract or by the Owner" vs bid-evaluator buyout-domain.md:9 "Explicitly excluded from this sub's scope"); "never state a code requirement you have not retrieved" (submittal-review, review-lens) against rfi-format.md:87 "Per [code section], [requirement]" and subcontract-writer:178 and :321 stating Maryland statute sections as fact. One of those is wrong: :178 says "Maryland = L&E Article §17-201", but Maryland's prevailing-wage law is State Finance and Procurement Article §17-201 ff. (verified).

**Dangling references:** `spec-parser` (construction-guide:258, rfi-drafter:164, issue-schema.md:112, spec-splitter:16, :117) does not exist; `split_drawing_set.py:152` writes "Sheet numbers and titles need identification via /sheet-index-builder" into every `sheet_index.yaml` and prints "Next: Run /sheet-index-builder" (:197), a skill that does not exist; construction-guide:401-404 names `references/red-flags.md` and three more, which resolve to construction-guide's own folder, where they are not; schedule-extractor:236-237 passes `--source_sheet` and `--output_file`, which `write_finding.py` rejects (`--source-sheet`, `--output-file`).

**Hand-off mismatches:** `sheet_index.yaml` exists in three shapes (`split_drawing_set.py`: 0-based `page_index`, `filename`; `templates/sheet_index.yaml:17`: `page: 1  # Page number within PDF (1-based)`; construction-guide:137: `pageIndex`, `filePath`); pe-review writes RFI candidates to `.construction/skills/pe-review/rfi_candidates.md` (pe_review_rules.md:77) while rfi-drafter reads only `.construction/skills/issues/` (rfi-drafter:188); only submittal-review and rfi-drafter have `issue_manager.py` on their allowlists, although construction-guide:258 and issue-schema.md:111-116 name four other skills as issue writers; code-researcher writes its own `project_context.yaml` with different keys from the shared one submittal-review confirms at its checkpoint; code-researcher never reads the repaired spec text spec-splitter says it produces for it (spec-splitter:19). Checked and consistent: review ids and `prior_review`, the compliance `source` path (review-data.md:169 = code-researcher:284), `find_pages.py` flags, and `check_review.py`'s enums against review-data.md.

### 3.3 Description discrimination (measured)

120 prompts: for each of the six skills Claude can invoke, 10 that should trigger it and 10 near-misses written to tempt it (for example "Run the unit tests and fix the failing code check in CI" against `code-researcher`'s trigger "code check", and "Clean up our GitHub issue queue" against `rfi-drafter`'s "issue queue"). A miss is a should-trigger prompt where the skill was not chosen; a false trigger is a near-miss where it was.

| Skill | Sonnet: miss / false | Opus: miss / false | Error rate |
|---|---|---|---:|
| code-researcher | 0 / 0 | 0 / 0 | 0% |
| construction-guide | 1 / 0 | 1 / 0 | 5% |
| pe-review | 0 / 0 | 0 / 0 | 0% |
| rfi-drafter | 1 / 0 | 1 / 0 | 5% |
| spec-splitter | 0 / 0 | 0 / 0 | 0% |
| viewport-highlighter | 0 / 0 | 0 / 0 | 0% |
| **All** | **2 / 0** | **2 / 0** | **1.7%** |

Both misses are defensible: "Compare hardware set 4 in the spec with what the door schedule shows for door 112" went to `pe-review`, and "Export RFI 26 to Word using our firm's template" went to `docx`. **The descriptions discriminate well; rewriting them is not worth the risk.**

The finding that matters is different: `construction-guide`, whose description says "load before reading drawings, specs…", was chosen alongside another construction skill **0 times in 120** on both models. Whenever `pe-review`, `rfi-drafter` or `code-researcher` handles a request, the guide's reading rules are absent unless that skill's own text says to load it, and only `submittal-review` and `project-setup` do.

Limits: a single-turn choice from names and descriptions approximates, but is not, triggering inside a live session; the six user-only skills are invisible to Claude and were not tested.

### 3.4 A/B eval: original vs rewritten `submittal-review` (measured)

What changed between the arms is in the rewrite's commit (`5e7f6f9`): the body of `SKILL.md`, `worker-prompt.md` and `review-data.md`; frontmatter, lens, writing guide and milestones unchanged. In short: full commands in every step; page numbering stated; `status` set after every step; the issue-severity mapping; the unattended and sheet-splitter paths; "don't write scripts, including inline `python -c`"; and construction-guide loaded only in AgentCM mode, with workers inlining the three reading rules they need. Instruction text loaded in a typical run fell from ~16,400 to ~10,300 tokens (−37%; computed from file sizes, not measured in the traces), and by ~6,600 tokens per worker.

Every run of both arms passed every grader. Raw results, with per-run grader verdicts and the behavior counts below: `docs/evals/submittal-review-language-ab-2026-10-04.json`.

| Case | Arm | Run | Score | Turns | Cost | Time (s) |
|---|---|---:|---:|---:|---:|---:|
| Lab casework (6 pages) | Original | 1 | 1.00 | 42 | $3.20 | 645 |
| | Original | 2 | 1.00 | 34 | $3.78 | 486 |
| | Rewrite | 1 | 1.00 | 38 | $3.86 | 644 |
| | Rewrite | 2 | 1.00 | 34 | $3.44 | 562 |
| Foodservice (366 pages) | Original | 1 | 1.00 | 61 | $3.64 | 715 |
| | Original | 2 | 1.00 | 59 | $4.98 | 726 |
| | Rewrite | 1 | 1.00 | 62 | $4.98 | 766 |
| | Rewrite | 2 | 1.00 | 67 | $3.73 | 707 |
| **Means** | Original | lab / food | 1.00 / 1.00 | 38 / 60 | $3.49 / $4.31 | 566 / 720 |
| | Rewrite | lab / food | 1.00 / 1.00 | 36 / 64.5 | $3.65 / $4.36 | 603 / 736 |
| **All 4 runs** | Original | | 1.00 | 49.0 | $15.60 total | 643 |
| | Rewrite | | 1.00 | 50.3 | $16.01 total | 670 |

**Result: a tie, and by the brief's rule not an improvement.** Scores are identical; the rewrite's mean cost is 2.6% higher, turns 2.5% higher and time 4% higher. Within one arm and case, cost varied by up to 37% between two runs ($3.64 vs $4.98), so none of these differences is distinguishable from noise with two runs per arm. Wall time is the weakest of the three: from the second original run on, the two arms ran concurrently on one account.

**Why cutting 37% of the instruction text did not cut cost.** Instruction text is a small and cached share of these runs; page images, the 366-page index and long JSON writes dominate. On this skill, wording changes pay off in behavior, not in dollars.

**What the rewrite did change (trace mining, measured).** These are the behaviors the rewrite targeted; the eval scores none of them.

| Behavior per run | Original lab | Rewrite lab | Original food | Rewrite food |
|---|---|---|---|---|
| construction-guide loaded | 1, 1 | 0, 0 | 1, 1 | 0, 0 |
| Inline Python (`"$PY" -c …`) | 3, 2 (pdfplumber reads, a findings summary) | 0, 0 | 7, 8 (pdfplumber; hand-parsing `pages_0.json` and `page_map_0.json`) | 2 one-liners (a JSON field print, a `print(1)` check), 0 |
| Script source read to learn arguments | 4 files, 0 | 0, 0 | 0, 0 | 0, 0 |
| `--help` lookups | 1, 1 | 0, 0 | 4, 3 | 3, 0 |
| Page-numbering errors (page 0 passed to the rasterizer) | 1, 0 | 0, 0 | 1, 0 | 0, 0 |
| `state.yaml` writes (status updates) | 2, 2 | 3, 3 | 3, 2 | 3, 5 |
| Gate runs (failed) | 2 (0), 2 (0) | 2 (1), 1 (0) | 1 (0), 2 (1) | 1 (0), 2 (1) |
| Issues logged | 1, 2 | 2, 2 | 2, 1 | 2, 1 |

**The fan-out instruction was ignored in all four foodservice runs, under both wordings.** Every foodservice trace had 19 elements, above the threshold (original: "More: fan out. Batch about five to eight elements per worker and launch the workers in parallel"; rewrite: "Nine or more: launch workers in parallel"), yet no run called the Agent tool; each reviewed all 19 itself (record batches of 7/6/6, 19, none, 8/8/3). The scores were still 1.00, so on this fixture fan-out was not needed, but it means `worker-prompt.md` and the per-worker saving (~6,600 tokens) are untested. Either state fan-out as a choice ("for more than about eight elements with drawings to read, consider workers") or find out why Sonnet declines it. The rewrite's status instruction was also followed only partly (3–5 writes against nine steps).

**Harness notes.** The rewrite arm's harness process crashed after its last run was graded, printing a "→" in a grader verdict to the Windows console (`UnicodeEncodeError: 'charmap' codec can't encode character '→'`), so it wrote no `summary.md`; every run's `run.json` and `graders.json` was already on disk and is what the tables use. `run.json` is written once before judging, with an empty grader list and score 0, then rewritten after judging, so anything reading results mid-run sees false zeros.

### 3.5 Frontmatter and emphasis (judged)

**Frontmatter.** Every `name` matches its folder (`claude plugin validate --strict` passes). Every description is in the third person, under 365 characters, says what the skill does and lists the phrases that trigger it; none says when not to use it, and §3.3 found no confusion that would need one. Specific problems:
- submittal-review:8 `argument-hint: "<submittal.pdf> [--section \"12 35 53\"] [--resubmittal-of <review_id>]"` advertises two flags the body never mentions; Step 1.3 says only "the user names a prior review". Add to Step 1: "`--section` overrides the section read from the cover; `--resubmittal-of` names the prior review id."
- `disable-model-invocation: true` is right for submittal-review (long, costly, writes deliverables) but wrong in effect for sheet-splitter and schedule-extractor, which other skills tell Claude to run (#7). spec-splitter writes files yet is model-invocable, deliberately, so submittal-log-generator can call it; the SOP's rule (SOP:591) doesn't allow for that.
- construction-guide is background knowledge for Claude, not a command a user types; `user-invocable: false` would take it out of the `/` menu.
- pe-review:3-7 promises "RFI research, submittal analysis"; the body has no procedure for either and hands submittal packages to submittal-review.

**References loaded by default but needed only sometimes.** construction-guide in flat-file projects (#14). In `submittal-review`, `worker-prompt.md` (~1,000 tokens) is read on every run because solo reviews follow its per-element steps (seven of the eight eval runs read it; none launched a worker), and `milestones.yaml` (~840 tokens) is read whole, in all eight runs, for the two or three gates a scope uses. Moving the per-element steps into SKILL.md Step 5 and having workers receive them would let solo runs skip the worker prompt; worth it only if the harder fixture shows a difference.

**Emphasis.** `submittal-review` has none and needs none. Elsewhere in the review workflow:

| file:line | Text | Keep? | Calm version |
|---|---|---|---|
| construction-guide:23 | "**NEVER read PDF files directly.** Construction PDFs are 30"×42" sheets — too large for direct reading." | Keep the rule; fix the reason, which is wrong for letter-size specs and submittals | "Read PDFs through the scripts, not the Read tool: a whole drawing sheet is illegible that way and a long PDF exceeds one read. Rasterize the page, crop for detail; use `extract_text_region.py` for text." |
| construction-guide:24 | "**NEVER read `ocr_output.json` in full.**" | Keep | "Read `ocr_output.json` only for one element's text, by id; it is 100–400 KB per sheet." |
| construction-guide:357 | "**MANDATORY CHECK:** Before returning ANY specification section or drawing detail as a response, verify the addenda log and revision history" | Keep, once (pe_review_rules.md:19-26 repeats it) | "Before you cite a spec section or drawing detail, check the addenda, ASIs and the sheet's revisions for anything that supersedes it. If there is no log, say so once." |
| construction-guide:240 | "### Critical Skills (invocable — produce deliverables)" | Drop (#7) | "Skills the user runs" |
| pe_review_rules.md:19, :21 | "## Mandatory Verification (every response)", "BEFORE returning any spec section or drawing detail:" | Merge into the construction-guide line above | — |
| red-flags.md:3 | "Scan for these on EVERY document interaction. Flag when detected even if unrelated to the query." | Reword | "While you read for the question, note any of these you see. Report them after your answer, one line each." |
| rfi-drafter:18 | "**Design**: RIGID output format and quality checks. GUIDED research sequence before drafting. FLEXIBLE across any trade" | Drop | — |
| rfi-drafter:39 | "Do NOT create custom scripts during execution." | Keep | "Don't write scripts, including inline `python -c`; every output goes through the scripts above." |
| rfi-drafter:52 | "the output MUST match their format exactly." | Keep the intent | "When they have a template, the export fills it, so the RFI goes out in their format." |
| rfi-drafter:179 | "**Critical rule: no skill writes an RFI directly.**" | Keep, move to construction-guide (#15) | "Skills log issues; the user decides which become RFIs." |
| rfi-drafter:234 | "Do NOT interrupt the current workflow to draft an RFI. Log and continue." | Keep | "Log it and carry on with the current task; drafting waits for the user." |
| research-checklist.md:105 | "Do NOT assert a code violation" | Keep, with the reason | "Frame code questions as 'appears to conflict with [section code-researcher retrieved]; please confirm': the design professional decides compliance." |
| code-researcher:39 | "## Framing Rule (Non-Negotiable)" | Drop the label; the rule already gives its reason | "## Framing" |
| code-researcher:88 | "**Human checkpoints at 1c, 3c, and 4c.** Do not skip them." | Reword (#12) | See #12. |
| code-researcher:224, :243 | "**Critical extraction discipline:**", "This is non-negotiable — code requirements vary significantly between editions." | Reword | "While extracting:"; "Requirements vary between editions, so confirm the adopted edition first." |

## 4. Top 15 problems

Ranked by how likely each is to make Claude do the wrong thing. Silent errors (wrong output, no error message) rank above errors a script catches.

### 1. A 0-based page index is passed to a 1-based rasterizer (silent wrong sheet). Measured.

- construction-guide/SKILL.md:137: "find the sheet in `sheet_index.yaml` → get `title`, `discipline`, `scale`, `pageIndex`, `filePath`"
- construction-guide/SKILL.md:148: `rasterize_page.py" "{filePath}" {pageIndex} --dpi 200 --output sheet.png`
- viewport-highlighter/SKILL.md:65: `"{pdf_path}" {page_index} --dpi 200 --output "{sheet_number}.png"`

`split_drawing_set.py` writes `filename`, `source_pdf` and `page_index` counting from 0; `rasterize_page.py` counts from 1. On the eval fixture, A-521 has `page_index: 1`, and page 1 of `Arch Set.pdf` is A-501: Claude reads the wrong sheet with no error. `page_index: 0` fails with "ERROR: Page 0 out of range (1-3)". In the original eval's first run Claude rasterized pages 0–2, hit that error and redid the call; the construction-guide cold reader passed `1` for A-521. (AgentCM's own index schema was not available to this audit; check whether its `pageIndex` is also 0-based.)

Replace construction-guide:137 with:
> 1. **Sheet lookup**: find the sheet in `sheet_index.yaml`. `filename` is its one-page PDF, in the same folder; `source_pdf` is the bound set and `page_index` its position there, counting from 0.

and :148 (and viewport-highlighter:65) with:
> `"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/rasterize_page.py" "{sheets folder}/{filename}" 1 --dpi 200 --output "{working folder}/{sheet_number}.png"`
> `rasterize_page.py` counts pages from 1: a split sheet is page 1; in the bound set, pass `page_index + 1`.

### 2. Examples teach code citations that are wrong, one of them marked "confirmed". Verified.

- code-researcher/SKILL.md:366: "IBC §1210.3 requires 0.60 COF in commercial kitchens" (also :301-302, and gap_report_template.md:24)
- code-researcher/references/schemas.yaml:200-205: `code: "IBC 2021"`, `section: "1210.3"`, `requirement: "Floor surfaces in commercial kitchens shall have a static coefficient of friction of not less than 0.60"`, `edition_confirmed: true` (and :252, :249 `confidence: confirmed`)
- rfi-drafter/references/rfi-format.md:123-128: "Per IBC Table 1005.1, the corridor requires a minimum 44" … reducing the clear width to approximately 3'-2" … This falls below both the IBC egress minimum and the ADA accessible route minimum of 3'-0" clear"

IBC 2021 Section 1210 is "Toilet and Bathroom Requirements" and §1210.3 is "Privacy" (water closet compartments, urinal partitions); no IBC section sets a 0.60 coefficient for kitchen floors. IBC 2021's minimum corridor width is Table 1020.3; §1005.1 is a section, not a table. The RFI example's arithmetic is also wrong (3'-2" is above 3'-0"), and it asserts a violation, which research-checklist.md:105 forbids ("Do NOT assert a code violation"). Anthropic's prompting guide calls examples "one of the most reliable ways to steer Claude's output". The code-researcher cold reader listed these citations among values it would be tempted to reuse, and called the Maryland example (COMAR 10.15.03) "the most tempting to reuse" because the test project is in Maryland; the rfi-drafter reader flagged the RFI example's citation as doubtful and said it would not copy it. This matters most in `submittal-review`, where a code-researcher topic file is the only thing that lets a code question count as researched.

Replace example values with placeholders, e.g. schemas.yaml `topic_findings`:
> ```yaml
>     - code: "<code and adopted edition, e.g. the state building code based on IBC 2021>"
>       section: "<section number, copied from the retrieved text>"
>       requirement: "<requirement, quoted from the retrieved text>"
>       edition_confirmed: false   # true only after Phase 3a confirmed the adopted edition
>       source_url: "<page the text was read from>"
> ```
and add one line at the top of each example block: "Example values are illustrative and are not code citations; never copy them into findings." Replace the RFI example with a drawing-to-drawing conflict that needs no code citation (door 105A: plan 3'-0", door schedule 3'-6"), or phrase the code part as rfi-format.md:87 should: "appears to conflict with the minimum corridor width in the adopted code ([section from code-researcher]); please confirm."

### 3. code-researcher resumes or overwrites the previous scope (silent). Judged; confirmed by cold read.

- code-researcher/SKILL.md:430: "Check for `.construction/skills/code-researcher/` before starting:"
- code-researcher/SKILL.md:439: "| `gap_analysis.yaml` exists | Gaps identified | Present to user, go to Phase 5 |"

Every file (project_context.yaml, scope_definition.yaml, pass1_*.yaml, jurisdiction.yaml, topics/, gap_analysis.yaml) has a fixed name in one folder. `submittal-review` calls code-researcher once per open question. Followed literally, the second call finds the first call's `gap_analysis.yaml` and presents it; the cold reader, given leftover egress files, said it would "report on egress". The resumption table also reads `scope_definition.yaml` as "scope confirmed", but :143 writes that file before the :159 checkpoint confirms anything.

Replace :430 with:
> Each research run has its own folder, `.construction/skills/code-researcher/{scope-slug}/` (kebab-case from the scope, e.g. `accessibility-work-surfaces`); every file below goes there. Before starting, look for that folder and resume from the table below. Leave other scopes' folders alone.

and give `scope_definition.yaml` a `confirmed: true` field set at checkpoint 1c, checked by the resumption table. `check_review.py` already accepts any existing path as `source`, so `submittal-review` needs only its example path updated (review-data.md:169).

### 4. schedule-extractor crops with percentages read as pixels (silent wrong crop). Judged from code.

- schedule-extractor/SKILL.md:70: "Report the approximate bounding box coordinates … as percentages of the image dimensions"
- schedule-extractor/SKILL.md:80-81: `crop_region.py" full_sheet.png \ --box {x1},{y1},{x2},{y2} \`

`crop_region.py --box` is in pixels unless `--normalized` is passed, and then it expects 0–1 (crop_region.py:65-66). Percentages such as `45,10,95,40` crop a 50×30-pixel corner of the sheet. Replace :70 with "… as fractions of the image width and height (0–1)" and add `--normalized` to the command at :81.

### 5. Two precedence orders and three different actions for a conflict. Judged; flagged by all three review-workflow cold reads.

- construction-guide/SKILL.md:326-332 (Agreement, Modifications, Addenda, Supplementary Conditions, General Conditions, Specifications, Drawings), then :335: "Specifications and Drawings are complementary, not ranked against each other in all cases."
- pe-review/references/pe_review_rules.md:8-14: "1. Change Orders / CCDs … 2. RFI Responses classified as Directives … 4. Approved Submittals (product-specific data ONLY …)"
- submittal-review/SKILL.md:231: "Precedence and the RFI and submittal authority rules are in `pe-review`'s `references/pe_review_rules.md`."
- construction-guide:323 "Do not present conflicting information as equally valid without stating which source controls" vs submittal-review:232 "Surface conflicts; never resolve them."

A submittal review loads construction-guide (SKILL:38), is pointed at pe_review_rules (SKILL:231), and gets two orders that disagree about where RFI responses and approved submittals sit, plus three instructions on what to do when documents disagree (name the controlling source; flag both and recommend an RFI; never resolve). Keep one block, in construction-guide, and have pe_review_rules.md point to it:
> **Precedence.** When documents conflict, cite both. If the contract names an order (check the General Conditions), say which source it makes control; otherwise the conflict is a question for the design team. A responded RFI, ASI or bulletin changes the documents it answers. An approved submittal governs only the product data it shows; an approved-as-noted markup changes it. Large-scale details govern small-scale plans, figured dimensions govern scaled ones, and specific notes govern general notes.

In `submittal-review`, replace SKILL:231 with nothing (the rewrite drops it) and keep SKILL:232 with its reason: "the A/E decides which governs".

### 6. `submittal-review` never updates `status`, so a restart resumes at the wrong step (silent). Measured.

- submittal-review/SKILL.md:57: "`state.yaml` carries `status`. On restart, read it and resume at the step after the last completed one."
- submittal-review/SKILL.md:96: "Write `state.yaml` (status: `intake`)." No later step sets it until :216 "Set `status: complete`".

In both original lab-casework runs, `state.yaml` was written once (run 1 at intake; run 2 not until Step 5, already as `status: review`) and edited once at the end. Followed as written, a session that dies in Step 7 restarts at Step 2 and rebuilds the trace. (The rewrite's runs set it three times each: better, still not after every step.) Replace :57 with:
> `status` in `state.yaml` names the last completed step. Set it at the end of every step; on a restart, read it and resume at the next step.

and end each step with "Set `status: <step>`" (done in the rewrite).

### 7. Skills tell Claude to invoke skills it cannot invoke, or that don't exist. Measured.

- submittal-review/SKILL.md:82: "If they are not, run `/construction:sheet-splitter`."
- construction-guide/SKILL.md:103: "Run `/sheet-splitter` first to split bound drawing sets into individual sheet PDFs." and :175 "Use `schedule-extractor` skill for structured extraction." and :240 "### Critical Skills (invocable — produce deliverables)" over a table of mostly user-only skills
- bid-evaluator/SKILL.md:23: "run `/bid-tabulator` first"
- split_drawing_set.py:197: "Next: Run /sheet-index-builder to identify sheet numbers via vision" (no such skill); construction-guide:258 `spec-parser` (no such skill)

A probe (`claude -p --plugin-dir`, Sonnet) asked the Skill tool for `construction:sheet-splitter` and got: "Skill construction:sheet-splitter cannot be used with Skill tool due to disable-model-invocation. Ask the user to run /construction:sheet-splitter themselves … Do not replicate this skill's workflow by other means." An unattended review of a project with an unsplit drawing set therefore stops at intake. The cause is in the SOP, which asks for both `disable-model-invocation: true` on file-writing skills (SOP:591) and skills that invoke one another (SOP:564). Replace submittal-review:82 with:
> If they are not, ask the user to run `/construction:sheet-splitter` (only the user can start it). Unattended, read the bound drawing set instead and add a line to `notes`.

construction-guide:175: "**Reading a schedule on a sheet:** rasterize and crop it. For an Excel export, suggest the user run `/construction:schedule-extractor`." Rename :240 to "Skills the user runs" and drop `spec-parser`. Change `split_drawing_set.py:197` to print "Next: identify sheet numbers from each title block (sheet-splitter Step 3)".

### 8. Rules forbid custom Python while instructions require it. Measured.

- `.claude/CLAUDE.md`: "Skills must NOT create custom Python scripts during execution"; submittal-review/SKILL.md:36 "Do not write custom scripts"
- construction-guide/SKILL.md:283-289: "**Extract text with pdfplumber:** ```python import pdfplumber …```" and :102 "plus `pdfplumber` / `pymupdf` for text and annotation extraction"
- code-researcher/SKILL.md:208: "Use pdfplumber for text-layer PDFs; use vision for scanned or image-heavy pages", with an allowlist (:454-457) of `construction-python` and `write_finding.py` only
- rfi-drafter/SKILL.md:55 "Read with python-docx to identify field locations", :60 "Store a SHA-256 hash of the template"; research-checklist.md:53 "Use pdfplumber to extract text"

In both original lab-casework runs, with construction-guide loaded, Claude ran `"$PY" -c "import pdfplumber …"` to read the submittal and spec (run 1 once, run 2 twice), and run 1 used more inline Python to summarize its findings, despite submittal-review:36. Replace construction-guide:283-289 with:
> **Extract text:** `"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/extract_text_region.py" "{pdf}" {page}`. Spec text is already extracted in `.construction/skills/spec_text/`.

Add `rasterize_page.py`, `crop_region.py`, `extract_text_region.py` and `find_pages.py` to code-researcher's allowlist, with code-researcher:208 reading "Read spec text from `.construction/skills/spec_text/`; rasterize drawing pages and read the PNG." For rfi-drafter's template mapping, add an `--inspect-template` mode to `rfi_export.py` (the script already opens the .docx), or state that this one step may read the template with python-docx. Word the rule so it covers the case Claude actually hits: "Don't write scripts, including inline `python -c`."

### 9. Five severity scales and three grade lists, unmapped at the one hand-off that needs a mapping. Measured.

- submittal-review/SKILL.md:213: "goes to the issue registry with `issue_manager.py add --source-skill submittal-review`, so `rfi-drafter` can turn it into an RFI."
- issue_manager.py:263-265: `--source-skill` required; `--severity` required, `choices=["info", "warning", "conflict", "safety"]`; `--description` required
- review-writing.md severities `critical/high/medium/low`; construction-guide:388 grades CONFIRMED/PROBABLE/CONFLICTING/NOT FOUND; pe_review_rules.md:53-56 CONFIRMED/CONFLICTING/NOT FOUND/OPEN plus Type and Priority fields (:60-64); check_review.py:32 CONFLICTING/NOT FOUND/OPEN

In both original lab-casework runs Claude ran `issue_manager.py add --help` to find the arguments (run 1 also read `annotate_pdf.py`, `check_review.py` and `export_submittal_review.py` in full; run 2 ran `check_review.py --help`), then invented a severity mapping (run 1: `warning`; run 2: `warning` and `conflict`). Each run makes up its own. Replace submittal-review:213 with the full command and the mapping:
> Log each finding with `rfi_candidate: true` so `rfi-drafter` can turn it into an RFI; don't draft the RFI here. Severity: `conflict` for a CONFLICTING grade, `warning` for NOT FOUND or OPEN, `safety` for a life-safety finding.
> `"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/issue_manager.py" add --source-skill submittal-review --severity {severity} --confidence high --description "{finding}" --sheets "{sheets}" --spec-sections "{sections}" --elements "{element}" --context "submittal-review {review_id} {finding id}" --rfi-subject "{subject}"`

Then pick one grade list for the plugin (CONFIRMED for a check that passed; CONFLICTING, NOT FOUND, OPEN for findings), delete PROBABLE from construction-guide:388, and put the issue-severity mapping in construction-guide's Issue Registry paragraph so every skill uses the same one.

### 10. Path variables in a reference file are empty when the command runs. Measured.

- rfi-drafter/references/research-checklist.md:17-18: "# ${CLAUDE_PLUGIN_ROOT} is not set in the shell here: use the plugin path that / # rfi-drafter's SKILL.md commands show."
- research-checklist.md:22-23 and :88 then use `"${CLAUDE_PLUGIN_ROOT}/bin/construction-python"` anyway.

Claude Code substitutes these variables in SKILL.md only. A probe in a plugin session printed `echo "[$CLAUDE_PLUGIN_ROOT] [$CLAUDE_SKILL_DIR]"` as `[] []`, so a copied command runs `"/bin/construction-python"`; under a pattern-restricted Bash grant the command is refused outright ("A variable in this command can't be checked before it runs"). Move the three commands into rfi-drafter's SKILL.md Step 2, where they are substituted, and replace research-checklist.md:16-24 with:
> Rasterize the sheet and crop to the conflict area with the commands in rfi-drafter's Step 2, then read the image.

### 11. pe-review's rules apply "to every response" and add work nobody asked for. Judged; confirmed by cold read.

- pe-review/SKILL.md:16: "Apply `${CLAUDE_SKILL_DIR}/references/pe_review_rules.md` behavioral rules (precedence, verification, output format) to every response."
- pe-review/SKILL.md:17: "Run the **red flag scan** … against any drawing or document you review — even if the red flag is unrelated to the query."
- red-flags.md:3: "Scan for these on EVERY document interaction. Flag when detected even if unrelated to the query."
- pe_review_rules.md:1 "# CLAUDE.md — AgentCM"; :19 "## Mandatory Verification (every response)"; :81-83 "load the `pe-review` skill"

The rules file is a pasted CLAUDE.md: once loaded it governs the rest of the session and tells Claude to load the skill it is already in. The cold reader listed seven additions to a simple "what's missing?" answer (unrelated red flags, a Severity/Type/Priority/Status block and an RFI-ready block per finding, three files written, a verification paragraph, a point-of-no-return analysis) and found no step telling it to read the project documents or how. Its RFI candidates go to `rfi_candidates.md` (pe_review_rules.md:77), which rfi-drafter never reads. Replace SKILL.md:16-17 with:
> 1. Read the documents the question names, following construction-guide's reading rules (load it first).
> 2. Check them against the question, using the references below where they apply.
> 3. Answer the question first. After the answer, list any red flags you noticed outside the question, one line each.
> 4. Log each finding the design team must answer with `issue_manager.py add` (construction-guide, Issue Registry).

Delete pe_review_rules.md:1 and :81-83, and change "(every response)" at :19 to "(before you cite a document)".

### 12. code-researcher has no unattended path, ignores the extracted spec text, and keeps its own project facts. Judged; confirmed by cold read.

- code-researcher/SKILL.md:88: "**Human checkpoints at 1c, 3c, and 4c.** Do not skip them." and :195 "**Do not begin Phase 2 until the user responds.**"
- submittal-review/SKILL.md:169: "If the PE agreed at the checkpoint, run `/construction:code-researcher` on the open questions."
- code-researcher/SKILL.md:115: "write to `.construction/skills/code-researcher/project_context.yaml`"; it never mentions `.construction/skills/spec_text/` or the shared `.construction/skills/project_context.yaml`

Invoked from a review after the PE agreed, it stops three more times; unattended, it cannot finish. It asks again for facts the PE already confirmed at the submittal-review checkpoint, under different keys (`occupancy_group`, `location.county` vs `building.facility_types`), and re-extracts spec PDFs that spec-splitter already repaired. Add after :88:
> When another skill invokes this one after the user agreed to research, treat that agreement as checkpoint 1c and report 3c and 4c at the end instead of stopping. When nobody can answer, do the same and say in the report which checkpoints were skipped. Without web access, stop after Phase 2 and mark every topic `uncertain`.

and in 1a: "Start from `.construction/skills/project_context.yaml`; add what is missing there." In 2a: "Read spec text from `.construction/skills/spec_text/`."

### 13. AgentCM is detected by the `.construction/` folder, which every project has. Judged.

- viewport-highlighter/SKILL.md:30-32: "**Check for AgentCM: `.construction/project.yaml` at the project root.** If `.construction/` is absent, **stop immediately**"
- bid-tabulator/SKILL.md:30: "If project context is available (`.construction/` directory), read `project.yaml`"
- construction-guide/SKILL.md:19: "When AgentCM structured data is available (`.construction/` directory)"

Skills keep working data in `.construction/skills/` in every project (construction-guide:294), so the folder test reports AgentCM where there is none; viewport-highlighter then carries on to an API that isn't there. Replace each with the test construction-guide:30 already states: "`.construction/project.yaml` exists".

### 14. construction-guide is mostly inapplicable where it is loaded, and absent where it is needed. Measured.

- construction-guide/SKILL.md: 6,644 tokens; AgentCM-only material at :15-99, :127-156, :196-199, :213-228; database discovery written three times (:62-66, :77-99, :222-226).
- submittal-review/SKILL.md:38: "Load the `construction-guide` skill before reading any project document."

The flat-file cold reader used 36% of it and the submittal-review reader about 15%. Both original eval runs loaded it in full on the first tool call. Meanwhile the discrimination test chose it alongside another construction skill 0 times in 120 on both models, so `pe-review`, `rfi-drafter` and `code-researcher` run without its reading rules. On `main` (PR #15) the guide grows further and states that its own data-access sections "describe an earlier AgentCM layout". Split it:
> `construction-guide/SKILL.md` (about 1,500 tokens): reading rules, where skills write, precedence (#5), the shared vocabulary (#9), the issue registry command. `construction-guide/references/agentcm.md`: everything AgentCM, loaded with "When `.construction/project.yaml` exists, read `references/agentcm.md` first."

Then a one-line "Load the construction-guide skill before reading project documents" in pe-review, rfi-drafter and code-researcher costs 1,500 tokens instead of 6,600.

### 15. Instructions for other skills live in a skill those skills never load. Judged.

- rfi-drafter/SKILL.md:220-222: "If you are running a skill OTHER than rfi-drafter and you notice a potential issue (schedule conflict, missing reference, spec/drawing mismatch), write it to the registry:"
- construction-guide/SKILL.md:258: "Any skill can log potential issues to `.construction/skills/issues/` via `${CLAUDE_PLUGIN_ROOT}/scripts/issue_manager.py`" (no arguments)

rfi-drafter's SKILL.md is in context only while rfi-drafter runs, so the one complete `issue_manager.py add` example is never seen by the skills it addresses, and those skills' exhaustive allowlists (tag-audit-and-takeoff:347, submittal-log-generator:25, code-researcher:454) don't include the script. Move rfi-drafter:218-237 into construction-guide's Issue Registry paragraph, with the required arguments and the severity mapping from #9, and add `issue_manager.py` to the allowlist of every skill that is meant to log issues.

### Next ten

1. **sheet-splitter, multiple sets:** sheet-splitter:58 says "All split pages go to the same `sheets/` output directory", so a second drawing set's `page_001.pdf` overwrites the first's; :142 says the merge "combines entries from all subdirectories into a single index", but `split_drawing_set.py:114` writes `sheet_index.yaml` inside each `--output-dir`, so no combined index exists where submittal-review and schedule-extractor look (judged from code).
2. **submittal-log-generator:** the same 01 33 00 text is a FLAG reason at :259 and an EXCLUDE at :281.
3. **viewport-highlighter:** :21 "Does NOT … delete viewports" vs :472 "DELETE each existing viewport first".
4. **schedule-extractor:236-237:** `--source_sheet`/`--output_file` are rejected by `write_finding.py`.
5. **rfi-drafter:50:** "Before the first RFI, ask the user for their firm's RFI form template" — nothing records that the user had none, so it asks every time (cold read). Add: "If the user has none, write `{"template": null}` to `rfi_template_map.json` and don't ask again."
6. **rfi-drafter:142-149:** `rfi_draft.json` and `RFI-026.docx` have no folder. Add: "Write the draft data to `.construction/skills/rfi-drafter/` and the .docx to the project's RFI folder (or the project root)."
7. **submittal-review:91-93, :117:** `$PY` and `$FP` are set in one Bash block and used in another; shell variables do not persist between Bash calls (fixed in the rewrite with full commands).
8. **construction-guide:98:** "At session start, run the project orientation query" sits under an unlabelled heading that a flat-file reader may apply. Prefix: "In AgentCM mode, at session start…"
9. **construction-guide:301** (legacy migration, "move it there before continuing") is legacy text loaded on every call; the best-practices page puts this in an "Old patterns" section. Move it to `project-setup`, which already migrates (project-setup:68).
10. **pe-review/references/pe-findings.md** has agent frontmatter (`tools: Read, Write, Glob`), is referenced nowhere, and duplicates pe_review_rules.md:72-79. Delete it.

## 5. Token cuts that change no behavior

Each cut removes text that restates what Claude knows, repeats another line, or repeats another file. Characters measured from the files; tokens ≈ characters ÷ 4. Cuts that change what Claude loads or knows (the AgentCM split, the pe-review checklists, dropping construction-guide from submittal-review) are not here; they are in §6 under "only after an eval".

| Skill | Cut | Chars | ≈ Tokens |
|---|---|---:|---:|
| construction-guide | Skills tables :238-264 → one line ("Skills the user runs: see the `/construction:` menu") | 2,100 | 525 |
| | Second database-discovery block :77-99 (repeats :62-66) and extraction-file table :68-75 (repeats rule 2) | 1,350 | 340 |
| | Drawing-types table and title-block line :107-119; reference-symbol list :183-192; duplicate partial-match tip :209 | 1,900 | 475 |
| | NIC/NFC definitions :372-379; "You already know construction" :406 (repeats pe-review:12); persona :11-13; known conventions :412-415 | 1,300 | 325 |
| | Legacy migration :301 (move to project-setup, which already migrates) | 311 | 80 |
| | **Subtotal** (26% of the file) | **~6,960** | **~1,740** |
| code-researcher | Workflow overview :60-86 (repeats the phase headings) | 1,000 | 250 |
| | "What This Skill Does" :12-35 and "Research Philosophy" :50-56 → three lines; "Use your full domain knowledge" :153-157 | 2,200 | 550 |
| | Checkpoint blocks :163-193, :297-319, :361-393: keep the structure, drop the resinous-flooring values | 1,800 | 450 |
| | **Subtotal** (23% of the file) | **~5,000** | **~1,250** |
| rfi-drafter | Second allowlist :262-269 (repeats :26-34) | 614 | 155 |
| | Output section :241-258 (repeats Step 5 and Mode 2) | 700 | 175 |
| | Step 3 and Step 4 bullet lists :110-120, :124-131 (repeat rfi-format.md and quality-checks.md) → one line each | 730 | 180 |
| | "RIGID … GUIDED … FLEXIBLE" :18-24; "a 30-minute task compressed to minutes" :46 | 400 | 100 |
| | **Subtotal** (22% of the file) | **~2,440** | **~610** |
| pe-review | SKILL.md:12 and :25 restate "you already know construction" → one line; pe_review_rules.md:1 and :81-83 | 680 | 170 |
| submittal-review | Intro bullets :14-18 → one sentence | 270 | 70 |
| code-researcher references | schemas.yaml example values → key names with one-line comments (14.8K → ~5K chars); gap_report_template.md → a template with placeholders (5.0K → ~2.5K). This is also the fix for #2 | ~12,300 | ~3,080 |

In a flat-file project, also moving construction-guide's AgentCM material (:15-99, :127-156, :213-228, about 7,200 characters beyond the cuts above) into a reference loaded only when `.construction/project.yaml` exists saves another ~1,800 tokens wherever the guide is loaded. That changes what Claude reads, so it belongs with the eval-gated items.

The rest of the plugin: a second reviewer estimated about 6,000 tokens of no-behavior cuts across the other ten skills: subcontract-writer ~800 and submittal-log-generator ~950 (each brings the file under 500 lines), tag-audit-and-takeoff ~1,300 (mostly database-model tables in quantity-model.md that Claude never acts on), viewport-highlighter ~800 (API response bodies), bid-evaluator ~650, schedule-extractor ~550, bid-tabulator ~500, spec-splitter ~290, sheet-splitter ~130, project-setup ~100. Across all skills, the "RIGID / GUIDED / FLEXIBLE" labels (bid-evaluator:29-33, bid-tabulator:15, submittal-log-generator:19-23) and the "offload / release from context" lines (bid-evaluator:66, :93, :179-184; submittal-log-generator:399) can go: Claude cannot unload context, and the labels change nothing.

## 6. What to do

### Change now (cheapest first; each fixes wrong facts, broken mechanics, contradictions or dead text)

1. **Fix the page-numbering text** (#1): construction-guide:137 and :148, viewport-highlighter:65. Three lines.
2. **Merge `submittal-review`'s mechanical fixes from the rewrite** (commit `5e7f6f9`): the page-numbering line, `status` after every step, full commands, the issue-severity mapping, the sheet-splitter wording. Each corrects a measured error, and the A/B shows no score or cost penalty (§3.4).
3. **Stop naming skills Claude can't invoke** (#7): submittal-review:82, construction-guide:103, :175, :240, bid-evaluator:23; delete `spec-parser` (construction-guide:258, rfi-drafter:164, issue-schema.md:112, spec-splitter:16, :117); change `split_drawing_set.py:152` and `:197` so they stop pointing to `/sheet-index-builder`.
4. **Fix schedule-extractor's crop units and graph flags** (#4, next-ten #4): "fractions (0–1)" plus `--normalized`; `--source-sheet`, `--output-file`.
5. **Detect AgentCM by `project.yaml`** (#13): viewport-highlighter:32, bid-tabulator:30, construction-guide:19.
6. **Remove the path variables from research-checklist.md** (#10), moving the commands into rfi-drafter's SKILL.md.
7. **Replace the wrong code citations in examples** (#2): code-researcher SKILL.md:301, :314, :366; schemas.yaml; gap_report_template.md; rfi-format.md's example RFI; subcontract-writer:178 ("L&E Article" → State Finance and Procurement Article, or better, "look up the state's prevailing-wage statute").
8. **One precedence block, one grade list, one issue-severity mapping**, all in construction-guide (#5, #9). Point pe_review_rules.md at them; delete its title line, "(every response)" and the Skills section (#11); delete the orphan pe-findings.md.
9. **Give code-researcher per-scope folders and an invoked/unattended path** (#3, #12), and have it read the shared `project_context.yaml` and `spec_text/`.
10. **Move rfi-drafter's other-skill instructions to construction-guide** and add `issue_manager.py` to the allowlist of every skill meant to log issues (#15); route pe-review's RFI candidates to the registry instead of `rfi_candidates.md`.
11. **Resolve the in-skill contradictions** the sweep found: viewport-highlighter:21 vs :472; submittal-log-generator:259 vs :281; tag-audit-and-takeoff:46 vs :155 (flat-file vision step); rfi-drafter:157 "always .docx" vs `generate_rfi_pdf.py`; issue status after export (`escalated` vs issue-schema.md:105 `resolved`).
12. **Apply the token cuts in §5.** About 3,800 tokens across the five review-workflow skills, plus ~3,000 in code-researcher's references. These shrink context and the surface for contradictions; §3.4 shows they will not measurably cut cost on submittal-review, where page images and long writes dominate.
13. **Bring the SOP in line with the code and the docs:** 250 → 1,536 characters (SOP:39, :47, :242, :588); "Check for .construction/ directory" → `.construction/project.yaml` (SOP:407, :497, :600); `.construction/spec_text/` → `.construction/skills/spec_text/` (SOP:202, :271, :285); and state that a skill another skill must invoke cannot be `disable-model-invocation: true` (SOP:564 vs :591).
14. **sheet-splitter, multiple sets** (next-ten #1): replace :58 "All split pages go to the same `sheets/` output directory" with "One PDF: `--output-dir \"{drawings}/sheets\"`. Several: `\"{drawings}/sheets/{source_pdf_stem}\"` for each; each folder gets its own `sheet_index.yaml`", and delete the merge claim at :141.
15. **Per-scope storage and real resume state** in bid-tabulator (`bids/{scope_slug}/`, and the `status` key its resume step reads) and submittal-log-generator (append each section's items to a batch file on disk, not "in memory", :397).

### Only after an eval shows it helps

1. **Adopt the rest of the `submittal-review` rewrite only on new evidence.** It tied the original on score and cost (§3.4); its mechanical fixes are already in "change now" item 2. Re-test the remainder (construction-guide not loaded in flat-file runs, workers inlining the reading rules) on the harder fixture in item 6, and decide first whether fan-out is required: Sonnet skipped it in all four 19-element runs.
2. **Split construction-guide** into a ~1,500-token core and an AgentCM reference (#14). Gate: the pe-review and rfi-drafter cases (they exist on `integrate/skills-foundation`) score the same or better with the slim guide, and an AgentCM-mode run still finds the database.
3. **Load the slim guide from pe-review, rfi-drafter and code-researcher.** Gate: those cases stop reading PDFs with the Read tool or inline Python, with no score loss.
4. **Cut pe-review's checklists to what Claude doesn't already know.** The CSI-layer audit found 94% of comparable content was restatement; red-flags, absence, coordination and scope-gap files are ~3,350 tokens. Gate: a pe-review case with a no-plugin arm passes without them; restore only the items a case fails without.
5. **Rewrite the heavy emphasis** in tag-audit-and-takeoff (12 strong markers: "**HARD GATE — you MUST complete this step**", "**CRITICAL — Vision is MANDATORY for this step.**"), submittal-log-generator (11: "RIGID" in six headings, "**THE CRITICAL RULE**") and bid-tabulator (4). Calm versions: "Complete this step before Step 2: …"; "Read each sheet's image to find tags; the text layer misses …". Gate: their cases show the steps still happen.
6. **Build the harder submittal-review fixture** the decisions doc lists first. Both current fixtures saturate at 1.0 with and without the rewrite, so they can compare cost but not review quality.
