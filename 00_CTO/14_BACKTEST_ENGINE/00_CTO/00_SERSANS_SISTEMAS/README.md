# 00_SERSANS_SISTEMAS - README

Status: ROOT_ORIENTATION_README
Created: 2026-07-28
Scope: material SersanSistemas movido al contexto CTO del backtest engine.

## 1. Que es esta carpeta

Esta carpeta agrupa todo el material SersanSistemas que vamos a usar como fuente practica para construir el backtester TSIS de small caps.

La ubicacion viva es ahora:

```text
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/00_CTO/00_SERSANS_SISTEMAS
```

La decision de moverlo aqui es correcta: Sersan ya no queda como una biblioteca externa aislada, sino como una fuente de conocimiento colocada junto al diseno del backtest engine.

## 2. Objetivo

Usar SersanSistemas para alimentar decisiones concretas del backtester, no para bloquear la implementacion con una guia cerrada.

Flujo correcto:

```text
necesidad concreta del vertical slice
  -> consultar Sersan course / youtube / blog
  -> contrastar con libros, datos y tests
  -> declarar decision TSIS minima
  -> implementar
  -> probar
  -> documentar lo demostrado
```

## 3. Paquetes principales

```text
00_SERSANS_SISTEMAS_BLOG
00_SERSANS_SISTEMAS_COURSE
00_SERSANS_SISTEMAS_YOUTUBE
```

### `00_SERSANS_SISTEMAS_COURSE/`

Rol: corpus principal del curso de trading algoritmico Sersan.

Estado: corpus 02-17 cerrado como canon Sersan, con adopcion TSIS no evaluada.

Contenido observado:

```text
files: 5647
markdown: 282
json/jsonl: 269
imagenes: 4740
other: 356
```

Entradas principales:

```text
00_SERSANS_SISTEMAS_COURSE/README.md
00_SERSANS_SISTEMAS_COURSE/07_INTEGRATION/FINAL/SERSAN_SYSTEM_MANUAL.md
00_SERSANS_SISTEMAS_COURSE/07_INTEGRATION/FINAL/FINAL_MANIFEST.json
00_SERSANS_SISTEMAS_COURSE/07_INTEGRATION/FINAL/KNOWLEDGE_RECORDS/
00_SERSANS_SISTEMAS_COURSE/01_SOURCE/<practice>/90_EXTRACTION/
```

Uso para el backtester:

```text
- datos, sesiones y price views;
- causalidad de estrategias;
- entradas, salidas, stops y filtros;
- metricas y lectura de performance;
- optimizacion, robustez, IS/OOS y walk forward;
- costes, slippage y fidelidad de ejecucion;
- money management, portfolio e incubacion.
```

### `00_SERSANS_SISTEMAS_YOUTUBE/`

Rol: material Sersan sobre experiencia real y proyecto small caps.

Contenido observado:

```text
files: 24
markdown: 12
imagenes: 8
other: 4
```

Incluye transcripciones de la serie small caps y notas/ideas extraidas del video:

```text
Small Caps el backtest NO te prepara para esto 1 mes en real
EP3 - estrategia ganadora para largos
EP4 - estrategia ganadora para cortos
EP5 - resultados tras 2 meses operando en real
```

Uso para el backtester:

```text
- recordar que la senal es solo una pieza;
- incorporar premarket, halts, spreads, slippage, locates, datos sucios, ejecucion real, riesgo y registros;
- extraer requisitos de observabilidad, ejecuciones, posiciones, locates, costes, dashboard y reconciliacion.
```

Estado: fuente practica smallcaps. No esta consolidada en el mismo canon 02-17 del curso salvo documentos de ideas extraidas. Debe tratarse como evidencia complementaria.

### `00_SERSANS_SISTEMAS_BLOG/`

Rol: articulos/PDF Sersan sobre backtesting y datos small caps.

Contenido observado:

```text
files: 2
pdf: 2
```

Archivos:

```text
Trading algoritmico en small caps_ errores al backtestear.pdf
Trading algoritmico en small caps_ la importancia de los datos.pdf
```

Uso para el backtester:

```text
- particularidades smallcaps;
- riesgos de datos;
- sesgos de backtest;
- ejecucion realista;
- requisitos que deben contrastarse con Data Foundation y literatura.
```

Estado: fuente complementaria. Falta convertirla a markdown/extraccion si queremos que agentes la lean rapido sin abrir PDF.

## 4. Relacion entre paquetes

```text
COURSE
  metodo general de construccion, evaluacion, optimizacion, sizing, portfolio e incubacion

YOUTUBE
  experiencia aplicada smallcaps y pistas de arquitectura operativa real

BLOG
  advertencias especificas de smallcaps: datos, sesgos y backtest enganoso
```

La prioridad practica para el backtester es:

```text
1. COURSE/07_INTEGRATION/FINAL para metodo consolidado.
2. YOUTUBE para smallcaps reales, DAS, ejecucion, locates, dashboard y operativa.
3. BLOG para riesgos especificos de datos/backtest smallcaps.
```

## 5. Politica de uso

```text
SERSAN_SOURCE_KNOWLEDGE
  ensenanza o experiencia observada en Sersan.

TSIS_DECISION_PENDING
  idea util para TSIS todavia no probada.

TSIS_VALIDATED_CONTRACT
  decision implementada y respaldada por tests, datos y evidencia local.
```

Regla:

```text
Nada de Sersan se adopta automaticamente como norma TSIS.
Se consulta bajo demanda cuando una decision concreta del backtester lo requiera.
```

## 6. Que falta por hacer

Inmediato:

```text
- Usar este corpus bajo demanda durante `BACKTEST_VERTICAL_SLICE_V0_1`.
- Cuando una decision del backtester toque Sersan, registrar fuente, estado y test asociado.
- Mantener el README del curso como mapa interno de `00_SERSANS_SISTEMAS_COURSE`.
```

Diferido no bloqueante:

```text
- Convertir los dos PDFs del BLOG a markdown/extraccion agent-friendly.
- Crear un indice rapido YOUTUBE -> requisitos smallcaps -> componentes del backtester.
- Construir un grafo Graphify raiz si se quiere navegacion semantica global.
- Revisar referencias absolutas antiguas solo cuando bloqueen navegacion; las notas historicas pueden conservar rutas antiguas como evidencia.
```

No hacer ahora:

```text
- No reconciliar exhaustivamente todo Sersan antes de programar.
- No escribir una guia cerrada antes del primer vertical slice.
- No tratar videos/blog como autoridad superior a contratos de datos, bibliografia y tests TSIS.
```

## 7. Estado recomendado

```text
SERSAN_ROOT_LOCATION = C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/00_CTO/00_SERSANS_SISTEMAS
COURSE_CANON = CLOSED_FOR_SERSAN_02_17
YOUTUBE_SMALLCAPS = COMPLEMENTARY_SOURCE
BLOG_SMALLCAPS = COMPLEMENTARY_SOURCE_REQUIRES_EXTRACTION
BACKTEST_ENGINE_USAGE = ON_DEMAND_DURING_VERTICAL_SLICE
FULL_TSIS_RECONCILIATION = DEFERRED_NOT_BLOCKING
```
