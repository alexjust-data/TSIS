# 01_MOMENTUM_EXPANSION

## Purpose

Capture events where demand, attention or forced participation creates rapid
price and volume expansion.

## Candidate Events

- `PM_Squeeze_Event`
- `Gap_And_Go_Event`
- `Opening_Drive_Event`
- `Parabolic_Expansion_Event`

## Inputs

- `master_daily_table`
- `master_intraday_table`
- `symbol_master`
- catalyst context when available

## Outputs

- observable event definitions;
- detector requirements;
- outcome questions for continuation, failure and exhaustion.

## No-goals

No entries, stops, targets or chase logic belong here.
