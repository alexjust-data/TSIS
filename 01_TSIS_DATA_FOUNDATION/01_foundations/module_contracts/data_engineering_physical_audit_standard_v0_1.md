# Data Engineering Physical Audit Standard v0.1

## Purpose

This standard defines the minimum data-engineering audit required for every
physical data folder used by module 01.

It applies to RAW vendor data, reference data, context data, derived ETL views,
feature layers, label layers and evidence-producing datasets.

The rule is:

```text
No data folder can be considered institutionally audited unless its physical
files have been inspected directly.
```

Documentation, historical notebooks, Graphify graphs, contract summaries and
coverage tables are not enough by themselves.

## Scope

The active target root for current module-01 data work is:

- `E:/TSIS/data/`

The following roots can still appear in historical contracts, registries,
dossiers, builders or evidence:

- `C:/TSIS_Data/data/`
- `D:/`
- any other physical root referenced by a dataset registry, contract, policy,
  validator, materializer or inspection dossier.

Those roots must not be treated as equivalent by name alone.

Rule:

```text
E:/TSIS/data is the preferred active physical root.
C:/TSIS_Data/data and D:/ are legacy, mirror, historical, specialized or
source-specific roots unless a live contract says otherwise.
```

Any new audit, builder, materialization or master-table preparation should
start from `E:/TSIS/data/` unless the dataset-specific contract explicitly
requires another root.

It also applies when a folder is only a context, review, provenance or derived
layer. Lower consumer permission does not remove the audit obligation.

## Non-Negotiable Rule

Every data folder must have a direct physical inspection package before it can
be described as `>90%` complete in `01_foundations`.

The package must prove what exists on disk, what shape it has, what rows mean,
what failures exist and what consumers are allowed to do with the result.

## Minimum Audit Dimensions

### 1. Root And Inventory

The audit must emit:

- canonical root path;
- expected subfolders;
- actual subfolders;
- file count by subfolder;
- file suffix/type distribution;
- total bytes when feasible;
- missing expected folders;
- unexpected folders;
- inventory manifest path;
- run timestamp.

### 2. File-Level Readability

The audit must check:

- files open with the expected reader;
- unreadable files;
- zero-byte files;
- empty files;
- corrupt parquet/csv/json/yaml files;
- schema extraction success;
- file-level row counts;
- file-level min/max dates where applicable.

### 3. Schema And Type Conformance

The audit must compare physical columns to schema contracts:

- required columns present;
- unexpected columns recorded;
- logical types checked;
- parseable datetime/date columns;
- numeric coercion for numeric fields;
- string/ticker fields normalized only for inspection, not silently rewritten;
- nested/list/object fields identified when present.

### 4. Identity And Partition Integrity

For ticker/date/partitioned roots, the audit must check:

- folder ticker vs payload ticker;
- file name ticker vs payload ticker;
- partition key vs payload key;
- duplicate keys;
- null keys;
- malformed tickers;
- suffix/class/share-class edge cases;
- entity reuse or ticker-change ambiguity when reference evidence exists.

### 5. Temporal Integrity

The audit must check:

- date range per file;
- global date range;
- rows before entity first-seen date;
- rows after entity last-observed date;
- duplicate dates/timestamps;
- monotonicity where applicable;
- timezone handling for intraday/event timestamps;
- lookahead/leakage risk for derived, feature or label layers.

### 6. Value Integrity

The audit must check values appropriate to the folder:

- prices positive and OHLC coherent for price data;
- sizes/volumes non-negative;
- bid/ask/spread coherence for book data;
- ratio denominator caveats for fundamentals/ratios;
- amount/share/split-ratio sanity for corporate actions;
- short-interest/short-volume arithmetic consistency for short data;
- null rates for critical columns;
- outliers and impossible values.

### 7. Coverage And Expectedness

The audit must separate:

- file presence;
- non-empty files;
- effective rows;
- expected missingness;
- unexpected missingness;
- sparse-but-valid families;
- coverage by ticker, date, dataset and subfamily.

Sparse context can be valid, but it must be explicitly classified as expected
sparsity, not silently counted as failure or success.

### 8. Cross-Source Reconciliation

When an authority exists, the audit must compare against it:

- `reference` for identity, lifecycle and corporate actions;
- FINRA or provenance layers for short data;
- market data roots for event overlays;
- daily/1m/quotes/trades for price/book/tape consistency where appropriate.

Reconciliation disagreement is not automatically `bad`, but it must produce a
review state or reason code.

### 9. Acceptance States

The audit must emit explicit states, such as:

- `pass`;
- `good`;
- `review`;
- `recoverable_with_flag`;
- `limited_window`;
- `reference_conflict`;
- `ticker_reuse_review`;
- `secondary_authority_only`;
- `forensic_only`;
- `bad`;
- `quarantine`.

The vocabulary must be compatible with `semantic_authority.md` and
`bad_evidence_and_rehabilitation.md`.

### 10. Human Inspection Evidence

Every audited folder must have a human-readable dossier that includes:

- population overview;
- visual overview when the folder has enough complexity;
- examples of good cases;
- examples of review/flagged cases;
- examples of bad/quarantine cases when they exist;
- explanation for sparse-but-valid cases;
- links to generated CSV/JSON/parquet manifests;
- readout with final institutional interpretation.

For every important image, the dossier must include:

```text
What it shows
What it answers
What it does not answer
How an inspector should read it
What institutional decision it supports
What limit remains open
```

## Builder Requirement

The preferred form is an executable builder under:

```text
scripts/inspection/<dataset_or_family>/
```

The builder must not rewrite historical audit folders. It should read historical
evidence and active physical data, then emit current evidence under
`01_foundations/inspection_dossiers/<dataset_or_family>/`.

Manual one-off inspection is not enough for a folder to clear the `>90%` gate.

## Relationship To Other Contracts

This standard extends:

- `evidence_model.md`;
- `inspection_dossier_model.md`;
- `layer_validation_standard_v0_1.md`;
- `raw_data_authority_and_derivation_map.md`;
- `bad_evidence_and_rehabilitation.md`;
- `dataset_contract_template.md`.

It does not replace dataset-specific contracts, schemas, policies or validators.

## Maturity Gate

For `01_foundations/README.md`, a data folder or family cannot be reported above
`90%` unless it has:

1. dataset contract;
2. canonical schema or schema family;
3. registry entry;
4. consumption policy;
5. validator;
6. physical data-engineering audit package;
7. inspection dossier with human-readable readout;
8. evidence assets with tables and visuals where applicable;
9. changelog or documented promotion note;
10. explicit remaining limits.

If any of these are missing, the maturity must stay below `90%` or the missing
gate must be declared next to the percentage.

## Final Rule

Every data folder must be audited as data, not only described as an idea.

Institutional confidence comes from inspecting physical files, not from knowing
that a root exists.
