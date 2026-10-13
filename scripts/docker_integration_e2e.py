from __future__ import annotations
import sys
import uuid
import httpx

BASE_URL = "http://127.0.0.1:8002"

def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[PASS] {message}")

def main() -> int:
    print("=" * 60)
    print(" SEATFLOW - DOCKER FULL-STACK INTEGRATION E2E")
    print("=" * 60)
    print()
    suffix = uuid.uuid4().hex[:10]
    email = f"integration_{suffix}@example.com"
    restaurant_name = f"Integration Restaurant {suffix}"
    customer = f"Integration Customer {suffix}"

    with httpx.Client(base_url=BASE_URL, timeout=15.0) as client:
        r = client.get("/health")
        check(r.status_code == 200, "Backend health endpoint")
        check(r.json().get("status") == "ok", "Health response status")
        r = client.post("/api/auth/register", json={"restaurant_name":restaurant_name, "email":email, "password":"IntegrationPass123!"})
        check(r.status_code == 201, "Owner registration")
        auth = r.json()
        token = auth["access_token"]
        user = auth["user"]
        check(auth["token_type"] == "bearer", "Bearer token returned")
        check(user["role"] == "owner", "Registered user has owner role")
        headers = {"Authorization": f"Bearer {token}"}
        r = client.get("/api/auth/me", headers=headers)
        check(r.status_code == 200, "Authenticated /me request")
        me = r.json()
        check(me["email"] == email, "Authenticated identity matches registration")
        restaurant_id = me["restaurant_id"]
        r = client.get("/api/waitlist", headers=headers)
        check(r.status_code == 200, "Initial waitlist retrieval")
        check(isinstance(r.json(), list), "Waitlist response is a list")
        r = client.post("/api/waitlist", headers=headers, json={"customer_name":customer,"phone":"09171234567","party_size":4})
        check(r.status_code == 201, "Waitlist entry creation")
        entry = r.json()
        entry_id = entry["id"]
        check(entry["restaurant_id"] == restaurant_id, "Waitlist entry is tenant-scoped")
        check(entry["status"] == "waiting", "New waitlist entry starts as waiting")
        r = client.get("/api/waitlist", headers=headers)
        check(r.status_code == 200, "Waitlist retrieval after creation")
        check(len([x for x in r.json() if x["id"] == entry_id]) == 1, "Created entry appears in waitlist")
        r = client.get("/api/waitlist/statistics/summary", headers=headers)
        check(r.status_code == 200, "Waitlist statistics")
        check(isinstance(r.json(), dict), "Statistics response is an object")
        r = client.post("/api/waitlist/call-next", headers=headers)
        check(r.status_code == 200, "Call-next operation")
        check(r.json()["id"] == entry_id, "Call-next selected the created entry")
        r = client.post(f"/api/waitlist/{entry_id}/seat", headers=headers)
        check(r.status_code == 200, "Seat operation")
        check(r.json()["status"] == "seated", "Entry transitioned to seated")
        r = client.get("/api/waitlist", headers=headers)
        check(r.status_code == 200, "Final waitlist retrieval")
        final_entry = next(x for x in r.json() if x["id"] == entry_id)
        check(final_entry["status"] == "seated", "Final waitlist state is seated")
        r = client.get("/api/waitlist")
        check(r.status_code in {401,403}, "Unauthorized waitlist request rejected")
        r = client.get("/api/waitlist", headers={"Authorization": "Bearer definitely-invalid-token"})
        check(r.status_code in {401,403}, "Invalid JWT rejected")
    print()
    print("=" * 60)
    print(" ALL DOCKER FULL-STACK INTEGRATION TESTS PASSED")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, httpx.HTTPError) as exc:
        print()
        print(f"[FAIL] {exc}")
        print()
        print("=" * 60)
        print(" DOCKER FULL-STACK INTEGRATION TEST FAILED")
        print("=" * 60)
        raise SystemExit(1)
