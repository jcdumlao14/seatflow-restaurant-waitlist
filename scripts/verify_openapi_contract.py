from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is not installed.")
    print("Install with: python -m pip install PyYAML")
    sys.exit(1)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "openapi.yaml"
BASE_URL = "http://127.0.0.1:8002"


def load_checked_in_contract() -> dict:
    with CONTRACT.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_live_contract() -> dict:
    request = Request(
        f"{BASE_URL}/openapi.json",
        headers={
            "Accept": "application/json",
            "User-Agent": "SeatFlow-OpenAPI-Drift-Checker/1.0",
        },
    )

    with urlopen(request, timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(
                f"Live OpenAPI endpoint returned HTTP {response.status}"
            )
        return json.load(response)


def normalize(payload: dict) -> dict:
    # JSON/YAML both represent the same OpenAPI structure.
    # Serialize and reload to remove representational differences.
    return json.loads(
        json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
        )
    )


def main() -> int:
    print("=" * 60)
    print(" SEATFLOW - OPENAPI CONTRACT DRIFT CHECK")
    print("=" * 60)
    print()

    if not CONTRACT.exists():
        print(f"FAIL: Missing contract: {CONTRACT}")
        return 1

    try:
        checked_in = load_checked_in_contract()
    except Exception as exc:
        print(f"FAIL: Could not read checked-in OpenAPI: {exc}")
        return 1

    try:
        live = load_live_contract()
    except Exception as exc:
        print(f"FAIL: Could not retrieve live OpenAPI: {exc}")
        return 1

    checked_in_normalized = normalize(checked_in)
    live_normalized = normalize(live)

    print(f"Checked-in contract: {CONTRACT}")
    print(f"Live contract:       {BASE_URL}/openapi.json")
    print()
    print(f"Checked-in version: {checked_in.get('openapi')}")
    print(f"Live version:       {live.get('openapi')}")
    print(f"Checked-in API:     {checked_in.get('info', {}).get('version')}")
    print(f"Live API:           {live.get('info', {}).get('version')}")
    print(
        f"Checked-in paths:   "
        f"{len(checked_in.get('paths', {}))}"
    )
    print(
        f"Live paths:         "
        f"{len(live.get('paths', {}))}"
    )
    print()

    if checked_in_normalized != live_normalized:
        print("FAIL: OPENAPI CONTRACT DRIFT DETECTED")
        print()
        print("The checked-in openapi.yaml does not match")
        print("the running FastAPI application's /openapi.json.")
        print()
        print("Regenerate the contract with:")
        print("  python .\\scripts\\generate_openapi.py")
        print("Then convert it with:")
        print("  python .\\scripts\\convert_openapi_to_yaml.py")
        print()
        return 1

    print("PASS: OpenAPI contract matches the live application.")
    print()
    print("=" * 60)
    print(" OPENAPI CONTRACT DRIFT CHECK PASSED")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
