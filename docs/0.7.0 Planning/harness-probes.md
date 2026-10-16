# Harness probes for the 0.7.0 fan-out design (V-1, V-2, V-3, V-4, V-10)

Measured 2026-10-15 on this machine (Windows 11, native Claude Code 2.1.288 at `~/.local/bin/claude.exe`, `claude-agent-sdk` 0.2.163 in the toolkit venv, Sonnet coordinator, Haiku worker). The spec is `0.7.0-dev-spec.md` on branch `claude/code-construction-skills-arch-fead54`, sections 5 and 8.

**Verdict in one line: all five confirmed.** The 0.6.0 harness's guard already covers a worker's Bash, Write and Edit calls; the session cost already includes the worker; the worker's transcript is on disk at the documented path; a plugin-shipped agent is spawned as `construction:<name>` and `claude plugin validate --strict` accepts the manifest's `agents` list; and a worker's `tool_use` and `tool_result` blocks reach the SDK stream by default, tagged with the spawning Agent call's id. Nothing stops the spec. One thing the spec assumed is wrong in the other direction (F8, below): the harness trace *already* holds every worker call, unlabelled, so any `Agent`-granting case whose run spawns a worker is graded on the worker's calls today.

## The probe

- Worktree note: this branch (`claude/pensive-allen-1a706a`) was cut from `main` (c8089c9, v0.5.1), not from `release/0.6.0` as the brief said. It had no commits of its own, so it was fast-forwarded to `release/0.6.0`'s tip (aaae1d4, "harness: record what the judge's calls cost") before anything ran. Nothing was pushed; PR #28 is untouched. Everything below is measured against the 0.6.0 harness.
- Case: `evals/plugin/_probe-fanout/` (the leading underscore keeps `run.py` from ever loading it). `prompt.md` has a Sonnet coordinator spawn one `construction:probe-worker` agent on Haiku, in the foreground, with a five-step prompt: `cat probe-input.txt` (Bash, inside), write `workers/01/worker-note.txt` (Write, inside), write `/tmp/probe.txt` (Write, outside), `echo … > "$HOME/probe-outside.txt"` (Bash, outside), and Edit an existing file in the system temp folder (outside). `prompt-noworker.md` is the same run with the coordinator doing the two inside steps itself. `setup.sh` writes one input line; no fixture, no venv link. `harness.yaml` caps a run at $0.60.
- Script: `evals/plugin/_probe-fanout/probe.py <worker|worker-forward|noworker>` drives the harness's own `runner.run_case` and patches three observers around it without changing what the harness does: an extra `PreToolUse` hook ahead of the guard that keeps every hook input in full; a tee on the SDK stream that keeps each message's class, `parent_tool_use_id` and blocks, the `init` message, and the result's `session_id`, `usage` and `model_usage`; and, for `worker-forward`, `forward_subagent_text=True` on the session options. After the session it lists the transcript folder, checks every outside path the worker was told to write, and writes `evals/results/probe-fanout/<stamp>-<arm>/` (`trace.jsonl` as the harness wrote it, `guard_log.json`, `stream.jsonl`, `hook_inputs.json`, `init.json`, `summary.json`).
- Agent, present only during the runs and removed after: `agents/probe-worker.md` with frontmatter `name: probe-worker`, a description, `tools: Read, Bash, Write, Edit` (the brief said Read, Bash, Write; Edit was added so V-1 could see an Edit denial), `model: sonnet`; the manifest carried `"agents": ["./agents/probe-worker.md"]`. The coordinator overrode the model to `haiku` on the Agent call so V-2 could see the worker's spend under its own model key.
- Runs, one per foreground command under the heavy-job lock (taken 23:47, released 23:52):

| Arm | Stamp (results folder) | Turns | Wall | Cost | Sonnet | Haiku (worker) |
|---|---|---|---|---|---|---|
| worker (first) | `2026-10-15T23-48-39-worker` | 3 | 46 s | $0.0681 | $0.0504 | $0.0177 |
| worker-forward | `2026-10-15T23-49-50-worker-forward` | 3 | 34 s | $0.0658 | $0.0521 | $0.0137 |
| noworker | `2026-10-15T23-51-43-noworker` | 4 | 19 s | $0.0433 | $0.0433 | none |
| worker (second, Edit on an existing file) | `2026-10-15T23-52-29-worker` | 2 | 34 s | $0.0735 | $0.0599 | $0.0136 |

The first worker run's Edit targeted `../probe-edit-outside.txt`, which did not exist; the Edit tool rejected it ("File does not exist") before any hook ran, so that run shows Bash and Write denials only. The second worker run gives the Edit a file that exists and is the run cited below unless stated.

## V-1: the guard fires for a worker's Bash, Write and Edit calls. Confirmed.

`guard_log.json` of the second worker run, in order (the hook input's `agent_id` and `agent_type` attribute each entry):

```
Bash  ALLOW  cat probe-input.txt                                   agent_id=a46d1aa859af918dd agent_type=construction:probe-worker
Write ALLOW  C:\…\_probe-fanout-20261015-235155-r1\workers\01\worker-note.txt   (worker)
Write DENY   \tmp\probe.txt            Blocked by the eval guard: writes outside the workspace are not allowed (\tmp\probe.txt)   (worker)
Bash  DENY   echo outside-bash-by-worker > "$HOME/probe-outside.txt"
             Blocked by the eval guard: the command names '$HOME/probe-outside.txt', which is outside the workspace, the plugin and the temp dir   (worker)
Edit  DENY   C:\Users\leerd\AppData\Local\Temp\probe-edit-outside.txt
             Blocked by the eval guard: writes outside the workspace are not allowed (C:\Users\leerd\AppData\Local\Temp\probe-edit-outside.txt)   (worker)
Write ALLOW  C:\…\_probe-fanout-20261015-235155-r1\coordinator-report.md        agent_id=None (the coordinator)
```

- Every worker call to a guarded tool reached the harness's `PreToolUse` hook: five worker entries plus the coordinator's one, six hook inputs, six guard decisions. The first worker run and the forward run show the same pattern with four worker entries each (no Edit, see above).
- The denials took effect. After each worker run: `~/probe-outside.txt` absent, `C:\tmp\probe.txt` absent, `%TEMP%\probe.txt` absent, and the temp-folder edit target still read `a`. The 0.6.0 harness's own leftovers check (`outside_files`) reported nothing in every run. The worker's own report lists steps 3, 4 and 5 as DENIED with the guard's reason text; the worker saw the Write denial as the tool result `Blocked by the eval guard: …` and the Bash denial as `PreToolUse:Bash hook error: Blocked by the eval guard: …`.
- The hook input for a worker's call carries `agent_id` (the id in the transcript file name), `agent_type` (`construction:probe-worker`), `parent_agent_id` (`null` at depth one), `session_id`, `cwd` (the workspace), `permission_mode` (`acceptEdits`) and `transcript_path`. A coordinator call has `agent_id` and `agent_type` `null` and an extra `effort` key. So `guard_log.json` can name the agent with a one-line change to `guard_hook` in `runner.py` (record `agent_id` and `agent_type`); the spec's worker-containment and single-writer checks (HR-6) can read attribution from there.
- The worker inherited the session's permissions: its inside-workspace Bash and Write ran without a prompt or a denial, so `allowed_tools` and `permission_mode` apply to workers as they do to the coordinator.
- Two caveats for HR-6. (1) A worker call that fails the tool's own validation never reaches the guard (the non-existent Edit target in the first run): it appears in the stream and the transcript with an error result, but not in `guard_log.json`. (2) `Read` is not a guarded tool, by design; the worker read the outside temp file before editing it and nothing logged that (the harness trace holds the call).
- `ResultMessage.permission_denials` is not a reliable record of worker denials: it listed the worker's two denials in the first run (the Agent call carried `run_in_background: false`; `requestShape: "foreground"` in the worker's meta file) and was empty in the second run, where the coordinator left the flag out and the CLI started the worker in the background (`requestShape: "background"`). The only difference seen between the two runs is that one; the guard log is the record either way.

## V-2: `total_cost_usd` includes the worker's spend. Confirmed.

- With the worker on Haiku and the coordinator on Sonnet, `ResultMessage.model_usage` of the first worker run has both keys, and their `costUSD` sum to `total_cost_usd` exactly: Sonnet 0.0504444 + Haiku 0.01766585 = 0.06811025 = `total_cost_usd`. The same identity holds in the other two worker runs (0.0521088 + 0.01368425 = 0.06579305; 0.0599348 + 0.0135798 = 0.0735146). The no-worker run has one key, Sonnet 0.0433 = `total_cost_usd`.
- With and without: $0.068, $0.066 and $0.074 with the worker against $0.043 without, on the same case. The rise is the worker's $0.014 to $0.018 plus the coordinator's extra context (the Agent tool, the hand-back).
- For HR-4: the per-model breakdown is already there (`model_usage[model].costUSD`, with input, output, cache-read and cache-creation tokens), so the harness can report `worker_cost_usd` whenever the worker runs on a model the coordinator does not use. When both run on Sonnet (AG-1 says the worker is Sonnet) the split is not in `model_usage`; it is in the worker's transcript file, whose assistant lines each carry `message.usage` (15 such lines in the second run's worker file, checked). `ResultMessage.usage` is the coordinator's usage only, never the worker's: in the first run it equals the Sonnet entry of `model_usage` token for token (6 input, 833 output, 51,572 cache read, 7,947 cache creation); in the second run it holds 531 of that entry's 978 output tokens. `model_usage` is the run's whole; `usage` is not.

## V-3: worker transcripts exist at the documented path. Confirmed.

Exact paths from the first worker run (session `63670428-7f72-43be-a6b3-312c73e9928a`, workspace `C:\Users\leerd\AppData\Local\Temp\construction-eval\_probe-fanout-20261015-234754-r1`):

```
C:\Users\leerd\.claude\projects\C--Users-leerd-AppData-Local-Temp-construction-eval--probe-fanout-20261015-234754-r1\
    63670428-7f72-43be-a6b3-312c73e9928a.jsonl                                   the session (34 lines)
    63670428-7f72-43be-a6b3-312c73e9928a\subagents\agent-a4c51b8760e4d26d2.jsonl   the worker (38 lines, 79,573 bytes)
    63670428-7f72-43be-a6b3-312c73e9928a\subagents\agent-a4c51b8760e4d26d2.meta.json   (207 bytes)
```

- The project folder is the workspace path with every character that is not a letter or digit replaced by `-` (the SDK's `_sanitize_path`): the `\` separators, the `:`, and the case folder's leading `_`, which is why the name reads `construction-eval--probe-fanout-…`. `session_id` comes from `ResultMessage.session_id` (and the `init` system message).
- The meta file: `{"agentType":"construction:probe-worker","description":"Run probe worker","toolUseId":"toolu_01Lhbh9mo2q4mqxYSJAsfMgw","spawnDepth":1,"requestShape":"foreground","requestNonInteractive":true,"model":"haiku"}`. `toolUseId` is the Agent call's id in the parent, the same id the stream's `parent_tool_use_id` carries, so a transcript file maps to its Agent call without parsing either transcript.
- The worker file's lines carry `agentId`, `isSidechain: true`, and the usual `type` (`user`, `assistant`, `attachment`) with `message.content` blocks (thinking, text, tool_use, tool_result) and `message.model` (`claude-haiku-4-5-20251001`). Every tool call the worker made is there, including the Edit that failed validation and the unguarded Read.
- A second witness: `claude_agent_sdk.list_subagents(session_id, directory=str(workspace))` returned `['a4c51b8760e4d26d2']`; `get_subagent_messages(session_id, agent_id, directory)` parses the file. The no-worker run has no `subagents` folder and `list_subagents` returns `[]`.
- One wrinkle: the `transcript_path` in a worker's hook input is the *session's* transcript (`…\63670428-….jsonl`), not the worker's file. Find the worker file through the Agent call's `toolUseId` in the meta files, or `list_subagents`, not through the hook.
- The folder outlives the workspace: the harness deletes the temp workspace after grading but nothing deletes `~/.claude/projects/<sanitized workspace>/`, so HR-5's copy into the run folder should be followed by removing that project folder (one folder per run; `ls ~/.claude/projects | grep -c construction-eval` gives 345 of them on this machine today).

## V-4: the `subagent_type` string, and `claude plugin validate --strict` with an `agents` key. Confirmed.

- The string is `construction:probe-worker`: the plugin's manifest `name`, a colon, the agent's frontmatter `name`. It is what the `init` system message lists under `agents` (`["claude", "construction:probe-worker", "Explore", "general-purpose", "Plan", "statusline-setup"]`), what the coordinator passed in its Agent call (`"subagent_type": "construction:probe-worker"` in the trace), what the hook input's `agent_type` says, and what the meta file's `agentType` says. For the spec's agent the string is `construction:pe-worker`.
- `claude plugin validate --strict .claude-plugin/plugin.json` (Claude Code 2.1.288), three manifest states with `agents/probe-worker.md` present:

| Manifest | Result |
|---|---|
| no `agents` key | passes |
| `"agents": ["./agents/probe-worker.md"]` (the spec's AG-3 form) | passes, `--json` report shows no warnings or notes |
| `"agents": "./agents/"` | fails: `agents: Invalid string: must end with ".md"` |

  `claude plugin validate --strict agents` (the folder) also passes; the command does not take a single `.md` file (it parses the argument as a JSON manifest). After the agent file and the manifest key were removed, `--strict` passes again on the unchanged 0.6.0 manifest.
- Not measured: whether an agent in `agents/` is loaded with *no* manifest key (the key-less manifest only validated; every run used the list form). The list form is what AG-3 specifies, so nothing depends on it.

## V-10: a worker's tool calls reach the SDK stream of a `-p` session with the parent id. Confirmed, by default.

What the stream carried in the first worker run (default options, `forward_subagent_text` unset), in order, after the coordinator's `AssistantMessage` with the Agent `tool_use` (id `toolu_01Lhbh9mo2q4mqxYSJAsfMgw`) and a `TaskStartedMessage`:

```
UserMessage       parent_tool_use_id=toolu_01Lhbh…  text: the worker's prompt
AssistantMessage  parent_tool_use_id=toolu_01Lhbh…  tool_use Bash   model=claude-haiku-4-5-20251001
UserMessage       parent_tool_use_id=toolu_01Lhbh…  tool_result "probe input line"
AssistantMessage  parent …                          tool_use Write (workers/01/worker-note.txt)
UserMessage       parent …                          tool_result "File created successfully…"
AssistantMessage  parent …                          tool_use Write (/tmp/probe.txt)
UserMessage       parent …                          tool_result is_error "Blocked by the eval guard: …"
AssistantMessage  parent …                          tool_use Bash (echo … $HOME/probe-outside.txt)
UserMessage       parent …                          tool_result is_error "PreToolUse:Bash hook error: Blocked by the eval guard: …"
AssistantMessage  parent …                          tool_use Edit (../probe-edit-outside.txt)
UserMessage       parent …                          tool_result is_error "<tool_use_error>File does not exist…"
TaskUpdatedMessage, TaskNotificationMessage          (no parent id)
UserMessage       parent_tool_use_id=None           tool_result for toolu_01Lhbh…: "[Subagent hand-back] …" the worker's reply
```

- By default the stream carries every worker `tool_use` and `tool_result` block as `AssistantMessage` / `UserMessage` objects whose `parent_tool_use_id` is the Agent call's id, plus the worker's prompt as a text block with the same id; `TaskProgressMessage`s in between carry no parent id. Counts: 5 tool_use and 5 tool_result blocks with a parent id in the first run, 6 and 6 in the second. The worker's own text and thinking do not arrive by default (one text block with a parent id: the prompt).
- With `ClaudeAgentOptions(forward_subagent_text=True)` (SDK 0.2.163; sent to the CLI as `forwardSubagentText` in the initialize request) the same run also forwards the worker's `ThinkingBlock` and text blocks before each call and its final text (23 messages with a parent id, 7 text blocks, against 11 and 1). Tool blocks are unchanged. The harness does not need this option for grading; it would only inflate the trace.
- The worker's final reply reaches the parent as the Agent call's `tool_result` (no parent id, since it is the coordinator's), wrapped in a `[Subagent hand-back]` preamble that says it is model output and carries no user authority.
- **Consequence for HR-2 (the mechanism):** the stream is the source. The runner already receives the blocks; it needs only to keep `parent_tool_use_id` on each trace entry (today `_block_summary` drops it). With that, `tool_used`, `regex` on the trace, `no-inline-python`, the writes-outside blocker and HR-6's checks see worker calls with attribution, and `summary.md` can count workers (distinct parent ids) and worker turns. The copied transcripts (HR-5) stay the audit and `--regrade` source, not the grading source.
- **Correction to F8:** "the trace holds a sub-agent only as its Agent tool_use entry" is not what the 0.6.0 harness does on this CLI and SDK. The harness loop handles `AssistantMessage` and `UserMessage` without looking at `parent_tool_use_id`, so the worker's calls are *already* in `trace.jsonl`, unlabelled: the second worker run's trace lists `Agent, Bash, Write, Write, Bash, Read, Edit, Write`, of which six are the worker's. Any case that grants `Agent` and whose run spawns one is graded on its workers' calls on this CLI and SDK, and a `tool_used` grader with `max:` counts them too. The two `submittal-review` cases grant `Agent`, but their saved 2026-10-12 traces in the 0.6.0 worktree hold no Agent call (17 and 30 tool uses, none of them `Agent`), so no graded run has been affected yet. HR-1's `unplanned-fan-out` blocker can be a `tool_used Agent max: 0` on every non-fan-out case today.

## What this settles in the spec

- HR-3: the guard covers workers; `Agent` need not be denied anywhere. Add `agent_id` and `agent_type` to each `guard_log.json` entry.
- HR-2: trace entries keep `parent_tool_use_id`; graders read the trace; no `forward_subagent_text`.
- HR-4: `total_cost_usd` is the whole run. Report `model_usage` per model; a per-worker figure needs the transcript's per-call usage when worker and coordinator share a model.
- HR-5: copy `~/.claude/projects/<sanitized workspace>/<session_id>/subagents/` into the run folder, keyed by the meta file's `toolUseId`, then remove the project folder.
- HR-6: containment and single-writer checks read the trace (with parent ids) and the guard log (with agent ids); a validation-failed call shows in the trace only; `Read` is never in the guard log.
- AG-4: `subagent_type: construction:pe-worker`.
- A coordinator told to spawn in the foreground may leave `run_in_background` out, and the CLI then starts the worker in the background (second run); the spec already treats workers as background (AG-4), so nothing changes, but the coordinator's word about it is not evidence.

## Not probed here

V-5 (`skills:` preload in a plugin agent), V-6 (interactive permission prompts), V-7 (`jsonschema` re-sync), V-8 (resume), V-9 (`scope_router.py` on the Sanibel index), and loading an agent from `agents/` without a manifest key.

## Rerunning

From the plugin root, under the heavy-job lock, one arm per command: `bin/construction-python "evals/plugin/_probe-fanout/probe.py" worker` (then `worker-forward`, `noworker`). Each is a 20- to 50-second Sonnet session at about $0.07. The agent file must exist for the worker arms: recreate `agents/probe-worker.md` with the frontmatter above and add `"agents": ["./agents/probe-worker.md"]` to the manifest, and remove both after. Results land in `evals/results/probe-fanout/`, which is gitignored.
