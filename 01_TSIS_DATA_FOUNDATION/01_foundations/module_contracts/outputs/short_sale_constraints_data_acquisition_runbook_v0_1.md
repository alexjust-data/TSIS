# Short Sale Constraints Data Acquisition Runbook v0.1

## Estado

Tipo: acquisition runbook / promotion preparation.

Modulo: `01_TSIS_DATA_FOUNDATION`.

Ambito: `CAPA 1 - DATA FOUNDATION`.

Tabla objetivo:

```text
short_sale_constraints_table_v0_1
```

Contrato principal:

```text
01_foundations/module_contracts/outputs/short_sale_constraints_table_target_contract_v0_1.md
```

Status:

```text
source_acquisition_prepared_not_connected
materialized = false
das_api_connected = false
historical_borrow_locate_source_acquired = false
```

## Regla Central

TSIS tiene historico de mercado de muchos anos.

Eso no significa que TSIS tenga historico de borrow, locate o availability.

```text
20 years of market data
!=
20 years of broker-specific borrow inventory
```

La data de mercado permite reconstruir o aproximar:

- precios;
- volumen;
- barras;
- quotes;
- trades;
- eventos observables;
- SSR proxy regulatorio si existe precio intradia suficiente.

La data de mercado no permite reconstruir por si sola:

- shares available to short en un broker concreto;
- hard-to-borrow / easy-to-borrow real en una cuenta concreta;
- locate request;
- locate approval;
- borrow fee;
- rebate;
- rechazos operativos del broker;
- inventario prestable interno.

Por tanto, ningun agente puede afirmar que existen 20 anos de
`borrow/locate/availability` salvo que exista una fuente historica
broker/vendor con semantica point-in-time.

## Separacion De Carriles

Este runbook prepara tres carriles distintos.

### Carril A - SSR Historico Derivado

Objetivo:

```text
Reconstruir SSR historico como derived_regulatory_proxy.
```

Fuente posible:

```text
master_daily_table / daily raw validado
master_intraday_bar_table / ohlcv_1m raw validado
market_calendar
instrument_master
```

Uso:

- saber si la regla SSR habria estado activa;
- filtrar o degradar short entries;
- construir estado regulatorio historico;
- comparar contra listas oficiales/vendor cuando existan.

Limitacion:

```text
SSR proxy no prueba borrow ni locate.
```

Nivel de confianza esperado:

```text
source_level = derived_regulatory_proxy
confirmed_by_official_or_vendor_feed = false
```

### Carril B - DAS / SageTrader Live Capture

Objetivo:

```text
Capturar desde ahora hacia adelante cualquier dato shortable/locate/borrow
que la plataforma, broker o API exponga.
```

Este carril no reconstruye historico pasado. Empieza en el momento en que la
captura queda operativa y auditada.

Fuentes candidatas:

```text
DAS Trader Pro API
SageTrader/DAS integration
broker export
broker order/locate logs
execution reject logs
manual or automated broker reports
```

Regla:

```text
DAS/SageTrader no se trata como fuente confirmada hasta tener documentacion
oficial, entitlement activo o muestra raw capturada.
```

Campos minimos que debe exponer o permitir reconstruir:

```text
source_system
broker_or_vendor
account_scope
ticker
instrument_id
as_of_utc
received_utc
ingested_utc
source_channel
shares_available_to_short
availability_status
easy_to_borrow_flag
hard_to_borrow_flag
locate_required
locate_requested
locate_approved
locate_approved_shares
locate_request_id
borrow_fee_rate
rebate_rate
raw_status_text
source_event_id
latency_ms
quality_state
```

Si DAS/API solo muestra un estado visual o textual, el adapter debe preservar
el texto bruto:

```text
raw_status_text = <exact broker/platform status>
parsed_status = <normalized TSIS interpretation>
parse_confidence = exact | inferred | ambiguous
```

### Carril C - Historico Broker/Vendor

Objetivo:

```text
Incorporar historico real de borrow/locate/availability si se compra,
descarga o recibe de broker/vendor.
```

Este carril solo es valido si la fuente incluye semantica temporal suficiente.

Metadata minima obligatoria:

```text
vendor_or_broker_name
delivery_date
coverage_start_date
coverage_end_date
coverage_frequency
timestamp_semantics
timezone
account_scope
symbol_mapping_policy
raw_file_hash
license_or_usage_scope
known_gaps
known_transformations
```

Frecuencias permitidas y uso:

```text
intraday_point_in_time
  -> puede alimentar execution feasibility si received/as_of <= event_time.

daily_open_snapshot
  -> puede alimentar contexto diario y pre-check de sesion, con staleness.

daily_end_of_day
  -> no puede validar ejecucion intradia anterior; solo contexto retrospectivo.

monthly_or_periodic_summary
  -> no puede usarse como execution gate; solo contexto amplio.
```

Regla:

```text
Un historico sin as_of/received semantics no es execution truth.
```

## Rutas Objetivo

No crear estas rutas como source of truth hasta que exista fuente real,
manifest y owner.

Rutas staging recomendadas cuando exista fuente:

```text
E:/TSIS/data/short_sale_constraints_raw/ssr_official/
E:/TSIS/data/short_sale_constraints_raw/ssr_derived_proxy/
E:/TSIS/data/short_sale_constraints_raw/das_live/
E:/TSIS/data/short_sale_constraints_raw/broker_historical/
E:/TSIS/data/short_sale_constraints_raw/vendor_historical/
```

Ruta de output gobernado:

```text
E:/TSIS/data/data_foundation_outputs/short_sale_constraints_table/
```

Regla:

```text
raw capture append-only primero;
tabla normalizada despues;
promocion solo despues de manifest, validators y evidencia.
```

## Contrato De Raw Capture DAS

Cuando se conecte DAS/SageTrader, el primer objetivo no es producir la tabla
final. El primer objetivo es capturar raw.

### Captura Minima

Cada observacion debe guardar:

```text
capture_run_id
source_system = das_trader_pro | sagetrader_das | broker_export | other
source_channel = api | file_export | screen_capture | order_log | reject_log
broker_or_vendor
account_scope
host_clock_utc
received_utc
raw_payload
raw_payload_hash
parser_version
ingested_utc
operator_or_process
```

### Preguntas Que Debe Resolver La Prueba DAS

Antes de construir el adapter institucional hay que contestar:

- expone shortable status por ticker?
- expone shares available to short?
- expone borrow fee o rebate?
- expone HTB/ETB?
- permite solicitar locate desde API?
- devuelve locate approval/reject con id?
- la disponibilidad es por cuenta, broker o ruta?
- hay timestamps de origen o solo timestamp local de recepcion?
- hay rate limits?
- hay cambios intradia o solo snapshots?
- permite replay/backfill o solo estado actual?

Si alguna respuesta queda desconocida, el campo correspondiente debe marcarse:

```text
unknown_not_exposed
```

No se permite rellenarlo por inferencia desde short volume, price action,
quotes, trades o intuicion operativa.

## Contrato De Historico Broker/Vendor

Cuando llegue una fuente historica, antes de materializar hay que crear:

```text
source_intake_manifest.json
source_field_map.md
coverage_report.md
sample_raw_payloads/
normalization_notes.md
quality_report.md
```

El manifest debe responder:

- que proveedor/broker entrego la data;
- que periodo cubre;
- que tickers cubre;
- si incluye delisted/inactive;
- si el ticker mapping es historico o current-only;
- si los timestamps son exchange time, broker time o vendor processing time;
- si son snapshots, eventos o logs de solicitudes;
- si hay account scope;
- si hay fees;
- si hay locates reales o solo availability;
- si los datos pueden usarse para backtesting o solo para contexto.

## Validacion Minima

### Para SSR Proxy

Checks minimos:

- prior close existe y usa price view declarada;
- intraday price source cubre regular session;
- trigger del 10% se calcula con timezone y session declarados;
- active window incluye resto de dia y siguiente sesion segun regla vigente;
- casos muestrales comparados contra fuente oficial/vendor cuando exista;
- discrepancias quedan en `review`, no se silencian.

### Para DAS Live

Checks minimos:

- raw payload se conserva append-only;
- todos los eventos tienen `received_utc`;
- todos los eventos tienen `broker_or_vendor`;
- todos los eventos tienen `account_scope` o `account_scope=unknown`;
- parsing no destruye `raw_status_text`;
- observaciones posteriores al evento no pueden alimentar features as-of;
- cambios de availability tienen secuencia temporal monotona por fuente;
- logs de reject/locate se enlazan por `source_event_id` cuando exista.

### Para Historico Vendor/Broker

Checks minimos:

- cobertura declarada vs cobertura fisica;
- duplicados por grain;
- timestamps parseables;
- timezone normalizado;
- symbol mapping contra `instrument_master`;
- staleness por observacion;
- filas sin account/broker scope degradadas;
- EOD snapshots prohibidos como prueba de intraday execution;
- raw hash reproducible.

## Semantica Para Backtesting

El backtester debe distinguir:

```text
theoretical_short_possible
regulatory_short_allowed
broker_short_executable
```

Definicion:

```text
theoretical_short_possible
  = el mercado tuvo precio/liquidez observable suficiente bajo el simulador.

regulatory_short_allowed
  = SSR/regla aplicable no bloquea la orden propuesta o exige ajuste.

broker_short_executable
  = antes del cutoff habia borrow/locate/availability valida para el broker,
    cuenta y cantidad simulada.
```

Si solo existe SSR proxy:

```text
broker_short_executable = unknown
```

Si existe DAS live desde una fecha futura:

```text
broker_short_executable puede evaluarse solo desde la primera fecha con captura.
```

Si existe historico vendor diario EOD:

```text
broker_short_executable intradia = not_proven
```

## Semantica Para ML/RL

`short_sale_constraints_table` puede alimentar market state solo si:

- la observacion es legal as-of;
- no incorpora availability posterior al evento;
- declara broker/account scope;
- declara staleness;
- separa constraints de labels/outcomes;
- no usa rejects futuros como feature previa;
- preserva unknowns en lugar de imputar shortability.

Uso prohibido:

```text
borrow_available_after_event -> feature_before_event
locate_reject_after_order -> pre-entry state
EOD availability -> intraday executable proof
```

## Promotion Checklist

Para pasar de `source_acquisition_prepared_not_connected` a
`materialization_candidate`, deben existir:

```text
1. fuente raw real o proxy SSR declarado;
2. manifest de fuente;
3. schema de raw capture;
4. field map al contrato objetivo;
5. sample raw payloads o sample files;
6. coverage report;
7. validators;
8. tests;
9. consumption policy;
10. dataset registry entry;
11. changelog;
12. Graphify refresh queue entry.
```

Para pasar a `validated_for_declared_scope`:

```text
1. output materializado;
2. manifest con run_id;
3. hashes de output;
4. test run evidence;
5. casos forenses good/review/bad;
6. limitaciones explicitas por fuente;
7. reglas de consumo downstream actualizadas.
```

## Decisiones TSIS

| Decision TSIS | Evidencia directa | Obligacion tecnica | Limitacion abierta |
| --- | --- | --- | --- |
| Separar `short_context_table` de `short_sale_constraints_table`. | `short_context_table` contiene short interest/volume; el contrato de constraints requiere SSR, borrow, locate y broker scope. | No inferir borrow/locate desde short interest o short volume. | Falta fuente broker/vendor para materializar constraints. |
| Reconstruir SSR historico como proxy cuando no haya lista oficial historica. | SEC Rule 201 define trigger por caida de 10% y efecto regulatorio. | Declarar `derived_regulatory_proxy`, price view, session, timezone y validacion. | Puede faltar exactitud si la fuente intradia no observa el trigger real. |
| Capturar DAS/live como raw append-only antes de normalizar. | TSIS exige reproducibilidad, raw hash y as-of legality para ejecucion. | Guardar payload bruto, timestamps y parser version. | DAS/API puede no exponer todos los campos requeridos. |
| Tratar historico vendor segun frecuencia. | Execution feasibility requiere observabilidad antes del evento. | Separar intraday point-in-time, daily open, EOD y summaries. | Fuentes historicas pueden ser demasiado agregadas para ejecucion intradia. |

## Referencias

SEC Regulation SHO / Rule 201:

```text
https://www.sec.gov/rules/final/2010/34-61595.pdf
```

17 CFR 242.201:

```text
https://www.ecfr.gov/current/title-17/chapter-II/part-242/section-242.201
```

17 CFR 242.203 locate requirement:

```text
https://www.ecfr.gov/current/title-17/chapter-II/part-242/section-242.203
```

Contratos TSIS relacionados:

```text
01_foundations/module_contracts/outputs/short_sale_constraints_table_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
```

## Regla Final

Hasta que exista fuente real:

```text
TSIS puede preparar la arquitectura.
TSIS puede derivar SSR proxy con validacion.
TSIS puede capturar DAS/live desde el primer dia conectado.
TSIS no puede afirmar historico broker-specific de borrow/locate/availability.
```

