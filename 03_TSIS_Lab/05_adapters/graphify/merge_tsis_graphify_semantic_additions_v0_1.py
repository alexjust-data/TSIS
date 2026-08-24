from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


FAMILIES = ("nodes", "edges", "hyperedges")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def norm(path: str) -> str:
    return str(Path(path)).replace("\\", "/").casefold()


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge validated semantic records for newly added corpus files.")
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--additions", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()

    plan = load(args.plan)
    additions = load(args.additions)
    if not isinstance(additions, dict):
        raise ValueError("Additions must be an object")

    chunks: dict[int, tuple[Path, dict]] = {}
    file_to_chunk: dict[str, int] = {}
    existing_ids: set[str] = set()
    for entry in plan["chunks"]:
        number = int(entry["chunk_num"])
        path = Path(entry["output_path"])
        payload = load(path)
        chunks[number] = (path, payload)
        for file_path in entry["files"]:
            file_to_chunk[norm(file_path)] = number
        existing_ids.update(str(node["id"]) for node in payload.get("nodes", []))

    new_nodes = additions.get("nodes", [])
    new_edges = additions.get("edges", [])
    new_hyperedges = additions.get("hyperedges", [])
    if not all(isinstance(record, dict) for family in (new_nodes, new_edges, new_hyperedges) for record in family):
        raise ValueError("All semantic records must be objects")

    new_ids = [str(node.get("id", "")) for node in new_nodes]
    if any(not value for value in new_ids) or len(new_ids) != len(set(new_ids)):
        raise ValueError("New node IDs are empty or duplicated")
    collisions = sorted(existing_ids & set(new_ids))
    if collisions:
        raise ValueError(f"New node IDs collide with existing records: {collisions[:10]}")
    all_ids = existing_ids | set(new_ids)

    normalized_edges = []
    for edge in new_edges:
        edge = dict(edge)
        if "relation" not in edge and "relationship" in edge:
            edge["relation"] = edge.pop("relationship")
        if str(edge.get("source", "")) not in all_ids or str(edge.get("target", "")) not in all_ids:
            raise ValueError(f"New edge has missing endpoint: {edge}")
        normalized_edges.append(edge)

    normalized_hyperedges = []
    for hyperedge in new_hyperedges:
        hyperedge = dict(hyperedge)
        if "nodes" not in hyperedge and "members" in hyperedge:
            hyperedge["nodes"] = hyperedge.pop("members")
        members = [str(member) for member in hyperedge.get("nodes", [])]
        if len(members) < 2 or len(members) != len(set(members)) or any(member not in all_ids for member in members):
            raise ValueError(f"New hyperedge has invalid members: {hyperedge}")
        normalized_hyperedges.append(hyperedge)

    by_family = {"nodes": new_nodes, "edges": normalized_edges, "hyperedges": normalized_hyperedges}
    touched: set[int] = set()
    source_files: set[str] = set()
    for family, records in by_family.items():
        for record in records:
            source_file = record.get("source_file")
            if not isinstance(source_file, str):
                raise ValueError(f"Missing source_file in {family}: {record}")
            key = norm(source_file)
            source_files.add(key)
            number = file_to_chunk.get(key)
            if number is None:
                raise ValueError(f"Addition source is absent from the new plan: {source_file}")
            chunks[number][1].setdefault(family, []).append(record)
            touched.add(number)

    for number in sorted(touched):
        path, payload = chunks[number]
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    evidence = {
        "schema_version": "TSIS_GRAPHIFY_SEMANTIC_ADDITIONS_MERGE_v0_1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "plan": str(args.plan),
        "additions": str(args.additions),
        "source_files": sorted(source_files),
        "counts": {family: len(records) for family, records in by_family.items()},
        "touched_chunks": sorted(touched),
    }
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"sources={len(source_files)} counts={evidence['counts']} chunks={sorted(touched)} status=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
