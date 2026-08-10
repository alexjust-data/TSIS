# TRADING_ACTIVITY_TA3_G_ONLY_SOURCE_AUTHORITY_DECISION_v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_ta3_g_only_source_authority_decision` |
| `document_version` | `v0_1` |
| `document_role` | `PHYSICAL_SOURCE_AUTHORITY_DECISION` |
| `document_status` | `FROZEN` |
| `effective_at` | `2026-08-07` |

---

## 1. Decision

The only authorized physical trade root for Trading Activity TA-3 is:

```text
G:/TSIS/data/trades_ticks_prod_2005_2026
```

No legacy drive, historical path or Foundation lineage reference may be used as
a fallback physical source.

---

## 2. Legacy-path boundary

Some historical Foundation evidence rows retain source paths under older drive
letters. Those paths prove where an earlier audit read a file. They do not grant
current consumption authority.

```text
legacy path in evidence
= historical lineage only

legacy file still physically present
= not authorized for TA-3 calculation

missing file in G:
= UNAVAILABLE_G_OFFICIAL
```

No data may be copied from a legacy root to rehabilitate this sample silently.
Any future governed migration into `G:` requires its own manifest, hashes,
validation and versioned source-gate rerun.

---

## 3. Missingness semantics

Absence of `market.parquet` under the official G root is not equivalent to zero
trading activity.

Every selected scope row must preserve one of:

```text
AVAILABLE_G_OFFICIAL
UNAVAILABLE_G_OFFICIAL
```

`UNAVAILABLE_G_OFFICIAL` is retained in the denominator. It is not silently
excluded, rewritten as zero or resolved from another drive.

---

## 4. Sample-selection consequence

Physical-file absence alone does not automatically replace a block. The
preregistered TA-3 sample intentionally preserves missingness and quality
conditions. A block may be replaced only after a variable-relevant local audit
assigns `LOCALLY_AUDITED_REPLACE_WINDOW`.

For the frozen sample, source-file presence must be audited separately for:

```text
target current-state observability
B20 physical reference cardinality
B60 physical reference cardinality
B120 physical reference cardinality
intervening-session continuity
```

The cardinality audit does not itself prove content-level coverage. The Binding
A runner must still apply the frozen coverage, eligibility and quality policies
inside every available file.

---

## 5. Authorization boundary

```text
G ROOT CONSUMPTION
= AUTHORIZED

LEGACY ROOT CONSUMPTION
= PROHIBITED

LEGACY PATH AS LINEAGE TEXT
= AUTHORIZED

MISSING G FILE AS ZERO ACTIVITY
= PROHIBITED

MISSING G FILE AS UNAVAILABLE
= REQUIRED
```
