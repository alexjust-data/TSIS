# Daily Inspection Readout v0.1

## 1. Proposito y alcance

Este documento es el cierre institucional de inspeccion para `daily` en el modulo `01_TSIS_backtest_SmallCaps`.

Su funcion no es rehacer la auditoria historica ni repetir los dossiers caso a caso. Su funcion es:

- resumir la politica de corte ya fijada;
- distinguir con claridad entre inspeccion visual y certificacion final;
- consolidar el resultado institucional de `daily`;
- explicar el significado operativo de cada bloque;
- y dirigir al inspector al dossier correcto cuando quiera bajar a evidencia visual completa.

La unidad de decision en `daily` es el `ticker-year file`, por ejemplo:

- `D:\ohlcv_daily\ticker=HMNY\year=2025\day_aggs_HMNY_2025.parquet`

El run base utilizado para esta capa de inspeccion trabaja sobre cobertura temporal global `2005-2026`. Eso significa rango temporal global del universo analizado, no presencia completa por ticker en todos los anos.

## 2. Fuentes de autoridad

Este readout no redefine la politica. La resume y la operacionaliza para inspeccion humana. Las fuentes que mandan son:

- auditoria historica:
  - `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/daily/03_daily_root_cause_audit_notebook.ipynb`
  - `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/daily/04_daily_closeout.ipynb`
  - `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/daily/04_daily_closeout.md`
- certificacion historica:
  - `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/00_daily_current_state.md`
  - `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/01_daily_recovery_and_coverage.md`
  - `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/02_daily_quality_policy.md`
  - `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/03_daily_closeout.md`
- contrato y politica institucional:
  - [daily_dataset_contract_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/daily_dataset_contract_v0_1.md>)
  - [daily_label_taxonomy_and_cut_policy.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/daily_label_taxonomy_and_cut_policy.md>)
  - [daily_consumption_policy.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/daily_consumption_policy.md>)
  - [daily_validators.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/validators/daily/daily_validators.md>)
- protocolo de evidencia:
  - [inspection_dossier_model.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/inspection_dossier_model.md>)
  - [bad_evidence_and_rehabilitation.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/bad_evidence_and_rehabilitation.md>)

## 3. Regla central: inspeccion visual no equivale a estado final de certificacion

`daily` se lee en dos planos distintos.

### A. Particion de inspeccion visual

Para construir dossiers humanos manejables, `daily` se parte en tres bloques mutuamente excluyentes:

- `bad`
- `non_good_quality`
- `good`

Esta particion es util para:

- inspeccionar evidencia de calidad del bar;
- ordenar ejemplos;
- y explicar por que un `ticker-year file` se queda en la franja buena, intermedia o dura.

### B. Estado final de certificacion

La decision operativa real no depende solo de esa particion visual. Depende de combinar:

- `quality axis`
- `coverage axis`

Eso genera la semantica final de certificacion:

- `good`
- `recoverable_without_penalty`
- `recoverable_with_flag`
- `review_not_rehabilitated`
- `bad`

Consecuencia decisiva:

- un caso puede ser sano en calidad de barra y seguir abierto en coverage;
- un caso puede no ser `good` en calidad pero seguir siendo recuperable;
- y el inspector no debe confundir un dossier visual con la policy final de uso.

## 4. Particion exacta de inspeccion

La particion de inspeccion de `daily` queda fijada asi:

- `bad`
  - entra un `ticker-year file` si `daily_refined_bucket = hard_invalid_parse_or_price`

- `non_good_quality`
  - entra un `ticker-year file` si `quality_policy != good`
  - y `daily_refined_bucket != hard_invalid_parse_or_price`

- `good`
  - entra un `ticker-year file` si `quality_policy = good`

Importante:

- `bad` y `non_good_quality` son bloques de anomalia de calidad del bar;
- `good` es muestra representativa de justificacion positiva;
- ninguno de estos tres bloques agota por si solo la semantica de coverage.

## 5. Resultado agregado actual de inspeccion

La capa visual de inspeccion y dossier de `daily` queda resumida asi:

- `bad`: `102` casos
- `non_good_quality`: `48` casos
- `good`: `24` casos en muestra representativa

Lectura correcta:

- existe un bloque duro pequeno y trazable de invalidez real;
- existe una franja intermedia donde el dano ya cambia la decision, aunque no destruya la semantica de la barra;
- y existe una franja buena defendible para uso principal, siempre que se recuerde que `good` significa barra diaria usable y no ausencia literal de cualquier warning.

Lo que estos conteos no dicen por si solos es la situacion de coverage. Para eso manda la capa de certificacion historica.

## 6. Semantica final de certificacion

### 6.1 Eje de calidad

Estados finales de calidad:

- `good`
  - `schema_only_or_other`
  - `vw_edge_absmax_only`
- `recoverable_with_flag`
  - `vw_low_ratio_limited_days`
  - `vw_mid_ratio_illiquid_regime`
  - `vw_high_ratio_illiquid_regime`
  - `vw_warn_minor_or_material`
- `bad`
  - `hard_invalid_parse_or_price`

### 6.2 Eje de coverage

Estados finales de coverage:

- `recoverable_without_penalty`
  - `LIKELY_VALID_GAP_ONLY`
- `recoverable_with_flag`
  - `AMBIGUOUS_REVIEW`
- `review_not_rehabilitated`
  - `REALLY_PROBLEMATIC_UNEXPECTED`

### 6.3 N?meros clave de coverage

- `653` tickers sin `complete_daily`
- `374` recuperables sin penalizacion
- `222` recuperables con flag
- `57` abiertos como frontera de coverage

Conclusi?n analitica:

- el gran frente de recuperacion en `daily` no es el bar invalido sino la coverage;
- mas del `91%` del faltante de coverage no debe leerse como fallo duro;
- el inspector debe evitar el error de tratar cualquier hueco como prueba de corrupcion del proveedor.

## 7. Lectura institucional por bloque visual

### 7.1 `bad`

Este bloque concentra el tail duro real de `daily`. Los patrones dominantes son:

- `OHLC = 0`;
- campos criticos diarios en cero como `open = 0`, `low = 0` o `close = 0`;
- parse/precio no defendible;
- contradicciones internas como `vw > high` con `high = 0`;
- y casos donde la barra deja de ser interpretable como sesion diaria normal de mercado.

Veredicto:

- fuera de `backtest_core`;
- preservar en `forensic_only`;
- rehabilitacion solo si otra evidencia permite reinterpretar o reconstruir el caso sin contaminar el uso principal.

Consecuencia operativa: este bloque no es simplemente 'peor calidad'; es una frontera semantica. Si se cruza, el sistema deja de distinguir mercado de artefacto, y eso invalida retornos, labels y comparaciones externas.

Dossier completo:

- [daily_hard_invalid_cases_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/daily/bad_case_evidence_packs/daily_hard_invalid_cases_v0_1.md>)

### 7.2 `non_good_quality`

Este bloque recoge la franja contractual `recoverable_with_flag` del eje de calidad. Los patrones dominantes son:

- anomalias `vw` no triviales;
- residuo persistente de iliquidez o borde de regla;
- desalineaciones que no deben tratarse como `good`;
- pero que tampoco activan exclusion dura de parse/precio.

Veredicto:

- no tratar como `good`;
- mantener en `recoverable_with_flag`;
- apto para sensibilidad, investigacion restringida o consumo con flag explicito segun la policy aplicable.

Consecuencia operativa: esta franja obliga a distinguir parseabilidad de fiabilidad. El precio sigue existiendo y puede ser util, pero ya no debe mezclarse sin marca con la franja sana porque introduce sesgo por iliquidez, residuo `vw` o anos demasiado escasos.

Dossier completo:

- [daily_non_good_quality_cases_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/daily/flagged_case_evidence_packs/daily_non_good_quality_cases_v0_1.md>)

### 7.3 `good`

Este bloque representa la franja autorizada del eje de calidad. Los patrones dominantes son:

- `schema_only_or_other`;
- `vw_edge_absmax_only`;
- residuo puntual y acotado;
- muy pocos dias afectados;
- y ausencia de activacion de invalidez dura de parse/precio.

En los casos `vw_edge_absmax_only`, los puntos rojos del panel de inspeccion marcan dias puntuales en los que `vw` queda fuera del rango `low-high`, pero con ratio y persistencia suficientemente bajos como para no sacar el caso de la franja buena vigente.

Veredicto:

- defendible para la franja principal autorizada de `daily`;
- apto para `backtest_core` en el eje de calidad.

Consecuencia operativa: `good` no debe leerse como ausencia literal de cualquier warning, sino como evidencia suficiente de que la barra diaria sigue siendo una representacion estable del retorno economico. El error evitado aqui es reducir el universo util por purismo excesivo y perder anos validos por residuos que no alteran la decision final.

Dossier de justificacion:

- [daily_good_cases_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/daily/good_justification/daily_good_cases_v0_1.md>)

## 8. Coverage historico ya integrado

La deuda visual principal de `daily` ya no esta pendiente. Las imagenes historicas `001.png` a `007.png` se han reincorporado como evidencia institucional de coverage en:

- [daily_coverage_cases_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/daily/coverage_case_evidence_packs/daily_coverage_cases_v0_1.md>)

Ese dossier fija dos familias de lectura:

- familia A: gaps alineados entre universos, compatibles con `recoverable_without_penalty`;
- familia B: desalineacion moderada, compatible con `recoverable_with_flag` y no con exclusion dura automatica.

Consecuencia:

- `daily` ya no queda cerrado solo por semantica escrita de coverage;
- tambien queda respaldado por evidencia visual historica promovida a `01_foundations`.

## 9. Significado operacional

La traduccion operacional final de `daily` queda asi:

- `backtest_core`
  - `good`
  - y coverage `recoverable_without_penalty`

- `backtest_extended`, sensibilidad o investigacion con restriccion
  - `recoverable_with_flag`

- `research_only` o `forensic_only`
  - `review_not_rehabilitated`
  - `bad`

- `ML` de calidad, deterioro o cambio de regimen
  - ciertos tails terminales o colas anomalas pueden ser utiles como etiqueta de deterioro o ruptura de normalidad
  - eso no los convierte en barras normales de mercado aptas para `backtest_core`

Principio rector:

- la presencia de un valor en el archivo no implica autorizacion para meterlo en backtest;
- TSIS no backtestea artefactos como si fueran mercado;
- TSIS tampoco trata cualquier hueco como prueba automatica de corrupcion cuando la capa de coverage dice otra cosa.

## 10. Evidencia visual y navegacion

La evidencia visual completa ya no vive solo en notebook. Vive en los dossiers y assets regenerables de `daily`.

Los tres documentos de trabajo ya existentes para inspeccion humana de calidad del bar son:

- [daily_hard_invalid_cases_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/daily/bad_case_evidence_packs/daily_hard_invalid_cases_v0_1.md>)
- [daily_non_good_quality_cases_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/daily/flagged_case_evidence_packs/daily_non_good_quality_cases_v0_1.md>)
- [daily_good_cases_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/daily/good_justification/daily_good_cases_v0_1.md>)

El bloque de coverage ya existe y completa la lectura institucional de recovery historico: [daily_coverage_cases_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/daily/coverage_case_evidence_packs/daily_coverage_cases_v0_1.md>).

## 11. Veredicto institucional final de `daily`

`daily` queda institucionalizado como dataset operativo con dos verdades simultaneas:

- calidad de barra ampliamente utilizable, con tail duro pequeno;
- y coverage alta pero no trivial, con una franja grande recuperable y un nucleo abierto mucho mas pequeno.

La existencia del bloque `bad` no desacredita automaticamente al proveedor completo ni invalida el dataset entero. Lo que hace es fijar, de forma trazable, donde termina la autorizacion de consumo principal y donde empieza la cuarentena forense.

Con este cierre, `daily` ya dispone de:

- contrato institucional;
- taxonomia exacta y politica de corte;
- policy de consumo;
- validadores;
- evidencia visual regenerable de calidad del bar;
- una semantica final de recovery alineada con `certification/daily`;
- y evidencia visual de coverage ya integrada dentro de `coverage_case_evidence_packs`.
