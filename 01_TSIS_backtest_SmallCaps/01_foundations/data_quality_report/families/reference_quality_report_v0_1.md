# Reference Quality Report v0.1

## 1. Scope And Role

Family:

```text
reference_v0_1
```

Physical root:

```text
E:/TSIS/data/reference
```

Role:

- identity;
- lifecycle;
- corporate actions;
- event/reference support;
- universe support;
- not price, tape, book, alpha or final universe membership by itself.

## 2. Final Status

```text
complete_import_ready
```

The modern dossier is complete for foundation promotion.

Foundations completion status:

```text
human_inspector_ready
```

Visual inspection status:

```text
visual_complete
```

## 3. Artifact Map

| Artifact | Status | Path |
| --- | --- | --- |
| Dataset contract | present | `01_foundations/contract_registry/dataset_contracts/reference_dataset_contract_v0_1.md` |
| Registry entry | present | `01_foundations/dataset_registry/reference/reference_registry_entry.yaml` |
| Consumption policy | present | `01_foundations/data_consumption_policies/reference_consumption_policy.md` |
| Validators | present | `01_foundations/validators/reference/reference_validators.md` |
| Inspection readout | present | `01_foundations/inspection_dossiers/reference/reference_inspection_readout_v0_2.md` |
| Institutional closeout | present | `01_foundations/inspection_dossiers/reference/reference_institutional_closeout_v0_1.md` |
| Evidence assets | present | `01_foundations/inspection_dossiers/reference/evidence_assets/` |
| Casepacks | present | `01_foundations/inspection_dossiers/reference/*case_evidence_packs/` |
| Visual inspector pack | present | `01_foundations/inspection_dossiers/reference/visual_inspector_pack/` |
| Schemas | present | `01_foundations/canonical_schemas/reference/` |

## 4. Physical And Technical Profile

Observed subfamilies:

- `all_tickers`;
- `overview`;
- `events`;
- `exchanges`;
- `splits`;
- `dividends`;
- `ticker_types`;
- `_run`.

Readout evidence:

- `all_tickers`: 3,109 parquet files;
- `overview`: 12,468 ticker dirs / parquet files;
- `events`: 12,468 ticker dirs / parquet files;
- `splits`: 12,468 ticker dirs / parquet files;
- `dividends`: 12,468 ticker dirs / parquet files;
- `exchanges`: 1 parquet file;
- `ticker_types`: 1 parquet file;
- `_run`: 3 operational files.

## 5. Quality Reading

Identity:

- `good_identity_snapshot = 12,093`;
- `bad_unresolved_identity = 200`;
- `review_transient_symbol = 175`.

Payload families:

- dividends strong and non-empty;
- splits real but sparse;
- events mainly ticker-change related;
- all_tickers is presence/snapshot support, not universe final.

## 6. Semantic Restrictions

`reference` may support:

- corporate actions service;
- price view builders;
- daily adjusted;
- 1m split-normalized;
- universe support;
- event overlays;
- forensic review.

It does not enable:

- alpha;
- live;
- RL;
- ticker changes as trading signals;
- all_tickers as final universe;
- overview market cap as daily point-in-time membership.

## 7. Consumer Matrix

| Consumer | Decision |
| --- | --- |
| `data_quality_report` | allowed |
| `corporate_actions_table` | allowed with policy |
| `price_view_builders` | allowed |
| `universe support` | allowed |
| `event overlays` | allowed |
| `backtest_core` | restricted/not default |
| `ML/RL/live` | not enabled |

## 8. Verdict

`reference_v0_1` meets the data-quality standard as a modern foundation reference layer.

It also meets the human-inspector package standard through a formal visual
inspector pack with generated panels, copied population visuals, manifest and
asset audit.

Final verdict:

```text
complete_foundation_reference_layer
```
