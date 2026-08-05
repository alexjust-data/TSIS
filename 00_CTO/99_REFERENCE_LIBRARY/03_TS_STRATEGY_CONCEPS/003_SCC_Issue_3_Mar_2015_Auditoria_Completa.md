# Auditoría completa — TradeStation Strategy Concepts Club, Issue 3 (marzo de 2015)

## 0. Alcance del artefacto

Este es el **único Markdown de la revista completa**. Integra:

```text
1. Moving Average Machine
2. Bar Range Expansion Strategy
3. ideas secundarias de backtesting presentes en el issue
4. auditoría temporal, matemática y metodológica
5. contratos de réplica para TSIS
6. planes de falsificación y validación postpublicación
```

No se generan archivos separados por estrategia.

### Fuentes examinadas

- PDF completo de 16 páginas: `SCC Issue 3 Mar 2015.pdf`
- ZIP original de apoyo: `2015-03.zip`
- Workspace y contenedor `.ELD` de ambas estrategias
- Imágenes renderizadas de las 16 páginas, incluidas:
  - la superficie de optimización de EURUSD de la página física 7;
  - las tablas comparativas y la curva de Portfolio Maestro de la página física 8;
  - el ejemplo de formación de órdenes BRE de la página física 12;
  - el informe completo de rendimiento BRE de la página física 14;
  - la curva detallada de capital de la página física 15.
- Los Markdown de los Issues 1 y 2 se utilizan sólo como **modelo de profundidad y organización**, nunca como autoridad factual para este número.

### Regla de evidencia

Se distinguen tres capas:

```text
SOURCE:
lo que afirma, define o muestra la revista

PACKAGE:
lo que confirman el PDF, los workspaces .tsw y los contenedores .ELD

AUDIT:
inferencia técnica, crítica científica y propuesta de implementación en TSIS
```

Cuando el PDF o el paquete no resuelven una decisión, se registra como ambigüedad. No se completa silenciosamente.

### Resultado ejecutivo del issue

| ID | Estrategia | Tipo | Evidencia publicada | Riesgo principal | Decisión |
|---|---|---|---|---|---|
| 005 | Moving Average Machine | Generador de estrategias de medias móviles y optimizador; seis pares FX daily | Rankings de optimización y curva agregada; no se publica un informe completo de performance | más de 100.000 filas evaluadas, duplicación de configuraciones ignoradas, selección in-sample, seis pares no independientes, casi 100% de exposición | Implementar como benchmark de gobernanza experimental, no aceptar como estrategia validada |
| 006 | Bar Range Expansion | Volatility breakout intradía desde el open con salidas múltiples; ES daily con LIBB 30m | PF 1.37, 822 trades, 77.01% ganadoras, $66,257.66, 10 años | secuencia intrabar incompleta, continuo sintético, cero slippage, payoff muy asimétrico, colisiones entre entradas y salidas | Replicar con motor event-driven y contratos físicos antes de evaluar el edge |

## 0.1 Veredicto global

El Issue 3 contiene dos objetos de investigación muy distintos.

`Moving Average Machine` no es realmente una estrategia concreta. Es una **máquina de búsqueda** sobre una familia de reglas. Su principal valor para TSIS no consiste en descubrir que “SMA 39 / EMA 50” sea mejor, sino en obligar a registrar:

```text
espacio total de configuraciones
configuraciones funcionalmente duplicadas
selección del ganador
correlación entre mercados
costes de búsqueda
validación fuera de muestra
```

`Bar Range Expansion` sí es una estrategia operativa completa, pero su comportamiento depende de detalles que un backtester diario convencional no puede resolver:

```text
open de la nueva sesión
órdenes stop long y short simultáneas
secuencia high/low intradía
reversals
stop monetario same-bar
salida en el primer open rentable
stop de canal de siete barras
time exit
roll de futuros
```

La revista aporta ideas legítimas y resultados interesantes, pero ninguna de las dos estrategias demuestra científicamente un edge reproducible.

```text
ISSUE_STATUS:
VALUABLE_SOURCE_MATERIAL

EDGE_STATUS:
UNPROVEN

IMPLEMENTATION_STATUS:
TWO_REPRODUCTION_CANDIDATES

SCIENTIFIC_RISK:
HIGH

LIVE_STATUS:
NOT_ELIGIBLE
```

---

# Parte I — Estrategia 005: Moving Average Machine

## 1) Identificación y alcance

- **ID de estrategia:** `SCC-2015-03-STRAT-005`
- **Revista:** *Strategy Concepts Club* — TradeStation Labs
- **Issue:** 3
- **Fecha declarada:** marzo de 2015
- **Metadata de creación del PDF:** 9 de marzo de 2015
- **Artículo:** *Moving Average Machine*
- **Autor:** **Stanley Dash, CMT**
- **Páginas físicas del PDF:** 4–9
- **Páginas impresas del artículo:** 2–7
- **Estilo declarado:** Trend following
- **Mercados declarados:** Equities, futures, forex
- **Horizonte declarado:** Position trading
- **Frecuencia de los tests publicados:** Daily
- **Mercados del estudio:** EURUSD, GBPUSD, AUDUSD, USDCAD, USDJPY y USDCHF
- **Archivos del ZIP:** estrategia `.ELD`, indicador `.ELD` dentro del mismo contenedor y workspace `.tsw`

### Inputs publicados

| Input | Default | Función declarada |
|---|---:|---|
| `NumMAs_1_2` | 2 | Selecciona estrategia de una o dos medias |
| `MA1Type_1S_2W_3E` | 1 | Tipo de MA1: 1=SMA, 2=WMA, 3=EMA |
| `MA1Length` | 20 | Longitud de MA1 |
| `MA2Type_1S_2W_3E` | 2 | Tipo de MA2; ignorado en modo de una media |
| `MA2Length` | 50 | Longitud de MA2; ignorado en modo de una media |

El indicador complementario utiliza los mismos inputs y representa una o dos medias en el gráfico.

### Evidencia adicional del ZIP

El workspace `TSL.Moving Average Machine.tsw` contiene metadatos legibles que confirman:

```text
chart principal:
GLD Daily [ARCX] SPDR Gold Trust

analysis techniques:
TSL:Mov Avg Machine
TSL:Mov Avg Machine indicator

inputs registrados:
NumMAs_1_2
MA1Type_1S_2W_3E
MA1Length
MA2Type_1S_2W_3E
MA2Length

TradeStation version string:
9.01.00.12679
```

El workspace corresponde al ejemplo visual de GLD, no al Portfolio Maestro de seis pares FX. El `.ELD` es un contenedor propietario binario y no expone el código EasyLanguage como texto legible en este entorno.

El paquete confirma identidad, inputs e instrumentos de ejemplo. No permite verificar directamente:

```text
funciones exactas utilizadas para SMA/WMA/EMA
semilla inicial de la EMA
MaxBarsBack
propiedades de fills
tratamiento de igualdad en crosses
export completo del Portfolio Maestro
```

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí, con facilidad.** |
| ¿Es una única estrategia? | **No.** Es una familia y un generador de experimentos. |
| ¿Puede replicarse el comportamiento básico con el PDF? | **Sí.** |
| ¿El artículo demuestra que SMA39/EMA50 tiene edge? | **No.** Es el ganador de una búsqueda in-sample muy amplia. |
| ¿La tesis general de trend following es plausible? | **Sí.** |
| ¿La comparación entre seis pares es independiente? | **No.** Todos comparten exposiciones USD y regímenes macroeconómicos. |
| ¿El resultado de Portfolio Maestro es OOS? | **No.** Usa la misma muestra y el mismo espacio de búsqueda. |
| ¿Está preparada para operar? | **No.** No tiene controles de riesgo y permanece casi siempre invertida. |

Clasificación TSIS:

```text
EXPERIMENT_GENERATOR
MULTIPLE_TESTING_CRITICAL
DUPLICATE_CONFIGURATION_RISK
PORTFOLIO_DEPENDENCE_RISK
POSTPUBLICATION_OOS_AVAILABLE
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 2. Qué es realmente

La Moving Average Machine parametriza dos familias clásicas.

### Modo de una media

```text
close cruza por encima de MA1 -> long en la apertura siguiente
close cruza por debajo de MA1 -> short en la apertura siguiente
```

### Modo de dos medias

```text
MA1 cruza por encima de MA2 -> long en la apertura siguiente
MA1 cruza por debajo de MA2 -> short en la apertura siguiente
```

No existen salidas independientes:

```text
no stop loss
no profit target
no flat state voluntario
no time exit
```

Cada señal opuesta revierte la posición. Por tanto, el sistema es estructuralmente:

```text
long o short
casi el 100% del tiempo
```

Esto es esencial: el resultado no compara sólo “calidad de señales”. También incorpora exposición continua, beta direccional alternante, gaps de apertura, carry de FX y costes de reversión.

La revista lo denomina “testing and optimization tool”. Esa clasificación es más correcta que llamarlo edge.

---

## 3. Reconstrucción matemática

Sea `C_t` el cierre diario de un símbolo.

### 3.1 Media simple

Para longitud `L`:

$$
SMA_t(L)=\frac{1}{L}\sum_{i=0}^{L-1}C_{t-i}
$$

Todos los cierres de la ventana reciben el mismo peso.

### 3.2 Media ponderada

La interpretación compatible con la función estándar `WAverage` es:

$$
WMA_t(L)=\frac{\sum_{i=0}^{L-1}(L-i)C_{t-i}}
{\sum_{j=1}^{L}j}
$$

El cierre más reciente recibe peso `L` y el más antiguo peso `1`.

### 3.3 Media exponencial

La forma habitual es:

$$
EMA_t(L)=\alpha C_t+(1-\alpha)EMA_{t-1}(L)
$$

con:

$$
\alpha=\frac{2}{L+1}
$$

La semilla exacta importa durante el warm-up. Sin exportar el EasyLanguage no puede confirmarse si la implementación usa exactamente `XAverage` ni cómo se inicializa el primer valor.

### 3.4 Selección por tipo

Podemos representar el selector de forma abstracta:

$$
MA(C,L,type)=
\begin{cases}
SMA(C,L), & type=1\\
WMA(C,L), & type=2\\
EMA(C,L), & type=3
\end{cases}
$$

Entonces:

$$
MA1_t=MA(C,MA1Length,MA1Type)
$$

$$
MA2_t=MA(C,MA2Length,MA2Type)
$$

### 3.5 Cross de una media

Una reconstrucción estándar del cruce alcista sería:

$$
C_t>MA1_t
$$

junto con:

$$
C_{t-1}\le MA1_{t-1}
$$

El cruce bajista sería el inverso.

La igualdad exacta puede resolverse de forma distinta según la semántica de `crosses over/under`; debe comprobarse durante la réplica.

### 3.6 Cross de dos medias

Cruce alcista:

$$
MA1_t>MA2_t
$$

$$
MA1_{t-1}\le MA2_{t-1}
$$

Cruce bajista:

$$
MA1_t<MA2_t
$$

$$
MA1_{t-1}\ge MA2_{t-1}
$$

### 3.7 Decision timestamp y ejecución

La información se conoce al cierre de `t`:

```text
decision_timestamp = session_close_t
```

La orden se ejecuta en:

```text
entry_timestamp = session_open_t+1
```

El retorno de cada posición incluye:

```text
open de entrada
sesiones completas
posibles gaps overnight
open de reversión
```

No debe modelarse como close-to-close.

### 3.8 Reversal

Cuando una posición long recibe señal short en `t`:

```text
open t+1:
1. cerrar long
2. abrir short
```

En términos de notional, una reversión exige una transacción equivalente a dos lados. No debe contabilizarse como una simple salida o una sola comisión.

### 3.9 Warm-up

Para una SMA o WMA de longitud `L` se requieren al menos `L` cierres válidos.

Para EMA, la función puede producir valores antes, pero la estabilidad depende de una historia suficiente. La frase del artículo “allowing for MaxBarsBack” indica que los cinco años efectivos comienzan después de reservar barras iniciales, pero no se publica el valor exacto de MaxBarsBack.

---

## 4. La afirmación de “18 combinaciones” necesita precisión

La revista afirma que las medias simples, ponderadas y exponenciales aplicadas a estrategias de una y dos líneas generan 18 combinaciones.

Funcionalmente:

```text
1-line:
3 tipos posibles

2-line:
3 tipos para MA1 × 3 tipos para MA2 = 9

familias únicas:
3 + 9 = 12
```

Se puede llegar a 18 filas codificadas si, en el modo de una línea, se siguen variando los tres valores de `MA2Type`; pero MA2 está explícitamente ignorada. Esas filas no constituyen estrategias diferentes.

Este detalle se vuelve mucho más importante dentro de la optimización real.

---

## 5. Espacio de optimización publicado

### 5.1 Rango de inputs

| Input | Inicio | Fin | Paso | Número de valores |
|---|---:|---:|---:|---:|
| `NumMAs_1_2` | 1 | 2 | 1 | 2 |
| `MA1Type` | 1 | 3 | 1 | 3 |
| `MA1Length` | 10 | 40 | 1 | 31 |
| `MA2Type` | 1 | 3 | 1 | 3 |
| `MA2Length` | 45 | 70 | 1 | 26 |

Número bruto de filas por optimización:

$$
2\times3\times31\times3\times26=14,508
$$

### 5.2 Configuraciones funcionalmente duplicadas

Cuando:

```text
NumMAs_1_2 = 1
```

los inputs siguientes se ignoran:

```text
MA2Type
MA2Length
```

Sin embargo, el optimizador sigue recorriendo:

```text
3 tipos MA2 × 26 longitudes MA2 = 78
```

variantes idénticas para cada combinación real de MA1.

Configuraciones únicas de una media:

$$
3\times31=93
$$

Filas brutas asignadas a ese modo:

$$
93\times78=7,254
$$

Por tanto:

> Cada estrategia única de una media puede aparecer repetida 78 veces con el mismo comportamiento, sólo porque cambian inputs que no se consumen.

Configuraciones únicas de dos medias:

$$
3\times31\times3\times26=7,254
$$

Total funcionalmente único por mercado:

$$
93+7,254=7,347
$$

No son 14.508 hipótesis económicas diferentes.

### 5.3 Consecuencia sobre los rankings

La revista informa del “highest ranking for a 1-line strategy”. Ese ranking puede estar distorsionado porque las filas repetidas de una misma estrategia ocupan múltiples posiciones consecutivas.

Ejemplo conceptual:

```text
una configuración 1-line obtiene PnL X

el optimizador puede producir 78 filas con PnL X
porque MA2Type y MA2Length son irrelevantes
```

Sin el informe completo no sabemos si TradeStation elimina esas repeticiones visualmente. El contrato científico debe hacerlo antes de comparar rankings.

### 5.4 Número total de evaluaciones del artículo

La revista describe:

```text
6 optimizaciones individuales
+
1 optimización de Portfolio Maestro
```

Si se usó el mismo grid completo en las siete ejecuciones:

```text
14,508 × 7 = 101,556 filas de backtest
```

Número aproximado de combinaciones efectivas no duplicadas:

```text
7,347 × 7 = 51,429 contextos modelo-mercado
```

Esto no incluye posibles pruebas previas, configuraciones descartadas ni ajustes editoriales.

---

## 6. Resultados publicados

## 6.1 Configuración

```text
Símbolos:
EURUSD
GBPUSD
AUDUSD
USDCAD
USDJPY
USDCHF

Trade size:
100,000 unidades de divisa

Comisiones:
$5 por lado

Historia:
5 años, 01/10/2009–31/12/2014
con reserva para MaxBarsBack

Bar interval:
Daily
```

No se publica en esa tabla:

```text
slippage
spread bid/ask
swap/carry
interest differential
capital inicial por símbolo
margin model
session cutoff
fuente exacta del daily open
```

### 6.2 Ejemplo EURUSD de la página física 7

La primera fila visible del informe de optimización muestra:

```text
NumMAs = 2
MA1 = SMA 40
MA2 = EMA 52
Net Profit = $58,140
Trades = 37
Percent Profitable = 62.16%
```

La fila resaltada en el ranking 17 muestra dos medias simples:

```text
MA1 = SMA 24
MA2 = SMA 68
Net Profit = $41,506
Trades = 24
Percent Profitable = 41.67%
```

La revista utiliza esta comparación para afirmar que mezclar tipos produjo mejor resultado in-sample que el par clásico SMA/SMA.

Lo único demostrado es:

```text
en esta muestra
y dentro de este grid
la mejor fila visible usa SMA/EMA
```

No demuestra que el tipo de media sea causal ni estable.

### 6.3 Ranking de estrategias de una media

| Símbolo | Mejor ranking 1-line publicado |
|---|---:|
| EURUSD | No aparece en top 200 |
| GBPUSD | 58 |
| AUDUSD | No aparece en top 200 |
| USDCAD | No aparece en top 200 |
| USDJPY | No aparece en top 200 |
| USDCHF | 180 |

La revista concluye que el enfoque de dos medias fue mejor en todos los tests.

Esa conclusión debe matizarse porque:

```text
se selecciona por ranking in-sample
no se muestra distribución completa
las filas 1-line pueden estar duplicadas
las reglas 1-line y 2-line tienen distinta frecuencia de trading
```

### 6.4 Ranking de dos SMA

| Símbolo | Mejor ranking SMA/SMA publicado |
|---|---:|
| EURUSD | 17 |
| GBPUSD | No aparece en top 200 |
| AUDUSD | 3; siguiente aparición 37 |
| USDCAD | 113 |
| USDJPY | 8; siguientes 13 y 25 |
| USDCHF | 182 |

La tabla no demuestra que SMA/SMA sea inferior universalmente. AUDUSD y USDJPY muestran resultados SMA/SMA cerca de la parte superior.

### 6.5 Mejor combinación de tipos por par

| Símbolo | MA1 | MA2 |
|---|---|---|
| EURUSD | SMA | EMA |
| GBPUSD | SMA | WMA |
| AUDUSD | WMA | SMA |
| USDCAD | SMA | WMA |
| USDJPY | SMA | WMA |
| USDCHF | SMA | EMA |

Cinco de los seis pares seleccionan una SMA como media corta. La excepción es AUDUSD.

La media larga seleccionada se reparte entre WMA, EMA y una SMA. Por tanto, la frase “weighted average for MA2” describe una familia amplia, no un único mecanismo.

### 6.6 Óptimo de Portfolio Maestro

El resultado agregado publicado es:

| Input | Resultado óptimo |
|---|---:|
| `NumMAs_1_2` | 2 |
| `MA1Type` | 1 = SMA |
| `MA1Length` | 39 |
| `MA2Type` | 3 = EMA |
| `MA2Length` | 50 |

La página física 8 muestra una curva agregada ascendente, pero también:

```text
drawdowns amplios
un descenso prolongado entre finales de 2011 y 2013
periodos extensos sin nuevos máximos
exposición casi permanente
```

El artículo no publica para este portfolio:

```text
Profit Factor
Sharpe
maximum drawdown exacto
número de operaciones
resultado por par
contribución marginal
correlación de PnL
turnover
coste de financiación
```

La curva visual no sustituye esas métricas.

---

## 7. Qué edge pretende capturar

La hipótesis general es:

> El precio muestra persistencia temporal; el cruce de una representación rápida y otra lenta identifica cambios suficientemente importantes en la dirección de la tendencia.

La mezcla de filtros responde a otra hipótesis:

> Distintos kernels de suavizado separan señal y ruido de forma diferente; combinar un promedio de igual peso con otro que enfatiza observaciones recientes podría detectar transiciones de tendencia mejor que dos filtros idénticos.

Es plausible como familia de investigación. El artículo no demuestra cuál de estas explicaciones produce el PnL.

### Hipótesis alternativas

Los resultados podrían explicarse por:

```text
trend following general de la muestra 2009–2014
selección del mejor punto entre miles
sesgo hacia longitudes cercanas al borde del grid
exposición USD compartida
carry de divisas
costes incompletos
regímenes excepcionales posteriores a la crisis
un único periodo favorable
```

---

## 8. Problemas científicos y técnicos

### 8.1 Selección masiva in-sample

El artículo selecciona ganadores después de decenas de miles de pruebas. No presenta:

```text
training set
validation set
holdout
walk-forward
nested optimization
White Reality Check
Hansen SPA
PBO
Deflated Sharpe Ratio
```

La probabilidad de encontrar una curva atractiva por azar es material.

### 8.2 El portfolio no es un OOS

Portfolio Maestro utiliza los mismos cinco años y el mismo grid. Agregar mercados no crea automáticamente una muestra independiente.

Es:

```text
otra función objetivo
sobre los mismos datos
```

### 8.3 Los seis pares comparten USD

Todos incluyen USD. La muestra no contiene seis apuestas macroeconómicas independientes.

Ejemplos:

```text
EURUSD, GBPUSD y AUDUSD:
USD está en la segunda pata

USDCAD, USDJPY y USDCHF:
USD está en la primera pata
```

Una tendencia general del dólar puede hacer que varias estrategias ganen simultáneamente.

### 8.4 Riesgo agregado no normalizado

Cada par opera 100.000 unidades, pero:

```text
volatilidad
valor de pip
margen
carry
liquidez
```

no son idénticos.

Un portfolio de tamaño nominal igual no es un portfolio de riesgo igual.

### 8.5 Casi 100% de exposición

La curva publicada incluye una estrategia siempre long o short. No existe un benchmark flat ni cash.

Debe compararse con:

```text
buy-and-hold o carry relevante
signo aleatorio con misma exposición
trend simple preregistrado
volatility-scaled time-series momentum
```

### 8.6 Coste de reversal

Cada cruce opuesto cierra y abre. Eso implica dos lados de transacción. El informe dice $5 por lado, pero no publica spread ni slippage.

En FX, el spread puede variar por:

```text
par
hora de rollover
regímenes de volatilidad
festivos
```

### 8.7 Carry y financiación

Mantener FX casi continuamente genera interés positivo o negativo según el par y el sentido. No se indica si TradeStation incorpora:

```text
rollover diario
triple swap
cambios de tipos
```

Sin esa información, parte del PnL podría proceder de carry no modelado o faltar un coste real.

### 8.8 Dependencia de la definición del daily bar

Un “día” de FX no tiene un único cierre natural. La señal puede cambiar con:

```text
cutoff 17:00 New York
medianoche UTC
medianoche del broker
Sunday bar
DST
```

La revista no publica el session template.

### 8.9 Longitudes en los bordes

En EURUSD, muchas filas superiores utilizan MA1=39 o 40, muy cerca del máximo permitido de 40. Esto plantea una pregunta:

```text
¿el óptimo real está fuera del grid?
¿o el borde refleja selección accidental?
```

No se debe ampliar el grid después de ver esto sin registrar una nueva hipótesis.

### 8.10 Tipos de media y longitud no son comparables uno a uno

Una EMA de 50 y una SMA de 50 no tienen la misma respuesta temporal. Comparar sólo el número de barras mezcla:

```text
tipo de kernel
lag efectivo
frecuencia de cruce
```

La variable científicamente relevante podría ser el lag efectivo, no el nombre SMA/WMA/EMA.

### 8.11 Seed de EMA y MaxBarsBack

Los primeros valores dependen de:

```text
seed
historia previa cargada
MaxBarsBack
```

Una réplica con una librería distinta puede generar cruces diferentes al inicio.

### 8.12 Falta informe completo

No podemos evaluar de la curva de Portfolio Maestro:

```text
asimetría de trades
años perdedores
dependencia de un solo par
concentración temporal
turnover
```

### 8.13 Rankings y configuraciones duplicadas

La duplicación de MA2 ignorada en modo 1-line invalida una interpretación ingenua del ranking. El sistema de experimentos debe canonicalizar la configuración antes de contar trials.

---

## 9. Cómo debe implementarse en TSIS

### 9.1 La estrategia y el experimento son objetos distintos

```text
StrategySpecification:
reglas de una configuración concreta

ExperimentDefinition:
espacio de búsqueda completo

Trial:
una configuración ejecutada en un mercado y periodo

SelectionRule:
criterio para escoger candidato
```

No debe almacenarse únicamente el ganador.

### 9.2 Canonicalización

Cuando `NumMAs=1`:

```text
MA2Type = NOT_APPLICABLE
MA2Length = NOT_APPLICABLE
```

Dos trials que sólo difieren en inputs ignorados deben compartir:

```text
canonical_strategy_hash
```

### 9.3 Datos mínimos

Por símbolo y sesión:

```text
session_date
open_raw
close_signal_view
session_template_id
corporate_action_state si es equity
fx_roll_state si es spot FX
```

### 9.4 Estado de señal

```text
ma_mode
ma1_type
ma1_length
ma1_value
ma2_type
ma2_length
ma2_value
cross_state
position_before
scheduled_action
```

### 9.5 Ejecución

```text
señal:
close t

fill:
open t+1

reversal:
exit old position + enter new position
```

Debe conservarse una política explícita de:

```text
official_open
first_trade
first_valid_quote
next_bar_open del proveedor
```

### 9.6 Costes

```text
commission_per_side
spread_model
slippage_model
carry_model
financing_model
```

### 9.7 Portfolio

El portfolio debe informar:

```text
exposición por divisa
exposición neta USD
volatility contribution
correlation matrix
marginal PnL
turnover por par
```

### 9.8 Registro de la búsqueda

Por cada experimento:

```text
search_space_declared_before_run
raw_trial_count
canonical_trial_count
selection_metric
number_of_markets
number_of periods
random_seed si aplica
```

---

## 10. Pseudocódigo de referencia

```python
from dataclasses import dataclass
from enum import Enum


class MAType(Enum):
    SMA = 1
    WMA = 2
    EMA = 3


@dataclass(frozen=True)
class MAMConfig:
    num_mas: int
    ma1_type: MAType
    ma1_length: int
    ma2_type: MAType | None
    ma2_length: int | None

    def canonical(self) -> "MAMConfig":
        if self.num_mas == 1:
            return MAMConfig(
                num_mas=1,
                ma1_type=self.ma1_type,
                ma1_length=self.ma1_length,
                ma2_type=None,
                ma2_length=None,
            )
        return self


def moving_average(close, ma_type, length):
    if ma_type is MAType.SMA:
        return sma(close, length)
    if ma_type is MAType.WMA:
        return wma(close, length)
    if ma_type is MAType.EMA:
        return ema_tradestation_compatible(close, length)
    raise ValueError("unsupported MA type")


def generate_signal(state_t, state_t_minus_1, config):
    ma1_t = moving_average(
        state_t.close_history,
        config.ma1_type,
        config.ma1_length,
    )
    ma1_prev = moving_average(
        state_t_minus_1.close_history,
        config.ma1_type,
        config.ma1_length,
    )

    if config.num_mas == 1:
        if state_t.close > ma1_t and state_t_minus_1.close <= ma1_prev:
            return "TARGET_LONG"
        if state_t.close < ma1_t and state_t_minus_1.close >= ma1_prev:
            return "TARGET_SHORT"
        return "NO_CHANGE"

    ma2_t = moving_average(
        state_t.close_history,
        config.ma2_type,
        config.ma2_length,
    )
    ma2_prev = moving_average(
        state_t_minus_1.close_history,
        config.ma2_type,
        config.ma2_length,
    )

    if ma1_t > ma2_t and ma1_prev <= ma2_prev:
        return "TARGET_LONG"
    if ma1_t < ma2_t and ma1_prev >= ma2_prev:
        return "TARGET_SHORT"
    return "NO_CHANGE"


def execute_next_open(signal, position, next_open, costs):
    if signal == "TARGET_LONG" and position <= 0:
        close_existing_position_if_needed()
        open_long(next_open, costs)

    elif signal == "TARGET_SHORT" and position >= 0:
        close_existing_position_if_needed()
        open_short(next_open, costs)
```

---

## 11. Cómo demostrar o destruir el supuesto edge

### Fase 1 — Réplica del grid publicado

```text
mismos seis pares
01/10/2009–31/12/2014
mismo cutoff daily
mismos rangos
100.000 unidades
$5 por lado
```

Checksums:

```text
EURUSD top visible:
SMA40 / EMA52
$58,140
37 trades
62.16%

Portfolio candidate:
SMA39 / EMA50
```

### Fase 2 — Canonicalización

Verificar que:

```text
93 estrategias 1-line únicas
7,254 estrategias 2-line únicas
7,347 configuraciones efectivas
```

No contar 78 veces cada modo 1-line.

### Fase 3 — Verdadero OOS postpublicación

Congelar antes de mirar datos posteriores:

```text
SMA39 / EMA50
seis pares originales
misma ejecución
```

Periodo:

```text
primera sesión posterior a la publicación verificable
hasta la última sesión completa disponible
```

Segmentar al menos:

```text
2015–2017
2018–2020
2021–2023
2024–2026
```

### Fase 4 — Selección anidada

En cada ventana:

```text
train:
seleccionar tipos y longitudes

validation:
elegir candidato

test:
evaluar una sola vez
```

No optimizar y evaluar sobre la misma muestra.

### Fase 5 — Benchmark de familia

Comparar con:

```text
SMA simple preregistrada
12-month time-series momentum
buy-and-hold/carry
signo aleatorio con igual turnover
estrategia always-long / always-short
```

### Fase 6 — Atribución por par

Informar:

```text
PnL individual
Sharpe individual
correlación entre PnL
contribución al drawdown
exposición USD
```

### Fase 7 — Costes reales

Escenarios:

```text
spread histórico
slippage
rollover/carry
reversal cost
cutoff alternativo
```

### Fase 8 — Robustez de tipos

En lugar de seleccionar una fila, agrupar por:

```text
SMA/SMA
SMA/WMA
SMA/EMA
WMA/SMA
...
```

Comparar distribuciones de performance, no sólo máximos.

### Fase 9 — Robustez de longitud

Evaluar si existe una meseta alrededor de:

```text
MA1 39
MA2 50
```

Un único pico aislado sería evidencia débil.

### Fase 10 — Corrección por múltiples pruebas

Aplicar:

```text
White Reality Check o Hansen SPA
Deflated Sharpe Ratio
PBO/CSCV
block bootstrap
```

El número de trials debe basarse en configuraciones canónicas, pero también debe reconocer que los trials están correlacionados.

---

## 12. Variantes que sólo deben estudiarse después de la réplica

### Variante A — Volatility scaling

Dimensionar cada par para una contribución de riesgo similar.

### Variante B — Flat zone

No revertir inmediatamente cuando la diferencia entre medias es mínima.

```text
|MA1 - MA2| / ATR < threshold -> flat
```

### Variante C — Slope filter

Exigir pendiente coherente, no sólo un cruce.

### Variante D — Distance oscillator

La propia revista propone estudiar la distancia entre las medias:

$$
D_t=\frac{MA1_t-MA2_t}{ATR_t}
$$

Puede utilizarse para:

```text
medir persistencia
escalar posición
reducir en sobreextensión
```

### Variante E — Stops

Añadir trailing stop monetario, porcentual o basado en volatilidad.

### Variante F — Ensemble de longitudes

Evitar escoger un único par de longitudes y combinar señales de una región estable.

### Variante G — Kernels con lag equivalente

Comparar SMA/WMA/EMA ajustando el lag efectivo, no la longitud nominal.

---

## 13. Encaje en Market State y Event State

### Market State

```text
close
ma1_value
ma2_value
ma_distance
ma_distance_atr
ma1_slope
ma2_slope
volatility_state
fx_carry_state
broad_market_context
```

### Evento

```text
event_type:
moving_average_cross

subject_scope:
single_instrument

decision_timestamp:
session_close_t

attributes:
mode
ma1_type
ma1_length
ma2_type
ma2_length
cross_direction
```

### Outcome

```text
next_open_gap
holding_period
return_until_next_cross
MFE
MAE
costs
carry
```

### Distinción clave

```text
Evento:
se ha producido un cruce

Estrategia:
revertir la posición en la apertura siguiente

Experimento:
buscar el mejor tipo y longitud
```

No son el mismo objeto.

---

## 14. Transferencia a small caps, futuros y otros mercados

### Small caps

Como baseline es implementable, pero debe incorporar:

```text
halts
gaps
corporate actions
borrow
spread
slippage
survivorship
universe point-in-time
```

Una media sobre precios ajustados puede producir señal; la ejecución debe utilizar precios raw operables.

No debe asumirse que el resultado FX se transfiere.

### Futuros

Requiere:

```text
roll calendar
contratos físicos
back-adjustment sólo para señal si está gobernado
PnL en contrato real
margin y multiplier
```

### FX

Requiere definir:

```text
session cutoff
Sunday bars
DST
bid/ask
carry
fuente de open
```

### Uso recomendado en TSIS

La Moving Average Machine merece existir como:

```text
BASELINE_FAMILY
EXPERIMENT_GOVERNANCE_TEST
MULTIPLE_TESTING_CASE
```

No como candidato prioritario de edge para small caps.

---

## 15. Veredicto de Moving Average Machine

```text
IMPLEMENTAR:
sí, como harness de experimentos y baseline

REPLICAR EL GRID:
sí, una vez, para reconciliar

ACEPTAR SMA39/EMA50 COMO EDGE:
no

OPTIMIZAR DE NUEVO SIN HOLDOUT:
no

VALOR PRINCIPAL PARA TSIS:
gobernanza de búsqueda y control de data snooping

LIVE:
no
```

Gate propuesto:

```text
MAM-CANONICAL-SEARCH-SPACE-AND-POSTPUBLICATION-OOS-GATE
```

---

# Parte II — Estrategia 006: Bar Range Expansion Strategy

## 1) Identificación y rendimiento

- **ID de estrategia:** `SCC-2015-03-STRAT-006`
- **Artículo:** *Bar Range Expansion Strategy*
- **Autor:** **Frederic Palmliden, CMT**
- **Páginas físicas:** 11–15
- **Páginas impresas:** 9–13
- **Estilo declarado:** Bar pattern
- **Mercados declarados:** Equities, futures, forex
- **Horizonte declarado:** Swing trading
- **Mercado del test:** E-mini S&P 500
- **Símbolo:** `@ES=107XN`
- **Bar interval:** Daily
- **Intrabar resolution:** 30 minutos mediante Look-Inside-Bar Back-testing
- **Historia:** 10 años terminando 31/12/2014
- **Archivos:** `.ELD` y workspace `.tsw`

### Inputs publicados

| Input | Default | Función declarada |
|---|---:|---|
| `LMult` | 0.7 | Multiplicador de rango para entrada long |
| `SMult` | 1.0 | Multiplicador de rango para entrada short |
| `ProfitPt` | 0 | Beneficio mínimo en puntos para salida en el primer open rentable |
| `TrailBar` | 7 | Ventana del stop por lowest low / highest high |
| `MyStop` | 1,750 | Stop loss monetario por trade |

### Evidencia adicional del ZIP

El workspace `TSL Bar Range Expansion.tsw` confirma:

```text
chart:
@ES=107XN Daily [CME]
E-mini S&P 500 Custom Continuous Contract

analysis technique:
TSL:Bar Range Expansion

inputs:
LMult
SMult
ProfitPt
TrailBar
MyStop

TradeStation version string:
9.01.00.12348
```

El `.ELD` no es legible como source EasyLanguage en este entorno. Por ello no pueden resolverse directamente:

```text
orden exacto de evaluación de exits
rounding a tick
reglas de reversal
semántica de first profitable open
SetStopPosition vs SetStopContract
persistencia de órdenes
```

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí**, pero necesita motor intrabar/event-driven. |
| ¿Puede replicarse sólo con barras daily? | **No de forma fiable.** |
| ¿El LIBB de 30 minutos resuelve toda la secuencia? | **No.** Reduce ambigüedad, pero no la elimina dentro de cada subbarra. |
| ¿La tesis económica es plausible? | **Sí:** expansión de rango como señal de momentum. |
| ¿El 77% ganador demuestra edge? | **No.** La pérdida media es 2.44 veces la ganancia media. |
| ¿El continuo usado es ejecutable? | **No.** Es una serie sintética para investigación. |
| ¿Está lista para real? | **No.** |

Clasificación TSIS:

```text
SOURCE_REPRODUCTION_CANDIDATE
INTRABAR_SEQUENCE_CRITICAL
DUAL_STOP_ORDER_CRITICAL
CONTINUOUS_FUTURES_RECONCILIATION_REQUIRED
EXIT_ATTRIBUTION_REQUIRED
POSTPUBLICATION_OOS_AVAILABLE
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 2. Qué estrategia es realmente

La estrategia calcula un umbral de expansión respecto del **open de cada nueva sesión**.

En cada día dispone dos órdenes potenciales:

```text
buy stop por encima del open
sell-short stop por debajo del open
```

La distancia se construye con el rango medio de las cuatro sesiones anteriores.

No intenta predecir de antemano la dirección. Espera a que el mercado demuestre una expansión intradía suficientemente grande y entra en la dirección del movimiento.

Después gestiona la posición mediante:

```text
1. salida en el primer open rentable
2. stop de canal de siete barras
3. stop monetario fijo
4. time exit
5. posible reversal por señal contraria
```

El artículo dice que se generaban posibles entradas todos los días y que una gran mayoría de trades se cerró en el primer open rentable o fue revertida.

Por tanto, no es sólo un volatility breakout. Es un sistema compuesto por:

```text
entry trigger
overnight harvesting
rolling channel stop
tail stop
time stop
reversal engine
```

---

## 3. Reconstrucción matemática de la entrada

### 3.1 Rango de barra

Para una sesión `t`:

$$
R_t=H_t-L_t
$$

La revista habla de bar range, no de true range.

El ejemplo de la página física 12 muestra cuatro rangos:

```text
21.25
24.00
23.75
35.00
```

Su media es:

$$
\frac{21.25+24+23.75+35}{4}=26
$$

### 3.2 Rango medio disponible antes de la nueva sesión

Para la nueva sesión `u`:

$$
\overline{R}_{u-1}^{(4)}=
\frac{R_{u-1}+R_{u-2}+R_{u-3}+R_{u-4}}{4}
$$

Toda esa información es observable al cierre anterior.

### 3.3 Apertura de la nueva sesión

Cuando se conoce `O_u`, se activan los niveles:

$$
LongStop_u=O_u+LMult\cdot\overline{R}_{u-1}^{(4)}
$$

$$
ShortStop_u=O_u-SMult\cdot\overline{R}_{u-1}^{(4)}
$$

Con defaults:

$$
LongStop_u=O_u+0.7\overline{R}
$$

$$
ShortStop_u=O_u-1.0\overline{R}
$$

La lógica es asimétrica: se exige una caída mayor para abrir short.

### 3.4 Ejemplo gráfico

La página física 12 utiliza deliberadamente multiplicadores iguales a 1 para simplificar:

```text
open = 1987.75
average range = 26
long = 2013.75
short = 1961.75
```

El high posterior supera 2013.75 y activa long.

Con el default `LMult=0.7`, el nivel matemático sería:

```text
1987.75 + 0.7 × 26 = 2005.95
```

Ese precio no coincide con el tick de 0.25 del ES. El artículo no explica:

```text
redondeo al tick superior
redondeo al tick más cercano
uso del precio decimal interno
```

La réplica exacta necesita el código o un checksum de órdenes.

### 3.5 Dos-stage decision

La señal no puede cerrarse por completo en el cierre anterior, porque el nivel depende del open futuro.

Debe modelarse así:

```text
close u-1:
calcular average_range_4
crear entry_intent

open u:
observar open
materializar long_stop y short_stop
activar órdenes

durante u:
procesar eventos intrabar
```

Esto es diferente de un backtest que fija todos los precios al cierre anterior.

### 3.6 Activación intradía

Long:

```text
si el precio alcanza LongStop_u -> comprar
```

Short:

```text
si el precio alcanza ShortStop_u -> vender en corto
```

Ambas órdenes pueden ser alcanzadas en la misma sesión.

---

## 4. Secuencia intrabar y reversals

### 4.1 Por qué OHLC daily es insuficiente

Supongamos:

```text
High >= LongStop
Low <= ShortStop
```

Una barra diaria sólo demuestra que ambos niveles se tocaron. No dice cuál fue primero.

Los caminos posibles incluyen:

```text
open -> long trigger -> short trigger
open -> short trigger -> long trigger
open -> ambos dentro de la misma subbarra
```

El PnL puede cambiar por completo.

### 4.2 LIBB de 30 minutos

TradeStation utilizó Look-Inside-Bar Back-testing a 30 minutos. Eso aporta una secuencia de subbarras, pero dentro de una subbarra de 30 minutos sigue existiendo el mismo problema si se alcanzan varios niveles.

Por tanto:

```text
LIBB 30m > OHLC daily
pero
LIBB 30m != secuencia de ticks
```

### 4.3 Reversal

El artículo afirma que una gran mayoría de posiciones fue “simply reversed” o cerrada en el primer open rentable.

Eso implica que, estando long, una orden short puede:

```text
cerrar long
abrir short
```

Y viceversa.

El backtester debe distinguir:

```text
exit fill
new entry fill
coste de ambos lados
nuevo entry price
reinicio del holding period
```

### 4.4 Pyramiding

No se publica si una nueva señal del mismo lado añade contratos. El informe muestra máximo de un contrato, por lo que la réplica debe asumir:

```text
no pyramiding
```

hasta que el `.ELD` importado demuestre otra cosa.

### 4.5 Orders active only for one session

El texto sugiere que los niveles se recalculan cada día desde el open del día. Por tanto, una orden no ejecutada debe caducar al terminar la sesión.

Debe registrarse explícitamente:

```text
valid_from = open_u
valid_until = close_u
```

---

## 5. Reconstrucción de las salidas

## 5.1 Primera apertura rentable

Para una posición long con precio de entrada `E`:

```text
si el open de una sesión posterior permite beneficio neto
incluyendo comisión
vender en ese open
```

Para una posición short, la condición se invierte.

Con `ProfitPt=0`, no exige beneficio adicional más allá de cubrir costes.

El informe publica:

```text
commission = $2.36
largest losing trade = -$1,754.72
MyStop = $1,750
```

La identidad:

$$
1750+2\times2.36=1754.72
$$

es una evidencia muy fuerte de que el informe descuenta $2.36 por lado y que el stop monetario se ejecuta a $1,750 antes de costes de ida y vuelta.

Para ES, con `BigPointValue = $50`, cubrir $4.72 equivale a:

$$
4.72/50=0.0944\text{ puntos}
$$

Como el tick es 0.25, un open favorable de un tick ya supera las comisiones del modelo.

### 5.2 Momento más temprano de esta salida

La entrada ocurre intradía después del open. Por eso la “first profitable open” no puede ser el mismo open de entrada.

El primer candidato normal es:

```text
open de la siguiente sesión
```

Aun así, la posición puede salir el mismo día de entrada por:

```text
MyStop
reversal
posible stop de canal, según código
```

### 5.3 Stop de siete barras

Para long:

$$
LongChannelStop_t=\min(L_t,L_{t-1},...,L_{t-6})
$$

Para short:

$$
ShortChannelStop_t=\max(H_t,H_{t-1},...,H_{t-6})
$$

El artículo lo denomina trailing stop, pero una ventana rolling no es necesariamente monotónica.

En una posición long, si aparece un nuevo mínimo y no se ejecuta antes por la secuencia del motor, el valor calculado podría bajar. Un trailing stop estricto nunca se alejaría del precio.

TSIS debe distinguir:

```text
ROLLING_CHANNEL_STOP
```

de:

```text
MONOTONIC_TRAILING_STOP
```

### 5.4 Stop monetario

```text
MyStop = $1,750 por posición de un contrato
```

La coincidencia exacta con la mayor pérdida publicada sugiere que el stop fue alcanzado y que el motor añadió $4.72 de comisiones.

El código puede utilizar `SetStopLoss`. La semántica exacta de per-position o per-contract debe verificarse, aunque con un contrato no cambia el resultado.

### 5.5 Time exit

El artículo dice:

```text
cerrar si el holding period supera cinco barras
es decir, en el open de la sexta barra
```

Debe fijarse una convención sin ambigüedad:

```text
entry_bar_index
bars_completed_since_entry
scheduled_time_exit_open
```

### 5.6 Prioridad entre salidas

En una misma subbarra pueden coexistir:

```text
channel stop
money stop
opposite entry/reversal
```

En un open pueden coexistir:

```text
first profitable open
time exit
nueva orden potencial del día
```

El PDF no publica la prioridad. El resultado exacto depende de ella.

### 5.7 Atribución obligatoria

Cada trade debe registrar:

```text
exit_reason:
FIRST_PROFITABLE_OPEN
CHANNEL_STOP
MONEY_STOP
TIME_EXIT
REVERSAL
```

Sin esta atribución no puede saberse qué componente genera el PnL.

---

## 6. Resultados publicados

### 6.1 Configuración

```text
Initial Capital: $10,000
Trade Size: 1 contrato
Commission: $2.36 por lado inferido
Slippage: $0
History: 10 años terminando 31/12/2014
Bar Interval: Daily
Look-Inside-Bar: 30 minutos
Continuous contract: @ES=107XN
Back adjustment: no
Rollover trigger: siete días antes de expiración
```

### 6.2 Resultado agregado

| Métrica | Resultado |
|---|---:|
| Total Net Profit | $66,257.66 |
| Gross Profit | $244,312.24 |
| Gross Loss | -$178,054.58 |
| Profit Factor | 1.37 |
| Total Trades | 822 |
| Winning Trades | 633 |
| Losing Trades | 189 |
| Percent Profitable | 77.01% |
| Avg. Trade Net Profit | $80.61 |
| Avg. Winning Trade | $385.96 |
| Avg. Losing Trade | -$942.09 |
| Avg Win / Avg Loss | 0.41 |
| Largest Winning Trade | $3,332.78 |
| Largest Losing Trade | -$1,754.72 |
| Max Consecutive Winners | 26 |
| Max Consecutive Losers | 4 |
| Avg Bars in Winners | 2.55 |
| Avg Bars in Losers | 2.68 |
| Account Size Required | $5,068.26 |
| Return on Initial Capital | 662.58% |
| Annual Rate of Return | 20.73% |
| Return Retracement Ratio | 0.26 |
| RINA Index | 290.34 |
| Trading Period | 9 años, 9 meses, 17 días |
| Percent Time in Market | 37.48% |

### 6.3 La asimetría del payoff

$$
\frac{942.09}{385.96}\approx2.44
$$

La pérdida media es aproximadamente 2.44 veces la ganancia media.

La expectativa positiva depende de mantener una tasa ganadora muy elevada:

$$
E\approx0.7701(385.96)-0.2299(942.09)
$$

antes de pequeñas diferencias de redondeo.

Por eso un descenso moderado del hit rate puede destruir el edge.

### 6.4 Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Net Profit | $39,756.96 | $26,500.70 |
| Gross Profit | $140,713.40 | $103,598.84 |
| Gross Loss | -$100,956.44 | -$77,098.14 |
| Profit Factor | 1.39 | 1.34 |
| Trades | 507 | 315 |
| Percent Profitable | 79.88% | 72.38% |
| Avg Trade Net Profit | $78.42 | $84.13 |
| Avg Winning Trade | $347.44 | $454.38 |
| Avg Losing Trade | -$989.77 | -$886.19 |
| Ratio Avg Win/Loss | 0.35 | 0.51 |
| Largest Winner | $2,232.78 | $3,332.78 |
| Largest Loser | -$1,754.72 | -$1,754.72 |
| Max Consecutive Winners | 23 | 12 |
| Max Consecutive Losers | 3 | 6 |
| Avg Bars Winners | 2.59 | 2.46 |
| Avg Bars Losers | 2.80 | 2.54 |

Aproximadamente:

```text
60% del beneficio neto proviene de longs
40% de shorts
```

El lado short tiene menos operaciones y menor porcentaje ganador, pero mayor ganancia media y expectativa media por trade.

### 6.5 Drawdown

La curva underwater de la página física 13 y la curva detallada de la página 15 muestran drawdowns iniciales cercanos o superiores al 30%.

El artículo reconoce que:

```text
30%+ puede hacer la estrategia intratable para muchos operadores
```

La curva ascendente posterior no elimina el riesgo de secuencia. Iniciar la estrategia en otra fecha podría haber producido una experiencia muy distinta.

### 6.6 Slippage cero

El informe utiliza:

```text
$0.00 slippage
```

Esto es especialmente problemático porque las entradas y varias salidas son órdenes stop intradía. Los stops suelen ejecutarse durante expansión de volatilidad, precisamente cuando el slippage puede ser mayor.

### 6.7 Rentabilidad sobre capital

El 662.58% se calcula sobre $10,000 durante casi diez años con un contrato ES. Esa cifra depende de:

```text
apalancamiento
margen histórico
no reinversión explícita
capital inicial pequeño
```

No debe compararse directamente con un retorno de cartera cash sin normalizar riesgo.

---

## 7. ¿Dónde podría estar el edge?

La hipótesis de entrada es:

> Un desplazamiento intradía grande respecto del rango reciente indica que nueva información u order flow está produciendo momentum que tiende a continuar durante un horizonte breve.

La salida en el primer open rentable plantea una hipótesis adicional:

> Parte del continuation edge persiste hasta el siguiente open, pero no necesariamente durante muchos días.

La asimetría `LMult=0.7`, `SMult=1.0` presupone:

> Los movimientos bajistas son más rápidos; para evitar ruido se exige una expansión más grande antes de vender en corto.

### Hipótesis alternativas

El PnL podría proceder de:

```text
prima de riesgo long del S&P 500
comportamiento overnight
orden de fills asumido por LIBB
roll artifacts
stop fills demasiado optimistas
slippage omitido
selección de multipliers
reversals rentables por construcción
```

---

## 8. Problemas científicos y técnicos

### 8.1 No hay OOS publicado

Los defaults, la lógica y las salidas se evalúan en la misma historia. No existe holdout.

### 8.2 Origen VolEx no equivale a validación

El artículo menciona la estrategia VolEx de Bill Cruz y Charlie Wright como antecedente. Esa genealogía conceptual no valida esta implementación concreta.

### 8.3 Dependencia de secuencia intrabar

Un modelo daily o incluso 30m puede decidir mal:

```text
qué entrada ocurrió primero
si un stop se ejecutó antes de un reversal
si ambos niveles se tocaron dentro de una subbarra
```

### 8.4 Stop fill assumptions

Un stop no garantiza fill exacto al precio de stop. Con gaps o movimientos rápidos, el fill real puede ser peor.

El modelo de slippage cero amplifica el optimismo.

### 8.5 Continuous futures sintético

`@ES=107XN` no es operable. La revista lo utiliza sin back adjustment y con roll siete días antes de expiración.

Aun así puede contener:

```text
saltos de roll
rangos artificiales
opens sintéticos
transiciones entre contratos
```

Una estrategia basada precisamente en rango y open es muy sensible a esos artefactos.

### 8.6 Operaciones que cruzan el roll

Debe saberse:

```text
qué contrato se mantenía
cómo se cierra
cómo se abre el nuevo
coste del spread de calendario
```

El continuo no resuelve esa ejecución física.

### 8.7 Nivel dependiente del open futuro

El precio de entrada sólo se conoce después de abrir la nueva sesión. La orden no puede preenviarse con precio definitivo durante la tarde anterior.

### 8.8 Tick rounding

`0.7 × average_range` puede producir precios inválidos para el tick del ES. El redondeo modifica:

```text
frecuencia de entrada
lado activado
PnL
```

### 8.9 Dos órdenes opuestas simultáneas

La estrategia tiene un componente OCO implícito o un motor de reversión. No se publica cuál.

Preguntas pendientes:

```text
¿se cancela la orden opuesta tras la primera entrada?
¿permanece y puede revertir?
¿se reactiva tras una salida?
```

La frase “simply reversed” sugiere que permanece en ciertos estados, pero no define todo el ciclo.

### 8.10 Múltiples exits sin prioridad publicada

Dos motores con las mismas barras pueden producir resultados distintos sólo por el orden de evaluación.

### 8.11 High win rate frágil

Con payoff 0.41, el break-even hit rate aproximado sin costes adicionales es:

$$
\frac{942.09}{942.09+385.96}\approx70.94\%
$$

El resultado publicado es 77.01%. El margen es de unos seis puntos porcentuales. Slippage y cambios de régimen pueden consumirlo.

### 8.12 Stop fijo no adaptativo

$1,750 representa:

```text
35 puntos ES
```

pero la volatilidad del ES cambió mucho entre 2005 y 2014. El mismo stop no expresa el mismo riesgo económico en todos los regímenes.

### 8.13 Multipliers asimétricos

La justificación “down moves take place more quickly” es plausible, pero no se publica:

```text
muestra usada para decidir 0.7 y 1.0
robustez alrededor de esos valores
resultado simétrico
```

### 8.14 First profitable open puede fabricar hit rate alto

Cerrar en el primer open ligeramente positivo convierte muchas ganancias en pequeños trades, mientras deja que las pérdidas continúen hasta stops más amplios.

Esto explica naturalmente:

```text
77% win rate
avg winner $386
avg loser -$942
```

No es una anomalía; es el diseño del exit.

### 8.15 El channel stop puede aflojarse

`Lowest(Low,7)` y `Highest(High,7)` no son necesariamente monotónicos. Debe verificarse si el código bloquea el stop para que sólo se acerque.

### 8.16 Coste de reversals

Un reversal implica dos lados. Si ocurre durante una expansión, el slippage puede ser doblemente adverso.

### 8.17 Sesión no documentada

No se publica la plantilla exacta de sesión del ES daily:

```text
RTH
ETH
23-hour
settlement cutoff
DST
```

Eso cambia el open, high, low y range.

### 8.18 Look-Inside-Bar no es tick replay

El artículo usa 30m, que es una mejora honesta respecto de daily OHLC, pero no prueba exactitud de ejecución.

---

## 9. Cómo debe implementarse en TSIS

### 9.1 Separar contexto previo y activación

Al cierre `t`:

```text
avg_range_4
LMult
SMult
entry_intent_id
```

En el open `t+1`:

```text
session_open
long_stop
short_stop
```

### 9.2 Motor de eventos intradía

Ordenar por timestamp:

```text
trades
quotes
bar opens
stop activations
fills
exit events
```

La versión científica debe usar como mínimo 1m; la reconciliación final idealmente trades/quotes.

### 9.3 Estado OCO/reversal

Registrar:

```text
long_order_status
short_order_status
position
pyramiding_policy
opposite_order_policy
```

### 9.4 Continuous para señal, contrato físico para ejecución

```text
reproduction_view:
@ES=107XN equivalente

execution_view:
contrato físico activo

roll_state:
old_contract
new_contract
roll_timestamp
spread_cost
```

### 9.5 Rounding

```text
long stop:
round upward to valid tick

short stop:
round downward to valid tick
```

Ésta es una política prudente; la réplica debe confirmar si coincide con TradeStation.

### 9.6 Modelo de stop fill

Escenarios:

```text
ideal stop price
next trade after trigger
quote ask para buy stop
quote bid para sell stop
adverse slippage distribution
```

### 9.7 Exits como módulos

```text
first_profitable_open_exit
rolling_channel_exit
money_stop_exit
time_exit
reversal_exit
```

Cada módulo genera una orden con prioridad y timestamp.

### 9.8 Lineage

Cada fill debe incluir:

```text
source_event_id
order_id
trigger_price
fill_price
slippage
active_contract
exit_reason
```

### 9.9 Estado de indisponibilidad

```text
MISSING_PREVIOUS_RANGE
MISSING_SESSION_OPEN
INVALID_TICK_SIZE
ROLL_MAPPING_UNAVAILABLE
INTRABAR_SEQUENCE_UNRESOLVED
NO_VALID_QUOTE
```

---

## 10. Pseudocódigo de referencia

```python
@dataclass
class BREConfig:
    long_mult: float = 0.7
    short_mult: float = 1.0
    profit_points: float = 0.0
    trail_bars: int = 7
    stop_dollars: float = 1750.0
    max_holding_bars: int = 5


def prepare_next_session_intent(completed_daily_bars, config):
    ranges = [bar.high - bar.low for bar in completed_daily_bars[-4:]]
    if len(ranges) < 4:
        return Unavailable("INSUFFICIENT_RANGE_HISTORY")

    return {
        "average_range_4": sum(ranges) / 4.0,
        "config": config,
    }


def activate_at_session_open(intent, session_open, tick_size):
    raw_long = session_open + intent["config"].long_mult * intent["average_range_4"]
    raw_short = session_open - intent["config"].short_mult * intent["average_range_4"]

    return {
        "long_stop": round_up_to_tick(raw_long, tick_size),
        "short_stop": round_down_to_tick(raw_short, tick_size),
        "valid_until": "SESSION_CLOSE",
    }


def process_market_event(event, state, orders, config):
    # Entries and reversals
    if event.trades_at_or_above(orders.long_stop):
        execute_target_long(state, event)

    if event.trades_at_or_below(orders.short_stop):
        execute_target_short(state, event)

    # Same-bar dollar stop
    if state.position != 0 and money_stop_hit(state, event, config.stop_dollars):
        exit_position(state, event, reason="MONEY_STOP")

    # Rolling channel stop
    if channel_stop_hit(state, event, config.trail_bars):
        exit_position(state, event, reason="CHANNEL_STOP")


def process_session_open(session_open_event, state, config, round_turn_cost):
    if state.position > 0:
        net_points = session_open_event.price - state.entry_price
        if net_points >= config.profit_points + round_turn_cost / state.big_point_value:
            exit_position(state, session_open_event, reason="FIRST_PROFITABLE_OPEN")

    elif state.position < 0:
        net_points = state.entry_price - session_open_event.price
        if net_points >= config.profit_points + round_turn_cost / state.big_point_value:
            exit_position(state, session_open_event, reason="FIRST_PROFITABLE_OPEN")

    if state.bars_held >= config.max_holding_bars:
        exit_position(state, session_open_event, reason="TIME_EXIT")
```

El pseudocódigo no fija silenciosamente la prioridad entre first-profit y time exit. Esa prioridad debe extraerse del `.ELD` o reconciliarse por trades.

---

## 11. Cómo demostrar o destruir el supuesto edge

### Fase 1 — Réplica del informe

Objetivos de checksum:

```text
822 trades
633 winners
189 losers
Net Profit $66,257.66
PF 1.37
largest loser -$1,754.72
exposure 37.48%
```

### Fase 2 — Reconciliación de exits

Contar por motivo:

```text
first profitable open
channel
money stop
time exit
reversal
```

El artículo sólo afirma cualitativamente que first-profit y reversal son mayoritarios.

### Fase 3 — Reconciliación intrabar

Comparar:

```text
daily OHLC
30m LIBB
5m
1m
trades/quotes
```

Medir cuántos trades cambian por resolución.

### Fase 4 — Contratos físicos

Reconstruir el roll de `107XN` y mapear cada señal al contrato ejecutable.

Comparar:

```text
continuous PnL
physical-contract PnL
roll cost
```

### Fase 5 — Verdadero OOS postpublicación

Congelar:

```text
LMult 0.7
SMult 1.0
ProfitPt 0
TrailBar 7
MyStop 1750
```

Evaluar desde la primera sesión posterior a la publicación verificable hasta 2026, sin cambiar parámetros.

### Fase 6 — Costes

Escenarios:

```text
$0 slippage
0.25 punto por stop
0.50 punto
1.00 punto
modelo condicional a volatilidad
```

Calcular break-even slippage.

### Fase 7 — Ablation de exits

Ejecutar:

```text
entry + first-profit only
entry + channel only
entry + money stop only
entry + time exit only
combinaciones preregistradas
```

Así se identifica el componente que aporta edge.

### Fase 8 — Dual-trigger audit

Para cada sesión:

```text
long_only_touched
short_only_touched
both_touched
either_touched
```

En `both_touched`, medir dependencia del orden.

### Fase 9 — Symmetry test

Comparar:

```text
0.7 / 1.0 publicado
1.0 / 1.0
0.7 / 0.7
multipliers volatility-calibrated
```

No seleccionar el mejor sin corrección por trials.

### Fase 10 — Regímenes

Segmentar por:

```text
VIX
realized volatility
bull/bear regime
overnight gap
trend state
crisis/non-crisis
```

### Fase 11 — Tail stress

Incluir:

```text
flash crash
limit moves
gaps
exchange interruptions
roll week
high-volatility opens
```

### Fase 12 — Bootstrap y múltiples pruebas

Debido a dependencia temporal y exits superpuestos:

```text
block bootstrap
stationary bootstrap
DSR/PBO si se optimiza
```

---

## 12. Variantes posteriores a la réplica

### Variante A — ATR en lugar de average range

$$
EntryDistance=k\cdot ATR_n
$$

Incluye gaps previos y puede estabilizar la escala.

### Variante B — Percentile breakout

Calibrar la expansión según percentil histórico, no un multiplicador fijo.

### Variante C — Session-segmented range

Separar:

```text
overnight range
RTH range
```

### Variante D — Volatility-scaled money stop

Sustituir $1,750 fijo por:

```text
k × ATR × BigPointValue
```

### Variante E — Monotonic channel stop

No permitir que el trailing stop se aleje de la posición.

### Variante F — Exit decomposition

Optimizar sólo después de demostrar que el evento de expansión tiene valor predictivo por sí mismo.

### Variante G — No reversal same-day

Cancelar la orden opuesta tras la primera entrada y comparar con la versión de reversal.

### Variante H — Close-to-next-open outcome study

Antes de diseñar la estrategia, estudiar el evento:

```text
expansión long/short
-> retorno intradía restante
-> overnight
-> siguiente sesión
```

---

## 13. Encaje en Market State y Event State

### Market State previo

```text
range_1
range_2
range_3
range_4
average_range_4
volatility_state
trend_state
session_template
roll_state
```

### Event State de activación

```text
event_type:
bar_range_expansion_order_activated

activation_timestamp:
session_open_u

attributes:
open
long_stop
short_stop
long_mult
short_mult
active_contract
```

### Event State de trigger

```text
event_type:
bar_range_expansion_triggered

trigger_side:
long | short

trigger_timestamp:
first legal market event
```

### Outcomes

```text
remaining_session_return
overnight_return
first_next_open_return
MFE
MAE
exit_reason
holding_bars
dual_trigger_state
```

### Distinción clave

```text
Evento:
el precio se ha expandido desde el open

Estrategia:
entrar por stop y aplicar cinco mecanismos de gestión
```

TSIS puede descubrir que el evento tiene información aunque la combinación publicada de exits no sea óptima.

---

## 14. Transferencia a small caps, equities y forex

### Small caps

La idea de expansión desde el open es muy relevante, pero el modelo de ES no se puede copiar directamente.

Deben incorporarse:

```text
gap premarket
halts
spread
liquidity
borrow
SSR
news catalyst
offerings
opening auction
```

En small caps, ambos niveles pueden cruzarse por prints aislados o spreads enormes. Se requieren quotes y reglas de calidad.

### Equities líquidas

Puede investigarse como opening range expansion, pero:

```text
corporate actions
session regular vs extended
auction fills
```

deben gobernarse.

### FX

No existe una apertura diaria universal. El nivel depende del cutoff elegido.

### Futuros

Es el dominio natural de la réplica, siempre usando:

```text
contrato físico
roll gobernado
session template explícito
```

---

## 15. Veredicto de Bar Range Expansion

```text
IMPLEMENTAR:
sí, como réplica event-driven

USAR DAILY OHLC SOLAMENTE:
no

ACEPTAR PF 1.37 COMO EDGE:
no

VALOR PRINCIPAL:
caso completo de entradas stop, secuencia intrabar y exits múltiples

RIESGO CENTRAL:
la ejecución real puede consumir la expectativa de $80.61 por trade

LIVE:
no
```

Gate propuesto:

```text
BRE-INTRABAR-SEQUENCE-PHYSICAL-FUTURES-AND-POSTPUBLICATION-OOS-GATE
```

---

# Parte III — Ideas adicionales de backtesting contenidas en el issue

## 1. Un generador de estrategias no es una estrategia

Moving Average Machine enseña que debe distinguirse:

```text
familia
configuración
trial
ganador
```

Guardar sólo el ganador elimina evidencia crítica sobre selección.

## 2. Inputs ignorados crean trials duplicados

Ésta es una de las lecciones más importantes del número.

```text
NumMAs=1
MA2Type y MA2Length no se consumen
```

El motor debe canonicalizar configuraciones antes de calcular número efectivo de pruebas.

## 3. “Funciona en varios mercados” no garantiza independencia

Seis pares FX compartiendo USD son observaciones correlacionadas. La diversificación debe medirse en PnL y factores, no por contar tickers.

## 4. Portfolio optimization puede ser otra forma de in-sample selection

Optimizar una función agregada en los mismos datos no crea un test nuevo.

## 5. El open futuro puede ser parte de la definición de la señal

BRE muestra un patrón de dos etapas:

```text
contexto conocido al cierre
nivel materializado al open
trigger durante la sesión
```

Esto debe representarse explícitamente en Event State.

## 6. Look-Inside-Bar es necesario, pero su resolución es parte del modelo

```text
30m
5m
1m
tick
```

pueden producir estrategias diferentes.

## 7. High win rate y buen payoff son dimensiones diferentes

BRE obtiene 77.01% de acierto, pero:

```text
avg win = $385.96
avg loss = -$942.09
```

El hit rate por sí solo no mide edge.

## 8. Exits deben auditarse por separado

La revista dedica más detalle a exits que la mayoría de artículos. TSIS debe conservar esa idea y registrar PnL por exit reason.

## 9. Continuous futures es una representación, no un instrumento

Puede ser útil para señal e investigación, pero la validación económica requiere contratos físicos.

## 10. Slippage cero es especialmente peligroso en stop entries

Las órdenes stop se ejecutan cuando el mercado ya se mueve en contra de la liquidez disponible.

## 11. La curva de capital no sustituye el informe

Moving Average Machine publica una curva agregada, pero no suficientes métricas. Una imagen ascendente no permite evaluar robustez.

## 12. Options Volume and Open Interest

La página física 10 promociona una suite de seis indicadores para detectar volumen y open interest de opciones anormalmente altos.

Clasificación:

```text
RESEARCH_NOTE
POTENTIAL_INFORMATION_OBJECT
NO_STRATEGY_RULES
NO_BACKTEST
NO_EDGE_EVIDENCE
```

Posible encaje futuro en TSIS:

```text
options_activity_context
unusual_call_volume
unusual_put_volume
open_interest_change
```

No debe confundirse con una estrategia validada.

---

# Parte IV — Priorización para TSIS

## 1. Orden recomendado

### Prioridad A — Moving Average Machine como gate de gobernanza experimental

No por su edge, sino porque permite validar:

```text
search-space registry
canonical hashes
ignored-input detection
trial accounting
selection audit
postpublication OOS
```

Es una buena prueba de la capa `08_EXPERIMENTS`.

### Prioridad B — Bar Range Expansion como gate del motor intrabar

Cuando existan datos futures gobernados, permitirá validar:

```text
orders activadas al open
stop entries
OCO/reversal
multiple exits
LIBB vs replay
physical contract mapping
```

## 2. Estado respecto de los datos actuales de TSIS

### MAM en equities

Puede probarse como baseline con datos diarios existentes, respetando:

```text
adjusted signal view
raw execution view
corporate actions
universe PIT
```

### MAM en FX

No debe darse por disponible hasta incorporar:

```text
FX daily source
session cutoff
bid/ask
carry
```

### BRE en ES

Requiere:

```text
ES physical contracts
continuous reconstruction
roll calendar
intraday bars o trades
session template
multiplier y tick history
```

## 3. Artefactos futuros derivados

Cuando se abran los gates físicos:

```text
SCC_2015_03_MAM_EXPERIMENT_GOVERNANCE_CONTRACT.md
SCC_2015_03_BRE_REPLICATION_CONTRACT.md
```

No deben crearse ahora como resúmenes duplicados.

## 4. Qué material adicional haría falta

El ZIP actual es suficiente para cerrar esta auditoría documental.

Para réplica exacta sería útil exportar desde TradeStation:

```text
EasyLanguage source como texto
Strategy Properties
MaxBarsBack
session template
trade list
optimization report completo
Portfolio Maestro report
Look-Inside-Bar properties
order fill assumptions
```

Sólo debe pedirse al abrir el gate correspondiente.

---

# Apéndice A — Integridad del paquete

## Archivos relevantes

```text
SCC Issue 3 Mar 2015.pdf
2015-03/Moving Average Machine/TSL MOV AVG MACHINE.ELD
2015-03/Moving Average Machine/TSL.Moving Average Machine.tsw
2015-03/Bar Range Expansion/TSL BAR RANGE EXPANSION.ELD
2015-03/Bar Range Expansion/TSL Bar Range Expansion.tsw
```

El PDF incluido dentro del ZIP es bit a bit idéntico al PDF cargado por separado.

## Tamaños

```text
PDF: 8,775,314 bytes
ZIP: 8,791,676 bytes
Moving Average Machine .ELD: 14,467 bytes
Moving Average Machine .tsw: 41,984 bytes
Bar Range Expansion .ELD: 7,357 bytes
Bar Range Expansion .tsw: 32,768 bytes
```

## SHA-256

```text
PDF:
af346efaa1ae49d040b81a5c1f5f60861083efe5cefb14157b0a3c429eb21aeb

ZIP:
c43bac11a753d46ab3336b2183e3d8d3ff2a4d2189c5ea12cb7a5de9b4b30fa0

Moving Average Machine .ELD:
59505ab20c369971467e13c9acbf98ee96f13d6f95160a0a585f88b7dac5fabd

Moving Average Machine .tsw:
169bbe78a6f4e26713c1fe84ba9db6aadafa41778805b43af1d612d38ab717d1

Bar Range Expansion .ELD:
140fca05c1c885da9c2c7183520637a5bba009b11627c0ad28a0fa09968959e3

Bar Range Expansion .tsw:
be97b3f74fe3ffc5940035964aee9d3a7cad4349f7b4bcd03fe99bfdc47f268c
```

## Metadata PDF

```text
Pages: 16
CreationDate: 2015-03-09 12:11:53 -04:00
Creator: Adobe InDesign CC 2014
Producer: Adobe PDF Library 11.0
```

## Limitación del paquete

```text
.tsw:
workspace OLE binario con strings y metadatos parcialmente legibles

.ELD:
contenedor propietario no legible como source EasyLanguage
en este entorno
```

No contiene exportaciones legibles de:

```text
source code
trade list
optimization report completo
portfolio report
session settings
```

---

# Referencias externas

Las siguientes referencias contextualizan la auditoría. No forman parte de la evidencia publicada por la revista.

## Documentación oficial TradeStation

[TS-AVERAGE]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/average_function_.htm

[TS-WAVERAGE]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/waverage_function_.htm

[TS-XAVERAGE]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/xaverage_function_.htm

[TS-BUY]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/word/buy_reserved_word_.htm

[TS-SELLSHORT]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/word/sellshort_reserved_word_.htm

[TS-LOWEST]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/lowest_function_.htm

[TS-SETSTOPLOSS]: https://help.tradestation.com/09_01/tsdevhelp/subsystems/elword/word/setstoploss_reserved_word_.htm

[TS-BUILTIN-STOPS]: https://help.tradestation.com/10_00/eng/tradestationhelp/elanalysis/el_procedures/strategy_built-in_stop_commands.htm

[TS-LIBB]: https://help.tradestation.com/10_00/eng/tradestationhelp/subsystems/spr_topics/report/look_inside_bar_back_testing_strategy_performance_report_.htm

[TS-IOG]: https://help.tradestation.com/09_01/tradestationhelp/orchart/about_intrabar_order_generation.htm

[TS-CONTINUOUS]: https://help.tradestation.com/10_00/eng/tradestationhelp/symbology/custom_continous_futures_symbology.htm

## Investigación y control de data snooping

[BLL-1992]: https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1992.tb04681.x

[STW-1999]: https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00163

[MOP-TSM]: https://w4.stern.nyu.edu/facdir/lpederse/papers/TimeSeriesMomentum.pdf

[DSR]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551

[PBO]: https://carmamaths.org/jon/backtest2.pdf

---

# Cierre del issue

El Issue 3 debe conservarse en TSIS como dos lecciones distintas:

```text
Moving Average Machine:
la búsqueda de parámetros es parte del objeto científico
y debe quedar gobernada

Bar Range Expansion:
la secuencia de ejecución es parte de la estrategia
y no puede reconstruirse honestamente con una sola barra diaria
```

Decisión final:

```text
ARCHIVE_STATUS:
AUDITED_COMPLETE

MAM_STATUS:
EXPERIMENT_GOVERNANCE_CANDIDATE

BRE_STATUS:
INTRABAR_REPLICATION_CANDIDATE

EDGE_ACCEPTED:
NO

ADDITIONAL_FILES_REQUIRED_NOW:
NO
```
