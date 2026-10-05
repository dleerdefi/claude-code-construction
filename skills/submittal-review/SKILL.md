---
name: submittal-review
description: >
  Expert PE review of a submittal (shop drawings, product data, samples,
  equipment brochures) against specs, drawings, code questions and trade
  coordination. Produces findings with both sources, trade routing and a
  completeness gate. Triggers: 'review submittal', 'review shop drawings'.
argument-hint: "<submittal.pdf> [--section \"12 35 53\"] [--resubmittal-of <review_id>]"
disable-model-invocation: true
---

# Submittal Review

Review a submittal the way an experienced Project Engineer does, then hand the PE a draft GC review they can trust. The trust comes from four things:
- every requirement is traced from the contract documents before the submittal is opened;
- every document that governs an element is read, and the gate proves it;
- every finding cites both sides and says who acts;
- nothing the documents cannot answer is stated as fact.

**What it produces:** findings with sources and actions, a suggested GC disposition, routing to the trades that must act and by when, code and authority questions, and what could not be verified. **What it never does:** approve, stamp or send anything. The PE decides the disposition and sends the review.

The procedure is the same for every CSI division. Your knowledge of the trade supplies the checks. `references/review-lens.md` lists what reviews most often skip: package questions, cross-trade handoffs, and code and authority questions.

## Permitted Scripts

| Script | Location | Purpose |
|---|---|---|
| `find_pages.py` | `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/` | Index a large submittal once; find the pages for each element |
| `check_review.py` | `${CLAUDE_SKILL_DIR}/scripts/` | Write review records; prove the review is complete |
| `export_submittal_review.py` | `${CLAUDE_SKILL_DIR}/scripts/` | Build the Excel review, suggested disposition and markup items |
| `annotate_pdf.py` | `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/` | Write review clouds and notes onto a copy of the submittal |
| `rasterize_page.py`, `crop_region.py`, `extract_text_region.py` | `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/` | Read submittal and drawing pages |
| `issue_manager.py` | `${CLAUDE_PLUGIN_ROOT}/scripts/` | Log design-team questions as issues for `rfi-drafter` |
| `write_finding.py` | `${CLAUDE_PLUGIN_ROOT}/scripts/graph/` | Graph entry (AgentCM only) |

Run every script through `"${CLAUDE_PLUGIN_ROOT}/bin/construction-python"`. Double-quote every path. Do not write custom scripts: write the JSON files below directly and let the permitted scripts read them.

Load the `construction-guide` skill before reading any project document. Never read construction PDFs directly: rasterize pages first.

## Data Contract

Everything for one review lives in `.construction/skills/submittal-review/{review_id}/`, where `review_id` is the submittal number and revision with spaces as hyphens (`12-35-53-001-R0`). The exact formats are in `${CLAUDE_SKILL_DIR}/references/review-data.md`; read it before Step 1.

```
state.yaml            submittal, sections, facility types, jurisdiction, schedule, status
pages_N.json          page index of submittal file N (find_pages.py)
trace.json            every element the contract documents require, with every governing reference
inventory.json        where each element is in the submittal (or that it is missing)
review_NN.json        per element: each governing reference read, findings, unverifiable items, questions
package_review.json   the package questions and every cross-document reconciliation
findings_NN.json      findings
compliance.json       code and authority questions: open, or researched with a source
routing.json          each trade that must act: what to send, what is needed back, gate, need-by
prior.json            resubmittals only: what happened to each prior finding
```

`state.yaml` carries `status`. On restart, read it and resume at the step after the last completed one.

---

## Workflow

```
- [ ] 1. Intake               - [ ] 6. Package questions and reconciliations
- [ ] 2. Trace requirements   - [ ] 7. Code questions and routing
- [ ] 3. Inventory            - [ ] 8. Gate
- [ ] 4. Checkpoint           - [ ] 9. Report
- [ ] 5. Review (fan out per element)
```

### 1. Intake

1. **Mode.** `.construction/project.yaml` present → AgentCM mode; otherwise flat file.
2. **Submittal.** Locate the package file(s). Read the cover or transmittal for:
   - submittal number, revision and title;
   - subcontractor;
   - spec section(s);
   - submittal types, using `submittal-log-generator`'s labels (Shop Drawings, Product Data, Samples, Design Data, Test Reports, Certificates, Delegated Design, ...).
3. **Resubmittal.** If the revision is above zero or the user names a prior review, find the prior review directory. Every prior finding must be accounted for in `prior.json` (Step 6).
4. **Prerequisites.**
   - **Spec text** must exist in `.construction/skills/spec_text/`. If it does not, run `/construction:spec-splitter`.
   - **Drawing sheets** must be split and indexed (`sheet_index.yaml`, or AgentCM's index). If they are not, run `/construction:sheet-splitter`.
5. **Project facts.** Read `.construction/skills/project_context.yaml`:
   - **Facility types** (`building.facility_types`): if missing, infer them from the cover sheet and code analysis, and confirm them at the checkpoint.
   - **Jurisdiction:** city, county and state.
   - **Construction schedule:** if the project has one, record its path in `state.yaml` as `schedule`.
6. **Register.** Check the submittal log for this item, and the RFI log and ASI/bulletin log for changes that affect the section. Note approved submittals this one depends on, such as the approved sink or fume hood a casework submittal must fit.
7. **Lessons.** If `.construction/skills/submittal-review/lessons.yaml` exists, read it. It holds what earlier reviews on this project missed or the PE overturned.
8. **Index each submittal file** (any file over about 20 pages):
   ```bash
   PY="${CLAUDE_PLUGIN_ROOT}/bin/construction-python"; FP="${CLAUDE_PLUGIN_ROOT}/scripts/pdf/find_pages.py"
   "$PY" "$FP" index --pdf "{submittal file N}" --output "{dir}/pages_N.json"
   ```
   It reports pages with no text layer (scans). Those must be rasterized to be read.

Write `state.yaml` (status: `intake`).

### 2. Trace requirements (before reading the submittal)

A review fails most often because the right detail was never pulled. Build `trace.json` from the contract documents alone:

1. **Package requirements.** Every submittal requirement in Part 1 of the section, with its article reference.
2. **Elements.** Every element of the scope in the contract documents:
   - Use each tagged elevation, equipment item, mark, door number, fixture type or assembly.
   - Find them in plans, elevations, details and schedules.
   - In AgentCM mode, query the database for tags and cross-references instead of reading sheets (read `query_command` from `.construction/database.yaml`; views in `.construction/db_schema.yaml`).
   - For product data with no tagged elements, the elements are the products the spec requires.
3. **Governing references per element** (`cd_refs`): every sheet, detail, section cut, schedule row and spec article that governs it. Follow every cut drawn on an elevation or plan. Record in `stated` what each one states about the element (sizes, models, ratings, heights, voltages, finishes, supports).
4. **Changes.** Apply responded RFIs, ASIs and bulletins to the trace, citing them.

### 3. Inventory the submittal

Map the submittal to the trace in `inventory.json`, both ways.

1. **Find each element's pages.** For an indexed file, write `element_terms.json` with the search terms for each element: tag, item number, name, scheduled model. Then run:
   ```bash
   "$PY" "$FP" map --index "{dir}/pages_N.json" --elements "{dir}/element_terms.json" --output "{dir}/page_map_N.json"
   ```
   It lists, per element, its heading pages and the pages that follow until the next element's tab. It also lists tabs that match no element (possible extra items), pages that match nothing, and image-only pages.
2. **Confirm the map.** Check each element's first page by reading its heading (`extract_text_region.py`, or a rasterized strip). For a short file, identify pages from titles and tags directly.
3. **Record the result:**
   - each trace element → its pages, or `missing`;
   - each submittal item with no matching element → `extra_items`, with a note;
   - each Part 1 package requirement → submitted or missing.

A missing element or package item becomes a completeness finding. Keep this pass light; detailed reading happens in Step 5.

### 4. Checkpoint

Show the user, in one short message:
- the section(s), submittal types, element count and pages, facility types and jurisdiction;
- the code and authority questions the trace already raises (accessibility, health department, fire, state agency, utility), each as a question.

Ask two things: confirm the facility types and jurisdiction, and whether to run `/construction:code-researcher` on those questions. A researched question can be checked. An unresearched one stays open in the report and is never answered from memory.

Write confirmed facility types to `project_context.yaml` (`building.facility_types`) if they were missing. If nobody can answer (unattended run), set `unattended: true`, proceed with the inferred values, leave every question open, and say so at the top of the report.

### 5. Review

Start each batch from its records:
```bash
"$PY" "${CLAUDE_SKILL_DIR}/scripts/check_review.py" --review-dir "{dir}" --scaffold {NN} --elements "{ids}"
```
This writes `review_{NN}.json` with every governing reference of each element marked `todo`.

- **Up to about eight elements:** review them yourself, following the worker prompt's per-element steps, one element at a time, releasing each element's pages before the next.
- **More:** fan out. Batch about five to eight elements per worker and launch the workers in parallel with the Agent tool, using `${CLAUDE_SKILL_DIR}/references/worker-prompt.md`. Fill `{plugin_root}` with `${CLAUDE_PLUGIN_ROOT}` and `{skill_dir}` with `${CLAUDE_SKILL_DIR}`. Each worker writes `findings_{NN}.json` and fills `review_{NN}.json`, then returns one line. If a batch file is incomplete, re-run that worker. Never parse results from a worker's reply.

Reviewing an element means four things:
- read every governing reference and the submittal pages;
- compare everything the references state;
- ask the cross-trade questions in `references/review-lens.md`;
- note every code or authority question it raises.

A finding cites both sides: the requirement (sheet, detail, schedule row, spec article, RFI or ASI) and the submittal (file, page, what it shows). Write findings as described in `${CLAUDE_SKILL_DIR}/references/review-writing.md`.

### 6. Package questions, reconciliations and prior comments

Yourself, in the main context:
1. `check_review.py --scaffold 90 --package` writes the eight package questions from the lens. Answer each.
2. **Reconcile** every pair of documents that must agree on the same items, field by field, and add a row for each. Examples: the equipment schedule against the electrical panel and plumbing connection schedules; fixture models against casework cutouts; hardware sets against the door schedule; submitted weights against the structural loads. A mismatch is a finding with both sources.
3. **Resubmittals:** every prior finding goes into `prior.json` as closed, open or partially closed, with evidence. An unaddressed prior comment is a finding of its own.

Your own findings use batch `90`: `F-90-01`, ...

### 7. Code questions and routing

**Code and authority questions** (`compliance.json`): gather the `questions` from every review record, add your own, and merge duplicates. Each row is a full question naming the authority and the elements it affects.
- If the PE agreed at the checkpoint, run `/construction:code-researcher` on the open questions. A question is `researched` only when a code-researcher topic file answers it: cite that file as `source`, then mark the result `consistent` or `finding`. A finding cites the code, edition and section from that file.
- Otherwise the question stays `open`, with the research command to run.

Never state a code requirement you have not retrieved.

**Routing** (`routing.json`): one row per trade that must act. Each row says:
- what to send them (pages, items);
- what is needed back;
- who to confirm for furnish, install and connect;
- the gate, the milestone in `${CLAUDE_SKILL_DIR}/references/milestones.yaml` by which it must be resolved;
- the need-by: the start date of that milestone's activity in this area, from the project schedule (record the activity), or `no schedule` when the project has none.

Every coordination finding belongs to a routing row.

### 8. Gate

```bash
"$PY" "${CLAUDE_SKILL_DIR}/scripts/check_review.py" --review-dir "{dir}"
```

It fails when any of these is true:
- an element in the trace is missing from the inventory, or a missing element has no completeness finding;
- a submitted element has no review record;
- a governing reference is unaccounted for or still `todo`;
- a package question is unanswered;
- a finding lacks a source, an action or a real element;
- a coordination finding is not routed, or a routing row lacks a gate or need-by;
- a code question is a bare topic name, or is marked researched without a code-researcher source;
- a prior finding is unaccounted for.

Fix every gap and re-run until it passes. Do not report before it passes. If something truly cannot be verified, record it as unverifiable with what is missing; that is part of the review, and it goes in the report.

### 9. Report

```bash
"$PY" "${CLAUDE_SKILL_DIR}/scripts/export_submittal_review.py" --review-dir "{dir}" \
  --output "{submittals_folder}/{submittal_no} R{rev} - GC Review.xlsx" --annotations "{dir}/markup"
"$PY" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/annotate_pdf.py" --pdf "{submittal.pdf}" \
  --items "{dir}/markup/{file_stem}.json" --output "{submittals_folder}/{submittal_no} R{rev} - GC Markup.pdf" --author "GC Review (draft)"
```

Deliverables go in the project's submittals folder (or the project root), never in `.construction/`. The export prints the **suggested disposition**; the rules are in `review-writing.md`.

Then:
1. **Issues.** Each design-team-owned finding (an absence in the CDs, a conflict between documents, a question only the A/E can answer) goes to the issue registry with `issue_manager.py add --source-skill submittal-review`, so `rfi-drafter` can turn it into an RFI. Never draft or send the RFI from here.
2. **Graph.** In AgentCM mode: `write_finding.py --type submittal_review` with counts and the output paths.
3. **Tell the PE**, briefly, as `review-writing.md` describes. Never split a finding from its action.
4. Set `status: complete` in `state.yaml`.

### Lessons

When the PE overturns a finding, or a miss surfaces later, append it to `.construction/skills/submittal-review/lessons.yaml` with:
- the section;
- what happened;
- what the review should have read or asked.

Step 1 reads this file on the next review in the project.

---

## Rules

- The contract documents govern. Precedence and the RFI and submittal authority rules are in `pe-review`'s `references/pe_review_rules.md`.
- Surface conflicts; never resolve them. If the drawings and the spec disagree, that is a design-team finding, not a reason to accept the submittal.
- No fabricated references. Every sheet, detail, article and code citation comes from a document you read or a finding `code-researcher` recorded.
- "By others" is not an answer. Name who, or record a scope gap.
- Approved-as-noted markups and responded RFIs change the trace. Read them.
- Draft only. Disposition is a suggestion; the PE decides and sends.
