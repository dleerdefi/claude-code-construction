"""Grade a run with the grader types `claude plugin eval` uses, plus Python checks.

file_exists, regex, tool_used and tool_order are free. llm asks a judge model.
python runs a check script from the case's harness.yaml with construction-python.
"""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, ResultMessage, query
from claude_agent_sdk.types import TextBlock

from cases import Case, Check, Grader
from runner import RunResult

TRANSCRIPT_EDGE = 12  # the judge sees the first and last 12 messages, like plugin eval
TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".csv", ".py", ".sh", ".jsonl", ".html", ".xml", ".log", ""}
JUDGE_SYSTEM = ("You are grading an automated run of a software tool against a rubric. Answer with a JSON object "
                "only: {\"verdict\": \"PASS\" or \"FAIL\", \"reason\": \"one or two sentences\"}. PASS only when the "
                "rubric is clearly satisfied by the material shown.")


@dataclass
class GraderResult:
    name: str
    type: str
    weight: float
    passed: bool
    detail: str = ""
    score: float | None = None  # python checks may report a partial score


@dataclass
class JudgeOptions:
    model: str = "haiku"
    votes: int = 1


# --- helpers ----------------------------------------------------------------

def _created(run: RunResult, pattern: str) -> list[str]:
    matches = {Path(p).as_posix() for p in glob.glob(pattern, root_dir=run.workspace, recursive=True)}
    created = set(run.created_files)
    return sorted(matches & created)


def transcript(run: RunResult) -> str:
    """Condensed transcript: assistant text, tool calls, results. Edges only when long."""
    lines = []
    for e in run.trace:
        if e["type"] == "assistant_text":
            lines.append(f"ASSISTANT: {e['text']}")
        elif e["type"] == "tool_use":
            lines.append(f"TOOL_USE {e['name']}: {json.dumps(e['input'], default=str)[:800]}")
        elif e["type"] == "tool_result":
            lines.append(f"TOOL_RESULT{' (error)' if e.get('is_error') else ''}: {e['content'][:800]}")
        elif e["type"] == "result":
            lines.append(f"RESULT: {e.get('result', '')}")
    if len(lines) > 2 * TRANSCRIPT_EDGE:
        lines = lines[:TRANSCRIPT_EDGE] + [f"... {len(lines) - 2 * TRANSCRIPT_EDGE} messages omitted ..."] + lines[-TRANSCRIPT_EDGE:]
    return "\n".join(lines)


def _target_text(run: RunResult, target) -> tuple[str | None, str]:
    """Resolve a grader target to text. Returns (text, description); text None when unreadable."""
    if target in (None, "trace"):
        return transcript(run), "trace"
    if isinstance(target, dict) and target.get("source") == "file":
        rel = str(target.get("path", ""))
        p = run.workspace / rel
        if not p.exists():
            return None, f"file {rel} does not exist"
        if p.suffix.lower() not in TEXT_SUFFIXES:
            return None, f"file {rel} is binary; use a python check for it"
        return p.read_text(encoding="utf-8", errors="replace"), f"file {rel}"
    return None, f"unsupported target {target!r}"


# --- grader types -------------------------------------------------------------

def grade_file_exists(g: Grader, run: RunResult) -> GraderResult:
    pattern = str(g.fields.get("path", ""))
    want = bool(g.fields.get("exists", True))
    hits = _created(run, pattern)
    passed = bool(hits) if want else not hits
    detail = f"{len(hits)} created file(s) match {pattern!r}" + (f": {hits[:3]}" if hits else "")
    return GraderResult(g.name, g.type, g.weight, passed, detail)


def grade_regex(g: Grader, run: RunResult) -> GraderResult:
    text, where = _target_text(run, g.fields.get("target"))
    if text is None:
        return GraderResult(g.name, g.type, g.weight, False, where)
    pattern = str(g.fields.get("pattern", ""))
    mode = str(g.fields.get("match", "contains"))
    n = len(re.findall(pattern, text, re.MULTILINE))
    if mode == "not_contains":
        passed = n == 0
    elif mode.startswith("count:"):
        passed = n == int(mode.split(":", 1)[1])
    else:
        passed = n > 0
    return GraderResult(g.name, g.type, g.weight, passed, f"{n} match(es) for {pattern!r} in {where} ({mode})")


def grade_tool_used(g: Grader, run: RunResult) -> GraderResult:
    tool = str(g.fields.get("tool", ""))
    input_match = g.fields.get("input_match")
    lo, hi = int(g.fields.get("min", 1)), g.fields.get("max")
    calls = [e for e in run.tool_uses if e["name"] == tool]
    if input_match:
        calls = [e for e in calls if re.search(str(input_match), json.dumps(e["input"], default=str))]
    n = len(calls)
    passed = n >= lo and (hi is None or n <= int(hi))
    return GraderResult(g.name, g.type, g.weight, passed, f"{n} call(s) to {tool}" + (f" matching {input_match!r}" if input_match else ""))


def grade_tool_order(g: Grader, run: RunResult) -> GraderResult:
    before, after = str(g.fields.get("before", "")), str(g.fields.get("after", ""))
    names = [e["name"] for e in run.tool_uses]
    i = names.index(before) if before in names else -1
    j = names.index(after) if after in names else -1
    passed = i >= 0 and j >= 0 and i < j
    return GraderResult(g.name, g.type, g.weight, passed, f"first {before} at {i}, first {after} at {j}")


async def _judge_once(rubric: str, material: str, model: str) -> tuple[bool, str]:
    prompt = f"RUBRIC:\n{rubric.strip()}\n\nMATERIAL:\n{material}\n\nReply with the JSON object."
    options = ClaudeAgentOptions(system_prompt=JUDGE_SYSTEM, tools=[], allowed_tools=[], max_turns=1,
                                 model=model, permission_mode="dontAsk")
    text = ""
    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, AssistantMessage):
            text += "".join(b.text for b in msg.content if isinstance(b, TextBlock))
        elif isinstance(msg, ResultMessage) and msg.result and not text:
            text = msg.result
    m = re.search(r"\{.*\}", text, re.DOTALL)
    try:
        data = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        data = {}
    verdict = str(data.get("verdict", "")).upper() or ("PASS" if "PASS" in text.upper() and "FAIL" not in text.upper() else "FAIL")
    return verdict == "PASS", str(data.get("reason") or text[:300])


async def grade_llm(g: Grader, run: RunResult, judge: JudgeOptions) -> GraderResult:
    text, where = _target_text(run, g.fields.get("target"))
    if text is None:
        return GraderResult(g.name, g.type, g.weight, False, where)
    rubric = g.body or g.fields.get("rubric", "") or g.name
    votes, reasons = 0, []
    for _ in range(max(1, judge.votes)):
        ok, reason = await _judge_once(rubric, text, judge.model)
        votes += ok
        reasons.append(("PASS: " if ok else "FAIL: ") + reason)
    passed = votes * 2 > max(1, judge.votes)
    return GraderResult(g.name, g.type, g.weight, passed, f"{votes}/{judge.votes} votes on {where}; " + " | ".join(reasons))


def grade_python(check: Check, run: RunResult, plugin_root: Path, trace_path: Path | None) -> GraderResult:
    py = plugin_root / "bin" / "construction-python"
    env = dict(os.environ, EVAL_WORKSPACE=str(run.workspace), EVAL_CASE_DIR=str(check.script.parent.parent),
               EVAL_TRACE=str(trace_path or ""), CONSTRUCTION_SKILLS_NO_BOOTSTRAP="1")
    try:
        from runner import find_bash
        proc = subprocess.run([find_bash(), py.as_posix(), check.script.as_posix()], cwd=run.workspace, env=env,
                              capture_output=True, text=True, timeout=600)
    except Exception as e:
        return GraderResult(check.name, "python", check.weight, False, f"could not run check: {e}")
    out = (proc.stdout + proc.stderr).strip()
    m = re.search(r"^score:\s*([01](?:\.\d+)?)\s*$", proc.stdout, re.MULTILINE)
    score = float(m.group(1)) if m else None
    passed = proc.returncode == 0 and (score is None or score >= 1.0)
    return GraderResult(check.name, "python", check.weight, passed, out[-600:], score)


async def grade_run(case: Case, run: RunResult, judge: JudgeOptions, plugin_root: Path,
                    trace_path: Path | None = None) -> list[GraderResult]:
    results: list[GraderResult] = []
    for g in case.graders:
        if g.type == "file_exists":
            results.append(grade_file_exists(g, run))
        elif g.type == "regex":
            results.append(grade_regex(g, run))
        elif g.type == "tool_used":
            results.append(grade_tool_used(g, run))
        elif g.type == "tool_order":
            results.append(grade_tool_order(g, run))
        elif g.type == "llm":
            results.append(await grade_llm(g, run, judge))
        else:
            results.append(GraderResult(g.name, g.type, g.weight, False, f"unsupported grader type {g.type!r}"))
    for c in case.checks:
        results.append(grade_python(c, run, plugin_root, trace_path))
    return results


def score(results: list[GraderResult]) -> float:
    total = sum(r.weight for r in results)
    if total == 0:
        return 0.0
    earned = sum(r.weight * (r.score if (r.score is not None and not r.passed) else (1.0 if r.passed else 0.0)) for r in results)
    return round(earned / total, 4)
