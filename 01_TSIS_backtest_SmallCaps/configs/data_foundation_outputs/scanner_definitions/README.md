# Scanner Definitions

This folder contains governed scanner-definition configs for
`daily_scanner_candidates_table_v0_1`.

These files are configs, not materialized datasets.

Authoritative contract:

```text
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
```

Active v0.1 definitions:

```text
trade_station_like_scanner_v0_1.yaml
broad_in_play_discovery_scanner_v0_1.yaml
```

Interpretation:

```text
trade_station_like_scanner_v0_1
  = operational visibility replay

broad_in_play_discovery_scanner_v0_1
  = broad research discovery to avoid late-arrival bias
```

Rules:

- Scanner definitions must be versioned.
- Builders must record the effective scanner config in the run manifest.
- No scanner config may contain labels, outcomes, rewards, fills, PnL or
  strategy decisions.
- A scanner candidate is not a market state.
- A strategy overlay such as DAS may consume candidates, but must keep its own
  experimental state table separate.
