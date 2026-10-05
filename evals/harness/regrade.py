"""Re-grade saved runs with the current graders, without re-running the agent.

A run folder (evals/results/<stamp>/<case>/run-N/) holds everything a grader
reads except the workspace: trace.jsonl, guard_log.json and run.json (which
records the workspace path and the files the run created). Trace graders
(tool_used, tool_order, regex on the trace) are always re-evaluated. Graders
that read the workspace (file_exists, regex or llm on a file, python checks)
are re-evaluated when the workspace still exists (failed runs keep theirs) and
otherwise keep their stored verdict. llm graders keep their stored verdict
unless --rejudge is given, since each vote costs a judge call; a new llm grader
with no stored verdict is judged regardless.
"""
from __future__ import annotations

import json
from pathlib import Path

from cases import Case
from graders import (GraderResult, JudgeOptions, grade_file_exists, grade_llm, grade_python, grade_regex,
                     grade_tool_order, grade_tool_used)
from runner import RunResult

KEPT = "kept from the original grading"


def load_saved_run(run_dir: Path, case_name: str) -> tuple[RunResult, dict[str, dict]]:
    """The RunResult a saved run folder describes, and its stored grader results by name."""
    meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    trace = [json.loads(line) for line in (run_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    guard_path = run_dir / "guard_log.json"
    guard_log = json.loads(guard_path.read_text(encoding="utf-8")) if guard_path.exists() else []
    run = RunResult(case=case_name, run_index=int(meta.get("run_index", run_dir.name.rsplit("-", 1)[-1])),
                    workspace=Path(meta["workspace"]), trace=trace, guard_log=guard_log,
                    created_files=list(meta.get("created_files", [])), elapsed_s=float(meta.get("elapsed_s", 0.0)),
                    num_turns=meta.get("num_turns"), cost_usd=meta.get("cost_usd"), subtype=meta.get("subtype", ""),
                    is_error=bool(meta.get("is_error")), error=meta.get("error") or "")
    stored_path = run_dir / "graders.json"
    stored = {g["name"]: g for g in json.loads(stored_path.read_text(encoding="utf-8"))} if stored_path.exists() else {}
    return run, stored


def _kept(stored: dict | None, name: str, gtype: str, weight: float, why: str) -> GraderResult:
    if stored is None:
        return GraderResult(name, gtype, weight, False, f"not evaluated: new grader and {why}")
    return GraderResult(name, gtype, weight, bool(stored["passed"]), f"{KEPT} ({why}): {stored.get('detail', '')}",
                        stored.get("score"))


def _reads_workspace(g) -> bool:
    if g.type == "file_exists":
        return True
    target = g.fields.get("target")
    return isinstance(target, dict) and target.get("source") == "file"


async def regrade_run(case: Case, run: RunResult, stored: dict[str, dict], judge: JudgeOptions, plugin_root: Path,
                      trace_path: Path, rejudge: bool) -> list[GraderResult]:
    workspace_ok = run.workspace.exists()
    results: list[GraderResult] = []
    for g in case.graders:
        prior = stored.get(g.name)
        if _reads_workspace(g) and not workspace_ok:
            results.append(_kept(prior, g.name, g.type, g.weight, "workspace gone"))
        elif g.type == "file_exists":
            results.append(grade_file_exists(g, run))
        elif g.type == "regex":
            results.append(grade_regex(g, run))
        elif g.type == "tool_used":
            results.append(grade_tool_used(g, run))
        elif g.type == "tool_order":
            results.append(grade_tool_order(g, run))
        elif g.type == "llm":
            if prior is not None and not rejudge:
                results.append(_kept(prior, g.name, g.type, g.weight, "no --rejudge"))
            else:
                results.append(await grade_llm(g, run, judge))
        else:
            results.append(GraderResult(g.name, g.type, g.weight, False, f"unsupported grader type {g.type!r}"))
    for c in case.checks:
        if workspace_ok:
            results.append(grade_python(c, run, plugin_root, trace_path))
        else:
            results.append(_kept(stored.get(c.name), c.name, "python", c.weight, "workspace gone"))
    return results
