from pathlib import Path
import subprocess
import sys

ROOT = Path.cwd()
REPORT = ROOT / "final_audit_report.txt"
results = []

def section(title):
    print(f"\n{'=' * 68}\n{title}\n{'=' * 68}")

def run_check(name, command, cwd=ROOT):
    section(name)
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=600,
        )
        output = result.stdout or "(no output)"
        print(output[-14000:])
        status = "PASS" if result.returncode == 0 else "FAIL"
        results.append((name, status, f"exit={result.returncode}"))
    except FileNotFoundError as exc:
        print(f"NOT RUN: {exc}")
        results.append((name, "NOT RUN", str(exc)))
    except subprocess.TimeoutExpired:
        print("TIMEOUT after 600 seconds")
        results.append((name, "TIMEOUT", "Exceeded 600 seconds"))

section("1. REPOSITORY")
print("Root:", ROOT)
print("Python:", sys.version)
print("Git branch and commit:")
run_check("Git snapshot", ["git", "log", "-1", "--oneline"])
print("\nDependency manifests:")
candidates = [
    "requirements.txt",
    "backend/requirements.txt",
    "backend/requirements-dev.txt",
    "backend/pyproject.toml",
    "backend/uv.lock",
    "pyproject.toml",
    "uv.lock",
    "Pipfile",
    "environment.yml",
]
found = False
for relative in candidates:
    path = ROOT / relative
    if path.is_file():
        found = True
        print(f"\n--- {relative} ---")
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            print("\n".join(lines[:100]))
            if len(lines) > 100:
                print(f"... ({len(lines) - 100} more lines)")
        except OSError as exc:
            print("Could not read:", exc)
if not found:
    print("No known dependency manifest found.")

section("2. KEY FILES")
required = [
    "README.md",
    "product-spec.md",
    "AGENTS.md",
    "openapi.yaml",
    "docker-compose.yml",
    ".env.example",
    ".github/workflows",
    "frontend/package.json",
    "frontend/src/App.tsx",
    "frontend/src/api.ts",
    "backend",
    "backend/tests",
    "docs/ai-usage-report.md",
    "docs/agent-extension-pack.md",
    "docs/permissions.md",
    "security/README.md",
    "ops/README.md",
    "agent-capabilities/README.md",
    "agent-hooks/README.md",
    "mcp-server/README.md",
    "custom-agent/README.md",
]
for relative in required:
    path = ROOT / relative
    print(f"{'PRESENT' if path.exists() else 'MISSING':8} {relative}")

section("3. AUTOMATED VALIDATION")
run_check("Git whitespace check", ["git", "diff", "--check"])
run_check(
    "Frontend lint",
    ["cmd", "/c", "npm", "run", "lint"],
    ROOT / "frontend",
)
run_check(
    "Frontend production build",
    ["cmd", "/c", "npm", "run", "build"],
    ROOT / "frontend",
)
run_check(
    "Backend pytest",
    [sys.executable, "-m", "pytest", "backend/tests", "-q"],
)
run_check(
    "Docker Compose configuration",
    ["docker", "compose", "config", "--quiet"],
)

section("4. GIT STATUS — REVIEW ONLY")
run_check("Git status", ["git", "status", "--short"])

section("5. SUMMARY")
for name, status, detail in results:
    print(f"{status:8} {name} — {detail}")

lines = [
    "SEATFLOW FINAL AUDIT",
    f"Repository: {ROOT}",
    "",
]
lines.extend(f"{status}\t{name}\t{detail}" for name, status, detail in results)
REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"\nAudit report saved to: {REPORT}")
print("\nNo files were staged, committed, or pushed by this audit.")
