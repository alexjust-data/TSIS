# Daily Adjusted - Operational Landing `v0_1`

## 1. Decision

La primera promocion operativa oficial de `daily_adjusted` debe vivir en:

- `E:\TSIS\data\ohlcv_daily_adjusted`

No debe vivir:

- dentro de `01_foundations`
- ni mezclado dentro de `D:\ohlcv_daily`

## 2. Por que esta ruta es correcta

La topologia del modulo ya fija que:

- `E:\TSIS\data\...` es el plano objetivo de datos operativos activos
- `01_foundations` es la capa institucional y contractual

Por tanto, `daily_adjusted` debe seguir la misma logica:

- datos materializados en `E:\TSIS\data\...`
- contrato y gobernanza en `01_foundations`

Esto evita dos errores:

- contaminar la capa raw `ohlcv_daily`
- y usar `01_foundations` como almacenamiento operativo de parquets

## 3. Layout fisico recomendado

La capa debe espejar la estructura de `ohlcv_daily`.

Ruta base:

- `E:\TSIS\data\ohlcv_daily_adjusted`

Ejemplo:

- `E:\TSIS\data\ohlcv_daily_adjusted\ticker=A\year=2005\day_aggs_A_2005_adjusted.parquet`

Regla:

- mismo ticker root
- mismo particionado anual
- mismo archivo base
- sufijo `_adjusted`

## 4. Naming recomendado

### Capa

- `ohlcv_daily_adjusted`

### Vista materializada

- `daily_adjusted_v0_1`

### Archivos

- `day_aggs_<TICKER>_<YEAR>_adjusted.parquet`

## 5. Estrategia de materializacion recomendada

La estrategia inicial no debe ser una reescritura masiva a ciegas.

Debe ser:

- **incremental por ticker-year**
- reproducible
- con `summary manifest`
- y con provenance explicita

## 6. Motivo para no empezar full-universe ciego

Aunque el universo es manejable, lanzar una promocion completa sin una primera integracion de consumidor haria dos cosas mal:

- escribir una capa grande sin validar todavia el primer uso real
- fijar demasiado pronto detalles operativos que quizas cambien al conectar el primer consumidor

Por eso el orden correcto es:

1. ruta oficial
2. layout oficial
3. materializador reproducible
4. primer consumidor real
5. luego expansion full-universe

## 7. Primer consumidor objetivo

El primer consumidor real objetivo debe ser:

- **labels diarios de retorno**

y, en segunda posicion inmediata:

- `backtest_core` diario

El contrato minimo de ese primer consumidor vive en:

- [daily_return_labels_consumer_contract_v0_1.md](./daily_return_labels_consumer_contract_v0_1.md)

## 8. Encaje correcto dentro de la estrategia real

El proyecto no es un sistema diario clasico.

Su nucleo real es:

- intradia
- scalping / hyperscalping
- small caps dormidas que despiertan abruptamente
- y una capa ML que debe adaptarse al regimen del mercado observado

Por tanto, `daily_adjusted` no es el motor operativo principal del sistema.

Su rol correcto es:

- verdad economica lenta
- benchmarking
- labels lentos o agregados
- retorno acumulado
- y consistencia institucional de evaluacion

El motor operativo principal sigue viviendo en:

- `quotes_raw`
- `trades_raw`
- `ohlcv_1m`
- `halts`

## 9. Por que labels diarios primero

Es el consumidor mas limpio para validar la capa porque:

- depende directamente de continuidad economica
- evita el error de aprender corporate actions como alpha
- y no necesita todavia abrir toda la complejidad de simulacion o ejecucion

Ademas, si los labels diarios ya salen de `daily_adjusted`, el resto del research diario queda mucho mejor anclado.

## 10. Segundo consumidor objetivo

Despues de labels diarios, el siguiente consumidor natural debe ser:

- `backtest_core`

usando `c_adjusted` como base de retorno y benchmarking economico.

## 11. Implicacion para `1m`

Si el modelo o el backtest intradia usan historia que cruza una frontera de split o reverse split, no deben aprender esa discontinuidad como si fuera un salto economico real.

Por tanto, la respuesta correcta es:

- **si**, el proyecto necesita disciplina de normalizacion por split tambien en `1m`

pero eso no obliga todavia a lanzar un clon full-universe completo como primer paso.

La secuencia correcta es:

1. cerrar `daily_adjusted`
2. crear una vista o utilidad institucional de `1m_split_normalized`
3. decidir despues si se materializa todo el universo `1m` o si se calcula bajo demanda

Regla:

- para evaluacion economica lenta: `daily_adjusted`
- para nucleo operativo intradia: `1m raw`, `quotes_raw`, `trades_raw`
- para cruzar fronteras de split en intradia: `1m_split_normalized`

## 12. Lo que queda fuera de esta primera promocion

No forma parte de esta primera promocion:

- `execution_simulator`
- `quotes_raw`
- `trades_raw`
- reconciliacion masiva completa con `split_normalized`
- corporate actions complejos mas alla de la cadena ya implementada

## 13. Condicion de promocion a full-universe

La capa deberia pasar de piloto incremental a promocion full-universe cuando se cumplan estas tres condiciones:

- primer consumidor real conectado
- smoke test validado en varios tickers con corporate actions reales
- decision estable sobre manifest y provenance

## 14. Veredicto final

La ruta operativa correcta para esta fase es:

- `E:\TSIS\data\ohlcv_daily_adjusted`

La estrategia correcta es:

- incremental, reproducible y con provenance

Y el primer consumidor correcto es:

- labels diarios de retorno

antes de abrir la promocion a `backtest_core` completo o a consumidores de umbral mas alto.

Esto no contradice el caracter intradia del proyecto.

La lectura correcta es:

- `daily_adjusted` primero para cerrar la verdad economica lenta;
- `1m_split_normalized` despues para proteger el nucleo intradia contra saltos falsos por splits y reverse splits;
- `quotes_raw` y `trades_raw` siguen siendo la verdad operativa del mercado observado.

El plan incremental exacto de promocion vive en:

- [daily_adjusted_incremental_materialization_plan_v0_1.md](./daily_adjusted_incremental_materialization_plan_v0_1.md)
