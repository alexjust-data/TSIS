# 030 - VWAP Bands MR Strategy

## Metadatos
- **Numero de archivo:** 030
- **Revista:** Strategy Concepts (TradeStation)
- **Archivo PDF:** SCC Issue 15 Mar 2016.pdf
- **Issue:** 15 (Mar 2016)
- **Página TOC:** 9
- **Línea TOC:** 78
- **Carpeta de origen:** G:\03_SersansSistemas_algoritmico\02_practice\02_workshops\23-practice-13\docs\STRATEGY CONCEPTS\STRATEGY CONCEPTS\2016-03
- **Autor:** Frederic Palmliden, CFA, CMT
- **Nombre de estrategia:** VWAP Bands MR Strategy

## Contexto operativo
- **Tipo de activo / mercado:** VWAP Bands MR Strategy
- **Mercados indicados:** No detectado
- **Horizonte:** Day trading
- **Estilo de estrategia:** Mean reversion

## Resumen técnico
Report – Performance Summary tabs based on the percent-based exit scheme All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily indicative of future results. The Percent Profitable row is marked, since that is the metric of interest                                                         SUGGESTIONS FOR here. Simply stated, almost 62% of the time the long signals achieved a 1.1%                                                           IMPROVEMENT favorable price movement before a similar unfavorable price movement. And although the short side suffered a net loss, almost 46% of the time the                                                            For entries, consideration could be given short signals achieved a .7% favorable price movement before a similar unfa-                                                           to adding a method to filter signals. As vorable price movement.                                                                                                                written, the Overnight-Futures-Range Breakout strategy pays no attention to A deeper investigation of this data would call for looking at the number                                                          the size of the overnight range, or the of times each of the exit rules was triggered and the number of times posi-                                                            proximity of the overnight high and low to

## Reglas clave
No detectado automáticamente.

## Inputs
No detectado automáticamente.

## Notas de performance / backtest
BACK-TESTING SETTINGS
Initial Capital   $30,000
$20,000 rounded down to nearest
Trade Size        1 share
Commissions       $.01 per share
History           6 years ending 12/31/15
Bar Interval      5 minutes
The performance of the TSL:VWAP
Bands MR strategy is first analyzed by itself
and then considered as a complement to
the original VWAP Bands strategy using
Portfolio Maestro.                                   All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily indicative of future results.
Additional Notes
 When the strategy is analyzed in Portfolio         The download includes a Portfolio Maestro file that you can import
Maestro, bear in mind that the strategy              into Portfolio Maestro. Simply go to File, select Portfolio Import/Export
is still tested using SPY. However, the              and choose Import. Then select the saved copy of the .pmx file from the
trend-following version of the strategy is           download.
tested using AAPL, per the original set-            TradeStation Portfolio Maestro 9.5 is required to run the VWAP strategies
tings of that version of the strategy.               with their respective EasyLanguage® functions at a portfolio level. The
 The trade size is set at the Strategy Group         strategies may be run on individual equities and ETFs in TradeStation 9.1
level in Portfolio Maestro with the same             or 9.5.
settings as in the Strategy Properties for
Profit Factor
All Strategies dialog in TradeStation.
Additional information on money                        e theoretical profit factor, which is calculated by dividing the gross
management in Portfolio Maestro can be                profit by the gross loss, is almost identical on the long and short sides.
found here, and general information on             Percent Profitable
Portfolio Maestro can be found here.
 The MaxBarsBack is set to 100 in the                 percentage of profitable short trades (64.35%). While long trades con-
strategy component and in Portfolio                   tributed the most to the overall net profit, notice that the number of long
Maestro at the Strategy Group level to                trades was roughly twice that of short trades.
facilitate the VWAP calculations.
RINA Index
 Commissions in Portfolio Maestro are
set at the Portfolio level in the Costs
relatively high at 357.89. The high figure is partially boosted by a low
and Quantity tab within the Back-test
percent of time in the market (9.50%).
Portfolio dialog.
STRATEGY CONCEPTS CLUB                  | 13
Figure 4: Strategy Performance Report – Performance Graphs Tab -                                         Figure 5: TSL:VWAP Bands MR Strategy Inputs Sensitivity Analysis (Long
Equity Curve Detailed                                                                                    Exits)
Figure 7 displays the performance summary when the
All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily
indicative of future results.                                                                            strategy is combined with the original TSL:VWAP Bands
trend-following strategy. The back-tested portfolio in
The equity curve is linear overall with small drawdowns.                                              Portfolio Maestro includes two Strategy Groups. The first
The volatility of the equity curve translated to a maximum                                               Strategy Group includes the TSL:VWAP Bands strategy
weekly drawdown of about 4.5%. Notice that there is a long                                               issued in the January publication, renamed TSL:VWAP
period towards the end of the chart where sideways perfor-                                               Bands TF for trend following and applied to AAPL on a
mance prevailed.                                                                                         5-minute bar interval. The second Strategy Group includes
the TSL:VWAP Bands MR strategy applied to SPY on a
As in previous articles, instead of analyzing one strategy                                           5-minute bar interval. Other previously discussed settings
input in isolation, data from TradeStation’s Strategy                                                    were kept in both Strategy Groups (e.g., initial capital, trade
Optimization Report can be used with Microsoft Excel to                                                  size, etc.).
perform sensitivity analysis between two strategy inputs at
the same time by creating a 3-D chart. For each optimiza-                                                    The total return is much higher when the two strate-
tion performed, the strategy inputs that were not optimized                                              gies are combined. However, keep in mind that additional
were kept at their default values, per the table in the Strategy                                         capital was required to run the strategies in a portfolio
Elements section above.                                                                                  setting. In this example, the initial capital for each strategy
Figure 5 illustrates the impact on the back-tested net
Figure 6: TSL:VWAP Bands MR Strategy Inputs Sensitivity Analysis (Short
profit when the LX1_Band_Num and LX2_Band_Num                                                            Exits)
input values change. The back-tested net profit is very stable
and the surface chart is very flat compared to those in
previously discussed sensitivity analysis charts. The chosen
default values for the two inputs are not peak values but are
near the center of the back end of the chart where the LX1_
Band_Num input is 2 and the LX2_Band_Num is 2.5.
In a similar fashion, figure 6 illustrates the impact on the
back-tested net profit when the SX1_Band_Num and SX2_
Band_Num input values change. The back-tested net profit
is again very stable and the surface chart is very flat. The
chosen default values for the two inputs are not peak values
but are on the left side of the front end of the chart where
both the SX1_Band_Num input and the SX2_Band_Num
input are 2.5. In this particular case, keeping the strategy
inputs values the same seems to provide enhanced risk-ad-
justed metrics for the symbol traded (i.e., SPY).
14 | STRATEGY CONCEPTS CLUB
