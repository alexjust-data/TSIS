# 07_SHORT_SQUEEZE_DYNAMICS

## Purpose

Capture events where short pressure, forced covering or liquidity vacuum may
shape price behavior.

## Candidate Events

- `SSR_Triggered_Event`
- `Short_Squeeze_Event`
- `Forced_Covering_Event`
- `High_Short_Interest_Event`

## Inputs

- price and volume data;
- SSR and halt context when available;
- borrow or short-interest proxies when governed;
- float and liquidity context.

## Outputs

- squeeze-related event definitions;
- detector requirements;
- outcome questions about magnitude, continuation and failure.

## No-goals

This folder does not define squeeze trading strategies.
