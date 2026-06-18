# 05_RUNNER_LIFECYCLE

## Purpose

Capture lifecycle states of smallcap runners across sessions.

## Candidate Events

- `First_Green_Day_Event`
- `First_Red_Day_Event`
- `Runner_Continuation_Event`
- `Runner_Collapse_Event`
- `Multi_Day_Runner_Event`

## Inputs

- daily bars;
- intraday confirmation;
- corporate actions context;
- symbol history and calendar.

## Outputs

- lifecycle event definitions;
- state transition hypotheses;
- outcome questions by day number and lifecycle phase.

## No-goals

This folder does not define swing entries, overnight risk rules or portfolio
exposure.
