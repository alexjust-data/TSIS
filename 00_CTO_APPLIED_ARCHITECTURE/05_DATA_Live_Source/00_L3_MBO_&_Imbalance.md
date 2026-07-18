
Tus requisitos son muy concretos:  

* US Small Caps (NASDAQ, NYSE, AMEX)
* MBO / Level 3 real
* Order Lifecycle completo
  * Add
  * Modify
  * Cancel
  * Execute
* Sólo 5–20 acciones al día
* Presupuesto retail (<100-200 €/mes idealmente)
* API utilizable desde Python/C++

Y la conclusión es bastante distinta de lo que normalmente se encuentra en Internet.


# La mala noticia

**Actualmente NO existe prácticamente ningún proveedor retail que venda MBO en streaming por ticker o por día.**

Los proveedores venden normalmente por:

* exchange
* feed
* licencia mensual

No por:

> "hoy quiero MBO únicamente de KAPA, GOVX y HOLO."

Eso prácticamente no existe.

---

# Lo que realmente existe

## 1. Databento

Es el más interesante.

Ofrece exactamente:

* MBP-10
* MBO
* Imbalance

en tiempo real.

El MBO contiene precisamente lo que buscamos:

* add
* cancel
* modify
* executions
* order id

es decir auténtico Order Lifecycle. ([Databento][1])

Pero...

MBO realtime sólo está disponible para Plus o Unlimited con las licencias correspondientes de mercado. ([Databento][2])

Y ahí aparece el problema económico.

---

## ¿Se puede comprar por uso?

Aquí encontré algo interesante.

Databento históricamente factura:

* histórico → por GB

pero

**Realtime MBO no funciona así.**

Realtime necesita:

* suscripción
* permisos
* licencia exchange

No existe oficialmente una modalidad:

> "dame hoy cinco tickers."

No la ofrecen.

---

# ¿Y si abres y cierras la suscripción?

No.

La licencia es mensual.

---

# ¿Y limitar los símbolos?

Sí.

Puedes suscribirte únicamente a:

```
AAPL

TSLA

NVDA
```

en vez de miles.

Eso reduce muchísimo el tráfico.

Pero

**NO reduce el coste de la licencia.**

La licencia es la misma.

---

# 2. dxFeed

dxFeed dispone de Order Book a nivel individual.

Incluso dispone de una modalidad denominada:

Enhanced Order Book

que incorpora:

* order id
* lifecycle
* modificaciones
* ejecuciones

muy parecido al MBO de Databento. ([kb.dxfeed.com][3])

El problema:

No publican precios retail.

Todo pasa por ventas.

Normalmente acaba siendo un producto enterprise.

---

# 3. Rithmic

Rithmic sí distribuye:

Market-by-Order

completo.

Con:

* microsegundos
* profundidad completa
* historical
* realtime ([Rithmic][4])

Pero...

Para futuros.

No para NASDAQ Small Caps.

---

# 4. Nasdaq TotalView

Aquí está realmente el origen del Level 3.

Nasdaq vende:

TotalView

ITCH

MBO

Order IDs

Lifecycle

Pero...

es un feed institucional.

No un producto pensado para retail.

Necesitas además:

* parser ITCH
* infraestructura
* licencias

---

# 5. Cboe EDGX Depth

Databento acaba de incorporar el feed completo EDGX.

Incluye:

* every order
* cancels
* modifies
* aggressor
* odd lots

Es L3 auténtico. ([Databento][2])

Pero sólo de EDGX.

No del mercado completo.

---

# 6. Polygon

No.

Tiene L1.

Trades.

Quotes.

No Order Lifecycle.

---

# 7. Alpaca

No.

---

# 8. Finnhub

No.

---

# 9. TwelveData

No.

---

# 10. IQFeed

L2.

No verdadero MBO.

---

# 11. IBKR

Ya vimos que no.

L2 agregado.

No Order Lifecycle.

---

# Lo interesante

Aquí viene la parte que creo que puede cambiar tu proyecto.

## Tú NO necesitas todo el mercado.

Necesitas esto:

Scanner

↓

20 acciones

↓

Elegir 5

↓

Recibir MBO

Eso significa que el ancho de banda requerido es ridículamente pequeño.

---

# ¿Existe alguna API "pay per symbol"?

He buscado precisamente eso.

No.

No existe.

Ningún proveedor importante cobra:

```
0.30 $

por símbolo
```

o

```
5 $

por día
```

para MBO realtime.

---

# Pero sí existe otra posibilidad

Y creo que merece mucha investigación.

Muchos proveedores tienen:

## Enterprise API

con facturación

```
por mensaje
```

no por símbolo.

Si sólo escuchas:

```
6 símbolos
```

el volumen diario es muy bajo.

Hay que investigar si:

Databento Plus

permite limitar el consumo y pagar realmente por mensajes consumidos, o si el coste fijo del plan hace imposible aprovechar esta característica. La documentación pública no deja esto completamente claro y habría que contrastarlo directamente con ventas. ([Databento][1])

---

# Otra posibilidad mucho más interesante

Y aquí creo que hay una oportunidad.

Muchos traders usan:

Bookmap

*

dxFeed

o

Rithmic

simplemente para visualizar el Order Flow.

Bookmap consume el flujo MBO del proveedor, lo reconstruye y ofrece funciones de replay y análisis. ([bookmap.dxfeed.com][5])

La cuestión importante es:

> ¿Bookmap permite acceder programáticamente al flujo MBO que ya está recibiendo?

Si la respuesta fuese sí mediante su API o algún SDK, podrías utilizar la suscripción de Bookmap como puerta de entrada para investigación, en lugar de contratar directamente un feed institucional.

No he encontrado evidencia pública de que su API exponga el flujo MBO bruto, por lo que habría que investigarlo específicamente.

---

# Otra idea que casi nadie considera

Muchos brokers institucionales reciben:

```
Nasdaq TotalView

↓

internamente

↓

API privada
```

No la anuncian.

Pero algunos brokers para prop firms sí la ofrecen.

Por ejemplo habría que investigar:

* Lightspeed
* Sterling
* CenterPoint
* Cobra
* TradeZero Institutional

No por su plataforma de trading, sino por si permiten acceder al feed completo mediante API privada.

Eso apenas aparece documentado públicamente.

---

# Mi conclusión

Después de revisar el mercado, mi impresión es que **estás buscando un nicho que prácticamente no está cubierto**.

No porque la tecnología no exista, sino porque el mercado está dividido en dos extremos:

* **Retail:** L1 y L2 agregados, baratos.
* **Institucional:** L3/MBO completo, pero con licencias mensuales elevadas.

No existe hoy una oferta claramente orientada al investigador cuantitativo independiente que sólo necesita **5–10 small caps al día** con Order Lifecycle completo.

## Creo que el siguiente paso de investigación sí merece la pena

En lugar de seguir buscando "otro proveedor", haría una investigación técnica y comercial muy específica sobre estas cuatro cuestiones:

1. **Databento:** confirmar con ventas si existe alguna modalidad de facturación por consumo o alguna excepción para un universo muy reducido de símbolos.
2. **Bookmap + dxFeed:** determinar si el flujo MBO recibido por Bookmap puede capturarse mediante su API o SDK para investigación.
3. **Brokers profesionales (Lightspeed, Sterling, CenterPoint, Cobra, etc.):** averiguar si alguno expone el feed TotalView/MBO a través de API privadas para clientes activos.
4. **Licencias NASDAQ directas:** estudiar si es posible contratar únicamente el feed TotalView para un único usuario investigador sin adquirir una infraestructura institucional completa.

Creo que esa investigación tiene bastantes posibilidades de encontrar una solución que hoy no aparece en la documentación pública y sería mucho más valiosa para TSIS que seguir comparando proveedores retail convencionales.

[1]: https://databento.com/docs/schemas-and-data-formats/whats-a-schema?utm_source=chatgpt.com "What's a schema? | Databento schemas & data formats"
[2]: https://databento.com/blog/real-time-cboe-edgx-depth-now-available-on-databento-us-equities?utm_source=chatgpt.com "Real-time Cboe EDGX Depth now on Databento US Equities | Databento Blog"
[3]: https://kb.dxfeed.com/en/data-model/market-events/dxfeed-order-book.html?utm_source=chatgpt.com "dxFeed Order Book"
[4]: https://www.rithmic.com/platforms/exchanges?utm_source=chatgpt.com "Rithmic | Trading Infrastructure for Futures"
[5]: https://bookmap.dxfeed.com/?utm_source=chatgpt.com "dxFeed Bookmap Product Description"
