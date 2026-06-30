# Mosquito Small Caps Source Event Index v0.1

Fecha: 2026-06-21
Estado: `source_note` estructurado para Event Library.

Fuente externa:

```text
C:\Users\AlexJ\Desktop\01_tools\asrtool\00_projects\SmallCaps_mosquito\La-Formula-Exacta-para-Entrar-en-Trades_Media_4Xh34AFFGJc_001_1080p_pdf.md
```

Imagenes copiadas al repo:

```text
source_assets/mosquito_smallcaps/img/
```

Documento fuente copiado al repo:

```text
source_assets/mosquito_smallcaps/La-Formula-Exacta-para-Entrar-en-Trades_Media_4Xh34AFFGJc_001_1080p_pdf.md
```

## 1. Proposito

Este documento convierte material discrecional de un trader en un inventario
visual de eventos candidatos para TSIS.

El trader explica entradas, stops, size y gestion. TSIS debe leer ese material
de otra forma:

```text
setup discrecional -> fenomeno observable de mercado
entrada             -> punto visual donde el fenomeno se hace evidente
stop                -> zona de invalidacion percibida por el trader
size                -> confianza operacional, no parte del evento
```

Este documento no promueve eventos. No define detectores. No autoriza
estrategias. Su funcion es preservar el contexto visual y textual que luego
usaremos para crear definiciones formales en Event Library.

## 2. Estrategias/playbooks como composicion de eventos

El documento fuente esta escrito como playbook discrecional. En especial,
presenta al menos dos marcos didacticos:

```text
Playbook pag. 2: Go ETB Go
PlayBook Pag. 3 - Doble máximo
```

TSIS no debe copiar esos playbooks como estrategias dentro de Event Library.
La lectura correcta es descomponerlos en fenomenos observables.

Una estrategia humana puede mezclar:

```text
contexto
+ estructura
+ presion de participantes
+ ruptura
+ invalidacion
+ decision operativa
```

Event Library solo conserva las primeras piezas como eventos o condiciones
observables. La decision operativa pertenece a Strategy Library o capas
posteriores.

Ejemplo didactico:

```text
Estrategia humana: Go ETB Go

Puede descomponerse en:

context_event:
  Low_Float_Catalyst_Volume_Extension_Event

retention_event:
  Day1_Gain_Retention_Above_50_Event

structure_event:
  Bull_Flag_Volume_Break_Event
  Rectangle_Range_Volume_Break_Event
  Prior_High_Open_Rebreak_Event

pressure_event:
  Double_Max_Short_Pressure_Event
  Failed_Bear_Attack_Absorption_Event
  High_Hold_Short_Squeeze_Continuation_Event
```

Otro ejemplo didactico:

```text
Estrategia humana: Doble máximo

Puede descomponerse en:

context_event:
  Low_Float_Catalyst_Volume_Extension_Event

level_event:
  Prior_High_Open_Rebreak_Event

structure_event:
  Rectangle_Range_Volume_Break_Event
  Bull_Flag_Volume_Break_Event

pressure_event:
  Double_Max_Short_Pressure_Event
  Failed_Bear_Attack_Absorption_Event

continuation_event:
  High_Hold_Short_Squeeze_Continuation_Event
  Mini_Stuffy_Rejection_Event
```

Esta composicion no es una regla de trading. Solo ayuda al lector humano a
entender que un evento aislado puede ser una pieza de una situacion mas amplia.

Regla:

```text
Evento aislado = fenomeno observable.
Conjunto de eventos = lectura compuesta del mercado.
Estrategia = lectura compuesta + decision operativa.
```

Por tanto, cuando este documento diga que un evento puede aparecer dentro de
`Go ETB Go`, `Doble máximo`, `Gap and Go`, `Bull Flag Breakout`,
`High Day Breakout`, `Short Squeeze Continuation` u otro arquetipo conocido,
eso no significa que TSIS este definiendo esa estrategia. Significa que el
evento es una pieza observable que esos marcos discrecionales suelen usar.

## 3. Regla de lectura

Cada bloque tiene esta estructura:

1. `Presentacion TSIS`: nombre candidato del evento y lectura como fenomeno.
2. `Imagenes fuente`: graficos o slides que sustentan la idea.
3. `Texto del trader`: explicacion limpia y contextualizada desde el documento
   fuente. Mantiene el sentido original, pero corrige ruido de transcripcion.
4. `Lectura TSIS`: traduccion del lenguaje discrecional a evento observable.
5. `Rol en lecturas compuestas`: estrategias/arquetipos donde puede aparecer
   y conjunto de eventos que podria integrar.
6. `Observables futuros`: posibles campos o condiciones para una definicion
   draft posterior.

Cuando el texto hable de comprar, entrar, stop, full size o salir, esas partes
se conservan como contexto humano, pero no forman parte del evento.

## 4. Eventos candidatos identificados

1. [`Low_Float_Catalyst_Volume_Extension_Event`](#5-low_float_catalyst_volume_extension_event): evento de extension por catalizador, bajo float y volumen creciente.
2. [`Day1_Gain_Retention_Above_50_Event`](#6-day1_gain_retention_above_50_event): evento de retencion significativa despues de una primera expansion.
3. [`Go_ETB_Go_Event`](#7-go_etb_go_event): evento compuesto de expansion, pausa, disponibilidad short y reactivacion.
4. [`Prior_High_Open_Rebreak_Event`](#8-prior_high_open_rebreak_event): evento de ruptura o reactivacion del maximo previo tras apertura cercana.
5. [`Rectangle_Range_Volume_Break_Event`](#9-rectangle_range_volume_break_event): evento de rango rectangular intradia que rompe con volumen.
6. [`Bull_Flag_Volume_Break_Event`](#10-bull_flag_volume_break_event): evento de bandera alcista que digiere el impulso y rompe con volumen.
7. [`Double_Max_Short_Pressure_Event`](#11-double_max_short_pressure_event): evento de presion short alrededor de una zona de doble maximo.
8. [`Failed_Bear_Attack_Absorption_Event`](#12-failed_bear_attack_absorption_event): evento de ataques bajistas fallidos y absorcion de venta.
9. [`High_Hold_Short_Squeeze_Continuation_Event`](#13-high_hold_short_squeeze_continuation_event): evento de aceptacion en zona alta y continuacion tipo squeeze.
10. [`Mini_Stuffy_Rejection_Event`](#14-mini_stuffy_rejection_event): evento micro de rechazo bajista rapido dentro de una ruptura o consolidacion.
11. [`Dead_Stock_Reactivation_High_Event`](#15-dead_stock_reactivation_high_event): evento de reactivacion de una accion apagada que vuelve a marcar maximos relativos.
12. [`Multi_Day_Reactivation_Flag_Event`](#16-multi_day_reactivation_flag_event): evento de reactivacion multi-dia con bandera o consolidacion posterior.
13. [`Delayed_Flag_Explosion_Event`](#17-delayed_flag_explosion_event): evento de bandera que no explota de inmediato pero mantiene estructura y rompe mas tarde.
14. [`Whole_Dollar_Range_Cook_Breakout_Event`](#18-whole_dollar_range_cook_breakout_event): evento de rango cocinado alrededor de nivel psicologico y ruptura posterior.
15. [`Relative_Volume_Watchlist_Event`](#19-relative_volume_watchlist_event): evento de activacion de vigilancia por volumen relativo claramente anomalo.
16. [`ETB_Borrow_Availability_Context_Event`](#20-etb_borrow_availability_context_event): evento de contexto por disponibilidad de borrows y participacion short posible.
17. [`Two_Day_Initial_Extension_As_One_Event`](#21-two_day_initial_extension_as_one_event): evento de extension inicial repartida en dos sesiones pero leida como una sola fase.
18. [`Prior_High_Proximity_Open_Event`](#22-prior_high_proximity_open_event): evento de apertura muy cercana al maximo relevante previo.
19. [`Failed_Breakout_Not_Invalidated_Event`](#23-failed_breakout_not_invalidated_event): evento de ruptura fallida que no invalida la estructura mayor.
20. [`Buyer_Dominance_Range_Hold_Event`](#24-buyer_dominance_range_hold_event): evento de rango sostenido donde el lado comprador domina e impide la ruptura bajista.

Relacion inicial con los playbooks fuente:

```text
Playbook pag. 2: Go ETB Go
  Low_Float_Catalyst_Volume_Extension_Event
  Relative_Volume_Watchlist_Event
  ETB_Borrow_Availability_Context_Event
  Day1_Gain_Retention_Above_50_Event
  Go_ETB_Go_Event
  Two_Day_Initial_Extension_As_One_Event
  Prior_High_Proximity_Open_Event
  Prior_High_Open_Rebreak_Event
  Rectangle_Range_Volume_Break_Event
  Bull_Flag_Volume_Break_Event
  Failed_Breakout_Not_Invalidated_Event

PlayBook Pag. 3 - Doble máximo
  Relative_Volume_Watchlist_Event
  ETB_Borrow_Availability_Context_Event
  Double_Max_Short_Pressure_Event
  Failed_Bear_Attack_Absorption_Event
  High_Hold_Short_Squeeze_Continuation_Event
  Mini_Stuffy_Rejection_Event
  Buyer_Dominance_Range_Hold_Event
```

Esta relacion no es exclusiva. Un mismo evento puede aparecer en varios
playbooks o arquetipos, porque Event Library clasifica fenomenos observables,
no recetas operativas.

## 5. Low_Float_Catalyst_Volume_Extension_Event

### Presentacion TSIS

Familia probable:

```text
MOMENTUM_EXPANSION
CATALYST_AND_ATTENTION
```

Fenomeno:

Una small cap o microcap de bajo float se expande con volumen relativo alto,
normalmente asociada a noticia o catalyst, y produce una subida inicial
material pero no absurda para el marco que el trader quiere estudiar.

Este evento no es Go ETB Go completo. Es la condicion inicial: la accion entra
en un estado de atencion, rango y volatilidad suficiente para que luego puedan
aparecer eventos de retencion, rebreak, squeeze o bandera.

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/001.png" width="760" alt="001 - Identificacion y caracteristicas del trade">

<img src="source_assets/mosquito_smallcaps/img/013.png" width="760" alt="013 - Ejemplo diario de extension por sector/catalyst">

### Texto del trader

El trader empieza definiendo el universo y el contexto. Busca acciones low
float, preferiblemente con menos de 10 millones de acciones en circulacion, y
descarta normalmente floats por encima de 30 o 40 millones salvo que el free
float efectivo sea mucho menor.

La razon que da es directa: con pocas acciones disponibles es mas facil que el
precio tenga rango. Lo que busca es volatilidad; si una empresa no se mueve, no
hay oportunidad. Para este marco no quiere cualquier movimiento: quiere que la
accion suba con volumen relativo alto, que haya una noticia de la accion o del
sector, y que la subida no sea irracional. El rango que menciona como deseable
para el primer dia esta aproximadamente entre 20% y 100%.

Tambien introduce una restriccion importante: si la subida viene de algo que
distorsiona demasiado la referencia, como ciertos splits o gaps extremos que
colocan el precio en una zona sin recorrido razonable, ya no lo considera el
mismo tipo de operativa.

### Lectura TSIS

Este bloque define un evento de expansion inicial con contexto:

```text
low float
-> catalyst/attention
-> volumen relativo alto
-> subida material
-> rango suficiente para research posterior
```

No debe confundirse con estrategia. La accion todavia no ha demostrado que
retenga el avance ni que los shorts esten atrapados. Solo ha generado la
primera condicion de interes.

### Rol en lecturas compuestas

Rol principal:

```text
context_event
```

Este evento no es una razon suficiente para actuar. Solo dice que el ticker
entro en un entorno donde pueden aparecer eventos posteriores de estructura,
presion short o continuacion.

Estrategias/arquetipos donde puede aparecer:

- `Go ETB Go` del playbook fuente;
- `Gap and Go`;
- `Low Float Momentum`;
- `First Green Day`;
- `Small Cap News Runner`.

Composicion didactica no operativa:

```text
Low_Float_Catalyst_Volume_Extension_Event
+ Day1_Gain_Retention_Above_50_Event
+ Prior_High_Open_Rebreak_Event
+ High_Hold_Short_Squeeze_Continuation_Event
```

Lectura humana:

```text
El activo tiene contexto de atencion y volatilidad.
Luego habra que ver si retiene, estructura y reactiva.
```

La accion operativa no pertenece a este evento.

### Observables futuros

- float o free-float proxy;
- gap o subida intradia/daily;
- volumen relativo;
- dollar volume;
- presencia de news/catalyst;
- tipo de catalyst;
- split/reverse split proximity;
- precio previo y recorrido left-side;
- borrow/ETB context como feature, no como evento.

## 6. Day1_Gain_Retention_Above_50_Event

### Presentacion TSIS

Familia probable:

```text
RUNNER_LIFECYCLE
MOMENTUM_EXPANSION
```

Fenomeno:

Despues de una sesion de expansion, el precio no devuelve mas de una parte
critica de la subida. El trader usa como referencia que aguante alrededor del
50% o mas de la ganancia.

La lectura importante es que el avance no se destruye. El mercado acepta una
parte relevante del nuevo precio.

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/002.png" width="760" alt="002 - Seguimiento al dia siguiente">

<img src="source_assets/mosquito_smallcaps/img/019.png" width="760" alt="019 - Dia 1 volumen, dia 2 consolida, dia 3 rompe">

### Texto del trader

El trader explica que al dia siguiente mira si la accion sigue aguantando el
50% o mas de la ganancia y si continua. Si mantiene esos niveles, revisa de
nuevo los borrows y acerca el chart a una pantalla principal.

La interpretacion humana es clara: si el precio sigue aguantando, los shorts no
han tenido suficiente fuerza para hundirla. Para el trader eso es una buena
senal para buscar continuacion long mas adelante.

Tambien aclara que el 50% no debe leerse de forma mecanica exacta. Si baja un
52%, no significa automaticamente que el fenomeno desaparezca. Lo relevante es
la idea de retencion significativa.

### Lectura TSIS

Evento de aceptacion post-expansion:

```text
day 1 expansion
-> day 2 pullback/consolidation
-> retention >= approximate threshold
-> no full destruction of advance
```

Esto no dice comprar. Solo dice que la subida previa sigue viva y que la
presion vendedora no ha dominado.

### Rol en lecturas compuestas

Rol principal:

```text
retention_event
```

Este evento mide si el mercado acepta parte relevante de la expansion inicial.
No dice que haya que entrar; solo indica que el movimiento no ha sido destruido
por completo.

Estrategias/arquetipos donde puede aparecer:

- `Go ETB Go` del playbook fuente;
- `Go Pause Go`;
- `First Green Day Continuation`;
- `Multi-Day Runner Continuation`;
- `Dip Hold Continuation`.

Composicion didactica no operativa:

```text
Low_Float_Catalyst_Volume_Extension_Event
+ Day1_Gain_Retention_Above_50_Event
+ Bull_Flag_Volume_Break_Event
```

Lectura humana:

```text
Hubo expansion.
El precio no la devuelve entera.
Eso deja vivo el escenario para buscar estructuras posteriores.
```

La retencion es contexto de supervivencia del movimiento, no una entrada.

### Observables futuros

- day1 high, low, close;
- day1 gain percent;
- day2 low relative to day1 move;
- retained_gain_pct;
- close retention;
- intraday support zones;
- volume fade or persistence;
- borrow/ETB availability as context.

## 7. Go_ETB_Go_Event

### Presentacion TSIS

Familia probable:

```text
SHORT_SQUEEZE_DYNAMICS
MOMENTUM_EXPANSION
RUNNER_LIFECYCLE
```

Fenomeno:

Secuencia multi-dia en una accion easy-to-borrow que primero se expande,
despues pausa o consolida sin destruir la estructura, y finalmente vuelve a
activar el maximo o la zona de ruptura.

El componente ETB importa porque permite que haya participacion short amplia.
Si esos shorts entran y el precio no cae, la siguiente ruptura puede tener mas
presion de cobertura.

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/001.png" width="760" alt="001 - Criterios Go ETB Go">

<img src="source_assets/mosquito_smallcaps/img/002.png" width="760" alt="002 - Seguimiento Go ETB Go">

<img src="source_assets/mosquito_smallcaps/img/003.png" width="760" alt="003 - Variables en la entrada">

<img src="source_assets/mosquito_smallcaps/img/015.jpg" width="760" alt="015 - Rotura de maximo en ejemplo ACB">

### Texto del trader

El trader presenta Go ETB Go como una variante de Go Pause Go: movimiento
alcista, consolidacion pequena y otra tirada. Aclara que no basta con ver una
figura tecnica. Hay que anadir capas: volumen, level 2, times and sales,
mercado, borrows y contexto.

El stock debe tener borrows. Si es easy to borrow, mejor que si hay que pagar
caro para ponerse corto. Si no hay acciones para short, practicamente descarta
esta operativa, porque parte de la dinamica que busca depende de que haya
participantes short involucrados.

El proceso descrito es:

```text
dia 1: subida con volumen y catalyst;
dia 2: seguimiento, retencion y borrows;
dia 3: accion pasa de observacion a posible activacion si aparece patron.
```

### Lectura TSIS

Go ETB Go debe definirse como evento compuesto, no como una entrada. Sus piezas
son:

```text
low float/catalyst expansion
-> gain retention
-> ETB/borrow context
-> maximo relevante marcado
-> consolidacion o pausa
-> reactivacion/ruptura
```

El nombre del trader contiene una decision operacional, pero TSIS conserva solo
el fenomeno observable.

### Rol en lecturas compuestas

Rol principal:

```text
composite_source_pattern
```

`Go_ETB_Go_Event` es especial dentro de este documento porque viene casi como
una estrategia/playbook completo. TSIS lo conserva como fuente didactica, pero
lo descompone en eventos mas pequenos para evitar mezclar fenomeno y decision.

Referencia fuente:

```text
Playbook pag. 2: Go ETB Go
```

Descomposicion didactica no operativa:

```text
context_event:
  Low_Float_Catalyst_Volume_Extension_Event

retention_event:
  Day1_Gain_Retention_Above_50_Event

structure_event:
  Rectangle_Range_Volume_Break_Event
  Bull_Flag_Volume_Break_Event
  Prior_High_Open_Rebreak_Event

pressure_event:
  Double_Max_Short_Pressure_Event
  Failed_Bear_Attack_Absorption_Event
  High_Hold_Short_Squeeze_Continuation_Event
```

Lectura humana:

```text
Una accion con borrows disponibles atrae shorts.
Si se expande, pausa y no cae, esos shorts pueden quedar presionados.
Si despues rompe un nivel importante, la presion puede acelerar el movimiento.
```

Esto no define entrada, stop, target ni size. Solo preserva la composicion de
eventos que el playbook discrecional esta usando.

### Observables futuros

- event_day_index;
- day1 expansion percent;
- retained_gain_pct;
- ETB/borrow proxy;
- max_level_source;
- days_since_initial_extension;
- rebreak distance;
- volume_on_rebreak;
- short-pressure mechanism hypothesis flag.

