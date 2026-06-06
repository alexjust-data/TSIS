# Intraday Regime Features - Initial Materialization Results `v0_1`

## 1. Rol

Este documento registra el primer aterrizaje ejecutable real de:

- `intraday_regime_features`

como consumidor inicial de:

- `ohlcv_1m_split_normalized`

y deja trazado:

- que script se ejecuto;
- que universo cubrio;
- que features quedaron materializadas;
- y que demuestra esta primera corrida.

## 2. Script ejecutado

Script:

- `scripts/materialize_intraday_regime_features.py`

Fuentes usadas:

- `D:\ohlcv_1m`
- `E:\TSIS\data\ohlcv_1m_split_normalized`

Salida materializada:

- `E:\TSIS\data\intraday_regime_features`

## 3. Grano materializado

Version inicial:

- `ticker-day`

Esto significa que cada fila representa:

- un ticker;
- una fecha;
- y un conjunto de features de contexto intradia ya agregadas a nivel sesion.

No representa todavia:

- un estado online minuto a minuto;
- ni una policy final de entrada/salida;
- ni una simulacion de ejecucion.

## 4. Universo cubierto en esta primera corrida

La primera corrida se apoyo en el universo piloto actualmente disponible en:

- `E:\TSIS\data\ohlcv_1m_split_normalized`

Tickers materializados:

- `BNGO`
- `BXRX`
- `CEI`
- `COSM`
- `EFSH`
- `LIVE`
- `PD`
- `SAVA`

Resumen de la corrida:

- `BNGO` -> `2` files vistos, `1` year file escrito, `47` day rows
- `BXRX` -> `2` files vistos, `1` year file escrito, `48` day rows
- `CEI` -> `1` file visto, `1` year file escrito, `26` day rows
- `COSM` -> `1` file visto, `1` year file escrito, `26` day rows
- `EFSH` -> `1` file visto, `1` year file escrito, `26` day rows
- `LIVE` -> `1` file visto, `1` year file escrito, `23` day rows
- `PD` -> `1` file visto, `1` year file escrito, `23` day rows
- `SAVA` -> `1` file visto, `1` year file escrito, `24` day rows

## 5. Familias de features realmente materializadas

### A. Features cross-session sobre `1m_split_normalized`

Quedaron materializadas:

- `gap_open_vs_prev_close`
- `open_vs_prev_session_close`
- `open_vs_prev_session_high`
- `open_vs_prev_session_low`
- `multi_session_return_3d_to_open`
- `multi_session_return_5d_to_open`
- `distance_to_prev_day_range_center`
- `prev_day_range_pct_norm`
- `range_expansion_vs_prev_day_norm`
- `distance_to_n_day_high_5`
- `distance_to_n_day_low_5`
- `realized_vol_prev_3_sessions_norm`
- `overnight_gap_zscore_20`

### B. Features intrasesion locales sobre `1m raw`

Quedaron materializadas:

- `intraday_return_since_open_raw`
- `session_range_pct_raw`
- `cum_volume_session_raw`
- `opening_drive_30m_raw`
- `pullback_from_session_high_raw`
- `session_vwap_distance_raw`

### C. Metadatos de auditoria

Tambien quedan materializados:

- `cross_session_price_view = 1m_split_normalized_v0_1`
- `intraday_price_view = 1m_raw`
- `feature_contract = intraday_regime_features_v0_1`
- `feature_grain = ticker_day`
- `source_raw_root`
- `source_split_normalized_root`

## 6. Que demuestra esta primera corrida

Esta corrida no demuestra todavia:

- que las features sean ya el set final;
- ni que el modelo intradia este resuelto;
- ni que la capa ya este promovida a full-universe.

Pero si demuestra algo importante:

- la separacion contractual entre `cross-session` y `intrasesion local` ya no vive solo en markdown;
- ya existe una materializacion real que la implementa;
- y `ohlcv_1m_split_normalized` ya tiene un primer consumidor tecnicamente conectado.

## 7. Lectura tecnica

El avance real aqui no es "tener mas columnas".

El avance real es que, por primera vez, el pipeline deja explicitamente fijado que:

- las comparaciones entre sesiones usan precios reescalados para no absorber splits como si fueran alpha;
- mientras que la geometria local de la sesion sigue leyendo el mercado observado tal como cotiza.

Eso traduce la semantica de `1m_split_normalized` a una utilidad concreta para ML y research de regimen.

## 8. Consecuencia de madurez

Despues de esta materializacion:

- `intraday_regime_features` ya no debe clasificarse solo como `Definida`

Su nivel correcto pasa a:

- `Nivel 2 - Implementada`

Porque ya existen:

- script;
- output persistido;
- layout real;
- y una corrida reproducible.

Todavia no pasa a `Pilotada` porque falta:

- una lectura semantica dedicada de las propias features;
- controles mas especificos sobre los falsos gaps corregidos;
- y una evidencia de que el consumidor downstream mejora exactamente el error objetivo.
