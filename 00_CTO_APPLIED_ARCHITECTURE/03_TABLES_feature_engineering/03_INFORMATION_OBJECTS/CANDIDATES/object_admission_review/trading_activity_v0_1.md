# Trading Activity - Object Admission Review v0.1

Status: `object_admission_review_v0_1`
Date: `2026-07-20`
Scope: `candidate_adversarial_review_pre_formal_admission`

Este documento revisa si el Objeto candidato `Trading Activity` merece existir
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
El mercado participa en la negociacion.
```

### Phenomenon Description

```text
Participacion negociada observable en el mercado de un instrumento.
```

### Observable Information To Preserve

```text
La intensidad con la que existe participacion negociada realizada,
en una escala temporal declarada, bajo una politica de corte
legal en decision_timestamp.
```

### Primary Informational Uncertainty

```text
Cuanta participacion negociada observable existe en el instrumento,
si esa participacion es normal o anomala para su contexto,
y si su intensidad altera la interpretacion del estado de mercado.
```

Esta incertidumbre no exige evidencia exclusiva. Puede compartir variables
con otros dominios. Lo que debe conservar es identidad informacional propia.

### Semantic Capability

```text
Trading Activity debe ser capaz de representar la intensidad observable
de participacion negociada de forma temporalmente legal.
```

### Candidate Information Object

```text
Trading Activity
```

## 3. Minimal Semantic Identity

`Trading Activity` deja de ser `Trading Activity` si desaparece:

```text
1. participacion negociada observable;
2. intensidad de participacion;
3. escala temporal, ventana o ritmo explicito;
4. negociacion realizada, no solo interes teorico o quote state;
5. legalidad temporal en decision_timestamp.
```

`Trading Activity` no necesita para conservar su identidad:

```text
spread;
quoted depth;
coste de ejecucion;
direccion del precio;
retorno;
price location;
volatilidad o rango;
agresor comprador/vendedor;
signed flow;
scanner selection;
outcomes futuros;
short activity con fuente y lag propios.
```

Regla:

```text
Si un modelo elimina la intensidad de participacion negociada,
ya no implementa Trading Activity.

Si un modelo solo cambia fuente, ventana, baseline, normalizacion
o resolucion temporal, no crea automaticamente otro Objeto.
```

## 4. Irreducibility Criterion

Definicion operativa:

```text
An Information Object is irreducible when its primary informational
uncertainty cannot be sufficiently represented by existing admitted
or candidate Objects without losing its semantic capability or
minimal semantic identity.
```

Aplicacion a `Trading Activity`:

```text
Trading Activity es irreducible si TSIS necesita preservar
participacion negociada observable como intensidad temporalmente legal,
y esa informacion no queda suficientemente preservada por Liquidity,
Price Movement, Price Location, Volatility, Order Flow Pressure,
Market Microstructure State, Selection Surfaces o Outcomes.
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

| Evidence | En Trading Activity | En Liquidity |
| --- | --- | --- |
| `dollar_volume` | cantidad economica negociada | proxy parcial de tradability o capacidad de absorcion |
| `trade_count` | intensidad de prints o participacion | proxy parcial de disponibilidad o actividad operable |
| `volume` | masa negociada observable | posible proxy indirecto de negociabilidad |

Conclusion:

```text
Shared evidence is allowed.
Shared identity is not assumed.
```

## 6. Boundary / Absorption Tests

| Attack | Question | Review result | Decision |
| --- | --- | --- | --- |
| Absorb into `Liquidity` | Es solo una forma de medir si es facil negociar? | No. `Liquidity` pregunta por ejecutabilidad, coste, disponibilidad e impacto. `Trading Activity` pregunta cuanta participacion realizada existe. | `not_absorbed` |
| Absorb into `Price Movement` | Es solo una medida indirecta de movimiento? | No. Puede haber actividad alta sin gran movimiento, y movimiento con actividad baja. | `not_absorbed` |
| Absorb into `Volatility / Range State` | Es solo amplitud del precio? | No. Volatilidad mide dispersion/amplitud. Trading Activity mide participacion. | `not_absorbed` |
| Absorb into `Order Flow Pressure` | Es solo order flow sin nombre? | No para el core. Trading Activity es no direccional por defecto. Signo, agresion e imbalance pertenecen a `Order Flow Pressure`. | `boundary_confirmed` |
| Absorb into `Market Microstructure State` | Es solo textura del tape? | No para el core. Trade size distribution puede ser extension o frontera microestructural, pero la identidad minima es participacion realizada. | `extension_boundary` |
| Absorb into `Selection Surfaces` | Es scanner activity? | No. Scanner threshold puede usar actividad, pero una seleccion no prueba participacion como Objeto. | `selection_separated` |
| Split `Relative Trading Activity` | RVOL merece Objeto propio? | No por defecto. Relative activity cambia baseline/normalizacion, no la incertidumbre primaria. | `representation_model` |
| Move `Economic Turnover` | Dollar/float turnover pertenece a otro dominio? | Dollar turnover puede ser modelo/extension. True float turnover requiere float PIT gobernado y queda bloqueado hasta fuente oficial. | `extension_with_restrictions` |

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
| `daily_absolute_participation_model` | core daily context candidate | Representa participacion realizada en sesion diaria cerrada o sesiones previas. |
| `daily_relative_participation_model` | relative model candidate | Representa anomalia contra baseline prior-only. No crea Objeto separado por defecto. |
| `intraday_absolute_accumulation_model` | core intraday candidate | Representa actividad acumulada hasta `t` usando barras cerradas. |
| `intraday_pace_model` | intraday relative extension | Representa actividad vs expectativa a tiempo `t`; requiere politica de variante. |
| `trade_window_intensity_model` | microstructure/event-window profile | Representa intensidad en ventana cerrada de trades. |
| `trade_size_distribution_model` | extension / microstructure boundary | Puede enriquecer textura de actividad, pero no es core hasta justificar identidad. |
| `economic_turnover_model` | extension with restrictions | `dollar_volume` permitido; true float turnover bloqueado sin float PIT gobernado. |
| `scanner_activity_threshold_model` | selection surface only | No implementa core de Trading Activity para State. |
| `directional_activity_model` | move to other domain | Signo, agresion e imbalance pertenecen a `Order Flow Pressure`. |

## 8. Semantic Capability Versus Minimum Model

Este documento no fija una variable minima obligatoria.

La condicion minima no es:

```text
usar una variable concreta.
```

La condicion minima es:

```text
existir al menos un Representation Model aprobado
capaz de implementar la semantic capability de Trading Activity.
```

Condicion minima de representacion:

```text
El modelo debe medir participacion negociada realizada
dentro de una ventana o escala temporal explicita,
con fuente observable declarada,
cutoff legal en decision_timestamp,
y sin depender de outcomes futuros ni selection bias no gobernado.
```

## 9. Temporal Legality Constraints

Reglas obligatorias:

```text
1. Una barra intradia solo es consumible despues de su cierre.

2. El volumen diario final solo es consumible despues del cierre
   o como contexto historico de sesiones previas.

3. Todo baseline debe ser prior-only o as-of.

4. Toda ventana de trades debe estar cerrada:
   window_end <= decision_timestamp.

5. Scanner selection no puede usarse como feature causal neutral
   sin separacion explicita de selection surface y selection bias.

6. Outcomes futuros quedan prohibidos como input.

7. Toda fuente 1m derivada debe declarar lineage, version y politica
   de reparacion o quote-guarding cuando aplique.
```

## 10. State Impact If Eventually Accepted

Si se admite formalmente, `Trading Activity` debe entrar en State como Objeto:

```text
Trading Activity
    -> approved Representation Models
        -> approved Physical Implementations
            -> legal State profile consumption
```

No debe entrar como:

```text
lista abierta de columnas de volumen, rvol, trade count,
pace, scanner threshold, dollar volume, size distribution
o variantes parametrizadas sin decision de modelo.
```

Perfiles probables:

```text
market_state_core:
    capacidad minima decision-safe de participacion observable.

market_state_intraday:
    acumulacion y/o pace intradia si el modelo queda aprobado.

market_state_microstructure_extension:
    trade-window intensity y, si se justifica, size distribution.

scanner/event context:
    selection surfaces separadas de causal features.
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
Trading Activity preserva una primary informational uncertainty propia:
la intensidad observable de participacion negociada.

No necesita evidencia exclusiva para existir.
Comparte evidencia con Liquidity, Microstructure y otros dominios,
pero no comparte identidad informacional.

El candidato sobrevive a los principales ataques de absorcion
si se mantiene separado de direction/aggression, scanner selection,
liquidity cost/depth, price movement, volatility y outcomes.
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
perfiles de State y controles de variantes.
```

Restricciones operativas recomendadas:

```text
1. Mantener core pequeno y semanticamente estable.

2. Tratar `Relative Trading Activity` como Representation Model,
   no como Objeto separado por defecto.

3. Tratar `scanner_activity_threshold_model` como Selection Surface,
   no como modelo core de State.

4. Mover signed/aggressor/imbalance a `Order Flow Pressure`.

5. Mantener trade size distribution como extension o frontera
   hasta justificar su rol.

6. Bloquear true float turnover hasta disponer de float PIT gobernado.

7. Exigir Operational Mapping antes de autorizar variables fisicas.

8. Exigir politica temporal explicita por modelo.
```

## 12. Open Questions For Formal Admission

```text
1. Que Representation Model debe implementar primero la semantic capability?

2. Cual es el perfil minimo de `market_state_core` para Trading Activity?

3. Que parte de trade size distribution pertenece a Trading Activity
   y que parte pertenece a Market Microstructure State?

4. Como se versionaran variantes de baseline, ventana y pace?

5. Que consumidores necesitan core, intraday profile o microstructure extension?

6. Que evidence threshold convierte una representacion en suficientemente estable
   para State y que queda como research-only?
```

## 13. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\trading_activity_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\trading_activity_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\trading_activity_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

