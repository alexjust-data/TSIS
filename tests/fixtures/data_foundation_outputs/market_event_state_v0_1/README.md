# Market / Event State Fixture v0.1

This fixture set is intentionally tiny and deterministic.

It exists to validate:

- legal component as-of composition;
- prohibited feature families;
- feature namespace rules;
- event-state label separation;
- non-official sample builders.

It does not represent the full TSIS universe.
It must not be promoted as market data.

Allowed use:

```text
contract tests
builder smoke tests
adversarial leakage tests
```

Forbidden use:

```text
research results
ML training
RL training
backtest evidence
official data foundation output
```
