# TSIS (Trading Scientific Intelligence System)

Primero leer: [START_HERE.md](START_HERE.md)

Arranque recomendado de Codex para TSIS:

```powershell
powershell -ExecutionPolicy Bypass -File C:\TSIS_Data\START_CODEX_TSIS_AUTONOMOUS.ps1
```

System and data pipeline for Small Cap stocks.

## Nota obligatoria sobre datos fisicos y minutos

Todo agente debe leer `E:/TSIS/data/README.md` como parte del contexto base del
proyecto. Ese README gobierna el plano fisico de datos.

Para trabajos con minutos/1m, la raiz fisica canonica es:

```text
E:/TSIS/data/ohlcv_1m
```

Motivo: TSIS ya tuvo un incidente real de velas 1m imposibles y reparacion
quote-guarded. La regla evita que agentes futuros usen rutas historicas,
asuman que el raw esta corregido, o ignoren overlays/manifests oficiales.