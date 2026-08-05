# Evaluación de estrategia: The Engulfing Candles Strategy

## 1) Identificación y rendimiento

- **ID:** 002
- **Archivo PDF:** SCC Issue 10 Oct 2015.pdf
- **Issue:** 10 (Oct 2015)
- **Revista:** Strategy Concepts (TradeStation)
- **Autor:** Frederic Palmliden, CFA, CMT
- **Mercado:** Futuros sobre índices y ETFs
- **Horizonte:** No detectado

---

- **Profit Factor = 1.67** (se indica como alto para esta familia).
- **Percent Profitable = No encontrado** (en el contexto de esta estrategia se califica como "algo alto" para este tipo de estrategia).
- **RINA Index = No encontrado** (alto, influido por baja exposición al mercado).
- **Comentario explícito:** se observan caídas pequeños (~5%), pero rendimiento cíclico y periodos de flat.

## 2) Tesis de trading y edge

La estrategia parte del análisis de velas envolventes (alcista y bajista engulfing) en barras de 120 minutos, combinada con ATR y con los patrones de Williams %R. Es una extensión de análisis clásico de velas de reversión y continuación para filtrar entradas dentro del contexto mensual.

El objetivo no es comprar cualquier señal aislada, sino esperar estructura: vela envolvente válida y confirmación con filtro de volatilidad y calendario intramáximo.

## 3) Contexto y reglas

- **Tipo de activo / mercado:** The Engulfing Candles Strategy
- **Mercados indicados:** Futuros sobre índices y ETFs
- **Horizonte:** No detectado
- **Estilo de estrategia:** Cycles

## 4) Datos y backtest

- Serie de pruebas: GBPUSD y marco de 120 minutos con estrategia TSL:Engulfing Candles y ATR Bands.
- Los parámetros optimizados utilizados en el ejemplo: AvgBodyLength=3, ATR_Length=5, ProfitTgt_ATRFactor=2.2, Stop_ATRFactor=4.8, BarToExitOn(LX)=32, BarToExitOn(SX)=13.
- Tiempo de prueba: 5 años hasta 30/06/2015.
- Trade Size: £100,000.
- Comisiones: $2.50 por entrada/salida por lado.
- Se recomienda usar backtesting con Look-Inside-Bar Back-testing (12 minutos) para mayor precisión en barras.

## 6) Implementación

### Parámetros de estudio
- AvgBodyLength: 5 (media exponencial del cuerpo real de velas).
- ATR_Length: 5 (ATR de cálculo).
- ProfitTgt_ATRFactor: 3 (múltiplo del ATR para objetivo de beneficio).
- Stop_ATRFactor: 3 (múltiplo del ATR para stop).
- TimeExit (Bars) LX / SX: número de barras de salida por tiempo.
- BarToExitOn: 5 barras por defecto para salida por tiempo en cada lado.

### Reglas resumidas de trading

- **Entradas largas**: cuando se detecta una vela envolvente alcista y el cierre es mayor que la vela previa, se genera orden de compra stop desde el máximo de la vela alcista o vela previa; la orden sólo es válida en la barra siguiente. Se exige calendario con al menos 19 días de trading restantes en el mes y cierre superior al de la barra previa.
- **Entradas cortas**: simétrico con vela envolvente bajista y cierre inferior al previo.
- **Salida**: salida tras 1 barra mínima o al cerrarse la barra de salida definida, usando stop y objetivo en múltiplos ATR.
- **Notas operativas**: la orden de entrada y la salida se disparan a mercado/siguiente barra según el componente de señal. Apertura diaria E-mini S&P 500 a las 18:00 ET.





