# Trading and Exchanges: Market Microstructure for Practitioners

**book_id:** `trading_and_exchanges_harris`  
**Autor/Fuente:** Larry Harris  
**Tipo:** Libro PDF  
**Fuente original:** `kupdf.net_harris-trading-and-exchanges-market-microstructure-for-practitioners-2003.pdf`  
**Estado:** `indexed`  
**Unidades extraidas:** 656 `page`  
**Caracteres extraidos:** 2073313  
**OCR/revision:** `False`

## Menu Rapido

- [Rol En TSIS](#rol-en-tsis)
- [Como Deben Usarlo Los Agentes](#como-deben-usarlo-los-agentes)
- [Secciones Resumidas](#secciones-resumidas)
- [Mapa TOC/Fuente Extraido](#mapa-tocfuente-extraido)
- [Componentes TSIS Afectados](#componentes-tsis-afectados)
- [Checklist Para Agentes](#checklist-para-agentes)

## Rol En TSIS

Explica el mercado que el backtester debe simular: participantes, ordenes, liquidez, spreads, costes, impacto y ejecucion.

**Utilidad principal:** referencia principal para Order Model, Fill Model, slippage, liquidity gates, TCA y realismo small caps.

## Como Deben Usarlo Los Agentes

- Usarlo antes de disenar reglas de fills: una orden no es una intencion abstracta, es una instruccion que interactua con liquidez, prioridad, spread y seleccion adversa.
- Para small caps obliga a separar precio observado, precio ejecutable, coste explicito, coste implicito, impacto y capacidad.
- Convierte pantallas de trades/quotes en requisitos: bid, ask, last, volume, spread, profundidad disponible, orden agresiva/pasiva y estado de mercado.
- No permite aceptar backtests que rellenen al close/last sin justificar si ese precio era realmente ejecutable.

## Secciones Resumidas

### Mercado Como Sistema De Intercambio

Participantes, mecanismos de mercado y funciones economicas de la negociacion.

**Encaje TSIS:** DataFoundation, VenueModel, MarketSession.

### Ordenes Y Prioridad

Tipos de ordenes, instrucciones, agresividad, pasividad, prioridad temporal/precio y restricciones.

**Encaje TSIS:** Order model, OMS, OrderEvent.

### Liquidez, Spread Y Costes

Costes explicitos e implicitos, bid-ask spread, seleccion adversa y liquidez disponible.

**Encaje TSIS:** CostModel, SlippageModel, SmallCapLiquidityGate.

### Impacto Y Ejecucion

Por que el tamano relativo, la urgencia y el tipo de orden cambian el precio realizado.

**Encaje TSIS:** ImpactModel, ParticipationCap, ExecutionPolicy.

### Aplicacion TSIS

Transformar conceptos de microestructura en pruebas de aceptacion del simulador.

**Encaje TSIS:** Fill realism tests, TCA report, executable price gates.

## Mapa TOC/Fuente Extraido

| # | Titulo detectado | Unidad |
|---|---|---|
| - | No se pudo extraer TOC estructurado; usar source_map y stats. | - |

Consultar el mapa completo en:

- `../index/trading_and_exchanges_harris_source_map.md`
- `../extracted/trading_and_exchanges_harris_toc.json`

## Componentes TSIS Afectados

- `Order`, `OrderType`, `OrderLifecycle`
- `ExecutionSimulator`, `FillModel`, `SlippageModel`
- `LiquidityModel`, `SpreadModel`, `ParticipationCap`
- `TransactionCostAnalysis`, `TradeVsQuoteFillAudit`

## Checklist Para Agentes

- Abrir primero este resumen.
- Abrir despues `../index/trading_and_exchanges_harris_concept_index.md` para localizar conceptos.
- Abrir `../index/trading_and_exchanges_harris_source_map.md` antes del PDF/EPUB.
- Si se toma una decision de arquitectura, citar `book_id`, seccion y artefacto TSIS afectado.
- No copiar texto largo del libro; convertirlo en decision, contrato, test o tarea.
