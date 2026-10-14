# SeatFlow Agent Extension Pack

## Components
- `agent-capabilities/seatflow_review.py`: read-only structural checks for
  expected project artifacts and selected API/Compose contract markers.
- `agent-capabilities/test_seatflow_review.py`: unit tests for the review tool.
- `agent-hooks/seatflow_guardrail.py`: selected-file or staged-file heuristic
  secret scan followed by capability tests.
- `agent-hooks/test_seatflow_guardrail.py`: guardrail unit tests.
- `custom-agent/AGENT.md`: specialist review workflow and permission boundaries.
- `mcp-server/server.py`: read-only MCP server exposing repository review and
  approved-document reading tools.
- `mcp-server/seatflow_mcp_core.py`: in-process structural review and
  allowlisted document-reading functions.
- `mcp-server/test_seatflow_mcp_core.py` and `mcp-server/smoke_test_mcp.py`:
  core safety tests and MCP protocol smoke test.
- `mcp-server/README.md`: isolated setup, usage, verification, and security
  boundaries.
- `docs/permissions.md`: approval requirements and protected information.

## Review workflow
Inspect API contract alignment, tenant isolation, waitlist transitions,
security implications, and regression coverage. Record actual commands and
outputs. Report unresolved risks and distinguish static checks from integration
tests.

## Safe use
The capability and guardrail are read-only. The guardrail scans only paths
explicitly supplied by the operator or already staged in Git. It never stages,
commits, deploys, modifies the database, or deletes files.

## Limitations
The structural capability is not a full OpenAPI parser. The guardrail uses
heuristic patterns and can miss secrets or report false positives. Neither is
a substitute for a dedicated security audit. The MCP server is implemented
with two read-only tools and has passed its core tests and local protocol
smoke test. It has not been established as a production deployment.