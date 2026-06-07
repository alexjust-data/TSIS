# Reference Artifacts

`reference_artifacts/` conserva artefactos locales de referencia que existian en `00_cto`.

## Estado

Esta carpeta no debe convertirse en data lake ni en source of truth operativo.

Los artefactos aqui son memoria local o material de transicion hasta que su significado quede formalizado en:

- `01_foundations/dataset_registry/`
- `01_foundations/canonical_schemas/`
- `01_foundations/contract_registry/`
- `01_foundations/data_consumption_policies/`

## Contenido actual

- `reference_listing_status.csv`
- `reference_listing_status.parquet`

## Regla

Si `reference_listing_status` sigue siendo relevante, debe decidirse si es:

- manifest ligero;
- snapshot historico;
- input de referencia;
- evidencia de una decision antigua;
- o payload que debe quedar fuera del repo.

Hasta entonces, no debe tratarse como autoridad activa.
