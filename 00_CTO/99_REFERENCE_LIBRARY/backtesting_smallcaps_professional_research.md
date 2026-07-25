# Backtesting Profesional Para Small Caps

Investigacion hecha el 22 de julio de 2026. Para construir una infraestructura profesional de backtesting de small caps, yo priorizaria este contenido, no libros de "trading retail".

## Nucleo Obligatorio

1. **Marcos Lopez de Prado, _Advances in Financial Machine Learning_**  
   Base moderna para evitar fugas de informacion, overfitting, purged/embargoed CV, backtest statistics y HPC. Es probablemente el libro mas util para disenar el protocolo de investigacion y validacion.  
   Fuente: [Wiley](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advances-in-financial-machine-learning-978-1-119-48208-6)

2. **Bailey, Borwein, Lopez de Prado & Zhu, "The Probability of Backtest Overfitting"**  
   Paper clave para medir PBO mediante CSCV. Obligatorio si vas a probar muchas variantes de estrategias.  
   Fuente: [SSRN](https://papers.ssrn.com/sol3/Papers.cfm?abstract_id=2326253)

3. **Bailey & Lopez de Prado, "The Deflated Sharpe Ratio"**  
   Corrige Sharpe por seleccion, multiples pruebas y no-normalidad. Metrica central para tu motor de evaluacion.  
   Fuente: [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551)

4. **Arnott, Harvey & Markowitz, "A Backtesting Protocol in the Era of Machine Learning"**  
   Protocolo de investigacion serio: hipotesis ex ante, trazabilidad de experimentos, control de data mining.  
   Fuente: [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3275654)

5. **White, "A Reality Check for Data Snooping" + Hansen, "A Test for Superior Predictive Ability"**  
   Para comparar muchas reglas/modelos contra benchmark sin enganarte con data snooping.  
   Fuentes: [White, Econometrica](https://doi.org/10.1111/1468-0262.00152), [Hansen, SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=264569)

## Small Caps: Sesgos Criticos

6. **Shumway, "The Delisting Bias in CRSP Data"**  
   Fundamental. En small caps, ignorar delistings y bankruptcies infla brutalmente los resultados.  
   Fuente: [Journal of Finance](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1997.tb03818.x)

7. **Dimson, "Risk Measurement When Shares Are Subject to Infrequent Trading"**  
   Small caps tienen dias sin operaciones, precios stale y betas sesgados.  
   Fuente: [ScienceDirect](https://www.sciencedirect.com/science/article/pii/0304405X79900138)

8. **Blume & Stambaugh, "Biases in Computed Returns"**  
   Muestra como closing prices y microestructura distorsionan el size effect. Muy importante para no sobreestimar retornos equal-weighted.  
   Fuente: [ScienceDirect](https://www.sciencedirect.com/science/article/pii/0304405X83900569)

9. **Hou, Xue & Zhang, "Replicating Anomalies"**  
   Paper moderno esencial: muchas anomalias desaparecen al controlar microcaps, value-weighting y multiples tests.  
   Fuente: [Review of Financial Studies](https://academic.oup.com/rfs/article/33/5/2019/5236964)

## Microestructura y Datos

10. **Hasbrouck, _Empirical Market Microstructure_**  
    Mejor referencia academica para trades, quotes, spreads, order flow y costes.  
    Fuente: [Oxford Academic](https://academic.oup.com/book/52241)

11. **Harris, _Trading and Exchanges_**  
    El libro practico serio sobre ordenes, mercados, liquidez, spreads y ejecucion.  
    Fuente: [Oxford Academic](https://academic.oup.com/book/52292)

12. **O'Hara, _Market Microstructure Theory_**  
    Base teorica: market making, inventario, informacion, liquidez.  
    Fuente: [Wiley](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/market-microstructure-theory-978-0-631-20761-0)

13. **Bouchaud et al., _Trades, Quotes and Prices_**  
    Referencia moderna sobre limit order books, price impact y regularidades empiricas.  
    Fuente: [Cambridge](https://www.cambridge.org/core/books/trades-quotes-and-prices/029A71078EE4C41C0D5D4574211AB1B5)

14. **Barndorff-Nielsen, Hansen, Lunde & Shephard, "Realized Kernels in Practice: Trades and Quotes"**  
    Util para limpiar datos TAQ/tick: trades corregidos, spreads negativos, outliers, timestamps.  
    Fuente: [Wiley](https://onlinelibrary.wiley.com/doi/full/10.1111/j.1368-423X.2008.00275.x)

## Costes, Liquidez y Capacidad

15. **Amihud, "Illiquidity and Stock Returns"**  
    La medida clasica de iliquidez basada en retorno absoluto sobre volumen en dolares.  
    Fuente: [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1386418101000246)

16. **Goyenko, Holden & Trzcinka, "Do Liquidity Measures Measure Liquidity?"**  
    Comparacion rigurosa de proxies de liquidez con datos diarios.  
    Fuente: [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1108553)

17. **Corwin & Schultz, "A Simple Way to Estimate Bid-Ask Spreads from Daily High and Low Prices"**  
    Muy util si no tienes quotes completas para todo el universo.  
    Fuente: [Journal of Finance](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.2012.01729.x)

18. **Frazzini, Israel & Moskowitz, "Trading Costs"**  
    Paper empirico muy serio sobre costes reales, impacto y capacidad.  
    Fuente: [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3229719)

19. **Almgren & Chriss, "Optimal Execution of Portfolio Transactions" + Gatheral, "No-Dynamic-Arbitrage and Market Impact"**  
    Para modelar ejecucion, impacto temporal/permanente y evitar modelos de coste absurdos.  
    Fuentes: [Almgren-Chriss](https://doi.org/10.21314/JOR.2001.041), [Gatheral SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1292353)

## Infraestructura Local Recomendada

Para un PC, la base tecnica mas razonable seria:

- **Parquet** como formato principal: columnar, comprimido, eficiente. Fuente: [Apache Parquet](https://parquet.apache.org/)
- **DuckDB** para consultas SQL directas sobre Parquet, con pushdown de columnas/filtros. Fuente: [DuckDB Parquet docs](https://duckdb.org/docs/current/data/parquet/overview)
- **Polars lazy** para pipelines rapidos y reproducibles en Python. Fuente: [Polars Lazy API](https://docs.pola.rs/user-guide/concepts/lazy-api/)
- **LEAN/QuantConnect** como motor de referencia para estudiar arquitectura event-driven profesional, aunque para small caps avanzadas probablemente acabaras customizando mucho. Fuente: [LEAN docs](https://www.quantconnect.com/docs/v2/lean-engine)

## Checklist Minimo De Tu Backtester

Tu infraestructura debe soportar, como minimo:

- Universo point-in-time, sin survivorship bias.
- Delistings, bankruptcies, mergers, ticker changes y corporate actions.
- Precios raw y ajustados, ambos guardados.
- Liquidez diaria e intradia: spread, ADV, turnover, no-trade days.
- Fill model realista: bid/ask, partial fills, participation cap, slippage, market impact.
- Short availability, borrow cost y hard-to-borrow para estrategias short.
- Halts, suspensiones y dias con prints erroneos.
- Registro de experimentos: hipotesis, parametros, numero de pruebas, hash de datos, version de codigo.
- Metricas robustas: DSR, PBO, drawdown, turnover, capacity, HAC/Newey-West, bootstrap.

Para datos USA, el estandar academico es **CRSP/Compustat + TAQ**; CRSP cubre activos e inactivos y corporate actions, y TAQ cubre trades/quotes/NBBO. Fuentes: [CRSP](https://www.crsp.org/about-us/), [NYSE TAQ](https://www.nyse.com/data-products/catalog/daily-taq). Para fundamentales y eventos publicos, EDGAR es obligatorio: [SEC EDGAR APIs](https://data.sec.gov/).
