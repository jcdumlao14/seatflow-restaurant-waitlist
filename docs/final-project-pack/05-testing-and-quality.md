# Testing and Quality

## Verified local results

The following results were reported from the local development environment on 2026-10-17. Rerun the commands before a release if the source code or dependencies change.

| Check | Reported result |
|---|---|
| Backend tests | 47 passed, 1 warning |
| Frontend lint | Passed |
| Frontend production build | Passed |
| Docker Compose configuration | Passed |
| OpenAPI contract verification | Passed; checked-in and live specifications matched, OpenAPI 3.1.0, API version 2.2.0, 13 paths |
| Docker integration E2E | 23 checks passed |
| Alembic revision | `6fd61589df5c (head)` |
| Git whitespace check | Passed |
| Local backend health | HTTP 200 |
| Local frontend | HTTP 200 |

The backend test run reported a Starlette deprecation warning concerning the HTTPX test-client integration. This warning did not cause the reported test run to fail.

These results describe local verification; they do not prove that production authentication, database connectivity, migrations, or hosted user journeys work.

## Reproducible commands

Run from the repository root unless noted otherwise:

```powershell
python -m pytest backend/tests -q
python scripts/verify_openapi_contract.py
python scripts/docker_integration_e2e.py
docker compose config --quiet
docker compose ps
docker compose exec -T backend alembic current
git diff --check
```

Run frontend checks from the frontend directory:

```powershell
Set-Location frontend
npm run lint
npm run build
Set-Location ..
```

The integration script creates test records in the local database. Inspect the script and test environment before running it again. Do not remove database volumes as a cleanup shortcut.

## Quality coverage and limitations

The backend suite includes test modules for configuration, phase-two functionality, role-based access control, waitlist operations, and WebSockets. The reported integration run covered health, registration, authentication, waitlist creation, tenant-scoped access, statistics, status changes, and rejection of missing or invalid credentials.

A passing test suite is evidence for the paths exercised, not proof of every possible error case. Confirm test assertions and coverage before claiming exhaustive workspace isolation or authorization coverage.

No frontend test script was identified in the recorded repository inventory. Frontend component and browser-level test coverage remains a gap unless separately added and verified.

## Recommended additional coverage

- Frontend form validation, loading, empty, success, and error states.
- Login, logout, and expired-token behavior.
- Workspace isolation across multiple owners.
- Invalid status transitions and API error responses.
- WebSocket disconnect, reconnect, and stale-update handling.
- Database migration and rollback rehearsal in a disposable test environment.

Record the command, environment, date, and actual result for every release check.
