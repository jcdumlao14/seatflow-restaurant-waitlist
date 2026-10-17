# SeatFlow — Problem and Solution

## Project overview
SeatFlow is a web-based restaurant waitlist management application.
The repository includes a React + TypeScript frontend and a FastAPI backend.
The project is designed to support restaurant waitlist operations through an
API-backed dashboard and persistent database.

## Problem statement
Restaurants may manage guest queues using paper lists, spreadsheets, or
disconnected tools. These approaches can make it difficult to keep queue
status consistent, see the current waiting list, and coordinate updates.

## Proposed solution
SeatFlow provides a centralized interface and backend for managing guest
waitlist records and their status. The intended workflow includes adding
guests, viewing the queue, updating guest status, and refreshing operational
statistics.

## Intended users
- Restaurant staff who manage the waitlist.
- Restaurant managers who oversee the queue.
- Authorized restaurant workspace owners or administrators.

These user roles and permissions must match the implemented authorization
rules; do not assume a role can perform an action without verifying it.

## Scope
- Authentication and workspace access.
- Waitlist management and status transitions.
- Waitlist and summary API endpoints.
- Persistent database storage.
- Live updates where WebSocket functionality is enabled.
- Containerized local execution and hosted deployment.

## Success measures
Record measured results instead of inventing performance claims:
- Automated tests pass.
- A user can complete the core waitlist workflow.
- Data remains consistent after refresh and service restart.
- Unauthorized users cannot access another workspace's data.
- Production health and database connectivity are verified.
- Deployment and recovery procedures are documented.
