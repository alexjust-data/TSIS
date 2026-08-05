# Evaluación de estrategia: Breakout Score Strategy

## 1) Identificación y rendimiento

- **ID:** 010
- **Archivo PDF:** SCC Issue 14 Feb 2016.pdf
- **Issue:** 14 (Feb 2016)
- **Revista:** Strategy Concepts (TradeStation)
- **Autor:** Frederic Palmliden, CFA, CMT
- **Mercado:** No detectado
- **Horizonte:** operativa swing
- **Estilo de estrategia:** Seguimiento de tendencia

---

- **Profit Factor = No encontrado** (se indica como alto para esta familia).
- **Percent Profitable = No encontrado** (en el contexto de esta estrategia se califica como "algo alto" para este tipo de estrategia).
- **RINA Index = No encontrado** (alto, influido por baja exposición al mercado).
- **Comentario explícito:** se observan caídas pequeños (~5%), pero rendimiento cíclico y periodos de flat.

## 2) Tesis de trading y edge

Esta estrategia construye un puntaje acumulado (`score`) a partir de penetraciones del precio más allá del canal asimétrico. Cada vez que el precio rompe por encima del canal se suma 1; cada ruptura por debajo resta 1. Cuantas más penetraciones, mayor sesgo direccional del score.

La mecánica crea una zona neutral alrededor del centro del canal para reducir ruido y evitar operar continuamente dentro de rangos. También introduce reglas de salida para evitar permanencia excesiva cuando el score pierde valor.

## 3) Contexto y reglas

- **Tipo de activo / mercado:** Breakout Score Strategy
- **Mercados indicados:** No detectado
- **Horizonte:** operativa swing
- **Estilo de estrategia:** Seguimiento de tendencia

## 4) Datos y backtest

- Se prueba sobre 10 años de SPY con parámetros base de la estrategia.
- El conteo total y la tasa de operaciones son razonables para un enfoque diario/swing (menos de 5 operaciones/año en la muestra base).
- Existe mejora en métricas de largo plazo con tamaño variable de posición: se observa beneficio acumulado mayor en operación larga sostenida; algunas operaciones puntuales en corto pueden actuar como outliers.
- La ventaja de tendencia es razonable si se aceptan periodos con 100% de tiempo de mercado bajo ciertas optimizaciones.
- Falta un control de reentrada en la misma dirección tras salida; se recomienda evaluar múltiples entradas y ajustes de stop.

## 6) Implementación

- Construcción de score basada en una ventana de canal (largo 8 por defecto en ejemplos).
- Entradas largas/cortas en función del score respecto a umbrales de longitud de ruptura.
- Salidas con reglas de salida del canal y ventanas de tiempo para consolidar beneficios.
- La estrategia nativa no incorpora stop de emergencia ni stop dinámico; se recomienda añadir `Stop Loss`/`Dollar Trailing` si se usa en producción.





