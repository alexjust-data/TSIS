# Daily Pattern Discovery Atlas v0.1

Fecha de revisión: 2026-08-25
Estado: `implementation_in_progress`
Módulo: `05_TSIS_STATISTICS_PATTERNS`
Máximo nivel de promoción posible: `exploratory_report_ready`

## 1. Decisión y pregunta inicial

TSIS construirá un censo descriptivo discovery-first sobre el universo cerrado
de 4.824 tickers. La pregunta inicial no es si una estrategia gana, sino qué
formas daily existen después de una activación observable:

```text
activación observable -> desarrollo multi-observación -> pico retrospectivo ->
debilidad observable -> evolución posterior observada
```

La intuición sobre gaps, runners, frontside, first red day, rupturas y backside
sirve para abrir líneas de investigación. No se impone como patrón verdadero.

## 2. Qué es y qué no es

Es un atlas de conteos, distribuciones, trayectorias, eventos descriptivos y
casos históricos. Su función es permitir tirar del hilo desde una cifra hasta
las velas reales que la producen y generar hipótesis posteriores.

No es un backtest, una estrategia long o short, una regla de entrada o salida,
una señal, una estimación de probabilidad, una medición de PnL, edge,
riesgo/recompensa, significancia o causalidad.

## 3. Datos y alcance cerrado

Autoridades:

- `G:/TSIS/data/ohlcv_daily`: evidencia OHLCV raw;
- `G:/TSIS/data/ohlcv_daily_adjusted`: vista derivada split-normalized;
- `ohlcv_daily_session_activity.parquet`: membresía exacta ticker-fecha;
- manifest cerrado de la auditoría upstream.

Alcance esperado del full:

- 4.824 tickers exactos;
- 9.290.966 sesiones;
- 44.423 ficheros raw;
- 2005-01-03 a 2026-03-06 observado.

El motor no sustituye la lista exacta por un intervalo ni amplía el universo.
Cada `source_daily_file` publicado debe ser una ruta canónica existente.

## 4. Tiempo, precio y causalidad

Las comparaciones entre observaciones usan OHLC split-normalized. OHLCV raw se
conserva como evidencia y escala contemporánea. `future_split_factor` puede
existir en el input ajustado, pero está prohibido físicamente en el output de
observables.

`D+k` significa la k-ésima observación disponible posterior del ticker, no el
k-ésimo día calendario ni una garantía de continuidad de mercado. Por tanto,
D+20 puede abarcar más de 20 sesiones de mercado cuando faltan observaciones.
La fecha real siempre se conserva y la app permite inspeccionarla.

Una fila `analysis_eligible=false` se conserva para reconciliar el censo, pero
no puede activar etiquetas, producir outcomes, alterar máximos acumulados ni
originar eventos retrospectivos.

## 5. Unidades de análisis

### 5.1 Sesión observable

Una fila por `ticker, date`, construida solo con la observación actual y las
anteriores. Incluye OHLCV, gap, variaciones ya observadas, rango, posición del
cierre, volumen relativo, estados de vela y referencias rolling de máximos.
Esas variaciones históricas no son PnL.

Las referencias nombradas en v0.1 significan:

- previous day: 1 observación anterior;
- previous week: máximo de 5 observaciones anteriores;
- previous month: 21 observaciones anteriores;
- previous quarter: 63;
- previous half year: 126;
- previous year: 252.

Son proxies rolling-N, no semanas, meses o años calendario. La activación de
ruptura v0.1 es un `high pierce`: `High actual > máximo High de la ventana
anterior`. No equivale a ruptura por cierre.

### 5.2 Etiqueta de activación

Una fila por `ticker, date, activation_label`. El programa aplica un catálogo
determinista a todas las sesiones elegibles. Nadie elige casos uno por uno y
una sesión conserva todas las etiquetas que cumpla.

Los gaps son umbrales acumulativos. `gap_ge_30pct` significa
`Open / PreviousClose - 1 >= 0.30`. Un gap del 60% cumple también los umbrales
10%, 20%, 30% y 50%. v0.1 no contiene un bucket exclusivo 30%-50%.

Familias materializadas:

- gap;
- avance close-close;
- expansión de volumen;
- gran rango;
- ruptura rolling-N del máximo anterior.

Una etiqueta describe una condición observada; no significa comprar, vender o
esperar un resultado.

### 5.3 Caso de activación y cohorte directa

`activation_case_index.parquet` contiene una fila por sesión activada, aunque
tenga varias etiquetas. Para cada etiqueta, `cohort_statistics.parquet` resume
el 100% de sus apariciones desde D0 hasta D+20. Las activaciones pueden solaparse
porque la pregunta es qué ocurrió después de cada aparición.

La app deriva la trayectoria individual desde las sesiones para mostrar hasta
120 observaciones previas y 60 posteriores. Los agregados usan D0..D+20.

### 5.4 Eventos descriptivos de todas las activaciones

`activation_event_statistics.parquet` resume, por etiqueta, el offset observado
de:

- pico retrospectivo dentro de D0..D+20;
- primera vela roja;
- primera vela roja estrictamente después de D0;
- primer lower close;
- primer lower high;
- primera observación posterior sin nuevo máximo acumulado.

Son outcomes retrospectivos. Se publican conteo de casos, conteo observado,
media y P25/P50/P75/P90 del offset. Empates del pico se resuelven por la primera
observación elegible.

### 5.5 Ciclo cooldown secundario

`episodes.parquet`, `episode_trajectories.parquet` y `episode_events.parquet`
forman una segunda unidad: anclas seleccionadas determinísticamente con 20
observaciones de cooldown global. Sirven para estudiar ciclos menos solapados,
pero no representan todas las activaciones y no responden por sí solas qué pasó
después de cada gap.

`cycle_cohort_statistics.parquet` queda nombrado explícitamente como esa vista
secundaria. No se mezcla con la cohorte directa principal.

## 6. Estadística materializada v0.1

Para cohortes directas:

- observaciones, casos de activación y tickers únicos;
- media y desviación estándar de cierre relativo a D0;
- P10, P25, mediana, P75 y P90;
- frecuencia observada de vela roja.

Para eventos directos:

- casos de activación y eventos observados;
- media y P25, mediana, P75 y P90 del offset.

También se publica cobertura por año. Min/max, histogramas, concentración por
ticker/año y desgloses adicionales quedan como backlog; no se presentan como
si ya existieran. No se calculan p-values, inferencia ni probabilidades.

## 7. Censura y casos no disponibles

Un caso es `right_censored` si no dispone de 21 observaciones desde D0. La
censura se conserva tanto en el índice directo como en los ciclos cooldown. Un
evento no observado aparece como ausencia de offset y reduce `event_observed`;
no se convierte en cero. Todos los conteos de D0 de cohortes directas deben
reconciliar exactamente con las etiquetas originales.

## 8. Lentes de Stephen Dux

Los diez textos revisados se usan como biblioteca de preguntas, no como reglas
a copiar. v0.1 representa directamente first red day, resistencias rolling,
gaps, volumen relativo, runners mediante trayectorias y picos retrospectivos.

Quedan como backlog explícito: resistencias multicapa compuestas, secuencia
caída-rebote-gap, failed breakout formal, multi-day top formal, float rotation
PIT y condiciones intradía. Se excluyen entradas, shorts, dip buys, premarket,
double intraday top, stops, ejecución y PnL.

## 9. Explorador visual local

La aplicación vive dentro del módulo y solo escucha en localhost. Navegación:

1. seleccionar una etiqueta;
2. ver trayectoria mediana, dispersión, pico y first red day agregados;
3. abrir cualquiera de los casos reales que forman la cifra;
4. recorrer su historial daily con gráfico interactivo;
5. guardar notas humanas separadas del censo.

El gráfico individual usa TradingView Lightweight Charts:

- velas daily split-normalized;
- panel de volumen inferior independiente y redimensionable;
- cursor con fecha y OHLCV;
- zoom con rueda y desplazamiento por arrastre;
- 120 observaciones anteriores y 60 posteriores disponibles;
- botón para recentrar D0;
- D0 marcado debajo de la vela;
- outcomes agrupados por fecha y marcados encima de la vela;
- autoescala y márgenes que mantienen las marcas fuera de las mechas.

La app no debe presentarse como válida si `/api/meta` no devuelve
`status: pass` para el run que consume.

## 10. Artefactos gobernados

Outputs primarios y derivados:

- `session_observables.parquet`;
- `activation_labels.parquet`;
- `activation_case_index.parquet`;
- `cohort_statistics.parquet`;
- `activation_event_statistics.parquet`;
- `episodes.parquet`;
- `episode_trajectories.parquet`;
- `episode_events.parquet`;
- `cycle_cohort_statistics.parquet`;
- `coverage_by_year.parquet`;
- `case_index.parquet`;
- `run_manifest.json`;
- `terminal_certification.json`;
- `certification_readout.md`.

Los manifests registran commit, hash de configuración, identidad/hash upstream,
ruta raw canónica y, para cada Parquet final, filas, bytes, schema y SHA-256.

## 11. Gates obligatorios

Antes de autorizar un full con una versión nueva:

1. implementación y tests sintéticos;
2. un probe production-equivalent acotado en cada uno de los 8 shards;
3. mismo runner, agregador, manifest y certificador que el full;
4. auditoría de fórmulas seleccionadas y muestra legible;
5. equivalencia física de schemas entre todos los parts;
6. exclusión exacta de filas inválidas de outcomes y eventos;
7. reconciliación de cohortes/eventos directos con todas las activaciones;
8. autorización gobernada versionada.

El full solo cierra si reconcilia 4.824 tickers y 9.290.966 sesiones, pasan todos
los gates, la app compila y su API consume únicamente el run certificado, el
lineage reconstruye la ejecución y Graphify queda refrescado o en cola.

## 12. Estado de ejecuciones

`20260824_full_v0_1` fue invalidado por la auditoría posterior aunque su antiguo
certificador estructural devolviera PASS. Se conserva sin borrado bajo
`runs/invalidated/20260824_full_v0_1_post_run_audit_fail` y está prohibido para
la app o un readout oficial. Los incidentes están registrados en
`INCIDENT_REGISTER_v0_1.md`.

La implementación corregida espera nuevos probes `20260825_probe_v0_2`. Solo si
los ocho pasan se autorizará `20260825_full_v0_1`. Hasta entonces el estado es
`implementation_in_progress`, no `exploratory_report_ready`.
