from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--part", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    plan = load_json(args.plan)
    expected = {str(item["community_id"]) for item in plan["communities"]}
    labels: dict[str, str] = {}
    overlaps: list[str] = []
    for path in args.part:
        payload = load_json(path)
        if not isinstance(payload, dict):
            raise ValueError(f"Label part is not an object: {path}")
        for key, value in payload.items():
            if key in labels:
                overlaps.append(key)
            labels[key] = value

    missing = sorted(expected - set(labels), key=int)
    extra = sorted(set(labels) - expected, key=int)
    empty = sorted(
        key
        for key, value in labels.items()
        if not isinstance(value, str) or not value.strip()
    )
    by_label: dict[str, list[str]] = defaultdict(list)
    for key, value in labels.items():
        if isinstance(value, str):
            by_label[value.strip()].append(key)
    duplicate_labels = {
        label: keys for label, keys in by_label.items() if label and len(keys) > 1
    }
    if overlaps or missing or extra or empty or duplicate_labels:
        raise ValueError(
            f"Invalid labels: overlaps={overlaps}, missing={missing}, extra={extra}, "
            f"empty={empty}, duplicate_labels={duplicate_labels}"
        )

    ordered = {
        str(item["community_id"]): labels[str(item["community_id"])]
        for item in plan["communities"]
    }
    args.output.write_text(
        json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"communities={len(expected)}",
        f"parts={len(args.part)}",
        "overlaps=0 missing=0 extra=0 empty=0 duplicate_labels=0",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
