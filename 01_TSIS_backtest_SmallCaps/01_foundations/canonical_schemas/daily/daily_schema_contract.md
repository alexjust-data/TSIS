# Daily Schema Contract - Modulo 01

## 1. Rol

Este documento define el schema logico canonico para `daily_core_v0_1`.

Su objetivo es fijar la unidad semantica minima del dataset `daily` sin depender de detalles accidentales de file layout legacy.

## 2. Unidad logica

La unidad logica canonica es:

- `ticker-day bar`

Cada fila representa una barra diaria para un instrumento y una fecha de sesion.

## 3. Claves logicas

Claves minimas:

- `ticker`
- `session_date`

Notas:

- `ticker` puede venir como columna o derivarse de metadata/particion/file identity;
- `year` puede vivir como particion, metadata o derivarse desde `session_date`.

## 4. Campos requeridos

Campos requeridos del schema logico:

- `ticker`
- `session_date`
- `open`
- `high`
- `low`
- `close`
- `volume`

## 5. Campos condicionales relevantes

Campos relevantes cuando existan:

- `vw`
- `n`

Interpretacion:

- `vw` = precio medio ponderado relevante para el bar cuando la fuente lo provee;
- `n` = medida de conteo o actividad asociada al bar cuando la fuente lo provee.

## 6. Tipos semanticos esperados

- `ticker`: identificador simbolico de instrumento
- `session_date`: fecha de sesion diaria
- `open`, `high`, `low`, `close`: numericos positivos o validamente parseables
- `volume`: numerico no negativo
- `vw`: numerico o nulo segun la fuente y el caso
- `n`: numerico entero o equivalente cuando aplique

## 7. Reglas estructurales minimas

Las siguientes reglas forman parte del schema operativo:

- `session_date` debe ser parseable y coherente con una sesion diaria;
- `high` no debe ser menor que `open`, `low` o `close` en filas validas;
- `low` no debe ser mayor que `open`, `high` o `close` en filas validas;
- `open`, `high`, `low`, `close` no deben ser cero o negativos en filas validas;
- `volume` no debe ser negativo;
- `vw`, cuando exista, no debe evaluarse de forma binaria ingenua fuera de su policy de calidad.

## 8. Reglas de interpretacion

Este schema no declara que cualquier desviacion de `vw` implique corrupcion dura.

La interpretacion correcta de `vw` depende de:

- la quality policy de `daily`;
- el regimen de iliquidez;
- y los validators especificos del bloque.

## 9. Exclusiones duras

Las filas o archivos que caigan en:

- `all_rows_invalid_after_parse`
- `negative_or_zero_ohlc_rows`
- `hard_invalid_parse_or_price`

quedan fuera del dataset consumible principal aunque el schema logico general siga siendo el mismo.

## 10. Relacion con el dataset contract

Este schema sirve a:

- `01_foundations/contract_registry/dataset_contracts/daily_dataset_contract_v0_1.md`

No redefine su policy.

Define la estructura logica minima que el dataset debe satisfacer.
