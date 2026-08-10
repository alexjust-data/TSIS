# SEC PIT Fundamental Evidence Consumption Policy v0_1

## Allowed now

```text
one-ticker research pilot
source reconciliation
parser fixtures
coverage and storage measurement
daily O/S candidate resolution with restrictions
```

## Prohibited now

```text
float = O/S when ownership is missing
use of filing/report/measurement date as availability
retroactive rewrite from later anchors or amendments
weighted-average shares as point O/S
automatic Form 4 transaction-to-float deltas
institutional ownership subtraction from float
scanner or canonical market-state consumption
```

## Required gates

Consumers must inspect `gate_readout.json`. A downstream value is unavailable
unless every gate required by that value passes. In particular, float remains
`UNAVAILABLE` until ownership coverage, holder deduplication and methodology
gates pass.

