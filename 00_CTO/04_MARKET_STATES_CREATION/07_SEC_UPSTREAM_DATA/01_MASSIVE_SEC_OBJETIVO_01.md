Tienes razón: con acceso a Massive limitado a un mes, mi planteamiento anterior era demasiado conservador. **El probe de 250 no debe significar “esperar a encontrar conflictos después”**. Debe servir únicamente para medir cobertura, schema y tamaño antes de expandir la descarga a los 4.824 durante este mismo mes.

Y una precisión: cuando termine la suscripción perderemos acceso a **Massive**, no a SEC.gov, que sigue siendo público. Lo que perderemos son sus extracciones estructuradas y sus textos procesados.

## Estrategia correcta: descarga “sunset-safe”

Durante este mes debemos conservar todo aquello que:

1. pueda ser necesario más tarde;
2. sea estructurado y relativamente pequeño;
3. no podamos reconstruir fácilmente nosotros;
4. ayude a seleccionar o interpretar la descarga SEC posterior.

## Auditoría previa de datos Massive no-SEC ya presentes en `G:\TSIS\data`

Auditoría ejecutada el `2026-08-21`. La verificación combina inventario físico,
muestras Parquet reales y los contratos/certificaciones vigentes de Data
Foundation. No se hizo una nueva materialización ni se abrió exhaustivamente
cada cabecera Parquet, porque las familias ya tienen evidencia certificada.

Massive es la continuidad del proveedor anteriormente denominado Polygon. Por
eso varias rutas y contratos existentes conservan todavía el nombre `Polygon`,
aunque correspondan a estas mismas familias de endpoints.

| Familia no-SEC | Evidencia física y cobertura ya disponible | Estado para este objetivo | Nueva descarga |
|---|---|---|---|
| All Tickers | `G:\TSIS\data\reference\all_tickers`; 3.109 snapshots, 649,14 MiB, `2005-01-02` a `2026-03-09`. El último snapshot contiene 5.258 filas. | **DISPONIBLE** para el horizonte histórico del universo. No es la autoridad final de pertenencia al universo. | **NO** hacer backfill ni duplicar. Solo incremental si un objetivo futuro supera `2026-03-09`. |
| Ticker Overview | `G:\TSIS\data\reference\overview`; 12.468 Parquet, 201,09 MiB, fechas nominales `2005-01-02` a `2026-03-09`; contiene CIK, FIGI, `share_class_shares_outstanding`, `weighted_shares_outstanding` y `market_cap`. | **DISPONIBLE, PERO NO PIT**. Es snapshot vendor secundaria; sus consultas históricas pueden incorporar conocimiento posterior. | **NO** hacer backfill ni snapshot nueva para este objetivo. Una futura captura actual requeriría un objetivo separado y solo serviría como benchmark. |
| Ticker Events | Autoridad primaria en `G:\TSIS\data\reference\events`: 12.468 Parquet, 45,21 MiB. Copia acotada en `G:\TSIS\data\additional\corporate_actions\ticker_events`: 4.824/4.824 archivos, 2.703 no vacíos, 5.158 eventos, 56,032% con evento. | **DISPONIBLE**. Los archivos vacíos son sentinels válidos; ausencia de evento no es ausencia de descarga. La copia `additional` es secundaria y no sustituye por sí sola la identidad canónica. | **NO** redescargar globalmente. |
| Splits | Autoridad primaria en `G:\TSIS\data\reference\splits`: 12.468 Parquet, 36,15 MiB. Copia acotada en `G:\TSIS\data\additional\corporate_actions\splits`: 4.824/4.824 archivos, 1.876 no vacíos, 6.283 eventos, 38,889% con split; 1.858 tickers con overlap exacto frente a `reference` y 18 en revisión. | **DISPONIBLE**. La cobertura inferior al 100% significa que muchos instrumentos no tuvieron split, no que falten sus archivos. | **NO** redescargar globalmente; conservar los 18 desacuerdos como revisión. |
| Balance Sheets | `G:\TSIS\data\additional\financials\balance_sheets`: 4.824/4.824 archivos, 4.813 no vacíos, 136.672 filas, 99,772% de cobertura efectiva, 119,42 MiB. Existe además la familia amplia en `G:\TSIS\data\financial\balance_sheets`. | **DISPONIBLE**, pero no es necesaria para reconstruir O/S o float. Usar `filing_date` para disponibilidad PIT cuando otro objetivo la consuma. | **NO** descargar para este objetivo. |
| Massive Float actual | No existe ruta física esperada en `reference`, `additional` o `financial`; tampoco existe registro, manifest o evidencia de una adquisición con `free_float` y `free_float_percent`. | **FALTA**. Solo será benchmark vendor actual, nunca fuente histórica PIT. | **SÍ, PERO EN RUN NO-SEC SEPARADO**: el agente Massive SEC no está autorizado; conservar únicamente cambios si se repite. |

Conclusión operativa de la auditoría:

```text
REUTILIZAR SIN DUPLICAR
All Tickers + Ticker Overview + Ticker Events + Splits + Balance Sheets

DESCARGA NO-SEC NUEVA MÍNIMA
Massive Float actual

AUTORIDAD DE O/S/FLOAT HISTÓRICO
sigue siendo SEC PIT; ningún dataset anterior la sustituye
```

## Contrato operativo del agente de descarga Massive SEC

Este bloque es la autoridad ejecutable para el agente encargado de la descarga.
Las secciones de inventario describen datos disponibles o trabajos futuros, pero
**no amplían esta autorización**.

### Puede descargar en el run Massive SEC

```text
AUTORIZADO GLOBALMENTE PARA LOS CIK DEL UNIVERSO

- EDGAR Index
- Form 3 y 3-A
- Form 4 y 4-A
- 8-K Disclosures
- Disclosure Taxonomy, una sola copia versionada
```

Estas familias son datos SEC estructurados o procesados por Massive. Deben
conservar accession, CIK, form, fechas disponibles, URL primaria SEC,
`retrieved_at_utc`, request ID, hashes y lineage del endpoint.

### Puede descargar solo después de su gate

```text
8-K Text
    PROBE 250
    -> medir cobertura, requests y bytes
    -> proyectar 4.824
    -> autorización humana o gate gobernado
    -> todos si caben; selección conservadora global si no

13F
    probe de varios trimestres
    -> demostrar filtro por CUSIP histórico
    -> medir cobertura, requests y bytes
    -> autorización humana o gate gobernado
    -> backfill filtrado si pasa
```

El probe no autoriza por sí solo la expansión. No se puede iniciar el backfill
completo de `8-K Text` o `13F` sin cerrar y persistir su gate.

### No puede descargar en el run Massive SEC

```text
DATOS NO-SEC YA PRESENTES EN G:
- All Tickers
- Ticker Overview
- Ticker Events
- Splits
- Balance Sheets

DATO NO-SEC AUSENTE, PERO FUERA DE ESTE RUN:
- Massive Float

OTRAS FAMILIAS FUERA DE ALCANCE:
- Risk Factors y Risk Taxonomy
- News
- Trades, Quotes y Aggregates
- Snapshots y Technical Indicators
- Short Volume y Short Interest
- IPOs y Dividends
- WebSockets
- 10-K Sections no requeridas por este objetivo
```

`Massive Float` permanece anotado como descarga pendiente porque falta en G:,
pero requiere un run no-SEC separado. El agente Massive SEC no puede incorporarlo
silenciosamente a su ejecución.

También queda prohibido:

```text
- sobrescribir datasets existentes en G:
- mezclar datos nuevos con roots históricos sin nueva versión lógica
- usar Ticker Overview como shares_outstanding_as_known PIT
- inferir O/S desde free_float / free_float_percent
- iniciar una descarga larga sin pre-manifest, PID, heartbeat, log vivo,
  monitor separado y final manifest
- ampliar endpoints o forms por conveniencia sin actualizar este contrato
```

### Precondiciones antes de la primera request

```text
1. confirmar por escrito que la licencia permite conservar y usar los datos;
2. congelar la lista exacta de CIK/instrumentos del universo;
3. fijar output root nuevo y versionado, sin overwrite;
4. crear pre-manifest, config, PID, heartbeat, log y monitor;
5. fijar rate limit, retries, backoff, checkpoint y resume idempotente;
6. registrar requests, bytes, filas, errores, hashes y cobertura;
7. cerrar con final manifest y reconciliación contra el target exacto.
```

## Adquisición Massive SEC para los 4.824 durante el mes

Esta tabla resume únicamente el alcance SEC del agente. No contiene autorización
para las familias no-SEC inventariadas anteriormente.

| Dataset Massive SEC | Alcance / acción |
|---|---|
| EDGAR Index | Historia completa disponible para todos los CIK del universo |
| Form 3 / 3-A | Historia completa disponible |
| Form 4 / 4-A | Historia completa disponible |
| 8-K Disclosures | Todos los registros disponibles del universo |
| Disclosure Taxonomy | Una sola copia |

La auditoría elimina la descarga preventiva duplicada de identidad, ticker events,
splits y balance sheets. Los datos existentes quedan como evidencia vendor
secundaria independiente; cualquier futura actualización debe ser incremental y
justificada por una extensión temporal concreta.

## Aclaración nueva: Massive no entrega `shares_outstanding_as_known` PIT

El endpoint más cercano es:

```text
GET /v3/reference/tickers/{ticker}
```

Del resultado debemos conservar únicamente como snapshot vendor secundaria:

```text
ticker
cik
composite_figi
share_class_figi
share_class_shares_outstanding
weighted_shares_outstanding
market_cap
retrieved_at_utc
request_id
```

Si en un objetivo futuro separado se captura una snapshot nueva, la política se
limitará al estado observado en su `retrieved_at_utc`. En este objetivo no se
descargará de nuevo Ticker Overview. Nunca se debe ejecutar un backfill por
`date=YYYY-MM-DD` para construir historia PIT: Massive documenta que la fecha histórica se compara con
`period_of_report`, por lo que una consulta puede incorporar información de un
filing presentado posteriormente. Esa salida puede contener look-ahead y no
equivale a `shares_outstanding_estimate_as_known`. [Massive Ticker
Overview](https://massive.com/docs/rest/stocks/tickers/ticker-overview).

Las snapshots se etiquetarán explícitamente:

```text
source_state = MASSIVE_CURRENT_VENDOR_SNAPSHOT
pit_history_authority = false
allowed_role = current benchmark and reconciliation only
```

No se añade Income Statements a la descarga mínima para resolver O/S. Sus
campos `basic_shares_outstanding` y `diluted_shares_outstanding` son promedios
ponderados del periodo, no acciones efectivamente outstanding en una fecha, y
su `filing_date` puede corresponder a un filing posterior que volvió a incluir
el periodo. Solo podrían incorporarse en otro objetivo como proxy declarado.
[Massive Income
Statements](https://massive.com/docs/rest/stocks/fundamentals/income-statements).

Tampoco se derivará O/S mediante:

```text
free_float / free_float_percent
```

porque Massive Float es actual, experimental, utiliza una metodología vendor y
redondea el porcentaje. La autoridad histórica seguirá siendo el resolver SEC
PIT con `measurement_at`, `available_at`, `eligible_from_session`, accession y
reconciliación de clase.

## El caso especial de 8-K Text

No debemos esperar a descubrir los conflictos después de cancelar Massive.

La secuencia correcta es:

```text
EDGAR Index global
+
8-K Disclosures global
        ↓
identificar todos los 8-K potencialmente relevantes
        ↓
descargar su 8-K Text durante este mes
```

Filtraríamos conservadoramente eventos relacionados con:

```text
offerings
unregistered equity sales
warrant exercises
convertibles
mergers y acquisitions
de-SPAC
changes in control
share-class modifications
reverse splits
charter amendments
repurchases
capital restructurings
other events relacionados con capital
```

Pero existe riesgo de que la clasificación de Massive omita algún evento. Por eso haría:

```text
PROBE 250
→ medir número y tamaño de todos los 8-K Text
→ extrapolar a 4.824
```

Si el volumen comprimido es asumible, **descargaría todos los 8-K Text de los 4.824**. Es mucho más seguro y debería pesar bastante menos que los filings completos porque Massive entrega solamente los Items procesados, no todo el submission ni sus exhibits. [Massive 8-K Text](https://massive.com/docs/rest/stocks/filings/8-k-text).

Si la proyección excede nuestro presupuesto físico:

```text
1. conservar todos los 8-K Disclosures;
2. conservar todos los textos de categorías relevantes;
3. añadir todos los 8-K de issuers complejos;
4. añadir una ventana alrededor de lifecycle events;
5. mantener accession + SEC URL para recuperar el filing original después.
```

Por tanto, un conflicto entre los primeros 250 **no implica automáticamente descargar todos los 8-K**. La decisión debe tomarse por proyección de cobertura y almacenamiento, pero antes de que termine el mes.

## Form 3 y Form 4: descarga global

Aquí no dejaría dudas:

```text
Form 3 completo para los CIK del universo
Form 4 completo para los CIK del universo
```

Son las extracciones Massive que más pueden ayudarnos posteriormente con ownership. El endpoint ya distingue derivados, ownership directo/indirecto, posición posterior, roles, transaction codes y footnotes. [Massive Form 3](https://massive.com/docs/rest/stocks/filings/form-3), [Massive Form 4](https://massive.com/docs/rest/stocks/filings/form-4).

No esperaría a que el resolver SEC detecte un conflicto.

## EDGAR Index: también global

Descargaría todo el índice correspondiente a nuestros CIK, no el EDGAR global completo.

```text
CIK del universo
→ todos los accessions disponibles
→ todas las form families
→ filing date
→ form type
→ SEC URL
```

Es metadata compacta y permitirá decidir posteriormente qué documentos SEC faltan, aunque Massive ya no esté disponible. [Massive EDGAR Index](https://massive.com/docs/rest/stocks/filings).

No limitaría anticipadamente los forms porque podríamos necesitar más tarde:

```text
DEF 14A
20-F
6-K
SC 13D/G
Forms 3/4/5
10-K/Q
8-K
S-1/F-1
S-3/F-3
424B*
EFFECT
POS AM
15/25
```

## 13F: también debemos decidirlo durante este mes

Si queremos institutional ownership en el futuro, no podemos dejarlo para después.

Pero el endpoint 13F solo permite filtrar principalmente por `filer_cik` y fecha, no directamente por los CUSIP de nuestro universo. Por ello:

```text
13F por ventanas temporales
→ procesar página en streaming
→ cruzar inmediatamente con CUSIP histórico TSIS
→ conservar solamente coincidencias
→ registrar hashes, filas y cobertura
```

Primero haría un probe de varios trimestres. Si Massive realmente ofrece historia suficiente, ejecutaría el backfill completo durante el mes. Si no la ofrece, quedará documentado que necesitaremos obtener 13F desde SEC posteriormente. [Massive 13-F](https://massive.com/docs/rest/stocks/filings/13-f-filings).

## Qué seguiría sin descargar

Incluso con acceso temporal, no aporta valor suficiente para este objetivo:

```text
Risk Factors
Risk Taxonomy
News
Trades
Quotes
Aggregates
Snapshots
Technical Indicators
Short Volume
Short Interest
IPOs
Dividends
WebSockets
10-K Business/Risk sections
```

`10-K Sections` no ofrece actualmente las tablas de ownership que necesitamos. No lo descargaría solo por miedo a perder acceso.

Balance Sheets ya existe con cobertura efectiva certificada de `99,772%`. No se
descargará de nuevo para float/O/S. Si EV/net cash pasa a ser un objetivo
inmediato, se abrirá primero un contrato de consumo sobre la familia existente.

## Plan para el mes

```text
DÍAS 1–2
- comprobar términos de conservación tras cancelar Massive;
- probe 250;
- medir historia, filas, requests y bytes;
- proyectar 4.824.

DÍAS 3–10
- adoptar desde G: All Tickers, Ticker Events y Splits;
- no duplicar sus backfills;
- EDGAR Index global del universo;
- Form 3 global;
- Form 4 global;
- 8-K Disclosures y taxonomía.

DÍAS 11–20
- 8-K Text según presupuesto;
- preferentemente todos si la proyección es asumible;
- si no, selección conservadora completa.

DÍAS 21–25
- probe y posible backfill 13F filtrado por CUSIP;
- reconciliación Massive–SEC.

DÍAS 26–30
- segunda pasada incremental;
- reparar páginas fallidas;
- certificar el handoff separado de Massive Float, sin descargarlo en este run;
- certificar manifests, hashes y cobertura;
- comprobar que todo puede utilizarse sin Massive.
```

Antes de ejecutar nada debemos verificar contractualmente que la licencia permite conservar y usar los datos descargados después de terminar la suscripción. No conviene descubrir esa restricción después del backfill.

La decisión corregida es:

```text
250 = PROBE DE TAMAÑO Y COBERTURA
      no límite de adquisición

4.824 = DESCARGA ESTRUCTURADA DURANTE ESTE MES

8-K TEXT = TODOS SI CABEN;
           SI NO, SELECCIÓN GLOBAL CONSERVADORA AHORA

CONFLICTOS FUTUROS = se resolverán con el inventario,
                     los datos estructurados Massive
                     y el enlace al primary SEC
```

Así no dependemos de tener Massive cuando el resolver alcance los últimos tickers.
