# Filosofía de Investigación de TSIS

## 1. Qué estamos construyendo

TSIS no es un backtester aislado, ni una colección de setups discrecionales convertidos en scripts, ni un experimento de machine learning sobre velas.

TSIS es un sistema propietario de investigación, representación, validación y decisión sobre el mercado de microcaps y small caps, construido para transformar datos históricos y datos live en estados de mercado útiles, explicables y operativamente explotables.

El objetivo no es simplemente encontrar setups que ganen dinero.
El objetivo es identificar dinámicas reales, invariantes y explotables del mercado, y convertirlas en decisiones robustas bajo incertidumbre.

La ambición del proyecto se despliega en tres capas conectadas:

1. `01_TSIS_backtest_SmallCaps`
   Investigación, auditoría, simulación, edge estadístico y arquitectura de backtesting.
2. `02_TSIS_webSocket_SmallCaps`
   Captura live, features en tiempo real, event engine, signal routing, execution bridge y monitorización de riesgo.
3. `03_TSIS_Offline_RL`
   Aprendizaje secuencial, behavioral cloning, offline RL, evaluación de políticas y candidatos de despliegue.

TSIS debe entenderse como un stack cuantitativo completo, no como un script de señales.

---

## 2. La tesis central

La hipótesis fundacional de TSIS es esta:

El mercado observable no es el objeto real.
Precio y tiempo son una proyección pobre de una dinámica más profunda.

Lo que realmente queremos modelar no son solo barras, indicadores o retornos aislados, sino:

- atención;
- liquidez;
- agresión compradora y vendedora;
- compresión o expansión del spread;
- presión short;
- fragilidad del libro;
- eventos regulatorios;
- corporate actions;
- cambios de identidad;
- contexto informacional;
- transiciones de régimen.

En microcaps, los movimientos extremos rara vez se explican bien desde una sola variable.
Se explican mejor como secuencias causales y microestructurales.

Ejemplo conceptual:

`news/catalyst -> atención -> RVOL -> estrechamiento del spread o vacío de liquidez -> breakout/squeeze -> riesgo de halt -> agotamiento -> colapso o continuación`

TSIS existe para modelar estas dinámicas con trazabilidad, no para decorar gráficos con indicadores.

---

## 3. Qué creemos sobre los datos

### 3.1. Sin datos defendibles no hay research defendible

La auditoría y certificación de datos no es trabajo auxiliar.
Es el cimiento del sistema.

No aceptamos como input operativo ningún dataset cuya semántica, cobertura, calidad y límites de uso no estén claros.

Por eso cada bloque de datos debe responder tres preguntas:

- `expected`: cuándo debería existir ese dato;
- `present`: cuándo existe físicamente;
- `healthy`: cuándo es utilizable bajo una política de calidad explícita.

Y además una cuarta:

- `usable`: para qué uso queda aprobado: `backtest_core`, `research`, `ml_primary`, `ml_flagged`, `forensic`, etc.

### 3.2. No existe “la data”; existen capas con roles distintos

Cada dataset tiene un rol funcional específico.

- `daily` y `ohlcv_1m`: verdad agregada de precio y volumen.
- `quotes`: estado microestructural visible del libro.
- `trades`: tape y prints observados, con sus propios problemas de comparabilidad y elegibilidad.
- `halts`: verdad del evento regulatorio o del venue.
- `reference`: verdad de identidad, existencia temporal y corporate actions.
- `short`: contexto de crowding y presión short.
- `additional`: fundamentals, news, IPOs, macro y contexto ampliado.

TSIS prohíbe mezclar estas capas como si fueran equivalentes.

### 3.3. La calidad no es binaria

Muchos bloques no se dividen solo en válido e inválido.
Se dividen en:

- `good`
- `review`
- `bad`

Y, cuando procede, también en:

- `recoverable_with_flag`
- `review_not_rehabilitated`
- `quarantine`

La filosofía del proyecto no es maximalista ni ingenua:
no excluimos todo lo imperfecto, pero tampoco promovemos a core lo que solo es tolerable con contexto.

---

## 4. Qué creemos sobre el mercado

### 4.1. El mercado no evoluciona principalmente en clock time

Para TSIS, el tiempo cronológico es una conveniencia, no la ontología del mercado.

El mercado, especialmente en microcaps, evoluciona en `event time`:

- bursts de volumen;
- cambios abruptos de spread;
- halts;
- absorción;
- failure o reclaim de niveles;
- prints agresivos;
- vacíos de liquidez;
- secuencias de squeeze y exhaustion.

Dos velas de un minuto pueden ser estructuralmente incomparables.
Por eso el sistema debe evolucionar hacia representaciones basadas en eventos, actividad e información, no solo en particiones temporales rígidas.

### 4.2. El gráfico clásico es útil para humanos, insuficiente para el sistema

Los gráficos OHLC son una interfaz de compresión visual.
No son una representación suficiente del mercado.

TSIS parte de que:

- el precio solo no basta;
- el volumen solo no basta;
- el retorno solo no basta;
- las velas no son el estado.

El estado del mercado debe enriquecerse con microestructura, reference, contexto causal, calidad de liquidez y régimen.

### 4.3. Los setups no son formas; son transiciones de estado

`gap and go`, `gap and crap`, `short into resistance`, `first red day`, `parabolic fade`, `VWAP reclaim`, `halt continuation`:
nada de eso debe modelarse como un dibujo.

Cada setup debe entenderse como una transición secuencial de estados de mercado bajo restricciones de liquidez, atención y riesgo.

---

## 5. Qué creemos sobre edge

### 5.1. Edge no es una curva bonita

Un backtest rentable no demuestra una hipótesis económica.
Solo demuestra que una regla produjo un resultado sobre un conjunto de datos bajo ciertos supuestos.

TSIS rechaza explícitamente:

- p-hacking;
- parameter mining sin estructura;
- selección oportunista de ventanas;
- validación IID falsa;
- leakage temporal;
- optimización retrospectiva disfrazada de descubrimiento.

### 5.2. El edge no es una constante; es una distribución incierta

No existe “el edge” como una entidad fija.
Existe una distribución incierta sobre la capacidad de un mecanismo para sobrevivir a:

- cambios de régimen;
- degradación temporal;
- spreads;
- slippage;
- capacidad limitada;
- halts;
- borrow constraints;
- no estacionariedad;
- cambios de composición del universo.

La pregunta correcta no es:

“¿gana?”

La pregunta correcta es:

“¿qué mecanismo explica este resultado, cuán estable parece, en qué régimen vive, y cómo se degrada bajo supuestos más duros?”

### 5.3. Buscamos mecanismos, no solo asociaciones

Asociación no es causalidad.

Si una variable aparece correlacionada con un resultado, TSIS exige preguntarse:

- ¿es causa?
- ¿es consecuencia?
- ¿es mediadora?
- ¿es confounder?
- ¿es solo una sombra observable de algo más profundo?

En microcaps, muchas señales visibles son residuos de mecanismos ocultos:

- atención;
- fragilidad del libro;
- presión short;
- calidad del catalyst;
- colapso de liquidez;
- retirada de market makers;
- participantes atrapados.

La investigación debe intentar acercarse a esos mecanismos, no enamorarse de proxies superficiales.

---

## 6. Invariantes y representación

### 6.1. El problema central es encontrar invariantes

Si una variable no es suficientemente estable, no puede sostener aprendizaje útil del pasado.

TSIS considera que una parte central del research consiste en identificar qué objetos son más invariantes que el precio bruto:

- retornos;
- spreads normalizados;
- estados de liquidez;
- patrones de transición evento -> respuesta;
- relaciones entre RVOL, spread y agresión;
- secuencias halt -> reopen -> continuation/failure;
- distancias a niveles bajo condiciones concretas de actividad.

La evolución del proyecto debe moverse desde features ingenuas hacia invariantes más defendibles.

### 6.2. El estado debe ser compacto, no arbitrario

El espacio observable del mercado es de muy alta dimensión.
No todo debe pasar crudo al modelo.

TSIS debe tender hacia:

- reducción de dimensión;
- separación entre ruido y estructura;
- construcción de estados compactos;
- representación de factores latentes;
- embeddings o hidden states cuando estén mejor justificados que las variables brutas.

No buscamos “muchas features”.
Buscamos estados con significado operativo.

---

## 7. Qué creemos sobre ML y RL

### 7.1. ML financiero no es sklearn sobre velas

Los datos financieros no son IID.
Tienen dependencia temporal, drift, reflexividad, feedback y leakage por todas partes.

Por eso TSIS adopta una postura conservadora:

- validación temporal estricta;
- purged CV y embargo cuando aplique;
- meta-labeling cuando tenga más sentido que la clasificación bruta;
- etiquetado consistente con triple barrera o reglas de invalidez económica;
- interpretación cauta de feature importance;
- separación explícita entre señal, ejecución y riesgo.

### 7.2. Primero detectar setups, luego decidir si vale la pena operarlos

Una convicción fuerte del proyecto es que, en este nicho, los modelos no deben empezar inventando trading desde cero.

La jerarquía correcta suele ser:

1. detectar contextos y setups;
2. estimar calidad o expectancy;
3. decidir si operar ese caso;
4. optimizar ejecución;
5. aplicar riesgo externo.

Esa filosofía encaja naturalmente con `meta-labeling`, `behavioral_cloning` y más adelante `offline RL`.

### 7.3. RL no sustituye la estructura; se apoya en ella

TSIS no parte de la fantasía de “hacer un AlphaGo del trading” sin más.

La posición del proyecto es más precisa:

- el mercado no es Go;
- no hay simulador perfecto;
- la no estacionariedad es brutal;
- la señal es débil y el slippage importa;
- pero sí hay decisiones secuenciales, estados y rewards útiles.

Por tanto, el papel de RL en TSIS no es mágico.
Es una capa posterior, apoyada sobre:

- datos auditados;
- estados de mercado bien definidos;
- políticas de riesgo fuertes;
- behavioral cloning;
- offline evaluation seria;
- simulación más realista que la habitual.

---

## 8. Ejecución y riesgo

### 8.1. Una señal sin ejecución realista no vale

En microcaps, el mayor enemigo del backtest no es solo el overfitting.
Es la ficción de ejecución.

Por eso TSIS debe modelar explícitamente:

- bid/ask;
- spread;
- slippage;
- fills parciales;
- volumen utilizable;
- borrows y locates;
- SSR;
- halts;
- restricciones de capacidad.

La señal puede ser correcta y el trade inviable.
El sistema debe saber la diferencia.

### 8.2. El risk engine debe poder vetar al modelo

El modelo no tiene autoridad soberana.
La gestión de riesgo es una capa externa y prioritaria.

Cualquier política o señal puede ser degradada, limitada o anulada por:

- spread excesivo;
- liquidez insuficiente;
- riesgo de halt;
- riesgo diario agregado;
- drawdown;
- concentración;
- borrow constraints;
- deterioro de régimen.

TSIS nunca debe tratar la salida de un modelo como una orden incuestionable.

---

## 9. Método científico del proyecto

### 9.1. Research antes que storytelling

Toda hipótesis debe pasar por:

1. definición clara;
2. universo correcto;
3. datos certificados;
4. evento o setup bien especificado;
5. simulación con costes realistas;
6. validación temporal seria;
7. análisis de robustez;
8. análisis de degradación;
9. revisión visual de casos;
10. decisión explícita de promoción, cuarentena o descarte.

### 9.2. La robustez importa más que el óptimo puntual

TSIS prefiere:

- mesetas estables;
- degradación tolerable;
- edge modesto pero persistente;
- interpretabilidad;
- capacidad de diagnóstico;

frente a:

- el mejor Sharpe aislado;
- parámetros extremadamente finos;
- estrategias frágiles;
- modelos opacos sin trazabilidad.

### 9.3. Todo debe poder reconstruirse

Cada resultado relevante debe poder responder:

- qué dataset se usó;
- qué versión de universo;
- qué política de calidad;
- qué configuración;
- qué simulador;
- qué costes;
- qué período;
- qué reglas de exclusión;
- qué commit o run produjo el resultado.

Sin trazabilidad no hay ciencia.
Sin ciencia no hay edge defendible.

---

## 10. Limitaciones de TSIS

TSIS reconoce explícitamente que:

- los mercados son parcialmente adversariales;
- muchos mecanismos siguen siendo invisibles;
- el edge puede desaparecer abruptamente;
- la ejecución real puede invalidar señales que parecían válidas;
- la simulación nunca replica perfectamente el mercado live;
- los labels financieros son aproximaciones imperfectas;
- los grafos causales en mercados siempre serán parciales, nunca finales;
- un modelo puede capturar estructura útil sin comprender plenamente el mecanismo subyacente;
- la calidad de datos puede mejorar mucho y aun así dejar ambigüedad irresuelta;
- un sistema robusto puede seguir fallando ante un cambio estructural del mercado.

El proyecto no asume observabilidad total, estacionariedad perfecta ni explotabilidad permanente.

---

## 11. Falsabilidad

TSIS exige que las hipótesis sean refutables.
Una narrativa rentable no basta.

Una hipótesis debe degradarse, ponerse en cuarentena o descartarse si ocurre una o varias de estas condiciones:

- desaparece OOS;
- depende críticamente de parámetros finos;
- colapsa bajo costes o slippage realistas;
- no sobrevive a cambios de régimen;
- depende de leakage temporal;
- no puede reconstruirse de forma consistente entre reruns;
- no tiene un mecanismo defendible, solo una asociación inestable;
- falla bajo perturbation, sensitivity o delayed-entry tests;
- requiere supuestos de datos incompatibles con la observabilidad live.

Ni la complejidad, ni la novedad, ni una rentabilidad pasada protegen una hipótesis frente a la refutación.

---

## 12. Filosofía de supervisión humana

TSIS es un sistema probabilístico de asistencia y decisión.
No se le concede soberanía irrestricta.

El proyecto no asume:

- infalibilidad del modelo;
- estabilidad eterna;
- autonomía sin límites;
- validez automática del despliegue live;
- transferencia incondicional del backtest a producción.

La autoridad humana sigue siendo final sobre:

- límites de riesgo;
- decisiones de despliegue;
- suspensión de estrategias o modelos;
- promoción o rollback;
- overrides de emergencia;
- interpretación de regímenes anómalos o structural breaks.

El sistema puede informar, rankear, recomendar y automatizar flujos acotados.
No elimina la responsabilidad del operador.

---

## 13. Fragilidad de régimen

Muchos edges de microcaps dependen de condiciones estructuralmente inestables, entre ellas:

- atención especulativa;
- abundancia de liquidez;
- momentum retail;
- expansión de volatilidad;
- disponibilidad de borrow;
- comportamiento concreto de market makers;
- entornos de tipos bajos o alta apetencia por riesgo.

TSIS asume que algunos edges pueden:

- degradarse;
- desaparecer;
- invertirse;
- o fragmentarse en subfamilias

cuando cambia la estructura del mercado.

Por eso la sensibilidad a régimen es una exigencia central, no un refinamiento tardío.

Un setup que funcionó en un ciclo especulativo no se asume transferible sin cambios al siguiente.

---

## 14. Pipeline de promoción de research

Las ideas no pasan directamente de la intuición a producción.
Deben recorrer un pipeline de promoción.

La ruta canónica es:

`idea -> exploratory research -> event formalization -> execution-aware simulation -> robustness testing -> walk-forward validation -> promotion candidate -> paper trading -> restricted live deployment -> monitored production`

En cada etapa, una hipótesis debe justificar su continuidad mediante:

- mejor especificación;
- evidencia más fuerte;
- mayor realismo de ejecución;
- menor dependencia de supuestos optimistas;
- y semántica operativa más clara.

La promoción se gana.
No la concede un notebook con buen resultado.

---

## 15. Principios operativos no negociables

- No confundir datos disponibles con datos utilizables.
- No confundir correlación con mecanismo.
- No confundir señal con ejecución.
- No confundir un setup con un dibujo.
- No confundir un modelo con una política completa.
- No confundir backtest con verdad.
- No confundir precisión local con robustez.
- No confundir complejidad con profundidad.
- No confundir automatización con entendimiento.

---

## 16. La pregunta maestra de TSIS

La pregunta final del proyecto no es:

“¿qué indicador compraría aquí?”

La pregunta maestra es:

“¿qué dinámica causal, microestructural y estadísticamente defendible está ocurriendo en este episodio, qué decisión secuencial permite, con qué incertidumbre, y bajo qué límites de ejecución y riesgo sigue siendo explotable?”

TSIS existe para responder esa pregunta mejor que un gráfico, mejor que una intuición aislada y mejor que un backtest ingenuo.

Ese es el estándar.
