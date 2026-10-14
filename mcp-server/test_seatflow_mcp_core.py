import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from seatflow_mcp_core import (
    ALLOWED_DOCUMENTS,
    read_approved_project_document,
)


class MCPReadOnlyCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()
        (self.root / "README.md").write_text(
            "# Safe project document\n", encoding="utf-8"
        )
        (self.root / "docs" / "permissions.md").write_text(
            "Read-only permissions.\n", encoding="utf-8"
        )
        (self.root / "secret.txt").write_text(
            "DO NOT EXPOSE\n", encoding="utf-8"
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_reads_allowlisted_document(self):
        result = read_approved_project_document("README.md", self.root)
        self.assertEqual(result, "# Safe project document\n")

    def test_rejects_unapproved_file(self):
        with self.assertRaises(ValueError):
            read_approved_project_document("secret.txt", self.root)

    def test_rejects_parent_traversal(self):
        with self.assertRaises(ValueError):
            read_approved_project_document("../secret.txt", self.root)

    def test_rejects_absolute_path(self):
        with self.assertRaises(ValueError):
            read_approved_project_document(
                str((self.root / "README.md").resolve()), self.root
            )

    def test_allowlist_is_explicit(self):
        self.assertNotIn("secret.txt", ALLOWED_DOCUMENTS)

    def test_rejects_missing_approved_document(self):
        with self.assertRaises(FileNotFoundError):
            read_approved_project_document("openapi.yaml", self.root)


if __name__ == "__main__":
    unittest.main(verbosity=2)