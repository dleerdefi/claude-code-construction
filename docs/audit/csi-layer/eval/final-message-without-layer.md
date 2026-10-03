I've drafted the GC review for 12 35 53-001 R0. The coverage gate passes. My suggested disposition is **Return to subcontractor — incomplete; revise and resubmit.** The export lists three required items not submitted and one RFI candidate for the design team. Three checks could not be verified. You decide the disposition and send the review.

Unattended run: I used facility type `education.k12` from `project_context.yaml` and did not run code-researcher. The knowledge layer is draft, global checks only. It has no 12 35 53 profile, so it supplied no regulatory hooks or interfaces. The project also has no submittal log, RFI log, ASI/bulletin log or schedule.

## Findings
Source is the requirement that governs, followed by where the submittal conflicts with it.

| ID | Severity | Owner | Governing source and finding |
|---|---|---|---|
| F-03 | critical | subcontractor | 3/A-501, 5/A-521 and 12 35 53 1.2.A say casework furnishes the brackets (48 in o.c. max, BLK-2 backing, 300 lb). SD-1 elevation 3 says "supports by others" and SD-2 Section C says "attachment to wall by others". |
| F-05 | critical | subcontractor | 2/A-501 and 12 35 53 2.3.A call for the accessible station at 34 in AFF with open knee space and no base cabinet. SD-1 elevation 2 shows 36 in AFF over drawer base DB-2. |
| F-01 | high | subcontractor | 12 35 53 1.3.B requires every elevation. Elevation 4 (4/A-501, acid storage base AB-1 under fume hood FH-1) is missing, while SD-1 says "all elevations shown". |
| F-02 | high | subcontractor | 12 35 53 1.3.B requires keyed plans and service fixture locations. The package has only elevations and sections. |
| F-06 | high | subcontractor | P-601 schedules sink S-1 as ACME LS-2416 (24x16), and 12 35 53 1.2.B says to size cutouts to the scheduled sink. SD-1 elevation 1 and SD-2 Section A cut for LS-1812 (18x12). |
| F-04 | high | gc | 12 35 53 1.2.A and 5/A-521 put bracket furnishing with casework and installation with the framer. The submittal's "by others" notes are not tied to anyone, and the framer's scope is unconfirmed. |
| F-07 | medium | design_team | 2/A-501 cites "Casework Schedule Type AW-1", which is not in the drawing set. It is an RFI candidate and I logged it in the issue registry. |
| F-08 | medium | gc | The check g.field-verify (knowledge layer) expects field-verify dimensions to name who verifies and by when. The transmittal and SD-1 say "field verify dimensions" with no list, owner or milestone. |
| F-09 | medium | subcontractor | The check g.deviations-identified (knowledge layer) expects the sub to cloud or list deviations. None are listed, though F-03, F-05 and F-06 are all departures from the CDs. |
| F-10 | low | gc | 12 35 53 1.3.A and 1.3.C require Product Data and Samples. They are not in this Shop Drawings package. |

## Suggested GC action
- **Return to the sub:** the sub corrects F-01, F-02, F-03, F-05 and F-06, lists deviations (F-09) and field-verify items (F-08), and resubmits.
- **GC to do:**
  - Settle bracket and backing scope in both subcontracts (F-04).
  - Check the approved 22 40 00 sink submittal and give the sub the sink template (F-06).
  - Track Product Data and Samples separately (F-10).
- **Design team:** send F-07 to rfi-drafter for an RFI.

## Coordination routing
Need-by dates are TBD because there is no schedule.

- **Framing contractor (F-03, F-04):** send A-501 elevation 3, A-521 detail 5 and the corrected elevation 3 / Section C pages. Ask them to confirm BLK-2 backing and bracket installation, and bracket locations and heights. Brackets are installed before second-side gypsum board on the Lab 104 east wall (gate: wall close-in).
- **Plumbing, 22 40 00 (F-06):** send the SD-1 elevation 1 and SD-2 Section A pages. Ask them to confirm the sink model and furnish the manufacturer template before casework fabrication release.
- **Fume hood supplier, 11 53 13 (F-01):** send A-501 elevation 4 and the revised elevation 4 once added. Ask them to confirm AB-1 venting and FH-1 fit before fabrication release.

## Open compliance questions
- **Accessible work surface:** what work surface height, knee clearance and reach requirements apply to the accessible student station in a K-12 lab in Baltimore, MD? It affects 2/A-501 and F-05. The CD says 34 in. Run `/construction:code-researcher` on `accessibility-work-surfaces`. The knowledge layer compiled no hooks for this section, so I added this question myself.

## Unverifiable
- **g.current-documents:** the submittal does not state the drawing revision it used, and there are no ASI or RFI logs to check against.
- **g.basis-of-design:** the spec names no manufacturer, and no product data was submitted.
- **g.lead-time:** there is no schedule and the sub states no lead time.

## Files
- `06 - Submittals/12 35 53-001 R0 - GC Review.xlsx`
- `06 - Submittals/12 35 53-001 R0 - GC Markup.pdf` (17 annotations)
- `.construction/skills/submittal-review/12-35-53-001-R0/`