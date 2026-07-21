# Semantic Domain Consolidation v0.1

Status: `semantic_domain_consolidation_v0_1`
Date: `2026-07-20`
Scope: `between_candidate_matrix_and_object_admission`

Este documento clasifica los candidatos descubiertos en `00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md` por naturaleza y por dominio semantico antes de abrir expedientes formales de admision.

No admite Objetos.
No rechaza Objetos.
No autoriza variables para State.
No modifica tablas, schemas, builders ni contratos.

## Por Que Existe

La matriz de candidatos mezcla deliberadamente varios tipos de entidades:

```text
infraestructura
calidad/gobernanza
informacion observable del mercado
representaciones canonicas
outcomes
superficies de seleccion
```

Eso sirve para descubrir.
No sirve todavia para admitir.

Antes de crear expedientes individuales, TSIS debe consolidar dominios para evitar admitir duplicados como si fueran Objetos distintos.

## Regla Principal

```text
La siguiente unidad de trabajo no es una tabla.
La siguiente unidad de trabajo tampoco es aun un Objeto aislado.

La siguiente unidad de trabajo es un cluster semantico
de candidatos relacionados.
```

## Flujo Actual

```text
Table Discovery Pass
    -> Candidate Matrix
        -> Semantic Domain Consolidation
            -> Domain Definition
                -> Representation Landscape
                    -> Object Admission
                        -> Operational Mapping
                            -> State build
```

## Clasificacion Por Naturaleza

### Infrastructure

```text
Instrument Identity
Universe Membership
Trading Session Context
Event Window Context
```

Lectura:

```text
Estos artefactos hacen posible interpretar, unir, cortar
y consumir informacion.

No compiten con Liquidity, Momentum o Trading Activity
como informacion observable del mercado.
```

Proceso recomendado:

```text
institutional/infrastructure review
not market-object admission by default
```

### Quality And Governance

```text
Observability Coverage
Dataset Consumption Eligibility
Representation Quality State
```

Lectura:

```text
Estos objetos gobiernan si una observacion existe,
si es interpretable y si puede consumirse.

No son alfa ni fenomeno economico directo.
```

Proceso recomendado:

```text
quality/governance object review
state gate mapping
not predictive object admission by default
```

### Market Information Domains

```text
Trading Activity
Price Movement
Price Location / Structure
Volatility / Range State
Liquidity
Market Microstructure State
Order Flow Pressure
News / Catalyst Context
Fundamental Context
Short-Side Context
Broad Market Context
Halt Context
```

Lectura:

```text
Estos son los dominios que pueden producir
Objetos de Informacion para Market State y Event State.
```

Proceso recomendado:

```text
domain definition
then formal Object admission
```

### Canonical Core Representations

```text
Market State
Event State
```

Lectura:

```text
No son Objetos comunes.
Son representaciones canonicas core que integran
Objetos admitidos bajo legalidad temporal.
```

Proceso recomendado:

```text
representation governance
not Information Object admission
```

### Outcome Layer

```text
Outcome Response
Future Return Label
MFE MAE Response
```

Lectura:

```text
Pertenecen a evaluacion, labels y medicion posterior.
No pueden entrar como input observable de Market State/Event State.
```

Proceso recomendado:

```text
outcome contract / label governance
not State input admission
```

### Selection Surfaces

```text
Intraday In-Play Candidate
Attention Activity Candidate
```

Lectura:

```text
Son superficies para decidir donde mirar.
No prueban por si solas que exista un Objeto de Informacion admitible.
```

Proceso recomendado:

```text
selection-bias review
scanner governance
possible later context-object review
```

## Domain Definition

Antes de abrir un `Representation Landscape` o un expediente formal de admision, cada cluster debe producir una definicion corta de dominio.

La definicion de dominio responde solo:

```text
Que informacion intenta preservar este dominio?
Que NO representa?
Que preguntas cientificas permite formular?
Donde termina y donde empieza el dominio vecino?
```

No debe listar todas las variables.
No debe decidir todavia el Modelo de Representacion final.
No debe admitir Objetos.

Debe sobrevivir a tres preguntas:

```text
Que informacion preserva?
Por que es diferente de los demas dominios?
Que perderia TSIS si desapareciera?
```

Template activo:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\02_DOMAIN_DEFINITION_TEMPLATE_v0_1.md
```

## Representation Landscape

Despues de definir el dominio, TSIS debe listar el paisaje de modelos de representacion posibles antes de admitir un Objeto.

Esto no selecciona el modelo final.
Solo evita admitir un Objeto en abstracto sin conocer si puede representarse de varias maneras.

Ejemplo:

```text
Liquidity
    -> spread model
    -> depth model
    -> effective spread model
    -> Amihud/Kyle/Roll candidates when data permits
```

Template activo:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\03_REPRESENTATION_LANDSCAPE_TEMPLATE_v0_1.md
```

## Clusters Semanticos De Trabajo

### Cluster 1 - Trading Activity

Incluye:

```text
Trading Activity
Daily Trading Activity
Intraday Trading Activity
Trade Count
Trade Rate
Dollar Volume
Relative Volume
Volume Pace
Attention Activity Candidate
```

Lectura provisional:

```text
Trading Activity parece el Objeto candidato principal.
Daily e Intraday parecen modelos/resoluciones.
Attention Activity parece superficie de seleccion o proxy
pendiente de separar de scanner bias.
```

Pregunta de dominio:

```text
Que informacion sobre intensidad de participacion
merece preservar TSIS y con que modelos temporales?
```

### Cluster 2 - Price Movement

Incluye:

```text
Daily Price State
Intraday Price Dynamics
returns
slope
move speed
move acceleration
gap percent
```

Lectura provisional:

```text
Price Movement debe describir como cambia el precio.
No debe absorber automaticamente localizacion, rango o volatilidad.
```

Pregunta de dominio:

```text
Que informacion sobre direccion, velocidad y aceleracion
del precio debe preservarse?
```

### Cluster 3 - Price Location / Structure

Incluye:

```text
Intraday Position
distance to VWAP
distance to HOD
distance to LOD
distance to session open
distance to prior close
Overnight Dislocation
```

Lectura provisional:

```text
Price Location responde donde esta el precio
respecto a referencias, no como se mueve.
```

Pregunta de dominio:

```text
Que referencias estructurales hacen interpretable
el precio en decision_timestamp?
```

### Cluster 4 - Volatility / Range

Incluye:

```text
Daily Volatility Range
Intraday Volatility
daily range
range so far
rolling volatility
compression
expansion
```

Lectura provisional:

```text
Puede ser Objeto propio o modelo especializado de Price Movement.
No debe decidirse hasta comparar su funcion cientifica.
```

Pregunta de dominio:

```text
Que informacion sobre amplitud, dispersion e incertidumbre
debe conservarse?
```

### Cluster 5 - Liquidity And Tradability

Incluye:

```text
Liquidity
spread
spread bps
top depth
quote count
quote update rate
dollar volume proxy
trade count proxy
```

Lectura provisional:

```text
Liquidity parece Objeto candidato fuerte.
Debe separar modelos L1/trades de proxies diarios o intradia.
```

Pregunta de dominio:

```text
Que informacion permite estimar facilidad, coste
y disponibilidad de negociacion?
```

### Cluster 6 - Microstructure And Order Flow

Incluye:

```text
Market Microstructure State
Order Flow Pressure
quote condition
locked/crossed
signed flow
aggressor imbalance
OFI candidates
```

Lectura provisional:

```text
Microstructure State puede ser un dominio general.
Order Flow Pressure puede ser Objeto propio o modelo interno,
pero depende de alignment y clasificacion trade-quote.
```

Pregunta de dominio:

```text
Que informacion del tape y del top-of-book cambia
la interpretacion del estado del mercado?
```

### Cluster 7 - External Context

Incluye:

```text
News / Catalyst Context
Fundamental Context
Short-Side Context
Capital Structure Context
Crowding Context
```

Lectura provisional:

```text
Son contextos externos con politicas as-of y lag.
No deben mezclarse con observables intradia sin prueba temporal.
```

Pregunta de dominio:

```text
Que informacion externa observable cambia la interpretacion
del instrumento o del evento?
```

### Cluster 8 - Broad Market And Regime Context

Incluye:

```text
Broad Market Context
Market Regime
index return
volatility proxy
risk-on/off state
```

Lectura provisional:

```text
Broad Market Context podria ser el Objeto padre.
Market Regime podria ser modelo de representacion
o Objeto propio si justifica identidad cientifica separada.
```

Pregunta de dominio:

```text
Que informacion del entorno general condiciona
el comportamiento del instrumento?
```

### Cluster 9 - Event And Interruption Context

Incluye:

```text
Halt Context
Regulatory Venue Interruption
Event Window Context
Event Relative Time
```

Lectura provisional:

```text
Halt Context puede ser contexto observable de interrupcion.
Event Window Context es infraestructura temporal de evento.
Event State no crea eventos; consume evento gobernado y ventana.
```

Pregunta de dominio:

```text
Que informacion contextualiza correctamente el mercado
respecto a un evento o interrupcion?
```

## Correccion A La Matriz v0.1

La matriz `00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md` proponia abrir expedientes de admision como siguiente paso.

Interpretacion actual:

```text
No abrir todavia expedientes de admision individuales.
Primero ejecutar Semantic Domain Consolidation.
```

Motivo:

```text
Un mismo dominio puede contener varios nombres crudos
que no son Objetos separados:

Objeto
modelo
resolucion temporal
contexto
superficie de seleccion
```

## Decision

```text
candidate_matrix_reviewed = true
semantic_domain_consolidation_required = true
object_admission_started = false
objects_admitted = 0
state_consumption_authorized = false
next_step = domain_definition_cluster_1_trading_activity
```

## Evidencia Base

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\00_DISCOVERY_PASS_000_018_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
