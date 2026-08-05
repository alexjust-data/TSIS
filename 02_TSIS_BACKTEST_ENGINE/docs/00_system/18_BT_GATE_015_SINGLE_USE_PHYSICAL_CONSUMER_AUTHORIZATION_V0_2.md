# BT-GATE-015 Single-Use Physical Consumer Authorization Candidate

VERSION = `V0_2`
GATE = `BT-GATE-015`
STATUS = `DRAFT_NOT_AUTHORIZED_PENDING_PREEXECUTION_REVIEW`
EXECUTION_AUTHORIZED = `false`
CONSUMED_BY_RUN_ID = `null`

This is a prepared candidate, not executable authority. It may be used as
input to the next implementation and pre-execution review cycle only.

## Frozen Candidate Scope

```text
event_type = event_type:market_data:session_opened
instrument = AAME
exchange = XNYS
session = 2021-01-19
maximum physical files = 1
maximum physical rows = 1
candidate file sha256 = ed975ad7d7a3e0ac68bd7dfe2c91743c86931a545162a4440d270cbb689477dd
record id = e71cad82e71783bbc50ebb8df1e44e2f9118dd4843c3cb4f0fbf2ee5a2a8ca76
record fingerprint = 31f1463baf0dc8f0dba3bc130c0bb1d61092897595849df57abc6b1023853a01
initial provider handoff = b7a4783d0ab64ffaf37fbfdf2ee76dffacbe9b14cf3f059891908c87116369b2
provider completion handoff = 3a6bf3ca04c0428a1728e1719cd6aeaea6bfaef43e12fb83939dde3cb6cb85d9
```

## Missing Authority

```text
physical runner binding = NOT_IMPLEMENTED_OR_ACCEPTED
pre-execution package = NOT_PRODUCED
pre-execution external review = NOT_EXECUTED
physical command = NOT_AUTHORIZED
physical consumer read = NOT_EXECUTED
physical state rows read = 0
```

No physical command may consume this candidate until all missing authority is
implemented, packaged and independently accepted.
