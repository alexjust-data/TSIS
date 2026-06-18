# 03_INTRADAY_REVERSALS

## Purpose

Capture events where intraday control changes direction.

## Candidate Events

- `Red_To_Green_Event`
- `Green_To_Red_Event`
- `Gap_And_Crap_Reversal_Event`

## Inputs

- intraday bars;
- previous close and open state;
- session calendar;
- volume and liquidity context.

## Outputs

- reversal event definitions;
- detector requirements;
- outcome questions about persistence and failure.

## No-goals

No long/short trigger rules belong here.
