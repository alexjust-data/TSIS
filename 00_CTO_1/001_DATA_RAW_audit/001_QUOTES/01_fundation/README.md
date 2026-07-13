# 001_QUOTES

Esta carpeta es una copia local navegable del dossier de auditoria `quotes`.

## Origen

Fuente canonica original:

`C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\quotes`

La copia se preparo en:

`C:\TSIS_Data\00_CTO_1\001_DATA_local_audit\001_QUOTES`

Fecha de reparacion de enlaces: 2026-07-11.

## Estructura local

- `quotes_inspection_readout_v0_1.md`: lectura institucional/cierre de la inspeccion `quotes`.
- `evidence/`: markdown de casos copiados previamente en esta carpeta:
  - `quotes_bad_cases_v0_1.md`
  - `quotes_good_cases_v0_1.md`
  - `quotes_review_cases_v0_1.md`
- `images/`: copia local de las imagenes referenciadas por los markdown. La estructura interna replica la ruta relativa dentro del dossier original.
- `referenced_docs/`: copia local de markdown auxiliares enlazados desde los readouts principales cuando no existian ya en `evidence/`.
- `path_references/`: manifiesto local para las referencias `file:` heredadas que apuntaban a raw daily quotes no disponibles en esta maquina.

## Reparacion aplicada

Los enlaces de imagen se reescribieron para apuntar a `images/` con rutas relativas desde cada markdown. Los enlaces a markdown auxiliares se reescribieron hacia copias locales en `referenced_docs/` o hacia los markdown ya existentes en `evidence/`.

Las rutas `file:` de los casepacks apuntaban al root historico de raw quotes diario. Ese root no esta disponible localmente, asi que se sustituyeron por enlaces al manifiesto local `path_references/quotes_raw_file_references_v0_1.md`. El manifiesto conserva el `relpath` historico y apunta, cuando existe, a la particion mensual fundacional disponible bajo:

`E:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded`

Esa particion mensual no es un sustituto identico del raw tape diario original; es el path fisico local existente para navegar al bloque fundacional disponible y filtrar por la fecha del caso.

## Fuente de verdad

Esta carpeta es una copia operativa para lectura y navegacion. La fuente institucional de verdad sigue siendo el dossier original bajo `01_foundations/inspection_dossiers/quotes`.
