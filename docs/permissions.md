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
