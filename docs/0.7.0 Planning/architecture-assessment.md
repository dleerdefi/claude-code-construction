# 0.7.0 architecture: the PM → PE model and pstack, tested adversarially

**Status:** assessment, with a recommended 0.7.0 scope (the development specification is `0.7.0-dev-spec.md`, beside this file) · **Written:** 2026-10-15 · **Against:** `main` c8089c9 (plugin 0.5.1), `release/0.6.0` aaae1d4 (PR #28, open), pstack v0.15.25 (cloned 2026-10-15), the Claude Code docs as read on 2026-10-15 (versions up to v2.1.296), `Inside pstack.md` (14 Oct 2026).

The question was in three parts. Should the skills run the way a General Contractor's project team runs, a Project Manager instructing Project Engineers who each own a plan set or scope? If so, should the PEs be sub-agents inside one Claude Code session or separate sessions that talk to each other? And is pstack worth porting onto that? Each part was argued against before it was argued for. The verdicts are below, then the evidence.

## 0. Verdicts

1. **The org chart transfers; the people do not.** What a GC team gets right carries over: work is partitioned by scope, a task reaches only the scopes it touches, one person owns each deliverable, and the PM owns the report. What does not carry over is the reason the partition works in real life: a PE's value is months of accumulated context and accountability. A Claude worker has neither beyond its transcript. On this plugin the memory already lives in files, `.construction/` (AgentCM's) and `.construction/skills/` (the plugin's), and a reading skill works the same with AgentCM closed (`reference/agentcm-mode.md`). So "a PE owns the structural set" collapses to **an ephemeral worker scoped to a partition**, justified by context-window budget and parallelism, not by expertise. That is the design, and it is a different thing from the one proposed.

2. **Sub-agents inside one session, not separate sessions.** The deciding fact is the repo's own gate: skills must pass eval before production, and the harness runs headless (`claude-agent-sdk`, the `-p` path). Sub-agents run there. Agent teams are experimental, off by default, and "In non-interactive mode with the `-p` flag, including Agent SDK sessions, Claude doesn't spawn teammates" (Claude Code docs, agent teams). Cross-session messaging works between terminals on one machine, but a headless run is one session, so nothing it did across sessions could be graded. A skill built on multi-session choreography cannot pass the gate that lets it ship. Separate sessions stay what they are good at today: a developer running work across repositories, watching it. They are not a thing the plugin can ask a PE on Windows to set up, and they would not be graded if it did.

3. **Fan-out is a cost multiplier, so it goes only where the work spans partitions.** The plugin already does this in submittal-review, and the measured case passed at 1.00 twice; submittal-log-generator's text recommends it for large manuals, but no case has ever exercised that paragraph and the skill's own per-section pattern releases each section's text as it goes. 0.7.0 is the generalization of a proven pattern into shared infrastructure, applied to the three skills whose work crosses disciplines or exceeds a sheet or page threshold (pe-review, tag-audit-and-takeoff, submittal-review), and switched on by default only after an A/B on the same case shows the score held and the cost is explained.

4. **pstack: port seven ideas, reject the rest.** pstack is a system for writing code with git under one person's style. Its orchestration is Cursor's (cloud agents, multi-model panels, PR stacks). The transferable part is its discipline: fixed output contracts for workers, "gather, don't conclude", gaps as required output, a decision trail for unattended runs, the author never being the critic, rules encoded as checks instead of prose, and skills that get shorter. Several of these the repo already practises under other names. The honest delta is smaller than the ten-item list in `Inside pstack.md`, and it is listed item by item in §6.

5. **No router skill in 0.7.0.** pstack needs a router because every one of its skills is explicit-only. Ten of this plugin's fourteen skills are user-invoked by slash command on purpose (they have side effects), and the rest trigger by description. Scope routing, the part of the PM's job that is a lookup, becomes a script, not a skill.

## 1. What was examined

- This repository, read on `release/0.6.0` (worktree `../claude-code-construction-0.6.0`, clean at aaae1d4) for everything that changed there: the 14 skills, `reference/agentcm-mode.md`, the eval harness and its README, the plugin eval suite README, `dev/gate`, the AgentCM fixture. `docs/CM_SKILLS_SOP.md`, `docs/SKILL_ROADMAP.md` and `docs/specs/revision-history.md` were read on `main` and their 0.6.0 diff checked (the SOP's changes are the findings-folder and `specs/` paths; the other two are unchanged). `skills/construction-guide/SKILL.md` was read on `main` first and again on 0.6.0, where it is rewritten (346 lines; the database section and the old `.construction/` tree are gone, the mode is decided by reading `project.yaml`); every claim about it below is against the 0.6.0 text. The `Downloads/construction-skills (1)` copy (1 October) was not opened.
- AgentCM's contract fixture (`evals/plugin/agentcm-mode/construction/`): `INDEX.md`, `CLAUDE.md`, `sheets/`, `schedules/`, `specs/`, `tags.tsv`, `xrefs.tsv`, `index/sheet_index.yaml`, `project.yaml`.
- pstack v0.15.25, cloned from `cursor/plugins` (sparse checkout of `pstack/`, at `%LocalAppData%\Temp\pstack-clone\plugins\pstack`; the scratchpad path was too long for git on Windows). Read: `plugin.json`, `README.md`, both agent definitions, `poteto-mode/SKILL.md`, the playbooks investigation, bug-fix, orchestrate, autonomous-run, session-pickup, pause-safely and authoring-a-skill, the skills why, swarm, show-me-your-work, correct, create-verification-skill and reflect with their references, nine principle skills, guide pages 01, 07 and 09. The report `Inside pstack.md` was read in full and checked against the source where it mattered; the clone worked, so no part of this rests on the report alone.
- The Claude Code docs (sub-agents, skills, hooks, agent teams, cross-session messaging, headless, plugin manifest), read 2026-10-15 through the guide agent, for what the runtime supports today. Facts from there are marked (docs) below.

## 2. What the repo already does

The proposal is not new to this plugin. The evidence that bears on it:

| Fact | Where | What it shows |
|---|---|---|
| submittal-review fans out: more than about eight elements → batches of five to eight per worker, launched with the Agent tool, each worker given `references/worker-prompt.md`, writing `findings_NN.json` and `review_NN.json`, returning one line. "Workers run in parallel and share nothing but the review directory." A gate script (`check_review.py`) proves completeness before the report. | `skills/submittal-review/SKILL.md` Step 5, `references/worker-prompt.md` | A coordinator → worker pattern with file handoffs and a deterministic gate is already in production. |
| The 366-page foodservice case passed at 1.00 in both of two harness runs, $3.64 and $4.98, 61 and 59 turns, about 12 minutes each (Sonnet, 2026-10-04). | `evals/plugin/README.md` | Fan-out is testable in the harness and holds up on a large input. |
| submittal-log-generator: "Parallel processing (recommended for 60+ sections)": sub-agents write numbered batch files, merged with `jq`; "Do not have agents return JSON in their response text and then parse it from conversation logs." | `skills/submittal-log-generator/SKILL.md` lines 410–417 | A second fan-out on paper only: its cases cover 2 and 4 sections, the skill's per-section pattern compacts after each section ("Release the section text from context"), and the PE has seen it work without workers. Its merge step is Windows-hostile (`jq` may be missing). |
| The suite's convention 5 is "no subagents"; submittal-review's cases are the recorded variance. | `evals/plugin/README.md`, Writing a case | Fan-out is the exception today, and each fan-out case costs $4–5 against under $1 for most cases. |
| A single Sonnet run of the whole suite: about $45, well over an hour. subcontract-writer alone: 18 minutes and $6 with no fan-out. | `evals/plugin/README.md` | Cost, not capability, is the constraint on how much parallelism the suite can afford to verify. |
| Findings go to `.construction/skills/<skill>/findings/` in both modes; the issue registry has few producers; three stores that nothing connects. | 0.6.0 `.claude/CLAUDE.md`, `docs/SKILL_ROADMAP.md` §1 | Cross-skill memory is files. It is incomplete, and a multi-agent design must not add a fourth store. |
| No skill runs a database query; AgentCM is read from its files only; writes go through the API or wait in an outbox. | `reference/agentcm-mode.md`, `dev/check_no_queries.py` | Workers can read AgentCM concurrently with no coordination at all. The only serialized resources are the API, the outbox, the registry and the plugin's own registers. |
| `dev/gate`, the no-inline-python and no-helper-scripts graders, the outside-writes blocker. | 0.6.0 `dev/`, `evals/harness/` | The repo already turns repeated corrections into checks. This is pstack's `/correct` ladder in practice. |

### The partition keys AgentCM gives

A PM routes a task by discipline and by trade. Both keys exist in AgentCM's files, and one of them is unreliable:

- `INDEX.md`'s Drawing sheets table has a Discipline column. In the contract fixture every sheet reads `discipline: unknown` (`index/sheet_index.yaml` says the same). The sheet number's prefix letter is the fallback (`reference/drawing_conventions.md`), and after that the PE.
- `INDEX.md`'s Specification sections table has a Division column, and `reference/csi_masterformat.yaml` maps a division to its typical subcontractors. This key is reliable.
- `xrefs.tsv` has `target: discipline` for a reference that names another discipline ("SEE STRUCTURAL"), and `target: sheet` with `found` for callouts. These lines are exactly the cross-partition signal a PM routes on: which other scope a task touches.
- `tags.tsv` carries a room, door or tag across every sheet it is on, which is how a task scoped to a room reaches every discipline that draws it.

So "the PM knows which parties to involve" is, on this data, a deterministic lookup: the sheets and sections in scope, their partitions, and every `xrefs.tsv` line that crosses out of those partitions. Encoding it as a script rather than as coordinator judgment is pstack's encode-lessons-in-structure principle, and it is also what makes the routing gradable.

## 3. The PM → PE model, tested

### 3.1 What the analogy gets right

- **Partition by scope.** A task about door hardware does not need the civil set. Loading only the partition's files is the single biggest lever on context (SOP §5.3: "minimum viable document access is the primary performance lever").
- **Route only to the scopes a task touches.** Most tasks touch one or two partitions; a few (set audits, coordination reviews, a bulletin) touch many.
- **One owner per deliverable.** One writer per output file. pstack says the same (separate-before-serializing-shared-state); submittal-review does it (each worker writes only its batch's files).
- **The PM owns the report.** The coordinator reconciles, decides, and talks to the PE. Workers never talk to the user. pstack: "You own every subagent's work. Review the diff and write your own summary."

### 3.2 Where it breaks

- **The PE's expertise is memory, and the memory is in the files.** A "structural PE" worker knows nothing about the structural set that any worker reading `INDEX.md` filtered to S-sheets would not. There is no transcript-level knowledge worth preserving between tasks that is not better written to `.construction/skills/`. pstack's own rule: "Fresh subagents by default… Interrupt-chained resumes silently drop directives." Standing per-discipline agents would be the construction version of the resumed agent pstack warns against.
- **Standing sessions buy nothing files do not, and cost a lot.** A session kept open per plan set holds an unbounded transcript that compacts, and when it closes its context is gone. Its only durable output is what it wrote to disk, which an ephemeral worker writes just as well. For a non-technical PE on Windows it is also a setup burden the user already named.
- **Lateral PE-to-PE communication is shared mutable state.** In real life PEs reach out to each other. In Claude Code that is SendMessage between named workers (docs: the `name` parameter makes an agent addressable). Two workers that negotiate a finding between themselves produce a conclusion the coordinator never saw, in a channel no grader reads. pstack's orchestrate playbook: "Keep sibling communication upward only." The construction version: a worker that finds a cross-partition question records it in its own output with the `xrefs.tsv` line as evidence; the coordinator routes it, which is what the PM does on a real team anyway.
- **"The PM knows whom to involve" is a lookup, not judgment** (§2). Leaving it to the coordinator's judgment makes it unrepeatable and ungradable.
- **Most skills do not span partitions.** See §5. For eight of fourteen skills a coordinator with nothing to coordinate is a layer that pays an orientation preamble for no return.

### 3.3 What it becomes

A **coordinator** (the session that received the slash command, running the skill as today) and **ephemeral workers**, each scoped to one partition, each given a brief that stands alone, each writing only its own files, each replying one line. The partitions come from a script. The coordinator merges, reconciles what crosses partitions, applies the gate, writes the registry and the findings, and reports to the PE. Fan-out happens only above a per-skill threshold, and the same exporters produce the same deliverables with or without it.

This is submittal-review Step 5 made shared, with the routing made deterministic. The "PM" is the skill's own workflow; the "PE" is a brief in `references/`, not a person or a session.

### 3.4 Outside a skill

The same question arrives more often as plain text than as a command: "is the kitchen equipment coordinated with the electrical", "which sheets reference 07 92 00". The workflow should not depend on the PE knowing a skill name, and on this plugin it mostly does not. construction-guide is model-invocable and loads before any document work, so the coordinator-side rule belongs there. What it routes to is decided by the question's kind, not by its size. A lookup across the whole set is, in AgentCM mode, one search over `tags.tsv`, `xrefs.tsv` and the sheet files; the index is the fan-out and no worker is spawned. A review or absence question is pe-review's description, and pe-review triggers by description and carries the fan-out. Only a read that must look at many drawings (flat-file mode, or sheets AgentCM could not read) fans out from the guide itself, and because no command fixed a threshold the PE agreed to, the coordinator shows the scope and the cost and asks first. A single-sheet question never runs the router. The spec carries this as D13 and §4.6, with a negative case so the rule cannot grow into the router §6.3 rejects.

## 4. Sub-agents in one session, or separate sessions

| | Sub-agents (Agent tool, one session) | Separate sessions messaging each other |
|---|---|---|
| **Runs in the eval harness** | Yes: sub-agents are available under `-p` and the SDK (docs, headless). The foodservice case proves it. | No: agent teams do not spawn under `-p` or the SDK (docs, agent teams). Cross-session messaging needs a second session, which a harness run does not have. **The repo's ship gate cannot grade it.** |
| **Shippable by the plugin** | Yes: a plugin ships agent definitions in `agents/*.md` (docs, sub-agents); the manifest `agents` key lists the files. Plugin agents cannot set `hooks`, `mcpServers` or `permissionMode`. | Nothing to ship: the plugin cannot start a session, name it or make the PE do so. |
| **User setup** | None. `/construction:pe-review` as today. | The PE starts N sessions, names each, keeps them open, and routes work by hand. The user's own words: hard to instruct a non-technical PE to do this. |
| **State and memory** | Workers are fresh; everything durable is on disk, where it already is. | A session's context compacts and then ends. Durable state is still the disk. |
| **Isolation** | The coordinator chooses the model (`sonnet` workers, docs) and the tools per worker; a worker without the Agent tool cannot nest (depth is three by default, docs). | Each session has full tools and its own permissions; nothing limits what a "PE session" does. |
| **Cost** | One coordinator plus N short workers; measured at $4–5 for 366 pages. Concurrency limit 20 by default (docs). | N long-lived sessions at full context each, plus the coordinator. |
| **Availability** | Native Windows, macOS, Linux; v2.1.219+ for nesting defaults. | Cross-session messaging: v2.1.224+ (v2.1.234+ native Windows), on by default (docs). Agent teams: experimental, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, one team per session, no nested teams (docs). |
| **What the user has seen work** | submittal-review. | Sessions across AgentCM and this repo, in the desktop app, with a developer watching. |

The user's observation about separate sessions is right for what it describes: a developer driving several repositories at once, in the desktop app, able to read every session. That is a development workflow, and it stays one. It is not an execution model a skill can depend on, and it is the wrong tool for a PE who typed one command and wants one workbook back. The spec documents it as an advanced pattern for developers and keeps it out of every skill.

## 5. Which skills span partitions

Fan-out multiplies cost (sub-$1 cases become $4–5) and adds a failure mode (an incomplete batch). It earns its place only where the work crosses partitions or the input exceeds what one context should hold.

| Skill | Spans partitions? | Threshold where one context runs out | Verdict |
|---|---|---|---|
| pe-review | Yes: coordination is by definition cross-trade; 0.6.0 checks every `xrefs.tsv` line from the sheets in scope with a crop each. | More than one discipline in scope, or more than about 10 sheets. The Sanibel real set has 125 sheets. | **Pilot.** Highest value, existing eval, a 4-discipline fixture. |
| tag-audit-and-takeoff | Yes across sheets: one tag type across a discipline's set, a view or quadrant at a time. | More than a few sheets. | **Second.** One worker per sheet or per discipline; the coordinator alone sends the ingest. |
| submittal-log-generator | Per section, independent; each section's text is released after it is processed, so one context does not fill. | None measured: the 60+ figure is the skill's own guess, and no case has exercised it. | **No fan-out in 0.7.0.** Measure a full manual without workers; if it completes, delete the parallel paragraph and the `jq` merge rather than build on them. |
| submittal-review | Already fans out per element batch. | About 8 elements (its own figure). | **Migrate** to the shared contract; keep `check_review.py`. |
| document-set-audit (roadmap #2, not built) | Yes: the whole set, every callout. | Always. | Built on the shared infrastructure when it is built; not in this scope. |
| revision-compare (specified, not built) | Per package; sheets pair independently. | Large packages. | Same. |
| sheet-splitter, spec-splitter | One bound PDF; scripts do the work. | n/a | No fan-out. |
| schedule-extractor | One schedule on one sheet. | n/a | No. |
| bid-tabulator, bid-evaluator, subcontract-writer | Bids and a template; one scope. | n/a | No. |
| rfi-drafter | One issue at a time; the PE's checkpoint is the whole point. | n/a | No. |
| code-researcher | Research by topic. | n/a | No. |
| project-setup, construction-guide | Orientation, reference. | n/a | No. |

Nine of fourteen skills gain nothing from a coordinator. The three that do are among the skills whose evals already cost the most.

## 6. pstack, tested

### 6.1 What it is, and the mismatch

pstack is 54 skills for shipping code: one router, 23 playbooks, 24 one-rule principles, two agent definitions and 7k lines of Bun/TypeScript. Its subject is a git repository; its proof is a running app; its unit of delivery is a PR; its reviewers are different model vendors. None of those exist here. This plugin's subject is a document set that nobody edits, its proof is a crop of the drawing and a gate script, its unit of delivery is a workbook or a Word file, and Claude Code offers one model vendor. So the orchestration layer (arena, architect, interrogate, babysit, shipping, both autopilots, orchestrate's PR machinery, worktree cleanup, the bot UI) has no object to act on, and the scripts are in the wrong language for a Python toolkit.

What survives the mismatch is pstack's discipline about agents, and most of it the repo already practises under other names.

### 6.2 Idea by idea

| pstack idea | What the repo has today | Delta | Verdict |
|---|---|---|---|
| SKILL.md orchestrates, sub-agent prompts live in `references/`, each with a fixed output contract the next stage consumes; "Gather, don't conclude." | submittal-review's `worker-prompt.md`: exact files to write, one-line reply, "Do not answer… the main reviewer handles code research." | One shared contract (`reference/worker-contract.md`) and one shared batch checker, used by every fan-out skill. | **Port.** |
| Uncertainty is required output: "If no gaps are mentioned, that's suspicious." | submittal-review's `unverifiable`; construction-guide's NOT FOUND grade; agentcm-mode's "not found in AgentCM's index, never does not exist". | A required "could not verify" section in every review deliverable (pe-review, tag-audit), graded. | **Port** (small). |
| Five confidence tiers with phrasing rules. | CONFIRMED / PROBABLE / CONFLICTING / NOT FOUND (construction-guide Output Standards), OPEN (pe-review rules). | None worth a change. The construction grades map to documents, pstack's to history. | **Already have.** |
| Decision trail (`show-me-your-work`): append-only TSV, evidence column, audited against the transcript. | `state.yaml` with status, `lessons.yaml`, the revision spec's `run_log.yaml`. No per-decision trail. | `decisions.tsv` per run, written by a script, read by graders. Pays off in unattended runs (the harness, overnight set audits). | **Port.** |
| Author is never the critic: a separate agent judges the author's output. | None. The gate script checks completeness, not judgment. | A review-check worker, fresh context, reads findings against their cited sources before the report. One vendor, so "different context", not "different model". Kept only if an A/B shows it catches something. | **Port as an experiment.** |
| `/correct`: fix each repeated mistake at the highest level (architecture, lint, test, docs); keep a rule → enforcer table. | `dev/gate`, the graders, `dev/check_no_queries.py`, the "deviations are signals" practice. No table. | The table, in `.claude/CLAUDE.md`. A rule nothing enforces counts as a repeat. | **Port** (an afternoon). |
| Fresh sub-agents by default; never resume; one writer per worktree; upward-only communication. | submittal-review: "share nothing but the review directory"; "If a batch file is incomplete, re-run that worker." | Make it the rule for every fan-out: no resume, no lateral messages, no shared files. | **Port.** |
| Skills get shorter: repeated cut passes, each checked against behavior; a principle can be 34 words. | Two skills over 500 lines; `docs/AUDIT_SKILL_LANGUAGE.md`. The SOP's 500-line rule. | A measured prune pass (blind A/B in the harness) is the only way to cut safely. | **Port as a maintenance item.** |
| Playbook steps copied verbatim into the todo list; a skipped step stays as `skip: reason`; a **Reply:** contract per playbook. | Every skill has a Workflow checklist; several have a "Tell the PE" section. | One SOP line: the checklist opens the todo list, a skipped step stays visible with its reason, every skill names its reply. | **Port** (an SOP line). |
| One router skill with playbooks. | Ten skills user-invoked by design; four trigger by description; README chains. | A router would re-route what already routes, and a wrong route is worse than an explicit command. | **Reject for 0.7.0.** |
| Verification skill (`create-verification-skill`): drive the real app and capture evidence. | The eval harness, the fixtures, `check_review.py`, the crop graders. There is no app to drive; the drawing is the artifact and the crop is the evidence. | None. | **Already have, in the harness.** |
| `/reflect`: mine the transcript, route lessons to skill edits. | `lessons.yaml` in submittal-review; SOP §8 "aspirational". | Could generalize to a project-level lessons file. Not an architecture item. | **Defer.** |
| Role-based models; cross-family judges; `/setup-pstack`. | Harness: `--model sonnet`, `--judge-model`. | Worker model per spawn (`sonnet` default, docs). Cross-family is unavailable. | **Partial:** model per worker, nothing more. |
| arena, architect, interrogate, tdd, typescript-best-practices, no-comments, unslop, technical-writing, teach, bro, sharpen, in-your-own-words, recall, ketchup, benchmark-checklist, automate-me, make-bot-ui, babysit, shipping, autopilot-full, autopilot-stack, worktree-cleanup, multi-phase-plan, the Bun scripts, the benny automation. | n/a | Code, PRs, prose style or Cursor features. | **Reject.** |
| orchestrate playbook (coordinator never writes code, brief template, completions as queue events, ledger keyed by head SHA, retry by failure mode). | n/a (no program of PRs) | Two pieces transfer: the brief template's shape (goal, scope, context by path, acceptance, verify, forbidden, report) and "retry a failed worker once with smaller scope, then record a gap". The rest is PR machinery. | **Borrow two pieces inside the worker contract.** |

### 6.3 Why the rejected items stay rejected

- **A router.** The PE types `/construction:submittal-review file.pdf`. A mode that reads "review this" and picks a skill adds a routing step the PE did not ask for and a new way to be wrong. If 0.7.0's fan-out proves out and a multi-skill chain (onboarding, a new bulletin) turns out to need an entry point, that is a 0.8.0 question with evidence behind it.
- **Multi-model review.** The runtime offers Claude tiers only (docs). Reviewers that differ by context are what is available, and the spec treats that as an experiment, not a guarantee.
- **The Bun scripts.** The toolkit is Python with a single `requirements.txt` and `bin/construction-python`. Every pstack script worth having (the TSV logger, a plan linter) is a few dozen lines of Python.
- **Verification skill generation.** The equivalent exists and is stronger here: real fixtures with planted defects, deterministic Python checks, blockers.

## 7. Risks and open questions carried into the spec

1. **Partition keys.** `discipline: unknown` on every sheet of the fixture. The router script needs the prefix fallback and must list what it could not place for the PE, never guess (spec SR-*).
2. **Harness coverage of workers.** Measured on 2026-10-15 (`harness-probes.md`, four runs against the 0.6.0 harness): the guard fires for a worker's Bash, Write and Edit calls and the denials take effect; `total_cost_usd` is the whole run; worker transcripts sit at the documented path; and the SDK stream carries every worker tool call with the parent's id by default, so the harness trace already holds worker calls, unlabelled. The harness work is small (spec HR-1 to HR-5) and nothing blocks; the one surprise is that any case granting `Agent` is already graded on its workers' calls on this CLI and SDK.
3. **Cost.** Fan-out on by default only after the A/B records score, turns, cost and wall time with and without it, on the same case, three runs each. "Explain the number": a run that scored the same and cost twice as much has to say what the second half bought.
4. **Shared state.** Workers never write the issue registry, the submittal log, `corrections.tsv`, an outbox or the API. The coordinator is the one writer. This is a rule the harness grades, not a sentence in a prompt.
5. **Plugin agent limits.** A plugin's agents cannot set `hooks`, `mcpServers` or `permissionMode` (docs). `skills:` can preload `construction-guide` (model-invocable) but no user-invoked skill. Workers do not inherit the parent's invoked skills, so every brief points at files by path, as `worker-prompt.md` does now. The exact `subagent_type` string for a plugin agent is a pre-ship check.
6. **Lateral messaging.** Possible (the `name` parameter), named as desirable, and rejected (§3.2). A worker's tools omit SendMessage and Agent.
7. **Compaction in long coordinator runs.** A set audit over 125 sheets may compact the coordinator. The decision log and per-worker files are the resume point; the spec requires that a coordinator can restart from `state.yaml` plus `decisions.tsv` and re-run only the incomplete batches.

## 8. Recommended 0.7.0 scope

- **Shared infrastructure, built first and tested alone:** the scope router script, the worker contract and batch checker, the decision log, one plugin agent definition for workers, the harness changes that let graders see workers, and the rule → enforcer table.
- **Pilot on pe-review**, with an A/B before fan-out is the default. Then tag-audit-and-takeoff, then submittal-review's migration. submittal-log-generator gets no fan-out work: one measured run of a full manual without workers decides whether its unexercised parallel paragraph is deleted.
- **The pstack items marked Port in §6.2**, each as a small, separately gradable change.
- **Not in 0.7.0:** a router skill, separate-session execution inside any skill, standing per-discipline agents, lateral worker messaging, new construction-administration skills (document-set-audit and revision-history stay on the roadmap and consume this infrastructure when they are built).
- **Base:** `main` after PR #28 (release/0.6.0) merges; the spec assumes 0.6.0's layout throughout.

The specification with requirement IDs, guardrails, evals and pre-ship checks is `0.7.0-dev-spec.md`.
