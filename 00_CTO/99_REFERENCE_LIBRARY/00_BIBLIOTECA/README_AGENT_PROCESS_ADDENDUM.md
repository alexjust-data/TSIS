# README Addendum - PDFs Comerciales Y Texto Extraido

Este addendum corrige/precisa el proceso del `README.md` para libros comerciales o con copyright.

## Regla

No persistir una copia completa del texto extraido de un libro comercial salvo permiso explicito. La extraccion completa puede usarse como material temporal de trabajo para generar resumenes, indices y mapas, pero debe borrarse al terminar.

## Flujo Recomendado

```text
PDF original
  -> working_pages.jsonl temporal
  -> metadata.json
  -> toc.json
  -> page_stats.json
  -> agent_summary.md
  -> concept_index.md
  -> source_map.md
  -> borrar working_pages.jsonl
```

Los agentes deben localizar informacion mediante:

```text
1. 02_TSIS_BACKTEST_ENGINE_CONCEPT_INDEX.md
2. summaries/<book_id>_agent_summary.md
3. index/<book_id>_concept_index.md
4. index/<book_id>_source_map.md
5. PDF original por numero de pagina
```

## Control De Calidad Adicional

```text
[ ] El PDF original sigue intacto.
[ ] Existe metadata.json.
[ ] Existe toc.json.
[ ] Existe page_stats.json.
[ ] Existe resumen con menu enlazado.
[ ] Existe concept_index.md.
[ ] Existe source_map.md.
[ ] No queda working_pages.jsonl persistido.
```

## Aplicado Al Piloto

Para `successful_algorithmic_trading`, el texto completo extraido se uso solo como material temporal y fue eliminado despues de generar los artefactos derivados.
