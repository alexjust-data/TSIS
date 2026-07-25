# 00_BIBLIOTECA - Proceso Para Convertir PDFs En Biblioteca Agent-Readable

Este directorio contiene libros, papers y documentacion larga que deben convertirse en una biblioteca rapida de consultar por agentes. El objetivo no es guardar solo PDFs, sino producir artefactos navegables, resumidos y trazables para que un agente local pueda encontrar informacion concreta sin releer un libro completo.

## Objetivo

Cada PDF importante debe terminar con:

```text
PDF original
  -> texto extraido con paginas
  -> resumen Markdown con menu enlazado
  -> indice de conceptos
  -> mapa fuente -> arquitectura TSIS
  -> grafo graphify opcional para busqueda transversal
```

El resultado debe permitir preguntas como:

```text
Donde explica este libro el event loop?
Que seccion habla de order lifecycle?
Que fuente debo leer para construir ExecutionSimulator?
Que paginas justifican separar Signal, Order, Fill y Position?
```

## Regla Principal Para Agentes

No empieces leyendo el PDF completo si ya existen artefactos procesados. Sigue este orden:

```text
1. 00_LIBRARY_INDEX.md
2. 02_TSIS_BACKTEST_ENGINE_CONCEPT_INDEX.md
3. summaries/<book_id>_agent_summary.md
4. extracted/<book_id>_pages.md solo si necesitas verificar paginas concretas
5. graphify query solo si necesitas relaciones entre varios libros
```

## Estructura Recomendada

Mantener los PDFs originales en esta carpeta o en `source/`. Para cada libro crear una carpeta procesada bajo `_processed/`:

```text
00_BIBLIOTECA/
  README.md
  00_LIBRARY_INDEX.md
  01_SOURCE_CROSSWALK.md
  02_TSIS_BACKTEST_ENGINE_CONCEPT_INDEX.md
  _processed/
    <book_id>/
      source/
        original.pdf
      extracted/
        <book_id>_pages.md
        <book_id>_toc.json
        <book_id>_metadata.json
      summaries/
        <book_id>_agent_summary.md
      index/
        <book_id>_concept_index.md
        <book_id>_source_map.md
        <book_id>_quotes_or_evidence.md
      graphify-out/
        graph.json
        GRAPH_REPORT.md
        graph.html
```

Ejemplo de `book_id`:

```text
successful_algorithmic_trading
python_for_algorithmic_trading_hilpisch
trading_and_exchanges_harris
advances_financial_machine_learning
```

Usar nombres ASCII, minusculas y guiones bajos.

## Artefactos Globales

### 00_LIBRARY_INDEX.md

Indice maestro de todos los libros procesados.

Debe contener:

```text
book_id
titulo
autor
tipo de fuente
estado de procesamiento
ruta del PDF
ruta del resumen
temas principales
utilidad para TSIS
ultima actualizacion
```

### 01_SOURCE_CROSSWALK.md

Mapa inverso fuente -> uso en TSIS.

Ejemplo:

```text
Fuente: QuantStart Event-Driven Backtesting
Extraer: Event, EventQueue, DataHandler, Strategy, Portfolio, ExecutionHandler
Encaja en: vertical slice del motor event-driven
Prioridad: alta
```

### 02_TSIS_BACKTEST_ENGINE_CONCEPT_INDEX.md

Mapa concepto -> fuente -> pagina/seccion.

Ejemplo:

```text
Concepto: Order lifecycle
Fuente primaria: NautilusTrader docs
Fuente secundaria: LEAN order docs
Fuente economica: Harris
Artefacto TSIS: OMS, OrderEvent, ExecutionSimulator
```

Este archivo es el mas importante para agentes. Debe responder rapido: "si busco X, donde leo?"

## Proceso De Principio A Fin

### Paso 1 - Inventario

Localizar el PDF y decidir `book_id`.

Registrar en `00_LIBRARY_INDEX.md`:

```text
titulo
autor
ruta original
book_id
estado = pending_extraction
```

No modificar ni borrar el PDF original.

### Paso 2 - Crear Scaffold

Crear:

```text
_processed/<book_id>/source/
_processed/<book_id>/extracted/
_processed/<book_id>/summaries/
_processed/<book_id>/index/
```

Copiar o referenciar el PDF original en `source/`.

### Paso 3 - Extraer Metadatos Y Texto

Extraer:

```text
numero de paginas
titulo detectado
autor detectado
tabla de contenidos si existe
texto por pagina
```

Guardar:

```text
extracted/<book_id>_metadata.json
extracted/<book_id>_toc.json
extracted/<book_id>_pages.md
```

Formato recomendado para `pages.md`:

```md
# <Book Title> - Extracted Pages

## Page 1

Texto...

## Page 2

Texto...
```

Cada pagina debe poder localizarse con busqueda de texto:

```text
rg -n "## Page 123" extracted/<book_id>_pages.md
```

Si el PDF es escaneado y no tiene texto extraible, marcar:

```text
requires_ocr = true
```

### Paso 4 - Detectar Estructura Del Libro

Crear un mapa de secciones:

```text
front matter
capitulos
subcapitulos
apendices
bibliografia
glosario
```

Si el TOC automatico falla, reconstruirlo manualmente a partir del texto.

Guardar en:

```text
extracted/<book_id>_toc.json
```

### Paso 5 - Crear Resumen Agent-Readable

Crear:

```text
summaries/<book_id>_agent_summary.md
```

Formato obligatorio:

```md
# <Titulo>

## Menu Rapido

- [Resumen Ejecutivo](#resumen-ejecutivo)
- [Mapa Del Libro](#mapa-del-libro)
- [Capitulo 1 - ...](#capitulo-1---...)
- [Conceptos Clave](#conceptos-clave)
- [Aplicacion A TSIS](#aplicacion-a-tsis)
- [Indice Para Agentes](#indice-para-agentes)

## Resumen Ejecutivo

...

## Mapa Del Libro

| Seccion | Paginas | Para que sirve |
|---|---:|---|

## Capitulo N - Nombre

**Paginas:** X-Y

**Resumen:** ...

**Ideas accionables para TSIS:** ...

**Componentes TSIS relacionados:** ...

**Leer si buscas:** ...

## Indice Para Agentes

| Si buscas... | Mira seccion | Paginas | Componente TSIS |
|---|---|---:|---|
```

El resumen debe ser transformativo y operativo. No copiar largos fragmentos del libro.

### Paso 6 - Crear Concept Index Del Libro

Crear:

```text
index/<book_id>_concept_index.md
```

Formato:

```md
# Concept Index - <Titulo>

| Concepto | Seccion | Paginas | Importancia TSIS | Notas |
|---|---|---:|---|---|
```

Conceptos esperados para libros de backtesting:

```text
event-driven
event queue
data handler
strategy
signal
portfolio
order
fill
execution
slippage
commission
risk
position
P&L
walk-forward
overfitting
leakage
market microstructure
```

### Paso 7 - Crear Source Map Del Libro

Crear:

```text
index/<book_id>_source_map.md
```

Formato:

```md
# Source Map - <Titulo>

| Componente TSIS | Que aporta este libro | Seccion/Paginas | Prioridad |
|---|---|---:|---|
```

Componentes TSIS de referencia:

```text
ResearchSpec
RunManifest
DataFoundation
HistoricalDataAdapter
ReplayDataAdapter
LiveDASAdapter
Clock
EventLoop
EventQueue
EventBus
OnlineStateBuilder
MarketStateSnapshot
EventStateSnapshot
EventDetection
Strategy
DecisionPolicy
Signal
PortfolioConstruction
PreTradeRisk
OMS
Order
OrderEvent
ExecutionSimulator
BrokerAdapter
Fill
Accounting
Portfolio
PostTradeRisk
Ledger
Metrics
Validation
Report
```

### Paso 8 - Actualizar Indices Globales

Actualizar:

```text
00_LIBRARY_INDEX.md
01_SOURCE_CROSSWALK.md
02_TSIS_BACKTEST_ENGINE_CONCEPT_INDEX.md
```

No basta con crear el resumen del libro. Si no se actualizan los indices globales, otros agentes no encontraran la informacion rapido.

### Paso 9 - Ejecutar Graphify Opcional

Graphify debe usarse sobre los artefactos ya procesados, no solamente sobre PDFs crudos.

Ruta recomendada:

```text
_processed/<book_id>/
```

Comando conceptual:

```text
/graphify _processed/<book_id> --wiki
```

Para toda la biblioteca:

```text
/graphify . --mode deep --wiki
```

Usar `--update` cuando se agregue o modifique un libro ya procesado:

```text
/graphify . --update
```

La salida importante:

```text
graphify-out/GRAPH_REPORT.md
graphify-out/graph.json
graphify-out/graph.html
graphify-out/wiki/
```

### Paso 10 - Control De Calidad

Antes de marcar un libro como procesado, verificar:

```text
[ ] El PDF original sigue intacto.
[ ] Existe metadata JSON.
[ ] Existe texto por pagina.
[ ] El resumen tiene menu enlazado.
[ ] Cada capitulo tiene paginas.
[ ] Hay indice "Si buscas...".
[ ] Hay concept index.
[ ] Hay source map.
[ ] Los indices globales fueron actualizados.
[ ] Se declaran limitaciones: OCR, paginas faltantes, TOC dudoso, formulas/tablas no extraidas.
```

## Estados De Procesamiento

Usar estos estados en `00_LIBRARY_INDEX.md`:

```text
pending_extraction
extracted
summarized
indexed
graphified
needs_ocr
needs_review
complete
```

## Politica De Copyright

Los artefactos deben resumir, mapear y citar paginas. No deben reproducir capitulos completos ni grandes bloques textuales del libro. Las citas textuales, si son necesarias, deben ser breves y estar vinculadas a la pagina fuente.

## Como Debe Trabajar Un Agente Con Esta Biblioteca

Para responder una pregunta:

```text
1. Buscar primero en 02_TSIS_BACKTEST_ENGINE_CONCEPT_INDEX.md.
2. Abrir el resumen del libro indicado.
3. Ir a la seccion resumida.
4. Verificar en extracted pages solo si hace falta precision.
5. Citar book_id, seccion y paginas.
```

Para procesar un libro nuevo:

```text
1. Crear book_id.
2. Extraer metadatos y paginas.
3. Crear resumen con menu.
4. Crear concept index.
5. Crear source map.
6. Actualizar indices globales.
7. Ejecutar graphify si procede.
8. Marcar estado.
```

Para mejorar un libro ya procesado:

```text
1. Revisar estado en 00_LIBRARY_INDEX.md.
2. Modificar solo los artefactos derivados.
3. No tocar el PDF original.
4. Actualizar fecha y estado.
5. Ejecutar graphify --update si hay grafo.
```

## Primer Piloto

Primer PDF elegido:

```text
C:\TSIS_Data\00_CTO\99_REFERENCE_LIBRARY\00_BIBLIOTECA\Successful Algorithmic Trading.pdf
```

`book_id` recomendado:

```text
successful_algorithmic_trading
```

Objetivo del piloto:

```text
Probar el flujo completo con un solo libro antes de procesar la biblioteca completa.
```
