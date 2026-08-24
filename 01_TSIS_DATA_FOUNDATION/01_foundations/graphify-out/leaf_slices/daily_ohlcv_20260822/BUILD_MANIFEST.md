# Graphify Build Manifest

- status: ACCEPTED
- target_id: foundation_daily_ohlcv_20260822
- strategy: FULL_REBUILD
- built_at_utc: 2026-08-22T13:02:21.055838+00:00
- git_branch: integrate/main-data-quality-dossiers-20260613
- git_commit: e71c6ce5c41df807577e309d1e58a543b45b2068
- graphify_version: 0.9.33
- graphify_python: C:\Users\AlexJ\AppData\Local\Programs\Python\Python313\python.exe
- extraction_spec: C:\Users\AlexJ\.codex\skills\graphify\references\extraction-spec.md
- extraction_spec_sha256: 32d7decad42d58129c6694ea4e4ce1f72a531bc5161827d2095787e9448735e9
- semantic_mode: codex_subagents_no_external_api
- corpus_files: 84
- nodes: 251
- edges: 325
- communities: 23
- queue_ids: DAILY_OHLCV_CURRENT
- forbidden_source_substrings: 01_TSIS_backtest_SmallCaps, E:/TSIS/data, 00_CTO_1
- dangling_endpoint_edges: 0
- missing_endpoint_edges: 0
- self_loop_edges: 0
- collapsed_edges: 0

## Next delta

Use the official Graphify incremental flow only if the corpus identity and source root remain compatible. Otherwise create a new full-rebuild leaf.
