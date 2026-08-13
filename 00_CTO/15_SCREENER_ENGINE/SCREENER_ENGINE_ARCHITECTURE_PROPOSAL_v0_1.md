# TSIS Screener Engine Architecture Proposal v0.1

Fecha: 2026-08-12  
Estado: `draft_for_human_review`  
Owner conceptual propuesto: `00_CTO/15_SCREENER_ENGINE`  
Runtime propuesto: modulo TSIS independiente, pendiente de autorizacion y naming final  
Consumidor inicial: `02_TSIS_BACKTEST_ENGINE`  
Autoridad: no promovida; este documento no autoriza implementacion ni ejecucion

## 1. Resumen ejecutivo

TSIS debe separar tres responsabilidades:

```text
Data Foundation
-> suministra observables, identidades, calendarios y artefactos PIT gobernados

Screener Engine
-> resuelve universos elegibles y ejecuta familias versionadas de scanners

Backtest Engine
-> consume snapshots sellados del Screener Engine durante replay
```

El motor no debe vivir dentro de `01_TSIS_DATA_FOUNDATION`. Data Foundation no
es propietaria de la decision de candidate selection: es el proveedor upstream
de los datos necesarios y conserva la autoridad sobre sus propios datasets,
schemas, policies, validators y manifests.

La conceptualizacion y arquitectura del nuevo subsistema debe vivir en:

```text
C:/TSIS_Data/00_CTO/15_SCREENER_ENGINE
```

El ejecutable se recomienda como modulo top-level independiente porque no sera
exclusivo del backtester. `02_TSIS_BACKTEST_ENGINE` sera su primer consumidor,
pero el mismo motor podra servir a research, replay y, despues de gates
independientes, operacion live/shadow.

`03_TSIS_SCREENER_ENGINE` no es un nombre disponible: `03_TSIS_Lab` ya existe y
es un modulo institucional vigente. Como nombre provisional se propone:

```text
C:/TSIS_Data/07_TSIS_SCREENER_ENGINE
```

El numero y nombre final requieren decision humana antes de crear el runtime.

## 2. Decisiones incorporadas del owner

1. La arquitectura conceptual del screener deja de plantearse como una
   subcarpeta interna del Backtest Engine y pasa a tener owner conceptual propio
   en `00_CTO/15_SCREENER_ENGINE`.
2. El motor ejecutable no vive en Data Foundation.
3. `02_TSIS_BACKTEST_ENGINE` consume la ejecucion del motor; no debe convertirse
   en propietario de su semantica general.
4. `Daily Eligible Universe` es un motor generalista.
5. No existe un unico motor In-Play universal. Debe existir una familia de
   scanners In-Play versionados, cada uno ligado a una estrategia o familia de
   estrategias y con contrato propio.
6. El presente documento es un draft de arquitectura. No abre `BT-GATE-016`, no
   autoriza runtime, no materializa datos y no promueve ningun candidato upstream.

## 3. Problema cientifico

El primer objetivo es seleccionar diariamente el `Universo elegible` dentro de
un parent frame gobernado de 4.824 tickers.

La pregunta cientifica no es:

```text
Que acciones sabemos hoy que tuvieron una oportunidad?
```

La pregunta correcta es:

```text
Que instrumentos podian ser clasificados como elegibles usando solamente
informacion legalmente disponible antes del cutoff de la sesion d?
```

La respuesta debe ser:

- point-in-time y causal;
- determinista;
- reproducible desde un manifest;
- versionada;
- auditable fila a fila;
- explicable mediante estados y razones;
- estable entre backtest, research y futuros consumidores autorizados;
- independiente de outcomes, PnL y conocimiento retrospectivo.

## 4. Que representan los 4.824 tickers

Los 4.824 instrumentos proceden de `lt1b_universe_v0_1`:

- universo base original: 12.468 instrumentos;
- activos cuyo ultimo estado clasificable era LT1B: 2.476;
- inactivos cuyo ultimo estado clasificable era LT1B: 2.348;
- total del parent frame: 4.824.

Este conjunto debe denominarse:

```text
fixed governed parent frame: lt1b_universe_v0_1
```

No debe presentarse como:

```text
universo historico completo de acciones estadounidenses
```

Tampoco es una reconstruccion diaria perfecta de todas las sociedades con
capitalizacion inferior a 1.000 millones. Esta limitacion debe aparecer en UI,
manifests, reports y claims cientificos.

## 5. Taxonomia propuesta

### 5.1 Parent Universe

Marco fisico/gobernado dentro del cual puede operar un run. En v0.1:

```text
lt1b_universe_v0_1
```

### 5.2 Daily Eligible Universe

Poblacion generalista de instrumentos clasificables y elegibles antes de la
sesion. Responde solamente:

```text
Este instrumento pertenece al universo elegible de la sesion d?
```

No es una senal, no significa que el ticker este In-Play y no contiene criterios
especificos de estrategia.

### 5.3 Generic Observation Profile

Vista, flag o ranking reproducible sobre el universo elegible. Puede ordenar o
describir, pero no cambia la identidad de la poblacion base.

Ejemplos futuros:

- percent-change profile;
- relative-volume profile;
- tradability profile;
- operator hot-list reconstruction.

Los perfiles son paralelos, no un embudo secuencial.

### 5.4 Strategy In-Play Scanner

Detector versionado que responde si un instrumento merece vigilancia para una
estrategia concreta bajo un reloj causal declarado.

No se define un unico In-Play global. La arquitectura debe soportar:

```text
inplay_momentum_scanner
inplay_das_frontside_scanner
inplay_short_parabolic_scanner
inplay_breakout_scanner
inplay_backside_scanner
...
```

Cada scanner declara:

- `scanner_definition_id` y version;
- estrategia o familia consumidora;
- parent universe y Daily Eligible Universe requerido;
- cutoff o schedule de reevaluacion;
- inputs y disponibilidad temporal;
- filtros, ranking y razones;
- estados unavailable/degraded/review;
- schema y grain de salida;
- tests y fixtures de frontera;
- claims permitidos y prohibidos.

### 5.5 Strategy Overlay

Hipotesis experimental posterior aplicada por una estrategia. No puede modificar
silenciosamente el Daily Eligible Universe ni promover sus filtros como doctrina
general.

## 6. Precedentes existentes y tratamiento propuesto

Existe una conceptualizacion anterior en:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/
00_SCANNER_CANDIDATE_SELECTION
```

Sus aportaciones que deben conservarse son:

- base eligible no es In-Play;
- In-Play no es estrategia;
- scanner no es market state ni event state;
- perfiles genericos son flags paralelos;
- no deben seleccionarse solo winners;
- float no puede ser hard filter sin fuente PIT gobernada;
- labels, outcomes, rewards, fills y PnL quedan fuera del scanner.

Sin embargo, el precedente v0.3 proponia un unico
`in_play_momentum_candidate_denominator` antes de overlays de estrategia. La
decision actual del owner es mas general: In-Play sera una familia de motores
dependientes de estrategia. Por tanto, ese v0.3 debe conservarse como antecedente
de un scanner In-Play Momentum, no como taxonomia universal.

Si esta propuesta se aprueba, el trabajo futuro debe decidir de forma gobernada
si los documentos de `00_CTO/11` se migran, se marcan como superseded o se
mantienen como historia. No deben quedar dos autoridades conceptuales activas.

## 7. Activo PIT ya disponible

Data Foundation y Market States ya produjeron un candidato directamente util:

```text
population_target_presession_4824_candidate_v0_1_experimental
```

Su contrato emplea, para cada sesion, informacion disponible antes de las
`04:00 America/New_York`:

```text
prior eligible RTH close
x
weighted-average shares proxy publicado previamente
= presession reference market-cap proxy
```

Politica primaria validada:

```text
price: 0.50 <= prior_eligible_RTH_close <= 20.00
cap:   presession_reference_market_cap_proxy < 100,000,000 USD
shares proxy: diluted weighted average; fallback basic weighted average
fundamental TTL: 180 days
availability: as_of_date < session_date
```

Grain autorizado:

```text
instrument_id x ticker_as_of_session x session_date
```

La clave compuesta es obligatoria porque se observaron 28.876 grupos duplicados
si la identidad se reduce indebidamente.

### 7.1 Validacion existente

El gate del selector termino:

```text
PASS_WITH_RESTRICTIONS
```

La materializacion registra:

| Medida | Valor |
| --- | ---: |
| Filas | 7.369.699 |
| Tickers | 4.824 |
| Sesiones | 5.328 |
| Cobertura | 2005-01-03 a 2026-03-09 |
| Checks de validacion | 21/21 PASS |
| Elegible | 1.417.316 |
| Ineligible por cap | 1.689.229 |
| Ineligible por precio | 2.360.588 |
| Shares stale | 201.243 |
| Precio unavailable | 671.242 |
| Shares unavailable | 1.027.005 |
| Corporate-action review | 3.076 |

Estado de promocion:

```text
VALIDATED_EXPERIMENTAL_CANDIDATE_NOT_CANONICAL
```

Este activo reduce radicalmente el riesgo de construir el primer motor, pero no
autoriza consumo automatico. Debe pasar por un contrato de adopcion del Screener
Engine y por el gate de consumo correspondiente del Backtest Engine.

### 7.2 Non-claims obligatorios

El candidato no prueba:

- market cap legal exacta;
- float exacto point-in-time;
- censo historico completo de EE. UU.;
- elegibilidad fuera del parent frame 4.824;
- ausencia total de ambiguedad de identidad/corporate actions;
- validez automatica como universo canonico de todos los consumidores.

## 8. Fronteras numericas pendientes de ratificacion

Hay una discrepancia documental:

- formulacion humana inicial: `0.5 < price < 20`;
- contratos historicos: `0.5 < price <= 20`;
- selector presesion validado: `0.50 <= price <= 20.00`.

Recomendacion v0.1:

```text
0.50 <= prior_eligible_RTH_close <= 20.00
presession_reference_market_cap_proxy < 100,000,000
```

Motivo: reutiliza sin alteracion la semantica ya sometida a probe y validacion.

Si se aprueba un intervalo estricto `(0.50, 20.00)`, debe crearse una nueva
policy version o una vista derivada versionada y repetir fixtures, probe,
reconciliacion y certificacion. No se permite cambiar operadores solamente en el
consumidor conservando el mismo identificador.

## 9. Ownership por capa

| Capa | Responsabilidad | No debe hacer |
| --- | --- | --- |
| `00_CTO/15_SCREENER_ENGINE` | Arquitectura, taxonomia, decisiones, contratos esperados, gates y mapa de promocion | Ejecutar builders o convertirse en segunda Data Foundation |
| `01_TSIS_DATA_FOUNDATION` | Proveer datasets, schemas, identities, calendars, PIT lineage, policies, validators y manifests upstream | Ser propietaria de la semantica general del Screener Engine o de estrategias |
| runtime independiente propuesto | Resolver universos, ejecutar definiciones y producir snapshots/manifests deterministas | Redefinir silenciosamente datasets upstream, outcomes o estrategias |
| `02_TSIS_BACKTEST_ENGINE` | Consumir snapshots sellados durante preflight/replay | Recalcular el universo con reglas locales o modificarlo durante el run |
| Strategy Research | Definir scanners/overlays especificos con contrato | Cambiar el universo base para favorecer una estrategia |
| `04_TSIS_webSocket_SmallCaps` futuro | Consumir un modo live autorizado | Reutilizar una autorizacion de backtest como autorizacion live |

## 10. Ubicacion del runtime

### 10.1 Opcion A: dentro de `02_TSIS_BACKTEST_ENGINE`

Ventaja:

- menor coste inicial de integracion.

Riesgos:

- acopla el screener al reloj y ciclo de vida del backtester;
- dificulta reutilizacion live/shadow;
- mezcla ownership de poblacion con execution/replay;
- favorece divergencia entre scanner historico y scanner operativo.

### 10.2 Opcion B: modulo independiente

Ventajas:

- un solo contrato semantico para varios consumidores;
- lifecycle y gates independientes;
- API batch/replay y API incremental/live bajo la misma definicion;
- tests de determinismo propios;
- evita que el backtester se convierta en source of truth del scanner.

Riesgos:

- requiere interfaz de consumo y versionado entre modulos;
- introduce un nuevo modulo gobernado y su mantenimiento.

### 10.3 Recomendacion

Elegir modulo independiente.

Nombre provisional disponible:

```text
C:/TSIS_Data/07_TSIS_SCREENER_ENGINE
```

No crear ese modulo hasta aprobar:

- nombre y numero;
- owner;
- README/AGENTS/LOCAL_RULES;
- contrato de entrada/salida;
- gate inicial;
- relacion con `00_CTO/11` y `00_CTO/14`.

## 11. Arquitectura funcional propuesta

```text
Governed upstream datasets and manifests
        |
        v
Input Manifest Resolver
        |
        v
Daily Eligible Universe Resolver
        |
        +--> full denominator states and reasons
        +--> eligible snapshot
        |
        v
Generic Profile Registry (optional parallel views)
        |
        v
Strategy In-Play Scanner Registry
        |
        +--> momentum scanner
        +--> DAS/frontside scanner
        +--> short/parabolic scanner
        +--> future versioned scanners
        |
        v
Sealed Screener Run Artifact
        |
        +--> Backtest adapter
        +--> Research adapter
        +--> future live adapter under separate authorization
```

## 12. Componentes logicos del runtime

### 12.1 InputManifestResolver

- abre manifests upstream;
- verifica hashes y schema versions;
- valida coverage, price view y temporal policy;
- falla si el dataset no esta autorizado para ese modo de consumo.

### 12.2 DailyEligibleUniverseResolver

- recibe `session_date`, cutoff, parent universe y policy version;
- resuelve una clasificacion por instrumento/sesion;
- nunca consulta datos posteriores al cutoff;
- preserva denominador completo y reasons.

### 12.3 ScannerDefinitionRegistry

- registra definiciones inmutables y versionadas;
- impide IDs duplicados o thresholds ocultos;
- distingue `generic_profile` de `strategy_inplay_scanner`.

### 12.4 ScannerExecutor

- ejecuta una definicion contra un snapshot elegible;
- produce resultados deterministas;
- registra input hashes, code/config fingerprint y reason codes.

### 12.5 ScreenerRunValidator

- comprueba grain, unicidad y accounting cerrado;
- verifica causalidad y estados incompatibles;
- genera failure codes estables.

### 12.6 ArtifactWriter

- genera manifest, snapshots, summaries y validation report;
- ordena deterministicamente por
  `(session_date, instrument_id, ticker_as_of_session)`;
- no sobrescribe artefactos institucionales.

### 12.7 Consumer Adapters

- Backtest adapter;
- research adapter;
- futuro live adapter.

Cada adapter valida compatibilidad. Ningun adapter redefine la seleccion.

## 13. Estados minimos del Daily Eligible Universe

El motor no debe devolver solo booleanos. Debe conservar como minimo:

```text
ELIGIBLE
INELIGIBLE_PRICE
INELIGIBLE_CAP
UNAVAILABLE_PRICE
UNAVAILABLE_SHARES
STALE_SHARES
CORPORATE_ACTION_REVIEW
```

Politica default propuesta:

- solamente `ELIGIBLE` puede pasar a perfiles o scanners In-Play;
- unavailable, stale y review se excluyen del conjunto consumible;
- todas las filas permanecen contabilizadas;
- una ausencia nunca se convierte silenciosamente en `INELIGIBLE`;
- cualquier override requiere policy version y manifest.

## 14. Contrato de salida por run

### 14.1 `screener_run_manifest.json`

Debe incluir:

- run ID y mode;
- engine version y commit;
- config fingerprint;
- upstream dataset IDs, runs, manifests y hashes;
- parent universe;
- fechas y cutoff;
- policy y scanner definition versions;
- grain y schema version;
- counts por estado y sesion;
- output hashes;
- limitaciones y non-claims;
- validation result y promotion state.

### 14.2 `daily_eligible_universe.parquet`

Grain:

```text
session_date x instrument_id x ticker_as_of_session
```

Campos minimos:

- membership state y reason code;
- reference price y source timestamp;
- shares proxy, source/as-of y age;
- market-cap proxy;
- identity and corporate-action state;
- policy/lineage IDs.

### 14.3 `scanner_candidates.parquet`

Solo para perfiles/scanners solicitados. Debe declarar:

- `scanner_definition_id`;
- version;
- selected state;
- ranks/flags/reasons;
- evaluation timestamp;
- snapshot dependency.

No puede contener outcomes, fills, PnL, reward, action o future labels.

### 14.4 `screener_validation_report.json`

Debe demostrar por sesion:

```text
parent population
= eligible
+ ineligible
+ unavailable
+ stale
+ review
```

## 15. Integracion con Backtest Engine

El estado vigente del Backtest Engine es:

```text
BT-GATE-014 = closed pass with restrictions
BT-GATE-015 = closed pass with restrictions
BT-GATE-016 = NOT_OPEN
BT-GATE-016_IMPLEMENTATION = NOT_AUTHORIZED
```

El preflight actual resuelve principalmente universos estaticos mediante
`UniverseDefinition`, `UniverseRegistry` y `selected_symbols`. No representa una
membresia diaria completa ni sus estados de clasificacion.

Integracion propuesta:

```text
Screener sealed artifact
-> Backtest ScreenerArtifactAdapter
-> RunPreflight validation
-> frozen universe_manifest
-> session-by-session replay membership
```

El backtester no debe:

- recalcular market cap;
- reinterpretar TTL;
- elegir otro price view;
- rellenar sesiones ausentes;
- cambiar membership durante replay;
- reutilizar un artefacto cuyo hash no coincida.

## 16. Gate propuesto

La capacidad candidata para el Backtest Engine puede formularse como:

```text
BT-GATE-016
DAILY_PIT_ELIGIBLE_UNIVERSE_CONSUMPTION_AND_PREFLIGHT_INTEGRATION
```

Es una propuesta de alcance, no un gate abierto.

Debe probar:

1. adopcion explicita del artefacto upstream;
2. compatibilidad de schema/grain/policy;
3. fail-closed ante hash o manifest incorrecto;
4. resolucion por sesion y no por lista estatica;
5. accounting completo;
6. ausencia de delivery antes de availability;
7. replay determinista;
8. outputs y manifests sellados;
9. ningun order/fill/PnL generado por el gate de universo;
10. ningun scanner In-Play autorizado implicitamente.

El Screener Engine necesitara su propio gate anterior de adopcion y ejecucion;
`BT-GATE-016` solo debe autorizar el consumo por `02`.

## 17. Condiciones fail-closed

No debe iniciarse el run si existe:

- manifest o hash no coincidente;
- dataset no autorizado para el modo solicitado;
- fecha fuera de cobertura;
- parent universe incompatible;
- schema, grain o policy incompatibles;
- duplicado en la clave compuesta;
- sesion requerida ausente;
- fila eligible con input unavailable/stale/review incompatible;
- source timestamp igual o posterior al cutoff;
- cambio de policy o scanner definition durante el run;
- accounting que no cierre;
- corporate action pendiente sin policy explicita;
- reutilizacion de un artefacto mutable o no identificable.

La policy default para una sesion ausente debe ser abortar, no arrastrar el
ultimo universo conocido.

## 18. Proceso cientifico minimo

```text
contract and decision record
-> implementation and unit tests
-> bounded production-equivalent probe per shard
-> variable/field-by-field audit
-> identity, PIT and denominator reconciliation
-> versioned certification readout
-> human or governed PASS
-> bounded consumer integration
-> deterministic replay evidence
-> broader materialization authorization
```

Cada run debe poder reconstruir:

- codigo y commit;
- config;
- datasets y versions;
- manifests y hashes;
- cutoff y calendario;
- policy y scanner definition;
- periodo;
- output;
- validator result;
- gate y promotion state.

## 19. Bibliografia aplicable

### 19.1 Sesgos y temporalidad financiera

- Ernest Chan, *Quantitative Trading*: look-ahead, survivorship, datos
  point-in-time, low-priced stocks y reproducibilidad.
- Ernest Chan, *Algorithmic Trading*: corporate actions, splits, dividendos,
  survivorship y membresia historica.
- Stefan Jansen, *Machine Learning for Algorithmic Trading*: feature stores
  point-in-time, universos personalizados y separacion temporal de features y
  outcomes.
- Urban Jaekle y Emilio Tomasini, *Trading Systems*: data quality, vendor risk,
  delistings, ranking y ejecucion diaria.

### 19.2 Arquitectura y auditabilidad

- Joe Reis y Matt Housley, *Fundamentals of Data Engineering*: tipos de tiempo,
  lineage, lifecycle, contracts y governance.
- Martin Kleppmann, *Designing Data-Intensive Applications*: logs como source of
  record, replay determinista y schema evolution.

### 19.3 Microestructura para scanners In-Play

- Larry Harris, *Trading and Exchanges*: spread, liquidity y execution realism.
- Kyle (1985): order flow, liquidity y price impact.
- Easley, Lopez de Prado y O'Hara (2012): flow toxicity y riesgo de liquidez.
- Zhang, Zohren y Roberts, *DeepLOB*: estructura espacio-temporal del mercado.

Estas fuentes justifican obligaciones tecnicas; no sustituyen evidencia TSIS ni
promocion mediante gates.

## 20. Matriz resumida de decisiones y evidencia

| Decision | Evidencia TSIS | Obligacion |
| --- | --- | --- |
| Separar Screener Engine de Data Foundation | `00_CTO/LOCAL_RULES.md`; contratos de scanner existentes | Data Foundation provee inputs; el motor gobierna selection |
| Runtime separado de Backtest | consumidores potenciales multiples y contrato preflight actual | interfaz sellada y adapters por consumidor |
| Parent frame fijo 4.824 | contrato `lt1b_universe_v0_1` | declarar alcance y non-claims |
| Resolver diario PIT | selector presesion v0.2 y gate readout | cutoff, availability y lineage por fila |
| No recalcular cap en `02` | candidato materializado y separacion de capas | consumir artifact versionado |
| Preservar unavailable/review | closeout y filosofia TSIS | denominator accounting cerrado |
| Familia de In-Play scanners | decision humana actual y overlay policy historica | contrato/version por estrategia |
| Separar scanner de state/strategy/outcome | arquitectura histórica y TSIS Lab v3 | validators que prohiban contaminacion |
| Fail closed y manifests | `01_DATA.md`, Backtest handoff y bibliografia de data systems | preflight obligatorio |

## 21. Preguntas que requieren decision humana

1. Aprobar `00_CTO/15_SCREENER_ENGINE` como owner conceptual activo.
2. Aprobar modulo runtime independiente frente a integrarlo en `02`.
3. Aprobar `07_TSIS_SCREENER_ENGINE` o seleccionar otro nombre disponible.
4. Ratificar frontera `[0.50, 20.00]` o exigir nueva policy estricta.
5. Autorizar el candidato presesion como input inicial controlado del motor.
6. Definir la primera familia In-Play que se diseñara despues del Daily Eligible
   Universe.
7. Decidir migracion/supersession de `00_CTO/11/.../00_SCANNER_CANDIDATE_SELECTION`.
8. Decidir si el trabajo del consumidor formara `BT-GATE-016`.

## 22. Secuencia recomendada tras aprobacion

1. Crear estructura gobernada de `00_CTO/15_SCREENER_ENGINE`.
2. Crear README, AGENTS/LOCAL_RULES si aplican, decision register y roadmap.
3. Emitir contrato `Daily Eligible Universe` v0.1.
4. Emitir contrato de adopcion del candidato presesion.
5. Cerrar decision de nombre del runtime.
6. Crear scaffold del runtime en rama y gate propios.
7. Implementar adapter y validadores sin recalcular upstream.
8. Ejecutar probe acotado por shard y auditoria campo a campo.
9. Preparar gate de consumo de Backtest.
10. Solo despues, diseñar el primer Strategy In-Play Scanner.

## 23. Regla corta

```text
El parent universe define el marco.
El Daily Eligible Universe define a quien podemos mirar hoy.
Un perfil define como observar u ordenar.
Cada In-Play scanner define vigilancia para una estrategia concreta.
La estrategia define que hacer.
El estado representa que sabia TSIS.
El outcome describe que ocurrio despues.
```

Si una implementacion mezcla estas responsabilidades, no debe promocionarse.

## 24. Referencias incluidas en el paquete

El ZIP que acompaña este documento incluye copias de las fuentes institucionales,
contratos, readouts, codigo de preflight y mapas bibliograficos empleados. El
archivo `EVIDENCE_INDEX.md` explica el papel de cada evidencia y
`SHA256SUMS.txt` permite verificar que el paquete no cambio despues de su
creacion.

