# Daily Label Taxonomy And Cut Policy

## 1. Rol

Este documento fija la taxonomia exacta de etiquetas y la politica de corte de `daily`.

Su funcion es dejar por escrito:

- cual es la unidad exacta de decision;
- que señales upstream se consumen;
- que buckets intermedios existen;
- que umbrales literales se aplican;
- que etiqueta final recibe cada `ticker-year file`;
- y como debe leerse separadamente la calidad del bar y la cobertura.

Este documento no sustituye:

- `daily_dataset_contract_v0_1.md`
- `daily_consumption_policy.md`
- `daily_validators.md`
- ni la evidencia historica de auditoria y certificacion

Los aterriza en una politica de corte unica y auditable.

## 2. Fuentes de autoridad

La politica aqui descrita nace de cuatro niveles de autoridad:

### A. Run de validacion upstream

El run `daily_validate_2005_2026_d_full_v030` materializa para cada file:

- `issues`
- `warns`
- `rows_after_parse`
- `vw_outside_range_rows`
- `vw_problem_days`
- `coverage_ratio_vs_business_days`
- y otras metricas auxiliares

### B. Bucketizacion operativa historica

La logica literal de bucketizacion historica queda fijada en:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/daily/04_daily_closeout.ipynb`

### C. Cierre operativo y certificacion

Referencias:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/daily/04_daily_closeout.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/01_daily_recovery_and_coverage.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/02_daily_quality_policy.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/03_daily_closeout.md`

### D. Capa contractual del modulo 01

Referencias:

- `01_foundations/contract_registry/dataset_contracts/daily_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/daily_consumption_policy.md`
- `01_foundations/validators/daily/daily_validators.md`
- `01_foundations/module_contracts/semantic_authority.md`

## 3. Unidad exacta de decision

La unidad exacta de clasificacion en `daily` es:

- `ticker-year file`

Ejemplo:

- `D:\ohlcv_daily\ticker=HMNY\year=2025\day_aggs_HMNY_2025.parquet`

La politica no clasifica primero "el ticker" de forma abstracta.

Clasifica:

- un file anual concreto;
- asociado a un ticker;
- dentro de un year;
- y con metricas propias de parse, integridad, `vw` y coverage.

## 4. Dos ejes distintos de politica

En `daily` existen dos ejes que no deben mezclarse:

### A. Calidad del bar diario

Pregunta:

- este `ticker-year file` representa barras diarias defendibles como mercado normal?

Salida:

- `daily_refined_bucket`
- `quality_policy`

### B. Cobertura del file o del ticker

Pregunta:

- la ausencia o discontinuidad observada en `daily` es compatible con gap valido, gap ambiguo o problema realmente abierto?

Salida:

- taxonomia de coverage

Un caso puede:

- ser sano en calidad del bar y seguir abierto en coverage;
- o estar mal en calidad del bar aunque la coverage no sea la cuestion principal.

## 5. Señales upstream que alimentan la decision

La bucketizacion historica consume estas señales base:

- `issues`
- `warns`
- `rows_after_parse`
- `vw_outside_range_rows`
- `vw_problem_days`
- `coverage_ratio_vs_business_days`

Y construye:

- `has_vw_issue`
- `has_vw_warn`
- `has_invalid_price_issue`
- `has_parse_issue`
- `vw_ratio_pct`

Definiciones literales:

- `has_vw_issue`
  - `issues` contiene `vw_outside_range_severe`

- `has_vw_warn`
  - `warns` contiene `vw_outside_range_`

- `has_invalid_price_issue`
  - `issues` contiene `negative_or_zero_ohlc_rows`

- `has_parse_issue`
  - `issues` contiene `all_rows_invalid_after_parse`

- `vw_ratio_pct`
  - `vw_outside_range_rows / rows_after_parse * 100`
  - solo cuando `rows_after_parse > 0`

## 6. Politica exacta de bucketizacion de calidad

La logica literal historica es esta:

```python
out['daily_refined_bucket'] = np.select([
    out['has_parse_issue'] | out['has_invalid_price_issue'],
    out['has_vw_issue'] & (out['vw_ratio_pct'] < 1.0) & (out['vw_problem_days'] < 3),
    out['has_vw_issue'] & (out['vw_ratio_pct'] < 5.0) & (out['vw_problem_days'] < 10),
    out['has_vw_issue'] & (out['vw_ratio_pct'] >= 5.0) & (out['vw_ratio_pct'] < 20.0),
    out['has_vw_issue'] & (out['vw_ratio_pct'] >= 20.0),
    out['has_vw_warn'],
], [
    'hard_invalid_parse_or_price',
    'vw_edge_absmax_only',
    'vw_low_ratio_limited_days',
    'vw_mid_ratio_illiquid_regime',
    'vw_high_ratio_illiquid_regime',
    'vw_warn_minor_or_material',
], default='schema_only_or_other')
```

Eso implica exactamente:

### `hard_invalid_parse_or_price`

Cae aqui si:

- `issues` contiene `all_rows_invalid_after_parse`
- o `issues` contiene `negative_or_zero_ohlc_rows`

Interpretacion:

- fallo duro de parse o de precio;
- no defendibilidad primaria del bar diario;
- exclusion del consumo principal.

### `vw_edge_absmax_only`

Cae aqui si:

- hay `vw_outside_range_severe`
- y `vw_ratio_pct < 1.0`
- y `vw_problem_days < 3`

Interpretacion:

- `1-2` dias afectados;
- ratio muy bajo;
- borde de regla;
- no persistencia suficiente para degradar el file como bloque no bueno.

### `vw_low_ratio_limited_days`

Cae aqui si:

- hay `vw_outside_range_severe`
- y `vw_ratio_pct < 5.0`
- y `vw_problem_days < 10`

Interpretacion:

- residuo real;
- pocos dias afectados;
- ratio todavia acotado;
- no debe tratarse como `good` sin mas.

### `vw_mid_ratio_illiquid_regime`

Cae aqui si:

- hay `vw_outside_range_severe`
- y `5.0 <= vw_ratio_pct < 20.0`

Interpretacion:

- persistencia material;
- compatible con regimen iliquido o construccion no trivial del bar;
- requiere flag o revision.

### `vw_high_ratio_illiquid_regime`

Cae aqui si:

- hay `vw_outside_range_severe`
- y `vw_ratio_pct >= 20.0`

Interpretacion:

- persistencia alta del problema `vw`;
- sigue sin equivaler automaticamente a corrupcion dura;
- no debe entrar en consumo ciego como `good`.

### `vw_warn_minor_or_material`

Cae aqui si:

- no entro en ninguno de los buckets anteriores;
- pero `warns` contiene `vw_outside_range_`

Interpretacion:

- existe señal `vw`, pero no severa a nivel `issues`;
- sigue siendo un caso no trivial;
- debe caer en capa de revision o flag.

### `schema_only_or_other`

Cae aqui por defecto si no se activa ninguna de las condiciones anteriores.

Interpretacion:

- no hay parse duro;
- no hay precio no positivo duro;
- no hay `vw_outside_range_severe`;
- no hay `vw_outside_range_` en `warns`;
- el file queda en el bucket base sano por descarte controlado.

## 7. Politica exacta de `quality_policy`

La logica historica literal es:

```python
out['quality_policy'] = np.select([
    out['daily_refined_bucket'].isin(['schema_only_or_other', 'vw_edge_absmax_only']),
    out['daily_refined_bucket'].isin(['vw_low_ratio_limited_days', 'vw_mid_ratio_illiquid_regime', 'vw_high_ratio_illiquid_regime', 'vw_warn_minor_or_material']),
    out['daily_refined_bucket'].eq('hard_invalid_parse_or_price'),
], ['good', 'review', 'bad'], default='review')
```

Eso significa:

### `good`

Incluye:

- `schema_only_or_other`
- `vw_edge_absmax_only`

La lectura correcta es:

- el file es defendible como barra diaria normal;
- el residuo observable no fuerza degradacion operativa;
- puede entrar en los consumidores principales permitidos por policy.

### `review`

Incluye:

- `vw_low_ratio_limited_days`
- `vw_mid_ratio_illiquid_regime`
- `vw_high_ratio_illiquid_regime`
- `vw_warn_minor_or_material`

La lectura correcta es:

- no es `good`;
- tampoco es exclusion dura;
- requiere cautela, flag, sensibilidad o uso restringido segun consumer.

### `bad`

Incluye:

- `hard_invalid_parse_or_price`

La lectura correcta es:

- el file no es defendible hoy como barra diaria normal apta para `backtest_core`;
- debe quedar fuera del consumo principal;
- puede preservarse para `forensic_only`;
- y solo reabrirse si otra evidencia permite rehabilitacion defendible.

## 8. Traduccion contractual actual

La capa contractual nueva del modulo 01 traduce hoy esa taxonomia historica a:

- `good`
- `recoverable_with_flag`
- `bad`

Mapeo contractual actual:

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

Regla de traduccion:

- `review` historico de `daily`
  - debe leerse contractualmente como `recoverable_with_flag`

## 9. Cierre de la desalineacion historico -> contractual

La bucketizacion historica de `daily` usa:

- `good`
- `review`
- `bad`

La capa contractual del modulo 01 usa:

- `good`
- `recoverable_with_flag`
- `bad`

El cierre institucional vigente es:

- `review` historico se traduce a `recoverable_with_flag`
- `vw_warn_minor_or_material` pertenece a esa misma franja contractual

Por tanto, en el estado actual del modulo:

- `vw_low_ratio_limited_days`
- `vw_mid_ratio_illiquid_regime`
- `vw_high_ratio_illiquid_regime`
- `vw_warn_minor_or_material`

se tratan todos como:

- `recoverable_with_flag`

## 10. Que significa exactamente "fallo duro"

En `daily`, "fallo duro" no significa intuicion subjetiva del inspector.

Significa, hoy, que el file activa una de estas señales upstream:

- `all_rows_invalid_after_parse`
- `negative_or_zero_ohlc_rows`

Eso es lo que dispara:

- `hard_invalid_parse_or_price`
- y, por tanto, `quality_policy = bad`

El closeout ademas documenta que este bloque duro real queda en:

- `19` casos `all_rows_invalid_after_parse`
- `29` casos `negative_or_zero_ohlc_rows`
- `54` casos `negative_or_zero_ohlc_rows + vw_outside_range_severe`

## 11. Que significa "la integridad primaria se sostiene"

En la implementacion historica actual, significa:

- el file NO activa `all_rows_invalid_after_parse`
- y NO activa `negative_or_zero_ohlc_rows`

Es decir:

- no se detecta parse invalido total;
- no se detectan OHLC no positivos como issue duro materializado;
- y el caso puede pasar a la segunda capa de decision dominada por `vw`.

Esto no implica perfeccion absoluta.

Implica solo que:

- no cayo en el exclusion tail duro primario.

## 12. Que decide el nivel de "limpieza" del coverage

La politica final de coverage no sale de `quality_policy`.

Sale de un cruce separado entre:

- tickers LT<1B> sin `complete_daily`
- y la auditoria de missing years contra calendario/universo

El script de autoridad es:

- `01_research/01_auditoria_RAW_DATA/cell_code/00_data_certification/058_daily_v2_cross_lt1b_missing_vs_universe_audit.py`

La regla literal es:

```python
def status(row: pd.Series) -> str:
    if int(row["unexpected_clean_rows"]) > 0:
        return "REALLY_PROBLEMATIC_UNEXPECTED"
    if int(row["unexpected_ambiguous_rows"]) > 0:
        return "AMBIGUOUS_REVIEW"
    if int(row["likely_valid_rows"]) > 0 and int(row["unexpected_rows"]) == 0:
        return "LIKELY_VALID_GAP_ONLY"
    return "UNCLASSIFIED"
```

## 13. Politica exacta de coverage

### `REALLY_PROBLEMATIC_UNEXPECTED`

Cae aqui si:

- `unexpected_clean_rows > 0`

Es decir:

- existe al menos un missing year clasificado como `unexpected_missing`

Lectura:

- coverage realmente abierta;
- no debe tratarse como gap benigno;
- pero tampoco confundirse automaticamente con corrupcion del bar diario.

### `AMBIGUOUS_REVIEW`

Cae aqui si:

- no hubo `unexpected_clean_rows`
- pero `unexpected_ambiguous_rows > 0`

Es decir:

- existe al menos un missing year clasificado como `unexpected_missing_ambiguous_ticker`

Lectura:

- no se probó como gap benigno;
- tampoco como faltante duro totalmente limpio;
- requiere flag o revision.

### `LIKELY_VALID_GAP_ONLY`

Cae aqui si:

- `likely_valid_rows > 0`
- y `unexpected_rows == 0`

Es decir:

- hay missing years clasificados como `likely_valid_gap_outside_reference_window`
- y no existe ninguna señal inesperada

Lectura:

- recuperable sin penalizacion;
- gap compatible con ventana valida o expectativa razonable del dataset.

### `UNCLASSIFIED`

Es una salida residual del script.

No debe considerarse estado final institucional deseable sin cierre adicional.

## 14. Coverage exploratorio vs coverage final

En `03_daily_root_cause_audit_notebook.ipynb` aparece un corte exploratorio por:

- `coverage_ratio_vs_business_days >= 0.8`
- `>= 0.5`
- `< 0.5`

Eso solo es:

- radiografia exploratoria de coverage

No es:

- la taxonomia final institucional de coverage

La autoridad final de coverage es:

- `LIKELY_VALID_GAP_ONLY`
- `AMBIGUOUS_REVIEW`
- `REALLY_PROBLEMATIC_UNEXPECTED`

## 15. Tabla consolidada de decision

### Calidad del bar

- si `all_rows_invalid_after_parse` o `negative_or_zero_ohlc_rows`
  - `daily_refined_bucket = hard_invalid_parse_or_price`
  - `quality_policy = bad`

- si no, y hay `vw_outside_range_severe` con `vw_ratio_pct < 1.0` y `vw_problem_days < 3`
  - `daily_refined_bucket = vw_edge_absmax_only`
  - `quality_policy = good`

- si no, y hay `vw_outside_range_severe` con `vw_ratio_pct < 5.0` y `vw_problem_days < 10`
  - `daily_refined_bucket = vw_low_ratio_limited_days`
  - `quality_policy = review` historico / `recoverable_with_flag` contractual

- si no, y hay `vw_outside_range_severe` con `5.0 <= vw_ratio_pct < 20.0`
  - `daily_refined_bucket = vw_mid_ratio_illiquid_regime`
  - `quality_policy = review` historico / `recoverable_with_flag` contractual

- si no, y hay `vw_outside_range_severe` con `vw_ratio_pct >= 20.0`
  - `daily_refined_bucket = vw_high_ratio_illiquid_regime`
  - `quality_policy = review` historico / `recoverable_with_flag` contractual

- si no, pero `warns` contiene `vw_outside_range_`
  - `daily_refined_bucket = vw_warn_minor_or_material`
  - `quality_policy = review` historico / revisar su mapeo contractual explicito

- si nada de lo anterior aplica
  - `daily_refined_bucket = schema_only_or_other`
  - `quality_policy = good`

### Coverage

- si existe algun `unexpected_missing`
  - `REALLY_PROBLEMATIC_UNEXPECTED`

- si no existe `unexpected_missing`, pero existe `unexpected_missing_ambiguous_ticker`
  - `AMBIGUOUS_REVIEW`

- si existen `likely_valid_gap_outside_reference_window` y ningun `unexpected`
  - `LIKELY_VALID_GAP_ONLY`

## 16. Regla de precedencia

La regla de precedencia correcta es:

- primero se decide la calidad primaria del bar;
- despues se decide la clasificacion de coverage;
- y ambas no deben colapsarse en una sola etiqueta binaria.

En particular:

- un `bad` de calidad no se salva por una coverage razonable;
- una coverage abierta no convierte por si sola un bar sano en `bad`;
- y un caso terminal plausible no convierte automaticamente barras invalidas en barras validas.

## 17. Regla de inspeccion

Todo dossier de inspeccion `daily` debe declarar, para cada caso:

- el `daily_refined_bucket`;
- la `quality_policy`;
- la clasificacion de coverage si aplica;
- la regla de corte que lo hizo caer ahi;
- y la evidencia visual o tabular suficiente para que un inspector pueda cotejar la decision.

## 18. Politica de cambio

Requieren actualizar este documento:

- cualquier cambio en los thresholds de `vw_ratio_pct`;
- cualquier cambio en `vw_problem_days`;
- cualquier cambio en los issues duros que disparan `hard_invalid_parse_or_price`;
- cualquier cambio en la taxonomia de coverage final;
- cualquier cambio en el mapeo de bucket a `quality_policy`.
