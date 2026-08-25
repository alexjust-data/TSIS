# CHANGELOG

## 2026-08-25

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
- Estado rebajado a `implementation_in_progress` hasta nuevos probes y full PASS.

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
