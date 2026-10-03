# Review Data — File Formats

All files live in `.construction/skills/submittal-review/{review_id}/`. Write them directly as YAML or JSON. `check_review.py` and `export_submittal_review.py` read them. A field they need that is missing is reported as a gap, never guessed.

Element ids are the contract-document reference that identifies the element: `1/A-501`, `EQ-14`, `D-142`, `WT-3`. Use the same id everywhere. `package` means the whole submittal.

## state.yaml

```yaml
review_id: 12-35-53-001-R0
status: intake            # intake | trace | inventory | checkpoint | review | package | routing | gate | report | complete
mode: flat_file           # flat_file | agentcm
submittal:
  number: "12 35 53-001"
  revision: 0
  title: Laboratory casework shop drawings
  subcontractor: Example Casework Co.
  received: 2026-10-01
  files: ["06 - Submittals/12 35 53-001 R0 Lab Casework.pdf"]   # index 0, 1, ... in other files
  types: [Shop Drawings]
sections: ["12 35 53"]
facility_types: [education.k12]
jurisdiction: "Howard County, Maryland"
schedule: null            # path to the extracted project schedule, if any
prior_review: null        # review_id of the previous revision, if any
unattended: false         # true when nobody could answer the checkpoint
notes: []                 # assumptions stated at the top of the report
```

## pages_{N}.json and page_map_{N}.json

Written by `find_pages.py index` and `map` for submittal file N. `element_terms.json` is its input: `[{"id": "EQ-14", "terms": ["EQ-14", "Item 14", "walk-in cooler", "<scheduled model>"]}]`.

## trace.json — from the contract documents only

```json
{
  "package_requirements": [
    {"ref": "12 35 53 1.3.B", "text": "Shop drawings: elevations, sections, in-wall supports, service fixture locations"}
  ],
  "elements": [
    {
      "id": "3/A-501",
      "type": "casework_elevation",
      "label": "Lab 104 east wall, wall-hung counter",
      "cd_refs": ["A-501 elevation 3", "A-521 detail 5", "Casework schedule type WH-1", "12 35 53 2.4.C"],
      "stated": [{"what": "counter height", "value": "36 in", "source": "3/A-501"},
                 {"what": "support", "value": "concealed steel bracket, backing BLK-2", "source": "5/A-521"}],
      "changes": ["ASI-004 revised counter length"]
    }
  ]
}
```

`cd_refs` lists every sheet, detail, section cut, schedule row and spec article that governs the element. Follow every cut drawn on an elevation or plan. The gate requires each one to be accounted for in the element's review record.

## inventory.json — where each element is in the submittal

```json
{
  "elements": [
    {"id": "3/A-501", "status": "submitted", "pages": [{"file": 0, "page": 4}]},
    {"id": "4/A-501", "status": "missing", "pages": []}
  ],
  "extra_items": [{"label": "Item 20 soft serve machine", "pages": [{"file": 0, "page": 334}], "note": "Not in the CDs; ask the sub why it is included"}],
  "package_items": [{"ref": "12 35 53 1.3.B", "status": "submitted", "pages": [{"file": 0, "page": 2}]}]
}
```

`status`: `submitted` | `partial` | `missing`. Every `missing` element or package item needs a completeness finding.

## review_{NN}.json — one record per reviewed element

```json
[
  {
    "element": "3/A-501",
    "refs": [
      {"ref": "A-501 elevation 3", "status": "read"},
      {"ref": "A-521 detail 5", "status": "read"},
      {"ref": "Casework schedule type WH-1", "status": "unavailable", "note": "Casework schedule not in the set"},
      {"ref": "12 35 53 2.4.C", "status": "read"}
    ],
    "pages": [{"file": 0, "page": 4}],
    "findings": ["F-03-01"],
    "unverifiable": [{"what": "Bracket load rating", "missing": "No bracket product data in the package"}],
    "questions": ["Does the adopted accessibility standard govern the height of this counter where it serves a wheelchair space?"]
  }
]
```

`check_review.py --scaffold NN --elements "..."` writes these records from the trace with every ref `todo`. Set each ref to `read` or `unavailable` (with a `note`); a `todo` left behind is a gap. `questions` are code or authority questions the reviewer noticed; the main reviewer carries them into `compliance.json`.

## package_review.json — package questions and reconciliations

```json
[
  {"item": "pk.current-documents", "status": "pass", "note": "Prepared from the conformed set incl. ASI-004"},
  {"item": "pk.by-others", "status": "finding", "finding": "F-005"},
  {"item": "Sink models: casework cutouts vs P-601 fixture schedule", "status": "finding", "finding": "F-002"},
  {"item": "pk.lead-time", "status": "unverifiable", "note": "No schedule in the project files"}
]
```

`check_review.py --scaffold 90 --package` writes the eight `pk.` rows from `review-lens.md` as `todo`. Add a row for every reconciliation. `status`: pass | finding | na | unverifiable. `na` and `unverifiable` need a `note`; `finding` needs a `finding` id.

## findings_{NN}.json — an array of findings

```json
[
  {
    "id": "F-03-01",
    "element": "3/A-501",
    "kind": "constructability",
    "severity": "critical",
    "owner": "gc",
    "grade": "NOT FOUND",
    "finding": "Wall-hung counter shows no support; note reads 'supports by others'.",
    "requirement": {"source": "A-521 detail 5", "text": "Concealed steel bracket by casework mfr, installed by framer before GWB"},
    "submittal": {"file": 0, "page": 4, "text": "Elevation 3 — 'supports by others'"},
    "action": "Show bracket type, spacing, height and load at elevation 3; furnish brackets to the framer before close-in.",
    "rfi_candidate": false,
    "markup": {"page": 4, "rect": [420, 300, 620, 380]}
  }
]
```

| Field | Values |
|---|---|
| `id` | Unique in the review. Workers use their batch number: `F-03-01`; the main reviewer uses `F-90-01` |
| `element` | an element id from the trace, or `package` |
| `kind` | completeness, conformance, coordination, constructability, absence, compliance |
| `severity` | critical, high, medium, low |
| `owner` | subcontractor (sub must fix), gc (GC must act or coordinate), design_team (only the A/E can answer), owner |
| `grade` | CONFLICTING (documents disagree), NOT FOUND (required information absent), OPEN (needs field verification or information not yet available) |
| `requirement.source` | sheet/detail, schedule row, spec article, RFI, ASI, or a code citation `code-researcher` recorded. Required |
| `submittal` | file index and page, and what it shows. Required except for absence and completeness findings |
| `action` | what has to happen, by whom. Required |
| `rfi_candidate` | true when owner is design_team and a written answer is needed |
| `markup` | optional page and rectangle in PDF points for the review cloud |

## routing.json — one row per trade that must act

```json
[
  {
    "trade": "Framing",
    "sections": ["09 22 16"],
    "send": "Submittal pages 4-5 and A-521 detail 5",
    "ask": "Confirm bracket backing at elevation 3 heights; install before second-side board",
    "confirm": "Brackets furnished by casework, installed by framer (12 35 53 1.3.D)",
    "gate": "wall_close_in",
    "need_by": "no schedule",
    "findings": ["F-03-01"]
  }
]
```

`gate` is an id in `milestones.yaml`. `need_by` is an ISO date read from the project schedule (with `schedule_activity` naming the activity), or `no schedule` when the project has none. Every coordination finding must appear in some row's `findings`.

## compliance.json — one row per code or authority question

```json
[
  {"question": "Does the adopted accessibility standard require the student station at elevation 2 to be at a lower work-surface height with knee clearance, and how many stations must be accessible?",
   "authority": "accessibility standard", "affects": ["2/A-501"], "severity": "high",
   "status": "open", "research": "/construction:code-researcher accessibility-work-surfaces"},
  {"question": "...", "authority": "Howard County Health Department", "affects": ["EQ-14"], "severity": "high",
   "status": "researched", "source": ".construction/skills/code-researcher/topics/foodservice-counter-heights.yaml",
   "result": "finding", "finding": "F-90-04"}
]
```

`status`: `open` (not researched) | `researched`. An open row needs the full `question` and a `research` command. A researched row needs `source`, a code-researcher topic file that exists, and `result`: `consistent` or `finding` (with a `finding` id whose requirement cites the code, edition and section). Never mark a question researched from memory.

## prior.json — resubmittals only

```json
[{"prior_finding": "F-002", "status": "closed", "evidence": "Sheet 3 now shows 34 in at elevation 2"},
 {"prior_finding": "F-005", "status": "open", "finding": "F-90-11", "evidence": "No change at elevation 4"}]
```

`status`: closed | partially_closed | open. Every finding in the prior review must appear. `open` and `partially_closed` need a new finding id.
