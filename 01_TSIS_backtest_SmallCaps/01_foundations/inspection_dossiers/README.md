# Inspection Dossiers

## Menu

- [Rol de esta carpeta](#rol-de-esta-carpeta)
- [Que es un inspection dossier](#que-es-un-inspection-dossier)
- [Que no es esta carpeta](#que-no-es-esta-carpeta)
- [Tipos de artefactos](#tipos-de-artefactos)
  - [Notebooks](#notebooks)
  - [Scripts o builders](#scripts-o-builders)
  - [Markdown institucional](#markdown-institucional)
- [Estructura esperada por dataset](#estructura-esperada-por-dataset)
- [Readout principal](#readout-principal)
- [Good justification](#good-justification)
- [Flagged case evidence packs](#flagged-case-evidence-packs)
- [Bad case evidence packs](#bad-case-evidence-packs)
- [Coverage case evidence packs](#coverage-case-evidence-packs)
- [Evidence assets](#evidence-assets)
- [Orden Visual Obligatorio](#orden-visual-obligatorio)
- [Regla obligatoria por evidencia](#regla-obligatoria-por-evidencia)
- [Lectura visual real](#lectura-visual-real)
- [Masa poblacional vs casos forenses](#masa-poblacional-vs-casos-forenses)
- [Rehabilitacion](#rehabilitacion)
- [Capas derivadas y promocion](#capas-derivadas-y-promocion)
- [Diferencias por bloque actual](#diferencias-por-bloque-actual)
  - [Daily](#daily)
  - [Quotes](#quotes)
  - [Trades](#trades)
  - [Minute / ohlcv_1m raw](#minute--ohlcv1m-raw)
  - [1m split normalized](#1m-split-normalized)
  - [Intraday regime features](#intraday-regime-features)
  - [Reference](#reference)
  - [Halts](#halts)
- [Additional, short y otros bloques](#additional-short-y-otros-bloques)
- [Flujo recomendado de trabajo](#flujo-recomendado-de-trabajo)
- [Paquete Inspector Profundo](#paquete-inspector-profundo) Para humanos
  - [Orden general obligatorio](#orden-general-obligatorio)
  - [`daily`](#daily-1)
  - [`quotes`](#quotes-1)
  - [`trades`](#trades-1)
  - [`minute` / `ohlcv_1m` raw](#minute--ohlcv_1m-raw-1)
- [Criterios de cierre](#criterios-de-cierre)
- [Madurez relativa de dossiers](#madurez-relativa-de-dossiers)
  - [Estado por bloque a 2026-06-07](#estado-por-bloque-a-2026-06-07)
    - [`daily`](#daily-2)
    - [`quotes`](#quotes-2)
    - [`trades`](#trades-2)
    - [`minute` / `ohlcv_1m` raw](#minute--ohlcv1m-raw-1)
    - [`1m_split_normalized`](#1msplitnormalized)
    - [`intraday_regime_features`](#intradayregimefeatures)
    - [`reference`](#reference-1)
    - [`halts`](#halts-1)
    - [`additional`](#additional)
    - [`short`](#short)
  - [Regla de mantenimiento](#regla-de-mantenimiento)
- [Regla de higiene](#regla-de-higiene)
- [Relacion con `01_research`](#relacion-con-01research)
- [Regla final](#regla-final)


## Rol de esta carpeta

`inspection_dossiers/` contiene la capa de lectura humana e inspeccion institucional de los datasets y bloques auditados del modulo 01.

Su funcion no es definir contratos nuevos desde cero.

Su funcion es hacer inspeccionable la evidencia que sostiene esos contratos.

La autoridad metodologica principal vive en:

- `01_foundations/module_contracts/inspection_dossier_model.md`
- `01_foundations/module_contracts/evidence_model.md`
- `01_foundations/module_contracts/bad_evidence_and_rehabilitation.md`
- `01_foundations/module_contracts/layer_validation_standard_v0_1.md`
- `AGENTS.md`, seccion de inspeccion y evidencia visual

Este README actua como mapa operativo de la carpeta. Resume como usarla, que debe contener cada dossier y como evitar duplicar, reinterpretar o degradar evidencia ya institucionalizada.

## Que es un inspection dossier

Un `inspection dossier` es la unidad documental que permite a un humano, agente o revisor entender por que un dataset, capa o bloque queda aceptado, condicionado, en revision, rechazado o promovido.

La cadena correcta es:

```text
evidencia historica preservada
-> artefactos reproducibles de inspeccion
-> inspection readout
-> contrato institucional / policy / registry / validator
```

El dossier no sustituye:

- un schema canonico;
- un dataset contract;
- una data consumption policy;
- un validator;
- una registry entry;
- ni la evidencia historica original.

El contrato dice que vale.

El dossier muestra por que vale.

Los assets permiten comprobarlo.

## Que no es esta carpeta

Esta carpeta no es:

- un vertedero de notebooks;
- un lugar para dejar imagenes huerfanas;
- una zona de outputs temporales;
- una copia del arbol historico de `01_research`;
- ni una fuente paralela de verdad que contradiga contratos.

Si una conclusion estable sale de un notebook, debe quedar encapsulada aqui como readout, case pack, asset trazable o referencia institucional. El notebook puede seguir siendo evidencia historica, pero no debe ser la unica forma de entender el cierre.

## Tipos de artefactos

### Notebooks

Sirven para:

- exploracion;
- diagnostico;
- apertura de casos;
- inspeccion interactiva;
- generacion inicial de tablas e imagenes;
- prueba de hipotesis;
- rehabilitaciones;
- y revision visual.

Un notebook puede ser evidencia valida, pero una decision estable no debe depender de memoria conversacional ni de abrir manualmente un notebook sin lectura institucional.

### Scripts o builders

Sirven para:

- reproducir evidence packs;
- exportar tablas;
- generar imagenes estables;
- materializar readouts repetibles;
- construir manifests;
- y reducir dependencia de ejecucion manual.

Cuando el formato esta maduro, debe preferirse un builder reproducible frente a una operacion manual.

### Markdown institucional

Sirve para:

- fijar la interpretacion;
- presentar el resultado a inspeccion humana;
- enlazar evidencia persistida;
- incrustar evidencia visual clave;
- declarar limites;
- y cerrar la decision operacional.

Un markdown institucional no debe ser solo narrativo. Debe apuntar a evidencia concreta.

## Estructura esperada por dataset

Cuando aplique, un dataset o bloque deberia converger hacia una estructura similar a:

```text
01_foundations/inspection_dossiers/<dataset>/
  <dataset>_inspection_readout_v0_1.md
  population_visual_overview/
  good_justification/
  flagged_case_evidence_packs/
  bad_case_evidence_packs/
  coverage_case_evidence_packs/
  evidence_assets/
  build_<dataset>_inspection_pack.md
```

La estructura exacta puede variar si el dataset lo exige, pero la logica debe quedar clara:

- readout principal;
- mapa visual poblacional cuando el bloque tenga masa o complejidad suficiente;
- evidencia de casos buenos;
- evidencia de casos condicionados o en revision;
- evidencia de casos malos;
- evidencia de cobertura cuando aplique;
- assets persistidos;
- y mecanismo o nota de construccion.

## Readout principal

El `inspection_readout` es el documento de entrada para el lector humano.

Debe responder como minimo:

- cual es el veredicto del bloque;
- que estados existen;
- que parte es `good`;
- que parte queda `flagged`, `review`, `recoverable` o equivalente;
- que parte queda `bad`;
- que evidencia visual o tabular soporta esas decisiones;
- que consumidores pueden usar el dataset;
- que limites siguen abiertos;
- que puede reabrirse o rehabilitarse;
- y donde estan los contratos, policies, schemas, validators o registry entries relacionados.

No debe copiar toda la auditoria historica.

Debe resumirla, enlazarla y convertirla en una lectura inspeccionable.

## Good justification

`good_justification/` documenta por que una familia, bucket, muestra o porcion del dataset puede tratarse como apta.

No todo `good` necesita evidencia por file, pero si necesita justificacion institucional.

Debe explicar:

- que entra en `good`;
- por que entra;
- que estadistica agregada lo sostiene;
- que ejemplos representativos lo muestran;
- que residuo queda;
- y por que ese residuo no invalida el consumo permitido.

## Flagged case evidence packs

`flagged_case_evidence_packs/` aplica a estados como:

- `review`;
- `recoverable_with_flag`;
- `review_not_rehabilitated`;
- `ml_flagged`;
- o equivalentes.

Debe explicar:

- por que esos casos no son `good`;
- por que no necesariamente son `bad`;
- que condicion o flag exigen;
- que consumidores pueden usarlos;
- que consumidores no deben usarlos;
- y que error metodologico evita mantenerlos separados.

## Bad case evidence packs

`bad_case_evidence_packs/` aplica a casos excluidos, rechazados o no aptos para consumo productivo.

Debe seguir el protocolo de:

- `01_foundations/module_contracts/bad_evidence_and_rehabilitation.md`

Un caso `bad` no puede quedar definido solo por una flag tecnica.

Debe tener, cuando aplique:

- identidad exacta del caso;
- dataset afectado;
- motivo primario de exclusion;
- bucket causal;
- evidencia estructural o numerica;
- evidencia visual si el fenomeno es visible;
- explicacion logica;
- evaluacion de rehabilitacion;
- y estado final de cierre.

Estados tipicos:

- `bad_confirmed`;
- `bad_recoverable_rejected`;
- `bad_rehabilitated_with_flag`;
- `bad_reclassified`.

Regla critica: no debe consumirse en backtest o ML como mercado real un artefacto que solo existe por problema de fuente, transformacion, duplicacion, escala o integridad.

## Coverage case evidence packs

`coverage_case_evidence_packs/` aplica cuando el problema principal no es la calidad puntual del dato, sino:

- cobertura;
- continuidad;
- frontera temporal;
- universo esperado;
- gaps;
- actividad no esperada;
- ausencia de files;
- o desalineacion entre datasets.

Esta capa es especialmente importante en:

- `daily`;
- `quotes`;
- `trades`;
- `ohlcv_1m`;
- y capas full-universe.

La cobertura no debe colapsarse automaticamente a `good` o `bad`.

Un gap puede ser:

- esperado;
- recuperable sin penalizacion;
- recuperable con flag;
- ambiguo;
- o realmente problematico.

El dossier debe decir cual es el caso y por que.

## Evidence assets

`evidence_assets/` contiene los artefactos persistidos que sostienen la lectura:

- imagenes;
- CSV;
- parquet;
- manifests;
- tablas resumen;
- muestras estratificadas;
- exports por ticker/date/file;
- auditorias auxiliares;
- y material reusable por notebooks o readouts.

Los assets deben ser:

- trazables;
- enlazables;
- reusables;
- y consumidos por algun readout, case pack, notebook o contrato.

Un asset sin consumidor claro es ruido operacional, salvo que este explicitamente archivado como evidencia historica.

## Orden Visual Obligatorio

Los dossiers de inspeccion humana deben progresar de lo general a lo particular.

La secuencia correcta es:

```text
mapa poblacional visual
-> distribuciones y masas por estado/familia
-> coverage/universo esperado
-> familias de evidencia
-> casos individuales
-> decision de consumo
```

Regla:

- no empezar por ticker, file o caso individual si todavia no existe una vision general del universo;
- no sustituir estadisticas generales por una muestra visual bonita;
- no sustituir casos individuales por graficos agregados;
- no dejar visuales generales encerrados solo en notebooks si son necesarios para el inspector;
- exportar PNGs estables e incrustarlos en markdown cuando el dossier vaya a lectura humana final.

Cada visual general debe seguir tambien:

```text
Que muestra
Responde
No responde
Consecuencia
```

Ejemplos concretos:

- `trades` necesita mapa poblacional antes de familias file-level;
- `daily` necesita quality y coverage antes de ejemplos;
- `quotes` necesita politica global y auditoria de casepacks antes de eventos;
- `minute` necesita core/vw, coverage, schema-only y familias antes de ticker-month;
- una capa derivada como `1m_split_normalized` necesita mapa de universo/auditoria/coverage antes de ejemplos de splits.

## Regla obligatoria por evidencia

Toda pieza relevante de evidencia debe explicar:

```text
Que muestra
Responde
No responde
Consecuencia
```

Esto aplica a:

- graficos;
- tablas;
- ejemplos;
- familias de casos;
- panels visuales;
- manifests;
- y capas de evidencia agregada.

No basta con describir la imagen.

No basta con listar nombres de buckets.

No basta con decir que un caso es raro, bueno o malo.

La evidencia debe declarar que pregunta contesta, que pregunta no contesta y que decision cambia.

## Lectura visual real

La explicacion de una imagen debe salir de la lectura visual real de la imagen, no solo del nombre del bucket ni de una plantilla.

Debe decir, cuando aplique:

- donde se ve exactamente el problema;
- si el problema vive en precio, escala, rango, tiempo, volumen o integridad estructural;
- si el panel demuestra la causa del rechazo;
- si el panel solo muestra una consecuencia parcial;
- y si hace falta evidencia complementaria.

Si el motivo real no se ve bien en la imagen, el dossier debe decirlo.

Si un caso es `bad_data` por integridad estructural, pero la imagen solo ensena una trayectoria de precio normal, esa imagen no basta. Deben existir tablas o panels adicionales con filas invalidas, duplicados, sizes, timestamps u otra evidencia causal.

## Masa poblacional vs casos forenses

Los dossiers no deben confundir:

- masa poblacional total;
- taxonomia de buckets;
- muestra metodologica;
- casos forenses;
- y estado final de consumo.

Una muestra de casos no sustituye un conteo poblacional.

Un conteo poblacional no sustituye una explicacion visual de familias abiertas.

Ambas capas deben estar conectadas.

## Rehabilitacion

Antes de cerrar un caso como `bad`, debe evaluarse si existe rehabilitacion defendible.

La rehabilitacion puede implicar:

- reclasificacion;
- uso restringido;
- flag explicita;
- rechazo final;
- o exclusion permanente.

La regla institucional es no convertir automaticamente un fallo tecnico en descarte final sin explicar si habia o no habia via de recuperacion.

## Capas derivadas y promocion

Cuando el dossier trate una capa derivada, normalizada o materializada, debe respetar:

- `01_foundations/module_contracts/layer_validation_standard_v0_1.md`

Una capa no queda validada solo porque:

- el script corrio;
- existen parquets;
- algunos casos se ven bien;
- o un piloto tuvo buena pinta.

Debe quedar claro su nivel de madurez:

- definida;
- implementada;
- pilotada;
- auditada;
- consumida;
- promovida.

Hasta que no exista evidencia full-universe o de consumidor real, no debe presentarse como capa cerrada para uso productivo amplio.

## Diferencias por bloque actual

### Daily

`daily` separa dos ejes:

- calidad del bar;
- coverage.

Su dossier no puede limitarse a `good / flagged / bad` de calidad. Tambien debe explicar gaps, recovery y cobertura.

Referencias locales:

- `daily/build_daily_inspection_pack.md`
- `daily/daily_inspection_readout_v0_1.md`
- `daily/coverage_case_evidence_packs/`
- `daily/daily_adjusted_full_universe_audit_v0_1.md`

### Quotes

`quotes` separa:

- calidad local del libro;
- explicacion causal externa;
- severidad economica;
- crossed/locked behavior;
- y contexto externo.

Un evento puede estar explicado por contexto externo y aun asi no quedar rehabilitado como libro limpio.

Referencias locales:

- `quotes/build_quotes_inspection_pack.md`
- `quotes/quotes_inspection_readout_v0_1.md`
- `quotes/good_justification/`
- `quotes/flagged_case_evidence_packs/`
- `quotes/bad_case_evidence_packs/`

### Trades

`trades` separa muchos planos que no deben mezclarse:

- snapshot poblacional de estres;
- taxonomia explicativa;
- muestra metodologica;
- closeout full;
- estados finales;
- familias semanticas;
- casos file-level;
- y evidencia estructural de integridad del tape.

Es uno de los bloques donde mas peligro hay de confundir sample, universo, bucket y decision final.

Referencias locales:

- `trades/build_trades_inspection_pack.md`
- `trades/trades_inspection_readout_v0_1.md`
- `trades/trades_global_universe_readout_v0_1.md`
- `trades/trades_sampling_strategy_v0_1.md`
- `trades/family_case_evidence_packs/`

### Minute / ohlcv_1m raw

El bloque `minute` documenta principalmente estado y closeout del `ohlcv_1m` raw en alcance `<1B>` y validaciones schema-only.

Debe distinguirse de `ohlcv_1m_split_normalized`.

Referencias locales:

- `minute/raw_1m_lt1b_closeout_recalculation_v0_1.md`
- `minute/raw_1m_schema_only_lt1b_inspection_readout_v0_1.md`
- `minute/minute_00_universe_quality_overview_v0_1.ipynb`
- `minute/minute_01_core_quality_model_v0_1.ipynb`
- `minute/minute_02_core_quality_population_readout_v0_1.ipynb`
- `minute/minute_03_casepack_builder_v0_1.ipynb`
- `minute/minute_04_ticker_month_inspector_v0_1.ipynb`
- `minute/minute_05_final_readout_v0_1.ipynb`
- `minute/core_quality_case_evidence_packs/minute_core_quality_visual_cases_v0_1.md`

La lectura moderna separa:

- calidad core OHLCV;
- calidad `vw_*`;
- estado combinado;
- y consumo permitido.

Esta separacion es obligatoria porque una gran parte del universo puede ser defendible para investigacion controlada de OHLCV sin `vw`, mientras `vw` sigue siendo una deuda dominante.

### 1m split normalized

`1m_split_normalized` es una capa derivada. Su dossier debe leerse con el estandar de validacion de capas.

Debe distinguir:

- piloto;
- auditoria full-universe de eventos split auditables;
- validacion semantica;
- controles negativos;
- consumo real;
- promocion;
- y materializacion fisica full-universe, que no es lo mismo que auditoria full-universe de eventos.

Referencias locales:

- `1m_split_normalized/README.md`
- `1m_split_normalized/ohlcv_1m_split_normalized_pilot_readout_v0_1.md`
- `1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1.md`
- `1m_split_normalized/ohlcv_1m_split_normalized_final_readout_v0_1.md`
- `1m_split_normalized/event_case_evidence_packs/ohlcv_1m_split_normalized_visual_inspector_pack_v0_1.md`

### Intraday regime features

`intraday_regime_features` no debe leerse como sustituto de normalizacion de precios.

Es una capa de features/contexto que depende de datos ya normalizados y de una semantica de precio clara.

Su dossier debe explicar:

- que preguntas de contexto contesta;
- que no contesta;
- que consumidores puede habilitar;
- y en que punto de madurez esta.

Referencia local:

- `intraday_regime_features/intraday_regime_features_semantic_pilot_readout_v0_1.md`

### Reference

`reference` documenta identidad, eventos, corporate actions y metadata upstream.

Referencias locales:

- `reference/README.md`
- `reference/reference_institutional_closeout_v0_1.md`
- `reference/reference_modernization_gap_audit_2026-06-12.md`

Debe distinguir:

- metadata e identidad;
- corporate actions;
- eventos de continuidad;
- overlays causales;
- price-view support;
- y consumidores restringidos.

No debe tratarse como precio, tape, universe final ni feature productiva por defecto.

### Halts

`halts` documenta eventos oficiales de halt/suspension y contexto regulatorio.

Referencias locales:

- `halts/README.md`
- `halts/build_halts_inspection_pack.md`
- `halts/halts_inspection_readout_v0_1.md`
- `halts/halts_casepacks_traceability_audit_v0_1.md`
- `halts/integration_notes.md`

Debe distinguir:

- evento oficial intradia;
- evento date-level;
- contexto SEC/regulatorio;
- review parcial de identidad;
- overlay visual contra `quotes` y `trades`;
- coverage frente al universo `<1B>`;
- y consumidores restringidos.

No debe tratarse como precio, tape, alpha, execution truth ni prueba de mercado limpio por ausencia de evento.

### Additional, short y otros bloques

Los bloques como `additional`, `short` o `short_review` pueden tener closeouts institucionales mas compactos si su naturaleza no exige case packs visuales equivalentes a `quotes`, `trades` o `daily`.

Aun asi, deben declarar:

- que datasets cubren;
- que evidencia se reviso;
- que schema/contract/policy queda asociado;
- y si el consumo queda permitido, restringido o no recomendado.

## Flujo recomendado de trabajo

Antes de crear o actualizar un dossier:

1. Leer los contratos rectores aplicables.
2. Identificar el dataset, capa o bloque exacto.
3. Identificar si es raw, adjusted, split-normalized, derived feature, label o registry/universe.
4. Inventariar evidencia historica preservada.
5. Separar masa poblacional, taxonomia, casos forenses y decision final.
6. Determinar que preguntas debe responder el dossier.
7. Reusar assets existentes cuando sean validos.
8. Generar assets nuevos solo si cubren una pregunta no respondida.
9. Escribir readout y case packs con `Que muestra / Responde / No responde / Consecuencia`.
10. Enlazar schemas, contracts, policies, validators y registry entries.
11. Eliminar o archivar outputs transitorios no consumidos.
12. Registrar el cambio si tiene impacto institucional.

## Paquete Inspector Profundo

Fecha de referencia: 2026-06-07.

Esta seccion indica que markdowns y notebooks debe abrir un inspector humano para comprender en profundidad los bloques con mayor evidencia institucional activa:

- `daily`
- `quotes`
- `trades`
- `minute` / `ohlcv_1m` raw

No sustituye contratos, policies, validators ni registry entries. Es una guia de lectura para inspeccion humana profunda: primero contexto y veredicto, despues evidencia visual, poblacional o interactiva por familia.

### Orden general obligatorio

Antes de entrar en un bloque concreto, abrir:

- `01_foundations/inspection_dossiers/README.md`

Motivo:

- fija el modelo comun de inspection dossiers;
- explica madurez relativa;
- separa readouts, casepacks, assets y contratos;
- y evita comparar bloques por numero bruto de imagenes.

### `daily`

Objetivo de inspeccion:

- entender calidad de barra diaria;
- entender coverage;
- distinguir `ohlcv_daily` de `ohlcv_daily_adjusted`;
- y no colapsar `daily` en un binario `good / bad`.

Orden de lectura:

1. `daily/README.md`

   Entrada local del bloque. Explica la diferencia entre `daily_core_v0_1` y `daily_adjusted_v0_1`, la separacion `quality axis` / `coverage axis`, el estado full-universe promovido de `daily_adjusted` y el rol de cada subcarpeta.

2. `daily/daily_inspection_readout_v0_1.md`

   Readout institucional principal. Resume veredicto, estados, consumidores, quality axis, coverage axis y cierre operativo de `daily`.

3. `daily/bad_case_evidence_packs/daily_hard_invalid_cases_v0_1.md`

   Dossier visual de la cola dura `bad`. Contiene los casos `hard_invalid_parse_or_price` con imagen incrustada. Debe abrirse para entender donde termina la defendibilidad de una barra diaria como mercado.

4. `daily/flagged_case_evidence_packs/daily_non_good_quality_cases_v0_1.md`

   Dossier visual de los casos `non_good_quality` / `recoverable_with_flag`. Debe abrirse para entender por que ciertas barras no son `good`, pero tampoco son exclusion dura.

5. `daily/good_justification/daily_good_cases_v0_1.md`

   Dossier visual de justificacion positiva. Debe abrirse para entender que significa `good` en `daily`: no perfeccion literal, sino barra diaria suficientemente defendible para consumo principal bajo policy.

6. `daily/coverage_case_evidence_packs/daily_coverage_cases_v0_1.md`

   Dossier visual de coverage. Debe abrirse para entender por que un gap no es automaticamente fallo duro, y como se separan `LIKELY_VALID_GAP_ONLY`, `AMBIGUOUS_REVIEW` y `REALLY_PROBLEMATIC_UNEXPECTED`.

Lectura correcta final:

- `daily` es un bloque institucionalmente avanzado y ampliamente utilizable;
- su verdad principal vive en OHLC, fechas, parse, volume y coverage;
- `vw` es diagnostico/flag, no autoridad unica de salud global;
- `daily_adjusted` esta full-universe auditado y promovido;
- no debe mezclarse raw, adjusted y adjusted proxy sin declarar price view.

### `quotes`

Objetivo de inspeccion:

- entender calidad local del libro observado;
- separar `good`, `review` y `bad`;
- entender crossed/locked behavior;
- y no confundir explicacion causal externa con rehabilitacion automatica del libro.

Orden de lectura:

1. `quotes/README.md`

   Entrada local del bloque. Explica alcance, fuentes historicas, autoridad documental, estructura, modelo de imagenes y reglas para futuros agentes.

2. `quotes/quotes_inspection_readout_v0_1.md`

   Readout institucional principal. Resume taxonomia, politica de consumo, evidencia poblacional y veredicto global de `quotes`.

3. `quotes/flagged_case_evidence_packs/quotes_review_cases_v0_1.md`

   Dossier visual principal de `review`. Es el documento visual mas grande del bloque. Debe abrirse para entender casos donde el libro ya no es limpio, pero tampoco queda necesariamente excluido como `bad`.

4. `quotes/bad_case_evidence_packs/quotes_bad_cases_v0_1.md`

   Dossier visual de `bad`. Debe abrirse para entender los casos donde el libro local queda fuera del consumo core por contradiccion economica, crossed severo, degeneracion estructural u otra causa no rehabilitada.

5. `quotes/good_justification/quotes_good_cases_v0_1.md`

   Dossier visual de `good`. Debe abrirse para entender como se ve un libro sano o aceptable bajo policy, incluyendo micro-ruido tolerado.

6. `quotes/quotes_open_casepacks_audit_v0_1.md`

   Auditoria de trazabilidad de casepacks. Debe abrirse para comprobar que la frontera final `review` y `bad` no se construyo ad hoc, sino con correspondencia entre pools, manifests, markdowns y assets fisicos.

Lectura correcta final:

- `quotes` esta muy cerrado operacionalmente como dossier de calidad local del libro;
- un evento externo puede explicar un episodio, pero no rehabilita automaticamente el libro como limpio;
- `review` no debe consumirse como ejecucion limpia;
- `bad` no desacredita al proveedor completo, pero excluye esa unidad/familia del consumo core.

### `trades`

Objetivo de inspeccion:

- entender el tape raw de trades;
- separar poblacion, muestra metodologica, full closeout `57f`, familias semanticas y consumo;
- evitar que desacuerdo contra `daily` o `1m` se lea automaticamente como corrupcion del tape;
- y revisar visualmente familias amplias, no solo dos o tres casos historicos.

Orden de lectura:

1. `trades/README.md`

   Entrada local del bloque. Explica autoridad documental, fuentes historicas, estructura, universe readout, rehabilitacion, familias semanticas, price views y reglas para futuros agentes.

2. `trades/trades_inspection_readout_v0_1.md`

   Readout institucional principal. Explica las verdades simultaneas del bloque: poblacion estresada, muestra metodologica, closeout final, familias semanticas y estados de consumo.

3. `trades/trades_global_universe_readout_v0_1.md`

   Readout visual poblacional. Debe abrirse para entender distribucion global de labels, severidades, cobertura `1m`, odd-lots, duplicates, outside daily/1m y rehabilitacion.

4. `trades/family_case_evidence_packs/good/good_cases_v0_1.md`

   Casepack amplio de `good`. Debe abrirse para entender que `good` mide cola pristine, no masa util total.

5. `trades/family_case_evidence_packs/bad_data/bad_data_cases_v0_1.md`

   Casepack amplio de `bad_data`. Debe abrirse para entender la cola dura real y sus subfamilias, incluyendo casos donde el panel de precio no basta y hace falta evidencia estructural.

6. `trades/family_case_evidence_packs/reference_scale_mismatch/reference_scale_mismatch_cases_v0_1.md`

   Casepack amplio de scale mismatch. Debe abrirse para entender casos donde el conflicto principal es comparabilidad/escala frente a arbitros, no corrupcion directa del tape.

7. `trades/family_case_evidence_packs/review_microstructure/review_microstructure_cases_v0_1.md`

   Casepack amplio de microestructura. Debe abrirse para entender odd-lots, textura de prints y conflictos microestructurales que exigen flag o lectura contextual.

8. `trades/family_case_evidence_packs/review_no_1m_reference/review_no_1m_reference_cases_v0_1.md`

   Casepack amplio de ausencia de arbitro `1m`. Debe abrirse para entender por que la falta de referencia fina no equivale automaticamente a bad tape.

9. `trades/family_case_evidence_packs/review_1m_reference_alignment/review_1m_reference_alignment_cases_v0_1.md`

   Casepack amplio de alineacion con referencia `1m`. Debe abrirse para entender la familia donde el conflicto se evalua contra arbitro intradia fino.

10. `trades/family_case_evidence_packs/review/review_cases_v0_1.md`

    Casepack amplio de `review` generico. Debe abrirse para entender la frontera de casos no limpios, no rehabilitados automaticamente y no necesariamente `bad`.

Lectura correcta final:

- `trades` es el dossier mas completo como sistema forense institucional;
- `good` diminuto no significa que todo lo demas sea basura;
- `reference_scale_mismatch`, `review_microstructure`, `review_no_1m_reference`, `review_1m_reference_alignment`, `review` y `bad_data` no deben colapsarse en una sola nocion de calidad;
- `outside_daily` u `outside_1m` son senales, no sentencia final aislada;
- toda conclusion debe declarar arbitro, price view, familia causal, alcance y estado de consumo.

### `minute` / `ohlcv_1m` raw

Objetivo de inspeccion:

- entender el estado raw de `ohlcv_1m` en alcance `<1B>`;
- distinguir raw `ohlcv_1m` de `ohlcv_1m_split_normalized`;
- separar calidad core OHLCV de calidad `vw_*`;
- entender por que `vw` es deuda dominante sin convertir automaticamente todo el bloque en inutil;
- y navegar desde estadistica global hasta ticker-mes concreto mediante widgets.

Orden de lectura:

1. `minute/README.md`

   Entrada local obligatoria del bloque. Explica rol, autoridad documental, frontera conceptual, closeout raw `<1B>`, modelo moderno core/vw, assets activos y reglas para futuros agentes.

2. `minute/raw_1m_lt1b_closeout_recalculation_v0_1.md`

   Closeout cuantitativo raw `<1B>`. Debe abrirse para entender el recalculo institucional del universo, la interseccion temporal PTI, los buckets heredados y el estado refinado inicial `good / review / bad` dominado por deuda `vw`.

3. `minute/raw_1m_schema_only_lt1b_inspection_readout_v0_1.md`

   Readout especifico del bloque `RESCUE_SCHEMA_ONLY`. Debe abrirse para entender por que schema-only no significa limpio productivo, sino una familia estructural homogenea de lectura/schema/encoding.

4. `minute/raw_1m_schema_only_lt1b_inspection_notebook_v0_1.ipynb`

   Notebook historico ejecutado del bloque schema-only. Deben revisarse celdas y outputs porque muestra las tablas, selectores y evidencia que sostienen el readout.

5. `minute/minute_00_universe_quality_overview_v0_1.ipynb`

   Notebook moderno ejecutado de vision global. Debe abrirse para entender universo, cobertura, distribuciones temporales, estados heredados y familias antes de bajar a casos.

6. `minute/minute_01_core_quality_model_v0_1.ipynb`

   Notebook moderno ejecutado que materializa el manifest core/vw. Es obligatorio para entender como se construyen `core_quality_state`, `vw_quality_state`, `combined_quality_state` y `allowed_consumption`.

7. `minute/minute_02_core_quality_population_readout_v0_1.ipynb`

   Notebook moderno ejecutado de lectura poblacional. Debe abrirse para ver la matriz core/vw, familias, conteos y consumo permitido.

8. `minute/core_quality_case_evidence_packs/minute_core_quality_visual_cases_v0_1.md`

   Dossier visual fijo de `67` imagenes: `7` mapas poblacionales y `60` casos, `10` por seccion. Debe abrirse primero por su `Mapa Poblacional Visual` para entender core/vw, matriz de estados, familias, coverage, schema-only, delta `vw_not_flagged` y consumo permitido por ano. Despues debe leerse caso a caso para `core_good_vw_not_flagged`, `core_good_vw_mild_or_moderate`, `core_good_vw_bad_persistent`, `core_good_vw_bad_diffuse`, `core_review_large_gap` y `core_review_sparse`. Cada imagen tiene lectura independiente con `Que muestra / Responde / No responde / Consecuencia`.

9. `minute/minute_03_casepack_builder_v0_1.ipynb`

   Notebook interactivo con widgets. Debe usarse cuando el inspector quiera abrir o ampliar un caso ticker-mes fuera de las `60` imagenes fijas de caso ya exportadas.

10. `minute/minute_04_ticker_month_inspector_v0_1.ipynb`

   Notebook interactivo con widgets. Debe abrirse para navegar ticker, mes, estado core, estado `vw`, familia core y familia `vw` sin depender de una muestra fija.

11. `minute/minute_05_final_readout_v0_1.ipynb`

    Notebook moderno ejecutado de cierre. Debe abrirse para confirmar la lectura final: raw `1m <1B>` es mucho mas defendible para OHLCV sin `vw`, pero no queda promovido a capa productiva limpia sin flags.

Lectura correcta final:

- `minute` no es `1m_split_normalized`;
- `minute` no demuestra backtest intradia productivo limpio;
- el raw `1m <1B>` queda institucionalmente entendido mediante dos lecturas complementarias: closeout heredado/recalculado y manifest moderno core/vw;
- existe un dossier visual fijo de `67` imagenes: `7` poblacionales y `60` casos con lectura individual;
- el resultado moderno es `core_good = 331511`, `core_review = 3149`, `core_bad = 0`;
- la deuda `vw` sigue siendo dominante con `vw_bad = 212763`;
- el consumo correcto separa `controlled_ohlcv_research`, `ohlcv_without_vw_only` y `flagged_research_or_sensitivity`;
- cualquier inspector debe declarar si su pregunta usa `vw` o no.

## Criterios de cierre

Un dossier esta razonablemente cerrado cuando:

- tiene un readout principal o closeout claro;
- sus claims estan respaldados por evidencia trazable;
- los assets relevantes estan enlazados o incrustados;
- no hay assets activos huerfanos que parezcan vigentes;
- las limitaciones estan declaradas;
- el estado de consumo esta claro;
- los contratos relacionados estan enlazados;
- y no contradice schemas, policies, validators ni registry.

## Madurez relativa de dossiers

Fecha de referencia: 2026-06-07.

Esta seccion es una foto operacional de la madurez de `inspection_dossiers/`.

Debe actualizarse cada vez que avance cualquier dossier de esta carpeta. Esta obligacion es adicional a la entrada correspondiente en `CHANGELOG.md`: el changelog registra el cambio historico, pero esta seccion mantiene el mapa vivo de estado, madurez y riesgo por bloque.

La madurez relativa no debe medirse por numero bruto de archivos, imagenes o markdowns. Debe medirse contra el modelo institucional definido en:

- `01_foundations/module_contracts/inspection_dossier_model.md`

Criterios de lectura:

- readout principal o closeout claro;
- builder, notebook o mecanismo reproducible;
- `good_justification` cuando aplique;
- `flagged_case_evidence_packs` o equivalente cuando haya uso condicionado;
- `bad_case_evidence_packs` cuando haya exclusion;
- `coverage_case_evidence_packs` cuando el problema sea coverage, continuidad o universo esperado;
- `evidence_assets` trazables;
- manifests, snapshots, tablas o parquets reproducibles;
- imagenes incrustadas y explicadas;
- aplicacion de `Que muestra / Responde / No responde / Consecuencia`;
- separacion entre masa poblacional, muestra metodologica, casos forenses y decision final;
- enlace a schema, dataset contract, consumption policy, validators y registry entry;
- y declaracion de consumidores permitidos, restringidos y no permitidos.

### Estado por bloque a 2026-06-07

#### `daily`

Estado: institucionalmente avanzado y operacionalmente central.

Evidencia principal:

- `daily/README.md`
- `daily/build_daily_inspection_pack.md`
- `daily/daily_inspection_readout_v0_1.md`
- `daily/daily_adjusted_full_universe_audit_v0_1.md`
- `daily/daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md`
- `daily/coverage_case_evidence_packs/`

Lectura correcta:

- separa calidad del bar y coverage;
- distingue `ohlcv_daily` de `ohlcv_daily_adjusted`;
- `daily_adjusted` tiene auditoria full-universe especifica;
- gaps, recovery y coverage son parte del dictamen.

Madurez relativa: muy alta para consumo institucional del bloque daily.

Riesgo principal: resumir daily como `good / bad` sin coverage, o mezclar price views sin declararlas.

#### `quotes`

Estado: muy cerrado operacionalmente como dossier de calidad local del libro.

Evidencia principal:

- `quotes/build_quotes_inspection_pack.md`
- `quotes/quotes_inspection_readout_v0_1.md`
- `quotes/quotes_open_casepacks_audit_v0_1.md`
- `quotes/good_justification/`
- `quotes/flagged_case_evidence_packs/`
- `quotes/bad_case_evidence_packs/`
- `quotes/coverage_case_evidence_packs/`
- `quotes/evidence_assets/`

Lectura correcta:

- evalua calidad local del libro observado;
- separa crossed/locked behavior, severidad economica, `ask = 0`, `ask > 0`, persistencia, timestamp drift, rollover UTC e integerization;
- el contexto externo puede explicar un episodio, pero no rehabilita automaticamente el libro como limpio;
- `good / review / bad` es una politica operativa clara.

Madurez relativa: muy alta como dossier operativo, con casepacks visuales amplios y auditoria de casepacks abiertos.

Riesgo principal: confundir explicacion causal externa con rehabilitacion, o consumir `review` como libro limpio.

#### `trades`

Estado: el dossier mas completo como sistema de inspeccion forense.

Evidencia principal:

- `trades/build_trades_inspection_pack.md`
- `trades/trades_inspection_readout_v0_1.md`
- `trades/trades_global_universe_readout_v0_1.md`
- `trades/trades_sampling_strategy_v0_1.md`
- `trades/trades_inspection_notebook_v0_1.ipynb`
- `trades/trades_universe_inspection_notebook_v0_1.ipynb`
- `trades/population_evidence_packs/`
- `trades/file_acceptance_evidence_packs/`
- `trades/good_justification/`
- `trades/flagged_case_evidence_packs/`
- `trades/bad_case_evidence_packs/`
- `trades/family_case_evidence_packs/`
- `trades/evidence_assets/`

Lectura correcta:

- no puede leerse como cierre binario simple;
- separa snapshot poblacional, muestra metodologica, closeout full `57f`, estados finales, familias semanticas y consumo operativo;
- desacuerdo contra `daily` o `1m` no prueba por si solo corrupcion del tape;
- `outside_daily`, `outside_1m`, duplicados, odd-lots, off-session activity o scale mismatch son senales, no sentencia final aislada;
- la utilidad no se mide por la cola `good` extrema.

Madurez relativa: mas completo que `quotes` como sistema forense institucional, aunque con mas caveats.

Riesgo principal: colapsar `reference_scale_mismatch`, `review_microstructure`, `review_no_1m_reference`, `review_1m_reference_alignment`, `review` y `bad_data` en una sola nocion de calidad.

#### `minute` / `ohlcv_1m` raw

Estado: cierre institucional acotado para `ohlcv_1m` raw en alcance `<1B>`.

Evidencia principal:

- `minute/README.md`
- `minute/raw_1m_lt1b_closeout_recalculation_v0_1.md`
- `minute/raw_1m_schema_only_lt1b_inspection_readout_v0_1.md`
- `minute/raw_1m_schema_only_lt1b_inspection_notebook_v0_1.ipynb`
- `minute/minute_00_universe_quality_overview_v0_1.ipynb`
- `minute/minute_01_core_quality_model_v0_1.ipynb`
- `minute/minute_02_core_quality_population_readout_v0_1.ipynb`
- `minute/minute_03_casepack_builder_v0_1.ipynb`
- `minute/minute_04_ticker_month_inspector_v0_1.ipynb`
- `minute/minute_05_final_readout_v0_1.ipynb`
- `minute/core_quality_case_evidence_packs/minute_core_quality_visual_cases_v0_1.md`
- `minute/core_quality_case_evidence_packs/minute_core_quality_visual_case_manifest_v0_1.csv`
- `minute/core_quality_case_evidence_packs/population_visual_overview/`
- `minute/core_quality_case_evidence_packs/population_visual_overview/minute_population_visual_manifest_v0_1.csv`
- `minute/core_quality_case_evidence_packs/images/`
- `minute/evidence_assets/core_quality/minute_core_quality_manifest_v0_1.parquet`
- `minute/evidence_assets/core_quality/minute_core_quality_family_counts_v0_1.csv`
- `minute/evidence_assets/core_quality/minute_core_quality_summary_v0_1.csv`

Lectura correcta:

- documenta raw `ohlcv_1m`, no `ohlcv_1m_split_normalized`;
- schema-only no equivale a validacion semantica completa;
- el alcance `<1B>` debe mantenerse visible.
- los porcentajes actuales validos para raw `1m <1B>` salen del recalculo local, no de los porcentajes historicos `full-scope`.
- estado refinado `<1B>` actual: `good = 46652`, `review = 75245`, `bad = 212763`.
- la lectura moderna separa core OHLCV de `vw`: `core_good = 331511`, `core_review = 3149`, `core_bad = 0`.
- la deuda `vw` sigue siendo dominante: `vw_bad = 212763`.
- consumo moderno permitido: `controlled_ohlcv_research = 118818`, `ohlcv_without_vw_only = 212693`, `flagged_research_or_sensitivity = 3149`.
- el dossier visual ya empieza con mapa poblacional antes de casos: core/vw state overview, matriz core/vw, familias, coverage/footprint, schema-only, delta `vw_not_flagged` y consumo por ano.

Madurez relativa: alta como auditoria raw core/vw separada, con manifest moderno, notebooks globales ejecutados, notebooks interactivos con widgets y dossier visual fijo de `67` imagenes (`7` poblacionales + `60` casos). Sigue por debajo de `trades` en volumen total de familias forenses, pero ya no debe describirse como pendiente de casepacks visuales fijos ni como pendiente de mapa poblacional general.

Riesgo principal: promover schema-only a calidad economica completa, mezclar raw 1m con split-normalized, o presentar raw 1m como capa productiva limpia.

Regla de mantenimiento especifica:

- si se exportan nuevos casepacks visuales;
- si cambia la clasificacion core/vw;
- si se reejecuta el manifest;
- o si se decide promocionar/restringir consumo;

entonces debe actualizarse esta seccion junto con `minute/README.md` y `CHANGELOG.md`.

#### `1m_split_normalized`

Estado: capa derivada avanzada, con piloto, auditoria full-universe y readout final.

Evidencia principal:

- `1m_split_normalized/README.md`
- `1m_split_normalized/ohlcv_1m_split_normalized_pilot_readout_v0_1.md`
- `1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1.md`
- `1m_split_normalized/ohlcv_1m_split_normalized_final_readout_v0_1.md`
- `1m_split_normalized/event_case_evidence_packs/ohlcv_1m_split_normalized_visual_inspector_pack_v0_1.md`
- `1m_split_normalized/event_case_evidence_packs/ohlcv_1m_split_normalized_visual_case_manifest_v0_1.csv`
- `1m_split_normalized/population_visual_overview/`
- `1m_split_normalized/ohlcv_1m_split_normalized_inspection_notebook_v0_1.ipynb`
- `1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_notebook_v0_1.ipynb`

Lectura correcta:

- no es raw `ohlcv_1m`;
- no debe leerse solo por el piloto inicial;
- debe evaluarse como capa derivada: definida, implementada, pilotada, consumida y auditada full-universe para eventos split auditables;
- no debe confundirse auditoria full-universe de eventos split con materializacion fisica full-universe de todos los ticker-month;
- el paquete visual moderno contiene `6` mapas poblacionales y `28` visuales de caso con `Que muestra / Responde / No responde / Consecuencia`;
- debe leerse contra `layer_validation_standard_v0_1.md`.

Madurez relativa: alta como capa derivada documentada y auditada para su deuda concreta de splits. Ya cumple el estandar inspector general-a-particular para esta pregunta: poblacion, familias de coverage, casos PASS, casos coverage-limited y decision de consumo. No debe describirse como pendiente de mapa visual poblacional.

Riesgo principal: decir "piloto" ignorando el audit full-universe posterior; o decir "full-universe" sin aclarar que se refiere a eventos split auditables, no a materializacion fisica de toda la vista.

#### `intraday_regime_features`

Estado: piloto semantico de features/contexto.

Evidencia principal:

- `intraday_regime_features/intraday_regime_features_semantic_pilot_readout_v0_1.md`

Lectura correcta:

- no normaliza precios;
- no sustituye `daily_adjusted` ni `1m_split_normalized`;
- genera contexto de regimen intradiario a partir de price views ya gobernadas;
- responde preguntas de extension contra sesiones previas, gap, volatilidad reciente, distancia a rangos previos y ruptura de contexto.

Madurez relativa: baja/media frente a `daily`, `quotes`, `trades` y `1m_split_normalized`; valiosa como capa semantica, no como promocion productiva amplia por si sola.

Riesgo principal: consumirla como feature productiva sin declarar alcance, price view y madurez.

#### `reference`

Estado: foundation layer promovida desde auditoria y certification historicas, con dossier inspector moderno completado para promocion foundation.

Evidencia principal actual:

- `reference/README.md`
- `reference/build_reference_inspection_pack.md`
- `reference/reference_institutional_closeout_v0_1.md`
- `reference/reference_inspection_readout_v0_2.md`
- `reference/reference_modernization_gap_audit_2026-06-12.md`
- `reference/reference_casepacks_traceability_audit_v0_1.md`
- `reference/integration_notes.md`
- `reference/evidence_assets/run_manifest.json`
- `reference/evidence_assets/population_visual_overview/`
- `reference/evidence_assets/case_manifest/reference_case_manifest_v0_1.md`
- `../contract_registry/dataset_contracts/reference_dataset_contract_v0_1.md`
- `../data_consumption_policies/reference_consumption_policy.md`
- `../dataset_registry/reference/reference_registry_entry.yaml`
- `../validators/reference/reference_validators.md`
- `../canonical_schemas/reference/`

Lectura correcta:

- `reference` gobierna identidad, ticker types, snapshots, corporate actions y eventos;
- `splits` y `dividends` alimentan price views;
- `events/ticker_change` es detector causal fuerte en `halts` y `quotes`, pero no continuidad economica cerrada;
- `all_tickers` no es universe final;
- `overview.market_cap` no es membership diaria fully PTI;
- la evidencia historica pesada existe y ahora esta promocionada como manifests, summaries, visuales y casepacks ligeros bajo `01_foundations`.

Madurez relativa: alta para su rol de foundation/reference layer. Ya tiene builder residente, physical root audit, historical/cache inventory, certification inventory, population summary, `5` visuales poblacionales, manifests y `5` casepacks. Sigue sin habilitar consumidores sensibles nuevos.

Riesgo principal: confundir madurez inspectora de foundation layer con permiso para feature/alpha/continuidad corporativa/live/RL sin contrato temporal y causal posterior.

#### `halts`

Estado: event/reference layer promovida desde auditoria y certification historicas, con dossier inspector moderno completado para promocion foundation.

Evidencia principal actual:

- `halts/README.md`
- `halts/build_halts_inspection_pack.md`
- `halts/halts_inspection_readout_v0_1.md`
- `halts/halts_casepacks_traceability_audit_v0_1.md`
- `halts/integration_notes.md`
- `halts/evidence_assets/run_manifest.json`
- `halts/evidence_assets/population_summary/halts_population_summary_v0_1.md`
- `halts/evidence_assets/population_visual_overview/`
- `halts/evidence_assets/case_manifest/halts_case_manifest_v0_1.md`
- `../contract_registry/dataset_contracts/halts_dataset_contract_v0_1.md`
- `../data_consumption_policies/halts_consumption_policy.md`
- `../dataset_registry/halts/halts_registry_entry.yaml`
- `../validators/halts/halts_validators.md`
- `../canonical_schemas/halts/`

Lectura correcta:

- `halts` gobierna eventos oficiales Nasdaq/NYSE y contexto SEC;
- `good_full_intraday_event` no debe mezclarse con `good_date_level_event`;
- `regulatory_context_only` no es ventana intradia;
- visuales contra `quotes` y `trades` son evidencia forense, no sustituto del evento oficial;
- ausencia de halt no prueba missing data ni mercado limpio;
- y `halts` no habilita alpha, live, RL ni execution simulation final.

Madurez relativa: alta para su rol de event/reference layer. Ya tiene builder residente, root audit, historical/cache inventory, certification inventory, population summary, `5` visuales poblacionales, manifests y `5` casepacks. Sigue sin habilitar consumidores sensibles nuevos.

Riesgo principal: convertir eventos oficiales o buckets visuales en features/alpha/masks productivos sin contrato de temporalidad, leakage y consumidor.

#### `additional`

Estado: closeout institucional compacto.

Evidencia principal:

- `additional/additional_institutional_closeout_v0_1.md`

Lectura correcta:

- agrupa datasets auxiliares, no tape;
- su consumo depende de lag, provenance, cobertura, fuente y semantica temporal;
- presencia fisica no implica consumo permitido.

Madurez relativa: compacta por naturaleza; suficiente como closeout de inventario/politica si no exige casepacks visuales.

Riesgo principal: usar `additional` como cajon generico sin schema/policy por subdataset.

#### `short`

Estado: closeout institucional compacto.

Evidencia principal:

- `short/short_institutional_closeout_v0_1.md`

Lectura correcta:

- short data es evidencia auxiliar de presion/crowding, no tape ejecutable;
- no debe interpretarse como volumen consolidado completo ni como senal causal same-day sin lag explicito;
- su consumo debe respetar fuente, fecha efectiva, revision y cobertura.

Madurez relativa: compacta y acotada; apropiada si el objetivo es declarar semantica y restricciones de consumo.

Riesgo principal: consumir short interest o short volume como si fuera microestructura intradia.

### Regla de mantenimiento

Cada avance material en cualquier dossier debe actualizar tres capas:

1. El documento local del bloque afectado.
2. Esta seccion de madurez relativa en `inspection_dossiers/README.md`.
3. `CHANGELOG.md`, cuando el avance tenga impacto institucional, contractual, de consumo o de estructura documental.

Si no se actualiza esta seccion, el mapa de madurez queda obsoleto aunque el changelog registre el cambio.

## Regla de higiene

No deben mantenerse en activo:

- carpetas viejas y nuevas con el mismo rol;
- manifests obsoletos mezclados con manifests vigentes;
- imagenes generadas pero no consumidas;
- notebooks que contradicen readouts sin nota de estado;
- ni exports historicos presentados como policy actual.

Si algo conserva valor historico, debe archivarse o declararse como evidencia historica.

Si ya no tiene valor, debe eliminarse.

## Relacion con `01_research`

La evidencia historica en `01_research` no debe reescribirse ni reorganizarse para encajar con esta carpeta.

La estrategia correcta es:

- preservar la evidencia historica;
- extraer conclusiones estables;
- encapsularlas en `01_foundations`;
- enlazar lo necesario;
- y dejar claro que decision institucional se deriva.

`inspection_dossiers/` existe para que esa evidencia sea legible sin depender de memoria conversacional.

## Regla final

Un bloque no esta institucionalmente maduro solo porque existan parquets, notebooks o contratos.

Debe poder:

- mostrar su evidencia;
- explicar sus decisiones;
- declarar sus limites;
- permitir inspeccion humana;
- y conectar esa lectura con consumo gobernado.
