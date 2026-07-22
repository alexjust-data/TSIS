# Trades Quality Report v0.1

## 1. Scope And Role

Family:

```text
trades_core_v0_1
```

Physical root:

```text
E:/TSIS/data/trades_ticks_prod_2005_2026
```

Role:

- RAW/STAGED observed trade tape;
- canonical source for executed prints in Module 01;
- execution realism and microstructure evidence layer;
- not a daily economic return series, adjusted benchmark, clean mark series, or direct portfolio valuation source.

## 2. Final Status

```text
complete_scoped
```

`trades_core_v0_1` is institutionally understood and governed, but it is not globally clean. The report imports the current `57f` closeout, final certification semantics and global universe readout into the normalized `data_quality_report/` surface.

## 3. Artifact Map

| Artifact | Status | Path |
| --- | --- | --- |
| Dataset contract | present | `01_foundations/contract_registry/dataset_contracts/trades_dataset_contract_v0_1.md` |
| Label taxonomy and cut policy | present | `01_foundations/contract_registry/dataset_contracts/trades_label_taxonomy_and_cut_policy.md` |
| Registry entry | present | `01_foundations/dataset_registry/trades/trades_registry_entry.yaml` |
| Consumption policy | present | `01_foundations/data_consumption_policies/trades_consumption_policy.md` |
| Schema contract | present | `01_foundations/canonical_schemas/trades/trades_schema_contract.md` |
| Validators | present | `01_foundations/validators/trades/trades_validators.md` |
| Main inspection readout | present | `01_foundations/inspection_dossiers/trades/trades_inspection_readout_v0_1.md` |
| Global universe readout | present | `01_foundations/inspection_dossiers/trades/trades_global_universe_readout_v0_1.md` |
| Population evidence | present | `01_foundations/inspection_dossiers/trades/population_evidence_packs/trades_population_readout_v0_1.md` |
| File acceptance evidence | present | `01_foundations/inspection_dossiers/trades/file_acceptance_evidence_packs/trades_file_acceptance_readout_v0_1.md` |
| Family casepacks | present | `01_foundations/inspection_dossiers/trades/family_case_evidence_packs/family_casepacks_index_v0_1.md` |
| Review/bad/good casepacks | present | `01_foundations/inspection_dossiers/trades/flagged_case_evidence_packs/`, `bad_case_evidence_packs/`, `good_justification/` |

## 4. File Structure And Technical Profile

Primary audited unit:

```text
raw file / ticker-day trade tape
```

Expected logical content:

- `ticker`;
- trade timestamp;
- executed trade price;
- executed trade size;
- exchange or venue where present;
- sale conditions or flags where present.

The project also materializes file-level audit rows. Those rows summarize one raw trade file against daily and 1m references, but they are not the raw executions themselves.

Every valid trade judgement must declare:

- reference basis: `daily`, `1m`, both or none;
- session basis;
- size basis: all prints, round-lot core, odd-lot aware, or other;
- price semantics: raw, split-normalized, adjusted proxy or adjusted;
- whether the problem is tape-intrinsic or reference-relative.

## 5. Population And Coverage

Current final `57f/full_clean_fast_same_schema` universe:

| Acceptance label | Count | Share |
| --- | ---: | ---: |
| `review` | 4,851,211 | 51.45% |
| `reference_scale_mismatch` | 2,418,062 | 25.65% |
| `review_microstructure` | 2,130,781 | 22.60% |
| `bad_data` | 15,869 | 0.168% |
| `review_no_1m_reference` | 8,091 | scoped small tail |
| `review_1m_reference_alignment` | 4,992 | scoped small tail |
| `good` | 106 | 0.001% |

The correct reading is not that almost all trades are bad. The correct reading is that pristine `good` is extremely narrow, while most potentially useful mass lives in intermediate, flagged, reference-relative or microstructure-aware states.

## 6. Cleanliness And Interpretability

The raw tape is heavily stressed, but not monolithically corrupt.

Key interpretations:

- `bad_data` is real but small.
- `reference_scale_mismatch` is a comparability and scale family, not automatic tape corruption.
- `review_microstructure` is dominated by tape texture, especially odd-lots.
- `good` is a pristine benchmark, not a proxy for all usable mass.
- `review` is the main recoverable front.

Current strict rehabilitation for generic `review` over `57f`:

| Metric | Value |
| --- | ---: |
| `review_total` | 4,851,211 |
| `review_recoverable_strict` | 3,327,955 |
| `review_recoverable_strict_pct` | 68.6005% |
| `review_not_rehabilitated_strict` | 1,523,256 |

Extended sensitivity:

| Metric | Value |
| --- | ---: |
| `review_recoverable_extended` | 3,505,290 |
| `review_recoverable_extended_pct` | 72.2560% |
| `review_not_rehabilitated_extended` | 1,345,921 |

`review_microstructure` provisional recovery:

| Metric | Value |
| --- | ---: |
| total | 2,130,781 |
| strict provisional recoverable | 1,516,547 |
| strict provisional recoverable pct | 71.1733% |
| extended provisional recoverable | 1,636,379 |
| extended provisional recoverable pct | 76.7971% |

`review_1m_reference_alignment` provisional recovery:

| Metric | Value |
| --- | ---: |
| total | 4,992 |
| strict provisional recoverable | 2,591 |
| strict provisional recoverable pct | 51.9030% |
| extended provisional recoverable | 3,715 |
| extended provisional recoverable pct | 74.4191% |

## 7. Semantic Quality

Final operational vocabulary:

| Final state | Meaning |
| --- | --- |
| `good` | pristine tape, extremely small benchmark population |
| `recoverable_with_flag` | usable only with explicit flag and policy |
| `review_not_rehabilitated` | not final-bad by default, but not authorized for clean use |
| `bad` | tape not economically or structurally defensible |

Important subfamilies:

| Family | Interpretation |
| --- | --- |
| `reference_scale_mismatch` | reference-relative scale/comparability conflict |
| `review_microstructure` | tape texture, odd-lots, sparsity or fine intraday conflict |
| `review_no_1m_reference` | evidence-resolution limit, not automatic bad data |
| `review_1m_reference_alignment` | 1m reference changes the case truth |
| `bad_data` | hard tape failure or non-defensible file |

`bad_data` itself is not one visual family:

| Subfamily | Share |
| --- | ---: |
| `colapso_escala_rango` | 53.86% |
| `conflicto_ralo_o_sparse` | 33.68% |
| `mixto_estructural_rango` | 9.59% |
| `integridad_estructural` | 2.87% |

`review_microstructure` is dominated by `odd_lot_dominante`:

| Texture | Count | Share |
| --- | ---: | ---: |
| `odd_lot_dominante` | 2,116,279 | 99.32% |
| `sparse_o_ralo` | 11,611 | 0.54% |
| `duplicacion_textura` | 1,903 | 0.089% |
| `conflicto_fino_1m` | 988 | 0.046% |

## 8. Case Evidence

The human auditor should read evidence in this order:

1. `trades_global_universe_readout_v0_1.md`
2. `trades_inspection_readout_v0_1.md`
3. `trades_population_readout_v0_1.md`
4. `trades_file_acceptance_readout_v0_1.md`
5. `family_casepacks_index_v0_1.md`
6. `trades_review_cases_v0_1.md`
7. `trades_bad_cases_v0_1.md`
8. `trades_good_cases_v0_1.md`

The casepacks do not enumerate millions of files. They show the causal signature of each family and prevent the main audit error: reading every disagreement with `daily` or `1m` as intrinsic tape corruption.

## 9. Consumer Matrix

| Consumer | Decision |
| --- | --- |
| `data_quality_report` | allowed |
| `execution_realism_research` | allowed with state flags and declared basis |
| `microstructure_research` | allowed with taxonomy and state |
| `duplicate_odd_lot_session_diagnostics` | allowed |
| `backtest_core` | prohibited for unflagged raw conflict states |
| `backtest_extended` | allowed only for authorized `recoverable_with_flag` subsets |
| `daily_return_labels` | prohibited as direct source |
| `ml_microstructure` | allowed only with explicit family semantics |
| `ml_primary_daily` | restricted/prohibited unless a downstream policy explicitly governs use |
| `RL/live` | not enabled by this report |

## 10. Verdict

`trades_core_v0_1` meets the data-quality standard as a governed raw trade-tape layer with explicit quality states and recovery semantics.

Final verdict:

```text
complete_scoped_raw_trade_tape_layer_not_globally_clean_but_institutionally_governed
```

## 11. Open Debt

- `reference_scale_mismatch` needs stable scale reconciliation before broad promotion.
- `review_microstructure` recovery remains provisional and must not be treated as unflagged clean tape.
- Structural integrity tails need panel support beyond price-only views.
- `good` is too small to act as the operational universe.
- Any future promotion to execution simulator, ML primary or live workflows requires explicit downstream contract updates.
