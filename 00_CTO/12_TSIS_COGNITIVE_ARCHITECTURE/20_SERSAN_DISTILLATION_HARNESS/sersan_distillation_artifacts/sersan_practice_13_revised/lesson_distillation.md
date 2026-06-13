# Lesson Distillation: sersan_practice_13_revised

Title: `Práctica 13 - Sistemas Tendenciales en el Oro`
Source MD: `03_only_md_revised/practica_13_revised.md`
Promotion state: `mechanical_rule_candidate` only; no TSIS doctrine promoted.

## What The Lesson Covers

- `sersan_practice_13_revised_sec_0001` Práctica 13 - Sistemas Tendenciales en el Oro. Section classified as concept. # Práctica 13 - Sistemas Tendenciales en el Oro
- `sersan_practice_13_revised_sec_0002` Índice. Section classified as qa. ## Índice 1. [Consultas](#consultas) 2. [Sistemas del Oro](#sistemas-del-oro) 3. [Sistema `Parabolic SAR`](#sistema-parabolic-sar) 4. [ORO con Sistemas tendenciales](#aplicacion...
- `sersan_practice_13_revised_sec_0003` Consultas. Section classified as qa. ## Consultas Bien, empezamos como siempre dando un repasito breve al *Discord*. Había alguna cosita que comentar. Bueno, Alejandro había añadido al hilo de... ***Buenas de nuevo...
- `sersan_practice_13_revised_sec_0004` Sistemas del Oro. Section classified as qa. ## Sistemas del Oro **El oro como activo tendencial** Bien, vamos a trabajar un *tendencial* en el oro. ¿Por qué un tendencial en el oro? Bueno, el oro es un activo bastante ten...
- `sersan_practice_13_revised_sec_0005` Sistema Parabolic SAR. Section classified as qa. ## Sistema Parabolic SAR [Revista: July 2015](../docs/STRATEGY%20CONCEPTS/STRATEGY%20CONCEPTS/2015-07/SCC%20Issue%207%20Jul%202015.pdf) <figure> <img src="../img/190.png" width=...
- `sersan_practice_13_revised_sec_0006` Aplicación de sistemas tendenciales en el oro. Section classified as qa. ## Aplicación de sistemas tendenciales en el oro Bien, vamos al oro, vamos al otro sistema tendencial de base, que hemos hecho aquí. Hemos dicho, oye, ¿cuál es el indicador tend...
- `sersan_practice_13_revised_sec_0007` Visualización de los cases. Section classified as concept. ## Visualización de los cases Vamos a poner esto en el gráfico para que lo veáis, para que lo veáis un poco en la práctica. Veis qué pasa con una media muy rápida con una lenta,...
- `sersan_practice_13_revised_sec_0008` Caso Fast_Avg 7 con media 3. Section classified as execution_realism. ### Caso Fast_Avg 7 con media 3 Recordar que el parámetro que pongo, bueno, por eso lo pinto en el gráfico y viene muy bien: - La media *slow* siempre es 46. - La *fast*, si pon...
- `sersan_practice_13_revised_sec_0009` Caso Fast_Avg 20 con media 11. Section classified as optimization. #### Caso `Fast_Avg 20` con `media 11` <figure> <img src="../img/052.png" width="600"> <figcaption>Figura 052</figcaption> </figure> **Análisis del periodo de mercado** ```sh TP...
- `sersan_practice_13_revised_sec_0010` Caso Fast_Avg 33 con media 2. Section classified as optimization. #### Caso `Fast_Avg 33` con `media 2` <figure> <img src="../img/068.png" width="600"> <figcaption>Figura 068</figcaption> </figure> Volvemos aquí, 33-2, esto lo dejo quieto, aco...
- `sersan_practice_13_revised_sec_0011` Caso Fast_Avg 7 con media 3. Section classified as procedure. #### Caso `Fast_Avg 7` con `media 3` <figure> <img src="../img/084.png" width="600"> <figcaption>Figura 084</figcaption> </figure> Entonces 7-3, esto, fijaros las medidas cómo c...
- `sersan_practice_13_revised_sec_0012` Implementación de salidas a los sistemas tendenciales. Section classified as optimization. ## Implementación de salidas a los sistemas tendenciales Bien, pues con esto teníamos un poquito dos medias elegidas. Vamos a ver si podemos a través de las salidas, a través de...

## Mechanical Rule Candidates

- `sersan_practice_13_revised_rule_0001` [setup_logic, entry_logic, exit_logic, stop_loss, take_profit, filters] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_13_revised_rule_0002` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_13_revised_rule_0003` [optimization, overfitting, sample_size, trade_distribution] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_13_revised_rule_0004` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_13_revised_rule_0005` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_13_revised_rule_0006` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_13_revised_rule_0007` [exit_logic, filters, optimization, robustness, sample_size, trade_distribution] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_13_revised_rule_0008` [setup_logic, entry_logic, exit_logic, take_profit, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_13_revised_rule_0009` [bar_construction, price_view] Data representation choices from this section must be declared before using results as strategy evidence.
- `sersan_practice_13_revised_rule_0010` [exit_logic, stop_loss, take_profit, filters, optimization, robustness] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_13_revised_rule_0011` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_13_revised_rule_0012` [exit_logic, take_profit, optimization, overfitting, robustness, sample_size] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_13_revised_rule_0013` [exit_logic, take_profit, filters, optimization, overfitting, robustness] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_13_revised_rule_0014` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.

## TSIS Translation Candidates

- `sersan_practice_13_revised_tr_0001` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_13_revised_tr_0002` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_13_revised_tr_0003` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_13_revised_tr_0004` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_13_revised_tr_0005` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_13_revised_tr_0006` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_13_revised_tr_0007` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_13_revised_tr_0008` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_13_revised_tr_0009` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_13_revised_tr_0010` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_13_revised_tr_0011` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_13_revised_tr_0012` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_13_revised_tr_0013` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_13_revised_tr_0014` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`

## Key Visual Evidence

### `sersan_practice_13_revised_img_0001`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/000.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/000.png`
- note: `image_evidence_notes/sersan_practice_13_revised_img_0001.md`

![sersan_practice_13_revised_img_0001](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/000.png)

### `sersan_practice_13_revised_img_0002`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/190.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/190.png`
- note: `image_evidence_notes/sersan_practice_13_revised_img_0002.md`

![sersan_practice_13_revised_img_0002](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/190.png)

### `sersan_practice_13_revised_img_0003`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/001.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/001.png`
- note: `image_evidence_notes/sersan_practice_13_revised_img_0003.md`

![sersan_practice_13_revised_img_0003](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/001.png)

### `sersan_practice_13_revised_img_0004`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/002.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/002.png`
- note: `image_evidence_notes/sersan_practice_13_revised_img_0004.md`

![sersan_practice_13_revised_img_0004](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/002.png)

### `sersan_practice_13_revised_img_0005`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/003.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/003.png`
- note: `image_evidence_notes/sersan_practice_13_revised_img_0005.md`

![sersan_practice_13_revised_img_0005](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/003.png)

### `sersan_practice_13_revised_img_0006`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/004.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/004.png`
- note: `image_evidence_notes/sersan_practice_13_revised_img_0006.md`

![sersan_practice_13_revised_img_0006](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/004.png)

### `sersan_practice_13_revised_img_0007`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/192.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/192.png`
- note: `image_evidence_notes/sersan_practice_13_revised_img_0007.md`

![sersan_practice_13_revised_img_0007](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/192.png)

### `sersan_practice_13_revised_img_0008`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/005.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/005.png`
- note: `image_evidence_notes/sersan_practice_13_revised_img_0008.md`

![sersan_practice_13_revised_img_0008](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/005.png)

### `sersan_practice_13_revised_img_0009`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/008.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/008.png`
- note: `image_evidence_notes/sersan_practice_13_revised_img_0009.md`

![sersan_practice_13_revised_img_0009](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/008.png)

### `sersan_practice_13_revised_img_0010`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/007.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/007.png`
- note: `image_evidence_notes/sersan_practice_13_revised_img_0010.md`

![sersan_practice_13_revised_img_0010](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/007.png)

### `sersan_practice_13_revised_img_0011`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/009.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/009.png`
- note: `image_evidence_notes/sersan_practice_13_revised_img_0011.md`

![sersan_practice_13_revised_img_0011](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/009.png)

### `sersan_practice_13_revised_img_0012`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/010.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/010.png`
- note: `image_evidence_notes/sersan_practice_13_revised_img_0012.md`

![sersan_practice_13_revised_img_0012](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/23-practice-13/img/010.png)

## Warnings

- This is automated corpus distillation, not final doctrine review.
- Image files were opened, hashed and classified through local metadata plus nearby MD context; OCR/value extraction is not yet implemented.
- Code/XLSX artifacts are inventoried through the corpus manifest but not semantically parsed in this run.
