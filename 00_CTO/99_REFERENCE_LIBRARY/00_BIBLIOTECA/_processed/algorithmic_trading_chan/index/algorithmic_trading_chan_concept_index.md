# Concept Index - Algorithmic Trading - Ernest P. Chan

Indice orientado a agentes. Las paginas son aproximadas segun la extraccion local.

## Menu

- [Backtesting y sesgos](#backtesting-y-sesgos)
- [Mean reversion](#mean-reversion)
- [Acciones, ETFs y small caps](#acciones-etfs-y-small-caps)
- [Futuros, divisas y contratos](#futuros-divisas-y-contratos)
- [Momentum](#momentum)
- [Riesgo](#riesgo)
- [Uso recomendado en TSIS](#uso-recomendado-en-tsis)

## Backtesting y sesgos

| Concepto | Paginas | Relevancia TSIS |
|---|---:|---|
| Backtesting como simulacion implementable | 19-21 | Define que un backtest debe poder conectarse con ejecucion automatizada |
| Equivalencia backtest/live | 20-22, 43-56 | Apoya el diseno de mismo Strategy Core con distintos adapters |
| Look-ahead bias | 21-22 | Obliga a timestamp decisional y estado observable |
| Data-snooping bias | 22-25 | Obliga a registrar variantes, parametros y seleccion |
| Out-of-sample y walk-forward | 24-25 | Base para separar desarrollo, validacion y test bloqueado |
| Simplicidad del modelo | 22-25 | Favorece estrategias lineales y pocas reglas para v0.1 |
| Splits y dividendos | 25-26 | Necesario en Data Foundation y ajuste point-in-time |
| Survivorship bias | 26-29 | Critico para small caps y delistings |
| Short-sale constraints | 20, 107-108 | Requiere borrow/shortability model |
| Primary vs consolidated prices | 29-31 | Afecta ejecucion simulada y comparacion con broker |
| Hipotesis estadistica | 34-40 | Base para reportar significancia sin exagerar |
| Regime shift | 42-43 | Requiere robustez temporal y analisis por regimen |
| Seleccion de plataforma | 43-56 | Motiva separacion entre motor, adapters y ejecucion real |

## Mean reversion

| Concepto | Paginas | Relevancia TSIS |
|---|---:|---|
| Estacionariedad | 57-64 | Requisito de research antes de estrategias MR |
| ADF test | 60-64 | Validacion inicial de series/spreads |
| Hurst exponent | 64-66 | Diagnostico de persistencia o reversion |
| Variance ratio | 66-68 | Test de random walk |
| Half-life | 64-66 | Lookback defendible sin optimizacion ciega |
| Cointegracion | 68-78 | Base para pares y baskets |
| CADF | 68-72 | Cointegracion de pares |
| Johansen | 72-78 | Cointegracion multiactivo |
| Spreads, log spreads y ratios | 82-88 | Define feature construction y units |
| Bollinger Bands | 88-90 | Regla practica de entrada/salida |
| Scaling-in | 90-92 | Riesgo por parametros y sizing progresivo |
| Kalman filter | 92-100 | Hedge ratio dinamico y modelo adaptativo |
| Errores de datos | 101-104 | Threshold strategies necesitan filtros de calidad |

## Acciones, ETFs y small caps

| Concepto | Paginas | Relevancia TSIS |
|---|---:|---|
| Dificultad de pares de acciones | 107-109 | Riesgo de ruptura por cambios idiosincraticos |
| Liquidez y NBBO pequeno | 107-109 | Slippage y partial fills importan |
| ETFs y triplets | 109-110 | Relaciones economicas mas estables que pares sueltos |
| Diagnostico de ruptura de cointegracion | 109-110 | Metodo cientifico: explicar fallo y anadir variable |
| Buy-on-gap intraday | 110-114 | Muy relevante para gaps de small caps |
| ETF/component arbitrage | 114-120 | Ejemplo de basket y tracking |
| Cross-sectional mean reversion | 120-124 | Ranking/portfolio construction separado de senal |
| Historical index membership | 114-124 | Point-in-time universe |
| Primary exchange data | 107-124 | Evita precios no ejecutables |

## Futuros, divisas y contratos

| Concepto | Paginas | Relevancia TSIS |
|---|---:|---|
| Cross-rates FX | 126-131 | Leccion de denominacion y conversion de P&L |
| Rollover interest | 131-133 | Costes/beneficios no contenidos en precio spot |
| Futures calendar spreads | 133-145 | Contrato economico explicito |
| Roll return | 133-145 | Diferencia entre spot return y total return |
| Intermarket spreads | 145-150 | Construccion de spreads y datos continuos |

## Momentum

| Concepto | Paginas | Relevancia TSIS |
|---|---:|---|
| Time-series momentum | 151-159 | Senal por retorno pasado del propio activo |
| Cross-sectional momentum | 162-169 | Ranking entre activos y portfolio construction |
| Causas economicas del momentum | 151-155 | Evita optimizar patrones sin explicacion |
| Non-overlapping tests | 152-155 | Evita inflar significancia |
| Roll-return momentum | 157-161 | Senal economica alternativa |
| Opening gap strategy | 173-175 | Relevante para scanner intraday |
| News-driven momentum / PEAD | 175-181 | Eventos con timestamp y ciclo de vida |
| Leveraged ETF close momentum | 181-182 | Ejecucion dependiente de timing intraday |
| Order book imbalance | 182-186 | Microestructura y short-horizon predictability |

## Riesgo

| Concepto | Paginas | Relevancia TSIS |
|---|---:|---|
| Kelly criterion | 188-197 | Sizing como problema de crecimiento esperado |
| Half-Kelly | 188-197 | Regla conservadora practica |
| Kelly multiestrategia | 192-197 | Asignacion usando covarianzas |
| Monte Carlo de retornos | 194-197 | Riesgo de distribuciones no gaussianas |
| CPPI | 198-200 | Control de drawdown y retirada de capital |
| Stop loss | 200-202 | Depende de naturaleza MR o momentum |
| Risk indicators | 202-204 | Potenciales filtros, alto riesgo de data snooping |

## Uso recomendado en TSIS

| Tarea de agente | Secciones a consultar |
|---|---|
| Disenar contrato de backtest reproducible | Cap. 1, especialmente sesgos y plataforma |
| Revisar estrategia de gaps small caps | Cap. 4 buy-on-gap y Cap. 7 opening/news momentum |
| Disenar filtros de calidad de datos | Cap. 1 y Cap. 3 data errors |
| Crear prototipo mean reversion | Cap. 2, 3 y 4 |
| Crear prototipo momentum | Cap. 6 y 7 |
| Definir sizing inicial | Cap. 8 Kelly/half-Kelly |
| Definir stop logic | Cap. 8 stop loss, distinguiendo MR vs momentum |
| Revisar peligro de sobreajuste | Cap. 1 data-snooping y Cap. 8 risk indicators |

