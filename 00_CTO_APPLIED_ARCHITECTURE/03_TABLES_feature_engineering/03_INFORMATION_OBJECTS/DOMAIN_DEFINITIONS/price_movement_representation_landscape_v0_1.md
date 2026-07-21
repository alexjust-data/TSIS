# Price Movement - Representation Landscape v0.1

Status: `representation_landscape_v0_1`
Date: `2026-07-20`
Scope: `post_domain_definition_pre_object_admission`

Este documento revisa el paisaje de modelos posibles para el dominio `Price Movement`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona el modelo final.
No autoriza variables para `Market State` ni `Event State`.
No modifica tablas, schemas, builders, contratos ni datasets.

## Dominio

```text
Price Movement
```

## Tesis Del Dominio

```text
Price Movement preserva informacion sobre como cambia el precio: direccion, magnitud, velocidad, aceleracion, continuidad y persistencia del desplazamiento en una escala temporal legal.
```

No responde principalmente:

```text
donde esta el precio, cuanta amplitud tiene el rango, cuanto volumen acompana, cuanto cuesta negociar, ni que retorno futuro ocurrio.
```

## Candidatos A Objeto Dentro Del Dominio 

| Candidato | Lectura cientifica | Decision pre-admision |
| --- | --- | --- |
| `Price Movement` | Candidato principal. Preserva cambio observable del precio. | `forward_to_object_admission` |
| `Daily Price State` | Perfil/resolucion diaria de movimiento y referencias diarias. | `not_separate_object_by_default` |
| `Intraday Price Dynamics` | Perfil/resolucion intradia del mismo Objeto. | `not_separate_object_by_default` |
| `Momentum` | Persistencia direccional del movimiento. | `representation_model_or_subobject_candidate` |
| `Opening Gap Movement` | Cambio discontinuo entre cierre previo y apertura. | `representation_model_candidate` |
| `Price Speed` | Tasa de cambio por unidad temporal. | `representation_model_candidate` |
| `Price Acceleration` | Cambio en la velocidad del precio. | `representation_model_candidate` |
| `Reversal / Fade` | Cambio de direccion o perdida de continuidad. | `representation_model_or_adjacent_pattern_candidate` |
| `Price Location / Structure` | Posicion contra referencias. | `move_to_price_location_structure` |
| `Volatility / Range` | Amplitud/dispersion del movimiento. | `move_to_volatility_range_state` |
| `Future Return` | Movimiento posterior usado como label/outcome. | `prohibited_as_state_input` |

## Paisaje De Modelos De Representacion 

| Modelo candidato | Que intenta medir | Capacidades derivables relacionadas | Fuentes / tablas | Estado | Riesgo principal |
| --- | --- | --- | --- | --- | --- |
| `daily_close_to_close_movement_model` | Cambio diario completo contra cierre previo. | `daily__daily_return_pct`, `daily__prior_close`, `daily__close_price` | OHLCV Daily; `004_master_daily_table` | `known_existing` | No es legal antes de market close para el dia actual. |
| `daily_open_to_close_movement_model` | Cambio dentro de la sesion diaria cerrada. | `daily__intraday_return_pct`, `daily__open_price`, `daily__close_price` | OHLCV Daily; `004_master_daily_table` | `known_existing` | Solo es final al cierre; no decision-safe intradia. |
| `opening_gap_movement_model` | Cambio discontinuo desde cierre previo a apertura. | `daily__gap_pct`, `daily__open_price`, `daily__prior_close` | OHLCV Daily; `004_master_daily_table` | `known_existing` | Debe separarse de distancia posterior a prior close. |
| `intraday_return_to_reference_model` | Cambio as-of contra apertura, cierre previo o segmento. | `intraday__return_vs_prior_close_ratio`, `intraday__return_vs_session_open_ratio`, `intraday__return_vs_segment_open_ratio` | OHLCV 1m + Daily; `014_master_intraday_bar_table_candidate`; state builder futuro | `formula_defined` |
Requiere declarar `price_ref`, segmento y corte legal. |
| `bar_to_bar_movement_model` | Cambio entre barras cerradas consecutivas o ventanas cortas. | `intraday__bar_open_price`, `intraday__bar_close_price`; derivacion candidata de bar return | OHLCV 1m; `013_ohlcv_1m_quote_guarded`; `014_master_intraday_bar_table_candidate` | `candidate_requires_register_id` | Falta `bar_return` atomico explicito en el register actual. |
| `move_speed_model` | Velocidad del movimiento en ventana W. | `intraday__move_speed_W` | OHLCV 1m; `014_master_intraday_bar_table_candidate` | `requires_variant` |
Requiere W, return_ref, price_ref, segment scope y min_periods. |
| `move_acceleration_model` | Cambio en la velocidad del movimiento. | `intraday__move_acceleration_W` | OHLCV 1m; `014_master_intraday_bar_table_candidate` | `requires_variant` | Sensible a ruido de 1m y a ventanas pequenas. |
| `momentum_persistence_model` | Persistencia direccional de cambios recientes. | returns/speed sequence; possible `move_speed_W` | OHLCV 1m / Daily | `candidate_requires_formula` | No debe llamarse `Price Movement` completo; mide persistencia, no todo cambio. |
| `reversal_fade_model` | Perdida de continuidad o cambio de direccion. | return sequence; `intraday__pullback_ratio_W`, `intraday__retrace_ratio_W` as boundary inputs | OHLCV 1m | `candidate_boundary_model` | Puede pertenecer a Price Structure o pattern research, no necesariamente core State. |
| `future_response_model` | Movimiento posterior tras t. | `future__future_return_H`, `future__mfe_H`, `future__mae_H` | `008_outcomes_table` | `prohibited_as_feature` | Es outcome/label. Prohibido como input observable. |

## Capacidades Minimas Para Un Objeto Admitible  Para que `Price Movement` pueda pasar a `Object Admission`, el expediente debe poder defender un modelo minimo que no use futuro.  Modelo minimo candidato:

```text
Price Movement  -> opening gap movement  -> as-of intraday return to legal reference  -> optional speed / acceleration extension
```

Capacidades nucleares:

```text
daily__prior_close daily__gap_pct intraday__bar_close_price intraday__return_vs_prior_close_ratio intraday__return_vs_session_open_ratio intraday__move_speed_W
```

Capacidades de extension:

```text
intraday__return_vs_segment_open_ratio intraday__move_acceleration_W daily__daily_return_pct daily__intraday_return_pct
```

Restriccion:

```text
Las capacidades daily final solo son decision-safe tras el cierre o como historico previo.
```

## Modelos Que Podrian Ser Redundantes

```text
Daily Price State vs Intraday Price Dynamics:  No son Objetos distintos por defecto. Son resoluciones/perfiles temporales de Price Movement.
```

```text
Momentum vs Move Speed:  `move_speed` mide tasa de cambio. `momentum` requiere persistencia direccional. No deben fusionarse sin definir horizonte y persistencia.
```

```text
Opening Gap vs Return vs Prior Close:  El gap mide cambio discontinuo al abrir. Return vs prior close en t mide cambio acumulado respecto al cierre previo. Comparten referencia pero no son identicos.
```

## Modelos Que
Requieren Separacion

```text
Price Location / Structure:  VWAP distance, distance to HOD/LOD/open/prior close miden posicion relativa, no cambio puro.
```

```text
Volatility / Range State:  Range, rolling volatility, compression y expansion miden amplitud/dispersion, no direccion o velocidad.
```

```text
Outcome Response:  Future return, MFE y MAE son respuestas posteriores. No pueden entrar como informacion observable del estado en t.
```

```text
Pattern/Strategy Events:  First high push, rebreak, pullback y setup-specific labels no son el dominio Price Movement completo. Pueden usar Price Movement como input.
```

## Modelos Bloqueados O No Listos

```text
bar_to_bar_return_model: blocked_reason:  el register actual no declara una capacidad canonica atomica `intraday__bar_return`. missing_source_or_policy:  falta decidir si se anade como capacidad derivable o se expresa mediante return_vs_reference.
```

```text
momentum_persistence_model: blocked_reason:  requiere definir persistencia, horizonte, min_periods y tolerancia a ruido. missing_source_or_policy:  formula canonica no cerrada.
```

```text
reversal_fade_model: blocked_reason:  puede pertenecer a pattern discovery o Price Location / Structure. missing_source_or_policy:  falta frontera conceptual con pullback/retrace.
```

```text
future_response_model: blocked_reason:  usa futuro. missing_source_or_policy:  no puede ser input de State; solo outcome/label.
```

## Fronteras Para La Admision  El expediente formal de admision de `Price Movement` debe responder:

```text
1. El Objeto se llamara `Price Movement` o `Momentum`?  2. Si se acepta `Price Movement`, que queda reservado para `Momentum`?  3. El gap es modelo interno de movimiento o frontera con Price Location?  4. Que referencias temporales son legales:  prior close, session open, segment open, bar close?  5. Que capacidades son decision-safe intradia?  6. Que capacidades daily solo pueden usarse tras cierre o como historico previo?  7. Como se separan retorno, velocidad, aceleracion,  rango y localizacion?  8. Que variables quedan prohibidas por outcome leakage?
```

## Recomendacion Para Object Admission

```text
Abrir un unico expediente candidato:  Price Movement
```

No abrir todavia expedientes separados para:

```text
Daily Price State Intraday Price Dynamics Opening Gap Movement Price Speed Price Acceleration Momentum Reversal / Fade
```

Lectura:

```text
Daily e intraday son perfiles temporales. Gap, speed y acceleration son modelos. Momentum podria ser subobjeto futuro, pero primero debe probar que preserva informacion distinta del movimiento general. Reversal/Fade puede pertenecer a pattern discovery.
```

## Decision Del Landscape

```text
decision = ready_to_define_candidate_object
```

Motivo:

```text
Existe un Objeto candidato coherente: `Price Movement`. El paisaje de modelos muestra que el dominio es representable con capacidades disponibles, formulas definidas o variantes gobernables.  Tambien muestra que localizacion, volatilidad y outcomes deben mantenerse fuera.
```

## Resultado Posterior

```text
Candidate Object Definition creado en:  C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\ 03_TABLES_feature_engineering\ 03_INFORMATION_OBJECTS\ CANDIDATES\ price_movement_candidate_object_definition_v0_1.md
```

## Siguiente Paso

```text
Continuar bucle cientifico con:  Price Location / Structure  -> Domain Definition  -> Representation Landscape  -> Object Admission
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\02_DOMAIN_DEFINITION_TEMPLATE_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\03_REPRESENTATION_LANDSCAPE_TEMPLATE_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_movement_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\013_ohlcv_1m_quote_guarded\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\table_representation_audit_ES.md
```
