# Event Behavioral Mechanics Guide v0.1

Fecha: 2026-06-20  
Estado: `draft_policy_candidate`  
Scope: `00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/`  

Este documento define como TSIS debe documentar la psicologia de traders, la
teoria de juegos, la dinamica de masas y la microestructura conductual dentro
de las definiciones de eventos.

No define una estrategia.
No define entradas.
No define stops.
No define targets.
No define sizing.

Su funcion es asegurar que los eventos no sean solo dibujos de velas, sino
hipotesis mecanicas, falsables y progresivamente investigables.

## Menu

- [1. Proposito](#1-proposito)
- [2. Regla central](#2-regla-central)
- [3. Separacion obligatoria](#3-separacion-obligatoria)
- [4. Por que importa](#4-por-que-importa)
- [5. Mecanismos conductuales permitidos](#5-mecanismos-conductuales-permitidos)
- [6. Estandar cientifico](#6-estandar-cientifico)
- [7. Template obligatorio](#7-template-obligatorio)
- [8. Evidence ladder](#8-evidence-ladder)
- [9. Claims prohibidos](#9-claims-prohibidos)
- [10. Referencias y research queue](#10-referencias-y-research-queue)
- [11. Regla final](#11-regla-final)

---

## 1. Proposito

TSIS estudia eventos de mercado, no solo configuraciones visuales.

Muchos eventos en small caps nacen de interacciones entre participantes:

- longs tempranos;
- traders de momentum;
- shorts atrapados;
- shorts que intentan defender niveles;
- vendedores que creen que el movimiento fallo;
- market makers y proveedores de liquidez;
- compradores tardios que persiguen el movimiento;
- operadores que reaccionan a noticias, volumen, halts o roturas.

Por eso, cada evento relevante debe poder documentar:

```text
que se observa
que mecanismo podria estar ocurriendo
que participantes podrian estar presionados
que evidencia lo apoya
que evidencia lo refutaria
```

La parte mecanica no convierte un evento en estrategia.

Un evento sigue respondiendo:

```text
Que esta ocurriendo?
```

No responde:

```text
Que debo hacer?
```

## 2. Regla central

Toda definicion de evento puede incluir una hipotesis conductual o
microestructural, pero debe marcarla como hipotesis hasta que exista evidencia.

Formato correcto:

```text
Hipotesis mecanica:
El movimiento podria acelerarse porque los shorts recientes quedan atrapados y
se ven forzados a cubrir cuando el precio rompe el high local anterior.
```

Formato incorrecto:

```text
Los shorts estan atrapados, por tanto hay que comprar.
```

El primer texto describe una hipotesis sobre el mecanismo.
El segundo mezcla mecanismo, certeza y accion operativa.

## 3. Separacion obligatoria

Cada evento debe separar cuatro capas:

| Capa | Pregunta | Ejemplo |
| --- | --- | --- |
| Fenomeno observable | Que ocurrio en el mercado? | Push, dip, rebreak, volumen expansivo. |
| Hipotesis mecanica | Por que podria ocurrir? | Shorts presionados, crowd chasing, liquidez retirada. |
| Evidencia medible | Como se puede aproximar? | Velas, volumen, spread, tape, rebreak, failure rate. |
| Estrategia | Que hago frente a eso? | Entrada, stop, sizing, salida. |

La Event Library solo puede contener las tres primeras.

La cuarta pertenece a:

- `03_STRATEGY_LIBRARY`;
- `08_EXECUTION_MODELS`;
- `09_DECISION_MODELS`.

## 4. Por que importa

Un mismo dibujo de velas puede nacer de mecanismos distintos.

Ejemplo:

```text
vela verde grande
```

Puede significar:

- noticia real y repricing;
- short squeeze;
- iliquidez extrema;
- market maker gap;
- retail chasing;
- cobertura forzada;
- manipulacion o spoof-like appearance;
- error de data.

Si TSIS solo guarda la forma visual, aprende poco.

Si TSIS guarda:

```text
forma observable + hipotesis mecanica + evidencia + alternativas
```

entonces puede despues investigar outcomes, clustering, false positives y
degradacion con mas rigor.

## 5. Mecanismos conductuales permitidos

Las definiciones de eventos pueden documentar mecanismos como:

### 5.1. Presion short y cobertura forzada

Fenomeno:

```text
participantes short quedan en perdida latente y pueden tener que cubrir si el
precio rompe niveles visibles.
```

Proxies posibles:

- squeeze/push previo;
- ruptura de high local;
- aceleracion de volumen en la rotura;
- rechazo rapido de dips;
- continuidad vertical tras failure de vendedores;
- SSR o short-sale constraints cuando aplique;
- tape/agresion compradora si existe dato adecuado.

### 5.2. Trapped trader dynamics

Fenomeno:

```text
un grupo de participantes entra en una direccion, el mercado no confirma su
tesis, y la salida forzada alimenta el movimiento contrario.
```

Ejemplos:

- shorts que venden el primer dip y quedan atrapados en el rebreak;
- longs tardios atrapados en un failed breakout;
- sellers que interpretan mal una pausa como agotamiento.

### 5.3. Herding y crowd attention

Fenomeno:

```text
la atencion colectiva aumenta y genera comportamiento de persecucion del
movimiento.
```

Proxies posibles:

- RVOL;
- volumen por minuto;
- news/catalyst;
- gap;
- continuidad de highs;
- aumento rapido de rango;
- repeticion de roturas intradia.

### 5.4. Reflexividad y feedback loops

Fenomeno:

```text
el movimiento del precio altera las creencias y restricciones de los
participantes, y esas reacciones alimentan el propio movimiento.
```

Ejemplo:

```text
push -> shorts entran -> dip no destruye -> rebreak -> shorts cubren ->
momentum traders persiguen -> nuevo impulso
```

### 5.5. Liquidity vacuum

Fenomeno:

```text
el precio se mueve verticalmente porque la liquidez disponible se retira o no
absorbe suficientemente la demanda agresiva.
```

Proxies posibles:

- velas con rango grande;
- bajo pullback relativo;
- spread widening;
- slippage visible;
- poca negociacion entre niveles;
- volumen concentrado en pocas velas.

### 5.6. Game-theoretic pressure

Fenomeno:

```text
varios grupos actuan anticipando la reaccion de otros grupos.
```

Ejemplo:

- shorts venden el dip esperando fallo;
- longs observan que el dip no rompe estructura;
- momentum traders atacan el rebreak;
- shorts cubren al perder el nivel;
- la cobertura acelera el nuevo impulso.

Este marco debe describirse como presion/incentivos, no como certeza mental de
participantes individuales.

## 6. Estandar cientifico

La psicologia del mercado no puede documentarse como afirmacion absoluta sin
evidencia.

Reglas:

1. Distinguir observacion de inferencia.
2. Distinguir mecanismo propuesto de hecho probado.
3. Declarar proxies usados para aproximar el mecanismo.
4. Declarar alternativas plausibles.
5. Declarar que evidencia refutaria la hipotesis.
6. Marcar si la hipotesis esta basada en observacion humana, literatura,
   evidencia estadistica, outcome research o datos live.
7. No convertir lenguaje psicologico en instruccion operativa.

Ejemplo correcto:

```text
Observed:
El precio hace un push, retrocede, rechaza rapidamente el dip y rompe el high
local con volumen expansivo.

Mechanism hypothesis:
El rebreak puede estar presionando a shorts que entraron durante el dip, lo que
puede contribuir a la aceleracion por cobertura.

Alternative explanations:
repricing por noticia, baja liquidez, chase de momentum, error de data,
continuacion natural sin participacion short relevante.

Evidence needed:
mayor volumen en rebreak, velocidad de recuperacion, fallo de sellers,
spread/tape si esta disponible, outcomes posteriores.
```

## 7. Template obligatorio

Cada evento relevante deberia incluir una seccion parecida a esta:

```yaml
behavioral_mechanics:
  status: hypothesis | literature_supported | data_supported | outcome_supported | falsified

  observed_sequence:
    - 

  participant_map:
    pressured_longs:
    pressured_shorts:
    momentum_buyers:
    liquidity_providers:
    late_chasers:
    sellers:

  game_theory_frame:
    incentive_conflict:
    who_is_forced_to_act:
    what_level_changes_incentives:
    what_failure_would_invalidate_the_pressure:

  crowd_dynamics:
    attention_source:
    herding_proxy:
    feedback_loop:

  microstructure_hypothesis:
    liquidity_state:
    spread_state:
    tape_or_orderflow_proxy:
    volume_proxy:

  measurable_proxies:
    -

  alternative_explanations:
    -

  falsification_tests:
    -

  references:
    status: pending | cited | not_applicable
    items:
      -

  event_strategy_boundary:
    contains_entry_rule: false
    contains_stop_rule: false
    contains_target_rule: false
    contains_sizing_rule: false
```

## 8. Evidence ladder

Toda hipotesis conductual debe indicar su nivel de evidencia.

| Estado | Significado |
| --- | --- |
| `human_hypothesis` | Observacion discrecional o experiencia humana. |
| `visual_case_supported` | Existen ejemplos visuales revisados. |
| `literature_supported` | Existe soporte teorico o empirico externo citado. |
| `data_supported` | Hay medicion interna en datos TSIS. |
| `outcome_supported` | Outcome Research confirma comportamiento posterior consistente. |
| `strategy_supported` | Una estrategia posterior muestra explotabilidad bajo constraints. |
| `falsified` | La hipotesis fue degradada o rechazada. |

Regla:

```text
human_hypothesis no es evidencia institucional.
```

Es un punto de partida valido, no una conclusion.

## 9. Claims prohibidos

Dentro de Event Library esta prohibido escribir como hecho no probado:

```text
los shorts estan obligados a cubrir
esto siempre atrapa shorts
el primer rebreak siempre es mejor
esta estructura tiene edge
hay que entrar en el dip
hay que comprar la vela de rotura
arriesgar menos en la segunda ocurrencia
```

Versiones aceptables:

```text
la hipotesis es que algunos shorts quedan presionados
la estructura puede representar forced covering
el indice ordinal de ocurrencia debe medirse en outcomes
la entrada pertenece a Strategy Library
el sizing pertenece a Decision Models o Strategy Library
```

## 10. Referencias y research queue

Cuando una definicion use psicologia, teoria de juegos o dinamica de masas como
parte importante del mecanismo, debe abrir una cola de referencias.

Temas iniciales a investigar:

1. Short squeezes y forced covering.
2. Feedback trading y positive feedback loops.
3. Herding, information cascades y crowd attention.
4. Market microstructure, order flow y liquidity vacuum.
5. Game theory aplicada a participantes con constraints asimetricos.
6. Reflexividad y cambios de creencias inducidos por precio.
7. Behavioral finance aplicada a panic, fear, FOMO y capitulation.

Regla:

```text
Si una referencia se usa como autoridad, debe citarse de forma trazable.
```

Hasta entonces, el documento debe marcar:

```text
references_status: pending
```

## 11. Regla final

TSIS puede estudiar miedo, euforia, presion short, masa y teoria de juegos.

Pero debe hacerlo con disciplina:

```text
observacion primero
hipotesis despues
proxies declarados
alternativas explicitas
falsabilidad obligatoria
estrategia separada
```

Un evento con buena mecanica sigue siendo solo un evento.

La decision de operar pertenece a capas posteriores.
