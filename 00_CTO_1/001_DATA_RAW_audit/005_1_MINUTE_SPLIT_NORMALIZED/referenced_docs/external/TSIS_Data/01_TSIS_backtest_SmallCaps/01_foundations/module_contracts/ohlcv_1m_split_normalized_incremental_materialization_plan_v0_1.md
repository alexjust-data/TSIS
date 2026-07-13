# Ohlcv 1m Split-Normalized Incremental Materialization Plan `v0_1`

## 1. Principio

`1m_split_normalized` no debe nacer como full-universe ciego.

Debe nacer como capa incremental guiada por consumidores reales.

## 2. Fases

### Fase 1

Smoke test tecnico:

- materializar unos pocos `ticker-month`
- verificar schema
- verificar factores de split

### Fase 2

Piloto semantico:

- escoger tickers con reverse split y split activo dentro del rango `1m`
- incluir controles sin eventos
- verificar que la capa cambia donde debe y no cambia donde no debe

### Fase 3

Primer consumidor intradia real:

- pipeline de features o estado de regimen que cruce sesiones

### Fase 4

Expansion incremental:

- por `ticker-month`
- priorizada por el universo realmente usado por el consumidor

### Fase 5

Solo despues:

- evaluar si compensa promocion masiva o cache persistente mas amplio

## 3. Trigger de full-universe

La materializacion full-universe solo tiene sentido si ya se cumplen las tres condiciones:

- el piloto semantico esta validado
- existe al menos un consumidor intradia real conectado
- la demanda incremental recurrente demuestra que la capa se usa de forma amplia y estable

## 4. Relacion con `daily_adjusted`

`daily_adjusted` se esta usando para cerrar la verdad economica lenta.

`1m_split_normalized` cierra otra cosa distinta:

- la verdad de escala comparable del intradia entre sesiones

## 5. Veredicto

El momento correcto para pasar `daily_adjusted` a cobertura mucho mas amplia no es "ahora por defecto", sino cuando su consumidor real deje de ser solo piloto y exija expansion estable.

La misma disciplina se aplicara a `1m_split_normalized`.
