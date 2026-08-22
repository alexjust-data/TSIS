# From `wake-up` to `market & event state_table`

```
PREMISA INICIAL:  
```


**Las 3 etapas de un frontside**

1. Fenómeno `wake-up`
2. intermedio o `trayectoria de estado`
3. `termination` del frontside

## PROCESO GENERAL

```
MERCADO:
Microcaps y smallcaps estadounidenses intradía pertenecientes al universo PIT   
(instrumentos que podemos observar legalmente en una ventana temporal t)

    Universo PIT diario:
    -------------------
    instrumento listado y permitido +
    market_cap_as_of(t) < $100M +
    $0.50 <= price_as_of(t) <= $20 +
    identidad y datos válidos

    donde

    market_cap_as_of(t) =
    (últimas shares outstanding conocidas en t) × (precio observable en t)

    price_as_of(t) = 
    antes del primer trade premarket → prior close elegible
```
```
FENÓMENO OBSERVABLE:
El ticker abandona su régimen dormido, desarrolla un episodio de activación/frontside y, posteriormente, el régimen comprador se deteriora hasta terminar o transformarse en backside.

    FAMILIA DE FENÓMENOS OBSERVABLES:
    Dormancy
    → activación anómala
    → participación In-Play
    → frontside ascendente
    → deterioro comprador
    → terminación
    → backside
```

```
PREGUNTA CIENTÍFICA:
¿Podemos representar el estado observable del mercado durante todo el episodio y detectar causalmente, con información disponible en cada instante, tanto el despertar como la terminación del frontside?
```

## PROCESO PARTICULAR `wake-up`

### FENÓMENO `wake-up` 

* [01_WAKE_UP_EVENT_DEFINITION](../WAKE_UP/01_DEFINITION/01_WAKE_UP_EVENT_DEFINITION.md)

```
FENÓMENO OBSERVABLE:  

Un instrumento abandona un régimen  
dormido o de baja actividad  
y entra en un régimen  
de activación materialmente anómala.  

    FAMILIA DE FENÓMENOS OBSERVABLES:
    Dormancy
    → activación anómala
```

### PREGUNTA CIENTÍFICA

```
PREGUNTA CIENTÍFICA:
¿Podemos detectar y representar causalmente el Wake-up de un tiker, con información disponible en cada instante y con una tasa controlada de falsas activaciones, antes de pasar por el filtro del scanner Vol. > 500k?

MOTIVACIÓN POSTERIOR:
Usar el Wake-up para iniciar el Episode Instance y representar después toda la evolución del frontside hasta su terminación.
```
### NECESIDAD DE INFORMACIÓN:
```
NECESIDAD DE INFORMACIÓN:
qué necesitamos conocer del mercado para responder la pregunta científica

    1. Conocer el régimen previo.
        ¿El instrumento estaba dormido
        o dentro de su actividad contextual esperable?

    2. Conocer la transición de actividad.
        ¿Ha aparecido una sorpresa material
        respecto al baseline PIT?

    3. Conocer la materialidad absoluta.
        ¿La actividad supera un suelo de minimis
        o el cambio es económicamente microscópico?

    4. Conocer si la evidencia es real y corroborada.
        ¿Procede de múltiples eventos válidos
        o de un print, corrección, desorden o anomalía?

    5. Conocer la respuesta contemporánea del mercado.
        ¿Trades, quotes, bid/ask, midprice o precio elegible
        corroboran la activación?
        ¿Debe esta respuesta ser obligatoria
        o sólo evidencia adicional?

    6. Conocer la dirección inicial.
        ¿La activación es up, down, mixed o indeterminate?
        La dirección se conserva como atributo,
        no como definición universal de Wake-up.

    7. Conocer la temporalidad causal.
        ¿Cuándo comenzó aparentemente la activación?
        ¿Cuándo pudo detectarse?
        ¿Cuándo quedó legalmente disponible?

    8. Conocer la calidad y cobertura.
        ¿Los trades y quotes poseen timestamps,
        secuencias, condiciones y cobertura suficientes?

    9. Conocer el denominador de exposición.
        ¿Cuántos symbol-seconds elegibles fueron observados
        y cuántas falsas activaciones produjo el detector?

    10. Conocer la relación con el scanner existente.
        ¿Cuánto antes o después se detecta Wake-up
        respecto al scanner de 500.000 acciones?

```
### OBJETOS DE INFORMACIÓN

```
OBJETO DE INFORMACIÓN:
¿Qué significado estable necesitamos conservar
sobre el mercado para estudiar el FENÓMENO OBSERVABLE?


                        PERFIL CANDIDATO DE OBJETOS

Estos recuadros no redefinen la semántica completa de cada Information Object.
Definen qué significado necesita consumir el perfil Wake-up de cada objeto.
La inclusión de un objeto en el perfil no implica que sea una condición
obligatoria para emitir Wake-up.

PROFILE MEMBERSHIP ≠ MANDATORY DETECTOR PREDICATE

Esto evita que Price Movement o Liquidity queden prematuramente convertidos en requisitos del detector.

┌──────────────────────────────────────────────────────────────────────────────┐
│ 1. TRADING ACTIVITY                                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ PREGUNTA SEMÁNTICA                                                           │
│ ──────────────────                                                           │
│ ¿Cómo cambia la participación transaccional respecto al régimen previo       │
│ del instrumento y a su baseline contextual PIT?                              │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • Intensidad de actividad                                                    │
│ • Ritmo de negociación                                                       │
│ • Concentración temporal de la actividad                                     │
│ • Actividad relativa al baseline PIT                                         │
│ • Materialidad absoluta de la activación                                     │
│ • Evolución de la participación                                              │
│                                                                              │
│ RESPONDE PRINCIPALMENTE A LAS NECESIDADES                                    │
│ ────────────────────────────────────────                                     │
│ 1. Régimen previo                                                            │
│ 2. Transición de actividad                                                   │
│ 3. Materialidad absoluta                                                     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 2. MARKET MICROSTRUCTURE STATE                                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ PREGUNTA SEMÁNTICA                                                           │
│ ──────────────────                                                           │
│ ¿Cómo se organizan e interactúan los eventos de trades y quotes durante      │
│ la transición desde el régimen dormido?                                      │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • Estructura multievento de la activación                                    │
│ • Secuenciación temporal de los mensajes                                     │
│ • Colapso del tiempo entre eventos                                           │
│ • Concentración o dispersión de prints                                       │
│ • Interacción contemporánea entre trades y quotes                            │
│ • Respuesta de bid, ask y midprice                                           │
│ • Continuidad o fragmentación de la actividad                                │
│                                                                              │
│ RESPONDE PRINCIPALMENTE A LAS NECESIDADES                                    │
│ ────────────────────────────────────────                                     │
│ 4. Evidencia real y corroborada                                              │
│ 5. Respuesta contemporánea del mercado                                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 3. PRICE MOVEMENT                                                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ PREGUNTA SEMÁNTICA                                                           │
│ ──────────────────                                                           │
│ ¿Existe desplazamiento observable del precio y cuáles son su dirección,      │
│ magnitud, velocidad y eficiencia?                                            │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • Dirección inicial del desplazamiento                                       │
│ • Magnitud del movimiento                                                    │
│ • Velocidad y aceleración                                                    │
│ • Respuesta del precio, midprice, bid y ask                                  │
│ • Eficiencia entre actividad y desplazamiento                                │
│ • Continuidad, reversión o agotamiento inicial                               │
│                                                                              │
│ RESPONDE PRINCIPALMENTE A LAS NECESIDADES                                    │
│ ────────────────────────────────────────                                     │
│ 5. Respuesta contemporánea del mercado                                       │
│ 6. Dirección inicial                                                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 4. LIQUIDITY                                                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ PREGUNTA SEMÁNTICA                                                           │
│ ──────────────────                                                           │
│ ¿Qué condiciones de liquidez observables acompañan a la activación y cómo    │
│ cambian durante la transición?                                               │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • Disponibilidad de quotes                                                   │
│ • Frescura de las cotizaciones                                               │
│ • Spread observable                                                          │
│ • Profundidad mostrada                                                       │
│ • Continuidad del mercado bilateral                                          │
│ • Deterioro, recuperación o mejora de la liquidez                            │
│ • Asimetría observable entre bid y ask                                       │
│                                                                              │
│ NO DEBE CONTENER EN ESTE PERFIL  CANDIDATO                                   │
│ ───────────────────────────────────────                                      │
│ • target_order_size                                                          │
│ • Coste esperado de nuestra orden                                            │
│ • Impacto estimado para nuestro tamaño                                       │
│ • Decisión final de Tradability                                              │
│                                                                              │
│ RESPONDE PRINCIPALMENTE A LAS NECESIDADES                                    │
│ ────────────────────────────────────────                                     │
│ 4. Evidencia real y corroborada                                              │
│ 5. Respuesta contemporánea del mercado                                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘


╔══════════════════════════════════════════════════════════════════════════════╗
║                    OBJETOS DE CONTEXTO DEL PERFIL                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│ 5. VOLATILITY / RANGE STATE                                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ PREGUNTA SEMÁNTICA                                                           │
│ ──────────────────                                                           │
│ ¿Cómo cambia la magnitud, variabilidad e inestabilidad del movimiento        │
│ respecto al régimen previo del instrumento?                                  │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • Magnitud del rango observado                                               │
│ • Variabilidad reciente del precio                                           │
│ • Expansión o contracción respecto al baseline PIT                           │
│ • Velocidad de expansión del rango                                           │
│ • Estabilidad o inestabilidad del movimiento                                 │
│ • Diferencia respecto al régimen dormido                                     │
│                                                                              │
│ RESPONDE PRINCIPALMENTE A LAS NECESIDADES                                    │
│ ────────────────────────────────────────                                     │
│ 1. Régimen previo                                                            │
│ 5. Respuesta contemporánea del mercado                                       │
│                                                                              │
│ No demuestra por sí solo una transición de actividad.                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 6. PRICE LOCATION / STRUCTURE                                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ PREGUNTA SEMÁNTICA                                                           │
│ ──────────────────                                                           │
│ ¿Dónde se encuentra el precio respecto a las referencias estructurales       │
│ que eran observables en ese instante?                                        │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • Posición respecto al prior close                                           │
│ • Posición respecto a la apertura de sesión                                  │
│ • Posición dentro del rango observable                                       │
│ • Distancia a máximos y mínimos conocidos                                    │
│ • Posición respecto a referencias intradía disponibles                       │
│ • Cambio de localización durante la activación                               │
│                                                                              │
│ RESPONDE PRINCIPALMENTE A LAS NECESIDADES                                    │
│ ────────────────────────────────────────                                     │
│ 5. Respuesta contemporánea del mercado                                       │
│ 6. Dirección inicial, como contexto estructural                              │
│                                                                              │
│ Contextualiza la dirección, pero no la determina por sí solo.                │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘


╔══════════════════════════════════════════════════════════════════════════════╗
║                    COMPOSICIÓN ARQUITECTÓNICA                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│ CORE-FOUR EXISTENTE                                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ FUNCIÓN EN EL PERFIL                                                         │
│ ───────────────────                                                          │
│ Aporta una representación reutilizable de actividad, movimiento, posición    │
│ estructural y régimen de rango.                                              │
│                                                                              │
│ OBJETOS INCLUIDOS                                                            │
│ ─────────────────                                                            │
│ • Trading Activity                                                           │
│ • Price Movement                                                             │
│ • Price Location / Structure                                                 │
│ • Volatility / Range State                                                   │
│                                                                              │
│ LÍMITE PARA WAKE-UP                                                          │
│ ───────────────────                                                          │
│ No representa completamente la interacción trade/quote ni las condiciones    │
│ observables de liquidez necesarias para estudiar la activación temprana.     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ EXTENSIÓN CANDIDATA PARA WAKE-UP                                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ FUNCIÓN EN EL PERFIL                                                         │
│ ───────────────────                                                          │
│ Completar la representación de la activación temprana con evidencia          │
│ microestructural y condiciones contemporáneas de liquidez.                   │
│                                                                              │
│ OBJETOS AÑADIDOS                                                             │
│ ────────────────                                                             │
│ • Market Microstructure State                                                │
│ • Liquidity                                                                  │
│                                                                              │
│ JUSTIFICACIÓN                                                                │
│ ─────────────                                                                │
│ Permiten distinguir una activación multievento corroborada de un print       │
│ aislado y observar si trades y quotes responden de forma coherente.          │
│                                                                              │
│ ESTADO                                                                       │
│ ──────                                                                       │
│ Inclusión candidata. Sus modelos, variables y bindings físicos todavía       │
│ deben definirse y validarse mediante el experimento.                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘


╔══════════════════════════════════════════════════════════════════════════════╗
║                    OBJETOS OPCIONALES O CONDICIONADOS                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│ FUNDAMENTAL CONTEXT                                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ PREGUNTA SEMÁNTICA                                                           │
│ ──────────────────                                                           │
│ ¿Qué características fundamentales del instrumento eran conocidas y          │
│ legalmente disponibles en el instante t?                                     │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • Identidad y tipo del instrumento                                           │
│ • Estado de listado y elegibilidad                                           │
│ • Shares outstanding conocidas as-of                                         │
│ • Market capitalization calculable as-of                                     │
│ • Vigencia y procedencia de cada observación                                 │
│                                                                              │
│ FUNCIÓN PRINCIPAL                                                            │
│ ─────────────────                                                            │
│ Resolver la elegibilidad PIT y permitir estratificación científica.          │           
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ NEWS / CATALYST CONTEXT                                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ PREGUNTA SEMÁNTICA                                                           │
│ ──────────────────                                                           │
│ ¿Existía un catalizador informativo publicado y disponible cuando comenzó    │
│ la activación?                                                               │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • Existencia o ausencia observable de noticias                               │
│ • Tipo y categoría del catalizador                                           │
│ • published_at y available_at                                                │
│ • Fuente, identidad y versión de la noticia                                  │
│ • Relación causalmente admisible con el instrumento                          │
│ • Antigüedad del catalizador en el instante t                                │
│                                                                              │
│ FUNCIÓN EN EL PERFIL                                                         │
│ ───────────────────                                                          │
│ Aportar contexto y permitir segmentar activaciones con y sin catalizador.    │
│                                                                              │
│ ESTADO                                                                       │
│ ──────                                                                       │
│ Contexto opcional. Wake-up puede existir sin una noticia conocida.           │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ HALT CONTEXT                                                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ PREGUNTA SEMÁNTICA                                                           │
│ ──────────────────                                                           │
│ ¿La observación del instrumento está condicionada por un halt, una           │
│ reanudación o una interrupción de continuidad?                               │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • Estado observable del halt                                                 │
│ • Inicio, anuncio y disponibilidad del evento                                │
│ • Momento y condiciones de reanudación                                       │
│ • Duración de la interrupción                                                │
│ • Cambios de continuidad antes y después del halt                            │
│ • Cobertura de la fuente de halts                                            │
│                                                                              │
│ FUNCIÓN EN EL PERFIL                                                         │
│ ───────────────────                                                          │
│ Evitar interpretar una discontinuidad institucional como actividad normal    │
│ y conservar el contexto causal del episodio.                                 │
│                                                                              │
│ ESTADO                                                                       │
│ ──────                                                                       │
│ Condicionado. Es obligatorio cuando un halt o resumption afecta la ventana   │
│ observada.                                                                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ ORDER FLOW PRESSURE                                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ PREGUNTA SEMÁNTICA                                                           │
│ ──────────────────                                                           │
│ ¿Qué presión direccional observable ejerce el flujo y con qué eficiencia     │
│ se convierte en desplazamiento del precio?                                   │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • Balance entre flujo comprador y vendedor clasificado                       │
│ • Intensidad y persistencia de la presión                                    │
│ • Alineación temporal entre trades y quotes                                  │
│ • Conversión del flujo en desplazamiento                                     │
│ • Divergencia entre esfuerzo y progreso                                      │
│ • Confianza y cobertura de la clasificación                                  │
│                                                                              │
│ RESPONDE PRINCIPALMENTE A LAS NECESIDADES                                    │
│ ────────────────────────────────────────                                     │
│ 5. Respuesta contemporánea del mercado                                       │
│ 6. Dirección inicial                                                         │
│                                                                              │
│ ESTADO                                                                       │
│ ──────                                                                       │
│ Extensión condicionada a una clasificación de trades, alineación             │
│ trade/quote y confianza suficientemente validadas.                           │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘


╔══════════════════════════════════════════════════════════════════════════════╗
║                  ELEMENTOS QUE NO SON INFORMATION OBJECTS                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│ TEMPORALIDAD CAUSAL                                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ PREGUNTA DE CONTROL                                                          │
│ ───────────────────                                                          │
│ ¿Qué información era legalmente observable y consumible en cada instante?    │
│                                                                              │
│ DEBE DEFINIR Y CONSERVAR                                                     │
│ ───────────────────────                                                      │
│ • event_time, observed_at y available_at                                     │
│ • Orden y secuencia causal de los mensajes                                   │
│ • Latencias de publicación y procesamiento                                   │
│ • Inputs máximos utilizados por cada representación                          │
│ • Prohibición de información futura                                          │
│                                                                              │
│ CLASIFICACIÓN ARQUITECTÓNICA                                                 │
│ ───────────────────────────                                                  │
│ Temporal Policy / Availability Contract / Lineage Metadata.                  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ CALIDAD Y COBERTURA                                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ PREGUNTA DE CONTROL                                                          │
│ ───────────────────                                                          │
│ ¿Son suficientes y fiables los datos utilizados para representar y detectar  │
│ la transición?                                                               │
│                                                                              │
│ DEBE DEFINIR Y CONSERVAR                                                     │
│ ───────────────────────                                                      │
│ • Cobertura temporal de trades y quotes                                      │
│ • Timestamps, secuencias y condiciones                                       │
│ • Cancelaciones, correcciones y mensajes fuera de orden                      │
│ • Quotes stale, gaps y periodos no observables                               │
│ • Reglas de rechazo, degradación y unavailable                               │
│                                                                              │
│ CLASIFICACIÓN ARQUITECTÓNICA                                                 │
│ ───────────────────────────                                                  │
│ Data Quality Contract / Coverage Evidence.                                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ DENOMINADOR Y FALSAS ALERTAS                                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ PREGUNTA DE CONTROL                                                          │
│ ───────────────────                                                          │
│ ¿Sobre cuánta exposición elegible se evalúa el detector y cuántas            │
│ activaciones incorrectas produce?                                            │
│                                                                              │
│ DEBE DEFINIR Y CONSERVAR                                                     │
│ ───────────────────────                                                      │
│ • Universo PIT elegible                                                      │
│ • Unidad experimental                                                        │
│ • Symbol-time total observado                                                │
│ • Periodos normales y activaciones negativas                                 │
│ • False-positive rate y carga de alertas                                     │
│ • Tratamiento del desbalance de clases                                       │
│                                                                              │
│ CLASIFICACIÓN ARQUITECTÓNICA                                                 │
│ ───────────────────────────                                                  │
│ Detector Experiment Contract / Evaluation Protocol.                          │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ COMPARACIÓN CON SCANNER DE 500K                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ PREGUNTA DE CONTROL                                                          │
│ ───────────────────                                                          │
│ ¿Cuánto antes, después o con qué diferencias detecta Wake-up la activación   │
│ respecto al scanner basado en volumen acumulado?                             │
│                                                                              │
│ DEBE DEFINIR Y CONSERVAR                                                     │
│ ───────────────────────                                                      │
│ • Timestamp de Wake-up                                                       │
│ • Timestamp de aparición en el scanner                                       │
│ • Diferencia temporal entre ambos                                            │
│ • Casos detectados solamente por uno de los sistemas                         │
│ • Activaciones fallidas y alertas tardías                                    │
│ • Cobertura y reglas exactas del scanner                                     │
│                                                                              │
│ CLASIFICACIÓN ARQUITECTÓNICA                                                 │
│ ───────────────────────────                                                  │
│ Benchmark / Evaluation Contract.                                             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ WATCH                                                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ SIGNIFICADO                                                                  │
│ ───────────                                                                  │
│ El instrumento merece observación reforzada porque se ha detectado una       │
│ transición compatible con Wake-up.                                           │
│                                                                              │
│ NO SIGNIFICA                                                                 │
│ ───────────                                                                  │
│ • In-Play confirmado                                                         │
│ • Frontside confirmado                                                       │
│ • Tradability                                                                │
│ • Entry Eligibility                                                          │
│ • Orden o fill                                                               │
│                                                                              │
│ CLASIFICACIÓN ARQUITECTÓNICA                                                 │
│ ───────────────────────────                                                  │
│ Salida del detector y comando de atención. No es un Information Object.      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ EPISODE INSTANCE                                                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ PREGUNTA DE SEGUIMIENTO                                                      │
│ ───────────────────────                                                      │
│ ¿Cómo evoluciona el episodio de activación iniciado por Wake-up?             │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • Identidad estable del episodio                                             │
│ • Evento que lo inició                                                       │
│ • Inicio, detección y disponibilidad                                         │
│ • Fase y estado actual                                                       │
│ • Bursts, pullbacks, halts y reactivaciones                                  │
│ • Expiración, cierre y desenlace posterior                                   │
│                                                                              │
│ CLASIFICACIÓN ARQUITECTÓNICA                                                 │
│ ───────────────────────────                                                  │
│ Entidad mutable de seguimiento. No es un Information Object ni un Event      │
│ Type.                                                                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ WAKE-UP                                                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ SIGNIFICADO CANDIDATO                                                        │
│ ─────────────────────                                                        │
│ Transición causalmente detectable desde un régimen dormido contextual hacia  │
│ una activación materialmente anómala y suficientemente corroborada.          │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • Identidad del evento y del instrumento                                     │
│ • Episode Instance iniciado                                                  │
│ • detected_at y available_at                                                 │
│ • Dirección inicial observada                                                │
│ • Versión del detector                                                       │
│ • Evidencia y referencias de procedencia                                     │
│                                                                              │
│ NO AFIRMA                                                                    │
│ ─────────                                                                    │
│ • In-Play, Frontside o continuación                                          │
│ • Tradability o Entry Eligibility                                            │
│ • Orden, fill o edge económico                                               │
│                                                                              │
│ CLASIFICACIÓN ARQUITECTÓNICA                                                 │
│ ───────────────────────────                                                  │
│ Event Type candidato. No es un fenómeno, un Information Object ni una señal  │
│ de compra.                                                                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘


Mapeo Final
------------

Necesidad                    Information Object o contrato
━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Elegibilidad PIT             Universe Resolver + Fundamental Context as-of
───────────────────────────  ────────────────────────────────────────────────────────
Régimen previo               Trading Activity + Market Microstructure State
                          Volatility / Range State
                          Liquidity como contexto
───────────────────────────  ────────────────────────────────────────────────────────
Transición anómala           Trading Activity
                          Market Microstructure State como corroboración
───────────────────────────  ────────────────────────────────────────────────────────
Materialidad absoluta        Trading Activity
───────────────────────────  ────────────────────────────────────────────────────────
Evidencia multievento        Market Microstructure State
                          Data Quality Contract como gate de validez
───────────────────────────  ────────────────────────────────────────────────────────
Respuesta contemporánea      Price Movement + Liquidity
                          Market Microstructure State
───────────────────────────  ────────────────────────────────────────────────────────
Dirección inicial            Price Movement
                          Order Flow Pressure como extensión diferida
───────────────────────────  ────────────────────────────────────────────────────────
Interpretación estructural   Price Location / Structure
───────────────────────────  ────────────────────────────────────────────────────────
Catalizador observable       News / Catalyst Context, opcional
───────────────────────────  ────────────────────────────────────────────────────────
Interrupción de continuidad  Halt Context, condicionado
───────────────────────────  ────────────────────────────────────────────────────────
Temporalidad causal          Temporal Policy / Availability Contract,
                            no Information Object
───────────────────────────  ────────────────────────────────────────────────────────
Calidad y cobertura          Data Quality Contract / Coverage Evidence,
                            no Information Object
───────────────────────────  ────────────────────────────────────────────────────────
Denominador                  Detector Experiment Contract,
                            no Information Object
───────────────────────────  ────────────────────────────────────────────────────────
Comparación con scanner      Benchmark / Evaluation Contract,
                            no Information Object
───────────────────────────  ────────────────────────────────────────────────────────


Por tanto, el perfil inicial candidato sería:
WAKE_UP_INFORMATION_OBJECT_PROFILE_CANDIDATE_V0_1
-------------------------------------------------

CORE REPRESENTATION:
- Trading Activity
- Price Movement
- Liquidity
- Market Microstructure State

SUPPORTING CONTEXT:
- Volatility / Range State
- Price Location / Structure

CONDITIONAL CONTEXT:
- Fundamental Context
- News / Catalyst Context
- Halt Context

DEFERRED EXTENSION:
- Order Flow Pressure
```

### MODELO DE REPRESENTACIÓN

ref. [REPRESENTATION_MODELS.md](/00_CTO/04_MARKET_STATES_CREATION/REPRESENTATION_MODELS.md)  
ref. [00_TABLES_MARKET_STATE_EVENT_STATE](/00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/00_TABLES_MARKET_STATE_EVENT_STATE.md)
```
MODELO DE REPRESENTACIÓN:  

Un modelo de representación conceptualiza la representación del OBJETO DE INFORMACION.  
Responde a ¿qué dimensiones observables consideramos necesarias para   
representar los OBJETOS DE INFORMMACION propuestos?

Si mañana descubres una forma mejor de medir la liquidez, cambias el modelo o su implementación, pero no cambias el OBJETO "Liquidity". 

╔══════════════════════════════════════════════════════════════════════════════╗
║                    CORE REPRESENTATION MODELS                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
┌──────────────────────────────────────────────────────────────────────────────┐
│ TRADING ACTIVITY                                                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ REPRESENTATION MODEL CANDIDATE                                               │
│ ──────────────────────────────                                               │
│ PIT-NORMALIZED MULTISCALE MARKED ACTIVITY PROCESS                            │
│                                                                              │
│ QUÉ CONCEPTUALIZA                                                            │
│ ─────────────────                                                            │
│ La actividad como un proceso irregular de eventos cuyos tiempos de llegada,  │
│ tamaños, valores nocionales y concentraciones se comparan causalmente con    │
│ el régimen PIT esperado del instrumento.                                     │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│                                                                              │
│ ABSOLUTE ACTIVITY                                                            │
│ • Número de trades                                                           │
│ • Número de acciones                                                         │
│ • Dollar volume                                                              │
│ • Presencia, ausencia o imposibilidad de observar actividad                  │
│                                                                              │
│ EVENT INTENSITY                                                              │
│ • Ritmo de llegada de trades                                                 │
│ • Duraciones entre trades                                                    │
│ • Compresión o expansión del tiempo entre eventos                            │
│                                                                              │
│ ACTIVITY MARKS                                                               │
│ • Distribución de tamaños                                                    │
│ • Distribución de valores nocionales                                         │
│ • Concentración en prints pequeños o grandes                                 │
│                                                                              │
│ TEMPORAL CONCENTRATION                                                       │
│ • Actividad dispersa o agrupada                                              │
│ • Bursts y subventanas de concentración                                      │
│ • Participación concentrada en intervalos breves                             │
│                                                                              │
│ RELATIVE SURPRISE                                                            │
│ • Desviación respecto al baseline PIT                                        │
│ • Desviación respecto a sesión y franja horaria                              │
│ • Desviación respecto al régimen reciente                                    │
│                                                                              │
│ BURST DYNAMICS                                                               │
│ • Continuidad mínima antinartefacto                                          │
│ • Duración observable del burst                                              │
│ • Decaimiento                                                                │
│ • Reactivación                                                               │
│                                                                              │
│ REGLAS CAUSALES                                                              │
│ ───────────────                                                              │
│ • El baseline sólo puede utilizar información disponible antes de t.         │
│ • Premarket, regular session y after-hours requieren baselines separados.    │
│ • Ausencia de datos no equivale a actividad igual a cero.                    │
│ • La persistencia económica posterior pertenece a In-Play.                   │
│                                                                              │
│ IMPLEMENTACIONES CANDIDATAS                                                  │
│ ───────────────────────────                                                  │
│ • Agregaciones multiescala de counts y volumen                               │
│ • Estimadores de duración e intensidad                                       │
│ • Procesos puntuales autoexcitados                                           │
│                                                                              │
│ NO DEBE CONGELAR COMO IDENTIDAD                                              │
│ ──────────────────────────────                                               │
│ • ACD                                                                        │
│ • Hawkes                                                                     │
│ • CUSUM                                                                      │
│ • BOCPD                                                                      │
│                                                                              │
│ Estos son posibles estimadores o detectores, no el significado estable del   │
│ modelo de representación.                                                    │
│                                                                              │
│ RECHAZAR COMO MODELO SUFICIENTE                                              │
│ ───────────────────────────────                                              │
│ • Volumen acumulado bruto                                                    │
│ • RVOL de una sola ventana                                                   │
│ • Trade count aislado                                                        │
│ • Un único z-score de ventana fija                                           │
│ • Umbral de 500.000 acciones                                                 │
│                                                                              │
│ BASE CIENTÍFICA PRINCIPAL                                                    │
│ ─────────────────────────                                                    │
│ Engle y Russell; Dufour y Engle; Andersen y Bollerslev.                      │
│                                                                              │
│ VEREDICTO PROVISIONAL                                                        │
│ ─────────────────────                                                        │
│ RECOMMENDED REPRESENTATION MODEL CANDIDATE                                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ MARKET MICROSTRUCTURE STATE                                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ REPRESENTATION MODEL CANDIDATE                                               │
│ ──────────────────────────────                                               │
│ OBSERVED TRADE-QUOTE EVENT COUPLING STATE                                    │
│                                                                              │
│ QUÉ CONCEPTUALIZA                                                            │
│ ─────────────────                                                            │
│ Cómo se organizan y relacionan temporalmente los eventos observados de       │
│ trades, bid, ask, quote sizes y revisiones del midprice.                     │
│                                                                              │
│ No determina todavía quién compra o vende ni reconstruye eventos de órdenes  │
│ que la fuente no permite observar directamente.                              │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│                                                                              │
│ EVENT COMPOSITION                                                            │
│ • Proporción de trades y quote updates                                       │
│ • Cambios de precio frente a cambios exclusivamente de tamaño                │
│ • Tipos de eventos observables dentro de cada ventana                        │
│                                                                              │
│ OBSERVED SEQUENCING                                                          │
│ • Orden temporal observable de trades y quotes                               │
│ • Intervalos entre eventos                                                   │
│ • Secuencias y transiciones repetidas                                        │
│                                                                              │
│ TRADE-QUOTE COUPLING                                                         │
│ • Revisiones de quotes alrededor de trades                                   │
│ • Distancia temporal observable trade-quote                                  │
│ • Cambios de bid, ask y midprice asociados temporalmente                     │
│                                                                              │
│ MULTIEVENT CORROBORATION                                                     │
│ • Múltiples eventos consistentes                                             │
│ • Prints aislados                                                            │
│ • Quotes aisladas                                                            │
│ • Secuencias compatibles con una activación real                             │
│                                                                              │
│ CONTINUITY                                                                   │
│ • Flujo continuo                                                             │
│ • Bursts fragmentados                                                        │
│ • Silencios prolongados                                                      │
│ • Reanudaciones                                                              │
│                                                                              │
│ QUOTE-STATE RESPONSE                                                         │
│ • Respuesta observable del bid                                               │
│ • Respuesta observable del ask                                               │
│ • Respuesta observable del midprice                                          │
│ • Estados one-sided, locked, crossed o stale cuando sean observables         │
│                                                                              │
│ REGLA DE INTERPRETACIÓN                                                      │
│ ───────────────────────                                                      │
│ Secuencia temporal observable no implica causalidad económica demostrada.    │
│ Una revisión posterior a un trade no prueba que ese trade la causara.        │
│                                                                              │
│ LIMITACIÓN DE FUENTE                                                         │
│ ────────────────────                                                         │
│ Observed quote update no demuestra por sí solo:                              │
│                                                                              │
│ • Nueva limit order                                                          │
│ • Cancelación                                                                │
│ • Orden oculta                                                               │
│ • Depleción del libro completo                                               │
│ • Estado de una cola individual                                              │
│                                                                              │
│ IMPLEMENTACIONES CANDIDATAS                                                  │
│ ───────────────────────────                                                  │
│ • Matrices de transición de eventos observados                               │
│ • Distribuciones de lags trade-quote                                         │
│ • Estadísticas multiescala de acoplamiento                                   │
│ • Procesos puntuales multivariantes                                          │
│                                                                              │
│ FRONTERA CON OTROS OBJETOS                                                   │
│ ──────────────────────────                                                   │
│ Trading Activity = cuánto y con qué rapidez ocurre actividad.                │
│ Microstructure = cómo se organizan e interactúan los eventos.                │
│ Liquidity = qué condiciones observables ofrece el mercado.                   │
│ Order Flow = qué presión direccional se infiere del flujo.                   │
│                                                                              │
│ RECHAZAR COMO MODELO SUFICIENTE                                              │
│ ───────────────────────────────                                              │
│ • Microestructura basada sólo en OHLCV                                       │
│ • Resúmenes independientes de trades y quotes                                │
│ • Snapshot estático de quotes                                                │
│ • Full order-book no respaldado por la fuente                                │
│                                                                              │
│ BASE CIENTÍFICA PRINCIPAL                                                    │
│ ─────────────────────────                                                    │
│ Hasbrouck; Cont, Kukanov y Stoikov; Bacry y Muzy.                            │
│                                                                              │
│ VEREDICTO PROVISIONAL                                                        │
│ ─────────────────────                                                        │
│ RECOMMENDED REPRESENTATION MODEL CANDIDATE                                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ PRICE MOVEMENT                                                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ REPRESENTATION MODEL CANDIDATE                                               │
│ ──────────────────────────────                                               │
│ SIGNED MULTISCALE CAUSAL PRICE-PATH RESPONSE                                 │
│                                                                              │
│ QUÉ CONCEPTUALIZA                                                            │
│ ─────────────────                                                            │
│ El movimiento como una trayectoria firmada y multiescala, no como un único   │
│ retorno ni como una etiqueta gráfica.                                        │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│                                                                              │
│ DIRECTION                                                                    │
│ • Up                                                                         │
│ • Down                                                                       │
│ • Mixed                                                                      │
│ • Indeterminate                                                              │
│                                                                              │
│ DISPLACEMENT                                                                 │
│ • Desplazamiento neto                                                        │
│ • Recorrido total                                                            │
│ • Desplazamiento desde referencias causalmente disponibles                   │
│ • Desplazamiento desde un onset estimado disponible en t                     │
│                                                                              │
│ VELOCITY                                                                     │
│ • Cambio por unidad de tiempo calendario                                     │
│ • Cambio por evento                                                          │
│ • Aceleración y desaceleración                                               │
│                                                                              │
│ PATH EFFICIENCY                                                              │
│ • Relación entre desplazamiento neto y recorrido total                       │
│ • Movimiento directo frente a trayectoria errática                           │
│ • Progreso producido por unidad de actividad                                 │
│                                                                              │
│ PRICE-SOURCE AGREEMENT                                                       │
│ • Last trade                                                                 │
│ • Eligible trade price                                                       │
│ • Midprice                                                                   │
│ • Bid                                                                        │
│ • Ask                                                                        │
│ • Desacuerdo entre fuentes de precio                                         │
│                                                                              │
│ PATH DYNAMICS                                                                │
│ • Continuidad                                                                │
│ • Estancamiento                                                              │
│ • Reversión                                                                  │
│ • Agotamiento inicial                                                        │
│                                                                              │
│ MULTISCALE STRUCTURE                                                         │
│ • Respuesta inmediata                                                        │
│ • Respuesta breve                                                            │
│ • Respuesta acumulada                                                        │
│                                                                              │
│ REGLAS CAUSALES                                                              │
│ ───────────────                                                              │
│ • Toda referencia debe existir y estar disponible en t.                      │
│ • Un onset estimado anterior no puede consumirse antes de su available_at.   │
│ • El movimiento no debe depender de máximos o mínimos finales futuros.       │
│ • Debe conservarse el desacuerdo entre trade price y midquote.               │
│                                                                              │
│ FRONTERA CON VOLATILITY                                                      │
│ ───────────────────────                                                      │
│ Price Movement representa dirección, trayectoria y progreso.                 │
│ Volatility representa magnitud e inestabilidad no firmadas.                  │
│                                                                              │
│ RECHAZAR COMO MODELO SUFICIENTE                                              │
│ ───────────────────────────────                                              │
│ • Retorno único                                                              │
│ • Last-trade-only movement                                                   │
│ • RSI o MACD                                                                 │
│ • Slope aislada                                                              │
│ • Chart-pattern label                                                        │
│ • PMH-break flag                                                             │
│                                                                              │
│ PMH breakout combina Price Movement, Price Location y una regla de evento.   │
│ No es una representación general de Price Movement.                          │
│                                                                              │
│ BASE CIENTÍFICA PRINCIPAL                                                    │
│ ─────────────────────────                                                    │
│ Aït-Sahalia, Mykland y Zhang; Russell y Engle.                               │
│                                                                              │
│ VEREDICTO PROVISIONAL                                                        │
│ ─────────────────────                                                        │
│ RECOMMENDED REPRESENTATION MODEL CANDIDATE                                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ LIQUIDITY                                                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ REPRESENTATION MODEL CANDIDATE                                               │
│ ──────────────────────────────                                               │
│ OBSERVABLE TOP-OF-BOOK LIQUIDITY CONDITION                                   │
│ AND RESILIENCE STATE                                                         │
│                                                                              │
│ QUÉ CONCEPTUALIZA                                                            │
│ ─────────────────                                                            │
│ Las condiciones de liquidez observables durante la activación, sin           │
│ condicionar todavía la representación al tamaño de nuestra orden.            │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│                                                                              │
│ AVAILABILITY                                                                 │
│ • Existencia de bid                                                          │
│ • Existencia de ask                                                          │
│ • Mercado bilateral                                                          │
│ • Mercado one-sided                                                          │
│ • Ausencia temporal o desconocimiento de quotes                              │
│                                                                              │
│ FRESHNESS                                                                    │
│ • Edad observable del bid                                                    │
│ • Edad observable del ask                                                    │
│ • Quotes stale                                                               │
│ • Continuidad de actualización                                               │
│                                                                              │
│ TIGHTNESS                                                                    │
│ • Spread absoluto                                                            │
│ • Spread relativo                                                            │
│ • Spread expresado en ticks                                                  │
│                                                                              │
│ DISPLAYED TOP-OF-BOOK DEPTH                                                  │
│ • Tamaño mostrado en bid                                                     │
│ • Tamaño mostrado en ask                                                     │
│ • Profundidad expresada en acciones                                          │
│ • Profundidad expresada en valor nocional                                    │
│                                                                              │
│ ASYMMETRY                                                                    │
│ • Diferencia entre bid y ask                                                 │
│ • Concentración unilateral                                                   │
│ • Cambio observable de asimetría                                             │
│                                                                              │
│ OBSERVED RESILIENCE                                                          │
│ • Recuperación observable de profundidad                                     │
│ • Cierre del spread después de abrirse                                       │
│ • Reposición aparente del top-of-book                                        │
│ • Persistencia del deterioro                                                 │
│                                                                              │
│ CONTINUITY                                                                   │
│ • Estabilidad del mercado bilateral                                          │
│ • Alternancia entre mercado y no-mercado                                     │
│ • Fragmentación temporal                                                     │
│                                                                              │
│ NORMALIZACIÓN NECESARIA                                                      │
│ ───────────────────────                                                      │
│ Debe conservar valores absolutos y valores normalizados por:                 │
│                                                                              │
│ • Precio                                                                     │
│ • Tick size                                                                  │
│ • Escala del instrumento                                                     │
│ • Sesión y franja horaria                                                    │
│ • Baseline PIT                                                               │
│                                                                              │
│ LIMITACIÓN DE INTERPRETACIÓN                                                 │
│ ───────────────────────────                                                  │
│ El tamaño mostrado en NBBO no representa el libro completo, liquidez oculta  │
│ ni capacidad ejecutable garantizada. Reposición observable no prueba que se  │
│ haya reconstruido la cola real.                                              │
│                                                                              │
│ NO DEBE CONTENER EN ESTE PERFIL                                              │
│ ───────────────────────────────                                              │
│ • Expected cost for our order                                                │
│ • Impact for target order size                                               │
│ • Fill probability for our order                                             │
│ • Tradability decision                                                       │
│ • Entry Eligibility                                                          │
│                                                                              │
│ RECHAZAR COMO MODELO SUFICIENTE                                              │
│ ───────────────────────────────                                              │
│ • Volume-as-liquidity                                                        │
│ • Order-size-conditioned liquidity                                           │
│ • Execution-cost model                                                       │
│ • Snapshot sin frescura ni continuidad                                       │
│ • Full-book liquidity sin full-book data                                     │
│                                                                              │
│ Amihud, Roll y Kyle lambda pueden ser proxies o extensiones históricas, pero │
│ no sustituyen el estado observable L1 para una transición de segundos.       │
│                                                                              │
│ BASE CIENTÍFICA PRINCIPAL                                                    │
│ ─────────────────────────                                                    │
│ Kyle; McInish y Wood; Cont, Kukanov y Stoikov.                               │
│                                                                              │
│ VEREDICTO PROVISIONAL                                                        │
│ ─────────────────────                                                        │
│ RECOMMENDED REPRESENTATION MODEL CANDIDATE                                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘


╔══════════════════════════════════════════════════════════════════════════════╗
║               SUPPORTING CONTEXT REPRESENTATION MODELS                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
┌──────────────────────────────────────────────────────────────────────────────┐
│ VOLATILITY / RANGE STATE                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ REPRESENTATION MODEL CANDIDATE                                               │
│ ──────────────────────────────                                               │
│ PIT-NORMALIZED UNSIGNED MULTISCALE VARIATION                                 │
│ AND RANGE-EXPANSION STATE                                                    │
│                                                                              │
│ QUÉ CONCEPTUALIZA                                                            │
│ ─────────────────                                                            │
│ La magnitud e inestabilidad no firmadas del movimiento y su expansión o      │
│ contracción respecto al régimen contextual anterior.                         │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • Rango observable                                                           │
│ • Variación acumulada                                                        │
│ • Expansión o contracción respecto al baseline PIT                           │
│ • Velocidad de expansión del rango                                           │
│ • Estabilidad o inestabilidad                                                │
│ • Persistencia de la expansión                                               │
│ • Discontinuidad candidata o jump-like behavior                              │
│ • Separación entre desplazamiento y oscilación                               │
│ • Diferencias entre trade-price variation y midquote variation               │
│                                                                              │
│ REGLAS CAUSALES                                                              │
│ ───────────────                                                              │
│ • Sólo puede utilizar observaciones disponibles hasta t.                     │
│ • Debe normalizarse por sesión, franja horaria e instrumento.                │
│ • Una discontinuidad observada no debe declararse jump sin validación.       │
│ • Debe controlar contaminación por bid-ask bounce y microstructure noise.    │
│                                                                              │
│ FRONTERA CON PRICE MOVEMENT                                                  │
│ ───────────────────────────                                                  │
│ Volatility / Range State no determina dirección.                             │
│ Price Movement conserva la trayectoria firmada y el progreso neto.           │
│                                                                              │
│ IMPLEMENTACIONES CANDIDATAS                                                  │
│ ───────────────────────────                                                  │
│ • Rangos causales multiescala                                                │
│ • Variación de midquote                                                      │
│ • Variación de eligible trade prices                                         │
│ • Estimadores robustos al ruido microestructural                             │
│                                                                              │
│ RECHAZAR COMO MODELO SUFICIENTE                                              │
│ ───────────────────────────────                                              │
│ • ATR de una única ventana                                                   │
│ • Rango de una sola barra                                                    │
│ • Realized volatility bruta a máxima frecuencia                              │
│ • Volatilidad sin baseline PIT                                               │
│                                                                              │
│ BASE CIENTÍFICA PRINCIPAL                                                    │
│ ─────────────────────────                                                    │
│ Andersen y Bollerslev; Aït-Sahalia, Mykland y Zhang;                         │
│ Barndorff-Nielsen y Shephard.                                                │
│                                                                              │
│ VEREDICTO PROVISIONAL                                                        │
│ ─────────────────────                                                        │
│ RECOMMENDED SUPPORTING REPRESENTATION MODEL CANDIDATE                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ PRICE LOCATION / STRUCTURE                                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ REPRESENTATION MODEL CANDIDATE                                               │
│ ──────────────────────────────                                               │
│ CAUSAL ANCHOR-RELATIVE LOCATION STATE                                        │
│                                                                              │
│ QUÉ CONCEPTUALIZA                                                            │
│ ─────────────────                                                            │
│ La posición del precio respecto a referencias estructurales que ya existían  │
│ y estaban legalmente disponibles en el instante t.                           │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • Distancia al prior close                                                   │
│ • Distancia a session open, cuando ya exista                                 │
│ • Posición dentro del rango conocido hasta t                                 │
│ • Distancia al máximo y mínimo conocidos hasta t                             │
│ • Distancia al VWAP disponible hasta t                                       │
│ • Distancia a referencias premarket disponibles                              │
│ • Cambio de localización                                                     │
│ • Edad de cada referencia                                                    │
│ • Fuente, available_at y estado de finalización de la referencia             │
│                                                                              │
│ REGLA CAUSAL ESENCIAL                                                        │
│ ──────────────────────                                                       │
│ Antes de finalizar el premarket existe:                                      │
│                                                                              │
│ running_premarket_high_as_of_t                                               │
│                                                                              │
│ No existe todavía:                                                           │
│                                                                              │
│ final_premarket_high                                                         │
│                                                                              │
│ Después de la apertura puede congelarse premarket_high_final porque ya       │
│ pertenece al pasado observable.                                              │
│                                                                              │
│ La misma regla se aplica a:                                                  │
│                                                                              │
│ • HOD                                                                        │
│ • LOD                                                                        │
│ • Session range                                                              │
│ • VWAP                                                                       │
│                                                                              │
│ Toda referencia debe ser as_of_t. Nunca debe utilizarse su valor final       │
│ retrospectivo para una decisión anterior.                                    │
│                                                                              │
│ NO DEBE REPRESENTAR                                                          │
│ ───────────────────                                                          │
│ • Flag                                                                       │
│ • Broken flag                                                                │
│ • Cup and handle                                                             │
│ • Gap and Go                                                                 │
│ • VWAP reclaim                                                               │
│ • PMH breakout                                                               │
│                                                                              │
│ Esos conceptos son patrones, Event Types o reglas de consumidores que        │
│ combinan varios Information Objects.                                         │
│                                                                              │
│ RECHAZAR COMO MODELO SUFICIENTE                                              │
│ ───────────────────────────────                                              │
│ • PMH final utilizado antes de la apertura                                   │
│ • HOD o LOD final retrospectivo                                              │
│ • Distancia a referencias sin available_at                                   │
│ • Etiqueta gráfica como representación de localización                       │
│                                                                              │
│ VEREDICTO PROVISIONAL                                                        │
│ ─────────────────────                                                        │
│ RECOMMENDED SUPPORTING REPRESENTATION MODEL CANDIDATE                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘


╔══════════════════════════════════════════════════════════════════════════════╗
║               CONDITIONAL CONTEXT REPRESENTATION MODELS                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
┌──────────────────────────────────────────────────────────────────────────────┐
│ FUNDAMENTAL CONTEXT                                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ REPRESENTATION MODEL CANDIDATE                                               │
│ ──────────────────────────────                                               │
│ PIT FUNDAMENTAL SCALE CONTEXT                                                │
│                                                                              │
│ QUÉ CONCEPTUALIZA                                                            │
│ ─────────────────                                                            │
│ La escala fundamental del instrumento conocida y legalmente disponible en    │
│ t, utilizada principalmente para elegibilidad y estratificación científica.  │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • Shares outstanding conocidas as-of                                         │
│ • Float conocido as-of, si la fuente posee suficiente autoridad              │
│ • Market capitalization calculable as-of                                     │
│ • Fecha efectiva de la observación                                           │
│ • Fecha de publicación                                                       │
│ • available_at                                                               │
│ • Fuente y versión                                                           │
│ • Edad, vigencia e incertidumbre                                             │
│ • Estado known, unknown o unavailable                                        │
│                                                                              │
│ UBICACIÓN ARQUITECTÓNICA                                                     │
│ ───────────────────────                                                      │
│ Universe Resolver utiliza Fundamental Context para evaluar reglas como:      │
│                                                                              │
│ market_cap_as_of_t < 100M                                                    │
│                                                                              │
│ Sólo debe proyectarse en Market State cuando el perfil lo requiera.          │
│                                                                              │
│ NO PERTENECE A FUNDAMENTAL CONTEXT                                           │
│ ──────────────────────────────────                                           │
│ • Identidad canónica del instrumento                                         │
│ • Security type                                                              │
│ • Listing status                                                             │
│ • Permiso de inclusión                                                       │
│                                                                              │
│ Estos elementos pertenecen a Reference / Identity / Universe Resolver.       │
│                                                                              │
│ NO DEBE AFIRMAR                                                              │
│ ───────────────                                                              │
│ • Que un dato revisado era conocido antes de su publicación                  │
│ • Que unknown equivale a cero                                                │
│ • Que float y shares outstanding son intercambiables                         │
│ • Que Fundamental Context es un predicado obligatorio de Wake-up             │
│                                                                              │
│ RECHAZAR COMO MODELO SUFICIENTE                                              │
│ ───────────────────────────────                                              │
│ • Snapshot fundamental actual aplicado retrospectivamente                    │
│ • Market cap sin shares outstanding as-of                                    │
│ • Backfill silencioso de revisiones                                          │
│ • Observación sin procedencia ni available_at                                │
│                                                                              │
│ VEREDICTO PROVISIONAL                                                        │
│ ─────────────────────                                                        │
│ RECOMMENDED CONDITIONAL REPRESENTATION MODEL CANDIDATE                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ NEWS / CATALYST CONTEXT                                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ REPRESENTATION MODEL CANDIDATE                                               │
│ ──────────────────────────────                                               │
│ AVAILABILITY-AWARE CATALYST EVENT CONTEXT                                    │
│                                                                              │
│ QUÉ CONCEPTUALIZA                                                            │
│ ─────────────────                                                            │
│ La existencia y naturaleza básica de catalizadores informativos que estaban  │
│ publicados, observados y disponibles en el instante t.                       │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • News observed: yes, no o unknown                                           │
│ • published_at                                                               │
│ • observed_at                                                                │
│ • available_at                                                               │
│ • Fuente                                                                     │
│ • Identidad y versión                                                        │
│ • Relación con el instrumento                                                │
│ • Categoría del catalizador                                                  │
│ • Antigüedad en el instante t                                                │
│ • Cobertura de la fuente                                                     │
│                                                                              │
│ DISTINCIÓN OBLIGATORIA                                                       │
│ ──────────────────────                                                       │
│ NO_NEWS_OBSERVED                                                             │
│                                                                              │
│ no equivale a:                                                               │
│                                                                              │
│ NEWS_COVERAGE_UNAVAILABLE                                                    │
│                                                                              │
│ Tampoco debe confundirse published_at con el primer instante legal de        │
│ consumo por TSIS.                                                            │
│                                                                              │
│ NO DEBE INTRODUCIR TODAVÍA                                                   │
│ ───────────────────────────                                                  │
│ • Sentiment score                                                            │
│ • Good news / bad news                                                       │
│ • LLM-derived catalyst quality                                               │
│ • Predicción de continuación                                                 │
│ • Atribución causal automática del movimiento                                │
│                                                                              │
│ Estas extensiones necesitarían contratos y validación científica propios.    │
│                                                                              │
│ RECHAZAR COMO MODELO SUFICIENTE                                              │
│ ───────────────────────────────                                              │
│ • Boolean news sin cobertura                                                 │
│ • Noticia sin published_at y available_at                                    │
│ • Headline actual aplicado retrospectivamente                                │
│ • Sentiment como única representación                                        │
│                                                                              │
│ VEREDICTO PROVISIONAL                                                        │
│ ─────────────────────                                                        │
│ RECOMMENDED CONDITIONAL REPRESENTATION MODEL CANDIDATE                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ HALT CONTEXT                                                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ REPRESENTATION MODEL CANDIDATE                                               │
│ ──────────────────────────────                                               │
│ INSTITUTIONAL CONTINUITY STATE MACHINE                                       │
│                                                                              │
│ QUÉ CONCEPTUALIZA                                                            │
│ ─────────────────                                                            │
│ El estado institucional de continuidad de negociación y sus transiciones     │
│ observables durante el episodio.                                             │
│                                                                              │
│ ESTADOS SEMÁNTICOS CANDIDATOS                                                │
│ ─────────────────────────────                                                │
│ NORMAL_TRADING                                                               │
│ LIMIT_STATE_OR_BAND_CONSTRAINT                                               │
│ HALT_OR_PAUSE_INDICATED                                                      │
│ HALTED                                                                       │
│ RESUMPTION_PENDING                                                           │
│ REOPENED                                                                     │
│ POST_HALT_TRANSITION                                                         │
│ UNKNOWN_OR_UNAVAILABLE                                                       │
│                                                                              │
│ Los nombres finales deben vincularse a los códigos oficiales de cada fuente │
│ y mecanismo regulatorio.                                                     │
│                                                                              │
│ DEBE CONSERVAR INFORMACIÓN SOBRE                                             │
│ ───────────────────────────────                                              │
│ • Código y motivo oficial                                                    │
│ • Estado previo y posterior                                                  │
│ • event_time                                                                 │
│ • observed_at                                                                │
│ • available_at                                                               │
│ • Duración                                                                   │
│ • Fuente y versión                                                           │
│ • Indicaciones de reanudación                                                │
│ • Cambios de continuidad antes y después                                     │
│                                                                              │
│ REGLAS DE INTERPRETACIÓN                                                     │
│ ────────────────────────                                                     │
│ • Ausencia de trades no demuestra por sí sola que exista un halt.            │
│ • Un gap temporal de datos no debe clasificarse automáticamente como halt.   │
│ • Los estados LULD, pause y regulatory halt no son intercambiables.          │
│ • El estado debe entregarse sólo después de su available_at.                 │
│                                                                              │
│ POR QUÉ UNA MÁQUINA DE ESTADOS                                               │
│ ──────────────────────────────                                               │
│ El fenómeno posee estados discretos, orden institucional y transiciones      │
│ legalmente definidas. Una colección de indicadores independientes perdería  │
│ esa estructura.                                                              │
│                                                                              │
│ RECHAZAR COMO MODELO SUFICIENTE                                              │
│ ───────────────────────────────                                              │
│ • Halt inferido solamente por silencio                                       │
│ • Boolean halt sin intervalos ni transición                                  │
│ • Anotación retrospectiva sin available_at                                   │
│ • Mezcla de LULD, pause y halt bajo una sola etiqueta                        │
│                                                                              │
│ BASE CIENTÍFICA Y NORMATIVA                                                  │
│ ───────────────────────────                                                  │
│ SEC Limit Up-Limit Down Plan y especificaciones oficiales CTA/UTP.           │
│                                                                              │
│ VEREDICTO PROVISIONAL                                                        │
│ ─────────────────────                                                        │
│ RECOMMENDED CONDITIONAL REPRESENTATION MODEL CANDIDATE                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘


╔══════════════════════════════════════════════════════════════════════════════╗
║                 DEFERRED EXTENSION REPRESENTATION MODEL                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
┌──────────────────────────────────────────────────────────────────────────────┐
│ ORDER FLOW PRESSURE                                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ REPRESENTATION MODEL CANDIDATE                                               │
│ ──────────────────────────────                                               │
│ SIGNED OBSERVED FLOW-PRICE CONVERSION                                        │
│ WITH PROVENANCE AND CLASSIFICATION CONFIDENCE                                │
│                                                                              │
│ QUÉ CONCEPTUALIZA                                                            │
│ ─────────────────                                                            │
│ La presión direccional inferida del flujo observado y la eficiencia con la   │
│ que dicha presión se convierte en desplazamiento del precio.                 │
│                                                                              │
│ DEBE CONSERVAR DOS SUBMODELOS SEPARADOS                                      │
│ ───────────────────────────────────────                                      │
│                                                                              │
│ QUOTE-EVENT IMBALANCE                                                        │
│ • Cambios observados de bid y ask                                            │
│ • Cambios observados de tamaños                                              │
│ • Desequilibrio de eventos del top-of-book                                   │
│ • Cobertura de quote events                                                  │
│                                                                              │
│ CLASSIFIED AGGRESSOR TRADE FLOW                                              │
│ • Trades clasificados como buyer o seller initiated                          │
│ • Volumen y valor nocional firmados                                          │
│ • Intensidad de la presión                                                   │
│ • Persistencia de la presión                                                 │
│ • Proporción de trades clasificables                                         │
│                                                                              │
│ FLOW-PRICE CONVERSION                                                        │
│ • Desplazamiento producido por unidad de flujo                               │
│ • Divergencia entre esfuerzo y progreso                                      │
│ • Respuesta del midprice                                                     │
│ • Decaimiento o renovación de la presión                                     │
│                                                                              │
│ CONFIDENCE AND PROVENANCE                                                    │
│ • Método de clasificación                                                    │
│ • Versión del clasificador                                                   │
│ • Trade-quote alignment                                                      │
│ • Confianza por evento y ventana                                             │
│ • Cobertura clasificada y no clasificada                                     │
│                                                                              │
│ DISTINCIÓN OBLIGATORIA                                                       │
│ ──────────────────────                                                       │
│ quote-based OFI                                                              │
│                                                                              │
│ no equivale a:                                                               │
│                                                                              │
│ trade-aggressor imbalance                                                    │
│                                                                              │
│ El primero utiliza cambios observados en bid, ask y tamaños.                 │
│ El segundo necesita inferir de forma fiable el lado agresor del trade.       │
│                                                                              │
│ RAZÓN DEL ESTADO DEFERRED                                                    │
│ ─────────────────────────                                                    │
│ Antes de admitir este modelo deben demostrarse:                              │
│                                                                              │
│ • Alineación fiable entre trades y quotes                                    │
│ • Tratamiento de trades dentro del spread                                    │
│ • Tratamiento de mensajes fuera de secuencia                                 │
│ • Cobertura clasificable suficiente                                          │
│ • Estabilidad por ticker, precio, sesión y régimen                           │
│                                                                              │
│ IMPLEMENTACIONES CANDIDATAS                                                  │
│ ───────────────────────────                                                  │
│ • Quote-event OFI                                                            │
│ • Tick test                                                                  │
│ • Quote rule                                                                 │
│ • Lee-Ready u otros clasificadores                                           │
│ • Modelos híbridos con confidence score                                      │
│                                                                              │
│ Estos métodos son implementaciones candidatas, no la identidad conceptual   │
│ del Information Object.                                                      │
│                                                                              │
│ RECHAZAR COMO MODELO SUFICIENTE                                              │
│ ───────────────────────────────                                              │
│ • Volumen comprador/vendedor sin clasificación trazable                      │
│ • OFI y aggressor imbalance mezclados                                        │
│ • Trade sign sin confidence ni cobertura                                     │
│ • Full order-flow reconstruido sin datos de órdenes                          │
│ • Presión inferida exclusivamente por velas                                  │
│                                                                              │
│ BASE CIENTÍFICA PRINCIPAL                                                    │
│ ─────────────────────────                                                    │
│ Cont, Kukanov y Stoikov; Lee y Ready; Hasbrouck.                             │
│                                                                              │
│ VEREDICTO PROVISIONAL                                                        │
│ ─────────────────────                                                        │
│ SCIENTIFICALLY RELEVANT                                                      │
│ DEFERRED UNTIL SOURCE AND CLASSIFICATION VALIDATION                          │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

```

### ARQUITECTURA DE DESARROLLO Y MATERIALIZACIÓN DE MODELOS DE REPRESENTACIÓN

Ref. 1 : [WAKE_UP_DISCOVERY_VARIABLES_v0_1](00_CTO\04_MARKET_STATES_CREATION\04_EVENTS\WAKE_UP\03_LABELS\WAKE_UP_DISCOVERY_VARIABLES_v0_1.md)


Árbol maestro

```
WU-TREE-00
FENÓMENO: WAKE-UP
│
├── 1. Pregunta científica
├── 2. Necesidades de información
│
├── 3. Perfil de Objetos de Información
│   │
│   ├── WU-TREE-01
│   │   CORE REPRESENTATION MODELS
│   │
│   ├── WU-TREE-02
│   │   SUPPORTING CONTEXT REPRESENTATION MODELS
│   │
│   ├── WU-TREE-03
│   │   CONDITIONAL CONTEXT REPRESENTATION MODELS
│   │
│   └── WU-TREE-04
│       DEFERRED EXTENSION REPRESENTATION MODEL
│
├── 4. Oracle Wake-Up
│   │
│   ├── Track Y independiente de los cuatro árboles
│   ├── Variables neutrales de descubrimiento
│   │   └── WAKE_UP_DISCOVERY_VARIABLES_v0_1.md (Ref. 1)
│   └── Produce los labels Y congelados para evaluación
│
├── 5. Integración Wake-Up
│   │
│   ├── Recibe los bindings técnicamente certificados del CORE
│   ├── Puede recibir atributos SUPPORTING certificados
│   ├── Puede recibir contextos CONDITIONAL certificados
│   ├── Excluye extensiones DEFERRED no autorizadas
│   ├── Selecciona los bindings y objetos autorizados
│   ├── Define el detector causal
│   ├── Ejecuta comparaciones y ablations en development
│   └── Congela una configuración Wake-Up completa
│
├── 6. Temporal validation 2023–2024
│   └── Una sola apertura para la configuración completa congelada
│
├── 7. Final OOS 2025–2026
│   └── Una sola apertura final controlada
│
└── 8. Promoción
    ├── Representation bindings seleccionados
    ├── Detector Wake-Up canónico
    ├── Builder de episodios
    ├── Materialización de producción
    ├── Certificación terminal
    ├── Escritura gobernada en event_state
    └── Autorización downstream
```
**Regla única del holdout**

Los árboles de representación terminan antes del holdout:
```
WU-TREE-01 CORE
└── desarrollo, probes, certificación y handoff
                                                 ┐
WU-TREE-02 SUPPORTING                            │
└── desarrollo, probes, certificación y handoff  ├── outputs autorizados
                                                 │
WU-TREE-03 CONDITIONAL                           │
└── desarrollo, probes, certificación y handoff  ┘
            │
            ▼
WU-TREE-00 / INTEGRACIÓN WAKE-UP
            │
            ├── Oracle Wake-Up congelado
            ├── Selección de objetos autorizados
            ├── Selección de bindings certificados
            ├── Definición del detector causal
            ├── Comparaciones y ablations en development
            └── Configuración Wake-Up completa congelada
                    │
                    ▼
            2023–2024 TEMPORAL VALIDATION
                    │
                    ▼
                    GATE
                    │
                    ▼
            2025–2026 FINAL OOS
                    │
                    ▼
                PROMOCIÓN


WU-TREE-04 DEFERRED
└── DEFERRED_NOT_AUTHORIZED
    ├── gates previos pendientes
    ├── sin bindings autorizados
    ├── sin materialización
    └── excluido de la integración de esta versión
```
Ningún árbol hijo debe contener su propia apertura de 2023–2024 o 2025–2026.

```
Si SUPPORTING o CONDITIONAL no están listos cuando se congela la configuración evaluada, quedan fuera de esa versión. Añadirlos después de observar 2025–2026 produciría una nueva versión y exigiría un nuevo protocolo de validación; 2025–2026 ya no sería un holdout virgen.

WU-TREE-04 DEFERRED no entra en desarrollo, certificación o integración mientras permanezca en estado DEFERRED_NOT_AUTHORIZED.
```

Organización documental propuesta
```
00_WAKE_UP_END_to_END.md
└── Árbol maestro WU-TREE-00

01_CORE_REPRESENTATION_MODELS_TREE_v0_1.md
└── WU-TREE-01

02_SUPPORTING_CONTEXT_REPRESENTATION_MODELS_TREE_v0_1.md
└── WU-TREE-02

03_CONDITIONAL_CONTEXT_REPRESENTATION_MODELS_TREE_v0_1.md
└── WU-TREE-03

04_DEFERRED_EXTENSION_REPRESENTATION_MODEL_TREE_v0_1.md
└── WU-TREE-04
```
Cada documento hijo debe declarar obligatoriamente:
```
document_version
tree_id
tree_version
parent_tree_id
parent_node
scope
blocking_policy
inputs
outputs
current_status
scientific_owner
technical_owner
threshold_decision_owner
promotion_authority
handoff_target
holdout_policy
```
Así pueden desarrollarse de forma independiente sin perder la relación con el fenómeno principal ni abrir los holdouts desde los árboles
hijos.

#### WU-TREE-01 `CORE REPRESENTATION MODELS`

```
FENÓMENO 
WAKE-UP
│
├── 1. PREGUNTA CIENTÍFICA
│   │
│   └── ¿Cuándo un instrumento pasa de un régimen dormido o normal
│       a un régimen de participación de mercado materialmente activo?
│
├── 2. NECESIDADES DE INFORMACIÓN
│   │
│   ├── Cuánta actividad aparece y con qué velocidad
│   ├── Cómo se organizan temporalmente trades y quotes
│   ├── Qué movimiento de precio acompaña a la activación
│   ├── En qué condiciones de liquidez ocurre
│   ├── Qué información estaba disponible legalmente en cada instante
│   └── Cuándo la evidencia es insuficiente y el sistema debe abstenerse
│
├── 3. PERFIL DE OBJETOS DE INFORMACIÓN
│   │
│   └── CORE REPRESENTATION MODELS
│       │
│       │   Los cuatro objetos siguientes son ramas hermanas.
│       │   Ninguno está contenido dentro de otro.
│       │
│       │   En Market Microstructure State, Price Movement y Liquidity,
│       │   los identificadores A/B son slots de arquitectura objetivo.
│       │   No declaran bindings existentes, implementados o certificados.
│       │
│       ├── 3.1. TRADING ACTIVITY
│       │   │
│       │   ├── Pregunta que responde
│       │   │   └── ¿Cuánta actividad aparece, con qué rapidez,
│       │   │       concentración y materialidad económica?
│       │   │
│       │   └── REPRESENTATION MODEL CANDIDATE
│       │       PIT-NORMALIZED MULTISCALE MARKED ACTIVITY PROCESS
│       │       │
│       │       ├── TA-BINDING CANDIDATE A
│       │       │   │
│       │       │   ├── Especificación científica exacta
│       │       │   │   ├── Grain
│       │       │   │   ├── Reloj de decisión
│       │       │   │   ├── Política de disponibilidad
│       │       │   │   ├── Ventanas y escalas
│       │       │   │   ├── Fuentes gobernadas
│       │       │   │   └── Semántica de zero, NULL, stale y unavailable
│       │       │   │
│       │       │   ├── Variables exactas de TA-Binding A
│       │       │   ├── Fórmulas, unidades y lineage
│       │       │   ├── Garantías PIT y causalidad
│       │       │   ├── Schema y contratos de salida
│       │       │   ├── Implementación
│       │       │   │   ├── Compute engine
│       │       │   │   ├── Runner
│       │       │   │   ├── Wrapper
│       │       │   │   ├── Aggregator
│       │       │   │   ├── Terminal certifier
│       │       │   │   └── Final manifest
│       │       │   │
│       │       │   ├── Unit tests
│       │       │   ├── Probe production-equivalent por shard
│       │       │   ├── Auditoría variable por variable
│       │       │   ├── Certification readout versionado
│       │       │   ├── Gate humano o gobernado
│       │       │   ├── Materialización experimental development
│       │       │   └── Certificación terminal de TA-Binding A
│       │       │
│       │       ├── TA-BINDING CANDIDATE B
│       │       │   │
│       │       │   ├── Especificación científica exacta
│       │       │   ├── Variables exactas de TA-Binding B
│       │       │   ├── Fórmulas, unidades y lineage
│       │       │   ├── Garantías PIT y causalidad
│       │       │   ├── Schema y contratos de salida
│       │       │   ├── Implementación completa
│       │       │   ├── Unit tests
│       │       │   ├── Probe production-equivalent por shard
│       │       │   ├── Auditoría variable por variable
│       │       │   ├── Certification readout versionado
│       │       │   ├── Gate humano o gobernado
│       │       │   ├── Materialización experimental development
│       │       │   └── Certificación terminal de TA-Binding B
│       │       │
│       │       └── SALIDA ESPERADA DE PRICE MOVEMENT
│       │           │
│       │           ├── TA-Binding A técnicamente admisible o rechazado
│       │           ├── TA-Binding B técnicamente admisible o rechazado
│       │           └── Conjunto de bindings certificados candidatos
│       │
│       │           IMPORTANTE:
│       │           aquí todavía no se elige el ganador científico.
│       │
│       ├── 3.2. MARKET MICROSTRUCTURE STATE
│       │   │
│       │   ├── Pregunta que responde
│       │   │   └── ¿Cómo se relacionan temporalmente los eventos
│       │   │       observados de trades, bid, ask, sizes y midprice?
│       │   │
│       │   └── REPRESENTATION MODEL CANDIDATE
│       │       OBSERVED TRADE-QUOTE EVENT COUPLING STATE
│       │       │
│       │       ├── MMS-BINDING A
│       │       │   ├── Especificación científica exacta
│       │       │   ├── Variables de MMS-Binding A
│       │       │   ├── Sincronización trade-quote
│       │       │   ├── Reglas de disponibilidad y latencia
│       │       │   ├── Fórmulas, unidades y lineage
│       │       │   ├── Garantías PIT
│       │       │   ├── Schema
│       │       │   ├── Implementación completa
│       │       │   ├── Unit tests
│       │       │   ├── Probe production-equivalent por shard
│       │       │   ├── Auditoría variable por variable
│       │       │   ├── Certification readout
│       │       │   ├── Gate gobernado
│       │       │   ├── Materialización development
│       │       │   └── Certificación terminal
│       │       │
│       │       ├── MMS-BINDING B
│       │       │   ├── Especificación científica exacta
│       │       │   ├── Variables de MMS-Binding B
│       │       │   ├── Sincronización trade-quote alternativa
│       │       │   ├── Fórmulas, unidades y lineage
│       │       │   ├── Garantías PIT
│       │       │   ├── Schema
│       │       │   ├── Implementación completa
│       │       │   ├── Unit tests
│       │       │   ├── Probe production-equivalent por shard
│       │       │   ├── Auditoría variable por variable
│       │       │   ├── Certification readout
│       │       │   ├── Gate gobernado
│       │       │   ├── Materialización development
│       │       │   └── Certificación terminal
│       │       │
│       │       └── SALIDA DE MARKET MICROSTRUCTURE STATE
│       │           └── Bindings MMS técnicamente certificados candidatos
│       │
│       ├── 3.3. PRICE MOVEMENT
│       │   │
│       │   ├── Pregunta que responde
│       │   │   └── ¿Qué dirección, trayectoria y progreso causal
│       │   │       presenta el precio durante la activación?
│       │   │
│       │   └── REPRESENTATION MODEL CANDIDATE
│       │       SIGNED MULTISCALE CAUSAL PRICE-PATH RESPONSE
│       │       │
│       │       ├── PM-BINDING A
│       │       │   ├── Especificación científica exacta
│       │       │   ├── Variables de PM-Binding A
│       │       │   ├── Definición del precio observable
│       │       │   ├── Ventanas y escalas causales
│       │       │   ├── Fórmulas, unidades y lineage
│       │       │   ├── Tratamiento de precios stale o no disponibles
│       │       │   ├── Garantías PIT
│       │       │   ├── Schema
│       │       │   ├── Implementación completa
│       │       │   ├── Unit tests
│       │       │   ├── Probe production-equivalent por shard
│       │       │   ├── Auditoría variable por variable
│       │       │   ├── Certification readout
│       │       │   ├── Gate gobernado
│       │       │   ├── Materialización development
│       │       │   └── Certificación terminal
│       │       │
│       │       ├── PM-BINDING B
│       │       │   ├── Especificación científica exacta
│       │       │   ├── Variables de PM-Binding B
│       │       │   ├── Definición alternativa del price path
│       │       │   ├── Fórmulas, unidades y lineage
│       │       │   ├── Garantías PIT
│       │       │   ├── Schema
│       │       │   ├── Implementación completa
│       │       │   ├── Unit tests
│       │       │   ├── Probe production-equivalent por shard
│       │       │   ├── Auditoría variable por variable
│       │       │   ├── Certification readout
│       │       │   ├── Gate gobernado
│       │       │   ├── Materialización development
│       │       │   └── Certificación terminal
│       │       │
│       │       └── SALIDA DE PRICE MOVEMENT
│       │           └── Bindings PM técnicamente certificados candidatos
│       │
│       └── 3.4. LIQUIDITY
│           │
│           ├── Pregunta que responde
│           │   └── ¿Qué condiciones observables de liquidez ofrece
│           │       el mercado y cómo se recuperan tras una perturbación?
│           │
│           └── REPRESENTATION MODEL CANDIDATE
│               OBSERVABLE TOP-OF-BOOK LIQUIDITY CONDITION
│               AND RESILIENCE STATE
│               │
│               ├── LQ-BINDING A
│               │   ├── Especificación científica exacta
│               │   ├── Variables de LQ-Binding A
│               │   ├── Definición de top-of-book observable
│               │   ├── Spread, sizes, revisión y resiliencia
│               │   ├── Reglas de crossed/locked/stale/unavailable
│               │   ├── Fórmulas, unidades y lineage
│               │   ├── Garantías PIT
│               │   ├── Schema
│               │   ├── Implementación completa
│               │   ├── Unit tests
│               │   ├── Probe production-equivalent por shard
│               │   ├── Auditoría variable por variable
│               │   ├── Certification readout
│               │   ├── Gate gobernado
│               │   ├── Materialización development
│               │   └── Certificación terminal
│               │
│               ├── LQ-BINDING B
│               │   ├── Especificación científica exacta
│               │   ├── Variables de LQ-Binding B
│               │   ├── Definición alternativa de liquidez/resiliencia
│               │   ├── Fórmulas, unidades y lineage
│               │   ├── Garantías PIT
│               │   ├── Schema
│               │   ├── Implementación completa
│               │   ├── Unit tests
│               │   ├── Probe production-equivalent por shard
│               │   ├── Auditoría variable por variable
│               │   ├── Certification readout
│               │   ├── Gate gobernado
│               │   ├── Materialización development
│               │   └── Certificación terminal
│               │
│               └── SALIDA DE LIQUIDITY
│                   └── Bindings LQ técnicamente certificados candidatos
│
│
└── 4. SALIDA Y HANDOFF DE WU-TREE-01
    │
    ├── Bindings CORE técnicamente admisibles o rechazados
    ├── Materializaciones development certificadas
    ├── Schemas, lineage y manifests versionados
    ├── Outputs causales X
    ├── Estados de cobertura, calidad y abstención
    ├── Ningún ganador científico seleccionado todavía
    ├── Ningún holdout abierto
    └── handoff_target
        └── WU-TREE-00 / INTEGRACIÓN WAKE-UP
```

Ref. 1: [WAKE_UP_DISCOVERY_VARIABLES_v0_1](03_LABELS/WAKE_UP_DISCOVERY_VARIABLES_v0_1.md)
```
WU-TREE-00 / CONTINUACIÓN EXTERNA AL WU-TREE-01
│
├── 4. ORACLE WAKE-UP
│   TRACK Y: VERDAD DE EVALUACIÓN
│   │
│   │   Esta rama se construye en paralelo.
│   │   No pertenece a Trading Activity.
│   │   No es un Binding.
│   │   No forma parte de las variables causales X.
│   │   Su owner estructural es WU-TREE-00.
│   │
│   ├── Protocolo de calibración RTH
│   ├── Denominator de 2.400 sesiones development 2011–2022
│   ├── Variables neutrales de descubrimiento
│   │   └── WAKE_UP_DISCOVERY_VARIABLES_v0_1.md (Ref. 1)
│   ├── Búsqueda de alta sensibilidad
│   ├── Pool de 4.447 candidatos no etiquetados
│   ├── Panel ciego de 240 casos
│   │   ├── 40 candidatos de transición
│   │   └── 200 controles
│   ├── Revisión humana independiente
│   ├── Adjudicación de desacuerdos
│   ├── Decisiones WUL-D01...WUL-D08
│   ├── Congelación de la definición del Oracle
│   ├── Materialización de labels sobre las 2.400 sesiones
│   ├── Auditoría de cobertura, abstenciones y leakage
│   └── ORACLE WAKE-UP CONGELADO
│       └── Labels Y utilizables por el evaluador
│
└── 5. INTEGRACIÓN WAKE-UP
    │
    │   Esta etapa pertenece a WU-TREE-00.
    │   WU-TREE-01 participa entregando los bindings CORE certificados.
    │   Aquí convergen:
    │
    │   X = outputs causales de los cuatro objetos CORE
    │   Y = labels del Oracle Wake-Up congelado
    │
    ├── 5.1. Definir el rol de cada objeto
    │   │
    │   ├── Trigger primario
    │   ├── Corroborador
    │   ├── Caracterizador del episodio
    │   ├── Control de calidad
    │   └── Veto o causa de abstención
    │
    │   Que un objeto sea CORE no significa necesariamente
    │   que todas sus variables sean condiciones obligatorias
    │   para disparar Wake-Up.
    │
    ├── 5.2. Construir configuraciones CORE candidatas
    │   │
    │   ├── Elegir un Binding certificado de Trading Activity
    │   ├── Elegir un Binding certificado de Microstructure
    │   ├── Elegir un Binding certificado de Price Movement
    │   ├── Elegir un Binding certificado de Liquidity
    │   └── Combinar los cuatro bajo un contrato común
    │
    │   Ejemplo puramente teórico, solo si todos los objetos llegan
    │   a tener exactamente dos bindings especificados y certificados:
    │   Si todos tuvieran exactamente A y B:
    │
    │   2 × 2 × 2 × 2 =  máximo teórico de 16 configuraciones CORE
    │   Este cálculo no declara que las 16 configuraciones existan
    │   ni que todas estén autorizadas para evaluación.
    │
    │   Ejemplos:
    │
    │   ├── CORE-C01 = TA-A + MMS-A + PM-A + LQ-A
    │   ├── CORE-C02 = TA-B + MMS-A + PM-A + LQ-A
    │   ├── CORE-C03 = TA-A + MMS-B + PM-A + LQ-A
    │   ├── CORE-C04 = TA-A + MMS-A + PM-B + LQ-A
    │   └── CORE-C05 = TA-A + MMS-A + PM-A + LQ-B
    │
    ├── 5.3. Congelar el detector CORE candidato para comparación development
    │   │
    │   ├── Inputs X permitidos
    │   ├── Reglas de activación
    │   ├── Umbrales
    │   ├── Quorum o corroboración
    │   ├── Reglas de abstención
    │   ├── Inicio del episodio
    │   ├── Continuidad
    │   ├── Cierre
    │   ├── Reset
    │   └── Rearm
    │
    ├── 5.4. Congelar el protocolo evaluador
    │   │
    │   ├── Mismo presupuesto para cada configuración
    │   ├── Mismas sesiones
    │   ├── Mismo Oracle
    │   ├── Mismas métricas
    │   ├── Mismo tratamiento de abstenciones
    │   ├── Mismo protocolo de timing
    │   └── Mismos estratos científicos
    │
    ├── 5.5. Comparación en development 2011–2022
    │   │
    │   ├── Capacidad de detección
    │   ├── Falsas activaciones
    │   ├── Error temporal respecto al Oracle
    │   ├── Cobertura
    │   ├── Abstenciones
    │   ├── Estabilidad por año
    │   ├── Estabilidad por precio
    │   ├── Estabilidad por market-cap proxy
    │   ├── Estabilidad por hora RTH
    │   ├── Sensibilidad a parámetros
    │   └── Robustez a calidad y fuentes
    │
    ├── 5.6. Ablation studies
    │   │
    │   ├── Sin Trading Activity
    │   ├── Sin Microstructure
    │   ├── Sin Price Movement
    │   ├── Sin Liquidity
    │   ├── Las sustituciones siguientes solo se ejecutan si ambos
    │   │   bindings están especificados, certificados y autorizados
    │   ├── Sustituyendo TA-A por TA-B
    │   ├── Sustituyendo MMS-A por MMS-B
    │   ├── Sustituyendo PM-A por PM-B
    │   └── Sustituyendo LQ-A por LQ-B
    │
    ├── 5.7. Selección y congelación de la configuración CORE
    │   │
    │   └── CORE WAKE-UP CONFIGURATION FROZEN
    │       ├── Binding seleccionado de Trading Activity
    │       ├── Binding seleccionado de Microstructure
    │       ├── Binding seleccionado de Price Movement
    │       ├── Binding seleccionado de Liquidity
    │       ├── Detector CORE seleccionado
    │       ├── Parámetros congelados
    │       ├── Reglas de episodio congeladas
    │       └── Reglas de abstención congeladas
    │
    ├── 5.8. Validación temporal 2023–2024
    │   │
    │   ├── Recibir la configuración CORE congelada
    │   ├── Incorporar SUPPORTING certificado y aceptado, si corresponde
    │   ├── Incorporar CONDITIONAL certificado y aceptado, si corresponde
    │   ├── Excluir DEFERRED no autorizado
    │   ├── Congelar los inputs X definitivos
    │   ├── Congelar el detector Wake-Up completo
    │   ├── Congelar parámetros, umbrales y reglas de abstención
    │   └── WAKE-UP CONFIGURATION FROZEN
    │
    ├── 5.9. Validación temporal 2023–2024
    │   │
    │   ├── Sin recalibrar bindings
    │   ├── Sin cambiar detector
    │   ├── Sin cambiar umbrales
    │   └── Gate de validación temporal
    │
    ├── 5.10. Final OOS 2025–2026
    │   │
    │   ├── Una única evaluación final
    │   ├── Sin selección posterior basada en OOS
    │   └── Gate final de promoción
    │
    └── 5.11. WAKE-UP CONFIGURATION PROMOVIDA
        │
        ├── Especificación canónica de todos los objetos integrados
        ├── Bindings canónicos seleccionados
        ├── Schemas canónicos
        ├── Builders canónicos
        ├── Detector Wake-Up canónico
        ├── Builder de episodios Wake-Up
        ├── Materialización de producción
        ├── Final manifest
        ├── Certificación terminal
        ├── Escritura gobernada en event_state
        └── Autorización downstream
```

#### WU-TREE-02 `SUPPORTING CONTEXT REPRESENTATION MODELS`

Este árbol puede desarrollarse de manera independiente y, en su primera versión, no debe bloquear el detector core.

```
WU-TREE-02
SUPPORTING CONTEXT REPRESENTATION MODELS
│
├── parent_tree
│   └── WU-TREE-00 / Perfil de Objetos de Información
│
├── dependency_policy
│   │
│   ├── No bloquea inicialmente WU-TREE-01
│   ├── No define por sí solo Wake-Up
│   ├── No puede usar información futura
│   └── Su valor incremental se evalúa en development
│
├── Volatility / Range State
│   │
│   ├── scientific_question
│   │   └── ¿La activación ocurre dentro de un régimen normal,
│   │       comprimido o excepcionalmente expansivo?
│   │
│   ├── Representation Model Candidate
│   │   │
│   │   ├── Uno o más bindings candidatos
│   │   ├── Variables causales multiescala
│   │   ├── Rangos observables hasta t
│   │   ├── Variación de midquote
│   │   ├── Variación de eligible trade prices
│   │   ├── Estimadores robustos al ruido microestructural
│   │   └── Estados de disponibilidad
│   │
│   ├── prohibited_semantics
│   │   │
│   │   ├── No usar high final de la sesión antes del cierre
│   │   ├── No usar low final de la sesión antes del cierre
│   │   ├── No usar volatilidad calculada con observaciones futuras
│   │   └── No interpretar volatilidad baja como ausencia automática de Wake-Up
│   │
│   ├── binding_lifecycle
│   │   ├── Especificación
│   │   ├── Implementación
│   │   ├── Unit tests
│   │   ├── Probes por shard
│   │   ├── Auditoría de variables
│   │   ├── Materialización development
│   │   └── Certificación
│   │
│   └── output
│       └── Atributo contextual de régimen de volatilidad/rango
│
├── Price Location / Structure
│   │
│   ├── scientific_question
│   │   └── ¿Dónde ocurre la activación respecto a referencias
│   │       estructurales conocidas y disponibles en t?
│   │
│   ├── Representation Model Candidate
│   │   └── CAUSAL ANCHOR-RELATIVE LOCATION STATE
│   │       │
│   │       ├── Uno o más bindings candidatos
│   │       ├── Posición respecto a prior close
│   │       ├── Posición respecto a session open
│   │       ├── Posición respecto a high observable hasta t
│   │       ├── Posición respecto a low observable hasta t
│   │       ├── Posición respecto a VWAP interno gobernado hasta t
│   │       └── Posición respecto a niveles previamente conocidos
│   │
│   ├── prohibited_semantics
│   │   │
│   │   ├── No usar session high final para decisiones anteriores
│   │   ├── No usar session low final para decisiones anteriores
│   │   ├── No usar VWAP con trades posteriores a t
│   │   └── No incorporar niveles conocidos retrospectivamente
│   │
│   ├── binding_lifecycle
│   │   ├── Especificación
│   │   ├── Implementación
│   │   ├── Unit tests
│   │   ├── Probes por shard
│   │   ├── Auditoría de variables
│   │   ├── Materialización development
│   │   └── Certificación
│   │
│   └── output
│       └── Atributo contextual de localización/estructura
│
├── supporting_evaluation
│   │
│   ├── Evaluación exclusivamente en development
│   ├── Comparación core-only contra core-plus-supporting
│   ├── Ablation de Volatility / Range
│   ├── Ablation de Price Location / Structure
│   ├── Estabilidad por estratos
│   ├── Valor incremental
│   └── Coste de disponibilidad y abstención
│
└── handoff_to_master
    │
    ├── SUPPORTING_ACCEPTED
    │   └── Atributos congelados antes de temporal validation
    │
    ├── SUPPORTING_NOT_INCREMENTAL
    │   └── Se conservan como contexto descriptivo, no como detector input
    │
    ├── SUPPORTING_REJECTED
    │   └── No se integran
    │
    └── Regreso a:
        WU-TREE-00 / Integración Wake-Up
```

La regla semántica es:
```
Volatility baja
≠
ausencia de Wake-Up
```
Y también:
```
Price Location
=
contexto causal de dónde ocurre la activación

Price Location
≠
definición autónoma de Wake-Up
```
———

# WU-TREE-03: `CONDITIONAL CONTEXT`

Estos objetos se consumen cuando están disponibles y son relevantes. No deben convertirse en dependencias universales silenciosas.
```
WU-TREE-03
CONDITIONAL CONTEXT REPRESENTATION MODELS
│
├── parent_tree
│   └── WU-TREE-00 / Perfil de Objetos de Información
│
├── dependency_policy
│   │
│   ├── No son obligatorios universalmente
│   ├── Su ausencia no equivale a valor cero
│   ├── Su ausencia no equivale a condición negativa
│   ├── Deben declarar disponibilidad y calidad
│   ├── Deben respetar publication/availability time
│   └── No definen aisladamente Wake-Up
│
├── Fundamental Context
│   │
│   ├── Representation Model Candidate
│   │   └── PIT FUNDAMENTAL SCALE CONTEXT
│   │
│   ├── possible_information
│   │   ├── Market-cap context
│   │   ├── Shares outstanding
│   │   ├── Float estimate
│   │   ├── Dilution context
│   │   └── Ownership context
│   │
│   ├── mandatory_availability_state
│   │   ├── AVAILABLE
│   │   ├── STALE
│   │   ├── DEGRADED
│   │   └── UNAVAILABLE
│   │
│   ├── prohibited_semantics
│   │   ├── UNAVAILABLE no puede convertirse en cero
│   │   ├── STALE no puede tratarse como observación actual
│   │   ├── Filing date no equivale automáticamente a availability time
│   │   └── Revisiones posteriores no pueden retropropagarse
│   │
│   ├── lifecycle
│   │   ├── Especificación PIT
│   │   ├── Binding candidato
│   │   ├── Implementación
│   │   ├── Probes
│   │   ├── Auditoría
│   │   ├── Materialización development
│   │   └── Certificación
│   │
│   └── output
│       └── Contexto fundamental condicionado por disponibilidad
│
├── News / Catalyst Context
│   │
│   ├── Representation Model Candidate
│   │   └── AVAILABILITY-AWARE CATALYST EVENT CONTEXT
│   │
│   ├── possible_states
│   │   ├── CATALYST_OBSERVED
│   │   ├── NO_CATALYST_OBSERVED
│   │   ├── SOURCE_UNAVAILABLE
│   │   ├── PUBLICATION_TIME_UNCERTAIN
│   │   └── CLASSIFICATION_UNCERTAIN
│   │
│   ├── mandatory_lineage
│   │   ├── Source
│   │   ├── Publication timestamp
│   │   ├── Observation timestamp
│   │   ├── Availability timestamp
│   │   ├── Classification method
│   │   └── Confidence
│   │
│   ├── prohibited_semantics
│   │   ├── No news encontrada no equivale a ausencia real de catalyst
│   │   ├── Catalyst posterior no puede asociarse retrospectivamente
│   │   ├── Fecha sin hora no puede fingir precisión intradía
│   │   └── Una noticia no define por sí sola Wake-Up
│   │
│   ├── lifecycle
│   │   ├── Validación de fuentes
│   │   ├── Especificación
│   │   ├── Binding candidato
│   │   ├── Implementación
│   │   ├── Probes
│   │   ├── Auditoría
│   │   ├── Materialización development
│   │   └── Certificación
│   │
│   └── output
│       └── Contexto causal de catalyst y disponibilidad informativa
│
├── Halt Context
│   │
│   ├── Representation Model Candidate
│   │   └── INSTITUTIONAL CONTINUITY STATE MACHINE
│   │
│   ├── possible_states
│   │   ├── TRADING_CONTINUOUS
│   │   ├── HALT_ACTIVE
│   │   ├── LULD_STATE
│   │   ├── REGULATORY_PAUSE
│   │   ├── RESUME_OBSERVED
│   │   ├── STATE_UNCERTAIN
│   │   └── DATA_UNAVAILABLE
│   │
│   ├── prohibited_semantics
│   │   ├── Ausencia de trades no demuestra halt
│   │   ├── Ausencia de quotes no demuestra halt
│   │   ├── Un gap temporal no demuestra resume
│   │   └── La falta de fuente oficial no puede convertirse en NO_HALT
│   │
│   ├── lifecycle
│   │   ├── Validación de fuentes institucionales
│   │   ├── Especificación de la state machine
│   │   ├── Binding candidato
│   │   ├── Implementación
│   │   ├── Probes
│   │   ├── Auditoría
│   │   ├── Materialización development
│   │   └── Certificación
│   │
│   └── output
│       └── Estado institucional de continuidad de negociación
│
├── conditional_evaluation
│   │
│   ├── Evaluación solamente en development
│   ├── Cobertura real de cada fuente
│   ├── Valor cuando el contexto está disponible
│   ├── Comportamiento cuando no está disponible
│   ├── Sensibilidad a timestamps inciertos
│   ├── Efecto sobre abstenciones
│   └── Ausencia de dependencia universal accidental
│
└── handoff_to_master
    │
    ├── Contextos condicionales certificados
    ├── Availability contract congelado
    ├── Reglas de uso condicional congeladas
    ├── Reglas de degradación/abstención
    └── Regreso a:
        WU-TREE-00 / Integración Wake-Up
```
La distinción fundamental es:
```
NO_CATALYST_OBSERVED
≠
SOURCE_UNAVAILABLE
```
Y también:
```
HALT no observado
≠
halt inexistente
```
———

# WU-TREE-04: `DEFERRED EXTENSION`

Este árbol documenta lo que todavía no está autorizado a entrar en desarrollo de bindings.
```
WU-TREE-04
DEFERRED EXTENSION REPRESENTATION MODEL
│
├── parent_tree
│   └── WU-TREE-00 / Perfil de Objetos de Información
│
├── object
│   └── Order Flow Pressure
│
├── Representation Model Candidate
│   └── SIGNED OBSERVED FLOW-PRICE CONVERSION
│       WITH PROVENANCE AND CLASSIFICATION CONFIDENCE
│
├── current_status
│   └── DEFERRED_NOT_AUTHORIZED
│
├── unresolved_gates
│   │
│   ├── Source-validation gate
│   │   ├── Cobertura
│   │   ├── Calidad
│   │   ├── Timestamp semantics
│   │   └── Source-state semantics
│   │
│   ├── Trade/quote alignment gate
│   │   ├── Orden temporal observable
│   │   ├── Empates de timestamp
│   │   ├── Latencias
│   │   ├── Quote revisions
│   │   └── Ausencia de causalidad inventada
│   │
│   ├── Aggressor-classification gate
│   │   ├── Método de clasificación
│   │   ├── Ground truth o evidencia
│   │   ├── Tasa de clasificación
│   │   ├── Error estimado
│   │   └── Confidence explícita
│   │
│   └── Flow-price conversion gate
│       ├── Definición científica
│       ├── Horizonte causal
│       ├── Separación de presión y respuesta
│       └── Robustez microestructural
│
├── prohibited_work
│   │
│   ├── No crear Binding A/B como si estuvieran autorizados
│   ├── No iniciar materialización larga
│   ├── No incorporarlo al detector Wake-Up
│   ├── No usarlo en selección de configuraciones CORE
│   └── No abrir temporal validation ni final OOS
│
├── authorization_gate
│   │
│   ├── Evidencia de fuentes suficiente
│   ├── Alignment certificado
│   ├── Clasificación de aggressor validada
│   ├── Semántica PIT aprobada
│   ├── Scientific owner declarado
│   ├── Threshold decision owner declarado
│   └── Decisión formal:
│       AUTHORIZE_BINDING_RESEARCH
│
├── possible_future_bindings
│   │
│   ├── Quote-event OFI Binding
│   ├── Classified Aggressor Flow Binding
│   └── Hybrid Confidence Binding
│
└── future_handoff
    │
    ├── Si los gates fallan
    │   └── Permanece DEFERRED
    │
    └── Si todos los gates pasan
        ├── Se crea un nuevo research_experiment
        ├── Se autorizan bindings candidatos
        ├── Se ejecuta el lifecycle completo
        └── Se solicita integración en una futura versión de Wake-Up
```

Deferred no significa que el objeto sea irrelevante. Significa que todavía no existe evidencia suficiente para autorizar una representación física.

———



### VARIABLES / FEATURES

Las fórmulas y columnas concretas del `BINDING` ganador

### MAPPING: objeto → modelo → binding → variable → fuente

### MATERIALIZACIÓN Y CERTIFICACIÓN

### MARKET STATE

### WAKE-UP DETECTOR

### EVENT STATE



```
VARIABLES / FEATURES
↓
TABLAS FUENTE 000–018
↓
MARKET STATE REPRESENTATION CONTRACT
↓
MARKET STATE BUILDER
↓
MARKET STATE
↓
MARKET STATE TRAJECTORY / WINDOW
↓
WAKE-UP DETECTOR CANDIDATO
↓
WAKE-UP EVENT CANDIDATE RECORD
├── EVENT STATE DE WAKE-UP — OPCIONAL
└── CANDIDATE MARKET ACTIVATION EPISODE INSTANCE
    ↓
    RESEARCH ACTIVE SYMBOL SET
    ↓
    TRADABLE IN-PLAY CLASSIFIER
    ↓
    TRADABILITY ASSESSMENT
    ↓
    FRONTSIDE PHASE TRACKER
    ↓
    FRONTSIDE TERMINATION DETECTOR CANDIDATO
    ↓
    FRONTSIDE TERMINATION EVENT CANDIDATE RECORD
    ├── EVENT STATE DE TERMINATION — OPCIONAL
    └── BACKSIDE CONFIRMATION / EPISODE RESOLUTION
↓
OUTCOME ENGINE — SEPARADO DE LOS INPUTS
↓
DETECTOR EVALUATION + VALIDACIÓN TEMPORAL/OOS
↓
EVENT TYPE ADMISSION / OPERATIONAL PROMOTION
↓
DETECTOR CONGELADO
↓
POLÍTICA / ESTRATEGIA
↓
RISK / OMS
↓
EJECUCIÓN
↓
FILL / POSICIÓN / PnL
```  