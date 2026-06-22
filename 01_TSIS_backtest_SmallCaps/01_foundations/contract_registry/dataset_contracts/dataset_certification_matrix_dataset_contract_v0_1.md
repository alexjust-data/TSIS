# Dataset Certification Matrix Dataset Contract `v0_1`

## 1. Dataset Identity

```text
dataset_id: dataset_certification_matrix_v0_1
family: data_foundation_outputs
class: certification/quality table
grain: dataset_family + certification_scope + quality_policy_version
```

## 2. Purpose

`dataset_certification_matrix` converts the human-readable family status matrix
into a governed table.

It answers:

```text
For this data family, what is the current inspected quality verdict, completion
state, visual evidence state and downstream gate?
```

It does not answer whether a specific ticker/date row is present or clean.

## 3. Source Lineage

Authoritative source:

```text
01_foundations/data_quality_report/family_status_matrix_v0_1.md
```

The materializer also verifies the real presence of:

- physical source roots;
- family quality reports;
- inspection dossiers;
- schema contracts;
- dataset contracts;
- registry entries;
- data consumption policies;
- validators;
- visual evidence assets.

## 4. Physical Layout

```text
E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix/
  dataset_certification_matrix_v0_1.parquet
  _dataset_certification_matrix_summary_v0_1.csv
  _dataset_certification_matrix_manifest_v0_1.json
```

## 5. Current Materialization

```text
build_run_id: dataset_certification_matrix_v0_1_20260622T154116Z
rows: 13
families: 13
human_inspector_ready_count: 13
visual_casepack_complete_count: 13
blocked_from_backtest_core_count: 2
scoped_only_count: 5
hard_fail_count: 0
output_sha256: e7803e3ec58cfb92c1313efc09bdd3a015800c4680437e4567a0174b257f1fb0
source_family_status_matrix_sha256: c380c7a5f85c14925410899b264de4e52c62571a1b1ff7b359cec733f16f5d35
```

Data quality verdict counts:

```text
usable_for_declared_scope: 6
complete_scoped: 5
blocked_by_data_defect: 2
```

## 6. Allowed Consumers

Permitted:

- `data_quality_report`
- `expected_data_calendar`
- `master_daily_table`
- `master_intraday_bar_table`
- `event_engine`
- `research_only`
- `forensic_only`

Conditionally permitted:

- `backtest_core`
- `backtest_extended`
- `ml_flagged`

Condition:

```text
Only as a gate or mask. It must be joined to actual data and family validators.
```

Prohibited:

- use as market data;
- use as feature value;
- use as label;
- use as price-view authority;
- use as proof that a ticker/date observation is clean.

## 7. Quality Policy

Good structural state:

- one row per family in `family_status_matrix_v0_1.md`;
- every claimed evidence surface exists;
- every visual-complete family has image evidence;
- every row links to contract, schema, registry, policy and validator.

Bad structural state:

- missing mandatory artifact;
- duplicate family;
- absent physical root;
- visual-complete claim with no images;
- hash drift without rematerialization.

Consumption interpretation:

- `declared_scope_allowed`: family can be consumed only as its own policy allows.
- `scoped_only`: family can be consumed only with scope flags and limitations.
- `blocked_from_backtest_core`: family is blocked from core quantitative use until repair or explicit waiver.

## 8. Known Limitations

- v0.1 is family-level, not ticker/date-level.
- It inherits the source matrix reference date.
- It does not run row-level market-data validation.
- It does not decide if a specific event window is tradable.
- It does not repair blocked families.

## 9. Change Policy

Version bump or rematerialization required when:

- the source matrix changes;
- a family status changes;
- a new family is added;
- a family is removed;
- a downstream gate changes;
- required evidence surfaces change;
- the schema changes.

