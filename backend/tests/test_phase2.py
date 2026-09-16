from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app


# ---------------------------------------------------------------------
# Test database
# ---------------------------------------------------------------------

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


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=test_engine)

client = TestClient(app)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def register_restaurant(
    restaurant_name: str,
    email: str,
    password: str = "Password123!",
):
    response = client.post(
        "/api/auth/register",
        json={
            "restaurant_name": restaurant_name,
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201, response.text

    return response.json()


def login(
    email: str,
    password: str = "Password123!",
):
    response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200, response.text

    return response.json()


def auth_headers(token: str):
    return {
        "Authorization": f"Bearer {token}"
    }


# ---------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------

def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ---------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------

def test_register_restaurant_owner():
    data = register_restaurant(
        "Test Restaurant",
        "owner@testrestaurant.com",
    )

    assert data["access_token"]
    assert data["token_type"] == "bearer"

    assert data["user"]["email"] == "owner@testrestaurant.com"
    assert data["user"]["role"] == "owner"
    assert data["user"]["is_active"] is True

    assert data["user"]["restaurant_id"] > 0


def test_duplicate_email_is_rejected():
    register_restaurant(
        "Restaurant One",
        "duplicate@example.com",
    )

    response = client.post(
        "/api/auth/register",
        json={
            "restaurant_name": "Restaurant Two",
            "email": "duplicate@example.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_short_password_is_rejected():
    response = client.post(
        "/api/auth/register",
        json={
            "restaurant_name": "Short Password Restaurant",
            "email": "short@example.com",
            "password": "1234567",
        },
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------

def test_login_success():
    register_restaurant(
        "Login Restaurant",
        "login@example.com",
    )

    data = login(
        "login@example.com",
    )

    assert data["access_token"]
    assert data["user"]["email"] == "login@example.com"
    assert data["user"]["role"] == "owner"


def test_login_wrong_password():
    register_restaurant(
        "Wrong Password Restaurant",
        "wrongpassword@example.com",
    )

    response = client.post(
        "/api/auth/login",
        json={
            "email": "wrongpassword@example.com",
            "password": "WrongPassword!",
        },
    )

    assert response.status_code == 401


def test_login_unknown_email():
    response = client.post(
        "/api/auth/login",
        json={
            "email": "doesnotexist@example.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 401


# ---------------------------------------------------------------------
# /me
# ---------------------------------------------------------------------

def test_me_returns_current_user():
    data = register_restaurant(
        "Me Restaurant",
        "me@example.com",
    )

    token = data["access_token"]

    response = client.get(
        "/api/auth/me",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    user = response.json()

    assert user["email"] == "me@example.com"
    assert user["role"] == "owner"
    assert user["restaurant_id"] == data["user"]["restaurant_id"]


def test_me_requires_authentication():
    response = client.get("/api/auth/me")

    assert response.status_code == 401


# ---------------------------------------------------------------------
# Protected waitlist endpoints
# ---------------------------------------------------------------------

def test_waitlist_requires_authentication():
    response = client.get("/api/waitlist")

    assert response.status_code == 401


def test_create_waitlist_entry_authenticated():
    data = register_restaurant(
        "Waitlist Restaurant",
        "waitlist@example.com",
    )

    token = data["access_token"]

    response = client.post(
        "/api/waitlist",
        headers=auth_headers(token),
        json={
            "customer_name": "Alice",
            "phone": "09171234567",
            "party_size": 4,
        },
    )

    assert response.status_code == 201

    entry = response.json()

    assert entry["customer_name"] == "Alice"
    assert entry["phone"] == "09171234567"
    assert entry["party_size"] == 4
    assert entry["status"] == "waiting"
    assert entry["restaurant_id"] if "restaurant_id" in entry else True


def test_authenticated_user_can_get_waitlist():
    data = register_restaurant(
        "Get Waitlist Restaurant",
        "getwaitlist@example.com",
    )

    token = data["access_token"]

    client.post(
        "/api/waitlist",
        headers=auth_headers(token),
        json={
            "customer_name": "Bob",
            "phone": "09170000001",
            "party_size": 2,
        },
    )

    response = client.get(
        "/api/waitlist",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    entries = response.json()

    assert len(entries) == 1
    assert entries[0]["customer_name"] == "Bob"


# ---------------------------------------------------------------------
# Tenant isolation
# ---------------------------------------------------------------------

def test_tenant_isolation_between_restaurants():
    restaurant_a = register_restaurant(
        "Restaurant A",
        "owner-a@example.com",
    )

    restaurant_b = register_restaurant(
        "Restaurant B",
        "owner-b@example.com",
    )

    token_a = restaurant_a["access_token"]
    token_b = restaurant_b["access_token"]

    # Restaurant A creates a customer.
    create_response = client.post(
        "/api/waitlist",
        headers=auth_headers(token_a),
        json={
            "customer_name": "Customer A",
            "phone": "09171111111",
            "party_size": 3,
        },
    )

    assert create_response.status_code == 201

    entry_a = create_response.json()
    entry_id = entry_a["id"]

    # Restaurant A can see its own customer.
    response_a = client.get(
        "/api/waitlist",
        headers=auth_headers(token_a),
    )

    assert response_a.status_code == 200

    entries_a = response_a.json()

    assert len(entries_a) == 1
    assert entries_a[0]["customer_name"] == "Customer A"

    # Restaurant B must NOT see Restaurant A's customer.
    response_b = client.get(
        "/api/waitlist",
        headers=auth_headers(token_b),
    )

    assert response_b.status_code == 200

    entries_b = response_b.json()

    assert entries_b == []

    # Restaurant B must not be able to modify Restaurant A's entry.
    modify_response = client.post(
        f"/api/waitlist/{entry_id}/seat",
        headers=auth_headers(token_b),
    )

    assert modify_response.status_code == 404


def test_tenant_isolation_for_call_next():
    restaurant_a = register_restaurant(
        "Call Next A",
        "callnext-a@example.com",
    )

    restaurant_b = register_restaurant(
        "Call Next B",
        "callnext-b@example.com",
    )

    token_a = restaurant_a["access_token"]
    token_b = restaurant_b["access_token"]

    client.post(
        "/api/waitlist",
        headers=auth_headers(token_a),
        json={
            "customer_name": "Alice A",
            "phone": "09172222222",
            "party_size": 2,
        },
    )

    # Restaurant B has no customers.
    response_b = client.post(
        "/api/waitlist/call-next",
        headers=auth_headers(token_b),
    )

    assert response_b.status_code == 404

    # Restaurant A can call its own customer.
    response_a = client.post(
        "/api/waitlist/call-next",
        headers=auth_headers(token_a),
    )

    assert response_a.status_code == 200
    assert response_a.json()["customer_name"] == "Alice A"
    assert response_a.json()["status"] == "notified"


# ---------------------------------------------------------------------
# Statistics isolation
# ---------------------------------------------------------------------

def test_statistics_are_tenant_isolated():
    restaurant_a = register_restaurant(
        "Stats A",
        "stats-a@example.com",
    )

    restaurant_b = register_restaurant(
        "Stats B",
        "stats-b@example.com",
    )

    token_a = restaurant_a["access_token"]
    token_b = restaurant_b["access_token"]

    client.post(
        "/api/waitlist",
        headers=auth_headers(token_a),
        json={
            "customer_name": "Stats Customer",
            "phone": "09173333333",
            "party_size": 5,
        },
    )

    stats_a = client.get(
        "/api/waitlist/statistics/summary",
        headers=auth_headers(token_a),
    )

    stats_b = client.get(
        "/api/waitlist/statistics/summary",
        headers=auth_headers(token_b),
    )

    assert stats_a.status_code == 200
    assert stats_b.status_code == 200

    assert stats_a.json()["total"] == 1
    assert stats_a.json()["waiting"] == 1

    assert stats_b.json()["total"] == 0
    assert stats_b.json()["waiting"] == 0
    

