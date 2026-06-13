# Data Audit Completion Artifact Contract

Fecha: 2026-06-12
Estado: contract v0.3
Ambito: cierre moderno de datasets pendientes en `01_TSIS_backtest_SmallCaps/01_foundations`

## 1. Proposito

Este contrato fija que debe producir cualquier agente que cierre un dataset pendiente de la auditoria de data.

El objetivo es que los datasets pendientes no queden cerrados con menos rigor que los bloques ya maduros.

Antes de trabajar sobre datasets con auditoria historica profunda, manda el contrato:

```text
historical_audit_preservation_and_promotion_contract.md
```

Ese contrato aplica especialmente a:

- `additional`;
- `halts`;
- `reference`;
- `short`.

Para esos datasets, el trabajo correcto es primero preservar, reconciliar y promocionar la auditoria historica existente. No se debe empezar por una reauditoria desde cero.

Fuera de alcance:

- `E:/TSIS/data/images_Flash_Research`

`images_Flash_Research` no forma parte del cierre de auditoria Polygon de este Harness. No debe tocarse ni inventariarse en este run.

Benchmark de calidad:

- `daily`;
- `quotes`;
- `trades`;
- `minute / ohlcv_1m_raw`;
- `1m_split_normalized`.

## 2. Principio rector

Un dataset no queda cerrado porque exista en disco ni porque tenga un markdown narrativo.

Queda cerrado cuando hay:

```text
root fisico verificado en modo read-only
-> evidencia historica leida
-> contrato institucional
-> schema
-> registry
-> consumption policy
-> validators
-> dossier inspector
-> notebooks inspectores cuando aporten navegacion humana
-> evidence assets/manifests
-> visuales/casepacks cuando la pregunta lo exija
-> decision de consumo
-> changelog
```

Si falta una pieza, el dataset puede estar `partially_institutionalized`, pero no debe declararse a paridad con los bloques maduros.

## 2.1. Preflight historico obligatorio

Antes de crear o modificar artefactos de un dataset, el agente debe responder:

```text
Existe auditoria historica en 00_data_certification/auditoria/<dataset>?
Existe certificacion historica en 00_data_certification/certification/<dataset>?
Que parte de esa auditoria ya esta promovida a 01_foundations?
Que parte falta institucionalizar?
Que evidencia moderna falta?
```

Si existe auditoria historica profunda, el agente debe crear o actualizar primero:

```text
inspection_dossiers/<dataset>/integration_notes.md
```

o un promotion gap equivalente, con:

- archivos historicos leidos;
- certification files leidos;
- estado actual en `01_foundations`;
- verdades historicas ya promovidas;
- verdades historicas pendientes de promocion;
- archivos que se van a crear/modificar;
- rutas protegidas no tocadas;
- condicion de parada.

Sin este preflight, el dataset no puede pasar a `modern_dossier_partial` ni `modern_dossier_complete`.

## 3. Rutas protegidas

Los agentes no deben modificar:

- `E:/TSIS/data/*`
- `C:/TSIS_Data/data/*`
- `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/`
- `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/data/`
- `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/run/`
- `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/`

Esas rutas se leen como evidencia y provenance.
El trabajo nuevo debe vivir en:

- `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/`
- `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/inspection/<dataset>/`

## 4. Paquete minimo por dataset

Para un dataset `<dataset>`, el agente debe crear o actualizar:

```text
01_foundations/canonical_schemas/<dataset>/
01_foundations/contract_registry/dataset_contracts/<dataset>_dataset_contract_v0_1.md
01_foundations/dataset_registry/<dataset>/<dataset>_registry_entry.yaml
01_foundations/data_consumption_policies/<dataset>_consumption_policy.md
01_foundations/validators/<dataset>/<dataset>_validators.md
01_foundations/inspection_dossiers/<dataset>/README.md
01_foundations/inspection_dossiers/<dataset>/<dataset>_inspection_readout_v0_1.md
01_foundations/inspection_dossiers/<dataset>/build_<dataset>_inspection_pack.md
01_foundations/inspection_dossiers/<dataset>/evidence_assets/
01_foundations/inspection_dossiers/<dataset>/integration_notes.md
scripts/inspection/<dataset>/
```

Si el dataset no requiere una pieza, el agente debe explicarlo en el README local y en el readout.

## 5. Evidence assets obligatorios

Cada dataset debe tener assets activos bajo:

```text
inspection_dossiers/<dataset>/evidence_assets/
```

Minimo:

- `physical_root_audit/`
- `historical_source_inventory/`
- `population_summary/`
- `case_manifest/` cuando existan casos;
- `visuals/` cuando haya imagenes o graficos;
- `run_manifest.json` o equivalente si hubo generador.
- manifest de notebooks si existen notebooks inspectores activos;
- manifest de visuales si se exportan imagenes.

Los assets deben estar consumidos por markdown, notebooks inspectores o contracts.
No debe haber assets mudos.

## 5.1. Notebooks inspectores

Si el dataset requiere inspeccion humana granular, el paquete debe incluir notebook inspector o justificar por que no aplica.

Un notebook inspector sirve para:

- navegar casos;
- usar widgets/selectores;
- abrir ticker/date/month/familia/estado;
- leer outputs ejecutados;
- comprobar tablas e imagenes;
- y ampliar evidencia forense.

Un notebook inspector no debe ser:

- almacen de codigo pesado;
- unica fuente de una conclusion;
- sustituto del readout;
- sustituto de manifests;
- ni output temporal sin version.

La logica pesada y estable debe vivir en scripts/builders residentes. El notebook debe actuar como lanzadera, lector o inspector.

Si una conclusion nace dentro de un notebook, debe quedar promovida a:

- readout;
- casepack;
- visual pack;
- manifest;
- tabla exportada;
- o policy/contract.

## 5.2. Imagenes y lectura visual

Cuando existan imagenes, cada imagen relevante debe estar:

- versionada o generada por builder residente;
- listada en manifest;
- enlazada o incrustada en markdown institucional;
- interpretada individualmente.

Formato obligatorio:

```text
Que muestra
Responde
No responde
Consecuencia
```

La interpretacion debe salir de la lectura real de la imagen.

Reglas:

- nombrar donde se ve el fenomeno si es visible;
- declarar si la imagen no prueba bien el fenomeno;
- pedir visual o tabla complementaria si el panel actual es insuficiente;
- no inferir causalidad solo por nombre de bucket;
- no usar imagenes como decoracion.

## 6. Dossier inspector

Cada dossier debe seguir orden general-a-particular:

```text
mapa poblacional
-> distribuciones y masas
-> coverage o presencia esperada
-> familias de evidencia
-> casos individuales
-> decision de consumo
```

Cuando haya graficos o imagenes, cada pieza debe declarar:

- `Que muestra`
- `Responde`
- `No responde`
- `Consecuencia`

Si el agente no puede generar visuals en una primera pasada, debe crear un gap audit y marcar el dataset como pendiente de visual pack.

Un mapa poblacional no sustituye casos forenses.
Una muestra de casos no sustituye mapa poblacional.

## 7. Scripts residentes

Todo script usado para generar assets aceptados debe vivir dentro del proyecto:

```text
01_TSIS_backtest_SmallCaps/scripts/inspection/<dataset>/
```

Prohibido aceptar como final outputs generados solo desde:

- `C:/Users/...`
- `C:/tmp`
- Downloads
- notebooks temporales no versionados
- chat-only scripts

## 8. Registry entry minima

Cada `*_registry_entry.yaml` debe parsear como YAML y contener:

- dataset identity;
- status;
- physical layout;
- source lineage;
- artifacts;
- coverage snapshot;
- quality policy;
- allowed consumers;
- evidence references;
- known limitations;
- notes.

Si hay estado `pending_modern_visual_pack`, debe declararse explicitamente.

## 9. Consumption policy minima

Cada policy debe separar:

- permitted consumers;
- restricted consumers;
- prohibited consumers;
- temporal leakage rules;
- flags obligatorias;
- usos no implicados;
- condiciones de promocion futura.

Regla:

```text
presencia fisica != consumo permitido
```

## 10. Validators minimos

Cada validator contract debe declarar:

- unidad de validacion;
- inputs requeridos;
- familias de checks;
- hard failures;
- review states;
- outputs esperados;
- pass criteria;
- non-goals;
- promotion implications.

Si todavia no existe runner ejecutable, el documento debe decirlo.
Si se crea runner, debe escribir outputs reproducibles bajo `evidence_assets/`.

## 11. Integration notes

Cada agente por dataset debe crear:

```text
inspection_dossiers/<dataset>/integration_notes.md
```

Debe contener:

- archivos creados;
- archivos modificados;
- roots fisicos leidos;
- rutas protegidas no tocadas;
- auditoria historica leida;
- notebooks leidos o creados;
- visuales generados y como se interpretaron;
- indices/changelog que recomienda actualizar;
- estado final propuesto;
- riesgos;
- gaps;
- tests o verificaciones ejecutadas;
- si requiere intervencion humana.

El integrador final usa estos notes para actualizar indices compartidos y changelog.

## 12. Estados de cierre

Estados permitidos:

- `not_started`
- `inventory_only`
- `foundation_minimal`
- `modernization_gap_documented`
- `modern_dossier_partial`
- `modern_dossier_complete`
- `blocked_needs_human_decision`
- `not_consumable_no_active_consumer`

Prohibido usar:

- `done`
- `clean`
- `ok`
- `closed`

sin declarar para que consumidor y bajo que contrato.

## 13. Criterio de aceptacion final

El integrador final puede marcar un dataset como `modern_dossier_complete` solo si:

- tiene paquete minimo o excepcion justificada;
- el YAML parsea;
- no hay referencias rotas;
- no hay `TODO`/`TBD` sin bloquear formalmente;
- no hay scripts temporales fuera del proyecto;
- los assets estan consumidos por markdown o notebook inspector;
- los visuales relevantes estan explicados con `Que muestra / Responde / No responde / Consecuencia`;
- los notebooks, si existen, no son la unica fuente de la conclusion;
- los estados de consumo no sobrepromueven el dataset;
- el changelog registra el hito.

## 14. Regla final

El Harness debe dejar a los agentes menos libertad de formato, no mas.

La excelencia aqui no es producir muchos markdowns.
Es producir evidencia verificable, localizable, versionada y consumible por otros agentes sin reinterpretar la auditoria desde cero.
