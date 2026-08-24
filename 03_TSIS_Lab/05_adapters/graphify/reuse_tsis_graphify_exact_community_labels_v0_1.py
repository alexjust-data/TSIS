from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def signature(community: dict[str, Any]) -> tuple[int, tuple[str, ...]]:
    return (
        int(community["member_count"]),
        tuple(sorted(str(node["id"]) for node in community["top_nodes"])),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-plan", type=Path, required=True)
    parser.add_argument("--old-labels", type=Path, required=True)
    parser.add_argument("--new-plan", type=Path, required=True)
    args = parser.parse_args()

    old_plan = load_json(args.old_plan)
    old_labels = load_json(args.old_labels)
    new_plan = load_json(args.new_plan)
    output_dir = args.new_plan.parent

    old_index: dict[tuple[int, tuple[str, ...]], list[int]] = defaultdict(list)
    for community in old_plan["communities"]:
        old_index[signature(community)].append(int(community["community_id"]))

    reused: dict[str, str] = {}
    changed: list[dict[str, Any]] = []
    for community in new_plan["communities"]:
        old_ids = old_index.get(signature(community), [])
        if len(old_ids) == 1:
            reused[str(community["community_id"])] = old_labels[str(old_ids[0])]
        else:
            changed.append(community)

    changed_plan = {
        **new_plan,
        "communities": changed,
        "output_path": str(output_dir / "community_labels_changed.json"),
    }
    (output_dir / "community_labels_reused.json").write_text(
        json.dumps(reused, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "community_label_plan_changed.json").write_text(
        json.dumps(changed_plan, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"old={len(old_plan['communities'])}",
        f"new={len(new_plan['communities'])}",
        f"reused={len(reused)}",
        f"changed={len(changed)}",
    )
    print("changed_ids", [community["community_id"] for community in changed])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
