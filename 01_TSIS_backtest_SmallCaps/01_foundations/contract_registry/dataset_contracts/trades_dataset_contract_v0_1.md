# `trades` Dataset Contract v0.1

## Purpose

This contract defines what `trades` is inside `01_TSIS_backtest_SmallCaps`, which audit layers are authoritative, and how the dataset must be interpreted by research, execution, backtest and ML pipelines.

The key architectural point is that `trades` is not a generic price series. It is the raw observed tape of executed prints. That makes it indispensable for execution and microstructure, but dangerous if it is naively compared against `daily` or `1m` references without declaring price semantics, session policy and corporate-action normalization.

This contract must be read together with:

- [price_semantics_and_adjustment_policy.md](../../module_contracts/price_semantics_and_adjustment_policy.md)
- [price_views_registry.md](../../module_contracts/price_views_registry.md)
- [corporate_actions_adjustment_methodology.md](../../module_contracts/corporate_actions_adjustment_methodology.md)
- [pipeline_price_view_policy.md](../../module_contracts/pipeline_price_view_policy.md)
- [market_session_scope.md](../../module_contracts/market_session_scope.md)
- [auditoria_and_certification_source_hierarchy.md](../../module_contracts/auditoria_and_certification_source_hierarchy.md)

## Institutional Role

`trades` is the canonical source for the observed trade tape:

- executed print price
- executed print size
- exchange / venue identity
- tape conditions
- timestamped market activity at trade level

It is not the canonical source for:

- daily economic return series
- benchmark valuation
- vendor-adjusted historical price comparison
- direct portfolio-level mark series

Those roles belong to `daily_adjusted` or later institutional price views, not to raw trades.

## Authoritative Historical Sources

The correct source hierarchy for `trades C + D` is:

### A. `auditoria/trades/v2`

- `03_diseno_implementacion_trades_CD.md`
- `04_trades_full_C_D_audit.ipynb`
- `04_trades_full_C_D_notebook.md`
- `05_trades_file_acceptance_audit.ipynb`
- `05_trades_file_acceptance_notebook.md`
- `06_trades_file_acceptance_full_lt1b_closeout.ipynb`

This layer explains root cause, scale problems, microstructure effects and the logic of the file-acceptance methodology sample.

### B. `certification/trades`

- `00_trades_current_state.md`
- `01_trades_label_assessment.md`
- `02_trades_base_certification_decision.md`
- `03_trades_old_vs_new_bucket_bridge.md`
- `04_trades_provisional_cert_policy.md`
- `05` to `12` bucket notes
- `13` to `18` recovery notes
- `19_trades_final_recovery_policy.md`
- `20_trades_closeout.md`

This layer is stronger for final recovery semantics, usage policy and closeout framing.

### C. Foundations

`01_foundations/trades` must promote both layers:

- technical explanation from `auditoria`
- final operational semantics from `certification`

## Audited Unit

The practical audited unit is the raw file / ticker-day trade tape, represented by one row in the materialized audit table and linked back to a concrete raw file when drilldown is needed.

Operationally the project works with two layers:

- raw trade rows inside each `market.parquet`
- file-level audit rows that summarize one raw file against references and internal diagnostics

This distinction is essential. Many counts that look massive in the historical notebook are counts of audited files or file-level materialized rows, not a direct count of individual executions.

## Current Data Sources

The active local storage topology currently points to:

- raw trades under `C:\TSIS_Data\data	rades_ticks_prod_2005_2026`
- active operational materialization under `C:\TSIS_Data_TSIS_backtest_SmallCapsunsacktest	rades_v2_materialized`

Target-state topology is documented in:

- [data_storage_topology_and_target_state.md](../../module_contracts/data_storage_topology_and_target_state.md)

The intended future direction is to unify active data usage on `D:\` / the operational disk, but contracts must remain independent from short-term physical migration.

## Session Semantics

The project-wide target market session is:

- `04:00-20:00 America/New_York`

But `trades` requires stricter interpretation than `daily`:

- off-session prints exist and are informative
- off-session presence is not automatically equivalent to bad data
- file acceptance must distinguish session context from intrinsic tape corruption

This is consistent with microstructure practice: session state changes liquidity, spread formation and comparability of prints against bar aggregates. Treating all off-session activity as uniform market information is methodologically wrong.

## Why `trades` must stay raw for execution work

The research consensus in market microstructure is that execution analysis must begin from observed tape and book states, not from economically adjusted historical series.

This is aligned with:

- Maureen O'Hara, *Market Microstructure Theory* (1995)
- Joel Hasbrouck, *Empirical Market Microstructure* (2007)
- Albert Menkveld, *High Frequency Trading and the New Market Makers* (2013)
- Marcos Lopez de Prado on separating execution reality from label construction in financial ML

The institutional implication is straightforward:

- execution research needs raw prints
- microstructure diagnostics need raw prints
- duplicate detection, odd-lot structure and sale-condition reading need raw prints
- adjusted daily views are the wrong layer for those tasks

## Historical Findings That Drive This Contract

### Layer A: Population Snapshot (`04`)

The full `C + D` snapshot showed a severely stressed universe:

- `PASS = 553,887`
- `SOFT_FAIL = 5,392,744`
- `HARD_FAIL = 3,685,493`

Dominant signals included:

- `trade_price_outside_daily_range`
- `trade_price_outside_1m_range`
- `duplicate_exact_trade_rows_present`
- `off_session_trades_present`

This layer proves the universe is not a clean residual dataset. It is a large, structurally stressed audit population.

### Layer B: File-Acceptance Methodology Sample (`05`)

The stratified sample of `380` files showed that many apparently severe cases are not equivalent to bad tape. Important findings were:

- inherited off-session diagnostics were partly unreliable and required raw recompute
- conflict against references concentrates much more in odd-lots than in round-lot core flow
- many extreme residuals are better explained as `reference_scale_mismatch`
- the median conservative core (`regular + round_lot`) often stops breaking against references

This layer changes the interpretation from trades is globally broken to a large share of the problem is comparability, microstructure regime, or reference mismatch.

### Layer C: Final File-Acceptance Labels (`57f`)

The authoritative current full-closeout labels are those materialized in the local `57f` cache:

- `review = 4,851,211`
- `reference_scale_mismatch = 2,418,062`
- `review_microstructure = 2,130,781`
- `bad_data = 15,869`
- `review_no_1m_reference = 8,091`
- `review_1m_reference_alignment = 4,992`
- `good = 106`

This is one of the most important conclusions in the whole block:

- the sample was methodologically useful
- but it was not sufficient to erase all residual `bad_data`
- the full policy still leaves a small but real hard-negative tail
- therefore `trades` must be governed by final closeout labels, not by sample intuition alone

## Final Certification Semantics

The decisive point from `certification/trades` is that file-level labels are still not the final operational state.

The final certification vocabulary is:

- `good`
- `recoverable_with_flag`
- `review_not_rehabilitated`
- `bad`

This semantic layer matters because it prevents a methodological collapse between:

- technical file labels
- and final pipeline authorization.

### Mapping logic

#### `good`

Enters here:

- `good`

Important caveat:

- semantically clean but extremely small
- must not be over-represented in the institutional story

#### `bad`

Enters here:

- `bad_data`

Meaning:

- residual tape that still looks intrinsically untrustworthy after explanatory buckets are drained away

#### `recoverable_with_flag`

Enters here, operationally or conceptually:

- `review_no_1m_reference`
- rehabilitable subset of generic `review`
- rehabilitable subset of `review_microstructure`
- rehabilitable subset of `review_1m_reference_alignment`
- `reference_scale_mismatch` only once stable scale reconciliation is validated

Meaning:

- not clean enough for unflagged use
- but not equivalent to intrinsically bad tape

#### `review_not_rehabilitated`

Enters here:

- non-rehabilitated residue of generic `review`
- non-rehabilitated part of `review_microstructure`
- non-rehabilitated part of `review_1m_reference_alignment`
- `reference_scale_mismatch` while no validated scale reconciliation exists

Meaning:

- the file is not final-bad by default
- but the project still does not authorize operational promotion

## Rehabilitation Rule

The strict historical rehabilitation rule for generic `review` was:

- `daily_vw_to_trade_vw` near `1x`
- `trade_vwap_vs_daily_vw_diff_pct_raw <= 0.5`
- `outside_daily_regular_pct <= 1`
- `outside_1m_regular_pct <= 15`

Historical result on the earlier materialized state:

- `review` total: `2,825,748`
- `review` strict rehabilitable: `2,427,056`
- weight: `85.89%`
- non-rehabilitated residue: `398,692`

Institutional reading:

- a large share of generic `review` can become `recoverable_with_flag`
- but the rule must be documented and explicit
- and those historical counts must not be confused with the current full `57f` aggregate until re-materialized there

## Canonical Price Views Relevant To `trades`

`trades` interacts with several price views, but exposes one primary native view:

- primary native view: `trades_raw`

Secondary derived views may be used for comparison or reconciliation:

- `split_normalized`
- `adjusted_proxy`
- later, institutional `adjusted`

But those are not replacements for raw tape. They are comparison layers.

## What `trades` is allowed to mean operationally

### Allowed

- execution realism
- trade-level microstructure
- duplicate analysis
- odd-lot vs round-lot structure
- sale-condition-aware diagnostics
- session-aware diagnostics
- reference-comparison diagnostics when price semantics are declared

### Not allowed

- direct substitution for portfolio return series
- direct substitution for benchmark-adjusted daily history
- naive comparison against external adjusted charts
- naive label generation for daily-return ML tasks

## Contractual Interpretation Rule

No `trades` judgement is valid unless the following are declared:

1. reference being compared against (`daily`, `1m`, or none)
2. session basis (`full 04:00-20:00`, regular-only, or other)
3. size basis (`all prints`, `round-lot`, `odd-lot` aware, etc.)
4. price semantics (`raw`, `split_normalized`, `adjusted_proxy`, `adjusted`)
5. whether the problem is tape-intrinsic or reference-relative

This rule exists to avoid the main methodological error exposed by the historical audit: treating all disagreement with `daily` or `1m` as if it proved bad tape.

## Current Institutional Status

Current state of `trades`:

- historical authority exists and is strong
- file-level closeout exists through `57f`
- certification semantics are rich and should drive final usage policy
- no final `01_foundations` inspection pack exists yet

That means `trades` is no longer unknown, but it is not yet fully promoted into the same institutional inspection stack that `daily` and `quotes` already have.

## Immediate Next Documents

This contract is intentionally high-level. It must be read together with the next trades-specific documents:

- `trades_label_taxonomy_and_cut_policy.md`
- `trades_consumption_policy.md`
- `trades_schema_contract.md`
- `trades_validators.md`
- `build_trades_inspection_pack.md`
