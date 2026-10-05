# Eval Harness

Runs the plugin's eval cases through a headless Claude Code session and grades what they produce. It works on Windows, macOS and Linux, and reads the same case folders as `claude plugin eval`, so a case is written once.

## Run it

From the plugin root:

```bash
bin/construction-python evals/harness/run.py --tag smoke --runs 1
```

| Option | Default | What it does |
|---|---|---|
| `--tag T` | | Run cases carrying this tag (repeatable) |
| `--case GLOB` | | Run cases whose folder name matches (repeatable) |
| `--runs N` | the case's `runs` | Runs per case; the case score is the mean |
| `--model M` | `sonnet` | Model for the agent under test |
| `--judge-model M` | `haiku` | Model for `llm` graders |
| `--judge-votes N` | 1 | Votes per `llm` grader; 3 matches plugin eval |
| `--budget-usd X` | 3.0 | Hard spend cap per run; a case can raise it with `budget_usd` in its `harness.yaml` |
| `--threshold X` | 1.0 | A case passes at or above this score |
| `--sandbox auto` | off | Turn the OS sandbox on where one exists (macOS, Linux) |
| `--keep` | | Keep every workspace (failed runs are always kept) |
| `--eval-dir DIR` | `evals/plugin` | Folder of case folders |
| `--output-dir DIR` | `evals/results/<timestamp>` | Where results are written |
| `--dry-run` | | List the selected cases and graders, run nothing |

Results go to `evals/results/<timestamp>/`: `summary.md`, `summary.json`, and per run `trace.jsonl`, `guard_log.json`, `graders.json`, `run.json`. Exit code 0 when every case meets the threshold, 1 otherwise, 2 on a harness error.

Each run is a real agent session and costs real money: between $0.15 and $6 per case on Sonnet (the eval suite README lists measured costs).

## Requirements

- The toolkit's Python environment (`bin/construction-python` builds it; the harness needs `claude-agent-sdk` from `requirements.txt`).
- Claude Code, signed in. **On Windows, the native install** (`irm https://claude.ai/install.ps1 | iex`, which puts `claude.exe` in `~/.local/bin`): the SDK refuses to drive npm's `claude.cmd` shim because `cmd.exe` cannot escape arguments safely. The npm install can stay for interactive use.
- Git Bash on Windows (the skills need it too).

## How a run works

1. A fresh workspace under the system temp dir; the case's `setup.sh` runs in it with `CONSTRUCTION_EVAL_HARNESS=1`.
2. A headless session with only this plugin loaded (none of your own settings, plugins, hooks or MCP servers), the case's `allowed_tools` pre-approved, `WebFetch`, `WebSearch` and `PowerShell` disallowed (so Windows runs behave like macOS and Linux), `max_turns` and `timeout_seconds` from the case, and the spend cap.
3. The prompt is the case's `prompt.md` body, usually `/construction:<skill>`.
4. Every Bash, Write and Edit call passes through the guard (below).
5. Graders run over the workspace and the trace.

## The guard

Native Windows has no OS sandbox, so the harness confines runs by policy instead (`guard.py`, a PreToolUse hook). It denies:

- writes outside the workspace;
- shell commands that name paths outside the workspace, the plugin, the toolkit's venv, the system temp dir, or system directories;
- network, download and install commands (`curl`, `wget`, `ssh`, `psql`, `pip install`, `npm install`, `git push`, `Invoke-WebRequest`, and so on);
- recursive deletes above the workspace.

Denied calls are logged in `guard_log.json` and reported in `summary.md`. This is policy confinement, not an OS sandbox: a determined agent could still find a way around it, so run the harness only on the plugin you trust. On macOS and Linux, `--sandbox auto` adds the OS sandbox on top.

`guard.py` is a pure function; its tests run with `bin/construction-python -m unittest discover -s evals/harness/tests`.

## Graders

The harness implements the grader types the smoke cases use, with the same frontmatter fields as plugin eval:

| Type | Passes when |
|---|---|
| `file_exists` | A file created during the run matches `path` (a glob relative to the workspace); `exists: false` inverts |
| `regex` | `pattern` is found in the target (`trace`, or `{source: file, path}`); `match: not_contains` or `count:N` |
| `tool_used` | Between `min` (default 1) and `max` calls to `tool` whose JSON input matches `input_match` |
| `tool_order` | The first `before` call precedes the first `after` call |
| `llm` | The judge model votes PASS on the grader body as rubric, over the transcript or the named text file |

Plus one harness-only type, kept outside the files plugin eval reads so the cases stay valid there:

| Type | Where | Passes when |
|---|---|---|
| `python` | `harness.yaml` in the case folder: `checks: [{name, script: checks/x.py, weight}]` | The script exits 0 (it may print `score: 0.0-1.0` for partial credit). It runs with `construction-python` in the workspace, with `EVAL_WORKSPACE`, `EVAL_CASE_DIR` and `EVAL_TRACE` in the environment, and can open xlsx and docx deliverables with the toolkit's libraries |

A run's score is the weighted fraction of passing graders. The judge refuses binary files, as plugin eval's does; grade those with a `python` check.
