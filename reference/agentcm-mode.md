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

## Which file answers what

Skills read AgentCM's files, never its database. A skill that only reads works the same with AgentCM closed.

- **Orientation** (how many sheets, sections, schedules, rooms): INDEX.md's headings, found by name, never by position: Drawing sheets (N), Specification sections (N), Schedules and legends (N), and the line "Rooms known".
- **A sheet's contents:** `sheets/<sheet>.tsv` (every line of text with its box, view and zone; `how` says accepted or pending), `sheets/<sheet>.txt` (the paragraphs under `## view` headings), `sheets/<sheet>.groups.tsv` (the accepted callouts and tags).
- **Rooms, doors and other identifiers:** `tags.tsv`, by `id` and `kind` (the lines starting with `101` and a tab are room 101 wherever it occurs). INDEX.md says when its room list is incomplete; then search the sheet files.
- **References** between sheets, details and specification sections: `xrefs.tsv` (what refers to A-101: the lines with a tab, `A-101` and a tab).
- **Schedules, legends and keyed notes:** INDEX.md's Schedules and legends table, then the table's own `schedules/<sheet>-<n>.tsv`. Its comment line gives the table's box on the sheet and, for a schedule ingested into AgentCM, `schedule_id=<id>` (`schedule_id=none` for a table read from the text alone).
- **Specification text:** `specs/<section>.txt` (above).

From `.construction/database.yaml` read only `project_id` and `api_url`; nothing else in it is a skill's to use. AgentCM's API is read in three places only: tag-audit-and-takeoff's `GET {api_url}/projects/{project_id}/sheets/{sheet_id}/claimed-elements` and `.../group-review/available-types` before it writes, and schedule-extractor's `.../schedules/{schedule_id}/rows`, through `xlsx_to_changeset.py`, for the Excel round trip.

## Writing back

- Never write under `.construction/` outside `.construction/skills/`. AgentCM regenerates its files and leaves alone any file changed since it wrote it, so an edited file goes stale and fixes nothing.
- AgentCM's data changes only through its write endpoints, `{api_url}/projects/{project_id}/...`: `schedules/ingest`, `schedules/reconcile`, `tag-detections/ingest`. Tell the PE what you sent; AgentCM refreshes the files it affects.
- A write names a sheet by its id: the `id` of the entry in `.construction/index/sheet_index.yaml` whose `sheet_number` matches. Never guess it from the number. If that file is missing or its entries have no `id` (an older sheet-splitter wrote a `pages:` list with `filename` and `page_index`), say so and stop.
- A reconcile names its schedule by the `schedule_id` in the schedule file's comment line (or INDEX.md); a table with `schedule_id=none` was never ingested, so there is nothing to reconcile.
- **Sending a write, and AgentCM closed.** Put the payload in `.construction/skills/<skill>/outbox/<endpoint>-<sheet>-<YYYYMMDD-HHMMSS>.json` (with the Write tool, or the script your skill names for it), then send that file: `curl -sS --fail-with-body -X POST "{api_url}/projects/{project_id}/<endpoint>" -H "Content-Type: application/json" -d @<file>`. The attempt is the check that AgentCM answers:
  - curl exits 0: AgentCM took it. Move the file to `.construction/skills/<skill>/sent/` and tell the PE what was sent.
  - curl cannot connect (exit 7): AgentCM is not running and nothing was sent. Leave the file in `outbox/`, finish the rest of the task from the files, and tell the PE to start AgentCM and rerun the write step, which sends what waits in `outbox/`.
  - curl exits 22: AgentCM refused it. Show the PE its answer and leave the file in `outbox/`.
- A skill's own working data goes in `.construction/skills/<skill>/`.

## When AgentCM is wrong

Never edit `.construction/` to fix it. Use the document's value in the task at hand and say so, with the crop as evidence: "AgentCM's index has room N141 as EXISTING DT WOMEN'S RESTROOM; the drawing shows EXISTING WOMEN'S RESTROOM (crop); I used the drawing's." Then send the correction back for the PE to confirm, never into accepted data:

- **A missed tag or callout:** `POST {api_url}/projects/{project_id}/tag-detections/ingest`, as tag-audit-and-takeoff sends it. It waits as a pending card in AgentCM's review.
- **Anything else on a sheet** (a wrong text, a room name, a wrong zone): one line in `.construction/skills/corrections.tsv`, appended only with the plugin's `scripts/corrections_append.py`, run through the plugin's Python as your skill's script list gives it. Never write the file any other way. Its arguments: `--sheet` (the sheet's number as INDEX.md names it), `--x --y --w --h` (the box from the sheet files, the numbers `crop.sh` took), `--kind` (text, room, tag, callout, zone, view, sheet or other), `--crop` (the PNG `crop.sh` printed), `--agentcm` (AgentCM's value) and `--drawing` (the drawing's value). It refuses a value it cannot check, says why, and writes nothing.
