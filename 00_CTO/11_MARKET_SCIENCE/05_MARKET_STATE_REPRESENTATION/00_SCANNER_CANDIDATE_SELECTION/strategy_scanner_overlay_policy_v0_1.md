# Strategy Scanner Overlay Policy v0.1

Fecha: 2026-06-30
Estado: `candidate_policy`
Scope: `00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/`

## 1. Rol

Esta policy aplica a toda estrategia nueva de TSIS:

```text
LONG/*
SHORT/*
FACTORS/*
estrategias futuras
```

Define como una estrategia debe consumir el scanner general sin contaminar Data
Foundation ni convertir filtros de estrategia en doctrina global.

## 2. Regla Central

```text
daily_scanner_candidates_table = denominador / donde mirar
strategy overlay = hipotesis especifica de estrategia
strategy state table = lectura experimental de estados de esa estrategia
market_state/event_state = composicion institucional futura
```

Una estrategia no debe modificar el scanner base para resolver su propia
hipotesis.

## 3. Scanner Base

El scanner base actual es:

```text
base_in_play_universe_scanner_v0_2
```

Significado correcto:

```text
base_eligible_smallcap_denominator
```

Filtros base:

```text
common_stock = true
market_cap_usd < 100000000
0.5 < last_price <= 20
data_quality in usable/review
```

Ese denominador conserva filas aunque ningun perfil dispare. Esa ausencia es
informacion cientifica: permite medir falsos negativos, llegada tardia y sesgo
de seleccion.

## 4. Perfiles Genericos

Los perfiles viven como flags paralelos sobre el mismo denominador:

```text
selected_trade_station_like_profile
selected_relative_volume_profile
selected_percent_change_profile
selected_dollar_volume_tradability_profile
selected_das_research_profile
selected_any_profile
```

No son un embudo secuencial.

Una estrategia puede elegir uno o varios denominadores de trabajo, pero debe
declararlo explicitamente.

## 5. Denominadores Que Toda Estrategia Debe Declarar

Todo notebook, run, tabla experimental o reporte de estrategia debe declarar
uno de estos denominadores:

```text
all_filters_passed
selected_any_profile
selected_trade_station_like_profile
selected_percent_change_profile
selected_dollar_volume_tradability_profile
selected_relative_volume_profile
selected_das_research_profile
manual_human_seed
conditional_on_current_strategy_detector
```

Interpretacion:

- `all_filters_passed`: base smallcap elegible; util para medir ausencia.
- `selected_any_profile`: candidato detectado por algun perfil generico.
- `selected_trade_station_like_profile`: aproximacion a pantalla humana tipo
  TradeStation.
- `selected_percent_change_profile`: movimiento minimo + top-N/rank.
- `selected_dollar_volume_tradability_profile`: tradability/economic activity,
  no alpha.
- `selected_relative_volume_profile`: solo valido cuando exista intraday/as-of
  acceleration; en replay diario contract-aligned es unavailable.
- `selected_das_research_profile`: semilla provisional DAS, no patron general.
- `manual_human_seed`: muestra humana; no poblacional.
- `conditional_on_current_strategy_detector`: muestra de un detector local; debe
  tratarse como potencialmente sesgada.

## 6. Prohibiciones

Una estrategia no debe:

- esconder filtros en un notebook;
- seleccionar solo casos buenos;
- reportar estadisticas poblacionales desde una muestra manual;
- usar labels/outcomes como features;
- convertir un overlay en Data Foundation sin promocion;
- escribir outputs oficiales en `E:/TSIS/data` sin contrato;
- tratar scanner rows como ML features o RL states directos.

## 7. Como Crear Un Overlay De Estrategia

Proceso obligatorio:

1. Elegir una version concreta de `daily_scanner_candidates_table`.
2. Declarar `scanner_run_id`, manifest y root.
3. Declarar denominador de estrategia.
4. Crear columnas namespaced.
5. Incluir positivos, negativos, fallos y review.
6. Separar features de labels/outcomes.
7. Guardar run local bajo la carpeta de estrategia.
8. Documentar thresholds y rationale.
9. Promover solo si hay evidencia de robustez y utilidad general.

Namespaces recomendados:

```text
scanner__
daily__
intraday__
event__
strategy__
quality__
human_label__
outcome__
```

Regla:

```text
human_label__* != feature
outcome__* != feature
```

## 8. Cuando Una Estrategia Necesita Filtros Nuevos

Primero se implementan como overlay local:

```text
strategy_overlay_v0_1
```

No como cambio de scanner base.

Solo despues de evidencia fuerte pueden proponerse como:

```text
generic observation profile
strategy-specific scanner contract
market_state component
event_state component
```

## 9. Relacion Con Replay De 20 Anos

Un replay 20y de `daily_scanner_candidates_table_v0_2` puede ser canonico para:

```text
esa version del scanner
esas fuentes
esas configs
ese price_view
ese periodo
ese manifest
```

No es inmutable en sentido absoluto.

Debe versionarse de nuevo cuando cambie:

- contrato;
- config;
- fuente upstream;
- repaired data;
- universo;
- price view;
- intraday/as-of availability;
- policy de calidad;
- schema.

Lectura correcta:

```text
canonical_for_declared_version != invariant_forever
```

## 10. Primera Implementacion

DAS es la primera estrategia con runbook especifico:

```text
C:/TSIS_Data/00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/DAS_SCANNER_USAGE_AND_OVERLAY_RUNBOOK_v0_1.md
```

DAS no es una excepcion. Es el primer caso aplicado de esta policy general.

