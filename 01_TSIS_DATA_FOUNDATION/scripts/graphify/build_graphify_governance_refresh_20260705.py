from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from build_project_graphify_refresh_20260705 import (
    CTO,
    FOUNDATIONS,
    REPO_ROOT,
    SMALLCAPS,
    add_edge,
    add_node,
    build_leaf,
    dedupe_nodes,
    existing,
    read_text,
    rel,
)


def collect_governance_corpus() -> list[Path]:
    paths: list[Path] = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "START_HERE.md",
        REPO_ROOT / "PROJECT_OPERATING_SYSTEM.md",
        REPO_ROOT / "PROJECT_RULES.md",
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / "VERSIONING_STANDARDS.md",
        REPO_ROOT / "LONG_RUNNING_OPERATIONS_CONTRACT.md",
        REPO_ROOT / "RESEARCH_PHILOSOPHY.md",
        REPO_ROOT / "CHANGELOG.md",
        CTO / "README.md",
        CTO / "LOCAL_RULES.md",
        CTO / "GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md",
        CTO / "GRAPHIFY_REFRESH_QUEUE.md",
        CTO / "CHANGELOG.md",
        CTO / "TSIS_LAB_ARCHITECTURE_v3.md",
        SMALLCAPS / "README.md",
        SMALLCAPS / "AGENTS.md",
        SMALLCAPS / "LOCAL_RULES.md",
        SMALLCAPS / "CHANGELOG.md",
        FOUNDATIONS / "README.md",
        FOUNDATIONS / "LOCAL_RULES.md",
        FOUNDATIONS / "GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md",
        FOUNDATIONS / "GRAPHIFY_REFRESH_QUEUE.md",
        FOUNDATIONS / "CHANGELOG.md",
    ]
    lab_root = REPO_ROOT / "03_TSIS_Lab"
    if lab_root.exists():
        paths += list(lab_root.rglob("*.md"))
    paths += list((CTO / "01_RESEARCH_PHILOSOPHY").glob("*.md"))
    paths += list((CTO / "10_AUTONOMOUS_RESEARCH_SYSTEMS").glob("*.md"))
    paths += list((CTO / "11_MARKET_SCIENCE").glob("*.md"))
    return existing(paths)


def build_governance_extraction(corpus_files: list[Path]) -> tuple[dict[str, Any], list[str]]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    missing: list[str] = []
    anchor = REPO_ROOT / "PROJECT_OPERATING_SYSTEM.md"
    if not anchor.exists():
        missing.append(str(anchor))
        anchor = REPO_ROOT / "README.md"

    concepts = {
        "project_operating_system": "Project Operating System",
        "agent_rules": "Agent Rules",
        "versioning_standards": "Versioning Standards",
        "graphify_official_protocol": "Graphify Official Build Protocol",
        "graphify_refresh_queue": "Graphify Refresh Queue",
        "cto_architecture": "CTO Architecture",
        "data_foundation": "Data Foundation Module",
        "market_science": "Market Science",
        "research_philosophy": "Research Philosophy",
        "long_running_operations": "Long Running Operations",
        "minute_data_e_root": "Minute Data Uses E:/TSIS Root",
        "dirty_snapshot": "Dirty Working Tree Snapshot",
    }
    concept_nodes = {
        name: add_node(nodes, "governance_concept", name, label, "concept", anchor)
        for name, label in concepts.items()
    }

    for path in corpus_files:
        doc = add_node(nodes, "document", rel(path), path.stem, "document", path)
        text = (rel(path) + " " + read_text(path)[:16000]).lower()
        add_edge(edges, concept_nodes["dirty_snapshot"], doc, "includes_current_file", path, "INFERRED", 0.8)
        if "project_operating_system" in text or "operating system" in text or "start_here" in text:
            add_edge(edges, doc, concept_nodes["project_operating_system"], "defines_or_references", path, "INFERRED", 0.9)
        if "agent" in text or "local_rules" in text or "project_rules" in text:
            add_edge(edges, doc, concept_nodes["agent_rules"], "defines_or_references", path, "INFERRED", 0.9)
        if "version" in text or "semver" in text or "versioning" in text:
            add_edge(edges, doc, concept_nodes["versioning_standards"], "defines_or_references", path, "INFERRED", 0.85)
        if "graphify_official_build_protocol" in text or "official build protocol" in text:
            add_edge(edges, doc, concept_nodes["graphify_official_protocol"], "defines_or_references", path, "INFERRED", 0.95)
        if "graphify_refresh_queue" in text or "refresh queue" in text:
            add_edge(edges, doc, concept_nodes["graphify_refresh_queue"], "defines_or_references", path, "INFERRED", 0.95)
        if "architecture" in text or "00_cto" in text or "cto" in text:
            add_edge(edges, doc, concept_nodes["cto_architecture"], "defines_or_references", path, "INFERRED", 0.85)
        if "01_foundations" in text or "data foundation" in text or "foundations" in text:
            add_edge(edges, doc, concept_nodes["data_foundation"], "defines_or_references", path, "INFERRED", 0.85)
        if "market_state" in text or "market science" in text or "11_market_science" in text:
            add_edge(edges, doc, concept_nodes["market_science"], "defines_or_references", path, "INFERRED", 0.85)
        if "research philosophy" in text or "knowledge model" in text or "research_governance" in text:
            add_edge(edges, doc, concept_nodes["research_philosophy"], "defines_or_references", path, "INFERRED", 0.85)
        if "long_running" in text or "long running" in text or "heartbeat" in text or "monitor" in text:
            add_edge(edges, doc, concept_nodes["long_running_operations"], "defines_or_references", path, "INFERRED", 0.85)
        if "e:/tsis" in text or "e:\\tsis" in text or "minutos" in text or "minute" in text:
            add_edge(edges, doc, concept_nodes["minute_data_e_root"], "defines_or_references", path, "INFERRED", 0.85)

    add_edge(edges, concept_nodes["project_operating_system"], concept_nodes["agent_rules"], "governs", anchor, "EXTRACTED", 1.0)
    add_edge(edges, concept_nodes["project_operating_system"], concept_nodes["versioning_standards"], "governs", anchor, "EXTRACTED", 1.0)
    add_edge(edges, concept_nodes["graphify_official_protocol"], concept_nodes["graphify_refresh_queue"], "controls", anchor, "EXTRACTED", 1.0)
    add_edge(edges, concept_nodes["cto_architecture"], concept_nodes["market_science"], "contains_domain", anchor, "INFERRED", 0.9)
    add_edge(edges, concept_nodes["data_foundation"], concept_nodes["market_science"], "feeds", anchor, "INFERRED", 0.85)
    add_edge(edges, concept_nodes["long_running_operations"], concept_nodes["minute_data_e_root"], "protects", anchor, "INFERRED", 0.85)
    add_edge(edges, concept_nodes["dirty_snapshot"], concept_nodes["graphify_refresh_queue"], "requires_review_before_closing", anchor, "INFERRED", 0.8)

    extraction = {
        "nodes": dedupe_nodes(nodes),
        "edges": edges,
        "hyperedges": [
            {
                "id": "project_governance_refresh_20260705",
                "label": "Project Governance Refresh 20260705",
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Build TSIS governance Graphify leaf for 20260705.")
    parser.add_argument("--leaf-dir", default=str(REPO_ROOT / "graphify-out" / "leaf_slices" / "graphify_governance_20260705"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    build_leaf(
        "graphify_governance_20260705",
        Path(args.leaf_dir),
        "project operating system, agent rules, Graphify protocol, refresh queue, architecture, research governance and minute-data operating constraints",
        "This governance leaf is built against the current working tree. It does not restore deleted/moved documents; missing baseline files are recorded and the dirty snapshot is explicit in BUILD_MANIFEST.md.",
        collect_governance_corpus(),
        build_governance_extraction,
        args.force,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
