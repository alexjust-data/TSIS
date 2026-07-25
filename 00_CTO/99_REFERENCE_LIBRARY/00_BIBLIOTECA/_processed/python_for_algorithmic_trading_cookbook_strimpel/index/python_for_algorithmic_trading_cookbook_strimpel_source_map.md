# Source Map - Python for Algorithmic Trading Cookbook - Jason Strimpel

## Ficha

| Campo | Valor |
|---|---|
| Book ID | `python_for_algorithmic_trading_cookbook_strimpel` |
| Tipo | cookbook tecnico Python |
| Estado | extraido e indexado |
| Uso principal | recetas Python modernas para datos, backtesting, analytics y live |

## Fuente por bloque

| Bloque | Extraer | Encaje TSIS |
|---|---|---|
| Ch. 1-4 | datos, pandas, visualizacion, storage | `DataIngestionPrototype`, `LocalStoreReference` |
| Ch. 5-9 | factors, VectorBT, Zipline, Alphalens, Pyfolio | `ResearchPrototype`, `ReferenceBacktest`, `Analytics` |
| Ch. 10-12 | IB API and live deployment | `BrokerAdapterReference`, `LiveRunner` |
| Ch. 13 | ThetaData, ArcticDB, risk alerts, execution DB | `TickStore`, `RiskAlert`, `ExecutionLedger` |

## Preguntas que responde

- Como montar prototipos Python modernos para datos y backtesting.
- Como usar VectorBT, Zipline Reloaded, Alphalens y Pyfolio.
- Como estructurar interaccion basica con broker API.
- Como almacenar tick data y execution details localmente.

## Preguntas que no responde

- Como construir el motor TSIS final.
- Como garantizar semantics historico/live.
- Como modelar small caps realistas.
- Como validar PBO/DSR.

## Prioridad de lectura

1. Ch. 4, 10, 11 y 13 para storage/live/ledger.
2. Ch. 6-9 para backtesting y analytics de referencia.
3. Ch. 1-2 para ingestion y transforms.

