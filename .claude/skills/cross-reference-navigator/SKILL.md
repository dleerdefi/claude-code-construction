---
name: cross-reference-navigator
description: Follow detail callouts, section cuts, spec references, and cross-sheet references in construction drawings. Resolves reference chains across sheets and between drawings and specs. Use when asked to follow a detail, find where a reference points, trace a cross-reference, or navigate between related drawings. Triggers on 'detail', 'section cut', 'see sheet', 'refer to', 'cross reference', or 'where does this point'.
---

!`mkdir -p ~/.construction-skills/analytics 2>/dev/null; echo "{\"skill\":\"cross-reference-navigator\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"repo\":\"$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")\"}" >> ~/.construction-skills/analytics/skill-usage.jsonl 2>/dev/null || true`



# Cross-Reference Navigator

Resolves cross-references between construction drawing sheets and between drawings and specifications. Construction documents form a dense web of references — this skill traverses them.

## Data Mode Check

**AgentCM?** Read `.construction/extractions/{sheet}/links.json` for pre-resolved references.

**No AgentCM?** Use vision to identify reference symbols and follow them.

## Reference Types

**Detail callout**: Circle containing `{detail_number}` / `{sheet_number}`. Example: `5/A-5.01` means detail 5 on sheet A-5.01.

**Section cut**: Line with arrows, triangle markers containing `{section_number}` / `{sheet_number}`. Example: `2/A-4.01` means section 2 on sheet A-4.01.

**Elevation marker**: Triangle or circle indicating direction of view, with `{elev_number}` / `{sheet_number}`.

**Spec reference**: Text like "refer to Section 07 92 00" or "per specification section 08 71 00".

**Sheet note**: Text like "SEE SHEET A-2.03 FOR ENLARGED PLAN" or "SEE DETAIL 3/A-5.02".

**Drawing note reference**: "SEE NOTE 5 ON THIS SHEET" or keynote number referencing a keynote legend.

## Workflow

### Single Reference Resolution

1. Identify the reference symbol/text on the source sheet
2. Parse the target: sheet number and detail/section number
3. Look up target sheet in the sheet index
4. Rasterize the target sheet
5. Locate the specific detail/section on the target sheet
6. Present the referenced content to the user

### Finding a Detail on a Target Sheet

Details on a sheet are typically arranged in a grid with detail numbers. To find detail 5 on sheet A-5.01:

1. Rasterize A-5.01 at 150 DPI
2. Use vision: "Find detail number 5 on this sheet. Details are individual enlarged drawings, each with a title and number below them. Report the location."
3. Crop and present at higher DPI

### Batch Reference Resolution

For resolving all references on a sheet:

1. Rasterize the sheet at 200 DPI
2. Vision prompt: "List every cross-reference on this drawing. Include detail callouts (circles with number/sheet), section cuts (lines with arrows and triangles), elevation markers, and any text references to other sheets or spec sections. For each, report: reference type, reference ID, target sheet/section."
3. Resolve each target
4. Build a reference map

### Writing Resolved References to Graph

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/graph/write_finding.py \
  --type "cross_reference_map" \
  --source_sheet "A-2.01" \
  --data '{"references": [{"type": "detail", "id": "5/A-5.01", "resolved": true}]}'
```

## Tips

- Unresolved references (target sheet doesn't exist) are common — flag these as potential missing documents
- Some references use abbreviated sheet numbers (e.g., `5/5.01` omitting the discipline prefix when same discipline)
- Keynote systems reference a master keynote list, not individual details
- Interior elevation markers often appear as numbered triangles around a room — each number is an elevation view on an interior elevations sheet
