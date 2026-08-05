# LOCAL_RULES - TSIS Backtest Engine

Status: ACTIVE_IMPLEMENTATION_RULES
Reset: 2026-07-28

1. `02_TSIS_BACKTEST_ENGINE` is the implementation root, not the architecture authority.
2. `00_CTO/14_BACKTEST_ENGINE` owns guide, decisions, architecture notes and construction log.
3. `01_TSIS_DATA_FOUNDATION` owns governed data semantics, certification and dataset contracts.
4. Do not copy ambiguous RAW market data into this folder.
5. Do not consume market data before `RunPreflight` resolves the run context.
6. Every run must declare dataset, universe, signal price view, execution price view, valuation price view, date range, session policy, timezone, missing-data policy, corporate-action policy, fill/cost assumptions and limitations.
7. `quote_guarded_1m` may be used in V0.1 only as controlled candidate input and execution proxy for engine mechanics, not as proof of executable fill realism.
8. Use synthetic fixtures first; use real TSIS data fixtures only after synthetic tests pass.
9. Keep code small and test-driven. Do not materialize future modules until a concrete vertical-slice need exists.
10. Use `REGULAR_ONLY`, `09:30-16:00`, `America/New_York` for the first data/replay smoke path unless the CTO guide changes.
11. Use SHA-256 only for files or partitions consumed by a run; do not hash the full 1.27M-file universe for a smoke test.
12. Every completed operational step must update `AGENTS.md` and `CHANGELOG.md`.
13. If an implementation step changes a TSIS decision or contract, update the corresponding document under `00_CTO/14_BACKTEST_ENGINE`.
14. Do not claim `TSIS_VALIDATED_CONTRACT` until code, tests and evidence exist.


## Graphify

Graphify is semantic navigation, not gate authority or evidence.

Any work with semantic impact on this branch must end with either:

1. an official update/rebuild and diagnosis of the affected leaf; or
2. a `pending` entry in `GRAPHIFY_REFRESH_QUEUE.md`.

Builds must follow `GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md`. Do not execute
physical backtest commands, consume single-use authorizations, or include
`runs`, `evidence`, `deliverables` or `99_archive` in the current-engine leaf.
