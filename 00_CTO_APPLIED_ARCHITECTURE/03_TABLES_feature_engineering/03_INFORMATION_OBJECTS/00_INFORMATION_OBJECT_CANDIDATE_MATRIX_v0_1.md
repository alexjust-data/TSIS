# Information Object Candidate Matrix v0.1

Status: `candidate_normalization_matrix_v0_1`
Date: `2026-07-20`
Scope: `post_discovery_pre_admission`

Este documento consolida los candidatos a `Objeto de Informacion` detectados en la primera pasada de revision de tablas `000-018`.

No admite Objetos.
No rechaza Objetos.
No autoriza variables para `Market State` ni `Event State`.
No cambia schemas, builders, contratos ni datasets fisicos.

Su funcion es evitar duplicados antes de abrir expedientes formales de admision.

## Pregunta

```text
De los candidatos descubiertos en las tablas 000-018:

cuales parecen Objetos de Informacion reales,
cuales son Modelos de Representacion,
cuales son especializaciones temporales,
cuales son contexto,
cuales son calidad/gobernanza,
y cuales no deben entrar como inputs observables de State?
```

## Regla De Lectura

```text
Discovery Pass
    -> Candidate Consolidation
        -> Candidate Normalization
            -> Object Admission
                -> Operational Mapping
```

La matriz pertenece a `Candidate Normalization`.

## Vocabulario De Clasificacion

| Valor | Significado |
| --- | --- |
| `candidate_information_object` | Puede ser un Objeto de Informacion real, pendiente de admision. |
| `representation_model` | Describe como representar un Objeto, no el Objeto en si. |
| `temporal_specialization` | Es una version daily, intraday, event-window o as-of de un Objeto mas general. |
| `context_object` | Preserva contexto necesario para interpretar estado, eventos o consumo. |
| `infrastructure_object` | Preserva infraestructura institucional, temporal o de identidad. |
| `quality_governance_object` | Preserva calidad, cobertura, certificacion, lineage o permiso de consumo. |
| `canonical_core_representation` | Es una representacion core como `Market State` o `Event State`, no un Objeto comun. |
| `outcome_layer_only` | Pertenece a outcomes/labels; no puede ser input observable de State. |
| `selection_surface` | Superficie de candidatos o scanner; no implica por si sola Objeto admitido. |
| `blocked_pending_evidence` | Falta evidencia, fuente, formula, politica temporal o contrato. |

## Matriz Consolidada

| Candidato normalizado | Que representa con la informacion actual | Candidatos crudos agrupados | Evidencia en tablas | Clasificacion provisional | Posible padre | Modelos / especializaciones probables | Capacidades relacionadas | Riesgo antes de admision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Instrument Identity` | La identidad estable y trazable del instrumento: simbolo, instrumento, exchange/security class y continuidad de identidad. | `Instrument Identity`, `Listing Status`, `Identity Lifecycle Change` | `000_instrument_master`, `005_corporate_actions_table` | `infrastructure_object` | n/a | identity/lifecycle model; listing status model | symbol resolution; identity as-of lookup; exchange/security classification; ticker-change lookup | No confundir identidad institucional con senal de mercado. Debe gobernar joins, universos y as-of, no predecir por si misma. |
| `Universe Membership` | Pertenencia del instrumento al universo TSIS bajo reglas de vigencia, elegibilidad y cobertura. | `Universe Membership`, `Listing Status` | `000_instrument_master` | `infrastructure_object` | `Instrument Identity` | universe membership model; active listing model | universe lookup; active/as-of eligibility | Debe diferenciar universo investigable, universo consumible y universo operativo. |
| `Trading Session Context` | Disponibilidad temporal del mercado: sesiones, apertura, cierre, festivos, early closes y pertenencia de un timestamp a una sesion. | `Trading Session Context`, `Temporal Observability Boundary` | `001_market_calendar`, `007_event_windows_table` | `context_object` + `infrastructure_object` | n/a | session availability model; calendar cutoff model; event-relative calendar model | session lookup; timestamp-in-session classification; expected session denominator | Es contexto temporal, no Feature Family. Debe alimentar legalidad temporal de 014/016/017. |
| `Observability Coverage` | Que datos se esperaban y que datos existen para un instrumento, dia, fuente o ventana. | `Dataset Expectedness`, `Observability Coverage` | `002_expected_data_calendar`, `003_dataset_certification_matrix`, `013_ohlcv_1m_quote_guarded` | `quality_governance_object` | n/a | expected-vs-present model; coverage denominator model | expected data lookup; missingness interpretation; missing bar count/ratio | No debe entrar como alfa salvo como calidad/coverage. Debe controlar si una observacion es interpretable. |
| `Dataset Consumption Eligibility` | Permiso institucional de consumo de un dataset segun estado, certificacion, scope y politica. | `Dataset Consumption Eligibility`, `Representation Quality State`, `State Quality` | `003_dataset_certification_matrix`, `016_market_state_table` | `quality_governance_object` | n/a | gate/verdict model; status matrix model; quality propagation model | dataset gate lookup; root status lookup; quality verdict propagation | No es informacion del mercado. Es un gate de consumo. |
| `Representation Quality State` | Calidad de la representacion fisica o derivada: integridad de precio, cobertura, lineage de reparacion y validez para consumo. | `Representation Quality State`, `Price Integrity State`, `State Quality`, `Intraday Bar Observability` | `003_dataset_certification_matrix`, `013_ohlcv_1m_quote_guarded`, `016_market_state_table` | `quality_governance_object` | `Observability Coverage` | price integrity model; repair lineage model; state quality model | guarded repair state; validation lineage; price integrity flags; quality propagation | Puede viajar con State como metadata/gate, pero no debe confundirse con fenomeno economico. |
| `Price Dynamics` | Movimiento observable del precio en distintas escalas: retornos, direccion, pendiente, aceleracion y localizacion contra referencias. | `Daily Price State`, `Intraday Price Dynamics`, `Overnight Dislocation`, `Intraday Position` | `004_master_daily_table`, `014_master_intraday_bar_table`, `013_ohlcv_1m_quote_guarded` | `candidate_information_object` | n/a | daily OHLC reference model; gap model; bar return/slope model; session reference model | daily return; intraday return; gap percent; bar return; move speed; move acceleration; VWAP distance; distance to references | No mezclar escala temporal con Objeto. `Daily` e `Intraday` son perfiles/modelos, no Objetos separados por defecto. |
| `Volatility / Range State` | Amplitud e incertidumbre observada del movimiento: rango diario, rango intradia y dispersion historica o de ventana. | `Daily Volatility Range`, `Intraday Volatility` | `004_master_daily_table`, `014_master_intraday_bar_table` | `candidate_information_object` | `Price Dynamics` posible, o Objeto separado | range model; rolling volatility model; expansion/compression model | daily range pct; intraday range so far; daily volatility_Nd; range_Nd | Decidir si es submodelo de `Price Dynamics` o Objeto propio. |
| `Trading Activity` | Intensidad de participacion negociada: volumen, dollar volume, transacciones, ritmo, actividad relativa y actividad por ventana. | `Daily Trading Activity`, `Intraday Trading Activity`, `Trading Activity`, `Attention Activity Candidate` parcial | `004_master_daily_table`, `014_master_intraday_bar_table`, `015_microstructure_features_table`, `018_intraday_scanner_candidates_table` | `candidate_information_object` | n/a | daily participation model; intraday volume pace model; trade intensity model; relative activity model | volume; dollar volume; transaction count; rvol; volume pace; trade count/rate; total volume window; dollar volume window | `Daily` e `Intraday` deben tratarse como modelos/resoluciones. `Attention Activity` puede ser solo seleccion de scanner. |
| `Liquidity` | Facilidad/coste de negociar: spread, profundidad visible, actividad suficiente, coste esperado y disponibilidad de liquidez. | `Liquidity` | `015_microstructure_features_table`; proxies en `004_master_daily_table` y `014_master_intraday_bar_table` | `candidate_information_object` | n/a | spread/depth model; tradability proxy model; liquidity availability model | spread bps; top depth; quote count/update rate; dollar volume; trade count; effective spread candidates | Distinguir liquidez real L1/trades de proxies diarios. No meter todos los proxies en core State sin perfil. |
| `Market Microstructure State` | Estado operativo del libro/tape L1: condiciones de quotes, locked/crossed, actualizacion, estado de profundidad y textura microestructural. | `Market Microstructure State`, `Regulatory Venue Interruption` parcial | `015_microstructure_features_table`, `006_halts_table` | `candidate_information_object` | n/a | quote condition model; top-of-book state model; microstructure interruption model | quote count; locked/crossed ratio; two-sided rows; quote update rate; depth; halt presence | Debe separar microestructura continua de eventos de interrupcion como halts. |
| `Order Flow Pressure` | Presion direccional inferida desde trades y quotes: agresion compradora/vendedora, signed flow, imbalance y consumo de liquidez. | `Order Flow Pressure` | `015_microstructure_features_table` | `candidate_information_object` | `Market Microstructure State` posible | signed flow model; aggressor imbalance model; OFI model | bid-hit/ask-lift; signed flow; aggressor imbalance; OFI candidates | Muchas capacidades estan en estado `candidate`; requiere alignment trade-quote y confianza de clasificacion. |
| `Halt Context` | Interrupcion regulatoria o de venue: presencia de halt, tipo, tiempo desde halt/resumption y clustering. | `Halt Context`, `Regulatory Venue Interruption` | `006_halts_table`, `007_event_windows_table` | `context_object` | `Market Microstructure State` relacionado, no identico | trading interruption model; halt classification model; event-window model | halt presence; halt type; time since halt/resume; halt clustering | No confundir fuente de evento con Event State. Debe definir consumo pre/at/post y outcome adjacency. |
| `Event Window Context` | Marco temporal gobernado alrededor de un evento/candidato: pre, at, post, ventana y elegibilidad de corte. | `Event Window Context`, `Event Relative Time` | `007_event_windows_table`, `017_event_state_table` | `context_object` + `infrastructure_object` | n/a | event-relative window model; window eligibility model | pre/at/post windows; event-relative slicing; window eligibility | Es infraestructura de eventos, no resultado ni evento en si mismo. Debe mapear a `state_role` y `consumption_legality`. |
| `Outcome Response` | Respuesta futura posterior: retornos futuros, MFE, MAE, break/failure y labels de evaluacion. | `Outcome Response`, `Future Return Label`, `MFE MAE Response` | `008_outcomes_table` | `outcome_layer_only` | n/a | future response label model; outcome horizon model | future returns; MFE/MAE; break/failure labels | Prohibido como input observable de Market State/Event State. Solo evaluacion, labels o research posterior. |
| `Fundamental Context` | Contexto fundamental point-in-time: tamano, estructura financiera, float, shares, market cap y antiguedad de filing. | `Fundamental Context`, `Capital Structure Context` | `009_fundamentals_asof_table`, `000_instrument_master` posible | `candidate_information_object` | `Instrument Context` relacionado | PIT fundamental model; capital structure model | float lookup; shares/market cap context; filing age | Debe probar disponibilidad PIT/as-of y evitar leakage por revisiones posteriores. |
| `News / Catalyst Context` | Informacion externa reciente que puede alterar el estado: presencia de noticia, edad, tipo, categoria, fuente y relevancia. | `News Context`, `Catalyst Context`, `News Recency` | `010_news_context_table`, `007_event_windows_table` | `candidate_information_object` | n/a | news availability model; catalyst classification model; news recency model | news presence; news age; source type; topic/category | Debe probar disponibilidad por vendor/as-of. `Catalyst` puede ser modelo de `News Context` o Objeto separado. |
| `Short-Side Context` | Presion/crowding short observable con lag: short volume, short ratio, days to cover, anomalia y restricciones. | `Short-Side Context`, `Short Activity`, `Crowding Context` | `011_short_context_table` | `candidate_information_object` | `Trading Activity` relacionado, no fusionar aun | short interest/activity model; source-lag model; crowding model | short volume ratio; days to cover; short activity anomaly; SSR state candidate | No fusionar automaticamente con `Trading Activity`: fuente, lag y semantica son distintas. Borrow availability esta bloqueado si no hay fuente real. |
| `Broad Market Context` | Contexto externo de mercado general: indice, volatilidad proxy, risk-on/off y entorno macro/mercado disponible as-of. | `Market Regime`, `Broad Market Context` | `012_regime_context_table` | `candidate_information_object` | n/a | broad market proxy model; regime context model | index return; volatility proxy; risk-on/off state | Decidir si `Market Regime` es Objeto o modelo de `Broad Market Context`. Revisar flags `valid_for_state/ml`. |
| `Market State` | Integracion canonica observable en `decision_timestamp` de Objetos admitidos y perfiles compatibles. | `Market State`, `State Quality` parcial | `016_market_state_table` | `canonical_core_representation` | n/a | profiled state integration model; core plus extension model | legal as-of integration; profile selection; quality propagation | No es Objeto comun. Se construye a partir de Objetos admitidos, no de candidatos. Evitar mega-tabla universal. |
| `Event State` | `Market State` contextualizado respecto a evento/ventana, con `state_role` y `consumption_legality` separados. | `Event State`, `Event Relative Context` | `017_event_state_table`, `007_event_windows_table` | `canonical_core_representation` | n/a | event-relative state model; state_role + consumption_legality model | pre/at/post state role; relative timing; consumption legality | No crea eventos. Depende de evento gobernado, ventanas y Market State. `post_event` no implica input legal. |
| `Intraday In-Play Candidate` | Superficie de seleccion que indica donde mirar intradia segun thresholds, scanner lineage y condiciones de actividad. | `Intraday In-Play Candidate`, `Attention Activity Candidate` | `018_intraday_scanner_candidates_table` | `selection_surface` | `Trading Activity` o `News / Catalyst Context` posible | scanner selection model; threshold/gate model | candidate selection; motion threshold; tradability threshold; scanner lineage | No admitir como Objeto hasta separar senal de seleccion, atencion observable y sesgo de muestreo. |

## Agrupaciones Que No Deben Abrirse Como Objetos Separados Todavia

| Nombre detectado | Lectura recomendada |
| --- | --- |
| `Daily Trading Activity` | Especializacion temporal de `Trading Activity`, no Objeto independiente por defecto. |
| `Intraday Trading Activity` | Especializacion temporal/modelo de `Trading Activity`. |
| `Short Activity` | Candidato relacionado con `Short-Side Context`; no fusionar aun con `Trading Activity` por lag y fuente. |
| `Attention Activity Candidate` | Puede ser una superficie de seleccion o proxy de atencion; requiere revision antes de llamarlo Objeto. |
| `Daily Price State` | Modelo/perfil diario de `Price Dynamics`. |
| `Intraday Price Dynamics` | Modelo/perfil intradia de `Price Dynamics`. |
| `Overnight Dislocation` | Posible subobjeto o modelo de gap dentro de `Price Dynamics`; no abrir como Objeto hasta comparar con `Price Dynamics`. |
| `Market Regime` | Puede ser modelo de `Broad Market Context` o Objeto propio; requiere decision explicita. |
| `State Quality` | Metadata/gate de calidad de State; no es fenomeno de mercado. |
| `Future Return Label` | Outcome/label, no input observable. |
| `MFE MAE Response` | Outcome/label, no input observable. |

## Orden Propuesto De Admision

No abrir todos los expedientes a la vez.

Primero admitir los Objetos con mayor valor estructural para `Market State` y `Event State`:

```text
1. Trading Activity
2. Liquidity
3. Price Dynamics
4. Volatility / Range State
5. Market Microstructure State
6. Order Flow Pressure
7. News / Catalyst Context
8. Fundamental Context
9. Short-Side Context
10. Broad Market Context
11. Halt Context
12. Trading Session Context
```

Los objetos de calidad, cobertura e infraestructura deben seguir un carril paralelo de gobernanza:

```text
Instrument Identity
Universe Membership
Observability Coverage
Dataset Consumption Eligibility
Representation Quality State
Event Window Context
```

Los siguientes no deben pasar a admision como input observable de State:

```text
Outcome Response
Future Return Label
MFE MAE Response
Intraday In-Play Candidate
```

`Intraday In-Play Candidate` puede revisarse despues como `selection_surface` o como posible contexto de atencion, pero no como Objeto admitido sin separar scanner, sesgo de seleccion y legalidad temporal.

## Proxima Accion

No abrir todavia expedientes individuales de admision.

Antes debe ejecutarse:

```text
Semantic Domain Consolidation
```

Motivo:

```text
La matriz mezcla candidatos de distinta naturaleza:
Objetos posibles,
Modelos de Representacion,
especializaciones temporales,
contextos,
calidad/gobernanza,
outcomes
y superficies de seleccion.
```

Primero deben consolidarse clusters semanticos para no admitir duplicados como Objetos separados.

Referencia activa:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
```

Despues se abriran expedientes solo para candidatos normalizados, no para cada nombre crudo.

Cada expediente debe reconstruir:

```text
fenomeno_o_necesidad_cientifica
    -> Objeto de Informacion
        -> Modelo de Representacion
            -> capacidades derivables
                -> variables fisicas candidatas
                    -> tablas fuente
                        -> legalidad temporal
                            -> decision de admision
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\00_DISCOVERY_PASS_000_018_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\000_instrument_master\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\001_market_calendar\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\002_expected_data_calendar\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\003_dataset_certification_matrix\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\005_corporate_actions_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\006_halts_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\007_event_windows_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\008_outcomes_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\009_fundamentals_asof_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\010_news_context_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\011_short_context_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\012_regime_context_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\013_ohlcv_1m_quote_guarded\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\015\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\016\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\017\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\018\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

## Decision De Esta Matriz

```text
discovery_pass_reviewed = true
candidate_consolidation_required = true
semantic_domain_consolidation_required = true
object_admission_started = false
objects_admitted = 0
state_consumption_authorized = false
next_step = semantic_domain_consolidation
```
