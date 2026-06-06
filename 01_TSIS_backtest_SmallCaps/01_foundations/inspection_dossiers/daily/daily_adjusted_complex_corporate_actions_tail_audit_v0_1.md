# Daily Adjusted Complex Corporate Actions Tail Audit v0.1

## Rol

Este documento mide la cola real de corporate actions que hoy queda fuera, o en la frontera, de la semantica institucional actual de `daily_adjusted`.

La pregunta no es si la implementacion actual de `adjusted` funciona para:

- `splits`
- `reverse splits`
- `cash dividends`

Eso ya esta razonablemente cerrado.

La pregunta es otra:

- que eventos estructurados existen de verdad en las fuentes;
- cuanto pesan dentro del universo `daily`;
- y cual de ellos sigue siendo deuda metodologica material.

## Fuentes auditadas

- `C:\\TSIS_Data\\data\\additional\\corporate_actions\\splits`
- `C:\\TSIS_Data\\data\\additional\\corporate_actions\\dividends`
- `C:\\TSIS_Data\\data\\additional\\corporate_actions\\ticker_events`
- `D:\\ohlcv_daily`

Script:

- [audit_daily_adjusted_complex_actions_tail.py](/C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/inspection/daily/audit_daily_adjusted_complex_actions_tail.py)

Evidencia:

- [daily_adjusted_complex_actions_tail_summary.csv](/C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_complex_actions_tail_audit/daily_adjusted_complex_actions_tail_summary.csv)
- [daily_adjusted_ticker_change_tail.csv](/C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_complex_actions_tail_audit/daily_adjusted_ticker_change_tail.csv)
- [daily_adjusted_non_cd_dividend_tail.csv](/C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_complex_actions_tail_audit/daily_adjusted_non_cd_dividend_tail.csv)
- [daily_adjusted_complex_actions_type_summary.csv](/C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_complex_actions_tail_audit/daily_adjusted_complex_actions_type_summary.csv)

## Hallazgo central

La deuda compleja real **no** aparece hoy como una masa rica de:

- `spin-offs`
- `stock dividends`
- reorganizaciones con taxonomia estructurada amplia

en las fuentes institucionales actuales.

Lo que existe de forma material y medible es mucho mas estrecho:

- `ticker_change`
- una cola pequena de `dividend_type != CD`

## Resultado agregado

### Taxonomia estructurada realmente presente

- `ticker_event_rows_total = 3037`
- `ticker_event_ticker_change_rows = 3037`
- `split_rows_total = 3335`
- `dividend_rows_total = 46118`
- `dividend_cd_rows = 45757`
- `dividend_non_cd_rows = 361`

### Interseccion con la cola compleja candidata

- `candidate_tickers_complex_tail = 2736`
- `candidate_tickers_with_daily_coverage = 2736`

### `ticker_change`

- `ticker_change_rows_total = 3037`
- `ticker_change_rows_within_daily_window = 2142`
- `ticker_change_rows_outside_daily_window = 895`
- `ticker_change_tickers_within_daily_window = 2072`

### Dividendos no `CD`

- `non_cd_dividend_rows_total = 361`
- `non_cd_dividend_rows_within_daily_window = 331`
- `non_cd_dividend_rows_outside_daily_window = 30`
- `non_cd_dividend_tickers_within_daily_window = 184`

Tipo observado:

- `SC = 361`

## Lectura tecnica

### 1. La fuente estructurada compleja es angosta

En `ticker_events` solo aparece un tipo:

- `ticker_change`

No hay una tabla rica donde hoy esten ya estructurados y listos para consumo:

- `spin-off`
- `stock dividend`
- `rights`
- `merger ratio`
- `distribution in kind`

Eso no prueba que tales eventos no existan economicamente en el mundo.

Si prueba algo mas acotado y util para el modulo:

- **esa cola no esta hoy estructurada en nuestras fuentes como una masa institucional ya consumible**.

### 2. La deuda material real es `ticker_change`, no una jungla desconocida

`2142` eventos `ticker_change` caen dentro de la ventana real disponible de `daily`.

Eso los convierte en deuda operativa real.

Pero su naturaleza es distinta de:

- `split`
- `reverse split`
- `cash dividend`

Un `ticker_change` no define por si mismo:

- continuidad economica defendible;
- factor multiplicativo de precio;
- ni cadena directa de ajuste.

Por eso la implementacion actual de `adjusted` no los incorpora automaticamente.

La deuda correcta aqui no es:

- “falta otro factor multiplicativo”

sino:

- “falta una politica institucional de continuidad corporativa y remap”.

### 3. La cola no `CD` existe, pero es pequena

Solo hay `361` filas no `CD` en todo el universo estructurado de dividendos, frente a:

- `45757` filas `CD`

Eso equivale aproximadamente a una cola del `0.78%` dentro de las filas de dividendos.

Y dentro de la ventana real de `daily` quedan activas:

- `331` filas
- sobre `184` tickers

Esto significa:

- la cola existe;
- no debe ignorarse;
- pero no domina metodologicamente la deuda de `adjusted`.

### 4. La semantica actual probablemente ya absorbe esta cola de cash subtype

La implementacion actual en `price_views.py` no filtra por `dividend_type == CD`.

Trabaja con:

- `cash_amount > 0`

Por tanto, esta cola `SC` no queda automaticamente fuera del ajuste por el solo hecho de no ser `CD`.

La deuda aqui no es:

- “el codigo ignora esas filas”

sino:

- “la policy institucional aun no explicita si `SC` debe tratarse exactamente igual que `CD`, o si requiere matiz”.

## Que si puede afirmarse ya

- La gran frontera compleja medible hoy **no** es una masa oculta de `spin-offs` o `stock dividends` estructurados.
- La deuda compleja realmente visible en nuestras fuentes es, sobre todo, `ticker_change`.
- La cola no `CD` existe pero es pequena y ya parece compatible con la mecanica actual basada en `cash_amount`.

## Que no debe afirmarse todavia

- No debe decirse que toda continuidad corporativa derivada de `ticker_change` queda resuelta.
- No debe decirse que el modulo ya soporta institucionalmente:
  - `spin-offs`
  - `stock dividends`
  - reorganizaciones economicas complejas

La razon no es una contradiccion de la auditoria.

La razon es otra:

- **esas clases no aparecen hoy como capa estructurada y consumible en las fuentes auditadas, o no aparecen con suficiente riqueza semantica para promocionarlas**.

## Consecuencia institucional

La siguiente deuda metodologica correcta ya no es rehacer `splits` ni reabrir `cash dividends`.

La deuda correcta es:

1. decidir si `ticker_change` debe dar lugar a una politica explicita de continuidad/remap;
2. declarar formalmente el tratamiento de `SC`;
3. y distinguir entre:
   - deuda estructurada presente en fuente
   - y deuda teorica futura si algun dia entran fuentes mas ricas de `spin-offs` o `stock dividends`.
