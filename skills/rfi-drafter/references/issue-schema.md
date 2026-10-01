# Issue Schema — Detection Registry Records

## Purpose

The issue registry at `.construction/issues/` accumulates potential
problems found by any skill during its normal work. Issues are NOT
RFIs — they are observations that MAY become RFIs after user review.

## File Convention

Issues are stored as individual JSON files:
```
.construction/issues/
├── ISS-2026-0001.json
├── ISS-2026-0002.json
├── ISS-2026-0003.json
└── ...
```

Issue IDs are sequential within the project. Use `scripts/issue_manager.py`
to create, list, update, and escalate issues.

## Record Schema

```json
{
  "id": "ISS-2026-0001",
  "created_at": "2026-04-05T14:23:00Z",
  "source_skill": "tag-audit-and-takeoff",
  "severity": "warning",
  "confidence": "medium",
  "status": "open",

  "description": "Door D-142 references hardware set 7, which does not appear in spec section 08 71 00",

  "location": {
    "sheets": ["A3.1"],
    "grid": "C-4",
    "rooms": ["142"],
    "details": [],
    "elements": ["D-142"]
  },

  "document_references": {
    "drawing_refs": ["Sheet A3.1, Door D-142 at Grid C-4"],
    "spec_sections": ["08 71 00"],
    "schedule_refs": ["Door Schedule on A0.2"]
  },

  "context": "During door tag audit, found tag referencing HW-7. Searched spec section 08 71 00 for hardware set definitions. Sets 1-6 defined. No set 7 found.",

  "potential_rfi_subject": "Missing Hardware Set 7 Definition for Door D-142",

  "escalated_to_rfi": null,
  "resolved_by": null,
  "resolved_at": null,
  "resolution_notes": null
}
```

## Field Definitions

### severity
How serious the issue is if confirmed:
- **info** — Observation, may not need action. Example: "Room 301
  finish code 'F7' not in finish legend, but appears to be
  standard VCT based on context."
- **warning** — Likely needs clarification but not blocking.
  Example: "Door schedule shows 3'-0" width but plan dimensions
  suggest 2'-8" clear opening."
- **conflict** — Documents contradict each other. Example:
  "Structural plan shows beam at Grid C-4, architectural RCP
  shows recessed light fixture at same location."
- **safety** — Potential life-safety or code compliance issue.
  Example: "Egress corridor width reduced below IBC minimum by
  door swing projection." These always surface to the user
  immediately, even during other skill workflows.

### confidence
How certain the skill is that this is a real issue:
- **high** — Clear contradiction with strong evidence
- **medium** — Likely issue but could be explained by context
  the skill doesn't have (verbal agreement, pending addendum)
- **low** — Possible issue, needs human judgment to determine

### status
- **open** — Detected, not yet reviewed by user
- **reviewed** — User has seen it, decided not to act yet
- **escalated** — User confirmed, RFI is being drafted
- **resolved** — Issue addressed (by RFI, addendum, or user
  determined it's not actually an issue)
- **dismissed** — User reviewed and determined it's not an issue

## Issue Lifecycle

```
Skill detects → writes to registry (status: open)
                    ↓
User reviews queue (status: reviewed)
    ↓                    ↓                ↓
Escalate to RFI    Dismiss            Defer (stays reviewed)
(status: escalated) (status: dismissed) 
    ↓
RFI drafted + exported
(status: resolved, escalated_to_rfi: "RFI-026")
```

## Writing Issues from Skills

Skills should write issues when they encounter:
- Schedule/drawing count mismatches (tag-audit-and-takeoff)
- Spec section references that don't exist (spec-parser)
- Cross-discipline spatial conflicts (pe-review)
- Missing required details or sections (pe-review)
- Code compliance concerns (pe-review, code-researcher)
- Submittal requirements with no matching spec product (submittal-log)

Skills should NOT write issues for:
- Normal variations in drawing conventions
- Items the user is already actively working on
- Cosmetic or formatting inconsistencies
- Things Claude is uncertain about at low confidence
