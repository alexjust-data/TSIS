# Reference Overview Schema Contract - Modulo 01

## 1. Rol

Este documento define el schema logico canonico para `reference/overview`.

La capa representa un snapshot de metadatos fundamentales y descriptivos de un ticker en una fecha de solicitud.

## 2. Unidad logica

La unidad logica canonica es:

- `ticker-overview snapshot`

Cada file observado contiene normalmente una fila para un ticker y una `request_date`.

## 3. Layout fisico observado

Ejemplos inspeccionados:

- `D:\reference\overview\ticker=AA\overview_AA_2016-10-31.parquet`
- `D:\reference\overview\ticker=IBM\overview_IBM_2026-03-09.parquet`
- `D:\reference\overview\ticker=AMC\overview_AMC_2008-11-10.parquet`

El schema fisico de `overview` es variable por fecha y disponibilidad de fuente.

Columnas base observadas:

- `ticker`
- `name`
- `market`
- `locale`
- `primary_exchange`
- `type`
- `active`
- `currency_name`
- `cik`
- `market_cap`
- `phone_number`
- `sic_code`
- `sic_description`
- `ticker_root`
- `list_date`
- `share_class_shares_outstanding`
- `weighted_shares_outstanding`
- `round_lot`
- `address.address1`
- `address.city`
- `address.state`
- `address.postal_code`
- `request_date`
- `_dataset`
- `_ingested_utc`

Columnas adicionales observadas en snapshots mas ricos:

- `composite_figi`
- `share_class_figi`
- `description`
- `homepage_url`
- `total_employees`
- `address.address2`
- `branding.logo_url`
- `branding.icon_url`

## 4. Claves logicas

Claves minimas:

- `ticker`
- `request_date`

Notas:

- `request_date` puede venir en el nombre fisico del file y como columna;
- `ticker` es simbolo de trading, no identidad corporativa final.

## 5. Campos requeridos

Campos requeridos:

- `ticker`
- `name`
- `market`
- `locale`
- `primary_exchange`
- `type`
- `active`
- `currency_name`
- `request_date`
- `_dataset`
- `_ingested_utc`

Campos altamente recomendados cuando existan:

- `cik`
- `composite_figi`
- `share_class_figi`
- `market_cap`
- `ticker_root`
- `list_date`
- `share_class_shares_outstanding`
- `weighted_shares_outstanding`
- `round_lot`

Campos descriptivos opcionales:

- `phone_number`
- `description`
- `sic_code`
- `sic_description`
- `homepage_url`
- `total_employees`
- `address.*`
- `branding.*`

## 6. Tipos semanticos esperados

- `ticker`: string no vacio
- `name`: string
- `market`: string
- `locale`: string
- `primary_exchange`: string
- `type`: string
- `active`: booleano
- `currency_name`: string
- `market_cap`: numerico o nulo
- `share_class_shares_outstanding`: entero o nulo
- `weighted_shares_outstanding`: entero o nulo
- `round_lot`: entero o nulo
- `request_date`: fecha parseable
- `_dataset`: string, debe ser `overview`
- `_ingested_utc`: timestamp parseable

## 7. Reglas estructurales minimas

- `ticker` no debe ser nulo.
- `request_date` debe ser parseable.
- `_dataset` debe ser `overview`.
- `_ingested_utc` debe ser parseable.
- El schema debe tolerar columnas opcionales ausentes por antiguedad, error 404 historico o disponibilidad de fuente.

## 8. Reglas de interpretacion

`overview` es una fotografia de metadatos.

No debe tratarse como:

- fuente unica de identidad historica;
- prueba final de continuidad corporativa;
- fuente unica de market cap historico;
- ni sustituto de universe builder.

Cuando se use para universo `lt1b`, debe declararse:

- fecha de observacion;
- fuente de market cap;
- y ventana de validez.

## 9. Conclusion operacional

`reference/overview` queda definido como snapshot variable de metadatos por ticker y fecha de solicitud.

La variabilidad de columnas es esperada y debe gobernarse mediante campos requeridos minimos mas campos opcionales.
