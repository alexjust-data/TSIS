# Lesson Distillation: sersan_practice_07_orb

Title: `Practice 7`
Source MD: `03_only_md_revised/practica_07_ORB.md`
Promotion state: `mechanical_rule_candidate` only; no TSIS doctrine promoted.

## What The Lesson Covers

- `sersan_practice_07_orb_sec_0001` Practice 7. Section classified as unclear. # Practice 7
- `sersan_practice_07_orb_sec_0002` Menú de navegación. Section classified as qa. ## Menú de navegación - [Practice 7](#practice-7) - [Cuestiones](#cuestiones) - [Refactory: `Strategy ORB`](#refactory-strategy-orb) - [Curso-ORB-02 : Strategy](#curso-orb-02--s...
- `sersan_practice_07_orb_sec_0003` Cuestiones. Section classified as qa. ## Cuestiones ***1. ¿Podrías dar alguna referencia en cuanto a umbrales mínimos y máximos de variaciones de combinaciones posibles para una optimización?*** Voy a intentar incid...
- `sersan_practice_07_orb_sec_0004` Refactory: Strategy ORB. Section classified as code_explanation. ## Refactory: `Strategy ORB` <div style="border-left: 4px solid #2196f3; background: #e3f2fd; padding: 10px 15px; margin: 10px 0; border-radius: 8px;"> <strong>📚 Serie ORB - Tob...
- `sersan_practice_07_orb_sec_0005` [Curso-ORB-02 : Strategy](../code/CURSO_ORB_02.ELD). Section classified as money_management. ### [Curso-ORB-02 : Strategy](../code/CURSO_ORB_02.ELD) ```c { ORB con filtro de tendencia en diario, filtro NR y ventana temporal de entrada y salida chart en 10 minutos, 2 dat...
- `sersan_practice_07_orb_sec_0006` Filtros. Section classified as execution_realism. ### Filtros ```sh FiltroEntrada (0), # en tanto por ciento, 0 no actúa FiltroTendencia (0), # Media de cierres diarios, si es 0 no actúa Filtro_NR (0), # número de barras diaria...
- `sersan_practice_07_orb_sec_0007` Filtro Narrow Range. Section classified as procedure. ### Filtro `Narrow Range` El otro filtro que tenemos, después del filtro de tendencia —que simplemente compara el cierre del día anterior del *data2* con la media de *n* barras...
- `sersan_practice_07_orb_sec_0008` Resultados con comisiones y sin comisiones; trampas comunes. Section classified as execution_realism. ### Resultados con comisiones y sin comisiones; trampas comunes Este, `sin comisiones`, pues seguramente ha encontrado mejores resultados. No, habrás encontrado mejores resultad...
- `sersan_practice_07_orb_sec_0009` Exploración de variantes, salidas y optimizaciones. Section classified as execution_realism. ### Exploración de variantes, salidas y optimizaciones Bien, entonces, siguiendo con la explicación de la estrategia, siguiendo con la explicación de los filtros que hay, este s...
- `sersan_practice_07_orb_sec_0010` Pruebas con el DAX (futuros). Section classified as execution_realism. ### Pruebas con el DAX (futuros) Tengo una idea con el DAX, acabando, que es bastante larga... **Evaluación del DAX y configuración del tick** A ver qué hemos encontrado... <fig...
- `sersan_practice_07_orb_sec_0011` Evaluación del sistema y criterios de validación. Section classified as optimization. ### Evaluación del sistema y criterios de validación Si tú miras en *in-sample*, ya veis que *robustness* más bien negativos. *In-sample:* <figure> <img src="../02_workshops/17-...

## Mechanical Rule Candidates

- `sersan_practice_07_orb_rule_0001` [setup_logic, entry_logic, exit_logic, filters, optimization, execution_realism] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_07_orb_rule_0002` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_07_orb_rule_0003` [setup_logic, entry_logic, exit_logic, stop_loss, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_07_orb_rule_0004` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_07_orb_rule_0005` [setup_logic, entry_logic, filters, sample_size, trade_distribution, execution_realism] Execution assumptions discussed in this section must be translated into explicit costs, halt/fill constraints or rejection checks before strategy evaluation.
- `sersan_practice_07_orb_rule_0006` [setup_logic, entry_logic, filters] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_07_orb_rule_0007` [setup_logic, entry_logic, exit_logic, take_profit, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_07_orb_rule_0008` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_07_orb_rule_0009` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_07_orb_rule_0010` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.

## TSIS Translation Candidates

- `sersan_practice_07_orb_tr_0001` -> `execution_realism_check` / `TSIS_EXECUTION_REALISM_CHECK_CANDIDATE`
- `sersan_practice_07_orb_tr_0002` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_07_orb_tr_0003` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_07_orb_tr_0004` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_07_orb_tr_0005` -> `execution_realism_check` / `TSIS_EXECUTION_REALISM_CHECK_CANDIDATE`
- `sersan_practice_07_orb_tr_0006` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_07_orb_tr_0007` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_07_orb_tr_0008` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_07_orb_tr_0009` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_07_orb_tr_0010` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`

## Key Visual Evidence

### `sersan_practice_07_orb_img_0001`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/17-practice-07/img/000.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/000.png`
- note: `image_evidence_notes/sersan_practice_07_orb_img_0001.md`

![sersan_practice_07_orb_img_0001](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/000.png)

### `sersan_practice_07_orb_img_0002`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/17-practice-07/img/001.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/001.png`
- note: `image_evidence_notes/sersan_practice_07_orb_img_0002.md`

![sersan_practice_07_orb_img_0002](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/001.png)

### `sersan_practice_07_orb_img_0003`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/17-practice-07/img/002.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/002.png`
- note: `image_evidence_notes/sersan_practice_07_orb_img_0003.md`

![sersan_practice_07_orb_img_0003](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/002.png)

### `sersan_practice_07_orb_img_0005`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/17-practice-07/img/085.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/085.png`
- note: `image_evidence_notes/sersan_practice_07_orb_img_0005.md`

![sersan_practice_07_orb_img_0005](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/085.png)

### `sersan_practice_07_orb_img_0006`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/17-practice-07/img/004.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/004.png`
- note: `image_evidence_notes/sersan_practice_07_orb_img_0006.md`

![sersan_practice_07_orb_img_0006](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/004.png)

### `sersan_practice_07_orb_img_0007`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/17-practice-07/img/005.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/005.png`
- note: `image_evidence_notes/sersan_practice_07_orb_img_0007.md`

![sersan_practice_07_orb_img_0007](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/005.png)

### `sersan_practice_07_orb_img_0008`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/17-practice-07/img/008.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/008.png`
- note: `image_evidence_notes/sersan_practice_07_orb_img_0008.md`

![sersan_practice_07_orb_img_0008](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/008.png)

### `sersan_practice_07_orb_img_0009`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/17-practice-07/img/007.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/007.png`
- note: `image_evidence_notes/sersan_practice_07_orb_img_0009.md`

![sersan_practice_07_orb_img_0009](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/007.png)

### `sersan_practice_07_orb_img_0010`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/17-practice-07/img/010.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/010.png`
- note: `image_evidence_notes/sersan_practice_07_orb_img_0010.md`

![sersan_practice_07_orb_img_0010](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/010.png)

### `sersan_practice_07_orb_img_0011`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/17-practice-07/img/011.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/011.png`
- note: `image_evidence_notes/sersan_practice_07_orb_img_0011.md`

![sersan_practice_07_orb_img_0011](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/011.png)

### `sersan_practice_07_orb_img_0012`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/17-practice-07/img/012.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/012.png`
- note: `image_evidence_notes/sersan_practice_07_orb_img_0012.md`

![sersan_practice_07_orb_img_0012](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/012.png)

### `sersan_practice_07_orb_img_0013`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/17-practice-07/img/014.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/014.png`
- note: `image_evidence_notes/sersan_practice_07_orb_img_0013.md`

![sersan_practice_07_orb_img_0013](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/17-practice-07/img/014.png)

## Warnings

- This is automated corpus distillation, not final doctrine review.
- Image files were opened, hashed and classified through local metadata plus nearby MD context; OCR/value extraction is not yet implemented.
- Code/XLSX artifacts are inventoried through the corpus manifest but not semantically parsed in this run.
