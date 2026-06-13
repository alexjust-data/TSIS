# Lesson Distillation: sersan_practice_11_bollinger_aberration

Title: `Practice 11`
Source MD: `03_only_md_revised/practica_11_bollinger_Aberration.md`
Promotion state: `mechanical_rule_candidate` only; no TSIS doctrine promoted.

## What The Lesson Covers

- `sersan_practice_11_bollinger_aberration_sec_0001` Practice 11. Section classified as qa. # Practice 11 - [Consultas Previas](#consultas-previas) - [Sistema Mean Reversion](#sistema-mean-reversion) - [Revisión - Sistema Bollinger Bands Mean Reversion](#revisión---sis...
- `sersan_practice_11_bollinger_aberration_sec_0002` Consultas Previas. Section classified as qa. ## Consultas Previas **Pregunta sobre cuándo un filtro se puede considerar bueno** > *Una pequeña duda con respecto a cuándo un filtro se puede considerar bueno. En la última se...
- `sersan_practice_11_bollinger_aberration_sec_0003` Sistema Mean Reversion. Section classified as procedure. ## Sistema Mean Reversion **Material subido: PDFs del sistema Mean Reversion** Vamos, vamos con donde nos quedamos. Bueno, a mí me he subido ahí en material, habéis visto en mat...
- `sersan_practice_11_bollinger_aberration_sec_0004` Revisión - Sistema Bollinger Bands Mean Reversion. Section classified as optimization. ## Revisión - Sistema Bollinger Bands Mean `Reversion` <figure> <img src="../02_workshops/21-practice-11/img/000.png" width="800"> <figcaption>Figura 000. Problemas técnicos con...
- `sersan_practice_11_bollinger_aberration_sec_0005` Salidas por tiempo. Section classified as optimization. ### Salidas por tiempo Una solución —ya la semana que viene lo probamos pero ya os adelanto alguna— una solución que viene bien cuando no encontramos solución vía pérdida, típic...
- `sersan_practice_11_bollinger_aberration_sec_0006` Selectores de Filtros. Section classified as code_explanation. ## Selectores de Filtros ***Code***: [FiltrosParaClase_MR.ELD](../code/FILTROSPARACLASEMR.ELD) **Estructura del selector con Switch** Lo que os decía, tenemos unos filtros para...
- `sersan_practice_11_bollinger_aberration_sec_0007` La Pauta del Overnight. Section classified as qa. ### La Pauta del Overnight Que, por cierto, lleva tiempo funcionando mal. Pero hay mucha gente que opera sistemas de *overnight* porque, durante muchos años, tanto la subida del...
- `sersan_practice_11_bollinger_aberration_sec_0008` Sistema - Strategy *ABERRATION. Section classified as code_explanation. ## Sistema - Strategy *ABERRATION* wsp : [Curso BB-TENDENCIAL(daily)](../code/CURSO-BB-TENDENCIAL(daily).wsp) **Introducción al sistema de ruptura por volatilidad** Hablamos tam...
- `sersan_practice_11_bollinger_aberration_sec_0009` Entradas. Section classified as optimization. ## Entradas **Retrasar señales** Hay vueltas para la entrada, para retrasar la entrada. Por ejemplo: pedirle dos cierres en vez de un cierre; pedirle que sí, pues lo que os digo...
- `sersan_practice_11_bollinger_aberration_sec_0010` Salidas. Section classified as optimization. ## Salidas **La media central** La salida más convencional y más conservadora es en el mínimo. Aquí nuevamente tenemos implementada una versión que es un poco extraña, porque re...
- `sersan_practice_11_bollinger_aberration_sec_0011` Problema de los laterales en tendenciales. Section classified as portfolio. ## Problema de los laterales en tendenciales ¿Qué problema tienen estos sistemas? Que este mismo tipo de salida le va a hacer sufrir mucho cuando no hay una tendencia, y ahí est...
- `sersan_practice_11_bollinger_aberration_sec_0012` Versión intradía del sistema tendencial. Section classified as code_explanation. ## Versión intradía del sistema tendencial Y también hay versiones intradiarias como puede ser esta que vais a ver ahora: **Código:** [ABERRATION_INTRADIA_STRATEGY](../code/CURS...

## Mechanical Rule Candidates

- `sersan_practice_11_bollinger_aberration_rule_0001` [setup_logic, entry_logic, exit_logic, filters, portfolio] Portfolio claims from this section must be evaluated as marginal contribution under correlation, drawdown and allocation constraints.
- `sersan_practice_11_bollinger_aberration_rule_0002` [bar_construction, price_view, exit_logic, stop_loss, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_11_bollinger_aberration_rule_0003` [setup_logic, entry_logic, exit_logic, filters] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_11_bollinger_aberration_rule_0004` [setup_logic, entry_logic, exit_logic, filters, optimization, robustness] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_11_bollinger_aberration_rule_0005` [setup_logic, entry_logic, exit_logic, stop_loss, take_profit, filters] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_11_bollinger_aberration_rule_0006` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, take_profit] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_11_bollinger_aberration_rule_0007` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, filters] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_11_bollinger_aberration_rule_0008` [bar_construction, price_view, setup_logic, entry_logic, filters] Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.
- `sersan_practice_11_bollinger_aberration_rule_0009` [setup_logic, entry_logic, exit_logic, stop_loss, filters, optimization] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_11_bollinger_aberration_rule_0010` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.
- `sersan_practice_11_bollinger_aberration_rule_0011` [setup_logic, entry_logic, exit_logic, filters, robustness, portfolio] Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.
- `sersan_practice_11_bollinger_aberration_rule_0012` [bar_construction, price_view, setup_logic, entry_logic, exit_logic, stop_loss] Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.

## TSIS Translation Candidates

- `sersan_practice_11_bollinger_aberration_tr_0001` -> `portfolio_evaluator` / `TSIS_PORTFOLIO_EVALUATOR_CANDIDATE`
- `sersan_practice_11_bollinger_aberration_tr_0002` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_11_bollinger_aberration_tr_0003` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_11_bollinger_aberration_tr_0004` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_11_bollinger_aberration_tr_0005` -> `backtest_checklist` / `TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE`
- `sersan_practice_11_bollinger_aberration_tr_0006` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_11_bollinger_aberration_tr_0007` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_11_bollinger_aberration_tr_0008` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_11_bollinger_aberration_tr_0009` -> `strategy_evaluator` / `TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE`
- `sersan_practice_11_bollinger_aberration_tr_0010` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`
- `sersan_practice_11_bollinger_aberration_tr_0011` -> `portfolio_evaluator` / `TSIS_PORTFOLIO_EVALUATOR_CANDIDATE`
- `sersan_practice_11_bollinger_aberration_tr_0012` -> `data_quality_gate` / `TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE`

## Key Visual Evidence

### `sersan_practice_11_bollinger_aberration_img_0019`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/21-practice-11/img/016.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/016.png`
- note: `image_evidence_notes/sersan_practice_11_bollinger_aberration_img_0019.md`

![sersan_practice_11_bollinger_aberration_img_0019](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/016.png)

### `sersan_practice_11_bollinger_aberration_img_0020`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/21-practice-11/img/018.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/018.png`
- note: `image_evidence_notes/sersan_practice_11_bollinger_aberration_img_0020.md`

![sersan_practice_11_bollinger_aberration_img_0020](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/018.png)

### `sersan_practice_11_bollinger_aberration_img_0021`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/21-practice-11/img/019.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/019.png`
- note: `image_evidence_notes/sersan_practice_11_bollinger_aberration_img_0021.md`

![sersan_practice_11_bollinger_aberration_img_0021](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/019.png)

### `sersan_practice_11_bollinger_aberration_img_0022`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/21-practice-11/img/020.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/020.png`
- note: `image_evidence_notes/sersan_practice_11_bollinger_aberration_img_0022.md`

![sersan_practice_11_bollinger_aberration_img_0022](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/020.png)

### `sersan_practice_11_bollinger_aberration_img_0023`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/21-practice-11/img/021.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/021.png`
- note: `image_evidence_notes/sersan_practice_11_bollinger_aberration_img_0023.md`

![sersan_practice_11_bollinger_aberration_img_0023](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/021.png)

### `sersan_practice_11_bollinger_aberration_img_0024`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/21-practice-11/img/022.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/022.png`
- note: `image_evidence_notes/sersan_practice_11_bollinger_aberration_img_0024.md`

![sersan_practice_11_bollinger_aberration_img_0024](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/022.png)

### `sersan_practice_11_bollinger_aberration_img_0025`

- relevance: `critical`
- visual_type: `drawdown_curve`
- source_ref: `../02_workshops/21-practice-11/img/024.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/024.png`
- note: `image_evidence_notes/sersan_practice_11_bollinger_aberration_img_0025.md`

![sersan_practice_11_bollinger_aberration_img_0025](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/024.png)

### `sersan_practice_11_bollinger_aberration_img_0026`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/21-practice-11/img/025.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/025.png`
- note: `image_evidence_notes/sersan_practice_11_bollinger_aberration_img_0026.md`

![sersan_practice_11_bollinger_aberration_img_0026](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/025.png)

### `sersan_practice_11_bollinger_aberration_img_0027`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/21-practice-11/img/027.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/027.png`
- note: `image_evidence_notes/sersan_practice_11_bollinger_aberration_img_0027.md`

![sersan_practice_11_bollinger_aberration_img_0027](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/027.png)

### `sersan_practice_11_bollinger_aberration_img_0028`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/21-practice-11/img/028.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/028.png`
- note: `image_evidence_notes/sersan_practice_11_bollinger_aberration_img_0028.md`

![sersan_practice_11_bollinger_aberration_img_0028](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/028.png)

### `sersan_practice_11_bollinger_aberration_img_0029`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/21-practice-11/img/029.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/029.png`
- note: `image_evidence_notes/sersan_practice_11_bollinger_aberration_img_0029.md`

![sersan_practice_11_bollinger_aberration_img_0029](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/029.png)

### `sersan_practice_11_bollinger_aberration_img_0030`

- relevance: `critical`
- visual_type: `optimization_map`
- source_ref: `../02_workshops/21-practice-11/img/030.png`
- resolved_path: `00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/030.png`
- note: `image_evidence_notes/sersan_practice_11_bollinger_aberration_img_0030.md`

![sersan_practice_11_bollinger_aberration_img_0030](../../../../00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/21-practice-11/img/030.png)

## Warnings

- This is automated corpus distillation, not final doctrine review.
- Image files were opened, hashed and classified through local metadata plus nearby MD context; OCR/value extraction is not yet implemented.
- Code/XLSX artifacts are inventoried through the corpus manifest but not semantically parsed in this run.
