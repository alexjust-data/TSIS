# Short | Recovery And Limits

En `short`, recuperar lo máximo posible no significa elevar Polygon a baseline.

Significa:

- salvar el valor de `short` usando la fuente correcta
- y acotar dónde Polygon sí aporta algo

## Capa causal

Base:

- [short_causal_alignment_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\short\cache_v2\short_causal_alignment_summary.parquet)
- [short_interest_context_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\short\cache_v2\short_interest_context_summary.parquet)

`short_volume`:

- `short_flow_near_market_anomaly = 53,229`
- `short_flow_near_halt = 88`
- `short_flow_market_clean = 2,603`

`short_interest`:

- `days_to_cover_spike_near_halt = 1,790`
- `high_short_interest_context = 203`

## Recuperación defendible

Lo recuperable de verdad es:

- `short_volume` como contexto diario
- `short_flow_near_halt` como subconjunto fuerte
- `short_interest` como contexto lento de crowding / squeeze risk

## Lo que no conviene forzar

- `Polygon short_volume` como baseline histórico principal
- `short_interest` como señal causal intradía fina

## Salvedad de cobertura histórica ticker-based

La auditoría vieja de `C:\\TSIS_Data\\data\\short_data` ya había detectado:

- cobertura desigual
- riesgo real de ticker reuse contamination

Por eso la vía de recuperación limpia es:

- usar baseline FINRA
- y, si se quiere conservar Polygon, hacerlo en root fresco `<1B>` y con semántica secundaria
