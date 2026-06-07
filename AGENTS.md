# TSIS

TSIS is an institutional-grade, agent-first quantitative research system focused on:

- microcap and smallcap market structure;
- event-driven modeling;
- execution realism;
- reproducible research;
- live trading infrastructure;
- offline reinforcement learning preparation.

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
- agentes de código;
- agentes de research;
- futuros sistemas autónomos que trabajen dentro de TSIS.

No es una nota breve.
No es una sugerencia.
Es la puerta de entrada operativa al repositorio.

Todo agente debe comportarse como si el repositorio fuera su única memoria fiable.

---

## 2. Repository Modules

TSIS está organizado como un monorepo compuesto por:

- `01_TSIS_backtest_SmallCaps`
- `02_TSIS_webSocket_SmallCaps`
- `03_TSIS_Offline_RL`

Los agentes deben respetar los límites entre módulos y sus contratos institucionales.

---

## 3. Mandatory Reading Order

Antes de modificar este repositorio, todo agente debe leer en este orden:

1. `PROJECT_OPERATING_SYSTEM.md`
2. `PROJECT_RULES.md`
3. `VERSIONING_STANDARDS.md`
4. `ARCHITECTURE_OVERVIEW.md`
5. `RESEARCH_PHILOSOPHY.md`
6. `LOCAL_RULES.md` de la carpeta o capa que vaya a modificar

Si una decisión local contradice un documento de nivel superior, manda el documento de nivel superior salvo que exista una excepción explícita y documentada.

---

## 4. Local Rules Precedence

`LOCAL_RULES.md` puede introducir restricciones locales más estrictas.

Las reglas locales pueden refinar el comportamiento dentro de una capa o carpeta, pero no pueden violar los estándares institucionales de nivel superior.

---

## 5. Qué debe entender un agente antes de tocar nada

Todo agente debe asumir que TSIS es:

- un sistema cuantitativo institucional en construcción;
- un repositorio `agent-first`;
- un sistema multi-módulo y multi-etapa;
- un stack basado en trazabilidad, reproducibilidad y semántica explícita;
- un proyecto donde `research`, `live` y `offline RL` deben convivir sin contaminarse.

Todo agente debe entender también que:

- el mercado no se modela solo como precio-tiempo;
- los datos no son homogéneos ni intercambiables;
- la microestructura, los eventos y la causalidad importan;
- la ejecución realista y el riesgo externo importan tanto como la señal;
- y ningún resultado debe depender de conocimiento escondido en conversaciones.

---

## 6. No Hidden State Assumption

Los agentes deben asumir que:

- los supuestos no documentados son inseguros;
- las convenciones implícitas no son autoritativas;
- el estado local oculto no es fiable;
- y cualquier conocimiento importante que no viva en el repositorio no debe tratarse como contrato operativo.

---

## 7. Reglas operativas no negociables

Todo agente MUST:

- trabajar en rama, nunca directamente sobre `main`;
- mantener cambios pequeños y semánticamente claros;
- preservar la separación entre capas del sistema;
- actualizar manifests, changelogs y documentación cuando el cambio altere semántica operativa;
- respetar naming canónico, versionado lógico y contratos de schema;
- dejar suficiente evidencia para trazabilidad técnica posterior;
- tratar notebooks como exploración, no como autoridad productiva final;
- tratar datasets y outputs institucionales como artefactos gobernados, no como ficheros casuales.

Todo agente MUST NOT:

- introducir cambios estructurales silenciosos;
- sobrescribir datasets importantes sin nueva versión lógica o sin justificación explícita;
- promocionar lógica exploratoria como institucional sin barrera de promoción;
- usar `main` como sandbox;
- dejar reglas importantes solo en prompts o conversaciones;
- mezclar en un solo cambio refactors, features, fixes y promociones institucionales sin separación clara.

---

## 8. Filosofía de trabajo por capas

TSIS separa estrictamente:

- raw data;
- reference/universe;
- features;
- eventos;
- estados;
- estrategias;
- ejecución;
- reporting;
- ML/RL.

Un agente no debe romper esta separación.

Reglas mínimas:

- `features` no deben contener lógica de señal;
- `event_engine` no debe asumir ejecución;
- `strategy_engine` no debe redefinir silenciosamente la semántica de datos upstream;
- `execution` no debe contaminar la definición de features;
- `ML/RL` no debe inventar source of truth distinta a la gobernada por manifests y policies oficiales.

---

## 9. Policy de versionado para agentes

Todo agente debe obedecer `VERSIONING_STANDARDS.md` como norma obligatoria.

En particular, un agente debe:

- crear rama antes de modificar estructura relevante;
- usar commits semánticos;
- respetar `Semantic Versioning` cuando aplique;
- no reescribir artefactos históricos institucionales silenciosamente;
- no introducir breaking changes sin actualización explícita de manifests, changelogs e impacto downstream;
- distinguir entre artefactos runtime y artefactos institucionales;
- preservar experimental containment;
- no tratar outputs exploratorios como outputs oficiales.

Si un agente duda sobre si un cambio exige:

- `version bump`
- `manifest update`
- `CHANGELOG update`
- `migration note`

entonces debe asumir que probablemente sí, y explicitar la duda en lugar de omitirla silenciosamente.

---

## 10. Institutional vs Runtime Artifacts

Los agentes deben distinguir entre:

- artefactos institucionales;
- artefactos exploratorios;
- artefactos runtime.

Los artefactos runtime no son source of truth.
No deben confundirse con outputs promocionados ni con evidencia institucional.

---

## 11. Reglas específicas para datasets y outputs

Todo agente debe asumir que el mayor riesgo de degradación del sistema no es solo el código, sino la ambigüedad sobre datasets, outputs y semántica histórica.

Por tanto:

- todo dataset relevante debe tener identidad lógica;
- todo output institucional debe poder enlazarse a un `run_id`, config, commit y dataset version;
- ningún dataset semánticamente nuevo debe reutilizar silenciosamente el nombre de uno anterior;
- ningún output promocionado debe tratarse como cache temporal;
- los artefactos runtime no deben confundirse con artefactos institucionales.

---

## 12. Notebooks

Los notebooks son válidos para:

- exploración;
- diseño metodológico;
- análisis visual;
- drilldown forense;
- prototipado inicial.

Los notebooks no son válidos como sede final de:

- lógica productiva canónica;
- contratos oficiales;
- validadores institucionales;
- políticas de ejecución;
- semántica definitiva de datasets.

Cuando una lógica deja de ser exploratoria, el agente debe migrarla a:

- `src/`
- `pipelines/`
- `validators/`
- `scripts/`
- `configs/`

según corresponda.

---

## 13. Reproducibilidad mínima exigida

Todo agente debe trabajar como si cualquier resultado fuera a ser auditado después por otro humano u otro agente.

Por tanto, todo resultado relevante debe poder responder:

- qué código;
- qué commit;
- qué dataset;
- qué versión de dataset;
- qué config;
- qué período;
- qué política de calidad;
- qué run id;
- qué output;
- y qué nivel de promoción tiene.

Si eso no puede reconstruirse, el resultado no debe presentarse como institucional.

---

## 14. Promoción institucional

Un agente no debe confundir:

- `exploratory`
- `provisional`
- `validated`
- `institutional`

Nada se considera `institutional` solo porque haya producido un resultado atractivo.

Para promoción institucional debe existir, como mínimo:

- manifest;
- owner;
- naming estable;
- changelog cuando aplique;
- validación documentada;
- reproducibilidad suficiente;
- compatibilidad explícita con contratos downstream.

---

## 15. Manejo de cambios de alta severidad

Cuando el agente toque algo de severidad `HIGH` o `CRITICAL`, debe actuar con disciplina reforzada.

Ejemplos típicos:

- schema canónico;
- ontología de eventos;
- definición del universo;
- semántica oficial de datasets;
- reward RL institucional;
- simulador de ejecución;
- políticas de calidad centrales.

En esos casos, el agente debe:

- evitar cambios colaterales innecesarios;
- documentar la intención con claridad;
- actualizar manifests y changelogs pertinentes;
- señalar impacto downstream;
- no ocultar breaking changes;
- y no mezclar el cambio con otras refactorizaciones oportunistas.

---

## 16. Filosofía de enforcement

Las reglas de TSIS no deben depender solo de buena voluntad.

Los agentes deben asumir que el sistema evolucionará hacia enforcement automático mediante:

- CI checks;
- schema validation;
- naming validation;
- manifest consistency checks;
- release gates;
- promotion barriers.

Por tanto, todo cambio debe diseñarse para sobrevivir no solo a revisión humana, sino a futura validación automática.

---

## 17. Si existe duda, manda la trazabilidad

Si un agente duda entre:

- rapidez o trazabilidad;
- conveniencia local o semántica global;
- experimento útil o contaminación institucional;
- shortcut o reproducibilidad;

la elección correcta es la que preserve trazabilidad, semántica y reproducibilidad.

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

Ese es el estándar operativo de agentes en TSIS.
