from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import importlib.metadata as importlib_metadata

from graphify.analyze import god_nodes, suggest_questions, surprising_connections
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.diagnostics import diagnose_extraction, format_diagnostic_report
from graphify.export import to_html, to_json
from graphify.report import generate


REPO_ROOT = Path(r"C:\TSIS_Data")
FOUNDATIONS = REPO_ROOT / "01_TSIS_DATA_FOUNDATION" / "01_foundations"
SMALLCAPS = REPO_ROOT / "01_TSIS_DATA_FOUNDATION"
CTO = REPO_ROOT / "00_CTO"
MARKET_STATE = CTO / "11_MARKET_SCIENCE" / "05_MARKET_STATE_REPRESENTATION"
DEFAULT_OUTPUT_BASE = REPO_ROOT / "graphify-out" / "leaf_slices"
OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs")


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


def existing(paths: list[Path]) -> list[Path]:
    seen: dict[str, Path] = {}
    for path in paths:
        if path.exists() and path.is_file():
            seen[str(path.resolve()).lower()] = path
    return sorted(seen.values(), key=lambda p: rel(p).lower())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def corpus_manifest(files: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(files, key=lambda p: rel(p).lower()):
        text = read_text(path)
        rows.append(
            {
                "path": rel(path),
                "absolute_path": str(path.resolve()),
                "sha256": sha256_file(path),
                "line_count": text.count("\n") + (1 if text else 0),
                "word_count": count_words(text),
                "bytes": path.stat().st_size,
            }
        )
    return rows


def detection_result(corpus: list[dict[str, Any]]) -> dict[str, Any]:
    docs = [item["absolute_path"] for item in corpus]
    return {
        "scan_root": str(REPO_ROOT),
        "total_files": len(corpus),
        "total_words": sum(item["word_count"] for item in corpus),
        "warning": None,
        "skipped_sensitive": [],
        "files": {"code": [], "document": docs, "paper": [], "image": [], "video": []},
    }


def add_node(nodes: list[dict[str, Any]], kind: str, name: str, label: str, file_type: str, source_file: Path) -> str:
    nid = f"tsis_{norm(kind)}_{norm(name)}"
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


def add_edge(
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


def dedupe_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return list({node["id"]: node for node in nodes}.values())


def output_tables() -> list[str]:
    return [
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
        "daily_strategy_candidate_events_table",
        "intraday_1m_strategy_candidate_events_table",
        "event_windows_table",
        "event_state_table",
        "market_state_table",
        "outcomes_table",
        "expected_data_calendar",
        "dataset_certification_matrix",
    ]


def table_component_paths(table: str) -> dict[str, Path | None]:
    return {
        "schema": FOUNDATIONS / "canonical_schemas" / "outputs" / f"{table}_schema_contract.md",
        "dataset_contract": FOUNDATIONS / "contract_registry" / "dataset_contracts" / f"{table}_dataset_contract_v0_1.md",
        "registry": FOUNDATIONS / "dataset_registry" / "outputs" / f"{table}_registry_entry.yaml",
        "consumption_policy": FOUNDATIONS / "data_consumption_policies" / f"{table}_consumption_policy.md",
        "validator": FOUNDATIONS / "validators" / "outputs" / f"{table}_validators.md",
    }


def collect_data_foundation_corpus() -> list[Path]:
    paths: list[Path] = []
    for table in output_tables():
        paths += [p for p in table_component_paths(table).values() if p is not None]
    paths += list((FOUNDATIONS / "module_contracts" / "outputs").glob("*.md"))
    paths += [
        FOUNDATIONS / "GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md",
        FOUNDATIONS / "GRAPHIFY_REFRESH_QUEUE.md",
        FOUNDATIONS / "module_contracts" / "README.md",
        SMALLCAPS / "CHANGELOG.md",
        SMALLCAPS / "scripts" / "validate_event_candidate_tables.py",
    ]
    paths += list((SMALLCAPS / "scripts").glob("materialize_*candidate*.py"))
    paths += list((SMALLCAPS / "scripts").glob("preflight_*candidate*.py"))
    paths += list((SMALLCAPS / "tests" / "data_foundation_outputs").glob("test_*candidate*.py"))
    paths += list((SMALLCAPS / "tests" / "data_foundation_outputs").glob("test_event_candidate_table_validators.py"))
    paths += list((SMALLCAPS / "configs" / "data_foundation_outputs").glob("*candidate*.json"))
    return existing(paths)


def build_data_foundation_extraction(corpus_files: list[Path]) -> tuple[dict[str, Any], list[str]]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    missing: list[str] = []
    source = FOUNDATIONS / "module_contracts" / "outputs" / "data_foundation_outputs_target_contract_v0_1.md"
    status = FOUNDATIONS / "module_contracts" / "outputs" / "data_foundation_outputs_status_matrix_v0_1.md"
    outputs_node = add_node(nodes, "contract", "data_foundation_outputs_target", "Data Foundation Outputs Target", "document", source)
    status_node = add_node(nodes, "contract", "data_foundation_outputs_status", "Data Foundation Outputs Status Matrix", "document", status)
    root_node = add_node(nodes, "filesystem", "data_foundation_outputs_root", "E:/TSIS/data/data_foundation_outputs", "concept", source)

    table_nodes: dict[str, str] = {}
    for table in output_tables():
        table_node = add_node(nodes, "table", table, table, "concept", source)
        table_nodes[table] = table_node
        add_edge(edges, outputs_node, table_node, "declares_output", source)
        add_edge(edges, status_node, table_node, "tracks_status", status)
        out_node = add_node(nodes, "output_path", table, str((OUTPUT_ROOT / table).as_posix()), "concept", source)
        add_edge(edges, table_node, out_node, "writes_under", source, "INFERRED", 0.85)
        add_edge(edges, root_node, out_node, "contains", source, "INFERRED", 0.85)
        for component, raw_path in table_component_paths(table).items():
            if raw_path is None or not raw_path.exists():
                missing.append(f"{table} / {component}")
                continue
            comp = add_node(nodes, component, table, f"{table} {component}", "document", raw_path)
            add_edge(edges, table_node, comp, "has_component", raw_path)
            add_edge(edges, comp, table_node, "governs", raw_path)

    candidate_specs = [
        ("master_intraday_bar_table_v0_2_candidate_quote_guarded", "master_intraday_bar_table", "Master Intraday Quote-Guarded Candidate"),
        ("daily_strategy_candidate_events_table_v0_1_candidate_controlled", "daily_strategy_candidate_events_table", "Daily Strategy Candidate Events Controlled"),
        ("intraday_1m_strategy_candidate_events_table_v0_1_candidate_quote_guarded", "intraday_1m_strategy_candidate_events_table", "Intraday 1m Strategy Candidate Events Quote-Guarded"),
        ("event_windows_table_v0_1_candidate_daily_strategy_events", "event_windows_table", "Daily Strategy Event Windows Candidate"),
        ("event_windows_table_v0_1_candidate_intraday_1m_quote_guarded", "event_windows_table", "Intraday 1m Event Windows Candidate"),
        ("market_state_table_v0_1_candidate_intraday_quote_guarded_controlled", "market_state_table", "Market State Intraday Quote-Guarded Candidate"),
        ("event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled", "event_state_table", "Event State Intraday Quote-Guarded Candidate"),
        ("outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_controlled", "outcomes_table", "Outcomes Intraday 1m Quote-Guarded Candidate"),
    ]
    candidate_nodes: dict[str, str] = {}
    for name, table, label in candidate_specs:
        cand = add_node(nodes, "candidate_dataset", name, label, "concept", source)
        candidate_nodes[name] = cand
        add_edge(edges, cand, table_nodes[table], "candidate_for", source, "INFERRED", 0.9)

    for path in [p for p in corpus_files if "state_raw_to_consumption_lineage" in p.name]:
        doc = add_node(nodes, "lineage_contract", path.stem, path.stem, "document", path)
        add_edge(edges, doc, table_nodes["market_state_table"], "guards_lineage_for", path, "INFERRED", 0.9)
        add_edge(edges, doc, table_nodes["event_state_table"], "guards_lineage_for", path, "INFERRED", 0.9)
        if "quote_guarded" in path.name:
            add_edge(edges, doc, candidate_nodes["master_intraday_bar_table_v0_2_candidate_quote_guarded"], "documents_lineage_for", path)
        if "event_windows" in path.name:
            add_edge(edges, doc, table_nodes["event_windows_table"], "documents_lineage_for", path)
        if "outcomes" in path.name:
            add_edge(edges, doc, table_nodes["outcomes_table"], "documents_lineage_for", path)

    for path in [p for p in corpus_files if "01_foundations/module_contracts/outputs" in rel(p)]:
        doc = add_node(nodes, "module_contract", path.stem, path.stem, "document", path)
        text = path.name.lower()
        add_edge(edges, outputs_node, doc, "references", path)
        if "event_candidate" in text:
            add_edge(edges, doc, table_nodes["daily_strategy_candidate_events_table"], "governs", path)
            add_edge(edges, doc, table_nodes["intraday_1m_strategy_candidate_events_table"], "governs", path)
        if "canonical_vs_representation" in text:
            add_edge(edges, doc, table_nodes["market_state_table"], "separates_canonical_from_representation", path)
            add_edge(edges, doc, table_nodes["event_state_table"], "separates_canonical_from_representation", path)
        if "state_builder" in text or "observable" in text or "formula" in text or "timestamp" in text or "snapshot" in text:
            add_edge(edges, doc, table_nodes["market_state_table"], "governs_state_builder", path, "INFERRED", 0.9)
            add_edge(edges, doc, table_nodes["event_state_table"], "governs_state_builder", path, "INFERRED", 0.9)
        if "quote_guarded_candidate" in text:
            add_edge(edges, doc, candidate_nodes["master_intraday_bar_table_v0_2_candidate_quote_guarded"], "governs", path)

    script_targets = {
        "validate_event_candidate_tables": ["daily_strategy_candidate_events_table", "intraday_1m_strategy_candidate_events_table"],
        "materialize_strategy_candidate_events_table": ["daily_strategy_candidate_events_table"],
        "materialize_daily_strategy_event_windows_candidate": ["event_windows_table"],
        "materialize_intraday_1m_strategy_candidate_events": ["intraday_1m_strategy_candidate_events_table"],
        "materialize_intraday_1m_strategy_event_windows": ["event_windows_table"],
        "materialize_master_intraday_quote_guarded": ["master_intraday_bar_table"],
        "preflight_master_intraday_quote_guarded": ["master_intraday_bar_table"],
        "materialize_market_state_intraday_quote_guarded": ["market_state_table"],
        "materialize_event_state_intraday_quote_guarded": ["event_state_table"],
        "materialize_intraday_1m_event_outcomes": ["outcomes_table"],
    }
    for path in corpus_files:
        stem = path.stem.lower()
        if path.suffix not in {".py", ".json"}:
            continue
        artifact = add_node(nodes, "artifact", path.stem, path.stem, "code" if path.suffix == ".py" else "document", path)
        for key, targets in script_targets.items():
            if key in stem:
                for target in targets:
                    add_edge(edges, artifact, table_nodes[target], "builds_or_validates", path, "INFERRED", 0.9)

    add_edge(edges, table_nodes["master_intraday_bar_table"], candidate_nodes["master_intraday_bar_table_v0_2_candidate_quote_guarded"], "feeds_candidate", source, "INFERRED", 0.9)
    add_edge(edges, candidate_nodes["master_intraday_bar_table_v0_2_candidate_quote_guarded"], candidate_nodes["market_state_table_v0_1_candidate_intraday_quote_guarded_controlled"], "feeds_candidate", source, "INFERRED", 0.9)
    add_edge(edges, candidate_nodes["master_intraday_bar_table_v0_2_candidate_quote_guarded"], candidate_nodes["intraday_1m_strategy_candidate_events_table_v0_1_candidate_quote_guarded"], "feeds_candidate", source, "INFERRED", 0.9)
    add_edge(edges, candidate_nodes["intraday_1m_strategy_candidate_events_table_v0_1_candidate_quote_guarded"], candidate_nodes["event_windows_table_v0_1_candidate_intraday_1m_quote_guarded"], "feeds_candidate", source, "INFERRED", 0.9)
    add_edge(edges, candidate_nodes["event_windows_table_v0_1_candidate_intraday_1m_quote_guarded"], candidate_nodes["event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled"], "feeds_candidate", source, "INFERRED", 0.9)
    add_edge(edges, candidate_nodes["event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled"], candidate_nodes["outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_controlled"], "post_event_outcome_candidate", source, "INFERRED", 0.9)
    add_edge(edges, candidate_nodes["daily_strategy_candidate_events_table_v0_1_candidate_controlled"], candidate_nodes["event_windows_table_v0_1_candidate_daily_strategy_events"], "feeds_candidate", source, "INFERRED", 0.9)

    extraction = {
        "nodes": dedupe_nodes(nodes),
        "edges": edges,
        "hyperedges": [
            {
                "id": "data_foundation_state_candidate_stack_20260705",
                "label": "Data Foundation State Candidate Stack 20260705",
                "nodes": [outputs_node, status_node, table_nodes["market_state_table"], table_nodes["event_state_table"], table_nodes["outcomes_table"]],
                "relation": "form",
                "confidence": "INFERRED",
                "confidence_score": 0.9,
                "source_file": str(source.resolve()),
            }
        ],
        "input_tokens": 0,
        "output_tokens": 0,
    }
    return extraction, missing


def collect_market_state_corpus() -> list[Path]:
    paths: list[Path] = []
    paths += [p for p in MARKET_STATE.rglob("*.md") if "00_privado" not in str(p) and "notebook" not in str(p)]
    paths += list((FOUNDATIONS / "module_contracts" / "outputs").glob("state_*.md"))
    paths += list((FOUNDATIONS / "module_contracts" / "outputs").glob("event_candidate*.md"))
    paths += list((FOUNDATIONS / "canonical_schemas" / "outputs").glob("*strategy_candidate_events_table_schema_contract.md"))
    paths += [
        FOUNDATIONS / "module_contracts" / "outputs" / "data_foundation_outputs_status_matrix_v0_1.md",
        FOUNDATIONS / "module_contracts" / "outputs" / "data_foundation_outputs_target_contract_v0_1.md",
        FOUNDATIONS / "module_contracts" / "outputs" / "master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md",
        CTO / "GRAPHIFY_REFRESH_QUEUE.md",
        FOUNDATIONS / "GRAPHIFY_REFRESH_QUEUE.md",
        CTO / "CHANGELOG.md",
        SMALLCAPS / "CHANGELOG.md",
        SMALLCAPS / "scripts" / "validate_event_candidate_tables.py",
    ]
    paths += list((SMALLCAPS / "scripts").glob("materialize_*candidate*.py"))
    paths += list((SMALLCAPS / "tests" / "data_foundation_outputs").glob("test_*candidate*.py"))
    return existing(paths)


def build_market_state_extraction(corpus_files: list[Path]) -> tuple[dict[str, Any], list[str]]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    missing: list[str] = []
    anchor = MARKET_STATE / "00_CTO" / "market_state_tables_status_and_operating_map_2026_07_01_v3.md"
    if not anchor.exists():
        missing.append(str(anchor))
        anchor = MARKET_STATE / "market_state_representation_contract_v0_1.md"

    concepts = {
        "canonical_state": "Canonical State",
        "representation_layer": "Representation Layer",
        "market_state_builder": "Market State Builder",
        "event_candidate_tables": "Event Candidate Tables",
        "quote_guarded_intraday_path": "Quote-Guarded Intraday Path",
        "raw_to_consumption_lineage": "Raw To Consumption Lineage",
        "daily_controlled_path": "Daily Controlled Path",
        "intraday_controlled_path": "Intraday Controlled Path",
        "outcomes_separated": "Outcomes Separated From State",
        "ml_rl_alphaevolve_disabled": "ML/RL/AlphaEvolve Production Disabled",
    }
    concept_nodes = {name: add_node(nodes, "market_state_concept", name, label, "concept", anchor) for name, label in concepts.items()}

    for path in corpus_files:
        doc = add_node(nodes, "document", rel(path), path.stem, "document" if path.suffix != ".py" else "code", path)
        text = (path.name + " " + read_text(path)[:12000]).lower()
        if "canonical" in text:
            add_edge(edges, doc, concept_nodes["canonical_state"], "defines_or_references", path, "INFERRED", 0.85)
        if "representation" in text or "alphaevolve" in text:
            add_edge(edges, doc, concept_nodes["representation_layer"], "defines_or_references", path, "INFERRED", 0.85)
        if "builder" in text or "materialize" in path.name.lower():
            add_edge(edges, doc, concept_nodes["market_state_builder"], "defines_or_references", path, "INFERRED", 0.85)
        if "event_candidate" in text or "strategy_candidate_events" in text:
            add_edge(edges, doc, concept_nodes["event_candidate_tables"], "defines_or_references", path, "INFERRED", 0.9)
        if "quote_guarded" in text or "quote-guarded" in text:
            add_edge(edges, doc, concept_nodes["quote_guarded_intraday_path"], "defines_or_references", path, "INFERRED", 0.9)
        if "raw_to_consumption" in path.name.lower() or "raw/staged" in text:
            add_edge(edges, doc, concept_nodes["raw_to_consumption_lineage"], "defines_or_references", path, "INFERRED", 0.9)
        if "daily" in text and "controlled" in text:
            add_edge(edges, doc, concept_nodes["daily_controlled_path"], "defines_or_references", path, "INFERRED", 0.8)
        if "intraday" in text and "controlled" in text:
            add_edge(edges, doc, concept_nodes["intraday_controlled_path"], "defines_or_references", path, "INFERRED", 0.8)
        if "outcome" in text or "label" in text or "reward" in text:
            add_edge(edges, doc, concept_nodes["outcomes_separated"], "defines_or_references", path, "INFERRED", 0.9)
        if "ml/rl" in text or "alphaevolve" in text or "production disabled" in text or "deshabilitado" in text:
            add_edge(edges, doc, concept_nodes["ml_rl_alphaevolve_disabled"], "defines_or_references", path, "INFERRED", 0.9)

    add_edge(edges, concept_nodes["canonical_state"], concept_nodes["representation_layer"], "separates_from", anchor, "EXTRACTED", 1.0)
    add_edge(edges, concept_nodes["raw_to_consumption_lineage"], concept_nodes["market_state_builder"], "gates", anchor, "INFERRED", 0.9)
    add_edge(edges, concept_nodes["event_candidate_tables"], concept_nodes["market_state_builder"], "feeds_state_construction", anchor, "INFERRED", 0.85)
    add_edge(edges, concept_nodes["quote_guarded_intraday_path"], concept_nodes["intraday_controlled_path"], "enables", anchor, "INFERRED", 0.9)
    add_edge(edges, concept_nodes["daily_controlled_path"], concept_nodes["event_candidate_tables"], "instantiates", anchor, "INFERRED", 0.9)
    add_edge(edges, concept_nodes["intraday_controlled_path"], concept_nodes["event_candidate_tables"], "instantiates", anchor, "INFERRED", 0.9)
    add_edge(edges, concept_nodes["outcomes_separated"], concept_nodes["canonical_state"], "must_not_be_inline_in", anchor, "EXTRACTED", 1.0)
    add_edge(edges, concept_nodes["ml_rl_alphaevolve_disabled"], concept_nodes["representation_layer"], "guards_production_boundary", anchor, "EXTRACTED", 1.0)

    extraction = {
        "nodes": dedupe_nodes(nodes),
        "edges": edges,
        "hyperedges": [
            {
                "id": "market_state_v3_route_20260705",
                "label": "Market State v3 Route 20260705",
                "nodes": list(concept_nodes.values()),
                "relation": "form",
                "confidence": "INFERRED",
                "confidence_score": 0.9,
                "source_file": str(anchor.resolve()),
            }
        ],
        "input_tokens": 0,
        "output_tokens": 0,
    }
    return extraction, missing


def label_communities(G: Any, communities: dict[int, list[str]]) -> dict[int, str]:
    labels: dict[int, str] = {}
    for cid, members in communities.items():
        text = " ".join(str(G.nodes[n].get("label", n)).lower() for n in members)
        if "quote" in text or "intraday" in text:
            labels[cid] = "Quote Guarded Intraday"
        elif "event" in text and "candidate" in text:
            labels[cid] = "Event Candidates"
        elif "lineage" in text or "raw" in text:
            labels[cid] = "State Lineage"
        elif "outcome" in text:
            labels[cid] = "Outcomes Boundary"
        elif "canonical" in text or "representation" in text:
            labels[cid] = "State Representation"
        elif "validator" in text or "test" in text:
            labels[cid] = "Validation Stack"
        elif "market_state" in text or "event_state" in text:
            labels[cid] = "Market Event State"
        else:
            labels[cid] = f"Graph Cluster {cid}"
    return labels


def write_manifest(
    leaf_id: str,
    leaf_dir: Path,
    scope: str,
    limitation: str,
    corpus: list[dict[str, Any]],
    extraction: dict[str, Any],
    diagnostics: dict[str, Any],
    missing: list[str],
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
    corpus_lines = "\n".join(f"- {item['path']} | sha256={item['sha256']} | lines={item['line_count']} | words={item['word_count']}" for item in corpus)
    missing_lines = "\n".join(f"- {item}" for item in missing) or "- none"
    dirty_block = status_short if status_short else "(clean)"
    labels_yaml = "\n".join(f"  {cid}: {label}" for cid, label in sorted(labels.items()))
    manifest = f"""# {leaf_id} Graphify Leaf Manifest

Date: {now.date().isoformat()}
Status: runtime, reconstructible Graphify leaf output.

Scope: {scope}
Leaf output: `{leaf_dir}`

## Graph Build Baseline

```yaml
graph_build_git_branch: {branch}
graph_build_git_commit: {commit}
graph_build_dirty_state: {str(dirty).lower()}
graph_build_dirty_paths_count: {len([line for line in status_short.splitlines() if line.strip()])}
graph_build_timestamp_utc: {now.isoformat()}
graphify_package_version: {importlib_metadata.version('graphifyy')}
graphify_skill_path: {skill_path}
graphify_skill_sha256: {skill_sha}
no_api_mode: true
semantic_extraction_mode: deterministic_curated_topology_extraction
build_from_json_root_or_equivalent: {REPO_ROOT}
root_graph_updated: false
queue_entries_left_pending: pending review after 20260705 leaf refresh
```

Important limitation:

```text
{limitation}
```

### Dirty Paths

```text
{dirty_block}
```

## Corpus

```text
{corpus_lines}
```

## Missing Components

```text
{missing_lines}
```

## Leaf Stats

```yaml
extraction_nodes: {len(extraction.get('nodes', []))}
extraction_edges: {len(extraction.get('edges', []))}
extraction_hyperedges: {len(extraction.get('hyperedges', []))}
nodes: {G.number_of_nodes()}
edges: {G.number_of_edges()}
communities: {len(communities)}
detected_files: {len(corpus)}
detected_words_approx: {sum(item['word_count'] for item in corpus)}
community_labels:
{labels_yaml}
```

## Diagnostic

```yaml
missing_endpoint_edges: {diagnostics.get('missing_endpoint_edges', 0)}
dangling_endpoint_edges: {diagnostics.get('dangling_endpoint_edges', 0)}
self_loop_edges: {diagnostics.get('self_loop_edges', 0)}
exact_duplicate_edges: {diagnostics.get('exact_duplicate_edges', 0)}
directed_same_endpoint_collapsed_edges: {diagnostics.get('directed_same_endpoint_collapsed_edges', 0)}
undirected_same_endpoint_collapsed_edges: {diagnostics.get('undirected_same_endpoint_collapsed_edges', 0)}
```
"""
    (leaf_dir / "BUILD_MANIFEST.md").write_text(manifest, encoding="utf-8")


def build_leaf(
    leaf_id: str,
    leaf_dir: Path,
    scope: str,
    limitation: str,
    corpus_files: list[Path],
    extraction_builder: Callable[[list[Path]], tuple[dict[str, Any], list[str]]],
    force: bool,
) -> None:
    graph_path = leaf_dir / "graph.json"
    if graph_path.exists() and not force:
        raise SystemExit(f"Refusing to overwrite existing leaf without --force: {graph_path}")
    corpus = corpus_manifest(corpus_files)
    extraction, missing = extraction_builder(corpus_files)
    detect = detection_result(corpus)
    leaf_dir.mkdir(parents=True, exist_ok=True)
    (leaf_dir / ".graphify_python").write_text(sys.executable, encoding="utf-8")
    (leaf_dir / ".graphify_root").write_text(str(REPO_ROOT), encoding="utf-8")
    (leaf_dir / "pre_manifest.json").write_text(
        json.dumps(
            {
                "run_id": leaf_id,
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "repo_root": str(REPO_ROOT),
                "leaf_dir": str(leaf_dir),
                "corpus_file_count": len(corpus),
                "graphify_package_version": importlib_metadata.version("graphifyy"),
                "semantic_extraction_mode": "deterministic_curated_topology_extraction",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (leaf_dir / "corpus_manifest.json").write_text(json.dumps(corpus, indent=2, ensure_ascii=False), encoding="utf-8")
    (leaf_dir / ".graphify_detect.json").write_text(json.dumps(detect, indent=2, ensure_ascii=False), encoding="utf-8")
    (leaf_dir / ".graphify_extract.json").write_text(json.dumps(extraction, indent=2, ensure_ascii=False), encoding="utf-8")
    diagnostics = diagnose_extraction(extraction, directed=False, root=REPO_ROOT)
    (leaf_dir / ".graphify_diagnose.json").write_text(json.dumps(diagnostics, indent=2, ensure_ascii=False), encoding="utf-8")
    (leaf_dir / "GRAPH_DIAGNOSTIC.md").write_text(format_diagnostic_report(diagnostics), encoding="utf-8")
    G = build_from_json(extraction, root=REPO_ROOT, directed=False)
    communities = cluster(G)
    cohesion = score_all(G, communities)
    labels = label_communities(G, communities)
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    questions = suggest_questions(G, communities, labels)
    commit = run_git(["rev-parse", "HEAD"]) or None
    wrote = to_json(G, communities, str(graph_path), force=force, built_at_commit=commit, community_labels=labels)
    if not wrote:
        raise SystemExit(f"Graphify refused to write graph.json for {leaf_id}")
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
    (leaf_dir / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
    (leaf_dir / ".graphify_analysis.json").write_text(
        json.dumps({"communities": {str(k): v for k, v in communities.items()}, "cohesion": {str(k): v for k, v in cohesion.items()}, "gods": gods, "surprises": surprises, "questions": questions}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (leaf_dir / ".graphify_labels.json").write_text(json.dumps({str(k): v for k, v in labels.items()}, indent=2, ensure_ascii=False), encoding="utf-8")
    to_html(G, communities, str(leaf_dir / "graph.html"), community_labels=labels)
    write_manifest(leaf_id, leaf_dir, scope, limitation, corpus, extraction, diagnostics, missing, G, communities, labels)
    print(f"Leaf complete: {leaf_id}")
    print(f"  path={leaf_dir}")
    print(f"  corpus={len(corpus)} nodes={G.number_of_nodes()} edges={G.number_of_edges()} communities={len(communities)}")
    print(f"  diagnostics missing={diagnostics.get('missing_endpoint_edges', 0)} dangling={diagnostics.get('dangling_endpoint_edges', 0)} self_loops={diagnostics.get('self_loop_edges', 0)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build TSIS project Graphify refresh leafs for 20260705.")
    parser.add_argument("--output-base", default=str(DEFAULT_OUTPUT_BASE))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--only", choices=["data", "market", "all"], default="all")
    args = parser.parse_args()
    base = Path(args.output_base)
    if args.only in {"data", "all"}:
        build_leaf(
            "data_foundation_outputs_topology_20260705",
            base / "data_foundation_outputs_topology_20260705",
            "deterministic topology of CAPA 1 outputs, state/event/outcome candidates, validators, scripts, tests and raw-to-consumption lineage",
            "This is a deterministic navigation/control graph. It maps governed filenames, contracts and explicit candidate routes; it is not a full semantic reading of every field-level rule.",
            collect_data_foundation_corpus(),
            build_data_foundation_extraction,
            args.force,
        )
    if args.only in {"market", "all"}:
        build_leaf(
            "market_state_representation_20260705",
            base / "market_state_representation_20260705",
            "Market State Representation v3 route, event candidates, quote-guarded intraday path, lineage and representation boundary",
            "This is a deterministic curated route graph. It preserves the production-disabled boundary and does not claim official state/event/outcome materialization unless the source docs do.",
            collect_market_state_corpus(),
            build_market_state_extraction,
            args.force,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
