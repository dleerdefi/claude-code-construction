# Construction Skills — Development

This repo is a Claude Code plugin (`construction`) of skills for construction document management.

## For Users

Clone into a Claude Code skills directory and run setup:
```bash
git clone https://github.com/dleerdefi/claude-code-construction ~/.claude/skills/construction
cd ~/.claude/skills/construction && ./setup
```

Or install from the marketplace inside Claude Code:
```
/plugin marketplace add dleerdefi/claude-code-construction
/plugin install construction@construction-skills
```

Skills are invoked as `/construction:<skill>`. See README.md.

## For Contributors

- The plugin manifest is `.claude-plugin/plugin.json`; `.claude-plugin/marketplace.json` lists the plugin for `/plugin marketplace add`
- Production skills live in `skills/<name>/SKILL.md` — edit directly
- `skills/construction-guide/` is the operating guide (data-access rules, drawing conventions, document precedence). It replaced the shared CLAUDE.md, which a plugin can't ship
- Dev/experimental skills live in `.claude/skills/_dev/<name>/` (gitignored, not shipped, never loaded by the plugin)
- Deprecated skills move to `.claude/skills/_deprecated_<name>/` (gitignored; outside `skills/`, so the plugin doesn't load them)
- This contributor guide lives at `.claude/CLAUDE.md`: a CLAUDE.md at the plugin root is not loaded by plugins and fails `claude plugin validate --strict`

### Dev Workflow
```bash
claude --plugin-dir .    # Load this checkout live (any OS); run /reload-plugins after edits
dev/link                 # Or symlink ~/.claude/skills/construction here (macOS/Linux)
dev/unlink               # Remove that symlink
claude plugin validate --strict .claude-plugin/plugin.json   # Check manifest + skills
```

### Key Rules
- Each commit = one logical change
- SKILL.md files are the canonical source — edit directly
- Shared tooling is referenced from the plugin root: `${CLAUDE_PLUGIN_ROOT}/reference/`, `${CLAUDE_PLUGIN_ROOT}/scripts/`, `${CLAUDE_PLUGIN_ROOT}/bin/construction-python`. Skill-local files use `${CLAUDE_SKILL_DIR}/scripts/` and `${CLAUDE_SKILL_DIR}/references/`. Claude Code substitutes both in SKILL.md bodies only, not in supporting files
- Skills run on Windows, macOS and Linux: double-quote every path in skill commands (`"${CLAUDE_PLUGIN_ROOT}/..."`) and run Python via `bin/construction-python`, never bare `python`; write intermediate files inside the project, never `/tmp`; don't commit symlinks (Git on Windows checks them out as plain text files)
- `requirements.txt` is the single list of Python dependencies: `bin/construction-python` creates the venv on first use and re-syncs it whenever this file changes
- Bump `version` in `.claude-plugin/plugin.json` and `VERSION` for each release; marketplace installs only update when it changes
- Where skills write: deliverables in visible project folders, never in `.construction/` (hidden on macOS/Linux); working data in `.construction/skills/`; AgentCM's areas (`agent_findings/` graph entries, database, API) only when AgentCM is present, detected by `.construction/project.yaml` — never by the `.construction/` folder alone
- Never fabricate dimensions, spec requirements, or code citations
- Skills must pass eval before moving from `_dev/` to production

### Codex Compatibility
- Every skill directory includes `agents/openai.yaml` for OpenAI Codex agent compatibility
- When creating a new skill, copy an existing `agents/openai.yaml` and update the name/description

### Script Allowlist
- Skills must declare an exhaustive list of allowed scripts in their SKILL.md
- Skills must NOT create custom Python scripts during execution
- All scripts live in the shared `scripts/` directory or per-skill `scripts/` subdirectories

### Authoritative SOP
- The comprehensive skill architecture SOP is at `docs/CM_SKILLS_SOP.md`
- Covers: three-tier progressive disclosure, YAML front matter spec, 500-line limit, refactoring lifecycle, evals framework, skill categories (Builder, Extraction, Generation, Research)
