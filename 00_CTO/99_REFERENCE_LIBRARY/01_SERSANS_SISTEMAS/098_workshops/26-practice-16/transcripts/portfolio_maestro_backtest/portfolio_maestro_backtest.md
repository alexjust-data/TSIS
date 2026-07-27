# Backtest Strategies Against Groups of Symbols Using Portfolio Maestro  September 26, 2023

## 00:00 - 00:04
Buenas tardes, todos. Bienvenidos a la clasa master de TradeStation.

## 00:04 - 00:10
Mi nombre es Jesús Nava, Soy el Director de la Client Trending e Educación para los securidades de TradeStation.

## 00:10 - 00:14
Para mí siempre es un placer unirme a todos y hablar un poco sobre TradeStation.

## 00:14 - 00:18
Hoy vamos a hacer una serie de TradeSt rotations en las que destacamos

## 00:18 - 00:23
ciertas características de desarrollo estratégico de la plataforma TradeStation.

## 00:23 - 00:28
Hoy vamos a hablar sobre la magia de Portfolio y vamos a entrar en eso en un momento

## 00:28 - 00:31
y las razones por las que queréis usarlo.

## 00:31 - 00:33
Antes de comenzar, aquí están las discusiones usuales.

## 00:33 - 00:35
Recuerden que cada símbolo y idea

## 00:35 - 00:37
que hablamos en esta presentación

## 00:37 - 00:40
es para propósitos educativos.

## 00:40 - 00:42
Estas no son recomendaciones de TradeStation.

## 00:42 - 00:45
Además, que el trading activo no es apto para todos

## 00:45 - 00:50
y que la performance histórica no garantiza resultados futuros.

## 00:50 - 00:53
Para más información sobre estas discusiones,

## 00:53 - 00:56
visiten www.tradestation.com

## 00:56 - 01:00
o en forward slash important dash information.

## 01:00 - 01:01
También tenemos algunas discusiones adicionales

## 01:01 - 01:03
en el fondo de la pantalla.

## 01:03 - 01:07
Y Manolo también ha compartido un enlace en el chat

## 01:07 - 01:09
para quien quiera un poco más de detalle.

## 01:09 - 01:13
Bien, vamos a ir a la plataforma de TradeStation

## 01:13 - 01:16
y hablar de este tool interesante

## 01:16 - 01:19
que está disponible como aplicación

## 01:19 - 01:21
dentro de la plataforma de TradeStation.

## 01:21 - 01:25
Antes de ir a Portfolio Maestro

## 01:25 - 01:27
y por qué queréis usarlo,

## 01:27 - 01:29
vamos a establecer nuestra análisis de cartas

## 01:29 - 01:32
con una estrategia, solo una idea,

## 01:32 - 01:35
para que podamos empezar usando esa idea

## 01:35 - 01:40
y transferir esa estrategia a Portfolio Maestro.

## 01:40 - 01:47
Así que creo que si has estado en una de mis clases de maestro,

## 01:47 - 01:51
ya sabes que encuentro la estrategia de desarrollo

## 01:51 - 01:53
y estrategia de trade un tema fascinante

## 01:53 - 01:56
y estoy seguro de que ustedes van a disfrutar de esto también.

## 01:56 - 01:59
Voy a ir aquí a estudios y agregar una de las estrategias

## 01:59 - 02:04
construidas que son parte de la plataforma de TradeStation.

## 02:04 - 02:06
Estudios y estrategias.

## 02:06 - 02:11
Voy a empezar con MACD.

## 02:11 - 02:13
Creo que es una estrategia que he usado

## 02:13 - 02:17
en muchos de mis ejemplos anteriores.

## 02:17 - 02:34
Voy a

## 02:34 - 02:38
entrar en el mercado cuando el MACD genera una entrada larga,

## 02:38 - 02:43
pero voy a combinar eso con un truco ATR.

## 02:43 - 02:46
A pesar de lo volatil que ha sido el mercado

## 02:46 - 02:49
o de lo grande que están obteniendo las barras,

## 02:49 - 02:53
cada símbolo tendrá un truco adaptable

## 02:53 - 02:55
a base de su volatilidad.

## 02:55 - 03:00
A veces usamos el ATR como medida de movimiento de precio,

## 03:00 - 03:04
así que hace sentido introducir

## 03:04 - 03:06
algunas de esas calculaciones en nuestra estrategia

## 03:06 - 03:09
porque entonces estamos haciendo la estrategia

## 03:09 - 03:11
que sea más sensible a lo que el mercado está haciendo

## 03:11 - 03:14
en un momento particular.

## 03:14 - 03:16
Y en este ejemplo particular,

## 03:16 - 03:20
hace más sentido porque quiero que la estrategia

## 03:20 - 03:23
también sea aplicada a múltiples símbolos.

## 03:23 - 03:28
Entonces, en vez de especificar un truco ATR

## 03:28 - 03:30
de una cantidad específica,

## 03:30 - 03:34
digamos que yo lo sete a $500 como ejemplo,

## 03:34 - 03:37
en vez de tener esa cantidad específica,

## 03:37 - 03:41
que podría traducir de manera diferente

## 03:41 - 03:42
dependiendo del símbolo que estás usando.

## 03:42 - 03:46
Si estás usando un truco de valor alto como Tesla,

## 03:46 - 03:49
que es el símbolo que tenemos aquí en el fondo,

## 03:49 - 03:52
cada parada es de $246.

## 03:52 - 03:57
Así que un truco ATR de $500,

## 03:57 - 04:01
o sea, considerando el valor de la parada,

## 04:01 - 04:06
eso es diferente de aplicar un truco ATR de $500

## 04:07 - 04:09
en una parada como Verizon,

## 04:09 - 04:12
que está empezando, creo, en el rango de $30.

## 04:12 - 04:14
Así que la razón...

## 04:15 - 04:17
Usando el truco ATR,

## 04:17 - 04:20
tenemos una forma de estandardizar el truco de Airster-Helling

## 04:20 - 04:23
basado en cómo la seguridad se mueve.

## 04:23 - 04:26
Así que déjame ir adelante y dejar que se resuelva

## 04:26 - 04:28
la entrada de MACD.

## 04:28 - 04:32
Voy a escoger hacia el very top.

## 04:32 - 04:34
Déjame encontrar los trucos ATR, aquí están.

## 04:34 - 04:38
Bien, y voy a agarrar el botón de control

## 04:38 - 04:42
y clicar en el truco ATR LX,

## 04:42 - 04:44
LX para la entrada larga.

## 04:44 - 04:47
Así que, al agarrar el botón de control,

## 04:47 - 04:49
puedes seleccionar múltiples estrategias,

## 04:49 - 04:51
lo que hice aquí,

## 04:51 - 04:56
seleccioné la entrada larga de MACD con el truco ATR LX.

## 04:56 - 04:59
Voy a poner esas estrategias en el truco.

## 04:59 - 05:03
La estrategia encontrará cada área o cada instancia

## 05:03 - 05:08
donde la estrategia generaría una entrada y una salida.

## 05:08 - 05:13
Puedes ver que en un mercado de tendencia,

## 05:13 - 05:16
estas entradas de MACD parecen muy bonitas.

## 05:16 - 05:19
Y el hecho de que el mercado esté uptrendido

## 05:19 - 05:22
significa que el truco no va a ser atrapado

## 05:22 - 05:26
hasta que se encuentre con ese movimiento hacia abajo.

## 05:26 - 05:28
En este caso, lo encontré aquí.

## 05:28 - 05:32
Así que esta es una estrategia de forma de caja.

## 05:32 - 05:34
Voy a ir aquí a la tabla de datos

## 05:34 - 05:38
y clicar en el reporte de la estrategia.

## 05:38 - 05:41
Vamos a la sumergencia de la performance.

## 05:41 - 05:42
Vamos a abrir esto un poco.

## 05:44 - 05:46
Podemos ver los resultados de la estrategia.

## 05:46 - 05:49
Esta es una estrategia que va de 5 años.

## 05:49 - 05:50
¿Cómo se sabe eso?

## 05:50 - 05:52
Bueno, sé la cantidad de datos defaultes

## 05:52 - 05:54
que tengo en mi análisis de gráficos,

## 05:54 - 05:56
pero también veo aquí en el topo,

## 05:56 - 05:59
en la tabla de los reportes de la estrategia de performance

## 05:59 - 06:00
y puedes ver que dice,

## 06:00 - 06:05
septiembre 26 de 2018 a septiembre 26 de 2023.

## 06:05 - 06:07
Así que un total de 5 años.

## 06:07 - 06:10
No tuvimos mucha actividad de intercambio en esos 5 años.

## 06:10 - 06:13
Puedes ver que el total número de intercambios es solo de 35.

## 06:13 - 06:20
Así que tal vez los intercambios sean de pequeño tamaño

## 06:22 - 06:25
para que yo haga algunas asumciones

## 06:25 - 06:28
sobre la estrategia en sí misma.

## 06:28 - 06:29
Quiero que mi estrategia reporte

## 06:29 - 06:32
tener una cantidad significativa de intercambios

## 06:32 - 06:35
para que te dé un poco más de confianza

## 06:35 - 06:37
sobre lo que la estrategia está haciendo.

## 06:37 - 06:40
Pero puedes ver cómo esta estrategia particular

## 06:40 - 06:42
es profitable para Tesla.

## 06:42 - 06:45
¿Fue profitable para Tesla?

## 06:45 - 06:46
Deja que lo aclaremos.

## 06:46 - 06:48
Y lo dijimos al principio.

## 06:48 - 06:49
El hecho de que estamos buscando

## 06:49 - 06:51
una estrategia de reporte de performance

## 06:51 - 06:55
y vemos que la estrategia ha realizado de una manera cierta,

## 06:55 - 06:57
no significa que va a hacer esa misma

## 06:57 - 06:59
o experiencia, ese mismo comportamiento,

## 06:59 - 07:02
avanzando y eso es algo que nosotros,

## 07:02 - 07:04
como estrategias, debemos de ser conscientes de.

## 07:04 - 07:06
Así que es muy imposible

## 07:06 - 07:09
esperar que las estrategias sean las mismas.

## 07:09 - 07:12
Sin embargo, en un contexto histórico,

## 07:12 - 07:15
esta estrategia generó algunos ganancias.

## 07:15 - 07:20
$16,000 de ganancias netas en un periodo de cinco años,

## 07:20 - 07:20
no es malo.

## 07:20 - 07:24
Si cambié el símbolo, aquí en la parte de atrás,

## 07:24 - 07:26
la estrategia recalculará.

## 07:26 - 07:30
Así que digamos que me switché el símbolo a Microsoft.

## 07:30 - 07:32
Recalcula la estrategia.

## 07:32 - 07:35
Noten que, de nuevo, el total número de intercambios

## 07:35 - 07:37
es de 33 intercambios.

## 07:37 - 07:39
Esta es una estrategia que, por Microsoft,

## 07:39 - 07:42
generó unos $9,000 de ganancias netas.

## 07:42 - 07:45
El factor de ganancias es de 1.54.

## 07:45 - 07:47
Usualmente veo el factor de ganancias

## 07:47 - 07:49
más que hago el total de ganancias netas,

## 07:49 - 07:51
incluso si quieres una estrategia

## 07:51 - 07:54
que sea profitable para empezar.

## 07:54 - 07:55
Pero al mismo tiempo, quieres saber

## 07:55 - 07:58
cuál es el ratio de ganancias con los ganancias.

## 08:00 - 08:02
No es todo sobre el total de ganancias netas

## 08:02 - 08:06
porque a veces, si el factor de ganancias es demasiado bajo,

## 08:06 - 08:09
es muy imposible para la estrategia

## 08:09 - 08:12
mantener esa ganancia.

## 08:12 - 08:14
El factor de ganancias de 1.5 significa

## 08:14 - 08:17
que por cada dólar que has perdido,

## 08:17 - 08:18
has ganado $1.50.

## 08:18 - 08:23
Así que tenemos ese tipo, ese ratio

## 08:23 - 08:28
cuando comparas ganancias con ganancias.

## 08:28 - 08:29
Así que el mayor el ratio significa

## 08:29 - 08:32
que el ratio de ganancias con los ganancias

## 08:32 - 08:36
es favorables a tu rendimiento, ¿cierto?

## 08:36 - 08:40
Vamos a ver algunas áreas de la reporta de la estrategia

## 08:40 - 08:41
de ganancias.

## 08:41 - 08:45
Porque quería mencionar que cuando haces

## 08:45 - 08:48
un test de vuelta de estrategia, como lo hice,

## 08:48 - 08:51
esto funciona muy bien para solo un símbolo.

## 08:51 - 08:53
Notas que empecé con Tesla,

## 08:53 - 08:57
miré la reporta de ganancias de estrategia,

## 08:57 - 08:59
luego mudé el símbolo a Microsoft

## 08:59 - 09:02
y parece que es favorable para eso también.

## 09:02 - 09:06
Si lo mudé a Apple,

## 09:06 - 09:07
podemos ver que es favorable.

## 09:07 - 09:11
Veamos el factor de ganancias de Apple, 3.75.

## 09:11 - 09:16
Y, por supuesto, es kind of expected

## 09:16 - 09:18
en un mercado uptrendido

## 09:18 - 09:21
para tener estos grandes intercambios.

## 09:21 - 09:24
La entrada de MACD entra en el mercado

## 09:24 - 09:28
y no sale hasta que tengamos un precio bajista

## 09:28 - 09:30
que sea suficiente significativo

## 09:30 - 09:34
para que se encuentre con la entrada de ganancias ATR.

## 09:34 - 09:37
Por default, esta entrada de ganancias utiliza tres ATR.

## 09:37 - 09:40
Entonces, lo que sea el valor de la entrada de ganancias ATR,

## 09:40 - 09:41
se multiplica por tres

## 09:41 - 09:44
y se establece como la entrada de ganancias.

## 09:44 - 09:47
Entonces, notas que aunque en este uptrendido

## 09:47 - 09:50
tuvimos algunas áreas en las que el precio se corregió

## 09:50 - 09:53
por unos días, no se corregió suficiente

## 09:53 - 09:55
para que nosotros lleguemos a esa entrada de ganancias.

## 09:55 - 09:57
No fue hasta aquí que el precio

## 09:57 - 09:59
realmente se corregió

## 09:59 - 10:01
y que nuestra entrada de ganancias se acercó aquí.

## 10:01 - 10:03
Y fue un buen tiempo

## 10:03 - 10:05
porque puedes ver que después de eso

## 10:05 - 10:07
el mercado continuó a bajar.

## 10:07 - 10:10
Así que muchas veces vas a encontrar intercambios como este.

## 10:10 - 10:11
Se ven muy bien.

## 10:11 - 10:16
Pero, de nuevo, esto es un backtest histórico.

## 10:16 - 10:17
Quiero decir, nadie puede sentarse allí

## 10:17 - 10:19
mirando los datos históricos

## 10:19 - 10:23
y pinpointar dónde sería la entrada óptima y la salida, ¿verdad?

## 10:23 - 10:25
Entonces, vamos a volver aquí

## 10:26 - 10:27
a mi reporte de performance.

## 10:27 - 10:29
Hice un símbolo.

## 10:29 - 10:30
Creo que fue Disney.

## 10:30 - 10:31
Sí.

## 10:31 - 10:32
Por ejemplo, si cambias a Disney,

## 10:32 - 10:36
puedes ver que no es un buen reporte aquí.

## 10:36 - 10:37
Tenemos una estrategia de perdida aquí.

## 10:37 - 10:41
El factor de ganancias es de 89 centavos.

## 10:41 - 10:43
Así que siempre vas a estar en el negativo.

## 10:43 - 10:45
En este caso particular,

## 10:45 - 10:46
por cada dólar que perdimos,

## 10:46 - 10:48
solo hicimos 89 centavos.

## 10:48 - 10:50
Así que no es un buen ratio.

## 10:50 - 10:52
Aunque si sigues a cambiar el símbolo,

## 10:52 - 10:54
puedes encontrar que muchos símbolos

## 10:54 - 10:58
tienen una performance profitable.

## 10:58 - 11:01
Idealmente, cuando estás desarrollando una estrategia,

## 11:01 - 11:04
quieres un método que te permita hacer

## 11:04 - 11:07
el backtest de un portfólio.

## 11:07 - 11:09
Así que tienes una estrategia en mente.

## 11:09 - 11:10
En este caso, muy simple.

## 11:10 - 11:12
Las reglas que seleccionamos aquí son muy simples.

## 11:12 - 11:14
Magdi, entrada óptima,

## 11:14 - 11:17
y luego tenemos un atr traicionamiento.

## 11:17 - 11:18
Pero lo que quieres hacer es que quieras aplicar

## 11:18 - 11:21
esa misma estrategia a un portfólio de símbolos

## 11:21 - 11:25
para que puedas agarrar la robustidad

## 11:25 - 11:28
de la estrategia en diferentes mercados.

## 11:28 - 11:31
¿Qué es el punto de encontrar una buena estrategia

## 11:31 - 11:34
si solo funciona en un símbolo particular?

## 11:34 - 11:37
En fin, esa estrategia va a fallar.

## 11:37 - 11:40
Tenemos una estrategia profitable en Tesla,

## 11:40 - 11:42
cambiamos el símbolo a Disney,

## 11:42 - 11:43
y entonces es una estrategia de perdida.

## 11:44 - 11:47
Así que no lo consideraría como una estrategia robusta.

## 11:47 - 11:50
Así que si puedes aplicar esa estrategia

## 11:50 - 11:52
a un portfólio de símbolos

## 11:52 - 11:56
y luego obtener un reporte basado en ese portfólio,

## 11:56 - 11:58
entonces puedes agarrar tu estrategia y decir,

## 11:58 - 12:03
bueno, parece que es profitable en general.

## 12:03 - 12:06
Así que si traigo 20 o 30 símbolos

## 12:06 - 12:09
y los traigo con esta estrategia,

## 12:09 - 12:11
parece que, basado en los números históricos,

## 12:11 - 12:14
voy a quedarse afloat en el lado positivo.

## 12:14 - 12:16
Pero eso es solo posible si tienes un instrumento

## 12:16 - 12:19
que te permite retestar una estrategia

## 12:19 - 12:21
contra un portfólio de símbolos.

## 12:21 - 12:25
Y eso es donde el portfólio maestro viene a placer.

## 12:28 - 12:30
Es divertido, estoy solo riendo

## 12:30 - 12:34
porque tenía un colegio que ríe

## 12:34 - 12:37
con la forma en la que pronuncio maestro

## 12:37 - 12:41
porque tiene esa pronunciación española,

## 12:41 - 12:42
es una palabra española.

## 12:42 - 12:46
Así que, o maestro o maestro,

## 12:46 - 12:47
lo que quieras pronunciarlo,

## 12:47 - 12:49
ese es el método que vamos a hablar hoy.

## 12:49 - 12:52
Así que vamos a cerrar el reporte de estrategia y performance.

## 12:52 - 12:54
Voy a venir aquí a mis aplicaciones

## 12:54 - 12:57
y la aplicación que estoy hablando de

## 12:57 - 13:00
está aquí, el portfólio maestro.

## 13:00 - 13:03
Vamos a abrirlo.

## 13:03 - 13:06
Todo el mundo debería tenerlo como parte de las aplicaciones

## 13:06 - 13:08
que son parte de TradeStation.

## 13:08 - 13:12
Así que déjame ir adelante y maximizar esto.

## 13:12 - 13:14
Bien, vas a encontrar

## 13:14 - 13:18
que hay muchos botones y herramientas aquí.

## 13:18 - 13:21
Voy a caminar a través de un backtest de portfólio

## 13:21 - 13:23
y voy a mostrarles cómo comenzar.

## 13:23 - 13:25
No tengo ningún documento de download,

## 13:25 - 13:27
así que no estamos usando nada customizado.

## 13:27 - 13:30
Esto es todo lo que está construido en TradeStation.

## 13:30 - 13:32
Y puedes jugar con la funcionalidad

## 13:32 - 13:33
y usarlo tú mismo,

## 13:33 - 13:36
lo que es lo que quiero encargar a todos a hacer.

## 13:36 - 13:38
Justo después de la clase,

## 13:38 - 13:40
set up different portfolios

## 13:40 - 13:43
y test them and see all the different functionality

## 13:43 - 13:44
that we have there.

## 13:44 - 13:47
By the way, another thing that I wanted to mention,

## 13:47 - 13:49
and I'll do this right now.

## 13:50 - 13:54
Let me bring this page over here.

## 13:54 - 13:58
All right, this is...

## 13:58 - 13:59
Let me just...

## 13:59 - 14:01
Oh, hold on.

## 14:01 - 14:01
This is...

## 14:01 - 14:03
Let me just remove this bar at the top.

## 14:03 - 14:04
This is our events page.

## 14:04 - 14:08
I know that Manolo usually shares the link here in the chat.

## 14:08 - 14:10
Manolo, if you can do that right now.

## 14:10 - 14:13
But if you go to the learn section of TradeStation,

## 14:13 - 14:15
the events section,

## 14:15 - 14:18
you're gonna find that on October 10th,

## 14:18 - 14:21
we have a follow-up to this class.

## 14:21 - 14:24
This class, which is available for you to register,

## 14:24 - 14:26
is titled rank, filter,

## 14:26 - 14:29
and manage your positions

## 14:29 - 14:32
when backtesting on Portfolio Maestro.

## 14:32 - 14:33
It's a follow-up class

## 14:33 - 14:36
because I go into more advanced features

## 14:36 - 14:37
of Portfolio Maestro.

## 14:37 - 14:40
So today is more like an introductory class.

## 14:40 - 14:41
I'm gonna show you how to get it started,

## 14:41 - 14:43
how to create the strategy groups,

## 14:43 - 14:45
how to create the portfolio.

## 14:45 - 14:47
And then October 10th,

## 14:47 - 14:50
I'll go over the ranking, the filtering,

## 14:50 - 14:52
and how to manage your positions

## 14:52 - 14:54
when running the backtesting on Portfolio.

## 14:54 - 14:56
So make sure that if you like this class

## 14:56 - 14:58
and you're interested,

## 14:58 - 15:00
you register for the October 10th class,

## 15:00 - 15:04
which is just part two of this presentation, okay?

## 15:04 - 15:06
Perfect.

## 15:06 - 15:09
So here's Portfolio Maestro.

## 15:09 - 15:12
I'm not gonna look at anything that is a sample portfolio

## 15:12 - 15:13
or a sample strategy group.

## 15:13 - 15:17
I'm gonna go right into thinking about the idea

## 15:17 - 15:21
that we started off with during this presentation,

## 15:21 - 15:23
which is the MACD long-end tree

## 15:23 - 15:27
combined with an ATR trailing stop.

## 15:27 - 15:30
And I wanna see how that strategy works

## 15:30 - 15:32
on a portfolio of samples.

## 15:32 - 15:33
So the first thing that you need to do,

## 15:33 - 15:35
you have two buttons here on the left-hand side.

## 15:35 - 15:37
You have one that says manage portfolio

## 15:37 - 15:39
and manage strategy groups.

## 15:39 - 15:39
The first thing you need to do

## 15:39 - 15:42
is create the strategy group,

## 15:42 - 15:44
and then we're gonna create the portfolio,

## 15:44 - 15:46
which is pretty much adding everything together,

## 15:46 - 15:49
like the symbols and the strategy all in a portfolio.

## 15:49 - 15:51
But let's start with the strategy group.

## 15:51 - 15:53
I'm gonna come over here to this section

## 15:53 - 15:54
for strategy groups.

## 15:54 - 15:55
You can see at the bottom

## 15:55 - 15:58
that we have sample strategy group one

## 15:58 - 16:00
and sample strategy group two.

## 16:00 - 16:04
As I said just a moment ago, we're just gonna ignore those.

## 16:04 - 16:06
And once I click on that button, manage strategy groups,

## 16:06 - 16:07
I'm just gonna click on new

## 16:07 - 16:09
right here on the top left corner.

## 16:09 - 16:11
This allows me to create a new strategy group.

## 16:11 - 16:14
I'm gonna call this strategy group MACD

## 16:14 - 16:20
and ATR trail, all right?

## 16:20 - 16:22
This example, I'm gonna work it on equities,

## 16:22 - 16:25
but notice that you can switch the asset class to futures

## 16:25 - 16:27
if you wanna do that.

## 16:27 - 16:29
I'm just gonna click okay.

## 16:29 - 16:31
And you can see that at the bottom,

## 16:31 - 16:36
it created that strategy group, MACD and ATR trail.

## 16:36 - 16:39
So the next step here is to add the strategy.

## 16:39 - 16:40
You can see that that's a button

## 16:40 - 16:42
we get right here at the very top.

## 16:42 - 16:43
So I'm gonna click here,

## 16:43 - 16:44
and this is gonna load all the strategies

## 16:44 - 16:47
that are built in to the TradeStation platform.

## 16:47 - 16:49
Not only the ones that are built in,

## 16:49 - 16:52
but also any custom strategy that you may have.

## 16:52 - 16:57
So if you have ownership of the strategy,

## 16:57 - 17:00
if you developed your own personal strategy

## 17:00 - 17:01
and wrote it in easy language,

## 17:03 - 17:06
I would be very interested in knowing

## 17:06 - 17:09
how that strategy works on a portfolio of symbols.

## 17:09 - 17:11
I'm sure that you bring it over here

## 17:11 - 17:15
and test it against a group of symbols.

## 17:15 - 17:18
So again, the same way that I did on the platform,

## 17:18 - 17:20
I'm gonna come here in portfolio maestro,

## 17:20 - 17:24
I'm going to find the MACD, long entry,

## 17:24 - 17:27
I'm going to highlight it,

## 17:27 - 17:28
but then I'm just gonna scroll up

## 17:28 - 17:31
and find the ATR trail LX.

## 17:31 - 17:33
Let me hold down the control key,

## 17:33 - 17:38
make sure that I have ATR trail LX highlighted,

## 17:38 - 17:42
and I have, did I highlight the MACD?

## 17:42 - 17:43
Okay, it's checked.

## 17:43 - 17:47
So it doesn't work as on the TradeStation platform,

## 17:47 - 17:49
we don't have check boxes.

## 17:49 - 17:51
So the MACD LE is checked,

## 17:51 - 17:55
and we just check the ATR trail and we just click okay.

## 17:55 - 17:58
So you can see that it adds the two strategies right here

## 17:58 - 18:00
on this top panel,

## 18:00 - 18:02
and I'm able to expand the details

## 18:02 - 18:03
of each one of these strategies.

## 18:03 - 18:06
I can open up the ATR trail LX,

## 18:06 - 18:09
and I can open up the MACD LE.

## 18:09 - 18:14
If you wanted to modify these inputs,

## 18:16 - 18:19
you would have to do it, let's see,

## 18:19 - 18:21
and I modified here.

## 18:21 - 18:24
That's one of the things that I wanted to,

## 18:24 - 18:26
you go in into strategy group.

## 18:26 - 18:27
Okay, there we go.

## 18:27 - 18:31
So for this example,

## 18:31 - 18:33
I'm gonna use the parameters that are here.

## 18:33 - 18:37
So the ATR is looking at 10 periods.

## 18:37 - 18:41
The ATR factor is three.

## 18:41 - 18:46
So it's using three ATRs for the trailing stop amount.

## 18:46 - 18:47
For the MACD,

## 18:47 - 18:51
we have the usual MACD values at 12, 26, and nine.

## 18:51 - 18:55
But if you wanted to adjust any of these parameters,

## 18:55 - 18:58
maybe you want to adjust the factor for the ATRs

## 18:58 - 19:01
or the number of bars that are used in the ATR calculator,

## 19:01 - 19:02
whatever it is,

## 19:02 - 19:06
you have to go into strategy group settings.

## 19:06 - 19:08
We'll go into some of these settings in just a moment,

## 19:08 - 19:10
but you go to the strategy inputs right here,

## 19:10 - 19:13
and this allows you to change those inputs

## 19:13 - 19:14
for any of the strategies

## 19:14 - 19:17
that you select right here on the top, okay?

## 19:17 - 19:21
Again, I'm just gonna use default parameters.

## 19:21 - 19:22
Merlin's asking,

## 19:22 - 19:24
how do you get the TS portfolio maestro

## 19:24 - 19:26
from the trade station?

## 19:26 - 19:28
You should have it available, Merlin.

## 19:28 - 19:30
If you go to the,

## 19:30 - 19:32
let me go back here to my trade station,

## 19:32 - 19:34
and let me know if anybody doesn't see it either,

## 19:34 - 19:36
but if you go to the apps,

## 19:36 - 19:40
you have portfolio maestro added here.

## 19:40 - 19:41
If you don't,

## 19:41 - 19:43
I believe there's a way for you to add it directly

## 19:43 - 19:45
on the client center,

## 19:45 - 19:47
on the trade station client center.

## 19:47 - 19:49
But if you don't have it,

## 19:49 - 19:50
I mean, you still go here and check,

## 19:50 - 19:52
and if you don't have it,

## 19:52 - 19:55
call client services and ask them

## 19:55 - 19:58
if they can enable it for you.

## 19:58 - 20:00
Okay, so Merlin found it.

## 20:00 - 20:03
Eduardo says he doesn't have it.

## 20:03 - 20:06
Don't you have to pay extra for portfolio maestro?

## 20:06 - 20:10
Jeff, depending on the pricing plan that you're on,

## 20:10 - 20:13
I think there are some tools that you pay extra for.

## 20:13 - 20:16
I'm not sure if anybody that has it here,

## 20:17 - 20:18
if you're paying for it,

## 20:18 - 20:20
if it's included in your plan,

## 20:20 - 20:22
but those are questions

## 20:22 - 20:25
that our client services department can answer

## 20:25 - 20:26
and let you know

## 20:26 - 20:28
if it's gonna cost you something or not.

## 20:28 - 20:30
But if you don't find portfolio maestro

## 20:30 - 20:33
right here in the apps section,

## 20:33 - 20:35
client services can add that for you,

## 20:35 - 20:38
or you can go to the trade station client center

## 20:38 - 20:42
and find trade station additional services.

## 20:42 - 20:46
And I believe portfolio maestro should be listed there.

## 20:46 - 20:51
All right, so let's go ahead and check my settings here.

## 20:52 - 20:54
So we already talked about changing inputs,

## 20:54 - 20:55
which I'm not gonna do.

## 20:55 - 20:58
I'm gonna just use it the way that it is.

## 20:58 - 21:01
Right here, the buttons allow me to add more strategies,

## 21:01 - 21:04
remove any of the strategies that I've added.

## 21:04 - 21:06
We're going into the settings of the strategy.

## 21:06 - 21:08
Let's go and take a look at some other settings,

## 21:08 - 21:10
because here in general,

## 21:10 - 21:14
you can specify commissions

## 21:14 - 21:17
if you're paying any commissions on stocks.

## 21:17 - 21:20
You can also do some back testing resolution

## 21:20 - 21:22
if you want to.

## 21:22 - 21:25
This is not a class where we talk about resolution.

## 21:25 - 21:27
I have a whole class talking about

## 21:27 - 21:30
look inside bar back testing and back testing resolution,

## 21:30 - 21:34
which goes into details on why you would want to use it.

## 21:34 - 21:37
But for now, we're just gonna leave it the way it is.

## 21:37 - 21:40
We're not gonna turn that feature on.

## 21:40 - 21:41
And position limits,

## 21:41 - 21:44
this allows you to enter multiple times

## 21:44 - 21:47
in the same direction as the currently held position.

## 21:47 - 21:51
So in simple words,

## 21:51 - 21:53
if the MACD generates an entry,

## 21:53 - 21:58
it's gonna buy and take you long on that security.

## 21:58 - 22:02
But if it meets the criteria again a few days later,

## 22:02 - 22:05
it's gonna buy again and increase your position size.

## 22:05 - 22:07
So that's what position limits allows you to do.

## 22:07 - 22:09
It's a pyramiding strategy

## 22:09 - 22:13
where your position size continuously increases

## 22:13 - 22:16
as the market conditions are in your favor,

## 22:16 - 22:18
or at least going in the direction of the strategy.

## 22:18 - 22:21
So every time that the strategy generates a signal

## 22:21 - 22:24
is going to increase your position size.

## 22:24 - 22:27
If you don't turn this on,

## 22:27 - 22:29
the strategy will only take one trade

## 22:29 - 22:30
in one direction at a time.

## 22:30 - 22:34
So if it enters long based on the MACD,

## 22:34 - 22:36
it will not do anything else

## 22:36 - 22:39
until it exits that long position.

## 22:39 - 22:41
It will not enter until it exits.

## 22:41 - 22:44
So that's what position limits does.

## 22:44 - 22:49
But notice that the same strategy settings

## 22:49 - 22:52
that you find on the platform

## 22:52 - 22:55
when you back test strategies are found here.

## 22:55 - 22:58
I'm not sure how familiar you are with strategy,

## 22:58 - 23:01
back testing, but a lot of that functionality

## 23:01 - 23:03
that you find when you're testing a strategy

## 23:03 - 23:06
on an individual stock

## 23:06 - 23:08
are also available here in Portfolio Maestro,

## 23:08 - 23:10
which makes the tool very robust

## 23:10 - 23:12
because then you can account for other factors

## 23:12 - 23:14
like commissions, slippage,

## 23:14 - 23:17
anything that may affect the strategy performance.

## 23:17 - 23:19
In the quantity box, of course,

## 23:19 - 23:22
you can change the fixed amount.

## 23:22 - 23:24
I'm just gonna leave it.

## 23:24 - 23:28
This is a fixed amount.

## 23:28 - 23:31
What I'm gonna do is since I'm gonna...

## 23:31 - 23:34
The idea here is that I'm going to apply the strategy

## 23:34 - 23:36
to a basket of symbols

## 23:36 - 23:41
and every symbol will have a different price, of course.

## 23:41 - 23:43
So if I trade 100 shares,

## 23:43 - 23:45
the risk on any single position

## 23:45 - 23:49
is going to be different when compared to another

## 23:49 - 23:51
because of the price of the shares.

## 23:51 - 23:54
So if I set my amount per trade

## 23:54 - 23:57
on a fixed dollar amount and I say,

## 23:57 - 24:07
let me trade $10,000 per position.

## 24:08 - 24:10
So if you're trading, for example,

## 24:10 - 24:14
a stock like Tesla that is trading at $250,

## 24:14 - 24:18
that would only give you how many shares?

## 24:18 - 24:22
That would only give you about 10, like 40 shares?

## 24:22 - 24:25
Is my math correct?

## 24:25 - 24:28
So we can do amounts per trade.

## 24:28 - 24:31
So invest $10,000 per position.

## 24:31 - 24:33
I'm gonna round down to the nearest,

## 24:33 - 24:40
let's go here, 10 shares and minimum number

## 24:40 - 24:42
to make sure that you adjust those

## 24:42 - 24:44
because if you're trading Tesla, for example,

## 24:44 - 24:47
and you're only investing $10,000,

## 24:47 - 24:50
if you've minimum, if it's 100 shares,

## 24:50 - 24:51
it won't put on that trade

## 24:51 - 24:56
because 100 shares of Tesla is going to cost you $25,000

## 24:58 - 25:00
and you're saying only invest 10,000.

## 25:00 - 25:04
So if you wanna trade $10,000 worth of Tesla,

## 25:04 - 25:08
make sure that your minimum trade size here reflects that

## 25:08 - 25:10
so that it's able to place that trade.

## 25:10 - 25:13
All right, I wanna click okay.

## 25:14 - 25:16
By the way, on the back testing,

## 25:16 - 25:19
we have some other check boxes here

## 25:19 - 25:22
that are brought over from the strategy engine

## 25:22 - 25:24
on the trade station platform.

## 25:24 - 25:28
I also do a class on the back testing settings,

## 25:28 - 25:32
not the place here for that explanation,

## 25:32 - 25:35
but if you have to configure the strategy,

## 25:35 - 25:37
then please take a look

## 25:37 - 25:40
at my other strategy trading presentations.

## 25:40 - 25:43
And that's it, I'm gonna click okay.

## 25:43 - 25:46
All right, so that's, I have the strategy.

## 25:46 - 25:48
I have the trade size already set up.

## 25:48 - 25:52
So now I'm gonna go here to the symbol list tab

## 25:52 - 25:54
because now I have to select the symbols

## 25:54 - 25:57
that I want to apply this strategy on.

## 25:57 - 26:00
So I'm gonna click on plus, add symbol.

## 26:00 - 26:03
Notice that we get access to the trade station

## 26:03 - 26:06
prepackaged list of symbols and any symbol list

## 26:06 - 26:08
that you've created yourself.

## 26:08 - 26:11
So if I go here to trade station symbol lists,

## 26:11 - 26:13
this is where, I'm sorry,

## 26:13 - 26:15
not the trade station symbol lists,

## 26:15 - 26:18
the trade station custom symbol list.

## 26:18 - 26:20
This is where the custom symbol lists

## 26:20 - 26:22
that you create would be listed.

## 26:25 - 26:27
I have a few here that I've created myself,

## 26:27 - 26:30
depending on the presentation that I have,

## 26:30 - 26:34
but you can go to the other categories here

## 26:34 - 26:36
if you want to scan.

## 26:36 - 26:37
I mean, if you wanna apply the strategy

## 26:37 - 26:38
on a particular sector,

## 26:38 - 26:41
or if you wanna do an index component,

## 26:41 - 26:45
notice that let's do the NASDAQ.

## 26:45 - 26:49
Let's not choose something as big as the 100

## 26:49 - 26:52
because that would mean that there's a potential

## 26:52 - 26:58
for you to have a position on each one of these 100 symbols.

## 26:59 - 27:04
If we specify the trade size to be $10,000 worth

## 27:04 - 27:08
and you multiply 10,000 by 100 symbols,

## 27:08 - 27:12
we are talking about how much?

## 27:12 - 27:14
We're talking about a million dollars

## 27:14 - 27:16
that you need in your account

## 27:16 - 27:20
in order to maintain a $10,000 position

## 27:20 - 27:21
in each one of these symbols.

## 27:21 - 27:22
Does that make sense?

## 27:22 - 27:25
So always think in terms of what is my account

## 27:26 - 27:28
capable of trading?

## 27:28 - 27:30
Look at your funds and make sure

## 27:30 - 27:31
that you're setting up your back test

## 27:31 - 27:35
in a way that you would be able to trade it.

## 27:35 - 27:37
So let me not choose the 100.

## 27:37 - 27:40
Let me go into the Dow Jones instead

## 27:40 - 27:43
and select the Dow Jones Industrial.

## 27:43 - 27:46
Let's see how it works in those 30.

## 27:46 - 27:49
It says 31 symbols in parentheses

## 27:49 - 27:52
because it also includes the symbol for the index itself,

## 27:52 - 27:54
dollar sign INDU.

## 27:54 - 27:57
Dollar sign INDU cannot be traded.

## 27:57 - 28:00
So I'm gonna look for a way to remove

## 28:00 - 28:02
that symbol from my test.

## 28:06 - 28:09
So John is asking how can you limit

## 28:09 - 28:11
the total amount traded to 100K?

## 28:11 - 28:14
That's a good question, John.

## 28:14 - 28:17
And when you're using strategies on trade station,

## 28:17 - 28:21
it's interesting because the strategy will assume

## 28:21 - 28:26
that you have enough money in your account to trade.

## 28:26 - 28:29
Now, when you do a portfolio back test,

## 28:29 - 28:31
there are some settings that you can tweak

## 28:31 - 28:34
in order to stop the strategy from trading

## 28:34 - 28:37
after a certain, whatever, number of positions

## 28:37 - 28:41
or after a capital has been invested.

## 28:41 - 28:45
So there are some ways that you can limit the portfolio.

## 28:45 - 28:48
However, on the initial stages of back testing,

## 28:49 - 28:53
there's no maximum amount that you can trade.

## 28:53 - 28:55
The strategy will assume that you can trade everything.

## 28:55 - 28:57
So if you say, like for example, I just did,

## 28:57 - 29:01
I told the strategy, I want you to trade $10,000

## 29:01 - 29:03
worth of every symbol.

## 29:03 - 29:05
And it'll assume that I have enough money in my account

## 29:05 - 29:09
to trade $10,000 worth of each symbol.

## 29:09 - 29:11
So if I supply 100 symbols, of course,

## 29:11 - 29:14
I'll need a million dollars in my account.

## 29:14 - 29:15
So those are the types of things

## 29:15 - 29:17
that you have to think about

## 29:17 - 29:20
when you're setting up the strategy

## 29:20 - 29:23
so that it's realistic to what your account is

## 29:23 - 29:25
and the funds that you have.

## 29:25 - 29:28
Of course, as I said just a moment ago,

## 29:28 - 29:29
there are some other constraints

## 29:29 - 29:31
and some other settings that you can turn on,

## 29:31 - 29:34
which is the topic that I'm going to cover

## 29:34 - 29:36
in the class of October 10th.

## 29:36 - 29:39
So here I'm going to select the 31 symbols,

## 29:39 - 29:42
even though there's one here that cannot be traded.

## 29:42 - 29:45
And let's see if I click OK here,

## 29:45 - 29:50
it adds the symbol list right here at the very top.

## 29:50 - 29:53
I'm able to expand it.

## 29:53 - 29:56
It gives me a description of each one of the symbols

## 29:56 - 29:58
that are added here to this group.

## 29:58 - 30:00
You can see the corporations.

## 30:00 - 30:06
I believe that I can, let's see,

## 30:06 - 30:07
if I select this one,

## 30:10 - 30:16
so this just gives me the properties for the symbol,

## 30:16 - 30:18
not what I wanted to do.

## 30:18 - 30:21
What I want to do, let's see, remove symbol,

## 30:21 - 30:22
confirm the list.

## 30:22 - 30:24
Are you sure you want to remove the selected symbol list?

## 30:24 - 30:26
I don't want to remove the symbol list.

## 30:26 - 30:27
I just want to remove a symbol.

## 30:27 - 30:30
Maybe it's not done here.

## 30:31 - 30:33
Interval settings.

## 30:33 - 30:35
All right, this is something else.

## 30:35 - 30:36
We'll look at the settings

## 30:36 - 30:38
and see how we can manage the symbol list.

## 30:38 - 30:40
I think I can do it later,

## 30:40 - 30:42
but the initial report is going to assume

## 30:42 - 30:47
that I'm able to trade the Dow Jones index when I can't.

## 30:47 - 30:50
Okay, let's go and take a look at the settings here.

## 30:50 - 30:53
You probably saw that I have interval settings.

## 30:53 - 30:56
So this is a, I'm going to do a daily back test.

## 30:56 - 30:59
So all the symbols are going to be loading daily bars

## 30:59 - 31:02
and the strategy is going to look at those daily bars.

## 31:02 - 31:03
I'm just going to click okay.

## 31:03 - 31:09
And at this point, these are all equities.

## 31:09 - 31:11
I'm not going to use additional data series.

## 31:13 - 31:14
Money management and ranking

## 31:14 - 31:17
are the features that I talked to you about.

## 31:17 - 31:21
I'm going to go into detail on those features

## 31:21 - 31:24
on the October 10th presentation.

## 31:24 - 31:27
But I just created what's called a strategy group,

## 31:27 - 31:31
which is a combination of strategies with symbols.

## 31:31 - 31:33
Now I'm going to build a portfolio

## 31:33 - 31:36
and I'm going to have additional settings that I can tweak.

## 31:36 - 31:41
So let's go over here to my manage portfolio button.

## 31:41 - 31:43
Notice that we're switching the button here.

## 31:43 - 31:48
And in here, I'm going to add, not add,

## 31:48 - 31:51
because what you see here,

## 31:51 - 31:55
this is a portfolio called sample portfolio two.

## 31:55 - 31:58
So it automatically loads a portfolio from the bottom

## 31:58 - 32:00
and I don't want to modify it.

## 32:00 - 32:02
So I'm just going to click over here at the very top

## 32:02 - 32:03
where it says new.

## 32:03 - 32:07
Again, we did it once when we created the strategy group.

## 32:07 - 32:09
Now we're doing it a second time

## 32:09 - 32:11
to create what's called the portfolio.

## 32:11 - 32:17
And this portfolio is going to be the MACD ATR trail.

## 32:17 - 32:21
And I'm just going to say DAO 30.

## 32:21 - 32:23
So I know that it's a back test.

## 32:23 - 32:25
The portfolio is a back test on the DAO 30.

## 32:25 - 32:28
I'm going to click OK.

## 32:28 - 32:30
Notice that it blanks out the top panel

## 32:30 - 32:33
because at this point it just creates

## 32:33 - 32:35
like a shell of the portfolio.

## 32:35 - 32:38
I need to bring in the strategy group

## 32:38 - 32:40
that I created just a moment ago.

## 32:40 - 32:42
So I'm going to click on this plus button

## 32:42 - 32:45
to add strategy group.

## 32:45 - 32:46
And you can see the list of strategy groups.

## 32:46 - 32:51
The one that I created was named MACD and ATR trail.

## 32:51 - 32:53
I'm going to click OK.

## 32:53 - 32:55
And here we see the two strategies

## 32:55 - 32:57
that we have in the strategy group

## 32:57 - 32:58
and we have the symbol here.

## 32:58 - 33:02
So we can expand and see all the symbols.

## 33:02 - 33:04
We can expand the strategies as well

## 33:04 - 33:08
and see the parameters of each one of those strategies.

## 33:08 - 33:11
You can remove the strategy group.

## 33:11 - 33:14
And at this point you have two buttons.

## 33:14 - 33:16
You have portfolio settings.

## 33:16 - 33:18
And over here on the right you have back test portfolio.

## 33:18 - 33:20
Let's go into portfolio settings

## 33:20 - 33:23
to see some of the things we can do.

## 33:23 - 33:27
Constraints and portfolio stops

## 33:27 - 33:30
are also two of the things we're going to talk about

## 33:30 - 33:33
on October 10th.

## 33:33 - 33:38
These are settings that you can apply to a portfolio level

## 33:39 - 33:42
and not on an individual strategy.

## 33:42 - 33:45
Now the MACD, LE and the ATR trail

## 33:45 - 33:46
that we selected earlier

## 33:46 - 33:49
is going to run on individual symbols.

## 33:49 - 33:53
But these other settings, constraints and portfolio stops

## 33:53 - 33:56
are set at the portfolio level,

## 33:56 - 33:59
not looking at individual symbols.

## 33:59 - 34:03
But here in the general tab, this is all fine.

## 34:03 - 34:05
I'm going to click OK.

## 34:05 - 34:09
All right, I'm going to go into...

## 34:09 - 34:13
I have a delete button here.

## 34:13 - 34:14
No?

## 34:14 - 34:17
So let's go into the back test portfolio dialog.

## 34:17 - 34:20
I'm just clicking on this back test portfolio.

## 34:21 - 34:25
I see information about what this is going to do.

## 34:25 - 34:28
So let me give this report a name.

## 34:28 - 34:34
MACD ATR trail on the Dow 30.

## 34:35 - 34:38
The initial capital that you see here,

## 34:38 - 34:42
you may think that it's what John was asking about.

## 34:42 - 34:46
John was asking, how do I limit my strategy or my portfolio

## 34:46 - 34:49
so that it doesn't trade more than $100,000?

## 34:49 - 34:52
You may think that this is that, but it's not.

## 34:52 - 34:55
The initial capital that you see right here,

## 34:55 - 34:57
it's only to calculate

## 34:57 - 35:00
what is called the return on initial capital.

## 35:00 - 35:04
So if my strategy is able to make $10,000

## 35:04 - 35:06
on a $100,000 capital,

## 35:06 - 35:09
it's just going to be a 10% return on initial capital.

## 35:09 - 35:12
So it's only used in the calculation

## 35:12 - 35:13
of return on initial capital.

## 35:13 - 35:16
So if you want to make this 100,000,

## 35:16 - 35:19
what you really have in your account, you can,

## 35:19 - 35:23
so that you can get those return on initial capital

## 35:23 - 35:25
calculations to be a little bit more accurate.

## 35:25 - 35:28
But remember that if you see return on initial capital

## 35:28 - 35:32
on the strategy performance report or any reporting

## 35:32 - 35:35
is based on this starting point, $100,000.

## 35:35 - 35:38
This is going two years back.

## 35:38 - 35:41
On the symbols that we looked at

## 35:41 - 35:44
on the TradeStation platform, we were going back five years.

## 35:44 - 35:48
So it's okay for us to go back five years.

## 35:48 - 35:51
Always be mindful of the number of symbols

## 35:51 - 35:53
you have in your portfolio.

## 35:53 - 35:56
I only have 30 symbols or 31 to be exact.

## 35:56 - 35:58
I'm going to try to remove that index symbol,

## 35:58 - 35:59
but I have 30 symbols.

## 35:59 - 36:02
It's not such a big deal to load five years

## 36:02 - 36:05
of historical data on each one of these symbols.

## 36:05 - 36:09
I'm only loading daily bars.

## 36:09 - 36:12
If I were loading five years of one minute,

## 36:12 - 36:15
maybe it's a different story.

## 36:15 - 36:19
But I'm not saying that you couldn't because you can.

## 36:19 - 36:22
I mean, we have intraday data here in Portfolio Maestro

## 36:22 - 36:25
and you can do intraday back testing.

## 36:25 - 36:28
But for the example we're working on, this is okay.

## 36:28 - 36:31
Five years of daily data on 30 symbols

## 36:31 - 36:35
is not going to be very taxing on the report here.

## 36:35 - 36:38
You also have access to other advanced settings

## 36:38 - 36:41
that you find on the TradeStation platform.

## 36:41 - 36:45
One of my prior strategy trading classes

## 36:45 - 36:48
that we did together was on optimization.

## 36:48 - 36:51
And we talked about the different methods

## 36:51 - 36:53
of optimization and so forth.

## 36:53 - 36:55
But that's, of course, a different class, you know?

## 36:56 - 36:57
And it's interesting that I always refer

## 36:57 - 37:00
to different classes just that it's impossible

## 37:00 - 37:03
to be able to fit everything in just one session.

## 37:03 - 37:05
And I'm just referring to these other classes

## 37:05 - 37:09
because I want you to be aware that we've done presentations

## 37:09 - 37:13
on a lot of these features and there's a lot

## 37:13 - 37:15
of educational content that you can reference

## 37:15 - 37:19
if you need some additional help, okay?

## 37:19 - 37:20
So we have the name here.

## 37:20 - 37:23
We have five years of historical data, okay?

## 37:23 - 37:25
This is all good.

## 37:25 - 37:28
I'm gonna leave my backtest type to standard strategy inputs.

## 37:28 - 37:30
I'm not changing anything here.

## 37:30 - 37:32
I'm just leaving everything the way it is.

## 37:32 - 37:33
And the symbols.

## 37:33 - 37:38
Oh, this is where I can exclude the dollar sign INDU

## 37:38 - 37:43
which I'm just gonna check the box here for exclude.

## 37:43 - 37:49
And there is another column here that says create.

## 37:49 - 37:52
Create is, I think it's create chart is what it says.

## 37:52 - 37:53
Yeah, create chart.

## 37:53 - 37:58
What it allows you to do, and this is interesting,

## 37:58 - 38:01
and we'll do it later, but I think it allows you

## 38:01 - 38:05
to see where the entries and exits are on a chart

## 38:06 - 38:09
because I mean, Portfolio Maestro doesn't have charting

## 38:09 - 38:11
like the Trade Station platform does.

## 38:11 - 38:14
And if you wanted to see a chart of the historical backtest,

## 38:14 - 38:17
then you have to make sure that these check boxes are checked.

## 38:18 - 38:19
Let's go ahead and do it.

## 38:19 - 38:20
I mean, it doesn't matter.

## 38:20 - 38:21
I'm just gonna click on this button that says

## 38:21 - 38:25
create all charts, okay?

## 38:25 - 38:26
So everything is checked.

## 38:26 - 38:28
I still have that check box on excluding

## 38:28 - 38:32
the dollar sign INDU, and I'm ready.

## 38:32 - 38:36
So all I need to do is click on perform backtest.

## 38:36 - 38:39
I just click it, and you can see that this initializes

## 38:39 - 38:42
and it's downloading historical data,

## 38:42 - 38:44
and you're gonna see that it doesn't take very long

## 38:44 - 38:53
for us to get the results.

## 38:53 - 38:56
Okay, the analysis is completed.

## 38:56 - 39:02
I'm gonna click on the button that says view report now.

## 39:02 - 39:04
One thing that I want you guys to notice is that

## 39:04 - 39:06
over here on the left-hand side,

## 39:07 - 39:11
I was moved from the portfolio section.

## 39:11 - 39:13
I was moved to the reporting section.

## 39:13 - 39:15
There's a reports tab here.

## 39:15 - 39:17
And we have, of course, the performance report.

## 39:17 - 39:20
We have an optimization report.

## 39:23 - 39:25
Interesting, my camera just died on me.

## 39:25 - 39:28
Okay, so we have optimization report

## 39:28 - 39:30
if you were running an optimization

## 39:30 - 39:32
within Portfolio Maestro, which you can.

## 39:34 - 39:36
And then we have some other reports here.

## 39:36 - 39:39
But what I wanna show you is these numbers.

## 39:39 - 39:43
This is an overall performance

## 39:43 - 39:46
on the 30 symbols combined.

## 39:46 - 39:49
Let's point out a few items here.

## 39:49 - 39:53
The total return is 86,506.

## 39:53 - 39:57
This is a total return when trading all 30 symbols.

## 39:57 - 40:00
You can see that gross profit,

## 40:00 - 40:04
it almost reached $300,000.

## 40:04 - 40:08
The loss was about $200,000.

## 40:08 - 40:13
So the profit factor right here is 1.42.

## 40:13 - 40:16
Okay, so for every dollar we made $1.42,

## 40:16 - 40:18
which a little low in my opinion,

## 40:18 - 40:20
but it's interesting that we're still

## 40:20 - 40:23
on a positive side of the strategy.

## 40:23 - 40:25
Notice the number of trades.

## 40:25 - 40:27
In a period of five years,

## 40:27 - 40:30
if you were trading all 30 symbols,

## 40:30 - 40:32
you would have traded 1,007 times

## 40:32 - 40:35
in that five-year time span.

## 40:35 - 40:38
We have a 43% profitability,

## 40:38 - 40:43
making 439 winning trades, 568 losing trades.

## 40:44 - 40:46
And remember, this is all numbers

## 40:46 - 40:49
on the overall performance of the portfolio.

## 40:49 - 40:52
Now, if you wanted to see the individual performance

## 40:52 - 40:57
and break down this total return per symbol,

## 40:57 - 41:00
you can go into the Trade Analysis tab.

## 41:00 - 41:04
Trade Analysis tab gives you similar numbers,

## 41:04 - 41:07
but here you have the ability to view hide.

## 41:07 - 41:09
Right here at the bottom right corner,

## 41:09 - 41:10
there's a view hide button.

## 41:10 - 41:12
I'm gonna click it.

## 41:12 - 41:14
And it just gives you a list of all the symbols

## 41:14 - 41:16
that make up this report.

## 41:16 - 41:19
I can click on this top checkbox next to symbol,

## 41:19 - 41:21
so that all the checkbox are highlighted,

## 41:21 - 41:23
and then I just click okay.

## 41:23 - 41:26
And this, of course, gives me a column

## 41:26 - 41:28
for each one of the symbols

## 41:28 - 41:31
that are part of the historical backtest.

## 41:31 - 41:35
And I believe these are,

## 41:35 - 41:38
I'm sure these are sorted in the way that they were traded.

## 41:38 - 41:40
That's why you have Johnson & Johnson

## 41:40 - 41:42
right here at the very beginning.

## 41:42 - 41:43
I don't think there's any,

## 41:43 - 41:46
I don't think it's sorted in any way

## 41:46 - 41:49
other than what was the first symbol that was traded.

## 41:49 - 41:50
Now, let's go here to the trade list

## 41:50 - 41:52
to confirm that theory.

## 41:52 - 41:55
I'm gonna go to the trade list and go over here.

## 41:55 - 41:58
This is back in 2018.

## 41:58 - 42:02
The first trade was done December 12th.

## 42:02 - 42:03
So 2018.

## 42:03 - 42:04
And you can see the symbol right here

## 42:04 - 42:06
is Johnson & Johnson.

## 42:06 - 42:09
So the order in which the columns are aligned

## 42:09 - 42:12
is the order in which the trades were generated.

## 42:12 - 42:18
And even though we go back five years,

## 42:18 - 42:22
so the chart should have loaded from September,

## 42:22 - 42:25
not December, the first trade is in December.

## 42:25 - 42:29
I'm not sure if you guys have done enough historical backtest

## 42:29 - 42:34
to have an understanding of why it started in December.

## 42:34 - 42:36
But maybe you know,

## 42:36 - 42:40
maybe you've heard of this term max bars back setting.

## 42:40 - 42:42
The strategy reserves an amount of data

## 42:42 - 42:46
at the beginning of the historical backtest for calculation.

## 42:46 - 42:48
And by default, that number's 50 bars.

## 42:48 - 42:49
And that's the reason why

## 42:49 - 42:52
we don't have earlier trades than December,

## 42:52 - 42:55
because that's when the strategy was able to generate trades.

## 42:55 - 42:57
But you can see the sequence of trades,

## 42:57 - 43:00
and you can see that it started with Johnson & Johnson,

## 43:00 - 43:03
and how many shares did it trade?

## 43:03 - 43:07
The price was 147 at that time,

## 43:09 - 43:10
right here, the quantity, 60 shares.

## 43:10 - 43:12
It was able to trade 60 shares.

## 43:12 - 43:16
Remember that in the trade size dialogue that we adjusted,

## 43:18 - 43:22
we specified that we wanted a $10,000 investment

## 43:22 - 43:24
on each one of these stocks,

## 43:24 - 43:28
and we wanted to round it down to 10 shares.

## 43:28 - 43:31
So you're not gonna see trades here that are lower than 10,

## 43:31 - 43:33
because we set that as a minimum.

## 43:37 - 43:40
And you don't see any odd number of shares.

## 43:40 - 43:45
So it's always rounded down to the nearest 10, 10 shares.

## 43:45 - 43:47
So you're not gonna see 61 or 62,

## 43:47 - 43:49
it's gonna round it down to 60.

## 43:49 - 43:50
So that's our first trade,

## 43:50 - 43:55
60 shares of Johnson & Johnson, not a profitable trade.

## 43:55 - 43:58
You can see that it lost $381 right here,

## 43:58 - 44:01
but you can see the history of all the trades

## 44:01 - 44:02
that were generated.

## 44:02 - 44:04
Pretty cool, huh?

## 44:04 - 44:06
Let's go here, and you have a lot of other tabs

## 44:06 - 44:09
that you can analyze in terms of performance.

## 44:09 - 44:15
You have returns on equity, equity table,

## 44:15 - 44:18
you have all the symbols visible here,

## 44:19 - 44:21
periodical returns,

## 44:21 - 44:23
the graphs, this is our equity curve line,

## 44:23 - 44:26
that's interesting,

## 44:26 - 44:27
and the settings for the strategy.

## 44:27 - 44:29
So the same performance metrics that you find

## 44:29 - 44:32
in the TradeStation platform

## 44:32 - 44:34
when you're developing a strategy

## 44:34 - 44:35
and you're looking at the strategy,

## 44:35 - 44:36
performance report,

## 44:36 - 44:38
you're gonna find all those same metrics

## 44:38 - 44:41
right here in Portfolio Maestro.

## 44:41 - 44:43
Another thing that I wanted to show you,

## 44:43 - 44:45
remember that checkbox that we checked

## 44:45 - 44:47
for us to be able to see a chart?

## 44:47 - 44:51
Let me go here to,

## 44:51 - 44:55
let me just see where I find that.

## 45:00 - 45:01
Okay, here we go.

## 45:01 - 45:02
At the very top,

## 45:02 - 45:03
you see where it says view trade charts?

## 45:03 - 45:06
I'm gonna click there,

## 45:06 - 45:10
and let me just see.

## 45:10 - 45:14
This gives me a window

## 45:14 - 45:19
with the strategy that I tested,

## 45:19 - 45:21
and here you can select the chart you want to see.

## 45:21 - 45:23
So if I wanna see a chart of Apple,

## 45:23 - 45:27
I just click on this little button for view chart,

## 45:27 - 45:29
and it opens up a chart for Apple.

## 45:29 - 45:32
Let me go ahead and exit out of this.

## 45:32 - 45:34
Oh, it actually closes it.

## 45:34 - 45:35
So let me go back in there.

## 45:35 - 45:36
View trade charts.

## 45:39 - 45:40
Let's go and open this up.

## 45:40 - 45:42
I'm gonna select Apple.

## 45:42 - 45:44
Let's view the chart.

## 45:44 - 45:47
How do I, let me move it out of the way.

## 45:47 - 45:54
All right, and in here in the chart,

## 45:54 - 45:59
I'm able to see the entries and exits of Apple.

## 45:59 - 46:04
This kinda, and it's not like trade station charting.

## 46:04 - 46:07
Let's get that straight.

## 46:07 - 46:09
But here, I'm able to see

## 46:09 - 46:11
what the strategy entered and exited.

## 46:11 - 46:14
You have the zoom out and the zoom in buttons here

## 46:14 - 46:18
if you wanted to get a little bit more detail, you know?

## 46:18 - 46:21
And of course, the time scale right here at the bottom.

## 46:21 - 46:23
Let me go ahead and exit out of this chart.

## 46:23 - 46:26
You want to, no, let's close this.

## 46:26 - 46:28
Okay, there we go, and close it.

## 46:28 - 46:29
So that's where you get the charting

## 46:29 - 46:31
if you wanted to see a chart.

## 46:32 - 46:34
I would rather go to the trade station platform

## 46:34 - 46:37
because I'm more familiar with the functionality there,

## 46:37 - 46:39
but this is the report.

## 46:39 - 46:41
So hopefully you got the steps.

## 46:41 - 46:43
You know, I just wanted to give you the introduction

## 46:43 - 46:46
on how to get Portfolio Maestro started.

## 46:46 - 46:48
First, you have to create the strategy group

## 46:48 - 46:50
with the symbols.

## 46:50 - 46:52
Then you have to create the portfolio.

## 46:52 - 46:54
You go into the settings of the portfolio

## 46:54 - 46:55
and you start the back test.

## 46:55 - 46:58
And then it just sends you here into the summary.

## 46:58 - 47:01
You can see that some symbols, of course,

## 47:01 - 47:03
have a negative return like Verizon

## 47:03 - 47:06
provided or generated a negative return.

## 47:06 - 47:11
Same for MMM, MMM.

## 47:11 - 47:14
You know, most of the symbols are positive,

## 47:14 - 47:16
which is interesting, you know?

## 47:19 - 47:21
Another thing that I wanted to show you is that

## 47:21 - 47:23
when you come over here to the trade log,

## 47:23 - 47:25
because one of the things that

## 47:25 - 47:27
Portfolio Maestro doesn't do is

## 47:27 - 47:29
it doesn't allow you to automate this.

## 47:29 - 47:31
Yes, it would be great for us to have the ability

## 47:31 - 47:33
to turn on a switch and say,

## 47:33 - 47:38
okay, do your thing, run the strategy on 30 symbols,

## 47:38 - 47:42
trade it based on my limitations,

## 47:42 - 47:45
whether the limitations are trade size,

## 47:45 - 47:47
constraints, portfolio stops,

## 47:47 - 47:49
whatever it is that I want to set,

## 47:49 - 47:52
turn it on and let the Portfolio Maestro tool

## 47:52 - 47:54
automate my strategy, but it doesn't do that.

## 47:54 - 47:58
But what it does do is give you a trace,

## 47:58 - 48:02
not the trace log, orders report right here, orders report.

## 48:02 - 48:05
So it does tell you what you need to do on a daily basis.

## 48:05 - 48:09
For example, here it tells you that you needed to,

## 48:10 - 48:12
UNH is United Healthcare, right?

## 48:12 - 48:17
So you needed to sell the 20 shares at $482.

## 48:18 - 48:23
This is the ATR LX was met yesterday.

## 48:24 - 48:26
You can see the action date is yesterday.

## 48:26 - 48:31
It doesn't use today's data because today hasn't closed yet.

## 48:31 - 48:34
And the historical back test here is loading,

## 48:34 - 48:36
of course, closed bars.

## 48:36 - 48:38
So you can see all the signals that were generated

## 48:38 - 48:40
as of yesterday.

## 48:40 - 48:43
Well, yesterday was Monday at 4 p.m.

## 48:43 - 48:45
And you have all your selling transactions.

## 48:45 - 48:47
These are all selling transactions.

## 48:47 - 48:50
We don't have any new trades going in.

## 48:50 - 48:53
These are open orders.

## 48:53 - 48:57
Positions, okay, you have your open orders.

## 48:57 - 48:59
It gives you the specific price that you need to sell at

## 48:59 - 49:02
based on the trailing stock.

## 49:02 - 49:03
This is what it is.

## 49:03 - 49:05
These are your trailing stock values

## 49:05 - 49:08
based on the calculated ATR.

## 49:08 - 49:11
These are your open positions.

## 49:11 - 49:15
You can see that United Healthcare is right there.

## 49:15 - 49:18
You entered, this is the opening price.

## 49:18 - 49:21
You entered at $445.

## 49:21 - 49:27
And you need a selling transaction at $482 or lower.

## 49:29 - 49:29
What's the price?

## 49:29 - 49:33
We need to find out what the price of United Healthcare

## 49:33 - 49:37
is at the moment.

## 49:37 - 49:38
Oh, $488.

## 49:38 - 49:39
That's where the price is, $488.

## 49:39 - 49:42
So you can see that you're setting your trailing stock

## 49:42 - 49:45
already for this position you currently have.

## 49:45 - 49:48
So based on the strategy,

## 49:48 - 49:51
these are the positions that you currently have

## 49:51 - 49:52
on your account.

## 49:52 - 49:55
And these are the filled orders for today

## 49:55 - 49:56
and the canceled orders.

## 49:56 - 50:00
It does give you details on what you need to do

## 50:00 - 50:03
to the strategy to be in sync with your report,

## 50:03 - 50:04
which is pretty cool.

## 50:04 - 50:06
Of course, you'd have to run it every single day

## 50:06 - 50:08
at the very end of the day

## 50:08 - 50:12
so you can get updated orders and updated positions.

## 50:12 - 50:13
Remember that the strategy,

## 50:13 - 50:16
the strategy is something that is calculated

## 50:16 - 50:18
on the close of every bar.

## 50:18 - 50:22
And if we're doing a strategy back test on daily bars,

## 50:22 - 50:24
then the strategy gets generated

## 50:24 - 50:26
at the close of every single day.

## 50:26 - 50:29
And that's the reason why it says 4 p.m.

## 50:29 - 50:30
And that's the reason why we're saying

## 50:30 - 50:32
you need to run it every single day

## 50:32 - 50:34
to get new orders, new reports.

## 50:34 - 50:38
It doesn't run automatically is what we're trying to say,

## 50:38 - 50:41
but it does give you which positions you should have open,

## 50:41 - 50:43
which orders you should be submitting.

## 50:43 - 50:47
And what orders to cancel and which orders to fill.

## 50:47 - 50:49
So pretty, pretty cool.

## 50:49 - 50:54
Let's see, how can you...

## 50:54 - 50:57
Okay, so from Malton, from Malton, yes.

## 50:57 - 50:59
Or Malone, I'm sorry.

## 50:59 - 51:00
I need to put my glasses on.

## 51:00 - 51:03
Is there a way to see individual total return

## 51:03 - 51:05
to check which performance?

## 51:05 - 51:06
Yes, exactly.

## 51:06 - 51:10
We do that here on the performance report.

## 51:10 - 51:12
Trade analysis is what we did here

## 51:12 - 51:14
as we displayed every single column.

## 51:15 - 51:17
We have this button here at the bottom right,

## 51:17 - 51:22
which allows you to hide or enable.

## 51:22 - 51:24
I'm just clicking on the checkbox here to add them,

## 51:24 - 51:27
and I see the individual return.

## 51:27 - 51:29
Jeff said, did you say that you cannot turn on

## 51:29 - 51:31
the strategy to run automatically?

## 51:31 - 51:35
Yes, I did say that, and I'm just reiterating that

## 51:35 - 51:38
you cannot turn this on for automation,

## 51:38 - 51:39
although it does give you a lot of details

## 51:39 - 51:41
as to what needs to be open,

## 51:41 - 51:43
what needs to be in active order,

## 51:43 - 51:46
and what needs to be done to your strategy.

## 51:51 - 51:52
Can you run the strategy automatically

## 51:52 - 51:56
in the TradeStation platform outside of Portfolio Maestro?

## 51:56 - 51:57
Of course you can.

## 51:57 - 52:00
In fact, I have 30 symbols in here,

## 52:00 - 52:05
so yes, I could theoretically have 30 charts open

## 52:05 - 52:09
on the platform, have the same strategy applied

## 52:09 - 52:11
to each one of the charts,

## 52:11 - 52:14
and have them turned on automatically.

## 52:14 - 52:17
The only problem of doing it that way

## 52:17 - 52:21
is that every chart will be independent,

## 52:21 - 52:24
so it will not be run as a portfolio.

## 52:24 - 52:28
Portfolio Maestro has this other layer of constraints

## 52:28 - 52:33
and stop level, I mean, portfolio level stops,

## 52:34 - 52:36
and some ranking and some filtering

## 52:36 - 52:38
that is done at the portfolio level.

## 52:38 - 52:43
So it does allow you to do some decision-making

## 52:44 - 52:47
as to what positions to put on.

## 52:47 - 52:49
If you go to the TradeStation platform

## 52:49 - 52:52
and you open up 30 individual charts

## 52:52 - 52:55
and automate 30 individual strategies,

## 52:55 - 52:57
then they're all going to be independent,

## 52:57 - 52:59
and there's not gonna be anything

## 52:59 - 53:01
cross-checking the symbols to see

## 53:01 - 53:04
which ones should be traded and which ones shouldn't.

## 53:04 - 53:07
So we're gonna get to more of that

## 53:07 - 53:08
in our next session, October 10th,

## 53:08 - 53:11
so make sure that you register for that session

## 53:11 - 53:13
if you'd like to learn a little bit more

## 53:13 - 53:14
about Portfolio Maestro.

## 53:14 - 53:15
But this is my class.

## 53:15 - 53:17
I hope that you guys enjoyed it.

## 53:17 - 53:20
If you have any questions, please feel free to reach out

## 53:20 - 53:23
to us at educationattradestation.com,

## 53:23 - 53:27
and we're there for you for any concerns,

## 53:27 - 53:31
and I want to wish everyone a wonderful afternoon.

## 53:31 - 53:33
I hope to see you in a future class.

## 53:33 - 53:34
Goodbye, everyone.

## 53:34 - 53:35
Great having you today.

## 53:35 - 53:35
Bye-bye.
