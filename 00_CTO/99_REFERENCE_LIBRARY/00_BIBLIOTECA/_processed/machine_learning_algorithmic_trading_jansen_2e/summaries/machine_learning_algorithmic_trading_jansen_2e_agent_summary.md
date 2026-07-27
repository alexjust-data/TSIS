# Machine Learning for Algorithmic Trading, 2nd Edition

**book_id:** `machine_learning_algorithmic_trading_jansen_2e`  
**Autor/Fuente:** Stefan Jansen  
**Tipo:** Libro PDF  
**Fuente original:** `Machine_Learning_for_Algorithmic_Trading_2nd_-_Stefan_Jansen.pdf`  
**Estado:** `indexed`  
**Unidades extraidas:** 1172 `page`  
**Caracteres extraidos:** 1597486  
**OCR/revision:** `False`

## Menu Rapido

- [Rol En TSIS](#rol-en-tsis)
- [Como Deben Usarlo Los Agentes](#como-deben-usarlo-los-agentes)
- [Secciones Resumidas](#secciones-resumidas)
- [Mapa TOC/Fuente Extraido](#mapa-tocfuente-extraido)
- [Componentes TSIS Afectados](#componentes-tsis-afectados)
- [Checklist Para Agentes](#checklist-para-agentes)

## Rol En TSIS

Libro fuerte para laboratorio ML, pero debe entrar despues del motor reproducible y datos limpios.

**Utilidad principal:** referencia ML posterior al core: feature store point-in-time, model registry, alpha research y validacion.

## Como Deben Usarlo Los Agentes

- El ML solo tiene sentido si los features son point-in-time y el backtester produce decisiones auditables.
- Separar factor research, model training, validation, prediction serving y portfolio/execution.
- Usar su contenido para disenar feature store, MLExperimentRegistry y pruebas de leakage.
- No usarlo como primer manual de motor event-driven.

## Secciones Resumidas

### Datos Y Alpha Factors

Fuentes de datos, factores, features y targets.

**Encaje TSIS:** FeatureStore/AlphaLibrary.

### Modelos Supervisados

Regresion, clasificacion, ensembles y model selection.

**Encaje TSIS:** MLExperimentRegistry.

### Deep Learning Y NLP

Modelos avanzados y datos alternativos.

**Encaje TSIS:** Future ML research.

### Backtesting Y Portfolio

Uso de herramientas de backtesting y portfolio con ML.

**Encaje TSIS:** MLBacktestAdapter.

### Aplicacion TSIS

Capas ML sobre motor event-driven y validacion cronologica.

**Encaje TSIS:** ML roadmap.

## Mapa TOC/Fuente Extraido

| # | Titulo detectado | Unidad |
|---|---|---|
| 1 | Preface |  |
| 2 | What to expect |  |
| 3 | What's new in the second edition |  |
| 4 | Who should read this book |  |
| 5 | What this book covers |  |
| 6 | To get the most out of this book |  |
| 7 | Get in touch |  |
| 8 | Machine Learning for Trading – From Idea to Execution |  |
| 9 | The rise of ML in the investment industry |  |
| 10 | From electronic to high-frequency trading |  |
| 11 | Factor investing and smart beta funds |  |
| 12 | Algorithmic pioneers outperform humans |  |
| 13 | ML-driven funds attract $1 trillion in AUM |  |
| 14 | The emergence of quantamental funds |  |
| 15 | Investments in strategic capabilities |  |
| 16 | ML and alternative data |  |
| 17 | Crowdsourcing trading algorithms |  |
| 18 | Designing and executing an ML-driven strategy |  |
| 19 | Sourcing and managing data |  |
| 20 | From alpha factor research to portfolio management |  |
| 21 | The research phase |  |
| 22 | The execution phase |  |
| 23 | Strategy backtesting |  |
| 24 | ML for trading – strategies and use cases |  |
| 25 | The evolution of algorithmic strategies |  |
| 26 | Use cases of ML for trading |  |
| 27 | Data mining for feature extraction and insights |  |
| 28 | Supervised learning for alpha factor creation |  |
| 29 | Asset allocation |  |
| 30 | Testing trade ideas |  |

Consultar el mapa completo en:

- `../index/machine_learning_algorithmic_trading_jansen_2e_source_map.md`
- `../extracted/machine_learning_algorithmic_trading_jansen_2e_toc.json`

## Componentes TSIS Afectados

- `PointInTimeFeatureStore`, `AlphaFactorLibrary`
- `MLExperimentRegistry`, `ModelRegistry`
- `PurgedValidationSplitter`, `BacktestMLAdapter`
- `PortfolioConstructionModel`

## Checklist Para Agentes

- Abrir primero este resumen.
- Abrir despues `../index/machine_learning_algorithmic_trading_jansen_2e_concept_index.md` para localizar conceptos.
- Abrir `../index/machine_learning_algorithmic_trading_jansen_2e_source_map.md` antes del PDF/EPUB.
- Si se toma una decision de arquitectura, citar `book_id`, seccion y artefacto TSIS afectado.
- No copiar texto largo del libro; convertirlo en decision, contrato, test o tarea.
