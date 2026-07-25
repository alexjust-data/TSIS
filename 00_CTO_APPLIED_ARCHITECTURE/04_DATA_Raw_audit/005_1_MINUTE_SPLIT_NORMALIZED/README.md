# 005_1_MINUTE_SPLIT_NORMALIZED

Esta carpeta es una copia local navegable del dossier de auditoria `1m_split_normalized`.

## Origen

Fuente canonica original:

`C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\inspection_dossiers\1m_split_normalized`

La copia se preparo en:

`C:\TSIS_Data\00_CTO_1\001_DATA_local_audit\005_1_MINUTE_SPLIT_NORMALIZED`

Fecha de reparacion de enlaces: 2026-07-11.

## Estructura local

- `ohlcv_1m_split_normalized_final_readout_v0_1.md`: lectura final del bloque split-normalized.
- `ohlcv_1m_split_normalized_visual_inspector_pack_v0_1.md`: pack visual de inspeccion.
- `images/`: copia local de las imagenes referenciadas por los markdown, incluidas imagenes necesarias para markdown auxiliares externos.
- `referenced_docs/`: copia local de markdown auxiliares enlazados desde los documentos principales.
- `path_references/`: manifiesto local para rutas operativas heredadas que no existen como fichero fisico en esta maquina.

## Reparacion aplicada

Los enlaces de imagen se reescribieron para apuntar a `images/` con rutas relativas desde cada markdown. Los enlaces a markdown auxiliares se reescribieron hacia copias locales en `referenced_docs/`.

Un markdown auxiliar copiaba una ruta de ejemplo bajo el root `E:\TSIS\data\ohlcv_1m_split_normalized` con relpath `ticker=A\year=2005\month=01\minute_aggs_A_2005_01_split_normalized.parquet`. Ese fichero exacto no esta materializado localmente, asi que se sustituyo por un enlace al manifiesto:

`path_references/ohlcv_1m_split_normalized_path_references_v0_1.md`

No se creo un parquet falso. El manifiesto conserva el relpath heredado y documenta los roots existentes.

## Fuente de verdad

Esta carpeta es una copia operativa para lectura y navegacion. La fuente institucional de verdad sigue siendo el dossier original bajo `01_foundations/inspection_dossiers/1m_split_normalized`.

