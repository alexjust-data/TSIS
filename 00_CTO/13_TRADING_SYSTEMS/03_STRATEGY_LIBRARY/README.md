# 03_STRATEGY_LIBRARY

Estado: working library para estrategias humanas, muestras visuales y
descomposicion en eventos.

## 1. Proposito

Strategy Library documenta estrategias como respuestas operativas humanas o
modelos de actuacion frente a fenomenos de mercado.

En la fase actual, su funcion principal no es validar edge.

Su funcion principal es ayudar a TSIS a:

```text
1. tomar una estrategia concreta;
2. buscar muestras historicas y visuales;
3. entender sus fases;
4. separar decision operativa de fenomeno observable;
5. desgranar los eventos que componen la estrategia;
6. enviar esos eventos a Event Library como definiciones v0.
```

## 2. Relacion con Event Library

La arquitectura TSIS mantiene la separacion:

```text
Evento = fenomeno observable.
Estrategia = respuesta operativa ante uno o varios eventos.
```

Pero el workflow de investigacion inicial puede empezar desde una estrategia
humana.

Esto no invierte la autoridad.

```text
Strategy Library ayuda a descubrir piezas observables.
Event Library gobierna la definicion final de eventos.
```

Por tanto:

- una estrategia puede contener muchos eventos;
- un evento puede aparecer en muchas estrategias;
- Strategy Library no debe redefinir eventos como autoridad final;
- Event Library no debe contener entradas, stops, targets ni sizing;
- Strategy Research validara despues si una estrategia tiene edge.

## 3. Workflow actual: estrategia -> eventos

Nuevo flujo operativo:

```text
estrategia humana
-> STRATEGY.md
-> strategy_case_explorer.ipynb
-> muestras visuales
-> descomposicion en eventos
-> Event Library v0: 001.md, 002.md, 003.md
-> busqueda historica por evento
-> depuracion y deduplicacion
-> promocion a evento nombrado y clasificado
```

El objetivo no es crear una taxonomia perfecta desde el primer dia.

El objetivo es capturar, observar y descomponer con precision.

## 4. Estructura de una estrategia

Cada estrategia debe vivir en una carpeta propia.

Ejemplo inicial:

```text
03_STRATEGY_LIBRARY/
  LONG/
    gap&go/
      STRATEGY.md
      strategy_case_explorer.ipynb
      runs/
      img/

  SHORT/
    first_red_day/
      STRATEGY.md
      strategy_case_explorer.ipynb
      runs/
      img/
```

El archivo `STRATEGY.md` debe explicar:

- que intenta capturar la estrategia;
- que contexto necesita;
- que fases visuales suelen aparecer;
- que decisiones operativas humanas contiene;
- que partes son eventos observables;
- que partes son reglas de actuacion;
- que notebooks o scripts sirven para buscar muestras;
- que eventos v0 se derivaron de ella.

## 4.2. Scanner General Y Overlays De Estrategia

Toda estrategia nueva debe consumir el scanner general como denominador antes
de crear filtros propios.

Policy transversal:

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/strategy_scanner_overlay_policy_v0_1.md
```

Regla:

```text
daily_scanner_candidates_table = donde mirar
strategy overlay = hipotesis especifica de la estrategia
strategy state table = lectura experimental de esa estrategia
market_state/event_state = composicion institucional futura
```

Un notebook de estrategia debe declarar siempre su denominador:

```text
all_filters_passed
selected_any_profile
selected_trade_station_like_profile
selected_percent_change_profile
selected_dollar_volume_tradability_profile
selected_relative_volume_profile
manual_human_seed
conditional_on_current_strategy_detector
```

No se permite reportar estadisticas poblacionales desde una muestra manual o
desde un detector local sesgado sin declararlo explicitamente.

## 4.3. Separacion entre traders fuente y estrategias TSIS

`03_STRATEGY_LIBRARY` separa dos cosas distintas:

```text
enseñanzas fuente de traders
estrategias/factores TSIS en investigacion o consolidacion
```

Las carpetas numeradas por trader/fuente guardan material didactico,
transcripciones, capturas, factores fuente y lecturas iniciales.

Ejemplos:

```text
00_Brian Lee/
01_Steven_Dux/
03_Edu_Trades/
04_Xavineta/
```

Las carpetas operativas de TSIS guardan estrategias propias, trabajadas o en
investigacion, independientemente de que hayan nacido inspiradas por un trader:

```text
LONG/
SHORT/
FACTORS/
```

Regla:

```text
Si el documento explica lo que enseña un trader, vive en la carpeta del trader.
Si el documento define una estrategia TSIS que vamos a buscar, medir, depurar y
mantener como nuestra, vive en LONG/ o SHORT/.
Si el documento define un factor TSIS transversal, vive en FACTORS/.
```

Ejemplo:

```text
01_Steven_Dux/SHORT/Gap_Up_Short/STRATEGY.md
```

es lectura fuente de Steven Dux.

```text
SHORT/gap_up_short/STRATEGY.md
```

seria una estrategia TSIS consolidada o en investigacion propia, si decidimos
crearla despues a partir de la fuente.

Por tanto, `LONG/`, `SHORT/` y `FACTORS/` no deben contener subcarpetas con el
nombre de un trader.

## 4.2. Regla de procedencia de imagenes

Las imagenes incrustadas dentro de un `STRATEGY.md` deben venir del mismo video,
documento o fuente primaria que esta definiendo esa estrategia.

Regla:

```text
No se pueden usar imagenes de otro video, otro playbook u otra estrategia como
evidencia visual dentro de una estrategia concreta.
```

Si una imagen de otra fuente parece conceptualmente parecida, puede mencionarse
solo como material relacionado, pero no debe incrustarse ni tratarse como
evidencia de esa estrategia.

Cuando aun no existan capturas del video propio, el documento debe incluir una
seccion de `Imagenes deseadas del propio video` con timestamps concretos y una
descripcion de que captura se necesita.

Objetivo:

```text
texto, imagen y estrategia deben compartir la misma fuente primaria.
```

## 5. Notebooks de estrategia

Cada estrategia puede tener un notebook asociado.

Uso correcto:

- lanzar busquedas amplias de muestras;
- filtrar por parametros configurables;
- visualizar graficos completos;
- revisar casos buenos, malos y ambiguos;
- capturar ejemplos para descomposicion;
- ayudar a decidir que eventos v0 deben escribirse.

Uso incorrecto:

- convertir el notebook en fuente canonica de la estrategia;
- esconder reglas criticas solo en celdas;
- redefinir eventos;
- guardar logica no reproducible;
- mezclar busqueda de muestras con conclusion institucional.

Regla:

```text
El notebook de estrategia es visor/lanzadera.
La logica reutilizable debe vivir en scripts reproducibles.
```

## 5.1. Regla general de screener

En la fase actual, muchas estrategias long deben empezar como si el humano
estuviera mirando un screener operativo, no como si ya conociera el patron
perfecto.

El screener base para small/micro caps funciona con filtros simples:

```text
market_cap < 100M
session_volume >= 500000
0.5 <= price <= 20
```

La arquitectura CTO activa del scanner vive en:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/
```

La autoridad operativa del output vive en:

```text
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md
```

Regla:

```text
El screener de estrategia consume candidatos.
No redefine el scanner transversal ni el market_state.
```

El screener no exige todavia:

- push perfecto;
- numero fijo de velas;
- volumen especifico del push;
- bandera limpia;
- rebreak dentro de X minutos;
- close por encima de un nivel;
- retencion perfecta del primer dip.

Regla:

```text
Primero se captura la aparicion en screener.
Despues el notebook etiqueta que ocurrio.
```

Por tanto, en notebooks de descubrimiento:

- los filtros de screener pueden ser filtros duros;
- los elementos del patron deben empezar como metricas o etiquetas;
- las muestras malas, ambiguas y raras son utiles;
- la optimizacion de filtros viene despues de revisar graficos.

Ejemplo para DAS:

```text
Scanner_Appearance_Candidate
-> medir si hubo primer push
-> medir si hubo primer dip
-> medir si hubo rebreak
-> clasificar estado DAS
```

## 5.2. Contrato de dependencias entre estrategias

Las estrategias deben ser independientes entre si.

Regla contractual:

```text
Una estrategia no puede depender de otra estrategia.
```

Por tanto, esta prohibido que una carpeta de estrategia importe codigo desde
otra carpeta de estrategia.

Ejemplos prohibidos:

```text
LONG/DAS importando helpers desde LONG/gap&go
LONG/Breakout importando helpers desde LONG/DAS
01_Steven_Dux/SHORT/First_Red_Day importando helpers desde LONG/Breakout
```

La razon es semantica, no solo tecnica.

Si `DAS` depende de `gap&go`, entonces DAS queda contaminado por decisiones de
implementacion, nombres, defaults, graficos, filtros o supuestos que pertenecen
a otra estrategia. Eso rompe la trazabilidad y dificulta saber si un resultado
pertenece realmente a DAS o a una herencia accidental de Gap and Go.

Regla correcta:

```text
codigo especifico de una estrategia -> vive dentro de la carpeta de esa estrategia
codigo comun reutilizable -> vive en infraestructura neutral compartida
runs de una estrategia -> viven dentro de runs/ de esa estrategia
notebook de una estrategia -> lanza scripts de esa estrategia
```

Infraestructura neutral significa una ruta comun que no represente ninguna
estrategia concreta.

Ejemplo valido:

```text
03_STRATEGY_LIBRARY/
  _shared/
    strategy_widgets_common.py
  LONG/
    gap&go/
    DAS/
    Breakout/
  SHORT/
```

Una estrategia puede reutilizar utilidades neutrales para:

- lectura de datos;
- formateo de comandos;
- carga de universo;
- referencia de exchange/company;
- helpers de charts;
- exportacion de PNGs;
- utilidades de runs.

Una estrategia no puede reutilizar desde otra estrategia:

- definiciones operativas;
- defaults semanticos;
- filtros propios;
- etiquetas de evento;
- nombres de triggers;
- reglas de seleccion;
- notebooks;
- runs;
- archivos de salida.

Si dos estrategias necesitan el mismo helper, el helper debe extraerse a una
capa neutral antes de ser compartido.

Si todavia no existe la capa neutral, se permite duplicacion temporal pequeña
antes que dependencia lateral entre estrategias.

Regla final:

```text
Compartir infraestructura neutral esta permitido.
Heredar semantica o codigo desde otra estrategia esta prohibido.
```

## 6. Primera estrategia piloto

La primera estrategia a estructurar sera:

```text
Gap and Go
```

Motivo:

- es una estrategia conocida y simple de explicar;
- conecta con momentum, premarket, opening drive y ruptura de niveles;
- permite crear muestras visuales rapidamente;
- ayuda a descubrir eventos sin forzar taxonomia prematura.

Posibles eventos a desgranar desde Gap and Go:

```text
First_3Bar_Push_Event
Premarket_High_Break_Event
Opening_Drive_Event
VWAP_Hold_After_Gap_Event
Gap_And_Go_Failure_Event
```

Estos nombres son provisionales.

Los eventos finales deben escribirse primero en Event Library como:

```text
00_EVENT_LIBRARY/001.md
00_EVENT_LIBRARY/002.md
00_EVENT_LIBRARY/003.md
```

y solo despues, cuando esten claros, se moveran a su familia final.

## 6.1. Siguiente secuencia long

Despues de Gap and Go, la secuencia de trabajo long continua con:

```text
DAS
Breakout
```

`DAS` se estudia primero porque parte de una accion que despierta, hace un
primer push, aguanta el primer dip y vuelve a romper el high de ese primer
push. El notebook debe ayudar a clasificar como se supera ese primer push:
ruptura de una vela, bandera, shelf, compresion, reclaim de VWAP u otra forma
observable.

`Breakout` se estudia despues porque generaliza la ruptura alcista de niveles
relevantes: premarket high, high of day, previous day high, rangos, whole
dollars, VWAP, trendlines y niveles multi-day.

Ambas estrategias pueden compartir visualizadores y scripts, pero deben mantener
definiciones separadas:

```text
DAS = ruptura o recuperacion del high del primer push tras primer dip retenido.
Breakout = ruptura alcista de un nivel relevante, sea o no el high del primer push.
```

## 7. Material fuente actual

Material existente o fuente:

```text
07_Long_plays.md
07_Short_Plays.md
Day Trading en Small Caps - XVNTrading.pdf
LONG/
SHORT/
traders_strategies/ en Event Library como material fuente interpretado
```

Este material puede inspirar estrategias y eventos, pero no es autoridad
institucional por si mismo.

## 8. No-goals

Strategy Library no debe:

- redefinir datasets upstream;
- redefinir eventos como fuente final;
- promocionar edge sin Strategy Research;
- esconder reglas solo en notebooks;
- mezclar material discrecional con contrato institucional sin separar capas.

## 9. Regla final

La Strategy Library puede empezar por lenguaje humano y discrecional.

Pero debe terminar separando:

```text
evento observable
contexto
decision operativa
regla de invalidacion
ejecucion
outcome pendiente
```

La descomposicion correcta de una estrategia produce ramas claras del arbol:

```text
Strategy Library
-> Event Library v0
-> Event Engine
-> Outcome Research
-> Strategy Research
```
