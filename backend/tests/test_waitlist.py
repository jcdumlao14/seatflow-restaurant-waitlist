from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def register_and_login():
    response = client.post(
        "/api/auth/register",
        json={
            "restaurant_name": "Waitlist Test Restaurant",
            "email": "waitlist-owner@example.com",
            "password": "SeatFlow123!",
        },
    )

    if response.status_code == 201:
        return response.json()["access_token"]

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "waitlist-owner@example.com",
            "password": "SeatFlow123!",
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


TOKEN = register_and_login()

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}


def test_add_waitlist_entry():
    response = client.post(
        "/api/waitlist",
        headers=HEADERS,
        json={
            "customer_name": "Alice",
            "phone": "09171234567",
            "party_size": 4,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["customer_name"] == "Alice"
    assert data["phone"] == "09171234567"
    assert data["party_size"] == 4
    assert data["status"] == "waiting"
    assert data["restaurant_id"] > 0


def test_get_waitlist():
    client.post(
        "/api/waitlist",
        headers=HEADERS,
        json={
            "customer_name": "Queue Test",
            "phone": "09170000001",
            "party_size": 2,
        },
    )

    response = client.get(
        "/api/waitlist",
        headers=HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert any(
        entry["customer_name"] == "Queue Test"
        for entry in data
    )


def test_call_next():
    client.post(
        "/api/waitlist",
        headers=HEADERS,
        json={
            "customer_name": "Call Next Test",
            "phone": "09170000002",
            "party_size": 2,
        },
    )

    response = client.post(
        "/api/waitlist/call-next",
        headers=HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "notified"


def test_call_next_empty_queue():
    register_response = client.post(
        "/api/auth/register",
        json={
            "restaurant_name": "Empty Queue Restaurant",
            "email": "empty-queue@example.com",
            "password": "SeatFlow123!",
        },
    )

    assert register_response.status_code == 201

    empty_token = register_response.json()["access_token"]

    response = client.post(
        "/api/waitlist/call-next",
        headers={
            "Authorization": f"Bearer {empty_token}"
        },
    )

    assert response.status_code == 404


def test_seat_party():
    add_response = client.post(
        "/api/waitlist",
        headers=HEADERS,
        json={
            "customer_name": "Seat Test",
            "phone": "09171111111",
            "party_size": 3,
        },
    )

    assert add_response.status_code == 201

    entry_id = add_response.json()["id"]

    response = client.post(
        f"/api/waitlist/{entry_id}/seat",
        headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "seated"


def test_cancel_party():
    add_response = client.post(
        "/api/waitlist",
        headers=HEADERS,
        json={
            "customer_name": "Cancel Test",
            "phone": "09172222222",
            "party_size": 2,
        },
    )

    assert add_response.status_code == 201

    entry_id = add_response.json()["id"]

    response = client.post(
        f"/api/waitlist/{entry_id}/cancel",
        headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_no_show_party():
    add_response = client.post(
        "/api/waitlist",
        headers=HEADERS,
        json={
            "customer_name": "No Show Test",
            "phone": "09173333333",
            "party_size": 2,
        },
    )

    assert add_response.status_code == 201

    entry_id = add_response.json()["id"]

    response = client.post(
        f"/api/waitlist/{entry_id}/no-show",
        headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "no_show"


def test_statistics():
    client.post(
        "/api/waitlist",
        headers=HEADERS,
        json={
            "customer_name": "Statistics Test",
            "phone": "09174444444",
            "party_size": 2,
        },
    )

    response = client.get(
        "/api/waitlist/statistics/summary",
        headers=HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert "total" in data
    assert "waiting" in data
    assert "notified" in data
    assert "seated" in data
    assert "cancelled" in data
    assert "no_show" in data


def test_invalid_status():
    response = client.patch(
        "/api/waitlist/999999/status?status=invalid",
        headers=HEADERS,
    )

    assert response.status_code == 400


def test_missing_entry():
    response = client.post(
        "/api/waitlist/999999/seat",
        headers=HEADERS,
    )

    assert response.status_code == 404
