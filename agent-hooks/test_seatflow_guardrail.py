"""Unit tests for the SeatFlow guardrail."""
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seatflow_guardrail import check_paths, check_staged_paths, scan_text


class GuardrailTests(unittest.TestCase):
    def test_clean_text_passes(self):
        self.assertEqual(scan_text("password = YOUR_PASSWORD_HERE\n"), [])

    def test_detects_private_key_without_exposing_contents(self):
        findings = scan_text(
            "-----BEGIN " + "PRIVATE KEY-----\n"
            "redacted test content\n"
        )
        self.assertTrue(findings)
        self.assertIn("private-key", findings[0])
        self.assertNotIn("redacted test content", str(findings))

    def test_rejects_path_outside_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            findings = check_paths(root, ["../outside.txt"])
            self.assertTrue(any("outside repository" in item for item in findings))

    def test_staged_scan_reads_git_index(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(
                ["git", "init", "-q"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )

            sample = root / "sample.py"
            sample.write_text("safe = True\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "sample.py"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )

            # Unstaged content must not affect the staged scan.
            sample.write_text(
                "-----BEGIN " + "PRIVATE KEY-----\n",
                encoding="utf-8",
            )
            self.assertEqual(check_staged_paths(root, ["sample.py"]), [])

            # The same marker must be detected once staged.
            subprocess.run(
                ["git", "add", "sample.py"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
            findings = check_staged_paths(root, ["sample.py"])
            self.assertTrue(
                any("private-key at line 1" in item for item in findings),
                findings,
            )

if __name__ == "__main__":
    unittest.main()