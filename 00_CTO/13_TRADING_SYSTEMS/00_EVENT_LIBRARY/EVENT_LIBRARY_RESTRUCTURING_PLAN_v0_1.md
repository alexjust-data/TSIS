# Event Library Restructuring Plan v0.1

Fecha: 2026-06-21
Estado: planning note para consenso humano-agente.

## 1. Problema detectado

La Event Library ha empezado a acumular demasiadas palabras, documentos largos
y nombres de eventos que pueden estar describiendo fenomenos muy parecidos.

El riesgo principal es que TSIS termine con:

- muchos nombres para estructuras casi iguales;
- documentos dificiles de usar para busqueda historica;
- mezcla entre material fuente, interpretacion humana y contrato tecnico;
- definiciones poco uniformes;
- eventos que parecen setups o estrategias;
- notebooks separados del evento que intentan visualizar.

Esto no debe seguir creciendo asi.

La Event Library debe ser tecnica, precisa y util para pasar de:

```text
definicion de evento
-> busqueda historica en datos
-> visualizacion de candidatos
-> revision humana
-> detector candidate futuro
```

## 2. Principio base

Los documentos actuales tipo Mosquito, EduTrades u otros source indexes deben
entenderse como fuentes interpretadas, no como definiciones finales de eventos.

Separacion propuesta:

```text
source indexes
  = biblioteca de material bruto interpretado

event definition
  = contrato tecnico del evento

notebook
  = herramienta visual para buscar y revisar candidatos
```

La Event Library debe responder:

```text
Que ocurrio?
Como se reconoce historicamente?
Que datos necesito para buscarlo?
Que NO cuenta como este evento?
```

No debe responder:

```text
Donde entro?
Donde salgo?
Donde pongo stop?
Que target busco?
Con que size actuo?
```

## 3. Nueva unidad de trabajo: v0 capture vs evento promovido

Hay dos estados distintos que no deben confundirse.

### 3.1. Estado v0: captura sin clasificar

En la fase actual no vamos a clasificar los eventos por familia ni a fijar su
nombre definitivo demasiado pronto.

La primera vez que escribimos un evento, vive como archivo numerado en la raiz
de Event Library:

```text
00_EVENT_LIBRARY/
  001.md
  002.md
  003.md
```

Regla:

```text
001.md, 002.md, 003.md = version v0 de captura.
```

Estos archivos existen para definir eventos sin forzar todavia:

- nombre final;
- familia;
- carpeta definitiva;
- clasificacion por tipo;
- relacion final con otros eventos.

El `event_id` inicial es el numero del archivo.

Ejemplo:

```yaml
event_id: 003
status: v0_capture
provisional_name: PM_Accepted_Extension_Break_Event
family_candidate: MOMENTUM_EXPANSION
```

### 3.2. Estado promovido: evento nombrado y clasificado

Cuando el evento este suficientemente claro, depurado y diferenciado de otros
eventos parecidos, se promociona a la estructura final.

Ejemplo:

```text
001.md
-> 01_MOMENTUM_EXPANSION/
     PM_ACCEPTED_EXTENSION_BREAK_EVENT/
       EVENT.md
       event_case_explorer.ipynb
       img/
```

Regla:

```text
v0 capture = archivo numerado en raiz.
evento promovido = carpeta con nombre final dentro de familia.
```

Esta no es una contradiccion. Es un workflow de maduracion:

```text
capturar sin clasificar
-> definir con precision
-> comparar duplicados
-> asignar nombre final
-> clasificar por familia
-> mover a carpeta definitiva
```

## 3.3. Nuevo enfoque de descubrimiento: estrategia -> eventos

El proceso inicial no buscara eventos de forma atomica desde cero.

Primero se tomara una estrategia concreta y se desgranaran los eventos que la
componen.

Workflow:

```text
estrategia humana
-> muestras visuales y notebook de estrategia
-> descomposicion en fenomenos observables
-> eventos v0 numerados en Event Library
-> busqueda historica por evento
-> depuracion y deduplicacion
-> promocion a evento nombrado y clasificado
```

Esto no significa que Strategy Library redefina Event Library.

Significa que las estrategias humanas se usan como fuente didactica para
descubrir piezas observables.

Regla:

```text
Strategy Library ayuda a descomponer.
Event Library gobierna el evento final.
```

Primera estrategia piloto:

```text
Gap and Go
```

Cuando Gap and Go tenga una estructura clara, se descompondra en sus eventos
v0 y esos eventos se escribiran como `001.md`, `002.md`, `003.md`, etc.

## 4. Regla sobre notebooks

Durante la fase v0, puede haber dos tipos de notebooks:

1. notebook de estrategia;
2. notebook de evento.

### 4.1. Notebook de estrategia

Vive en `03_STRATEGY_LIBRARY`.

Sirve para:

- buscar muestras de una estrategia completa;
- revisar graficos;
- entender que eventos componen la estrategia;
- generar casos visuales para descomposicion.

Ejemplo:

```text
03_STRATEGY_LIBRARY/
  GAP_AND_GO/
    STRATEGY.md
    strategy_case_explorer.ipynb
```

### 4.2. Notebook de evento

Durante v0, el notebook del evento puede referenciar el archivo numerado.

Cuando el evento se promueva, el notebook puede vivir dentro de la carpeta del
evento para que el humano lo encuentre facilmente junto a la definicion.

Pero el notebook no debe convertirse en la autoridad tecnica del detector.

Uso correcto del notebook:

- lanzar busquedas;
- seleccionar filtros;
- cargar runs;
- visualizar candidatos;
- revisar graficos;
- comparar ejemplos buenos y malos.

Uso incorrecto del notebook:

- contener la logica canonica del evento;
- ser el unico lugar donde vive la busqueda;
- definir reglas finales sin versionado;
- reemplazar scripts reproducibles.

Regla:

```text
El notebook es visor/lanzadera.
La logica reutilizable vive en scripts.
```

Ubicacion probable de scripts:

```text
01_TSIS_backtest_SmallCaps/
  01_research/
    04_event_discovery/
      scripts/
        event_discovery/
```

El notebook del evento debe llamar a scripts parametrizados, no duplicar logica.

## 5. Estructura unica para EVENT.md

Cada evento debe usar la misma plantilla, aunque en v0 el archivo se llame
`001.md`, `002.md`, `003.md`.

Template propuesto:

```text
# 001

## 1. Identidad

## 2. Definicion En Una Frase

## 3. Fenomeno Observable

## 4. Fases Del Evento

## 5. Contrato De Busqueda Historica

## 6. Candidate Row Esperada

## 7. Casos Que NO Son Este Evento

## 8. Relacion Con Otros Eventos

## 9. Ejemplos Visuales

## 10. Notebook
```

## 6. Contenido obligatorio por seccion

### 6.1. Identidad

Debe incluir:

```yaml
event_id:
provisional_name:
final_name:
family_candidate:
family_final:
status:
version:
aliases:
source_notes:
derived_from_strategy:
```

Ejemplo:

```yaml
event_id: 001
provisional_name: PM_Accepted_Extension_Break_Event
final_name:
family_candidate: MOMENTUM_EXPANSION
family_final:
status: v0_capture
version: 0.1.0
aliases:
  - shelf_break_event
  - accepted_extension_break
source_notes:
  - MOSQUITO_SMALLCAPS_SOURCE_EVENT_INDEX_v0_1.md
derived_from_strategy:
  - Gap and Go
```

### 6.2. Definicion en una frase

Una sola frase clara.

Ejemplo:

```text
Evento de premarket donde una primera extension no se destruye, el precio
acepta una zona elevada durante varios minutos y despues rompe esa zona con un
impulso violento.
```

### 6.3. Fenomeno observable

Debe explicar que ocurre en el mercado, sin lenguaje operativo.

Debe evitar:

- entrada;
- stop;
- target;
- sizing;
- comprar;
- vender;
- operar;
- ejecutar;
- estrategia rentable.

### 6.4. Fases del evento

Debe ser una tabla tecnica.

Ejemplo:

| Fase | Descripcion | Condicion observable | Campos necesarios |
| --- | --- | --- | --- |
| initial_extension | primera expansion relevante | subida minima desde base inicial | `open`, `high`, `low`, `close`, `volume`, `ts` |
| acceptance_shelf | precio elevado no se destruye | rango lateral o ascendente tras extension | `high`, `low`, `close`, `volume` |
| violent_break | ruptura de la zona aceptada | varias velas consecutivas con highs/closes crecientes | `open`, `high`, `low`, `close`, `volume` |

### 6.5. Contrato de busqueda historica

Esta es la seccion mas importante para Python.

Debe contener un bloque casi machine-readable:

```yaml
search_contract:
  event_id:
  search_grain:
  session_scope:
  time_anchor:
  data_source:
  required_columns:
  configurable_parameters:
  hard_conditions:
  soft_features:
  exclusions:
  review_flags:
```

Ejemplo:

```yaml
search_contract:
  event_id: pm_accepted_extension_break_event
  search_grain: ticker_session
  session_scope: premarket
  time_anchor: shelf_break_start
  data_source: E:\TSIS\data\ohlcv_1m
  required_columns:
    - ts
    - open
    - high
    - low
    - close
    - volume
  configurable_parameters:
    initial_extension_pct_min: 20
    shelf_min_minutes: 15
    shelf_max_pullback_pct: 35
    break_push_pct_min: 15
    consecutive_break_bars_min: 3
  hard_conditions:
    - initial_extension_exists
    - elevated_price_acceptance_exists
    - shelf_break_exists
  soft_features:
    - volume_expansion
    - higher_lows_during_shelf
    - close_near_high_during_break
  exclusions:
    - single_spike_no_acceptance
    - low_volume_noise
    - missing_premarket_data
  review_flags:
    - shelf_too_short
    - weak_break_volume
    - ambiguous_initial_extension
```

### 6.6. Candidate row esperada

Debe decir que campos emitiria un script exploratorio si encuentra el evento.

Ejemplo:

```yaml
candidate_row:
  event_id:
  event_name:
  ticker:
  date:
  session_scope:
  event_start_ts:
  event_end_ts:
  time_anchor_ts:
  initial_extension_pct:
  shelf_duration_minutes:
  shelf_pullback_pct:
  break_push_pct:
  break_bar_count:
  event_quality_state:
  review_flags:
  source_data_root:
  run_id:
```

### 6.7. Casos que NO son este evento

Esta seccion es obligatoria para reducir duplicados.

Ejemplo:

```text
No es este evento si:

- solo hay spike vertical sin aceptacion previa;
- el precio hace push y se destruye inmediatamente;
- no existe ruptura posterior de la zona aceptada;
- el movimiento ocurre fuera del scope temporal definido;
- faltan datos de premarket necesarios para comprobar la secuencia.
```

### 6.8. Relacion con otros eventos

Debe comparar eventos parecidos y explicar por que no son exactamente lo mismo.

Ejemplo:

| Evento relacionado | Diferencia |
| --- | --- |
| First_3Bar_Push_Event | detecta impulso, pero no exige aceptacion previa |
| Gap_And_Go_Event | puede romper temprano, pero no necesariamente forma shelf |
| DAS_Event | se centra en dips posteriores al squeeze/push, no en la primera estructura de aceptacion |

### 6.9. Ejemplos visuales

Debe incluir solo imagenes realmente utiles.

Cada imagen debe tener:

- ruta local;
- descripcion;
- que parte del evento muestra;
- que parte NO demuestra.

### 6.10. Notebook

Debe indicar:

```text
Notebook asociado:
event_case_explorer.ipynb
```

Y debe explicar:

- que script lanza;
- que parametros expone;
- donde guarda runs;
- como borrar runs;
- que output visualiza.

## 7. Regla de deduplicacion

Antes de crear un nuevo evento, hay que comprobar si ya existe algo equivalente.

Regla:

```text
Si dos eventos se detectan con la misma secuencia, mismos campos y misma ancla
temporal, probablemente son el mismo evento con alias o subtipo.
```

Otra regla:

```text
Si cambia la estructura temporal o el fenomeno central, puede ser otro evento.
```

Ejemplo de posible solapamiento:

```text
First_3Bar_Push_Event
PM_Accepted_Extension_Break_Event
DAS_Event
Gap_And_Go_Event
VWAP_Reclaim_Event
```

Pueden compartir componentes:

```text
impulso inicial
pullback
aceptacion
ruptura de maximo
reclaim de nivel
continuacion
```

Pero no todo componente debe convertirse en evento top-level.

## 8. Diferencia entre componente y evento

Un componente es una pieza reutilizable.

Ejemplos:

```text
3-bar push
pullback
VWAP reclaim
prior high break
volume expansion
high hold
```

Un evento top-level debe tener una estructura suficientemente completa.

Regla:

```text
Componente = pieza del fenomeno.
Evento = secuencia observable con identidad propia.
```

## 9. Workflow propuesto

No crear mas eventos en masa.

Trabajar estrategia por estrategia, y dentro de cada estrategia, evento por
evento:

```text
1. elegir estrategia piloto
2. escribir STRATEGY.md en Strategy Library
3. crear notebook de estrategia para buscar muestras
4. revisar graficos y casos
5. desgranar eventos que componen la estrategia
6. escribir cada evento como NNN.md en la raiz de Event Library
7. comprobar duplicados entre eventos v0
8. conectar cada evento a busqueda historica
9. revisar graficos por evento
10. ajustar definicion
11. asignar nombre final y familia solo cuando este claro
12. mover a carpeta definitiva
```

Primera estrategia recomendada para definir:

```text
Gap and Go
```

Posibles eventos a desgranar despues de analizar Gap and Go:

```text
First_3Bar_Push_Event
Premarket_High_Break_Event
Opening_Drive_Event
VWAP_Hold_After_Gap_Event
Gap_And_Go_Failure_Event
```

Estos nombres son provisionales. La fase v0 debe evitar convertir nombres
rapidos en taxonomia definitiva.

## 10. Estructura final deseada

Ejemplo:

```text
00_EVENT_LIBRARY/
  EVENT_LIBRARY_RESTRUCTURING_PLAN_v0_1.md
  EVENT_DEFINITION_STANDARD_v0_1.md

  001.md
  002.md
  003.md

  01_MOMENTUM_EXPANSION/
    PM_ACCEPTED_EXTENSION_BREAK_EVENT/
      EVENT.md
      event_case_explorer.ipynb
      img/

  07_SHORT_SQUEEZE_DYNAMICS/
    DAS_EVENT/
      EVENT.md
      event_case_explorer.ipynb
      img/
```

Durante v0, los eventos numerados son la zona de trabajo activa.

Cuando un evento este terminado:

```text
001.md
-> 01_MOMENTUM_EXPANSION/PM_ACCEPTED_EXTENSION_BREAK_EVENT/EVENT.md
```

Los source indexes y documentos de traders quedan como referencias:

```text
traders_strategies/
source_assets/
```

No son la forma final de un evento.

## 11. Regla final

La Event Library debe dejar de crecer como coleccion de textos largos.

Debe evolucionar hacia:

```text
fase v0:
  un evento provisional
  un archivo numerado NNN.md
  un contrato de busqueda historica
  una frontera clara contra estrategia

fase promovida:
  un evento nombrado
  una carpeta por evento
  un EVENT.md tecnico
  un notebook visual
  un contrato de busqueda historica mantenido
  una frontera clara contra estrategia
```

Si un documento no ayuda a escribir una busqueda historica reproducible en
Python o a distinguir el evento de otros eventos parecidos, entonces el
documento todavia no esta suficientemente acotado.
