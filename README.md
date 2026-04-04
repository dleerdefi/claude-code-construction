# Construction Skills for Claude Code

Open-source skills that give Claude Code the working knowledge of a Project Engineer. Split drawings, parse specs, tabulate bids, generate subcontracts, and more — directly from your terminal or IDE.

## Prerequisites

- [Claude Code](https://claude.ai/code) (CLI, VS Code extension, or JetBrains)
- Python 3.10+
- Your construction project documents (drawings, specs, bids, etc.)

## Setup

**1. Install the skills:**

```bash
# Global install (available in all projects)
git clone https://github.com/dleerdefi/claude-code-construction ~/.claude/skills/construction

# Or per-project install
git clone https://github.com/dleerdefi/claude-code-construction .claude/skills/construction
```

**2. Run setup** (installs Python dependencies into an isolated venv):

```bash
cd ~/.claude/skills/construction    # or .claude/skills/construction
./setup
```

**3. Connect to your project.** Add this line to your project's `CLAUDE.md`:

```
@~/.claude/skills/construction/.claude/skills/CLAUDE.md
```

If your project doesn't have a `CLAUDE.md` yet, run `/init` in Claude Code first.

**4. Start using skills.** Open Claude Code in your project folder and type:

```
/project-setup
```

This inventories your project files, classifies document types, and establishes context for the other skills.

## Skills

| Command | What it does |
|---------|-------------|
| `/project-setup` | Inventory project files, classify documents, establish context |
| `/sheet-splitter` | Split a bound drawing set PDF into individual sheet PDFs |
| `/spec-splitter` | Split a bound project manual into individual spec section PDFs + text |
| `/schedule-extractor` | Extract door, finish, window, or panel schedules to Excel |
| `/submittal-log-generator` | Parse every spec section and generate a submittal register in Excel |
| `/bid-tabulator` | Tabulate multiple subcontractor bids into a comparison spreadsheet |
| `/bid-evaluator` | Evaluate tabulated bids — scope gaps, risk scoring, award recommendation |
| `/code-researcher` | Research applicable building codes, standards, and jurisdiction requirements |
| `/subcontract-writer` | Generate a scope-specific subcontract from your firm's template |

## AgentCM (Optional)

If your project uses [AgentCM](https://github.com/dleerdefi/AgentCM), skills automatically read from pre-indexed structured data in the `.construction/` directory for faster results. Skills work without AgentCM using Claude's built-in vision and PDF tools.

## Output

Skills save structured results to a `.construction/` directory in your project root. Excel files, split PDFs, and extracted text are written to your project folder. Each skill reports its output location when complete.

## Architecture & Technical Details

See [CM Skills SOP](docs/CM_SKILLS_SOP.md) for the full technical breakdown — skill architecture, design philosophy, YAML front matter spec, and the evaluation framework.

## Documentation

- [Quickstart Guide](docs/QUICKSTART.md) — try your first skill in 5 minutes
- [CM Skills SOP](docs/CM_SKILLS_SOP.md) — skill architecture and design standard
- [Troubleshooting](docs/TROUBLESHOOTING.md) — common issues and fixes
- [Evaluation Spec](evals/EVAL_SPEC.md) — test framework for validating skills
- [Running Evals](docs/RUNNING_EVALS.md) — how to run eval test cases

## Requirements

Python dependencies are installed automatically by `./setup` into an isolated venv at `~/.construction-skills/venv/`. No manual activation needed — all scripts run through `bin/construction-python`.

Packages: `pdfplumber`, `pymupdf`, `openpyxl`, `Pillow`, `PyYAML`

## License

MIT

---

Made with 👷 by [dleerdefi](https://github.com/dleerdefi)