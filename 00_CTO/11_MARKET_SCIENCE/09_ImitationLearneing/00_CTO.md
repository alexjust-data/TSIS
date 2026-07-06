Sí. **Imitation Learning en trading sí existe**, pero el material serio está más concentrado en **portfolio management, optimal execution, market making, HFT simulada e IRL para inferir intención de gestores**, no tanto en “day trading small caps” directo.

## Qué buscar exactamente

Los términos buenos no son solo “imitation learning trading”, sino:

**behavior cloning trading**
**inverse reinforcement learning finance**
**learning from expert demonstrations trading**
**imitation learning optimal execution**
**imitative reinforcement learning market making**
**offline RL from expert policies trading**

## Papers fiables para empezar

**Base teórica obligatoria**

DAgger / imitation learning secuencial: explica por qué copiar decisiones como si fuera supervised learning falla cuando tus propias acciones cambian el estado futuro. Fundamental para trading. ([publications.ri.cmu.edu][1])

Survey serio de imitation learning: Osa, Pajarinen, Neumann, Bagnell, Abbeel, Peters. ([arXiv][2])

Inverse Reinforcement Learning clásico: Ng & Russell, recuperar la función de recompensa desde comportamiento observado. ([Stanford AI Lab][3])  

**Finance / trading directamente relacionado**  

  
- **MetaTrader: RL integrating diverse policies for portfolio optimization**. Usa imitation learning para aprender de varias políticas expertas y luego seleccionar según régimen de mercado. Muy relevante para tu idea TSIS de eventos/regímenes. ([arXiv][4])

- **IMM: Imitative Reinforcement Learning for Automatic Market Making**. Aplicación directa a market making. ([arXiv][5])

- **FlowHFT: Imitation Learning via Flow Matching Policy for HFT**. Muy moderno, 2025; aprende de múltiples estrategias expertas bajo distintos escenarios de mercado. ([arXiv][6])

- **FlowOE: Imitation Learning for Optimal Execution**. Muy relevante si quieres ejecución, slippage, órdenes grandes, impacto y timing. ([arXiv][7])

- **Combining RL and IRL for Asset Allocation Recommendations — Igor Halperin et al.** Recupera la intención/reward implícita de gestores desde su historial y luego usa RL para mejorar decisiones. ([arXiv][8])

- **Attention-Based Behavioral Cloning for Algorithmic Trading**. Behavior cloning con LSTM + attention aplicado a trading. ([ACM Digital Library][9])

- **Improving algorithmic trading consistency via human expertise**. Usa etiquetado experto + behavior imitation para estabilizar un agente. ([ScienceDirect][10])

- **Imitation Reward for Noisy Financial Environments**. Usa una señal experta para mejorar el reward en entornos financieros ruidosos. ([arXiv][11])

**Repos útiles**

- **FinRL Imitation Learning**: repo específico de AI4Finance. No es oro puro institucional, pero sirve para empezar. ([GitHub][12])

- **FinRL general**: framework de RL financiero con entornos, agentes y backtesting. ([GitHub][13])

- **AIRL Market Making**: aplicación de adversarial inverse RL a market making. ([GitHub][14])

## Vídeos / charlas más fiables

No hay muchos vídeos buenos específicamente de “imitation learning trading”. Los más serios que encontré son de **RL/IRL en finanzas**, especialmente Igor Halperin:

- *“Combining Reinforcement Learning and Inverse Reinforcement Learning…” / Igor Halperin**. Buena puerta de entrada a IRL financiero. ([YouTube][15])

- **“Machine Learning in Finance: From Theory to Practice”** menciona RL e IRL aplicado a modelado financiero. ([YouTube][16])

- **Zihao Zhang — Deep Learning for Market by Order Data** no es imitation learning puro, pero es muy relevante para microestructura/LOB. ([YouTube][17])

## Mi lectura para TSIS / small caps

Para tu caso, **imitation learning tiene mucho sentido**, pero no como “copiar al trader humano y ya está”. La forma seria sería:

1. Construir una **tabla de episodios/eventos**: gap, squeeze, VWAP reclaim, HOD break, SSR, liquidity stress, failed breakout.
2. Crear una **política experta inicial** desde reglas humanas o trades tuyos.
3. Hacer **behavior cloning** para aprender: estado → acción.
4. Validar si la política clonada generaliza fuera de muestra.
5. Luego usar **offline RL / AlphaEvolve / OpenEvolve** para mejorar sobre la política experta.
6. Comparar contra baseline humano, reglas simples y random policy.

La idea más potente para ti sería:

**Imitation Learning = aprender la “intuición operativa” inicial.  
Offline RL / AlphaEvolve = intentar superar esa intuición bajo control estadístico.**

Esto encaja muy bien con tu Event Library.


[1]: https://publications.ri.cmu.edu/storage/publications/pub_files/2011/4/Ross-AISTATS11-NoRegret.pdf?utm_source=chatgpt.com "A Reduction of Imitation Learning and Structured ..."
[2]: https://arxiv.org/abs/1811.06711?utm_source=chatgpt.com "An Algorithmic Perspective on Imitation Learning"
[3]: https://ai.stanford.edu/~ang/papers/icml00-irl.pdf?utm_source=chatgpt.com "Algorithms for Inverse Reinforcement Learning"
[4]: https://arxiv.org/abs/2210.01774?utm_source=chatgpt.com "MetaTrader: An Reinforcement Learning Approach Integrating Diverse Policies for Portfolio Optimization"
[5]: https://arxiv.org/abs/2308.08918?utm_source=chatgpt.com "IMM: An Imitative Reinforcement Learning Approach with ..."
[6]: https://arxiv.org/abs/2505.05784?utm_source=chatgpt.com "FlowHFT: Imitation Learning via Flow Matching Policy for ..."
[7]: https://arxiv.org/html/2506.05755v1?utm_source=chatgpt.com "FlowOE: Imitation Learning with Flow Matching for Optimal ..."
[8]: https://arxiv.org/abs/2201.01874?utm_source=chatgpt.com "Combining Reinforcement Learning and Inverse Reinforcement Learning for Asset Allocation Recommendations"
[9]: https://dl.acm.org/doi/10.1007/s10489-024-06064-y?utm_source=chatgpt.com "Attention-Based Behavioral Cloning for algorithmic trading"
[10]: https://www.sciencedirect.com/science/article/abs/pii/S0957417424012168?utm_source=chatgpt.com "Improving algorithmic trading consistency via human ..."
[11]: https://arxiv.org/html/2411.08637v1?utm_source=chatgpt.com "Imitation Reward for Noisy Financial Environments"
[12]: https://github.com/AI4Finance-Foundation/FinRL_Imitation_Learning?utm_source=chatgpt.com "AI4Finance-Foundation/FinRL_Imitation_Learning"
[13]: https://github.com/AI4Finance-Foundation/FinRL?utm_source=chatgpt.com "FinRL®: Financial Reinforcement Learning. ..."
[14]: https://github.com/JurajZelman/airl-market-making?utm_source=chatgpt.com "JurajZelman/airl-market-making: The official repository for ..."
[15]: https://www.youtube.com/watch?v=-_JwRqTUUjs&utm_source=chatgpt.com "Combining Reinforcement Learning and Inverse ..."
[16]: https://www.youtube.com/watch?v=HizcRBqeXR8&utm_source=chatgpt.com "\"Machine Learning in Finance: From Theory to Practice\" with ..."
[17]: https://www.youtube.com/watch?v=yqccDoujAUc&utm_source=chatgpt.com "Zihao Zhang (Oxford-Man Institute) - \"Deep Learning for ..."



# agente 1

![](img/001.png)


Sí. De hecho, creo que has encontrado **una de las líneas más interesantes que existen ahora mismo** para TSIS.

La diapositiva que has puesto es de **Igor Halperin**, probablemente el investigador que más ha trabajado en unir **IRL + RL** para finanzas.

Los dos últimos puntos son muchísimo más interesantes que el primero.

---

### 1. Inverse Reinforcement Learning (IRL) para aprender de gestores

La idea es elegantísima.

En vez de preguntar:

> ¿Qué política es buena?

preguntas:

> **¿Qué objetivo está optimizando este gestor?**

Es decir:

```text
Estados

↓

Acciones del gestor

↓

IRL

↓

Reward implícito
```

No observas la recompensa.

La reconstruyes.

Eso es IRL.

---

Por ejemplo.

Observas durante diez años un fondo.

Nunca sabes exactamente qué intenta hacer.

Pero ves:

```text
estado A

compra

estado B

vende

estado C

espera

...
```

IRL intenta responder:

> ¿Qué función de utilidad haría que ese comportamiento fuese óptimo?

Eso es muchísimo más potente que copiar acciones.

---

#### Paper principal

**Combining Reinforcement Learning and Inverse Reinforcement Learning for Asset Allocation Recommendations**

Autores:

* Igor Halperin
* Jiayu Liu
* Xiao Zhang

Es probablemente el paper más importante sobre este tema en finanzas. El flujo es:

1. IRL aprende la función de recompensa implícita de los gestores a partir de su historial.
2. Esa recompensa se usa como objetivo para un agente RL.
3. El agente optimiza una política que mejora el rendimiento observado de los gestores. ([arXiv][1])

---

### 2. RL para mejorar al humano

Aquí está la magia.

No quieren sustituir al gestor.

Quieren hacer:

```text
Gestor experto

↓

IRL

↓

Reward

↓

RL

↓

Nueva política
```

Es decir:

```text
copiar

↓

comprender

↓

mejorar
```

No es Behavior Cloning.

Es muchísimo más potente.

---

### Vídeos imprescindibles

#### 1) Reinforcement Learning and its Inverse: Applications for Finance

Duración:

≈52 minutos.

Es probablemente **el mejor vídeo existente** sobre este tema.

[YouTube – Reinforcement Learning and its Inverse: Applications for Finance (Igor Halperin)](https://www.youtube.com/watch?v=-_JwRqTUUjs&utm_source=chatgpt.com)

([YouTube][2])

---

#### 2) Machine Learning in Finance: From Theory to Practice

También de Halperin.

Habla de:

* RL
* IRL
* reward
* portfolio
* aplicaciones reales

[YouTube – Machine Learning in Finance: From Theory to Practice](https://www.youtube.com/watch?v=HizcRBqeXR8&utm_source=chatgpt.com)

([YouTube][3])

---

#### 3) ODSC Talk

Muy recomendable.

Explica:

* qué es IRL
* por qué usarlo en finanzas
* aplicaciones

[ODSC – Inverse Reinforcement Learning for Financial Applications](https://odsc.com/speakers/reinforcement-learning-and-inverse-reinforcement-learning-in-finance/?utm_source=chatgpt.com)

([Open Data Science Conference][4])

---

### Capítulos y guías

El mejor resumen moderno es el capítulo del **CFA Institute**:

**Reinforcement Learning and Inverse Reinforcement Learning: A Practitioner's Guide for Investment Management**

Autores:

* Halperin
* Kolm
* Ritter

Resume exactamente la filosofía que buscas: usar IRL para capturar el conocimiento de expertos y RL para refinarlo bajo restricciones reales de riesgo y validación. ([CFA Institute Research and Policy Center][5])

---

### Papers relacionados

Además del principal, leería:

* **Recent Advances in Reinforcement Learning in Finance** (Hambly et al.), una revisión muy completa sobre RL en ejecución, market making y optimización de carteras. ([ORA][6])
* **The Evolution of Reinforcement Learning in Quantitative Finance**, un survey de 2025 que revisa 167 trabajos y sitúa RL, offline RL e imitation learning en el contexto financiero moderno. ([arXiv][7])

---

### Lo que más me interesa para TSIS

Creo que aquí hay una idea que encaja extraordinariamente bien con la arquitectura que llevas construyendo.

Imagina que ya tienes:

```text
Event Library

↓

Event Table

↓

State Snapshot
```

Y además guardas **tus propias decisiones** durante años:

```text
estado

↓

acción

↓

resultado
```

Entonces podrías hacer algo que apenas he visto aplicado en trading discrecional de small caps:

```text
Tus operaciones

↓

IRL

↓

Aprender cuál era realmente
tu función de recompensa

↓

Offline RL

↓

Buscar una política mejor

↓

AlphaEvolve

↓

Seguir refinándola
```

Es decir, **no enseñarías a la IA únicamente "qué hiciste"**, sino que intentarías inferir **qué criterio implícito seguías al decidir** (tu tolerancia al riesgo, preferencia por determinados contextos, paciencia, etc.) y después optimizarlo.

Desde un punto de vista de investigación, me parece una de las direcciones más originales que podrías explorar dentro de TSIS, especialmente porque tu sistema ya está diseñado alrededor de estados, eventos y decisiones, que es exactamente la estructura que requieren IRL y RL.

[1]: https://arxiv.org/abs/2201.01874?utm_source=chatgpt.com "Combining Reinforcement Learning and Inverse Reinforcement Learning for Asset Allocation Recommendations"
[2]: https://www.youtube.com/watch?v=-_JwRqTUUjs&utm_source=chatgpt.com "Combining Reinforcement Learning and Inverse ..."
[3]: https://www.youtube.com/watch?v=HizcRBqeXR8&utm_source=chatgpt.com "\"Machine Learning in Finance: From Theory to Practice\" with ..."
[4]: https://odsc.com/speakers/reinforcement-learning-and-inverse-reinforcement-learning-in-finance/?utm_source=chatgpt.com "Inverse Reinforcement Learning for Financial Applications"
[5]: https://rpc.cfainstitute.org/research/foundation/2025/chapter-6-reinforcement-learning-inverse-reinforcement-learning?utm_source=chatgpt.com "Chapter 6: Reinforcement Learning and Inverse ..."
[6]: https://ora.ox.ac.uk/objects/uuid%3A45234c44-2874-4666-b273-38ee57d6be50/files/rp5547s30v?utm_source=chatgpt.com "Recent advances in reinforcement learning in finance"
[7]: https://arxiv.org/html/2408.10932v3?utm_source=chatgpt.com "The Evolution of Reinforcement Learning in Quantitative ..."


# Agente 1

```text
en "cuál era realmente tu función de recompensa" no entiendo realmente "recompensa"
```


Esta es, probablemente, **la idea más difícil de entender de todo Reinforcement Learning**. Una vez la entiendes, IRL cobra muchísimo sentido.

#### Primero: ¿qué es una recompensa (reward)?

En RL, la recompensa **no es dinero**.

Es una función matemática que dice al agente:

> **"Esto está bien"** o **"esto está mal"**.

Por ejemplo, en un videojuego:

```text
Matar enemigo     +10

Morir            -100

Coger moneda      +1

Llegar a meta   +1000
```

Eso es la función de recompensa.

El agente intenta maximizar la suma de recompensas.

---

##### En trading parece obvio...

Uno podría pensar:

```text
Reward = PnL
```

Pero eso casi nunca es la realidad.

Imagina dos traders.

##### Trader A

Siempre busca:

* ganancias pequeñas
* stop pequeño
* salir rápido

##### Trader B

Aguanta muchísimo.

Busca:

* movimientos enormes
* acepta drawdowns grandes

Los dos pueden terminar el año ganando exactamente:

```text
+100.000$
```

Pero claramente **no están optimizando lo mismo**.

---

#### Entonces...

El dinero observado es el resultado.

Pero la recompensa interna puede ser distinta.

Por ejemplo.

Trader A realmente optimiza algo parecido a:

```text
Reward =
Beneficio
-
0.5 × Tiempo en mercado
-
2 × Riesgo
```

Mientras Trader B podría optimizar:

```text
Reward =
Beneficio
-
0.1 × Riesgo
+
0.8 × Capturar grandes tendencias
```

Nunca escribieron esas ecuaciones.

Simplemente actúan así.

---

### Aquí entra IRL

IRL dice:

"No conozco esa ecuación."

Solo observo:

```text
Estado

↓

Acción del trader
```

Miles de veces.

Y pregunta:

> **¿Qué función de recompensa haría que esas acciones fueran las óptimas?**

Es como un detective.

---

### Un ejemplo mucho más intuitivo

Imagina que observas a un padre educando a su hijo.

Nunca le preguntas por qué hace las cosas.

Solo ves:

```text
El niño rompe algo

↓

El padre no grita
```

Otro día:

```text
El niño pega

↓

El padre sí castiga
```

Otro:

```text
El niño ayuda

↓

El padre sonríe
```

Después de cientos de observaciones puedes empezar a deducir:

> Este padre valora mucho el respeto.

Eso sería su "reward".

Nunca lo escribió.

Lo inferiste.

Eso hace IRL.

---

### Ahora llevado a TSIS

Supongamos que durante cinco años registras absolutamente todo.

Para cada operación guardas:

```text
Estado

Gap

Float

PM Volume

Sector

VWAP

L2

Tape

Spread

SSR

...
```

Después:

```text
Acción

Entrar

No entrar

Esperar

Añadir

Salir

Cancelar
```

Y además:

```text
Resultado

PnL

MAE

MFE

Duración

Slippage
```

Tú nunca escribes reglas como:

```text
Si gap > 50

entonces comprar
```

Simplemente operas.

---

#### Entonces IRL observa

Miles de ejemplos como:

```text
Estado A

↓

Compras
```

```text
Estado B

↓

No compras
```

```text
Estado C

↓

Esperas
```

Y empieza a descubrir cosas como:

> "Curiosamente, Alex casi nunca entra cuando el spread supera cierto umbral."

O:

> "Da muchísimo peso al volumen premarket."

O:

> "Evita entrar cuando detecta absorción en el ask."

Tú nunca escribiste eso.

Pero tus decisiones lo revelan.

---

### Entonces, ¿qué significa "aprender tu reward"?

No significa descubrir que:

```text
Reward = dinero
```

Significa descubrir **qué criterio estabas utilizando realmente para decidir**.

Podría inferir algo como:

```text
Reward ≈

+ Alta probabilidad de squeeze
+ Volumen creciente
+ Riesgo bajo
- Spread amplio
- Liquidez pobre
- Noticias dudosas
```

No tiene por qué ser una fórmula simple. En la práctica suele ser una función muy compleja del estado del mercado.

---

### Y aquí viene la parte más interesante

En realidad, **IRL no está intentando copiar tus acciones**.

Está intentando responder a una pregunta mucho más profunda:

> **¿Qué objetivo implícito estabas persiguiendo cuando tomabas esas decisiones?**

Una vez obtiene una aproximación de ese objetivo, entra el siguiente paso:

```text
Tus operaciones

↓

IRL

↓

Función de recompensa aproximada

↓

Offline RL

↓

"Si este era el objetivo,
¿existe una política mejor
que la que seguía Alex?"
```

Esa diferencia es enorme.

* **Behavior Cloning** aprende: *"Alex hizo X, así que hago X."*
* **Inverse RL** aprende: *"Alex intentaba maximizar Y."*
* **Offline RL** busca: *"¿Puedo maximizar Y mejor que Alex?"*

Y esa transición, desde imitar acciones a inferir objetivos y luego optimizarlos, es precisamente lo que hace que esta línea de investigación sea tan potente para un proyecto como TSIS.



# Agente 1


Alex, esta pregunta me parece excelente porque, de hecho, estás describiendo algo que **no es exactamente IRL**, pero está muy cerca y puede convertirse en un sistema de investigación muy potente.

Mi respuesta corta es:

> **Sí, científicamente tiene muchísimo valor. Pero el valor depende de cómo representes esas marcas.**

Voy a explicarlo.

---

**Lo que tú harías**

Imagina un squeeze.

Generas automáticamente un PNG.

Después, tranquilamente, sin presión del mercado, dibujas:

```text
      ↑ salida

      │
      │
      │
      ● entrada

──────────────
```

O incluso:

```text
entrada1

↓

salida1

↓

entrada2

↓

salida2

↓

entrada3

↓

salida3
```

Haces eso 2.000 veces.

Eso genera una base de datos enorme.

---

**¿Qué son realmente esas marcas?**

No son imágenes.

Las imágenes son solo la interfaz humana.

Las marcas representan:

```text
estado

↓

acción humana
```

Por ejemplo:

```text
09:31:15

Estado #18472

↓

ENTRAR LONG
```

Luego

```text
09:31:42

Estado #18501

↓

AÑADIR
```

Luego

```text
09:32:10

Estado #18538

↓

SALIR 30%
```

etc.

Las líneas dibujadas deben transformarse en acciones temporales sobre estados concretos.

---

**Entonces...**

Tu dataset sería algo así:

| Estado | Acción humana |
| ------ | ------------- |
| s₁     | entrar        |
| s₂     | mantener      |
| s₃     | añadir        |
| s₄     | salir 25%     |
| s₅     | mantener      |
| s₆     | salir         |

Eso ya es un dataset de demostraciones.

---

## ¿Eso sirve para Behavior Cloning?

Sí.

Perfectamente.

Porque tienes

```text
estado

↓

acción
```

Eso es exactamente lo que necesita Behavior Cloning.

---

## ¿Sirve para IRL?

Aquí viene el matiz importante.

No directamente.

Porque IRL intenta inferir

```text
estado

↓

acción

↓

¿qué recompensa hacía racional esa acción?
```

Pero...

Si tienes miles de demostraciones coherentes...

Sí es suficiente para aplicar IRL.

De hecho, así funcionan muchos trabajos.

---

## Lo importante

La gente piensa que IRL necesita:

```text
estado

acción

reward
```

No.

Precisamente NO conoce el reward.

Solo observa:

```text
estado

↓

acción
```

Miles de veces.

Y reconstruye el reward.

---

## Lo que me gusta muchísimo de tu idea

Hay una cosa muy inteligente.

Tú NO estás copiando operaciones reales.

Estás etiquetando

> **la operación que un experto considera correcta.**

Eso elimina muchísimo ruido.

Porque durante el trading real influyen:

* estrés
* cansancio
* llamadas
* errores
* miedo
* FOMO
* ejecución mala

Mientras que aquí dices:

> "Si pudiera volver atrás, haría esto."

Eso es una demostración mucho más limpia.

En robótica esto se llama **expert demonstration**.

Y es muy valiosa.

---

## Pero yo haría una mejora enorme

No guardaría solamente:

```text
entrada

salida
```

Guardaría TODA la secuencia.

Por ejemplo:

```text
09:31:10

esperar

09:31:11

esperar

09:31:12

esperar

09:31:13

esperar

09:31:14

comprar

09:31:15

mantener

09:31:16

mantener

09:31:17

añadir

09:31:18

mantener

09:31:19

salir parcial

09:31:22

salir final
```

Eso es muchísimo más rico.

---

## ¿Y si además tienes tu Event Library?

Entonces aparece algo precioso.

Tu dataset sería

```text
Evento

↓

Estado

↓

Acción experta

↓

Estado

↓

Acción experta

↓

Estado

↓

Acción experta
```

Eso ya es prácticamente una colección de trayectorias.

En RL se llaman

```text
trajectories
```

Y son exactamente el tipo de datos que usan:

* Behavior Cloning
* IRL
* Offline RL

---

## Donde creo que puedes ir incluso más lejos

Aquí es donde creo que puedes hacer algo que **no he visto en la literatura aplicada al trading discrecional**.

En vez de guardar solo la acción, guarda también **la intención**.

Por ejemplo:

```text
Estado

↓

Entrar

Motivo:

"Espero ruptura del HOD porque veo absorción en el ask y aceleración del tape."
```

O:

```text
Salir parcial

Motivo:

"Ha aparecido una pared de liquidez y el impulso empieza a agotarse."
```

Eso ya no es solo aprendizaje por demostración. Estás añadiendo una **capa semántica** sobre la decisión. Esa información podría utilizarse para:

* validar si la política aprendida coincide con tu razonamiento,
* estudiar cuándo tu criterio cambia según el contexto,
* e incluso comparar lo que "dice" tu razonamiento con lo que IRL infiere como función de recompensa.

## Mi única advertencia científica

Hay un detalle que cuidaría mucho.

Si tú dibujas **la entrada perfecta conociendo todo lo que ocurrió después**, introduces información del futuro. Eso convierte las demostraciones en *hindsight demonstrations* (demostraciones hechas con retrospectiva), no en decisiones que realmente podrían haberse tomado en ese instante.

Para que el dataset sea científicamente sólido, cada acción debería cumplir esta regla:

> **La decisión debe poder justificarse utilizando únicamente la información disponible en ese momento.**

Es decir, cuando marques una entrada en el minuto 09:31:14, el sistema solo debería tener acceso al estado del mercado hasta las 09:31:14, nunca a lo que pasó a las 09:35.

Si respetas esa restricción, entonces sí: un conjunto de unas **2.000 trayectorias expertas**, alineadas con los estados de TSIS y sin fuga de información, sería un dataset de muchísimo valor para investigar **Behavior Cloning, Inverse Reinforcement Learning y Offline Reinforcement Learning** de una forma metodológicamente muy seria. Creo que, para tu proyecto, es una de las ideas con más potencial.


# agente 1

```
con esto "La decisión debe poder justificarse utilizando únicamente la información disponible en ese momento." te refieres a cuadno entra en juego el sistema,,, verdad? no cuando yo hago las marcas.....
```

**Exactamente. Has entendido el matiz correcto.**

No me refiero al momento en que tú, semanas después, estás analizando el gráfico y haciendo las marcas.

Me refiero al **instante que representará el sistema cuando aprenda**.

### Tu proceso sería algo así

#### Fase 1 (offline, tú como experto)

Coges un gráfico histórico completo.

Lo estudias con calma.

Marcas:

* entrada
* salida
* añadidos
* parciales

No pasa nada porque estés viendo todo el gráfico. De hecho, eso es una ventaja: puedes etiquetar con mucha más calidad que operando en tiempo real.

---

#### Fase 2 (construcción del dataset)

Ahora llega la parte importante.

Supongamos que has marcado una entrada aquí:

```text
09:31:24   ← entrada
```

Cuando generes el ejemplo para IA, **no debes darle esto**:

```text
09:31:24

↓

todo el gráfico hasta las 10:15
```

Porque entonces el modelo "vería el futuro".

Debe recibir únicamente:

```text
09:31:24

↓

todo lo ocurrido
hasta las 09:31:24
```

Y la etiqueta será:

```text
Acción = Entrar
```

Eso es científicamente correcto.

---

### Otro ejemplo

Imagina este gráfico:

```text
09:30

↓

09:31

↓

09:32   ← tú marcas entrada

↓

09:35

↓

09:40

↓

09:50

↓

09:55   ← salida
```

Cuando entrenes el modelo:

El ejemplo de entrada será

```text
Estado en 09:32

↓

Entrar
```

NO

```text
Estado 09:32

+

todo lo que ocurrió
hasta las 09:55
```

---

## ¿Entonces puedo mirar el futuro para etiquetar?

**Sí.**

Y esto es muy importante.

En aprendizaje por demostración, el experto puede usar retrospectiva para producir demostraciones de alta calidad.

Eso **no invalida** el dataset.

Lo que invalida el dataset es que **el algoritmo**, durante el entrenamiento, tenga acceso a información que en la realidad no existiría en el momento de decidir.

---

## De hecho, yo iría un paso más allá en TSIS

Creo que ni siquiera deberías guardar una simple marca en el PNG.

Yo almacenaría algo como esto:

```yaml
event_id: 18472

timestamp: 09:31:24

state_snapshot_id: 839201

expert_action:
    type: BUY

confidence: 0.92

reason:
    "Primer pullback sano tras squeeze"

future_used_for_label:
    true
```

¿Por qué pondría `future_used_for_label: true`?

Porque es **honesto científicamente**. Estás diciendo:

> "La etiqueta fue creada por un experto revisando el episodio completo."

Eso no significa que el modelo vea el futuro. Significa que **el experto utilizó retrospectiva para decidir cuál habría sido la mejor acción**.

---

## De hecho, creo que aquí hay una oportunidad muy interesante para TSIS

Tu idea no es exactamente crear un dataset de *trades ejecutados*. Es crear un dataset de **demostraciones expertas ideales** (*expert demonstrations*).

Eso tiene una ventaja enorme: elimina errores de ejecución, miedo, FOMO, despistes o limitaciones humanas. Estás enseñando al modelo **cómo habría actuado un experto en condiciones ideales**, siempre que cada acción esté asociada únicamente al estado disponible en ese instante.

Esa diferencia es sutil, pero desde el punto de vista de investigación es muy importante y, en mi opinión, hace que el enfoque sea incluso más interesante que aprender de un simple historial de operaciones reales.

