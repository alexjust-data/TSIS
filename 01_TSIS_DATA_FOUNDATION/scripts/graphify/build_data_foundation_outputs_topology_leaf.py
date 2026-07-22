from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import importlib.metadata as importlib_metadata

from graphify.analyze import god_nodes, suggest_questions, surprising_connections
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.diagnostics import diagnose_extraction, format_diagnostic_report
from graphify.export import to_html, to_json
from graphify.report import generate


REPO_ROOT = Path(r"C:\TSIS_Data")
FOUNDATIONS_ROOT = REPO_ROOT / "01_TSIS_DATA_FOUNDATION" / "01_foundations"
LEAF_DIR = FOUNDATIONS_ROOT / "graphify-out" / "leaf_slices" / "data_foundation_outputs_topology_20260629"
OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs")

OUTPUT_TABLES = [
    "instrument_master",
    "market_calendar",
    "corporate_actions_table",
    "master_daily_table",
    "master_intraday_bar_table",
    "microstructure_features_table",
    "halts_table",
    "fundamentals_asof_table",
    "news_context_table",
    "short_context_table",
    "short_sale_constraints_table",
    "regime_context_table",
    "event_windows_table",
    "event_state_table",
    "market_state_table",
    "outcomes_table",
    "expected_data_calendar",
    "dataset_certification_matrix",
]

MODULE_CONTRACTS = [
    "01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md",
    "01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md",
    "01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md",
    "01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md",
    "01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/master_intraday_bar_table_wider_scope_materialization_plan_v0_1.md",
    "01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/microstructure_features_table_multi_window_materialization_plan_v0_1.md",
    "01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/short_sale_constraints_table_target_contract_v0_1.md",
    "01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/short_sale_constraints_data_acquisition_runbook_v0_1.md",
    "01_TSIS_DATA_FOUNDATION/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md",
    "01_TSIS_DATA_FOUNDATION/01_foundations/GRAPHIFY_REFRESH_QUEUE.md",
    "01_TSIS_DATA_FOUNDATION/CHANGELOG.md",
]


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    return result.stdout.strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_words(text: str) -> int:
    return len(re.findall(r"\b\S+\b", text))


def norm(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_") or "node"


def rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def node_id(kind: str, name: str) -> str:
    return f"data_foundation_outputs_{norm(kind)}_{norm(name)}"


def node(
    nodes: list[dict[str, Any]],
    kind: str,
    name: str,
    label: str,
    file_type: str,
    source_file: Path,
) -> str:
    nid = node_id(kind, name)
    nodes.append(
        {
            "id": nid,
            "label": label,
            "file_type": file_type,
            "source_file": str(source_file.resolve()),
            "source_location": None,
            "source_url": None,
            "captured_at": None,
            "author": None,
            "contributor": None,
        }
    )
    return nid


def edge(
    edges: list[dict[str, Any]],
    source: str,
    target: str,
    relation: str,
    source_file: Path,
    confidence: str = "EXTRACTED",
    score: float = 1.0,
) -> None:
    edges.append(
        {
            "source": source,
            "target": target,
            "relation": relation,
            "confidence": confidence,
            "confidence_score": score,
            "source_file": str(source_file.resolve()),
            "source_location": None,
            "weight": 1.0,
        }
    )


def candidate_files() -> tuple[list[Path], dict[str, dict[str, Path | None]]]:
    files: list[Path] = []
    components: dict[str, dict[str, Path | None]] = {}

    def add(path: Path) -> Path | None:
        if path.exists():
            files.append(path)
            return path
        return None

    for rel_path in MODULE_CONTRACTS:
        add(REPO_ROOT / rel_path)

    for table in OUTPUT_TABLES:
        components[table] = {
            "schema": add(FOUNDATIONS_ROOT / "canonical_schemas" / "outputs" / f"{table}_schema_contract.md"),
            "dataset_contract": add(
                FOUNDATIONS_ROOT
                / "contract_registry"
                / "dataset_contracts"
                / f"{table}_dataset_contract_v0_1.md"
            ),
            "registry": add(FOUNDATIONS_ROOT / "dataset_registry" / "outputs" / f"{table}_registry_entry.yaml"),
            "consumption_policy": add(FOUNDATIONS_ROOT / "data_consumption_policies" / f"{table}_consumption_policy.md"),
            "validator": add(FOUNDATIONS_ROOT / "validators" / "outputs" / f"{table}_validators.md"),
        }

    unique: dict[str, Path] = {}
    for path in files:
        unique[str(path.resolve()).lower()] = path
    return list(unique.values()), components


def corpus_manifest(files: list[Path]) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for path in sorted(files, key=lambda p: rel(p).lower()):
        text = path.read_text(encoding="utf-8", errors="replace")
        manifest.append(
            {
                "path": rel(path),
                "absolute_path": str(path.resolve()),
                "sha256": sha256_file(path),
                "line_count": text.count("\n") + (1 if text else 0),
                "word_count": count_words(text),
                "bytes": path.stat().st_size,
            }
        )
    return manifest


def build_extraction(components: dict[str, dict[str, Path | None]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []

    target_contract = REPO_ROOT / MODULE_CONTRACTS[0]
    status_matrix = REPO_ROOT / MODULE_CONTRACTS[1]
    composition_contract = REPO_ROOT / MODULE_CONTRACTS[2]
    build_loop = REPO_ROOT / MODULE_CONTRACTS[3]
    intraday_plan = REPO_ROOT / MODULE_CONTRACTS[4]
    microstructure_plan = REPO_ROOT / MODULE_CONTRACTS[5]
    short_constraints_contract = REPO_ROOT / MODULE_CONTRACTS[6]
    short_constraints_runbook = REPO_ROOT / MODULE_CONTRACTS[7]

    outputs_contract = node(nodes, "contract", "target_contract", "Data Foundation Outputs Target Contract", "document", target_contract)
    status_node = node(nodes, "contract", "status_matrix", "Data Foundation Outputs Status Matrix", "document", status_matrix)
    composition_node = node(nodes, "contract", "market_state_event_state_composition", "Market State Event State Composition", "document", composition_contract)
    build_loop_node = node(nodes, "contract", "market_state_event_state_build_loop", "Market State Event State Build Loop", "document", build_loop)
    output_root_node = node(nodes, "filesystem", "data_foundation_outputs", "E:/TSIS/data/data_foundation_outputs", "concept", target_contract)

    table_nodes: dict[str, str] = {}
    for table in OUTPUT_TABLES:
        table_node = node(nodes, "table", table, table, "concept", target_contract)
        table_nodes[table] = table_node
        edge(edges, outputs_contract, table_node, "implements", target_contract)
        edge(edges, status_node, table_node, "references", status_matrix)
        table_output_node = node(
            nodes,
            "output_path",
            table,
            str((OUTPUT_ROOT / table).as_posix()),
            "concept",
            target_contract,
        )
        edge(edges, table_node, table_output_node, "references", target_contract, "INFERRED", 0.85)
        edge(edges, output_root_node, table_output_node, "references", target_contract, "INFERRED", 0.85)

        for component, path in components[table].items():
            if path is None:
                missing.append({"table": table, "component": component})
                continue
            component_node = node(nodes, component, table, f"{table} {component}", "document", path)
            edge(edges, table_node, component_node, "references", path)
            if component == "schema":
                edge(edges, component_node, table_node, "implements", path)
            elif component == "validator":
                edge(edges, component_node, table_node, "conceptually_related_to", path, "INFERRED", 0.85)
            elif component == "registry":
                edge(edges, component_node, table_output_node, "references", path)
            elif component == "consumption_policy":
                edge(edges, component_node, table_node, "rationale_for", path, "INFERRED", 0.85)
            elif component == "dataset_contract":
                edge(edges, component_node, table_node, "implements", path)

    market_state_inputs = [
        "instrument_master",
        "market_calendar",
        "master_daily_table",
        "master_intraday_bar_table",
        "microstructure_features_table",
        "halts_table",
        "fundamentals_asof_table",
        "news_context_table",
        "short_context_table",
        "short_sale_constraints_table",
        "regime_context_table",
        "dataset_certification_matrix",
    ]
    for table in market_state_inputs:
        if table in table_nodes:
            edge(edges, table_nodes[table], table_nodes["market_state_table"], "shares_data_with", composition_contract, "INFERRED", 0.85)
    event_state_inputs = ["event_windows_table", "outcomes_table", "halts_table", "news_context_table", "market_state_table"]
    for table in event_state_inputs:
        if table in table_nodes:
            edge(edges, table_nodes[table], table_nodes["event_state_table"], "shares_data_with", composition_contract, "INFERRED", 0.85)

    edge(edges, composition_node, table_nodes["market_state_table"], "implements", composition_contract)
    edge(edges, composition_node, table_nodes["event_state_table"], "implements", composition_contract)
    edge(edges, build_loop_node, table_nodes["market_state_table"], "rationale_for", build_loop, "INFERRED", 0.85)
    edge(edges, build_loop_node, table_nodes["event_state_table"], "rationale_for", build_loop, "INFERRED", 0.85)

    if "master_intraday_bar_table" in table_nodes:
        plan_node = node(nodes, "plan", "master_intraday_wider_scope", "Master Intraday Wider Scope Plan", "document", intraday_plan)
        edge(edges, plan_node, table_nodes["master_intraday_bar_table"], "rationale_for", intraday_plan, "INFERRED", 0.85)
    if "microstructure_features_table" in table_nodes:
        plan_node = node(nodes, "plan", "microstructure_multi_window", "Microstructure Multi Window Plan", "document", microstructure_plan)
        edge(edges, plan_node, table_nodes["microstructure_features_table"], "rationale_for", microstructure_plan, "INFERRED", 0.85)
    if "short_sale_constraints_table" in table_nodes:
        contract_node = node(nodes, "contract", "short_sale_constraints_target", "Short Sale Constraints Target Contract", "document", short_constraints_contract)
        runbook_node = node(nodes, "runbook", "short_sale_constraints_acquisition", "Short Sale Constraints Acquisition Runbook", "document", short_constraints_runbook)
        edge(edges, contract_node, table_nodes["short_sale_constraints_table"], "implements", short_constraints_contract)
        edge(edges, runbook_node, table_nodes["short_sale_constraints_table"], "rationale_for", short_constraints_runbook, "INFERRED", 0.85)
        edge(edges, table_nodes["short_context_table"], table_nodes["short_sale_constraints_table"], "conceptually_related_to", short_constraints_contract, "INFERRED", 0.85)

    extraction = {
        "nodes": list({item["id"]: item for item in nodes}.values()),
        "edges": edges,
        "hyperedges": [
            {
                "id": "data_foundation_output_table_contract_stack",
                "label": "Data Foundation Output Table Contract Stack",
                "nodes": [outputs_contract, status_node, output_root_node],
                "relation": "form",
                "confidence": "EXTRACTED",
                "confidence_score": 1.0,
                "source_file": str(target_contract.resolve()),
            },
            {
                "id": "market_state_event_state_composition_stack",
                "label": "Market State Event State Composition Stack",
                "nodes": [composition_node, build_loop_node, table_nodes["market_state_table"], table_nodes["event_state_table"]],
                "relation": "form",
                "confidence": "INFERRED",
                "confidence_score": 0.85,
                "source_file": str(composition_contract.resolve()),
            },
        ],
        "input_tokens": 0,
        "output_tokens": 0,
    }
    return extraction, missing


def detection_result(corpus: list[dict[str, Any]]) -> dict[str, Any]:
    files = [item["absolute_path"] for item in corpus]
    return {
        "scan_root": str(REPO_ROOT),
        "total_files": len(corpus),
        "total_words": sum(item["word_count"] for item in corpus),
        "warning": None,
        "skipped_sensitive": [],
        "files": {"code": [], "document": files, "paper": [], "image": [], "video": []},
    }


def label_communities(G: Any, communities: dict[int, list[str]]) -> dict[int, str]:
    labels: dict[int, str] = {}
    for cid, members in communities.items():
        text = " ".join(str(G.nodes[n].get("label", n)).lower() for n in members)
        if "market_state" in text or "event_state" in text:
            labels[cid] = "Market Event State"
        elif "microstructure" in text or "intraday" in text:
            labels[cid] = "Intraday Microstructure"
        elif "short" in text:
            labels[cid] = "Short Context"
        elif "calendar" in text or "instrument" in text:
            labels[cid] = "Reference Identity"
        elif "schema" in text:
            labels[cid] = "Schema Stack"
        elif "validator" in text:
            labels[cid] = "Validation Stack"
        elif "registry" in text:
            labels[cid] = "Registry Stack"
        else:
            labels[cid] = f"Output Contracts {cid}"
    return labels


def write_manifest(
    leaf_dir: Path,
    corpus: list[dict[str, Any]],
    extraction: dict[str, Any],
    diagnostics: dict[str, Any],
    missing: list[dict[str, Any]],
    G: Any,
    communities: dict[int, list[str]],
    labels: dict[int, str],
) -> None:
    now = datetime.now(timezone.utc)
    branch = run_git(["branch", "--show-current"]) or "unknown"
    commit = run_git(["rev-parse", "HEAD"]) or "unknown"
    status_short = run_git(["status", "--short"])
    dirty = bool(status_short.strip())
    skill_path = Path.home() / ".codex" / "skills" / "graphify" / "SKILL.md"
    skill_sha = sha256_file(skill_path) if skill_path.exists() else None
    corpus_lines = "\n".join(
        f"- {item['path']} | sha256={item['sha256']} | lines={item['line_count']} | words={item['word_count']}"
        for item in corpus
    )
    missing_lines = "\n".join(f"- {item['table']} / {item['component']}" for item in missing) or "- none"
    dirty_block = status_short if status_short else "(clean)"
    labels_yaml = "\n".join(f"  {cid}: {label}" for cid, label in sorted(labels.items()))

    manifest = f"""# Data Foundation Outputs Topology Graphify Leaf Manifest

Date: {now.date().isoformat()}
Status: runtime, reconstructible Graphify leaf output.

Scope: deterministic topology of CAPA 1 Data Foundation output tables.
Leaf output: `{leaf_dir}`

## Graph Build Baseline

```yaml
graph_build_git_branch: {branch}
graph_build_git_commit: {commit}
graph_build_dirty_state: {str(dirty).lower()}
graph_build_timestamp_utc: {now.isoformat()}
graphify_package_version: {importlib_metadata.version("graphifyy")}
graphify_skill_path: {skill_path}
graphify_skill_sha256: {skill_sha}
no_api_mode: true
semantic_extraction_mode: deterministic_file_topology_extraction
build_from_json_root_or_equivalent: {REPO_ROOT}
root_graph_updated: false
next_delta_commands:
  - git diff --name-status {commit}...HEAD
  - git status --short
```

Important limitation:

```text
This leaf maps table-to-contract topology from governed filenames and explicit
module contracts. It is not a full semantic reading of every schema field or
validator rule. It is safe as a navigation/control graph, not as the final
semantic graph for all Data Foundation outputs.
```

### Dirty Paths

```text
{dirty_block}
```

## Corpus

Corpus files:

```text
{corpus_lines}
```

## Missing Components

```text
{missing_lines}
```

## Leaf Stats

```yaml
extraction_nodes: {len(extraction.get("nodes", []))}
extraction_edges: {len(extraction.get("edges", []))}
extraction_hyperedges: {len(extraction.get("hyperedges", []))}
nodes: {G.number_of_nodes()}
edges: {G.number_of_edges()}
communities: {len(communities)}
detected_files: {len(corpus)}
detected_words_approx: {sum(item["word_count"] for item in corpus)}
community_labels:
{labels_yaml}
```

## Diagnostic

```yaml
missing_endpoint_edges: {diagnostics.get("missing_endpoint_edges", 0)}
dangling_endpoint_edges: {diagnostics.get("dangling_endpoint_edges", 0)}
self_loop_edges: {diagnostics.get("self_loop_edges", 0)}
exact_duplicate_edges: {diagnostics.get("exact_duplicate_edges", 0)}
directed_same_endpoint_collapsed_edges: {diagnostics.get("directed_same_endpoint_collapsed_edges", 0)}
undirected_same_endpoint_collapsed_edges: {diagnostics.get("undirected_same_endpoint_collapsed_edges", 0)}
```
"""
    (leaf_dir / "BUILD_MANIFEST.md").write_text(manifest, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic Data Foundation output table topology leaf.")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    graph_path = LEAF_DIR / "graph.json"
    if graph_path.exists() and not args.force:
        print(f"Refusing to overwrite existing leaf without --force: {graph_path}", file=sys.stderr)
        return 2

    files, components = candidate_files()
    corpus = corpus_manifest(files)
    extraction, missing = build_extraction(components)
    detect = detection_result(corpus)

    LEAF_DIR.mkdir(parents=True, exist_ok=True)
    (LEAF_DIR / ".graphify_python").write_text(sys.executable, encoding="utf-8")
    (LEAF_DIR / ".graphify_root").write_text(str(REPO_ROOT), encoding="utf-8")
    (LEAF_DIR / "pre_manifest.json").write_text(
        json.dumps(
            {
                "run_id": "data_foundation_outputs_topology_20260629",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "repo_root": str(REPO_ROOT),
                "leaf_dir": str(LEAF_DIR),
                "corpus_file_count": len(corpus),
                "missing_components": missing,
                "graphify_package_version": importlib_metadata.version("graphifyy"),
                "semantic_extraction_mode": "deterministic_file_topology_extraction",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (LEAF_DIR / "corpus_manifest.json").write_text(json.dumps(corpus, indent=2, ensure_ascii=False), encoding="utf-8")
    (LEAF_DIR / ".graphify_detect.json").write_text(json.dumps(detect, indent=2, ensure_ascii=False), encoding="utf-8")
    (LEAF_DIR / ".graphify_extract.json").write_text(json.dumps(extraction, indent=2, ensure_ascii=False), encoding="utf-8")

    diagnostics = diagnose_extraction(extraction, directed=False, root=REPO_ROOT)
    (LEAF_DIR / ".graphify_diagnose.json").write_text(json.dumps(diagnostics, indent=2, ensure_ascii=False), encoding="utf-8")
    (LEAF_DIR / "GRAPH_DIAGNOSTIC.md").write_text(format_diagnostic_report(diagnostics), encoding="utf-8")

    G = build_from_json(extraction, root=REPO_ROOT, directed=False)
    communities = cluster(G)
    cohesion = score_all(G, communities)
    labels = label_communities(G, communities)
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    questions = suggest_questions(G, communities, labels)
    commit = run_git(["rev-parse", "HEAD"]) or None

    wrote = to_json(G, communities, str(graph_path), force=args.force, built_at_commit=commit, community_labels=labels)
    if not wrote:
        print("Graphify refused to write graph.json due to shrink guard.", file=sys.stderr)
        return 3

    report = generate(
        G,
        communities,
        cohesion,
        labels,
        gods,
        surprises,
        detect,
        {"input": 0, "output": 0},
        str(REPO_ROOT),
        suggested_questions=questions,
        built_at_commit=commit,
    )
    (LEAF_DIR / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
    (LEAF_DIR / ".graphify_analysis.json").write_text(
        json.dumps(
            {
                "communities": {str(k): v for k, v in communities.items()},
                "cohesion": {str(k): v for k, v in cohesion.items()},
                "gods": gods,
                "surprises": surprises,
                "questions": questions,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (LEAF_DIR / ".graphify_labels.json").write_text(
        json.dumps({str(k): v for k, v in labels.items()}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    to_html(G, communities, str(LEAF_DIR / "graph.html"), community_labels=labels)
    write_manifest(LEAF_DIR, corpus, extraction, diagnostics, missing, G, communities, labels)

    print(f"Leaf complete: {LEAF_DIR}")
    print(f"Corpus files: {len(corpus)}")
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities")
    print(f"Missing components: {len(missing)}")
    print(f"Diagnostics: missing={diagnostics.get('missing_endpoint_edges', 0)} dangling={diagnostics.get('dangling_endpoint_edges', 0)} self_loops={diagnostics.get('self_loop_edges', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
