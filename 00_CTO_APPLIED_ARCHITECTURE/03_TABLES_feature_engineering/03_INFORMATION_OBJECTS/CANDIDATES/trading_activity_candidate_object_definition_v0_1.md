# Trading Activity - Candidate Object Definition v0.1

Status: `candidate_object_definition_v0_1`
Date: `2026-07-20`
Scope: `post_landscape_pre_formal_admission`

Este documento define el Objeto candidato `Trading Activity` despues de Domain Definition y Representation Landscape. No constituye admision formal.

No disena tablas.
No promociona datasets.
No modifica schemas, builders, validators ni contratos.
No autoriza variables concretas para `Market State` o `Event State`.

## Nota De Estado

```text
Este documento no admite institucionalmente el Objeto.
Solo fija una definicion candidata trazable para futura admision formal.

Domain = unidad cientifica de trabajo.
Candidate Object = posible unidad semantica dentro del dominio.
Accepted Object = decision institucional posterior, aun no ejecutada aqui.
```


## 1. Identificacion

### Nombre

```text
Trading Activity
```

### Definicion Corta

```text
Unidad semantica que preserva la intensidad de participacion
negociada observable en un instrumento, bajo una escala temporal
y una politica de corte declaradas.
```

### Taxonomy Axes

Information Object Family:

```text
Trading Activity
```

Source Domain:

```text
OHLCV Daily
OHLCV 1m
Trades
```

Temporal Resolution:

```text
daily
intraday_bar
event_window
```

Institutional Role:

```text
observable
state_input_candidate
scanner_context_candidate
research_input_candidate
```

## 2. Significado Cientifico

### Informacion Que Se Desea Preservar

```text
Si el mercado esta participando realmente en la negociacion
de un instrumento, con que intensidad y en que escala temporal.
```

### Fenomeno Observable

```text
Actividad negociada: volumen, numero de operaciones,
dollar volume, ritmo de llegada de trades o barras,
y desviacion respecto a baselines historicos o esperados.
```

### Significado Para TSIS

```text
Trading Activity permite distinguir estados de precio similares
que no tienen el mismo significado porque el nivel de participacion
negociada es distinto.
```

Ejemplo:

```text
Un movimiento de precio con baja actividad no representa
lo mismo que un movimiento equivalente con actividad anomala.
```

## 3. Justificacion Cientifica

### Hipotesis Principal

```text
La intensidad de participacion negociada condiciona
la interpretacion del estado del mercado y puede alterar
la probabilidad de continuacion, fallo, expansion,
reversion, operabilidad y calidad de seleccion de candidatos.
```

### Por Que Merece Existir

```text
Porque preserva una dimension que no queda capturada
por precio, localizacion, volatilidad, liquidez, microestructura,
order flow, noticias, fundamentals ni outcomes.
```

`Trading Activity` responde:

```text
Hay participacion real?
La actividad actual es normal o anomala?
La sesion esta despierta o dormida?
El evento o scanner aparece con participacion negociada suficiente?
```

### Que Perderia TSIS Si No Existiera

TSIS perderia capacidad para separar:

```text
precio con participacion vs precio con prints escasos;
scanner candidate con actividad observable vs seleccion debil;
evento con respuesta negociada vs evento sin respuesta;
estado operable vs estado teorico pero poco negociado;
movimiento anomalo por intensidad vs movimiento ordinario.
```

## 4. Preguntas Cientificas

```text
El movimiento observado esta soportado por participacion real?

La actividad actual es anomala respecto al historico del instrumento?

La participacion se esta acelerando durante la sesion?

El evento genera actividad negociada o solo contexto externo?

Los candidatos intradia seleccionados tienen actividad suficiente
para ser investigables y operables?

La probabilidad de continuacion, fallo, expansion o reversa
cambia segun el nivel de Trading Activity?

Que perfiles de State necesitan actividad diaria,
intradia o por ventana de trades?
```

## 5. Modelos De Representacion Conocidos

| Modelo | Rol | Medidas candidatas | Estado | Decision |
| --- | --- | --- | --- | --- |
| `daily_absolute_participation_model` | contexto diario cerrado | volume, transaction_count, dollar_volume | `existing` | `allowed_as_daily_context` |
| `daily_relative_participation_model` | normalizacion historica | volume_20d_avg, rvol_20d, volume_Nd_avg, rvol_Nd | `existing_plus_requires_variant` | `allowed_with_prior_only_baseline` |
| `intraday_absolute_accumulation_model` | actividad acumulada hasta t | bar_volume, bar_transaction_count, session_volume_to_time, session_dollar_volume_to_time | `formula_defined_candidate` | `allowed_after_bar_close` |
| `intraday_pace_model` | actividad vs expectativa intradia | volume_pace_W, dollar_volume_pace_W | `requires_variant` | `allowed_after_variant_policy` |
| `trade_window_intensity_model` | intensidad de trades en ventana cerrada | trade_count_WINDOW, trade_rate_WINDOW, total_volume_WINDOW, dollar_volume_WINDOW | `candidate_profile` | `allowed_as_microstructure_extension` |
| `trade_size_distribution_model` | textura de tamanos negociados | size_median_WINDOW, size_p90_WINDOW, odd_lot_ratio_pct_WINDOW | `complementary` | `extension_only_until_justified` |
| `scanner_activity_threshold_model` | seleccion de candidatos | scanner thresholds, tradability threshold | `selection_surface_only` | `not_object_model_for_state_core` |
| `directional_activity_model` | actividad con signo/agresion | signed_flow, aggressor_imbalance, bid_hit_ask_lift | `candidate_other_domain` | `move_to_order_flow_pressure` |

## 6. Implementacion Fisica Candidata

Variables candidatas core o contexto:

```text
daily__volume
daily__transaction_count
daily__dollar_volume
daily__volume_20d_avg
daily__rvol_20d
intraday__bar_volume
intraday__bar_transaction_count
intraday__session_volume_to_time
intraday__session_dollar_volume_to_time
trades__trade_count_WINDOW
trades__trade_rate_WINDOW
trades__total_volume_WINDOW
trades__dollar_volume_WINDOW
```

Variables candidatas de extension:

```text
daily__volume_Nd_avg
daily__rvol_Nd
daily__dollar_volume_Nd_avg
intraday__volume_pace_W
intraday__dollar_volume_pace_W
trades__size_median_WINDOW
trades__size_p90_WINDOW
trades__odd_lot_ratio_pct_WINDOW
```

Variables excluidas de este Objeto por ahora:

```text
trades__signed_flow_WINDOW
trades__aggressor_imbalance_WINDOW
trades__bid_hit_ask_lift_WINDOW
short__short_volume_ratio
short__short_interest_z_WINDOW
decision__selected_by_scanner
future__future_return_H
future__mfe_H
future__mae_H
```

Motivo:

```text
signed/aggressor pertenecen a Order Flow Pressure;
short pertenece a Short-Side Context;
scanner selection es decision/superficie de seleccion;
futuro pertenece a outcomes y esta prohibido como input de State.
```

## 7. Tablas Fuente

| Tabla | Contribucion | Rol |
| --- | --- | --- |
| `004_master_daily_table` | volumen, transaction_count, dollar_volume, rvol_20d | daily context / historical baseline |
| `013_ohlcv_1m_quote_guarded` | barras 1m corregidas/guarded para volumen intradia | upstream intraday source |
| `014_master_intraday_bar_table` | actividad por barra cerrada y acumulados intradia | intraday representation profile |
| `015_microstructure_features_table` | trades por ventana, trade rate, size distribution | microstructure/event-window extension |
| `018_intraday_scanner_candidates_table` | selection surface que puede usar actividad | scanner context only, not proof of object |

## 8. Legalidad Temporal

Reglas obligatorias:

```text
1. Una barra intradia solo es consumible despues de su cierre.

2. El volumen diario final solo es consumible despues del cierre
del mercado o como contexto historico de sesiones previas.

3. Todo baseline debe ser prior-only o as-of.

4. Toda ventana de trades debe estar cerrada:
window_end <= decision_timestamp.

5. La seleccion de scanner no puede usarse como feature causal neutral
sin separarla de decision/selection bias.

6. Outcomes futuros quedan prohibidos como input.
```

## 9. Consumidores

Consumidores principales:

```text
Market State
Event State
intraday scanners
pattern discovery
clustering
ML
IRL
Offline RL
AlphaEvolve candidate evaluation
execution-aware research
risk filters
```

Lectura:

```text
No todos los consumidores necesitan el mismo perfil.
Market State core debe ser pequeno.
Extensiones intradia/microestructura pueden ser perfiles separados.
```

## 10. Representaciones Equivalentes O Solapadas

```text
Liquidity:
comparte `dollar_volume` y trade count como proxies,
pero responde facilidad/coste/disponibilidad de negociar.
Trading Activity responde intensidad de participacion negociada.
```

```text
Order Flow Pressure:
comparte trades,
pero introduce signo, agresion e imbalance.
Trading Activity es no direccional por defecto.
```

```text
Market Microstructure State:
puede incluir quote state, spread, locked/crossed y depth.
Trading Activity solo consume microestructura si el modelo mide actividad de trades.
```

```text
Short-Side Context:
puede hablar de short activity,
pero la fuente, lag y semantica son distintas.
No debe fusionarse con Trading Activity.
```

## 11. Evaluacion Tecnica

Coste computacional:

```text
low para daily y barras 1m;
medium para ventanas de trades;
high si se exige trade-quote alignment o perfiles densos por evento.
```

Riesgo de ruido:

```text
alto en small caps con prints escasos,
odd lots,
ventanas demasiado cortas
y cobertura irregular.
```

Riesgo de overfitting:

```text
alto si se crean demasiadas variantes N/W sin justificar.
```

Control recomendado:

```text
mantener core pequeno;
declarar variantes;
separar perfiles pesados;
exigir mapping antes de State.
```

## 12. Impacto Sobre State

Si se admite, `Trading Activity` debe entrar como:

```text
Objeto admitido para representar intensidad de participacion.
```

No debe entrar como:

```text
lista abierta de todas las variables de volumen,
trade count,
rvol,
pace,
scanner,
size distribution
y thresholds.
```

Perfil recomendado:

```text
market_state_core:
    actividad minima as-of y decision-safe.

market_state_intraday:
    acumulacion y pace intradia.

market_state_microstructure_extension:
    trade-window intensity y size distribution.

scanner/event context:
    seleccion y atencion, separados de causal features.
```

## 13. Decision

```text
decision = candidate_defined_pending_formal_admission
```

Justificacion:

```text
Trading Activity conserva informacion cientifica distinta,
observable y necesaria para interpretar el estado del mercado.

La evidencia disponible permite representarlo con capacidades existentes,
formulas definidas o variantes gobernables.

No queda absorbido por Price Movement, Liquidity, Microstructure,
Order Flow, Short-Side Context, Quality ni Selection Surface.
```

Restricciones:

```text
1. No autoriza variables directamente para State.

2. Requiere Operational Mapping antes de consumo.

3. Requiere separar core, intraday profile y microstructure extension.

4. Requiere temporal cutoff explicito por modelo.

5. Requiere no usar volumen final diario antes del cierre.

6. Requiere no incluir signed flow/aggressor imbalance en este Objeto.

7. Requiere no usar scanner selection como variable causal neutral.

8. Requiere bloquear true float turnover hasta tener float PIT gobernado.
```

## 14. Estado De Promocion

```text
information_object_status = candidate_defined
formal_admission_required = true
operational_mapping_required = true
state_consumption_authorized = false
physical_variables_authorized = false
schema_change_authorized = false
builder_change_authorized = false
```

## 15. Siguiente Paso

```text
Crear operational mapping:

Trading Activity
    -> modelos
    -> capacidades derivables
    -> variables fisicas
    -> tablas fuente
    -> perfiles de State
```

## 16. Evidencia TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\trading_activity_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\trading_activity_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\015\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\018\table_representation_audit_ES.md
```


