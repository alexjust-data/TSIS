# Price Movement - Candidate Object Definition v0.1

Status: `candidate_object_definition_v0_1`
Date: `2026-07-20`
Scope: `post_landscape_pre_formal_admission`

Este documento define el Objeto candidato `Price Movement` despues de Domain Definition y Representation Landscape. No constituye admision formal.

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
Price Movement
```

### Definicion Corta

```text
Unidad semantica que preserva como cambia el precio
de un instrumento en una escala temporal declarada,
utilizando solo referencias observables legalmente en t.
```

### Taxonomy Axes

Information Object Family:

```text
Price Movement
```

Source Domain:

```text
OHLCV Daily
OHLCV 1m
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
research_input_candidate
outcome_separated
```

## 2. Significado Cientifico

### Informacion Que Se Desea Preservar

```text
Direccion, magnitud, velocidad, aceleracion
y continuidad del cambio observable del precio.
```

### Fenomeno Observable

```text
Desplazamiento del precio entre referencias temporales legales:
prior close, session open, segment open, bar close o ventana cerrada.
```

### Significado Para TSIS

```text
Price Movement permite distinguir estados de mercado donde el precio
esta quieto, se mueve, acelera, desacelera, persiste o cambia de direccion.
```

## 3. Justificacion Cientifica

### Hipotesis Principal

```text
La trayectoria observable del precio hasta t contiene informacion
sobre continuidad, presion, agotamiento o cambio de regimen local,
y condiciona la interpretacion posterior de estados, eventos y outcomes.
```

### Por Que Merece Existir

```text
Porque el estado del mercado no puede describirse solo por referencias,
volumen, liquidez o contexto externo.
Debe saber si el precio esta cambiando y como.
```

### Que Perderia TSIS Si No Existiera

```text
Perderia la capacidad de representar direccion,
intensidad dinamica, velocidad, aceleracion,
gap discontinuo y persistencia del movimiento observable.
```

Tambien perderia capacidad para separar:

```text
movimiento observado
vs
posicion relativa;

movimiento observado
vs
amplitud/volatilidad;

movimiento observable hasta t
vs
resultado futuro.
```

## 4. Preguntas Cientificas

```text
El precio se esta moviendo en t?

En que direccion se mueve?

Con que intensidad y velocidad?

Esta acelerando o desacelerando?

El movimiento actual es continuacion, gap o reversion?

Los eventos ocurren despues de movimiento acumulado,
durante aceleracion o tras agotamiento?

Que parte del movimiento observable ayuda a explicar
continuation, failure, expansion o reversal posteriores?
```

## 5. Modelos De Representacion Admitidos O Restringidos

| Modelo | Rol | Medidas candidatas | Estado | Decision |
| --- | --- | --- | --- | --- |
| `opening_gap_movement_model` | cambio discontinuo apertura vs cierre previo | gap_pct | `existing` | `allowed_with_open_cutoff` |
| `intraday_return_to_reference_model` | cambio as-of contra referencia legal | return_vs_prior_close, return_vs_session_open, return_vs_segment_open | `formula_defined` | `allowed_after_bar_close` |
| `daily_closed_return_model` | movimiento diario completo historico | daily_return_pct, intraday_return_pct | `existing` | `allowed_after_market_close_or_prior_history` |
| `move_speed_model` | velocidad del movimiento en W | move_speed_W | `requires_variant` | `allowed_after_variant_policy` |
| `move_acceleration_model` | cambio de velocidad | move_acceleration_W | `requires_variant` | `extension_only_until_validated` |
| `momentum_persistence_model` | persistencia direccional | return/speed sequence | `candidate_requires_formula` | `not_core_until_defined` |
| `reversal_fade_model` | perdida de continuidad o cambio de direccion | pullback/retrace/return sequence | `candidate_boundary_model` | `not_core_until_domain_boundary_resolved` |
| `future_response_model` | movimiento posterior | future_return_H, MFE, MAE | `prohibited_as_feature` | `outcome_only` |

## 6. Implementacion Fisica Candidata

Variables/capacidades candidatas core:

```text
daily__prior_close
daily__gap_pct
intraday__bar_close_price
intraday__return_vs_prior_close_ratio
intraday__return_vs_session_open_ratio
intraday__return_vs_segment_open_ratio
intraday__move_speed_W
```

Variables/capacidades de extension:

```text
daily__daily_return_pct
daily__intraday_return_pct
intraday__move_acceleration_W
```

Variables/capacidades fronterizas:

```text
intraday__pullback_ratio_W
intraday__retrace_ratio_W
intraday__vwap_distance_ratio
daily__daily_range_pct
daily__volatility_Nd
daily__range_Nd
```

Variables/capacidades excluidas como input de este Objeto:

```text
future__future_return_H
future__mfe_H
future__mae_H
```

## 7. Tablas Fuente

| Tabla | Contribucion | Rol |
| --- | --- | --- |
| `004_master_daily_table` | open, close, prior_close, gap_pct, daily_return_pct, intraday_return_pct | daily closed/historical movement context |
| `013_ohlcv_1m_quote_guarded` | barras OHLCV 1m corregidas/guarded | upstream intraday source |
| `014_master_intraday_bar_table` | barras cerradas y retornos as-of candidatos | intraday movement profile |
| `008_outcomes_table` | future returns, MFE, MAE | outcome only, prohibited as input |

## 8. Legalidad Temporal

Reglas obligatorias:

```text
1. Una barra intradia solo es consumible despues de su cierre.

2. `gap_pct` es legal despues de conocer apertura y prior_close.

3. `daily_return_pct` e `intraday_return_pct` del dia actual
solo son legales tras market close.

4. `return_vs_prior_close` y `return_vs_session_open`
son legales intradia solo con precio_ref observado hasta t.

5. Speed y acceleration requieren ventanas cerradas y min_periods.

6. Future returns, MFE y MAE son outcomes, no inputs.
```

## 9. Consumidores

```text
Market State
Event State
pattern discovery
intraday scanners
backtests
ML
IRL
Offline RL
AlphaEvolve candidate evaluation
risk filters
outcome analysis as X/y separated input/output
```

## 10. Representaciones Equivalentes O Solapadas

```text
Price Location / Structure:
comparte referencias de precio, pero mide posicion relativa,
no cambio temporal.
```

```text
Volatility / Range State:
comparte high/low/returns, pero mide amplitud/dispersion,
no direccion o velocidad como informacion principal.
```

```text
Trading Activity:
puede explicar si un movimiento esta soportado por participacion,
pero no mide el movimiento.
```

```text
Outcome Response:
future returns son evaluacion posterior, no movimiento observable en t.
```

## 11. Evaluacion Tecnica

Coste computacional:

```text
low para returns diarios e intradia simples;
medium para speed/acceleration con variantes;
high si se crean demasiados horizontes sin gobernanza.
```

Riesgo de ruido:

```text
alto en ventanas 1m demasiado cortas,
precios con reparaciones pendientes,
y small caps con prints escasos.
```

Riesgo de overfitting:

```text
alto si se multiplican horizontes y referencias
sin admission/mapping explicito.
```

Control recomendado:

```text
definir pocos horizontes canonicos;
separar core y extension;
prohibir outcomes como features;
y exigir calidad de 013/014 antes de State.
```

## 12. Impacto Sobre State

Si se admite, `Price Movement` debe entrar como:

```text
Objeto admitido para representar cambio observable del precio.
```

No debe entrar como:

```text
mega conjunto de retornos,
distancias,
rangos,
volatilidades,
futuros returns,
y patterns de estrategia.
```

Perfil recomendado:

```text
market_state_core:
    return as-of minimo contra referencia legal.

market_state_intraday:
    speed / acceleration con variantes gobernadas.

market_state_event_extension:
    movimiento pre/at-event bajo ventanas cerradas.

outcomes:
    future returns, MFE, MAE separados.
```

## 13. Decision

```text
decision = candidate_defined_pending_formal_admission
```

Justificacion:

```text
Price Movement conserva informacion observable,
cientificamente distinta y necesaria sobre el cambio del precio.

La evidencia disponible permite representarlo con capacidades existentes,
formulas definidas o variantes gobernables.

No queda absorbido por Price Location, Volatility,
Trading Activity, Liquidity, Order Flow, Quality ni Outcomes.
```

Restricciones:

```text
1. No autoriza variables directamente para State.

2. Requiere Operational Mapping antes de consumo.

3. Requiere separar movimiento, localizacion y volatilidad.

4. Requiere declarar referencia temporal y price_ref por modelo.

5. Requiere no usar daily close final antes del cierre.

6. Requiere no incluir future returns, MFE ni MAE como inputs.

7. Requiere resolver si `intraday__bar_return` debe existir
como capacidad atomica canonica en 05_DATA_derivable.

8. Requiere tratar Momentum como modelo/subobjeto pendiente,
no como sinonimo automatico de Price Movement.
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
Continuar bucle cientifico con:

Price Location / Structure
    -> Domain Definition
    -> Representation Landscape
    -> Object Admission
```

Operational mapping de `Price Movement` queda pendiente hasta tener suficientes Objetos core admitidos para decidir perfiles de State sin sesgo por un unico dominio.

## 16. Evidencia TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_movement_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_movement_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\013_ohlcv_1m_quote_guarded\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\table_representation_audit_ES.md
```

