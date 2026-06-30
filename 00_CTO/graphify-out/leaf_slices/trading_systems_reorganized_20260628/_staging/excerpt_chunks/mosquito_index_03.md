## 13. High_Hold_Short_Squeeze_Continuation_Event

### Presentacion TSIS

Familia probable:

```text
SHORT_SQUEEZE_DYNAMICS
MOMENTUM_EXPANSION
```

Fenomeno:

Despues de marcar o romper maximos, el precio no se destruye. Consolida cerca
de la parte alta y prepara una nueva continuacion. El trader lo interpreta como
una zona donde shorts previos, shorts de venganza y longs nuevos conviven bajo
presion.

Referencia fuente principal:

```text
PlayBook Pag. 3 - Doble máximo
```

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/010.png" width="760" alt="010 - High hold y nueva salida de shorts">

<img src="source_assets/mosquito_smallcaps/img/015.jpg" width="760" alt="015 - Ruptura y posterior continuacion">

<img src="source_assets/mosquito_smallcaps/img/017.jpg" width="760" alt="017 - Fuerza de la rotura y segundo patron">

### Texto del trader

Despues de marcar maximo, a veces el precio no se va inmediatamente arriba.
Entonces, segun el trader, los shorts intentan un ultimo ataque bajista. Si no
pueden y la accion sigue aguantando maximos, aparece una consolidacion mucho
mas potente.

La razon conductual que propone es que ahi quedan atrapados varios grupos: los
que no salieron en el primer nivel, los que volvieron a entrar cabreados y los
que estan intentando defender el fallo. Por eso observa el volumen de la
primera salida de shorts, la segunda y la tercera.

### Lectura TSIS

Evento de continuacion por aceptacion en zona alta:

```text
break/retest high
-> no immediate collapse
-> high consolidation
-> renewed volume
-> squeeze continuation hypothesis
```

Este evento se relaciona con DAS y con futuros eventos de short squeeze, pero
no debe mezclarse con reglas de entrada.

### Rol en lecturas compuestas

Rol principal:

```text
impulse_event
pressure_event
```

Este evento aparece cuando el precio acepta la zona alta y vuelve a empujar.
Puede ser una fase posterior dentro de un squeeze: primero se expande, luego
no se destruye y despues reactiva con nuevo volumen.

Estrategias/arquetipos donde puede aparecer:

- `Doble máximo` del PlayBook Pag. 3 fuente;
- `Go ETB Go` del playbook fuente;
- `DAS` / `Dips After Squeeze`;
- `Short Squeeze Continuation`;
- `High Hold Continuation`;
- `Breakout Pullback Continuation`.

Composicion didactica no operativa:

```text
Low_Float_Catalyst_Volume_Extension_Event
+ Failed_Bear_Attack_Absorption_Event
+ High_Hold_Short_Squeeze_Continuation_Event
```

Lectura humana:

```text
El precio ya mostro fuerza.
El retroceso o pausa no destruye la zona alta.
La reactivacion puede forzar cobertura o nueva persecucion compradora.
```

La seleccion del dip, ruptura o vela exacta pertenece a estrategia, no al
evento.

### Observables futuros

- high_hold_duration;
- distance from high;
- consolidation range near high;
- breakout volume sequence;
- number of continuation pushes;
- pullback depth;
- halt risk if expansion accelerates.

## 14. Mini_Stuffy_Rejection_Event

### Presentacion TSIS

Familia probable:

```text
INTRADAY_REVERSALS
SHORT_SQUEEZE_DYNAMICS
```

Fenomeno:

Una vela o microsecuencia intenta bajar durante la ruptura o al final de una
consolidacion, pero recupera rapidamente y termina fuerte. El trader lo llama
mini-stuffy move.

Referencia fuente principal:

```text
PlayBook Pag. 3 - Doble máximo
```

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/011.jpg" width="760" alt="011 - Mini-stuffy move en ruptura">

### Texto del trader

El trader dice que en la ultima vela que rompe la consolidacion se puede ver un
mini-stuffy move: la vela baja para abajo y vuelve a subir. Su lectura es que
los shorts intentan darle otra vez y no pueden.

Despues de esa recuperacion, afirma que muchas veces el trade se va hacia
arriba realizando un short squeeze.

### Lectura TSIS

Este evento es muy local y probablemente requiere 1m o incluso tape:

```text
downward stab
-> fast recovery
-> close strong
-> continuation pressure
```

No debe definirse como "comprar mecha". La mecha es evidencia visual del
fenomeno de rechazo.

### Rol en lecturas compuestas

Rol principal:

```text
micro_failure_event
```

Este evento es una version muy local de fallo bajista. Puede servir como
detalle dentro de una estructura mayor, pero por si solo es demasiado pequeno
para gobernar una lectura completa del mercado.

Estrategias/arquetipos donde puede aparecer:

- `Doble máximo` del PlayBook Pag. 3 fuente;
- `Go ETB Go` del playbook fuente;
- `DAS` / `Dips After Squeeze`;
- `Failed Stuff Move`;
- `Micro Pullback Reclaim`;
- `Tape Reclaim`.

Composicion didactica no operativa:

```text
High_Hold_Short_Squeeze_Continuation_Event
+ Mini_Stuffy_Rejection_Event
+ continuation_push
```

Lectura humana:

```text
El lado vendedor intenta romper una vela o microzona.
El precio recupera rapido.
Esa recuperacion puede ser evidencia de que la presion bajista fallo.
```

Este evento probablemente necesitara revision visual o datos de tape antes de
pasar a detector_candidate.

### Observables futuros

- lower wick ratio;
- recovery speed;
- close location in candle;
- volume spike;
- relation to consolidation high;
- follow-through over next N minutes.

## 15. Dead_Stock_Reactivation_High_Event

### Presentacion TSIS

Familia probable:

```text
RUNNER_LIFECYCLE
MOMENTUM_EXPANSION
```

Fenomeno:

Una accion que venia muerta, aplastada o en rojo durante varios dias marca un
nuevo maximo relativo con volumen y obliga a reconsiderar su estado.

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/012.png" width="760" alt="012 - Accion aplastada que marca maximo">

<img src="source_assets/mosquito_smallcaps/img/016.png" width="760" alt="016 - Reactivacion despues de caida de varios dias">

### Texto del trader

El trader muestra una accion que estaba muerta: varios dias aplastada y en
rojo. De repente marca maximo despues de esa secuencia bajista. Su reaccion no
es operar automaticamente, sino plantearsela y observar como reacciona.

Si posteriormente da una banderita o patron de continuacion, entonces la
reactivacion puede pasar a ser interesante.

### Lectura TSIS

Evento de cambio de estado:

```text
multi-day weakness
-> first relative high / volume response
-> reactivation watch state
```

Este evento puede alimentar reactivaciones, banderas o dobles maximos, pero por
si solo solo marca que el activo despierta.

### Rol en lecturas compuestas

Rol principal:

```text
state_change_event
```

Este evento marca un cambio de estado: de ticker olvidado o vendido a ticker
que vuelve a mostrar atencion. No significa que la estructura ya sea operable.

Estrategias/arquetipos donde puede aparecer:

- `Dead Cat Bounce`;
- `First Green Day`;
- `Multi-Day Reactivation`;
- `Former Runner Reactivation`;
- `Volume Reclaim`.

Composicion didactica no operativa:

```text
Dead_Stock_Reactivation_High_Event
+ Multi_Day_Reactivation_Flag_Event
+ Bull_Flag_Volume_Break_Event
```

Lectura humana:

```text
El activo parecia muerto.
De pronto vuelve a marcar un maximo relativo con volumen.
Eso lo devuelve al radar, pero todavia necesita estructura.
```

La reactivacion es una alerta contextual, no una senal.

### Observables futuros

- days_down_or_flat;
- relative low compression;
- first higher high;
- reactivation volume;
- close above recent range;
- catalyst or sector attention.

## 16. Multi_Day_Reactivation_Flag_Event

### Presentacion TSIS

Familia probable:

```text
RUNNER_LIFECYCLE
MOMENTUM_EXPANSION
RESISTANCE_AND_BREAKOUTS
```

Fenomeno:

El caso ideal de retencion no se cumple perfectamente, pero aparece un nuevo
repico con volumen que reactiva el seguimiento. Luego se forma una bandera o
consolidacion multi-dia y una ruptura posterior.

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/016.png" width="760" alt="016 - Segundo patron reactiva el seguimiento">

<img src="source_assets/mosquito_smallcaps/img/017.jpg" width="760" alt="017 - Ruptura posterior parabolica">

<img src="source_assets/mosquito_smallcaps/img/018.png" width="760" alt="018 - Banderita de reactivacion">

<img src="source_assets/mosquito_smallcaps/img/023.jpg" width="760" alt="023 - Operacion fallida que funciona despues">

### Texto del trader

El trader explica una variacion: el segundo dia no aguanta el 50% ideal y la
accion baja durante varios dias. Pero aparece un nuevo repico con volumen
relativamente alto. Eso le plantea que la operacion se reactiva.

Reconoce que no es tan buena como la estructura ideal, pero si despues aparece
un patron excelente, quiere vigilarla. En sus ejemplos, esa reactivacion puede
dar una banderita durante varios dias y luego romper con fuerza.

### Lectura TSIS

Este evento separa el patron ideal de una segunda oportunidad:

```text
initial event weakens
-> not fully dead
-> new volume repop
-> multi-day flag
-> reactivation breakout
```

Es importante porque evita descartar automaticamente un ticker solo porque no
cumplio la retencion perfecta.

### Rol en lecturas compuestas

Rol principal:

```text
reactivation_structure_event
```

Este evento representa una segunda vida. La primera secuencia pudo fallar o no
ser ideal, pero el activo vuelve a mostrar volumen y construye una nueva
estructura.

Estrategias/arquetipos donde puede aparecer:

- `Go ETB Go` como variante no ideal;
- `Multi-Day Flag Breakout`;
- `Former Runner Second Leg`;
- `Delayed Continuation`;
- `Reactivation Breakout`.

Composicion didactica no operativa:

```text
Dead_Stock_Reactivation_High_Event
+ Multi_Day_Reactivation_Flag_Event
+ Delayed_Flag_Explosion_Event
```

Lectura humana:

```text
La primera oportunidad no limpio el camino.
Pero el ticker vuelve a atraer volumen.
Si construye una bandera y rompe, la secuencia se reactiva.
```

Esto permite mantener memoria de ticker sin transformar la vigilancia en
estrategia.

### Observables futuros

- initial failure depth;
- days_since_initial_event;
- reactivation volume;
- new high / lower high;
- flag duration;
- breakout over reactivation high;
- outcome by reactivation index.

## 17. Delayed_Flag_Explosion_Event

### Presentacion TSIS

Familia probable:

```text
RESISTANCE_AND_BREAKOUTS
RUNNER_LIFECYCLE
```

Fenomeno:

La accion forma una bandera o rango, pero no explota inmediatamente. Se queda
uno o dos dias parada, flotando o controlada, sin destruir la estructura, y
finalmente rompe con un movimiento amplio.

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/021.png" width="760" alt="021 - Dos dias de espera antes de explosion">

<img src="source_assets/mosquito_smallcaps/img/022.jpg" width="760" alt="022 - Flaguea y explota despues">

<img src="source_assets/mosquito_smallcaps/img/024.jpg" width="760" alt="024 - Banderita perfecta despues de fallo">

### Texto del trader

El trader muestra una variante complicada. La accion tiene volumen alto, forma
la banderita y rompe mas tarde, pero estuvo dos dias parada. Dice que no pudo
aguantarla porque estuvo flotando y controlada antes de explotar.

En otro ejemplo, una operacion falla ese dia, pero al dia siguiente funciona. El
trader insiste en que no hay que dejar de vigilar automaticamente una accion
cuando el primer intento no sale limpio.

### Lectura TSIS

Evento de digestion prolongada:

```text
setup appears
-> no immediate follow-through
-> structure not invalidated
-> multi-day float/control
-> delayed expansion
```

Este evento es distinto de la bandera rapida. El tiempo de espera es parte del
fenomeno.

### Rol en lecturas compuestas

Rol principal:

```text
delayed_structure_event
```

Este evento explica que no toda continuacion ocurre en la primera ruptura. A
veces la estructura necesita varios dias de digestion antes de expandir.

Estrategias/arquetipos donde puede aparecer:

- `Delayed Bull Flag Breakout`;
- `Multi-Day Flag Breakout`;
- `Post-Failure Continuation`;
- `Range Expansion After Compression`;
- `Former Runner Continuation`.

Composicion didactica no operativa:

```text
Bull_Flag_Volume_Break_Event
+ failed_initial_follow_through
+ Delayed_Flag_Explosion_Event
```

Lectura humana:

```text
El patron aparece.
No explota enseguida.
Pero tampoco invalida.
La compresion temporal termina en expansion posterior.
```

El evento protege una idea importante: fallo inmediato no siempre equivale a
evento muerto.

### Observables futuros

- days_in_flag;
- invalidation not breached;
- volume compression;
- range narrowing;
- delayed breakout;
- post-failure watchlist persistence;
- liquidity risk flags.

