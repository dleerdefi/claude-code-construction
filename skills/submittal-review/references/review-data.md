# Review Data — File Formats

All files live in `.construction/skills/submittal-review/{review_id}/`. Write them directly as YAML or JSON. `check_coverage.py` and `export_submittal_review.py` read them; a field they need that is missing is reported as a gap, never guessed.

Element ids are the contract-document reference that identifies the element: `1/A-501`, `EQ-14`, `D-142`, `WT-3`. Use the same id everywhere.

## state.yaml

```yaml
review_id: 12-35-53-001-R0
status: intake            # intake | context | trace | inventory | review | package | routing | coverage | report | complete
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
prior_review: null        # review_id of the previous revision, if any
unattended: false         # true when nobody could answer the checkpoint
notes: []                 # assumptions stated at the top of the report
```

## trace.json — from the contract documents only

```json
{
  "package_requirements": [
    {"ref": "12 35 53 1.4.B", "text": "Shop Drawings: elevations, sections, in-wall supports, service fixture locations"}
  ],
  "elements": [
    {
      "id": "3/A-501",
      "type": "casework_elevation",
      "label": "Lab 104 east wall, wall-hung counter",
      "cd_refs": ["A-501 elevation 3", "A-521 detail 5", "Casework schedule type WH-1", "12 35 53 2.4.C"],
      "requirements": {
        "cw.xf.counter-height": {"value": "36", "unit": "in", "source": "3/A-501"},
        "cw.xf.in-wall-supports": {"value": "Concealed steel bracket, backing BLK-2", "source": "5/A-521"}
      },
      "changes": ["ASI-004 revised counter length"]
    }
  ]
}
```

## inventory.json — where each element is in the submittal

```json
{
  "elements": [
    {"id": "3/A-501", "status": "submitted", "pages": [{"file": 0, "page": 4}]},
    {"id": "4/A-501", "status": "missing", "pages": []}
  ],
  "extra_items": [{"label": "Elevation 7 (storage wall)", "pages": [{"file": 0, "page": 6}], "note": "Not in CDs; ask the sub"}],
  "package_items": [{"ref": "12 35 53 1.4.B", "status": "submitted", "pages": [{"file": 0, "page": 2}]}]
}
```

`status`: `submitted` | `partial` | `missing`. Every `missing` element or package item needs a completeness finding.

## values_{NN}.json — what the submittal states, per element

```json
[{"element": "3/A-501", "field": "cw.xf.counter-height", "value": "36", "unit": "in", "file": 0, "page": 4}]
```

## findings_{NN}.json — an array of findings

```json
[
  {
    "id": "F-003",
    "element": "3/A-501",
    "check": "cw.in-wall-support",
    "kind": "constructability",
    "severity": "critical",
    "owner": "gc",
    "grade": "NOT FOUND",
    "finding": "Wall-hung counter shows no support; note reads 'supports by others'.",
    "requirement": {"source": "A-521 detail 5", "text": "Concealed steel bracket by casework mfr, installed by framer before GWB"},
    "submittal": {"file": 0, "page": 4, "text": "Elevation 3 — 'supports by others'"},
    "action": "Show bracket type, spacing, height and load at elevation 3; furnish brackets to framer before close-in.",
    "rfi_candidate": false,
    "markup": {"page": 4, "rect": [420, 300, 620, 380]}
  }
]
```

| Field | Values |
|---|---|
| `id` | `F-` + number, unique in the review. Workers use their batch number: `F-03-01` |
| `element` | an element id, or `package` |
| `check` | a check, reconciliation or hook id from `context.yaml`; `obs.<slug>` for an observation the layer has no check for |
| `kind` | completeness, conformance, coordination, constructability, absence, compliance |
| `severity` | critical, high, medium, low |
| `owner` | subcontractor (sub must fix), gc (GC must act or coordinate), design_team (only the A/E can answer), owner |
| `grade` | CONFLICTING (documents disagree), NOT FOUND (required information absent), OPEN (needs field verification or information not yet available) |
| `requirement.source` | sheet/detail, schedule row, spec article, RFI, ASI or code citation. Required |
| `submittal` | file index, page, what it shows. Required except for absence findings about the CDs |
| `action` | what has to happen, by whom. Required |
| `rfi_candidate` | true when owner is design_team and a written answer is needed |
| `markup` | optional page and rectangle in PDF points for the review cloud |

## coverage_{NN}.json — one row per element × applicable check

```json
[
  {"element": "3/A-501", "check": "cw.counter-heights", "status": "pass", "evidence": ["3/A-501", "sub p4"]},
  {"element": "3/A-501", "check": "cw.in-wall-support", "status": "finding", "finding": "F-003", "evidence": ["5/A-521", "sub p4"]},
  {"element": "3/A-501", "check": "cw.appliance-openings", "status": "na", "note": "No appliances on this elevation"},
  {"element": "package", "check": "rf.rc.drains", "status": "unverifiable", "note": "Plumbing roof plan not in the set"}
]
```

`status`: pass | finding | na | unverifiable. `na` and `unverifiable` need a `note`. `finding` needs a `finding` id.

Which checks: every check in `context.yaml` with `scope: element`, for every element that is `submitted` or `partial`; every check with `scope: package` and every reconciliation, once, as `element: package`.

## routing.json — one row per interface in the context

```json
[
  {
    "interface": "if.casework-backing",
    "relevant": true,
    "reason": "Elevation 3 is wall-hung on in-wall brackets",
    "trade": "Framing",
    "sections": ["09 22 16"],
    "send": "Submittal pages 4-5 and A-521 detail 5",
    "ask": "Confirm bracket backing at elevation 3 heights; install before second-side board",
    "confirm": "Brackets furnished by casework, installed by framer (12 35 53 1.3.D)",
    "gate": "wall_close_in",
    "need_by": "2026-11-02",
    "findings": ["F-003"]
  },
  {"interface": "if.casework-base", "relevant": false, "reason": "Base is by casework per 12 35 53 2.5"}
]
```

## compliance.json — one row per regulatory hook

```json
[
  {"hook": "cw.rh.accessibility-work-surfaces", "topic": "accessibility-work-surfaces", "binding": "unbound",
   "affects": ["2/A-501"], "result": "open",
   "note": "Accessible station submitted at 36 in; requirement not researched. Run /construction:code-researcher on this topic."}
]
```

`result`: open | consistent | finding. An `unbound` hook is always `open`. `finding` needs a `finding` id whose requirement cites the code, edition and section.

## prior.json — resubmittals only

```json
[{"prior_finding": "F-002", "status": "closed", "evidence": "Sheet 3 now shows 34 in at elevation 2"},
 {"prior_finding": "F-005", "status": "open", "finding": "F-011", "evidence": "No change at elevation 4"}]
```

`status`: closed | partially_closed | open. Every finding in the prior review must appear. `open` and `partially_closed` need a new finding id.
