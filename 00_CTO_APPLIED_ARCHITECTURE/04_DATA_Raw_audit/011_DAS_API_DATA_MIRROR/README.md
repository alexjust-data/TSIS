# DAS API Data Mirror vs E_TSIS_DATA

Run revisado: `das_cmdapi_live_20260708T193719Z`
Captura DAS: `2026-07-08`
Raw DAS: `E:\TSIS\data_DAS_live\raw_cmdapi\runs\das_cmdapi_live_20260708T193719Z`

## Proposito

Este documento responde solo a la pregunta de espejo de datos:

```text
Que datos ofrece realmente DAS CMD API y si tenemos una familia equivalente bajo E:\TSIS\data.
```

No es una comparacion fila contra fila por fecha. Es una comparacion de familias/campos/capacidad real.

## Espejo Por Familia

| DAS API observado | Familia en E:\TSIS\data | Espejo | Lectura correcta |
| --- | --- | --- | --- |
| `$T&S` / `tms` | `trades_ticks_prod_2005_2026` / `000_TRADES` | Si, fuerte-parcial | Ambos son prints/trades: precio, size, tiempo. E tiene schema historico; DAS trae venue/flags propios. |
| `$Quote` / `lv1` | `quotes_` / `001_QUOTES` | Si, parcial | Ambos tienen bid/ask/size. E tiene timestamps SIP, sequence, conditions, tape/trf; DAS no entrega todo eso en Lv1. |
| `$Lv2` / `lv2` | sin espejo directo en `001_DATA_local_audit` | Extra DAS | DAS ofrece profundidad Lv2 limitada. No equivale a quotes SIP ni a L3/MBO. |
| `$Bar` / `MINCHART` | `ohlcv_1m` / `004_1_MINUTE` | Si, parcial | DAS devuelve barras 1m de chart. Para minuto vivo real, lo mas serio es reconstruir 1m desde `$T&S`. |
| `$Bar` / `DAYCHART` | `ohlcv_daily` / `002_DAILY` | Si, parcial | DAS devuelve barras daily historicas bajo demanda. No es daily foundation oficial. |
| `$LDLU`, `$SymStatus` | `Halts` / `008_HALTS` | Parcial | Es estado operativo live: bandas, SSR/status. No es halt master oficial. |
| `$SHORTINFO` | `short` / `009_SHORT`, `010_SHORT_REVIEW` | Parcial | Es shortability/short info DAS. No es short interest FINRA por settlement date. |
| `$TopLst`, `candidate_registry` | `reference` / scanner context | Parcial | Es lista/candidatos live. No es instrument master. |
| `account_state`, `%ORDER`, `%TRADE`, `%POS` | sin espejo publico local | Fuera | Es broker/account telemetry sensible. No debe mezclarse con familias de mercado. |

## Conteo Real Capturado

| familia_DAS | filas/eventos | que representa |
| --- | ---: | --- |
| `tms` | 65,590 | Time and Sales / trades live. |
| `lv2` | 36,327 eventos raw; 36,319 parseables | Depth/Lv2 DAS limitado. |
| `lv1` | 35,174 eventos raw; 35,081 quotes parseadas | Quotes Lv1: bid/ask/last/volume/VWAP/RVOL. |
| `minchart_1m` | 979 | Barras 1m DAS devueltas por comando `MINCHART`. |
| `daychart` | 104 | Barras daily DAS devueltas por comando `DAYCHART`. |
| `ldlu` | 179 | Limit down / limit up. |
| `symstatus` | 140 | Estado/SSR. |
| `shortinfo` | 18 | Short info para candidatos PASS. |
| `toplist` | 13 mensajes | Listas DAS tipo scanner seed. |
| `session` | 185 | Mensajes de sesion/no model-facing. |
| `account_state` | 2 | Estado cuenta/posicion; sensible. |

## Aclaracion Sobre DAYCHART

`DAYCHART` no significa que estuvimos conectados todo el dia.

DAS CMD API permite conectarse unos minutos y pedir barras daily historicas por comando. En el run se enviaron comandos como:

```text
SB SKYQ DAYCHART 2026/06/28 2026/07/08
```

Y DAS respondio con barras daily historicas:

```text
$Bar SKYQ 2026/06/29 4.1386 2.88 3.05 3.48 20002322 1
$Bar SKYQ 2026/06/30 4.18 3.41 3.91 3.67 12775434 1
```

Por eso hay `104` barras daily aunque la conexion duro minutos: se pidieron como historico de chart durante la conexion.

Detalle observado:

- `18` simbolos tuvieron respuestas `DAYCHART`.
- La mayoria devolvio `6` barras daily.
- Fechas principales devueltas: `2026/06/29`, `2026/06/30`, `2026/07/01`, `2026/07/02`, `2026/07/06`, `2026/07/07`.
- No debe interpretarse como captura live de todo el dia ni como daily foundation oficial.

## Respuesta Clara

Si, DAS API nos da un espejo real de varias familias que ya tenemos en `E:\TSIS\data`:

- trades: si, via `$T&S`;
- quotes: si parcial, via `$Quote`;
- 1m: si, reconstruible desde `$T&S`, y tambien hay `MINCHART` como chart vendor;
- daily: si parcial, via `DAYCHART` historico bajo demanda;
- short/status/halts: parcial, no institucional;
- Lv2: DAS ofrece algo adicional que no esta reflejado como familia local equivalente en `001_DATA_local_audit`.

No, DAS API no replica todo lo que tenemos en E: no entrega adjusted, split-normalized, reference completo, halts oficiales, short interest FINRA, additional datasets ni toda la metadata SIP de quotes.