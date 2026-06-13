# Lesson Distillation: sersan_practice_08_orb

Title: `Practice 8`
Source MD: `03_only_md_revised/practica_08_ORB.md`
Promotion state: `mechanical_rule_candidate` only; no TSIS doctrine promoted.

## What The Lesson Covers

- `sersan_practice_08_orb_sec_0001` Practice 8. Section classified as unclear. # Practice 8
- `sersan_practice_08_orb_sec_0002` Menú de navegación. Section classified as qa. ## Menú de navegación - [Practice 8](#practice-8) - [Cuestiones](#cuestiones) - [ORB](#orb) - [Tipos de filtros aplicables y primeros ejemplos](#tipos-de-filtros-aplicables-y-pr...
- `sersan_practice_08_orb_sec_0003` Cuestiones. Section classified as qa. ## Cuestiones **Configuración del horario del gráfico y diferencias entre "local" y "exchange"** Cuando cargas un símbolo en el gráfico, puedes elegir aquí *local* o *exchange*....
- `sersan_practice_08_orb_sec_0004` ORB. Section classified as warning. ## ORB Al final, tú con un *Volatility Breakout* tal como lo hemos definido hasta ahora, que por supuesto es opcional (todo es opcional en un sistema), es decir, nosotros fijamo...
- `sersan_practice_08_orb_sec_0005` Tipos de filtros aplicables y primeros ejemplos. Section classified as code_explanation. ### Tipos de filtros aplicables y primeros ejemplos ¿En qué se basan esos filtros? Bien, en el que vimos de base había uno típico de tendencia: - ***Momentum***: es decir, si el...
- `sersan_practice_08_orb_sec_0006` eleccionFiltro 1. Section classified as code_explanation. #### `eleccionFiltro 1` <figure> <img src="../02_workshops/18-practice-08/img/031.png" width="800"> <figcaption>Figura 31. Selector de filtros en el ShowMe.</figcaption> </figur...
- `sersan_practice_08_orb_sec_0007` eleccionFiltro 2. Section classified as procedure. #### `eleccionFiltro 2` ***Bien, ahora le ponemos el 2*** $$ C > \text{Average}(13) \quad \text{and} \quad \text{Close} > \text{Open} $$ $$ \text{Cierre mayor que la media de 13...
- `sersan_practice_08_orb_sec_0008` eleccionFiltro 3. Section classified as procedure. #### `eleccionFiltro 3` <figure> <img src="../02_workshops/18-practice-08/img/036.png" width="800"> <figcaption>Figura 36. Filtro 3 aplicado en el gráfico.</figcaption> </figure...
- `sersan_practice_08_orb_sec_0009` eleccionFiltro 4. Section classified as procedure. #### `eleccionFiltro 4` <figure> <img src="../02_workshops/18-practice-08/img/038.png" width="800"> <figcaption>Figura 38. Filtro 4 seleccionado.</figcaption> </figure> El cuart...
- `sersan_practice_08_orb_sec_0010` eleccionFiltro 5. Section classified as portfolio. #### `eleccionFiltro 5` **Preparación para el siguiente filtro: comparación con el cierre y cambios en la lógica** Ahora vamos a hacer lo mismo pero con el cierre. ``` Case 5: i...
- `sersan_practice_08_orb_sec_0011` eleccionFiltro 6. Section classified as procedure. #### `eleccionFiltro 6` Está mezclando ya conceptos, porque sigue introduciendo la media, pero ahora compara el cierre con el *open*, que esto ya lo habíamos hecho antes. Es la...
- `sersan_practice_08_orb_sec_0012` eleccionFiltro 7. Section classified as procedure. #### `eleccionFiltro 7` El 7 pide que el cierre sea menor, es decir, que la tendencia sea alcista, haya volatilidad, pero que el día haya sido bajista. Esa configuración le gust...

## Mechanical Rule Candidates

- `sersan_practice_08_orb_rule_0001` [setup_logic, entry_logic, filters, sample_size, trade_distribution] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_08_orb_rule_0002` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_08_orb_rule_0003` [setup_logic, entry_logic, exit_logic, take_profit, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_08_orb_rule_0004` [setup_logic, entry_logic, exit_logic, stop_loss, filters] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_08_orb_rule_0005` [setup_logic, entry_logic, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_08_orb_rule_0006` [setup_logic, entry_logic, filters] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_08_orb_rule_0007` [setup_logic, entry_logic, filters] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_08_orb_rule_0008` [setup_logic, entry_logic, exit_logic, filters, robustness] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_08_orb_rule_0009` [setup_logic, entry_logic, exit_logic, take_profit, filters, sample_size] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_08_orb_rule_0010` [setup_logic, entry_logic, filters] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_08_orb_rule_0011` [setup_logic, entry_logic, filters, robustness] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_08_orb_rule_0012` [setup_logic, entry_logic, filters] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_08_orb_rule_0013` [setup_logic, entry_logic, filters, sample_size, trade_distribution] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_08_orb_rule_0014` [setup_logic, entry_logic, filters] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_08_orb_rule_0015` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_08_orb_rule_0016` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_08_orb_rule_0017` [filters] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.

## TSIS Translation Candidates

- `sersan_practice_08_orb_tr_0001` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_08_orb_tr_0002` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_08_orb_tr_0003` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_08_orb_tr_0004` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_08_orb_tr_0005` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_08_orb_tr_0006` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_08_orb_tr_0007` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_08_orb_tr_0008` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_08_orb_tr_0009` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_08_orb_tr_0010` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_08_orb_tr_0011` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_08_orb_tr_0012` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_08_orb_tr_0013` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_08_orb_tr_0014` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_08_orb_tr_0015` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_08_orb_tr_0016` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_08_orb_tr_0017` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`

## Key Visual Evidence

### `sersan_practice_08_orb_img_0002`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/18-practice-08/img/000.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/000.png`
- note: `image_evidence_notes/sersan_practice_08_orb_img_0002.md`

![sersan_practice_08_orb_img_0002](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/000.png)

### `sersan_practice_08_orb_img_0003`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/18-practice-08/img/002.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/002.png`
- note: `image_evidence_notes/sersan_practice_08_orb_img_0003.md`

![sersan_practice_08_orb_img_0003](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/002.png)

### `sersan_practice_08_orb_img_0004`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/18-practice-08/img/003.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/003.png`
- note: `image_evidence_notes/sersan_practice_08_orb_img_0004.md`

![sersan_practice_08_orb_img_0004](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/003.png)

### `sersan_practice_08_orb_img_0005`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/18-practice-08/img/004.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/004.png`
- note: `image_evidence_notes/sersan_practice_08_orb_img_0005.md`

![sersan_practice_08_orb_img_0005](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/004.png)

### `sersan_practice_08_orb_img_0006`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/18-practice-08/img/005.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/005.png`
- note: `image_evidence_notes/sersan_practice_08_orb_img_0006.md`

![sersan_practice_08_orb_img_0006](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/005.png)

### `sersan_practice_08_orb_img_0007`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/18-practice-08/img/006.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/006.png`
- note: `image_evidence_notes/sersan_practice_08_orb_img_0007.md`

![sersan_practice_08_orb_img_0007](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/006.png)

### `sersan_practice_08_orb_img_0008`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/18-practice-08/img/007.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/007.png`
- note: `image_evidence_notes/sersan_practice_08_orb_img_0008.md`

![sersan_practice_08_orb_img_0008](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/007.png)

### `sersan_practice_08_orb_img_0009`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/18-practice-08/img/008.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/008.png`
- note: `image_evidence_notes/sersan_practice_08_orb_img_0009.md`

![sersan_practice_08_orb_img_0009](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/008.png)

### `sersan_practice_08_orb_img_0010`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/18-practice-08/img/011.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/011.png`
- note: `image_evidence_notes/sersan_practice_08_orb_img_0010.md`

![sersan_practice_08_orb_img_0010](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/011.png)

### `sersan_practice_08_orb_img_0011`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/18-practice-08/img/009.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/009.png`
- note: `image_evidence_notes/sersan_practice_08_orb_img_0011.md`

![sersan_practice_08_orb_img_0011](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/009.png)

### `sersan_practice_08_orb_img_0012`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/18-practice-08/img/010.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/010.png`
- note: `image_evidence_notes/sersan_practice_08_orb_img_0012.md`

![sersan_practice_08_orb_img_0012](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/010.png)

### `sersan_practice_08_orb_img_0013`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/18-practice-08/img/014.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/014.png`
- note: `image_evidence_notes/sersan_practice_08_orb_img_0013.md`

![sersan_practice_08_orb_img_0013](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/18-practice-08/img/014.png)

## Warnings

- This is automated corpus distillation, not final doctrine review.
- Image files were opened, hashed and classified through local metadata plus nearby MD context; OCR/value extraction is not yet implemented.
- Code/XLSX artifacts are inventoried through the corpus manifest but not semantically parsed in this run.
