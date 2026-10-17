# SeatFlow On-Call Runbook

## Purpose

Provide a repeatable response to incidents affecting SeatFlow. Follow the organization's access controls and obtain authorization before production changes.

## Initial triage

1. Record the time, affected service, and reported user impact.
2. Check the hosted API health endpoint.
3. Inspect recent deployment and application logs.
4. Check database connectivity and migration status using authorized tools.
5. Determine whether the issue affects all users or one workspace.
6. Avoid publishing secrets or personal data in incident notes.
7. Record actions taken and the result of each diagnostic check.

## API unavailable

- Check service status and recent deployment logs.
- Look for startup errors, missing configuration, and dependency failures.
- Verify the application health endpoint.
- Escalate to the authorized operator if a production change is required.

## Login or database connection failure

- Determine whether the health endpoint succeeds while database-backed requests fail.
- Check the exact redacted application error.
- Verify privately that the configured database role is allowed to log in and has the required permissions.
- Check credentials privately in the provider dashboard.
- Confirm the connection URL uses a driver supported by the application.
- Do not paste credentials into chat, tickets, or logs.
- Do not reset, delete, or reprovision the production database as a diagnostic shortcut.

Known issue at the time of this document: production login returned a database error indicating that the configured role was not permitted to log in. Production authentication should remain marked unresolved until the database-role issue is corrected through an authorized process and login is retested.

## Waitlist data or statistics appear stale

- Use the dashboard refresh action.
- Inspect the waitlist and statistics API responses.
- Compare returned values with the authorized source data.
- Check server logs for failed requests or database errors.
- Confirm whether the issue is isolated to one workspace.
- Do not manually edit production records to hide a display inconsistency.

## Migration failure

- Stop repeated deployment attempts until the cause is understood.
- Preserve the exact error message after removing secrets.
- Identify the attempted migration and current schema revision.
- Check application-to-schema compatibility.
- Escalate before retrying, reverting, or restoring data.
- Use only the approved backup and recovery procedure.

## Recovery and incident closure

1. Verify API health and database-backed authentication.
2. Verify retrieval and modification of a test or otherwise authorized waitlist entry.
3. Verify statistics and any required live-update behavior.
4. Confirm the error rate has returned to an acceptable level using available evidence.
5. Record cause, impact, actions, verification, and follow-up work.

Do not declare recovery based solely on a successful health endpoint when login or database-backed operations were affected.

## Operational status

This is a documented runbook. Successful production incident-response, alert-delivery, and rollback rehearsals have not been established by the reported local test results. Mark these as unverified until exercised and recorded.
