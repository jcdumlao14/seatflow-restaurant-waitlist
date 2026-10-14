# SeatFlow Product Specification

## Problem
Restaurants need a reliable way to manage waiting parties, update service
statuses, and monitor queue activity.

## Product
SeatFlow is a restaurant waitlist application with a React/TypeScript
frontend, FastAPI backend, and PostgreSQL database.

## Intended users
Restaurant owners, managers, and authorized staff.

## Core requirements
- Authenticate users before protected operations.
- Enforce role permissions and restaurant tenant isolation.
- Manage waitlist entries and supported status transitions.
- Display statistics consistent with backend data.
- Persist records in PostgreSQL.
- Document HTTP APIs and authenticated WebSocket behavior.
- Run the local application using Docker Compose.

## Acceptance criteria
- Setup instructions work on a clean environment.
- Unauthorized access is rejected.
- Changes persist after application restarts.
- Statistics reflect persisted records.
- Tests cover core backend, frontend, and integration behavior.

This document defines intended behavior. Verify each requirement against the
current implementation and test results before claiming completion.
