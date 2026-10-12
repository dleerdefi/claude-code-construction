"""write_finding.py and query_findings.py: findings live in .construction/skills/<skill>/findings/ in both modes."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRITE = ROOT / "scripts" / "graph" / "write_finding.py"
QUERY = ROOT / "scripts" / "graph" / "query_findings.py"
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")


def construction_files(project):
    base = project / ".construction"
    return sorted(p.relative_to(base).as_posix() for p in base.rglob("*") if p.is_file()) if base.exists() else []


class Findings(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.project = Path(tmp.name)

    def write(self, *args):
        return subprocess.run([sys.executable, str(WRITE), *args], cwd=self.project, capture_output=True, text=True, env=ENV)

    def test_flat_file_finding_goes_to_the_skill_folder_and_creates_nothing_else(self):
        r = self.write("--skill", "bid-tabulator", "--type", "bid_tabulation", "--title", "5 bids", "--data", '{"bids": 5}')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        files = construction_files(self.project)
        self.assertEqual(len(files), 1, files)
        self.assertRegex(files[0], r"^skills/bid-tabulator/findings/\d{4}-\d{2}-\d{2}_bid_tabulation_[0-9a-f]{8}\.json$")
        self.assertFalse((self.project / ".construction" / "project.yaml").exists(),
                         "writing a finding must not make the folder look like an AgentCM project")
        entry = json.loads((self.project / ".construction" / files[0]).read_text(encoding="utf-8"))
        self.assertEqual((entry["skill"], entry["type"], entry["data"]), ("bid-tabulator", "bid_tabulation", {"bids": 5}))

    def test_agentcm_finding_goes_to_the_same_place_not_agent_findings(self):
        (self.project / ".construction").mkdir()
        (self.project / ".construction" / "project.yaml").write_text("project:\n  name: x\n", encoding="utf-8")
        r = self.write("--skill", "schedule-extractor", "--type", "schedule_extracted", "--title", "door schedule")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        files = construction_files(self.project)
        self.assertEqual([f for f in files if f != "project.yaml"][0].split("/")[:3], ["skills", "schedule-extractor", "findings"])
        self.assertFalse((self.project / ".construction" / "agent_findings").exists())

    def test_refuses_a_skill_name_that_is_not_a_folder_name(self):
        for bad in ("../issues", "Bid Tabulator", ""):
            r = self.write("--skill", bad, "--type", "t", "--title", "t")
            self.assertEqual(r.returncode, 2, bad)
        self.assertEqual(construction_files(self.project), [])

    def test_requires_the_skill(self):
        r = self.write("--type", "t", "--title", "t")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--skill", r.stderr)

    def test_query_reads_every_skill_and_filters_by_skill(self):
        self.write("--skill", "bid-tabulator", "--type", "bid_tabulation", "--title", "a")
        self.write("--skill", "bid-evaluator", "--type", "bid_evaluation", "--title", "b")
        everything = subprocess.run([sys.executable, str(QUERY)], cwd=self.project, capture_output=True, text=True, env=ENV)
        self.assertEqual(sorted(e["skill"] for e in json.loads(everything.stdout)), ["bid-evaluator", "bid-tabulator"])
        one = subprocess.run([sys.executable, str(QUERY), "--skill", "bid-evaluator"], cwd=self.project,
                             capture_output=True, text=True, env=ENV)
        self.assertEqual([e["type"] for e in json.loads(one.stdout)], ["bid_evaluation"])


if __name__ == "__main__":
    unittest.main()
