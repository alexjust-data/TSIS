# Raw Data Authority and Derivation Map

## 1. Rol del documento

Este contrato fija la distincion institucional entre:

- data RAW;
- raw market data;
- raw reference data;
- raw context data;
- reference data;
- context data;
- vistas derivadas ETL;
- feature layers;
- label/target layers;
- audit evidence;
- runtime/cache artifacts.

Su funcion es impedir que humanos o agentes mezclen capas distintas solo porque
viven cerca en disco, aparecen juntas en un grafo, comparten ticker/date o se
usan en el mismo flujo de auditoria.

Este documento no sustituye:

- dataset contracts especificos;
- schemas canonicos;
- data consumption policies;
- dataset registry entries;
- validators;
- inspection dossiers.

Si este contrato contradice una policy viva mas especifica, debe abrirse una
revision. Hasta entonces, manda la policy viva mas especifica para consumo y
este documento manda para clasificacion transversal RAW/derivada.

## 2. Dos ejes obligatorios

TSIS separa dos preguntas que no deben mezclarse:

1. `Procedencia`: el dato fue descargado/preservado desde vendor sin alterar su
   contenido semantico?
2. `Rol funcional`: ese dato representa precio, libro, tape, reference,
   contexto, derivado, feature, label o evidencia?

Consecuencia:

```text
Todo dato descargado de Polygon y preservado sin alterar su contenido semantico
es RAW vendor data.
```

Eso incluye, cuando cumplen esa condicion:

- daily;
- quotes;
- trades;
- ohlcv_1m;
- reference;
- halts;
- short;
- financials;
- news;
- IPOs;
- economic;
- corporate actions;
- regime/context datasets descargados como vendor payload.

Pero:

```text
RAW vendor data no significa necesariamente raw market price authority.
```

Por ejemplo, `short` puede ser RAW vendor context data; `financials` puede ser
RAW vendor fundamentals/context data; `reference` puede ser RAW vendor reference
data. Ninguno de esos roles los convierte en price/book/tape authority.

## 3. Regla central sobre RAW

La definicion correcta dentro de TSIS es:

```text
RAW data significa dato preservado sin alterar su contenido semantico.
```

RAW no significa:

```text
dato con minima transformacion
```

La expresion "minima transformacion" es peligrosa porque puede esconder cambios
que ya alteran la verdad observable:

- corregir precios;
- aplicar splits o dividendos;
- filtrar filas malas;
- deduplicar de forma destructiva;
- imputar valores;
- mezclar vendors;
- normalizar continuidad de ticker;
- reclasificar estados de calidad;
- seleccionar solo lo sano.

Nada de eso sigue siendo RAW aunque el cambio parezca pequeno.

## 4. Clases institucionales de artefacto

### `RAW_VENDOR_ORIGINAL`

Dato recibido o descargado de una fuente externa sin cambios de filas, valores,
columnas semanticas ni interpretacion.

Puede tener metadata externa de descarga, pero el contenido de mercado o evento
no se corrige.

Esta clase aplica tanto a market data como a reference/context data.

### `RAW_STAGED`

Dato RAW preservado en un formato operativo distinto.

Ejemplos permitidos:

- particionado por ticker/year;
- compresion;
- conversion de contenedor;
- metadata de lineage separada;
- manifest externo.

Condicion obligatoria:

```text
filas y valores semanticos permanecen equivalentes al origen preservado
```

Si se corrigen valores, se eliminan filas, se ajustan precios o se mezclan
fuentes, deja de ser RAW.

Alias operativo aceptado:

```text
RAW_VENDOR_STAGED
```

### `RAW_AUDITED`

RAW con diagnosticos, flags, manifests, readouts o dossiers alrededor.

La RAW auditada no cambia por tener auditoria. La auditoria vive fuera o junto a
ella como evidencia separada.

### `REFERENCE_DATA`

Datos de identidad, lifecycle, corporate actions, ticker events, exchange,
halts o universe support.

Cuando proceden de vendor y se preservan sin alterar contenido semantico,
tambien son RAW vendor data por procedencia.

Pueden ser autoridad para identidad o eventos, pero no son precio, tape ni
libro.

### `CONTEXT_DATA`

Datos auxiliares para explicar entorno, causalidad o condiciones de mercado:
short, fundamentals, news, economic, IPOs y otros overlays.

Cuando proceden de vendor y se preservan sin alterar contenido semantico,
tambien son RAW vendor data por procedencia.

No son core market price truth salvo contrato especifico.

### `DERIVED_ETL_VIEW`

Vista construida desde una o varias fuentes gobernadas mediante reglas
explicitas.

Ejemplos:

- `daily_adjusted`;
- `ohlcv_1m_split_normalized`.

Una vista derivada puede ser institucional y estar muy madura, pero no es RAW.

### `FEATURE_LAYER`

Capa de variables explicativas para research, estados, modelos o diagnostico.

Puede ser muy util y estar validada, pero su rol es `X`, no fuente primaria ni
certificacion de upstream.

### `LABEL_TARGET_LAYER`

Capa de outcomes o targets forward-looking.

Su rol es `y`, no `X`, y no puede estar disponible en decision time.

Se audita por anti-leakage, cobertura, formula y lineage, no porque sea
auditoria primaria de RAW.

### `AUDIT_EVIDENCE`

Dossiers, readouts, casepacks, imagenes, manifests, global metrics, notebooks,
scripts de inspeccion y Graphify outputs usados para entender y demostrar el
estado de una capa.

Son evidencia. No son dataset de mercado por defecto.

### `RUNTIME_CACHE_OR_TEMP`

Outputs transitorios, caches, logs o estados intermedios no promovidos.

No son source of truth institucional.

## 5. Prioridad de auditoria

La auditoria primaria empieza por:

```text
RAW_VENDOR_ORIGINAL / RAW_STAGED / RAW_AUDITED
```

Para preguntas de precio, liquidez, book o tape, la prioridad dentro de esa RAW
recae en raw market data:

```text
daily + quotes + trades + ohlcv_1m_raw
```

Para preguntas de identidad, lifecycle, corporate actions, halts, short,
fundamentals, news o contexto, la prioridad recae en la RAW vendor de esa
familia y su policy especifica.

Despues vienen:

1. `RAW_AUDITED`: demuestra que la RAW fue inspeccionada sin alterar su
   contenido.
2. `DERIVED_ETL_VIEW`: demuestra que una transformacion esta gobernada y no
   introduce errores semanticos.
3. `FEATURE_LAYER`: demuestra que variables downstream respetan upstream,
   tiempo, leakage y consumidor.
4. `LABEL_TARGET_LAYER`: demuestra que outcomes/targets son correctos, no
   disponibles en decision time y no contaminados por corporate actions falsas.
5. `AUDIT_EVIDENCE`: demuestra como se llego a una conclusion; no reemplaza el
   objeto auditado.

Regla no negociable:

```text
Ninguna capa derivada certifica retroactivamente la calidad de la RAW que la
alimenta.
```

Una capa derivada puede detectar problemas upstream, puede exigir revisar la
RAW y puede quedar bloqueada por la RAW. Pero no convierte la RAW en buena.

## 5.1 Regla de raiz operativa preferida

La raiz operativa preferida para la base de datos activa de TSIS es:

```text
E:/TSIS/data
```

Las referencias a `D:/...` o `C:/TSIS_Data/data/...` en documentos historicos,
manifests o dossiers deben leerse como rutas legacy/provenance mientras no
exista una excepcion explicita.

El cierre final de almacenamiento RAW exige demostrar paridad entre las carpetas
raw/source-preserved relevantes bajo `D:/` y sus landings bajo `E:/TSIS/data`,
segun:

```text
01_foundations/module_contracts/transversal/raw_storage_parity_audit_requirement_v0_1.md
```

## 6. Mapa institucional por familia

| Familia | Raiz fisica o logica principal | Procedencia RAW vendor | Rol funcional | Rol correcto en la cadena de auditoria | No debe usarse para afirmar |
| --- | --- | --- | --- | --- | --- |
| `daily_core_v0_1` | `D:/ohlcv_daily`, `E:/TSIS/data/ohlcv_daily` segun contrato/registry/dossier vigente | Si, si es vendor-preserved | Raw market data diaria | Base diaria de precio/volumen agregada; gobierna calidad y coverage diarios | Verdad economica ajustada, ejecucion intradia, libro o tape |
| `quotes_core_v0_1` | `C:/TSIS_Data/data/quotes`, `D:/quotes`, `E:/TSIS/data/quotes` segun contrato/registry vigente | Si, si es vendor-preserved | Raw market data de book | Evidencia microestructural de bid/ask y calidad local del book | Identidad issuer, halts, corporate actions, precio ajustado o ejecucion |
| `trades_core_v0_1` | `C:/TSIS_Data/data/trades_ticks_prod_2005_2026`, `D:/trades_ticks_prod_2005_2026`, `E:/TSIS/data/trades_ticks_prod_2005_2026` segun contrato/registry vigente | Si, si es vendor-preserved | Raw market data de tape | Tape de ejecucion y prints, con taxonomia de comparabilidad y recovery | Serie economica diaria generica, libro, adjusted truth o continuidad corporativa |
| `ohlcv_1m_raw_v0_1` | `D:/ohlcv_1m`, `E:/TSIS/data/ohlcv_1m` segun contrato/registry/dossier vigente | Si, si es vendor-preserved | Raw market data intradia | Base intradia raw entendida y reconciliada para LT1B con restricciones | Capa productiva limpia universal, verdad split-sensitive cross-session |
| `halts_v0_1` | `E:/TSIS/data/Halts`, `D:/Halts` segun registry/dossier | Si, si es vendor/external-preserved | Raw reference/event data | Evento externo para explicar microestructura, halts y causal overlays | Alpha, precio, tape, book o ejecucion |
| `reference_v0_1` | `E:/TSIS/data/reference` | Si, si es vendor-preserved | Raw reference data | Identidad, lifecycle, ticker types, splits, dividends, exchange/events | Precio, ejecucion, feature alpha, membership diaria PTI final |
| `additional_v0_1` | `C:/TSIS_Data/data/additional`, `E:/TSIS/data/additional` segun subfamilia vigente | Si, si es vendor-preserved | Raw context data por subfamilia | Contexto auxiliar por subfamilia: financials, news, IPOs, economic, corporate actions secundarios | Dataset plano homogeneo, corporate actions autoridad primaria, price truth |
| `short_v0_1` | `C:/TSIS_Data/data/short`, `E:/TSIS/data/short` segun registry vigente | Si, si es vendor-preserved | Raw context data short-side | Contexto short-side con flags, ventanas y source limits | Core limpio universal, causalidad intradia fina, short truth full-history |
| `short_review_finra_v0_1` | `E:/TSIS/data/short_review/finra_short` | Si, si es source-preserved | Raw context/provenance baseline | Baseline official/free FINRA y provenance para comparar short local | Sustituto silencioso de `short`, cobertura completa 2005-2026 |
| `lt1b_universe_v0_1` | `runs/backtest/market_cap_last_observed_cutoff/...` | No, es derivacion de universo | Universe derivation | Corte operacional canonico `<1B>` con ticker + ventana PTI | Membership diaria fully point-in-time, reference completa |
| `daily_adjusted_v0_1` | `E:/TSIS/data/ohlcv_daily_adjusted` | No, es derivado | Derived ETL price view | Vista diaria economica lenta ajustada y promovida full-universe | Reemplazo de raw daily, quotes, trades o ejecucion intradia |
| `ohlcv_1m_split_normalized_v0_1` | `E:/TSIS/data/ohlcv_1m_split_normalized` | No, es derivado | Derived ETL price view | Vista intradia derivada para comparabilidad cross-session split-sensitive | Sustituto full-universe de `1m raw` o certificacion global de raw |
| `intraday_regime_features_v0_1` | `E:/TSIS/data/intraday_regime_features` | No, es feature derivada | Feature layer | Consumidor piloto/feature layer para validar uso correcto de price views | Auditoria primaria de raw, alpha, capa productiva global |
| `daily_return_labels_v0_1` | `E:/TSIS/data/daily_return_labels` | No, es label derivado | Label/target layer | Outcomes `ret_1d`, `ret_3d`, `ret_5d` derivados de `daily_adjusted` para targets futuros | Feature disponible en decision time, auditoria primaria de raw |
| `financial` / `financial standalone schemas` | `E:/TSIS/data/financial`, `01_foundations/canonical_schemas/financial/` | Si para payloads vendor-preserved; no para schemas | Raw context/fundamentals data + schema backlog | Datos financieros/contextuales pendientes de decision de dataset propio o absorcion bajo `additional/financials` | Dataset gobernado completo, registry, policy o evidencia final |
| `regime_indicators` / `regime_indicators schemas` | `E:/TSIS/data/regime_indicators`, `01_foundations/canonical_schemas/regime_indicators/` | Si para payloads vendor-preserved; no para schemas | Raw context/regime data + schema backlog | Indicadores ETF/index/macro-regime pendientes de institucionalizacion propia | Capa institucional operativa o evidencia de regime model |
| `inspection_dossiers/evidence_assets` | `01_foundations/inspection_dossiers/**/evidence_assets/` | No | Audit evidence | Prueba humana de realidad material, casos, severidad, imagenes y manifests | Fuente primaria de mercado o input de modelo por defecto |
| `graphify-out` leaves | `01_foundations/graphify-out/leaf_slices/*`, `00_data_certification/graphify-out/leaf_slices/*` | No | Audit evidence / semantic map | Mapa semantico para orientar consultas y relaciones | Source of truth fisico, profiler de parquet, certificacion por si solo |

## 7. Como leer documentos historicos de auditoria

Los documentos historicos de:

```text
01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/
01_research/01_auditoria_RAW_DATA/00_data_certification/certification/
```

son evidencia preservada.

Pueden explicar:

- que data se descargo;
- que problemas se encontraron;
- como se penso el universo `<1B>`;
- que notebooks o markdowns demostraron root cause;
- que crosswalks unieron familias;
- que decisiones expected/present/healthy/usable se propusieron o cerraron.

No son, por si solos, contratos vivos modernos.

Los documentos historicos generales que deben tratarse como candidatos
importantes para entender la RAW existente son:

- `auditoria/05_crosswalk_multidataset.md`
- `auditoria/00_auditoria_general.ipynb`
- `auditoria/00_auditoria_general.md`
- `auditoria/00_que_proyecto_estamos_construyendo.md`
- `auditoria/01_auditoria_1B_general.ipynb`
- `auditoria/01_auditoria_1B_general.md`

Nota Graphify:

```text
certification_decisions_graph no indexa hoy esos documentos generales como nodos.
```

Consecuencia:

- si una consulta depende de esos documentos, el agente debe declarar que el
  grafo historico actual no cubre esa evidencia general;
- despues debe consultar las fuentes historicas directamente;
- y si el conocimiento pasa a ser operativo, debe aterrizarlo en
  `01_foundations` como contrato, policy, registry, validator, dossier o deuda.

Leaf futuro esperado para cubrir esa evidencia:

```text
certification_notebook_evidence_graph
```

## 8. Reglas para nuevas capas o nuevas raices fisicas

Antes de anadir o promocionar una nueva familia de data, el agente debe
clasificarla con estas preguntas:

1. Que verdad afirma conservar?
2. Es RAW vendor por procedencia o es derivado?
3. Si es RAW vendor, su rol funcional es market, reference, context,
   fundamentals, event, universe support u otro?
4. Que upstream gobierna su contenido?
5. Que puede demostrar por si sola?
6. Que no puede demostrar nunca?
7. Que contrato, schema, registry, policy, validator y dossier la gobiernan?
8. Que consumidores quedan permitidos o prohibidos?
9. Que documentos historicos pueden explicar su origen sin convertirse en
   autoridad viva?

Si no se puede responder, la capa no debe promocionarse.

## 9. Relacion con `E:/TSIS/data`

`E:/TSIS/data` es un plano fisico operativo importante, pero no es por si solo
la autoridad conceptual.

Regla:

```text
La raiz fisica describe donde vive algo.
El contrato describe que significa.
```

Por tanto, un README fisico en `E:/TSIS/data` debe apuntar a este contrato y no
duplicar ni reemplazar la autoridad semantica de `01_foundations`.

## 10. Estado y mantenimiento

Status:

```text
v0_1 - active transversal classification contract
```

Owner:

```text
Modulo 01 / Data Foundation governance
```

Este documento debe actualizarse cuando:

- aparezca una nueva familia de datos;
- cambie la raiz fisica activa de una familia;
- una capa pase de schema-only a dataset gobernado;
- una capa derivada sea promovida a full-universe;
- un nuevo Graphify leaf cubra evidencia historica antes excluida;
- o una policy especifica cambie la lectura de RAW, reference, context,
  feature o label.

## 11. Regla final

La auditoria RAW no puede quedar desplazada por capas derivadas.

La secuencia correcta es:

```text
RAW vendor/reference/context -> auditoria -> certificacion -> foundations -> derivados ->
features/labels -> research/backtest/ML/RL
```

Toda desviacion debe quedar escrita, versionada y justificada.
