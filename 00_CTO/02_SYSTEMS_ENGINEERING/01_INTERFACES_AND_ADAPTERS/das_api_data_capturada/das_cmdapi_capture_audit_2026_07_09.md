# DAS CMD API Capture Audit - 2026-07-09

Fecha de escritura documental: 2026-07-10  
Estado: auditado desde artefactos locales existentes  
Root auditado: `E:/TSIS/data_DAS_live`  
Copia CTO: `C:/TSIS_Data/00_CTO/02_SYSTEMS_ENGINEERING/01_INTERFACES_AND_ADAPTERS/das_api/`

## Alcance

Auditoria read-only de los artefactos existentes en:

```text
E:/TSIS/data_DAS_live
```

No se modifico ningun run DAS durante la auditoria. No se creo `final_summary.json` retroactivo.

Este informe documenta lo que fue descargado mediante DAS CMD API durante las conexiones de prueba y captura del 2026-07-08. Los payloads raw completos permanecen solo en `E:/TSIS/data_DAS_live`; este documento no copia credenciales ni transcripts completos.

## Inventario General

- Total auditado: `48` archivos.
- Tamano total: `77,414,826 bytes` aprox. `73.8 MiB`.
- Runs raw CMD API encontrados: `5`.
- Runs de screener encontrados: `2`.

Rutas principales:

```text
E:/TSIS/data_DAS_live/raw_cmdapi/runs/
E:/TSIS/data_DAS_live/screener/runs/
```

## Runs Encontrados

| Run | Tipo | Resultado auditado |
| --- | --- | --- |
| `das_cmdapi_dry_run_codex_20260706T2039Z` | dry-run | PASS, no abrio socket, no capturo datos reales |
| `das_cmdapi_live_20260708T191835Z` | live | FAIL por timeout, socket no abierto, sin eventos |
| `das_cmdapi_live_20260708T191918Z` | live | FAIL por timeout, socket no abierto, sin eventos |
| `das_cmdapi_live_20260708T192045Z` | live | socket abierto, screener parcial, 41 evaluados, 5 PASS, `final_summary.json` existe pero status `FAIL` sin `last_error` |
| `das_cmdapi_live_20260708T193719Z` | live | captura real principal, 100 evaluados, 18 PASS, streaming capturado, sin `final_summary.json` |

## Run Principal Recuperado

Run principal:

```text
E:/TSIS/data_DAS_live/raw_cmdapi/runs/das_cmdapi_live_20260708T193719Z
```

Ventana observada:

```text
start: 2026-07-08T19:37:35Z
last heartbeat: 2026-07-08T20:07:09Z
duracion aproximada: 29m 34s
```

Log:

```text
operator requested stop during streaming
```

Estado final auditado:

- `heartbeat.json` existe.
- `subscription_state.json` existe.
- `command_transcript.jsonl` existe.
- `events.jsonl` existe.
- `candidate_registry.jsonl` existe.
- `final_summary.json` no existe.

Interpretacion: la captura produjo datos utiles, pero el cierre no quedo completamente certificado porque no se escribio `final_summary.json`.

## Screener Del Run Principal

Screener:

```text
E:/TSIS/data_DAS_live/screener/runs/das_cmdapi_live_20260708T193719Z
```

Resultado:

- TOPLIST symbols vistos: `116`.
- Simbolos evaluados: `100`.
- PASS: `18`.
- FAIL: `82`.

Filtros usados:

```text
market_cap < 100,000,000
0.50 <= price <= 20.00
volume >= 300,000
sessions: premarket, regular_market, afterhours
```

Simbolos PASS:

```text
SKYQ, NVVE, TVRD, LHAI, ZCMD, VANI, SDOT, INLF, CLRO,
BTAI, VEEE, LUCY, JEM, BBLG, BJDX, VMAR, VTAK, SRXH
```

Principales motivos de FAIL:

- `market_cap_unavailable`: 63
- `price_outside_range`: 33
- `market_cap_above_limit`: 9
- `volume_below_min`: 7

## Datos Capturados

En el run principal se registraron:

- `command_transcript.jsonl`: `852` filas.
- `events.jsonl`: `138,711` filas.
- `candidate_registry.jsonl`: `136` filas.
- Eventos raw con linea DAS: `138,616`.
- Parse errors JSONL: `0`.

Familias de datos recibidas:

| Familia | Lineas | Definicion operativa en TSIS |
| --- | ---: | --- |
| `tms` | 65,590 | Time and Sales; prints/trades recibidos por suscripcion `SB <symbol> tms`. Es la base correcta para construir velas 1m del minuto vivo. |
| `lv2` | 36,327 | Top-of-book/regional level 2 observado por `SB <symbol> Lv2`. DAS confirmo que el API no expone TotalView/ARCA Book depth completo. |
| `lv1` | 35,174 | Level 1 quote stream recibido por `SB <symbol> Lv1`; incluye bid/ask, last, volume, high/low, open, VWAP y campos derivados cuando `ReturnFullLv1 YES` esta activo. |
| `minchart_1m` | 979 | Barras minuto devueltas por `SB <symbol> MINCHART ... 1`; evidencia historica/reciente, no sustituto certificado del minuto vivo durante streaming. |
| `ldlu` | 179 | Limit down / limit up por `GET LDLU <symbol>` o respuesta asociada. |
| `symstatus` | 140 | Symbol status por `GET SymStatus <symbol>`; incluye flags observados como SSR. |
| `daychart` | 104 | Barras diarias devueltas por `SB <symbol> DAYCHART ...`. |
| `shortinfo` | 18 | Short info por `GET SHORTINFO <symbol>`; formato posicional observado, no decodificado completamente en v0. |
| `toplist` | 13 | Listas DAS `$TopLst` recibidas por `SB TOPLIST`; usadas como fuente semilla del screener v0. |
| `session` | 185 | Handshake/login/session y lineas no clasificadas emitidas alrededor de la sesion. Puede incluir respuestas de cuenta/orden/trade no copiadas aqui. |
| `account_state` | 2 | Lineas de estado de cuenta reconocidas por parser v0. Cuenta/orden/trade son sensibles y no deben copiarse a docs compartidos. |

Simbolos con mas eventos:

| Symbol | Eventos |
| --- | ---: |
| TVRD | 34,887 |
| SKYQ | 23,936 |
| NVVE | 20,081 |
| SRXH | 18,278 |
| SDOT | 12,156 |
| VTAK | 9,489 |

## Atributos Observados Por Familia

Los atributos siguientes se derivan de `events.jsonl` del run principal. Son campos observados, no una certificacion completa del contrato DAS. El raw sigue siendo la fuente de verdad.

```sh
# Run auditado
run_id="das_cmdapi_live_20260708T193719Z"
events="E:/TSIS/data_DAS_live/raw_cmdapi/runs/das_cmdapi_live_20260708T193719Z/events.jsonl"

# toplist / $TopLst
family=toplist
prefix="$TopLst"
observed_attributes="list_name symbols"
operational_use="fuente semilla de candidatos; no es scanner market-wide filtrado por API"

# lv1 / $Quote
family=lv1
prefix="$Quote"
observed_attributes="symbol A Asz B Bsz V L Hi Lo op ycl tcl PE VWAP tradesAllDay RVOL T"
definition="Level 1 quote stream; bid/ask, sizes, volume, last, high/low, open, prior/today close, primary exchange, VWAP, trades count, relative volume and quote time"

# tms / $T&S
family=tms
prefix="$T&S"
observed_attributes="symbol price shares_or_size condition_or_sale_marker time venue flags"
definition="Time and Sales stream; base para construir OHLCV 1m vivo por simbolo suscrito"

# lv2 / $Lv2
family=lv2
prefix="$Lv2"
observed_attributes="symbol side market_maker_or_venue price size action time"
definition="Top-of-book/regional level 2 observado via CMD API; no equivale a Nasdaq TotalView/ARCA Book depth completo"

# ldlu / $LDLU
family=ldlu
prefix="$LDLU"
observed_attributes="symbol limit_down limit_up"
definition="Bandas limit down / limit up para el simbolo"

# symstatus / $SymStatus
family=symstatus
prefix="$SymStatus"
observed_attributes="symbol status_flags SSR TA TAT"
definition="Estado operativo del simbolo; SSR observado en el run"

# shortinfo / $SHORTINFO
family=shortinfo
prefix="$SHORTINFO"
observed_attributes="symbol positional_shortinfo_fields"
definition="Informacion short/availability en formato posicional; requiere decodificacion/certificacion posterior"

# daychart / $Bar
family=daychart
prefix="$Bar"
observed_attributes="symbol date bar_numeric_fields volume interval_or_type"
definition="Barras diarias solicitadas por DAYCHART; orden exacto de OHLC debe certificarse contra manual/parser antes de uso model-facing"

# minchart_1m / $Bar
family=minchart_1m
prefix="$Bar"
observed_attributes="symbol datetime_minute bar_numeric_fields volume interval_or_type"
definition="Barras minuto solicitadas por MINCHART 1; utiles para reconciliacion, pero el minuto vivo debe construirse desde tms"

# session
family=session
prefixes_observed="#Welcome #Please #LOGIN Client %POS %ORDER %TRADE"
observed_attributes="session_messages broker/account/order/trade_lines_not_republished_here"
definition="Mensajes de sesion y lineas no clasificadas emitidas alrededor de login; tratar como sensibles cuando contengan cuenta/orden/trade"

# account_state
family=account_state
prefixes_observed="#POS #POSEND"
observed_attributes="account_state_lines"
definition="Estado de cuenta/posiciones detectado por parser v0; sensible, no publicable sin sanitizacion"
```

## Resumen Por Simbolo PASS

| Symbol | Total eventos | Familias principales |
| --- | ---: | --- |
| TVRD | 34,887 | lv1, tms, lv2, ldlu, symstatus, shortinfo, daychart, minchart_1m |
| SKYQ | 23,936 | lv1, tms, lv2, ldlu, symstatus, shortinfo, daychart, minchart_1m |
| NVVE | 20,081 | lv1, tms, lv2, ldlu, symstatus, shortinfo, daychart, minchart_1m |
| SRXH | 18,278 | lv1, tms, lv2, shortinfo, ldlu, symstatus, daychart, minchart_1m |
| SDOT | 12,156 | lv1, tms, ldlu, symstatus, shortinfo, daychart, minchart_1m |
| VTAK | 9,489 | lv1, tms, shortinfo, ldlu, symstatus, lv2, daychart, minchart_1m |
| LHAI | 3,725 | lv1, tms, ldlu, symstatus, shortinfo, daychart, minchart_1m |
| LUCY | 3,170 | lv1, tms, shortinfo, ldlu, symstatus, lv2, daychart, minchart_1m |
| CLRO | 2,690 | ldlu, lv1, symstatus, shortinfo, tms, daychart, minchart_1m |
| VANI | 2,226 | ldlu, lv1, shortinfo, symstatus, tms, daychart, minchart_1m |
| ZCMD | 1,693 | lv1, ldlu, symstatus, shortinfo, tms, daychart, minchart_1m |
| JEM | 1,442 | lv1, ldlu, symstatus, shortinfo, tms, lv2, daychart, minchart_1m |
| VEEE | 1,208 | lv1, ldlu, symstatus, shortinfo, tms, lv2, daychart, minchart_1m |
| BTAI | 1,031 | ldlu, lv1, symstatus, shortinfo, tms, daychart, minchart_1m |
| BJDX | 816 | ldlu, lv1, symstatus, shortinfo, tms, lv2, daychart, minchart_1m |
| INLF | 658 | lv1, ldlu, symstatus, shortinfo, tms, daychart, minchart_1m |
| VMAR | 520 | lv1, ldlu, symstatus, shortinfo, tms, lv2, daychart, minchart_1m |
| BBLG | 173 | ldlu, lv1, symstatus, shortinfo, tms, lv2, daychart, minchart_1m |

## Seguridad / Credenciales

- `pre_manifest.json` declara `credentials_written_to_disk=false`.
- `LOGIN` aparece redactado en transcript.
- Auditoria detecto:
  - login commands: `1`
  - redacted login commands: `1`
  - raw login suspect: `0`

No se deben copiar payloads raw ni transcript completo a documentacion compartida.

## Observaciones Criticas

1. La captura principal contiene datos reales y recuperables.
2. El run principal no debe marcarse como PASS certificado porque falta `final_summary.json`.
3. El cierre fue incompleto: el log registra stop del operador, `QUIT` aparece en transcript, pero `subscription_state.json` aun muestra suscripciones activas.
4. La app v0 debe corregirse para garantizar `final_summary.json` y unsubscribe completo incluso tras `Ctrl+C`.
5. Estos datos son evidencia raw DAS, no dataset canonical ni Data Foundation.
6. DAS confirmo posteriormente que no existe scanner market-wide por API, que Trade Signal/Scanner son frontend-only, y que TotalView/ARCA Book/Fundamentals/News no aplican al CMD API. Por tanto, DAS API debe tratarse como capture/validation para simbolos ya seleccionados, no como scanner global NYSE/NASDAQ/AMEX.

## Conclusion

La descarga DAS util es principalmente el run:

```text
das_cmdapi_live_20260708T193719Z
```

Contiene evidencia real de Lv1, tms, Lv2, TOPLIST, SHORTINFO, SymStatus, LDLU, DAYCHART y MINCHART 1m para candidatos filtrados. Debe preservarse como raw evidence. No debe promocionarse a dataset estable hasta crear validadores/reconciliacion y corregir el cierre de runs.
