# State Observable Eligibility Contract v0.1

## Estado

Tipo: observable eligibility contract.
Modulo: `01_TSIS_DATA_FOUNDATION`.
Ambito: `CAPA 1 - DATA FOUNDATION`.

Status:

```text
contract_defined
state_builder_inputs_governed = true
market_state_table_materialized = false
event_state_table_materialized = false
ml_ready_dataset_enabled = false
rl_training_dataset_enabled = false
alphaevolve_evaluator_enabled = false
```

Este contrato cierra el puente entre schemas/componentes fuente y los observables que un futuro state builder podra usar para construir `market_state_table_v0_1` y `event_state_table_v0_1`.

No materializa datos. No crea un builder. No crea features ganadoras. No habilita ML/RL/AlphaEvolve directo. No convierte outcomes, scanners, thresholds, acciones, fills ni PnL en estado.

Formula gate status:

```text
state_derived_observables_formula_contract_v0_1 = complete_for_contract_defined_scope
```

## Fuentes Normativas

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/master_daily_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/master_intraday_bar_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/microstructure_features_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/microstructure_features_table_multi_window_materialization_plan_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/fundamentals_asof_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/news_context_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/short_context_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/regime_context_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/halts_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/short_sale_constraints_table_target_contract_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/instrument_master_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/market_calendar_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/expected_data_calendar_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/corporate_actions_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/dataset_certification_matrix_schema_contract.md
```

## Principio Central

```text
state observable = columna literal o derivada que puede conocerse legalmente en t,
respeta cutoff, tiene lineage/calidad y no codifica outcome, reward, label,
accion, fill, PnL, decision ni threshold descubierto.
```

El state builder solo puede consumir observables declarados en este contrato y con `status` compatible con el uso solicitado.
## Regla Transversal Sobre `derived`

Una tabla de estado no es una tabla raw-only.

```text
estado base = observables literales + derivadas neutrales + calidad/lineage,
siempre bajo cutoff legal as-of.
```

Pero `derived` no significa "factor elegido", "ventana optima" ni "decision cientifica cerrada".

En este contrato, una derivada puede aparecer por dos motivos distintos:

| Caso | Lectura correcta | Ejemplo |
| --- | --- | --- |
| Derivada ya existente en schema/componente | Puede ser elegible porque ya existe como observable reproducible, no porque sea la mejor ventana | `volume_20d_avg`, `rvol_20d`, `dollar_volume`, `quotes_spread_bps_p90` |
| Derivada posible todavia no cerrada | No entra como schema oficial hasta tener formula, ventana, cutoff y quality gate | `intraday__move_shape`, `intraday__volume_shape`, `microstructure__price_impact_proxy` |

Regla obligatoria:

```text
si se cambia la formula, la ventana, el baseline, el horizonte, el smoothing,
el ranking o la transformacion de una derivada, ya no es el mismo observable.
Debe declararse en state_derived_observables_formula_contract_v0_1.md o en una
version posterior equivalente.
```

Esto aplica a todas las areas:

```text
Daily
Intradia 1m
Microestructura
Fundamentals
News
Short Context
Regime
Halts
Short Constraints / Float / Live Alerts
Soporte Legal / Calidad / Lineage
```

Ejemplo:

```text
rvol_20d existe hoy porque lo declara master_daily_table_schema_contract.
Eso no afirma que 20 sesiones sea la ventana optima.

rvol_14d, rvol_60d, rvol_intraday_to_time o cualquier alternativa pueden ser
hipotesis validas, pero deben entrar como derivadas candidatas con formula y
cutoff contratados antes de alimentar el state builder oficial.
```

## Regla Para AlphaEvolve, ML Y Estadistica De Estrategias

AlphaEvolve, ML, RL o un analisis estadistico de estrategia pueden proponer o comparar:

```text
lookbacks alternativos
ventanas alternativas
baselines alternativos
normalizaciones alternativas
umbrales alternativos
representaciones semanticas derivadas
detectores de eventos
politicas de decision
```

Pero no pueden modificar silenciosamente la verdad observable base.

El flujo correcto es:

```text
observables legales existentes
-> hipotesis o candidato de derivada/representacion
-> formula contract versionado
-> builder/replay reproducible
-> evaluator bloqueado
-> decision de promocion o rechazo
```

Por tanto:

```text
AlphaEvolve no decide que 20d, 14d o 60d sea verdad base.
AlphaEvolve puede descubrir que una variante funciona mejor.
Si esa variante se quiere usar como estado/feature oficial, se contrata como
nuevo observable derivado versionado, con formula, ventana, cutoff, lineage y
gates.
```

## Taxonomia De Tipo Y Rol Del Observable

La distincion `literal_or_derived` no basta para decidir si algo es nuclear,
ajustable o prohibido.

Regla:

```text
literal_or_derived dice como nace el dato.
observable_role dice para que sirve y como debe gobernarse.
```

Por tanto:

```text
no-derived no equivale automaticamente a nuclear;
derived no equivale automaticamente a experimental.
```

| Tipo / rol | Ejemplo | Lectura correcta | Como se gobierna |
| --- | --- | --- | --- |
| Literal nuclear | `open`, `high`, `low`, `close`, `volume`, `published_utc`, `short_interest` | dato observado directamente o valor fuente conocido as-of | puede entrar si fuente, cutoff, calidad y disponibilidad pasan |
| Derivado mecanico | `dollar_volume`, `gap_pct`, `daily_return_pct` | calculo simple desde inputs observables; no decide estrategia | requiere formula estable y cutoff; puede ser elegible si la formula esta contratada o ya existe en schema |
| Derivado con ventana/baseline | `volume_20d_avg`, `rvol_20d`, `move_speed_5m`, `spread_p90_30s` | depende de ventana, baseline, agregado o smoothing; puede moverse segun hipotesis | si ya existe en schema se puede consumir como observable existente; si se cambia ventana/formula debe crear nuevo candidato/version |
| Contexto as-of literal | `filing_date`, `as_of_date`, `halt_start_et`, `regime_proxy_role` | informacion externa conocida con lag/cutoff propio | requiere disponibilidad real; la fecha del evento no siempre es fecha de conocimiento |
| Contexto as-of derivado | `days_to_cover`, `short_volume_ratio`, regime returns/ranges, conteos news por ventana | transformacion de contexto externo | requiere lag, ventana, formula y cutoff especificos del componente |
| Calidad | `row_level_price_integrity_state`, `microstructure_quality_state`, `valid_for_*` | decide si la fila/familia puede consumirse | viaja con el estado como gate; no es alpha directa |
| Lineage | `source_file`, `build_run_id`, `schema_version`, file hashes | permite reproducir y auditar | obligatorio para trazabilidad; no debe usarse como senal causal |
| Soporte legal/semantico | `instrument_id`, `session_date`, `price_view`, calendar/session fields | hace legal el join, la vista y el timestamp | soporte del builder; no es por si solo factor predictivo |
| Candidato experimental | `rvol_14d_candidate`, `intraday__move_shape`, `price_impact_proxy` | hipotesis o representacion no cerrada | requiere contrato de formula, replay/evidencia y decision de promocion |
| Representacion semantica/latente | `attention`, `crowding`, `book_fragility`, `liquidity_vacuum` | interpretacion/modelo construido desde observables legales | capa posterior; nunca reemplaza el estado base observable |
| Prohibido como feature de estado | `winner`, `reward`, `PnL`, `best_threshold`, `selected_by_scanner` | outcome, accion, decision, leakage o threshold descubierto | no entra en X; solo puede vivir en outcomes, evaluadores, eventos o auditoria |

Lectura practica para agentes:

```text
Antes de usar una columna, no preguntes solo si es literal o derived.
Pregunta tambien su rol.
```

Checklist minimo:

```text
1. existe en schema/componente o esta definido como candidato?
2. es literal, derivado, quality, lineage, support, semantic o prohibido?
3. si es derivado, la formula/ventana/baseline estan contratados?
4. si se propone mover una ventana o formula, se crea nuevo observable/version?
5. el uso previsto permite esa clase de observable?
```

## Modelo De Fila

Campos logicos de cada fila de elegibilidad:

```text
area
source_component
source_schema_path
source_column
target_namespace
target_observable_name
literal_or_derived
observable_role
observable_class
formula
cutoff_rule
quality_gate_required
allowed_for_market_state
allowed_for_event_state
allowed_for_ml
allowed_for_rl
allowed_for_alphaevolve
leakage_risk
status
```

Para mantener el documento legible, las matrices usan columnas compactas:

| Columna compacta | Equivale a |
| --- | --- |
| `source_column` | columna fuente o grupo de columnas reales con la misma regla |
| `target_observable` | namespace + nombre final propuesto |
| `class` | literal/derivada + rol/clase compacta del observable |
| `cutoff / rule` | regla as-of, formula o caveat |
| `quality gate` | gate minimo antes de consumo |
| `allowed usage` | usos autorizados |
| `status` | estado operativo |

Cuando `source_column` contiene varias columnas separadas por coma, cada columna hereda la misma regla salvo que otra fila la restrinja.

## Vocabulario De Status

| Status | Significado |
| --- | --- |
| `eligible_now` | puede entrar como observable de estado con cutoff y quality gate declarados |
| `eligible_with_cutoff_restriction` | puede entrar solo bajo restriccion temporal explicita |
| `candidate_requires_formula` | derivada posible, pero exige formula, ventana y cutoff formal antes de schema oficial |
| `candidate_requires_materialization` | contrato posible, pero falta output materializado o evidencia de builder |
| `blocked_no_source` | objetivo deseado, pero no hay fuente usable |
| `blocked_no_materialized_table` | existe target/contrato, pero no tabla materializada |
| `future_no_namespace` | componente futuro; hoy no tiene namespace confirmado |
| `support_only` | soporte legal/semantico; no feature alpha directa |
| `lineage_only` | trazabilidad/manifests/build ids; no senal causal |
| `quality_only` | calidad/coverage/gates de consumo; no senal alpha |
| `prohibited_as_feature` | no puede entrar como feature de estado; solo puede existir fuera de X |

## Reglas Globales

1. Ningun observable puede usar datos con `component_as_of_utc > decision_timestamp_utc`.
2. Si la fuente usa fechas, se aplica la politica de disponibilidad del componente.
3. Same-session daily close/high/low/volume no puede usarse antes de estar legalmente disponible.
4. Same-session regime close final no puede usarse como contexto intradia antes de disponibilidad.
5. Short interest/short volume no equivale a borrow, locate, availability ni SSR.
6. Microestructura candidate controlada no implica full universe.
7. Outcomes, labels, rewards, actions, fills y PnL no son observables de estado.
8. Scanner thresholds no son features causales de estado; como maximo son lineage o evento externo.
9. Toda derivada requiere lectura explicita: si ya existe en un schema, entra como observable existente; si se cambia formula/ventana/baseline, se convierte en nuevo candidato y requiere contrato de formula.
10. Derivadas como speed, pace, shape, attention, crowding o fragility requieren formula, ventana, cutoff, version y quality gate.
11. Todo observable promovido debe estar namespaced.

# 1. Daily Eligibility

Fuente:

```text
source_component = master_daily_table_v0_1
source_schema_path = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/master_daily_table_schema_contract.md
```

Regla diaria base: daily puede alimentar estado como memoria historica o contexto de sesion. Para decisiones intradia no se permite usar high/low/close/volume final de la misma sesion antes de que la sesion este cerrada y disponible.
Nota sobre derivadas daily:

```text
Las derivadas daily incluidas aqui existen porque aparecen en el schema diario
o porque son derivables de columnas diarias gobernadas. No fijan por si mismas
que una ventana sea optima. Si se cambia 20d por 14d, 60d, 2 meses, mediana,
EWMA u otro baseline, debe declararse como nuevo observable derivado en el
contrato de formulas.
```

| source_column | target_observable | class | cutoff / rule | quality gate | allowed usage | status |
| --- | --- | --- | --- | --- | --- | --- |
| `master_daily_id` | `daily__source_row_id` | literal / lineage | row source id only | schema valid | lineage | `lineage_only` |
| `instrument_id`, `ticker`, `session_date`, `year`, `month` | `identity__/calendar__daily_join_state` | literal / support | must match decision instrument/session | identity/calendar joins valid | support | `support_only` |
| `price_view` | `daily__price_view` | literal / state | selected legal price view | price-view policy valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_now` |
| `quality_gate_family`, `source_dataset`, `source_root` | `daily__source_family_state` | literal / lineage | source metadata only | schema valid | lineage | `lineage_only` |
| `expected_session`, `expected_reason`, `expected_dataset_id`, `expected_source_root` | `quality__daily_expected_data_state` | literal / quality | expected coverage known from expected calendar | expected_data_calendar gate | quality,state,event_state | `quality_only` |
| `data_present`, `missing_expected_data`, `source_daily_present`, `source_adjusted_present` | `quality__daily_presence_state` | literal / quality | observed availability at build/cutoff | family gates valid | quality,state,event_state | `quality_only` |
| `open` | `daily__open` | literal / price | prior closed session, or current session after open policy allows | row price integrity good/review allowed | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `high`, `low`, `close`, `volume`, `vwap`, `transaction_count` | `daily__session_final_ohlcv` | literal / price-volume | same-session only after close and availability; prior sessions allowed | row price integrity and family gates | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `source_raw_vwap`, `source_t_epoch_ms` | `daily__raw_time_price_lineage` | literal / lineage | provenance only | schema valid | lineage | `lineage_only` |
| `prior_close` | `daily__prior_close` | literal / price-context | prior session closed and available | row price integrity good/review allowed | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_now` |
| `gap_pct` | `daily__gap_pct` | derived / price-context | legal after current session open and prior close available | formula from open/prior_close | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `daily_return_pct`, `intraday_return_pct`, `daily_range_pct` | `daily__session_return_range_metrics` | derived / price-context | same-session only after close; prior sessions allowed | formula source OHLC valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `dollar_volume` | `daily__dollar_volume` | derived / liquidity-context | same-session only after close; prior sessions allowed | price and volume valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `volume_20d_avg`, `rvol_20d` | `daily__lookback_volume_state` | derived / historical-liquidity | lookback window closed before decision; current final volume not pre-close | lookback policy valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `future_split_factor`, `future_dividend_sum`, `future_dividend_factor`, `future_adjustment_factor` | `daily__adjustment_support_state` | literal / support | adjustment metadata only; not alpha | corporate action policy valid | support | `support_only` |
| `adjusted_materialized_price_view`, `adjusted_proxy_open`, `adjusted_proxy_high`, `adjusted_proxy_low`, `adjusted_proxy_close` | `daily__adjusted_price_view_support` | literal / support | price-view construction support | corporate action and price-view policy | support,state if builder selects view | `support_only` |
| `source_daily_file`, `source_splits_file`, `source_dividends_file` | `daily__source_manifest` | literal / lineage | provenance only | files/manifests present | lineage | `lineage_only` |
| `corporate_action_count`, `split_action_count`, `dividend_action_count`, `ticker_change_action_count`, `has_split_action`, `has_dividend_action`, `has_ticker_change_action`, `has_any_corporate_action` | `daily__corporate_action_adjustment_state` | literal / support | effective-date policy proves action known/applicable | corporate_actions gate | support,state,event_state | `support_only` |
| `row_level_price_integrity_state`, `selected_price_hard_invalid`, `negative_volume`, `backtest_core_row_candidate` | `quality__daily_row_state` | literal / quality | row quality state at build time | row quality gates | quality,state,event_state | `quality_only` |
| `family_data_quality_verdict`, `family_foundations_completion_status`, `family_visual_inspection_status`, `family_production_use_gate`, `family_event_consumption_gate` | `quality__daily_family_gate_state` | literal / quality | family certification state | dataset certification matrix | quality,state,event_state | `quality_only` |
| `gate_quality_policy_version`, `expectation_policy_version`, `quality_policy_version`, `schema_version`, `build_run_id`, `created_at_utc`, `expected_data_calendar_build_run_id`, `dataset_certification_matrix_build_run_id`, `corporate_actions_build_run_id` | `daily__lineage_policy_bundle` | literal / lineage | provenance only | versions present | lineage | `lineage_only` |
# 2. Intradia 1m Eligibility

```text
source_component = master_intraday_bar_table_v0_1 / master_intraday_bar_table_v0_2_candidate_quote_guarded
source_schema_path = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/master_intraday_bar_table_schema_contract.md
quote_guarded_contract_path = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
```

Regla intradia base: 1m es el eje operativo para estrategias intradia. Puede alimentar estado solo con barras cerradas o con una policy explicita para decision dentro de barra. No se permite convertir thresholds de scanner en verdad del estado.
Nota sobre derivadas intradia:

```text
Las familias rolling/session_so_far/shape/pace no fijan una ventana concreta.
El contrato de elegibilidad solo dice que son familias posibles. El contrato de
formulas debe decidir si la ventana es 1m, 3m, 5m, 15m, desde open, desde
segment open, hasta t, o cualquier otra variante legal.
```

| source_column | target_observable | class | cutoff / rule | quality gate | allowed usage | status |
| --- | --- | --- | --- | --- | --- | --- |
| `master_intraday_bar_id` | `intraday__source_row_id` | literal / lineage | row source id only | schema valid | lineage | `lineage_only` |
| `ticker`, `instrument_id`, `ts_utc`, `session_date`, `year`, `month` | `identity__/calendar__intraday_join_state` | literal / support | must match decision instrument and timestamp | identity/calendar joins valid | support | `support_only` |
| `bar_size` | `intraday__bar_size` | literal / state | declared bar size must match builder resolution | schema valid | state,event_state | `eligible_now` |
| `price_view` | `intraday__price_view` | literal / state | selected legal price view | price-view policy valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_now` |
| `quality_gate_family`, `source_dataset`, `source_root`, `source_file` | `intraday__source_family_state` | literal / lineage | provenance only | schema valid | lineage | `lineage_only` |
| `open`, `high`, `low`, `close`, `volume`, `vwap`, `transaction_count` | `intraday__last_closed_bar_ohlcv` | literal / price-volume | closed 1m bar `<= decision_timestamp_utc`; no incomplete bar unless policy explicit | core/vwap consumption gates | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_now` |
| `source_t_epoch_ms` | `intraday__source_event_time` | literal / support | source timestamp must be `<= decision_timestamp_utc` | timestamp policy valid | support,state | `eligible_with_cutoff_restriction` |
| `source_raw_open`, `source_raw_high`, `source_raw_low`, `source_raw_close`, `source_raw_vwap`, `source_raw_volume`, `source_raw_transaction_count` | `intraday__raw_price_view_lineage` | literal / lineage | raw provenance for constructed view | price-view policy valid | lineage/support | `lineage_only` |
| `future_split_factor`, `o_split_normalized`, `h_split_normalized`, `l_split_normalized`, `c_split_normalized`, `vw_split_normalized`, `materialized_source_price_view` | `intraday__split_normalized_price_view_support` | literal / support | split policy and effective dates must be legal | split normalization gate | support,state if builder selects view | `support_only` |
| `source_1m_file_reported`, `source_splits_file`, `source_split_normalized_file` | `intraday__source_manifest` | literal / lineage | provenance only | files/manifests present | lineage | `lineage_only` |
| `pilot_role`, `pilot_event_type`, `pilot_event_date` | `intraday__pilot_scope_state` | literal / support | describes scoped pilot; not alpha | scope policy valid | support/quality | `support_only` |
| `session_segment` | `intraday__session_segment` | literal / time-context | segment known from timestamp/session clocks | market calendar valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_now` |
| `raw_quality_manifest_present`, `raw_quality_manifest_rows`, `raw_core_quality_state`, `raw_core_issue_family`, `raw_combined_quality_state`, `raw_allowed_consumption`, `raw_vw_quality_state`, `raw_vw_issue_family`, `raw_final_policy_bucket_lt1b` | `quality__intraday_raw_gate_state` | literal / quality | quality state known at build/cutoff | raw quality manifest promoted/valid | quality,state,event_state | `quality_only` |
| `raw_manifest_negative_or_zero_ohlc_rows`, `raw_manifest_negative_volume_rows`, `raw_manifest_high_low_inversion_rows`, `raw_manifest_duplicate_ts_utc_rows`, `raw_manifest_vw_outside_range_rows` | `quality__intraday_manifest_issue_counts` | literal / quality | issue counts from manifest; not alpha by themselves | raw quality manifest valid | quality,state,event_state | `quality_only` |
| `corporate_action_count`, `split_action_count`, `dividend_action_count`, `ticker_change_action_count`, `has_split_action`, `has_dividend_action`, `has_ticker_change_action`, `has_any_corporate_action` | `intraday__corporate_action_adjustment_state` | literal / support | effective-date policy proves action known/applicable | corporate_actions gate | support,state,event_state | `support_only` |
| `row_level_price_integrity_state`, `selected_price_hard_invalid`, `negative_volume`, `core_ohlcv_consumption_allowed`, `vwap_consumption_allowed`, `vwap_consumption_state` | `quality__intraday_bar_state` | literal / quality | row quality state at build time | row/family gates | quality,state,event_state | `quality_only` |
| `event_research_bar_candidate`, `backtest_core_bar_candidate`, `full_universe_claim`, `materialization_scope` | `quality__intraday_consumption_scope` | literal / quality | consumption scope only; no causal alpha | certification gate | quality,state,event_state | `quality_only` |
| quote-guarded flags: `quote_guarded_view`, `quote_guarded_repair_applied`, `repair_state`, `repair_reason`, `source_quote_guarded_repair_manifest`, `source_quote_guarded_run_id` | `intraday__quote_guarded_state` | literal / lineage-quality | overlay/repair lineage known at build/cutoff | quote-guarded manifest PASS/promoted for scope | quality,lineage,state,event_state | `eligible_with_cutoff_restriction` |
| rolling closed bars: `open/high/low/close/volume/vwap/transaction_count over window` | `intraday__session_so_far_price_volume` | derived / state | all bars in window `<= decision_timestamp_utc` | formula declared; missing-bar policy valid | state,event_state,ml_candidate,alphaevolve_candidate | `candidate_requires_formula` |
| rolling closed bars + daily prior close/open/segment open | `intraday__returns_continuous` | derived / state | all inputs known `<= decision_timestamp_utc`; continuous value, no threshold | formula declared | state,event_state,ml_candidate,alphaevolve_candidate | `candidate_requires_formula` |
| rolling closed bars over declared windows | `intraday__move_shape` | derived / state | speed/acceleration/range/pullback/retrace over windows ending `<= t` | formula and window policy declared | state,event_state,ml_candidate,alphaevolve_candidate | `candidate_requires_formula` |
| rolling volume + daily/as-of baseline | `intraday__volume_shape` | derived / state | baseline must be prior/as-of; no future session volume | formula and lookback policy declared | state,event_state,ml_candidate,alphaevolve_candidate | `candidate_requires_formula` |
| calendar/session clocks + `ts_utc` | `intraday__time_context` | derived / support-state | computed from legal calendar/session clocks | market calendar valid | state,event_state,ml_candidate,alphaevolve_candidate | `candidate_requires_formula` |
| expected bars + observed bars/missingness | `intraday__coverage_state` | derived / quality | expected/observed only up to `t` | expected calendar and raw quality valid | quality,state,event_state | `candidate_requires_formula` |

Prohibicion intradia explicita:

```text
first_cross_50_ts_utc no entra como feature base.
selected_intraday_in_play_candidate no entra como feature causal.
threshold de scanner no entra como verdad del estado.
```

Si se estudian cruces, el estado debe exponer materia prima continua: retornos, max/min hasta t, velocidad, rango, volumen, liquidez, tiempo y calidad. El umbral lo prueba el evaluador, ML, RL o AlphaEvolve despues.

# 3. Microestructura Eligibility

```text
source_component = microstructure_features_table
source_schema_path = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/microstructure_features_table_schema_contract.md
```

Regla microestructura base: microestructura no es daily ni 1m. Describe quotes/trades/tape dentro de ventanas gobernadas. Para estrategias de segundos, 1m no basta; pero microestructura candidate controlada no implica full-universe ni execution truth.
Nota sobre derivadas de microestructura:

```text
Metricas como median, p90, ratios, depth mean o price impact proxy son
transformaciones de una ventana de quotes/trades. La ventana, el agregado y la
formula pueden moverse segun la hipotesis, pero cada variante necesita contrato
de formula antes de ser observable oficial.
```

| source_column | target_observable | class | cutoff / rule | quality gate | allowed usage | status |
| --- | --- | --- | --- | --- | --- | --- |
| `microstructure_feature_id`, `event_window_id` | `microstructure__source_row_window_id` | literal / lineage | row/window source id only | schema valid | lineage/support | `lineage_only` |
| `ticker`, `instrument_id`, `instrument_identity_temporal_match`, `session_date`, `year`, `month` | `identity__/calendar__microstructure_join_state` | literal / support | must match decision instrument/window | identity/calendar joins valid | support | `support_only` |
| `window_start_utc`, `window_end_utc`, `window_label`, `source_scope_note` | `microstructure__window_state` | literal / support-state | window end must be `<= decision_timestamp_utc` unless explicitly role-labelled as anchor window | window policy valid | state,event_state | `eligible_with_cutoff_restriction` |
| `quotes_root_used`, `quotes_root_state`, `target_official_quotes_root`, `legacy_incomplete_e_quotes_root`, `trades_root_used`, `trades_root_state` | `microstructure__source_root_state` | literal / lineage-quality | provenance/root state only | source roots certified for scope | lineage/quality | `lineage_only` |
| `source_quotes_file`, `source_trades_file`, `source_quotes_file_sha256`, `source_trades_file_sha256`, `source_quotes_file_present`, `source_trades_file_present` | `microstructure__source_manifest` | literal / lineage | provenance only | source files/hashes present when expected | lineage | `lineage_only` |
| `is_common_stock`, `is_lt1b_operational`, `lt1b_classification_1b`, `instrument_master_build_run_id`, `instrument_master_schema_version` | `microstructure__instrument_scope_state` | literal / support-quality | scope/identity only; no alpha | instrument master valid | support/quality | `support_only` |
| `quotes_rows`, `quotes_window_rows`, `quotes_first_ts_utc`, `quotes_last_ts_utc` | `microstructure__quote_activity` | literal / coverage-state | quote timestamps/rows within declared window and `<= t` | quote family gate | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `quotes_ask_zero_pct`, `quotes_bid_zero_pct`, `quotes_ask_size_zero_pct`, `quotes_bid_size_zero_pct`, `quotes_two_sided_rows` | `microstructure__quote_coverage_quality` | literal / quality-state | window coverage known by cutoff | quote quality gate | quality,state,event_state | `quality_only` |
| `quotes_crossed_rows`, `quotes_locked_rows`, `quotes_crossed_ratio_pct_all_rows`, `quotes_crossed_ratio_pct_two_sided`, `quotes_locked_ratio_pct_two_sided` | `microstructure__locked_crossed_state` | literal / state-quality | quotes within window and `<= t` | quote family gate | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `quotes_spread_bps_median`, `quotes_spread_bps_p90`, `quotes_top_depth_mean` | `microstructure__spread_liquidity_state` | literal/derived-from-window / state | computed only from quotes in legal window ending `<= t` | quote family gate and formula/window declared | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `trades_rows`, `trades_window_rows`, `trades_first_ts_utc`, `trades_last_ts_utc` | `microstructure__trade_activity` | literal / coverage-state | trade timestamps/rows within declared window and `<= t` | trade family gate | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `trades_invalid_price_rows`, `trades_invalid_size_rows`, `trades_odd_lot_ratio_pct`, `trades_duplicate_exact_ratio_pct`, `trades_off_regular_session_ratio_pct` | `microstructure__trade_quality_state` | literal / quality-state | window quality known by cutoff | trade quality gate | quality,state,event_state | `quality_only` |
| `trades_total_volume`, `trades_dollar_volume`, `trades_price_min`, `trades_price_max`, `trades_price_last`, `trades_size_median`, `trades_size_p90` | `microstructure__trade_volume_price_size_state` | literal/derived-from-window / state | computed only from trades in legal window ending `<= t` | trade family gate and formula/window declared | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `quotes_family_data_quality_verdict`, `quotes_family_event_consumption_gate`, `quotes_family_production_use_gate`, `trades_family_data_quality_verdict`, `trades_family_event_consumption_gate`, `trades_family_production_use_gate`, `microstructure_quality_state` | `quality__microstructure_family_gate_state` | literal / quality | quality/certification state known at build/cutoff | dataset certification matrix | quality,state,event_state | `quality_only` |
| `event_research_microstructure_candidate`, `execution_sim_candidate`, `backtest_core_microstructure_candidate`, `full_universe_claim`, `materialization_scope` | `quality__microstructure_consumption_scope` | literal / quality | scope/permission only; no causal alpha | scope policy valid | quality,state,event_state | `quality_only` |
| `dataset_certification_matrix_build_run_id` | `microstructure__lineage_policy_bundle` | literal / lineage | provenance only | version present | lineage | `lineage_only` |
| multi-window additions: missingness reason, empty-in-window flags, staleness/sparse-window state, event role/family, leakage-safe flag, decision-time eligibility | `microstructure__multi_window_governance_state` | derived/support / quality | not official until schema/contract declares columns | multi-window plan and builder contract | quality,state,event_state | `candidate_requires_materialization` |
| quote/trade windows over multiple horizons | `microstructure__price_impact_proxy` | derived / research-state | proxy only from observables `<= t`; never from fills or future prints | formula/window policy required | research,event_state_candidate,alphaevolve_candidate | `candidate_requires_formula` |

No debe usarse como:

```text
outcome
fill garantizado
execution truth
full-universe claim si solo hay ventanas controladas
```
# 4. Contexto As-Of Eligibility

Regla contexto as-of: esta capa no describe la vela ni el book. Describe informacion, restricciones y contexto externo conocidos legalmente en o antes de `t`. Cada familia tiene su propio lag/cutoff. `period_end`, `trade_date` o `halt_date` no significan disponibilidad automatica.
Nota sobre derivadas de contexto as-of:

```text
Ratios, recencias, flags agregados, conteos, freshness, days_to_cover,
short_volume_ratio, regime returns/ranges o news aggregates pueden ser
observables derivados si respetan lag/cutoff. La eleccion de ventana, lag,
normalizacion o agregacion no es libre: debe quedar contratada antes de uso
oficial.
```

## 4.1 Fundamentals

```text
source_component = fundamentals_asof_table_v0_1
source_schema_path = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/fundamentals_asof_table_schema_contract.md
```

| source_column | target_observable | class | cutoff / rule | quality gate | allowed usage | status |
| --- | --- | --- | --- | --- | --- | --- |
| `fundamental_asof_id` | `fundamentals__source_row_id` | literal / lineage | row source id only | schema valid | lineage | `lineage_only` |
| `ticker`, `instrument_id` | `identity__fundamentals_join_state` | literal / support | must match instrument as-of | identity join valid | support | `support_only` |
| `statement_family`, `source_dataset_id`, `source_subblock`, `timeframe`, `fiscal_year`, `fiscal_quarter`, `cik` | `fundamentals__statement_context` | literal / state | statement metadata available by filing/as_of cutoff | fundamentals quality valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `period_end`, `filing_date`, `as_of_date`, `as_of_year` | `fundamentals__availability_cutoff_state` | literal / support-state | `filing_date/as_of_date <= decision date/time`; never use `period_end` as availability | as-of semantics valid | support,state,event_state | `eligible_with_cutoff_restriction` |
| revenue/cash/assets/debt/cash-flow fields declared in schema | `fundamentals__financial_statement_values` | literal / state | values allowed only after filing/as_of availability | fundamentals quality valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `fundamental_quality_state`, `valid_for_*` fields | `quality__fundamentals_gate_state` | literal / quality | certification state known at build/cutoff | family quality gates | quality,state,event_state | `quality_only` |
| `as_of_semantics`, `period_end_is_availability_date`, `requires_event_time_filter`, `prohibited_without_asof_filter`, `contains_future_information_without_event_filter` | `quality__fundamentals_leakage_gate_state` | literal / quality | leakage policy must pass before use | as-of/leakage gates | quality,state,event_state | `quality_only` |
| source lineage fields | `fundamentals__source_manifest` | literal / lineage | provenance only | source/version present | lineage | `lineage_only` |

## 4.2 News

```text
source_component = news_context_table_v0_1
source_schema_path = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/news_context_table_schema_contract.md
```

| source_column | target_observable | class | cutoff / rule | quality gate | allowed usage | status |
| --- | --- | --- | --- | --- | --- | --- |
| `news_context_id`, `article_id` | `news__source_article_id` | literal / lineage | source/article id only | schema valid | lineage | `lineage_only` |
| `ticker`, `source_path_ticker`, `instrument_id`, `ticker_attribution_state` | `identity__news_join_state` | literal / support-quality | must match instrument attribution as-of | attribution quality valid | support/quality/state | `eligible_with_cutoff_restriction` |
| `published_utc`, `as_of_utc` | `news__availability_cutoff_state` | literal / support-state | `published_utc/as_of_utc <= decision_timestamp_utc` | time alignment valid | support,state,event_state | `eligible_with_cutoff_restriction` |
| `publisher_name`, `author` | `news__source_context` | literal / state | known at publish/as_of time | news quality valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `title`, `description`, `keywords`, `insights` | `news__text_context` | literal / state | known at publish/as_of time; no future revision unless versioned | news quality valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `news_quality_state`, `valid_for_*` fields | `quality__news_gate_state` | literal / quality | quality/certification state known at build/cutoff | news quality gates | quality,state,event_state | `quality_only` |
| `requires_event_time_filter`, `causal_proof_by_itself`, `timezone_alignment_required_for_intraday_claims` | `quality__news_leakage_causality_gate_state` | literal / quality | must pass event-time and timezone policy; news is not causal proof by itself | leakage policy valid | quality,state,event_state | `quality_only` |
| source lineage fields | `news__source_manifest` | literal / lineage | provenance only | source/version present | lineage | `lineage_only` |

## 4.3 Short Context

```text
source_component = short_context_table_v0_1
source_schema_path = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/short_context_table_schema_contract.md
```

| source_column | target_observable | class | cutoff / rule | quality gate | allowed usage | status |
| --- | --- | --- | --- | --- | --- | --- |
| `short_context_id` | `short_context__source_row_id` | literal / lineage | row source id only | schema valid | lineage | `lineage_only` |
| `ticker`, `instrument_id` | `identity__short_context_join_state` | literal / support | must match instrument as-of | identity join valid | support | `support_only` |
| `source_family`, `source_system`, `source_scope`, `observation_family` | `short_context__source_scope_state` | literal / support-state | source scope known by cutoff | short quality valid | support,state,event_state | `eligible_with_cutoff_restriction` |
| `observation_date`, `settlement_date`, `trade_date`, `as_of_date` | `short_context__availability_lag_state` | literal / support-state | use only with declared availability lag; date of observation is not same as availability | lag policy valid | support,state,event_state | `eligible_with_cutoff_restriction` |
| `short_interest`, `avg_daily_volume`, `days_to_cover` | `short_context__short_interest_state` | literal / state | available only after source lag/as_of date | short quality valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `total_volume`, `short_volume`, `exempt_volume`, `short_volume_ratio`, venue short-volume columns | `short_context__short_volume_state` | literal/derived / state | available only after source lag/as_of date | short quality valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `borrow_data_present`, `ssr_data_present`, `execution_truth` | `quality__short_context_scope_warning` | literal / quality | warning only: short context is not borrow/locate/SSR truth | short scope policy | quality | `quality_only` |
| `requires_availability_lag_assumption`, `short_quality_state`, `valid_for_*` fields | `quality__short_context_gate_state` | literal / quality | lag and quality gates must pass | short quality gates | quality,state,event_state | `quality_only` |
| source certification/duplicate/lineage fields | `short_context__source_manifest` | literal / lineage | provenance only | source/version present | lineage | `lineage_only` |

## 4.4 Regime

```text
source_component = regime_context_table_v0_1
source_schema_path = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/regime_context_table_schema_contract.md
```

| source_column | target_observable | class | cutoff / rule | quality gate | allowed usage | status |
| --- | --- | --- | --- | --- | --- | --- |
| `regime_context_id` | `regime__source_row_id` | literal / lineage | row source id only | schema valid | lineage | `lineage_only` |
| `regime_symbol`, `regime_proxy_role` | `regime__proxy_identity` | literal / state | proxy mapping known by cutoff | regime quality valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_now` |
| `as_of_utc`, `as_of_date` | `regime__availability_cutoff_state` | literal / support-state | `as_of_utc/as_of_date <= decision_timestamp_utc` | time policy valid | support,state,event_state | `eligible_with_cutoff_restriction` |
| `open`, `high`, `low`, `close`, `previous_close`, returns/range fields | `regime__price_return_state` | literal/derived / state | same-session final values only after availability; intraday values only if bars observed by `t` | regime data quality valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `volume`, `vwap`, `bars_observed` | `regime__volume_coverage_state` | literal/derived / state-quality | only bars observed by `t`; no final volume pre-close | coverage valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| market-calendar fields | `calendar__regime_session_state` | literal / support-state | calendar state known by timestamp | market calendar valid | support,state,event_state | `eligible_now` |
| coverage/quality flags, `regime_quality_state`, `valid_for_*` fields | `quality__regime_gate_state` | literal / quality | quality/certification known at build/cutoff | regime quality gates | quality,state,event_state | `quality_only` |
| source lineage fields | `regime__source_manifest` | literal / lineage | provenance only | source/version present | lineage | `lineage_only` |

## 4.5 Halts

```text
source_component = halts_table_v0_1
source_schema_path = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/halts_table_schema_contract.md
```

| source_column | target_observable | class | cutoff / rule | quality gate | allowed usage | status |
| --- | --- | --- | --- | --- | --- | --- |
| `halt_event_id` | `halt__event_id` | literal / lineage | event id only | schema valid | lineage/support | `lineage_only` |
| `ticker`, `halt_date` | `identity__/calendar__halt_join_state` | literal / support | must match instrument/session | identity/calendar joins valid | support | `support_only` |
| `halt_start_et`, `resume_quote_et`, `resume_trade_et` | `halt__timestamp_state` | literal / event-state | timestamp must be known `<= decision_timestamp`; resume fields only after known | halt quality valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `halt_code`, `halt_type`, `halt_reason`, `is_sec_suspension`, `halt_event_state` | `halt__event_taxonomy_state` | literal / state | classification known at or after event availability | halt quality valid | state,event_state,ml_candidate,alphaevolve_candidate | `eligible_with_cutoff_restriction` |
| `quality_state`, `valid_for_*` fields | `quality__halt_gate_state` | literal / quality | quality/certification known at build/cutoff | halt quality gates | quality,state,event_state | `quality_only` |
| `prohibited_as_alpha`, `requires_decision_time_availability_contract` | `quality__halt_leakage_gate_state` | literal / quality | halt cannot be used as alpha unless decision-time availability is contracted | leakage policy valid | quality,state,event_state | `quality_only` |
| source lineage fields | `halt__source_manifest` | literal / lineage | provenance only | source/version present | lineage | `lineage_only` |

Regla practica de contexto as-of:

```text
contexto as-of = informacion o restriccion conocida legalmente en t
no = outcome, causalidad demostrada, feature sin lag/cutoff, shortability si solo hay short volume/interest
```
# 5. Short Constraints, Float Y Live Alerts

Esta seccion existe para evitar que componentes deseados se presenten como si ya fueran estado oficial. Pueden formar parte del roadmap, pero no se habilitan como observables base si no hay tabla materializada, schema, fuente y cutoff.

## 5.1 Short Sale Constraints

```text
source_component = short_sale_constraints_table
source_contract_path = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/short_sale_constraints_table_target_contract_v0_1.md
```

| source_column | target_observable | class | cutoff / rule | quality gate | allowed usage | status |
| --- | --- | --- | --- | --- | --- | --- |
| `ssr_active`, SSR windows, `as_of_utc` | `short_constraints__ssr_state` | literal / restriction-state | must come from materialized source with as-of timestamp | not materialized today | future state | `blocked_no_materialized_table` |
| `hard_to_borrow_flag`, `borrow_fee_rate`, borrow availability fields | `short_constraints__borrow_state` | literal / restriction-state | must come from broker/vendor source with availability timestamp | no governed source today | future state/execution/RL | `blocked_no_source` |
| `locate_approved`, locate availability fields | `short_constraints__locate_state` | literal / restriction-state | must come from locate/broker source known before decision | no governed source today | future execution/RL | `blocked_no_source` |

## 5.2 Float / Shares Point-In-Time

```text
source_component = float_context_table
source_status = pending/not materialized; no current confirmed feature namespace in market_state/event_state schema
```

| source_column | target_observable | class | cutoff / rule | quality gate | allowed usage | status |
| --- | --- | --- | --- | --- | --- | --- |
| `float_shares`, `shares_outstanding`, free-float fields | `float__point_in_time_share_state` | literal / context-state | must have point-in-time effective/as_of semantics | no official schema/table today | future state | `future_no_namespace` |

## 5.3 Real-Time Corporate Event Alerts

```text
source_component = real_time_corporate_event_alerts_table
source_status = blocked/future live; no promoted feed today
```

| source_column | target_observable | class | cutoff / rule | quality gate | allowed usage | status |
| --- | --- | --- | --- | --- | --- | --- |
| offerings/filings/newswire alert fields, `received_utc`, latency fields | `corporate_alert__live_event_state` | literal / event-context-state | must prove received time and latency before decision | no promoted live feed today | future event_state/alphaevolve/RL | `future_no_namespace` |

# 6. Soporte Legal, Calidad Y Lineage

Estos componentes hacen legal y reproducible el estado. No son alpha por si solos. El state builder debe usarlos para filtrar, unir, validar y explicar cada fila.

| source_component | source_columns / evidence | target_observable | class | rule | status |
| --- | --- | --- | --- | --- | --- |
| `instrument_master` | ticker/instrument ids, temporal identity, security type, LT1B/common-stock flags | `identity__*` | support | define identidad legal del instrumento en `t` | `support_only` |
| `market_calendar` | sessions, open/close, segments, holidays, clocks | `calendar__*` | support-state | define sesion/segmento/minutos y evita usar tiempo imposible | `support_only` |
| `expected_data_calendar` | expected sessions/bars/files | `quality__expected_coverage_state` | quality | define denominador esperado para coverage/missingness | `quality_only` |
| `corporate_actions` | split/dividend/ticker-change effective dates and files | adjustment/support observables | support | permite price views legales; no alpha por si solo | `support_only` |
| `dataset_certification_matrix` | family gates, production/event consumption gates, review/block states | `quality__family_gate_state` | quality | decide si una familia puede consumirse para cada uso | `quality_only` |
| manifests/build runs/policies/schemas | schema version, build id, created_at, source roots, file hashes | `lineage__*` or namespace-local lineage | lineage | reproduce cada fila; no debe entrenarse como alpha salvo auditoria | `lineage_only` |

Regla de soporte:

```text
support/quality/lineage puede viajar junto al estado para hacerlo legal,
pero no debe confundirse con senal predictiva.
```

# 7. Prohibiciones Explicitas

Los siguientes campos/conceptos no son elegibles como estado base aunque existan en tablas downstream o se puedan calcular:

| concepto | razon | status |
| --- | --- | --- |
| `winner`, `loser`, labels de resultado | outcome futuro | `prohibited_as_feature` |
| `reward`, PnL posterior, fill posterior | resultado/ejecucion posterior | `prohibited_as_feature` |
| `mfe`, `mae`, returns futuros `+1/+5/+15/+30` | outcome | `prohibited_as_feature` |
| `selected_by_scanner = true` como feature causal | decision/seleccion, no observable neutral | `prohibited_as_feature` |
| `first_cross_50_ts_utc` como verdad base | threshold humano/estrategico; debe parametrizarse fuera del estado | `prohibited_as_feature` |
| mejor threshold encontrado por AlphaEvolve/ML/RL | resultado de optimizacion | `prohibited_as_feature` |
| accion tomada: enter/exit/hold/scale | action/policy, no estado observable | `prohibited_as_feature` |
| `daily close/high/low/volume` final antes de cierre | leakage temporal | `prohibited_as_feature` |
| halt/resume conocido despues de la decision | leakage temporal | `prohibited_as_feature` |
| live news/corporate alert sin `received_utc` gobernado | disponibilidad no demostrada | `prohibited_as_feature` |
| borrow/locate/SSR inferido desde short volume/interest | confunde contexto con restriccion operativa | `prohibited_as_feature` |
| semantic labels tipo `Attention=0.93`, `Crowding=High`, `Liquidity Vacuum` sin formula/version/cutoff | representacion derivada no contratada | `prohibited_as_feature` |

Regla para representaciones semanticas o latentes:

```text
observables as-of legales
-> representation_builder_candidate versionado
-> semantic_state_representation_candidate
-> evaluator bloqueado
```

La representacion semantica puede existir como capa derivada, pero no reemplaza la tabla base de estado observable.

# 8. Requisitos Del State Builder

El builder que consuma este contrato debe producir filas de estado con trazabilidad suficiente para explicar cada observable.

## 8.1 Requisitos Minimos Por Observable

Cada observable final debe declarar:

```text
source_component
source_schema_path
source_column_or_formula_inputs
target_namespace
target_observable_name
literal_or_derived
observable_role
observable_class
formula_if_derived
window_if_derived
cutoff_rule
quality_gate_required
allowed_for_market_state
allowed_for_event_state
allowed_for_ml
allowed_for_rl
allowed_for_alphaevolve
leakage_risk
status
```


## 8.2 Reglas Para Derivadas Ajustables

Toda derivada ajustable debe tener identidad versionada. No se permite cambiar
una ventana o formula manteniendo el mismo nombre de observable.

Ejemplo:

```text
daily__rvol_20d              # observable existente si el schema lo declara
daily__rvol_14d_candidate    # nuevo candidato si se propone 14d
daily__rvol_60d_candidate    # nuevo candidato si se propone 60d
intraday__move_speed_5m_candidate
intraday__move_speed_15m_candidate
microstructure__spread_p90_30s_candidate
microstructure__spread_p90_120s_candidate
```

Cada candidato debe declarar:

```text
formula
inputs
window
baseline
cutoff
missingness_policy
quality_gate
lineage
allowed_usage
promotion_decision
```

Si la propuesta viene de AlphaEvolve, ML, RL o estadistica de una estrategia,
debe quedar registrada como candidato/evidencia, no como cambio silencioso del
estado base.

## 8.3 Reglas De Uso Por Tabla Final

```text
market_state_table_v0_1
= observables neutrales as-of por instrument/timestamp/cutoff

event_state_table_v0_1
= subset/control de market_state + event__ metadata conocida <= cutoff + state_role + leakage gates
```

`event_state_table_v0_1` no debe contener outcomes inline. Puede contener keys/referencias para unir outcomes despues.

## 8.4 Roles De Estado Permitidos

Estos roles no cambian la verdad observable; cambian el punto de corte y el uso:

| state_role | uso | regla |
| --- | --- | --- |
| `DISCOVERY_STATE` | exploracion de patrones | debe excluir outcomes/labels |
| `EVENT_ANCHOR_STATE` | estado en el ancla del evento | cutoff = evento/ancla conocida |
| `ENTRY_DECISION_STATE` | estado antes de decidir entrada | cutoff = decision timestamp |
| `RISK_STATE` | gestion de riesgo | cutoff = decision/risk timestamp |
| `EXECUTION_STATE` | simulacion/ejecucion | solo con microestructura y constraints gobernados |
| `RL_TRANSITION_STATE` | transiciones para RL | requiere action/outcome separados |
| `POST_EVENT_ANALYSIS_STATE` | analisis posterior | puede mirar estados posteriores, pero no entrenar como pre-decision sin role/cutoff |

## 8.5 Decision Timestamp Policy

El builder debe distinguir al menos estos timestamps cuando aplique:

```text
pre_market_snapshot_t
end_of_bar_t
event_anchor_t
entry_decision_t
exit_decision_t
halt_resume_t
post_event_measurement_t
```

Un observable elegible para un timestamp puede no ser elegible para otro.

# 9. Acceptance Criteria v0.1

Este contrato queda terminado para el scope declarado cuando se cumple:

| criterio | estado |
| --- | --- |
| Daily mapeado desde schema real a observables elegibles/bloqueados | `done` |
| Intradia 1m mapeado desde schema real y ruta quote-guarded | `done` |
| Microestructura mapeada desde schema real y plan multi-window | `done` |
| Fundamentals/news/short/regime/halts mapeados por lag/cutoff | `done` |
| Short constraints/float/live alerts marcados como bloqueados/futuros cuando corresponde | `done` |
| Soporte legal/calidad/lineage separado de alpha/features | `done` |
| Prohibiciones explicitas documentadas | `done` |
| Requisitos minimos del state builder documentados | `done` |

Estado final:

```text
state_observable_eligibility_contract_v0_1 = complete_for_contract_defined_scope
```

Lo que queda fuera de este contrato y debe hacerse en contratos/builders posteriores:

```text
1. materializar master_intraday_bar_table_v0_2_candidate_quote_guarded
2. crear state builder y validators que consuman state_derived_observables_formula_contract_v0_1.md
3. crear builder de market_state/event_state usando este contrato
4. crear outcomes separados
5. crear evaluator bloqueado para AlphaEvolve/RL/ML
```
