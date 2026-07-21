# Volatility / Range State - Domain Definition v0.1

Status: `domain_definition_v0_1`
Date: `2026-07-20`
Scope: `cluster_4_pre_landscape_pre_admission`

Este documento define el dominio semantico `Volatility / Range State`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona modelos finales.
No autoriza variables para `Market State` ni `Event State`.
No modifica tablas, schemas, builders, contratos ni datasets.

## Nombre Del Dominio

```text
Volatility / Range State
```

## Que Informacion Intenta Preservar

```text
La amplitud, dispersion e incertidumbre observable del movimiento de precio en una ventana temporal declarada.
```

La informacion central es:

```text
cuanto se esta expandiendo, comprimiendo o dispersando el precio.
```

No es:

```text
direccion del movimiento, posicion contra referencias, volumen, liquidez, order flow, ni outcome futuro.
```

## Por Que Este Dominio Merece Existir

```text
Porque dos movimientos con la misma direccion pueden tener significados distintos si su amplitud, rango o dispersion son distintos.
```

Este dominio preserva una incertidumbre distinta:

```text
cuanto espacio de variacion tiene el precio y que tan inestable es el entorno observado?
```

## Que Perderia TSIS Si Este Dominio Desapareciera

```text
Perderia capacidad para distinguir expansion vs compresion, rango estrecho vs rango amplio, movimiento ordenado vs movimiento disperso, y estado de baja vs alta incertidumbre local.
```

## Que No Representa

```text
direccion, velocidad, aceleracion, localizacion contra VWAP/HOD/LOD, participacion, liquidez, noticias, fundamentales, outcomes futuros, ni calidad tecnica.
```

## Preguntas Cientificas Que Permite Formular

```text
El precio esta en un entorno de rango estrecho o amplio?  La amplitud observada hasta t es anomala?  Hay expansion o compresion intradia?  El evento ocurre en alta o baja incertidumbre local?  La probabilidad de continuation/failure cambia con el rango previo?
```

## Candidatos Incluidos

```text
Daily Volatility Range Intraday Volatility daily range range so far rolling volatility compression expansion
```

Lectura actual:

```text
Volatility / Range State = candidato principal a Objeto de Informacion.  Daily e Intraday son modelos/resoluciones. Compression/Expansion son estados o modelos derivados, no Objetos separados por defecto.
```

## Posibles Modelos De Representacion

```text
daily range model rolling daily volatility model rolling daily range model intraday range-so-far model closed-window realized volatility model compression / expansion model relative range model
```

## Capacidades Derivables Relacionadas

### Capacidades Imprescindibles

```text
daily__daily_range_pct intraday__high_so_far intraday__low_so_far intraday__range_so_far_ratio
```

### Capacidades Complementarias

```text
daily__volatility_Nd daily__range_Nd intraday closed-window return dispersion compression / expansion ratio
```

### Capacidades Fronterizas

```text
intraday__move_speed_W intraday__move_acceleration_W intraday__pullback_ratio_W intraday__retrace_ratio_W future volatility / future range
```

Lectura:

```text
speed/acceleration pertenecen a Price Movement. pullback/retrace pertenecen a Price Location o pattern research. futuro pertenece a Outcomes.
```

## Tablas Que Aportan Evidencia

```text
004_master_daily_table = daily_range_pct y posibles baselines diarios.  014_master_intraday_bar_table = high_so_far, low_so_far, range_so_far_ratio, y futuras ventanas de dispersion intradia.  013_ohlcv_1m_quote_guarded = fuente intradia guarded para rangos intradia.
```

## Fronteras Con Otros Dominios 

| Dominio vecino | Frontera |
| --- | --- |
| `Price Movement` | Movement mide direccion/velocidad/aceleracion. Volatility/Range mide amplitud/dispersion. |
| `Price Location / Structure` | Location mide posicion respecto a referencias. Range puede usar high/low, pero como amplitud. |
| `Trading Activity` | Activity mide participacion; Volatility no mide volumen. |
| `Liquidity` | Liquidity mide coste/facilidad; Volatility mide variabilidad del precio. |
| `Outcome Layer` | Future volatility/range son labels/outcomes, no inputs. |

## Decision De Dominio

```text
decision = ready_for_representation_landscape
```

Motivo:

```text
El dominio tiene identidad propia: preserva amplitud y dispersion observable. No debe absorber movimiento direccional ni localizacion estructural.
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\table_representation_audit_ES.md
```
