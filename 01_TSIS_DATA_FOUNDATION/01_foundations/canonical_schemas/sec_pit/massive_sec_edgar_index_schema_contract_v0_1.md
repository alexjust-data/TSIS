# Massive SEC EDGAR index schema contract v0.1

Status: **PROVISIONAL_LIVE_PROBE_PENDING**

Endpoint ID: edgar_index  
REST path: /stocks/filings/vX/index  
Query grain: one normalized issuer CIK pagination chain  
Page limit: 10,000

Documented/expected vendor fields:

- accession_number;
- cik;
- filing_date;
- filing_url;
- form_type;
- issuer_name;
- ticker.

Required row identity for the probe: accession_number, cik, form_type.

The probe must audit amendments, duplicate accession rows, ticker/CIK
relationships, date formats, NULLs, pagination completeness and agreement with
the frozen target membership.
