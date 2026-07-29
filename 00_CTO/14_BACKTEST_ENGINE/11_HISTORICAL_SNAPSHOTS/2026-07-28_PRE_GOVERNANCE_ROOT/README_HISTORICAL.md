# TSIS Backtest Engine

Status: LIVE_WORKSPACE
Started: 2026-07-28

This workspace is for building a serious Python backtest engine for TSIS small caps.

The operating rule is simple:

```text
backtester first
guide as living engineering record
no closed book before the first working vertical slice
```

## Current Entry Points

- `AGENT.md`: operational handoff for agents, current state and next steps.
- `00_CTO/00_como_trabajamos.md`: working method.
- `00_CTO/99_NOTAS_BRUTO_gpt/00_BACKTEST_ENGINE_ARCHITECTURE_V0_1.md`: raw architecture draft.
- `00_CTO/00_SERSANS_SISTEMAS/README.md`: Sersan source package orientation.
- `01_GUIDE/README.md`: living guide by infrastructure layer.
- `01_GUIDE/01_DATA.md`: first layer, data and universe contract.

## Work Style

Each layer is written only as far as needed to support implementation.

For every layer:

```text
read local TSIS contracts
read Sersan evidence
read processed book notes
make a minimal TSIS decision
define contracts and gates
implement or prepare the next coding step
record the result
update AGENT.md, CHANGELOG.md and the affected guide layer
```

The guide does not replace tests, manifests or code. It explains why the tested contracts exist.

## Implementation Root

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE
```

This is now the clean executable root for code, tests, configs, runs and engine outputs.
