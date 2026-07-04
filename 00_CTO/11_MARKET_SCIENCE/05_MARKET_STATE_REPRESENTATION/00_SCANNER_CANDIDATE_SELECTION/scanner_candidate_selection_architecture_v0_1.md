# Scanner Candidate Selection Architecture v0.1

Fecha: 2026-06-30
Estado: candidate_policy
Scope: TSIS Market State Representation, Data Foundation, Trading Systems,
ML/RL, live readiness and AlphaEvolve evaluators

## Nota de revision 2026-06-30

Este documento queda conservado como arquitectura de candidate selection v0.1,
pero la decision CTO activa para nueva implementacion vive en:

```text
scanner_base_universe_and_profiles_contract_v0_2.md
```

La lectura vigente ya no es:

```text
dos scanners independientes
```

La lectura vigente es:

```text
un denominador base elegible + perfiles reproducibles + overlays posteriores
por estrategia
```

El replay v0.1 sigue siendo evidencia util de forma, lineage y separacion de
responsabilidades, pero no debe usarse como doctrina final.

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
- confundir una hot list operativa con el estado completo del mercado.

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

## 3. Decision v0.2: un scanner base, multiples perfiles

La conclusion posterior a la revision DAS y Market State es:

```text
TSIS debe mantener una sola poblacion base y derivar perfiles sobre ella.
```

Hard filters del scanner base:

```text
common_stock = true
market_cap_usd < 100000000
0.5 < last_price <= 20
data_quality in usable/review
```

Semantica precisa:

```text
base_in_play_universe_scanner_v0_2 = identificador estable
base_eligible_smallcap_denominator = significado correcto
```

Los perfiles son flags/ranks paralelos sobre el mismo denominador. No forman
un embudo secuencial.

Perfiles derivados:

```text
trade_station_like_profile_v0_2
relative_volume_profile_v0_2
percent_change_profile_v0_2
dollar_volume_tradability_profile_v0_2
das_research_profile_v0_2
```

Interpretacion actual:

- `relative_volume_profile_v0_2` debe convertirse en aceleracion de volumen
  intradia/as-of; un proxy daily no basta para promocion.
- `percent_change_profile_v0_2` debe aplicar un minimo declarado antes de
  rankear top-N.
- `dollar_volume_tradability_profile_v0_2` mide operabilidad/tradability, no
  alpha.
- `das_research_profile_v0_2` es provisional; el DAS real debe vivir como
  overlay de estrategia o tabla experimental propia.

La razon es tecnica:

- `volume_today >= 500k` puede llegar tarde para frontside/DAS;
- `% change 1D top 25` reconstruye visibilidad humana, pero no agota discovery;
- float bajo importa, pero debe tener fuente point-in-time auditada antes de
  ser hard filter;
- el scanner debe crear denominador, no seleccionar solo buenos ejemplos;
- ML/RL necesita estados, no filas de scanner.

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

Regla:

```text
Data Foundation define el denominador y perfiles genericos.
Strategy Research define overlays de estrategia.
```

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
| Separar candidate selection de estado. | RL y decision models operan sobre estados, no sobre listas de observacion. Levine et al. (2020) revisa offline RL como aprendizaje desde datasets historicos de decision. | Scanner rows no pueden usarse como `market_state` final. | Hace falta construir `market_state_table`/`event_state_table` completos. |
| Reemplazar dos scanners por scanner base + perfiles. | La cobertura del dataset condiciona cualquier politica aprendida; dividir universos por thresholds de research puede crear sesgo de seleccion. | Mantener denominador base y guardar perfiles como flags/ranks/reasons. | Los contratos operativos de `01_foundations` aun son v0.1. |
| No hacer hard filter universal de `volume_today > 500k`. | Causal ML y Causal Factor Investing advierten contra confundir proxy observable con mecanismo. En microcaps, volumen puede ser consecuencia de attention shock. | Guardar volumen como feature, tier, ranking y razon; medir si llega tarde. | Requiere replay intradia/as-of mas rico para medir timing. |
| No usar `% change 1D` como unica razon. | DeepLOB y literatura LOB muestran que el mercado relevante para decision tiene estructura espacio-temporal, no solo retorno diario. | Persistir multiples perfiles de ranking. | Algunas razones dependen de tablas contextuales aun no maduras. |
| Bloquear labels/outcomes/rewards dentro del scanner. | `VERSIONING_STANDARDS.md` exige separar features, labels, rewards, actions y datasets; offline RL necesita transiciones gobernadas. | Validators deben prohibir PnL/fill/reward/label/action en scanner table. | Strategy tables pueden tener labels, pero fuera del scanner general. |

Referencias primarias y detalle operativo viven en:

```text
scanner_base_universe_and_profiles_contract_v0_2.md
```

## 8. Definicion corta para agentes

```text
Scanner Candidate Selection = capa reproducible que define que instrumentos
estaban bajo observacion o discovery en un as-of determinado.
```

Si un agente no puede explicar la diferencia entre scanner, profile, state,
event, strategy y outcome, no debe modificar esta capa.
