# Ohlcv 1m Split-Normalized Dataset Contract `v0_1`

## 1. Rol

Este documento define la primera promocion contractual de `ohlcv_1m_split_normalized` como capa intradia de reconciliacion de escala mecanica.

No define una capa economica completa tipo `adjusted`.

Define una capa minima para evitar que modelos o backtests intradia aprendan discontinuidades de split o reverse split como si fueran alpha.

## 2. Que representa

`ohlcv_1m_split_normalized` representa:

- la misma barra observada de `1m`
- en la misma semantica intradia raw
- pero reescalada por el factor de split futuro

La pregunta que responde es:

- si dos tramos historicos intradia son comparables en escala mecanica entre sesiones

## 3. Que no representa

`ohlcv_1m_split_normalized` no representa:

- retorno economico total ajustado por dividendos
- truth operativa de ejecucion minuto a minuto en el numero raw observado
- sustituto de `quotes_raw` o `trades_raw`

## 4. Transformacion contractual

La transformacion minima es:

1. partir de `ohlcv_1m raw`
2. aplicar el `future_split_factor`
3. producir columnas `o/h/l/c` en escala split-normalized

Formula base:

- `px_split_normalized = px_raw * future_split_factor`

Definicion exacta del factor:

- `future_split_factor(date_t) = producto de todos los split_ratio con execution_date > date_t`

Interpretacion tecnica:

- una observacion anterior a un split futuro debe reexpresarse en la nueva escala;
- una observacion en la fecha del split o posterior ya vive en esa nueva escala y por tanto debe llevar factor `1` salvo splits aun posteriores.

## 4.1 Que seria evidencia de que esto esta mal

La capa quedaria conceptualmente mal si observaramos cualquiera de estas cosas:

- meses anteriores a un split futuro con `future_split_factor = 1` de forma sistematica;
- meses posteriores al ultimo split relevante con `future_split_factor != 1` sin que exista otro split futuro;
- barras `1m` donde la escala raw y la split-normalized no cambian pese a existir un split futuro activo;
- o, al contrario, barras sin split futuro donde la capa inventa reescalados no explicables.

## 4.2 Que debe verse si esta bien

Si la capa esta bien, debe verse esto:

- tramo pre-evento con `future_split_factor != 1`;
- fecha del evento y tramo posterior con `future_split_factor = 1`, salvo nuevos eventos posteriores;
- controles anteriores al evento que pueden seguir saliendo no neutros;
- controles posteriores al evento que deben salir neutros.

## 5. Columnas minimas esperadas

Columnas raw preservadas:

- `ticker`
- `ts`
- `date`
- `year`
- `month`
- `o`
- `h`
- `l`
- `c`
- `v`

Columnas de reconciliacion minima:

- `future_split_factor`
- `o_split_normalized`
- `h_split_normalized`
- `l_split_normalized`
- `c_split_normalized`
- `materialized_price_view`
- `source_1m_file`

## 6. Vista contractual

La vista contractual de esta capa es:

- `1m_split_normalized`

No:

- `1m_adjusted`

## 7. Usos permitidos

Usos permitidos:

- reconciliacion historica entre `1m`, `daily`, `quotes` y `trades`
- features intradia que crucen sesiones y necesiten escala comparable
- ML intradia cuando el contexto abarque fechas con splits o reverse splits
- backtests intradia que calculen estados o retornos entre sesiones

## 8. Usos prohibidos

Usos prohibidos:

- tratar esta capa como sustituto universal de `1m raw`
- usarla para estudiar microestructura observada local cuando la verdad requerida es el numero raw del mercado
- usarla como capa completa de ajuste economico por dividendos

## 9. Justificacion

Sin esta capa, un modelo intradia o un backtest que compare sesiones distintas puede aprender:

- `+200%`
- `-90%`
- o cualquier shock aparente

que en realidad solo refleja:

- un split
- o un reverse split

Eso no es un riesgo teorico abstracto.

Es exactamente el tipo de error que hace que:

- un estado entre sesiones parezca un breakout inexistente;
- un feature de gap o retorno arranque dominado por un cambio mecanico;
- o un clasificador de regimen absorba corporate actions como si fueran dinamica de mercado.

## 9.1 Objetivo de auditoria

Esta capa no se promueve para "tener otra vista mas".

Se promueve para poder auditar y demostrar que:

- cuando una discontinuidad entre sesiones desaparece en `1m_split_normalized`, la explicacion es mecanica y trazable;
- cuando no desaparece, el problema ya no es el split y debe buscarse en otra parte;
- y el sistema no esta maquillando los datos, sino declarando explicitamente la base de escala que usa.

## 10. Relacion con otras vistas

- `1m raw`: verdad observada del minuto
- `1m_split_normalized`: verdad de escala comparable entre sesiones
- `daily_adjusted`: verdad economica lenta para retornos y labels diarios

## 11. Veredicto

`ohlcv_1m_split_normalized` es la siguiente capa intradia minima que debe promocionarse despues de `daily_adjusted`, porque protege el nucleo ML/backtest del proyecto frente a saltos mecanicos de escala sin obligar todavia a crear un `1m_adjusted` economico completo.
