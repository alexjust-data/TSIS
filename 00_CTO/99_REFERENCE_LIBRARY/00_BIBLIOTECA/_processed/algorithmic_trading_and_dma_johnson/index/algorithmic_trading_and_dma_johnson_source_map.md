# Source Map - Algorithmic Trading and DMA - Barry Johnson

## Ficha

| Campo | Valor |
|---|---|
| Book ID | `algorithmic_trading_and_dma_johnson` |
| Tipo | libro practico de ejecucion, DMA y trading electronico |
| Estado | OCR completo e indexado |
| Uso principal | order model, execution algorithms, TCA, routing, infrastructure |

## Fuente por bloque

| Bloque | Extraer | Encaje TSIS |
|---|---|---|
| Ch. 1-3 | DMA, microstructure, world markets | `MarketModel`, `VenueModel` |
| Ch. 4 | order types and instructions | `OrderModel` |
| Ch. 5 | TWAP/VWAP/POV/IS/liquidity algorithms | `ExecutionAlgorithmLibrary` |
| Ch. 6-7 | TCA and optimal strategy | `PreTradeTCA`, `PostTradeTCA` |
| Ch. 8-10 | order placement, tactics, forecasting | `ExecutionSimulator`, `OrderPlacementPolicy` |
| Ch. 11 | order management and infrastructure | `OMS`, `BrokerAdapter`, `LiveExecutionStack` |
| Ch. 12-15 | portfolio, multi-asset, news, AI | future modules |

## Preguntas que responde

- Que tipos de orden e instrucciones debe soportar un OMS.
- Como separar algoritmo de ejecucion y estrategia alfa.
- Como medir implementation shortfall y TCA.
- Como elegir entre VWAP, POV, IS y liquidity-seeking.
- Como pensar en venue choice, routing, aggressiveness y hidden liquidity.
- Que infraestructura requiere trading electronico.

## Preguntas que no responde

- Como implementar el backtester Python entero.
- Como hacer validacion estadistica avanzada.
- Como limpiar datos Polygon/DAS.

## Prioridad de lectura

1. Ch. 4-7 para `OrderModel`, algos y TCA.
2. Ch. 8-11 para `ExecutionSimulator` y broker adapter.
3. Ch. 12 solo cuando haya portfolio execution.
4. Ch. 14-15 solo para news/AI future.

