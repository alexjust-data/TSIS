# Trades Inspection Readout v0.1

## 1. Proposito

Este documento es el cierre institucional de inspeccion de `trades` en `01_foundations`.

Su funcion no es reabrir toda la auditoria, sino ordenar las tres verdades del bloque:

- masa poblacional global muy tensionada;
- muestra metodologica profunda que explica la estructura del conflicto;
- cierre full final que conserva una cola `bad` pequena y una masa `review` muy grande que no puede tratarse como un todo homogeneo.

## 2. Fuentes de autoridad

Mandan conjuntamente:

- `auditoria/trades/v2`
- `certification/trades`
- `certification/global_metrics` con chequeo de drift
- contratos y policies ya promovidos a `01_foundations`

## 3. Regla central

En `trades` nunca debe mezclarse:

1. poblacion;
2. muestra file-acceptance `380`;
3. full closeout `57f`;
4. estados finales de certificacion.

Esta es la frontera conceptual del bloque. Si se rompe, el inspector acaba leyendo como `bad tape` lo que en realidad es conflicto de comparabilidad, escala o microestructura.

## 4. Estados finales correctos

La certificacion final ya no debe expresarse solo con labels tecnicos. Debe expresarse como:

- `good`
- `recoverable_with_flag`
- `review_not_rehabilitated`
- `bad`

La traduccion file-level sirve para construir esa semantica, no para sustituirla.

## 5. Conteos finales observados en `57f`

- `review = 4,851,211`
- `reference_scale_mismatch = 2,418,062`
- `review_microstructure = 2,130,781`
- `bad_data = 15,869`
- `review_no_1m_reference = 8,091`
- `review_1m_reference_alignment = 4,992`
- `good = 106`

## 5b. Rematerializacion de la regla de rehabilitacion sobre `57f`

La politica historica de recuperacion no debe quedarse anclada al parcial `57e/full_clean`. Ya se ha recalculado sobre el cache canonico real:

- `root_cause_exports/file_acceptance_cache_lt1b_full_clean_fast_same_schema`

### Regla estricta aplicada al bucket `review`

Se exige:

- `scale_bucket_vw` en `{~1x, near_1x}`
- `trade_vwap_vs_daily_vw_diff_pct_raw <= 0.5`
- `outside_daily_regular_pct <= 1`
- `outside_1m_regular_pct <= 15`

Resultado real sobre `57f`:

- `review_total = 4,851,211`
- `review_recoverable_strict = 3,327,955`
- `review_recoverable_strict_pct = 68.6005%`
- `review_not_rehabilitated_strict = 1,523,256`

### Regla extendida

Se exige:

- `scale_bucket_vw` en `{~1x, near_1x}`
- `trade_vwap_vs_daily_vw_diff_pct_raw <= 1.0`
- `outside_daily_regular_pct <= 2`
- `outside_1m_regular_pct <= 20`

Resultado real:

- `review_recoverable_extended = 3,505,290`
- `review_recoverable_extended_pct = 72.2560%`
- `review_not_rehabilitated_extended = 1,345,921`

### Que responde

- cuanta masa del bucket `review` puede pasar hoy de forma defendible a `recoverable_with_flag`;
- cuanta masa sigue abierta como `review_not_rehabilitated`;
- y cuan lejos queda el cierre real del optimismo implicito en el parcial `57e`.

### Que no responde

- la rehabilitacion completa del bloque `trades`;
- la parte recuperable de `review_microstructure` y `review_1m_reference_alignment`;
- ni la rehabilitacion potencial futura de `reference_scale_mismatch`.

### Consecuencia

La consecuencia institucional es fuerte: la masa util real de `trades` es mucho mayor que el bucket `good`, pero tambien bastante menos limpia de lo que sugeria el resultado historico parcial sobre `57e`.

## 5c. Recuperacion provisional de `review_microstructure` y `review_1m_reference_alignment`

La politica historica de `certification` ya sostenia que estas dos familias admiten recuperacion parcial segun uso. Sobre `57f`, esa intuicion ya puede cuantificarse de forma operativa.

### `review_microstructure`

Regla provisional estricta:

- `scale_bucket_vw` en `{~1x, near_1x}`
- `trade_vwap_vs_daily_vw_diff_pct_raw <= 1.0`
- `core_outside_daily_pct <= 1`
- `core_outside_1m_pct <= 1`

Resultado:

- `review_microstructure_total = 2,130,781`
- `recoverable_strict_provisional = 1,516,547`
- `recoverable_strict_pct = 71.1733%`

Sensibilidad extendida:

- `trade_vwap_vs_daily_vw_diff_pct_raw <= 2.0`
- `core_outside_daily_pct <= 2`
- `core_outside_1m_pct <= 2`

Resultado:

- `recoverable_extended_provisional = 1,636,379`
- `recoverable_extended_pct = 76.7971%`

### Que responde

- cuanta masa de microestructura dificil conserva un nucleo economicamente usable con `flag`;
- y cuanta parte del bucket sigue siendo demasiado rugosa incluso para uso extendido.

### `review_1m_reference_alignment`

Regla provisional estricta:

- `scale_bucket_vw` en `{~1x, near_1x}`
- `trade_vwap_vs_daily_vw_diff_pct_raw <= 1.0`
- `core_outside_daily_pct <= 1`
- `core_outside_daily_volume_pct <= 1`

Resultado:

- `review_1m_reference_alignment_total = 4,992`
- `recoverable_strict_provisional = 2,591`
- `recoverable_strict_pct = 51.9030%`

Sensibilidad extendida:

- `trade_vwap_vs_daily_vw_diff_pct_raw <= 2.0`
- `core_outside_daily_pct <= 2`
- `core_outside_daily_volume_pct <= 2`

Resultado:

- `recoverable_extended_provisional = 3,715`
- `recoverable_extended_pct = 74.4191%`

### Que responde

- cuanta parte de este bucket pequeno pero delicado puede admitirse con limitacion de uso;
- y cuanta parte sigue siendo demasiado conflictiva incluso con arbitro `1m` presente.

### Regla de cautela

Estas dos cuantificaciones no deben presentarse como si fueran una regla historica cerrada equivalente a la de `review` generico.

Deben presentarse como:

- rematerializacion operativa provisional;
- anclada en la semantica historica de `certification`;
- y util para estimar masa recuperable real mientras se formaliza una policy final mas cerrada.

## 6. Como leer esos numeros

La lectura ingenua seria:

- casi todo `trades` esta mal.

La lectura correcta es:

- hay un conflicto masivo, pero su semantica dominante no es `bad_data`;
- la masa vive en comparabilidad de escala y microestructura;
- la cola `bad_data` existe, pero es pequena;
- `good` existe, pero es extremadamente escaso.

La consecuencia institucional es fuerte: `trades` no puede consumirse como si fuera serie diaria simple, pero tampoco debe descartarse como dataset universalmente roto.

## 6a. `bad_data` no es una sola familia visual

La cola `bad_data` existe y es real, pero no se ve siempre de la misma manera.

Hoy ya puede distinguirse, sobre `57f`, entre al menos dos subfamilias:

### `bad_data` de colapso de escala o de rango

Firma dominante:

- `trade_price_outside_daily_range`
- `scale_bucket_vw = nan`
- `% outside daily` y `% outside 1m` muy altos o totales

Que responde:

- si el tape y los arbitros viven en mundos de precio incompatibles;
- y si el panel de precio por si solo ya demuestra ruptura semantica.

Conteo observado en `57f`:

- `trade_price_outside_daily_range`: `9,606` (`60.53%` de `bad_data`)
- `scale_bucket_vw = nan`: `4,247` (`26.76%`)
- `outside_daily_regular_pct = 100%`: `5,707` (`35.96%`)
- `outside_1m_regular_pct = 100%`: `4,910` (`30.94%`)

Consecuencia:

- esta subfamilia si queda bien defendida por el panel actual `trades raw vs daily vs 1m`.

### `bad_data` de integridad estructural del tape

Firma dominante:

- `negative_or_zero_size_rows`
- duplicacion dura
- o rows invalidos con precio casi normal

Que responde:

- si el file deja de ser un flujo de ejecucion valido aunque el camino del precio no grite;
- y si el rechazo vive en la estructura del tape mas que en la geometria del panel.

Conteo observado en `57f`:

- `negative_or_zero_size_rows`: `695` (`4.38%`)
- `duplicate_excess_ratio_gt_hard_cap`: `1,329` (`8.37%`)
- estructural sin conflicto diario fuerte: `204` (`1.29%`)
- estructural mezclado con conflicto de rango: `491` (`3.09%`)

Consecuencia:

- esta subfamilia no queda bien demostrada por el panel de precio actual;
- necesita una visualizacion adicional de integridad (`size <= 0`, duplicados, filas invalidas).

## 6b. Por que `good` es tan pequeno y por que eso no basta para condenar el bloque

El dato que mas alarma genera es:

- `good = 106`

frente a millones de files en `review`.

La tentacion natural es concluir:

- si `good` es casi cero, entonces casi todo `trades` es basura.

Esa conclusion seria metodologicamente incorrecta.

### Primera aclaracion

`good` no significa aqui "todo lo suficientemente util". Significa:

- files donde `trades`, `daily` y `1m` quedan casi impecablemente alineados;
- sin conflicto material de escala;
- sin textura microestructural que obligue a flag;
- y sin residuo relevante fuera de los arbitros.

Es una definicion de pureza, no una definicion amplia de utilidad.

### Segunda aclaracion

La propia certificacion historica deja escrito que este bucket es:

- real;
- muy pequeno;
- y sesgado a files diminutos.

En `certification/trades/12_trades_good.md` el `good` historico aparece con:

- `80` files;
- `rows_after_parse` mediano `3.5`;
- `p75 = 17.25`.

Eso cambia la interpretacion del grafico: el bucket `good` no esta fallando porque falten ejemplos limpios escondidos. Esta saliendo pequeno porque el criterio exigido para entrar ahi es extraordinariamente severo.

### Tercera aclaracion

La masa economicamente recuperable de `trades` no debe buscarse dentro de `good`. Debe buscarse sobre todo en:

- `review` rehabilitable bajo regla estricta o extendida;
- subconjuntos utiles de `review_microstructure`;
- `review_1m_reference_alignment`;
- `review_no_1m_reference`;
- y, en el futuro, posibles reconciliaciones validadas de `reference_scale_mismatch`.

Por eso el estado final correcto del bloque no es:

- `good` contra todo lo demas.

El estado final correcto es:

- `good`
- `recoverable_with_flag`
- `review_not_rehabilitated`
- `bad`

La lectura correcta de ese `0.001%` no es "casi todo roto". La lectura correcta es:

- el umbral de pureza para `good` es tan alto que casi toda la masa que todavia puede ser util queda desplazada a buckets recuperables con flag.

### Cuarta aclaracion

La rematerializacion real sobre `57f` muestra que esa masa util no debe inflarse ingenuamente:

- si solo mirabas `57e`, parecia que casi el `86%` de `review` era recuperable en regla estricta;
- al recalcular sobre `57f`, baja a `68.6005%`.

Eso significa que el bloque sigue siendo potencialmente util, pero exige bastante mas prudencia de la que sugeria el parcial historico.

### Quinta aclaracion

La siguiente ronda de evidencia ya no depende de elegir ejemplos a mano. La muestra base sobre `57f` ya esta materializada en:

- [trades_stratified_sample_manifests_v0_1.md](./evidence_assets/stratified_samples/trades_stratified_sample_manifests_v0_1.md)

Conteos seleccionados:

- `review`: `60`
- `reference_scale_mismatch`: `60`
- `review_microstructure`: `60`
- `bad_data`: `60`
- `review_no_1m_reference`: `60`
- `review_1m_reference_alignment`: `60`
- `good`: `106`

Esto responde a:

- con que base reproducible se construiran los futuros packs amplios del inspector;
- como se evita el cherry-picking en familias masivas;
- y por que la etapa siguiente ya debe centrarse en renderizar y explicar casos, no en volver a decidir la muestra.

## 7. Capa poblacional

Dossier:

- [trades_population_readout_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/trades/population_evidence_packs/trades_population_readout_v0_1.md>)

### Que prueba

- cuanto pesa cada label en el estado parcial heredado;
- como se compone el residuo D full;
- y donde se concentra la contaminacion de escala.

### Responde

- cuanta masa hay;
- como se reparte entre familias;
- que buckets dominan el residuo;
- y si la presion principal viene de `bad_data` o de conflicto interpretable.

### No responde

- si un file concreto es recuperable o no;
- si una familia grande debe consumirse sin flags;
- ni si los ejemplos curados bastan para representar toda la poblacion.

### Que decision cambia

La capa poblacional cambia una idea muy peligrosa: impide cerrar `trades` con una logica binaria `good / bad`. Obliga a reconocer una masa intermedia enorme cuya explicacion no es trivial.

### Consecuencia

La consecuencia operativa es que ninguna policy seria puede decidir el consumo de `trades` mirando solo el tamano relativo de `good` y `bad`.

## 8. Capa metodologica file-acceptance

Dossier:

- [trades_file_acceptance_readout_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/trades/file_acceptance_evidence_packs/trades_file_acceptance_readout_v0_1.md>)

### Que prueba

- por que la muestra `380` no es el universo;
- por que esa muestra si sirve para redisenar la taxonomia;
- y por que `reference_scale_mismatch` y `review_microstructure` no deben seguir viviendo dentro de `bad_data` heredado.

### Responde

- que vio el notebook historico al reabrir raw files;
- si las familias candidatas se sostienen mas alla de 2 o 3 ejemplos vistosos;
- y que firmas repite realmente la muestra estratificada.

### No responde

- el tamano exacto del universo final por si sola;
- ni la masa ya rehabilitada sobre `57f`;
- ni la politica final de consumo sin pasar por certificacion.

### Que decision cambia

Esta capa cambia la politica de clasificacion. Sin ella, gran parte de la masa seguiria mal etiquetada como `bad_data` o como `review` sin semantica.

### Consecuencia

La consecuencia institucional es que la taxonomia deja de ser solo contable y pasa a ser causal: distingue comparabilidad, microestructura, falta de arbitro y dano duro real.

## 9. Casos ejemplares por estado

- review / flagged:
  - [trades_review_cases_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/trades/flagged_case_evidence_packs/trades_review_cases_v0_1.md>)
- bad:
  - [trades_bad_cases_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/trades/bad_case_evidence_packs/trades_bad_cases_v0_1.md>)
- good:
  - [trades_good_cases_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/trades/good_justification/trades_good_cases_v0_1.md>)
- casepacks amplios por familia:
  - [family_casepacks_index_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/trades/family_case_evidence_packs/family_casepacks_index_v0_1.md>)

### Como deben leerse

Los case packs no enumeran millones de files. Su funcion es mostrar la firma causal de cada familia:

- que aspecto tiene la escala rota frente a referencia;
- que aspecto tiene un conflicto microestructural recuperable con flag;
- y como se diferencia una cola `bad` real de una mera discrepancia interpretable.

La nueva capa de family casepacks amplia esa lectura sobre una muestra mucho mas grande y reproducible:

- `bad_data`: `60`
- `good`: `106`
- `reference_scale_mismatch`: `60`
- `review`: `60`
- `review_1m_reference_alignment`: `60`
- `review_microstructure`: `60`
- `review_no_1m_reference`: `60`

Responde a:

- como se ve cada familia cuando se deja de depender de 1 o 2 ejemplos historicos;
- si la firma analitica del bucket se sostiene en una muestra defendible;
- y con que base concreta debe leer el inspector la semantica de cada familia.

No responde a:

- la enumeracion completa del universo;
- ni sustituye la exploracion libre del notebook, que sigue siendo la via para abrir casos concretos a demanda.

### Responden

- que aspecto visual y metrico tiene cada familia;
- que pregunta concreta resuelve un caso representativo;
- y que decision institucional cambiaria si ese patron domina una parte grande del bucket.

### No responden

- la masa poblacional completa;
- la tasa final exacta de rehabilitacion;
- ni la verdad total del universo file por file.

### Regla de lectura de familias

El inspector no debe leer una familia como si el nombre del bucket se explicara solo.

En `trades`, cada familia debe interpretarse como una categoria con semantica propia:

- `reference_scale_mismatch`
  - familia de conflicto de escala frente a referencias;
  - no familia de tape roto en bruto.
- `review_microstructure`
  - familia donde el dano vive en la textura fina del tape;
  - no simple error generico de comparacion.
- `review_no_1m_reference`
  - familia donde falta arbitro fino;
  - no prueba de limpieza ni de condena total.
- `review_1m_reference_alignment`
  - familia donde el arbitro `1m` cambia la verdad del caso;
  - no simple residuo menor.
- `bad_data`
  - familia donde el flujo deja de ser economicamente defendible;
  - no solo "casos extremos visualmente feos".
- `good`
  - familia pristine y muy estrecha;
  - no medida amplia de masa util.

La obligacion del dossier no es solo ensenar imagenes. Es traducir cada familia a:

- significado causal;
- consecuencia operativa;
- error metodologico que evita;
- y decision institucional que justifica.

## 10. Consecuencia operativa por pipeline

- ejecucion y microestructura:
  - pueden trabajar sobre `trades_raw`, pero con fuerte dependencia de flags y arbitros;
  - la masa `review` no debe tratarse como flujo limpio.
- backtest_core:
  - no debe consumir `trades_raw` conflictivo como si fuese verdad economica diaria;
  - debe usar otras vistas para se?al y valoracion.
- backtest_extended / forensic research:
  - puede reutilizar fracciones `recoverable_with_flag` cuando la regla y el bucket lo permitan.
- ML microestructural:
  - puede usar parte de esta masa como senal informada o tarea de calidad;
  - no debe aprender `review` conflictivo como si fuera normalidad limpia.
- labels primarios de retorno:
  - no deben depender de `trades_raw` conflictivo como si fuera verdad economica diaria.

### Responde

- que vista puede sostener cada pipeline;
- donde un conflicto de escala rompe reconciliacion pero no necesariamente el raw;
- y donde el dano duro obliga a exclusion completa.

### No responde

- la cuantificacion final de `recoverable_with_flag` sobre `57f`;
- ni el porcentaje exacto de masa util real del bloque.

## 11. Veredicto institucional final

`trades` no debe cerrarse ni como dataset muerto ni como dataset ya rehabilitado por completo.

La lectura institucional correcta es:

- existe una cola `bad` pequena pero real;
- existe una cola `good` semanticamente limpia pero minima;
- y existe una masa enorme de conflicto cuya explicacion dominante es comparabilidad, escala y microestructura, no corrupcion universal del tape.

Eso obliga a un consumo disciplinado, con flags y semantica explicita, pero no obliga a desechar el bloque entero. La excelencia aqui no consiste en negar el dano ni en exagerarlo. Consiste en separarlo correctamente para que cada pipeline consuma solo la vista y el estado que puede sostener metodologicamente.

## 12. Regla de explicacion en la presentacion final

Cuando se presenten resultados de `trades`, no debe mostrarse solo:

- el nombre del bucket;
- el conteo;
- o la formula de rehabilitacion.

Hay que explicar tambien que es cada cosa y a que pregunta responde.

### Minimo explicativo obligatorio

Debe definirse siempre:

- que es `population`;
- que es `case_pack`;
- que es `muestra_380`;
- que es el cache final `57f/full_clean_fast_same_schema`;
- que es `recoverable_with_flag`;
- y que significa cada columna clave usada en la rehabilitacion.

### Columnas que no pueden darse por sabidas

- `daily_vw_to_trade_vw`
  - cociente entre `daily_vw` y `trade_vwap`;
  - responde a si el tape y el arbitro diario viven en la misma escala general.
- `scale_bucket_vw`
  - discretizacion de esa escala;
  - responde a si el caso esta cerca de `1x` o en conflicto de escala.
- `trade_vwap_vs_daily_vw_diff_pct_raw`
  - distancia porcentual entre `trade_vwap` y `daily_vw`;
  - responde a si el promedio economico del tape discrepa de forma material.
- `outside_daily_regular_pct`
  - porcentaje de trades regulares fuera del rango diario;
  - responde a cuanto contradice el tape al arbitro `daily`.
- `outside_1m_regular_pct`
  - porcentaje de trades regulares fuera del arbitro `1m`;
  - responde a cuanto contradice el tape a la estructura fina intradia.

### Regla de lectura

No basta con decir:

- "cumple umbral";
- "no cumple umbral";
- o "esta en review".

Hay que traducirlo siempre a:

- que pregunta responde;
- que error metodologico evita;
- y que decision institucional cambia.
