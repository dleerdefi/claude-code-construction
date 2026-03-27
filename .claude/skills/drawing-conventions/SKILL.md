---
name: drawing-conventions
description: Construction drawing domain knowledge — sheet numbering, symbols, abbreviations, line types, hatching patterns, and title block conventions. Auto-applied when Claude encounters construction drawings or PDFs. Covers architectural, structural, MEP, civil, and landscape disciplines.
user-invocable: false
---

!`mkdir -p ~/.construction-skills/analytics 2>/dev/null; echo "{\"skill\":\"drawing-conventions\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"repo\":\"$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")\"}" >> ~/.construction-skills/analytics/skill-usage.jsonl 2>/dev/null || true`



# Drawing Conventions

Core domain knowledge for interpreting construction drawings. Auto-applied when working with construction documents.

## Drawing Sheet Anatomy

Every sheet has these zones:
- **Title block** (bottom-right): Project info, sheet number, scale, revision
- **Drawing area** (main body): The actual plans/details
- **Revision block** (right edge or top-right): Revision history with delta symbols
- **Key notes / general notes** (varies): Numbered notes referenced in the drawing
- **Legend** (if present): Symbol definitions specific to this sheet

## Drawing Types and What to Look For

**Floor plans** (A-1.XX, A-2.XX): Room layouts, dimensions, door/window tags, wall types, room names/numbers. Multiple floors indicated by the level digit.

**Elevations** (A-3.XX): Exterior/interior vertical views. Material callouts, floor-to-floor heights, window head/sill heights.

**Sections** (A-4.XX, S-4.XX): Cut-through views showing construction assembly. Wall sections show material layers. Structural sections show framing, connections.

**Details** (A-5.XX through A-9.XX): Enlarged views of specific conditions. Referenced from plans/sections via detail callout bubbles (circle with number/sheet).

**Site plans** (C-1.XX): Property boundaries, grading, utilities, parking. Civil engineering scale (1"=20', etc.).

**Structural** (S-X.XX): Foundation plans, framing plans, connection details. Look for beam/column schedules, rebar callouts, member sizes.

**MEP** (M-X.XX, E-X.XX, P-X.XX): Ductwork, piping, electrical panels/circuits. Often overlaid on architectural backgrounds.

## Reading Symbols

For comprehensive symbol reference, see `${CLAUDE_SKILL_DIR}/../../reference/drawing_conventions.md`.

**Critical symbols to recognize:**
- **Detail callout**: Circle with `detail#` over `sheet#` — points to an enlarged detail
- **Section cut**: Line with arrows showing cut direction, triangle with section#/sheet#
- **Door tag**: Circle or hexagon with door number (cross-ref to door schedule)
- **Window tag**: Similar to door tag, references window schedule
- **Room tag**: Room name and number, sometimes with finish code
- **Revision cloud**: Bumpy outline marking changed areas, with delta triangle
- **North arrow**: Orientation reference on plans
- **Grid lines**: Lettered/numbered structural grid (A, B, C... and 1, 2, 3...)

## Reading Dimensions

- Dimension strings run between witness lines
- Stacked dimensions: overall on outside, intermediate inside
- Units: Architectural = feet-inches (5'-6"), Civil = decimal feet (45.50'), Metric = mm
- Confirm scale before reporting any measurement
- See `${CLAUDE_SKILL_DIR}/../../reference/scale_factors.yaml` for scale conversion

## Schedules on Drawings

Drawings often contain tabular schedules embedded in the sheet:
- **Door schedule**: Door number, size, type, frame, hardware set
- **Window schedule**: Window mark, size, type, glazing
- **Room finish schedule**: Room, floor, base, walls, ceiling finishes
- **Fixture schedule**: Fixture type, manufacturer, model
- **Panel schedule**: Circuit numbers, loads, breaker sizes

To extract these, use the `schedule-extractor` skill.

## Abbreviations

Construction drawings use extensive abbreviations. See `${CLAUDE_SKILL_DIR}/../../reference/common_abbreviations.yaml` for a comprehensive lookup. Common ones: TYP (typical), SIM (similar), NTS (not to scale), UNO (unless noted otherwise), EQ (equal), CLR (clear), NOM (nominal).
