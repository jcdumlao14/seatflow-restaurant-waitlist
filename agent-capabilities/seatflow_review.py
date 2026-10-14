"""Read-only structural review for the SeatFlow repository."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_FILES = (
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
)

REQUIRED_DIRS = (
    "frontend",
    "backend",
    "agent-capabilities",
    "agent-hooks",
    "mcp-server",
    "custom-agent",
)


def review_project(root: str | Path) -> dict:
    """Inspect expected project artifacts; never execute project code."""
    project = Path(root).resolve()
    if not project.is_dir():
        raise ValueError("Project root must be an existing directory.")

    checks = []
    for relative in REQUIRED_FILES:
        exists = (project / relative).is_file()
        checks.append({
            "name": f"required_file:{relative}",
            "passed": exists,
            "severity": "error",
            "detail": "present" if exists else "missing required file",
        })

    for relative in REQUIRED_DIRS:
        exists = (project / relative).is_dir()
        checks.append({
            "name": f"required_directory:{relative}",
            "passed": exists,
            "severity": "error",
            "detail": "present" if exists else "missing required directory",
        })

    openapi_path = project / "openapi.yaml"
    if openapi_path.is_file():
        content = openapi_path.read_text(encoding="utf-8-sig", errors="replace")
        has_paths = "paths:" in content
        has_statistics = "/api/waitlist/statistics/summary" in content
        checks.extend((
            {
                "name": "openapi_has_paths_section",
                "passed": has_paths,
                "severity": "error",
                "detail": "paths section found" if has_paths else "paths section not found",
            },
            {
                "name": "openapi_documents_statistics_endpoint",
                "passed": has_statistics,
                "severity": "warning",
                "detail": (
                    "statistics endpoint documented"
                    if has_statistics
                    else "statistics endpoint string not found; verify the contract manually"
                ),
            },
        ))

    compose_path = project / "docker-compose.yml"
    if compose_path.is_file():
        content = compose_path.read_text(encoding="utf-8-sig", errors="replace")
        has_services = "services:" in content
        checks.append({
            "name": "compose_has_services",
            "passed": has_services,
            "severity": "error",
            "detail": "services section found" if has_services else "services section not found",
        })

    errors = sum(
        not item["passed"] and item["severity"] == "error"
        for item in checks
    )
    warnings = sum(
        not item["passed"] and item["severity"] == "warning"
        for item in checks
    )

    return {
        "project": project.name,
        "mode": "read-only structural checks",
        "checks": checks,
        "summary": {
            "passed": sum(item["passed"] for item in checks),
            "failed": sum(not item["passed"] for item in checks),
            "errors": errors,
            "warnings": warnings,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="SeatFlow repository root")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    try:
        result = review_project(args.root)
    except (OSError, ValueError) as exc:
        print(f"Review could not run: {type(exc).__name__}")
        return 2

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"SeatFlow review: {result['project']}")
        print(f"Summary: {result['summary']}")
        for check in result["checks"]:
            mark = "PASS" if check["passed"] else "FAIL"
            print(f"[{mark}] {check['name']}: {check['detail']}")

    return 1 if result["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())