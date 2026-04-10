# Grouping Rules — OCR Item Reconciliation

## Core Problem

Google Document AI extracts text at the token/word level. A single
construction tag like "WALK-IN FREEZER" often becomes 3+ separate
extracted items: "WALK", "-", "IN", "FREEZER" — each with its own
bounding box. This document defines how to reassemble them.

## Text Reconstruction

1. Collect all candidate items from the spatial neighborhood query.
2. Sort candidates by y-coordinate (top to bottom), then by
   x-coordinate (left to right) within each line.
3. **Line detection**: Items share a line if their y-center values
   are within a tolerance of the median text height for that cluster.
   Typical tolerance: ±3pt for 10-14pt text, ±5pt for 16-20pt text.
4. Concatenate items on each line with spaces. Concatenate lines
   with a single space (for comparison) or newline (for display).
5. Fuzzy-match the concatenated result against the vision-identified
   tag text. Accept if Levenshtein similarity > 0.80, or if the
   concatenation contains the vision text as a substring.

## Spatial Coherence Checks

Items that belong to the same tag exhibit these properties:

- **Horizontal adjacency**: Gap between consecutive items on the
  same line is typically < 2x the average character width in the
  cluster. Large horizontal gaps usually indicate separate elements.
- **Vertical stacking**: Multi-line tags have consistent line
  spacing. If lines 1-2 are 16pt apart, line 2-3 should be within
  ±4pt of that same spacing. Irregular gaps signal a boundary.
- **Alignment**: Multi-line tag text is typically left-aligned or
  center-aligned. Items that break alignment likely belong to a
  different element.
- **Bounding box containment**: If a containing element exists
  (room tag box, fixture symbol border), all constituents should
  fall within or very near that boundary.

## What to Include vs. Exclude

### Include as constituents (part of the tag text)

- Words that reconstruct the tag name/identifier
- Hyphens, slashes, ampersands connecting tag words
- Parenthetical qualifiers: "(TYP.)", "(N.I.C.)"
- Tag prefixes/suffixes: "EX.", "NEW", "EXIST."

### Include as associated items (metadata, not tag text)

- Room numbers (usually a standalone number near the room name)
- Dimension strings (contain `'-` patterns or `"` for inches)
- Area values (contain "SF" or "SQ FT")
- Finish codes (short alphanumeric codes, often in a different
  text size than the tag name)
- Reference marks (detail bubbles, section marks near the tag)

### Exclude entirely

- Items with x-center > 200pt away from the tag cluster center
- Items clearly belonging to adjacent tags (different spatial
  cluster with its own coherent text)
- Drawing linework artifacts (single characters like "—" or "|"
  that are actually OCR misreads of graphic lines)
- Spec section references that happen to be nearby but belong to
  a general note block

## Handling Common OCR Split Patterns

| Pattern               | Example Items           | Reconstruction       |
|-----------------------|-------------------------|----------------------|
| Word-per-item         | "WALK" "IN" "FREEZER"   | "WALK IN FREEZER"    |
| Hyphen split          | "WALK" "-" "IN"         | "WALK-IN"            |
| Mid-word break        | "FR" "EEZER"            | "FREEZER"            |
| Number merge          | "ROOM103"               | "ROOM 103" or "103"  |
| Slash in designations | "HW" "/" "7"            | "HW/7"               |
| Multi-line stacked    | Line1: "WOMEN'S"        | "WOMEN'S RESTROOM"   |
|                       | Line2: "RESTROOM"       |                      |

## Confidence Scoring

| Condition                                  | Confidence |
|--------------------------------------------|------------|
| Vision text = concatenated text (exact)     | high       |
| Vision text ≈ concatenated (>90% similar)   | high       |
| Vision text ≈ concatenated (80-90% similar) | medium     |
| Vision text partially matches (<80%)        | low        |
| No OCR items match vision text              | flag       |

Low-confidence and flagged items always route to manual review
with the "vision-only detection, no OCR anchor" status.
