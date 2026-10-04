# Writing the Review

## A finding

One condition per finding. Four parts, in this order:

1. **What the submittal shows**, with file and page.
2. **What governs**, with the exact source: `A-521 detail 5`, `Casework schedule type WH-1`, `12 35 53 2.4.C`, `ASI-004`, or a code citation `code-researcher` recorded, with edition.
3. **Why it matters**, only when not obvious: the failure mode, the trade it hits, the milestone it threatens.
4. **Action**, with who does it: "Revise elevation 2 to the scheduled height and resubmit" (subcontractor); "Route pages 4–5 to the framer; backing before second-side board" (gc); "Confirm intended height; drawings and casework schedule disagree" (design_team).

Good: *Elevation 2 shows the accessible station top at 36 in (sub p3). A-501 elevation 2 and casework schedule type AW-1 call for 34 in. Revise and resubmit.*
Bad: *Counter height may not be compliant.* (No sources, no action, implies a code finding nobody researched.)

Do not soften a conflict into a question, or harden a question into a defect. If the submittal matches the drawings but the drawings look wrong, it is a design-team finding about the drawings, not a submittal defect.

## Severity

| Severity | Meaning |
|---|---|
| critical | Life safety, structural, or concealed work that will be covered before it can be fixed; or a miss that stops fabrication or inspection |
| high | Will cause rework, a failed inspection, or a delay if not fixed before release |
| medium | Must be fixed but has room in the schedule |
| low | Clarity, documentation or minor conformance |

Judge severity for this project: the same miss is critical where the work is about to be covered and medium where it is not.

## Owner

| Owner | Who acts |
|---|---|
| subcontractor | The submitter corrects and resubmits |
| gc | The GC coordinates, routes, schedules or decides a scope split |
| design_team | Only the architect or engineer can answer; becomes an issue for `rfi-drafter` |
| owner | Owner-furnished items, owner standards, owner decisions |

## Suggested disposition

`export_submittal_review.py` computes it from the findings; the PE decides. This is the GC's action before or alongside the design team's review, not the A/E stamp.

| Condition (first match wins) | Suggested GC action |
|---|---|
| A required element or Part 1 item is missing | Return to subcontractor — incomplete; revise and resubmit |
| Any critical or high finding owned by the subcontractor | Return to subcontractor — revise and resubmit |
| Only medium or low subcontractor findings | Forward to design team with GC comments |
| No subcontractor findings | Forward to design team — no GC exceptions |

Then, whatever the action:
- design-team findings → "plus RFI candidates" (logged as issues)
- open high or critical code questions → "code questions open: research before release for fabrication"
- unverifiable items → listed, with what is missing

## The message to the PE

Short. Lead with the suggested disposition and the one or two findings that drive it. Then each finding with its source and action on the same line. Then routing that is time-critical (trade, gate and date). Then code questions: each written as the question, the authority, the elements it affects, and whether it was researched. Then what could not be verified and what is missing. Then the files. No recap of steps.
