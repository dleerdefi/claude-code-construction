# Draft GC review: 12 35 53-001 R0, Laboratory Casework Shop Drawings

**Suggested disposition (the PE decides):** Return to subcontractor as incomplete, revise and resubmit.
- One of four CD elevations is not submitted, and there is no plan and no Product Data or Samples.
- The shops deviate from the CDs in four places without clouding any of them.
- Three items need a design-team answer.
- Eight high-severity compliance questions are open.
- The coverage gate passed: 78 of 78 element-by-check rows, 15 findings, 41 rows unverifiable.

**Assumptions to know about:**
- This was an unattended run. I took `education.k12` from `project_context.yaml` and did not run `/construction:code-researcher`, so every regulatory hook stays open.
- The knowledge layer is draft, not PE-reviewed.
- The project has no submittal log, RFI log, ASI or addenda log, or schedule. The CD set is only A-501, A-521 and P-601. There are no lab gas, mechanical or electrical sheets, and casework schedule type AW-1 is referenced but missing.

## Findings

Each line gives the finding, then its owner, governing source and action.

| ID | Sev | Owner | Governing source | Finding → action |
|---|---|---|---|---|
| F-001 | high | Sub | 12 35 53 1.3.B; 4/A-501 | Elevation 4 (FH-1 on acid storage base AB-1) is not submitted. SD-1 says "ALL ELEVATIONS SHOWN", which is wrong. → Sub submits elevation 4 and corrects the note. GC reviews it together with the 11 53 13 hood submittal. |
| F-002 | high | Sub | 2/A-501 (type AW-1); 12 35 53 2.3.A | The accessible station top is 36 in AFF; the CDs say 34 in. → Sub revises to 34 in. GC holds fabrication release. |
| F-003 | **critical** | Sub | 2/A-501 | The accessible station sits over drawer base DB-2, but the CDs require open knee space with no base cabinet. → Sub deletes DB-2 and dimensions the knee space. |
| F-004 | **critical** | Sub | 5/A-521; 3/A-501; 12 35 53 1.2.A | The shops say "SUPPORTS BY OTHERS" and "ATTACHMENT TO WALL BY OTHERS". The CDs make the casework manufacturer furnish the brackets and the framer install them. No bracket, 48 in o.c. spacing, 300 lb capacity or BLK-2 backing is shown. → Sub shows the bracket and backing and delivers brackets to the framer before gypsum board. |
| F-005 | high | Sub | P-601 S-1; 2/A-521; 12 35 53 1.2.B | The sink cutout is for ACME LS-1812 (18x12); P-601 schedules LS-2416 (24x16). → Sub resizes the cutout and confirms SB-1 fits. GC confirms with plumbing that LS-2416 is still the approved sink before tops are cut. |
| F-006 | high | GC | 5/A-521; 12 35 53 1.2.A | The "by others" notes name no party. → GC confirms the framing subcontract includes bracket and backing install, and schedules delivery before close-in. |
| F-007 | high | Sub | 12 35 53 1.3.B | No plan keyed to the CD elevation tags was submitted. → Sub adds a Lab 104 plan. |
| F-008 | medium | Sub | 12 35 53 1.3.A, 1.3.C | Product Data and Samples are not in this package, and no hardware is shown. → Sub confirms when they will be submitted. GC logs them. |
| F-009 | medium | GC | 12 35 53 1.3.B | "Field verify dimensions" is stated, but nothing says which dimensions, who verifies or by when. The elevations carry no dimensions. → GC requires the list, assigns a verifier and completes it before procurement release. |
| F-010 | low | Design team (RFI candidate) | 12 35 53 Parts 2 and 3; 1/A-501 | Toe kick height, finish and base provider are not defined anywhere. → Design team states them. |
| F-011 | medium | Design team (RFI candidate) | P-601 (S-2, EW-1); A-501 | The S-2 hand sink (HS-1512) and EW-1 eyewash appear on no elevation. → Design team confirms their locations and whether they affect the casework. |
| F-012 | high | Design team (RFI candidate) | 12 35 53 1.3.B; A-501 | No service fixtures, shutoffs or devices appear in the set, and furnish, install and connect responsibility is not stated. → Design team identifies the sheets and states the responsibilities. GC holds in-wall rough-in coordination until then. |
| F-013 | high | Sub | Sources cited in F-001 to F-005 | No deviations are clouded or listed. → Sub resubmits with all deviations identified. The review should state that the stamp does not accept unmarked deviations. |
| F-014 | medium | Sub | 2/A-501; 12 35 53 2.2.A | Nothing shows how the open-knee top is supported. → Sub shows the frame, legs or wall rail. |
| F-015 | medium | Sub | 12 35 53 1.3.B; 1/A-501 | The elevations show no dimensions, edges, backsplash, seams, fillers or scribes. → Sub adds them, with no seam at the sink cutout. |

## Coordination routing

No schedule exists, so I could not set need-by dates. The date given is the gate each item depends on.

| Trade (section) | What to send / ask | Gate | Findings |
|---|---|---|---|
| **Framing** (06 10 53, 09 22 16, 05 50 00) | Send elevation 3, Section C, 3/A-501 and 5/A-521. Confirm backing and that brackets and BLK-2 go in before second-side gypsum board. Furnish is by the casework manufacturer and install by the framer. This is the critical one. | `wall_close_in` | F-004, F-006 |
| **Plumbing** (22 40 00) | Confirm the current approved sink (LS-2416) and its template, and the location of S-2. | `in_wall_rough_in` | F-005, F-011 |
| **Eyewash** (22 45 00) | Confirm the location of EW-1 and clearance from casework. | `in_wall_rough_in` | F-011 |
| **Lab gas and plumbing** (22 63 00) | Send service fixture types and locations. Furnish, install and connect are not stated. | `in_wall_rough_in` | F-012 |
| **Electrical** (26 27 26, 26 51 00) | Request device locations and heights at the casework walls. | `in_wall_rough_in` | F-012 |
| **Fume hoods** (11 53 13) | Send elevation 4 when submitted. Request hood dimensions, services and weight, and review both submittals together. | `procurement_release` | F-001 |
| **HVAC** (23 31 00) | AB-1 is "vented to hood exhaust". Confirm the connection is on the mechanical drawings, since none are in the set. | `above_ceiling_close_in` | F-001 |
| **Finishes** (09 60 00, 09 30 00, 09 90 00) | Ask whether finishes run under and behind the casework. | `floor_finish_install` | F-007 |
| **Resilient flooring** (09 65 13) | Base at casework is undefined. | `equipment_set` | F-010 |

Two interfaces are not relevant: temporary conditions for woodwork (the casework is steel with epoxy tops) and counter dispensers (none in the lab).

## Open compliance questions

All nine are unbound and unresearched. Run `/construction:code-researcher` on the topic named after each question.

1. **`accessibility-work-surfaces`:** Do accessible work surfaces, sinks and counters meet the adopted standard for height, knee and toe clearance and reach, and how many must be accessible? It affects elevation 2 (F-002, F-003) and the others.
2. **`seismic-nonstructural-anchorage`:** Does the seismic design category or occupancy require engineered anchorage for tall or heavy casework, including the wall-hung counter? It affects all four elevations.
3. **`laboratory-hazardous-materials-storage`:** What do the adopted fire code and lab standard require for acid storage base AB-1 (construction, labeling, quantity, venting)? It affects elevation 4.
4. **`emergency-eyewash-shower`:** Do the location, travel distance, supply and tempering of EW-1 meet the applicable standard? It affects the package.
5. **`school-construction-agency-review`:** Does a state agency besides the local building department review changes or substitutions for this Baltimore, MD school, including deferred submittals? It affects the package.
6. **`building-risk-category-assignment`:** What risk category applies to this school, and does it change nonstructural anchorage of the casework? It affects the package.
7. **`instructional-lab-emergency-shutoffs`:** Do the adopted fire and fuel gas codes, NFPA 45 or state education rules require emergency gas or power shutoff in Lab 104, and where? It affects all four elevations (F-012).
8. **`childrens-accessibility-dimensions`:** Which children's reach ranges and counter heights apply, and for which ages? The grade group of Lab 104 is unknown. It affects elevations 1 to 3.
9. **`composite-wood-formaldehyde`** (low): Are any composite wood products in the casework certified to the formaldehyde emission standard? Steel casework and epoxy tops are specified, and Product Data is not submitted. It affects the package.

**Unverifiable (41 rows):**
- Elevation 4 rows, because it is not submitted.
- Electrical devices and service fixtures, because those sheets are not in the set.
- Hardware, because Product Data is not submitted.
- `g.current-documents`, because no ASI, addenda or RFI log exists.
- Lead time and the summer window, because there is no schedule.
- Site conditions and the school-agency check, which depend on schedule and jurisdiction information the project lacks.

## Files
- `06 - Submittals/12 35 53-001 R0 - GC Review.xlsx`
- `06 - Submittals/12 35 53-001 R0 - GC Markup.pdf` (20 annotations, author "GC Review (draft)")
- Working data: `.construction/skills/submittal-review/12-35-53-001-R0/`
- I logged F-010, F-011 and F-012 to the issue registry for `rfi-drafter`. No RFI was drafted or sent.