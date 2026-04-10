# Spatial Parameters — Neighborhood Query Tuning

## Padding Values by Tag Type

The spatial neighborhood query around anchor items uses padding to
capture all constituent items and associated metadata. Padding is
applied in all four directions from the anchor item's bounding box.

These are starting values. Tune based on observed results — if
grouping consistently misses items, increase padding. If too many
irrelevant items appear in candidate sets, decrease padding.

| Tag Type              | Pad (pt) | Rationale                          |
|-----------------------|----------|------------------------------------|
| Room name tags        | 100      | Name + number + finish code + dims |
| Room number tags      | 60       | Number + possible name nearby      |
| Door tags             | 70       | Number + frame/hardware refs       |
| Light fixture tags    | 50       | Symbol + designation code          |
| Plumbing fixture tags | 50       | Symbol + designation code          |
| Fire protection tags  | 50       | Symbol + designation code          |
| Electrical device tags| 50       | Symbol + designation code          |
| Equipment tags        | 80       | Tag + name (often multi-line)      |
| Grid bubble tags      | 40       | Single letter/number in circle     |
| View label tags       | 90       | Title + scale + sheet ref          |
| Finish tags           | 60       | Code + description                 |
| General note refs     | 120      | Note number + full text block      |
| Callout tags          | 50       | Detail number + sheet ref, compact symbol|

## Text Search Strategy by Tag Type

For Step 2 (text-anchor search), use the most distinctive word to
minimize false positives. These patterns work for common tag types:

| Tag Type              | Search Strategy                         |
|-----------------------|-----------------------------------------|
| Room names            | Use full room name or most specific word|
|                       | "FREEZER" not "ROOM", "JANITOR" not "CLOSET"|
| Door numbers          | Search for "D-" or door number pattern  |
| Light fixtures        | Search for fixture type code ("A1", "B2")|
| Plumbing fixtures     | Search for fixture designation ("P-1")  |
| Equipment tags        | Search for equipment name or tag number |
| Grid bubbles          | Search for single letter/number in known|
|                       | grid sequence (may need grid index)     |

## Handling Multiple Anchor Hits

When the text search returns multiple items on the same sheet:

1. **Cluster the hits** — Group anchor hits that are within 200pt
   of each other. These likely belong to the same tag (multi-word).
2. **Separate clusters = separate tag locations** — Each spatially
   distinct cluster represents a different instance of the tag.
3. **Run neighborhood query per cluster** — Each cluster gets its
   own candidate set and grouping pass.

## Adaptive Padding

If initial padding returns < 3 items, double the padding and re-query.
This handles cases where OCR items are more spread out than typical,
which occurs on sheets with unusual text spacing or large-format tags.

If initial padding returns > 40 items, reduce padding by 30% and
re-query. Too many candidates degrades grouping accuracy and wastes
tokens.

Target candidate set size: 8-25 items per tag.
