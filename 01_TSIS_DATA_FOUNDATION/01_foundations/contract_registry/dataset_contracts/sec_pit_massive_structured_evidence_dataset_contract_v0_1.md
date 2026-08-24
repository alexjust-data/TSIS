# SEC PIT Massive structured evidence dataset contract v0.1

Status: **PROVISIONAL_NOT_MATERIALIZED**

## Identity

Logical dataset ID: sec_pit_massive_structured_evidence_v0_1  
Provider: Massive REST Stocks/Filings  
Physical root: D:/sec_float_pit_MASSIVE  
Promotion class: raw vendor evidence

This dataset is not the canonical SEC truth, a canonical float series or a
point-in-time market-state feature. It is retained source evidence requiring
reconciliation against governed SEC and TSIS contracts.

## Included endpoint families

- EDGAR filing index;
- Form 3/3-A structured ownership;
- Form 4/4-A structured ownership transactions;
- 8-K structured disclosures;
- disclosure taxonomy.

8-K text and 13F are absent from v0.1 unless later versions cite independent
gate and authorization evidence.

## Grains

Raw grain: one immutable vendor response page, identified by raw SHA-256.

Commit grain: one endpoint plus sanitized page-URL work ID.

Normalized grain: one vendor result row plus acquisition lineage fields.

Endpoint business keys are provisional until live-probe sample audit:

- EDGAR index: accession number, CIK, form type;
- Form 3: accession number, issuer CIK, form type;
- Form 4: accession number, issuer CIK, form type;
- 8-K disclosure: accession number, CIK;
- taxonomy: taxonomy and primary category.

Any observed mismatch fails the probe; the contract must be versioned rather
than silently changing production semantics.

## Required acquisition lineage

Every normalized row must include endpoint ID, Massive request ID, retrieval
UTC timestamp, raw SHA-256, target CIK and row index. Every page receipt must
bind sanitized URL, raw/normalized paths and hashes, row count, next URL,
HTTP/retry metrics and observed fields.

## Target semantics

The source membership is exactly 4,824 ordered ticker cases from target
SHA-256 1ae6fe0391383fbf83d5e0b800d91db690a386d07a780481f354d9b3850718ee.
Calls are deduplicated to 4,288 normalized issuer CIKs while preserving every
ticker/instrument membership in a pre-manifest hash.

## Quality gates

No promotion is permitted until:

- license/retention confirmation is persisted;
- bounded live probe passes;
- endpoint schemas and sample values are audited;
- pagination and target coverage reconcile;
- raw and normalized hashes validate;
- duplicate identities and NULL/unavailable semantics are quantified;
- temporal meaning and PIT-safe downstream use are documented;
- the full run receives a separate authorization and final audit.
