# Lesson Distillation: sersan_practice_06_orb

Title: `Consultas`
Source MD: `03_only_md_revised/practica_06_ORB.md`
Promotion state: `mechanical_rule_candidate` only; no TSIS doctrine promoted.

## What The Lesson Covers

- `sersan_practice_06_orb_sec_0001` Consultas. Section classified as qa. # Consultas
- `sersan_practice_06_orb_sec_0002` Menú de navegación. Section classified as qa. ## Menú de navegación - [Consultas](#consultas) - [Estrategias ORB (Opening Range Breakout)](#estrategias-orb-opening-range-breakout) - [Definición de estrategia ORB clásica](#d...
- `sersan_practice_06_orb_sec_0003` Estrategias ORB (Opening Range Breakout). Section classified as code_explanation. # Estrategias ORB (Opening Range Breakout) - [Un alumno aporta este Paper ORB (Opening Range Breakout)](../Opening_Range_Breakout_ORB_A_Profitable_Day_Trading_Strategy_5_Minutes...
- `sersan_practice_06_orb_sec_0004` Definición de estrategia ORB clásica. Section classified as code_explanation. ## Definición de estrategia ORB clásica Cargo en TradeStation: [PRACTICA_06.ELD](../PRACTICA%2006.ELD) - code *Strategy* : [ORB clásica](../Estrategia%20ORB%20básica.pdf) - code...
- `sersan_practice_06_orb_sec_0005` Características principales. Section classified as qa. ## Características principales **En qué time frame se va a operar** La primera decisión esencial en un sistema intradía es definir en qué *time frame* se va a operar. Esa es sie...
- `sersan_practice_06_orb_sec_0006` Análisis del sistema ORB en el DAX. Section classified as optimization. ## Análisis del sistema ORB en el DAX **Pautas previas de congestión** También en el *doc* habla de las *pautas horarias* y de cómo ciertos filtros mejoran los resultados cuando...
- `sersan_practice_06_orb_sec_0007` Cambios y configuraciones, refactorizando nuestro código. Section classified as qa. ## Cambios y configuraciones, refactorizando nuestro código - code `PRACTICA_06.EDL`: [TSM 1stHour Breakout : Straegy](../PRACTICA%2006.ELD) - code refactorizado [CURSO-ORB-STRA...

## Mechanical Rule Candidates

- `sersan_practice_06_orb_rule_0001` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_06_orb_rule_0002` [setup_logic, entry_logic, exit_logic, take_profit] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_06_orb_rule_0003` [setup_logic, entry_logic, filters, sample_size, trade_distribution] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_06_orb_rule_0004` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_06_orb_rule_0005` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_06_orb_rule_0006` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.

## TSIS Translation Candidates

- `sersan_practice_06_orb_tr_0001` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_06_orb_tr_0002` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_06_orb_tr_0003` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_06_orb_tr_0004` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_06_orb_tr_0005` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_06_orb_tr_0006` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`

## Key Visual Evidence

### `sersan_practice_06_orb_img_0001`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/16-practice-06/img/001.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/001.png`
- note: `image_evidence_notes/sersan_practice_06_orb_img_0001.md`

![sersan_practice_06_orb_img_0001](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/001.png)

### `sersan_practice_06_orb_img_0002`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/16-practice-06/img/002.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/002.png`
- note: `image_evidence_notes/sersan_practice_06_orb_img_0002.md`

![sersan_practice_06_orb_img_0002](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/002.png)

### `sersan_practice_06_orb_img_0003`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/16-practice-06/img/003.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/003.png`
- note: `image_evidence_notes/sersan_practice_06_orb_img_0003.md`

![sersan_practice_06_orb_img_0003](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/003.png)

### `sersan_practice_06_orb_img_0004`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/16-practice-06/img/004.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/004.png`
- note: `image_evidence_notes/sersan_practice_06_orb_img_0004.md`

![sersan_practice_06_orb_img_0004](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/004.png)

### `sersan_practice_06_orb_img_0005`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/16-practice-06/img/005.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/005.png`
- note: `image_evidence_notes/sersan_practice_06_orb_img_0005.md`

![sersan_practice_06_orb_img_0005](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/005.png)

### `sersan_practice_06_orb_img_0006`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/16-practice-06/img/006.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/006.png`
- note: `image_evidence_notes/sersan_practice_06_orb_img_0006.md`

![sersan_practice_06_orb_img_0006](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/006.png)

### `sersan_practice_06_orb_img_0007`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/16-practice-06/img/080.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/080.png`
- note: `image_evidence_notes/sersan_practice_06_orb_img_0007.md`

![sersan_practice_06_orb_img_0007](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/080.png)

### `sersan_practice_06_orb_img_0008`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/16-practice-06/img/008.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/008.png`
- note: `image_evidence_notes/sersan_practice_06_orb_img_0008.md`

![sersan_practice_06_orb_img_0008](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/008.png)

### `sersan_practice_06_orb_img_0012`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/16-practice-06/img/012.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/012.png`
- note: `image_evidence_notes/sersan_practice_06_orb_img_0012.md`

![sersan_practice_06_orb_img_0012](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/012.png)

### `sersan_practice_06_orb_img_0013`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/16-practice-06/img/013.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/013.png`
- note: `image_evidence_notes/sersan_practice_06_orb_img_0013.md`

![sersan_practice_06_orb_img_0013](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/013.png)

### `sersan_practice_06_orb_img_0014`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/16-practice-06/img/014.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/014.png`
- note: `image_evidence_notes/sersan_practice_06_orb_img_0014.md`

![sersan_practice_06_orb_img_0014](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/014.png)

### `sersan_practice_06_orb_img_0015`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/16-practice-06/img/015.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/015.png`
- note: `image_evidence_notes/sersan_practice_06_orb_img_0015.md`

![sersan_practice_06_orb_img_0015](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/16-practice-06/img/015.png)

## Warnings

- This is automated corpus distillation, not final doctrine review.
- Image files were opened, hashed and classified through local metadata plus nearby MD context; OCR/value extraction is not yet implemented.
- Code/XLSX artifacts are inventoried through the corpus manifest but not semantically parsed in this run.
