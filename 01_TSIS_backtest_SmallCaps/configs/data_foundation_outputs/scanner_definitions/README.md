# Scanner Definitions

This folder contains governed scanner-definition configs for
`daily_scanner_candidates_table`.

These files are configs, not materialized datasets.

Authoritative contracts:

```text
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_2.md
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
```

Active v0.2 model:

```text
base_in_play_universe_scanner_v0_2.yaml
trade_station_like_profile_v0_2.yaml
relative_volume_profile_v0_2.yaml
percent_change_profile_v0_2.yaml
dollar_volume_tradability_profile_v0_2.yaml
das_research_profile_v0_2.yaml
```

Interpretation:

```text
base_in_play_universe_scanner_v0_2
  = common-stock smallcap <100M candidate denominator

profiles
  = operational/research/tradability selections inside the same denominator
```

Historical v0.1 definitions:

```text
trade_station_like_scanner_v0_1.yaml
broad_in_play_discovery_scanner_v0_1.yaml
```

Historical interpretation:

```text
trade_station_like_scanner_v0_1
  = operational visibility replay

broad_in_play_discovery_scanner_v0_1
  = broad research discovery to avoid late-arrival bias
```

v0.1 is preserved as controlled replay evidence. v0.2 is the forward
implementation path because it avoids treating operational visibility and
research discovery as separate universes.

Rules:

- Scanner definitions must be versioned.
- Builders must record the effective scanner config in the run manifest.
- No scanner config may contain labels, outcomes, rewards, fills, PnL or
  strategy decisions.
- A scanner candidate is not a market state.
- A strategy overlay such as DAS may consume candidates, but must keep its own
  experimental state table separate.
