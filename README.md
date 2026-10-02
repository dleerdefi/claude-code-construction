# Construction Skills for Claude Code

Open-source skills that give Claude Code the working knowledge of a Project Engineer. Split drawings, parse specs, tabulate bids, generate subcontracts, and more — directly from your terminal or IDE.

The skills ship as a Claude Code plugin named `construction` and work on Windows, macOS and Linux.

## Prerequisites

| | Windows | macOS | Linux |
|---|---|---|---|
| [Claude Code](https://claude.ai/code) (CLI, VS Code or JetBrains) | ✓ | ✓ | ✓ |
| Shell for the skills' commands | [Git for Windows](https://git-scm.com/download/win) (Git Bash) | built in | built in |
| Python 3.10 or newer | [python.org](https://www.python.org/downloads/) installer (the `py` launcher is fine) | [python.org](https://www.python.org/downloads/) or Homebrew — Apple's built-in `python3` is 3.9, too old | your distribution's `python3` (3.10+) with `venv` |
| `git` | included in Git for Windows | `xcode-select --install` or Homebrew | your package manager |

You also need your construction project documents (drawings, specs, bids, etc.).

## Setup

Install the plugin one of two ways. Both work the same on every OS; on Windows, run the commands in **Git Bash**.

### Option A — clone into your skills directory (recommended)

```bash
# Available in every project
git clone https://github.com/dleerdefi/claude-code-construction ~/.claude/skills/construction
cd ~/.claude/skills/construction && ./setup

# Or for one project only: run from your project folder
git clone https://github.com/dleerdefi/claude-code-construction .claude/skills/construction
.claude/skills/construction/setup
```

Claude Code loads the clone as the `construction` plugin in new sessions (or run `/reload-plugins` in an open one). `./setup` creates the Python environment and removes skill links left by older versions. Update later with `git pull` in the clone.

### Option B — install from the marketplace

Inside Claude Code:

```
/plugin marketplace add dleerdefi/claude-code-construction
/plugin install construction@construction-skills
```

No separate marketplace is needed: this repository is the marketplace. The Python environment is created automatically the first time a skill runs a script (about a minute). Updates arrive when a new version is released; turn on auto-update under `/plugin` → Marketplaces.

### Start using skills

Open Claude Code in your project folder and run:

```
/construction:project-setup
```

This inventories your project files, classifies document types, and adds construction context to your project's `CLAUDE.md` (run `/init` first if you don't have one).

> **Upgrading from an earlier version?** Pull the update and re-run `./setup` once to clean up the old per-skill links. Remove the `@~/.claude/skills/construction/.claude/skills/CLAUDE.md` line from your project's `CLAUDE.md`: that guide now ships as the `construction-guide` skill.

To check that everything works on your machine, follow [Validating your install](docs/VALIDATING.md).

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
| `/construction:rfi-drafter` | Draft RFIs and review the issues other skills have flagged |
| `/construction:pe-review` | Review drawings, specs, submittals or RFIs with Project Engineer judgment |
| `/construction:tag-audit-and-takeoff` | Count tagged elements across sheets and audit tag completeness |
| `/construction:viewport-highlighter` | Find and highlight the views on drawing sheets (requires AgentCM) |
| `/construction:construction-guide` | Operating guide Claude loads before working with your documents (data-access rules, conventions, document precedence) |

Type `/construction:` in Claude Code to list every skill. Claude also runs them on its own when your request matches.

## Tested with

Tested in Claude Code with **Claude Opus 5.5** and **Claude Sonnet 5.5** on Windows and macOS.

| Skill | Status |
|---|---|
| project-setup | ✅ Validated |
| spec-splitter | ✅ Validated |
| sheet-splitter | ✅ Validated |
| submittal-log-generator | 🔄 Testing in progress |
| All other skills | 🔄 Testing in progress |

Found a problem? [Open an issue](https://github.com/dleerdefi/claude-code-construction/issues) with your OS, model, and the skill's output.

## AgentCM (Optional)

If your project uses [AgentCM](https://github.com/dleerdefi/AgentCM), skills automatically read from its pre-indexed structured data in `.construction/` for faster results. Skills work without AgentCM using Claude's built-in vision and PDF tools.

## Output

Deliverables — Excel workbooks, Word documents, split sheet and spec PDFs, reports — are saved in your project folder where you can open them, and each skill tells you where. Skills keep their working data (extraction progress, extracted spec text, the issue registry) in a hidden `.construction/skills/` folder that you don't need to open. In AgentCM projects, skills also record their findings in AgentCM's `.construction/` data.

## Documentation

- [Quickstart Guide](docs/QUICKSTART.md) — try your first skill in 5 minutes
- [Validating your install](docs/VALIDATING.md) — check the plugin works on your machine
- [Troubleshooting](docs/TROUBLESHOOTING.md) — common issues and fixes
- [CM Skills SOP](docs/CM_SKILLS_SOP.md) — skill architecture and design standard
- [Running Evals](docs/RUNNING_EVALS.md) and the [plugin eval suite](evals/plugin/README.md) — the scored evals for contributors

## Requirements

Python dependencies are installed into an isolated venv at `~/.construction-skills/venv/`, by `./setup` or automatically on first use, and re-synced whenever `requirements.txt` changes. No manual activation needed — all scripts run through `bin/construction-python`.

Packages: `pdfplumber`, `pymupdf`, `openpyxl`, `Pillow`, `PyYAML`, `python-docx`, `fpdf2`

## License

MIT

---

Made with 👷 by [dleerdefi](https://github.com/dleerdefi)
