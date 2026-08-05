# Evaluación de estrategia: Put Call VRAO Add-on Strategy

## 1) Identificación y rendimiento

- **ID:** 004
- **Archivo PDF:** SCC Issue 4 Apr 2015.pdf
- **Issue:** 4 (Apr 2015)
- **Revista:** Strategy Concepts (TradeStation)
- **Autor:** Stanley Dash, CMT
- **Mercado:** Equities
- **Horizonte:** No detectado

---

- **Profit Factor = No encontrado** (se indica como alto para esta familia).
- **Percent Profitable = 60.29%** (en el contexto de esta estrategia se califica como "algo alto" para este tipo de estrategia).
- **RINA Index = 2.00** (alto, influido por baja exposición al mercado).
- **Comentario explícito:** se observan caídas pequeños (~5%), pero rendimiento cíclico y periodos de flat.

## 2) Tesis de trading y edge

La estrategia es un componente adicional para una tendencia base, por ejemplo `TSL:Mov Avg Machine`, que añade posiciones sólo en la misma dirección de la posición existente. Su ventaja es “acumular” exposición en tendencia cuando la señal principal ya está activa, mejorando beneficio por tendencia y suavizando el riesgo ajustado.

Los valores del índice RINA mejoran notablemente frente a usar sólo la estrategia principal. El tamaño de posición efectivo crece con adiciones controladas y la frecuencia de operaciones se reduce en la versión combinada.

## 3) Contexto y reglas

- **Tipo de activo / mercado:** Put/Call VRAO Add-on Strategy
- **Mercados indicados:** Equities
- **Horizonte:** No detectado
- **Estilo de estrategia:** Seguimiento de tendencia

## 4) Datos y backtest

- Instrumento base principal del ejemplo: SPY (SPDR S&P 500 ETF).
- Horizonte de prueba: 7 años hasta 31/12/2014, barras diarias.
- Tamaño de entrada inicial 100 acciones y adición en base a condiciones de VRAO (largo o corto).
- En pruebas se observó menor número de operaciones con combinación, mejora en Profit Factor y RINA, y un promedio de shares ~318.5 en entradas principales.
- No existen salidas nativas en la estrategia add-on: la señal del componente principal controla apertura/cierre.
- Máximo de adiciones por entrada principal: 4.
- Mejora adicional sugerida: incluir stops o trailing stops, y posible combinación con estrategias de salida por toma parcial/progresiva.

## 6) Implementación

- **MA1Type_1S_2W_3E**: 1 (media simple).
- **MA1Length**: 36 (rango 20–45 optimizado).
- **MA2Type_1S_2W_3E**: 3 (media exponencial).
- **MA2Length**: 53 (rango 50–75 optimizado).
- **OscLength**: 20 (rango 15–30).
- **BullLevel**: 0.87.
- **BearLevel**: 0.13.
- **Input de adiciones**: `PCVRAO` cruza `BullLevel` para añadir largo; cruza `BearLevel` para añadir corto, con orden válida en la barra siguiente para evitar conflictos.
- **Regla de salida**: sin salidas propias; una nueva señal del sistema principal cierra posiciones y reinicia.





