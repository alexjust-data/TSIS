# Ohlcv 1m Split-Normalized Pilot Manifest `v0_2`

## 1. Veredicto

El primer lote real de `1m_split_normalized` ya queda fijado.

Se ha construido sobre la interseccion valida:

- `1m`
- `daily`
- y split activo dentro de la ventana real disponible

No se ha elegido por intuicion.

Se ha elegido por cobertura real comprobada.

## 2. Tamano

El lote queda fijado con la misma escala minima que el piloto de `daily_adjusted`:

- `10` casos

Composicion:

- `4` `reverse split`
- `4` `forward split`
- `2` `control`

## 3. Casos seleccionados

### Reverse split

- `BXRX | 2022-12 | 40 -> 1`
- `COSM | 2022-12 | 25 -> 1`
- `CEI | 2022-12 | 50 -> 1`
- `BNGO | 2025-01 | 60 -> 1`

### Forward split

- `EFSH | 2025-01 | 1 -> 2`
- `SAVA | 2023-12 | 10 -> 14`
- `PD | 2006-03 | 1 -> 2`
- `LIVE | 2014-02 | 1 -> 3`

### Controls

- `BXRX | 2022-11`
- `BNGO | 2025-02`

## 4. Por que estos casos

La cesta no busca solo variedad nominal.

Busca demostrar:

- shocks mecanicos recientes y muy visibles
- al menos un tramo historico mas antiguo
- mas de un ratio de split
- y controles del mismo ticker en meses sin split activo

## 5. Que prueba este lote

Debe permitir verificar:

- que `1m raw` rompe escala entre sesiones en los meses con split
- que `1m_split_normalized` neutraliza esa ruptura
- que los controles permanecen neutros
- y que la comparabilidad queda alineada con la disciplina ya fijada en `daily`

## 6. Artefacto material

CSV asociado:

- `01_foundations/dataset_registry/1m/ohlcv_1m_split_normalized_pilot_manifest_v0_2.csv`

## 7. Siguiente paso

El siguiente paso correcto ya no es volver a discutir el lote.

Es:

- materializar este piloto
- y producir una lectura corta caso por caso de `raw` vs `split_normalized`
