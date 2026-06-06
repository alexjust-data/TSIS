# Intraday Regime Features Variable Taxonomy `v0_1`

## 1. Rol

Este documento clasifica la primera familia minima de variables para `intraday_regime_features`.

No define aun el modelo final.

Define:

- que variables tienen mas sentido como primera promocion;
- que vista de precio debe usar cada grupo;
- y por que.

## 2. Regla maestra

No todas las variables de contexto intradia deben calcularse con la misma vista.

### Grupo A

Variables de comparabilidad entre sesiones:

- deben usar `1m_split_normalized`

### Grupo B

Variables de estado local de la sesion:

- deben usar `1m raw`

### Grupo C

Variables de microestructura fina:

- quedan para fase posterior con `quotes_raw` y `trades_raw`

## 2.1 Justificacion cientifica resumida

La taxonomia no se apoya solo en comodidad de implementacion.

Se apoya en cuatro ideas metodologicas:

- features que cruzan sesiones no deben calcularse con precios contaminados por corporate actions;
- datos intradia permiten construir medidas mas ricas de estado y volatilidad que el daily agregado;
- hay predictibilidad intradia y no toda la informacion vive en la ultima barra;
- y gap overnight, forma del volumen y expansion de rango son variables con respaldo empirico.

Referencias clave:

- Felton, Jain, *True Returns: Adjusting Stock Prices for Cash Dividends and Stock Splits*
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3354728
- Andersen et al., *Modeling and Forecasting Realized Volatility*
  - https://www.nber.org/papers/w8160
- Huddleston, Liu, Stentoft, *Intraday Market Predictability: A Machine Learning Approach*
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3726765
- Heston, Korajczyk, Sadka, *Intraday Patterns in the Cross-section of Stock Returns*
  - https://arxiv.org/abs/1005.3535
- Perreten, Wallmeier, *Overnight Returns and the Timing of Trading Volume*
  - https://papers.ssrn.com/sol3/Delivery.cfm/5004991.pdf?abstractid=5004991&mirid=1

## 3. Grupo A | Usa `1m_split_normalized`

### 3.1 Gaps y retornos entre sesiones

- `gap_open_vs_prev_close`
- `premarket_move_vs_prev_close`
- `open_vs_prev_session_close`
- `multi_session_return_1d_to_open`
- `multi_session_return_3d_to_open`
- `multi_session_return_n_to_now`

Por que:

- comparan precios de sesiones distintas;
- y sin split-normalization pueden absorber corporate actions como si fueran cambio real.
- este es exactamente el tipo de error que Felton y Jain muestran para series no ajustadas, trasladado aqui al uso cross-session de `1m`.

### 3.2 Distancias relativas a referencias previas

- `distance_to_prev_day_high`
- `distance_to_prev_day_low`
- `distance_to_prev_day_close`
- `distance_to_n_day_high`
- `distance_to_n_day_low`

Por que:

- miden extension o compresion respecto a sesiones previas;
- y requieren una base de escala consistente.
- sin esa consistencia, una distancia grande puede ser solo residuo mecanico de split y no extension real del activo.

### 3.3 Rango y volatilidad multi-sesion

- `prev_day_range_pct`
- `n_day_range_expansion`
- `realized_vol_prev_n_sessions`
- `overnight_gap_zscore`

Por que:

- resumen comportamiento reciente del activo a traves de sesiones;
- y no deben contaminarse por splits.
- Andersen et al. justifican precisamente el uso de medidas realizadas y agregadas de alta frecuencia para describir mejor el estado del activo.

## 4. Grupo B | Usa `1m raw`

### 4.1 Geometria local de la sesion

- `intraday_return_since_open`
- `bar_return_1m`
- `bar_range_pct`
- `distance_to_session_high`
- `distance_to_session_low`
- `pullback_from_session_high`

Por que:

- describen la sesion observada tal como cotiza;
- y su verdad primaria es local, no inter-sesion.
- aqui el objetivo no es continuidad historica de escala, sino fidelidad a la sesion actual.

### 4.2 Actividad local

- `bar_volume`
- `cum_volume_session`
- `session_vwap_distance`
- `opening_drive_strength`
- `intraday_range_expansion_session`

Por que:

- son features del comportamiento de la sesion actual;
- no de continuidad historica entre dias.
- por tanto, corregirlas con `split_normalized` por defecto anadiria una mediacion innecesaria donde la verdad local raw ya es la semantica correcta.

## 5. Grupo C | Fase posterior con `quotes_raw` y `trades_raw`

- `spread_bps`
- `effective_spread`
- `signed_volume_imbalance`
- `crossed_quote_flags`
- `quote_instability`
- `odd_lot_dominance`
- `tape_integrity_flags`
- `duplicate_trade_pressure`

Por que:

- estas variables viven en la microestructura fina;
- no deben meterse en la primera promocion de `1m_split_normalized`.
- Heston, Korajczyk y Sadka apoyan que estas familias contienen estructura informativa, pero metodologicamente pertenecen a otra capa mas cercana a `quotes_raw` y `trades_raw`.

## 6. Regla de auditoria

Si una variable cruza sesiones y se calculo sobre `1m raw`, debe considerarse sospechosa hasta demostrar lo contrario.

Si una variable es puramente intrasesion y se calculo sobre `1m_split_normalized`, debe justificarse explicitamente por que no bastaba `1m raw`.

## 7. Veredicto

La primera promocion de `intraday_regime_features` debe centrarse en:

- contexto cross-session seguro con `1m_split_normalized`
- estado local de sesion con `1m raw`

y dejar la microestructura fina para una segunda capa metodologicamente distinta.

## 8. Referencias metodologicas

- Felton, Jain, *True Returns: Adjusting Stock Prices for Cash Dividends and Stock Splits*
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3354728
- Andersen, Bollerslev, Diebold, Labys, *Modeling and Forecasting Realized Volatility*
  - https://www.nber.org/papers/w8160
- Huddleston, Liu, Stentoft, *Intraday Market Predictability: A Machine Learning Approach*
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3726765
- Heston, Korajczyk, Sadka, *Intraday Patterns in the Cross-section of Stock Returns*
  - https://arxiv.org/abs/1005.3535
- Perreten, Wallmeier, *Overnight Returns and the Timing of Trading Volume*
  - https://papers.ssrn.com/sol3/Delivery.cfm/5004991.pdf?abstractid=5004991&mirid=1
