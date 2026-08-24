# Massive SEC Form 3 schema contract v0.1

Status: **PROVISIONAL_LIVE_PROBE_PENDING**

Endpoint ID: form_3  
REST path: /stocks/filings/vX/form-3  
Query parameter: issuer_cik  
Page limit: 10,000

Documented/expected fields include accession_number,
date_of_original_submission, filing_date, filing_url, form_type, issuer_cik,
issuer_name, owner_cik, owner_name, period_of_report, security_title,
security_type, shares_owned and tickers.

Required row identity for the probe: accession_number, issuer_cik, form_type.

The sample audit must distinguish filing rows from owner/security-detail rows
and quantify whether an accession can legitimately repeat at this endpoint
grain.
