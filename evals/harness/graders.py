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
from guard import outside_writes
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
    if target == "tool_inputs":  # every tool call's input, whole: the trace keeps only its ends, each cut at 800
        return "\n".join(json.dumps(e["input"], default=str) for e in run.tool_uses), "tool inputs"
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
    # Isolated like the agent run (runner.py): without these the judge loads the user's plugins,
    # skills and MCP servers, whose tool definitions alone can exceed the context window
    options = ClaudeAgentOptions(system_prompt=JUDGE_SYSTEM, tools=[], allowed_tools=[], max_turns=1,
                                 model=model, permission_mode="dontAsk",
                                 setting_sources=[], strict_mcp_config=True)
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
    # Absolute paths: the check runs from inside the workspace, so a relative one (a regrade of
    # evals/results/<stamp>) would resolve a second time from there and find nothing.
    workspace, script = Path(run.workspace).resolve(), Path(check.script).resolve()
    env = dict(os.environ, EVAL_WORKSPACE=str(workspace), EVAL_CASE_DIR=str(script.parent.parent),
               EVAL_TRACE=str(Path(trace_path).resolve()) if trace_path else "", CONSTRUCTION_SKILLS_NO_BOOTSTRAP="1")
    try:
        from runner import find_bash
        proc = subprocess.run([find_bash(), py.as_posix(), script.as_posix()], cwd=workspace, env=env,
                              capture_output=True, text=True, timeout=600)
    except Exception as e:
        return GraderResult(check.name, "python", check.weight, False, f"could not run check: {e}")
    out = (proc.stdout + proc.stderr).strip()
    m = re.search(r"^score:\s*([01](?:\.\d+)?)\s*$", proc.stdout, re.MULTILINE)
    score = float(m.group(1)) if m else None
    passed = proc.returncode == 0  # the script decides; a printed score only gives partial credit on failure
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
    return results + grade_blockers(run)


# --- blockers: a run that does either scores 0, whatever its graders say ---------------------------
# Writing the project's CLAUDE.md is project-setup's job (David): exempt in that case only, any other skill
# changing it counts.
NOT_ORIGINALS = {"project-setup": {"CLAUDE.md"}}


def _mentions(run: RunResult, name: str) -> list[str]:
    """Where the run names a file: in its commands (tool inputs), its output (tool results, its own text), both or neither."""
    base = name.replace("\\", "/").rsplit("/", 1)[-1]
    commands = "\n".join(json.dumps(e.get("input"), default=str) for e in run.tool_uses)
    output = "\n".join(str(e.get("content") or e.get("text") or e.get("result") or "") for e in run.trace
                       if e.get("type") in ("tool_result", "assistant_text", "result"))
    return [where for where, text in (("commands", commands), ("output", output)) if base and base in text]


def _outside_detail(run: RunResult, commands: list[str]) -> tuple[bool, str]:
    hits = run.outside_files
    parts = []
    for h in hits or []:
        said = _mentions(run, h["name"])
        parts.append(f"{h['place']}: {h['name']} ({h['change']}{', hard place' if h['hard'] else ''}; "
                     + ("named in the run's " + " and ".join(said) if said else "not named by the run") + ")")
    if hits is None:
        parts.append("files outside not recorded (the run predates the check)")
    if commands:
        parts.append(f"commands that wrote outside: {commands[:5]}")
    if hits and run.overlapping_runs:
        parts.append(f"other runs active at the time: {run.overlapping_runs}")
    ok = not hits and not commands
    return ok, ("; ".join(parts) if parts else "nothing left outside the project folder, and no command wrote outside it")


def grade_blockers(run: RunResult) -> list[GraderResult]:
    outside = sorted(set(outside_writes(run.tool_uses, run.guard_log, str(run.ran_in or run.workspace))))
    outside_ok, outside_detail = _outside_detail(run, outside)
    exempt = NOT_ORIGINALS.get(run.case, set())
    changed = [f for f in run.modified_files if not f.startswith(".construction/") and f not in exempt]
    if run.deleted_files is None:
        deleted, note = [], "; deleted files not recorded (the run predates the check)"
    else:
        deleted, note = [f for f in run.deleted_files if not f.startswith(".construction/") and f not in exempt], ""
    block = run.agentcm_block
    if block is None:
        block_ok, block_detail = True, "AgentCM's block in CLAUDE.md not recorded (the run predates the check)"
    elif block.get("before") is None:
        block_ok, block_detail = True, "no AgentCM block in CLAUDE.md before the run"
    else:
        block_ok = block.get("after") == block["before"]
        block_detail = ("AgentCM's block in CLAUDE.md unchanged" if block_ok else
                        "AgentCM's block in CLAUDE.md changed or removed (it must come out byte for byte)")
    return [
        GraderResult("writes-inside-project", "blocker", 0, outside_ok, outside_detail),
        GraderResult("originals-intact", "blocker", 0, not changed and not deleted,
                     (f"original documents changed: {changed[:5]}; deleted: {deleted[:5]}" if changed or deleted
                      else "no original document changed or deleted") + note),
        GraderResult("agentcm-block-intact", "blocker", 0, block_ok, block_detail),
    ]


def mark(r: GraderResult) -> str:
    """PASS / FAIL, BLOCKER for a failed blocker, REPORT for a failed grader of weight 0 (listed, not scored)."""
    if r.passed:
        return "PASS"
    if r.type == "blocker":
        return "BLOCKER"
    return "REPORT" if r.weight == 0 else "FAIL"


def score(results: list[GraderResult]) -> float:
    if any(r.type == "blocker" and not r.passed for r in results):
        return 0.0
    total = sum(r.weight for r in results)
    if total == 0:
        return 0.0
    earned = sum(r.weight * (r.score if (r.score is not None and not r.passed) else (1.0 if r.passed else 0.0)) for r in results)
    return round(earned / total, 4)
