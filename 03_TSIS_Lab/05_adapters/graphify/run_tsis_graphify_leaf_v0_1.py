#!/usr/bin/env python
"""Governed three-phase Graphify leaf builder for TSIS."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import importlib.metadata
import json
import os
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.build import build_from_json
from graphify.cache import check_semantic_cache, save_semantic_cache
from graphify.cluster import cluster, score_all
from graphify.detect import classify_file, count_words, save_manifest
from graphify.diagnostics import diagnose_extraction, format_diagnostic_report
from graphify.export import to_html, to_json
from graphify.extract import extract
from graphify.report import generate

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PLAN = SCRIPT_DIR / "tsis_graphify_refresh_plan_v0_1.json"
BUILDER_ID = "run_tsis_graphify_leaf_v0_1"
FINAL_FILES = [
    "graph.json", "GRAPH_REPORT.md", "graph.html", "BUILD_MANIFEST.md",
    "corpus_manifest.json", "manifest.json", "cost.json",
    "GRAPH_DIAGNOSTIC.md", "GRAPH_DIAGNOSTIC.json", ".graphify_detect.json",
    ".graphify_extract.json", ".graphify_analysis.json", ".graphify_labels.json",
    ".graphify_python", ".graphify_root",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git_value(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=False)
    return p.stdout.strip() if p.returncode == 0 else f"ERROR:{p.stderr.strip()}"


def plan_target(plan: dict, target_id: str) -> dict:
    for target in plan["targets"]:
        if target["target_id"] == target_id:
            return target
    raise KeyError(f"Unknown target_id: {target_id}")


def matched(rel: str, patterns: list[str]) -> bool:
    value = rel.replace("\\", "/")
    expanded: set[str] = set()
    pending = [p.replace("\\", "/").lower() for p in patterns]
    while pending:
        pattern = pending.pop()
        if pattern in expanded:
            continue
        expanded.add(pattern)
        if pattern.startswith("**/"):
            pending.append(pattern[3:])
        if "/**/" in pattern:
            pending.append(pattern.replace("/**/", "/", 1))
    return any(fnmatch.fnmatch(value.lower(), pattern) for pattern in expanded)


def collect_corpus(target: dict, repo_root: Path) -> tuple[dict, list[dict]]:
    selected: dict[str, tuple[Path, str]] = {}
    for source in target["sources"]:
        root = Path(source["root"])
        if root.is_file():
            candidates = [root]
        else:
            candidates_by_path: dict[str, Path] = {}
            for pattern in source.get("include", ["**/*"]):
                for candidate in root.glob(pattern):
                    if candidate.is_file():
                        candidates_by_path[str(candidate.resolve()).lower()] = candidate
            candidates = candidates_by_path.values()
        for path in candidates:
            if not path.is_file():
                continue
            rel = path.name if root.is_file() else path.relative_to(root).as_posix()
            if not matched(rel, source.get("include", ["**/*"])):
                continue
            if matched(rel, source.get("exclude", [])):
                continue
            kind = classify_file(path)
            if kind is None:
                continue
            selected[str(path.resolve()).lower()] = (path.resolve(), kind.value)

    files: dict[str, list[str]] = {}
    manifest: list[dict] = []
    total_words = 0
    for path, kind in sorted(selected.values(), key=lambda x: str(x[0]).lower()):
        words = count_words(path)
        total_words += words
        files.setdefault(kind, []).append(str(path))
        try:
            repo_rel = path.relative_to(repo_root).as_posix()
        except ValueError:
            repo_rel = str(path)
        manifest.append({
            "path": repo_rel,
            "absolute_path": str(path),
            "category": kind,
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "word_count": words,
        })
    detection = {
        "scan_root": str(repo_root),
        "files": files,
        "all_files": files,
        "total_files": len(manifest),
        "total_words": total_words,
        "skipped_sensitive": [],
        "needs_graph": True,
    }
    return detection, manifest


def paths(plan: dict, target: dict, run_id: str) -> tuple[Path, Path, Path]:
    run_root = Path(plan["run_base"]) / run_id / target["target_id"]
    output = run_root / "staging" / "graphify-out"
    monitor = run_root / "monitor"
    return run_root, output, monitor


def heartbeat(monitor: Path, **values: object) -> None:
    payload = {"observed_at_utc": now(), "pid": os.getpid(), **values}
    write_json(monitor / "heartbeat_latest.json", payload)
    monitor.mkdir(parents=True, exist_ok=True)
    with (monitor / "heartbeat.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def base_manifest(plan: dict, target: dict, run_id: str, run_root: Path, output: Path) -> dict:
    repo = Path(plan["repo_root"])
    spec = Path(plan["extraction_spec"])
    return {
        "run_id": run_id,
        "target_id": target["target_id"],
        "builder_id": BUILDER_ID,
        "strategy": target["strategy"],
        "created_at_utc": now(),
        "host": socket.gethostname(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "repo_root": str(repo),
        "git_branch": git_value(repo, "branch", "--show-current"),
        "git_commit": git_value(repo, "rev-parse", "HEAD"),
        "git_status_at_start": git_value(repo, "status", "--short"),
        "graphify_version": importlib.metadata.version("graphifyy"),
        "graphify_python": sys.executable,
        "extraction_spec": str(spec),
        "extraction_spec_sha256": sha256(spec),
        "semantic_mode": "codex_subagents_no_external_api",
        "run_root": str(run_root),
        "staging_output": str(output),
        "publish_dir": target["publish_dir"],
        "expected_artifacts": FINAL_FILES,
        "monitor_command": f'python "{SCRIPT_DIR / "monitor_tsis_graphify_refresh_v0_1.py"}" --run-root "{run_root}" --watch',
        "safe_stop": "Stop only the active phase process. Published outputs are untouched until publish phase.",
    }


def prepare(plan: dict, target: dict, run_id: str) -> int:
    repo = Path(plan["repo_root"])
    run_root, output, monitor = paths(plan, target, run_id)
    output.mkdir(parents=True, exist_ok=True)
    pre = base_manifest(plan, target, run_id, run_root, output)
    write_json(monitor / "pre_manifest.json", {**pre, "status": "preparing"})
    write_json(monitor / "pid_manifest.json", {"run_id": run_id, "target_id": target["target_id"], "pid": os.getpid(), "phase": "prepare", "created_at_utc": now()})
    heartbeat(monitor, status="running", stage="corpus_detection", target_id=target["target_id"], detail="collecting curated corpus")
    detection, corpus = collect_corpus(target, repo)
    if not corpus:
        raise RuntimeError("Curated corpus is empty")
    write_json(output / ".graphify_detect.json", detection)
    write_json(output / "corpus_manifest.json", corpus)
    (output / ".graphify_python").write_text(sys.executable, encoding="utf-8")
    (output / ".graphify_root").write_text(str(repo), encoding="utf-8")

    code_files = [Path(p) for p in detection["files"].get("code", [])]
    heartbeat(monitor, status="running", stage="ast_extraction", target_id=target["target_id"], files=len(corpus), code_files=len(code_files), detail="Graphify AST extraction")
    ast = extract(code_files, cache_root=repo, root=repo, parallel=True, max_workers=int(plan.get("max_ast_workers", 6))) if code_files else {"nodes": [], "edges": [], "input_tokens": 0, "output_tokens": 0}
    write_json(output / ".graphify_ast.json", ast)

    semantic_files = [p for k in ("document", "paper", "image") for p in detection["files"].get(k, [])]
    cache_root = Path(target.get("semantic_cache_root", target["publish_dir"]))
    cached_nodes, cached_edges, cached_hyperedges, uncached = check_semantic_cache(
        semantic_files, root=repo, prompt_file=plan["extraction_spec"], cache_root=cache_root
    )
    write_json(output / ".graphify_cached.json", {"nodes": cached_nodes, "edges": cached_edges, "hyperedges": cached_hyperedges})

    images = {str(Path(p).resolve()).lower() for p in detection["files"].get("image", [])}
    normal = sorted([p for p in uncached if str(Path(p).resolve()).lower() not in images], key=lambda p: (str(Path(p).parent).lower(), str(p).lower()))
    chunks: list[list[str]] = []
    size = int(plan.get("semantic_chunk_size", 22))
    for i in range(0, len(normal), size):
        chunks.append(normal[i:i + size])
    chunks.extend([[p] for p in uncached if str(Path(p).resolve()).lower() in images])
    chunk_dir = run_root / "chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)
    chunk_plan = []
    for index, items in enumerate(chunks, 1):
        chunk_plan.append({
            "chunk_num": index,
            "total_chunks": len(chunks),
            "files": items,
            "output_path": str(chunk_dir / f"chunk_{index:04d}.json"),
            "deep_mode": True,
        })
    write_json(run_root / "chunk_plan.json", {"target_id": target["target_id"], "extraction_spec": plan["extraction_spec"], "chunks": chunk_plan})
    status = "waiting_semantic_extraction" if chunks else "ready_to_assemble"
    heartbeat(monitor, status=status, stage="prepare_complete", target_id=target["target_id"], files=len(corpus), code_files=len(code_files), semantic_files=len(semantic_files), chunks_complete=0, chunks_total=len(chunks), nodes=len(ast.get("nodes", [])), edges=len(ast.get("edges", [])), detail=f"cache_hits={len(semantic_files)-len(uncached)}")
    return 0


def load_chunks(run_root: Path) -> dict:
    plan = read_json(run_root / "chunk_plan.json")
    nodes: list[dict] = []
    edges: list[dict] = []
    hyperedges: list[dict] = []
    input_tokens = 0
    output_tokens = 0
    missing = []
    for chunk in plan["chunks"]:
        path = Path(chunk["output_path"])
        if not path.exists():
            missing.append(str(path))
            continue
        data = read_json(path)
        if not isinstance(data.get("nodes"), list) or not isinstance(data.get("edges"), list):
            raise RuntimeError(f"Invalid semantic chunk: {path}")
        nodes.extend(data["nodes"])
        edges.extend(data["edges"])
        hyperedges.extend(data.get("hyperedges", []))
        input_tokens += int(data.get("input_tokens", 0) or 0)
        output_tokens += int(data.get("output_tokens", 0) or 0)
    if missing:
        raise RuntimeError("Missing semantic chunks:\n" + "\n".join(missing))
    return {"nodes": nodes, "edges": edges, "hyperedges": hyperedges, "input_tokens": input_tokens, "output_tokens": output_tokens}


def assemble(plan: dict, target: dict, run_id: str) -> int:
    repo = Path(plan["repo_root"])
    run_root, output, monitor = paths(plan, target, run_id)
    write_json(monitor / "pid_manifest.json", {"run_id": run_id, "target_id": target["target_id"], "pid": os.getpid(), "phase": "assemble", "created_at_utc": now()})
    chunk_plan = read_json(run_root / "chunk_plan.json")
    done = sum(Path(c["output_path"]).exists() for c in chunk_plan["chunks"])
    heartbeat(monitor, status="running", stage="semantic_assembly", target_id=target["target_id"], chunks_complete=done, chunks_total=len(chunk_plan["chunks"]), detail="validating chunks")
    new = load_chunks(run_root)
    cached = read_json(output / ".graphify_cached.json")
    semantic = {
        "nodes": cached.get("nodes", []) + new["nodes"],
        "edges": cached.get("edges", []) + new["edges"],
        "hyperedges": cached.get("hyperedges", []) + new["hyperedges"],
        "input_tokens": new["input_tokens"],
        "output_tokens": new["output_tokens"],
    }
    seen: set[str] = set()
    semantic["nodes"] = [n for n in semantic["nodes"] if not (n.get("id") in seen or seen.add(n.get("id")))]
    write_json(output / ".graphify_semantic.json", semantic)
    save_semantic_cache(new["nodes"], new["edges"], new["hyperedges"], root=repo, merge_existing=True, allowed_source_files=[p for c in chunk_plan["chunks"] for p in c["files"]], prompt_file=plan["extraction_spec"], cache_root=output)

    ast = read_json(output / ".graphify_ast.json")
    merged_nodes = list(ast.get("nodes", []))
    seen = {n.get("id") for n in merged_nodes}
    merged_nodes.extend(n for n in semantic["nodes"] if n.get("id") not in seen and not seen.add(n.get("id")))
    extraction = {"nodes": merged_nodes, "edges": ast.get("edges", []) + semantic["edges"], "hyperedges": semantic["hyperedges"], "input_tokens": semantic["input_tokens"], "output_tokens": semantic["output_tokens"]}
    write_json(output / ".graphify_extract.json", extraction)

    diag = diagnose_extraction(extraction, directed=False, root=repo)
    write_json(output / "GRAPH_DIAGNOSTIC.json", diag)
    (output / "GRAPH_DIAGNOSTIC.md").write_text(format_diagnostic_report(diag), encoding="utf-8")
    G = build_from_json(extraction, root=repo, directed=False)
    if G.number_of_nodes() == 0:
        raise RuntimeError("Graphify produced an empty graph")
    communities = cluster(G)
    cohesion = score_all(G, communities)
    labels = {cid: f"Community {cid}" for cid in communities}
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    questions = suggest_questions(G, communities, labels)
    analysis = {"communities": {str(k): v for k, v in communities.items()}, "cohesion": {str(k): v for k, v in cohesion.items()}, "gods": gods, "surprises": surprises, "questions": questions}
    write_json(output / ".graphify_analysis.json", analysis)
    to_json(G, communities, str(output / "graph.json"), force=True, built_at_commit=git_value(repo, "rev-parse", "HEAD"), community_labels=labels)

    degree = dict(G.degree())
    community_plan = []
    for cid, members in communities.items():
        ranked = sorted(members, key=lambda n: degree.get(n, 0), reverse=True)[:15]
        community_plan.append({"community_id": cid, "member_count": len(members), "cohesion": cohesion.get(cid), "top_nodes": [{"id": n, "label": G.nodes[n].get("label", n), "source_file": G.nodes[n].get("source_file")} for n in ranked]})
    write_json(run_root / "community_label_plan.json", {"target_id": target["target_id"], "instruction": "Assign one specific 2-5 word label per community. Do not use Community N.", "communities": community_plan, "output_path": str(run_root / "community_labels.json")})
    heartbeat(monitor, status="waiting_community_labels", stage="assemble_complete", target_id=target["target_id"], chunks_complete=len(chunk_plan["chunks"]), chunks_total=len(chunk_plan["chunks"]), nodes=G.number_of_nodes(), edges=G.number_of_edges(), detail=f"communities={len(communities)}")
    return 0


def build_manifest_text(pre: dict, target: dict, corpus_count: int, G, communities: dict, diag: dict) -> str:
    return f"""# Graphify Build Manifest\n\n- status: ACCEPTED\n- target_id: {target['target_id']}\n- strategy: {target['strategy']}\n- built_at_utc: {now()}\n- git_branch: {pre['git_branch']}\n- git_commit: {pre['git_commit']}\n- graphify_version: {pre['graphify_version']}\n- graphify_python: {pre['graphify_python']}\n- extraction_spec: {pre['extraction_spec']}\n- extraction_spec_sha256: {pre['extraction_spec_sha256']}\n- semantic_mode: {pre['semantic_mode']}\n- corpus_files: {corpus_count}\n- nodes: {G.number_of_nodes()}\n- edges: {G.number_of_edges()}\n- communities: {len(communities)}\n- queue_ids: {', '.join(target.get('queue_ids', []))}\n- forbidden_source_substrings: {', '.join(target.get('forbidden_source_substrings', []))}\n- dangling_endpoint_edges: {diag.get('dangling_endpoint_edges', 0)}\n- missing_endpoint_edges: {diag.get('missing_endpoint_edges', 0)}\n- self_loop_edges: {diag.get('self_loop_edges', 0)}\n- collapsed_edges: {diag.get('undirected_same_endpoint_collapsed_edges', 0)}\n\n## Next delta\n\nUse the official Graphify incremental flow only if the corpus identity and source root remain compatible. Otherwise create a new full-rebuild leaf.\n"""


def publish_copy(output: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for name in FINAL_FILES:
        src = output / name
        if not src.exists():
            raise RuntimeError(f"Expected publication artifact missing: {src}")
        dst = destination / name
        tmp = destination / (name + ".tmp")
        shutil.copy2(src, tmp)
        os.replace(tmp, dst)
    if (output / "cache").exists():
        shutil.copytree(output / "cache", destination / "cache", dirs_exist_ok=True)


def publish(plan: dict, target: dict, run_id: str) -> int:
    repo = Path(plan["repo_root"])
    run_root, output, monitor = paths(plan, target, run_id)
    labels_path = run_root / "community_labels.json"
    if not labels_path.exists():
        raise RuntimeError(f"Missing governed community labels: {labels_path}")
    labels_raw = read_json(labels_path)
    labels = {int(k): str(v) for k, v in labels_raw.items()}
    analysis = read_json(output / ".graphify_analysis.json")
    communities = {int(k): v for k, v in analysis["communities"].items()}
    missing_labels = sorted(set(communities) - set(labels))
    if missing_labels:
        raise RuntimeError(f"Missing labels for communities: {missing_labels}")
    write_json(monitor / "pid_manifest.json", {"run_id": run_id, "target_id": target["target_id"], "pid": os.getpid(), "phase": "publish", "created_at_utc": now()})
    heartbeat(monitor, status="running", stage="terminal_certification", target_id=target["target_id"], detail="rebuilding labeled outputs")

    extraction = read_json(output / ".graphify_extract.json")
    detection = read_json(output / ".graphify_detect.json")
    corpus = read_json(output / "corpus_manifest.json")
    diag = diagnose_extraction(extraction, directed=False, root=repo)
    gate_keys = ["non_object_edges", "missing_endpoint_edges", "self_loop_edges"]
    bad = {k: diag.get(k, 0) for k in gate_keys if diag.get(k, 0)}
    node_ids = {str(node.get("id")) for node in extraction.get("nodes", []) if node.get("id")}
    non_import_dangling = [
        edge for edge in extraction.get("edges", [])
        if (str(edge.get("source")) not in node_ids or str(edge.get("target")) not in node_ids)
        and not (
            str(edge.get("relation", "")).lower() in {"imports", "imports_from"}
            or (
                str(edge.get("relation", "")).lower() == "references"
                and str(edge.get("target", "")).startswith("ref_defs_")
                and str(edge.get("source_file", "")).lower().endswith((".json", ".yaml", ".yml"))
            )
            or (
                str(edge.get("relation", "")).lower() == "depends_on"
                and str(edge.get("target", "")).startswith("pkg_")
                and str(edge.get("source_file", "")).lower().endswith(("pyproject.toml", "requirements.txt"))
            )
        )
    ]
    if non_import_dangling:
        bad["non_import_dangling_edges"] = len(non_import_dangling)
    if diag.get("post_build_error"):
        bad["post_build_error"] = diag["post_build_error"]
    if bad:
        heartbeat(monitor, status="blocked", stage="diagnostic_gate", target_id=target["target_id"], detail=str(bad))
        raise RuntimeError(f"Graph diagnostic gate failed: {bad}")
    source_files = [
        str(item.get("source_file")).replace("\\", "/")
        for collection in ("nodes", "edges", "hyperedges")
        for item in extraction.get(collection, [])
        if item.get("source_file")
    ]
    source_text = "\n".join(source_files).lower()
    forbidden = [s for s in target.get("forbidden_source_substrings", []) if s.replace("\\", "/").lower() in source_text]
    if forbidden:
        heartbeat(monitor, status="blocked", stage="legacy_path_gate", target_id=target["target_id"], detail=str(forbidden))
        raise RuntimeError(f"Forbidden legacy source paths remain: {forbidden}")

    G = build_from_json(extraction, root=repo, directed=False)
    cohesion = score_all(G, communities)
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    questions = suggest_questions(G, communities, labels)
    commit = git_value(repo, "rev-parse", "HEAD")
    to_json(G, communities, str(output / "graph.json"), force=True, built_at_commit=commit, community_labels=labels)
    report = generate(G, communities, cohesion, labels, gods, surprises, detection, {"input": extraction.get("input_tokens", 0), "output": extraction.get("output_tokens", 0)}, str(repo), suggested_questions=questions, built_at_commit=commit)
    (output / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
    to_html(G, communities, str(output / "graph.html"), community_labels=labels)
    write_json(output / ".graphify_labels.json", {str(k): v for k, v in labels.items()})
    write_json(output / "GRAPH_DIAGNOSTIC.json", diag)
    (output / "GRAPH_DIAGNOSTIC.md").write_text(format_diagnostic_report(diag), encoding="utf-8")
    save_manifest(detection["files"], str(output / "manifest.json"), kind="both", root=repo)
    write_json(output / "cost.json", {"input_tokens": extraction.get("input_tokens", 0), "output_tokens": extraction.get("output_tokens", 0), "files": len(corpus), "built_at_utc": now()})
    pre = read_json(monitor / "pre_manifest.json")
    (output / "BUILD_MANIFEST.md").write_text(build_manifest_text(pre, target, len(corpus), G, communities, diag), encoding="utf-8")

    publish_copy(output, Path(target["publish_dir"]))
    for mirror in target.get("mirror_dirs", []):
        publish_copy(output, Path(mirror))
    final = {**pre, "status": "complete", "finished_at_utc": now(), "corpus_files": len(corpus), "nodes": G.number_of_nodes(), "edges": G.number_of_edges(), "communities": len(communities), "diagnostics": diag, "published_to": [target["publish_dir"], *target.get("mirror_dirs", [])]}
    write_json(monitor / "final_manifest.json", final)
    heartbeat(monitor, status="complete", stage="published", target_id=target["target_id"], files=len(corpus), nodes=G.number_of_nodes(), edges=G.number_of_edges(), detail=target["publish_dir"])
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("phase", choices=["prepare", "assemble", "publish"])
    ap.add_argument("--target-id", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--plan", default=str(DEFAULT_PLAN))
    args = ap.parse_args()
    plan = read_json(Path(args.plan))
    target = plan_target(plan, args.target_id)
    try:
        return {"prepare": prepare, "assemble": assemble, "publish": publish}[args.phase](plan, target, args.run_id)
    except Exception as exc:
        run_root, _, monitor = paths(plan, target, args.run_id)
        heartbeat(monitor, status="failed", stage=args.phase, target_id=target["target_id"], detail=repr(exc))
        pre = read_json(monitor / "pre_manifest.json") if (monitor / "pre_manifest.json").exists() else {"run_id": args.run_id, "target_id": target["target_id"]}
        write_json(monitor / "final_manifest.json", {**pre, "status": "failed", "failed_at_utc": now(), "phase": args.phase, "error": repr(exc)})
        raise


if __name__ == "__main__":
    raise SystemExit(main())

