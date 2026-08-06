# From `wake-up` to `market & event state_table`

```
PREMISA INICIAL:  
```


**Las 3 etapas de un frontside**

1. `wake-up`
2. intermedio o `trayectoria de estado`
3. `termination`

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

### FENÓMENO OBSERVABLE

```
FENÓMENO OBSERVABLE:
subconjunto que transita de Dormancy a activación anómala.

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
                            + Volatility / Range State
                            + Liquidity como contexto
───────────────────────────  ────────────────────────────────────────────────────────
Transición anómala           Trading Activity
                            + Market Microstructure State como corroboración
───────────────────────────  ────────────────────────────────────────────────────────
Materialidad absoluta        Trading Activity
───────────────────────────  ────────────────────────────────────────────────────────
Evidencia multievento        Market Microstructure State
                            + Data Quality Contract como gate de validez
───────────────────────────  ────────────────────────────────────────────────────────
Respuesta contemporánea      Price Movement + Liquidity
                            + Market Microstructure State
───────────────────────────  ────────────────────────────────────────────────────────
Dirección inicial            Price Movement
                            + Order Flow Pressure como extensión diferida
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


```
VARIABLES / FEATURES
```
```
NECESIDADES DE INFORMACIÓN
```
```
INFORMATION OBJECTS
```
```
REPRESENTATION MODELS
```
```
MAPPING OPERACIONAL
Objeto → representación → feature → fuente
```
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



## FENÓMENO `Wake-up`
```
Un instrumento abandona un régimen  
dormido o de baja actividad  
y entra en un régimen  
de activación materialmente anómala.  
```

## Definición científica ¿Qué fenómeno queremos identificar?

> Dentro de un universo point-in-time elegible y una sesión autorizada, un Wake-up Event es la transición
> causalmente detectable que abre un nuevo episodio de activación —conforme a sus reglas de deduplicación y
> rearme y siempre que no exista un Market Activation Episode vigente— desde un régimen dormido o de baja
> actividad contextual hacia un régimen de actividad materialmente anómala respecto a un baseline
> point-in-time.
>
> La transición debe estar sustentada por una sorpresa relativa de actividad, un suelo absoluto de minimis
> destinado exclusivamente a descartar cambios microscópicos y una corroboración contemporánea multievento
> o multifuente suficientemente no redundante para excluir un print aislado, ruido transitorio, desorden
> temporal o un defecto de datos.
>
> Cuando clock >= wake_up_available_at_utc, la detección inicia WATCH, crea un
> CandidateMarketActivationEpisodeInstance e incorpora el instrumento al ResearchActiveSymbolSet. No afirma
> todavía que la participación sea persistente, que exista un frontside, que el instrumento sea tradable
> para un tamaño determinado, que el precio vaya a continuar, que una política permita entrar ni que exista
> edge económico.
>
> Una activación que posteriormente falle, vuelva al régimen dormido o nunca alcance In-Play no invalida
> retrospectivamente el Wake-up emitido con información causalmente disponible.