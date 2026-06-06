# Ohlcv 1m Historical Closeout vs Lt1b Scope Reconciliation `v0_1`

## 1. Rol

Este documento no reaudita `ohlcv_1m` desde cero.

Su funcion es otra:

- reconciliar el cierre historico raw de `1m`;
- con el marco moderno del proyecto como universo `lt1b`;
- y con el cierre nuevo de `ohlcv_1m_split_normalized`.

La pregunta que resuelve es concreta:

- como debe leerse hoy el cierre historico de `1m` sin mezclar una policy valida con porcentajes cuyo alcance no quedo materializado como `<1B>` explicito.

## 2. Documentos leidos para esta reconciliacion

### Universo y corte

- `01_research/01_auditoria_RAW_DATA/00_data_certification/00_descarga_universo.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/00_auditoria_general.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/01_auditoria_1B_general.md`

### Auditoria y certificacion historica de `1m`

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/ohlcv_1m/00_auditoria_ohlcv_1m.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/ohlcv_1m/04_ohlcv_1m_closeout.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/1m/00_1m_current_state.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/1m/02_1m_quality_policy.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/1m/03_1m_closeout.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/global_metrics/01_global_metrics_tables_traceable.md`

### Cierre moderno de splits

- `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_final_readout_v0_1.md`
- `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1.md`

## 3. Lo que si queda claro del universo del proyecto

El proyecto no se esta definiendo como all-cap generico.

Los documentos de universo y cobertura fijan explicitamente un marco `lt1b`, por ejemplo en:

- `01_auditoria_1B_general.md`

ahora mismo con referencias como:

- `market_cap_cutoff_lt_1b_active_inactive.parquet`
- `Descarga para universo smallcaps <1B`
- y la cobertura de:
  - `daily`
  - `ohlcv_1m`
  - `quotes`
  - `trades`

dentro de ese universo objetivo.

Por tanto, el marco institucional moderno del proyecto si es:

- `lt1b`

## 4. Donde estaba el matiz real

El matiz no era:

- que `1m` no perteneciera conceptualmente al proyecto `lt1b`

El matiz era otro:

- el cierre historico de calidad raw de `1m` dejo su policy y sus porcentajes sobre un artefacto operativo `full-scope`;
- no sobre un artefacto paralelo y trazable donde esos mismos porcentajes quedaran recalculados nominalmente para `<1B>`.

Este punto ya esta escrito explicitamente en la certificacion historica:

### `03_1m_closeout.md`

- no se encontro un artefacto ya materializado con filtro explicito `<1B>` para ese cierre
- la policy puede consumirse ya
- pero las proporciones exactas deben declararse como `full-scope`
- si mas adelante hace falta cifra exacta `<1B>`, hay que aplicar la misma policy sobre universo filtrado, no reinventar la auditoria

### `02_1m_quality_policy.md`

- las cuentas de taxonomia `vw` son `full-scope`
- no deben presentarse como proporciones finales `<1B>` sin hacer el filtro explicito

### `01_global_metrics_tables_traceable.md`

- la tabla `1m_operational` se declara como `full-scope operativo`
- y no debe venderse como corte `<1B>` recalculado

## 5. Que parte del cierre historico de `1m` sigue siendo valida

La reconciliacion no exige tirar el cierre viejo.

Su parte fuerte sigue siendo valida:

- la identificacion de problemas dominantes:
  - `schema`
  - `vw`
  - `parse_invalid`
  - `price_invalid`
- la taxonomia:
  - `good`
  - `review`
  - `bad`
- la logica de rescate frente a cuarentena
- y la conclusion de que la cuarentena dura es pequena en comparacion con el rescate

Eso sigue valiendo como:

- policy de lectura del raw `1m`
- y lectura causal del bloque

## 6. Que parte no debe repetirse hoy sin matiz

Lo que no debe repetirse hoy como si ya fuera `lt1b` demostrado son:

- los porcentajes exactos del cierre historico raw

por ejemplo:

- `RESCUE_SCHEMA_PLUS_VW = 83.65%`
- `RESCUE_SCHEMA_ONLY = 16.11%`
- `QUARANTINE_PARSE_INVALID = 0.2397%`
- `QUARANTINE_PRICE_INVALID = 0.0040%`

La razon no es que esos numeros sean falsos.

La razon es otra:

- esos numeros pertenecen al cierre historico `full-scope`
- no a un recalculo nominal y trazable sobre un materializado `<1B>` especifico

## 7. Donde entra `ohlcv_1m_split_normalized`

El cierre nuevo de `ohlcv_1m_split_normalized` no contradice el cierre historico raw.

Resuelve otra deuda:

- que los splits no contaminen comparaciones entre sesiones ni consumidores cross-session

El estado moderno correcto de `1m` debe leerse en dos capas:

### Capa A. Raw quality historical closeout

Responde a:

- que problemas de calidad estructural y economica dominan en `1m raw`

### Capa B. Split-normalized modern closeout

Responde a:

- si la comparabilidad cross-session queda bien resuelta frente a splits

No son cierres redundantes.
Son cierres complementarios.

## 8. Lectura institucional correcta hoy

La lectura correcta del bloque `1m` es esta:

1. el proyecto institucional vive en marco `lt1b`
2. el cierre historico raw de `1m` sigue siendo valido en policy y causalidad
3. sus proporciones historicas deben declararse como `full-scope` salvo recalculo explicito `<1B>`

## Estado posterior

Ese recalculo explicito `<1B>` ya existe ahora en:

- [raw_1m_lt1b_closeout_recalculation_v0_1.md](/C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/minute/raw_1m_lt1b_closeout_recalculation_v0_1.md)

Por tanto, este documento ya no debe leerse como una nota de deuda abierta, sino como la explicacion institucional de por que el recorte `<1B>` hacia falta y como debe convivir con el closeout raw historico `full-scope`.
4. la deuda moderna de splits ya quedo cerrada exhaustivamente sobre el universo auditable
5. por tanto, el bloque `1m` ya no esta abierto en definicion base, sino en reconciliacion de alcance y uniformidad final

## 9. Que queda pendiente si quisieramos precision `<1B>` estricta en raw `1m`

Si en el futuro quisieramos afirmar:

- “esta es la distribucion exacta raw de calidad de `1m` dentro de `<1B>`”

entonces faltaria una pieza concreta:

- recalcular la policy historica raw de `1m` sobre un artefacto de universo filtrado `<1B>` explicitamente materializado

Importante:

- eso no exigiria reinventar la auditoria;
- solo reaplicar la misma policy sobre el alcance exacto que hoy queremos citar

## 10. Veredicto

La reconciliacion correcta no es:

- negar el cierre historico de `1m`

Ni tampoco:

- reutilizar sus porcentajes `full-scope` como si ya fueran porcentajes `<1B>`

La reconciliacion correcta es:

- conservar la policy y la lectura causal del cierre historico raw;
- declarar con precision que sus proporciones eran `full-scope`;
- y situar el cierre nuevo de `ohlcv_1m_split_normalized` como la capa moderna que ya resolvio la deuda de splits dentro del marco institucional actual.
