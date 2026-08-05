# Evaluación de estrategia: 2+1 Moving Average Strategy

## 1) Identificación y rendimiento

- **ID:** 006
- **Archivo PDF:** SCC Issue 9 Sept 2015.pdf
- **Issue:** 9 (Sept 2015)
- **Revista:** Strategy Concepts (TradeStation)
- **Autor:** Frederic Palmliden, CFA, CMT
- **Mercado:** Futuros sobre índices y ETFs
- **Horizonte:** No detectado

---

- **Profit Factor = No encontrado** (se indica como alto para esta familia).
- **Percent Profitable = No encontrado** (en el contexto de esta estrategia se califica como "algo alto" para este tipo de estrategia).
- **RINA Index = No encontrado** (alto, influido por baja exposición al mercado).
- **Comentario explícito:** se observan caídas pequeños (~5%), pero rendimiento cíclico y periodos de flat.

## 2) Tesis de trading y edge

La estrategia 2+1 compara tres medias móviles (rápida, media y lenta) para definir estructura de tendencia en un activo. La señal de entrada se dispara cuando la media rápida cruza a la media media en la dirección de la tendencia respecto a la media lenta.

Es una construcción muy limpia para probar calidad de señal de tendencia y la persistencia de movimientos de mercado. En pruebas, el beneficio está más relacionado con la coherencia de la señal que con el número de entradas.

## 3) Contexto y reglas

- **Tipo de activo / mercado:** 2+1 Moving Average Strategy
- **Mercados indicados:** Futuros sobre índices y ETFs
- **Horizonte:** No detectado
- **Estilo de estrategia:** Basada en volatilidad

## 4) Datos y backtest

- Aplicada en IWM diario con 11 años de historial (señales desde aprox. 2005).
- Se compararon dos esquemas: tamaño fijo de 100 acciones y tamaño variable con capital constante.
- Los resultados muestran que el esquema de capital constante mejora rendimiento total en términos de beneficio absoluto, con holding medio razonable para una estrategia Seguimiento de tendencia.
- No se incluyen stops integrados; se propone añadir componentes de gestión de riesgo de la plataforma si fuese necesario.

## 6) Implementación

- **Price**: Close (por defecto).
- **FastLength**: 10.
- **MedLength**: 50.
- **SlowLength**: 200.
- **Entrada larga**: cruce alcista de media rápida sobre media media y precio por encima de media lenta.
- **Entrada corta**: cruce bajista de media rápida bajo media media y precio por debajo de media lenta.
- **Salida**: cruce opuesto (media rápida hacia abajo/superior según posición).
- **Gestión**: se conserva el `Max. Shares/Contracts Held` y `Total Shares/Contracts Held` por configuración, útil para análisis de escalado y riesgo.





