# Cómo reducir coste de data

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

## Opción 1 : Reducir muchísimo el universo

Aquí es donde creo que tu proyecto TSIS tiene una ventaja enorme.   
Tú NO necesitas: 20.000 acciones.  
Tú mismo me has explicado varias veces que:

```
Universe Builder
↓
20 candidatos
↓
solo esos pasan al motor.
```
Eso cambia completamente el problema.  
Imagina:  
```
09:30 Universe Builder encuentra
KZIA
ABEO
APDN
...
...
20 símbolos.
```

Desde ese momento `solamente necesitas L2/L3 para esos 20`.  
No para todo el mercado.  
Eso reduce muchísimo: ancho de banda, conexiones, consumo    
y en algunos proveedores también el coste (cuando facturan por uso o por volumen). ([Databento][2])



## Opción 2 - Comprar únicamente NASDAQ

Aquí hay una observación importante.  
Tus small caps... ¿cotizan dónde?  
La mayoría: Nasdaq.
No NYSE.  
No CBOE.  
No ARCA.  

Es decir...  
Quizá el 90% de tu edge esté en   
**Nasdaq TotalView.**

Y no necesites comprar:
* NYSE
* CBOE
* MEMX
* MIAX
* etc.

Muchísimos traders institucionales hacen exactamente eso.  
Compran solamente el exchange donde está el activo.

## Opción 3 : Broker + feed externo

Esto es muy común.

Ejemplo:
```
IBKR
↓
ejecuta órdenes

Databento
↓
solo datos
```
o
```
IBKR
↓
ejecución

dxFeed
↓
profundidad
```
o
```
IBKR
↓
ejecución

Nasdaq directamente
↓
TotalView
```

Muchos fondos pequeños trabajan así. ([dxFeed Market Data][3])


## Opción 4 : Replantear qué necesitas realmente

Aquí creo que merece la pena detenerse.  
Has dicho:

```
"mi estrategia quiere medir eso"
```

La pregunta científica sería:

```
¿Qué es exactamente "eso"?
```
Porque muchas veces la respuesta no es realmente MBO.  
Por ejemplo.  

Quieres medir: ***spoofing*** → `sí necesitas MBO`.  
Quieres medir: ***absorción*** : `Quizá MBP-10 sea suficiente.`  
Quieres medir: ***book pressure*** : `MBP-10.`  
Quieres medir: ***queue imbalance*** : `MBP-10`.    
Quieres medir: ***liquidity vacuum*** : `MBP-10`.  
Quieres medir: ***iceberg*** : `MBO ayuda mucho`. Pero no siempre es imprescindible.

Es decir...  
```
Puede que el 80% del edge venga de MBP-10.  
Y solamente un 20% requiera MBO.
```
Eso reduce muchísimo el coste.

## Opción 5 (la que probablemente haría un hedge fund)

No procesar **L3** en todos los símbolos.

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




## Lo que yo haría si estuviera construyendo TSIS

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


## Arquitectura híbrida

Y aquí creo que está la oportunidad más interesante para TSIS.  
En lugar de intentar comprar **todos los feeds L2/L3**, puedes diseñar una arquitectura híbrida.

Por ejemplo:

* L1 completo para todo el universo.
* MBP-10 únicamente para los 20-30 símbolos que el *Universe Builder* selecciona.
* MBO únicamente para los 3-5 símbolos donde realmente vas a tomar una decisión de entrada.

Desde el punto de vista científico, eso sigue siendo totalmente válido, porque   
**el dato más caro solo se consume cuando ya existe una hipótesis razonable de que el activo merece ese nivel de observación**.



[1]: https://databento.com/microstructure/level-2-market-data?utm_source=chatgpt.com "What is level 2 (L2) market data? | Databento Microstructure Guide"
[2]: https://databento.com/equities?utm_source=chatgpt.com "Equities Market Data - Real-time & historical equities API"
[3]: https://dxfeed.com/coverage/us/?utm_source=chatgpt.com "US Securities Provided by dxFeed Market Data Services"

<br>
<br>

# ¿Cómo entrenar modelo con MBO 3-5 símbolos?

**si realmente quieres descubrir científicamente qué valor aporta MBO,**   
**no puedes entrenar usando solamente los 3–5 símbolos que finalmente habrías operado**.

Esa arquitectura de:

```text
20–30 candidatos → MBP-10
3–5 oportunidades → MBO
```

puede ser válida para **producción en vivo**, cuando el modelo ya existe.   
Pero sería insuficiente para construir el primer modelo porque eliminaría muchas oportunidades     
rechazadas y numerosos casos negativos necesarios para aprender.

## La separación fundamental

Debemos distinguir dos problemas:

### Entrenamiento histórico

Necesitas MBO para una muestra suficientemente amplia de:

* pushes que continuaron;
* pushes que fracasaron;
* squeezes;
* falsas explosiones de volumen;
* intentos que no llegaron a convertirse en setup;
* acciones seleccionadas por el scanner que permanecieron dormidas;
* oportunidades aparentemente buenas que acabaron en pérdida;
* oportunidades que el trader humano habría descartado.

### Inferencia en vivo

Cuando el sistema ya ha aprendido qué situaciones merecen atención, entonces sí puedes aplicar una cascada:

```text
Mercado completo
        ↓
Scanner barato: daily + L1 + trades
        ↓
20–30 candidatos
        ↓
MBP-10/MBO para esos candidatos
        ↓
Modelo de microestructura
        ↓
3–5 oportunidades operables
```

No debes confundir el coste de recopilar el dataset inicial con el coste operativo diario del modelo terminado.


## Cómo plantearía el dataset

No descargaría veinte años de MBO de todas las acciones.   
Sería innecesario, probablemente imposible con la cobertura disponible y extraordinariamente caro.

Plantearía la construcción en dos etapas.

### Reconstruir el universo histórico sin usar MBO

Primero ejecutarías tu scanner, día por día,   
utilizando exclusivamente datos que habrían estado disponibles antes o en ese momento.

```text
Mercado completo
↓
Scanner barato con datos L1/trades/fundamentales
↓
símbolos que cumplen tus filtros dinámicos
↓
MBO para todos esos candidatos
↓
modelo de microestructura
↓
3–5 oportunidades operables
```

Por tanto, **sí: los símbolos que entren dinámicamente en tu scanner son, en principio, aquellos para los que necesitas recoger MBO**, aunque después muchos no desarrollen ningún push y nunca sean operados. Esos casos negativos son precisamente necesarios para entrenar.

Tus filtros son:

```text
Market cap < 100 M
0,50 < precio < 20 USD
Volumen acumulado > 300.000
```

Los dos últimos cambian durante la sesión:  
Debes reconstruir un *scanner continuo o event-driven*.

**Cómo se reconstruye técnicamente**

Tienes que recorrer el mercado cronológicamente, igual que lo haría TradeStation en vivo.  
Por cada símbolo mantienes un estado:

```text
último precio
volumen acumulado de la sesión
market cap point-in-time
estado actual: elegible / no elegible
hora de entrada en el scanner
hora de salida del scanner
```

Cada vez que llega una operación o una barra, actualizas:

```text
last_price
cumulative_volume
market_cap_estimated
```

Y vuelves a evaluar:

```python
eligible = (
    market_cap < 100_000_000
    and 0.50 < last_price < 20.00
    and cumulative_volume > 300_000
)
```

Cuando pasa de `False` a `True`:

```text
SCANNER_ENTER
```

Cuando pasa de `True` a `False`:

```text
SCANNER_EXIT
```

Ejemplo:

| Hora ET | Precio | Volumen acumulado | Market cap | Estado          |
| ------: | -----: | ----------------: | ---------: | --------------- |
|   07:15 |   1,42 |            90.000 |       18 M | fuera           |
|   07:48 |   1,67 |           275.000 |       21 M | fuera           |
|   07:51 |   1,71 |           305.000 |       22 M | entra           |
|   08:20 |   1,95 |           850.000 |       25 M | dentro          |
|   09:34 |   0,47 |         2.100.000 |        6 M | sale por precio |
|   09:39 |   0,53 |         2.400.000 |        7 M | vuelve a entrar |

Tu tabla histórica debería conservar todos esos cambios:

```text
scanner_membership_intervals
```

| Fecha      | Símbolo |  Entrada |   Salida | Motivo entrada | Motivo salida |
| ---------- | ------- | -------: | -------: | -------------- | ------------- |
| 2022-06-14 | ABCD    | 07:51:12 | 09:34:08 | volumen >300k  | precio <0,50  |
| 2022-06-14 | ABCD    | 09:39:41 | 16:00:00 | precio >0,50   | fin sesión    |

Eso reproduce mucho mejor el comportamiento de un scanner real.

**¿A qué hora se ejecuta?**

No necesitas necesariamente recalcular literalmente cada segundo si usas datos event-driven. Puedes actualizar cada vez que llega:

* una operación;
* una actualización de precio;
* una nueva barra de un segundo;
* o una barra de un minuto, si en la primera fase aceptas menor precisión.

Para hiperscalping, terminarás queriendo trades o intervalos de un segundo, no únicamente barras de un minuto.

**¿Se hace un barrido de todo el día y nos quedamos con las que entraron?**

Sí, pero con una precisión conceptual importante.

Históricamente haces un replay de todo el periodo operativo y conservas todos los símbolos que hayan entrado al menos una vez en el scanner.

Por ejemplo:

```text
scanner_union_for_day =
todos los símbolos que fueron elegibles
en algún instante entre 04:00 y 20:00
```

Esa unión puede ser:

```text
ABCD
EFGH
IJKL
MNOP
QRST
```

Pero no debes limitarte a guardar una lista diaria. También debes conservar:

```text
cuándo entraron
por qué entraron
cuánto tiempo permanecieron
cuándo salieron
si volvieron a entrar
```

Porque un símbolo que entra a las 10:45 no debería contaminar el dataset como si hubiera sido candidato desde las 07:00.

### Entonces, ¿qué `MBO` comprar?

Hay tres niveles posibles.

**Nivel 1: MBO durante todo el día para cada ticker que entró**

Ejemplo:

```text
ABCD entró en el scanner a las 08:12
```

Compras:

```text
ABCD, 07:00–11:30
```

Ventaja:

* tienes el contexto anterior;
* puedes estudiar qué precedió a la entrada;
* puedes reconstruir la evolución completa;
* evitas problemas de inicialización del libro.

Desventaja:

* es más caro.

Esta sería la opción científicamente más limpia para una muestra inicial.

**Nivel 2: pre-roll + intervalo elegible + post-roll**

Ejemplo:

```text
Entrada: 08:12
Salida: 09:05
```

Compras:

```text
08:07–09:15
```

Es decir:

```text
5 minutos antes
+
todo el periodo elegible
+
10 minutos después
```

Esto reduce mucho los datos, pero todavía permite estudiar:

* qué ocurrió antes de alcanzar 300.000;
* la explosión que produjo la entrada;
* la continuidad o fallo posterior;
* el final del push.

Para tu investigación podría ser una opción razonable.

**Nivel 3: MBO solo después de la entrada**

Ejemplo:

```text
MBO desde 08:12 en adelante
```

Es la opción más barata, pero tiene dos problemas:

1. pierdes la microestructura que precedió a la entrada;
2. necesitas recibir un snapshot válido del libro al suscribirte.

Si el proveedor solo empieza a emitir eventos MBO sin un snapshot completo, no podrás reconstruir correctamente las órdenes que ya existían antes de tu suscripción.

### Históricamente, ¿qué tickers elegir?

Para cada día:

```text
1. Obtener universo point-in-time de acciones válidas.
2. Aplicar market cap <100 M.
3. Recorrer trades o barras intradía cronológicamente.
4. Mantener precio y volumen acumulado.
5. Detectar todos los SCANNER_ENTER.
6. Conservar todos los símbolos que entraron.
7. Solicitar MBO para esos symbol-days.
8. Añadir una ventana previa a la entrada.
```

Formalmente:

```text
MBO historical acquisition set =
todos los symbol-days que habrían pasado
el scanner en tiempo real
```

No:

```text
solo símbolos que hicieron un gran squeeze
```

Y tampoco:

```text
solo símbolos que finalmente operaste
```

**¿Necesitas también los que nunca alcanzaron 300.000?**

Para responder a tu pregunta original, no necesariamente todos.

Pero científicamente conviene añadir una muestra de **near misses**:

```text
Market cap <100 M
precio 0,50–20
volumen máximo del día entre 200k y 299.999
```

¿Por qué?

Porque, si solo entrenas con acciones que cruzaron 300.000, el modelo aprende dentro del universo condicionado por ese cruce. Eso está bien si tu política siempre exigirá 300.000, pero no podrá responder:

> ¿Qué diferencia microestructural había entre las que estuvieron a punto de activarse y las que explotaron?

Una muestra de controles podría ser:

```text
Por cada 4 candidatos que cruzan 300k:
1 símbolo similar que terminó entre 200k–300k
1 símbolo similar que cumplía precio y market cap pero permaneció inactivo
```

No necesitas comprar MBO para miles de acciones dormidas. Necesitas una muestra de control razonable.

# ¿Hay sesgo de supervivencia son solo tickers que pasaron el scanner?

**No necesariamente.**

Seleccionar históricamente todos los símbolos que habrían pasado el scanner cada día es precisamente una forma correcta de evitar el sesgo de supervivencia, siempre que cumplas estas condiciones:

1. Incluyas empresas posteriormente deslistadas.
2. Utilices el ticker que existía ese día.
3. Utilices los fundamentales y atributos conocidos en ese momento.
4. No selecciones el símbolo porque hoy sabes que hizo un squeeze.
5. Incluyas todos los candidatos, aunque no desarrollaran ningún patrón.
6. No limites la muestra a las operaciones que acabaron siendo ganadoras.

Pero existe otro sesgo diferente y posiblemente más peligroso:

## Sesgo de selección por resultado

Sería incorrecto hacer esto:

```text
Buscar retrospectivamente los mejores pushes
        ↓
Descargar MBO alrededor de ellos
        ↓
Entrenar el modelo
```

Porque el modelo solo observaría eventos que sabes que terminaron siendo interesantes.

La selección correcta es:

```text
Scanner point-in-time
        ↓
Todos los candidatos del día
        ↓
Descargar MBO para todos
        ↓
Después descubrir cuáles:
- no hicieron nada;
- fallaron;
- continuaron;
- exprimieron;
- revirtieron.
```

El resultado nunca debe decidir qué datos descargas.

# Cómo convertir MBO en estados manejables

No entrenaría inicialmente el modelo directamente con miles de mensajes MBO crudos por segundo.

Primero reconstruiría el libro y generaría variables causales por ventanas cortas.

## Variables de estado MBO

Por ejemplo, cada 100 ms, 250 ms o 1 segundo:

### Libro

* profundidad por nivel;
* profundidad acumulada;
* imbalance bid/ask;
* microprice;
* distancia entre niveles;
* convexidad del libro;
* concentración de liquidez;
* huecos de liquidez;
* estabilidad del best bid/ask;
* número de órdenes por nivel;
* tamaño medio y mediano por orden.

### Flujo de órdenes

* adds bid/ask;
* cancels bid/ask;
* modifies;
* cancel-to-add ratio;
* cancel-to-trade ratio;
* reposición tras ejecuciones;
* retirada de liquidez;
* stacking;
* pulling;
* persistencia de órdenes;
* vida media de las órdenes;
* velocidad de llegada de mensajes.

### Cola

* órdenes delante;
* cambios de prioridad;
* tamaño de cola;
* velocidad de consumo;
* probabilidad estimada de fill;
* replenishment en el mismo precio;
* repetición de tamaños;
* aparente iceberg/reload.

### Tape

* agresiones al ask;
* agresiones al bid;
* signed volume;
* tamaño de prints;
* aceleración del tape;
* trades por segundo;
* volumen por segundo;
* porcentaje de ejecuciones que mueven el precio;
* respuesta del precio a la agresión;
* absorción estimada.

MBO permite estudiar la vida de cada orden y reconstruir posiciones de cola; MBP-10 solamente proporciona cambios agregados por precio en los diez primeros niveles, junto con tamaño y número agregado de órdenes. ([Databento][3])


# No empezaría con Offline RL

Con tu situación actual, el orden científico debería ser:

## Fase 1: supervisado

Primero responder preguntas más sencillas:

```text
Dado state_t:
¿cuál es la probabilidad de +0,5 R antes de -0,25 R?
¿cuál es la probabilidad de extensión en 5/15/30 segundos?
¿cuál será MFE?
¿cuál será MAE?
¿estamos ante continuación, fallo o neutralidad?
```

Modelos iniciales:

* logistic regression;
* gradient-boosted trees;
* random forest como baseline;
* XGBoost/LightGBM;
* temporal CNN;
* TCN;
* transformer temporal pequeño.

Esto te permitirá comprobar:

* si MBO añade información;
* qué variables aportan;
* en qué horizontes;
* en qué regímenes;
* si el edge sobrevive a costes y latencia.

## Fase 2: modelos secuenciales

Después:

* LSTM/GRU;
* TCN;
* transformer;
* representación autoregresiva del order flow;
* modelos multimodales con mercado + chart + MBO.

## Fase 3: imitation learning

Si registras tus decisiones reales:

```text
estado
acción humana
timing
size
salida
```

puedes entrenar primero behavioral cloning y estudiar qué parte de tu reconocimiento discrecional es reproducible.

## Fase 4: Offline RL

Solo cuando tengas un dataset con:

```text
s_t
a_t
r_t
s_t+1
done
behavior_policy
```

y acciones tanto buenas como malas.

CQL e IQL son métodos de Offline RL. No son inicialmente métodos para descubrir si una variable MBO predice un squeeze. Su objetivo es aprender una política de decisión evitando, hasta cierto punto, acciones alejadas de la distribución observada.

## Decision Transformer

También necesita secuencias:

```text
return-to-go
estado
acción
return-to-go
estado
acción
...
```

Si todavía no tienes acciones históricas coherentes ni una definición estable de recompensa, aplicar Decision Transformer sería prematuro.

---

# ¿Cuánta historia necesitas?

Para hiperscalping, el número de años no es la unidad principal. Importan más:

* número de días;
* número de símbolos-día;
* número de eventos independientes;
* diversidad de regímenes;
* diversidad de resultados;
* cantidad de pushes/fallos;
* cobertura de distintas condiciones de mercado.

Cinco años con:

```text
20 candidatos/día
× 250 días
× 5 años
= 25.000 symbol-days
```

puede ser mucho más valioso que veinte años de barras si cada symbol-day contiene millones de eventos y cientos de estados relevantes.

No obstante, 25.000 symbol-days completos de MBO pueden seguir siendo enormes. Por eso construiría un diseño por capas.

---

# Diseño de adquisición que considero realista

## Capa A: universo amplio y barato

Para todo el mercado:

* daily;
* OHLCV de 1 minuto;
* trades;
* BBO/L1;
* noticias y datos de referencia;
* scanner point-in-time.

Objetivo:

```text
reconstruir los candidatos históricos
```

## Capa B: muestra MBO de descubrimiento

Comprar inicialmente MBO para una muestra estratificada, por ejemplo:

```text
100–150 días
20–30 candidatos diarios
2–4 horas por símbolo
```

Seleccionando deliberadamente:

* mercado alcista;
* mercado bajista;
* alta volatilidad;
* baja volatilidad;
* días con squeezes;
* días sin squeezes;
* runners;
* falsos runners;
* stocks con distintos floats;
* distintos rangos de precio;
* distintos tipos de catalizador.

Esto podría producir aproximadamente:

```text
2.000–4.500 symbol-days
```

Suficiente para desarrollar el pipeline y comprobar si MBO aporta señal incremental.

## Capa C: expansión dirigida

Después de conocer:

* qué franjas horarias importan;
* qué variables son útiles;
* qué tipos de candidatos son relevantes;
* cuánto historial hace falta;

ampliarías la compra histórica solo donde aumenta la potencia estadística.

## Capa D: recogida prospectiva

Desde el momento en que contratas live, guardarías continuamente MBO de todos los candidatos del scanner:

```text
scanner → 20 candidatos → almacenar MBO de los 20
```

Aunque el modelo solo opere 3–5.

Esto es crucial: **en vivo puedes procesar para trading solamente los mejores, pero para investigación debes conservar los descartados**.

---

# La arquitectura correcta para TSIS

```text
1. Historical Point-in-Time Universe Builder
   ↓
2. Daily Scanner Replay
   ↓
3. Candidate Symbol-Day Table
   ↓
4. Historical MBO Acquisition Manifest
   ↓
5. Raw MBO Archive
   ↓
6. Deterministic Order Book Reconstruction
   ↓
7. State Builder: 100 ms / 250 ms / 1 s
   ↓
8. Event Candidate Detection
   ↓
9. Outcomes separados
   ↓
10. Supervised baselines
   ↓
11. Incremental-value study:
       L1
       L1 + MBP
       L1 + MBP + MBO
   ↓
12. Imitation / Offline RL
```

El paso 11 es especialmente importante. No debes asumir que MBO aporta valor porque intuitivamente parezca más rico.

Debes comparar:

```text
Modelo A: solo trades + L1
Modelo B: trades + MBP-10
Modelo C: trades + MBP-10 + features exclusivas MBO
```

Manteniendo iguales:

* fechas;
* candidatos;
* labels;
* splits temporales;
* modelo;
* hiperparámetros;
* costes;
* latencia simulada.

Entonces podrás decir:

> MBO aporta una mejora out-of-sample de X sobre MBP-10 para detectar continuación a 5 segundos, pero no aporta valor a 60 segundos.

Esa es la conclusión científica que justificaría pagar por el feed.

## Mi recomendación concreta

No compraría todavía ocho años completos ni entrenaría directamente CQL, IQL o Decision Transformer.

Empezaría con:

```text
6–12 meses de MBO
todos los candidatos históricos del scanner
no solo los ganadores
ventanas 07:00–12:00 ET o más estrechas
estados a 250 ms y 1 segundo
labels multihorizonte
modelos supervisados
comparación L1 vs MBP vs MBO
```

Después ampliaría a dos o tres años solo si la primera fase demuestra una aportación incremental estable.

La regla central sería:

> **En entrenamiento, MBO para todos los candidatos seleccionados ex ante. En producción, MBO puede concentrarse dinámicamente en las oportunidades de mayor prioridad.**

Eso evita tanto el sesgo de supervivencia como el error más peligroso: entrenar únicamente con patrones que retrospectivamente sabemos que existieron.

[1]: https://databento.com/equities?utm_source=chatgpt.com "Equities Market Data - Real-time & historical equities API"
[2]: https://databento.com/docs/standards-and-conventions/symbology?utm_source=chatgpt.com "Symbology | Databento standards & conventions"
[3]: https://databento.com/docs/schemas-and-data-formats/mbo?utm_source=chatgpt.com "Market by order (MBO) | Databento schemas & data formats"


