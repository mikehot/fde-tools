import os
import sys
import subprocess
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestCLI(unittest.TestCase):
    def run_cli(self, *args):
        cmd = [sys.executable, "-m", "fde_tools.cli"] + list(args)
        env = os.environ.copy()
        env["PYTHONPATH"] = REPO_ROOT
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)

    def test_cli_help(self):
        res = self.run_cli("--help")
        self.assertEqual(res.returncode, 0)
        self.assertTrue("FDE" in res.stdout or "Field Deployed Engineer" in res.stdout)
        self.assertIn("fde check-16kb", res.stdout)
        self.assertIn("fde hash-doc", res.stdout)

    def test_cli_version(self):
        res = self.run_cli("--version")
        self.assertEqual(res.returncode, 0)
        self.assertIn("FDE-Tools v1.0.0", res.stdout)

    def test_cli_info(self):
        res = self.run_cli("info")
        self.assertEqual(res.returncode, 0)
        self.assertIn("System Environment & Diagnostics:", res.stdout)
        self.assertIn("Python Runtime", res.stdout)

    def test_cli_unknown_command(self):
        res = self.run_cli("nonexistent-command-xyz")
        self.assertNotEqual(res.returncode, 0)
        self.assertTrue("Unknown command" in res.stdout or "Unknown command" in res.stderr)


if __name__ == "__main__":
    unittest.main()
