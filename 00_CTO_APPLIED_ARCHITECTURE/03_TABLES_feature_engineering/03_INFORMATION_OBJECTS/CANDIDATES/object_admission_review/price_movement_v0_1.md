# Price Movement - Object Admission Review v0.1

Status: `object_admission_review_v0_1`
Date: `2026-07-20`
Scope: `candidate_adversarial_review_pre_formal_admission`

Este documento revisa si el Objeto candidato `Price Movement` merece existir
como `Information Object` independiente.

No constituye admision formal.
No autoriza variables para `Market State` ni `Event State`.
No selecciona implementacion fisica final.
No modifica schemas, builders, validators, manifests, contratos ni datasets.

## Nota De Estado

```text
Domain Definition = define el dominio semantico.
Representation Landscape = revisa modelos posibles.
Candidate Object Definition = fija el candidato trazable.
Object Admission Review = intenta romper el candidato antes de admitirlo.
Accepted Object = decision institucional posterior, no ejecutada aqui.
```

Este documento aplica el criterio refinado de admision:

```text
Un Information Object no necesita evidencia exclusiva.

Necesita preservar una primary informational uncertainty
que no quede suficientemente representada por otros Objetos
sin perder su semantic capability o minimal semantic identity.
```

## 1. Jerarquia Metodologica

La revision usa la siguiente jerarquia:

```text
Observable market phenomenon
    -> Phenomenon description
        -> Observable information to preserve
            -> Primary informational uncertainty
                -> Semantic capability
                    -> Candidate Information Object
                        -> Minimal semantic identity
                            -> Representation Model
                                -> Physical implementation
```

Lectura:

```text
El Objeto no nace de una variable.
El Objeto nace de una incertidumbre informacional primaria
que TSIS decide preservar sobre fenomenos observables.
```

## 2. Candidate Object

### Observable Market Phenomenon

```text
El precio cambia.
```

### Phenomenon Description

```text
Desplazamiento observable del precio de un instrumento
entre referencias temporales legalmente disponibles.
```

### Observable Information To Preserve

```text
Como cambia el precio hasta el decision_timestamp:
direccion, magnitud, velocidad, aceleracion,
continuidad, discontinuidad y persistencia del cambio observable.
```

### Primary Informational Uncertainty

```text
Como se esta desplazando el precio hasta el instante observado,
en que direccion, con que intensidad dinamica,
y si el cambio observable representa continuidad, gap,
aceleracion, desaceleracion o perdida de direccion.
```

Esta incertidumbre no exige evidencia exclusiva. Puede compartir precios,
referencias OHLCV y retornos con otros dominios. Lo que debe conservar es
identidad informacional propia: cambio temporal del precio.

### Semantic Capability

```text
Price Movement debe ser capaz de representar el cambio observable
del precio de forma temporalmente legal.
```

### Candidate Information Object

```text
Price Movement
```

## 3. Minimal Semantic Identity

`Price Movement` deja de ser `Price Movement` si desaparece:

```text
1. cambio observable del precio;
2. referencia temporal legal contra la que se mide el cambio;
3. direccion o magnitud del desplazamiento;
4. separacion entre movimiento observable hasta t y outcome futuro;
5. legalidad temporal en decision_timestamp.
```

`Price Movement` no necesita para conservar su identidad:

```text
posicion contra VWAP, HOD, LOD, open o prior close;
amplitud o dispersion como fenomeno principal;
volumen o participacion negociada;
spread, depth o coste de ejecucion;
agresion compradora/vendedora;
scanner selection;
pattern labels;
future returns, MFE o MAE.
```

Regla:

```text
Si un modelo elimina el cambio observable del precio,
ya no implementa Price Movement.

Si un modelo solo cambia horizonte, ventana, bar size,
referencia temporal o resolucion fisica,
no crea automaticamente otro Objeto.
```

## 4. Irreducibility Criterion

Definicion operativa:

```text
An Information Object is irreducible when its primary informational
uncertainty cannot be sufficiently represented by existing admitted
or candidate Objects without losing its semantic capability or
minimal semantic identity.
```

Aplicacion a `Price Movement`:

```text
Price Movement es irreducible si TSIS necesita preservar
cambio observable del precio como informacion temporalmente legal,
y esa informacion no queda suficientemente preservada por
Price Location / Structure, Volatility / Range State, Trading Activity,
Liquidity, Order Flow Pressure, Selection Surfaces o Outcomes.
```

## 5. Shared Evidence Rule

```text
Una misma evidencia fisica puede contribuir a varios Objetos.
El significado lo decide:

Information Object
    -> Representation Model
        -> temporal use
            -> consumer context
```

Ejemplo:

| Evidence | En Price Movement | En dominio vecino |
| --- | --- | --- |
| `prior_close` | referencia temporal para medir cambio | referencia estructural para Price Location |
| `open_price` | referencia legal para gap o return intradia | nivel estructural de sesion |
| `close_price` | precio observado para retorno as-of o cierre diario | input para range/volatility si se combina con high/low |
| `high_price` / `low_price` | posible soporte de trayectoria o extension | nucleo de Volatility / Range State |

Conclusion:

```text
Shared evidence is allowed.
Shared identity is not assumed.
```

## 6. Boundary / Absorption Tests

| Attack | Question | Review result | Decision |
| --- | --- | --- | --- |
| Absorb into `Price Location / Structure` | Es solo posicion contra referencias? | No. `Price Movement` mide cambio temporal. `Price Location` mide donde esta el precio respecto a referencias. | `not_absorbed` |
| Absorb into `Volatility / Range State` | Es solo amplitud o dispersion? | No. Volatility mide rango/dispersion/incertidumbre. Price Movement mide direccion, magnitud y dinamica del cambio. | `not_absorbed` |
| Absorb into `Trading Activity` | Es solo movimiento soportado por actividad? | No. La actividad contextualiza el movimiento, pero no mide como cambia el precio. | `not_absorbed` |
| Absorb into `Liquidity` | Es solo efecto de negociabilidad? | No. Liquidity pregunta por ejecutabilidad, coste o disponibilidad. Price Movement pregunta como se desplaza el precio. | `not_absorbed` |
| Absorb into `Order Flow Pressure` | Es solo presion compradora/vendedora inferida? | No. Price Movement observa desplazamiento de precio; no atribuye agresion ni signo de flujo. | `boundary_confirmed` |
| Absorb into `Outcome Layer` | Future return es Price Movement? | No como input. Movimiento futuro es outcome/label, no informacion observable en t. | `outcome_separated` |
| Split `Momentum` | Momentum merece Objeto propio? | No por defecto. Momentum es persistencia direccional del movimiento, no sinonimo de todo cambio de precio. | `representation_model_or_subobject_pending` |
| Split `Opening Gap Movement` | Gap merece Objeto propio? | No por defecto. Gap es modelo de cambio discontinuo entre referencias temporales. | `representation_model` |
| Split `Price Speed` / `Price Acceleration` | Velocidad/aceleracion merecen Objetos propios? | No por defecto. Son modelos derivados de cambio temporal y horizonte declarado. | `representation_models` |
| Move `Reversal / Fade` | Reversal pertenece a Price Movement o pattern research? | Parcialmente fronterizo. Puede ser modelo de perdida de continuidad, pero tambien pattern/strategy surface. | `boundary_model_with_restrictions` |

## 6.1 Scientific Review Versus Engineering Readiness

Este documento separa dos preguntas distintas:

```text
Scientific Review:
    Debe existir este Information Object?

Engineering Readiness:
    Esta TSIS preparado para usarlo operativamente?
```

Regla:

```text
La falta de una fuente fisica suficiente, un mapping operativo,
una variante gobernada o una politica temporal completa
no invalida por si sola la identidad cientifica del Objeto.

Puede existir esta combinacion:

scientific_identity = accepted
operational_readiness = blocked_or_restricted
```

Lectura:

```text
Scientific identity decide si el Objeto merece existir.
Engineering readiness decide si puede consumirse, materializarse
o integrarse en State bajo contratos operativos.
```

## 7. Representation Models Under Review

| Model | Admission role | Review |
| --- | --- | --- |
| `opening_gap_movement_model` | core discontinuous movement candidate | Representa cambio legal desde prior close hasta apertura. |
| `intraday_return_to_reference_model` | core intraday candidate | Representa cambio as-of contra referencia legal observada. |
| `daily_closed_return_model` | daily historical context candidate | Representa movimiento diario completo solo tras cierre o como historia previa. |
| `bar_to_bar_movement_model` | candidate requiring capability decision | Representa cambio entre barras cerradas; falta decidir capacidad atomica canonica. |
| `move_speed_model` | extension / intraday dynamic model | Representa tasa de cambio en W; requiere politica de variantes. |
| `move_acceleration_model` | extension model | Representa cambio en la velocidad; sensible a ruido y horizonte. |
| `momentum_persistence_model` | representation model or subobject pending | Representa persistencia direccional, no todo Price Movement. |
| `reversal_fade_model` | boundary model | Puede representar perdida de continuidad, pero roza pattern research. |
| `future_response_model` | outcome only | Prohibido como feature/input de State. |

## 8. Semantic Capability Versus Minimum Model

Este documento no fija una variable minima obligatoria.

La condicion minima no es:

```text
usar una variable concreta.
```

La condicion minima es:

```text
existir al menos un Representation Model aprobado
capaz de implementar la semantic capability de Price Movement.
```

Condicion minima de representacion:

```text
El modelo debe medir cambio observable del precio
entre referencias temporales declaradas,
con fuente observable declarada,
cutoff legal en decision_timestamp,
y sin depender de outcomes futuros ni labels de estrategia.
```

## 9. Temporal Legality Constraints

Reglas obligatorias:

```text
1. Una barra intradia solo es consumible despues de su cierre.

2. `gap_pct` es legal despues de conocer apertura y prior_close.

3. `daily_return_pct` e `intraday_return_pct` del dia actual
   solo son legales tras market close.

4. `return_vs_prior_close` y `return_vs_session_open`
   son legales intradia solo con precio observado hasta t.

5. Speed, acceleration, persistence y reversal/fade requieren
   ventanas cerradas, horizonte declarado y min_periods.

6. Future returns, MFE y MAE son outcomes, no inputs.

7. Toda fuente 1m derivada debe declarar lineage, version y politica
   de reparacion o quote-guarding cuando aplique.
```

## 10. State Impact If Eventually Accepted

Si se admite formalmente, `Price Movement` debe entrar en State como Objeto:

```text
Price Movement
    -> approved Representation Models
        -> approved Physical Implementations
            -> legal State profile consumption
```

No debe entrar como:

```text
lista abierta de retornos, distancias, rangos, volatilidades,
future returns, MFE, MAE, pattern labels o variantes parametrizadas
sin decision de modelo.
```

Perfiles probables:

```text
market_state_core:
    cambio as-of minimo contra referencia temporal legal.

market_state_intraday:
    speed / acceleration / persistence con variantes gobernadas.

market_state_event_extension:
    movimiento pre/at-event bajo ventanas cerradas.

outcomes:
    future returns, MFE y MAE separados de X.
```

## 11. Preliminary Review Decision

```text
peer_review_result = survives_adversarial_review
formal_admission_decision = pending
```

### Scientific Identity

```text
scientific_identity = accepted_by_review
scientific_identity_confidence = high
recommended_scientific_admission_path = accepted
```

Justificacion cientifica:

```text
Price Movement preserva una primary informational uncertainty propia:
como cambia el precio hasta t.

No necesita evidencia exclusiva para existir.
Comparte precios y referencias OHLCV con Price Location,
Volatility y otros dominios, pero no comparte identidad informacional.

El candidato sobrevive a los principales ataques de absorcion
si se mantiene separado de price location, range/volatility,
trading activity, liquidity, order flow, scanner selection
y outcomes futuros.
```

### Operational Readiness

```text
operational_readiness = accepted_with_restrictions
state_consumption_authorized = false
physical_variables_authorized = false
operational_mapping_required = true
```

Justificacion operativa:

```text
El Objeto tiene identidad cientifica suficiente,
pero su consumo operativo requiere todavia mapping,
seleccion de modelos aprobados, politicas temporales,
decisiones sobre bar_return atomico, perfiles de State
y controles de variantes para speed, acceleration y momentum.
```

Restricciones operativas recomendadas:

```text
1. Mantener core pequeno y semanticamente estable.

2. Tratar `Momentum` como Representation Model o subobject pending,
   no como sinonimo automatico de Price Movement.

3. Tratar `Opening Gap Movement`, `Price Speed` y `Price Acceleration`
   como Representation Models, no como Objetos separados por defecto.

4. Separar estrictamente Price Movement de Price Location / Structure.

5. Separar estrictamente Price Movement de Volatility / Range State.

6. Prohibir future returns, MFE y MAE como inputs.

7. Exigir Operational Mapping antes de autorizar variables fisicas.

8. Resolver si `intraday__bar_return` debe existir como capacidad
   atomica canonica o si se expresa mediante returns contra referencia.
```

## 12. Open Questions For Formal Admission

```text
1. Que Representation Model debe implementar primero la semantic capability?

2. Cual es el perfil minimo de `market_state_core` para Price Movement?

3. Debe existir `intraday__bar_return` como capacidad atomica canonica?

4. Que queda reservado para `Momentum` y que queda en Price Movement core?

5. Que referencias temporales son canonicas:
   prior_close, session_open, segment_open, previous_bar_close?

6. Como se versionaran horizontes W para speed, acceleration y persistence?

7. Que parte de reversal/fade pertenece a Price Movement
   y que parte pertenece a pattern discovery o strategy research?
```

## 13. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_movement_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_movement_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\price_movement_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

