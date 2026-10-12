# AgentCM mode

The rules every skill follows when AgentCM manages the project folder. Written against AgentCM's contract version 1. AgentCM's own `.construction/CLAUDE.md` is the map of the folder; this file adds only what a skill must do with it.

## The mode

- `.construction/project.yaml` present and readable means AgentCM mode; absent means flat-file mode. Decide once, at the skill's first step, and never switch mid-task. Nothing else decides it: `.construction/skills/` exists in every project, AgentCM or not.
- Read `contract_version` in `project.yaml`. If it is missing (AgentCM older than contract 1) or above 1, tell the PE which, and continue.

## Where things are

Follow `.construction/CLAUDE.md`; it is authoritative about this folder. Start at `.construction/INDEX.md`: every sheet (number, title, revision, discipline, how complete its text is, PDF and page, 1-based), every specification section with its text file, the schedules and legends, and how many rooms are known. Never re-do AgentCM's work: no splitting sheets, extracting specification text or rasterizing whole sheets.

**Specification text** is in `.construction/specs/<section>.txt` (`08 71 00` is `08-71-00.txt`; each line starts with its page in the manual), one file per section INDEX.md lists under Specification sections. A manual INDEX.md lists under "Spec manuals not read" (a scan, or no SECTION headings) is the one exception: spec-splitter splits and extracts it, and its sections are read from `.construction/skills/spec_text/`.

## Which source wins

AgentCM's data comes ahead of anything a skill could extract itself; the documents stay above both. Highest first:

1. **The drawing or specification itself**, seen through `crop.sh` or the section's page. Used to check, never as the first stop.
2. **What a person confirmed in AgentCM:** lines marked `accepted`, rows marked `schedule`, accepted zones' tables, confirmed sheet names and vocabularies.
3. **What AgentCM read from the text alone:** lines marked `text` or `pending`, estimated view areas, sheets marked `partial`. Leads to check, not facts.
4. **The skill's own extraction**, only for what AgentCM does not hold (the meaning of a schedule's rows, a symbol count).

## When a file is missing, or a search finds nothing

- A file the contract promises is missing (`sheets/A-501.tsv`, say): AgentCM has not processed it. Tell the PE and stop that part of the work; do not fall back to your own extraction. Sheets listed in `.construction/pending.tsv` are waiting for a refresh: check it before trusting their files.
- A search of `tags.tsv`, `xrefs.tsv` or a `.groups.tsv` that finds nothing proves nothing: they hold only what was accepted or found in the text. Say "not found in AgentCM's index", never "does not exist".

## Looking at a drawing

```bash
sh .construction/crop.sh <sheet> <x> <y> <w> <h>
powershell -File .construction/crop.ps1 <sheet> <x> <y> <w> <h>
```

`<sheet>` is the sheet's number as INDEX.md names it (its file name in `sheets/`); the box is the one the sheet files give, 0 to 1 from the top left of the sheet (a view's heading gives its area, a `.tsv` line its own box). The script prints the PNG's path: read that PNG. A box too large to read sharply is refused (exit 2): crop a smaller one. Never ask for `rasters/`, `graph/export`, `extractions/` or `exports/`: they are not in the contract.

## The database

- Query only through AgentCM's wrappers, one query per call: `sh .construction/query.sh "SELECT ..."` or `powershell -File .construction/query.ps1 "SELECT ..."`.
- From `.construction/database.yaml` read only `project_id` and `api_url`. Never read or use a password or `query_command`: they are not part of the contract.
- Filter every query on this project's `project_id`: one database serves several projects.
- Query the five views (`v_room_profile`, `v_sheet_contents`, `v_schedule_pivot`, `v_cross_references`, `v_open_conflicts`) and, of the tables, only `sheets`, `rooms`, `schedules`, `schedule_rows`, `schedule_cells`, `extracted_items` and `graph_elements`, with the columns your skill's own instructions already query. Anything new goes through a view.

## Writing back

- Never write under `.construction/` outside `.construction/skills/`. AgentCM regenerates its files and leaves alone any file changed since it wrote it, so an edited file goes stale and fixes nothing.
- AgentCM's data changes only through its write endpoints, `{api_url}/projects/{project_id}/...`: `schedules/ingest`, `schedules/reconcile`, `tag-detections/ingest`. Tell the PE what you sent; AgentCM refreshes the files it affects.
- A write names a sheet by its id: the `id` of the entry in `.construction/index/sheet_index.yaml` whose `sheet_number` matches. Never guess it from the number. If that file is missing or its entries have no `id` (an older sheet-splitter wrote a `pages:` list with `filename` and `page_index`), say so and stop.
- A skill's own working data goes in `.construction/skills/<skill>/`.
