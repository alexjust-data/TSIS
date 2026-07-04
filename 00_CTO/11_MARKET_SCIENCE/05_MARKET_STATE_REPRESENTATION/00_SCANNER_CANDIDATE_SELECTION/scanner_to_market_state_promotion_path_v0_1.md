# Scanner To Market State Promotion Path v0.1

Fecha: 2026-06-30
Estado: candidate_policy

## 1. Problema

El scanner es necesario, pero insuficiente.

Una fila de scanner dice:

```text
este ticker entro en observacion bajo esta definicion, en este as-of, por estas razones
```

No dice:

```text
este era el estado completo del mercado
```

Por tanto, debe existir una ruta explicita de promocion.

## 2. Ruta canonica

```text
base_eligible_smallcap_denominator
-> scanner profiles / ranks / candidate reasons
-> daily_scanner_candidates_table
-> candidate set / denominator
-> strategy-specific overlay when needed
-> strategy-specific experimental state table
-> event_state_candidate
-> market_state_candidate
-> institutional_market_state
```

## 3. Fase 1: Daily scanner candidates

Rol:

```text
Define donde mirar.
```

Lectura vigente:

```text
un scanner base define la poblacion observable;
los perfiles definen ranking, visibilidad operativa o research;
los overlays de estrategia definen hipotesis especificas posteriores;
la tabla persiste ambas cosas como lineage.
```

El identificador operativo actual puede seguir siendo
`base_in_play_universe_scanner_v0_2`, pero el significado correcto es
`base_eligible_smallcap_denominator`.

Los perfiles son paralelos sobre ese denominador. No deben interpretarse como
embudo secuencial salvo que una tabla posterior lo declare expresamente.

Debe contener:

- scanner definition;
- base universe definition;
- profile ids;
- session/as-of;
- denominator;
- ranks;
- candidate reasons;
- source lineage;
- quality flags;
- downstream usage flags.

Debe preservar tambien filas del denominador que no activen ningun perfil,
porque son necesarias para medir falsos negativos y sesgo de seleccion.

No debe contener:

- labels;
- outcome;
- PnL;
- fill;
- reward;
- action;
- estrategia.

## 4. Fase 2: Strategy-specific experimental state

Ejemplo:

```text
das_candidate_state_table_experimental
```

Rol:

```text
Medir que paso dentro de candidatos in-play bajo una hipotesis concreta.
```

Puede contener namespaces de research como:

```text
scanner__
daily__
afterhours__
premarket__
frontside__
das__
vwap__
ema_wilder__
quality__
human_label__
outcome__
```

Antes de esta tabla puede existir un overlay de estrategia, por ejemplo:

```text
das_frontside_scanner
short_into_resistance_scanner
```

El overlay usa la tabla scanner como denominador/lineage y aplica filtros
propios. No puede redefinir silenciosamente la base de Data Foundation.

Pero su estado debe ser explicitamente experimental.

No puede reemplazar `market_state_table`.

## 5. Fase 3: Event state candidate

Rol:

```text
Reconstruir estado alrededor de un evento/candidato con reloj causal,
lookbacks legales y calidad declarada.
```

Debe poder explicar:

- que evento o candidato activo el estado;
- que datos estaban disponibles;
- que lookback se uso;
- que fuentes faltaban;
- que quality flags heredo;
- que esta prohibido consumir downstream.

## 6. Fase 4: Market state candidate

Rol:

```text
Componer componentes de Data Foundation en una representacion de estado.
```

Debe incluir, segun disponibilidad:

- instrument identity;
- market calendar/session;
- daily context;
- intraday context;
- microstructure;
- halts;
- fundamentals;
- news/catalyst;
- short context;
- short constraints;
- regime context;
- quality flags;
- scanner/candidate lineage.

## 7. Fase 5: Institutional market state

Solo puede existir si tiene:

- schema estable;
- registry;
- validators;
- consumption policy;
- manifests;
- quality inheritance;
- leakage tests;
- coverage declaration;
- changelog;
- promotion decision.

Hasta entonces, cualquier estado es candidato o experimental.

## 8. Regla de promocion

```text
El denominador base abre la puerta.
Los perfiles genericos explican por que una fila merece inspeccion.
El overlay de estrategia formula una hipotesis especifica.
El estado reconstruye el mundo observable.
La estrategia interpreta el estado.
El evaluador juzga decisiones bajo reglas bloqueadas.
```

## 9. Trabajo pendiente conocido

Pendiente antes de usar scanner-derived state para ML/RL institucional:

1. replay amplio de `daily_scanner_candidates_table`;
2. ventanas event/state gobernadas;
3. builders reales de `market_state` y `event_state`;
4. validators anti-leakage;
5. evidencia visual/forense por muestras;
6. promotion review;
7. registro de consumo por ML/RL.
