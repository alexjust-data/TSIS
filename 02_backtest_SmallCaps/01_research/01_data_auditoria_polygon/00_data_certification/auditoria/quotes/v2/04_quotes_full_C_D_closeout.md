# 04_quotes_full_C_D_closeout

## Objetivo

Este documento acompana al notebook `04_quotes_full_C_D_closeout.ipynb`.

Aqui queda la lectura ejecutiva y defendible de la auditoria de `quotes`, apoyada en la cache `v2` y restringida al universo canonico `<1B>`.

## Base actual

- Dataset source:
  `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_materialized\quotes_current_cd_merged\quotes_current.parquet`
- Universo operativo `<1B>`:
  `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet`
- Merge verificado:
  `verification_passed = true`
- Filas merged source actuales:
  `9,930,334`

## Que debe responder este cierre

Al final este notebook debe dejar claro:

- que universo exacto se audito
- que artefactos se usaron
- cuales son los fallos duros reales
- cuales son los fallos blandos o esperables
- que parte del dataset puede considerarse operativamente sana
- que residuos quedan y como interpretarlos

## Estado actualizado

El notebook `04_quotes_full_C_D_closeout.ipynb` ya fue convertido en notebook de cierre real y no en simple scaffold.

Capas incluidas:

- alcance auditado
- resumen de severidad
- taxonomia final
- buckets bajo revision final
- casos representativos desde `case_index`
- rollover UTC separado
- conclusion operativa

## Dependencia operativa

Este cierre `v2` depende de los artefactos generados por:

```sh
python "C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\quotes\v2\cell_code\build_quotes_cd_audit_artifacts_v2.py"
```

## Narrativa de cierre fijada

Lectura ejecutiva actual:

- `quotes <1B>` no presenta senales de corrupcion masiva del dataset
- la mayor parte del universo cae en `clean_pass_or_other` o en `soft_crossed_micro_noise`
- el residuo principal se concentra en familias ya interpretables:
  - `soft crossed` persistente
  - borde de umbral `hard`
  - rollover UTC en dias grandes
- muchos `hard fails` top quedan exactamente en `5.0%`
- muchos `warns` top caen exactamente en `0.8%`
- los extremos severos existen, pero ya quedan aislados y con peso pequeno

## Buckets bajo revision puntual

El cierre deja bajo revision manual final solo estos buckets:

- `persistent_soft_crossed_mid_large_scale`
- `large_file_threshold_edge_hard_many_crosses`
- `medium_file_threshold_edge_hard_many_crosses`
- `high_hard_crossed_10_to_20`

## Decision provisional de cierre

- considerar operativamente sana la mayor parte del universo auditado
- aceptar como residuo esperable el micro-ruido soft y el rollover UTC limpio
- no seguir refinando taxonomia salvo que la revision economica de los buckets anteriores lo justifique

## Matiz economico nuevo

Se anadio una capa de severidad del crossed para no depender solo de `% crossed`.

Definiciones:

- `cross_abs = bid_price - ask_price`
- `cross_rel_bps = (bid_price - ask_price) / mid_price * 10000`

Lectura ejecutiva:

- varias familias duras no muestran un cruce pequeno alrededor del spread
- muestran un patron de `ask_price = 0` o cuasi `0`, que empuja la severidad relativa hacia `20000 bps`
- por tanto, una parte relevante del hard fail no es desorden fino del libro, sino degeneracion clara del lado ask

Lectura por buckets:

- `high_hard_crossed_10_to_20`:
  cruce economicamente extremo
- `medium_file_threshold_edge_hard_many_crosses`:
  cruce economicamente extremo
- `large_file_threshold_edge_hard_many_crosses`:
  bucket mixto; mezcla cruce pequeno con cola extrema
- `persistent_soft_crossed_mid_large_scale`:
  bucket intermedio real; aqui si aparece masa en severidad `mild/moderate`

Implicacion de cierre:

- el `% crossed` sigue siendo util para prevalencia
- pero la decision economica debe apoyarse tambien en la magnitud del crossed
- la siguiente separacion util ya no es por mas taxonomias, sino por:
  - `ask_price == 0`
  - `ask_price > 0`

## Refinamiento ya resuelto

Ese corte `ask == 0` vs `ask > 0` ya se materializo.

Lectura final de los buckets mas delicados:

- `high_hard_crossed_10_to_20`:
  dominado por `ask = 0`; el residuo con `ask > 0` sigue siendo severo
- `medium_file_threshold_edge_hard_many_crosses`:
  dominado por `ask = 0`; el residuo con `ask > 0` sigue siendo severo
- `large_file_threshold_edge_hard_many_crosses`:
  bucket mixto real; aproximadamente mitad `ask = 0`, mitad `ask > 0`
- `persistent_soft_crossed_mid_large_scale`:
  bucket de `ask > 0` casi puro; no se explica por degeneracion trivial del ask

Implicacion operativa:

- parte del hard fail puede justificarse como `ask` degenerado
- pero no todo el residuo puede cerrarse con esa explicacion
- el foco economico real ya no esta en las familias puramente `ask = 0`
- esta en entender y decidir que hacer con:
  - `large_file_threshold_edge_hard_many_crosses`
  - `persistent_soft_crossed_mid_large_scale`

## Corte final de crossed positivo

Dentro de esos buckets se anadio un corte final sobre la severidad del crossed con `ask > 0`:

- `mild`: `< 5 bps`
- `moderate`: `5-25 bps`
- `severe`: `>= 25 bps`

Lectura final:

- `large_file_threshold_edge_hard_many_crosses`:
  mezcla real de mild, moderate y severe
- `persistent_soft_crossed_mid_large_scale`:
  grueso mild/moderate con cola severe
- `medium_file_threshold_edge_hard_many_crosses`:
  bucket pequeno pero mezclado
- `high_hard_crossed_10_to_20`:
  cuando sobrevive a `ask > 0`, sobrevive como severe

Implicacion de cierre:

- el residuo ya no se interpreta como caos
- se interpreta como mezcla de tres mecanismos:
  - degeneracion `ask = 0`
  - crossed positivo leve o moderado
  - cola positiva severa concentrada

## Politica explicita good review bad

La politica de cierre para `quotes <1B>` queda asi:

- `good`
  - familias dominadas por `clean_pass_or_other`
  - `soft_crossed_micro_noise`
  - `persistent_soft_crossed_low`
  - `utc_rollover_large_day_clean`
  - lectura:
    - no hay evidencia de problema economico relevante
    - el residuo es leve, estable o puramente temporal
- `review`
  - familias mixtas donde conviven regimenes `mild` y `moderate`
  - o donde la parte `ask > 0` sigue siendo interpretable pero no trivial
  - buckets principales:
    - `large_file_threshold_edge_hard_many_crosses`
    - `persistent_soft_crossed_mid_large_scale`
- `bad`
  - familias donde el residuo con `ask > 0` es claramente severo
  - o donde la estructura residual no puede defenderse como ruido leve
  - buckets principales:
    - `high_hard_crossed_10_to_20`
    - `medium_file_threshold_edge_hard_many_crosses`

Regla verbal reproducible:

- si el bucket esta dominado por `ask = 0` o por crossed positivo `mild`, tiende a `good`
- si mezcla `mild` y `moderate`, o si la cola severa existe pero no domina, queda en `review`
- si cuando sobrevive `ask > 0` lo hace como `severe`, queda en `bad`

Lectura final por los cuatro buckets abiertos:

- `high_hard_crossed_10_to_20`:
  `bad`
- `medium_file_threshold_edge_hard_many_crosses`:
  `bad`
- `large_file_threshold_edge_hard_many_crosses`:
  `review`
- `persistent_soft_crossed_mid_large_scale`:
  `review`

Implicacion operativa:

- la mayor parte del universo puede cerrarse como `good`
- el residuo importante ya queda concentrado en muy pocas familias `review/bad`
- el inspector final del notebook sirve para enseñar exactamente que files componen cada una

## Estado de cierre

`quotes <1B>` puede darse por cerrado a nivel de auditoria, con una salvedad explicita.

Que significa "cerrado":

- el universo auditado ya esta bien acotado a `<1B>`
- el flujo `v2` ya tiene artefactos reproducibles
- el notebook de cierre ya incorpora:
  - `preflight`
  - lectura ejecutiva
  - severidad economica del crossed
  - corte `ask = 0` vs `ask > 0`
  - corte `mild / moderate / severe`
  - politica `good / review / bad`
  - inspector final por `file`
- la conclusion ya es defendible frente a terceros

La salvedad:

- "cerrado" no significa que no existan casos malos
- significa que esos casos ya estan:
  - localizados
  - tipificados
  - medidos
  - y acotados dentro del universo total

Lectura final de cierre:

- no hay senal de corrupcion masiva del dataset
- la mayor parte del universo es operativamente sana
- el residuo ya no es una bolsa caotica
- queda concentrado en pocas familias bien caracterizadas

Decision operativa final:

- `good`: aceptable para cierre
- `review`: aceptable con monitorizacion o filtro segun el uso
- `bad`: residual localizado que no bloquea el cierre del universo

## Implicacion para backtesting y ML IA

La politica `good / review / bad` no debe aplicarse igual en todos los usos.

### Backtesting

En backtesting el criterio debe ser mas conservador, porque cualquier contaminacion en `quotes` puede afectar:

- spreads
- estados del libro
- features derivadas del bid ask
- simulacion de fills o de condiciones de entrada salida

Uso recomendado:

- `good`
  - entra en el dataset principal de backtest
- `review`
  - no debe mezclarse a ciegas con `good`
  - conviene correr dos universos:
    - `core = good`
    - `extended = good + review`
  - si las metricas cambian mucho entre ambos, el edge depende de zonas fragiles del dato
- `bad`
  - fuera del universo principal
  - puede conservarse solo para stress test o robustness testing

Regla practica:

- el backtest oficial debe salir con `good`
- `review` debe usarse para sensibilidad
- `bad` no debe usarse para calibrar la estrategia principal

### ML IA

En ML IA el tratamiento puede ser menos duro, porque aqui importa no solo la limpieza del dato sino tambien no sesgar el modelo hacia un mercado artificialmente limpio.

Uso recomendado:

- `good`
  - base principal de entrenamiento
- `review`
  - puede usarse, pero con control
  - opciones razonables:
    - menor peso muestral
    - feature explicita de calidad
    - comparativa entre modelo estricto y modelo amplio
- `bad`
  - fuera del entrenamiento supervisado principal
  - si puede usarse para:
    - deteccion de anomalias
    - tests adversariales
    - clasificadores de calidad de dato

Regla practica:

- baseline ML:
  - entrenar con `good`
- comparativa:
  - entrenar tambien con `good + review`
- metadata de calidad:
  - anadir variables como:
    - `quotes_quality`
    - `taxonomy`
    - `ask_zero_share`
    - `positive_cross_bucket`

### Decision operativa resumida

- para backtesting oficial:
  - usar `good`
- para sensibilidad y research:
  - usar `good + review`
- para ML supervisado:
  - entrenar baseline con `good`
  - comparar contra `good + review`
  - incluir metadata de calidad cuando sea posible
- para anomalia y monitorizacion:
  - usar `bad` y parte de `review` como set duro

Lectura final:

- si una familia puede contaminar precios, spreads o estados del libro, no debe entrar sin control en backtesting
- en ML IA si puede entrar, pero solo si el pipeline sabe que esta viendo un regimen de menor calidad
