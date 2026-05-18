# Daily | Recovery And Coverage

En `daily`, el gran frente de recuperación no es el bar inválido. Es la cobertura.

## Qué se puede recuperar

Sobre los `653` tickers `<1B>` sin `complete_daily`:

- `LIKELY_VALID_GAP_ONLY`: `374` (`57.27%`)
- `AMBIGUOUS_REVIEW`: `222` (`34.00%`)
- `REALLY_PROBLEMATIC_UNEXPECTED`: `57` (`8.73%`)

La lectura correcta es:

- más de la mitad del faltante no parece fallo real
- un tercio queda en revisión
- el bloque realmente duro es pequeño

## `LIKELY_VALID_GAP_ONLY`

Esto es recuperación casi directa.

Semántica:

- no es agujero bruto de mercado
- es gap compatible con ventana válida o expectativa razonable del dataset

Ejemplo visual ya existente:

- [001.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\daily\img\001.png)

Lectura:

- `CMPX` muestra huecos que no rompen la coherencia transversal del activo

Decisión:

- `recoverable_without_penalty` a nivel cobertura

## `AMBIGUOUS_REVIEW`

Semántica:

- no queda probado como faltante malo
- tampoco como gap claramente válido

Decisión:

- `recoverable_with_flag`
- mantener en `review` hasta cierre global

## `REALLY_PROBLEMATIC_UNEXPECTED`

Aquí la tentación sería leerlos como fallo duro de `daily`.

No conviene hacerlo tan rápido.

Hecho importante:

- los `57` tienen `1m`, `quotes` y `trades` en `100%`
- firma de cobertura: `1m|quotes|trades` para todos
- `non_contiguous_span`: `100%`

Base:

- [problematic57_cross_1m_quotes_trades_summary.json](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit\problematic57_cross_1m_quotes_trades_full\problematic57_cross_1m_quotes_trades_summary.json)
- [007.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\daily\img\007.png)

Lectura:

- no es “no existía mercado”
- es frontera abierta de cobertura específica de `daily`

Decisión:

- no recuperarlos como `good`
- no tratarlos todavía como `bad` bruto
- dejarlos como `review_not_rehabilitated` de cobertura
