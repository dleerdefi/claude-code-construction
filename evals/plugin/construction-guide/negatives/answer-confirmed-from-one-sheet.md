---
grader: answer
expect: FAIL
note: >
  A real answer from this case (2026-10-12, run 2 of the new guide in the A/B) with every grade
  changed from PROBABLE to CONFIRMED. Every value was read from A500 alone, so the strict rubric
  must fail it; a rubric edit that lets it pass has stopped checking that a grade fits the evidence.
---
Door 220 is on the Door Schedule on A500, "Second Floor" row. All values are CONFIRMED: they come straight from the door schedule on A500.

**Direct answer**

| Item | Value | Source | Confidence |
|---|---|---|---|
| Leaf width | 3'-0" | [A500, Door Schedule, Door 220, Panel Leaf – Width] | CONFIRMED |
| Leaf height | 8'-0" | [A500, Door Schedule, Door 220, Panel Leaf – Height] | CONFIRMED |
| Leaf type | F | [A500, Door Schedule, Door 220, Panel Leaf – Type] | CONFIRMED |
| Leaf material | WD (wood) | [A500, Door Schedule, Door 220, Panel Leaf – Material] | CONFIRMED |
| Frame type | 1 | [A500, Door Schedule, Door 220, Door Frame – Type] | CONFIRMED |
| Frame material | HM (hollow metal) | [A500, Door Schedule, Door 220, Door Frame – Material] | CONFIRMED |
| Door/frame fire rating | 20 | [A500, Door Schedule, Door 220, Door/Frame Rating] | CONFIRMED |
| Hardware set | 10 | [A500, Door Schedule, Door 220, Door Hardware] | CONFIRMED |
| Head detail | A11/A510 | [A500, Door Schedule, Door 220, Details – Head] | CONFIRMED |

For reference, the same row gives jamb F11/A510 and threshold/sill L1/A510. Glazing type, STC rating and access control are blank for this door.

**Cross-reference findings**
- I read the row from the text layer and confirmed it against a rendered crop of the schedule. The columns line up.
- The type letters and frame type number have drawings on A500. Panel Type F and Door Frame Type 1 are drawn there (not examined). The notes say "SEE SPECIFICATIONS FOR DOOR HARDWARE SETS."
- A500 shows the rating as "20" with no unit. I'm reading it as minutes, but the sheet doesn't say so.

**Gaps**
- I did not open sheet A510, so I haven't verified that detail 11 (head) exists there.
- I did not check what hardware set 10 contains. That depends on the door hardware spec in `02 - Specifications`, which I didn't open.
- I did not check the addenda log or the revision history. I found no revision history in this workspace, so this is a gap.
- I did not check whether the floor plan tags door 220 the same way.
- A wood leaf in a hollow metal frame with a 20 rating is plausible, but the unit and the rated-leaf requirements should be confirmed against the specs.

**Recommended actions**
- Open A510 to confirm head detail 11, jamb detail 11 and sill detail 1.
- Check hardware set 10 in the hardware spec section.
- Confirm that the rating "20" means 20 minutes and that the wood leaf is a listed 20-minute door.

I logged no issues, because nothing conflicts so far.
