# 03_TABLES_feature_engineering Local Rules

Status: `local_rules_v0_1`
Date: `2026-07-16`

These rules govern work inside:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering
```

They refine the parent local rules:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\LOCAL_RULES.md
```

---

## 1. Role

`03_TABLES_feature_engineering` is a table representation and feature engineering audit surface.

It helps connect:

```text
epistemology
representation governance
operational contracts
builders
validators
manifests
physical datasets
market representation families
variable hypotheses
feature engineering decisions
```

It is not automatically the official source of truth for a table.

Official table status must be proven through operational evidence.

---

## 2. Maturity Levels

Every table must be classified before work starts:

```text
specification_only
candidate_materialized
validated_candidate
official_promoted
historical_or_superseded
```

Rules:

```text
file exists != official table
parquet exists != promoted table
manifest exists != downstream permission
Graphify node exists != operational proof
```

---

## 3. Six-Question Gate

Every table analysis must answer these questions before attributes are
finalized:

```text
What phenomenon or representation do I want to materialize?

Why does it deserve to exist as its own entity?

What scientific questions must it answer?

What other representations consume it?

What minimum information does it need to contain?

Now, and only now:
What attributes must it have?
```

Operational rule:

```text
Do not start by listing columns.
Start by defining representation responsibility.
Then derive the minimum required attributes.
```

Additional feature engineering guardrail:

```text
What do we need to know
to correctly describe
the state of the market
at an instant t?

What information can help
explain or predict
the future behavior
of the phenomenon represented?
```

Every variable must justify:

```text
why it deserves to exist
which scientific hypothesis it represents
which market representation family it belongs to
which downstream consumer can use it
```

---

## 4. Required Evidence For Table Status

A table status claim must cite at least one relevant authority:

```text
schema contract
dataset contract
dataset registry entry
data consumption policy
validator
builder
manifest
summary
status matrix
pytest result
physical artifact inspection
```

Do not infer status from folder naming alone.

---

## 5. 013-018 Working Rule

The active dependency logic is:

```text
013 quote-guarded 1m base
    -> 014 master intraday bars
        -> 018 scanner/event candidates
            -> event windows
                -> 015 microstructure features
                    -> 016 market state
                        -> 017 event state
                            -> outcomes / downstream research
```

Implementation order may be adjusted, but dependency meaning must not be
inverted.

---

## 6. 013 Specific Rule

`013_ohlcv_1m_quote_guarded` must be read as:

```text
raw ohlcv_1m
+
repair_manifest_lt1b_v0_1.parquet
=
ohlcv_1m_quote_guarded view
```

It is a governed overlay/view, not an official full-universe physical
replacement tree.

---

## 7. Changelog Rule

Update:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\CHANGELOG.md
```

when a table reading, maturity level, operational dependency or validation
status changes.

Do not log trivial formatting.

---

## 8. Final Rule

The goal of `03_TABLES_feature_engineering` is governed implementation, not more literature.

Documents here should unblock table creation, validation or correct downstream
consumption, and should prevent unjustified variable accumulation.

