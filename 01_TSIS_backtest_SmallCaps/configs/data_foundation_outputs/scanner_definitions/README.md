# Scanner Definitions

This folder contains governed scanner-definition configs for scanner candidate
tables.

These files are configs, not materialized datasets.

Authoritative contracts:

```text
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_3.md
01_foundations/module_contracts/outputs/intraday_scanner_framework_and_definitions_contract_v0_1.md
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_2.md
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
```

Active intraday v0.1 model:

```text
base_eligible_smallcap_denominator_v0_3.yaml
intraday_in_play_momentum_candidate_denominator_v0_1.yaml
```

Interpretation:

```text
base_eligible_smallcap_denominator_v0_3
  = who TSIS may inspect

intraday_in_play_momentum_candidate_denominator_v0_1
  = first 1m +50% cross in extended hours + tradability gate at first cross
```

Use this model for intraday strategy denominators, DAS/frontside research and
future market/event state candidate seeding. It detects premarket, regular and
afterhours first-cross timing from `ohlcv_1m`.

Active daily/coarse v0.3 model:

```text
base_eligible_smallcap_denominator_v0_3.yaml
in_play_momentum_candidate_denominator_v0_3.yaml
trade_station_like_profile_v0_3.yaml
```

Interpretation:

```text
base_eligible_smallcap_denominator_v0_3
  = who TSIS may inspect

in_play_momentum_candidate_denominator_v0_3
  = base + movement >= 50% + minimum volume/tradability

trade_station_like_profile_v0_3
  = operator visibility replay, not the in-play denominator
```

`v0.3` is the daily/EOD proxy path for scanner candidate semantics. It is not
the official detector of first intraday push timing.

Historical v0.2 model:

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
  = stable identifier for the common-stock smallcap <100M eligible denominator

profiles
  = parallel operational/research/tradability flags and ranks inside the same
    denominator
```

The precise meaning of the base is:

```text
base_eligible_smallcap_denominator
```

It is not a proof that every row is already in-play. It is the set of rows that
TSIS is allowed to observe before applying generic observation profiles or
strategy overlays.

Profile counts are not a sequential funnel. A 100-row denominator with 80
percent-change rows, 79 volume-acceleration rows and 40 dollar-volume rows means
parallel profile membership over the same 100 rows.

Current v0.2 caution:

- `relative_volume_profile_v0_2` must be interpreted as provisional until it is
  built from intraday/as-of recent-bar acceleration or marked unavailable.
- `percent_change_profile_v0_2` must require a declared minimum percent move
  before top-N ranking.
- `dollar_volume_tradability_profile_v0_2` is tradability, not alpha.
- `das_research_profile_v0_2` is provisional strategy-overlay lineage, not a
  final DAS scanner.

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

v0.1 is preserved as controlled replay evidence. v0.2 is implementation
evidence that exposed the need to separate base eligible from in-play momentum.
v0.3 supersedes it for daily/coarse materializations. Intraday v0.1 supersedes
daily proxies when first-push timestamp/segment matters.

Rules:

- Scanner definitions must be versioned.
- Builders must record the effective scanner config in the run manifest.
- No scanner config may contain labels, outcomes, rewards, fills, PnL or
  strategy decisions.
- A scanner candidate is not a market state.
- A strategy overlay such as DAS may consume candidates, but must keep its own
  experimental state table separate.
