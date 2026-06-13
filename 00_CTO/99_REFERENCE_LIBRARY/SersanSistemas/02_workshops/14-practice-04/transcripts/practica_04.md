# practica_04

## 00:00 - 00:16
los asistentes están en modo de solo escucha. ¿Qué tal? Muy buenas tardes a todos, a ver un

## 00:16 - 00:23
momentito porque lo que está pasando es que no soy presentador, no soy presentador y por eso

## 00:23 - 00:32
pues no podía compartir la pantalla, pero ya me he nombrado presentador a mí mismo y ahí estamos.

## 00:32 - 00:42
Muy buenas tardes a todos, aquí estamos en una clase más del curso de trading algoritmico,

## 00:42 - 01:01
a ver que tengo todavía que abrir algún programa. 0.5, no 0.5 no, 0.5 es 50% pero sí me da más de un

## 01:01 - 01:11
50% mirado. Hoy vamos a continuar desarrollando el sistema de ruptura en acciones, la parte

## 01:11 - 01:30
0.5. Pero de momento vamos a sentarnos en la parte tendencial y

## 01:32 - 01:39
mandaremos un cierto trabajo optativo por supuesto para para casa, pero antes que nada, antes que

## 01:39 - 01:49
nada había alguna pregunta en el discor, antes que nada, bueno lo había comentado ya Alberto ahí,

## 01:49 - 01:57
que teníamos alguna pregunta sin responder, fijaros que hay un canal donde podemos ver si

## 01:58 - 02:12
trabajamos, para que lo tomemos en consideración, no quiere decir que a lo mejor no estemos en

## 02:12 - 02:16
otro sitio, puede ser que lo hagamos, pero ahí sí que seguro que contestamos, es decir, el sitio

## 02:16 - 02:24
digamos más claro para hacer preguntas relacionadas con el curso, van ahí. Si alguien quiere preguntar

## 02:24 - 02:28
en otros sitios puede hacerlo, pero ya pues depende, te puede ser que te responda alguien,

## 02:28 - 02:34
que no, etcétera. Había habido creo un par de preguntas sobre la plataforma que ya había

## 02:34 - 02:40
contestado a Alberto, nosotros usarla como tal a nivel de trading la hemos usado, yo sí que la he

## 02:40 - 02:45
visto hace muchísimos años, muchísimos años, por lo cual la versión que hay ahora pues no sé

## 02:45 - 02:54
cómo será, antiguamente era para hacer opciones sobre futuros, no sé si será actualmente igual,

## 02:54 - 02:58
al 100%, porque te digo, estoy hablando de una información de hace muchísimo tiempo,

## 02:58 - 03:02
de todas maneras nadie mejor que la propia TrainStation te va a informar de ello, quiero

## 03:02 - 03:08
decir que al final en caso de que tengas dudas, en la web hay un apartado que lo explica, o sea,

## 03:08 - 03:15
lo que sí que es, que entiendo que eso será igual, no tiene nada que ver con la plataforma

## 03:15 - 03:21
de TrainStation a nivel desktop, la versión 10 y la 9.5, en normal y con entera una cosa

## 03:21 - 03:29
completamente aparta, así era antes y yo me imagino que seguirá igual, entonces ya digo,

## 03:29 - 03:34
nada que ver, nada que ver y estaba centrada, de hecho no era ni algorímica en su momento,

## 03:34 - 03:38
no sé si ha cambiado, estoy ahora mismo mientras te hablo mirándolo en la web a ver si veo alguna

## 03:38 - 03:45
cosa distinta, me da la sensación que no, me da la sensación que es un poco parecida y no tiene más,

## 03:45 - 03:50
pero ya te digo, no podemos ayudar mucho más que esto, si no, pues ya digo, hay un chat,

## 03:51 - 03:56
tenéis cuenta, enviar un email al client center, deciros esta plataforma para que sirva y tal,

## 03:56 - 04:01
pero antiguamente era para hacer opciones sobre futuros y era solo para eso, solo para hacer

## 04:01 - 04:10
opciones sobre futuros. Y bueno, poco más, sí, Alejandro también había hecho un comentario en

## 04:10 - 04:21
la parte de pregunta aquí con dos partes, en una nos felicitaba y agradecía el contenido, Alejandro

## 04:21 - 04:27
la verdad que es una persona bastante... del perfil alumno avanzado podemos decir, ya sabéis que

## 04:27 - 04:33
hay distintos perfiles en el curso y que tratamos de aportar valor a todos, aunque lógicamente el

## 04:33 - 04:39
que ya sabe muchas cosas, pues puedes aportar mucho en pocas cosas, porque hay veces que,

## 04:39 - 04:43
como digo, el diablo está en los detalles, hay cosas que pueden ser detalles, que pueden ser muy

## 04:43 - 04:47
importantes, pero en lo que es cantidad de información, lógicamente, pues siempre lo aprovecha

## 04:47 - 04:54
más el que empieza de cero, eso es obvio, pero bueno, luego comentaba el tema de porfolio que

## 04:54 - 05:00
echaba en falta alguna parte avanzada. Bueno, ya te comenté, Alejandro, tomamos nota y bueno,

## 05:00 - 05:05
pues a medida que avancemos hacia la parte porfolio, que lógicamente todavía falta,

## 05:05 - 05:13
porque quiero antes hacer bastantes estrategias más y pues ya veremos, a ver si podemos resolver un

## 05:13 - 05:20
poquito esa inquietud que tienes. Hoy, de hecho, vamos a trabajar este sistema en 100 acciones en

## 05:20 - 05:27
el Nasdaq, pero no con la finalidad de hacer un porfolio sobre ella, sino con la finalidad

## 05:27 - 05:34
de validar la idea, de ver si el sistema funciona, etcétera, etcétera, ¿vale? Pero un poco otro

## 05:34 - 05:41
camino que ya os comenté, que son sistemas que tienen poca frecuencia operativa, pues una de las

## 05:41 - 05:48
maneras de validarlo es juntando activos, y este es lo que vamos a hacer un poco con

## 05:48 - 05:54
este sistema. ¿Podría hacerse por otro camino? Bueno, podría hacerse, pero a nosotros en este

## 05:54 - 06:01
tipo de sistemas nos gusta mucho este método, es decir, meter todo el Nasdaq 100 o en una cesta

## 06:01 - 06:08
de ETFs o en todo el SP500, en un montón de acciones que, lógicamente, pues se comportan

## 06:09 - 06:19
de su manera, pues tratar de validar la idea, la idea ahí, ¿no? Esto por un lado, ¿vale? Entonces ya

## 06:19 - 06:25
está, creo que los demás que teníais comentarios del Discord, de acuerdo, aquellos que todavía

## 06:25 - 06:32
no hayáis entrado, que tenemos un Discord de alumnos que podéis apuntaros, por ahí ya os dejarán

## 06:33 - 06:41
la dirección, y si no nos la pedís, y bueno, pues ya está. Luego, otro tema que quería hablar, que lo dije,

## 06:41 - 06:51
que lo comentaría, lo comento ahora, es colgué la entrevista de Iván, la verdad que ahora no veo

## 06:51 - 07:03
dónde la colgué, porque ahora la encuentro. ¿Dónde la colgué? Bienvenido, quizá, sí, la colgué en bienvenido,

## 07:04 - 07:15
bueno, Iván es, aquellos que no lo conozcáis, él es el gestor de Emerging Funds, es una gestora

## 07:15 - 07:23
que tiene oficina en distintos sitios, en Nueva York, en Dubái, es, la verdad que es todo con la suerte

## 07:23 - 07:30
de que sea amigo personal, además de colega de profesión, y es un tener excelente, como ha

## 07:30 - 07:37
demostrado en su, en el concurso, que es el mismo que ganó la Rey Williams, año pasado que lo ha ganado, ¿no?

## 07:37 - 07:44
Abrí el debate ahí un poquito, aquellos que hayáis visto la ponencia, los que no hayáis visto,

## 07:44 - 07:51
yo os recomiendo verla, Robotrader, cada año participamos hace bastantes años, no me acuerdo

## 07:51 - 07:56
que ya tengo la ponencia, pero bueno, ya os avisaré, creo que era en abril, creo que era en abril,

## 07:57 - 08:03
y bueno, pues ahí cuando la haga ya os lo comunicaré, y lo había dicho,

## 08:03 - 08:08
tengo que ponerle el título, así que tengo que ponerle el título, a ver si se lo paso un día de estos,

## 08:08 - 08:12
bueno, entonces la verdad que la ponencia estuvo interesante, y lo más interesante

## 08:12 - 08:17
estuvieron las preguntas, ahí os puse como debate, ¿no?, de que habían un par de cositas en que no

## 08:17 - 08:22
estamos de acuerdo, que esto por supuesto yo lo, bueno, mira, en cierto, en marzo tengo una reunión

## 08:22 - 08:29
con Iván, y seguro que lo volveremos a comentar, pero lo que quería es que vierais, como ya os he

## 08:29 - 08:35
dicho insistentemente, la teoría que nosotros os explicamos cómo hacemos nosotros las cosas,

## 08:35 - 08:39
y os hemos explicado algunas que también no hacemos, ¿de acuerdo?, porque hay que explicar,

## 08:39 - 08:47
hay que explicarlo todo y explicar lo que nosotros pensamos, pero hay distintos caminos para llegar

## 08:47 - 08:51
a Roma, y además en lo esencial, en lo esencial os aseguro que estamos 100% de acuerdo, porque es

## 08:52 - 08:59
lo esencial, es lo esencial, ¿de acuerdo?, y de ahí no hay variación, el hecho, como por ejemplo,

## 08:59 - 09:04
cuando os expliqué, si os acordáis, el BRAC, y os dije que el BRAC, en mi opinión, a mí,

## 09:04 - 09:09
no tiene mucho sentido, pero no tiene mucho sentido, lo que quiero decir es el nombre,

## 09:09 - 09:15
¿de acuerdo?, es decir, al final un BRAC, el BRAC es, es decir, una optimización convencional es

## 09:15 - 09:21
muy parecida al BRAC, ¿vale?, y si tú haces una optimización convencional y le sacas 4.000 trades,

## 09:21 - 09:26
y no tiene muchos grados de libertad, de verdad, seguramente no hace falta World Forward,

## 09:26 - 09:35
¿vale?, pero hazlo, ¿de acuerdo?, no está de más, no está de más, al final la mayoría de traders

## 09:35 - 09:42
utilizamos varios métodos de evaluación, y realmente si están bien hechos, hay varios que son útiles,

## 09:42 - 09:47
y es verdad que para algún tipo de sistema puede venir mejor, puede venir otro, pero la idea está

## 09:47 - 09:52
clara, y acordaros cuando os dije, significación estadística, representatividad de la muestra,

## 09:52 - 10:01
esto es los cimientos de la metodología clásica, y también es lo que hace Iván, ¿de acuerdo?,

## 10:01 - 10:06
es lo que hace Iván, es lo mismo, ¿vale?, él, por ejemplo, no le gusta World Forward, a Kevin le

## 10:06 - 10:10
gusta, a Andrea Humbert, por ejemplo, tampoco le gusta World Forward, es decir, hay distintos,

## 10:10 - 10:17
hay distintos, como os digo, opiniones, y demás, a mí el Cluster World Forward me gusta mucho,

## 10:18 - 10:25
ya trataremos de hacer en este sistema, como tal, no lo vamos a hacer, porque ahora a medida que

## 10:25 - 10:31
avance la clase lo veréis, los problemas que te vas encontrando, pero en otros sistemas sí que lo haremos,

## 10:31 - 10:39
haremos un World Forward al uso, pero en este no lo vamos a hacer como tal, y podemos acabar validando

## 10:39 - 10:44
la idea, igual, ¿de acuerdo?, es decir, ahí está un poquito el tema, ¿vale?,

## 10:45 - 10:52
y bien, pues vamos un poquito a ir avanzando en la clase de hoy,

## 10:55 - 11:06
tengo tantas cositas por aquí abiertas, esto lo vamos a cerrar, dejamos este gráfico, vamos a abrir,

## 11:06 - 11:15
bueno, tengo ya aquí todo preparado, así que mira, voy a ir abriendo, voy a dejar ya el 3.6 abierto,

## 11:16 - 11:27
porque luego, si tengo tiempo, haremos una cosita en directo, haremos una cosita en directo en

## 11:27 - 11:33
porfolio maestro, principalmente aquí hemos usado un poco porfolio maestro y un mucho porfolio trader

## 11:33 - 11:40
para este sistema, pero bueno, como ya os dije varias veces y voy a insistir en ello,

## 11:40 - 11:49
pues todos tienen sus cosas, todos tienen sus cosas y bueno, por eso a veces usas una cosita

## 11:49 - 11:57
de aquí y a veces otra cosita de allá, a ver, aquí casi que voy a abrir el workspace directo,

## 11:57 - 12:03
porque si no me va a saturar mucho el equipo, sí, sí, sí, voy a abrir el workspace directo,

## 12:03 - 12:16
aquí está, es que esto, cuando estás en directo aquí también el tema de recursos,

## 12:16 - 12:31
hay que vigilarlo porque se colapsa todo rápido, vamos con ello, esto lo abro luego y aquí está,

## 12:31 - 12:39
cualquier duda como siempre recordar que ahí está Alberto, Pilar y también seguramente Víctor y

## 12:39 - 12:55
bueno, estamos ahí todo el mundo atento a vuestras preguntas, bueno, ya estáis viendo un poquito el

## 12:56 - 13:09
sistema en cuestión, me los voy a enseñar en porfolio trader por un lado, aquí está,

## 13:09 - 13:19
aquí lo estoy viendo yo y os voy a explicar un poquito el planteamiento de hoy,

## 13:19 - 13:36
PowerLenguages, antes que nada, si, nos habíais comentado lo del, la verdad que tenía pensado

## 13:36 - 13:43
daroslo hoy, me comprometo a lo largo de la semana, antes la siguiente clase, daroslo,

## 13:43 - 13:53
daroslo, pero todavía no, realmente las clases llevan bastante trabajo de preparación y no me,

## 13:53 - 13:59
era lo siguiente que me faltaba y no llegaba tiempo de hacerlo, vale, pero para la siguiente,

## 13:59 - 14:08
antes de la siguiente clase os hacemos el código, el código y demás, la idea básica porque aquí

## 14:08 - 14:13
este código realmente es muy largo pero de momento estamos usando tres cositas, ¿de acuerdo?,

## 14:13 - 14:20
estamos usando tres cositas, solo la parte tendencial es simplemente el canal y simplemente

## 14:20 - 14:26
el terelink, es lo que hoy vamos a trabajar, vale, bien, recordar el sistema que es simplemente un

## 14:26 - 14:33
canal de Donchan, el pseudocódigo de hecho en palabras, ya os lo pasaré escrito bien como Dios

## 14:34 - 14:44
pero en palabras no es más que tenemos una banda arriba de los n cierres anteriores, por efecto,

## 14:44 - 14:51
acordaros que Donchan hablaba de 20 porque era más o menos un mes, más o menos cuatro semanas,

## 14:51 - 14:57
más o menos la regla de cuatro semanas y entonces en este caso como eran acciones pues nosotros

## 14:57 - 15:02
decidimos hacerlo con los cierres, se podría perfectamente haber hecho con el máximo, hoy

## 15:02 - 15:09
no lo he probado, no lo he cambiado, el otro día ya lo jugamos un poco con ello pero lo vamos

## 15:09 - 15:16
a dejar en el cierre pero podría ser que fuera mejor el máximo, ya digo que no he trabajado a

## 15:16 - 15:23
fondo ese concepto, lo he dejado en el cierre porque a nosotros en acciones el cierre en gráfico

## 15:23 - 15:29
diario normalmente el cierre le damos bastante importancia y por lo tanto pues ya nos parece bien

## 15:29 - 15:35
trabajar con el canal de cierres, el canal de cierres también está la parte baja porque el

## 15:35 - 15:39
sistema permite hacer cortos aunque no lo he trabajado, eso de hecho es lo que os voy a dejar

## 15:39 - 15:47
para el que quiera trabajarlo para casa y ver a ver qué puede hacer y como os decía planteamos

## 15:47 - 15:55
en el código distintas salidas pero hoy vamos a trabajar solo el training, solo vamos a trabajar

## 15:55 - 16:01
también tenemos en el código planteado salir por la media central que aquí no está pintada pero

## 16:01 - 16:12
pero aquí sí, podemos salir también por la media central está planteado está también

## 16:12 - 16:19
planteado salir en n barras está también planteado salir en un stop porcentual también

## 16:19 - 16:28
en un tp porcentual por arriba es decir objetivo y stop y está planteado un training pero como ya

## 16:28 - 16:34
comentamos y vamos a evaluar un tendencial puro y para eso necesitamos dejar con los beneficios

## 16:34 - 16:42
si ponemos tp no vamos a cumplir ese requisito y por lo tanto decidimos solo entrar hoy es lo que

## 16:42 - 16:49
vamos a mirar entrar por cierre por encima del canal y salir solo por training esta es la única

## 16:49 - 17:00
salida además hablamos muy de pasada porque ya comenté que os lo enseñaría un filtro que hoy

## 17:00 - 17:10
vamos a probar también de que es esta parte de aquí a ver un segundo que voy a poner el foco vale

## 17:11 - 17:20
esta parte de aquí no esta parte de aquí no es esta parte de aquí de acuerdo este filtro atr que

## 17:20 - 17:30
simplemente es si el true range de la vela actual es menor que el true range medio mensual por un

## 17:30 - 17:35
multiplicador que vamos a estudiar pero que acabaremos dejando en uno vale porque era la

## 17:35 - 17:40
idea pero como ya os comenté a veces podemos hacer optimizaciones instrumentales para ver para

## 17:40 - 17:47
coger información de la variable y este es un claro ejemplo de bien empecemos por el principio

## 17:48 - 18:03
el principio cual es el principio el principio es evaluar el canal evaluar el canal ya lo hicimos

## 18:03 - 18:13
por un lado con con igualando el stop de los acordes y tp creo que pusimos 05 pusimos uno

## 18:13 - 18:18
a nivel de evaluación preliminar y hicimos un pequeño estudio rápido para ver si

## 18:18 - 18:25
conseguimos seguir adelante por la señal de entrada así que vimos que parecía tener cierta

## 18:25 - 18:33
ventaja y hoy hemos continuado avanzando en esa idea pero ya con la versión trailing esta es la

## 18:33 - 18:42
primera estudio que hemos hecho vamos a presentar 44 estudios vale tenemos aquí la fichita en excel

## 18:43 - 18:51
enseñaré trabajo en sí el portfolio trader pero antes empezamos por la ficha vale vamos a

## 18:51 - 18:59
optimizar o estudiar o a testear el sistema de ruptura de acciones en todo el nasdaq cien de

## 18:59 - 19:05
acuerdo en las cien acciones que hoy cotizan en las acciones cuidado aquí que esto no quiere decir

## 19:05 - 19:12
que estemos haciendo una buena simulación ha pasado de cartera porque no hemos salido en

## 19:12 - 19:17
cuenta las deslistadas y la puntuación que hay pero nosotros estamos validando el sistema

## 19:17 - 19:23
no estamos montando una operativa en la sección vemos estamos evaluando el sistema podíamos

## 19:23 - 19:29
hacerlo en apple podíamos hacerlo en microsoft podíamos hacerlo en google pero eso tendría

## 19:29 - 19:36
y nos dejaría sin prácticamente margen de maniobra para poder analizar los parámetros

## 19:36 - 19:42
porque habría una significación estadística que para nosotros no sería suficiente y una manera

## 19:42 - 19:50
de hacer esto es evaluar todas las acciones a la vez de tal manera que el sistema tenga que tener

## 19:50 - 19:57
un comportamiento bueno en la mayoría de ellas porque seguro que no ganan todas al final pues

## 19:57 - 20:04
puede de esta manera consigues mayor número de operaciones y estaremos de acuerdo que son que

## 20:04 - 20:11
es un activo homogéneo entre sí comparable y que tiene si bastante correlación entre sí aunque

## 20:11 - 20:18
ya veréis que curiosamente al final cuando os muestre un perfomance report completo de una

## 20:19 - 20:23
de una buena de la combinación por ejemplo que de que acabaríamos eligiendo para operar

## 20:23 - 20:30
y veréis que realmente muchas acciones de las acciones entre sí no tienen tanta correlación

## 20:30 - 20:37
con el operando el sistema de resultados mensuales no tienen tanta pero eso lo veremos al final bien

## 20:37 - 20:44
aquí tenemos un poco todos los inputs que hay puestos en el en el sistema nosotros aquí sólo

## 20:44 - 20:55
vamos a trabajar estos que os voy a marcar en rojo vamos a trabajar el periodo del canal que

## 20:55 - 21:02
esa es la que vamos a hacer en esta primera luego trabajaremos traen y y probaremos el filtro

## 21:02 - 21:10
de acuerdo pero es el filtro a ver si tiene algún sentido o no nada más de momento nada nada más

## 21:11 - 21:18
se podría ir hecho se debería también evaluar la parte corta nosotros hoy no lo hemos hecho pero

## 21:19 - 21:25
recomiendo que lo hagáis el que tenga la capacidad de hacerlo que no pues que lo trabaja un poquito

## 21:25 - 21:31
conceptualmente y para la semana que viene empezaremos algo más pero le haremos un pequeño

## 21:31 - 21:38
vistazo también a esta parte al lado corto de este sistema a ver si tiene cierto sentido operarlo

## 21:38 - 21:44
o no de acuerdo o qué cambios podríamos hacer para operarlo en el lado corto porque la idea en

## 21:44 - 21:48
sí se bueno canal de doldrán yo puedo ponerlo arriba puedo ponerlo abajo de hecho ya está abajo

## 21:48 - 21:56
también pero es operable igual abajo que arriba por igual yo os digo que no igual no lo es porque

## 21:56 - 22:02
lógicamente el mercado de acciones tiene un sesgo alcista muy considerable y si se puede operar el

## 22:02 - 22:06
lado corto pero hay que hacerlo de una determinada forma y tendencialmente no es una de ellas

## 22:07 - 22:12
tendencialmente no es una de ellas una de las cosas que aquí no lo hemos hecho posteriormente

## 22:12 - 22:17
cuando hagamos práctica de búsqueda de señales de evaluación de activos también lo miraremos ya

## 22:17 - 22:24
la teoría recordar que hablamos no lógicamente si tú te planteas un setup de entrada decís bueno

## 22:24 - 22:29
si yo tengo un sistema tendencial pues lo voy a operar en aquellos activos que potencialmente

## 22:29 - 22:36
tengan más tendencia las acciones de ser activo esencial no lo no es así en realidad pero no lo

## 22:36 - 22:40
es sobre todo a nivel índice cuando vas a nivel de acción lo es bastante lo es bastante a nivel

## 22:40 - 22:47
índice también es tendencial en el largo plazo pero pero contra más te vas a bajando a frame el

## 22:47 - 22:54
mercado de equity menos tendenciales y más antitencial se vuelve entonces muchos sistemas

## 22:54 - 23:01
que operan acciones operan operan índices sobre todo índices brusátiles operan más bien antitencial

## 23:01 - 23:08
o versiones tipo antitenciales no no el concepto tendencial puro que es más dado de materias

## 23:08 - 23:14
primeras visas baterías primas de divisas y de acciones como digo en contado porque sí que

## 23:14 - 23:23
podemos coger tendencias bastante buenas vamos un poco al concepto que es este y este es el

## 23:23 - 23:28
concepto entonces cómo lo hemos evaluado esto bueno lo hemos evaluado a través de por folio

## 23:29 - 23:42
trader vale que es este este programa que forma parte de multichars ya digo programas y pues

## 23:42 - 23:49
es el que hemos usado pero es usar cualquiera al final lo que hemos hecho aquí es yo os explico

## 23:49 - 23:54
lo que hemos hecho y lo podéis aquellos que tengan es la posibilidad de hacerlo aplicar a

## 23:54 - 24:01
cualquier programa de acuerdo hemos hecho como aquí en el excel alguien se ha fijado hemos usado un

## 24:01 - 24:09
periodo in sample que va desde inicio del 2007 hasta final del 2018 y desde ahí es decir desde

## 24:09 - 24:16
principios de 2019 hasta el pasado viernes hemos usado auto sample vale se podría haber dejado

## 24:16 - 24:20
un tercer periodo ya os he comentado de muchos autores que lo hacen de acuerdo que dejan un

## 24:20 - 24:26
tercer periodo le llaman de validación perfecto nosotros ese periodo como los procesos suelen

## 24:26 - 24:31
durar tiempo suelen ir desde imaginaros ahora que esto estuvieramos empezando a estudiarlo y

## 24:31 - 24:37
siguiéramos pues desde ahora hasta hasta que siga el sistema de estudio que de hecho ya lleva

## 24:37 - 24:42
varias semanas no pues ya varias semanas observando y siguiendo fuera fuera de mostra

## 24:42 - 24:51
en lo que sería una especie de paper trade en esa fase ya estaría listo solemos hacerlo así pero

## 24:51 - 24:57
es correcto también es correcto también dejar un tercer periodo no es una práctica que esté que

## 24:57 - 25:03
esté para nada incorrecta hemos adoptado cinco dólares por tel que es por ejemplo lo que cobra

## 25:03 - 25:08
hoy en día tres station aunque tiene varios planes pero es un plan común para todo el mundo

## 25:08 - 25:15
si haces más volumen todavía puede ser más barato y un tic un tic de slipage vale hemos asumido un

## 25:15 - 25:26
tic de slipage hemos optimizado bueno realmente como hemos hecho exhaustiva hemos puesto net

## 25:26 - 25:33
profit pero en realidad cuando haces exhaustiva no importa porque recoges todos los datos a ver

## 25:33 - 25:40
a qué lo que es por folio trader lo que os decía de las plataformas por folio trader en cuanto a

## 25:41 - 25:49
bactés tiene algunas limitaciones por ejemplo la información que facilita es más del pobre

## 25:51 - 25:58
a nivel de utilización el world forward es infame de acuerdo es infame a nivel de configuración y

## 25:58 - 26:03
demás sobre todo en subversión por folio subversión sistema es bastante mejor ya lo veremos en otro

## 26:03 - 26:11
momento pero a versión por folio es bastante infame y en cambio tiene una gran utilidad que

## 26:11 - 26:15
es que puede ir a mercado es decir puedes acabar de montarlo puede incluso hacer forward testing

## 26:15 - 26:22
dejarlo en simulación más para sistemas central diarios quizá no que esté y puede ir a mercado

## 26:22 - 26:27
puedes configurar el por folio imaginaros que esto final fuéramos a operar las 10 acciones podría

## 26:27 - 26:33
meter por códigos reglas de prioridad vale si caso de que no las quisiera operar todas porque a veces

## 26:33 - 26:40
eso se puede hacer yo lo optimizo en 100 pero luego voy a operar las 10 x las 10 que entre en

## 26:40 - 26:44
primero las 10 que cumplan determinada condición extra de por folio yo puedo montar una regla de

## 26:44 - 26:51
por folio no es objeto ahora este tipo de cosas ya hablaremos más cuando usemos por folios como tal

## 26:51 - 26:58
no pero los comento ya que enseño el programa pues para que lo eso entonces aquí lo que hemos puesto

## 26:58 - 27:09
es un 2% a cada acción con una cuenta de 100 mil dólares hemos metido 2% de máximo a cada

## 27:09 - 27:17
a cada acción por lo tanto permitiendo apalancar en el caso de que de que sea el caso y nada más

## 27:17 - 27:23
luego ya las reglas del sistema propiamente que ya que ya conocéis en el sentido de cierre por encima

## 27:23 - 27:28
de la banda y un trailing esto en esta primera optimización claro cuando tú evaluas recordar

## 27:28 - 27:37
la teoría una entrada hay que hacer una asumción para la salida bueno yo le puse 20% de 20% de

## 27:37 - 27:46
trailing podemos haber puesto 10% da igual le puse 10% de los decía que es pobre porque

## 27:46 - 27:52
esos son los datos que facilita a nivel de por folio bueno le puedes meter un costo fitness es

## 27:52 - 28:03
verdad que aquí tenemos tenemos que hacer uno uno propio para ese que tiene implementado

## 28:03 - 28:09
multichar tiene un sharp esto que veis justo en fitness value realmente es sharp

## 28:09 - 28:17
sharp vale pero de hecho por eso teníamos sortino pero ya no lo hemos hecho porque se

## 28:17 - 28:23
lo tiene por defecto se lo tiene lo tiene por defecto entonces habíamos usado este de acuerdo

## 28:23 - 28:27
para hacer el sortino y ahí es donde nos hemos dado cuenta que no era de por folio de acuerdo era

## 28:27 - 28:36
de sistema y por lo tanto los datos que dan no son correctos sí que sí que permiten para

## 28:36 - 28:42
este ejercicio es un dato que es útil vale es útil porque creo que la lectura que da

## 28:42 - 28:51
probablemente es extrapolable y saldría bastante análoga en el caso en el caso que fuera de por

## 28:51 - 28:58
folio pero realmente cuando tú pones unas reglas cuando tú evaluas un por folio ahí como

## 28:58 - 29:05
como se explicó esto con algunas reglas de prioridad o sea realmente el el motor del

## 29:05 - 29:14
porfil realmente lo que va evaluando cada barra de acuerdo cada barra y cada pasa todos los sistemas

## 29:14 - 29:19
por todas las barras y luego aplica las reglas de ejección monetaria del por folio entonces

## 29:20 - 29:28
el ratio de sharp el ratio de sortino lo que tú quieras hacer no lo puedes calcular sistema

## 29:28 - 29:33
sistema porque no se suman y hasta acuerdo al final al final hay que calcularlo a nivel de

## 29:33 - 29:43
por folio y entonces no se ha implementado entonces hay que hacerlo que no lo habíamos

## 29:43 - 29:49
visto pensamos que era así francamente lo digo y entonces hay que volver a rehacer este ratio

## 29:49 - 29:56
de sharp pero insisto que al objeto esto no nos serviría y para concluir que sharp tiene el

## 29:56 - 30:02
porfolio es decir no sabemos ese dato hoy en día pero sí que a nivel de comparación de sets de

## 30:02 - 30:10
comparación de si el canal de 8 o de 10 o de 14 va mejor es sí que tiene sí que consideramos que

## 30:10 - 30:14
tiene relevancia de acuerdo que es el objeto os lo explico así en franqueza porque veis que

## 30:14 - 30:19
tiene este dato negativo esto qué sentido tiene pero tiene este sentido que os digo este no es

## 30:19 - 30:26
el ratio de sharp real del porfolio sino la suma de los sistemas y de manera individual haciendo

## 30:26 - 30:33
la media y por lo tanto pues está completamente desvirtuada totalmente desvirtuada porque esto

## 30:33 - 30:37
habría que hacerlo con los rendimientos del porfolio de acuerdo aprovechando la diversificación que

## 30:37 - 30:44
da cada cada una de las acciones entre entre sí a pesar de ser el mismo sistema ya lo veis que

## 30:44 - 30:51
sí que la que tiene cierta descorregación por supuesto es absolutamente mejorable pero pero que

## 30:51 - 31:00
ya tiene una cierta cierta es con esto son los datos que hemos obtenido simplemente optimizando

## 31:00 - 31:05
el canal de acuerdo de in sample aquí tenemos

## 31:05 - 31:25
vale vale si si no estaba aquí consultando porque tengo el gráfico lo voy a abrir donde

## 31:25 - 32:03
tengo esto voy a enseñarnos cada vez el gráfico vale esta no es o si es esta no es y está si

## 32:04 - 32:14
está aquí está aquí está aquí vale es esta bueno poco a poco porque digo voy a ir enseñando

## 32:14 - 32:20
cada tengo aquí un montón de cosas para abrir entonces tengo que ir paso paso paso bien esta

## 32:20 - 32:24
es la misma optimización que veis aquí en el extra recogida pero sólo el in sample de acuerdo

## 32:24 - 32:29
aquí lógicamente sólo tenemos una variable y por lo tanto no podemos hacer un gráfico en 3d pero

## 32:29 - 32:36
si en 2d no es más que a la izquierda tenemos net profit o sharp vale este sharp falso le voy

## 32:36 - 32:41
a llamar para para que me trenais pero bueno que insisto a nivel de comparación de ser creemos

## 32:41 - 32:49
que sí que tiene relevancia vale aunque su valor no tenga sentido y el net el net profit recuerdo

## 32:49 - 32:57
el net profit vale aquí en realidad ya te digo no hay no hay una función fitness como tal porque

## 32:57 - 33:02
están todas o sea hay sólo 25 posibilidades están las 25 de acuerdo cuando yo necesito una

## 33:02 - 33:07
función fitness cuando tengo que elegir entre 1000 y me tengo que quedar con 200 entonces

## 33:07 - 33:13
tengo que decir bueno esas 200 por qué criterio me las quedo bien si yo me las voy a quedar todas

## 33:13 - 33:19
da igual igual la función fitness porque yo ahora sí quisiera estos datos les puedo hacer cualquier

## 33:19 - 33:26
cálculo en excel ahora quisiera aquí calcular algo pero de cada de cada una de ellas las

## 33:26 - 33:31
optimizaciones yo podría recoger sus datos y calcular lo que quisiera es decir al final no no

## 33:31 - 33:37
no tengo que elegir por lo tanto la función fitness como tal no es necesaria esto cuando

## 33:37 - 33:46
hay pocas variables pocos inputs pues es interesante de acuerdo aquí de momento hemos dicho que podemos

## 33:46 - 33:52
tener tres inputs en total que pueden variar pero de momento estamos trabajando sólo uno para ver

## 33:52 - 34:00
sólo la entrada sin verse afectada por la por las salidas y dejándola la salida estática dejando

## 34:00 - 34:08
el filtro de volatilidad desactivado el 0 y la salida por trailing fijo en el 0 20 para que no

## 34:08 - 34:15
varíe y por lo tanto ver el canal por sí es lo que hace vale tenemos por un lado como veis el

## 34:15 - 34:26
dato sample en el dato en sample aquí ya estamos viendo que en el gráfico pues bueno se aprecia

## 34:26 - 34:31
claramente no claramente que en el retorno la verdad que es el verde hay bastante estabilidad

## 34:31 - 34:39
vale y en share podemos decir que hay estas dos tres zonas pero donde se aprecia mayor estabilidad

## 34:39 - 34:50
aquí en el sample podemos ver que es esta zona entre aquí que podemos decir que es 8 no 8 hasta

## 34:50 - 34:57
aquí 14 de acuerdo y por aquí para toda esta zona aparentemente de acuerdo aunque aquí tenemos

## 34:57 - 35:05
un share muy alto como veis el 5 bastante bastante bueno vale vamos a ver el mismo en auto sample

## 35:07 - 35:12
siempre es el que nos da o con más información aquí también hubiera sido interesante que en esa

## 35:12 - 35:18
práctica no la no la hemos hecho pero si al final fuéramos a operar haríamos esta misma

## 35:18 - 35:23
optimización invertida para los que os lo explicamos nos gusta mucho está este ejercicio

## 35:23 - 35:34
es decir hemos hecho en sample de 2007 a 2018 y a un sample de 2019 a 2024 así simplificando mucho

## 35:34 - 35:51
pues bueno esto total eran unos 17 años 17 años vale pues hacemos 13 no a ver 17 y más o menos

## 35:51 - 36:03
4 entre 4 y 5 no entre 4 y 5 vale entre 4 y 5 pues haber hecho de 2007 8 9 10 11 a 11 12 de acuerdo

## 36:03 - 36:10
dejarlo esa parte auto sample y hasta ahora en sample al revés auto sample al final y auto

## 36:10 - 36:16
sample al principio de acuerdo este también puede ser un ejercicio aquellos que podáis hacerlo y

## 36:16 - 36:21
luego comparar el auto sample que os sale de esa manera que os sale de la otra y coger esa

## 36:21 - 36:25
esa información porque cuando salen iguales eso sí que es una prueba fantástica de lo que usted

## 36:25 - 36:32
porque en un sistema tendencial como éste es verdad que hay 100 acciones todos estos datos al

## 36:32 - 36:41
final hay mucho sesgo de muestra la práctica hablamos mucho mucho de ello si yo tengo un

## 36:41 - 36:50
activo como esta aunque es verdad que este caso ya está en este caso creo que aplica bien aplica

## 36:50 - 36:55
bien porque tienen en el periodo el sample que empieza en 2007 nada más empezar pues tienen la

## 36:55 - 37:03
crisis de la crisis del 2008 2009 aquellos pues que ya estuvieras en el mercado recordaréis

## 37:03 - 37:09
que hemos empezado aquí hemos empezado aquí más o menos más o menos para ser exactos aquí en esta

## 37:09 - 37:14
línea que os pongo ahora vale entonces sí que empieza un tiro lateral al cista pero luego viene

## 37:14 - 37:19
un desplome vale final hay dos mercados bajistas podemos decir de cierta importancia todo este

## 37:20 - 37:26
este primero cae en sample y el otro cae auto sample y un poco así está elegido pero aún así

## 37:26 - 37:32
repito que es que es interesante esta esta mezcla porque ese ese mercado sí que es común puede

## 37:32 - 37:37
haber acciones que tengan otros porque no lógicamente las 100 no tienen la beta que

## 37:37 - 37:41
tienen microsoft o que tiene apple o netflix que son acciones que tienen bastante beta con el

## 37:41 - 37:47
mercado pero pero claro la mayoría la tienen la mayoría la tienen y por lo tanto ahí sí que

## 37:48 - 37:55
en esas crisis sistémicas de 2008 2009 y el tema del covid 2020 ahí sé que cayeron todas de

## 37:55 - 38:02
acuerdo o para todas se me entiende prácticamente todas huy me avisa esto voy a quitar mi cámara

## 38:02 - 38:09
porque me está avisando que que está justito de calidad para grabar así que le le quito la cámara

## 38:09 - 38:17
la cámara que tampoco pasa nada sino si no me veis porque me está me estaba avisando el mismo

## 38:17 - 38:40
programa que la conexión está perdiendo velocidad si puedo cerrar algo más un momentito que dicen

## 38:40 - 38:50
que me viene al móvil pues no sé ver puede ser que como está en la mesa lo voy a lo voy a poner

## 38:50 - 38:56
si puede ser puede ser porque mi hija me envía un mensaje veo así que igual igual ha sido eso yo

## 38:56 - 39:01
como tengo los auriculares pues no me he enterado a ver lo pongo no molestar y todo caso lo dejo

## 39:01 - 39:14
un poquito más más alejado a ver si así vamos vamos mejor también a veces no me den cuenta yo

## 39:14 - 39:19
con las manos porque es verdad que es micro estos son muy sensibles y cualquier ruidito que haces

## 39:19 - 39:26
aquí cerca se cola se me disculpe se me disculpe bueno pero sigo todo lo que os digo de acuerdo

## 39:26 - 39:34
lo voy comentando porque son cosas de la teoría y son importantes recordarlas no pero aún así

## 39:34 - 39:40
digo nosotros nos gusta mucho hacer esta doble este doble juego por delante y por detrás del

## 39:40 - 39:47
auto sample es lo que os decía este es el de el covid que cae que cae más aquí aunque fue bastante

## 39:47 - 39:58
peor el de 2008 pero ahí ahí está un poquito el tema vale vuelvo a donde estaba bien en auto

## 39:58 - 40:05
sample vamos a abrir ahora este gráfico que tengo es ese gráfico que habéis visto es el

## 40:05 - 40:15
mapa lo que pasa que es el mapa cuando sólo hay una a ver cuando sólo hay una variable donde

## 40:15 - 40:21
entonces no se puede hacer 3d sino que estos de acuerdo es net profit contra la misma contra la

## 40:21 - 40:28
misma variable más fácil todavía obtidos a dos sample a que no t2 no es t2 no es perdón

## 40:28 - 40:54
t1 t1 a ver t1 auto sample aquí está ahora sí es claro que comprobar que sea esa es perfecto

## 40:54 - 41:05
aquí tenemos la t2 por la variable ya que tenemos el gráfico de acuerdo a los que aquí va

## 41:05 - 41:10
prácticamente a medida que aumenta a medida que aumenta degradando es verdad que el auto sample

## 41:10 - 41:16
aquí plantea cierto problema que tampoco lo es tanto al lado del sample pues menos operaciones

## 41:16 - 41:24
normal por lo normal pero ya vamos viendo que la parte baja del canal aunque en este caso por

## 41:24 - 41:31
ejemplo el auto sample con valor 1 es bastante bien no es de hecho el que gana y a medida que

## 41:31 - 41:38
va aumentando el canal va perdiendo va perdiendo rendimiento teniendo insisto el trailing fijo

## 41:40 - 41:48
veamos ahora bueno aquí vemos que en esta zona aquí donde vemos el pico claro sobre todo el

## 41:48 - 41:57
sharp es aquí no en 6 acuerdo ahí en 6 vemos una cierta cierto pico que es verdad que hay

## 41:57 - 42:03
un salto importante al 7 5 6 por ahí podía estar podía estar bien también hay cierta estabilidad

## 42:03 - 42:10
aquí vamos a acabar de ver el all data uniendo los dos vale porque al final

## 42:10 - 42:21
ahí se incorpora un poco todo y donde además tenemos una muestra pues que ronda las de 2000

## 42:21 - 42:34
operaciones las 2000 operaciones fijaros que ahí pues bueno estamos en esa zona de 6 y 10 a ver que

## 42:34 - 43:00
os abro el opt y uno all data aquí lo tenemos aquí tenemos el auto y bien aquí veis un poquito

## 43:00 - 43:07
el gráfico y lo que os decía no en esta parte la verdad que es bastante estable de acuerdo del

## 43:07 - 43:16
doctor en sí es bastante estable fijaros que la zona podemos decir que luego lo veréis optimizado

## 43:16 - 43:22
todo todo junto ya lo veremos pero es bastante estable canal de noche es bastante es bastante

## 43:22 - 43:30
estable y en esta zona entre 5 es visto 10 pues está ahí bastante estabilizado aquí para irnos

## 43:32 - 43:42
para irnos para elegir uno de momento de cara a evaluar la salida pues he cogido el 6 podríamos

## 43:42 - 43:50
haber elegido otro de acuerdo es decir no tiene no tiene tampoco una brutal importancia en este

## 43:50 - 43:57
este momento de acuerdo pero el 6 me ha parecido un buen equilibrio y es el que he decidido bloquear

## 43:57 - 44:03
para evaluar la salida de acuerdo luego ya veremos un performance report de todo de todo esto puesto

## 44:03 - 44:14
en conjunto vale el 6 fijaros que al final tienen 2430 40% de aciertos típico típico

## 44:14 - 44:22
tendencial vale luego ya veremos más datos porque aquí simplemente pues nos sirve a nivel de

## 44:22 - 44:33
compararse de acuerdo no nos sirve de mucho más bien y donde como hemos evaluado el cómo hemos

## 44:33 - 44:41
evaluado el trailing como os digo bloqueando el 6 ahora os muestro el excel de esta segunda

## 44:41 - 44:49
optimización vale que es este simplemente aquí pues lo que os digo es la misma

## 44:52 - 44:59
cantidad de datos las mismas cien acciones bloqueamos el canal en 6 y dejamos oscilar

## 44:59 - 45:10
también 25 25 incrementos entre 0 0 6 y 0 30 el trailing bueno hemos puesto 25 en uno 25

## 45:10 - 45:19
para que tuvieran la misma capacidad de variación aquí tenemos los datos in sample aquí sí que se

## 45:19 - 45:26
aprecia claramente que los datos bajos deteriora muchísimo es decir el trailing realmente

## 45:26 - 45:31
deteriora mucho a la medida que lo acercas mucho claro estamos hablando de un sistema

## 45:31 - 45:37
tendencial opera muchísimo 7000 6300 se lo lleva todo en comisiones y sale demasiado rápido

## 45:37 - 45:43
realmente no tiene no tiene sentido habría que verlo evaluado desde bastante más arriba como

## 45:43 - 45:51
mínimo mínimo 0 10 y eso pues ya digo más no 0 15 hasta más de 0 30 quizá para verlo porque

## 45:51 - 45:55
al final lógicamente estamos en diario lo que quiere es que corran los los beneficios pero

## 45:55 - 46:01
nosotros también nos interesa protegernos y protegernos de las caídas de acuerdo que

## 46:01 - 46:08
es el problema al final lógicamente si evaluamos solo net profit va a querer mantenerse dentro por

## 46:08 - 46:12
eso hay que evaluar alguna cosa más aquí tenemos este ratio de charco que no nos de una buena

## 46:12 - 46:30
lectura nos sirve para este cometido que os digo y vamos a ver el opti 1 in sample es este es este

## 46:30 - 46:47
no tío no no pero optí 2 optí 2 y 2 aquí está optí 2 in sample aquí veis en este en este

## 46:47 - 46:53
perfil es bastante distinto a la anterior porque en el anterior el doncha era bastante bastante

## 46:53 - 46:59
armónico no el cierto a la rango pues por favor cierto rendimiento aquí pues claramente no es así

## 46:59 - 47:04
tiene los valores bajos pues prácticamente no tiene sentido hasta que no llega a la zona de

## 47:04 - 47:11
0 20 0 20 algo nos estabiliza en un cierto rendimiento lo cual pues como os digo tendría

## 47:11 - 47:18
habría tenido sentido dejarlo ir un poquito un poquito más un poquito más pero bueno lo hemos

## 47:18 - 47:26
dejado ahí está hasta el 0 30 que ya creo que es suficiente bueno ahí habéis 0 20 está bien

## 47:27 - 47:32
es el que habíamos puesto antes por la que habíamos visto la evaluación preliminar la

## 47:32 - 47:41
zona de 0 20 pues puede estar bien la verdad que 0 20 de momento no apunta a ir a ir mal si

## 47:41 - 47:52
miramos el auto sample y nos fijamos fijaros que ya por este charco falso 0 18 27 26 esa zona y si

## 47:52 - 48:01
nos fijamos en net profit pues clava el máximo 0 20 0 21 26 18 es decir más o menos la misma la

## 48:01 - 48:41
misma zona vamos a ver este este gráfico este es el 2 si este es este es que si lo

## 48:41 - 48:48
legramos lo vemos aquí el gráfico pues lo que veis no claramente los las partes bajas pues

## 48:49 - 48:56
este especie de charco sí que es bastante volátil pero ya veis que no es estable es el clásico

## 48:56 - 49:00
ejemplo donde se ve que no es estable que varía mucho que puede tener un valor bueno pero lo

## 49:00 - 49:06
siguiente no etcétera y habéis que en la parte final sí que estabiliza y estabiliza en valores

## 49:06 - 49:15
en valores altos claramente entre 0 20 0 25 todos son valores buenos todos son valores buenos y

## 49:15 - 49:22
donde además recogemos una cantidad importante de 3 estamos hablando todavía en este dato fuera

## 49:22 - 49:31
de muestra autosample de 900 800 trades de ese orden y si ya recogemos los dos unidos

## 49:31 - 49:43
pues nuevamente tenemos que se va muy arriba en 0 27 el que más tirando hacia arriba 27 26 25

## 49:43 - 49:55
bastante bastante alto pero aquí a ver que os la abro la dos old data vamos a ver este gráfico

## 49:55 - 50:07
el gráfico ahora me parece que no tengo el dos soldada alberto no lo he guardado aquí pero

## 50:17 - 50:21
lógicamente este interesante que es el que tienen más trade si por lo tanto es el que

## 50:21 - 50:28
está pues más más estabilizado pero aquí se aprecia actualmente esta tendencia que ya veía

## 50:28 - 50:35
bien veis en el chapel bueno pues a partir de 0 20 podríamos haber elegido uno uno más alto

## 50:35 - 50:44
pero al final hemos preferido bloquear el 0 20 aunque repito podríamos haber cogido otro

## 50:45 - 50:55
hemos haber cogido otro pero hemos preferido bloquear el 0 el 0 20 porque si os fijáis aunque

## 50:55 - 51:08
los que dan mayor datos 26 25 también el 0 20 fijaros que tiene el doble de operaciones

## 51:08 - 51:18
de acuerdo tiene siguen manteniendo mantienen bastante buen equilibrio de acuerdo se está

## 51:18 - 51:23
bien acompañado se nota que hay bajada que vuelve a subir es decir bastante estabilizado y

## 51:23 - 51:32
tiene muchos trades nosotros en este tipo de situaciones solemos tirar siempre a más operaciones

## 51:32 - 51:38
solemos tirar más a más operaciones porque nos tira mucho la significación estadística

## 51:38 - 51:47
de acuerdo entonces aquí aunque estemos hablando viendo mejores resultados con 1500 con 1300 la

## 51:47 - 51:55
zona de 0 25 por ejemplo de acuerdo porque tampoco lo grabaríamos demasiado esto a 0 26 27 0 20 0

## 51:55 - 52:01
25 podríamos también haber elegido perfectamente este está está bien tiene un mejor resultado

## 52:03 - 52:15
pero tiene como veis 903 menos 903 menos entonces siempre que estamos ante esa dicotomía siempre

## 52:15 - 52:21
cogemos más trade siempre cogemos más trade aunque suponga un poquito menos rendimiento porque

## 52:21 - 52:28
porque más trade significa mayor significación estadística y también significa mayor respuesta

## 52:28 - 52:37
ante cambios y de hecho aunque gana mucho menos fijaros el drawdown que es bastante bastante

## 52:37 - 52:45
menos aquí podríamos hacer pero ya digo no si tiene sentido si tiene sentido hacerlo porque

## 52:45 - 52:51
realmente como hay gestión monetaria hay unos por ciento y las salidas son porcentuales realmente

## 52:51 - 52:57
el capital está bastante cualizado aunque no sea en porcentaje de acuerdo pero aún así no nos

## 52:57 - 53:14
convence del todo que no sea de acuerdo pero no nos convence del todo pero bueno ya digo que no

## 53:14 - 53:23
no está mal tampoco hacerlo está mal esto es lo que mucha gente llama un recovery factor pero que

## 53:23 - 53:28
es net profit partido por por drawdown la verdad con los datos que tenemos aquí pues es de las

## 53:28 - 53:37
pocas cosas que podemos hacer de acuerdo y pues podrías podrías hacerlo y como veis 0 20 es el

## 53:37 - 53:43
que mejor que cualquier sin haberlo hecho pues ya ya veis ya veíamos que esa zona es la que la

## 53:43 - 53:48
que equilibra porque porque tiene muchas operaciones y tener muchas operaciones normalmente mejora la

## 53:48 - 53:56
respuesta ante ante hablando de un tendencial hablando de un tendencial mejora mejora la respuesta

## 53:56 - 54:04
ante caídas y demás claro hay que estimar bien los costes de acuerdo que se más bien los costes

## 54:04 - 54:14
porque dices tú estimas que prefieres operar mil trens más pero eso solo te va a servir si has

## 54:14 - 54:20
estimado bien los costes y si realmente tienes un tipo de deslizamiento podrías hacer ahí también

## 54:20 - 54:26
una prueba de sensibilidad deberías de mirar bien esto y probarla también en dos tics es decir bueno

## 54:26 - 54:33
pues mira no lo tengo claro voy a volver a hacer la optimización con dos tics en vez de un tic a ver

## 54:33 - 54:41
qué tal a ver cómo lo veo de acuerdo y si ves que no lo ves claro pues podrías entonces decantarte

## 54:41 - 54:49
más al 0 25 pero nosotros aquí nos quedaríamos con el con el 0 20 porque 2400 operaciones con

## 54:49 - 54:59
dos inputs solo además optimizados de manera separada está realmente realmente bien que es esto

## 54:59 - 55:05
luego no quiere decir que lo operamos en las 100 acciones de esto ahora perfectamente podríamos

## 55:05 - 55:14
luego pues operar las 10 acciones de mayor capitalización por ejemplo por elegir un

## 55:14 - 55:21
criterio no debería de operar las 10 también podría hacerlo pero que no es obligatorio no

## 55:21 - 55:26
quiero decir que esto lo estamos haciendo para validar la estrategia para tener una

## 55:26 - 55:32
mayor significación estadística pero no es obligatorio que luego en nuestro plan operativo

## 55:32 - 55:44
o usemos todas las acciones pues aquí hemos bloqueado 0 20 de acuerdo hemos bloqueado 0 20

## 55:44 - 55:59
espérate que vamos a meter este este dato en todas las tablas de acuerdo con es más que el net

## 55:59 - 56:28
profit partido por el máximo 0 18 0 15 y aquí en el otro sample menos de profit partido por

## 56:28 - 56:34
máximo del lado lo multiplicamos por menos 1 para que no dé un número negativo y estamos

## 56:35 - 56:45
0 12 0 15 varía varía un poquito 0 20 está a mitad de a mitad de tabla en el caso auto sample vale

## 56:47 - 56:56
bien este lo voy a guardar pero voy a hacerlo también en la excel de sample perdón en el excel que

## 56:56 - 57:06
lo hemos hecho solo de old data que no lo había hecho ahí lo voy a hacer ahora un momentito porque

## 57:06 - 57:16
es interesante también verlo y con los pocos datos que nos da en este caso luego pasaremos

## 57:16 - 57:23
a maestro y veremos más más información no más el problema que tiene es que es casi posible pero

## 57:23 - 57:50
es imposible pero es muy difícil optimizar con él porque da muy muy pocos muy pocos vamos siguiendo

## 57:50 - 58:24
por ahí la clase del toque de 86 aquí recovery profit partido por máximo bueno ahí veis 5 13 12 12

## 58:24 - 58:30
6 o con lo que más vale que es al final los habíamos quedado también pues con esos 2.406 que

## 58:30 - 58:37
es la misma final porque en la primera llevamos elegido 0 20 pero es verdad es casualidad no

## 58:38 - 58:44
habíamos quedado con 0 20 por defecto vale y vamos con la tercera la tercera hemos

## 58:44 - 58:54
ido a probar un filtro que es totalmente opcional y no es obligatorio pero hemos querido ver hemos

## 58:54 - 59:01
querido ver porque queríamos introduciros un filtro volatilidad aquí para un tendencial y

## 59:01 - 59:09
así pues ya explicároslo pero como digo no es obligatorio pero lo hemos probado vale bueno

## 59:09 - 59:14
para ver un poco como oscilaba que este sí que teníamos muy claro que no le íbamos a dejar este

## 59:14 - 59:22
nivel de granularidad pero queríamos ver un poco queríamos analizar cómo se movía se movía el

## 59:22 - 59:28
tema de acuerdo y hemos dejado el 6 fijo hemos fijado el 20 y hemos dejado el filtro aterre que

## 59:28 - 59:33
es el multiplicador recuerdo que le damos a la tierra ahora nos voy a enseñar en el gráfico

## 59:33 - 59:39
ha quedado claro también hemos dejado oscilar 25 vale esto esto cómo funciona vale esto cómo

## 59:39 - 59:51
funciona el código es simplemente el true range de la vela actual a ver si lo puedo enseñar

## 59:51 - 60:06
aquí en el gráfico aquí abajo fijaros tengo tengo dos aterres pintados y no sé cómo se ve

## 60:06 - 60:22
porque lo voy a poner un poco más grueso voy a poner un poco más grueso para que se vea mejor

## 60:22 - 60:33
ahora se verá mejor supongo hay dos hay dos aterres metidos en el mismo gráfico es lo mismo de

## 60:33 - 60:39
acuerdo porque el true range es el a ver a su vez de una barra de acuerdo entonces yo he metido el

## 60:39 - 60:45
a ver a su vez de uno en amarillo y a la ver a su vez hasta porque está de 14 perdón está mal

## 60:45 - 60:53
porque es el que se mete por efecto no lo había había cambiado es el de 22 porque 22

## 60:53 - 61:02
bueno porque es un mes más o menos sin más no hemos no lo hemos optimizado se podía haber

## 61:02 - 61:07
hecho una una un pequeño mapa pero a ver la pena con este tipo de cosas la verdad porque al final

## 61:07 - 61:13
lo que queremos es ver si la volatilidad va a variar nos hace un filtro volatilidad lo que

## 61:13 - 61:18
hace es comparar la volatilidad actual con la volatilidad de x periodo hay varias maneras de

## 61:18 - 61:23
hacerlo eso que te crea te crea desde el estándar hay algún estudio con el bix que espero en el

## 61:23 - 61:29
curso poderlos mostrar alguno acuerdo con la curva del bix método poco avanzado y creo que

## 61:29 - 61:38
no tocaba en este momento el curso y ese es un método sencillo que al final tiene bastantes

## 61:38 - 61:45
aporta aporta valor aporta aporta más valor de los sistemas de ruptura y a tendenciales que

## 61:45 - 61:50
no tendecía el puro pero bueno lo hemos querido meter para explicaros lo y ya está y se puede

## 61:50 - 61:58
usar simplemente comparar lo que os digo la volatilidad actual la volatilidad de hoy de

## 61:58 - 62:05
la vela actual que esto es esto ahora mismo está hoy recibiendo datos efectivamente está ahí subiendo

## 62:05 - 62:16
estos serios por ejemplo esto es apple y pues tiene la volatilidad de hoy es la barra

## 62:16 - 62:24
amarilla con la volatilidad media del último mes como veis es bastante más alta de decir

## 62:24 - 62:30
está haciendo todos estos últimos días como veis está teniendo una volatilidad baja de acuerdo

## 62:30 - 62:38
para su volatilidad media del mes y esto es lo que evaluamos simplemente de acuerdo ese filtro

## 62:38 - 62:51
consiste en el código que no es perdón consiste simplemente que si esa volatilidad por un

## 62:51 - 62:55
multiplicador que vamos a suponer que es uno vamos a suponer que el multiplicador es uno

## 62:55 - 63:07
con lo cual no es importante decir que es la volatilidad si esa volatilidad de hoy es

## 63:07 - 63:14
menor que la volatilidad de todo el mes si eso se cumple es decir si la volatilidad de hoy es

## 63:14 - 63:25
menor entonces puedo operar si la volatilidad es mayor no esto es el filtro podemos decir natural

## 63:26 - 63:32
para ir largo en tendencia porque normalmente sabemos que el mercado sube con poca volatilidad

## 63:32 - 63:38
y baja con más volatilidad entonces cuando la volatilidad está alta normalmente por eso está

## 63:38 - 63:45
el filtro así lógicamente habrá veces que no pero normalmente el mercado está nervioso el mercado

## 63:45 - 63:51
está tenso y así no se sube acuerdo el mercado tiende a subir tranquilo es verdad que cuando hay

## 63:51 - 63:56
una vuelta del mercado bajista pues ahí puede esto puede hacerte este filtro que a

## 63:56 - 64:01
mejor tardes un poco en volver al mercado hasta que no se tranquilice pero bueno pues perfecto

## 64:01 - 64:06
no al final al final lo que hace es tratar de eliminar operaciones cuando hay volatilidad

## 64:06 - 64:12
elevada es decir cuando la volatilidad de hoy es más alta que la medida podría incluso probarse

## 64:12 - 64:21
con más que en vez de la del mes fuera del trimestre es decir estaría bien es decir estaría

## 64:21 - 64:27
bien porque a lo mejor es que no yo yo sabes que como voy de largo plazo prefiero evaluar contra

## 64:27 - 64:33
la volatilidad de más de más periodos lo podemos lo podemos mirar hemos hecho con la con un mes

## 64:33 - 64:38
pero pero hubiera tenido perfectamente sentido hacerlo con con más con lo que os digo porque

## 64:38 - 64:45
al final pues yo que sé vais a ver que se vuelve mucho más tranquilo no le pongo pues

## 64:45 - 64:54
60 días por decir algo 60 días es que pues se vuelve más más estable de acuerdo se

## 64:54 - 65:00
vuelve más más estable seguimos teniendo una volatilidad baja pero se vuelve un poquito más

## 65:02 - 65:09
bueno más como decirlo más rígida no pero al final tiene más periodos recogidos entonces

## 65:09 - 65:15
tendría tendría las dos cosas sentidos y habría pues que evaluar un poquito muchas acciones como

## 65:15 - 65:22
como ya hemos dicho para ver a ver cómo como como hemos hecho con un con un mes y eso que

## 65:22 - 65:29
hemos hecho en la opti número 3 lo que hemos hecho en la opti número 3 que la tenía por aquí

## 65:29 - 65:40
preparada ver simplemente bloqueado el 6 bloqueado el 0 20 acuerdo y he dejado de 0 a 240 por dejar

## 65:40 - 65:45
25 pero ya os digo que no en este caso no le vamos a hacer queríamos simplemente analizarlo

## 65:47 - 65:53
ver un poco el mapa y aquí lo tenemos vale en esa primera vamos a hacer ya lo de recovery

## 65:53 - 66:08
que con los pocos datos que tenemos aquí pues no podemos hacer muchas más cosas ahora que

## 66:08 - 66:19
tenemos hasta algún dato negativo todo el cabono porque era negativo el profil no sí bueno y ese

## 66:19 - 66:27
73 a bueno bueno claro fijaros no mira es el clásico ejemplo de poca significación estadística

## 66:27 - 66:33
este con con un 0 2 multiplica pero tampoco que realmente no opera de acuerdo no opera nunca

## 66:33 - 66:44
entonces bueno no lógicamente no tiene no tiene sentido con cero con cero para que para que lo

## 66:44 - 66:52
tengáis en cuenta equivale no usarlo es que cero este valor que os marco equivale a no usar filtro

## 66:53 - 67:01
es la versión sin filtro y me queda un recovery de 254 aquí coloca muy bien hay alguno que

## 67:01 - 67:08
coloca ligeramente mejor ligeramente si no incluso bastante mejor vale pero

## 67:10 - 67:20
también el no usarlo queda bastante bastante equilibrado vamos a ver el mapa vamos a ver el

## 67:20 - 67:33
mapa en sample ahí lo vemos 0 es el que queda vez aquí el 0 1 pues queda esta bestial bajada

## 67:33 - 67:40
y a partir de ahí pues a partir de uno veis estabiliza mucho por por sharp y sí que aquí

## 67:40 - 67:46
entre la zona de 0 9 1 1 1 es donde tienes es decir en 1 de acuerdo ahí está claro que nos

## 67:46 - 67:52
queríamos con uno que es lo que os decía este realmente nunca lograríamos así lo

## 67:52 - 67:59
podemos usar en 0 en 1 en 2 si me apuras un 1 y medio vale 1 se suele hacer así el

## 67:59 - 68:05
aterre un aterre y medio 2 aterres 3 aterres de acuerdo no vamos a ir a 1,3 aterres con

## 68:05 - 68:13
lo que os decía de el sentido común y la lógica en cuanto a los incrementos de acuerdo no vamos

## 68:13 - 68:20
a poner 0,33 aterres vale porque eso es una sobre optimización de manual de acuerdo manual

## 68:20 - 68:31
a ver que me han levantado la mano alberto vale bien me comentan el recovery bueno el recovery

## 68:31 - 68:36
recovery simplemente el nombre no importa porque no en todas las plataformas se llama recovery

## 68:36 - 68:43
acuerdo es net profit partido por drawdown vale y esto como el drawdown está negativo se multiplica

## 68:43 - 68:51
por por menos 1 se cambia de signo para que no tenga un valor negativo pero es net profit partido

## 68:51 - 68:56
por drawdown vale net profit es lo que han ganado los cien el sistema aplicado a las

## 68:56 - 69:01
cien acciones y el drawdown es el que ha tenido el porfolio esto sí que es del porfolio está

## 69:01 - 69:10
bien de acuerdo está bien calculado por lo tanto al final es un buen estimador de retorno riesgo

## 69:10 - 69:18
entre esta está el tsi que es justamente este ratio multiplicado por los winners que es el

## 69:18 - 69:26
número el porcentaje de ganadoras de trades acertados vale es otro ratio que se llama

## 69:26 - 69:32
tristation index que es de este estilo vale cuando hablamos de las funciones fitness pues

## 69:32 - 69:38
hablamos muchísimo de esto de retorno de drawdown y hablamos de retorno riesgo de muchos y os dije

## 69:38 - 69:47
que todos tienen mucha correlación y que a nosotros nos gusta mucho el sortino vale trabajé

## 69:47 - 69:54
muchos rutinos os acordáis y también nos gusta bastante loop y vale los iremos viendo durante

## 69:54 - 70:01
el curso de acuerdo los iremos viendo no os preocupéis aquí me interesa ir introduciendo

## 70:01 - 70:10
las cosas poco a poco y en este sistema tendencial que acordaros hablamos que es para un perfil de

## 70:10 - 70:18
medio largo plazo que no necesita una implicación una dedicación continua que no quiere estar todo

## 70:18 - 70:22
el día pendiente del mercado pues bueno buscamos de entrada una estrategia de este estilo y

## 70:22 - 70:28
decidimos usarlo por doncha porque había salido mucho en el curso haremos muchas más cosas y

## 70:28 - 70:36
veremos distintos ratios pero al final es un ratio de retorno de acuerdo que al final casi siempre

## 70:36 - 70:44
son los que son más interesantes de acuerdo ratios de retorno riesgo porque al final retorno

## 70:44 - 70:50
es lo que nos interesa ganar pero el riesgo nos interesa mucho controlarlo porque cuando uno no

## 70:50 - 70:54
controla riesgos se va a tomar bien toda la farola entonces no queremos irnos a tomar bien todo el

## 70:54 - 71:02
mercado y sobre todo cuando uno empieza debe fijarse más que nada en el riesgo porque el

## 71:02 - 71:07
riesgo es lo que nos saca de la partida es lo que nos envía para casa y no podemos permitir

## 71:08 - 71:15
que nos envíen para casa de acuerdo eso es lo que no podemos permitir bajo ningún concepto y por

## 71:15 - 71:24
eso es vital vital vital controlar el riesgo vale vamos al auto sample estamos evaluando el filtro

## 71:24 - 71:32
estamos evaluando el filtro por si solo habiendo bloqueado el canal habiendo bloqueado el canal

## 71:32 - 71:42
en seis que francamente podría haber estado en otro y en 0 en 0 20 el tréil que también

## 71:42 - 71:46
habían varios pero sé sí que pues por ahí parecía equilibrar bastante bastante bien

## 72:18 - 72:27
que haces el directo que dicen no a ver a bueno aquí hay combinaciones como habéis visto antes

## 72:27 - 72:44
0 1 0 2 pues el auto sample en este caso dan 0 y fijaros tiene divisor por 0 porque es que

## 72:44 - 72:52
no llega ni a operar el auto sample no no hace no hace trade pero aparte de eso es que en auto

## 72:52 - 73:00
sample justo el valor 1 es el que queda mejor colocado en el retorno en retorno vamos a ver

## 73:00 - 73:32
el mapa el mapa y t2 no pero no t3 auto sample aquí lo tenemos que lo tenemos carlos en la parte

## 73:32 - 73:44
baja pues que no vale la pena ni comentarlo y a partir de ahí 0 9 1 1 1 2 5 toda esta zona

## 73:44 - 73:49
que ahí ha cuidado el caso 7 veces para que empieza a degradar en la zona de 1 la verdad que

## 73:49 - 73:56
está bastante 1 1 2 está bastante bastante cómodo bastante cómodo ahí también aquí en el recovery

## 73:56 - 74:01
pues se aprecia poco eso es el recovery al final se aprecia un poco eso el 0 coloca bien en 0

## 74:01 - 74:06
coloca coloca bien vamos a ver en el old data que es donde al final siempre hay más trades por lo

## 74:06 - 74:12
tanto más significación estadística y que al final recoge la parte optimizada y la parte no

## 74:12 - 74:23
optimizada está bien analizar el old data no penséis que la teoría que lo hicimos al final

## 74:23 - 74:30
está bien comparar el sample comparar el sample es muy importante perfil de optimización acordaros

## 74:30 - 74:38
y bastante interesante esto de el auto sample por delante el auto sample por detrás moverlo de

## 74:38 - 74:43
acuerdo mover la muestra que es parecido a lo que hace el braque pero nosotros no le hemos puesto

## 74:43 - 74:55
nombre pero pero es parecido a lo que hace el braque y pero al final la elección puede

## 74:55 - 75:00
perfectamente hacerse con el old data de acuerdo pero siempre que haya significación y que sea

## 75:00 - 75:05
concordante con lo que hemos visto en el auto sample y el sample final eso es la unión de los

## 75:05 - 75:14
dos el hecho hace que la caudman y es lo comparto una cosa es la variación de la cosa y es la

## 75:14 - 75:18
selección de parámetros le decía yo para elegir los parámetros cojo la optimización hasta ayer

## 75:18 - 75:25
solo decía caudman hasta ayer porque porque me interesa me interesan los todos los datos

## 75:25 - 75:31
disponibles yo ya he evaluado el sistema considero que es robusto considero que la franja de

## 75:31 - 75:39
optimización imaginaros aquí la zona de entre 6 y 12 por ahí o vale y el trailing pues lo voy a

## 75:39 - 75:43
dejar ya fijo en 0 20 voy a ver el canal bueno pues a lo mejor optimizo sólo el canal con 0 20

## 75:43 - 75:50
filtro el filtro en 1 y el trailing en 0 20 y le voy a optimizar solo el canal le meto todo el

## 75:50 - 75:55
histórico que tengo y le meto hasta el último día y con eso el hijo puedo perfectamente hacer eso

## 75:55 - 76:01
sería un comportamiento correcto con la idea ya validada con la idea ya validada y considerada

## 76:01 - 76:07
robusta y en la zona que yo voy a voy a operar y ahí la elección la haría mirando varios casos

## 76:07 - 76:17
miraría sortino de acuerdo del sample de distintos ratios miraría aquí recovery pero podría hacerlo

## 76:17 - 76:23
con el old data y optimizado hasta el último día perfectamente aquí veis lógicamente los primeros

## 76:23 - 76:29
saben con un recovery muy alto porque no operan pero luego pues ya nos vamos a ir unos 4 0 4 0

## 76:29 - 76:35
acuerdo aquí el 1 cae un poquito más nos sale en recovery también puntual de hecho el recovery sale

## 76:35 - 76:44
bastante mejor el 0 bastante mejor el 0 que el que el 1 de acuerdo con lo cual aquí operarlo o no

## 76:44 - 76:59
está dudoso está dudoso está dudoso vale ser uno es aquí vamos a ver el mapa y por qué sabroso

## 76:59 - 77:06
bueno es algo que es normal porque eso que os digo en los tendenciales puros es no son los filtros

## 77:06 - 77:13
no son tan eficaces donde son muy eficaces en los temas de breakout en los temas de breakout que

## 77:13 - 77:20
este lo haremos breakout no hoy lo podemos plantear pero no lo hemos analizado que hemos hablado de

## 77:20 - 77:26
él pero como breakout es probable que aporte más es probable que aporte que aporte más aquí es

## 77:26 - 77:34
discutible aquí es discutible pero lo queríamos explicar y ver cómo lo hubiéramos analizado que

## 77:34 - 77:40
es un poco al final de acuerdo no no metido a saco todo optimizado y a ver qué nos sale no

## 77:40 - 77:45
claro lo veremos eso también ahora veremos todo optimizado a ver qué nos ha salido a ver y 3

## 77:45 - 77:54
all data aquí tengo el mapa aquí está vale lógicamente los valores bajos pero ahí veis a

## 77:54 - 77:59
partir de 1 pues queda bastante estabilizado lógicamente el 0 el 0 también está ahí pues

## 77:59 - 78:08
bastante alto vale pero aquí eso 0 o 1 de acuerdo no hay no hay más es el es el juego que yo que yo

## 78:08 - 78:19
haría un poco el 0 o 1 por recovery aunque es un tanto precipitado no no es tan este no es tan

## 78:19 - 78:26
concluyente esto pero no cobrir tampoco es la planación de versa quiero decir que no ahora no

## 78:26 - 78:31
no si recovery no da no no es así hay otros factores pero se dieron poco los dos candidatos

## 78:31 - 78:58
de acuerdo aquí tenemos 2.400 y tenemos 2.200 en esto aquí lógicamente me podías decir no no

## 78:58 - 79:14
estaba viendo es que hemos tenido a ver déjame mirarlo aquí no abiertas tantas que las voy a

## 79:14 - 79:40
saber no ya no sé cuál es cuál es cuál a ver opti 3 opti 3 la data está aquí está el 1 si

## 79:40 - 79:59
si 1477 y el 0 aquí en 14 vale en 14 yo aquí francamente con esta información no lo veo muy

## 79:59 - 80:11
claro que habría que realizarlo un poco mejor pero sí que perdemos 206 en un filtro es para

## 80:11 - 80:18
perder 3 y cuidado con el nada si es lo que pasa que fijaros que ganamos un poquito de un poquito

## 80:18 - 80:29
de profit pero perdemos la blanca entonces a costa de ese ese profit no no sabes ganar

## 80:29 - 80:36
realmente no acaba de conseguir reducir el riesgo que es quizá donde más debe actuar

## 80:36 - 80:43
filtro de acuerdo saqué un filtro al final que estoy buscando yo estoy buscando pues evitar

## 80:43 - 80:50
trades negativos es verdad que mejora el porcentaje de acierto que es lo lógico pero no hay mejor el

## 80:50 - 80:57
drawdown esto habría que profundizar un poco más podemos hacer esto vamos a intentar mirarlo

## 80:57 - 81:03
esta hora te había pensado cuando hagamos la pausita de cinco minutos tratar de montarlo

## 81:03 - 81:20
ayer y lo podemos lo podemos mirar pero yo con esta información en el filtro la verdad no lo

## 81:20 - 81:32
veo bien le he hecho toda junta porque porque quería mostraros el mapa 3d de acuerdo queríamos

## 81:32 - 81:40
el mapa 3d y entonces hemos hecho esta opti junta que es la opti junta pues el canal de

## 81:40 - 81:49
1 a 25 el trailing de 6 a 30 que de 6 hemos visto que no pero por hacer la misma y el filtro 0 o

## 81:49 - 82:00
1 0 o 1 simplemente es decir no o sí pero con uno también quizá mejor en vez de 22 a mejor va

## 82:00 - 82:05
mejor poniéndole más más un periodo mayor la verdad que no lo hemos mirado pero podríamos

## 82:05 - 82:11
podemos directamente mirarlo nos llevaría mucho rato y puede ser porque a lo mejor simplemente

## 82:11 - 82:18
la volatilidad de un mes pues es una comparación demasiado cercana pudiera ser pero pero vaya así

## 82:18 - 82:24
excursito sí que da una cierta mejora pero no en ratios de no en el recovery da una cierta mejora

## 82:24 - 82:33
rendimiento pero no a mí no me no me convence porque un filtro es sobre todo sobre todo para

## 82:33 - 82:41
mejorar el perfil de riesgo pero bueno hemos hecho esa optimización aquí ya tenemos 1250 combinaciones

## 82:41 - 82:48
con las sin acciones ya es un poquito más intensiva pero realmente por los grados de libertad que hay

## 82:48 - 82:57
se podría hacer podría hacer pero bueno yo he preferido enseñaros la si para que la vierais

## 82:57 - 83:09
paso a paso vale bien tenemos aquí el sample vamos a poner aquí también el recovery vale con

## 83:09 - 83:30
profit dividido por máximo lauda operamos por recovery aquí fijaros que nos da en el

## 83:30 - 83:40
sample nos da el mejor el filtro activado 25 y 0 12 0 12 de decir bastante distinto lo que hemos

## 83:40 - 83:51
elegido en muy distinto vamos a ver el mapa de esto vamos a ver el mapa de esto 84 in sample

## 83:51 - 84:00
aquí podemos ver el mapa en 2d mirando a una variable o podemos mirar el mapa en 3d para

## 84:00 - 84:05
mirar el mapa 3d también tenemos que hacer alguna asupción porque tenemos tres variables

## 84:05 - 84:12
que bloquear una que es fácil porque como tenemos el 0 1 pues le vamos le podemos poner el 0 vale

## 84:12 - 84:21
o le podemos poner el uno 0 y le podemos poner vamos a hacer lo grande para que así veáis el

## 84:21 - 84:27
gráfico lo mejor posible lógicamente lo que os decía veis el trailing aquí no tiene mucho sentido

## 84:27 - 84:36
de verdad pues ha sido cortarla hecho podemos hasta hacerlo esto aquí no me dejas a pensar

## 84:36 - 85:04
que se podía bueno creo que sí que se puede dejar aquí lo que puedo es pintar las dos del 0

## 85:04 - 85:12
y el uno veis ahí podéis veis que la verdad que no creo que se vea muy bien este con el 0 y el

## 85:12 - 85:27
1 lo puedo poner que marcar una u otra es el 0 es quiere decir que con el valor 1 aquí en esta

## 85:27 - 85:35
parte de valores más bajos pues parece ir mejor pero va bastante en línea en cambio en el 1 pasa

## 85:35 - 85:42
lo contrario los valores bajos va mejor lo voy a poner bloqueado porque así queda un poco para

## 85:42 - 85:51
ver lo que en directo creo que va a ser más más confuso así que voy a activar esto la barca de

## 85:51 - 86:07
agua para que la quita a veces ayuda un poco a ver si así nos molesta lo de abajo no hay

## 86:07 - 86:19
vemos un poquito esto sería bloqueando el 1 lo que os decía el canal vez canal es muy estable es

## 86:19 - 86:25
el canal no acordaros lo que lo hicimos en excel es que os decía vez así se ve parecido

## 86:26 - 86:29
esto es lo que vemos en excel que ya os lo comenté multichats lo hace porque no tenemos

## 86:29 - 86:36
en excel también lo podemos hacer en excel pero multichats lo incorpora es bastante interesante

## 86:36 - 86:44
aquí en las partes bajas del canal como degrada muchísimo pero a partir de 5 o 6 veis ahí en un

## 86:44 - 86:50
poquito estamos en el in sample ahora o iremos pero es bastante estable bastante estable y la

## 86:50 - 86:55
zona del filtro sí que lo hemos quedado un poco bajo parece que es más alto pero lo que les decíamos

## 86:55 - 87:03
de los trades pero hay que verlo hay que verlo 0 20 está ahí al borde de gradar está al borde

## 87:03 - 87:13
de gradar está un poquito justito pero 20 es un poquito justito ese es con el con el filtro

## 87:13 - 87:18
activado y con el filtro desactivado fijaros y con el filtro desactivado parece que alarga un poco

## 87:18 - 87:34
más pero es que parece que parece que la llenura llega un poquito más allá no así es desactivado

## 87:34 - 87:45
es muy parecido pero ya vemos que todo pues toda esta zona 0 20 0 25 en el caso del filtro y

## 87:45 - 87:54
don chian pues ya digo desde 6 7 8 10 20 es decir es muy estable es muy estable tiene pocas pocas

## 87:54 - 88:03
diferencias de acuerdo esto al final que está indicando lo que muestra es estabilidad está

## 88:03 - 88:07
simplemente es estabilidad lo que es lo que queremos esto es lo que llamamos un mapa de

## 88:07 - 88:14
optimización que hay muchos nombres en la literatura dependiendo de nombres pues más guays como todos

## 88:14 - 88:21
pero esto es el mapa de optimización de toda la vida que hemos hecho que nos vas a ver más sensibilidad

## 88:21 - 88:27
de variables a mí que me interesa pues variables que su vez sus vecinos estén bien decir esto es

## 88:27 - 88:35
bien esto es bien para el lado del canal para el lado del teletrello parece que degrada más pero

## 88:35 - 88:43
tiene un punto falso porque como lo hemos graduado tanto la mente nos esga un poco por eso viene bien

## 88:43 - 88:49
el watermark este para evitar no ver un poco eso no nos esga pero realmente también es bastante

## 88:49 - 88:56
grande la zona también es bastante grande tenemos una zona aquí realmente grande que sí que quizás

## 88:56 - 89:00
más 25 habría que estudiarlo mejor esto yo me he quedado en el 0 20 por lo que os he dicho

## 89:00 - 89:08
los trains porque considero tener suficiente margen todavía para caerme mucho pero es verdad que 0 25

## 89:08 - 89:16
se ve más cómodo a nivel de estabilidad se ve más más cómodo y que incluso el 6 lo mismo en 6 quizá se

## 89:16 - 89:24
ve un poco más cómodo la zona de 15 de 12 12 0 25 quizá parece más estable parece más estable

## 89:24 - 89:32
en este gráfico de ese orden pero bueno que estamos en el in sample vamos ahora al auto sample a

## 89:32 - 89:38
ver qué conclusiones sacamos aquí lo que hemos dicho aquí parece en el mapa a mí lo que veo un

## 89:38 - 89:51
poquito más estable es esta zona aquí más o menos es 0 12 es este 12 por ahí 16 pero 12 0 11 claro

## 89:51 - 89:57
es que hay mucho trailing ahí todos están ahí es en la zona de recovery alto no cero 12 no

## 89:57 - 90:01
perdón cero 20 pico perdón perdón me equivocaba me equivocaba esto es demasiado bajos lo de más

## 90:01 - 90:06
abajo equivocado equivocado veis dame ya mejor recovery pero en el mapa no se ve tan estable

## 90:06 - 90:15
es esto esto es muy buen ejemplo para que veáis que a veces lo cerrado no que a veces no es el que

## 90:15 - 90:24
el que es aquí bueno ahí estaba el filtro activado es activado pero aquí alterna activado y no

## 90:24 - 90:33
activado que parece más activado vamos a ponerlo en activado y está esa y espera que me gusta más

## 90:33 - 90:49
que se vea el gris también la volumen al gris es aquí esta zona no con el 1 con el uno que se mueve

## 90:49 - 90:55
un poquito es claro es que el que es es detalles ya digo estar ahí todas el 0 es lo que os decía

## 90:55 - 91:05
parece más estable parece más estable 0 pero dentro de la zona cómoda vez es más más abrupto cambio

## 91:05 - 91:10
el uno perdón 0 poquito más estable es un poquito más estable se mueve pero es un poquito más

## 91:10 - 91:17
estable entonces en el 0 sí que iríamos por esa zona más o menos más o menos pero en cambio fijaros

## 91:17 - 91:23
que ahí nos están saliendo que los mejores da muy bajo da un recovery recovery de equilibró entre

## 91:23 - 91:27
retorno y riesgo da muy bajo que estamos mirando en el profit podíamos mirar también recovery

## 91:27 - 91:32
por el recovery no porque no lo no le metió en el modelo podría mirar de la hora por ejemplo

## 91:32 - 91:33
vale podría mirar a bravado

## 91:35 - 91:43
ese es el bravado que fijaros que cambia completamente el el profit lo da en la

## 91:43 - 91:53
parte alta el bravado lo da bajo en el 0 a 0 8 por eso viene bien el recovery no lo lo

## 91:53 - 91:57
podía haber metido como fitness pero no lo he hecho entonces ahora no lo puedo lo podía hacer

## 91:57 - 92:04
pero no lo tendría que hacer lo podía ver con un archivo para que prepararlo y no lo tengo listo

## 92:05 - 92:11
lo que sí que podemos meter aquí es el el sharp el sharp este falso que tenemos pero bueno pero ya

## 92:11 - 92:18
digo que es es es falso pero pero sirve un poco veis como al final lo que os digo en esas zonas

## 92:18 - 92:23
sigue tirando más para el profit y aquí se ha igualado más ya no es tan dramático la caída

## 92:23 - 92:29
porque porque el riesgo en la parte baja también lo conciberá bajo cuando lo consideraba pero

## 92:29 - 92:35
estaría bien bien verlo en el recovery que un poco lo vemos aquí pero pero eso que os digo

## 92:35 - 92:40
el recovery cambia un poco pero por net profit ahí el mapa en el profit está bien está bien está bien

## 92:40 - 92:46
también teniendo cuenta donde saldrá el recovery estaría estaría muy bien pero fijaros cómo

## 92:46 - 92:53
estabiliza en este este sharp la zona ya se vuelve absolutamente plana plana plana tanto con 0 como

## 92:54 - 93:04
se nota planísima realmente es enorme no aquí hay un poco de cráter pero pero si es ahí de la zona

## 93:04 - 93:10
0 25 es donde empieza la zona plana lo que pasa que está ahí también lo de los tres bueno este

## 93:10 - 93:17
es el sample sample vamos ahora a ver el auto sample es muy muy interesante poco para que veáis

## 93:17 - 93:24
cómo tenemos que analizar los los sistemas de este tipo que al final tienen pocas operaciones lo que

## 93:24 - 93:33
hacemos juntar acciones y a través de ellas que esto quiere decir que no va a ir óptimamente

## 93:33 - 93:38
en ninguna pero va a tener un buen equilibrio entre todas por tanto es más robusto mucho más

## 93:38 - 93:45
robusto adaptarse a todas que adaptarse a una aparentemente mejor adaptarse a una sí claro si

## 93:45 - 93:52
tienes la certeza que el ajuste va a ser en el futuro sí pero se explica mucho en la teoría al

## 93:52 - 93:57
final no tenemos certeza sobre el futuro tenemos que tratar de poner las probabilidades a nuestro

## 93:57 - 94:04
favor y eso pues lo hacemos sobre todo pues priorizando la robustez y como con este ejemplo

## 94:04 - 94:11
que estoy poniendo bien aquí en el auto sample bajamos número de trades y aquí fijaros que el

## 94:11 - 94:20
mayor recovery lo lo da a cero el canal en uno y 0 11 por decir súper rápido operando un montón

## 94:20 - 94:27
pero fijaros que pues bajando bastante el rendimiento pero también el dragón y cuidado

## 94:27 - 94:39
también el dragón interesante no aquí en la mayoría todos porque como ni fijaros que están

## 94:39 - 94:47
en el 1 en el 2 en el canal el canal súper súper bajo hasta que no llegas aquí 11 5 20 no empiezan

## 94:47 - 94:56
a aparecer algunos otros pero realmente lo dan los sex que son muy muy rápidos aquí insisto que

## 94:56 - 95:03
convendía hacer un más sensibilidad al slip y tener claro que uno puede ser dependiendo de

## 95:03 - 95:11
qué acción puede ser un poco justo un poco justo de hecho los futuros muchas veces metemos uno y

## 95:11 - 95:20
medio aunque es depender porque aquí vamos compramos en realidad compramos en la apertura

## 95:20 - 95:26
la apertura tiene mucha mucha volatilidad entonces no no necesariamente el slip de apertura tiene

## 95:26 - 95:34
que ser contrario porque como vamos en ruptura pero de datos de cierre a veces entra mejor decir

## 95:34 - 95:40
no no no es un sex como claro pero hay que contar que que que de media el normal es que sea negativo

## 95:41 - 95:50
pero habrá muchos que serán positivo en este tipo de entrada bien vamos a ver el mapa vamos a ver

## 95:50 - 95:56
el mapa en este en este caso es aquí lo que os digo ya las optimizaciones como que no son

## 95:56 - 96:02
tan claras porque porque hay demasiadas variables de acuerdo y por eso lo que lo que os he enseñado

## 96:02 - 96:09
de esto paso a paso no siempre es mejor de esta manera no hacerlo de manera independiente que

## 96:09 - 96:14
también se puede hacer y podemos también sacar conclusiones con una opinación global no existe

## 96:14 - 96:23
mal pero es mejor práctica hacerlo una a una de acuerdo a hacer conceptos independientes primero

## 96:23 - 96:40
el canal para la entrada luego para la salida bien el mapa del auto sample lo tengo aquí estamos

## 96:47 - 96:56
creo que estoy en el perfecto bien estamos caros que hay los vértices los vértices del

## 96:56 - 97:04
trailing no ya se vuelven más ásperos los vértices más ásperos estamos con el filtro activado

## 97:04 - 97:09
pero el filtro es activado es parecido cambia un poco pero es parecido en el

## 97:09 - 97:13
plazo que cae a medida que se va para hacer el canal aquí es un poco al revés lo que hemos

## 97:13 - 97:20
visto antes que el canal corto rápido bueno también porque está afectado por la última

## 97:20 - 97:29
parte de mercado los últimos años y pues bueno nos ha interesado ahí ser más rápido aquí si

## 97:29 - 97:39
metemos drawdown vamos a ver el gráfico por drawdown como cambia no se vuelve absolutamente

## 97:39 - 97:46
extraño donde quiere el canal aquí todo lo contrario es el canal muy elevado muy elevado

## 97:46 - 97:53
y con un trailing muy rápido de acuerdo muy rápido eso es lo que quiere pero no tener

## 97:53 - 98:01
lógicamente a nosotros nos interesa el equilibrio porque es solo por si solo pues no aporta no

## 98:01 - 98:09
vamos a ver este sharp falso que tenemos mucha estabilidad muy extraño también mucha mucha

## 98:09 - 98:19
estabilidad aquí pero más riesgo como veis en el canal corto curioso es que línea recta

## 98:19 - 98:25
tira aquí con el trailing fijo no porque te saca muy rápido seguramente sale vuelve a entrar sale

## 98:25 - 98:29
vuelve a entrar sale vuelve a entrar y hace muchísimas operaciones pero bueno de esa

## 98:29 - 98:39
manera pues ha conseguido evitarse la seguramente las correcciones vamos a ver el old data ya tienen

## 98:39 - 99:08
poco la información de ambos bueno pues recoger y pues tenemos ahí una bajita sola en el 1 se

## 99:08 - 99:15
va rápidamente ya la zona de 20 el canal alternando entre 0 y 1 no tiene muchos es guay y el trailing

## 99:15 - 99:23
más bien bajito claro ser más bien bajito que un poquito más de rapidez poquito más de rapidez y

## 99:23 - 99:45
con muchísimos trades muchísimos muchísimos trades vamos a ver el mapa aquí estamos ahora con

## 99:45 - 99:55
uno de filtro que pues vemos inicial subida por net profit como pues lógicamente bueno lógicamente

## 99:55 - 100:05
degrada mucho al principio en ese ese trailing tan rápido y aquí lo quiere más bien alto 0 20

## 100:05 - 100:13
todavía está justo ahí parece que 0 25 es mejor profit de acuerdo se ve como se estabiliza y él

## 100:13 - 100:20
aquí sí que aparece el canal ya más bajito es el canal aparece ahí más bajito está más bien en

## 100:20 - 100:28
4 4 5 y 6 un pico pero baja rápido y cuidado bajar rápido y bajar rápido y mirar qué peligro

## 100:28 - 100:38
tiene la derecha el cercano ahí aquí parece mejor esta zona está muy sensible no muy sensible

## 100:38 - 100:47
muy muy sensible no y además con ese trailing ahí al 0 30 acordaros ya operando poco operando

## 100:47 - 100:58
poco si lo vemos en trago down ser al revés esto ya os lo digo es totalmente inverso es

## 100:58 - 101:09
totalmente inverso llanura planísima y con con el con el trailing muy muy muy bajo haciendo un

## 101:09 - 101:15
montón de operaciones pero con muy poco retorno como habéis visto antes tanto en 0 como en 1

## 101:15 - 101:28
acuerdo tanto en 0 como entonces pues no equilibra aquí el único dato que tenemos un poco para ver

## 101:28 - 101:34
mixto es el sharp falso este que tenemos es el único que podemos usar un poco de retorno

## 101:34 - 101:40
riesgo de lo que nos permite a nivel de porfolio es un sistema individual tienen más margen y

## 101:40 - 101:46
fijaros que aquí pues sí ya vemos que el don chan da igual casi que casi da igual que don chan cojamos

## 101:46 - 101:54
y que el trailing lo queremos elevado es verdad que aquí sí que el 0 20 parece tener margen tener

## 101:54 - 102:02
tranquilidad está por aquí pero más establecer o 25 de acuerdo así que viendo estos datos sí

## 102:02 - 102:09
que quizá parece mejor el 0 25 que 0 20 queremos elegir ahora lo iremos lo iremos viendo

## 102:11 - 102:22
vale bien esto cuanto a las optis que ya tenía preparados voy a hacer ahora 5 minutitos 5

## 102:22 - 102:32
minutitos de descanso y vamos luego a montar en maestro alguna de estas combinaciones generalizarlos

## 102:32 - 102:42
ahí un poquito un poquito con más con más información vale vamos a coger algunos candidatos

## 102:42 - 102:50
los vamos a y los vamos a mirar ahí en maestro de acuerdo así que de momento voy a poner un

## 102:50 - 103:05
momentito la pausa voy a poner el reloj 5 minutitos así esto así y pues ahí lo pone 8 8 y 1 así

## 103:05 - 103:44
aparecemos otra vez por aquí ahora ya sé por aquí y ya activado y activó la grabación para que no para

## 103:44 - 103:54
que no se nos olvide haber aprovechado para leer un poquito algunos temas a ver respondiendo por

## 103:54 - 104:01
abajo ahora juan me pregunta que no le queda claro cómo elegir los gráficos 3d para lo iremos viendo

## 104:01 - 104:09
cuando iremos viendo el final un gráfico 3d es una representación de parámetros lo hemos visto en la

## 104:09 - 104:14
teoría excel aquí ya lo habéis visto con multichars ya os lo dije que teníamos viendo todo de distintas

## 104:14 - 104:22
fuentes porque lo que importa son los conceptos no no pensé no queráis aprenderlo todo en un

## 104:22 - 104:30
sistema porque vamos a ver muchos al final es la la idea es una zona estable es la estabilidad

## 104:30 - 104:38
si más no tiene no tiene más que otro otro criterio aquí en mi opinión el procedimiento más correcto

## 104:38 - 104:48
era es decir la opti 1 luego la opti 2 y la opti 3 que finalmente decidimos no aplicar el filtro

## 104:48 - 104:54
os he querido hacer esta última 4 para que la veréis toda junta recuerdo pero es mejor práctica

## 104:54 - 105:04
hacerlo de la de la de la otra manera es mejor práctica hacerla que más pero bueno espera que

## 105:04 - 105:15
lo pongo abro otra vez el mapa por ejemplo por ejemplo hemos visto antes el opti 1 data aquí

## 105:15 - 105:27
vale hemos visto esta en 2d el opti 1 all data vale bueno o tampoco estaría mal hacerla hacerla

## 105:27 - 105:33
después posteriormente como esta que hemos hecho pero por mantener el ritmo a mejor hacer hacer no

## 105:33 - 105:41
estaría mal hacer la la 4 pero ya un poquito más cerrada de acuerdo es decir no no dejando si

## 105:41 - 105:46
hemos visto que los valores tan bajos de traily pues no nos convencen pues ya los podíamos

## 105:46 - 105:53
oscupir ya de cara a hacer una elección pues elegir pero pero haríamos más cosas como las

## 105:53 - 106:01
que vamos a hacer ahora en maestro pero definitiva definitiva no es más que un equilibrio recuerdo

## 106:01 - 106:12
un equilibrio entre el rendimiento el riesgo por por distintos por distintas métricas pues

## 106:12 - 106:19
el reto no puede ser en drama puede ser echar puede ser el sortino vale que como digo lo iremos

## 106:19 - 106:26
viendo a lo largo del curso y eso lo puedes hacer tú aquí lo puedes hacer a través de

## 106:27 - 106:35
el recovery excel de acuerdo como lo vimos en el curso varias veces de acuerdo haciendo

## 106:35 - 106:42
una tabla dinámica si os acordáis vale yo estoy aquí puedo hacer una tabla dinámica y de hecho

## 106:42 - 106:51
además tengo normalmente me lo hace automático que ya la excel es bastante listo a ver aquí

## 106:51 - 106:59
tabla dinámica recomendada con gráfico ahora está había una que me decía gráfico y tabla

## 107:00 - 107:10
a uno ya me la selecciona hecho recovery y aquí le puedo elegir

## 107:11 - 107:24
la verdad voy a poner recovery las dos variables y recovery vale no este lo pongo aquí recordar

## 107:24 - 107:31
que lo hicimos en la teoría lo hicimos en la teoría pasa que aquí pues bueno es lo que

## 107:31 - 107:41
digo al final tengo este cual es la 41 final sólo tengo estas dos variables una contra la otra

## 107:41 - 107:52
si metiera también el filtro entonces ya la cosa pues sería distinto pero hay varias maneras

## 107:52 - 108:27
de hacerlo pero en definitiva me he quedado así un momentito por defecto aquí de superficie y

## 108:27 - 108:39
hasta esto pero voy a vamos a poner un diseño que nos guste más y hemos hecho el mapa en un

## 108:39 - 108:54
momentito en excel aquí es igual lo voy a quitar esto y bueno pues aquí en el excel pues también

## 108:54 - 109:01
ahora yo puedo jugar un poco con ella y la puedo ir pues moviendo puedo ir aquí a la opción 3d

## 109:01 - 109:19
puedo pues hacer alguna cosita con ello esto repito que lo vimos lo vimos en la teoría bueno

## 109:19 - 109:25
poder un poquito lógicamente tengo poquito menos de margen de maniobra que multicharts que ya está

## 109:25 - 109:30
más pensado para eso pero pero es un poco la misma la misma idea es un poco la misma idea que

## 109:30 - 109:39
lo estamos viendo por recovery final esto esto es un poco la idea que la zona si os fijáis por

## 109:39 - 109:47
recovery es pues muy muy estable pero habría que ahora vamos a ver un poquito en multicharts

## 109:47 - 109:57
viendo esto que tenemos aquí alguna alguna combinación antes dejarme que lo deje así puesto

## 110:00 - 110:11
a ver luego comentaba también aquí antonio antonio que que las dudas decía que si las

## 110:11 - 110:16
contesta alberto no las contesto yo si no es exactamente así antonio es exactamente así alberto

## 110:16 - 110:25
contesta las preguntas que tienen que ver que son de rápido responder y que tienen que ver pues

## 110:25 - 110:30
con el seguimiento de la clase bueno para que nos esperemos al final pero ya os explique si

## 110:30 - 110:36
has estado viendo las prácticas directo o posiblemente grabadas que la idea siempre es

## 110:36 - 110:43
dejar una parte al final de la clase también al inicio trato de contestar las que tenéis en el

## 110:43 - 110:54
discord y vamos respondiendo un poco todas las preguntas y al final alberto digamos que las

## 110:54 - 111:02
preguntas que aportan valor a los alumnos que es lo que tú sugieres las las dejamos un poco para

## 111:02 - 111:08
el final cuando cuando las hay también además las podéis poner en discord y también si enviáis

## 111:08 - 111:17
y las trataremos de atender lo que comentas abre el micro era algo que valorábamos pero

## 111:17 - 111:23
que sinceramente creo que al final va a ser creo que puede ser contraproducente pero no por no

## 111:23 - 111:28
por eso porque sois muchos entiendes porque sois muchos pero de todas maneras no descarto al final

## 111:28 - 111:37
puedes ir escribiendo en el chat y nosotros sí consideramos que tu duda aporta como muchas yo

## 111:37 - 111:45
ya las digo que insisto que eso en principio creo que la estructura mejor era y así es como

## 111:45 - 111:49
vamos a intentar mantenerlo que mejor algún día pues se me olvide algo distinto pero la idea lo

## 111:49 - 111:56
expliqué el primer día pasa la clase verás como lo explique así que la última media hora la dejaría

## 111:56 - 112:03
para eso es decir vosotros podéis ir preguntando y aquellas que sean de contenido que creo que

## 112:03 - 112:09
pueden aportar valor para todos al final las respondemos las que alberto tiene que

## 112:09 - 112:12
responder porque si tú me preguntas oye es que no he entendido que ha dicho no sé qué o qué

## 112:12 - 112:19
el gráfico que colores no sé cuánto o algo que afecta o es que no se ve bien o no se oye lo sé

## 112:19 - 112:24
cualquier cosa que afecte al funcionamiento de la clase en ese momento pues pues él ya trata de

## 112:24 - 112:32
resolverlo incluso me lo dice a mí o solo responde él pero las preguntas que pueden ser de cierto

## 112:32 - 112:38
contenido mi idea es plantearlas así pero si creo como este caso ahora afectan a la continuidad

## 112:38 - 112:45
de la clase pues prefiero resolverlas in situ pero si hay muchas pues prefiero dejarlo para el final

## 112:45 - 112:53
porque si no no avanzamos sin más más de acuerdo no es no es base de todas maneras si en algún

## 112:53 - 112:58
momento consideramos que es bueno abrir pues a lo mejor hacemos una clase y se mira está vamos

## 112:58 - 113:05
a dedicarla a eso vale si se acumula todo con el plan y ya ya habíamos contemplado si vamos

## 113:05 - 113:10
viendo que se acumulan muchas preguntas que hay algún grupo que nos va siguiendo pues bueno en

## 113:10 - 113:18
un momento dado decir oye clases solo de preguntas de clases solo de preguntas y lo haremos y si yo

## 113:18 - 113:24
un día tengo si 23 preguntas en el disco pues lo haré en este momento hay pocas preguntas en el

## 113:24 - 113:29
disco para Antonio hay para Antonio Antonio si cuando me llenes el disco de preguntas

## 113:29 - 113:40
tengo la clase dedicada pero pero es eso al final hay que hay que hay que ir avanzando y tratar de

## 113:40 - 113:47
que todos podáis preguntar ya te digo que no descartamos si realmente creéis que es necesario

## 113:47 - 113:51
abrir el micro lo hemos pero yo creo que es más productivo y práctico ir avanzando

## 113:52 - 113:59
pero insisto que si es necesario lo haremos si es necesario lo haremos así vale

## 114:01 - 114:10
bueno antes me comentaba lo de los mapas que lo ha comentado un poco para Antonio pero el

## 114:11 - 114:21
quedaros con la idea Antonio si Antonio me preguntaba qué datos elegir de los mapas que

## 114:21 - 114:26
lo había preguntado también Juan Antonio un poco al final que no le quedaba claro cómo elegir en

## 114:26 - 114:34
los gráficos 3d es lo que os decía ahora no no no nos quedemos ahora con elegir exacto aparte

## 114:34 - 114:42
que ahora voy a ir a multicharles vamos a coger más más información más información en el mapa en

## 114:42 - 114:48
el mapa hay veces que nos servirá muy bien para elegir y hay veces que nos servirá poco para

## 114:48 - 114:54
elegir pues la zona pero por dónde van los tiros y luego yo como ya os he dicho puedo acabar elegir

## 114:54 - 115:03
en el excel excel o multicharles en otra herramienta me puede servir un poco para ver la zona elegir

## 115:03 - 115:11
el valor exacto a veces no me resultará evidente hay veces que sí veces que sí el mapa es una

## 115:11 - 115:18
excelente herramienta de sensibilidad de parámetros decir para ver por dónde van los tiros por dónde

## 115:18 - 115:27
van los tiros pero no es sota sota caballo y rey sota caballo rey la elección final por daros

## 115:27 - 115:38
cuando vimos cuando vimos las clases en la teoría que teníamos una excel que hacíamos trabajando

## 115:38 - 115:46
en sample el sample el old data por un equilibrio de datos y demás esto al final nosotros nosotros

## 115:46 - 115:52
esto final ahora y ahí voy ahora y lo acabaríamos de afinar en maestro porque porque a mí la

## 115:52 - 115:58
información que me da multicharles es fantástico porque va muy rápido optimizando es fantástico

## 115:58 - 116:06
porque tiene los mapas pero los datos que me da del portfolio son son pocos entonces como eso

## 116:06 - 116:13
maestro me da más pues por eso acabó más es lo que os decía antes y ahí voy ahí voy ahora pero

## 116:13 - 116:19
como no me dejáis avanzar pues que no pasa nada que no pasa nada que es broma me podéis preguntar lo

## 116:19 - 116:25
lo que queráis que para eso estamos ya os dije que no que no acabaremos hasta que no acabemos

## 116:25 - 116:33
el temario que yo quiero hacer así que no hay problema vale venga vamos ahora a abrir maestro

## 116:33 - 116:43
y lo que no sabe de la de antes y toco una pregunta para luego de no hay ninguna para luego apuntada

## 116:43 - 116:47
ya no veo nada rojo o sea en principio está todo el día de preguntas no hay preguntas para luego

## 116:47 - 116:56
bueno repásate ahí las preguntas si ves alguna de esto me la marcas en rojo para que luego ya la

## 116:56 - 117:05
procese así vale no hay nada para entonces más o menos vamos a lo digo para si me guardo tiempo

## 117:05 - 117:13
para luego no estamos al día de preguntas es si si preguntáis más ahora luego luego al final los

## 117:13 - 117:22
últimos 20 minutos dependerás que haya pues os dejo más rato o menos entonces tenemos aquí el

## 117:22 - 117:45
sistema de ruptura que para levantar la mano para ahora ahora y escribirán aquí tengo el

## 117:46 - 118:51
vamos a ver o configurado todo igual ya vamos a hacer de momento un 602 con 100 mil vamos a

## 118:51 - 119:04
hacer hasta el viernes pero se lo habéis pasado 20 años vamos a hacer un par o tres de portfolios

## 119:04 - 119:30
rápidamente con esta información que teníamos a ver dónde tengo el excel pero esto no por

## 119:30 - 119:38
un lado tengo este y por otro lado tengo el excel que ahora no sé lo he cerrado el excel

## 119:39 - 120:03
este es por aquí por recovery era en el filtro vamos a hacer una cosa vamos a desactivarlo

## 120:03 - 120:14
de momento vamos a ir sin filtro que es verdad que por recovery y lo vamos a hacer primero uno con

## 120:14 - 120:44
el primero que teníamos que era 6 0 20 0 0 0 0 0 20 está todo bloqueado vale vamos a ir con

## 120:46 - 121:09
2% a cada acción y eso no sí nos va a tardar un poco nos va a tardar un poquito ese problema

## 121:09 - 121:16
que tiene maestro es que esto la verdad que es un problema realmente potente pero que

## 121:16 - 121:22
teóricamente se ha quedado muy atrás y a nivel de procesamiento de información es súper lento es

## 121:22 - 121:29
súper lento otro día también trataremos de enseñarnos algo con con cual analyzer que es

## 121:29 - 122:27
un poquito más rápido 100 vamos a ver que lo tengo configurado todo igual ya vamos a hacer de

## 122:27 - 122:56
momento un 6 0 2 con 100 mil vamos a hacer hasta el viernes pero se lo habéis pasado 20 años

## 122:56 - 123:09
vamos a hacer un par o tres de portfolios rápidamente con esta información que teníamos

## 123:09 - 123:32
aquí a ver dónde tengo el excel pero esto no por un lado tengo este y por otro lado tengo el excel

## 123:32 - 123:57
que no sé lo he cerrado el excel este es por aquí por recovery

## 123:58 - 124:04
en el filtro vamos a hacer una cosa vamos a desactivarlo de momento vamos a ir sin filtro

## 124:04 - 124:15
que es verdad que por recovery y lo vamos a hacer primero uno con el primero que teníamos que era 6

## 124:15 - 124:55
0 20 0 0 0 0 0 20 está todo bloqueado vale vamos a ir con 2% a cada acción que son así nos va a

## 124:55 - 125:10
tardar un poco nos va a tardar un poquito ese problema que tiene maestro es que esto la verdad

## 125:10 - 125:17
que es un problema realmente potente pero que teóricamente se ha quedado muy atrás y a nivel

## 125:17 - 125:25
de procesamiento de información es súper lento es súper lento otro día también trataremos de

## 125:25 - 125:44
enseñarnos algo con con cual analyzer que es un poquito más rápido bien lo bueno que tenemos

## 125:44 - 125:54
aquí es podemos mirar mucho más por ejemplo la exposición que hemos ido teniendo 150 en algún

## 125:54 - 126:52
momento pero algo tengo en el mone management mal voy a usar el de voy a usar el de el de maestro

## 126:53 - 127:05
voy a usar el de maestro voy a usar el de maestro por fix x fractional a market value que para

## 127:05 - 127:53
acciones no muy bien el dito que no se explicó el 0 0 20 que lo dejo ahora no lo toco vamos a

## 127:53 - 128:04
probar la cartera 6 0 20 0 que es la que habíamos elegido inicialmente para ir avanzando en las

## 128:05 - 128:16
validaciones pero que la verdad que no tengo claro que se la mejor ahora lo veremos combinado con los

## 128:16 - 128:56
mapas ahora está mucho más después ahora ha ido creciendo un poco bueno hemos ido a 1 y medio hasta

## 128:56 - 129:21
dos veces de exposición 2 mil 943 3 147 aquí una de las cosas interesantes que podemos ver es esto

## 129:22 - 129:35
es esto que realmente hay muchas acciones que al final es 6 20 de acuerdo nos quedamos con

## 129:35 - 129:44
este vamos a comparar 2 3 2 3 por folios distintos con este setup un momento vamos a hacerlos

## 129:44 - 131:11
primero y luego los comparamos pero no vamos a ver vamos a ver qué tal no convergen pues que

## 131:11 - 131:37
es que locura si te ve el 3 a ver está en 18 0 13 a ver el mapa aquí que teníamos antes

## 131:37 - 132:22
vamos a volver a verlo ahora me dice que no me abre el archivo no te creo a ver si vemos lo

## 132:22 - 133:09
mismo aquí que allí 8 0 13 si lo que pasa que la que el recovery siempre se ve muy afectado por

## 133:10 - 133:30
el final te tira muy abajo te tira muy abajo es esta ya ya ya aquí si miras por este este

## 133:30 - 133:34
char que tenemos por eso quería mirar a varias aquí no ahora hemos mirado 6 20 que ya la tenemos

## 133:34 - 133:43
guardada vale que si la miramos tanto aquí tanto aquí como como en el excel no dan mal

## 133:43 - 134:16
sería por aquí vamos a usar el foco el lápiz 6 20 sería más o menos por aquí ya no sé

## 134:16 - 134:51
estoy buscando la manera que lo vea mejor aquí más o menos aquí 6 20 es más o menos vale más o menos

## 134:52 - 135:13
esta tenemos pero si miramos el excel puramente por datos por recovery realmente le gusta mucho

## 135:13 - 135:20
más aquí pero ahí vemos que tanto por estar como por retorno de grado muy rápido quien gana y el

## 135:20 - 135:26
drama pasa que el drama en la teoría lo hablamos bastante todos los ratios que tienen el drawdown

## 135:26 - 135:36
el denominador al final el que dirige el ratio es el drama porque como hace de divisor vale

## 135:36 - 135:47
tira muchísimo de la tira muchísimo del ratio para él vale y acaba viéndose muy afectado el

## 135:47 - 135:55
tsi lo trata de corregir añadiendo los winners al numerador vale que eso hace que los sistemas

## 135:55 - 136:04
que aciertan más que aciertan más pues suban un poco en el ratio es verdad que aquí vamos

## 136:04 - 136:09
para el próximo día me gustaría ver en este en esta cartera que nos da sortino para para todo

## 136:09 - 136:20
el rato porque ahí ahí es donde realmente tenemos un buen equilibrio vale un buen equilibrio vamos

## 136:20 - 136:28
a ver si sí para para el próximo día casi con total seguridad que lo que lo tendremos porque

## 136:28 - 136:34
hemos visto el problema que tiene el que tienen ellos preinstalado y lo vamos a corregir y trataremos

## 136:34 - 136:51
de traerlo pero con esa información realmente en este mapa para eso decía que no siempre vas

## 136:51 - 136:58
a poder elegir es complicado elegir porque realmente es casi da igual no bueno casi da

## 136:58 - 137:04
igual me refiero en toda esta zona en toda esta planicia vale si luego y ahí ya te fijas el

## 137:04 - 137:13
retorno es donde ya te vas para arriba no se te empieza pero lo tengo activado pero pocas

## 137:13 - 137:20
diferencias se te empieza a ir más para arriba es donde decíamos que interesaba más el ratio

## 137:20 - 137:30
un poco más abajo no perdón el el trailing el porcentaje de trailing más más a 0 25 porque

## 137:30 - 137:35
en el 0 20 incluso estaba estaba justo pero bueno el 0 20 al final acaba ha sido un poco un equilibrio

## 137:35 - 137:43
entre lo que quieren los ratios de de drawdown lo que quieren los ratios de de retorno riesgo

## 137:43 - 137:52
porque al tener el drawdown el denominador tira mucho de él y el profit el profit quiere un muy

## 137:52 - 138:05
elevado si ordenamos sólo por profit vale fijaros un poco más grande todo el rato 0 28 0 27 0 30

## 138:05 - 138:17
he bloqueado que no haya filtro vale que no haya si en cambio ordeno por drawdown lo contrario 0 7

## 138:17 - 138:25
0 8 0 7 0 6 de acuerdo lo más bajo si ordenamos recovery busca el término medio vale pero el

## 138:25 - 138:31
drawdown tira mucho de por eso al final este shark aunque es un poco como os he dicho antes

## 138:31 - 138:40
falso por por el por demás y ahí cambia es verdad que también da los saltos por retorno pero hay poca

## 138:40 - 138:48
diferencia de esos valores están todo el rato alrededor del 0 todos estos es lo mismo

## 138:48 - 138:58
es prácticamente lo mismo todo esto hay muy muy poca variación de acuerdo de mi poca variación en

## 138:58 - 139:07
el dato de 6 p6 y 10 pero también bastante elevado el tréil bastante elevado el tréil y pero ya

## 139:07 - 139:13
digo con muy poca con muy poca variación pues al final nos hemos quedado con un compromiso pero

## 139:13 - 139:21
vamos a ver vamos a hacer rápidamente porque es un buen ejercicio hemos hemos hecho este del 6 20

## 139:21 - 139:32
y ahora vamos a ver todos estos incluso voy a voy a quitar el este límite vamos a ver por

## 139:32 - 139:43
ejemplo el que mejor retorno da vale que es que no tengo ordenado al revés pero es el canal primero

## 139:43 - 139:55
vale sería 6 0 27 1 vale lo voy a poner que es bastante parecido al que voy a dejar la gestión

## 139:55 - 140:05
monetaria igual para no tocar nada vamos a hacer 6 0 27 1 me lo punto ahí para tener claro luego

## 140:05 - 140:15
cuál es cuál es cuál 6 por de hecho el filtro podría poner si voy a poner así porque así me aclaro

## 140:15 - 140:36
más y sería mejor 6 1 0 27 venga 6 1 0 27 0 27 dejamos toda la gestión monetaria como hemos

## 140:36 - 140:45
hecho el otro para poderlos comparar espero que vuelva a cruz ahí va vale es seguramente se hace

## 140:45 - 140:51
vamos a ver el que menor dada obtiene que es muy es muy raro ya os lo digo pero vamos a verlo

## 140:51 - 141:12
vale sería por canal en ese caso 25 ahora viene el filtro y luego el tréil 0 0 7 vale el que mejor

## 141:13 - 142:08
tiene que es 4 0 24 4 1 0 24 luego los comparamos hoy ahora voy ahora voy ahora voy fran de

## 142:08 - 142:42
contexto a ver este el de net ya lo he hecho no 25 1 0 0 7 25 1 0 0 7 de la segunda fran

## 142:42 - 143:22
que me los acabo de apuntar este recobrimos que damos con uno de la este pero 0 12 aunque

## 143:22 - 143:27
en estar de luego haremos una pasión de dios estaré hecha una es que de hecho lo intentamos

## 143:27 - 143:34
hacer pero maestro entre los problemas que tiene lo que os decía es de optimizando aparte de la

## 143:34 - 143:40
velocidad es que como tarda tanto tiene un problema con gélito que ha tenido mil protestas y mil

## 143:40 - 143:50
demandas que es que exige que esté eslogado mientras hace todo el test y como es extremadamente

## 143:50 - 143:55
lento y lo tú lo dejas un fin de semana los fines de semana muchas veces hacen mantenimiento y al

## 143:55 - 144:02
final muchas veces se tras cuelga entonces es un problema bastante serio porque al final hay

## 144:02 - 144:07
veces que para conseguir acabar una optimización más allá que pueda durar dos días que ya es

## 144:07 - 144:15
un problema lo difícil es que en dos días no se cuelgue y el tiempo real se cuelgue lo que sea y

## 144:15 - 144:23
entonces lo pierde es bastante es increíble como tecnológicamente los problemas que tiene a este

## 144:23 - 144:29
nivel porque hace muchos tiempos mucho tiempo que tiene evoluciones pendientes y el programa

## 144:29 - 144:35
en sí no es que sea malo pero se ha quedado completamente desfasado es actualizado y como

## 144:35 - 144:38
no lo revisan en ese sentido pues claro la tecnología va avanzando los procesadores

## 144:38 - 144:43
van avanzando y él no alta y está ahí un poquito limitado espérate que ya no sé cuál he hecho

## 144:43 - 144:59
cuál no he hecho a ver 25 107 hecho no vale este lo he hecho 6 27 0 1 luego lo revisaré que estén

## 144:59 - 145:28
que estén bien pero ahora voy a hacer el siguiente 4 1 0 24 4 pero 24 aquí lo normal lo que pasa es

## 145:28 - 145:39
lo que os digo esta optimización de 3 de porfolio trader tiene tiene ese problema da pocos datos

## 145:39 - 145:43
entonces los tienes que construir tú el problema es lo que os digo que al ver este problema con

## 145:43 - 145:48
char no hemos podido utilizar el sortino que usamos para las estrategias sueltas entonces hay

## 145:48 - 145:54
que hacerlo para por folio porque pensamos que valía pero hemos visto que no entonces hay que

## 145:54 - 146:00
hacer el sortino para por folio y a veces lo que hemos hecho es hacer varias es decir hacer una

## 146:00 - 146:07
lo bueno es que modificar es muy rápido y como el coste fitness al costo fitness es una fórmula

## 146:07 - 146:14
que tú puedes programar al final le puedes meter varios pasadas recoges varios uno pues le ponen

## 146:14 - 146:21
sortino sharp y el que quieras los pasas todos al excel y entonces ahí es donde ya tienes tú para

## 146:21 - 146:27
hacer distintos cálculos o ratios que puedas calcular directamente en el ex de momento sólo

## 146:27 - 146:32
puedo calcular el recovery utilizar este sharp que insisto que no es el valor correcto pero sí

## 146:32 - 146:39
que es extrapolable a para hacerla para hacer la selección para este era el 4 ya sólo me queda

## 146:39 - 146:56
uno más raro y ahora podremos comparar datos entre ellos vale 1 0 0 se lee bien el maestro

## 146:56 - 147:09
la pantalla ahora ahora ahora no me siguen por cierre pero esto es instrumental y no

## 147:09 - 147:14
no merece mucho la pena pararse mucho en explicaros todo esto es al final simplemente estoy haciendo

## 147:14 - 147:21
todo el porfolio con unos ex concretos trataré de dejarlo mañana a ver si me acaba porque

## 147:21 - 147:26
ese fin de semana he intentado dos veces que maestro me hiciera toda la optimización completa

## 147:26 - 147:31
pero esta optimización que hemos hecho multicharts también se puede hacer pero en multicharts he

## 147:31 - 147:41
tardado unos en hacer la larga de esto tardado unos 15 minutos y maestro se ha colgado después

## 147:41 - 147:48
de llevar cada una de ellas como 20 pico horas y no había acabado esta es la relación y era

## 147:48 - 147:56
lo mismo en verdad era lo mismo mismo código todo igual y esa esa es un poco la comparación

## 147:56 - 148:02
no entonces que ya os lo había comentado alguna vez es un drama de maestro pues es la

## 148:02 - 148:08
sola que es que ya digo es súper potente luego a nivel de informes es brutal ahora

## 148:08 - 148:13
ahora veréis todos los datos que nos saca está fantástico y los hemos revisado bueno

## 148:13 - 148:22
hay uno por ejemplo que no está bien ya lo pasamos pero pero esto sí que sí que están bien y bueno

## 148:22 - 148:41
pues es la lástima comentaba fran comentaba fran que la selección del filtro volatilidad

## 148:41 - 148:49
lo hecho entre 0 y 1 pero que 1 4 tenía mejor que decir estaba una zona robusta de estar sería

## 148:49 - 149:03
mejor pues sí pero ahí a mí me parece podríamos podríamos trabajarlo un poco un poco

## 149:03 - 149:11
más pero me parece sobre optimizarlo me parece demasiado los filtros a mí de norma me cuesta

## 149:11 - 149:16
meter filtros y a este tendencial para la ganancia que he visto ya ya comentado creo que no se lo

## 149:16 - 149:24
metería no se lo metería pero encima si lo metes tiene que ser o no optimizado o muy poco

## 149:24 - 149:30
sabes es decir esa el filtro es la manera de sobre utilizar más porque es cuando tú ya tienes

## 149:30 - 149:36
tu sistema vamos a suponer 6 0 20 es vale venga y ahora le meto un filtro que me va a eliminar

## 149:36 - 149:45
los malos o sea eso he dicho así no te suena a una cosa fácil de sobre optimizar porque al

## 149:45 - 149:51
final le vas a quitar los cientos tres cientos o cientos igual sabes que está muy bien no quitar

## 149:51 - 149:59
la parte mala pero pero el problema es que estás aumentando el riesgo de que de que de que sea una

## 149:59 - 150:04
sobre optimización aunque en el mapa parece robusto aunque en el mapa parece robusto que

## 150:04 - 150:12
entiendo lo que dices y tienes sentido no te digo que no pero le daría más vueltas porque le daría

## 150:12 - 150:20
más vueltas y ya digo granular lo tanto explico es como el filtro no 0 20 ya te digo yo lo sé

## 150:20 - 150:27
optimizado los todos en 0 25 porque porque vierais el mapa bien granulado pero realmente

## 150:27 - 150:35
tampoco me gusta es decir en un sistema en diario con mil y pico trades de verdad prefiero ir de 0 0 5

## 150:35 - 150:43
en 0 0 5 sabes es decir ir a buscar tanto el detalle explico 0 21 0 22 0 23

## 150:46 - 150:51
explicó es decir al final recuerda que lo que estás viendo es lo que ha ido mejor en el pasado

## 150:51 - 151:00
entonces ya te digo al final elegir siempre el mejor el que y esa ya te digo el tema del

## 151:00 - 151:09
incremento es una cosa que es quizá la que más tiene su canal una media esto es muy evidente porque

## 151:09 - 151:16
va de uno en uno vale que sí que no hay mucha historia pero cuando tienes fitos cosas así que

## 151:16 - 151:25
tú puedes hacer 0,1 0,2 pero si por puestos ya podríamos hacer 0 0 1 0 0 2 0 0 3 y por qué

## 151:25 - 151:38
no 0,0 0 0 1 0,0 0 0 2 sabes me entiendes hay que hay que cortarlo sí sí ya sé ya sé que tenía

## 151:38 - 151:45
muchos ya sé que tenía muchos muchos años pero sí sí ya sé que tenía muchos pero el filtro

## 151:45 - 151:52
otro no tenía tantos o sea de cambiar el filtro cada 300 o sea has cambiado 300 o sea eso el

## 151:52 - 151:59
sistema tiene los 400 con el filtro en 0 o el filtro en 1 y de 0 a 1 cambia 300 y de 1 a 4

## 151:59 - 152:05
igual cambiaba 200 ahora lo miramos lo miramos lo miramos porque este sí este es el que tengo

## 152:05 - 152:12
con todos no sí es el que tengo con todos aquí de tener uno a bueno no en ese no lo he hecho es

## 152:12 - 152:29
en el 3 en la opti 3 aquí no aquí te he dado todo el rato sólo sólo el filtro es que fíjate

## 152:29 - 152:36
aquí llevaba la extrema operaciones aquí tenías en 1 o 4 lo que tú dices que te ha gustado es este

## 152:36 - 152:46
como en verde vale este a ti te ha gustado porque bueno te ha dado un recovery bastante más elevado

## 152:47 - 152:57
mejorado ha mejorado sobre todo porque tienes ahí 1 430 este sí que te ha bajado pero de éste a

## 152:57 - 153:06
éste que tienes 103 de diferencia entre ellos o sea poner ese filtro o no ponerlo son 103 de

## 153:06 - 153:19
diferencia y gana un poquito más y baja el verdadero dices o sea está muy bien bueno sí claro si de

## 153:19 - 153:26
aquí cinco años eso se mantiene es verdad ahora eso es seguro que se mantendrá no la realidad es

## 153:26 - 153:31
que eso no es seguro no es seguro que el cero pues decir bueno ya pero el cero le he quitado

## 153:31 - 153:35
un grado de libertad no estamos de acuerdo al final no no he añadido variabilidad a la que yo

## 153:35 - 153:41
meto esto estoy metiendo una tr o sea se metió en una condición más al sistema porque esta

## 153:41 - 153:50
no trabaja soy ignorando el atr yo aquí le estoy ya asumiendo que cuando el atr de un día con el

## 153:50 - 153:56
atr de un mes por multiplicado por una 4 sea mayor no pere y de esa manera le he quitado

## 153:56 - 154:05
siempre que es un 3 por acción de media 3 por acción entonces no no no es una certeza fran es

## 154:05 - 154:11
que esto va así o sea no no no es una certeza o sea no es no es que yo te diga esto seguro que

## 154:11 - 154:17
luego no irá no no para nada no te lo puedo decir no sería serio decirte eso no lo sé seguro pero

## 154:17 - 154:23
estoy añadiendo un grado de certidumbre más para el beneficio que me da no me renta me explico es

## 154:23 - 154:31
decir para el beneficio que me dan no me renta a mí no me parece suficiente para yo para añadir

## 154:31 - 154:40
grados de libertad para añadir posibilidades al sistema de oscilar de que siempre que añades

## 154:40 - 154:46
como mínimo ya ves una y a veces son varias porque es la condición o sea es el valor de

## 154:46 - 154:57
la tierra y que la tierra de hoy sea menor que la tierra mensual esos más o menos son dos para

## 154:57 - 155:04
añadir de dos necesito necesito que me convenza mucho pero de todas maneras lo estudiaría más

## 155:04 - 155:09
decir miraría esto miraría esto en el gráfico muchas acciones y la otra cosa que ahora no hemos

## 155:09 - 155:15
hecho esas que ahora lo vamos a hacer el maestro un poco y un poco pero también lo miraría gráfico

## 155:15 - 155:22
nosotros miramos mucho pero miramos mucho ahora esto lo miraría el gráfico en distintas acciones

## 155:22 - 155:28
miraría el gráfico ya lo haremos ya lo haremos aunque no lo hagamos hoy lo haré porque a esto

## 155:28 - 155:35
tengo que volver para necesito ver un sortino ahí para ser más cómodo tienes entonces necesito verlo

## 155:35 - 155:49
lo veré pero el filtro no es no es no es ni concluyente ni granulandolo en 1.4 si el filtro

## 155:49 - 155:53
es jose donett sigo sigo las preguntas porque ya estamos en hora de preguntas y hay que ir

## 155:53 - 156:01
contestando comenta en esta línea jose que si el filtro quitar a 503 sería más válida entiendo

## 156:01 - 156:09
si sería más válido si si sería más válido sería más válido en este en el caso de los filtros

## 156:09 - 156:17
es un poco es un poco al revés y por eso es como lo diría no es que sea contra el tuitivo es contra

## 156:17 - 156:23
el tuitivo para lo que he explicado me está diciendo siempre contra más tres mejor vale

## 156:23 - 156:29
pero ahora me dices que si el filtro quita más es mejor y que quedamos bueno las dos cosas son

## 156:29 - 156:35
verdad las dos cosas son verdad quiere decir que para que el filtro me quite tengo que tener

## 156:35 - 156:44
muchos antes si no ya no me vales es decir si tengo mil ya no filtró me entiendes ya no filtró

## 156:44 - 156:51
ya no ya no estoy suficientemente cómodo para que eso baje más me explicó entonces pero

## 156:51 - 156:58
evidentemente el filtro valida el filtro valida quitando el filtro valida actuando las reglas

## 156:58 - 157:08
para evaluarlas tiene que tienen que implicar cambios si no si no implica cambios no está

## 157:08 - 157:15
validada y la significación pasa por ahí vale porque cada regla tenga un número de tres donde

## 157:15 - 157:21
actúen y en distintos momentos distintas condiciones de mercado etcétera significación y

## 157:21 - 157:27
representatividad significación y representatividad significación la verdad las estadísticas

## 157:27 - 157:36
representatividad la de actuar en distintos mercados vale por eso que ahora lo hemos metido 20 a esto

## 157:36 - 157:44
para ver esta curva en 20 bien aquí tenemos un resumen vale de entrada aquí ratios que no valen

## 157:44 - 157:49
para nada el esto que veis aquí si lo veis es el total retorno partido por máxima darolón aquí no

## 157:49 - 157:59
vale para nada aquí no vale para nada porque bueno vale bueno habiendo hecho que su manera

## 157:59 - 158:06
vale un poco pero para regular regular porque al final es lo que os decía antes es decir el

## 158:06 - 158:12
drawdown no lo puedo meter en porcentaje que es verdad que aquí como yo he regulado en 100

## 158:12 - 158:17
acciones y vengo con gestión monetaria que es muy importante muy importante porque porque es muy

## 158:17 - 158:24
importante porque si venís aquí a ver la lista de trades pues yo al final he ido exponiendo si tú

## 158:24 - 158:34
multiplicas por ejemplo de igual esta acción hemos comprado 60 por 33.14 al final he comprado

## 158:34 - 158:41
1988 dólares que es más o menos el 2% que habíamos hablado al inicio 2000 dólares vale entonces

## 158:41 - 158:49
si yo siempre he ido exponiendo esa misma cantidad pues es mejor sería mejor el porcentaje sí pero

## 158:49 - 158:54
como yo siempre voy exponiendo bueno un 2% de la cuenta ya estoy haciendo porcentaje porque ahora

## 158:54 - 159:02
tengo 100.000 2% pero cuando tenga 200.000 pues será el doble pues ya voy exponiendo siempre una

## 159:02 - 159:10
cantidad que depende del porcentaje gracias a ese 2% 2% entonces las cantidades están más o menos

## 159:10 - 159:14
ecualizadas pero como lo mismo que se ha hecho en el excel os he dicho no está mal recovery sirve

## 159:14 - 159:23
pero sería mejor aún en porcentaje sería mejor vale pero aquí como ya tenemos esa tenemos el

## 159:23 - 159:30
recalculado tenemos algunos datos más que nos sirve tenemos el tráiler real aquí muy elevado

## 159:30 - 159:40
porque porque hemos metido la exposición a casi el 200 hemos metido un poco un poco elevado a la

## 159:40 - 159:49
exposición pero aquí sí que tenemos el triple r a 0 34 aquí tenemos a 0 92 carros como cambia

## 159:50 - 160:07
0 0 0 6 y 1 0 6 aquí el que los cambios son bestiales el uno es saber cuál era este 6 1 0 27

## 160:07 - 160:16
ese era el primero bueno el que era por net profit era por net profit al final equilibra

## 160:16 - 160:30
bastante curiosa ver a los cero de la onda de 60 la otra tenía un 70 70 y pico como está muy

## 160:30 - 160:37
expuesto sí sí sí está muy expuesto está muy expuesto fíjate estamos componiendo 25 29 por ciento

## 160:37 - 160:48
y aquí que he hecho 0 88 que hay un fallo y aquí me he equivocado que he pasado con este 25 1 0 27

## 160:48 - 161:14
0 0 7 y porque ahora tampoco tengo que haber hecho algo mal no ves que no vale nada te va

## 161:14 - 161:47
a haber configurado algo mal los clothes falls trailing 0 0 7 no bueno esperate esperate esperate

## 161:47 - 161:56
esperate que este era el día de la hora no está bien es que se no no hace nada vez era

## 161:56 - 162:07
un poco solo se tiene muy poco straights diría muy poco straights no era de aquí era de aquí

## 162:07 - 162:30
sí sí claro grabo muy poco no se ha ganado muy poco el de era el de máximo el de máximo

## 162:31 - 162:44
era el de máximo era el de máximo era bueno aquí por mirarlo rápido en el sumario fijaros

## 162:44 - 162:53
simplemente profit factor aquí tenemos 39 aquí tenemos 59 73 147 porque tanto por profit factor

## 162:53 - 163:07
como por r incluso que por sharp aunque más parecido es el 6 0 el 6 1 0 27 actuando el filtro

## 163:07 - 163:16
que se quedaba más más profit que hemos estado impuestos aquí todos 6 6 1 0 27 correcto y este

## 163:16 - 163:29
era el de antes 6 0 6 0 0 20 ser 1 43 tan notablemente notablemente alejado notablemente

## 163:29 - 163:37
alejado bueno vamos a ver vamos a ver el siguiente día si podemos sacar el sortino vía por folio

## 163:37 - 163:46
porque no está no está sacado no está no está sacado y sacar el sharp bien vía via cartera aquí

## 163:46 - 163:51
ya os sale ya ya tenemos positivo y es otra cosa porque se está calculado bien se ha calculado bien

## 163:51 - 164:02
y tiene mejor mejor ya veis que sé que hay algún dato negativo pero este quedaba cancelar aquí lo

## 164:02 - 164:09
que pasa que realmente la exposición es un poco elevada teníamos que haberla regulado más hemos

## 164:09 - 164:15
llegado a exponernos al al al 200 pero dos veces nos ha apalancado hasta dos veces

## 164:15 - 164:23
claro tenemos niveles de trowdown muy jeves a nivel de por folio tenemos trowdowns de aquí del 60

## 164:23 - 164:35
aquí del 60 aquí del 30 para ver si aquí tiene menos trowdown aquí del 60 y será el 79 bastante

## 164:35 - 164:55
bastante elevado bueno este tipo de que recordar que no está no estamos evaluando el por folio

## 164:55 - 165:02
para operarlo así es lo que os comentaba estamos evaluando la idea por evaluando la idea y luego

## 165:02 - 165:09
ya decidiríamos cómo lo operábamos aquí tenemos muchas acciones en negativo lógicamente luego

## 165:09 - 165:17
una vez el sistema está validado yo luego lo operaré a lo mejor no necesariamente las 10 mejores

## 165:17 - 165:24
pero así que serán de las mejores de acuerdo es decir al final yo valido la idea en las 100

## 165:24 - 165:29
acciones porque eso me da mayor robustez digamos que la idea la pongo más a prueba en acciones

## 165:29 - 165:39
incluso no han ganado vale y esto lo que os decía o sea esto también incluso aquí incluso en

## 165:39 - 165:49
el por folio trader que no es tan no me dará tanta información pero este mismo mirar para que veáis

## 165:49 - 165:57
la comparación que es interesante de ver pero pongo aquí este que nos ha dado aquí mejor podríamos

## 165:57 - 166:10
decir que era 6 1 0 27 lo podemos ver aquí 6 1 0 27 para nosotros a 0 esto va a 0 esto va a 0 27

## 166:10 - 166:30
y ahora se le hacemos backtest y aquí ya veréis que cambia mucho la cosa aquí también tenemos

## 166:30 - 166:38
un montón de datos esto cambia mucho hasta hasta más que allí es que lo hemos puesto bien 6 0

## 166:38 - 166:47
filtro 1 por nosotros con el 1 a 0 27 0 0 0 a bueno a 100 por ciento está expuesto que no puede ir

## 166:47 - 166:57
así no puede ir así está muy expuesto a tener un drawdown 46 y tengo el money management a mente

## 166:57 - 167:03
por folio 2 por ciento está bien está bien está el 2 por ciento es aquí ya hemos controlado mejor

## 167:03 - 167:09
porque le hemos expuesto hemos controlado la exposición claro también tiene un factor de

## 167:09 - 167:19
146 y ganar 52 mil poco claro todo lo uno depende del otro no uno depende del otro pero aquí por

## 167:19 - 167:26
ejemplo mirar lo que os quería enseñar antes la correlación de los retornos mensuales de acuerdo

## 167:26 - 167:31
de todas las 100 acciones fijaros que hay datos en negativo porque hay acciones que pierden que

## 167:32 - 167:39
pero que siendo todo en el nasdaq 100 claro es que apel con microsoft tiene 0 66 apel con google

## 167:39 - 167:50
0 48 con amazon 0 55 con envidia 0 32 con facebook 0 29 que son acciones directoras de acuerdo están

## 167:50 - 167:56
ordenadas están ordenadas por capitalización vale que es decir que todas las que veis primeras son

## 167:56 - 168:03
acciones super top para elegir y fijaros su nivel de correlación bajar aquí no sé si se llega a

## 168:03 - 168:12
ver bien esperados que os voy a poner el foco lo que sea mejor con el foco es ahí fijaros ahí veis

## 168:12 - 168:23
microsoft mirar la columna para abajo es 0 66 0 67 0 53 0 69 0 56 0 55 0 40 con tesla pero 48

## 168:23 - 168:33
0 36 0 39 0 68 51 es decir es el mismo sistema en el mismo frame vale sus correlaciones mensuales

## 168:33 - 168:42
son relativamente moderadas pero no son 0 809 está bien tiene una diversificación moderada que es

## 168:42 - 168:51
muy mejora lógicamente muy mejor vale entonces aquí fijaros que ya con una exposición más

## 168:51 - 168:59
controlada tenemos datos de retorno poquito más estables es una curva bastante justa bastante

## 168:59 - 169:06
muy muy justo bastante virgen pero es un sistema muy justo pero con este nivel de profit factor

## 169:06 - 169:13
ese nivel de retorno acepta algo de apalancamiento y tiene algo de mejora por por delante lógicamente

## 169:13 - 169:19
tiene mucha mejora por aquí además hemos cargado pocos años espérate que vamos a ver cómo tarda

## 169:19 - 169:32
poco está con la serie vamos a meter desde el 2007 al bienes pasado 2% mira vamos a meter un 3

## 169:32 - 170:06
nos vas a poner un poquito más y veis ya tenemos un sharp calculado bien a 29 45 es decir el sharp

## 170:06 - 170:15
al uno es un sharp bajito es un sistema justo pero bueno poco a poco lo podemos hacer crecer

## 170:15 - 170:21
a uno el sistema de hecho este set simplemente es el de mayor retorno no es el que mejor equilibra

## 170:21 - 170:34
aquí ahora podíamos mirar mirar varios pero y hemos mejorado un poquito ha sufrido bastante

## 170:34 - 170:45
aquí porque es verdad que con este nivel de de ratio del trailing pues le cuesta le cuesta salirse

## 170:45 - 170:55
esto ya os digo habían sets este set tiraba más para el retorno pero teníamos alguno que tiraba

## 170:55 - 171:00
un poco más al equilibrio no aquí podíamos encontrar alguno que mejorara esto a cambio de

## 171:00 - 171:08
mejor un retorno un poco peor es un poco la que hay que fijaros hemos ganado un poco de histórico

## 171:09 - 171:20
como tenemos ratios negativos en varios varias acciones a los ves en facebook perdemos dinero

## 171:20 - 171:27
en google en una de las google también porque al final tienen muy pocas acciones con este nivel

## 171:27 - 171:34
de exposición con este canal y con este ratio realmente opera muy poco cada una de las acciones

## 171:34 - 171:42
de acuerdo pero muy poco por eso al final nos vemos obligados a meter pues un análisis global que al

## 171:42 - 171:50
final nos pueda meter más acciones para que al final nos pueda meter 1.100 trades desde el 2007

## 171:50 - 172:05
desde 2007 nos mete 1.100 trades todavía no dejamos un set elegido porque me gustaría me gustaría

## 172:05 - 172:12
poder ver una optimización en el sarte para el sortino de porfolio que aquí sí que lo veo pero

## 172:12 - 172:18
no lo veo optimizando porque es una cosa bastante extraña por parte de multicharts ahí en los

## 172:18 - 172:26
foros de multicharts están con varios mensajes al respecto es decir que tienes sharp metido

## 172:26 - 172:31
como función tienes sortino metido como fines y que a mí no lo tienes como fines ya por defecto

## 172:31 - 172:37
de optimización es un poco extraño es porque si ya lo tienes metido dentro del programa o sea lo

## 172:37 - 172:42
das ese ratio lo das lo puedes perfectamente usar como ratio de iana porque es un dato que

## 172:42 - 172:49
estás calculando si tú me lo estás calculando y aquí pero curiosamente lo da para el performance

## 172:49 - 172:54
pero no lo da como ratio de iana lo tienes que meter tú por código y el que tienes metido por

## 172:54 - 172:59
sistema nos sirve por lo que os decía tienes que hacer específico de porfolio de acuerdo entonces

## 172:59 - 173:08
tienes ese problema pues es un tanto curioso pero pero así es vale bien para el próximo día vamos

## 173:08 - 173:17
a tomar una decisión una decisión respecto a este sistema tal como está es decir en una configuración

## 173:17 - 173:31
de full tendencia vale de full tendencia a aquel que quiera y que lo tenga los recursos que tengan

## 173:31 - 173:36
software los conocimientos para hacerlo pues si lo quiere también hacer alguna propuesta que es

## 173:36 - 173:42
súper bienvenida como deberes para casa que quiero ir mandando algunos vale la regla de entrada

## 173:42 - 173:51
simplemente es esta no tiene más es decir es cierre por encima del canal que es por cierres

## 173:51 - 173:58
vale por el número de velas y en la apertura de la siguiente vela compra vale sí que para evitar

## 173:58 - 174:02
que comprar acciones negativas hemos hecho porque muchos años puede pasar cierre mayor que cero

## 174:02 - 174:09
eso es con el t1 es el filtro pero si vale cero es true si el filtro vale cero no actúa que no

## 174:09 - 174:15
esté comprado y que haya par filtro estará una regulación que pasa pero que no actúa que al

## 174:15 - 174:20
menos tenga una vela cerrada para que no compren la cierre y la misma vela vuelva a entrar que al

## 174:20 - 174:28
menos haya pasado una vela desde que ha cerrado y esto que el total trecha igual hacer esto para

## 174:28 - 174:35
que abra al principio vale porque si no no compraría al requerir al requerir que sea distinto de largo

## 174:35 - 174:42
no compraría entonces es una conexión que se suele poner para que empiece a operar y ya pero ya

## 174:42 - 174:49
estamos a la regla de entrada es esta no tiene no tiene más luego lo otro es la gestión monetaria y

## 174:49 - 174:57
la regla de salida por trailing esto me comprometo en lo que queda de semana es decir hoy pues antes

## 174:57 - 175:04
del viernes de acuerdo en ya subiros el código el código así como está vale eso subiré en texto

## 175:04 - 175:18
y os subiré un pdf con una con un con el seudo código con el seudo código con el seudo código

## 175:18 - 175:28
y escrito escrito para que ya la podáis tener y jugar en todas estas condiciones el trailing

## 175:28 - 175:37
que actúa es este de aquí si el present el que es mayor que cero vale lo inicializa la variable

## 175:37 - 175:44
y hasta si está largo es el valor máximo entre el máximo menos el máximo por el trailing o el

## 175:44 - 175:49
teléfon que ya tiene calculado porque sólo puede subir un trailing acordar esta es la condición que

## 175:49 - 175:58
lo controla decir máximo menos el máximo por el porcentaje y ese es el precio y hasta ese es el

## 175:58 - 176:05
precio que simplemente con esta condición te aseguras que no puede bajar no es por atr se

## 176:05 - 176:11
podía hacer por atr pero los querido hacer este caso sólo para hacerlo así por antagé super simple

## 176:11 - 176:18
más simple no puede ser super super simple vale y visto aquí por ejemplo en el gráfico de alguno

## 176:18 - 176:31
de ellos para acabar viendo alguno el informe el informe si es el informe bueno lo vemos aquí

## 176:31 - 176:38
en un momento en cualquiera me creo son mismo venga que valoros tenemos postos aquí bueno ese

## 176:38 - 176:46
es el 6 0 20 es el 6 0 20 que estábamos viendo viendo antes creo que ahora estamos viendo 6 con

## 176:46 - 176:56
el filtro en 1 y 0 27 todavía menos pero no menos ya veis claro es un sistema que deja correr deja

## 176:56 - 177:03
correr se ha comprado deja correr el sistema de muy largo plazo por eso la única manera de

## 177:03 - 177:10
evaluarlo es metiéndolo en varias acciones de acuerdo y que cuando el mercado va a entrar

## 177:10 - 177:17
lateral pues sufre sufre mucho porque hay que fijaros acaba entrando otra vez el canal no está

## 177:17 - 177:28
bien ajustado y vuelve a entrar el canal no está no está bien no está bien porque no están 6 están

## 177:28 - 177:37
20 6 es muy rápido entrar muy rápido esta es la diferencia habéis visto que había varios

## 177:37 - 177:43
varias zonas esta esta es la versión súper rápida de entrar habían otras versiones hay

## 177:43 - 177:49
que acabar de hay que acabar de elegir aquel que quiera proponer con el código del sistema

## 177:49 - 177:55
que le daremos y demás alguna que nos lo envíe nos lo puede enviar lo voy a poner el disco lo

## 177:55 - 178:02
puede enviar al email y yo me comprometo a responderle otra cosa que queda pendiente

## 178:03 - 178:10
para el día siguiente vamos a hacer esto acabar de tomar una decisión acabar de tomar una decisión

## 178:10 - 178:26
con nuestro sortino de porfolio decisión de parámetros de esta versión como está que hacemos

## 178:26 - 178:33
con los cortos esto es lo que os quería poner para casa unido con esto aquel que quiera en

## 178:33 - 178:41
este set up en este código que haría con el lado corto si alguien quiere proponer o quiere

## 178:42 - 178:46
trabajarlo o simplemente puede proponerlo bien trabajándolo o bien

## 178:48 - 178:54
o bien filosóficamente podemos hacer las dos cosas me valen las dos cosas aquel que

## 178:54 - 178:59
quiera trabajarlo porque puede hacerlo ya que lo haga el que no quiera trabajarlo porque no es

## 178:59 - 179:06
capaz simplemente que le que lo que lo conceptualice y que diga pues mira yo creo que en los cortos

## 179:06 - 179:13
en esta versión haría esto esto esto y porque en acciones en este mismo set up en acciones que

## 179:13 - 179:21
hacemos con los cortos y luego ya lo que vendría es lo mejor tiene que ver con esto vale es que

## 179:23 - 179:29
que otras variaciones hacemos este comentamos que el don chan es un mecanismo de entrar en

## 179:29 - 179:38
tendencia pero es un mecanismo muy útil para hacer break out entonces esto ahora con lo que

## 179:38 - 179:48
tiene ya en el código se puede hacer break out se puede hacer un break out como como

## 179:48 - 179:55
haríamos sobre que tratamos de desarrollar este serían un poco las cosas pendientes respecto a

## 179:55 - 180:04
esta estrategia que deberíamos de liquidarlo ya para entrar en otra en otra cosa no le metamos

## 180:04 - 180:09
más conceptos ya sé que le podríamos meter una tr le podemos meter mil cosas ya lo haremos de

## 180:09 - 180:14
acuerdo el sistema este lo vamos a dejar así con un don chan sencillito entre en la versión

## 180:14 - 180:23
tendencial que es muy mejorable lo vamos a dejar así y cortos y haremos un break out con esta con

## 180:23 - 180:30
este código también vale y a partir de ahí seguiremos en otras en otras cosas vale a ver

## 180:30 - 180:45
si me queda alguna pregunta como si puedes subir el código un poco antes sería lo suyo para trabajar

## 180:45 - 180:55
con él sí sí sí a ver si mañana me he puesto te he dicho antes el viernes para para dar límite

## 180:55 - 181:02
pero pero antonio el segundo código yo te lo voy a pasar pero ya lo tienes ya lo tienes quiero

## 181:02 - 181:09
decir que el segundo código es explicado lo he explicado todas las clases que yo te lo voy a

## 181:09 - 181:15
pasar e insisto que te lo voy a pasar pero si ahora luego que yo te vuelvo a subir la clase

## 181:15 - 181:22
me oyes lo escribes aparte que lo he enseñado lo he enseñado es decir es que la la es que el

## 181:22 - 181:32
setup de entrada es este de verdad o sea todo lo demás todo todo lo demás es accesorio esto es

## 181:32 - 181:43
esto es el setup de entrada es el setup de entrada si cierra por encima del canal de n cierres hemos

## 181:43 - 181:50
visto 6 hemos visto 20 etcétera compra en la apertura de la siguiente vela esto es lo que

## 181:50 - 181:55
lo pasaré y el trailing es lo único que tiene un poco más de desarrollo a nivel de programación

## 181:55 - 182:05
pero el concepto es súper básico o sea es el mayor el máximo que haya hecho el precio desde que

## 182:05 - 182:10
abres el más en ese caso sí que es el máximo de ese máximo siempre le va restando un porcentaje

## 182:10 - 182:17
ese es el stop trailing cada vela cambia con cada vela que cambia si hace un máximo porque si no

## 182:17 - 182:21
hace un máximo no actualiza de acuerdo es decir sólo el máximo del máximo le restas un porcentaje

## 182:22 - 182:31
y eso era lo que era un 027 un 020 de acuerdo es hora que es un 20% entonces es un poco la idea

## 182:31 - 182:41
pero insisto que me comprometo a si mañana no llego voy a hacer lo máximo para que el miércoles

## 182:41 - 182:52
lo podáis tener lo podáis lo podáis tener el miércoles vale y qué más qué más qué más o sea

## 182:52 - 182:57
se puede preguntar si se puede aplicar trailing esto y esto para la vez aseguró una pérdida esto

## 182:57 - 183:10
fija sí sí sí es es posible y tiene sentido pero en este caso y el sentido a ver depende

## 183:10 - 183:14
del tipo que vos es realmente digo eh depende del tipo que vos o sea en el trailing que hemos

## 183:14 - 183:22
puesto nosotros en el trailing que hemos puesto nosotros mucho mucho sentido no tiene vale porque

## 183:22 - 183:28
ya hemos puesto porque hay muchos el concepto clásico de trailing hay muchas veces que se activa

## 183:28 - 183:35
a partir de cierta cantidad pues en esos casos mucha gente sí que usa un esto un esto de seguridad

## 183:35 - 183:40
podemos decir acordaros cuando hablamos un poco del esto de seguridad no y que entra ya nada más

## 183:40 - 183:47
abrir pues un poco por si se lía no es que me saque no pues no tener que no me saca pero en

## 183:47 - 183:53
nuestro caso el telín se activa desde la entrada en el momento del cálculo se calcula del cierre

## 183:53 - 184:00
anterior y en el momento que el precio que acaba la barra en que ha entrado ya entra en juego el

## 184:00 - 184:05
valor máximo que haya o el cierre anterior o el máximo que haya hecho ese día el máximo que haya

## 184:05 - 184:10
hecho ese día actúa de trailing y entonces ya tienes trailing claro que es un 20 por ciento por

## 184:10 - 184:17
eso has visto algunos aquí como este o bueno incluso otros peores que se va se va para abajo y a tomar

## 184:17 - 184:24
viento a tomar viento el problema de los tendenciales puros es este que si tú quieres un tendencial

## 184:24 - 184:30
puro y quieres tres como esta locura de que te pilla toda la subida no esto pues claro solo

## 184:30 - 184:38
ahí dejándolo dejándole tragándote estas cosas también ese problema porque si yo le pongo una

## 184:38 - 184:43
salida por tiempo que va muy bien y evitará mucho esto que evitará también que pille la

## 184:44 - 184:49
por eso decía que un tendencial es bastante desagradecido es muy desagració te decía el puro

## 184:49 - 184:54
luego están los breakout que también son tipo de tendencial que ya se manejan mejor y que este

## 184:54 - 184:59
lo haremos también mercado vale entonces conceptualmente si se puede pero en esta

## 184:59 - 185:04
configuración tal como está no tiene demasiado sentido porque ya actúa siempre este lo que pasa

## 185:04 - 185:09
que le da mucho margen le da mucho margen pero este desde el primer momento que entra ya va

## 185:09 - 185:14
calculando aquí le calcula un 27 pero no ha saltado ahora para que veas este aquí le

## 185:14 - 185:28
pongo 10 por ciento y seguramente salta salta ahí salta aquí salta aquí es un poco la idea no es

## 185:28 - 185:34
claro yo lo tengo siempre siempre calcula este este que hemos hecho nosotros imagínate que le

## 185:34 - 185:41
pongo 005 no va a parar de salirse todo el rato es ya cambiado completamente el sistema es otro

## 185:41 - 185:47
sistema no para entrar a salir a salir a salir a salir a salir que cuesta mucho porque el precio

## 185:47 - 185:52
va haciendo sus oscilaciones y alguna vez oye y ahora un trocho grande pero la mayoría de veces

## 185:52 - 185:57
no porque se va a salir todo el rato y ahí está el equilibrio de los tendenciales este es el

## 185:57 - 186:03
problema en los sensores que para pillar largos recorridos y no caer en esto hay que dejarlo

## 186:03 - 186:08
sufrir claro que hay maneras de utilizarlo más para evitar las otras pero un tendencial puro es

## 186:08 - 186:13
uno de los casos de trelling aunque ya os lo comenté en la teoría es verdad que trelling

## 186:13 - 186:19
acopla bastante acopla bastante pero el porcentaje acopla menos entonces acopla bastante quiere decir

## 186:19 - 186:29
que lo lo vas a lo metes ahí pero 25 y luego empezarás a ver que a veces ha degradado ha

## 186:29 - 186:43
degradado a ver un segundo que te leo es que a veces que va directo a pérdidas se hacen más

## 186:44 - 186:53
es que el trelling hay veces que se va directo a pérdidas igual por el cierre o algo y hace más

## 186:53 - 187:05
de lo configurado a que te pierde más de lo que tienes esperado que es decir depende cómo lo

## 187:05 - 187:09
tengas votado si lo pones desde el principio si lo pones en principio que se siempre puesto en

## 187:09 - 187:16
mercado al final claro te puede pillar un gapos aquí en este caso vas a tendencia y te vas a

## 187:16 - 187:23
tragar claro los resultados el otro día lo hablaba en el directo del jueves había no sé qué acción

## 187:23 - 187:28
había caído 15 pues te lo tragas claro esto hay en acciones tienes ese problema aquí muy

## 187:28 - 187:34
diversificado y porque te lo tragas en tendencia tenés el problema pero ya veremos otro tipo de

## 187:34 - 187:39
estrategias cuidado es decir al final ahora estamos viendo esta pero pero que tiene su lado

## 187:39 - 187:44
bueno y su lado malo al final y por eso la idea es tener varias tener una así tener otra que te

## 187:44 - 187:49
lo compensa y ésta te queda enganchada pero a lo mejor tienes otra que había iba corto en petróleo

## 187:49 - 187:59
y no sé qué hay que ir diversificando los tendenciales ya digo que son de hecho cuando

## 187:59 - 188:04
uno no tiene mucha experiencia son sistemas bastante poco llevaderos vale lo hablamos

## 188:04 - 188:09
en la teoría normalmente es más tendencial hay más llevadero un sistema antitenencial porque

## 188:09 - 188:15
porque el antitencial no deja no tiene colas largas en cambio los tendenciales o sea con

## 188:15 - 188:21
dentro lateral no para de fallar no para de fallar no para de fallar y te devuelve mucho el mercado

## 188:25 - 188:40
por no sé jose bien bien no sé exactamente esto que dices un 2 y que te hago un 4 no sé no sé

## 188:40 - 188:44
por qué que no tengas un problema de cálculo sino lo que te digo los gaps claro los gaps y

## 188:44 - 188:51
sí pero vaya el gap está afectado igual de un stop que de está afectado igual o sea no tiene

## 188:51 - 188:59
más si está bien calculado no tiene no tiene más tendrás alguno 100% tendrás alguno 100% que

## 188:59 - 189:05
te va a hacer más o sea es que eso es así no tiene mayor mayoría tendrás muchos hechos que

## 189:05 - 189:12
te hará que te hará más pero pero vaya tanto en uno como en otro tanto en esto como si no bueno

## 189:12 - 189:19
explica pasar a nosotros un email y tal y explicando lo mejor y lo miramos lo miramos a ver por qué

## 189:19 - 189:29
porque te pasa eso tendencia al puro no es usual por nuestro blog fijado mejor trailing la verdad

## 189:29 - 189:38
que era es que se pende en que que vayas depende en que vayas un esto en un tendencial en un

## 189:38 - 189:43
tendencial puro el trailing y generando somos súper amigos de los que los digo estamos ahora

## 189:43 - 189:49
empezando las prácticas como el que dice vale es la primera estrategia que hemos hecho vale pero

## 189:49 - 189:57
si algún tipo de sistema va bien el trailing es en el tendencial en el tendencial puro si alguno

## 189:57 - 190:03
vale va bien este tu aquí puede nosotros operando en live pero no usamos vamos a esto pero no es

## 190:03 - 190:11
tendencial puro no es tendencial puro en un tendencial puro ya digo el trailing es el caso

## 190:11 - 190:18
que más que más sentido tiene sobre todo en acciones sobre todo en acciones buscando el largo

## 190:18 - 190:22
recorrido que es un poco la idea este sistema que lo puedes configurar así pero no es la idea ya

## 190:22 - 190:28
ese sistema y por eso lo hemos metido en las acciones es que corra vale es un sistema para

## 190:28 - 190:34
correr esta es su idea su sentido y claro es un o sea es un sistema que cuando netflix sube un

## 190:34 - 190:41
200 por ciento lo pilla me entiendes ahora eso tiene un precio me entiendes eso tiene un precio

## 190:41 - 190:48
cuando meta está en lateral un montón de tiempo pues te lo tragas ahora en cambio está en el

## 190:48 - 190:56
que alucinas pero claro tu imagínate ya en sus está básico que no no no no voy ahora a 6020

## 190:56 - 191:04
vale que solo hablamos y le quito el filtro vale esto ya es configuración básica original sin

## 191:04 - 191:16
hacer nada el largo que lleva en meta está comprado ahora mismo en 119 20 están 470

## 191:17 - 191:27
400 por ciento claro eso sólo lo pillas así sólo pillas así claro a costa de eso aquí se te ha

## 191:27 - 191:33
tragado tres hostias que te han dejado la cuenta bonita pero hay que estar dimensionado para ello

## 191:33 - 191:38
y cuando está estado en lateral pues está cosido también claro bueno en estas etapas ha aguantado

## 191:38 - 191:46
muy bien porque claro tiene mucho margen pero hay acciones o yo que sé cuando netflix mira

## 191:46 - 191:56
netflix es tremendo porque netflix tuvo ahora sí pero a tener una época hace tiempo y ahí a la

## 191:56 - 192:17
tragadita perdona venga comprado en 95 98 y te sacan 300 bueno tiene lo bueno y tiene lo

## 192:17 - 192:22
malo pero cuando se pasa una época mala pues te hace polvo pero es aquí el tiempo que está que

## 192:22 - 192:31
no hace nada si no si no si no al final coge tendencia en el tendencial ya digo es el caso

## 192:31 - 192:38
que te va a pensar con esto puro tiene que tener otra salida que me lo decía la verdad de antonio

## 192:38 - 192:45
si yo aquí este sistema tiene puesto un esto pero como salgo tengo que necesito otras sí o sí porque

## 192:45 - 192:54
si no vuelve yo te desactivo el trailing ahora y te pongo el mismo en stop el mismo 0 20 no sale

## 192:55 - 193:03
nunca entiendes porque no cae 0 20 el precio de entrada nunca ya tiene que caer 0 20 de aquí

## 193:03 - 193:10
explicó es decir al final no es igual 0 10 necesita otra salida cambio el trailing no

## 193:10 - 193:16
el trailing garantiza que no necesita nada más entonces si yo no quiero muchos grados de libertad

## 193:16 - 193:21
y demás quiero simple trailing me soluciona que sólo puedo usar esa salida yo aquí sólo tengo un

## 193:22 - 193:31
y una salida nada más las las pérdidas se pregunta antonio si se podían compensar con el lado

## 193:31 - 193:37
corto bastante bien bueno si se puede claro esa es la idea pero es muy difícil hacer cortos en

## 193:37 - 193:43
acciones antonio es muy difícil es posible pero es muy difícil con un tendencial es muy complicado

## 193:43 - 193:50
es muy complicado porque vuelve mucho es decir mira esto es un ejemplo muy bueno de hecho mira

## 193:50 - 193:56
es que lo podemos hacer rápidamente ya para ir acabando podemos hacer mira el mismo lo vamos

## 193:56 - 194:01
a poner corto ahora mismo vale el don chan porque esto no nos vale te pongo el don chan

## 194:01 - 194:29
lo que lo cambiaron pero te lo pongo igual 20 0 20 vale 20 0 20 20 0 20 hay perdón pero cortos

## 194:29 - 194:51
true 0 20 no activa el corto no lo activa estoy atontado y si se activa lo que pasa

## 194:51 - 195:06
igual no ha saltado pero si parece lo que salte alguna vez 20 20 20 no claro ya sé que pasa ya

## 195:06 - 195:12
sé que pasa ya sé que pasa que con él sin el filtro lo tengo mal configurado es fallo míos

## 195:15 - 195:23
porque como la volatilidad es inverso lo activo la volatilidad y así

## 195:23 - 195:32
es un problema de que no es que sea un problema en sí pero que no bueno si es un problema porque

## 195:32 - 195:46
no le he previsto activar el corto sin activar el filtro así pierde casi seguro en el lado corto

## 195:46 - 196:01
digo es que pierdes que se arruina entonces claro pues lo bajamos pero entonces no era bien el

## 196:01 - 196:06
largo tienes que hacer que hay que buscarle un set up para el corto es decir el mismo set up en

## 196:06 - 196:12
acciones el largo y corto es muy complicado hay poca algún tipo de sistema pero no no un

## 196:12 - 196:19
tendencial en un tendencial no lo vas a conseguir en este tipo no lo vas a conseguir entonces aquí

## 196:19 - 196:24
y hay que ir a otra cosa aquí la otra casa aquí en un corto pues no es lo que os decía ya no os

## 196:24 - 196:28
digo porque si no ya pero no corto hay que ir a otra cosa este mismo sistema hemos puesto salida

## 196:28 - 196:35
por tiempo esto tp aquí la otra cosa en un corto en acciones se puede para que la otra cosa hay que

## 196:35 - 196:42
salir rápido de acuerdo hay que salir entonces en este set up es muy complicado porque las

## 196:42 - 196:48
tendencias son muy abruptas es decir te entran entran muy bien así este caen y mira te has

## 196:48 - 196:52
rebotado y te has sacado antes encima ya te mete aquí y aquí aún mira no salvas pero es

## 196:52 - 197:02
súper complicado es súper complicado es súper complicado vuelve muchísimo el precio vuelve

## 197:04 - 197:12
y le cuesta muchísimo rebota muy violentamente luego vuelve a caer y la vez aquí cae ya está fuera

## 197:12 - 197:22
final largo otra vez corto estás corto ahí estás es muy es muy duro que el mercado vuelve mucho

## 197:22 - 197:29
muy escarpado es mucho más escarpado cayendo que subiendo el mercado se resiste mucho caer

## 197:29 - 197:36
para que me entiendas existe mucho que hay algún momento que no pero en norma acabas

## 197:36 - 197:42
perdiendo mucha pasta en cortos pero nosotros el nasa que lo operamos el lado corto pero

## 197:42 - 197:53
este año hemos perdido el largo plazo pero el año pasado hemos perdido con apolo vale ya la última

## 197:55 - 198:01
pregunta antonio comenta no que si a mejor bajar el frame más tendencia vaquista más

## 198:02 - 198:06
bueno puedes bajar el frame o puedes operar otro tipo de sistema antonio otro tipo de

## 198:06 - 198:11
sistema si no no hace falta buscar tendencia es decir puedes buscar tendencia en el lado largo

## 198:11 - 198:18
y ir anti tendencia en corto y también puedes buscar una nota y freme no digo que no pero es

## 198:18 - 198:26
que el mercado es fractal es decir el lado corto tendrás ganarás unas cosas pero perderás otras

## 198:26 - 198:36
es decir no no necesariamente es más sencillo es más difícil es más difícil pero sí sí que

## 198:36 - 198:41
hay algunas cosas que te pueden ir bien ese nivel sobre todo te puede ir bien en el control del

## 198:41 - 198:49
riesgo el perder menos cuando falle no te puede ir mejor ahí pero también te va a sacar sabes

## 198:49 - 198:55
o sea también así que no más tendencia el puro es complicado es complicado ahí hay que

## 198:55 - 199:06
buscar más bien break out anti tendencial por la tiri y breakout rotura para salir buscar salir

## 199:06 - 199:13
por tiempo o por tp tener un objetivo el total o al menos la mitad hay que jugar un poco con eso

## 199:13 - 199:20
vale bien ya os he dicho un poco la agenda del día que viene y para los que queráis trabajar

## 199:20 - 199:31
pues lo podéis poner bien en el discord y nos lo envíais por email vale lo que digo máximo

## 199:31 - 199:36
bienes pero intentaré por todos los medios que el miércoles ya esté subido el pseudocódigo y la

## 199:36 - 199:41
explicación que la idea que tenemos es hacerlo en un pdf donde nos aportamos la ficha un poco

## 199:41 - 199:45
una explicación de cada sistema vale y tener así poderla la podéis tener como como documentación

## 199:45 - 199:57
del curso de acuerdo pues nada más amigos os veo el viernes os veo os veo el viernes gracias en

## 199:57 - 200:05
las otras palabras hay el viernes que digo el viernes pues bien lunes bueno jueves el que quiera

## 200:05 - 200:12
ya sabe que estoy en directo para todos los para quien quiera los clientes para para todo el que

## 200:12 - 200:18
quiera interactuar con con nosotros públicamente pues ahí estamos y si no la clase el lunes que

## 200:18 - 200:25
viene de acuerdo en un par de horitas está el vídeo subido hasta pronto familia os veo chao
