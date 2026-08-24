# Massive SEC Form 4 schema contract v0.1

Status: **PROVISIONAL_LIVE_PROBE_PENDING**

Endpoint ID: form_4  
REST path: /stocks/filings/vX/form-4  
Query parameter: issuer_cik  
Page limit: 10,000

Documented/expected fields include accession_number,
date_of_original_submission, filing_date, filing_url, form_type, issuer_cik,
issuer_name, owner CIK/name, period_of_report, record_type, security
title/type, transaction code/date/price/shares, post-transaction shares and
tickers.

Required row identity for the probe: accession_number, issuer_cik, form_type.

The audit must determine true row grain, derivative/non-derivative semantics,
numeric representation, amendment behavior, duplicates and NULL/unavailable
values before typed materialization.
