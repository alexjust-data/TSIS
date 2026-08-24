# Massive SEC 8-K disclosures schema contract v0.1

Status: **PROVISIONAL_LIVE_PROBE_PENDING**

Endpoint ID: eight_k_disclosures  
REST path: /stocks/filings/8-K/vX/disclosures  
Query parameter: cik  
Page limit: 1,000

Documented/expected fields include accession_number, cik, filing_date,
filing_url, primary/secondary/tertiary category, supporting_text and tickers.

Required row identity for the probe: accession_number and cik.

The audit must identify category cardinality, multi-item filings, supporting
text size, duplicate accession/category rows, missing categories and whether
taxonomy values reconcile with the separately acquired disclosure taxonomy.
