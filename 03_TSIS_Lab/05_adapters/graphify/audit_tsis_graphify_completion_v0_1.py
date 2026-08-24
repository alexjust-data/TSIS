from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_LEAF_FILES = (
    ".graphify_root",
    "BUILD_MANIFEST.md",
    "corpus_manifest.json",
    "graph.html",
    "graph.json",
    "GRAPH_DIAGNOSTIC.json",
    "GRAPH_DIAGNOSTIC.md",
    "GRAPH_REPORT.md",
    "manifest.json",
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def graph_checks(path: Path) -> dict:
    graph = load(path)
    nodes = graph.get("nodes", [])
    links = graph.get("links", [])
    hyperedges = graph.get("hyperedges", [])
    ids = [str(node.get("id", "")) for node in nodes]
    id_set = set(ids)
    dangling = [
        index
        for index, edge in enumerate(links)
        if str(edge.get("source", "")) not in id_set or str(edge.get("target", "")) not in id_set
    ]
    invalid_hyperedges = []
    for index, hyperedge in enumerate(hyperedges):
        members = [str(member) for member in hyperedge.get("nodes", hyperedge.get("members", []))]
        if len(members) < 2 or len(members) != len(set(members)) or any(member not in id_set for member in members):
            invalid_hyperedges.append(index)
    return {
        "nodes": len(nodes),
        "edges": len(links),
        "hyperedges": len(hyperedges),
        "communities": len({str(node.get("community", "")) for node in nodes}),
        "empty_node_ids": sum(not value for value in ids),
        "duplicate_node_ids": len(ids) - len(id_set),
        "dangling_edges": len(dangling),
        "invalid_hyperedges": len(invalid_hyperedges),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Terminal completion audit for the governed TSIS Graphify refresh.")
    parser.add_argument("--tsis-plan", required=True, type=Path)
    parser.add_argument("--foundation-plan", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    repo_root = Path(r"C:\TSIS_Data")
    targets = [*load(args.tsis_plan)["targets"], *load(args.foundation_plan)["targets"]]
    publish_dirs = [Path(target["publish_dir"]) for target in targets]
    duplicate_publish_dirs = len(publish_dirs) - len({str(path).casefold() for path in publish_dirs})
    leaf_results = []
    for target, publish_dir in zip(targets, publish_dirs):
        missing = [name for name in REQUIRED_LEAF_FILES if not (publish_dir / name).is_file()]
        marker = (publish_dir / ".graphify_root").read_text(encoding="utf-8-sig").strip() if not missing else ""
        manifest_text = (publish_dir / "BUILD_MANIFEST.md").read_text(encoding="utf-8-sig") if not missing else ""
        checks = graph_checks(publish_dir / "graph.json") if not missing else {}
        accepted = "- status: ACCEPTED" in manifest_text
        graph_pass = bool(checks) and all(
            checks[key] == 0
            for key in ("empty_node_ids", "duplicate_node_ids", "dangling_edges", "invalid_hyperedges")
        )
        leaf_results.append(
            {
                "target_id": target["target_id"],
                "publish_dir": str(publish_dir),
                "missing_files": missing,
                "graphify_root": marker,
                "root_marker_pass": marker.casefold() == str(repo_root).casefold(),
                "accepted_manifest": accepted,
                "graph_checks": checks,
                "status": "PASS" if not missing and marker.casefold() == str(repo_root).casefold() and accepted and graph_pass else "FAIL",
            }
        )

    roots = [
        repo_root / "graphify-out",
        repo_root / "00_CTO" / "graphify-out",
        repo_root / "00_CTO_APPLIED_ARCHITECTURE" / "graphify-out",
        repo_root / "01_TSIS_DATA_FOUNDATION" / "01_foundations" / "graphify-out",
        repo_root / "02_TSIS_BACKTEST_ENGINE" / "graphify-out",
    ]
    root_results = []
    marker = "TSIS_GRAPHIFY_TERMINAL_ACCEPTANCE_20260822_FINAL"
    for root in roots:
        stderr = root / "GRAPH_DIAGNOSTIC_TERMINAL_20260822.stderr.log"
        manifest = root / "BUILD_MANIFEST.md"
        checks = graph_checks(root / "graph.json")
        result = {
            "root": str(root),
            "terminal_diagnostic_present": (root / "GRAPH_DIAGNOSTIC_TERMINAL_20260822.json").is_file(),
            "terminal_stderr_bytes": stderr.stat().st_size if stderr.is_file() else -1,
            "acceptance_marker": marker in manifest.read_text(encoding="utf-8-sig") if manifest.is_file() else False,
            "graph_checks": checks,
        }
        result["status"] = "PASS" if (
            result["terminal_diagnostic_present"]
            and result["terminal_stderr_bytes"] == 0
            and result["acceptance_marker"]
            and all(checks[key] == 0 for key in ("empty_node_ids", "duplicate_node_ids", "dangling_edges", "invalid_hyperedges"))
        ) else "FAIL"
        root_results.append(result)

    queues = [
        repo_root / "GRAPHIFY_REFRESH_QUEUE.md",
        repo_root / "00_CTO" / "GRAPHIFY_REFRESH_QUEUE.md",
        repo_root / "00_CTO_APPLIED_ARCHITECTURE" / "GRAPHIFY_REFRESH_QUEUE.md",
        repo_root / "02_TSIS_BACKTEST_ENGINE" / "GRAPHIFY_REFRESH_QUEUE.md",
        repo_root / "01_TSIS_DATA_FOUNDATION" / "01_foundations" / "module_contracts" / "core_market_raw_alignment_audit" / "GRAPHIFY_REFRESH_QUEUE.md",
    ]
    queue_marker = "TSIS_GRAPHIFY_QUEUE_CORPUS_EXCLUSION_ACCEPTED_20260822"
    queue_results = {
        str(path): path.is_file() and queue_marker in path.read_text(encoding="utf-8-sig") for path in queues
    }
    terminal_audit = load(repo_root / "runs" / "graphify_refresh" / "GRAPHIFY_TERMINAL_AUDIT_20260822.json")
    source_audit = load(repo_root / "runs" / "graphify_refresh" / "GRAPHIFY_SOURCE_COVERAGE_AUDIT_20260822.json")
    terminal_pass = terminal_audit.get("status") == "PASS"
    source_pass = source_audit.get("status") == "PASS"
    overall = (
        len(targets) == 16
        and duplicate_publish_dirs == 0
        and all(item["status"] == "PASS" for item in leaf_results)
        and all(item["status"] == "PASS" for item in root_results)
        and all(queue_results.values())
        and terminal_pass
        and source_pass
    )
    payload = {
        "schema_version": "TSIS_GRAPHIFY_COMPLETION_AUDIT_v0_1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if overall else "FAIL",
        "configured_target_count": len(targets),
        "duplicate_publish_dir_count": duplicate_publish_dirs,
        "leaf_results": leaf_results,
        "root_results": root_results,
        "queue_marker_results": queue_results,
        "terminal_audit_pass": terminal_pass,
        "source_coverage_audit_pass": source_pass,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"status={payload['status']} targets={len(targets)} "
        f"leaf_pass={sum(item['status'] == 'PASS' for item in leaf_results)} "
        f"root_pass={sum(item['status'] == 'PASS' for item in root_results)} "
        f"queue_markers={sum(queue_results.values())}/{len(queue_results)}"
    )
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
