from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is not installed.")
    print("Install with: python -m pip install PyYAML")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
OPENAPI_JSON = ROOT / "openapi.yaml"
TEMP_JSON = ROOT / "openapi.generated.json"
OUTPUT = ROOT / "openapi.yaml"


def main() -> int:
    print("=" * 60)
    print(" SEATFLOW - CONVERT OPENAPI CONTRACT TO YAML")
    print("=" * 60)
    print()

    if not OPENAPI_JSON.exists():
        print(f"ERROR: Missing {OPENAPI_JSON}")
        return 1

    try:
        payload = json.loads(
            OPENAPI_JSON.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        print(f"ERROR: openapi.yaml is not valid JSON: {exc}")
        return 1

    if payload.get("openapi") != "3.1.0":
        print(
            f"ERROR: Expected OpenAPI 3.1.0, "
            f"found {payload.get('openapi')!r}"
        )
        return 1

    # Preserve the generated JSON temporarily so the conversion is
    # completely reproducible and does not depend on manual editing.
    TEMP_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    yaml_text = yaml.safe_dump(
        payload,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=120,
    )

    OUTPUT.write_text(yaml_text, encoding="utf-8")

    TEMP_JSON.unlink(missing_ok=True)

    print(f"Output: {OUTPUT}")
    print(f"OpenAPI version: {payload.get('openapi')}")
    print(f"API title: {payload.get('info', {}).get('title')}")
    print(f"API version: {payload.get('info', {}).get('version')}")
    print(f"HTTP paths: {len(payload.get('paths', {}))}")
    print(
        "Component schemas: "
        f"{len(payload.get('components', {}).get('schemas', {}))}"
    )
    print()
    print("YAML serialization: PASS")
    print()
    print("=" * 60)
    print(" OPENAPI YAML CONVERSION COMPLETE")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
