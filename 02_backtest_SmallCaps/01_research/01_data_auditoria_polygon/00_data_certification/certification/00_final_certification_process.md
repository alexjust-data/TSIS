# Final Certification Process

## Objetivo

Este documento fija como se va a plantear la certificacion final de `00_data_certification`.

No sustituye las auditorias por bloque ya existentes.
Su funcion es unirlas bajo un contrato unico, reproducible y defendible, para que distintos agentes trabajen con la misma logica.

La idea central es separar tres cosas que hoy estan mezcladas en varios notebooks y `.md`:

- presencia
- salud
- aptitud de uso

La certificacion final no debe responder solo:

- "el file existe"

Debe responder tambien:

- "deberia existir"
- "esta presente"
- "esta sano segun la politica del bloque"
- "para que uso queda aprobado o excluido"

## Modelo de certificacion

La certificacion final se planteara en tres capas:

- `presencia`
- `salud`
- `aptitud de uso`

Cada una responde a una pregunta distinta:

- `presencia`
  - existe fisicamente el dato esperado
- `salud`
  - el dato presente pasa la politica de calidad definida para su bloque
- `aptitud de uso`
  - el dato sano o parcialmente sano sirve para `backtest`, `research`, `ml` o solo para uso forense

## Unidad canonica de decision

No se debe certificar solo a nivel de dataset completo.

La unidad canonica de decision debe existir al menos en tres niveles:

- `ticker,date,dataset`
- `ticker,dataset`
- `global,dataset` y `global,auditoria`

Cada unidad tendra cuatro campos logicos:

- `expected`
  - deberia existir dato aqui
- `present`
  - existe dato en disco y entra en inventario
- `healthy`
  - pasa la politica de calidad del bloque
- `usable_for`
  - `backtest_core`, `research`, `ml`, `forensic_only`, `excluded`

Esto evita confundir:

- descargado
- materializado
- auditado
- certificado

## Contrato de salida

La salida final no debe ser solo narrativa en notebook.

Debe producir un paquete canonico de artefactos:

- `cert_manifest.json`
- `cert_global_summary.json`
- `cert_dataset_summary.parquet`
- `cert_ticker_summary.parquet`
- `cert_ticker_date_matrix.parquet`
- `cert_exclusions.parquet`
- `cert_open_issues.parquet`

### Veredicto global

El `cert_global_summary.json` debe emitir un veredicto explicito:

- `CERTIFIED`
- `CERTIFIED_WITH_LIMITATIONS`
- `NOT_CERTIFIED`

Y debe incluir:

- motivos formales
- contadores
- limites conocidos
- fecha de construccion
- universo aplicado

## Regla maestra por dataset

Antes de unir artefactos hay que fijar una politica por bloque.

La regla final no puede depender de interpretacion libre de cada agente.

Ejemplo de politica esperada:

- `daily`
  - `good` usable core
  - `review` usable con flag
  - `bad` excluido
- `ohlcv_1m`
  - misma logica que `daily`
- `quotes`
  - `good` core
  - `review` sensitivity o ML con flag
  - `bad` fuera
- `trades`
  - misma logica que `quotes`
- `halts`
  - usable como capa de verdad del evento
- `reference`
  - usable como capa de identidad con flags cuando aplique
- `short`
  - baseline preferido `FINRA`
  - `Polygon` solo comparativo o secundario
- `additional`
  - certificar por subbloque, no como capa unica
- `financials`
  - separar cobertura fisica de validez temporal

### Punto critico

Hay que decidir de forma explicita:

- si `WARN` bloquea o no bloquea
- si `review` bloquea o no bloquea
- si un bloque puede quedar certificado con exclusiones

Sin esta regla no existe certificacion final.
Solo existe diagnostico.

## Grano temporal canonico

No hay que forzar todos los datasets al mismo grano nativo.
Hay que normalizarlos operativamente.

Regla propuesta:

- `quotes`, `trades`, `halts`
  - nivel dia
- `ohlcv_1m`
  - nivel dia o mes segun artefacto disponible
- `daily`
  - nivel dia de trading o expansion controlada desde inventario con flag
- `financials`, `short_interest`, `news`, `ipos`, `economic`
  - nivel evento o periodo

Luego se construira una matriz canonica `ticker,date` solo para el universo y uso objetivo que se quiera certificar.

## Universo canonico

Antes de certificar hay que congelar un unico universo de referencia para esta fase.

Recomendacion:

- universo base de certificacion
  - `<1B>` canonico
- universo ampliado
  - `full operational`

Cada artefacto final debe declarar a cual de los dos pertenece.

Esto es obligatorio porque hoy existen mezclas entre:

- universo full historico
- universo `<1B>`
- universos operativos especificos por bloque

Si esto no se congela, las coberturas dejan de ser comparables.

## Logica secuencial de certificacion

La certificacion final se implementara en cinco capas.

### 1. Universe certification

Debe cerrar:

- universo PTI
- lifecycle
- corte `<1B>`
- expected calendar

### 2. Presence certification

Debe cerrar:

- inventarios
- outputs materializados
- merges `C/D`
- faltantes reales

### 3. Health certification

Debe cerrar:

- severidades por bloque
- root cause ya documentado
- traduccion formal a `good`, `review`, `bad`

### 4. Usage certification

Debe cerrar:

- `backtest_core`
- `research`
- `ml`
- `forensic_only`
- exclusion sets

### 5. Residual issues

Debe dejar por escrito:

- que no esta resuelto
- por que no bloquea
- o por que si bloquea

## Regla de veredicto global

La regla de veredicto debe ser simple y dura.

### `CERTIFIED`

Se puede emitir solo si:

- el universo esta congelado
- `expected` y `present` estan definidos
- las politicas de salud estan cerradas
- no hay blockers abiertos

### `CERTIFIED_WITH_LIMITATIONS`

Se puede emitir si:

- la estructura principal esta cerrada
- pero quedan limites explicitos no bloqueantes

Ejemplos posibles:

- cobertura mensual aproximada en `daily` o `ohlcv_1m`
- `financial_ratios` sparse
- `Polygon short` no baseline

### `NOT_CERTIFIED`

Se debe emitir si:

- falta politica formal
- falta traduccion `expected/present/healthy`
- o hay bloques con `FAIL` sin resolver

## Orden correcto de implementacion

No se debe empezar implementando sin marco.

El orden correcto es:

1. definir contrato de certificacion final
2. fijar universo canonico y usos objetivo
3. definir politica bloqueante por dataset
4. implementar ensamblador final
5. revisar folder por folder para mapear inputs, reglas y excepciones

## Metodo de trabajo folder por folder

Cada folder se analizara con la misma ficha.

Para cada bloque hay que responder:

- que certifica
- que artefactos produce
- que veredicto local tiene
- que reglas de salud usa
- que limites deja abiertos
- como se traduce al ensamblador final

Esta ficha permite implementar la certificacion final sin rehacer la auditoria base.

## Resultado esperado

El resultado final no debe ser solo una conclusion verbal tipo:

- "la auditoria esta bastante bien"

Debe convertirse en una salida reproducible que permita decir:

- que parte del universo esta certificada
- para que uso queda certificada
- que exclusions se aplican
- que limites siguen abiertos

## Decision operativa actual

Este documento se adopta como guia de trabajo para los siguientes agentes.

La siguiente fase consiste en recorrer los folders uno por uno y mapear:

- artefactos
- reglas
- severidades
- veredictos
- traduccion al ensamblador final

## Resumen corto

La certificacion final se planteara como una union formal de:

- universo esperado
- presencia observada
- salud certificable
- aptitud de uso

Y su salida final sera un veredicto global reproducible:

- `CERTIFIED`
- `CERTIFIED_WITH_LIMITATIONS`
- `NOT_CERTIFIED`

con artefactos canonicos y reglas explicitas por bloque.
