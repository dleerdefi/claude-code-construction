"""The no-database-query check (David): a run that calls query.sh, query.ps1 or psql is reported in every case for
0.6.0, and scores 0 once AgentCM's guide tells a running skill to read the files. Reading the script, listing it or
searching for its name is not a call. Run: bin/construction-python -m unittest discover evals/harness/tests"""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import graders  # noqa: E402
from graders import grade_blockers, mark, score, GraderResult  # noqa: E402
from guard import database_calls, database_queries  # noqa: E402
from runner import RunResult  # noqa: E402


def bash(command):
    return {"type": "tool_use", "name": "Bash", "input": {"command": command}}


class Calls(unittest.TestCase):
    def assertCalls(self, command):
        self.assertTrue(database_calls(command), command)

    def assertNoCall(self, command):
        self.assertEqual(database_calls(command), [], command)

    def test_the_guides_own_spellings(self):
        self.assertCalls('sh .construction/query.sh "SELECT count(*) FROM v_room_profile"')
        self.assertCalls('powershell -File .construction/query.ps1 "SELECT 1"')

    def test_the_script_run_directly_or_through_a_wrapper(self):
        for c in ('./.construction/query.sh "SELECT 1"', '.construction/query.sh "SELECT 1"',
                  'bash .construction/query.sh "SELECT 1"', 'cd .construction && sh query.sh "SELECT 1"',
                  'source .construction/query.sh', 'timeout 30 sh .construction/query.sh "SELECT 1"',
                  'env PGPASSWORD=x sh .construction/query.sh "SELECT 1"', 'pwsh -NoProfile -File .construction/query.ps1 x'):
            self.assertCalls(c)

    def test_psql_however_it_is_reached(self):
        for c in ('psql -h 127.0.0.1 -c "SELECT 1"', 'PGPASSWORD=x psql -U agentcm', '"C:/Program Files/PostgreSQL/16/bin/psql.exe" -c x',
                  'echo "SELECT 1" | psql', 'psql <<EOF\nSELECT 1;\nEOF', 'n=$(psql -tAc "SELECT count(*) FROM rooms")',
                  'bash -c "psql -c \'SELECT 1\'"', 'ls; psql -c x', 'powershell -Command "& .construction/query.ps1 \'SELECT 1\'"'):
            self.assertCalls(c)

    def test_reading_listing_or_searching_is_not_a_call(self):
        for c in ('cat .construction/query.sh', 'ls -la .construction/query.sh .construction/query.ps1',
                  'grep -n psql .construction/CLAUDE.md', 'echo "the guide says: sh .construction/query.sh"',
                  'grep -rn "query.sh" .construction/', 'head .construction/database.yaml'):
            self.assertNoCall(c)

    def test_a_quoted_semicolon_does_not_make_a_command(self):
        self.assertNoCall('grep -n "x; psql" notes.txt')


class Blocker(unittest.TestCase):
    def run_with(self, *commands, refused=()):
        run = RunResult(case="agentcm-mode-rfi-drafter", run_index=1, workspace=Path("ws"),
                        trace=[bash(c) for c in commands],
                        guard_log=[{"tool": "Bash", "allow": False, "reason": "x", "input": {"command": c}} for c in refused])
        return run

    def blocker(self, run):
        return next(r for r in grade_blockers(run) if r.name == "no-database-query")

    def test_for_0_6_0_a_query_is_reported_not_scored(self):
        run = self.run_with("grep -n 1607 .construction/tags.tsv", 'sh .construction/query.sh "SELECT 1"')
        r = self.blocker(run)
        self.assertFalse(r.passed)
        self.assertIn("query.sh", r.detail)
        self.assertEqual(mark(r), "REPORT")
        self.assertEqual(score([GraderResult("g", "regex", 1, True, ""), r]), 1.0)

    def test_once_the_guide_says_so_a_query_scores_the_run_zero(self):
        run = self.run_with('sh .construction/query.sh "SELECT 1"')
        with mock.patch.object(graders, "DATABASE_QUERY_BLOCKS", True):
            r = self.blocker(run)
        self.assertEqual(mark(r), "BLOCKER")
        self.assertEqual(score([GraderResult("g", "regex", 1, True, ""), r]), 0.0)

    def test_a_run_that_only_reads_the_files_passes(self):
        r = self.blocker(self.run_with("grep -n 1607 .construction/tags.tsv", "cat .construction/query.sh"))
        self.assertTrue(r.passed)
        self.assertEqual(r.detail, "no call to query.sh, query.ps1 or psql")

    def test_a_refused_call_still_counts(self):
        found = database_queries([bash("psql -c x")], [{"allow": False, "input": {"command": "psql -c x"}}])
        self.assertEqual(found, ["psql -c x (refused by the guard)"])


if __name__ == "__main__":
    unittest.main()
