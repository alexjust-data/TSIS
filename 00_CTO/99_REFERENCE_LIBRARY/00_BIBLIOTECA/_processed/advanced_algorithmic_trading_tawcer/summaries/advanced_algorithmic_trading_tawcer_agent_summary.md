# Advanced Algorithmic Trading

**book_id:** `advanced_algorithmic_trading_tawcer`  
**Autor/Fuente:** QuantStart / Michael Halls-Moore  
**Tipo:** Libro PDF  
**Fuente original:** `84-advanced-algorithmic-trading-(www.tawcer.com).pdf`  
**Estado:** `indexed`  
**Unidades extraidas:** 517 `page`  
**Caracteres extraidos:** 854989  
**OCR/revision:** `False`

## Menu Rapido

- [Rol En TSIS](#rol-en-tsis)
- [Como Deben Usarlo Los Agentes](#como-deben-usarlo-los-agentes)
- [Secciones Resumidas](#secciones-resumidas)
- [Mapa TOC/Fuente Extraido](#mapa-tocfuente-extraido)
- [Componentes TSIS Afectados](#componentes-tsis-afectados)
- [Checklist Para Agentes](#checklist-para-agentes)

## Rol En TSIS

Sirve como puente entre el primer backtester event-driven y modelos cuantitativos mas avanzados.

**Utilidad principal:** continuacion avanzada de QuantStart para research, modelos y componentes cuantitativos posteriores al vertical slice.

## Como Deben Usarlo Los Agentes

- No sustituye a la arquitectura del motor, pero aporta ideas de research, estadistica y portfolio que se conectan al core.
- Usarlo despues de tener ledgers fiables: las tecnicas avanzadas necesitan series limpias y reproducibles.
- Puede alimentar librerias de estrategias benchmark y modelos estadisticos para pruebas comparativas.
- Vincular cada tecnica a datos, supuestos, validacion y costes.

## Secciones Resumidas

### Research Cuantitativo

Modelos, estadistica y flujo de investigacion.

**Encaje TSIS:** Research lab.

### Series Temporales

Forecasting, estacionariedad y modelos cuantitativos.

**Encaje TSIS:** TimeSeriesResearch.

### Portfolio Y Riesgo

Construccion de cartera y metricas.

**Encaje TSIS:** PortfolioAnalytics.

### Ejecucion Y Realismo

Supuestos de coste/ejecucion que afectan resultados.

**Encaje TSIS:** Execution realism.

### Aplicacion TSIS

Biblioteca de benchmarks avanzados sobre motor ya validado.

**Encaje TSIS:** Benchmark suite.

## Mapa TOC/Fuente Extraido

| # | Titulo detectado | Unidad |
|---|---|---|
| 1 | I Introduction |  |
| 2 | Introduction To Advanced Algorithmic Trading |  |
| 3 | The Hunt for Alpha |  |
| 4 | Why Time Series Analysis, Bayesian Statistics and Machine Learning? |  |
| 5 | Bayesian Statistics |  |
| 6 | Time Series Analysis |  |
| 7 | Machine Learning |  |
| 8 | How Is The Book Laid Out? |  |
| 9 | Required Technical Background |  |
| 10 | Mathematics |  |
| 11 | Programming |  |
| 12 | How Does This Book Differ From "Successful Algorithmic Trading"? |  |
| 13 | Software Installation |  |
| 14 | Installing Python |  |
| 15 | Installing R |  |
| 16 | QSTrader Backtesting Simulation Software |  |
| 17 | Alternatives |  |
| 18 | Where to Get Help |  |
| 19 | II Bayesian Statistics |  |
| 20 | Introduction to Bayesian Statistics |  |
| 21 | What is Bayesian Statistics? |  |
| 22 | Frequentist vs Bayesian Examples |  |
| 23 | Applying Bayes' Rule for Bayesian Inference |  |
| 24 | Coin-Flipping Example |  |
| 25 | Bayesian Inference of a Binomial Proportion |  |
| 26 | The Bayesian Approach |  |
| 27 | Assumptions of the Approach |  |
| 28 | Recalling Bayes' Rule |  |
| 29 | The Likelihood Function |  |
| 30 | Bernoulli Distribution |  |

Consultar el mapa completo en:

- `../index/advanced_algorithmic_trading_tawcer_source_map.md`
- `../extracted/advanced_algorithmic_trading_tawcer_toc.json`

## Componentes TSIS Afectados

- `ResearchStrategyLibrary`, `TimeSeriesResearch`
- `PortfolioAnalytics`, `RiskMetrics`
- `StrategyBenchmarkSuite`, `ExperimentRunner`

## Checklist Para Agentes

- Abrir primero este resumen.
- Abrir despues `../index/advanced_algorithmic_trading_tawcer_concept_index.md` para localizar conceptos.
- Abrir `../index/advanced_algorithmic_trading_tawcer_source_map.md` antes del PDF/EPUB.
- Si se toma una decision de arquitectura, citar `book_id`, seccion y artefacto TSIS afectado.
- No copiar texto largo del libro; convertirlo en decision, contrato, test o tarea.
