# Construction Drawing Conventions

## Sheet Numbering

Standard format: `{Discipline Prefix}-{Level/Category}.{Sequence}`

### Discipline Prefixes

| Prefix | Discipline |
|---|---|
| G | General (cover, notes, symbols, abbreviations) |
| H | Hazardous Materials |
| V | Survey / Geotechnical |
| C | Civil / Site |
| L | Landscape |
| S | Structural |
| A | Architectural |
| I | Interiors |
| Q | Equipment |
| F | Fire Protection |
| P | Plumbing |
| D | Process / Piping |
| M | Mechanical / HVAC |
| E | Electrical |
| W | Distributed Energy |
| T | Telecommunications |
| R | Resource (BIM reference) |
| X | Other Disciplines |
| Z | Contractor / Shop Drawings |

### Level/Category Digit

| Digit | Category |
|---|---|
| 0 | General (schedules, notes, diagrams, legends) |
| 1 | Plans — Lowest level (basement, site) |
| 2 | Plans — Ground/first floor |
| 3 | Plans — Upper floors |
| 4 | Elevations (A) / Plans continued (others) |
| 5 | Sections (A) / Plans continued (others) |
| 6-7 | Details and enlarged plans |
| 8 | Sections and details (A) |
| 9 | 3D views, schedules, or details |

Example: `A-2.01` = Architectural, Level 2 (first floor), sheet 01

## Common Symbols

### Section Cut
A line with arrows showing the direction of view. End markers are triangles or circles containing the section number over the sheet number where the section is drawn.

### Detail Callout
A circle (sometimes with a tail/leader) containing the detail number over the sheet number. Example: `5` over `A-5.01` means detail 5 is found on sheet A-5.01.

### Elevation Marker
A triangle or circle with a number pointing in the direction of view. The number references the elevation drawing, and the sheet number appears below.

### Door/Window Tags
Circles or hexagons containing an alphanumeric mark that cross-references a schedule.

### Revision Cloud
An irregular bumpy closed shape enclosing changed content. Accompanied by a delta triangle with the revision number.

### North Arrow
Indicates drawing orientation. Project north may differ from true north.

### Grid Lines / Column Lines
Lettered (A, B, C) in one direction and numbered (1, 2, 3) in the other. These are the primary location reference system.

### Level / Elevation Marks
Triangles or circles at section cuts showing elevation above a datum (usually finish floor).

## Line Types

| Line | Meaning |
|---|---|
| Solid thick | Visible outlines, walls in section |
| Solid thin | Dimensions, leaders, hatching |
| Dashed | Hidden or below-grade elements |
| Dash-dot | Center lines, grid lines |
| Dash-dot-dot | Property lines |
| Dotted | Elements above (shown on plan) |

## Hatching / Fill Patterns

| Pattern | Material |
|---|---|
| Diagonal lines (45°) | Earth/fill (in section) |
| Small dots | Concrete (in section) |
| Brick pattern | Masonry (in section) |
| Diagonal cross-hatch | Steel/metal (in section) |
| Wavy lines | Insulation |
| Wood grain | Wood (in section) |
| No fill (white) | Open space / air |

## Title Block Standard Fields

Every drawing sheet has a title block containing:
- Project name and number
- Sheet number and title
- Scale(s)
- Date
- Drawn by / Checked by initials
- Architect/Engineer firm name and seal
- Revision history (number, date, description)
- Owner name
- Project location (address, city, state)
