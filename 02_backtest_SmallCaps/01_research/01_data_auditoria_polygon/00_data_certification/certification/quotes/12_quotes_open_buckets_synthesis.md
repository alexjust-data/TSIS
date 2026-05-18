# Quotes Open Buckets Synthesis

## Objetivo

Este documento cierra la lectura de los cuatro buckets que quedaron abiertos en `quotes`.

No sustituye al `closeout` original de `auditoria`.
Lo complementa con una lectura de certificacion apoyada en:

- `quotes`
- `halts`
- `reference`
- `additional`
- y casos visuales concretos

## Decision final de los cuatro buckets

- `persistent_soft_crossed_mid_large_scale`
  - `review`
- `large_file_threshold_edge_hard_many_crosses`
  - `review`
- `medium_file_threshold_edge_hard_many_crosses`
  - `bad`
- `high_hard_crossed_10_to_20`
  - `bad`

## Regla general que sale del cruce

El punto clave de esta fase es este:

- `halt` puede explicar el episodio
- pero no convierte automaticamente un libro fragil en `good`

Por tanto, en `quotes` hay que separar siempre:

- contexto causal del evento
- calidad operativa del libro

Eso es lo que evita sobrepromover buckets malos o mixed solo porque tengan un `halt` coherente.

## Buckets `review`

### 1. `persistent_soft_crossed_mid_large_scale`

Lectura:

- sigue siendo un bucket de crossed persistente real
- parte de sus casos queda bien contextualizada por `halts`
- otra parte sigue como residuo microestructural no explicado

Decision:

- `review`

Documento:

- [08_persistent_soft_crossed_mid_large_scale.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\quotes\08_persistent_soft_crossed_mid_large_scale.md)

### 2. `large_file_threshold_edge_hard_many_crosses`

Lectura:

- bucket mixto real
- combina casos moderados, severos y parte explicable por `halts`
- no es suficientemente limpio para `good`
- tampoco es uniformemente duro como para bajarlo entero a `bad`

Decision:

- `review`

Documento:

- [09_large_file_threshold_edge_hard_many_crosses.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\quotes\09_large_file_threshold_edge_hard_many_crosses.md)

## Buckets `bad`

### 3. `medium_file_threshold_edge_hard_many_crosses`

Lectura:

- la severidad local ya es demasiado agresiva
- aunque algunos casos tengan `halt`, eso no rehabilita la calidad del file
- el bucket mantiene cola severa suficiente para quedarse fuera del uso core

Decision:

- `bad`

Documento:

- [10_medium_file_threshold_edge_hard_many_crosses.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\quotes\10_medium_file_threshold_edge_hard_many_crosses.md)

### 4. `high_hard_crossed_10_to_20`

Lectura:

- es la familia mas dura de las cuatro abiertas
- aun cuando coincide con `halt`, sigue siendo `bad`
- no hay base para abrir subpromocion a `review`

Decision:

- `bad`

Documento:

- [11_high_hard_crossed_10_to_20.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\quotes\11_high_hard_crossed_10_to_20.md)

## Implicacion para certificacion de `quotes`

La politica local de `quotes` queda reforzada asi:

- `good`
  - usable para el uso mas estricto
- `review`
  - usable solo con control y segun el caso de uso
- `bad`
  - fuera del uso core

Y la lectura transversal queda afinada:

- `halts` es la capa causal mas fuerte para explicar una parte del residuo de `quotes`
- `reference` explica un subconjunto real pero menor
- `news` e `ipos` aportan sobre todo contexto y no deben sobreleerse como limpieza de calidad

## Cierre del bloque abierto

Con esta fase, `quotes` ya no tiene abierto un residuo ambiguo grande.
El residuo importante queda:

- localizado
- clasificado
- ilustrado con casos visuales
- y separado entre `review` y `bad`

Eso permite pasar del cierre de auditoria al cierre de certificacion del bloque.
