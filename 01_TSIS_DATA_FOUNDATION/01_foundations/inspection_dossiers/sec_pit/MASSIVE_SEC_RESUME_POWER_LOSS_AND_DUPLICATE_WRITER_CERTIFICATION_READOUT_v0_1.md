# Massive SEC resume, power-loss and duplicate-writer certification readout v0.1

Status: **PASS_MOCKED_CONTROL_PLANE**

Date: 2026-08-22

## Certified scenarios

| Scenario | Result | Evidence |
|---|---|---|
| raw + normalized + receipt commit | PASS | hashes recompute from receipt |
| crash after receipt before request ledger | PASS | ledger rebuilt deterministically from receipt |
| same work ID with changed normalized bytes | PASS_FAIL_CLOSED | collision raises and cannot overwrite |
| second live writer | PASS_BLOCKED | exclusive root lock rejects process |
| dead same-host writer | PASS_RESUMABLE | stale lock archived only by resume |
| network failure after first of two pages/chains | PASS | first execution terminal FAILED with one receipt |
| resume same run | PASS | committed page skipped; one remaining request; final COMPLETE |
| credential in URL | PASS_BLOCKED | Bearer header used; sanitized URL persisted |
| 429 response | PASS_ADAPTIVE | shared rate reduced from 2 to 1 req/s in test |
| pagination host/path escape | PASS_BLOCKED | response rejected before commit |

Test command and scope are documented in
01_foundations/validators/sec_pit/massive_sec_acquisition_validators_v0_1.md.
Result: 20 passed.

## Recovery guarantees

Recovery is page-granular and receipt-authoritative. Resume validates frozen
inputs/code/authorization and artifact hashes. Only an uncommitted in-flight
page may be downloaded again.

## Explicit limits

- no HTTP byte-range continuation is claimed;
- a vendor response that changes for the same work ID fails closed instead of
  overwriting prior bytes;
- operating-system and USB-disk caches cannot provide absolute protection from
  sudden hardware failure;
- a single physical D drive is not a backup;
- live Massive behavior remains untested until authorized.

Recommended physical controls: UPS, healthy NTFS target, SMART/health checks
outside this runner, and a separately governed post-download copy to another
physical volume before institutional promotion.
