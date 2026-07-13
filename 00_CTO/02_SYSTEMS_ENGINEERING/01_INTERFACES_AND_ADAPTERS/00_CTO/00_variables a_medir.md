Has llegado exactamente al mismo muro con el que se encuentra prácticamente todo investigador independiente en microestructura.

Y, de hecho, esto tiene una explicación económica muy clara.

## El problema no es Databento

El problema es el origen de los datos.

Los datos L2 y L3 no los genera Databento.

Los generan:

* Nasdaq TotalView
* NYSE OpenBook
* Cboe Depth
* MEMX Depth
* MIAX
* etc.

Databento únicamente redistribuye esas fuentes.

Y los exchanges cobran muchísimo por redistribuir profundidad de mercado. ([Databento][1])

---

## Fíjate en la tabla que has enviado

En ella se ve claramente:

L1

✔ MBP-1

L2

✔ MBP-10

L3

✔ MBO

Pero observa otra cosa importante.

Para L2/L3 únicamente aparecen feeds como:

* Nasdaq TotalView-ITCH
* NYSE Integrated
* Cboe EDGX Depth
* MEMX Depth

No aparece el bundle barato.

Eso significa:

**si quieres profundidad real... tienes que pagar el feed propietario del exchange.** ([Databento][2])

---

# Entonces...

¿estamos condenados a pagar 1.500-5.000 $/mes?

No necesariamente.

Yo dividiría las soluciones en cinco niveles.

---

# Opción 1 (la que yo estudiaría primero)

## Reducir muchísimo el universo

Aquí es donde creo que tu proyecto TSIS tiene una ventaja enorme.

Tú NO necesitas:

20.000 acciones.

Tú mismo me has explicado varias veces que:

Universe Builder

↓

20 candidatos

↓

solo esos pasan al motor.

Eso cambia completamente el problema.

Imagina:

09:30

Universe Builder encuentra

```
KZIA
ABEO
APDN
...
```

20 símbolos.

Desde ese momento solamente necesitas L2/L3 para esos 20.

No para todo el mercado.

Eso reduce muchísimo:

* ancho de banda
* conexiones
* consumo

y en algunos proveedores también el coste (cuando facturan por uso o por volumen). ([Databento][2])

---

# Opción 2

## Comprar únicamente NASDAQ

Aquí hay una observación importante.

Tus small caps...

¿cotizan dónde?

La mayoría:

Nasdaq.

No NYSE.

No CBOE.

No ARCA.

Es decir...

Quizá el 90% de tu edge esté en

Nasdaq TotalView.

Y no necesites comprar:

* NYSE
* CBOE
* MEMX
* MIAX
* etc.

Muchísimos traders institucionales hacen exactamente eso.

Compran solamente el exchange donde está el activo.

---

# Opción 3

## Broker + feed externo

Esto es muy común.

Ejemplo:

IBKR

↓

ejecuta órdenes

Databento

↓

solo datos

o

IBKR

↓

ejecución

dxFeed

↓

profundidad

o

IBKR

↓

ejecución

Nasdaq directamente

↓

TotalView

Muchos fondos pequeños trabajan así. ([dxFeed Market Data][3])

---

# Opción 4

## Replantear qué necesitas realmente

Aquí creo que merece la pena detenerse.

Has dicho:

> "mi estrategia quiere medir eso"

La pregunta científica sería:

**¿Qué es exactamente "eso"?**

Porque muchas veces la respuesta no es realmente MBO.

Por ejemplo.

Quieres medir:

* spoofing

→ sí necesitas MBO.

Quieres medir:

* absorción

Quizá MBP-10 sea suficiente.

Quieres medir:

* book pressure

MBP-10.

Quieres medir:

* queue imbalance

MBP-10.

Quieres medir:

* liquidity vacuum

MBP-10.

Quieres medir:

* iceberg

MBO ayuda mucho.

Pero no siempre es imprescindible.

Es decir...

Puede que el 80% del edge venga de MBP-10.

Y solamente un 20% requiera MBO.

Eso reduce muchísimo el coste.

---

# Opción 5 (la que probablemente haría un hedge fund)

No procesar L3 en todos los símbolos.

Harían algo parecido a:

```
8000 acciones

↓

scanner

↓

40 acciones

↓

L1

↓

20 acciones

↓

L2

↓

5 acciones

↓

L3
```

Eso es exactamente una arquitectura jerárquica.

Y curiosamente...

encaja perfectamente con TSIS.

---

# Lo que yo haría si estuviera construyendo TSIS

No empezaría comprando MBO para todo.

Construiría la arquitectura así:

```
Polygon / IB

↓

Universe Builder

↓

20 símbolos

↓

MBP-10

↓

Feature Engine

↓

¿merece la pena?

↓

si sí

↓

MBO
```

Así el coste crece únicamente cuando ya has demostrado que existe edge.

---

# Hay otra posibilidad que casi nadie contempla

Y aquí creo que está la oportunidad más interesante para TSIS.

En lugar de intentar comprar **todos los feeds L2/L3**, puedes diseñar una arquitectura híbrida.

Por ejemplo:

* L1 completo para todo el universo.
* MBP-10 únicamente para los 20-30 símbolos que el *Universe Builder* selecciona.
* MBO únicamente para los 3-5 símbolos donde realmente vas a tomar una decisión de entrada.

Desde el punto de vista científico, eso sigue siendo totalmente válido, porque **el dato más caro solo se consume cuando ya existe una hipótesis razonable de que el activo merece ese nivel de observación**.

---

## Mi impresión sobre tu caso

Conociendo bastante bien cómo estás diseñando TSIS, **no creo que debas asumir desde el principio un coste de 1.500–5.000 USD/mes**.

Creo que primero deberíamos responder una pregunta mucho más importante:

> **¿Qué variables microestructurales quieres medir exactamente?**

Por ejemplo:

* Queue imbalance.
* Liquidity imbalance.
* Absorción.
* Icebergs.
* Cancelaciones masivas.
* Order replenishment.
* Pulling/stacking.
* Spoofing.
* Estrés de los proveedores de liquidez.
* Microprice.
* Book pressure.
* Queue position.

Cuando tengamos esa lista, podremos clasificar cada variable según el **mínimo nivel de datos necesario (L1, MBP-10 o MBO)**. Es muy posible que descubramos que solo una pequeña parte de tus hipótesis necesita realmente L3, y que el resto pueda investigarse con un coste mucho menor. Esa decisión puede ahorrarte miles de dólares al año sin comprometer el rigor científico.

[1]: https://databento.com/microstructure/level-2-market-data?utm_source=chatgpt.com "What is level 2 (L2) market data? | Databento Microstructure Guide"
[2]: https://databento.com/equities?utm_source=chatgpt.com "Equities Market Data - Real-time & historical equities API"
[3]: https://dxfeed.com/coverage/us/?utm_source=chatgpt.com "US Securities Provided by dxFeed Market Data Services"
