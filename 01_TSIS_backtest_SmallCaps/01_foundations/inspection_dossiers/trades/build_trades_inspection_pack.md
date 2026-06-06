# `trades` Inspection Pack | Estado actual

## Por que existe este documento

`trades` todavia no estaba, al empezar este bloque, en el mismo estado de dossier de inspeccion que `daily` o `quotes`.

Esta nota deja constancia de:

- donde esta el bloque hoy;
- por que fue necesario pausarlo en varios momentos;
- que evidencia historica ya existe;
- y que tiene que ocurrir antes de considerar cerrado el bloque de forma institucional dentro de `01_foundations`.

## Jerarquia de autoridad historica

La jerarquia correcta para `trades` es:

- `auditoria/trades/v2`
  - para estres poblacional, root cause, muestra metodologica y drill-down tecnico;
- `certification/trades`
  - para semantica final de recuperacion y framing de closeout;
- `certification/global_metrics`
  - para tablas transversales entre bloques, siempre con chequeo de drift si cambian caches o rutas.

## Lo que ya esta claro

En `trades` no deben mezclarse cuatro niveles distintos:

1. snapshot poblacional de estres;
2. taxonomia explicativa y muestra metodologica file-level;
3. labels file-level del cierre full final `57f`;
4. estados finales de certificacion:
   - `good`
   - `recoverable_with_flag`
   - `review_not_rehabilitated`
   - `bad`

El riesgo metodologico principal del bloque es confundir uno de esos niveles con otro.

## Estado mas reciente de `bad_data`

La familia `bad_data` ya no debe presentarse al inspector solo como una coleccion de casos duros.

Ahora queda exigido que su dossier arranque con dos mapas de universo:

1. distribucion final completa de `57f` por `acceptance_label`;
2. composicion interna de `bad_data` por firmas duras de fallo.

Y, ademas, los casos de subfamilia estructural deben incorporar evidencia localizada:

- marcador `X` roja sobre el print con `size <= 0` en el panel superior;
- tabla exacta de filas invalidas con:
  - `timestamp`
  - `price`
  - `size`
  - `exchange`
  - `conditions`
- tabla de grupos duplicados exactos relevantes.

Regla institucional:

- si la causalidad principal vive en la integridad del tape y no en la geometria del precio,
- el panel de precio por si solo no basta;
- el dossier debe anadir evidencia estructural localizada.

## Por que `trades` no podia promoverse de inmediato como `daily`

Porque `trades` toca directamente la infraestructura transversal que primero tuvimos que formalizar:

- semantica de precio;
- comparacion `raw` vs `adjusted`;
- `split_normalized`;
- corporate actions;
- caveats de comparacion contra plataformas externas;
- y policy de price views por pipeline.

Sin esos contratos transversales, un dossier de `trades` habria corrido el mismo riesgo que detecto la auditoria historica:

- tratar cualquier desacuerdo con referencias como si implicara automaticamente `bad tape`.

## Que dicen hoy los notebooks historicos

### `04` dice

- el universo materializado full esta fuertemente tensionado;
- el conflicto contra `daily` y `1m` es grande;
- duplicados y actividad fuera de sesion importan;
- la poblacion no puede tratarse como un residuo pequeno.

### `05` dice

- la muestra metodologica profunda suaviza la lectura ingenua;
- odd-lots y comparabilidad con referencias pesan mucho;
- muchos casos extremos colapsan hacia `reference_scale_mismatch` o `review_microstructure`.

### `06` dice

- el cierre full final sigue dejando una cola real de `bad_data`;
- la muestra metodologica explica bien la logica;
- pero no sustituye la representatividad del cierre completo.

## Como se gestionaban historicamente los ejemplos

El `05_trades_file_acceptance_audit.ipynb` no esta organizado alrededor de un unico widget universal.

Su patron historico es:

- tablas resumen por capa;
- tablas ordenadas de casos;
- previews directos tipo `show_layer1_file_example(...)`;
- plots por capa;
- y markdown interpretativo.

Eso significa que el notebook historico ya era interactivo en la practica, pero por:

- tablas;
- rankings;
- y helpers de preview;

no por un dropdown unico.

## Evidencia visual ya disponible

`certification/trades/img/` ya trae un set muy util de activos promovibles.

### Poblacion / agregado

- `00_current_policy_distribution_from_raw_shards.png`
- `11_d_full_final_bucket_distribution.png`
- `12_d_full_scale_contamination_by_bucket.png`

### Casos representativos por bucket

- `01_reference_scale_mismatch_sga_2009_01_05.png`
- `02_reference_scale_mismatch_lpcn_2014_07_07.png`
- `03_review_microstructure_qrteb_2019_07_24.png`
- `04_review_microstructure_czfs_2022_08_11.png`
- `05_review_1m_reference_alignment_relv_2018_06_07.png`
- `06_review_1m_reference_alignment_metc_2021_03_22.png`
- `07_bad_data_bwl_a_2009_03_26.png`
- `08_bad_data_anda_2012_05_10.png`
- `09_review_no_1m_reference_glbl_2024_09_19.png`
- `10_review_tof_2010_06_21.png`
- `13_good_dmys_2022_09_06.png`
- `14_good_clsn_2016_05_16.png`

Estas imagenes ya no deben tratarse como material accesorio. Forman parte del cierre institucional del bloque.

## Punto de entrada interactivo en `01_foundations`

Ademas de los `.md`, `01_foundations` ahora expone un notebook de inspeccion libre:

- [trades_inspection_notebook_v0_1.ipynb](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/trades/trades_inspection_notebook_v0_1.ipynb>)

Y un selector reusable:

- [trades_case_panel.py](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/inspection/trades/trades_case_panel.py>)

Ademas, la capa poblacional global ya tiene su propio notebook ejecutable:

- [trades_universe_inspection_notebook_v0_1.ipynb](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/trades/trades_universe_inspection_notebook_v0_1.ipynb>)

Y su lectura institucional persistente:

- [trades_global_universe_readout_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/trades/trades_global_universe_readout_v0_1.md>)

y su modulo reusable:

- [trades_universe_panel.py](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/inspection/trades/trades_universe_panel.py>)

La razon es simple:

- el usuario no debe quedar atrapado en el orden fijo de ejemplos de los `.md`;
- debe poder elegir libremente:
  - capa,
  - bucket,
  - y caso;
- usando la evidencia historica ya promovida.

La diferencia entre ambos notebooks debe quedar clara:

- `trades_inspection_notebook_v0_1.ipynb`
  - prioriza evidencia file-level, familias y casos;
- `trades_universe_inspection_notebook_v0_1.ipynb`
  - prioriza universo completo, firmas agregadas y mapas poblacionales.

No compiten entre si. Se complementan.

## Politica de muestreo para los futuros case packs

La politica formal de muestreo ya queda fijada en:

- [trades_sampling_strategy_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/trades/trades_sampling_strategy_v0_1.md>)

Ese documento define:

- cuando usar enumeracion completa;
- cuando usar muestra estratificada;
- y por que variables debe estratificarse cada familia principal.

No debe elegirse la muestra futura a ojo ni por comodidad visual.

## Implicacion inmediata para el cierre de `trades`

Un stack final de inspeccion de `trades` necesita, como minimo:

1. readout poblacional;
2. readout file-acceptance;
3. readout full-closeout;
4. readout de estados finales explicando:
   - `good`
   - `recoverable_with_flag`
   - `review_not_rehabilitated`
   - `bad`
5. case packs representativos para:
   - `reference_scale_mismatch`
   - `review_microstructure`
   - `review_no_1m_reference`
   - `review_1m_reference_alignment`
   - `bad_data`
   - `review` generico
   - y la cola extremadamente estrecha de `good`

Y, ademas, una via de exploracion interactiva donde el usuario escoja ejemplos libremente.

Tambien necesita ya, y queda materializado, una capa poblacional ambiciosa con graficos del universo `57f` tales como:

- distribucion final por `acceptance_label`;
- mezcla anual por label;
- mezcla relativa de `scale_bucket_vw` por label;
- mezcla de firmas duras por label;
- severidad `outside_daily_regular_pct` por label;
- severidad `outside_1m_regular_pct` por label;
- severidad de duplicacion exacta por label;
- severidad de `odd_lot_trade_pct` por label;
- cobertura del arbitro `1m` por label;
- waterfall de rehabilitacion de `review`.

Y, en una segunda capa mas fina:

- `bad_data` por subfamilia visual;
- `review_microstructure` por textura dominante;
- `reference_scale_mismatch` por bucket de escala;
- `review` por severidad interna de rehabilitacion.

Regla para el siguiente agente:

- no reducir la capa global a dos o tres plots heredados del historico;
- y no presentar casos file-level sin un mapa agregado moderno del universo completo.

## Regla obligatoria para las familias de casos

En `trades`, cada familia debe explicarse como una familia semantica real, no como una mera lista de files ni como un nombre tecnico de bucket.

Eso significa que para cada familia el dossier final debe responder, como minimo, a estas preguntas:

1. que representa realmente esa familia;
2. por que esos casos acaban juntos y no en otro bucket;
3. que firma causal o estructural comparten;
4. que error metodologico evita esa separacion;
5. que decision institucional cambia;
6. que pipelines quedan afectados.

Ejemplos de lectura esperada:

- `reference_scale_mismatch`
  - no significa "file raro";
  - significa conflicto de comparabilidad por escala frente a arbitros, distinto de dano intrinseco del tape.
- `review_microstructure`
  - no significa solo "hay review";
  - significa que el conflicto dominante vive en odd-lots, textura del tape o comparabilidad fina.
- `review_no_1m_reference`
  - no significa que el caso este limpio;
  - significa que falta el arbitro fino para cerrar la disputa con precision.
- `review_1m_reference_alignment`
  - no significa simple discrepancia residual;
  - significa que el conflicto aparece precisamente al abrir el arbitro `1m`.
- `bad_data`
  - no significa solo "caso feo";
  - significa frontera semantica donde el tape deja de ser economicamente defendible.
- `good`
  - no significa "masa util total";
  - significa cola pristine extremadamente estricta.

Regla para el siguiente agente:

- no presentar families como taxonomia muda;
- no limitarse a listar atributos o nombres de ficheros;
- y no asumir que el inspector entendera el significado de un bucket por su nombre tecnico.

Cada familia debe quedar explicada como categoria causal, operativa e institucional.

## Marca de pausa actual

A estas alturas, la primera pila institucional de inspeccion ya esta materializada.

El trabajo siguiente ya no parte de cero:

- ya hay readout poblacional;
- ya hay readout file-acceptance;
- ya hay readout final;
- ya hay case packs;
- y ya existe un notebook de inspeccion con selector libre.

Lo que sigue abierto ya no es estructura basica, sino refinamiento:

- enlace mas estricto a caches actuales si vuelven a derivar los counts;
- case packs mas ricos si aparecen nuevas imagenes representativas;
- y regeneracion mas profunda por script cuando no baste con las imagenes historicas promovidas.

## Siguiente paso de mayor valor

El siguiente movimiento fuerte para `trades` no es otra ronda de ejemplos.

Es rematerializar la regla de rehabilitacion sobre:

- `57f/full_clean_fast_same_schema`

Objetivo concreto:

- cuantificar cuanto de la masa actual en `review` pasaria hoy a `recoverable_with_flag`

Por que importa:

- la cola `good` es pristine y muy pequena;
- no mide la masa economicamente util real del bloque;
- la pregunta operativa correcta no es "cuanto `good` existe";
- la pregunta operativa correcta es "cuanto `review` puede rehabilitarse con una regla explicita y defendible".

Instruccion para el siguiente agente:

- no reutilizar sin mas los counts historicos de rehabilitacion sobre `57e/full_clean`;
- rematerializar la regla sobre `57f/full_clean_fast_same_schema`;
- y promover el resultado a `01_foundations` como parte del cierre institucional real de `trades`.

Despues de eso, el siguiente movimiento sera aplicar la politica de muestreo por familia para construir packs mas amplios y no depender solo de la evidencia historica ya promovida.

## Estado actual de la muestra estratificada sobre `57f`

Ese paso ya esta materializado en:

- [trades_stratified_sample_manifests_v0_1.md](./evidence_assets/stratified_samples/trades_stratified_sample_manifests_v0_1.md)

Y en los manifests reproducibles por familia dentro de:

- `evidence_assets/stratified_samples/`

Conteos seleccionados:

- `review`: `60`
- `reference_scale_mismatch`: `60`
- `review_microstructure`: `60`
- `bad_data`: `60`
- `review_no_1m_reference`: `60`
- `review_1m_reference_alignment`: `60`
- `good`: `106` (enumeracion completa)

Que responde esta capa nueva:

- como traducir la politica de muestreo a artefactos reproducibles;
- que conjunto debe usarse para los futuros `.md` ampliados y exports del inspector;
- y por que la seleccion ya no depende de ejemplos a dedo.

Que no responde:

- aun no renderiza todas las imagenes ricas por caso;
- ni sustituye el notebook interactivo, que sigue siendo el punto de exploracion libre.

Consecuencia:

- la siguiente etapa ya no debe rediscutir la muestra;
- debe reutilizar estos manifests para exportar muchos ejemplos por familia con panel rico y lectura analitica.

## Estado actual de los casepacks amplios por familia

La siguiente etapa ya esta ejecutada. Existe un export amplio por familia en:

- [family_casepacks_index_v0_1.md](./family_case_evidence_packs/family_casepacks_index_v0_1.md)

Conteos finales exportados:

- `bad_data`: `60`
- `good`: `106`
- `reference_scale_mismatch`: `60`
- `review`: `60`
- `review_1m_reference_alignment`: `60`
- `review_microstructure`: `60`
- `review_no_1m_reference`: `60`

Que responde esta capa:

- como se ve una muestra amplia y defendible de cada familia;
- como cambia la lectura cuando se dejan de usar solo 1 o 2 ejemplos bonitos;
- y con que base concreta debe leer el inspector la semantica de cada familia.

Que no responde:

- aun no agota el universo completo de cada bucket;
- ni sustituye la exploracion libre del notebook.

Consecuencia:

- `trades` ya tiene, ademas del notebook y de los ejemplos historicos, una capa exportada amplia por familia;
- la etapa siguiente ya no es crear mas scaffolding, sino revisar si algun bucket necesita otra vuelta de analisis o render mas especializado.

## Regla para la siguiente etapa

Nadie debe construir el cierre final de `trades` usando solo las salidas viejas del notebook.

La siguiente etapa debe pasar por:

- `trades_dataset_contract_v0_1.md`
- `trades_label_taxonomy_and_cut_policy.md`
- `trades_consumption_policy.md`
- `trades_schema_contract.md`
- `trades_validators.md`

El notebook de inspeccion y el selector libre complementan esos contratos. No los sustituyen.
## Estado interactivo actual

La capa `muestra_380` del notebook y del selector ya no debe leerse como preview tabular pobre.

Ahora su funcion es:

- abrir cualquier caso de la muestra metodologica de `380` files;
- dibujar un panel rico con:
  - `trades raw`,
  - arbitro `daily`,
  - arbitro `1m`,
  - y concentracion temporal del conflicto;
- explicar que familia representa el caso;
- y responder que decision cambiaria si ese patron dominara una fraccion grande del bucket.

La distincion con `population` y `case_pack` se mantiene por semantica de evidencia, no por pobreza visual:

- `population`: evidencia agregada;
- `case_pack`: evidencia curada;
- `muestra_380`: evidencia metodologica file-level con panel comparable.

## Regla de presentacion obligatoria

Cuando se presenten resultados de `trades`, no puede asumirse que el lector ya sabe que significa cada capa o cada metrica.

Debe explicarse siempre, de forma explicita:

- que es `population`;
- que es `case_pack`;
- que es `muestra_380`;
- que es el cierre full `57f/full_clean_fast_same_schema`;
- que significa la politica de rehabilitacion;
- y que significa cada columna clave usada en esa rehabilitacion.

En particular, al presentar la rehabilitacion de `review`, hay que definir en lenguaje llano:

- `daily_vw_to_trade_vw`
  - cociente entre `daily_vw` y `trade_vwap`;
  - responde a si tape y arbitro diario viven en la misma escala general.
- `scale_bucket_vw`
  - bucket discreto derivado de `daily_vw_to_trade_vw`;
  - responde a si el caso esta cerca de `1x`, muy lejos o en escala extrema.
- `trade_vwap_vs_daily_vw_diff_pct_raw`
  - distancia porcentual entre `trade_vwap` y `daily_vw`;
  - responde a si el promedio economico del tape discrepa materialmente del arbitro diario.
- `outside_daily_regular_pct`
  - porcentaje de trades regulares fuera del rango diario;
  - responde a cuanto contradice el tape al arbitro `daily`.
- `outside_1m_regular_pct`
  - porcentaje de trades regulares fuera del arbitro `1m`;
  - responde a cuanto contradice el tape a la estructura intradia fina.

La regla de estilo es:

- no solo decir el nombre de la metrica;
- no solo dar el umbral;
- sino explicar que pregunta responde y que decision cambia.

## Rematerializacion actual de la rehabilitacion sobre `57f`

Ya no dependemos solo del resultado historico parcial de `57e/full_clean`.

Sobre el cache canonico real:

- `runs/backtest/trades_v2_materialized/trades_current_cd_merged/root_cause_exports/file_acceptance_cache_lt1b_full_clean_fast_same_schema`

la regla de rehabilitacion para el bucket `review` se ha rematerializado asi:

### Regla estricta

Debe cumplir todo:

- `scale_bucket_vw` en `{~1x, near_1x}`
- `trade_vwap_vs_daily_vw_diff_pct_raw <= 0.5`
- `outside_daily_regular_pct <= 1`
- `outside_1m_regular_pct <= 15`

Resultado actual sobre `57f`:

- `review_total = 4,851,211`
- `review_recoverable_strict = 3,327,955`
- `review_recoverable_strict_pct = 68.6005%`
- `review_not_rehabilitated_strict = 1,523,256`

### Regla extendida

Debe cumplir todo:

- `scale_bucket_vw` en `{~1x, near_1x}`
- `trade_vwap_vs_daily_vw_diff_pct_raw <= 1.0`
- `outside_daily_regular_pct <= 2`
- `outside_1m_regular_pct <= 20`

Resultado actual sobre `57f`:

- `review_recoverable_extended = 3,505,290`
- `review_recoverable_extended_pct = 72.2560%`
- `review_not_rehabilitated_extended = 1,345,921`

## Lectura institucional del cambio frente a `57e`

Historicamente, sobre `57e/full_clean`, la regla estricta absorbia `85.89%` del bucket `review`.

En el cache final real `57f`, la misma regla absorbe `68.6005%`.

Eso cambia la lectura del bloque:

- la intuicion historica de que `review` era mayoritariamente rehabilitable sigue siendo cierta;
- pero lo es bastante menos de lo que sugeria el parcial `57e`;
- y por tanto la masa `review_not_rehabilitated` final es mucho mas grande de lo que parecia en la version parcial.

Esto obliga a no presentar el resultado de `57e` como si fuese ya el cierre operativo del bloque.

## Recuperacion provisional adicional sobre `57f`

Ademas del bucket `review` generico, se ha cuantificado una primera recuperacion provisional para dos familias que `certification` ya declaraba parcialmente recuperables segun uso:

- `review_microstructure`
- `review_1m_reference_alignment`

### `review_microstructure`

La semantica historica del bucket dice:

- no es escala rara;
- no es tape grotescamente roto;
- el dano vive en la textura microestructural;
- y parte del bucket puede ser util con `flag`.

Para bajarlo a conteo operativo sobre `57f`, se usa una regla provisional estricta:

- `scale_bucket_vw` en `{~1x, near_1x}`
- `trade_vwap_vs_daily_vw_diff_pct_raw <= 1.0`
- `core_outside_daily_pct <= 1`
- `core_outside_1m_pct <= 1`

Resultado:

- `review_microstructure_total = 2,130,781`
- `review_microstructure_recoverable_strict_provisional = 1,516,547`
- `review_microstructure_recoverable_strict_pct = 71.1733%`

Sensibilidad extendida:

- `trade_vwap_vs_daily_vw_diff_pct_raw <= 2.0`
- `core_outside_daily_pct <= 2`
- `core_outside_1m_pct <= 2`

Resultado:

- `review_microstructure_recoverable_extended_provisional = 1,636,379`
- `review_microstructure_recoverable_extended_pct = 76.7971%`

### `review_1m_reference_alignment`

La semantica historica del bucket dice:

- `daily` parece razonable;
- la tension real aparece frente a `1m`;
- y por eso existe una recuperacion limitada, no plena.

Para cuantificarlo sobre `57f`, se usa una regla provisional estricta:

- `scale_bucket_vw` en `{~1x, near_1x}`
- `trade_vwap_vs_daily_vw_diff_pct_raw <= 1.0`
- `core_outside_daily_pct <= 1`
- `core_outside_daily_volume_pct <= 1`

Resultado:

- `review_1m_reference_alignment_total = 4,992`
- `review_1m_reference_alignment_recoverable_strict_provisional = 2,591`
- `review_1m_reference_alignment_recoverable_strict_pct = 51.9030%`

Sensibilidad extendida:

- `trade_vwap_vs_daily_vw_diff_pct_raw <= 2.0`
- `core_outside_daily_pct <= 2`
- `core_outside_daily_volume_pct <= 2`

Resultado:

- `review_1m_reference_alignment_recoverable_extended_provisional = 3,715`
- `review_1m_reference_alignment_recoverable_extended_pct = 74.4191%`

## Regla de interpretacion

Estos numeros no deben presentarse como si fueran una regla historica tan oficial y cerrada como la de `review` generico.

Deben presentarse como:

- cuantificacion operativa provisional;
- anclada en la semantica historica de `certification`;
- y util para estimar masa util real por familia mientras se formaliza una regla final mas completa.

## Subfamilias visuales dentro de `bad_data`

La familia `bad_data` no es visualmente homogenea.

Hoy ya sabemos, sobre el cierre real `57f`, que contiene al menos dos subfamilias principales:

### 1. Colapso de escala o de rango frente a arbitros

Firma dominante:

- `trade_price_outside_daily_range`
- `scale_bucket_vw = nan`
- `outside_daily_regular_pct = 100%` o muy alto
- `outside_1m_regular_pct = 100%` o muy alto

Lectura visual:

- el panel de precio actual si funciona bien;
- los arbitros `daily` y `1m` viven en una escala absurda frente al tape raw;
- o el tape colapsa cerca de cero mientras los arbitros quedan muy arriba.

Conteo observado en `57f`:

- `scale_bucket_vw = nan`: `4,247` (`26.76%` del bucket `bad_data`)
- `outside_daily_regular_pct = 100%`: `5,707` (`35.96%`)
- `outside_1m_regular_pct = 100%`: `4,910` (`30.94%`)
- `trade_price_outside_daily_range` en `issues_list`: `9,606` (`60.53%`)

### 2. Corrupcion de integridad estructural del tape

Firma dominante:

- `negative_or_zero_size_rows`
- duplicacion excesiva
- o rows invalidos con precio aparentemente casi normal

Lectura visual:

- el panel de precio actual no siempre funciona;
- puede parecer que el caso "no grita";
- y sin embargo el file sigue siendo `bad_data` porque la integridad basica del tape ya esta rota.

Conteo observado en `57f`:

- `negative_or_zero_size_rows` en `issues_list`: `695` (`4.38%`)
- `duplicate_excess_ratio_gt_hard_cap` en `issues_list`: `1,329` (`8.37%`)
- componente estructural sin `trade_price_outside_daily_range`: `204` (`1.29%`)
- componente estructural mezclado con conflicto de rango: `491` (`3.09%`)

### Consecuencia metodologica

El panel rico actual:

- es suficiente para `bad_data` de colapso de escala/rango;
- pero es insuficiente para una parte de `bad_data` de integridad estructural.

Regla para el siguiente refinamiento:

- no volver a tratar `bad_data` como una unica familia visual;
- distinguir siempre entre `bad_data` de escala/rango y `bad_data` de integridad del tape;
- y anadir una visualizacion complementaria de integridad cuando el problema principal no viva en la trayectoria de precio.

Implementacion ya aplicada:

- cuando existe `size <= 0`,
- el panel superior marca esa fila con una `X` roja,
- para que el inspector no solo vea el conteo agregado sino la localizacion visual de la fila invalida dentro del tape.
