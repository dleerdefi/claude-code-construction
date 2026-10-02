#!/usr/bin/env python3
"""Run the plugin's eval cases headlessly on Windows, macOS or Linux.

Usage (from the plugin root):
  bin/construction-python evals/harness/run.py --tag smoke --runs 1
  bin/construction-python evals/harness/run.py --case sheet-splitter --keep
  bin/construction-python evals/harness/run.py --dry-run

Reads the same cases as `claude plugin eval` (evals/plugin/<case>/). Results go
to evals/results/<timestamp>/ (summary.md, summary.json, per-run traces). Exit
code 0 when every case scores at or above --threshold, 1 otherwise, 2 on a
harness error.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cases import load_cases, select  # noqa: E402
from graders import JudgeOptions, grade_run, score  # noqa: E402
from report import write_run, write_summary  # noqa: E402
from runner import RunOptions, cleanup, run_case  # noqa: E402

PLUGIN_ROOT = HERE.parents[1]


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--eval-dir", default=str(PLUGIN_ROOT / "evals" / "plugin"), help="folder of case folders")
    p.add_argument("--tag", action="append", default=[], help="run cases with this tag (repeatable)")
    p.add_argument("--case", action="append", default=[], help="run cases whose folder or name matches this glob (repeatable)")
    p.add_argument("--runs", type=int, help="runs per case (default: the case's `runs`)")
    p.add_argument("--model", default="sonnet", help="model for the agent under test (default: sonnet)")
    p.add_argument("--judge-model", default="haiku", help="model for llm graders (default: haiku)")
    p.add_argument("--judge-votes", type=int, default=1, help="votes per llm grader; 3 matches plugin eval")
    p.add_argument("--budget-usd", type=float, default=3.0, help="hard spend cap per run (default: 3.0)")
    p.add_argument("--threshold", type=float, default=1.0, help="a case passes at or above this score (default: 1.0)")
    p.add_argument("--sandbox", choices=["auto", "off"], default="off",
                   help="auto: turn the OS sandbox on where one exists (macOS/Linux); no effect on Windows")
    p.add_argument("--keep", action="store_true", help="keep every workspace (failed runs are always kept)")
    p.add_argument("--output-dir", help="results folder (default: evals/results/<timestamp>)")
    p.add_argument("--dry-run", action="store_true", help="list the selected cases and graders, run nothing")
    return p.parse_args(argv)


async def main_async(args) -> int:
    cases = select(load_cases(Path(args.eval_dir)), args.tag, args.case)
    if not cases:
        print("no cases selected", file=sys.stderr)
        return 2
    if args.dry_run:
        for c in cases:
            print(f"{c.dir.name}: tags={c.tags} runs={args.runs or c.runs} max_turns={c.max_turns} "
                  f"timeout={c.timeout_seconds}s tools={c.allowed_tools}")
            for g in c.graders:
                print(f"    grader {g.name}: {g.type} w={g.weight:g}")
            for ch in c.checks:
                print(f"    check {ch.name}: {ch.script.name} w={ch.weight:g}")
        return 0

    stamp = time.strftime("%Y-%m-%dT%H-%M-%S")
    out_dir = Path(args.output_dir) if args.output_dir else PLUGIN_ROOT / "evals" / "results" / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    opts = RunOptions(plugin_root=PLUGIN_ROOT, model=args.model, budget_usd=args.budget_usd,
                      sandbox=args.sandbox, keep=args.keep)
    judge = JudgeOptions(model=args.judge_model, votes=args.judge_votes)

    summary = {"timestamp": stamp, "model": args.model, "judge_model": args.judge_model, "threshold": args.threshold,
               "cases": [], "total_cost_usd": 0.0, "passed": 0, "total": len(cases)}
    for case in cases:
        n_runs = args.runs or case.runs
        print(f"{case.dir.name} ({n_runs} run{'s' if n_runs != 1 else ''})")
        run_scores, run_details, cost = [], [], 0.0
        for i in range(1, n_runs + 1):
            run = await run_case(case, i, opts)
            run_dir = write_run(out_dir, run, [])
            graders = await grade_run(case, run, judge, PLUGIN_ROOT, run_dir / "trace.jsonl")
            write_run(out_dir, run, graders)
            s = score(graders)
            failed = s < args.threshold or run.is_error
            cleanup(run, failed=failed, keep=args.keep)
            run_scores.append(s)
            cost += run.cost_usd or 0.0
            for g in graders:
                print(f"      {'PASS' if g.passed else 'FAIL'} {g.name} ({g.type}): {g.detail[:160]}")
            run_details.append({"run_index": i, "score": s, "num_turns": run.num_turns, "elapsed_s": round(run.elapsed_s),
                                "cost_usd": run.cost_usd, "error": run.error, "graders": [g.__dict__ for g in graders],
                                "guard_denials": [d for d in run.guard_log if not d["allow"]],
                                "kept_workspace": str(run.workspace) if (failed or args.keep) else ""})
        case_score = round(sum(run_scores) / len(run_scores), 4)
        ok = case_score >= args.threshold
        notes = "; ".join(f"run {d['run_index']}: {d['error']}" for d in run_details if d["error"]) or ("pass" if ok else "below threshold")
        print(f"  score {case_score:.2f}  ${cost:.2f}  {'PASS' if ok else 'FAIL'}")
        summary["cases"].append({"name": case.dir.name, "score": case_score, "runs": n_runs, "cost_usd": cost,
                                 "notes": notes, "run_details": run_details})
        summary["total_cost_usd"] += cost
        summary["passed"] += ok
    write_summary(out_dir, summary)
    print(f"\n{summary['passed']}/{summary['total']} cases passed · total ${summary['total_cost_usd']:.2f} · report: {out_dir / 'summary.md'}")
    return 0 if summary["passed"] == summary["total"] else 1


def main() -> int:
    args = parse_args()
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    try:
        return asyncio.run(main_async(args))
    except KeyboardInterrupt:
        return 2


if __name__ == "__main__":
    sys.exit(main())
