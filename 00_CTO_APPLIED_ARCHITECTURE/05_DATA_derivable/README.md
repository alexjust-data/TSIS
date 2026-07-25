# 05_DATA_derivable

Status: `derivable_layer_v0_3_atomic_capability_boundary`
Date: `2026-07-20`
Knowledge state: `secondary_summary`

## Regla Central

```text
Simplicidad primero.

Cada capa debe responder una sola pregunta
y no invadir las decisiones de la capa siguiente.
```

Esta carpeta responde una sola pregunta:

```text
Con la RAW data o data gobernada disponible actualmente en TSIS,
que capacidades de derivacion y observables pueden calcularse legalmente?
```

## Posicion En La Arquitectura

```text
04_DATA_Raw_audit
Que campos y fuentes existen realmente?

        ->

05_DATA_derivable
Que capacidades derivables pueden calcularse legalmente desde esas fuentes?

        ->

03_TABLES_feature_engineering
Que significado tienen esas capacidades/atributos,
como se organizan y cuales merecen formar parte
de la representacion del mercado?
```

## Principio Fundamental

```text
Una capacidad de derivacion no implica que deba utilizarse
para representar el estado del mercado.

05_DATA_derivable responde unicamente:

Puede calcularse de forma legal,
reproducible y gobernada?

La utilidad cientifica de esa capacidad
se decide posteriormente.
```

Esto evita el error operativo:

```text
Como puedo calcularlo,
entonces debo usarlo.
```

## Regla Atomica Del Registro

```text
Una fila del register = una capacidad derivable canonica.
```

Una fila no debe mezclar varias capacidades distintas.

Correcto:

```text
daily__gap_pct
daily__daily_return_pct
daily__daily_range_pct
intraday__move_speed_W
intraday__move_acceleration_W
```

Incorrecto como fila del register:

```text
daily__return_range_metrics
intraday__shape_pace_W
daily__adjustable_Nd_families
```

Esos agrupadores pueden vivir en el catalogo narrativo, no en el register operativo.

Las variantes `W`, `N`, `baseline`, `price_ref` o `statistic` no se expanden hasta que haga falta. Se declaran como parametros requeridos de una capacidad canonica.

## Que Hace Esta Carpeta

Registra capacidad tecnica de derivacion:

```text
raw_source
raw_fields_required
derivation_definition
variant_required
required_variant_fields
cutoff legal
quality requirements
estado operativo
materializaciones conocidas o candidatas
```

No asigna significado cientifico.
No admite Information Objects.
No decide pertenencia a Market State ni Event State.
No sustituye schemas, builders, validators, manifests ni status matrices.

## Documentos Activos

```text
README.md
00_DATA_DERIVABLE_CATALOG_BY_RAW_SOURCE_v0_1.md
01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
02_DERIVABLE_CAPABILITY_STATUS_MATRIX_v0_1.md
99_archive/
```

## Estados Locales

```text
existing
formula_defined
requires_variant
candidate
blocked_no_source
prohibited_as_feature
```

## Cutoffs Permitidos

```text
yes_at_source_timestamp
yes_after_bar_close
yes_after_session_open
yes_after_market_close
yes_with_asof_cutoff
yes_with_closed_window
no_future_or_prohibited
```

## Autoridades De Referencia

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\raw_data_authority_and_derivation_map.md
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_quality_report\family_status_matrix_v0_1.md
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\state_observable_eligibility_contract_v0_1.md
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\state_derived_observables_formula_contract_v0_1.md
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\state_decision_timestamp_policy_v0_1.md
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_contract_v0_1.md
```

## Regla Final

```text
05_DATA_derivable registra capacidad de calculo.
03_TABLES_feature_engineering decide significado y admision.
```

