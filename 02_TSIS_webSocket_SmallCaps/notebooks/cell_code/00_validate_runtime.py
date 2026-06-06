from __future__ import annotations

import importlib.util
import json
import platform
import sys

from _ws_common import ensure_layout, resolve_api_key, utc_now_iso


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def main() -> None:
    layout = ensure_layout()
    api_env, api_key = resolve_api_key()

    report = {
        "generated_at_utc": utc_now_iso(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "api_key_env": api_env,
        "api_key_present": bool(api_key),
        "modules": {
            "websockets": has_module("websockets"),
            "pandas": has_module("pandas"),
            "pyarrow": has_module("pyarrow"),
            "duckdb": has_module("duckdb"),
        },
        "paths": {name: str(path) for name, path in layout.items()},
    }

    print(json.dumps(report, indent=2))

    if not api_key:
        print(
            "\nWARNING: define MASSIVE_API_KEY o POLYGON_API_KEY antes de lanzar la captura."
        )


if __name__ == "__main__":
    main()
