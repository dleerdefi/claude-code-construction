"""issue_manager.py: a registry an older version left in .construction/issues/ is copied, never moved."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "issue_manager.py"


class LegacyRegistry(unittest.TestCase):
    def test_old_registry_is_copied_and_left_in_place(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy = root / ".construction" / "issues"
            legacy.mkdir(parents=True)
            old = legacy / "ISS-2026-0001.json"
            old.write_text(json.dumps({"id": "ISS-2026-0001", "status": "open", "severity": "warning"}), encoding="utf-8")
            r = subprocess.run([sys.executable, str(SCRIPT), "list"], cwd=root, capture_output=True, text=True,
                               env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue((root / ".construction" / "skills" / "issues" / "ISS-2026-0001.json").is_file())
            self.assertTrue(old.is_file(), "the old registry must be left as it is")
            self.assertIn("Copied issue registry", r.stderr)


if __name__ == "__main__":
    unittest.main()
