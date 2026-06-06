# Daily Adjusted Full-Universe Audit v0.1

## Rol

Este documento audita el estado real actual de `daily_adjusted` frente al objetivo full-universe `2005-2026`.
Sus resultados son la evidencia agregada usada para sostener la promocion institucional de la capa.

## Universo comparado

- fuente raw: `D:\ohlcv_daily`
- capa ajustada actual: `E:\TSIS\data\ohlcv_daily_adjusted`

## Resultado agregado

- `raw_tickers = 12494`
- `adjusted_tickers = 12230`
- `raw_tickers_with_files = 12230`
- `adjusted_tickers_with_files = 12230`
- `raw_year_files = 125438`
- `adjusted_year_files = 125438`
- `ticker_coverage_pct = 97.8870%`
- `ticker_with_files_coverage_pct = 100.0000%`
- `year_file_coverage_pct = 100.0000%`
- `missing_outputs = 0`
- `extra_adjusted_outputs = 0`
- `read_error_files = 0`
- `files_missing_required_columns = 0`
- `nonpositive_factor_rows = 0`
- `null_factor_rows = 0`
- `bad_price_view_rows = 0`
- `empty_source_daily_rows = 0`
- `missing_source_daily_file_rows = 0`
- `adjusted_rows_total = 27418158`
- `split_non1_rows_total = 2335782`
- `div_non1_rows_total = 3210135`
- `adj_non1_rows_total = 3192661`

## Perfil de activacion dentro de la capa ya materializada

- `neutral_control = 9816`
- `split_only = 1210`
- `dividend_only = 861`
- `split_and_dividend = 343`

## Tickers actualmente materializados

La tabla completa por ticker se exporta en:

- `evidence_assets/daily_adjusted_full_universe_audit/daily_adjusted_ticker_activation_summary.csv`
- `evidence_assets/daily_adjusted_full_universe_audit/daily_adjusted_ticker_activation_summary.parquet`

Primeros casos de la tabla ordenada por perfil y ticker:

- `AAME` -> `year_files=22`, `rows=4949`, `split_non1=0`, `div_non1=4721`, `adj_non1=4721`, `profile=dividend_only`
- `AAN` -> `year_files=16`, `rows=3892`, `split_non1=0`, `div_non1=3877`, `adj_non1=3877`, `profile=dividend_only`
- `AATC` -> `year_files=6`, `rows=1150`, `split_non1=0`, `div_non1=1140`, `adj_non1=1140`, `profile=dividend_only`
- `ABL` -> `year_files=11`, `rows=1980`, `split_non1=0`, `div_non1=1961`, `adj_non1=1961`, `profile=dividend_only`
- `ABTX` -> `year_files=8`, `rows=1758`, `split_non1=0`, `div_non1=1735`, `adj_non1=1735`, `profile=dividend_only`
- `AC` -> `year_files=13`, `rows=2742`, `split_non1=0`, `div_non1=2684`, `adj_non1=2684`, `profile=dividend_only`
- `ACCO` -> `year_files=15`, `rows=3482`, `split_non1=0`, `div_non1=3482`, `adj_non1=3482`, `profile=dividend_only`
- `ACIC` -> `year_files=6`, `rows=829`, `split_non1=0`, `div_non1=785`, `adj_non1=785`, `profile=dividend_only`
- `ACII` -> `year_files=4`, `rows=528`, `split_non1=0`, `div_non1=528`, `adj_non1=528`, `profile=dividend_only`
- `ACNB` -> `year_files=17`, `rows=3747`, `split_non1=0`, `div_non1=3741`, `adj_non1=3741`, `profile=dividend_only`
- `ACRE` -> `year_files=15`, `rows=3485`, `split_non1=0`, `div_non1=3485`, `adj_non1=3485`, `profile=dividend_only`
- `ACTG` -> `year_files=22`, `rows=5327`, `split_non1=0`, `div_non1=2729`, `adj_non1=2729`, `profile=dividend_only`
- `ACU` -> `year_files=22`, `rows=5202`, `split_non1=0`, `div_non1=5202`, `adj_non1=5202`, `profile=dividend_only`
- `ADAM` -> `year_files=9`, `rows=1663`, `split_non1=0`, `div_non1=1663`, `adj_non1=1663`, `profile=dividend_only`
- `ADES` -> `year_files=20`, `rows=4436`, `split_non1=0`, `div_non1=3442`, `adj_non1=3442`, `profile=dividend_only`
- `ADK` -> `year_files=12`, `rows=2634`, `split_non1=0`, `div_non1=2140`, `adj_non1=2140`, `profile=dividend_only`
- `ADTN` -> `year_files=22`, `rows=5327`, `split_non1=0`, `div_non1=4688`, `adj_non1=4688`, `profile=dividend_only`
- `AE` -> `year_files=21`, `rows=5042`, `split_non1=0`, `div_non1=5003`, `adj_non1=5003`, `profile=dividend_only`
- `AFBI` -> `year_files=6`, `rows=1228`, `split_non1=0`, `div_non1=991`, `adj_non1=991`, `profile=dividend_only`
- `AFCG` -> `year_files=6`, `rows=1247`, `split_non1=0`, `div_non1=1247`, `adj_non1=1247`, `profile=dividend_only`
- `AGC` -> `year_files=14`, `rows=3087`, `split_non1=0`, `div_non1=2825`, `adj_non1=2825`, `profile=dividend_only`
- `AGRO` -> `year_files=16`, `rows=3798`, `split_non1=0`, `div_non1=3713`, `adj_non1=3713`, `profile=dividend_only`
- `AIB` -> `year_files=16`, `rows=3162`, `split_non1=0`, `div_non1=2885`, `adj_non1=2885`, `profile=dividend_only`
- `AII` -> `year_files=5`, `rows=521`, `split_non1=0`, `div_non1=521`, `adj_non1=521`, `profile=dividend_only`
- `AIP` -> `year_files=13`, `rows=2346`, `split_non1=0`, `div_non1=295`, `adj_non1=295`, `profile=dividend_only`
- `AIRS` -> `year_files=6`, `rows=1091`, `split_non1=0`, `div_non1=206`, `adj_non1=206`, `profile=dividend_only`
- `ALCO` -> `year_files=22`, `rows=5327`, `split_non1=0`, `div_non1=5327`, `adj_non1=5327`, `profile=dividend_only`
- `ALIT` -> `year_files=6`, `rows=1173`, `split_non1=0`, `div_non1=1107`, `adj_non1=1107`, `profile=dividend_only`
- `ALRS` -> `year_files=8`, `rows=1627`, `split_non1=0`, `div_non1=1627`, `adj_non1=1627`, `profile=dividend_only`
- `ALSK` -> `year_files=17`, `rows=4167`, `split_non1=0`, `div_non1=3848`, `adj_non1=3848`, `profile=dividend_only`
- `ALTA` -> `year_files=2`, `rows=316`, `split_non1=0`, `div_non1=311`, `adj_non1=311`, `profile=dividend_only`
- `ALTG` -> `year_files=7`, `rows=1521`, `split_non1=0`, `div_non1=1318`, `adj_non1=1318`, `profile=dividend_only`
- `ALTS` -> `year_files=12`, `rows=2268`, `split_non1=0`, `div_non1=1835`, `adj_non1=1835`, `profile=dividend_only`
- `AMNB` -> `year_files=20`, `rows=4771`, `split_non1=0`, `div_non1=4742`, `adj_non1=4742`, `profile=dividend_only`
- `AMPS` -> `year_files=9`, `rows=1609`, `split_non1=0`, `div_non1=755`, `adj_non1=755`, `profile=dividend_only`
- `AMPY` -> `year_files=8`, `rows=1654`, `split_non1=0`, `div_non1=151`, `adj_non1=151`, `profile=dividend_only`
- `AMRB` -> `year_files=17`, `rows=3977`, `split_non1=0`, `div_non1=3968`, `adj_non1=3968`, `profile=dividend_only`
- `AMS` -> `year_files=22`, `rows=5127`, `split_non1=0`, `div_non1=618`, `adj_non1=618`, `profile=dividend_only`
- `AMSF` -> `year_files=22`, `rows=5104`, `split_non1=0`, `div_non1=5104`, `adj_non1=5104`, `profile=dividend_only`
- `AMTB` -> `year_files=9`, `rows=1845`, `split_non1=0`, `div_non1=1830`, `adj_non1=1830`, `profile=dividend_only`
- `AMWD` -> `year_files=22`, `rows=5327`, `split_non1=0`, `div_non1=1620`, `adj_non1=1620`, `profile=dividend_only`
- `ANH` -> `year_files=17`, `rows=4081`, `split_non1=0`, `div_non1=4075`, `adj_non1=4075`, `profile=dividend_only`
- `ANTX` -> `year_files=9`, `rows=1736`, `split_non1=0`, `div_non1=733`, `adj_non1=733`, `profile=dividend_only`
- `ANV` -> `year_files=10`, `rows=1994`, `split_non1=0`, `div_non1=1994`, `adj_non1=1994`, `profile=dividend_only`
- `AOMR` -> `year_files=6`, `rows=1185`, `split_non1=0`, `div_non1=1174`, `adj_non1=1174`, `profile=dividend_only`
- `AP` -> `year_files=22`, `rows=5324`, `split_non1=0`, `div_non1=3086`, `adj_non1=3086`, `profile=dividend_only`
- `APLP` -> `year_files=4`, `rows=623`, `split_non1=0`, `div_non1=568`, `adj_non1=568`, `profile=dividend_only`
- `APOG` -> `year_files=22`, `rows=5327`, `split_non1=0`, `div_non1=5304`, `adj_non1=5304`, `profile=dividend_only`
- `APSG` -> `year_files=10`, `rows=1912`, `split_non1=0`, `div_non1=1477`, `adj_non1=1477`, `profile=dividend_only`
- `APWC` -> `year_files=16`, `rows=3452`, `split_non1=0`, `div_non1=1646`, `adj_non1=1646`, `profile=dividend_only`
- `ARKO` -> `year_files=7`, `rows=1305`, `split_non1=0`, `div_non1=1305`, `adj_non1=1305`, `profile=dividend_only`
- `ARKR` -> `year_files=22`, `rows=5087`, `split_non1=0`, `div_non1=4683`, `adj_non1=4683`, `profile=dividend_only`
- `ARP` -> `year_files=16`, `rows=3344`, `split_non1=0`, `div_non1=3298`, `adj_non1=3298`, `profile=dividend_only`
- `ASC` -> `year_files=14`, `rows=3168`, `split_non1=0`, `div_non1=3162`, `adj_non1=3162`, `profile=dividend_only`
- `ASFI` -> `year_files=16`, `rows=3907`, `split_non1=0`, `div_non1=3295`, `adj_non1=3295`, `profile=dividend_only`
- `ASIX` -> `year_files=11`, `rows=2369`, `split_non1=0`, `div_non1=2369`, `adj_non1=2369`, `profile=dividend_only`
- `ASRV` -> `year_files=22`, `rows=5280`, `split_non1=0`, `div_non1=5256`, `adj_non1=5256`, `profile=dividend_only`
- `ASTL` -> `year_files=6`, `rows=1098`, `split_non1=0`, `div_non1=893`, `adj_non1=893`, `profile=dividend_only`
- `ATLCL` -> `year_files=6`, `rows=1069`, `split_non1=0`, `div_non1=1035`, `adj_non1=1035`, `profile=dividend_only`
- `ATLCZ` -> `year_files=3`, `rows=526`, `split_non1=0`, `div_non1=526`, `adj_non1=526`, `profile=dividend_only`
- `ATNI` -> `year_files=21`, `rows=4978`, `split_non1=0`, `div_non1=4978`, `adj_non1=4978`, `profile=dividend_only`
- `ATRI` -> `year_files=20`, `rows=4838`, `split_non1=0`, `div_non1=4792`, `adj_non1=4792`, `profile=dividend_only`
- `AUBN` -> `year_files=22`, `rows=4331`, `split_non1=0`, `div_non1=4331`, `adj_non1=4331`, `profile=dividend_only`
- `AUDC` -> `year_files=22`, `rows=5327`, `split_non1=0`, `div_non1=5316`, `adj_non1=5316`, `profile=dividend_only`
- `AUS` -> `year_files=4`, `rows=593`, `split_non1=0`, `div_non1=158`, `adj_non1=158`, `profile=dividend_only`
- `AWRE` -> `year_files=22`, `rows=5314`, `split_non1=0`, `div_non1=2398`, `adj_non1=2398`, `profile=dividend_only`
- `AXR` -> `year_files=22`, `rows=5093`, `split_non1=0`, `div_non1=631`, `adj_non1=631`, `profile=dividend_only`
- `BAFN` -> `year_files=6`, `rows=1006`, `split_non1=0`, `div_non1=814`, `adj_non1=814`, `profile=dividend_only`
- `BBCP` -> `year_files=9`, `rows=1819`, `split_non1=0`, `div_non1=1539`, `adj_non1=1539`, `profile=dividend_only`
- `BBI` -> `year_files=10`, `rows=2146`, `split_non1=0`, `div_non1=104`, `adj_non1=104`, `profile=dividend_only`
- `BBUC` -> `year_files=5`, `rows=998`, `split_non1=0`, `div_non1=931`, `adj_non1=931`, `profile=dividend_only`
- `BBW` -> `year_files=22`, `rows=5327`, `split_non1=0`, `div_non1=5327`, `adj_non1=5327`, `profile=dividend_only`
- `BCAL` -> `year_files=6`, `rows=955`, `split_non1=0`, `div_non1=955`, `adj_non1=955`, `profile=dividend_only`
- `BCBP` -> `year_files=22`, `rows=4741`, `split_non1=0`, `div_non1=4724`, `adj_non1=4724`, `profile=dividend_only`
- `BCIC` -> `year_files=2`, `rows=134`, `split_non1=0`, `div_non1=134`, `adj_non1=134`, `profile=dividend_only`
- `BCML` -> `year_files=9`, `rows=1970`, `split_non1=0`, `div_non1=1970`, `adj_non1=1970`, `profile=dividend_only`
- `BCRH` -> `year_files=8`, `rows=1609`, `split_non1=0`, `div_non1=1530`, `adj_non1=1530`, `profile=dividend_only`
- `BCSF` -> `year_files=9`, `rows=1834`, `split_non1=0`, `div_non1=1834`, `adj_non1=1834`, `profile=dividend_only`
- `BCTF` -> `year_files=10`, `rows=1497`, `split_non1=0`, `div_non1=997`, `adj_non1=997`, `profile=dividend_only`
- `BDGE` -> `year_files=14`, `rows=3144`, `split_non1=0`, `div_non1=18`, `adj_non1=18`, `profile=dividend_only`
- `BDL` -> `year_files=22`, `rows=4038`, `split_non1=0`, `div_non1=3898`, `adj_non1=3898`, `profile=dividend_only`
- `BDN` -> `year_files=22`, `rows=5327`, `split_non1=0`, `div_non1=5327`, `adj_non1=5327`, `profile=dividend_only`
- `BELFA` -> `year_files=22`, `rows=4537`, `split_non1=0`, `div_non1=4537`, `adj_non1=4537`, `profile=dividend_only`
- `BELFB` -> `year_files=22`, `rows=5327`, `split_non1=0`, `div_non1=5327`, `adj_non1=5327`, `profile=dividend_only`
- `BFIN` -> `year_files=21`, `rows=5163`, `split_non1=0`, `div_non1=5131`, `adj_non1=5131`, `profile=dividend_only`
- `BFS` -> `year_files=22`, `rows=5327`, `split_non1=0`, `div_non1=5327`, `adj_non1=5327`, `profile=dividend_only`
- `BFST` -> `year_files=9`, `rows=1985`, `split_non1=0`, `div_non1=1970`, `adj_non1=1970`, `profile=dividend_only`
- `BGFV` -> `year_files=21`, `rows=5095`, `split_non1=0`, `div_non1=4760`, `adj_non1=4760`, `profile=dividend_only`
- `BGS` -> `year_files=20`, `rows=4727`, `split_non1=0`, `div_non1=4727`, `adj_non1=4727`, `profile=dividend_only`
- `BGSF` -> `year_files=13`, `rows=2699`, `split_non1=0`, `div_non1=2591`, `adj_non1=2591`, `profile=dividend_only`
- `BHFAL` -> `year_files=9`, `rows=1878`, `split_non1=0`, `div_non1=1872`, `adj_non1=1872`, `profile=dividend_only`
- `BHFAM` -> `year_files=6`, `rows=1074`, `split_non1=0`, `div_non1=1074`, `adj_non1=1074`, `profile=dividend_only`
- `BHFAN` -> `year_files=7`, `rows=1326`, `split_non1=0`, `div_non1=1326`, `adj_non1=1326`, `profile=dividend_only`
- `BHFAO` -> `year_files=7`, `rows=1454`, `split_non1=0`, `div_non1=1454`, `adj_non1=1454`, `profile=dividend_only`
- `BHM` -> `year_files=8`, `rows=1365`, `split_non1=0`, `div_non1=1365`, `adj_non1=1365`, `profile=dividend_only`
- `BHR` -> `year_files=9`, `rows=1978`, `split_non1=0`, `div_non1=1933`, `adj_non1=1933`, `profile=dividend_only`
- `BIG` -> `year_files=19`, `rows=4543`, `split_non1=0`, `div_non1=4171`, `adj_non1=4171`, `profile=dividend_only`
- `BITE` -> `year_files=6`, `rows=926`, `split_non1=0`, `div_non1=268`, `adj_non1=268`, `profile=dividend_only`
- `BJRI` -> `year_files=22`, `rows=5327`, `split_non1=0`, `div_non1=3738`, `adj_non1=3738`, `profile=dividend_only`
- `BKEP` -> `year_files=12`, `rows=2833`, `split_non1=0`, `div_non1=2823`, `adj_non1=2823`, `profile=dividend_only`

## Muestra de tickers raw aun no materializados

- `sample_missing = ['ABHW', 'ABTW', 'ACCP', 'ACLL', 'ACTW', 'ACVW', 'ADNTW', 'ADTW', 'AFGL', 'AHLP', 'AHOW', 'AHPW', 'AIRTV', 'AIVW', 'ALCW', 'ALLEW', 'ALPX', 'ALVU', 'ALVW', 'ALZH', 'AMDI', 'AMFWW', 'AOLW', 'APTVW', 'ARMKW', 'ARPW', 'ASXW', 'AVE', 'AVI', 'AXLLW', 'BBCO', 'BBRX', 'BBUW', 'BDXW', 'BEER', 'BEPW', 'BFL', 'BHVNW', 'BIPW', 'BLUEV', 'BNKW', 'BNW', 'BPYW', 'BTRY', 'BTXW', 'BWAW', 'BWCW', 'BXLTW', 'CAGW', 'CBSOW']`
- `sample_missing_with_files = []`

La diferencia entre `raw_tickers` y `adjusted_tickers` se debe a directorios raw sin archivos `ticker-year`.
Para la unidad contractual de coverage (`ticker-year file`), no hay faltantes.

## Comparacion fisica de outputs

- `missing_outputs = 0`
- `extra_adjusted_outputs = 0`
- `missing_outputs_sample = []`
- `extra_adjusted_outputs_sample = []`

## Validacion contractual agregada

- `read_error_files = 0`
- `files_missing_required_columns = 0`
- `nonpositive_factor_rows = 0`
- `null_factor_rows = 0`
- `bad_price_view_rows = 0`
- `empty_source_daily_rows = 0`
- `missing_source_daily_file_rows = 0`
- `future_split_factor_min = 2.204585537918872e-14`
- `future_dividend_factor_min = 4.9557436997882835e-23`
- `future_adjustment_factor_min = 4.9557436997882835e-23`

## Lectura tecnica

La conclusion principal ya no es que falte expansion material.
La capa `daily_adjusted` ya esta bien defendida en semantica piloto y en consumidor inicial, y ahora tambien tiene cobertura fisica full-universe frente al daily raw observado.

Los numeros fuertes son estos:

- `12230` tickers con archivos ajustados frente a `12230` tickers raw con archivos;
- `125438` archivos anuales ajustados frente a `125438` archivos raw;
- cobertura actual de `100.0000%` por ticker con archivos y `100.0000%` por archivo anual;
- `missing_outputs = 0` y `extra_adjusted_outputs = 0`.
- `read_error_files = 0`, `files_missing_required_columns = 0`, `nonpositive_factor_rows = 0`.

Eso significa que la deuda de expansion fisica queda cerrada por coverage.

Dentro del universo materializado, la activacion sigue siendo inspeccionable por perfiles agregados:

- `neutral_control = 9816`;
- `split_only = 1210`;
- `dividend_only = 861`;
- `split_and_dividend = 343`.

Eso no sustituye las inspecciones semanticas caso por caso ya existentes, pero si actualiza la evidencia agregada de coverage.
Las validaciones agregadas de columnas obligatorias, legibilidad, factores positivos y provenance minimo tambien cierran sin incidencias.

## Veredicto

`daily_adjusted` no esta hoy en falta metodologica base.
La capa esta correctamente definida, consumida y materializada fisicamente a cobertura full-universe.
Este audit cierra la deuda de coverage material y las validaciones contractuales agregadas de la materializacion full-universe.
La promocion documental final queda reflejada en maturity, registry y changelog; por tanto la capa queda defendible como `Nivel 6 - Promovida`.
