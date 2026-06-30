## 8. Prior_High_Open_Rebreak_Event

### Presentacion TSIS

Familia probable:

```text
RESISTANCE_AND_BREAKOUTS
MOMENTUM_EXPANSION
```

Fenomeno:

La accion abre extremadamente cerca del maximo del primer dia, o incluso lo
supera por poco. El nivel del maximo previo se convierte en el punto critico de
reactivacion.

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/003.png" width="760" alt="003 - Variables de entrada alrededor del maximo">

<img src="source_assets/mosquito_smallcaps/img/014.png" width="760" alt="014 - Maximo marcado como resistencia">

<img src="source_assets/mosquito_smallcaps/img/015.jpg" width="760" alt="015 - Rotura temprana del maximo">

### Texto del trader

El trader dice que si la accion abre superando el maximo del primer dia por
menos de un 1%, ese es un contexto agresivo. Si abre cerca del rango del segundo
dia, busca algo mas defensivo porque no es la entrada perfecta. Si esta cerca
del maximo del primer dia, se prepara para actuar con mas agresividad.

En el ejemplo ACB marca el maximo importante con una linea roja. Explica que
cuando rompe ese nivel el precio se dispara por acumulacion de compra y shorts
que deben cubrir. Tambien remarca que muchas veces esta ruptura ocurre muy
pronto, incluso en los primeros minutos, por lo que el trader discrecional debe
tener el nivel preparado.

### Lectura TSIS

El evento es:

```text
previous high identified
-> open near that high
-> immediate test/rebreak risk
-> high attention around level
```

No es "entrar al romper". La entrada es estrategia. El evento es la proximidad
operativa del precio a un nivel donde pueden activarse compradores, stops y
coberturas.

### Rol en lecturas compuestas

Rol principal:

```text
level_reactivation_event
```

Este evento identifica que el precio esta cerca de un maximo relevante. Es una
zona de atencion, no una orden. Puede ser importante porque muchos operadores
ven el mismo nivel y porque las coberturas, stops o nuevos compradores pueden
concentrarse ahi.

Estrategias/arquetipos donde puede aparecer:

- `Go ETB Go` del playbook fuente;
- `High of Day Breakout`;
- `Previous Day High Breakout`;
- `Opening Range Breakout`;
- `Gap and Go`.

Composicion didactica no operativa:

```text
Day1_Gain_Retention_Above_50_Event
+ Prior_High_Open_Rebreak_Event
+ High_Hold_Short_Squeeze_Continuation_Event
```

Lectura humana:

```text
El mercado no solo esta fuerte.
Esta fuerte justo debajo o encima de un nivel que muchos participantes miran.
```

La ruptura puede ser usada por estrategias futuras, pero el evento solo marca
la interaccion con el nivel.

### Observables futuros

- prior_high_level;
- open_to_prior_high_pct;
- minutes_to_rebreak;
- volume_at_rebreak;
- first_hour flag;
- gap relative to previous high;
- failure if rebreak does not hold.

## 9. Rectangle_Range_Volume_Break_Event

### Presentacion TSIS

Familia probable:

```text
RESISTANCE_AND_BREAKOUTS
LIQUIDITY_AND_SPREAD_STATE
```

Fenomeno:

Consolidacion intradia en rango rectangular, con resistencia superior clara,
soportes que se elevan o se mantienen firmes, y ruptura posterior con volumen.

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/004.jpg" width="760" alt="004 - Consolidacion del precio en rango">

<img src="source_assets/mosquito_smallcaps/img/026.jpg" width="760" alt="026 - Rango intradia sostenido antes del despegue">

### Texto del trader

El trader muestra un rango en velas de un minuto. Dice que tambien podria verse
en velas de cinco minutos, pero el principio es el mismo: el precio marca una
resistencia arriba, se apoya cada vez mas arriba y rompe con volumen.

Advierte que operar rectangulos en cualquier sitio no sirve. El rectangulo solo
tiene valor cuando aparece en momentos concretos y en acciones puntuales. La
dificultad no es reconocer la figura, sino encontrar el contexto correcto.

### Lectura TSIS

El evento no es el rectangulo aislado. Es:

```text
contexto small cap activo
-> rango intradia comprimido
-> soporte no destruido
-> resistencia clara
-> volumen aparece en ruptura
```

Este evento puede ser subestructura de Go ETB Go, doble maximo o coccion
intradia.

### Rol en lecturas compuestas

Rol principal:

```text
structure_event
```

Este evento describe una pausa organizada. Su valor no esta en el rectangulo
como dibujo, sino en que el precio deja de caer, acepta una zona y comprime
antes de una posible expansion.

Estrategias/arquetipos donde puede aparecer:

- `Go ETB Go` del playbook fuente;
- `Range Breakout`;
- `Opening Drive Consolidation Break`;
- `High Tight Range`;
- `Base Breakout`.

Composicion didactica no operativa:

```text
Low_Float_Catalyst_Volume_Extension_Event
+ Rectangle_Range_Volume_Break_Event
+ Prior_High_Open_Rebreak_Event
```

Lectura humana:

```text
La accion ya tiene contexto.
Luego deja de ser solo movimiento vertical y construye una zona.
Esa zona puede ser la plataforma de una ruptura posterior.
```

Una estrategia futura puede actuar sobre la ruptura del rango, pero este evento
solo describe la existencia y calidad de la estructura.

### Observables futuros

- range_duration_minutes;
- range_high;
- range_low;
- support_slope;
- number_of_touches;
- breakout_volume_ratio;
- breakout_close_above_range;
- VWAP relation.

## 10. Bull_Flag_Volume_Break_Event

### Presentacion TSIS

Familia probable:

```text
MOMENTUM_EXPANSION
RESISTANCE_AND_BREAKOUTS
```

Fenomeno:

Despues de una subida previa, la accion crea una mini consolidacion tipo
bandera. El precio apoya, no destruye el avance y rompe posteriormente con
volumen.

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/007.png" width="760" alt="007 - Banderita alcista intradia">

<img src="source_assets/mosquito_smallcaps/img/018.png" width="760" alt="018 - Banderita en diario con potencia compradora">

<img src="source_assets/mosquito_smallcaps/img/019.png" width="760" alt="019 - Dia 1, dia 2 consolida, dia 3 rompe">

<img src="source_assets/mosquito_smallcaps/img/024.jpg" width="760" alt="024 - Banderita perfecta">

### Texto del trader

El trader llama a esto "banderita". La describe como una mini consolidacion:
apoya una vez, vuelve a apoyar, y despues rompe con volumen. En otro ejemplo
explica que, aunque el precio este mas abajo, una vela que no marca ninguna
vela roja relevante puede indicar potencia compradora.

Tambien insiste en que muchas veces el trader discrecional intenta iniciar
antes de la ruptura porque, si espera a que rompa arriba sin patron, el riesgo
visual puede quedar demasiado lejos.

### Lectura TSIS

TSIS debe separar dos cosas:

```text
evento = bandera/aceptacion/ruptura con volumen
estrategia = anticipar, entrar en ruptura, anadir o gestionar stop
```

La bandera aparece repetidamente como subevento dentro de estructuras mayores:
Go ETB Go, reactivaciones multi-dia, doble maximo y delayed explosion.

### Rol en lecturas compuestas

Rol principal:

```text
structure_event
```

Este evento representa digestion ordenada despues de un impulso. No equivale a
"comprar bandera". La bandera solo dice que, despues de subir, el precio no ha
colapsado y esta generando una estructura de continuacion potencial.

Estrategias/arquetipos donde puede aparecer:

- `Go ETB Go` del playbook fuente;
- `Bull Flag Breakout`;
- `Flag Continuation`;
- `First Pullback Continuation`;
- `Multi-Day Runner Flag`.

Composicion didactica no operativa:

```text
Low_Float_Catalyst_Volume_Extension_Event
+ Day1_Gain_Retention_Above_50_Event
+ Bull_Flag_Volume_Break_Event
+ High_Hold_Short_Squeeze_Continuation_Event
```

Lectura humana:

```text
El precio ya hizo una expansion.
La pausa no destruye el movimiento.
La ruptura con volumen sugiere que la digestion termino.
```

La accion de anticipar, esperar ruptura o gestionar riesgo pertenece a
Strategy Library.

### Observables futuros

- prior_push_pct;
- flag_duration;
- flag_depth_pct;
- lower_highs / higher_lows;
- red_candle_absence or red_pressure_low;
- breakout_volume;
- breakout close quality;
- distance to prior high.

## 11. Double_Max_Short_Pressure_Event

### Presentacion TSIS

Familia probable:

```text
SHORT_SQUEEZE_DYNAMICS
RESISTANCE_AND_BREAKOUTS
```

Fenomeno:

La accion vuelve hacia una zona de maximos despues de haber mostrado volumen
alto. Durante el dia aguanta, consolida y no permite que los ataques bajistas
destruyan la estructura. El maximo se convierte en una zona de presion para
shorts.

Referencia fuente principal:

```text
PlayBook Pag. 3 - Doble máximo
```

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/006.jpg" width="760" alt="006 - Volumen relativamente alto y caso que se escapa">

<img src="source_assets/mosquito_smallcaps/img/008.jpg" width="760" alt="008 - Ataques bajistas que no rompen la estructura">

<img src="source_assets/mosquito_smallcaps/img/010.png" width="760" alt="010 - Consolidacion alta y salida de shorts">

### Texto del trader

El trader introduce el doble maximo desde un dia con volumen relativamente alto.
Dice que no hace falta complicarse: hay barras de volumen que son tan claras
que no hay que preguntarse si son altas. Cuando ve ese volumen, pasa la accion a
vigilancia.

Despues describe una accion que durante el dia consolida y empieza a irse a
maximos. Ve ataques bajistas, pero no baja. La interpretacion que da es
psicologica: si alguien va short y el precio no baja, se asusta; si rebota, se
asusta mas; si vuelve a anadir short y tampoco cae, queda mas cargado y con mas
presion.

Para el trader, al final del dia la clave es que los shorts no han podido
bajarla de ese nivel.

### Lectura TSIS

El evento es una presion acumulada alrededor de maximos:

```text
high relative volume day
-> intraday consolidation
-> failed bear attacks
-> return toward highs
-> short pressure hypothesis
```

El doble maximo no es solo una linea. Es una zona donde varios grupos de
participantes pueden quedar atrapados o forzados.

### Rol en lecturas compuestas

Rol principal:

```text
pressure_event
```

Este evento no dice que un doble maximo se deba operar. Dice que la zona de
maximos puede concentrar presion: compradores que defienden, shorts que atacan,
shorts que anaden y participantes que reaccionan al fallo de esos ataques.

Estrategias/arquetipos donde puede aparecer:

- `Doble máximo` del PlayBook Pag. 3 fuente;
- `Go ETB Go` del playbook fuente;
- `Double Top Breakout`;
- `Short Squeeze Continuation`;
- `High Retest Squeeze`;
- `Failed Breakdown Reversal`.

Composicion didactica no operativa:

```text
Rectangle_Range_Volume_Break_Event
+ Failed_Bear_Attack_Absorption_Event
+ Double_Max_Short_Pressure_Event
+ High_Hold_Short_Squeeze_Continuation_Event
```

Lectura humana:

```text
El precio vuelve a una zona donde los shorts esperaban rechazo.
Si no consigue caer, la presion cambia de lado.
```

La hipotesis short debe tratarse como mecanismo conductual pendiente de
evidencia, no como certeza.

### Observables futuros

- prior volume spike;
- high retest distance;
- failed downside attempts;
- intraday support defended;
- volume on retest;
- number of retests;
- close near highs;
- short-pressure proxy flags.

## 12. Failed_Bear_Attack_Absorption_Event

### Presentacion TSIS

Familia probable:

```text
SHORT_SQUEEZE_DYNAMICS
MOMENTUM_EXHAUSTION
```

Fenomeno:

Los vendedores o shorts intentan romper la estructura, pero el precio absorbe
los ataques y recupera repetidamente. La accion no baja donde "deberia" bajar
si la presion short tuviera control.

Referencia fuente principal:

```text
PlayBook Pag. 3 - Doble máximo
```

### Imagenes fuente

<img src="source_assets/mosquito_smallcaps/img/008.jpg" width="760" alt="008 - Fallo de ataques bajistas durante la consolidacion">

<img src="source_assets/mosquito_smallcaps/img/011.jpg" width="760" alt="011 - Detalle de rechazo y recuperacion">

### Texto del trader

El trader lo explica desde el lado short: el precio intenta bajar, vuelve a
rebotar, y quien esta corto se asusta. Si vuelve a intentar bajar y no puede,
queda todavia mas comprometido.

En sus palabras, la accion lleva toda la sesion aguantando y esta "llena de
shorts". Lo importante no es solo que el precio suba, sino que los intentos de
hundirla fracasan.

### Lectura TSIS

Evento de absorcion:

```text
downside attempt
-> no follow-through
-> rebound
-> repeated failure
-> pressure transfers to short side
```

No podemos afirmar cobertura short sin datos adicionales. Lo documentamos como
hipotesis conductual.

### Rol en lecturas compuestas

Rol principal:

```text
failure_event
pressure_event
```

Este evento marca que el lado vendedor intenta tomar control y falla. Es una
pieza clave en lecturas de squeeze porque el fallo visible puede cambiar la
percepcion de riesgo de los participantes cortos.

Estrategias/arquetipos donde puede aparecer:

- `Doble máximo` del PlayBook Pag. 3 fuente;
- `Go ETB Go` del playbook fuente;
- `Failed Breakdown`;
- `Bear Trap`;
- `Short Squeeze Continuation`;
- `Dip Reclaim`.

Composicion didactica no operativa:

```text
Double_Max_Short_Pressure_Event
+ Failed_Bear_Attack_Absorption_Event
+ High_Hold_Short_Squeeze_Continuation_Event
```

Lectura humana:

```text
Los vendedores tuvieron oportunidad de romper la estructura.
No lo consiguieron.
El fallo puede aumentar urgencia defensiva en el lado short.
```

El evento no prueba que todos los shorts cubran. Solo identifica el fallo de
presion bajista observable.

### Observables futuros

- downside attempt count;
- wick recovery;
- close location after attempt;
- support defense;
- volume on failed attack;
- time spent above defended zone;
- subsequent high retest.

