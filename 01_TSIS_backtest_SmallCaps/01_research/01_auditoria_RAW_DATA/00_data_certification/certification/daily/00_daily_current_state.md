# Daily | Current State

`daily` llega a certificación en mejor estado que `trades`.

La lectura correcta separa dos planos:

- calidad del bar `daily`
- cobertura de años faltantes frente al universo `<1B>`

## Calidad del bar

Base:

- [04_daily_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\daily\04_daily_closeout.md)
- [daily_lt1b_hard_invalid_exclusion_summary.json](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit\daily_lt1b_hard_invalid_exclusion_v030\daily_lt1b_hard_invalid_exclusion_summary.json)

Estado:

- universo `daily <1B>` auditado: `44,423` ticker-year files
- tail duro excluido: `102`
- peso del tail duro: `0.23%`
- resto recuperable como `good` o `review`: `99.77%`

## Cobertura

Base:

- [lt1b_vs_complete_daily_summary.json](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit\lt1b_vs_complete_daily_post_57_recovery\lt1b_vs_complete_daily_summary.json)
- [lt1b_missing_vs_universe_audit_summary.json](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit\lt1b_missing_vs_universe_audit_post_57_recovery\lt1b_missing_vs_universe_audit_summary.json)

Estado:

- universo `<1B>` total: `4,824` tickers
- con `complete_daily`: `4,171`
- sin `complete_daily`: `653`

Dentro de esos `653`:

- `374` `LIKELY_VALID_GAP_ONLY`
- `222` `AMBIGUOUS_REVIEW`
- `57` `REALLY_PROBLEMATIC_UNEXPECTED`

## Lectura inicial

`daily` no entra a certificación como dataset roto.

Entra como:

- dataset muy sano en calidad de bar
- con una frontera de cobertura que necesita clasificación fina
