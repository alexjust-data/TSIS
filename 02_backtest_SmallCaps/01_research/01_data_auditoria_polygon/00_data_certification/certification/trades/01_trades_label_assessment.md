# Trades | Lectura de labels

Esta nota no rediseña `trades`. Solo fija la lectura útil de los labels actuales apoyándose en la auditoría ya hecha y en casos visuales concretos.

Importante:

- la lectura de labels de esta nota está apoyada en el estado materializado final de `57f/full_clean_fast_same_schema`
- ese run final ya quedo cerrado en disco
- por tanto estas conclusiones valen como lectura técnica del residuo ya calculado, no todavía como cierre global final de `trades`

## `reference_scale_mismatch`

Este bucket sí está bien orientado conceptualmente: el conflicto dominante no parece tape roto, sino desalineación fuerte entre `trades` raw y referencias `daily/1m`.

![SGA](img/01_reference_scale_mismatch_sga_2009_01_05.png)
![LPCN](img/02_reference_scale_mismatch_lpcn_2014_07_07.png)

Decisión:

- mantenerlo como bucket propio
- no tratarlo como `bad_data`
- usarlo como explicación primaria del residuo estructural de escala

## `review_microstructure`

Este bucket sigue siendo `review`, no `bad`. La señal dominante es comparabilidad difícil, muy cargada en odd-lots o en mezcla microestructural que no invalida por sí sola el tape completo.

![QRTEB](img/03_review_microstructure_qrteb_2019_07_24.png)
![CZFS](img/04_review_microstructure_czfs_2022_08_11.png)

Decisión:

- mantener `review_microstructure` como bucket propio
- no promoverlo a `good`
- no mezclarlo con `reference_scale_mismatch`

## `review_1m_reference_alignment`

Este bucket es pequeño pero real. Aquí `daily` y `VWAP` quedan razonablemente alineados, pero el núcleo comparable rompe de forma muy amplia contra `1m`.

![RELV](img/05_review_1m_reference_alignment_relv_2018_06_07.png)
![METC](img/06_review_1m_reference_alignment_metc_2021_03_22.png)

Decisión:

- mantenerlo separado de `review` simple
- no absorberlo todavía en `bad_data`
- tratarlo como conflicto abierto de comparabilidad `1m`

## `bad_data`

Aquí hay que ser más fino. El bucket existe y es pequeño. La mayoría de `bad_data` actual cae cerca de `~1x`, así que no debe reinterpretarse entero como `scale mismatch`. Pero sí hay fuga real de algunos casos extremos de escala que la regla actual no drena bien.

![BWL.A](img/07_bad_data_bwl_a_2009_03_26.png)
![ANDA](img/08_bad_data_anda_2012_05_10.png)

Decisión:

- `bad_data` debe mantenerse como bucket real
- pero no debe darse por cerrado sin revisar la fuga residual de `scale mismatch`
- hace falta separar:
  - `bad_data` genuino
  - `scale mismatch` extremo no capturado por la regla actual

## `review_no_1m_reference`

Bucket residual y pequeño. Aquí no falta explicación de tape; falta confirmación `1m`.

![GLBL](img/09_review_no_1m_reference_glbl_2024_09_19.png)

Decisión:

- mantener `review`
- no promover
- no usar como evidencia de mala calidad intrínseca

## `review`

El bucket genérico `review` sigue siendo demasiado ancho y probablemente contiene mezcla de casos leves con casos de escala mal drenados.

![TOF](img/10_review_tof_2010_06_21.png)

Decisión:

- no usar `review` actual como estado final de certificación
- cerrar primero:
  - run full completo
  - refinado de `reference_scale_mismatch`
  - frontera `good / review`
