# Quotes Quality Report v0.1

## 1. Scope And Role

Family:

```text
quotes_core_v0_1
```

Physical root:

```text
E:/TSIS/data/quotes
```

Role:

- RAW/STAGED book observations;
- canonical source for observed historical `bid`/`ask` state in Module 01;
- microstructure and execution-context evidence layer;
- not issuer identity, halt truth, corporate-action authority, adjusted price series or daily return layer.

## 2. Final Status

```text
complete_import_ready
```

`quotes_core_v0_1` is already institutional. This report imports the existing quotes audit, taxonomy, casepacks and readout into the normalized `data_quality_report/` surface.

## 3. Artifact Map

| Artifact | Status | Path |
| --- | --- | --- |
| Dataset contract | present | `01_foundations/contract_registry/dataset_contracts/quotes_dataset_contract_v0_1.md` |
| Label taxonomy and cut policy | present | `01_foundations/contract_registry/dataset_contracts/quotes_label_taxonomy_and_cut_policy.md` |
| Registry entry | present | `01_foundations/dataset_registry/quotes/quotes_registry_entry.yaml` |
| Consumption policy | present | `01_foundations/data_consumption_policies/quotes_consumption_policy.md` |
| Schema contract | present | `01_foundations/canonical_schemas/quotes/quotes_schema_contract.md` |
| Validators | present | `01_foundations/validators/quotes/quotes_validators.md` |
| Inspection readout | present | `01_foundations/inspection_dossiers/quotes/quotes_inspection_readout_v0_1.md` |
| Good case evidence | present | `01_foundations/inspection_dossiers/quotes/good_justification/quotes_good_cases_v0_1.md` |
| Review case evidence | present | `01_foundations/inspection_dossiers/quotes/flagged_case_evidence_packs/quotes_review_cases_v0_1.md` |
| Bad case evidence | present | `01_foundations/inspection_dossiers/quotes/bad_case_evidence_packs/quotes_bad_cases_v0_1.md` |
| Open casepack audit | present | `01_foundations/inspection_dossiers/quotes/quotes_open_casepacks_audit_v0_1.md` |
| Global policy assets | present | `01_foundations/inspection_dossiers/quotes/evidence_assets/global_policy/` |

## 4. File Structure And Technical Profile

Primary audited unit:

```text
ticker-date-file
```

Expected logical content:

- `ticker`;
- quote timestamp;
- `bid`;
- `ask`;
- conditional `bid_size`, `ask_size`, `exchange`, `conditions` and `session_date`.

The institutional session target is governed by `market_session_scope.md` and includes `04:00-20:00 America/New_York`.

## 5. Population And Coverage

The quotes readout summarizes this audited population:

| Severity | Count |
| --- | ---: |
| `PASS` | 4,365,496 |
| `SOFT_FAIL` | 4,078,384 |
| `HARD_FAIL` | 1,081,392 |
| total `ticker-date-file` population | 9,525,272 |

Final inspection translation:

| Human evidence bucket | Count |
| --- | ---: |
| `review` open cases | 64 |
| `bad` open cases | 15 |
| `good` representative sample | 12 |

Dominant taxonomy mass:

| Family | Count | Share |
| --- | ---: | ---: |
| `clean_pass_or_other` | 4,361,934 | 45.793% |
| `soft_crossed_micro_noise` | 1,924,034 | 20.199% |
| `persistent_soft_crossed_low` | 887,600 | 9.318% |

The five largest well-understood families sum to `86.868%` of the universe.

Open decision families:

| Family | Count | Share |
| --- | ---: | ---: |
| `high_hard_crossed_10_to_20` | 101,549 | 1.066% |
| `medium_file_threshold_edge_hard_many_crosses` | 85,963 | 0.902% |
| `large_file_threshold_edge_hard_many_crosses` | 50,288 | 0.528% |
| `persistent_soft_crossed_mid_large_scale` | 47,076 | 0.494% |
| total open decision mass | 284,876 | 2.991% |

## 6. Cleanliness And Interpretability

Quotes must be read in three layers:

| Layer | Meaning |
| --- | --- |
| population | full audited mass and taxonomy distribution |
| taxonomy | structural family of book behavior |
| casepack | human-forensic evidence for open decisions |

Critical interpretation rules:

- `HARD_FAIL` is an alarm state, not by itself the final consumption verdict.
- Crossed book behavior must separate `ask = 0` artifacts from economically interpretable `ask > 0` crossed states.
- UTC rollover and integerization can explain apparent anomalies without making the book automatically clean.
- External context can explain an episode, but it does not automatically rehabilitate local book quality.

The main danger is collapsing all crossed states into one binary variable. The audit shows at least two distinct classes:

- economically interpretable crossed states where `ask > 0`;
- mechanical or degraded crossed states dominated by `ask = 0`, integerization or timestamp partition effects.

## 7. Semantic Quality

Final quality vocabulary:

| State | Current reading |
| --- | --- |
| `good` | Clean or materially benign book families. |
| `review` | Open or contextualized families not clean enough for unflagged use. |
| `bad` | Local book quality too degraded or economically aggressive to defend. |

Institutional use must preserve price-view semantics:

- `quotes_raw` is the observed book layer;
- `split_normalized` may reconcile mechanical scale;
- `adjusted` is for daily economic price views, not raw book state;
- `adjusted_proxy` is diagnostic only.

Using adjusted daily prices as execution book truth is prohibited.

## 8. Case Evidence

The human auditor should read evidence in this order:

1. `quotes_inspection_readout_v0_1.md`
2. `quotes_open_casepacks_audit_v0_1.md`
3. `quotes_good_cases_v0_1.md`
4. `quotes_review_cases_v0_1.md`
5. `quotes_bad_cases_v0_1.md`

The casepacks are intentionally not a full enumeration of the universe. They show:

- what a clean or benign book looks like;
- why selected open families remain `review`;
- why selected hard families remain `bad`;
- where external context explains but does not automatically fix the local book.

## 9. Consumer Matrix

| Consumer | Decision |
| --- | --- |
| `data_quality_report` | allowed |
| `book_quality_research` | allowed under state flags |
| `microstructure_research` | allowed under quotes policy |
| `execution_context_analysis` | allowed as raw book evidence, not fill guarantee |
| `backtest_core` | allowed only where policy permits and state is declared |
| `ml_flagged` | allowed with explicit taxonomy and state |
| `ml_primary` | restricted |
| `execution_simulator` | not enabled automatically |
| `daily_return_labels` | prohibited as direct source |
| `adjusted price research` | prohibited as replacement for adjusted views |
| `RL/live` | not enabled by this report |

## 10. Verdict

`quotes_core_v0_1` meets the data-quality standard as the institutional raw book-observation layer.

Final verdict:

```text
complete_institutional_raw_quotes_layer_with_explicit_good_review_bad_policy
```

## 11. Open Debt

- The `good` casepack is representative, not exhaustive by design.
- The `review` and `bad` open casepacks must remain linked to the population taxonomy to avoid over-reading a small sample.
- Any execution simulator must declare whether it consumes raw, split-normalized, adjusted or diagnostic price views.
- Future policy changes to crossed severity, integerization, UTC rollover or open bucket handling require contract and changelog updates.
