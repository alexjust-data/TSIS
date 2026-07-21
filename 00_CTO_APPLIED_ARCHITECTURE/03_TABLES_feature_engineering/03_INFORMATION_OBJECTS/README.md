# 03_INFORMATION_OBJECTS

Status: `information_objects_index_v0_7_ontology_v1_frozen`
Date: `2026-07-21`

Esta carpeta guarda la capa semantica entre las capacidades derivables y la construccion posterior de Market State / Event State.

`TSIS Market Ontology v1` esta congelada y bloqueada. La unidad activa de trabajo ya no es Formal Admission transversal, sino Phase B gobernada, empezando por Operational Mapping de los Information Objects admitidos.

## Definicion

```text
Objeto de Informacion
=
unidad semantica de informacion que TSIS decide preservar
sobre uno o varios fenomenos observables,
independiente de su Modelo de Representacion
y de su implementacion fisica.
```

El Objeto no es aun la representacion. Es lo que debe ser representado.

Ejemplo:

```text
Liquidity
= Objeto de Informacion

coste de negociacion + profundidad + disponibilidad
= Modelo de Representacion

spread_bps + depth + quote_count
= implementacion fisica / variables
```

## Dominio vs Objeto

```text
Dominio
=
espacio cientifico de informacion observable.

Objeto de Informacion
=
unidad semantica candidata o admitida dentro de un dominio.

Modelo de Representacion
=
forma concreta de expresar el Objeto mediante capacidades y variables.
```

Un dominio puede estar suficientemente definido sin que ningun Objeto este aun admitido.

## Taxonomias Separadas

Cada expediente debe separar estos ejes:

```text
information_object_family
= semantica del Objeto o dominio.

source_domain
= fuente observable.

temporal_resolution
= escala o ventana temporal.

institutional_role
= funcion institucional.
```

No usar `family` como campo unico. Una familia semantica de Objetos no es lo mismo que una Feature Family historica, una fuente, una resolucion temporal o un rol de calidad/gobernanza.

## Principio Semantico

```text
El significado no pertenece a una variable aislada.

Pertenece a:

Dominio
    -> Objeto de Informacion
        -> Modelo de Representacion
            -> Uso temporalmente legal
```

Una misma variable fisica puede tener significados distintos en dominios distintos. Por ejemplo, `dollar_volume` puede ser actividad negociada en `Trading Activity` y proxy de tradability en `Liquidity`.

## Orden De Trabajo

```text
00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
    -> candidatos descubiertos en tablas 000-018

01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
    -> agrupacion por naturaleza y clusters semanticos

02_DOMAIN_DEFINITION_TEMPLATE_v0_1.md
    -> plantilla corta para definir cada dominio

03_REPRESENTATION_LANDSCAPE_TEMPLATE_v0_1.md
    -> plantilla corta para revisar modelos posibles

04_TSIS_MARKET_ONTOLOGY_PHASE_v0_1.md
    -> regla de fase: completar admisiones formales antes de expandir ingenieria

DOMAIN_DEFINITIONS/
    -> definiciones reales de dominio y representation landscapes

CANDIDATES/
    -> definiciones candidatas de Objetos, aun sin admision formal

CANDIDATES/object_admission_review/
    -> revision adversarial / peer-review antes de admision formal

ACCEPTED / ACCEPTED_WITH_RESTRICTIONS / REJECTED
    -> decisiones formales de admision del Objeto
```

No crear un expediente por cada nombre crudo detectado en una tabla. Primero debe verificarse si el nombre es Dominio, Objeto, Modelo de Representacion, especializacion temporal, contexto, calidad/gobernanza, outcome o superficie de seleccion.

## Estados

```text
domain_defined
representation_landscape_defined
candidate_object_defined
accepted
accepted_with_restrictions
rejected
```

## Regla

```text
Las tablas pueden descubrir candidatos.
Los dominios ordenan el espacio cientifico.
La admision formal decide que Objetos existen institucionalmente.
```

## Estado Actual

```text
formal_object_admission = started
first_formal_admission_object = Trading Activity
first_formal_admission_status = accepted_with_restrictions
state_variables_authorized = false
physical_variables_authorized = false
schema_change_authorized = false
builder_change_authorized = false
operational_mapping_design_started = true
operational_consumption_authorized = false
```

Estado de los 12 dominios principales:

```text
Trading Activity:
    domain_definition = complete
    representation_landscape = complete
    candidate_object_definition = complete
    object_admission_review = complete
    formal_object_admission = accepted_with_restrictions
    operational_mapping_design = complete
    builder_validation_design = complete
    market_state_integration_design = proposed_pending_validation
    state_variables_authorized = false

Remaining 11 domains:
    domain_definition = complete
    representation_landscape = complete
    candidate_object_definition = complete
    object_admission_review = complete
    formal_object_admission = not_started
    state_variables_authorized = false
```

## Expedientes Activos

```text
Trading Activity
    domain_definition = DOMAIN_DEFINITIONS/trading_activity_domain_definition_v0_1.md
    representation_landscape = DOMAIN_DEFINITIONS/trading_activity_representation_landscape_v0_1.md
    candidate_object = CANDIDATES/trading_activity_candidate_object_definition_v0_1.md
    object_admission_review = CANDIDATES/object_admission_review/trading_activity_v0_1.md
    formal_admission = ACCEPTED_WITH_RESTRICTIONS/trading_activity_formal_admission_v0_1.md
    formal_object_admission = accepted_with_restrictions
    operational_mapping = ../04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/trading_activity_operational_mapping_v0_1.md
    builder_validation = ../05_STATE_BUILDER_VALIDATION/trading_activity_builder_validation_v0_1.md
    market_state_integration = ../06_MARKET_STATE_INTEGRATION/trading_activity_market_state_integration_v0_1.md
    state_variables_authorized = false

Price Movement
    domain_definition = DOMAIN_DEFINITIONS/price_movement_domain_definition_v0_1.md
    representation_landscape = DOMAIN_DEFINITIONS/price_movement_representation_landscape_v0_1.md
    candidate_object = CANDIDATES/price_movement_candidate_object_definition_v0_1.md

Price Location / Structure
    domain_definition = DOMAIN_DEFINITIONS/price_location_structure_domain_definition_v0_1.md
    representation_landscape = DOMAIN_DEFINITIONS/price_location_structure_representation_landscape_v0_1.md
    candidate_object = CANDIDATES/price_location_structure_candidate_object_definition_v0_1.md

Volatility / Range State
    domain_definition = DOMAIN_DEFINITIONS/volatility_range_state_domain_definition_v0_1.md
    representation_landscape = DOMAIN_DEFINITIONS/volatility_range_state_representation_landscape_v0_1.md
    candidate_object = CANDIDATES/volatility_range_state_candidate_object_definition_v0_1.md

Liquidity
    domain_definition = DOMAIN_DEFINITIONS/liquidity_domain_definition_v0_1.md
    representation_landscape = DOMAIN_DEFINITIONS/liquidity_representation_landscape_v0_1.md
    candidate_object = CANDIDATES/liquidity_candidate_object_definition_v0_1.md

Market Microstructure State
    domain_definition = DOMAIN_DEFINITIONS/market_microstructure_state_domain_definition_v0_1.md
    representation_landscape = DOMAIN_DEFINITIONS/market_microstructure_state_representation_landscape_v0_1.md
    candidate_object = CANDIDATES/market_microstructure_state_candidate_object_definition_v0_1.md

Order Flow Pressure
    domain_definition = DOMAIN_DEFINITIONS/order_flow_pressure_domain_definition_v0_1.md
    representation_landscape = DOMAIN_DEFINITIONS/order_flow_pressure_representation_landscape_v0_1.md
    candidate_object = CANDIDATES/order_flow_pressure_candidate_object_definition_v0_1.md

News / Catalyst Context
    domain_definition = DOMAIN_DEFINITIONS/news_catalyst_context_domain_definition_v0_1.md
    representation_landscape = DOMAIN_DEFINITIONS/news_catalyst_context_representation_landscape_v0_1.md
    candidate_object = CANDIDATES/news_catalyst_context_candidate_object_definition_v0_1.md

Fundamental Context
    domain_definition = DOMAIN_DEFINITIONS/fundamental_context_domain_definition_v0_1.md
    representation_landscape = DOMAIN_DEFINITIONS/fundamental_context_representation_landscape_v0_1.md
    candidate_object = CANDIDATES/fundamental_context_candidate_object_definition_v0_1.md

Short-Side Context
    domain_definition = DOMAIN_DEFINITIONS/short_side_context_domain_definition_v0_1.md
    representation_landscape = DOMAIN_DEFINITIONS/short_side_context_representation_landscape_v0_1.md
    candidate_object = CANDIDATES/short_side_context_candidate_object_definition_v0_1.md

Broad Market Context
    domain_definition = DOMAIN_DEFINITIONS/broad_market_context_domain_definition_v0_1.md
    representation_landscape = DOMAIN_DEFINITIONS/broad_market_context_representation_landscape_v0_1.md
    candidate_object = CANDIDATES/broad_market_context_candidate_object_definition_v0_1.md

Halt Context
    domain_definition = DOMAIN_DEFINITIONS/halt_context_domain_definition_v0_1.md
    representation_landscape = DOMAIN_DEFINITIONS/halt_context_representation_landscape_v0_1.md
    candidate_object = CANDIDATES/halt_context_candidate_object_definition_v0_1.md

Event Window Context
    classification = infrastructure_context
    formal_object_admission = not_applicable
    state_variables_authorized = false
    note = event windows govern event-relative slicing; they are not market information by themselves.
```

## Regla De Lock De Ontologia v1

No crear mas capas de revision cientifica salvo contradiccion estructural real.

La metodologia de admision queda congelada.
`TSIS Market Ontology v1` queda frozen/locked.
Phase A queda cerrada.

Artefactos de cierre:

```text
Formal Admissions
    -> Cross-Object Ontology Review
        -> TSIS Market Ontology v1 Freeze
```

El trabajo activo posterior al freeze es Phase B:

```text
Operational Mapping
    -> Builder Validation
        -> Market State Integration
            -> Event State Integration
                -> Operational Promotion
```

El vertical completo de Trading Activity se conserva como:

```text
pilot_vertical_artifact
proof_of_process
not_operational_authority
```

La apertura de Phase B no autoriza por si sola:

```text
production builders
State consumption
schema changes
physical materialization
dataset promotion
```