"""pdf_text.py --output: a dump saved for searching goes into the skill's working folder, created if missing."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import fitz  # PyMuPDF

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pdf" / "pdf_text.py"


class Output(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.pdf = self.root / "09 65 40.pdf"
        doc = fitz.open()
        doc.new_page().insert_text((72, 72), "SECTION 09 65 40 LUXURY VINYL TILE 1.3 SUBMITTALS Product Data.", fontsize=10)
        doc.save(str(self.pdf))
        doc.close()

    def test_output_creates_its_folder(self):
        out = self.root / ".construction" / "skills" / "subcontract-writer" / "text" / "09-65-40.txt"
        r = subprocess.run([sys.executable, str(SCRIPT), str(self.pdf), "--output", str(out)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("SUBMITTALS", out.read_text(encoding="utf-8"))
        self.assertIn("1 page(s); 1 TEXT, 0 VISION", r.stdout)


if __name__ == "__main__":
    unittest.main()
