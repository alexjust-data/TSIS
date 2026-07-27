# Source Audit — Practice 04

## Universo

- Markdown: `practica_04_donchain.md` — 1997 líneas.
- Imágenes inspeccionadas: 245.
- Imágenes únicas enlazadas: 190.
- Imágenes huérfanas auditadas: 55.
- Referencias repetidas: 6.
- Referencias rotas: 0.
- Duplicados binarios exactos: 0.

## Anomalías

- La numeración no es continua y contiene `299.png`, `2004.png` y `2005.png`.
- Coexisten `162.jpg` y `162.png` como archivos distintos.
- Hay 55 imágenes no enlazadas; se conservaron porque incluyen tablas, superficies, configuraciones y gráficos relevantes.
- El Markdown enlaza `OPTI4.xlsx` situado fuera de este ZIP.
- Sin audio original, los bloques editoriales no pueden atribuirse literalmente al profesor.

## Veredicto

`PASS_WITH_ANOMALIES`. Todas las imágenes tienen estado explícito y ninguna anomalía invalida la extracción semántica; sí limita reproducibilidad y atribución literal.
