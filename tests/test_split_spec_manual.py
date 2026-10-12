"""split_spec_manual.py --sections-file: a synthetic manual split by a sections file, and the refusals."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "spec-splitter" / "scripts" / "split_spec_manual.py"
HEADER = "# manual: Project Manual.pdf\n# pages: 1-based\n"


def make_manual(path, pages=10):
    """A manual with no SECTION headings: each page says only which page it is."""
    doc = fitz.open()
    for i in range(1, pages + 1):
        doc.new_page().insert_text((72, 72), f"MANUAL PAGE {i}")
    doc.save(str(path))
    doc.close()


def page_texts(path):
    with fitz.open(str(path)) as doc:
        return [page.get_text().strip() for page in doc]


class SectionsFile(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.pdf = self.tmp / "Project Manual.pdf"
        make_manual(self.pdf)
        self.out = self.tmp / "Specification Sections"

    def split(self, rows, header=HEADER):
        sections = self.tmp / "sections.tsv"
        sections.write_text(header + "section\ttitle\tfirst\tlast\n" + rows, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.pdf), "--sections-file", str(sections), "--output-dir", str(self.out)],
            capture_output=True, text=True, env=dict(os.environ, PYTHONIOENCODING="utf-8"))

    def assertRefused(self, result, reason):
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("refused", result.stdout)
        self.assertIn(reason, result.stdout)
        self.assertFalse(self.out.exists(), "a refused file must write nothing")

    def test_splits_the_listed_sections_with_their_pages(self):
        result = self.split("08 71 00\tDOOR HARDWARE\t2\t4\n09 65 13\tRESILIENT BASE AND ACCESSORIES\t6\t9\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(page_texts(self.out / "08 71 00 - DOOR HARDWARE.pdf"),
                         ["MANUAL PAGE 2", "MANUAL PAGE 3", "MANUAL PAGE 4"])
        self.assertEqual(page_texts(self.out / "09 65 13 - RESILIENT BASE AND ACCESSORIES.pdf"),
                         ["MANUAL PAGE 6", "MANUAL PAGE 7", "MANUAL PAGE 8", "MANUAL PAGE 9"])
        self.assertTrue((self.out / "spec_index.yaml").exists())
        self.assertIn("pages read: none", result.stdout)

    def test_without_a_sections_file_a_manual_with_no_headings_is_not_split(self):
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.pdf), "--output-dir", str(self.out)],
                                capture_output=True, text=True, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("--sections-file", result.stdout)

    def test_refuses_overlapping_sections(self):
        self.assertRefused(self.split("08 71 00\tDOOR HARDWARE\t2\t5\n09 65 13\tRESILIENT BASE\t5\t8\n"), "overlap")

    def test_refuses_pages_outside_the_manual(self):
        self.assertRefused(self.split("09 65 13\tRESILIENT BASE\t8\t11\n"), "outside the manual's 10 pages")
        self.assertRefused(self.split("01 10 00\tSUMMARY\t0\t3\n"), "outside the manual's 10 pages")

    def test_refuses_a_section_that_runs_backwards(self):
        self.assertRefused(self.split("08 71 00\tDOOR HARDWARE\t5\t3\n"), "runs backwards")

    def test_refuses_a_missing_page_base(self):
        self.assertRefused(self.split("08 71 00\tDOOR HARDWARE\t2\t4\n", header="# manual: Project Manual.pdf\n"),
                           "page base is missing")

    def test_refuses_any_base_but_1_based(self):
        self.assertRefused(self.split("08 71 00\tDOOR HARDWARE\t1\t3\n",
                                      header="# manual: Project Manual.pdf\n# pages: 0-based\n"), "only 1-based")

    def test_refuses_a_file_for_another_manual(self):
        self.assertRefused(self.split("08 71 00\tDOOR HARDWARE\t2\t4\n",
                                      header="# manual: Other Manual.pdf\n# pages: 1-based\n"), "Other Manual.pdf")

    def test_refuses_a_section_listed_twice(self):
        self.assertRefused(self.split("08 71 00\tDOOR HARDWARE\t2\t4\n08 71 00\tDOOR HARDWARE\t6\t7\n"),
                           "already listed")


if __name__ == "__main__":
    unittest.main()
