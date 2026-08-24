from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


GRAPH_ROOTS = (
    ("tsis_root", Path(r"C:\TSIS_Data\graphify-out")),
    ("cto", Path(r"C:\TSIS_Data\00_CTO\graphify-out")),
    (
        "applied_architecture",
        Path(r"C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\graphify-out"),
    ),
    (
        "data_foundation",
        Path(
            r"C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\graphify-out"
        ),
    ),
    ("backtest_engine", Path(r"C:\TSIS_Data\02_TSIS_BACKTEST_ENGINE\graphify-out")),
)

FORBIDDEN_SOURCE_PATH_FRAGMENTS = (
    "01_tsis_backtest_smallcaps",
    "e:/tsis/data",
    "06_tsis_trading_voice",
)

SOURCE_PATH_KEYS = {
    "source_file",
    "source_path",
    "file_path",
    "corpus_file",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def as_records(payload: dict[str, Any], key: str) -> list[Any]:
    records = payload.get(key)
    if isinstance(records, list):
        return records
    graph_metadata = payload.get("graph")
    if isinstance(graph_metadata, dict):
        records = graph_metadata.get(key)
        if isinstance(records, list):
            return records
    return []


def endpoint_id(value: Any) -> str | None:
    if isinstance(value, (str, int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, dict):
        for key in ("id", "node_id"):
            candidate = value.get(key)
            if isinstance(candidate, (str, int, float)) and not isinstance(candidate, bool):
                return str(candidate)
    return None


def relationship(edge: dict[str, Any]) -> str:
    for key in ("relationship", "relation", "type", "label"):
        value = edge.get(key)
        if isinstance(value, str):
            return value
    return ""


def permits_external_endpoint(edge: dict[str, Any]) -> bool:
    relation = relationship(edge).casefold()
    return "import" in relation or "depend" in relation


def hyperedge_members(hyperedge: dict[str, Any]) -> list[Any]:
    for key in ("members", "nodes", "node_ids", "participants"):
        value = hyperedge.get(key)
        if isinstance(value, list):
            return value
    return []


def collect_source_paths(value: Any, output: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.casefold() in SOURCE_PATH_KEYS and isinstance(child, str):
                output.append(child)
            else:
                collect_source_paths(child, output)
    elif isinstance(value, list):
        for child in value:
            collect_source_paths(child, output)


def artifact_state(root: Path) -> dict[str, Any]:
    report_candidates = (
        root / "GRAPH_REPORT.md",
        root / "report.md",
        root / "REPORT.md",
    )
    html_candidates = (root / "graph.html", root / "GRAPH.html")
    artifacts = {
        "graph_json": (root / "graph.json").is_file(),
        "report_md": any(path.is_file() for path in report_candidates),
        "graph_html": any(path.is_file() for path in html_candidates),
        "build_manifest": (root / "BUILD_MANIFEST.md").is_file(),
        "official_diagnostic_json": (
            root / "GRAPH_DIAGNOSTIC_TERMINAL_20260822.json"
        ).is_file(),
        "official_diagnostic_stderr": (
            root / "GRAPH_DIAGNOSTIC_TERMINAL_20260822.stderr.log"
        ).is_file(),
    }
    artifacts["missing"] = [key for key, present in artifacts.items() if present is False]
    return artifacts


def audit_graph(graph_id: str, root: Path) -> dict[str, Any]:
    graph_path = root / "graph.json"
    payload = load_json(graph_path)
    if not isinstance(payload, dict):
        raise ValueError(f"Graph payload is not an object: {graph_path}")

    nodes = as_records(payload, "nodes")
    edges = as_records(payload, "edges") or as_records(payload, "links")
    hyperedges = as_records(payload, "hyperedges")

    node_ids: list[str] = []
    invalid_node_records = 0
    for node in nodes:
        if not isinstance(node, dict):
            invalid_node_records += 1
            continue
        node_id = endpoint_id(node.get("id"))
        if node_id is None:
            invalid_node_records += 1
            continue
        node_ids.append(node_id)
    node_id_set = set(node_ids)
    duplicate_node_ids = sorted(
        node_id for node_id, count in Counter(node_ids).items() if count > 1
    )

    invalid_edge_records = 0
    missing_edge_endpoints = 0
    permitted_external_edge_endpoints = 0
    hard_missing_edge_endpoints = 0
    self_loops = 0
    hard_missing_examples: list[dict[str, Any]] = []
    for edge in edges:
        if not isinstance(edge, dict):
            invalid_edge_records += 1
            continue
        source = endpoint_id(edge.get("source"))
        target = endpoint_id(edge.get("target"))
        if source is None or target is None:
            invalid_edge_records += 1
            continue
        if source == target:
            self_loops += 1
        missing = int(source not in node_id_set) + int(target not in node_id_set)
        if not missing:
            continue
        missing_edge_endpoints += missing
        if permits_external_endpoint(edge):
            permitted_external_edge_endpoints += missing
        else:
            hard_missing_edge_endpoints += missing
            if len(hard_missing_examples) < 20:
                hard_missing_examples.append(
                    {
                        "source": source,
                        "target": target,
                        "relationship": relationship(edge),
                    }
                )

    invalid_hyperedge_records = 0
    invalid_hyperedge_members = 0
    invalid_hyperedge_examples: list[dict[str, Any]] = []
    hyperedge_ids: list[str] = []
    missing_hyperedge_ids = 0
    for ordinal, hyperedge in enumerate(hyperedges):
        if not isinstance(hyperedge, dict):
            invalid_hyperedge_records += 1
            continue
        hyperedge_id = endpoint_id(hyperedge.get("id"))
        if hyperedge_id is None:
            missing_hyperedge_ids += 1
        else:
            hyperedge_ids.append(hyperedge_id)
        for raw_member in hyperedge_members(hyperedge):
            member = endpoint_id(raw_member)
            if member is not None and member in node_id_set:
                continue
            invalid_hyperedge_members += 1
            if len(invalid_hyperedge_examples) < 20:
                invalid_hyperedge_examples.append(
                    {
                        "ordinal": ordinal,
                        "hyperedge_id": hyperedge_id,
                        "member": member,
                    }
                )
    duplicate_hyperedge_ids = sorted(
        hyperedge_id
        for hyperedge_id, count in Counter(hyperedge_ids).items()
        if count > 1
    )

    source_paths: list[str] = []
    collect_source_paths(payload, source_paths)
    forbidden_source_paths: list[dict[str, str]] = []
    for source_path in source_paths:
        normalized = source_path.replace("\\", "/").casefold()
        for fragment in FORBIDDEN_SOURCE_PATH_FRAGMENTS:
            if fragment in normalized:
                forbidden_source_paths.append(
                    {"source_path": source_path, "forbidden_fragment": fragment}
                )

    official_path = root / "GRAPH_DIAGNOSTIC_TERMINAL_20260822.json"
    official_stderr = root / "GRAPH_DIAGNOSTIC_TERMINAL_20260822.stderr.log"
    official_diagnostic = load_json(official_path)
    official_stderr_bytes = official_stderr.stat().st_size
    artifacts = artifact_state(root)

    hard_failures = {
        "invalid_node_records": invalid_node_records,
        "duplicate_node_ids": len(duplicate_node_ids),
        "invalid_edge_records": invalid_edge_records,
        "hard_missing_edge_endpoints": hard_missing_edge_endpoints,
        "self_loops": self_loops,
        "invalid_hyperedge_records": invalid_hyperedge_records,
        "missing_hyperedge_ids": missing_hyperedge_ids,
        "duplicate_hyperedge_ids": len(duplicate_hyperedge_ids),
        "invalid_hyperedge_members": invalid_hyperedge_members,
        "forbidden_source_paths": len(forbidden_source_paths),
        "missing_artifacts": len(artifacts["missing"]),
        "official_diagnostic_stderr_bytes": official_stderr_bytes,
    }
    status = "PASS" if not any(hard_failures.values()) else "FAIL"
    return {
        "graph_id": graph_id,
        "root": str(root),
        "status": status,
        "counts": {
            "nodes": len(nodes),
            "unique_node_ids": len(node_id_set),
            "edges": len(edges),
            "hyperedges": len(hyperedges),
            "source_paths_checked": len(source_paths),
            "missing_edge_endpoints_raw": missing_edge_endpoints,
            "permitted_external_edge_endpoints": permitted_external_edge_endpoints,
        },
        "hard_failures": hard_failures,
        "duplicate_node_ids": duplicate_node_ids[:20],
        "hard_missing_edge_examples": hard_missing_examples,
        "duplicate_hyperedge_ids": duplicate_hyperedge_ids[:20],
        "invalid_hyperedge_examples": invalid_hyperedge_examples,
        "forbidden_source_path_examples": forbidden_source_paths[:20],
        "artifacts": artifacts,
        "official_multigraph_diagnostic": official_diagnostic,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            r"C:\TSIS_Data\runs\graphify_refresh\GRAPHIFY_TERMINAL_AUDIT_20260822.json"
        ),
    )
    args = parser.parse_args()

    reports = [audit_graph(graph_id, root) for graph_id, root in GRAPH_ROOTS]
    payload = {
        "schema_version": "TSIS_GRAPHIFY_TERMINAL_AUDIT_v0_1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all(report["status"] == "PASS" for report in reports) else "FAIL",
        "graphs": reports,
    }
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")
    for report in reports:
        root = Path(report["root"])
        (root / "GRAPHIFY_TERMINAL_AUDIT_20260822.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        counts = report["counts"]
        print(
            report["graph_id"],
            report["status"],
            f"nodes={counts['nodes']}",
            f"edges={counts['edges']}",
            f"hyperedges={counts['hyperedges']}",
            f"external_missing={counts['permitted_external_edge_endpoints']}",
        )
    print("overall", payload["status"], args.output)
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
