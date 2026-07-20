# <TABLE_ID> <TABLE_NAME> - Table Representation Review

Status: `table_representation_review_draft`
Date: `<YYYY-MM-DD>`

This review is deliberately operational.
It does not promote the table.
It determines what the table represents, what it contains, what it lacks, and whether it can feed Market State / Event State.

Companion files in the same table folder:

```text
<table_name>.md
= current physical / contractual / schema state

table_representation_audit_ES.md
= this table-level audit

object_candidates.md
= bridge to Information Object admission, when candidate objects are detected
```

---

## 1. Table Identity

```text
table_id:
table_name:
dataset_id:
review_scope:
maturity_level:
```

Allowed maturity levels:

```text
specification_only
candidate_materialized
validated_candidate
official_promoted
historical_or_superseded
```

---

## 2. Level 1 - Architectural Questions

### 1. What entity, representation or institutional function does the table materialize?

```text
...
```

### 1.1 Does it represent market information, infrastructure, context, quality, governance, event, state or outcome?

```text
...
```

### 1.2 If it stores market information, what market phenomena do the stored information help describe?

```text
...
```

For institutional infrastructure tables, answer explicitly:

```text
not_applicable_as_market_phenomenon
```

### 2. Why does it deserve to exist as its own entity?

```text
...
```

### 3. What scientific questions must it answer?

```text
...
```

### 4. What other representations consume it?

```text
...
```

### 5. What minimum information does it need to contain?

```text
...
```

### 6. Only now: what attributes must it have?

```text
...
```

---

## 3. Level 2 - Physical And Boundary Questions

### 7. Grain

```text
...
```

### 8. Primary Key

```text
...
```

### 9. What does it consume?

```text
...
```

### 10. What does it produce?

```text
...
```

### 11. What information must it not contain?

```text
...
```

### 12. Column Classification

| Category | Columns |
| --- | --- |
| identity |  |
| observable |  |
| derived |  |
| quality |  |
| lineage |  |
| as_of |  |
| governance |  |
| outcome |  |

### 13. Information Objects Implemented

| Information Object | Full / Partial | Variables | Notes |
| --- | --- | --- | --- |
|  |  |  |  |

### 14. Variables Not Yet Justified

```text
...
```

### 15. Missing Information

```text
...
```

### 16. Overlap With Other Tables

```text
...
```

### 17. Temporal Legality

```text
as_of_defined:
decision_timestamp_safe:
leakage_risk:
required_policy:
```

### 18. Physical / Contractual / Validation / Promotion Status

```text
physical_status:
contract_status:
validation_status:
promotion_status:
```

---

## 4. Evidence Paths

```text
schema_contract:
dataset_contract:
registry_entry:
consumption_policy:
validator:
builder:
manifest:
summary:
tests:
physical_artifact:
```

---

## 5. Review Decision

```text
decision:
required_changes:
can_feed_market_state:
can_feed_event_state:
notes:
```

Allowed decisions:

```text
keep_as_is
keep_with_restrictions
redesign_required
split_required
merge_required
archive_or_supersede
blocked_pending_evidence
```



