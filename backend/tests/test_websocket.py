import jwt

from fastapi.testclient import TestClient

from app.api.websocket import authenticate_websocket
from app.api.websocket import router as websocket_router
from app.database import get_db
from app.main import app
from app.services.auth import ALGORITHM, SECRET_KEY


def register_user(
    client,
    restaurant_name,
    email,
):
    response = client.post(
        "/api/auth/register",
        json={
            "restaurant_name": restaurant_name,
            "email": email,
            "password": "SeatFlow123!",
        },
    )

    assert response.status_code == 201

    return response.json()


def get_test_db():
    override = app.dependency_overrides.get(get_db)

    assert override is not None, (
        "Test database override is not configured"
    )

    generator = override()
    db = next(generator)

    return generator, db


def close_test_db(generator):
    try:
        next(generator)

    except StopIteration:
        pass


def test_websocket_requires_token():

    with TestClient(app) as client:

        try:
            with client.websocket_connect(
                "/ws/waitlist"
            ) as websocket:

                websocket.receive_json()

        except Exception as exc:

            assert getattr(exc, "code", None) == 1008


def test_websocket_authenticate_function_accepts_valid_token():

    with TestClient(app) as client:

        auth = register_user(
            client,
            "Direct Auth Bistro",
            "direct-auth@example.com",
        )

        token = auth["access_token"]

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        assert str(payload["sub"]) == str(
            auth["user"]["id"]
        )

        generator, db = get_test_db()

        try:

            user = authenticate_websocket(
                token,
                db,
            )

            assert user is not None

            assert user.id == auth["user"]["id"]

            assert (
                user.restaurant_id
                == auth["user"]["restaurant_id"]
            )

        finally:
            close_test_db(generator)


def test_websocket_accepts_valid_token():

    with TestClient(app) as client:

        auth = register_user(
            client,
            "WS Bistro",
            "ws-owner@example.com",
        )

        token = auth["access_token"]

        with client.websocket_connect(
            f"/ws/waitlist?token={token}"
        ) as websocket:

            message = websocket.receive_json()

            assert message["type"] == "connected"

            assert (
                message["restaurant_id"]
                == auth["user"]["restaurant_id"]
            )

            assert (
                message["user_id"]
                == auth["user"]["id"]
            )


def test_websocket_rejects_invalid_token():

    with TestClient(app) as client:

        try:

            with client.websocket_connect(
                "/ws/waitlist?token=invalid-token"
            ) as websocket:

                websocket.receive_json()

        except Exception as exc:

            assert getattr(exc, "code", None) == 1008


def test_websocket_is_tenant_scoped():

    with TestClient(app) as client:

        first = register_user(
            client,
            "First Bistro",
            "first@example.com",
        )

        second = register_user(
            client,
            "Second Bistro",
            "second@example.com",
        )

        token_one = first["access_token"]
        token_two = second["access_token"]

        with client.websocket_connect(
            f"/ws/waitlist?token={token_one}"
        ) as ws_one:

            connected_one = ws_one.receive_json()

            assert (
                connected_one["restaurant_id"]
                == first["user"]["restaurant_id"]
            )

            with client.websocket_connect(
                f"/ws/waitlist?token={token_two}"
            ) as ws_two:

                connected_two = ws_two.receive_json()

                assert (
                    connected_two["restaurant_id"]
                    == second["user"]["restaurant_id"]
                )

                assert (
                    connected_one["restaurant_id"]
                    != connected_two["restaurant_id"]
                )

                ws_one.send_text("ping")

                pong_one = ws_one.receive_json()

                assert pong_one["type"] == "pong"

                ws_two.send_text("ping")

                pong_two = ws_two.receive_json()

                assert pong_two["type"] == "pong"
