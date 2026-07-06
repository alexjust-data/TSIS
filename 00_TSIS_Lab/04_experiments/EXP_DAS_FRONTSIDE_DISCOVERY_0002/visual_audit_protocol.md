# Visual Audit Protocol - EXP_DAS_FRONTSIDE_DISCOVERY_0002

Fecha: 2026-07-06
Estado: draft_operativo

## Objetivo

Garantizar que humano y maquina entienden igual cada anchor:

```text
scanner gate
first push high
first dip low
rebreak
fake rebreak
```

La imagen no es decoracion. Es evidencia de auditoria.

## Regla Principal

Toda marca visual debe pintarse desde el mismo dato que alimenta el calculo.

```text
calculo del anchor = coordenada visual del anchor
```

No se permite colocar puntos, cruces o cajas a ojo.

## Requisitos Minimos De Cada Chart

Cada PNG debe incluir:

```text
ticker
session_date
visual_price_source
state
maxpush
first_push
scanner/momentum trigger
rebreak/fake rebreak state
```

Cada label debe tener:

```text
label_id
anchor_type
ts o bar_index
price
porcentaje principal
numero de barras/minutos desde anchor anterior
volumen si aplica
calculation_rule
```

## Vista 1m

El chart debe cumplir `LOCAL_RULES.md`.

No se permite:

```text
usar raw 1m sin declarar repair/guard state
pintar mechas raw sospechosas como verdad
recortar raw contra quotes sin scale guard
ocultar scale mismatch
```

## Labels Obligatorios Iniciales

```text
scanner_gate
first_push_high
first_dip_low
rebreak_confirmed o fake_rebreak
```

Si no hay rebreak, no se debe inventar una cruz azul.

Si hay fake rebreak, se pinta como fake y se explica la razon:

```text
close_not_above_level
volume_not_confirmed
wick_only
failed_hold
```

## Auditoria Humana

Un caso queda como `human_review_required` si:

```text
first dip ambiguo
rebreak dudoso
fake rebreak dudoso
raw/quotes scale mismatch
quote/trade coverage insuficiente
labels se solapan o no son legibles
algoritmo contradice lectura humana
```

## Muestras Visuales Obligatorias

Para cada sweep:

```text
25 casos aleatorios capturados
25 casos con recovery
25 casos sin recovery
25 fake rebreak
25 destruction cases
25 casos con data quality sospechosa si existen
```

El objetivo es revisar sesgos del detector antes de confiar en estadisticas masivas.

## Manifest Visual

Cada lote de imagenes debe tener manifest:

```text
visual_inspection_manifest_id
experiment_id
sweep_id
image_path
ticker
session_date
case_id
visual_price_source
scale_guard_state
anchor_ids_rendered
renderer_version
created_utc
human_review_status
```
