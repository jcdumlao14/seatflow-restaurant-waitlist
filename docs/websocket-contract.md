# SeatFlow WebSocket Contract

## Overview

SeatFlow provides a real-time WebSocket endpoint for authenticated restaurant waitlist updates.

Endpoint: `/ws/waitlist`

The endpoint is documented separately from `openapi.yaml` because OpenAPI describes the HTTP API and does not natively define the WebSocket messaging protocol.

## Connection

Local development: `ws://<host>/ws/waitlist?token=<JWT>`

Production: `wss://<host>/ws/waitlist?token=<JWT>`

The JWT is supplied through the `token` query parameter. The server validates the JWT, authenticated user, active status, restaurant ID, and tenant consistency.

## Connected Message

```json
{
  "type": "connected",
  "restaurant_id": 1,
  "user_id": 10
}
```

## Ping/Pong

The client may send `ping`. The server responds with:

```json
{
  "type": "pong"
}
```

## Waitlist Update Events

When a waitlist operation changes state, the server broadcasts:

```json
{
  "type": "waitlist.updated",
  "action": "created",
  "entry_id": 123
}
```

Supported actions: `created`, `called`, `status_changed`, `seated`, `cancelled`, `no_show`.

## Tenant Isolation

WebSocket connections are grouped by the authenticated user's `restaurant_id`). Events are broadcast only to connections belonging to the same restaurant. The client cannot switch tenants by supplying another restaurant identifier.

## Authentication Failure

Missing or invalid authentication is rejected. Depending on the handshake stage, the client may observe HTTP 403 or WebSocket close code 1008.

## Reconnection

The frontend reconnects after a connection failure and refreshes the waitlist state after reconnection.

## REST and WebSocket Relationship

REST endpoints perform waitlist mutations. WebSocket messages notify connected clients that the waitlist changed, and the frontend refreshes current state through the REST API.

Expected flow:

1. Client authenticates through REST.
2. Client receives a JWT.
3. Client opens `/ws/waitlist?token=<JWT>`.
4. Server authenticates the JWT and derives the tenant.
5. A REST waitlist operation changes application state.
6. Backend broadcasts `waitlist.updated`^.
7. Connected clients receive the event.
8. Frontend refreshes waitlist data.

## Verification

The contract is verified by `scripts/websocket_e2e_test.py`.

The E2E test covers backend health, isolated tenants, authenticated WebSocket connections, user identity, ping/pong, event delivery, cross-tenant isolation, and invalid-token rejection.

Successful verification reports `ALL WEBSOCKET END-TO-END TESTS PASSED`.

## Security

Production deployments must use HTTPS and `wss://`. JWTs should be issued only over HTTPS and protected by the client. Tenant identity must be derived from the authenticated token rather than a client-provided restaurant identifier.

The local Docker configuration uses `ws://` for development.
