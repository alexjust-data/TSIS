# Quotes Schema Contract - Modulo 01

## 1. Rol

Este documento define el schema logico canonico para `quotes_core_v0_1`.

Su objetivo es fijar la unidad semantica minima del dataset `quotes` sin depender de detalles accidentales de file layout legacy.

## 2. Unidad logica

La unidad logica canonica es:

- una observacion del libro `bid/ask`

Cada fila representa una observacion del libro para un instrumento y un instante temporal concreto dentro de la sesion objetivo del bloque.

## 3. Claves logicas

Claves minimas:

- `ticker`
- `quote_timestamp`

Notas:

- `ticker` puede venir como columna o derivarse de metadata, particion o file identity;
- `session_date` puede vivir como columna, metadata o derivarse desde `quote_timestamp` bajo la sesion institucional de `quotes`.

## 4. Campos requeridos

Campos requeridos del schema logico:

- `ticker`
- `quote_timestamp`
- `bid`
- `ask`

## 5. Campos condicionales relevantes

Campos relevantes cuando existan:

- `bid_size`
- `ask_size`
- `session_date`
- `exchange`
- `conditions`

## 6. Tipos semanticos esperados

- `ticker`: identificador simbolico de instrumento
- `quote_timestamp`: timestamp parseable y util para mapear la observacion a una sesion
- `bid`, `ask`: numericos no negativos o validamente parseables
- `bid_size`, `ask_size`: numericos no negativos cuando existan
- `session_date`: fecha de sesion derivable o materializada
- `exchange`, `conditions`: metadata contextual cuando la fuente la provea

## 7. Reglas estructurales minimas

Las siguientes reglas forman parte del schema operativo:

- `quote_timestamp` debe ser parseable;
- la observacion debe poder mapearse a la sesion objetivo `04:00-20:00 America/New_York` salvo limitacion declarada;
- `bid` y `ask` no deben ser negativos;
- `ask = 0` o `bid = 0` no deben interpretarse ingenuamente como crossed economico sin policy contextual;
- `bid_size` y `ask_size`, cuando existan, no deben ser negativos;
- la identidad temporal del file, la fecha de sesion y el timestamp deben ser reconciliables.

## 8. Reglas de interpretacion

Este schema no declara que cualquier crossed implique corrupcion dura.

La interpretacion correcta de `bid > ask` depende de:

- la severidad economica del crossed;
- la persistencia local;
- el tamano del file y del episodio;
- la presencia real de `ask > 0`;
- y la policy de calidad de `quotes`.

Tambien separa dos cosas:

- estructura local del libro;
- explicacion causal del episodio desde otros datasets.

El schema solo fija la primera.

## 9. Exclusiones duras

Las familias o files que caigan en:

- `medium_file_threshold_edge_hard_many_crosses`
- `high_hard_crossed_10_to_20`

quedan fuera del dataset consumible principal aunque el schema logico general siga siendo el mismo.

## 10. Relacion con el dataset contract

Este schema sirve a:

- `01_foundations/contract_registry/dataset_contracts/quotes_dataset_contract_v0_1.md`

No redefine su policy.

Define la estructura logica minima que el dataset debe satisfacer.
