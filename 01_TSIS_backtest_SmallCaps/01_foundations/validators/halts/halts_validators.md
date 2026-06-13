# Halts Validators v0.1

## Scope

Este documento define los validadores institucionales minimos para `halts_v0_1`.

Gobierna:

- `E:\TSIS\data\Halts`

Raiz historica observada:

- `D:\Halts`

Existe un builder/runner de evidencia inspector moderno:

- `scripts/inspection/halts/build_halts_inspection_pack.py`

Este builder no reemplaza todos los validadores ejecutables futuros, pero ya emite outputs reproducibles para root audit, inventories, summaries, population visuals, case manifests y run manifest.

## Governed dataset

- Dataset contract: `01_foundations/contract_registry/dataset_contracts/halts_dataset_contract_v0_1.md`
- Registry: `01_foundations/dataset_registry/halts/halts_registry_entry.yaml`
- Consumption policy: `01_foundations/data_consumption_policies/halts_consumption_policy.md`
- Dossier: `01_foundations/inspection_dossiers/halts/halts_inspection_readout_v0_1.md`
- Run manifest: `01_foundations/inspection_dossiers/halts/evidence_assets/run_manifest.json`
- Schemas: `01_foundations/canonical_schemas/halts/`

## Unit of validation

Las unidades varian por subfamilia:

- raw Nasdaq/NYSE/SEC downloads: source row o raw document;
- source-specific outputs: source event row;
- master multisource: canonical event row;
- SEC suspensions: release/context row;
- coverage summary: `ticker`;
- visual overlay: `ticker + visual_date + event/window`;
- run artifacts: file-level provenance row.

## Required inputs

Inputs minimos:

- raiz fisica actual;
- processed master multisource;
- schemas canonicos;
- contrato de dataset;
- registry entry;
- policy de consumo;
- closeouts historicos;
- certification historica;
- cache historico si se reproduce evidencia;
- universe reference si el validator mide alcance `<1B>`;
- quotes/trades/minute artifacts si se valida coherencia de overlay.

## Validator families

### 1. Root and processed presence

Debe comprobar:

- existe `E:\TSIS\data\Halts`;
- existen subroots raw y processed;
- existen parquets/csv processed esperados;
- root actual y legacy no se contradicen sin nota;
- no se escribe en roots protegidas durante validacion.

Hard failure:

- raiz canonica ausente;
- processed master ausente;
- root audit no puede leer huella minima;
- escritura detectada en roots raw/protegidas durante el run.

### 2. Source allowlist and provenance

Debe comprobar:

- `source` pertenece a `nasdaq`, `nyse` o `sec`;
- `source_priority` es consistente con la fuente;
- Nasdaq/NYSE conservan link o contexto de fuente cuando existe;
- SEC conserva `release_no`, `item_link` y flag `is_sec_suspension`.

Hard failure:

- source fuera de allowlist;
- SEC sin identificador de release/link cuando se usa como evidencia;
- source row sin provenance suficiente para reproducibilidad.

### 3. Schema conformity

Debe comprobar columnas requeridas del master:

- `source`;
- `source_priority`;
- `ticker`;
- `issuer_name`;
- `listing_exchange`;
- `halt_date`;
- `halt_start_et`;
- `resume_quote_et`;
- `resume_trade_et`;
- `halt_code`;
- `halt_type`;
- `raw_reason`;
- `release_no`;
- `item_link`;
- `url_source`;
- `is_sec_suspension`.

Hard failure:

- columna clave ausente;
- tipo incompatible que impide parsear fecha/hora;
- `halt_date` no parseable en evento operativo;
- `source` nulo.

Review:

- campos intradia nulos en SEC/context;
- issuer/ticker parcial;
- `resume_quote_et` o `resume_trade_et` ausentes en evento que aun puede ser date-level.

### 4. Event identity and time semantics

Debe comprobar:

- `halt_date` parseable;
- `halt_start_et`, `resume_quote_et`, `resume_trade_et` parseables cuando existen;
- horas expresadas como Eastern Time;
- `resume_trade_et` no contradice `halt_start_et` sin flag;
- keys exactas y semanticas deduplican de forma trazable.

Hard failure:

- evento intradia sin fecha parseable;
- timestamp imposible sin marca de review;
- deduplicacion no reproducible.

Review:

- evento date-level sin ventana intradia;
- partial identity;
- regulatory context only;
- missing resume fields.

### 5. Multisource reconciliation

Debe comprobar:

- filas pre/post builder por fuente;
- delta de dedup por fuente;
- concat multisource contra persisted master;
- razon de cualquier diferencia.

Referencia poblacional actual:

- Nasdaq: `119630 -> 118594`, delta `1036`;
- NYSE: `13178 -> 13178`, delta `0`;
- SEC: `1346 -> 1346`, delta `0`;
- all sources concat: `134154 -> 133118`, delta `1036`;
- persisted multisource parquet: `133116`.

Hard failure:

- delta no explicado;
- persisted master no trazable a source-specific outputs.

### 6. Event taxonomy validation

Debe comprobar:

- estados permitidos;
- conteos coherentes;
- separacion good/review/bad;
- ninguna policy convierte review en good por defecto.

Estados permitidos:

- `good_full_intraday_event`
- `good_date_level_event`
- `review_partial_identity`
- `regulatory_context_only`
- `bad_unusable_event`

Hard failure:

- estado fuera de vocabulario sin versionado;
- `bad_unusable_event` entra a consumidores operativos;
- `regulatory_context_only` se trata como ventana intradia.

### 7. LT1B coverage validation

Debe comprobar:

- universe ticker count;
- tickers con y sin eventos matcheados;
- total de eventos ligados al universo;
- interpretacion correcta de ausencia.

Referencia poblacional actual:

- universe tickers: `4824`;
- tickers with halt data: `3912`;
- tickers without halt data: `912`;
- halt events total for universe: `53909`.

Hard failure:

- interpretar `tickers_without_halt_data` como missing coverage sin evidencia;
- usar coverage como universe membership final.

### 8. Visual overlay validation

Debe comprobar:

- cada visual bucket tiene descripcion;
- cada imagen o panel relevante declara que muestra, responde, no responde y consecuencia;
- los buckets de review no se promocionan a good sin lectura;
- quotes/trades signals no sustituyen evento oficial.

Buckets gobernados:

- `confirmed_halt_microstructure_coherent`
- `halt_with_trades_signal_only`
- `halt_with_quotes_signal_only`
- `halt_present_but_market_clean`
- `market_signal_without_clear_halt_window`

Hard failure:

- declarar causalidad solo por proximidad temporal;
- usar senal de mercado sin halt oficial como evento confirmado;
- usar visuales mudos sin lectura interpretativa.

## Hard failures

Hard failures minimos:

- root canonico ausente;
- processed master ausente;
- source fuera de allowlist;
- columna clave ausente;
- fecha principal no parseable;
- source/provenance irrecuperable;
- estado de taxonomia fuera de vocabulario;
- `bad_unusable_event` consumido como operativo;
- SEC/date-level usado como intraday window;
- escritura en roots protegidas durante auditoria;
- evidencia visual usada sin interpretacion.

## Review/recoverable states

Review states:

- `review_partial_identity`
- `regulatory_context_only`
- `halt_with_trades_signal_only`
- `halt_with_quotes_signal_only`
- `halt_present_but_market_clean`
- `market_signal_without_clear_halt_window`

Recoverable states:

- date-level event para contexto diario;
- missing resume fields cuando policy restringe uso;
- SEC context cuando se conserva como contexto regulatorio;
- legacy root path si registry declara root actual;
- raw residual rows preservadas como bad/forensic only.

## Output fields

Un validator ejecutable futuro debe emitir, como minimo:

- `run_id`
- `validated_at_utc`
- `dataset_id`
- `source_root`
- `unit_type`
- `units_checked`
- `rows_checked`
- `files_checked`
- `source`
- `event_taxonomy`
- `visual_case_bucket`
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
- lista o manifest de casos afectados;
- enlace a closeout o dossier;
- root audit reproducible;
- y, si el claim es causal contra market data, evidencia visual o tabular suficiente.

## Pass criteria

El bloque puede mantener estado institucional si:

- raiz y processed master existen;
- schemas minimos son verificables;
- source allowlist se respeta;
- no hay hard failures agregados sin explicar;
- review states quedan separados de good;
- SEC/context no se trata como intradia;
- no se habilitan consumidores no declarados;
- y toda conclusion causal conserva evidencia o link a evidencia historica.

## Non-goals

Este validador no prueba:

- calidad de quotes/trades/daily/minute;
- execution feasibility;
- alpha;
- ausencia global de eventos no capturados;
- universe membership final;
- ni continuidad corporativa.

## Promotion implications

Para promover `halts` a consumidores mas sensibles se seguira necesitando:

- runner ejecutable especifico por consumidor;
- contrato de temporal availability;
- update de registry;
- update de policy;
- dossier actualizado;
- changelog.

## Regla final

`halts` se valida por fuente, evento, temporalidad y uso.

No existe un pass unico que autorice todos los consumidores.
