# DasTrades CMD API System Map v0.1

> STATUS 2026-07-09: DEPRECATED / NOT ACTIVE FOR EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003.  
> Project decision: DAS CMD API will not be used as market-data source for DAS 0003 because it is not useful/available for the current work.  
> This document remains as historical technical reference for the DasTrades/Sage CMD API integration boundary only.  

Fecha de creacion: 2026-07-07  
Fecha de actualizacion: 2026-07-08  
Estado: local_detailed_system_map_gitignored  
Owner layer: `00_CTO/02_SYSTEMS_ENGINEERING/01_INTERFACES_AND_ADAPTERS/das_api`  
Git policy: local ignored document; do not publish unless a sanitized publication scope is explicitly approved.  

## Proposito

Este documento es el mapa CTO detallado de la integracion TSIS con
DasTrades/Sage CMD API.

`00_CTO` actua como cerebro arquitectonico: aqui se explica la vision completa,
los boundaries, el flujo de datos, la app terminal, los datos que se pueden
capturar, los contratos que gobiernan cada pieza y donde vive cada artefacto.

Este documento no contiene credenciales, payloads reales, account ids ni
transcripts reales. Tampoco habilita ejecucion.

## Disambiguation Obligatoria

```text
DasTrades/Sage CMD API = proveedor/API live y posible broker interface
DAS = estrategia de trading distinta, no pertenece a este mapa API
```

No mezclar estos dos significados en rutas, contratos, Graphify, notas de
agentes ni nombres de carpetas.

## Lecturas Autoritativas Y Enlaces

### Arquitectura general versionable

```text
C:/TSIS_Data/00_CTO/02_SYSTEMS_ENGINEERING/01_INTERFACES_AND_ADAPTERS/README.md
C:/TSIS_Data/00_CTO/02_SYSTEMS_ENGINEERING/01_INTERFACES_AND_ADAPTERS/live_source_adapter_topology_v0_1.md
C:/TSIS_Data/00_CTO/02_SYSTEMS_ENGINEERING/01_INTERFACES_AND_ADAPTERS/broker_api_safety_boundary_v0_1.md
```

### Referencia cruda local del proveedor

```text
C:/TSIS_Data/00_CTO/99_REFERENCE_LIBRARY/DasTrades_API/
```

Uso:

- manual de CMD API;
- zips oficiales;
- ejemplos oficiales;
- notebooks exploratorios;
- dumps/transcripts locales;
- notas privadas locales.

Regla:

```text
reference library != contrato operativo
```

### Contratos operativos del modulo live

```text
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps/01_data_ingestion_live/vendor_das/README.md
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps/01_data_ingestion_live/vendor_das/das_cmdapi_capture_contract_v0_1.md
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps/01_data_ingestion_live/vendor_das/das_cmdapi_data_catalog_v0_1.md
```

Uso:

- contrato de captura;
- catalogo de datos disponibles;
- reglas read-only/data-only;
- run artifacts obligatorios;
- command allowlist/blocklist;
- source inventory;
- gaps de evidencia.

### Implementacion local de la app terminal

```text
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps/src/das_cmdapi/
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps/configs/das_cmdapi_capture_v0_1.example.json
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps/tests/test_das_cmdapi_contract.py
```

Uso:

- app terminal;
- config local;
- validacion de allowlist/blocklist;
- escritura de run files;
- monitor;
- helpers de screener.

### Data plane fisico

```text
E:/TSIS/data_DAS_live/
```

Uso:

- runs raw CMD API;
- JSONL append-only;
- heartbeat;
- summaries;
- screener outputs;
- catalogos derivados si se declaran.

Regla:

```text
live payloads do not live in Git
```

## Mapa De Capas

```text
DasTrades/Sage CMD API manual and examples
-> 00_CTO/99_REFERENCE_LIBRARY/DasTrades_API/

CTO detailed system map
-> 00_CTO/02_SYSTEMS_ENGINEERING/01_INTERFACES_AND_ADAPTERS/das_api/

Module-owned capture contract and data catalog
-> 02_TSIS_webSocket_SmallCaps/01_data_ingestion_live/vendor_das/

Terminal app / adapter implementation
-> 02_TSIS_webSocket_SmallCaps/src/das_cmdapi/

Local config
-> 02_TSIS_webSocket_SmallCaps/configs/das_cmdapi_capture_v0_1.example.json

Physical live data root
-> E:/TSIS/data_DAS_live/

Field parity and model-facing gate
-> 02_TSIS_webSocket_SmallCaps/01_data_ingestion_live/source_parity_audit/

Future execution bridge, if ever approved
-> 02_TSIS_webSocket_SmallCaps/05_execution_bridge/
-> 02_TSIS_webSocket_SmallCaps/06_risk_monitor/
```

## Estado Actual De La App

Estado a 2026-07-08:

```text
v0 interactive terminal capture app implemented; pending live DAS smoke test
```

La app actual:

- pide credenciales DAS en terminal y no las escribe a disco;
- abre socket DAS CMD API;
- envia `LOGIN <user> <password> <account> 0` con transcript redactado;
- valida allowlist/blocklist antes de cada send;
- escribe los archivos obligatorios de run;
- captura TOPLIST/Lv1 para screener inicial;
- aplica denominador inicial de market cap, precio, volumen y sesion;
- limita el screener a `100` simbolos evaluados por contrato;
- imprime en terminal TOPLIST, universo candidato y cada decision PASS/FAIL con price, volume, market cap, session y motivos;
- escribe screener outputs;
- pregunta si se quiere descargar full data para candidatos PASS;
- si se acepta, suscribe candidatos a Lv1, tms y Lv2 si estan habilitados;
- consulta SHORTINFO, LDLU, SymStatus, DAYCHART y MINCHART 1m;
- mantiene lectura de stream hasta `Ctrl+C` o `capture_seconds`;
- refresca heartbeat y subscription_state mientras corre;
- intenta unsubscribe y `QUIT` al cerrar;
- soporta dry-run y monitor de run directory.

No debe documentarse como smoke PASS productivo hasta ejecutar una prueba real
contra DAS en horario valido y revisar `command_transcript.jsonl`, `events.jsonl`,
`candidate_registry.jsonl`, `screener_manifest.json` y `final_summary.json`.
## Arquitectura Del Paquete `src/das_cmdapi`

```text
src/das_cmdapi/
  __init__.py
  allowlist.py
  capture.py
  client.py
  config.py
  market_cap.py
  monitor.py
  parsing.py
  run_files.py
  screener.py
  README.md
```

### `capture.py`

Rol:

```text
terminal entry point and live capture orchestrator
```

Responsabilidades actuales:

- parsear CLI args;
- cargar config;
- aplicar overrides de `--data-root`, `--run-id`, `--symbol`, `--capture-seconds` y `--max-screener-symbols`;
- pedir credenciales en terminal para live mode;
- crear run files antes de captura;
- conectar al socket DAS;
- enviar LOGIN con redaction en transcript;
- ejecutar screener con salida terminal observable y limite efectivo `100`;
- preguntar por descarga full data;
- subscribir/desubscribir candidatos PASS;
- registrar transcript/event JSONL mientras corre;
- cerrar con `final_summary.json` si el proceso termina controladamente.

Comando live normal:

```powershell
$env:PYTHONPATH = "C:\TSIS_Data\02_TSIS_webSocket_SmallCaps\src"
python -m das_cmdapi.capture --config "C:\TSIS_Data\02_TSIS_webSocket_SmallCaps\configs\das_cmdapi_capture_v0_1.example.json"
```

Comando dry-run:

```powershell
$env:PYTHONPATH = "C:\TSIS_Data\02_TSIS_webSocket_SmallCaps\src"
python -m das_cmdapi.capture --dry-run --config "C:\TSIS_Data\02_TSIS_webSocket_SmallCaps\configs\das_cmdapi_capture_v0_1.example.json"
```

Comando con run id explicito:

```powershell
$env:PYTHONPATH = "C:\TSIS_Data\02_TSIS_webSocket_SmallCaps\src"
python -m das_cmdapi.capture --run-id "das_cmdapi_live_<timestamp>" --config "C:\TSIS_Data\02_TSIS_webSocket_SmallCaps\configs\das_cmdapi_capture_v0_1.example.json"
```
### `config.py`

Rol:

```text
config schema and defaults
```

Defaults principales:

| Campo | Valor actual |
| --- | --- |
| host | `127.0.0.1` |
| port | `9800` |
| data_root | `E:/TSIS/data_DAS_live` |
| login_mode | `terminal_prompt_socket_login` |
| socket_login_enabled | `false` in config; enabled in memory by live terminal app after credential prompt |
| locate_queries_enabled | `false` |
| channels | `Lv1`, `tms`, `Lv2`, `TOPLIST`, `DAYCHART`, `MINCHART` |
| symbol_queries | `SHORTINFO`, `LDLU`, `SymStatus` |
| account_queries | `BP`, `AccountInfo`, `POSITIONS`, `ORDERS`, `TRADES`, `ROUTESTATUS`, `LOCATES`, `INTMSGS` |
| daychart_days_back | `10` |
| minchart_minutes_back | `60` |
| max_screener_symbols | `100` hard contract cap |
| stream_poll_seconds | `1.0` |
| capture_seconds | `null` means run until `Ctrl+C` |
| max_response_bytes | `50000000` |
### `allowlist.py`

Rol:

```text
read-only command validation and execution blocklist
```

Hard-blocked by default:

```text
NEWORDER
REPLACE
CANCEL ALL
CANCEL
COMPLEXORDER
SLNEWORDER
SLCANCELORDER
SLOFFEROPERATION
```

Socket `LOGIN` is disabled for generic validation. In live mode the terminal app enables it only after prompting credentials and redacts it in transcript.

Short locate read-only inquiries are disabled unless
`locate_queries_enabled=true`.

### `run_files.py`

Rol:

```text
run directory and atomic/append-only output helpers
```

Debe asegurar que cada run tenga paths consistentes, JSON atomic cuando aplica
y JSONL append-only para evidencia incremental.

### `monitor.py`

Rol:

```text
terminal run monitor
```

Comando esperado:

```powershell
$env:PYTHONPATH = "C:\TSIS_Data\02_TSIS_webSocket_SmallCaps\src"
python -m das_cmdapi.monitor "E:\TSIS\data_DAS_live\raw_cmdapi\runs\<run_id>"
```

### `screener.py`

Rol:

```text
screener denominator helpers
```

Evalua candidatos sin inventar datos ausentes. Si falta market cap, price,
volume o session, el candidato debe fallar con razon explicita o quedar como
unavailable, no asumirse valido.

### `client.py`

Rol esperado:

```text
DAS socket client boundary
```

En v0 debe seguir subordinado al contrato read-only/data-only y al blocklist
antes de cualquier send.

## Flujo De Ejecucion De La App

### Flujo actual live capture

```text
PowerShell command
-> load config
-> apply CLI overrides
-> prompt DAS credentials in terminal
-> create run_id
-> create run directory under E:/TSIS/data_DAS_live/raw_cmdapi/runs/<run_id>
-> write pre_manifest.json and pid_manifest.json
-> connect to DAS host/port
-> send redacted LOGIN through socket
-> send read-only session setup commands
-> capture TOPLIST/Lv1 evidence for screener
-> evaluate denominator and write candidate_registry/screener outputs
-> ask operator whether to download full data for PASS candidates
-> if accepted, subscribe configured PASS candidate channels
-> append command_transcript.jsonl continuously
-> append events.jsonl continuously
-> refresh heartbeat.json atomically
-> update subscription_state.json after subscribe/unsubscribe changes
-> keep reading stream until Ctrl+C or capture_seconds
-> unsubscribe active channels
-> send QUIT
-> write final_summary.json on controlled stop
```

### Flujo dry-run

```text
PowerShell command with --dry-run
-> load config
-> apply CLI overrides
-> create run_id
-> create run directory under E:/TSIS/data_DAS_live/raw_cmdapi/runs/<run_id>
-> build command plan
-> validate every command against allowlist/blocklist
-> write pre_manifest.json
-> write pid_manifest.json
-> write subscription_state.json
-> append command_transcript.jsonl
-> append events.jsonl dry_run_no_socket
-> write heartbeat.json
-> write final_summary.json
-> exit PASS/FAIL without opening socket
```
## Data Storage Architecture Decision

La arquitectura fisica de DAS live tiene dos capas obligatorias:

```text
1. raw evidence layer
   -> particion primaria por run_id
   -> verdad de auditoria append-only

2. normalized query layer
   -> particion por data_family / market_date / symbol
   -> forma comoda para analisis, replay, inspeccion y futuros builders
```

Regla central:

```text
raw_cmdapi/runs/<run_id> is the audit truth
normalized/<data_family>/market_date=<YYYY-MM-DD>/symbol=<SYMBOL>/ is the query surface
```

No se debe usar `date/symbol` como particion primaria del raw porque DAS CMD API
es un stream operacional: comandos, respuestas, no-response, errores,
subscriptions, heartbeats y cortes de luz se entienden por run. La particion
por fecha/ticker se construye despues como capa normalizada derivada.

### Required Physical Layout

```text
E:/TSIS/data_DAS_live/
  README.md

  raw_cmdapi/
    runs/
      <run_id>/
        pre_manifest.json
        pid_manifest.json
        heartbeat.json
        command_transcript.jsonl
        events.jsonl
        candidate_registry.jsonl
        subscription_state.json
        capture.log
        final_summary.json

  screener/
    runs/
      <run_id>/
        screener_manifest.json
        candidates.jsonl
        candidates.csv

  normalized/
    lv1/
      market_date=<YYYY-MM-DD>/
        symbol=<SYMBOL>/
          data.parquet
    tms/
      market_date=<YYYY-MM-DD>/
        symbol=<SYMBOL>/
          data.parquet
    lv2/
      market_date=<YYYY-MM-DD>/
        symbol=<SYMBOL>/
          data.parquet
    toplist/
      market_date=<YYYY-MM-DD>/
        data.parquet
    shortinfo/
      market_date=<YYYY-MM-DD>/
        symbol=<SYMBOL>/
          data.parquet
    symstatus/
      market_date=<YYYY-MM-DD>/
        symbol=<SYMBOL>/
          data.parquet
    ldlu/
      market_date=<YYYY-MM-DD>/
        symbol=<SYMBOL>/
          data.parquet
    daychart/
      market_date=<YYYY-MM-DD>/
        symbol=<SYMBOL>/
          data.parquet
    minchart_1m/
      market_date=<YYYY-MM-DD>/
        symbol=<SYMBOL>/
          data.parquet
    account_state/
      market_date=<YYYY-MM-DD>/
        run_id=<run_id>/
          data.parquet

  indexes/
    candidate_daily_index/
      market_date=<YYYY-MM-DD>/
        candidates.parquet
    run_index.parquet

  catalog/
    das_cmdapi_command_catalog_v0_1.json
    das_cmdapi_field_inventory_v0_1.md
```

`normalized/account_state` is separated from symbol-market data because account
and broker telemetry can be sensitive and is not automatically model-facing.

### Date And Timestamp Semantics

- Every raw event must preserve `observed_at_utc`.
- Any source timestamp returned by DAS must be preserved as a source field.
- Normalized partitions use `market_date=<YYYY-MM-DD>` for the US equity market
  session date, not the local machine date in Europe.
- If market_date cannot be inferred safely, the event remains in raw and the
  normalized writer must record an explicit `market_date_unavailable` reason.

### Candidate Registry Contract

Every ticker that passes or is evaluated by the screener must produce an entry
in:

```text
raw_cmdapi/runs/<run_id>/candidate_registry.jsonl
```

Minimum fields:

| Field | Meaning |
| --- | --- |
| `run_id` | Capture run id. |
| `detected_at_utc` | Time TSIS detected/evaluated the candidate. |
| `market_date` | US equity market date if known. |
| `session` | `premarket`, `regular_market` or `afterhours` if known. |
| `symbol` | Candidate ticker. |
| `price_usd` | Price used for the denominator if available. |
| `volume_shares` | Volume used for the denominator if available. |
| `market_cap_usd` | Market cap from governed TSIS reference unless DAS is later certified. |
| `filter_status` | `pass`, `fail` or `unavailable`. |
| `failure_reasons` | Explicit reasons; missing fields are not invented. |
| `capture_plan` | Data families planned for full capture. |
| `capture_status` | `pending`, `active`, `complete`, `partial`, `failed` or `interrupted`. |
| `raw_event_refs` | References to raw run/event offsets or command transcript ids when available. |
| `normalized_paths` | Paths written under `normalized/` when available. |

### Full Candidate Capture Bundle

For every candidate that passes the initial screener, the app should attempt the
full read-only symbol bundle allowed by config:

- Lv1;
- Time and Sales;
- Lv2 if enabled;
- TOPLIST context if available;
- SHORTINFO;
- LDLU;
- SymStatus;
- DAYCHART;
- MINCHART 1m;
- no-response / permission / login-required observations.

`all data` means all read-only data families available to the app and permitted
by config/contract. It does not mean orders, cancels, replaces, locate orders,
credential capture or unredacted account secrets.

### Write Order

During live capture:

1. Write raw JSONL first.
2. Flush raw JSONL continuously.
3. Update heartbeat.
4. Append/update candidate registry.
5. Write normalized outputs only after raw evidence exists.
6. Link normalized outputs back to raw run ids and event ids.

A normalized writer failure must not invalidate raw evidence.

## Run Artifacts Obligatorios

Cada run real o dry-run debe escribir:

| File | Timing | Proposito |
| --- | --- | --- |
| `pre_manifest.json` | antes de socket/subscriptions | declara run id, config, command set, redaction policy y data root |
| `pid_manifest.json` | tras iniciar proceso | declara host/process/python/output paths |
| `heartbeat.json` | durante el run | stage, progreso, counters, bytes, ultimo error |
| `command_transcript.jsonl` | continuo | comando enviado, respuesta raw/redacted, timestamps, status |
| `events.jsonl` | continuo | evento/linea DAS preservada con metadata TSIS |
| `subscription_state.json` | al cambiar subscriptions | simbolos/canales activos |
| `capture.log` | continuo | log humano operacional |
| `final_summary.json` | solo cierre limpio | counts, status, errores, completitud |

## Power Loss / Interrupciones

La evidencia critica son los JSONL flushed durante el run:

```text
command_transcript.jsonl
events.jsonl
```

Si se corta la luz:

1. no se sobrescribe el run interrumpido;
2. si falta `final_summary.json`, el run queda `INCOMPLETE`;
3. los JSONL ya escritos siguen siendo evidencia valida;
4. el siguiente intento usa nuevo `run_id`;
5. cualquier recovery/index debe escribir un manifest separado.

## Datos Que Puede Descargar/Capturar DAS CMD API

Este inventario depende de permisos, sesion DAS, horario de mercado, simbolo y
configuracion de la plataforma. Una ausencia de respuesta es evidencia valida,
no un fallo silencioso.

### 1. Session / Authentication / Client State

Comandos previstos:

```text
ECHO OFF
CLIENT
ReturnFullLv1 YES
LOGIN <user> <password> <account> 0  # terminal prompt only; transcript redacted
QUIT
```

Regla:

```text
terminal_prompt_socket_login by default
```

El operador humano se loguea en DAS Trader / Passport / frontend. La app no
debe guardar credenciales.

### 2. Level 1 Quotes

Comandos:

```text
SB <symbol> Lv1
UNSB <symbol> Lv1
ReturnFullLv1 YES
```

Familias esperadas:

- symbol;
- bid/ask price;
- bid/ask size;
- last price;
- volume;
- open/high/low/close-like fields si DAS los retorna;
- VWAP/RVOL/tradesAllDay si DAS los retorna;
- timestamp/session fields si DAS los retorna.

Uso TSIS:

- feed live primario para small universe;
- fuente preferente para precio y volumen del screener;
- no model-facing hasta parity/cutoff contract.

### 3. Time And Sales

Comandos:

```text
SB <symbol> tms
UNSB <symbol> tms
```

Familias esperadas:

- print price;
- print size;
- trade flags/conditions;
- print time;
- venue/market center si retorna;
- side/indicator si retorna.

Uso TSIS:

- tape live;
- acumulacion de volumen si la ventana de captura es completa;
- evidencia para microestructura live.

### 3b. Level 3 / Market-By-Order Depth

Estado v0:

```text
not certified / not in current DAS CMD API contract
```

TSIS no debe prometer L3 hasta encontrar y probar un comando/payload DAS
explicito equivalente a market-by-order o profundidad order-level. Si el manual
local demuestra un comando L3, se debe anadir primero al catalogo, allowlist,
parser y smoke test. Mientras tanto, `Lv2` es la profundidad certificable de v0.
### 4. Level 2 Book

Comandos:

```text
SB <symbol> Lv2
UNSB <symbol> Lv2
```

Familias esperadas:

- side/condition;
- MMID/venue;
- level price;
- level size;
- time/order metadata si retorna.

Notas:

- puede no devolver datos por permisos, simbolo, horario o setup;
- debe capturarse `no_response` como observacion valida;
- usar solo en simbolos seleccionados por capacidad.

### 5. Top Lists / Scanner-like Lists

Comandos:

```text
SB TOPLIST
UNSB TOPLIST
```

Uso TSIS:

- fuente candidata para descubrimiento de simbolos live;
- posible insumo del screener;
- no sustituye universe/market cap gobernado si DAS no provee ese campo con
  semantica certificada.

### 6. Daily Chart Bars

Comandos:

```text
SB <symbol> DAYCHART <start> <end>
UNSB <symbol> DAYCHART
```

Uso TSIS:

- contexto chart diario retornado por DAS;
- evidencia auxiliar, no reemplazo de Data Foundation historico.

### 7. Minute Chart Bars

Comandos:

```text
SB <symbol> MINCHART <start> <end> 1
UNSB <symbol> MINCHART
```

Uso TSIS:

- barras intradia/minuto desde DAS si disponibles;
- comparacion live-source contra Polygon/Data Foundation cuando proceda;
- no redefine `E:/TSIS/data/ohlcv_1m` ni quote-guarded historical truth.

### 8. Symbol Status / Short-side Data

Comandos:

```text
GET SHORTINFO <symbol>
GET LDLU <symbol>
GET SymStatus <symbol>
```

Familias esperadas:

- short info / shortable status si retorna;
- limit up / limit down;
- SSR/symbol status;
- restricciones por simbolo.

Uso TSIS:

- contexto operativo live;
- filtro/screener potencial;
- broker/source-specific hasta parity contract.

### 9. Account And Broker State Read-only

Comandos previstos:

```text
GET BP
GET AccountInfo
GET POSITIONS
GET ORDERS
GET TRADES
GET ROUTESTATUS
GET LOCATES
GET INTMSGS
```

Regla:

```text
account/broker telemetry is sensitive and not automatically model-facing
```

Uso TSIS:

- observabilidad operativa;
- futura ejecucion/risk bridge solo bajo contrato separado;
- redaction obligatoria cuando aplique.

### 10. Short Locate Read-only Queries

Comandos candidatos, disabled by default:

```text
SLPRICEINQUIRE <symbol> <shares> <route>
SLAvailQuery <account> <symbol>
SLReuseQuery <symbol|ALL>
SLRouteMinCharge <route|ALLROUTE>
```

Regla:

```text
locate read-only queries require locate_queries_enabled=true
```

Ordenes de locate siguen bloqueadas.

## Screener v0

El screener inicial debe cubrir:

```text
sessions = premarket, regular_market, afterhours
market_cap < 100,000,000 USD
0.50 <= price <= 20.00 USD
volume >= 300,000 shares
```

Fuente de volumen:

1. DAS Lv1 `V` si esta disponible;
2. suma de Time and Sales si la ventana capturada es completa;
3. `null/unavailable` si no se puede probar.

Fuente de market cap:

```text
governed_tsis_reference_or_universe_until_das_field_is_proven
```

Regla:

```text
missing data is not invented
```

Si falta market cap, price, volume o session, el candidato debe registrar la
razon de fallo/unavailability.

Outputs esperados:

```text
E:/TSIS/data_DAS_live/screener/runs/<run_id>/screener_manifest.json
E:/TSIS/data_DAS_live/screener/runs/<run_id>/candidates.jsonl
E:/TSIS/data_DAS_live/screener/runs/<run_id>/candidates.csv
```

## Source Parity Gate

Ningun campo de DAS entra directamente en ML/RL/features model-facing.

Cada campo debe clasificarse como:

- trainable historically and reproducible live;
- live-only;
- broker-only;
- operational telemetry;
- forbidden for model input;
- pending certification.

Lugar del trabajo:

```text
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps/01_data_ingestion_live/source_parity_audit/
```

## Seguridad Operativa

Default:

```text
read-only/data-only
```

Bloqueado en v0:

- ordenes;
- cancels;
- replaces;
- complex orders;
- locate orders;
- route actions;
- cambios de cuenta;
- credential storage;
- automatic login con secrets persistidos.

No se escribe en markdown/logs/JSONL/parquet metadata/screenshots:

- passwords;
- tokens;
- account ids;
- broker secrets;
- screenshots con datos de cuenta;
- transcripts sin redaction si contienen informacion sensible.

## Que Falta Para Validar Captura Real

PENDING antes de declarar smoke PASS productivo:

1. Ejecutar una sesion live real contra DAS en horario valido.
2. Confirmar que `LOGIN` queda redactado en `command_transcript.jsonl`.
3. Confirmar TOPLIST/Lv1 screener con candidatos reales.
4. Confirmar full capture para al menos un candidato PASS o simbolo controlado.
5. Revisar `events.jsonl` para Lv1, tms, Lv2 si entitlement existe, SHORTINFO, LDLU, SymStatus, DAYCHART y MINCHART.
6. Confirmar no-response/permission/login-required como evidencia, no como silencio.
7. Confirmar `Ctrl+C` cierra con unsubscribe, `QUIT`, heartbeat cerrado y `final_summary.json`.
8. Confirmar comportamiento de run incompleto si se corta la luz.
9. Documentar en este mapa cualquier campo DAS nuevo observado.
10. Mantener account/broker snapshot fuera del flujo por defecto salvo contrato sensible explicito.

## Comandos De Usuario Esperados

Live actual:

```powershell
$env:PYTHONPATH = "C:\TSIS_Data\02_TSIS_webSocket_SmallCaps\src"
python -m das_cmdapi.capture --config "C:\TSIS_Data\02_TSIS_webSocket_SmallCaps\configs\das_cmdapi_capture_v0_1.example.json"
```

Dry-run:

```powershell
$env:PYTHONPATH = "C:\TSIS_Data\02_TSIS_webSocket_SmallCaps\src"
python -m das_cmdapi.capture --dry-run --config "C:\TSIS_Data\02_TSIS_webSocket_SmallCaps\configs\das_cmdapi_capture_v0_1.example.json"
```

Monitor:

```powershell
$env:PYTHONPATH = "C:\TSIS_Data\02_TSIS_webSocket_SmallCaps\src"
python -m das_cmdapi.monitor "E:\TSIS\data_DAS_live\raw_cmdapi\runs\<run_id>"
```

