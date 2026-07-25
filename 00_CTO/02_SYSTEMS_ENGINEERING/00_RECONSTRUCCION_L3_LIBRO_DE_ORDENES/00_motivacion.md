
Este documento surge por la inquietud de obtener toda la data posible del mercado de SmallCaps.  
En el documento [DAS_0003_DATA_DESEADA_EN_LIVE](C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\DAS_0003_DATA_DESEADA_EN_LIVE.md) detalla las definiciones de:

- L3 / Market-By-Order / Order Lifecycle
- L2 / Market-By-Price Depth
- Auction Imbalance / Opening Imbalance / NOII
- Execution, Orders, Fills And Routing
- Fee/Rebate, Tick Size And Venue Rule State
- etc

---

```
¿cómo los profesionales realmente capturan, almacenan y utilizan datos MBO/LOB para investigación y ML?

¿Quiénes son las 30-50 personas del mundo que realmente trabajan con MBO, Nasdaq ITCH, TotalView y reconstrucción de libros de órdenes?
```

Eso incluye:
```
investigadores de Oxford (DeepLOB, MBO),
desarrolladores de Databento,
ingenieros de dxFeed,
autores de parsers ITCH,
desarrolladores de Bookmap,
ingenieros de matching engines,
autores de librerías open source de reconstrucción de order books.
```

Esa gente publica en:
```
YouTube,
GitHub,
conferencias,
blogs técnicos,
podcasts,
presentaciones de universidades,
repositorios de código.
```

Creo que esa investigación tendría muchísimo más valor para TSIS que seguir comparando proveedores, porque probablemente descubriríamos cómo los profesionales realmente capturan, almacenan y utilizan datos MBO/LOB para investigación y ML, además de posibles soluciones retail que no aparecen en la documentación comercial.



[![(PDF) Deep Learning for Market by Order Data](https://tse4.mm.bing.net/th/id/OIP.yspBbNIdMQbkWz58d1_kTQHaJl?r=0\&pid=Api)](https://www.researchgate.net/publication/349391697_Deep_Learning_for_Market_by_Order_Data?utm_source=chatgpt.com)

He revisado los trabajos, papers y repositorios más relevantes intentando responder únicamente a estas preguntas:

1. **¿De dónde obtienen realmente los profesionales los datos MBO/L3?**
2. **¿Capturan live o compran histórico?**
3. **¿Cómo reconstruyen y almacenan el libro?**
4. **¿Cómo transforman esos datos para ML, simulación o RL?**

La conclusión más importante es ésta:

> La mayoría de los investigadores punteros que publican sobre MBO/LOB **no captura un feed live retail durante años**. Utilizan históricos derivados directamente de los feeds nativos de las bolsas, especialmente **Nasdaq TotalView-ITCH**, normalmente comprados o procesados a través de **LOBSTER**, o reciben datasets institucionales no públicos de bolsas, universidades o empresas colaboradoras.

La arquitectura dominante no es:

```text
broker retail
→ websocket
→ guardar DOM
→ entrenar ML
```

Sino:

```text
feed nativo de la bolsa
→ mensajes MBO históricos
→ parser/reconstructor
→ log de mensajes + snapshots LOB
→ normalización
→ dataset de entrenamiento
→ ML / RL / simulación
```

# 1. Zihao Zhang, Bryan Lim y Stefan Zohren

## Deep Learning for Market by Order Data

Éste es probablemente el trabajo más cercano intelectualmente a lo que quieres construir.

Utilizaron:

* cinco acciones muy líquidas;
* un año completo, 2018;
* datos de la London Stock Exchange;
* más de 169 millones de eventos;
* aproximadamente 46 millones de observaciones sólo en test;
* mensajes MBO individuales;
* un LOB derivado de diez niveles para comparación. 

Las acciones fueron:

```text
LLOY
BARC
TSCO
BT
VOD
```

## Proveedor

El paper identifica la bolsa de origen —London Stock Exchange—, pero **no identifica al proveedor comercial, contrato o vendor concreto**.

No hay evidencia pública de que compraran el dataset a:

* Refinitiv;
* Bloomberg;
* LSEG Data;
* BMLL;
* algún broker.

Por tanto, lo correcto es clasificarlo así:

```text
Origen del dato:
London Stock Exchange

Proveedor comercial:
no declarado

Probable modalidad:
dataset institucional o académico,
no suscripción retail live
```

No debemos inventar el vendor.

## Qué contiene su MBO

Para cada mensaje construyen una representación basada en la orden individual:

```text
tipo de evento
lado
precio
cantidad
nivel del libro
posición de la orden dentro de la cola
```

El punto esencial es que reconstruyen el libro paso a paso y asignan a cada orden su posición y nivel. El MBO se interpreta como una secuencia de mensajes desde la cual se deriva el LOB. 

## Cómo lo utilizan para ML

Usan ventanas de:

```text
50 actualizaciones MBO anteriores
```

No cincuenta segundos ni cincuenta milisegundos.

Trabajan en **event time o tick time**:

```text
t = llegada de un nuevo evento
```

Los horizontes de predicción son:

```text
20 eventos
50 eventos
100 eventos
```

El objetivo es predecir:

```text
sube
permanece estable
baja
```

Utilizan:

* regresión lineal;
* MLP;
* LSTM;
* mecanismos de atención;
* ensemble entre modelo MBO y modelo LOB. 

## Resultado relevante para TSIS

El modelo basado solamente en MBO no fue claramente superior al LOB. Sin embargo, el ensemble:

```text
modelo MBO
+
modelo LOB
```

superó a cada representación individual.

Esto significa que:

> El MBO contiene información adicional, pero no sustituye necesariamente al MBP/LOB. Ambas representaciones pueden ser complementarias. ([arXiv][1])

---

# 2. El mismo grupo Oxford: ClusterLOB

Autores:

* Yichi Zhang;
* Mihai Cucuringu;
* Alexander Shestopaloff;
* Stefan Zohren.

Este proyecto es especialmente valioso porque trabaja directamente con:

```text
ADD
CANCEL
TRADE
```

y no sólo con snapshots de diez niveles.

## Proveedor real

Aquí sí está declarado:

> Los datos proceden de **LOBSTER**, que reconstruye el libro utilizando Nasdaq ITCH. ([GitHub][2])

La cadena real es:

```text
Nasdaq Historical TotalView-ITCH
        ↓
LOBSTER
        ↓
message file + order book file
        ↓
ClusterLOB
```

Utilizan:

* un año de MBO;
* 15 acciones Nasdaq;
* acciones clasificadas como small-tick, medium-tick y large-tick;
* eventos individuales de órdenes. ([arXiv][3])

## Qué hacen con las órdenes

A cada evento individual le añaden seis características dependientes del tiempo y después aplican:

```text
K-means++
```

para agrupar las órdenes en tres patrones interpretativos:

```text
directional
opportunistic
market-making
```

Posteriormente calculan order-flow imbalance por cluster y por tipo de mensaje:

```text
OFI de additions
OFI de cancellations
OFI de trades
```

en ventanas de 30 minutos.

Después construyen estrategias basadas en esas señales y evalúan su Sharpe fuera de muestra. ([arXiv][3])

## Lección para TSIS

No guardan únicamente:

```text
bid_price_1
bid_size_1
...
ask_price_10
ask_size_10
```

Mantienen también la secuencia de eventos originales porque necesitan distinguir:

```text
liquidez añadida
liquidez cancelada
liquidez ejecutada
```

Esta distinción desaparece en un snapshot MBP-10 puro.

---

# 3. LOBSTER: la infraestructura académica central

LOBSTER no es simplemente un dataset.

Es un **sistema de reconstrucción**.

Su fuente original es:

```text
Nasdaq Historical TotalView-ITCH
```

LOBSTER procesa los mensajes ITCH y reconstruye el libro de cualquier acción negociada en Nasdaq hasta el nivel de profundidad solicitado. ([SSRN][4])

## Qué entrega

Normalmente entrega dos archivos sincronizados:

### Message file

Contiene eventos como:

```text
submission
execution
cancellation
deletion
hidden execution
cross trade
trading halt
```

### Order-book file

Contiene el estado del libro inmediatamente después de cada mensaje:

```text
ask_price_1
ask_size_1
bid_price_1
bid_size_1
...
ask_price_N
ask_size_N
bid_price_N
bid_size_N
```

Es decir:

```text
mensaje n
↔
snapshot del libro después del mensaje n
```

Ésta es una estructura extraordinariamente útil para ML porque alinea:

```text
causa microestructural
con
estado resultante del libro
```

## Por qué aparece en tantos papers

LOBSTER resuelve el trabajo más difícil:

```text
descargar ITCH binario
interpretar los mensajes
gestionar order IDs
gestionar replaces
gestionar ejecuciones parciales
mantener colas
construir los niveles
exportar datos utilizables
```

Muchos investigadores no implementan su propio parser live. Compran o descargan el histórico reconstruido de LOBSTER.

## Limitación importante

LOBSTER no es un feed nacional consolidado.

Representa principalmente el libro de Nasdaq reconstruido desde Nasdaq TotalView-ITCH.

No integra automáticamente:

```text
NYSE Arca
Cboe BZX
Cboe EDGX
IEX
NYSE National
```

Por tanto, sus modelos aprenden la microestructura del venue Nasdaq, no necesariamente la liquidez consolidada estadounidense.

---

# 4. TotalViewITCH.jl: cómo un investigador serio reconstruye y almacena ITCH

Este proyecto muestra de forma muy transparente la arquitectura profesional.

Su fuente es:

```text
Historical Nasdaq TotalView-ITCH
```

Los autores indican que el feed contiene toda la actividad de órdenes y cotizaciones en Nasdaq y permite reconstruir el libro a profundidad arbitraria con precisión de nanosegundos. ([GitHub][5])

## Pipeline real

```text
archivo binario ITCH
        ↓
deserialización de mensajes
        ↓
reconstrucción de órdenes
        ↓
generación de snapshots
        ↓
persistencia por ticker y fecha
```

## Mensajes que conserva

El sistema almacena:

```text
Add
Cancel
Delete
Replace
Execute
Execute with price
```

Además mantiene:

```text
order reference number
new order reference number
MPID cuando existe
timestamp en segundos
nanosegundos
ticker
lado
precio
```

Cada orden tiene un identificador único durante la sesión. ([GitHub][5])

## Tablas producidas

El proyecto genera cuatro conjuntos:

```text
messages
orderbooks
noii
trades
```

`messages` contiene los cambios del libro.

`orderbooks` contiene un snapshot después de cada cambio.

`noii` contiene mensajes de imbalance de subastas.

`trades` contiene, entre otras cosas, ejecuciones asociadas a órdenes no mostradas. ([GitHub][5])

## Almacenamiento

Ofrece:

```text
CSV particionado
MongoDB
```

y recomienda para escalas grandes:

```text
Apache Parquet
+
Apache Spark
```

La partición utilizada es esencialmente:

```text
tipo_de_tabla/
    ticker=SYMBOL/
        date=YYYY-MM-DD/
            partition.csv
```

Para procesamiento masivo recomienda:

* múltiples procesos;
* varios jobs;
* cluster HPC. ([GitHub][5])

## Lección para TSIS

Los profesionales no guardan una única tabla gigantesca ordenada solamente por timestamp.

Particionan al menos por:

```text
venue
fecha
símbolo
tipo de dato
```

Y suelen conservar dos capas:

```text
raw message log
derived book states
```

---

# 5. MarketGPT — Aaron Wheeler

MarketGPT es uno de los ejemplos abiertos más claros de cómo convertir MBO en una representación entrenable por transformers.

## Proveedor/origen

Utiliza:

```text
Nasdaq TotalView-ITCH 5.0
```

Los archivos raw empleados proceden del FTP público de muestras de Nasdaq. ([GitHub][6])

Esto no significa que Nasdaq regale años completos de ITCH live. El FTP público incluye principalmente archivos de muestra y algunas sesiones históricas útiles para investigación y desarrollo.

## Reconstrucción

El autor utiliza un fork de un reconstructor ITCH.

Para cada símbolo genera:

```text
message.csv
book_20.csv
```

Por ejemplo:

```text
12302019.NASDAQ_ITCH50_AAPL_message.csv
12302019.NASDAQ_ITCH50_AAPL_book_20.csv
```

Después los mensajes se preprocesan a:

```text
NumPy .npy
```

para entrenamiento. ([GitHub][6])

## Pipeline

```text
ITCH comprimido
    ↓
parser/reconstructor
    ↓
message CSV
    ↓
20-level book CSV
    ↓
filtrado de premarket/after-hours
    ↓
tokenización
    ↓
NumPy arrays
    ↓
GPT / Transformer
```

## Cómo utiliza los datos

Los mensajes se transforman en tokens, de forma parecida al procesamiento de lenguaje.

El modelo aprende la secuencia:

```text
ADD
CANCEL
EXECUTE
REPLACE
...
```

Después genera secuencias sintéticas de actividad de mercado.

El repositorio incluye:

* tokenización y decodificación;
* preprocesamiento multiactivo;
* entrenamiento con PyTorch;
* sweeps con Weights & Biases;
* simulador de eventos discretos;
* evaluación contra datos empíricos. ([GitHub][6])

## Lección

No convierte prematuramente todo el MBO a barras ni únicamente a features.

Conserva la secuencia discreta de eventos para que el modelo aprenda:

```text
gramática del mercado
dependencia entre mensajes
distribución temporal
transiciones entre tipos de orden
```

---

# 6. JAX-LOB

Autores principales:

* Sascha Frey;
* Kang Li;
* Peer Nagy;
* Stefan Zohren;
* Jakob Foerster;
* Anisoara Calinescu.

## Proveedor

Utiliza:

```text
LOBSTER
```

para cargar y reproducir mensajes históricos. ([arXiv][7])

Por tanto, la cadena vuelve a ser:

```text
Nasdaq TotalView-ITCH
→ LOBSTER
→ mensajes MBO
→ JAX-LOB
```

## Qué hace distinto

JAX-LOB no se limita a predecir.

Reconstruye un entorno donde:

* entran órdenes históricas;
* entran órdenes del agente;
* se aplican matching y prioridad;
* evoluciona el libro;
* el agente recibe una observación;
* el agente envía una acción;
* se calcula reward.

El motor está escrito para JAX y GPU, lo que permite ejecutar miles de libros en paralelo. ([arXiv][8])

## Carga de datos

El paper describe una estrategia muy concreta:

```text
pre-load de mensajes
en ventanas temporales fijas
no solapadas
```

El número de mensajes por paso es constante, mientras que la duración física del paso puede variar.

Esto convierte la simulación a una representación basada en eventos:

```text
N mensajes históricos por step
```

en lugar de:

```text
1 step = 1 segundo
```

Esta decisión reduce esperas y facilita vectorización GPU. ([arXiv][7])

## Uso

El entorno se emplea para:

* optimal execution;
* market making;
* RL;
* simulación multilibro;
* evaluación de políticas;
* calibración de agentes.

---

# 7. JaxMARL-HFT

Es la evolución multiagente de JAX-LOB.

## Proveedor

También usa mensajes históricos de:

```text
LOBSTER
```

En cada paso procesa conjuntamente:

```text
mensajes históricos de mercado
+
órdenes generadas por agentes RL
```

([ACM Digital Library][9])

El experimento principal emplea aproximadamente:

```text
un año de datos
400 millones de órdenes
```

para entrenar agentes de:

* ejecución;
* market making. ([arXiv][10])

## Arquitectura conceptual

```text
historical MBO replay
         +
actions from execution agent
         +
actions from market-making agent
         ↓
matching engine JAX
         ↓
new LOB state
         ↓
observations and rewards
```

## Uso profesional

Esto es mucho más cercano a cómo se debería usar MBO para Offline RL o simulación contrafactual:

* no entrenar directamente contra un CSV plano;
* reconstruir el entorno;
* inyectar las acciones del agente;
* modelar fills y prioridad;
* calcular inventario, coste y P&L.

---

# 8. LOBS5 — Peer Nagy y colaboradores

Este proyecto utiliza explícitamente:

```text
NASDAQ LOB data from LOBSTER
```

Los archivos se descargan y se preprocesan para entrenamiento. ([GitHub][11])

## Uso

Emplean dos representaciones:

```text
order-book states
+
tokenized messages
```

Los mensajes se convierten en tokens numéricos, mientras que el estado del libro conserva su estructura espacial.

Esto sigue el mismo patrón observado en el paper MBO de Oxford:

> El mensaje original y el libro derivado contienen información distinta y conviene conservar ambas capas.

---

# 9. DeepLOB

Autores:

* Zihao Zhang;
* Stefan Zohren;
* Stephen Roberts.

DeepLOB trabaja principalmente con LOB/MBP, no con MBO individual.

## Datasets

El trabajo utiliza:

1. FI-2010 como benchmark público;
2. un año de cotizaciones de la London Stock Exchange para evaluación más realista. ([arXiv][12])

FI-2010 contiene:

* cinco acciones de Nasdaq Nordic;
* diez días;
* aproximadamente cuatro millones de mensajes;
* diez niveles del libro;
* datos ya normalizados en distintas variantes. ([arXiv][13])

## Proveedor

FI-2010 es un benchmark académico.

Para la parte LSE, el proveedor comercial no se especifica claramente.

## Representación

DeepLOB recibe esencialmente:

```text
bid_price_1 ... bid_price_10
bid_size_1  ... bid_size_10
ask_price_1 ... ask_price_10
ask_size_1  ... ask_size_10
```

utilizando:

* convoluciones para relaciones espaciales entre niveles;
* Inception modules;
* LSTM para dependencia temporal.

No necesita `order_id`.

Por tanto:

```text
DeepLOB
→ necesita MBP-10 / LOB

Deep Learning for MBO
→ necesita lifecycle individual de órdenes
```

Son dos requisitos de datos distintos.

---

# 10. Justin Sirignano y Rama Cont

Este trabajo es famoso porque utiliza una base con:

```text
miles de millones de quotes y transacciones
de acciones estadounidenses
```

y entrena modelos universales sobre muchos activos. ([arXiv][14])

## Proveedor

El paper no publica de forma inequívoca el nombre del vendor comercial.

No es legítimo afirmar que utilizaron:

* Nasdaq TotalView;
* NYSE OpenBook;
* LOBSTER;
* Refinitiv;
* Bloomberg;
* direct feeds.

La descripción pública habla de una gran base de order book, quotes y transactions, pero no permite identificar con certeza al proveedor.

## Qué utilizan

Su modelo incorpora historia de:

* precios;
* tamaños;
* niveles del libro;
* order flow;
* movimientos anteriores.

Pooling:

```text
muchas acciones
+
muchos periodos
```

para buscar patrones universales de formación de precios.

## Lección

La aportación importante no es el sistema de captura, que no está documentado, sino el uso de un dataset transversal:

```text
una red
entrenada sobre muchos instrumentos
```

en vez de un modelo distinto por ticker.

---

# 11. ABIDES — David Byrd, Maria Hybinette y Tucker Balch

ABIDES es una infraestructura de simulación.

Está diseñada alrededor de la semántica de:

```text
Nasdaq ITCH
Nasdaq OUCH
```

y permite ejecutar:

* simulaciones completamente sintéticas;
* replay de sesiones históricas;
* agentes que observan el mercado;
* agentes que insertan órdenes;
* experimentos de latencia;
* market making;
* ejecución. ([par.nsf.gov][15])

## Proveedor

ABIDES no es un proveedor de datos.

La infraestructura puede recibir históricos transformados a eventos compatibles con su modelo. En trabajos abiertos suelen utilizar históricos Nasdaq o series derivadas, pero la fuente comercial concreta depende del experimento.

## Cómo almacena y procesa

La unidad principal es el evento:

```text
timestamp
sender
recipient
message type
payload
```

La simulación utiliza una cola global de eventos ordenada temporalmente.

Esto permite modelar:

```text
latencia exchange
latencia del agente
latencia de red
orden de llegada
matching
confirmaciones
cancelaciones
```

Es mucho más adecuado que un dataframe convencional para estudiar causalidad o latencia.

---

# 12. Stefan Jansen y los parsers ITCH abiertos

El material de Stefan Jansen muestra una arquitectura accesible para investigadores individuales:

```text
descargar archivo Nasdaq ITCH
→ descomprimir
→ parsear mensajes binarios
→ mantener diccionario de órdenes activas
→ reconstruir trades
→ reconstruir libro
→ guardar resultados
```

El proyecto demuestra cómo generar el libro para un símbolo a partir de los mensajes ITCH. ([GitHub][16])

No es una solución live, pero sí enseña el formato que utilizan muchos profesionales para histórico.

---

# 13. Lo que realmente almacenan

Después de revisar estos proyectos, aparecen tres capas recurrentes.

## Capa 1 — Raw exchange messages

Se conserva sin transformar:

```text
venue
trading_date
sequence
exchange_timestamp
message_type
order_id
new_order_id
side
price
quantity
participant_id
match_number
stock_locate
tracking_number
```

Esta capa es inmutable.

## Capa 2 — Normalized order lifecycle

Se transforma el protocolo específico:

```text
ITCH A/F/X/D/U/E/C
```

a una ontología propia:

```text
ADD
MODIFY
CANCEL_PARTIAL
DELETE
EXECUTE_PARTIAL
EXECUTE_FULL
REPLACE
TRADE_HIDDEN
```

## Capa 3 — Derived LOB states

Después de cada mensaje, o a intervalos seleccionados:

```text
bid_price_1
bid_qty_1
bid_order_count_1
...
ask_price_10
ask_qty_10
ask_order_count_10
```

Además se derivan:

```text
spread
midprice
microprice
imbalance
book slope
queue imbalance
cancel intensity
add intensity
trade intensity
order age
replenishment
```

Los proyectos más serios conservan las tres capas. No sustituyen el raw MBO por el MBP-10.

---

# Cómo capturan live los profesionales

Aquí existe mucha menos información pública.

Las firmas de HFT normalmente utilizan:

```text
direct exchange feeds
```

como:

* Nasdaq TotalView-ITCH;
* NYSE Integrated Feed;
* NYSE Arca Integrated;
* Cboe PITCH;
* IEX DEEP;
* CME MDP 3.0.

El pipeline típico es:

```text
multicast UDP
→ network interface timestamping
→ feed handler
→ sequence/gap detection
→ packet recovery
→ order book builder
→ shared memory/ring buffer
→ strategy processes
→ append-only capture
```

Pero los autores académicos analizados rara vez describen haber desplegado personalmente este stack live. Lo normal es que trabajen con:

* histórico de la bolsa;
* LOBSTER;
* datasets de una institución colaboradora;
* datos internos de una firma;
* archivos públicos de muestra.

Por tanto, buscar sus papers no suele revelar un proveedor retail secreto.

---

# Proveedores reales encontrados

| Autor/proyecto           | Mercado             | Fuente/proveedor identificado         | Live o histórico        |
| ------------------------ | ------------------- | ------------------------------------- | ----------------------- |
| Zhang, Lim, Zohren — MBO | LSE                 | Fuente LSE; vendor no declarado       | Histórico institucional |
| DeepLOB                  | LSE / Nasdaq Nordic | LSE no declarado + FI-2010            | Histórico               |
| ClusterLOB               | Nasdaq              | **LOBSTER → Nasdaq ITCH**             | Histórico               |
| JAX-LOB                  | Nasdaq              | **LOBSTER → Nasdaq ITCH**             | Histórico replay        |
| JaxMARL-HFT              | Nasdaq              | **LOBSTER → Nasdaq ITCH**             | Histórico replay        |
| LOBS5                    | Nasdaq              | **LOBSTER**                           | Histórico               |
| MarketGPT                | Nasdaq              | **Nasdaq TotalView-ITCH FTP**         | Histórico/muestra       |
| TotalViewITCH.jl         | Nasdaq              | **Historical TotalView-ITCH**         | Histórico               |
| LOBSTER                  | Nasdaq              | **Nasdaq Historical TotalView-ITCH**  | Histórico reconstruido  |
| Sirignano–Cont           | US equities         | Vendor no declarado                   | Histórico institucional |
| ABIDES                   | Nasdaq-like         | ITCH/OUCH semantics; dataset variable | Simulación/replay       |
| Stefan Jansen tutorial   | Nasdaq              | Nasdaq ITCH FTP/sample                | Histórico               |

# La conclusión para TSIS

La práctica profesional y académica que aparece repetidamente es:

```text
MBO exchange-native
        ↓
guardar todos los mensajes
        ↓
reconstruir lifecycle y libro
        ↓
materializar snapshots MBP-N
        ↓
conservar mensaje y snapshot alineados
        ↓
crear ventanas event-time
        ↓
ML supervisado / clustering / RL / simulación
```

Y no:

```text
pedir snapshots L2 a un broker
→ guardarlos cada 100 ms
→ asumir que tenemos MBO
```

## Para MBP-10

Los modelos tipo DeepLOB pueden funcionar con:

```text
TradeStation aggregate depth
o
IBKR reconstructed depth
```

siempre que se valide:

* completitud;
* frecuencia;
* resets;
* conflation;
* cobertura de venues.

## Para MBO real

Los trabajos de Zhang, ClusterLOB, MarketGPT y JAX-LOB requieren:

```text
ADD
CANCEL
DELETE
REPLACE
EXECUTE
order_id
event ordering
```

Eso no puede reconstruirse fielmente desde IBKR ni desde un MBP-10 agregado.

## La oportunidad retail más realista

La literatura revisada apunta a una estrategia híbrida:

```text
live barato MBP-10-like
para inferencia y captura diaria
        +
Nasdaq ITCH/LOBSTER histórico
para investigación MBO y validación
```

No tendrías exactamente el mismo proveedor en histórico y live, pero sí podrías separar:

```text
Modelos LOB/MBP
→ entrenados y ejecutados con estados top-10

Modelos MBO/lifecycle
→ entrenados con Nasdaq ITCH/LOBSTER
→ utilizados inicialmente como investigación,
simulación y extracción de features
```

La gran limitación para tus small caps es que casi toda esta literatura utiliza acciones muy líquidas. La metodología es transferible, pero **no existe evidencia suficiente de que sus resultados se mantengan automáticamente en microcaps con spreads grandes, halts, odd lots, liquidez fragmentada y books extremadamente inestables**. Esa es precisamente una de las áreas donde TSIS podría producir investigación original.

[1]: https://arxiv.org/abs/2102.08811?utm_source=chatgpt.com "Deep Learning for Market by Order Data"
[2]: https://github.com/yichizhang-oxford/clusterlob?utm_source=chatgpt.com "YichiZhang-Oxford/ClusterLOB"
[3]: https://arxiv.org/abs/2504.20349?utm_source=chatgpt.com "ClusterLOB: Enhancing Trading Strategies by Clustering Orders in Limit Order Books"
[4]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1977207&utm_source=chatgpt.com "LOBSTER: Limit Order Book Reconstruction System"
[5]: https://github.com/cswaney/TotalViewITCH.jl "GitHub - cswaney/TotalViewITCH.jl: A toolkit to process NASDAQ TotalView-ITCH data. · GitHub"
[6]: https://github.com/aaron-wheeler/marketgpt "GitHub - aaron-wheeler/MarketGPT: MarketGPT: Developing a Pre-trained transformer (GPT) for Modeling Financial Time Series · GitHub"
[7]: https://arxiv.org/pdf/2308.13289?utm_source=chatgpt.com "JAX-LOB: A GPU-Accelerated limit order book simulator to ..."
[8]: https://arxiv.org/abs/2308.13289?utm_source=chatgpt.com "JAX-LOB: A GPU-Accelerated limit order book simulator to unlock large scale reinforcement learning for trading"
[9]: https://dl.acm.org/doi/10.1145/3768292.3770416?utm_source=chatgpt.com "JaxMARL-HFT: GPU-Accelerated Large-Scale Multi-Agent ..."
[10]: https://arxiv.org/abs/2511.02136?utm_source=chatgpt.com "JaxMARL-HFT: GPU-Accelerated Large-Scale Multi-Agent Reinforcement Learning for High-Frequency Trading"
[11]: https://github.com/peernagy/LOBS5?utm_source=chatgpt.com "peernagy/LOBS5"
[12]: https://arxiv.org/abs/1808.03668?utm_source=chatgpt.com "DeepLOB: Deep Convolutional Neural Networks for Limit Order Books"
[13]: https://arxiv.org/pdf/2308.01915?utm_source=chatgpt.com "LOB-Based Deep Learning Models for Stock Price Trend ..."
[14]: https://arxiv.org/abs/1803.06917?utm_source=chatgpt.com "Universal features of price formation in financial markets: perspectives from Deep Learning"
[15]: https://par.nsf.gov/servlets/purl/10185795?utm_source=chatgpt.com "Towards High-Fidelity Multi-Agent Market Simulation"
[16]: https://github.com/PacktPublishing/Hands-On-Machine-Learning-for-Algorithmic-Trading/blob/master/Chapter02/01_NASDAQ_TotalView-ITCH_Order_Book/01_build_itch_order_book.ipynb?utm_source=chatgpt.com "Working with Order Book Data: NASDAQ ITCH"
