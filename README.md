# Construction Skills for Claude Code

Open-source skills that give Claude Code the working knowledge of a Project Engineer. Split drawings, parse specs, tabulate bids, generate subcontracts, and more — directly from your terminal or IDE.

## Prerequisites

- [Claude Code](https://claude.ai/code) (CLI, VS Code extension, or JetBrains) on Windows, macOS or Linux
- Python 3.10+
- On Windows: [Git for Windows](https://git-scm.com/download/win), whose Git Bash runs the skills' commands
- Your construction project documents (drawings, specs, bids, etc.)

## Setup

The repo is a Claude Code plugin named `construction`. Install it one of two ways.

**Option A — clone into your skills directory** (recommended; update with `git pull`). On Windows, run these in Git Bash:

```bash
# All projects
git clone https://github.com/dleerdefi/claude-code-construction ~/.claude/skills/construction
cd ~/.claude/skills/construction && ./setup

# Or one project: run from your project folder
git clone https://github.com/dleerdefi/claude-code-construction .claude/skills/construction
.claude/skills/construction/setup
```

Claude Code loads the clone as the `construction` plugin in new sessions. `./setup` creates the Python environment and removes skill links left by older versions.

**Option B — install from the marketplace** inside Claude Code:

```
/plugin marketplace add dleerdefi/claude-code-construction
/plugin install construction@construction-skills
```

The Python environment is created automatically the first time a skill runs a script (about a minute).

**Then start using skills.** Open Claude Code in your project folder and run:

```
/construction:project-setup
```

This inventories your project files, classifies document types, and adds construction context to your project's `CLAUDE.md` (run `/init` first if you don't have one).

> **Upgrading from an earlier version?** Pull the update and re-run `./setup` once to clean up the old per-skill links. Remove the `@~/.claude/skills/construction/.claude/skills/CLAUDE.md` line from your project's `CLAUDE.md`: that guide now ships as the `construction-guide` skill.

## Skills

| Command | What it does |
|---------|-------------|
| `/construction:project-setup` | Inventory project files, classify documents, establish context |
| `/construction:sheet-splitter` | Split a bound drawing set PDF into individual sheet PDFs |
| `/construction:spec-splitter` | Split a bound project manual into individual spec section PDFs + text |
| `/construction:schedule-extractor` | Extract door, finish, window, or panel schedules to Excel |
| `/construction:submittal-log-generator` | Parse every spec section and generate a submittal register in Excel |
| `/construction:bid-tabulator` | Tabulate multiple subcontractor bids into a comparison spreadsheet |
| `/construction:bid-evaluator` | Evaluate tabulated bids — scope gaps, risk scoring, award recommendation |
| `/construction:code-researcher` | Research applicable building codes, standards, and jurisdiction requirements |
| `/construction:subcontract-writer` | Generate a scope-specific subcontract from your firm's template |
| `/construction:construction-guide` | Operating guide Claude loads before working with your documents (data-access rules, conventions, document precedence) |

Type `/construction:` in Claude Code to list every skill. Claude also runs them on its own when your request matches.

## AgentCM (Optional)

If your project uses [AgentCM](https://github.com/dleerdefi/AgentCM), skills automatically read from pre-indexed structured data in the `.construction/` directory for faster results. Skills work without AgentCM using Claude's built-in vision and PDF tools.

## Output

Deliverables — Excel workbooks, Word documents, split sheet and spec PDFs, reports — are saved in your project folder where you can open them, and each skill tells you where. Skills keep their working data (extraction progress, extracted spec text, the issue registry) in a hidden `.construction/skills/` folder that you don't need to open. In AgentCM projects, skills also record their findings in AgentCM's `.construction/` data.

## Architecture & Technical Details

See [CM Skills SOP](docs/CM_SKILLS_SOP.md) for the full technical breakdown — skill architecture, design philosophy, YAML front matter spec, and the evaluation framework.

## Documentation

- [Quickstart Guide](docs/QUICKSTART.md) — try your first skill in 5 minutes
- [CM Skills SOP](docs/CM_SKILLS_SOP.md) — skill architecture and design standard
- [Troubleshooting](docs/TROUBLESHOOTING.md) — common issues and fixes
- [Evaluation Spec](evals/EVAL_SPEC.md) — test framework for validating skills
- [Running Evals](docs/RUNNING_EVALS.md) — how to run eval test cases

## Requirements

Python dependencies are installed into an isolated venv at `~/.construction-skills/venv/`, by `./setup` or automatically on first use, and re-synced whenever `requirements.txt` changes. No manual activation needed — all scripts run through `bin/construction-python`.

Packages: `pdfplumber`, `pymupdf`, `openpyxl`, `Pillow`, `PyYAML`, `python-docx`, `fpdf2`

## License

MIT

---

Made with 👷 by [dleerdefi](https://github.com/dleerdefi)