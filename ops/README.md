# Operations Documentation

Document and test the actual procedures for:
- Starting and stopping services
- Checking health and reading logs
- Diagnosing frontend, API, database, and WebSocket failures
- Database backup and restoration
- Migration failures and release rollback

Validate commands against the current Compose configuration. Protect persistent
data and never use destructive volume cleanup as routine troubleshooting.
