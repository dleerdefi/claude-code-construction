"""The generated agentcm-mode cases grade what they claim: every check compiles."""
import py_compile
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

EVALS = HERE.parent / "plugin"


class Checks(unittest.TestCase):
    def test_every_case_check_compiles(self):
        checks = sorted(EVALS.glob("*/checks/*.py"))
        self.assertTrue(checks)
        with tempfile.TemporaryDirectory() as tmp:
            for i, f in enumerate(checks):
                with self.subTest(check=f.relative_to(EVALS).as_posix()):
                    py_compile.compile(str(f), cfile=str(Path(tmp) / f"{i}.pyc"), doraise=True)


if __name__ == "__main__":
    unittest.main()
