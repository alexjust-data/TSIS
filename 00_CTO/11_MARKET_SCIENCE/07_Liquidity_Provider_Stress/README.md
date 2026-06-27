Esta es la pregunta clave para Tsis:

```
¿Podemos detectar que la liquidez está a punto de desaparecer?
```


```
¿Cuánto alpha hay en cada horizonte temporal?  DeepLOB - Zihao Zhang
¿Qué ocurrirá al precio en los próximos segundos? Alpha Term Structures - Petter Kolm 
```

Has hecho dos preguntas muy buenas y además están relacionadas.

---

# PARTE 1

# Órdenes ocultas (Hidden Orders / Icebergs)

Sí.

Existen.

Y son IMPORTANTÍSIMAS.

Pero hay muchos mitos.

---

# Lo que ves en DAS

Supongamos:

```text
Ask

100 shares
```

Tú piensas:

```text
Sólo quedan 100 shares.
```

---

Compras:

```text
100
```

---

Y aparece:

```text
100 más
```

---

Compras otra vez:

```text
100
```

---

Y aparecen:

```text
100 más
```

---

Y otra vez.

Y otra vez.

---

¿Qué ocurre?

Probablemente:

```text
Iceberg Order
```

---

# Iceberg

Ejemplo real:

```text
Orden real

50.000 shares
```

---

Visible:

```text
100 shares
```

---

Cada vez que ejecutas:

```text
100
```

el sistema muestra:

```text
100 nuevos
```

---

# ¿Por qué?

Porque el trader NO quiere revelar:

```text
su tamaño real
```

---

# ¿Quién usa esto?

Muchísima gente.

---

## Fondos

## Institucionales

## HFT

## Market Makers

## Liquidity Providers

---

# ¿Afecta a tu pregunta?

MUCHO.

Porque destruye una ilusión.

---

Mucha gente cree:

```text
Level 2
=
Liquidez real
```

---

Falso.

---

Lo que ves es:

```text
Liquidez visible
```

---

Pero existe:

```text
Liquidez oculta
```

---

Por eso el libro de Bouchaud es tan importante.

La liquidez visible suele ser una fracción de la liquidez total.

---

# Entonces

¿Cómo detectamos estrés?

NO mirando:

```text
Hay 100 shares.
```

---

Porque pueden existir:

```text
50.000 ocultas.
```

---

Debes observar:

```text
qué ocurre cuando golpean esas órdenes
```

---

Ejemplo.

---

## Caso A

```text
Compran

100
100
100
100
```

---

Y el precio:

```text
No sube
```

---

Probablemente:

```text
Iceberg vendedor
```

---

O liquidez escondida.

---

## Caso B

```text
Compran

100
100
100
100
```

---

Y el ask corre:

```text
5.00

5.05

5.10

5.15
```

---

Eso sí es:

```text
Retirada de liquidez
```

---

Y ahí aparece tu:

```text
Liquidity Provider Stress
```

---

# Lo importante

TSIS debería aprender:

NO:

```text
Qué profundidad veo
```

Sino:

```text
Qué profundidad desaparece
```

---

Porque el estrés aparece cuando:

```text
La liquidez deja de reponerse.
```

---

# PARTE 2

# DeepLOB vs Alpha Term Structures

Aquí hay una diferencia gigantesca.

---

# DeepLOB

Zihao Zhang

Oxford.

---

Pregunta:

```text
¿Qué ocurrirá al precio
en los próximos segundos?
```

---

Input:

```text
LOB
```

---

Arquitectura:

```text
LOB
↓
CNN
↓
Inception
↓
LSTM
↓
Up / Down / Neutral
```

---

Objetivo:

```text
Predicción
```

---

# Deep Learning of Alpha Term Structures

Petter Kolm

Morgan Stanley.

---

Pregunta distinta.

---

NO pregunta:

```text
¿Subirá?
```

---

Pregunta:

```text
¿Cuánto alpha
hay en cada horizonte temporal?
```

---

Ejemplo.

---

Predicción:

```text
30 segundos
↑

1 minuto
↑

5 minutos
↓

15 minutos
↓
```

---

Eso es una:

```text
Term Structure
```

---

Igual que existe:

```text
Yield Curve
```

---

Él crea:

```text
Alpha Curve
```

---

Arquitectura:

```text
LOB
↓
Deep Learning
↓
Alpha(1s)

Alpha(10s)

Alpha(30s)

Alpha(1m)

Alpha(5m)
```

---

# ¿Cuál me interesa más para TSIS?

Sinceramente:

```text
Alpha Term Structures
```

---

Porque DeepLOB es:

```text
Dirección
```

---

Mientras que Kolm está más cerca de:

```text
Market State Representation
```

---

# Lo que creo que acabará ocurriendo

Y aquí viene algo importante.

---

Ni DeepLOB.

Ni Kolm.

---

Funcionarán directamente sobre microcaps.

---

Porque ambos fueron diseñados para:

```text
ES

Large Caps

LOB estable
```

---

Tus microcaps tienen:

```text
News

Halts

SSR

Low Float

Attention Shock

Liquidity Collapse
```

---

Entonces sospecho que la representación correcta para TSIS será algo parecido a:

```text
LOB Features

+

Liquidity Stress

+

Attention

+

Catalyst

+

Inventory Stress

+

Market State
```

---

Y aquí aparece una idea que creo que puede cambiar completamente tu investigación.

Quizá el objetivo NO sea:

```text
Predecir precio
```

---

Quizá sea:

```text
Predecir

Liquidity Stress
```

---

Porque:

```text
Liquidity Stress
```

↓

```text
Spread Expansion
```

↓

```text
Price Impact
```

↓

```text
Squeeze
```

---

Y eso conecta directamente:

```text
Hidden Orders
Icebergs
Market Makers
Order Flow
Microstructure
DeepLOB
Kolm
López de Prado
```

en una única pregunta científica:

```text
¿Podemos detectar que la liquidez está a punto de desaparecer?
```

Porque si TSIS llega a responder eso, estarías muchísimo más cerca de entender los grandes squeezes de microcaps que simplemente intentando predecir la siguiente vela.

# Que debe funcionar

Ésta es EXACTAMENTE la pregunta correcta.

Y la respuesta corta es:

> **Sí, científicamente se puede responder.**
>
> Pero la mayoría de gente interpreta mal lo que significa "funciona".

---

**DeepLOB**

La pregunta es:

```text id="h0h8hv"
¿Qué ocurrirá al precio
en los próximos segundos?
```

---

Matemáticamente:

```text id="ym0qea"
P(up | estado actual del LOB)
```

---

Eso es una tarea de:

```text id="g4r89w"
clasificación probabilística
```

---

Y sí.

Los papers muestran que:

```text id="hyg4ri"
hay señal
```

---

Pero la señal es pequeña.

---

Ejemplo.

No obtienes:

```text id="lkjlwm"
95%
```

---

Obtienes algo tipo:

```text id="4jlwmv"
53%
55%
57%
```

---

Y eso en HFT ya es enorme.

---

**Entonces**

¿Funciona?

Sí.

---

¿Te hace rico?

No necesariamente.

---

Porque todavía falta:

```text id="jlwm61"
execution
slippage
fees
latency
capacity
```

---

**Petter Kolm**

La pregunta es distinta.

---

No pregunta:

```text id="jlwm62"
¿Subirá?
```

---

Pregunta:

```text id="jlwm63"
¿Cuál es la estructura temporal
del alpha?
```

---

Ejemplo.

---

Estado actual:

```text id="jlwm64"
LOB
```

---

Modelo:

```text id="jlwm65"
Alpha 1 segundo = +0.8bp

Alpha 10 segundos = +0.6bp

Alpha 1 minuto = +0.2bp

Alpha 5 minutos = -0.1bp
```

---

Eso te dice:

```text id="jlwm66"
La ventaja desaparece rápido
```

---

**Científicamente**

Ésta me parece más interesante.

Porque:

```text id="jlwm67"
explica
```

---

Mientras que DeepLOB sólo:

```text id="jlwm68"
predice
```

---

**Ahora viene la pregunta importante para TSIS**

Y aquí creo que está el error que veo en mucha gente.

---

Supongamos que DeepLOB tiene razón.

---

Predice:

```text id="jlwm69"
57% up
```

---

Perfecto.

---

La pregunta es:

```text id="jlwm70"
¿Por qué?
```

---

Y DeepLOB no lo sabe.

---

Es una caja negra.

---

**López de Prado diría**

```text id="jlwm71"
Has encontrado
una correlación útil.
```

---

No necesariamente:

```text id="jlwm72"
un mecanismo.
```

---

**Ahora piensa en microcaps**

Éste es el punto clave.

---

En ES:

```text id="jlwm73"
LOB
```

es gran parte del estado.

---

En una microcap:

```text id="jlwm74"
LOB
```

es sólo una parte.

---

Porque tienes:

```text id="jlwm75"
News

Float

SSR

Attention

Halt Risk

Market Cap

Catalyst
```

---

Que DeepLOB nunca ve.

---

**Entonces**

¿Funcionaría DeepLOB?

Sí.

---

Pero probablemente:

```text id="jlwm76"
peor de lo esperado
```

---

Porque le falta contexto.

---

**Mi opinión**

Si mañana me dieras:

```text id="jlwm77"
20 años de microcaps
+
Level 2
+
Tape
```

NO construiría primero:

```text id="jlwm78"
DeepLOB
```

---

Construiría:

```text id="jlwm79"
Market State Representation
```

---

Y después probaría:

```text id="jlwm80"
DeepLOB
```

sobre ese estado.

---

**Lo realmente importante**

La pregunta:

```text id="jlwm81"
¿Qué ocurrirá al precio
en los próximos segundos?
```

es científicamente válida.

---

La pregunta:

```text id="jlwm82"
¿Cuánto alpha hay
en cada horizonte temporal?
```

también.

---

Pero para TSIS creo que existe una tercera pregunta más poderosa:

```text id="jlwm83"
¿Qué mecanismo
está generando ese alpha?
```

---

Porque:

```text id="jlwm84"
DeepLOB
```

↓

predice.

---

```text id="jlwm85"
Kolm
```

↓

describe la duración del alpha.

---

Pero:

```text id="jlwm86"
Microestructura
+
Causalidad
```

↓

explican por qué existe.

---

Y si tu objetivo es construir algo tipo:

```text id="jlwm87"
TSIS
+
Research Agents
+
AlphaEvolve
```

esa tercera pregunta probablemente sea la más valiosa de las tres.

De hecho, si tuviera que resumir la frontera actual:

```text id="jlwm88"
2018
=
DeepLOB
(predicción)

2021
=
Alpha Term Structures
(descripción del alpha)

2025+
=
Causal Market State Representation
(explicación del mecanismo)
```

Y sospecho que la última es la que más ventaja competitiva puede darte en microcaps, porque es donde casi no existe literatura específica y donde TSIS podría aportar algo realmente nuevo.
