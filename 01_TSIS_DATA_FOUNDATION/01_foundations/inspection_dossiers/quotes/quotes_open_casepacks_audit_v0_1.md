# Quotes Open Casepacks Audit v0.1

## Rol

Este documento audita la trazabilidad completa de la bolsa abierta de `quotes`.
No valida una transformacion derivada como en `1m_split_normalized`.
Valida otra cosa: que los casos abiertos que llegan al inspector (`review` y `bad`) coinciden exactamente con el pool historico abierto y que sus assets existen realmente.

## Que se audita

- correspondencia exacta entre `build_quotes_case_pool()` y los manifests exportados;
- conteos esperados por scope (`64 review`, `15 bad`);
- coherencia entre manifest y markdown de cada dossier;
- y existencia fisica de los assets referenciados por cada caso.

## Resultado agregado

### Scope `review`

- `status`: `PASS`
- `expected_rows_from_pool`: `64`
- `expected_rows_contract`: `64`
- `manifest_rows`: `64`
- `doc_total_cases`: `64`
- `menu_entries`: `64`
- `missing_from_manifest`: `0`
- `extra_in_manifest`: `0`
- `menu_mismatch_vs_manifest`: `0`
- `manifest_rows_all_assets_present`: `64`
- `manifest_rows_with_missing_assets`: `0`

### Scope `bad`

- `status`: `PASS`
- `expected_rows_from_pool`: `15`
- `expected_rows_contract`: `15`
- `manifest_rows`: `15`
- `doc_total_cases`: `15`
- `menu_entries`: `15`
- `missing_from_manifest`: `0`
- `extra_in_manifest`: `0`
- `menu_mismatch_vs_manifest`: `0`
- `manifest_rows_all_assets_present`: `15`
- `manifest_rows_with_missing_assets`: `0`

## Lectura tecnica

Si ambos scopes pasan, la conclusion correcta es esta:

- la cola abierta de `quotes` no se construyo ad hoc;
- no faltan casos del pool historico abierto;
- no sobran casos inventados en los dossiers;
- y cada caso publicado por el inspector referencia assets realmente existentes.

Esto no equivale a una auditoria full-universe de transformacion semantica, porque `quotes` aqui no esta validando una vista derivada nueva como `1m_split_normalized`.
Pero si cierra la deuda institucional correcta para `quotes`: demostrar que la bolsa final `review/bad` es completa, trazable y reproducible.

## Veredicto

Si el resultado es `PASS` en `review` y `bad`, el inspector puede asumir que la frontera abierta final de `quotes` esta cerrada con integridad de coverage y de assets.
