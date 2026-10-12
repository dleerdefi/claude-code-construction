"""corrections_append.py: one checked line per correction, appended to .construction/skills/corrections.tsv."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "corrections_append.py"
HEADER = "sheet\tx\ty\tw\th\tkind\tcrop\tagentcm\tdrawing"
INDEX_MD = """# AgentCM agent index: Test

## Drawing sheets (2)

| Sheet | Title | Rev | Date | Discipline | Text | Lines | Agent file | PDF | Page |
|---|---|---|---|---|---|---|---|---|---|
| A-101 | FIRST FLOOR PLAN |  |  | A | full | 120 | sheets/A-101.txt | 01 - Drawings/Arch.pdf | 3 |
| A-601 | DOOR SCHEDULE |  |  | A | full | 80 | sheets/A-601.txt | 01 - Drawings/Arch.pdf | 9 |

## Pages not yet named (1)

| Sheet | Title | Rev | Date | Discipline | Text | Lines | Agent file | PDF | Page |
|---|---|---|---|---|---|---|---|---|---|
| Arch-p12 |  |  |  |  | partial | 4 | sheets/Arch-p12.txt | 01 - Drawings/Arch.pdf | 12 |
"""
GOOD = ["--sheet", "A-101", "--x", "0.41", "--y", "0.22", "--w", "0.08", "--h", "0.03", "--kind", "room",
        "--crop", ".construction/crops/A-101_0.41_0.22_0.08_0.03.png",
        "--agentcm", "EXISTING DT WOMEN'S RESTROOM", "--drawing", "EXISTING WOMEN'S RESTROOM"]


def with_arg(args, name, value):
    out = list(args)
    out[out.index(f"--{name}") + 1] = value
    return out


class CorrectionsAppend(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / ".construction").mkdir()
        (self.root / ".construction" / "project.yaml").write_text("project:\n  contract_version: 1\n", encoding="utf-8")
        (self.root / ".construction" / "INDEX.md").write_text(INDEX_MD, encoding="utf-8")
        self.tsv = self.root / ".construction" / "skills" / "corrections.tsv"

    def run_script(self, args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.root, capture_output=True, text=True,
                              env=dict(os.environ, PYTHONIOENCODING="utf-8"))

    def assertRefused(self, args, reason):
        before = self.tsv.read_bytes() if self.tsv.exists() else None
        r = self.run_script(args)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn(reason, r.stdout)
        self.assertEqual(self.tsv.read_bytes() if self.tsv.exists() else None, before, "a refusal must write nothing")

    def test_first_use_writes_the_header_then_the_line(self):
        r = self.run_script(GOOD)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        raw = self.tsv.read_bytes()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), "no BOM")
        self.assertNotIn(b"\r\n", raw)
        lines = raw.decode("utf-8").split("\n")
        self.assertEqual(lines[0], HEADER)
        self.assertEqual(lines[1].split("\t"), ["A-101", "0.41", "0.22", "0.08", "0.03", "room",
                                                ".construction/crops/A-101_0.41_0.22_0.08_0.03.png",
                                                "EXISTING DT WOMEN'S RESTROOM", "EXISTING WOMEN'S RESTROOM"])
        self.assertEqual(lines[2], "")
        self.assertIn(lines[1], r.stdout)

    def test_tabs_and_line_breaks_become_spaces(self):
        r = self.run_script(with_arg(with_arg(GOOD, "drawing", "EXISTING\tWOMEN'S\nRESTROOM"), "agentcm", "line one\r\nline two"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        row = self.tsv.read_text(encoding="utf-8").split("\n")[1].split("\t")
        self.assertEqual(len(row), 9)
        self.assertEqual((row[7], row[8]), ("line one line two", "EXISTING WOMEN'S RESTROOM"))

    def test_two_appends_keep_both_lines(self):
        self.run_script(GOOD)
        self.run_script(with_arg(with_arg(GOOD, "sheet", "Arch-p12"), "kind", "sheet"))
        lines = self.tsv.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 3)
        self.assertEqual([lines[1].split("\t")[0], lines[2].split("\t")[0]], ["A-101", "Arch-p12"])

    def test_refusals(self):
        self.assertRefused(with_arg(GOOD, "kind", "door"), "kind must be one of")
        self.assertRefused(with_arg(GOOD, "x", "1.4"), "x must be a number from 0 to 1")
        self.assertRefused(with_arg(GOOD, "h", "-0.1"), "h must be a number from 0 to 1")
        self.assertRefused(with_arg(GOOD, "w", "wide"), "w must be a number from 0 to 1")
        self.assertRefused(with_arg(GOOD, "sheet", "A-999"), "is not a sheet INDEX.md names")
        self.assertRefused(with_arg(GOOD, "crop", " "), "crop is empty")
        self.assertFalse(self.tsv.exists())

    def test_refuses_without_agentcm(self):
        (self.root / ".construction" / "project.yaml").unlink()
        self.assertRefused(GOOD, "corrections are for AgentCM's data")

    def test_refuses_a_file_whose_header_was_changed(self):
        self.tsv.parent.mkdir(parents=True)
        self.tsv.write_text("sheet\tbox\tnote\nA-101\t0.1\tsomething\n", encoding="utf-8")
        self.assertRefused(GOOD, "does not start with the header line")


if __name__ == "__main__":
    unittest.main()
