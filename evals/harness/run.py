#!/usr/bin/env python3
"""Run the plugin's eval cases headlessly on Windows, macOS or Linux.

Usage (from the plugin root):
  bin/construction-python evals/harness/run.py --tag smoke --runs 1
  bin/construction-python evals/harness/run.py --case sheet-splitter --keep
  bin/construction-python evals/harness/run.py --dry-run
  bin/construction-python evals/harness/run.py --regrade evals/results/2026-10-04T23-51-00

Reads the same cases as `claude plugin eval` (evals/plugin/<case>/). Results go
to evals/results/<timestamp>/ (summary.md, summary.json, per-run traces). Exit
code 0 when every case scores at or above --threshold, 1 otherwise, 2 on a
harness error.

--regrade re-grades the runs saved in a results folder with the current
graders and writes a new results folder; the agent is not run, so a changed
grader costs nothing to check. Graders that need the workspace keep their
stored verdict when the workspace is gone; llm graders keep theirs unless
--rejudge.
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
from regrade import load_saved_run, regrade_run  # noqa: E402
from report import write_run, write_summary, write_trace  # noqa: E402
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
    p.add_argument("--regrade", metavar="RESULTS_DIR", help="re-grade the runs saved in this results folder; run nothing")
    p.add_argument("--rejudge", action="store_true", help="with --regrade: ask the judge again for llm graders")
    return p.parse_args(argv)


async def regrade_async(args, cases) -> int:
    src = Path(args.regrade)
    if not src.is_dir():
        print(f"{src} is not a results folder", file=sys.stderr)
        return 2
    stamp = time.strftime("%Y-%m-%dT%H-%M-%S")
    out_dir = Path(args.output_dir) if args.output_dir else PLUGIN_ROOT / "evals" / "results" / f"{stamp}-regrade"
    out_dir.mkdir(parents=True, exist_ok=True)
    judge = JudgeOptions(model=args.judge_model, votes=args.judge_votes)
    by_name = {c.dir.name: c for c in cases}
    summary = {"timestamp": stamp, "regraded_from": str(src), "model": "(regrade)", "judge_model": args.judge_model,
               "threshold": args.threshold, "cases": [], "total_cost_usd": 0.0, "passed": 0, "skipped": 0, "total": 0}
    for case_dir in sorted(p for p in src.iterdir() if p.is_dir() and p.name in by_name):
        case = by_name[case_dir.name]
        run_dirs = sorted((p for p in case_dir.iterdir() if p.is_dir() and (p / "run.json").exists()),
                          key=lambda p: int(p.name.rsplit("-", 1)[-1]))
        if not run_dirs:
            continue
        summary["total"] += 1
        print(f"{case.dir.name} ({len(run_dirs)} saved run{'s' if len(run_dirs) != 1 else ''})")
        run_scores, run_details, cost = [], [], 0.0
        for run_dir in run_dirs:
            run, stored, source = load_saved_run(run_dir, case.dir.name)
            new_dir = write_trace(out_dir, run)
            graders = await regrade_run(case, run, stored, judge, PLUGIN_ROOT, new_dir / "trace.jsonl", args.rejudge,
                                        source)
            write_run(out_dir, run, graders)
            s = score(graders)
            run_scores.append(s)
            cost += run.cost_usd or 0.0
            for g in graders:
                print(f"      {'PASS' if g.passed else 'FAIL'} {g.name} ({g.type}): {g.detail[:160]}")
            run_details.append({"run_index": run.run_index, "score": s, "num_turns": run.num_turns,
                                "elapsed_s": round(run.elapsed_s), "cost_usd": run.cost_usd, "error": run.error,
                                "graders": [g.__dict__ for g in graders],
                                "guard_denials": [d for d in run.guard_log if not d["allow"]],
                                "kept_workspace": str(run.workspace) if source == "workspace" else ""})
        case_score = round(sum(run_scores) / len(run_scores), 4)
        ok = case_score >= args.threshold
        print(f"  score {case_score:.2f}  {'PASS' if ok else 'FAIL'}")
        summary["cases"].append({"name": case.dir.name, "score": case_score, "runs": len(run_dirs), "cost_usd": cost,
                                 "notes": ("pass" if ok else "below threshold") + f" (regraded from {src.name})",
                                 "run_details": run_details})
        summary["total_cost_usd"] += cost
        summary["passed"] += ok
    if not summary["total"]:
        print(f"no saved runs in {src} match the selected cases", file=sys.stderr)
        return 2
    write_summary(out_dir, summary)
    print(f"\n{summary['passed']}/{summary['total']} cases pass with the current graders (original agent cost "
          f"${summary['total_cost_usd']:.2f}, nothing spent now) · report: {out_dir / 'summary.md'}")
    return 0 if summary["passed"] == summary["total"] else 1


async def main_async(args) -> int:
    cases = select(load_cases(Path(args.eval_dir)), args.tag, args.case)
    if not cases:
        print("no cases selected", file=sys.stderr)
        return 2
    if args.regrade:
        return await regrade_async(args, cases)
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
               "cases": [], "total_cost_usd": 0.0, "passed": 0, "skipped": 0, "total": len(cases)}
    for case in cases:
        n_runs = args.runs or case.runs
        print(f"{case.dir.name} ({n_runs} run{'s' if n_runs != 1 else ''})")
        run_scores, run_details, cost = [], [], 0.0
        skipped_reason = ""
        for i in range(1, n_runs + 1):
            run = await run_case(case, i, opts)
            if run.skipped:
                skipped_reason = run.error
                break
            run_dir = write_trace(out_dir, run)
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
        if skipped_reason:
            print(f"  SKIPPED  {skipped_reason.splitlines()[0][:160]}")
            summary["cases"].append({"name": case.dir.name, "score": 0.0, "runs": 0, "cost_usd": 0.0,
                                     "notes": "skipped: " + skipped_reason.splitlines()[0][:200], "run_details": []})
            summary["skipped"] += 1
            continue
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
    for stream in (sys.stdout, sys.stderr):  # grader verdicts contain characters a cp1252 console cannot print
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    try:
        return asyncio.run(main_async(args))
    except KeyboardInterrupt:
        return 2


if __name__ == "__main__":
    sys.exit(main())
