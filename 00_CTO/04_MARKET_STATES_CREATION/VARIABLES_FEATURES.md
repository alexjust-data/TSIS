# Variables / Features

Este archivo es un indice. La documentacion gobernada de implementacion fisica
experimental vive en [`VARIABLES_FEATURES/`](VARIABLES_FEATURES/).

Cadena de trabajo:

```text
Information Object
-> Representation Model Candidate
-> Experimental Physical Binding
-> source and temporal hard gates
-> deterministic pilot
-> stratified and OOS comparison
-> admission decision
-> canonical physical implementation, only if authorized
```

Estado actual:

```text
Information Object
= Trading Activity

Representation Model Candidate
= ABSOLUTE-AND-PIT-RELATIVE
  MULTISCALE MARKED ACTIVITY PROCESS

Physical Binding
= Binding A specified and implemented for deterministic pilot

Multisession run plan
= COMPLETE

Runner, config and monitor
= IMPLEMENTED_AND_TESTED

Prelaunch test gate
= PASS

Full 130-session run
= COMPLETE

Independent post-run validation
= PASS

Full legacy source gate
= PASS_WITH_RESTRICTIONS

Stratified development design
= PREREGISTERED_WITH_BLOCKING_SOURCE_GATE

Population-target PIT selector gate
= PENDING

Stratified development execution
= BLOCKED_PENDING_PIT_SELECTOR_AND_SAMPLE_MANIFEST

OOS comparison
= NOT_AUTHORIZED

Canonical features
= NOT_AUTHORIZED
```

Lectura minima:

1. [`CURRENT_STATUS_AND_HANDOFF_v0_8.md`](CURRENT_STATUS_AND_HANDOFF_v0_8.md)
2. [`TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_3.md`](TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_3.md)
3. [`TRADING_ACTIVITY_CONTRACT_RECTIFICATION_AND_ALIGNMENT_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_CONTRACT_RECTIFICATION_AND_ALIGNMENT_v0_1.md)
4. [`TRADING_ACTIVITY_SOURCE_QUALITY_LABEL_CONSUMPTION_POLICY_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_SOURCE_QUALITY_LABEL_CONSUMPTION_POLICY_v0_1.md)
5. [`TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_5.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_5.md)
6. [`TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md)
7. [`TRADING_ACTIVITY_BINDING_A_IMPLEMENTATION_READOUT_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_IMPLEMENTATION_READOUT_v0_1.md)
8. [`TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_RUN_PLAN_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_RUN_PLAN_v0_1.md)
9. [`TRADING_ACTIVITY_BINDING_A_MULTISESSION_RUNNER_IMPLEMENTATION_READOUT_v0_2.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_MULTISESSION_RUNNER_IMPLEMENTATION_READOUT_v0_2.md)
10. [`TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_EXECUTION_READOUT_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_EXECUTION_READOUT_v0_1.md)
11. [`TRADING_ACTIVITY_STRATIFIED_DEVELOPMENT_SAMPLE_PLAN_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_STRATIFIED_DEVELOPMENT_SAMPLE_PLAN_v0_1.md)
12. [`POPULATION_TARGET_PIT_RECOVERY_AND_GOVERNANCE_PLAN_v0_1.md`](VARIABLES_FEATURES/POPULATION_TARGET_PIT_RECOVERY_AND_GOVERNANCE_PLAN_v0_1.md)
13. [`FLOAT_CONTEXT_SOURCE_AUDIT_PLAN_v0_1.md`](VARIABLES_FEATURES/FLOAT_CONTEXT_SOURCE_AUDIT_PLAN_v0_1.md)
14. [`TRADING_ACTIVITY_PARALLEL_WORKSTREAM_COORDINATION_v0_1.md`](TRADING_ACTIVITY_PARALLEL_WORKSTREAM_COORDINATION_v0_1.md)

Las variables de Binding A son bindings experimentales. No son todavia:

```text
features canonicas
predicados obligatorios del detector
Wake-up Event
signal
entry eligibility
outcomes
```

El siguiente trabajo es ejecutar el inventario de recuperacion y la auditoria
del selector PIT gobernados por:

```text
POPULATION_TARGET_PIT_RECOVERY_AND_GOVERNANCE_PLAN_v0_1.md
```

En paralelo pueden avanzar el sample-manifest schema, runner por
instrument-block, lockbox guards y auditoria de float. No materializar TA-3
hasta congelar y hashear el sample manifest.
