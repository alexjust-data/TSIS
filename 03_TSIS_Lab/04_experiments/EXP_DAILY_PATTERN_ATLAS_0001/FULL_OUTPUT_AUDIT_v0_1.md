# Full Output Audit v0.1

Status: `pass` para evidencia descriptiva exploratoria.

No implica conocimiento validado, inferencia, probabilidad, estrategia, señal o
PnL.

## Operación e integridad

- `operation_final_manifest`: `pass`, exit code 0, 8/8 shards, 0 fallos;
- duración: 3.997,105 segundos;
- 11/11 artefactos: SHA-256, schema SHA-256, bytes y filas recalculados y
  coincidentes con `run_manifest.json`;
- 8/8 manifests y certificaciones de shard: `pass`;
- heartbeat final: `stage=complete`, `status=pass`, proceso finalizado.

## Scope independiente

- 4.824 tickers y 9.290.966 sesiones;
- fechas: 2005-01-03 a 2026-03-06;
- contra autoridad upstream: 0 ticker-fecha ausentes, 0 adicionales y 0 tickers
  ausentes o adicionales;
- 44.423 fuentes daily distintas y 0 rutas ausentes.

## Calidad y causalidad

- 12 fórmulas recalculadas, error absoluto máximo 0;
- cinco tablas sharded: 4.824/4.824 parts y una variante física de schema;
- 0 claves duplicadas o nulas en los 11 outputs;
- 0 infinitos o valores outcome no finitos;
- `future_split_factor` ausente de observables;
- 1.495 sesiones y 747 filas de trayectoria `invalid_ohlcv` segregadas;
- 0 activaciones, outcomes, eventos o peaks sobre filas inválidas;
- 0 mismatches de running high, peak o roles de conocimiento.

## Reconciliaciones directas

- 27 etiquetas por 21 offsets: 567 cohortes directas;
- D0 directo: 9.728.326 casos-etiqueta, igual a `activation_labels`;
- `activation_case_index`: 4.495.723 ticker-fecha, diferencia simétrica 0;
- 27 etiquetas por 6 eventos: 162 filas, casos por etiqueta exactos;
- D0 mismatch: 0; event-case mismatch: 0.

`cohort_statistics` representa todas las activaciones.
`cycle_cohort_statistics` es una vista secundaria: 422.042 episodios, 779.786
asignaciones etiqueta-episodio y separación mínima de 21 observaciones por
ticker, con 0 violaciones del cooldown 20.

## Lectura descriptiva seleccionada

- `gap_ge_30pct`: 13.488 casos; mediana close D+20 -15,2671%; P10/P90
  -60,0000%/+63,7847%; peak mediano D0; first red tras D0 mediano D+1;
- `gap_ge_50pct`: 8.129 casos; mediana close D+20 -18,1818%; P10/P90
  -65,6148%/+64,8505%; peak mediano D+1; first red tras D0 mediano D+1;
- breakout high previo día/semana/mes: medianas close D+20 -0,5405%, -0,6116%
  y -0,6173%; peaks medianos D+8, D+8 y D+7.

Los gaps contienen colas derechas extremas: sus medias D+20 son +1.417,8348% y
+2.045,3196% mientras las medianas son negativas. Deben estudiarse
conjuntamente media, mediana, cuantiles y casos reales; ninguna cifra aislada
describe la distribución completa.

## Incidentes de la auditoría

El primer intento dio falso `FAIL` porque el auditor heredaba la cardinalidad de
un probe de ocho tickers. `INC-20260825-010` fue registrado, corregido y cubierto
por regresión; la auditoría completa se repitió desde cero con `pass`.

El premanifest histórico conserva `git.dirty=true` y conteo 7, pero no enumera
las rutas. Los hashes de config, runner y upstream coinciden y el delta
comprometido desde la autorización es solo documental; esta cautela no altera
el PASS numérico ni el estado exploratorio. `INC-20260825-011` la declara y el
runner futuro ya persiste entradas, rutas y fingerprint porcelain.