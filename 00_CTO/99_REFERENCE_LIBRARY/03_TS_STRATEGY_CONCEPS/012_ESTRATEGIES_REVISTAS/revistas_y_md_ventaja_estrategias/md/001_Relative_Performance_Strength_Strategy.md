# 001 - Relative Performance Strength Strategy

## Metadatos
- **Numero de archivo:** 001
- **Revista:** Strategy Concepts (TradeStation)
- **Archivo PDF:** SCC Issue 1 Jan 2015.pdf
- **Issue:** 1 (Jan 2015)
- **Página TOC:** 2
- **Línea TOC:** 71
- **Carpeta de origen:** G:\03_SersansSistemas_algoritmico\02_practice\02_workshops\23-practice-13\docs\STRATEGY CONCEPTS\STRATEGY CONCEPTS\2015-01
- **Autor:** Stanley Dash, CMT
- **Nombre de estrategia:** Relative Performance Strength Strategy

## Contexto operativo
- **Tipo de activo / mercado:** Relative Performance Strength Strategy
- **Mercados indicados:** Futures
- **Horizonte:** No detectado
- **Estilo de estrategia:** Trend following

## Resumen técnico
The Relative Performance Strength (RPS)         constructed by using the average RPS           the TSL:Relative Performance is a relative strength measure comparing        and the standard deviation of the RPS.         Strength Strategy the percentage moves – rather than the          The look-back lengths for the RPS, and prices – of two highly correlated securities.   the average RPS, as well as the standard The strategy compares the current               deviation and the number of standard reading of the RPS to the historical band       deviations to be used around the average to generate trading signals. The current        RPS, are specified in the strategy inputs. reading between the two securities is               As an example, figure 2 shows the obtained by calculating the percentage          historical RPS band using blue lines for the moves for both securities, then dividing        upper and lower bands. The red line is the the percentage move of the traded security      RPS. The average RPS is not shown in the by the percentage move of the second            graphic, but would be in the center of the

## Reglas clave
No detectado automáticamente.

## Inputs
Input          Default                                           Description
Length           7       Look-back length for the securities’ percentage returns.
AvgLength        15      Look-back length for the average RPS calculation.
StdDevLength    250      Look-back length for the RPS standard deviation.
StdDevNum       0.75     Number of standard deviations to be used with the average RPS to create the historical band.

Note: The default input values were found by strategy testing optimization. Applying the strategy to
other securities would likely require adjustments to the input values.
Short Entry                                                                             cases, V would have outperformed MA for the last seven
If the RPS is higher than the top band or lower than the                                trading days and a decline would be expected in the next
lower band, the RPS is not trending and the percentage                                  trading session.
move of the tradable security is greater than that of the
second security, then sell short next bar at market.                                    STRATEGY PERFORMANCE
Exits                                                                                   REPORT HIGHLIGHTS
uE xit out of all positions on the open of the next bar.

## Notas de performance / backtest
No detectado automáticamente.
