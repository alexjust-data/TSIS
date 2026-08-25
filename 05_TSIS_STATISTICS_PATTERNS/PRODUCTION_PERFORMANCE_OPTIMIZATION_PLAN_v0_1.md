# Production Performance Optimization Plan v0.1

## Propósito

Reducir el tiempo de futuras materializaciones del Daily Pattern Atlas sin
cambiar fórmulas, scopes, cardinalidades, causalidad, outputs ni gates. Este
documento es backlog de implementación para una versión posterior; no modifica
el motor que produjo y certificó `20260825_full_v0_1`.

## Baseline observado

Run: `20260825_full_v0_1`.

- tiempo total: 3.997,105 segundos, aproximadamente 66,62 minutos;
- shards: aproximadamente 24 minutos para 4.824 tickers en 8 shards y 4 workers;
- agregación: aproximadamente 39 minutos;
- certificación terminal: aproximadamente 4 minutos;
- filas de sesiones: 9.290.966;
- etiquetas: 9.728.326;
- casos de activación distintos: 4.495.723.

El cuello de botella dominante fue la agregación global. El índice directo
cruzó etiquetas y sesiones completas, agrupó etiquetas por caso y calculó IDs.
Después, las estadísticas de evento repitieron un join de trayectorias para 27
etiquetas de activación.

## Arquitectura candidata v0.2

1. Materializar dentro de cada shard una tabla estrecha de casos de activación,
   con flags o lista de etiquetas y un ID determinista precalculado.
2. Materializar por shard las trayectorias directas necesarias para D0-D20,
   reutilizando una sola numeración de observaciones por ticker.
3. Calcular todos los event offsets en una única expansión por caso y no en 27
   joins separados por etiqueta.
4. Agregar primero por shard y combinar únicamente tablas estrechas. Las
   estadísticas no combinables de forma algebraica conservarán valores exactos
   o un merge DuckDB sobre las columnas mínimas requeridas.
5. Retirar `string_agg` y hashes fila a fila del hot path global; crear las
   representaciones legibles después de resolver IDs y flags.
6. Aplicar proyección explícita para que cada fase lea solo sus columnas.
7. Hacer los shards content-addressed y reanudables: un shard certificado con
   mismo código, config, upstream y schema no se recalcula.
8. Publicar heartbeat por lote o etiqueta durante la agregación para ofrecer
   progreso granular y ETA basada en trabajo completado.

## Gate antes de sustituir v0.1

La optimización debe pasar, con el runner/wrapper/aggregator/certifier finales:

- unit tests y regresiones heredadas;
- un probe production-equivalent por cada uno de los 8 shards;
- `EXPLAIN ANALYZE` y benchmark de las rutas de mayor cardinalidad;
- igualdad exacta de claves y conteos contra v0.1 en el probe;
- igualdad numérica de estadísticas dentro de la tolerancia contractual;
- una sola variante de schema por tabla;
- todos los controles `INC-20260824-001` a `INC-20260825-010` en `PASS`;
- autorización gobernada antes de cualquier nuevo full.

## Criterio de éxito de rendimiento

La versión candidata debe reportar por separado tiempo de shards, agregación y
certificación, y demostrar una mejora material sobre el baseline de 3.997,105
segundos en el mismo corpus y hardware. No se aceptará una mejora que cambie la
semántica o reduzca controles para ganar velocidad.