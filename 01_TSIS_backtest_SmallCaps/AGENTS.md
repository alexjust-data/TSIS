# Contrato Local de Agentes - Modulo 01

## 1. Rol

Este documento es el contrato operativo local para agentes que trabajen dentro de:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps`

Refina la gobernanza raiz de TSIS para el modulo historico de research y backtesting.

Si una interpretacion local entra en conflicto con un contrato raiz de TSIS, manda el contrato raiz.

## 2. Identidad del modulo

Este modulo es la capa historica de investigacion y simulacion de TSIS.

Su funcion es:

- construir datasets y universos historicos defendibles;
- auditar y certificar calidad de datos;
- formalizar estados de mercado y objetos de research;
- simular ejecucion con realismo;
- producir evidencia reproducible para promocion o cuarentena;
- soportar capas downstream live y RL sin redefinir silenciosamente la semantica upstream.

Los agentes no deben tratar este modulo como:

- un workspace generico de notebooks;
- un contenedor informal de scripts;
- o un sandbox libre para ideas de estrategia sin contrato de datos.

## 3. Fase actual

La fase actual del modulo es:

`consolidacion institucional`

La prioridad mas alta es:

- preservar memoria cientifica;
- formalizar contratos;
- formalizar politicas;
- construir la capa operativa institucional.

No es la fase prioritaria para:

- expandir RL;
- multiplicar features nuevas;
- abrir muchas estrategias nuevas;
- profundizar simuladores antes de cerrar contratos.

## 4. Zonas protegidas

Las siguientes rutas estan congeladas estructuralmente durante la fase actual:

- `01_research/01_auditoria_RAW_DATA/`
- `data/`
- `run/`
- `runs/`

Los agentes NO DEBEN:

- reorganizar esos arboles;
- renombrarlos;
- colapsarlos en una estructura nueva;
- reescribir evidencia historica in place;
- ni hacer refactors de limpieza dentro de ellos sin instruccion explicita.

Estas rutas contienen:

- lineage de auditoria;
- evidencia de certificacion;
- historia runtime;
- contexto de reproducibilidad.

La congelacion debe leerse como congelacion estructural por defecto.

Solo se admite intervencion minima de ejecutabilidad cuando:

- exista una necesidad operativa explicita;
- no se altere la semantica institucional del material historico;
- la intervencion quede acotada a restaurar kernel, paths, carga o reejecucion trazable;
- y se deje constancia local en un `LOCAL_MAINTENANCE.md` dentro del bloque afectado indicando que se toco, por que y que cambio concreto se hizo.

Si esa intervencion tuvo impacto institucional, operativo o de reproducibilidad, tambien debe reflejarse en `CHANGELOG.md`.

## 5. Estrategia correcta de consolidacion

La estrategia correcta para este modulo es:

`preservar la estructura actual de evidencia + construir una capa institucional al lado`

Los agentes deben asumir que el primer gran objetivo de construccion es:

- `01_foundations/`

No deben asumir que el primer movimiento correcto es refactorizar el arbol de research.

## 6. Zonas estructurales del modulo

Los agentes deben pensar este modulo en cuatro zonas.

### Evidencia preservada

- `00_cto/`
- `01_research/`

### Artefactos protegidos

- `data/`
- `run/`
- `runs/`

### Implementacion estable

- `src/`
- `scripts/`
- `configs/`
- `docs/`
- `tests/`

### Nueva capa institucional

- `01_foundations/`

## 7. Como tratar auditoria y certificacion

`01_research/01_auditoria_RAW_DATA/00_data_certification/` contiene conocimiento institucional valioso pero distribuido.

Los agentes deben tratarlo como:

- memoria cientifica preservada;
- fuente de evidencia para nuevos contratos;
- razonamiento historico que debe encapsularse, no borrarse.

Por tanto:

- no reescribir closeouts solo para homogeneizar estilo;
- no aplastar la historia de auditoria en un arbol nuevo "mas limpio";
- no reinterpretar conclusiones silenciosamente sin crear un contrato nuevo explicito.

El movimiento correcto es:

- referenciar evidencia existente;
- extraer conclusiones estables;
- formalizarlas en `01_foundations/`;
- dejar intacta la evidencia historica.

## 8. Prioridades de construccion

Los agentes deben priorizar:

1. documentos locales de gobernanza
2. `01_foundations/module_contracts/`
3. dataset registry
4. data consumption policies
5. canonical schemas
6. ontology
7. promotion states
8. lineage
9. validators
10. contract registry

## 8.1 Lectura obligatoria de infraestructura de datos y precio

Antes de trabajar con datasets, price views, corporate actions, reconciliacion externa, backtest o ML, los agentes deben leer tambien:

1. `01_foundations/module_contracts/data_storage_topology_and_target_state.md`
2. `01_foundations/module_contracts/event_families_and_reference_inventory.md`
3. `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`
4. `01_foundations/module_contracts/price_views_registry.md`
5. `01_foundations/module_contracts/corporate_actions_adjustment_methodology.md`
6. `01_foundations/module_contracts/external_price_comparison_caveats.md`
7. `01_foundations/module_contracts/policy_explanation_standard.md`

La razon es institucional:

- el modulo no contiene un unico "precio";
- no contiene una unica familia de market data;
- y no permite comparar series externas o internas sin declarar antes su semantica.

Por tanto, ningun agente debe abrir un trabajo de:

- `daily`
- `quotes`
- `trades`
- `1m`
- backtest
- ML
- o reconciliacion externa

sin haber identificado primero:

- que familia de dato esta consumiendo;
- que vista de precio usa;
- que corporate actions pueden afectarla;
- y si la comparacion implicada es `raw`, `split_normalized`, `adjusted` o solo `adjusted_proxy`.

## 8.2 Regla obligatoria para inspeccion y evidencia visual

Cuando un agente construya o actualice:

- `inspection_readout`
- `good_justification`
- `flagged_case_evidence_packs`
- `bad_case_evidence_packs`
- `coverage_case_evidence_packs`
- notebooks de inspeccion
- o widgets/selectores visuales

debe aplicar la regla de:

- `que muestra`
- `responde`
- `no responde`
- `consecuencia`

para cada:

- grafico;
- tabla;
- ejemplo;
- familia de casos;
- y capa de evidencia.

No basta con describir la imagen.

Tampoco basta con listar nombres de buckets, files o atributos tecnicos.

La pieza correcta de evidencia debe dejar claro:

- que preguntas permite contestar;
- que preguntas no permite contestar;
- y que decision metodologica u operacional cambia.

La politica detallada vive en:

- `01_foundations/module_contracts/inspection_dossier_model.md`

## 9. Notebooks

Los notebooks dentro de este modulo siguen siendo validos para:

- evidencia historica;
- razonamiento exploratorio;
- soporte de closeout;
- diagnostico visual.

No deben tratarse como automaticamente obsoletos.

Las conclusiones estables deben promoverse a:

- contratos;
- schemas;
- policies;
- validators;
- o entradas de registry.

## 10. Regla general de higiene de artefactos

Los agentes deben asumir que todo folder, file, output o derivado que ya no forme parte del flujo activo del modulo es ruido operacional salvo que este explicitamente archivado.

Regla:

- si ya no esta en uso, debe eliminarse;
- si conserva valor historico, metodologico o de reproducibilidad, debe archivarse;
- y ese archivado debe quedar anotado explicitamente en su lugar.

Los agentes no deben dejar:

- carpetas viejas y nuevas con el mismo rol activo;
- manifests obsoletos mezclados con manifests vigentes;
- exports historicos que ya no correspondan a la politica actual;
- ni residuos "por si acaso" cuando ya existe una carpeta activa canonicamente gobernada.

La presencia de residuos no archivados degrada:

- trazabilidad;
- legibilidad;
- y capacidad de inspeccion institucional.

## 11. Areas de alta severidad

Dentro de este modulo, deben tratarse como `HIGH` o `CRITICAL` por defecto:

- semantica de calidad de datasets;
- traduccion de auditoria a certificacion;
- definiciones `good/review/bad`;
- politicas de consumo como `backtest_core` y `ml_flagged`;
- schemas canonicos;
- semantica de elegibilidad del universo;
- semantica de eventos o ejecucion consumida downstream.

## 12. Regla final

Si un agente tiene que elegir entre:

- dejar el arbol mas limpio;
- preservar evidencia cientifica historica;
- o construir contratos operativos explicitos;

la opcion correcta es:

`preservar evidencia y construir contratos`

## Mandatory certification source reading

- `01_foundations/module_contracts/auditoria_and_certification_source_hierarchy.md` when working any certified block (`daily`, `quotes`, `trades`).
