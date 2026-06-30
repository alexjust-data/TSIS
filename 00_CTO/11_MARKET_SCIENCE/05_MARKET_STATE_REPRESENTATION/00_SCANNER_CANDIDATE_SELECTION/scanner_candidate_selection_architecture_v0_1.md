# Scanner Candidate Selection Architecture v0.1

Fecha: 2026-06-30
Estado: candidate_policy
Scope: TSIS Market State Representation, Data Foundation, Trading Systems,
ML/RL, live readiness and AlphaEvolve evaluators

## 1. Tesis

TSIS necesita una capa explicita de seleccion de candidatos antes de construir
estados de mercado.

El objetivo no es producir una senal.

El objetivo es responder:

```text
Que instrumentos merecen ser inspeccionados bajo una definicion reproducible,
en una fecha/as-of concreta, y por que razon entraron en el conjunto?
```

Sin esta capa, el research queda expuesto a dos errores:

- mirar solo los casos que ya sabemos que funcionaron;
- confundir una hot list operativa con el universo real de discovery.

## 2. Lugar en la arquitectura

La cadena correcta es:

```text
audited raw / foundation components
-> scanner_candidate_selection
-> daily_scanner_candidates_table
-> market_state / event_state builders
-> strategy research
-> ML/RL / decision models / evaluators
```

El scanner vive antes del estado.

Un scanner row no es:

- `market_state`;
- `event_state`;
- setup detectado;
- estrategia;
- label;
- outcome;
- reward;
- fill;
- orden.

## 3. Por que no basta un scanner unico

TSIS separa dos preguntas distintas:

```text
Que habria visto el operador?
```

y:

```text
Que ticker empezaba a estar vivo aunque el operador todavia no lo hubiera visto?
```

La primera pregunta protege la reconstruccion de la realidad operativa humana.
La segunda protege el research contra sesgo de llegada tardia.

Por eso el framework v0.1 tiene dos definiciones:

```text
trade_station_like_scanner_v0_1
broad_in_play_discovery_scanner_v0_1
```

## 4. Relacion con Data Foundation

Data Foundation gobierna:

- schema;
- dataset contract;
- registry;
- consumption policy;
- validators;
- builder;
- configs versionadas;
- manifests de runs.

`00_CTO` no duplica esa autoridad.

Esta carpeta explica como y por que esos artefactos existen dentro del diseno
global de TSIS.

## 5. Relacion con estrategias

Las estrategias pueden consumir candidatos, pero no pueden redefinir el scanner
base como si fuera su propiedad.

Ejemplo:

```text
daily_scanner_candidates_table
-> das_candidate_state_table_experimental
-> DAS labels / diagnostics / outcomes
```

DAS puede prototipar estados propios, pero no debe escribir directamente
`market_state_table` ni declarar institucional un estado sin promocion.

## 6. Relacion con ML/RL

El scanner es un mecanismo de denominador y seleccion.

Sirve para responder:

```text
Sobre que conjunto de instrumentos podia actuar o investigar TSIS?
```

No sirve, por si solo, para entrenar una politica.

ML/RL debe consumir estados compuestos, temporalmente legales y validados. El
scanner puede formar parte del lineage o del contexto de seleccion, pero no es
la representacion completa del mercado.

## 7. Evidencia y fundamento cientifico

Decision TSIS -> Evidencia directa -> Obligacion tecnica -> Limitacion abierta:

| Decision TSIS | Evidencia directa | Obligacion tecnica | Limitacion abierta |
| --- | --- | --- | --- |
| Separar candidate selection de estado. | RL y decision models operan sobre estados, no sobre listas de observacion. `RESEARCH_PHILOSOPHY.md` define setups como transiciones de estado. | Scanner rows no pueden usarse como `market_state` final. | Hace falta construir `market_state_table`/`event_state_table` completos. |
| Mantener scanner operativo y scanner broad separados. | La comparacion entre visibilidad humana y discovery amplio evita sesgo de llegada tardia. | Persistir `scanner_definition_id`, `candidate_reasons`, rankings y flags separados. | Los thresholds broad v0.1 deben calibrarse con replay amplio. |
| No hacer hard filter universal de `volume_today > 500k`. | DAS/frontside puede aparecer antes de volumen acumulado alto. | Guardar volumen como feature, tier y razon; no como exclusion universal. | Requiere replay intradia/as-of mas rico para medir timing. |
| No usar `% change 1D` como unica razon. | Market state incluye atencion, liquidez, after-hours, premarket, news, halts y regimen. | Persistir razones multiples de inclusion. | Algunas razones dependen de tablas contextuales aun no maduras. |
| Bloquear labels/outcomes/rewards dentro del scanner. | `VERSIONING_STANDARDS.md` exige separar features, labels, rewards, actions y datasets. | Validators deben prohibir PnL/fill/reward/label/action en scanner table. | Strategy tables pueden tener labels, pero fuera del scanner general. |

## 8. Definicion corta para agentes

```text
Scanner Candidate Selection = capa reproducible que define que instrumentos
estaban bajo observacion o discovery en un as-of determinado.
```

Si un agente no puede explicar la diferencia entre scanner, state, event,
strategy y outcome, no debe modificar esta capa.

