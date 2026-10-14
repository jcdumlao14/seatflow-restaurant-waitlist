# SeatFlow Agent Extension Pack

## Intended components
- `agent-capabilities/`: reusable review workflows
- `agent-hooks/`: automated checks and guardrails
- `mcp-server/`: narrowly scoped MCP tools, if implemented
- `custom-agent/`: specialist instructions or implementation
- `docs/permissions.md`: access boundaries and approval rules

## Suggested specialist workflow
Review API contract alignment, tenant isolation, waitlist state transitions,
security implications, and test coverage. Report evidence and unresolved risks.

## Safety
Use least privilege, validate tool inputs, protect secrets, and require approval
for destructive or production actions.

This document is not proof that these components are implemented. Record each
component's implementation and test evidence before submission.
