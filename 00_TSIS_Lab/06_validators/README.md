# 06_validators

Fecha: 2026-07-06
Estado: skeleton operativo inicial

## Rol

Esta carpeta contiene validadores ejecutables del Lab.

Un validador no descubre eventos y no decide si hay edge. Su funcion es bloquear runs que no cumplen contratos de evidencia, leakage, calidad, lineage o trazabilidad visual.

## Validador Visual DAS / TSIS

```text
validate_visual_inspection_manifest.py
```

Valida que un run tenga evidencia visual label-level:

```text
visual_inspection_manifest.parquet
label_id unico
signal_name por cada metrica medida
source_field que conecta la etiqueta con el dato medido
bbox/anchor en pixeles
imagenes existentes y no vacias
renderer_source_path + renderer_source_hash
no solape entre cajas de etiquetas dentro de la misma imagen
```

Lectura correcta:

```text
PNG existe != evidencia visual suficiente
EXPORT_MANIFEST.csv existe != manifest label-level suficiente
```

El run solo pasa si cada senal que alimenta el funnel/outcome tiene una etiqueta trazable y no solapada.
