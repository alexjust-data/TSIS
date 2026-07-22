# Reference Dividends Schema Contract - Modulo 01

## 1. Rol

Este documento define el schema logico canonico para `reference/dividends`.

La capa representa eventos de dividendos por ticker, descargados desde la fuente de referencia.

Es una fuente primaria para construir vistas economicas como `daily_adjusted`, pero no decide por si sola la continuidad total de precio ni todos los corporate actions complejos.

## 2. Unidad logica

La unidad logica canonica es:

- `ticker-dividend event`

Cada fila con payload representa un evento de dividendo asociado a un ticker.

## 3. Layout fisico observado

Ejemplo con payload real:

- `D:\reference\dividends\ticker=MSFT\dividends_MSFT.parquet`

Columnas fisicas observadas con payload:

- `cash_amount`
- `currency`
- `dividend_type`
- `ex_dividend_date`
- `frequency`
- `id`
- `pay_date`
- `record_date`
- `ticker`
- `declaration_date`
- `_dataset`
- `_ingested_utc`

Ejemplo sin payload:

- `D:\reference\dividends\ticker=AA\dividends_AA.parquet`

Columnas fisicas observadas sin eventos:

- `ticker`
- `_dataset`
- `_ingested_utc`

## 4. Claves logicas

Claves recomendadas para filas con payload:

- `ticker`
- `id`

Claves alternativas cuando `id` no sea suficiente:

- `ticker`
- `ex_dividend_date`
- `cash_amount`
- `dividend_type`

## 5. Campos requeridos

Campos requeridos para cualquier file:

- `ticker`
- `_dataset`
- `_ingested_utc`

Campos requeridos para filas con payload:

- `cash_amount`
- `currency`
- `dividend_type`
- `ex_dividend_date`
- `frequency`
- `id`
- `pay_date`
- `record_date`

Campos opcionales:

- `declaration_date`

## 6. Tipos semanticos esperados

- `ticker`: string no vacio
- `cash_amount`: numerico no negativo
- `currency`: string, normalmente `USD`
- `dividend_type`: string
- `ex_dividend_date`: fecha parseable
- `frequency`: entero o numerico
- `id`: string identificador del evento
- `pay_date`: fecha parseable o nula
- `record_date`: fecha parseable o nula
- `declaration_date`: fecha parseable o nula
- `_dataset`: string, debe ser `dividends`
- `_ingested_utc`: timestamp parseable

## 7. Reglas estructurales minimas

- Todo file debe conservar `ticker`, `_dataset` e `_ingested_utc`.
- En files con payload, `ex_dividend_date` debe ser parseable.
- En files con payload, `cash_amount` no debe ser negativo.
- En files con payload, `ticker + id` no deberia duplicarse salvo limitacion documentada.
- Un file con solo `ticker`, `_dataset`, `_ingested_utc` debe leerse como `no payload observed`, no como schema roto.

## 8. Reglas de interpretacion

`dividend_type = CD` representa el caso dominante de cash dividend ordinario observado en la auditoria.

Tipos no `CD`, como `SC`, deben tratarse como frontera semantica documentada:

- pueden tener `cash_amount`;
- pueden ser consumibles por la mecanica actual si la policy lo permite;
- pero no deben confundirse automaticamente con todo el universo de spin-offs, stock dividends o reorganizaciones complejas.

## 9. Relacion con price views

Esta capa alimenta:

- `daily_adjusted`
- `adjusted_proxy`
- auditorias de corporate actions

No debe usarse para:

- ejecucion intradia;
- microestructura;
- verdad raw del libro o tape.

## 10. Conclusion operacional

`reference/dividends` queda definido como fuente de eventos de dividendos por ticker, con dos formas fisicas validas:

- payload real de eventos;
- file sin eventos con metadata minima.
