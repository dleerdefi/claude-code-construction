"""poppler.py: the Poppler folder goes into every agentcm-mode case's environment, first on PATH, and the preflight
stops the run before any case when the crop scripts can't render: tools missing, Xpdf's pdfinfo, no PNG."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import poppler  # noqa: E402
from runner import extra_env, find_bash  # noqa: E402

FIXTURE = HERE.parent / "plugin" / "agentcm-mode"
POPPLER_V = "pdfinfo version 24.08.0\nCopyright 2005-2024 The Poppler Developers - http://poppler.freedesktop.org"
XPDF_V = "pdfinfo version 4.04 [www.xpdfreader.com]\nCopyright 1996-2022 Glyph & Cog, LLC"


class Env(unittest.TestCase):
    def test_the_folder_goes_first_on_path_and_only_when_set(self):
        self.assertEqual(poppler.case_env({"PATH": "/usr/bin"}), {})
        env = poppler.case_env({"PATH": "/usr/bin", poppler.VAR: "/opt/poppler/bin"})
        self.assertEqual(env[poppler.VAR], "/opt/poppler/bin")
        self.assertTrue(env["PATH"].startswith("/opt/poppler/bin" + os.pathsep))

    def test_only_agentcm_mode_cases_get_it(self):
        class C:
            def __init__(self, tags):
                self.tags = tags
        old = os.environ.get(poppler.VAR)
        os.environ[poppler.VAR] = "/opt/poppler/bin"
        try:
            self.assertIn(poppler.VAR, extra_env(C(["agentcm-mode", "tag-audit-and-takeoff"])))
            self.assertEqual(extra_env(C(["smoke", "bid-tabulator"])), {})
        finally:
            if old is None:
                os.environ.pop(poppler.VAR)
            else:
                os.environ[poppler.VAR] = old


class Preflight(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.fixture = self.root / "fixture"
        sheets = self.fixture / "construction" / "sheets"
        sheets.mkdir(parents=True)
        (sheets / "A-101.tsv").write_text("x\ty\tw\th\ttext\n0.050\t0.060\t0.120\t0.014\tGENERAL NOTES\n", encoding="utf-8")
        for name in ("crop.sh", "crop.ps1"):  # the eval stub: writes one fixed PNG and prints its path
            shutil.copy(FIXTURE / "construction" / name, self.fixture / "construction" / name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.bash = find_bash()

    def tool(self, name, prints):
        p = self.bin / name
        p.write_text("#!/bin/sh\ncat <<'EOF'\n" + prints + "\nEOF\n", encoding="utf-8", newline="\n")
        p.chmod(0o755)

    def run_preflight(self):
        return poppler.preflight(self.bash, self.fixture, dict(os.environ, **{poppler.VAR: str(self.bin)}))

    def test_poppler_and_a_png_pass(self):
        self.tool("pdfinfo", POPPLER_V)
        self.tool("pdftoppm", "")
        lines = self.run_preflight()
        self.assertIn("pdfinfo version 24.08.0", lines[0])
        self.assertTrue(any(l.startswith("crop.sh A-101 0.050 0.060 0.120 0.014") for l in lines))

    def test_a_missing_tool_is_named(self):
        self.tool("pdfinfo", POPPLER_V)
        with self.assertRaises(poppler.PopplerError) as e:
            self.run_preflight()
        self.assertIn("pdftoppm not found", str(e.exception))

    def test_xpdfs_pdfinfo_is_refused(self):
        self.tool("pdfinfo", XPDF_V)
        self.tool("pdftoppm", "")
        with self.assertRaises(poppler.PopplerError) as e:
            self.run_preflight()
        self.assertIn("is not Poppler's", str(e.exception))

    def test_a_crop_script_that_gives_no_png_stops_the_run(self):
        self.tool("pdfinfo", POPPLER_V)
        self.tool("pdftoppm", "")
        (self.fixture / "construction" / "crop.sh").write_text("#!/bin/sh\necho 'pdftoppm: cannot open' >&2\nexit 1\n",
                                                              encoding="utf-8", newline="\n")
        with self.assertRaises(poppler.PopplerError) as e:
            self.run_preflight()
        self.assertIn("crop.sh A-101", str(e.exception))
        self.assertIn("gave no PNG", str(e.exception))

    def test_the_box_comes_from_drawn_marks_when_there_is_one(self):
        self.assertEqual(poppler.known_box(self.fixture), ("A-101", 0.05, 0.06, 0.12, 0.014))
        for box in ([0.8, 0.3, 0.06, 0.021], "0.8 0.3 0.06 0.021", {"x": 0.8, "y": 0.3, "w": 0.06, "h": 0.021}):
            (self.fixture / "drawn-marks.json").write_text(json.dumps([{"sheet": "A-101", "box": box}]), encoding="utf-8")
            self.assertEqual(poppler.known_box(self.fixture), ("A-101", 0.8, 0.3, 0.06, 0.021))


if __name__ == "__main__":
    unittest.main()
