# Lesson Distillation: sersan_practice_12_revised

Title: `Práctica 12 - Salidas y Gestión de Stops`
Source MD: `03_only_md_revised/practica_12_revised.md`
Promotion state: `mechanical_rule_candidate` only; no TSIS doctrine promoted.

## What The Lesson Covers

- `sersan_practice_12_revised_sec_0001` Práctica 12 - Salidas y Gestión de Stops. Section classified as qa. # Práctica 12 - Salidas y Gestión de Stops 1. [Consultas](#consultas) 2. [Análisis de Stops: Monetario vs Porcentual](#análisis-de-stops-monetario-vs-porcentual) 3. [Strategy `S...
- `sersan_practice_12_revised_sec_0002` Consultas. Section classified as qa. ## Consultas > *Ando trasteando con el mercado de Forex, mercado donde nunca he conseguido nada interesante, dicho sea de paso. Pero viendo tus clases en la práctica comentabas...
- `sersan_practice_12_revised_sec_0003` Análisis de Stops: Monetario vs Porcentual. Section classified as validation. ## Análisis de Stops: Monetario vs Porcentual <video width="640" controls> <source src="../media/Estrategia_de_salida_eficaces.mp4" type="video/mp4"> </video> [Ver video: Estrat...
- `sersan_practice_12_revised_sec_0004` Strategy Salidas_02 : Código con 32 salidas. Section classified as optimization. ## Strategy `Salidas_02` : Código con 32 salidas [Strategy: Salidas_02](../code/CURSO-SALIDAS_02.ELD) Bueno, vamos con la clase de hoy. Queríamos hablar de salidas. Tenemos un c...
- `sersan_practice_12_revised_sec_0005` Strategy : ABERRATION. Section classified as qa. # Strategy : ABERRATION { Copiado de TSM MA BBands: Moving average with Bollinger bands Moving averge systems with entries using Bolllinger bands Copyright 1999-2004, P J Kaufma...
- `sersan_practice_12_revised_sec_0006` Trailing ATR + Profit ATR. Section classified as portfolio. # Trailing ATR + Profit ATR case 11: Input: # Input: Periodo_Salida(14), C11_NumATRs_01 ( 2.5 ), C11_NumATRs_02 ( 4.75 ); C11_NumATRs_01 ( 7.75 ), C11_NumATRs_02 ( 7.25 ); ``` Q...
- `sersan_practice_12_revised_sec_0007` Se calcula solo cuando está cerrado. Section classified as qa. # Se calcula solo cuando está cerrado end else begin SetStopLoss (Close * C16_Stop_Pct / 100 * Bigpointvalue); SetProfitTarget (Close * (C16_Stop_Pct * C16_Profit_NxStopPct) / 1...

## Mechanical Rule Candidates

- `sersan_practice_12_revised_rule_0001` [setup_logic, entry_logic, exit_logic, stop_loss, take_profit, filters] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_12_revised_rule_0002` [exit_logic, stop_loss, filters, optimization, overfitting, robustness] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_12_revised_rule_0003` [bar_construction, price_view, exit_logic, stop_loss, filters, robustness] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_12_revised_rule_0004` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_12_revised_rule_0005` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_12_revised_rule_0006` [setup_logic, entry_logic, exit_logic, stop_loss, take_profit, filters] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_12_revised_rule_0007` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.

## TSIS Translation Candidates

- `sersan_practice_12_revised_tr_0001` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_12_revised_tr_0002` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_12_revised_tr_0003` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_12_revised_tr_0004` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_12_revised_tr_0005` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_12_revised_tr_0006` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_12_revised_tr_0007` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`

## Key Visual Evidence

### `sersan_practice_12_revised_img_0001`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/000.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/000.png`
- note: `image_evidence_notes/sersan_practice_12_revised_img_0001.md`

![sersan_practice_12_revised_img_0001](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/000.png)

### `sersan_practice_12_revised_img_0006`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/009.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/009.png`
- note: `image_evidence_notes/sersan_practice_12_revised_img_0006.md`

![sersan_practice_12_revised_img_0006](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/009.png)

### `sersan_practice_12_revised_img_0007`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/010.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/010.png`
- note: `image_evidence_notes/sersan_practice_12_revised_img_0007.md`

![sersan_practice_12_revised_img_0007](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/010.png)

### `sersan_practice_12_revised_img_0008`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/011.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/011.png`
- note: `image_evidence_notes/sersan_practice_12_revised_img_0008.md`

![sersan_practice_12_revised_img_0008](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/011.png)

### `sersan_practice_12_revised_img_0009`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/012.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/012.png`
- note: `image_evidence_notes/sersan_practice_12_revised_img_0009.md`

![sersan_practice_12_revised_img_0009](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/012.png)

### `sersan_practice_12_revised_img_0010`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/033.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/033.png`
- note: `image_evidence_notes/sersan_practice_12_revised_img_0010.md`

![sersan_practice_12_revised_img_0010](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/033.png)

### `sersan_practice_12_revised_img_0011`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/013.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/013.png`
- note: `image_evidence_notes/sersan_practice_12_revised_img_0011.md`

![sersan_practice_12_revised_img_0011](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/013.png)

### `sersan_practice_12_revised_img_0012`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/014.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/014.png`
- note: `image_evidence_notes/sersan_practice_12_revised_img_0012.md`

![sersan_practice_12_revised_img_0012](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/014.png)

### `sersan_practice_12_revised_img_0013`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/015.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/015.png`
- note: `image_evidence_notes/sersan_practice_12_revised_img_0013.md`

![sersan_practice_12_revised_img_0013](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/015.png)

### `sersan_practice_12_revised_img_0014`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/016.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/016.png`
- note: `image_evidence_notes/sersan_practice_12_revised_img_0014.md`

![sersan_practice_12_revised_img_0014](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/016.png)

### `sersan_practice_12_revised_img_0015`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/034.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/034.png`
- note: `image_evidence_notes/sersan_practice_12_revised_img_0015.md`

![sersan_practice_12_revised_img_0015](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/034.png)

### `sersan_practice_12_revised_img_0016`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/035.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/035.png`
- note: `image_evidence_notes/sersan_practice_12_revised_img_0016.md`

![sersan_practice_12_revised_img_0016](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/22-practice-12/img/035.png)

## Warnings

- This is automated corpus distillation, not final doctrine review.
- Image files were opened, hashed and classified through local metadata plus nearby MD context; OCR/value extraction is not yet implemented.
- Code/XLSX artifacts are inventoried through the corpus manifest but not semantically parsed in this run.
