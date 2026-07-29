# Local Rules - TSIS Backtest Engine

Status: LIVE_RULES

1. The backtester is the main artifact. The guide exists to record decisions made while building it.
2. Do not finish a full theoretical guide before the first vertical slice.
3. Every guide layer must start from a concrete implementation need.
4. Sersan and the books are evidence sources. They become TSIS rules only after a TSIS decision, contract or test.
5. Before any intraday data work, read `G:/TSIS/data/README.md` and the relevant Data Foundation contracts.
6. Physical paths do not define dataset meaning. Dataset contracts, schemas, registries and consumption policies define meaning.
7. Do not correct RAW data in place.
8. Every run must declare dataset, universe, price view, date range, session policy, cost model, fill model and limitations.
9. Use simple guide filenames such as `01_DATA.md`, `02_REPLAY.md`, `03_STATE.md`.
10. Keep unresolved questions visible. Do not hide them inside prose.
11. Every completed operational step must update `AGENT.md`, `CHANGELOG.md` and the affected guide layer.
12. If a session resumes after interruption, read `AGENT.md` first and continue from its `Registro Vivo De Pasos`.
