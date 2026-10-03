# Reviewer instructions (ablation arm)

You are reviewing a construction submittal as a commercial-construction Project Engineer, following the plugin's `submittal-review` procedure. The documents are prose transcriptions of PDFs (no rasterizing needed; "pages" are the page labels in the text).

Read, in this order:
1. `/home/user/claude-code-construction/skills/submittal-review/SKILL.md` (the procedure) and its `references/review-writing.md` and `references/review-data.md`.
2. `{arm_dir}/context.md` — the compiled knowledge for this section (this is what Step 2 of the procedure produces). Use it as the procedure says: its checks, reconciliations, hooks, interfaces and failure modes are what to check. If it is thin, your own expertise fills the gap; the procedure still applies.
3. `{arm_dir}/reflexes.md` — always-on checks.
4. `{case_dir}/cds.md` — the contract documents.
5. `{case_dir}/submittal.md` — the submittal package.

HARD RULES: Do NOT read anything under `reference/csi/`, do NOT read any other file in `{case_dir}` (there is a sealed answer key; reading it invalidates the test), do not search the web, do not run the plugin scripts (the file formats are JSON; write the review as markdown instead). Do not spawn subagents. There is no one to answer questions (unattended run): make reasonable choices, leave code questions open rather than answering them from memory, and finish.

Do the work the procedure describes: trace requirements (every element in the CDs), inventory the submittal against the trace (missing / extra), review every element against every applicable check, run the reconciliations (documents that must agree), the compliance rows (regulatory hooks: bound / open), the routing rows (every interface: relevant or not), and the coverage ledger.

Write ONE file `{arm_dir}/review.md` with these sections, in this order:
1. **Findings** — a table: `id | element | severity | owner (subcontractor/gc/design_team/owner) | grade | what the submittal shows (page) | what governs (document, location) | action (who does what)`. One condition per finding. Cite both sides. No fabricated references.
2. **Suggested GC disposition** (per review-writing.md rules) and the one or two findings that drive it.
3. **Coordination routing** — a table: `interface / trade | section(s) | relevant? | what to send them (pages/items) | what is needed back | confirm who furnishes/installs/connects | gate milestone | need-by (relative to construction sequence)`.
4. **Compliance questions** — a table: `question | authority (county health dept, state, accessibility standard, fire marshal, energy code, AHJ...) | status (open: needs research / consistent / finding) | elements affected`. Never cite a code section or value you did not retrieve from the project documents.
5. **Coverage ledger** — a table with one row per element × check (status pass / finding / na / unverifiable, with a note), plus the package-scope checks. Count the rows.
6. **Unverifiable items** and the knowledge confidence floor.

Reply with one line: counts of findings by severity and the number of coverage rows.
