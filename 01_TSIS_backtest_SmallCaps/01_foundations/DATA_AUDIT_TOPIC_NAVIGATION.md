# Data Audit Topic Navigation

Este documento define donde buscar por tema durante una auditoria de data en `01_foundations`.

No sustituye `DATA_AUDIT_QUALITY_STANDARD.md`. Su funcion es operacional: cuando un auditor humano, un agente o un reviewer tenga una pregunta concreta, debe poder ir al sitio correcto sin depender de memoria conversacional.

Regla base: primero se identifica el tema, despues la familia de data, y solo entonces se leen los artefactos concretos.

## 1. Caracteristicas Tecnicas De Los Files

Pregunta tipica:

- Que contiene cada file?
- Que columnas reales tiene?
- Como esta particionado?
- Que tipos fisicos y semanticos usa?
- Que granularidad, timezone y clave logica aplica?

Donde mirar:

- `canonical_schemas/<family>/`
- `contract_registry/dataset_contracts/`
- `inspection_dossiers/<family>/*readout*`
- `inspection_dossiers/<family>/evidence_assets/technical_profile/`
- `inspection_dossiers/<family>/evidence_assets/schema_profile/`

Evidencia esperada:

- schema esperado;
- schema observado;
- columnas obligatorias y opcionales;
- tipos fisicos;
- tipos semanticos;
- primary key logica;
- particionado;
- timezone;
- granularidad;
- row-count y file-size profile;
- empty-file y unreadable-file profile.

Si no existe este bloque, la auditoria no explica tecnicamente la data.

## 2. Limpieza Y Calidad Basica

Pregunta tipica:

- Hay datos vacios, sucios o no interpretables?
- Hay nulos, strings vacios, sentinels, NaN o inf?
- Hay duplicados?
- Hay outliers?
- Hay valores imposibles?
- Hay timestamps rotos?

Donde mirar:

- `validators/<family>/`
- `inspection_dossiers/<family>/*readout*`
- `inspection_dossiers/<family>/evidence_assets/quality_tables/`
- `inspection_dossiers/<family>/evidence_assets/case_manifests/`
- `inspection_dossiers/<family>/bad_case_evidence_packs/`
- `inspection_dossiers/<family>/flagged_case_evidence_packs/`

Evidencia esperada:

- null profile;
- empty-string profile;
- sentinel profile;
- duplicate profile;
- impossible-value profile;
- outlier profile;
- timestamp validity;
- chronology validity;
- examples by ticker/date/file;
- verdict per defect class.

Si solo hay coverage o row counts, no es una auditoria de limpieza.

## 3. Coverage, Disponibilidad Y Usabilidad

Pregunta tipica:

- La data existe?
- Esta presente para el universo esperado?
- Es legible?
- Es valida?
- Es usable?
- Que diferencia hay entre missing, bad y recoverable?

Donde mirar:

- `dataset_registry/`
- `inspection_dossiers/<family>/*coverage*`
- `inspection_dossiers/<family>/*readout*`
- `inspection_dossiers/<family>/evidence_assets/population_tables/`
- `inspection_dossiers/<family>/evidence_assets/coverage_tables/`
- `inspection_dossiers/<family>/evidence_assets/final_asset_manifest.*`

Evidencia esperada:

- expected universe;
- present universe;
- readable universe;
- valid universe;
- usable universe;
- missing cases;
- bad cases;
- recoverable cases;
- temporal coverage;
- ticker/date coverage;
- per-consumer usability.

Coverage no equivale a calidad. Present no equivale a usable.

## 4. Schema, Contratos Y Formato Canonico

Pregunta tipica:

- Que schema gobierna esta familia?
- Que nombres de columnas son canonicos?
- Que aliases son aceptados?
- Que campos estan prohibidos?
- Que version logica aplica?

Donde mirar:

- `canonical_schemas/<family>/`
- `contract_registry/`
- `module_contracts/`
- `validators/<family>/`
- `data_consumption_policies/`

Evidencia esperada:

- schema contract;
- dataset contract;
- schema version;
- field semantics;
- allowed aliases;
- breaking-change notes;
- validator coverage;
- downstream compatibility statement.

Si el schema vive solo en codigo o notebooks, no es contrato institucional.

## 5. Semantica De Precio Y Ajustes

Pregunta tipica:

- La data es raw, adjusted, split-normalized o dividend-adjusted?
- Que eventos corporativos se aplicaron?
- Existe mezcla silenciosa de price views?
- Puede usarse para labels, features o execution?

Donde mirar:

- `canonical_schemas/<family>/`
- `data_consumption_policies/`
- `inspection_dossiers/<family>/*readout*`
- `inspection_dossiers/<family>/evidence_assets/`
- dossiers especificos de `daily_adjusted`, `1m_split_normalized`, quotes o trades cuando apliquen.

Evidencia esperada:

- price-view declaration;
- raw vs adjusted distinction;
- split factors;
- dividend factors;
- corporate-action compatibility;
- cross-view reconciliation;
- no-mixing guarantee;
- consumer restrictions.

Si no se declara la price view, la data no debe alimentar contratos downstream sensibles.

## 6. Politicas De Consumo Downstream

Pregunta tipica:

- Quien puede consumir esta data?
- Para que uso esta aprobada?
- Que consumidores estan bloqueados?
- Que flags deben propagarse?

Donde mirar:

- `data_consumption_policies/`
- `module_contracts/`
- `inspection_dossiers/<family>/*readout*`
- `inspection_dossiers/<family>/evidence_assets/final_asset_manifest.*`

Evidencia esperada:

- consumer matrix;
- allowed consumers;
- prohibited consumers;
- required flags;
- quality gates;
- assumptions;
- limitations;
- downstream impact.

El readout humano debe traducir defects tecnicos en restricciones de uso.

## 7. Casos Buenos, Condicionados Y Malos

Pregunta tipica:

- Como se ve un caso bueno?
- Como se ve un caso malo?
- Que caso es aceptable con flags?
- Que caso debe ser rechazado?

Donde mirar:

- `inspection_dossiers/<family>/good_justification/`
- `inspection_dossiers/<family>/flagged_case_evidence_packs/`
- `inspection_dossiers/<family>/bad_case_evidence_packs/`
- `inspection_dossiers/<family>/coverage_case_evidence_packs/`
- `inspection_dossiers/<family>/family_case_evidence_packs/`
- `inspection_dossiers/<family>/causal_case_evidence_packs/`
- `inspection_dossiers/<family>/evidence_assets/case_manifests/`

Evidencia esperada:

- ticker/date/file identifier;
- defect or quality label;
- chart or table;
- technical explanation;
- semantic explanation;
- consumer implication;
- reproducible asset path.

Una auditoria sin casos concretos obliga al auditor a confiar en agregados.

## 8. Rehabilitacion Y Recoverable Data

Pregunta tipica:

- Que defects pueden recuperarse?
- Que defects requieren flags?
- Que defects son quarantine?
- Que transformacion se aplico?

Donde mirar:

- `inspection_dossiers/<family>/*readout*`
- `inspection_dossiers/<family>/flagged_case_evidence_packs/`
- `inspection_dossiers/<family>/evidence_assets/quality_tables/`
- `data_consumption_policies/`
- `validators/<family>/`

Evidencia esperada:

- recoverable defect class;
- recovery rule;
- before/after profile;
- required flag;
- consumer restrictions;
- non-recoverable boundary.

Recoverable no significa clean. Debe quedar propagado como semantica.

## 9. Poblacion, Universo Y Drift

Pregunta tipica:

- Que tickers, fechas, anos, sesiones o vendors cubre la data?
- Hay drift temporal?
- Hay drift por vendor o batch?
- Hay familias incompletas?

Donde mirar:

- `dataset_registry/`
- `inspection_dossiers/<family>/evidence_assets/population_tables/`
- `inspection_dossiers/<family>/evidence_assets/coverage_tables/`
- `inspection_dossiers/<family>/*readout*`

Evidencia esperada:

- ticker population;
- date population;
- year/month/session population;
- vendor/batch population;
- missingness by segment;
- badness by segment;
- drift profile;
- representativeness statement.

Los defectos agregados deben poder bajarse a segmentos concretos.

## 10. Graficos, Tablas Y Manifests

Pregunta tipica:

- Donde esta la evidencia que sostiene una conclusion?
- Que tabla o grafico corresponde a cada claim?
- Como se reproduce?

Donde mirar:

- `inspection_dossiers/<family>/evidence_assets/`
- `inspection_dossiers/<family>/evidence_assets/final_asset_manifest.*`
- `inspection_dossiers/<family>/evidence_assets/case_manifests/`
- `inspection_dossiers/<family>/*readout*`

Evidencia esperada:

- asset path;
- asset type;
- run id;
- source dataset;
- config;
- code path;
- timestamp;
- claim supported;
- limitations.

Un grafico sin manifest es evidencia debil. Un claim sin asset es deuda.

## 11. Lineage, Registry Y Source Of Truth

Pregunta tipica:

- De donde viene este dataset?
- Que identidad logica tiene?
- Que version o batch representa?
- Que rutas son oficiales?

Donde mirar:

- `dataset_registry/`
- `contract_registry/dataset_contracts/`
- `data_consumption_policies/`
- `inspection_dossiers/<family>/*readout*`
- `README.md` local de la familia, si existe.

Evidencia esperada:

- dataset identity;
- physical roots;
- logical version;
- source vendor;
- snapshot or batch;
- promotion level;
- owner;
- downstream contract links.

Ningun path suelto debe actuar como source of truth sin registry o contrato.

## 12. Capas Derivadas Y Promocion

Pregunta tipica:

- Esta capa es raw, normalized, adjusted, derived o promoted?
- Que depende de que?
- Que cambio exige version nueva?

Donde mirar:

- `module_contracts/`
- `contract_registry/`
- `dataset_registry/`
- `CHANGELOG.md` del modulo;
- `inspection_dossiers/<family>/*readout*`

Evidencia esperada:

- upstream dependency;
- transformation semantics;
- input contract;
- output contract;
- promotion status;
- versioning implications;
- downstream breakage risk.

Una capa derivada debe declarar su dependencia y no redefinir silently la data upstream.

## 13. Leakage, Labels, Features Y ML/RL

Pregunta tipica:

- Esta data puede usarse para features?
- Puede usarse para labels?
- Hay riesgo de leakage?
- Es compatible con Offline RL?

Donde mirar:

- `data_consumption_policies/`
- `module_contracts/`
- `inspection_dossiers/<family>/*readout*`
- `RESEARCH_PHILOSOPHY.md` y reglas locales aplicables.

Evidencia esperada:

- temporal availability;
- causal availability;
- label/feature separation;
- adjusted/raw compatibility;
- embargo or lag requirements;
- forbidden joins;
- RL compatibility statement.

La utilidad para research no autoriza automaticamente uso para labels o RL.

## 14. Microestructura, Trades Y Quotes

Pregunta tipica:

- Los trades son plausibles frente a quotes y daily?
- Las quotes tienen bid/ask usable?
- Hay crossed/locked markets?
- Hay price/size defects?

Donde mirar:

- `inspection_dossiers/trades/`
- `inspection_dossiers/quotes/`
- `canonical_schemas/trades/`
- `canonical_schemas/quotes/`
- `validators/trades/`
- `validators/quotes/`
- `data_consumption_policies/`

Evidencia esperada:

- trade price/size validity;
- duplicate trade profile;
- quote spread profile;
- crossed/locked profile;
- stale quote profile;
- trade-vs-quote alignment;
- trade-vs-daily alignment;
- regular-hours and full-day distinction;
- consumer restrictions.

Microestructura no debe reducirse a OHLC coverage.

## 15. Daily, Daily Adjusted Y 1m

Pregunta tipica:

- Daily raw es consistente?
- Daily adjusted respeta corporate actions?
- 1m split-normalized mantiene semantica temporal?
- Que puede usarse para labels o features?

Donde mirar:

- `inspection_dossiers/daily/`
- `inspection_dossiers/daily_adjusted/`
- `inspection_dossiers/1m_split_normalized/`
- `canonical_schemas/daily/`
- `canonical_schemas/daily_adjusted/`
- `canonical_schemas/1m_split_normalized/`
- `validators/daily/`
- `validators/1m_split_normalized/`
- `data_consumption_policies/`

Evidencia esperada:

- OHLC validity;
- volume validity;
- split/dividend adjustment logic;
- raw vs adjusted declaration;
- minute bar completeness;
- timestamp and session validity;
- cross-layer reconciliation;
- downstream use matrix.

La familia 1m no debe heredar aprobacion de daily sin evidencia propia.

## 16. Deudas, Limitaciones Y Riesgo Residual

Pregunta tipica:

- Que no esta cerrado?
- Que no se pudo auditar?
- Que riesgo queda vivo?
- Que bloquearia promocion institucional?

Donde mirar:

- `inspection_dossiers/<family>/*readout*`
- `inspection_dossiers/<family>/README.md`, si existe;
- `CHANGELOG.md` del modulo cuando la deuda tenga impacto operativo;
- `PROJECT_OPERATING_SYSTEM.md` para promocion y gobernanza.

Evidencia esperada:

- explicit open debt;
- severity;
- affected data;
- affected consumers;
- proposed next action;
- whether blocking or non-blocking.

La deuda debe estar escrita donde el siguiente auditor la encuentre.

## 17. Estructura Por Tema Para Nuevas Auditorias

Toda auditoria nueva debe crear una seccion de readout por cada tema aplicable:

1. Scope y lineage.
2. File structure and technical profile.
3. Schema contract.
4. Population and coverage.
5. Data cleanliness.
6. Semantic quality.
7. Cross-layer reconciliation.
8. Case evidence.
9. Consumer matrix.
10. Verdict and restrictions.
11. Open debt.

Cada seccion debe apuntar a:

- contrato esperado;
- evidencia observada;
- tabla o grafico;
- caso concreto;
- decision de consumo.

## 18. Regla Final

Cuando alguien pregunte por un tema, no se debe contestar desde memoria. Se debe navegar por tema, abrir los contratos, abrir el dossier de la familia, revisar `evidence_assets/`, y solo entonces dar una conclusion.

Este documento existe para que las auditorias futuras de data no sean menos exigentes que `daily`, `trades`, `quotes`, `daily_adjusted` y `1m_split_normalized`.
