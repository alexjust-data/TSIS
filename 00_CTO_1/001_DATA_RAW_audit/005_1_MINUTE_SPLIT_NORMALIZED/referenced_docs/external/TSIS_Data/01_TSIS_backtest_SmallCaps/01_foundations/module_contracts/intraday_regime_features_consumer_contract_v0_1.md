# Intraday Regime Features Consumer Contract `v0_1`

## 1. Rol

Este documento define el primer consumidor intradia recomendado para `1m_split_normalized`.

No define todavia:

- el modelo final de entrada/salida;
- el simulador de ejecucion;
- ni una policy RL.

Define una capa intermedia y mas limpia:

- un generador de `intraday_regime_features`

su objetivo es describir el estado relevante del activo cuando el pipeline necesita comparar la sesion actual con sesiones anteriores sin dejar que splits o reverse splits se hagan pasar por alpha.

## 1.1 Regla de fase actual

Este contrato no abre todavia una fase general de:

- feature engineering de estrategia;
- research de alpha;
- ni modelado rico de regimen.

En la fase actual, `intraday_regime_features v0_1` debe entenderse solo como:

- un consumidor minimo de validacion semantica de `1m_split_normalized`

Su mision actual no es maximizar poder predictivo.

Su mision actual es demostrar que:

- un uso downstream sensible a comparaciones entre sesiones deja de contaminarse por shocks mecanicos de split cuando usa la vista correcta.

Toda ampliacion futura de familias de features debe tratarse, por ahora, como:

- backlog diferido de fase posterior

y no como parte de la auditoria actual de data.

## 2. Consumidor

Consumidor:

- generador de features de regimen intradia

Clase de consumidor:

- `ml_primary`
- `research_only`
- y mas adelante `backtest_core` como soporte de evaluacion contextual

## 3. Por que este es el primer consumidor correcto de `1m_split_normalized`

Es el primer consumidor correcto porque:

- usa exactamente la parte de `1m_split_normalized` que mas importa validar;
- necesita comparar sesiones distintas;
- y es mucho mas facil de auditar que un `execution_simulator` completo.

El error metodologico que evita es:

- aprender gaps falsos;
- aprender shocks de precio falsos;
- o confundir cambios mecanicos de escala con cambio real de regimen.

## 3.2 Limite del contrato actual

La justificacion metodologica de este consumidor no autoriza, por si sola, a abrir ya:

- un set amplio de features de premarket;
- taxonomias ricas de apertura;
- perfiles sofisticados de volumen;
- ni investigacion de edge o ML final.

Autoriza solo esto:

- un conjunto minimo de variables cross-session e intrasesion necesarias para auditar que la capa de precio corrige exactamente el tipo de error que prometia corregir.

## 3.1 Justificacion metodologica explicita

La decision no se apoya solo en intuicion arquitectonica.

Se apoya en cuatro bloques metodologicos.

### A. No mezclar retornos entre sesiones con precios sin corregir corporate actions

Este es el bloque mas fuerte.

Felton y Jain muestran que calcular retornos historicos sin ajustar bien splits y dividendos produce retornos erroneos y puede contaminar inferencia y decisiones cuantitativas.

Fuente:

- Felton, Jain, *True Returns: Adjusting Stock Prices for Cash Dividends and Stock Splits*
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3354728

Consecuencia para este proyecto:

- cualquier feature que cruce sesiones y use cambios de precio debe evitar saltos mecanicos;
- por eso `1m_split_normalized` tiene sentido como input contractual del consumidor.

### B. La informacion intradia si sirve para medir estado y regimen

Andersen, Bollerslev, Diebold y Labys establecen la logica de usar datos de alta frecuencia para construir medidas de volatilidad realizada y modelar el estado del activo mejor que con solo datos diarios.

Fuentes:

- *Modeling and Forecasting Realized Volatility*
  - https://www.nber.org/papers/w8160
- *Realized Return Volatility, Asset Pricing, and Risk Management*
  - https://www.nber.org/reporter/2006number4/realized-return-volatility-asset-pricing-and-risk-management

Consecuencia para este proyecto:

- una capa de features intradia de estado y regimen tiene base metodologica;
- volatilidad y rango intradia agregados son variables naturales de primera promocion.

### C. Hay predictibilidad intradia y no todo vive en el ultimo tick

Huddleston, Liu y Stentoft muestran predictibilidad intradia con ML en horizontes cortos.

Fuente:

- *Intraday Market Predictability: A Machine Learning Approach*
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3726765

Heston, Korajczyk y Sadka documentan patrones intradia persistentes y muestran que volumen, order imbalance, volatilidad y spreads contienen estructura informativa.

Fuente:

- *Intraday Patterns in the Cross-section of Stock Returns*
  - https://arxiv.org/abs/1005.3535

Consecuencia para este proyecto:

- no es absurdo construir una capa previa de contexto intradia;
- tiene sentido que ML no mire solo la barra actual, sino el estado reciente y entre sesiones.

### D. El gap overnight y la forma del volumen intradia importan

Perreten y Wallmeier muestran que patrones intradia de volumen predicen retornos overnight; en su trabajo el `shape` del volumen y el gap son informativos.

Fuente:

- *Overnight Returns and the Timing of Trading Volume*
  - https://papers.ssrn.com/sol3/Delivery.cfm/5004991.pdf?abstractid=5004991&mirid=1

Consecuencia para este proyecto:

- variables como `gap_open_vs_prev_close`, volumen relativo de apertura y forma de actividad tienen respaldo metodologico;
- por tanto una capa de `intraday_regime_features` es un primer consumidor razonable de `1m_split_normalized`.

## 4. Inputs obligatorios

Inputs obligatorios:

- `D:\ohlcv_1m`
- `E:\TSIS\data\ohlcv_1m_split_normalized`

Inputs auxiliares esperables:

- `daily_adjusted` cuando haya que alinear contexto diario lento;
- halts o eventos, si mas adelante la policy de regimen lo exige.

## 5. Regla central de semantica

No toda feature debe usar la misma vista.

La regla correcta es:

- si la feature cruza sesiones y depende de comparabilidad de escala:
  - usar `1m_split_normalized`
- si la feature describe solo la sesion local observada:
  - usar `1m raw`

## 6. Variables que deben usar `1m_split_normalized`

Estas variables deben usar `1m_split_normalized` porque comparan sesiones distintas y, sin esa capa, pueden absorber corporate actions como si fueran movimiento real:

- `gap_open_vs_prev_close`
- `premarket_move_vs_prev_close`
- `open_vs_prev_session_close`
- `open_vs_prev_session_high`
- `open_vs_prev_session_low`
- `multi_session_return_n`
- `distance_to_prev_day_range`
- `distance_to_n_day_extremes`
- `multi_session_range_expansion`
- `realized_vol_prev_n_sessions`
- `overnight_gap_zscore`

## 7. Variables que deben seguir usando `1m raw`

Estas variables deben seguir usando `1m raw` porque describen la verdad local observada del mercado dentro de la sesion:

- retorno barra a barra dentro de la sesion
- rango de la barra actual
- volumen de la barra actual
- VWAP intrasesion acumulado
- opening drive de la sesion actual
- pullback desde el high de la sesion actual
- compresion o expansion estrictamente intrasesion

## 8. Variables que quedan para una fase posterior

Estas variables no deben entrar en esta primera promocion, porque dependen mas de `quotes_raw` y `trades_raw` que de `1m_split_normalized`:

- spread
- order imbalance
- quote instability
- crossed states
- signed trade flow
- odd-lot microstructure fina
- tape integrity

## 9. Que representa el output

El output no representa:

- una recomendacion de ejecucion final;
- ni una orden;
- ni una politica de entrada/salida.

Representa:

- el estado cuantitativo del activo y su contexto intradia entre sesiones

para que luego un modelo o regla superior pueda decidir:

- si una familia de estrategias tiene derecho a activarse;
- si el activo llega demasiado extendido;
- si el gap es real o mecanico;
- o si el contexto previo favorece o no el setup actual.

## 10. Para que sirve

Sirve para:

- ML de regimen intradia;
- research de contexto pretrade;
- filtros de activacion de estrategia;
- y soporte a backtests intradia que usen memoria de varias sesiones.

## 11. Para que no sirve

No sirve directamente para:

- modelar slippage fino;
- simular fills;
- reconstruir el libro;
- ni decidir ejecucion microestructural de segundo nivel.

## 12. Condicion minima de implementacion

Para declarar este consumidor como conectado de verdad deben existir:

- una lectura real de `1m_split_normalized`;
- una lectura real de `1m raw`;
- una separacion explicita entre features cross-session y features intrasesion;
- y una prueba de que las features expuestas a splits no se calculan sobre raw.

## 12.1 Condicion minima de prudencia

Mientras este consumidor siga en fase de auditoria de data, no debe crecer por ambicion funcional.

La regla correcta es:

- primero demostrar que la capa valida el problema semantico;
- despues cerrar el piloto;
- y solo mas adelante promover nuevas familias de features como parte de research o backtest contextual.

El backlog diferido de familias futuras vive en:

- `01_foundations/module_contracts/intraday_regime_features_deferred_families_v0_1.md`

## 13. Veredicto final

Este consumidor es el primer aterrizaje correcto de `1m_split_normalized` porque:

- aprovecha su semantica exacta;
- evita el error mas peligroso para ML intradia que cruza sesiones;
- y no obliga todavia a abrir toda la complejidad de ejecucion, RL o simulacion microestructural completa.

## 14. Referencias metodologicas

- Felton, Jain, *True Returns: Adjusting Stock Prices for Cash Dividends and Stock Splits*
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3354728
- Andersen, Bollerslev, Diebold, Labys, *Modeling and Forecasting Realized Volatility*
  - https://www.nber.org/papers/w8160
- Andersen, Bollerslev, Diebold, *Realized Return Volatility, Asset Pricing, and Risk Management*
  - https://www.nber.org/reporter/2006number4/realized-return-volatility-asset-pricing-and-risk-management
- Huddleston, Liu, Stentoft, *Intraday Market Predictability: A Machine Learning Approach*
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3726765
- Heston, Korajczyk, Sadka, *Intraday Patterns in the Cross-section of Stock Returns*
  - https://arxiv.org/abs/1005.3535
- Perreten, Wallmeier, *Overnight Returns and the Timing of Trading Volume*
  - https://papers.ssrn.com/sol3/Delivery.cfm/5004991.pdf?abstractid=5004991&mirid=1
