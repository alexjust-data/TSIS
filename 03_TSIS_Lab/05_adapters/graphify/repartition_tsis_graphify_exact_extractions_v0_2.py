from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FAMILIES = ("nodes", "edges", "hyperedges")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def normalized(path: str) -> str:
    return str(Path(path)).replace("\\", "/").casefold()


def corpus_records(path: Path) -> dict[str, dict[str, Any]]:
    payload = load_json(path)
    if not isinstance(payload, list):
        raise ValueError(f"Corpus manifest is not a list: {path}")
    records: dict[str, dict[str, Any]] = {}
    for record in payload:
        if not isinstance(record, dict):
            raise ValueError(f"Non-object corpus record: {path}")
        absolute_path = record.get("absolute_path")
        digest = record.get("sha256")
        if not isinstance(absolute_path, str) or not isinstance(digest, str):
            raise ValueError(f"Missing absolute_path/sha256: {path}")
        key = normalized(absolute_path)
        if key in records:
            raise ValueError(f"Duplicate corpus path: {absolute_path}")
        records[key] = record
    return records


def canonical_fingerprint(record: dict[str, Any]) -> str:
    encoded = json.dumps(
        record, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_extractions(plan: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    output = {family: [] for family in FAMILIES}
    for chunk in plan["chunks"]:
        path = Path(chunk["output_path"])
        payload = load_json(path)
        if not isinstance(payload, dict):
            raise ValueError(f"Extraction is not an object: {path}")
        for family in FAMILIES:
            records = payload.get(family, [])
            if not isinstance(records, list) or not all(
                isinstance(record, dict) for record in records
            ):
                raise ValueError(f"Invalid {family} in {path}")
            output[family].extend(records)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-plan", type=Path, required=True)
    parser.add_argument("--new-plan", type=Path, required=True)
    parser.add_argument("--old-manifest", type=Path, required=True)
    parser.add_argument("--new-manifest", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--allow-removed-suffix", action="append", default=[])
    parser.add_argument("--allow-added-suffix", action="append", default=[])
    args = parser.parse_args()

    old_plan = load_json(args.old_plan)
    new_plan = load_json(args.new_plan)
    old_corpus = corpus_records(args.old_manifest)
    new_corpus = corpus_records(args.new_manifest)

    old_paths = set(old_corpus)
    new_paths = set(new_corpus)
    added_paths = sorted(new_paths - old_paths)
    removed_paths = sorted(old_paths - new_paths)
    changed_paths = sorted(
        path
        for path in old_paths & new_paths
        if old_corpus[path]["sha256"] != new_corpus[path]["sha256"]
    )
    allowed_removed_suffixes = [
        value.replace("\\", "/").casefold().lstrip("/")
        for value in args.allow_removed_suffix
    ]
    allowed_added_suffixes = [
        value.replace("\\", "/").casefold().lstrip("/")
        for value in args.allow_added_suffix
    ]
    unauthorized_additions = [
        path
        for path in added_paths
        if not any(path.endswith(suffix) for suffix in allowed_added_suffixes)
    ]
    unauthorized_removals = [
        path
        for path in removed_paths
        if not path.endswith("/graphify_refresh_queue.md")
        and not any(path.endswith(suffix) for suffix in allowed_removed_suffixes)
    ]
    if unauthorized_additions or changed_paths or unauthorized_removals or not removed_paths:
        raise ValueError(
            "Delta contains an unauthorized corpus change: "
            f"added={added_paths}, unauthorized_added={unauthorized_additions}, changed={changed_paths}, "
            f"unauthorized_removed={unauthorized_removals}, removed={removed_paths}"
        )

    file_to_chunk: dict[str, dict[str, Any]] = {}
    for chunk in new_plan["chunks"]:
        for file_path in chunk["files"]:
            key = normalized(file_path)
            if key in file_to_chunk:
                raise ValueError(f"New file occurs in multiple chunks: {file_path}")
            if key not in new_corpus:
                raise ValueError(f"New chunk file absent from corpus: {file_path}")
            file_to_chunk[key] = chunk

    old_records = load_extractions(old_plan)
    output_by_chunk: dict[int, dict[str, list[dict[str, Any]]]] = {
        int(chunk["chunk_num"]): {family: [] for family in FAMILIES}
        for chunk in new_plan["chunks"]
    }
    removed_counts = Counter()
    written_counts = Counter()
    expected_fingerprints = {family: Counter() for family in FAMILIES}
    written_fingerprints = {family: Counter() for family in FAMILIES}

    for family in FAMILIES:
        for record in old_records[family]:
            source_file = record.get("source_file")
            if not isinstance(source_file, str):
                raise ValueError(f"Missing source_file in {family}: {record}")
            source_key = normalized(source_file)
            if source_key not in old_corpus:
                raise ValueError(f"Extraction source absent from old corpus: {source_file}")
            if source_key in removed_paths:
                removed_counts[family] += 1
                continue
            expected_fingerprints[family][canonical_fingerprint(record)] += 1
            chunk = file_to_chunk.get(source_key)
            if chunk is None:
                raise ValueError(f"Preserved source absent from new chunks: {source_file}")
            output_by_chunk[int(chunk["chunk_num"])][family].append(record)
            written_counts[family] += 1
            written_fingerprints[family][canonical_fingerprint(record)] += 1

    if expected_fingerprints != written_fingerprints:
        raise ValueError("Record fingerprint conservation failed")

    for chunk in new_plan["chunks"]:
        chunk_num = int(chunk["chunk_num"])
        destination = Path(chunk["output_path"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(output_by_chunk[chunk_num], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    evidence = {
        "schema_version": "TSIS_GRAPHIFY_EXACT_EXTRACTION_REPARTITION_v0_2",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "old_plan": str(args.old_plan),
        "new_plan": str(args.new_plan),
        "old_manifest": str(args.old_manifest),
        "new_manifest": str(args.new_manifest),
        "old_corpus_files": len(old_corpus),
        "new_corpus_files": len(new_corpus),
        "added_paths": added_paths,
        "changed_paths": changed_paths,
        "allowed_removed_suffixes": allowed_removed_suffixes,
        "allowed_added_suffixes": allowed_added_suffixes,
        "removed_paths": removed_paths,
        "old_record_counts": {
            family: len(old_records[family]) for family in FAMILIES
        },
        "removed_record_counts": dict(removed_counts),
        "written_record_counts": dict(written_counts),
        "record_fingerprint_conservation": "PASS",
        "new_chunks": len(new_plan["chunks"]),
    }
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"old_files={len(old_corpus)}",
        f"new_files={len(new_corpus)}",
        f"removed_queues={len(removed_paths)}",
        f"chunks={len(new_plan['chunks'])}",
    )
    print("old_records", {family: len(old_records[family]) for family in FAMILIES})
    print("removed_records", dict(removed_counts))
    print("written_records", dict(written_counts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
