---
name: submittal-log-generator
description: Extract all submittal requirements from every specification section and generate a comprehensive submittal register in Excel. Runs as a long-running process that systematically parses each spec section. Works with AgentCM structured data, Anthropic PDF support, or pdfplumber fallback. Use when asked to create a submittal log, find what submittals are required, build a submittal register, or extract submittal items from specs. Triggers on 'submittal log', 'submittal register', 'what submittals are required', 'submittal schedule', 'submittals from specs', or 'extract submittals'.
disable-model-invocation: true
argument-hint: "[spec_range: all|div_08|div_09]"
---

!`mkdir -p ~/.construction-skills/analytics 2>/dev/null; echo "{\"skill\":\"submittal-log-generator\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"repo\":\"$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")\"}" >> ~/.construction-skills/analytics/skill-usage.jsonl 2>/dev/null || true`



# Submittal Log Generator

Long-running skill that processes every specification section to extract submittal requirements and produces a professional submittal register in Excel. Designed to handle full project manuals (200+ spec sections) with state persistence.

## Current Submittal State
!`cat .construction/submittal_extraction_state.yaml 2>/dev/null || echo "No prior extraction — starting fresh"`

## Data Mode Selection

Check data sources in this order:

### Mode 1: AgentCM Graph (fastest)
If `.construction/specs/` directory exists with parsed YAML files:
```python
import os, yaml, glob
specs_dir = os.path.join(os.getcwd(), ".construction", "specs")
if os.path.isdir(specs_dir):
    parsed_specs = glob.glob(os.path.join(specs_dir, "*.yaml"))
    # Read submittal data directly from parsed YAML
```
Skip to Step 3 (each YAML already has `submittals_required` extracted).

### Mode 2: PDF with Text Layer (preferred for raw specs)
Use `pdfplumber` to extract text from spec PDFs. This works well when specs have a searchable text layer (most architect-issued specs do).

```python
import pdfplumber
with pdfplumber.open(spec_pdf) as pdf:
    text = pdf.pages[0].extract_text()
    if text and len(text.strip()) > 50:
        mode = "pdfplumber"
```

### Mode 3: Vision on Scanned Specs (fallback)
If pdfplumber returns empty or garbled text (scanned document), fall back to vision:
```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py spec.pdf {page} --dpi 200 --output spec_page.png
```
Then use vision to read the page content.

## Workflow

```
Submittal Log Progress:
- [ ] Step 1: Inventory all spec sections
- [ ] Step 2: Initialize state file
- [ ] Step 3: Process loop (per section)
-     [ ] 3a: Extract section text
-     [ ] 3b: Locate submittal paragraphs
-     [ ] 3c: Parse individual submittal items
-     [ ] 3d: Classify and enrich each item
-     [ ] 3e: Write section results to state
-     [ ] 3f: Compact — release section text from context
- [ ] Step 4: Check addenda for modifications
- [ ] Step 5: Assign responsible parties
- [ ] Step 6: Generate Excel register
- [ ] Step 7: Write graph entry
```

### Step 1: Inventory All Spec Sections

**Single bound project manual** (one large PDF):
1. Extract table of contents (usually pages 2-5)
2. Parse TOC to build section-to-page mapping
3. Use pdfplumber on TOC pages to find lines matching: `SECTION {DD} {DD} {DD} - {TITLE}....{PAGE}`

```python
import re
toc_pattern = re.compile(
    r'(?:SECTION\s+)?(\d{2})\s*(\d{2})\s*(\d{2})\s*[-–—]\s*(.+?)\.{2,}\s*(\S+)',
    re.IGNORECASE
)
```

**Individual spec section files** (separate PDFs per section):
1. List all PDFs in the spec folder
2. Classify by filename pattern (e.g., `07 92 00 Joint Sealants.pdf`)
3. Sort by CSI section number

Build the section queue:
```yaml
sections:
  - number: "01 33 00"
    title: "Submittal Procedures"
    source: "Project_Manual.pdf"
    page_start: 45
    page_end: 52
  - number: "03 30 00"
    title: "Cast-in-Place Concrete"
    source: "Project_Manual.pdf"
    page_start: 78
    page_end: 94
```

### Step 2: Initialize State File

```yaml
# .construction/submittal_extraction_state.yaml
run_id: "uuid"
started: "ISO-8601"
status: "in_progress"
total_sections: 48
processed: 0
current_section: null
queue_remaining: ["03 30 00", "04 20 00", ...]
submittals_found: 0
errors: []
```

### Step 3: Process Loop (Per Section)

#### 3a: Extract Section Text

**pdfplumber mode:**
```python
def extract_section_text(pdf_path, page_start, page_end):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for i in range(page_start - 1, min(page_end, len(pdf.pages))):
            page_text = pdf.pages[i].extract_text()
            if page_text:
                text += page_text + "\n"
    return text
```

**Vision mode**: Rasterize each page, use vision to read the text, concatenate.

#### 3b: Locate Submittal Paragraphs

Submittal requirements live in Part 1, under headings like:
- `SUBMITTALS`
- `ACTION SUBMITTALS`
- `INFORMATIONAL SUBMITTALS`
- `CLOSEOUT SUBMITTALS`

```python
submittal_section_patterns = [
    re.compile(r'(?:1\.\d+\s+)?(?:ACTION\s+)?SUBMITTALS', re.IGNORECASE),
    re.compile(r'(?:1\.\d+\s+)?INFORMATIONAL\s+SUBMITTALS', re.IGNORECASE),
    re.compile(r'(?:1\.\d+\s+)?CLOSEOUT\s+SUBMITTALS', re.IGNORECASE),
]
```

If pdfplumber text extraction is unreliable for a section, use vision:
"Read this specification page. Extract only the submittal requirements. For each submittal item, provide: the paragraph reference (e.g., A.1), the submittal type (Product Data, Shop Drawings, Samples, etc.), and a description of what must be submitted."

#### 3c: Parse Individual Submittal Items

Each submittal requirement is typically a lettered paragraph:

```
A. Product Data: For each type of door hardware indicated. Include
   construction details, material descriptions, dimensions...
B. Shop Drawings: For door hardware schedule, prepared by or under
   the supervision of supplier's Architectural Hardware Consultant...
C. Samples: For each exposed finish required...
```

Parse into structured items:

```python
def parse_submittal_items(submittal_text, section_number, section_title):
    items = []
    item_pattern = re.compile(
        r'([A-Z]|\d+)\.\s+(.*?)(?=(?:[A-Z]|\d+)\.\s|\Z)',
        re.DOTALL
    )
    for match in item_pattern.finditer(submittal_text):
        letter = match.group(1)
        description = match.group(2).strip()
        item_type = classify_submittal_type(description)
        items.append({
            "spec_section": section_number,
            "section_title": section_title,
            "spec_paragraph": f"1.5.{letter}",
            "description": clean_description(description),
            "type": item_type,
            "action": classify_action_vs_informational(description),
        })
    return items
```

#### 3d: Classify and Enrich

**Submittal type classification:**

```python
TYPE_PATTERNS = {
    "Product Data": [r"product\s+data", r"manufacturer.s\s+data", r"cut\s+sheets?"],
    "Shop Drawings": [r"shop\s+drawings?", r"fabrication\s+drawings?"],
    "Samples": [r"samples?", r"color\s+samples?", r"material\s+samples?"],
    "Certificates": [r"certificates?", r"certification", r"installer\s+qualif"],
    "Test Reports": [r"test\s+reports?", r"lab\s+reports?", r"field\s+test"],
    "Warranties": [r"warrant", r"guarantee"],
    "O&M Manuals": [r"operation\s+and\s+maintenance", r"o\s*&\s*m\s+manual"],
    "LEED": [r"leed", r"sustainability", r"recycled\s+content"],
    "Closeout": [r"closeout", r"as-built", r"record\s+drawings?"],
    "Delegated Design": [r"delegated\s+design", r"engineering\s+calculations?"],
}
```

**Division-to-responsible-party mapping**: see `${CLAUDE_SKILL_DIR}/../../reference/csi_masterformat.yaml` for `typical_subs`.

#### 3e: Write Section Results to State

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/graph/write_finding.py \
  --type "submittal_section_parsed" \
  --title "Submittals from section {number}" \
  --data '{"section": "08 71 00", "items_found": 5}'
```

Append items to accumulator file: `.construction/submittal_extraction_items.json`

#### 3f: Compact

Release the section text from context. Only carry forward:
- State file path
- Running item count
- Next section in queue

### Step 4: Check Addenda

After processing all base spec sections:

1. Find addenda files in the project
2. Search for references to spec sections already processed
3. If an addendum modifies a submittal requirement, update or add items
4. Mark modified items with `modified_by_addendum: "Addendum 3"`

### Step 5: Assign Responsible Parties

Map divisions to typical subcontractors from `${CLAUDE_SKILL_DIR}/../../reference/csi_masterformat.yaml`. If user provides actual sub assignments, use those instead.

### Step 6: Generate Excel Register

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/excel/submittal_log_to_xlsx.py \
  --data .construction/submittal_extraction_items.json \
  --project "Dover High School" \
  --output "Submittal_Register.xlsx"
```

Excel output:
- **Register tab**: All submittals with auto-numbered IDs ({Div}-{Seq})
- **Summary tab**: Count by division, type, and responsible party
- **Tracking columns**: Required Date, Submitted Date, Status, Approved Date (blank)
- **Priority column**: Pre-populated for typical critical-path items (steel, long-lead equipment, curtain wall)

### Step 7: Write Graph Entry

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/graph/write_finding.py \
  --type "submittal_log_generated" \
  --title "Submittal register: {N} items from {M} spec sections" \
  --output-file "Submittal_Register.xlsx" \
  --data '{"total_submittals": 142, "sections_parsed": 48, "by_type": {"Product Data": 55, "Shop Drawings": 30}}'
```

## Resumption

Check for `.construction/submittal_extraction_state.yaml`. If `status: in_progress`, resume from `queue_remaining`.

## Performance

| Spec Size | Est. Duration | Notes |
|---|---|---|
| 20 sections | 5-10 min | Small renovation |
| 50 sections | 15-25 min | Typical commercial |
| 100+ sections | 30-60 min | Large institutional |

pdfplumber mode is 3-5x faster than vision mode.

## Quality Validation and Review

After generating the register, perform a review pass before presenting to the engineer:

### Text Quality
Scan all descriptions for spacing artifacts (words broken mid-word, missing spaces between words). These are PDF text extraction issues. Fix them in-place and note the correction in the REVIEW_NOTES column.

### Content Review
Read each item and assess whether it describes an **actual deliverable** or a **procedural instruction**:
- **Keep**: Product data, shop drawings, samples, test reports, certificates, warranties, LEED documentation, O&M manuals — these are real submittal items
- **Flag for review**: Cross-references to other sections ("See Section 01 30 00..."), descriptions of the submittal process itself, general administrative language — add to REVIEW_NOTES: "Appears to be a procedural reference — recommend removal"

### Present Findings
Tell the engineer: "I generated a submittal register with [N] items. [X] items have text quality issues I've corrected. [Y] items appear to be procedural references rather than submittal requirements — these are flagged in the REVIEW_NOTES column. Would you like to review the flagged items?"

The engineer makes the final decision on what to keep or remove.

### Sanity Checks
- Div 08: Hardware schedule submittal (almost always required)
- Div 09: Color/material samples
- Div 23: HVAC equipment submittals and TAB report
- Div 26: Panel schedules and lighting cut sheets
- Total count sanity: 3-6 submittals per spec section is typical

### File Safety
Never overwrite an existing submittal register. If a file already exists at the target location, save with a versioned name (e.g., `Submittal_Register_v2.xlsx`).
