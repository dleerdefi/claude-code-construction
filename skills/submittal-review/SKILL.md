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

Draft the GC's review of one submittal for the PE: findings that cite both the contract documents and the submittal, a suggested disposition, routing to the trades that must act and by when, code and authority questions, and what could not be verified. You never approve, stamp or send anything; the PE decides the disposition and sends the review.

The procedure is the same for every CSI division; your knowledge of the trade supplies the checks. `references/review-lens.md` lists what reviews most often skip.

## Scripts

Use only these. Run each with `"${CLAUDE_PLUGIN_ROOT}/bin/construction-python"` and double-quote every path. Write the JSON and YAML files yourself; don't write scripts, including inline `python -c`. The commands here and the formats in `references/review-data.md` are complete, so you don't need to open the scripts.

| Script | Path | Use |
|---|---|---|
| `rasterize_page.py` | `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/` | `"<pdf>" <page> --dpi 200 --output "<png>"` |
| `crop_region.py` | `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/` | `"<png>" --box x1,y1,x2,y2 --normalized --output "<png>"` |
| `extract_text_region.py` | `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/` | `"<pdf>" <page> [--bbox x1,y1,x2,y2]`: a page's text layer |
| `find_pages.py` | `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/` | Index a large submittal file; find each element's pages |
| `check_review.py` | `${CLAUDE_SKILL_DIR}/scripts/` | Scaffold review records; the completeness gate |
| `export_submittal_review.py` | `${CLAUDE_SKILL_DIR}/scripts/` | Excel review, suggested disposition, markup items |
| `annotate_pdf.py` | `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/` | Review clouds on a copy of the submittal |
| `issue_manager.py` | `${CLAUDE_PLUGIN_ROOT}/scripts/` | Log design-team questions for `rfi-drafter` |
| `write_finding.py` | `${CLAUDE_PLUGIN_ROOT}/scripts/graph/` | Graph entry, AgentCM mode only |

## Reading documents

- Read PDFs through the scripts, not the Read tool: drawing sheets are too large to read legibly that way, and a long brochure exceeds what one read returns. Rasterize the page (crop when detail matters) and read the PNG; use `extract_text_region.py` or `find_pages.py` for text.
- Page numbers start at 1 in every script and every review file.
- Split sheets are one page each: rasterize page 1 of the sheet's own PDF (`filename` in `sheet_index.yaml`, in the same folder). `page_index` in `sheet_index.yaml` counts from 0 within `source_pdf`.
- Spec text is already extracted: `.construction/skills/spec_text/<section with underscores>.txt` (`12_35_53.txt`).
- Write images and other working files inside the review directory.
- AgentCM mode only: load the `construction-guide` skill for the database and graph conventions.

## Data contract

Everything for one review lives in `.construction/skills/submittal-review/{review_id}/`, where `review_id` is the submittal number and revision with spaces as hyphens (`12-35-53-001-R0`). Read `${CLAUDE_SKILL_DIR}/references/review-data.md`, which gives the format of every file, before Step 1.

```
state.yaml            submittal, sections, facility types, jurisdiction, schedule, notes, status
pages_N.json          page index of submittal file N (find_pages.py)
trace.json            every element the contract documents require, with every governing reference
inventory.json        where each element is in the submittal, or that it is missing
review_NN.json        per element: each governing reference read, findings, unverifiable items, questions
package_review.json   the package questions and every cross-document reconciliation
findings_NN.json      findings
compliance.json       code and authority questions: open, or researched with a source
routing.json          each trade that must act: what to send, what is needed back, gate, need-by
prior.json            resubmittals only: what happened to each prior finding
```

`status` in `state.yaml` names the last completed step. Set it at the end of every step; on a restart, read it and resume at the next step.

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
2. **Submittal.** Locate the package file(s). Read only the cover or transmittal page now, for:
   - submittal number, revision and title;
   - subcontractor;
   - spec section(s);
   - submittal types, using `submittal-log-generator`'s labels (Shop Drawings, Product Data, Samples, Design Data, Test Reports, Certificates, Delegated Design).
3. **Resubmittal.** If the revision is above zero or the user names a prior review, set `prior_review` to that review's id. Step 6 accounts for every prior finding.
4. **Prerequisites.**
   - **Spec text** in `.construction/skills/spec_text/`. If it is missing, invoke the `construction:spec-splitter` skill.
   - **Drawing sheets** split and indexed (`sheet_index.yaml`, or AgentCM's index). If they are not, ask the user to run `/construction:sheet-splitter`; you cannot invoke it. Unattended, read the bound drawing set instead and add a line to `notes`.
5. **Project facts.** From `.construction/skills/project_context.yaml`:
   - **Facility types** (`building.facility_types`). If missing, infer them from the cover sheet and code analysis and confirm them at the checkpoint.
   - **Jurisdiction:** city, county and state. Record what is known; put what is missing in `notes`.
   - **Construction schedule:** if the project has one, record its path as `schedule`.
6. **Registers.** Check the submittal log for this item, and the RFI and ASI/bulletin logs for changes to the section. Note approved submittals this one must fit, such as the approved sink a casework submittal must take. A log that doesn't exist goes in `notes`.
7. **Lessons.** If `.construction/skills/submittal-review/lessons.yaml` exists, read it: it holds what earlier reviews on this project missed or the PE overturned.
8. **Index each submittal file over about 20 pages:**
   ```bash
   "${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/find_pages.py" index --pdf "{submittal file N}" --output "{dir}/pages_N.json"
   ```
   It lists pages with no text layer (scans); rasterize those to read them.

Write `state.yaml` with `status: intake`.

### 2. Trace requirements, before reading the submittal

A review fails most often because the right detail was never pulled. Build `trace.json` from the contract documents alone:

1. **Package requirements.** Every submittal requirement in Part 1 of the section, with its article reference.
2. **Elements.** An element is one thing the contract documents tag or list: an elevation, equipment item, mark, door, fixture type or assembly. Use the id the documents use.
   - Find each in the plans, elevations, details and schedules.
   - In AgentCM mode, query the database for tags and cross-references instead of reading sheets (`query_command` in `.construction/database.yaml`; views in `.construction/db_schema.yaml`).
   - For product data with no tagged elements, the elements are the products the spec requires.
   - A schedule that must agree with an element (a fixture schedule against casework cutouts) is a reconciliation in Step 6, not another element.
3. **Governing references per element** (`cd_refs`): every sheet, detail, section cut, schedule row and spec article that governs it. Follow every cut drawn on an elevation or plan. Record in `stated` what each one states about the element: sizes, models, ratings, heights, voltages, finishes, supports.
4. **Changes.** Apply responded RFIs, ASIs and bulletins to the trace, citing them.

Set `status: trace`.

### 3. Inventory the submittal

Map the submittal to the trace in `inventory.json`, both ways.

1. **Find each element's pages.** For an indexed file, write `{dir}/element_terms.json` with the search terms for each element (tag, item number, name, scheduled model), then run:
   ```bash
   "${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/find_pages.py" map --index "{dir}/pages_N.json" --elements "{dir}/element_terms.json" --output "{dir}/page_map_N.json"
   ```
   It lists each element's heading pages and the pages that follow until the next element, tabs that match no element (possible extra items), pages that match nothing, and image-only pages.
2. **Confirm the map.** Check each element's first page by reading its heading (`extract_text_region.py`, or a rasterized strip). For a short file, identify pages from titles and tags directly.
3. **Record the result:**
   - each trace element → its pages, or `missing`;
   - each submittal item with no matching element → `extra_items`, with a note;
   - each Part 1 package requirement → submitted or missing.

Each `missing` element or package item gets a completeness finding in `findings_90.json`; a `partial` element gets a finding that lists what is absent. Keep this pass light; detailed reading happens in Step 5.

Set `status: inventory`.

### 4. Checkpoint

Show the user, in one short message:
- the section(s), submittal types, element count and pages, facility types and jurisdiction;
- the code and authority questions the trace already raises (accessibility, health department, fire, state agency, utility), each as a question.

Ask two things: confirm the facility types and jurisdiction, and whether to run `/construction:code-researcher` on those questions. A researched question can be checked; an unresearched one stays open in the report.

Write confirmed facility types to `project_context.yaml` (`building.facility_types`) if they were missing.

**Unattended** (nobody can answer): don't wait. Set `unattended: true`, proceed with the inferred values, keep every code question open, add a `notes` line saying so (the workbook prints `notes` as assumptions), and open your final message with it.

Set `status: checkpoint`.

### 5. Review

Scaffold each batch's records:
```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_SKILL_DIR}/scripts/check_review.py" --review-dir "{dir}" --scaffold {NN} --elements "{id},{id}"
```
This writes `review_{NN}.json` with every governing reference of each element marked `todo`.

- **Eight elements or fewer:** review them yourself, one at a time, following the per-element steps in `${CLAUDE_SKILL_DIR}/references/worker-prompt.md`.
- **Nine or more:** launch workers in parallel with the Agent tool, five to eight elements each, using `${CLAUDE_SKILL_DIR}/references/worker-prompt.md`. Fill `{plugin_root}` with `${CLAUDE_PLUGIN_ROOT}` and `{skill_dir}` with `${CLAUDE_SKILL_DIR}`. Each worker writes `findings_{NN}.json` and fills `review_{NN}.json`, then replies with one line. Take results from the files, not the replies; re-run a worker whose files are incomplete.

Reviewing an element means four things:
- read every governing reference and the submittal pages;
- compare everything the references state;
- ask the cross-trade questions in `references/review-lens.md`;
- note every code or authority question it raises.

A finding cites both sides: the requirement (sheet, detail, schedule row, spec article, RFI or ASI) and the submittal (file, page, what it shows). Write findings as `${CLAUDE_SKILL_DIR}/references/review-writing.md` describes.

Set `status: review`.

### 6. Package questions, reconciliations and prior comments

Yourself, in the main context:
1. Scaffold the eight package questions from the lens, then answer each:
   ```bash
   "${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_SKILL_DIR}/scripts/check_review.py" --review-dir "{dir}" --scaffold 90 --package
   ```
2. **Reconcile** every pair of documents that must agree on the same items, field by field, and add a row for each: the equipment schedule against the electrical and plumbing connection schedules; fixture models against casework cutouts; hardware sets against the door schedule; submitted weights against the structural loads. A mismatch is a finding with both sources.
3. **Resubmittals:** every prior finding goes into `prior.json` as closed, open or partially closed, with evidence. An unaddressed prior comment is a finding of its own.

Your own findings use batch `90`: `F-90-01`, `F-90-02`, ...

Set `status: package`.

### 7. Code questions and routing

**Code and authority questions** (`compliance.json`): gather the `questions` from every review record, add your own, and merge duplicates. Each row is a full question naming the authority and the elements it affects.
- If the PE agreed at the checkpoint, invoke `construction:code-researcher` on the open questions. A question is `researched` only when a code-researcher topic file answers it: cite that file as `source`, then mark the result `consistent` or `finding`. A finding cites the code, edition and section from that file.
- Otherwise the question stays `open`, with the research command to run (`/construction:code-researcher <short-topic-slug>`).

State a code requirement only when code-researcher retrieved it; the PE relies on every citation being sourced.

**Routing** (`routing.json`): one row per trade that must act. Each row says:
- what to send them (pages, items);
- what is needed back;
- who to confirm for furnish, install and connect;
- the gate: the milestone id in `${CLAUDE_SKILL_DIR}/references/milestones.yaml` by which it must be resolved;
- the need-by: the start date of that milestone's activity in this area, from the project schedule (name the activity), or `no schedule` when the project has none.

Every coordination finding belongs to a routing row.

Set `status: routing`.

### 8. Gate

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_SKILL_DIR}/scripts/check_review.py" --review-dir "{dir}"
```

It prints each gap and fails when:
- a trace element is missing from the inventory, or a missing element has no completeness finding;
- a submitted element has no review record, or a governing reference is unaccounted for or still `todo`;
- a package question is unanswered;
- a finding lacks a source, an action or a real element;
- a coordination finding is not routed, or a routing row lacks a gate or need-by;
- a code question is a bare topic name, or is marked researched without a code-researcher source;
- a prior finding is unaccounted for.

Fix each gap and re-run until it passes. What truly cannot be verified is recorded as `unverifiable` (or a reference as `unavailable`) with what is missing; that is part of the review and goes in the report.

Set `status: gate`.

### 9. Report

Deliverables go in the folder that holds the submittal (or the project root), never in `.construction/`:
```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_SKILL_DIR}/scripts/export_submittal_review.py" --review-dir "{dir}" --output "{submittal folder}/{submittal number} R{revision} - GC Review.xlsx" --annotations "{dir}/markup"
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/annotate_pdf.py" --pdf "{submittal file}" --items "{markup file the export printed}" --output "{submittal folder}/{submittal number} R{revision} - GC Markup.pdf" --author "GC Review (draft)"
```
The export prints the **suggested disposition** (rules in `review-writing.md`) and the path of each markup file.

Then:
1. **Issues.** Log each finding with `rfi_candidate: true` so `rfi-drafter` can turn it into an RFI; don't draft the RFI here. Severity: `conflict` for a CONFLICTING grade, `warning` for NOT FOUND or OPEN, `safety` for a life-safety finding.
   ```bash
   "${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/issue_manager.py" add --source-skill submittal-review --severity {severity} --confidence high --description "{finding}" --sheets "{sheets}" --spec-sections "{sections}" --elements "{element}" --context "submittal-review {review_id} {finding id}" --rfi-subject "{subject}"
   ```
2. **Graph.** AgentCM mode only: `write_finding.py --type submittal_review --title "{submittal number} R{revision} review" --data '{counts}' --output-files '["{xlsx}", "{pdf}"]'`.
3. **Tell the PE**, briefly, as `review-writing.md` describes, each finding with its action.
4. Set `status: complete`.

### Lessons

When the PE overturns a finding or a miss surfaces later, append to `.construction/skills/submittal-review/lessons.yaml`: the section, what happened, and what the review should have read or asked. Step 1 reads it on the next review.

---

## Rules

- Surface conflicts; don't resolve them. When documents disagree, cite both and make it a design-team finding: the A/E decides which governs, and a conflict is not a reason to accept the submittal.
- Approved-as-noted markups, responded RFIs, ASIs and bulletins change the trace. Read them.
- Every sheet, detail, article and code citation comes from a document you read or a finding `code-researcher` recorded.
- "By others" is not an answer. Name who, or record a scope gap.
- Draft only. The disposition is a suggestion; the PE decides and sends.
