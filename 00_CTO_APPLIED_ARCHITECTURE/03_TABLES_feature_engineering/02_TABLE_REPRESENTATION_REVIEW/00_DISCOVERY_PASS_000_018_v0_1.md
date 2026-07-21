# Discovery Pass 000-018 v0.1

Status: `pass_01_discovery_matrix`
Date: `2026-07-20`

Primera pasada transversal. Descubre responsabilidades, candidatos y riesgos; no corrige ni promueve.

## Regla

```text
Primera vuelta = descubrir.
Segunda vuelta = reconciliar.
Tercera vuelta = construir.
```

## Matriz

| ID | Tabla | Maturity | Decision | Objetos candidatos | Market State | Event State |
| --- | --- | --- | --- | --- | --- | --- |
| 000 | instrument_master | `validated_candidate` | `keep_with_restrictions` | Instrument Identity<br>Universe Membership<br>Listing Status | `yes_as_identity_context` | `yes_as_identity_context` |
| 001 | market_calendar | `validated_candidate` | `keep_with_restrictions` | Trading Session Context<br>Temporal Observability Boundary | `yes_as_temporal_context` | `yes_as_window_context` |
| 002 | expected_data_calendar | `validated_candidate` | `keep_with_restrictions` | Dataset Expectedness<br>Observability Coverage | `yes_as_quality_context_only` | `yes_as_quality_context_only` |
| 003 | dataset_certification_matrix | `validated_candidate` | `keep_with_restrictions` | Dataset Consumption Eligibility<br>Representation Quality State | `yes_as_quality_gate_not_signal` | `yes_as_quality_gate_not_signal` |
| 004 | master_daily_table | `validated_candidate` | `keep_with_restrictions` | Daily Price State<br>Overnight Dislocation<br>Daily Trading Activity<br>Daily Volatility Range | `yes_after_temporal_gating` | `yes_after_temporal_gating` |
| 005 | corporate_actions_table | `validated_candidate` | `keep_with_restrictions` | Corporate Action Context<br>Price Adjustment Context<br>Identity Lifecycle Change | `yes_as_instrument_context` | `yes_as_event_context_when_governed` |
| 006 | halts_table | `validated_candidate` | `keep_with_restrictions` | Halt Context<br>Regulatory Venue Interruption | `yes_when_decision_safe` | `yes_as_event_source_context` |
| 007 | event_windows_table | `validated_candidate` | `keep_with_restrictions` | Event Window Context<br>Event Relative Time | `conditional_event_proximity_only` | `yes_primary_window_input` |
| 008 | outcomes_table | `validated_candidate` | `keep_with_restrictions` | Outcome Response<br>Future Return Label<br>MFE MAE Response | `no_observable_input` | `no_input_yes_y_join` |
| 009 | fundamentals_asof_table | `validated_candidate` | `keep_with_restrictions` | Fundamental Context<br>Capital Structure Context | `yes_as_external_context_profile` | `yes_when_as_of_safe` |
| 010 | news_context_table | `validated_candidate` | `keep_with_restrictions` | News Context<br>Catalyst Context<br>News Recency | `yes_as_news_context_profile` | `yes_when_governed` |
| 011 | short_context_table | `validated_candidate` | `keep_with_restrictions` | Short-Side Context<br>Short Activity<br>Crowding Context | `yes_with_lag_policy` | `yes_for_squeeze_context_with_lag` |
| 012 | regime_context_table | `validated_candidate` | `keep_with_restrictions` | Market Regime<br>Broad Market Context | `pending_state_gate` | `pending_event_gate` |
| 013 | ohlcv_1m_quote_guarded | `validated_candidate` | `keep_with_restrictions` | Intraday Bar Observability<br>Price Integrity State | `yes_indirect_after_014` | `yes_indirect_after_014` |
| 014 | master_intraday_bar_table | `candidate_materialized` | `keep_with_restrictions` | Intraday Price Dynamics<br>Intraday Position<br>Intraday Trading Activity<br>Intraday Volatility | `yes_as_intraday_profile_after_mapping` | `yes_for_event_windows_after_gating` |
| 015 | microstructure_features_table | `candidate_materialized` | `keep_with_restrictions` | Liquidity<br>Trading Activity<br>Market Microstructure State<br>Order Flow Pressure | `yes_as_microstructure_extension` | `yes_as_event_window_profile` |
| 016 | market_state_table | `candidate_materialized` | `redesign_required` | Market State<br>State Quality | `target_table_itself_pending_mapping` | `feeds_event_state_after_gating` |
| 017 | event_state_table | `candidate_materialized` | `redesign_required` | Event State<br>Event Relative Context | `not_market_state_source` | `target_table_itself_pending_gates` |
| 018 | intraday_scanner_candidates_table | `specification_only` | `keep_with_restrictions` | Intraday In-Play Candidate<br>Attention Activity Candidate | `optional_candidate_context_only` | `candidate_surface_not_validated_event` |

## Lectura Transversal

```text
000-003 = infraestructura, expectedness, calidad y gobierno.
004-012 = contexto diario, eventos, outcomes y contexto externo/as-of.
013 = capacidad intradia quote-guarded validada como candidato tecnico, pendiente de promocion institucional.
014 y 015 = superficies hermanas: barras intradia y microestructura.
016 = Market State por perfiles, no mega-tabla.
017 = Event State con state_role separado de consumption_legality.
018 = candidate surface/scanner, no evento validado ni estado canonico.
```

## Siguiente Paso

```text
Consolidar Objetos candidatos repetidos entre tablas.
Evaluar cada Objeto con 01_INFORMATION_OBJECT_ADMISSION_PROCESS.md.
No modificar builders/schemas hasta cerrar mapping Objeto -> Modelo -> Capacidades -> Variables -> Tablas.
```
