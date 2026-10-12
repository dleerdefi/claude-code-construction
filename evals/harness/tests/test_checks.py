"""The shared no-agentcm-writes check: .construction/skills/ is allowed, anything else under .construction/ fails."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECK = Path(__file__).resolve().parents[2] / "plugin" / "_checks" / "no_agentcm_writes.py"


def run_check(workspace: Path):
    return subprocess.run([sys.executable, str(CHECK)], capture_output=True, text=True,
                          env=dict(os.environ, EVAL_WORKSPACE=str(workspace)))


class NoAgentcmWrites(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.ws = Path(tmp.name)

    def touch(self, rel):
        p = self.ws / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8")

    def test_passes_without_a_construction_folder(self):
        self.assertEqual(run_check(self.ws).returncode, 0)

    def test_passes_on_skills_working_data_and_findings(self):
        self.touch(".construction/skills/bid-tabulator/bids/a.json")
        self.touch(".construction/skills/bid-tabulator/findings/2026-10-12_bid_tabulation_complete_0a1b2c3d.json")
        self.touch(".construction/skills/spec_text/manifest.json")
        self.assertEqual(run_check(self.ws).returncode, 0)

    def test_fails_on_anything_else_under_construction(self):
        for rel in (".construction/agent_findings/x.json", ".construction/project.yaml",
                    ".construction/index/sheet_index.yaml", ".construction/spec_text/01_10_00.txt"):
            with self.subTest(rel=rel):
                self.touch(rel)
                r = run_check(self.ws)
                self.assertEqual(r.returncode, 1)
                self.assertIn(rel, r.stdout)
                (self.ws / rel).unlink()


if __name__ == "__main__":
    unittest.main()
