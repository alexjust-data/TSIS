# Graphify Refresh Queue — Core Market RAW Alignment Audit

## GFQ-20260821-CORE-MARKET-QUOTES-ACCEL-001

Status: pending  
Date: 2026-08-21  
Severity: MEDIUM  
Leaf target: `foundations_authority / core market RAW alignment audit`

Affected files:

- `quotes_worker_acceleration_runbook_v0_1.md`;
- `CHANGELOG.md`;
- `../../../../scripts/core_market_raw_alignment_audit/accelerate_quotes_workers.py`;
- `../../../../scripts/core_market_raw_alignment_audit/monitor_quotes_accelerator.ps1`;
- `../../../../tests/core_market_raw_alignment_audit/test_quotes_accelerator.py`.

Reason: the active full audit now includes an auxiliary transactional scheduler
for Quotes, an automatic 2-to-3 worker gate and an independent long-operation
control surface. The official Graphify leaf was not rebuilt because the full
source-disk scan is still active.

Required action: after the full audit closes, rebuild and diagnose the
core-market alignment leaf, encode the acceleration/resume topology and update
the corresponding `BUILD_MANIFEST.md` before the next governed root merge.
