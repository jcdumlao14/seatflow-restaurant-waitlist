# SeatFlow AI Agent Instructions

- Inspect the existing code, configuration, and tests before editing.
- Make focused changes and preserve unrelated work and backups.
- Keep frontend API communication centralized in `frontend/src/api.ts`
  unless the architecture is deliberately changed.
- Align backend API changes with `openapi.yaml`.
- Treat authentication, authorization, and tenant isolation as security
  boundaries.
- Never expose or commit passwords, JWTs, tokens, or private data.
- Never run destructive database or Docker-volume commands without approval.
- Review diffs and run applicable lint, build, and tests after changes.
- Report the actual commands and results; never claim unrun checks passed.
