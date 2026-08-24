#!/usr/bin/env python
"""Governed official Graphify composition for accepted TSIS leaf graphs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import networkx as nx
from networkx.readwrite import json_graph

from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.cluster import cluster, score_all
from graphify.export import to_html, to_json
from graphify.report import generate

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PLAN = SCRIPT_DIR / "tsis_graphify_refresh_plan_v0_1.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def group_for(plan: dict, group_id: str) -> dict:
    return next(g for g in plan["merge_groups"] if g["group_id"] == group_id)


def target_for(plan: dict, target_id: str) -> dict:
    return next(t for t in plan["targets"] if t["target_id"] == target_id)


def run_paths(plan: dict, group: dict, run_id: str) -> tuple[Path, Path, Path]:
    root = Path(plan["run_base"]) / run_id / group["group_id"]
    return root, root / "staging" / "graphify-out", root / "monitor"


def heartbeat(monitor: Path, **values: object) -> None:
    payload = {"observed_at_utc": now(), "pid": os.getpid(), **values}
    write_json(monitor / "heartbeat_latest.json", payload)
    with (monitor / "heartbeat.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def inputs(plan: dict, group: dict) -> list[Path]:
    result = [Path(p) for p in group.get("input_graphs", [])]
    result.extend(Path(target_for(plan, t)["publish_dir"]) / "graph.json" for t in group.get("input_targets", []))
    return result


def load_graph(path: Path) -> nx.Graph:
    data = read_json(path)
    try:
        return json_graph.node_link_graph(data, edges="links")
    except TypeError:
        return json_graph.node_link_graph(data)


def _hyperedge_members(hyperedge: dict) -> tuple[str, list[str]]:
    if isinstance(hyperedge.get("nodes"), list):
        return "nodes", [str(value) for value in hyperedge["nodes"]]
    if isinstance(hyperedge.get("members"), list):
        return "members", [str(value) for value in hyperedge["members"]]
    return "nodes", []


def _graph_hyperedges(data: dict) -> list[dict]:
    top_level = data.get("hyperedges")
    nested = data.get("graph", {}).get("hyperedges") if isinstance(data.get("graph"), dict) else None
    if isinstance(top_level, list) and top_level:
        return top_level
    if isinstance(nested, list) and nested:
        return nested
    return top_level if isinstance(top_level, list) else []


def repair_merged_hyperedge_namespaces(
    merged_path: Path,
    graph_paths: list[Path],
    audit_path: Path,
) -> dict:
    """Compose every input hyperedge with exact merge namespaces, or fail closed."""
    merged = read_json(merged_path)
    merged_nodes = [node for node in merged.get("nodes", []) if node.get("id")]
    merged_ids = {str(node["id"]) for node in merged_nodes}
    suffix_index: dict[str, list[str]] = defaultdict(list)
    for node_id in sorted(merged_ids):
        parts = node_id.split("::")
        for offset in range(len(parts)):
            suffix_index["::".join(parts[offset:])].append(node_id)

    input_records: list[dict] = []
    composed_hyperedges: list[dict] = []
    repaired_members = 0
    unresolved: list[dict] = []
    ambiguous: list[dict] = []
    duplicate_hyperedge_ids: list[str] = []
    generated_hyperedge_ids: list[dict] = []
    seen_hyperedge_ids: set[str] = set()
    merged_before = _graph_hyperedges(merged)

    for input_index, graph_path in enumerate(graph_paths, start=1):
        source = read_json(graph_path)
        prefix_counts: Counter[str] = Counter()
        for node in source.get("nodes", []):
            original_id = str(node.get("id", ""))
            if not original_id:
                continue
            for candidate in suffix_index.get(original_id, []):
                marker = "::" + original_id
                if candidate.endswith(marker):
                    prefix_counts[candidate[: -len(marker)]] += 1
        if not prefix_counts:
            raise RuntimeError(f"Cannot infer merge namespace for input graph: {graph_path}")
        ranked = prefix_counts.most_common()
        if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
            raise RuntimeError(
                f"Ambiguous merge namespace for input graph {graph_path}: {ranked[:3]}"
            )
        prefix = ranked[0][0]
        source_hyperedges = _graph_hyperedges(source)
        input_records.append(
            {
                "input_index": input_index,
                "path": str(graph_path),
                "namespace": prefix,
                "namespace_evidence_nodes": ranked[0][1],
                "source_hyperedges": len(source_hyperedges),
            }
        )

        for hyperedge_ordinal, source_hyperedge in enumerate(source_hyperedges):
            original_hyperedge_id = str(source_hyperedge.get("id", ""))
            if not original_hyperedge_id:
                identity_payload = json.dumps(
                    {
                        "input_graph": str(graph_path),
                        "ordinal": hyperedge_ordinal,
                        "relation": source_hyperedge.get("relation"),
                        "nodes": _hyperedge_members(source_hyperedge)[1],
                        "source_file": source_hyperedge.get("source_file"),
                    },
                    sort_keys=True,
                    ensure_ascii=False,
                )
                original_hyperedge_id = (
                    "generated_" + hashlib.sha256(identity_payload.encode("utf-8")).hexdigest()[:24]
                )
                generated_hyperedge_ids.append(
                    {
                        "input_graph": str(graph_path),
                        "ordinal": hyperedge_ordinal,
                        "generated_id": original_hyperedge_id,
                    }
                )
            composed_id = f"{prefix}::{original_hyperedge_id}"
            if composed_id in seen_hyperedge_ids:
                duplicate_hyperedge_ids.append(composed_id)
                continue
            seen_hyperedge_ids.add(composed_id)
            _, members = _hyperedge_members(source_hyperedge)
            mapped_members: list[str] = []
            for member in members:
                expected = f"{prefix}::{member}"
                if expected in merged_ids:
                    mapped_members.append(expected)
                    repaired_members += 1
                    continue
                candidates = sorted(
                    candidate
                    for candidate in set(suffix_index.get(member, []))
                    if candidate.startswith(prefix + "::")
                )
                if len(candidates) == 1:
                    mapped_members.append(candidates[0])
                    repaired_members += 1
                elif not candidates:
                    unresolved.append(
                        {
                            "input_graph": str(graph_path),
                            "hyperedge_id": original_hyperedge_id,
                            "member": member,
                            "namespace": prefix,
                        }
                    )
                else:
                    ambiguous.append(
                        {
                            "input_graph": str(graph_path),
                            "hyperedge_id": original_hyperedge_id,
                            "member": member,
                            "namespace": prefix,
                            "candidates": candidates,
                        }
                    )
            composed = dict(source_hyperedge)
            composed["id"] = composed_id
            composed["nodes"] = mapped_members
            composed.pop("members", None)
            composed_hyperedges.append(composed)

    invalid_after: list[dict] = []
    for hyperedge in composed_hyperedges:
        _, members = _hyperedge_members(hyperedge)
        for member in members:
            if member not in merged_ids:
                invalid_after.append(
                    {"hyperedge_id": str(hyperedge.get("id", "")), "member": member}
                )
    expected_hyperedges = sum(record["source_hyperedges"] for record in input_records)
    status = "PASS"
    if (
        unresolved
        or ambiguous
        or invalid_after
        or duplicate_hyperedge_ids
        or len(composed_hyperedges) != expected_hyperedges
    ):
        status = "FAIL"
    audit = {
        "schema_version": "TSIS_GRAPHIFY_HYPEREDGE_NAMESPACE_REPAIR_v0_1",
        "status": status,
        "created_at_utc": now(),
        "merged_graph": str(merged_path),
        "input_graphs": input_records,
        "hyperedges_seen_in_raw_merge": len(merged_before),
        "expected_input_hyperedges": expected_hyperedges,
        "hyperedges": len(composed_hyperedges),
        "repaired_members": repaired_members,
        "affected_hyperedges": sorted(seen_hyperedge_ids),
        "duplicate_hyperedge_ids": sorted(set(duplicate_hyperedge_ids)),
        "generated_hyperedge_ids": generated_hyperedge_ids,
        "unresolved": unresolved,
        "ambiguous": ambiguous,
        "invalid_after": invalid_after,
    }
    write_json(audit_path, audit)
    if status != "PASS":
        raise RuntimeError(
            "Hyperedge namespace composition failed: "
            f"expected={expected_hyperedges} composed={len(composed_hyperedges)} "
            f"unresolved={len(unresolved)} ambiguous={len(ambiguous)} "
            f"duplicates={len(duplicate_hyperedge_ids)} invalid_after={len(invalid_after)}"
        )
    merged.setdefault("graph", {})["hyperedges"] = composed_hyperedges
    merged["hyperedges"] = composed_hyperedges
    write_json(merged_path, merged)
    return audit


def prepare(plan: dict, group: dict, run_id: str) -> int:
    run_root, output, monitor = run_paths(plan, group, run_id)
    output.mkdir(parents=True, exist_ok=True)
    graph_paths = inputs(plan, group)
    missing = [str(p) for p in graph_paths if not p.exists()]
    if missing:
        raise RuntimeError("Missing accepted leaf graphs:\n" + "\n".join(missing))
    pre = {"run_id": run_id, "group_id": group["group_id"], "status": "running", "created_at_utc": now(), "input_graphs": [str(p) for p in graph_paths], "publish_dir": group["publish_dir"], "merge_command": ["graphify", "merge-graphs", *map(str, graph_paths), "--out", str(output / "graph.json")]}
    write_json(monitor / "pre_manifest.json", pre)
    write_json(monitor / "pid_manifest.json", {"pid": os.getpid(), "phase": "prepare", "created_at_utc": now()})
    heartbeat(monitor, status="running", stage="official_merge", target_id=group["group_id"], detail=f"inputs={len(graph_paths)}")
    cmd = pre["merge_command"]
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    (run_root / "merge.log").write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(f"graphify merge-graphs failed with code {proc.returncode}")
    repair_merged_hyperedge_namespaces(
        output / "graph.json",
        graph_paths,
        run_root / "HYPEREDGE_NAMESPACE_REPAIR.json",
    )
    G = load_graph(output / "graph.json")
    communities = cluster(G)
    cohesion = score_all(G, communities)
    degree = dict(G.degree())
    write_json(output / ".graphify_analysis.json", {"communities": {str(k): v for k, v in communities.items()}, "cohesion": {str(k): v for k, v in cohesion.items()}})
    community_plan = []
    for cid, members in communities.items():
        ranked = sorted(members, key=lambda n: degree.get(n, 0), reverse=True)[:15]
        community_plan.append({"community_id": cid, "member_count": len(members), "cohesion": cohesion.get(cid), "top_nodes": [{"id": n, "label": G.nodes[n].get("label", n), "source_file": G.nodes[n].get("source_file")} for n in ranked]})
    write_json(run_root / "community_label_plan.json", {"group_id": group["group_id"], "instruction": "Assign one specific 2-5 word label per community.", "communities": community_plan, "output_path": str(run_root / "community_labels.json")})
    heartbeat(monitor, status="waiting_community_labels", stage="merge_complete", target_id=group["group_id"], nodes=G.number_of_nodes(), edges=G.number_of_edges(), detail=f"communities={len(communities)}")
    return 0


def publish(plan: dict, group: dict, run_id: str) -> int:
    run_root, output, monitor = run_paths(plan, group, run_id)
    labels = {int(k): str(v) for k, v in read_json(run_root / "community_labels.json").items()}
    analysis = read_json(output / ".graphify_analysis.json")
    communities = {int(k): v for k, v in analysis["communities"].items()}
    if set(labels) != set(communities):
        raise RuntimeError("Community label set does not match merged communities")
    G = load_graph(output / "graph.json")
    source_files = sorted({str(data.get("source_file")).replace("\\", "/") for _, data in G.nodes(data=True) if data.get("source_file")})
    source_text = "\n".join(source_files).lower()
    forbidden = [s for s in group.get("forbidden_source_substrings", []) if s.replace("\\", "/").lower() in source_text]
    if forbidden:
        raise RuntimeError(f"Forbidden legacy paths remain after merge: {forbidden}")
    cohesion = score_all(G, communities)
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    questions = suggest_questions(G, communities, labels)
    source_files = sorted({str(data.get("source_file")) for _, data in G.nodes(data=True) if data.get("source_file")})
    detection = {"scan_root": plan["repo_root"], "files": {"merged_sources": source_files}, "total_files": len(source_files), "total_words": 0, "skipped_sensitive": []}
    to_json(G, communities, str(output / "graph.json"), force=True, community_labels=labels)
    (output / "GRAPH_REPORT.md").write_text(generate(G, communities, cohesion, labels, gods, surprises, detection, {"input": 0, "output": 0}, plan["repo_root"], suggested_questions=questions), encoding="utf-8")
    to_html(G, communities, str(output / "graph.html"), community_labels=labels)
    write_json(output / ".graphify_labels.json", {str(k): v for k, v in labels.items()})
    diag_cmd = ["graphify", "diagnose", "multigraph", "--graph", str(output / "graph.json")]
    diag = subprocess.run(diag_cmd, text=True, capture_output=True, check=False)
    (output / "GRAPH_DIAGNOSTIC.md").write_text(diag.stdout + "\n" + diag.stderr, encoding="utf-8")
    if diag.returncode != 0:
        raise RuntimeError(f"Graphify multigraph diagnostic failed with code {diag.returncode}")
    if "dropping hyperedge" in diag.stderr.lower():
        raise RuntimeError("Graphify diagnostic dropped one or more hyperedges")
    repair = read_json(run_root / "HYPEREDGE_NAMESPACE_REPAIR.json")
    manifest = f"# Graphify Build Manifest\n\n- status: ACCEPTED\n- group_id: {group['group_id']}\n- built_at_utc: {now()}\n- input_graphs: {len(inputs(plan, group))}\n- source_files: {len(source_files)}\n- nodes: {G.number_of_nodes()}\n- edges: {G.number_of_edges()}\n- communities: {len(communities)}\n- merge_authority: graphify merge-graphs\n- hyperedge_namespace_repair_status: {repair['status']}\n- hyperedge_members_repaired: {repair['repaired_members']}\n"
    (output / "BUILD_MANIFEST.md").write_text(manifest, encoding="utf-8")
    destination = Path(group["publish_dir"])
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(run_root / "HYPEREDGE_NAMESPACE_REPAIR.json", output / "HYPEREDGE_NAMESPACE_REPAIR.json")
    for name in ["graph.json", "GRAPH_REPORT.md", "graph.html", ".graphify_labels.json", ".graphify_analysis.json", "GRAPH_DIAGNOSTIC.md", "BUILD_MANIFEST.md", "HYPEREDGE_NAMESPACE_REPAIR.json"]:
        src = output / name
        tmp = destination / (name + ".tmp")
        shutil.copy2(src, tmp)
        os.replace(tmp, destination / name)
    final = {**read_json(monitor / "pre_manifest.json"), "status": "complete", "finished_at_utc": now(), "nodes": G.number_of_nodes(), "edges": G.number_of_edges(), "communities": len(communities)}
    write_json(monitor / "final_manifest.json", final)
    heartbeat(monitor, status="complete", stage="published", target_id=group["group_id"], nodes=G.number_of_nodes(), edges=G.number_of_edges(), detail=group["publish_dir"])
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("phase", choices=["prepare", "publish"])
    ap.add_argument("--group-id", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--plan", default=str(DEFAULT_PLAN))
    args = ap.parse_args()
    plan = read_json(Path(args.plan))
    group = group_for(plan, args.group_id)
    run_root, _, monitor = run_paths(plan, group, args.run_id)
    try:
        return prepare(plan, group, args.run_id) if args.phase == "prepare" else publish(plan, group, args.run_id)
    except Exception as exc:
        heartbeat(monitor, status="failed", stage=args.phase, target_id=group["group_id"], detail=repr(exc))
        pre = read_json(monitor / "pre_manifest.json") if (monitor / "pre_manifest.json").exists() else {"run_id": args.run_id, "group_id": group["group_id"]}
        write_json(monitor / "final_manifest.json", {**pre, "status": "failed", "failed_at_utc": now(), "error": repr(exc)})
        raise


if __name__ == "__main__":
    raise SystemExit(main())

