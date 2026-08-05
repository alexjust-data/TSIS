# Evaluación de estrategia: Regression Angles Strategy

## 1) Identificación y rendimiento

- **ID:** 009
- **Archivo PDF:** SCC Issue 13 Jan 2016.pdf
- **Issue:** 13 (Jan 2016)
- **Revista:** Strategy Concepts (TradeStation)
- **Autor:** Stanley Dash, CMT
- **Mercado:** No detectado
- **Horizonte:** operativa swing

---

- **Profit Factor = No encontrado** (se indica como alto para esta familia).
- **Percent Profitable = No encontrado** (en el contexto de esta estrategia se califica como "algo alto" para este tipo de estrategia).
- **RINA Index = No encontrado** (alto, influido por baja exposición al mercado).
- **Comentario explícito:** se observan caídas pequeños (~5%), pero rendimiento cíclico y periodos de flat.

## 2) Tesis de trading y edge

Se calculan ángulos de regresión lineal sobre ventanas deslizantes de `LRLength`. Un ángulo positivo del `LRAngleBuySignal` impulsa compras, y uno negativo del `LRAngleSellSignal` impulsa ventas. La entrada/salida depende de secuencias de barras donde el ángulo confirma o deja de confirmar tendencia.

La estrategia busca filtrar la pendiente dominante y operar cambios de dirección con un sesgo de tendencia, pero sin sobreexponer el sistema al ruido de corto plazo.

## 3) Contexto y reglas

- **Tipo de activo / mercado:** Regression Angles Strategy
- **Mercados indicados:** No detectado
- **Horizonte:** operativa swing
- **Estilo de estrategia:** Seguimiento de tendencia

## 4) Datos y backtest

- Se prueba sobre SPY en barras de 130 minutos, cinco años de datos.
- Ventaja en equilibrio de resultados entre lados, con ratio promedio de ganancias vs pérdidas saludable y baja exposición en promedio.
- % de tiempo en mercado no mostrado, coherente con un enfoque swing.
- Se sugiere incorporar stop de emergencia, ya que no hay gestión de riesgo adicional nativa en el bloque de reglas.

## 6) Implementación

- **LRLength**: 10.
- **LRAngleBuySignal**: 2.25 (ángulo de entrada para compra).
- **LRAngleSellSignal**: -2.25 (ángulo de entrada para venta).
- **ExitBarCount**: 4.
- **ExitBar_AnglesCounterTrend**: 4.

- Entrada larga: cuando el ángulo de la media de regresión (`LRAngleBuySignal`) cruza al alza el umbral.
- Entrada corta: cuando el ángulo cruza a la baja el umbral.
- Salida: si durante `ExitBarCount` barras el ángulo se debilita respecto a la barra previa (según dirección), se cierra la posición.





