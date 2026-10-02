"""Load eval cases from the plugin eval directory.

A case is a folder with `prompt.md` (YAML frontmatter + the prompt), an optional
`case.yaml` (`context.scaffold_script`, `context.add_dirs`), `graders/*.md` (YAML
frontmatter + rubric body) and, for this harness only, an optional `harness.yaml`
listing Python checks. The format is the one `claude plugin eval` reads, so the
same case runs under both.
"""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Grader:
    name: str
    type: str
    fields: dict
    body: str

    @property
    def weight(self) -> float:
        return float(self.fields.get("weight", 1))


@dataclass
class Check:
    name: str
    script: Path
    weight: float = 1.0


@dataclass
class Case:
    name: str
    dir: Path
    prompt: str
    meta: dict
    scaffold: Path | None
    add_dirs: list[Path]
    graders: list[Grader]
    checks: list[Check] = field(default_factory=list)

    @property
    def tags(self) -> list[str]:
        return [str(t) for t in self.meta.get("tags", [])]

    @property
    def runs(self) -> int:
        return int(self.meta.get("runs", 3))

    @property
    def max_turns(self) -> int:
        return int(self.meta.get("max_turns", 10))

    @property
    def timeout_seconds(self) -> int:
        return int(self.meta.get("timeout_seconds", 300))

    @property
    def allowed_tools(self) -> list[str]:
        return [str(t) for t in self.meta.get("allowed_tools", [])]

    @property
    def append_system_prompt(self) -> str:
        return str(self.meta.get("append_system_prompt", "") or "")


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter dict, body). A file without frontmatter is all body."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            meta = yaml.safe_load("\n".join(lines[1:i])) or {}
            return meta, "\n".join(lines[i + 1:]).strip()
    return {}, text


def load_case(case_dir: Path) -> Case:
    meta, prompt = split_frontmatter((case_dir / "prompt.md").read_text(encoding="utf-8"))
    scaffold, add_dirs = None, []
    case_yaml = case_dir / "case.yaml"
    if case_yaml.exists():
        cfg = yaml.safe_load(case_yaml.read_text(encoding="utf-8")) or {}
        ctx = cfg.get("context") or {}
        if ctx.get("scaffold_script"):
            scaffold = case_dir / ctx["scaffold_script"]
        add_dirs = [case_dir / d for d in ctx.get("add_dirs", [])]
    graders = []
    for g in sorted((case_dir / "graders").glob("*.md")) if (case_dir / "graders").is_dir() else []:
        gmeta, body = split_frontmatter(g.read_text(encoding="utf-8"))
        graders.append(Grader(name=g.stem, type=str(gmeta.get("type", "")), fields=gmeta, body=body))
    checks = []
    harness_yaml = case_dir / "harness.yaml"
    if harness_yaml.exists():
        hcfg = yaml.safe_load(harness_yaml.read_text(encoding="utf-8")) or {}
        for c in hcfg.get("checks", []):
            checks.append(Check(name=str(c.get("name") or Path(c["script"]).stem), script=case_dir / c["script"],
                                weight=float(c.get("weight", 1))))
    return Case(name=str(meta.get("name") or case_dir.name), dir=case_dir, prompt=prompt, meta=meta,
                scaffold=scaffold, add_dirs=add_dirs, graders=graders, checks=checks)


def load_cases(eval_dir: Path) -> list[Case]:
    cases = []
    for d in sorted(eval_dir.iterdir()):
        if d.is_dir() and not d.name.startswith(("_", ".")) and (d / "prompt.md").exists():
            cases.append(load_case(d))
    return cases


def select(cases: list[Case], tags: list[str], names: list[str]) -> list[Case]:
    """Keep cases matching any tag and any name glob (both filters optional)."""
    out = []
    for c in cases:
        if tags and not any(t in c.tags for t in tags):
            continue
        if names and not any(fnmatch.fnmatch(c.name, n) or fnmatch.fnmatch(c.dir.name, n) for n in names):
            continue
        out.append(c)
    return out
