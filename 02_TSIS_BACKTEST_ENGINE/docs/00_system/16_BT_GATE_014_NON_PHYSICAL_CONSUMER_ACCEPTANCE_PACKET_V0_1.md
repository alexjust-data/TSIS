# BT-GATE-014 Non-Physical Consumer Acceptance Packet V0.1

```text
BT-GATE-014 = SINGLE_USE_PHYSICAL_AUTHORIZATION_ISSUED_NOT_CONSUMED
BT-GATE-014_PHASE_B_EXTERNAL_RE_REVIEW = PASS
PHASE_B_NON_PHYSICAL_IMPLEMENTATION = ACCEPTED
NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION = AUTHORIZED_NOT_CONSUMED
PHYSICAL_CONSUMER_READ = NOT_EXECUTED
PHYSICAL_STATE_ROWS_READ = 0
PHYSICAL_CONSUMER_EVIDENCE = NOT_YET_PRODUCED
BT-GATE-014_CLOSED_PASS = NOT_AUTHORIZED
```

## Corrected evidence

```text
positive cases = 15/15 PASS
negative cases = 33/33 PASS
external-review regression tests = 27/27 PASS
included tests = 36 PASS
full repository tests = 155 PASS, 0 skipped
deterministic output hash = bb499dd82edf7b7fb165aa9d5e088468e946138c16b1ffce89a4bbb74b8bd7fd
scientific manifest hash = 25f80ee5c11aadd2838fbc8a54aa7b182ed2583fc49f1ba78c1cb26e235456ee
physical state rows read = 0
orders/fills/positions/cash/equity mutations = 0
PnL calculated = false
```

Corrected findings: complete component/row temporal equations; stored-at visibility; rows-sidecars bijection; exact frozen runtime authority; real permutation and two-root manifest tests; input hash/size binding; fully reproducible repository suite.

## Reproduction

```powershell
python -m pip install -e .
python -B RUN_BT_GATE_014_INCLUDED_TESTS.py
python -B RUN_FULL_REPOSITORY_TESTS.py
python -B scripts/run_bt_gate_014_non_physical_market_state_consumer.py
```

Validated-store boundary: only `ValidatedBoundedMarketStateAvailable` with a receipt bound to event content and frozen authority is accepted. Package JSON evidence is reported from `ZIP_MANIFEST.json`; repository-local JSON counts are not package claims.


## Latest contract-conformance correction

- Provider ZIP identities are checked directly against compiled frozen pins,
  adoption before/after values, configuration pins and the nested ZIP bytes.
- Validation and receipt issuance are atomic through
  `validate_and_seal(raw_row, sidecar, frozen_authority, consumed_sidecar_sha256)`.
- Component status uses provider semantics: component `available`, row
  `available_for_decision_replay`; component IDs and rule IDs are mandatory.
- Consumed synthetic sidecar identity is separated from provider sidecar
  authority identity.
- Market bars come from an independent, closed and hashed synthetic fixture.
- `POSITIVE_10`, `POSITIVE_12`, `NEGATIVE_18` and `NEGATIVE_31` execute their
  declared behavior.
- `next_required_authorization =
  NEW_SINGLE_USE_PHYSICAL_CONSUMER_AUTHORIZATION` remains ungranted.

## Final Phase B hardening

- The runner uses one closed row-sidecar bijection followed by atomic validation
  and sealing; duplicate rows, duplicate sidecars and orphan sidecars fail
  before any dictionary index can hide them.
- Embedded JSON is strict and rejects duplicate keys, `NaN` and infinities.
- Sidecar, component and fixture-document schemas are closed to unexpected
  properties; synthetic/non-provider boundary flags are mandatory.
- Audit-lineage mappings and sequences are recursively immutable, with raw and
  parsed representations checked for equality before store insertion.
- Validation receipts bind dataset, provider authority, structural schema and
  the consumed sidecar hash; the store independently reconstructs physical
  fingerprint and candidate identity.
- All Market State artifacts serialize UTC timestamps with canonical `Z`.
- Governance validates one deterministic hash across policy, gate,
  traceability, package manifest and the canonical run.
