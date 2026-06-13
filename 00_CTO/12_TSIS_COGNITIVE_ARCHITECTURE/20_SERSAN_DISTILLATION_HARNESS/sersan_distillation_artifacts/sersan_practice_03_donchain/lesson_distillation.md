# Lesson Distillation: sersan_practice_03_donchain

Title: `Índice`
Source MD: `03_only_md_revised/practica_03_donchain.md`
Promotion state: `mechanical_rule_candidate` only; no TSIS doctrine promoted.

## What The Lesson Covers

- `sersan_practice_03_donchain_sec_0001` Índice. Section classified as qa. ## Índice - [Bases diarias vs Bases intradiarias (1440 minutos) - Recordatorio del tema anterior](#bases-diarias-vs-bases-intradiarias-1440-minutos---recordatorio-del-tema-anter...
- `sersan_practice_03_donchain_sec_0002` Bases diarias vs Bases intradiarias (1440 minutos). Section classified as validation. # Bases diarias vs Bases intradiarias (1440 minutos) La semana pasada introdujimos los **canales de Donchian**, y hoy, antes de continuar con ese tema (aunque está relacionado),...
- `sersan_practice_03_donchain_sec_0003` Introducción - canales de Donchian. Section classified as qa. # Introducción - `canales de Donchian` *code* : [ PRACTICE 02](../code/PRACTICA%2002.ELD) ![](../../12-practice-02/img/002.png) He querido empezar por este sistema porque es uno...
- `sersan_practice_03_donchain_sec_0004` 🟦 Aplicación práctica: Donchian en Apple AAPL. Section classified as optimization. ## 🟦 Aplicación práctica: Donchian en Apple `AAPL` En este punto del curso, hemos planteado un *sistema Donchian* basado en datos diarios. La última vez lo probamos con *Apple*,...
- `sersan_practice_03_donchain_sec_0005` Aplicación práctica: Donchian en XLK. Section classified as money_management. ## Aplicación práctica: Donchian en `XLK` Como ya comentamos, es esencial probar el sistema en distintos activos. Aquí lo aplicamos sobre el **ETF sectorial de tecnología `XLK`*...
- `sersan_practice_03_donchain_sec_0006` Regla de entrada. Section classified as money_management. ### Regla de entrada La entrada sigue siendo la ruptura clásica de Donchian: ```sh Begin if Close > Highest(Price_Up, Per_Canal)[1] then Buy Contratos contracts Next Bar at Mark...
- `sersan_practice_03_donchain_sec_0007` 🟦 Aplicación práctica: Donchian en XLF. Section classified as execution_realism. ## 🟦 Aplicación práctica: Donchian en `XLF` Seguimos con más opciones, ya me ha cargado el sector financiero `XLF` que es tremendamente volátil <figure> <img src="../02_workshop...
- `sersan_practice_03_donchain_sec_0008` ¿que salidas hemos visto ya?. Section classified as optimization. ### ¿que salidas hemos visto ya? Bien, continuamos analizando las demás posibilidades. El otro día recordaréis que ya implementé la *salida por tiempo*, una opción que personalm...
- `sersan_practice_03_donchain_sec_0009` implemento salida en el canal contrario. Section classified as money_management. ### implemento salida en el canal contrario También podríamos haber definido una *salida en el canal contrario*, una alternativa más de largo recorrido. Esa opción, de hecho, ya...
- `sersan_practice_03_donchain_sec_0010` Combinación práctica de salidas: media, tiempo y stop porcentual. Section classified as procedure. ### Combinación práctica de salidas: media, tiempo y stop porcentual ...entonces vamos a desactivar los cortos; lo voy a dejar así para que salga por la media, va a salir por el...
- `sersan_practice_03_donchain_sec_0011` Filtros de entrada. Section classified as procedure. ### Filtros de entrada En este mismo *setup*, para no complicar demasiado la explicación, repasaremos algunos posibles filtros de entrada.
- `sersan_practice_03_donchain_sec_0012` Filtro que evita reentradas inmediatas Bar_Filtro. Section classified as warning. #### Filtro que evita reentradas inmediatas `Bar_Filtro`** El primero es un filtro diseñado para evitar que ocurra lo que se observa en la imagen: una *reentrada inmediata* tras...

## Mechanical Rule Candidates

- `sersan_practice_03_donchain_rule_0001` [bar_construction, price_view, setup_logic, entry_logic, filters, money_management] Money-management or sizing effects from this section must be evaluated separately from raw strategy edge and with drawdown/aggressiveness sensitivity.
- `sersan_practice_03_donchain_rule_0002` [bar_construction, price_view, setup_logic, entry_logic, optimization, sample_size] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_03_donchain_rule_0003` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, take_profit] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_03_donchain_rule_0004` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_03_donchain_rule_0005` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, take_profit] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_03_donchain_rule_0006` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_03_donchain_rule_0007` [setup_logic, entry_logic, exit_logic, take_profit, optimization, execution_realism] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_03_donchain_rule_0008` [setup_logic, entry_logic, exit_logic, stop_loss, take_profit, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_03_donchain_rule_0009` [setup_logic, entry_logic, exit_logic, stop_loss, take_profit, robustness] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_03_donchain_rule_0010` [setup_logic, entry_logic, exit_logic, stop_loss, take_profit, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_03_donchain_rule_0011` [setup_logic, entry_logic, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_03_donchain_rule_0012` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, filters] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_03_donchain_rule_0013` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_03_donchain_rule_0014` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_03_donchain_rule_0015` [bar_construction, price_view, setup_logic, entry_logic, filters, regime] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_03_donchain_rule_0016` [setup_logic, entry_logic] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_03_donchain_rule_0017` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_03_donchain_rule_0018` [setup_logic, entry_logic] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_03_donchain_rule_0019` [bar_construction, price_view, setup_logic, entry_logic] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_03_donchain_rule_0020` [setup_logic, entry_logic] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_03_donchain_rule_0021` [setup_logic, entry_logic] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_03_donchain_rule_0022` [setup_logic, entry_logic, filters] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_03_donchain_rule_0023` [setup_logic, entry_logic, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_03_donchain_rule_0024` [setup_logic, entry_logic, exit_logic, money_management, position_sizing] Money-management or sizing effects from this section must be evaluated separately from raw strategy edge and with drawdown/aggressiveness sensitivity.
- `sersan_practice_03_donchain_rule_0025` [setup_logic, entry_logic, exit_logic, robustness] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_03_donchain_rule_0026` [setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_03_donchain_rule_0027` [setup_logic, entry_logic, exit_logic, take_profit, money_management, position_sizing] Money-management or sizing effects from this section must be evaluated separately from raw strategy edge and with drawdown/aggressiveness sensitivity.
- `sersan_practice_03_donchain_rule_0028` [setup_logic, entry_logic, exit_logic] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_03_donchain_rule_0029` [bar_construction, price_view, setup_logic, entry_logic, money_management, position_sizing] Money-management or sizing effects from this section must be evaluated separately from raw strategy edge and with drawdown/aggressiveness sensitivity.
- `sersan_practice_03_donchain_rule_0030` [bar_construction, price_view, setup_logic, entry_logic, optimization, robustness] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_03_donchain_rule_0031` [setup_logic, entry_logic, exit_logic, filters, optimization, sample_size] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.

## TSIS Translation Candidates

- `sersan_practice_03_donchain_tr_0001` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_03_donchain_tr_0002` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_03_donchain_tr_0003` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_03_donchain_tr_0004` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_03_donchain_tr_0005` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_03_donchain_tr_0006` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_03_donchain_tr_0007` -> `execution_realism_check` / `TSIS_EXECUTION_REALISM_CHECK_CANDIDATE`
- `sersan_practice_03_donchain_tr_0008` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_03_donchain_tr_0009` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_03_donchain_tr_0010` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_03_donchain_tr_0011` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_03_donchain_tr_0012` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_03_donchain_tr_0013` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_03_donchain_tr_0014` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_03_donchain_tr_0015` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_03_donchain_tr_0016` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_03_donchain_tr_0017` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_03_donchain_tr_0018` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_03_donchain_tr_0019` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_03_donchain_tr_0020` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_03_donchain_tr_0021` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_03_donchain_tr_0022` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_03_donchain_tr_0023` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_03_donchain_tr_0024` -> `money_management_policy` / `TSIS_MONEY_MANAGEMENT_POLICY_CANDIDATE`
- `sersan_practice_03_donchain_tr_0025` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_03_donchain_tr_0026` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_03_donchain_tr_0027` -> `money_management_policy` / `TSIS_MONEY_MANAGEMENT_POLICY_CANDIDATE`
- `sersan_practice_03_donchain_tr_0028` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_03_donchain_tr_0029` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_03_donchain_tr_0030` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_03_donchain_tr_0031` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`

## Key Visual Evidence

### `sersan_practice_03_donchain_img_0006`

- relevance: `critical`
- visual_type: `drawdown_curve`
- source_ref: `../../12-practice-02/img/002.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/12-practice-02/img/002.png`
- note: `image_evidence_notes/sersan_practice_03_donchain_img_0006.md`

![sersan_practice_03_donchain_img_0006](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/12-practice-02/img/002.png)

### `sersan_practice_03_donchain_img_0007`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../../13-practice-03/img/00.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/00.png`
- note: `image_evidence_notes/sersan_practice_03_donchain_img_0007.md`

![sersan_practice_03_donchain_img_0007](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/00.png)

### `sersan_practice_03_donchain_img_0008`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/13-practice-03/img/01.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/01.png`
- note: `image_evidence_notes/sersan_practice_03_donchain_img_0008.md`

![sersan_practice_03_donchain_img_0008](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/01.png)

### `sersan_practice_03_donchain_img_0009`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/13-practice-03/img/02.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/02.png`
- note: `image_evidence_notes/sersan_practice_03_donchain_img_0009.md`

![sersan_practice_03_donchain_img_0009](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/02.png)

### `sersan_practice_03_donchain_img_0010`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/13-practice-03/img/04.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/04.png`
- note: `image_evidence_notes/sersan_practice_03_donchain_img_0010.md`

![sersan_practice_03_donchain_img_0010](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/04.png)

### `sersan_practice_03_donchain_img_0011`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/13-practice-03/img/05.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/05.png`
- note: `image_evidence_notes/sersan_practice_03_donchain_img_0011.md`

![sersan_practice_03_donchain_img_0011](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/05.png)

### `sersan_practice_03_donchain_img_0012`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/13-practice-03/img/06.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/06.png`
- note: `image_evidence_notes/sersan_practice_03_donchain_img_0012.md`

![sersan_practice_03_donchain_img_0012](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/06.png)

### `sersan_practice_03_donchain_img_0013`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/13-practice-03/img/07.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/07.png`
- note: `image_evidence_notes/sersan_practice_03_donchain_img_0013.md`

![sersan_practice_03_donchain_img_0013](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/07.png)

### `sersan_practice_03_donchain_img_0014`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/13-practice-03/img/15.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/15.png`
- note: `image_evidence_notes/sersan_practice_03_donchain_img_0014.md`

![sersan_practice_03_donchain_img_0014](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/15.png)

### `sersan_practice_03_donchain_img_0015`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/13-practice-03/img/16.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/16.png`
- note: `image_evidence_notes/sersan_practice_03_donchain_img_0015.md`

![sersan_practice_03_donchain_img_0015](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/16.png)

### `sersan_practice_03_donchain_img_0016`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/13-practice-03/img/17.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/17.png`
- note: `image_evidence_notes/sersan_practice_03_donchain_img_0016.md`

![sersan_practice_03_donchain_img_0016](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/17.png)

### `sersan_practice_03_donchain_img_0017`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/13-practice-03/img/18.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/18.png`
- note: `image_evidence_notes/sersan_practice_03_donchain_img_0017.md`

![sersan_practice_03_donchain_img_0017](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/13-practice-03/img/18.png)

## Warnings

- This is automated corpus distillation, not final doctrine review.
- Image files were opened, hashed and classified through local metadata plus nearby MD context; OCR/value extraction is not yet implemented.
- Code/XLSX artifacts are inventoried through the corpus manifest but not semantically parsed in this run.
