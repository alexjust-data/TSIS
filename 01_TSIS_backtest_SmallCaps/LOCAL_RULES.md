# Reglas Locales - Modulo 01

## 0. Regla inicial obligatoria de comunicacion `English`

Cuando el humano escriba un mensaje que empiece por `English`, `ENGLISH` o `english`, con o sin dos puntos inmediatamente despues, el agente debe traducir primero al ingles exclusivamente el texto del humano posterior a ese marcador.

La primera linea de la respuesta debe ser:

```text
English: <traduccion al ingles del contenido posterior a ENGLISH>
```

Esta linea debe aparecer antes de cualquier otra respuesta, explicacion, analisis, accion, herramienta, pregunta o pensamiento visible.

Despues de esa traduccion inicial, el agente puede responder normalmente al contenido del mensaje en el idioma normal de la conversacion.

Importante: `English` / `ENGLISH` / `english` NO significa que la respuesta del agente deba estar en ingles. Solo obliga a traducir primero la frase del humano.

Si el humano escribe literalmente `English answer`, el agente debe responder en ingles. La respuesta en ingles debe ser la traduccion fiel de la respuesta que habria dado en espanol, manteniendo el mismo contenido, alcance y nivel de detalle.

Esta regla es obligatoria dentro de `01_TSIS_backtest_SmallCaps` y hereda de la gobernanza raiz de TSIS.

## 1. Alcance

Estas reglas gobiernan el trabajo dentro de:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps`

Refinan la politica raiz de TSIS para este modulo y son deliberadamente estrictas durante la fase de consolidacion institucional.

## 2. Prioridad local actual

La prioridad local actual es:

`consolidacion institucional del conocimiento auditado`

Eso significa:

- formalizacion de contratos;
- formalizacion de politicas;
- formalizacion de schemas;
- formalizacion de lineage;
- diseno de validators;
- endurecimiento de gobernanza.

No significa:

- embellecimiento de carpetas;
- limpieza historica;
- expansion prematura downstream.

## 3. Regla de no tocar

Las siguientes rutas estan congeladas estructuralmente:

- `01_research/01_auditoria_RAW_DATA/`
- `data/`
- `run/`
- `runs/`

Dentro de esas rutas no se debe:

- renombrar carpetas;
- mover archivos;
- colapsar notebooks;
- borrar outputs;
- normalizar material historico por estetica;
- ni hacer refactors de limpieza.

Cualquier excepcion requiere instruccion explicita.

La congelacion de estas rutas debe interpretarse como:

- congelacion estructural por defecto;
- y prohibicion de reescritura funcional salvo necesidad justificada.

Solo se admite intervencion minima de ejecutabilidad cuando concurran las siguientes condiciones:

- existe una necesidad operativa explicita;
- no se altera la semantica institucional del material historico;
- la intervencion queda trazable y acotada a restaurar acceso, paths, kernel o capacidad de reejecucion;
- y debe dejarse explicitamente anotado que se toco, por que se toco y que cambio concreto se hizo.

La forma preferida de dejar esa anotacion es:

- crear o actualizar un `LOCAL_MAINTENANCE.md` dentro del bloque historico afectado;
- y registrar tambien el cambio en `CHANGELOG.md` del modulo si tuvo impacto institucional, operativo o de reproducibilidad.

## 4. Preservar pero no reorganizar todavia

Las siguientes zonas deben preservarse y entenderse antes de cualquier intervencion estructural:

- `00_cto/`
- `01_research/02_reference_layer/`
- `01_research/03_universe_builder/`
- `01_research/04_feature_engine/`
- `01_research/05_event_engine/`
- `01_research/06_strategy_engine/`
- `01_research/07_execution_simulator/`
- `01_research/08_research_backtests/`
- `01_research/09_edge_statistico/`
- `01_research/10_regime_modeling/`
- `01_research/11_ml_preparation/`
- `02_infrastructure/`

Pueden mapearse y documentarse, pero no reorganizarse masivamente en la fase actual.

## 5. Donde debe vivir el trabajo nuevo

El trabajo institucional nuevo debe ir principalmente a:

- `01_foundations/`

Ese es el hogar por defecto para:

- module contracts;
- ontology;
- dataset registry;
- canonical schemas;
- data consumption policies;
- lineage maps;
- promotion state definitions;
- validators;
- contract registries.

## 6. Prioridad de escritura

Cuando haya que decidir donde escribir material nuevo:

- usar `01_foundations/` para contratos institucionales;
- usar `docs/` para documentacion secundaria explicativa;
- usar `src/` y `scripts/` para logica ejecutable;
- usar `01_research/` solo si el artefacto es genuinamente exploratorio o historico.

No colocar nuevo source of truth institucional dentro de arboles de auditoria preservados salvo instruccion explicita.

## 7. Archivos de gobernanza

`README.md`, `AGENTS.md`, `LOCAL_RULES.md` y `CHANGELOG.md` deben declarar explicitamente:

- la fase actual;
- las zonas no tocables;
- el principio de evidencia preservada;
- el rol de `01_foundations/`;
- como debe progresar el trabajo local.

Ademas, el modulo debe mantener como lectura obligatoria de infraestructura general:

- `01_foundations/module_contracts/data_storage_topology_and_target_state.md`
- `01_foundations/module_contracts/event_families_and_reference_inventory.md`
- `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`
- `01_foundations/module_contracts/price_views_registry.md`
- `01_foundations/module_contracts/corporate_actions_adjustment_methodology.md`
- `01_foundations/module_contracts/external_price_comparison_caveats.md`

Ningun trabajo serio de:

- market data
- corporate actions
- reconciliacion externa
- backtest
- ML
- o inspeccion institucional

debe abrirse sin haber pasado antes por esos documentos.

## 8. Regla para CHANGELOG

`CHANGELOG.md` de este modulo debe registrar:

- hitos institucionales del modulo;
- cambios semanticos en como opera el modulo;
- hitos de consolidacion o promocion;
- cambios de contratos con impacto downstream.

No debe registrar ruido trivial.

## 9. Regla general de higiene de artefactos

Todo folder, file, output o derivado que haya sido usado de forma transitoria y ya no forme parte del flujo activo del modulo debe tratarse como ruido operacional.

Regla:

- si ya no esta en uso, debe eliminarse;
- si sigue teniendo valor historico, metodologico o de reproducibilidad, debe archivarse;
- y ese archivado debe quedar explicitamente anotado en su lugar para que humanos y agentes no lo confundan con outputs activos.

No deben mantenerse en paralelo:

- carpetas viejas y nuevas que cumplan el mismo rol;
- outputs obsoletos mezclados con outputs activos;
- manifests viejos mezclados con manifests vigentes;
- ni exports historicos que ya no correspondan a la politica actual.

La carpeta activa debe reflejar solo:

- artefactos vigentes;
- manifests vigentes;
- y outputs realmente consumidos por los contratos, dossiers o pipelines institucionales actuales.

## 10. Regla para contenidos de Foundations

Cualquier cosa promovida a `01_foundations/` debe responder al menos una de estas preguntas:

- cual es el significado canonico de este objeto?
- quien puede consumirlo?
- que estado tiene?
- que schema lo gobierna?
- que lineage tiene?
- como se valida?

Si no responde ninguna, probablemente no pertenece a `01_foundations/`.

## 11. Regla para contratos

Los contratos escritos en este modulo deben preferir:

- semantica explicita;
- nombres estables;
- definiciones de estados finitos;
- consumidores permitidos;
- consecuencias operativas.

Evitar lenguaje vago cuando se define significado institucional.

## 12. Regla de reorganizacion

No debe empezar una reorganizacion estructural amplia hasta que:

- los archivos de gobernanza esten completos;
- exista `01_foundations/`;
- existan contratos basicos del modulo;
- y los limites entre preservado y nuevo sean explicitos.

## 13. Regla final

El trabajo local debe obedecer este orden:

`preservar evidencia -> formalizar contratos -> anadir validators -> reorganizar solo cuando este semantica y operativamente justificado`
