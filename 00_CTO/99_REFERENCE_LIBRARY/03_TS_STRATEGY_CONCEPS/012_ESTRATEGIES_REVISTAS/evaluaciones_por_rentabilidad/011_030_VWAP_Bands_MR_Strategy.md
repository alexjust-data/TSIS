# Evaluación de estrategia: VWAP Bands MR Strategy

## 1) Identificación y rendimiento

- **ID:** 011
- **Archivo PDF:** SCC Issue 15 Mar 2016.pdf
- **Issue:** 15 (Mar 2016)
- **Revista:** Strategy Concepts (TradeStation)
- **Autor:** Frederic Palmliden, CFA, CMT
- **Mercado:** No detectado
- **Horizonte:** intradía
- **Estilo de estrategia:** Reversión a la media

---

- **Profit Factor = No encontrado** (se indica como alto para esta familia).
- **Percent Profitable = No encontrado** (en el contexto de esta estrategia se califica como "algo alto" para este tipo de estrategia).
- **RINA Index = No encontrado** (alto, influido por baja exposición al mercado).
- **Comentario explícito:** se observan caídas pequeños (~5%), pero rendimiento cíclico y periodos de flat.

## 2) Tesis de trading y edge

Es un filtro de continuación/contratendencia sobre bandas de VWAP con parámetros de sensibilidad de salida (`LX1_Band_Num`, `LX2_Band_Num`, `SX1_Band_Num`, `SX2_Band_Num`). La versión original se analiza sola y combinada con la estrategia VWAP Bands clásica dentro de Portfolio Maestro.

El enfoque se apoya en señales de ventaja estadística por banda y optimización multidimensional de parámetros para mantener estabilidad de retorno ante cambios de entrada, con especial atención al porcentaje de éxitos por lado.

## 3) Contexto y reglas

- **Tipo de activo / mercado:** VWAP Bands MR Strategy
- **Mercados indicados:** No detectado
- **Horizonte:** intradía
- **Estilo de estrategia:** Reversión a la media

## 4) Datos y backtest

- backtest inicial sobre SPY con intervalos de 5 minutos y capital inicial 30,000.
- Comisiones de 0.01 por acción, tamaño de operación 1 acción.
- En combinación con VWAP Bands Seguimiento de tendencia, el retorno global mejora, con `Percent of Time in Market` bajo (~9.5%) y drawdown contenido.
- Los análisis 3D muestran superficie de beneficio bastante plana en los niveles optimizados, lo que favorece robustez.
- Recomendación de validación: comprobar estabilidad de `Trail_Stop_Length` y condiciones de entrada/salida para cada símbolo.

## 6) Implementación

- Inputs clave:
  - Estrategia MR de largo: `LX1_Band_Num` 2, `LX2_Band_Num` 2.5 (zona estable).
  - Estrategia MR de corto: `SX1_Band_Num` 2.5, `SX2_Band_Num` 2.5 (zona estable de la cara frontal).
  - `MaxBarsBack = 100` en Portfolio Maestro para cálculos de VWAP.
- backtest muestra curva de equity lineal con volatilidad baja y máxima caída semanal cercana al 4.5%.
- Requiere Portfolio Maestro 9.5 para ejecución a nivel de grupo y importación del archivo `.pmx` cuando aplique.





