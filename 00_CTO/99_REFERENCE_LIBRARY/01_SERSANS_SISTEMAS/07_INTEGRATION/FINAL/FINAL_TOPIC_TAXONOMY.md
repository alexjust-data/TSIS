# Taxonomía final de Topics

Estado: `CLOSED_FOR_SERSAN_02_17`

## KR-001 — Data, sesiones y series continuas

- `TOPIC-0001` — **Continuous_Charts**: Construcción de series continuas y políticas de rollover/ajuste.
- `TOPIC-0005` — **Futures_Rollover**: Expiración, contrato front y elección del punto de rollover.
- `TOPIC-0006` — **Price_Adjustment_Policies**: Forward/backward, diferencia/ratio, tick y corporate actions.
- `TOPIC-0011` — **Forex_Data_Quality**: Fuentes, calidad, horarios y limitaciones de datos Forex.
- `TOPIC-0015` — **Multidata_Alignment**: Alineación temporal de instrumentos y filtros cross-asset.
- `TOPIC-P03-001` — **Daily Bars from Intraday Data**: Sesiones, settle y construcción de barras de 1.440 minutos

## KR-002 — Especificación causal de estrategias

- `TOPIC-0007` — **Strategy_Specification**: Separación de setup, entradas, salidas, parámetros y costes.
- `TOPIC-0008` — **Entry_Evaluation**: Prueba rápida de una entrada con payoff aproximadamente unitario.
- `TOPIC-0013` — **Portfolio_Risk_Overlays**: Stop y take profit globales de portfolio.
- `TOPIC-P03-003` — **Trend-Following versus Counter-Trend Character**: Psicología, exposición overnight y diversificación por tipo de estrategia
- `TOPIC-P03-004` — **Controlled Strategy Inputs**: Inputs de configuración, análisis y optimización
- `TOPIC-P03-010` — **Re-entry Control**: BarsSinceExit y separación mínima entre operaciones

## KR-003 — Entradas Donchian y semántica de ruptura

- `TOPIC-0002` — **Donchian**: Especificación, implementación y evaluación inicial del sistema Donchian.
- `TOPIC-P03-002` — **Donchian Foundations and Source Discipline**: Regla de cuatro semanas, fuentes originales y significado del canal
- `TOPIC-P03-005` — **Breakout Entry Semantics**: Close/High/Low, barra anterior, orden siguiente y variantes de ruptura
- `TOPIC-P03-006` — **Entry Setup Evaluation**: Evaluación aislada con salidas simétricas y límites de la inferencia
- `TOPIC-P04-003` — **Donchian Close-Channel Specification**: Ruptura causal de máximos de cierres y entrada en la barra siguiente.

## KR-004 — Salidas, trailing y dependencia del camino

- `TOPIC-0074` — **ATR_Stop_Implementation**: Escala, BigPointValue y verificación de stops.
- `TOPIC-P03-008` — **Trend Exit Families**: Media, canal opuesto, stop, profit target, trailing y tiempo
- `TOPIC-P04-004` — **Pure Trend Following Exit Design**: Trailing porcentual como salida autosuficiente de un tendencial puro.
- `TOPIC-P04-015` — **Trailing Stop Path Risk**: Activación, gaps, acoplamiento, devolución de beneficio y whipsaw.

## KR-005 — Position sizing y control de exposición

- `TOPIC-P03-007` — **Exposure Normalization and Position Sizing**: Tamaño fijo frente a exposición nominal dinámica
- `TOPIC-P05-011` — **Improvement Paths and Exposure Control**: None
- `TOPIC-P05-015` — **Turtle Position Management**: None

## KR-006 — Métricas y evaluación de performance

- `TOPIC-0003` — **Performance_Evaluation**: Esperanza, payoff, métricas, informes, curva y drawdown.
- `TOPIC-P04-009` — **Objective-Function Plurality**: Net Profit, drawdown, Sharpe y Sortino como lentes no equivalentes.
- `TOPIC-P05-002` — **Sharpe and Sortino Semantics**: None
- `TOPIC-P05-005` — **Portfolio Metric Reconstruction**: None

## KR-007 — Benchmark y suficiencia económica

- `TOPIC-0009` — **Benchmarking**: Comparación contra activo e índice en términos retorno-riesgo.
- `TOPIC-P05-010` — **Benchmark and Economic Adequacy**: None

## KR-008 — Backtest y lectura a nivel portfolio

- `TOPIC-0010` — **Portfolio_Backtesting**: Grupos, capital, cartera, dimensionamiento y riesgo agregado.
- `TOPIC-P04-010` — **Portfolio-Level Backtest Interpretation**: Lectura agregada y desagregada por activo de resultados de cartera.

## KR-009 — Generalización transversal y universo PIT

- `TOPIC-0073` — **Timeframe_Representativeness**: Trades, años, regímenes y microestructura por timeframe.
- `TOPIC-P03-009` — **Cross-Asset Generalization**: Pruebas AAPL, XLK, XLF, META y QQQ
- `TOPIC-P04-001` — **Validation by Cross-Asset Aggregation**: Validación de sistemas de baja frecuencia mediante una cesta homogénea.
- `TOPIC-P04-011` — **Universe and Survivorship Bias**: Nasdaq-100 actual como sonda de lógica, no simulación PIT operable.

## KR-010 — Regímenes y filtros

- `TOPIC-0004` — **Market_Regimes**: Regímenes como filtros y riesgo de sobreajuste.
- `TOPIC-0014` — **Filter_Validation**: Actuación efectiva, muestra pre/post y grados de libertad.
- `TOPIC-0066` — **ADX_ATR_Comparability**: ADX, ATR porcentual y lectura por timeframe.
- `TOPIC-P03-011` — **Volatility Filtering**: ATR normalizado, contracción previa y sensibilidad por activo/lado
- `TOPIC-P03-013` — **Market Regime Framing**: Dirección × volatilidad, ADX/ATR/VIX y límites de identificación
- `TOPIC-P04-005` — **ATR Volatility Filter**: Filtro TrueRange frente a ATR previo y su evaluación instrumental.

## KR-011 — Optimización y estabilidad paramétrica

- `TOPIC-P03-012` — **Instrumental Optimization**: Optimización para mapas de sensibilidad, no solo selección del óptimo
- `TOPIC-P04-007` — **Exhaustive Parameter Search**: Diseño de cuatro optimizaciones y lectura de todas las combinaciones.
- `TOPIC-P04-008` — **Parameter Stability Surfaces**: Mesetas, valles, fronteras y sensibilidad en superficies 3D.
- `TOPIC-P05-006` — **Parameter Sensitivity and Optimization Surfaces**: None

## KR-012 — IS/OOS, holdouts y Walk Forward

- `TOPIC-0069` — **Walk_Forward_Sample_Constraints**: Cortes, tamaño muestral y regímenes.
- `TOPIC-P04-006` — **Experimental Design and Holdouts**: Partición IS/OOS, posible validación adicional y observación forward.
- `TOPIC-P05-004` — **Walk Forward as Stress Test**: None
- `TOPIC-P05-008` — **IS OOS and All-Data Reconciliation**: None

## KR-013 — Robustez, simplicidad y sobreoptimización

- `TOPIC-0012` — **BRaC_Robustness**: Build-Reveal-Compare, IS/OOS y tamaño de muestra.
- `TOPIC-P03-014` — **Strategy Simplicity and Degrees of Freedom**: Concepto previo, búsqueda dirigida y control de complejidad
- `TOPIC-P04-002` — **Methodological Pluralism**: BRaC, Walk Forward y otros métodos bajo significación y representatividad.
- `TOPIC-P04-016` — **Strategy Simplicity and Degrees of Freedom**: Cerrar el diseño antes de añadir ATR, salidas y filtros adicionales.
- `TOPIC-P05-016` — **Search Algorithms and Practitioner Judgment**: None

## KR-014 — Fidelidad de ejecución y costes

- `TOPIC-P04-012` — **Costs Slippage and Capital Allocation**: Comisión, tick de slippage, capital y exposición por instrumento.
- `TOPIC-P05-001` — **Intrabar Backtest Fidelity**: None
- `TOPIC-P05-012` — **Bid Ask Execution Fidelity**: None

## KR-015 — Asimetría long/short y tendencialidad

- `TOPIC-P04-014` — **Long-Short Structural Asymmetry**: Sesgo alcista de acciones y fragilidad del trend following corto.
- `TOPIC-P05-003` — **Directional Asymmetry and Asset Tendentiality**: None
- `TOPIC-P05-013` — **Short-Side Donchian Alternatives**: None

## KR-016 — Diversificación y correlación

- `TOPIC-0067` — **Portfolio_Equal_Weight**: Ponderación robusta y diversificación por estrategia.
- `TOPIC-0071` — **Apolo_Portfolio_Role**: Alfa y descorrelación como criterio de cartera.
- `TOPIC-P04-018` — **Diversification and Correlation**: Diversificación por activos/estrategias y correlación de retornos operativos.

## KR-017 — Herramientas, informes y límites operativos

- `TOPIC-0075` — **Visual_Strategy_Verification**: ShowMe y gráficos para comprobar activaciones.
- `TOPIC-P04-013` — **Portfolio Trader Capabilities and Limits**: Optimización, reglas de prioridad, forward/live y limitaciones analíticas.

## KR-018 — Selección multicriterio y decisión operativa

- `TOPIC-P04-017` — **Strategy Selection versus Idea Validation**: Separar evidencia de edge, elección de parámetros y decisión operativa.
- `TOPIC-P05-007` — **Multicriteria Candidate Ranking**: None
- `TOPIC-P05-009` — **Portfolio Maestro Final Selection**: None

## KR-019 — Sondas de edge y líneas de mejora

- `TOPIC-0068` — **Preliminary_Edge_Screening**: Descarte rápido antes de investigación costosa.
- `TOPIC-P05-014` — **Entry Edge Probes**: None

## KR-021 — ORB: rango de apertura y ruptura

- `TOPIC-0064` — **ORB_Strategy_Specification**: Definición causal, rango inicial, sesión, entradas y salidas ORB.

## KR-022 — Biblioteca de filtros y atribución marginal

- `TOPIC-0065` — **Reusable_Filter_Library**: Filtros conmutables, baseline sin filtro y atribución marginal.

## KR-023 — Revisión de superficies de optimización: Apolo

- `TOPIC-0070` — **Optimization_Surface_Review**: Mapas, mesetas, granularidad y selección auditada.

## KR-024 — Bollinger antitendencial: diario e intradía

- `TOPIC-0072` — **Bollinger_Mean_Reversion**: Sistema antitendencial, bandas, entradas y salidas.

## UNMAPPED

- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
- `None` — **None**: Sin alcance declarado
