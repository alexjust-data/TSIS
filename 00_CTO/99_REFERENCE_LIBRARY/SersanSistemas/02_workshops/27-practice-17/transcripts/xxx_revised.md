**Regímenes de mercado y el VIX Term Structure**

Tengo dos cosas pendientes para empezar; voy a dejar el *COT* para el final, como puede ser que a alguien le interese, y después vale. Hoy voy con esto de *regímenes de mercado*. Vale, esto lo tenía apuntado desde el principio y al final pues ha llegado al final, pues sí quería darlo. Cuando hablé del *VIX*, el *VIX* tiene muchas utilidades, pero es muy peligroso y muy complicado. Recordaros en la teoría, cuando se hizo ese ejemplo con el *VIX*, que parecía que iba bien y al final se iba a tomar viento. Vale, ¿por qué? Porque el histórico, que si *contango*, que si *van guards*... O sea, es un activo complicado de operar, porque el índice es muy chulo, le puedes coger cosas, va muy bien, pero tú no puedes operar el índice: tienes que operar futuros o *ETF*. Hubo un *ETF* que se rompió, no me acuerdo el nombre, Alberto se acordará supongo, que ha salido un momento, en fin... O sea, al final tiene tiene tiene miga la cosa, es cuidado.

<div style="border-left: 4px solid #27ae60; background: #ecf9f1; padding: 10px 15px; margin: 10px 0;">
  <strong>📘 Nota técnica</strong><br>
  El <em>VIX</em> (Volatility Index) es el índice de volatilidad implícita del S&P 500, calculado a partir de los spreads de las opciones. El problema de operarlo directamente es que los instrumentos disponibles (futuros y ETFs) sufren el efecto del <em>contango</em> (cuando los futuros lejanos cotizan más alto que los cercanos), lo que erosiona el valor con el tiempo.
</div>

Ahora bien, el *VIX* también tiene alguna utilidad muy interesante, que es como la *estructura de la volatilidad*. Como al final es un indicador de miedo, porque mide el *spread* de las opciones de los S&P 500, y tiene distintos vencimientos, tiene *curvas de plazos*. El CME publica índices, vale. Quizás viendo uno que le llaman *VIX*, esto está en la plataforma, vale, el *VIX Near Term*. Estos los voy a dar, y aquí tengo el *VIX*. Y esto hay muchos autores, hay *papers*, os vamos a dar el *paper* también. Hemos visto el *SSRN* que tiene, sobre mañana... Esto es... Por favor, cuando acabe me voy a casa, pero subiré todo lo que he comentado. Esto hay *papers* que usan eso como indicador de *régimen de mercado*, pero un poco de... en este caso *régimen*, *régimen*, *modo alarma roja*, *modo alarma roja*.

**El indicador IVTS**

Entonces esto es un indicador muy sencillo que se llama... Y se me está complicando la cosa porque ya suponía que claro, hablar tres, pensar que todavía cuando... Como sufrido tanta tanta tos... Sé que esto no importa, pero me hace gracia explicaros que tengo una gran parte de esto, era... tenía días en carne viva, o sea, era tremendo. Y ahora pues claro, recuperando muchísimo, mucho mejor, pero por ejemplo cuando como, solo de la excitación o lo que la comida me da tos. Todo es claro, hablar hablar hablar pues la garganta está a quejarse a veces. Entonces ese es el tema. Sé que voy a volver, porque parece que sin querer me había ido elevando la voz, vuelvo a nivel bajo. Eso le llaman *ASMR*, voy a empezar a hacer *ASMR*, si hablaros así, sus sus raros, a ver a ver qué tal, a ver qué tal si podemos ir, aguantar bien.

Lo que os comentaba de los *regímenes*, hay un *paper* que ya os lo subo, como decía mañana, y bueno parece que ya haberlo se ha preparado varios, pero bueno el principal, que es el precursor, creo que es éste. No es... bueno, se lo subimos a... pero no es éste, era... es el el primero. Y *VTS*, si buscamos información, esto es *implied*, por la directa, y *term structure*, vale. Entonces hay un *paper* que se ha subido al *SSRN*, vale, que habla un poco de todo esto, ya lo subiré, que lo quiera leer.

<div style="border-left: 4px solid #27ae60; background: #ecf9f1; padding: 10px 15px; margin: 10px 0;">
  <strong>📘 Nota técnica</strong><br>
  El <em>IVTS</em> (Implied Volatility Term Structure) es un indicador que compara el VIX de corto plazo con el VIX a tres meses. Cuando el ratio supera 1, significa que la volatilidad a corto plazo ha superado a la de largo plazo, lo cual suele ocurrir en momentos de pánico o crisis de mercado (<em>backwardation</em>).
</div>

Ya os lo explico simplemente: divide el *VIX* por diferentes plazos, vale, y con esto pues hace distintas... El que he visto más veces usado con el de tres meses, pero final para la estructura. Los futuros, acordaros, que normalmente están en *contango*. También el *VIX*, ¿qué quiere decir en *contango*? Lo vimos en la teoría, pero no recuerdo... Es lo lógico, es decir, que el futuro más lejano en el tiempo valga más que ahora. ¿Por qué? Porque el tiempo, solo el factor temporal, los tipos de interés, incorporan un coste. Recordaros el *valor temporal del dinero*, primera clase del curso. Para los no iniciados, si alguien iniciado se lo saltó, hombre, que habéis comprado el curso, yo recomiendo verlo, pero ahí hablamos un poco de esto y de otras cosas.

Y lo que digo, esto es lo normal. Que ahora mismo, por ejemplo, ¿qué pasa? Tenemos el *VIX* corto plazo a 12,47 y el *VIX* a tres meses 14,76. En *contango*, lo lógico, lo lógico, lo normal. Entonces este indicador *IVTS*, que lo tenemos aquí, pues recoge eso, está en 0,84, que está por debajo de 1. Cuando sube de 1, quiere decir que el tres meses ha superado al corto plazo, bien. Eso usualmente pasa en momentos críticos de mercado.

**Recomendación de uso del IVTS**

Entonces esto recomiendo explorarlo, probar dos meses, para cada uno tiene que trabajarlo. Yo sé, da un código, hemos hecho un código para que lo podéis trabajar, un código marco, no un código ya acabado. Y ya esto es todo. Esto es poneros súper *bonus*, de hecho os diría más. Esto, en el curso hay perfiles de todo tipo de gente: gente que está empezando, gente que ha hecho *trading* gente que no, y gente que ya incluso hacía *trading* algorítmico y está viendo a ver qué cuento, vale.

**Repaso del material del curso**

Y aprovecho para deciros una cosa: nosotros hemos, en este tiempo, hemos revisionado prácticamente todos los vídeos. En el curso hay cosas, hay perlas de muchísimo valor, lo que pasa que no están... No digo "ojo, voy a decir una perla", es decir, está todo comentado por ahí, está hablado, porque yo hablo y hablo y hablo y he soltado cosas de mucho valor, de acuerdo. Y el material al final que hemos dado es una locura, es una locura, mucho más de lo que pensábamos ahora de entrada, porque somos así. Es todo el material, solo solo lo de *Status and Concepts* es una bomba. Todo ese material ahí, con el Excel aquel que os dio el análisis, realmente ahí hay muchísimo material para trabajar y seguir aprendiendo. Pues el curso, que hay que seguir aprendiendo, esto no acaba, no acaba ni mucho menos hoy, y cuando acabas hay que seguir trabajando permanente, bien.

Después de este rollo, que venía al caso pero no sé por qué, aprovecho para hidratar. Venía al caso por lo que os decía: en este caso, este *IVTS*, esto podemos considerarlo un nivel avanzado, podemos considerarlo un nivel avanzado. Entonces, si sois principiantes y demás, mirarlo, claro que sí, entenderlo, pero tampoco os vais locos, vale, tampoco os vais locos.

**Código marco para análisis de regímenes**

Entonces nada más. Entonces lo que os decía: os hemos hecho un para... os lo enseño para valorar y para estudiar. Hay muchos códigos, como por ejemplo el que dimos, el *buscador de entradas*, también bastante potente pienso yo, pensado con que crezcáis y lo adaptéis. Éste está más desarrollado que este, pero aun así es un marco, es un ejemplo de cómo trabajar estas cosas, no es directamente ya el sistema hecho. Lo mismo aquí: aquí hemos planteado un código marco para analizar *regímenes de mercado*, para que vosotros trabajéis y para valorar el *IVTS* y mostraros si tiene utilidad o no, vale. Y lo hemos hecho de una manera simple que nos ha parecido razonable y creemos que es así. Y hasta aquí está el código.

Al mismo tiempo pues hemos incorporado más maneras de mirar el *régimen*: manera súper fácil, una *media móvil*, el *ADX*, vale, y como os digo la volatilidad mediante el *IVTS* este. Entonces al final hemos creado aquí unos *cases* que definen un tipo de mercado:

- El *Buy and Hold* alcista no volátil quiere decir que está por encima de la media y el *ADX* por encima de su umbral, ahora lo miramos en el gráfico.
- *Alcista volátil*: el mercado por encima de la media, el *ADX* por encima del umbral, pero el mercado está volátil, es decir, el *IVTS*, perdón, ya diré... *IVTS*, ese, venga, pues vamos, *IVTS* y *IVRS*, vale, *IVTS*.
- Pero no sé por qué tengo en la cabeza... Bueno, aquí está volátil, con eso disparado, no tienes el *ADX* negativo y no volátil, es decir, el mercado no tiene tendencia porque el *ADX* está indicando que se halla, podríamos decir que es lateral. Es decir, lateral, el *ADX* te puede decir eso con la volatilidad baja. Y el *ADX* con la volatilidad alta, o sea, el *ADX* bajo pero la volatilidad alta.
- Luego *bajista y no volátil*, que quiere decir bajista pues por debajo de la media pero con tendencia de mercado *ADX*, y así.
- Y luego al final hemos puesto el *mercado volátil*, el *mercado no volátil*, o sea, solo la volatilidad, solo el *IVTS* en *false* o *true*. Y hasta... Pero esto, como os pongo aquí arriba, puede crecer.

**Escenarios de régimen de mercado**

Realmente hemos puesto 6, pero se pueden plantear más escenarios. Por ejemplo, *media alcista pero el ADX bajista*, que quiere decir por debajo del umbral, es más que correcto, y viceversa. Es decir, se puede plantear distintos escenarios. Estos son los típicos, porque el *ADX bajista*, como pongo aquí, que no sé si es lo más correcto, prácticamente es lateral, pero se puede plantear distintos escenarios.

Esto al final, si hacemos aquí una sencilla para que lo veáis... Lo había hecho antes porque nos ha guardado. Esto solo sale el largo porque es el *SPY* de 0 a 8. Esto, que dura 0 coma segundos, diario, vale. Nos va a decir que el que más gana es el 0, es decir *Buy and Hold*. Pero no es la que mejor es, que lo tiene... Pero me interesa sobre todo que veáis, acordaros que el 7 y el 8 eran el volatilidad, volatilidad. Y fijaros que el volatilidad gana 245 y volatilidad gana solo 17 con las más operaciones. Es decir, claramente confirma, vale.

**Análisis del régimen de volatilidad**

Que ahora voy a poner el volatilidad... Y además se podía separar el *setup* de entrada y salidas, y todo esto está hecho para mostrar, simplemente mostrar, simplemente el ejercicio. O sea, está la misma que la planta para salir. Decir, esto compra cuando la verdadera está alta y vende cuando los... Fijaros cómo demuestra claramente que comprar cuando este indicador se dispara cuesta caro, casi no gana. Y de hecho, depende cómo, pierde.

Porque fijaros aquí, que ya se empieza a disparar, aquí da una señal de aviso, pero aquí ya en la primera caída ya estaba a punto de romperse, por un poco, por no nada se... No lo compra antes, de hecho aquí ya corta, y para mí disparé, compra y al final se mantiene alto. Aquí, que ya está recuperado, para que vuelva a bajar, comprar. Y entonces la mayoría de veces suponen tres perdedores. Comprar cuando eso está alto, de hecho fijaros que su porcentaje de aciertos es el, bueno, es el 65, pero es que gana... es que al final gana un poco. Pensaba que me saldrían pérdidas.

A ver, todo esto cuando era extrañado para ser el *régimen de mercado* de 5... O umbral 1,15, *spread* que será 15, no sé... ¿Puede mercado 8? Sí, sí, bueno, pues igual sale, sale. Sobre todo fijaros la diferencia. Lo que decía: con el otro, ahora pasamos al otro, al comprar justamente cuando está bajo y mantener. Y fijaros el cambio: ya tenemos también 105 operaciones. Otra cosa, realmente también pierde, que no tiene ningún criterio. Eso es un evaluador, no sale por ningún criterio, solo sale cuando la barra tira, su claro...

**Evaluación de señales de alerta**

Aquí, fijaros, como la mayoría de veces también tiene tres perdedores, lógicamente aquí, porque aquí aquí sí que sale, pero vuelve a entrar muy rápidamente. O sea, la señal de alerta no le dura nada, rápidamente vuelve y vuelve a caer, se vuelve a salir, va un poco persiguiendo la presión, está en este lateral. Pero al final es que es una corrección, que es corrección no es especialmente grave. Al final sí que es verdad que falla mucho. Al final está, sí que llegaba y justo al nivel para marcar el peligro, pero al final no había peligro, volvía. El mercado estaba fuerte, como aquí ha llegado, se ha acercado pero ha vuelto. Y al final aquí pues acaba entrando y se queda comprado. Así que, comprado, al final te muestra claramente como es un indicador de peligro muy claro, muy claro, vale.

**Análisis de otros cases**

También también lo vemos en otros, también vemos por ejemplo que el *case* que hay otro que pierde. Hay dos que pierden: el 2 y el 4. Ahora vamos a ver que son así está volátil. Cuidado, el *alcista volátil*, el alcista pero con esto disparado, te pierde dinero, es el que perdía, vale. Pero es que, fijaros, fijaros, que si lo pongo arriba... Y a nosotros no lo vais a ver, pero es que es imposible verlo todo, claro, es imposible verlo todo. Si vemos una cosa, no vemos la otra. A ver si lo puedo poner así, me la voy a ponerlo así, aunque se vea un trozo, ya me ya me vale, ya me vale.

Vale, es el 2, el 4, no, 4, 2. Pero el 2 *alcista volátil*, pero fijaros que su homólogo es *alcista no volátil*, es el 1, es 42, 42. Y el, claramente vuelve a demostrar que el 1 acaba confirmando. Y el 4 va a ser lo mismo: el 4 es con el *ADX* por debajo, es decir *lateral y volátil*, otra vez volátil vuelve a perder. Y su homólogo, *ADX no volátil*, es el 3, que es el segundo, gana gana bastante, 134. Vale, el lateral gana gana cuando el *ADX* cae, comprar ahí le da bastante.

**Análisis de ratios riesgo-retorno**

Esto simplemente es un analizador, habría que contemplar más escenarios de salir de maneras distintas, un poco, pero fijaros que si ya miramos *ratios de retorno-riesgo*, la cosa ya no queda tan clara. Y el que da mejor es 3. Por ejemplo, el que da mejor es 3, en este caso por *TSI*, que es este del *lateral y no volátil*. Es decir, es extraño, es decir, es extraño, es comprar ahí, comprar cuando está lateral y no volátil es extraño. Pero tiene sentido, porque al final, si el mercado está lateral pero no, el indicador de volatilidad no marca peligro, lo normal, que va a hacer la bolsa, por subir, pues ahí es un buen momento para entrar. O sea, está marcando un buen *setup*, porque el problema, el problema, es que aquí para evaluar eso, sale a entrar la salida igual.

**Lógica del case 3**

Entonces entonces al final, cuando corta se sale cualquiera de ellos. Es decir, si se corta el *ADX*, sale. Entonces está... entonces aquí necesita que los los 2. Entonces el 3 es lateral, que quiere decir que ignora la tendencia, es decir, aunque esté por debajo de la media, compra igual. Este ignora la tendencia, se ignora estar por debajo por encima de la media. Podría haberse complementado distinto, pero pero ve lo que compensa. Decir: solo opera solo con el *ADX*. Cuando el *ADX* no esté disparado, compras. Es así. No, exacto, cuando el mercado en tendencia, menos 1, es decir, cuando el mercado esté, compra. Y se sale cuando *pueden estar largos false* si cualquiera de los 2, tienen que ser los 2 *true*, claro.

Pero ese es el 3 activado, la situación activado el 3. El 3 es este, no lo ves, y a la que ya el *ADX* vuelve por arriba, es un tanto extraño, pero bueno le compensa. Cuando el *ADX* se empieza a disparar, es una vez entre las paradojas del *ADX*. Pero es verdad que los tramos de tendencia más fuerte se nos va a perder, como es aquí, ves. Pero sí que es verdad que la tendencia, como es, es un *ADX* que es muy lento, de 22, decir, de un mes. Es aquí, a la que ya está tendencia fuerte, se sale. ¿Por qué? Porque digamos que está más cerca de acabarse la tendencia. ¿Entendéis? Un poco a la inversa.

**Comportamiento en tendencias fuertes**

Ahora, ¿qué pasa cuando hay tantos son fuertes? Pues se queda fuera, se queda fuera. Ahora sí, aquí ya corrige y vuelve a estar. Al final lo que ha de centrar un poco en el mercado descansa. Es y porque le compensa, le compensa. Antes de ir, porque así tiene muy pocos *drawdowns*. Tampoco es que gane tanto, hay otros dos que ganan más: el *Buy and Hold* y el y el 7, el *no volátil*, comprar siempre que no... que estar comprado mientras no haya volatilidad. Pero el riesgo le compensa porque así se sale muy rápido, vale.

Pero insisto que esto estoy explicándolo para que entendáis por qué lo hace, no... Pero el objetivo de esto es es es daros el código, que entendáis un poco distintos mecanismos. Pueden haber otros, recordar que ya os enseñé en un ejercicio es componer el *DAX* en el de más y de menos. Se puede evaluar para evaluar, probarlo, a ver con el de más y con el de menos para alcista y para bajista. Hay que mirar los distintos umbrales, hay que trabajarlo. Esto simplemente era un ejemplo, vale.

**Prueba con volatilidad normalizada**

Hemos hecho otro ejemplo que no acaba de ir tan... Para nada, es decir, al final no deja de no deja de demostrar la validez del *IVTS* para esto, vale. Porque lo hemos probado con la *volatilidad normalizada*, probando distintos periodos, 60, 90. Y sí que sí que un poco lo detecta, pero mucho peor, vale, mucho peor. Es decir, o sea, este código de aquí es exactamente igual que el de la derecha.

Vamos a hacerle también la optimización, pero en vez de usar el *IVTS*, para poder usar más código, vale. De hecho me la voy a cargarle ya más código, porque claro aquí ya puedo meterle pues 30 años para poder meterle más código, más histórico. Entonces hemos usado el, como la *volatilidad normalizada*, haciendo lo mismo. Es un ratio, la volatilidad de 60 contra de 90, buscar un ratio de volatilidad, pues probar 60, 90, hay que probarlo. Entonces esto ya hay que hay que trabajarlo, no lo hemos trabajado porque repito el objetivo era daros el código.

**Resultados de la optimización**

Pero aquí podemos hacer la misma prueba, que va a tardar un poquito más, pero muy poco igualmente. Y veréis veréis lo que nos da. En este en este caso, aquí vemos otra vez lógicamente el que más ganas es *Buy and Hold*. Vemos que el 8 gana más que el 7, pero así gana muy parecido. Es decir, no hay una gran diferencia, hay una gran diferencia, vale. Es decir, no parece... No, de hecho gana el volátil más que... No acaba de no acaba de tener sentido. Habría que ver, habría que ver un poco lo que se va, que hay que jugar con los términos, vale.

Porque ese ratio cambia mucho de si le pones a ver qué jugar, eso con el umbral, con las dos cosas, pues sé que el umbral se ha necesario más elevado, es complicado. Sí que cuando ves el dibujo, le ves le ves, que tiene que tiene cierto sentido, pero no acaba de no acaba de tirar. Así con el volátil, con el volátil, que es el 8, no... El 8 debería haber momento... Aquí sí que ahora se ha caído, se ha caído más, se ha caído más. Ahora puede ser que con este 1,1, pero digo, es una sobreoptimización.

**Ajuste de parámetros**

En el final no deja de ser un intento por por enseñaros lo que queremos. Decir, es simplemente decir: poniendo 0,8, 0,60, parece que a lo mejor pues puede ir mejor. Pero ya digo, es solo para que entendáis la idea, para que entendáis la idea. Que sí, aquí sí que el 8 ahora vez, aquí sí que se ha penalizado la volatilidad, solo por poner 1,1. Pero aquí es muy sensible al indicador del *ATR*, entonces... Pero aquí sí que nos ha salido ya poco lo lógico: que el 8 más volátil gana menos, el 7 gana más. Tiene tiene tiene un poco más sentido, tiene un poco más sentido.

**Conclusiones del análisis**

El *Buy and Hold* sigue siendo el mejor. Y así, con más histórico, por *TSI*, en este caso sí que el *Buy and Hold* gana tanto, gana tanto, que le compensa, le compensa el riesgo, y no tiene ningún tipo de problema. Porque además es que no le no le está contando el del lado, porque no ha salido. No sé por qué no ha salido, porque debería salir. No, en el código tiene salir las barras *chart* creo... ¿Por qué no sale? No contemplado el *trade* en el optimizador porque está abierto, abierto... No, ya está puesto, pero al estar abierto no le ponemos hasta ayer. Y entonces lo volvemos a hacer. Entonces ya, porque no le ha contado, porque no le ha contado al cierre de *trade*.

Entonces ese es el pequeño pequeño es igual. Y nos digo que esto sigue sin contar, no sé por qué no lo cuenta, no lo entiendo. No lo cuenta y no marca *trades* cerrados, pero no sé por qué no cuenta la verdad, no lo entiendo. No entiendo por qué no cuenta el *drawdown*. Sí, si lo ha cerrado, pero no le cuenta el *drawdown*, se lo ha bloqueado. Sí, sí, porque mirar, el *drawdown* ahí está, cuenta... Bueno, sale éste que no cuenta la intradía, no cuenta la intradía. Bueno, es es falso totalmente, porque no es gigantesco como habéis visto. Ahí es que lo, llendo ese.

**Resultados finales**

El siguiente sería este. En este caso es el 1, o vendría el 7. Bueno, *alcista no volátil*, es bastante lógico. *Alcista no volátil*, o vendría el 7, que es *no volátil*, sale lógico, sale lógico, es decir, sale lógico. Y el peor, el 2, que es el *alcista volátil*, el *alcista volátil*. El 5, *bajista y no volátil*, es decir, no comprar en *bajista y no volátil*, no le no le no le gustan, a lo que sea *no volátil* es bajista. Bueno, esto es lo que tenía en cuanto en cuanto al *régimen*. Pero lo voy a dejar guardado así, Alberto.

---

**Sistemas COT**

Y vamos con los *COT*, vamos con los *COT*. Vamos a hacerlo breve porque solo es una y media. Veo que se está aguantando la mayoría. Yo sé aguantar, es aguanto. Vamos a hacer brevemente los los *COT* previamente pero bien, bien hecho. Un segundo que voy a abrir, porque el aire ya no va, se me ha abierto aquí en otro sitio, pero yo ahora mismo lo desplazo inmediatamente.

<div style="border-left: 4px solid #27ae60; background: #ecf9f1; padding: 10px 15px; margin: 10px 0;">
  <strong>📘 Nota técnica</strong><br>
  Los <em>COT</em> (Commitment of Traders) son informes publicados semanalmente por la CFTC (Commodity Futures Trading Commission) que muestran las posiciones de los diferentes tipos de traders en los mercados de futuros: comerciales (hedgers), no comerciales (especuladores institucionales) y pequeños especuladores.
</div>

Vale, los *COT*, os voy a dar todo lo que tengo sobre los *COT*, porque había mucho interés, no sé exactamente motivo, pero había mucho interés, y por lo tanto voy a satisfacer vuestra curiosidad. Nosotros tenemos ahora mismo tres estrategias diseñadas. Que no son estrategias, están todas en preproducción, no se han acabado nunca, porque no viene el caso de operar en futuros. Y aun así, solo lo operaríamos en una cuenta muy grande, ya muy diversificada. Lo digo para para todos vosotros, es decir, no sería un tercer sistema, de acuerdo. Sería como mínimo un décimo sistema, vale. Son sistemas que van normalmente en *barras semanales*, vale, porque los *COT* es un dato que viene en semanal.

**Documentación de los COT**

Primero, repito que lo subiré todo al Discord mañana, lo subiré todo al Discord mañana. Pero yo os explico aquí lo que tenemos, vale. De momento os subiré esto, que hay tres artículos directamente de la web para que os veáis, vale, porque es el mejor sitio donde ir a leerlo. Me parece absurdo hacer el PDF cuando está online, vale. *¿Conoces los COT?* Vale, aquí explico qué son los *COT*, estos de 2017, totalmente en vigor. Hay un ejemplo, hablo de los *COT*, los *3C*, eso que los publica, patatín patatán, vale.

Y luego los sistemas. Aquí están, algunos explicado. Yo explico los otros, no está todo porque no se ha publicado, no es público. Explico el *COT Index*, vale, que es lo que se basa la mayoría de sistemas, vale. El *COT Index* no deja de ser una especie de estocástico de los *COT*. Es decir, normalizar los *COT*. El *COT Index* es normalizar los *COT*. Ahora veréis qué es eso. Y explico un sistema, muestro unos datos, vale. Estos los subiré al Discord, no hace falta ahora ni que os fijéis en la dirección ni nada, porque los subiré todo al Discord, vale, que las estáis viendo, pero no hace falta porque los subiré, vale. Aquí la segunda parte y demás. Esto por un lado, en cuanto a la documentación.

**Sistemas COT desarrollados**

Esos dos sistemas, los que vais a ver ahora, aquí con *Estrategia 1*, el 2 es este artículo, este artículo de *Traders*. No es el que hemos desarrollado, creo que no es impecable, porque hay cosas que hay que interpretarlas y demás. Por ejemplo, *money management* no lo implementamos, pero está bastante desarrollado. Y ahora sí os doy el código que hicimos nosotros, lo hicimos nosotros. El *COT 2* y el *COT 3* es el *COT de Kaufman* (Perry J. Kaufman, autor de *Trading Systems and Methods*). Ahora los veremos, vale.

**COT 1 - Sistema Rullero**

Vamos con el *COT 1*, que son los dos de los artículos que veréis en web. El *COT 1*: primero, los *COT*, este indicador que veis, son los que os decía, esa esa forma que habéis visto es el *comercial*, hecho con 55 semanas, que es un año. Es decir, el saldo de los *comerciales*, como hace un estocástico. Pero las cosas hay que entenderlas: un estocástico hace lo mismo. Cuando está arriba quiere decir que está en el máximo del periodo que está estipulando, pues esto es lo mismo. Cuando está aquí, que está en el periodo máximo, que un año, el saldo de los *COT*, vale, el saldo de los *COT*.

Y ese es el de los *pequeños especuladores*. En los artículos iniciales explico qué es un *COT comercial*, qué es un *non comercial* y qué es un *pequeño especulador*. No voy ahora a recrearme mucho en eso porque no tenéis los artículos y quiero lo sepa.

<div style="border-left: 4px solid #27ae60; background: #ecf9f1; padding: 10px 15px; margin: 10px 0;">
  <strong>📘 Nota técnica</strong><br>
  <ul>
    <li><em>Comerciales</em>: Considerados las "manos fuertes". Usan futuros como cobertura, deben tener el activo subyacente en posesión.</li>
    <li><em>Non Comerciales</em>: Especuladores institucionales, hedge funds.</li>
    <li><em>Pequeños Especuladores</em>: Traders minoristas, considerados el "dinero tonto" en la teoría clásica.</li>
  </ul>
</div>

Pero los *comerciales* se consideran las *manos fuertes*, es un poco... El *pequeño especulador* somos nosotros, los pardillos, es un poco la idea. Y los *non comerciales* son los que consideran los *hedge funds*, eso es un poco la teoría. La diferencia entre estos *comerciales*, los *hedge funds*, es que los *comerciales* utilizan el futuro como cobertura, tienen que tener el activo en posesión y se están cubriendo, y el otro, el *hedge* no, por eso es uno u otro. Pero ya digo, es igual, eso al final da un saldo, y ese saldo se hace un *COT Index*.

**Datos COT en TradeStation**

Y aquí están bruto, que estos datos están todos aquí, es decir, estos *COT* están todos aquí publicabas. Este esto con *Net Position*, esto es de TradeStation. Solo tenéis ya esto. Si ahora aquí buscáis *EasyLanguage*, *COT Net Position*, este indicador existe la plataforma. No tenéis vosotros pues si buscáis en aquí *CO*... Yo tengo más porque tengo varios propios, pero veréis que tenéis ya muchos. Y os podéis abrir, pues leer el código, ver cómo está hecho, como siempre. Son datos *fundamentales*, esto lo coge de *Reuters* y lo y lo grafica, vale. Entonces ahí está hecho, eso ya lo tenéis.

Y aquí veis los saldos, es el porcentaje que tiene cada uno. Todos estos son indicadores que ya están y que tú no puedes hacer, tú no puedes... Que ya está toda esta información que veis aquí está disponible. La tienes que montar, lógicamente tiene que ser un futuro que publique esos datos. Estos no lo publican, por tanto no hay datos si no los publican, por nada, obvio.

**El COT Index**

Y nosotros qué hemos hecho: pues el *COT Index*. Con esos datos hemos hecho el *COT Index*, que los datos son estos. Esto que tú quieres, aquí ves arriba el *non comercial*, y abajo ves el *index* son *comercial*. Ves cuando baja, pues se quiere la parte baja, cuando sube de 52 semanas, pues se ve. Es, este tiene puesta las bandas de... Son nuestras también. Y ya está. Pero es que la información saldo disponible.

**Reglas del sistema COT 1**

¿Qué hace ese sistema? Ese sistema en sí usa la idea de *Rullero*, pero realmente no tiene nada. Realmente la idea de *Rullero* es la idea más básica de los *COT*, vale. Es decir, simplemente tienes un *trigger* arriba y abajo, es un periodo que nosotros damos 55 semanas, no a conocieron sabes, si tienes un periodo para salir mal, centra.

Esto sí que quiero recordar que era de *Rullero*, solo va largo, y solo usa dos: *comerciales* y los *pequeños*, no usan los *no comerciales*, vale. Entonces al final, simplemente compra cuando el *COT* de la barra anterior, que es la semana anterior, tiene el *COT comercial*, el índice anterior está por debajo del *trigger*, y la siguiente está por encima. Eso se podría haber hecho con un *crossover*, entiendo. Eso justamente es un *crossover*, si le pones *si COT Index crossover*... No perdón, perdón, perdón, que me estoy leyendo eso, me pasa por leer rápido.

**Lógica de entrada del COT 1**

¿Cómo funciona esto? Si en la semana anterior el *comercial* estaba por debajo del *C trigger* 70, es decir no está sobrecomprado, se entiende, y el índice de los *especuladores* de esta barra es mayor que el *S trigger*, que es el inverso, es decir que 30, compró en un *stop long*, que no deja de ser el... Vamos a las horas, vuelvo vuelvo a revivir y empiezo y empiezo. Que mientras lo leía digo, no me cuadra.

Compra cuando se sobrecompra el *comercial*, vale. Compra cuando se sobrecompra en la barra anterior, es decir, cuando supera 70, y los *especuladores* están por debajo de la venta. ¿Por qué? Porque se considera que los pequeños no están nunca en el lado bueno. Por lo tanto, cuando los pequeños están comprando, el... Están abajo, están en mínimos. Compra, es decir, compra cuando éste entra en la banda arriba y éste la banda abajo. Esto es como compra.

**Reglas de salida del COT 1**

Y sale, sale de dos maneras por lo que se había dicho antes: por la señal contraria, vale. Es decir, simplemente, ¿cuándo se sale? Cuando es menor que la de arriba y el otro cuando los dos son, se sale. O en un *stop* que es el mínimo de cinco barras, son cinco semanas, vale. Solo haces, solo haces, nada más, semanal, es muy sencillo.

**Resultados del COT 1**

Esto funciona. Bueno, no va mal en muchos futuros, muchos futuros no va mal, no en todos. El número de operaciones pues que no es poco. En los de bolsa en general va bien. Pero digo, a lardes de sistemas estos sistemas no se optimiza nada, y cualquier análisis se hace conjunto, conjunto. Siempre se habrá que meter todos los futuros en tal y analizarlo. A lo mejor probar la salida por cuatro o cinco semanas, eso sí, pero con un montón de futuros dentro.

Está ahí en todos, acciones está ganando. Creo que el Dow Jones suele ir muy bien con con algunos generales y... Pero hay otros que pierde. El petróleo no va casi ninguno, en el petróleo no va casi ninguno. No me acuerdo mal. Bueno, ahí usted ya, usted ya... En el oro, algunos sí que van, otros no. Bueno, este parece que sí. A ver, solo va largo, está pensado más para bolsa. Solo va largo. Pero es también petróleo, en oro va bastante bien.

**Validación de los COT**

Bueno, eso es uno. Para el código, lo trabajáis, lo que si queréis. Pero existe una anécdota: al final estos sistemas, como puso los artículos, sirven para validar si hay algo. No, para mí es evidente que cualquier tema... Esto demuestra que va, hay algo.

**Timing de los datos COT**

Porque entender cómo es el *COT*, que no lo he explicado muy breve, vale. Los *COT* se publican al cierre de los viernes, pero son datos recogidos hasta martes, son datos recogidos hasta martes. Y tú por lo tanto te va a dar la señal aquí, cierre de esta vela. Esta semana va a coger el dato. Ahora, no, ahora va a acabar la semana, te va a coger el dato, no sabe si va al señal, te va a comprar la apertura de la siguiente vela.

Bueno, te va a poner el esto para entrar si le toca entrar central lunes o cuando sea. El martes va a quedar la entrada, porque va a quedar toda la semana puesta. El final pues es el máximo y te va a entrar con datos. Y hasta el cierre del viernes no va no va a cambiar la señal, hasta el cierre del viernes no va a cambiar. Vamos de semana en semana. A mí el viernes me da señal de comprar, me compra vamos a suponer el lunes, y yo hasta el viernes ahí voy feliz de la vida. Se va a hacer mucho riesgo, de solo para complementar carteras.

**COT 2 - Versión propia con Non Comerciales**

Esta versión es una versión totalmente propia, que no deja de ser un ejercicio de curioso por experiencia de seguir muchos años, donde me planteé... Digo que los *non comerciales*, los *non comerciales* son los que más *correlación* tienen con el precio. Si tú ves aquí el gráfico de *non comercial*, vas a ver este que tiene una bastante correlación con el precio. Cuando el precio sube, se sube, cuando el precio baja, baja. Se nota tendencias más o menos moderadas. Digo este, pez, ves ahí, mínimo para arriba, para arriba, para arriba, satura, lateral. Suele ir bastante. Tú analizas la correlación, es indicador, este tiene bastante correlación.

Entonces me planteé hacer algo con él, no con él al revés, siguiendo el precio al inverso de los otros. Hice unas reglas, es un ejercicio didáctico. Que compra, compra cuando es mayor que el *set trigger*, en este caso es mayor que 10, cuando sale de abajo, sale de abajo de la banda del *COT*. Es decir, compra aquí. Además le exijo que este sea positivo, porque el saldo de *non comerciales* por debajo de cero se considera bajista para el mercado.

**Reglas completas del COT 2**

Es entonces de cuando que este saldo sea positivo para... Una tarrela, ya digo, basada en ella, son bastantes. Que esté, que sea, o sea, que sea mayor que el *set trigger* de 10, pero menor que 90, es decir, que cuando ya esté sobrecomprado no compre, no compre. Y que sea positivo. Y además que el índice sea mayor que antes anterior, es el que el índice demuestra que esté subiendo, que haya tendencia en ese momento.

Compra tiene a favor un poco de seguimiento de precio. Y el corto al revés. Pero es que en el corto no van casi ninguno. En cambio el largo va bastantes. Y y bueno, para salir pues tiene tiene un canal también, lo mismo con el *PerAuto* anterior que usaba el *Rullero*. Y también tiene la señal contraria. Pero en esta no hay tantas reglas. Simplemente que cuando cruza el *non comercial* cruza por debajo del de 90, cuando vuelve de arriba, se sobrecompra y sale, se sale. O cuando es menor que, decir que eso es como una seguridad por si no ha llegado a cruzar. Cuando vuelve a entrar en sobrecomprar, se sale, o también si entra en negativo. Y esto, y lo inverso al comprar, claro.

**Resultados del COT 2**

Esto opera muchísimo, pero muchísimo, al seguir un poco el precio, pero muchísimo fatal, fatal. Pero bueno, por el largo en muchos tiene tiene *profit factor* positivo. Y bueno, sí sí que demuestra que tiene cierto sentido. Esto para nada recomiendo seguir investigándolo. Yo lo lo hice como un ejercicio didáctico.

Es aquí, en el largo aquí sí que hay bastantes operaciones en el largo. En la mayoría hay muchos que va largo, en el corto... Pero es que en el petróleo tampoco debe ir, porque costaba mucho que funcionara nada. Pot igual, este sí, mira, para no... Tampoco, tampoco, en el *natural gas* es bastante curioso, porque era era un futuro que es súper bajista de aquí. Hay mucho problema con el conocido *contango*, *van guards* en todo esto que os he contado.

**COT 2 en Natural Gas**

*Natural Gas*, en este, como era... Y ves, este, curiosamente en el *gas natural* funciona funciona razonablemente bien. Pero creo que también funciona este, que es solo largo, sonaba igual la otra porque hay varios, vale. Bien, es la primera versión, vale, en los dos versiones. Yo los códigos los voy a dar todos. No vamos a hacerme pendiente de... Repito, esto es ahí, vamos a hacer el *paper*. Esto es material de *bonus*. Está el código ahí, lo podéis abrir en *EasyLanguage*. Y esto lo queríamos dar como *bonus*, no es es código hecho nuestro, todo todo ello es propio y totalmente extra, no es un ejercicio un sistema luso, sino material de estudio. Esto es lo mismo, no es un sistema luso, vale.

**COT 3 - Sistema de Kaufman**

Este es lo mismo. Vimos el de la revista y de lo que se comentaba, lo programamos. Puede haber alguna cosa que no esté bien, ya digo, no hay que interpretarlas. Y podría ser que no estuviera bien. Esto, ya los que pilotéis de programación pues es verlo. Ahí está el código, he sacado la revista, os damos el artículo, y hemos tratado de ser fieles a su a su idea. Pero ya digo, como siempre en estas cosas explicadas, y más en una revista, pues hay cosas que hay que interpretarlas. Tienes, bueno, tienes al autor para preguntarle. Entonces al final pues ese es el tema.

Este es más complejo, tiene dos datas, es complicado, pero bueno, también lo mismo. En algunos van, otros no. Pasa lo mismo que los *comerciales*, en largo bastante bien, corto no tanto. Bueno, pues lo que os digo, depende depende de cuáles. Hay algunos que van mejor que otros. Es un poco complicado. Estamos en las tres horas 26 minutos en en directo.

**Pruebas con diferentes activos**

Es llegar a los dos... En el petróleo, pues en el petróleo, por ver si va alguno, cargando, que le pasa para estar a mucho cargando, a mucho cargar tampoco van... Este el oro es un poco más variable, lo gusta más, curiosamente es un poco más le ir allí. En la web acordaros que tenía unos puestos en su momento, lo cual pues ahora podéis ver cómo han ido después. Interesante, esto siempre es un dato de 2017, creo. Pues aquí en el oro vuelve, en largo pero no en el corto.

Y el *gas natural*, que siempre me da curiosidad, porque el *gas natural* es un activo realmente complejo. Cuando lo encuentre, aquí para el corto, para bajar mucho es... Ese día, el 2 y el 3 es de Kaufman, está en el libro de Kaufman, es más convencional.

**Características del sistema Kaufman**

Es verdad que tiene una cosa interesante, me gustó probarlo, es una cosa más interesante. Y tiene realmente muchísimo mérito lo que hace, por eso quizá para mí es de los más destacados. Porque en este caso sí que al de *Rullero* le implementamos esta salida, creo que ya la llevaba, este cambio no lleva nada, es simplemente la regla en bruto.

Opera poquísimo. Este sí que habría que meterlo en 200 futuros, pero muy poco, es una vela muy estricta. Mejor, se podía mirar de buscar a mejor periodos más cortos. Todo esto que veis, *offset*, tal, esto es es una función que pinta en el gráfico directamente, vale. TradeStation no permite que los sistemas pinten, y que eso es un truco. Es es un código, esto no es nuestro, están los foros de TradeStation, así os vendrá y tal, lo podéis abrir y utilizar. Creo que se utilizaba *arrays*, era... No, esa usa vectores en vez de *arrays*, que es más más eficiente, usaba vectores. Entonces al final esto lo que hace es pintar. El mismo código a veces satura poco el ordenador, pero es verdad que lo he ido mejorando.

**Lógica del COT 3 (Kaufman)**

Entonces, ¿qué hace el *COT 3*, vale, que es el de Kaufman, qué es lo que hace? Es un poco comprar igual, es decir, con los *COT Index* tienes el *COT Index* de *comerciales*, vale, de tenerlo todos, de *comerciales*, de los *comerciales*. Y aquí usa el *comercial anterior* que sea mayor que el *set trigger*, vale, que es mayor que ochenta. Es decir, un poquito parecido al que había de... No, bueno, será distinto. Este este compra más bien cuando se sobrecompra, no... Eso es, entra cuando se sobrecompra.

Pero además, esta es la curiosidad, no compra en contra del precio. Es decir, le pide que el cierre sea menor que el cierre de tres semanas, que haya caído un poco, sino no entra. Le pide las dos cosas, exige este *setup*. Es a medio curiosidad de comprar contra, porque además lo realmente destacable es que no tiene nada de salir.

**Salida del sistema Kaufman**

Sale por señal contraria en el sentido: cuando está largo, solo sale si el *COT* es menor que 40, el *COT Index*. Mientras no pasa eso, no se sale. Ni mínimos, ni máximos, ni *stop*, ni nada, vale. Yo aquí tengo puesto, pero no está activo si no recuerdo mal en ese día. No tengo... En algunos tengo puesto un elemento precreado de tres veces o no a tener de lo que sea. No, aquí no hay nada. Es decir, esto está comprando, saliendo solo cuando cae de 40.

Es una auténtica locura porque no tiene salida, no tiene salida. Es decir, va pelo, va pelo. Y por eso hacen algún futuro que tenga desastres. Pero realmente son poquísimos, en la mayoría gana dinero. En la mayoría, con muy pocos *trades*. Pero claro, es lo que decimos, al final es la misma regla. Solo utiliza los *COT*, está al final es el que más valida los *COT*.

**Resultados del sistema Kaufman**

Aquí, para que este del *NASDAQ* está en plano, podemos decir que. Ahora solo hay 10 operaciones, en el final hay poco histórico. Pero en términos generales, es 77 por ciento de acierto. Se ha marcado *setup* de entrada bastante bueno. Es verdad que dices "hombre, claro, pero es que la bolsa es esa, son activos alcistas". Sí, sí, es verdad, hay un sesgo a favor, un viento de cola. Pero bueno, el oro también ha subido, pero no no tanto.

Y además se aprecia. A este sí que lo metes en el *gas natural* y dices "hombre, aquí no puede ser que vaya", y efectivamente no va. Habría que buscar, sabría que buscar el contrario para estos, probarlo. Usamos el código a ver el inverso como en cortos para un activo bajista, probar de salidas.

**Mérito del sistema Kaufman**

Pero ya digo, es es realmente es realmente destacable, porque tienes otros activos que al final muchos, la mayoría de activos a largo plazo tienden a subir, eso es así. Pero que tiene tiene muy pocos *trades*. Pero es verdad que sí sí que se nota que el *setup* suele estar bastante afinado, lógicamente no siempre. Al final, oye, puede ser un número casual.

Y está el que más opera es el que hemos hecho nosotros, que se puede trabajar y pulir más. Y todos estos ejercicios no dejan de ser ejercicios académicos para el mercado y realizarlo. Y pueden ser filtros y bases para sistemas.

**Conclusión sobre los COT**

Porque para mí queda, en general queda bastante claro con todos los sistemas, cuando los trabajas bien, que sí que es verdad que los *COT* tienen algo predictivo, tienen algo predictivo. Pero claro, es una señal muy retrasada, y claro se tiene un precio, se tiene un precio, social muy muy lenta, por muy lenta. Pero sí que sí que parece haber algo algo ahí.

Esto, como nos lo habíais pedido, pues ya digo, subiré todo este material de los de los *COT*, subiré el código y los sistemas, y así os lo dejaré subido repositorio para aquel que lo quiera aprovechar, vale.

---

**Despedida del curso**

No veo preguntas, con lo cual despido lógicamente con unas palabras de despedida, vale. Que seguramente las mismas, o recordar que se os podía poner el vídeo del final de la teoría. Recuerdo, para insistir en ello, de acuerdo, lo dije mucho hasta por el marketing. No espero, creo que no ha pasado, pero por si alguien todavía queda que pensaba que hacer un curso con nosotros supondría ser al día siguiente, o sea hoy, *trader algorítmico profesional*, creo que sus expectativas no eran realistas, de acuerdo.

Yo creo que ha quedado un curso realmente potente. Por cierto, por favor, la encuesta que os va a llegar después, responderla, lo agradezco, lo agradezco mucho, y leeré todos vuestros comentarios con mucho interés.

**Recomendaciones finales**

Pero que tenéis que seguir trabajando. Volver a hacer el curso, por favor, entero, teoría, práctica. Podéis seguir preguntando, trataremos de responder a todo el mundo en el Discord. Por favor, poder ser aquí en la sección de pregunta aquí. Y aprovechar todo el material, hay mucho material.

Yo tengo la sensación, por las preguntas muchas veces, que todo el material no se ha visto. Pasa nada, no entiendo, también hay esta parte de la teoría, que es verdad que esto aquí parece como queda escondido. Pero todas, aquí, y te abre todo un montón de material de la teoría, de acuerdo. Materiales que vimos sobre la teoría, ves, todo. Cosas que salieron la teoría, las daba aquí. Yo que sé, los glosarios que estaban en los vídeos, si no estaban bien aquí en la evaluación. Todo material anexo 1 de estadística, el material estadística, todos aquí.

**Material disponible**

Ahí digo, porque tengo la sensación, no me acuerdo quién me lo dijo, que no que no había visto esto aquí. Puso manual extra de análisis técnico, vale. Todo esto por si alguien no lo había visto, quería recordarlo, porque sí que una persona me dijo que lo había visto. Y tenía la sensación por alguna pregunta que quizá no se había visto todo este material de teoría que hay aquí. Y por supuesto el de la práctica.

Yo creo que ahora no nos queda nada pendiente por subir, aparte de lo de hoy, aparte de lo de hoy. Pero así, por lo que fuera, pasará a faltar algo, por favor hacérnoslo saber. Y por supuesto que nos lo subiría, los, el está... Tiene bastante potencial, sobre todo por el libro. Pero yo, habiendo subido, pues por supuesto mirarlo.

**Material destacado**

El de *Strategy Concepts*, este es muy potente, de acuerdo, trabajarlo mucho, os recomiendo buscar. Y por supuesto el *buscador de entradas*, de entradas y salidas. Todo el material de filtros creo que al final quedó muy muy completo. Con algunos todos los doy por desarrollar, es decir, no nunca nunca pensábamos que salierais aquí con un montón de sistemas hechos para operar, aunque hay cosas que son para operar o que son casi para operar con 2, 3 toques, vale.

**Filosofía del curso**

Pero como es aquella frase, ¿no?, de que no me des el pescado sino enséñame a pescar, no... Es un poco eso. No sé si era así la frase, pero bueno, algo es. Se trata de daros las herramientas. Yo espero haberlo conseguido. Le he puesto todo todo el cariño.

Y quedamos a vuestra disposición. Recordar los jueves, por favor, los directos. Nada más. Ahora sí ya que me despido. Mañana os subiré todo el material de hoy. Os mando un abrazo muy fuerte. Y con esto acaba el curso de *trading algorítmico*. Un abrazo muy fuerte y espero veros por los mercados. ¡Hasta pronto! Chao.
