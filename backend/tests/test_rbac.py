from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

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


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=test_engine)

client = TestClient(app)


def register(
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


def headers(token: str):
    return {
        "Authorization": f"Bearer {token}"
    }


def create_staff(
    owner_token: str,
    email: str,
    role: str = "staff",
):
    response = client.post(
        "/api/users",
        headers=headers(owner_token),
        json={
            "email": email,
            "password": "StaffPassword123!",
            "role": role,
        },
    )

    assert response.status_code == 201, response.text

    return response.json()


# ------------------------------------------------------------
# RBAC
# ------------------------------------------------------------

def test_owner_can_list_users():
    owner = register(
        "Owner List Restaurant",
        "owner-list@example.com",
    )

    response = client.get(
        "/api/users",
        headers=headers(owner["access_token"]),
    )

    assert response.status_code == 200

    users = response.json()

    assert len(users) == 1
    assert users[0]["role"] == "owner"


def test_owner_can_create_staff():
    owner = register(
        "Staff Creation Restaurant",
        "staff-owner@example.com",
    )

    staff = create_staff(
        owner["access_token"],
        "staff@example.com",
        "staff",
    )

    assert staff["email"] == "staff@example.com"
    assert staff["role"] == "staff"
    assert (
        staff["restaurant_id"]
        == owner["user"]["restaurant_id"]
    )


def test_owner_can_create_manager():
    owner = register(
        "Manager Creation Restaurant",
        "manager-owner@example.com",
    )

    manager = create_staff(
        owner["access_token"],
        "manager@example.com",
        "manager",
    )

    assert manager["role"] == "manager"


def test_staff_cannot_create_users():
    owner = register(
        "Staff Restriction Restaurant",
        "staff-restriction-owner@example.com",
    )

    staff = create_staff(
        owner["access_token"],
        "restricted-staff@example.com",
        "staff",
    )

    staff_login = login(
        "restricted-staff@example.com",
        "StaffPassword123!",
    )

    response = client.post(
        "/api/users",
        headers=headers(
            staff_login["access_token"]
        ),
        json={
            "email": "another@example.com",
            "password": "Password123!",
            "role": "staff",
        },
    )

    assert response.status_code == 403


def test_staff_cannot_list_users():
    owner = register(
        "Staff List Restriction",
        "staff-list-owner@example.com",
    )

    staff = create_staff(
        owner["access_token"],
        "staff-list@example.com",
        "staff",
    )

    staff_login = login(
        "staff-list@example.com",
        "StaffPassword123!",
    )

    response = client.get(
        "/api/users",
        headers=headers(
            staff_login["access_token"]
        ),
    )

    assert response.status_code == 403


def test_manager_can_list_users():
    owner = register(
        "Manager List Restaurant",
        "manager-list-owner@example.com",
    )

    manager = create_staff(
        owner["access_token"],
        "manager-list@example.com",
        "manager",
    )

    manager_login = login(
        "manager-list@example.com",
        "StaffPassword123!",
    )

    response = client.get(
        "/api/users",
        headers=headers(
            manager_login["access_token"]
        ),
    )

    assert response.status_code == 200

    users = response.json()

    assert len(users) == 2


def test_manager_cannot_create_users():
    owner = register(
        "Manager Create Restriction",
        "manager-create-owner@example.com",
    )

    create_staff(
        owner["access_token"],
        "manager-create@example.com",
        "manager",
    )

    manager_login = login(
        "manager-create@example.com",
        "StaffPassword123!",
    )

    response = client.post(
        "/api/users",
        headers=headers(
            manager_login["access_token"]
        ),
        json={
            "email": "blocked@example.com",
            "password": "Password123!",
            "role": "staff",
        },
    )

    assert response.status_code == 403


def test_owner_can_change_staff_role():
    owner = register(
        "Role Change Restaurant",
        "role-owner@example.com",
    )

    staff = create_staff(
        owner["access_token"],
        "role-staff@example.com",
        "staff",
    )

    response = client.patch(
        f"/api/users/{staff['id']}/role",
        headers=headers(owner["access_token"]),
        json={
            "role": "manager",
        },
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["role"] == "manager"


def test_manager_cannot_change_roles():
    owner = register(
        "Manager Role Restriction",
        "manager-role-owner@example.com",
    )

    manager = create_staff(
        owner["access_token"],
        "manager-role@example.com",
        "manager",
    )

    staff = create_staff(
        owner["access_token"],
        "manager-role-staff@example.com",
        "staff",
    )

    manager_login = login(
        "manager-role@example.com",
        "StaffPassword123!",
    )

    response = client.patch(
        f"/api/users/{staff['id']}/role",
        headers=headers(
            manager_login["access_token"]
        ),
        json={
            "role": "manager",
        },
    )

    assert response.status_code == 403


def test_owner_role_cannot_be_changed():
    owner = register(
        "Owner Protection Restaurant",
        "owner-protection@example.com",
    )

    owner_id = owner["user"]["id"]

    response = client.patch(
        f"/api/users/{owner_id}/role",
        headers=headers(owner["access_token"]),
        json={
            "role": "staff",
        },
    )

    assert response.status_code == 400
    assert "Owner role cannot be changed" in response.json()["detail"]


def test_users_are_tenant_isolated():
    owner_one = register(
        "Tenant One",
        "tenant-one-owner@example.com",
    )

    owner_two = register(
        "Tenant Two",
        "tenant-two-owner@example.com",
    )

    staff_one = create_staff(
        owner_one["access_token"],
        "tenant-one-staff@example.com",
        "staff",
    )

    response = client.patch(
        f"/api/users/{staff_one['id']}/role",
        headers=headers(owner_two["access_token"]),
        json={
            "role": "manager",
        },
    )

    assert response.status_code == 404
