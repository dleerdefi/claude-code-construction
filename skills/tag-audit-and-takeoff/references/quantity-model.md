# Quantity Model — Three-Entity Architecture

## Entity Types

### 1. Element Instance (direct detection)

A tag physically detected on a floor plan sheet. Represents one
installed item at a specific building location.

| Field              | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| id                 | uuid    | Unique detection ID                      |
| sheet_id           | string  | Sheet where detected                     |
| tag_type           | string  | CSI-aligned category                     |
| tag_text           | string  | Reconstructed tag text                   |
| constituent_ids    | int[]   | OCR extracted item IDs that form this tag|
| composite_bbox     | object  | Union bbox of all constituents           |
| associated_items   | object  | Room number, dimensions, codes, etc.     |
| view_type          | string  | Always "floor_plan" for instances        |
| status             | enum    | pending_review / approved / rejected     |
| approved_by        | string  | User who approved (null if pending)      |
| approved_at        | datetime| Approval timestamp                       |
| confidence         | string  | high / medium / low                      |
| provenance         | string  | "vision_detected" or "user_added"        |

### 2. Element Type Definition (detail/section/elevation)

A tag detected on a detail, section, elevation, or enlarged plan.
Defines what elements exist within a TYPE of space. Does NOT
represent a single installed item — represents a template that
applies to all locations of that type.

| Field              | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| id                 | uuid    | Unique type definition ID                |
| sheet_id           | string  | Sheet where the detail/section lives     |
| source_detail      | string  | Detail reference (e.g., "3/A5.2")       |
| parent_view_label  | string  | View title (e.g., "TYPICAL TOILET")     |
| tag_type           | string  | CSI-aligned category                     |
| tag_text           | string  | Reconstructed tag text                   |
| constituent_ids    | int[]   | OCR extracted item IDs                   |
| composite_bbox     | object  | Union bbox                               |
| view_type          | string  | detail / section / elevation / enlarged  |
| status             | enum    | pending_review / approved / rejected     |
| elements_in_type   | object[]| All elements defined in this view        |
| confidence         | string  | high / medium / low                      |

### 3. Derived Instance (multiplied from type definition)

Created when a type definition is applied across building locations.
Never directly detected — always inferred from the relationship
between a type definition and floor plan references.

| Field              | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| id                 | uuid    | Unique derived instance ID               |
| type_def_id        | uuid    | Source type definition                   |
| target_room        | string  | Room tag/number where this applies       |
| target_sheet       | string  | Floor plan sheet where room appears      |
| tag_type           | string  | Inherited from type definition           |
| tag_text           | string  | Inherited from type definition           |
| derivation_method  | string  | How the link was established (see below) |
| status             | enum    | pending_review / approved / rejected     |
| deduplicated       | boolean | True if a direct instance already exists |

## Derivation Methods

When resolving type definitions to building locations, three
methods are available (in order of reliability):

1. **callout_reference** — A detail callout bubble on a floor plan
   explicitly references the source detail number. Most reliable.
   Graph query: find callout detections on floor plans whose
   reference text matches the type definition's source_detail.

2. **room_type_match** — Room tags on floor plans match the type
   definition's parent_view_label. E.g., all rooms tagged "TOILET"
   get elements from "TYPICAL TOILET" detail.
   Graph query: find room tag detections whose text matches or
   contains the parent_view_label.

3. **schedule_crossref** — A finish schedule or room schedule
   cross-references the detail. Least common but catches cases
   where neither callouts nor room names make the link obvious.

## Deduplication Rules

Before creating a derived instance, check:

1. Does the target room already have a direct element instance of
   the same tag_type and tag_text (or a close text match)?
2. If yes: mark the derived instance as `deduplicated: true` and
   do NOT add it to the building quantity total.
3. If no: the derived instance counts toward building quantity.

Present all derived instances (including deduplicated) to the user.
The user may override deduplication if the direct instance and the
derived instance actually represent different physical items.

## QTO Aggregation

```
Building Qty = (approved element instances where deduplicated=false)
             + (approved derived instances where deduplicated=false)
```

Every number traces to either:
- "Detected on sheet X at bbox Y, approved by user Z on date W"
- "Derived from type def T applied to room R via method M,
   approved by user Z on date W"
