# Intraday Regime Features Consumption Policy `v0_1`

## 1. Decision

`intraday_regime_features_v0_1` queda aprobada como:

- consumidor piloto validado de `ohlcv_1m_split_normalized`;
- capa de features/states para investigacion contextual;
- evidencia de que las comparaciones cross-session no deben calcularse sobre `1m raw` cuando hay riesgo de splits.

No queda aprobada todavia como:

- feature layer full-universe `<1B>`;
- input obligatorio de todo backtest;
- simulador de ejecucion;
- policy RL;
- ni modelo final de alpha.

Lectura de fase:

- ahora sirve para validar arquitectura y semantica de normalizacion;
- mas adelante puede convertirse en atributos/states para backtest o ML;
- hoy no debe tratarse como bloque central del backtest base.

## 2. Usos permitidos

Usos permitidos actuales:

- auditoria de semantica downstream de `1m_split_normalized`;
- research de estados intradia en los tickers piloto;
- pruebas de leakage y feature semantics;
- diseno de contratos futuros para features/states full-universe;
- soporte conceptual para ML/backtest que cruce sesiones.

Preguntas que puede ayudar a formular en una fase posterior:

- si abre extendida contra la sesion anterior;
- si esta cerca o lejos del rango previo;
- si la volatilidad reciente esta comprimida o expandida;
- si el gap es excepcional contra su historia reciente;
- si la sesion rompe el contexto de los ultimos dias.

Estas preguntas no equivalen todavia a edge validado ni a autorizacion de consumo global.

## 3. Usos prohibidos hasta nueva promocion

No se debe usar como:

- input full-universe `<1B>` sin comprobar coverage;
- feature primaria de backtest global;
- dependencia bloqueante del backtest base;
- variable de decision live;
- input de RL productivo;
- evidencia de edge economico por si misma.

## 4. Regla de vista de precio

Toda feature cross-session debe declarar que usa:

- `cross_session_price_view = 1m_split_normalized_v0_1`

Toda feature intrasesion local debe declarar que usa:

- `intraday_price_view = 1m_raw`

Si una feature cross-session se calcula sobre raw, debe tratarse como sospechosa hasta auditoria explicita.

Si una feature local intrasesion se calcula sobre split-normalized, debe justificar por que la verdad local raw no bastaba.

## 5. Condiciones para promocion futura

Para pasar de piloto a capa productiva de research/backtest, debe existir:

- universo objetivo explicito `<1B>`;
- materializacion reproducible sobre ese universo;
- coverage esperado/presente/healthy/usable;
- validadores de schema, nulos, lookbacks y provenance;
- politica de leakage temporal;
- decision documentada sobre frecuencia `ticker-day` vs `ticker-minute`;
- auditoria agregada y casos visuales fuera del lote piloto;
- compatibilidad con `daily_adjusted`, `reference`, `halts`, `quotes` y `trades` cuando entren en la feature layer.

## 6. Veredicto

La capa es importante para TSIS porque transforma la validacion de `1m_split_normalized` en un estado/feature downstream real.

Pero su madurez actual debe leerse como:

- `pilot_semantic_validation_consumer`

no como:

- `full_universe_feature_layer`.

Regla final:

- conservarla como consumidor piloto y memoria metodologica;
- no expandirla por ahora como set de atributos definitivo;
- volver a ella cuando el proyecto entre formalmente en feature/state research o cuando un backtest/ML necesite memoria cross-session intradia.
