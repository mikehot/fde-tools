import os
import sys
import tempfile
import json
import shutil
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from fde_tools.commands.scaffold_mcp import run_scaffold_mcp
from fde_tools.commands.hash_doc import run_hash_doc, compute_dhash
from fde_tools.commands.eval_runner import run_eval_runner
from fde_tools.commands.guard_scan import run_guard_scan
from fde_tools.commands.check_16kb import run_check_16kb


class TestCommands(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_scaffold_mcp(self):
        target = os.path.join(self.test_dir, "test_mcp_server")
        ret = run_scaffold_mcp(target, "unit-test-server")
        self.assertEqual(ret, 0)
        self.assertTrue(os.path.exists(os.path.join(target, "server.py")))
        self.assertTrue(os.path.exists(os.path.join(target, "requirements.txt")))
        self.assertTrue(os.path.exists(os.path.join(target, "claude_desktop_config.json")))

        with open(os.path.join(target, "server.py"), "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("unit-test-server", content)
        self.assertIn("search_enterprise_knowledge", content)

    def test_hash_doc(self):
        sample_img = os.path.join(self.test_dir, "sample_doc.png")
        with open(sample_img, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 200)

        dh = compute_dhash(sample_img)
        self.assertIsInstance(dh, str)
        self.assertTrue(len(dh) > 0)

        ret = run_hash_doc(sample_img, tenant_id="TEST-TENANT", order_prefix="INV")
        self.assertEqual(ret, 0)

    def test_hash_doc_nonexistent(self):
        ret = run_hash_doc("/nonexistent/path/to/image.jpg")
        self.assertEqual(ret, 1)

    def test_eval_runner_success(self):
        dataset_file = os.path.join(self.test_dir, "golden_sample.jsonl")
        sample_cases = [
            {
                "id": "TC-01",
                "category": "Security Guard",
                "intent": "Deny prompt injection",
                "assertions": {
                    "blocked": True,
                    "confidence_min": 0.95
                }
            },
            {
                "id": "TC-02",
                "category": "Field Ingestion",
                "intent": "Verify amount equation",
                "assertions": {
                    "passed": True
                }
            }
        ]
        with open(dataset_file, "w", encoding="utf-8") as f:
            for c in sample_cases:
                f.write(json.dumps(c) + "\n")

        ret = run_eval_runner(dataset_file, threshold=0.90)
        self.assertEqual(ret, 0)

    def test_guard_scan_clean(self):
        clean_code = os.path.join(self.test_dir, "clean.py")
        with open(clean_code, "w", encoding="utf-8") as f:
            f.write("print('Clean code without secrets')\n")
        ret = run_guard_scan(self.test_dir)
        self.assertEqual(ret, 0)

    def test_guard_scan_detects_secret(self):
        vuln_code = os.path.join(self.test_dir, "vuln.py")
        with open(vuln_code, "w", encoding="utf-8") as f:
            f.write('API_KEY = "sk-proj-1234567890abcdef1234567890abcdef12345678"\n')
        ret = run_guard_scan(self.test_dir)
        self.assertEqual(ret, 1)

    def test_check_16kb_nonexistent(self):
        ret = run_check_16kb("/nonexistent/file.so")
        self.assertEqual(ret, 1)


if __name__ == "__main__":
    unittest.main()
