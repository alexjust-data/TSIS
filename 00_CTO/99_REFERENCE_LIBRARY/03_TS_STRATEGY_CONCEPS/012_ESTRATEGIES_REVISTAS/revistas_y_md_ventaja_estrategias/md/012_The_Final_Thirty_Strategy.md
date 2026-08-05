# 012 - The Final Thirty Strategy

## Metadatos
- **Numero de archivo:** 012
- **Revista:** Strategy Concepts (TradeStation)
- **Archivo PDF:** SCC Issue 6 Jun 2015.pdf
- **Issue:** 6 (Jun 2015)
- **Página TOC:** 9
- **Línea TOC:** 25
- **Carpeta de origen:** G:\03_SersansSistemas_algoritmico\02_practice\02_workshops\23-practice-13\docs\STRATEGY CONCEPTS\STRATEGY CONCEPTS\2015-06
- **Autor:** Stanley Dash, CMT
- **Nombre de estrategia:** The Final Thirty Strategy

## Contexto operativo
- **Tipo de activo / mercado:** The Final Thirty Strategy
- **Mercados indicados:** Broad-based stock index ETFs
- **Horizonte:** No detectado
- **Estilo de estrategia:** Trend following

## Resumen técnico
Equity Curves SUGGESTIONS FOR IMPROVEMENT The TSL:Asymmetric Channel Breakout offers a new twist on traditional strategy trading applications by giving the trader the ability to focus on one side of the market (i.e., long or short). The strategy is also unique in that it blends trend-fol- lowing and mean-reversion rules. As always, a number of possible improve- ments could be explored.

## Reglas clave
No detectado automáticamente.

## Inputs
No detectado automáticamente.

## Notas de performance / backtest
REPORT HIGHLIGHTS                                                                                                     50%.
TradeStation’s Strategy Performance Report and Strategy                                                       Percent of Time in the Market (not shown)
Optimization Report were used with the Final Thirty                                                                u Th
 is approaches 0% in all tests, as the maximum hold
strategy to step through the development questions as enu-                                                            would be 30 minutes per day.
merated in the Strategy Elements section above.
Does the magnitude of the price change in the first six
BACK-TESTING SETTINGS                                                                                            hours aid in qualifying signals? TradeStation’s optimization
engine can help address this by testing only the first two
Symbol                                             SPY – SPDR S&P 500 ETF
inputs. As listed in the table below, the optimization ranges
Trade Size                                         100 shares
were intentionally set to straddle zero. That is, perhaps a
Commissions                                        $.01 per share
positive change is a good signal, but it may be that a “not
History                                            5 years ending 3/31/15
very negative” change is also bullish. In this case, using a
Bar Interval                                       30-minute
threshold percent price change improved the profitability
Does the direction of price change up until 3:30 p.m.                                                         and some of the metrics that concerned us.
portend the action in the last 30 minutes of the day? To create
Optimization 1
a baseline study, the inputs were left at default values as
Input                    Optimization Range     Optimal Result
in the table above. That means with PositiveDayChange
and NegativeDayChange set at 0, the price change from                                                                PositiveDayChange            -.25 .. 1: .05         .35
the open up to 3:30 p.m. had only to be up or down any                                                               NegativeDayChange            -1 .. .25: .05         -.30
Figure 2: Strategy Performance Report highlights for baseline results
All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily indicative of future results.
STRATEGY CONCEPTS CLUB   | 11
Figure 3: Strategy Performance Report highlights after optimization of PositiveDayChange and NegativeDayChange
All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily indicative of future results.
Optimization 2
Figure 3 is an excerpt from the Strategy Performance
Input                    Optimization Range   Optimal Result
Report – Performance Summary tab and the Performance
VolumePctFilter              50 .. 125: 5          55
Graphs tab – Equity Curve Line after optimization of
PositiveDayChange and NegativeDayChange.                                                                              VolumeAvgDays                 1 .. 10: 1            5
Total Number of Trades                                                                                                 Figure 4 is an excerpt from the Strategy Performance
 is number has been reduced dramatically, with better                                                          Report – Performance Summary tab and the Performance
profitability.                                                                                                  Graphs tab – Equity Curve Line after optimization of
Percent Profitable                                                                                                 VolumePctFilter and VolumeAvgDays.
Total Number of Trades
right direction.                                                                                                u This reflects only an incremental decrease in the number
Ratio Avg. Win:Avg. Loss                                                                                              of trades.
Percent Profitable
Can volume serve as a filter? With PositiveDayChange                                                           u This metric shows only a very small change from the
and NegativeDayChange left at .35 and -.30, respectively,                                                             previous test, though the consistent levels for long and
per the optimization above, and UseDayChange_1_                                                                       short trades are notable.
AndVolume_2 now set to 2, an optimization can be run on                                                            Ratio Avg. Win:Avg. Loss
the volume filter conditions.                                                                                      u 1.33. Here, too, only an incremental improvement.
Figure 4: Strategy Performance Report highlights after optimization of VolumePctFilter and VolumeAvgDays
All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily indicative of future results.
12 | STRATEGY CONCEPTS CLUB
The final run was to optimize the price and volume conditions                                                      SUGGESTIONS FOR IMPROVEMENT
together. The optimization ranges were narrowed from the                                                           The strategy and tests offered here do not include the use
individual tests above based on the earlier results.                                                               of any protective stops. Even with an extremely short and
Optimization 3                                                                                                     well-defined holding period, prudence dictates the use of
a protective stop in case of an exceptional adverse move in
Input                                         Optimization Range                   Optimal Result
the last few minutes of the day. The TradeStation-supplied
PositiveDayChange                                  -.25 .. .5: .05                        .35
strategy component Stop Loss may be used off the shelf for
NegativeDayChange                                  -.5 .. .25: .05                        .20                    this purpose.
VolumePctFilter                                     50 .. 110: 5                           90                          Similarly, there are no proactive exits for taking profits.
VolumeAvgDays                                         2 .. 10: 1                            6                    It is possible that profit could be maximized by employing
limit orders based on range to take profits intrabar rather
The standout observation is that the optimal                                                                  than waiting for the close of the session.
NegativeDayChange value is a positive number. The                                                                        The last series of tests showed a large drop in the
possibility that a bearish signal might be generated                                                               number of trades on the long side along with a jump in the
by upward price action that is not strong enough was                                                               percentage of those trades that were profitable. Although
mentioned earlier in the article and turned up in this series                                                      the strategy is predicated on the price direction for the day,
of tests. In this study, 14 of the best 20 results included a non-                                                 it is possible that some gauge of trend outside the day might
negative value for NegativeDayChange.                                                                              contribute to the strategy’s edge.
Figure 5: Strategy Performance Report highlights after optimization of PositiveDayChange, NegativeDayChange, VolumePctFilter and VolumeAvgDays
All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily indicative of future results.
Figure 5 is an excerpt from the Strategy Performance
Report – Performance Summary tab and the Performance
Graphs tab – Equity Curve Line after the optimization of
