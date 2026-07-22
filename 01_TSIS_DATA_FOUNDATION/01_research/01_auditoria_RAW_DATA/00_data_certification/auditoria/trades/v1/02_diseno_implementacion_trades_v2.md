## Diseño de implementación Agent02 v2 para Trades

### Objetivo

Traducir el contrato y la auditoría de `trades` a un diseño ejecutable para las cuatro piezas principales:

- `050_trades_v2_validate_file.py`
- `051_trades_v2_inventory.py`
- `052_trades_v2_validate_batches.py`
- `053_trades_v2_materialize_current.py`

El objetivo de este documento no es describir la teoría.
El objetivo es fijar:

- inputs
- outputs
- tablas
- claves
- reglas de materialización
- y orden de construcción

---

## 1. Arquitectura objetivo

La arquitectura objetivo de `trades` debe replicar la de `quotes v2`:

1. `051`
   - inventario físico exacto
2. `050`
   - validador unitario por file
3. `052`
   - validación batch append-only con `resume`
4. `053`
   - materialización `current/retry/live`

Agent03 queda fuera de esta primera implementación.
Primero se debe construir la verdad técnica de Agent02.

---

## 2. Fase 0: contrato del file observado

El file primario de trades es:

- `market.parquet`

Path observado:

- `D:\trades_ticks_prod_2005_2026\KZR\year=2021\month=04\day=2021-04-07\market.parquet`

Schema observado:

- `ticker: string`
- `date: string`
- `timestamp: timestamp[us]`
- `price: double`
- `size: int64`
- `exchange: int64`
- `conditions: list<int64>`
- `year: int64`
- `month: int64`
- `day: string`

Ese schema es el baseline del contrato.

---

## 3. `050_trades_v2_validate_file.py`

### 3.1. Rol

Validar exactamente un `market.parquet` y devolver un evento estructurado.

### 3.2. Inputs

- `file`
- `expected_root` opcional
- `run_id`
- `batch_id`
- `scan_reason`
- `validation_kind`
- thresholds opcionales de validación

### 3.3. Output obligatorio

- `file`
- `ticker`
- `date`
- `rows`
- `severity`
- `issues`
- `warns`
- `action`
- `metrics_json`
- `validator_version`
- `processed_at_utc`
- `run_id`
- `batch_id`
- `scan_reason`
- `validation_kind`

### 3.4. Checks mínimos

#### Física

- file existe
- size > 0
- parquet legible

#### Partición

- parsear:
  - ticker
  - year
  - month
  - day
- contrastar contra columnas del file

#### Schema

- columnas mínimas presentes
- tipos compatibles

#### Contenido

- rows > 0
- timestamp parseable
- price > 0
- size > 0
- timestamps dentro del día
- ticker constante
- date constante

#### Métricas base

- `price_min`
- `price_max`
- `size_sum`
- `size_max`
- `exchange_nunique`
- `duplicate_exact_trade_rows`
- `duplicate_exact_trade_ratio_pct`
- `off_session_trade_pct`
- `max_trades_same_timestamp`

#### Contexto de referencia opcional

- `ohlcv_1m`
- `ohlcv_daily`

### 3.5. Cross-checks con referencia

La primera versión debe soportar dos modos:

#### Modo A. Sin referencia externa

Valida solo contra:

- file
- path
- schema
- contenido interno

#### Modo B. Con referencia externa

Cruza con:

- `ohlcv_1m`
- `ohlcv_daily`

y añade a `metrics_json`:

- `ohlcv_1m_found`
- `ohlcv_daily_found`
- `trade_price_vs_1m_range_ok`
- `trade_price_vs_daily_range_ok`
- `trade_volume_vs_1m_ratio`
- `trade_volume_vs_daily_ratio`
- `trade_vwap`
- `trade_vwap_vs_daily_vw_diff_pct`

### 3.6. Política de severidad

#### HARD_FAIL

- corrupción física
- schema roto
- inconsistencias graves de partición
- precios o tamaños imposibles
- timestamps fuera del día
- incoherencia grave con referencia externa

#### SOFT_FAIL

- `dtype_mismatch`
- duplicados
- off-session notable
- referencia externa ausente
- desviaciones moderadas con `ohlcv_1m/daily`

#### PASS

- el file es estructural y económicamente defendible

---

## 4. `051_trades_v2_inventory.py`

### 4.1. Rol

Construir el inventario exacto de `market.parquet` en roots locales.

### 4.2. Inputs

- `--c-root`
  - esperado:
    - `C:\TSIS_Data\data\trades_ticks_prod_2005_2026`
- `--d-root`
  - esperado:
    - `D:\trades_ticks_prod_2005_2026`
- `--outdir`
- `--batch-size`
- `--resume`

### 4.3. Path esperado

- `{root}\{ticker}\year=YYYY\month=MM\day=YYYY-MM-DD\market.parquet`

### 4.4. Output incremental

Dentro del `outdir`:

- `inventory_batches\inventory_batch_000001.parquet`
- `inventory_batches\inventory_batch_000002.parquet`
- ...
- `inventory_checkpoint.json`
- `inventory_run_manifest.json`

### 4.5. Output final

- `trades_inventory_files.parquet`
- `trades_inventory_files.csv`
- `trades_inventory_by_ticker.parquet`
- `trades_inventory_by_ticker.csv`
- `trades_inventory_summary.json`

### 4.6. Columnas mínimas del inventario

- `root`
- `root_path`
- `file`
- `relpath`
- `ticker`
- `date`
- `year`
- `month`
- `day`
- `task_key`
- `size_bytes`
- `mtime_utc`
- `inventory_seen_utc`

### 4.7. Regla de resume

`051` debe:

- persistir por batches
- mantener checkpoint del último `relpath` persistido
- reanudar sobre el mismo `outdir`
- consolidar al final el inventario total

---

## 5. `052_trades_v2_validate_batches.py`

### 5.1. Rol

Leer `trades_inventory_files.parquet`, filtrar el universo objetivo, validar files en paralelo y persistir eventos append-only por batch.

### 5.2. Inputs

- `--inventory-parquet`
- `--outdir`
- `--run-id`
- `--workers`
- `--chunk-size`
- `--root`
- `--ticker`
- `--date-from`
- `--date-to`
- `--limit`
- `--scan-reason`
- `--validation-kind`
- `--resume`

### 5.3. Flujo

1. leer inventario
2. aplicar filtros
3. trocear en batches
4. para cada batch:
   - validar en paralelo usando `050`
   - escribir:
     - `events_batches/batch_000001.parquet`
5. actualizar:
   - `validation_checkpoint.json`
   - `validation_run_manifest.json`
6. regenerar:
   - `batch_manifest_trades_strict.csv`
   - `validation_run_summary.json`

### 5.4. Output incremental

- `events_batches\batch_*.parquet`
- `validation_checkpoint.json`
- `validation_run_manifest.json`

### 5.5. Output final

- `batch_manifest_trades_strict.csv`
- `batch_manifest_trades_strict.parquet`
- `validation_run_summary.json`

### 5.6. Regla de resume

`052` debe:

- detectar batches ya escritos
- no recalcular batches ya confirmados
- continuar desde el siguiente batch pendiente
- conservar coherencia del manifest y del checkpoint

---

## 6. `053_trades_v2_materialize_current.py`

### 6.1. Rol

Leer el log append-only de events y materializar:

- `trades_current`
- `retry_current`
- `retry_frozen`
- `live_status`

### 6.2. Inputs

- `--validation-outdir`
- `--inventory-parquet`
- `--outdir` opcional
- `--run-id`

### 6.3. Flujo

1. leer:
   - `validation_checkpoint.json`
   - `validation_run_manifest.json`
2. identificar batches confirmados
3. leer `events_batches/batch_*.parquet`
4. concatenar eventos válidos
5. derivar `current`
6. enriquecer `current` con inventario
7. derivar `retry_current`
8. derivar `retry_frozen`
9. escribir outputs contractuales

### 6.4. Output final

- `trades_current.parquet`
- `trades_current.csv`
- `retry_current.parquet`
- `retry_current.csv`
- `retry_frozen.parquet`
- `retry_frozen.csv`
- `trades_agent_strict_events_current.csv`
- `retry_queue_trades_strict_current.csv`
- `retry_frozen_trades_strict.csv`
- `live_status_trades_strict.json`
- `materialization_summary.json`

### 6.5. Materialización parcial o final

`053` debe soportar:

- `partial`
- `final`

según el estado del validate y los batches confirmados.

---

## 7. Convenciones de naming

### 7.1. run_id

Debe identificar lógicamente el objetivo del run.

Ejemplos:

- `trades_validate_q1_2024_d_smoke`
- `trades_validate_2005_2026_d_full`

### 7.2. outdir

Debe ser el identificador físico real del run.

Ejemplos:

- `...\trades_v2_inventory\trades_inventory_2005_2026`
- `...\trades_v2_validation\trades_validate_q1_2024_d_smoke`

La regla operativa es:

- mismo `outdir` + `--resume` = mismo run
- distinto `outdir` = run distinto

---

## 8. Dependencias externas de referencia

### 8.1. OHLCV daily

Path ejemplo:

- `D:\ohlcv_daily\ticker=AACQ\year=2021\day_aggs_AACQ_2021.parquet`

Uso:

- rango diario
- volumen diario
- `vw`

### 8.2. OHLCV 1m

Path ejemplo:

- `D:\ohlcv_1m\ticker=EMA\year=2026\month=03\minute_aggs_EMA_2026_03.parquet`

Uso:

- rango por minuto
- volumen por minuto
- intensidad de prints

### 8.3. Eventos corporativos

Uso futuro:

- splits
- ticker changes
- otros eventos

No es necesario para cerrar la primera versión del pipeline v2, pero sí para Agent03 y causalidad.

---

## 9. Orden recomendado de construcción

Orden correcto:

1. `050_trades_v2_validate_file.py`
2. `051_trades_v2_inventory.py`
3. `052_trades_v2_validate_batches.py`
4. `053_trades_v2_materialize_current.py`
5. smoke acotado
6. verificación de outputs
7. Agent03 Trades

Razón:

- primero hay que fijar qué significa un file válido
- luego inventariar
- luego persistir validación
- luego materializar current/retry/live

---

## 10. Smoke recomendado

Antes de ir a histórico completo:

- root `D`
- ventana temporal acotada
- límite pequeño o medio

Ejemplo:

- `--root D`
- `--date-from 2024-01-01`
- `--date-to 2024-03-31`
- `--limit 5000`

Objetivo:

- cerrar semántica
- revisar issues
- revisar métricas
- confirmar compatibilidad de outputs

---

## 11. Entregables mínimos para considerar v2 operable

Debe existir:

- inventario incremental reanudable
- validate batch reanudable
- materialize reejecutable
- contrato por file estable
- exports contractuales para Agent03

Debe quedar explícito:

- qué se considera `PASS`
- qué se considera `SOFT_FAIL`
- qué se considera `HARD_FAIL`
- cuándo se manda a `retry`
- cuándo se congela

---

## 12. En una frase

El pipeline v2 de `trades` debe ser un espejo arquitectónico de `quotes`, pero con validación centrada en:

- `price`
- `size`
- `timestamp`
- `exchange`
- `conditions`
- coherencia con `ohlcv_1m`
- coherencia con `ohlcv_daily`



---

 He cerrado el espejo trades v2 completo y lo he verificado con smoke real.

  Scripts creados:

  - C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/050_trades_v2_validate_file.py
  - C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/051_trades_v2_inventory.py
  - C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/052_trades_v2_validate_batches.py
  - C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/053_trades_v2_materialize_current.py

  Estado:

  - 050 validado contra un market.parquet real, cruzando con ohlcv_daily y ohlcv_1m.
  - 051 escribe inventory_batches, checkpoint, manifest y consolida trades_inventory_*.
  - 052 escribe events_batches, validation_checkpoint.json, validation_run_manifest.json, batch_manifest_trades_v2.*,
    validation_run_summary.json, con --resume.
  - 053 materializa trades_current.*, retry_current.*, retry_frozen.*, trades_agent_strict_events_current.csv,
    retry_queue_trades_strict_current.csv, live_status_trades_strict.json.

  Verificación hecha:

  - py_compile OK en 050/051/052/053
  - smoke de 051 OK
  - smoke de 052 OK
  - smoke de 053 OK

  En el smoke de 052, los 2 files salieron HARD_FAIL; eso no es fallo del pipeline, es el resultado real de esos samples
  acotados. 053 materializó bien y dejó materialization_mode = final.

  Siguiente paso útil: darte las tres lanzaderas de trades en el mismo formato que ya dejamos para quotes, primero con
  un smoke controlado y luego con el full.



# Lanzaderas Trades v2

1. Inventory 051

```sh
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\051_trades_v2_inventory.py `
   --c-root C:\TSIS_Data\data\trades_ticks_prod_2005_2026 `
   --d-root D:\trades_ticks_prod_2005_2026 `
   --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026 `
   --batch-size 100000 `
   --resume

python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\051_trades_v2_inventory.py --c-root C:\TSIS_Data\data\trades_ticks_prod_2005_2026 --d-root D:\trades_ticks_prod_2005_2026 --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026 --batch-size 100000 --resume
```

2. Validate 052

```sh
# smoke 2024
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\052_trades_v2_validate_batches.py
`
   --inventory-parquet C:
\TSIS_Data\v1\backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026\trades_inventory_files.p
arquet `
   --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_q1_2024_d_smoke `
   --run-id trades_validate_q1_2024_d_smoke `
   --workers 8 `
   --chunk-size 500 `
   --root D `
   --date-from 2024-01-01 `
   --date-to 2024-03-31 `
   --limit 5000 `
   --scan-reason rescan_all `
   --validation-kind normal_validation `
   --ohlcv-daily-root D:\ohlcv_daily `
   --ohlcv-1m-root D:\ohlcv_1m `
   --resume

python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\052_trades_v2_validate_batches.py --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026\trades_inventory_files.parquet --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_q1_2024_d_smoke --run-id trades_validate_q1_2024_d_smoke --workers 8 --chunk-size 500 --root D --date-from 2024-01-01 --date-to 2024-03-31 --limit 5000 --scan-reason rescan_all --validation-kind normal_validation --ohlcv-daily-root D:\ohlcv_daily --ohlcv-1m-root D:\ohlcv_1m --resume



# 2005-2026 full
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\052_trades_v2_validate_batches.py
`
   --inventory-parquet C:
\TSIS_Data\v1\backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026\trades_inventory_files.p
arquet `
   --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_2005_2026_d_full `
   --run-id trades_validate_2005_2026_d_full `
   --workers 8 `
   --chunk-size 500 `
   --root D `
   --date-from 2005-01-01 `
   --date-to 2026-03-31 `
   --scan-reason rescan_all `
   --validation-kind normal_validation `
   --ohlcv-daily-root D:\ohlcv_daily `
   --ohlcv-1m-root D:\ohlcv_1m `
   --resume

python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\052_trades_v2_validate_batches.py --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026\trades_inventory_files.parquet --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_2005_2026_d_full --run-id trades_validate_2005_2026_d_full --workers 8 --chunk-size 500 --root D --date-from 2005-01-01 --date-to 2026-03-31 --scan-reason rescan_all --validation-kind normal_validation --ohlcv-daily-root D:\ohlcv_daily --ohlcv-1m-root D:\ohlcv_1m --resume
```


3. Materialize 053


```sh
# materialize smoke 2024
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\053_trades_v2_materialize_current.py --validation-outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_q1_2024_d_smoke --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026\trades_inventory_files.parquet --run-id trades_validate_q1_2024_d_smoke

# materialize 2005-2026 full
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\053_trades_v2_materialize_current.py --validation-outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_2005_2026_d_full --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026\trades_inventory_files.parquet --run-id trades_validate_2005_2026_d_full
```

Orden recomendado:

1. lanzar 051
2. verificar trades_inventory_summary.json
3. lanzar 052 smoke
4. verificar validation_run_summary.json y batch_manifest_trades_v2.csv
5. lanzar 053 smoke
6. revisar live_status_trades_strict.json
7. escalar al full


## 1. lanzar 051

```sh
PS C:\Users\AlexJ> python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\051_trades_v2_inventory.py --c-root C:\TSIS_Data\data\trades_ticks_prod_2005_2026 --d-root D:\trades_ticks_prod_2005_2026 --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026 --batch-size 100000 --resume
scan_C: matched=100000
...
scan_D: matched=1200000
scan_D: files_seen=1205751 matched=1205751
=== SUMMARY ===
{
  "outdir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_inventory\\trades_inventory_2005_2026",
  "c_root": "C:\\TSIS_Data\\data\\trades_ticks_prod_2005_2026",
  "d_root": "D:\\trades_ticks_prod_2005_2026",
  "resume": true,
  "batch_size": 100000,
  "c_inventory": {
    "root": "C",
    "rows": 8429405,
    "task_keys": 8429405,
    "tickers": 4371,
    "date_min": "2005-01-03",
    "date_max": "2026-03-06",
    "total_bytes": 198491596015
  },
  "d_inventory": {
    "root": "D",
    "rows": 1205751,
    "task_keys": 1205751,
    "tickers": 932,
    "date_min": "2003-09-10",
    "date_max": "2026-03-13",
    "total_bytes": 43398430020
  },
  "all_rows": 9635156,
  "all_task_keys": 9635156,
  "all_tickers": 5023,
  "outputs": {
    "trades_inventory_files_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_inventory\\trades_inventory_2005_2026\\trades_inventory_files.parquet",
    "trades_inventory_files_csv": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_inventory\\trades_inventory_2005_2026\\trades_inventory_files.csv",
    "trades_inventory_by_ticker_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_inventory\\trades_inventory_2005_2026\\trades_inventory_by_ticker.parquet",
    "trades_inventory_by_ticker_csv": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_inventory\\trades_inventory_2005_2026\\trades_inventory_by_ticker.csv",
    "summary_json": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_inventory\\trades_inventory_2005_2026\\trades_inventory_summary.json",
    "checkpoint_json": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_inventory\\trades_inventory_2005_2026\\inventory_checkpoint.json",
    "manifest_json": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_inventory\\trades_inventory_2005_2026\\inventory_run_manifest.json",
    "inventory_batches_dir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_inventory\\trades_inventory_2005_2026\\inventory_batches"
  }
}
```

## 2. verificar `trades_inventory_summary.json`

Qué verificamos ahora del `051`:

```sh
- existencia de summary, checkpoint, manifest, parquet final y inventory_batches
- completed_roots = ["C","D"]
- manifest.finalized = true
- consistencia entre:
   - persisted_rows_total
   - all_rows
   - batch_files
   - parquet final
- recuento real de tickers
- columnas esperadas
- nulos en file/ticker/task_key
- rangos de fechas
- solape real entre tickers de C y D
- warning explícito si hay fechas anteriores a 2005
```

```sh
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\054_trades_v2_verify_inventory.py --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026 --out-json C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026\inventory_verification_report.json
```

El inventario queda verificado para pasar a 052.

Lo que ahora sí puedes afirmar con soporte técnico es:

```sh
- el run C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/trades_v2_inventory/trades_inventory_2005_2026 está
   consistente internamente
- el parquet final, el summary, el checkpoint, el manifest y los 98 batches cuadran entre sí
- el universo inventariado actual contiene:
   - 9635156 files
   - 5023 tickers únicos en C ∪ D
   - 4371 tickers en C
   - 932 tickers en D
   - 280 tickers solapados entre C y D

La única advertencia real que queda abierta es esta:

- en D hay fechas anteriores a 2005
- el inventario las detecta correctamente
- no rompe la consistencia del run
- pero sí obliga a corregir la narrativa del dataset:
   - no es estrictamente 2005-2026
   - físicamente contiene al menos desde 2003-09-10

Conclusión operativa:

- 051 está cerrado
- ya puedes lanzar 052 smoke con seguridad razonable
```

## 3. lanzar 052 smoke

```sh
PS C:\Users\AlexJ> python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\052_trades_v2_validate_batches.py --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026\trades_inventory_files.parquet --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_q1_2024_d_smoke --run-id trades_validate_q1_2024_d_smoke --workers 8 --chunk-size 500 --root D --date-from 2024-01-01 --date-to 2024-03-31 --limit 5000 --scan-reason rescan_all --validation-kind normal_validation --ohlcv-daily-root D:\ohlcv_daily --ohlcv-1m-root D:\ohlcv_1m --resume
[1/10] batch_000001 files=500 events=500 counts={'SOFT_FAIL': 383, 'HARD_FAIL': 113, 'PASS': 4}
[2/10] batch_000002 files=500 events=500 counts={'SOFT_FAIL': 347, 'HARD_FAIL': 153}
[3/10] batch_000003 files=500 events=500 counts={'SOFT_FAIL': 300, 'HARD_FAIL': 198, 'PASS': 2}
[4/10] batch_000004 files=500 events=500 counts={'SOFT_FAIL': 281, 'HARD_FAIL': 217, 'PASS': 2}
[5/10] batch_000005 files=500 events=500 counts={'SOFT_FAIL': 273, 'HARD_FAIL': 227}
[6/10] batch_000006 files=500 events=500 counts={'SOFT_FAIL': 322, 'HARD_FAIL': 174, 'PASS': 4}
[7/10] batch_000007 files=500 events=500 counts={'SOFT_FAIL': 381, 'HARD_FAIL': 118, 'PASS': 1}
[8/10] batch_000008 files=500 events=500 counts={'SOFT_FAIL': 412, 'HARD_FAIL': 80, 'PASS': 8}
[9/10] batch_000009 files=500 events=500 counts={'HARD_FAIL': 323, 'SOFT_FAIL': 172, 'PASS': 5}
[10/10] batch_000010 files=500 events=500 counts={'SOFT_FAIL': 312, 'HARD_FAIL': 186, 'PASS': 2}
{
  "run_id": "trades_validate_q1_2024_d_smoke",
  "validator_version": "trades_v2_validate_file/0.1.0",
  "started_at_utc": "2026-04-01T16:29:07.910344+00:00",
  "finished_at_utc": "2026-04-01T16:31:33.363116+00:00",
  "inventory_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_inventory\\trades_inventory_2005_2026\\trades_inventory_files.parquet",
  "outdir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_validation\\trades_validate_q1_2024_d_smoke",
  "selected_files": 5000,
  "workers": 8,
  "chunk_size": 500,
  "batches_written": 10,
  "severity_counts_total": {
    "SOFT_FAIL": 3183,
    "HARD_FAIL": 1789,
    "PASS": 28
  },
  "filters": {
    "root": "D",
    "ticker": "",
    "date_from": "2024-01-01",
    "date_to": "2024-03-31",
    "limit": 5000
  },
  "ohlcv_daily_root": "D:\\ohlcv_daily",
  "ohlcv_1m_root": "D:\\ohlcv_1m",
  "resume": true
}
```

## 5. lanzar 053 smoke

```sh
PS C:\Users\AlexJ> python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\053_trades_v2_materialize_current.py --validation-outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_q1_2024_d_smoke --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026\trades_inventory_files.parquet --run-id trades_validate_q1_2024_d_smoke
{
  "run_id": "trades_validate_q1_2024_d_smoke",
  "materialized_at_utc": "2026-04-01T16:37:16.574888+00:00",
  "validation_outdir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_validation\\trades_validate_q1_2024_d_smoke",
  "inventory_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_inventory\\trades_inventory_2005_2026\\trades_inventory_files.parquet",
  "outdir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_validation\\trades_validate_q1_2024_d_smoke",
  "events_rows": 5000,
  "current_rows": 5000,
  "retry_current_rows": 4972,
  "retry_frozen_rows": 0,
  "batches_read": 10,
  "batches_read_names": [
    "batch_000001.parquet",
    "batch_000002.parquet",
    "batch_000003.parquet",
    "batch_000004.parquet",
    "batch_000005.parquet",
    "batch_000006.parquet",
    "batch_000007.parquet",
    "batch_000008.parquet",
    "batch_000009.parquet",
    "batch_000010.parquet"
  ],
  "batches_skipped_names": [],
  "materialization_mode": "final",
  "validation_completion_status": "completed",
  "validation_checkpoint_source": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_validation\\trades_validate_q1_2024_d_smoke\\validation_checkpoint.json",
  "validation_manifest_source": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_validation\\trades_validate_q1_2024_d_smoke\\validation_run_manifest.json"
}
```

## Notebook para revisar 052 y 053 visualmente `03_trades_root_cause_audit_notebook.ipynb`

```sh
C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/
trades/03_trades_root_cause_audit_notebook.ipynb

pensado para cubrir:

- validation_run_summary.json
- batch_manifest vía events_batches
- live_status_trades_strict.json
- causas exactas de HARD_FAIL
- warnings dominantes
- concentración por batch
- concentración por fecha
- concentración por ticker
- ejemplos concretos por ticker,date,file
- problema de escala corporativa
- duplicados
- desalineación trade_vwap vs daily_vw / 1m_vw
```

# RESULTADOS NOTEBOOK

## Nota De Cambio De Contrato: `trade_price_outside_daily_range`

### Regla que cambia

Hasta `050_trades_v2_validate_file.py` `v0.1.0`, la regla era:

- si un `market.parquet` cae en `trade_price_outside_daily_range`
- entonces el file se clasifica como `HARD_FAIL`
- salvo algunos casos ya degradados por heurística de `possible_corporate_action_scale_mismatch`

La propuesta de cambio es:

- `trade_price_outside_daily_range` deja de ser `HARD_FAIL` automatico
- primero debe clasificarse en subtipos
- los casos con desalineacion consistente de escala pasan a `SOFT_FAIL`
- `HARD_FAIL` queda reservado para:
   - ruptura de rango sin explicacion de escala
   - o combinado con senales estructurales adicionales

### Por qué cambia

El smoke `trades_validate_q1_2024_d_smoke` mostró que:

- `1789` files quedaron como `HARD_FAIL`
- `1786` de esos `1789` se explican por una sola regla:
   - `trade_price_outside_daily_range`

Eso indica que el validador no esta detectando “muchos tipos de corrupcion”.
Indica que una unica regla esta dominando el resultado del smoke.

La auditoria visual y cuantitativa posterior mostró que una parte relevante de esos casos no parece corrupcion interna de
`market.parquet`, sino desalineacion entre:

- `trades`
- `ohlcv_daily`
- `ohlcv_1m`

En varios ejemplos, `daily` y `1m` estan alineados entre si, mientras que `trades` aparece en otra escala estable.

![](../trades/img/06.png)  
![](../trades/img/07.png)  


## Evidencia visual que lo justificó

### Caso forense representativo

![](../trades/img/02.png)

En el caso `AQMS 2024-03-21` se observó:

- `trades` alrededor de `0.48`
- `ohlcv_daily` alrededor de `96`
- `ohlcv_1m` alrededor de `96`
- `outside_daily_pct = 100%`

Métricas observadas:

- `possible_price_scale_factor_vs_daily ≈ 0.0050`
- `possible_price_scale_factor_vs_1m ≈ 0.0050`
- `trade_volume_vs_daily_ratio ≈ 206`
- `trade_volume_vs_1m_ratio ≈ 210`

Eso muestra un patrón compatible con:

- fuerte desalineacion de escala
- precio dividido aproximadamente por `200`
- volumen multiplicado aproximadamente por `200`

La figura forense mostró:

- `trades` coherentes entre sí en una banda baja
- `daily` y `1m` coherentes entre sí en una banda alta
- incompatibilidad de escala entre ambos bloques
- no un pequeño escape marginal del rango

### Evidencia agregada del smoke

La clasificación agregada de `trade_price_outside_daily_range` mostró tres poblaciones:

- `scale_mismatch_strong`
- `true_outside_range_without_scale_shift`
- `other_reference_break`

![](../trades/img/02.png)

La revisión posterior del bucket `other_reference_break` mostró que gran parte de ese grupo seguía alineado en diagonales de:

- `possible_price_scale_factor_vs_daily` vs `possible_price_scale_factor_vs_1m`
- `trade_volume_vs_daily_ratio` vs `trade_volume_vs_1m_ratio`

![](../trades/img/04.png)
![](../trades/img/05.png)
![](../trades/img/00.png)
![](../trades/img/01.png)

Eso sugiere que el clasificador actual infra-detecta casos de escalado y los deja indebidamente en buckets no explicados.

En particular, el subtipo dominante `mixed_other_break` presentó medianas como:

- `median_pf_daily ≈ 0.0125`
- `median_pf_1m ≈ 0.0125`
- `median_vol_daily ≈ 79.9`
- `median_vol_1m ≈ 87.7`

Eso es consistente con una desalineacion sistematica de escala, no con ruido aleatorio.

### Impacto esperado sobre severidades

El impacto esperado del cambio es:

- reducir materialmente el número de `HARD_FAIL`
- aumentar el número de `SOFT_FAIL`
- mantener `PASS` aproximadamente estable
- concentrar los `HARD_FAIL` en casos realmente estructurales

Esperado en términos cualitativos:

- casos con mismatch de escala:
   - `HARD_FAIL -> SOFT_FAIL`
- casos de rango roto en la misma escala:
   - permanecen como `HARD_FAIL`
- casos con schema roto, timestamps fuera de día, precios/tamaños imposibles:
   - permanecen como `HARD_FAIL`

### Principio de implementación

La nueva lógica no debe depender de una lista cerrada de factores como:

- `1/10`
- `1/20`
- `1/200`

Debe detectar escalado probable por coherencia conjunta entre:

- `possible_price_scale_factor_vs_daily`
- `possible_price_scale_factor_vs_1m`
- `trade_volume_vs_daily_ratio`
- `trade_volume_vs_1m_ratio`

Criterio conceptual:

- si `daily` y `1m` apuntan al mismo factor de escala
- y el volumen acompaña razonablemente el inverso esperado
- entonces el caso debe reclasificarse como `scale_mismatch_*`
- y degradarse a `SOFT_FAIL`

### Trazabilidad y reproducibilidad

Este cambio no invalida la evidencia previa.

Para preservar reproducibilidad:

- el smoke actual queda congelado como baseline
- el cambio se hará con nueva `validator_version`
- el nuevo run se ejecutará en un `outdir` distinto
- el notebook podrá comparar:
   - baseline `v0.1.0`
   - nuevo run `v0.2.0`

Así, la evidencia queda separada en:

- comportamiento del contrato anterior
- evidencia visual que justifica el cambio
- comportamiento del contrato nuevo


# v020

He creado una línea paralela versionada sin tocar la baseline:

- C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/050_trades_v2_validate_file_v020.py
- C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/051_trades_v2_inventory_v020.py
- C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/052_trades_v2_validate_batches_v020.py
- C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/053_trades_v2_materialize_current_v020.py
- C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/054_trades_v2_verify_inventory_v020.py

Además:

- 050_v020 ya lleva VALIDATOR_VERSION = trades_v2_validate_file/0.2.0
- 052_v020 ya apunta a 050_trades_v2_validate_file_v020.py
- la baseline actual no se ha tocado
- py_compile pasó en 050/052/053 v020

La siguiente acción correcta es modificar solo C:/TSIS_Data/02_backtest_SmallCaps/notebooks/
cell_code/00_data_certification/050_trades_v2_validate_file_v020.py para relajar la regla de trade_price_outside_daily_range
usando una detección de escala más robusta. Luego correremos un smoke nuevo con 052_v020 en un outdir nuevo, por ejemplo:

- trades_validate_q1_2024_d_smoke_v020

He cambiado solo C:/TSIS_Data/02_backtest_SmallCaps/notebooks/
cell_code/00_data_certification/050_trades_v2_validate_file_v020.py y la baseline sigue intacta. py_compile pasó y C:/TSIS_Data/
v1/backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/052_trades_v2_validate_batches_v020.py sigue apuntando al
validador v020.

Qué cambia en v020: trade_price_outside_daily_range ya no usa la heurística fija 0.1/10.0. Ahora detecta mismatch de escala por
coherencia entre possible_price_scale_factor_vs_daily, possible_price_scale_factor_vs_1m, trade_volume_vs_daily_ratio y
trade_volume_vs_1m_ratio, y deja trazado en metrics_json:

- scale_mismatch_confidence
- scale_mismatch_detected

Lanza el smoke paralelo así:

```sh
PS C:\Users\AlexJ> python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\052_trades_v2_validate_batches_v020.py --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026\trades_inventory_files.parquet --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_q1_2024_d_smoke_v020 --run-id trades_validate_q1_2024_d_smoke_v020 --workers 8 --chunk-size 500 --root D --date-from 2024-01-01 --date-to 2024-03-31 --limit 5000 --scan-reason rescan_all --validation-kind normal_validation --ohlcv-daily-root D:\ohlcv_daily --ohlcv-1m-root D:\ohlcv_1m --resume
[1/10] batch_000001 files=500 events=500 counts={'SOFT_FAIL': 444, 'HARD_FAIL': 52, 'PASS': 4}
[2/10] batch_000002 files=500 events=500 counts={'SOFT_FAIL': 432, 'HARD_FAIL': 68}
[3/10] batch_000003 files=500 events=500 counts={'SOFT_FAIL': 451, 'HARD_FAIL': 47, 'PASS': 2}
[4/10] batch_000004 files=500 events=500 counts={'SOFT_FAIL': 449, 'HARD_FAIL': 49, 'PASS': 2}
[5/10] batch_000005 files=500 events=500 counts={'SOFT_FAIL': 469, 'HARD_FAIL': 31}
[6/10] batch_000006 files=500 events=500 counts={'SOFT_FAIL': 444, 'HARD_FAIL': 52, 'PASS': 4}
[7/10] batch_000007 files=500 events=500 counts={'SOFT_FAIL': 383, 'HARD_FAIL': 116, 'PASS': 1}
[8/10] batch_000008 files=500 events=500 counts={'SOFT_FAIL': 416, 'HARD_FAIL': 76, 'PASS': 8}
[9/10] batch_000009 files=500 events=500 counts={'SOFT_FAIL': 351, 'HARD_FAIL': 144, 'PASS': 5}
[10/10] batch_000010 files=500 events=500 counts={'SOFT_FAIL': 424, 'HARD_FAIL': 74, 'PASS': 2}
{
  "run_id": "trades_validate_q1_2024_d_smoke_v020",
  "validator_version": "trades_v2_validate_file/0.2.0",
  "started_at_utc": "2026-04-02T08:18:24.290641+00:00",
  "finished_at_utc": "2026-04-02T08:19:38.011737+00:00",
  "inventory_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_inventory\\trades_inventory_2005_2026\\trades_inventory_files.parquet",
  "outdir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_validation\\trades_validate_q1_2024_d_smoke_v020",
  "selected_files": 5000,
  "workers": 8,
  "chunk_size": 500,
  "batches_written": 10,
  "severity_counts_total": {
    "SOFT_FAIL": 4263,
    "HARD_FAIL": 709,
    "PASS": 28
  },
  "filters": {
    "root": "D",
    "ticker": "",
    "date_from": "2024-01-01",
    "date_to": "2024-03-31",
    "limit": 5000
  },
  "ohlcv_daily_root": "D:\\ohlcv_daily",
  "ohlcv_1m_root": "D:\\ohlcv_1m",
  "resume": true
}
```

Y después materializa con:

```sh
PS C:\Users\AlexJ> python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\053_trades_v2_materialize_current_v020.py --validation-outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_q1_2024_d_smoke_v020 --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026\trades_inventory_files.parquet --run-id trades_validate_q1_2024_d_smoke_v020
{
  "run_id": "trades_validate_q1_2024_d_smoke_v020",
  "materialized_at_utc": "2026-04-02T08:25:34.995197+00:00",
  "validation_outdir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_validation\\trades_validate_q1_2024_d_smoke_v020",
  "inventory_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_inventory\\trades_inventory_2005_2026\\trades_inventory_files.parquet",
  "outdir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_validation\\trades_validate_q1_2024_d_smoke_v020",
  "events_rows": 5000,
  "current_rows": 5000,
  "retry_current_rows": 4972,
  "retry_frozen_rows": 0,
  "batches_read": 10,
  "batches_read_names": [
    "batch_000001.parquet",
    "batch_000002.parquet",
    "batch_000003.parquet",
    "batch_000004.parquet",
    "batch_000005.parquet",
    "batch_000006.parquet",
    "batch_000007.parquet",
    "batch_000008.parquet",
    "batch_000009.parquet",
    "batch_000010.parquet"
  ],
  "batches_skipped_names": [],
  "materialization_mode": "final",
  "validation_completion_status": "completed",
  "validation_checkpoint_source": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_validation\\trades_validate_q1_2024_d_smoke_v020\\validation_checkpoint.json",
  "validation_manifest_source": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_validation\\trades_validate_q1_2024_d_smoke_v020\\validation_run_manifest.json"
}
```

## Notebook para revisar 052 y 053 visualmente `03_trades_root_cause_audit_notebook.ipynb`

Lectura operativa

v020 ha hecho bien su trabajo:

- ha sacado del HARD_FAIL gran parte de los falsos duros por escala
- y ha dejado concentrado el residuo “real”

Ese residuo parece ser, sobre todo:

1. same_scale_true_range_break

- trades y referencias están en la misma escala
- pero los trades siguen fuera de rango
- aquí el siguiente trabajo es afinar qué significa “fuera de rango”:
   - tolerancia
   - sesión
   - calidad de daily
   - calidad de 1m
   - prints raros pero legítimos

2. same_scale_session_break

- aquí probablemente el problema es de ventana de sesión
- daily/1m y trades pueden no estar representando exactamente el mismo universo horario

![](../trades/img/08.png)
![](../trades/img/09.png)
![](../trades/img/10.png)
![](../trades/img/11.png)

La lectura de estas salidas es:

- v020 ha funcionado
- el problema principal de escalado está bastante limpiado
- los 709 HARD_FAIL restantes parecen mayoritariamente casos de rango real en la misma escala
- el siguiente refinado debe centrarse en:
   - sesión
   - tolerancias de rango
   - combinación daily + 1m, no en escala

![](../trades/img/12(1).png)
![](../trades/img/12(2).png)
![](../trades/img/12(3).png)
![](../trades/img/12(4).png)
![](../trades/img/12(5).png)
![](../trades/img/12(6).png)

**El hallazgo dominante en estas imagenes es otro:**

- casi todos los casos son breaks_daily_only
- y además la mayoría son large_gap_gt20pct

Eso cambia el orden de prioridad.

Lo que dicen exactamente los gráficos

1. Sesión

- mixed_session, RTH_with_some_extended y mostly_RTH están bastante repartidos.
- No hay una concentración brutal en extended hours.
- Por tanto, la sesión explica parte del fenómeno, pero no parece la causa dominante.

2. Daily-only vs Daily+1m

- aplastante mayoría: breaks_daily_only
- muy pocos: breaks_daily_and_1m

Esto es lo más importante de todo.

Interpretación:

- el file rompe daily
- pero en la mayoría de casos no rompe 1m
- así que daily está pesando demasiado como criterio duro

3. Magnitud del gap

- la mayoría cae en large_gap_gt20pct
- luego una bolsa menor en medium_gap_5_20pct
- casi no hay gaps pequeños

Esto quiere decir:

- no estamos frente a microescapes tipo tolerancia 0.2%
- los casos que sobreviven son desviaciones grandes respecto a daily

Pero como a la vez son daily_only, eso sugiere:

- no es que el trade esté apenas fuera
- es que daily puede no ser la referencia correcta/completa para ese file
- mientras que 1m no lo contradice

4. Boxplots

- la magnitud del gap es bastante parecida entre breaks_daily_only y breaks_daily_and_1m
- por sesión también es parecida

Eso refuerza:

- ni la sesión ni el tamaño del gap separan el fenómeno principal
- la separación importante es qué referencia lo confirma
   - solo daily
   - o daily + 1m

Qué implica para la siguiente regla

Yo haría exactamente esto:

1. trade_price_outside_daily_range deja de ser HARD_FAIL si:

- escala ~1
- y no rompe 1m

Eso debería pasar a SOFT_FAIL, con algo como:

- daily_only_range_break_same_scale

2. mantener HARD_FAIL cuando:

- rompe daily
- y también rompe 1m

Eso sí parece una rotura más sólida.

3. la sesión la usaría como refinador secundario, no como regla principal:

- si off_session_trade_pct es alto, añadir warning contextual
- pero no decidir la dureza solo con eso

4. la magnitud del gap la usaría como segundo eje:

- daily_only + gap pequeño/medio claramente bajar
- daily_only + gap grande probablemente también bajar a SOFT_FAIL, visto que 1m no acompaña
- daily+1m + gap grande mantener duro



# v030

## Nota De Cambio De Contrato: `trade_price_outside_daily_range` en misma escala

### Hallazgo nuevo tras `v0.2.0`

La versión `trades_v2_validate_file/0.2.0` redujo los `HARD_FAIL` de:

- `1789` a `709`

sin cambiar el número de `PASS`.

Eso confirmó que una parte importante de los `HARD_FAIL` del baseline estaba inflada por desalineaciones de escala entre:

- `market.parquet`
- `ohlcv_daily`
- `ohlcv_1m`

Tras limpiar esa capa, el residuo duro quedó mucho más concentrado y permitió analizar mejor la naturaleza real de los casos
restantes.

### Qué muestran los `709 HARD_FAIL` restantes

La auditoría de `v0.2.0` mostró que los `HARD_FAIL` residuales siguen dominados casi por completo por:

- `trade_price_outside_daily_range`

Sin embargo, al abrir el subtipo dominante `same_scale_true_range_break`, aparecieron tres hechos clave:

#### 1. La mayoría rompe solo `daily`, no `1m`

La descomposición mostró que dentro de `same_scale_true_range_break` domina claramente:

- `breaks_daily_only`

mientras que:

- `breaks_daily_and_1m`

es minoritario.

Interpretación:
- en la mayoría de los casos, `daily` marca rotura
- pero `1m` no confirma esa rotura

Eso indica que `ohlcv_daily` por sí sola está pesando demasiado como criterio duro.

#### 2. La mayoría de gaps son grandes

La distribución por magnitud mostró que domina:

- `large_gap_gt20pct`

seguido por:
- `medium_gap_5_20pct`

y casi no existen:
- gaps pequeños

Interpretación:
- no se trata de pequeñas salidas por tolerancia
- se trata de discrepancias grandes frente a `daily`
- pero aun así, en la mayoría de los casos `1m` no acompaña la rotura

Eso refuerza que el problema principal no es “subir tolerancia porcentual sin más”, sino rebalancear qué referencia manda.

#### 3. La sesión no es la causa dominante

La distribución por sesión mostró presencia relevante en:

- `mostly_RTH`
- `RTH_with_some_extended`
- `mixed_session`

sin una concentración aplastante en extended hours.

Interpretación:
- la sesión aporta contexto
- pero no explica por sí sola el grueso del residuo duro

### Cambio propuesto para la siguiente iteración

La siguiente iteración no debe seguir afinando escala.
Debe cambiar la lógica de severidad para los casos con escala aproximadamente unitaria.

#### Regla nueva propuesta

En casos donde:

- `possible_price_scale_factor_vs_daily ≈ 1`
- `possible_price_scale_factor_vs_1m ≈ 1`

la severidad debe depender de si la rotura está confirmada por `1m`:

##### Caso A: rompe `daily` pero no rompe `1m`
- degradar de `HARD_FAIL` a `SOFT_FAIL`
- nuevo warning sugerido:
   - `daily_only_range_break_same_scale`

Interpretación:
- `daily` sola no basta para declarar rotura dura

##### Caso B: rompe `daily` y también rompe `1m`
- mantener `HARD_FAIL`
- nuevo issue sugerido:
   - `trade_price_outside_daily_and_1m_range`

Interpretación:
- la rotura queda confirmada por dos referencias
- es un candidato mucho más sólido a dureza real

### Papel de la sesión en la nueva lógica

La sesión debe quedar como refinador secundario, no como regla principal.

Uso sugerido:
- si `off_session_trade_pct` es alto:
   - añadir warning contextual
   - por ejemplo `extended_hours_context`
- pero no endurecer o relajar automáticamente solo por sesión

### Papel de la magnitud del gap

La magnitud del gap debe seguir registrándose y analizándose, pero no decidir por sí sola la severidad.

Uso sugerido:
- gap pequeño o medio:
   - refuerza degradación cuando solo rompe `daily`
- gap grande:
   - solo debe seguir duro si además rompe `1m`

### Impacto esperado sobre severidades

Se espera que esta iteración:

- reduzca todavía más los `HARD_FAIL`
- aumente los `SOFT_FAIL`
- mantenga `PASS` estable
- concentre los `HARD_FAIL` en los casos mejor confirmados por referencias múltiples

### Principio técnico de la siguiente versión

La regla debe priorizar la jerarquía de confirmación:

1. `1m` como confirmación intradía fuerte
2. `daily` como referencia contextual más gruesa
3. sesión como contexto adicional
4. magnitud del gap como cuantificador, no como único decisor

### Trazabilidad y reproducibilidad

Este cambio debe implementarse en una nueva línea paralela versionada, sin tocar:

- baseline `v0.1.0`
- iteración `v0.2.0`
- runs ya ejecutados

La comparación reproducible debe mantenerse entre:

- baseline original
- versión con limpieza de escala
- versión con rebalanceo `daily` vs `1m`


## ejecutamos v030

He creado y ajustado:

- C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/050_trades_v2_validate_file_v030.py
- C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/051_trades_v2_inventory_v030.py
- C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/052_trades_v2_validate_batches_v030.py
- C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/053_trades_v2_materialize_current_v030.py
- C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/054_trades_v2_verify_inventory_v030.py

Qué cambia en v030:

- VALIDATOR_VERSION = trades_v2_validate_file/0.3.0
- si same_scale_context y rompe daily pero no 1m:
   - baja a warning daily_only_range_break_same_scale
- si same_scale_context y rompe daily y 1m:
   - issue nuevo trade_price_outside_daily_and_1m_range
- deja métricas nuevas:
   - outside_daily_detected
   - outside_1m_detected
   - same_scale_context

py_compile pasó y 052_v030 ya apunta al validador v030.

Lanza el smoke paralelo así:

```sh
PS C:\Users\AlexJ> python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\052_trades_v2_validate_batches_v030.py --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026\trades_inventory_files.parquet --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_q1_2024_d_smoke_v030 --run-id trades_validate_q1_2024_d_smoke_v030 --workers 8 --chunk-size 500 --root D --date-from 2024-01-01 --date-to 2024-03-31 --limit 5000 --scan-reason rescan_all --validation-kind normal_validation --ohlcv-daily-root D:\ohlcv_daily --ohlcv-1m-root D:\ohlcv_1m --resume
[1/10] batch_000001 files=500 events=500 counts={'SOFT_FAIL': 453, 'HARD_FAIL': 43, 'PASS': 4}
[2/10] batch_000002 files=500 events=500 counts={'SOFT_FAIL': 436, 'HARD_FAIL': 64}
[3/10] batch_000003 files=500 events=500 counts={'SOFT_FAIL': 458, 'HARD_FAIL': 40, 'PASS': 2}
[4/10] batch_000004 files=500 events=500 counts={'SOFT_FAIL': 451, 'HARD_FAIL': 47, 'PASS': 2}
[5/10] batch_000005 files=500 events=500 counts={'SOFT_FAIL': 476, 'HARD_FAIL': 24}
[6/10] batch_000006 files=500 events=500 counts={'SOFT_FAIL': 448, 'HARD_FAIL': 48, 'PASS': 4}
[7/10] batch_000007 files=500 events=500 counts={'SOFT_FAIL': 388, 'HARD_FAIL': 111, 'PASS': 1}
[8/10] batch_000008 files=500 events=500 counts={'SOFT_FAIL': 420, 'HARD_FAIL': 72, 'PASS': 8}
[9/10] batch_000009 files=500 events=500 counts={'SOFT_FAIL': 356, 'HARD_FAIL': 139, 'PASS': 5}
[10/10] batch_000010 files=500 events=500 counts={'SOFT_FAIL': 429, 'HARD_FAIL': 69, 'PASS': 2}
{
  "run_id": "trades_validate_q1_2024_d_smoke_v030",
  "validator_version": "trades_v2_validate_file/0.3.0",
  "started_at_utc": "2026-04-02T09:15:47.297492+00:00",
  "finished_at_utc": "2026-04-02T09:16:11.507564+00:00",
  "inventory_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_inventory\\trades_inventory_2005_2026\\trades_inventory_files.parquet",
  "outdir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_validation\\trades_validate_q1_2024_d_smoke_v030",
  "selected_files": 5000,
  "workers": 8,
  "chunk_size": 500,
  "batches_written": 10,
  "severity_counts_total": {
    "SOFT_FAIL": 4315,
    "HARD_FAIL": 657,
    "PASS": 28
  },
  "filters": {
    "root": "D",
    "ticker": "",
    "date_from": "2024-01-01",
    "date_to": "2024-03-31",
    "limit": 5000
  },
  "ohlcv_daily_root": "D:\\ohlcv_daily",
  "ohlcv_1m_root": "D:\\ohlcv_1m",
  "resume": true
}
```
Y después:

```sh
PS C:\Users\AlexJ> python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\053_trades_v2_materialize_current_v030.py --validation-outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_q1_2024_d_smoke_v030 --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026\trades_inventory_files.parquet --run-id trades_validate_q1_2024_d_smoke_v030
{
  "run_id": "trades_validate_q1_2024_d_smoke_v030",
  "materialized_at_utc": "2026-04-02T09:20:31.062912+00:00",
  "validation_outdir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_validation\\trades_validate_q1_2024_d_smoke_v030",
  "inventory_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_inventory\\trades_inventory_2005_2026\\trades_inventory_files.parquet",
  "outdir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_validation\\trades_validate_q1_2024_d_smoke_v030",
  "events_rows": 5000,
  "current_rows": 5000,
  "retry_current_rows": 4972,
  "retry_frozen_rows": 0,
  "batches_read": 10,
  "batches_read_names": [
    "batch_000001.parquet",
    "batch_000002.parquet",
    "batch_000003.parquet",
    "batch_000004.parquet",
    "batch_000005.parquet",
    "batch_000006.parquet",
    "batch_000007.parquet",
    "batch_000008.parquet",
    "batch_000009.parquet",
    "batch_000010.parquet"
  ],
  "batches_skipped_names": [],
  "materialization_mode": "final",
  "validation_completion_status": "completed",
  "validation_checkpoint_source": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_validation\\trades_validate_q1_2024_d_smoke_v030\\validation_checkpoint.json",
  "validation_manifest_source": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\trades_v2_validation\\trades_validate_q1_2024_d_smoke_v030\\validation_run_manifest.json"
}
```

Hemos pasado por tres capas:

- v010
   - castigaba muchísimo por trade_price_outside_daily_range
   - ahí había muchos falsos duros por desalineación de escala
- v020
   - limpió gran parte de eso
   - mostró que muchos HARD_FAIL eran realmente mismatch de escala entre trades y daily/1m
- v030
   - intentó dejar duro solo lo confirmado mejor por daily + 1m
   - mejoró algo, pero no cerró el problema del todo

El punto clave es este:

- el validador ha mejorado
- pero la evidencia visual y la clasificación aún no están completamente alineadas
- por eso no te puedo decir todavía “esto ya está perfecto”

Por qué propongo el siguiente paso

Porque ahora mismo hay una contradicción que hay que resolver antes de seguir cambiando reglas.

He visto casos de tres tipos:

1. Casos claramente duros y plausibles

- ejemplo: ACIU, AAT, APWC
- los trades están en la misma escala
- y sí rompen daily y 1m
- eso parece problema real

2. Casos dudosos o mixtos

- ejemplo: APRE
- rompe daily bastante
- pero 1m no acompaña igual
- aquí no está tan claro que deba seguir duro

3. Casos directamente inconsistentes con lo que esperábamos

- ejemplo: ANSC
- el gráfico muestra outside_daily_count = 0
- y outside_1m_count = 0
- pero ha aparecido dentro del flujo de inspección de HARD_FAIL

Eso último es el problema más importante ahora mismo.

Cuál es el problema real que tenemos ahora

No es solo un problema de datos. Es un problema de trazabilidad entre capas:

- clasificación en 050
- materialización en 053
- selección del caso en notebook
- recálculo visual de outside_daily y outside_1m

Si una de esas capas no coincide con otra, puedes estar viendo un caso mal etiquetado o mal renderizado.

Entonces, antes de seguir afinando la regla, hay que responder esta pregunta:

- ¿los 657 HARD_FAIL de v030 son realmente casos duros?
- ¿o una parte de ellos sigue siendo residuo falso por inconsistencias de clasificación o visualización?

De dónde deriva este problema

Deriva de que estamos comparando varias referencias distintas:

- market.parquet
- ohlcv_daily
- ohlcv_1m

y además estamos resumiendo eso en varias etapas:

- métricas calculadas por el validador
- issues/warns persistidos
- materialización current
- notebook forense

Cuando todo eso no está perfectamente alineado, aparecen casos como:

- un file que debería ser daily+1m
- pero visualmente parece daily-only
- o peor: un file que visualmente no rompe nada y aun así entra en el bucket duro

Eso significa que aún no estamos midiendo el residuo con precisión quirúrgica suficiente.

Qué problema concreto sospecho ahora

Sospecho una de estas dos cosas, o ambas:

1. algunos casos de v030 todavía están mal clasificados

- sobre todo cuando 1m falta, es ancho, o no confirma claramente

2. el notebook puede estar mostrando casos que no corresponden exactamente al issue filtrado

- por bug de widget
- por mezcla de selección
- o por desalineación entre issues_list y el recálculo visual

Qué no hemos visto todavía porque no hemos granulado suficiente

Todavía no hemos separado bien estos subtipos:

- trade_price_outside_daily_and_1m_range realmente confirmado
- trade_price_outside_daily_range que persiste por error o por edge case
- casos con 1m faltante o NaN
- casos con muy pocos trades
- casos con 1 o 2 prints anómalos frente a cientos normales
- casos donde daily es más estrecha que la realidad intradía
- casos donde el notebook está recalculando algo distinto de lo que usó el validador

Y eso es importante porque no todos esos casos deberían tratarse igual.

Por eso el siguiente paso tiene sentido

El siguiente paso que propuse no es “otra heurística más”.
Es una auditoría tabular exacta para cada HARD_FAIL v030, con recálculo independiente de:

- outside_daily_count
- outside_1m_count
- ohlcv_1m_found
- same_scale_context
- issue realmente presente
- classification_consistent = True/False

Porque ahora mismo necesitamos saber:

- qué parte del residuo duro está bien confirmada
- qué parte sigue siendo ambigua
- y qué parte puede estar entrando por inconsistencia del pipeline analítico

Resumen corto

Ahora mismo mi decisión se basa en esto:

- ya vimos y corregimos el problema gordo de escala
- v030 mejora el contrato, pero aún deja casos ambiguos
- he visto ejemplos buenos y ejemplos contradictorios
- por eso no conviene seguir cambiando reglas “a ciegas”
- primero hay que cerrar la trazabilidad exacta del residuo duro

Si quieres, el siguiente paso te lo bajo ya a algo totalmente operativo:

- una celda que liste todos los HARD_FAIL v030
- con recálculo independiente
- y marque exactamente cuáles son:
   - consistentes
   - ambiguos
   - o sospechosos de bug analítico.



Ahora mismo en trades estamos usando como referencia:

- ohlcv_daily
- ohlcv_1m

Pero todavía no hemos auditado esos dos universos con el mismo rigor con el que hemos auditado trades y quotes. Entonces hay un
límite estructural:

- no puedes interpretar del todo bien un trade_price_outside_daily_range
- si no sabes antes qué calidad real tiene daily
- ni puedes interpretar del todo bien trade_price_outside_1m_range
- si no sabes qué calidad real tiene 1m

Así que sí: aparcar esta rama en el punto actual y abrir dos auditorías espejo tiene sentido.

Por qué es buena decisión

1. evita seguir afinando trades sobre referencias que aún no están auditadas a fondo
2. te da contexto causal real:

- si daily tiene defectos sistemáticos, trades vs daily se estaba leyendo mal
- si 1m tiene defectos sistemáticos, trades vs 1m también

3. permite volver luego a esta rama con mucha más precisión:

- qué es fallo real de trades
- qué es fallo de la referencia daily
- qué es fallo de la referencia 1m
- qué es desalineación entre universos

Mi recomendación
Sí, dejaría esta rama en estado “parking” con esta lectura:

- v010: baseline inflado
- v020: limpia escala
- v030: rebalancea daily frente a 1m
- estado actual:
   - prometedor
   - pero todavía no cerrado
   - pendiente de auditar daily y 1m

Qué haría exactamente ahora
Abrir dos líneas de auditoría paralelas:

1. daily

- contrato Agent02/Agent03
- auditoría técnica
- inventory / validate / materialize
- notebook raíz de problemas

2. 1m

- lo mismo

Resultado esperado
Después de eso, cuando volvamos a esta rama de trades, ya podremos decir con más fundamento:

- si daily está bien y 1m está bien, el residuo duro de trades es mucho más fiable
- si una de las referencias falla, sabemos exactamente cuánto ruido estaba metiendo

Sí, es una decisión razonable y probablemente la correcta.

Si quieres, el siguiente paso es dejar redactada la nota de parking de esta rama y el plan de arranque para:

- auditoría daily
- auditoría 1m