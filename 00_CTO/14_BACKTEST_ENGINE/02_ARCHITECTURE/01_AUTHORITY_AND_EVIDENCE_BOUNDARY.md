# Authority and evidence boundary

| Layer | Root | Responsibility |
|---|---|---|
| Authority | `00_CTO/14_BACKTEST_ENGINE` | decisions, policies, contracts, gates, traceability, exceptions and allowed claims |
| Implementation | `02_TSIS_BACKTEST_ENGINE/src` | executable behavior |
| Verification | `02_TSIS_BACKTEST_ENGINE/tests` | bounded acceptance evidence |
| Physical evidence | `02_TSIS_BACKTEST_ENGINE/runs` | immutable run outputs and hashes |
| Local handoff | `02_TSIS_BACKTEST_ENGINE/README.md`, `AGENTS.md`, `CHANGELOG.md` | current operational state; must remain consistent with authority |

## Component map

| Component | Current state | Next dependency |
|---|---|---|
| RunPreflight | `CLOSED_PASS` | unified run orchestration |
| RealDataInspector | `CLOSED_PASS` | broader governed fixtures |
| HistoricalReplayFeed | `CLOSED_PASS_MINIMUM` | unified run manifest |
| MechanicalEventLoop | `CLOSED_PASS_PROXY` | bounded fill simulator |
| AccountingEngine | `CLOSED_PASS_MINIMUM` | execution/cost integration |
| Execution semantics contract | `CORRECTED_DRAFT_READY_FOR_REVIEW` | independent review |
| DeterministicFillSimulator | `NOT_AUTHORIZED` | contract closure and authorization |
| StateReplayFeed | `NOT_AUTHORIZED` | provider–consumer compatibility gate |

## Dependency rule

The state-provider lane is parallel. Its progress cannot silently authorize state consumption by the backtester. Likewise, backtester progress cannot change provider contracts.

