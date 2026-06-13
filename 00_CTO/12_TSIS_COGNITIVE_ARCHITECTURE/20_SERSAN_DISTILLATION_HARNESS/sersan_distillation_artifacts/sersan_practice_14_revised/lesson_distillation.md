# Lesson Distillation: sersan_practice_14_revised

Title: `Práctica 14 - Buscador de Entradas y Sistema Tomorrow's Trend`
Source MD: `03_only_md_revised/practica_14_revised.md`
Promotion state: `mechanical_rule_candidate` only; no TSIS doctrine promoted.

## What The Lesson Covers

- `sersan_practice_14_revised_sec_0001` Práctica 14 - Buscador de Entradas y Sistema Tomorrow's Trend. Section classified as procedure. # Práctica 14 - Buscador de Entradas y Sistema Tomorrow's Trend
- `sersan_practice_14_revised_sec_0002` Índice. Section classified as qa. ## Índice - [Consultas](#consultas) - [Repaso del sistema de sesion pasada: medias móviles](#repaso-del-sistema-de-sesion-pasada-medias-móviles) - [Prueba del filtro Donchian](#...
- `sersan_practice_14_revised_sec_0003` Consultas. Section classified as qa. ## Consultas **Respuestas a preguntas sobre estrategias y diversificación** > *Buenas @Sersan Sistemas. Misma pelea de los últimos comentarios jaja, pero a ver tu opinión sobre...
- `sersan_practice_14_revised_sec_0004` Repaso del sistema de sesion pasada: medias móviles. Section classified as execution_realism. ## Repaso del sistema de sesion pasada: `medias móviles` Bien, por hacer un pequeño recordatorio, acordaros que probamos distintas medias, vimos, hicimos un *switch* con diferen...
- `sersan_practice_14_revised_sec_0005` Prueba del filtro Donchian. Section classified as procedure. ### Prueba del filtro `Donchian` Posible mejora es lo que os decía, simplemente activar el *Donchian*. <figure> <img src="../img/009.png" width="800"> <figcaption>Figura 009</fi...
- `sersan_practice_14_revised_sec_0006` Walk Forward: análisis con programa externo. Section classified as portfolio. ### Walk Forward: análisis con programa externo Bien, vamos a ver lo que os decía, estáis viendo aquí un *Walk Forward*. Tenemos un programa externo, pero da igual, le podéis us...
- `sersan_practice_14_revised_sec_0007` Filtros para sistemas tendenciales: evitar expansión. Section classified as code_explanation. ## Filtros para sistemas tendenciales: evitar expansión A nivel de filtros, para acabar ya esto, ¿vale?, ir un poco a algo... bueno creo que eso también es interesante. Pero par...
- `sersan_practice_14_revised_sec_0008` Uso de indicadores Show Me para visualizar filtros. Section classified as optimization. ## Uso de indicadores `Show Me` para visualizar filtros A nivel sobre todo para que veáis lo que os decía, me voy a poneros un ejemplo que casi va a ser más fácil que lo veáis....
- `sersan_practice_14_revised_sec_0009` Implementación de filtros con switch-case. Section classified as optimization. ## Implementación de filtros con switch-case Entonces hemos probado distintos filtros. Nuevamente, la manera de programarlos es igual con el *case*, ¿vale? - [Function: Nuestras...
- `sersan_practice_14_revised_sec_0010` case 4 Filtro : Wide Spread. Section classified as validation. ### `case 4` Filtro : Wide Spread Es decir, evitar entrar después de mucha expansión, ¿entendéis? Es decir, una vela de expansión de novedad, evitar entrar ahí. Eso es un poco l...
- `sersan_practice_14_revised_sec_0011` case 3 Filtro : Narrow Range. Section classified as warning. ### `case 3` Filtro : Narrow Range A ver, podemos probarlo rápidamente porque no tarda mucho. Sea un el *narrow* que era 3, ```sh Case 3: NuestrasPatternDirectionalFast = Narrow...
- `sersan_practice_14_revised_sec_0012` case 7 WideSpread. Section classified as procedure. ### `case 7` WideSpread 7 y 8 es el *wide spread*. Incluso a ver, una cosa, ya tengo curiosidad si ya está aquí. ```sh case 7: NuestrasPatternDirectionalFast = true; case -7: Nu...

## Mechanical Rule Candidates

- `sersan_practice_14_revised_rule_0001` [setup_logic, entry_logic] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_14_revised_rule_0002` [setup_logic, entry_logic, exit_logic, filters, walk_forward] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_14_revised_rule_0003` [bar_construction, price_view, setup_logic, entry_logic, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_14_revised_rule_0004` [setup_logic, entry_logic, exit_logic, filters, optimization, robustness] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_14_revised_rule_0005` [setup_logic, entry_logic, exit_logic, filters, sample_size, trade_distribution] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_14_revised_rule_0006` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_14_revised_rule_0007` [setup_logic, entry_logic, exit_logic, filters] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_14_revised_rule_0008` [bar_construction, price_view, setup_logic, entry_logic, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_14_revised_rule_0009` [setup_logic, entry_logic, exit_logic, filters, optimization, market_microstructure] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_14_revised_rule_0010` [setup_logic, entry_logic, filters, sample_size, trade_distribution, market_microstructure] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_14_revised_rule_0011` [setup_logic, entry_logic, filters, market_microstructure] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_14_revised_rule_0012` [setup_logic, entry_logic, filters, market_microstructure] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_14_revised_rule_0013` [setup_logic, entry_logic, exit_logic, stop_loss, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_14_revised_rule_0014` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, filters] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_14_revised_rule_0015` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_14_revised_rule_0016` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_14_revised_rule_0017` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.

## TSIS Translation Candidates

- `sersan_practice_14_revised_tr_0001` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_14_revised_tr_0002` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_14_revised_tr_0003` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_14_revised_tr_0004` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_14_revised_tr_0005` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_14_revised_tr_0006` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_14_revised_tr_0007` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_14_revised_tr_0008` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_14_revised_tr_0009` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_14_revised_tr_0010` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_14_revised_tr_0011` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_14_revised_tr_0012` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_14_revised_tr_0013` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_14_revised_tr_0014` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_14_revised_tr_0015` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_14_revised_tr_0016` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_14_revised_tr_0017` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`

## Key Visual Evidence

### `sersan_practice_14_revised_img_0001`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/000.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/000.png`
- note: `image_evidence_notes/sersan_practice_14_revised_img_0001.md`

![sersan_practice_14_revised_img_0001](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/000.png)

### `sersan_practice_14_revised_img_0002`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/001.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/001.png`
- note: `image_evidence_notes/sersan_practice_14_revised_img_0002.md`

![sersan_practice_14_revised_img_0002](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/001.png)

### `sersan_practice_14_revised_img_0019`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/018.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/018.png`
- note: `image_evidence_notes/sersan_practice_14_revised_img_0019.md`

![sersan_practice_14_revised_img_0019](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/018.png)

### `sersan_practice_14_revised_img_0020`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/019.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/019.png`
- note: `image_evidence_notes/sersan_practice_14_revised_img_0020.md`

![sersan_practice_14_revised_img_0020](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/019.png)

### `sersan_practice_14_revised_img_0021`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/020.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/020.png`
- note: `image_evidence_notes/sersan_practice_14_revised_img_0021.md`

![sersan_practice_14_revised_img_0021](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/020.png)

### `sersan_practice_14_revised_img_0022`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/021.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/021.png`
- note: `image_evidence_notes/sersan_practice_14_revised_img_0022.md`

![sersan_practice_14_revised_img_0022](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/021.png)

### `sersan_practice_14_revised_img_0023`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/022.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/022.png`
- note: `image_evidence_notes/sersan_practice_14_revised_img_0023.md`

![sersan_practice_14_revised_img_0023](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/022.png)

### `sersan_practice_14_revised_img_0024`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/023.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/023.png`
- note: `image_evidence_notes/sersan_practice_14_revised_img_0024.md`

![sersan_practice_14_revised_img_0024](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/023.png)

### `sersan_practice_14_revised_img_0025`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/024.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/024.png`
- note: `image_evidence_notes/sersan_practice_14_revised_img_0025.md`

![sersan_practice_14_revised_img_0025](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/024.png)

### `sersan_practice_14_revised_img_0026`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/026.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/026.png`
- note: `image_evidence_notes/sersan_practice_14_revised_img_0026.md`

![sersan_practice_14_revised_img_0026](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/026.png)

### `sersan_practice_14_revised_img_0027`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/027.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/027.png`
- note: `image_evidence_notes/sersan_practice_14_revised_img_0027.md`

![sersan_practice_14_revised_img_0027](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/027.png)

### `sersan_practice_14_revised_img_0028`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../img/028.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/028.png`
- note: `image_evidence_notes/sersan_practice_14_revised_img_0028.md`

![sersan_practice_14_revised_img_0028](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/24-practice-14/img/028.png)

## Warnings

- This is automated corpus distillation, not final doctrine review.
- Image files were opened, hashed and classified through local metadata plus nearby MD context; OCR/value extraction is not yet implemented.
- Code/XLSX artifacts are inventoried through the corpus manifest but not semantically parsed in this run.
