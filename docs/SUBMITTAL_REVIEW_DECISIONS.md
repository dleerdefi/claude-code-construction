# Submittal Review: Decisions

How the `submittal-review` skill came to be built the way it is, what was tried and dropped, what was measured, and what comes next. Last updated 2026-10-04.

## The goal

Expert submittal reviews for any CSI scope, not surface-level checks. The output should be actionable: findings with sources, which subcontractors and trades must coordinate and by when, which rules and authorities (a state or county health department, for example) must be checked, and that checking actually done. The real misses that motivated it:
- casework shop drawings not checked against every detail and elevation;
- a health-department counter-height requirement nobody checked;
- in-wall backing and brackets not coordinated with framing, plumbing and electrical;
- huge foodservice equipment brochures that were never reviewed properly.

## What was tried first

1. **A review of `reference/pe_expertise/`**, the archived scope files (`docs/PE_EXPERTISE_REVIEW.md` on commit `265bdef`). It graded the archive, found several claims that were wrong (firestop sequencing among them), and planned to migrate the useful parts into a structured layer.
2. **A CSI knowledge layer** (`reference/csi/`, never merged). It held 293 YAML files across Divisions 01–14, 21–23, 26–28 and 31–33 plus 15 facility overlays, and `scripts/csi/csi_knowledge.py` compiled them per spec section.
   - **Contents:** checks, reconciliations, failure modes, code questions, interface edges between trades, and milestone gates.
   - **How it was built:** fourteen parallel authors drafted it, an integration pass connected the divisions, and seven reviewers reviewed it. The reviewers came from the same pipeline, so they were not independent.
   - **Where it went:** PR #3, later split into #5–#13.
3. **A first `submittal-review` skill** that compiled that layer for every review, with a one-row-per-element-per-check coverage ledger.

## What the audit measured

`docs/AUDIT_CSI_LAYER.md` reports a read-and-test audit of that work.
- **Mostly restatement.** Classified against what Claude writes closed-book for 12 sections, the compiled knowledge was 94% restatement or noise, 5% new and review-changing, and under 1% wrong. The wrong items were correct facts delivered to the wrong section by inheritance or overlays.
- **No better at finding defects.** In blind ablation on three realistic submittals, reviews run without the layer caught the same planted defects with less noise, and the blind scorer preferred them all three times.
- **The eval didn't test the layer.** The shipped eval passed 9 of 9 with the layer emptied.
- **Busywork and bugs.** The coverage ledger was busywork at scale, and its script counted unfilled rows as covered.
- **Goals left unmet.** It solved none of: health-department validation, large brochures, or need-by dates.
- **The value was in the procedure.** Trace the contract documents first, inventory both ways, cite both sides, keep code questions open, route to trades.

The classification tables in `docs/audit/csi-layer/marginal-value/classification/` list every item with its verdict. The roughly 60 items that changed a review are mostly cross-trade handoffs a single-trade reviewer doesn't think of (freezer underfloor heat, sprinklers inside walk-ins, return air through rated walls) and code questions phrased as questions.

## The decision

- **Do not merge the knowledge layer.** PRs #3 and #5–#13 are closed. The layer is kept on branches as a source to draw from (see the end of this file).
- **Rebuild the skill without it** (PR #14):
  - **Short lens instead of the layer.** A short review lens (`skills/submittal-review/references/review-lens.md`) holds the package questions, cross-trade questions and code-question guidance. Claude's own trade knowledge supplies the rest.
  - **Per-element records instead of the ledger.** Every governing reference must be marked read, or unavailable with a reason, before the review can report.
  - **The audit's gate-script bugs are fixed.** A code question can only be marked researched if it cites a real `code-researcher` result.
  - **A page finder for large PDFs** (`scripts/pdf/find_pages.py`).
  - **Evals that include a no-plugin arm**, with results committed (`docs/evals/`).
- **Knowledge comes back only with proof.** An item returns only with an eval case that passes with it and fails without it.

## What the rebuilt skill measured

Two cases, two runs each with the plugin and with no plugin at all, judged by sonnet (`docs/evals/submittal-review-2026-10-03.json`):

| Case | With the skill | No plugin |
|---|---|---|
| Lab casework, 4 planted defects | 1.00 both runs; ~3 min, ~$0.70 | 0.78 both runs; all 4 defects found; ~1 min, ~$0.25 |
| Foodservice, 366 pages, 4 defects (two on pages 15 and 206) | 1.00 both runs; ~4.5 min, ~$1.30 | 0.67 and 0.78; all 4 defects found; ~1.5 min, ~$0.45 |

On these fixtures the skill finds no more defects than Claude with no plugin. What it adds:
- the deliverables a PE sends: an Excel review and a marked-up PDF;
- proof that every governing reference was read;
- per-trade routing with gates;
- consistent dispositions;
- code questions kept open.

The price is about 3× the time and cost. Both fixtures are too easy: their defects are text mismatches any text search finds.

## Lessons

- **Measure value before scaling.** A with-and-without comparison after the first division would have stopped the layer at 10 files instead of 293.
- **Independent review means a different reviewer.** Reviewers from the same pipeline, using the same model and the same instructions, mostly confirmed the work.
- **Count findings, not items.** Files, divisions and item counts measured effort, not value.
- **An eval without a baseline arm proves nothing about the skill.** A case should only pass if the thing under test is doing work.

## Next steps, in order

1. **A harder eval fixture** that a careful PE catches and a text search does not. It should include a condition drawn on a drawing rather than written, a defect on a scanned page, a chain from spec to schedule to detail, many elements, and resubmittal closure. This decides whether the procedure beats plain Claude at finding defects, or only at deliverables.
2. **Unattended code research**, so health-department and accessibility questions get researched and checked, not left open, when nobody is there to approve it.
3. **Need-by dates from the construction schedule**, not milestone names.
4. **Knowledge deltas from the audit's list**, each with an eval case that fails without it.
5. **A real past project with known misses**, reviewed and compared with what actually went wrong.

## Where everything is

| What | Where |
|---|---|
| Rebuilt skill, page finder, evals, results | PR #14, branch `feat/submittal-review` |
| Knowledge layer, first skill, full audit evidence, `PE_EXPERTISE_REVIEW.md` | branch `feat/csi-knowledge-layer`, commit `265bdef` |
| The layer split by division group | branches `csi/1-framework` … `csi/9-submittal-review` (closed PRs #5–#13) |
| Notes from the seven division reviewers | the bodies of closed PRs #6–#12 |
| The original single PR | closed PR #3 |
