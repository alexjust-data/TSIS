# 024 - Pivot Breakout Strategy

## Metadatos
- **Numero de archivo:** 024
- **Revista:** Strategy Concepts (TradeStation)
- **Archivo PDF:** SCC+Issue+12+Dec+2015.pdf
- **Issue:** 12 (Dec 2015)
- **Página TOC:** 9
- **Línea TOC:** 76
- **Carpeta de origen:** G:\03_SersansSistemas_algoritmico\02_practice\02_workshops\23-practice-13\docs\STRATEGY CONCEPTS\STRATEGY CONCEPTS\2015-12
- **Autor:** Stanley Dash, CMT
- **Nombre de estrategia:** Pivot Breakout Strategy

## Contexto operativo
- **Tipo de activo / mercado:** Pivot Breakout Strategy
- **Mercados indicados:** Stock index futures, ETFs
- **Horizonte:** No detectado
- **Estilo de estrategia:** Cycles

## Resumen técnico
Gauge Strategy Inputs Sensitivity Analysis All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily indicative of future results. values change. The back-tested net profit is fairly stable       clearly shows that the approach works better on the along a curved ridge formation on the back side of the sur-      long side versus the short side, notwithstanding that the face. Notice that there is a severe drop in performance near     test period was a bull market. Therefore, a clear area of the front corner of the surface where the moving averages        improvement would be to tweak the rules for short entries. use similar lengths and where the strategy rules become          A possible solution would be to include additional rules to reversed with the Fast_MA_Length input value greater             filter trades by including other calculated indices, such as than the Slow_MA_Length input value. The chosen default          the percent of Nasdaq 100 issues below the 50-day moving

## Reglas clave
Long Entries
 e following conditions are required to generate a signal:
 ere are at least 19 trading days remaining in the
calendar month.
 e bar closes higher than the previous bar.
 illiams %R is less than 85.
uW
 hen these conditions are met, a limit order is placed
uW
to buy on the next bar at a price equal to or better than
the next bar’s opening price.
 lease keep in mind that the opening time of the daily
P
session for E-mini S&P 500 futures is 6 p.m. ET.
Exits
held for at least 1 bar.
from the closing price of the bar.

## Inputs
No detectado automáticamente.

## Notas de performance / backtest
the highest high of the bars that constitute the pivot low                     Breakout strategy on five years of data of the SPDR S&P
bar and the right-strength bars. The order remains in                          500 ETF (SPY). The interval was set to 65 minutes, which
force until filled or until a new pivot high or low pattern                    generates six bars per day, as the strategy is intended for
is completed.                                                                  swing trading.
Short Entries                                                                      BACK-TESTING SETTINGS
below the lowest low of the bars that constitute pivot
Commissions                                 $.01 per share
high bar and the right-strength bars. The order remains
in force until filled or a new pivot high or low pattern is                      History                                     5 years ending 9/30/2015
completed.                                                                       Bar Interval                                65-minute
Look-Inside-Bar Back-testing (LIBBT)        5-minute
Exits
the pattern that generated the entry.                                          greater precision to back-testing, especially when testing a
closes while long is equal to the LowerClosesLX input                          useful in those cases when more than one trade is made on
value. The count of lower closes includes the bar of entry.                    a single bar.
of the pattern that generated the entry.                                       Total Net Profit
side, including this one. It may be a result of the test
closes while short is equal to the HigherClosesSX input                           period encompassing a bull market, intraday data
value. The count of higher closes includes the bar of                             notwithstanding.
entry.
STRATEGY CONCEPTS CLUB        | 11
Figure 3: Strategy Performance Report – Performance Summary tab
Total Number of Trades
 e total number of trades is reasonable for swing
trading given a five-year period and intraday data
(approximately 7,500 bars). The trades are split almost
exactly between long and short.
Percent Profitable
 ese values are in the expected range for trend following.
It may be beneficial to experiment with additional methods
to improve the win rate. A small improvement in this
statistic could make a big difference in the overall results.
Notice also that this is another example of a much better
result on the long side.
Ratio Avg. Win:Avg. Loss
 is is a reasonable value for a strategy that uses a bar
pattern to identify the near-term direction of prices and is
reasonably consistent for both long and short trades.
Avg. Bars in Winning Trades and Avg. Bars in Losing
All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily   Trades
indicative of future results.
 ese values offer some credence to the method used to
Figure 4: Strategy Performance Report – Performance Graphs tab –                                            exit trades. One of the challenges in a bar-pattern strategy
Equity Curve Line                                                                                           like this is constructing an exit routine that allows for the
trade to work yet proactively takes a profit. The consecutive
closes approach to taking a profit when price movement
stalls may be effective here.
SUGGESTIONS FOR IMPROVEMENT
Pivot highs and lows can be useful bar patterns for
identifying significant price points. The Pivot Breakout
strategy uses these to set up a trade and then requires price
continuation for entry. The strategy does not, however,
qualify the patterns; might there be a method to determine
when a pattern is more reliable or offers greater profit
potential?
As constructed, the left- and right-strength values are the
same for pivot low and pivot high patterns. It is possible that
using different values would be beneficial. This would require
adding additional inputs and making some modifications to
All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily
the EasyLanguage® for the strategy. This does carry the risk
indicative of future results.                                                                          of overcomplicating matters, particularly with asymmetric
patterns that may become entwined. With
that caution in mind, it may nevertheless
Stanley Dash, CMT is Vice-president, Applied Technical Analysis, at TradeStation. He and his                        yield interesting results.
group support active and institutional traders with analytical tools and education designed to                              The Pivot Breakout strategy includes
help them become more effective traders.                                                                                an exit based on consecutive closes against
His Wall Street career began in 1975 and includes time as an active floor trader at one of                        the current position. This shows promise as
the leading U.S. futures and options exchanges. Mr. Dash has lectured for the New York Institute                        a gauge for determining when the short-
of Finance and the Institute for Financial Markets. He is also a Chartered Market Technician and                        term effect of the pivot pattern has worn off.
a member of the Market Technicians Association, where he serves on the Editorial Board of the                           Additional or alternative proactive exits may
Association’s Journal of Technical Analysis.                                                                            help maximize retention of unrealized gains.
12 | STRATEGY CONCEPTS CLUB
Fall 2015
Williams E-mini
Influx Strategy
Visit TradeStation Labs
in the TradingApp Store
®
Built by traders for traders, the TradingApp® Store gives TradeStation clients
