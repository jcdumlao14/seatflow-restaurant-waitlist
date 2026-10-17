# Context Management and Repository Instructions

## Sources of truth
1. Current source code and automated tests.
2. Current environment and deployment configuration, without exposing secrets.
3. Current product specification and acceptance criteria.
4. Current task tracker and decision log.
5. README and other explanatory documentation.

If these sources disagree, record the discrepancy and resolve it explicitly.

## Context to provide for each engineering task
- Project objective and user journey.
- Relevant API routes, models, and frontend components.
- Database schema and migration history.
- Security and workspace-isolation requirements.
- Recent failures and verified test output.
- Files allowed to change.
- Acceptance criteria and rollback considerations.

## Task and decision log
For each meaningful change, record:
- Date.
- Problem and rationale.
- Decision taken.
- Files affected.
- Tests executed and results.
- Deployment impact.
- Follow-up actions.

## Context hygiene
- Keep instructions concise and specific.
- Prefer links to canonical documents over duplicated instructions.
- Do not copy credentials, access tokens, private keys, or full connection
  strings into prompts, logs, commits, or documentation.
- Distinguish confirmed facts from assumptions.
- Do not treat old backups as current source-of-truth files.
- Recheck repository state before applying a previous recommendation.

## Suggested task lifecycle
1. Inspect the current state.
2. Define a minimal change.
3. Implement the change.
4. Run focused tests.
5. Run the full relevant checks.
6. Review the diff for unrelated changes and secrets.
7. Update documentation.
8. Obtain approval and deploy.
9. Verify production and record evidence.
