from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8002"
OUTPUT = Path("openapi.yaml")


def main() -> int:
    url = f"{BASE_URL}/openapi.json"

    print("=" * 60)
    print(" SEATFLOW - GENERATE OPENAPI CONTRACT")
    print("=" * 60)
    print()
    print(f"Source: {url}")
    print(f"Output: {OUTPUT}")

    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "SeatFlow-OpenAPI-Generator/1.0",
        },
    )

    try:
        with urlopen(request, timeout=10) as response:
            if response.status != 200:
                print(f"ERROR: HTTP {response.status}")
                return 1

            payload = json.load(response)

    except Exception as exc:
        print(f"ERROR: Could not retrieve OpenAPI schema: {exc}")
        return 1

    # PyYAML is not required. JSON is valid YAML 1.2 and can therefore
    # be stored in a .yaml contract artifact while preserving the exact
    # generated OpenAPI structure.
    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(f"Generated: {OUTPUT}")
    print(f"OpenAPI version: {payload.get('openapi')}")
    print(f"API title: {payload.get('info', {}).get('title')}")
    print(f"API version: {payload.get('info', {}).get('version')}")
    print(f"HTTP paths: {len(payload.get('paths', {}))}")
    print(f"Component schemas: {len(payload.get('components', {}).get('schemas', {}))}")

    print()
    print("=" * 60)
    print(" OPENAPI CONTRACT GENERATED")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
