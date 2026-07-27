# SERSAN SYSTEM MANUAL — 02–17

## Propósito

Reconstrucción operacional del método enseñado en las prácticas 02–17. No es un resumen cronológico ni una validación externa de las estrategias de ejemplo.

## Principios de uso

1. Declarar datos, sesión, precios y costes antes de interpretar el backtest.
2. Separar hipótesis, reglas, parámetros y decisiones de implementación.
3. Tratar la optimización como búsqueda condicionada, no como evidencia de edge.
4. Exigir robustez, muestra suficiente y validación fuera de muestra.
5. Evaluar sizing y portfolio como capas que alteran el riesgo, no como maquillaje del resultado.
6. Incubar y vigilar degradación antes de comprometer capital.

## Arquitectura del conocimiento

### Datos y representación

- `KR-001` — Data, sesiones y series continuas
- `KR-002` — Especificación causal de estrategias

### Sistemas, entradas y salidas

- `KR-003` — Entradas Donchian y semántica de ruptura
- `KR-004` — Salidas, trailing y dependencia del camino
- `KR-005` — Position sizing y control de exposición
- `KR-009` — Generalización transversal y universo PIT
- `KR-010` — Regímenes y filtros
- `KR-025` — Aberration, overnight y ajuste de salidas temporales
- `KR-026` — Arquitectura y taxonomía de salidas
- `KR-027` — Sistemas tendenciales en oro y Parabolic SAR
- `KR-028` — Buscador de entradas y Tomorrow's Trend

### Evaluación y costes

- `KR-006` — Métricas y evaluación de performance
- `KR-007` — Benchmark y suficiencia económica
- `KR-008` — Backtest y lectura a nivel portfolio
- `KR-011` — Optimización y estabilidad paramétrica
- `KR-012` — IS/OOS, holdouts y Walk Forward
- `KR-013` — Robustez, simplicidad y sobreoptimización

### Optimización y robustez

- `KR-014` — Fidelidad de ejecución y costes
- `KR-015` — Asimetría long/short y tendencialidad
- `KR-016` — Diversificación y correlación
- `KR-017` — Herramientas, informes y límites operativos
- `KR-018` — Selección multicriterio y decisión operativa
- `KR-019` — Sondas de edge y líneas de mejora
- `KR-020` — Fuentes externas y disciplina bibliográfica
- `KR-021` — ORB: rango de apertura y ruptura
- `KR-022` — Biblioteca de filtros y atribución marginal
- `KR-023` — Revisión de superficies de optimización: Apolo
- `KR-024` — Bollinger antitendencial: diario e intradía

### Sizing, portfolio e incubación

- `KR-029` — Money management, position sizing y MSA
- `KR-030` — Construcción, ponderación y diversificación de portfolios
- `KR-031` — Regímenes de mercado e IVTS
- `KR-032` — Datos COT, COT Index y sistemas semanales
- `KR-033` — Incubación, costes y transición a operación

## Flujo operativo

### 1. Fijar el contrato de investigación

Definir universo, frecuencia, calendario, sesión, timestamps, precios de señal y ejecución, corporate actions, costes y disponibilidad point-in-time.

### 2. Formular la hipótesis

Escribir qué comportamiento se espera capturar y por qué podría persistir. La regla técnica implementa la hipótesis; no la sustituye.

### 3. Construir reglas ejecutables

Separar entradas, salidas, stops, filtros, sizing y rebalanceo. Cada cambio crea una variante identificable y consume grados de libertad.

### 4. Ejecutar el backtest y diagnosticar

Revisar operaciones, PnL, drawdown, distribución, estabilidad temporal, exposición y sensibilidad a costes. Un resultado agregado no basta.

### 5. Optimizar con límites

Definir espacio de búsqueda, función objetivo y presupuesto de pruebas. Rechazar mesetas estrechas, dependencia de pocos trades y parámetros sin estabilidad vecinal.

### 6. Validar robustez

Usar separación temporal, validación fuera de muestra y perturbaciones de parámetros, datos, costes y ejecución. Mantener trazabilidad de todas las variantes probadas.

### 7. Diseñar sizing y portfolio

Dimensionar por riesgo declarado. Evaluar correlación, coincidencia de pérdidas, drawdowns conjuntos y efecto del rebalanceo; no asumir que más sistemas implican diversificación.

### 8. Incubar y operar

Comparar resultados observados con el rango esperado, registrar desviaciones y aplicar reglas previas de reducción, pausa o retirada.

## Límites del manual

- Los Assets y decisiones se han admitido solo dentro del canon Sersan.
- No se ha realizado todavía la reconciliación física con TSIS.
- Los hallazgos abiertos permanecen explícitos en `FINAL_OPEN_FINDINGS.jsonl`.
- Para evidencia detallada debe consultarse cada Knowledge Record y su `evidence_id`.
