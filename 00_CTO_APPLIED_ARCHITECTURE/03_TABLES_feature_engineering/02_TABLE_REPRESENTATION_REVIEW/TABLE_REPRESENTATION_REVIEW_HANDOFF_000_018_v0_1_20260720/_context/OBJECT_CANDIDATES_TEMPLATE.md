# <TABLE_ID> <TABLE_NAME> - Object Candidates

Status: `object_candidates_draft`
Date: `<YYYY-MM-DD>`

This file belongs to the Object Discovery Process.

Information Object definition:

```text
A semantic unit of information that TSIS decides to preserve
about one or more observable phenomena, independent of its
Representation Model and physical implementation.
```
It is a bridge between table review and Information Object admission.
It does not admit objects by itself.
It does not define scientific meaning by itself.
It records candidate objects discovered while reviewing a table.

The Object Admission Process must later reconstruct the scientific direction:

```text
phenomenon_or_scientific_need
    -> Information Object
        -> Representation Model
            -> implementation candidates
                -> temporal legality
                    -> admission decision
```

---

## Source Table

```text
table_id:
table_name:
dataset_id:
review_file:
```

---

## Candidate Objects

### <Candidate Object Name>

Candidate Object:

```text
<Candidate Object Name>
```

Taxonomy axes:

```text
information_object_family:
source_domain:
temporal_resolution:
institutional_role:
```

Rule:

```text
Do not use a single generic family field.
The candidate may be semantic, but source, time scale and institutional role must remain separate.
```


Candidate variables:

```text
variable_1
variable_2
variable_3
```

Why this may be an Information Object:

```text
...
```

Current table location:

```text
<table_name>
```

Candidate status:

```text
pending_admission
```

Allowed statuses:

```text
pending_admission
accepted
accepted_with_restrictions
rejected
merged_into_existing_object
blocked_pending_evidence
```

Reference to Information Object file:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\<object_name>.md
```

Notes:

```text
...
```
