# Cell Code - Quotes V2

Convencion para `00_data_certification_v2`:

- Cada notebook puede tener una o varias celdas lanzadera.
- La logica larga vive en `cell_code/quotes/*.py`.
- Los scripts deben leer configuracion desde `globals()` cuando sea posible.
- Los scripts no deben descargar ni mutar estado de produccion salvo que el notebook lo indique explicitamente.

Uso recomendado desde notebook:

```python
from pathlib import Path

SCRIPT = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification_v2\cell_code\quotes\04_universe_lifecycle_snapshot.py")
exec(SCRIPT.read_text(encoding="utf-8"), globals())
```
