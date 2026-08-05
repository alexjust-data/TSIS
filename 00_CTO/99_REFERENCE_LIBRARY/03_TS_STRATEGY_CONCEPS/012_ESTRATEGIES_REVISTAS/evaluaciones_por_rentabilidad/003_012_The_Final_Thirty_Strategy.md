# Evaluación de estrategia: The Final Thirty Strategy

## 1) Identificación y rendimiento

- **ID:** 003
- **Archivo PDF:** SCC Issue 6 Jun 2015.pdf
- **Issue:** 6 (Jun 2015)
- **Revista:** Strategy Concepts (TradeStation)
- **Autor:** Stanley Dash, CMT
- **Mercado:** ETFs de índices bursátiles amplios
- **Horizonte:** No detectado

---

- **Profit Factor = 1.34** (se indica como alto para esta familia).
- **Percent Profitable = No encontrado** (en el contexto de esta estrategia se califica como "algo alto" para este tipo de estrategia).
- **RINA Index = 92.70** (alto, influido por baja exposición al mercado).
- **Comentario explícito:** se observan caídas pequeños (~5%), pero rendimiento cíclico y periodos de flat.

## 2) Tesis de trading y edge

Esta estrategia adapta TSL:Asymmetric Channel Breakout para trabajar sólo un lado del mercado (largo o corto), combinando reglas de seguimiento de tendencia y de reversión a la media dentro del canal.

El filtro principal usa el cambio porcentual del precio en las primeras horas de sesión para validar la dirección y la calidad de la ruptura. El objetivo es mantener la señal útil del canal asimétrico evitando sobre-operar en tramos sin dirección.

## 3) Contexto y reglas

- **Tipo de activo / mercado:** The Final Thirty Strategy
- **Mercados indicados:** ETFs de índices bursátiles amplios
- **Horizonte:** No detectado
- **Estilo de estrategia:** Seguimiento de tendencia

## 4) Datos y backtest

- Instrumento base: SPY (SPDR S&P 500 ETF).
- Tamaño de muestra principal: cinco años hasta 31/03/2015.
- Marco temporal: 30 minutos.
- Symbolización de entradas ajustada con `PositiveDayChange` y `NegativeDayChange` para el cambio entre apertura y 15:30.
- Optimización por etapas: primero parámetros base, luego ajuste conjunto de precio y volumen.
- El número de operaciones se redujo tras optimizar, con mejoría en tasa de acierto; la mejora fue incremental por filtros.
- No se incluyen stops de protección en los tests; el riesgo se gestiona de forma básica.
- Tasa de operaciones del lado corto y largo más balanceada tras filtros de volumen.

## 6) Implementación

- **Input**: PositiveDayChange (rango -0.25 a 1.0, paso 0.05; óptimo 0.35).
- **Input**: NegativeDayChange (rango -1 a 0.25, paso 0.05; óptimo -0.30 o -0.20 según la iteración).
- **Input**: VolumePctFilter (rango 50 a 125, paso 5; óptimo 55 o 90).
- **Input**: VolumeAvgDays (rango 1 a 10, paso 1; óptimo 5 o 6).
- **Input**: AndDayChange_1 y AndDayChange_2: se usan conjuntamente para filtrar condiciones de precio y volumen.
- Entradas y salidas usan el esquema nativo de la estrategia base, con enfoque de ruptura de canal y reglas de continuación en zona terminal de sesión.





