# Historical Audit Preservation And Promotion Contract

Fecha: 2026-06-13
Estado: contract v0.1
Ambito: Data Quality Harness sobre auditoria historica preservada en `01_research/01_auditoria_RAW_DATA`

## 1. Proposito

Este contrato impide que un agente vuelva a auditar desde cero datasets que ya tienen trabajo historico profundo.

Antes de crear, reescribir o completar artefactos en:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/
```

el agente debe leer, inventariar y reconciliar la auditoria historica preservada en:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/
```

La pregunta correcta no es:

```text
Como audito este dataset desde cero?
```

La pregunta correcta es:

```text
Que verdad historica ya existe, que parte esta promovida a 01_foundations, que parte falta institucionalizar y que evidencia moderna falta para igualar el estandar de daily/quotes/trades/minute/1m_split_normalized?
```

## 2. Rutas historicas protegidas

Estas rutas son evidencia historica y provenance. Son read-only:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/halts/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/short/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/
```

Prohibido:

- modificar;
- mover;
- borrar;
- renombrar;
- limpiar;
- normalizar;
- regenerar encima;
- convertir en outputs modernos sin copia/promocion controlada.

Permitido:

- leer contratos historicos;
- leer closeouts;
- leer manifests;
- leer notebooks;
- leer cell_code;
- leer cache metadata;
- extraer tablas ligeras de inventario;
- citar rutas como provenance;
- promover conclusiones a `01_foundations` solo mediante artefactos nuevos o actualizaciones explicitas.

## 3. Jerarquia de fuentes

Para un dataset con auditoria historica, la jerarquia operativa es:

1. Contratos raiz TSIS y contratos del modulo SmallCaps.
2. Este contrato.
3. Estado actual de `01_foundations`.
4. Auditoria historica bajo `00_data_certification/auditoria/<dataset>`.
5. Certificacion historica bajo `00_data_certification/certification/<dataset>` y `global_metrics`.
6. Roots fisicos de data, siempre read-only.
7. Nueva evidencia moderna generada por el Harness.

Si hay conflicto entre una inferencia nueva y un closeout historico, el agente no puede sobrescribir la conclusion historica. Debe crear un gap o conflict note y parar para revision humana.

## 4. Regla no-rework

Un agente no debe rehacer una auditoria desde cero cuando ya existen:

- contrato historico;
- diseno/implementacion historica;
- builder o `cell_code`;
- cache artifacts;
- notebook inspector;
- closeout estructural;
- closeout causal;
- certificacion o closeout final.

En esos casos el trabajo correcto es promocion institucional, no redescubrimiento.

Promocion institucional significa:

- inventariar lo historico;
- comparar contra `01_foundations`;
- identificar lo ya promovido;
- identificar lo no promovido;
- crear contratos, registries, policies, validators o dossiers modernos faltantes;
- crear evidencia ligera o visual moderna solo donde aporte decision;
- preservar el estado de consumo honesto;
- no sobrepromover.

## 5. Gate por carpeta

Hasta nueva decision humana, el Data Quality Harness trabaja una carpeta/dataset cada vez.

Flujo obligatorio:

```text
dataset seleccionado
-> leer contratos y auditoria historica
-> inventariar estado actual en 01_foundations
-> escribir integration_notes / promotion_gap
-> crear o actualizar paquete minimo solo para ese dataset
-> validar
-> parar
-> revision humana
```

Prohibido en el mismo run:

- terminar `reference` y continuar automaticamente con `Halts`;
- actualizar indices finales globales antes de revisar la carpeta;
- hacer integracion final de todos los datasets si solo se ha revisado uno;
- lanzar escrituras paralelas en indices compartidos.

## 6. Ledger historico obligatorio

Todo agente que trabaje estos datasets debe partir de este ledger.

### 6.1. additional

Ruta historica:

```text
01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/
```

Estado historico:

- auditoria profunda existente;
- contrato historico existente;
- diseno/implementacion historica existente;
- root-cause notebook existente;
- causal overlay existente;
- closeout estructural existente;
- closeout causal existente;
- closeout final existente;
- certificacion historica existente.

Inventario historico observado:

- `01_contrato_additional.md`
- `02_diseno_implementacion_additional_v2.md`
- `03_additional_root_cause_audit_notebook.ipynb`
- `03_additional_root_cause_audit_phase1_closeout.md`
- `04_additional_causal_overlay_closeout.md`
- `04_additional_closeout.md`
- `descarga_additional.md`
- `cell_code/`
- `cache_v2/`
- `img/`

Verdad historica principal:

- `additional` no es un dataset plano; es un bloque heterogeneo.
- Subbloques: `financials_core`, `financials_ratios`, `news`, `ipos`, `corporate_actions_additional`, `economic`.
- `financials_core`, `economic` y buena parte de `news` son utiles.
- `ratios`, `ipos`, `corporate_actions_additional` requieren uso condicionado.
- Corporate actions en `additional` son fuente secundaria frente a `reference`.
- `news` es materialmente multi-ticker; no puede usarse como causa unica sin ambiguedad.

Hechos historicos relevantes:

- descarga ticker-based: `43,416` tareas, `43,416` ok, `0` errors;
- macro: `3/3` ok;
- `news`: `287,138` eventos, `3,869` tickers, solo `36.38%` mono-ticker;
- `news_near_halt_market_event`: `1,268`;
- `ipo_near_halt_market_event`: `156`;
- dividend overlap contra reference: `1,253` exact;
- split overlap contra reference: `1,858` exact.

Estado frente a `01_foundations`:

- hay foundation minima: schemas, registry, contract, policy e institutional closeout;
- no hay dossier inspector moderno comparable a `daily/quotes/trades/minute`;
- no hay visual/casepack moderno completo institucionalizado.

Trabajo permitido:

- promocionar el ledger historico a dossier moderno parcial;
- crear `integration_notes.md`;
- crear evidence assets ligeros que referencien cache/manifests historicos;
- crear visual gap audit si no se generan nuevos visuales;
- no tratar `additional` como dataset homogeneo.

Trabajo prohibido:

- reauditar `additional` desde cero;
- fusionar subbloques como si tuvieran schema comun;
- usar corporate actions de `additional` como verdad primaria;
- usar `news` multi-ticker como causalidad directa sin flags.

Estado Harness propuesto:

```text
foundation_minimal + historical_deep_audit_closed + modern_dossier_gap
```

### 6.2. halts

Ruta historica:

```text
01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/halts/
```

Estado historico:

- auditoria profunda existente;
- contrato historico existente;
- descarga oficial documentada;
- builder multi-source documentado;
- notebook inspector existente;
- causal overlay existente;
- closeout estructural existente;
- closeout causal existente;
- closeout final existente;
- certificacion historica existente.

Inventario historico observado:

- `00_descarga_datos_halts.md`
- `00_descarga_datos_halts.ipynb`
- `01_contrato_halts.md`
- `01_fases_auditoria.md`
- `02_diseno_implementacion_halts_v2.md`
- `03_halts_root_cause_audit_notebook.ipynb`
- `03_halts_root_cause_audit_phase1_closeout.md`
- `04_halts_causal_overlay_closeout.md`
- `04_halts_closeout.md`
- `cell_code/`
- `cache_v2/`
- `img_phase1/`

Verdad historica principal:

- `halts` es verdad oficial de eventos, no una inferencia desde quotes/trades.
- Fuentes oficiales: Nasdaq, NYSE, SEC.
- Quotes/trades son evidencia de comportamiento alrededor del evento, no fuente primaria del evento.
- SEC aporta contexto regulatorio, no intradia completo.

Hechos historicos relevantes:

- rows fuente iniciales: Nasdaq `119,630`, NYSE `13,178`, SEC `1,346`;
- canonical events: `132,257`;
- `good_full_intraday_event`: `129,638`;
- `good_date_level_event`: `1,272`;
- `review_partial_identity`: `1,096`;
- `regulatory_context_only`: `250`;
- residual hard bad: `1` canonical event;
- visual cases `<1B`: `25,301`;
- `confirmed_halt_microstructure_coherent`: `18,591`;
- `halt_with_trades_signal_only`: `3,914`;
- `halt_with_quotes_signal_only`: `1,896`.

Estado frente a `01_foundations`:

- existen schemas;
- no hay paquete foundation moderno completo visible: registry, policy, validators, dossier moderno;
- la auditoria historica esta mucho mas avanzada que su promocion institucional.

Trabajo permitido:

- promocionar `halts` a `01_foundations`;
- crear contract/registry/policy/validators/dossier desde evidencia historica;
- crear evidence manifests ligeros apuntando a cache historica;
- crear notebooks o wrappers inspectores solo si el rol humano queda mejor soportado.

Trabajo prohibido:

- descargar de nuevo fuentes oficiales sin decision humana;
- reconstruir master encima de artefactos historicos;
- tratar `halts` como dataset Polygon;
- cambiar la verdad primaria desde official events a market behavior.

Estado Harness propuesto:

```text
historical_deep_audit_closed + foundation_promotion_missing
```

### 6.3. reference

Ruta historica:

```text
01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/
```

Estado historico:

- auditoria profunda existente;
- contrato historico existente;
- download notebooks existentes;
- related-companies notebook existente;
- root-cause notebook existente;
- closeout estructural existente;
- causal overlay existente;
- closeout final existente;
- certificacion historica existente.

Inventario historico observado:

- `00_descarga_datos_polygon_01_reference.ipynb`
- `01_contrato_reference.md`
- `01_related_companies.ipynb`
- `02_diseno_implementacion_reference_v2.md`
- `03_reference_root_cause_audit_notebook.ipynb`
- `03_reference_root_cause_audit_phase1_closeout.md`
- `04_reference_causal_overlay_closeout.md`
- `04_reference_closeout.md`
- `cell_code/`
- `cache_v2/`

Verdad historica principal:

- `reference` es identidad, existencia, taxonomia y corporate actions; no es market behavior.
- Debe cruzar con daily, 1m, quotes, trades y halts para evaluar uso, pero no se valida solo por comportamiento de mercado.
- Orden de confianza historico: identity snapshot, events->halts, splits->trades, events->quotes.

Hechos historicos relevantes:

- download audit: `12,468` requests, `12,243` ok, `200` errors, `25` resume-skip;
- identity snapshot: `12,468` rows;
- `good_identity_snapshot`: `12,093` (`96.99%`);
- `bad_unresolved_identity`: `200` (`1.60%`);
- `review_transient_symbol`: `175` (`1.40%`);
- all_tickers listing snapshots: `12,977,501` rows, `13,124` tickers;
- events exploded: `13,215` rows;
- split case index: `14,909` rows;
- dividend case index: `273,799` rows;
- events->halts candidates: `948`;
- events->quotes candidates: `2,595`;
- ticker-change near halt: `775`;
- ticker-change near quotes anomaly: `2,330`.

Estado frente a `01_foundations`:

- foundation minima promovida: schemas, contract, registry, policy, validators y closeout/gap audit;
- existe `reference_modernization_gap_audit_2026-06-12.md`;
- no esta al nivel de dossier moderno completo con visual/casepack comparable a los bloques maduros.

Trabajo permitido:

- completar promocion moderna partiendo del gap audit ya existente;
- crear visual/casepack plan o assets ligeros;
- mejorar evidence index, README y readout;
- no duplicar conclusiones historicas como si fueran nuevas.

Trabajo prohibido:

- reauditar reference desde cero;
- tratar errores `overview 404` como downloader bug sin leer la explicacion historica;
- declarar consumo universal sin flags de identidad/transient/unresolved;
- borrar o reemplazar foundation minima ya promovida.

Estado Harness propuesto:

```text
foundation_minimal + historical_deep_audit_closed + modernization_gap_documented
```

### 6.4. short

Ruta historica:

```text
01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/short/
```

Estado historico:

- auditoria profunda existente;
- contrato historico existente;
- root-cause notebook existente;
- causal overlay existente;
- closeout estructural existente;
- closeout causal existente;
- closeout final existente;
- certificacion historica existente.

Inventario historico observado:

- `01_contrato_short.md`
- `02_diseno_implementacion_short_v2.md`
- `03_short_root_cause_audit_notebook.ipynb`
- `03_short_root_cause_audit_phase1_closeout.md`
- `04_short_causal_overlay_closeout.md`
- `04_short_closeout.md`
- `cobertura_short_data.md`
- `cell_code/`
- `cache_v2/`

Verdad historica principal:

- FINRA es baseline oficial para short.
- Polygon/local short es fuente secundaria/comparativa.
- El problema principal no es falta de archivos sino compatibilidad temporal, ticker reuse y limites de causalidad.
- Short flow puede explicar contexto, no reemplaza validacion de price/volume/halts.

Hechos historicos relevantes:

- short data local cubria `4,824/4,824` tickers para short_interest y short_volume;
- certification previa: `CERTIFIED_OK 1,130`, `CERTIFIED_OK_WITH_LIMITED_WINDOW 738`, `REVIEW_TICKER_REUSE 761`, `REVIEW_REFERENCE_CONFLICT 2,195`;
- FINRA short volume: `4,623` tickers, `0` empty, ventana `2018-08-01` a `2026-04-29`;
- Polygon short volume: `3,381` tickers, `1,443` empty;
- short_volume causal rows: `55,920`;
- `short_flow_near_market_anomaly`: `53,229`;
- `short_flow_near_halt`: `88`;
- `short_flow_market_clean`: `2,603`;
- short_interest context rows: `1,993`.

Estado frente a `01_foundations`:

- hay foundation minima para `short` y `short_review`;
- no hay dossier moderno completo comparable a mature datasets;
- la politica de consumo debe preservar FINRA baseline y Polygon secondary.

Trabajo permitido:

- mejorar promocion institucional;
- crear evidence manifests y readout moderno parcial;
- documentar limits de consumo;
- crear visual/casepack gap si no se generan paneles.

Trabajo prohibido:

- tratar Polygon short como baseline oficial;
- sobrepromover high short interest como causa;
- usar tickers con riesgo de reuse sin flags;
- ignorar FINRA.

Estado Harness propuesto:

```text
foundation_minimal + historical_deep_audit_closed + modern_dossier_gap
```

## 7. Diferencia entre auditoria historica y foundation moderna

La auditoria historica ya contiene mucha verdad:

- notebooks;
- builders;
- caches;
- closeouts;
- visual overlays;
- certificacion;
- metricas globales.

Pero `01_foundations` es la capa institucional consumible por TSIS.

Por tanto, un dataset puede tener auditoria historica cerrada y aun asi no estar listo para consumo moderno si falta:

- registry parseable;
- consumption policy;
- validators;
- inspection dossier local;
- manifests consumibles;
- visual/casepack institucional;
- integration notes;
- estado de consumo.

El trabajo del Harness es cerrar esa distancia sin destruir la auditoria historica.

## 8. Promotion gap obligatorio

Antes de modificar `01_foundations`, el agente debe producir o actualizar un `integration_notes.md` o documento equivalente para el dataset con:

- historical audit files read;
- certification files read;
- current `01_foundations` files found;
- historical truths already promoted;
- historical truths not promoted;
- modern evidence missing;
- files the agent intends to create or update;
- files it will not touch;
- stop condition.

Si el dataset tiene una auditoria historica profunda, este documento debe existir antes de cualquier integracion global.

## 9. No-copy-big-data rule

No se deben copiar caches historicas grandes, parquet pesados o roots fisicos a `01_foundations`.

La promocion debe crear artefactos ligeros:

- manifests;
- summaries;
- readouts;
- case indices reducidos;
- visual summaries;
- links relativos a provenance;
- checksums cuando aplique;
- builders residentes si se requiere reproducibilidad.

Los datos pesados siguen siendo provenance read-only.

## 10. Reglas de notebooks

Los notebooks historicos son evidencia.

El agente debe leerlos como:

- interfaz inspectora historica;
- registro de outputs ejecutados;
- guia de visualizacion;
- trazabilidad de decisiones.

Pero no debe convertir notebooks en la unica fuente moderna.

Una conclusion estable debe estar promovida a:

- readout;
- policy;
- validator;
- contract;
- manifest;
- evidence pack;
- integration notes.

## 11. Reglas de imagenes y visual overlays historicos

Cuando existan imagenes o overlays historicos:

- deben inventariarse;
- debe explicarse si ya tienen lectura causal en closeout;
- no deben tratarse como decoracion;
- no deben copiarse masivamente sin motivo;
- no deben reemplazarse por graficos nuevos sin preservar la lectura historica.

Si se crea un visual moderno, debe declarar:

```text
Que muestra
Responde
No responde
Consecuencia
```

## 12. Rutas prohibidas adicionales

Ademas de las rutas historicas protegidas, se mantienen como read-only:

```text
E:/TSIS/data/
C:/TSIS_Data/data/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/data/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/run/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/
```

`E:/TSIS/data/images_Flash_Research` queda fuera de alcance del Data Quality Harness.

No se inventaria, no se OCRiza, no se mueve, no se valida y no se institucionaliza en este run.

## 13. Acceptance para agentes

Un agente Data Quality Harness solo puede comenzar un dataset si puede declarar:

```text
He leido este contrato.
He leido la auditoria historica aplicable.
He leido la certificacion historica aplicable.
He comparado contra 01_foundations.
No voy a modificar rutas protegidas.
Voy a trabajar una sola carpeta/dataset y parar al terminar.
```

Si no puede cumplirlo, debe parar.

## 14. Primer siguiente paso

El siguiente trabajo no debe ser "cerrar todos los datasets".

Debe ser:

```text
Seleccionar un unico dataset.
Crear su promotion gap / integration notes.
Promover solo lo que falta desde la auditoria historica hacia 01_foundations.
Parar para revision humana.
```

Orden recomendado despues de este contrato:

1. `reference`, porque ya tiene foundation minima y gap moderno documentado.
2. `halts`, porque tiene auditoria historica cerrada pero poca promocion en `01_foundations`.
3. `additional`, porque es heterogeneo y ya tiene foundation minima.
4. `short`, porque depende de preservar FINRA baseline.
5. `financial`, si se confirma que no esta cubierto suficientemente por `additional/financials_core`.
6. `regime_indicators`.
7. Integracion final, solo cuando todos los gates por dataset hayan sido revisados.

