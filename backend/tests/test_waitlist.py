import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_add_waitlist_entry():
    response = client.post(
        "/api/waitlist",
        json={
            "customer_name": "Alice",
            "phone": "09171234567",
            "party_size": 4,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["customer_name"] == "Alice"
    assert data["party_size"] == 4
    assert data["status"] == "waiting"


def test_get_waitlist():
    client.post(
        "/api/waitlist",
        json={
            "customer_name": "Queue Test",
            "phone": "09170000001",
            "party_size": 2,
        },
    )

    response = client.get("/api/waitlist")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["customer_name"] == "Queue Test"


def test_call_next():
    client.post(
        "/api/waitlist",
        json={
            "customer_name": "Call Next Test",
            "phone": "09170000002",
            "party_size": 2,
        },
    )

    response = client.post("/api/waitlist/call-next")

    assert response.status_code == 200
    assert response.json()["status"] == "notified"


def test_call_next_empty_queue():
    response = client.post("/api/waitlist/call-next")

    assert response.status_code == 404
    assert response.json()["detail"] == "No customers are currently waiting"


def test_seat_party():
    add_response = client.post(
        "/api/waitlist",
        json={
            "customer_name": "Seat Test",
            "phone": "09171111111",
            "party_size": 3,
        },
    )

    assert add_response.status_code == 201

    entry_id = add_response.json()["id"]

    response = client.post(
        f"/api/waitlist/{entry_id}/seat"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "seated"


def test_cancel_party():
    add_response = client.post(
        "/api/waitlist",
        json={
            "customer_name": "Cancel Test",
            "phone": "09172222222",
            "party_size": 2,
        },
    )

    entry_id = add_response.json()["id"]

    response = client.post(
        f"/api/waitlist/{entry_id}/cancel"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_no_show_party():
    add_response = client.post(
        "/api/waitlist",
        json={
            "customer_name": "No Show Test",
            "phone": "09173333333",
            "party_size": 2,
        },
    )

    entry_id = add_response.json()["id"]

    response = client.post(
        f"/api/waitlist/{entry_id}/no-show"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "no_show"


def test_statistics():
    client.post(
        "/api/waitlist",
        json={
            "customer_name": "Statistics Test",
            "phone": "09174444444",
            "party_size": 2,
        },
    )

    response = client.get(
        "/api/waitlist/statistics/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["waiting"] == 1
    assert data["notified"] == 0
    assert data["seated"] == 0
    assert data["cancelled"] == 0
    assert data["no_show"] == 0


def test_invalid_status():
    response = client.patch(
        "/api/waitlist/999999/status?status=invalid"
    )

    assert response.status_code == 400


def test_missing_entry():
    response = client.post(
        "/api/waitlist/999999/seat"
    )

    assert response.status_code == 404
    