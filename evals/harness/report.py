"""Write run artifacts and the summary under evals/results/<timestamp>/."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from graders import GraderResult, score
from runner import RunResult


def write_run(out_dir: Path, run: RunResult, graders: list[GraderResult]) -> Path:
    d = out_dir / run.case / f"run-{run.run_index}"
    d.mkdir(parents=True, exist_ok=True)
    with (d / "trace.jsonl").open("w", encoding="utf-8") as f:
        for e in run.trace:
            f.write(json.dumps(e, default=str) + "\n")
    (d / "guard_log.json").write_text(json.dumps(run.guard_log, indent=1, default=str), encoding="utf-8")
    (d / "graders.json").write_text(json.dumps([asdict(g) for g in graders], indent=1), encoding="utf-8")
    (d / "run.json").write_text(json.dumps({
        "case": run.case, "run_index": run.run_index, "workspace": str(run.workspace), "score": score(graders),
        "elapsed_s": round(run.elapsed_s, 1), "num_turns": run.num_turns, "cost_usd": run.cost_usd,
        "subtype": run.subtype, "is_error": run.is_error, "error": run.error, "created_files": run.created_files,
        "guard_denials": [g for g in run.guard_log if not g["allow"]],
    }, indent=1, default=str), encoding="utf-8")
    return d


def write_summary(out_dir: Path, summary: dict) -> None:
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=1, default=str), encoding="utf-8")
    lines = [f"# Eval run {summary['timestamp']}", "",
             f"Model: {summary['model']} · judge: {summary['judge_model']} · threshold: {summary['threshold']}", "",
             "| Case | Score | Runs | Cost | Notes |", "|---|---|---|---|---|"]
    for c in summary["cases"]:
        lines.append(f"| {c['name']} | {c['score']:.2f} | {c['runs']} | ${c['cost_usd']:.2f} | {c['notes']} |")
    ran = summary["total"] - summary.get("skipped", 0)
    lines += ["", f"Total cost: ${summary['total_cost_usd']:.2f} · {summary['passed']}/{ran} cases at or above threshold"
              + (f" · {summary['skipped']} skipped" if summary.get("skipped") else ""), ""]
    for c in summary["cases"]:
        lines.append(f"## {c['name']}")
        for r in c["run_details"]:
            lines.append(f"- run {r['run_index']}: score {r['score']:.2f}, {r['num_turns']} turns, {r['elapsed_s']}s, ${r['cost_usd'] or 0:.2f}"
                         + (f", error: {r['error']}" if r["error"] else ""))
            for g in r["graders"]:
                mark = "PASS" if g["passed"] else "FAIL"
                lines.append(f"    - {mark} {g['name']} ({g['type']}, w={g['weight']:g}): {g['detail'][:300]}")
            if r["guard_denials"]:
                lines.append(f"    - guard denied {len(r['guard_denials'])} call(s): "
                             + "; ".join(str(d['input'].get('command', d['input'].get('file_path', '')))[:80] for d in r["guard_denials"]))
            if r["kept_workspace"]:
                lines.append(f"    - workspace kept: {r['kept_workspace']}")
        lines.append("")
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
