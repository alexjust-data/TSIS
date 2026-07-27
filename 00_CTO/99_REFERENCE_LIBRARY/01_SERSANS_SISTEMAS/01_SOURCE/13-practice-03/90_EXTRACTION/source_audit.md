# Source Audit — 13-practice-03

## Resultado

`PASS_WITH_ANOMALIES`

| Control | Resultado |
|---|---:|
| Markdown principal | `practica_03_donchain.md` |
| Líneas | 1861 |
| PNG inspeccionados | 111 |
| Imágenes locales distintas enlazadas | 95 |
| Imágenes huérfanas | 16 |
| Referencias repetidas | 1 |
| Duplicados binarios | 1 grupo |

## Anomalías

- Referencia fuera del ZIP: `../12-practice-02/img/002.png`.
- `img/20.png` aparece dos veces en el Markdown.
- `img/95.png` y `img/96.png` son idénticas byte a byte.
- Las 16 imágenes huérfanas se inspeccionaron y no se eliminaron.
- Faltan los PDF, el `.ELD` y el audio/vídeo citados.

## Regla epistemológica

Las capturas prueban que una configuración o resultado fue mostrado. No prueban por sí solas reproducibilidad, robustez, validez fuera de muestra ni aplicabilidad a TSIS.
