from __future__ import annotations

from pathlib import Path


ROOT = Path(r"C:\TSIS_Data")
MARKER = "TSIS_GRAPHIFY_TERMINAL_ACCEPTANCE_20260822"
CHANGE_MARKER = "TSIS_GRAPHIFY_REFRESH_20260822"
QUEUE_MARKER = "TSIS_GRAPHIFY_QUEUE_RESOLUTION_20260822"


def append_once(path: Path, marker: str, block: str) -> None:
    current = path.read_text(encoding="utf-8-sig")
    if marker in current:
        raise RuntimeError(f"Marker already present in {path}: {marker}")
    separator = "" if current.endswith("\n") else "\n"
    path.write_text(current + separator + "\n" + block.rstrip() + "\n", encoding="utf-8")


def prepend_once(path: Path, marker: str, block: str) -> None:
    current = path.read_text(encoding="utf-8-sig")
    if marker in current:
        raise RuntimeError(f"Marker already present in {path}: {marker}")
    path.write_text(block.rstrip() + "\n\n" + current, encoding="utf-8")


MANIFESTS = {
    ROOT / "graphify-out" / "BUILD_MANIFEST.md": """## TSIS_GRAPHIFY_TERMINAL_ACCEPTANCE_20260822

- terminal_status: PASS
- run_id: tsis_graphify_merge_20260822_r2
- graphify_version: 0.9.33
- nodes: 10573
- edges: 20234
- hyperedges: 317
- communities: 658
- hyperedges_expected_from_inputs: 317
- hyperedges_composed: 317
- hyperedge_members_repaired: 1761
- invalid_node_records: 0
- duplicate_node_ids: 0
- invalid_edge_records: 0
- hard_missing_edge_endpoints: 0
- self_loop_edges: 0
- invalid_hyperedge_members: 0
- duplicate_hyperedge_ids: 0
- forbidden_legacy_source_paths: 0
- official_diagnostic_stderr_bytes: 0
- official_diagnostic: GRAPH_DIAGNOSTIC_TERMINAL_20260822.json
- terminal_audit: GRAPHIFY_TERMINAL_AUDIT_20260822.json
- consolidated_audit: C:\\TSIS_Data\\runs\\graphify_refresh\\GRAPHIFY_TERMINAL_AUDIT_20260822.json
""",
    ROOT / "00_CTO" / "graphify-out" / "BUILD_MANIFEST.md": """## TSIS_GRAPHIFY_TERMINAL_ACCEPTANCE_20260822

- terminal_status: PASS
- run_id: tsis_graphify_merge_20260822_r6
- graphify_version: 0.9.33
- nodes: 1628
- edges: 2903
- hyperedges: 57
- communities: 116
- hyperedges_expected_from_inputs: 57
- hyperedges_composed: 57
- hyperedge_members_repaired: 299
- invalid_node_records: 0
- duplicate_node_ids: 0
- invalid_edge_records: 0
- hard_missing_edge_endpoints: 0
- self_loop_edges: 0
- invalid_hyperedge_members: 0
- duplicate_hyperedge_ids: 0
- forbidden_legacy_source_paths: 0
- official_diagnostic_stderr_bytes: 0
- official_diagnostic: GRAPH_DIAGNOSTIC_TERMINAL_20260822.json
- terminal_audit: GRAPHIFY_TERMINAL_AUDIT_20260822.json
""",
    ROOT
    / "00_CTO_APPLIED_ARCHITECTURE"
    / "graphify-out"
    / "BUILD_MANIFEST.md": """## TSIS_GRAPHIFY_TERMINAL_ACCEPTANCE_20260822

- terminal_status: PASS
- run_id: tsis_graphify_refresh_20260822_r3
- graphify_version: 0.9.33
- nodes: 1529
- edges: 1761
- hyperedges: 105
- communities: 91
- invalid_node_records: 0
- duplicate_node_ids: 0
- invalid_edge_records: 0
- hard_missing_edge_endpoints: 0
- self_loop_edges: 0
- invalid_hyperedge_members: 0
- duplicate_hyperedge_ids: 0
- forbidden_legacy_source_paths: 0
- official_diagnostic_stderr_bytes: 0
- official_diagnostic: GRAPH_DIAGNOSTIC_TERMINAL_20260822.json
- terminal_audit: GRAPHIFY_TERMINAL_AUDIT_20260822.json
""",
    ROOT
    / "01_TSIS_DATA_FOUNDATION"
    / "01_foundations"
    / "graphify-out"
    / "BUILD_MANIFEST.md": """## TSIS_GRAPHIFY_TERMINAL_ACCEPTANCE_20260822

- terminal_status: PASS
- run_id: foundation_graphify_merge_20260822_r5
- graphify_version: 0.9.33
- nodes: 4840
- edges: 9075
- hyperedges: 147
- communities: 330
- hyperedges_expected_from_inputs: 147
- hyperedges_composed: 147
- hyperedge_members_repaired: 795
- generated_missing_hyperedge_ids: 33
- invalid_node_records: 0
- duplicate_node_ids: 0
- invalid_edge_records: 0
- hard_missing_edge_endpoints: 0
- self_loop_edges: 0
- invalid_hyperedge_members: 0
- duplicate_hyperedge_ids: 0
- forbidden_legacy_source_paths: 0
- official_diagnostic_stderr_bytes: 0
- official_diagnostic: GRAPH_DIAGNOSTIC_TERMINAL_20260822.json
- terminal_audit: GRAPHIFY_TERMINAL_AUDIT_20260822.json
""",
    ROOT / "02_TSIS_BACKTEST_ENGINE" / "graphify-out" / "BUILD_MANIFEST.md": """## TSIS_GRAPHIFY_TERMINAL_ACCEPTANCE_20260822

- terminal_status: PASS
- target_id: backtest_engine_current_20260822
- graphify_version: 0.9.33
- nodes: 2576
- edges: 6495
- hyperedges: 8
- communities: 137
- invalid_node_records: 0
- duplicate_node_ids: 0
- invalid_edge_records: 0
- hard_missing_edge_endpoints: 0
- self_loop_edges: 0
- invalid_hyperedge_members: 0
- duplicate_hyperedge_ids: 0
- forbidden_legacy_source_paths: 0
- official_diagnostic_stderr_bytes: 0
- official_diagnostic: GRAPH_DIAGNOSTIC_TERMINAL_20260822.json
- terminal_audit: GRAPHIFY_TERMINAL_AUDIT_20260822.json
""",
}


CHANGELOGS = {
    ROOT / "CHANGELOG.md": """## 2026-08-22 - TSIS_GRAPHIFY_REFRESH_20260822

- Rebuilt the governed CTO, Applied Architecture, Data Foundation and Backtest Engine graph leaves.
- Rebuilt the CTO, Data Foundation and TSIS root merges with the official Graphify flow.
- Preserved and namespaced every input hyperedge instead of accepting Graphify merge truncation.
- Added the current `04_TSIS_SCREENERS` and `05_TSIS_STATISTICS_PATTERNS` topology through their governed leaf coverage.
- Removed semantically obsolete source paths from the published graphs.
- Persisted official multigraph diagnostics and an independent terminal audit for all five requested roots.
- Final root: 10,573 nodes, 20,234 edges, 317 hyperedges and 658 communities.
""",
    ROOT / "00_CTO" / "CHANGELOG.md": """## 2026-08-22 - TSIS_GRAPHIFY_REFRESH_20260822

- Rebuilt six current CTO leaves and published a new governed root merge.
- Added current market-state, Wake-Up, trading-system, backtest-authority and screener coverage.
- Repaired deterministic hyperedge namespaces across all leaf inputs.
- Terminal graph: 1,628 nodes, 2,903 edges, 57 hyperedges and 116 communities; audit PASS.
""",
    ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md": """## 2026-08-22 - TSIS_GRAPHIFY_REFRESH_20260822

- Replaced the stale Applied Architecture graph with a full semantic rebuild from the current corpus.
- Repaired extraction self-loops before publication and repeated clustering and community labeling.
- Terminal graph: 1,529 nodes, 1,761 edges, 105 hyperedges and 91 communities; audit PASS.
""",
    ROOT / "01_TSIS_DATA_FOUNDATION" / "01_foundations" / "CHANGELOG.md": """## 2026-08-22 - TSIS_GRAPHIFY_REFRESH_20260822

- Rebuilt eight governed Data Foundation leaves from current paths and source semantics.
- Removed obsolete `01_TSIS_backtest_SmallCaps` and `E:/TSIS/data` source identities.
- Rebuilt the Foundation root with fail-closed hyperedge namespace repair.
- Terminal graph: 4,840 nodes, 9,075 edges, 147 hyperedges and 330 communities; audit PASS.
""",
    ROOT / "02_TSIS_BACKTEST_ENGINE" / "CHANGELOG.md": """## 2026-08-22 - TSIS_GRAPHIFY_REFRESH_20260822

- Replaced the stale Backtest Engine snapshot with a controlled full-rebuild fallback after the incremental audit.
- Published the current leaf and synchronized the requested root mirror.
- Removed obsolete `01_TSIS_backtest_SmallCaps` source identities.
- Terminal graph: 2,576 nodes, 6,495 edges, 8 hyperedges and 137 communities; audit PASS.
""",
}


QUEUES = {
    ROOT / "GRAPHIFY_REFRESH_QUEUE.md": """## 2026-08-22 - TSIS_GRAPHIFY_QUEUE_RESOLUTION_20260822

- resolution_status: ACCEPTED_REFRESH_PUBLISHED
- published_root: `C:\\TSIS_Data\\graphify-out`
- covered_queue_ids: `GFQ-20260805-ROOT-001`, `GFQ-20260811-ROOT-002`, `GFQ-20260812-SEC-PIT-OWNERSHIP-002`, `GFQ-20260813-FOUNDATIONS-SEC-SHARE-CLASS-V021-001`
- coverage_rule: the terminal root supersedes older pending refresh requests only where their governed source files occur in the published leaf corpus manifests.
- remains_pending_out_of_scope: `GFQ-20260817-ROOT-WAKE-UP-ORACLE-LAB-001`, `GFQ-20260821-ROOT-MODULE-MAP-001`, `GFQ-20260707-001`, `GFQ-20260706-001`, `GFQ-20260716-001`
- evidence: `C:\\TSIS_Data\\runs\\graphify_refresh\\GRAPHIFY_TERMINAL_AUDIT_20260822.json`
""",
    ROOT / "00_CTO" / "GRAPHIFY_REFRESH_QUEUE.md": """## 2026-08-22 - TSIS_GRAPHIFY_QUEUE_RESOLUTION_20260822

- resolution_status: ACCEPTED_REFRESH_PUBLISHED
- published_root: `C:\\TSIS_Data\\00_CTO\\graphify-out`
- covered_queue_ids: `GFQ-20260811-001`, `GFQ-20260811-002`, `GFQ-20260810-001`, `GFQ-20260730-001`, `GFQ-20260722-001`, `GFQ-20260701-001`, `GFQ-20260704-005..015`, `GFQ-20260705-001..003`, `GFQ-20260623-001`, `GFQ-20260621-001`, `GFQ-20260621-003`, `GFQ-20260630-002..004`
- coverage_rule: entries are resolved only for source files present in the six leaf corpus manifests published by this refresh.
- evidence: `C:\\TSIS_Data\\00_CTO\\graphify-out\\GRAPHIFY_TERMINAL_AUDIT_20260822.json`
""",
    ROOT
    / "00_CTO_APPLIED_ARCHITECTURE"
    / "GRAPHIFY_REFRESH_QUEUE.md": """## 2026-08-22 - TSIS_GRAPHIFY_QUEUE_RESOLUTION_20260822

- resolution_status: ACCEPTED_REFRESH_PUBLISHED
- published_root: `C:\\TSIS_Data\\00_CTO_APPLIED_ARCHITECTURE\\graphify-out`
- covered_queue_ids: `GFQ-20260805-APPLIED-001`
- evidence: `C:\\TSIS_Data\\00_CTO_APPLIED_ARCHITECTURE\\graphify-out\\GRAPHIFY_TERMINAL_AUDIT_20260822.json`
""",
    ROOT
    / "01_TSIS_DATA_FOUNDATION"
    / "01_foundations"
    / "GRAPHIFY_REFRESH_QUEUE.md": """## 2026-08-22 - TSIS_GRAPHIFY_QUEUE_RESOLUTION_20260822

- resolution_status: ACCEPTED_REFRESH_PUBLISHED
- published_root: `C:\\TSIS_Data\\01_TSIS_DATA_FOUNDATION\\01_foundations\\graphify-out`
- covered_queue_ids: `GFQ-20260722-root-path-migration-data-foundation`, `GFQ-20260704-minute-data-plane-reading`, `GFQ-20260701-001`, all actionable `GFQ-20260629-*`, `GFQ-20260630-daily-scanner-v0-2-base-universe-profiles`, `GFQ-20260630-daily-scanner-v0-3-in-play-momentum`, `GFQ-20260621-001..002`, `GFQ-20260622-001..008`, `GFQ-20260623-001..002`, `GFQ-20260624-001`, `GFQ-20260625-001..002`, `GFQ-20260626-001..005`, `GFQ-20260627-001..009`, `GFQ-20260627-011..013`, `GFQ-20260628-001`, `GFQ-20260628-004`, `GFQ-20260630-002..004`, `GFQ-20260703-001`, `GFQ-20260704-002..010`, `GFQ-20260705-001..003`
- coverage_rule: entries are resolved only for source files present in the eight leaf corpus manifests published by this refresh.
- remains_pending_out_of_scope: `GFQ-20260627-010`, `GFQ-20260627-014`, `GFQ-20260628-002`, `GFQ-20260628-003`
- evidence: `C:\\TSIS_Data\\01_TSIS_DATA_FOUNDATION\\01_foundations\\graphify-out\\GRAPHIFY_TERMINAL_AUDIT_20260822.json`
""",
    ROOT / "02_TSIS_BACKTEST_ENGINE" / "GRAPHIFY_REFRESH_QUEUE.md": """## 2026-08-22 - TSIS_GRAPHIFY_QUEUE_RESOLUTION_20260822

- resolution_status: ACCEPTED_REFRESH_PUBLISHED
- published_root: `C:\\TSIS_Data\\02_TSIS_BACKTEST_ENGINE\\graphify-out`
- covered_queue_ids: `GFQ-20260805-BT-004`
- preserved_historical_status: `GFQ-20260805-BT-001` remains `published_snapshot`
- remains_pending_out_of_scope: `GFQ-20260805-BT-002`, `GFQ-20260805-BT-003`
- evidence: `C:\\TSIS_Data\\02_TSIS_BACKTEST_ENGINE\\graphify-out\\GRAPHIFY_TERMINAL_AUDIT_20260822.json`
""",
}


def main() -> int:
    missing = [
        str(path)
        for path in (*MANIFESTS, *CHANGELOGS, *QUEUES)
        if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError("Missing governed documentation:\n" + "\n".join(missing))

    for path, block in MANIFESTS.items():
        append_once(path, MARKER, block)
    for path, block in CHANGELOGS.items():
        prepend_once(path, CHANGE_MARKER, block)
    for path, block in QUEUES.items():
        prepend_once(path, QUEUE_MARKER, block)

    print(f"manifests_updated={len(MANIFESTS)}")
    print(f"changelogs_updated={len(CHANGELOGS)}")
    print(f"queues_updated={len(QUEUES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
