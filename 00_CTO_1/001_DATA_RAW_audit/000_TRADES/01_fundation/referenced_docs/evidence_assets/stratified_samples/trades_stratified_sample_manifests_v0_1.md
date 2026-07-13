# Trades Stratified Sample Manifests v0.1

## Rol

Este documento resume la primera materializacion de muestras estratificadas por familia sobre el cache final `57f/full_clean_fast_same_schema`.

No son ejemplos elegidos a dedo. Son manifests reproducibles para export y lectura del inspector.

## Conteos por familia

| familia | universo | target | seleccionado |
|---|---:|---:|---:|
| `review` | 4851211 | 60 | 60 |
| `reference_scale_mismatch` | 2418062 | 60 | 60 |
| `review_microstructure` | 2130781 | 60 | 60 |
| `bad_data` | 15869 | 60 | 60 |
| `review_no_1m_reference` | 8091 | 60 | 60 |
| `review_1m_reference_alignment` | 4992 | 60 | 60 |
| `good` | 106 | 106 | 106 |

## Artefactos

- manifests `.parquet` y `.csv` por familia en `evidence_assets/stratified_samples/`
- resumen de cuotas por estrato en `stratified_sample_summary.csv`

## Nota metodologica

- `good` se enumera completo mientras siga siendo pequeno.
- `review_no_1m_reference` y `review_1m_reference_alignment` ya no se tratan como buckets diminutos del historico; en el cierre real tienen masa suficiente para muestreo estratificado fuerte.