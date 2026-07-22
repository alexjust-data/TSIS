# Trades File Acceptance Readout v0.1

## 1. Rol

Este documento explica que demuestra la muestra metodologica de `380` files y, sobre todo, que no demuestra.

La muestra `380` no sustituye el cierre full `57f`. Sirve para:

- exploracion profunda;
- calibracion de labels;
- drenaje de falsos `bad_data` hacia buckets mas explicables;
- y refactorizacion de la politica file-level.

## 2. Como se construyo la muestra

La auditoria historica deja claro que:

- `380` no es una muestra al azar puro;
- se reserva cupo por `sample_stratum`;
- se toman `20` files por estrato mediante `reservoir sampling`;
- y la finalidad es no perder casos raros o severos.

Consecuencia:

- la muestra esta sesgada a aprendizaje metodologico;
- sirve para descubrir estructura y corregir taxonomia;
- no sirve para sustituir el conteo final poblacional.

## 3. Hallazgo metodologico clave

La muestra demuestra tres cosas:

1. parte del diagnostico heredado estaba contaminado por metricos poco fiables;
2. una parte fuerte del outside se concentra en odd-lots y microestructura fina;
3. el residuo extremo conservador queda dominado por `reference_scale_mismatch`.

## 4. Que cambia respecto a la lectura ingenua

La lectura ingenua seria:

- `review` masivo implica que Polygon trades esta mal.

La lectura defendible despues de `05` es:

- gran parte del conflicto no parece dano intrinseco del tape;
- parece comparabilidad imperfecta contra `daily` y `1m`;
- y por eso la politica final necesita buckets de comparabilidad y microestructura separados.

## 5. Reparto de la muestra 380

La propia nota metodologica deja este reparto:

- `review = 140`
- `reference_scale_mismatch = 106`
- `review_microstructure = 111`
- `review_no_1m_reference = 21`
- `review_1m_reference_alignment = 2`
- `bad_data = 0` en la muestra estratificada actual

### Lectura analitica

- `106` casos caen ya en `reference_scale_mismatch`: son conflictos de escala contra referencia, no prueba directa de tape roto.
- `111` casos caen en `review_microstructure`: la lectura dominante es odd-lot y comparabilidad fina, no dano bruto universal.
- `21` casos quedan en `review_no_1m_reference`: el conflicto frente a `daily` existe, pero falta arbitro `1m`.
- `2` casos quedan en `review_1m_reference_alignment`: `daily` y `VWAP` alinean, pero el nucleo rompe al mirar `1m`.
- el hecho de que `bad_data` desaparezca de la muestra estratificada no prueba que `bad_data` no exista; prueba que la muestra drenaba sobre todo falsos positivos del bucket duro heredado.

## 6. Que no debe concluir el inspector

El inspector no debe concluir:

- que la muestra `380` limpia todo el bloque;
- ni que el full final ya no contiene `bad_data`.

El cierre `57f` demuestra que `bad_data` sigue existiendo como cola pequena pero real.

## 7. Conclusiones metodologicas

1. La muestra `380` es autoridad explicativa, no autoridad de conteo final.
2. Sirve para justificar por que la politica file-level se volvio mas rica.
3. Sirve para explicar por que `reference_scale_mismatch` y `review_microstructure` no deben tratarse como `bad_data` sin mas.
4. No sustituye el cierre full `57f`, que es la verdad operativa final del bloque.

## 8. Como debe conectarse la muestra con el cierre real

La muestra `380` por si sola no dice cuanta masa util existe en `trades`. Solo dice:

- que familias existen;
- que firmas comparten;
- y por que una parte del conflicto no es simple corrupcion del tape.

Para convertir esa intuicion metodologica en una lectura operativa hay que cruzarla con el cierre real `57f`.

### Que pasa con `review`

En el cierre real:

- `review_total = 4,851,211`
- `review_recoverable_strict = 3,327,955` (`68.6005%`)
- `review_recoverable_extended = 3,505,290` (`72.2560%`)

La muestra `380` ayuda a entender por que esa rehabilitacion existe; no la sustituye.

### Que pasa con `review_microstructure`

La muestra explico que esta familia vive mucho en:

- odd-lots;
- textura del tape;
- y comparabilidad fina.

Sobre `57f`, esa intuicion se materializa operativamente en una recuperacion provisional de:

- `1,516,547` casos strict (`71.1733%`)
- `1,636,379` casos extended (`76.7971%`)

### Que pasa con `review_1m_reference_alignment`

Aunque la muestra lo vio muy poco, el cierre real permite ya cuantificar una recuperacion provisional de:

- `2,591` casos strict (`51.9030%`)
- `3,715` casos extended (`74.4191%`)

### Que responde esta seccion

Responde:

- como debe leerse la muestra `380` frente al cierre final;
- por que los ejemplos metodologicos no bastan como conteo;
- y como se traduce la intuicion causal de la muestra a masa util real.

No responde:

- a la regla final cerrada de todas las familias;
- ni a la promocion de `reference_scale_mismatch`, que sigue siendo prudencialmente no rehabilitada.

### Consecuencia

El inspector no debe quedarse en:

- "la muestra explico bien el problema";
- ni en "el `good` es minimo, luego casi nada sirve".

La lectura correcta es:

- la muestra explica por que el bucket `review` no es uniformemente malo;
- y el cierre real cuantifica que una parte material de esa masa sigue siendo util bajo flag.
