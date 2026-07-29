# Local governance rules

1. JSON registers are canonical machine-readable records; Markdown explains them.
2. Stable identifiers are never reused.
3. `ACTIVE`, `CLOSED_PASS` and `AUTHORIZED` require explicit evidence.
4. Inference must be labeled `INFERRED_FROM_IMPLEMENTATION`.
5. Missing proof must be labeled `MISSING_EVIDENCE`, not converted to a pass.
6. Contradictions are registered; they are not silently normalized.
7. A waiver requires owner, rationale, scope, expiry/review date and closing gate.
8. Implementation does not authorize itself.
9. Tests prove only the behavior they bind to.
10. A smoke run does not establish realism, tradability, robustness or edge.
11. No later gate may weaken causality, hash verification, fail-closed behavior or no-imputation without an explicit superseding decision.
12. Times are UTC in evidence unless an artifact explicitly states otherwise.
13. The implementation tree is the main executable artifact; this guide records the authority and reasons behind it.
14. Data meaning comes from contracts, schemas, registries and consumption policies, never from physical paths alone.
15. RAW data must not be corrected in place.
16. Each run must declare dataset, universe, price views, date range, session policy, cost model, fill model and limitations.
17. Sersan and books are evidence sources; they become TSIS rules only through an explicit TSIS decision, contract or test.
18. `00_CTO_APPLIED_ARCHITECTURE` is external context, not local authorization.
19. There is one live agent contract: `AGENTS.md`. Singular `AGENT.md` is historical only.


## Governance as part of Definition of Done

Para cualquier incremento material realizado en `02_TSIS_BACKTEST_ENGINE`,
la sincronización aplicable de `00_CTO\14_BACKTEST_ENGINE` forma parte de la
Definition of Done.

Un agente no puede declarar un gate como cerrado basándose únicamente en que:

- el código existe;
- los tests pasan;
- un contrato fue corregido;
- un run fue generado.

También debe comprobar que decisiones, políticas, trazabilidad, limitaciones,
documentación viva y estado del gate representan la misma realidad.

Si esta sincronización no se ha completado, el estado deberá indicar
`GOVERNANCE_SYNC_PENDING`.