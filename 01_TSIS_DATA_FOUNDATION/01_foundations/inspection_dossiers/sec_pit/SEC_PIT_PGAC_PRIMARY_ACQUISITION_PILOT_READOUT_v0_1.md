# SEC PIT PGAC Primary Acquisition Pilot Readout `v0_1`

Date: 2026-08-11

```text
run_id                    = sec_pit_pgac_primary_v0_2_20260811T1035Z
authorization_scope       = PGAC_ONLY
acquisition_gate          = PASS
payload_integrity_gate    = PASS
network_failures          = 0
http_429                  = 0
next_ticker_authorization = NOT_AUTHORIZED_PENDING_REVIEW
```

## Scope and lineage

The human authorized a bounded PGAC pilot using contact
`alexjustdata@gmail.com`. The authorization is bound to predownload probe
`sec_pit_predownload_7t_probe_v0_3` and exact selection SHA-256
`ddce5a64826268ceb4f36d34476eba03d879c9a47c6a94d634a7af74823bb998`.
No other ticker, CNOBP or parent-universe scale-out was authorized.

The executed runner and every imported acquisition/telemetry component are
fingerprinted in the final manifest. Content is stored by SHA-256 under the
versioned runtime root `C:/TSIS_Data/runtime/sec_pit_primary_v0_2`.

## Result

- Planned/fetched: `68/68` documents.
- Unique URLs, payload hashes and object paths: `68/68/68`.
- Actual uncompressed bytes: `26,958,608` versus a conservative
  `61,198,686`-byte upper bound.
- Independent post-run gzip decode, byte-count and SHA-256 verification:
  `68 PASS`, `0 FAIL`.
- Wall time: approximately `21.5 s`; terminal throughput `190.19 docs/min`.
- HTTP attempt p50/p95/p99: `131.4/242.7/262.9 ms`.
- Document p50/p95/p99: `315.7/426.8/440.4 ms`.
- Retries/HTTP 429/acquisition failures: `0/0/0`.

## Bottleneck finding

Measured time shares were `58.86%` throttle/retry wait, `37.80%` HTTP,
`3.05%` storage, `1.94%` SHA-256 plus gzip and `1.04%` atomic write. The
provisional bottleneck is therefore `SEC_RATE_LIMIT_OR_NETWORK`. C++ is not a
useful optimization target for primary acquisition based on this pilot.

The SEC process peaked near `0.131 GiB` RSS and `0.615 GiB` private memory.
System-level peaks include the concurrent Trading Activity run and must not be
attributed entirely to SEC. Trading Activity remained `RUNNING`, with its
supervisor and two adopted shards alive after PGAC completed.

## Artifact hashes

```text
authorization.json         285ad715a08fd5f3ac1a62ba235b714fe38b4d33a78a8ec8d9ac2c7ed76f9d9b
pre_manifest.json          361a0ebe3a26bdf29f977511ee7dbd103247d3d40c110af19db02afa9227287d
acquisition.jsonl          e64b85e702d03b24b671ead6c6f3bcd33553012fae381461603799d31346dea8
document_performance.jsonl 2752b4e6ecb218e6aadc1b5043437ce9253e650233890254bec290e0819c5e35
performance_summary.json   1231de6785227a47fc861df56ed2a58956ae34b2f6b81f24748736b0fc2a5837
final_manifest.json        cf398ad366edfbc99fbb54e7b6333d16a992ffb4ec1fcd764bb79e87d68ed7eb
```

## Promotion boundary

This is a primary-document acquisition and telemetry PASS only. It does not
certify parsing, lifecycle extraction, reconciliation, canonical promotion or
downloads for the remaining five eligible tickers. A terminal-heartbeat display
gap found by the monitor was corrected after this run for future executions;
the executed component hashes above preserve the exact PGAC implementation.

