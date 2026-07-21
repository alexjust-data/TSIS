# Price Location / Structure - Representation Landscape v0.1

Status: `representation_landscape_v0_1`
Date: `2026-07-20`
Scope: `post_domain_definition_pre_object_admission`

Este documento revisa modelos posibles para `Price Location / Structure`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona el modelo final.
No autoriza variables para `Market State` ni `Event State`.

## Dominio

```text
Price Location / Structure
```

## Candidatos A Objeto Dentro Del Dominio 

| Candidato | Lectura cientifica | Decision pre-admision |
| --- | --- | --- |
| `Price Location / Structure` | Candidato principal. Preserva posicion contextual del precio. | `forward_to_object_admission` |
| `Intraday Position` | Modelo intradia. | `not_separate_object_by_default` |
| `VWAP Location` | Modelo contra referencia de precio medio negociado. | `representation_model_candidate` |
| `HOD/LOD Proximity` | Modelo contra extremos observados hasta t. | `representation_model_candidate` |
| `Prior Close Recovery` | Modelo de posicion contra prior close. | `representation_model_candidate` |
| `Pullback / Retrace Location` | Modelo estructural o pattern-adjacent. | `boundary_model` |
| `Opening Gap Movement` | Cambio discontinuo de apertura. | `belongs_to_price_movement_when_change` |

## Paisaje De Modelos De Representacion 

| Modelo candidato | Que intenta medir | Capacidades derivables relacionadas | Fuentes / tablas | Estado | Riesgo principal |
| --- | --- | --- | --- | --- | --- |
| `session_anchor_location_model` | Posicion del precio contra apertura/sesion/segmento. | `intraday__return_vs_session_open_ratio`, `intraday__return_vs_segment_open_ratio` | OHLCV 1m; `014_master_intraday_bar_table_candidate` | `formula_defined` | Confundir distancia a anchor con movimiento/persistencia. |
| `prior_close_location_model` | Posicion actual respecto a prior close. | `daily__prior_close`, `intraday__return_vs_prior_close_ratio` | Daily + OHLCV 1m; `004`, `014` | `formula_defined` | Confundir con gap o return; requiere price_ref legal en t. |
| `vwap_location_model` | Distancia a VWAP legalmente construido hasta t. | `intraday__vwap_distance_ratio`, `intraday__bar_vwap` | OHLCV 1m; `013`, `014` | `requires_variant` | VWAP debe usar solo barras/trades <= t; fallback policy. |
| `hod_lod_proximity_model` | Cercania a high/low observado hasta t. | `intraday__high_so_far`, `intraday__low_so_far`; distance formulas pending | OHLCV 1m; `014` | `formula_defined_plus_missing_distance_ids` | Prohibido usar HOD/LOD final del dia antes del cierre. |
| `range_position_model` | Coordenada del precio dentro del rango observado hasta t. | `intraday__high_so_far`, `intraday__low_so_far`, `intraday__bar_close_price` | OHLCV 1m; `014` | `candidate_requires_formula` | Puede solaparse con Volatility/Range si se interpreta como amplitud. |
| `pullback_retrace_location_model` | Distancia desde max/min/anchor del movimiento reciente. | `intraday__pullback_ratio_W`, `intraday__retrace_ratio_W` | OHLCV 1m; `014` | `requires_variant` | Puede ser pattern-specific; no core sin admision clara. |
| `final_daily_structure_model` | Posicion contra high/low/close diario final. | daily high/low/close | `004_master_daily_table` | `existing_after_close_only` | No decision-safe intradia para el dia actual. |

## Modelos Que Podrian Ser Redundantes

```text
Prior close location vs Opening gap movement:  Comparten prior_close, pero uno mide posicion actual y el otro cambio discontinuo de apertura.
```

```text
VWAP location vs session anchor location:  Ambos son referencias intradia, pero VWAP depende de participacion negociada, mientras session open es anchor temporal fijo.
```

## Modelos Que
Requieren Separacion

```text
Range/Volatility:  Usar high_so_far y low_so_far como coordenadas no equivale a medir amplitud o incertidumbre.
```

```text
Price Movement:  Distancia actual a referencia no equivale necesariamente a velocidad, aceleracion o persistencia del cambio.
```

```text
Pattern Discovery:  Pullback/retrace puede ser modelo de estructura, pero si se convierte en setup especifico debe vivir fuera del core.
```

## Modelos Bloqueados O No Listos

```text
distance_to_session_hod/lod: blocked_reason:  no aparecen como capacidades atomicas explicitas en el register. missing_source_or_policy:  formula id, denominator, price_ref y cutoff.
```

```text
anchored_vwap_distance: blocked_reason:  requiere anchor policy. missing_source_or_policy:  anchor definition and VWAP construction policy.
```

```text
final_daily_high_low_location: blocked_reason:  no es legal intradia antes del cierre. missing_source_or_policy:  only after-market-close or prior-day context.
```

## Fronteras Para La Admision

```text
1. Que anchors son core y cuales extension?  2. VWAP location entra en core o intraday extension?  3. HOD/LOD proximity necesita capacidades atomicas nuevas?  4. Como se evita usar HOD/LOD final del dia antes del cierre?  5. Pullback/retrace es location estructural o pattern research?  6. Como se separa location de movement y volatility?
```

## Recomendacion Para Object Admission

```text
Abrir un unico expediente candidato:  Price Location / Structure
```

No abrir todavia expedientes separados para:

```text
Intraday Position VWAP Location HOD/LOD Proximity Prior Close Recovery Pullback / Retrace Location
```

## Decision Del Landscape

```text
decision = ready_to_define_candidate_object
```

Motivo:

```text
Existe un Objeto candidato coherente. Los modelos posibles comparten una misma pregunta: donde esta el precio respecto a referencias legales en t?
```

## Resultado Posterior

```text
Candidate Object Definition creado en:  C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\ 03_TABLES_feature_engineering\ 03_INFORMATION_OBJECTS\ CANDIDATES\ price_location_structure_candidate_object_definition_v0_1.md
```

## Siguiente Paso

```text
Continuar bucle cientifico con:  Volatility / Range State  -> Domain Definition  -> Representation Landscape  -> Object Admission
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_location_structure_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\013_ohlcv_1m_quote_guarded\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\table_representation_audit_ES.md
```
