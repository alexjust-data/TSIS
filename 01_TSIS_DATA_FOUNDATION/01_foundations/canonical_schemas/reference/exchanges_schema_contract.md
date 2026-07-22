# Reference Exchanges Schema Contract - Modulo 01

## 1. Rol

Este documento define el schema logico canonico para `reference/exchanges`.

La capa representa la tabla de exchanges, TRFs, SIPs u otros venues de referencia.

## 2. Unidad logica

La unidad logica canonica es:

- `exchange-reference row`

Cada fila describe un venue o entidad de mercado identificable.

## 3. Layout fisico observado

Ejemplo inspeccionado:

- `D:\reference\exchanges\exchanges.parquet`

Columnas fisicas observadas:

- `id`
- `type`
- `asset_class`
- `locale`
- `name`
- `acronym`
- `mic`
- `operating_mic`
- `participant_id`
- `url`
- `_dataset`
- `_ingested_utc`

Resultado observado:

- `rows = 26`

## 4. Claves logicas

Clave primaria recomendada:

- `id`

Claves auxiliares:

- `mic`
- `participant_id`
- `operating_mic`

## 5. Campos requeridos

Campos requeridos:

- `id`
- `type`
- `asset_class`
- `locale`
- `name`
- `_dataset`
- `_ingested_utc`

Campos recomendados cuando existan:

- `acronym`
- `mic`
- `operating_mic`
- `participant_id`
- `url`

## 6. Tipos semanticos esperados

- `id`: entero
- `type`: string
- `asset_class`: string
- `locale`: string
- `name`: string
- `acronym`: string o nulo
- `mic`: string o nulo
- `operating_mic`: string o nulo
- `participant_id`: string o nulo
- `url`: string o nulo
- `_dataset`: string, debe ser `exchanges`
- `_ingested_utc`: timestamp parseable

## 7. Reglas estructurales minimas

- `id` no debe ser nulo.
- `name` no debe ser nulo.
- `_dataset` debe ser `exchanges`.
- `_ingested_utc` debe ser parseable.
- `id` no deberia duplicarse salvo limitacion documentada.

## 8. Reglas de interpretacion

Esta capa sirve para mapear codigos de venue y participantes.

No define por si sola:

- calidad de quotes;
- calidad de trades;
- ni sesion de mercado.

Debe combinarse con `market_session_scope.md` y validators de `quotes` o `trades` cuando se use para auditoria microestructural.

## 9. Conclusion operacional

`reference/exchanges` queda definido como tabla canonica de venues de referencia para enriquecer y explicar datos intradia.
