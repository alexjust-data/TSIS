# Evaluation Systems

## Objetivo

Diseñar mecanismos de evaluación.

## Preguntas

- ¿Cómo sabemos que algo funciona?
- ¿Cómo medimos calidad?
- ¿Cómo detectamos fallos?

## Contenido esperado

- Agent Evals
- Backtest Evals
- Research Evals
- Reproducibility
- Benchmark Design
- Fitness Functions

## Resultado esperado

Sistema capaz de distinguir verdad de ruido.



----


## 2. Evaluación de agentes

**Frontera actual:** el problema ya no es “¿responde bien?”, sino “¿qué paso falló, con qué herramienta, con qué coste, con qué traza, bajo qué versión del prompt y del código?”. Anthropic insiste en evals para agentes, OpenAI tiene BrowseComp para navegación web difícil, y SWE-bench se ha convertido en referencia para agentes de código. ([OpenAI][3])

**Punto crítico:** los benchmarks públicos se están rompiendo/contaminando; Berkeley RDI muestra que incluso SWE-bench puede explotarse si el harness está mal diseñado. Por tanto, TSIS necesita evals propios, no solo benchmarks externos. ([Berkeley RDI][4])

**Para TSIS:** crear un sistema de evaluación interno: exactitud de hipótesis, reproducibilidad del backtest, calidad del informe, detección de overfitting, respeto de reglas, coste por experimento y trazabilidad completa.

**Recursos:** Anthropic Demystifying Evals, OpenAI BrowseComp, Survey on Evaluation of LLM-based Agents, LangChain Agent Evaluation Checklist. ([arXiv][5])


Y DeepMind, OpenAI y Anthropic están llegando a la misma conclusión:

El evaluador es más importante que el modelo.