# 020 - The Engulfing Candles Strategy

## Metadatos
- **Numero de archivo:** 020
- **Revista:** Strategy Concepts (TradeStation)
- **Archivo PDF:** SCC Issue 10 Oct 2015.pdf
- **Issue:** 10 (Oct 2015)
- **Página TOC:** 8
- **Línea TOC:** 77
- **Carpeta de origen:** G:\03_SersansSistemas_algoritmico\02_practice\02_workshops\23-practice-13\docs\STRATEGY CONCEPTS\STRATEGY CONCEPTS\2015-10
- **Autor:** Frederic Palmliden, CFA, CMT
- **Nombre de estrategia:** The Engulfing Candles Strategy

## Contexto operativo
- **Tipo de activo / mercado:** The Engulfing Candles Strategy
- **Mercados indicados:** Stock index futures, ETFs
- **Horizonte:** No detectado
- **Estilo de estrategia:** Cycles

## Resumen técnico
(GBPUSD) 120-minute bars with TSL: Engulfing Candles strategy and ShowMe and TSL:Strategy ATR Bands indicator For more background on candlestick analysis, readers may want to consult books and websites from luminaries such as Steve Nison, Thomas Bulkowski, John Person and Greg Morris, among others. bearish engulfing (right) patterns

## Reglas clave
The following is a summary of the trading rules as described
Number of candles (bars) used to calculate
AvgBodyLength              5         the exponential average of the real body         in the previous section.
of the candles
Long Entries
Number of candles (bars) used to calcu-
ATR_Length                 5         late the ATR                                     u W hen a bullish engulfing candle is identified, a buy stop is
placed one minimum tick above the higher of the bullish
ProfitTgt_ATRFactor        3         Multiple of ATRs for setting profit target
engulfing candle or the bear candle that preceded it. The
Stop_ATRFactor             3         Multiple of ATRs for setting stop level             buy stop order is valid only on the bar immediately fol-
lowing the bullish engulfing candle.
TimeExit (Bars) LX and TimeExit (Bars) SX                                              Short Entries
Input                 Default                     Description                        u W
 hen a bearish engulfing candle is identified, a sell stop is
placed one minimum tick below the lower of the bearish
Number of candles (bars) to hold position
BarToExitOn              5       before exit; bar of entry and bar of exit are not     engulfing candle or the bull candle that preceded it. The
included in the count                                 sell stop order is valid only on the bar immediately fol-
lowing the bearish engulfing candle.
TSL:Engulfing Candles ShowMe
Exits
Input                 Default                     Description
Number of candles (bars) used to calculate             for each entry as a multiple of the average true range of the
AvgBodyLength            5       the exponential average of the real body of
the candles                                            most recent bars.
Plot                                          Description
(Bars) LX and TimeExit (Bars) SX are used to exit any
Bullish Eng           Mark placed on the low of a bullish engulfing candle              positions that have not been closed by either the profit
Bearish Eng           Mark placed on the high of a bearish engulfing candle             target or stop loss.
Alert Criteria                                Alert Text
Bullish engulfing     “Bullish Engulfing”
candle
Bearish engulfing     “Bearish Engulfing”
candle
10 | STRATEGY CONCEPTS CLUB
Figure 3: Strategy Performance Report – Performance Summary tab (excerpts)
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
The following discussion is based on results
from a series of tests and optimizations, but
not from a comprehensive optimization of all
inputs simultaneously. Broad optimizations
were done on the inputs AvgBodyLength,
ATR_Length, ProfitTgt_ATRFactor and
Stop_ATRFactor.
Using values derived from that optimiza-       All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily indicative of future results.
tion, the inputs related to maximum holding
periods were optimized: BarToExitOn in the
TimeExit (Bars) LX and TimeExit (Bars) SX strategy compo-
Entries and ATR exits in this strategy are taken with limit and
nents. The addition of these strategy components improved
stop orders; Look-Inside-Bar Back-testing (LIBBT) is used to
the Total Net Profit and reduced the Avg. Bars in Winning
add greater precision when back testing a strategy that uses
Trades and Avg. Bars in Losing Trades.
these types of orders.
The values and results below were returned following this
second step in testing. Readers are encouraged to experiment                   Total Net Profit
with their own tests, with and without the time exits or any                   u Th  e results here are promising for a five-year test and
other components that they suspect might integrate well.                            appear favorable on both the long and short sides.
Total Number of Trades
BACK-TESTING SETTINGS                                                                        u Th
 e pace of trading is manageable with approximately one
AvgBodyLength                          3                                                        trade every two days given the five-year test period. For
those considering using a different bar interval, it might be
ATR_Length                             5
useful to think in bars rather than days: approximately one
ProfitTgt_ATRFactor                    2.2                                                      trade every 25 bars in this example.
Stop_ATRFactor                         4.8
Percent Profitable
BarToExitOn (LX)                       32                                                    u Th
 is metric is very encouraging. A common guide in
BarToExitOn (SX)                       13                                                       short-term swing trading strategies like this is to look for a
win rate of about 70%. Additionally, the Percent Profitable
Symbol                                 GBPUSD                                                   is also consistent for long and short trades.
Trade Size                             £100,000
Max. Consecutive Winning Trades and Max.
Commissions                            $2.50 per trade, per side                             Consecutive Losing Trades
History                                5 years ending 6/30/2015                              u Th
 e longest winning streak is 19 trades, a very healthy
Bar Interval                           120 minutes                                             number. And it is complemented with no losing streak
exceeding seven trades. These fields report only the longest
Look-Inside-Bar Back-testing
12 minutes                                              such streaks. More information is available on the Trade
(LIBBT)
Analysis tab and is discussed below.
STRATEGY CONCEPTS CLUB           | 11
Visit TradeStation Labs
in the TradingApp Store
®
Built by traders for traders, the TradingApp® Store gives TradeStation clients
access to more ideas, strategies and custom trading solutions than ever before.
TradeStation Labs is an active contributor to the TradingApp Store, with dozens
of custom products available for download.
 elect and download any product instantly
uS
Products from TradeStation Labs in the TradingApp Store download directly to your TradeStation desktop platform
in seconds – offering full compatibility and seamless integration.
TradeStation Labs is a team of technical analysts who work side by side with the platform developers, bridging
the possibilities of what can be done with TradeStation and what you need to realize those possibilities. All
TradeStation Labs’ products are geared to helping you make the most of your TradeStation experience.
TRADESTATION LABS’ FEATURED PRODUCT
Fibonacci Retracement Channel
Anyone studying price charts will notice
that price action often occurs within
channels, and these channels often
persist for extended periods. Although
the judgment of the chartist is usually
involved in finding these channels, they
may also be detected systematically using
linear regression techniques. Fibonacci
retracement levels within the channel
often act as support and resistance, while
breaking a well-established channel may
reveal a change in trend.
This product contains two indicators which calculate
and display price channels on a chart. They are both
based on Fibonacci levels around linear regression
