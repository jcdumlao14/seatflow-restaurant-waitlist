# Final Project Submission Checklist

## Product and specification
- [ ] Problem and target users are clear.
- [ ] Product specification and acceptance criteria match the implementation.
- [ ] Agent-team roles, permissions, and approval gates are documented.
- [ ] Context-management and repository instructions are documented.

## Application
- [ ] Core user journeys work end to end.
- [ ] Authentication and workspace isolation are verified.
- [ ] Database persistence is verified.
- [ ] Live updates are tested if included in the product scope.

## Testing
- [ ] Backend tests run and pass.
- [ ] Frontend lint and build run and pass.
- [ ] Frontend tests are present or the decision and gap are documented.
- [ ] Database migrations are tested.
- [ ] Integration and error-path tests are evidenced.

## Delivery
- [ ] Docker Compose services start correctly.
- [ ] Hosted frontend is reachable.
- [ ] Hosted API is reachable.
- [ ] Production database connectivity is verified.
- [ ] Production schema migrations are verified.
- [ ] CI checks run automatically on pull requests or pushes.
- [ ] Deployment and rollback instructions are tested.

## Operations
- [ ] Logs and health checks support troubleshooting.
- [ ] User-impact alert rules are configured.
- [ ] A test alert is delivered and recovery is confirmed.
- [ ] On-call runbook and escalation path are available.
- [ ] No secrets are committed or published.

## Peer reviews
- [ ] Review participant project 1 and submit useful feedback.
- [ ] Review participant project 2 and submit useful feedback.
- [ ] Review participant project 3 and submit useful feedback.

## Final evidence
For every completed item, keep a reproducible command, test result, CI run,
deployment check, screenshot, or other appropriate evidence.
Documentation alone is not proof that a feature works.
