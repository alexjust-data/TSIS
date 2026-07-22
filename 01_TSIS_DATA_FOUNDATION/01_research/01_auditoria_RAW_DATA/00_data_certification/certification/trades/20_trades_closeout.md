# Trades | Closeout

Este bloque ya queda suficientemente cerrado para entrar en la certificacion final sin rehacer la auditoria base.

## Base correcta del bloque

La lectura final de `trades` debe apoyarse en tres capas distintas:

- universo full indexado `<1B>` de `9,429,112` files
- residuo `D full` de `390,475` files
- semantica fina de `file_acceptance`

Rutas base:

- [00_trades_current_state.md](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/certification/trades/00_trades_current_state.md)
- [02_trades_base_certification_decision.md](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/certification/trades/02_trades_base_certification_decision.md)
- [03_trades_old_vs_new_bucket_bridge.md](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/certification/trades/03_trades_old_vs_new_bucket_bridge.md)

## Lectura final de buckets

- `good`
  - real, pero muy pequeno
- `bad_data`
  - `bad`
- `reference_scale_mismatch`
  - `review`
- `review_microstructure`
  - `review`
- `review_1m_reference_alignment`
  - `review`
- `review_no_1m_reference`
  - `review`
- `review`
  - `review`

Soporte:

- [10_trades_bucket_synthesis.md](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/certification/trades/10_trades_bucket_synthesis.md)
- [12_trades_good.md](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/certification/trades/12_trades_good.md)

## Recuperacion

La conclusion importante del bloque es que `review` no equivale a perdida total.

Recuperacion ya defendible:

- `review_no_1m_reference`
  - recuperable `with_flag`
- `review_microstructure`
  - recuperable parcialmente segun uso
- `review_1m_reference_alignment`
  - recuperable con limitacion
- `review`
  - recuperable en gran parte mediante regla explicita

Recuperacion potencial pero aun no operativa:

- `reference_scale_mismatch`
  - pendiente de prueba de reconciliacion de escala

Soporte:

- [18_trades_recovery_synthesis.md](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/certification/trades/18_trades_recovery_synthesis.md)
- [19_trades_final_recovery_policy.md](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/certification/trades/19_trades_final_recovery_policy.md)

## Regla oficial recomendada

Estados finales recomendados para certificacion:

- `good`
- `recoverable_with_flag`
- `review_not_rehabilitated`
- `bad`

Regla estricta oficial para rehabilitar `review`:

- `daily_vw_to_trade_vw` cerca de `1x`
- `trade_vwap_vs_daily_vw_diff_pct_raw <= 0.5`
- `outside_daily_regular_pct <= 1`
- `outside_1m_regular_pct <= 15`

Resultado historico sobre el estado parcial de `57e/full_clean` materializado:

- `review` total: `2,825,748`
- `review` rehabilitable estricto: `2,427,056`
- `85.89%` del bucket
- residuo no rehabilitado: `398,692`

Estado final de referencia ahora:

- usar `57f/full_clean_fast_same_schema` como cache canonico de cierre
- conservar `57e/full_clean` solo como run parcial anterior sobre el mismo indice full `<1B>`

Estado agregado final observado en `57f/full_clean_fast_same_schema`:

- `review`: `4,851,211`
- `reference_scale_mismatch`: `2,418,062`
- `review_microstructure`: `2,130,781`
- `bad_data`: `15,869`
- `review_no_1m_reference`: `8,091`
- `review_1m_reference_alignment`: `4,992`
- `good`: `106`
- cobertura raw full: `9,429,112` files

Lectura de esa transicion:

- el soporte cuantitativo historico del bloque nacio con el parcial de `57e`
- el cierre operativo final ya debe leerse sobre `57f`
- la regla de rehabilitacion estricta sigue documentada, pero sus cifras historicas no deben confundirse con el agregado final completo mientras no se rematerialice esa derivacion sobre `57f`

## Veredicto del bloque

Veredicto practico:

- `trades` no debe cerrarse como "casi todo review no usable"
- tampoco como "todo recuperable"

La lectura correcta es:

- existe un nucleo `bad` pequeno y real
- existe un `good` semanticamente limpio pero escaso
- existe una masa grande de `review` que si puede rehabilitarse con reglas explicitas y flags de uso
- y queda un residuo `review_not_rehabilitated` que debe conservarse como tal en la certificacion final
