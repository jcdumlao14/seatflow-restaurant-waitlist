"""Read-only guardrail for staged or explicitly selected SeatFlow files."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

SECRET_PATTERNS = (
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("AWS-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    (
        "credential-assignment",
        re.compile(
            r"""(?ix)
            \b(?:api[_-]?key|client[_-]?secret|password|passwd|access[_-]?token)
            \b\s*[:=]\s*["']?
            (?!your[_ -]|replace[_ -]|example|placeholder|changeme|none\b|null\b)
            [A-Za-z0-9_./+=-]{12,}
            """
        ),
    ),
)

def scan_text(content: str) -> list[str]:
    """Return finding labels and line numbers; never return matched secret text."""
    findings = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append(f"{label} at line {line_number}")
    return findings


def staged_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def check_staged_paths(root: Path, paths: list[str]) -> list[str]:
    """Scan the exact blob contents stored in Git's index."""
    errors = []
    for relative in paths:
        result = subprocess.run(
            ["git", "show", f":{relative}"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            errors.append(f"Could not read staged file: {relative}")
            continue
        for finding in scan_text(result.stdout):
            errors.append(f"{relative}: {finding}")
    return errors


def check_paths(root: Path, paths: list[str]) -> list[str]:
    """Check selected files, refusing paths that resolve outside the repository."""
    errors = []
    root = root.resolve()
    for relative in paths:
        candidate = (root / relative).resolve()
        if not candidate.is_relative_to(root):
            errors.append(f"Rejected path outside repository: {relative}")
            continue
        if not candidate.is_file():
            errors.append(f"Selected file not found: {relative}")
            continue
        try:
            content = candidate.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            errors.append(f"Could not read selected file: {relative}")
            continue
        findings = scan_text(content)
        for finding in findings:
            errors.append(f"{relative}: {finding}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="SeatFlow repository root")
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Inspect staged Git files only; does not stage or change files",
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        default=None,
        help="Explicit repository-relative paths to inspect",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip the capability unit tests",
    )
    args = parser.parse_args()
    root = Path(args.root).resolve()

    if not root.is_dir():
        print("Guardrail failed: repository root is not a directory.")
        return 2
    if args.staged and args.paths is not None:
        parser.error("Use either --staged or --paths, not both.")

    try:
        paths = staged_paths(root) if args.staged else args.paths
        if paths is None:
            parser.error("Provide --paths or explicitly select --staged.")
        if not paths:
            print("No selected files to scan.")
        else:
            errors = (
                check_staged_paths(root, paths)
                if args.staged
                else check_paths(root, paths)
            )
            if errors:
                print("GUARDRAIL FAILED")
                for error in errors:
                    print(f"- {error}")
                return 1
            print(f"Secret scan passed for {len(paths)} selected file(s).")
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Guardrail could not complete: {type(exc).__name__}")
        return 2

    if not args.skip_tests:
        command = [
            sys.executable, "-m", "unittest", "discover",
            "-s", "agent-capabilities", "-p", "test_*.py", "-v",
        ]
        result = subprocess.run(command, cwd=root, check=False)
        if result.returncode:
            print("Capability tests failed.")
            return result.returncode

    print("GUARDRAIL PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())