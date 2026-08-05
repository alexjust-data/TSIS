# 027 - Breakout Score Strategy

## Metadatos
- **Numero de archivo:** 027
- **Revista:** Strategy Concepts (TradeStation)
- **Archivo PDF:** SCC Issue 14 Feb 2016.pdf
- **Issue:** 14 (Feb 2016)
- **Página TOC:** 3
- **Línea TOC:** 69
- **Carpeta de origen:** G:\03_SersansSistemas_algoritmico\02_practice\02_workshops\23-practice-13\docs\STRATEGY CONCEPTS\STRATEGY CONCEPTS\2016-02
- **Autor:** Frederic Palmliden, CFA, CMT
- **Nombre de estrategia:** Breakout Score Strategy

## Contexto operativo
- **Tipo de activo / mercado:** Breakout Score Strategy
- **Mercados indicados:** No detectado
- **Horizonte:** Swing trading
- **Estilo de estrategia:** Trend-following

## Resumen técnico
Readers interested in a different approach to price                        The Breakout Score can then be displayed as an oscil- channels may want to examine Frederic Palmliden’s                           lator and offers a thumbnail of the direction in which the Asymmetric Channel Breakout strategy published in Issue                     market is leaning. However, if trading rules were to be 6, June 2015.                                                               similar to those used for the simple price channel strategy, it would not address the weaknesses mentioned above; that is, entries and reversals on a cross of 0 might be The Breakout Score strategy is built on a simple price                      saws during trading ranges or avoid being “always in” the channel. In the example below, the length of the channel                    market. is set to 8 bars. The score on each bar is the sum of the                       The Breakout Score strategy attempts to address this upside and downside breakouts of the channel. Each                          by setting distinct entry levels away from the center line. upside penetration of the channel adds 1 to the score;                      This creates a neutral zone in which no new positions are each downside penetration subtracts 1 from the score.                       taken. In addition, there are two exit signals associated

## Reglas clave
No detectado automáticamente.

## Inputs
No detectado automáticamente.

## Notas de performance / backtest
 e strategy shows reasonable profitability, with
REPORT HIGHLIGHTS                                               positive results on both sides of the market. However,
it should be noted that there was a large positive outlier
The Breakout Score strategy was applied to 10 years of          on the short side, which contributed the lion’s share
daily data of the SPDR S&P 500 ETF (SPY). The inputs            of the short-side profits. That trade ran from 9/19/08
were set to the values as noted in the Strategy Elements        to 10/28/08 and resulted in a profit exceeding $4,700.
section above. These were determined by a series of             (Outlier trades are listed on the Trade Analysis tab of
optimizations.                                                  the Strategy Performance Report.)
STRATEGY CONCEPTS CLUB      |5
Profit Factor                                               Avg. Bars in Winning Trades and Avg. Bars in
 ese metrics are quite good for a trend-following       Losing Trades
strategy, even when discounting the outlier short        u O n average, holding periods for winning trades are
trade.                                                      almost three times those of losing trades, though the
short side did not help these metrics. This, too, fits with
Total Number of Trades                                         a functional trend-following approach: hold winners
trading – should have a modest number of trades
Max. Shares/Contracts Held and Total Shares/
when applied to daily bars. There were fewer than 5
Contracts Held
trades per year in this test.
 s discussed above, the trade size used in this test was
Percent Profitable                                            based on employing $15,000, with the share quantity
 ese results are very encouraging for any trend-          rounded down to the nearest 10 shares. These fields
following approach. Strategy traders know that a win       show the largest position taken was 200 shares; not
rate exceeding 40% for trend following is a favorable      shown is that the smallest position taken was 70 shares.
sign.                                                      The average position size was 105 shares. This can be
calculated by dividing the Total Shares/Contracts Held
Ratio Avg. Win:Avg. Loss
 ese values, too, are healthy for trend following: an
when comparing results for the same strategy with
effective reward to risk ratio that exceeds 2.
different trade size schemes, such as 100 shares for all
trades.
Figure 4 – Strategy Performance
Report – Performance Summary
tab
All performance results are hypothetical. Past
performance, actual or hypothetical, is not
necessarily indicative of future results.
6 | STRATEGY CONCEPTS CLUB
Figure 5 – Strategy Performance
Report – Performance Graphs tab
– Equity Curve Line
All performance results are hypothetical. Past
performance, actual or hypothetical, is not
necessarily indicative of future results.
Percent of Time in the Market                                                        and Dollar Trailing, or others, may be added to the chart
a high percentage of the time. A very simple price                                    The strategy makes no provision for reentry in the
channel strategy is likely to be in the market virtually                          same direction following an exit; that is, an LX 0 Score
100% of the time. This is one of the weaknesses of such                           or SX 0 Score exit signal may occur mid-trend. If the
a strategy. Setting a neutral zone between long and                               Breakout Score does not retrace, then no new signal to
short signals and having several exit methods is meant                            reenter in the same direction would be generated.
to mitigate this. At 53%, Percent of Time in the Market
is very reasonable for a strategy like this.                                           On the other hand, while holding a position, the
strategy can generate additional entry signals in the same
direction. TradeStation’s default setting, applied here, is
SUGGESTIONS FOR IMPROVEMENT                                                          not to permit multiple entries. An aggressive trader may
It is worth mentioning once again that there should be                               want to run back-tests allowing them, perhaps combined
some type of emergency stop for this strategy. Nothing of                            with changes to the trade size setting. (The setting for
the kind is included in this back-test or in the strategy as                         multiple entries can be seen in figure 3, just above the
written. The TradeStation-supplied strategies Stop Loss                              trade size setting.)
Stanley Dash, CMT is Vice-president, Applied Technical Analysis, at TradeStation. He and his group support active and institutional traders with analytical
tools and education designed to help them become more effective traders.
His Wall Street career began in 1975 and includes time as an active floor trader at one of the leading U.S. futures and options exchanges. Mr. Dash
has lectured for the New York Institute of Finance and the Institute for Financial Markets. He is also a Chartered Market Technician and a member of the
Market Technicians Association, where he serves on the Editorial Board of the Association’s Journal of Technical Analysis.
STRATEGY CONCEPTS CLUB                 |7
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
