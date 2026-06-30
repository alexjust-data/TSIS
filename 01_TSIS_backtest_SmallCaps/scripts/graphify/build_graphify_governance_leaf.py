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


DEFAULT_REPO_ROOT = Path(r"C:\TSIS_Data")
DEFAULT_LEAF_DIR = (
    DEFAULT_REPO_ROOT
    / "00_CTO"
    / "graphify-out"
    / "leaf_slices"
    / "graphify_governance_20260629"
)


CORPUS_RELATIVE_PATHS = [
    "AGENTS.md",
    "CHANGELOG.md",
    "PROJECT_OPERATING_SYSTEM.md",
    "PROJECT_RULES.md",
    "VERSIONING_STANDARDS.md",
    "ARCHITECTURE_OVERVIEW.md",
    "RESEARCH_PHILOSOPHY.md",
    "LONG_RUNNING_OPERATIONS_CONTRACT.md",
    "00_CTO/LOCAL_RULES.md",
    "00_CTO/README.md",
    "00_CTO/CHANGELOG.md",
    "00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md",
    "00_CTO/GRAPHIFY_REFRESH_QUEUE.md",
    "01_TSIS_backtest_SmallCaps/LOCAL_RULES.md",
    "01_TSIS_backtest_SmallCaps/CHANGELOG.md",
    "01_TSIS_backtest_SmallCaps/01_foundations/README.md",
    "01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md",
    "01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md",
    "01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/graphify/README.md",
    "01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md",
    "01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md",
    "01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_REFRESH_QUEUE.md",
]


def run_git(repo_root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    return result.stdout.strip()


def sha256_text(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_words(text: str) -> int:
    return len(re.findall(r"\b\S+\b", text))


def normalize_id(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
    return cleaned or "node"


def node_id(rel_path: str, entity: str) -> str:
    stem = Path(rel_path).with_suffix("").as_posix()
    return f"{normalize_id(stem)}_{normalize_id(entity)}"


def make_node(rel_path: str, entity: str, label: str, file_type: str, repo_root: Path) -> dict[str, Any]:
    return {
        "id": node_id(rel_path, entity),
        "label": label,
        "file_type": file_type,
        "source_file": str((repo_root / rel_path).resolve()),
        "source_location": None,
        "source_url": None,
        "captured_at": None,
        "author": None,
        "contributor": None,
    }


def make_edge(
    source: str,
    target: str,
    relation: str,
    confidence: str,
    score: float,
    rel_path: str,
    repo_root: Path,
    weight: float = 1.0,
) -> dict[str, Any]:
    return {
        "source": source,
        "target": target,
        "relation": relation,
        "confidence": confidence,
        "confidence_score": score,
        "source_file": str((repo_root / rel_path).resolve()),
        "source_location": None,
        "weight": weight,
    }


def build_extraction(repo_root: Path) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    def n(rel: str, entity: str, label: str, file_type: str = "concept") -> str:
        node = make_node(rel, entity, label, file_type, repo_root)
        nodes.append(node)
        return node["id"]

    def e(
        source: str,
        target: str,
        relation: str,
        rel: str,
        confidence: str = "EXTRACTED",
        score: float = 1.0,
        weight: float = 1.0,
    ) -> None:
        edges.append(make_edge(source, target, relation, confidence, score, rel, repo_root, weight))

    agents_contract = n("AGENTS.md", "TSIS Agents Contract", "TSIS Agents Contract", "document")
    mandatory_reading = n("AGENTS.md", "Mandatory Reading Order", "Mandatory Reading Order")
    no_hidden_state = n("AGENTS.md", "No Hidden State Assumption", "No Hidden State Assumption")
    institutional_artifacts = n("AGENTS.md", "Institutional Artifacts", "Institutional Artifacts")
    reproducibility = n("AGENTS.md", "Reproducibility Minimum", "Reproducibility Minimum")

    project_os = n("PROJECT_OPERATING_SYSTEM.md", "Project Operating System", "Project Operating System", "document")
    root_changelog = n("CHANGELOG.md", "Root Changelog", "Root Changelog", "document")
    governance_leaf_build = n(
        "CHANGELOG.md",
        "Cross Project Graphify Governance Leaf Build",
        "Cross Project Graphify Governance Leaf Build",
    )
    project_rules = n("PROJECT_RULES.md", "Project Rules", "Project Rules", "document")
    versioning = n("VERSIONING_STANDARDS.md", "Versioning Standards", "Versioning Standards", "document")
    architecture = n("ARCHITECTURE_OVERVIEW.md", "Architecture Overview", "Architecture Overview", "document")
    philosophy = n("RESEARCH_PHILOSOPHY.md", "Research Philosophy", "Research Philosophy", "document")
    long_running = n(
        "LONG_RUNNING_OPERATIONS_CONTRACT.md",
        "Long Running Operations Contract",
        "Long Running Operations Contract",
        "document",
    )
    telemetry = n("LONG_RUNNING_OPERATIONS_CONTRACT.md", "Progress Telemetry Standard", "Progress Telemetry Standard")
    pre_manifest = n("LONG_RUNNING_OPERATIONS_CONTRACT.md", "Pre Manifest", "Pre Manifest")
    heartbeat = n("LONG_RUNNING_OPERATIONS_CONTRACT.md", "Heartbeat", "Heartbeat")
    pid_manifest = n("LONG_RUNNING_OPERATIONS_CONTRACT.md", "PID Manifest", "PID Manifest")
    monitor = n("LONG_RUNNING_OPERATIONS_CONTRACT.md", "Separate Monitor", "Separate Monitor")

    cto_local = n("00_CTO/LOCAL_RULES.md", "CTO Local Rules", "CTO Local Rules", "document")
    cto_graph_protocol = n(
        "00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md",
        "CTO Graphify Official Build Protocol",
        "CTO Graphify Official Build Protocol",
        "document",
    )
    cto_queue = n(
        "00_CTO/GRAPHIFY_REFRESH_QUEUE.md",
        "CTO Graphify Refresh Queue",
        "CTO Graphify Refresh Queue",
        "document",
    )
    cto_root_graph = n("00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "CTO Root Graph", "CTO Root Graph")
    leaf_first = n("00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "Leaf First Graph Build", "Leaf First Graph Build")
    build_manifest = n("00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "Build Manifest Baseline", "Build Manifest Baseline")
    no_api_mode = n("00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "No API Mode", "No API Mode")
    graph_delta = n("00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "Graph Delta Audit", "Graph Delta Audit")
    merge_gate = n("00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "Root Merge Gate", "Root Merge Gate")
    runtime_output = n("00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "Graphify Runtime Output", "Graphify Runtime Output")

    smallcaps_local = n("01_TSIS_backtest_SmallCaps/LOCAL_RULES.md", "SmallCaps Local Rules", "SmallCaps Local Rules", "document")
    foundations_readme = n(
        "01_TSIS_backtest_SmallCaps/01_foundations/README.md",
        "Data Foundation README",
        "Data Foundation README",
        "document",
    )
    foundations_graph_protocol = n(
        "01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md",
        "Data Foundation Graphify Official Build Protocol",
        "Data Foundation Graphify Official Build Protocol",
        "document",
    )
    foundations_queue = n(
        "01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md",
        "Data Foundation Graphify Refresh Queue",
        "Data Foundation Graphify Refresh Queue",
        "document",
    )
    foundations_root_graph = n(
        "01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md",
        "Data Foundation Root Graph",
        "Data Foundation Root Graph",
    )
    table_graph_protocol = n(
        "01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md",
        "Data Foundation Graph and Table Design Protocol",
        "Data Foundation Graph and Table Design Protocol",
        "document",
    )
    table_outputs = n(
        "01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md",
        "Data Foundation Outputs",
        "Data Foundation Outputs",
    )
    market_state_outputs = n(
        "01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md",
        "Market State Tables",
        "Market State Tables",
    )

    certification_graph_protocol = n(
        "01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md",
        "Data Certification Graphify Official Build Protocol",
        "Data Certification Graphify Official Build Protocol",
        "document",
    )
    certification_queue = n(
        "01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_REFRESH_QUEUE.md",
        "Data Certification Graphify Refresh Queue",
        "Data Certification Graphify Refresh Queue",
        "document",
    )
    certification_root_graph = n(
        "01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md",
        "Data Certification Root Graph",
        "Data Certification Root Graph",
    )

    e(agents_contract, mandatory_reading, "implements", "AGENTS.md")
    e(agents_contract, no_hidden_state, "implements", "AGENTS.md")
    e(agents_contract, institutional_artifacts, "implements", "AGENTS.md")
    e(agents_contract, reproducibility, "implements", "AGENTS.md")
    e(mandatory_reading, project_os, "references", "AGENTS.md")
    e(mandatory_reading, project_rules, "references", "AGENTS.md")
    e(mandatory_reading, versioning, "references", "AGENTS.md")
    e(mandatory_reading, architecture, "references", "AGENTS.md")
    e(mandatory_reading, philosophy, "references", "AGENTS.md")
    e(reproducibility, build_manifest, "conceptually_related_to", "AGENTS.md", "INFERRED", 0.85)
    e(no_hidden_state, graph_delta, "conceptually_related_to", "AGENTS.md", "INFERRED", 0.85)

    e(root_changelog, governance_leaf_build, "references", "CHANGELOG.md")
    e(governance_leaf_build, cto_graph_protocol, "references", "CHANGELOG.md", "INFERRED", 0.85)
    e(governance_leaf_build, foundations_graph_protocol, "references", "CHANGELOG.md", "INFERRED", 0.85)
    e(governance_leaf_build, certification_graph_protocol, "references", "CHANGELOG.md", "INFERRED", 0.85)
    e(governance_leaf_build, long_running, "references", "CHANGELOG.md", "INFERRED", 0.75)

    e(project_rules, long_running, "references", "PROJECT_RULES.md", "INFERRED", 0.85)
    e(project_rules, cto_graph_protocol, "references", "PROJECT_RULES.md", "INFERRED", 0.85)
    e(versioning, build_manifest, "rationale_for", "VERSIONING_STANDARDS.md", "INFERRED", 0.85)
    e(architecture, cto_root_graph, "conceptually_related_to", "ARCHITECTURE_OVERVIEW.md", "INFERRED", 0.75)

    e(long_running, telemetry, "implements", "LONG_RUNNING_OPERATIONS_CONTRACT.md")
    e(telemetry, pre_manifest, "implements", "LONG_RUNNING_OPERATIONS_CONTRACT.md")
    e(telemetry, heartbeat, "implements", "LONG_RUNNING_OPERATIONS_CONTRACT.md")
    e(telemetry, pid_manifest, "implements", "LONG_RUNNING_OPERATIONS_CONTRACT.md")
    e(telemetry, monitor, "implements", "LONG_RUNNING_OPERATIONS_CONTRACT.md")
    e(long_running, cto_graph_protocol, "conceptually_related_to", "LONG_RUNNING_OPERATIONS_CONTRACT.md", "INFERRED", 0.75)
    e(long_running, foundations_graph_protocol, "conceptually_related_to", "LONG_RUNNING_OPERATIONS_CONTRACT.md", "INFERRED", 0.75)
    e(long_running, certification_graph_protocol, "conceptually_related_to", "LONG_RUNNING_OPERATIONS_CONTRACT.md", "INFERRED", 0.75)

    e(cto_local, cto_graph_protocol, "references", "00_CTO/LOCAL_RULES.md", "INFERRED", 0.75)
    e(cto_graph_protocol, cto_root_graph, "implements", "00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md")
    e(cto_graph_protocol, leaf_first, "implements", "00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md")
    e(cto_graph_protocol, build_manifest, "implements", "00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md")
    e(cto_graph_protocol, no_api_mode, "implements", "00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md")
    e(cto_graph_protocol, graph_delta, "implements", "00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md")
    e(cto_graph_protocol, merge_gate, "implements", "00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md")
    e(cto_graph_protocol, runtime_output, "implements", "00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md")
    e(cto_queue, cto_graph_protocol, "references", "00_CTO/GRAPHIFY_REFRESH_QUEUE.md")
    e(cto_queue, graph_delta, "conceptually_related_to", "00_CTO/GRAPHIFY_REFRESH_QUEUE.md", "INFERRED", 0.85)

    e(smallcaps_local, foundations_graph_protocol, "references", "01_TSIS_backtest_SmallCaps/LOCAL_RULES.md", "INFERRED", 0.75)
    e(foundations_readme, foundations_graph_protocol, "references", "01_TSIS_backtest_SmallCaps/01_foundations/README.md", "INFERRED", 0.75)
    e(foundations_graph_protocol, foundations_root_graph, "implements", "01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md")
    e(foundations_graph_protocol, leaf_first, "conceptually_related_to", "01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "INFERRED", 0.85)
    e(foundations_graph_protocol, build_manifest, "implements", "01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md")
    e(foundations_graph_protocol, no_api_mode, "implements", "01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md")
    e(foundations_graph_protocol, graph_delta, "implements", "01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md")
    e(foundations_queue, foundations_graph_protocol, "references", "01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md")
    e(foundations_queue, graph_delta, "conceptually_related_to", "01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md", "INFERRED", 0.85)
    e(table_graph_protocol, foundations_graph_protocol, "references", "01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md")
    e(table_graph_protocol, table_outputs, "implements", "01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md")
    e(table_graph_protocol, market_state_outputs, "implements", "01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md")
    e(table_outputs, market_state_outputs, "conceptually_related_to", "01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md", "INFERRED", 0.85)

    e(certification_graph_protocol, certification_root_graph, "implements", "01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md")
    e(certification_graph_protocol, leaf_first, "conceptually_related_to", "01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "INFERRED", 0.85)
    e(certification_graph_protocol, build_manifest, "implements", "01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md")
    e(certification_graph_protocol, no_api_mode, "implements", "01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md")
    e(certification_graph_protocol, graph_delta, "implements", "01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md")
    e(certification_queue, certification_graph_protocol, "references", "01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_REFRESH_QUEUE.md")
    e(certification_queue, graph_delta, "conceptually_related_to", "01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_REFRESH_QUEUE.md", "INFERRED", 0.85)

    e(cto_root_graph, foundations_root_graph, "conceptually_related_to", "00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "INFERRED", 0.85)
    e(foundations_root_graph, certification_root_graph, "conceptually_related_to", "01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "INFERRED", 0.85)
    e(cto_root_graph, certification_root_graph, "conceptually_related_to", "00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "INFERRED", 0.75)
    e(merge_gate, cto_root_graph, "rationale_for", "00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "INFERRED", 0.85)
    e(merge_gate, foundations_root_graph, "rationale_for", "01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "INFERRED", 0.85)
    e(merge_gate, certification_root_graph, "rationale_for", "01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "INFERRED", 0.85)
    e(runtime_output, institutional_artifacts, "conceptually_related_to", "00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "INFERRED", 0.75)

    return {
        "nodes": nodes,
        "edges": edges,
        "hyperedges": [
            {
                "id": "three_root_graphify_governance",
                "label": "Three Root Graphify Governance",
                "nodes": [cto_root_graph, foundations_root_graph, certification_root_graph],
                "relation": "form",
                "confidence": "INFERRED",
                "confidence_score": 0.85,
                "source_file": str((repo_root / "00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md").resolve()),
            },
            {
                "id": "long_running_graphify_observability",
                "label": "Long Running Graphify Observability",
                "nodes": [pre_manifest, heartbeat, pid_manifest, monitor],
                "relation": "form",
                "confidence": "EXTRACTED",
                "confidence_score": 1.0,
                "source_file": str((repo_root / "LONG_RUNNING_OPERATIONS_CONTRACT.md").resolve()),
            },
        ],
        "input_tokens": 0,
        "output_tokens": 0,
    }


def build_detection(repo_root: Path, corpus: list[dict[str, Any]]) -> dict[str, Any]:
    files = [str((repo_root / item["path"]).resolve()) for item in corpus]
    return {
        "scan_root": str(repo_root.resolve()),
        "total_files": len(corpus),
        "total_words": sum(item["word_count"] for item in corpus),
        "warning": None,
        "skipped_sensitive": [],
        "files": {
            "code": [],
            "document": files,
            "paper": [],
            "image": [],
            "video": [],
        },
    }


def label_communities(G: Any, communities: dict[int, list[str]]) -> dict[int, str]:
    labels: dict[int, str] = {}
    for cid, members in communities.items():
        text = " ".join((str(G.nodes[m].get("label", m)) for m in members)).lower()
        if "heartbeat" in text or "pid" in text or "monitor" in text:
            labels[cid] = "Operational Telemetry"
        elif "queue" in text or "delta" in text:
            labels[cid] = "Refresh Queue Control"
        elif "certification" in text:
            labels[cid] = "Certification Graph"
        elif "foundation" in text or "table" in text or "market state" in text:
            labels[cid] = "Data Foundation Graph"
        elif "agent" in text or "hidden state" in text or "reproducibility" in text:
            labels[cid] = "Agent Traceability"
        elif "version" in text or "manifest" in text:
            labels[cid] = "Versioned Manifest"
        elif "cto" in text:
            labels[cid] = "CTO Graph Governance"
        else:
            labels[cid] = f"Governance Cluster {cid}"
    return labels


def write_manifest(
    repo_root: Path,
    leaf_dir: Path,
    corpus: list[dict[str, Any]],
    extraction: dict[str, Any],
    diagnostics: dict[str, Any],
    G: Any,
    communities: dict[int, list[str]],
    labels: dict[int, str],
) -> None:
    now = datetime.now(timezone.utc)
    branch = run_git(repo_root, ["branch", "--show-current"]) or "unknown"
    commit = run_git(repo_root, ["rev-parse", "HEAD"]) or "unknown"
    status_short = run_git(repo_root, ["status", "--short"])
    dirty = bool(status_short.strip())
    changed_since_head = run_git(repo_root, ["diff", "--name-status", f"{commit}...HEAD"])
    graphify_version = importlib_metadata.version("graphifyy")
    skill_path = Path.home() / ".codex" / "skills" / "graphify" / "SKILL.md"
    skill_sha = sha256_text(skill_path) if skill_path.exists() else None

    corpus_lines = "\n".join(
        f"- {item['path']} | sha256={item['sha256']} | lines={item['line_count']} | words={item['word_count']}"
        for item in corpus
    )
    dirty_block = status_short if status_short else "(clean)"
    delta_block = changed_since_head if changed_since_head else "(no committed delta from HEAD)"
    labels_yaml = "\n".join(f"  {cid}: {label}" for cid, label in sorted(labels.items()))

    manifest = f"""# Graphify Governance Leaf Manifest

Date: {now.date().isoformat()}
Status: runtime, reconstructible Graphify leaf output.

Scope: cross-project Graphify governance contracts for `00_CTO`, `01_foundations`, and `00_data_certification`.
Leaf output: `{leaf_dir}`

## Graph Build Baseline

```yaml
graph_build_git_branch: {branch}
graph_build_git_commit: {commit}
graph_build_dirty_state: {str(dirty).lower()}
graph_build_timestamp_utc: {now.isoformat()}
graphify_package_version: {graphify_version}
graphify_skill_path: {skill_path}
graphify_skill_sha256: {skill_sha}
graphify_upstream_reference: https://github.com/safishamsi/graphify
graphify_installed_vs_protocol_status: aligned_to_0_9_1_before_build
no_api_mode: true
semantic_extraction_mode: codex_host_inline_manual_semantic_extraction
gemini_api_key_present: {str(bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))).lower()}
build_from_json_root_or_equivalent: {repo_root}
semantic_update_coverage: curated_governance_docs_only
root_graph_updated: false
queue_entries_covered:
  - graphify_governance_protocol_alignment
  - build_manifest_commit_and_corpus_baseline
  - no_api_graphify_semantic_extraction_rule
next_delta_commands:
  - git diff --name-status {commit}...HEAD
  - git status --short
```

Dirty paths are recorded because this leaf was built against the current working
tree. This leaf is not a promotion of every dirty path; it only covers the
corpus listed below.

### Dirty Paths

```text
{dirty_block}
```

### Delta Since Build Commit

```text
{delta_block}
```

## Procedure

- Controlled corpus selected from root, `00_CTO`, `01_foundations`, and `00_data_certification` governance docs.
- Graphify package and Codex skill were aligned to `graphifyy 0.9.1` before build.
- No external API key was required or requested.
- Semantic extraction was performed inline by the host Codex agent using the Graphify extraction schema.
- Official Graphify `build_from_json` assembly was used.
- Official Graphify community detection, JSON export, HTML export, report generation and diagnostics were used.
- Root `00_CTO/graphify-out/graph.json` was intentionally not updated.

## Corpus

Inclusion rules:

```text
- root governance docs required by AGENTS.md
- Graphify official build protocols
- Graphify refresh queues
- Graphify table/design protocol for Data Foundation graph coupling
- long-running operations contract
```

Exclusion rules:

```text
- no raw data
- no data_foundation_outputs materializations
- no graphify-out historical graph payloads
- no notebooks
- no images
- no private documents beyond explicit governance files
```

Corpus files:

```text
{corpus_lines}
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

## Build Notes

- This is a leaf refresh only.
- This leaf establishes the governance graph standard for the next larger rebuilds.
- It does not claim full semantic coverage of `00_CTO`, `01_foundations`, or `00_data_certification`.
- The next work item is to rebuild each root through bounded leaves and merge only after diagnostics are clean.
"""
    (leaf_dir / "BUILD_MANIFEST.md").write_text(manifest, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the TSIS Graphify governance leaf.")
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    parser.add_argument("--leaf-dir", default=str(DEFAULT_LEAF_DIR))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    leaf_dir = Path(args.leaf_dir).resolve()
    graph_path = leaf_dir / "graph.json"

    missing = [rel for rel in CORPUS_RELATIVE_PATHS if not (repo_root / rel).exists()]
    if missing:
        print("Missing corpus files:", file=sys.stderr)
        for rel in missing:
            print(f"  - {rel}", file=sys.stderr)
        return 2

    if graph_path.exists() and not args.force:
        print(f"Refusing to overwrite existing leaf without --force: {graph_path}", file=sys.stderr)
        return 3

    leaf_dir.mkdir(parents=True, exist_ok=True)
    (leaf_dir / ".graphify_python").write_text(sys.executable, encoding="utf-8")
    (leaf_dir / ".graphify_root").write_text(str(repo_root), encoding="utf-8")

    corpus: list[dict[str, Any]] = []
    for rel in CORPUS_RELATIVE_PATHS:
        path = repo_root / rel
        text = path.read_text(encoding="utf-8", errors="replace")
        corpus.append(
            {
                "path": rel,
                "absolute_path": str(path.resolve()),
                "sha256": sha256_text(path),
                "line_count": text.count("\n") + (1 if text else 0),
                "word_count": count_words(text),
                "bytes": path.stat().st_size,
            }
        )

    pre_manifest = {
        "run_id": "graphify_governance_20260629",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "leaf_dir": str(leaf_dir),
        "corpus_file_count": len(corpus),
        "corpus": corpus,
        "graphify_package_version": importlib_metadata.version("graphifyy"),
        "no_api_mode": True,
        "semantic_extraction_mode": "codex_host_inline_manual_semantic_extraction",
    }
    (leaf_dir / "pre_manifest.json").write_text(json.dumps(pre_manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    (leaf_dir / "corpus_manifest.json").write_text(json.dumps(corpus, indent=2, ensure_ascii=False), encoding="utf-8")

    extraction = build_extraction(repo_root)
    detection = build_detection(repo_root, corpus)
    (leaf_dir / ".graphify_extract.json").write_text(json.dumps(extraction, indent=2, ensure_ascii=False), encoding="utf-8")
    (leaf_dir / ".graphify_detect.json").write_text(json.dumps(detection, indent=2, ensure_ascii=False), encoding="utf-8")

    diagnostics = diagnose_extraction(extraction, directed=False, root=repo_root)
    (leaf_dir / ".graphify_diagnose.json").write_text(json.dumps(diagnostics, indent=2, ensure_ascii=False), encoding="utf-8")
    (leaf_dir / "GRAPH_DIAGNOSTIC.md").write_text(format_diagnostic_report(diagnostics), encoding="utf-8")

    G = build_from_json(extraction, root=repo_root, directed=False)
    if G.number_of_nodes() == 0:
        print("Graph is empty; aborting.", file=sys.stderr)
        return 4

    communities = cluster(G)
    cohesion = score_all(G, communities)
    labels = label_communities(G, communities)
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    questions = suggest_questions(G, communities, labels)
    commit = run_git(repo_root, ["rev-parse", "HEAD"]) or None

    wrote = to_json(
        G,
        communities,
        str(graph_path),
        force=args.force,
        built_at_commit=commit,
        community_labels=labels,
    )
    if not wrote:
        print("Graphify refused to write graph.json due to shrink guard.", file=sys.stderr)
        return 5

    report = generate(
        G,
        communities,
        cohesion,
        labels,
        gods,
        surprises,
        detection,
        {"input": 0, "output": 0},
        str(repo_root),
        suggested_questions=questions,
        built_at_commit=commit,
    )
    (leaf_dir / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
    (leaf_dir / ".graphify_analysis.json").write_text(
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
    (leaf_dir / ".graphify_labels.json").write_text(
        json.dumps({str(k): v for k, v in labels.items()}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    to_html(G, communities, str(leaf_dir / "graph.html"), community_labels=labels)
    write_manifest(repo_root, leaf_dir, corpus, extraction, diagnostics, G, communities, labels)

    print(f"Leaf complete: {leaf_dir}")
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities")
    print(f"Diagnostics: missing={diagnostics.get('missing_endpoint_edges', 0)} dangling={diagnostics.get('dangling_endpoint_edges', 0)} self_loops={diagnostics.get('self_loop_edges', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
