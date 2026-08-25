# CHANGELOG

## 2026-08-25

- Invalidado científicamente `20260825_full_v0_1`: sus estadísticas consumían
  la capa local con doble ajuste de splits. El motor ahora lee exclusivamente
  `G:/TSIS/data/ohlcv_daily` (Massive `adjusted=true`), con regresión IBG y probe
  production-equivalent de 8/8 shards PASS; el full corregido queda pendiente.

- Cambiada exclusivamente la fuente de velas del primer gráfico a
  `G:/TSIS/data/ohlcv_daily` (`o/h/l/c/v`, Massive `adjusted=true`), manteniendo
  separadas y sin recálculo las etiquetas y estadísticas del run existente.

- Añadido debajo del visor estadístico un segundo gráfico OHLCV read-only para
  el mismo ticker y periodo, alimentado directamente por
  `G:/TSIS/data/ohlcv_daily_adjusted` con OHLC adjusted canónico y sin
  activaciones, eventos, outcomes ni recálculo de estadísticas.

- Ampliado el explorador local con catálogo visible de 5 familias y reconciliación
  exacta de sus 27 etiquetas materializadas.
- Eliminada la mini-gráfica agregada `Trayectoria mediana` y aclarada la carga
  inicial de 90 casos recientes frente al total censado, con paginación incremental.
- Enlazadas las etiquetas D0 al gráfico: cada selección conserva el caso, cambia
  la cohorte activa y marca todas sus ocurrencias en la vida daily del ticker.
- Sustituido el contexto fijo -120/+60 por toda la historia disponible, manteniendo
  separados los outcomes retrospectivos D0..D+20 y el panel inferior de volumen.
- Invalidado y aislado `20260824_full_v0_1` tras auditoría científica posterior.
- Corregida la exclusión de filas inválidas en outcomes, peaks y running highs.
- Normalizado el schema físico OHLCV y eliminado `future_split_factor` de X.
- Canonizado lineage raw y añadido commit, hashes, schemas y upstream al manifest.
- Separadas las cohortes directas del 100% de activaciones de los ciclos cooldown.
- Añadidas estadísticas directas de pico, first red day y debilidad por etiqueta.
- Reforzado el certificador con scope exacto, schemas, outcomes y artifacts.
- Instrumentado el wrapper largo con premanifest completo, PID manifest, heartbeat
  latest/JSONL, monitor compacto, stop command y final operativo.
- Sustituido el gráfico estático por velas TradingView interactivas con volumen,
  zoom, desplazamiento, cursor, contexto anterior/posterior y marcas fuera de mechas.
- Corregida la selección de datos de la app para exigir certificación terminal
  `pass`: prioriza el full PASS más reciente, cae al probe PASS más reciente y
  rechaza runs incompletos, fallidos o con certificación ilegible.
- Ejecutado `20260825_full_v0_1` en 3.997,105 s: 8/8 shards y cierre
  operacional `pass`.
- Certificación terminal e auditoría independiente `pass`: 12 fórmulas con
  error máximo 0, 4.824/4.824 parts con un schema y cero infinitos.
- Publicado `FINAL_CENSUS_READOUT_v0_2` con activaciones directas, tiempos de
  eventos y separación explícita de ciclos cooldown.
- Registrado `INC-20260825-011` y reforzado el premanifest futuro con rutas dirty y fingerprint porcelain.
- Persistido el plan v0.2 para eliminar joins globales repetidos y habilitar shards reutilizables.
- Promovido el experimento a `exploratory_report_ready`; sigue siendo evidencia
  descriptiva, no conocimiento validado.

## 2026-08-24

- Iniciado `Daily Pattern Discovery Atlas v0.1` como censo descriptivo daily
  discovery-first del universo auditado de 4.824 tickers.
- Fijados límites contra backtest, probabilidad, señales, ejecución y PnL.
- Incorporadas las ideas daily observables de Stephen Dux como lentes candidatas,
  sin promocionarlas a eventos validados.
- Ejecutado y certificado el censo completo `20260824_full_v0_1`: 4.824 tickers,
  9.290.966 sesiones, 422.042 episodios y cobertura 2005-01-03 a 2026-03-06.
- Añadidos readout reproducible, auditoría terminal, motor sharded, tests y
  explorador visual local con navegación desde cohortes hasta velas daily.
