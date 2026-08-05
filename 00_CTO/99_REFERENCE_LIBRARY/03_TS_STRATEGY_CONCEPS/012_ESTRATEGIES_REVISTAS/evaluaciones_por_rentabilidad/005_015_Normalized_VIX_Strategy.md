# Evaluación de estrategia: Normalized VIX Strategy

## 1) Identificación y rendimiento

- **ID:** 005
- **Archivo PDF:** SCC Issue 8 Aug 2015.pdf
- **Issue:** 8 (Aug 2015)
- **Revista:** Strategy Concepts (TradeStation)
- **Autor:** Stanley Dash, CMT
- **Mercado:** Futuros sobre índices y ETFs
- **Horizonte:** No detectado

---

- **Profit Factor = No encontrado** (se indica como alto para esta familia).
- **Percent Profitable = No encontrado** (en el contexto de esta estrategia se califica como "algo alto" para este tipo de estrategia).
- **RINA Index = No encontrado** (alto, influido por baja exposición al mercado).
- **Comentario explícito:** se observan caídas pequeños (~5%), pero rendimiento cíclico y periodos de flat.

## 2) Tesis de trading y edge

Se usa la puntuación típica geométrica normalizada del VIX (`Geometric Standard Score`) para convertir el índice a una serie con escala comparable. La estrategia abre posiciones en contra de la tendencia predominante cuando ese valor supera/baja umbrales.

El núcleo permite identificar condiciones de estrés o complacencia en volatilidad y tratar entradas de reversión de corto plazo cuando el Z-score de VIX se sitúa en extremos.

## 3) Contexto y reglas

- **Tipo de activo / mercado:** Normalized VIX Strategy
- **Mercados indicados:** Futuros sobre índices y ETFs
- **Horizonte:** No detectado
- **Estilo de estrategia:** Reversión a la media

## 4) Datos y backtest

- Se aplica sobre el contrato continuo del E-mini S&P 500 (`@ES=107XN`) en barras diarias.
- También se puede trasladar a otros símbolos (p. ej., SPY) manteniendo los principios.
- Parámetros base: `GSS_High=1.5`, `GSS_Low=-1.5`.
- Resultados destacados:
  - Total Number of Trades = 143 (84 largos, 59 cortos).
  - Ratio ganancia/pérdida promedio = 1.41.
  - Percent of Time in the Market = 5.74%.
  - Drawdown semanal máximo alrededor de 12%; Sharpe 0.42 y K-Ratio 6.10.
- Recomendación de mejoras: añadir control de tendencia adicional para entradas cortas y comprobar estados consecutivos del VIX (por ejemplo filtros de niveles altos/bajos).

## 6) Implementación

- Data secundaria obligatoria: `$VIX.X` con cálculo de score geométrico.
- Entradas de estudio:
  - Largo: media geométrica estandarizada > `1.5`, sin señal de largo en las últimas 4 barras.
  - Corto: media geométrica estandarizada < `-1.5`, sin señal de corto en las últimas 4 barras.
- Salidas: cierre al mercado tras 1 barra de apertura.
- El sistema de barras diarias y el horario de sesión del ES se debe ajustar a 6 p.m. ET (apertura diaria del contrato).





