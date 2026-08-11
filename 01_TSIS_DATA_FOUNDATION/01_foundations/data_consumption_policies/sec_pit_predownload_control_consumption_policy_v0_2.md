# SEC PIT Predownload Control Consumption Policy `v0_2`

Status: `ACTIVE_BLOCKING_POLICY`

Consumers may use these outputs for acquisition planning, identity review,
capacity estimation and authorization review. They may not use them as final
shares outstanding, float, freely tradable supply, institutional ownership,
legal listing/delisting truth or canonical lifecycle truth.

A primary-document run is permitted only when all of the following hold:

- parent membership comes from `lt1b_universe_v0_1`;
- instrument identity comes from `instrument_master_v0_1` plus interval evidence;
- security-class gate passes;
- selection gate passes without required-evidence truncation;
- the exact manifest and parquet hashes are separately authorized;
- free space is at least 100 GiB;
- the run uses PID, heartbeat, live log, atomic manifests and resume checkpoints.

`CNOBP` remains excluded while its common-stock flag conflicts with its
depositary/preferred security name. `BBBY` remains a ticker-reuse review case;
its issuer prehistory must not be represented as target-instrument history.

G8 remains a tradability estimate with explicit unavailable/degraded states;
registration effectiveness alone is insufficient. G12 remains a separate,
global 13F information-table acquisition keyed through historical CUSIP.
