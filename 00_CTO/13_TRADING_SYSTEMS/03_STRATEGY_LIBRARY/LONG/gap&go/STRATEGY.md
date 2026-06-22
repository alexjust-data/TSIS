# Gap And Go - Initial Strategy Definition v0.1

Fecha: 2026-06-22  
Estado: `initial_strategy_definition`  
Scope: `03_STRATEGY_LIBRARY/LONG/gap&go/`  

Este documento define inicialmente que entendemos por `Gap and Go` en TSIS.

No es un backtest.
No valida edge.
No define todavia una estrategia institucional.

Su funcion es servir como primera definicion tecnica para buscar muestras,
visualizarlas en notebook y despues desgranar los eventos que componen la
estrategia.

## 1. Definicion corta

`Gap and Go` es una estrategia long de apertura basada en momentum.

Ocurre cuando una accion small/micro cap viene activa en premarket, abre con
gap alcista o presion compradora relevante, rompe el `premarket high` con
volumen durante la apertura y continua el movimiento sin destruir
inmediatamente la estructura.

En una frase:

```text
Gap and Go =   
gap alcista +  
atencion premarket +  
ruptura del premarket high +  
volumen expansivo +  
continuidad inicial.
```

## 2. Lectura desde el documento fuente

El documento `07_Long_plays.md` describe Gap and Go como el patron clasico de apertura en momentum.

Lectura fuente:

```text
Una accion hace breakout del premarket high y continua su movimiento al alza en la apertura.
```

Condiciones del documento fuente:

```text
1. Accion verde en el dia.
2. Breakout del premarket high con volumen.
3. Sector caliente o catalizador relevante.
4. Solo aplicable en el primer dia de corrida.
5. No intentar en fases tardias o despues de un parabolic run.
```

TSIS no debe copiar esto como receta cerrada. Debe usarlo como punto de partida
para buscar muestras, separar componentes y definir eventos observables.

## 3. Naturaleza de la estrategia

Gap and Go no es un evento atomico.

Es una estrategia compuesta.

Puede contener:

```text
contexto
-> gap
-> actividad premarket
-> nivel premarket high
-> ruptura
-> volumen
-> continuidad o fallo
```

Por eso el primer trabajo no es optimizar entrada, stop o target.

El primer trabajo es:

```text
encontrar muestras historicas
-> ver graficos
-> separar fenomenos observables
-> escribir eventos v0 en Event Library
```

## 4. Arbol conceptual inicial

Propuesta de descomposicion:

```text
Gap_And_Go_Strategy
  -> Catalyst_Attention_Context
  -> Premarket_Gap_Context
  -> Premarket_High_Defined_Event
  -> Premarket_High_Break_Event
  -> Opening_Drive_Event
  -> PMH_Hold_Or_Failure_Event
  -> VWAP_Hold_Context
```

Esta lista no es definitiva. Sirve para empezar a mirar la estrategia como un
conjunto de piezas observables.

## 5. Explicacion de cada componente

### 5.1. `Catalyst_Attention_Context`

Contexto donde existe una razon observable para que el ticker reciba atencion.

Puede venir de:

- noticia;
- press release;
- earnings;
- sector caliente;
- volumen premarket anormal;
- mencion o atencion colectiva.

No significa que la noticia sea buena ni que el movimiento tenga edge.

En TSIS este componente responde:

```text
Por que este ticker esta recibiendo atencion hoy?
```

### 5.2. `Premarket_Gap_Context`

Contexto donde el precio esta por encima del cierre anterior antes o al inicio
de la sesion regular.

Ejemplo:

```text
prior_close = 1.00
premarket_price = 1.35
gap_pct = 35%
```

En TSIS este componente responde:

```text
El mercado ya repricio el ticker antes de abrir?   
es decir, ¿el precio ya cambió de valor de forma importante antes de que abra el mercado regular? 
```

### 5.3. `Premarket_High_Defined_Event`

Evento donde el premarket crea un maximo claro que puede funcionar como nivel visible para traders.

No basta con que exista un high tecnico cualquiera.

Debe ser un nivel que tenga sentido visual:

- fue marcado con volumen;
- el precio opero debajo despues;
- otros participantes pueden verlo como referencia;
- no es solo una wick aislada de mala calidad.

En TSIS este evento responde:

```text
Existe un PMH claro que pueda actuar como nivel de decision del mercado?
```

### 5.4. `Premarket_High_Break_Event`

Evento donde el precio rompe el `premarket high`.

Es probablemente el evento central de Gap and Go.

Debe medir:

- cuando rompe;
- si cierra por encima;
- con que volumen rompe;
- si la ruptura ocurre temprano;
- si falla inmediatamente o no.

En TSIS este evento responde:

```text
El mercado rompio el nivel premarket high de forma observable?
```

### 5.5. `Opening_Drive_Event`

Evento de impulso direccional durante la apertura regular.

No es cualquier subida.

Debe capturar la fase donde el mercado abre y el precio se desplaza con fuerza,
normalmente en los primeros minutos.

En TSIS este evento responde:

```text
La apertura produjo desplazamiento real o solo ruido alrededor del nivel?
```

### 5.6. `PMH_Hold_Or_Failure_Event`

Evento posterior a la ruptura del PMH.

Mide si el precio:

- sostiene el nivel roto;
- lo retestea y aguanta;
- falla bajo el PMH rapidamente;
- convierte la ruptura en fakeout.

Este componente es clave porque Gap and Go puede fallar en segundos.

En TSIS este evento responde:

```text
Despues de romper PMH, el mercado acepto el nuevo precio o lo rechazo?
```

### 5.7. `VWAP_Hold_Context`

Contexto donde VWAP ayuda a interpretar si el movimiento mantiene control
comprador.

No es necesariamente el evento central de Gap and Go, pero puede actuar como
filtro o condicion de calidad.

En TSIS este contexto responde:

```text
El precio mantiene estructura por encima de VWAP o pierde control intradia?
```

## 6. Condiciones iniciales para buscar muestras

Estas condiciones son parametros de busqueda, no reglas finales.

```yaml
search_seed:
  min_gap_pct:
  min_premarket_volume:
  min_price:
  max_market_cap:
  max_minutes_after_open_for_break:
  min_breakout_volume_ratio:
  first_day_run_filter:
```

## 7. Explicacion de parametros

### 7.1. `min_gap_pct`

Porcentaje minimo de gap frente al cierre anterior.

Sirve para excluir tickers que apenas se movieron antes de la apertura.

Ejemplo:

```text
min_gap_pct = 20
```

significa buscar acciones que esten al menos un 20% por encima del cierre
anterior.

### 7.2. `min_premarket_volume`

Volumen minimo negociado en premarket.

Sirve para exigir que el movimiento tenga participacion real y no sea solo una
marca aislada.

Ejemplo:

```text
min_premarket_volume = 500000
```

significa que el ticker debe haber negociado al menos 500k acciones antes de la
apertura regular.

### 7.3. `min_price`

Precio minimo permitido.

Sirve para excluir tickers demasiado baratos donde el ruido, spreads, ticks y
errores de microestructura pueden dominar la lectura.

Ejemplo:

```text
min_price = 0.5
```

significa que no se buscan candidatos por debajo de 0.50 USD.

### 7.4. `max_market_cap`

Capitalizacion maxima permitida.

Sirve para mantener el universo dentro de small/micro caps, donde la dinamica
de Gap and Go suele ser mas explosiva y sensible a volumen.

Ejemplo:

```text
max_market_cap = 100000000
```

significa buscar empresas por debajo de 100M de market cap cuando ese dato
exista.

### 7.5. `max_minutes_after_open_for_break`

Numero maximo de minutos desde la apertura regular para que ocurra la ruptura
del PMH.

Sirve para separar Gap and Go de rupturas tardias.

Ejemplo:

```text
max_minutes_after_open_for_break = 30
```

significa que la ruptura del premarket high debe ocurrir dentro de los primeros
30 minutos de mercado regular.

### 7.6. `min_breakout_volume_ratio`

Ratio minimo entre el volumen de la ruptura y el volumen de referencia reciente.

Sirve para exigir que la ruptura tenga participacion superior al contexto
inmediato.

Ejemplo:

```text
min_breakout_volume_ratio = 2.0
```

significa que la vela o ventana de ruptura debe tener al menos el doble del
volumen promedio de las velas previas comparables.

### 7.7. `first_day_run_filter`

Filtro para priorizar acciones en primer dia de corrida.

Sirve para excluir movimientos tardios, extensiones parabolicas de varios dias
o tickers que ya agotaron gran parte del momentum.

Puede aproximarse con:

- dias desde primer volumen anormal;
- extension previa multi-dia;
- distancia frente a precio base reciente;
- numero de sesiones consecutivas verdes;
- volumen relativo en sesiones anteriores.

## 8. Secuencia buscable inicial

Una primera busqueda historica podria intentar encontrar:

```text
1. ticker con gap up frente a prior close;
2. volumen premarket suficiente;
3. premarket high claro;
4. apertura regular cerca o debajo del PMH;
5. ruptura del PMH en los primeros minutos;
6. volumen de ruptura expansivo;
7. ausencia de fallo inmediato bajo PMH.
```

Esto no define todavia entrada ni salida.

Define una muestra candidata de Gap and Go.

## 9. Casos que NO deberian contar

No deberia contarse como Gap and Go si:

- hay gap up sin volumen;
- no existe premarket high claro;
- el PMH es solo una wick aislada;
- rompe PMH pero falla en segundos;
- ya viene de varios dias de extension extrema;
- ocurre despues de un parabolic run;
- la ruptura ocurre tarde en la sesion;
- el gap se rellena antes de romper;
- falta data de premarket;
- la ruptura no tiene volumen relativo.

## 10. Relacion con eventos v0 en Event Library

Cuando esta estrategia tenga suficientes muestras, se descompondra en eventos
v0 dentro de:

```text
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/
```

Ejemplo:

```text
001.md = Premarket_Gap_Context / evento provisional
002.md = Premarket_High_Defined_Event / evento provisional
003.md = Premarket_High_Break_Event / evento provisional
004.md = Opening_Drive_Event / evento provisional
005.md = PMH_Hold_Or_Failure_Event / evento provisional
```

Los nombres son provisionales. La numeracion v0 permite escribir y comparar
eventos antes de clasificarlos por familia.

## 11. Notebook esperado

Notebook futuro:

```text
strategy_case_explorer.ipynb
```

Debe permitir:

- elegir parametros de busqueda;
- imprimir el comando equivalente para terminal;
- ejecutar o cargar runs;
- ver candidatos encontrados;
- visualizar chart tipo TradingView;
- marcar ejemplos buenos, malos y ambiguos.

## 12. Chart requerido para revision

Cada muestra debe poder verse en un chart interactivo con:

- velas 1m;
- VWAP;
- volumen 1m en panel inferior;
- volumen coloreado segun color de vela;
- velas verdes cuando `close >= open`;
- velas rojas cuando `close < open`;
- premarket, regular market y after-hours visibles;
- ventana amplia alrededor del evento;
- mucho aire arriba y abajo del precio;
- crosshair vertical y horizontal;
- tooltip OHLCV completo;
- eje X con fecha y hora;
- ticker con exchange cuando exista;
- marca visual del PMH y de la ruptura.

## 13. Frontera con Event Library

Strategy Library puede hablar de:

- estrategia humana;
- decision operativa fuente;
- contexto;
- fases visuales;
- muestras;
- posibles componentes.

Event Library debe quedarse con:

- fenomeno observable;
- contrato de busqueda;
- condiciones;
- exclusiones;
- candidate rows;
- relacion con otros eventos.

Regla:

```text
Gap and Go es la estrategia piloto.
Sus piezas observables se convertiran en eventos v0 numerados.
```

## 14. Referencias iniciales

Fuentes internas:

- `03_STRATEGY_LIBRARY/07_Long_plays.md`
- `00_EVENT_LIBRARY/EVENT_LIBRARY_RESTRUCTURING_PLAN_v0_1.md`

Fuentes externas de contexto:

- SEC Microcap Stock Guide:
  https://www.sec.gov/about/reports-publications/investorpubsmicrocapstock
- Investopedia - Playing the Gap:
  https://www.investopedia.com/articles/trading/05/playinggaps.asp
- Farmer et al. - What really causes large price changes?
  https://arxiv.org/abs/cond-mat/0312703

Estas fuentes no validan edge. Solo apoyan contexto sobre gaps, microcaps,
liquidez y movimientos grandes de precio.
