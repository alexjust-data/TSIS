# Intraday Regime Features - Semantic Pilot Results `v0_1`

## 1. Rol

Este documento fija el veredicto semantico del primer piloto de:

- `intraday_regime_features`

como consumidor real de:

- `ohlcv_1m_split_normalized`

No sustituye el readout visual.

Lo resume y lo convierte en una conclusion contractual trazable.

Readout principal:

- `01_foundations/inspection_dossiers/intraday_regime_features/intraday_regime_features_semantic_pilot_readout_v0_1.md`

## 2. Pregunta auditada

La pregunta correcta no era:

- "se generaron columnas?"

La pregunta correcta era:

- las features cross-session cambian materialmente cuando `raw` arrastraria un shock mecanico de split?
- y permanecen neutras cuando no deberian cambiar?

## 3. Resultado global

El piloto confirma la semantica esperada.

### Casos positivos fuertes

Reverse splits:

- `BNGO 2025-01` -> `max_abs_gap_diff_pct = 5183.28%`
- `CEI 2022-12` -> `4900.00%`
- `BXRX 2022-12` -> `3897.11%`
- `COSM 2022-12` -> `2450.70%`

Forward splits:

- `EFSH 2025-01` -> `111.76%`
- `LIVE 2014-02` -> `66.67%`

Estos casos demuestran que, cuando el evento cae dentro de la memoria util de la feature:

- `raw` fabricaria gaps y cambios de extension falsos;
- y `split_normalized` los neutraliza.

### Casos frontera coherentes

- `PD 2006-03` -> `49.81%`
- `SAVA 2023-12` -> `28.49%`

Estos casos no contradicen la semantica.

Indican ventanas donde:

- el efecto existe;
- pero la memoria util del feature ya no carga tanto pasado reescalable dentro del mismo mes.

### Controles correctos

- `BXRX 2022-11` -> `0.00%`
- `BNGO 2025-02` -> `0.00%`

Esto prueba dos cosas importantes:

- un control pre-evento puede vivir con `future_split_factor != 1` y aun asi no distorsionar features si toda la ventana permanece en escala relativa homogénea;
- un control post-evento neutro permanece exactamente neutro.

## 4. Que demuestra de verdad

El piloto no demuestra que el modelo final ya exista.

Si demuestra que:

- la separacion contractual entre `cross-session` y `intrasesion local` ya produce un efecto metodologicamente correcto;
- `1m_split_normalized` no se usa aqui como decoracion, sino para corregir precisamente la familia de errores que queriamos eliminar;
- y el primer consumidor ya enseña, con controles y casos positivos, que el problema de falsos gaps y falsos shocks de regime era real.

## 5. Veredicto contractual

### Sobre `intraday_regime_features`

La capa ya no debe clasificarse solo como:

- `Nivel 2 - Implementada`

Su nivel correcto pasa a:

- `Nivel 3 - Pilotada`

porque ya tiene:

- implementacion real;
- output persistido;
- piloto semantico;
- controles;
- y readout visual auditado.

### Sobre `ohlcv_1m_split_normalized`

La capa ya no debe quedarse solo en:

- `Nivel 4 - Auditada`

Su nivel correcto pasa a:

- `Nivel 5 - Consumida`

porque ahora ya existe:

- un consumidor real implementado;
- una lectura visual y cuantitativa del efecto en ese consumidor;
- y evidencia de que ese consumidor deja de ver shocks mecanicos falsos cuando usa la capa correcta.

## 6. Que falta despues de esto

Todavia no estamos en:

- `Nivel 6 - Promovida`

para ninguna de las dos capas.

Falta:

- ampliar cobertura mas alla del universo piloto;
- correr validacion agregada masiva;
- y conectar `intraday_regime_features` a un downstream de research, ML o backtest contextual mas amplio.
