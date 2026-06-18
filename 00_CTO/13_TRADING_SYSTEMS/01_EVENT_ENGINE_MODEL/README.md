# 01_EVENT_ENGINE_MODEL

Estado: design surface.

## Purpose

Define the conceptual Event Engine that converts audited market data and event
definitions into a reproducible `event_table`.

## Inputs

- `master_daily_table`
- `master_intraday_table`
- `symbol_master`
- `corporate_actions_table`
- `calendar_table`
- `00_EVENT_LIBRARY/`

## Outputs

- `event_table` schema proposal;
- detector design notes;
- event versioning rules;
- required lineage fields;
- reproducibility requirements.

## No-goals

This folder does not implement production pipelines. Operational code belongs
in the relevant module after contracts are promoted.
