"""dev/check_construction_writes.py: writes under .construction/ outside skills/ fail; reads, skills/ and crops/ pass."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ccw", ROOT / "dev" / "check_construction_writes.py")
ccw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ccw)


class Markdown(unittest.TestCase):
    def flagged(self, text):
        return bool(ccw.scan_text("x/SKILL.md", text))

    def test_writes_outside_skills_are_flagged(self):
        self.assertTrue(self.flagged("Write the manifest to `.construction/spec_text/manifest.json`."))
        self.assertTrue(self.flagged("Save the page image as `.construction/rasters/A-101.png` before reading it."))
        self.assertTrue(self.flagged("If only `.construction/spec_text/` exists, move it to `.construction/skills/spec_text/` first."))

    def test_reads_skills_crops_negations_and_history_pass(self):
        self.assertFalse(self.flagged("Write it to `.construction/skills/spec_text/` with the Write tool."))
        self.assertFalse(self.flagged("Never write `.construction/index/`: that folder belongs to AgentCM."))
        self.assertFalse(self.flagged("Older versions wrote it to `.construction/spec_text/`: copy it to "
                                      "`.construction/skills/spec_text/` and leave the old one as it is."))
        self.assertFalse(self.flagged("A write names a sheet by its id in `.construction/index/sheet_index.yaml`."))
        self.assertFalse(self.flagged("`sh .construction/crop.sh <sheet> <x> <y> <w> <h>` writes `.construction/crops/A-101.png`."))
        self.assertFalse(self.flagged("Read `.construction/INDEX.md` first."))


class Python(unittest.TestCase):
    def flagged(self, text):
        return bool(ccw.scan_python("x.py", text))

    def test_rename_through_assignments_is_flagged(self):
        self.assertTrue(self.flagged('LEGACY = ".construction/issues"\nlegacy = Path(LEGACY)\nlegacy.rename(d)\n'))
        self.assertTrue(self.flagged('open(".construction/agent_findings/x.json", "w")\n'))
        self.assertTrue(self.flagged('d = os.path.join(root, ".construction", "agent_findings")\nos.makedirs(d)\n'))

    def test_copies_from_old_places_and_reads_pass(self):
        self.assertFalse(self.flagged('LEGACY = ".construction/issues"\nlegacy = Path(LEGACY)\nshutil.copytree(legacy, d)\n'))
        self.assertFalse(self.flagged('text = open(".construction/project.yaml").read()\n'))
        self.assertFalse(self.flagged('d = os.path.join(root, ".construction", "skills", skill, "findings")\nos.makedirs(d)\n'))


class Shell(unittest.TestCase):
    def test_shell_writes(self):
        self.assertTrue(ccw.scan_shell("x.sh", "mkdir -p .construction/rasters\n"))
        self.assertTrue(ccw.scan_shell("x.sh", "echo x > .construction/a.txt\n"))
        self.assertFalse(ccw.scan_shell("x.sh", "mkdir -p .construction/skills/rfi-drafter\n"))
        self.assertFalse(ccw.scan_shell("x.sh", 'cat ".construction/INDEX.md"\n'))


class Repository(unittest.TestCase):
    def test_repo_is_clean_and_every_known_entry_still_matches(self):
        findings, known = ccw.scan(ROOT)
        self.assertEqual(findings, [], findings)
        for rel, marker, _ in ccw.KNOWN:
            self.assertTrue(any(f[0] == rel and marker in f[3] for f in known),
                            f"stale KNOWN entry, remove it: {rel}: {marker}")


if __name__ == "__main__":
    unittest.main()
