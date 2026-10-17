# Observability and User-Impact Alerting

## Objective

Detect failures that affect restaurant staff and waitlist operations, rather than relying only on whether a process is running.

This document describes recommended monitoring. Do not treat a signal, dashboard, or alert as implemented unless its configuration and operation have been verified.

## Signals to collect

### Availability
- API health-check success rate.
- Failed requests and HTTP status distribution.
- Frontend-to-backend connectivity.

### Latency
- API response latency.
- Database connection and query delays.
- Time to load and refresh the waitlist.

### Correctness
- Failed waitlist mutations.
- Authentication and authorization failures.
- Mismatch between queue records and summary statistics.
- WebSocket disconnects or failed updates, if supported.

### Infrastructure
- Database connection failures.
- Container restarts.
- Deployment and migration failures.
- Resource saturation where metrics are available.

## User-impact alerts

Prioritize alerts that indicate staff cannot sign in, retrieve the queue, or update guest status.

Suggested alert conditions:
- Repeated API health-check failures.
- Elevated server-error rates over a sustained interval.
- Database connection or authentication failures.
- Repeated failures in waitlist mutations.
- Sustained latency that prevents normal queue operations.
- WebSocket failures where real-time updates are a required feature.

Define thresholds using observed baseline traffic and the monitoring platform's capabilities. Avoid claiming specific alert thresholds are active until the configuration is inspected.

## Response expectations

For every production alert, document:
- Alert name and user impact.
- Trigger condition and evaluation window.
- Responsible operator or escalation route.
- First diagnostic checks.
- Recovery or mitigation procedure.
- Evidence required to close the incident.

Avoid logging tokens, passwords, database URLs, or unnecessary personal information.

## Verification and current status

The local application health endpoint and local integration checks have been verified in the reported test run. These checks do not establish that production alerting, dashboards, notification delivery, or recovery automation are configured and working.

Before marking observability complete:
1. Inspect the actual monitoring and alert configuration.
2. Verify the notification destination and authorized responders.
3. Trigger a safe test alert in the approved environment.
4. Confirm notification receipt and recovery behavior.
5. Record timestamps and redacted evidence.

Until those checks are demonstrated, treat alert delivery and end-to-end alert testing as outstanding verification items.
