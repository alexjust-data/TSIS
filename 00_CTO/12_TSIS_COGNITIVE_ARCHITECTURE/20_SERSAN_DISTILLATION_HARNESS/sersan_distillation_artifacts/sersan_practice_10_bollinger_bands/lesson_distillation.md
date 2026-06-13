# Lesson Distillation: sersan_practice_10_bollinger_bands

Title: `Practice 10`
Source MD: `03_only_md_revised/practica_10_bollinger_bands.md`
Promotion state: `mechanical_rule_candidate` only; no TSIS doctrine promoted.

## What The Lesson Covers

- `sersan_practice_10_bollinger_bands_sec_0001` Practice 10. Section classified as unclear. # Practice 10
- `sersan_practice_10_bollinger_bands_sec_0002` Cuestiones. Section classified as qa. ## Cuestiones **El debate entre Builders y No Builders en el Trading Algorítmico** Es interesante porque se abrió un debate ahí entre *builders* y *no builders*. Para quien no l...
- `sersan_practice_10_bollinger_bands_sec_0003` Apolo - tema cerrado. Section classified as optimization. ## Apolo - tema cerrado El tema de Apolo quedó claro. No hay más que añadir. Si alguien tiene algo que hable ahora o calle para siempre. Ya si lo preguntáis en Discord le contes...
- `sersan_practice_10_bollinger_bands_sec_0004` Strategy Bandas de Bollinger - Antitendencial. Section classified as optimization. ## Strategy `Bandas de Bollinger` - Antitendencial Hoy vamos a empezar por la parte *antitendencial*. Aprovecho para enseñaros esto. Yo creo que sí que lo podemos dar, Alberto,...
- `sersan_practice_10_bollinger_bands_sec_0005` La versión original - Strategy : STAD23 Bollinger Bands. Section classified as qa. ### La versión original - Strategy : STAD23 Bollinger Bands Entonces, bueno, la versión principal que la he revisado bien, explicado, también os la pondré al final. <figure> <im...
- `sersan_practice_10_bollinger_bands_sec_0006` Refactoring - Strategy : STAD23 Bollinger Bands 1. Section classified as qa. ### Refactoring - Strategy : STAD23 Bollinger Bands 1 Strategy : [STAD23 Bollinger Bands 1](../code/SATD23%20BOLLINGER%20BANDS%2001.ELD) **Maneras de tratar las bandas de Bollin...
- `sersan_practice_10_bollinger_bands_sec_0007` Análisis del Sistema Original en Diario. Section classified as optimization. ### Análisis del Sistema Original en Diario tsw : [10-Curso-MeanReversion(esd).tsw](../code/10-Curso-MeanReversion(esd).tsw) Tengo 4 gráficos abiertos con 4 variaciones de la es...
- `sersan_practice_10_bollinger_bands_sec_0008` Comparación Diario vs Intradía. Section classified as optimization. ### Comparación Diario vs Intradía - [STAD23 Bollinger Bands-intradia-01](../code/STAD23%20BOLLINGER%20BANDS-INTRADIA-%2001.ELD) - [STAD23 Bollinger Bands-01](../code/SATD23%20B...
- `sersan_practice_10_bollinger_bands_sec_0009` Optimización en MultiCharts. Section classified as qa. ## Optimización en MultiCharts Vamos a ver qué tenemos por aquí, todavía estamos cargando. Bueno pues nada... Bueno, tengo este abierto aquí. De momento vamos a trabajar previam...
- `sersan_practice_10_bollinger_bands_sec_0010` Pregunta: Optimizar Timeframe. Section classified as qa. ## Pregunta: Optimizar Timeframe ***Prueba de estrés*** Y bueno, vamos a ir. Preguntaba José por el tema de optimizar el *timeframe*. No, no me consta que haya una forma ni senc...

## Mechanical Rule Candidates

- `sersan_practice_10_bollinger_bands_rule_0001` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_10_bollinger_bands_rule_0002` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_10_bollinger_bands_rule_0003` [bar_construction, price_view, setup_logic, entry_logic, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_10_bollinger_bands_rule_0004` [setup_logic, entry_logic, exit_logic] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_10_bollinger_bands_rule_0005` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_10_bollinger_bands_rule_0006` [setup_logic, entry_logic, exit_logic, stop_loss, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_10_bollinger_bands_rule_0007` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_10_bollinger_bands_rule_0008` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_10_bollinger_bands_rule_0009` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.

## TSIS Translation Candidates

- `sersan_practice_10_bollinger_bands_tr_0001` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_10_bollinger_bands_tr_0002` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_10_bollinger_bands_tr_0003` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_10_bollinger_bands_tr_0004` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_10_bollinger_bands_tr_0005` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_10_bollinger_bands_tr_0006` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_10_bollinger_bands_tr_0007` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_10_bollinger_bands_tr_0008` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_10_bollinger_bands_tr_0009` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`

## Key Visual Evidence

### `sersan_practice_10_bollinger_bands_img_0001`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/20-practice-10/img/000.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/000.png`
- note: `image_evidence_notes/sersan_practice_10_bollinger_bands_img_0001.md`

![sersan_practice_10_bollinger_bands_img_0001](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/000.png)

### `sersan_practice_10_bollinger_bands_img_0002`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/20-practice-10/img/001.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/001.png`
- note: `image_evidence_notes/sersan_practice_10_bollinger_bands_img_0002.md`

![sersan_practice_10_bollinger_bands_img_0002](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/001.png)

### `sersan_practice_10_bollinger_bands_img_0003`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/20-practice-10/img/003.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/003.png`
- note: `image_evidence_notes/sersan_practice_10_bollinger_bands_img_0003.md`

![sersan_practice_10_bollinger_bands_img_0003](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/003.png)

### `sersan_practice_10_bollinger_bands_img_0004`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/20-practice-10/img/004.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/004.png`
- note: `image_evidence_notes/sersan_practice_10_bollinger_bands_img_0004.md`

![sersan_practice_10_bollinger_bands_img_0004](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/004.png)

### `sersan_practice_10_bollinger_bands_img_0005`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/20-practice-10/img/005.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/005.png`
- note: `image_evidence_notes/sersan_practice_10_bollinger_bands_img_0005.md`

![sersan_practice_10_bollinger_bands_img_0005](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/005.png)

### `sersan_practice_10_bollinger_bands_img_0006`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/20-practice-10/img/006.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/006.png`
- note: `image_evidence_notes/sersan_practice_10_bollinger_bands_img_0006.md`

![sersan_practice_10_bollinger_bands_img_0006](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/006.png)

### `sersan_practice_10_bollinger_bands_img_0007`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/20-practice-10/img/007.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/007.png`
- note: `image_evidence_notes/sersan_practice_10_bollinger_bands_img_0007.md`

![sersan_practice_10_bollinger_bands_img_0007](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/007.png)

### `sersan_practice_10_bollinger_bands_img_0008`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/20-practice-10/img/008.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/008.png`
- note: `image_evidence_notes/sersan_practice_10_bollinger_bands_img_0008.md`

![sersan_practice_10_bollinger_bands_img_0008](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/008.png)

### `sersan_practice_10_bollinger_bands_img_0009`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/20-practice-10/img/009.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/009.png`
- note: `image_evidence_notes/sersan_practice_10_bollinger_bands_img_0009.md`

![sersan_practice_10_bollinger_bands_img_0009](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/009.png)

### `sersan_practice_10_bollinger_bands_img_0010`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/20-practice-10/img/010.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/010.png`
- note: `image_evidence_notes/sersan_practice_10_bollinger_bands_img_0010.md`

![sersan_practice_10_bollinger_bands_img_0010](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/010.png)

### `sersan_practice_10_bollinger_bands_img_0011`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/20-practice-10/img/012.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/012.png`
- note: `image_evidence_notes/sersan_practice_10_bollinger_bands_img_0011.md`

![sersan_practice_10_bollinger_bands_img_0011](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/012.png)

### `sersan_practice_10_bollinger_bands_img_0012`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/20-practice-10/img/013.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/013.png`
- note: `image_evidence_notes/sersan_practice_10_bollinger_bands_img_0012.md`

![sersan_practice_10_bollinger_bands_img_0012](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/20-practice-10/img/013.png)

## Warnings

- This is automated corpus distillation, not final doctrine review.
- Image files were opened, hashed and classified through local metadata plus nearby MD context; OCR/value extraction is not yet implemented.
- Code/XLSX artifacts are inventoried through the corpus manifest but not semantically parsed in this run.
