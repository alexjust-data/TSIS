# TSIS · Arquitectura científica del backtest

```text
╔ TSIS · ARQUITECTURA CIENTÍFICA DEL BACKTEST · DE PREGUNTA A ESTRATEGIA AUTORIZADA ═════════════════════════════════════════╗
║ REGLA MAESTRA: un run técnicamente correcto no demuestra edge; un edge validado no autoriza producción.                    ║
║ La salida final siempre es condicional al universo, régimen, horizonte, costes, capacidad y versión evaluados.             ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
                                                              │                                                               
                                                              ▼                                                               
┌ CONTROL PLANE TRANSVERSAL · GOBIERNA TODAS LAS FASES ──────────────────────────────────────────────────────────────────────┐
│ Gate Register · Research Experiment Registry · Trial Ledger completo · permisos y presupuesto de búsqueda                  │
│ versionado de datos / estados / eventos / outcomes / estrategia / costes / código / entorno · manifests y hashes           │
│ Evidence Registry · seeds · logs inmutables · revisión independiente · reproducción · fail closed ante ambigüedad          │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
┌ 0 · FRONTERA IMPLEMENTADA Y AUTORIZADA EN ESTE ENCARGO ────────────────────────────────────────────────────────────────────┐
│ [CLOSED] BT-GATE-001…014: preflight, inspección física, replay, trades, accounting, costes, fill simulator,                │
│          estrategia end-to-end, portfolio multi-símbolo/sesión, replay físico y consumo PIT de Market State.               │
│ [ACTIVE] BT-GATE-015: consumo físico PIT de Event State; su cierre exige PASS post-ejecución independiente y explícito.    │
│          La autorización V0.4 es de un solo uso; no se reejecuta y no autoriza órdenes, fills, PnL ni consumo general.     │
│ [CLOSED BOUNDARY] BT-GATE-016 = NOT_DEFINED.                                                                               │
│ La siguiente capability exige contrato, autorización y evidencia propios; no se abre implícitamente.                       │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
┌ DECISIÓN · ¿BT-GATE-015 consta como CLOSED_PASS explícito en las autoridades vigentes? ────────────────────────────────────┐
├─────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┤
│                 NO — FAIL CLOSED / RECHAZAR                 │                        SÍ — CONTINUAR                        │
├─────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
│ Preservar autorización, receipts y evidencia.               │ Congelar el alcance aceptado de BT-GATE-015.                 │
│ No reejecutar la autorización consumida.                    │ No reutilizar su autorización single-use.                    │
│ Reconciliar contrato / review / register.                   │ Definir por contrato la siguiente capability.                │
│ No abrir el gate siguiente implícitamente.                  │ Solo después puede avanzar la construcción.                  │
└─────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────┘
                                                         RUTA DE PASS                                                         
                                                              │                                                               
                                                              ▼                                                               
╔ ARQUITECTURA OBJETIVO · LOS BLOQUES SIGUIENTES NO SON AUTORIZACIÓN ACTUAL ═════════════════════════════════════════════════╗
║ Cada bloque se incorpora mediante su propio gate: contrato → implementación acotada → evidencia → review → cierre.         ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
                                                              │                                                               
                                                              ▼                                                               
┌ 1 · CONTRATO CIENTÍFICO ───────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Antes de programar o buscar parámetros se fija qué pregunta puede falsarse y qué resultado contaría como fracaso.          │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
┌ PREGUNTA ────────────────────────────┐   ┌ HIPÓTESIS ───────────────────────────┐   ┌ EXPERIMENTO ─────────────────────────┐
│ Fenómeno y mecanismo.                │   │ H1 y hipótesis nula.                 │   │ Experiment ID y familia de trials.   │
│ Universo PIT y sesión.               │   │ Baseline declarado.                  │   │ Qué puede variar y qué queda fijo.   │
│ Lado y horizonte.                    │──►│ Efecto mínimo relevante.             │──►│ Presupuesto y reglas de abandono.    │
│ Información legal en t.              │   │ Criterio de falsación.               │   │ Métricas, splits, juez y holdout.    │
└──────────────────────────────────────┘   └──────────────────────────────────────┘   └──────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
┌ 2 · DATA FOUNDATION + UNIVERSO POINT-IN-TIME ──────────────────────────────────────────────────────────────────────────────┐
│ El backtester consume datos autoritativos; nunca corrige silenciosamente la historia durante una evaluación.               │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
┌ DATOS AUTORITATIVOS ─────────────────┐   ┌ UNIVERSO PIT ────────────────────────┐   ┌ LEGALIDAD TEMPORAL ──────────────────┐
│ Schemas, lineage y versión.          │   │ Membership histórica as-of.          │   │ event_time + available_at.           │
│ Quotes, trades, barras y noticias.   │   │ Ticker / venue changes.              │   │ Política same-timestamp.             │
│ Halts, bad prints y corporate        │──►│ Calendario, sesión y timezone.       │──►│ Cero early delivery.                 │
│ actions.                             │   │ Regla de inclusión reproducible.     │   │ Ambigüedad temporal = FAIL CLOSED.   │
│ Símbolos muertos y delistings.       │   │                                      │   │                                      │
└──────────────────────────────────────┘   └──────────────────────────────────────┘   └──────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
┌ 3 · SEPARACIÓN SAGRADA X / Y · FRONTERA ANTI-LEAKAGE ──────────────────────────────────────────────────────────────────────┐
├─────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┤
│               X — OBSERVABLES LEGALES AS-OF t               │                      Y — FUTURO AISLADO                      │
├─────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
│ Market State + Event State + rolling state.                 │ Outcomes, labels y rewards con horizonte propio.             │
│ Único input permitido a detector, modelo o estrategia.      │ Se calculan después del cutoff y viven separados de X.       │
│ Snapshots reconstruibles y versionados.                     │ No existe ruta Y → feature / detector / decisión.            │
│ Tests de no-lookahead, truncation invariance y ordering.    │ Solo el evaluador autorizado combina evidencia + Y.          │
│ X no puede ser reescrito después de ver el resultado.       │ Labels ML / rewards RL: contrato y versión propios.          │
└─────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
┌ 4 · DESCUBRIMIENTO, PROMOCIÓN Y FREEZE DEL CANDIDATO ──────────────────────────────────────────────────────────────────────┐
│ Explorar sirve para descubrir estructura; la prueba de edge empieza únicamente después de congelar el candidato.           │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
┌ GENERADORES ─────────────────────────┐   ┌ EXPLORACIÓN ─────────────────────────┐   ┌ PROMOCIÓN + FREEZE vN ───────────────┐
│ Humano, reglas, ML, RL o             │   │ Sweeps y estadística descriptiva.    │   │ StrategySpec exacta.                 │
│ AlphaEvolve.                         │   │ Event / representation candidates.   │   │ Features / eventos / costes          │
│ Proponen probes, ventanas y          │   │ Baselines y sensibilidad inicial.    │   │ versionados.                         │
│ variantes.                           │──►│ Todo intento entra en Trial Ledger.  │──►│ Code + data + env hashes.            │
│ Mismo protocolo para todos.          │   │                                      │   │ Evaluador bloqueado y holdout        │
│ No controlan al juez ni el holdout.  │   │                                      │   │ sellado.                             │
└──────────────────────────────────────┘   └──────────────────────────────────────┘   └──────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
┌ 5 · MOTOR DE BACKTEST EVENT-DRIVEN · DATA PLANE ───────────────────────────────────────────────────────────────────────────┐
│ Mismo orden causal que en live: observar → decidir → arriesgar → ordenar → ejecutar → contabilizar → evidenciar.           │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
┌ 5A · PREFLIGHT ──────────────────────┐   ┌ 5B · REPLAY ─────────────────────────┐   ┌ 5C · ESTADO PIT ─────────────────────┐
│ RunSpec y StrategySpec.              │   │ HistoricalDataSource.                │   │ MarketStateStore.                    │
│ Permisos y alcance.                  │   │ Global Clock + EventQueue.           │   │ EventStateStore.                     │
│ Data / universe manifests.           │──►│ Sesiones, halts y missing data.      │──►│ Rolling / session state.             │
│ Cost model, seed y entorno.          │   │ Orden determinista de eventos.       │   │ Solo información disponible en t.    │
└──────────────────────────────────────┘   └──────────────────────────────────────┘   └──────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
┌ 5D · DECISIÓN ───────────────────────┐   ┌ 5E · PORTFOLIO / RISK / OMS ─────────┐   ┌ 5F · EXECUTION SIM ──────────────────┐
│ Condition → DecisionRecord.          │   │ Sizing, cash y exposure.             │   │ Bid / ask y spread.                  │
│ DecisionPolicy → OrderIntent.        │   │ Liquidez, capacity y shortability.   │   │ Latency, queue y participation.      │
│ Sin fills inventados.                │──►│ Accept / reject / cancel / amend.    │──►│ Partial fill / no fill / impact.     │
│ No muta portfolio ni accounting.     │   │ Máquina de estados de la orden.      │   │ Fees, locate y borrow.               │
└──────────────────────────────────────┘   └──────────────────────────────────────┘   └──────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
┌ 5G · ORDER / FILL EVENTS ────────────┐   ┌ 5H · ACCOUNTING ─────────────────────┐   ┌ 5I · EVIDENCE ───────────────────────┐
│ Submitted / accepted / rejected.     │   │ Cash, positions y buying power.      │   │ State / decision ledgers.            │
│ Partial / filled / canceled.         │   │ PnL realizado / no realizado.        │   │ Orders, fills, trades y equity.      │
│ Timestamps y reason codes.           │──►│ Fees, borrow y equity.               │──►│ Exceptions, metrics y hashes.        │
│ Feedback causal al EventLoop.        │   │ Identidades contables invariantes.   │   │ Final manifest reproducible.         │
└──────────────────────────────────────┘   └──────────────────────────────────────┘   └──────────────────────────────────────┘
┌ BUCLE DEL RUN ─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ↺ Siguiente evento hasta fin de sesión/rango; estado, órdenes, posiciones y cash persisten causalmente entre eventos.      │
│ El runtime produce simulación y evidencia. No decide por sí mismo que exista edge.                                         │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
┌ 6 · VERIFICACIÓN TÉCNICA DEL MOTOR Y DEL RUN ──────────────────────────────────────────────────────────────────────────────┐
│ Antes de mirar rentabilidad se demuestra que el run reproduce exactamente las reglas, la causalidad y el accounting.       │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
┌ GOLDEN CASES ────────────────────────┐   ┌ DETERMINISMO ────────────────────────┐   ┌ NEGATIVE TESTS ──────────────────────┐
│ Casos manuales mínimos.              │   │ Mismos inputs → mismos ledgers.      │   │ No-lookahead y no early delivery.    │
│ Reconciliación trade-by-trade.       │   │ Mismos hashes y métricas.            │   │ Ordering / same timestamp.           │
│ Órdenes, fills, cash y posición.     │──►│ Seeds y entorno fijados.             │──►│ Identidades contables.               │
│ Benchmarks independientes si aplica. │   │ Reproducción bajo autorización       │   │ Fails esperados ante datos           │
│                                      │   │ propia.                              │   │ inválidos.                           │
└──────────────────────────────────────┘   └──────────────────────────────────────┘   └──────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
┌ DECISIÓN · ¿VERIFICACIÓN TÉCNICA = PASS? ──────────────────────────────────────────────────────────────────────────────────┐
├─────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┤
│                 NO — FAIL CLOSED / RECHAZAR                 │                        SÍ — CONTINUAR                        │
├─────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
│ Run técnicamente inválido.                                  │ Run técnicamente válido y reproducible.                      │
│ Archivar evidencia sin interpretar PnL.                     │ Puede entrar en evaluación científica.                       │
│ Corregir motor, datos o contrato.                           │ Todavía NO prueba edge.                                      │
│ Nueva versión / autorización; nunca parche retroactivo.     │ La StrategySpec permanece congelada.                         │
└─────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────┘
                                                         RUTA DE PASS                                                         
                                                              │                                                               
                                                              ▼                                                               
┌ 7 · VALIDACIÓN CIENTÍFICA · EVALUADOR BLOQUEADO ───────────────────────────────────────────────────────────────────────────┐
│ Inputs autorizados: evidencia del run + Y aislado + baselines. El generador no puede modificar métricas ni juez.           │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
┌ CONTRATO DEL EVALUADOR ────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Métricas, umbrales, baselines, splits y familia de tests definidos antes del run.                                          │
│ Las reglas de promoción quedan bloqueadas antes de evaluar el candidato vN.                                                │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
┌ 7A · REALISMO ECONÓMICO ──────────────────────────────────┐    ┌ 7B · ROBUSTEZ ────────────────────────────────────────────┐
│ PnL neto sobre precios ejecutables.                       │    │ Plateaus; no depender de un pico paramétrico.             │
│ Spread, slippage, latency, no-fills, fees, borrow y       │    │ Subperiodos, símbolos, regímenes y sesiones.              │
│ locate.                                                   │───►│ Concentración de PnL, colas, drawdown y stress.           │
│ Escenarios base / moderado / severo.                      │    │ Estabilidad de reglas y failure modes.                    │
│ Capacity, participation e impacto.                        │    │                                                           │
└───────────────────────────────────────────────────────────┘    └───────────────────────────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
┌ 7C · VALIDACIÓN TEMPORAL OOS ─────────────────────────────┐    ┌ 7D · SELECCIÓN Y MÚLTIPLES PRUEBAS ───────────────────────┐
│ Out-of-sample cronológico y walk-forward.                 │    │ Todos los trials y grados de libertad contabilizados.     │
│ Purging + embargo cuando hay solapamiento informacional.  │    │ Penalización de complejidad y selection bias.             │
│ CPCV / CSCV cuando el diseño lo justifique.               │───►│ DSR, PBO, Reality Check, SPA o FDR según el diseño.       │
│ No random K-fold para series financieras dependientes.    │    │ Ningún resultado desaparece del historial.                │
└───────────────────────────────────────────────────────────┘    └───────────────────────────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
┌ 7E · HOLDOUT FINAL SELLADO ───────────────────────────────┐    ┌ 7F · REPLICACIÓN INDEPENDIENTE ───────────────────────────┐
│ Se abre una sola vez para el candidato congelado.         │    │ Ejecución limpia desde manifests y hashes.                │
│ No se elige variante después de observarlo.               │    │ Reviewer / agente independiente.                          │
│ Si falla, el holdout queda quemado.                       │───►│ Segunda implementación o vendor si es viable.             │
│ Cambio material = vN+1 + nuevo Experiment ID.             │    │ Resultado y discrepancias quedan evidenciados.            │
└───────────────────────────────────────────────────────────┘    └───────────────────────────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
┌ DECISIÓN · ¿LA EVIDENCIA ES NETA, ROBUSTA, OOS, AJUSTADA POR SELECCIÓN Y REPLICABLE? ──────────────────────────────────────┐
├─────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┤
│                 NO — FAIL CLOSED / RECHAZAR                 │                        SÍ — CONTINUAR                        │
├─────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
│ REJECTED / REFORMULATE.                                     │ PASS CIENTÍFICO CONDICIONAL.                                 │
│ Conservar evidencia favorable y negativa.                   │ Promover a Knowledge Object versionado.                      │
│ No cambiar el juez para salvar el resultado.                │ Válido solo dentro del scope demostrado.                     │
│ Nueva hipótesis = vN+1, nuevos trials y nuevo holdout.      │ Todavía no autoriza capital real.                            │
└─────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────┘
                                                         RUTA DE PASS                                                         
                                                              │                                                               
                                                              ▼                                                               
┌ 8 · PROMOCIÓN A CONOCIMIENTO ──────────────────────────────────────────────────────────────────────────────────────────────┐
├─────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┤
│             KNOWLEDGE OBJECT · CONDITIONAL EDGE             │                      ESTADO CIENTÍFICO                       │
├─────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
│ Versión, universo, régimen, side y horizonte.               │ PROVISIONAL / VALIDATED / REJECTED / SUPERSEDED.             │
│ Definición exacta de X, evento, policy y ejecución.         │ Validated significa que sobrevivió al protocolo fijado.      │
│ Effect size neto + incertidumbre.                           │ No significa verdad universal ni edge permanente.            │
│ Capacity ceiling, dependencias y limitaciones.              │ No permite reusar silenciosamente datos o holdout.           │
│ Failure modes y evidencia contradictoria.                   │ Producción exige una validación operativa separada.          │
└─────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
┌ 9 · VALIDACIÓN OPERATIVA ──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Se contrasta el execution model contra datos y llegada reales antes de asignar capital significativo.                      │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
┌ 9A · SHADOW / PAPER ─────────────────┐   ┌ 9B · RECONCILIACIÓN ─────────────────┐   ┌ 9C · LIVE PILOT LIMITADO ────────────┐
│ Mismo strategy core.                 │   │ Estado, timing y señales.            │   │ Capital y participation pequeños.    │
│ Datos y arrival reales.              │   │ Orders, rejects y cancels.           │   │ Hard risk limits y kill switch.      │
│ Capital cero.                        │──►│ Fills, spread, slippage y latency.   │──►│ Sin cambiar reglas durante el pilot. │
│ Telemetría y manifests completos.    │   │ Backtest vs observed envelope.       │   │ Receipts y revisión post-pilot.      │
└──────────────────────────────────────┘   └──────────────────────────────────────┘   └──────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
┌ DECISIÓN · ¿SHADOW + PILOT CONFIRMAN EDGE, EJECUCIÓN Y RIESGO DENTRO DEL ENVELOPE? ────────────────────────────────────────┐
├─────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┤
│                 NO — FAIL CLOSED / RECHAZAR                 │                        SÍ — CONTINUAR                        │
├─────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
│ Pausar, reducir o retirar.                                  │ PASS OPERATIVO.                                              │
│ Revisar execution model y dependencias.                     │ Autorizar producción limitada y explícita.                   │
│ No reescribir el backtest histórico.                        │ Allocation y capacity caps fijados.                          │
│ Cambio material = vN+1 y nueva validación.                  │ Monitorización y kill criteria obligatorios.                 │
└─────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────┘
                                                         RUTA DE PASS                                                         
                                                              │                                                               
                                                              ▼                                                               
╔ 10 · CUÁNDO PUEDE DECIRSE QUE LA ESTRATEGIA ESTÁ «DADA POR BUENA» ═════════════════════════════════════════════════════════╗
║ NIVEL CIENTÍFICO  = VALIDATED CONDITIONAL EDGE: pasó verificación técnica + validación científica bloqueada.               ║
║ NIVEL OPERATIVO   = APPROVED FOR LIMITED PRODUCTION: además pasó shadow, reconciliación y live pilot limitado.             ║
║ AUTORIZACIÓN FINAL = condicional · acotada · versionada · auditable · revocable; nunca una certificación permanente.       ║
║ Scope obligatorio: versión · universo · régimen · horizonte · allocation · capacity · risk limits · dependencias.          ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
                                                              │                                                               
                                                              ▼                                                               
┌ 11 · MONITORIZACIÓN, DEGRADACIÓN Y RETIRADA ───────────────────────────────────────────────────────────────────────────────┐
│ La evidencia live no reescribe la historia; activa acciones predefinidas y, si hay cambio material, una nueva versión.     │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
┌ LIVE VS EXPECTED ────────────────────┐   ┌ DRIFT / BREAKS ──────────────────────┐   ┌ ACCIÓN PREDEFINIDA ──────────────────┐
│ Signal rate y expectancy.            │   │ Datos, estados y eventos.            │   │ Continue / reduce.                   │
│ Drawdown y tail losses.              │   │ Venue, regulación y borrow.          │   │ Pause / investigate.                 │
│ Fills, costes y capacity.            │──►│ Execution model y latencia.          │──►│ Retire / supersede.                  │
│ Concentración y utilización.         │   │ Régimen y degradación del edge.      │   │ Kill switch ante breach.             │
└──────────────────────────────────────┘   └──────────────────────────────────────┘   └──────────────────────────────────────┘
                                                              │                                                               
                                                              ▼                                                               
╔ ↺ BUCLE DE NUEVA VERSIÓN ══════════════════════════════════════════════════════════════════════════════════════════════════╗
║ Cambio material, decay, breach o retirada → cerrar vN → crear vN+1 + nuevo Experiment ID + nuevo Trial Ledger.             ║
║ Volver a la fase 1. Nunca modificar retroactivamente el contrato, los trials, el holdout ni la evidencia pasada.           ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```
