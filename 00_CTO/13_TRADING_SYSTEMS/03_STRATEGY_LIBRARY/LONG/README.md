# LONG

## Purpose

Contain long-side strategy concepts after they are separated from event
definitions.

## Inputs

- Event Library;
- Outcome Research;
- Edge Hypotheses;
- Execution Models.

## Outputs

- long-side strategy definitions;
- variants;
- execution assumptions;
- failure modes.

## Current Children

- `DAS/`
- `Breakout/`
- `gap&go/`

## Current Research Sequence

The current long-side pilot sequence is:

```text
1. gap&go
2. DAS
3. Breakout
```

Each strategy folder should first define the human strategy in `STRATEGY.md`,
then create or reuse notebooks to collect samples, and only after that split
the strategy into Event Library v0 event files.

## No-goals

This folder does not define events or data contracts.
