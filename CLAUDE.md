# Construction Skills — Development

This repo contains Claude Code skills for construction document management.

## For Users

Import into your project's `CLAUDE.md`:
```
@.claude/skills/construction/CLAUDE.md
```

Or install globally:
```bash
./setup --global
```

## For Contributors

- Production skills live in `.claude/skills/<name>/SKILL.md` — edit directly
- Dev/experimental skills live in `.claude/skills/_dev/<name>/` (gitignored, not shipped)
- Deprecated skills are renamed with `_deprecated_` prefix (prevents skill matching, keeps content accessible)

### Dev Workflow
```bash
bin/dev-setup       # Symlink to ~/.claude/skills/construction for live testing
bin/dev-teardown    # Remove symlink
```

### Key Rules
- Each commit = one logical change
- SKILL.md files are the canonical source — edit directly
- `reference/` data is shared across skills — accessed via `${CLAUDE_SKILL_DIR}/../../reference/`
- `scripts/` Python tools are shared — accessed via `${CLAUDE_SKILL_DIR}/../../scripts/`
- All skills write findings to `.construction/agent_findings/` via graph entry pattern
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
