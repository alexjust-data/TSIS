# Price Location / Structure - Object Admission Review v0.1

Status: `object_admission_review_v0_1`
Date: `2026-07-20`
Scope: `candidate_adversarial_review_pre_formal_admission`

Este documento revisa si el Objeto candidato `Price Location / Structure`
merece existir como `Information Object` independiente.

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
El precio ocupa una posicion contextual.
```

### Phenomenon Description

```text
Posicion contextual del precio observable de un instrumento
respecto a referencias estructurales legalmente conocidas.
```

### Observable Information To Preserve

```text
Donde esta situado el precio en decision_timestamp
respecto a anchors de sesion, VWAP, high/low observado hasta t,
prior close, rango observado y referencias de segmento.
```

### Primary Informational Uncertainty

```text
Que posicion estructural ocupa el precio en t:
si esta extendido, centrado, cerca de extremos observados,
sobre o bajo VWAP, recuperando o perdiendo una referencia,
o ubicado dentro de un rango observado.
```

Esta incertidumbre no exige evidencia exclusiva. Puede compartir precios,
anchors, high/low, VWAP y ratios con otros dominios. Lo que debe conservar
es identidad informacional propia: localizacion contextual del precio.

### Semantic Capability

```text
Price Location / Structure debe ser capaz de representar
la posicion contextual del precio frente a referencias estructurales
legalmente conocidas en decision_timestamp.
```

### Candidate Information Object

```text
Price Location / Structure
```

## 3. Minimal Semantic Identity

`Price Location / Structure` deja de ser `Price Location / Structure`
si desaparece:

```text
1. precio observable en t;
2. referencia estructural o anchor legalmente conocido;
3. distancia, proximidad o coordenada relativa contra esa referencia;
4. separacion entre localizacion actual y movimiento temporal;
5. legalidad temporal en decision_timestamp.
```

`Price Location / Structure` no necesita para conservar su identidad:

```text
direccion, velocidad o aceleracion del cambio;
persistencia direccional;
amplitud o dispersion como fenomeno principal;
volumen o participacion negociada;
spread, depth o coste de ejecucion;
agresion compradora/vendedora;
scanner selection;
pattern labels;
future HOD/LOD, future returns, MFE o MAE.
```

Regla:

```text
Si un modelo elimina la posicion relativa del precio
contra una referencia estructural legal,
ya no implementa Price Location / Structure.

Si un modelo solo cambia anchor, referencia, ventana,
denominador o resolucion fisica,
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

Aplicacion a `Price Location / Structure`:

```text
Price Location / Structure es irreducible si TSIS necesita preservar
localizacion contextual del precio frente a referencias legales,
y esa informacion no queda suficientemente preservada por
Price Movement, Volatility / Range State, Trading Activity,
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

| Evidence | En Price Location / Structure | En dominio vecino |
| --- | --- | --- |
| `prior_close` | anchor estructural para posicion actual | referencia temporal para Price Movement |
| `session_open` | anchor de sesion | referencia para return intradia |
| `high_so_far` / `low_so_far` | extremos observados para proximidad o coordenada | componentes de range/volatility si se interpreta amplitud |
| `VWAP` | referencia estructural construida hasta t | puede depender de Trading Activity para su construccion |
| `bar_close_price` | precio actual para medir distancia | precio observado para returns o rangos |

Conclusion:

```text
Shared evidence is allowed.
Shared identity is not assumed.
```

## 6. Boundary / Absorption Tests

| Attack | Question | Review result | Decision |
| --- | --- | --- | --- |
| Absorb into `Price Movement` | Es solo cambio contra referencias? | No. `Price Movement` mide desplazamiento temporal. `Price Location / Structure` mide posicion actual frente a anchors. | `not_absorbed` |
| Absorb into `Volatility / Range State` | Es solo rango o amplitud? | No. Puede usar high/low como coordenadas, pero no mide amplitud o incertidumbre como fenomeno principal. | `not_absorbed` |
| Absorb into `Trading Activity` | VWAP depende de participacion, entonces es activity? | No. VWAP location usa VWAP como referencia de localizacion; no mide intensidad de participacion. | `not_absorbed` |
| Absorb into `Liquidity` | Es solo cercania a zonas ejecutables? | No. Liquidity pregunta por coste, disponibilidad e impacto. Location pregunta donde esta el precio. | `not_absorbed` |
| Absorb into `Outcome Layer` | Future HOD/LOD o future extrema son location? | No como input. Son outcomes o conocimiento posterior. | `outcome_separated` |
| Split `Intraday Position` | Intraday Position merece Objeto propio? | No por defecto. Es perfil temporal de Price Location / Structure. | `representation_profile` |
| Split `VWAP Location` | VWAP Location merece Objeto propio? | No por defecto. Es modelo contra un anchor especifico. | `representation_model` |
| Split `HOD/LOD Proximity` | Cercania a extremos merece Objeto propio? | No por defecto. Es modelo de localizacion contra extremos observados hasta t. | `representation_model` |
| Move `Opening Gap Movement` | Gap pertenece aqui? | Si mide cambio de apertura, pertenece a Price Movement. Si mide distancia actual a prior close, puede ser location model. | `boundary_confirmed` |
| Move `Pullback / Retrace Location` | Es estructura o pattern research? | Fronterizo. Puede ser modelo estructural, pero si codifica setup especifico debe salir del core. | `boundary_model_with_restrictions` |

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
| `session_anchor_location_model` | core location candidate | Representa posicion contra session open o segment anchors legalmente conocidos. |
| `prior_close_location_model` | core / daily-intraday bridge candidate | Representa posicion actual frente a prior close as-of. |
| `vwap_location_model` | intraday representation model | Representa distancia a VWAP construido solo con informacion <= t. |
| `hod_lod_proximity_model` | intraday structure model | Representa cercania a high/low observado hasta t, no HOD/LOD final futuro. |
| `range_position_model` | extension candidate | Representa coordenada dentro del rango observado; debe separarse de Volatility. |
| `pullback_retrace_location_model` | boundary extension | Puede representar estructura relativa reciente, pero roza pattern research. |
| `anchored_vwap_distance_model` | candidate requiring anchor policy | Requiere politica de anchor y construccion de VWAP. |
| `final_daily_structure_model` | after-close / prior-day context only | Prohibido intradia para dia actual antes del cierre. |

## 8. Semantic Capability Versus Minimum Model

Este documento no fija una variable minima obligatoria.

La condicion minima no es:

```text
usar una variable concreta.
```

La condicion minima es:

```text
existir al menos un Representation Model aprobado
capaz de implementar la semantic capability de Price Location / Structure.
```

Condicion minima de representacion:

```text
El modelo debe medir posicion del precio observable en t
contra una referencia estructural declarada,
con fuente observable declarada,
cutoff legal en decision_timestamp,
y sin depender de anchors finales futuros ni labels de estrategia.
```

## 9. Temporal Legality Constraints

Reglas obligatorias:

```text
1. Una barra intradia solo es consumible despues de su cierre.

2. `high_so_far` y `low_so_far` solo pueden incluir informacion <= t.

3. HOD/LOD final del dia solo es legal tras market close
   o como contexto historico de sesiones previas.

4. VWAP debe construirse solo con barras o trades disponibles <= t.

5. `prior_close` debe proceder de una sesion previa conocida as-of.

6. Anchored VWAP requiere politica explicita de anchor.

7. Pullback/retrace requiere ventana cerrada, anchor declarado
   y separacion de pattern labels.

8. Toda fuente 1m derivada debe declarar lineage, version y politica
   de reparacion o quote-guarding cuando aplique.
```

## 10. State Impact If Eventually Accepted

Si se admite formalmente, `Price Location / Structure` debe entrar en State
como Objeto:

```text
Price Location / Structure
    -> approved Representation Models
        -> approved Physical Implementations
            -> legal State profile consumption
```

No debe entrar como:

```text
lista abierta de distancias, returns, ranges, final HOD/LOD,
pattern labels, future extrema o variantes parametrizadas
sin decision de modelo.
```

Perfiles probables:

```text
market_state_core:
    posicion as-of minima contra anchors canonicos.

market_state_intraday:
    VWAP location, HOD/LOD proximity y range position
    con politicas temporales gobernadas.

market_state_event_extension:
    posicion frente a anchors de evento o segmento,
    si el anchor esta definido antes o en decision_timestamp.

outcomes:
    future extrema, future HOD/LOD, future returns, MFE y MAE separados.
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
Price Location / Structure preserva una primary informational uncertainty propia:
donde esta situado el precio frente a referencias estructurales legales.

No necesita evidencia exclusiva para existir.
Comparte precios, anchors, high/low y VWAP con otros dominios,
pero no comparte identidad informacional.

El candidato sobrevive a los principales ataques de absorcion
si se mantiene separado de movement, range/volatility, trading activity,
liquidity, pattern labels y outcomes futuros.
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
seleccion de anchors canonicos, politicas de VWAP,
distancias a HOD/LOD observados, formulas registradas
y controles contra HOD/LOD final del dia usados antes del cierre.
```

Restricciones operativas recomendadas:

```text
1. Mantener core pequeno y semanticamente estable.

2. Tratar `Intraday Position`, `VWAP Location`, `HOD/LOD Proximity`
   y `Prior Close Recovery` como modelos/perfiles, no Objetos separados
   por defecto.

3. Separar estrictamente Price Location / Structure de Price Movement.

4. Separar estrictamente Price Location / Structure de Volatility / Range State.

5. Prohibir HOD/LOD final del dia antes del cierre como input intradia.

6. Exigir VWAP policy antes de autorizar `vwap_location_model`.

7. Mantener pullback/retrace como extension o pattern-research boundary
   hasta resolver su frontera.

8. Registrar o formular explicitamente distance_to_session_hod,
   distance_to_session_lod y session_range_position antes de mapping.
```

## 12. Open Questions For Formal Admission

```text
1. Que Representation Model debe implementar primero la semantic capability?

2. Cual es el perfil minimo de `market_state_core`
   para Price Location / Structure?

3. Que anchors son canonicos:
   session_open, prior_close, VWAP, high_so_far, low_so_far, segment_open?

4. VWAP location entra en core, intraday profile o extension?

5. Deben existir distance_to_session_hod y distance_to_session_lod
   como capacidades atomicas canonicas?

6. Como se define session_range_position sin contaminar Volatility / Range?

7. Que parte de pullback/retrace pertenece a estructura
   y que parte pertenece a pattern discovery o strategy research?
```

## 13. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_location_structure_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_location_structure_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\price_location_structure_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

