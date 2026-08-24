# Massive SEC disclosure taxonomy schema contract v0.1

Status: **PROVISIONAL_LIVE_PROBE_PENDING**

Endpoint ID: disclosure_taxonomy  
REST path: /stocks/taxonomies/vX/disclosures  
Query grain: one singleton pagination chain  
Page limit: 1,000

Documented/expected fields include description, primary/secondary/tertiary
category and taxonomy.

Required row identity for the probe: taxonomy and primary_category.

The taxonomy response must be versioned by retrieval time and raw hash. It
cannot be assumed historically invariant, and it must reconcile with category
values observed in 8-K disclosure rows.
