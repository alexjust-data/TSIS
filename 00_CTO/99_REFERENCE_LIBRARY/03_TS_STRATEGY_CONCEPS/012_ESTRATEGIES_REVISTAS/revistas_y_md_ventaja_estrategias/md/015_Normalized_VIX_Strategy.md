# 015 - Normalized VIX Strategy

## Metadatos
- **Numero de archivo:** 015
- **Revista:** Strategy Concepts (TradeStation)
- **Archivo PDF:** SCC Issue 8 Aug 2015.pdf
- **Issue:** 8 (Aug 2015)
- **Página TOC:** 2
- **Línea TOC:** 14
- **Carpeta de origen:** G:\03_SersansSistemas_algoritmico\02_practice\02_workshops\23-practice-13\docs\STRATEGY CONCEPTS\STRATEGY CONCEPTS\2015-08
- **Autor:** Stanley Dash, CMT
- **Nombre de estrategia:** Normalized VIX Strategy

## Contexto operativo
- **Tipo de activo / mercado:** Normalized VIX Strategy
- **Mercados indicados:** Stock-index futures and ETFs
- **Horizonte:** No detectado
- **Estilo de estrategia:** Mean reversion

## Resumen técnico
is normalized using a rolling geometric standard score                         If the normalized VIX reading (i.e., the geometric approach. In addition to the normalization of the index, the              standard score) is above a specified limit, a long entry is the opposite direction of the prevailing trend. The custom                the normalized VIX reading is below a specified level. This provide a fresh perspective on utilizing the VIX index in                 VIX. Also, in order to limit whipsaws, a trade entry is only of bars. The TSL:Normalized VIX indicator is provided to help The TSL:Normalized VIX strategy consists of multiple                      set as listed below. elements and requires a secondary data series (i.e., VIX data) to function properly. The necessary VIX data                          Input                 Default                   Description can be inserted in a TradeStation chart by using the                                                         Geometric standard score value that is symbol $VIX.X. The core element of the strategy is the                      GSS_High                1.5      considered high. normalization of the VIX data using a rolling geometric                                                      Geometric standard score value that is

## Reglas clave
The TSL:Normalized VIX strategy was applied to the
E-mini S&P 500 Continuous Contract (@ES=107XN) using
daily bars. However, the strategy could be modified to be
used on other securities (e.g., SPY) and bar intervals using
the same basic principles. The detailed strategy rules are
listed below.
Long Entries
moving average, the geometric standard score is above
1.5, and no long signal has been generated for the last 4
bars, buy on a market order on the next bar.
Short Entries
moving average, the geometric standard score is below
-1.5, and no short signal has been generated for the last
4 bars, sell short on a market order on the next bar.
Exits
the open of the first bar after entry.
Note: Please keep in mind that for the ES, entries and
exits occur at 6 p.m. ET, which is the opening time of the         All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily
daily session for the futures contract.                            indicative of future results.

## Inputs
No detectado automáticamente.

## Notas de performance / backtest
REPORT HIGHLIGHTS                                                  in the back-tested period, as the worst drawn-down in the
period was only about $2,000. The stop loss is included as a
The strategy was tested on the ES using the custom                 safety net measure.
continuous futures contract (@ES=107XN), which is the
closest replication to the CME roll. The custom continuous         Total Number of Trades = 143
contract utilizes no back adjustment and the rollover trigger is
 e total trades are unevenly split between long trades (84)
7 trading days prior to the expiration date. The problem when
and short trades (59). Testing revealed that, overall, the
using the @ES adjusted continuous contract is that some
strategy worked better on the long side versus the short
theoretical trades would not have occurred at the prices listed
side.
in the back-test. As a reminder, the main purpose behind
any continuous contract is to create a longer history than is      Ratio Average Win to Average Loss = 1.41
possible using data from just one delivery month; however,         u The average winning trade is about 140% of the average
the method of construction of the continuous contract series          losing trade. Also, the largest losing trade is much smaller
should be considered when back-testing.                               than the largest winning trade.
Percent of Time in the Market = 5.74%
BACK-TESTING SETTINGS
 e time in the market is very small, which makes the strategy
Initial Capital             $10,000
results that much more impressive. The Sharpe ratio registered
Trade Size                  1 Contract                               0.42 and the K-Ratio came out at 6.10, which are very good.
Commissions                 $2.36 per side per contract
The equity curve looks very impressive for the back-tested
History                     10 years ending 6/30/15
period, especially considering that the overall market experi-
Bar Interval                Daily                                 enced much turmoil in the analyzed period (e.g., 2008) when
Stop Loss                   $2,500                                the VIX index experienced dramatic fluctuations. The back-
STRATEGY CONCEPTS CLUB                 |5
Figure 4: Strategy Performance Report – Equity Curve Detailed                                            Figure 5: TSL:Normalized VIX Strategy Inputs Sensitivity Analysis
All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily
indicative of future results.
only helps address these hurdles to a limited extent. For
instance, when the VIX is trending at high levels or at
very low levels, a series of trade signals is generated.
All performance results are hypothetical. Past performance, actual or hypothetical, is not necessarily   Checking for recent trade signals helps by creating a
indicative of future results.                                                                            delay for reentry, but some losing streaks remain. A more
efficient way of checking to see if the VIX is trending may
tested period also includes different types of markets (i.e., bull                                       be explored. Ideas could include checking for consecutive
and bear markets as well as low- and high-volatility markets).                                           VIX readings above or below certain levels.
The experienced volatility of the equity curve translated to a
maximum weekly drawdown of only 12%.                                                                          Another possible area of improvements has to do with
the short trades taken by the strategy. It is no secret that
Instead of analyzing one strategy input in isolation, data                                          the VIX index works better on the long side. As discussed
from TradeStation’s Strategy Optimization Reports can be                                                 in the Strategy Performance section, the limited short
utilized in Microsoft Excel to perform sensitivity analysis                                              trades in the back-test were not as good as the long trades.
between two strategy inputs at the same time by creating a                                               From the testing performed on the custom strategy, it is
3-D chart. For instance, an exhaustive Strategy Optimization                                             possible to add value by including short trades, but this
Report can be run on the GSS_High and GSS_Low strategy                                                   usually comes with added volatility in the performance.
inputs, and the resulting data can be used to create a surface                                           The reader may simply want to turn short trades off
chart in Excel.                                                                                          entirely in the Format Strategy dialog. The reader may also
Figure 5 illustrates the impact on the back-tested net                                              want to consider exploring additional rules and conditions
profit when the GSS_High and GSS_Low input values change.                                                to initiate short trades. Interesting results were found by
The back-tested net profit is fairly stable in the middle portion                                        using Bollinger Bands on the VIX data. This idea may be
of the surface. The chosen default values for the two inputs                                             explored in the future.
were selected in this area (when the GSS_High input is 1.5 and
the GSS_Low is -1.5). While these are not peak values, the net                                           A special thank you goes out to Dr. Rainford Knight from
profit doesn’t drop as fast as it does beyond the peak values in                                         the Department of Finance at Florida Atlantic University
the back portion of the surface.                                                                         for his guidance on log-normal distributions.
SUGGESTIONS FOR IMPROVEMENT                                                                                  Frederic Palmliden, CMT, is Senior Quantitative Analyst at
TradeStation. As part of the TradeStation Labs team, he designs
The normalization of the VIX data using the geometric                                                        custom strategies and indicators and related educational content
standard score approach offers interesting trading appli-                                                    for TradeStation publications. In addition to being a Chartered
cation ideas. The process helps deal with scaling issues                                                     Market Technician (CMT), Frederic is trilingual and has over 10 years’
and provides context to the current VIX value. However,                                                      experience in the financial services industry, ranging from research and
a number of challenges remain, and the custom strategy                                                       asset allocation strategies to proprietary trading.
6 | STRATEGY CONCEPTS CLUB
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
