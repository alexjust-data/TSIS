# Handoff Actual TSIS Lab - 2026-07-08

Estado: handoff operativo para continuar el trabajo sin reabrir decisiones ya tomadas.
Idioma de trabajo: espanol para corpus explicativo. Nombres tecnicos, rutas, campos y ids se mantienen en ingles cuando ya existen asi en el proyecto.

## 1. Situacion General

Estamos trabajando en `C:/TSIS_Data/00_TSIS_Lab`, dentro del marco nuevo de TSIS como Scientific Discovery Engine.

La idea central ya acordada es:

```text
TSIS no parte de eventos oficiales.
TSIS parte de experimentos reproducibles para descubrir fenomenos repetibles.
```

AlphaEvolve no es el centro del proyecto. AlphaEvolve sera un posible generador automatico de experimentos candidatos, igual que un humano puede proponer experimentos. Ambos deben pasar por el mismo Scientific Validation Pipeline.

La investigacion actual esta centrada en la estrategia DAS long/frontside small caps.

## 2. Experimentos Relevantes

### EXP_DAS_FRONTSIDE_DISCOVERY_0001

Ruta:

```text
C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001
```

Uso:

- Sirvio para validar visualmente la logica humana de `first push`, `first push high`, `first dip low` y `rebreak`.
- Aqui se discutio y ajusto la logica visual con imagenes anotadas.
- La logica conceptual correcta debe tomarse de este experimento cuando haya dudas sobre `first dip low`.

Definiciones humanas consolidadas:

```text
first push = primer tramo de expansion tras despertar el ticker.
first push high = maximo del primer tramo; puede ser la mecha de la primera vela roja, no necesariamente una vela verde.
first dip = primer pullback local despues del first push.
first dip low = minimo real de ese pullback local; puede estar en una vela verde posterior a la primera roja.
rebreak = ruptura posterior del first push high.
```

### EXP_DAS_FRONTSIDE_DISCOVERY_0002

Ruta:

```text
C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0002
```

Uso:

- Experimento actual.
- Objetivo: construir denominador cientifico desde 1m quote-guarded para estudiar movimientos frontside en 2026 y despues ampliar.
- Ya se genero denominador 2026 con data saneada quote-guarded.

Run relevante:

```text
C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0002/evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z
```

Resultado observado:

```text
152 candidatos emitidos para 2026
```

Estos candidatos no son todavia estrategia ni evento validado. Son tickers que el scanner-denominador habria capturado bajo las reglas actuales. Dentro de ellos puede haber casos DAS buenos, casos malos, falsos frontside y otros fenomenos.

## 3. Fuente Correcta De 1m

No usar `E:/TSIS/data/ohlcv_1m` directamente para este experimento visual/estadistico.

La fuente correcta para continuar ahora es el universo 1m quote-guarded materializado:

```text
C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_1
```

Este output viene de:

```text
E:/TSIS/data/ohlcv_1m
+
repair_manifest_lt1b_v0_1
+
quote-guarded repair shards
```

Motivo:

- El raw 1m tenia mechas imposibles.
- Ya se reparo el problema con el flujo quote-guarded.
- Los experimentos visuales y estadisticos deben consumir esta vista materializada, no el raw directo.

Regla escrita tambien en:

```text
C:/TSIS_Data/00_TSIS_Lab/LOCAL_RULES.md
```

## 4. Estado Del Universo Quote-Guarded

Output root:

```text
C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_1
```

2026 completo:

```text
year=2026
completed=5982
failed=0
rows=52686038
repairs=322699
```

2025 tambien fue materializado, con un caso previo pendiente/observado de LFST por shard corrupto. Si el siguiente agente necesita afirmar estado final de 2025, debe verificar summaries actuales antes de escribirlo como cerrado.

2005-2014 fueron vistos completos:

```text
2005 complete
2006 complete
2007 complete
2008 complete
2009 complete
2010 complete
2011 complete
2012 complete
2013 complete
2014 complete
```

2015-2020 tienen `complete_with_failures` / `failed_tickers > 0` en la metadata local revisada. No asumir cierre limpio full 2005-2026 sin resolver esos failures y validar el run final.

## 5. Decisiones Del Scanner Denominador

Cambio conceptual importante:

El scanner denominador NO debe filtrar por +50%.

Antes el +50% era un sampling probe humano para cazar imagenes interesantes. Ahora no debe funcionar como filtro del denominador si estamos investigando cientificamente donde nace el edge.

Regla actual:

```text
scanner denominator = market cap + price + volume + session scope
```

No:

```text
scanner denominator = market cap + price + volume + +50%
```

Filtros denominador actuales:

```text
market_cap < 100M
0.50 <= price <= 20
volumen acumulado minimo configurable
session scope configurable, por defecto 03:30-10:00 NY para visual audit
```

El +50% puede seguir existiendo como parametro de investigacion en sweeps, pero no como verdad fija ni como filtro obligatorio del denominador.

## 6. Problema Actual Que Hay Que Corregir

El codigo actual de `EXP_DAS_FRONTSIDE_DISCOVERY_0002` todavia conserva parte de logica vieja:

- filtro/argumento visual de `threshold_pct=50`
- punto negro de scanner gate en imagen
- calculo incorrecto de `first_dip_low` en algunos casos
- rebreak marcado en lugares incorrectos
- rebreak permitido con reglas no alineadas con la definicion humana actual

El usuario pidio explicitamente:

```text
quita el filtro del 50% y el punto de la imagen del 50%
revisa/rectifica first_dip_low usando la logica que quedo bien en 0001
rebreak valido = vela que rompe first_push_high y cierra por encima, y la vela posterior tambien cierra por encima
```

## 7. Scripts Que Hay Que Revisar / Tocar

### Builder de anchors DAS frontside

```text
C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0002/scripts/build_das_frontside_anchor_candidates_from_worklist_v0_1.py
```

Puntos detectados que hay que corregir:

- Hay llamadas desalineadas con firmas actuales.
- `find_first_push_and_dip(...)` debe recibir `bars, push_start_idx, cfg`, no parametros viejos.
- `classify_rebreak(...)` debe recibir `bars, detection, cfg`, no parametros viejos.
- No debe anadir `scanner_gate` como anchor visual.
- El estado de detection debe alinearse con la funcion real.
- Keys antiguas como `vol`, `prior_vol_avg`, `first_attempt` deben revisarse contra las keys reales actuales: probablemente `volume`, `prior_volume_avg`, `first_failed_attempt`.

### Scanner 2026 full universe

```text
C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0002/scripts/build_2026_scanner_from_qg_full_universe_1m_v0_2.py
```

Puntos a revisar:

- No debe usar `threshold_pct` como filtro.
- `--threshold-pct` puede eliminarse o quedar como no-op documentado, pero no debe condicionar seleccion.
- Default de sesion visual/experimental debe pasar a `03:30` NY cuando aplique.

### Wrapper monitorizado del scanner

```text
C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0002/scripts/run_scanner_2026_qg_full_universe_monitored_v0_2.py
```

Puntos a revisar:

- No debe pasar `--threshold-pct 50` al child.
- Default de session start debe ser `03:30` si el proceso pretende cubrir premarket completo para visual audit.

### Renderer PNG

```text
C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0002/scripts/render_das_frontside_anchor_candidates_v0_2.py
```

Puntos a corregir:

- No renderizar `scanner_gate` como punto negro.
- El chart debe imprimir desde `03:30` NY hasta `10:00` NY cuando exista data.
- VWAP debe calcularse por el renderer desde barras usadas, no confiar en VWAP heredado si no es fiable.
- Wilder debe ser mas gruesa que EMA8.
- Cuando Wilder esta por encima de EMA8, ambas lineas deben pintarse rojas.
- Cuando Wilder esta por debajo de EMA8, ambas lineas deben pintarse verdes.
- Las cajas deben ir fuera del area de precio, debajo de la leyenda y sin tapar velas.

## 8. Regla Correcta Para first_dip_low

No usar minimos tardios de toda la sesion.

Regla humana actual:

```text
1. Detectar inicio del push.
2. Seguir el primer tramo de expansion.
3. El first_push_high se congela en el maximo del primer tramo, incluyendo la posible mecha de la primera vela roja.
4. Tras el first_push_high, detectar el primer pullback local.
5. El first_dip_low es el minimo local de ese pullback, que puede estar en:
   - la primera vela roja,
   - una secuencia de velas rojas,
   - o la primera vela verde posterior si su mecha deja el minimo real.
6. No permitir que el first_dip_low derive hacia un minimo muy posterior de la sesion.
```

Si hay duda, comparar contra 0001 y no inventar otra definicion.

## 9. Regla Correcta Para rebreak Valido

Nueva regla solicitada por el usuario:

```text
rebreak valido =
  una vela posterior al first_dip_low rompe first_push_high
  AND esa misma vela cierra por encima de first_push_high
  AND la vela siguiente tambien cierra por encima de first_push_high
```

No basta:

```text
high > first_push_high
```

No basta:

```text
mecha por encima del nivel
```

Volumen, color de vela, cuerpo, VWAP y otras confirmaciones quedan como variables/diagnosticos para investigar, no como hard filter actual salvo que un contrato posterior lo declare.

## 10. Falsos Rebreaks

Si una vela rompe por high pero no cumple confirmacion, debe poder registrarse como fake/rejected attempt:

```text
fake_rebreak_reason:
  close_not_above_level
  next_close_not_above_level
  no_next_bar
```

Si ademas se calcula volumen, debe quedar como diagnostico:

```text
break_volume
prior_volume_avg
volume_ratio
```

Pero no usar volumen como filtro duro hasta que se cree un contrato/sweep especifico.

## 11. Preguntas Cientificas Activas

Pregunta principal:

```text
Por que algunos tickers recuperan el first dip y otros se destruyen?
```

Preguntas asociadas:

```text
cuanto movimiento existe antes del in-play gate?
cuanto movimiento queda despues del in-play gate?
es necesario esperar al first dip + rebreak?
existe edge capturable antes del first_push_high?
que variables explican recuperacion/fallo?
```

Metricas futuras que se quieren medir:

```text
scanner_to_inplay_opportunity
post_inplay_opportunity
missed_move
tradable_after_inplay
MFE desde scanner gate
MAE desde scanner gate
MFE desde in-play gate
MAE desde in-play gate
return 1m/2m/5m/10m/30m despues de in-play
failure rate
fake breakout rate
continuation rate
time-to-failure
time-to-extension
```

Pero antes de medir todo eso hay que tener anchors correctos.

## 12. No Hacer

No lanzar runs largos por cuenta propia.

Si hace falta ejecutar 2026 completo, dar primero:

```text
comando de ejecucion
comando de monitor
```

El usuario quiere ver la evolucion.

No volver a usar raw 1m directo para visual/audit.

No copiar la logica del notebook DAS si contradice lo acordado. Se puede estudiar como referencia visual, pero la logica actual debe estar contratada y reproducible en scripts del Lab.

No presentar el +50% como verdad cientifica. Era un sampling probe humano.

## 13. Siguiente Paso Recomendado

1. Parchear los scripts listados en la seccion 7.
2. Ejecutar tests sinteticos pequenos de:
   - first_push_high con mecha de primera vela roja,
   - first_dip_low en vela verde posterior,
   - fake rebreak por close insuficiente,
   - rebreak valido con close actual y close siguiente por encima.
3. Regenerar solo 5-10 PNGs, no todo el universo.
4. Revisar visualmente con el usuario.
5. Cuando el usuario valide, regenerar los 152 PNGs del run 2026.
6. Solo despues empezar tablas de estadisticas.

## 14. Estado De Conversacion

El usuario esta frustrado por compactaciones frecuentes y por errores visuales previos. Ser directo, no teorizar de mas y no prometer sin verificar.

Prioridad absoluta ahora:

```text
anchors correctos antes de estadisticas.
```
