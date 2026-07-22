# 1m Split-Normalized Inspection Dossier

Fecha de referencia: 2026-06-07.

## Rol

Esta carpeta gobierna la inspeccion de `ohlcv_1m_split_normalized_v0_1`.

No gobierna:

- `ohlcv_1m_raw`;
- `daily_adjusted`;
- una capa `1m_adjusted` economica completa;
- ni una materializacion fisica full-universe de todos los ticker-month.

La pregunta central es:

```text
La vista split-normalized reescala correctamente las observaciones intradia anteriores a splits futuros,
deja neutro el tramo posterior, y evita que consumidores cross-session aprendan saltos mecanicos como alpha?
```

## Autoridad Documental

Documentos contractuales:

- `01_foundations/contract_registry/dataset_contracts/ohlcv_1m_split_normalized_dataset_contract_v0_1.md`
- `01_foundations/canonical_schemas/ohlcv_1m/ohlcv_1m_split_normalized_schema_contract.md`
- `01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_registry_entry.yaml`
- `01_foundations/module_contracts/ohlcv_1m_split_normalized_operational_landing_v0_1.md`
- `01_foundations/module_contracts/ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md`
- `01_foundations/module_contracts/ohlcv_1m_split_normalized_semantic_pilot_v0_1.md`
- `01_foundations/module_contracts/ohlcv_1m_split_normalized_pilot_results_v0_1.md`

Documentos transversales:

- `01_foundations/module_contracts/inspection_dossier_model.md`
- `01_foundations/module_contracts/evidence_model.md`
- `01_foundations/module_contracts/layer_validation_standard_v0_1.md`
- `01_foundations/module_contracts/foundations_transversal_final_review_v0_2.md`

Consumidor minimo:

- `01_foundations/module_contracts/intraday_regime_features_consumer_contract_v0_1.md`
- `01_foundations/module_contracts/intraday_regime_features_semantic_pilot_results_v0_1.md`
- `01_foundations/inspection_dossiers/intraday_regime_features/intraday_regime_features_semantic_pilot_readout_v0_1.md`

## Frontera Conceptual

Hay dos frases que deben mantenerse separadas:

```text
Los eventos de split auditables del universo 1m pasan los invariantes semanticos sin fallos observados.
```

No es lo mismo que:

```text
La capa fisica ohlcv_1m_split_normalized esta materializada full-universe para todos los ticker-month.
```

Estado correcto:

- auditoria full-universe de eventos split auditables: cerrada con `FAIL = 0`;
- materializacion fisica full-universe de la vista derivada: no promovida en esta carpeta;
- uso permitido: comparabilidad cross-session alrededor de splits;
- uso prohibido: sustituir `1m raw` como verdad local de ejecucion.

## Estructura

```text
inspection_dossiers/1m_split_normalized/
  README.md
  ohlcv_1m_split_normalized_pilot_readout_v0_1.md
  ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1.md
  ohlcv_1m_split_normalized_final_readout_v0_1.md
  ohlcv_1m_split_normalized_inspection_notebook_v0_1.ipynb
  ohlcv_1m_split_normalized_full_universe_audit_notebook_v0_1.ipynb
  population_visual_overview/
    ohlcv_1m_split_normalized_population_visual_manifest_v0_1.csv
    *.png
  event_case_evidence_packs/
    ohlcv_1m_split_normalized_visual_inspector_pack_v0_1.md
    ohlcv_1m_split_normalized_visual_case_manifest_v0_1.csv
    images/
      *.png
  evidence_assets/
    full_universe_split_audit/
      full_universe_split_event_audit_meta.csv
      full_universe_split_event_status_summary.csv
      full_universe_split_event_cases.csv
      full_universe_split_event_cases.parquet
  images/
    *.png
```

`NOTOCAR.md` no forma parte del paquete inspector activo de `1m_split_normalized`.

## Orden Inspector Obligatorio

### 1. Contrato

Leer primero el contrato dataset y schema.

El inspector debe entender:

- `px_split_normalized = px_raw * future_split_factor`;
- `future_split_factor(date_t) = producto de split_ratio con execution_date > date_t`;
- el dia del evento no cuenta como futuro para esa observacion;
- la capa no ajusta dividendos;
- la capa no reemplaza `1m raw`.

### 2. Readout final

Leer:

- `ohlcv_1m_split_normalized_final_readout_v0_1.md`

Rol:

- integra contrato;
- piloto visual;
- auditoria full-universe de eventos;
- consumidor minimo;
- y veredicto de madurez.

### 3. Mapa poblacional visual

Leer:

- `event_case_evidence_packs/ohlcv_1m_split_normalized_visual_inspector_pack_v0_1.md`

Primero abrir la seccion:

- `Mapa Poblacional Visual`

Contiene `6` visuales:

- status overview;
- direccion y ratio;
- cobertura temporal;
- fuerza de invariantes PASS;
- anatomia de coverage-limited;
- concentracion por ticker.

Cada visual tiene:

- `Que muestra`;
- `Responde`;
- `No responde`;
- `Consecuencia`.

### 4. Casepacks visuales

El mismo readout contiene `28` visuales de caso:

- `PASS / Reverse Split`;
- `PASS / Forward Split`;
- `Coverage Limited / No Pre Coverage`;
- `Coverage Limited / No Post Coverage`;
- `Coverage Limited / No 1m Coverage`.

Los casos PASS muestran:

- serie agregada desde `1m raw`;
- serie agregada desde `1m split_normalized`;
- `future_split_factor`;
- fecha de split;
- y estado del invariante.

Los casos coverage-limited muestran:

- que lado de la ventana falta;
- si hay tramo pre o post disponible;
- y por que no se puede contar como fallo semantico.

### 5. Notebooks

Los notebooks siguen siendo utiles para navegacion:

- `ohlcv_1m_split_normalized_inspection_notebook_v0_1.ipynb`
- `ohlcv_1m_split_normalized_full_universe_audit_notebook_v0_1.ipynb`

Pero no sustituyen el paquete visual fijo.

Si un inspector necesita ampliar casos, debe exportar nuevas imagenes fijas y actualizar el manifest/readout, no dejar la conclusion solo dentro del widget.

## Evidencia Cuantitativa Principal

Auditoria full-universe de eventos split:

- `split_files_seen = 4824`
- `non_empty_split_files_with_1m_ticker = 1876`
- `total_event_cases = 3335`
- `PASS = 2280` (`68.37%`)
- `FAIL = 0` (`0.00%`)
- `NO_PRE_COVERAGE = 164` (`4.92%`)
- `NO_POST_COVERAGE = 151` (`4.53%`)
- `NO_1M_COVERAGE = 740` (`22.19%`)

Lectura correcta:

- `PASS` significa cobertura bilateral suficiente y cero violaciones de invariantes;
- `NO_PRE_COVERAGE` no es fallo: falta historia previa;
- `NO_POST_COVERAGE` no es fallo: falta historia posterior;
- `NO_1M_COVERAGE` no es fallo: existe split maestro, pero no historia `1m` cargable;
- `FAIL = 0` es el dato institucional fuerte.

## Lectura Institucional

`ohlcv_1m_split_normalized` queda fuerte para su objetivo preciso:

- proteger comparaciones cross-session frente a splits/reverse splits;
- evitar falsos gaps y falsos shocks mecanicos;
- servir como price view contractual para consumidores intradia que cruzan sesiones.

No queda autorizado como:

- sustituto de `1m raw`;
- capa full adjusted;
- evidencia de calidad general del tape intradia;
- materializacion fisica full-universe completa.

## Mantenimiento

Debe actualizarse este README si ocurre cualquiera de estos casos:

- se reejecuta `full_universe_split_event_cases.parquet`;
- cambia `FAIL`;
- cambia el estado de materializacion fisica;
- se anaden casepacks visuales;
- se promueve o restringe el consumo de `ohlcv_1m_split_normalized`;
- o cambia el consumidor minimo que valida la capa.

Ademas debe actualizarse:

- `event_case_evidence_packs/ohlcv_1m_split_normalized_visual_inspector_pack_v0_1.md`;
- `01_foundations/inspection_dossiers/README.md`;
- `CHANGELOG.md`.
