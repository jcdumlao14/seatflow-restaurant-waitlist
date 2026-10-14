"""Tests for the read-only SeatFlow review capability."""
import tempfile
import unittest
from pathlib import Path

from seatflow_review import review_project


class ReviewProjectTests(unittest.TestCase):
    def test_reports_missing_required_files(self):
        with tempfile.TemporaryDirectory() as directory:
            result = review_project(directory)
            self.assertGreater(result["summary"]["errors"], 0)
            missing = {
                check["name"]
                for check in result["checks"]
                if not check["passed"]
            }
            self.assertIn("required_file:README.md", missing)

    def test_passes_when_required_artifacts_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in (
                "README.md",
                "product-spec.md",
                "AGENTS.md",
                "openapi.yaml",
                "docker-compose.yml",
                ".github/workflows/ci.yml",
                "docs/agent-extension-pack.md",
                "docs/permissions.md",
                "security/README.md",
                "ops/README.md",
            ):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                if relative == "openapi.yaml":
                    path.write_text(
                        "paths:\n  /api/waitlist/statistics/summary:\n",
                        encoding="utf-8",
                    )
                elif relative == "docker-compose.yml":
                    path.write_text("services:\n", encoding="utf-8")
                else:
                    path.write_text("test fixture\n", encoding="utf-8")

            for relative in (
                "frontend",
                "backend",
                "agent-capabilities",
                "agent-hooks",
                "mcp-server",
                "custom-agent",
            ):
                (root / relative).mkdir(parents=True, exist_ok=True)

            result = review_project(root)
            self.assertEqual(result["summary"]["errors"], 0)
            self.assertEqual(result["summary"]["failed"], 0)

    def test_rejects_non_directory_root(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "does-not-exist"
            with self.assertRaises(ValueError):
                review_project(missing)


if __name__ == "__main__":
    unittest.main()