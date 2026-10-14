# Agent Permissions and Safety

## Default
Use the minimum permissions needed for each task.

## Require approval
- Destructive database or filesystem operations
- Docker volume deletion
- Production deployments or configuration changes
- Publishing images or packages
- Installing dependencies when scope or risk is unclear

## Protect
- Passwords, JWTs, API tokens, and private keys
- Customer and other private application data
- Production database access

Do not bypass authorization to make tests pass. Document actual tool
permissions and test safeguards before enabling automated actions.

## MCP server boundary

The local MCP server exposes only repository structural review and reading
of explicitly allowlisted project documents. It does not expose arbitrary
file reads, filesystem writes, shell execution, database operations, or
deployment tools.

Review tool inputs and outputs before using them with sensitive repositories.
The allowlist and file-size limit are safeguards, not a substitute for
operating-system permissions or a security audit. Local smoke-test success
does not imply production authorization or deployment.