# Reference Institutional Closeout v0.1

Estado actualizado 2026-06-13:

Este closeout v0.1 queda como antecedente institucional compacto.

La paridad inspectora moderna para el alcance `foundation_promotion` queda cerrada en:

- `reference_inspection_readout_v0_2.md`
- `build_reference_inspection_pack.md`
- `reference_casepacks_traceability_audit_v0_1.md`
- `integration_notes.md`
- `evidence_assets/run_manifest.json`

## 1. Rol

Este dossier traduce la auditoria historica de `reference` a una lectura institucional moderna dentro de `01_foundations`.

No reescribe la evidencia historica.
No mueve caches.
No sustituye los notebooks o closeouts preservados.

Su funcion es responder:

- que se cerro;
- que evidencia sostiene el cierre;
- que estados gobiernan consumo;
- que queda abierto;
- y como debe leerse `reference` dentro del sistema actual.

## 2. Fuentes de evidencia

Auditoria preservada:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/04_reference_closeout.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/04_reference_causal_overlay_closeout.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/03_reference_root_cause_audit_phase1_closeout.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/cache_v2/`

Contratos modernos relacionados:

- `01_foundations/contract_registry/dataset_contracts/reference_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/reference_consumption_policy.md`
- `01_foundations/dataset_registry/reference/reference_registry_entry.yaml`
- `01_foundations/validators/reference/reference_validators.md`
- `01_foundations/canonical_schemas/reference/`

## 3. Veredicto

`reference` queda aceptado como capa fundacional institucional.

El bloque es utilizable para:

- identidad;
- snapshots de ticker;
- tipos de instrumento;
- corporate actions;
- eventos de continuidad;
- overlays causales;
- price view construction;
- universe support;
- auditoria forense.

No queda aceptado como:

- precio;
- execution tape;
- feature productiva por defecto;
- continuidad economica completa;
- universe membership final;
- ni fuente de alpha sin contrato posterior.

## 4. Que muestra la auditoria historica

### Estructura

La auditoria historica deja cerradas estas familias:

- `overview`
- `all_tickers`
- `events`
- `splits`
- `dividends`

Tambien existen schemas modernos para:

- `exchanges`
- `ticker_types`
- `_run`

### Causalidad

La fase causal ya probo que `reference` no es solo metadata estatica.

Frentes principales:

- `splits -> trades`
- `splits -> daily / ohlcv_1m`
- `events/ticker_change -> halts`
- `events/ticker_change -> quotes`
- `identity review -> trades sample`

## 5. Lectura por frente causal

### `splits -> trades`

Resultado historico:

- `split_explains_trade_scale_mismatch`: `9`
- `split_near_scale_mismatch_review`: `13`

Que muestra:

- los splits explican un subconjunto pequeno pero real de `scale_suspect` en `trades`.

Responde:

- si `reference/splits` puede explicar casos concretos de mismatch de escala.

No responde:

- si todos los residuos de `trades` se explican por splits.

Consecuencia:

- `split_explains_trade_scale_mismatch` puede tratarse como `good` explicativo;
- `split_near_scale_mismatch_review` debe seguir en review.

### `splits -> daily / 1m`

Resultado historico:

- `daily_split_ratio_review`: `1`
- `review_no_daily_alignment`: `21`
- `m1_split_ratio_review`: `1`
- `review_no_1m_alignment`: `21`

Que muestra:

- la explicacion por split aparece fuerte en trades, pero no replica limpiamente en raw daily o raw 1m para la mayoria de casos enlazados.

Responde:

- si el mismo split explica de forma uniforme todas las capas raw.

No responde:

- si la capa derivada `split_normalized` esta mal; esa pregunta ya vive en su propio dossier.

Consecuencia:

- mantener lectura estricta: split explica casos concretos, no todos los desacoples entre capas.

### `events/ticker_change -> halts`

Resultado historico:

- `ticker_change_near_halt`: `775`
- `reference_event_near_halt_review`: `173`
- `same_day`: `355`
- `near_3d`: `420`
- `near_30d`: `173`

Que muestra:

- `ticker_change` se alinea materialmente con eventos halt.

Responde:

- si `reference/events` aporta contexto real sobre episodios de mercado.

No responde:

- si cada ticker change implica causalidad economica cerrada.

Consecuencia:

- `ticker_change_near_halt` puede ser `good` cuando el halt y la reaccion de mercado son visualmente coherentes;
- el resto queda en `review`.

### `events/ticker_change -> quotes`

Resultado historico:

- `ticker_change_near_quotes_anomaly`: `2330`
- `reference_event_near_quotes_review`: `247`
- `reference_event_near_quotes_clean`: `18`
- dentro del bloque fuerte: `HARD_FAIL = 431`, `SOFT_FAIL = 1899`, `PASS = 0`

Que muestra:

- los ticker changes conviven masivamente con anomalias en `quotes`.

Responde:

- si `reference` ayuda a detectar zonas fragiles del libro.

No responde:

- si el ticker change explica limpiamente cada anomalia.

Consecuencia:

- `ticker_change_near_quotes_anomaly` es detector fuerte y debe permanecer `review`;
- no debe consumirse como `good` ni como alpha sin contrato posterior.

### `identity review -> trades`

Resultado historico:

- `identity_review_without_trades_link`: `746`
- `identity_review_linked_to_scale_mismatch`: `2`
- `identity_review_linked_to_other_trades_case`: `2`

Que muestra:

- el residuo de identidad no emerge como explicador dominante de los casos de `trades` revisados.

Responde:

- si la primera capa causal de identidad explica mucho tape stress.

No responde:

- si identity es irrelevante estructuralmente.

Consecuencia:

- mantener identity review como frontera estructural, no sobredimensionarla como causa dominante de `trades`.

## 6. Politica de estados

### `good`

- `good_identity_snapshot`
- `good_split_event`
- `split_explains_trade_scale_mismatch`
- `ticker_change_near_halt` cuando el mercado es coherente

### `review`

- `review_transient_symbol`
- `review_instrument_type_ambiguity`
- `review_no_split_payload`
- `split_near_scale_mismatch_review`
- `ticker_change_near_quotes_anomaly`
- `reference_event_near_halt_review`
- `reference_event_near_quotes_review`
- `identity_review_residual`

### `bad`

- `bad_unresolved_identity`

No aparece una familia agregada `bad` dominante en el overlay de mercado.

## 7. Decision de consumo

Permitido:

- construir price views con splits/dividends;
- apoyar universe builder;
- explicar auditorias de `quotes`, `trades`, `daily`, `1m` y `halts`;
- alimentar event overlays;
- filtrar tipos de instrumento;
- usar como forensic/research evidence.

Restringido:

- backtest event-driven;
- ML;
- execution simulation;
- live;
- RL.

Bloqueado sin contrato:

- usar ticker changes como alpha;
- usar overview market cap como membership diaria PTI;
- usar all_tickers como universe final;
- usar eventos futuros sin control de disponibilidad temporal.

## 8. Limitaciones abiertas

- continuidad economica por `ticker_change`;
- transient symbols;
- ambiguity de instrument type;
- eventos cerca de quotes anomalies sin causalidad visual limpia;
- extension futura de adjusted a corporate actions complejas;
- posible remap service futuro.

## 9. Criterio de cierre

`reference` cumple el criterio de promocion foundation minima porque existen y se mantienen enlazados:

- dataset contract;
- registry entry;
- consumption policy;
- validators contract;
- canonical schemas;
- este closeout compacto;
- evidencia historica preservada.

Ese criterio ya no debe confundirse con el estado vigente del dossier.

La promocion moderna posterior anadio:

- README local actualizado;
- builder/script reproducible;
- evidence assets activos bajo `01_foundations`;
- mapa poblacional visual;
- manifests versionados;
- casepacks por familia;
- readout v0.2 con evidencia general-a-particular;
- auditoria de trazabilidad de casepacks;
- absorcion explicita de `certification/reference`.

La auditoria de gap que motivo ese upgrade vive en:

- `reference_modernization_gap_audit_2026-06-12.md`
## 10. Regla final

`reference` debe leerse como capa semantica upstream.

Su valor operativo aparece cuando impide tres errores:

1. tratar todos los tickers como common stock continuo;
2. tratar corporate actions como alpha o corrupcion;
3. interpretar microestructura sin contexto de eventos e identidad.
