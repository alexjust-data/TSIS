# Consumer Classes - Modulo 01

## 1. Rol del documento

Este documento define las clases de consumidores del modulo:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps`

Su objetivo es fijar una taxonomia formal de quienes pueden consumir activos institucionales y bajo que nivel de exigencia.

## 2. Principio rector

No todos los consumidores son equivalentes.

Un mismo dataset puede ser:

- valido para backtest base;
- valido solo para ML con flags;
- util solo para investigacion;
- o util solo para forense.

Por tanto, las policies de consumo deben anclarse en clases de consumidor formales.

## 3. Tipos de consumidores

Las clases base del modulo son las siguientes.

### backtest_core

Consumidor principal para evaluacion historica defendible del modulo.

Exige:

- semantica suficientemente cerrada;
- calidad estable;
- riesgo acotado;
- y compatibilidad con uso base de investigacion.

### backtest_extended

Consumidor para ampliacion controlada de cobertura, sensibilidad o analisis complementario.

Tolera mas limitaciones que `backtest_core`, pero no opera sin politica explicita.

### event_engine

Consumidor de objetos o datasets usados para formalizar eventos, causalidad o estructura temporal relevante.

Exige:

- consistencia temporal;
- semantica clara del evento;
- y trazabilidad suficiente.

### execution_simulator

Consumidor para modelos de ejecucion, liquidez, slippage, colas o halts.

Exige:

- interpretacion fuerte de microestructura relevante;
- y limites conocidos cuando la calidad no soporte simulacion principal.

### ml_primary

Consumidor ML permitido sin banderas especiales obligatorias.

Exige:

- semantica estable;
- leakage control razonable;
- y calidad compatible con uso sistematico.

### ml_flagged

Consumidor ML permitido solo si las limitaciones viajan explicitamente como condicion de uso.

Puede consumir activos `review` o `recoverable_with_flag` cuando exista policy expresa.

### rl_allowed

Consumidor RL potencial.

Debe tratarse como clase de umbral alto.

Por defecto, no debe inferirse desde `ml_primary` ni desde `ml_flagged`.

Requiere contrato explicito adicional, dada la sensibilidad de RL a calidad, semantica y causalidad operacional.

### causal_only

Consumidor que usa el activo como soporte causal, contextual o de anotacion, pero no como fuente cuantitativa principal de simulacion o aprendizaje.

### research_only

Consumidor para investigacion exploratoria o analisis acotado no promocionado.

### forensic_only

Consumidor para auditoria, diagnostico, reconciliacion y preservacion de evidencia.

### live_downstream_candidate

Consumidor potencial de capas posteriores fuera del modulo 01, como sistemas live.

Esta clase debe tratarse con umbral muy alto y no debe habilitarse sin cierre contractual adicional.

## 4. Relaciones entre clases

Las clases no son equivalentes ni totalmente transitivas.

En particular:

- `backtest_core` no implica automaticamente `execution_simulator`;
- `ml_primary` no implica `rl_allowed`;
- `research_only` no implica `backtest_extended`;
- `causal_only` no implica consumo cuantitativo principal;
- `validated` no implica todos los consumidores;
- `institutional` tampoco implica todos los consumidores.

## 5. Politica de asignacion

Una clase de consumidor solo debe asignarse a un dataset o contrato cuando exista justificacion explicita basada en:

- calidad;
- schema;
- semantica;
- evidencia;
- y riesgos conocidos.

No debe asignarse por:

- conveniencia del siguiente pipeline;
- costumbre;
- o necesidad de cerrar un experimento.

## 6. Relacion con policies

Las `data_consumption_policies/` deben usar estas clases como vocabulario base.

No deben proliferar consumidores nuevos sin:

- justificacion clara;
- definicion formal;
- y analisis de compatibilidad con las clases ya existentes.

## 7. Regla final

Si un activo no tiene consumidor claramente definido, no esta listo para consumo institucional serio.
