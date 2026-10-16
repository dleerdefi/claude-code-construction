"""extract_text_region.py --words: where each word sits, in PDF points and as fractions of the page."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import fitz  # PyMuPDF

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pdf" / "extract_text_region.py"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


class Words(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.pdf = Path(tmp.name) / "sheet.pdf"
        doc = fitz.open()
        page = doc.new_page(width=1000, height=500)
        page.insert_text((100, 100), "DOOR HARDWARE", fontsize=10)
        page.insert_text((600, 300), "220 3'-0\" 10", fontsize=10)
        doc.save(str(self.pdf))
        doc.close()

    def test_words_with_points_and_fractions(self):
        r = run(str(self.pdf), "1", "--words")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual(data["page_size"], {"width": 1000.0, "height": 500.0})
        w = next(w for w in data["words"] if w["text"] == "220")
        self.assertAlmostEqual(w["x0"], 600, delta=1)
        self.assertAlmostEqual(w["x"], 0.6, delta=0.002)
        self.assertAlmostEqual(w["y"], w["top"] / 500, delta=0.0002)
        self.assertTrue(0.25 < w["y"] < 0.6 and w["w"] > 0 and w["h"] > 0)

    def test_match_keeps_only_the_matching_words(self):
        data = json.loads(run(str(self.pdf), "1", "--words", "--match", "^(220|HARDWARE)$").stdout)
        self.assertEqual(sorted(w["text"] for w in data["words"]), ["220", "HARDWARE"])

    def test_without_words_the_output_is_as_before(self):
        data = json.loads(run(str(self.pdf), "1").stdout)
        self.assertNotIn("words", data)
        self.assertIn("HARDWARE", data["text"])

    def test_match_needs_words(self):
        self.assertNotEqual(run(str(self.pdf), "1", "--match", "220").returncode, 0)


if __name__ == "__main__":
    unittest.main()
