# Intraday Regime Features Good/Scoped Cases v0.1

This file documents positive evidence for:

```text
intraday_regime_features_v0_1
```

The evidence is scoped to the semantic pilot. It does not promote a production
feature store.

## Evidence Assets

| Asset | Reading |
| --- | --- |
| `../evidence_assets/intraday_regime_features_semantic_case_manifest_v0_1.csv` | Pilot case table and image links. |
| `../evidence_assets/intraday_regime_features_provenance_summary_v0_1.csv` | Confirms expected raw vs split-normalized price-view provenance. |
| `../evidence_assets/intraday_regime_features_key_quality_summary_v0_1.csv` | Confirms no duplicate `ticker + date` rows in the pilot output. |
| `../evidence_assets/intraday_regime_features_image_manifest_v0_1.csv` | Visual evidence inventory. |

## Strong Positive Split Cases

| Case | Role | Max absolute gap difference |
| --- | --- | ---: |
| `BNGO 2025-01` | reverse split | 5,183.28% |
| `CEI 2022-12` | reverse split | 4,900.00% |
| `BXRX 2022-12` | reverse split | 3,897.11% |
| `COSM 2022-12` | reverse split | 2,450.70% |
| `EFSH 2025-01` | forward split | 111.76% |
| `LIVE 2014-02` | forward split | 66.67% |

Reading:

- raw cross-session features would create false split-driven shocks;
- split-normalized cross-session features expose and neutralize those shocks;
- this proves a real downstream consumer relationship to
  `ohlcv_1m_split_normalized`.

## Controls

| Case | Role | Max absolute gap difference |
| --- | --- | ---: |
| `BXRX 2022-11` | control | 0.00% |
| `BNGO 2025-02` | control | 0.00% |

Reading:

- the pilot does not invent differences where no cross-session discontinuity is
  expected inside the useful feature window.

## Provenance Check

All 8 feature files match:

| Field | Value |
| --- | --- |
| `feature_contract` | `intraday_regime_features_v0_1` |
| `feature_grain` | `ticker_day` |
| `cross_session_price_view` | `1m_split_normalized_v0_1` |
| `intraday_price_view` | `1m_raw` |
