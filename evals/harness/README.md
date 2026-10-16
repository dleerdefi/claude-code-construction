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
| `--regrade DIR` | | Re-grade the runs saved in results folder `DIR` with the current graders, run nothing (see below) |
| `--rejudge` | | With `--regrade`: ask the judge again for `llm` graders instead of keeping their stored verdicts |

Results go to `evals/results/<timestamp>/`: `summary.md`, `summary.json`, and per run `trace.jsonl`, `guard_log.json`, `graders.json`, `run.json` and `workspace/`, a copy of every file the run created or modified (the deliverables and the skill's working data, not the fixture inputs), taken before the temp workspace is deleted. Exit code 0 when every case meets the threshold, 1 otherwise, 2 on a harness error.

Each run is a real agent session and costs real money: between $0.15 and $6 per case on Sonnet (the eval suite README lists measured costs).

**Re-grading without re-running.** A run folder holds everything a grader reads, so a changed or new grader can be checked against saved runs for free: `bin/construction-python evals/harness/run.py --regrade evals/results/<stamp> [--case GLOB]` writes a new `evals/results/<stamp>-regrade/` folder. Trace graders (`tool_used`, `tool_order`, `regex` on the trace) are re-evaluated from the trace. Graders that read files (`file_exists`, `regex`/`llm` on a file, python checks) are re-evaluated against the live workspace when it still exists (failed runs keep theirs, `--keep` keeps all) and otherwise against the run folder's `workspace/` snapshot, marked "on the snapshot"; only runs saved before the snapshot existed keep their stored verdict, marked "kept from the original grading". A python check that reads a fixture input rather than a file the run wrote will not find it on the snapshot. `llm` graders keep theirs unless `--rejudge`; a new `llm` grader with no stored verdict is judged. Write a new grader, regrade the last results folder, and only then spend on a run. (The `reads-specs` grader for bid-evaluator was first written against the wrong text and failed three runs that had read the sections; a regrade would have shown that before the $1 round.)

**Negative examples.** A case may keep known-wrong material beside an `llm` grader in `negatives/*.md` (frontmatter `grader: <name>`, `expect: FAIL`, an optional `note:`; the body is the material). `bin/construction-python evals/harness/run.py --check-negatives [--case GLOB] [--judge-votes 3]` judges each with its grader's rubric and exits 1 when a verdict differs, so a rubric edit that lets a wrong answer pass shows before a run is spent (construction-guide keeps an answer that grades single-source values CONFIRMED).

**Skipped cases.** A case whose `setup.sh` exits 3 (its inputs are missing: the Sanibel downloads, or a fixture that lacks what the case needs) is reported as skipped and, by default, does not fail the run, so contributors without the downloads still get a result; the last line and `summary.md` give the skipped count. With `--no-skip` any skipped case fails the run. A gate that counts on every case running (0.6.0's: `--tag agentcm-mode --no-skip`) uses it.

## Requirements

- The toolkit's Python environment (`bin/construction-python` builds it; the harness needs `claude-agent-sdk` from `requirements.txt`).
- Claude Code, signed in. **On Windows, the native install** (`irm https://claude.ai/install.ps1 | iex`, which puts `claude.exe` in `~/.local/bin`): the SDK refuses to drive npm's `claude.cmd` shim because `cmd.exe` cannot escape arguments safely. The npm install can stay for interactive use.
- Git Bash on Windows (the skills need it too).
- For the agentcm-mode cases, Poppler (`pdfinfo`, `pdftoppm`): AgentCM's real `crop.sh` and `crop.ps1` render the fixture's PDFs with it. Point `AGENTCM_POPPLER_BIN` at Poppler's bin folder on the harness run (`AGENTCM_POPPLER_BIN="C:\path\to\poppler\Library\bin" bin/construction-python evals/harness/run.py --tag agentcm-mode ...`). The harness passes it into every agentcm-mode case's setup, session and teardown, with that folder first on PATH: Git Bash and MiKTeX ship Xpdf tools under the same names. The path is never written into the fixture or the repository. Unset, the crop scripts take `pdfinfo` and `pdftoppm` from PATH. Before any agentcm-mode case starts, a preflight (`poppler.py`) runs the fixture's `crop.sh` (and `crop.ps1` on Windows) on a known box and checks that a PNG comes back and that the `pdfinfo` found is Poppler's. Otherwise the run stops with a setup error (exit 2) naming what is missing, and no case runs.

## How a run works

1. A fresh workspace under the system temp dir; the case's `setup.sh` runs in it with `CONSTRUCTION_EVAL_HARNESS=1`.
2. A headless session with only this plugin loaded (none of your own settings, plugins, hooks or MCP servers). An agentcm-mode case also loads the workspace's project settings (`setting_sources=["project"]`), so the project's `CLAUDE.md` is read at the start, as in a real session, and AgentCM's `.construction/CLAUDE.md` through the import in AgentCM's block. Claude Code also walks up from the project, and the workspace is under your home folder, so it would read your own `~/.claude/CLAUDE.md` as the project's. Every folder above the workspace is therefore excluded (`claudeMdExcludes`, built at run time, never written to a file): its `CLAUDE.md`, `CLAUDE.local.md`, `.claude/CLAUDE.md` and `.claude/rules/`. That exclusion is why an agentcm-mode run sees only the project's two instruction files, `CLAUDE.md` and `.construction/CLAUDE.md`. A probe (2026-10-15) found exactly those two with the exclusion, and the user's own `CLAUDE.md` as well without it. Keep the exclusion (David). `run.json` records the setting and how many globs were excluded. Every other case loads no settings. The session also gets the case's `allowed_tools` pre-approved, `WebFetch`, `WebSearch` and `PowerShell` disallowed (so Windows runs behave like macOS and Linux), `max_turns` and `timeout_seconds` from the case, and the spend cap.
3. The prompt is the case's `prompt.md` body, usually `/construction:<skill>`.
4. Every Bash, Write and Edit call passes through the guard (below).
5. The case's `teardown` script, if its `harness.yaml` names one, runs in the workspace (to stop a server its `setup.sh` started); its output goes in the trace and a failure never fails the run.
6. Graders run over the workspace and the trace.

## The guard

Native Windows has no OS sandbox, so the harness confines runs by policy instead (`guard.py`, a PreToolUse hook). It denies:

- writes outside the workspace;
- shell commands that name paths outside the workspace, the plugin, the toolkit's venv, the system temp dir, or system directories;
- network, download and install commands (`curl`, `wget`, `ssh`, `psql`, `pip install`, `npm install`, `git push`, `Invoke-WebRequest`, and so on);
- recursive deletes above the workspace.

A case may let `curl`, and only `curl`, reach listed addresses: `allow_urls` in its `harness.yaml` (`allow_urls: ["http://127.0.0.1:47817/"]` for the agentcm-mode cases' stand-in for AgentCM's API). Every address in the command must start with one of them, and options that would send the request elsewhere (`-x`/`--proxy`, `-K`/`--config`, `--connect-to`, `--resolve`, `--next`) are still denied. Addresses are not read as paths.

Denied calls are logged in `guard_log.json` and reported in `summary.md`. This is policy confinement, not an OS sandbox: a determined agent could still find a way around it, so run the harness only on the plugin you trust. On macOS and Linux, `--sandbox auto` adds the OS sandbox on top.

`guard.py` is a pure function; its tests run with `bin/construction-python -m unittest discover -s evals/harness/tests`.

## Graders

The harness implements the grader types the smoke cases use, with the same frontmatter fields as plugin eval:

| Type | Passes when |
|---|---|
| `file_exists` | A file created during the run matches `path` (a glob relative to the workspace); `exists: false` inverts |
| `regex` | `pattern` is found in the target (`trace`; `tool_inputs`, every tool call's JSON-encoded input in full, for "did it read X" over a long run; or `{source: file, path}`); `match: not_contains` or `count:N` |
| `tool_used` | Between `min` (default 1) and `max` calls to `tool` whose JSON input matches `input_match` |
| `tool_order` | The first `before` call precedes the first `after` call |
| `llm` | The judge model votes PASS on the grader body as rubric, over the transcript or the named text file |

Plus one harness-only type, kept outside the files plugin eval reads so the cases stay valid there:

| Type | Where | Passes when |
|---|---|---|
| `python` | `harness.yaml` in the case folder: `checks: [{name, script: checks/x.py, weight}]` | The script exits 0 (it may print `score: 0.0-1.0` for partial credit). It runs with `construction-python` in the workspace, with `EVAL_WORKSPACE`, `EVAL_CASE_DIR` and `EVAL_TRACE` in the environment, and can open xlsx and docx deliverables with the toolkit's libraries |

A run's score is the weighted fraction of passing graders. The judge refuses binary files, as plugin eval's does; grade those with a `python` check.

- **Report-only graders.** A grader with `weight: 0` is evaluated and listed but never scored. `summary.md` marks a failed one `REPORT`, not `FAIL`. The regular (no-AgentCM) cases carry `no-inline-python` and `no-helper-scripts` this way, except the three bid cases, where they have scored since 0.5.x. Their failures are the baseline for the mode refactor.
- **Blockers.** Every run, in every case, is also graded on three blockers, and one check that is reported for now (`no-database-query`). A run that trips a blocker scores 0, whatever its graders say; `summary.md` marks it `BLOCKER`.
  - `writes-inside-project` fails when a run leaves anything outside its project folder. The guard lets commands use the temp dir and the plugin, so it doesn't stop a page image sent to `/tmp`, and a write made inside Python code never shows as a shell redirect. So the check reads the disk (`leftovers.py`):
    - Each run gets a temp folder of its own next to its workspace, and TMP, TEMP and TMPDIR point at it.
    - Before and after the session, the runner lists the **hard places**, where nothing but the run writes: every file in the run's temp folder, `C:\tmp` on Windows, and the project folder's parent.
    - It also lists the top of the **shared places**: the system temp folder (on Windows, Git Bash's `/tmp` is this folder whatever TEMP says), `/tmp` elsewhere, and the home folder.
    - The user's **Desktop, Documents and Downloads** (where the shell keeps them, OneDrive included) are walked whole after the session. Any file created or changed since the session started is a hit, so a file saved inside a folder that already exists is caught. On Windows the listing carries both times; about half a million files take some 8 seconds. Paths in the machine's noise list (below) are left out. A file moved in from the same volume keeps its old times and is not seen.
    - A new entry, or a file whose size or time changed, is a hit. In shared places only, names in the machine's noise list are left out. That list is this machine's file names, so it lives on the machine, never in the repository: `~/.construction-skills/eval-noise.jsonl`, one `{place, pattern, reason}` per line. Only names an idle baseline showed changing go there, each with its baseline; `probe_leftovers.py --idle` prints what changed. With no file, nothing is left out.
    - **Which hits block** (David): any hit in a hard place is a blocker. A hit in a shared place is a blocker only when the run's commands or output name the file or the folder it is in, by full path, `/tmp/<name>`, `Documents/<path>`, or a file name. The place itself doesn't count as the folder: every run names the temp folder, since its workspace is inside it. Any other shared-place hit goes on `outside-review` (`REVIEW` in `summary.md`), unscored. Before the merge, every reviewed item is looked at by name, in the run records (`evals/results/`, gitignored, so names stay on the machine). PR #28 gets only counts and a verdict per category ("12 tmpXXXX folders: other sessions' tests, not the run"), never a path or file name from the machine.
    - The report names each file, its place, and whether the run's commands or output name it.
    - If another harness run was active at the same time, the report names it too: `~/.construction-skills/eval-runs.jsonl` records every run's start and end.
    - The command scan stays as the second signal for how a write happened (`guard.outside_writes`: redirects, `-o`/`--output`/`--output-dir`, `mkdir`, `touch`, `rm`, `tee`, `cp`/`mv` destinations and `sed -i`, following the command's own `cd` and variables, skipping heredoc bodies, quoted text and refused calls). A command that wrote outside fails the run even if its file is gone.
    - `probe_leftovers.py` checks the check on a machine without an agent. Python writes planted in `/tmp`, `C:\tmp`, the run's temp folder and a folder that already exists in Documents must be caught. The probe makes that folder itself, `Documents/construction-eval-probe/nested/`, and removes it; it never writes into the user's own folders, and an idle interval must come back clean. It removes what it planted.
  - `originals-intact` fails when a file that was in the workspace before the run, outside `.construction/`, is changed or deleted. The project's `CLAUDE.md` is exempt only in the `project-setup` case, where writing it is the skill's job; any other skill changing it counts. Runs saved before 2026-10-13 did not record deleted files, and their result says so.
  - `agentcm-block-intact` fails when AgentCM's block in the project's `CLAUDE.md` (from `<!-- AgentCM: start` to `<!-- AgentCM: end -->`, as AgentCM's `projectPointer.ts` writes it) does not come out of the run byte for byte, in every case, project-setup's included. The runner records the block's sha256 before and after; text outside the block is free.
  - `no-database-query` flags a run whose shell commands call AgentCM's database (David): `query.sh`, `query.ps1` or `psql`. For 0.6.0 it is reported (`REPORT` in `summary.md`) and not scored, since AgentCM's guide still offers the database. Every such run is listed for David with its case and the guide line it followed, if any. It becomes a blocker (`DATABASE_QUERY_BLOCKS` in `graders.py`) once AgentCM's guide says a running construction skill reads the files, not the database. That covers a call in command position, behind `sh`, `bash`, `source`, `env`, `timeout` or `powershell -File`, inside a `bash -c` or `powershell -Command` string, and inside `$(...)`. A call the guard refused still counts. Reading the script, listing it or searching for its name is not a call. The skills read AgentCM's files only. AgentCM's guide offers the database for counts and joins, so a run that queries it because the guide says so is reported to David: the fix belongs in AgentCM's guide, not the skill.
- **Runs passed.** `summary.md` counts the runs that met the threshold per case (the "passes in at least 2 of 3 runs" bar).
