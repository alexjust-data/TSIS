# 02_VWAP_CONTROL

## Purpose

Capture events where control around VWAP changes, holds or fails.

## Candidate Events

- `VWAP_Bounce_Event`
- `VWAP_Reclaim_Event`
- `VWAP_Loss_Event`
- `VWAP_Rejection_Event`

## Inputs

- intraday bars;
- VWAP calculation policy;
- session calendar;
- liquidity and spread context.

## Outputs

- VWAP control event definitions;
- required features for event detection;
- outcome questions about continuation, rejection and failure.

## No-goals

This folder does not define how to trade a VWAP reclaim or rejection.
