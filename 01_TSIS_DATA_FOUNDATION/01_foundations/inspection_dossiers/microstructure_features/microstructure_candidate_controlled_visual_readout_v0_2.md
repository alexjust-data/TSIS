# Microstructure Candidate Controlled Visual Readout v0.2

## Scope

This readout is visual/forensic evidence for `the 50-window controlled microstructure_features_table_v0_2_candidate materialization`.

It does not promote a new official dataset and it does not claim full-universe microstructure coverage.

```text
candidate_dir = E:\TSIS\data\data_foundation_outputs\microstructure_features_table\microstructure_features_table_v0_2_candidate_controlled_25_per_role
candidate_partition = E:\TSIS\data\data_foundation_outputs\microstructure_features_table\microstructure_features_table_v0_2_candidate_controlled_25_per_role\year=2025\month=12\part-0000.parquet
window_manifest = C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\runs\data_foundation\microstructure_features_table_v0_2_candidate_controlled_25_per_role\microstructure_features_table_v0_2_candidate_window_manifest_v0_1.csv
case_count = 50
cached_quote_files_read = 9
cached_trade_files_read = 5
official_dataset_created = false
full_universe_claim = false
```

## How To Read These Images

Each image has three panels: bid/ask quote path, trade prints, and spread/volume texture. The purpose is to help a human inspector decide whether the candidate windows are understandable as microstructure state components.

Important limitation: `D:/quotes` lineage is still provisional until the E-root quotes parity/authority work is complete.

## Cases

### Case 01 - `AFJK` `2025-12-31` `pre_event_30m`

![Case 01](visual_evidence_v0_2_controlled_25_per_role/images/01_afjk_2025_12_31_pre_event_30m_272bc9c8f8.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`1,002` quotes y `3,507` trades. La mediana
del spread es `403.66` bps y el p90 es
`722.03` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `96.44%`, el duplicate exact ratio es `0.74%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 02 - `AFJK` `2025-12-31` `pre_event_30m`

![Case 02](visual_evidence_v0_2_controlled_25_per_role/images/02_afjk_2025_12_31_pre_event_30m_b2862dc7d0.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`301` quotes y `473` trades. La mediana
del spread es `366.97` bps y el p90 es
`592.26` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `94.93%`, el duplicate exact ratio es `1.27%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 03 - `AFJK` `2025-12-31` `pre_event_30m`

![Case 03](visual_evidence_v0_2_controlled_25_per_role/images/03_afjk_2025_12_31_pre_event_30m_c888b1dc39.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`301` quotes y `473` trades. La mediana
del spread es `366.97` bps y el p90 es
`592.26` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `94.93%`, el duplicate exact ratio es `1.27%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 04 - `AFJK` `2025-12-31` `pre_event_30m`

![Case 04](visual_evidence_v0_2_controlled_25_per_role/images/04_afjk_2025_12_31_pre_event_30m_c9aa3abcb6.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`1,002` quotes y `3,507` trades. La mediana
del spread es `403.66` bps y el p90 es
`722.03` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `96.44%`, el duplicate exact ratio es `0.74%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 05 - `AFJK` `2025-12-31` `same_session_regular`

![Case 05](visual_evidence_v0_2_controlled_25_per_role/images/05_afjk_2025_12_31_same_session_regular_0e659e67b1.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`6,107` quotes y `21,218` trades. La mediana
del spread es `497.71` bps y el p90 es
`843.38` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `96.06%`, el duplicate exact ratio es `0.48%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 06 - `AFJK` `2025-12-31` `same_session_regular`

![Case 06](visual_evidence_v0_2_controlled_25_per_role/images/06_afjk_2025_12_31_same_session_regular_416853fae0.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`6,107` quotes y `21,218` trades. La mediana
del spread es `497.71` bps y el p90 es
`843.38` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `96.06%`, el duplicate exact ratio es `0.48%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 07 - `AFJK` `2025-12-31` `same_session_regular`

![Case 07](visual_evidence_v0_2_controlled_25_per_role/images/07_afjk_2025_12_31_same_session_regular_65fcb7445e.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`6,107` quotes y `21,218` trades. La mediana
del spread es `497.71` bps y el p90 es
`843.38` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `96.06%`, el duplicate exact ratio es `0.48%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 08 - `AFJK` `2025-12-31` `same_session_regular`

![Case 08](visual_evidence_v0_2_controlled_25_per_role/images/08_afjk_2025_12_31_same_session_regular_8dbd508a18.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`6,107` quotes y `21,218` trades. La mediana
del spread es `497.71` bps y el p90 es
`843.38` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `96.06%`, el duplicate exact ratio es `0.48%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 09 - `BFIN` `2025-12-31` `pre_event_30m`

![Case 09](visual_evidence_v0_2_controlled_25_per_role/images/09_bfin_2025_12_31_pre_event_30m_8f88fc2db3.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`3,040` quotes y `427` trades. La mediana
del spread es `NA` bps y el p90 es
`NA` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `NA%`, el duplicate exact ratio es `NA%` y el off-regular-session ratio es `NA%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 10 - `BFIN` `2025-12-31` `pre_event_30m`

![Case 10](visual_evidence_v0_2_controlled_25_per_role/images/10_bfin_2025_12_31_pre_event_30m_ee057dce3d.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`3,040` quotes y `427` trades. La mediana
del spread es `NA` bps y el p90 es
`NA` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `NA%`, el duplicate exact ratio es `NA%` y el off-regular-session ratio es `NA%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 11 - `BFIN` `2025-12-31` `same_session_regular`

![Case 11](visual_evidence_v0_2_controlled_25_per_role/images/11_bfin_2025_12_31_same_session_regular_6e0ab5aa87.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`2,527` quotes y `427` trades. La mediana
del spread es `24.97` bps y el p90 es
`49.75` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `92.51%`, el duplicate exact ratio es `0.47%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 12 - `BFIN` `2025-12-31` `same_session_regular`

![Case 12](visual_evidence_v0_2_controlled_25_per_role/images/12_bfin_2025_12_31_same_session_regular_cbdbc46814.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`2,527` quotes y `427` trades. La mediana
del spread es `24.97` bps y el p90 es
`49.75` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `92.51%`, el duplicate exact ratio es `0.47%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 13 - `BYFC` `2025-12-31` `pre_event_30m`

![Case 13](visual_evidence_v0_2_controlled_25_per_role/images/13_byfc_2025_12_31_pre_event_30m_39d14df75d.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`194` quotes y `0` trades. La mediana
del spread es `330.47` bps y el p90 es
`533.18` bps. No se observan crossed quotes en esta ventana. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 14 - `BYFC` `2025-12-31` `pre_event_30m`

![Case 14](visual_evidence_v0_2_controlled_25_per_role/images/14_byfc_2025_12_31_pre_event_30m_d88d7a90e7.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`194` quotes y `0` trades. La mediana
del spread es `330.47` bps y el p90 es
`533.18` bps. No se observan crossed quotes en esta ventana. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 15 - `BYFC` `2025-12-31` `same_session_regular`

![Case 15](visual_evidence_v0_2_controlled_25_per_role/images/15_byfc_2025_12_31_same_session_regular_01950b2e05.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`888` quotes y `0` trades. La mediana
del spread es `198.02` bps y el p90 es
`974.79` bps. No se observan crossed quotes en esta ventana. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 16 - `BYFC` `2025-12-31` `same_session_regular`

![Case 16](visual_evidence_v0_2_controlled_25_per_role/images/16_byfc_2025_12_31_same_session_regular_1d69348482.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`888` quotes y `0` trades. La mediana
del spread es `198.02` bps y el p90 es
`974.79` bps. No se observan crossed quotes en esta ventana. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 17 - `CODX` `2025-12-31` `pre_event_30m`

![Case 17](visual_evidence_v0_2_controlled_25_per_role/images/17_codx_2025_12_31_pre_event_30m_09412eec25.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`11` quotes y `0` trades. La mediana
del spread es `158.50` bps y el p90 es
`193.95` bps. No se observan crossed quotes en esta ventana. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 18 - `CODX` `2025-12-31` `pre_event_30m`

![Case 18](visual_evidence_v0_2_controlled_25_per_role/images/18_codx_2025_12_31_pre_event_30m_5f54334c51.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`11` quotes y `0` trades. La mediana
del spread es `158.50` bps y el p90 es
`193.95` bps. No se observan crossed quotes en esta ventana. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 19 - `CODX` `2025-12-31` `pre_event_30m`

![Case 19](visual_evidence_v0_2_controlled_25_per_role/images/19_codx_2025_12_31_pre_event_30m_a5a0efa53e.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`11` quotes y `0` trades. La mediana
del spread es `158.50` bps y el p90 es
`193.95` bps. No se observan crossed quotes en esta ventana. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 20 - `CODX` `2025-12-31` `same_session_regular`

![Case 20](visual_evidence_v0_2_controlled_25_per_role/images/20_codx_2025_12_31_same_session_regular_11a2a2bc7f.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`2,020` quotes y `0` trades. La mediana
del spread es `23.72` bps y el p90 es
`122.10` bps. No se observan crossed quotes en esta ventana. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 21 - `CODX` `2025-12-31` `same_session_regular`

![Case 21](visual_evidence_v0_2_controlled_25_per_role/images/21_codx_2025_12_31_same_session_regular_5815f32b4d.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`2,020` quotes y `0` trades. La mediana
del spread es `23.72` bps y el p90 es
`122.10` bps. No se observan crossed quotes en esta ventana. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 22 - `CODX` `2025-12-31` `same_session_regular`

![Case 22](visual_evidence_v0_2_controlled_25_per_role/images/22_codx_2025_12_31_same_session_regular_a6489db03a.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`2,020` quotes y `0` trades. La mediana
del spread es `23.72` bps y el p90 es
`122.10` bps. No se observan crossed quotes en esta ventana. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 23 - `GVH` `2025-12-31` `pre_event_30m`

![Case 23](visual_evidence_v0_2_controlled_25_per_role/images/23_gvh_2025_12_31_pre_event_30m_5f6aa818cd.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`730` quotes y `0` trades. La mediana
del spread es `75.19` bps y el p90 es
`226.42` bps. No se observan crossed quotes en esta ventana. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 24 - `GVH` `2025-12-31` `pre_event_30m`

![Case 24](visual_evidence_v0_2_controlled_25_per_role/images/24_gvh_2025_12_31_pre_event_30m_dcd6122dd5.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`730` quotes y `0` trades. La mediana
del spread es `75.19` bps y el p90 es
`226.42` bps. No se observan crossed quotes en esta ventana. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 25 - `GVH` `2025-12-31` `same_session_regular`

![Case 25](visual_evidence_v0_2_controlled_25_per_role/images/25_gvh_2025_12_31_same_session_regular_a0ddb9fb9e.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`5,198` quotes y `0` trades. La mediana
del spread es `125.79` bps y el p90 es
`343.64` bps. Se observan 6 crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 26 - `GVH` `2025-12-31` `same_session_regular`

![Case 26](visual_evidence_v0_2_controlled_25_per_role/images/26_gvh_2025_12_31_same_session_regular_ec0dff985f.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`5,198` quotes y `0` trades. La mediana
del spread es `125.79` bps y el p90 es
`343.64` bps. Se observan 6 crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 27 - `INBS` `2025-12-31` `pre_event_30m`

![Case 27](visual_evidence_v0_2_controlled_25_per_role/images/27_inbs_2025_12_31_pre_event_30m_2df96d8c45.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`42,670` quotes y `0` trades. La mediana
del spread es `45.61` bps y el p90 es
`86.46` bps. Se observan 26 crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 28 - `INBS` `2025-12-31` `pre_event_30m`

![Case 28](visual_evidence_v0_2_controlled_25_per_role/images/28_inbs_2025_12_31_pre_event_30m_4e8160249c.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`19,053` quotes y `0` trades. La mediana
del spread es `37.31` bps y el p90 es
`78.13` bps. Se observan 16 crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 29 - `INBS` `2025-12-31` `pre_event_30m`

![Case 29](visual_evidence_v0_2_controlled_25_per_role/images/29_inbs_2025_12_31_pre_event_30m_b0847518e3.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`42,670` quotes y `0` trades. La mediana
del spread es `45.61` bps y el p90 es
`86.46` bps. Se observan 26 crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 30 - `INBS` `2025-12-31` `pre_event_30m`

![Case 30](visual_evidence_v0_2_controlled_25_per_role/images/30_inbs_2025_12_31_pre_event_30m_ce32f4195f.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`33,933` quotes y `0` trades. La mediana
del spread es `41.64` bps y el p90 es
`79.37` bps. Se observan 19 crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 31 - `INBS` `2025-12-31` `pre_event_30m`

![Case 31](visual_evidence_v0_2_controlled_25_per_role/images/31_inbs_2025_12_31_pre_event_30m_ea509fce4b.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`33,933` quotes y `0` trades. La mediana
del spread es `41.64` bps y el p90 es
`79.37` bps. Se observan 19 crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 32 - `INBS` `2025-12-31` `pre_event_30m`

![Case 32](visual_evidence_v0_2_controlled_25_per_role/images/32_inbs_2025_12_31_pre_event_30m_ef79a19e52.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`19,053` quotes y `0` trades. La mediana
del spread es `37.31` bps y el p90 es
`78.13` bps. Se observan 16 crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 33 - `INBS` `2025-12-31` `same_session_regular`

![Case 33](visual_evidence_v0_2_controlled_25_per_role/images/33_inbs_2025_12_31_same_session_regular_1230a98188.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`231,722` quotes y `0` trades. La mediana
del spread es `44.03` bps y el p90 es
`82.39` bps. Se observan 143 crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 34 - `INBS` `2025-12-31` `same_session_regular`

![Case 34](visual_evidence_v0_2_controlled_25_per_role/images/34_inbs_2025_12_31_same_session_regular_25548764b9.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`231,722` quotes y `0` trades. La mediana
del spread es `44.03` bps y el p90 es
`82.39` bps. Se observan 143 crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 35 - `INBS` `2025-12-31` `same_session_regular`

![Case 35](visual_evidence_v0_2_controlled_25_per_role/images/35_inbs_2025_12_31_same_session_regular_4a13b7a946.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`231,722` quotes y `0` trades. La mediana
del spread es `44.03` bps y el p90 es
`82.39` bps. Se observan 143 crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 36 - `INBS` `2025-12-31` `same_session_regular`

![Case 36](visual_evidence_v0_2_controlled_25_per_role/images/36_inbs_2025_12_31_same_session_regular_b5b49ae6be.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`231,722` quotes y `0` trades. La mediana
del spread es `44.03` bps y el p90 es
`82.39` bps. Se observan 143 crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 37 - `INBS` `2025-12-31` `same_session_regular`

![Case 37](visual_evidence_v0_2_controlled_25_per_role/images/37_inbs_2025_12_31_same_session_regular_e47375d62c.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`231,722` quotes y `0` trades. La mediana
del spread es `44.03` bps y el p90 es
`82.39` bps. Se observan 143 crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 38 - `INBS` `2025-12-31` `same_session_regular`

![Case 38](visual_evidence_v0_2_controlled_25_per_role/images/38_inbs_2025_12_31_same_session_regular_e91d668b15.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`231,722` quotes y `0` trades. La mediana
del spread es `44.03` bps y el p90 es
`82.39` bps. Se observan 143 crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato. No hay trades fuente para esta ventana; el caso queda como `review_partial_source` y no puede interpretarse como microestructura completa para ejecucion.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 39 - `JXG` `2025-12-31` `pre_event_30m`

![Case 39](visual_evidence_v0_2_controlled_25_per_role/images/39_jxg_2025_12_31_pre_event_30m_4c13f5636d.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`765` quotes y `297` trades. La mediana
del spread es `2,496.05` bps y el p90 es
`4,643.18` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `88.22%`, el duplicate exact ratio es `0.00%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 40 - `JXG` `2025-12-31` `pre_event_30m`

![Case 40](visual_evidence_v0_2_controlled_25_per_role/images/40_jxg_2025_12_31_pre_event_30m_80beb9355a.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`765` quotes y `297` trades. La mediana
del spread es `2,496.05` bps y el p90 es
`4,643.18` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `88.22%`, el duplicate exact ratio es `0.00%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 41 - `JXG` `2025-12-31` `same_session_regular`

![Case 41](visual_evidence_v0_2_controlled_25_per_role/images/41_jxg_2025_12_31_same_session_regular_19495db16a.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`2,107` quotes y `2,219` trades. La mediana
del spread es `1,917.81` bps y el p90 es
`3,540.00` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `93.87%`, el duplicate exact ratio es `1.80%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 42 - `JXG` `2025-12-31` `same_session_regular`

![Case 42](visual_evidence_v0_2_controlled_25_per_role/images/42_jxg_2025_12_31_same_session_regular_28ee80d663.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`2,107` quotes y `2,219` trades. La mediana
del spread es `1,917.81` bps y el p90 es
`3,540.00` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `93.87%`, el duplicate exact ratio es `1.80%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 43 - `OTLK` `2025-12-31` `pre_event_30m`

![Case 43](visual_evidence_v0_2_controlled_25_per_role/images/43_otlk_2025_12_31_pre_event_30m_8087871c2e.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`1,483` quotes y `2,196` trades. La mediana
del spread es `63.09` bps y el p90 es
`63.09` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `39.98%`, el duplicate exact ratio es `1.28%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 44 - `OTLK` `2025-12-31` `pre_event_30m`

![Case 44](visual_evidence_v0_2_controlled_25_per_role/images/44_otlk_2025_12_31_pre_event_30m_fc7e4df378.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`1,483` quotes y `2,196` trades. La mediana
del spread es `63.09` bps y el p90 es
`63.09` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `39.98%`, el duplicate exact ratio es `1.28%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 45 - `OTLK` `2025-12-31` `same_session_regular`

![Case 45](visual_evidence_v0_2_controlled_25_per_role/images/45_otlk_2025_12_31_same_session_regular_1e58478ed7.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`22,121` quotes y `20,154` trades. La mediana
del spread es `60.79` bps y el p90 es
`63.90` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `35.75%`, el duplicate exact ratio es `1.66%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 46 - `OTLK` `2025-12-31` `same_session_regular`

![Case 46](visual_evidence_v0_2_controlled_25_per_role/images/46_otlk_2025_12_31_same_session_regular_1fdcf467af.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`22,121` quotes y `20,154` trades. La mediana
del spread es `60.79` bps y el p90 es
`63.90` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `35.75%`, el duplicate exact ratio es `1.66%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 47 - `PAVM` `2025-12-31` `pre_event_30m`

![Case 47](visual_evidence_v0_2_controlled_25_per_role/images/47_pavm_2025_12_31_pre_event_30m_3dabb8482c.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`11` quotes y `14,526` trades. La mediana
del spread es `234.54` bps y el p90 es
`465.12` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `NA%`, el duplicate exact ratio es `NA%` y el off-regular-session ratio es `NA%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 48 - `PAVM` `2025-12-31` `pre_event_30m`

![Case 48](visual_evidence_v0_2_controlled_25_per_role/images/48_pavm_2025_12_31_pre_event_30m_9915bcd220.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento. En esta imagen hay
`11` quotes y `14,526` trades. La mediana
del spread es `234.54` bps y el p90 es
`465.12` bps. No se observan crossed quotes en esta ventana. En trades, el odd-lot ratio es `NA%`, el duplicate exact ratio es `NA%` y el off-regular-session ratio es `NA%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 49 - `PAVM` `2025-12-31` `same_session_regular`

![Case 49](visual_evidence_v0_2_controlled_25_per_role/images/49_pavm_2025_12_31_same_session_regular_669312c293.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`1,567` quotes y `14,526` trades. La mediana
del spread es `137.99` bps y el p90 es
`348.89` bps. Se observan 4 crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato. En trades, el odd-lot ratio es `92.37%`, el duplicate exact ratio es `0.70%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.

### Case 50 - `PAVM` `2025-12-31` `same_session_regular`

![Case 50](visual_evidence_v0_2_controlled_25_per_role/images/50_pavm_2025_12_31_same_session_regular_91e947bf8b.png)

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento. En esta imagen hay
`1,567` quotes y `14,526` trades. La mediana
del spread es `137.99` bps y el p90 es
`348.89` bps. Se observan 4 crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato. En trades, el odd-lot ratio es `92.37%`, el duplicate exact ratio es `0.70%` y el off-regular-session ratio es `0.00%`.

**Decision de consumo.** `execution_sim_candidate=False`,
`backtest_core_microstructure_candidate=False`,
`full_universe_claim=False`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.
