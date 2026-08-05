# Evaluación de estrategia: Market Breadth Gauge Strategy

## 1) Identificación y rendimiento

- **ID:** 007
- **Archivo PDF:** SCC+Issue+12+Dec+2015.pdf
- **Issue:** 12 (Dec 2015)
- **Revista:** Strategy Concepts (TradeStation)
- **Autor:** Stanley Dash, CMT
- **Mercado:** Acciones, futuros y forex
- **Horizonte:** No detectado

---

- **Profit Factor = No encontrado** (se indica como alto para esta familia).
- **Percent Profitable = No encontrado** (en el contexto de esta estrategia se califica como "algo alto" para este tipo de estrategia).
- **RINA Index = No encontrado** (alto, influido por baja exposición al mercado).
- **Comentario explícito:** se observan caídas pequeños (~5%), pero rendimiento cíclico y periodos de flat.

## 2) Tesis de trading y edge

La estrategia usa el índice de amplitud de mercado como segundo dato (`Data2`) y calcula medias rápidas y lentas sobre un índice de amplitud basado en precio x volumen (cambios de issues alcistas menos bajistas). Se normaliza para evitar sesgos de escala y luego se convierte en señal de tendencia.

La ventaja propuesta es filtrar si la amplitud acompaña el movimiento direccional de precio, mejorando la selección de trades con mejor consistencia entre tendencia y contexto de mercado.

## 3) Contexto y reglas

- **Tipo de activo / mercado:** Market Breadth Gauge Strategy
- **Mercados indicados:** Acciones, futuros y forex
- **Horizonte:** No detectado
- **Estilo de estrategia:** Patrón de barras

## 4) Datos y backtest

- Aplicada a QQQ en pruebas diarias, extensible a SPY con símbolo equivalente de amplitud (`$VALSPD`).
- Ejemplo con cinco años hasta 30/09/2015, capital inicial 15,000 y riesgo de 0.01 por operación.
- La señal larga presenta mejor comportamiento que la corta: 138 largas vs 26 cortas en un caso, por lo que la fiabilidad de la parte corta debe interpretarse con cautela.
- Se observa curva de equity lineal con drawdown semanal alrededor de 5%.
- Se recomienda sensibilidad por pares de inputs `(Slow_MA_Length, Fast_MA_Length)` y `(MBG_LE_Level, MBG_SE_Level)` para robustecer.

## 6) Implementación

- Regla base:
  - Larga si el cierre está por encima de mayor máximo de las últimas dos barras y el cambio relativo de breadth confirma con filtro de nivel.
  - Corta si el cierre está por debajo de menor mínimo de las dos barras y condiciones breadth análogas.
- Se usa salida por tiempo/rango de tendencia con control de entrada y salida de barra.
- Se prioriza configuración de parámetros basada en la superficie de sensibilidad con máximo en zonas planas, evitando extremos de optimización.





