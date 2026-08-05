# Evaluación de estrategia: Pivot Breakout Strategy

## 1) Identificación y rendimiento

- **ID:** 008
- **Archivo PDF:** SCC+Issue+12+Dec+2015.pdf
- **Issue:** 12 (Dec 2015)
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

La estrategia detecta pivotes de máximos y mínimos con `left strength` y `right strength` para definir un patrón de ruptura válido. Tras el patrón, exige continuidad para activar entrada, con filtros sobre cierres consecutivos.

Es un enfoque de ruptura de estructura intradía orientado a operativa swing, con sensibilidad a la calidad de la formación del pivote y al contexto de cierre de velas.

## 3) Contexto y reglas

- **Tipo de activo / mercado:** Pivot Breakout Strategy
- **Mercados indicados:** Futuros sobre índices y ETFs
- **Horizonte:** No detectado
- **Estilo de estrategia:** Cycles

## 4) Datos y backtest

- Prueba en SPY con barras de 65 minutos en cinco años (hasta 30/09/2015), con LIBBT de 5 minutos para mayor precisión.
- Número de operaciones razonable para operativa swing intradía (~equilibrado entre largos y cortos).
- Ventaja relativa en el lado largo: métricas de duración, tasa de acierto y beneficio mejor distribuidos.
- A continuación se sugiere testear modificaciones de configuración de pivotes y condiciones de salida para reducir operaciones perdedoras.

## 6) Implementación

- Entradas largas: patrón de pivote bajo válido + ruptura + cierre con mínimo de cierres consecutivos `LowerClosesLX` definido en parámetro.
- Entradas cortas: patrón de pivote alto válido + ruptura + cierre con máximo de cierres consecutivos `HigherClosesSX`.
- Regla operativa de duración: la operación permanece en mercado al menos 1 barra.
- Entradas por orden límite a mejor precio del siguiente bar.
- Considerar entrada/exit orders en librería de Strategy para ajustar precisión entre pivote y patrón.





