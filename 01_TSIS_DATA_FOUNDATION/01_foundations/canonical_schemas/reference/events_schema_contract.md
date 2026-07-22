# Reference Events Schema Contract - Modulo 01

## 1. Rol

Este documento define el schema logico canonico para `reference/events`.

La capa representa eventos corporativos de identidad y continuidad disponibles en la fuente de referencia.

En el estado observado, la familia material dominante es `ticker_change`.

## 2. Unidad logica

La unidad logica canonica del file es:

- `ticker-events payload`

Dentro de cada fila, el campo `events` contiene una lista de eventos estructurados.

La unidad semantica interna es:

- `ticker-corporate event`

## 3. Layout fisico observado

Ejemplo inspeccionado:

- `D:\reference\events\ticker=AA\events_AA.parquet`

Columnas fisicas observadas:

- `name`
- `composite_figi`
- `cik`
- `events`
- `ticker`
- `_dataset`
- `_ingested_utc`

Schema anidado observado para `events`:

- `events`: list of struct
  - `date`: string
  - `ticker_change`: struct
    - `ticker`: string
  - `type`: string

## 4. Claves logicas

Clave del payload:

- `ticker`

Clave recomendada del evento interno:

- `ticker`
- `events.date`
- `events.type`
- `events.ticker_change.ticker`

## 5. Campos requeridos

Campos requeridos:

- `ticker`
- `events`
- `_dataset`
- `_ingested_utc`

Campos identificadores recomendados:

- `name`
- `composite_figi`
- `cik`

Campos requeridos dentro de cada evento:

- `date`
- `type`

Campos requeridos para `type = ticker_change`:

- `ticker_change.ticker`

## 6. Tipos semanticos esperados

- `ticker`: string
- `name`: string o nulo
- `composite_figi`: string o nulo
- `cik`: string o nulo
- `events`: lista de structs
- `events.date`: fecha parseable
- `events.type`: string
- `events.ticker_change.ticker`: string cuando aplique
- `_dataset`: string, debe ser `events`
- `_ingested_utc`: timestamp parseable

## 7. Reglas estructurales minimas

- `ticker` no debe ser nulo.
- `_dataset` debe ser `events`.
- `_ingested_utc` debe ser parseable.
- `events` puede contener cero, uno o multiples eventos segun fuente.
- Todo evento con `type = ticker_change` debe tener `ticker_change.ticker`.
- La fecha del evento debe ser parseable cuando exista.

## 8. Reglas de interpretacion

Un `ticker_change` no define por si solo:

- continuidad economica completa;
- factor de ajuste;
- ni identidad corporativa final.

Debe leerse como evento de referencia que exige una policy de continuidad/remap antes de promoverlo a consumo economico.

## 9. Relacion con daily_adjusted

La auditoria de cola compleja de `daily_adjusted` mostro que la deuda estructurada visible principal en esta familia es `ticker_change`.

Por tanto, `reference/events` es fuente relevante para continuidad corporativa, pero no queda automaticamente consumida por `daily_adjusted`.

## 10. Conclusion operacional

`reference/events` queda definido como payload anidado de eventos corporativos por ticker.

Su uso requiere expandir el array `events` antes de aplicar reglas file-level o event-level.
