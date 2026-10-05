# RFI Format — Template & Field Guidance

## Template

```
REQUEST FOR INFORMATION

Project:      [Project Name]
Project No:   [Number]
RFI No:       [Next sequential number from RFI log, or "TBD"]
Date:         [Today's date]
From:         [GC Company Name — PE Name]
To:           [Design Professional — Name, Firm]

Subject:      [Clear, specific, < 15 words]

Spec Section: [CSI section number, or "N/A — Drawing-only issue"]
Drawing Ref:  [Sheet number(s), grid location(s), detail references]

DESCRIPTION:
[Clear description of the issue. What the drawings/specs show,
what the conflict or ambiguity is, and why clarification is needed.
Reference specific sheets, details, grid locations, room numbers.]

SUGGESTED RESOLUTION:
[Propose a solution. Frame as suggestion, not directive. Include
the reasoning. Faster response when the A/E can simply confirm.]

IMPACT IF NOT RESOLVED:
[What construction activity is affected. The date by which a
response is needed to avoid schedule impact.]

ATTACHMENTS:
[List marked-up drawings, photos, reference documents. AgentCM
can generate annotated sheet crops showing the conflict area.]
```

## Field-by-Field Guidance

### Subject Line
Specific enough that anyone can understand the issue from the
subject alone. Include the location and nature of the issue.
- GOOD: "Corridor Width at Grid B — Floor Plan and Enlarged Plan Disagree"
- GOOD: "Conflicting Finish Schedules — Room 203 Flooring"
- BAD: "Question about the floor plan"
- BAD: "Dimension issue"

### To (Addressee)
Route to the design professional who OWNS the document containing
the issue. Common routing:
- Architectural drawings/specs → Architect
- Structural drawings/specs → Structural Engineer
- MEP drawings/specs → MEP Engineer (specific discipline)
- Civil/site drawings → Civil Engineer
- Conflict BETWEEN disciplines → Architect (as prime consultant),
  CC the other discipline's engineer

### Drawing References
Always use the full reference format. Never say "the floor plan"
or "the detail."
- Sheet references: "Sheet A-2.01, Grid B-4"
- Detail references: "Detail 3/A-7.02"
- Section references: "Section 2/S-4.01"
- Spec references: "Spec Section 08 71 00, Paragraph 2.01.A"
- Room references: "Room 203 (Classroom)"

If multiple sheets are involved, list each with its specific
grid location or area of concern.

### Description
Structure the description in three parts:
1. **What the documents show** — objective statement of current state
2. **What the conflict/ambiguity is** — why this is a problem
3. **Why clarification is needed** — what decision is blocked

Avoid opinion or blame. State facts. Let the evidence speak.

### Suggested Resolution
Common resolution patterns by issue type:
- **Dimension conflict**: "Dimension appears to be [X] based on
  adjacent dimensions. Please confirm."
- **Cross-discipline conflict**: "Recommend aligning with [discipline]
  drawing [sheet] which shows [condition]."
- **Missing detail**: "Request a [detail type] addressing [condition]."
- **Product conflict**: "Suggest using [product] per manufacturer's
  recommendation for this application."
- **Code conflict**: "Per [code section], [requirement]. Please
  clarify how the design addresses this." Only with a section you
  have read and verified applies to this project; otherwise describe
  the condition and ask the design professional to confirm compliance.

Always frame as a question or suggestion, never a directive.

### Impact Statement
Include three elements:
1. What work is affected
2. When that work is scheduled
3. When a response is needed to avoid delay

Example: "Framing at Grid B is scheduled to begin October 15.
A response is requested by October 1 to allow for material
procurement and layout adjustments."

## Example RFI

The condition below and its sheet, room, door and dimension references are
invented to show the format. It is not a finding on the real drawings. The
example deliberately contains no code citation: an RFI states what the
documents show and asks the design professional to resolve it. Cite a code
section only when you have read that section and verified it applies.

```
REQUEST FOR INFORMATION

Project:      Sanibel Fire and Rescue Station 172
Project No:   2023820
RFI No:       RFI-026
Date:         September 18, 2025
From:         Example Builders, Inc. — David Chen, PE
To:           Schenkel Shultz Architecture — Project Architect

Subject:      Corridor Width at Grid B — Floor Plan and Enlarged Plan
              Dimensions Disagree

Spec Section: N/A — Drawing-only issue
Drawing Ref:  Sheet A-2.01 (First Floor Plan), Grid Line B between
              Rooms 104 and 105; Enlarged Plan 2/A-2.11; Door tag 105A

DESCRIPTION:
Sheet A-2.01 dimensions the corridor (Room 104) at 3'-8" clear
between the face of stud at Grid B and the Room 105 (Office) wall.
Enlarged Plan 2/A-2.11 dimensions the same corridor at 4'-0" clear.
The dimension string on 2/A-2.11 closes to the Grid B to Grid C
spacing shown on Sheet A-2.01; the 3'-8" string on A-2.01 does not.
Door 105A (3'-0" wide per the door schedule, Sheet A-6.01) swings
into this corridor. The two sheets cannot both be built, and the
corridor wall location sets the layout for the adjacent office
walls.

SUGGESTED RESOLUTION:
The 4'-0" clear dimension on 2/A-2.11 appears to govern, since its
dimension string closes to the grid spacing. Please confirm 4'-0"
clear and issue a corrected dimension on Sheet A-2.01, or advise if
the office wall is to shift instead.

IMPACT IF NOT RESOLVED:
Interior framing at Grid B is scheduled for October 15, 2025. A
response is requested by October 1, 2025 to avoid impact to the
framing and drywall schedule.

ATTACHMENTS:
1. Annotated crop of Sheet A-2.01 at Grid B showing the 3'-8" string
2. Annotated crop of Enlarged Plan 2/A-2.11 showing the 4'-0" string
3. Door schedule excerpt for door 105A
```
