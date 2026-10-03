---
name: submittal-review
description: >
  Expert PE review of a submittal (shop drawings, product data, samples,
  equipment brochures) against specs, drawings, code questions and trade
  coordination. Produces findings, a coverage ledger and coordination
  routing. Triggers: 'review submittal', 'review shop drawings'.
argument-hint: "<submittal.pdf> [--section \"12 35 53\"] [--resubmittal-of <review_id>]"
disable-model-invocation: true
---

# Submittal Review

Review a submittal the way an experienced Project Engineer does, then hand the PE a draft GC review they can trust. Trust comes from three things this skill enforces: every requirement is traced to its source before review, every element is checked against every applicable check (the **coverage ledger** proves it), and nothing the documents cannot answer is stated as fact.

**What it produces:** findings with sources and actions, a suggested GC disposition, routing to the trades that must coordinate, open compliance questions, and a coverage ledger. **What it never does:** approve, stamp or send anything. The PE decides the disposition and sends the review.

The procedure here is the same for every CSI division. What to check for a given section comes from the CSI knowledge layer, compiled per section.

## Permitted Scripts

| Script | Location | Purpose |
|---|---|---|
| `csi_knowledge.py` | `${CLAUDE_PLUGIN_ROOT}/scripts/csi/` | Compile section knowledge, reflexes, milestones |
| `check_coverage.py` | `${CLAUDE_SKILL_DIR}/scripts/` | Prove the review covered every element, check, hook and interface |
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
state.yaml        submittal, sections, facility types, prior review, status
context.yaml/.md  compiled knowledge (resolver output)
reflexes.md       always-on checks for this project
trace.json        every element the contract documents require, with its CD references
inventory.json    where each element is in the submittal (or that it is missing)
values_*.json     values read from the submittal, per element
findings_*.json   findings
coverage_*.json   one row per element × applicable check
routing.json      every interface: relevant or not, and the routing if relevant
compliance.json   every regulatory hook and what it means for this submittal
prior.json        resubmittals only: what happened to each prior finding
```

`state.yaml` carries `status`. On restart, read it and resume at the step after the last completed one.

---

## Workflow

```
- [ ] 1. Intake               - [ ] 6. Review (fan out per element)
- [ ] 2. Compile knowledge    - [ ] 7. Package checks and reconciliations
- [ ] 3. Checkpoint           - [ ] 8. Compliance and coordination routing
- [ ] 4. Trace requirements   - [ ] 9. Coverage gate
- [ ] 5. Inventory submittal  - [ ] 10. Report
```

### 1. Intake

1. **Mode.** `.construction/project.yaml` present → AgentCM mode; otherwise flat file.
2. **Submittal.** Locate the package file(s). Read the cover or transmittal: submittal number, revision, title, subcontractor, spec section(s), submittal types (use `submittal-log-generator`'s type labels: Shop Drawings, Product Data, Samples, Design Data, Test Reports, Certificates, Delegated Design, ...).
3. **Resubmittal.** If the revision is above zero or the user names a prior review, find the prior review directory. Every prior finding must be accounted for in `prior.json` (Step 7).
4. **Prerequisites.** Spec text must exist in `.construction/skills/spec_text/`. If it does not, run `/construction:spec-splitter`. Drawing sheets must be split and indexed (`sheet_index.yaml`, or AgentCM's index). If not, run `/construction:sheet-splitter`.
5. **Facility types.** Read `building.facility_types` in `.construction/skills/project_context.yaml`. If it is missing, infer candidates from the drawings' cover sheet and code analysis (occupancy, building use) and confirm them at the checkpoint. Use dotted types when known (`healthcare.hospital`, `education.k12`, `laboratory`, `foodservice`). A building can have several.
6. **Register.** Check the submittal log for this item, and the RFI log and ASI/bulletin log for changes affecting the section. Note approved submittals this one depends on, for example the approved sink or fume hood a casework submittal must fit.

Write `state.yaml` (status: `intake`).

### 2. Compile knowledge

```bash
PY="${CLAUDE_PLUGIN_ROOT}/bin/construction-python"; KB="${CLAUDE_PLUGIN_ROOT}/scripts/csi/csi_knowledge.py"
"$PY" "$KB" resolve --section "{section}" --project . --types "{types}" --format yaml --output "{dir}/context.yaml"
"$PY" "$KB" resolve --section "{section}" --project . --types "{types}" --format md --output "{dir}/context.md"
"$PY" "$KB" reflexes --project . --format md --output "{dir}/reflexes.md"
```

Read `context.md`. It tells you:
- `review_mode`: per element (fan out) or per package
- `element_types`: the units of review
- the checks, each with its `scope` (element or package), `trace_to`, `gate` and owner
- reconciliations, failure modes, regulatory hooks with their binding status, and interfaces
- `confidence_floor` and warnings: say "draft knowledge" in the report when the floor is `draft`

If the warnings say the project specifies this scope under an equivalent section, resolve that one too.

**Knowledge, not requirements.** The compiled context says what to verify and where to look. The project documents supply the requirement. If they conflict with the knowledge layer, the documents govern and you note the conflict.

### 3. Checkpoint

Show the user, in one short message:
- the section(s), submittal types, element count estimate and facility types
- the regulatory hooks that are **unbound** and of high or critical severity, by topic

Ask two things: confirm facility types, and whether to run `/construction:code-researcher` on the unbound topics now. Researched hooks become checkable. Unresearched hooks stay **open compliance items** in the report and are never answered from memory.

Write confirmed facility types to `project_context.yaml` (`building.facility_types`) if they were missing. If nobody can answer (unattended run), proceed with the inferred types and leave hooks open, and say so at the top of the report.

### 4. Trace requirements (before reading the submittal)

A review fails most often because the right detail was never pulled. Build `trace.json` from the contract documents alone:

1. **Package requirements.** Every submittal requirement in Part 1 of the section, with its article reference.
2. **Elements.** For `per_element` review, list every element of the scope in the contract documents: each tagged elevation, item, mark, equipment number or assembly in `element_types`. Find them through `trace_to` terms (plans, elevations, details, schedules). In AgentCM mode, query the database for tags and cross-references instead of reading sheets (read `query_command` from `.construction/database.yaml`; views in `.construction/db_schema.yaml`).
3. **CD references per element.** For each element, every sheet, detail, section and schedule row that governs it. Follow every detail or section cut drawn on an elevation or plan. Record the value of each `extract_fields` item the documents state, with its source.
4. **Changes.** Apply responded RFIs, ASIs and bulletins to the trace, citing them.

For `package` review, the trace is the package requirements plus the governing CD references.

### 5. Inventory the submittal

Map the submittal to the trace in `inventory.json`, both ways:
- each trace element → the submittal pages that cover it, or `missing`
- each submittal item with no matching element → `extra_items`
- each Part 1 package requirement → submitted or missing

Keep this pass light: identify pages from titles, tags and headers. Detailed reading happens in Step 6. A missing element or package item becomes a completeness finding.

### 6. Review

Every element-scope check is answered for every submitted element: pass, finding, not applicable (with a reason), or unverifiable (with what is missing).

- **Up to about eight elements:** review them yourself, one element at a time, releasing each element's pages before the next.
- **More:** fan out. Batch about five to eight elements per worker and launch the workers in parallel with the Agent tool, using the prompt in `${CLAUDE_SKILL_DIR}/references/worker-prompt.md`; fill `{plugin_root}` with `${CLAUDE_PLUGIN_ROOT}` and `{skill_dir}` with `${CLAUDE_SKILL_DIR}`. Each worker writes `findings_{NN}.json`, `coverage_{NN}.json` and `values_{NN}.json` to the review directory and returns only a one-line summary. If a batch file is missing, re-run that worker. Never parse results from a worker's reply.

Reviewing an element means reading the CD references in its trace and the submittal pages in its inventory, comparing them check by check, and keeping the reflexes in mind. A finding cites both sides: the requirement (sheet, detail, schedule row, spec article, RFI or ASI) and the submittal (file, page, what it shows). Write findings as described in `${CLAUDE_SKILL_DIR}/references/review-writing.md`.

### 7. Package checks, reconciliations and prior comments

Yourself, in the main context:
- every package-scope check (`element: "package"` in coverage)
- every reconciliation in the context: compare the named documents field by field using the trace and `values_*.json`; a mismatch is a finding with both sources
- **resubmittals:** every prior finding goes into `prior.json` as closed, open or partially closed, with evidence. An unaddressed prior comment is a finding of its own.

### 8. Compliance and coordination routing

**Compliance** (`compliance.json`): one row per regulatory hook.
- `bound` → check the submittal against the cited requirement; a shortfall is a finding citing code, edition and section
- `bound_unconfirmed` → the same, and the finding says *verify with AHJ*
- `unbound` → `result: open`, with the elements it affects and the research command. Never state a code requirement you have not retrieved.

**Routing** (`routing.json`): one row per interface in the context. If the submittal shows content that interface depends on (in-wall supports, utility connections, cutouts for others' products, penetrations, embeds), it is relevant. Write what to send the counterpart trade (pages, items), what is needed back, who to confirm for furnish/install/connect, and the need-by date: the gate milestone mapped to the project schedule where one exists. If it is not relevant, say why in one line. A coordination finding with no routing row is a coverage gap.

Use `milestone --id {gate} --project . --format md` when a gate is near on the schedule; it lists everything else due by then.

### 9. Coverage gate

```bash
"$PY" "${CLAUDE_SKILL_DIR}/scripts/check_coverage.py" --review-dir "{dir}"
```

It fails if any element × check lacks a row, a missing element has no completeness finding, a finding lacks a source or an action, an unbound hook is marked anything but open, an interface or hook has no row, or a prior finding is unaccounted for. Fix every gap and re-run until it passes. Do not report before it passes. If something truly cannot be verified, record it as `unverifiable` with what is missing; that is coverage, and it goes in the report.

### 10. Report

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
3. **Tell the PE**, briefly: suggested disposition and why; the findings, each with its source and its action on the same line (never split a finding from its action); who has to coordinate what, by when; open compliance items, each named as needing code research with the topic to run `/construction:code-researcher` on; anything unverifiable; the confidence floor if it is draft. Then the file paths.
4. Set `status: complete` in `state.yaml`.

### Learning loop

When the PE overturns a finding or a miss surfaces later, append it to `.construction/skills/submittal-review/knowledge_feedback.yaml`: section, what happened, the check that should have caught it (or "none"), and the suggested knowledge-layer change (a failure mode, a check, or a hook, per `reference/csi/SCHEMA.md` §8). Plugin maintainers fold these into the layer; do not edit the plugin's files from a project.

---

## Rules

- The contract documents govern. Precedence and the RFI and submittal authority rules are in `pe-review`'s `references/pe_review_rules.md`.
- Surface conflicts; never resolve them. If the drawings and the spec disagree, that is a design-team finding, not a reason to accept the submittal.
- No fabricated references. Every sheet, detail, article and code citation comes from a document you read or a finding `code-researcher` recorded.
- "By others" is not an answer. Name who, or record a scope gap.
- Approved-as-noted markups and responded RFIs change the trace. Read them.
- Draft only. Disposition is a suggestion; the PE decides and sends.
