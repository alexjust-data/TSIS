# Ohlcv 1m Split-Normalized Pilot Results `v0_1`

## 1. Estado

El piloto real ya fue materializado en:

- `E:\TSIS\data\ohlcv_1m_split_normalized`

Manifest usado:

- `01_foundations/dataset_registry/1m/ohlcv_1m_split_normalized_pilot_manifest_v0_2.csv`

Resumen operativo:

- `E:\TSIS\data\ohlcv_1m_split_normalized\_split_normalized_materialization_summary.csv`

## 2. Veredicto corto

El piloto queda semanticamente valido.

La capa hace exactamente lo que debe hacer:

- en meses con split activo, la parte pre-evento recibe `future_split_factor != 1`
- en la fecha del evento y despues, el factor vuelve a `1`
- en controles posteriores al evento, el factor queda neutro

La conclusion importante no es solo que "el script corre".

La conclusion importante es que el patron observado en los datos coincide con la semantica exacta que declaramos en contrato.

## 2.1 Que estamos auditando exactamente

Este piloto no intenta demostrar que `1m_split_normalized` sea una serie economica completa.

Intenta auditar tres afirmaciones mucho mas precisas:

1. que la capa no inventa reescalados fuera de la logica de splits futuros;
2. que la capa no deja sin corregir los tramos anteriores a un split;
3. que los casos aparentemente raros, como un control pre-evento no neutro, son consecuencia correcta de la definicion del factor y no un bug.

## 2.2 Regla de validacion

La regla tecnica que se intenta falsar es esta:

- `future_split_factor(date_t) = producto de split_ratio para toda execution_date > date_t`

Si esa regla fuera falsa en la implementacion, deberiamos ver incoherencias como:

- un mes post-evento con gran masa `!= 1` sin split posterior;
- un mes pre-evento con masa `= 1` donde deberia haber reescalado;
- o controles supuestamente neutros que se comportan como si hubiera un split inexistente.

## 3. Lectura importante

El piloto demuestra una regla que debe quedar muy clara:

- un control no significa necesariamente `future_split_factor = 1`

Si el control es:

- un mes anterior a un split futuro

entonces la capa correctamente sigue aplicando un factor distinto de `1`, porque la normalizacion es:

- forward-looking

y busca reexpresar el pasado en la escala posterior al split.

Esto es justo el tipo de detalle que evita naipes en el aire.

Si este matiz no se explicita, alguien puede mirar `BXRX 2022-11` y concluir:

- "el control salio mal"

cuando la lectura correcta es:

- "el control esta antes del split y por tanto debe llevar el factor del split futuro".

## 3.1 Diferencia entre control pre-evento y control post-evento

Hay dos tipos de control y no deben mezclarse:

- `control pre-evento`
  - no tiene split dentro del mes;
  - pero si tiene un split futuro fuera del mes;
  - por tanto puede llevar `future_split_factor != 1`.

- `control post-evento`
  - no tiene split dentro del mes;
  - y tampoco tiene split futuro relevante dentro de la cadena activa;
  - por tanto debe ser neutro.

## 4. Resultado por caso

### Reverse split

- `BXRX | 2022-12 | 40 -> 1`
  - `rows = 7424`
  - `split_non1_rows = 0`
  - lectura:
    - el split cae el `2022-12-01`, al arranque del mes;
    - por eso dentro de ese `ticker-month` ya no hay tramo pre-evento que reescalar.
  - conclusion de auditoria:
    - este caso es importante porque evita una falsa expectativa ingenua;
    - no todo mes de evento debe contener filas reescaladas;
    - si el split cae en el primer dia observado del mes, el resultado correcto puede ser precisamente `0`.

- `COSM | 2022-12 | 25 -> 1`
  - `rows = 16986`
  - `split_non1_rows = 9929`
  - `58.45%` del mes queda reescalado
  - lectura:
    - del `2022-12-01` al `2022-12-15` el factor es `0.04`;
    - desde `2022-12-16` el factor pasa a `1.0`.
  - conclusion de auditoria:
    - este es el caso canonico que queriamos ver;
    - antes del evento hay masa amplia reescalada;
    - en la fecha exacta del evento el factor deja de aplicarse;
    - por tanto la frontera temporal del split esta quedando respetada y no maquillada.

- `CEI | 2022-12 | 50 -> 1`
  - `rows = 15660`
  - `split_non1_rows = 10956`
  - `69.96%` del mes queda reescalado
  - lectura:
    - la mayor parte del mes esta antes del evento del `2022-12-21`;
    - por tanto la mayor parte del mes debe reexpresarse.
  - conclusion de auditoria:
    - el porcentaje alto no significa error;
    - significa que el evento cae tarde en el mes;
    - justo por eso la mayor parte de las barras siguen estando en escala previa.

- `BNGO | 2025-01 | 60 -> 1`
  - `rows = 10560`
  - `split_non1_rows = 9256`
  - `87.65%` del mes queda reescalado
  - lectura:
    - el evento cae muy tarde, el `2025-01-27`;
    - casi todo enero pertenece al tramo pre-evento.
  - conclusion de auditoria:
    - este caso empuja al extremo la semantica;
    - si casi todo el mes es pre-evento, casi todo el mes debe reescalarse;
    - ver un `87.65%` alto aqui no es sospechoso, es exactamente lo esperable.

### Forward split

- `EFSH | 2025-01 | 1 -> 2`
  - `rows = 6328`
  - `split_non1_rows = 2430`
  - `38.40%` del mes queda reescalado
  - conclusion de auditoria:
    - forward split y reverse split comparten la misma logica temporal;
    - cambia la magnitud del ratio, no el principio de reescalado.

- `SAVA | 2023-12 | 10 -> 14`
  - `rows = 7760`
  - `split_non1_rows = 5393`
  - `69.50%` del mes queda reescalado
  - conclusion de auditoria:
    - la capa no presupone ratios simples `2x` o `10x`;
    - tambien funciona con ratios menos triviales como `10 -> 14`.

- `PD | 2006-03 | 1 -> 2`
  - `rows = 9345`
  - `split_non1_rows = 3200`
  - `34.24%` del mes queda reescalado
  - conclusion de auditoria:
    - este caso evita el sesgo de pensar que la semantica solo funciona en datos recientes;
    - la regla tambien se sostiene en un tramo historico temprano.

- `LIVE | 2014-02 | 1 -> 3`
  - `rows = 7038`
  - `split_non1_rows = 7038`
  - `100%` del mes queda reescalado
  - lectura:
    - el evento cae el `2014-02-12`;
    - pero el mes disponible en `1m` queda completamente en tramo pre-evento bajo esta definicion de fechas observadas.
  - conclusion de auditoria:
    - un `100%` reescalado tampoco implica bug por si solo;
    - implica que toda la muestra disponible del mes cae antes de que el dataset considere consumado el nuevo regimen de escala.

### Controls

- `BXRX | 2022-11 | control pre-evento`
  - `rows = 3801`
  - `split_non1_rows = 3801`
  - `100%` del mes queda reescalado
  - lectura:
    - es control porque no hay split dentro del mes;
    - no es neutro en factor porque sigue siendo pasado respecto al split de `2022-12-01`.
  - conclusion de auditoria:
    - este es el caso mas importante pedagogicamente;
    - demuestra que "control" no significa "factor 1";
    - significa "mes sin evento interno", lo cual es distinto.

- `BNGO | 2025-02 | control post-evento`
  - `rows = 2724`
  - `split_non1_rows = 0`
  - lectura:
    - es el control neutro puro;
    - ya no hay split futuro dentro de la cadena relevante.
  - conclusion de auditoria:
    - este es el caso que cierra la pinza;
    - demuestra que la capa no deja residuos artificiales una vez superado el evento.

## 5. Consecuencia metodologica

El piloto demuestra que la lectura correcta de `1m_split_normalized` no es:

- "mes con split = factor distinto de 1"

sino:

- "toda observacion anterior al split futuro debe reescalarse a la nueva base"

Eso es exactamente lo que protege al ML y al backtest intradia de aprender saltos mecanicos falsos entre sesiones.

## 5.1 Por que esto no es construir castillos en el aire

No estamos diciendo:

- "parece razonable"

Estamos verificando observaciones que podrian refutar la semantica y no la refutan.

En concreto, ya observamos que:

- un evento al inicio del mes puede dar `0` filas reescaladas;
- un evento tardio puede dar `>80%` del mes reescalado;
- un control pre-evento puede dar `100%` reescalado;
- y un control post-evento puede dar `0`.

Estas cuatro situaciones, juntas, son justamente las que nos permiten auditar que la capa:

- no esta maquillando los datos;
- no esta aplicando una regla superficial;
- y si esta obedeciendo una logica temporal precisa.

## 6. Siguiente paso

Con el piloto validado, el siguiente paso correcto es:

- construir una lectura corta `raw vs split_normalized` caso por caso
- y despues conectar el primer consumidor intradia real que cruce sesiones

Estado actual:

- esta capa visual ya fue exportada en:
  - `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_pilot_readout_v0_1.md`
