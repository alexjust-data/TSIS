# SEC PIT Predownload Control Seven-Case Readout `v0_1`

Date: 2026-08-11

```text
implementation_policy     = sec_pit_predownload_control_v0_2
probe_run                  = sec_pit_predownload_7t_probe_v0_3
network_access             = PROHIBITED_AND_NOT_USED
probe_gate                 = PASS
download_authorization     = NOT_AUTHORIZED_PENDING_HUMAN_GATE
parent_universe_scale      = NOT_AUTHORIZED
```

## Result

The offline probe reused the seven existing SEC metadata inventories and the
existing lifecycle reconciliation. It made no SEC request and downloaded no
primary document. Its final manifest binds the exact script, config, universe,
instrument master, lifecycle ledger, seven inventories, filtered snapshot
content and every emitted output by SHA-256.

| Ticker | Inventory | Selected candidates | Class gate | Acquisition state |
|---|---:|---:|---|---|
| ALUR | 314 | 224 | PASS | eligible for governed review |
| BBBY | 2,265 | 1,798 | PASS | eligible; ticker-reuse restrictions remain |
| BGM | 150 | 104 | PASS | eligible for governed review |
| BNAI | 349 | 249 | PASS | eligible for governed review |
| CNOBP | 1,918 | 1,573 diagnostic candidates | FAIL | halted before acquisition |
| DOMH | 1,288 | 911 | PASS | eligible for governed review |
| PGAC | 87 | 68 | PASS | eligible for governed review |

The technical plan contains 4,927 role candidates including the halted negative
control. The executable eligible subset contains 3,354 documents across six
tickers with a conservative SEC filing-size ceiling of 3,075,265,452 bytes.
That size is planning evidence, not response-byte fact.

## Interval finding

The ledger now preserves separately:

- LT1B operational PTI window;
- target identity snapshot interval;
- instrument-master validity projection;
- market first/last daily presence;
- SEC legal dates when admitted;
- SEC exchange-end candidates when only provisional.

No legal SEC listing or delisting date was admitted in the existing six-case
reconciliation. ALUR has an exchange-end candidate, not a legal delisting.
BBBY remains `TICKER_REUSE_CONFLICT`. These states are visible rather than
silently replaced with Massive/Polygon dates.

## Operational closure

The legacy seven-ticker coordinator now refuses broad primary acquisition.
The replacement runner:

- consumes the exact v0.2 selection parquet;
- excludes class halts;
- requires a separate hash-bound authorization;
- rate-limits sequentially;
- writes pre/PID/heartbeat/final manifests;
- stores content by SHA-256;
- resumes after interruption by skipping already fetched URLs.

Before any authorized network run, the runner now also exposes a dedicated live
monitor and persists low-overhead resource telemetry plus per-document stage
timings. This allows the first bounded acquisition probe to distinguish SEC
throttling/network latency from hashing/compression CPU or storage I/O before
considering native optimization. The current offline probe was not rerun and no
performance conclusion is claimed because no SEC request was made.

No authorization file with `status=AUTHORIZED` was created in this work.
