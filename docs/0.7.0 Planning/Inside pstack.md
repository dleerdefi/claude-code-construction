Inside pstack

1. [Overview](#top)
2. [How it fits together](#map)
3. [Anatomy of a skill](#anatomy)
4. [The skills](#skills)
5. [The playbooks](#playbooks)
6. [The principles](#principles)
7. [Models and subagents](#models)
8. [Scripts](#scripts)
9. [How she drives it](#driving)
10. [Her philosophy](#philosophy)
11. [Is it best practice?](#verdict)
12. [Build your own](#yours)
13. [History and sources](#history)

A research report · pstack v0.15.25 · updated 14 Oct 2026 · [what changed](#history)

# pstack

"if you want to go fast, go deep first."

pstack is the set of agent skills Lauren Tan (poteto) built at Cursor and still uses every day. She is on the React Compiler core team, worked at Meta and Netflix, and since August 2026 has worked on Grok Bot at SpaceXAI, after SpaceX acquired Cursor. The pack is built around one router skill, `/poteto-mode`, which picks a playbook for your task and pulls in the other skills as each step needs them. Her README states the goal: "the goal is not to maximize loc, in fact it's the opposite. pstack helps you write less, but higher quality code." This report reads every file in the pack and explains how each skill is built, why it is built that way, and which parts are worth reusing.

**54**SKILL.md files

**23**playbooks in the router

**24**one-rule principles

**2**subagent definitions

**\~7k**lines of Bun/TS scripts

**129**commits since 22 May 2026

#### Where it lives

The public copy lives only at [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack), MIT licensed, and installs with `/add-plugin pstack`. Commits #156, #329 and #414 port changes from Cursor's private skill tree, so the public repo is a cleaned-up mirror of an internal original. Her personal GitHub has no separate copy, but its ancestors live there: [noodle](https://github.com/poteto/noodle), [brainmaxxing](https://github.com/poteto/brainmaxxing) and [how](https://github.com/poteto/how).

#### What "skill" means here

Every skill is a folder with a `SKILL.md` (YAML frontmatter plus Markdown), optionally with `references/`, `scripts/` or `playbooks/` next to it. This is the open Agent Skills format, the same one Claude Code reads. The orchestration parts (subagents with a model per role, Custom Modes, `/loop`, cloud agents) depend on Cursor features.

#### How to read this page

Start with the map and the anatomy section to see how the pack is put together. The skill and playbook explorers are reference: click any row. The last four sections cover her habits, her stated philosophy, an assessment, and a list of ideas to copy into your own pack.

How it fits together

## One router, many playbooks, a small set of multi-agent workflows

You type a goal and a check that can pass or fail. The router chooses a playbook. The playbook's steps call the workflow skills, those fan out to subagents running on the model assigned to each role, and every result has to be proven on the real app before it becomes a PR.

Subagents spawned inside playbook steps run as `poteto-agent`, which loads poteto-mode before doing anything. The workflow skills set their own `subagent_type` and model so that reviewers come from different model families.

Anatomy of a skill

## How the files are shaped

pstack's skills follow a few strict conventions. These conventions carry most of the design, so they are the part to copy if you build your own pack.

\# the entire SKILL.md of principle-encode-lessons-in-structure --- name: principle-encode-lessons-in-structure 1 description: "Apply when you catch yourself writing 2 the same instruction a second time, or notice a recurring correction. Encode the rule as a lint, metadata flag, runtime check, or script instead of more text." disable-model-invocation: true 3 --- # Encode Lessons in Structure If the lesson needs judgment and cannot be 4 encoded, make the instruction more prominent and add an example of the failure mode. \*\*Corollary:\*\* If the fix is structural, only use the structural fix. The instruction is the symptom.

1

**The name is the folder name and the citation key.** Other skills refer to it as "the **encode-lessons-in-structure** principle skill" and never paste its text.

2

**The description holds the trigger and the rule.** It reads "Apply when …", then the rule. For many principles the description is most of the content, so the router's index can quote it.

3

**53 of the 54 skills set `disable-model-invocation: true`.** No skill loads just because a word in your prompt matched. A skill runs only when you type it or when poteto-mode's steps call it. The one exception is `setup-pstack`.

4

**The body adds only what the description can't hold.** This file is 34 words long. Commit history shows repeated passes that deleted sentences newer models no longer need: #329 cut 633 lines, #419 cut "19 more instructions Opus 5.5 does not need", and #538 cut 736 lines.

skills/why/ (a multi-agent workflow skill) SKILL.md # orchestrator: who to spawn, which model references/ epistemics.md # 5 confidence tiers + banned words investigator-prompt.md # template with {PLACEHOLDERS} synthesizer-prompt.md # template with a fixed output order source-playbook.md # category → playbook index sources/ code-archaeology.md # git -S, -G, --follow, blame linear.md notion.md slack.md datadog.md sentry.md databricks.md incident-postmortem.md # added for defensive code

A

**SKILL.md orchestrates and `references/` holds what subagents read.** The SKILL.md says when to spawn which subagent and with which role model. Each reference file is named for the subagent that receives it (explorer-prompt, runner-prompt, judgment-reviewer) and starts with a one-line note to the orchestrator.

B

**Every subagent ends with a fixed output contract.** Exact headings and a per-item schema, shaped for the next stage to consume. Investigators are told "Gather, don't conclude." One synthesizer reconciles their findings and spot-checks their citations.

C

**Uncertainty is written down, not left out.** Empty searches, skipped sources with reasons, and gaps are required output. The epistemics file says: "If no gaps are mentioned, that's suspicious."

#### Playbooks start with a stance and end with a reply contract

Each playbook opens with one bold line saying what you own ("You own the contract. The structure changes. The behavior does not."), then numbered steps, then **Reply:** listing exactly what the final message must contain.

#### The steps go into the todo list first

poteto-mode copies the matched playbook's steps verbatim into the todo list. architect, arena, swarm and figure-it-out each open a todo per phase. A skipped step stays visible as `skip: <reason>`.

#### Models are named by role

Skills ask for roles such as "how explorer" or "arena runners", which `pstack-models.mdc` maps to slugs. Every skill also says what to do when a slug is rejected: fall back to the family default, say so, and keep going.

#### Rules carry stable IDs

unslop's rules are numbered, and a removed rule leaves a gap in the numbering so citations like "unslop rule 14" never point at the wrong rule. Principle and skill names serve the same purpose.

#### Scripts enforce the rules that matter most

Where the prose says "run X", X is a deterministic tool. `check-plan.mjs` lints plans, `watch-pr` returns typed verdicts, `log.sh` writes well-formed TSV rows. The prose stays short because the scripts do the checking.

#### Outside input is labeled untrusted

Transcripts, Bugbot comments, reviewer output and webhook bodies are all labeled "untrusted data". Reply text is never interpolated into a shell command. Transcript reads are limited to the active workspace.

The skills

## Every skill, how it works, and what it teaches

30 task skills plus the two subagent definitions. Each entry covers what the skill does, how it runs step by step, its files, the rules from its text worth quoting, and a design lesson for writing your own. The 24 principle skills have their own section further down.

The playbooks

## 23 playbooks inside `/poteto-mode`

Playbooks are not skills. They have no slash command and live as Markdown files under `poteto-mode/playbooks/`. The router matches your task to one of them, and you can also name one with phrases like "babysit this pr", "land the stack" or "full autopilot on this queue". The word counts show how much each one costs to load.

The principles

## 24 rules, one per file

She calls these "perhaps one of the most durable parts of pstack" and expects most of the other skills to "compress into short principles or workflows" as models improve. Many "were extracted from my sessions correcting agents since the start of this year" (X, 14 Oct). On 14 Oct four of them were rewritten from rules into reasoning (#633); the cards below show the new wording. poteto-mode keeps an inline index of these principles, each written as "when it applies" plus the rule. Before applying one, the agent opens its leaf file. Its reply must name each principle that changed a decision, so a principle mentioned with no decision behind it is easy to spot. In everyday use you don't invoke principles. You steer with their names: "apply prove it works. show me the real output."

Models and subagents

## Assign each role the model that suits it

pstack uses different models for different jobs. Fast code models do the reading and the mechanical edits. A strong judgment model writes, judges and handles the hardest changes. Reviews always pair different model families, because "agreement is high-signal."

| Role line in pstack-models.mdc | Default |
| --- | --- |
| feature, refactoring · bug-fix · perf-issue · hillclimb | `grok-4.7-xhigh-fast` |
| judgment and prose · hardest tasks | `claude-opus-5-5-xhigh` |
| how explorer · why investigators · reflect tooling · swarm workers | `grok-4.7-xhigh-fast` |
| how explainer · why synthesizer · reflect judgment, divergent, synthesizer | `claude-opus-5-5-xhigh` |
| arena runners · architect runners · interrogate reviewers · arena cross-judge pool | Opus + Grok (a list: one subagent per entry) |

#### The subagent rules in poteto-mode

- **Defaults for every spawn.** Background, agent mode (read-only mode removes MCP access), file pointers instead of pasted context, and an explicit model.
- **Match the model to the job.** new in 0.15.24 Each spawn starts from its role's model, then moves only the effort level and speed. One step up for the hardest work, one down for judgment, two or more down for routine work. Fast mode only when CI or trunk is red or someone is blocked right now. Verification stays on the swarm model. The family never changes, "so a diverse panel stays diverse."
- **Fresh subagents by default.** A fix round, a retry or the next queue item goes to a new agent with the consolidated brief. Resume an old agent only when it holds state that is costly to move, such as a checkout, uncommitted changes or a running dev server. "Interrupt-chained resumes silently drop directives."
- **You own their work.** Review the diff and write your own summary instead of passing theirs along.
- **Review separation is mandatory.** Feature work with several valid shapes must go through arena, and the Laziness Protocol cannot waive this.
- **Judges come from another family.** Arena's judge and show-me-your-work's trail reviewer must come from a different model family than the author.

| Pattern | Where | Shape | Why it works |
| --- | --- | --- | --- |
| Explore → explain | how | 2–4 read-only explorers on angles → 1 explainer | Cheap models do the reading; one strong model writes the explanation. |
| Investigate → synthesize | why, recall, reflect | 1 agent per evidence source → 1 synthesizer | One agent per source means no source gets skimmed; nulls become findings. |
| Bakeoff + graft | arena, architect, eval | N runners on one brief → blind cross-family judge → base + grafts | The rubric is hidden from candidates and the judge sees only labels, so the comparison stays fair. |
| Coverage / race | swarm, shipping, plans | N cloud workers on slices or a race → one table | A result without its SHAs is a gap, and a gap is never a pass. |
| Adversarial panel | interrogate | 1 reviewer per model → lead buckets findings | The variety comes from different models, not personas. The lead filters out padding and nitpicks. |
| Author ≠ critic | no-comments, shipping | Separate agent judges the author's output | "An author defends its comments the way you'd defend yours." |

Scripts

## The rules that run as code

About 7k lines of Bun and TypeScript under `poteto-mode/scripts/`, with \~63 tests and a strict typecheck. Each script replaces a rule the agent might otherwise forget. This is the pack applying encode-lessons-in-structure and build-the-lever to itself.

| Script | Used by | What it enforces |
| --- | --- | --- |
| `check-plan.mjs` | Multi-phase plan, step 6 | Lints a plan file: no long dashes, curly quotes or mid-sentence colons; the fixed skeleton in order; the verification sentence word for word; exactly ten live lanes, each with a screenshot and a pass condition; perf boxes Metric/Probe/Baseline/Rule. Exits 1 on any problem. |
| `watch-pr` | Babysit, Shipping | Polls GitHub and returns a typed verdict with exit codes: READY/COMPLETE (0), BLOCKER on conflicts (2), review threads (3), failing checks (4), merge gate (6), query failure (7), TIMEOUT (5). It counts Bugbot passes, which drives "lean toward dismissing from the third pass". A Code Review Gate waiting on an owner's approval counts as that gate, not a failure, so the watcher never sits waiting on a human. |
| `orch` | Orchestrate | File-based bookkeeping, "one command in and one line out": units.tsv, a verification ledger keyed by PR + head SHA (a new SHA voids the verdict), inbox, gates, frontier, standing orders. It never spawns agents. A PID-based lock heals itself after a crash. Since 0.15.24 the frontier is read from the PR base chain through `gh` or Origin. Graphite is no longer needed. |
| `worktree-audit.sh` | Worktree cleanup | Read-only. Gets paths from `git worktree list`, never from hand-typed paths, reads PR state from Origin when it can and from `gh` otherwise, and sorts each worktree into hold-wip / hold-open-pr / verify-recent-chat / safe / review. "The bucket is advice, not permission." |
| `log.sh` | show-me-your-work | Appends a timestamped TSV row, strips tabs and newlines, and prefixes cells starting with = + - @ so the log can't inject spreadsheet formulas. |
| `bootstrap.ts` | watch-pr, orch | Installs the scripts' one dependency, keyed by a hash of package.json + bun.lock, so a rerun does nothing. Skills never need to say "npm install first". |

How she drives it

## Short prompts with a check that can pass or fail

The guide (`docs/guide/`, ten pages) and `poteto-help/references/prompting.md` describe how she prompts. Her prompts are lowercase and conversational. They name the goal and how to tell it's done, and never the method.

#### Five things a prompt carries

- **The goal.**
- **A done check that can pass or fail.** "Make it better" and "work on it for an hour" are not checks.
- **The proof you want to see.**
- **What you already know** (job IDs, the failing fixture).
- **Real constraints**: "repro first", "don't change any code yet", "zero behavior change", "bugs included", "byte-identical".

**Leave out** the list of skills ("a hand-written sequence usually reorders or drops steps the playbook would have kept") and your theory of the cause ("a stated guess narrows the search to wherever you pointed").

#### All five in one prompt

/poteto-mode the csv export drops its last row since yesterday's deploy. failing job id is 4812. repro first, then fix. done means the 60k-row fixture exports every row. show me the row counts before and after.

#### Follow-ups stay short

/poteto-mode do it continue /poteto-mode new task. figure out why the cache entry survives logout. don't change any code yet.

#### The overnight contract

/poteto-mode im going to bed. \[1\] migrate every caller to the new parser in a fresh worktree off \<base>. \[2\] done means zero old callers, all parser fixtures pass, old api deleted. \[3\] keep a decision log. don't ask me before committing. \[4\] /loop until done. if you're truly stuck after a few hours, stop and write up why. \[5\]

**\[1\]** A session override that stops it asking. **\[2\]** Isolation. **\[3\]** A check every iteration can run. **\[4\]** A trail to audit and a permission granted up front. **\[5\]** A wake mechanism plus a way out, which "beats eight hours of creative goal reinterpretation."

#### Earn trust before you loop

- You've done the task once by hand, or watched an agent do it.
- The agent has your tools and signals: a verify skill, a profiler, logs.
- Every stage proves its work and can stop the line.
- You've read transcripts and turned repeated failures into tools, skills or checks.

Until all four hold, "run it while you watch." In the morning: `/show-me-your-work catch me up on what you did last night`, reading the cross-model Attention section first.

#### The design ladder

- Unsure about a small finished change → `/interrogate`.
- A change that crosses a function boundary → `/architect`, which runs arena.
- A standalone decision (naming, a format, an algorithm) → `/arena`.
- A coverage matrix → `/swarm`.
- A question you can answer by running something → a prototype.
- A contested design that's expensive to reverse → architect, then interrogate.
- Work across several PRs → a plan, written last.

"Most changes need none of it." Also: "`/interrogate` belongs on a diff." Reviewing an abstract plan makes reviewers "invent theoretical risks and edge cases that will never happen."

#### One-line steers

i said the goal is to repro. i did not ask for a fix yet. apply prove it works. show me the real output, not the build log. use subtract before you add. delete the obsolete adapters first. /teach me why you implemented it this way and not with a queue. /unslop that, no emdashes /bro

#### Pitfalls she lists

Listing skills in the prompt. A vague finish condition. Leading with your theory. Taking the first design. Polishing an abstract plan. Parallel agents in one worktree. Looping before you trust the loop. Trusting an unvetted number. Correcting the same mistake by hand. Accepting every review comment. Reporting success off a green build.

#### The investment she ranks first

From guide page 1: "Of everything in this guide, the verification skill pays off the most. An agent that can check its own work keeps going until the check passes. An agent that can't hands every result back to you." Run `/create-verification-skill` once per repo, then name it in prompts: `use /verify-<app> to verify your changes and show me a video and screenshots as proof.`

Her philosophy

## What she says, in her own words

These quotes come from her X posts and long-form X articles (March to October 2026). Read her productivity numbers knowing that she promotes Cursor and Grok Bot.

> "It's agent orchestration, but applied depth first rather than breadth first." … "Naive parallelization just makes them write slop faster."
> 
> "How I Use Cursor", 25 May 2026

> "Agents are like new hires in a constant state of amnesia and idiocy... They're capable yet stupid, and very teachable."
> 
> "How I Use Cursor", 25 May 2026

> "The bottleneck with agents is verification." … "'I fixed it' isn't good enough. Show me the failing test and the passing test. Show me the before and after video."
> 
> "How I Use Cursor" and "Loops You Can Trust", May–June 2026

> "I never set out to build pstack... I just started turning every recurring failure mode into a skill... The agents improved because their instructions carried the scars from previous runs."
> 
> "Loops You Can Trust", 24 Jun 2026

> "every time you intervene and correct your agent, you should think about how to eliminate it entirely. in order of value: 1. categorically eliminate the problem through better architecture or choice of data structures 2. turn it into a lint rule or test so CI catches it 3. turn it into a skill or rule 4. have humans review the code to catch it (ngmi)"
> 
> X, 16 Aug 2026 (later became `/correct`)

> "The truth is that I do plan, but I do so through code." … "Prototyping is planning, but with code." … "abstract plans only give you the illusion of progress."
> 
> "The Complete Guide to pstack Pt. 2", 9 Sep 2026

> "the thing about loops is that you need to build trust first. a low trust loop is just a waste of tokens. and if you don't apply engineering taste, the slop really compounds."
> 
> X, 8 Jun 2026

> "ban and delete most if not all code comments! agents love copying what already exists. a seemingly harmless comment explaining some temporary workaround is one of the worst viruses you can have in your codebase."
> 
> X, 13 Oct 2026

> "i love writing. i never let agents write for me... i still strongly believe that writing is thinking."
> 
> X, 13 Oct 2026

> "as models get smarter, i expect most of pstack skills to compress into short principles or workflows (a generic list of steps) and that i will be able to delete a few of them."
> 
> X, 14 Oct 2026

#### The themes, distilled

- **Trust first, parallelism second.** Go deep with one agent until its output can be verified, then run many. Trying to parallelize agents you don't trust "is a huge waste of tokens."
- **Verification is the product.** Her Pt. 1 guide is titled "Verification is all you need." She calls a verification skill "more like critical infrastructure."
- **The codebase is the memory.** "I think your codebase is the ultimate form of memory." Agents copy what exists, so the fix is to make the wrong path impossible, not to document it.
- **Supervise like a manager.** "Loops You Can Trust" draws on Andy Grove's *High Output Management*: do it by hand first, give agents your tools, make every stage prove its work, read the transcripts.
- **Use models for what they're good at.** "if you like opus (i think it's a great manager of agents), you can use it to orchestrate all your other models."

#### The numbers, and how far to trust them

"shipped almost 1000 PRs this month" (29 Jul). "Merged and shipped 221 PRs in 2 days" (7 Aug). "here's how i shipped 2,500 PRs last month" (21 Sep talk). Her guide says about 2,000 a month. These figures are self-reported and not audited, and they don't agree with each other. She told Matt Pocock "They're not obviously like 2,500 features", and full autopilot is "quite token intensive."

She also wrote (11 Oct) that maintainability and clean code still mattering is something "i would argue … is no longer true," defining good code as "correct, bug free, fast and cost efficient to run." That sits uneasily next to pstack's own *minimize-reader-load* principle. One way to reconcile them: in her view the reader who matters most is now the next agent, and the code should make the wrong path impossible for it.

Is it best practice?

## An assessment

My read after going through all 54 skills, the scripts and the history. The ideas are strong and travel well. The full orchestration is expensive and partly tied to Cursor.

Strong, copy these

- **Evidence is required at every step.** Labeling claims as measured, inferred or guess, blast-radius's five-rung ladder, why's confidence tiers, and "a gap is never a pass" give a reviewer something concrete to check in every output.
- **The author is never the critic.** Comment Sicko, cross-family judges, an independent verifier for every PR before landing, and a second-model review of the decision trail.
- **Rules become structure.** /correct's ladder, scripts like check-plan and watch-pr, and the rule → enforcer table put the important rules into code instead of more prose.
- **Skills are short and get shorter.** Repeated cut passes, each checked against the skill's behavior, and a principle file can be 34 words. She treats a skill as finished when there is nothing left to remove.
- **Nothing loads by surprise.** Explicit invocation plus one router keeps the context small and makes behavior predictable.

Costs and caveats

- **Tokens.** Panels, swarms of ten live lanes per PR, and cross-model reviews add up. One tester (cited by The Neuron) reported about 30 minutes without pstack versus about an hour with it, though the pstack run caught three false claims.
- **Ceremony for small tasks.** Flavio Copes: "That is sometimes more ceremony than a task needs." The router does offer skips (`skip: <reason>`, "most changes need none of it"), but the playbooks lean heavy.
- **Written prose only guides.** Only the scripts actually enforce anything. The rest relies on the model obeying, which is why she keeps moving rules into code.
- **One person's style.** It encodes her habits, her models (Opus 5.5 + Grok 4.7) and her stack (GitHub or Origin, Bugbot; Graphite was dropped in October). Her answer is `/automate-me`: build your own mode on top.
- **Productivity claims are self-reported**, and she has a commercial interest in Cursor and Grok Bot.

Porting to Claude Code

The SKILL.md format carries over unchanged. The orchestration needs translating. A community port, [michael-denyer/pstack-claude](https://github.com/michael-denyer/pstack-claude) (\~2k stars), already targets Claude Code, Codex and others, and so does [backnotprop/pstack](https://github.com/backnotprop/pstack) (\~1.9k stars, Claude, Codex and pi). Both were updated on 14 Oct. One review notes its reviewers differ "by separate context, not by model family." That is the main thing lost in a port.

| pstack (Cursor) | Closest Claude Code equivalent | Notes |
| --- | --- | --- |
| `skills/<name>/SKILL.md` + `disable-model-invocation` | `~/.claude/skills/` or `.claude/skills/`, same frontmatter | Copies over as is. Change references to Cursor tools. |
| `agents/poteto-agent.md`, `comment-sicko.md` | `.claude/agents/*.md` (name, description, tools, model) | Same idea: a thin agent definition that loads the router first. |
| Task tool with a model slug per role | Agent tool with `subagent_type` and `model` | Model choice is limited to Claude tiers. For cross-family review, shell out to another vendor's CLI, or accept reviewers that differ only by context. |
| `environment: "cloud"`, worktrees | Agent `isolation: "worktree"` or `"remote"` | Same rule: one writer per worktree. |
| `pstack-models.mdc` (alwaysApply rule) | `CLAUDE.md` lines, or `model:` in agent frontmatter | Keep the role names. Each skill reads its role and falls back to a default. |
| Custom Mode (Option+Enter) | Invoke the router skill per task, or point to it from `CLAUDE.md` | There is no exact equivalent to a mode that stays on. |
| `/loop` | `/loop` | Same rule applies: loop on a check that can pass or fail, never on a duration. |
| `agent-transcripts/` | `~/.claude/projects/<slug>/*.jsonl` | For reflect, recall, automate-me, and auditing show-me-your-work. |
| `create-skill` (Cursor built-in) | skill-creator skill | Includes eval and description-tuning loops. |
| `control-ui` / `control-cli`, `/deslop` (cursor-team-kit) | Playwright CLI, tmux; write your own deslop skill | Your global `playwright-cli` skill plus per-project `browser-checks` already cover what a `verify-<app>` skill does. |

Build your own

## What to copy, in the order I'd copy it

Ordered by how much each idea pays back for the effort, based on her ranking and on which skills the rest of the pack depends on.

1. **Give every app a scripted way to prove behavior.** Launch, Doctor, Drive, Evidence and Cleanup sections, plus a feature map with one file per feature. She ranks this as the best investment in the guide, and the whole pack's definition of "verified" depends on it.
2. **Require evidence in every reply.** Copy poteto-mode's reply rules: label every claim measured, inferred or guess, "never hand the human a check you could run", and paste failing-then-passing output verbatim.
3. **Put author and critic in separate agents.** Start with a comment-stripping critic and a judge who never sees model names. Use a different model whenever you have one.
4. **Write one router and small playbooks.** Each playbook gets a stance line, numbered steps copied into the todo list, and a **Reply:** contract. Your own `-mode` skill can start with three playbooks: investigation, bug fix, feature.
5. **Turn repeated corrections into structure.** Use /correct's ladder (architecture, then types or a lint whose error names the fix, then a test, then docs) and keep a rule → enforcer table in CLAUDE.md. A rule that nothing enforces counts as a repeat.
6. **Make skills explicit-only and put the rule in the description.** Use `disable-model-invocation: true` by default and write "Apply when … " followed by the rule, so an index can quote it.
7. **Have SKILL.md orchestrate and keep subagent prompts in `references/`.** Give each subagent a fixed output contract the next stage consumes. Workers gather evidence and a single judge draws the conclusions.
8. **Keep a decision trail for unattended runs.** An append-only TSV with an evidence column, checked against the transcript at the end and reviewed by a second model.
9. **Prune and evaluate.** Delete instructions the current model follows without being told. Test skill changes blind: organic prompts, sanitized directories, and grading from transcripts instead of self-reports.
10. **Start smaller than you think.** Her guide: add a skill or check "when the same failure shows up twice." pstack grew out of her earlier repos `brainmaxxing`, `noodle` and `how`, with each recurring failure turned into a skill.

History and sources

## How it got here

Dates come from the cursor/plugins commit history (129 commits touch `pstack/`, 123 by her) and from her posts.

1. Feb–Apr 2026

   The predecessors live in her personal GitHub. [brainmaxxing](https://github.com/poteto/brainmaxxing) (principles such as encode-lessons-in-structure and prove-it-works, plus a reflect skill), [noodle](https://github.com/poteto/noodle) ("Orchestrate agents using skills", already shipping unslop and adversarial-review), and [how](https://github.com/poteto/how). She joins Cursor from Meta at the end of March.
2. 22–25 May

   "Add pstack plugin" lands in cursor/plugins: 74 files, 18 principles. The launch article "How I Use Cursor" follows on 25 May.
3. May–Jun

   Versions 0.2–0.9. Multi-model `/interrogate`, `/setup-pstack` with per-role models, the hillclimb playbook. "Loops You Can Trust" is published on 24 June.
4. Jul

   create- and maintain-verification-skill, swarm. Review panels briefly default to three models (Fable, Sol, Grok).
5. Aug

   0.13–0.14. Autopilot playbooks, /no-comments with Comment Sicko, /technical-writing, babysit, shipping, orchestrate, bro. She starts at SpaceXAI on 17 August, after SpaceX's acquisition of Cursor's maker.
6. Sep

   0.15.0 removes em dashes and mannered prose from the skills and adds attack-the-premise and test-behavior-not-implementation. Defaults move to Opus 5.5 + Grok 4.7. Guides Pt. 1 and 2 and her talk ("how i shipped 2,500 PRs last month") come out.
7. Oct

   /correct, /benchmark-checklist, /poteto-help, /ketchup. Sol is dropped from the panels and default effort moves from max to xhigh. "pstack is now 10% smaller with no loss in behavior." 0.15.23 adds /in-your-own-words on 13 October.
8. 13–14 Oct

   0.15.24 and 0.15.25. [/sharpen](https://github.com/cursor/plugins/pull/615) arrives, three draft skills folded into one. [#613](https://github.com/cursor/plugins/pull/613) gives each subagent an effort level and speed matched to its job, cuts shipping and both autopilot playbooks down to their rules with a reason for each, runs one full swarm per PR instead of one per push, and removes Graphite. The autopilots now report through [/ketchup](https://github.com/cursor/plugins/pull/616), which [#628](https://github.com/cursor/plugins/pull/628) teaches to explain changes with screenshots, videos and diagrams. [#633](https://github.com/cursor/plugins/pull/633) rewrites four principles (attack-the-premise, fix-root-causes, test-behavior-not-implementation, make-operations-idempotent) from specific mechanisms into the reasoning behind them, so an agent can handle cases the text never names.

#### Does she have a personal pstack repo?

No. The only copy is cursor/plugins (she has a working fork at [poteto/plugins](https://github.com/poteto/plugins)). pstack is also listed as a Grok Bot plugin. Related public repos: [poteto/verification-skill-example](https://github.com/poteto/verification-skill-example), a large worked example of a verification skill and feature map. Her X bio now reads "Grok @Bot at @SpaceXSI. Shipping with pstack … prev cursor, meta, netflix".

### Sources

- Source: [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack) at v0.15.25 (every SKILL.md, reference, playbook, script and guide page was read for this report; the 0.15.24–0.15.25 changes were read as diffs)
- Pull requests [#613](https://github.com/cursor/plugins/pull/613), [#615](https://github.com/cursor/plugins/pull/615), [#616](https://github.com/cursor/plugins/pull/616), [#628](https://github.com/cursor/plugins/pull/628) and [#633](https://github.com/cursor/plugins/pull/633), 13–14 Oct 2026
- [pstack guide](https://github.com/cursor/plugins/tree/main/pstack/docs/guide), pages 01–10
- ["How I Use Cursor"](https://x.com/poteto/status/2058975157503570132), 25 May 2026
- ["Loops You Can Trust"](https://x.com/poteto/status/2069824386283319343), 24 Jun 2026
- ["The Complete Guide to pstack Pt. 1: Verification is all you need"](https://x.com/poteto/status/2094457600259842065), 31 Aug 2026
- ["Pt. 2: The art of supervising someone smarter than you"](https://x.com/poteto/status/2097732320606507506), 9 Sep 2026
- [Talk video, "how i shipped 2,500 PRs last month"](https://x.com/poteto/status/2102050467505430555), 21 Sep 2026
- [Matt Pocock live interview](https://www.youtube.com/watch?v=MN9dGgmLyso), \~2 Oct 2026
- [Correction-ladder post](https://x.com/poteto/status/2089067865098113024), 16 Aug 2026
- [Workflow-in-brief post](https://x.com/poteto/status/2090141955695198633), 19 Aug 2026
- [Comments-as-viruses post](https://x.com/poteto/status/2110149626133438732), 13 Oct 2026
- [Principles post](https://x.com/poteto/status/2110496830429839869), 14 Oct 2026
- [poteto/noodle](https://github.com/poteto/noodle), [poteto/brainmaxxing](https://github.com/poteto/brainmaxxing), [poteto/how](https://github.com/poteto/how)
- [garrytan/gstack](https://github.com/garrytan/gstack), whose README pstack's README answers point by point
- [Flavio Copes on pstack](https://flaviocopes.com/pstack) (ceremony and cost)
- [The Neuron explainer](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/)
- [Redreamality talk write-up](https://redreamality.com/blog/lauren-tan-poteto-trust-before-parallel/) (from auto-captions)
- [alexop.dev on pstack playbooks](https://alexop.dev/posts/pstack-playbooks-as-factories/)
- [michael-denyer/pstack-claude](https://github.com/michael-denyer/pstack-claude) and [backnotprop/pstack](https://github.com/backnotprop/pstack), community ports

X was read through an API mirror because x.com blocks direct fetches. Reddit was not searchable, and the "10,000 agent runs a week" usage figure on a Cursor landing page could not be verified, so neither is used here.

Compiled 13 October 2026 and updated 14 October 2026 from the pstack source at v0.15.25 and public posts. pstack is MIT licensed, © Lauren Tan. Quotes are reproduced for commentary. This page is not affiliated with Cursor, xAI or SpaceX.