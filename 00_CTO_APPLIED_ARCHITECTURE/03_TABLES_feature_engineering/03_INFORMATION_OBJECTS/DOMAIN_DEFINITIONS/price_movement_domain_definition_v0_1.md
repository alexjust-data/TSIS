# Price Movement - Domain Definition v0.1

Status: `domain_definition_v0_1`
Date: `2026-07-20`
Scope: `cluster_2_pre_landscape_pre_admission`

Este documento define el dominio semantico `Price Movement`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona modelos finales.
No autoriza variables para `Market State` ni `Event State`.
No modifica tablas, schemas, builders, contratos ni datasets.

## Nombre Del Dominio

```text
Price Movement
```

## Que Informacion Intenta Preservar

```text
Como cambia el precio de un instrumento en una escala temporal declarada, respecto a una referencia temporal legal.
```

El dominio intenta preservar informacion sobre:

```text
direccion del cambio, magnitud del cambio, velocidad del cambio, aceleracion del cambio, continuidad o discontinuidad temporal del cambio, y persistencia del movimiento.
```

La informacion central no es:

```text
donde esta el precio, cuanto rango hay, cuanto se negocio, cuanto cuesta negociar, ni que ocurrio despues.
```

La informacion central es:

```text
cambio observable del precio.
```

## Por Que Este Dominio Merece Existir

```text
Porque el estado del mercado no puede describirse correctamente sin saber si el precio esta cambiando, en que direccion, con que intensidad y con que dinamica temporal.
```

En small caps y microcaps, dos estados con la misma localizacion actual pueden tener significados distintos si llegaron alli mediante trayectorias distintas:

```text
subida gradual, impulso rapido, gap discontinuo, reversion, aceleracion, desaceleracion, o ausencia de movimiento.
```

Este dominio merece existir porque conserva una incertidumbre que otros dominios no conservan de forma suficiente:

```text
como se esta desplazando el precio hasta el instante observado?
```

## Que Perderia TSIS Si Este Dominio Desapareciera  TSIS perderia capacidad para distinguir:

```text
precio quieto vs precio en movimiento; movimiento alcista vs bajista; movimiento lento vs rapido; movimiento lineal vs acelerado; gap de apertura vs continuidad intradia; impulso reciente vs movimiento ya agotado; y cambio observable vs outcome futuro.
```

Tambien perderia una dimension critica para:

```text
Market State, Event State, pattern discovery, scanners, backtests, ML, RL, AlphaEvolve candidate evaluation, y analisis de continuation/failure.
```

## Que No Representa  Este dominio no representa:

```text
posicion del precio contra VWAP/HOD/LOD/open/prior close, amplitud o dispersion como fenomeno principal, volumen o participacion, liquidez, spread, profundidad, order flow direccional, noticias, fundamentales, short context, outcomes futuros, ni calidad tecnica del dataset.
```

Distincion clave:

```text
return_vs_prior_close = cambio respecto a una referencia temporal.  actual_distance_to_prior_close = localizacion estructural respecto a una referencia.
```

El primero puede pertenecer a `Price Movement`. El segundo debe revisarse en `Price Location / Structure`.

## Preguntas Cientificas Que Permite Formular

```text
El precio se esta moviendo de forma observable en t?  La direccion del cambio es positiva, negativa o neutra?  La velocidad del movimiento esta aumentando o disminuyendo?  El movimiento actual es continuo o discontinuo respecto a la sesion anterior?  El movimiento reciente tiene persistencia o esta revirtiendo?  Los eventos relevantes ocurren durante aceleracion, desaceleracion o estabilizacion de precio?  La probabilidad de continuation/failure cambia segun la dinamica previa del precio?
```

## Candidatos Incluidos  Detectados en la primera pasada:

```text
Daily Price State Intraday Price Dynamics Overnight Dislocation returns slope move speed move acceleration gap percent
```

Lectura actual:

```text
Price Movement = candidato principal a Objeto de Informacion.  Daily Price State = modelo/resolucion diaria, no Objeto separado por defecto.  Intraday Price Dynamics = modelo/resolucion intradia, no Objeto separado por defecto.  Overnight Dislocation = posible modelo de cambio discontinuo de apertura o frontera con Price Location / Structure.  Momentum = posible modelo/subobjeto de persistencia direccional, no sinonimo completo de Price Movement.
```

## Posibles Objetos Dentro Del Dominio

```text
Price Movement
```

Candidato principal.

```text
Momentum
```

Probablemente modelo especializado de persistencia direccional. No debe absorber todo el dominio por defecto.

```text
Opening Gap Movement
```

Probablemente modelo de cambio discontinuo entre cierre previo y apertura. No debe confundirse con localizacion posterior contra prior close.

```text
Price Acceleration
```

Probablemente modelo derivado de velocidad de movimiento, no Objeto separado por defecto.  Regla anti-duplicacion:

```text
Un cambio de horizonte, ventana, referencia de precio, bar size, o escala temporal no crea automaticamente un nuevo Objeto de Informacion.
```

Primero debe probarse que preserva una informacion semanticamente distinta.

## Posibles Modelos De Representacion  Estos modelos no quedan seleccionados todavia. Solo quedan identificados para el `Representation Landscape`.

```text
daily close-to-close movement model daily open-to-close movement model opening gap movement model intraday bar return model session return-to-time model segment return model move speed model move acceleration model persistence / momentum model reversal / fade model
```

## Capacidades Derivables Relacionadas

### Capacidades Imprescindibles  Estas capacidades son el nucleo minimo del dominio:

```text
daily__open_price daily__close_price daily__prior_close daily__gap_pct daily__daily_return_pct daily__intraday_return_pct intraday__bar_open_price intraday__bar_close_price intraday__return_vs_prior_close_ratio intraday__return_vs_session_open_ratio
```

### Capacidades Complementarias  Estas capacidades refinan el dominio, pero no lo definen por si solas:

```text
intraday__return_vs_segment_open_ratio intraday__move_speed_W intraday__move_acceleration_W
```

### Capacidades Fronterizas  Estas capacidades probablemente pertenecen a otro dominio salvo que un modelo explicito demuestre lo contrario:

```text
intraday__vwap_distance_ratio intraday__pullback_ratio_W intraday__retrace_ratio_W daily__daily_range_pct daily__volatility_Nd daily__range_Nd future__future_return_H
```

Lectura:

```text
VWAP/HOD/LOD/prior-close distances pertenecen mejor a Price Location / Structure. Range y volatility pertenecen mejor a Volatility / Range State. Future returns pertenecen a Outcomes y estan prohibidos como input de State.
```

## Tablas Que Aportan Evidencia

```text
004_master_daily_table = precio diario, prior_close, gap_pct, daily_return_pct, intraday_return_pct.  013_ohlcv_1m_quote_guarded = fuente intradia 1m quote-guarded para barras OHLCV.  014_master_intraday_bar_table = representacion intradia por barras cerradas, retornos as-of y futuros modelos de velocidad/aceleracion.  008_outcomes_table = futuros returns/MFE/MAE solo como outcomes, no como Price Movement observable en t.
```

## Fronteras Con Otros Dominios 

| Dominio vecino | Frontera |
| --- | --- |
| `Price Location / Structure` | `Price Movement` mide cambio. `Price Location` mide posicion relativa contra referencias como VWAP, HOD, LOD, open o prior close. |
| `Volatility / Range State` | `Price Movement` mide direccion/velocidad/aceleracion. `Volatility` mide amplitud, dispersion e incertidumbre del movimiento. |
| `Trading Activity` | `Price Movement` no mide participacion negociada. Un movimiento puede existir con alta o baja actividad. |
| `Liquidity` | `Price Movement` no mide facilidad, coste o disponibilidad de negociar. |
| `Order Flow Pressure` | `Price Movement` observa desplazamiento de precio; no infiere agresion compradora/vendedora. |
| `Outcome Layer` | `Price Movement` solo puede usar informacion observable hasta t. Futuros retornos son labels/outcomes, no input. |
| `Representation Quality State` | Correcciones, missingness y repair lineage condicionan confianza, pero no son movimiento de precio. |

## Riesgos De Fusion O Division  Riesgo de fusion incorrecta:

```text
Fusionar Price Movement con Price Location porque ambos usan referencias de precio.
```

Riesgo de division incorrecta:

```text
Crear Daily Price State e Intraday Price Dynamics como Objetos separados, cuando probablemente son modelos o resoluciones del mismo Objeto.
```

Riesgo de contamination:

```text
Incluir future_return_H como si fuera movimiento observable.
```

Riesgo temporal:

```text
Usar close diario final antes del cierre para decisiones intradia.
```

Riesgo semantico:

```text
Llamar Momentum a todo Price Movement. Momentum deberia reservarse para persistencia direccional, no para cualquier cambio de precio.
```

## Decision De Dominio

```text
decision = ready_for_representation_landscape
```

Motivo:

```text
El dominio tiene identidad semantica suficiente: preserva cambio observable del precio.  No parece reducible a Price Location, Volatility, Trading Activity, Liquidity, Order Flow, Quality ni Outcomes.  Pero necesita Representation Landscape antes de abrir Object Admission, porque debe decidir si `Momentum`, `Gap Movement`, `Speed` y `Acceleration` son modelos internos o Objetos separados.
```

## Siguiente Paso

```text
Crear:  C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\ 03_TABLES_feature_engineering\ 03_INFORMATION_OBJECTS\ DOMAIN_DEFINITIONS\ price_movement_representation_landscape_v0_1.md
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\02_DOMAIN_DEFINITION_TEMPLATE_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\013_ohlcv_1m_quote_guarded\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\table_representation_audit_ES.md
```
