# 023 - Market Breadth Gauge Strategy

## Metadatos
- **Numero de archivo:** 023
- **Revista:** Strategy Concepts (TradeStation)
- **Archivo PDF:** SCC+Issue+12+Dec+2015.pdf
- **Issue:** 12 (Dec 2015)
- **Página TOC:** 2
- **Línea TOC:** 69
- **Carpeta de origen:** G:\03_SersansSistemas_algoritmico\02_practice\02_workshops\23-practice-13\docs\STRATEGY CONCEPTS\STRATEGY CONCEPTS\2015-12
- **Autor:** Stanley Dash, CMT
- **Nombre de estrategia:** Market Breadth Gauge Strategy

## Contexto operativo
- **Tipo de activo / mercado:** Market Breadth Gauge Strategy
- **Mercados indicados:** Equities, futures, forex
- **Horizonte:** No detectado
- **Estilo de estrategia:** Bar pattern

## Resumen técnico
breadth indices, but also to unique data series dedicated                       The strategy requires using the value-based index as a to different stock indices and to discrete subsets of market               secondary data source for its calculations. For the purposes breadth indices. These calculated indices include multiple                 of this article, the necessary data can be inserted into a families of market breadth indices, including tick indices,                TradeStation chart using the symbol $VALNDD. The data Arms indices and value-based breadth indices. A value-                     series is purposely hidden in the screenshots throughout based breadth index is the sum of the price changes of each                this article to emphasize the strategy signals and improve advancing issue multiplied by its volume less the price                    their visibility. change of each declining issue multiplied by its volume.                       The strategy first calculates fast and slow exponential The result is then multiplied by 0.0001 to keep the value at a             moving averages of the value-based breadth index. Then, it reasonable level.                                                          computes the difference between these two moving aver- The table to the left               ages. Because of scaling and other issues, this calculated TradeStation

## Reglas clave
The TSL:Market Breadth Gauge strategy was applied to
the PowerShares QQQ Trust Series 1 (QQQ). However,
the strategy could be modified to be used on other secu-
rities (e.g., SPY) using the same basic principles with the
corresponding value-based breadth index as Data2 (e.g.,
$VALSPD for SPY). The detailed strategy rules are listed
below.
Long Entries
All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily
market order on the next bar.
Total Net Profit – Long Trades vs. Short Trades
Short Entries                                                                e theoretical total net profit comes mainly from long
on a market order on the next bar.                                        This is consistent with what was found when additional
Exits                                                                       testing was performed with other symbols. The Market
Breadth Gauge strategy seems to work much better on
bar when the low is below the lowest low of the last two                 further, notice that only 26 trades were short versus
bars.                                                                    138 long trades. The profit factor and other metrics for
bar when the high is above the highest high of the last                  expected, since the low number of short trades makes
two bars.                                                                it difficult to gauge the reliability of these performance
Ratio Avg. Win:Avg. Loss

## Inputs
No detectado automáticamente.

## Notas de performance / backtest
REPORT HIGHLIGHTS                                                           (1.93) is much lower than that on the short side (4.04). On
BACK-TESTING SETTINGS                                                       the surface, these figures point to the strategy favoring the
Initial Capital               $15,000
short side. However, the low number of short trades in this
particular back-test may not provide an adequate repre-
Trade Size                    $10,000 rounded down to nearest 1 share
sentation of what could be expected going forward. A 4.04
Commissions                   $.01 per share                               ratio, meaning an average winning trade that is approx-
History                       5 years ending 9/30/15                       imately four times as large as the average losing trade, is
Bar Interval                  Daily                                        simply not realistic.
STRATEGY CONCEPTS CLUB                 |5
Figure 4: Strategy Performance Report – Performance Graphs Tab - Equity Curve Detailed
Average Bars in Winning vs. Losing
Trades
trades is greater for both long and short
trades (6.06 and 4.73, respectively)
compared to the average number of
bars in losing trades for both long and
short trades (3.56 and 2.64, respectively).
Winning trades are held longer and
losing trades are cut sooner. This is an
attractive characteristic for any trading
strategy.
The equity curve is linear and quite
attractive, with small drawdowns overall.
The performance seems to be somewhat
cyclical as well, which is fairly typical in
strategy trading. The volatility of the equity
curve translated to a maximum weekly
drawdown of about 5%.
As in previous articles, instead of ana-
lyzing one strategy input in isolation, data
from TradeStation’s Strategy Optimization
Report can be used with Microsoft Excel to
perform sensitivity analysis between two
strategy inputs at the same time by creating
a 3-D chart. When performing sensitivity
analysis, it is important to consider strategy          All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily indicative of future results.
inputs that are related. Here, two
different pairs of strategy          Figure 5: TSL:Market Breadth Gauge Strategy Inputs Sensitivity Analysis
inputs are considered:
1) the Slow_MA_Length
input coupled with the
Fast_MA_Length input, and
2) the MBG_LE_Level input
coupled with the MBG_‌SE_
Level input. For each pair,
an exhaustive Strategy
Optimization Report can be
run and the resulting data
can be used to create a sur-
face chart in Excel. For each
optimization performed, the
strategy inputs that were not
optimized were kept at their
default values, per the table
in the Strategy Elements
section above.
Figure 5 illustrates
the impact on the back-
tested net profit when the
Slow_‌MA_Length and
Fast_MA_Length input
All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily indicative of future results.
6 | STRATEGY CONCEPTS CLUB
Figure 6: TSL:Market Breadth
Gauge Strategy Inputs Sensitivity
Analysis
All performance results are hypothetical. Past
performance, actual or hypothetical, is not
necessarily indicative of future results.
values change. The back-tested net profit is fairly stable       clearly shows that the approach works better on the
along a curved ridge formation on the back side of the sur-      long side versus the short side, notwithstanding that the
face. Notice that there is a severe drop in performance near     test period was a bull market. Therefore, a clear area of
the front corner of the surface where the moving averages        improvement would be to tweak the rules for short entries.
use similar lengths and where the strategy rules become          A possible solution would be to include additional rules to
reversed with the Fast_MA_Length input value greater             filter trades by including other calculated indices, such as
than the Slow_MA_Length input value. The chosen default          the percent of Nasdaq 100 issues below the 50-day moving
values for the two inputs are not peak values but are close to   average ($%50DMABND).
the top of the ridge where the Fast_MA_Length input is 5              Another possible area of improvement would be to
