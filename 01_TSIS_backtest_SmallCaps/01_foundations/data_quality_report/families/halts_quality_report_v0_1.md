# Halts Quality Report v0.1

## 1. Scope And Role

Family:

```text
halts_v0_1
```

Physical root:

```text
E:/TSIS/data/Halts
```

Role:

- RAW reference/event data;
- official halt/regulatory context;
- event and audit overlay;
- not alpha, price, book, tape or execution data.

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
| Dataset contract | present | `01_foundations/contract_registry/dataset_contracts/halts_dataset_contract_v0_1.md` |
| Registry entry | present | `01_foundations/dataset_registry/halts/halts_registry_entry.yaml` |
| Consumption policy | present | `01_foundations/data_consumption_policies/halts_consumption_policy.md` |
| Validators | present | `01_foundations/validators/halts/halts_validators.md` |
| Inspection readout | present | `01_foundations/inspection_dossiers/halts/halts_inspection_readout_v0_1.md` |
| Evidence assets | present | `01_foundations/inspection_dossiers/halts/evidence_assets/` |
| Casepacks | present | `01_foundations/inspection_dossiers/halts/*case_evidence_packs/` |
| Visual inspector pack | present | `01_foundations/inspection_dossiers/halts/visual_inspector_pack/` |
| Schemas | present | `01_foundations/canonical_schemas/halts/` |

## 4. Physical And Technical Profile

Root audit:

| Root | Files | Dirs | Parquet | CSV | XML | HTML | JSON |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `E:/TSIS/data/Halts` | 5,702 | 6 | 5 | 17 | 5,662 | 16 | 2 |

The E root matches the observed historical D root by aggregate footprint.

## 5. Population And Quality

Canonical event taxonomy:

| Event taxonomy | Events |
| --- | ---: |
| `good_full_intraday_event` | 129,638 |
| `good_date_level_event` | 1,272 |
| `review_partial_identity` | 1,096 |
| `regulatory_context_only` | 250 |
| `bad_unusable_event` | 1 |

LT1B event taxonomy:

| Event taxonomy | Events |
| --- | ---: |
| `good_full_intraday_event` | 53,720 |
| `good_date_level_event` | 186 |
| `regulatory_context_only` | 3 |

## 6. Semantic Reading

Strong:

- official halt/event context;
- dominant full-intraday event mass;
- coherent quote/trade overlays in large case families.

Limits:

- SEC/context/date-level data is not intraday;
- absence of halt does not mean clean market;
- visual absence does not automatically invalidate official event.

## 7. Consumer Matrix

| Consumer | Decision |
| --- | --- |
| `event_engine` | allowed |
| `data_quality_report` | allowed |
| `forensic_review` | allowed |
| `quotes/trades/minute overlays` | allowed with temporal flags |
| `backtest masks` | restricted |
| `alpha` | not enabled |
| `execution_simulator` | not enabled |
| `RL/live` | not enabled |

## 8. Verdict

`halts_v0_1` meets the data-quality standard as a modern foundation event layer.

It also meets the human-inspector package standard through a formal visual
inspector pack with generated panels, copied population visuals, manifest and
asset audit.

Final verdict:

```text
complete_foundation_event_context_layer
```
