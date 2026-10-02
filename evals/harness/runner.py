"""One eval run: workspace, scaffold, headless Claude session, trace capture.

The session is driven through the Agent SDK with the plugin loaded from the
repo, the case's tools pre-approved, and the guard installed as a PreToolUse
hook. On Windows the SDK needs the native Claude Code install (claude.exe); it
refuses npm's claude.cmd shim.
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, HookMatcher, ResultMessage,
                              SystemMessage, UserMessage, query)
from claude_agent_sdk.types import TextBlock, ToolResultBlock, ToolUseBlock

from cases import Case
from guard import GUARDED_TOOLS, Policy, decide

SCAFFOLD_TIMEOUT = 120
RESULT_TEXT_LIMIT = 4000
TOOL_RESULT_LIMIT = 2000


@dataclass
class RunOptions:
    plugin_root: Path
    model: str = "sonnet"
    budget_usd: float = 3.0
    sandbox: str = "off"  # "auto" turns the OS sandbox on where one exists (macOS/Linux)
    keep: bool = False
    disallowed_tools: tuple[str, ...] = ("WebFetch", "WebSearch", "PowerShell")


@dataclass
class RunResult:
    case: str
    run_index: int
    workspace: Path
    trace: list[dict] = field(default_factory=list)
    guard_log: list[dict] = field(default_factory=list)
    created_files: list[str] = field(default_factory=list)
    elapsed_s: float = 0.0
    num_turns: int | None = None
    cost_usd: float | None = None
    subtype: str = ""
    is_error: bool = False
    error: str = ""
    result_text: str = ""

    @property
    def tool_uses(self) -> list[dict]:
        return [e for e in self.trace if e["type"] == "tool_use"]


def find_bash() -> str:
    """Git Bash, preferred over any WSL bash on PATH (the skills themselves require Git Bash)."""
    env = os.environ.get("CLAUDE_CODE_GIT_BASH_PATH")
    if env and Path(env).exists():
        return env
    if os.name == "nt":
        for cand in (r"C:\Program Files\Git\bin\bash.exe", r"C:\Program Files\Git\usr\bin\bash.exe",
                     os.path.expandvars(r"%LOCALAPPDATA%\Programs\Git\bin\bash.exe")):
            if Path(cand).exists():
                return cand
    found = shutil.which("bash")
    if not found:
        raise RuntimeError("bash not found; install Git for Windows or a system bash")
    return found


def snapshot(workspace: Path) -> set[str]:
    return {p.relative_to(workspace).as_posix() for p in workspace.rglob("*") if p.is_file()}


def make_workspace(case: Case, run_index: int) -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    ws = Path(tempfile.gettempdir()) / "construction-eval" / f"{case.dir.name}-{stamp}-r{run_index}"
    ws.mkdir(parents=True, exist_ok=False)
    return ws


def run_scaffold(case: Case, workspace: Path) -> str:
    """Run the case's setup.sh in the workspace. Returns captured output; raises on failure."""
    if not case.scaffold:
        return ""
    env = dict(os.environ, CONSTRUCTION_EVAL_HARNESS="1")
    proc = subprocess.run([find_bash(), case.scaffold.as_posix()], cwd=workspace, env=env,
                          capture_output=True, text=True, timeout=SCAFFOLD_TIMEOUT)
    out = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        raise RuntimeError(f"scaffold failed (exit {proc.returncode}):\n{out}")
    return out


def _block_summary(block) -> dict | None:
    if isinstance(block, TextBlock):
        return {"type": "assistant_text", "text": block.text}
    if isinstance(block, ToolUseBlock):
        return {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}
    if isinstance(block, ToolResultBlock):
        content = block.content if isinstance(block.content, str) else json.dumps(block.content, default=str)
        return {"type": "tool_result", "tool_use_id": block.tool_use_id, "is_error": bool(block.is_error),
                "content": content[:TOOL_RESULT_LIMIT]}
    return None


async def _session(case: Case, workspace: Path, opts: RunOptions, result: RunResult) -> None:
    policy = Policy(workspace=str(workspace), plugin_root=str(opts.plugin_root),
                    extra_roots=tuple(str(d) for d in case.add_dirs))

    async def guard_hook(input_data, tool_use_id, context):
        name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {}) or {}
        d = decide(name, tool_input, policy)
        result.guard_log.append({"tool": name, "allow": d.allow, "reason": d.reason,
                                 "input": {k: (v[:500] if isinstance(v, str) else v) for k, v in tool_input.items()}})
        if d.allow:
            return {}
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                       "permissionDecisionReason": d.reason}}

    allowed = case.allowed_tools or ["Read", "Glob", "Grep"]
    disallowed = [t for t in opts.disallowed_tools if t not in allowed]
    options = ClaudeAgentOptions(
        cwd=str(workspace),
        plugins=[{"type": "local", "path": str(opts.plugin_root)}],
        allowed_tools=allowed,
        disallowed_tools=disallowed,
        permission_mode="acceptEdits",
        hooks={"PreToolUse": [HookMatcher(matcher="|".join(GUARDED_TOOLS), hooks=[guard_hook])]},
        system_prompt={"type": "preset", "preset": "claude_code", "append": case.append_system_prompt}
        if case.append_system_prompt else {"type": "preset", "preset": "claude_code"},
        max_turns=case.max_turns,
        max_budget_usd=opts.budget_usd,
        model=opts.model,
        add_dirs=[str(d) for d in case.add_dirs],
        env={"CONSTRUCTION_SKILLS_NO_BOOTSTRAP": "1"},
        sandbox={"enabled": True} if opts.sandbox == "auto" and sys.platform != "win32" else None,
        stderr=lambda line: result.trace.append({"type": "stderr", "line": line}),
    )
    async for msg in query(prompt=case.prompt, options=options):
        if isinstance(msg, SystemMessage):
            keep = {k: msg.data.get(k) for k in ("model", "permissionMode", "tools", "plugins", "plugin_errors") if k in msg.data}
            result.trace.append({"type": "system", "subtype": msg.subtype, "data": keep})
        elif isinstance(msg, (AssistantMessage, UserMessage)):
            content = msg.content if isinstance(msg.content, list) else []
            for b in content:
                s = _block_summary(b)
                if s:
                    result.trace.append(s)
        elif isinstance(msg, ResultMessage):
            result.num_turns = msg.num_turns
            result.cost_usd = msg.total_cost_usd
            result.subtype = msg.subtype
            result.is_error = msg.is_error
            result.result_text = (msg.result or "")[:RESULT_TEXT_LIMIT]
            if msg.errors:
                result.error = "; ".join(str(e) for e in msg.errors)
            result.trace.append({"type": "result", "subtype": msg.subtype, "is_error": msg.is_error,
                                 "num_turns": msg.num_turns, "total_cost_usd": msg.total_cost_usd,
                                 "duration_ms": msg.duration_ms, "permission_denials": msg.permission_denials,
                                 "errors": msg.errors, "result": result.result_text})


async def run_case(case: Case, run_index: int, opts: RunOptions, log=print) -> RunResult:
    workspace = make_workspace(case, run_index)
    result = RunResult(case=case.name, run_index=run_index, workspace=workspace)
    t0 = time.time()
    try:
        scaffold_out = run_scaffold(case, workspace)
        if scaffold_out:
            result.trace.append({"type": "scaffold", "output": scaffold_out[:TOOL_RESULT_LIMIT]})
        before = snapshot(workspace)
        try:
            await asyncio.wait_for(_session(case, workspace, opts, result), timeout=case.timeout_seconds)
        except asyncio.TimeoutError:
            result.is_error = True
            result.error = f"timed out after {case.timeout_seconds}s"
        result.created_files = sorted(snapshot(workspace) - before)
    except Exception as e:  # scaffold or transport failure: the run is an error, not a crash
        result.is_error = True
        result.error = f"{type(e).__name__}: {e}"
    result.elapsed_s = time.time() - t0
    log(f"    run {run_index}: {result.num_turns or '?'} turns, {result.elapsed_s:.0f}s, "
        f"${(result.cost_usd or 0):.2f}, {len(result.created_files)} files created"
        + (f", ERROR: {result.error}" if result.error else ""))
    return result


def cleanup(result: RunResult, failed: bool, keep: bool) -> None:
    if keep or failed:
        return
    shutil.rmtree(result.workspace, ignore_errors=True)
