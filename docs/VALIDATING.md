# Validating Your Install

Run these checks after installing or updating the plugin, on Windows (in Git Bash), macOS or Linux. Steps 1–3 take a minute. Step 4 runs real skills on real documents.

Below, `PLUGIN` is where the plugin lives:
- a clone: `~/.claude/skills/construction` (or your project's `.claude/skills/construction`)
- a marketplace install: the path `claude plugin list` shows for `construction@construction-skills`

## 1. Claude Code sees the plugin

```bash
claude plugin list
```

You should see `construction@skills-dir` (clone) or `construction@construction-skills` (marketplace), enabled. Inside Claude Code, typing `/construction:` should list 14 skills.

## 2. The plugin is well formed

```bash
claude plugin validate "$PLUGIN/.claude-plugin/plugin.json"
```

Expect `Validation passed`.

## 3. The Python environment works

```bash
"$PLUGIN/bin/construction-python" -c "import fitz, pdfplumber, openpyxl, PIL, yaml, docx, fpdf; print('Python environment OK')"
```

The first run creates `~/.construction-skills/venv` and installs the dependencies (about a minute). Expect `Python environment OK`. If it fails, see [Troubleshooting](TROUBLESHOOTING.md).

## 4. Skills work on real documents

Use a copy of a real project (or the sample project below) with a bound drawing set and a bound project manual, ideally in a folder whose name has spaces and `&` (e.g. `01 - Drawings/Architectural & Structural/`): that exercises path handling on every OS. Open Claude Code in the project folder and run:

| Run | Expect |
|---|---|
| `/construction:project-setup` | A summary of your documents; a "Construction Project Context" section appended to `CLAUDE.md` |
| `/construction:sheet-splitter` | One PDF per sheet in a `sheets/` folder next to the drawing set, named like `A-1.1 - FLOOR PLAN.pdf`, each about the size of one sheet (not the whole set); `sheets/sheet_index.yaml` |
| `/construction:spec-splitter` | One PDF per spec section in a visible folder (e.g. `Specification Sections/`); extracted text in `.construction/skills/spec_text/` |
| `/construction:submittal-log-generator` | Runs spec-splitter itself if needed, then `Submittal_Log.xlsx` in your Submittals folder or the project root |
| `/construction:rfi-drafter` then "review issues" | A list of open issues (possibly empty) — no errors |

Then check where things landed:
- Deliverables (PDFs, Excel, Word, reports) are in your project folders, where you can open them.
- `.construction/` (hidden on macOS/Linux) contains only `skills/` — unless the project uses AgentCM.

### Sample project

The sample project is the Sanibel Fire and Rescue Station 172 plans and specifications, placed in `evals/test_docs/SANIBEL FIRE AND RESCUE STATION 172/`. Its PDFs are large, so they are downloaded separately: see [Running Evals](RUNNING_EVALS.md#get-test-documents) for the links and where to put them.

## 5. Automated eval (Windows, macOS and Linux)

Steps 1–4 can be run for you, graded, on a small built-in sample project:

```bash
cd "$PLUGIN"
bin/construction-python evals/harness/run.py --tag smoke --runs 1
```

Every case should score 1.00. On Windows this needs the native Claude Code install (`irm https://claude.ai/install.ps1 | iex`); see [the harness README](../evals/harness/README.md). On macOS and Linux you can run the same cases with Claude Code's own sandbox instead: `claude plugin eval . --tag smoke --scaffold --allow-tools Bash Write Edit --runs 1 --ablation none` (see [the eval suite README](../evals/plugin/README.md)).

## Report results

If a check fails, [open an issue](https://github.com/dleerdefi/claude-code-construction/issues) with your OS, Claude model, the step, and the output.
