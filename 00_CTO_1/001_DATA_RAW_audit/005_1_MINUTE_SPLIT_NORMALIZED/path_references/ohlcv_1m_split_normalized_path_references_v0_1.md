# OHLCV 1m Split-Normalized Path References

Este manifiesto documenta rutas operativas heredadas que aparecen en markdown auxiliares copiados dentro de `005_1_MINUTE_SPLIT_NORMALIZED`.

## example-ticker-a-2005-01

- Estado: `example_path_not_materialized_locally`
- Root piloto existente: `E:\TSIS\data\ohlcv_1m_split_normalized`
- Existe root piloto: `True`
- Root candidato full-universe existente: `E:\TSIS\data\ohlcv_1m_split_normalized_full_universe_candidate`
- Existe root candidato full-universe: `True`
- Relpath heredado no materializado: `ticker=A\year=2005\month=01\minute_aggs_A_2005_01_split_normalized.parquet`
- Fichero exacto existe localmente: `False`

Nota: esta referencia viene del contrato operativo como ejemplo de forma de path. No se crea un parquet falso; el estado correcto es que el root existe, pero ese ticker/month exacto no esta materializado localmente.
