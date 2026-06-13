# TSIS Data Audit Harness Agentic Operating Map

Fecha: 2026-06-11
Estado: snapshot auditor y mapa operativo v0.1
Ambito: `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations`
Destino: diseno de Harness agentic para auditoria de data en tiempo real

## 0. Proposito ejecutivo

Este documento tiene tres funciones al mismo tiempo:

1. Dejar una foto auditada, verificable y fechada de lo que existe hoy en
   `01_foundations`.
2. Convertir esa auditoria historica en un mapa de transito para agentes
   Harness que operaran sobre data entrante en tiempo real.
3. Definir los contratos minimos que debera respetar cualquier agente antes de
   tomar decisiones, generar reportes, abrir revisiones humanas o habilitar
   consumo por backtest, ML o AlphaEvolve.

La idea central es simple: los agentes no deben inventar una auditoria nueva.
Deben ejecutar, mantener y extender la semantica ya descubierta en la auditoria
manual y semi-automatizada. La auditoria existente es el baseline de verdad.
El Harness debe convertirla en un sistema operativo recurrente.

Este MD no reemplaza a los contratos, registries, manifests, notebooks ni
dossiers existentes. Los resume y los convierte en una guia de arquitectura.
Cuando haya conflicto, la fuente primaria es siempre el artefacto verificable:
schema, manifest, parquet, CSV, notebook, script o dossier auditado.

## 1. Control de lectura y verificacion

La carpeta completa fue leida y no se uso ningun documento de `00_CTO` como
fuente unica de verdad. Se verificaron los artefactos reales: Markdown, YAML,
CSV, Parquet, PNG, notebooks y referencias cruzadas.

### 1.1 Corpus leido

- Ruta leida: `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations`
- Archivos totales leidos: 1,961
- Bytes leidos: 540,904,131
- Errores de lectura: 0
- Hash agregado SHA256 del corpus leido:
  `cd25250ffb3e879a0fcb2a43e46b8fc05ed2db218a418d7f6e93aa93a763f00e`

### 1.2 Distribucion por extension

| Extension | Archivos |
|---|---:|
| `.png` | 1,414 |
| `.md` | 293 |
| `.csv` | 204 |
| `.parquet` | 21 |
| `.yaml` | 12 |
| `.ipynb` | 11 |
| `.json` | 1 |
| sin extension | 5 |

### 1.3 Distribucion por carpeta principal

| Carpeta | Archivos | Bytes |
|---|---:|---:|
| `inspection_dossiers` | 1,792 | 539,994,338 |
| `module_contracts` | 75 | 489,530 |
| `canonical_schemas` | 43 | 152,773 |
| `dataset_registry` | 17 | 52,557 |
| `contract_registry` | 16 | 115,530 |
| `data_consumption_policies` | 11 | 59,204 |
| `validators` | 5 | 34,685 |
| `00_CTO` | 2 | 5,514 |

### 1.4 Validaciones tecnicas hechas

- PNG: 1,414 imagenes verificadas, 0 corruptas.
- Referencias Markdown a archivos: 162 referencias, 0 faltantes despues de
  normalizar rutas Windows.
- Referencias Markdown a imagenes: 1,410 referencias, 2 faltantes.
- Referencias CSV a PNG: 964 referencias, 0 faltantes.
- YAML: todos los YAML parsean salvo un caso descrito abajo.
- Parquet: se abrieron los 21 Parquet, con schema y numero de filas verificados.
- Notebooks: se leyeron 11 notebooks completos.

### 1.5 Incidencias tecnicas detectadas

1. `dataset_registry/trades/trades_registry_entry.yaml` no parsea como YAML
   estricto porque contiene items con backticks no escapados en `notes`.
   Su contenido sigue siendo interpretable y contiene informacion operacional
   relevante. Antes de agentizar, debe corregirse.

2. Faltan dos imagenes referenciadas en:
   `inspection_dossiers/trades/family_case_evidence_packs/bad_data/bad_data_cases_v0_1.md`

   Imagenes faltantes:

   - `./images/00_trades_57f_acceptance_distribution.png`
   - `./images/01_bad_data_57f_failure_signatures.png`

3. `inspection_dossiers/trades/family_casepacks_index.csv` indexa solo
   `bad_data`, aunque existen manifests y casepacks reales para mas familias.
   Esto no invalida la auditoria, pero si es una deuda de navegabilidad.

## 2. Lectura correcta de este documento

Este MD debe usarse como:

- Mapa de onboarding para cualquier agente que vaya a tocar auditoria de data.
- Baseline para disenar pruebas de regresion del Harness.
- Inventario de estados de calidad ya aceptados.
- Diccionario de decisiones: que se puede consumir, que requiere review, que se
  bloquea y que se puede rehabilitar bajo condiciones.
- Puente entre auditoria historica y operacion live.
- Documento de gobierno para evitar que un agente sobredeclare limpieza,
  descarte informacion util o colapse categorias distintas.

Este MD no debe usarse como:

- Sustituto de schemas, registries, manifests o dossiers.
- Licencia para simplificar taxonomias.
- Fuente unica para resolver casos frontera.
- Documento final de arquitectura completa de TSIS.
- Documento de estrategia de trading.

## 3. Principios que los agentes deben respetar

### 3.1 La data no es binaria

El proyecto no clasifica la data solo como buena o mala. Existen estados como
`good`, `review`, `bad`, `recoverable_without_penalty`,
`recoverable_with_flag`, `review_not_rehabilitated`,
`reference_scale_mismatch`, `review_microstructure`,
`review_no_1m_reference` y `review_1m_reference_alignment`.

Un agente que reduzca todo a pass/fail pierde informacion critica.

### 3.2 La severidad no siempre es veredicto final

En quotes y trades, una severidad `HARD_FAIL` o `SOFT_FAIL` puede ser alarma de
inspeccion, no sentencia final automatica para todos los usos. El agente debe
preservar la diferencia entre metrica, alarma, familia y decision de consumo.

### 3.3 La cobertura no es fallo semantico

Estados como `NO_PRE_COVERAGE`, `NO_POST_COVERAGE` o `NO_1M_COVERAGE` no deben
confundirse con transformaciones erroneas. Son limites de observabilidad.

### 3.4 La vista de precio importa

No es lo mismo usar daily raw, daily adjusted, quotes, trades, raw 1m,
split-normalized 1m o features derivadas. Un agente debe conocer el contrato de
cada vista antes de autorizar consumo.

### 3.5 La evidencia visual es parte del contrato

Los casepacks, imagenes, panels y manifests no son decoracion. Son evidencia
auditora. El Harness debe poder generar, validar y versionar evidencia.

### 3.6 El agente no decide estrategia si la data no paso gates

AlphaEvolve y cualquier motor de generacion/optimizacion de estrategias deben
recibir data con estado de consumo explicito. No deben usar datasets en review
como si fueran limpios.

## 4. Estado auditado por bloque

### 4.1 Daily core

Dataset conceptual: `daily_core_v0_1`
Estado actual: institucionalizado para consumo con reglas.

La auditoria diaria ya ha producido una semantica madura: no basta con que un
archivo exista, y tampoco basta con penalizar todo gap como fallo. La auditoria
distingue errores duros, gaps recuperables, gaps recuperables con flag y casos
no rehabilitados.

#### Hechos verificados

- Universo contractual: 44,423 ticker-year files.
- Hard bad excluidos: 102.
- Tickers diarios incompletos: 653.
- `recoverable_without_penalty`: 374.
- `recoverable_with_flag`: 222.
- Frontera abierta de cobertura: 57.
- Casos visuales hard/bad: 102.
- Casos visuales non-good quality: 48.
- Muestra good visual: 24.

#### Estados que deben preservarse

- `good`
- `recoverable_without_penalty`
- `recoverable_with_flag`
- `review_not_rehabilitated`
- `bad`

#### Lectura operativa

Daily core puede ser usado como base institucional de OHLCV diario, pero el
Harness debe mantener trazabilidad por ticker-year. No debe convertir la calidad
diaria en un bool global.

#### Regla para agentes

Un agente daily debe producir por cada lote live:

- manifest de llegada;
- validacion de schema;
- coverage report;
- clasificacion de gaps;
- decision de consumo;
- evidencia de casos frontera;
- cambios respecto al baseline anterior.

#### Riesgos si se automatiza mal

- Penalizar gaps recuperables como fallo duro.
- Declarar `recoverable_with_flag` como `good`.
- Usar VW como metrica dominante de salud primaria.
- No separar ticker-level, day-level y file-level.

### 4.2 Daily adjusted

Dataset conceptual: vista diaria ajustada.
Estado actual: full-universe promovido, no piloto.

Daily adjusted es una vista derivada para investigacion de retornos ajustados.
No es una fuente de ejecucion intradia ni un reemplazo de raw. Es crucial para
evitar falsos edges generados por splits o dividendos, pero tambien puede crear
errores si se usa fuera de su contrato.

#### Hechos verificados

- Root de salida: `E:\TSIS\data\ohlcv_daily_adjusted`
- Fuente raw: `D:\ohlcv_daily`
- `raw_tickers`: 12,494.
- `adjusted_tickers`: 12,230.
- `raw_tickers_with_files`: 12,230.
- `adjusted_tickers_with_files`: 12,230.
- `raw_year_files`: 125,438.
- `adjusted_year_files`: 125,438.
- Cobertura de tickers: aproximadamente 97.88698575316151%.
- Cobertura de tickers con files: 100%.
- Cobertura year-file: 100%.
- `missing_outputs`: 0.
- `extra_outputs`: 0.
- `read_errors`: 0.
- Archivos sin columnas requeridas: 0.
- `nonpositive_factor_rows`: 0.
- `null_factor_rows`: 0.
- `bad_price_view_rows`: 0.
- `adjusted_rows_total`: 27,418,158.
- `split_non1_rows_total`: 2,335,782.
- `div_non1_rows_total`: 3,210,135.
- `adj_non1_rows_total`: 3,192,661.

#### Perfil de activacion

- `neutral_control`: 9,816.
- `split_only`: 1,210.
- `dividend_only`: 861.
- `split_and_dividend`: 343.

#### Tail de acciones complejas

- `ticker_change`: 3,037.
- Cola de dividendos no CD: 361.

#### Lectura operativa

La vista ajustada parece tecnicamente consistente y promovida. Su uso debe
estar limitado a analisis de retornos ajustados, comparabilidad historica y
feature research donde el contrato lo permita.

#### Regla para agentes

Un agente price-view debe impedir que:

- daily adjusted se use como precio ejecutable;
- raw daily se use para retornos historicos sin tratar splits/dividendos;
- cambios de ticker se interpreten automaticamente como continuidad limpia;
- eventos corporativos complejos se oculten bajo un ajuste numerico sin review.

### 4.3 Quotes

Dataset conceptual: `quotes_core_v0_1`
Estado actual: institucionalizado con semantica forense.

Quotes es una familia muy sensible porque contiene microestructura, spreads,
crossed markets y comportamientos que pueden parecer errores pero a veces son
rasgos del mercado o del feed. La auditoria no debe reducirse a "cruzo/no
cruzo".

#### Poblacion verificada

- `PASS`: 4,365,496.
- `SOFT_FAIL`: 4,078,384.
- `HARD_FAIL`: 1,081,392.
- Total: 9,525,272 ticker-date-file.

#### Muestras forenses verificadas

- `review`: 64 casos.
- `bad`: 15 casos.
- muestra `good`: 12 casos.

#### Bad manifest

- Filas: 15.
- Severidad: todos `HARD_FAIL`.
- Taxonomia:
  - `medium_file_threshold_edge_hard_many_crosses`: 13.
  - `high_hard_crossed_10_to_20`: 2.
- Buckets positivos de crossed:
  - `severe`: 7.
  - `mild`: 5.
  - `moderate`: 3.

#### Review manifest

- Filas: 64.
- Taxonomia:
  - `persistent_soft_crossed_mid_large_scale`: 39.
  - `large_file_threshold_edge_hard_many_crosses`: 25.
- Severidad:
  - `SOFT_FAIL`: 39.
  - `HARD_FAIL`: 25.

#### Good manifest

- Filas: 12.
- Taxonomia:
  - `clean_pass_or_other`: 3.
  - `persistent_soft_crossed_low`: 3.
  - `soft_crossed_micro_noise`: 3.
  - `utc_rollover_large_day_clean`: 3.
- Severidad:
  - `SOFT_FAIL`: 9.
  - `PASS`: 3.

#### Casepacks

Los casepacks de review y bad pasan auditoria: manifest, documentacion y assets
coinciden, sin assets faltantes en esos indices.

#### Lectura operativa

Quotes puede tener eventos que disparan alarmas sin implicar inutilidad total.
Un agente debe capturar:

- crossed bid/ask;
- ask igual a cero vs ask positivo;
- persistencia;
- escala;
- contexto temporal;
- relacion con daily/trades/1m;
- decision final por consumo.

#### Regla para agentes

El agente de quotes no debe rehabilitar automaticamente un caso solo porque hay
contexto externo. Debe proponer lectura, adjuntar evidencia y mantener estado de
review cuando la conclusion no sea mecanica.

### 4.4 Trades

Dataset conceptual: `trades_raw`
Estado actual: `draft_institutionalized`.

Trades es la zona mas delicada. La auditoria muestra que no esta muerto, pero
tampoco esta limpio. Hay informacion util, mucha review, problemas de escala,
microestructura y casos bad claros.

#### Poblacion verificada por estado/familia

| Estado/familia | Filas |
|---|---:|
| `review` | 4,851,211 |
| `reference_scale_mismatch` | 2,418,062 |
| `review_microstructure` | 2,130,781 |
| `bad_data` | 15,869 |
| `review_no_1m_reference` | 8,091 |
| `review_1m_reference_alignment` | 4,992 |
| `good` | 106 |

Total aproximado auditado: 9,429,112.

#### Porcentajes aproximados

- `review`: 51.45%.
- `reference_scale_mismatch`: 25.65%.
- `review_microstructure`: 22.60%.
- `bad_data`: 0.168%.
- `good`: 0.001%.

#### Rehabilitacion de review

Universo `review`: 4,851,211.

- Strict recoverable: 3,327,955 (68.6005%).
- Strict not rehabilitated: 1,523,256.
- Extended recoverable: 3,505,290 (72.2560%).
- Extended not rehabilitated: 1,345,921.

#### Rehabilitacion provisional de review_microstructure

Universo `review_microstructure`: 2,130,781.

- Strict recoverable: 1,516,547 (71.1733%).
- Extended recoverable: 1,636,379 (76.7971%).

#### Rehabilitacion provisional de review_1m_reference_alignment

Universo `review_1m_reference_alignment`: 4,992.

- Strict recoverable: 2,591 (51.9030%).
- Extended recoverable: 3,715 (74.4191%).

#### Bad data subfamilies

- `colapso_escala_rango`: 8,547.
- `integridad_estructural`: 456.
- `mixto_estructural_rango`: 1,522.
- `conflicto_ralo_o_sparse`: 5,344.
- `conflicto_rango_local`: 0.

#### Review microstructure textures

- `odd_lot_dominante`: 2,116,279.
- `sparse_o_ralo`: 11,611.
- `duplicacion_textura`: 1,903.
- `conflicto_fino_1m`: 988.
- `mixto`: 0.

#### Manifests verificados

- `good`: 106 filas.
- `bad_data`: 60 filas en manifest estratificado.
- `review`: 60 filas en manifest estratificado.
- `reference_scale_mismatch`: 60 filas en manifest estratificado.
- `review_microstructure`: 60 filas en manifest estratificado.
- `review_no_1m_reference`: 60 filas en manifest estratificado.
- `review_1m_reference_alignment`: 60 filas en manifest estratificado.

#### Lectura operativa

Trades requiere agentes, pero no para declarar el dataset limpio. Requiere
agentes para:

- mantener taxonomia;
- separar escala, microestructura, sparse data e integridad;
- generar casepacks repetibles;
- decidir que familias se pueden rehabilitar;
- bloquear consumo cuando la evidencia no es suficiente;
- producir cola de revision humana.

#### Regla para agentes

Un agente de trades debe tratar `good` como rareza auditada, no como muestra
representativa del total. Tambien debe preservar `reference_scale_mismatch` como
familia propia, porque puede contener informacion recuperable bajo reglas de
escala y referencia.

### 4.5 Raw 1m

Dataset conceptual: `ohlcv_1m_raw_v0_1`
Estado actual: `institutional_raw_closeout_reconciled_lt1b`.

Raw 1m ha sido reconciliado para el universo lt1b, pero no debe declararse
globalmente limpio. El core OHLCV parece mucho mas sano que VW, y esa diferencia
es una conclusion estructural.

#### Hechos verificados

- Tickers referencia lt1b: 4,824.
- Task keys / filas actuales de manifest 1m: 334,660.
- Tickers unicos actuales: 4,822.

#### Operacion de rescue

- `RESCUE_SCHEMA_ONLY`: 19,713 (5.890456%).
- `RESCUE_SCHEMA_PLUS_VW`: 314,947 (94.109544%).

#### Estados refinados finales

- `good`: 46,652 (13.940118%).
- `review`: 75,245 (22.484014%).
- `bad`: 212,763 (63.575868%).

#### Separacion core/VW

- `core_good`: 331,511 (99.059045%).
- `core_review`: 3,149 (0.940955%).
- `core_bad`: 0.
- `vw_good`: 46,652.
- `vw_review`: 75,245.
- `vw_bad`: 212,763.
- `core_good_vw_bad`: 212,693 (63.554951%).

#### Lectura operativa

La conclusion no es "1m esta mal". La conclusion es que OHLCV core es
ampliamente usable bajo contrato, mientras VW genera la mayor deuda. Esto es
clave para features y backtest: un feature que no depende de VW no debe ser
bloqueado igual que uno que si depende de VW.

#### Regla para agentes

El agente 1m debe emitir calidad por columna/semantica, no solo por archivo.
Debe distinguir:

- core OHLCV;
- volumen;
- VW;
- coverage;
- continuidad temporal;
- relacion con splits;
- compatibilidad con features downstream.

### 4.6 1m split-normalized

Dataset conceptual: vista intradia split-normalized.
Estado actual: vista derivada validada para casos auditables; no full adjusted.

Esta vista existe para evitar falsos gaps generados por splits en intradia. No
es sustituto de raw 1m ni vista ajustada total.

#### Auditoria full universe de eventos split

- Split files vistos: 4,824.
- Split files no vacios con ticker 1m: 1,876.
- Total event cases: 3,335.

#### Estados de eventos

- `PASS`: 2,280 (68.37%).
- `FAIL`: 0 (0.00%).
- `NO_PRE_COVERAGE`: 164 (4.92%).
- `NO_POST_COVERAGE`: 151 (4.53%).
- `NO_1M_COVERAGE`: 740 (22.19%).

#### Lectura operativa

El dato importante es que 100% de los casos plenamente auditables pasan. Los
NO_* son limites de cobertura, no fallo de transformacion.

#### Regla para agentes

El agente split-normalized debe:

- validar eventos nuevos contra raw y referencia;
- separar fallo de transformacion de falta de cobertura;
- impedir que la vista se use como full adjusted;
- generar evidencia alrededor de la ventana del evento.

### 4.7 Intraday regime features

Dataset conceptual: features intradia derivadas.
Estado actual: pilot semantic validation consumer.

Este bloque valida que usar split-normalized puede evitar falsos split gaps en
features. No debe confundirse con un contrato full universe ni con modelo de
ejecucion.

#### Regla para agentes

Un agente de features debe declarar:

- fuente exacta;
- vista de precio;
- dependencia de VW;
- dependencia de split-normalized;
- ventana temporal;
- estado de calidad de cada input;
- decision de consumo por feature.

### 4.8 Additional datasets

Estado general: accepted auxiliary con restricciones por subbloque.

Subbloques relevantes:

- `financials_core`: good.
- `ratios`: review.
- `news`: good_review.
- `ipos`: good_review.
- `corporate_actions`: additional review, secundario frente a referencia.
- `economic`: good macro / review para causalidad ticker.

#### Lectura operativa

Los additional datasets no deben entrar al sistema como verdad primaria sin
gates. Sirven para contexto, features y contraste, pero su contrato debe estar
separado del contrato de OHLCV/trades/quotes.

#### Regla para agentes

El Harness debe exigir:

- provenance;
- coverage;
- fecha efectiva;
- entidad afectada;
- granularidad;
- si aplica a ticker, company, mercado o macro;
- si puede usarse causalmente o solo descriptivamente.

### 4.9 Short y short_review

Estado general:

- `short`: accepted con restricciones.
- `short_review`: baseline FINRA oficial/free/provenance.
- No existe claim limpio de full history 2005-2026.

#### Hechos locales

- Universo: 4,824.
- Tasks: 9,648 OK.
- `short_interest` rows: 520,048.
- `short_volume` rows: 1,430,506.

#### Certificacion local

- `certified_ok`: 1,130.
- `certified_ok_limited_window`: 738.
- `review_ticker_reuse`: 761.
- `review_reference_conflict`: 2,195.

#### FINRA baseline

- Short interest rows: 505,745.
- Short interest tickers: 4,687.
- Short interest window: 2017-12-29 a 2026-04-15.
- Short volume rows: 4,689,038.
- Short volume tickers: 4,623.
- Short volume window: 2018-08-01 a 2026-04-29.

#### Regla para agentes

Un agente short debe ser especialmente estricto con:

- ticker reuse;
- conflictos de referencia;
- ventanas limitadas;
- supervivorship;
- provenance FINRA;
- diferencias entre short interest y short volume.

## 5. Contratos y registries

La carpeta contiene varias capas de verdad:

- `canonical_schemas`: forma esperada de datasets y columnas.
- `contract_registry`: contratos por dataset y familia.
- `dataset_registry`: estado declarativo de datasets.
- `module_contracts`: contratos de modulos y consumidores.
- `data_consumption_policies`: reglas de uso por dataset/estado.
- `validators`: validadores existentes o esqueleto de validacion.
- `inspection_dossiers`: evidencia real, manifests, casepacks, imagenes.

### 5.1 Regla de prioridad

Para un agente, la prioridad debe ser:

1. Artefacto fisico verificable: parquet, CSV, PNG, notebook, script output.
2. Schema o contract formal.
3. Registry de dataset.
4. Dossier de inspeccion.
5. README o documentacion narrativa.
6. Notas CTO.

La documentacion es mapa, no prueba definitiva.

### 5.2 Deuda contractual inmediata

Antes de montar agentes productivos conviene cerrar:

- YAML invalido en `dataset_registry/trades/trades_registry_entry.yaml`.
- Indice incompleto de casepacks de trades.
- Dos imagenes faltantes en bad_data trades.
- Definicion formal de schema para outputs live de Harness.
- Nombres canonicos de estados compartidos.
- Politica de versionado de manifests live.

## 6. Traduccion a Harness agentic

### 6.1 Que debe hacer el Harness

Harness no es un agente unico. Debe ser una arquitectura de ejecucion,
observabilidad y gobierno que coordine agentes especializados.

Debe recibir data entrante y producir:

- manifest de llegada;
- binding a contrato;
- validacion de schema;
- validacion de semantica;
- comparacion contra baseline;
- decision de consumo;
- evidencia;
- cola de review;
- log auditable;
- metricas de drift.

### 6.2 Que no debe hacer el Harness

No debe:

- inventar taxonomias sin registrar cambio;
- corregir silenciosamente data;
- borrar casos raros porque molestan;
- promover datasets a clean sin evidencia;
- mezclar daily adjusted con precios ejecutables;
- alimentar AlphaEvolve con data en review sin flag;
- ocultar diferencias entre raw, adjusted y split-normalized.

### 6.3 Modelo de pipeline live

Cada llegada de data debe pasar por estos niveles:

1. Intake.
2. Contract binding.
3. Schema validation.
4. Structural validation.
5. Semantic validation.
6. Cross-source reconciliation.
7. Consumption decision.
8. Evidence generation.
9. State persistence.
10. Human review queue cuando aplique.

## 7. Agentes iniciales propuestos

### 7.1 `audit_harness_orchestrator`

Responsabilidad:

- Coordinar ejecucion.
- Crear `run_id`.
- Garantizar orden de pasos.
- Unificar outputs.
- Detener pipeline si falta contrato critico.

Inputs:

- lote entrante;
- registry;
- dataset contract;
- calendario;
- universo vigente.

Outputs:

- `run_manifest.json`;
- `run_summary.md`;
- status final del run.

Riesgo que evita:

- ejecuciones parciales sin trazabilidad.

### 7.2 `registry_contract_binding_agent`

Responsabilidad:

- Identificar dataset;
- resolver version de contrato;
- resolver schema canonico;
- declarar si el lote es conocido, nuevo o incompatible.

Outputs:

- `contract_binding_report.json`.

Regla:

- Si no hay contrato, no hay consumo automatico.

### 7.3 `schema_validator_agent`

Responsabilidad:

- Verificar columnas;
- tipos;
- nulls criticos;
- valores no positivos donde no aplican;
- timestamp;
- claves primarias esperadas;
- duplicados estructurales.

Outputs:

- `schema_validation.parquet`;
- `schema_validation_summary.csv`.

Regla:

- No debe emitir juicio semantico si el schema ya fallo de forma dura.

### 7.4 `quality_semantics_agent`

Responsabilidad:

- Traducir metricas a estados ya existentes.
- Mantener taxonomias.
- Clasificar warnings, soft fails y hard fails.
- Separar bad, review, good y recoverable.

Outputs:

- `quality_summary.parquet`;
- `quality_summary.csv`;
- `taxonomy_counts.json`.

Regla:

- Debe preservar categorias granulares.

### 7.5 `price_view_guard_agent`

Responsabilidad:

- Validar que cada consumidor usa la vista correcta.
- Separar raw, adjusted, split-normalized, quotes, trades y features.
- Bloquear usos semanticamente erroneos.

Outputs:

- `price_view_decision.json`.

Ejemplos de bloqueo:

- usar daily adjusted para ejecucion;
- usar raw daily para retornos historicos sin ajuste;
- usar split-normalized como full adjusted;
- usar quotes_raw como daily returns.

### 7.6 `cross_source_reconciliation_agent`

Responsabilidad:

- Comparar fuentes cuando aplique:
  daily vs 1m;
  trades vs 1m;
  quotes vs trades;
  corporate actions vs adjusted;
  FINRA vs short local.

Outputs:

- `reconciliation_report.parquet`;
- `reconciliation_summary.md`.

Regla:

- La reconciliacion no debe rehabilitar automaticamente. Debe separar evidencia
  de decision.

### 7.7 `consumption_gate_agent`

Responsabilidad:

- Convertir estado de calidad en decision de consumo.
- Emitir permisos por consumidor:
  backtest, ML, AlphaEvolve, reporting, human review.

Outputs:

- `consumption_decision.json`;
- `consumer_matrix.csv`.

Estados posibles:

- `allow`;
- `allow_with_flags`;
- `review_required`;
- `block`;
- `not_applicable`.

### 7.8 `evidence_snapshot_agent`

Responsabilidad:

- Generar evidencias reproducibles.
- Verificar assets.
- Crear manifest de imagenes.
- Detectar referencias rotas.

Outputs:

- `evidence_manifest.csv`;
- `casepack_index.csv`;
- imagenes y notas de caso.

Regla:

- Ningun casepack debe quedar con assets faltantes.

### 7.9 `casepack_generation_agent`

Responsabilidad:

- Crear paquetes de revision humana para casos frontera.
- Incluir metricas, fuente, filas representativas, graficos y lectura sugerida.

Output minimo por caso:

- `case_note.md`;
- `metrics.json`;
- `source_rows.parquet` o CSV;
- imagen principal;
- decision pendiente.

### 7.10 `drift_and_baseline_monitor_agent`

Responsabilidad:

- Comparar lote live contra baseline historico.
- Detectar cambios de distribucion.
- Alertar si una familia crece, desaparece o cambia de textura.

Outputs:

- `drift_report.md`;
- `drift_metrics.parquet`.

Ejemplos:

- aumento brusco de crossed quotes;
- incremento de `core_good_vw_bad` en 1m;
- cambio de proporciones de trades microstructure;
- aparicion de gaps daily no vistos.

### 7.11 `human_review_queue_agent`

Responsabilidad:

- Crear cola de decisiones humanas.
- Priorizar por impacto, novedad, severidad y consumo bloqueado.
- Mantener estado de resolucion.

Outputs:

- `open_review_queue.csv`;
- `resolved_review_queue.csv`;
- `review_decisions.md`.

Regla:

- Las decisiones humanas deben convertirse en nuevos tests o nuevas reglas.

## 8. Artefactos live obligatorios por run

Cada ejecucion Harness deberia escribir una carpeta:

`<harness_root>/<dataset>/<date>/<run_id>/`

Contenido minimo:

- `arrival_manifest.json`
- `contract_binding_report.json`
- `schema_validation.parquet`
- `schema_validation_summary.csv`
- `quality_summary.parquet`
- `quality_summary.csv`
- `taxonomy_counts.json`
- `reconciliation_report.parquet` cuando aplique
- `consumption_decision.json`
- `consumer_matrix.csv`
- `state_snapshot.json`
- `evidence_manifest.csv`
- `open_review_queue.csv`
- `run_summary.md`
- `logs/`

### 8.1 `arrival_manifest.json`

Debe contener:

- `run_id`;
- `dataset`;
- `source`;
- `arrival_time_utc`;
- `local_time`;
- `file_count`;
- `row_count` si aplica;
- `byte_count`;
- `input_hashes`;
- `producer`;
- `expected_contract`;
- `calendar_date`;
- `market_session`.

### 8.2 `consumption_decision.json`

Debe contener:

- dataset;
- version de contrato;
- estado global;
- decision por consumidor;
- flags obligatorios;
- casos bloqueantes;
- referencias a evidencia;
- timestamp;
- agente responsable;
- version del agente.

### 8.3 `state_snapshot.json`

Debe contener:

- estado anterior;
- estado nuevo;
- cambios de taxonomia;
- cambios de coverage;
- nuevos casos review;
- casos resueltos;
- hash de outputs.

## 9. Modelo de decision por consumidor

La calidad debe traducirse por uso. Una misma data puede ser valida para un
uso y no para otro.

| Dataset | Backtest | ML | AlphaEvolve | Reporting | Review humana |
|---|---|---|---|---|---|
| Daily core good | allow | allow | allow | allow | no |
| Daily recoverable_without_penalty | allow | allow_with_flags | allow_with_flags | allow | no |
| Daily recoverable_with_flag | allow_with_flags | allow_with_flags | review_required para features sensibles | allow | si frontera nueva |
| Daily bad | block | block | block | allow solo audit | si |
| Daily adjusted | allow para retornos ajustados | allow bajo contrato | allow bajo contrato | allow | si eventos complejos |
| Quotes review | review_required | review_required | block salvo experimento controlado | allow audit | si |
| Quotes bad | block | block | block | allow audit | si |
| Trades review | review_required | review_required | block salvo research aislado | allow audit | si |
| Trades bad_data | block | block | block | allow audit | si |
| Raw 1m core_good_vw_bad | allow si no usa VW | allow_with_flags | allow solo si feature no usa VW | allow audit | si drift |
| 1m split-normalized PASS | allow para caso de split | allow bajo contrato | allow bajo contrato | allow | no |
| 1m split-normalized NO_* | allow limitado / review | review_required | review_required | allow audit | si |
| Short certified_ok | allow bajo contrato | allow bajo contrato | allow bajo contrato | allow | no |
| Short review_reference_conflict | review_required | review_required | block | allow audit | si |

## 10. Evaluacion inicial de los agentes

Antes de live, el Harness debe pasar un replay offline sobre `01_foundations`.
No se debe considerar valido si solo ejecuta sin errores. Debe reproducir
lecturas clave.

### 10.1 Checks minimos de replay

El Harness debe poder reproducir o reconciliar:

- Daily: 44,423 ticker-year files y 102 hard bad excluidos.
- Daily: 374 recoverable_without_penalty y 222 recoverable_with_flag.
- Daily adjusted: 125,438 raw year files y 125,438 adjusted year files.
- Daily adjusted: 0 missing outputs, 0 extra outputs, 0 read errors.
- Quotes: total 9,525,272; PASS 4,365,496; SOFT_FAIL 4,078,384; HARD_FAIL 1,081,392.
- Quotes bad manifest: 15 casos.
- Quotes review manifest: 64 casos.
- Trades: poblacion total por familias principales segun tabla de este MD.
- Trades: `review` 4,851,211 y `bad_data` 15,869.
- Trades: strict recoverable de review 3,327,955.
- 1m raw: 334,660 task keys.
- 1m raw: `core_good` 331,511 y `core_good_vw_bad` 212,693.
- 1m split-normalized: 3,335 event cases y 0 FAIL.
- Short: `certified_ok` 1,130 y `review_reference_conflict` 2,195.

### 10.2 Checks de comportamiento

El Harness debe demostrar que:

- no declara trades limpio;
- no declara raw 1m globalmente limpio;
- no convierte severity en veredicto final sin contrato;
- no colapsa NO_COVERAGE en FAIL;
- no permite daily adjusted como ejecucion;
- no alimenta AlphaEvolve con data bloqueada;
- genera evidencia con assets existentes;
- detecta las 2 imagenes faltantes actuales;
- detecta el YAML invalido de trades.

## 11. Roadmap recomendado

### Fase 1: Preparar fuentes para agentes

Objetivo: que los agentes puedan leer y confiar en las fuentes existentes.

Tareas:

- Corregir YAML invalido de trades.
- Completar indice de casepacks de trades.
- Resolver o registrar formalmente las 2 imagenes faltantes.
- Definir schema de outputs live Harness.
- Definir vocabulario canonico de estados.
- Crear tabla de mapping dataset -> agente -> contrato.

Justificacion:

Si el agente arranca sobre fuentes con deuda de navegabilidad, gastara energia
en interpretar estructura en vez de auditar data.

### Fase 2: Replay offline

Objetivo: ejecutar el Harness sobre la auditoria historica y verificar que
reproduce el baseline.

Tareas:

- Correr agentes contra manifests existentes.
- Comparar outputs contra counts verificados.
- Generar reporte de diferencias.
- Bloquear cambios que alteren semantica sin explicacion.

Justificacion:

Un agente que no reproduce el pasado no debe operar el presente.

### Fase 3: Shadow live

Objetivo: correr el Harness en paralelo con data entrante sin bloquear consumo.

Tareas:

- Procesar data nueva en modo observacion.
- Comparar contra procesos actuales.
- Medir falsos positivos y falsos negativos.
- Afinar colas de review.

Justificacion:

Antes de que el Harness gobierne, debe observar y demostrar estabilidad.

### Fase 4: Gating live

Objetivo: permitir que el Harness emita decisiones de consumo vinculantes.

Tareas:

- Activar `consumption_gate_agent`.
- Bloquear datasets sin contrato.
- Emitir flags a consumidores.
- Registrar decisiones y overrides.

Justificacion:

La calidad de data debe ser una dependencia explicita de backtest, ML y
AlphaEvolve.

### Fase 5: Integracion con AlphaEvolve

Objetivo: que la busqueda de estrategias use solo data autorizada y conozca
sus flags.

Tareas:

- Pasar matriz de consumo a AlphaEvolve.
- Incluir data quality flags como constraints.
- Penalizar estrategias que dependan de zonas en review.
- Registrar lineage completo de cada experimento.

Justificacion:

Un edge robusto no puede depender de errores de data, gaps mal tratados,
splits falsos o vistas de precio equivocadas.

## 12. Casos de uso adicionales de Harness en esta auditoria

Ademas de data live, Harness puede servir para:

1. Regresion documental:
   verificar que README, registries y manifests no se contradicen.

2. Regresion visual:
   verificar que imagenes esperadas existen y se regeneran cuando cambian
   manifests.

3. Auditoria de consumo:
   registrar quien uso que dataset, con que estado y para que experimento.

4. Cola de investigacion:
   priorizar casos donde una pequena decision humana desbloquea mucho universo.

5. Drift historico:
   detectar si nuevos lotes tienen patrones no vistos en la auditoria de 20
   anos.

6. Gobierno de AlphaEvolve:
   impedir que una estrategia optimizada explote errores de data.

7. Reporting ejecutivo:
   producir informes claros de salud de data sin obligar a leer notebooks.

8. Onboarding de nuevos agentes:
   darles rutas, estados, reglas y pruebas antes de tocar codigo.

## 13. Riesgos principales

### 13.1 Riesgo de sobreautomatizacion

Si los agentes toman decisiones sin contratos, pueden convertir incertidumbre en
falsa precision. La solucion es exigir evidencia y estados intermedios.

### 13.2 Riesgo de sobrelimpieza

Si todo lo raro se borra, se pierde informacion de mercado real. Especialmente
en quotes, trades y small caps, lo raro no siempre es incorrecto.

### 13.3 Riesgo de contamination hacia AlphaEvolve

Si AlphaEvolve recibe data con errores silenciosos, encontrara edges falsos.
Cada experimento debe guardar lineage de data y flags de calidad.

### 13.4 Riesgo de deuda semantica

Si cada agente crea su vocabulario, el sistema se fragmenta. Debe existir un
state vocabulary canonico.

### 13.5 Riesgo de confundir auditoria con produccion

La auditoria historica esta avanzada, pero live requiere idempotencia,
observabilidad, retry, versionado y control de drift.

## 14. Lista de no hacer todavia

No hacer todavia:

- Crear agentes productivos sin replay offline.
- Reorganizar carpetas historicas masivamente.
- Declarar terminada la auditoria completa.
- Declarar trades clean.
- Declarar raw 1m clean global.
- Usar `00_CTO` como autoridad de calidad.
- Generar estrategias AlphaEvolve con datasets en review sin flags.
- Optimizar edge antes de cerrar gates de data.
- Mezclar daily adjusted con ejecucion.
- Colapsar coverage gaps en failures.
- Borrar categorias porque parezcan pequenas.
- Ignorar casepacks y evidencia visual.

## 15. Backlog inmediato antes de implementar agentes

Prioridad alta:

1. Arreglar YAML de trades registry.
2. Completar index de casepacks de trades.
3. Resolver las 2 referencias de imagen faltantes.
4. Crear schema de outputs Harness.
5. Crear vocabulary canonico de estados.
6. Crear matriz dataset -> contrato -> agente -> consumidor.

Prioridad media:

7. Crear replay runner offline.
8. Crear comparador de counts contra baseline.
9. Crear plantilla estandar de `run_summary.md`.
10. Crear plantilla de casepack live.
11. Crear formato de review queue.
12. Definir politica de overrides humanos.

Prioridad posterior:

13. Shadow live.
14. Gating live.
15. Integracion con ML.
16. Integracion con AlphaEvolve.
17. Reporting ejecutivo recurrente.

## 16. Primer documento hijo recomendado

El siguiente documento que conviene crear no es aun codigo de agentes. Es:

`2026-06-11_harness_data_audit_state_vocabulary.md`

Debe definir:

- estados canonicos;
- estados por dataset;
- transiciones permitidas;
- estados terminales;
- estados revisables;
- estados rehabilitables;
- mapping a decisiones de consumo;
- ejemplos reales desde esta auditoria.

Justificacion:

Sin vocabulario canonico, cada agente interpretara `review`, `bad`,
`recoverable`, `soft_fail`, `hard_fail`, `NO_COVERAGE` y `PASS` de forma
distinta. Ese seria el primer punto de caos.

## 17. Segundo documento hijo recomendado

Despues del vocabulary, crear:

`2026-06-11_harness_live_run_artifact_contract.md`

Debe definir de forma estricta los schemas de:

- `arrival_manifest.json`;
- `contract_binding_report.json`;
- `schema_validation_summary.csv`;
- `quality_summary.parquet`;
- `taxonomy_counts.json`;
- `consumption_decision.json`;
- `consumer_matrix.csv`;
- `state_snapshot.json`;
- `evidence_manifest.csv`;
- `open_review_queue.csv`;
- `run_summary.md`.

Justificacion:

Los agentes deben escribir outputs estables. Si los outputs cambian en cada
run, no habra sistema operativo, solo ejecuciones sueltas.

## 18. Decision final de arquitectura

El camino correcto segun los contratos y la auditoria leida es:

1. No empezar por crear agentes genericos.
2. Empezar por convertir la auditoria existente en contratos ejecutables.
3. Usar replay offline para comprobar que los agentes entienden la verdad ya
   descubierta.
4. Pasar despues a shadow live.
5. Solo entonces permitir gating live.
6. Integrar finalmente backtest, ML y AlphaEvolve con decisiones de consumo.

La arquitectura Harness debe nacer de la auditoria, no por encima de ella.
El objetivo no es tener agentes; el objetivo es tener calidad de data
gobernable, repetible y defendible.

## 19. Apice de verdad resumido

Si un futuro agente solo recuerda una pagina, debe recordar esto:

- Daily core esta institucionalizado, pero conserva estados recuperables y
  flags.
- Daily adjusted esta promovido para retornos ajustados, no para ejecucion.
- Quotes esta institucionalizado con semantica forense; severity no es siempre
  veredicto final.
- Trades esta avanzado pero en draft institutionalized; no esta limpio ni
  muerto.
- Raw 1m tiene core OHLCV mayoritariamente sano y deuda fuerte en VW.
- 1m split-normalized valida 100% de casos auditables y 0 FAIL, pero los NO_*
  son cobertura.
- Additional y short tienen valor, pero con restricciones de provenance,
  coverage y causalidad.
- Los agentes deben reproducir esta lectura antes de operar live.
- AlphaEvolve debe recibir data gated, con lineage y flags.

## 20. Cierre

Este documento queda como snapshot auditor de 2026-06-11 para disenar Harness
agentic sobre la auditoria de data. Su valor principal no es describir carpetas,
sino fijar el criterio de transicion:

auditoria historica verificada -> contratos ejecutables -> replay offline ->
shadow live -> gating live -> consumo por backtest, ML y AlphaEvolve.

Ese es el rail inicial para TSIS en esta parte del sistema.
