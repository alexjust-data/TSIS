Esta respuesta sí la voy a enfocar como si estuviera escribiendo una **due diligence técnica** para decidir la arquitectura de TSIS.

No me interesa cuál es "mejor broker". Me interesa responder:

> **¿Cuál de los dos me acerca más a un MBP-10 científico para entrenar modelos de ML?**

Y aquí aparecen diferencias mucho más profundas de las que parecen.

---

# Antes de comparar: ¿qué es exactamente nuestro objetivo?

El objetivo **NO** es tener un DOM bonito.

El objetivo es reconstruir un estado del libro suficientemente consistente para que un modelo pueda aprender relaciones como:

```text
Depth imbalance

Book slope

Liquidity withdrawal

Replenishment

Microprice

Queue pressure

Depth velocity

Liquidity collapse

Hidden liquidity (parcialmente)

etc.
```

Por tanto el feed ideal debería contener:

| Campo                | Necesario |
| -------------------- | --------- |
| timestamp            | sí        |
| exchange timestamp   | ideal     |
| update incremental   | sí        |
| snapshot inicial     | sí        |
| top10                | sí        |
| total shares         | sí        |
| número órdenes       | sí        |
| venue                | sí        |
| secuencia            | ideal     |
| reset messages       | ideal     |
| replay igual al live | ideal     |

Ahora comparemos.

---

# 1. Filosofía de la API

## TradeStation

TradeStation no expone simplemente un callback tipo:

```text
update row
```

Expone DOS APIs completamente distintas:

### A)

MarketDepthQuotes

No agrega.

Devuelve información por participante.

Ejemplo:

```json
Bid

Price

Size

OrderCount

Name
```

donde

```text
Name
```

es:

```text
NSDQ

ARCA

BATS

etc
```

Es decir:

**la unidad de información es el participante**. ([TradeStation API][1])

---

### B)

MarketDepthAggregates

Aquí cambia completamente la filosofía.

Ya no devuelve participantes.

Devuelve:

```text
Price

TotalSize

BiggestSize

SmallestSize

NumParticipants

TotalOrderCount

EarliestTime

LatestTime
```

Es decir:

la API YA HA RECONSTRUIDO un MBP por precio. ([TradeStation API][1])

---

Esto es importantísimo.

Porque significa que TradeStation internamente ya hace:

```text
ARCA

+

NASDAQ

+

BATS

+

...

↓

Agrupación por precio

↓

Resultado agregado
```

Eso está muchísimo más cerca de Databento MBP-10.

---

## Interactive Brokers

IB hace justo lo contrario.

Su callback es:

```cpp
updateMktDepth()

updateMktDepthL2()
```

que devuelve:

```text
position

marketMaker

operation

side

price

size
```

Nada más. ([Interactive Brokers][2])

No existe:

```text
TotalOrderCount

NumParticipants

BiggestOrder

SmallestOrder

AggregateVolume
```

No existe.

---

# Primera conclusión

TradeStation entrega mucha más información estructural del libro.

IB entrega únicamente modificaciones de filas.

Aquí gana claramente TradeStation.

---

# 2. Número de órdenes

Esto me parece una diferencia enorme.

TradeStation:

```text
TotalOrderCount
```

por nivel.

Además:

```text
NumParticipants
```

([TradeStation API][1])

---

IB:

no devuelve número de órdenes.

Sólo:

```text
size
```

---

¿Por qué importa?

Imagina

```text
Bid

3.25

9000 shares
```

Eso puede ser

Caso A

```text
1 orden
```

Caso B

```text
25 órdenes
```

Son mercados completamente distintos.

Para ML:

el modelo debería distinguirlos.

TradeStation sí.

IB no.

---

# 3. Participantes

TradeStation Quote API

devuelve

```text
NSDQ

ARCA

EDGX

...
```

por separado.

Después puedes pedir:

Aggregate.

Eso significa que puedes elegir.

([TradeStation API][1])

---

IB

SmartDepth

puede agregar varios exchanges.

Pero tú no sabes realmente cómo se hizo esa agregación.

Y además IB dice explícitamente:

> no garantizamos mostrar todos los precios cotizados. ([Interactive Brokers][2])

Esa frase para investigación científica pesa muchísimo.

---

# 4. Integridad del libro

Aquí aparece una diferencia menos obvia.

TradeStation

envía snapshots completos.

Cada mensaje contiene

```text
Bids[]

Asks[]
```

con arrays completos.

No sólo un cambio.

([TradeStation API][1])

---

IB

envía únicamente

```text
insert

update

delete
```

sobre una posición.

Tú debes mantener el libro.

---

¿Qué prefiero?

Sorprendentemente...

Para ML

prefiero snapshots completos.

Porque:

si pierdes un paquete

el siguiente snapshot vuelve a sincronizar.

Con IB:

si pierdes un update

tu libro queda corrupto.

---

# 5. Reconstrucción

TradeStation

prácticamente ya entrega:

```text
MBP

↓

Top10

↓

listo
```

IB

te obliga a reconstruir.

---

# 6. Calidad temporal

Aquí IB tiene una ventaja.

IB envía eventos incrementales.

TradeStation parece enviar snapshots agregados.

Eso significa:

TradeStation probablemente tenga más latencia.

No enorme.

Pero probablemente mayor.

La documentación no especifica frecuencia de publicación.

Eso habría que medir.

---

# 7. Información estadística

TradeStation entrega además:

```text
BiggestSize

SmallestSize
```

Eso me sorprendió muchísimo.

Porque ya puedes construir features como

```text
LargestOrderRatio

Concentration

OrderFragmentation
```

Sin MBO.

IB imposible.

---

# 8. ¿Qué pierde TradeStation?

Aquí viene el gran problema.

NO sabemos:

si esos snapshots contienen TODOS los cambios.

Puede ser

```text
snapshot cada 100 ms
```

o

```text
snapshot cuando cambia algo
```

La documentación no lo dice.

Y esto es importantísimo.

---

# 9. SmartDepth de IB

IB añade:

```text
SMART depth
```

agregado.

Pero:

IB nunca explica exactamente

cómo construye ese agregado.

Ni qué exchanges.

Ni prioridades.

Ni tiempos.

---

# 10. Timestamps

TradeStation

cada nivel tiene

```text
EarliestTime

LatestTime
```

Eso me llamó muchísimo la atención.

Porque significa que la agregación conserva información temporal.

([TradeStation API][1])

---

IB

simplemente

```text
price

size

position
```

No timestamp por fila.

---

# 11. Calidad para ML

Aquí es donde cambia todo.

## Si quisiera entrenar

DeepLOB

DeepBook

Transformer

etc.

Mi ranking sería

---

## Databento MBP10

★★★★★

---

## TradeStation Aggregates

★★★★☆

Porque ya tienes

```text
Top10

OrderCount

Participants

LargestOrder

SmallestOrder
```

---

## IB

★★☆☆☆

Porque realmente tienes

```text
Price

Size

Position
```

Nada más.

Y debes confiar en la reconstrucción.

---

# Lo que todavía no sabemos (y es decisivo)

Después de leer la documentación, **hay cinco preguntas que siguen sin respuesta pública** y que determinarían si TradeStation puede sustituir a Databento para TSIS:

1. **¿Cada cambio del libro genera un mensaje o TradeStation agrupa cambios en snapshots periódicos?**
2. **¿Cuál es la frecuencia máxima de actualización (10 ms, 50 ms, 100 ms, 250 ms...)?**
3. **¿Los arrays `Bids[]` y `Asks[]` representan un snapshot completo de los `maxlevels` solicitados o sólo los niveles modificados?**
4. **¿Qué ocurre cuando se pierde una conexión? ¿Existe un mensaje explícito de reset o simplemente llega un nuevo snapshot?**
5. **¿Qué cobertura real tiene la agregación?** La documentación habla de "aggregated data from the participants", pero no especifica exactamente qué books (NASDAQ TotalView, ARCA, BATS, EDGX, BX...) intervienen en esa agregación. ([TradeStation API][1])

---

# Mi conclusión para TSIS

La conclusión que saco **después de leer la API**, no por intuición, es bastante diferente de la que tenía antes.

**TradeStation no parece ser simplemente "otro broker con Level 2".**

Su API de `MarketDepthAggregates` está diseñada alrededor de un **objeto agregado de libro**, no alrededor de callbacks de modificaciones individuales. Además expone métricas (`TotalOrderCount`, `NumParticipants`, `BiggestSize`, `SmallestSize`) que **IBKR simplemente no proporciona**. ([TradeStation API][1])

Desde un punto de vista de investigación en ML, eso es mucho más valioso que recibir únicamente `price`, `size` y `position`.

## Lo que yo haría ahora

En lugar de seguir comparando más brokers, creo que merece la pena hacer una **ingeniería inversa de la API de TradeStation**.

No una comparación comercial, sino una investigación técnica de unas 30–40 páginas respondiendo cuestiones como:

* estructura exacta de cada mensaje JSON;
* semántica de cada campo;
* comportamiento temporal;
* cobertura de exchanges;
* consistencia del snapshot;
* throughput máximo;
* límites de símbolos;
* reconstrucción del libro;
* validación frente a Databento MBP-10.

Esa investigación nos permitiría responder con evidencia si **TradeStation puede convertirse en el "Databento retail" para TSIS** o si, por el contrario, sólo ofrece snapshots enriquecidos insuficientes para investigación cuantitativa seria. Creo que esa es la siguiente decisión técnica importante antes de diseñar toda la capa de microestructura.

[1]: https://api.tradestation.com/docs/specification/?utm_source=chatgpt.com "Specification | TradeStation API"
[2]: https://interactivebrokers.github.io/tws-api/market_depth.html?utm_source=chatgpt.com "TWS API v9.72+: Market Depth (Level II)"
