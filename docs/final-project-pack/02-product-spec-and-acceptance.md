# Product Specification and Acceptance Criteria

## Product
SeatFlow Restaurant Waitlist

## Architecture
- Frontend: React, TypeScript, Vite.
- Backend: FastAPI.
- Data layer: SQLAlchemy and PostgreSQL.
- Schema migrations: Alembic.
- Authentication: document and verify the repository's JWT and password-hashing implementation.
- Live updates: WebSocket functionality, subject to integration-test verification.
- Local orchestration: Docker Compose.

## Core user journeys

### Journey A — Authentication
1. A user registers or signs in using the supported workflow.
2. Invalid credentials are rejected.
3. Authenticated requests include the expected authorization token.
4. Protected endpoints reject missing or invalid credentials.

### Journey B — Waitlist management
1. An authorized user opens the dashboard.
2. The application retrieves the waitlist and summary.
3. The user adds a guest or party.
4. The user performs a supported status transition.
5. The dashboard reflects the latest server state after refresh.

### Journey C — Workspace isolation
1. An authenticated user accesses their workspace.
2. Requests are scoped to the user's authorized workspace.
3. A user cannot read or modify another workspace's records.
4. Cross-workspace access attempts are covered by automated tests.

### Journey D — Recovery and consistency
1. A user changes a guest's status.
2. The server persists the change.
3. A refresh or reconnect retrieves the persisted state.
4. Repeated requests do not silently create duplicate records or invalid transitions.

## Acceptance criteria
- [ ] Frontend production build succeeds.
- [ ] Frontend lint succeeds.
- [ ] Backend unit/API tests pass.
- [ ] Invalid authentication is rejected.
- [ ] Workspace isolation is tested.
- [ ] Core waitlist transitions are tested.
- [ ] Statistics agree with persisted records.
- [ ] WebSocket reconnect and update behavior is tested, if supported.
- [ ] Database migrations run against a clean test database.
- [ ] Hosted health endpoint succeeds.
- [ ] Hosted database connection and migrations are verified.
- [ ] User-facing error states are understandable.
- [ ] Setup, testing, deployment, and rollback instructions are reproducible.

## Evidence rule
For each checkbox, record a test result, command output, CI run, or deployment
verification. Do not mark a criterion complete based solely on documentation.
