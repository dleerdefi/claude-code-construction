"""The llm judge runs isolated from the user's settings, plugins and MCP servers, like the agent run."""
import asyncio
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

import graders  # noqa: E402


class JudgeIsolation(unittest.TestCase):
    def test_judge_session_loads_no_user_settings_or_mcp_servers(self):
        seen = []

        async def fake_query(prompt, options):
            seen.append(options)
            return
            yield  # an async generator that yields nothing

        real = graders.query
        graders.query = fake_query
        try:
            asyncio.run(graders._judge_once("rubric", "material", "haiku"))
        finally:
            graders.query = real

        self.assertEqual(len(seen), 1)
        options = seen[0]
        self.assertEqual(options.setting_sources, [])
        self.assertTrue(options.strict_mcp_config)
        self.assertEqual(options.tools, [])


class JudgeCost(unittest.TestCase):
    """The eval budget counts the judge's calls (David): each call's cost is kept on its grader's result."""

    def test_each_votes_cost_adds_up_on_the_grader(self):
        costs = iter([0.004, 0.005, 0.006])

        async def fake_query(prompt, options):
            yield graders.AssistantMessage(content=[graders.TextBlock('{"verdict": "PASS", "reason": "ok"}')], model="haiku")
            yield graders.ResultMessage(subtype="success", duration_ms=1, duration_api_ms=1, is_error=False, num_turns=1,
                                        session_id="s", total_cost_usd=next(costs))

        real = graders.query
        graders.query = fake_query
        try:
            g = SimpleNamespace(name="answer", type="llm", weight=1, body="rubric", fields={"target": "trace"})
            run = SimpleNamespace(trace=[{"type": "assistant_text", "text": "done"}])
            r = asyncio.run(graders.grade_llm(g, run, graders.JudgeOptions(votes=3)))
        finally:
            graders.query = real

        self.assertTrue(r.passed)
        self.assertAlmostEqual(r.cost_usd, 0.015)
        self.assertAlmostEqual(graders.judge_cost([r, graders.GraderResult("f", "file_exists", 1, True)]), 0.015)

    def test_a_grader_kept_from_an_earlier_grading_costs_nothing_now(self):
        self.assertEqual(graders.judge_cost([graders.GraderResult("answer", "llm", 1, True, "kept")]), 0.0)


if __name__ == "__main__":
    unittest.main()
