from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote

import httpx
import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatus


BASE_URL = os.getenv("SEATFLOW_TEST_BASE_URL", "http://127.0.0.1:8002")
WS_BASE_URL = BASE_URL.replace("http://", "ws://").replace("https://", "wss://")
TIMEOUT = 5.0


def unique_email(prefix: str) -> str:
    return f"{prefix}.{int(time.time() * 1000000)}@example.com"


def register_owner(client: httpx.Client, email: str, restaurant_name: str):
    response = client.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "restaurant_name": restaurant_name,
            "email": email,
            "password": "TestPassword123!",
        },
    )
    assert response.status_code == 201, (
        f"Register failed: {response.status_code} {response.text}"
    )
    return response.json()


async def receive_json(ws, timeout: float = TIMEOUT):
    raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    return json.loads(raw)


async def expect_no_message(ws, timeout: float = 1.0):
    try:
        message = await asyncio.wait_for(ws.recv(), timeout=timeout)
    except asyncio.TimeoutError:
        return True

    raise AssertionError(
        f"Unexpected WebSocket message received: {message!r}"
    )


async def run_test():
    print("=" * 60)
    print(" SEATFLOW - WEBSOCKET END-TO-END TEST")
    print("=" * 60)

    with httpx.Client(timeout=TIMEOUT) as client:
        # ---------------------------------------------------------
        # 1. Health
        # ---------------------------------------------------------
        response = client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        print("[PASS] Backend health")

        # ---------------------------------------------------------
        # 2. Create two independent tenants
        # ---------------------------------------------------------
        tenant1_email = unique_email("ws-tenant1")
        tenant2_email = unique_email("ws-tenant2")

        tenant1 = register_owner(
            client,
            tenant1_email,
            "WebSocket E2E Tenant One",
        )

        tenant2 = register_owner(
            client,
            tenant2_email,
            "WebSocket E2E Tenant Two",
        )

        token1 = tenant1["access_token"]
        token2 = tenant2["access_token"]

        user1 = tenant1["user"]
        user2 = tenant2["user"]

        restaurant1 = user1["restaurant_id"]
        restaurant2 = user2["restaurant_id"]

        assert restaurant1 != restaurant2
        print(
            f"[PASS] Created isolated tenants "
            f"(restaurant {restaurant1} != {restaurant2})"
        )

        # ---------------------------------------------------------
        # 3. Verify WebSocket authentication and tenant identity
        # ---------------------------------------------------------
        ws_url_1 = f"{WS_BASE_URL}/ws/waitlist?token={quote(token1)}"
        ws_url_2 = f"{WS_BASE_URL}/ws/waitlist?token={quote(token2)}"

        async with websockets.connect(ws_url_1) as ws1, \
                   websockets.connect(ws_url_2) as ws2:

            connected1 = await receive_json(ws1)
            connected2 = await receive_json(ws2)

            assert connected1["type"] == "connected"
            assert connected1["restaurant_id"] == restaurant1
            assert connected1["user_id"] == user1["id"]

            assert connected2["type"] == "connected"
            assert connected2["restaurant_id"] == restaurant2
            assert connected2["user_id"] == user2["id"]

            print("[PASS] Tenant 1 WebSocket authenticated")
            print("[PASS] Tenant 2 WebSocket authenticated")
            print("[PASS] WebSocket identity is derived from authenticated user")

            # -----------------------------------------------------
            # 4. Verify ping/pong
            # -----------------------------------------------------
            await ws1.send("ping")
            pong = await receive_json(ws1)

            assert pong == {"type": "pong"}
            print("[PASS] WebSocket ping/pong")

            # -----------------------------------------------------
            # 5. Tenant 1 creates a waitlist entry
            # -----------------------------------------------------
            create_response = client.post(
                f"{BASE_URL}/api/waitlist",
                headers={
                    "Authorization": f"Bearer {token1}",
                },
                json={
                    "customer_name": "WebSocket E2E Customer",
                    "phone": "09170000000",
                    "party_size": 3,
                },
            )

            assert create_response.status_code == 201, (
                f"Create waitlist failed: "
                f"{create_response.status_code} "
                f"{create_response.text}"
            )

            entry = create_response.json()
            entry_id = entry["id"]

            assert entry["restaurant_id"] == restaurant1

            print(
                f"[PASS] Tenant 1 waitlist entry created "
                f"(entry {entry_id})"
            )

            # -----------------------------------------------------
            # 6. Tenant 1 receives its own broadcast
            # -----------------------------------------------------
            update1 = await receive_json(ws1)

            assert update1["type"] == "waitlist.updated"
            assert update1["action"] == "created"
            assert update1["entry_id"] == entry_id
            print("[PASS] Tenant 1 received waitlist.updated")

            # -----------------------------------------------------
            # 7. Tenant 2 must NOT receive Tenant 1's broadcast
            # -----------------------------------------------------
            await expect_no_message(ws2, timeout=1.0)
            print("[PASS] Tenant 2 did not receive Tenant 1 event")

        # ---------------------------------------------------------
        # 8. Invalid token must be rejected
        # ---------------------------------------------------------
        invalid_url = (
            f"{WS_BASE_URL}/ws/waitlist"
            f"?token={quote('definitely-invalid-jwt-token')}"
        )

        rejected = False
        rejection_detail = ""

        try:
            async with websockets.connect(invalid_url) as invalid_ws:
                await receive_json(invalid_ws, timeout=2.0)

        except InvalidStatus as exc:
            # The application rejects invalid authentication before
            # websocket.accept(), so the HTTP upgrade is rejected.
            # FastAPI/Uvicorn exposes this to the client as HTTP 403.
            status_code = getattr(
                exc.response,
                "status_code",
                None,
            )

            rejected = status_code == 403
            rejection_detail = f"HTTP {status_code}"

        except ConnectionClosed as exc:
            # If the server accepts the connection and then closes it,
            # RFC WebSocket policy code 1008 is the expected rejection.
            rejected = exc.code == 1008
            rejection_detail = f"WebSocket close code {exc.code}"

        assert rejected, (
            "Invalid WebSocket token was not rejected correctly. "
            f"Observed: {rejection_detail}"
        )

        print(
            "[PASS] Invalid WebSocket token rejected "
            f"({rejection_detail})"
        )

    print()
    print("=" * 60)
    print(" ALL WEBSOCKET END-TO-END TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(run_test())
    except Exception as exc:
        print()
        print("=" * 60)
        print(" WEBSOCKET END-TO-END TEST FAILED")
        print("=" * 60)
        print(f"{type(exc).__name__}: {exc}")
        raise
