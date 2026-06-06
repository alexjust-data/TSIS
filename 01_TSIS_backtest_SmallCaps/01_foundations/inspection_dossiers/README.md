# Inspection Dossiers

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
  good_justification/
  flagged_case_evidence_packs/
  bad_case_evidence_packs/
  coverage_case_evidence_packs/
  evidence_assets/
  build_<dataset>_inspection_pack.md
```

La estructura exacta puede variar si el dataset lo exige, pero la logica debe quedar clara:

- readout principal;
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

### 1m split normalized

`1m_split_normalized` es una capa derivada. Su dossier debe leerse con el estandar de validacion de capas.

Debe distinguir:

- piloto;
- auditoria full-universe;
- validacion semantica;
- controles negativos;
- consumo real;
- y promocion.

Referencias locales:

- `1m_split_normalized/ohlcv_1m_split_normalized_pilot_readout_v0_1.md`
- `1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1.md`
- `1m_split_normalized/ohlcv_1m_split_normalized_final_readout_v0_1.md`

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
