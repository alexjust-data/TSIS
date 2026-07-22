# Build Quotes Inspection Pack - Modulo 01

## 1. Rol

Este documento describe como debe construirse el dossier de inspeccion de `quotes`.

No ejecuta nada.

Fija la intencion operativa para el builder futuro.

## 2. Fuentes principales

La construccion del pack debe apoyarse en:

- notebooks historicos de auditoria `quotes`;
- markdowns de auditoria, metodologia y closeout;
- markdowns de certificacion local de `quotes`;
- artefactos persistidos de buckets y tablas de calidad ya cerradas;
- evidencia contextual cruzada cuando aplique:
  - `halts`
  - `reference`
  - `news`
  - `ipos`
  - `crosswalk`

## 3. Objetivo metodologico

El builder no debe inventar una interpretacion nueva.

Debe:

- recuperar la evidencia ya existente;
- organizarla;
- y dejarla lista para inspeccion institucional.

En `quotes`, eso implica una distincion obligatoria:

- explicacion causal del episodio;
- calidad local del libro.

El builder debe ayudar a mostrar ambas cosas sin colapsarlas en una sola.

## 4. Assets que debe producir o clasificar

El builder deberia producir o clasificar:

- tablas resumen por bucket;
- ejemplos `good`;
- ejemplos `review`;
- ejemplos `bad`;
- ejemplos donde el contexto externo explica pero no rehabilita;
- imagenes nuevas si hacen falta;
- y un indice de casos inspeccionables por `ticker-date-file`.

Los assets visuales finales no deben quedarse como outputs huerfanos.

Deben terminar:

- incrustados en `quotes_inspection_readout_v0_1.md`;
- o incrustados en `good_justification`, `flagged_case_evidence_packs`, `bad_case_evidence_packs` y `coverage_case_evidence_packs`.

## 5. Regla visual de `quotes`

En `quotes`, la imagen buena para inspector no es solo un resumen de counts.

Debe poder mostrar fisicamente:

- donde aparece el crossed;
- con que magnitud economica;
- cuanto dura;
- si sobrevive `ask > 0`;
- y que contexto externo relevante existe alrededor del episodio.

La regla correcta para el panel visual es:

- primero mostrar el hecho local del libro;
- despues mostrar la gravedad economica;
- y solo despues mostrar el contexto causal externo.

## 6. Familias de dossier objetivo

La estructura de inspeccion de `quotes` debe seguir el mismo patron de `daily`:

- `bad_case_evidence_packs`
- `flagged_case_evidence_packs`
- `good_justification`
- `coverage_case_evidence_packs`
- `evidence_assets`

Con una salvedad semantica:

- en `quotes`, `coverage` no es hoy el eje principal del cierre;
- el eje principal es la calidad local del libro y su relacion con el contexto externo.

## 7. Evolucion prevista

Fase inicial aceptable:

- script de construccion y export de casos
- notebook historico como lanzadera y visor

Fase madura deseable:

- script reproducible equivalente con generacion de manifests y dossiers

## 8. Regla final

El objetivo de `quotes` no es solo etiquetar buckets.

Es dejar explicaciones plausibles, trazables e inspeccionables de por que un caso cae en:

- `good`
- `review`
- `bad`

y cuando un episodio esta:

- explicado
- pero no rehabilitado.

## 8.1 Regla de granularidad: masa poblacional vs casos forenses

En `quotes` no debe confundirse nunca:

- la masa poblacional total auditada;
- la capa de taxonomias o buckets;
- y la capa de casos ejemplares del inspector final.

La lectura correcta es:

1. la auditoria global produce conteos poblacionales amplios como:
   - `PASS`
   - `SOFT_FAIL`
   - `HARD_FAIL`
2. esa masa se reorganiza en familias taxonomicas;
3. y solo despues se seleccionan casos ejemplares para inspeccion forense de las familias abiertas.

Por tanto:

- los `case packs` no pretenden enumerar uno a uno todos los `HARD_FAIL` del universo;
- pretenden representar visual y forensicamente las familias abiertas que siguen importando para la decision institucional.

Regla de interpretacion obligatoria para el inspector:

- la masa completa del universo debe justificarse con evidencia poblacional;
- las familias abiertas deben justificarse con evidencia forense ejemplar;
- y ambos planos deben leerse juntos.

Esto implica que el cierre institucional final de `quotes` debe incluir dos capas de evidencia separadas:

### A. Evidencia poblacional

Debe mostrar, como minimo:

- distribucion global de severidad
- taxonomia completa
- root mix
- severidad economica del crossed
- regimenes `mild / moderate / severe`
- rollover UTC
- y composicion `ask = 0` vs `ask > 0`

Esta capa responde:

- cuanta masa hay
- donde esta
- y de que tipo es

### B. Evidencia forense ejemplar

Debe mostrar:

- casos `review`
- casos `bad`
- y, cuando proceda, ejemplos `good`

Esta capa responde:

- como se ve fisicamente cada familia abierta
- por que un caso cae en `good`, `review` o `bad`
- y cuando un episodio esta explicado pero no rehabilitado

Conclusion metodologica:

- una bolsa pequena de ejemplos nunca debe presentarse como si representara exhaustivamente toda la masa poblacional;
- si se usa una muestra forense, debe declararse explicitamente como muestra de familias abiertas;
- y la capa poblacional debe seguir estando visible mediante tablas, graficos e imagenes historicas del notebook de auditoria.

## 9. Estado actual y pausa metodologica explicita

El bloque `quotes` queda temporalmente en pausa parcial de refinamiento visual y de reconciliacion final.

Motivo:

- durante la construccion de los dossiers se confirmo que ciertas discrepancias de escala y comparacion externa no pueden cerrarse bien sin una politica transversal mas fuerte de:
  - `price views`
  - corporate actions
  - split normalization
  - y adjusted economics

En particular, quedaron abiertos o en revision:

- la institucionalizacion reusable de `split_normalized`
- la institucionalizacion reusable de `adjusted`
- y la separacion limpia entre:
  - `quotes raw`
  - `daily raw`
  - `adjusted external`

La razon de apartarlo temporalmente ahora no es abandono del bloque.

Es lo contrario:

- se ha detectado que el problema ya es de infraestructura general del modulo;
- y primero debe cerrarse esa infraestructura para no fijar conclusiones locales sobre una semantica de precio incompleta.

Documentos que motivan y soportan esta pausa:

- `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`
- `01_foundations/module_contracts/external_price_comparison_caveats.md`
- `01_foundations/module_contracts/price_views_registry.md`
- `01_foundations/module_contracts/corporate_actions_adjustment_methodology.md`
- `01_foundations/module_contracts/event_families_and_reference_inventory.md`
