"""dev/check_no_queries.py: any reference to AgentCM's database in what the plugin ships fails."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dev"))

import check_no_queries as cnq  # noqa: E402


def tree(files):
    d = tempfile.TemporaryDirectory()
    for rel, text in files.items():
        p = Path(d.name) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return d


class NoQueries(unittest.TestCase):
    def test_each_name_is_found(self):
        with tree({
            "skills/a/SKILL.md": 'Run `sh .construction/query.sh "SELECT 1"`.\n',
            "skills/b/references/r.md": "Use powershell -File .construction/query.ps1.\n",
            "reference/agentcm-mode.md": "Never read query_command.\n",
            "scripts/x.py": 'parser.add_argument("--query-wrapper")\n',
            "skills/c/scripts/y.sh": "psql -c 'select 1'\n",
        }) as d:
            found = {(rel, hit) for rel, _, hit, _ in cnq.scan(Path(d))}
        self.assertEqual(found, {
            ("skills/a/SKILL.md", "query.sh"), ("skills/b/references/r.md", "query.ps1"),
            ("reference/agentcm-mode.md", "query_command"), ("scripts/x.py", "query-wrapper"),
            ("skills/c/scripts/y.sh", "psql"),
        })

    def test_file_reads_and_unshipped_folders_pass(self):
        with tree({
            "skills/a/SKILL.md": "Read `.construction/tags.tsv`; GET {api_url}/projects/{id}/schedules/{s}/rows.\n",
            "evals/plugin/case/graders/no-db.md": "pattern: query\\.sh|psql\n",
            "docs/notes.md": "query.sh was removed in 0.6.0\n",
        }) as d:
            self.assertEqual(cnq.scan(Path(d)), [])
            self.assertEqual(cnq.main([d]), 0)

    def test_the_repo_is_clean(self):
        self.assertEqual(cnq.scan(ROOT), [])


if __name__ == "__main__":
    unittest.main()
