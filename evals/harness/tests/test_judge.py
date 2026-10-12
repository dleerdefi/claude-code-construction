"""The llm judge runs isolated from the user's settings, plugins and MCP servers, like the agent run."""
import asyncio
import sys
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
