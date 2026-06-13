# Webinar TradeStation VII Cómo desarrollar tu Sistema de Trading II - SERSAN SISTEMAS (720p, h264)

## 00:09 - 00:18
Bueno pues buenas tardes, buenas tardes a todos, soy Sergi Sánchez de Celsan Sistemas.

## 00:18 - 00:24
Empezamos el séptimo webinar de TrayStation en directo desde bolsa.com, bueno estamos

## 00:24 - 00:30
aquí en MSL, en las oficinas MSL en Madrid, pero lo estamos retransmitiendo también para

## 00:30 - 00:40
todos los internautas de bolsa.com, vale, bueno, a ver, vamos a, a ver un momentito

## 00:40 - 00:54
que me oigo doble, vale, gracias, venga, voy a compartir la pantalla, bueno, voy bastante

## 00:54 - 01:03
por directo porque tenemos bastantes cosas a comentar hoy, se ve bien, sí, se ve bastante

## 01:03 - 01:08
bien, verdad, aquí en internet confío que también, voy a ver un momentito, supongo

## 01:08 - 01:15
que también, vale, bueno, a ver, antes un breve repaso a un poquito, lo muy breve,

## 01:16 - 01:23
porque va completamente ligado a lo que vamos a hacer ahora en el 7, pero brevemente lo

## 01:23 - 01:27
que comentamos en el 6 que era la iniciación de los sistemas para aquellos que no asistierais,

## 01:27 - 01:33
el disclaimer que es importantísimo, ya os lo habéis leído todos, ya lo sabéis de memoria,

## 01:33 - 01:37
bueno ya sabéis también lo que es TrayStation y los que no lo sabéis pues os recomiendo

## 01:37 - 01:42
que entréis en nuestra web, celsanstistemas.com y encontraréis mucha información al respecto

## 01:42 - 01:46
o sino también en la web de TrayStation, por supuesto, aunque más bien en inglés,

## 01:46 - 01:53
TrayStation es una plataforma, software y en este caso que vamos a tratar hoy para

## 01:53 - 01:59
backtesting y operativa con sistemas, vale, lo bueno es que te permite, te permite testearlo,

## 01:59 - 02:05
te permite crearlo y te permite también operarlo, vale, es en ese sentido una solución global

## 02:05 - 02:10
porque pues también es broker, de acuerdo, por lo tanto eso en mi opinión es una ventaja

## 02:10 - 02:15
bastante notable, una plataforma muy premiada, me lo paso porque ya sé que lo habéis visto

## 02:15 - 02:25
en anteriores webinars, vale, bueno, voy a ir a las cosas un poquito que me interesan

## 02:26 - 02:31
con relación a webinar 7, no vamos a repasarlo todo el 6, ya sabéis que están todos disponibles

## 02:31 - 02:38
tanto en bolsa.com como en nuestra web, en las secciones celsanstistemas, media y formación

## 02:38 - 02:42
si no recuerdo mal, allí están todos los vídeos publicados, tanto este como el 6 y

## 02:42 - 02:48
los anteriores webinars los podéis consultar allí, vale, el tema de los datos históricos

## 02:48 - 02:53
y el backtesting, vamos a continuar a partir un poco de aquí, vamos a ver lo que es una

## 02:53 - 03:00
optimización de ciertas maneras de optimizar, vamos a ver una solución para trabajar con

## 03:01 - 03:07
nuestras carteras de sistemas, vale, pero es importantísimo comentar antes el tema

## 03:07 - 03:12
del backtesting básico, de acuerdo, dijimos que una muy buena manera de comenzar era con

## 03:13 - 03:19
los elementos precreados, voy a ir cambiando un poquito la plataforma, siempre cuando pueda

## 03:19 - 03:26
hacerlo, claro, así va a ser mejor, de los elementos precreados, aquellos que no tengáis

## 03:26 - 03:33
nociones de programación y que no sepáis nada de easy language, que es el lenguaje

## 03:33 - 03:37
de programación de 3D Station, que es como su propio nombre indica, pues es un lenguaje

## 03:37 - 03:44
bastante sencillo, que lógicamente requiere una formación, en 3D Station podéis insertar

## 03:44 - 03:51
distintas estrategias, podés insert strategy, tienes ya un montón de elementos precreados,

## 03:54 - 03:58
de acuerdo, que vienen ya preinstalados en la plataforma, y que además todos son totalmente

## 03:58 - 04:02
editables y consultables, eso es muy importante, vale, solo como no hemos fijaros que lo que

## 04:02 - 04:09
acaba en LX es long exit, vale, lo que acaba en SX es short exit y lo que acaba en LE es

## 04:09 - 04:16
long entry y lo que acaba en SE es short entry, vale, entonces esa es un poco la pauta,

## 04:19 - 04:23
que también lo veis en las columnas, vale, el que hace buy, hace sell, hace short, vale,

## 04:23 - 04:28
cover, sell en 3D Station es cerrar largos, vale, no es abrir cortos, abrir cortos es

## 04:28 - 04:33
short, vale, y cover es cerrar cortos, de acuerdo, entonces aquí veis en las pestañitas

## 04:33 - 04:37
lo que marca cada elemento que hace, y esto que es muy sencillito, pues está muy bien,

## 04:38 - 04:42
es una manera de empezar, veis bollinger bands, entradas largas, bollinger bands, entradas

## 04:42 - 04:46
cortas, pues con eso montas un sistema para empezar, no quiero decir que con eso ya es

## 04:46 - 04:50
C, pero bueno, es una manera de empezar, porque luego también tenemos las salidas, tenemos

## 04:50 - 04:57
un montón de salidas precreadas, bueno, encontraré alguna que me acorde ahora, bueno, es igual

## 04:58 - 05:04
aquí salidas por parabólico, salidas por porcentaje, stop porcentaje, por un stop trailing,

## 05:04 - 05:11
un poco corto, por un profit target, por cierre en beneficio, bueno, hay realmente

## 05:13 - 05:20
muchas, por supuesto pues podéis importar varios y tal, aquí por expansiones de volatilidad,

## 05:20 - 05:24
hay realmente un montón y más normales, por un stop monetario por ejemplo también

## 05:24 - 05:29
está, vale, y como decía, lo muy bueno que es, es que tú simplemente das aquí, tienes

## 05:29 - 05:32
dos colas, una le das a definición, eso sí, va a ser en inglés, pero aquí los que lo

## 05:32 - 05:36
dominéis pues perfecto y aquellos que no pues usáis Google Translator, que quieras

## 05:36 - 05:41
o no, poco pues orienta, aquí ya tenéis una pequeña explicación de todos los indicadores

## 05:41 - 05:47
que tiene, eso es realmente muy útil porque te ayuda a situarte exactamente lo que hace,

## 05:47 - 05:53
¿no?, lo que hace, la verdad que es bastante completa, y luego el Easy Language, ¿de acuerdo?,

## 05:53 - 06:00
veis el código, y esto realmente es la mejor manera de aprender, de iniciarse, de iniciarse

## 06:00 - 06:07
un poquito en Easy Language, bueno, porque entendiendo cómo ellos han solucionado esta

## 06:07 - 06:13
estrategia, que en este caso es un People Reversal de entrada, vale, pues bueno, pues

## 06:13 - 06:20
tú puedes aprender, porque ahora aquí mismo lo mismo, en este singlón pulsas F1 y automáticamente

## 06:20 - 06:26
te va a abrir la ayuda y te va a explicar qué es esa función, ¿de acuerdo?, entonces

## 06:26 - 06:30
pues bueno, es una manera de ir poquito a poco aprendiendo, ¿de acuerdo?, y familiarizarse,

## 06:30 - 06:35
vale, esto voy rápido porque esto está tratado en el webinar 6, ¿eh?, porque ya soy consciente

## 06:35 - 06:41
que estoy yendo rápido, que sencillamente es un pequeño recordatorio de lo que tratamos

## 06:41 - 06:48
en el anterior, aquí fijaros que tengo justamente insertados entradas de Bollinger largas,

## 06:48 - 06:54
entradas de Bollinger cortas y un Stop Loss de 700 dólares, pues bueno, ese sistema hace

## 06:54 - 06:57
eso de entrada largo y corto y si pierden a un momento 700 dólares, como es aquí,

## 06:57 - 07:04
pues cierra, a ver que las líneas están, voy a ponerlas para que se vean bien en ambos

## 07:04 - 07:16
casos, no es esta, es justo la que no coges, siempre es esa, no es esa, voy a ver cuál

## 07:27 - 07:35
me falta, ah, que si no se confunde con las bandas de Bollinger, ya se lo voy a saber

## 07:35 - 07:42
más claro, vale, esto que está, no está optimizado ni nada ese sistema, eh, seguramente,

## 07:42 - 07:47
digo yo que será perdedor esto porque, bueno, mucho sería que ganara dinero, la verdad,

## 07:47 - 07:52
pero bueno, pues mira, gana dinero todo, es que hasta de oídas soy bueno, hay que ver,

## 07:52 - 07:56
elijo un sistema hacia ojo y lo elijo, por supuesto es broma porque esto ya os gratizo

## 07:56 - 08:03
que no ganará dinero, aunque tiene, es probable que no tenga comisiones, exacto, no tiene

## 08:03 - 08:08
comisiones, vale, no tiene comisiones, con lo cual seguro, casi seguro que con las comisiones

## 08:09 - 08:14
ya sería perdedor porque tiene un profit factor de 106 solo, vale, pero bueno, es un

## 08:14 - 08:20
sencillo ejemplo con los parámetros por defecto del Bollinger Bands en 15 minutos en el futuro

## 08:20 - 08:26
del DAX y con un stop loss de 700 dólares. Aplicaros que estos señales de stop que tiene

## 08:26 - 08:30
3x6 normalmente son intra barras, claro, o sea que eso es bastante útil porque hay muchas

## 08:30 - 08:38
plataformas que normalmente ponen el stop en la barra de entrada suele ser bastante problemático,

## 08:38 - 08:45
se puede hacer, pero normalmente con una programación standard por decirlo no entra porque el sistema

## 08:45 - 08:51
lee que el sistema está largo cuando acaba la barra actual, hay una sentencia típica

## 08:51 - 08:56
que es Get Mark Sentry por ejemplo o Market Position, es igual, ¿cómo está el sistema?

## 08:56 - 09:02
Claro, la lee que está en este caso largo cuando acaba, en cambio de decisiones es capaz

## 09:02 - 09:06
de leerlo durante la barra de entrada, por lo tanto si pierde 700 dólares en este caso

## 09:06 - 09:14
la barra de entrada sale, ¿cómo ha pasado aquí? Dos veces, ¿veis? Vale, entonces en

## 09:17 - 09:22
este webinar de hoy nos vamos a sentar en lo que es la optimización, quería sencillamente

## 09:22 - 09:28
comentaros lo de los herramientas de backtesting, esta era una, también os hablé del inside

## 09:28 - 09:35
bar backtesting, no voy a mostraros pero sencillamente no voy ahora a poneros el ejemplo que os puse

## 09:36 - 09:41
porque lleva un poquito de tiempo, pero sencillamente recordar que es un tema bastante importante

## 09:41 - 09:48
que no todas las plataformas contemplan, cuando una barra tiene lugar, lo explico brevemente

## 09:48 - 09:52
porque es importante, una barra tiene lugar en tiempo real como esta que se está construyendo

## 09:52 - 09:59
ahora mismo 15 minutos, esta barra si aquí hubiera un sistema aplicado como lo hay de

## 09:59 - 10:05
hecho, pues el sistema sabe rápidamente qué precio, si salta un stop o no salta un stop

## 10:05 - 10:12
porque el curso del tiempo, digamos que tiene claro cómo se construye la barra, en cambio

## 10:13 - 10:17
el sistema ya, esta barra por ejemplo que veis aquí no tiene ni idea cómo se ha construido,

## 10:17 - 10:21
es backtesting esto ya, esta barra no sabes cómo se ha construido, sabes que ha abierto

## 10:21 - 10:25
aquí, sabes que ha cerrado aquí y que ha hecho un mínimo aquí y un máximo aquí,

## 10:25 - 10:32
en este caso muy probablemente puedes pensar que ha sido casi el mínimo, se ha ido máximo

## 10:33 - 10:39
y ha vuelto, esta probablemente haya sido así, pero no siempre ocurre lo que parece

## 10:39 - 10:46
y no siempre es fácil averiguar lo que ha ocurrido, para solucionar esto todas las plataformas

## 10:46 - 10:51
digamos que tienen un algoritmo que calcula, que estiman cómo se ha construido la barra,

## 10:51 - 10:56
pero no lo saben con certeza todas, algunas de ellas sí, Interestation es una de ellas

## 10:56 - 11:03
con esta función que se llama look inside bar backtesting que la encontráis aquí,

## 11:03 - 11:08
esta función si se activa, bueno ahora mismo en este sistema no sé si tendrá efecto,

## 11:08 - 11:13
pero bueno vamos a verificarlo obviamente si tiene efecto, sería fantástico que lo

## 11:13 - 11:23
tuviera, esto lo activamos con un minuto, esto qué hace, esto comprueba con un histórico

## 11:23 - 11:30
paralelo, en este sistema no actúa, con un histórico paralelo comprueba cómo se ha

## 11:31 - 11:36
construido esa barra de 15 minutos en un minuto, por lo tanto sabe qué precio se ha tocado

## 11:36 - 11:41
antes y sobre todo en sistemas que tienen estrategia de entrada y estrategia de salida

## 11:41 - 11:47
por profit y salida por pérdidas, normalmente suele actuar y suele dar resultados bastante

## 11:47 - 11:52
dispares y alguna vez muy dispares, entonces no en todos los sistemas actúa, pero es una

## 11:52 - 11:57
herramienta de backtesting que aporta muchísima fiabilidad y que nos permite tener prácticamente

## 11:57 - 12:04
la certeza que testamos la realidad de lo que esperamos y hay otras plataformas que

## 12:04 - 12:11
no lo hacen eso y no puedes testearlo, yo utilizo un minuto normalmente, puedes hacerlo

## 12:11 - 12:17
en ticks, puedes hacerlo incluso en ticks, lo que pasa que en ticks el problema que tienes

## 12:17 - 12:22
es que solo tienes seis meses de histórico, entonces claro solo vas a poder comprobar

## 12:22 - 12:27
seis meses, en minuto como tienes todo pues ya pones un minuto, pero puedes poner hasta

## 12:27 - 12:34
20 segundos, si quieres o sea 20 segundos, el que le digas lo va a usar, pero normalmente

## 12:34 - 12:40
con un minuto incluso a veces en más, en 5 o en 15, evidentemente esto hace más lenta

## 12:40 - 12:47
la optimización, entonces a veces si ves que es poco sensible le pones 30 minutos

## 12:48 - 12:54
y luego le pones uno a ver cómo actúa, vas viendo cómo trabaja, pero en la mayoría

## 12:54 - 13:01
de sistemas tiene algún efecto, en algunos es muy notable, en algunos es muy poco y algunos

## 13:01 - 13:09
nada, aquí porque solo hay un stop, el sistema solo puede salir por esa señal, le da igual

## 13:10 - 13:15
saber cuando lo ha tocado porque cuando lo toca sale, realmente el debate está cuando

## 13:15 - 13:22
puede tocar varias órdenes, cuando esta variable actúa es cuando hay varias órdenes de salida

## 13:23 - 13:30
en el mercado, sean de profit o de win, cuando hay varias órdenes de salida no siempre sabes

## 13:30 - 13:38
exactamente cuál de ellas ha saltado primero o de entrada o un stop and reverse por ejemplo,

## 13:38 - 13:45
pero en el webinar 6 vimos un ejemplo que era bastante exagerado que aplicaba mucho,

## 13:46 - 13:51
que realmente se está, bueno aquellos que están siguiendo el mercado el DAX se está

## 13:51 - 13:59
dando la vuelta al alza, aprovechamos, mercado en directo. Y luego nada, también Transition

## 14:01 - 14:06
tiene algunas funciones fitness que hasta se han extendido a otras plataformas, la verdad

## 14:06 - 14:11
que no tienen nada, pero el Transition Index por ejemplo es un fitness que usa Transition

## 14:11 - 14:16
porque ya usan otras, también tiene a nivel de estadísticos el RINA porque como RINA

## 14:16 - 14:21
tiene una colaboración con Transition solo usa Transition, el RINA Index que sale en

## 14:21 - 14:27
el Performance Report, bueno, pero esto son cosas que al final también tampoco son super

## 14:27 - 14:32
destacadas, la más destacable en backtesting la vamos a ver hoy que es hablando de backtesting

## 14:32 - 14:39
de un sistema concreto es el World Forward Optimizer que vamos a pasar a verlo. Bien,

## 14:40 - 14:47
como os decía hoy vamos a hablar mucho de optimización, al final la optimización aquellos

## 14:47 - 14:50
que estéis familiarizados con el sistema pues ya sabéis lo que es, pero aquellos que

## 14:50 - 14:56
no lo estéis pues sencillamente es un proceso de búsqueda de valores óptimos que cumplen

## 14:56 - 15:03
una determinada condición, una determinada objetivo, un target, y se utiliza para, como

## 15:03 - 15:08
pongo aquí, ahora veremos que es un debate bastante interesante, yo ya os digo que soy

## 15:09 - 15:12
completamente partidario de la optimización pero bueno hay gente que no lo es, es un debate

## 15:12 - 15:18
interesante y hay razones en ambos sentidos, esto como la derecha y la izquierda, los de

## 15:18 - 15:21
la derecha dan argumentos para la derecha, los de la izquierda dan argumentos para la

## 15:21 - 15:28
derecha, bueno, quien tiene razón pues depende, depende de cada momento supongo, entonces

## 15:28 - 15:32
realmente la optimización en términos general en estadísticas se utiliza para un montón

## 15:32 - 15:39
de cosas, entonces es un proceso para mi que sé que hay que utilizarlo, es verdad

## 15:39 - 15:45
que tiene pues como casi todas las herramientas muy potentes tienen peligros porque un Fórmula

## 15:45 - 15:52
1 es una máquina realmente muy potente y seguramente las manos menos de las mías sería

## 15:52 - 15:58
un peligro bastante importante, pero Alonso no lo lleva mal, lo maneja bien, entonces

## 15:58 - 16:03
al final todas las herramientas muy potentes en sí conllevan riesgos, porque justamente

## 16:03 - 16:10
su potencia en su potencia deriva su riesgo, pero el hecho de que tenga riesgos no implica

## 16:11 - 16:16
que no debamos usarlo, en mi opinión supongo como los futuros, los futuros son muy peligrosos,

## 16:16 - 16:22
no los futuros no son peligrosos, lo que son peligrosos es el que usa mal los futuros,

## 16:22 - 16:26
pero el futuro en sí, uno puede operar un futuro sin apalancamiento exactamente igual

## 16:26 - 16:33
que un ETF y mucho más barato, realmente no tiene peligro en sí el concepto, lo que

## 16:35 - 16:40
pasa es que el futuro permite un apalancamiento como otros activos que si no se usa bien pues

## 16:40 - 16:47
es peligroso, sería una analogía de este tipo, entonces en mi opinión sí que hay

## 16:47 - 16:54
que usarla pero hay que utilizarla con buen criterio, me he insultado porque es el mismo

## 16:54 - 17:01
tema que tengo yo, digo se me ha olvidado, entonces como os decía hay que usarlo con

## 17:05 - 17:08
buen criterio y hoy en día tenemos herramientas como vais a ver el World Forward Optimizer

## 17:08 - 17:14
que nos ayuda muchísimo a medir la robustez del sistema que es al final lo que buscamos,

## 17:14 - 17:19
al final cuando hacemos un sistema lo que buscamos es que gane dinero, eso es más bien

## 17:19 - 17:26
obvio, el problema es que todavía no podemos conocer el futuro y al final lo backtesteamos

## 17:27 - 17:33
en datos pasados, es la herramienta que tenemos para comprobar o para validar si una idea

## 17:33 - 17:40
creemos que es buena, pero realmente los resultados pasados no garantizan los futuros, frase típica

## 17:41 - 17:48
del sector financiero, eso es cierto, pero si realmente trabajamos bien esta optimización

## 17:49 - 17:55
y utilizamos herramientas como la que vais a ver ahora posteriormente, pues podemos entre

## 17:55 - 18:02
comillas fabricar datos futuros, podemos fabricar datos futuros o live, ya lo vamos a ver entre

## 18:03 - 18:10
comillas, esta es la típica frase que la sacan fuera de contexto y estas muerta, pero eso

## 18:10 - 18:16
es en las comillas. Bueno aquí brevemente no quiero extenderme

## 18:16 - 18:22
mucho en conceptos teóricos, que luego esto queda grabado y podéis leerlo con calma,

## 18:22 - 18:31
aunque no sé si se le da muy bien en el ordenador, pero bueno, bien, fantástico, bueno, seguro

## 18:36 - 18:41
que habéis oído hablar de concepto de sobre-optimizar y concepto de robustez que se puede definir

## 18:41 - 18:48
de muchas maneras, yo os la he definido de una manera más bien pragmática, porque hablamos

## 18:48 - 18:53
muchas veces de robustez, a veces con ligereza, porque realmente la robustez lo que podemos

## 18:53 - 18:58
hacer es fomentarla, intentar buscarla, pero realmente hasta que no opere en real no lo

## 18:58 - 19:04
sabemos si es robusto, la robustez de verdad es que el sistema opera y va como esperábamos

## 19:04 - 19:10
en el backtesting, entonces a priori decimos, hombre, es un sistema que va más activos

## 19:10 - 19:16
es más robusto, bueno, a priori sí, un sistema que pasa el World Forward Optimizer con buenas

## 19:16 - 19:21
pruebas es robusto, bien, a priori sí, pero hasta que no opere realmente no vamos a saber

## 19:21 - 19:29
si realmente es realmente robusto, porque al final estamos en un entorno de incertidumbre.

## 19:30 - 19:36
El tema de la muestra, cuando optimizamos esto, antes previamente aquí había un debate

## 19:36 - 19:40
interesante antes de empezar sobre los grados de libertad, sobre la optimización, sobre

## 19:40 - 19:47
la muestra y demás, al final la muestra debe ser o debería de ser en términos generales,

## 19:47 - 19:52
porque hay excepciones, vamos a ver que con World Forward Optimizer vamos a intentar mantener

## 19:52 - 19:57
estos dos criterios, pero siendo un poco más laxos veréis por qué, al final tiene que

## 19:57 - 20:04
ser representativa del universo, es decir, contra más tipos de mercado tengamos en un

## 20:05 - 20:11
backtesting mejor, de acuerdo, si yo cojo un mercado que es, estoy optimizando un sistema

## 20:11 - 20:17
en el futuro del DAX, quiero que haya mercados bajistas, alcistas, volátiles, poco volátiles,

## 20:17 - 20:23
laterales, contra más tipos de mercado haya más fácil o más probable es que el mercado,

## 20:23 - 20:28
el sistema se haya adaptado bien a todos los mercados, pero luego aparte de eso tiene que

## 20:28 - 20:33
ser estadísticamente significativa, porque de nada me sirve si ese estudio es representativo

## 20:33 - 20:40
al final tiene 5 traits, porque por muy representativo que sea del universo objeto de estudio realmente

## 20:42 - 20:47
no es estadísticamente significativo, entonces hay que buscar un poquito los dos, ya que os

## 20:47 - 20:51
ponía más grados de libertad, más significaciones necesitamos, esto pues utilizamos la TV Studen

## 20:51 - 20:55
normalmente para medirlo, aunque la verdad la TV Studen me parece muy poco agresiva,

## 20:55 - 21:00
quiero decir que se pasa con mucha facilidad, o sea realmente no pasarla, si no la pasas

## 21:00 - 21:07
realmente es que tienes muy muy pocos traits y realmente el beneficio por traits es muy

## 21:07 - 21:14
bajo, realmente se suele pasar, pero hay que pasarla, y luego el otro método importantísimo

## 21:15 - 21:22
de que medimos robustez y que buscamos que un sistema, o valorar si un sistema funciona

## 21:24 - 21:30
en live es lo que llamamos la prueba externa, que es donde vamos a entrar ahora en el Google

## 21:30 - 21:36
Forward Optimizer que vais a ver en breve, el World Forward clásico ahora muy breve

## 21:36 - 21:41
os lo voy a enseñar lo que es en TV Station, eso sí que la mayoría de plataformas de sistemas

## 21:41 - 21:48
lo tiene, al final tampoco todas, hay algunas que hay que hacerlo manualmente, sabéis que

## 21:49 - 21:52
siempre son muy gracios, hay gente que luego me lo dice, pero por qué no lo dice, porque

## 21:52 - 21:57
no me gusta nunca hablar de, además yo plataformas trabajo muchas, pero voy a hablar de una en

## 21:57 - 22:02
este caso, por ejemplo en caso de VisualChar, no tiene World Forward ni clásico, o sea

## 22:02 - 22:05
tú tienes que hacer tu backtest en un periodo y luego tu probarlo en otro periodo por tu

## 22:05 - 22:10
cuenta, pero hay muchas plataformas que este proceso lo hacen implementado, o sea que ya

## 22:10 - 22:15
te dejan decir qué parte pones dentro y qué parte pones fuera del histórico y ya te sacan

## 22:15 - 22:21
las estadísticas, digamos que es más rápido, pero esto no es para nada exclusivo de TV

## 22:21 - 22:28
Station, no tiene muchas plataformas, el World Forward clásico, y luego está el Self-Adaptative,

## 22:29 - 22:34
que nada, no voy a hacer nada más sobre ello, que esto ya es un avanzado, son sistemas que

## 22:34 - 22:39
en el código ya se autoajustan al mercado y que el World Forward va muy bien para eso,

## 22:39 - 22:45
luego lo vamos a ver. ¿Qué es el World Forward convencional? Pues bueno, por ejemplo este

## 22:45 - 22:49
sistema que tenemos aquí, vamos a hacer muy breve que veáis una optimización clásica

## 22:49 - 22:54
para aquellos que no estáis familiarizados con TV Station, en el menú para elegir las

## 22:54 - 22:59
funciones fitness, en el menú VIEW tenéis el Chart Analysis Preferences y hay una pestaña

## 22:59 - 23:04
que es Strategy, aquí es un poco donde se controlan las opciones generales de optimización

## 23:04 - 23:11
y donde se elige la función fitness, la función objetivo que vamos a optimizar, bueno hay

## 23:13 - 23:19
varias, a mí personalmente digo porque siempre es una pregunta que me hacen, ya lo digo,

## 23:19 - 23:24
a mí me gusta mucho el Expectancy Score, me gusta mucho el TV Station Index y me gusta

## 23:24 - 23:30
mucho el Perfect Profit Correlation y sin desmenecer nada a Profit Factor, que mi compañero

## 23:30 - 23:36
Roberto le gusta mucho por ejemplo, al final la mayoría, como ya he dicho muchas veces,

## 23:36 - 23:43
no todos pero la mayoría tienen una elevada correlación entre ellos, es decir, normalmente

## 23:43 - 23:48
un buen sistema suele salir bien en todo, o sea, debería de salir siempre que sean

## 23:48 - 23:55
de rentabilidad riesgo, claro si uno coge máximo consecutivo de perdidos a lo mejor

## 23:55 - 23:59
uno sale, pero es decir, siempre que utiliza algún ratio de rentabilidad riesgo, cualquiera

## 23:59 - 24:05
de ellos, normalmente van a salir parecidos las zonas, de acuerdo, parecidos, no tendremos

## 24:05 - 24:10
que ser igual, pero aquí se elige, se elige cómo se ordenan, en principio esto es lo

## 24:10 - 24:16
que os quiero explicar de esta ventana, luego vamos a Format, o hacéis doble clic encima

## 24:16 - 24:25
de una orden, de una flechita, o si no habéis el menú Format, Format Strategies o botón

## 24:25 - 24:30
derecho, que es la manera un poco más sencilla, sale todo, encima del gráfico sale Format

## 24:30 - 24:36
Strategies, aquí salen los sistemas que están insertados, en la pestaña Properties for All

## 24:36 - 24:40
están estas opciones que habéis visto de si usamos el Look Inside Verbal Testing o no,

## 24:40 - 24:45
lo vamos a desconectar, porque ya hemos visto que no actuaba y para esta prueba no da igual,

## 24:45 - 24:53
Comisiones, vamos a poner 3, bueno 3 no, porque 2 ya es mucho porque en Trail Station

## 24:53 - 25:01
el futuro del DAX a veces cuesta 1.20, no 30€, cuesta 1.20 dólares más 0.50, no,

## 25:01 - 25:09
sí, más o menos, ponemos 2 euros, sale por un poco menos, por euro y pico, vale, Slip

## 25:09 - 25:30
Bajé para el DAX, Roberto, 12, 15, 20, 15 euros, por contrato, euros, es, es, el punto

## 25:30 - 25:36
del DAX son 25, pues bueno, medio punto es medio punto, es un poco más de medio punto,

## 25:36 - 25:41
yo creo que es menos, pero bueno, es igual, no pasa nada, esto es una mera, una mera prueba,

## 25:42 - 25:45
aquí en el Backtesting normalmente lo vais a tocar, pero que sepáis, aquellos que no

## 25:45 - 25:52
estéis familiarizados, pues bueno, si usáis órdenes limitadas hay que elegir cómo simula

## 25:52 - 25:55
el hecho de las órdenes limitadas, porque ya sabéis que con una orden limitada no podemos

## 25:55 - 26:00
estar seguros que se ha ejecutado, porque te puedes quedar en la cola cuando se toca

## 26:00 - 26:06
el precio, entonces bueno, aquí te dice que qué asumciones quieres hacer con una orden

## 26:06 - 26:11
limitada, que ejecute cuando lo toca, que ejecute cuando excede el límite y luego incluso

## 26:11 - 26:17
combinaciones de que la marca ejecutada cuando se ejecuta al menos un número determinado

## 26:17 - 26:22
de acciones en ese precio, eso es bastante interesante, esto normalmente hay que dejarlo

## 26:22 - 26:27
por defecto, si queremos penalizar extra las órdenes con un slippage adicional a las órdenes

## 26:27 - 26:32
a mercado, además del que hemos fijado aquí, si queremos que las órdenes a mercado tengan

## 26:32 - 26:37
un slippage adicional y estas opciones de automatización que lo explicaré al final previamente, para

## 26:37 - 26:42
conectarlo a tiempo real al mercado, pero a lo mismo no nos importa, también hay aquí

## 26:42 - 26:49
si no están en el código, si no está en el código las órdenes de gestión de contratos,

## 26:49 - 26:54
pero el código puedes por supuesto modificarlo, puedes poner euros por trade o número de contratos

## 26:54 - 27:02
fijos y ya está, entonces aquí para optimizar desde el menú format en inputs, vamos a optimizar

## 27:02 - 27:13
simplemente, no nos complicamos, con un incremento, optimizar, no, es que el sistema está aplicado

## 27:19 - 27:28
en un time frame concreto, no se puede optimizar con código avanzado, bueno preguntan perdonad

## 27:31 - 27:36
porque aquí no lo es claro, las preguntas en internet, preguntan si pueden optimizar

## 27:36 - 27:39
varios time frames, estamos comentando que al principio el gráfico está insertado sobre

## 27:39 - 27:43
un time frame y tú optimizas ese y luego Roberto que está aquí también de

## 27:43 - 27:50
Desensant Systems, pues comenta que con código avanzado se puede hacer de, se puede hacer

## 27:50 - 27:55
programente, con código avanzado prácticamente no voy a decir todo porque no, porque todo

## 27:55 - 27:59
no se puede, pero realmente se puede casi todo lo que es objetivizable, porque además

## 27:59 - 28:04
hoy en día ICLenguage cada vez es más abierto y tiene más objetos externos, se puede llamar

## 28:04 - 28:10
bases de datos externas, de Excel, realmente se pueden trabajar de manera muy flexible,

## 28:10 - 28:16
todo no, insisto, pero por código se puede hacer casi todo, pasa que ya hay cosas pues

## 28:16 - 28:20
un poquito más complicadas, que yo mismo por ejemplo sería capaz, para eso está Roberto

## 28:20 - 28:27
que sí que es capaz de todo y más. Entonces por ejemplo aquí optimizamos la banda

## 28:27 - 28:31
de Bollinger y es 32, vamos a dejar la desviación porque es una probabilidad que queremos hacer

## 28:31 - 28:39
las dos, optimizamos la misma, la otra para el otro lado y el stop lo dejamos o no, vamos

## 28:39 - 28:48
a optimizar un poco el stop también, vamos a poner desde 500 a 1500, 250, 2000, vale.

## 28:54 - 28:59
Esto aquí fijaros que os salen las opciones, esta línea de abajo no debe salir, eso es

## 28:59 - 29:05
un fallo de mi portátil de hace tiempo, en ningún ordenador me pasa, pero aquí no sé,

## 29:05 - 29:08
como que no encajan las ventanas, no sé por qué, me pasaron varios problemas, no solo

## 29:08 - 29:15
con 3D, entonces alguna historia interna del portátil, pero aquí esto se debe ver mejor

## 29:15 - 29:19
que aquí, optimización siempre tenéis dos tipos, ya la standard y la world forward,

## 29:19 - 29:23
luego la veremos porque la world forward es la que nos lleva al world forward ultimizer,

## 29:23 - 29:30
la optimización standard que puede ser exhaustiva o genética, si le dais a advanced settings

## 29:30 - 29:35
fijaros que aquí es donde marcáis el periodo que dejáis fuera de muestra, este es el world

## 29:35 - 29:40
forward clásico que os decía antes en el powerpoint, aquí le ponemos el outsample

## 29:40 - 29:46
window, es decir que parte del histórico quieres que no optimice, por defecto pone 30

## 29:46 - 29:51
pero podés cambiarlo y podés incluso poner una parte inicial y una parte final como quieras,

## 29:51 - 29:57
normalmente se deja 30, 20, 10% de visual, depende de la cantidad de muestra, y luego

## 29:57 - 30:02
las opciones del optimizador automático que al principio le das a su jest y te las va

## 30:02 - 30:11
a tocar, se puede tocar las pruebas de stress pero no toca, bueno esto depende, esto depende

## 30:12 - 30:20
mucho, no hay una regla absoluta, realmente depende del tipo de sistema, si es un sistema

## 30:20 - 30:23
que va en gráfico diario, es un sistema que va en intradía, es un sistema que tiene

## 30:23 - 30:28
pocos straights, muchos straights, en todas formas déjame que luego cuando hablemos del

## 30:28 - 30:32
world forward ultimizer vamos a entrar un poco más en este concepto de periodos que

## 30:32 - 30:37
es muy muy interesante, pero luego quizá vamos a entrar mejor, aquí ya no me deja

## 30:37 - 30:43
hacer lo genético porque realmente hay muy pocas combinaciones, no me deja elegir, bueno

## 30:43 - 30:50
no se me deja no, no me deja cambiarlo, no, me va a decir que lo haga exhaustivo porque

## 30:50 - 30:56
hay muy pocas, esto ahora lo va a hacer, no sé si va rápido, no sé cuánto histórico

## 30:56 - 31:02
he cargado, aquí ni me he fijado, no, hay demasiado histórico, bueno lo vamos a dejar

## 31:02 - 31:13
ahí, le he dejado el 30% fuera de muestra, bueno entonces esto aquí va haciendo su proceso

## 31:14 - 31:21
y ahora veréis que nos va a sacar una estadística con los datos in sample, los datos auto sample

## 31:21 - 31:26
no optimizados y conjuntos, esto sería el world forward clásico que me estaba refiriendo

## 31:26 - 31:32
aquí, el world forward clásico, que consiste en optimizar un histórico y dejar libre

## 31:32 - 31:36
otro, hay plataformas que no lo permiten hacer ya directamente y tú optimizas una

## 31:36 - 31:41
parte y lo pruebas en otra, pero evidentemente es mucho más rápido así, porque además

## 31:41 - 31:46
nos permite unir los datos ya en una estadística y además es realmente mucho más sencillo,

## 31:46 - 32:07
no sé cuánto histórico he cargado aquí, normalmente va remontando, cuando a veces

## 32:08 - 32:15
pone una hora y al final son 30 minutos, bueno seguimos en todo el caso avanzando un poco

## 32:18 - 32:25
la teoría y ahora cuando nos acabe pues volvemos aquí, entonces en que supone que es el world

## 32:30 - 32:37
forward avanzado, lo vais a ver mejor en una imagen, esto es una aplicación que forma

## 32:38 - 32:44
parte de the station, pero es una aplicación por sí sola, se llama world forward optimizer,

## 32:44 - 32:50
esta aplicación te permite, como pongo aquí un poco, pues empieza realmente cuando el

## 32:50 - 32:55
resto de métodos de backtesting acaban, como os decía antes es bastante parecido a probar

## 32:55 - 33:00
con datos futuros, porque aquí en este world forward clásico que acabamos de hacer hemos

## 33:00 - 33:05
visto una optimización, con un periodo in sample y otro periodo auto sample que ahora

## 33:05 - 33:11
cuando acabe veremos, el world forward optimizer lo que hace es en un único proceso hacer

## 33:11 - 33:18
centenares de muestras distintas, lo vais a ver en un ejemplo práctico, lo voy a enseñar

## 33:19 - 33:25
para que lo veáis, hace centenares, de tal manera que yo puedo combinar, aquí que hemos

## 33:25 - 33:32
hecho en este ejemplo, hemos optimizado el 70% histórico y hemos dejado el 30% fuera,

## 33:32 - 33:39
en este ejemplo que se está ahora optimizando, pero yo puedo hacer también 80-20 o 90-10

## 33:39 - 33:46
o 60-40, puedo variar la ventana, puedo variar la ventana y puedo variar el número de runes,

## 33:47 - 33:53
el número de cortes, aquí fijaros cada rune para que lo entendáis en este gráfico, es

## 33:53 - 33:56
una simplificación por meses, no tiene por qué ser natural por meses, las fuentes pueden

## 33:56 - 34:01
cambiar pero sencillamente para que, aquí al final el periodo de optimización es de

## 34:02 - 34:09
5 meses, 4 se optimizan y 1 no, es 20%, optimizo el 80% y el 20% lo dejo fuera, igual aquí,

## 34:14 - 34:21
pero fijaros que esto es un rune, esto es otro rune, esto es otro, 3, 4, 5, 6, 7 y 8,

## 34:21 - 34:28
en total ha hecho 8 runes, y lo mismo, yo puedo variar esta ventana que en este caso

## 34:28 - 34:33
en esta pantalla es 80-20, pero también puedo variar el número de runes, o sea porque

## 34:33 - 34:41
hago 8 y no hago 5 o no hago 15, porque esto moviendo donde, el hecho, fijaros aquí que

## 34:43 - 34:49
este periodo que inicia, inicia en el mes 1 y este inicia en el mes 2 y este inicia

## 34:49 - 34:54
en el mes 3, se inicia en el mes 4, esto es así ya digo porque es una ejemplificación

## 34:54 - 34:58
pero no tiene por qué ser así, este podría empezar en el mes 3 y este en el mes 5 y

## 34:58 - 35:04
este en el mes 7 y por lo tanto en medio de 8 pues hacer 4 o al revés, podría empezar

## 35:04 - 35:11
justo aquí, en el mes y medio y en el 2 mes y medio y en vez de 8 hacer 12, 12 runes.

## 35:14 - 35:19
Estas dos, voy a ir un poco adelante y atrás ahora para intentar explicaros lo mejor que

## 35:19 - 35:26
pueda, estas dos variables, es decir el porcentaje que yo dejo fuera de mostra, normalmente elegimos

## 35:27 - 35:34
entre el 5 y el 30% como veis aquí y el número de runes que hacemos, son las dos variables

## 35:34 - 35:42
claves para hacer un World Forward Ultimizer, que insisto vais a ver en un ejemplo práctico.

## 35:43 - 35:50
Aquí variamos estas dos variables, en este ejemplo práctico de 5 a 30% fuera de muestra

## 35:51 - 35:58
con incrementos de 5% y con de 4 a 12 runes de 1 en 1, es decir 4, 5, 6, hacemos un montón

## 35:59 - 36:06
de runes distintos, de tal manera veis aquí tenéis, que luego lo veréis cuando acabe

## 36:07 - 36:12
este que está haciendo ahora, aquí tenéis una copia de uno de ellos, es este, en la

## 36:12 - 36:19
columna primera tenéis fuera de muestra de 5 a 30% y en la fila de la cabecera veis

## 36:19 - 36:26
que van los runes del 4 al 11, que hay equipos de 12 pero es al 11, son distintos runes,

## 36:27 - 36:35
o sea un rune es esto, es cada fila, un rune es cada fila, ahora lo vas a ver, lo hace

## 36:41 - 36:47
todo en un proceso el solo, si si si, un proceso muy intensivo y además hace unas pruebas

## 36:47 - 36:53
a cada set que ahora lo vais a ver, realmente lo destacable no es solo el hecho de probarlo

## 36:53 - 36:58
sino que luego te da datos sobre ello, luego te da datos de cada una de ellas, de cada

## 36:58 - 37:04
una de ellas, entonces aquí obtenemos cada combinación, este cluster, esta casilla que

## 37:04 - 37:12
es 5% fuera de muestra y 4 runs, y esta de aquí es 20% fuera de muestra y 7 runs, cada

## 37:16 - 37:23
una de ellas pues así, y todas ellas, de todas ellas vas a poder ver todos los datos,

## 37:24 - 37:33
por lo tanto, recapitulando, recapitulando, como os decía en la definición inicial es

## 37:33 - 37:40
un proceso que hace sucesivas optimizaciones, aplicando, o sea, hace sucesivas optimizaciones,

## 37:41 - 37:47
sucesivos runs con una ventana elegida concreta, los mejores parámetros que obtienen ese

## 37:47 - 37:55
set los aplica un periodo fuera de muestra y en ese caso igual que hace la optimización

## 37:55 - 38:00
clásica wall forward, lo que pasa que lo hace en muchos sets conjunto y que nos da

## 38:00 - 38:07
los datos agrupados luego, luego podemos ver todos estos datos de manera agrupada, ahora

## 38:09 - 38:13
lo vais a ver que es realmente fantástico, por eso decía antes no de las comillas de

## 38:13 - 38:18
qué lo vuelvo a poner, es como probar el sistema de datos futuros porque realmente

## 38:18 - 38:23
es así, realmente tú puedes construir con este método un histórico fuera de muestra

## 38:23 - 38:30
muy largo, de mucho tiempo atrás, o sea, que hubiera pasado si en el pasado yo hubiera

## 38:31 - 38:35
hecho wall forward y hubiera aplicado, que hubiera pasado si, esa es un poco la clave,

## 38:35 - 38:41
por eso entre comillas insisto hablamos de fabricar datos futuros, estas son una de las

## 38:41 - 38:46
preguntas típicas que responde wall forward optimizer que además equivale a decir si

## 38:46 - 38:52
es robusto mi sistema, lo resumimos así, pero un sistema robusto pues sería esto, un

## 38:52 - 38:55
sistema que gane dinero después de optimizar gane dinero, no, eso es lo que queremos,

## 38:55 - 39:01
pues este aplicación intenta responder a eso, bueno no intenta, responde a eso, o sea responde

## 39:01 - 39:06
objetivamente a eso, otra cosa insisto, esto lo comento siempre, no quiere decir que un

## 39:06 - 39:12
sistema que pase el wall forward optimizer va a ganar dinero en el mercado seguro, eso

## 39:12 - 39:16
es imposible porque el mercado cambia y si el mercado puede automáticamente hacer un

## 39:16 - 39:20
cambio que no ha estado contemplado nunca en el histórico el sistema dejará de ganar

## 39:20 - 39:30
dinero. Desde luego con esta aplicación podemos objetivar la robustez, yo puedo decir objetivamente

## 39:30 - 39:34
que ese sistema es robusto en este momento, ahora, lo que no puedo decir es si el futuro

## 39:34 - 39:40
del mercado que hará, pero si puedo llegar a esta conclusión que hasta ahora pues no

## 39:40 - 39:46
será muy difícil llegar, realmente utilizabamos con excel, hacíamos wall forward, pero incluso

## 39:46 - 39:51
las pruebas que hemos hecho todos en excel mezclando histórico tal no llegan a este

## 39:51 - 39:57
nivel nunca, ahora lo vais a ver porque los datos que obtenemos son tremendos, y una cosa

## 39:57 - 40:05
que es realmente que nosotros en Cersan Sistemas que ya sabéis que además de estar explicándolos

## 40:05 - 40:12
y intentando formar a todo el país, bueno a los interesados en 3 session pues intentamos

## 40:12 - 40:17
hacerlo no, pero además somos desarrolladores de sistemas y nosotros intentamos aplicar

## 40:17 - 40:21
esta última casilla que veis aquí, de que cada cuanto tiempo debemos reoptimizar nuestro

## 40:21 - 40:31
sistema y wall forward automation también responde a eso, no en todos los casos, porque

## 40:31 - 40:34
depende de la muestra si es significativa o no, aquello que os decía antes necesitamos

## 40:34 - 40:40
que la muestra sea significativa, pero si la muestra es significativa normalmente vamos

## 40:40 - 40:45
a poder también programar la reoptimización del sistema, nosotros ahora mismo tenemos

## 40:45 - 40:52
un sistema operando, o sea este set que os voy a dar, ahora os voy a enseñar un wall

## 40:52 - 40:56
forward en el programa original, de verdad este es el set, perdón este es el wall forward

## 40:56 - 40:59
que ha elegido los parámetros de nemesis de un sistema que está en el mercado operando

## 40:59 - 41:06
en tiempo real ahora mismo, o sea que es 100% real, estos son algunos de los gráficos que

## 41:07 - 41:14
vamos a ver ahora mismo, pero no me extendo aquí porque un poco lo pongo como por seguridad

## 41:14 - 41:18
por si no me fuera la conexión o algo, pues no tengo y puedo hablar de ello, pero estas

## 41:18 - 41:25
mismas tablas las vais a ver ahora en situ, antes recapitulemos un momentito que nos va

## 41:26 - 41:32
a ayudar a comprender un poquito todo esto, aquellos que estén familiarizados con sistemas

## 41:32 - 41:39
puede resultar más o menos entendible, pero realmente si no pues es un concepto que puede

## 41:39 - 41:46
resultar un tanto complejo, la optimización que habíamos puesto con el wall forward clásico

## 41:46 - 41:50
ya ha acabado, cuando acaba aparece el gráfico, no nos la abre, tenemos que ir a la opción

## 41:50 - 41:56
view, strategy, optimización report o darle al myusov por acceso directo al teclado,

## 41:56 - 42:03
por ejemplo aquí y os va a abrir el histórico, el informe de la optimización, fijaros que

## 42:05 - 42:12
arriba hay tres tipos de datos, all data, in sample data y out of sample data, es decir

## 42:14 - 42:19
aquello que os decía que habíamos elegido aquella ventana del 30% ya tenéis los datos

## 42:19 - 42:24
separados, esto normalmente los portamos, debemos aguardar y los sacamos cada uno de

## 42:24 - 42:31
ellos y lo portamos en excel, digamos que puedes trabajar mejor con los datos. Un dato

## 42:32 - 42:39
muy destacable que da TrayStation ya aquí en este informe, que insisto esto es el wall

## 42:39 - 42:44
forward clásico, esta optimización es normal y corriente solo que ya nos permite ver este

## 42:44 - 42:50
wall forward, tiene una última columna que se llama el robotness index, que no es más

## 42:50 - 42:57
que si el sistema está ganando lo mismo anualmente en la parte fuera de muestra que

## 42:57 - 43:04
la parte optimizada, en este caso fijaros que el mejor ordenado por expectancy score

## 43:06 - 43:12
porque es el que hemos elegido, que está marcado en gris, en el conjunto de datos fijaros

## 43:12 - 43:18
que fuera de muestra lo ha hecho un 55% peor, no ha ido bien, en cambio aquí tenemos el

## 43:18 - 43:23
tercero que lo ha hecho mejor, realmente lo ha hecho un 288 mejor, se ha ido muy bien

## 43:23 - 43:30
fuera de muestra, esto realmente es una muestra que tiene 403, para una intradía me gustaría

## 43:31 - 43:38
que tuviera más pero no está mal, no es una mala muestra, entonces si ahora por ejemplo

## 43:38 - 43:45
aplicamos este conjunto, no vamos a complicarnos mucho la vida, esto es solo para que veáis

## 43:45 - 43:48
como funciona, aquí si haces doble clic estos parámetros ahora mismo me los ha aplicado

## 43:48 - 43:56
al sistema, me los ha cambiado, este que es set zone, pues son en vez del 20 por defectos

## 43:56 - 44:02
30, el periodo 30 que se ha ido a la banda alta y si que el stop más o menos lo mantiene

## 44:02 - 44:07
siendo 50, 1000 en esa zona más bien baja, pero fijaros que el periodo lo quiere aumentar

## 44:07 - 44:13
un poco, quiere ir un poco más lento, porque le hemos puesto comisiones entonces a la que

## 44:13 - 44:20
el operar empieza a costar dinero normalmente quiere operar menos, eso suele pasar, entonces

## 44:23 - 44:28
esta es una optimización normal, esto aquí podemos exportarlo a excel, podemos exportarlo

## 44:28 - 44:33
a excel y trabajarlo y mezclarlo, nosotros a modo de ejemplo, que veáis un poquito el

## 44:33 - 44:40
proceso sencillamente, nosotros hacemos optimizaciones de muchos tipos, esto por favor no divulgáis

## 44:40 - 44:50
nada, que tendría que mataros luego, a ver si lo encuentro, no está aquí, no está

## 44:52 - 45:02
aquí, aquí, estos son world forward, pero es igual efectos del dato es lo mismo, esto

## 45:02 - 45:06
por ejemplo, aquí tienes la tabla insample, la tabla autosample, la tabla load data, aquí

## 45:06 - 45:11
hacemos luego unos distintos vistores y los trabajamos, pero al final apuntamos un poquito

## 45:12 - 45:22
los datos de la optimización, etcétera, no lo he oído, perdón, ¿me puedo repetir?

## 45:22 - 45:28
Sí sí, puedes hacerlo antes o después, puedes dejarlos, ahora lo he comentado, esto es un

## 45:28 - 45:40
excel a título de muestra, nosotros lo exportamos y aquí trabajas, aquí el property for alls

## 45:41 - 45:50
en el, ya lo diré, aquí por ejemplo, vamos a poner por probarlo solo, aquí en el advanced

## 45:50 - 45:57
settings, aquí escrut first, aquí excluye histórico por delante o por detrás, si quiere

## 45:59 - 46:08
puede poner 30% por delante y cero por detrás, en el world forward optimizer no, yo lo he

## 46:08 - 46:12
hecho lo primer día para ver que hacía y sé que lo hace pero no tiene sentido, realmente

## 46:12 - 46:17
no tiene sentido, realmente para el world forward optimizer lo que nos interesa es saber si

## 46:17 - 46:23
ha ido ganando dinero en el futuro, no en el pasado, no tendría, lo vamos a ver y creo

## 46:23 - 46:29
que queda claro, entonces si queremos hacer un world forward optimizer que tenemos que

## 46:29 - 46:32
hacer, porque esta es la optimización que hemos visto clásica, que también es interesante

## 46:32 - 46:38
y útil, es la que tiene la mayoría de plataformas, que insisto puede ser genética o exhaustiva,

## 46:38 - 46:42
en caso de three station, pero luego para hacer un world forward optimizer tenemos que venir

## 46:42 - 46:47
aquí y elegir world forward, a esto hay que ponerle un nombre, que será luego el nombre

## 46:47 - 46:53
que tendrá, es esto, este es de don chan porque es un canal de don chan que mi amigo

## 46:53 - 47:00
Roberto le gusta mucho y luego aquí, al final lo que se elige es un poco lo mismo, la ventana,

## 47:05 - 47:08
aquí realmente no importa porque luego la van a cambiar, pero bueno, podéis elegir

## 47:08 - 47:12
la ventana que dais, realmente no importa, el algoritmo y tal, pero lo mismo, puede ser

## 47:12 - 47:17
genética o exhaustiva, igual, o sea, tú puedes hacer un world forward optimizer genético

## 47:17 - 47:24
o exhaustivo, lo único que hay que marcarlo aquí, ponerle un nombre porque luego una

## 47:24 - 47:28
vez acabe la optimización aquí, lleve su tiempo, habrá que ir aquí y hacer otro proceso,

## 47:28 - 47:34
o sea, es un proceso en dos fases actualmente, de hecho están trabajando en versiones donde

## 47:34 - 47:41
esto está un poco más unificado, porque esto, esta app world forward optimizer lo compró

## 47:41 - 47:46
hace años a Grail, si buscas esto también encontrarás su formación, es una aplicación,

## 47:46 - 47:50
ya lo he dicho muchas veces, pero es que no me canso de decirlo, para mi es única, es

## 47:50 - 47:56
fantástica, entonces la compro y realmente la he ido integrando en 3D Station, pero bueno,

## 47:56 - 48:01
como que en cada versión que saca la integra un poco más, es decir, hay alguna cosita,

## 48:01 - 48:06
entonces aún realmente hay cosas que se ve, que se nota, que es una aplicación que se

## 48:06 - 48:10
externa y que ellos la están integrando, y esto es uno de ellos, porque realmente esto

## 48:11 - 48:15
la lógica sería que ya desde aquí pudieras ya hacer las dos cosas, pero realmente haces

## 48:15 - 48:20
un proceso aquí y luego vienes aquí y lo abres y haces otro, ahora mismo está así,

## 48:20 - 48:27
en la 9.5 que está en beta, en principio creo que hay alguna mejora en ese sentido,

## 48:27 - 48:31
no estoy seguro si cambia totalmente, pero hay alguna mejora en ese sentido, bueno, entonces

## 48:31 - 48:38
una vez se hace, a ver que voy a quitar aquí la optimización para que no me salga a optimizar,

## 48:38 - 48:43
entonces esto se acaba la optimización, sale también nuestro informe igual, o sea cuando

## 48:43 - 48:46
hacemos el World Forward Optimizer también sacamos el informe este y lo podemos llevar

## 48:46 - 48:52
a Excel, de hecho ese que os he abierto era uno de World Forward, pero desde aquí vamos

## 48:52 - 48:56
a cargar el histórico y le vamos a hacer un proceso de World Forward ¿Vale? ¿Cómo se

## 48:56 - 49:01
hace un proceso de World Forward Optimizer? Esto que veis es la aplicación en cuestión,

## 49:01 - 49:07
que se abre desde dentro de 3D Station, es una de ellas, de todas estas que hay aquí,

## 49:07 - 49:12
entonces es esta World Forward Optimizer ¿Vale? Esto se abre, esa clic y aparece ese

## 49:12 - 49:19
programa ¿Vale? Aparece ese programa, bueno voy a abrirlo así de momento, aparece así,

## 49:19 - 49:26
abres un set que hemos optimizado que está aquí ¿Vale? Y aquí ahora eliges unas determinadas

## 49:27 - 49:35
opciones que os voy a explicar como se hace ¿Vale? Primero el criterio, bueno antes no

## 49:36 - 49:42
os he explicado las pruebas, os lo voy a explicar brevemente porque eso creo que es muy importante,

## 49:42 - 49:51
no solo el hecho de que, no solo el hecho de estos sets que habéis visto, todo este

## 49:52 - 49:58
cluster está mezclado entre autosample y run, sino esto que veis aquí, pass y fail,

## 49:58 - 50:05
que es ¿Vale? Esto verde tan chulo que es ¿Vale? Realmente al final el WFE lo que hace

## 50:06 - 50:12
en realidad es una prueba de estrés muy fuerte ¿Vale? Y nos va a dar al final un resultado

## 50:12 - 50:17
de pass o fail de cada uno de los clusters pero también en global ¿Vale? Él nos va

## 50:17 - 50:25
a decir si cree que el sistema pasa esta prueba ¿Vale? Y en que consiste pasar esta prueba

## 50:26 - 50:31
¿Vale? ¿En que consiste pasar esta prueba? Pues pasar esta prueba son estos 5 sets ¿Vale?

## 50:31 - 50:38
Estos 5 pruebas ¿Vale? Primero de ellos, que son configurables ¿Vale? Me vuelvo al

## 50:40 - 50:46
WF porque os lo voy a enseñar aquí ¿Vale? Son configurables, él tiene estos por defecto

## 50:46 - 50:51
pero son estas 5 que veis aquí, criterio 1, criterio 2, criterio 3, criterio 4, criterio

## 50:51 - 50:58
5 ¿Vale? El criterio 5 es que el sistema gane dinero ¿Vale? Parece bastante, con datos fuera

## 50:58 - 51:05
de muestra ¿Eh? ¿De acuerdo? O sea todas estas pruebas son a los datos o a la comparación

## 51:05 - 51:11
entre los datos fuera de muestra y optimizados, es decir los datos out of sample y in sample

## 51:11 - 51:16
¿Vale? Entonces que el sistema en total fuera de muestra gane dinero, incluso yo puedo cambiarlo,

## 51:16 - 51:21
puedo hacerlo más exigente si quiero ¿Vale? Que el WF Efficiency sea mayor que el 50%,

## 51:21 - 51:28
el WF Efficiency es lo que os decía antes, es el beneficio, lo que gana el sistema anualizado

## 51:28 - 51:35
¿Vale? Que sea al menos el 50% fuera de muestra que lo que gana dentro de muestra, es decir

## 51:35 - 51:40
si el sistema gana un millón en ese set que al menos gane 500.000 fuera de muestra, con

## 51:40 - 51:46
eso pasaría, de nuevo se puede endurecer la prueba, si quieres ponerlo 80, 90 o 100 ¿Vale?

## 51:46 - 51:52
100, cuando un sistema tiene un WF Efficiency, bueno no un sistema, un determinado cluster

## 51:52 - 51:57
tiene un 100% quiere decir que gana exactamente lo mismo fuera de muestra que optimizado

## 51:57 - 52:04
que eso es lo ideal ¿No? Eso sería lo ideal que hiciera exactamente lo mismo, no es fácil

## 52:04 - 52:09
pero es lo ideal ¿Vale? Pero normalmente la industria considera que el hecho que gane

## 52:09 - 52:16
un 50 se considera apto, se considera razonable porque puede haber un mercado distinto ¿Vale?

## 52:16 - 52:22
Además aquí la, si tenemos más de 100, hombre entendido, pero si es muy reiterado

## 52:22 - 52:28
y se aleja mucho es sospechoso, es sospechoso, habría que mirarlo, no quiero decir que no,

## 52:28 - 52:35
puede ser porque puedes tener, a ver caso típico, tu pruebas un sistema muy tendencial

## 52:35 - 52:41
el periodo en sample es poco tendencial y justo cuando el periodo fuera de muestra tiene

## 52:41 - 52:46
una tendencia inhumana, por lo mejor una muestra pega un, ¿Vale? Pero que pasa aquí, que

## 52:46 - 52:52
aquí no hablamos de un solo set, ahora lo ves, hablamos de muchos runs, entonces realmente

## 52:52 - 52:58
es una prueba que por eso en si, porque hay gente que dice, hombre el 50 me parece un

## 52:58 - 53:03
poco laxo, bueno pero es que no es a 1, o sea realmente lo vas a ver en un conjunto,

## 53:03 - 53:08
o sea no es en un único run como el ejemplo que habéis visto ahora anteriormente en una

## 53:08 - 53:14
columna, ese es un run, en el estadístico que os he enseñado en 3stations, la tabla,

## 53:14 - 53:19
había la columna de la derecha, que ahí en uno ponía 200, otro menos 50, eso era

## 53:19 - 53:26
el world floor of efficiency, de 1, 70 a 30, este es de por ejemplo los 5 runs que hayan,

## 53:27 - 53:34
los 5 fuera de muestra, es decir es una media de todos, por lo tanto y cada uno de ellos

## 53:35 - 53:43
corresponde a un periodo distinto, por lo tanto es una prueba que se aplica mucho a

## 53:43 - 53:48
lo largo del tiempo, por lo tanto tiene mucha validez estadística, ¿de acuerdo? Consistencia

## 53:48 - 53:55
de los beneficios, es decir, que ninguno, no es en la distribución de los beneficios,

## 53:59 - 54:06
quiero decir ahora, exacto, que ninguno de ellos, bueno se puede poner que todos ganen

## 54:06 - 54:13
o que al menos el 50% de ellos tengan beneficios, es decir, si tú tienes 10 runs, con cuántos

## 54:16 - 54:20
crees que tienen que haber ganado o cuántos perdidos, si yo le pongo 50 quiere decir que

## 54:20 - 54:25
al menos el 5 runs tiene que haber ganado, si le pongo 80 pues creen que al menos en

## 54:25 - 54:32
8 tiene que haber ganado, ¿vale? Fuera de muestra, insisto, lo vais a ver ahora en

## 54:33 - 54:37
plática y luego la distribución, ese también es importante, aunque ojo que este a veces

## 54:37 - 54:44
los tendenciales le cuesta de pasar, aunque Nemesis lo ha pasado, pero le cuesta, lo ha

## 54:45 - 54:51
pasado por muy poco, por este variable, ¿vale? Porque que ninguno de los runs contribuya

## 54:51 - 54:57
más de, en este caso, el 50% del beneficio total, es decir, que no haya 2, 3 que no ganan

## 54:57 - 55:01
nada y en uno de golpe gane todo, eso tampoco, lo que nos gusta es que el sistema realmente

## 55:01 - 55:06
demuestre que ha ganado dinero en distintos periodos, no solo en uno de ellos, ¿no? Y

## 55:06 - 55:13
para acabar el último variable es que el drawdown sea, en este caso, que ninguno de

## 55:13 - 55:24
los sets tenga más de un 40% de drawdown, ¿vale? Sobre capital inicial, bueno, ahora

## 55:24 - 55:27
vamos a verlo en práctico porque aquí os he querido enseñar aquí y la verdad es que

## 55:27 - 55:33
creo que aquí queda muy engorroso. Ahora os lo voy a enseñar en el ejemplo práctico,

## 55:33 - 55:37
¿vale? Aquí abajo veis un poco la idea y es esto, ¿ves? Él te dice de cada uno de

## 55:37 - 55:41
ellos si lo pasa o no, de cada uno de ellos, te dice el global, el global es que los tiene

## 55:41 - 55:47
que pasar todos, o sea, nada más que no pase uno, lo marca felt, o sea, tiene que pasar

## 55:47 - 55:52
las 5, sí, sí, por eso digo, que dices, el hecho de que sea 50% me parece largo, no,

## 55:52 - 56:01
no, no, los tiene que pasar todos, ¿vale? Los tiene que pasar todos, los tiene que pasar

## 56:02 - 56:09
todos, ¿vale? Entonces, volviendo al World Forward, aquí realmente lo que os quería

## 56:10 - 56:16
enseñar es, bueno, defines el capital inicial, defines cuál es la función fitness que eliges

## 56:16 - 56:20
para hacer esta mezcla. Realmente en este caso podéis incluso utilizar el profit, ¿verdad?

## 56:20 - 56:25
Entonces, ya viene, o sea, esto ya se basa en la muestra que ha obtenido en la optimización

## 56:25 - 56:29
hecha antes de The Station, es decir, si tú ya hayas elegido un determinado criterio

## 56:29 - 56:34
por algoritmo genético, es ese ya, o sea, tú no vienes ya de la totalidad del histórico

## 56:34 - 56:40
sino vienes de la serie de trades que ha obtenido de una optimización, por lo tanto, aquella

## 56:40 - 56:45
muestra ya está sesgada por el fitness que hayáis elegido en The Station, ¿me explico?

## 56:45 - 56:49
Que hayáis elegido al hacer aquí, o sea, aquí hayáis una optimización por un criterio

## 56:49 - 56:53
concreto, ¿no? Por ejemplo, expectancy score, por lo tanto la muestra ya viene un poco sesgada

## 56:53 - 56:57
por ese criterio, ¿vale? Por lo tanto nosotros solemos utilizar una mezcla de los tres que

## 56:57 - 57:02
nos gustan, pero bueno, de verdad que no es, en el World Forward Optimization no está

## 57:02 - 57:10
relevante, se puede hacer por el profit, ¿vale? Y una vez hacemos el set up, el start el cluster

## 57:10 - 57:18
análisis y al final llegáis, una vez acaba el proceso, que dura lo suyo, recomiendo hacerlo

## 57:18 - 57:27
por la noche, llegáis a un resultado, ¿vale? Llegáis a un resultado, son horas dependiendo

## 57:27 - 57:34
de, bueno, es depende mucho de los trades, claro, si es un sistema diario que tiene pues

## 57:34 - 57:38
depende, puede estar horas, puede estar horas, pero a lo mejor un diario no lo puede hacer

## 57:38 - 57:42
en una hora, en dos, para que a lo mejor un interés pues se tarda cinco horas, tres,

## 57:42 - 57:48
depende, realmente depende, depende de la muestra que tú hayas puesto, ¿no? Comparativamente

## 57:48 - 57:53
es bastante rápido, creo yo, este proceso, comparativamente es más lenta la optimización

## 57:53 - 57:56
clásica en 3D Session que el World Forward, la optimización lenta en 3D Session es un

## 57:56 - 58:01
tanto lenta actualmente, aunque está, ahora mismo ya digo, la 9.5 está en beta y por

## 58:01 - 58:05
fin van a utilizar el multicore, entonces se va a acelerar mucho, que está ya en beta

## 58:05 - 58:15
2, con lo cual, pues no sé cuánto, no sé cuántos meses tardará, ¿cómo? Sí, si eres

## 58:15 - 58:26
cliente, tú eres cliente de 3D Session, pero tienes cuenta, tú tienes cuenta, pero si

## 58:26 - 58:33
tienes cuenta lo que puedes hacer es irte, bueno, luego te lo cuento, te puedes solicitar

## 58:34 - 58:41
e inscribirte al beta tester, sí, entonces te avisa y te la instala si quieres, ¿vale?

## 58:42 - 58:46
Ten en cuenta que en el que la instales solo va con uno, yo aquí por ejemplo, justamente

## 58:46 - 58:50
para mí, puedes tener instaladas las dos, pero solo puedes tener activa una de ellas,

## 58:50 - 58:55
o puedes pasar de una a otra, yo ayer pasé de la 9.5 a la 9.1 aquí, para evitar que

## 58:55 - 59:01
no se me colgara cualquier historia, porque es una beta y falla, pero ahora mismo yo si

## 59:01 - 59:05
hablo de la 9.5 me va a decir que no, que tengo que activarla, tarda un rato, o sea

## 59:05 - 59:10
que no puedes simultanear las dos en el mismo ordenador trabajando abiertas, sí, sí, sí,

## 59:10 - 59:14
en el ordenador, pero abiertas no puedes tener abiertas la 9.1, si tienes una abierta no

## 59:14 - 59:21
puedes tener abiertas la otra, bueno, entonces tú llegas aquí y al final te presenta este

## 59:21 - 59:28
ejemplo histórico, en este caso, esto es un sistema intradiliario que vais a ver, para

## 59:28 - 59:35
que sepamos, para hacer lo más real posible el ejemplo, es este sistema que está operando

## 59:35 - 59:42
en canteras, que lleva unos días bastante buenos, la verdad, la verdad que le toca,

## 59:42 - 59:48
este ya pensé que tenía que perder, porque lleva 6, está casi en su récord, 1, 2, 3,

## 59:48 - 59:56
4, 5, 6, 7 seguidos, es casi récord, 7 seguidos acertados para un tendencial puro, es récord,

## 59:56 - 60:04
2, 3, 4, 5, 6, 7 seguidos, es rarísimo, tiene que palmar, no puede ser, pero ves,

## 60:04 - 60:09
este ya pensabas que iba a palmar y gana, por eso hay que seguir el sistema siempre,

## 60:09 - 60:17
y a lo mejor te pensas que ya no puede ser y también gana, no, no, es hombre, creo que

## 60:17 - 60:21
son sustos, pero es igual, no estamos aquí por eso, no me despises que tú te vas siempre

## 60:21 - 60:27
de una cosa a la otra, es un sistema tendencial puro y los temas tendenciales puros, pues

## 60:27 - 60:31
tienen, además, tiene aquí dragodrones, intradis fuertes, como este aquí, el susto

## 60:31 - 60:40
debe ser este, no lo veo ahora, aquí, esta vela, realmente tiene un sistema tendencial

## 60:40 - 60:45
puro que intenta dejar correr los beneficios y cortar las pérdidas, pero bueno, pues a

## 60:45 - 60:52
veces les pillan trades muy negativos, pero bueno, este es un sistema que todavía no

## 60:52 - 60:57
está disponible en alquiler, esperamos que no esté pronto, lo tenemos en carteras de

## 60:57 - 61:01
clientes operando, pero no en alquiler en los bloqueos españoles, pero es más por

## 61:01 - 61:08
un tema de tiempo que por otra cosa, esperamos que pronto esté, este chat, uno de ellos,

## 61:08 - 61:13
porque hay varios, uno de los que hemos hecho es este, este está hecho, pone la fecha por

## 61:13 - 61:20
aquí, no, no me acuerdo, pues esto ya lleva meses hecho, eh, no va a poner en ningún

## 61:20 - 61:29
sitio la fecha aquí, ah bueno, muy hábil, vale, esto acabó en octubre, 4 de octubre

## 61:29 - 61:36
del 2013, se hizo este set, desde ahí está una parte auditado y otra ya completamente

## 61:36 - 61:40
operando en live, o sea, todo esto que habéis visto, esto es todo live, esto está operando

## 61:40 - 61:44
no en esta cuenta que está, esta es demo, pero está exactamente igual operando live

## 61:44 - 61:51
en el oro, bueno, entonces aquí que tenemos, que al final nos da el resultado, en este

## 61:51 - 61:56
caso elegimos un fuera de muestra entre 10 y 30, que suelo elegir ese yo, y los runes

## 61:56 - 62:02
ya depende, depende, ¿de qué depende? Depende de los threads que tengamos, y aquí entramos

## 62:02 - 62:06
otra vez en aquella frase que os he dicho antes de que la muestra tiene que ser estadísticamente

## 62:06 - 62:14
significativa, ¿de acuerdo? Lo ideal es que cada rune sea estadísticamente significativo,

## 62:15 - 62:21
¿de acuerdo? Pero aquí sí que somos un poco más laxos que con una sola optimización,

## 62:21 - 62:24
¿por qué? Pues justamente por eso, porque cuando hacemos una sola optimización tenemos

## 62:24 - 62:32
una y aquí tenemos muchas de cada uno de ellos, aquí por poner este tenemos 20% con

## 62:33 - 62:39
15, tienes 15 runes distintos, cada uno de ellos se ha optimizado y se ha aplicado en

## 62:39 - 62:45
otro, pero no solo en este, tienes las pruebas de un montón, de un montón más de runes

## 62:45 - 62:50
distintas, ¿qué quiere decir? Que realmente tienes mucha información sobre la robustez,

## 62:50 - 62:57
o mejor dicho, por no utilizar conceptos confusos, sobre la adaptabilidad del sistema, ¿de acuerdo?

## 62:58 - 63:03
Porque realmente este rune con este no tiene que ver, o sea, este realmente hemos elegido

## 63:03 - 63:10
un período in-sample y out-sample 90%, 10% y le hemos hecho 5 cortes, 5 runs, en cambio

## 63:11 - 63:18
este de aquí, y tiene pass también, lo hemos hecho con un período de 30%, es decir, 70

## 63:18 - 63:27
in-sample, 30% out-sample y lo hemos hecho 25 runs, solo, y ha pasado, es decir, en estos

## 63:28 - 63:35
25 tiene más del 50% for all efficiency el consistency de todo lo que habéis visto,

## 63:35 - 63:43
¿vale? Esto es lo que se ve aquí en el test, que los ha pasado todos, es decir, gana dinero

## 63:43 - 63:50
de media gana más de un 50, más del 50% de los runs de los 25, es decir, al menos 13

## 63:50 - 63:56
ganan dinero de los 25, fuera de muestra todo, claro, contra más runs más difícil porque

## 63:56 - 64:01
lógicamente es más complicado, ninguno de ellos contribuye más del 50 y este tiene

## 64:01 - 64:05
especial mérito porque cuesta, cuesta porque es un tendencial y veréis que hay alguno

## 64:05 - 64:13
que está a punto, mira, a veces aquí tiene 45, 34, porque es normal en un tendencial,

## 64:13 - 64:17
es normal, los tendenciales tienen sistemas con colas muy largas, sistemas de aquello

## 64:17 - 64:22
de que realmente, aquello de la ley del paleto, hasta a veces haces más, realmente el beneficio

## 64:22 - 64:29
total de los sistemas tendenciales viene de muy pocos trades, porque cuando cogen tendencia

## 64:29 - 64:34
ganan muchísimo y luego se pasan mucho tiempo que ahora sí, un poquito, ahora no, a lo

## 64:34 - 64:39
tal, a lo mejor van ganando pero poquito, o perdiendo también, ¿no? Sí, por eso digo

## 64:39 - 64:46
que en esta, yo os confieso, os confieso que hice esta prueba, os confieso que en MSS

## 64:46 - 64:52
hice el workforce optimizer convencido que no lo pasaba, ¿vale? Convencido de que no

## 64:52 - 64:57
lo pasaba, ¿por qué? Porque es un sistema que acierta ya digo 35% de los trades, o sea

## 64:57 - 65:04
es un tendencial puro, vale, un tendencial puro y es muy difícil de que, yo pensaba

## 65:04 - 65:09
que no pasaría la distribución, vale, o sea que habría algún set, de hecho hay alguno

## 65:09 - 65:15
que lo tiene, este yo creo que es por eso que no debe pasar, ¿ves? Por la distribución,

## 65:15 - 65:39
porque el run 2 contribuye más de 50%, disculpe, el porcentaje, bueno, aquí utilizamos de

## 65:39 - 65:48
10 a 30, no, no, pero cuál utilizo quiere decir luego para operar, no, ahora llegaremos,

## 65:48 - 65:53
ahora llegaremos, de momento no hemos hablado nada de operar, esta prueba es una prueba

## 65:53 - 66:00
de estrés, lo que buscamos aquí es que aquí donde pone matrix average ponga pas,

## 66:03 - 66:09
si pone pas estamos contentos, quiere decir que el sistema es un sistema objetivamente

## 66:09 - 66:15
robusto, ¿por qué? Porque hemos conseguido que se adapte a muchas condiciones de cambio

## 66:15 - 66:20
de mercado porque, insisto, este set de aquí, estos 5 run no tiene nada que ver, o sea este

## 66:20 - 66:26
primero es de 2011, 2011 tal, o sea, no tiene nada que ver este con este, claro, porque

## 66:26 - 66:30
al haber 25 imagínate la diferencia, o sea, realmente es muy distinto los períodos de

## 66:30 - 66:37
uno y otro, y en todos ellos ha conseguido demostrar que se adapta, o sea que optimizando

## 66:37 - 66:43
un periodo y aplicando mejor parámetro consigue ganar dinero, consigue todo lo que hemos dicho,

## 66:43 - 66:47
las 5 pruebas, ¿no? Y no tiene un drama mayor de un 40, etcétera, etcétera, o sea todo

## 66:48 - 66:55
eso, ¿no? Entonces lo que primero busco es eso, que es robusto, luego ya tú me preguntas

## 66:55 - 66:59
¿qué parámetros elegirías? Bueno, luego la fijación de parámetros, lo voy a comentar

## 66:59 - 67:04
brevemente porque no tenemos tiempo de profundizar, esto la idea es un poco hablar de 3-station,

## 67:04 - 67:09
o sea, es un... para enseñaros la herramienta y que luego vosotros podáis profundizar

## 67:09 - 67:16
en ella, ¿no? Tenemos pensado en el tiempo hacer ya cosas más de sistemas, más aplicado

## 67:16 - 67:19
a la... a cómo elegirías todos los parámetros de un sistema, bueno, pues podemos hacer

## 67:19 - 67:23
un seminario de eso, ¿no? Pero aquí es más que entendáis la herramienta y que la podáis

## 67:23 - 67:31
utilizar, ¿vale? Luego, por folio maestro, es otra aplicación, sí, la respuesta es

## 67:31 - 67:36
sí, pero no aquí, no en esta. Vale, entonces aquí llegamos a la conclusión que lo pasa,

## 67:36 - 67:41
¿vale? Aquí brevemente ya digo, os comento lo que hay, fijaros que tenéis los datos de

## 67:41 - 67:46
todo, de todos los in-sample que hay, de todos, el periodo de optimización, qué parámetros

## 67:46 - 67:52
he elegido, como veis, pues profit, drawdown, blablá, trades, profit factor, de cada uno

## 67:52 - 67:56
de ellos y también de los de fuera de muestra, de todos, todos, de cada uno de ellos tenéis

## 67:56 - 68:02
los estadísticos principales, abajo tenéis la media, ¿vale? El mayor, el menor, ¿vale?

## 68:02 - 68:07
Y aquí fijaros que en un in-sample ya te da, por ejemplo, un deratio que también es

## 68:07 - 68:13
importante, el post optimisation risk, que es 1,5 veces el drawdown medio que ha obtenido,

## 68:13 - 68:19
aquí el drawdown está aquí, ¿vale? Tiene 12, pues te da 18, ¿qué quiere decir ver

## 68:19 - 68:23
si alguno de ellos ha pasado ese 18? Fijaros que ninguno tiene más de 18, eso te aprueba

## 68:23 - 68:29
más que nos da confianza, ninguno de los hechos ha tenido más de 18 medio drawdown,

## 68:29 - 68:34
es decir, que las previsiones, las previsiones, pues van bien, van bien, porque eso todo esto

## 68:34 - 68:39
es fuera de muestra o al final es como si fuera live, estamos de acuerdo, eso es como

## 68:39 - 68:45
si aquí ese día hubiéramos activado el sistema live, con esos parámetros, ¿no? El beneficio

## 68:45 - 68:51
anualizado, esta es la variable que compara, ves, para obtener el world forward, ves, 100%,

## 68:51 - 69:01
100, 32, 32, se ha ganado lo mismo, el sistema ha ganado en este conjunto que es 15% autosample,

## 69:01 - 69:11
10 runs, en este conjunto tienes 100% world forward de efficiency, y tenemos aquí distintos

## 69:11 - 69:18
ratios de student, desviación estándar, bueno, hay distintos ratos, ¿vale? Y como no, este

## 69:18 - 69:26
a mi me encanta, y tenéis la curva de todo el sistema, de todos esos sets, tenéis el

## 69:26 - 69:31
primero que es in sample, por supuesto, porque claro, el primero tiene que ser in sample,

## 69:31 - 69:37
pero a partir de aquí todo es la curva hecha con los distintos enganches de cada periodo

## 69:37 - 69:47
fuera de muestra, y también todos los straights fuera de muestra, y podéis sacar el performance

## 69:47 - 69:50
report, por defectos todo, pero si queréis solo elegir fuera de muestra, pues lo elegís,

## 69:50 - 70:12
desde 2009-612 lo sacas, no exactamente, me preguntan si se puede, ahora vamos a ver algo

## 70:12 - 70:16
parecido a eso, algo parecido a eso, me preguntan si se puede ver que día de la semana ha ido

## 70:16 - 70:24
mejor el sistema, y bueno, no exactamente en esta prueba, repito que debemos centrarnos

## 70:24 - 70:32
en que esta prueba es una prueba de estrés, ¿de acuerdo? Lo que buscamos es verificar

## 70:32 - 70:39
o tener la mayor probabilidad posible de que el sistema que hemos hecho y que hemos estudiado

## 70:39 - 70:45
para ganar dinero en el futuro, ¿vale? Eso es lo que más probablemente buscamos, acabo

## 70:45 - 70:50
de pronto caer, si, de pronto he tenido un lapsus, digo, he activado el micro en el hangout,

## 70:50 - 71:01
digo, si me doy cuenta que no, bueno, estaba activo, bueno, y esta es la equity preview,

## 71:01 - 71:05
esto es un poco, no es lo que usted me preguntaba, pero aquí sí que puedes ver un conjunto

## 71:05 - 71:10
de parámetros concretos, ¿qué curva tendría? Un conjunto de parámetros, ¿vale? Y aquí

## 71:10 - 71:16
en la distribución puedes ver también análisis de distribución, es que no quiero profundizar

## 71:16 - 71:21
mucho porque si no no voy a llegar a otra cosa, esto como buen sistema tendencial, pues

## 71:21 - 71:28
como os decía, sistema de colas muy largas, ¿vale? Típico sistema tendencial donde tiene,

## 71:28 - 71:34
bueno, luego además puedes hacer pruebas de Monte Carlo, pruebas de Monte Carlo, incluso

## 71:34 - 71:37
la optimización de raíz se puede hacer de Monte Carlo, pero yo personalmente no os lo

## 71:37 - 71:41
recomiendo, ya aquellos que me conocéis, ya sé que Monte Carlo, todo el mundo de los

## 71:41 - 71:46
sistemas hablan de Monte Carlo, Monte Carlo es una herramienta interesante, pero a mí

## 71:46 - 71:50
una herramienta que siempre me da el mismo resultado, pues no me hace falta hacerla porque

## 71:50 - 71:56
ya lo sé que me va a dar, entonces a mí Monte Carlo como yo los backtests que hago

## 71:56 - 71:59
ya son significativos, o sea tienen muchos traits normalmente, o sea realmente es una

## 71:59 - 72:04
muestra estadísticamente significativa, normalmente Monte Carlo empeora un 20, un 30, un 50% de

## 72:04 - 72:10
los resultados, entonces pues bueno, ya más o menos por ahí se mueve, ¿no? Pero bueno,

## 72:10 - 72:15
sí que va a haber a veces sacar este tipo de, o sea Monte Carlo para aplicar, digo Monte

## 72:15 - 72:19
Carlo convencional que la mayoría de gente lo usa un poco para fijar el capital inicial,

## 72:19 - 72:23
para ver el draudón que puedes esperar, para un poco esos criterios, ¿no? Donde sí que

## 72:23 - 72:29
para mí es útil, por ejemplo, para percibir escenarios, ¿no? Para ver en qué porcentaje

## 72:29 - 72:32
hay de que el sistema esté ganando dinero en un año, cosas así, no sé qué me parece,

## 72:32 - 72:38
por ejemplo, puede ser interesante, ¿vale? Bueno, hasta aquí brevemente la explicación

## 72:38 - 72:44
del World Forward Optimizer, ¿vale? Antes os he comentado que también puede servir

## 72:44 - 72:50
para fijar parámetros, ¿vale? Me lo preguntaba usted antes a nivel de parámetros, ¿vale?

## 72:50 - 72:56
Entonces, una ventaja extra que no todo el mundo utiliza, que nosotros donde podemos

## 72:56 - 73:02
utilizar utilizamos y de hecho en nemesis lo estamos utilizando, ¿vale? Este es el clúster

## 73:02 - 73:08
además donde fijamos parámetros, os lo voy a demostrar, creo que el mejor, bueno, aquí,

## 73:08 - 73:12
perdón, muy breve, aquí antes me preguntaba usted si se pueden ver todos los datos, es

## 73:12 - 73:17
aquí, ves, aquí tú tienes el resumen, pero aquí puedes ver el anualizado, de cada de

## 73:17 - 73:21
los sets, el World Forward Efficiency de cada uno, ves, todos, fíjate que hay muchos

## 73:21 - 73:30
con 100 o con 80, 90, muchos, no es uno, claro, si veis solo uno, pero realmente hay una armonía,

## 73:30 - 73:36
hay una armonía en todos los sets, realmente se ve una distribución ordenada, ¿no? Hay

## 73:36 - 73:41
una zona mejor que otra, pero bueno, pero aquí está el 56, que el 56 con 25 runs,

## 73:41 - 73:45
o sea, sigue optimizando cada dos por tres, sin parar, optimizo, pero optimizo, pero esto

## 73:45 - 73:52
es, si haces los periodos de optimización, fíjate que deben ser nada, son 200 días,

## 73:52 - 73:59
200 días optimiza, 90 opera, 200 días optimiza, 90 opera, y con eso ha pasado, es que no me

## 73:59 - 74:07
lo creo ni yo. O sea, con eso ha pasado, haciendo 200 días optimizo, 90 operó, 200 días optimizo,

## 74:07 - 74:18
90 operó, ¿vale? Bueno, el que tú fijes, o sea, tú la muestra, el histórico, tú

## 74:18 - 74:23
lo has marcado aquí en Travestation, o sea, la optimización que hablas aquí, tú en

## 74:23 - 74:30
el histórico que quieras, y luego tú eliges el número de días, pero no por días, sino

## 74:31 - 74:36
por este porcentaje que hemos dicho, ¿no? Tú eliges entre el 5 y el 30%, perdón, entre

## 74:36 - 74:41
el 10 y el 30% fuera de muestra, y con esa variable eliges qué tamaño tiene en el sample

## 74:41 - 74:45
y otro sample de la muestra que tú habías elegido inicialmente en Travestation, o sea,

## 74:46 - 74:58
vamos a iniciar el existo aquí. No, sí, a priori sí, a priori sí, o sea, a priori,

## 74:58 - 75:03
es lo que decíamos antes, ¿no? A priori, tú me dices, hombre, que es más tiempo,

## 75:03 - 75:08
lo que pasa es que un sistema, eso es un sistema que va en 30 minutos, eh, un sistema que va

## 75:08 - 75:12
en velas de 30 minutos, ¿vale? Entonces depende, tú tienes, aquí hay varias teorías y las

## 75:12 - 75:18
dos son varias, depende, lo que te decía, si tú consigues con una optimización no

## 75:18 - 75:23
excesivamente extensa, bueno, cuando no hablo no excesivamente extensa, esta empieza en

## 75:23 - 75:31
2007, ¿vale? Va de 2007 a 2013, bueno, un poco, son años en un 30 minutos, eh, ¿vale?

## 75:31 - 75:35
Estamos hablando de un sistema que va en 30 minutos, ¿vale? Pero el fenómeno salió

## 75:35 - 75:41
a cero desde 2000, bueno, adelante, pruébalo, no, o sea, no hay ningún problema, pasa que

## 75:41 - 75:47
estamos hablando de un 30 minutos, si tú realmente desde ese período consigues adaptar

## 75:47 - 75:52
una ventana, una manera de optimizar y de reoptimizar que al final da resultados como

## 75:52 - 75:58
estamos viendo, tú puedes llegar a la conclusión que por qué no seguir usando ese método,

## 75:58 - 76:03
¿no? O sea, si yo, vamos a suponer, si yo aquí he visto que optimiza, en este caso,

## 76:03 - 76:09
891 días y opera 154, que esto varía porque va por barras, ¿cómo ves, vale? O sea, donde

## 76:09 - 76:12
lo cuadra es en barras y a veces los días pues puede variar por fiestas, por historias,

## 76:13 - 76:19
pero fíjate que más o menos son 891 días, o 29500 barras, optimiza y opera, optimiza

## 76:19 - 76:26
y opera, ¿vale? Si tú llegas a la conclusión que esa manera de reoptimizar es buena, funciona,

## 76:26 - 76:33
tienes ratios que te gustan, ¿por qué no seguir optimizando así? Y es donde entra

## 76:33 - 76:37
esta método que os decía de fijación de parámetros, ¿de acuerdo? Walford automation

## 76:37 - 76:51
se puede utilizar para fijar los parámetros para operar, no aplicaría, no, esto es real,

## 76:51 - 76:59
pero aplicaría en qué, en qué, no me entiendo. Esta optimización empieza en 2007, ¿vale?

## 77:00 - 77:05
Pero si esto lo he hecho yo, o sea, esto lo he hecho yo, lo he hecho mi empresa, o sea,

## 77:05 - 77:12
esto lo hemos hecho los otros. No, no es que, no, es depende, es depende, al final lo que

## 77:12 - 77:18
yo quiero, insisto, es una muestra significativa, una muestra y un sabistica significativa,

## 77:18 - 77:24
en el oro, irse más atrás, en mi opinión, hacemos una reflexión ahora, puede tener

## 77:24 - 77:29
un problema, ¿vale? Porque hemos intentado no irnos, o sea, yo me he ido lo menos atrás

## 77:29 - 77:36
posible en el oro, ¿vale? Lo menos atrás posible, ¿para qué? Para tener muestras significativas.

## 77:36 - 77:40
Fíjate que aquí, no hemos hablado, tienes los stretch in sample, los stretch out of

## 77:40 - 77:45
sample, fíjate que los stretch out of sample aquí de media tienen un 98. En esta prueba

## 77:45 - 77:51
se considera que con 30 son aptos, a mí me parece un poco justo, pero se puede utilizar

## 77:51 - 77:56
porque no es uno, son muchos de 30, ¿vale? Volvemos un poco a la idea de que si tú tuvieras

## 77:56 - 78:03
solo uno de 30, sí que es poco, pero si tienes 10 de 30, claro, que uno realmente esté sobre

## 78:04 - 78:09
optimizado, pero que los 10 lo estén, pues es más difícil, y además de otro set igual,

## 78:09 - 78:13
¿no? Porque hay muchos clusters y realmente si tú ves fail, que ahora te voy a enseñar

## 78:13 - 78:20
uno luego con todo fail, claro, si ves solo dos paths, no, vale, o sea, insisto, lo primero

## 78:20 - 78:27
es que aquí ponga paths, si no pone paths, ni parámetros ni leches en vinagre, o sea,

## 78:27 - 78:33
no vale, no vale este método, entonces no, pero si vemos que hay un paths general, podemos

## 78:33 - 78:36
pensar también en esta situación, porque hemos visto que el sistema se ha adaptado

## 78:36 - 78:43
muy bien, ¿vale? Entonces, entonces yo aquí, ¿por qué en el oro hago eso? Pues en el oro

## 78:44 - 78:49
hago eso, nos va a quedar mal esto por otro día, lo veo, nos va a quedar mal esto por

## 78:49 - 78:53
otro día, ¿por qué hago eso? Pues lo vas a ver enseguida, ¿por qué hago eso? Porque

## 78:53 - 78:58
Nemesis ahora mismo, un sistema que estamos muy atentos y de momento estamos muy contentos,

## 78:58 - 79:01
porque Nemesis está, en mi opinión, como desarrollador de sistemas, en una situación

## 79:01 - 79:08
de riesgo, ¿vale? Al final, cuando uno ya lleva años, pues ya intentas ver por dónde

## 79:10 - 79:16
pueden ir un poco el movimiento de las variables de los parámetros, ¿vale? De hecho, aquellos

## 79:16 - 79:20
que me hayan oído otras veces, digo que yo optimizo mucho, pero no solo para elegir

## 79:20 - 79:25
parámetros, optimizo mucho para ver cómo se mueve el optimizador, ¿de acuerdo? O sea,

## 79:25 - 79:29
cómo se va moviendo con los nuevos datos las zonas de los parámetros, porque eso te

## 79:29 - 79:35
va dando un poco de información de hacia dónde va el sistema, ¿no? Bueno, eso sí

## 79:35 - 79:42
que depende. Nosotros mensualmente intentamos hacerle una pequeña revisión, pero no siempre

## 79:43 - 79:50
implica una optimización masiva con el protocolo de evaluación heavy, ¿vale? Pero sí que

## 79:50 - 79:57
nuevamente miramos. Siempre que una variable de riesgo nos hace récord en live, ya vemos

## 79:57 - 80:04
que... o sea, cualquiera. Traits consecutivos en negativos, drawdown, media perdedora, cinco...

## 80:07 - 80:13
No, no, no, no. Ahora hablo de la operativa en live. No, no, no, no. Ahora no estoy hablando

## 80:13 - 80:17
de what for optimizer. Ahora digo, ¿estamos operando? En general veo que el sistema se

## 80:17 - 80:24
me desvía de lo previsto, in sample, no. Pues valor, ¿no? Al final, en esta cada una

## 80:27 - 80:32
de ellas, pues estos ratios tienes una media, todos ellos se mueven en un parámetro parecido.

## 80:32 - 80:39
No, lo reviso. Lo reviso y vemos. A veces hay que reoptimizar, a veces... Bueno, a veces

## 80:45 - 80:52
depende. A veces se para, a veces no. En principio no se para, pero bueno, tampoco te digo que

## 80:52 - 80:57
no se para. Es decir, depende. Pero en principio no, ¿vale? Entonces, ese sistema va sobre

## 80:57 - 81:01
el oro en 30 minutos. Esto es el oro semanal, pero te lo muestro para que me enseñes. El

## 81:01 - 81:06
oro ha cambiado, claramente, de tendencia a largo plazo. Entonces, si yo cojo mucho

## 81:06 - 81:13
histórico antiguo, voy a coger un periodo de alcista, alcista, alcista, alcista, alcista.

## 81:13 - 81:18
Corro el riesgo de ajustarme en exceso a ese mercado alcista que poco tiene que ver con

## 81:18 - 81:25
el actual, ¿vale? Entonces, me he ido para atrás, pero intentando no ir, intentando,

## 81:25 - 81:30
ya digo, lo menos posible para mantener la muestra estabísticamente significativa.

## 81:30 - 81:35
Para tener bastante histórico real. Y de hecho, ya hemos hecho un set en este mercado,

## 81:35 - 81:39
ya ha ganado dinero. Que quiero por eso decir que está en peligro, porque puede ser, fijaros

## 81:39 - 81:45
ahora aquí, como veis, fijaros que estos parámetros, los últimos sets, fue este el

## 81:45 - 81:51
que elegimos, espérate, lo tengo apuntado, sube, porque ya sé que voy a abrir y tengo

## 81:51 - 81:55
que empezar a matar a todo el mundo y no es plan. A ver, me parece que sí que fue este,

## 81:55 - 82:00
pero fíjate que este último set realmente ha hecho un cambio bastante notable en los

## 82:00 - 82:08
parámetros anteriores. ¿Lo vemos? Y el siguiente se ha parecido al anterior. ¿Veis que habéis

## 82:08 - 82:14
empezado 41-13, 41-12, 37, aquí un variable cambia y además, justamente, me parece que

## 82:14 - 82:20
no le va bien. ¿Ves? O sea, ahí cambia de zona y realmente falla, o sea, realmente la

## 82:20 - 82:25
zona seguía siendo la misma. Bueno, puede pasar, eso es la vida real. Pero aquí fíjate

## 82:25 - 82:30
que pega un cambio, se va a 35-11 y el tercero, fíjate que en ningún caso lo ha dado, ese

## 82:30 - 82:37
11 no había salido nunca, había salido este 10 y había perdido, ¿vale? Aquí sale 35-11,

## 82:37 - 82:44
11, 11, cambia bastante, es decir, que se nota que el sistema está como cambiando y gana,

## 82:44 - 82:51
gana 16 en la media. Y el siguiente que es el life y esto que estáis viendo, esto 35-94010

## 82:52 - 83:02
es esto, este sistema está operando con esos parámetros. ¿Lo veis? 35-94010, este sistema

## 83:03 - 83:08
está operando con esos parámetros. Ya veis que mal no está yendo. O sea, es esto que

## 83:08 - 83:12
habéis visto con todos los traits acertados consecutivos, que es una aberración histórica,

## 83:12 - 83:20
yo creo que puede estar en el récord, te lo digo en serio. Sí, sí, no, no, no, en 7,

## 83:20 - 83:26
ahora mismo no quisiera, a ver, ¿cuánto está cargado? No quisiera decir una cosa por otra,

## 83:26 - 83:31
pero si no hay récord está ahí, o sea, seguro, seguro, o sea, no es, no es, porque aquí no

## 83:31 - 83:35
vienen los winnings, ¿no? Ah, bueno, pero en el performance sí, en el performance sí,

## 83:35 - 83:44
8, falta uno para igualar su récord histórico en life, operando en life, quiere decir que

## 83:44 - 83:51
sigue mostrando que el life va como tiene que ir, bueno, como esperamos que vaya, ¿no?

## 83:54 - 84:01
Este es solo en oro, este sí, pero está previsto trabajarlo en más, pero de momento solo lo

## 84:01 - 84:05
tenemos preparado para, o sea, solo está acabado y operando y tal, pues claro, lleva su tiempo

## 84:05 - 84:11
y tal, pero de momento solo está operando en oro, en 30 minutos, en el GC, este código

## 84:11 - 84:19
que ves, entonces, bueno, lo que íbamos, que no sé qué era, sí, cualquier sistema

## 84:23 - 84:31
tendencial, Roberto, estamos donde estamos, a ver, en principio es un sistema muy tendencial,

## 84:32 - 84:37
pero bueno, eso ahora mismo ya digo no nos interesa mucho, fíjate que los lives también

## 84:37 - 84:41
son muy parecidos a los anteriores y además se ha vuelto a cambiar a 4 y dices, oye, hay

## 84:41 - 84:48
que ver, ¿no? Y este va, este lo ha optimizado hasta octubre y desde ese momento está en

## 84:48 - 84:53
life, claro, no sabemos lo que ha hecho porque va en life, hay que ver cuando acabe el periodo,

## 84:53 - 85:00
cuando acabe el periodo lo diríamos, y cuando acaba el periodo, pues aquí, en OS más 1,

## 85:02 - 85:07
o sea, te da en la optimización que le toca, este sistema le toca optimizar el 11 de marzo

## 85:07 - 85:16
2014, o sea, el 11 de marzo le toca un nuevo run, habrá que calcularlo, si todo sigue

## 85:16 - 85:21
igual y seguimos yendo igual, pues le tocaría en agosto, 16 de agosto, un nuevo run, pero

## 85:21 - 85:25
bueno, lo podemos ir haciendo y cambiar de ventana, si consideramos, pero de momento

## 85:25 - 85:31
ya tú sales a operar con un programa de optimización, está hecho así, o sea, está la ficha,

## 85:31 - 85:38
eso me parece que sí que lo puedo enseñar, a ver, sí, exacto, que está, esa es la ficha

## 85:38 - 85:44
que tenemos de nemesis, además también hemos hecho incluso, o sea, he hecho esta pero también

## 85:44 - 85:50
hemos hecho lo normal, tenemos los dos datos comparados, a un sitio está apuntado a la

## 85:50 - 85:57
optimización, no lo veo aquí, está en el calendario en todo caso, aquí nos ha apuntado,

## 85:57 - 86:07
bueno, pues aquí nos ha apuntado, está en el calendario, entonces, este sistema hemos

## 86:07 - 86:12
fijado los parámetros así, ¿por qué? Porque nos da mucha confianza, un SEMA tendencia

## 86:12 - 86:18
ya ha pasado la prueba así, porque realmente ha demostrado mucha consistencia, porque el

## 86:18 - 86:25
world format es muy alto, por decentes razones, y sobre todo, sí, solo sí, tenemos suficientes

## 86:27 - 86:34
trades fuera de muestra en cada uno de ellos, más de 50, en una serie de runs de 10 runs,

## 86:34 - 86:40
con más de 50 estaría cómodo, fíjate que la media es 98, 98 trades cada set fuera de

## 86:40 - 86:45
muestra, y además, repito, sé que me había acerpesado pero es que es muy importante,

## 86:45 - 86:50
o sea, esta muestra en sí es la que elige parámetros, pero realmente a mí la información

## 86:50 - 86:56
me la dan todos, o sea, lo que le da fuerza a ella misma es que la ha pasado en todos,

## 86:56 - 87:03
vale, es decir, al final yo elijo con una de ellas, o sea, yo me quedo con una, pero

## 87:03 - 87:10
claro, es que la de al lado tampoco estaba mal, es decir, las otras cediscos es que se

## 87:10 - 87:18
ha salido, sí, las dos cediscos quiere decir que ha pasado, cada cedisco es que ha pasado

## 87:20 - 87:25
alguno de ellos con nota especial, es decir, world forward más de 100, o sea, pass es

## 87:25 - 87:31
50, pero si da más de 100 le marca este disco, y en el consistency of profits es más del

## 87:31 - 87:38
80, si le pones estrella es que se ha salido, pero si uno da fail lo marca failed, o sea,

## 87:39 - 87:44
si aquí hubiera salido failed marca failed, o sea, los tiene que pasar todos igual, o

## 87:44 - 87:54
sea, tírales algo, a ver, fíjate que tiene muchas estrellitas también, o sea, además

## 87:54 - 88:02
tiene bastantes estrellitas, entonces, no, la zona verde él elige el centro, en este

## 88:03 - 88:07
caso sí, pero yo no siempre me quedo con la zona verde, no siempre me quedo con la zona

## 88:07 - 88:13
verde, yo luego analizo un poco cada uno de los, cada uno de los, de los parámetros,

## 88:13 - 88:22
no solo el paso, no, Javerto, por favor, a ver si encuentro como el patio colegio empezando

## 88:23 - 88:30
a remartir aquí, avisos, a ver, entonces, yo reviso cada uno de ellos, de acuerdo, cada

## 88:32 - 88:35
uno de ellos, y entonces elijo, porque fíjate que cada uno de ellos te marca una zona,

## 88:35 - 88:42
él calcula el punto donde tiene, está más rodeado, o sea, no calcula el que es el mejor,

## 88:42 - 88:48
sino calcula el que está mejor rodeado, ¿me explico? ¿Por qué? Porque piensa en el error,

## 88:48 - 88:53
¿no? Porque piensa si se desvía, que se desvía a un sitio bueno, ¿no? Vale, entonces sí

## 88:53 - 89:00
que normalmente es una guía, pero no, en este caso que los pasa todos, pues bueno, hubiéramos

## 89:00 - 89:03
podido elegido, pero en este hemos elegido este porque realmente es el que me gusta

## 89:03 - 89:07
más, está más equilibrado en todas, fíjate, no es solo uno, en el beneficio anualizado

## 89:07 - 89:11
es el que más gana, bueno, no, gana más este, pero yo en caso que no haya mucha diferencia

## 89:11 - 89:18
siempre intento irme a más runs, por lo mismo que más trades, ¿no? Vale, siempre

## 89:18 - 89:25
en caso de duda me voy a más runs, ¿vale? Claro, dices, hombre, pero el hecho que a

## 89:25 - 89:29
medida de más runs vaya perdiendo eficacia no es mala señal, no, no, porque en el fondo

## 89:29 - 89:33
te está diciendo, claro, pensá que cuando más runs estás optimizando períodos muy

## 89:33 - 89:39
cortos, o sea, claro, realmente estás, o sea, es más fácil sobreoptimizar, ¿vale?

## 89:41 - 89:44
O sea, es más fácil sobreoptimizar en un histórico de 11.000 barras que en uno de

## 89:44 - 89:49
20.000, pues claro, en este de 25.000, jate, que son 300 días, o este ya al extremo, ¿no?

## 89:49 - 89:55
Es este que hemos dicho solo optimizado 100 días, optimizado 100 días, claro, es más

## 89:55 - 89:59
fácil ahí reoptimizar, o sea, es más fácil que realmente no hayas captado la señal,

## 89:59 - 90:04
¿no? Pero bueno, también nos sirve bien este, fijaros, esto lo miramos, por ejemplo,

## 90:04 - 90:10
ves, para ver este que tiene muchas optimizaciones, ver los últimos que también, fijaros, que

## 90:10 - 90:14
ya ha hecho el cambio, ves, que decía el cambio de parámetros, como han ido, ¿vale?

## 90:14 - 90:19
Los últimos como han ido y este ha perdido, pero no mucho, no podemos considerar que sea

## 90:19 - 90:26
una gran aberración, en el histórico ha perdido bastante más y el anterior gano mucho,

## 90:26 - 90:35
¿vale? Y esto ya es desde 2013, septiembre de 2013, ¿vale? Esto ya es desde septiembre

## 90:35 - 90:41
de 2013, si vamos aquí, es desde aquí, o sea, ya es clarísimamente en el mercado

## 90:41 - 90:47
este, o sea, este mercado podemos decir que está ya metido desde 2011, ¿vale, Loro?

## 90:47 - 90:53
O sea, que ya hay, incluso en estos, jate, ya tienes muchos, ¿vale? Pero sobre todo

## 90:53 - 90:58
los últimos, en este caso, cuando hay menos sets, ¿vale? Porque este tiene muchos, pues

## 90:58 - 91:04
son los últimos, ¿vale? Los últimos ya son fuera de muestra, han sido en el periodo bajista

## 91:04 - 91:09
y aquí tiene más 16, más 26, más 16, menos 3, más, realmente desde aquí ya está en

## 91:09 - 91:13
el periodo bajista, este quizá es el primero que pierde, este puede ser que sea el primero

## 91:13 - 91:17
que pierde, que no capta la señal, puede ser el cambio de mercado, creo que iba por

## 91:17 - 91:26
ahí, sí, exactamente, este coge ya un poco de mercado bajista, es el primero, ves, acaba

## 91:26 - 91:33
en enero de 2012 y viene desde 2009, este acaba por aquí de optimizar, optimiza de

## 91:33 - 91:41
por aquí a aquí y falla, pero ya al siguiente ya no, es que ya le ha cogido la, ya le ha

## 91:41 - 91:46
captado otra vez la señal, ¿vale? Así que el método funciona, es que la reoptimización

## 91:46 - 91:53
consigue captar la señal del mercado, ¿no?, consigue captar de momento, ¿algún día puede

## 91:53 - 91:56
cambiar? Eso sí, o sea, yo siempre digo, los sistemas no son algo estáticos, no son,

## 91:56 - 92:00
no hay que pensar que uno, mucha gente me dice, ah, pon un sistema, te lo pones en la

## 92:00 - 92:07
playa y a vivir, no, no, no, no, no es eso, no es eso, o sea, además hay que trabajar,

## 92:07 - 92:11
hay que seguirlo, o sea, no, no es eso, no es eso, o sea, sería también deseable, pero

## 92:11 - 92:15
no es eso, los sistemas hay que estar encima, no se más pueden dejar de funcionar, hay

## 92:15 - 92:19
que revisarlos, hay que trabajar en ellos, no es, no es coger un sistema de encontrar

## 92:19 - 92:23
que funcione a este, el nemesis y hasta, hola, ya hemos encontrado la gallina de los huevos

## 92:23 - 92:28
de oros, punto, lo pongo a todo el dinero, me vendo la casa, lo pongo todo en este sistema

## 92:28 - 92:32
porque va a ser la bomba, dos años, deja de funcionar, arruinado, no, hay que estar

## 92:32 - 92:36
diversificado, hay que tener varios sistemas, es igual, aunque este ahora mismo es el que

## 92:36 - 92:41
nos parece mejor, tenemos más operando en la cartera, ¿por qué? porque a lo mejor

## 92:41 - 92:46
es el que parece mejor, de hecho, ahora ni que sea brevemente os enseñaré el maestro

## 92:46 - 92:51
y veréis que ese sistema en esa cartera con otro habrá ido muy bien, pero en otras periodos,

## 92:51 - 92:56
¿no? Vale, a ver, sobre World Forward, os enseño

## 92:56 - 93:00
por ejemplo que no, aquí es que no los tengo todos porque es el portátil, es el que uso

## 93:00 - 93:07
más así en casa, digamos que en el despacho está el que hace más estas cosas, pero alguno

## 93:07 - 93:17
más, este es, ah, pero es bruto, esto no vale, este, a ver, ¿esto qué era? Ah, no, me equivocaba,

## 93:17 - 93:36
no hablaba de los cruceros, no, este puede ser, ¿veis? Este es un ejemplo de prueba

## 93:36 - 93:46
fallada, tiene también verdes, pero tiene muchos fails, hay que trabajar más, necesita

## 93:46 - 93:53
mejorarlo, no, este es un sistema que está operando, o sea, este sistema no ha fijado

## 93:53 - 93:58
los parámetros así, este sistema, no, en el SCP, este sistema, concretamente, de una

## 93:58 - 94:03
de las versiones que tenemos, lo puedo decir objetivamente porque he conseguido los datos,

## 94:04 - 94:10
los sistemas habilitados que están en Train Motion, que son 500, es el mejor sistema del

## 94:10 - 94:16
SCP que más beneficio por garantías ganó el año pasado, 49%, este, una versión de

## 94:16 - 94:26
este, bueno, este, o sea, a ver, esto al final viene, claro, a ver, esto viene al final de

## 94:26 - 94:32
una optimización que tú eliges, puede ser, no recuerdo este cuál era, es decir, puede

## 94:32 - 94:39
ser que este no, bueno, no es este, no es este, además, no es este porque este no tiene

## 94:39 - 94:44
el stop entry aún, esta es una versión antigua, pero de todas maneras es una versión, el

## 94:44 - 94:47
sistema ha quedado muy bien, pero aquí tú al final has elegido un periodo determinado,

## 94:47 - 94:51
o sea, tú marcas unas cosas, o sea, el hecho de que te ve la prueba negativa no necesariamente

## 94:51 - 94:54
quiere decir que no es el sistema, a lo mejor tú no has elegido bien el fitness, no has

## 94:54 - 94:57
elegido bien la muestra, bueno, hay que trabajar más, a lo mejor necesitas una muestra mayor,

## 94:58 - 95:05
una muestra más pequeña, depende, vale, depende, este sistema lo pasó claramente,

## 95:05 - 95:11
o sea, Artemisa, Artemisa, ¿cuál ha abierto ahora? No, pero otra vez, es que no los tengo

## 95:11 - 95:19
todos aquí, aquí hay muy pocos, aquí hay muy pocos, no, mira, hay uno de Apolo, este

## 95:20 - 95:29
no es el que ha abierto, no, pero es la misma familia, ah, no, no, este es el B, no, no,

## 95:29 - 95:35
esta es una prueba que hicimos, que quedó descartada, esta es una prueba que hicimos,

## 95:35 - 95:40
esta es una prueba que hicimos de fijar el stop como en el IBS entraría y no, en el

## 95:40 - 95:46
SP no iba, en el SP no iban a haber peor resultados y no lo aplicamos, está operando

## 95:46 - 95:53
la 03, está operando la 03 no a 03B, vale, entonces, bueno, pero es igual, un ejemplo

## 95:53 - 95:59
a título de que puede pasarla o puede no pasarla la prueba, vale, al final es una herramienta

## 95:59 - 96:05
más de estrés que además te permite fijar los, fijar los parámetros en aquellos casos

## 96:05 - 96:16
que te permitan, vale, seguimos, seguimos, bueno, ¿alguna pregunta sobre, sobre el World

## 96:16 - 96:25
Forward Optimizer? Cualquier, no, no, o sea, el programa lo que hace es desear datos, es

## 96:25 - 96:31
un sistema, en forex también, puedes poner sistemas en forex, yo tenemos uno trabajando,

## 96:31 - 96:35
el único tema aquí que tenéis que vigilar es lo que os digo, o sea, esto os he hecho

## 96:35 - 96:38
una resumen importante, la ayuda de World Forward Optimizer también es muy potente,

## 96:38 - 96:44
también está en inglés, pero es muy potente, realmente hay temas a vigilar, lo que decía

## 96:44 - 96:50
el número de 3, o sea, tienen que haber una cierta consistencia, lo que pasa que es verdad

## 96:50 - 96:55
que normalmente si no haces bien el proceso no te lo va a pasar porque es muy difícil

## 96:55 - 96:59
que casualmente pase tantos sets distintos, vale, al final, al final la ventaja de esta

## 96:59 - 97:05
prueba es que lo hacen muchas distintas, entonces puede que luego uno lo pase de chiripa,

## 97:05 - 97:10
pero que pase muchos de chiripa no es fácil, entonces normalmente si no haces el proceso

## 97:10 - 97:14
bien te va del fail, pero lo que te quiero decir es eso, que no siempre que te da fail

## 97:14 - 97:21
quiere decir que no valga el sistema, no llegamos directamente a esa conclusión, que no la

## 97:21 - 97:26
ha pasado la prueba, pero bueno, hay que trabajar más, porque el sistema para operar no es

## 97:26 - 97:32
solo el código, yo sabéis hoy, de hecho, creo que es mi especialidad el backtest, porque

## 97:32 - 97:35
el Roberto se ha especializado más en la programación, yo de siempre incluso cuando

## 97:35 - 97:39
gestiono la Seca Build Club, aquellos que me conozcas, me habéis visto que yo siempre

## 97:39 - 97:42
lo he dicho, a mi la programación no es una de mis especialidades, mi especialidad siempre

## 97:42 - 97:48
ha sido el backtest, al final un sistema para operar es todo, es el código y su backtest,

## 97:48 - 97:54
entonces, o sea, sus parámetros para operar, entonces puede ser que el proceso que hayas

## 97:54 - 97:59
hecho de optimización, la muestra que has elegido, los rangos que has elegido, el tipo

## 97:59 - 98:04
de algoritmo, alguna cosa de la optimización no haya sido el adecuado y necesitas cambiar

## 98:04 - 98:09
algo para que pase esa prueba, pero claro, la tiene que pasar cumpliendo con número

## 98:09 - 98:15
de tres, cumpliendo todo, hay veces que no la pasa, como decía Roberto, que no vale

## 98:15 - 98:34
el sistema. Pues es una buena pregunta, no, creo que no, no, no, no, para nada, lo que

## 98:36 - 98:44
tú tienes que, en 3 Session tienes que tener el tiempo real para operar, nada más, ningún

## 98:44 - 98:53
problema, los datos los cargas igual, los cargas con delay, los datos los cargas, el

## 98:53 - 99:01
histórico lo tienes, o sea, para hacer backtest, sí, sí, sí, en Texas, pero tendrás el anterior

## 99:02 - 99:07
ayer, hoy, claro, no, no, igual, a ver, me preguntan por cómo se puede tener esta herramienta

## 99:07 - 99:13
en 3 Session, sí, sí, o sea, tú para tener la plataforma de 3 Session tienes que cumplir

## 99:13 - 99:20
los requisitos que te exige para operar, para que no te cobre por ella, si no, 10 futuros

## 99:20 - 99:24
al mes, por ejemplo, vale, si tú operas 10 futuros al mes, toda la plataforma es gratis,

## 99:24 - 99:29
punto, y luego para operar tienes que tener tiempo real, pero si tú, para hacer backtest

## 99:29 - 99:36
no, para hacer backtest no tienes que tener tiempo real, o sea, tú puedes hacer un backtest,

## 99:36 - 99:42
tú puedes tener un backtest de futuro BLSP y no tener el mercado BLSP pagado, lo que

## 99:42 - 100:10
no podrás superar luego, el tiempo real, ahora, nada más, ahora al final te enseño

## 100:10 - 100:16
los temas, nada más, lo que hemos comentado, bueno, aquí cuatro cositas, os lo dejo muy

## 100:16 - 100:24
breve y os lo leéis, a ver algo que... todas cosas, en tu ordenador, 3 Session en tu ordenador,

## 100:24 - 100:35
pero nosotros lo ponemos en un servidor, aunque puede ser, ahí hay alguna cosa, se está trabajando

## 100:40 - 100:48
en algo de eso, puede ser que con el tiempo pueda, pero no, no es algo inminente, ¿quién?

## 100:48 - 100:55
ah, no, no, en nuestro caso no, lo tienes tú en tu ordenador o en tu servidor, en sociedad

## 100:55 - 101:00
de que tenemos carteras operando en un servidor que hemos encontrado en Canadá que va muy

## 101:00 - 101:06
bien un ratito y está ahí operando, ya conectamos con el móvil, con el tablet, con el portátil,

## 101:06 - 101:14
con el fijo, con la nevera, con el lavaje, casi ya conectas con todo, tiene scripts,

## 101:15 - 101:24
reinicia, sola, está todo lo más automatizado posible, todo, todo, tiene alertas, eso ya

## 101:24 - 101:35
lo tiene 3 Session, aparte tenemos scripts propios para controlar, es un host normal,

## 101:36 - 101:40
hay empresas de este tipo, pero nosotros como tenemos un programador muy buen profesional

## 101:40 - 101:47
no nos hace falta, sí, sí, pero claro, nosotros pagamos, me parece que pagamos 10 o 15 dólares

## 101:51 - 101:58
por eso y si tú cuantas das, verás que pagas pues 50, 100 dólares por empresas especializadas

## 101:58 - 102:03
en eso, que bueno, está muy bien, es un servicio de esto, pues nosotros pues lo damos, porque

## 102:03 - 102:10
ya pues Roberto lo sabe hacer, él se encarga de eso, pero eso ahora va solo, eso solo se

## 102:10 - 102:16
entra si hay un problema, que no hay problemas y además 3 Session de verdad, una vez, 3

## 102:16 - 102:20
Session solo en algún problema se ha tenido con el net, pero en ordenadores que tú instalas

## 102:20 - 102:25
3 Session de cero para operar, es increíblemente estable, o sea es un software increíblemente

## 102:25 - 102:44
estable, no se cuelga nunca el tiempo de un cliente solo, si el suyo opera solo, bueno

## 102:44 - 102:49
eso es una cuenta, nosotros al final somos un supervisor técnico, eso es una cuenta

## 102:49 - 102:57
que entra a Live, o sea tú cuando entras ahí, luego si puedo dentro de un momento,

## 102:57 - 103:01
no, no, no, no, estamos además en directo, no sé si al entrar enseñar algún dato privado

## 103:01 - 103:09
y estamos transmitiéndonos en directo, entonces tampoco es plan que la policía, si podemos

## 103:09 - 103:18
evitar que venga la policía a buscarlos, pues casi mejor, si puede ser a todos los

## 103:18 - 103:25
señores policías que nos escuchan, tranquilos, tranquilos que no pasa nada, está todo correcto,

## 103:25 - 103:33
David por favor, esto luego lo cortas, gracias, bueno, vamos rápido por favor, lo que os

## 103:33 - 103:40
decía aquí, bueno, esto ya, ah, esto es que creo que es muy interesante, existen, nosotros

## 103:40 - 103:48
todavía no lo hemos hecho, pero existen, existen, me consta que hay algún desarrollador

## 103:48 - 103:54
americano bastante conocido que lo está haciendo, aquellos que hayáis oído hablar

## 103:54 - 103:59
de los Self-Adaptative, son sistemas que hay varias maneras, hay algunos que entrarían,

## 103:59 - 104:02
hay muchas maneras, pero la idea es el sistema que automáticamente cambie de parámetros,

## 104:02 - 104:08
pues oí un webinar bastante, bastante que me gustó mucho la idea, era un sistema que

## 104:08 - 104:14
acá entraría, creo que iban velas de un minuto en el SP y usaban, habían hecho un

## 104:14 - 104:21
World Forward y salían, imagínate, estos diez combinaciones de parámetros, cogían

## 104:21 - 104:25
estas diez combinaciones de parámetros que solo iban haciendo periódicamente, que habían

## 104:25 - 104:31
ido bien en un periodo X, que fuera, porque hablamos un minuto, y luego ellos probaban

## 104:31 - 104:36
desde el premarket hasta media hora de iniciar el mercado que parámetros se habían ido

## 104:36 - 104:43
mejor en ese rato y aplicaban el resto de jornada esos parámetros, automáticamente

## 104:43 - 104:50
en el código, sí, sí, por código, un Self-Adaptative, o sea, él lo elegía y a media jornada tenía

## 104:50 - 104:55
una revisión del tema, a media jornada si había habido un de estos pues podía haber,

## 104:55 - 105:02
pero usaba el, sí, pero usando, no, pero la clave, la clave tiene, a mí eso a priori

## 105:02 - 105:06
si me lo explicas o me gusta, pero así me gusta por una, o sea, ¿dónde me gusta?

## 105:06 - 105:11
porque te lo está haciendo en datos que han pasado en World Forward, o sea, todos esos

## 105:11 - 105:19
sets han ido bien en un momento, me explico o no, entonces él ya te está hablando primero

## 105:19 - 105:24
de un sistema que ha pasado, que ha pasado que es robusto, que ha demostrado que se

## 105:24 - 105:33
ha adaptado en distintos periodos y él elige esos para, o sea, él ha estudiado que viendo

## 105:33 - 105:40
qué tiempo que hemos dicho, más o menos, si un set va bien en ese periodo, pues digamos

## 105:40 - 105:44
tiene capacidad predictiva sobre el resto de jornada, lo ha probado con el World Forward

## 105:44 - 105:49
Optimizer, lo ha salido y por lo tanto tiene datos objetivos para verificarlo, porque esta

## 105:49 - 105:54
prueba es lo que te digo, te permite eso, entonces utiliza esos sets y en tiempo real

## 105:54 - 105:58
va haciendo eso, va probándolo por código implementado y lo va revisando, o sea, cada

## 105:58 - 106:04
continuamente, lo dijo pero no me acuerdo cada cuánto, dijo que continuamente iba reaciendo

## 106:04 - 106:09
el World Forward Optimizer, no sé, cada semana, se llama muy de corto plazo, o sea, cada semana

## 106:09 - 106:13
iba haciendo esto y va aplicando, probando y recuerdo que dijo sets que entraban y salían,

## 106:13 - 106:18
¿no? Habían sets que entraban y salían cada semana de la parrilla de sets, que aquí

## 106:18 - 106:25
digo 10, pero que a lo mejor eran 25, eran más de 10, eran muchos, no me acuerdo, no

## 106:25 - 106:30
quisiera engañarnos, pero eran muchos, eran muchos, a lo mejor eran 25 sets o 20 o los

## 106:30 - 106:36
que fuera, ¿no? Bueno, es una aproximación interesante, es una aproximación interesante,

## 106:36 - 106:43
no me dejo caer ahí porque ahí está, ¿vale? Porfolio, porfolio, ¿vale? Super breve total,

## 106:43 - 106:49
¿vale? Luego intentaremos algún día hablar más de porfolio y porfolio maestro, ¿vale?

## 106:49 - 106:54
Esto que hemos hablado es de World Forward Optimizer, ¿vale? Antes me han preguntado

## 106:54 - 106:59
si se puede mezclar sistemas, sí, no solo se puede, sino que se debe, se debe mezclar

## 106:59 - 107:02
los sistemas, ¿vale? TreSystem tenía otra herramienta de backtest, también en mi opinión

## 107:02 - 107:10
fantástica que se llama porfolio maestro, porfolio maestro es un simulador de carteras

## 107:10 - 107:15
que ahora mismo se abre desde fuera de la plataforma, pero en la 9.5 ya lo han integrado

## 107:15 - 107:18
como una aplicación dentro, es lo mismo que decíamos antes, poco a poco pues va entrando,

## 107:18 - 107:23
¿no? Pero ahora mismo se abre fuera, o sea, hay que hacer login en TreSystem igual, ¿eh?

## 107:23 - 107:27
O sea, no es que se abra, si no tienes usuario no puedes, pero el icono, digamos, está en

## 107:27 - 107:33
el escritorio, hay que abrirlo como una aplicación por separado, ¿vale? Entonces, al final como

## 107:33 - 107:38
os decía, pues tener un porfolio de sistemas es muy recomendable aunque uno tenga un sistema

## 107:38 - 107:43
muy bueno, ¿vale? Porque el sistema muy bueno mañana puede dejar de serlo y eso lamentablemente

## 107:43 - 107:52
no podemos saberlo, podemos intentar minimizar el riesgo, podemos hacer World Forward y está

## 107:52 - 107:56
muy seguros de que es muy sólido, pero el mercado puede cambiar radicalmente, puede

## 107:56 - 108:01
pasar algo que realmente está totalmente imprevisto, algo que nunca había pasado en

## 108:01 - 108:05
el histórico, lo que sea, y se va a dejar de funcionar. Entonces, pues es aquello de

## 108:05 - 108:10
no poner todos los gobos en el mismo cesto, ¿no? Y es una realidad, ¿no? Entonces aquí

## 108:10 - 108:15
pues una de las típicas ventajas, ¿no? Sobre todo mejora el riesgo porque los profit, si

## 108:15 - 108:21
tú sumas un sistema que gana mil y otro que gana mil, ganan dos mil, ¿vale? Bien. Pero

## 108:21 - 108:25
si el primero tiene un drawdown de 500 y el segundo tiene un drawdown de 500, el drawdown

## 108:25 - 108:31
seguramente no va a ser mil. Puede ser incluso que sea 500, eso sería ya el sumo de la perfección

## 108:31 - 108:38
de la descorrelación, pero probablemente pues será 700, será, por decir algo, lo que

## 108:38 - 108:41
sea, ¿no? Es decir, será un drawdown que no será la suma de los dos, por lo tanto

## 108:41 - 108:46
ya es obvio que el ratio de la rentabilidad se suma y el del riesgo no, ¿vale? Por lo

## 108:46 - 108:51
tanto la mejora de la rentabilidad de riesgo es bastante clara, sobre todo de la parte

## 108:51 - 108:57
del riesgo, ¿vale? Y en esa misma línea pues actualizas mucho la equity, ¿no? A veces

## 108:57 - 109:02
incluso puedes perder rendimiento porque pues perder rendimiento quiere decir que si tú

## 109:02 - 109:06
pones solo todo en el sistema del oro que está yendo como un tiro, no, mejor, en teoría

## 109:06 - 109:11
ganaría más, pero también cuando venga el drawdown seguramente perderé más y poniendo

## 109:11 - 109:14
más sistemas puedo suavizar la curva, que también es recomendable, pero sobre todo

## 109:14 - 109:25
para el corazón, ¿vale? Y luego pues aquello de que digo yo, que siempre hay que pensar,

## 109:25 - 109:29
que siempre me habéis ido a hablar, siempre hay que pensar en el riesgo, siempre, cuando

## 109:29 - 109:35
uno opera en el mercado y tendemos la costumbre de pensar demasiado en la rentabilidad. La

## 109:35 - 109:39
rentabilidad está bien, es lo que buscamos, pero tiene que llegar de la mano de controlar

## 109:39 - 109:46
primero el riesgo, ¿vale? Porque si operamos un sistema, si nosotros sacamos ahora este

## 109:46 - 109:50
sistema y creemos mucho en el nemesis, ¿no? Pues a lo mejor venimos aquí seis meses y

## 109:51 - 109:58
nos equivocamos, nos equivocamos con este sistema y no vale. Puede pasar, esto puede

## 109:58 - 110:03
pasar y esto tenemos que tener claro que puede pasar. Por más pruebas que hayamos hecho,

## 110:03 - 110:09
por más robusto que sea, por más lucecitas verdes del PAS, por más, todo lo que queráis

## 110:09 - 110:13
puede pasar. ¿Es más difícil? De acuerdo, es más difícil. Si está todo rojo es más

## 110:13 - 110:20
fácil, vale, estamos de acuerdo, pero puede pasar. Entonces como eso puede pasar hay que

## 110:20 - 110:28
diversificarse, hay que diversificarse. Y aquí he puesto un ejemplo de esto. Esto

## 110:28 - 110:32
es de hace bastantes años, aquello, no sé si conocéis mi trayectoria o no, bueno, aquellos

## 110:32 - 110:38
que no lo sepan, yo presidí un club del 2005 al 2007 que es esto. Estos son datos reales

## 110:38 - 110:43
porque esas curvas son tan poco lineales, porque son de operativa real, las curvas operativas

## 110:43 - 110:50
reales no siempre son tan rectas, ¿no? Esto, no sé si se ve muy bien, si piensa esta leñita

## 110:50 - 110:59
de abajo, esto es un sistema que no ganó, no ganó nunca. Bueno, pues aún así el club

## 110:59 - 111:06
ganó un 85% al final, la cartera, ¿no? Y dices, hombre, ¿y hubiera ganado más sin

## 111:06 - 111:12
ese? Hombre, en valor absoluto sí, pero lo curioso del tema es, y esto aquí no los tengo,

## 111:12 - 111:18
pero los ratios comparativos con los sectoriales se demostraba, o sea realmente ese sistema

## 111:18 - 111:23
se revisó hasta la saciedad, o sea, actualmente ya estaba en el taller, pero siempre aportaba

## 111:23 - 111:28
valor, al final era un sistema que aportaba valor, ¿por qué? Porque estaba muy descorrelacionado

## 111:28 - 111:33
con los otros y realmente iba bien cuando los otros iban bastante mal, entonces llegaba

## 111:33 - 111:37
aportar valor a la cartera, llegaba aportar valor a la cartera, entonces fue un sistema

## 111:37 - 111:42
que siempre se mantuvo porque tenía sentido, a pesar de que no lo parezca en valor absoluto

## 111:42 - 111:49
tenía sentido. ¿Por qué tiene sentido? Porque el mejorar la, porque reducías el

## 111:49 - 111:58
drawdown, reducías el riesgo, mejorar el drawdown tiene varias ventajas, esta es la resumen

## 111:58 - 112:09
de esa que habéis visto, es esta. Tiene varias ventajas, la obvia es que, bueno, pues esto

## 112:09 - 112:15
de que no tienes, que tienes el riesgo más diluido, que no tienes todos los huevos en

## 112:15 - 112:19
el mismo cesto, esta es la obvia, pero hay una segunda más indirecta que es a través

## 112:19 - 112:23
del money management, ¿vale? Reducir el riesgo de cualquier estrategia global, de cualquier

## 112:23 - 112:29
portfolio en general, luego hay que verlo, nos permite ser un poco más agresivos con

## 112:29 - 112:34
la gestión monetaria, ¿vale? O dicho de otra manera, nos permite destinar más parte de

## 112:34 - 112:43
capital a operar y, por lo tanto, desde ese punto de vista, en un caso ideal, puede darse

## 112:43 - 112:48
el caso que un sistema que esté perdiendo dinero, reduzca el drawdown tanto de la cartera,

## 112:48 - 112:55
que la cartera gane más con ese sistema porque puede destinar más capital a operar, no se

## 112:55 - 113:04
me ha explicado. Pues bien, porque yo casi no me he entendido, os lo agradezco. Entonces,

## 113:12 - 113:20
MSA es una muy buena aplicación que también tengo, pero no, no, ni se acerca. No, pero

## 113:20 - 113:28
MSA es muy buena, es muy barata, además, la tenemos, pero porfolio maestro es otra

## 113:28 - 113:33
cosa, porfolio maestro es un monstruo, o sea, ahora vamos a intentar en 5 minutos verlo.

## 113:33 - 113:39
Esto es una imagen de porfolio maestro, a ver, muy breve en porfolio maestro, ¿vale?

## 113:39 - 113:45
Porfolio maestro tú puedes mezclar, primero, tú puedes mezclar distintos sistemas, o sea,

## 113:45 - 113:50
tú mezcas distintos grupos de estrategia y cada grupo de estrategia puede ser una combinación

## 113:50 - 113:57
de una cesta de activos con un sistema con varios, ¿vale? En este caso es solo, por

## 113:57 - 114:04
ejemplo, este, este es este que habéis visto, ¿vale? Némesis, ¿vale? Este es Némesis,

## 114:04 - 114:11
con que símbolo? Con el oro, está ahí. Hay otros, pero tú puedes tener una cesta con

## 114:11 - 114:17
este que va en 4 pares del forex, este mismo va en los 4 pares, por lo tanto tú puedes

## 114:17 - 114:22
mezclar en una cartera infinitas combinaciones de sistemas que pueden estar en distintos

## 114:22 - 114:29
activos, en distintas cestas, son mismas cestas, en distintos time frames, es decir, entre

## 114:29 - 114:33
días, con diarios, con semanales, con lo que te dé la gana, ¿vale? Y por supuesto

## 114:33 - 114:41
en distintos activos, ¿vale? En distintas divisas también. ¿El sistema? Ah, sí, sí,

## 114:41 - 114:46
sí, no claro, ahí la cuenta. No, bueno, esta, esta cartera tiene el riesgo forzado,

## 114:46 - 114:54
pero esta cartera ha salido a operar con 70.000 dólares. La verdad, para mi gusto yo la hubiera

## 114:54 - 115:03
perfilido con 100, esta misma, ¿eh? No, tiene ratios de riesgo asumibles, un poco, un poco,

## 115:04 - 115:10
de verdad, son asumibles, ahora, ahora, no me corres tanto, ahora te lo enseño. A ver,

## 115:10 - 115:16
entonces, bueno, esto al final tiene un backtest, pero ¿qué tiene de particular como muy bien

## 115:16 - 115:20
comentaba aquí Roberto? A ver, cualquier sistema tú, aquí os he dicho el resumen,

## 115:20 - 115:26
tú fijas los parámetros, ¿vale? Fijas el intervalado de ese sistema, los parámetros

## 115:26 - 115:29
que tenga ese sistema, pero tú puedes hacer varias cosas más. Una, aplicar un money management

## 115:29 - 115:33
para cada sistema, que ya puede estar definido en el código como es el caso, aquí hay unas

## 115:33 - 115:38
variables de money management, pero el portfolio tiene implementados varios, de tal manera

## 115:38 - 115:44
que puedes probar de uno a otro rápidamente. Bueno, aquí están todos, o sea, fíjate que

## 115:44 - 115:51
hay fixed fractional, fixed risk, fixed normal, los típicos, pero sobre margen, sobre ATR,

## 115:51 - 115:55
sobre market value, sobre precio, bueno, hay un montón, no vas a profundizar en eso porque

## 115:55 - 116:00
solo con eso te has hecho un webinar de dos horas, solo hablando del money, sí, sí,

## 116:00 - 116:05
quiero decir que imagina que vamos a intentar hacer un vistacito al portfolio de esto para

## 116:05 - 116:10
que veáis la capacidad, luego ya detaremos más adelante a hablar de él, que veáis

## 116:10 - 116:15
su potencia, sencillamente, ¿vale? Luego tú de cada sistema puedes declarar el money

## 116:15 - 116:19
management a cada sistema, ¿vale? Otra variable que nosotros, por ejemplo, todavía no hemos

## 116:19 - 116:23
usado pero que también es bastante interesante es que si tú, imagina que aplicas un sistema

## 116:23 - 116:28
sobre una cartera de 500 acciones, puedes hacerlo, con esa que le haces te le pones acciones

## 116:28 - 116:33
todas. Entonces, el portfolio de esto tiene un sistema de ranking que no deja de ser

## 116:33 - 116:41
otro sistema, un subsistema de selección de valores dentro de una gran cesta, ¿vale?

## 116:41 - 116:48
De ranking, es decir, tú le dices yo quiero que opere solo en los 10 o en el percentil,

## 116:49 - 116:56
en el primer percentil, en el 10% mejores o peores que tiene un determinado dato, RSI

## 116:56 - 117:03
alto, RSI bajo, media de periodos en tal y importado por Excel.

## 117:04 - 117:09
O sea, un criterio que te importe si crees, ¿vale? O sea, criterios de ordenación.

## 117:09 - 117:13
Nosotros, por ejemplo, no hemos usado todavía esto, pero son criterios de ordenación de

## 117:13 - 117:20
valores dentro de la cesta. O sea, tú tienes una cesta, una symbol list y tú quieres que

## 117:20 - 117:24
él utilice, que no quieres le pones no y todos los utiliza todos. Si yo quiero filtraría

## 117:24 - 117:28
otro que quiere decir que no necesariamente, en este caso sí porque solo hay uno, utilizaría

## 117:28 - 117:34
todos los símbolos de la cesta, sino que utilizaría los que cumplieran esos criterios.

## 117:34 - 117:40
Es un sistema de selección, correcto. Sí, es un subsistema de selección de parámetros,

## 117:40 - 117:50
sí, sí. Es un sistema de subselección de símbolos. Sí, sí, sí. No, no, no lo aplica.

## 117:50 - 117:54
Sí, sí, sí, lo puedes, sí, sí, por supuesto, sí, sí, sí. ¿Vale? Entonces, esto no es

## 117:54 - 117:59
sistema, pero luego a cada uno de ellos lo puedes hacer. Luego, además, ahí donde tiene

## 117:59 - 118:06
herramientas muy poderias, esto está muy puesto por los CTAs, ¿vale? Tiene un montón de criterios

## 118:06 - 118:12
de constrictions, ¿vale? Constraints, perdón, restricciones operativas. O sea, tú puedes

## 118:12 - 118:19
fijar, esto yo lo llamo money management a nivel de portfolio, ¿vale? ¿Cómo? Para

## 118:19 - 118:25
money management, sí, para cualquiera que tenga alguna restricción impuesta por la

## 118:25 - 118:30
equity, ¿no? O sea, tú tienes el money management del sistema, pero luego puedes, además, ponerle

## 118:30 - 118:36
reglas, restricciones al portfolio en general. Es decir, el portfolio no puede tener como

## 118:36 - 118:43
mucho 10 posiciones abiertas, 5, 2, bueno. El portfolio como mucho puede ir largo tanto,

## 118:43 - 118:49
se puede apalancar tanto, se puede tal, bueno, distintas, tú las fijas. Porfolio stops,

## 118:49 - 118:52
esto por ejemplo, el otro día, no digo el nombre, había un CTA que me confesó que

## 118:52 - 118:58
lo hacía. Y es discrecional, ¿eh? O sea, que no lo hace por maestro, pero usa exactamente

## 118:58 - 119:04
la misma regla, la que hemos hablado antes. La misma regla, si el portfolio le pierde

## 119:04 - 119:12
más de un 2%, para una semana. No, creo que un mes, no sé si es 100% en el periodo,

## 119:16 - 119:24
pero aquí tú lo puedes elegir, tú puedes poner, no, el portfolio, entero, entero. Esto

## 119:27 - 119:32
de nuevo es aplicable o no, es una opción. Es una opción que tú dices, porfolio stop

## 119:32 - 119:42
2, pues si el portfolio pierde un 2, un 3, un 5, un 10. No, en estas reglas, bueno, una

## 119:42 - 119:48
perdida es un drawdown, ¿no? Es eso, un drawdown. Si llegas a un determinado drawdown, paras,

## 119:48 - 119:58
es eso, pero en porcentaje. Paras qué? Un mes, una semana, un día, lo que tú le digas,

## 120:01 - 120:06
pasa a ese periodo, en la simulación de acá te arrancas. Tú puedes simular eso, a ver

## 120:06 - 120:11
qué pasaría. Puedes elegir la divisa del portfolio, porque pueden haber distintos,

## 120:11 - 120:15
en el global pueden haber cientos de divisas, pero al final dices, bueno, la cuenta en qué

## 120:15 - 120:22
va a estar, originalmente. En dólares, en euros, en peso mexicano, no sé, no sé, no,

## 120:25 - 120:31
creo que no está, todavía. Bueno, dale tiempo. Bueno, entonces, aquí llegas al backtest,

## 120:31 - 120:35
tú preparas todo esto, que hemos ido muy rápido, y llegas a la opción del backtest,

## 120:35 - 120:41
porque también, por supuesto, hay opciones. Por supuesto, comisiones y demás, y cualquier,

## 120:41 - 120:45
o sea, hay una simulación estándar que, sencillamente, con los parámetros que yo

## 120:45 - 120:49
le he fijado, pero luego lo puedo optimizar. Puedo utilizar alguna variable, la que yo

## 120:49 - 120:56
quiera, ¿vale? Cualquiera que esté aquí del sistema, o cualquiera constrain, o cualquiera

## 120:56 - 121:01
esto, o sea, cualquier variable que hemos definido previamente, incluso las de restricción,

## 121:01 - 121:05
la restricción del portfolio, o la de la pérdida del drawdown del portfolio, si quiero también

## 121:05 - 121:10
la puedo optimizar. ¿Qué pruebe? Pues en vez de un 2, probate un 2 y un 4. A ver, ¿dónde

## 121:10 - 121:15
sería mejor parar el portfolio? Bueno, tal vez una manera de ver el portfolio, si a veces

## 121:15 - 121:20
sale a cuenta, es una manera de ver si nos sirve, sale a cuenta aplicar reglas de equity

## 121:20 - 121:24
o no, ¿no? Si antes que aplique reglas de equity, pues mirar si te sale a cuenta o no

## 121:24 - 121:29
en ese portfolio, aplicarlo, sencillamente. Aquí al final lo optimizas, le das, no entro,

## 121:29 - 121:34
ya digo, puedes optimizar, puedes hacer también golf course aquí, pero el clásico, el golf

## 121:34 - 121:39
course, es decir, dejar una parte fuera, ¿no? Pero es igual, no entramos porque, ¿vale?

## 121:39 - 121:44
Y tú al final llegas, que esto al final es muy potente, pero realmente el objetivo es

## 121:44 - 121:50
este, el objetivo es llegar a esto, ¿vale? El objetivo es al final obtener un informe,

## 121:50 - 122:06
obtener un informe de una cartera, déjame mirar lo que he hecho, adiós. No, hombre,

## 122:07 - 122:19
ahora no. No se cuelga, no, hombre, no se cuelga lo que pasa que realmente ahora no

## 122:20 - 122:25
está, o sea, está el hangout abierto, retransmitido online en directo, está haciendo muchas

## 122:25 - 122:32
cosas el pobre, es decir, está haciendo muchas cosas. O sea, claro, cuando estás operando,

## 122:32 - 122:35
eso sí que lo recomienda, mejor tener un ordenador que está quietito, que tenga menos

## 122:35 - 122:43
software instalado, es decir, claro, contra más cosas tenga más problemas, los ordenadores,

## 122:43 - 122:47
pero es como no, cuando lo compras nuevo va como un tiro, cuando llevas un año trabajando

## 122:47 - 122:50
ya todos los ordenadores empiezan a ganar, pues lo mismo, pues es igual, lo mejor es

## 122:50 - 122:55
si tú vas a operar con ese quietito ahí, lo formateas, le pones decisiones, no haces

## 122:55 - 123:02
nada más, y eso va de lujo al principio, de todas maneras no se ha colgado, hemos tenido

## 123:03 - 123:08
suerte. A ver, aquí tienes un sumario, tú has simulado esta cartera, esta cartera es

## 123:08 - 123:12
esta cartera que hemos dicho, que entre ella está el oro, son 10 años, pues ha ganado

## 123:12 - 123:15
450.000, aquí hay un resumen, por ejemplo, me preguntabas ¿qué drawdown ha tenido esta

## 123:15 - 123:23
cartera? 28.000 dólares, esa cartera ha tenido un drawdown de 28.000 dólares, que es un

## 123:24 - 123:30
13% o un 40% sobre el capital inicial, son 70.000 dólares, se lo habrá tenido en principio,

## 123:30 - 123:36
pero en el momento que lo ha tenido, no, un drawdown de 40, en el momento que lo ha tenido

## 123:36 - 123:41
sobre el capital inicial, pero bueno, pues como no tiene monedas, te lo compro, puedes

## 123:41 - 123:48
estimarlo, puedes estimarlo que desgo. Estos datos son, no son todos fuera de monstruo,

## 123:49 - 123:52
pero casi todos, ¿por qué? Porque primero, el sistema del oro está aplicado con unos

## 123:52 - 123:59
parámetros concretos, con los que le tocan ahora, con estos que habéis visto que hemos

## 123:59 - 124:05
elegido para el futuro, pero claro, en todo el histórico anterior, es una manera de penalizarlo

## 124:05 - 124:11
porque realmente no son los que hubiera elegido, con lo cual el oro es todo fuera de monstruo,

## 124:11 - 124:16
porque esos parámetros son los que ha elegido ahora para operar, bueno, el único optimizado

## 124:16 - 124:20
es el que ha optimizado el último set, todo el resto de los 10 años, además son 10,

## 124:20 - 124:26
fíjate que en el oro hemos visto 2007, el oro que es el que más gana es todo fuera

## 124:26 - 124:30
de monstruo, fíjate porque aquí insisto, te vienes en 2010 y tienes todo el oro fuera

## 124:30 - 124:36
de monstruo y el oro es este, bueno, sí que tiene un periodo aquí que pierde, pero bueno,

## 124:36 - 124:45
recupera rápido, fíjate 2005, es este que ves ahora marcado, te quedas ahí quieto,

## 124:45 - 124:50
eso, eso es el oro, ves que incluso, hemos dicho que lo hemos empezado a optimizar en

## 124:50 - 124:58
2007, ¿no? Es aquí, ¿eh? Está en positivo, está en positivo, pero ojo, lo hemos empezado

## 124:58 - 125:01
a optimizar, pero los parámetros que ha elegido ahí no eran esos, recordaros que

## 125:01 - 125:05
han cambiado claramente, esos parámetros se han elegido por aquí, con lo cual es todo

## 125:05 - 125:12
fuera de monstruo el oro, todo fuera de monstruo, Artemisa BLSP es casi la mitad, Apollo es

## 125:12 - 125:16
todo porque es lo mismo, también tiene fijados los parámetros de esta manera, o sea, realmente

## 125:16 - 125:23
hay muchos sistemas, son todo fuera de monstruo, y quiero decir que es un drawdown bastante

## 125:24 - 125:31
realista, barra pesimista, quiero decir, no está optimizado para nada, es un drawdown,

## 125:33 - 125:36
bueno, luego aquí puedes ver lo que han hecho por supuesto todos los sistemas, ha puesto

## 125:36 - 125:40
tener un montón de información de la cartera en global, del portfolio y de todo cada uno

## 125:40 - 125:46
de ellos, ¿no? La lista de los trades de todos, bueno, un montón, ¿no? Y distintos ratios,

## 125:46 - 125:55
bueno, ya digo que hay toda la curva a la cuenta, beneficios periódicos por años, por

## 125:56 - 126:07
ejemplo. No, en este no, en esta versión ya con los tres sets no, no pierdo ninguno,

## 126:07 - 126:11
y luego aquí a nivel de gráficos, pues muy importante, ¿no? Tenés datos aquí, se

## 126:11 - 126:17
ve un poco porque me ha, al conectarme he perdido mucha pantalla, realmente me falta

## 126:17 - 126:24
un montón, tendría que ser más anchos. ¿Él? Sí, sí, ahora lo enseño, pero aquí

## 126:25 - 126:31
veis la equity realizada, pues bueno, una equity bastante estable, insisto y repito

## 126:31 - 126:38
con mucho fuera de muestra, mucho, mucho fuera de muestra, ¿vale? Es una buena equity, aquí

## 126:38 - 126:43
tenemos un drawdown, lógicamente inicio porque no tiene muy management, lo cual lo tiene,

## 126:43 - 126:49
a medida que aumenta capital, el nivel porcentual, claro, ya es irrelevante. No, ahora aquí

## 126:49 - 126:56
no hay, hay, hay, hay, hay, nosotros en futuros por defecto utilizamos el market, pero bueno,

## 126:56 - 127:00
porque venimos a la gestión y nos obliga el apalancamiento un poco, porque es una manera

## 127:00 - 127:05
de controlar el apalancamiento, es el mixed fractional sobre market value, es decir, un

## 127:05 - 127:12
porcentaje, una fracción como market fractional, pero no sobre el riesgo, sino sobre el nominado

## 127:12 - 127:17
del futuro, que es el valor de mercado del futuro, entonces es una manera de controlar

## 127:17 - 127:24
el apalancamiento, porque si no es difícil en futuros, pues si utilizas gatos de riesgo

## 127:24 - 127:29
se te dispara el apalancamiento y no puedes. Bueno, aquí tienes luego puedes ver la curva

## 127:29 - 127:38
de todos, como veíamos, no se ven, no, ganan todos, este es euro dólar, sí, este es un

## 127:41 - 127:51
poco más, bueno, pero es que se opera muy poco, opera muy poco, opera, opera, opera, bueno,

## 127:52 - 127:57
pues tienes un montón de charts, si tuvieras muchos grupos de estrategia, pues podía ver

## 127:57 - 128:05
ahora cada grupo de estrategia separado, aquí en el gráfico, está costando esto ya, vale,

## 128:06 - 128:12
bueno, luego puedes ver, por ejemplo, esto que decía Roberto, es uno que miramos mucho,

## 128:12 - 128:17
por ejemplo, es rolling a 12 meses, que hubiera ganado a 12 meses en cada punto, este es su

## 128:17 - 128:21
primer momento a 12 meses que ganó muy poco, de hecho aquí en la tabla lo tienes, pero

## 128:21 - 128:29
ahí lo ves, peor periodo a 12 meses ganó todos los dólares, no, eso quiere decir

## 128:29 - 128:36
que entrando en cualquier momento, ese mes entrando a 12 meses antes cuando hubieras ganado,

## 128:37 - 128:51
en cualquier momento, 12 meses después, ¿qué ganarías? Vale, o 24, bueno, no, en 12 meses

## 128:53 - 128:59
ha ganado, ha ganado, bueno, ha habido que casi no, pero bueno, tiene el oro que es mucha

## 128:59 - 129:03
tendencia y además pesa mucho el oro, así entre el money management ahí tiene un peso

## 129:03 - 129:08
importante, luego tenemos ya una prueba aquí con money management, he intentado hacerla

## 129:08 - 129:13
antes para que lo vierais, pero bueno, igual han quedado cosas raras, pero bueno, lo pongo

## 129:13 - 129:17
aquí, aquí varían los contratos, porque el Nasdaq como es el más pequeño, realmente

## 129:17 - 129:23
le ha subido contratos, porque esta, el money management como os decía, por market fractional,

## 129:23 - 129:27
por valor de mercado, como el Nasdaq es el que menos valor de mercado tiene, le ha puesto

## 129:27 - 129:32
más contratos, pero bueno, también teniendo en cuenta la equity, teniendo en cuenta por

## 129:32 - 129:41
supuesto la equity, pasa algo aquí, ah no, ya está, ya está, bueno, aquí hay la z

## 129:41 - 129:48
cuenta location, pues puedes ver, pues aquí es el Nasdaq cuando no cambia el otro, realmente

## 129:48 - 129:58
tiene mucha información y los gráficos son todos configurables, exportables, este es

## 129:58 - 130:06
el con el money management y el que más ha tirado del carro es el Nasdaq, el market value

## 130:06 - 130:11
además tiene la ventaja esta de que permite para comparar, nosotros cuando hacemos backtips

## 130:11 - 130:15
de carteras inicial siempre lo usamos, no es este caso, ¿por qué? porque es una manera

## 130:15 - 130:19
de comparar los futuros, porque si no, ¿cómo comparas el futuro del Nasdaq con el futuro

## 130:19 - 130:25
del oro? Claro, el market value es una manera de compararlo, o sea, ¿cómo eliges qué

## 130:25 - 130:30
contratos tiene uno y otro? Ese es uno el nominal, porque realmente el que tiene mayor

## 130:30 - 130:37
valor pues tiene más riesgo también, lógicamente, entonces si no, claro, realmente el Nasdaq

## 130:37 - 130:42
es insignificante a lo del oro, entonces aquí por eso el Nasdaq como ha ido bien, pues ha

## 130:42 - 130:46
empezado, pero déjate que no se empiece así, empezó porque ha ido más, porque como ha

## 130:46 - 130:51
ido ganando pues ha subido, el Nasdaq no estaba el primero, pero ha cogido una buena racha

## 130:51 - 130:54
y como ha ido subiendo la cuenta pues ha ido aumentando el contrato, así que ese es lo

## 130:54 - 131:05
que tiene el money management para eso está, ¿no? No, perfecto, lo aplica, lo lee el código

## 131:05 - 131:12
igual, es el lenguaje lo lee y lo aplica, sí, sí, no hay problema, o sea, tú le pones

## 131:12 - 131:16
no que no aplique ninguno, no, este hecho es así, o sea, este no está aplicado con

## 131:16 - 131:23
el de portfolio maestro, está aplicado en código, sí, sí, cada uno, cada sistema lo aplica

## 131:23 - 131:37
él, tú lo puedes, no, no, creo, la verdad que no creo haberlo probado, no, pero tú

## 131:42 - 131:49
le pones no, lo bueno que tienes es que si tú lo aplicas por él aquí en la columna

## 131:49 - 131:57
te sale, te sale el rato, incluso puedes ver en la tabla de trades te sale la fórmula,

## 131:57 - 132:00
buenísimo, si tú lo aplicas de portfolio maestro tiene una columna última que te sale

## 132:00 - 132:07
el cálculo que ha hecho el money management con la fórmula, no, si viene en el código

## 132:07 - 132:12
no porque es el código, es un easy language, punto, si lo aplica él te viene aquí y te

## 132:12 - 132:22
dice el cálculo que ha hecho, entonces 3x3x4x5, ¿el ratio que él tiene? Sí, sí, es configurable,

## 132:22 - 132:29
o sea, el ratio que él tiene, tú le puedes evitar parámetros luego, todos, sí, todos

## 132:30 - 132:36
y optimizar, si quieres, o sea, cualquier variable es optimizable luego, si quieres,

## 132:36 - 132:47
todas, o sea, tú vas aquí al, sí, es una buena manera, no, pero bueno, pero tú puedes

## 132:49 - 132:52
ser que tengas un ratio que a lo mejor pues es distinto y no lo tiene él, pues lo creas,

## 132:52 - 133:04
lo pones en el código y ya está, o sea, no, pero sí, sí, se puede que cualquier variable

## 133:04 - 133:17
del sistema es optimizable, cualquier variable del sistema es optimizable, a ver, aquí,

## 133:17 - 133:22
estos son las opciones de money management, aquí tienes también parámetros, las de,

## 133:22 - 133:25
las suyas, tú aquí cualquiera de ellas la cambias y cualquiera de estas ahora si yo

## 133:25 - 133:32
la pongo y me voy al portfolio, le voy a backtest, verás que me saldrá, ahora aquí le he elegido

## 133:32 - 133:36
a una, ¿ves? le he elegido a una, voy aquí a money management, ¿ves? me sale la pestaña,

## 133:36 - 133:40
al hacer el backtest portfolio tengo una pestaña que es money management para optimizar esto

## 133:40 - 133:51
si quiero, sí, sí, sí, sí, si quieres sí, pero si estuvieran en el sistema también

## 133:52 - 133:58
podrías porque sería un input de aquí, me explico, aquí son los inputs, esto, money

## 133:58 - 134:02
management vale uno, estos son variables de money management, minimum size, maximum size,

## 134:02 - 134:06
esto yo si quiero optimizado optimizo, o sea, realmente optimizado puedes hacer de las dos

## 134:06 - 134:12
maneras, pero es verdad que a mí también me gusta que lo enseñe maestro, pero bueno,

## 134:13 - 134:16
a lo mejor si tú tienes un rato que lo quieres hacer distinto pues no puedes, pero maestro

## 134:16 - 134:21
tiene que luego te enseña el dato, vale, bueno y tiene algunas cosas más, luego si

## 134:21 - 134:27
haces la optimización salen aquí, aquí puedes ver el trace log, aquí si has hecho, todas

## 134:27 - 134:33
las opciones que has hecho de money management de esto estarían aquí, o sea todas las reglas

## 134:33 - 134:37
que tú has, money management cancelación, o sea trades que no se han podido hacer por

## 134:37 - 134:42
money management, trades que no se han podido hacer por constricción o por ranking, estarían

## 134:42 - 134:48
aquí, podrías ver que trades no se han hecho por las restricciones, o además puedes

## 134:48 - 135:06
hacer correlación, un desmelene, si la correlación entre símbolos ha quedado razonable si, sabes

## 135:06 - 135:24
algo de jesús, a ver vamos a ir abriéndonos y caer porque, dígame perdone, ratio, que

## 135:24 - 135:37
es ratio, ratio de visual, pero que es ratio, pero que es ratio, hay muchos ratios, ratio

## 135:38 - 135:46
visual char, pero eso decía ratio visual char, ratio visual char recovery, Usted trabaja

## 135:46 - 135:55
con visual char, recomiendo que vea el webinar 6, lo vio el webinar 6, vale, bueno esto ves

## 135:55 - 136:03
la matriz de correlaciones, perfecto, se lo agradezco, bueno matriz de correlaciones de

## 136:03 - 136:08
los activos, además puedes hacer algún formular análisis también, aquí ahora bueno, realmente

## 136:08 - 136:12
hay muchos tests una vez hecho al portfolio hacer como veis y no podemos profundizar más

## 136:12 - 136:19
porque es un poco largo, pero es una herramienta realmente muy potente también para mezclar

## 136:20 - 136:25
y para ver que podemos sobre todo esperar de un conjunto de sistemas, un conjunto de

## 136:25 - 136:32
sistemas y cómo pueden mover porque a veces parece una cosa y luego no es tal, es realmente

## 136:33 - 136:41
una herramienta bastante buena. El ratio, bueno, TrayStation tiene TrayStation index,

## 136:42 - 136:48
que es lo que es ratio visual char, pero en el numerador además multiplica los winning

## 136:48 - 136:54
trades, los trades ganadores, es una manera de, es lo mismo rentabilidad riesgo pero al

## 136:54 - 137:01
multiplicarlo por los winning trades digamos que fomentas la tasa de acierto un poco, fomentas,

## 137:02 - 137:06
o sea es rentabilidad riesgo fomentando un poco la tasa de acierto, pero muy parecido,

## 137:06 - 137:11
es lo que le decía, tienen una gran correlación entre ellos, yo lo decía tanto por eso, lo

## 137:11 - 137:17
decía por el inside bar backtesting que Visual no lo tiene, ese es un gran problema, en el

## 137:17 - 137:24
backtesting o sea realmente las barras las simulan y eso, sobre todo hay sistemas que

## 137:24 - 137:32
es crítico, pero es que es otra cosa, es otra cosa, o sea no, luego por ejemplo TrayStation

## 137:32 - 137:39
ajusta el futuro, ajusta el futuro, Visual no ajusta el futuro, la persona que viene

## 137:39 - 137:42
que yo, yo pegué muchos años con Visual, estuve años y años pidiéndoles y llegué

## 137:42 - 137:46
con ellos hasta hablar un histórico del CAC, trabajarlo con ellos porque lo iban a hacer,

## 137:46 - 137:50
no sé qué pasó que al final no lo hicieron, pero tuvieron previsto hace un montón de

## 137:50 - 137:56
años hacerlo, porque ellos lo hacen con acciones, muy bien hecho, o sea ajusta las acciones,

## 137:56 - 138:03
muy bien hecho, sí sí, yo tampoco, bueno pues vamos a intentar a ver si en skype podemos

## 138:06 - 138:14
hacer algo con nuestros amigos, alguna pregunta de maestro de, sí dígame, dígame, cuentas

## 138:18 - 138:24
gestionadas, no, cuentas gestionadas como tal no, porque en ese país no se puede gestionar,

## 138:24 - 138:29
eso es la realidad, otra cosa, no se puede gestionar legalmente, solo se puede gestionar

## 138:29 - 138:33
por una institución de inversión colectiva, nosotros lo que hacemos es desarrollamos carteras

## 138:33 - 138:39
para clientes, por eso como desarrolladores de software lo podemos hacer y les ayudamos

## 138:39 - 138:42
a instalarlo y a colocarlo en un servidor si lo quieren o se la damos a usted para que

## 138:42 - 138:47
usted la opere en su ordenador, si quiere eso ya es decisión, pero la mayoría de gente

## 138:47 - 138:51
pues suele elegir operarlo en la nube, nosotros digamos tenemos una supervisión técnica

## 138:51 - 138:58
de ello, como desarrolladores de software, pero no tocamos, no tomamos decisiones, o

## 138:59 - 139:05
sea, gestionar como tal no gestionamos, si, automático ponemos los sistemas y usted

## 139:05 - 139:12
los supervisa y yo los puedo supervisar técnicamente, pero, o sea, es su cuenta, nosotros somos

## 139:14 - 139:22
un supervisor técnico, no, no se debe, es que no se puede hacer, otra cosa es que la

## 139:22 - 139:30
vida, las fuertes MAM son ilegales en España, si, otra cosa es, yo digo, yo no he dicho

## 139:31 - 139:36
en ningún momento que nadie lo haga, porque mucha gente se salta en los semáforos de

## 139:36 - 139:43
rojo, quiero decir, y es ilegal hacerlo, quiero decir, al final, yo no digo que no se haga,

## 139:44 - 139:51
yo digo que la ley española no permite hacerlo, la ley española no permite hacerlo, la ley

## 139:53 - 139:57
española no solo permite gestionar instituciones de inversión colectiva, lo que pasa es que

## 139:57 - 140:00
los desarrolladores de sistemas tenemos la suerte porque, igual que está TraditMotion,

## 140:00 - 140:07
hay supermercados, todos venden sistemas, eso es totalmente legal, porque en los sistemas

## 140:07 - 140:12
como no tocamos el dinero, realmente, o sea, realmente es un programa que da la orden,

## 140:12 - 140:17
pues somos desarrolladores de software, pero ni tocamos el dinero, ni podemos cobrar por

## 140:17 - 140:23
resultados, que las MAM lo hacen, porque si cobramos por resultados entonces ya sí que

## 140:23 - 140:30
estamos gestionando, eso si yo digo lo que dice la ley española, luego ya cada uno hace

## 140:30 - 140:35
y deshace, pero nosotros lo que hacemos como desarrolladores que somos, desarrollamos sistemas,

## 140:35 - 140:42
nos ponemos a disposición del cliente en algún broker español, normalmente si lo

## 140:42 - 140:45
hacemos en la nube lo hacemos a través de TraditMotion, porque es la plataforma que

## 140:45 - 140:49
nos da más, porque es donde los testeamos, o sea, yo tengo un sistema en el futuro de

## 140:49 - 140:55
TraditMotion o Testion, no me importan los datos, yo el backtesting lo hago siempre

## 140:55 - 141:01
en Testion, porque como backtesting para mí es el mejor, o sea, todas las plataformas

## 141:01 - 141:04
tienen puntos fuertes y no puntos débiles, porque también, por ejemplo, el tema del

## 141:04 - 141:09
64 bits, que es un tema que están ahora mejorando, que no lo tienen todavía, la verdad es que

## 141:09 - 141:16
sí lo tienen, para mí es un punto débil, pero aún así el backtesting para mí es

## 141:16 - 141:28
insuperable. Bueno, como MetaTD está muy de moda en Forex, se usa mucho, los históricos

## 141:29 - 141:35
son muy malos, según me han dicho, yo la tengo aquí instalada, la he usado muy poco,

## 141:35 - 141:39
a mí me han dicho, justamente hoy he estado hablando con un buen amigo que opera con ella

## 141:39 - 141:44
y dice que él los importa porque son un desastre, me ha dicho que él los importa, porque dice

## 141:44 - 141:48
que un backtest ahí no se puede hacer, y que él tiene dudas del backtest también,

## 141:48 - 141:52
no sé, hablábamos entre los dos y le he preguntado si él tenía garantía de decir

## 141:52 - 141:55
que el backtest era bueno, me ha dicho que no lo sabía, la verdad que no lo sé, no

## 141:55 - 142:01
sé, porque yo he visto auténticas, y sí que hay, prefiero no dar nombres, pero realmente

## 142:01 - 142:06
el backtest, claro, es que al final te lo crees, la verdad, yo en Testion me lo creo,

## 142:06 - 142:11
me lo creo, el backtest en Testion, y no el de todas me lo creo, quiero decir que al

## 142:11 - 142:15
final el backtest él lo hace y tú saca un numerito ahí y tú te lo tienes que creer,

## 142:16 - 142:23
quiero decir que al final no deja de ser una estadística, el de MetaTrader, no sé, yo

## 142:23 - 142:29
sé que MetaTrader sale en sistemas muy buenos, yo he visto estadísticas de MetaTrader muy

## 142:29 - 142:38
buenas, sí, supongo que están optimizadas, supongo, pero yo he visto muchas estadísticas

## 142:38 - 142:45
de MetaTrader demasiado buenas, ahora, no sé, no digo que sea, seguramente es el desarrollador

## 142:46 - 142:53
que lo acuerdan demasiado o lo que sea, pero es una plataforma que se tiende a haber estadísticas

## 142:54 - 143:09
muy buenas, seguramente, seguramente, seguramente, sí, sí, sí, sí, es todo probable, no,

## 143:19 - 143:29
no, pero yo donde, no, pero eso puede hacerlo también, no, no, pero eso puedes hacerlo

## 143:29 - 143:37
igual, puedes ponerlos o no, claro, igual, no, no, no, no, yo no digo nada, realmente

## 143:38 - 143:43
la tengo y la he trabajado poco, yo sé gente que lo ha dado a operar y esto que le he

## 143:43 - 143:47
dicho me lo han comentado, pero no lo sé, de verdad, no puedo hablar, yo no he llegado

## 143:47 - 144:07
a operar con MetaTrader, no tengo conocimiento para operar y realmente es como se ve, bueno,

## 144:07 - 144:14
es verdad que MetaTrader hay muchos brokers, precios me preguntabas, ¿qué me preguntabas

## 144:14 - 144:44
de precios antes? No, no, en forex es gratis todo, solo pagas el spread, en forex sí,

## 144:46 - 144:59
pero solo para forex, spread, sí, que es bastante competitiva, un dólar 20 el futuro,

## 145:02 - 145:09
en forex es todo gratis y tienes las mismas herramientas, lo único que es solo para forex,

## 145:09 - 145:14
no vas a poder abrir el futuro de SP, si quieres abrir el futuro de SP tendrás que abrirte

## 145:14 - 145:19
la cuenta de futuro y entonces sí que cumplir los requisitos, pero la plataforma es la misma

## 145:19 - 145:24
en forex y no pagas nada, tienes que abrir la cuenta y poner 2000 dólares para abrir

## 145:24 - 145:30
la cuenta, pero luego no pagas nada, solo que te cobras el spread que va en el, ellos

## 145:30 - 145:38
dicen un 8, yo le he visto un 6, un 6, un 8, está, y los históricos de, a ver, Transition,

## 145:39 - 145:45
bueno, es que solo hablamos en el 6, no sé si usted estuvo en el 6, le recomiendo que

## 145:45 - 145:51
vea el 6 entonces, ah, lo he visto ya, ya hablamos un poco de los datos, realmente Transition

## 145:51 - 145:56
destaca mucho con los datos, las bases de datos están bastante cuidadas, están bastante

## 145:56 - 146:06
cuidadas, sí, yo tengo datos de tic data y los comparo porque tengo datos de tic data,

## 146:07 - 146:14
es que Interactive Blockets en datos no acaba de ser, es que los construye, sí, los filtra,

## 146:15 - 146:31
sí, sí, no, bueno, pues es, en tu utilitas forex contra el 6 yo también no, mira ahora

## 146:31 - 146:36
está un 8 porque tenemos aquí un indicador que nos marca el spread, un 7, ahí lo tienes,

## 146:36 - 146:46
un 7, un 8, un 8, ahora está un 8, un 7, un 6, ¿ves? Menos mala que me ha dado razón,

## 146:46 - 146:50
digo, yo le he visto un 6, es que yo se la voy poniendo un 8, yo le he visto un 6, ahora

## 146:50 - 146:52
está en el horario americano, esto es un indicador que ves que depende de la hora de

## 146:52 - 147:04
cambiar de color y bueno, vamos a ver, lo tenemos, ¿te gusta? Perfecto, para gustos

## 147:04 - 147:17
colores, sí, correcto, y eso diría que es bastante general, todos los que tienen tics

## 147:17 - 147:41
yo creo que sí, yo tengo un histórico hecho con dig data, claro, sí, de acuerdo, pero

## 147:41 - 148:08
qué pasa, ¿por qué no va esto ahora? Cambia la cuenta que no me acuerdo, ahora, no me

## 148:08 - 148:21
ha dicho nada Jesús, pero es que no me ha dicho nada. Bueno, perdonad porque estamos

## 148:21 - 148:28
aquí hablando y yo me acabo de acordar que sigo conectado en directo, ¿ves lo que pasa?

## 148:29 - 148:33
Tenéis que venir, esto va para los entrenadores, tenéis que venir porque lo mejor es la charla,

## 148:33 - 148:37
bueno, y las cervezas, están aquí ahora con unas cervezas, unas copas aquí, sacaron

## 148:37 - 148:45
unos canapés, están sacando aquí un festival, un festival de, no digo más, es como la película

## 148:46 - 148:50
más o menos, ahora ha empezado aquí a circular, yo no la he visto todavía pero me han explicado,

## 148:50 - 148:57
ahora empiezan a entrar las chicas por aquí y no sé cuántas cosas más, en fin, perdonadme

## 148:57 - 149:00
las mujeres que nos estáis escuchando, ya sabéis que los hombres somos primitivos.

## 149:00 - 149:07
Bueno, pues nada, me despido ya de todos vosotros y vosotras, espero, si había alguna ya yo

## 149:07 - 149:14
creo que ya se ha ido con este comentario que he hecho, y nada, pues vamos a intentar

## 149:14 - 149:18
conectar con nuestros amigos de la Trading Week, no sé si lo vamos a conseguir o no,

## 149:18 - 149:25
pero vamos a intentarlo, espero que os haya gustado el webinar y ya sabéis que en cellsandsystemas.com

## 149:25 - 149:34
y en TrayStation.com y en Bolsap.com podéis encontrar información variada y sobre TrayStation,

## 149:34 - 149:38
sobre Cellsandsistemas, si tenéis alguna duda también sobre sistemas o lo que sea,

## 149:39 - 149:45
y el próximo webinar que sería ya el octavo, pues no sé cuándo va a ser, pues supongo

## 149:45 - 149:51
que en un mes o así lo daremos, ¿de acuerdo? En fin, buen fin de semana a todas y a todos

## 149:51 - 149:53
y hasta pronto, chao.
