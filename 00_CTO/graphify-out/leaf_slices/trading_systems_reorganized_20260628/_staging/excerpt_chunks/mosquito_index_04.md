## 18. Whole_Dollar_Range_Cook_Breakout_Event

### Presentacion TSIS

Familia probable:

```text
RESISTANCE_AND_BREAKOUTS
LIQUIDITY_AND_SPREAD_STATE
```

Fenomeno:

La accion se sostiene durante largo tiempo alrededor de un nivel psicologico o
rango relevante, por ejemplo cerca de 1 dolar. No logra ser hundida. El patron
"cuece" durante suficiente tiempo, involucra participantes y termina
despegando.

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/025.png" width="760" alt="025 - Nivel cercano a 1 dolar y estructura que aguanta">

<img src="source_assets/mosquito_smallcaps/img/026.jpg" width="760" alt="026 - Rango sostenido, compras y despegue">

### Texto del trader

El trader dice que no basta con mirar el patron, el mercado o las borrows por
separado. Hay que juntar todas las variables.

En el ejemplo, la accion esta alrededor de un nivel cercano a 1 dolar. En
intradia rompe 0.90, consolida, luego sostiene por encima de 1. El trader
explica que estaba esperando que la accion "le dijera" cuando actuar.

La idea central es dejar cocer el patron. Si intenta crearlo demasiado pronto,
se esconde. Necesita esperar a que se involucren traders. Cuanto mas tiempo
evoluciona sin romper el rango, mas potente puede ser. Al final despega porque
el lado comprador es mas fuerte que el vendedor; en sus palabras, hay un
comprador al que le da igual a que precio comprar.

### Lectura TSIS

Este evento combina:

```text
psychological level
-> range acceptance
-> failed downside break
-> participant build-up
-> late breakout
```

Es probablemente uno de los eventos mas importantes del documento porque une
nivel, tiempo, liquidez, absorcion y conducta de masas.

### Observables futuros

- whole-dollar proximity;
- time above/below level;
- failed breakdowns;
- range duration;
- volume build-up;
- late-day breakout;
- buyer dominance proxy;
- spread/liquidity quality.

## 19. Relative_Volume_Watchlist_Event

### Presentacion TSIS

Familia probable:

```text
CATALYST_AND_ATTENTION
MOMENTUM_EXPANSION
```

Fenomeno:

Una accion muestra una barra o sesion de volumen relativo tan evidente que pasa
de universo pasivo a vigilancia activa. El trader lo describe como volumen que
no necesita discusion: se ve directamente en el grafico.

Este evento no es una ruptura ni una entrada. Es un cambio de atencion.

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/006.jpg" width="760" alt="006 - Volumen relativamente alto">

<img src="source_assets/mosquito_smallcaps/img/025.png" width="760" alt="025 - Volumen y contexto global de variables">

### Texto del trader

El trader insiste varias veces en que el volumen relativo alto es una condicion
central. En el playbook de doble maximo dice que no hace falta volverse loco:
si el volumen es realmente alto, la barra se ve sin tener que preguntarlo.
Cuando aparece ese volumen, la accion pasa directamente a vigilancia.

Tambien repite que no basta con un patron visual. Rectangulos, banderas o
dobles maximos solo importan si aparecen en acciones concretas y con volumen
relevante.

### Lectura TSIS

Evento de activacion de vigilancia:

```text
previously passive ticker
-> obvious relative volume expansion
-> watchlist state
-> later structure may matter
```

No significa que el precio vaya a continuar. Solo indica que la accion esta
recibiendo participacion anomala suficiente para justificar research.

### Rol en lecturas compuestas

Rol principal:

```text
context_event
attention_event
```

Estrategias/arquetipos donde puede aparecer:

- `Go ETB Go`;
- `Doble máximo`;
- `Gap and Go`;
- `First Green Day`;
- `Volume Breakout`;
- `Small Cap Momentum`.

Composicion didactica no operativa:

```text
Relative_Volume_Watchlist_Event
+ Low_Float_Catalyst_Volume_Extension_Event
+ Bull_Flag_Volume_Break_Event
```

Lectura humana:

```text
El ticker ya no esta muerto para el mercado.
Hay volumen visible.
Ahora las estructuras posteriores merecen atencion.
```

### Observables futuros

- relative_volume_daily;
- volume_vs_recent_sessions;
- dollar_volume;
- volume_percentile;
- first_volume_spike_date;
- volume_visible_by_eye_flag;
- watchlist_activation_ts.

## 20. ETB_Borrow_Availability_Context_Event

### Presentacion TSIS

Familia probable:

```text
SHORT_SQUEEZE_DYNAMICS
CATALYST_AND_ATTENTION
```

Fenomeno:

El ticker tiene borrows disponibles o condicion `easy to borrow`, permitiendo
que participantes short entren con facilidad. Esto no es un movimiento de
precio, pero si es un estado observable del entorno de participantes.

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/001.png" width="760" alt="001 - Criterios del playbook y borrows/ETB">

<img src="source_assets/mosquito_smallcaps/img/002.png" width="760" alt="002 - Seguimiento al dia siguiente y revision de borrows">

### Texto del trader

El trader explica que el stock debe tener borrows. Si es `easy to borrow`, lo
considera mejor que si hay que pagar caro para ponerse corto. Si no hay acciones
disponibles para short, practicamente descarta esa operativa.

Al dia siguiente vuelve a revisar los borrows. La razon es que parte del marco
depende de que haya participacion short posible. Si los shorts pueden entrar y
el precio no cae, la presion posterior puede aumentar.

### Lectura TSIS

Evento/contexto de acceso short:

```text
borrow availability exists
-> short participation is possible
-> failed downside pressure becomes more informative
```

Esto no prueba que haya shorts atrapados. Solo establece que el mercado permite
esa participacion.

### Rol en lecturas compuestas

Rol principal:

```text
participant_access_context
short_context_event
```

Estrategias/arquetipos donde puede aparecer:

- `Go ETB Go`;
- `Doble máximo`;
- `Short Squeeze Continuation`;
- `Failed Breakdown`;
- `High Hold Squeeze`.

Composicion didactica no operativa:

```text
ETB_Borrow_Availability_Context_Event
+ Failed_Bear_Attack_Absorption_Event
+ High_Hold_Short_Squeeze_Continuation_Event
```

Lectura humana:

```text
Los shorts pueden participar.
Si participan y no consiguen bajar el precio, su posicion psicologica cambia.
```

### Observables futuros

- borrow_available_flag;
- ETB_flag;
- borrow_cost_proxy;
- borrow_availability_date;
- shortability_status;
- source_quality_flag;
- missing_borrow_data_flag.

## 21. Two_Day_Initial_Extension_As_One_Event

### Presentacion TSIS

Familia probable:

```text
RUNNER_LIFECYCLE
MOMENTUM_EXPANSION
```

Fenomeno:

La extension inicial no ocurre en una sola sesion, sino en dos dias
consecutivos o cercanos. El trader interpreta ese movimiento doble como una
misma extension inicial si responde al mismo catalyst o continuidad de
atencion.

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/013.png" width="760" alt="013 - Movimiento doble asociado a catalyst sectorial">

<img src="source_assets/mosquito_smallcaps/img/014.png" width="760" alt="014 - Marcado del maximo tras movimiento compuesto">

### Texto del trader

En el ejemplo de ACB, el trader explica que el segundo dia de movimiento no le
invalida la lectura. Le da igual que el recorrido inicial ocurra en un dia o en
dos, porque para su marco puede contar como el mismo movimiento si viene de una
noticia y continuidad de atencion.

Esta idea es importante porque evita definir de forma demasiado estrecha el
primer dia de expansion.

### Lectura TSIS

Evento de normalizacion temporal de extension:

```text
day1 extension
+ day2 continuation
-> treated as one initial extension window
```

No es estrategia. Es una regla conceptual para no romper artificialmente una
misma fase de atencion en dos eventos desconectados.

### Rol en lecturas compuestas

Rol principal:

```text
lifecycle_context_event
extension_window_event
```

Estrategias/arquetipos donde puede aparecer:

- `Go ETB Go`;
- `Doble máximo`;
- `Multi-Day Runner`;
- `First Green Day Continuation`;
- `Sector Catalyst Runner`.

Composicion didactica no operativa:

```text
Low_Float_Catalyst_Volume_Extension_Event
+ Two_Day_Initial_Extension_As_One_Event
+ Prior_High_Open_Rebreak_Event
```

Lectura humana:

```text
La primera extension puede durar mas de una sesion.
El nivel relevante nace del bloque completo, no solo del primer dia calendario.
```

### Observables futuros

- extension_window_start_date;
- extension_window_end_date;
- cumulative_extension_pct;
- same_catalyst_flag;
- max_level_source_day;
- volume_distribution_by_day;
- event_day_count.

## 22. Prior_High_Proximity_Open_Event

### Presentacion TSIS

Familia probable:

```text
RESISTANCE_AND_BREAKOUTS
MOMENTUM_EXPANSION
```

Fenomeno:

El precio abre muy cerca del maximo relevante anterior, o lo supera por poco.
Esto crea una sesion donde el nivel puede activarse muy pronto.

Este evento separa la proximidad al nivel de la ruptura posterior. Estar cerca
del maximo no es lo mismo que romperlo.

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/003.png" width="760" alt="003 - Variables de entrada segun apertura cerca del maximo">

<img src="source_assets/mosquito_smallcaps/img/015.jpg" width="760" alt="015 - Rotura temprana del maximo en primeras velas">

### Texto del trader

El trader distingue dos situaciones: si la accion abre superando el maximo del
primer dia por menos de un 1%, lo considera contexto agresivo; si abre mas cerca
del rango del segundo dia, lo trata de forma mas defensiva.

Tambien remarca que muchas rupturas pueden ocurrir en el minuto uno o dos, por
lo que el nivel debe estar preparado antes de la apertura.

### Lectura TSIS

Evento de proximidad al nivel:

```text
prior high exists
-> open is very near prior high
-> level can activate early
```

No dice que haya que comprar. Solo identifica que la sesion empieza en una zona
donde el nivel previo es inmediatamente relevante.

### Rol en lecturas compuestas

Rol principal:

```text
level_proximity_event
opening_context_event
```

Estrategias/arquetipos donde puede aparecer:

- `Go ETB Go`;
- `Doble máximo`;
- `Opening Range Breakout`;
- `High of Day Breakout`;
- `Prior High Rebreak`.

Composicion didactica no operativa:

```text
Two_Day_Initial_Extension_As_One_Event
+ Prior_High_Proximity_Open_Event
+ Prior_High_Open_Rebreak_Event
```

Lectura humana:

```text
El ticker no abre en cualquier sitio.
Abre donde el maximo previo puede importar inmediatamente.
```

### Observables futuros

- prior_high_level;
- open_to_prior_high_pct;
- open_above_prior_high_flag;
- first_minutes_to_level_test;
- session_gap_type;
- aggressive_open_context_flag.

## 23. Failed_Breakout_Not_Invalidated_Event

### Presentacion TSIS

Familia probable:

```text
MOMENTUM_EXHAUSTION
RUNNER_LIFECYCLE
RESISTANCE_AND_BREAKOUTS
```

Fenomeno:

Una ruptura o intento de continuacion no funciona inmediatamente, pero la
estructura mayor tampoco queda invalidada. El ticker sigue vivo y puede romper
mas tarde.

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/022.jpg" width="760" alt="022 - Banderita que falla primero y explota despues">

<img src="source_assets/mosquito_smallcaps/img/023.jpg" width="760" alt="023 - Operacion fallida que funciona al dia siguiente">

<img src="source_assets/mosquito_smallcaps/img/024.jpg" width="760" alt="024 - Banderita perfecta despues de fallo previo">

### Texto del trader

El trader muestra varios casos donde el primer intento no funciona limpio. En
uno de ellos se sale porque el precio marea y no explota; mas tarde la accion
continua flagueando y acaba haciendo un movimiento grande. En otro, la operacion
falla el dia inicial pero funciona al dia siguiente.

La leccion humana no es perseguir todas las fallidas. Es no borrar
automaticamente un ticker si la estructura relevante no fue destruida.

### Lectura TSIS

Evento de fallo sin invalidacion:

```text
breakout attempt
-> no immediate follow-through
-> key invalidation not breached
-> structure remains alive
-> later expansion possible
```

Este evento separa fracaso operativo de destruccion estructural.

### Rol en lecturas compuestas

Rol principal:

```text
failed_attempt_event
not_invalidated_event
```

Estrategias/arquetipos donde puede aparecer:

- `Go ETB Go`;
- `Delayed Bull Flag Breakout`;
- `Post-Failure Continuation`;
- `Former Runner Continuation`;
- `Second Chance Breakout`.

Composicion didactica no operativa:

```text
Bull_Flag_Volume_Break_Event
+ Failed_Breakout_Not_Invalidated_Event
+ Delayed_Flag_Explosion_Event
```

Lectura humana:

```text
El primer intento no paga.
Pero la estructura no muere.
El ticker sigue en vigilancia.
```

### Observables futuros

- breakout_attempt_ts;
- follow_through_failure_flag;
- invalidation_level;
- invalidation_breached_flag;
- days_until_retry;
- liquidity_risk_flag;
- later_breakout_flag.

## 24. Buyer_Dominance_Range_Hold_Event

### Presentacion TSIS

Familia probable:

```text
LIQUIDITY_AND_SPREAD_STATE
SHORT_SQUEEZE_DYNAMICS
RESISTANCE_AND_BREAKOUTS
```

Fenomeno:

El precio aguanta un rango durante mucho tiempo, no rompe por abajo y sugiere
presencia compradora dominante. El trader lo describe como una accion que no
consigue bajar ni romper el rango porque hay un comprador fuerte.

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/025.png" width="760" alt="025 - Variables globales antes del rango">

<img src="source_assets/mosquito_smallcaps/img/026.jpg" width="760" alt="026 - Rango sostenido y comprador dominante">

### Texto del trader

En la variacion 6, el trader explica que la accion aguanta, consolida varias
veces y permanece por encima de una zona relevante. Dice que el patron necesita
"coccion": si se fuerza antes de tiempo puede no funcionar. Cuanto mas tiempo
evoluciona, mas participantes se involucran.

Al final, segun su lectura, despega porque no logra bajar ni romper el rango.
La interpretacion es que el lado comprador es mas fuerte que el vendedor.

### Lectura TSIS

Evento de dominancia compradora en rango:

```text
extended intraday range
-> repeated hold
-> downside failure
-> buyer dominance hypothesis
-> eventual expansion
```

No podemos afirmar la identidad del comprador. Solo documentamos que el precio
no pierde el rango pese al tiempo y los intentos de bajada.

### Rol en lecturas compuestas

Rol principal:

```text
absorption_event
range_hold_event
```

Estrategias/arquetipos donde puede aparecer:

- `Doble máximo`;
- `Range Cook Breakout`;
- `Liquidity Absorption`;
- `High Tight Range`;
- `Short Squeeze Continuation`.

Composicion didactica no operativa:

```text
Rectangle_Range_Volume_Break_Event
+ Buyer_Dominance_Range_Hold_Event
+ Whole_Dollar_Range_Cook_Breakout_Event
```

Lectura humana:

```text
El precio pasa tiempo suficiente en una zona.
No cae donde deberia caer.
La presion compradora parece dominar la estructura.
```

### Observables futuros

- range_hold_duration;
- failed_downside_breaks;
- range_low_defended_count;
- time_above_key_level;
- volume_absorption_proxy;
- whole_dollar_relation;
- eventual_breakout_flag.

## 25. Condiciones que no son eventos por si solas

### ETB / borrows

`Easy To Borrow` no es evento de precio. Puede modelarse como
`participant_access_context` si existe fuente de datos gobernada, porque cambia
la posibilidad de participacion short.

Por si solo no prueba que los shorts esten dentro ni que esten cubriendo.

### Catalyst / noticia

La noticia puede originar atencion y volumen, pero el evento TSIS debe separar:

```text
catalyst context
observable price/volume response
subsequent retention or failure
```

### Low float

Low float es una propiedad del instrumento, no una ocurrencia temporal. Puede
formar parte de un evento de contexto cuando aparece combinado con catalyst,
volumen y expansion. Por si solo es un amplificador de rango, fragilidad y
squeeze potencial.

### Stop, full size y anadir

Estos elementos pertenecen a Strategy Library, Execution Models o Decision
Models. Se conservan como contexto del trader, pero no deben entrar en una
definicion de evento.

## 26. Prioridad para futuras definiciones

Orden recomendado:

1. `Relative_Volume_Watchlist_Event`
2. `ETB_Borrow_Availability_Context_Event`
3. `Go_ETB_Go_Event`
4. `Double_Max_Short_Pressure_Event`
5. `Prior_High_Proximity_Open_Event`
6. `Whole_Dollar_Range_Cook_Breakout_Event`
7. `Bull_Flag_Volume_Break_Event`
8. `High_Hold_Short_Squeeze_Continuation_Event`
9. `Failed_Breakout_Not_Invalidated_Event`
10. `Buyer_Dominance_Range_Hold_Event`
11. `Multi_Day_Reactivation_Flag_Event`
12. `Mini_Stuffy_Rejection_Event`

La razon es practica: los dos primeros son condiciones de lectura que aparecen
en casi todos los playbooks del documento. Despues vienen los eventos compuestos
y las estructuras que permiten separar contexto, nivel, presion, fallo y
continuacion.

## 27. Regla final

Este documento conserva material fuente visual y textual.

La siguiente fase no es backtestear ni operar. La siguiente fase es elegir un
evento candidato y convertirlo en definicion draft formal dentro de la familia
correspondiente de Event Library.

