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
  GAP_AND_GO/
    STRATEGY.md
    strategy_case_explorer.ipynb
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
