---
name: spec-parser
description: Parse construction specification sections to extract product requirements, submittal requirements, manufacturers, and quality assurance criteria. Use when asked about spec requirements, product data, approved manufacturers, or what a spec section says. Triggers on 'spec', 'specification', 'section 08', 'division 07', 'what does the spec require', or CSI section numbers.
argument-hint: "<spec_section_number>"
---

!`mkdir -p ~/.construction-skills/analytics 2>/dev/null; echo "{\"skill\":\"spec-parser\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"repo\":\"$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")\"}" >> ~/.construction-skills/analytics/skill-usage.jsonl 2>/dev/null || true`



# Spec Parser

Extracts structured data from construction specification documents organized by CSI MasterFormat.

## Data Mode Check

**AgentCM?** Read `.construction/specs/{section_number}.yaml` for pre-parsed data.

**No AgentCM?** Parse specs directly from PDF or DOCX files.

## Workflow

```
Parse Progress:
- [ ] Step 1: Locate spec files
- [ ] Step 2: Identify sections and table of contents
- [ ] Step 3: Extract section structure (3-part format)
- [ ] Step 4: Extract key data per section
- [ ] Step 5: Write parsed output
- [ ] Step 6: Write graph entry
```

### Step 1: Locate Spec Files

Check for spec files in:
- Folders named `Specifications`, `Specs`, `Project Manual`
- PDFs with CSI-pattern filenames (e.g., `07 92 00 Joint Sealants.pdf`)
- A single bound project manual PDF

### Step 2: Identify Sections

If a single bound manual, use `pdfplumber` to find the table of contents (usually in the first 5-10 pages). Map section numbers to page ranges.

```python
import pdfplumber
with pdfplumber.open(spec_pdf) as pdf:
    for i, page in enumerate(pdf.pages[:10]):
        text = page.extract_text()
        if "TABLE OF CONTENTS" in text.upper() or "SECTION" in text:
            # Parse TOC entries: "Section 07 92 00 - Joint Sealants........ 07 92 00-1"
            pass
```

### Step 3: Extract 3-Part Section Structure

CSI specs follow a standard 3-part format:
- **Part 1 — General**: Scope, related sections, references, submittals, quality assurance
- **Part 2 — Products**: Manufacturers, materials, fabrication, mixes
- **Part 3 — Execution**: Preparation, installation, field quality control, cleaning

### Step 4: Extract Key Data

For each section, extract:

```yaml
section_number: "08 71 00"
section_title: "Door Hardware"
division: 8
division_name: "Openings"
submittals_required:
  - type: "Product Data"
    description: "Manufacturer's data for each type of hardware"
  - type: "Samples"
    description: "Hardware finish samples"
  - type: "Hardware schedule"
    description: "Complete hardware schedule with sets"
approved_manufacturers:
  - name: "Schlage"
    product_line: "ND Series"
  - name: "Von Duprin"
    product_line: "99 Series"
quality_assurance:
  - "Installer must be factory-authorized"
  - "Fire-rated hardware must be UL listed"
applicable_standards:
  - "ANSI/BHMA A156 Series"
  - "NFPA 80"
warranty: "5 years from substantial completion"
```

### Step 5: Write Output

Save to `.construction/specs/{section_number}.yaml`.

For individual lookups, return the extracted data directly to the user.

### Step 6: Write Graph Entry

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/graph/write_finding.py \
  --type "spec_parsed" \
  --title "Parsed spec section {section_number}" \
  --data '{"section": "08 71 00", "submittals": 3, "manufacturers": 2}'
```

## Resolving Referenced Standards

When a spec section references an external standard (e.g., ASTM C920, AAMA 501):
- WebSearch to verify the standard's full title and current edition
- Note if the spec references an outdated edition
- Flag any standards that have been withdrawn or superseded

## Tips

- Addenda and ASIs modify spec sections — always check for addenda that supersede spec requirements
- "Or equal" language means substitutions are allowed with architect approval
- Proprietary specs name a single manufacturer with no substitutions
- Division 01 (General Requirements) applies to all work — always read it
