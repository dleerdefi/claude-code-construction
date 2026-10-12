"""Negative examples: material an llm grader must judge a set way, kept beside the grader.

A case may hold `negatives/*.md`, each with frontmatter naming the llm grader it tests and the
verdict it must get (`expect: FAIL`, usually), and the material as its body. `run.py
--check-negatives` asks the judge, the same way the grader does, and fails when a verdict
differs: a rubric edit that lets a known-wrong answer pass shows at once, before a run is spent.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cases import Case, split_frontmatter
from graders import JudgeOptions, _judge_once


@dataclass
class Negative:
    path: Path
    grader: str
    expect: str  # "PASS" or "FAIL"
    material: str


def load_negatives(case: Case) -> list[Negative]:
    out = []
    for p in sorted((case.dir / "negatives").glob("*.md")):
        meta, body = split_frontmatter(p.read_text(encoding="utf-8"))
        out.append(Negative(p, str(meta.get("grader", "")), str(meta.get("expect", "FAIL")).upper(), body))
    return out


async def check_negative(case: Case, neg: Negative, judge: JudgeOptions) -> tuple[bool, str]:
    """(verdict as expected, detail). The verdict is the grader's: a majority of judge votes."""
    grader = next((g for g in case.graders if g.name == neg.grader and g.type == "llm"), None)
    if grader is None:
        return False, f"{case.name} has no llm grader named {neg.grader!r}"
    rubric = grader.body or grader.fields.get("rubric", "") or grader.name
    n = max(1, judge.votes)
    votes, reason = 0, ""
    for _ in range(n):
        ok, reason = await _judge_once(rubric, neg.material, judge.model)
        votes += ok
    verdict = "PASS" if votes * 2 > n else "FAIL"
    return verdict == neg.expect, f"{verdict} ({votes}/{n} pass votes), expected {neg.expect}: {reason[:200]}"
