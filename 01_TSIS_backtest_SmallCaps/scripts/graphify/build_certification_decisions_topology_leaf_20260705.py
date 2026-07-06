from __future__ import annotations

import argparse
import hashlib
import json
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
CERT_ROOT = (
    REPO_ROOT
    / "01_TSIS_backtest_SmallCaps"
    / "01_research"
    / "01_auditoria_RAW_DATA"
    / "00_data_certification"
)
LEAF_DIR = CERT_ROOT / "graphify-out" / "leaf_slices" / "certification_decisions_topology_20260705"

GOVERNANCE_FILES = [
    CERT_ROOT / "GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md",
    CERT_ROOT / "GRAPHIFY_REFRESH_QUEUE.md",
    CERT_ROOT / "module_contracts" / "graphify" / "README.md",
    CERT_ROOT / "module_contracts" / "graphify" / "certification_decisions_graph_protocol.md",
]

FAMILY_ALIASES = {
    "1m": "ohlcv_1m",
    "ohlcv_1m": "ohlcv_1m",
    "additional": "additional",
    "daily": "daily",
    "global_metrics": "global_metrics",
    "halts": "halts",
    "quotes": "quotes",
    "reference": "reference",
    "short": "short",
    "trades": "trades",
}

DECISION_KEYWORDS = {
    "expected": "Expected State",
    "present": "Present State",
    "healthy": "Healthy State",
    "usable_for": "Usable For State",
    "recovery": "Recovery Decision",
    "recoverable": "Recoverable Bucket",
    "exclusion": "Exclusion Decision",
    "excluded": "Exclusion Decision",
    "good": "Good Bucket",
    "review": "Review Bucket",
    "bad": "Bad Bucket",
    "closeout": "Closeout Decision",
    "policy": "Certification Policy",
}


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


def make_id(kind: str, name: str) -> str:
    return f"certification_decisions_{norm(kind)}_{norm(name)}"


def add_node(nodes: dict[str, dict[str, Any]], kind: str, name: str, label: str, file_type: str, source_file: Path) -> str:
    nid = make_id(kind, name)
    nodes[nid] = {
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


def collect_corpus() -> list[Path]:
    files: dict[str, Path] = {}
    for path in GOVERNANCE_FILES:
        if path.exists():
            files[str(path.resolve()).lower()] = path

    cert_dir = CERT_ROOT / "certification"
    if cert_dir.exists():
        for path in cert_dir.glob("**/*.md"):
            files[str(path.resolve()).lower()] = path
        global_metrics = cert_dir / "global_metrics"
        if global_metrics.exists():
            for path in global_metrics.glob("*.json"):
                files[str(path.resolve()).lower()] = path

    audit_dir = CERT_ROOT / "auditoria"
    if audit_dir.exists():
        patterns = ("closeout", "policy", "contrato")
        for path in audit_dir.glob("**/*.md"):
            lowered = path.name.lower()
            if any(pattern in lowered for pattern in patterns):
                files[str(path.resolve()).lower()] = path

    return sorted(files.values(), key=lambda p: rel(p).lower())


def infer_family(path: Path) -> str | None:
    try:
        parts = path.relative_to(CERT_ROOT).parts
    except ValueError:
        return None
    if not parts:
        return None
    if parts[0] == "certification" and len(parts) > 1:
        return FAMILY_ALIASES.get(parts[1].lower())
    if parts[0] == "auditoria" and len(parts) > 1:
        return FAMILY_ALIASES.get(parts[1].lower())
    return None


def infer_doc_type(path: Path) -> str:
    name = path.name.lower()
    if "closeout" in name:
        return "closeout"
    if "policy" in name:
        return "policy"
    if "contrato" in name or "contract" in name:
        return "contract"
    if "metrics" in name or path.suffix.lower() == ".json":
        return "global_metrics"
    if "current_state" in name:
        return "current_state"
    if "recovery" in name:
        return "recovery"
    if "graphify" in rel(path).lower():
        return "graphify_governance"
    return "certification_document"


def corpus_manifest(files: list[Path]) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        manifest.append(
            {
                "path": rel(path),
                "absolute_path": str(path.resolve()),
                "sha256": sha256_file(path),
                "line_count": text.count("\n") + (1 if text else 0),
                "word_count": count_words(text),
                "bytes": path.stat().st_size,
                "family": infer_family(path),
                "doc_type": infer_doc_type(path),
            }
        )
    return manifest


def build_extraction(files: list[Path]) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    protocol = CERT_ROOT / "module_contracts" / "graphify" / "certification_decisions_graph_protocol.md"
    root = add_node(nodes, "root", "certification_decisions_topology", "Certification Decisions Topology", "concept", protocol)
    graph_protocol = add_node(nodes, "protocol", "certification_decisions_graph_protocol", "Certification Decisions Graph Protocol", "document", protocol)
    graphify_protocol = add_node(nodes, "protocol", "graphify_official_build", "00 Data Certification Graphify Official Build Protocol", "document", CERT_ROOT / "GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md")
    refresh_queue = add_node(nodes, "queue", "graphify_refresh_queue", "00 Data Certification Graphify Refresh Queue", "document", CERT_ROOT / "GRAPHIFY_REFRESH_QUEUE.md")

    add_edge(edges, graph_protocol, root, "implements", protocol)
    add_edge(edges, graphify_protocol, root, "rationale_for", CERT_ROOT / "GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md", "INFERRED", 0.85)
    add_edge(edges, refresh_queue, root, "references", CERT_ROOT / "GRAPHIFY_REFRESH_QUEUE.md")

    family_nodes: dict[str, str] = {}
    doc_type_nodes: dict[str, str] = {}
    decision_nodes: dict[str, str] = {}

    def family_node(family: str) -> str:
        if family not in family_nodes:
            family_nodes[family] = add_node(nodes, "family", family, family, "concept", protocol)
            add_edge(edges, root, family_nodes[family], "references", protocol, "INFERRED", 0.85)
        return family_nodes[family]

    def doc_type_node(doc_type: str) -> str:
        if doc_type not in doc_type_nodes:
            doc_type_nodes[doc_type] = add_node(nodes, "doc_type", doc_type, doc_type, "concept", protocol)
            add_edge(edges, graph_protocol, doc_type_nodes[doc_type], "references", protocol, "INFERRED", 0.85)
        return doc_type_nodes[doc_type]

    def decision_node(keyword: str, label: str) -> str:
        if keyword not in decision_nodes:
            decision_nodes[keyword] = add_node(nodes, "decision", keyword, label, "concept", protocol)
            add_edge(edges, graph_protocol, decision_nodes[keyword], "references", protocol, "INFERRED", 0.85)
        return decision_nodes[keyword]

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        rel_path = rel(path)
        family = infer_family(path)
        doc_type = infer_doc_type(path)
        label = path.stem.replace("_", " ").replace("-", " ").title()
        doc = add_node(nodes, "document", rel_path, label, "document", path)
        add_edge(edges, root, doc, "references", path)
        add_edge(edges, doc_type_node(doc_type), doc, "references", path)
        if family:
            add_edge(edges, family_node(family), doc, "references", path)
        lowered = text.lower()
        for keyword, decision_label in DECISION_KEYWORDS.items():
            if keyword in lowered or keyword in path.name.lower():
                add_edge(edges, doc, decision_node(keyword, decision_label), "references", path)

    if "global_metrics" in family_nodes:
        add_edge(edges, family_nodes["global_metrics"], root, "conceptually_related_to", protocol, "INFERRED", 0.85)

    hyperedges = []
    for family, family_id in sorted(family_nodes.items()):
        family_docs = [
            edge["target"]
            for edge in edges
            if edge["source"] == family_id and edge["relation"] == "references"
        ]
        if len(family_docs) >= 2:
            hyperedges.append(
                {
                    "id": f"certification_family_stack_{norm(family)}",
                    "label": f"{family} Certification Evidence Stack",
                    "nodes": [family_id, *family_docs[:8]],
                    "relation": "form",
                    "confidence": "INFERRED",
                    "confidence_score": 0.85,
                    "source_file": str(protocol.resolve()),
                }
            )

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "hyperedges": hyperedges[:12],
        "input_tokens": 0,
        "output_tokens": 0,
    }


def detection_result(corpus: list[dict[str, Any]]) -> dict[str, Any]:
    files = [item["absolute_path"] for item in corpus]
    return {
        "scan_root": str(CERT_ROOT.resolve()),
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
        if "quotes" in text:
            labels[cid] = "Quotes Certification"
        elif "trades" in text:
            labels[cid] = "Trades Certification"
        elif "global metrics" in text or "global_metrics" in text:
            labels[cid] = "Global Metrics"
        elif "graphify" in text or "protocol" in text or "queue" in text:
            labels[cid] = "Graphify Governance"
        elif "daily" in text:
            labels[cid] = "Daily Certification"
        elif "halts" in text:
            labels[cid] = "Halts Certification"
        elif "reference" in text:
            labels[cid] = "Reference Certification"
        elif "short" in text:
            labels[cid] = "Short Certification"
        elif "additional" in text:
            labels[cid] = "Additional Certification"
        elif "ohlcv" in text or "1m" in text:
            labels[cid] = "1m Certification"
        else:
            labels[cid] = f"Certification Cluster {cid}"
    return labels


def write_manifest(
    corpus: list[dict[str, Any]],
    extraction: dict[str, Any],
    diagnostics: dict[str, Any],
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
        f"- {item['path']} | sha256={item['sha256']} | family={item['family']} | doc_type={item['doc_type']} | words={item['word_count']}"
        for item in corpus
    )
    labels_yaml = "\n".join(f"  {cid}: {label}" for cid, label in sorted(labels.items()))
    dirty_block = status_short if status_short else "(clean)"

    manifest = f"""# Certification Decisions Topology Graphify Leaf Manifest

Date: {now.date().isoformat()}
Status: runtime, reconstructible Graphify leaf output.

Scope: deterministic topology refresh for `00_data_certification` certification decisions.
Leaf output: `{LEAF_DIR}`

## Graph Build Baseline

```yaml
graph_build_git_branch: {branch}
graph_build_git_commit: {commit}
graph_build_dirty_state: {str(dirty).lower()}
graph_build_timestamp_utc: {now.isoformat()}
graphify_package_version: {importlib_metadata.version("graphifyy")}
graphify_skill_path: {skill_path}
graphify_skill_sha256: {skill_sha}
graphify_upstream_reference: https://github.com/safishamsi/graphify
graphify_installed_vs_protocol_status: aligned_to_0_9_1_before_build
no_api_mode: true
semantic_extraction_mode: deterministic_certification_decision_topology
build_from_json_root_or_equivalent: {REPO_ROOT}
semantic_update_coverage: controlled_certification_decisions_topology
corpus_manifest_path: {LEAF_DIR / "corpus_manifest.json"}
corpus_file_count: {len(corpus)}
queue_entries_covered:
  - GFQ-20260628-002 graphify no-API and version-alignment protocol
  - GFQ-20260628-001 graphify build baseline provenance rule
queue_entries_left_pending:
  - full semantic refresh of certification_decisions_graph if field-level/case-level reasoning is required
diagnostics_command: graphify diagnose multigraph --graph "{LEAF_DIR / "graph.json"}" --json
next_delta_commands:
  - git diff --name-status {commit}...HEAD
  - git status --short
```

Important limitation:

```text
This leaf is a deterministic topology refresh. It maps families, documents,
doc types and explicit decision keywords from the controlled certification
corpus. It does not replace the 2026-06-19 semantic certification decisions
leaf and must not be presented as a full semantic re-extraction of every
closeout/policy body.
```

### Dirty Paths

```text
{dirty_block}
```

## Corpus

Inclusion rules:

```text
- certification/**/*.md
- certification/global_metrics/*.json
- auditoria/**/*closeout*.md
- auditoria/**/*policy*.md
- auditoria/**/*contrato*.md
- local Graphify governance docs
```

Exclusion rules:

```text
- graphify-out/
- notebooks
- parquet/csv
- images
- runtime/cache folders
- physical evidence assets
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
"""
    (LEAF_DIR / "BUILD_MANIFEST.md").write_text(manifest, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build certification decisions topology Graphify leaf.")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    graph_path = LEAF_DIR / "graph.json"
    if graph_path.exists() and not args.force:
        print(f"Refusing to overwrite existing leaf without --force: {graph_path}", file=sys.stderr)
        return 2

    files = collect_corpus()
    corpus = corpus_manifest(files)
    extraction = build_extraction(files)
    detect = detection_result(corpus)

    LEAF_DIR.mkdir(parents=True, exist_ok=True)
    (LEAF_DIR / ".graphify_python").write_text(sys.executable, encoding="utf-8")
    (LEAF_DIR / ".graphify_root").write_text(str(REPO_ROOT), encoding="utf-8")
    (LEAF_DIR / "pre_manifest.json").write_text(
        json.dumps(
            {
                "run_id": "certification_decisions_topology_20260705",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "repo_root": str(REPO_ROOT),
                "cert_root": str(CERT_ROOT),
                "leaf_dir": str(LEAF_DIR),
                "corpus_file_count": len(corpus),
                "graphify_package_version": importlib_metadata.version("graphifyy"),
                "semantic_extraction_mode": "deterministic_certification_decision_topology",
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
    write_manifest(corpus, extraction, diagnostics, G, communities, labels)

    print(f"Leaf complete: {LEAF_DIR}")
    print(f"Corpus files: {len(corpus)}")
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities")
    print(f"Diagnostics: missing={diagnostics.get('missing_endpoint_edges', 0)} dangling={diagnostics.get('dangling_endpoint_edges', 0)} self_loops={diagnostics.get('self_loop_edges', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

