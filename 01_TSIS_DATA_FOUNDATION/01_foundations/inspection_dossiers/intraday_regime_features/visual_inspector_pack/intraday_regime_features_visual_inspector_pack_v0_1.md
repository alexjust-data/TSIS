# Intraday Regime Features Visual Inspector Pack v0.1

Family:

```text
intraday_regime_features_v0_1
```

Physical root:

```text
E:/TSIS/data/intraday_regime_features
```

Visual inspection status:

```text
visual_complete_scoped
```

Foundations completion status:

```text
human_inspector_ready_scoped
```

## 1. Scope

This visual pack formalizes the semantic pilot evidence for
`intraday_regime_features_v0_1`.

It answers five inspector questions:

1. What is the exact pilot population?
2. Do split-sensitive cases diverge under raw-vs-split-normalized comparison?
3. Do control cases remain neutral?
4. Are nulls interpretable as lookback boundaries?
5. Which consumers are explicitly blocked by the pilot boundary?

The pack does not claim full-universe production feature readiness.

## 2. Aggregate Panels

### 2.1 Pilot Population Map

![Pilot population map](images/intraday_regime_features_pilot_population_map_v0_1.png)

What it shows:

- 8 materialized pilot tickers;
- 243 ticker-day rows;
- 8 feature parquet files;
- 41 columns;
- 0 read errors;
- 0 duplicate `ticker + date` rows;
- date span from `2006-03-01` to `2025-02-28`.

Inspector reading:

- This proves the exact pilot footprint.
- It does not prove full-universe feature-store coverage.

### 2.2 Semantic Case Summary

![Semantic case summary](images/intraday_regime_features_semantic_case_summary_v0_1.png)

What it shows:

- maximum raw-vs-split-normalized gap-feature divergence by ticker/month;
- strong reverse-split cases above 2,450%;
- forward-split cases ranging from 28.49% to 111.76%;
- two controls at 0.00%.

Inspector reading:

- The consumer reacts where split normalization should matter.
- The controls remain neutral.
- This supports the use of `ohlcv_1m_split_normalized` for cross-session
  feature semantics.

### 2.3 Lookback Null Boundary Panel

![Lookback null boundary panel](images/intraday_regime_features_lookback_null_boundary_panel_v0_1.png)

What it shows:

- top non-zero null rates by feature column;
- highest null rate in `overnight_gap_zscore_20`;
- remaining nulls concentrated in multi-session and previous-session features.

Inspector reading:

- The observed nulls are boundary evidence for lookback-dependent features.
- They should not be interpreted as silent corruption inside this pilot scope.

### 2.4 Provenance Matrix

![Provenance matrix](images/intraday_regime_features_provenance_matrix_v0_1.png)

What it shows:

- `feature_contract` matches `intraday_regime_features_v0_1` in all 8 files;
- `feature_grain` matches `ticker_day` in all 8 files;
- `cross_session_price_view` matches `1m_split_normalized_v0_1` in all 8 files;
- `intraday_price_view` matches `1m_raw` in all 8 files.

Inspector reading:

- The pilot files expose the intended semantic contract directly in data.
- Downstream consumers can reconstruct the intended price-view semantics.

### 2.5 Production Boundary Panel

![Production boundary panel](images/intraday_regime_features_production_boundary_panel_v0_1.png)

What it shows:

- validation, inspection and scoped research use are allowed;
- extended backtest and flagged ML use are restricted;
- core backtest, primary ML, execution simulation, RL and live consumers are
  not enabled.

Inspector reading:

- `human_inspector_ready_scoped` is not equivalent to production-ready.
- The pack is explicit about which downstream claims remain blocked.

## 3. Concrete Semantic Cases

### 3.1 Strong Split Cases

![BNGO 2025-01](images/BNGO_2025_01.png)

`BNGO 2025-01` is a reverse-split case with maximum absolute gap divergence of
`5,183.28%`. It is a strong positive case: raw 1m would create a false
cross-session regime shock, while the split-normalized view neutralizes the
mechanical discontinuity.

![CEI 2022-12](images/CEI_2022_12.png)

`CEI 2022-12` is a reverse-split case with maximum absolute gap divergence of
`4,900.00%`. It confirms that the feature consumer detects split-driven
distortion in cross-session memory features.

![BXRX 2022-12](images/BXRX_2022_12.png)

`BXRX 2022-12` is a reverse-split case with maximum absolute gap divergence of
`3,897.11%`. It shows a material raw-vs-normalized divergence even when
`days_factor_ne_1 = 0`, proving that the relevant question is scale
discontinuity inside the feature window, not only whether a factor differs from
1 on every day.

![COSM 2022-12](images/COSM_2022_12.png)

`COSM 2022-12` is a reverse-split case with maximum absolute gap divergence of
`2,450.70%`. It reinforces that raw 1m can manufacture false regime shocks
around reverse splits.

![EFSH 2025-01](images/EFSH_2025_01.png)

`EFSH 2025-01` is a forward-split case with maximum absolute gap divergence of
`111.76%`. It is a strong positive forward-split case.

![LIVE 2014-02](images/LIVE_2014_02.png)

`LIVE 2014-02` is a forward-split case with maximum absolute gap divergence of
`66.67%` and maximum absolute three-session return divergence of `119.08%`.
It is a positive case above the review threshold.

### 3.2 Boundary Split Cases

![PD 2006-03](images/PD_2006_03.png)

`PD 2006-03` is a forward-split boundary case with maximum absolute gap
divergence of `49.81%`. It is coherent but below the 50% review threshold.

![SAVA 2023-12](images/SAVA_2023_12.png)

`SAVA 2023-12` is a forward-split boundary case with maximum absolute gap
divergence of `28.49%`. The lower divergence is not a failure; it describes a
window where little re-scalable past remains inside the month.

### 3.3 Controls

![BXRX 2022-11](images/BXRX_2022_11.png)

`BXRX 2022-11` is a control month with maximum absolute gap divergence of
`0.00%`. It confirms that the consumer does not invent a split effect where the
feature ratios should remain invariant.

![BNGO 2025-02](images/BNGO_2025_02.png)

`BNGO 2025-02` is a control month with maximum absolute gap divergence of
`0.00%`. It confirms neutral behavior after the split-sensitive window has
passed.

## 4. Manifested Visual Assets

The complete machine-readable visual index is:

```text
intraday_regime_features_visual_case_manifest_v0_1.csv
```

The generated asset audit is:

```text
intraday_regime_features_visual_asset_audit_v0_1.csv
```

The pack contains:

- 5 generated aggregate panels;
- 10 copied semantic pilot case images;
- 15 manifested image assets total.

## 5. Verdict

`intraday_regime_features_v0_1` now has a formal visual inspector pack matching
the foundation completion standard for a scoped pilot.

Final visual verdict:

```text
visual_complete_scoped_not_production_feature_store
```
