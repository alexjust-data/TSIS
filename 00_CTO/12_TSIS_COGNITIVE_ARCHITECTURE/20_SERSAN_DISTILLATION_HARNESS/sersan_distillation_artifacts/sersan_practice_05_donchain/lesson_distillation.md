# Lesson Distillation: sersan_practice_05_donchain

Title: `Cuestiones`
Source MD: `03_only_md_revised/practica_05_donchain.md`
Promotion state: `mechanical_rule_candidate` only; no TSIS doctrine promoted.

## What The Lesson Covers

- `sersan_practice_05_donchain_sec_0001` Cuestiones. Section classified as qa. # Cuestiones
- `sersan_practice_05_donchain_sec_0002` Menú de navegación. Section classified as qa. ## Menú de navegación - [Cuestiones](#cuestiones) - [Continuamos desde aquí practica_04_revised.md](#continuamos-desde-aquí-practica_04_revisedmd) - [OPtimizacion 4](#optimizaci...
- `sersan_practice_05_donchain_sec_0003` Continuamos desde aquí [practica_04_revised.md](../../14-practice-04/transcripts/practica_04_revised.md). Section classified as portfolio. ## Continuamos desde aquí [practica_04_revised.md](../../14-practice-04/transcripts/practica_04_revised.md) Ya os comenté que MultiCharts tenía un bug en este punto: las fórmula...
- `sersan_practice_05_donchain_sec_0004` OPtimizacion 4. Section classified as qa. ### OPtimizacion 4 Entonces la optimización grande, aquí recordar que inicialmente hemos hecho las dos cosas otra vez para que veáis la diferencia, de acuerdo, porque quería y a...
- `sersan_practice_05_donchain_sec_0005` Optimización Sortino: filtro y trailing. Section classified as optimization. ### Optimización Sortino: filtro y trailing **Eje X: `Net_Profit`** **Eje Y: `Filtro_ATR`** **Eje Z: `Prc_Trail`** <figure> <img src="../02_workshops/15-practice-05/img/129.png"...
- `sersan_practice_05_donchain_sec_0006` Optimización 1. Section classified as qa. #### **Optimización 1** En esto, pues, al final hemos traducido en estos 4 Excels que rápidamente os voy a enseñar ahora, y luego enseñaremos, trabajaremos el que es. <figure> <...
- `sersan_practice_05_donchain_sec_0007` Optimizacion 2. Section classified as optimization. #### **Optimizacion 2** Este efecto, como has visto antes en el Per_canal… <figure> <img src="../02_workshops/15-practice-05/img/066.png" width="800"> <figcaption>Figura 066. Di...
- `sersan_practice_05_donchain_sec_0008` Maestro para tomar la ultima decisión. Section classified as optimization. ### Maestro para tomar la ultima decisión Aunque todos estos los llevaríamos, y en este caso en un sistema multi-activos, donde lo acabaríamos de afinar es el "maestro". Nosotro...
- `sersan_practice_05_donchain_sec_0009` Backtest Filtro_ATR 1 - Per_canal 6- Pcr_Trail0.24. Section classified as portfolio. #### Backtest `Filtro_ATR 1` - `Per_canal 6`- `Pcr_Trail0.24` Vamos a pasar algunos sets por maestro. He montado el visor, que estuviera por favor bien montado, y he hecho uno d...
- `sersan_practice_05_donchain_sec_0010` Backtest Filtro_ATR 1 - Per_canal 6- Pcr_Trail 0.22. Section classified as money_management. #### Backtest `Filtro_ATR 1` - `Per_canal 6`- `Pcr_Trail 0.22` <figure> <img src="../02_workshops/15-practice-05/img/084.png" width="800"> <figcaption>Figura 084. Selección de c...
- `sersan_practice_05_donchain_sec_0011` Backtest Filtro_ATR 1 - Per_canal 23- Pcr_Trail 0.24. Section classified as procedure. #### Backtest `Filtro_ATR 1` - `Per_canal 23`- `Pcr_Trail 0.24` <figure> <img src="../02_workshops/15-practice-05/img/086.png" width="800"> <figcaption>Figura 086. Carga de set...
- `sersan_practice_05_donchain_sec_0012` Backtest Filtro_ATR 1 - Per_canal 5- Pcr_Trail 0.24. Section classified as optimization. #### **Backtest `Filtro_ATR 1` - `Per_canal 5`- `Pcr_Trail 0.24`** De los sets que hemos hecho, para que veáis, en el caso que quisiéramos quedarnos con uno como ejemplo, hemos...

## Mechanical Rule Candidates

- `sersan_practice_05_donchain_rule_0001` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_05_donchain_rule_0002` [bar_construction, price_view, optimization, robustness, walk_forward, IS_OOS] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_05_donchain_rule_0003` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_05_donchain_rule_0004` [exit_logic, stop_loss, take_profit, filters, optimization, sample_size] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_05_donchain_rule_0005` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_05_donchain_rule_0006` [bar_construction, price_view, exit_logic, take_profit, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_05_donchain_rule_0007` [optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_05_donchain_rule_0008` [exit_logic, take_profit, filters, optimization, robustness, sample_size] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_05_donchain_rule_0009` [filters, optimization, robustness, money_management, position_sizing, portfolio] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_05_donchain_rule_0010` [setup_logic, entry_logic, exit_logic, stop_loss, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_05_donchain_rule_0011` [bar_construction, price_view, filters, optimization, robustness, sample_size] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_05_donchain_rule_0012` [setup_logic, entry_logic, exit_logic, take_profit, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_05_donchain_rule_0013` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.

## TSIS Translation Candidates

- `sersan_practice_05_donchain_tr_0001` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_05_donchain_tr_0002` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_05_donchain_tr_0003` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_05_donchain_tr_0004` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_05_donchain_tr_0005` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_05_donchain_tr_0006` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_05_donchain_tr_0007` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_05_donchain_tr_0008` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_05_donchain_tr_0009` -> `money_management_policy` / `TSIS_MONEY_MANAGEMENT_POLICY_CANDIDATE`
- `sersan_practice_05_donchain_tr_0010` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_05_donchain_tr_0011` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_05_donchain_tr_0012` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_05_donchain_tr_0013` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`

## Key Visual Evidence

### `sersan_practice_05_donchain_img_0001`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/15-practice-05/img/000.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/000.png`
- note: `image_evidence_notes/sersan_practice_05_donchain_img_0001.md`

![sersan_practice_05_donchain_img_0001](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/000.png)

### `sersan_practice_05_donchain_img_0002`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/15-practice-05/img/001.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/001.png`
- note: `image_evidence_notes/sersan_practice_05_donchain_img_0002.md`

![sersan_practice_05_donchain_img_0002](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/001.png)

### `sersan_practice_05_donchain_img_0003`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/15-practice-05/img/002.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/002.png`
- note: `image_evidence_notes/sersan_practice_05_donchain_img_0003.md`

![sersan_practice_05_donchain_img_0003](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/002.png)

### `sersan_practice_05_donchain_img_0004`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/15-practice-05/img/006.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/006.png`
- note: `image_evidence_notes/sersan_practice_05_donchain_img_0004.md`

![sersan_practice_05_donchain_img_0004](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/006.png)

### `sersan_practice_05_donchain_img_0005`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/15-practice-05/img/005.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/005.png`
- note: `image_evidence_notes/sersan_practice_05_donchain_img_0005.md`

![sersan_practice_05_donchain_img_0005](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/005.png)

### `sersan_practice_05_donchain_img_0006`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/15-practice-05/img/008.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/008.png`
- note: `image_evidence_notes/sersan_practice_05_donchain_img_0006.md`

![sersan_practice_05_donchain_img_0006](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/008.png)

### `sersan_practice_05_donchain_img_0007`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/15-practice-05/img/010.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/010.png`
- note: `image_evidence_notes/sersan_practice_05_donchain_img_0007.md`

![sersan_practice_05_donchain_img_0007](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/010.png)

### `sersan_practice_05_donchain_img_0008`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/15-practice-05/img/121.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/121.png`
- note: `image_evidence_notes/sersan_practice_05_donchain_img_0008.md`

![sersan_practice_05_donchain_img_0008](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/121.png)

### `sersan_practice_05_donchain_img_0009`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/15-practice-05/img/012.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/012.png`
- note: `image_evidence_notes/sersan_practice_05_donchain_img_0009.md`

![sersan_practice_05_donchain_img_0009](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/012.png)

### `sersan_practice_05_donchain_img_0010`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/15-practice-05/img/123.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/123.png`
- note: `image_evidence_notes/sersan_practice_05_donchain_img_0010.md`

![sersan_practice_05_donchain_img_0010](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/123.png)

### `sersan_practice_05_donchain_img_0011`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/15-practice-05/img/126.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/126.png`
- note: `image_evidence_notes/sersan_practice_05_donchain_img_0011.md`

![sersan_practice_05_donchain_img_0011](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/126.png)

### `sersan_practice_05_donchain_img_0012`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/15-practice-05/img/011.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/011.png`
- note: `image_evidence_notes/sersan_practice_05_donchain_img_0012.md`

![sersan_practice_05_donchain_img_0012](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/15-practice-05/img/011.png)

## Warnings

- This is automated corpus distillation, not final doctrine review.
- Image files were opened, hashed and classified through local metadata plus nearby MD context; OCR/value extraction is not yet implemented.
- Code/XLSX artifacts are inventoried through the corpus manifest but not semantically parsed in this run.
