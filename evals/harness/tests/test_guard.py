"""Unit tests for the harness guard. Run: bin/construction-python -m unittest discover evals/harness/tests"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from guard import Policy, decide, normalize, shell_paths  # noqa: E402

WS = os.path.join(tempfile.gettempdir(), "construction-eval", "case-r1")
PLUGIN = "C:/plugin" if os.name == "nt" else "/opt/plugin"
POLICY = Policy(workspace=WS, plugin_root=PLUGIN)
PY = f'"{PLUGIN}/bin/construction-python"'


class ShellCommands(unittest.TestCase):
    def test_plugin_script_with_relative_output_is_allowed(self):
        cmd = f'cd "01 - Drawings/sheets" && {PY} "{PLUGIN}/scripts/pdf/rasterize_page.py" page_001.pdf 1 --output tb.png'
        self.assertTrue(decide("Bash", {"command": cmd}, POLICY).allow)

    def test_temp_dir_output_is_allowed(self):
        out = os.path.join(tempfile.gettempdir(), "tb_001.png").replace("\\", "/")
        self.assertTrue(decide("Bash", {"command": f"{PY} x.py --output {out}"}, POLICY).allow)

    def test_workspace_absolute_path_with_spaces_is_allowed(self):
        cmd = f'ls "{WS}/01 - Drawings/sheets"'
        self.assertTrue(decide("Bash", {"command": cmd}, POLICY).allow)

    def test_dev_null_and_usr_bin_are_allowed(self):
        self.assertTrue(decide("Bash", {"command": "ls > /dev/null 2>&1; /usr/bin/env python --version"}, POLICY).allow)

    def test_curl_is_denied(self):
        d = decide("Bash", {"command": "curl --version"}, POLICY)
        self.assertFalse(d.allow)
        self.assertIn("curl", d.reason)

    def test_powershell_download_is_denied(self):
        self.assertFalse(decide("PowerShell", {"command": "Invoke-WebRequest https://x.test -OutFile a"}, POLICY).allow)

    def test_pip_install_is_denied(self):
        self.assertFalse(decide("Bash", {"command": f"{PY} -m pip install requests"}, POLICY).allow)

    def test_git_push_is_denied_but_git_status_is_fine(self):
        self.assertFalse(decide("Bash", {"command": "git push origin main"}, POLICY).allow)
        self.assertTrue(decide("Bash", {"command": "git status --short"}, POLICY).allow)

    def test_path_under_home_outside_roots_is_denied(self):
        home = str(Path.home()).replace("\\", "/")
        self.assertFalse(decide("Bash", {"command": f'cat "{home}/Documents/secrets.txt"'}, POLICY).allow)

    def test_tilde_path_is_denied_unless_toolkit_venv(self):
        self.assertFalse(decide("Bash", {"command": "ls ~/Documents"}, POLICY).allow)
        self.assertTrue(decide("Bash", {"command": "ls ~/.construction-skills/venv"}, POLICY).allow)

    def test_recursive_delete_of_root_or_home_is_denied(self):
        self.assertFalse(decide("Bash", {"command": "rm -rf /"}, POLICY).allow)
        self.assertFalse(decide("Bash", {"command": "rm -rf ~"}, POLICY).allow)
        self.assertFalse(decide("Bash", {"command": "rm -rf ../"}, POLICY).allow)
        self.assertTrue(decide("Bash", {"command": "rm -rf sheets/tmp"}, POLICY).allow)

    def test_git_bash_drive_path_is_normalized(self):
        self.assertEqual(normalize("/c/Users/x/file.pdf"), "C:/Users/x/file.pdf")
        ws_gitbash = "/" + WS[0].lower() + WS[2:].replace("\\", "/") if os.name == "nt" else WS
        self.assertTrue(decide("Bash", {"command": f'ls "{ws_gitbash}/01 - Drawings"'}, POLICY).allow)

    def test_glob_slash_is_not_the_root(self):
        self.assertTrue(decide("Bash", {"command": "ls; ls */ | head -80"}, POLICY).allow)
        self.assertTrue(decide("Bash", {"command": "ls sheets/*/ && cat sheet_index.yaml"}, POLICY).allow)
        self.assertFalse(decide("Bash", {"command": "ls /"}, POLICY).allow)

    def test_heredoc_body_is_not_scanned_for_paths(self):
        cmd = ("cat > .construction/skills/x/project_context.yaml <<'E'\n"
               "occupancy: B / R-2 / S-2\nnote: /construction:code-researcher egress\nE\n")
        self.assertTrue(decide("Bash", {"command": cmd}, POLICY).allow)
        self.assertEqual(shell_paths(cmd), [])
        self.assertFalse(decide("Bash", {"command": "cat > ~/notes.txt <<'E'\nx\nE\n"}, POLICY).allow)

    def test_shell_paths_extraction(self):
        paths = shell_paths(f'cd "{WS}/a b" && cat /etc/hosts > out.txt')
        self.assertIn(f"{WS}/a b", paths)
        self.assertIn("/etc/hosts", paths)
        self.assertNotIn("out.txt", paths)


class FileWrites(unittest.TestCase):
    def test_write_inside_workspace_is_allowed(self):
        self.assertTrue(decide("Write", {"file_path": os.path.join(WS, "sheets", "sheet_index.yaml")}, POLICY).allow)
        self.assertTrue(decide("Edit", {"file_path": "CLAUDE.md"}, POLICY).allow)

    def test_write_outside_workspace_is_denied(self):
        outside = os.path.join(tempfile.gettempdir(), "elsewhere.txt")
        d = decide("Write", {"file_path": outside}, POLICY)
        self.assertFalse(d.allow)
        self.assertIn("outside the workspace", d.reason)
        self.assertFalse(decide("Write", {"file_path": os.path.join(WS, "..", "x.txt")}, POLICY).allow)

    def test_other_tools_are_not_decided_here(self):
        self.assertTrue(decide("Read", {"file_path": "/anything"}, POLICY).allow)


if __name__ == "__main__":
    unittest.main()
