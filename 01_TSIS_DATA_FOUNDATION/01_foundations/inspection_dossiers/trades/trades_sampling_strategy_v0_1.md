# `trades` Sampling Strategy v0.1

## Proposito

Este documento fija la estrategia de muestreo para los futuros case packs de `trades`.

La regla principal es:

- no seleccionar ejemplos a dedo;
- no limitarse a un puñado de casos visualmente llamativos;
- y no asumir que una familia queda explicada con dos o tres figuras bonitas.

El objetivo es construir una muestra forense **representativa y defendible** para cada familia relevante del bloque.

## Dos modos de cobertura

### 1. Enumeracion completa

Se usa cuando el bucket es lo bastante pequeno como para inspeccionarlo entero sin perder legibilidad institucional.

### 2. Muestra estratificada

Se usa cuando el bucket es demasiado grande para enumeracion completa.

La muestra estratificada debe:

- cubrir centro y colas;
- cubrir anos distintos;
- cubrir subfirmas causales dentro del bucket;
- y evitar cherry-picking del inspector o del agente.

## Regla transversal de tamano

La politica inicial recomendada es:

- bucket con `<= 30` casos:
  - enumeracion completa
- bucket con `31-120` casos:
  - enumeracion completa si el render final sigue siendo legible; si no, muestra fuerte de `20-40`
- bucket con `> 120` casos:
  - muestra estratificada fuerte de `24-60` casos

La cifra exacta final por bucket puede cambiar si el universo actualizado deriva, pero la regla de representatividad no.

## Familias y estrategia recomendada

## `reference_scale_mismatch`

### Que representa

Familia de conflicto de comparabilidad por escala frente a arbitros (`daily`, `1m`, VWAP de referencia). No es, por defecto, una familia de tape roto.

### Cobertura recomendada

- muestra estratificada fuerte

### Variables de estratificacion

- `scale_bucket_vw`
- `scale_bucket_high`
- `trade_vwap_vs_daily_vw_diff_pct_raw`
- `outside_1m_regular_pct`
- `year`
- tamano del file (`rows_after_parse` o proxy disponible)

### Logica

Hay que cubrir:

- escalas cercanas y escalas extremas;
- anos antiguos y recientes;
- conflicto leve, medio y severo contra `1m`;
- files pequenos y files mas densos.

### Consecuencia esperada

La muestra debe permitir distinguir:

- conflicto de escala estable y repetible;
- escalas aberrantes que siguen siendo comparabilidad y no corrupcion;
- y frontera donde el bucket ya no se sostiene como simple mismatch.

## `review_microstructure`

### Que representa

Familia donde el conflicto dominante vive en la textura fina del tape:

- odd-lots
- duplicacion
- burst por timestamp
- comparabilidad fina del flujo

### Cobertura recomendada

- muestra estratificada fuerte

### Variables de estratificacion

- `odd_lot_trade_pct`
- `outside_1m_odd_lot_pct`
- `outside_1m_round_lot_pct`
- `duplicate_exact_ratio_pct_raw`
- `max_trades_same_timestamp_raw`
- `outside_minutes_pct_active`
- `year`

### Logica

Hay que cubrir:

- casos dominados por odd-lots;
- casos dominados por duplicacion;
- casos mixtos;
- y distintos grados de persistencia temporal del outside.

### Consecuencia esperada

La muestra debe demostrar que `review_microstructure` no es un cajon de sastre, sino una familia con subfirmas internas reconocibles.

## `review_no_1m_reference`

### Que representa

Familia donde existe conflicto contra referencias mas gruesas, pero falta `1m` para arbitrar el caso con precision.

### Cobertura recomendada

- historicamente parecia candidata a enumeracion completa;
- en el cierre real `57f` ya tiene masa suficiente para muestra estratificada fuerte

### Variables de orden interno

- `outside_daily_regular_pct`
- `trade_vwap_vs_daily_vw_diff_pct_raw`
- `year`
- tamano del file

### Logica

La intuicion historica era que el bucket seria pequeno. En el cierre real eso ya no se sostiene del todo. Por tanto, la regla vigente pasa a ser:

- muestra estratificada fuerte sobre el universo full;
- y, si hace falta, enumeracion completa solo sobre subtramos severos o anos concretos.

### Consecuencia esperada

El inspector debe ver claramente que:

- la ausencia de `1m` no absuelve;
- pero tampoco permite condena automatica.

## `review_1m_reference_alignment`

### Que representa

Familia donde `daily` y VWAP pueden parecer razonables, pero `1m` cambia la verdad del caso.

### Cobertura recomendada

- historicamente parecia candidata a enumeracion completa;
- en el cierre real `57f` ya tiene masa suficiente para muestra estratificada fuerte

### Logica

El bucket sigue siendo conceptualmente importante, pero ya no es tan pequeno como sugeria la intuicion heredada de la muestra metodologica. La regla vigente pasa a ser:

- muestra estratificada fuerte sobre el universo full;
- y, si hace falta, enumeracion completa solo sobre subfamilias especialmente raras o severas.

### Consecuencia esperada

Cada caso debe dejar muy claro:

- por que `1m` es el arbitro decisivo;
- y por que el caso no puede promoverse por una lectura demasiado gruesa.

## `review` generico

### Que representa

Residuo que sigue abierto y no cae limpiamente en una familia mas especifica ya reinterpretada.

### Cobertura recomendada

- muestra estratificada fuerte

### Variables de estratificacion

- `trade_vwap_vs_daily_vw_diff_pct_raw`
- `outside_daily_regular_pct`
- `outside_1m_regular_pct`
- `outside_minutes_pct_active`
- `sample_stratum`
- `year`

### Logica

La muestra debe impedir dos errores:

- creer que `review` es un bucket vacio sin estructura;
- o creer que toda su masa es automaticamente recuperable.

### Consecuencia esperada

La muestra debe servir como base para rematerializar la regla de rehabilitacion y estimar la masa real de `recoverable_with_flag`.

## `bad_data`

### Que representa

Cola donde el file deja de ser economicamente defendible como flujo de ejecucion o comparacion.

### Cobertura recomendada

- muestra estratificada fuerte
- o enumeracion completa si la extraccion final de ejemplos queda manejable

### Variables de estratificacion

- magnitud de `trade_vwap_vs_daily_vw_diff_pct_raw`
- `outside_1m_regular_pct`
- `duplicate_exact_ratio_pct_raw`
- `scale_bucket_vw` cuando exista
- `year`
- tamano del file

### Logica

Hay que cubrir:

- dano de escala extrema;
- dano de duplicacion;
- dano mixto;
- y casos donde la ruptura es visual y economicamente obvia.

### Consecuencia esperada

El inspector debe poder separar sin duda la cola `bad` de las familias meramente recuperables.

## `good`

### Que representa

Cola pristine extremadamente estricta donde `trades`, `daily` y `1m` alinean casi impecablemente.

### Cobertura recomendada

- enumeracion completa

### Logica

Es pequeno y conceptualmente muy importante. Su rareza es parte del mensaje institucional.

### Consecuencia esperada

El inspector debe ver:

- que `good` existe de verdad;
- que no es imaginario;
- y que tampoco mide por si solo la masa util del bloque.

## Regla de export

Para cada familia, la exportacion futura debe producir:

1. imagenes agregadas de la familia;
2. muestra estratificada o enumeracion completa segun la regla anterior;
3. manifests reproducibles en `evidence_assets/stratified_samples/`;
4. `.md` para inspector que expliquen, para cada imagen y cada caso:
   - que muestra;
   - responde;
   - no responde;
   - consecuencia.

## Primera materializacion ya creada

La primera materializacion sobre `57f/full_clean_fast_same_schema` ya existe en:

- [trades_stratified_sample_manifests_v0_1.md](./evidence_assets/stratified_samples/trades_stratified_sample_manifests_v0_1.md)

Resultado actual:

- `review`: `60`
- `reference_scale_mismatch`: `60`
- `review_microstructure`: `60`
- `bad_data`: `60`
- `review_no_1m_reference`: `60`
- `review_1m_reference_alignment`: `60`
- `good`: `106` (enumeracion completa)

Eso fija la muestra base que debe usarse en la siguiente etapa de export y dossier, salvo que cambie el cache canonico o la policy de estratificacion.
3. `md` especifico de familia;
4. y texto interpretativo que explique:
   - que significa la familia;
   - por que esos casos estan juntos;
   - que decision cambia;
   - y que pipeline afecta.

## Regla para el siguiente agente

No construir los futuros case packs de `trades` solo desde:

- intuicion visual;
- facilidad de lectura;
- o nombres de ticker conocidos.

La cobertura debe salir de esta politica de muestreo y quedar trazable en el dossier final.
