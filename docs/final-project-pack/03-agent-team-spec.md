# Agent Team Specification

## Purpose
This document defines a proposed agent-assisted engineering workflow for
developing and operating SeatFlow. It does not imply that autonomous agents
or an on-call agent are already implemented.

## Roles

### 1. Coordinator
Responsibilities:
- Break work into small, reviewable tasks.
- Maintain the acceptance-criteria checklist.
- Track dependencies and unresolved risks.
- Require evidence before declaring work complete.

Permissions:
- May propose plans and documentation updates.
- Must not deploy, delete data, rotate production configuration, or merge
  changes without explicit authorization.

### 2. Implementation agent
Responsibilities:
- Implement a scoped frontend or backend change.
- Follow existing architecture and repository instructions.
- Add or update tests with code changes.
- Report changed files and verification results.

Controls:
- No production secrets in logs or generated documentation.
- No unrelated rewrites.
- No destructive database operations without approval.

### 3. Test and quality agent
Responsibilities:
- Run backend tests, frontend lint, and production builds.
- Check API contracts and edge cases.
- Test authentication and workspace isolation.
- Report failures accurately without suppressing them.

### 4. Deployment and reliability agent
Responsibilities:
- Review container and deployment configuration.
- Verify health checks, migration behavior, logs, and alerts.
- Prepare rollback steps.
- Recommend corrective action when production checks fail.

Controls:
- Read-only diagnosis by default.
- Human approval required for production changes and destructive actions.

## Shared task contract
Every task should include:
1. Goal and acceptance criteria.
2. Relevant files and dependencies.
3. Allowed and prohibited actions.
4. Tests or checks to run.
5. Expected evidence.
6. Actual result, changed files, and remaining risks.

## Human approval gates
Require human approval before:
- Production deployment or rollback.
- Database reset, deletion, or destructive migration.
- Changes to production credentials or access permissions.
- Merging changes that bypass required checks.

## Completion definition
A task is complete only when acceptance criteria have evidence, tests are
reported honestly, documentation is updated when needed, and unresolved
risks are disclosed.
