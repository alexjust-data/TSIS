# Ohlcv 1m Split-Normalized - Full Universe Audit Readout `v0_1`

## 1. Rol

Este documento cierra la pregunta que quedaba abierta despues del piloto:

- no solo si la semantica de `1m_split_normalized` parecia correcta en una muestra fuerte;
- sino si los casos de split del universo `1m` quedaban resueltos al nivel mas exhaustivo que permite la cobertura real del dataset.

## 2. Universo auditado

La auditoria exhaustiva se hizo contra:

- todas las tablas de `splits` disponibles en fuentes maestras;
- intersectadas con cobertura real de `D:\ohlcv_1m`;
- y evaluadas con una ventana por evento de:
  - mes previo
  - mes del evento
  - mes posterior

La unidad auditada no fue "ticker bonito" ni "muestra pedagógica".

Fue:

- `ticker + execution_date de split`

en todo el universo con intersección real contra `1m`.

## 3. Regla semántica auditada

La regla contractual auditada fue exactamente esta:

- `future_split_factor(date_t) = producto de todos los split_ratio con execution_date > date_t`

La auditoría exhaustiva no intentó probar una intuición visual difusa.

Intentó falsar esta lógica con invariantes concretos por evento.

## 4. Resultado agregado

Meta global:

- `split_files_seen = 4824`
- `non_empty_split_files_with_1m_ticker = 1876`
- `total_event_cases = 3335`

Resultado por estado:

- `PASS = 2280` (`68.37%`)
- `FAIL = 0` (`0.00%`)
- `NO_PRE_COVERAGE = 164` (`4.92%`)
- `NO_POST_COVERAGE = 151` (`4.53%`)
- `NO_1M_COVERAGE = 740` (`22.19%`)

## 5. Qué significa exactamente este resultado

### Lo fuerte

- No apareció **ningún** caso `FAIL`.

Eso significa que, en todos los casos donde la auditoría encontró cobertura suficiente para comprobar los invariantes:

- no apareció ni una sola violación semántica.

### Lo que no debe malinterpretarse

`NO_PRE_COVERAGE`, `NO_POST_COVERAGE` y `NO_1M_COVERAGE` no significan:

- split mal resuelto.

Significan:

- falta de historia suficiente en el dataset para falsar una de las dos caras del evento;
- o ausencia total de historia `1m` para ese ticker/evento.

## 6. Veredicto correcto

La formulación institucional correcta es esta:

- **100% de los casos plenamente auditables pasan**

No:

- "100% de todos los eventos del mundo quedaron demostrados"

porque un subconjunto del universo no tiene suficiente cobertura empírica en `1m` para esa prueba.

Pero sí podemos afirmar, con precisión, que:

- **entre todos los casos del universo que el dataset permite auditar de forma completa, el porcentaje de paso es del 100% y el de fallo es 0%**.

## 7. Por qué la auditoría es suficientemente fuerte

Esta no es una revisión superficial.

Se apoya en tres niveles acumulativos:

### A. Piloto semántico de capa

- casos positivos fuertes
- controles pre-evento
- controles post-evento

### B. Consumidor mínimo real

- `intraday_regime_features`

que demostró que:

- `raw` fabricaba falsos gaps y falsos shocks cross-session;
- y `split_normalized` los neutraliza.

### C. Barrido full-universe

- `3335` eventos auditados
- `0` fallos
- y notebook selector para inspección caso por caso

## 8. Notebook de supervisión total

El inspector puede navegar cualquier caso del universo auditado en:

- [ohlcv_1m_split_normalized_full_universe_audit_notebook_v0_1.ipynb](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_notebook_v0_1.ipynb>)

Ese notebook permite:

- filtrar por `status`
- elegir `ticker`
- elegir `evento`
- ver metadatos del caso
- ver la serie `raw`
- ver la serie `split_normalized`
- y ver la trayectoria de `future_split_factor`

sin depender de PNGs fijos ni de una muestra reducida.

## 9. Consecuencia institucional

Para el problema concreto:

- "resolver correctamente los splits en `1m` para comparaciones entre sesiones"

la auditoría ya queda cerrada al máximo nivel razonable que permite la cobertura real del dataset.

La frase prudente y fuerte a la vez es:

- los casos de split auditables del universo `1m` quedan resueltos sin fallos observados;
- y los casos no plenamente auditables quedan clasificados explícitamente como límites de cobertura, no como errores semánticos.

## 10. Qué sigue abierto y qué no

### Ya no queda abierto

- demostrar que la semántica de split funciona;
- demostrar que el piloto no era un artefacto bonito;
- demostrar que un consumidor real deja de ver shocks falsos.

### Sí puede seguir abierto en el futuro

- ampliar cobertura materializada;
- usar la misma capa en más consumidores;
- o cerrar otras auditorías de `1m` no relacionadas con splits.

Pero la deuda concreta de:

- "probar exhaustivamente que los casos de split se resuelven bien"

queda ya cerrada para el universo auditable disponible.
