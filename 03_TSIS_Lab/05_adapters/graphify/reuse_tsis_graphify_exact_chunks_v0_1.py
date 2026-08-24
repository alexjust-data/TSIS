from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def normalized(path: str) -> str:
    return str(Path(path)).replace("\\", "/").casefold()


def manifest_hashes(path: Path) -> dict[str, str]:
    payload = load_json(path)
    if not isinstance(payload, list):
        raise ValueError(f"Corpus manifest is not a list: {path}")
    hashes: dict[str, str] = {}
    for record in payload:
        if not isinstance(record, dict):
            raise ValueError(f"Non-object corpus record: {path}")
        absolute_path = record.get("absolute_path")
        digest = record.get("sha256")
        if not isinstance(absolute_path, str) or not isinstance(digest, str):
            raise ValueError(f"Missing absolute_path/sha256: {path}")
        key = normalized(absolute_path)
        if key in hashes:
            raise ValueError(f"Duplicate corpus path: {absolute_path}")
        hashes[key] = digest
    return hashes


def chunk_signature(chunk: dict[str, Any], hashes: dict[str, str]) -> tuple[tuple[str, str], ...]:
    files = chunk.get("files")
    if not isinstance(files, list) or not all(isinstance(value, str) for value in files):
        raise ValueError(f"Invalid chunk files: {chunk.get('chunk_num')}")
    signature: list[tuple[str, str]] = []
    for file_path in files:
        key = normalized(file_path)
        if key not in hashes:
            raise ValueError(f"Chunk file absent from corpus manifest: {file_path}")
        signature.append((key, hashes[key]))
    return tuple(signature)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-plan", type=Path, required=True)
    parser.add_argument("--new-plan", type=Path, required=True)
    parser.add_argument("--old-manifest", type=Path, required=True)
    parser.add_argument("--new-manifest", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    old_plan = load_json(args.old_plan)
    new_plan = load_json(args.new_plan)
    old_hashes = manifest_hashes(args.old_manifest)
    new_hashes = manifest_hashes(args.new_manifest)

    old_by_signature: dict[tuple[tuple[str, str], ...], dict[str, Any]] = {}
    for chunk in old_plan["chunks"]:
        signature = chunk_signature(chunk, old_hashes)
        if signature in old_by_signature:
            raise ValueError("Ambiguous duplicate chunk signature in old plan")
        old_by_signature[signature] = chunk

    reused: list[dict[str, Any]] = []
    unmatched: list[dict[str, Any]] = []
    for chunk in new_plan["chunks"]:
        signature = chunk_signature(chunk, new_hashes)
        old_chunk = old_by_signature.get(signature)
        if old_chunk is None:
            unmatched.append(
                {
                    "new_chunk_num": chunk["chunk_num"],
                    "files": chunk["files"],
                }
            )
            continue
        source = Path(old_chunk["output_path"])
        destination = Path(chunk["output_path"])
        if not source.is_file():
            raise FileNotFoundError(f"Missing old extraction: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        reused.append(
            {
                "old_chunk_num": old_chunk["chunk_num"],
                "new_chunk_num": chunk["chunk_num"],
                "files": len(chunk["files"]),
                "source": str(source),
                "destination": str(destination),
            }
        )

    evidence = {
        "schema_version": "TSIS_GRAPHIFY_EXACT_CHUNK_REUSE_v0_1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "old_plan": str(args.old_plan),
        "new_plan": str(args.new_plan),
        "old_manifest": str(args.old_manifest),
        "new_manifest": str(args.new_manifest),
        "old_chunks": len(old_plan["chunks"]),
        "new_chunks": len(new_plan["chunks"]),
        "reused_chunks": len(reused),
        "unmatched_chunks": len(unmatched),
        "reused": reused,
        "unmatched": unmatched,
    }
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"new_chunks={len(new_plan['chunks'])}",
        f"reused={len(reused)}",
        f"unmatched={len(unmatched)}",
    )
    print("unmatched_chunk_nums", [item["new_chunk_num"] for item in unmatched])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
