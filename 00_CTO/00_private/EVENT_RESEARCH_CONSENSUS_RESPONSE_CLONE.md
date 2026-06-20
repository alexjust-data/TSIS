# Event Research y Event Engine v0.1

Fecha: 2026-06-20  
Estado: clon maquetado en Markdown de la respuesta conversacional.  
Alcance: borrador de consenso, no materializacion contractual.

## 1. Fase Event Research Desde Cero

Propongo que empecemos por consensuar solo esto, sin tocar archivos:

### Definicion de alcance

1. Que entregables debe producir esta fase.
2. Que NO debe producir todavia.
3. Que data puede alimentar eventos desde `01_foundations/data_quality_report/families`.
4. Que estados tendra un evento: idea, draft, detector candidate, validado, promovido, etc.
5. Que contrato minimo debe tener cualquier evento antes de escribir detectores.

Mi propuesta para el primer micro-paso es discutir el punto 1: que entregables exactos esperamos de esta fase antes de pasar a Event Engine.

## 2. Entregables Propuestos

Para el punto 1, yo separaria los entregables de esta fase en dos bloques: Event Research y pre-Event Engine.

### Entregables Event Research

1. **Event Research Scope**: que es un evento, que no es, y frontera estricta con setup/estrategia/decision.
2. **Event Family Taxonomy v0.1**: familias iniciales de eventos, sin pretender que sean definitivas.
3. **Event Definition Contract v0.1**: plantilla obligatoria para definir cualquier evento.
4. **Event Lifecycle**: estados de promocion de un evento desde `source_note` hasta `promoted`.
5. **Event Input Authority Matrix**: que familias de data pueden alimentar eventos y con que restricciones.
6. **Initial Event Backlog**: lista inicial de eventos candidatos, todavia sin validarlos.

### Entregables Pre-Event Engine

1. **event_table Conceptual Contract v0.1**: columnas minimas, lineage y semantica.
2. **Detector Candidate Contract v0.1**: que necesita una definicion para convertirse en detector.
3. **Event Versioning Rules**: como versionar cambios en definicion de eventos.
4. **Event Reproducibility Requirements**: dataset version, input view, detector version, commit/run metadata.
5. **Event Quality Flags**: como marcar eventos con data incompleta, blocked inputs o ambiguedad.

### Fuera De Esta Fase

Lo que yo no incluiria todavia en esta fase:

- codigo de detectores;
- backtests;
- outcome labels finales;
- estrategias;
- reglas de entrada/salida;
- modelos ML;
- AlphaEvolve;
- eventos `institutional`;
- claims de edge.

Mi recomendacion: consensuar primero esta lista de entregables. Si estas de acuerdo, el siguiente micro-paso seria discutir uno por uno los entregables y fijar cuales son obligatorios para cerrar la fase v0.1.

## 3. Alcance Inicial v0.1

Para cerrar el primer acuerdo, mi propuesta es que la fase v0.1 quede definida por estos entregables obligatorios:

1. Event Research Scope
2. Event Family Taxonomy v0.1
3. Event Definition Contract v0.1
4. Event Lifecycle
5. Event Input Authority Matrix
6. Initial Event Backlog
7. event_table Conceptual Contract v0.1
8. Detector Candidate Contract v0.1
9. Event Versioning Rules
10. Event Quality Flags

Mi recomendacion es aceptar estos 10 como alcance v0.1, porque separan bien:

- definicion conceptual;
- dependencia de data;
- promocion institucional;
- puente hacia Event Engine.

## 4. Scope Negativo v0.1

Para avanzar sin editar nada, dejo el punto 2 propuesto: que no entra todavia en esta fase.

### Fuera De Alcance

1. No crear eventos promovidos como `institutional`.
2. No escribir detectores productivos.
3. No generar `event_table` materializada.
4. No correr backtests.
5. No definir entradas, stops, targets, sizing ni gestion de posicion.
6. No crear estrategias.
7. No medir edge.
8. No crear outcome labels finales.
9. No entrenar ML.
10. No usar AlphaEvolve/OpenEvolve.
11. No activar RL ni Decision Models.
12. No consumir familias de data bloqueadas como si fueran limpias.
13. No redefinir Data Foundation desde `00_CTO`.
14. No modificar contracts de `01_foundations` dentro de esta fase.
15. No reconstruir Graphify salvo que luego decidamos documentar y ejecutar una ventana especifica.

### Frase Resumen

Esta fase define como TSIS nombra, gobierna, versiona y prepara eventos para deteccion futura; no detecta, valida, opera ni monetiza eventos todavia.

## 5. Data Que Puede Alimentar Event Research

Yo lo dividiria en cuatro niveles de autoridad para evitar que el Event Engine nazca contaminado.

### Nivel A: Inputs Base Permitidos

Estos pueden alimentar definiciones de eventos v0.1, siempre citando su contrato/policy:

| Familia | Uso permitido en Event Research |
|---|---|
| `halts_v0_1` | Eventos/regulatory context, halt overlays, halt continuation/failure context. |
| `reference_v0_1` | Identidad, lifecycle, corporate actions, splits/dividends, ticker history. |
| `daily_adjusted_v0_1` | Contexto daily ajustado declarado, labels daily ajustados, comparacion split/dividend-aware. |
| `ohlcv_1m_split_normalized_v0_1` | Intraday split-sensitive research, no como raw 1m universal. |
| `additional_v0_1` | Contexto auxiliar por subfamilia: news, IPOs, macro, secondary corporate actions. |

### Nivel B: Inputs Permitidos Con Scope Limitado

| Familia | Restriccion |
|---|---|
| `intraday_regime_features_v0_1` | Solo pilot/research scoped. No production feature store. |
| `short_review_finra_v0_1` | Solo provenance/source-scope short context. No short replacement. |
| core `daily`, `quotes`, `trades`, `ohlcv_1m` | Usables si nos apoyamos en sus contracts/dossiers especificos, no solo en esta carpeta `families`. |

### Nivel C: Inputs Bloqueados Para Eventos v0.1

| Familia | Regla |
|---|---|
| `financial_v0_1` | Bloqueado para consumo de eventos hasta repair/reaudit. Puede informar deuda o diseno futuro, no deteccion. |
| `regime_indicators_v0_1` daily | Bloqueado por fechas 1970. |
| `regime_indicators_v0_1` minute | Review/scoped unicamente; no base canonica de eventos. |

### Nivel D: Regla General

Un evento puede declarar un input bloqueado o scoped como dependencia futura, pero no puede usarlo como condicion obligatoria de detector v0.1 si ese input no esta permitido para consumo.

La consecuencia practica: los primeros eventos deberian apoyarse en precio/volumen, reference, halts y contexto auxiliar gobernado, pero no en fundamentals financieros ni regime daily hasta que esten reparados.

## 6. Estados De Vida De Un Evento

Propongo estos estados, separados entre conocimiento conceptual y capacidad tecnica:

| Estado | Significado |
|---|---|
| `source_note` | Idea cruda desde nota privada, experiencia humana, Sersan, revision visual o conversacion. No gobierna nada. |
| `event_idea` | Fenomeno formulado claramente: que parece ocurrir, por que importa y que lo distinguiria de otros eventos. |
| `draft_definition` | Tiene nombre, familia, descripcion, condiciones observables, inputs requeridos y exclusiones. Todavia no es detector. |
| `detector_candidate` | La definicion ya puede traducirse a reglas detectables, con inputs permitidos y ambiguedades documentadas. |
| `detector_specified` | Existe especificacion formal del detector, columnas requeridas, parametros, versionado y flags de calidad. Aun puede no haber codigo. |
| `event_table_candidate` | Puede generar filas candidatas en una futura `event_table`, con lineage y quality flags definidos. |
| `outcome_ready` | El evento esta listo para ser medido por Outcome Research. No significa que tenga edge. |
| `validated_event` | La deteccion y la medicion de outcomes son reproducibles y suficientemente revisadas para uso de research. |
| `promoted_event` | Evento gobernado como referencia activa dentro de TSIS. Requiere version, contrato, detector, lineage, evidence y changelog si aplica. |
| `deprecated_event` | Se conserva por trazabilidad, pero no debe usarse para nuevo research salvo migracion explicita. |
| `archived_event` | Congelado como memoria historica, fallo o concepto reemplazado. |

### Reglas Fuertes

Ningun evento pasa de `draft_definition` a `detector_candidate` si depende de data bloqueada como input obligatorio.

`validated_event` no significa estrategia rentable; solo significa que el fenomeno esta definido, detectado y medido de forma reproducible.

Mi recomendacion: usar estos estados como lifecycle v0.1.

## 7. Contrato Minimo De Un Evento

Para que un evento exista como `draft_definition`, exigiria este contrato minimo:

```yaml
event_id: pm_squeeze_event
event_name: PM_Squeeze_Event
version: 0.1.0
status: draft_definition
family: MOMENTUM_EXPANSION

definition:
  short_description:
  market_question:
  observable_phenomenon:
  why_it_matters:

boundaries:
  is_event_because:
  is_not_strategy_because:
  explicitly_not:
    - entry_rule
    - stop_loss
    - target
    - sizing
    - execution_instruction

observable_conditions:
  required:
    - condition_name:
      description:
      input_family:
      field_or_proxy:
      threshold_type: fixed | relative | percentile | categorical | TBD
      threshold_value:
      notes:
  optional:
    - condition_name:
      description:
      input_family:
      field_or_proxy:
      notes:

required_inputs:
  allowed:
    - input_family:
      status:
      use:
      governing_report_or_contract:
  restricted:
    - input_family:
      restriction:
      allowed_use:
  blocked:
    - input_family:
      reason:
      consequence:

candidate_features:
  - feature_name:
    source:
    semantic_role:
    required_for_detector: true | false

exclusions:
  - exclusion_name:
    reason:
    required_input:

ambiguities:
  - ambiguity:
    consequence:
    proposed_resolution:

quality_flags:
  - flag_name:
    meaning:
    severity: info | review | blocked

detector_readiness:
  status: not_ready | candidate | specified
  missing_requirements:
  minimum_detector_inputs:
  expected_output_granularity: ticker_day | ticker_session | intraday_window | event_interval

event_table_mapping:
  expected_primary_key:
  required_lineage:
  required_quality_flags:
  fields_expected_from_detector:

promotion_requirements:
  next_state:
  required_evidence:
  required_review:
```

### Boundary Rules

La parte critica es `boundaries`: cada evento debe demostrar explicitamente que no es estrategia.

Si una definicion necesita una entrada, stop, target o sizing para tener sentido, no es todavia una definicion de evento valida.

Un evento puede incluir umbrales de observacion, pero no instrucciones de accion.

## 8. Taxonomia Inicial De Familias

Yo mantendria la estructura actual como familias v0.1 organizativas, no como verdad definitiva.

| Familia | Pregunta que responde | Ejemplos candidatos |
|---|---|---|
| `MOMENTUM_EXPANSION` | Se esta expandiendo atencion, precio y volumen de forma anomala? | `PM_Squeeze_Event`, `Gap_And_Go_Event`, `Opening_Drive_Event`, `Parabolic_Expansion_Event` |
| `VWAP_CONTROL` | Esta cambiando el control intradia alrededor de VWAP? | `VWAP_Reclaim_Event`, `VWAP_Loss_Event`, `VWAP_Bounce_Event`, `VWAP_Rejection_Event` |
| `INTRADAY_REVERSALS` | Esta cambiando la direccion/control intradia? | `Red_To_Green_Event`, `Green_To_Red_Event`, `Gap_And_Crap_Reversal_Event` |
| `MOMENTUM_EXHAUSTION` | La expansion previa empieza a fallar o agotarse? | `Failed_Breakout_Event`, `Bull_Trap_Event`, `Parabolic_Top_Event`, `Late_Day_Fade_Event` |
| `RUNNER_LIFECYCLE` | En que fase del ciclo de runner esta el ticker? | `First_Green_Day_Event`, `First_Red_Day_Event`, `Multi_Day_Runner_Event`, `Runner_Collapse_Event` |
| `RESISTANCE_AND_BREAKOUTS` | El precio interactua con un nivel relevante? | `PMH_Breakout_Event`, `Previous_Day_High_Breakout_Event`, `Resistance_Test_Event`, `Daily_Level_Breakout_Event` |
| `SHORT_SQUEEZE_DYNAMICS` | Hay contexto o dinamica compatible con presion short/forced covering? | `SSR_Triggered_Event`, `Short_Squeeze_Event`, `Forced_Covering_Event`, `High_Short_Interest_Event` |
| `HALT_AND_REOPEN` | Hay interrupcion/reapertura que cambia el estado del evento? | `Halt_Event`, `Halt_Reopen_Event`, `Halt_Continuation_Event`, `Halt_Failure_Event` |
| `CATALYST_AND_ATTENTION` | Hay catalyst/atencion externa asociada al movimiento? | `News_Catalyst_Event`, `IPO_Context_Event`, `Unusual_Attention_Event` |
| `LIQUIDITY_AND_SPREAD_STATE` | El evento depende de liquidez/spread/fragilidad del libro? | `Liquidity_Vacuum_Event`, `Spread_Expansion_Event`, `Spread_Compression_Event` |
| `EXPERIMENTAL` | Ideas no promovidas o descubiertas por Pattern/Cluster/AlphaEvolve. | `TBD` |

### Familias Nuevas Propuestas

1. `HALT_AND_REOPEN`, porque `halts_v0_1` esta `complete_import_ready` y es una capa de evento real.
2. `CATALYST_AND_ATTENTION`, porque `additional_v0_1` permite news/IPOs/macro como contexto auxiliar.
3. `LIQUIDITY_AND_SPREAD_STATE`, porque microestructura es central en TSIS y probablemente quotes/trades/1m la alimentaran.

### Regla

Una familia no valida sus eventos. Solo organiza el espacio conceptual.

La validacion ocurre despues mediante detector + `event_table` + outcome research.

## 9. Initial Event Backlog v0.1

Lo dejaria como backlog conceptual, no como eventos definidos. Cada item seria solo una hipotesis de fenomeno observable que despues tendra que pasar por el contrato.

### Regla De Prioridad

| Prioridad | Significado |
|---|---|
| `P0` | Eventos simples, centrales y aptos para probar contratos. |
| `P1` | Eventos importantes pero con mas dependencia contextual. |
| `P2` | Eventos valiosos pero con mayor riesgo semantico o dependencia de inputs complejos. |

### Backlog

| Prioridad | Evento candidato | Familia | Por que entra pronto |
|---|---|---|---|
| `P0` | `PM_Squeeze_Event` | `MOMENTUM_EXPANSION` | Nucleo natural de small caps: gap, float, PM volume, push, pullback. |
| `P0` | `Gap_And_Go_Event` | `MOMENTUM_EXPANSION` | Evento base para runners intradia y research posterior. |
| `P0` | `VWAP_Reclaim_Event` | `VWAP_CONTROL` | Fenomeno observable frecuente; frontera clara con estrategia. |
| `P0` | `Red_To_Green_Event` | `INTRADAY_REVERSALS` | Evento simple, medible, util para validar estructura. |
| `P0` | `Halt_Event` | `HALT_AND_REOPEN` | Tenemos `halts_v0_1` con consumo permitido para `event_engine`. |
| `P1` | `Halt_Reopen_Event` | `HALT_AND_REOPEN` | Necesario para continuation/failure posterior. |
| `P1` | `Halt_Continuation_Event` | `HALT_AND_REOPEN` | Fenomeno de mercado, no entrada. |
| `P1` | `Halt_Failure_Event` | `HALT_AND_REOPEN` | Complementa la rama de continuation. |
| `P1` | `SSR_Triggered_Event` | `SHORT_SQUEEZE_DYNAMICS` | Puede apoyarse en precio; short data queda scoped/provenance. |
| `P1` | `Short_Squeeze_Context_Event` | `SHORT_SQUEEZE_DYNAMICS` | Importante, pero no debe depender de short data bloqueada/no completa. |
| `P1` | `First_Green_Day_Event` | `RUNNER_LIFECYCLE` | Lifecycle diario observable. |
| `P1` | `First_Red_Day_Event` | `RUNNER_LIFECYCLE` | Complemento natural para runner lifecycle. |
| `P1` | `PMH_Breakout_Event` | `RESISTANCE_AND_BREAKOUTS` | Evento de nivel; no implica entrada. |
| `P1` | `Previous_Day_High_Breakout_Event` | `RESISTANCE_AND_BREAKOUTS` | Nivel daily simple y trazable. |
| `P2` | `News_Catalyst_Event` | `CATALYST_AND_ATTENTION` | Util, pero requiere attribution-aware handling. |
| `P2` | `IPO_Context_Event` | `CATALYST_AND_ATTENTION` | Sparse event context; no core detector inicial. |
| `P2` | `Liquidity_Vacuum_Event` | `LIQUIDITY_AND_SPREAD_STATE` | Importante, pero depende de microstructure inputs mas delicados. |
| `P2` | `Spread_Expansion_Event` | `LIQUIDITY_AND_SPREAD_STATE` | Requiere quotes/spread quality policy. |
| `P2` | `Parabolic_Expansion_Event` | `MOMENTUM_EXPANSION` | Potente pero mas dificil de definir sin contaminar con estrategia. |
| `P2` | `Parabolic_Top_Event` | `MOMENTUM_EXHAUSTION` | Riesgo alto de mezclar con short strategy; mejor postergar. |

### Eventos Piloto Recomendados

Para empezar de verdad, yo elegiria 3 eventos piloto:

1. `PM_Squeeze_Event`
2. `VWAP_Reclaim_Event`
3. `Halt_Event`

Cubren tres naturalezas distintas:

- expansion de momentum;
- control intradia;
- evento exogeno/regulatorio.

Eso prueba si el contrato sirve sin meternos todavia en estrategias.

## 10. Event Table Conceptual Contract v0.1

La `event_table` no debe ser una tabla de trades. Debe ser una tabla de fenomenos observados.

### Unidad De Fila

Una fila = una ocurrencia detectada de un evento para un ticker, en una fecha/sesion/intervalo concreto.

No representa:

- trade;
- posicion;
- senal;
- orden;
- decision;
- setup operable.

### Clave Conceptual

`event_instance_id`

Derivada de:

- `event_type`;
- `event_definition_version`;
- `ticker`;
- `event_date`;
- `event_start_ts`;
- `event_end_ts`;
- `detector_version`;
- `input_dataset_versions`.

### Columnas Minimas

```yaml
identity:
  - event_instance_id
  - event_type
  - event_family
  - event_definition_version
  - detector_version
  - event_status

security:
  - ticker
  - canonical_security_id
  - symbol_valid_from
  - symbol_valid_to
  - identity_quality_flag

time:
  - event_date
  - session_type
  - event_start_ts
  - event_end_ts
  - detection_ts
  - timezone
  - calendar_quality_flag

data_lineage:
  - source_dataset_versions
  - source_input_views
  - data_quality_profile
  - blocked_input_used
  - restricted_input_used
  - detector_run_id
  - build_commit

market_context:
  - prior_close
  - open
  - high_to_event
  - low_to_event
  - last_price_at_event
  - volume_to_event
  - rvol_to_event
  - gap_pct
  - float
  - market_cap
  - split_adjustment_context
  - corporate_action_context

event_features:
  - feature_payload
  - threshold_payload
  - condition_pass_payload
  - ambiguity_payload

event_quality:
  - event_quality_state
  - missing_required_inputs
  - degraded_inputs
  - ambiguous_conditions
  - confidence_score
  - review_required

non_strategy_guards:
  - no_entry_rule
  - no_stop_rule
  - no_target_rule
  - no_sizing_rule
```

### Estados De Calidad De Fila

| Estado | Uso |
|---|---|
| `good_event` | Cumple definicion con inputs permitidos y sin ambiguedad critica. |
| `review_event` | Cumple parcialmente, pero requiere revision por ambiguedad o input scoped. |
| `degraded_event` | Detectable, pero con perdida de calidad documentada. |
| `blocked_event` | No debe consumirse downstream porque depende de input bloqueado o inconsistente. |
| `invalid_event` | Falso positivo, condicion imposible o fallo de detector/input. |

### Regla Sobre Payloads

No meteria todas las features como columnas fijas desde el dia uno. Usaria:

```text
core columns + typed payloads
```

Porque `PM_Squeeze_Event`, `Halt_Event` y `VWAP_Reclaim_Event` no tendran exactamente las mismas condiciones.

El payload debe ser estructurado, no texto libre:

```yaml
feature_payload:
  pm_volume: 5000000
  first_push_pct: 25.0
  pullback_pct: 7.0

condition_pass_payload:
  gap_gt_threshold: true
  float_lt_threshold: true
  pm_volume_gt_threshold: true
```

### Regla Fuerte

`event_table` no contiene decision, accion, entrada, stop, target ni sizing.

Si aparece una columna como:

- `entry_price`;
- `stop_price`;
- `target_price`;
- `position_size`;
- `trade_direction`;

entonces ya no es `event_table`; pertenece a Strategy Research, Execution Models o Decision Models.

## 11. Detector Candidate Contract v0.1

Un `detector_candidate` no es codigo productivo. Es una especificacion suficientemente clara para que despues alguien pueda implementar un detector sin reinterpretar la idea.

### Condicion Para Pasar A `detector_candidate`

Un evento solo puede pasar de `draft_definition` a `detector_candidate` si tiene:

1. Condiciones observables separadas de accion operativa.
2. Inputs permitidos o `restricted` claramente marcados.
3. Ningun input bloqueado como requisito obligatorio.
4. Granularidad temporal definida.
5. Reglas de inicio y fin del evento.
6. Reglas de ambiguedad.
7. Quality flags esperadas.
8. Mapping preliminar a `event_table`.

### Contrato

```yaml
detector_candidate:
  event_id:
  event_name:
  event_definition_version:
  detector_candidate_version:
  status: detector_candidate

  detection_unit:
    grain: ticker_day | ticker_session | intraday_window | event_interval
    session_scope: premarket | regular | afterhours | full_extended | daily
    timezone:
    calendar_policy:

  required_inputs:
    - input_name:
      family:
      dataset_or_view:
      status: allowed | restricted
      governing_contract:
      required_fields:
      allowed_missingness:
      fallback_allowed: true | false

  prohibited_inputs:
    - input_name:
      reason:

  start_condition:
    description:
    logic_type: threshold | sequence | state_transition | external_event | composite
    required_fields:
    parameters:
    ambiguity_rule:

  end_condition:
    description:
    logic_type: threshold | time_window | state_transition | external_event | session_close | TBD
    required_fields:
    parameters:
    ambiguity_rule:

  observable_conditions:
    hard_conditions:
      - condition_id:
        description:
        field:
        operator:
        threshold:
        threshold_source: fixed | config | percentile | learned_later
    soft_conditions:
      - condition_id:
        description:
        field:
        operator:
        threshold:
        consequence_if_missing:

  parameter_policy:
    fixed_parameters:
    research_parameters:
    prohibited_overfit_parameters:
    version_bump_required_when:

  expected_outputs:
    event_table_fields:
    feature_payload_fields:
    condition_pass_payload_fields:
    quality_flags:

  ambiguity_handling:
    duplicate_candidates:
    overlapping_events:
    missing_intraday_data:
    halted_session:
    split_or_corporate_action:
    symbol_identity_conflict:

  review_requirements:
    minimum_case_review:
    good_examples_required:
    bad_examples_required:
    edge_cases_required:

  non_strategy_guard:
    forbidden_fields:
      - entry_price
      - stop_price
      - target_price
      - position_size
      - trade_direction
    validation_rule:
```

### Reglas Importantes

Un detector detecta que algo ocurrio. No decide si operar.

Un detector puede tener thresholds de observacion. No puede tener thresholds de rentabilidad.

Un detector puede marcar start/end de evento. No puede marcar entry/exit de trade.

### Estados De Detector

| Estado | Significado |
|---|---|
| `not_ready` | Falta definicion o inputs. |
| `candidate` | Se puede especificar sin codigo. |
| `specified` | La logica esta lista para implementacion. |
| `implemented_experimental` | Hay codigo exploratorio, no promovido. |
| `validated_research` | Codigo y outputs reproducibles para research. |
| `promoted_detector` | Detector gobernado y versionado. |

## 12. Event Versioning Rules + Quality Flags

### Versionado

Usaria SemVer para eventos y detectores:

```text
MAJOR.MINOR.PATCH
```

### Bump Rules

| Cambio | Bump |
|---|---|
| Correccion textual sin cambiar semantica | `PATCH` |
| Aclarar exclusiones sin cambiar deteccion | `PATCH` |
| Anadir optional condition no obligatoria | `MINOR` |
| Anadir quality flag compatible | `MINOR` |
| Cambiar threshold obligatorio | `MAJOR` |
| Cambiar start/end condition | `MAJOR` |
| Cambiar input obligatorio | `MAJOR` |
| Cambiar familia semantica del evento | `MAJOR` |
| Cambiar significado de una fila en `event_table` | `MAJOR` |

### Reglas

`event_definition_version` versiona el concepto.

`detector_version` versiona la logica que materializa el concepto.

`event_table_version` versiona el schema/output.

No deben mezclarse.

Ejemplo:

```text
PM_Squeeze_Event v0.1.0
pm_squeeze_detector v0.1.0
event_table_contract v0.1.0
```

Un cambio en detector no siempre cambia el evento conceptual. Un cambio conceptual fuerte si obliga a revisar detector y `event_table` mapping.

### Quality Flags

```yaml
identity_flags:
  - identity_good
  - identity_review
  - identity_unresolved
  - transient_symbol
  - corporate_action_near_event

input_flags:
  - input_good
  - input_restricted
  - input_scoped
  - input_missing_optional
  - input_missing_required
  - blocked_input_dependency

time_flags:
  - calendar_good
  - premarket_event
  - regular_session_event
  - extended_hours_event
  - timestamp_ambiguous
  - halt_overlap
  - split_window_overlap

condition_flags:
  - all_hard_conditions_passed
  - soft_condition_missing
  - threshold_boundary_case
  - overlapping_event_candidate
  - duplicate_event_candidate

quality_state_flags:
  - good_event
  - review_event
  - degraded_event
  - blocked_event
  - invalid_event

non_strategy_flags:
  - no_entry_rule
  - no_stop_rule
  - no_target_rule
  - no_sizing_rule
```

### Severidad

| Flag | Consecuencia |
|---|---|
| `good_event` | Puede pasar a Outcome Research. |
| `review_event` | Puede entrar en analisis, pero separado. |
| `degraded_event` | Solo analisis forense/research flagged. |
| `blocked_event` | No downstream consumption. |
| `invalid_event` | Se excluye salvo para diagnostico del detector. |

### Reglas Fuertes

Si `blocked_input_dependency = true`, `event_quality_state` no puede ser `good_event`.

Si `input_missing_required = true`, `event_quality_state` debe ser `blocked_event` o `invalid_event`.

Si una fila no puede demostrar `no_entry_rule`/`no_stop_rule`/`no_target_rule`/`no_sizing_rule`, no pertenece a `event_table`.

## 13. Estructura De Archivos Propuesta

Antes de documentar, propondria una estructura simple de archivos. No ejecutaria nada hasta que la aceptes.

### Opcion Recomendada

Crear pocos documentos, pero con contratos claros:

```text
00_CTO/13_TRADING_SYSTEMS/
  00_EVENT_LIBRARY/
    EVENT_RESEARCH_SCOPE_v0_1.md
    EVENT_INPUT_AUTHORITY_MATRIX_v0_1.md
    EVENT_DEFINITION_CONTRACT_v0_1.md
    EVENT_LIFECYCLE_v0_1.md
    EVENT_FAMILY_TAXONOMY_v0_1.md
    INITIAL_EVENT_BACKLOG_v0_1.md

  01_EVENT_ENGINE_MODEL/
    EVENT_TABLE_CONCEPTUAL_CONTRACT_v0_1.md
    DETECTOR_CANDIDATE_CONTRACT_v0_1.md
    EVENT_VERSIONING_AND_QUALITY_FLAGS_v0_1.md
```

Actualizar solo indices:

```text
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/README.md
00_CTO/13_TRADING_SYSTEMS/01_EVENT_ENGINE_MODEL/README.md
00_CTO/13_TRADING_SYSTEMS/README.md
00_CTO/CHANGELOG.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

### Por Que Asi

- `00_EVENT_LIBRARY` gobierna que es un evento, familias, backlog e inputs.
- `01_EVENT_ENGINE_MODEL` gobierna como esos eventos pasaran a detector y `event_table`.
- No tocamos `01_foundations`.
- No creamos eventos institucionales.
- No creamos codigo.
- No reconstruimos Graphify; solo lo dejamos en cola como cambio HIGH, porque son contratos nuevos de trading systems.

### Alternativa Mas Compacta

Un solo documento grande:

```text
00_CTO/13_TRADING_SYSTEMS/EVENT_RESEARCH_AND_ENGINE_CONTRACTS_v0_1.md
```

No la recomiendo, porque mezcla Event Library y Event Engine Model y luego sera mas dificil mantenerlo.

Mi recomendacion: usar la opcion de 9 documentos especificos + indices minimos.

## 14. Principio General

Dejaria explicito este principio en todos los documentos donde aplique:

```text
Event Research v0.1 crea lenguaje, contratos y prerequisitos.
Event Engine v0.1 prepara deteccion futura.
Ninguno crea estrategias, trades, outcomes finales ni edge claims.
```

## 15. Estado Final De La Conversacion

Resumen de consenso alcanzado hasta ahora, sin tocar archivos:

### Documentos Event Library

1. `EVENT_RESEARCH_SCOPE_v0_1.md`
2. `EVENT_INPUT_AUTHORITY_MATRIX_v0_1.md`
3. `EVENT_DEFINITION_CONTRACT_v0_1.md`
4. `EVENT_LIFECYCLE_v0_1.md`
5. `EVENT_FAMILY_TAXONOMY_v0_1.md`

### Reglas Recordadas

- No crea eventos `institutional`.
- No crea detectores productivos.
- No crea `event_table` materializada.
- No crea estrategias ni backtests.
- No mide edge.
- No toca `01_foundations`.
- Data Foundation gobierna inputs; `00_CTO` solo consume esa autoridad.
- Graphify no se reconstruye ahora; si escribimos los documentos, se anota en refresh queue como cambio HIGH.

### Punto Pendiente Antes De Escribir

Decidir si aceptamos estos borradores como base inicial o si quieres revisar/cambiar alguno antes de preparar el parche.

Mi recomendacion: aceptarlos como v0.1 draft/promoted contract surface y escribirlos, porque son suficientemente estrictos y dejan claro que todavia no estamos detectando ni validando eventos.

## 16. Pausa Operativa

Quedo a la espera de tu OK explicito.

Cuando digas "adelante" o equivalente, el siguiente paso seria preparar el parche con esos 9 documentos y los indices minimos. Hasta entonces no escribo nada en el repo.

Estado actual:

- Borradores conceptuales completos en chat.
- Ningun archivo modificado por esos borradores contractuales.
- Siguiente accion posible: revisar un borrador concreto o autorizar la materializacion en el repo.
