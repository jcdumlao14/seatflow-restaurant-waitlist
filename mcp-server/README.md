# SeatFlow MCP Server

A narrowly scoped, read-only Model Context Protocol (MCP) server for
reviewing the SeatFlow repository and reading approved project documents.

## Tools

### `review_repository_structure`

Runs the existing structural reviewer in-process and returns its checks.
The review inspects required project artifacts, selected OpenAPI markers,
and the Docker Compose services section. It does not execute application
code or modify project files.

### `read_approved_project_document`

Reads one explicitly allowlisted document relative to the repository root.
The allowlist is maintained in `seatflow_mcp_core.py`. Absolute paths,
parent-directory traversal, unapproved paths, missing files, and documents
larger than the configured size limit are rejected.

## Setup on Windows PowerShell

Run these commands from the repository root. The MCP environment is separate
from the application's Python dependencies.

```powershell
py -3.14 -m venv "$env:LOCALAPPDATA\SeatFlowMCP\venv"

$mcpPython = Join-Path $env:LOCALAPPDATA "SeatFlowMCP\venv\Scripts\python.exe"

& $mcpPython -m pip install -r mcp-server\requirements.txt
```

If the isolated environment already exists, reuse it rather than recreating it.

## Run the server

```powershell
$mcpPython = Join-Path $env:LOCALAPPDATA "SeatFlowMCP\venv\Scripts\python.exe"

& $mcpPython mcp-server\server.py
```

The server uses standard input/output (stdio) transport. Run it through an
MCP-compatible client that supports launching a local stdio server. Keep
standard output reserved for MCP protocol messages.

The repository root defaults to the parent directory of `mcp-server`.
Set `SEATFLOW_REPO_ROOT` before launching the server to select another
existing repository directory.

## Verification

Run the core unit tests:

```powershell
python -m unittest discover -s mcp-server -p "test_*.py" -v
```

Run the MCP protocol smoke test using the isolated environment:

```powershell
$mcpPython = Join-Path $env:LOCALAPPDATA "SeatFlowMCP\venv\Scripts\python.exe"

& $mcpPython mcp-server\smoke_test_mcp.py
```

The verified test run passed six core tests and discovered both MCP tools.
The protocol smoke test successfully called the approved-document tool and
the repository-review tool; the structural review reported 19 passed checks,
zero failures, zero errors, and zero warnings.

## Security boundaries and limitations

- Tools are read-only and do not provide arbitrary filesystem access.
- Document reads are restricted to the explicit allowlist.
- The server does not implement application login, tenant operations,
  database access, deployment, or write/execute tools.
- The structural reviewer checks selected markers; it is not a complete
  OpenAPI parser or a security audit.
- Keep dependencies isolated and review dependency updates before installation.
- Do not expose secrets, customer data, or production credentials in tool output.

A successful local smoke test verifies this implementation in the tested
environment; it does not establish a production deployment or remote service.