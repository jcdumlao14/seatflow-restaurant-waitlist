# Containerization, Deployment, and Rollback

## Local containerization

The Docker Compose configuration defines `postgres`, `backend`, and `frontend`.

Reported local verification on 2026-10-17:
- `docker compose config --quiet` passed.
- The backend, frontend, and PostgreSQL containers were running; PostgreSQL was reported healthy.
- The local backend health endpoint returned HTTP 200.
- The frontend returned HTTP 200.
- The integration script passed 23 checks.

A running container alone is not proof that every application workflow works. Recheck logs, health, and the integration test after relevant changes.

Useful commands:

```powershell
docker compose config --services
docker compose ps
docker compose logs --tail 100 backend
docker compose logs --tail 100 frontend
docker compose logs --tail 100 postgres
```

## Hosted deployment status

The hosted frontend and API endpoints were reported reachable. The API health endpoint returned HTTP 200.

Production login is **not verified as working**. The observed database error was:

`FATAL: role "seatflow_40ho_user" is not permitted to log in`

Treat this as an unresolved production database-role issue. API health success does not establish that authenticated requests or database-backed workflows succeed. Do not describe production deployment as fully validated.

Do not reset, delete, replace, or reprovision the production database as a diagnostic shortcut.

## Deployment readiness checklist

Before declaring a release ready:
- Confirm the intended branch and commit.
- Review CI results for that exact commit.
- Verify required environment variable names and configured values privately.
- Confirm application-role database login and database-backed application requests.
- Apply migrations using the approved deployment process.
- Verify the resulting schema revision.
- Confirm CORS and the frontend API base URL.
- Verify health and authenticated application workflows.
- Ensure logs do not expose credentials or personal data.

Do not claim production database connectivity or production migrations are verified until evidence is collected.

## Migration safety

1. Review the migration file and its parent revision.
2. Back up data using the approved provider procedure before a production schema change.
3. Test the migration in a disposable or staging environment first.
4. Confirm compatibility between the application version and the resulting schema.
5. Apply the migration only with authorization and a documented recovery plan.
6. Verify the current revision and run relevant smoke tests.

Never use `docker compose down -v` as a routine deployment or rollback command; it can remove local database volumes. Do not run destructive database commands without explicit approval.

## Rollback procedure

- Pause further rollout attempts if the deployment is unhealthy.
- Identify the deployed commit, application logs, and migration revision.
- If safe, redeploy the last known-good application version using the approved provider workflow.
- Check whether the old application version is compatible with the current schema.
- Restore data or reverse a schema change only through an approved, tested recovery procedure.
- Verify health and critical user journeys, then document the incident and result.

A rollback procedure is documented here; a successful rollback rehearsal has not been established by the local test results above.
