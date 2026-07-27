# Matriz Sersan → TSIS

Esta matriz distingue conocimiento docente consolidado de adopción arquitectónica. Ninguna fila aprueba por sí sola una modificación de TSIS.

| ID | Conocimiento | Cobertura TSIS preliminar | Acción |
|---|---|---|---|
| KR-001 | Data, sesiones y series continuas | `PARCIALMENTE_CUBIERTO` | Mantener como referencia; aplicar solo a fuentes y contratos que requieran sesiones/rollover. |
| KR-002 | Especificación causal de estrategias | `ALINEADO` | Incorporar como contrato obligatorio de Strategy Specification y causalidad point-in-time. |
| KR-003 | Entradas Donchian y semántica de ruptura | `PENDIENTE_DE_ESTRATEGIA` | Materializar únicamente cuando se formalice un experimento Donchian para TSIS. |
| KR-004 | Salidas, trailing y dependencia del camino | `PENDIENTE_EN_MOTOR` | Convertir en requisitos y pruebas del simulador de órdenes/salidas. |
| KR-005 | Position sizing y control de exposición | `PENDIENTE_EN_MOTOR` | Definir política de sizing, capital compartido y exposición antes de backtests de cartera. |
| KR-006 | Métricas y evaluación de performance | `PARCIALMENTE_PLANIFICADO` | Crear especificación canónica de métricas con fórmulas y convenciones reproducibles. |
| KR-007 | Benchmark y suficiencia económica | `ALINEADO` | Exigir benchmark y umbral de suficiencia económica además de robustez. |
| KR-008 | Backtest y lectura a nivel portfolio | `PENDIENTE_EN_MOTOR` | Separar agregación informativa de simulación de cartera con capital y concurrencia. |
| KR-009 | Generalización transversal y universo PIT | `ALINEADO_CON_RESTRICCION` | Conservar el Nasdaq actual solo como sonda; TSIS debe usar universo PIT para inferencia operable. |
| KR-010 | Regímenes y filtros | `ALINEADO_CON_RESTRICCION` | Tratar filtros y regímenes como hipótesis con coste de grados de libertad. |
| KR-011 | Optimización y estabilidad paramétrica | `PENDIENTE_EN_VALIDACION` | Implementar mapas de sensibilidad y regiones estables; no escoger solo el máximo. |
| KR-012 | IS/OOS, holdouts y Walk Forward | `PENDIENTE_EN_VALIDACION` | Formalizar splits temporales, embargo/purga cuando corresponda y holdouts sellados. |
| KR-013 | Robustez, simplicidad y sobreoptimización | `ALINEADO` | Integrar con DSR/PBO/CSCV y registro de grados de libertad de TSIS. |
| KR-014 | Fidelidad de ejecución y costes | `PARCIALMENTE_CUBIERTO` | Verificar que quote_guarded alimenta un fill simulator causal; añadir costes y reglas bid/ask. |
| KR-015 | Asimetría long/short y tendencialidad | `ALINEADO` | Evaluar long y short como hipótesis separadas; no transferir resultados entre lados. |
| KR-016 | Diversificación y correlación | `PENDIENTE_EN_PORTFOLIO` | Calcular correlación de retornos operativos y concentración antes de combinar estrategias. |
| KR-017 | Herramientas, informes y límites operativos | `REFERENCIA_SOLAMENTE` | No adoptar limitaciones de TradeStation como arquitectura TSIS; conservarlas como contexto. |
| KR-018 | Selección multicriterio y decisión operativa | `PENDIENTE_EN_GOBERNANZA` | Definir decisión multicriterio ex ante y mantener separado ranking, selección y aprobación. |
| KR-019 | Sondas de edge y líneas de mejora | `BACKLOG_DE_INVESTIGACION` | Convertir cada mejora en experimento preregistrado, no en cambio acumulativo del sistema. |
| KR-020 | Fuentes externas y disciplina bibliográfica | `PENDIENTE_VALIDACION_EXTERNA` | Verificar autores, títulos y afirmaciones antes de citarlos como autoridad. |
