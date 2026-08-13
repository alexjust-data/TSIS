# Evidence Index - Screener Engine Architecture Proposal v0.1

Fecha: 2026-08-12  
Estado: `evidence_bundle_index`  
Documento principal: `SCREENER_ENGINE_ARCHITECTURE_PROPOSAL_v0_1.md`

## Regla de lectura

Las copias incluidas permiten revisar el razonamiento sin depender de rutas
externas al ZIP. No crean una nueva source of truth. La autoridad sigue siendo
el archivo original en el repositorio y su estado de promocion declarado.

`SHA256SUMS.txt` contiene el hash de cada archivo empaquetado. Los nombres se
conservan bajo `evidence/repository/` siguiendo su ruta relativa desde
`C:/TSIS_Data`.

## 1. Gobierno y arquitectura TSIS

| Fuente | Justificacion |
| --- | --- |
| `AGENTS.md` | Separacion de capas, trazabilidad, versionado y gates obligatorios. |
| `PROJECT_OPERATING_SYSTEM.md` | Mapa institucional y responsabilidades entre modulos. |
| `PROJECT_RULES.md` | Reglas generales de cambio y autoridad. |
| `VERSIONING_STANDARDS.md` | Versionado de contratos, datasets, runs y artefactos. |
| `RESEARCH_PHILOSOPHY.md` | Causalidad, leakage, outcomes separados y claims cientificos. |
| `00_CTO/LOCAL_RULES.md` | Rol conceptual de CTO y prohibicion de duplicar Data Foundation. |
| `00_CTO/TSIS_LAB_ARCHITECTURE_v3.md` | Separacion entre observables, estados, experimentos y decisiones. |

## 2. Autoridad Backtest Engine

| Fuente | Justificacion |
| --- | --- |
| `00_CTO/14_BACKTEST_ENGINE/01_GUIDE/01_DATA.md` | Universe policy, PIT legality, preflight y manifests requeridos. |
| `00_CTO/14_BACKTEST_ENGINE/00_CTO/00_SERSANS_SISTEMAS/00_SERSANS_SISTEMAS_YOUTUBE/Small Caps el backtest NO te prepara para esto  1 mes en real/ideas_extraidas/SERSAN_BOOK_EVIDENCE_MATRIX.md` | Evidencia bibliografica destilada para datos/scanners/backtest. |
| `02_TSIS_BACKTEST_ENGINE/docs/00_system/CURRENT_PROJECT_HANDOFF.md` | Gates cerrados y `BT-GATE-016` no abierto/no autorizado. |
| `02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/preflight/contracts.py` | Contratos actuales de universo y contexto resuelto. |
| `02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/preflight/registries.py` | Registry de universo estatico actual. |
| `02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/preflight/run_preflight.py` | Resolucion y validacion preflight actual. |

## 3. Precedentes conceptuales de scanner

Se incluye el corpus Markdown completo de:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/
00_SCANNER_CANDIDATE_SELECTION
```

Justifica la separacion entre base eligible, perfiles, In-Play, strategy overlay,
state y outcome. Tambien permite auditar la evolucion v0.1 -> v0.2 -> v0.3 y la
divergencia deliberada de esta propuesta: In-Play pasa a ser una familia de
scanners especificos, no un unico denominador universal.

## 4. Parent frame y selector PIT presesion

| Fuente | Justificacion |
| --- | --- |
| `01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/universes/lt1b_universe_schema_contract.md` | Procedencia y limitaciones de los 4.824 instrumentos. |
| `00_CTO/04_MARKET_STATES_CREATION/VARIABLES_FEATURES/POPULATION_TARGET_PRESESSION_4824_SELECTOR_CONTRACT_v0_2.md` | Formula, cutoff, identity, TTL, fronteras y non-claims. |
| `.../POPULATION_TARGET_PRESESSION_4824_SELECTOR_GATE_READOUT_v0_1.md` | Gate `PASS_WITH_RESTRICTIONS` y resultados de probes. |
| `.../POPULATION_TARGET_PRESESSION_4824_FULL_MATERIALIZATION_CLOSEOUT_v0_1.md` | Cobertura, counts y promotion state. |
| `.../evidence_assets/population_target_presession_4824_full_materialization_final_manifest_v0_1.json` | Identidad y lineage del run. |
| `.../evidence_assets/population_target_presession_4824_full_materialization_summary_v0_1.json` | Accounting agregado. |
| `.../evidence_assets/population_target_presession_4824_full_materialization_validation_v0_2.json` | Resultado machine-readable de validacion. |
| `01_TSIS_DATA_FOUNDATION/configs/population_target_presession_4824_audit_v0_1.json` | Policy/config de auditoria. |

## 5. Scanner diario anterior

| Fuente | Justificacion |
| --- | --- |
| `scanner_framework_and_definitions_contract_v0_3.md` | Semantica base eligible e In-Play Momentum anterior. |
| `daily_scanner_candidates_table_target_contract_v0_3.md` | Alcance y restricciones del replay diario/EOD. |
| `base_eligible_smallcap_denominator_v0_3.yaml` | Thresholds ejecutables anteriores. |
| `in_play_momentum_candidate_denominator_v0_3.yaml` | Thresholds In-Play Momentum anteriores. |
| `materialize_daily_scanner_candidates_table_v0_3.py` | Evidencia de implementacion y reloj EOD del builder anterior. |
| `test_daily_scanner_candidates_table_builder_v0_3.py` | Fixtures existentes. |

Estas fuentes se incluyen para demostrar por que el builder EOD no debe
reutilizarse silenciosamente como selector presesion.

## 6. Biblioteca procesada

| Fuente procesada | Uso |
| --- | --- |
| `quantitative_trading_chan_concept_index.md` | Look-ahead, survivorship, PIT, low-priced stocks y reproducibilidad. |
| `algorithmic_trading_chan_concept_index.md` | Corporate actions y membership historica. |
| `trading_systems_urban_jaekle_concept_index.md` | Calidad, vendor, delistings y ranking. |
| `fundamentals_data_engineering_reis_source_map.md` | Tipos de tiempo, lineage y governance. |
| `designing_data_intensive_applications_kleppmann_source_map.md` | Source of record, replay y schema evolution. |
| `trading_and_exchanges_harris_source_map.md` | Liquidez, spread y execution realism para futuros In-Play scanners. |

Solo se incluyen indices y source maps procesados, no libros completos. Las
referencias externas orientan el diseÃ±o, pero no gobiernan TSIS sin destilacion
y promocion.

## 7. Alcance y limitaciones del paquete

El paquete:

- documenta una propuesta;
- conserva evidencia revisable;
- no contiene datasets pesados ni parquets;
- no contiene outputs runtime;
- no abre gates;
- no crea el motor ejecutable;
- no promueve el candidato presesion a canonical;
- no sustituye los originales del repositorio.


