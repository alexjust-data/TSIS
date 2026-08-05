# 026 - Regression Angles Strategy

## Metadatos
- **Numero de archivo:** 026
- **Revista:** Strategy Concepts (TradeStation)
- **Archivo PDF:** SCC Issue 13 Jan 2016.pdf
- **Issue:** 13 (Jan 2016)
- **Página TOC:** 9
- **Línea TOC:** 75
- **Carpeta de origen:** G:\03_SersansSistemas_algoritmico\02_practice\02_workshops\23-practice-13\docs\STRATEGY CONCEPTS\STRATEGY CONCEPTS\2016-01
- **Autor:** Stanley Dash, CMT
- **Nombre de estrategia:** Regression Angles Strategy

## Contexto operativo
- **Tipo de activo / mercado:** Regression Angles Strategy
- **Mercados indicados:** No detectado
- **Horizonte:** Swing trading
- **Estilo de estrategia:** Trend-following

## Resumen técnico
on the back-tested net profit when the                                               Figure 6: TSL:VWAP Bands Equity Curves with Different Values for the Signal_Band_Num Trail_Stop_Length and Signal_Band_Num                                                Strategy Input input values change. The back-tested net profit is fairly stable on a rounded mount formation. Notice that there is a severe drop in performance near the front right corner of the surface where both inputs are in the lower range of tested values. The chosen default values for the two inputs are not peak values but are near a flat portion of the rounded mount where the Trail_Stop_Length input is 22 and the

## Reglas clave
LRAngleBuySignal               0       generates a buy signal                The TSL:Regression Angles strategy has both entry and exit
rules based on the angle of a trailing regression line calcu-
Linear regression angle that
LRAngleSellSignal              0       generates a short signal              lated from the midpoint of each bar. A positive angle (rising
linear regression line) is bullish and a negative angle (falling
Number of bars’ linear regression     linear regression line) is bearish.
angles to monitor for exit signals;
ExitBarCount                   3       should be greater than or equal
to ExitBar_AnglesCounterTrend         Long Entries
Number of bars on which                 LRAngleBuySignal input value, then buy on the open of
linear regression angle shows
movement against the trend              the next bar.
ExitBar_AnglesCounterTrend     3       to generate an exit signal;
should be less than or equal to
ExitBarCount
STRATEGY CONCEPTS CLUB         | 11
Short Entries                                       Figure 3: Strategy Performance Report – Performance Summary Tab
crosses under the LRAngleSellSignal
input value, then sell short on the open
of the next bar.
Exits
the regression lines on a sequence of
bars show movement against the trend.
The angles of the regression lines of each
group of ExitBar_AnglesCounterTrend
bars are examined. If the angles of
ExitBarCount bars in the group are less
than the angle of the line one bar ago,
then exit long positions. If the angles
of ExitBarCount bars in the group are
greater than the angle of the line one bar
ago, then exit short positions.

## Inputs
No detectado automáticamente.

## Notas de performance / backtest
The results discussed here are based on
applying the Regression Angles strategy to
five years of 130-minute bars of SPY. Some
limited optimizations were done in search           All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily indicative of future results.
of value areas that tended to repeat, but the
results discussed here are not necessarily
Total Net Profit
optimal in themselves.
 ese figures show a good balance between the long and short sides.
Many of the other fields highlighted also reflect a reasonable balance in
BACK-TESTING SETTINGS
the results.
Trade Size          100 shares
Profit Factor
Commissions         $.01 per share
History             5 years ending 11/30/2015      u Although a profit factor in a higher range than this would be desirable,
symmetry between long and short results is again apparent.
Bar Interval        130 minutes
Total Number of Trades
Input                                      Value   u The number of trades is reasonable for a 5-year test of a swing-trading
LRLength                              10             strategy; approximately 60 signals per year.
LRAngleBuySignal                      2.25         Percent Profitable
LRAngleSellSignal                     -2.25        u This metric stands out positively for a trend-following approach. Although
ExitBarCount                          4              somewhat tilted to the long side, a win rate of 50% is a very good sign for a
trend-following strategy.
ExitBar_AnglesCounterTrend            4
12 | STRATEGY CONCEPTS CLUB
Figure 4: Strategy Performance
Report – Performance Graphs tab
- Equity Curve Line
All performance results are hypothetical. Past
performance, actual or hypothetical, is not
necessarily indicative of future results.
Ratio Avg. Win:Avg. Loss                                                              SUGGESTIONS FOR IMPROVEMENT
with the Percent Profitable described above. A healthy                             emergency stop. Nothing of that kind is included in this
win rate combined with a favorable win:loss ratio leads to                         back-test or in the strategy as written. Traders may want
positive expectancy.                                                               to add TradeStation-supplied stops such as Stop Loss and
Dollar Trailing.
Avg. Bars in Winning Trades and Avg. Bars in Losing
Trades                                                                                    The strategy makes no provision for reentry in the
for profitable trades than for losing trades. Profitable                           regression angles weaken prompting an exit from a
trades lasted about 4 days and losing trades were                                  long position, there is no reentry method should the
held about 2.5 days. Both results fit well into a swing-                           bullish trend resume. This is likely to result in missed
trading concept such as this.                                                      opportunities.
Readers interested in another interesting applica-
Percent of Time in the Market (not shown in figure 3)                                 tion of linear regression may want to read the Analysis
from 0 for entries (2.25 and -2.25 in the test above),                              Retracement Channel Indicator by Frederic Palmliden.
combined with a proactive exit built on continuous                                  The indicator associated with that paper is available in the
monitoring of the regression angles, were effective in                              TradingApp Store.
moderating the Percent of Time in the Market. This test
showed a reasonable 72.8% for this metric, a generally
acceptable value for a trend-following strategy.
Stanley Dash, CMT is Vice-president, Applied Technical Analysis, at TradeStation. He and his group support active and institutional traders with analytical tools
and education designed to help them become more effective traders.
His Wall Street career began in 1975 and includes time as an active floor trader at one of the leading U.S. futures and options exchanges. Mr. Dash has
lectured for the New York Institute of Finance and the Institute for Financial Markets. He is also a Chartered Market Technician and a member of the Market
Technicians Association, where he serves on the Editorial Board of the Association’s Journal of Technical Analysis.
STRATEGY CONCEPTS CLUB        | 13
Ready to expand your TradeStation
horizons with EasyLanguage®?
Creating your own indicators and strategies will give you
new perspectives on markets and on your trading.
TradeStation’s Client Training and Education Department has taught thousands of traders how to use EasyLanguage
and would like to count you among them. We can guide you through all the steps in creating indicators, ShowMe™
and PaintBar™ studies and trading strategies. And if you’re thinking “but I’m not a programmer,” well, most of the
thousands of people we’ve taught weren’t programmers either. But, like you, they were passionate about markets
and willing to spend a few hours working with us to learn.
You’ll be surprised by how quickly you can get up to speed and begin writing your own indicators and trading
strategies in EasyLanguage, and how this will open up a whole new world of market analysis.
Beginners Course                                                      Advanced Users Course
For the EasyLanguage beginner, the same course work can be            For advanced users, step up to the latest in EasyLanguage by
accessed LiveOnTheWeb and in a self-paced home study course.          incorporating objects in your studies and strategies. Here, too, the
same course work can be accessed LiveOnTheWeb and in a self-
EasyLanguage Boot Camp                                                paced home study course.
A two-day LiveOnTheWeb class
$249 SCC Member Price: $124.50                                        Implementing Objects in EasyLanguage
A two-day LiveOnTheWeb class
Register with promo code ELBC4SCC
$249 SCC Member Price: $124.50
Your instructor will guide you step by step through more than 30                  Register with promo code IOEL4SCC
