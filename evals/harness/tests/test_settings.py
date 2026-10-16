"""What a session loads: an agentcm-mode case reads the workspace's project settings (its CLAUDE.md, and AgentCM's
.construction/CLAUDE.md through it), with every instruction file above the workspace excluded; any other case loads
none. Run: bin/construction-python -m unittest discover evals/harness/tests"""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runner import claude_md_excludes, setting_sources  # noqa: E402

ROOT = Path(Path.cwd().anchor)
HOME = ROOT / "Users" / "pe (2)"
WS = HOME / "AppData" / "Local" / "Temp" / "construction-eval" / "agentcm-mode-rfi-drafter-20261015-r1"


def posix(p: Path) -> str:
    return p.as_posix().rstrip("/")


def glob(p: Path) -> str:
    return posix(p).replace("(", "\\(").replace(")", "\\)")


class SettingSources(unittest.TestCase):
    def test_an_agentcm_mode_case_loads_the_project_settings(self):
        self.assertEqual(setting_sources(SimpleNamespace(tags=["agentcm-mode", "drawings"])), ["project"])

    def test_any_other_case_loads_none(self):
        self.assertEqual(setting_sources(SimpleNamespace(tags=["smoke"])), [])
        self.assertEqual(setting_sources(SimpleNamespace(tags=[])), [])


class ClaudeMdExcludes(unittest.TestCase):
    def test_the_users_own_claude_md_is_excluded(self):
        self.assertIn(posix(ROOT / "Users") + "/pe \\(2\\)/.claude/CLAUDE.md", claude_md_excludes(WS))

    def test_every_folder_above_the_workspace_and_none_inside_it(self):
        found = claude_md_excludes(WS)
        self.assertEqual(len(found), 4 * len(WS.parents))
        for parent in WS.parents:
            self.assertIn(glob(parent) + "/CLAUDE.md", found)
        self.assertFalse([g for g in found if "agentcm-mode-rfi-drafter" in g])

    def test_the_drive_root_too(self):
        self.assertIn(posix(ROOT) + "/CLAUDE.md", claude_md_excludes(WS))

    def test_each_kind_of_instruction_file(self):
        top = glob(WS.parent)
        for name in ("CLAUDE.md", "CLAUDE.local.md", ".claude/CLAUDE.md", ".claude/rules/**"):
            self.assertIn(f"{top}/{name}", claude_md_excludes(WS))

    def test_glob_characters_in_a_folder_name_are_escaped(self):
        found = claude_md_excludes(ROOT / "a[1]" / "b*{c}" / "ws")
        self.assertIn(posix(ROOT) + "/a\\[1\\]/b\\*\\{c\\}/CLAUDE.md", found)


if __name__ == "__main__":
    unittest.main()
