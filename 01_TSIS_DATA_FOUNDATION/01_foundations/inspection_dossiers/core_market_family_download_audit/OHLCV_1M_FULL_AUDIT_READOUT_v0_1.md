# OHLCV 1m Full Audit Readout v0.1

Fecha de cierre documental: 2026-08-24  
Familia: `ohlcv_1m`  
RAW auditado, solo lectura: `G:/TSIS/data/ohlcv_1m`  
Run principal: `20260823_ohlcv_1m_download_audit_v0_1`  
Estado: `PARTIAL_CERTIFICATION_PRESENT_DATA_HEALTHY_TEMPORALLY_INCOMPLETE`

## Veredicto

La ejecución técnica y la evidencia correspondiente a los Parquets presentes
son correctas:

```text
technical_execution                          = PASS
exact_4824_universe                          = PASS
present_parquet_integrity                    = PASS_ADOPTED_CLOSED_AUDIT
timestamp_and_session_reconciliation         = PASS
global_calendar_continuity_through_max_date  = PASS
requested_scope_to_2026_08_20                = FAIL_LOCAL_ARCHIVE_INCOMPLETE
per_ticker_provider_expectedness             = UNRESOLVED
overall                                      = PARTIAL_CERTIFICATION_PRESENT_DATA_HEALTHY_TEMPORALLY_INCOMPLETE
```

No se certifica que el archivo local esté completo hasta el 20 de agosto de
2026. La última fecha globalmente cubierta es 2026-03-09; únicamente diez
tickers alfabéticamente contiguos conservan actividad posterior, hasta
2026-03-27. Faltan globalmente las 100 sesiones XNYS entre 2026-03-30 y
2026-08-20.

## Decisión operativa congelada

```text
REDOWNLOAD_O_REPAIR_1M_AHORA       = NO
MUTAR_RAW_1M                       = NO
ESPERAR_TRADES_COMPLETO            = SI
CONSTRUIR_SCREENER_DIARIO          = SI, DESPUES DE CERRAR TRADES Y SEC PIT
REVISAR_SOLO_ENTRADAS_DEL_SCREENER = SI
RECONSTRUIR_VELAS_DESDE_TRADES     = SOLO SI UN CASO SELECCIONADO LO NECESITA
```

Esta auditoría no autoriza una redescarga completa de 1m ni la reparación de
los 5.238 casos sin RTH. El screener causal se construirá directamente con
Trades completos, Quotes y SEC PIT. Solo después se cruzarán sus
`ticker × session_date_et` seleccionados con las incidencias 1m. Si un caso
seleccionado necesita velas para el backtest, se reconstruirá una vista
derivada y versionada desde Trades; el RAW permanecerá inmutable.

## Qué significa exactamente el 0,05644 %

El denominador no es `4.824 × todas las sesiones esperadas`. Es el conjunto de
claves observadas `ticker × session_date_et` que contienen al menos una fila 1m.

```text
ticker-fecha observados con >= 1 fila 1m   9.280.325
ticker-fecha con >= 1 fila RTH             9.275.087
ticker-fecha observados sin filas RTH          5.238

5.238 / 9.280.325 × 100 = 0,0564419888 %
```

Por tanto, sí es el porcentaje de los **ticker-día observados** que no tienen
minutos RTH. No es el porcentaje de días esperados que faltan, porque los días
sin ninguna fila 1m no entran en este denominador. Tampoco demuestra por sí
solo una descarga defectuosa: los 5.238 casos tienen archivos presentes,
legibles y actividad observada fuera de RTH.

El segundo porcentaje usa otro denominador:

```text
filas 1m de los 5.238 casos                 14.302
total de filas 1m                    1.306.098.487

14.302 / 1.306.098.487 × 100 = 0,0010950170 %
```

Esto significa que el 0,001095 % de las filas observadas pertenece a esos
ticker-día sin RTH. No significa que esas filas falten.

Los 14.302 registros son barras **presentes** en premarket, after-hours o fuera
de 04:00-20:00. No son una estimación de 14.302 barras ausentes. La auditoría
de descarga no puede inferir cuántas barras RTH deberían existir sin observar
trades elegibles de la misma fecha.

## Resultado exacto sin RTH

| Actividad observada | Ticker-fecha | Filas 1m |
|---|---:|---:|
| Solo premarket | 2.295 | 6.726 |
| Solo after-hours | 2.799 | 5.495 |
| Premarket y after-hours | 143 | 1.959 |
| After-hours y fuera de 04:00-20:00 | 1 | 122 |
| **Total** | **5.238** | **14.302** |

Los 5.238 casos afectan a 1.571 tickers. La clasificación usa
`America/New_York` y `session_date_et`, derivados de `ts_utc`:

```text
premarket     [04:00, 09:30)
RTH           [09:30, 16:00)
after-hours   [16:00, 20:00)
outside       fuera de [04:00, 20:00)
```

## Forense cruzado posterior de los 5.238 casos

El contraste posterior separó ausencia de barra de evidencia de descarga
defectuosa. Se usaron Daily y el archivo legacy de Trades solamente como
testigos locales. Trades legacy contiene RTH y no es la fuente completa que se
está preparando; no se empleó Quotes como sustituto de un trade elegible para
formar OHLC.

```text
casos 1m observados sin RTH                         5.238
Daily ausente                                       4.430
Daily presente                                        808

con archivo Trades legacy disponible                3.121
sin trade RTH estrictamente elegible                 3.113
sin archivo Trades legacy                            2.117
candidatos locales de alta confianza                     8
```

Los 4.430 casos sin Daily no prueban por sí solos una pérdida: Daily también
depende de trades y reglas de agregación. Entre los 808 con Daily presente,
585 reproducen su OHLC con las barras extendidas ya presentes. Los 223
restantes son compatibles con condiciones que pueden actualizar volumen o
high/low sin actualizar open/close; por ello tampoco se clasificaron como
pérdida solo mediante Daily.

El clasificador estricto exigió que el trade legacy RTH actualizara tanto
`consolidated_updates_high_low` como `consolidated_updates_open_close`. Con esa
regla quedaron ocho `ticker × fecha` con evidencia local fuerte de una barra
1m RTH ausente:

| Ticker | Fecha ET |
|---|---|
| GYRO | 2007-06-18 |
| HBNC | 2007-07-19 |
| ITIC | 2005-04-27 |
| LVAC | 2022-08-09 |
| NBAC | 2020-05-13 |
| PNRG | 2007-09-10 |
| STRT | 2007-03-30 |
| TOP | 2023-05-12 |

```text
trades RTH estrictamente elegibles en los 8 casos       7.068
minutos elegibles únicos, cota inferior                    252
8 / 9.280.325 ticker-fecha observados             0,000086204 %
252 / 1.306.098.487 filas 1m                      0,000019294 %
```

`TOP` del 2023-05-12 concentra 7.060 trades elegibles y 244 minutos
elegibles. Su archivo 1m contiene 82 barras entre 04:00 y 09:28 ET, pero
ninguna en RTH, mientras Trades legacy contiene actividad RTH abundante. Es la
inconsistencia local más clara. Los otros siete casos suman ocho minutos
elegibles como cota inferior.

Esta clasificación es de **alta confianza local**, no una certificación de
paridad con el proveedor. La reconciliación directa con Massive REST no pudo
cerrarse con la credencial disponible: las consultas históricas devolvieron
`403` y después `429`. Tampoco puede extrapolarse el diccionario actual de
condiciones como si fuera una autoridad PIT para 2005-2026. Por ello:

- los ocho casos quedan registrados para revisión selectiva futura;
- los 2.117 casos sin archivo Trades legacy quedan `UNVERIFIED`, no
  `DEFECTIVE`;
- TradingView puede ayudar a localizar casos, pero una vela externa no prueba
  por sí sola un fallo: puede usar otro feed, elegibilidad o ajuste;
- Quotes prueba presencia de mercado, no que existiera un trade elegible para
  formar OHLC.

## Muestra pseudoaleatoria reproducible de 2025 y 2026

Selección uniforme dentro de los candidatos de cada año, con semilla fija
`20260824`; cinco casos de 2025 y cinco de 2026. La semilla hace que otro agente
obtenga exactamente los mismos ejemplos.

| Ticker | Fecha ET | Total | Premarket | RTH | After-hours | Patrón |
|---|---|---:|---:|---:|---:|---|
| FSEA | 2025-01-27 | 2 | 0 | 0 | 2 | Solo after-hours |
| BNIX | 2025-02-28 | 1 | 1 | 0 | 0 | Solo premarket |
| RDGT | 2025-07-14 | 1 | 0 | 0 | 1 | Solo after-hours |
| ISRL | 2025-09-02 | 1 | 0 | 0 | 1 | Solo after-hours |
| AMBI | 2025-10-21 | 1 | 1 | 0 | 0 | Solo premarket |
| VINC | 2026-01-14 | 1 | 1 | 0 | 0 | Solo premarket |
| HNST | 2026-03-09 | 2 | 2 | 0 | 0 | Solo premarket |
| HTCR | 2026-03-09 | 1 | 1 | 0 | 0 | Solo premarket |
| JFBR | 2026-03-09 | 8 | 8 | 0 | 0 | Solo premarket |
| KMDA | 2026-03-09 | 2 | 2 | 0 | 0 | Solo premarket |

Universos de selección: 307 casos en 2025 y 213 en 2026.

## Alcance físico y ejecución

```text
universo esperado / committed             4.824 / 4.824
fallos / reintentos                        0 / 0
ticker literal NA                         presente
Parquets                                   466.945
bytes                                      44.882.364.693
filas                                      1.306.098.487
ticker-session_date_et                     9.280.325
timestamps no parseables                   0
filas fuera del scope declarado            0
errores de ecuación por sesión             0
manifests de tarea verificados             4.824
artefactos de tarea con SHA-256 verificado 9.648
artefactos finales con SHA-256 verificado  4
```

El run comenzó en `2026-08-23T18:37:01.095418Z` y terminó en
`2026-08-24T01:07:23.906810Z`. La integridad física de los Parquets presentes
se adopta del run cerrado
`20260821_core_market_raw_alignment_audit_v0_1`, cuyo manifest fue verificado.
Este cierre no volvió a leer millones de footers: releyó `ts_utc` para
clasificar reloj y sesión, y verificó hashes, manifests, conteos y
reconciliaciones.

## Cobertura temporal

```text
primera session_date_et observada     2005-01-03
última session_date_et observada      2026-03-27
sesiones XNYS observadas              5.342
huecos globales XNYS hasta 2026-03-27 0
fechas globales no XNYS               0
sesiones XNYS ausentes después        100
primera ausencia global               2026-03-30
última ausencia del scope             2026-08-20
```

La cola es irregular:

```text
2026-03-06   2.564 tickers
2026-03-09   1.474 tickers
2026-03-10       8 tickers
...
2026-03-27       9 tickers
```

Solo `BCSF`, `BCTF`, `BCTX`, `BDL`, `BDN`, `BDSX`, `BDTX`, `BEAG`, `BEAT` y
`BEBE` aparecen después de 2026-03-09. Es evidencia fuerte de una cola parcial
o descarga interrumpida por lotes alfabéticos; no se presenta como causa
demostrada sin el manifest del downloader original.

## Distribución de filas por sesión

| Sesión | Filas | % de todas las filas |
|---|---:|---:|
| Premarket | 33.833.603 | 2,590432753 % |
| RTH | 1.243.035.794 | 95,171673987 % |
| After-hours | 29.225.478 | 2,237616710 % |
| Fuera de 04:00-20:00 | 3.612 | 0,000276549 % |
| **Total** | **1.306.098.487** | **100 %** |

Las 3.612 filas fuera de 04:00-20:00 ocupan 3.607 ticker-día y 478 tickers.
Se preservan; no se eliminan.

## Reconciliación del resultado antiguo 4.264

El valor antiguo no era el universo completo de fechas sin RTH. Era el
subconjunto que cumplía simultáneamente:

```text
1m presente
Daily ausente
rth_rows = 0
session_date_et <= 2026-03-06
```

Reconciliación exacta:

```text
nuevo conjunto completo sin RTH      5.238
subconjunto antiguo                   4.264
intersección                          4.264
antiguos ausentes del nuevo               0
nuevos no incluidos antes               974
```

Los 974 adicionales son 808 casos hasta 2026-03-06 donde Daily estaba presente
u otra condición del filtro estrecho no se cumplía, más 166 casos posteriores
a 2026-03-06. El antiguo 4.264 era correcto para su pregunta estrecha, pero fue
incorrecto presentarlo como total general de fechas 1m sin RTH.

## Reconciliación UTC a fecha de sesión ET

La auditoría anterior contaba 9.354.195 claves ticker-fecha física. La actual
cuenta 9.280.325 claves por `session_date_et`. No se perdió ninguna de las
1.306.098.487 filas.

```text
claves antiguas solo UTC             73.905
claves nuevas solo ET                    35
filas perdidas                            0
```

De las 73.905 claves antiguas exclusivas, 66.846 caían en sábado. La explicación
es el rollover de actividad after-hours almacenada bajo fecha UTC hacia la
sesión ET anterior. Para comparar familias debe usarse `session_date_et`, no el
campo físico `date` sin normalizar.

## Schema

Los 466.945 archivos contienen las 13 columnas requeridas:

```text
ticker, ts_utc, date, year, month, o, h, l, c, v, vw, n, t
```

Existen tres fingerprints físicos conocidos:

- 414.093 archivos con `v: double`;
- 52.346 archivos con `v: int64`;
- 506 archivos de `FCEL`/`XRX` con strings grandes, `v: int64` y `vw` de tipo
  Arrow `null`.

Los 506 archivos de FCEL/XRX conservan la columna `vw`, pero su valor no está
disponible. Esto es una limitación de contenido/schema y no evidencia de un
archivo no descargado.

## Scripts, configuración y pruebas

Todo el código empleado está dentro del proyecto:

| Papel | Ruta | SHA-256 |
|---|---|---|
| Auditor/finalizador | `01_TSIS_DATA_FOUNDATION/scripts/core_market_family_download_audit/audit_family_download.py` | `3C013410BB99A98A0718035F4B69ADFB6BDEE4021D9F900473A88E547CBD01E3` |
| Wrapper de run/resume | `01_TSIS_DATA_FOUNDATION/scripts/core_market_family_download_audit/run_family_download_audit.ps1` | `1ED3305C82F31465DF5A4BC883D3324570D8B173403F876820DDC66591C78438` |
| Monitor Python | `01_TSIS_DATA_FOUNDATION/scripts/core_market_family_download_audit/monitor_family_download_audit.py` | `3FE2D081BD571F3BF5F943A117205E5A82B27D9C64F18F4D34D96B43585949AF` |
| Wrapper del monitor | `01_TSIS_DATA_FOUNDATION/scripts/core_market_family_download_audit/monitor_family_download_audit.ps1` | `419ADE4862ABC373EC76924AE04FAB71DE9A7E6BF5DF29FA77DE1787002DE140` |
| Parada segura | `01_TSIS_DATA_FOUNDATION/scripts/core_market_family_download_audit/stop_family_download_audit.ps1` | `748445C9671D3A09EA57F0FDD5D87702F3DB8FC42C15C0AA381D1491582BD2C8` |
| Analizador de cierre 1m | `01_TSIS_DATA_FOUNDATION/scripts/core_market_family_download_audit/analyze_ohlcv_1m_full_audit.py` | `4B4DC77E5A61A882F11D58B0B54447EE225B6609EE678F64A7B9748BE9256BBF` |
| Configuración | `01_TSIS_DATA_FOUNDATION/configs/core_market_family_download_audit_v0_1.yaml` | `36DE28F348D3D8A511D6284D41ECD8C5CBDD6B0C7002E9BA2A0FD9BF02AE5D6C` |
| Pruebas | `01_TSIS_DATA_FOUNDATION/tests/core_market_family_download_audit/test_audit_family_download.py` | `9DADE24FC849D018E8A480FAD778D436CA25AC83DF6FCC59F53763590CC202EB` |

Los hashes describen los archivos en el momento de este readout. El analizador
de cierre es read-only respecto al RAW y a los runs cerrados; solo escribe
evidencia pequeña en el dossier.

## Comandos reproducibles

Ejecución Full utilizada:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_family_download_audit\run_family_download_audit.ps1" -Family ohlcv_1m -Mode Full -RunId "20260823_ohlcv_1m_download_audit_v0_1" -HumanAuthorizedFull -Detach
```

Monitor:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_family_download_audit\monitor_family_download_audit.ps1" -RunRoot "C:\TSIS_Data\runs\data_ops\core_market_family_download_audit\20260823_ohlcv_1m_download_audit_v0_1" -Watch
```

Reproducción del análisis de cierre:

```powershell
python "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_family_download_audit\analyze_ohlcv_1m_full_audit.py" --run-root "C:\TSIS_Data\runs\data_ops\core_market_family_download_audit\20260823_ohlcv_1m_download_audit_v0_1" --alignment-run-root "C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit\20260821_core_market_raw_alignment_audit_v0_1" --legacy-session-run-root "C:\TSIS_Data\runs\data_ops\core_market_session_coverage_audit\20260822_core_market_session_coverage_daily_1m_quotes_v0_2" --output-dir "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\inspection_dossiers\core_market_family_download_audit\evidence_assets\ohlcv_1m_full_audit_v0_1"
```

## Evidencia persistida

- `evidence_assets/ohlcv_1m_full_audit_v0_1/ohlcv_1m_full_audit_deep_summary_v0_1.json`
- `evidence_assets/ohlcv_1m_full_audit_v0_1/ohlcv_1m_no_rth_sample_2025_2026_v0_1.csv`
- `evidence_assets/ohlcv_1m_full_audit_v0_1/analysis_manifest_v0_1.json`
- `C:/TSIS_Data/runs/data_ops/core_market_family_download_audit/20260823_ohlcv_1m_download_audit_v0_1/03_closeout/final_manifest.json`

El manifest del análisis contiene hashes de todos los artefactos generados. El
resumen JSON contiene el resultado completo, incluidos patrones de sesión,
colas temporales, fingerprints de schema y reconciliaciones antiguas.

## Límites de esta certificación

Esta auditoría sí certifica:

- ejecución completa sobre los 4.824 tickers seleccionados;
- integridad adoptada de cada Parquet presente;
- ausencia de truncamiento técnico en los artefactos auditados;
- reconciliación de todas las filas por sesión ET;
- cobertura global continua de sesiones XNYS hasta la última fecha observada.

No certifica:

- que Massive no tuviera actividad en un ticker-día totalmente ausente;
- el lifecycle esperado de cada símbolo sin una autoridad independiente;
- completitud del archivo local hasta 2026-08-20;
- exactitud económica de OHLCV, duplicados por minuto o reglas de construcción
  de barras, que estaban fuera del scope de esta auditoría de descarga.

La siguiente fase autorizada no es reparar 1m. Es completar Trades, cerrar SEC
PIT y ejecutar el screener diario. Después se cruzarán sus entradas con los
ocho candidatos y con cualquier incidencia adicional que revele Trades
completo. Solo los casos materialmente relevantes para el backtest podrán
originar una reconstrucción derivada de velas, con nueva versión, lineage y
certificación. La cola temporal 1m hasta 2026-08-20 se tratará como una
adquisición futura separada; no modifica esta decisión.
