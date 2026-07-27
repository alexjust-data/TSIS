# TSIS

TSIS is an institutional-grade, agent-first Scientific Discovery Engine focused on:

- microcap and smallcap market structure;
- event-driven and state-based market modeling;
- reproducible research experiments;
- evidence, validation and knowledge promotion;
- classic backtesting and strategy research;
- live trading infrastructure;
- offline reinforcement learning preparation;
- autonomous candidate generation under validation gates.

## 0. Regla inicial obligatoria de comunicacion `English`

Si un mensaje del humano empieza por `English`, `ENGLISH` o `english`, con o sin dos puntos inmediatamente despues, el agente MUST traducir primero al ingles exclusivamente el texto del humano posterior a ese marcador.

La primera linea de la respuesta MUST ser:

```text
English: <traduccion al ingles del contenido posterior a ENGLISH>
```

Esa linea debe aparecer antes de cualquier respuesta, analisis, herramienta, pregunta de aclaracion, explicacion, accion o pensamiento visible.

Despues de escribir la traduccion, el agente debe continuar respondiendo normalmente al contenido del mensaje en el idioma normal de la conversacion.

Importante: `English` / `ENGLISH` / `english` NO significa que la respuesta del agente deba estar en ingles. Solo obliga a traducir primero la frase del humano.

Si el humano escribe literalmente `English answer`, el agente MUST responder en ingles. La respuesta en ingles debe ser la traduccion fiel de la respuesta que habria dado en espanol, manteniendo el mismo contenido, alcance y nivel de detalle.

Esta regla aplica siempre, en cualquier modulo de TSIS y para cualquier agente futuro.

# TSIS AGENTS Contract

## 1. Rol de este documento

`AGENTS.md` es el contrato operativo persistente entre:

- humanos;
- agentes de codigo;
- agentes de research;
- futuros sistemas autonomos que trabajen dentro de TSIS.

No es una nota breve.
No es una sugerencia.
Es la puerta de entrada operativa al repositorio.

Todo agente debe comportarse como si el repositorio fuera su unica memoria fiable.

---

## 1.1 Nota humana de arranque

`START_HERE.md` es la primera nota operativa que debe leer el humano al abrir TSIS.

No sustituye este contrato. Todo agente debe seguir obedeciendo el orden de lectura obligatorio definido en este documento y en los contratos locales aplicables.

---

## 2. Repository System Map

TSIS esta organizado como un ecosistema con autoridad raiz, laboratorio transversal, modulos operativos y data roots pesados:

- `00_CTO`: filosofia, arquitectura, mapas y autoridad.
- `00_CTO_APPLIED_ARCHITECTURE`: arquitectura aplicada y handoffs de ingenieria gobernada.
- `01_TSIS_DATA_FOUNDATION`: auditoria, certificacion, contratos, policies, validators, dossiers y outputs gobernados de Data Foundation.
- `02_TSIS_BACKTEST_ENGINE`: futura implementacion del backtester profesional TSIS; consume Data Foundation y arquitectura CTO.
- `03_TSIS_Lab`: contratos, registros, plantillas y experimentos cientificos reproducibles.
- `04_TSIS_webSocket_SmallCaps`: operacion live/shadow y procesamiento event-driven.
- `05_TSIS_Offline_RL`: aprendizaje secuencial sobre estados/outcomes gobernados.
- `06_TSIS_Trading_voice`: Trading Decision Intelligence / proceso de decision del trader.
- `G:/TSIS/data`: outputs pesados, materializaciones y roots fisicos.

Los agentes deben respetar los limites entre capas, modulos y contratos institucionales. Para resolver rutas antiguas, leer `PATH_MIGRATION_2026_07_22.md`.

---

## 3. Mandatory Reading Order

Antes de modificar este repositorio, todo agente debe leer en este orden:

1. `PATH_MIGRATION_2026_07_22.md`
2. `PROJECT_OPERATING_SYSTEM.md`
3. `PROJECT_RULES.md`
4. `VERSIONING_STANDARDS.md`
5. `RESEARCH_PHILOSOPHY.md`
6. `00_CTO/TSIS_LAB_ARCHITECTURE_v3.md`
7. `03_TSIS_Lab/README.md`
8. `G:/TSIS/data/README.md`
9. `LOCAL_RULES.md` de la carpeta o capa que vaya a modificar

La lectura obligatoria de arquitectura vive en `00_CTO/TSIS_LAB_ARCHITECTURE_v3.md`.

`G:/TSIS/data/README.md` es lectura base obligatoria porque define el plano fisico de datos. Para cualquier trabajo con minutos/1m, scanners intradia, backtests intradia, reparaciones de velas o price views derivados de minutos, ese README fija que la raiz fisica canonica es `G:/TSIS/data/ohlcv_1m` y que el raw no debe tratarse como corregido in place. El motivo es evitar que se repita la ambiguedad que llevo al incidente de velas 1m imposibles y a la reparacion quote-guarded LT1B.

Si una decision local contradice un documento de nivel superior, manda el documento de nivel superior salvo que exista una excepcion explicita y documentada.

---

## 4. Local Rules Precedence

`LOCAL_RULES.md` puede introducir restricciones locales mas estrictas.

Las reglas locales pueden refinar el comportamiento dentro de una capa o carpeta, pero no pueden violar los estandares institucionales de nivel superior.

---

## 5. Que debe entender un agente antes de tocar nada

Todo agente debe asumir que TSIS es:

- un `Scientific Discovery Engine` cuantitativo institucional en construccion;
- un repositorio `agent-first`;
- un sistema multi-modulo y multi-etapa;
- un stack basado en trazabilidad, reproducibilidad y semantica explicita;
- un laboratorio donde `research_experiment` es la unidad cientifica central;
- un proyecto donde `research`, `backtest clasico`, `live`, `offline RL` y `AlphaEvolve` deben convivir sin contaminarse.

Todo agente debe entender tambien que:

- el mercado no se modela solo como precio-tiempo;
- los datos no son homogeneos ni intercambiables;
- la microestructura, los eventos, los estados, los outcomes y la causalidad importan;
- la ejecucion realista y el riesgo externo importan tanto como la senal;
- AlphaEvolve propone candidatos, pero no valida conocimiento;
- y ningun resultado debe depender de conocimiento escondido en conversaciones.

---

## 6. No Hidden State Assumption

Los agentes deben asumir que:

- los supuestos no documentados son inseguros;
- las convenciones implicitas no son autoritativas;
- el estado local oculto no es fiable;
- y cualquier conocimiento importante que no viva en el repositorio no debe tratarse como contrato operativo.

---

## 7. Reglas operativas no negociables

Todo agente MUST:

- trabajar en rama, nunca directamente sobre `main`;
- mantener cambios pequenos y semanticamente claros;
- preservar la separacion entre capas del sistema;
- actualizar manifests, changelogs y documentacion cuando el cambio altere semantica operativa;
- respetar naming canonico, versionado logico y contratos de schema;
- dejar suficiente evidencia para trazabilidad tecnica posterior;
- tratar notebooks como exploracion, no como autoridad productiva final;
- tratar datasets y outputs institucionales como artefactos gobernados, no como ficheros casuales;
- convertir hipotesis ejecutables en `research_experiment` cuando pasen de conversacion a trabajo reproducible.

Todo agente MUST NOT:

- introducir cambios estructurales silenciosos;
- sobrescribir datasets importantes sin nueva version logica o sin justificacion explicita;
- promocionar logica exploratoria como institucional sin barrera de promocion;
- usar `main` como sandbox;
- dejar reglas importantes solo en prompts o conversaciones;
- mezclar en un solo cambio refactors, features, fixes y promociones institucionales sin separacion clara;
- tratar `sampling_probe` como evento validado;
- tratar `evidence_report` como conocimiento validado;
- tratar `representation_candidate` como canonical state;
- tratar una salida AlphaEvolve como verdad por tener buen score.

---

## 8. Filosofia de trabajo por capas

TSIS separa estrictamente:

- raw data;
- reference/universe;
- canonical observables;
- canonical state / event_state;
- outcomes separados;
- research experiments;
- evidence reports;
- knowledge objects;
- validated knowledge;
- event families / representations / transitions;
- estrategias o politicas;
- ejecucion;
- reporting;
- ML/RL/AlphaEvolve.

Un agente no debe romper esta separacion.

Reglas minimas:

- `features` no deben contener logica de senal sin contrato;
- `event_engine` no debe asumir ejecucion;
- `market_state/event_state` no deben contener outcomes futuros;
- `outcomes` deben permanecer separados de X;
- `strategy_engine` no debe redefinir silenciosamente la semantica de datos upstream;
- `execution` no debe contaminar la definicion de features o estados;
- `ML/RL` no debe inventar source of truth distinta a la gobernada por manifests y policies oficiales;
- `AlphaEvolve` no debe promocionar conocimiento, reescribir truth upstream ni modificar gates de leakage/calidad/holdout; solo puede proponer candidate research experiments bajo contrato.

---

## 9. Policy de versionado para agentes

Todo agente debe obedecer `VERSIONING_STANDARDS.md` como norma obligatoria.

En particular, un agente debe:

- crear rama antes de modificar estructura relevante;
- usar commits semanticos;
- respetar `Semantic Versioning` cuando aplique;
- no reescribir artefactos historicos institucionales silenciosamente;
- no introducir breaking changes sin actualizacion explicita de manifests, changelogs e impacto downstream;
- distinguir entre artefactos runtime y artefactos institucionales;
- preservar experimental containment;
- no tratar outputs exploratorios como outputs oficiales;
- versionar `research_experiment`, `sampling_probe`, `parameter_sweep`, `evidence_report`, `knowledge_object` y runs AlphaEvolve/autonomous generator cuando existan.

Si un agente duda sobre si un cambio exige:

- `version bump`
- `manifest update`
- `CHANGELOG update`
- `migration note`

entonces debe asumir que probablemente si, y explicitar la duda en lugar de omitirla silenciosamente.

---

## 10. Institutional vs Runtime Artifacts

Los agentes deben distinguir entre:

- artefactos institucionales;
- artefactos exploratorios;
- artefactos runtime.

Los artefactos runtime no son source of truth.
No deben confundirse con outputs promocionados ni con evidencia institucional.

---

## 11. Reglas especificas para datasets y outputs

Todo agente debe asumir que el mayor riesgo de degradacion del sistema no es solo el codigo, sino la ambiguedad sobre datasets, outputs y semantica historica.

Por tanto:

- todo dataset relevante debe tener identidad logica;
- todo output institucional debe poder enlazarse a un `run_id`, config, commit y dataset version;
- ningun dataset semanticamente nuevo debe reutilizar silenciosamente el nombre de uno anterior;
- ningun output promocionado debe tratarse como cache temporal;
- los artefactos runtime no deben confundirse con artefactos institucionales.

---

## 12. Notebooks

Los notebooks son validos para:

- exploracion;
- diseno metodologico;
- analisis visual;
- drilldown forense;
- prototipado inicial.

Los notebooks no son validos como sede final de:

- logica productiva canonica;
- contratos oficiales;
- validadores institucionales;
- politicas de ejecucion;
- semantica definitiva de datasets.

Cuando una logica deja de ser exploratoria, el agente debe migrarla a:

- `src/`
- `pipelines/`
- `validators/`
- `scripts/`
- `configs/`

segun corresponda.

---

## 13. Reproducibilidad minima exigida

Todo agente debe trabajar como si cualquier resultado fuera a ser auditado despues por otro humano u otro agente.

Por tanto, todo resultado relevante debe poder responder:

- que codigo;
- que commit;
- que dataset;
- que version de dataset;
- que config;
- que periodo;
- que politica de calidad;
- que run id;
- que output;
- que experimento o contrato lo gobierna;
- y que nivel de promocion tiene.

Si eso no puede reconstruirse, el resultado no debe presentarse como institucional.

Ademas, toda operacion larga que un agente ejecute o deje preparada para un humano debe cumplir:

- `LONG_RUNNING_OPERATIONS_CONTRACT.md`

Ningun agente debe recomendar una copia masiva, materializacion, auditoria, normalizacion, reparacion, build Graphify, entrenamiento o evaluacion larga sin pre-manifest, PID, heartbeat, timestamps, log vivo, monitor separado y final manifest.

---

## 14. Promocion institucional

Un agente no debe confundir:

- `exploratory`
- `provisional`
- `validated`
- `institutional`
- `draft`
- `executed`
- `evidence_ready`
- `candidate_knowledge`
- `validated_knowledge`
- `falsified`
- `quarantined`
- `archived`

Nada se considera `institutional` solo porque haya producido un resultado atractivo.

Para promocion institucional debe existir, como minimo:

- manifest;
- owner;
- naming estable;
- changelog cuando aplique;
- validacion documentada;
- reproducibilidad suficiente;
- compatibilidad explicita con contratos downstream.

---

## 15. Manejo de cambios de alta severidad

Cuando el agente toque algo de severidad `HIGH` o `CRITICAL`, debe actuar con disciplina reforzada.

Ejemplos tipicos:

- schema canonico;
- ontologia de eventos;
- definicion del universo;
- semantica oficial de datasets;
- `research_experiment_contract`;
- `scientific_validation_pipeline`;
- reward RL institucional;
- simulador de ejecucion;
- politicas de calidad centrales;
- gates de leakage/calidad/holdout;
- autoridad AlphaEvolve/autonomous generator.

En esos casos, el agente debe:

- evitar cambios colaterales innecesarios;
- documentar la intencion con claridad;
- actualizar manifests y changelogs pertinentes;
- senalar impacto downstream;
- no ocultar breaking changes;
- y no mezclar el cambio con otras refactorizaciones oportunistas.

---

## 16. Filosofia de enforcement

Las reglas de TSIS no deben depender solo de buena voluntad.

Los agentes deben asumir que el sistema evolucionara hacia enforcement automatico mediante:

- CI checks;
- schema validation;
- naming validation;
- manifest consistency checks;
- release gates;
- promotion barriers.

Por tanto, todo cambio debe disenarse para sobrevivir no solo a revision humana, sino a futura validacion automatica.

---

## 17. Si existe duda, manda la trazabilidad

Si un agente duda entre:

- rapidez o trazabilidad;
- conveniencia local o semantica global;
- experimento util o contaminacion institucional;
- shortcut o reproducibilidad;

la eleccion correcta es la que preserve trazabilidad, semantica y reproducibilidad.

---

## 18. Regla final

Nunca debe quedar conocimiento estructural importante:

- solo en conversaciones;
- solo en prompts;
- solo en memoria humana;
- solo en notebooks temporales;
- solo en outputs sin contexto.

Todo conocimiento importante de TSIS debe vivir:

- dentro del repositorio;
- versionado;
- documentado;
- trazable;
- legible por agentes;
- y reconstruible por humanos.

Ese es el estandar operativo de agentes en TSIS.

