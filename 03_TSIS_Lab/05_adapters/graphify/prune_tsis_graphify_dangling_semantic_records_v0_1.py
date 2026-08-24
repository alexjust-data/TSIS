from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prune semantic edges and hyperedge members whose endpoints were deliberately removed."
    )
    parser.add_argument("--chunks-dir", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()

    chunk_paths = sorted(args.chunks_dir.glob("chunk_*.json"))
    if not chunk_paths:
        raise FileNotFoundError(f"No chunk_*.json files in {args.chunks_dir}")

    chunks: list[tuple[Path, dict]] = []
    node_ids: set[str] = set()
    for path in chunk_paths:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        chunks.append((path, payload))
        node_ids.update(str(node["id"]) for node in payload.get("nodes", []))

    removed_edges: list[dict] = []
    removed_members: list[dict] = []
    removed_hyperedges: list[dict] = []
    changed_chunks: list[str] = []

    for path, payload in chunks:
        original_edges = payload.get("edges", [])
        kept_edges = []
        for edge in original_edges:
            source = str(edge.get("source", ""))
            target = str(edge.get("target", ""))
            if source in node_ids and target in node_ids:
                kept_edges.append(edge)
            else:
                removed_edges.append({"chunk": path.name, "edge": edge})

        kept_hyperedges = []
        hyperedges_changed = False
        for hyperedge in payload.get("hyperedges", []):
            member_field = "members" if "members" in hyperedge else "nodes" if "nodes" in hyperedge else None
            if member_field is None:
                removed_hyperedges.append({"chunk": path.name, "hyperedge": hyperedge})
                hyperedges_changed = True
                continue
            original_members = [str(member) for member in hyperedge.get(member_field, [])]
            seen: set[str] = set()
            valid_members: list[str] = []
            for member in original_members:
                if member in node_ids and member not in seen:
                    valid_members.append(member)
                    seen.add(member)
                elif member not in node_ids:
                    removed_members.append(
                        {"chunk": path.name, "hyperedge_id": hyperedge.get("id"), "member": member}
                    )
            if len(valid_members) < 2:
                removed_hyperedges.append({"chunk": path.name, "hyperedge": hyperedge})
                hyperedges_changed = True
                continue
            if valid_members != original_members:
                hyperedge = dict(hyperedge)
                hyperedge[member_field] = valid_members
                hyperedges_changed = True
            kept_hyperedges.append(hyperedge)

        if len(kept_edges) != len(original_edges) or hyperedges_changed:
            payload["edges"] = kept_edges
            payload["hyperedges"] = kept_hyperedges
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            changed_chunks.append(path.name)

    remaining_dangling_edges = 0
    remaining_invalid_members = 0
    for _, payload in chunks:
        remaining_dangling_edges += sum(
            1
            for edge in payload.get("edges", [])
            if str(edge.get("source", "")) not in node_ids
            or str(edge.get("target", "")) not in node_ids
        )
        remaining_invalid_members += sum(
            1
            for hyperedge in payload.get("hyperedges", [])
            for member in hyperedge.get("members", hyperedge.get("nodes", []))
            if str(member) not in node_ids
        )

    evidence = {
        "schema_version": "tsis.graphify_semantic_prune.v0_1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "chunks_dir": str(args.chunks_dir),
        "chunk_count": len(chunk_paths),
        "node_id_count": len(node_ids),
        "changed_chunks": changed_chunks,
        "removed_edge_count": len(removed_edges),
        "removed_hyperedge_member_count": len(removed_members),
        "removed_hyperedge_count": len(removed_hyperedges),
        "removed_edges": removed_edges,
        "removed_hyperedge_members": removed_members,
        "removed_hyperedges": removed_hyperedges,
        "remaining_dangling_edge_count": remaining_dangling_edges,
        "remaining_invalid_hyperedge_member_count": remaining_invalid_members,
        "status": "PASS" if remaining_dangling_edges == 0 and remaining_invalid_members == 0 else "FAIL",
    }
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"chunks={len(chunk_paths)} changed={len(changed_chunks)} "
        f"removed_edges={len(removed_edges)} removed_members={len(removed_members)} "
        f"removed_hyperedges={len(removed_hyperedges)} status={evidence['status']}"
    )
    return 0 if evidence["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
