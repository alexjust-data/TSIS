# Lesson Distillation: sersan_practice_04_donchain

Title: `Consultas`
Source MD: `03_only_md_revised/practica_04_donchain.md`
Promotion state: `mechanical_rule_candidate` only; no TSIS doctrine promoted.

## What The Lesson Covers

- `sersan_practice_04_donchain_sec_0001` Consultas. Section classified as qa. # Consultas
- `sersan_practice_04_donchain_sec_0002` Menú de navegación. Section classified as qa. ## Menú de navegación - [Consultas](#consultas) - [Entrevista de Iván Sherman y debate metodológico](#entrevista-de-iván-sherman-y-debate-metodológico) - [*Continuación*: Canal...
- `sersan_practice_04_donchain_sec_0003` Entrevista de Iván Sherman y debate metodológico. Section classified as optimization. # Entrevista de Iván Sherman y debate metodológico Iván, que es gestor de Emerging Funds, es una gestora que tiene oficina en distintos sitios, en Nueva York, en Dubái, es, la v...
- `sersan_practice_04_donchain_sec_0004` Continuación*: [Canal de Donchian (13-practice-03)](../../13-practice-03/transcripts/practica_03_revised.md). Section classified as optimization. # *Continuación*: [Canal de Donchian (13-practice-03)](../../13-practice-03/transcripts/practica_03_revised.md) El pseudocódigo de hecho en palabras no es más que tenemos una ba...
- `sersan_practice_04_donchain_sec_0005` PROCESO : Evaluando la idea. Section classified as portfolio. ## PROCESO : Evaluando la idea Empecemos por el principio ¿cuál es el principio? El principio es evaluar el canal, evaluar el canal ya lo hicimos por un lado igualando el *stop*...
- `sersan_practice_04_donchain_sec_0006` Optimización 1. Section classified as portfolio. ### Optimización 1 Hemos trabajado, como se ve en el Excel, con un periodo *in sample* que va desde el inicio de 2007 hasta finales de 2018, y a partir de ahí, es decir, desde p...
- `sersan_practice_04_donchain_sec_0007` Optimización 2. Section classified as money_management. ### Optimización 2 **¿Cómo hemos evaluado el *trailing*?** Como os digo bloqueando el 6... ahora os muestro el Excel de esta segunda optimización: Simplemente aquí pues lo que o...
- `sersan_practice_04_donchain_sec_0008` Optimización 3. Section classified as portfolio. ### Optimización 3 **Filtro de volatilidad `ATR`** Vamos con la tercera. La tercera hemos ido a probar un filtro que es totalmente opcional y no es obligatorio, pero hemos queri...
- `sersan_practice_04_donchain_sec_0009` Optimización 4. Section classified as optimization. ### Optimización 4 Le he hecho toda junta porque queríamos mostraros el mapa 3D. Hemos hecho esta optimización junta. ¿Qué es la optimización junta? Pues: * El canal de 1 a 25 *...
- `sersan_practice_04_donchain_sec_0010` Resultados In Sample. Section classified as optimization. #### **Resultados In Sample** Bien, tenemos aquí el *in sample*. Fijaros que nos da en el *in sample* el mejor: el filtro activado, 25 (**L**) y 0.12 (**M**), es decir, bastante...
- `sersan_practice_04_donchain_sec_0011` Análisis del Out of Sample. Section classified as execution_realism. #### **Análisis del Out of Sample** <figure> <img src="../02_workshops/14-practice-04/img/075.png" width="800"> <figcaption>Figura 075. Datos del periodo out of sample.</figcapt...
- `sersan_practice_04_donchain_sec_0012` Análisis All Data: la información de ambos periodos. Section classified as portfolio. #### **Análisis `All Data`: la información de ambos periodos** Pues tenemos en `Per_canal` una sola en el 1 y se va rápidamente ya la zona de 20 del canal, alternando entre 0 y...

## Mechanical Rule Candidates

- `sersan_practice_04_donchain_rule_0001` [setup_logic, entry_logic, exit_logic, take_profit, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_04_donchain_rule_0002` [bar_construction, price_view, optimization, overfitting, robustness, BRaC] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_04_donchain_rule_0003` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_04_donchain_rule_0004` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_04_donchain_rule_0005` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_04_donchain_rule_0006` [setup_logic, entry_logic, exit_logic, take_profit, optimization, robustness] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_04_donchain_rule_0007` [setup_logic, entry_logic, exit_logic, take_profit, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_04_donchain_rule_0008` [setup_logic, entry_logic, exit_logic, filters, optimization, overfitting] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_04_donchain_rule_0009` [setup_logic, entry_logic, exit_logic, stop_loss, take_profit, filters] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_04_donchain_rule_0010` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, take_profit] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_04_donchain_rule_0011` [setup_logic, entry_logic, exit_logic, take_profit, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_04_donchain_rule_0012` [setup_logic, entry_logic, exit_logic, filters, optimization, overfitting] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_04_donchain_rule_0013` [setup_logic, entry_logic, exit_logic, stop_loss, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_04_donchain_rule_0014` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_04_donchain_rule_0015` [setup_logic, entry_logic, exit_logic, take_profit, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_04_donchain_rule_0016` [setup_logic, entry_logic, exit_logic, filters, optimization, portfolio] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_04_donchain_rule_0017` [setup_logic, entry_logic, exit_logic, filters, optimization, portfolio] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_04_donchain_rule_0018` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_04_donchain_rule_0019` [setup_logic, entry_logic, exit_logic, take_profit, optimization, robustness] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_04_donchain_rule_0020` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_04_donchain_rule_0021` [bar_construction, price_view, setup_logic, entry_logic, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_04_donchain_rule_0022` [bar_construction, price_view, setup_logic, entry_logic, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_04_donchain_rule_0023` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.

## TSIS Translation Candidates

- `sersan_practice_04_donchain_tr_0001` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_04_donchain_tr_0002` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_04_donchain_tr_0003` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_04_donchain_tr_0004` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_04_donchain_tr_0005` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_04_donchain_tr_0006` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_04_donchain_tr_0007` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_04_donchain_tr_0008` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_04_donchain_tr_0009` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_04_donchain_tr_0010` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_04_donchain_tr_0011` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_04_donchain_tr_0012` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_04_donchain_tr_0013` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_04_donchain_tr_0014` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_04_donchain_tr_0015` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_04_donchain_tr_0016` -> `portfolio_evaluator` / `TSIS_PORTFOLIO_EVALUATOR_CANDIDATE`
- `sersan_practice_04_donchain_tr_0017` -> `portfolio_evaluator` / `TSIS_PORTFOLIO_EVALUATOR_CANDIDATE`
- `sersan_practice_04_donchain_tr_0018` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_04_donchain_tr_0019` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_04_donchain_tr_0020` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_04_donchain_tr_0021` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_04_donchain_tr_0022` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_04_donchain_tr_0023` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`

## Key Visual Evidence

### `sersan_practice_04_donchain_img_0022`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/14-practice-04/img/199.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/199.png`
- note: `image_evidence_notes/sersan_practice_04_donchain_img_0022.md`

![sersan_practice_04_donchain_img_0022](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/199.png)

### `sersan_practice_04_donchain_img_0023`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/020.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/020.png`
- note: `image_evidence_notes/sersan_practice_04_donchain_img_0023.md`

![sersan_practice_04_donchain_img_0023](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/020.png)

### `sersan_practice_04_donchain_img_0024`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/021.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/021.png`
- note: `image_evidence_notes/sersan_practice_04_donchain_img_0024.md`

![sersan_practice_04_donchain_img_0024](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/021.png)

### `sersan_practice_04_donchain_img_0025`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/023.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/023.png`
- note: `image_evidence_notes/sersan_practice_04_donchain_img_0025.md`

![sersan_practice_04_donchain_img_0025](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/023.png)

### `sersan_practice_04_donchain_img_0026`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/200.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/200.png`
- note: `image_evidence_notes/sersan_practice_04_donchain_img_0026.md`

![sersan_practice_04_donchain_img_0026](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/200.png)

### `sersan_practice_04_donchain_img_0027`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/201.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/201.png`
- note: `image_evidence_notes/sersan_practice_04_donchain_img_0027.md`

![sersan_practice_04_donchain_img_0027](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/201.png)

### `sersan_practice_04_donchain_img_0028`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/203.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/203.png`
- note: `image_evidence_notes/sersan_practice_04_donchain_img_0028.md`

![sersan_practice_04_donchain_img_0028](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/203.png)

### `sersan_practice_04_donchain_img_0029`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/204.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/204.png`
- note: `image_evidence_notes/sersan_practice_04_donchain_img_0029.md`

![sersan_practice_04_donchain_img_0029](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/204.png)

### `sersan_practice_04_donchain_img_0030`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/2004.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/2004.png`
- note: `image_evidence_notes/sersan_practice_04_donchain_img_0030.md`

![sersan_practice_04_donchain_img_0030](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/2004.png)

### `sersan_practice_04_donchain_img_0031`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/2005.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/2005.png`
- note: `image_evidence_notes/sersan_practice_04_donchain_img_0031.md`

![sersan_practice_04_donchain_img_0031](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/2005.png)

### `sersan_practice_04_donchain_img_0032`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/030.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/030.png`
- note: `image_evidence_notes/sersan_practice_04_donchain_img_0032.md`

![sersan_practice_04_donchain_img_0032](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/030.png)

### `sersan_practice_04_donchain_img_0033`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/205.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/205.png`
- note: `image_evidence_notes/sersan_practice_04_donchain_img_0033.md`

![sersan_practice_04_donchain_img_0033](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/14-practice-04/img/205.png)

## Warnings

- This is automated corpus distillation, not final doctrine review.
- Image files were opened, hashed and classified through local metadata plus nearby MD context; OCR/value extraction is not yet implemented.
- Code/XLSX artifacts are inventoried through the corpus manifest but not semantically parsed in this run.
