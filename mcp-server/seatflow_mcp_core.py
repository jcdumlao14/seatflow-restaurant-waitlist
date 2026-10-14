"""Read-only core functions for the SeatFlow MCP server."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path

PROJECT_ROOT = Path(
    os.environ.get(
        "SEATFLOW_REPO_ROOT",
        Path(__file__).resolve().parents[1],
    )
).resolve()

ALLOWED_DOCUMENTS = frozenset({
    "README.md",
    "AGENTS.md",
    "product-spec.md",
    "openapi.yaml",
    "docs/permissions.md",
    "docs/agent-extension-pack.md",
    "security/README.md",
    "ops/README.md",
})

MAX_DOCUMENT_BYTES = 200_000


def _root(root=None) -> Path:
    """Return an existing project directory."""
    project = Path(root if root is not None else PROJECT_ROOT).resolve()
    if not project.is_dir():
        raise ValueError("Project root must be an existing directory.")
    return project


def review_repository_structure(root=None) -> str:
    """Run the existing read-only structural reviewer in-process."""
    project = _root(root)
    reviewer = project / "agent-capabilities" / "seatflow_review.py"

    if not reviewer.is_file():
        raise FileNotFoundError("Structural reviewer was not found.")

    spec = importlib.util.spec_from_file_location(
        "seatflow_review_runtime", reviewer
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the structural reviewer.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.review_project(project)

    lines = [
        f"SeatFlow review: {result['project']}",
        f"Summary: {result['summary']}",
    ]

    for check in result["checks"]:
        mark = "PASS" if check["passed"] else "FAIL"
        lines.append(
            f"[{mark}] {check['name']}: {check['detail']}"
        )

    report = "\n".join(lines)
    if result["summary"]["errors"]:
        raise RuntimeError(report)

    return report


def read_approved_project_document(path: str, root=None) -> str:
    """Read one explicitly allowlisted document inside the project root."""
    if not isinstance(path, str) or not path.strip():
        raise ValueError("A relative document path is required.")

    requested = Path(path)
    if requested.is_absolute() or ".." in requested.parts:
        raise ValueError("Absolute paths and parent traversal are forbidden.")

    normalized = requested.as_posix()
    if normalized not in ALLOWED_DOCUMENTS:
        raise ValueError("Document is not on the approved allowlist.")

    project = _root(root)
    candidate = (project / requested).resolve()

    try:
        candidate.relative_to(project)
    except ValueError:
        raise ValueError("Document path escapes the project root.") from None

    if not candidate.is_file():
        raise FileNotFoundError("Approved document was not found.")

    if candidate.stat().st_size > MAX_DOCUMENT_BYTES:
        raise ValueError("Document exceeds the maximum permitted size.")

    return candidate.read_text(encoding="utf-8-sig")