# Research Design - EXP_DAS_FRONTSIDE_DISCOVERY_0002

Fecha: 2026-07-06
Estado: draft_operativo

## Pregunta Principal

```text
?Por que algunos tickers recuperan el primer dip y otros se destruyen?
```

Esta es la pregunta central del experimento.

No buscamos todavia saber si una estrategia gana dinero. Buscamos entender la estructura del fenomeno frontside en small caps:

```text
un ticker despierta
el scanner lo caza
hace primer push
hace primer dip
recupera o muere
rompe o falla
continua o se destruye
```

## Preguntas Secundarias

```text
?A partir de que zona de movimiento inicial cambia el comportamiento posterior?
```

```text
?El +50% era una buena zona de captura, era demasiado tarde, demasiado pronto o solo era util para generar imagenes?
```

```text
?Que coste de oportunidad genera esperar a un umbral alto de movimiento?
```

```text
?Que oportunidades desaparecen por filtros de volumen, precio, market cap u hora?
```

```text
?Hay informacion explotable antes de esperar a first dip/rebreak?
```

```text
?Es necesario esperar a first dip y rebreak para declarar estrategia in-play, o existen puntos anteriores con edge medible?
```

## Hipotesis De Trabajo

Las siguientes frases son hipotesis, no reglas finales:

```text
H1: el +50% no es un numero magico; puede ser una zona de comportamiento o solo un sampling probe humano.
```

```text
H2: muchos tickers que parecen interesantes en scanner mueren antes de recuperar el primer dip.
```

```text
H3: esperar al rebreak reduce ruido, pero puede perder una parte grande del movimiento capturable.
```

```text
H4: entrar antes del rebreak puede capturar mas movimiento, pero aumenta fake moves, MAE y riesgo de destruccion.
```

```text
H5: volumen acumulado es un filtro fuerte, pero puede tener alto coste de oportunidad.
```

```text
H6: la recuperacion del primer dip depende de una combinacion de estructura de precio, volumen, tiempo, contexto diario, liquidez y estado intradia.
```

## Denominador Correcto

El denominador no son solo los casos que hicieron rebreak.

El denominador debe ser:

```text
todos los tickers cazados por el scanner bajo una configuracion declarada
```

Despues se clasifican:

```text
1. no despierta suficiente despues del scanner gate
2. hace primer push pero muere rapido
3. hace primer push pero no deja dip limpio
4. hace first push + first dip y no recupera
5. recupera parcialmente
6. rompe first_push_high
7. rompe y continua
8. rompe y falla
9. presenta spike/mecha raw sospechosa o data no confiable
```

Esto evita sesgo de supervivencia.

Si miramos solo tickers con `rebreak_confirmed`, ya estamos mirando los supervivientes.

## El +50% En Este Experimento

El `+50%` no se trata como verdad cientifica.

Lectura correcta:

```text
+50% = sampling probe humano / filtro discrecional historico
```

Su funcion original era cazar movimientos frontside suficientemente grandes para estudio visual y para que el long tuviera posibilidad economica.

En `0002`, el +50% se evalua dentro de una matriz:

```text
threshold_pct = 20, 30, 40, 50, 70, 100
```

La pregunta no es:

```text
?gana dinero el 50%?
```

La pregunta es:

```text
?como cambia la poblacion capturada y su comportamiento posterior al cambiar el umbral?
```

## Familias Que Deben Estudiarse

### Scanner Capture

```text
threshold_pct
market_cap_gate
price_gate
accumulated_volume_gate
session_scope
premarket phase
```

### Price Structure

```text
first_push_start
first_push_high
first_dip_low
dip_depth
recovery_to_first_push_high
rebreak_level
close_above_level
wick_break_vs_body_break
hold_above_level_n_bars
```

### Volume Confirmation

```text
volume vs previous 3/5/10 bars
volume vs dip volume
volume vs first push volume
cumulative volume
volume acceleration
volume available after in-play
```

### Time Structure

```text
minutes from scanner gate
minutes from push start
minutes from first dip
premarket phase
near open vs early premarket
```

### Trend Context

```text
VWAP relation
EMA/Wilder regime
slope
compression/expansion
```

### State Context

```text
market cap
price
float cuando exista
daily gap
prior volume
liquidity
spread/microstructure cuando exista
```

### Execution Context

```text
tradable range
spread
slippage proxy
volume available after in-play
intraminute uncertainty
```

## Opportunity Decomposition

El experimento debe medir cuatro conceptos separados:

```text
scanner_to_inplay_opportunity
= movimiento capturable desde scanner gate hasta in-play gate
```

```text
post_inplay_opportunity
= movimiento capturable despues del in-play gate
```

```text
missed_move
= cuanto movimiento ya ocurrio antes de que la estrategia fuera valida
```

```text
tradable_after_inplay
= cuanto queda realmente despues de confirmar estructura
```

Pero en `0002` todavia no congelamos `inplay_gate` como verdad final.

Primero medimos desde varios anchors:

```text
scanner gate
first push start
first push high
first dip low
recovery point
rebreak point
```

## Que NO Responde Este Experimento

Este experimento no responde todavia:

```text
si la estrategia DAS es rentable
cual es la entrada exacta
cual es el stop exacto
cual es el take profit exacto
cual es el mejor threshold definitivo
si AlphaEvolve debe operar directamente
```

Tampoco valida una regla operativa.

Solo produce evidencia para decidir que estudiar despues.

## Resultado Esperado

El resultado esperado no es un numero unico.

Debe ser una lectura por zonas:

```text
20%-30%: muchos casos, mucho ruido, posible destruccion rapida
40%-60%: posible zona de equilibrio entre captura y supervivencia
70%-100%: menos casos, mas movimiento perdido, posible agotamiento
```

Esto se confirmara o se rechazara con datos.

El output principal debe permitir responder:

```text
que threshold captura demasiada basura
que threshold pierde demasiadas oportunidades
que condiciones predicen recuperacion del primer dip
que condiciones predicen destruccion
que parte del movimiento ocurre antes y despues del rebreak
```
