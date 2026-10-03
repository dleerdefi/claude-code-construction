# Review Lens

What an expert PE asks of every submittal, beyond comparing it to the drawings. Use your own knowledge of the scope for everything else; this file only lists what reviews most often skip.

## Package questions (answer each once, in `package_review.json`)

| Id | Question |
|---|---|
| `pk.current-documents` | Was it prepared from the current documents, including addenda, ASIs, bulletins and responded RFIs? Which revision did the submitter use? |
| `pk.basis-of-design` | Is each product the basis of design or a listed acceptable manufacturer? Anything else is a substitution, with its own timing and comparison data. |
| `pk.products-marked` | On product data, are the model, size, options, voltage, finish and accessories marked on every cut sheet that covers a product family? |
| `pk.deviations` | Is every deviation from the contract documents clouded or listed? Compare independently; do not rely on the submitter's list. |
| `pk.by-others` | Is every "by others", "NIC", "by GC" or "owner furnished" note mapped to a named party in the contract documents? An unmapped one is a scope gap. |
| `pk.field-verify` | Are "verify in field" dimensions listed with who verifies them and by when? |
| `pk.delegated-design` | Where the contractor designs or selects the system, is the design sealed where required, complete enough to review, and filed as a deferred submittal if the AHJ requires? |
| `pk.lead-time` | Does the stated lead time, with review cycles, support the schedule activity that needs the product? |

Add a row for every cross-document reconciliation you perform (the equipment schedule against the electrical panel schedule; sink models against the casework cutouts; door hardware sets against the door schedule).

## Cross-trade questions (for every element)

These produce the findings a single-trade reviewer misses. Ask them of each element, and route what you find (`routing.json`):

1. **What does this need from another trade before it goes in?** Backing, blocking or in-wall brackets; embeds, sleeves, pits, depressions or recesses in concrete; rough-ins at a location, voltage or size; structure or dunnage; openings, curbs or access.
2. **What does another trade need from this before they close something up?** Weights and reactions, connection sizes and locations, heat or exhaust loads, control points, field-wired devices.
3. **Who furnishes, installs and connects each part?** Read the spec and the drawings; never accept "by others".
4. **What gets covered first?** Name the milestone in `milestones.yaml` by which it must be resolved, and the date from the project schedule when there is one.

## Code and authority questions

A drawing will not tell you whether the jurisdiction requires something. For each element, ask which authorities have a say:
- the accessibility standard (heights, clearances, reach, operating force);
- the health department (food service counters and tray slides, hand sinks, finishes, floor sinks, plan approval);
- fire and life safety (ratings, listings, egress, alarm interfaces);
- energy, seismic and wind (certification, anchorage);
- state agencies for schools and healthcare;
- the serving utility.

Write each one as a full question that names the authority and the elements it affects. Research it with `code-researcher` when you can (Step 7). Never state a code requirement you have not retrieved.
