# SPEC: revision-history (new builder skill) + revision-compare (comparing only) + project-setup changes

Status: design chosen by the user on 2026-10-02 (compare-only variant; D8–D12 added the same day); not built yet. Supersedes candidate #1 "revision-compare" in `docs/SKILL_ROADMAP.md` §5. Requirement IDs: `RH-*` = revision-history, `RC-*` = revision-compare, `PS-*` = project-setup, `SS-*` = shared scripts, `EV-*` = evals, `G-*` = guardrails, `V-*` = checks before shipping.

## 0. Decisions the user confirmed
- D1. revision-compare **compares and reports only**. The PE does slip-sheeting, SUPERSEDED stamping, markup carry-forward and Set setup in Bluebeam, not Claude Code.
- D2. Revision history is built by a **separate builder skill named `revision-history`**, not by project-setup and not as a mode of revision-compare.
- D3. project-setup only **finds the change documents and recommends** running revision-history. It stays filename-only, with no vision and no scripts.
- D4. **Formal changes only** in v1: Addenda, Bulletins, ASIs (G710), Proposal Requests (G709), CCDs (G714), Change Orders (G701).
  - RFI sketches (SK-#) and RFI answers marked "CD to follow" are an edge case left for later.
  - Exception: when a formal document cites an RFI number, record it on that document's row.
- D5. **No SessionStart hook in v1.** Add one once refresh is stable. It would only check for new files and suggest a refresh, never run the builder.
- D6. Two records with different jobs:
  - The PE's Bluebeam set is the record of which sheet is current in the field.
  - `revision-history` is Claude's record of what changed, when, and through which document. It is a knowledge base and controls nothing.
- D7. Purpose: let Claude Code work as a highly competent PE and act on behalf of real PEs/PMs, including on projects it joins a year or more into construction.
- D8. If the current version of a sheet is unclear, **ask the PE**. Never guess, and never compare against both.
- D9. **Procore support: yes.** Read a Procore Drawings Log CSV export, and export a reference CSV in the same columns (RH-14). There's no CSV import into Procore.
- D10. revision-compare **keeps its own run log** as well as adding to revision-history (RC-15).
- D11. **Build revision-history first,** then revision-compare (§11).
- D12. **No slip-sheet worklist.** revision-compare doesn't produce a slip-sheet checklist; the sheet pairing (RC-5) stays in the revision log only.

## 1. Research findings these designs rely on (full sources in Appendix A)
- F1. **Bluebeam keeps no sheet history a script can read.**
  - Sets group separate PDFs when they are opened.
  - Batch Slip Sheet changes files in place (and saves automatically if the file is closed). It has two modes: insert-before (only this mode can stamp "Superseded") and replace (old pages are deleted). There is no archive.
  - Studio Projects history is kept on Bluebeam's servers only. `%LocalAppData%\Revu\` holds a cache of current copies.
  - Studio Sessions keep no history. [high]
- F2. **Sets are `.bex` files, not `.bfx`.** `.bfx` is Bluebeam File Exchange: XML listing URLs to PDFs and `.bax` markups, used for document-management integrations. [high]
- F3. **`.bex` structure** (no official documentation; taken from the code of the third-party parser `bluebeam-set-manager` v0.1.0, PyPI, 2026-05-29):
  - Root `<BluebeamRevuPageSet Version="1">`, then set-level settings.
  - `<File>` holds `<Category>` and a CDATA path.
  - `<Page>` holds `<Label>`, `<Width>`, `<Height>`, `<Index>` and `<Tags>`.
  - Tag keys include `SheetNumber`, `SheetName` and `RevisionNumber`.
  - The CDATA path is mixed in with child elements, so a normal XML library won't save it back unchanged. Read it with a tolerant regex scan. [medium]
- F4. **How Revu recognises revisions in a Set:** "If the drawing's sheet number already exists within the Set, Revu assumes it is the next revision."
  - A revision filter (Auto or Wildcard) reads revisions from file names.
  - Older revisions can be set to Hide, Gray Out, Cross Out or Show. Current ones can be highlighted or stacked behind a blue arrow.
  - Revu 20/21 has no "Add Version" command or version dropdown. [high]
- F5. **Stamps:**
  - Stamps are markups that appear in the Markups list with a Subject. Stamp templates are PDFs (Revu 21.10+: `%AppData%\Bluebeam Software\Revu\21\Stamps`). [high]
  - How a placed stamp is stored inside the PDF is **inferred**: a `/Subtype /Stamp` annotation with `/Subj` and `/Contents`. Bluebeam adds private keys such as `/BSIColumnData`. [medium; must be checked]
  - Flattened stamps become ordinary page content, so detection must also search the page text.
- F6. **Page labels:** Revu's dialog fields (Style, Prefix, Start, Page Range) match standard PDF page labels. AutoMark builds labels from title-block regions. Assumed readable with PyMuPDF `get_page_labels` and `Page.get_label`. [medium-high]
- F7. **AIA A201-2017 §1.1.1** (read directly):
  - Contract Documents include "Addenda issued prior to execution… and Modifications issued after execution."
  - "A Modification is (1) a written amendment… (2) a Change Order, (3) a Construction Change Directive, or (4) a written order for a minor change in the Work issued by the Architect."
  - So ASIs, CCDs and COs are modifications. Addenda are part of the contract. Bulletins and PRs are not modifications; their sheets are for pricing until a CO, CCD or ASI issues them.
  - G710 ASI: proceeding with the work means accepting no change in contract sum or time.
  - IBC 107.4: permit revisions need approval first. [high]
- F8. **Procore:**
  - Revisions are matched by drawing number and the revision number goes up automatically.
  - Revisions are ordered by Drawing Date, and the top one is current. Drawings can be marked obsolete.
  - Log columns: Number, Title, Revision, Date Authored, Date Received, Set, Status.
  - Markups on the Personal and Published layers carry forward; sketches don't.
  - The Drawings Log can be exported to CSV. No CSV import of drawing details was found; details come from Procore reading the sheets at upload plus review-and-confirm, from file names, or from the API. [high / medium]
- F9. **Bluebeam Max Smart Overlay** (Max plan only): rasterized red/green comparison, results on the web. It doesn't know what kind of document issued a change or whether a change was clouded, and it keeps no change log. Those are where these skills differ.

## 2. Where the skills sit in the pipeline
`/init → /project-setup → /sheet-splitter + /spec-splitter → /revision-history (build, then refresh) → /revision-compare (for each new package) → appends to revision-history`
- revision-history needs `sheet_index.yaml` and `spec_text/`.
- This brings back the revision tracking lost when sheet-index-builder was removed in commit `5ab70df` (roadmap line 28).

## 3. revision-history (new builder skill; built first)
- RH-1. **Purpose:** build, then keep current, Claude's record of every formal change since bid: what changed, when, and through which document, each entry cited to its source.
- RH-2. **Modes:** `build` (first run, including a year or more into a project) and `refresh` (only files new since the last run). revision-compare also adds entries (RC-12).
- RH-3. **Sources (formal changes only, per D4):**
  - a. Revision blocks on current sheets. Every earlier delta stays in the block. Clouds usually disappear on reissue, so clouds and deltas only locate the latest revision.
  - b. Change-document folders: text of pages 1–2 of each Addendum, Bulletin, ASI, PR, CCD and CO. Capture the number, date, description, the sheets and spec sections it says it revises, and any RFI, PCO or CO numbers it cites.
  - c. Revised spec sections: search `spec_text/` headers, footers and revision notes.
  - d. Existing logs: CO, ASI, CCD and Bulletin logs, plus a Procore Drawings Log CSV export if present (RH-14).
  - e. `.bex` files: read only, using the regex approach in F3.
  - f. Superseded copies of sheets (a `Superseded/` folder, SUPERSEDED-stamped pages, or the same sheet number twice in one PDF). Record where they are; don't diff them at build time.
- RH-4. **The first build stays at index level** and does not diff old against new versions. Approach:
  - Make one vision call per title-block layout (one per consultant) to find the revision-block region.
  - Extract that region's text from the PDF on every sheet with the same layout.
  - Fall back to vision only for scanned or unreadable sheets.
  - For change documents, extract text first and use vision only if a page is scanned.
  - Reuse `scripts/vision/analyze_title_block.py` and `scripts/pdf/extract_text_region.py`, which currently have no users (roadmap line 29).
- RH-5. **Change-document register:** one row per document. Fields:
  - `doc_id`, `doc_type` (Addendum | Bulletin | ASI | PR | CCD | CO), `number`, `date_issued`, `date_received`, `issued_by`, `title_description`
  - `sheets_claimed[]`, `spec_sections_claimed[]`, `cited_rfis[]`, `cited_pco_co[]`
  - `contract_status_observed` (RH-6), `superseded_or_converted_by`
  - `source_file`, `source_pages`, `extraction_method`, `confidence`, `notes`, `pe_edits_preserved`
- RH-6. **Contract status is shown, never concluded.** Values:
  - `modification` (ASI, CCD, CO)
  - `contract_document` (Addendum)
  - `for_pricing` (Bulletin or PR with no CO, CCD or ASI found)
  - `pending_ahj`
  - `unknown`

  "Latest issued" and "current for construction" are separate questions.
- RH-7. **Revision history by sheet and spec section:** one row per delta. Fields:
  - `target_type` (sheet | spec_section), `target_id`, `target_title`
  - `rev`, `rev_date`, `rev_description` (verbatim from the block), `issued_via_doc_id` (or `unresolved`)
  - `observed_in_pe_set` (current | superseded | not_found), `source_file`, `source_page`, `region_bbox`, `extraction_method`, `confidence`
- RH-8. **Discrepancies are written to the issue registry** (`scripts/issue_manager.py`) with evidence:
  - a. A document lists a sheet or section, but that target's revision block has no matching delta (not slip-sheeted, or the architect missed it).
  - b. A revision block cites a document that isn't in the folders.
  - c. A CCD has no CO behind it (report its age; draw no conclusion).
  - d. A Bulletin or PR is still `for_pricing` while sheets marked with its delta are in the PE's current set.
  - e. Revision numbers or dates are out of order, or a rev number is repeated.
  - f. The spec revision note and the change document disagree.
  - g. The Procore Drawings Log export disagrees with revision-history (RH-14).
- RH-9. **Storage:**
  - Working data: `.construction/skills/revision-history/`, containing `change_documents.yaml`, `revision_history.yaml`, `manifest.json` (path, hash, last processed), `run_log.yaml`.
  - For people to read: `Revision_History.xlsx` with tabs Change Documents, Sheet & Section History, Discrepancies, Summary.
  - Never write to `.construction/index/`; that folder belongs to AgentCM.
- RH-10. **Living-register rule:** update rows in place keyed by ID and never overwrite the PE's edits. Generalize schedule-extractor's `_row_key` + `xlsx_to_changeset.py` into a shared `scripts/registers/` helper. Build this in Phase 1.
- RH-11. **Refresh:** compare folder contents with `manifest.json` and process only new or changed files. Report something like "3 new since <date>: ASI 14, CCD 06, Bulletin 5" plus any new discrepancies. Update the CLAUDE.md line (PS-3).
- RH-12. **Skills that read it:**
  - construction-guide gets a rule: before citing a sheet or spec paragraph, check the history (is this the current revision; is a for-pricing document or a CCD with no CO pending against it).
  - rfi-drafter: check whether an ASI already answered the question.
  - submittal-log-generator: flag spec sections revised after a submittal was approved.
  - pe-review and document-set-audit: use it as background.
  - Closeout: use it for the record documents.
- RH-13. Keep SKILL.md under 500 lines and keep scripts inside the skill. Suggested scripts: `build_history.py`, `extract_revision_blocks.py`, `parse_change_docs.py`, `reconcile.py`, `export_history.py`, `refresh.py`.
- RH-14. **Procore (D9):**
  - Read a Procore Drawings Log CSV export (Discipline, Drawing No., Drawing Title, Revision No., and dates/set if present) and reconcile it (RH-8g).
  - Export `Procore_Drawing_Reference.csv` in the same columns: Discipline, Drawing No., Drawing Title, Revision No., Drawing Date, Received Date, Set name = `issued_via_doc_id`, Status. It's for whoever does Procore's review-and-confirm step.
  - Mention the Procore file-naming convention ("Number_Title.pdf" or "Number_RevNumber_Title.pdf") in the docs.
  - No API calls.

## 4. revision-compare (comparing only; built second)
- RC-1. **Purpose:** compare a newly received formal package against the PE's current set and report what changed and what it affects.
- RC-2. **Never does any of these:** slip-sheet, stamp, carry markups forward, write or change a `.bex`, set page labels, or change the PE's set or any issued PDF.
- RC-3. **Inputs:** the package (sheets and spec sections), the PE's current set (folder, bound PDF or `.bex`), and the previous `spec_text/`.
- RC-4. **Finding the baseline:**
  - Match by page label, then title-block sheet number (`sheet_index.yaml`), then file name.
  - Skip pages carrying a SUPERSEDED `/Stamp` annotation (Subject or Contents) and pages showing a flattened SUPERSEDED stamp in their text.
  - If a sheet number appears twice in one PDF, the unstamped copy is current.
  - Use `.bex` tags if a `.bex` exists.
  - If it's still unclear, **stop and ask the PE** (D8), showing the candidates with file and page.
- RC-5. **Pairing:** sheets added, removed and reissued, plus sheets the package says it revises but doesn't include.
- RC-6. **Comparing:**
  - Rasterize both versions at the same DPI and align them using text anchors from the PDF.
  - Find changed regions with a pixel diff (Pillow `ImageChops` and a grid flood-fill; no numpy).
  - Diff the words in each region. Before/after values come from the PDF text and are authoritative.
- RC-7. **Clouds:** use vision only to describe regions and decide clouded vs. unclouded. Check the new revision-block row against the package's number and date; a mismatch is a finding.
- RC-8. **Spec comparison:** section by section on `spec_text/`.
- RC-9. **Impact:**
  - discipline, trades (`csi_masterformat.yaml`), affected `Submittal_Log.xlsx` rows, and open RFIs;
  - cost/time flag Y, Possible or N with a reason and no pricing;
  - contract status from RH-6, shown with the G710 note for ASIs and "for pricing, not for construction" for Bulletins and PRs.
- RC-10. **Issue registry:** unclouded changes, and conflicts with sheets or sections that weren't revised.
- RC-11. **Outputs** in `Revisions/{package_label}/`:
  - `Revision_Log_{label}.xlsx` with tabs Summary, Sheet Changes, Change Items, Spec Changes.
  - Red/green overlay PDFs.
  - **Copies** of the new sheets with change markups (real cloudy-border annotations, Subject such as `Revision-Compare: unclouded change`). The PE can move these onto their own sheets with Bluebeam's markup transfer.
  - Working data in `.construction/skills/revision-compare/{label}/`.
- RC-12. **Every run adds entries to revision-history** (RH-5 and RH-7 rows) through the RH-10 helper.
- RC-13. **How it differs from Smart Overlay:** diff from the PDF text, unclouded-change detection, document-type awareness, impact routing and the log.
- RC-14. Scripts inside the skill: `find_baseline.py`, `pair_sheets.py`, `diff_pages.py`, `diff_spec_text.py`, `export_revision_log.py`. SKILL.md under 500 lines.
- RC-15. **Run log (D10):** `.construction/skills/revision-compare/run_log.yaml`, one entry per run:
  - `run_id`, `date`, `package_doc_id`, `package_files`
  - baseline found for each sheet (file, page, method), plus questions asked and the PE's answers (D8)
  - counts (sheets added, removed, reissued; change items; clouded/unclouded; findings)
  - output paths, and the revision-history rows added.

## 5. project-setup changes (still filename-only: no vision, no scripts)
- PS-1. Step 2 new detection rows:
  - change-document folders and files (ASI, CCD, Bulletin, Addendum, PR, CO, "Revisions", "Change Directives");
  - change logs;
  - a Procore Drawings Log CSV export;
  - `Superseded/` folders;
  - `.bex` files.
- PS-2. Step 3 new recommendation row: "Run `/revision-history` to build the change history (N change documents found)."
- PS-3. Step 4 CLAUDE.md line: `Revision history: {path or "not built"}, last refreshed {date}, {N} change documents`.
- PS-4. Update the pipeline diagram to include `/revision-history`. The "does not use vision" and "no scripts" statements stay.

## 6. Guardrails
- G-1. Every log entry and finding cites its source file and page (plus region for sheets). Never cite anything from outside the supplied documents.
- G-2. Contract status, cost and time are shown, never concluded. No pricing and no legal conclusions.
- G-3. Never modify the PE's set, the issued PDFs or the PE's register edits.
- G-4. If the current revision is unclear, ask (D8).
- G-5. Never present for-pricing sheets as what to build from.

## 7. Shared-script and documentation issues found during design
- SS-1. `scripts/pdf/annotate_pdf.py` line 86 draws "cloud" as a dashed rectangle. Switch to `set_border(clouds=N)` on Square/Polygon annotations (PyMuPDF 1.22.5+). Needed for RC-11 (Phase 2).
- SS-2. `scripts/pdf/annotate_pdf.py` line 112, `stamp=0`, always draws the "Approved" stamp. Neither skill writes stamps, but fix it or document it.
- SS-3. `requirements.txt` pins `PyMuPDF>=1.24.0`. Check which version added image stamps before anything relies on them.
- SS-4. Done 2026-10-02: `docs/SKILL_ROADMAP.md` §5.1, §7 and §8 now point to this spec.
- SS-5. `docs/CM_SKILLS_SOP.md` line 181 already lists an "ASI/Bulletin log"; the RH-5 register fills it.

## 8. Things to check before shipping (no Revu install on this machine)
- V-1. Revu shows PyMuPDF cloudy-border annotations as revision clouds.
- V-2. SUPERSEDED detection works on real PDFs stamped by Revu Sets and by Batch Slip Sheet.
- V-3. `.bex` parsing works on a real Set file.
- V-4. Revu page labels can be read through PyMuPDF.
- V-5. Procore Drawings Log CSV export: confirm the actual column names before writing RH-14.

## 9. Evals (aiming for the SOP's 100% of seeded conflicts)
- EV-4 (Phase 1). revision-history fixture: a synthetic change-document folder plus sheets with revision blocks. The planted CCD→A501 mismatch (RH-8a), missing ASI 9 (RH-8b) and CCD with no CO (RH-8c) must all be caught. Register fields must be filled in and cited.
- EV-5 (Phase 1). Refresh: add an ASI. Only that file is processed, the report names it, and the PE's xlsx edits survive.
- EV-7 (Phase 1). Procore reconciliation: a planted revision mismatch in a sample Drawings Log CSV is flagged (RH-8g).
- EV-1 (Phase 2). The planted-edit fixture `_fixtures/revision/make_revision_set.py` (following the `make_addendum.py` pattern; every page stamped "EVAL FIXTURE" identically in both issues) with its assertions:
  - A500 door 220 changed from 3'-0" to 3'-6", clouded;
  - A101 door tag removed;
  - an unclouded note change;
  - one sheet added and one removed;
  - a control sheet with 0 items;
  - spec 09 65 13 changed;
  - nothing cited from outside the sets.
- EV-2 (Phase 2). Stamped (annotation) and flattened-stamp pages are skipped. A duplicate sheet number resolves to the unstamped copy. An unclear case triggers a question, not a guess.
- EV-3 (Phase 2). A for-pricing package gets the warning and the for-pricing status.
- EV-6 (Phase 2). revision-compare adds correctly linked revision-history rows and writes a run_log entry.

## 10. Open items
- None for v1.
- O6. Future, not v1: RFI sketches and "CD to follow" answers; the SessionStart hook; permit revisions and deferred submittals as document types.

## 11. Order of work (D11)
- **Phase 1 – revision-history:**
  - RH-1 to RH-14;
  - the RH-10 shared register helper;
  - issue-registry wiring;
  - PS-1 to PS-4;
  - the construction-guide rule from RH-12;
  - EV-4, EV-5, EV-7.
- **Phase 2 – revision-compare:**
  - RC-1 to RC-15;
  - SS-1 (clouds);
  - EV-1, EV-2, EV-3, EV-6;
  - V-1 to V-4 on a real Revu install.
- SS-2 and SS-3 can happen at any time. V-5 before RH-14.

## Appendix A: Sources
**Bluebeam**
- Sets panel (Revu 21): https://support.bluebeam.com/user-manual/menus/window/sets-panel.html
- Sets preferences: https://support.bluebeam.com/user-manual/menus/revu/sets-preferences.html
- Sets panel (Revu 20): https://support.bluebeam.com/online-help/revu20/Content/RevuHelp/Menus/Window/Panels/Sets/Sets-Tab--V.htm
- Manage large PDFs with Sets: https://support.bluebeam.com/revu/how-to/manage-large-pdfs-with-sets.html
- bFX guide: https://support.bluebeam.com/resources/pdfs/bfx-guide.pdf
- Batch Slip Sheet (Revu 21): https://support.bluebeam.com/user-manual/menus/batch/slip-sheet.html
- Batch Slip Sheet (Revu 20): https://support.bluebeam.com/online-help/revu20/Content/RevuHelp/Menus/Batch/Slip-Sheet/Batch-Slip-Sheet--T.htm
- Transfer markups with Batch Slip Sheet: https://support.bluebeam.com/revu/how-to/transfer-markups-with-batch-slip-sheet.html
- Transfer markups: https://support.bluebeam.com/revu/how-to/transfer-markups.html
- Studio Project files: https://support.bluebeam.com/user-manual/menus/window/manage-project-files.html
- Revision history from Sessions: https://support.bluebeam.com/studio/how-to/tips-and-tricks/create-revision-history-sessions.html
- Work offline in Studio: https://support.bluebeam.com/articles/revu-work-offline-in-studio/
- Studio API: https://developers.bluebeam.com/s/studio
- Stamps: https://support.bluebeam.com/user-manual/menus/tools/edit-stamps.html
- Back up stamps: https://support.bluebeam.com/revu/how-to/backup-and-restore-stamps.html
- Page labels: https://support.bluebeam.com/user-manual/menus/window/edit-page-labels-page-numbers.html
- Smart Overlay: https://support.bluebeam.com/revu/how-to/use-smart-overlay.html
- Community thread on the Superseded stamp: https://community.bluebeam.com/discussion/7880/superseded-stamp-using-add-files-to-set

**Third-party tools and libraries**
- `.bex` parser: https://pypi.org/project/bluebeam-set-manager/
- `BSIColumnData` discussion: https://github.com/py-pdf/pypdf/discussions/2270
- pymkup: https://github.com/psolin/pymkup
- PyMuPDF Page docs: https://pymupdf.readthedocs.io/en/latest/page.html
- PyMuPDF Annot docs: https://pymupdf.readthedocs.io/en/latest/annot.html

**Contract documents and codes**
- AIA A201-2017 (SC sample): https://procurement.sc.gov/files/A201_2017.SCOSE_.sample.pdf
- G710 summary: https://help.aiacontracts.com/hc/en-us/articles/1500009443722-Summary-G710-2017-Architect-s-Supplemental-Instructions
- G714 summary: https://help.aiacontracts.com/hc/en-us/articles/1500009448081-Summary-G714-2017-Construction-Change-Directive
- EJCDC C-942 Field Order: https://ejcdc.org/product/c-942-field-order/
- IBC 107.4: https://up.codes/s/amended-construction-documents
- IBC 107.3.4.1: https://codes.iccsafe.org/s/IBC2018P6/chapter-1-scope-and-administration/IBC2018P6-Ch01-SubCh02-Sec107.3.4.1
- Conformed documents: https://www.lawinsider.com/dictionary/conformed-documents

**Procore**
- Drawings: https://support.procore.com/products/online/user-guide/project-level/drawings
- Drawing log: https://support.procore.com/products/online/user-guide/project-level/drawings/tutorials/manage-drawing-log
- Upload drawing revisions: https://en-gb.support.procore.com/products/online/user-guide/project-level/drawings/tutorials/upload-drawing-revisions
- Upload drawings: https://support.procore.com/products/online/user-guide/project-level/drawings/tutorials/upload-drawings
- Export the Drawings Log to PDF or CSV: https://v2.support.procore.com/product-manuals/drawings-project/tutorials/export-the-drawings-log-to-pdf-csv
- Direct drawing uploads (API): https://procore.github.io/documentation/tutorial-direct-drawing-uploads

## Appendix B: Repo files this touches
- `docs/SKILL_ROADMAP.md`
- `docs/CM_SKILLS_SOP.md`
- `skills/project-setup/SKILL.md`
- `skills/sheet-splitter/SKILL.md`
- `skills/construction-guide/SKILL.md`
- `scripts/pdf/annotate_pdf.py`
- `scripts/pdf/extract_annotations.py`
- `scripts/pdf/extract_text_region.py`
- `scripts/vision/analyze_title_block.py`
- `scripts/issue_manager.py`
- `requirements.txt`
- New: `skills/revision-history/`, `skills/revision-compare/`, `scripts/registers/`, `evals/plugin/_fixtures/revision/`
