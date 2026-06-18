# 09_DECISION_MODELS

Estado: design surface.

## Purpose

Convert probabilities, risk state and execution constraints into action policy.

## Inputs

- ML predictions;
- event and outcome context;
- execution constraints;
- risk and portfolio state;
- abstention rules.

## Outputs

- action policy;
- abstention policy;
- sizing policy;
- risk gates;
- decision audit requirements.

## No-goals

ML models do not decide trades directly. Decision Models consume predictions
and constraints.
