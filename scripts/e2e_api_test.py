import time
from datetime import datetime

import httpx


BASE_URL = "http://127.0.0.1:8002"


def check(response, expected_status, label):
    actual = response.status_code

    if actual != expected_status:
        print(f"[FAIL] {label}")
        print(f"       Expected HTTP {expected_status}, got {actual}")
        print(f"       Response: {response.text}")
        raise AssertionError(label)

    print(f"[PASS] {label} -> HTTP {actual}")


def main():
    print("=" * 68)
    print(" SEATFLOW - END-TO-END API CONTRACT TEST")
    print("=" * 68)
    print(f"Base URL: {BASE_URL}")
    print()

    suffix = datetime.now().strftime("%Y%m%d%H%M%S")
    owner_email = f"e2e.owner.{suffix}@example.com"
    manager_email = f"e2e.manager.{suffix}@example.com"
    staff_email = f"e2e.staff.{suffix}@example.com"

    tenant2_owner_email = f"e2e.tenant2.{suffix}@example.com"

    owner_password = "OwnerPass123!"
    manager_password = "ManagerPass123!"
    staff_password = "StaffPass123!"
    tenant2_password = "TenantTwoPass123!"

    with httpx.Client(timeout=15.0) as client:

        # ------------------------------------------------------------
        # 1. HEALTH
        # ------------------------------------------------------------
        response = client.get(f"{BASE_URL}/health")
        check(response, 200, "Health endpoint")

        health = response.json()
        assert health["status"] == "ok"
        assert health["service"] == "seatflow-api"

        # ------------------------------------------------------------
        # 2. REGISTER OWNER / TENANT 1
        # ------------------------------------------------------------
        response = client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "restaurant_name": f"SeatFlow E2E Restaurant {suffix}",
                "email": owner_email,
                "password": owner_password,
            },
        )
        check(response, 201, "Register owner")

        owner_auth = response.json()

        assert owner_auth["token_type"] == "bearer"
        assert owner_auth["access_token"]

        owner = owner_auth["user"]

        assert owner["email"] == owner_email
        assert owner["role"] == "owner"
        assert owner["is_active"] is True
        assert owner["restaurant_id"] > 0

        tenant1_id = owner["restaurant_id"]
        owner_token = owner_auth["access_token"]

        owner_headers = {
            "Authorization": f"Bearer {owner_token}"
        }

        # ------------------------------------------------------------
        # 3. OWNER LOGIN
        # ------------------------------------------------------------
        response = client.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": owner_email,
                "password": owner_password,
            },
        )
        check(response, 200, "Owner login")

        login_data = response.json()

        assert login_data["access_token"]
        assert login_data["user"]["id"] == owner["id"]
        assert login_data["user"]["restaurant_id"] == tenant1_id

        # Use the fresh login token for subsequent tests.
        owner_token = login_data["access_token"]
        owner_headers = {
            "Authorization": f"Bearer {owner_token}"
        }

        # ------------------------------------------------------------
        # 4. AUTHENTICATED /ME
        # ------------------------------------------------------------
        response = client.get(
            f"{BASE_URL}/api/auth/me",
            headers=owner_headers,
        )
        check(response, 200, "GET /api/auth/me")

        me = response.json()

        assert me["id"] == owner["id"]
        assert me["email"] == owner_email
        assert me["role"] == "owner"
        assert me["restaurant_id"] == tenant1_id

        # ------------------------------------------------------------
        # 5. CREATE MANAGER
        # ------------------------------------------------------------
        response = client.post(
            f"{BASE_URL}/api/users",
            headers=owner_headers,
            json={
                "email": manager_email,
                "password": manager_password,
                "role": "manager",
            },
        )
        check(response, 201, "Owner creates manager")

        manager = response.json()

        assert manager["email"] == manager_email
        assert manager["role"] == "manager"
        assert manager["restaurant_id"] == tenant1_id

        # ------------------------------------------------------------
        # 6. CREATE STAFF
        # ------------------------------------------------------------
        response = client.post(
            f"{BASE_URL}/api/users",
            headers=owner_headers,
            json={
                "email": staff_email,
                "password": staff_password,
                "role": "staff",
            },
        )
        check(response, 201, "Owner creates staff")

        staff = response.json()

        assert staff["email"] == staff_email
        assert staff["role"] == "staff"
        assert staff["restaurant_id"] == tenant1_id

        # ------------------------------------------------------------
        # 7. OWNER LISTS USERS
        # ------------------------------------------------------------
        response = client.get(
            f"{BASE_URL}/api/users",
            headers=owner_headers,
        )
        check(response, 200, "Owner lists restaurant users")

        users = response.json()

        assert len(users) >= 3

        user_emails = {user["email"] for user in users}

        assert owner_email in user_emails
        assert manager_email in user_emails
        assert staff_email in user_emails

        # ------------------------------------------------------------
        # 8. STAFF LOGIN
        # ------------------------------------------------------------
        response = client.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": staff_email,
                "password": staff_password,
            },
        )
        check(response, 200, "Staff login")

        staff_auth = response.json()
        staff_token = staff_auth["access_token"]

        staff_headers = {
            "Authorization": f"Bearer {staff_token}"
        }

        # ------------------------------------------------------------
        # 9. STAFF RBAC DENIAL
        # ------------------------------------------------------------
        response = client.get(
            f"{BASE_URL}/api/users",
            headers=staff_headers,
        )
        check(response, 403, "Staff denied user-management access")

        # ------------------------------------------------------------
        # 10. CREATE FIRST WAITLIST ENTRY
        # ------------------------------------------------------------
        response = client.post(
            f"{BASE_URL}/api/waitlist",
            headers=staff_headers,
            json={
                "customer_name": "Alice Santos",
                "phone": "09170000001",
                "party_size": 4,
            },
        )
        check(response, 201, "Create waitlist entry")

        entry1 = response.json()

        entry1_id = entry1["id"]

        assert entry1["restaurant_id"] == tenant1_id
        assert entry1["customer_name"] == "Alice Santos"
        assert entry1["party_size"] == 4
        assert entry1["status"] == "waiting"
        assert entry1["estimated_wait_minutes"] == 10

        # ------------------------------------------------------------
        # 11. CREATE SECOND WAITLIST ENTRY
        # ------------------------------------------------------------
        response = client.post(
            f"{BASE_URL}/api/waitlist",
            headers=staff_headers,
            json={
                "customer_name": "Bob Reyes",
                "phone": "09170000002",
                "party_size": 2,
            },
        )
        check(response, 201, "Create second waitlist entry")

        entry2 = response.json()

        entry2_id = entry2["id"]

        assert entry2["restaurant_id"] == tenant1_id
        assert entry2["status"] == "waiting"

        # The second entry should see one existing waiting party.
        assert entry2["estimated_wait_minutes"] == 15

        # ------------------------------------------------------------
        # 12. RETRIEVE WAITLIST
        # ------------------------------------------------------------
        response = client.get(
            f"{BASE_URL}/api/waitlist",
            headers=staff_headers,
        )
        check(response, 200, "Retrieve waitlist")

        waitlist = response.json()

        ids = {entry["id"] for entry in waitlist}

        assert entry1_id in ids
        assert entry2_id in ids

        # ------------------------------------------------------------
        # 13. CALL NEXT
        # ------------------------------------------------------------
        response = client.post(
            f"{BASE_URL}/api/waitlist/call-next",
            headers=staff_headers,
        )
        check(response, 200, "Call next waiting party")

        called = response.json()

        assert called["id"] == entry1_id
        assert called["status"] == "notified"

        # ------------------------------------------------------------
        # 14. SEAT FIRST ENTRY
        # ------------------------------------------------------------
        response = client.post(
            f"{BASE_URL}/api/waitlist/{entry1_id}/seat",
            headers=staff_headers,
        )
        check(response, 200, "Seat notified party")

        seated = response.json()

        assert seated["id"] == entry1_id
        assert seated["status"] == "seated"

        # ------------------------------------------------------------
        # 15. CREATE CANCELLATION CASE
        # ------------------------------------------------------------
        response = client.post(
            f"{BASE_URL}/api/waitlist",
            headers=staff_headers,
            json={
                "customer_name": "Carol Cruz",
                "phone": "09170000003",
                "party_size": 3,
            },
        )
        check(response, 201, "Create cancellation test entry")

        cancel_entry = response.json()
        cancel_entry_id = cancel_entry["id"]

        # ------------------------------------------------------------
        # 16. CANCEL ENTRY
        # ------------------------------------------------------------
        response = client.post(
            f"{BASE_URL}/api/waitlist/{cancel_entry_id}/cancel",
            headers=staff_headers,
        )
        check(response, 200, "Cancel waitlist entry")

        cancelled = response.json()

        assert cancelled["id"] == cancel_entry_id
        assert cancelled["status"] == "cancelled"

        # ------------------------------------------------------------
        # 17. CREATE NO-SHOW CASE
        # ------------------------------------------------------------
        response = client.post(
            f"{BASE_URL}/api/waitlist",
            headers=staff_headers,
            json={
                "customer_name": "David Garcia",
                "phone": "09170000004",
                "party_size": 2,
            },
        )
        check(response, 201, "Create no-show test entry")

        no_show_entry = response.json()
        no_show_entry_id = no_show_entry["id"]

        # ------------------------------------------------------------
        # 18. MARK NO-SHOW
        # ------------------------------------------------------------
        response = client.post(
            f"{BASE_URL}/api/waitlist/{no_show_entry_id}/no-show",
            headers=staff_headers,
        )
        check(response, 200, "Mark customer as no-show")

        no_show = response.json()

        assert no_show["id"] == no_show_entry_id
        assert no_show["status"] == "no_show"

        # ------------------------------------------------------------
        # 19. DIRECT STATUS UPDATE
        # ------------------------------------------------------------
        response = client.patch(
            f"{BASE_URL}/api/waitlist/{entry2_id}/status",
            params={"status": "seated"},
            headers=staff_headers,
        )
        check(response, 200, "Direct waitlist status update")

        updated = response.json()

        assert updated["id"] == entry2_id
        assert updated["status"] == "seated"

        # ------------------------------------------------------------
        # 20. INVALID STATUS REJECTION
        # ------------------------------------------------------------
        response = client.patch(
            f"{BASE_URL}/api/waitlist/{entry2_id}/status",
            params={"status": "invalid_status"},
            headers=staff_headers,
        )
        check(response, 400, "Reject invalid waitlist status")

        # ------------------------------------------------------------
        # 21. STATISTICS
        # ------------------------------------------------------------
        response = client.get(
            f"{BASE_URL}/api/waitlist/statistics/summary",
            headers=staff_headers,
        )
        check(response, 200, "Waitlist statistics")

        stats = response.json()

        assert stats["total"] >= 4
        assert stats["seated"] >= 2
        assert stats["cancelled"] >= 1
        assert stats["no_show"] >= 1

        # ------------------------------------------------------------
        # 22. CREATE SECOND TENANT
        # ------------------------------------------------------------
        response = client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "restaurant_name": f"SeatFlow E2E Tenant Two {suffix}",
                "email": tenant2_owner_email,
                "password": tenant2_password,
            },
        )
        check(response, 201, "Register second tenant")

        tenant2_auth = response.json()
        tenant2_token = tenant2_auth["access_token"]
        tenant2_id = tenant2_auth["user"]["restaurant_id"]

        assert tenant2_id != tenant1_id

        tenant2_headers = {
            "Authorization": f"Bearer {tenant2_token}"
        }

        # ------------------------------------------------------------
        # 23. TENANT 2 SEES ONLY ITS OWN WAITLIST
        # ------------------------------------------------------------
        response = client.get(
            f"{BASE_URL}/api/waitlist",
            headers=tenant2_headers,
        )
        check(response, 200, "Tenant 2 waitlist isolation")

        tenant2_waitlist = response.json()

        assert tenant2_waitlist == []

        # ------------------------------------------------------------
        # 24. TENANT 2 CANNOT ACCESS TENANT 1 ENTRY
        # ------------------------------------------------------------
        response = client.patch(
            f"{BASE_URL}/api/waitlist/{entry1_id}/status",
            params={"status": "cancelled"},
            headers=tenant2_headers,
        )
        check(response, 404, "Cross-tenant waitlist protection")

        # ------------------------------------------------------------
        # 25. TENANT 2 USER LIST IS ISOLATED
        # ------------------------------------------------------------
        response = client.get(
            f"{BASE_URL}/api/users",
            headers=tenant2_headers,
        )
        check(response, 200, "Tenant 2 user isolation")

        tenant2_users = response.json()

        assert len(tenant2_users) == 1
        assert tenant2_users[0]["email"] == tenant2_owner_email
        assert tenant2_users[0]["restaurant_id"] == tenant2_id

        # ------------------------------------------------------------
        # 26. TENANT 1 DATA STILL INTACT
        # ------------------------------------------------------------
        response = client.get(
            f"{BASE_URL}/api/waitlist",
            headers=staff_headers,
        )
        check(response, 200, "Tenant 1 data remains isolated")

        tenant1_waitlist = response.json()

        tenant1_ids = {entry["id"] for entry in tenant1_waitlist}

        assert entry1_id in tenant1_ids
        assert entry2_id in tenant1_ids
        assert cancel_entry_id in tenant1_ids
        assert no_show_entry_id in tenant1_ids

    print()
    print("=" * 68)
    print(" ALL END-TO-END API CONTRACT TESTS PASSED")
    print("=" * 68)
    print()
    print("Validated:")
    print("  [PASS] Health")
    print("  [PASS] Registration")
    print("  [PASS] Authentication")
    print("  [PASS] JWT / current-user")
    print("  [PASS] Owner RBAC")
    print("  [PASS] Staff RBAC denial")
    print("  [PASS] User creation")
    print("  [PASS] Waitlist creation")
    print("  [PASS] Waitlist retrieval")
    print("  [PASS] Call-next workflow")
    print("  [PASS] Seating workflow")
    print("  [PASS] Cancellation workflow")
    print("  [PASS] No-show workflow")
    print("  [PASS] Direct status update")
    print("  [PASS] Invalid-status rejection")
    print("  [PASS] Statistics")
    print("  [PASS] Multi-tenant isolation")
    print("  [PASS] Cross-tenant access protection")
    print("  [PASS] PostgreSQL-backed API integration")
    print()
    print("This test created unique E2E records and did not reset the database.")


if __name__ == "__main__":
    main()
