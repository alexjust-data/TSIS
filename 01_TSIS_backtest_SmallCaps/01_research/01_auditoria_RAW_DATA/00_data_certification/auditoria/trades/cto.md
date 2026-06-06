**Guía técnica para continuar la auditoría de trades**

El criterio correcto para validar un file de trades no es comprobar únicamente si existe algún print fuera del rango daily o 1m, sino determinar si el contenido negociado elegible del fichero es consistente con las referencias y si cualquier desviación observada es marginal, explicable o estructural. En un entorno profesional, la validación debe combinar integridad del file, elegibilidad microestructural, consistencia contra referencias y una regla explícita de aceptación.

## Primera capa: integridad del file. 

Cada fichero debe pasar controles básicos de schema, tipos, timestamps, precios, tamaños y coherencia
con la partición de fecha y ticker. Si falla aquí, el file no puede considerarse válido y no merece análisis posterior. Esta capa
detecta corrupción, parseos defectuosos, columnas inválidas o registros físicamente imposibles.

## Segunda capa:  elegibilidad del trade.   

No todos los prints observados en el tape deben compararse del mismo modo contra daily high/low/last o contra agregaciones 1m. Antes de usar un trade como evidencia económica hay que clasificarlo por condiciones de mercado: sesión regular frente a pre/post, trades corregidos o cancelados, prints especiales, odd-lots, transacciones no aptas para formar high/low, etc. Este punto es crítico porque una gran parte de los aparentes breaks puede venir de comparar referencias agregadas con prints que no deberían participar en esas referencias.

**Estamos acotando en varias dimensiones. Hist?ricamente se prototip? con `57e`, pero el estado final full `<1B>` ya debe leerse sobre `57f/full_clean_fast_same_schema`:**

```
python "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\trades\cell_code\57f_build_trades_file_acceptance_artifacts_lt1b_full_clean_fast_same_schema.py" --workers 4

- temporal:
    - regular vs pre/post
- microestructural:
    - conditions
    - cancel/correction
    - tipos especiales
- tamaño:
    - size < 100 vs size >= 100
- elegibilidad económica:
    - si ese trade debería o no compararse con daily/1m
```

**Qué problema evita**

```
- tomar un print raro
- que quizá es premarket, especial, corregido o marginal
- compararlo como si fuera equivalente al flujo normal del mercado
- y concluir que el file está roto
```

**La secuencia conceptual correcta**

La capa 2 debería responder:

- “de todo lo que hay en el tape, ¿qué parte es realmente comparable con las referencias?”

La capa 4 debería responder:

- “de esa parte comparable, ¿cuánto está fuera?”

La capa 5 debería responder:

- “ese outside comparable, ¿es marginal o estructural?”

Y la capa 6:

- “con eso, ¿es good, review o bad?”

## Tercera capa: calidad interna del tape.  

Incluso si el file es íntegro y los trades son elegibles, hay que medir contaminación
microestructural. Aquí entran duplicados exactos, bursts artificiales, repetición anómala por timestamp, secuencias sospechosas y
patrones de volumen no plausibles. Esta capa no decide por sí sola si el file es bueno o malo, pero sí si el diagnóstico posterior está contaminado por ruido mecánico.

## Cuarta capa: consistencia contra referencias.   

Una vez filtrado lo anterior, el file debe contrastarse contra daily y 1m. Aquí no basta con saber si existe un price_min por debajo de daily_low o un price_max por encima de daily_high; eso solo demuestra que hubo al menos un extremo fuera. La auditoría correcta debe medir la masa real del outside: cuántos trades quedan fuera, cuánto volumen representan, si el desvío está concentrado en un instante o se reparte a lo largo del día, y si ocurre solo en pre/post o también en regular market.

## Quinta capa: métricas de severidad real.   

Las métricas clave que faltan por institucionalizar en la auditoría son outside_trade_pct, outside_volume_pct, persistencia temporal del outside, concentración temporal del outside y descomposición por sesión. Estas variables son las que permiten separar un file con uno o dos prints marginales de un file cuyo contenido negociado está estructuralmente fuera de referencia. En términos operativos, un min/max roto no invalida necesariamente un file; una fracción amplia y persistente del flujo fuera de rango sí lo invalida.

## Sexta capa: criterio explícito de aceptación.  
 
Toda auditoría seria debe terminar en una política reproducible good / review / bad. Un file solo puede darse por bueno si el outside elegible es marginal, de bajo peso en volumen, concentrado, preferentemente fuera de sesión regular y coherente con una microestructura sana. Un file debe marcarse como malo si el outside elegible es amplio, con volumen relevante, persistente y presente en regular market, o si además está confirmado por referencias 1m. Entre ambos extremos debe existir una zona de revisión manual.

## Implicación para los siguientes agentes.    
El trabajo ya hecho en D y C+D ha servido para caracterizar el problema dominante y demostrar que no estamos ante ruido trivial. Sin embargo, el siguiente salto metodológico ya no consiste en refinar taxonomías globales, sino en cerrar la auditoría file-level con lógica de validación profesional. La prioridad ya no es “qué issue domina”, sino “bajo qué condiciones un file puede aceptarse como económicamente sano aunque exista un break contra daily”.

## Líneas de trabajo recomendadas para los próximos agentes.   
Un agente debe centrarse en definir la elegibilidad exacta de trades frente a daily y 1m según sale conditions y sesión. Otro agente debe construir las métricas file-level de masa real del outside: porcentaje de trades fuera, porcentaje de volumen fuera, persistencia y concentración temporal. Un tercer agente debe proponer y calibrar la regla final de aceptación good / review / bad sobre muestras auditadas manualmente. Solo después de eso tendrá sentido reescribir la taxonomía final del notebook y defender frente a terceros qué parte del universo puede considerarse válida y qué parte debe mantenerse como residuo estructural.



## ejecutamos para fase2/05_trades_file_acceptance_audit.ipynb

Los scripts que he dejado para esta auditoría nueva están en:

```
C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\trades\cell_code
```

Builder principal <1B>. 

Recorre el materializado C + D, filtra por el universo objetivo <1B>, crea la muestra estratificada, baja a raw en esa muestra y guarda los artefactos cacheados.

Usa estas dos bases:

```
C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/trades_v2_materialized/trades_current_cd_merged/trades_current.parquet

C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/market_cap_last_observed_cutoff/20260320_market_cap_last_observed_cutoff/market_cap_cutoff_lt_1b_active_inactive.parquet
```

Comando:

```sh
python "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\trades\cell_code\57b_build_trades_file_acceptance_artifacts_lt1b.py" --batch-size 50000 --sample-per-stratum 20

{
  "built_at_utc": "2026-04-17T22:00:11.325245+00:00",
  "current_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_materialized\\trades_current_cd_merged\\trades_current.parquet",
  "target_lt1b_path": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\market_cap_last_observed_cutoff\\20260320_market_cap_last_observed_cutoff\\market_cap_cutoff_lt_1b_active_inactive.parquet",
  "target_tickers": 4824,
  "cache_dir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_materialized\\trades_current_cd_merged\\root_cause_exports\\file_acceptance_cache_lt1b",
  "batch_size": 50000,
  "sample_per_stratum": 20,
  "max_batches": null,
  "files_total": 9429112,
  "sample_files": 380,
  "artifacts": [
    "condition_combo_summary.parquet",
    "layer1_integrity_examples.parquet",
    "layer1_integrity_summary.parquet",
    "layer2_eligibility_summary.parquet",
    "layer3_tape_quality_summary.parquet",
    "layer4_reference_consistency_summary.parquet",
    "layer5_severity_real_summary.parquet",
    "layer6_policy_examples.parquet",
    "layer6_policy_summary.parquet",
    "raw_file_metrics.parquet",
    "sample_index.parquet"
  ]
}
```
Ahora el builder:

- trata como inválidos solo price < 0 y size < 0
- imprime progreso en terminal durante el barrido y durante el recálculo de muestra
- deja los artefactos en:

```sh
C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b
```

Ejecutamos notebook

- la integridad dura mejora mucho si solo invalidas negativos reales
- el problema serio restante está en consistencia contra referencias
- ese conflicto suele estar concentrado, no siempre persistente
- la política actual todavía deja demasiados review y muy pocos good
- por tanto, el siguiente cuello de botella real es la capa 2: elegibilidad de trades frente a daily y 1m

-----


Propongo rehacer la capa 2 así:

  Objetivo
  Que daily y 1m no se comparen contra todos los prints raw, sino solo contra un subconjunto “económicamente elegible”.

  Nueva capa 2

  1. integrity_filter

  - excluir solo:
      - timestamp nulo
      - price < 0
      - size < 0
      - filas corruptas o fuera de partición
  - price = 0 y size = 0 no invalidan por sí mismos

  2. session_filter

  - clasificar:
      - premarket
      - regular
      - afterhours
  - construir métricas por sesión
  - la referencia principal para aceptación debe ser regular

  3. sale_condition_filter

  - separar al menos tres grupos:
      - eligible_core
      - reviewable_noncore
      - excluded_special
  - eligible_core:
      - prints regulares
      - sin señales de corrección/cancelación
      - sin flags especiales claramente no comparables
  - excluded_special:
      - corrections
      - cancels
      - prints administrativos
      - trades no aptos para high/low si puedes identificarlos
  - reviewable_noncore:
      - todo lo dudoso que no quieras excluir de forma dura al principio

  4. lot_filter

  - marcar:
      - odd-lot
      - round-lot
  - no excluir automáticamente odd-lots al principio
  - pero sí medir outside separado:
      - outside_core_round_lot_pct
      - outside_core_odd_lot_pct

  5. reference_alignment
     Construir tres comparaciones:

  - outside_daily_all_regular
  - outside_daily_core_regular
  - outside_1m_core_regular

  La que debería gobernar la política final es:

  - outside_1m_core_regular

  Métricas nuevas mínimas

  Por file:

  - core_trade_pct
  - core_volume_pct
  - excluded_trade_pct
  - excluded_volume_pct
  - outside_daily_core_trade_pct
  - outside_daily_core_volume_pct
  - outside_1m_core_trade_pct
  - outside_1m_core_volume_pct
  - outside_core_minutes_pct_active
  - outside_core_longest_run_minutes
  - outside_core_top_minute_trade_share_pct
  - outside_core_top_minute_volume_share_pct
  - outside_core_prepost_trade_pct
  - outside_core_regular_trade_pct
  - outside_core_odd_lot_trade_pct
  - outside_core_round_lot_trade_pct

  Nueva política good / review / bad

  good

  - outside_1m_core_regular_trade_pct <= 1
  - outside_1m_core_regular_volume_pct <= 1
  - outside_core_minutes_pct_active <= 5
  - duplicados bajos
  - core_trade_pct suficientemente alto
  - sin fallos de integridad

  review

  - outside pequeño o moderado
  - persistencia baja o media
  - conflicto ambiguo entre daily y 1m
  - peso elevado de prints no-core o odd-lot

  bad

  - outside core regular alto
  - volumen core regular alto
  - persistencia alta
  - confirmado contra 1m
  - o integridad realmente rota

  Qué espero que pase si haces esto

  - bajará el ruido artificial
  - muchos review deberían moverse a good
  - los bad restantes serán más defendibles frente a terceros

  Implementación práctica
  Yo haría esto en este orden:

  1. añadir columnas eligibility_class, session_class, lot_class en compute_raw_metrics_for_sample_row
  2. recalcular todas las métricas sobre eligible_core
  3. dejar coexistir métricas viejas y nuevas durante una iteración
  4. recalibrar layer6_policy_summary

  Si quieres, el siguiente paso es que te escriba el contrato técnico exacto de eligibility_class para meterlo ya en el
  builder 57b.


