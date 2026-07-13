Sí: **si realmente quieres descubrir científicamente qué valor aporta MBO, no puedes entrenar usando solamente los 3–5 símbolos que finalmente habrías operado**.

Esa arquitectura de:

```text
20–30 candidatos → MBP-10
3–5 oportunidades → MBO
```

puede ser válida para **producción en vivo**, cuando el modelo ya existe. Pero sería insuficiente para construir el primer modelo porque eliminaría muchas oportunidades rechazadas y numerosos casos negativos necesarios para aprender.

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

---

# Cómo plantearía el dataset

No descargaría veinte años de MBO de todas las acciones. Sería innecesario, probablemente imposible con la cobertura disponible y extraordinariamente caro.

La tabla que has mostrado indica que Databento ofrece más de ocho años en algunos datos históricos, pero la disponibilidad depende del plan y del esquema; en Standard y Plus, por ejemplo, MBO aparece limitado al último mes, mientras que Unlimited anuncia más de ocho años. Además, actualmente Databento señala que Nasdaq TotalView-ITCH es su único feed de acciones estadounidenses en tiempo real con MBP-10 y MBO. ([Databento][1])

Plantearía la construcción en dos etapas.

## Etapa 1: reconstruir el universo histórico sin usar MBO

Primero ejecutarías tu scanner, día por día, utilizando exclusivamente datos que habrían estado disponibles antes o en ese momento.

Ejemplo:

```text
Fecha: 2022-06-14
Hora del scanner: 09:15 ET

Inputs disponibles entonces:
- precio premarket;
- gap;
- volumen premarket;
- float conocido ese día;
- market cap conocida entonces;
- noticias publicadas hasta esa hora;
- previous close;
- ATR histórico;
- volumen relativo;
- cambios porcentuales;
- restricciones de precio y liquidez.

Resultado del scanner:
A, B, C, D, E ... 23 símbolos
```

Después repites el procedimiento para cada día.

El resultado sería una tabla de selección:

| Fecha      | Símbolo | Hora selección | Pasó scanner | Razón                |
| ---------- | ------- | -------------: | -----------: | -------------------- |
| 2022-06-14 | ABCD    |          09:15 |            1 | gap + RVOL           |
| 2022-06-14 | EFGH    |          09:15 |            1 | news + volume        |
| 2022-06-14 | IJKL    |          09:15 |            0 | volumen insuficiente |

El punto decisivo es que el scanner debe reconstruirse **point-in-time**. No puedes usar la lista actual de símbolos y retroceder, porque excluirías empresas deslistadas, cambios de ticker, fusiones, quiebras y otras transformaciones. Databento conserva los símbolos históricos tal como existían en cada momento y ofrece un security master point-in-time con valores listados y deslistados, precisamente para evitar esta clase de error. ([Databento][2])

---

# Etapa 2: comprar MBO únicamente para el universo seleccionado históricamente

Una vez reconstruidos los candidatos de cada día, solicitas MBO solo para:

```text
día D
+
símbolos que pasaron el scanner en D
+
franja temporal relevante
```

Por ejemplo:

```text
ABCD
2022-06-14
08:00–11:30 ET
```

No necesitarías descargar necesariamente:

```text
ABCD
todo el día
todos los días del año
```

Y mucho menos todos los símbolos del mercado.

Tu unidad de adquisición sería:

```text
symbol-date-window
```

Por ejemplo:

```text
ABCD | 2022-06-14 | 08:00–11:30
EFGH | 2022-06-14 | 08:00–11:30
MNOP | 2022-06-15 | 08:00–11:30
```

Databento define MBO como cada evento de orden individual, identificado por `order_id`, incluyendo altas, cancelaciones, modificaciones, operaciones y otros eventos del libro; sus snapshots permiten reconstruir la prioridad de las órdenes dentro de cada nivel. ([Databento][3])

---

# ¿Hay sesgo de supervivencia si seleccionas los tickers que pasaron el scanner?

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

---

# Tu dataset no debería contener únicamente “eventos”

Aquí hay una distinción muy importante.

Tú describes:

```text
evento 1: acción dormida
evento 2: explosión de volumen
evento 3: continuación
evento 4: final del push
```

Eso es útil como **segmentación posterior**, pero el modelo debe recibir estados construidos sin mirar el futuro.

Por ejemplo, a las 09:42:17:

```text
state_t
```

solo puede contener información hasta las 09:42:17.

Después puedes calcular outcomes:

```text
máximo avance en 2 segundos
máximo avance en 5 segundos
máximo avance en 15 segundos
máximo avance en 30 segundos
máximo avance en 60 segundos
máxima excursión adversa
tiempo hasta ruptura
tiempo hasta fallo
R realizable bajo política X
```

La separación debe ser:

```text
STATE TABLE
Lo observable en t
```

y, en otra tabla:

```text
OUTCOME TABLE
Lo sucedido después de t
```

Nunca introduciría directamente “evento 3 = continuación” como feature observable, porque esa clasificación puede contener información futura.

---

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

---

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
