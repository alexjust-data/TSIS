# Reference Validators v0.1

## Scope

Este documento define los validadores institucionales minimos para `reference_v0_1`.

Gobierna:

- `E:\TSIS\data\reference`

Existe un builder/runner de evidencia inspector moderno:

- `scripts/inspection/reference/build_reference_inspection_pack.py`

Este builder no reemplaza todos los validadores semanticos futuros, pero ya emite outputs reproducibles para root audit, inventories, summaries, visuals, case manifests y run manifest.

## Governed dataset

- Dataset contract: `01_foundations/contract_registry/dataset_contracts/reference_dataset_contract_v0_1.md`
- Registry: `01_foundations/dataset_registry/reference/reference_registry_entry.yaml`
- Consumption policy: `01_foundations/data_consumption_policies/reference_consumption_policy.md`
- Dossier: `01_foundations/inspection_dossiers/reference/reference_inspection_readout_v0_2.md`
- Run manifest: `01_foundations/inspection_dossiers/reference/evidence_assets/run_manifest.json`
- Schemas: `01_foundations/canonical_schemas/reference/`

## Unit of validation

Las unidades varian por subfamilia:

- `all_tickers`: `snapshot_date + ticker`
- `overview`: `ticker + request_date`
- `events`: payload `ticker`, y evento interno explotado
- `splits`: `ticker + id` o `ticker + execution_date + split_from + split_to`
- `dividends`: `ticker + id` o `ticker + ex_dividend_date + cash_amount + dividend_type`
- `exchanges`: `id`
- `ticker_types`: `code`
- `_run`: row operacional de audit/error/progress

## Required inputs

Inputs minimos:

- raiz fisica actual;
- schemas canonicos;
- contrato de dataset;
- registry entry;
- policy de consumo;
- closeouts historicos;
- universe reference si el validator mide alcance `<1B>`;
- price-view contracts si valida splits/dividends para adjusted.

## Validator families

### 1. Root and subfamily presence

Debe comprobar:

- existe la raiz `E:\TSIS\data\reference`;
- existen subfamilias esperadas;
- `_run`, `exchanges` y `ticker_types` tienen files globales;
- subfamilias por ticker tienen particiones esperadas.

Hard failure:

- raiz ausente;
- subfamilia requerida ausente sin nota de deprecacion.

### 2. Schema conformity

Debe comprobar:

- columnas requeridas por subfamilia;
- `_dataset`;
- `_ingested_utc`;
- parseabilidad de fechas;
- sentinel forms validos para files sin payload.

Hard failure:

- columna clave ausente en payload;
- `_dataset` incompatible;
- fecha principal no parseable en payload;
- sentinel form contado como business row.

### 3. Identity checks

Debe comprobar:

- ticker no nulo;
- ticker fisico compatible con particion cuando aplica;
- duplicados de claves logicas;
- tipos de instrumento conocidos;
- presencia de identificadores como `cik`, `composite_figi`, `share_class_figi` cuando existan.

Review:

- transient symbols;
- instrument type ambiguity;
- identity payload incompleto;
- ticker/root mismatch explicable.

### 4. Corporate action checks

Splits:

- `split_from > 0`;
- `split_to > 0`;
- `execution_date` parseable;
- ratio no nulo;
- no duplicado duro de evento.

Dividends:

- `cash_amount >= 0`;
- `ex_dividend_date` parseable;
- `dividend_type` declarado;
- `currency` parseable;
- cola no `CD` marcada para review.

Hard failure:

- ratio split no positivo;
- cash amount negativo;
- fecha principal no parseable.

Review:

- `dividend_type != CD`;
- ratio inusual;
- evento cercano a market anomaly sin confirmacion.

### 5. Events checks

Debe comprobar:

- payload `events` parseable;
- cada evento tiene `date` y `type`;
- `type = ticker_change` tiene `ticker_change.ticker`;
- eventos internos pueden explotarse a grano evento.

Hard failure:

- evento sin `type`;
- ticker_change sin ticker destino.

Review:

- continuidad economica no demostrada;
- ticker_change cercano a quotes anomaly;
- ticker_change cercano a halt sin evidencia visual coherente.

### 6. Operational artifacts

Debe comprobar:

- audit CSV parseable;
- errors CSV parseable;
- progress JSON parseable;
- `out_file` trazable;
- `status` no nulo.

Hard failure:

- artifacts operacionales corruptos si se usan para reproducibilidad.

No debe concluir:

- calidad semantica de reference solo por progreso de descarga.

### 7. Cross-dataset evidence checks

Cuando el validador mida causalidad:

- `splits -> trades`;
- `events -> halts`;
- `events -> quotes`;
- `identity -> trades`;

debe separar:

- proximidad temporal;
- evidencia visual;
- causalidad fuerte;
- detector review;
- no-link/coverage limit.

Hard failure:

- declarar `good` causal solo por proximidad temporal.

Review:

- anomaly detection sin explicacion visual limpia.

## Hard failures

Hard failures minimos:

- root/subfamily missing sin justificacion;
- required key missing;
- principal date unparseable;
- nonpositive split ratio components;
- negative dividend cash amount;
- ticker_change event without target ticker;
- global table duplicate primary key;
- operational artifact unreadable when used as evidence;
- event payload cannot be parsed but is needed for a consumer.

## Review/recoverable states

Review states:

- `review_transient_symbol`
- `review_instrument_type_ambiguity`
- `review_no_split_payload`
- `split_near_scale_mismatch_review`
- `ticker_change_near_quotes_anomaly`
- `reference_event_near_halt_review`
- `reference_event_near_quotes_review`
- `identity_review_residual`

Recoverable states:

- valid sentinel no-payload file;
- missing optional metadata;
- legacy root path in old schema examples when registry declares current root;
- operational download error preserved as provenance but not consumed as market data.

## Output fields

Un validator ejecutable futuro debe emitir, como minimo:

- `run_id`
- `validated_at_utc`
- `dataset_id`
- `source_root`
- `subfamily`
- `unit_type`
- `units_checked`
- `rows_checked`
- `files_checked`
- `hard_fail_count`
- `review_count`
- `good_count`
- `reason_code`
- `evidence_path`
- `schema_contract`
- `dataset_contract`
- `policy`
- `registry_entry`

## Evidence requirements

Para cerrar o cambiar estados debe existir:

- tabla resumen;
- lista de casos afectados;
- enlace a closeout o dossier;
- y, si el claim es causal, evidencia visual o tabular suficiente.

## Pass criteria

El bloque puede mantener estado institucional si:

- raiz y subfamilias esperadas existen;
- schemas minimos son verificables;
- no hay hard failures agregados sin explicar;
- review states quedan separados de good;
- no se habilitan consumidores no declarados;
- y toda conclusion causal conserva evidencia o link a evidencia historica.

## Non-goals

Este validador no prueba:

- continuidad economica total;
- universo final diario PTI;
- que un evento sea alpha;
- calidad de quotes/trades/daily;
- ni que una price view derivada este promovida por si sola.

## Promotion implications

Para promover `reference` a consumidores mas sensibles se seguira necesitando:

- runner ejecutable versionado especifico del consumidor sensible;
- output reproducible;
- update de registry;
- update de policy;
- dossier actualizado;
- changelog.

## Regla final

`reference` se valida por subfamilia y por uso.

No existe un pass unico que autorice todos los consumidores.
