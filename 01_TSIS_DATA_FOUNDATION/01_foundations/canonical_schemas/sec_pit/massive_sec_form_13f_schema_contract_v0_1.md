# Massive SEC Form 13F conditional schema contract v0.1

Status: **CONDITIONAL_NOT_AUTHORIZED**

Endpoint ID: form_13f  
REST path: /stocks/filings/vX/13-F  
Maximum page limit: 1,000

Expected fields include accession_number, CUSIP, filer CIK, filing date/URL,
form type, issuer name, market value, period, shares/principal amount and type,
and title of class. Provisional identity is accession number, CUSIP and filer
CIK.

CIK targeting cannot express the objective membership directly because the
endpoint is filer-oriented. Acquisition requires a separate multi-quarter
global query, governed CUSIP-to-instrument PIT bridge, coverage/false-positive
audit and explicit authorization. v0.1 rejects any 13F config.
