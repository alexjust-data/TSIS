# Trading Activity - Representation Landscape v0.1

Status: `representation_landscape_v0_1`
Date: `2026-07-20`
Scope: `post_domain_definition_pre_object_admission`

Este documento revisa el paisaje de modelos posibles para el dominio `Trading Activity`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona el modelo final.
No autoriza variables para `Market State` ni `Event State`.
No modifica tablas, schemas, builders, contratos ni datasets.  Su funcion es separar:

```text
Objeto candidato modelo de representacion especializacion temporal proxy compartido superficie de seleccion frontera con otro dominio
```

## Dominio

```text
Trading Activity
```

## Tesis Del Dominio

```text
Trading Activity preserva informacion sobre la intensidad con la que el mercado participa en la negociacion de un instrumento en una escala temporal declarada.
```

La informacion central no es:

```text
precio, direccion, spread, profundidad, agresion, outcome, ni seleccion del scanner.
```

La informacion central es:

```text
participacion negociada observable.
```

## Candidatos A Objeto Dentro Del Dominio 

| Candidato | Lectura cientifica | Decision pre-admision |
| --- | --- | --- |
| `Trading Activity` | Candidato principal. Preserva intensidad de participacion negociada. | `forward_to_object_admission` |
| `Daily Trading Activity` | Resolucion/modelo diario de `Trading Activity`. | `not_separate_object_by_default` |
| `Intraday Trading Activity` | Resolucion/modelo intradia de `Trading Activity`. | `not_separate_object_by_default` |
| `Relative Trading Activity` | Modelo normalizado contra baseline historico o esperado. | `representation_model_candidate` |
| `Participation Intensity` | Nombre semantico cercano al modelo central. | `representation_model_candidate` |
| `Attention Activity` | Puede ser superficie de seleccion o proxy de atencion. | `blocked_for_object_admission_until_selection_bias_review` |
| `Short Activity` | Procede de fuente short con lag y significado de crowding. | `move_to_short_side_context` |
| `Signed Flow / Aggressor Imbalance` | Introduce direccion y presion. | `move_to_order_flow_pressure` |

## Paisaje De Modelos De Representacion 

| Modelo candidato | Que intenta medir | Capacidades derivables relacionadas | Fuentes / tablas | Estado | Riesgo principal |
| --- | --- | --- | --- | --- | --- |
| `daily_absolute_participation_model` | Cuanto se negocio en la sesion diaria cerrada. | `daily__volume`, `daily__transaction_count`, `daily__dollar_volume` | OHLCV Daily; `004_master_daily_table` | `known_existing` | No es legal como input intradia antes del cierre si usa valor final del dia. |
| `daily_relative_participation_model` | Si la actividad diaria cerrada fue normal o anomala respecto a baseline historico. | `daily__volume_20d_avg`, `daily__rvol_20d`, `daily__volume_Nd_avg`, `daily__rvol_Nd`, `daily__dollar_volume_Nd_avg` | OHLCV Daily; `004_master_daily_table`; variantes futuras | `known_existing_plus_requires_variant` | Baseline debe usar solo sesiones previas; `rvol` final del dia no es decision-safe intradia. |
| `intraday_absolute_accumulation_model` | Cuanta actividad se ha acumulado desde apertura hasta `t`. | `intraday__bar_volume`, `intraday__bar_transaction_count`, `intraday__session_volume_to_time`, `intraday__session_dollar_volume_to_time` | OHLCV 1m; `013_ohlcv_1m_quote_guarded`; `014_master_intraday_bar_table_candidate` | `formula_defined_candidate_materialization` | Depende de barras cerradas, cobertura 1m y estado de 014. |
| `intraday_pace_model` | Si la actividad acumulada va rapida o lenta respecto a una expectativa para ese momento de sesion. | `intraday__volume_pace_W`, `intraday__dollar_volume_pace_W`, `intraday__bars_expected_to_time`, `intraday__bars_observed_to_time` | OHLCV 1m + calendario + baseline diaria; `014_master_intraday_bar_table_candidate` | `requires_variant` | Alto riesgo de ambiguedad si no se fija ventana, baseline, min_periods y calendario. |
| `trade_window_intensity_model` | Intensidad puntual del tape en una ventana cerrada. | `trades__trade_count_WINDOW`, `trades__trade_rate_WINDOW`, `trades__total_volume_WINDOW`, `trades__dollar_volume_WINDOW` | Trades; `015_microstructure_features_table_candidate` | `known_candidate_profile` |
Requiere ventana cerrada, min_rows y control de perfil general vs perfil de evento. |
| `trade_size_distribution_model` | Estructura de tamanos negociados dentro de una ventana. | `trades__size_median_WINDOW`, `trades__size_p90_WINDOW`, `trades__odd_lot_ratio_pct_WINDOW` | Trades; `015_microstructure_features_table_candidate` | `known_complementary` | Puede medir textura microestructural mas que actividad basica; no debe entrar en core sin justificacion. |
| `economic_turnover_model` | Cantidad economica negociada y, si existe fuente, rotacion relativa a float/share base. | `daily__dollar_volume`, `trades__dollar_volume_WINDOW`, `reference__float_pit_state` | `004_master_daily_table`; `015_microstructure_features_table_candidate`; reference/float PIT futuro | `partial_blocked_for_true_float_turnover` | True turnover requiere float PIT gobernado; hoy `reference__float_pit_state` esta bloqueado/no oficial. |
| `scanner_activity_threshold_model` | Uso de actividad como criterio para seleccionar candidatos donde mirar. | scanner thresholds, tradability threshold, motion/activity filters | `018_intraday_scanner_candidates_table` | `selection_surface_only` | La seleccion no prueba el Objeto; puede introducir selection bias. |
| `directional_activity_model` | Actividad con signo o agresion compradora/vendedora. | `trades__signed_flow_WINDOW`, `trades__aggressor_imbalance_WINDOW`, `trades__bid_hit_ask_lift_WINDOW` | Trades + Quotes; `015_microstructure_features_table_candidate` | `move_to_order_flow_pressure` | Cambia de intensidad no direccional a presion direccional. No debe mezclarse sin admision separada. |

## Capacidades Minimas Para Un Objeto Admitible  Para que `Trading Activity` pueda pasar a `Object Admission`, el expediente debe poder defender al menos un modelo minimo decision-safe.  Modelo minimo candidato:

```text
Trading Activity  -> daily historical baseline  -> intraday closed-bar accumulation  -> optional trade-window intensity extension
```

Capacidades nucleares:

```text
daily__volume daily__transaction_count daily__dollar_volume daily__volume_20d_avg daily__rvol_20d intraday__bar_volume intraday__bar_transaction_count intraday__session_volume_to_time intraday__session_dollar_volume_to_time trades__trade_count_WINDOW trades__total_volume_WINDOW trades__dollar_volume_WINDOW
```

Restriccion:

```text
El core intradia no puede usar volumen diario final del mismo dia antes del cierre.
```

## Modelos Que Podrian Ser Redundantes

```text
Daily Trading Activity vs Intraday Trading Activity:  No son Objetos distintos por defecto. Son resoluciones/modelos temporales del mismo Objeto candidato.
```

```text
Relative Volume vs Volume Pace:  Ambos normalizan actividad contra una expectativa. La diferencia debe quedar en el modelo: - `rvol` final diario o historico cerrado; - `pace` intradia as-of contra expectativa a tiempo t.
```

```text
Trade Count vs Transaction Count:  Pueden representar intensidad de prints, pero proceden de fuentes y granularidades distintas. No deben duplicarse sin declarar fuente, ventana y rol.
```

```text
Dollar Volume vs Total Volume:  No son equivalentes. `volume` mide cantidad de acciones. `dollar_volume` mide cantidad economica negociada. Ambas pueden ser necesarias si el modelo distingue participacion fisica y economica.
```

## Modelos Que
Requieren Separacion

```text
Signed Flow / Aggressor Imbalance:  Debe separarse hacia `Order Flow Pressure` porque introduce direccion, agresion y consumo de liquidez. Trading Activity es intensidad principalmente no direccional.
```

```text
Spread / Depth / Quote Update Rate:  Deben separarse hacia `Liquidity` o `Market Microstructure State`. Pueden contextualizar actividad, pero no son participacion negociada.
```

```text
Short Activity:  Debe separarse hacia `Short-Side Context` porque su fuente, lag y significado son distintos de la actividad negociada intradia observable.
```

```text
Attention Activity / Scanner Activity:  Debe separarse hacia `Selection Surfaces` salvo que se pruebe que representa una propiedad observable independiente y no solo una regla de seleccion.
```

## Modelos Bloqueados O No Listos

```text
true_float_turnover_model: blocked_reason:  requiere float point-in-time gobernado. missing_source_or_policy:  `reference__float_pit_state` esta marcado como blocked/no official.
```

```text
attention_activity_object_model: blocked_reason:  mezcla actividad observable con seleccion de scanner. missing_source_or_policy:  falta revision de selection bias y definicion de atencion observable independiente.
```

```text
directional_activity_model: blocked_reason:  pertenece mejor a `Order Flow Pressure`. missing_source_or_policy:  requiere trade-quote alignment, side classifier y confidence policy.
```

## Fronteras Para La Admision  El expediente formal de admision de `Trading Activity` debe responder:

```text
1. Cual es la definicion minima de participacion negociada?  2. Que modelos son core y cuales extension?  3. Que resoluciones son necesarias:  daily, intraday_bar, event_window?  4. Que variables son decision-safe en `decision_timestamp`?  5. Como se evita usar volumen final diario antes del cierre?  6. Como se separa actividad de liquidez,  microestructura y order flow direccional?  7. Que se pierde si `Trading Activity` no entra en Market State?  8. Que consumidores necesitan solo core  y cuales necesitan extensiones pesadas?
```

## Recomendacion Para Object Admission

```text
Abrir un unico expediente candidato:  Trading Activity
```

No abrir todavia expedientes separados para:

```text
Daily Trading Activity Intraday Trading Activity Relative Trading Activity Participation Intensity Attention Activity Short Activity
```

Lectura:

```text
Daily, intraday, relative y window-based son modelos/perfiles. Attention es superficie de seleccion. Short Activity pertenece a Short-Side Context. Signed/aggressor pertenece a Order Flow Pressure.
```

## Decision Del Landscape

```text
decision = ready_to_define_candidate_object
```

Motivo:

```text
Existe un Objeto candidato coherente: `Trading Activity`. El paisaje de modelos muestra que el dominio es representable con capacidades disponibles o variantes gobernables.  Tambien muestra que varios nombres detectados no deben convertirse en Objetos separados por defecto.
```

## Resultado Posterior

```text
Candidate Object Definition creado en:  C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\ 03_TABLES_feature_engineering\ 03_INFORMATION_OBJECTS\ CANDIDATES\ trading_activity_candidate_object_definition_v0_1.md
```

## Siguiente Paso

```text
Crear operational mapping:  Trading Activity  -> modelos  -> capacidades derivables  -> variables fisicas  -> tablas fuente  -> perfiles de State
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\02_DOMAIN_DEFINITION_TEMPLATE_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\03_REPRESENTATION_LANDSCAPE_TEMPLATE_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\trading_activity_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\015\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\018\table_representation_audit_ES.md
```
