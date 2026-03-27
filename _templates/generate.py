#!/usr/bin/env python3
"""Generate SKILL.md from SKILL.md.tmpl + partials.

Usage:
  python _templates/generate.py                    # Generate all
  python _templates/generate.py drawing-reader     # Generate one skill
  python _templates/generate.py --check            # Verify all are up-to-date
  python _templates/generate.py --list             # List skills with templates
"""

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
PARTIALS_DIR = Path(__file__).resolve().parent / "partials"


def load_partials() -> dict[str, str]:
    """Load all partial templates from _templates/partials/."""
    partials = {}
    if not PARTIALS_DIR.exists():
        return partials
    for f in PARTIALS_DIR.glob("*.md"):
        partials[f.stem] = f.read_text(encoding="utf-8")
    return partials


def render_template(tmpl_content: str, partials: dict[str, str], vars: dict[str, str] | None = None) -> str:
    """Substitute {{PARTIAL:name}} and {{VAR:name}} in template content."""
    vars = vars or {}

    # Substitute partials
    def replace_partial(match):
        name = match.group(1).strip()
        if name in partials:
            return partials[name]
        print(f"  WARNING: Partial '{name}' not found", file=sys.stderr)
        return match.group(0)

    result = re.sub(r"\{\{PARTIAL:([^}]+)\}\}", replace_partial, tmpl_content)

    # Substitute variables
    def replace_var(match):
        name = match.group(1).strip()
        if name in vars:
            return vars[name]
        # Leave unreplaced vars as-is (they may be documentation placeholders)
        return match.group(0)

    result = re.sub(r"\{\{VAR:([^}]+)\}\}", replace_var, result)

    return result


def parse_vars_from_tmpl(tmpl_path: Path) -> dict[str, str]:
    """Extract VAR definitions from a vars.yaml alongside the template, if present."""
    vars_file = tmpl_path.parent / "vars.yaml"
    if not vars_file.exists():
        return {}
    try:
        import yaml
        with open(vars_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return {str(k): str(v) for k, v in (data or {}).items()}
    except ImportError:
        # PyYAML not available, skip vars
        return {}


def find_skills_with_templates() -> list[tuple[str, Path, Path]]:
    """Find all skills that have a .tmpl file. Returns (name, tmpl_path, output_path).

    Scans both production skills (.claude/skills/) and dev skills (.claude/skills/_dev/).
    """
    results = []
    search_dirs = [SKILLS_DIR]

    # Also scan _dev/ subdirectory if it exists
    dev_dir = SKILLS_DIR / "_dev"
    if dev_dir.exists():
        search_dirs.append(dev_dir)

    for parent in search_dirs:
        for skill_dir in sorted(parent.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name.startswith("_"):
                continue
            tmpl = skill_dir / "SKILL.md.tmpl"
            output = skill_dir / "SKILL.md"
            if tmpl.exists():
                prefix = "_dev/" if parent == dev_dir else ""
                results.append((f"{prefix}{skill_dir.name}", tmpl, output))
    return results


def generate_one(name: str, tmpl_path: Path, output_path: Path, partials: dict[str, str]) -> bool:
    """Generate SKILL.md from template. Returns True if file changed."""
    tmpl_content = tmpl_path.read_text(encoding="utf-8")
    vars = parse_vars_from_tmpl(tmpl_path)
    rendered = render_template(tmpl_content, partials, vars)

    if output_path.exists():
        existing = output_path.read_text(encoding="utf-8")
        if existing == rendered:
            return False

    output_path.write_text(rendered, encoding="utf-8")
    return True


def cmd_generate(skill_filter: str | None = None):
    """Generate SKILL.md files from templates."""
    partials = load_partials()
    skills = find_skills_with_templates()

    if skill_filter:
        skills = [(n, t, o) for n, t, o in skills if n == skill_filter]
        if not skills:
            print(f"No template found for skill '{skill_filter}'")
            sys.exit(1)

    changed = 0
    for name, tmpl_path, output_path in skills:
        if generate_one(name, tmpl_path, output_path, partials):
            print(f"  Generated: {name}/SKILL.md")
            changed += 1
        else:
            print(f"  Unchanged: {name}/SKILL.md")

    print(f"\n{changed} file(s) updated, {len(skills) - changed} unchanged.")


def cmd_check():
    """Verify all generated SKILL.md files are up-to-date."""
    partials = load_partials()
    skills = find_skills_with_templates()

    if not skills:
        print("No templates found. Nothing to check.")
        sys.exit(0)

    stale = []
    for name, tmpl_path, output_path in skills:
        tmpl_content = tmpl_path.read_text(encoding="utf-8")
        vars = parse_vars_from_tmpl(tmpl_path)
        rendered = render_template(tmpl_content, partials, vars)

        if not output_path.exists():
            stale.append((name, "missing"))
        else:
            existing = output_path.read_text(encoding="utf-8")
            if existing != rendered:
                stale.append((name, "outdated"))

    if stale:
        print("FAIL: The following SKILL.md files are out of date:")
        for name, reason in stale:
            print(f"  {name}: {reason}")
        print(f"\nRun 'python _templates/generate.py' to regenerate.")
        sys.exit(1)
    else:
        print(f"OK: All {len(skills)} SKILL.md files are up-to-date.")


def cmd_list():
    """List skills that have templates."""
    skills = find_skills_with_templates()
    if not skills:
        print("No templates found.")
    else:
        print(f"Skills with templates ({len(skills)}):")
        for name, _, _ in skills:
            print(f"  {name}")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        cmd_generate()
    elif args[0] == "--check":
        cmd_check()
    elif args[0] == "--list":
        cmd_list()
    elif args[0].startswith("--"):
        print(f"Unknown flag: {args[0]}")
        print(__doc__)
        sys.exit(1)
    else:
        cmd_generate(args[0])
