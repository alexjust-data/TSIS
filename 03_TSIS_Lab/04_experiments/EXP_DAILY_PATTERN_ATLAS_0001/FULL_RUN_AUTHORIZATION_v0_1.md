# Full Run Authorization v0.1 — invalidada

Fecha original: 2026-08-24
Estado actual: `INVALIDATED_BY_POST_RUN_AUDIT`
Experimento: `EXP_DAILY_PATTERN_ATLAS_0001`

Esta autorización ya no es válida. El antiguo probe y el certificador
estructural omitieron controles que después detectaron:

- outcomes y picos contaminados por filas OHLCV inválidas;
- schema físico de volumen variable entre tickers;
- cohortes cooldown presentadas erróneamente como todas las activaciones;
- lineage incompleto y rutas raw legacy;
- `future_split_factor` dentro del output observable.

La ejecución `20260824_full_v0_1` está preservada bajo `runs/invalidated/` y no
puede alimentar la app, readouts oficiales o promoción. La evidencia completa
vive en `INCIDENT_REGISTER_v0_1.md`.

Cualquier nueva autorización deberá tener otra versión, ejecutar los ocho
probes production-equivalent con el código comprometido y demostrar PASS en los
controles heredados INC-003 a INC-007.
