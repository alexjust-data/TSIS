# Auditoría completa — TradeStation Strategy Concepts Club, Issue 11 (noviembre de 2015)

## 0. Alcance del artefacto

Este es el **único archivo Markdown de la revista completa**. Integra:

```text
1. The Measured Moves Strategy
2. Seasonality Bands Strategy
3. ideas secundarias de investigación y backtesting presentes en el número
4. reconstrucción matemática, temporal y de máquina de estados
5. auditoría de los resultados publicados
6. inspección forense de los archivos .ELD y workspaces .tsw
7. contratos de implementación y réplica para TSIS
8. planes de falsificación, ablación y validación postpublicación
```

No se generan archivos separados por estrategia.

### Incidencia documental de la entrega

El PDF cargado por separado con esta entrega es:

```text
SCC Issue 10 Oct 2015(2).pdf
```

y es una copia binariamente idéntica del Issue 10 ya procesado.

El archivo `2015-11.zip`, sin embargo, sí contiene el PDF correcto:

```text
2015-11/SCC Issue 11 Nov 2015.pdf
```

La auditoría se ha realizado sobre ese PDF de noviembre y sobre sus archivos de apoyo. No ha sido necesario solicitar una nueva carga.

### Fuentes examinadas

- PDF correcto de 22 páginas extraído de `2015-11.zip`.
- Archivo de apoyo completo `2015-11.zip`.
- Dos contenedores propietarios correspondientes a las estrategias nuevas:
  - `TSL MEASURED MOVES.ELD`;
  - `TSL SEASONALITY BANDS.ELD`.
- Dos workspaces correspondientes a las estrategias nuevas:
  - `TSL.Measured Moves.tsw`;
  - `TSL Seasonality Bands.tsw`.
- El paquete también vuelve a incluir:
  - `TSL WILLIAMS E-MINI INFLUX.ELD`;
  - `TSL.Williams E-mini Influx.tsw`.

Estos dos últimos archivos son duplicados exactos de los incluidos y auditados en el Issue 10. No constituyen una estrategia nueva del Issue 11 y no reciben un nuevo identificador.

- Todas las tablas y figuras renderizadas del PDF, incluidas:
  - la secuencia visual de benchmarks y señales de Measured Moves;
  - el informe completo de rendimiento de Measured Moves;
  - su análisis de rachas y curva de capital;
  - la construcción de la curva estacional y sus bandas;
  - el ejemplo de señal de Seasonality Bands;
  - su informe completo de rendimiento;
  - la superficie `Top_Band × Low_Band`;
  - el gráfico de beneficio de cada operación que identifica el outlier dominante.

### Regla de evidencia

Se distinguen tres capas:

```text
SOURCE:
lo que afirma, define o muestra la revista

PACKAGE:
lo que confirman el PDF correcto del ZIP,
los workspaces, streams OLE y contenedores .ELD

AUDIT:
inferencia técnica, crítica científica
y propuesta de implementación en TSIS
```

Cuando una decisión no queda resuelta, se registra como ambigüedad. No se completa silenciosamente.

No se ha añadido investigación web externa. Las fórmulas que no aparecen literalmente se presentan como reconstrucciones funcionales que deben reconciliarse mediante réplica.

---

## 0.1 Inventario forense

| Archivo | Tamaño | SHA-256 |
|---|---:|---|
| `2015-11.zip` | 5,691,467 bytes | `2acad3462d8c77dbeca7189dfe7c6d893f0aba757970bd1555de9e8752b9ea2a` |
| `SCC Issue 11 Nov 2015.pdf` dentro del ZIP | 5,627,697 bytes | `7b34e38e30a67b285bf9f85a72da3f7ae814d04fbc6091360cd82573b1b5d9ba` |
| `TSL MEASURED MOVES.ELD` | 21,507 bytes | `7e8176706a20a9bad274183d5f29ac9abf671fc386499a68191c9e27c9befe19` |
| `TSL.Measured Moves.tsw` | 25,600 bytes | `eb57f8aef64e60220bca9a865b0908aded89e9e8211eb2a6062edfcdf5d60c31` |
| `TSL SEASONALITY BANDS.ELD` | 22,381 bytes | `e5fb2c9f042cf27689dfd5cfc222ee2291275a9a3f5f10a8285836091355a521` |
| `TSL Seasonality Bands.tsw` | 49,152 bytes | `547692fcdcdb4cd57d725367d61359cec860cba0ab1c92beb05f701c2b5b4c78` |
| `TSL WILLIAMS E-MINI INFLUX.ELD` repetido | 18,805 bytes | `94ff62ae6fe0fc470f14104010f18104a40dd749b49c4b4cb9487ff60655ee6d` |
| `TSL.Williams E-mini Influx.tsw` repetido | 26,112 bytes | `0fa90f393a55e66c96dbe1e17aabea354f623f42af20ad2a5da981d1f8977117` |
| PDF suelto incorrecto, Issue 10 | 6,092,363 bytes | `58b8f98f4752d638e4e2d393e434236400d754997b62d2ab69420b0e8ab1c17d` |

Los hashes de los dos archivos Williams E-mini Influx coinciden exactamente con los registrados en el Issue 10. Se clasifican como:

```text
PACKAGE_CARRYOVER_DUPLICATE
NOT_A_NEW_STRATEGY
```

Los pequeños streams `Zone.Identifier` son metadatos del sistema de archivos y no forman parte del contenido científico.

---

## 0.2 Limitación de los `.ELD`

Los `.ELD` son contenedores propietarios de TradeStation. Presentan marcadores internos de exportación, pero no exponen el código EasyLanguage como texto legible.

```text
se confirma la existencia de las técnicas;
no puede auditarse el código línea por línea;
no puede certificarse la prioridad exacta entre órdenes;
no pueden resolverse por lectura directa:
    - la secuencia de benchmarks dentro de una barra;
    - la semántica exacta de Lowest/Highest;
    - la inclusión de la observación actual;
    - la alineación de las semanas;
    - la actualización del aprendizaje estacional.
```

---

## 0.3 Workspaces y datos de optimización

Los workspaces son contenedores OLE válidos.

### Measured Moves

Streams principales:

| Stream | Tamaño |
|---|---:|
| `Embedding 1/Contents` | 16,547 bytes |
| `Embedding 1/ChartSetting` | 1,332 bytes |
| `Embedding 1/DrawingObjects` | 595 bytes |
| `Embedding 1/AnalisysTechniques` | 305 bytes |
| `Embedding 1/optdatafile` | **0 bytes** |

### Seasonality Bands

| Stream | Tamaño |
|---|---:|
| `Embedding 1/Contents` | 15,040 bytes |
| `Embedding 1/ChartSetting` | 666 bytes |
| `Embedding 1/DrawingObjects` | 3,022 bytes |
| `Embedding 1/AnalisysTechniques` | 311 bytes |
| `Embedding 1/optdatafile` | **0 bytes** |

En ambos casos:

```text
no se conserva el grid de optimización;
no se conserva el ranking de configuraciones;
no se conserva el número total de pruebas;
no puede calcularse el grado completo de selección in-sample;
no puede comprobarse la afirmación de que el punto publicado
es estable salvo mediante la superficie visual del artículo.
```

---

## 0.4 Evidencia del workspace Measured Moves

El workspace confirma:

```text
Serie:
TSLA 5 min [NASDAQ]
Tesla Motors Inc.

Técnicas:
TSL:Measured Moves ShowMe
TSL:Measured Moves Strategy

Inputs activos del ShowMe:
MeasuredMovePct = 1.25
UpMoveColor = Red
DownMoveColor = Cyan

Inputs activos de la estrategia:
MeasuredMovePct = 1.25
PTPct = 0.5
SLPct = 1.5
```

La tabla de defaults del artículo muestra `1 / 0.5 / 0.5`, pero el test publicado y el workspace utilizan:

```text
1.25 / 0.5 / 1.5
```

El stop del test es, por tanto, tres veces la distancia del profit target.

---

## 0.5 Evidencia del workspace Seasonality Bands

El workspace confirma:

```text
Serie:
@S.C=11INN Weekly [CBOT]
Soybeans Custom Continuous Contract

Técnicas:
TSL:Seasonality Bands Strategy
TSL:Seasonality Bands Indicator

Inputs activos de la estrategia:
Years_Set_Apart = 1
Years_To_Trade = 10
Trail_Stop_Length = 2
Top_Band = 0.14
Low_Band = -0.17

Inputs activos del indicador:
Years_Set_Apart = 1
Years_To_Trade = 10
Top_Band = 0.14
Low_Band = -0.17
```

---

## 0.6 Resultado ejecutivo

| ID | Estrategia | Tipo real | Resultado publicado | Hallazgo crítico | Decisión |
|---|---|---|---|---|---|
| 022 | Measured Moves | Máquina intradía contraria basada en desplazamientos porcentuales desde benchmarks dinámicos | TSLA 5m; 1 año; 1,015 trades; $10,262; PF 1.16; 70.25% ganadoras | expectativa de sólo $10.11 por trade; stop 1.5% frente a target 0.5%; ejecución extremadamente sensible a intrabar y costes | útil como prueba del motor, edge no aceptado |
| 023 | Seasonality Bands | Comparación de YTD actual contra curva estacional expanding y bandas aditivas | Soybeans semanal; 31 trades; $66,779.08; PF 4.07 | una sola operación explica 46.64% del neto y todo el beneficio short; superficie inestable; discrepancia de fechas; posible contaminación por rolls | candidato de investigación, no estrategia validada |

Estado del número:

```text
ISSUE_11_STATUS:
DOCUMENTALLY_CLOSED

NEW_STRATEGIES:
2

DUPLICATE_PACKAGE_STRATEGIES:
1

SCIENTIFICALLY_VALIDATED:
0

LIVE_ELIGIBLE:
0
```

---

# Parte I — Estrategia 022: Measured Moves

## 1) Identificación

- **ID:** `SCC-2015-11-STRAT-022`
- **Artículo:** *The Measured Moves Strategy*
- **Autor:** Stanley Dash, CMT
- **Páginas físicas del PDF:** 4–9
- **Estilo declarado:** mean reversion
- **Mercados declarados:** equities, futures, forex
- **Horizonte:** day trading
- **Activo del test:** Tesla Motors Inc.
- **Símbolo histórico:** `TSLA`
- **Intervalo:** 5 minutos
- **Historia:** un año terminado el 31 de agosto de 2015
- **Tamaño:** 100 acciones
- **Comisión:** $0.01 por acción y lado
- **LIBBT:** 1 minuto
- **Slippage publicado:** no indicado
- **Entradas permitidas:** no en la primera ni en la última barra
- **Liquidación obligatoria:** fin de sesión

### Inputs del test

| Input | Valor |
|---|---:|
| `MeasuredMovePct` | 1.25% |
| `PTPct` | 0.50% |
| `SLPct` | 1.50% |

---

## 2. Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse? | **Sí**, como máquina de estados intradía. |
| ¿Puede replicarse con OHLC de 5 minutos? | **No de forma fiable.** Hay múltiples órdenes y reversals dentro de barra. |
| ¿LIBBT de 1 minuto resuelve todo? | **No.** Dentro de un minuto todavía puede desconocerse la secuencia. |
| ¿La estrategia es mean reversion? | **Sí.** Vende una subida y compra una caída de magnitud predefinida. |
| ¿Tiene una expectativa amplia frente a costes? | **No.** Sólo $10.11 por trade con 100 acciones. |
| ¿Está equilibrada long/short? | En número de trades, sí; en PnL, no. El 72.15% del beneficio es long. |
| ¿La tasa de acierto es suficiente por sí sola? | **No.** La pérdida media duplica la ganancia media. |
| ¿El resultado demuestra edge? | **No.** Un activo, un año, optimización limitada y slippage cero. |
| ¿Merece implementación? | **Sí**, principalmente como test exigente del backtester. |
| ¿Está lista para operar? | **No.** |

Clasificación:

```text
INTRADAY_STATE_MACHINE
MEAN_REVERSION_EVENT
ORDER_ARBITRATION_STRESS_TEST
EXECUTION_FRAGILE
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 3. Qué estrategia es realmente

No es una simple regla:

```text
si TSLA cae 1.25%, comprar
si sube 1.25%, vender
```

El porcentaje se mide desde **benchmarks intradía dinámicos** que cambian a medida que aparecen nuevos máximos, nuevos mínimos o se completa un measured move.

La estructura real es:

```text
apertura del día
→ inicialización de benchmarks
→ extensión del rango
→ actualización de máximo y mínimo de referencia
→ cruce de umbral porcentual
→ entrada contraria
→ reset de benchmarks
→ bracket PT/SL
→ posible señal opuesta y reversal
→ cierre obligatorio de sesión
```

Es, por tanto, una máquina de estados con dos referencias simultáneas:

```text
high benchmark:
origen para medir una caída

low benchmark:
origen para medir una subida
```

---

## 4. Reconstrucción de benchmarks

Sea `m = 0.0125`.

### 4.1 Inicio del día

En la primera barra:

\[
HighBenchmark = Open_{day}
\]

\[
LowBenchmark = Open_{day}
\]

No se permite entrar en esa barra.

### 4.2 Umbral de measured move down

Desde el benchmark alto:

\[
BuyLevel =
HighBenchmark \times (1-m)
\]

Si el mercado cae hasta ese nivel, se completa un measured move down y se genera una entrada long contraria.

### 4.3 Umbral de measured move up

Desde el benchmark bajo:

\[
ShortLevel =
LowBenchmark \times (1+m)
\]

Si el mercado sube hasta ese nivel, se completa un measured move up y se genera una entrada short contraria.

### 4.4 Extensión del benchmark

La reconstrucción funcional más probable es:

```text
si aparece un high mayor antes de completarse la caída:
    HighBenchmark = nuevo high

si aparece un low menor antes de completarse la subida:
    LowBenchmark = nuevo low
```

La revista expresa que el benchmark se resetea cuando:

```text
se supera el benchmark anterior;
o se completa un measured move.
```

En esos casos, el high y el low de la barra pasan a ser los nuevos benchmarks para medir, respectivamente:

```text
una caída futura;
una subida futura.
```

### 4.5 Reset tras una señal

Cuando se completa un measured move:

```text
HighBenchmark = High de la barra del evento
LowBenchmark = Low de la barra del evento
```

Esto permite detectar una nueva oscilación inmediatamente después.

---

## 5. Ambigüedad intrabar del benchmark

Una sola barra puede:

```text
hacer un nuevo high;
hacer un nuevo low;
tocar un nivel de entrada;
tocar un profit target;
tocar un stop;
tocar una señal opuesta.
```

Con OHLC no se conoce si la secuencia fue:

```text
Open → High → Low → Close
```

o:

```text
Open → Low → High → Close
```

La secuencia altera:

```text
qué benchmark estaba activo;
qué orden se llenó primero;
si hubo entrada o reversal;
qué PT/SL quedó activo;
cuántos trades se contabilizan.
```

LIBBT a un minuto sólo sustituye una barra de 5m por cinco barras de 1m. Si dentro de un minuto se tocan múltiples niveles, la ambigüedad permanece.

---

## 6. Entradas

### Long

```text
si el precio completa una caída del 1.25%
desde el high benchmark:
    comprar mediante limit
```

El artículo describe:

```text
buy on a limit order
at a fixed percent below the benchmark
```

El fill ideal al precio límite debe stressarse porque:

```text
puede haber gap por debajo;
puede haber poca liquidez;
el bid/ask importa;
una orden limit no garantiza fill por tocar el low.
```

### Short

```text
si el precio completa una subida del 1.25%
desde el low benchmark:
    vender short mediante limit
```

### Primera y última barra

No se abren posiciones en:

```text
primera barra de la sesión;
última barra de la sesión.
```

Debe definirse la plantilla de sesión que determina cuáles son esas barras.

---

## 7. Exits

Con precio de entrada `E`:

### Long

\[
TargetLong = E(1+0.005)
\]

\[
StopLong = E(1-0.015)
\]

### Short

\[
TargetShort = E(1-0.005)
\]

\[
StopShort = E(1+0.015)
\]

### Fin de sesión

Toda posición abierta se cierra al final de la sesión.

### Reversal

Si antes de PT o SL aparece una señal opuesta:

```text
la posición puede cerrarse y revertirse.
```

El artículo no documenta completamente:

```text
prioridad entre signal reversal y stop;
prioridad entre reversal y target;
si la señal se evalúa antes o después del fill de salida;
cómo se contabiliza el reversal en el mismo minuto.
```

---

## 8. Asimetría reward/risk

La distancia nominal es:

```text
profit target = 0.5%
stop = 1.5%
```

Ratio nominal:

\[
R = 0.5/1.5 = 0.3333
\]

Win rate de equilibrio nominal, sin costes:

\[
p^\* =
\frac{1.5}{1.5+0.5}
=
75\%
\]

La tasa publicada es 70.25%, inferior a ese 75%.

La estrategia sigue siendo ligeramente rentable porque las pérdidas reales medias no alcanzan siempre el stop completo y las salidas/reversals/EOD alteran la distribución.

Con las medias publicadas:

\[
AvgWin = 103.78
\]

\[
AvgLoss = 213.87
\]

\[
p^\* =
\frac{213.87}{103.78+213.87}
\approx 67.33\%
\]

El 70.25% supera el equilibrio real sólo por unos 2.92 puntos porcentuales.

---

## 9. Resultados publicados

### 9.1 Agregado

| Métrica | Resultado |
|---|---:|
| Beneficio neto | $10,262.00 |
| Beneficio bruto | $73,996.00 |
| Pérdida bruta | -$63,734.00 |
| Profit Factor | 1.16 |
| Operaciones | 1,015 |
| Ganadoras | 713 |
| Perdedoras | 298 |
| Even | 4 |
| Percent Profitable | 70.25% |
| Expectativa media | $10.11 |
| Ganancia media | $103.78 |
| Pérdida media | -$213.87 |
| Ratio ganancia/pérdida | 0.49 |
| Mayor ganancia | $268.00 |
| Mayor pérdida | -$434.00 |
| Máx. ganadoras consecutivas | 15 |
| Máx. perdedoras consecutivas | 4 |

### 9.2 Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Beneficio neto | $7,404.00 | $2,858.00 |
| Beneficio bruto | $36,267.00 | $37,729.00 |
| Pérdida bruta | -$28,863.00 | -$34,871.00 |
| Profit Factor | 1.26 | 1.08 |
| Operaciones | 497 | 518 |
| Percent Profitable | 72.23% | 68.34% |
| Expectativa media | $14.90 | $5.52 |
| Ganancia media | $101.02 | $106.58 |
| Pérdida media | -$213.80 | -$213.93 |
| Ratio ganancia/pérdida | 0.47 | 0.50 |
| Mayor ganancia | $268.00 | $202.00 |
| Mayor pérdida | -$434.00 | -$430.00 |

### 9.3 Concentración long

\[
7404 / 10262 \approx 72.15\%
\]

Aunque los trades están repartidos casi 50/50, más del 72% del beneficio procede del lado long.

### 9.4 Frecuencia

El artículo estima unas cuatro operaciones por día.

Con 1,015 trades en aproximadamente un año:

```text
la cifra es coherente con 4 trades por sesión.
```

---

## 10. Fragilidad frente a costes

La expectativa neta es:

\[
\$10.11 \text{ por operación}
\]

Para 100 acciones:

\[
10.11 / 100 = \$0.1011
\]

por acción y round trip.

Es decir, un coste adicional de aproximadamente:

```text
10.11 centavos por acción round trip
5.055 centavos por acción y lado
```

elimina la expectativa media.

La comisión publicada ya consume:

```text
$1 por lado
$2 round trip
```

pero no se modelan:

```text
spread;
slippage;
latencia;
partial fill;
impact;
short locate;
adverse selection;
gap a través del stop.
```

Para una estrategia de TSLA a cinco minutos y más de mil operaciones, esta omisión es crítica.

---

## 11. Curva de capital

La curva asciende de forma general durante gran parte del test, alcanza una zona aproximada de $13,000 y retrocede hacia $10,000 al final.

No debe describirse como lineal o estable.

Observaciones:

```text
existen fases prolongadas de ruido;
el tramo final presenta deterioro;
el PF 1.16 deja poco margen;
la estrategia depende de alta tasa de acierto;
un cambio de microestructura puede volverla negativa.
```

---

## 12. Rachas

El artículo muestra:

```text
una racha ganadora de 15;
75 rachas ganadoras de 4 o más;
5 rachas perdedoras de 4;
ninguna racha perdedora publicada mayor que 4 en el stream agregado.
```

Sin embargo, en los subsets direccionales el informe muestra:

```text
máx. pérdidas long = 7
máx. pérdidas short = 5
```

Esto no es una contradicción: los subsets ignoran operaciones de la otra dirección al construir su serie.

Las rachas históricas no acotan las futuras. Una estrategia con:

```text
stop tres veces mayor que target
```

puede sufrir un deterioro muy rápido si la win rate baja.

---

## 13. Riesgos científicos y de backtesting

### 13.1 Un solo año

No cubre suficientes regímenes de:

```text
volatilidad;
tendencia;
liquidez;
microestructura;
eventos corporativos.
```

### 13.2 Un solo activo

TSLA durante ese periodo puede ser excepcional.

### 13.3 Optimización sobre la muestra

El artículo reconoce optimización limitada.

### 13.4 Slippage cero

Puede eliminar todo el beneficio.

### 13.5 LIBBT no es tick replay

La prioridad exacta continúa sin resolver.

### 13.6 Stop entries y limit fills

El mero toque del precio no garantiza ejecución.

### 13.7 Bar interval selection

Un cambio de 5m a 1m, 3m o 10m cambia:

```text
benchmarks;
número de swings;
trades por barra;
secuencia.
```

### 13.8 Session template

El open diario inicial es parte del algoritmo.

### 13.9 Corporate actions

Tesla cambió ticker posteriormente, pero la réplica histórica debe preservar:

```text
TSLA;
splits;
símbolo mapping;
precios ajustados/raw;
cantidad.
```

### 13.10 Short execution

No se documenta borrow o SSR.

### 13.11 Multiple entries por barra

El propio artículo advierte que un intervalo demasiado grande puede generar múltiples trades por barra y reducir precisión.

### 13.12 Riesgo de martingale implícito

Activar pyramiding permitiría añadir a posiciones en contra de tendencias fuertes. Eso no es una mejora inocua, sino una nueva estrategia de riesgo.

---

## 14. Contrato TSIS

### 14.1 Datos necesarios

```text
TSLA raw 1m o trades
quotes para spread y fill
session calendar
corporate actions
short availability
```

### 14.2 Estado intradía

```text
session_id
bar_index_in_session
is_first_bar
is_last_bar
day_open
high_benchmark
low_benchmark
buy_threshold
short_threshold
position
entry_price
profit_target
stop_level
last_completed_move_direction
orders_active
```

### 14.3 Eventos

```text
NEW_HIGH_BENCHMARK
NEW_LOW_BENCHMARK
DOWN_MOVE_COMPLETED
UP_MOVE_COMPLETED
LONG_LIMIT_FILLED
SHORT_LIMIT_FILLED
PROFIT_TARGET_FILLED
STOP_FILLED
REVERSAL_SIGNAL
END_OF_DAY_EXIT
INTRABAR_AMBIGUITY
```

### 14.4 Estados de indisponibilidad

```text
SESSION_TEMPLATE_UNRESOLVED
MISSING_DAY_OPEN
INSUFFICIENT_INTRABAR_DATA
QUOTE_DATA_UNAVAILABLE
MULTIPLE_LEVELS_SAME_TIMESTAMP
SHORT_NOT_AVAILABLE
CORPORATE_ACTION_UNRESOLVED
```

---

## 15. Pseudocódigo funcional

```python
m = 0.0125
pt = 0.005
sl = 0.015

on_session_start:
    high_benchmark = session_open
    low_benchmark = session_open
    position = 0

for each intraday event in chronological order:

    if new_high > high_benchmark:
        high_benchmark = new_high

    if new_low < low_benchmark:
        low_benchmark = new_low

    buy_level = high_benchmark * (1 - m)
    short_level = low_benchmark * (1 + m)

    if entries_allowed:
        if price <= buy_level:
            execute_or_schedule_long_limit(buy_level)
            high_benchmark = current_bar_high
            low_benchmark = current_bar_low

        elif price >= short_level:
            execute_or_schedule_short_limit(short_level)
            high_benchmark = current_bar_high
            low_benchmark = current_bar_low

    if long:
        target = entry_price * (1 + pt)
        stop = entry_price * (1 - sl)

    if short:
        target = entry_price * (1 - pt)
        stop = entry_price * (1 + sl)

on_session_end:
    flatten()
```

La implementación final debe ser event-driven. Una evaluación única por OHLC no es suficiente.

---

## 16. Plan de réplica y falsificación

### Fase 1 — Checksum histórico

Objetivos:

```text
1,015 trades
497 long
518 short
713 ganadoras
net ≈ $10,262
PF ≈ 1.16
```

### Fase 2 — Reconciliación de benchmark

Comparar:

```text
actualización continua por tick;
actualización por subbarra de 1m;
actualización sólo al cierre de 5m;
reset de ambos benchmarks tras señal;
reset independiente.
```

### Fase 3 — Fill model

```text
touch fill ideal
queue-aware approximation
bid/ask fill
marketable limit
partial fill
gap through stop
```

### Fase 4 — Intrabar adversarial

Si target y stop se tocan en el mismo intervalo:

```text
best case
worst case
path from finer data
ambiguous excluded
```

### Fase 5 — Costes

```text
+1 cent/share RT
+5 cents/share RT
+10 cents/share RT
spread histórico
borrow short
```

### Fase 6 — Cross-sectional

Parámetros congelados sobre:

```text
AAPL
NVDA
AMD
AMZN
META
QQQ
SPY
```

### Fase 7 — Regímenes

Separar:

```text
trending up
trending down
high volatility
low volatility
news days
earnings days
```

### Fase 8 — Postpublicación

Desde noviembre de 2015 en adelante, sin retocar parámetros.

### Fase 9 — Long/short separado

La rama short tiene PF 1.08 y debe validarse independientemente.

---

## 17. Decisión — Measured Moves

```text
IMPLEMENTAR:
sí, como stress test del backtester

ACEPTAR COMO EDGE:
no

VALOR PRINCIPAL:
máquina de estados
+
ordenación intrabar
+
ejecución de múltiples niveles

PRIORIDAD DE INVESTIGACIÓN:
media

PRIORIDAD DE ENGINE VALIDATION:
muy alta

SIGUIENTE GATE:
SCC-022-INTRABAR-BENCHMARK-AND-COST-GATE
```

---

# Parte II — Estrategia 023: Seasonality Bands

## 18) Identificación

- **ID:** `SCC-2015-11-STRAT-023`
- **Artículo:** *Seasonality Bands Strategy*
- **Autor:** Frederic Palmliden, CFA, CMT
- **Páginas físicas:** 10–15
- **Estilo declarado:** trend-following
- **Mercados declarados:** equities, futures, forex
- **Horizonte:** swing trading
- **Activo del test:** soybeans
- **Serie:** `@S.C=11INN`
- **Intervalo:** semanal
- **Capital inicial:** $20,000
- **Tamaño:** un contrato
- **Comisión:** $3.16 por lado
- **Slippage publicado:** no indicado
- **Inputs:** `1 / 10 / 2 / 0.14 / -0.17`

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse? | **Sí**, pero exige una especificación exacta de calendario semanal y aprendizaje expanding. |
| ¿Es una estrategia estacional pura? | **No.** Compara la trayectoria YTD actual contra una trayectoria estacional y opera el sentido de los cruces. |
| ¿La estimación inicial es robusta? | **No.** `Years_Set_Apart=1` permite comenzar con muy poca historia. |
| ¿La serie continua puede contaminar la estacionalidad? | **Sí, de forma severa.** Los rolls de commodities son estacionales. |
| ¿La muestra es suficiente? | **No.** Sólo 31 trades. |
| ¿El PF 4.07 es robusto? | **No.** Una sola operación domina el resultado. |
| ¿La rama short es rentable sin el outlier? | **No.** Pasa aproximadamente a -$5,169.80. |
| ¿Los parámetros son estables? | La superficie publicada dice que no especialmente. |
| ¿Existe inconsistencia documental de fechas? | **Sí.** |
| ¿Está lista para operar? | **No.** |

Clasificación:

```text
SEASONAL_LEARNING_MODEL
EXPANDING_HISTORICAL_REFERENCE
WEEKLY_FUTURES_STRATEGY
ROLL_CONTAMINATION_RISK
OUTLIER_DEPENDENT
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 19. Qué estrategia es realmente

La estrategia crea dos trayectorias en espacio de retornos:

```text
YTDPerf:
rendimiento acumulado real del año actual

CumPerf:
rendimiento acumulado estacional esperado,
construido con promedios semanales históricos
```

Después crea:

```text
TopBand = CumPerf + 14 puntos porcentuales
LowBand = CumPerf - 17 puntos porcentuales
```

La señal no depende simplemente de estar fuera de la banda.

Opera **el sentido del cruce**:

```text
cruce hacia arriba de cualquier banda:
long

cruce hacia abajo de cualquier banda:
short
```

Esto mezcla cuatro tipos de eventos:

```text
1. breakout alcista sobre la banda superior;
2. reentrada alcista desde debajo de la banda inferior;
3. reentrada bajista desde encima de la banda superior;
4. breakdown bajista bajo la banda inferior.
```

No todos representan el mismo mecanismo económico.

---

## 20. Reconstrucción de los retornos semanales

Sea `P_{y,w}` el cierre de la semana `w` del año `y`.

Retorno semanal:

\[
r_{y,w} =
\frac{P_{y,w}}{P_{y,w-1}} - 1
\]

Para la primera semana del año debe definirse la base:

```text
último cierre semanal del año anterior;
primer cierre del año;
barra que cruza el cambio de año.
```

La revista no lo especifica.

---

## 21. Curva estacional histórica

Para cada week bucket `w`, debe calcularse el promedio de los retornos semanales de los años históricos disponibles:

\[
\bar r_{w,t}
=
\frac{1}{N_{w,t}}
\sum_{y \in H_t}
r_{y,w}
\]

donde `H_t` debe contener sólo años disponibles antes del decision timestamp.

La curva acumulada:

\[
CumPerf_{w,t}
=
\prod_{j=1}^{w}
(1+\bar r_{j,t})
-1
\]

La revista la describe como:

> compounded return of the weekly average returns for each year.

---

## 22. Aprendizaje expanding y point-in-time

El artículo afirma:

```text
se reserva un periodo inicial sin señales;
después se añaden nuevos datos con el tiempo;
el sistema continúa aprendiendo.
```

La implementación causal correcta debe ser expanding:

```text
para una señal de la semana w del año y:
usar únicamente años anteriores a y;
no usar el retorno de la semana w del año y
para construir su propia referencia.
```

No debe hacerse:

```text
calcular la media estacional con toda la historia 2002–2015
y después backtestear 2002–2015 contra esa misma media.
```

Eso sería look-ahead.

### Ambigüedad

No puede confirmarse desde el `.ELD`:

```text
si la semana actual se incorpora antes o después de la señal;
si el año actual se incorpora semana a semana;
si sólo se incorpora al terminar el año;
cómo se trata un week bucket sin historial.
```

---

## 23. `Years_Set_Apart` y `Years_To_Trade`

Inputs:

```text
Years_Set_Apart = 1
Years_To_Trade = 10
```

Interpretación declarada:

```text
Years_Set_Apart:
años reservados antes de generar señales

Years_To_Trade:
número de años desde el año actual en los que se permiten señales
```

La relación exacta entre ambos y la historia cargada no queda completamente documentada.

Con sólo un año inicial:

```text
la primera curva estacional puede basarse en una única observación por semana;
no existe una estimación fiable de promedio;
los primeros trades tienen enorme estimation error.
```

La frase del artículo que atribuye el mal inicio a una “initial learning phase” debe interpretarse con cuidado: si el aprendizaje inicial es de un año, el modelo empieza a operar con una referencia extremadamente ruidosa.

---

## 24. Alineación de semanas

Una estrategia estacional semanal debe especificar:

```text
ISO week vs week-of-year TradeStation;
inicio y fin de la semana;
weeks 52 y 53;
semanas incompletas;
feriados;
cambio de año;
barra que contiene sesiones de dos años;
DST si se aplica a la sesión;
semana de Thanksgiving;
cierres festivos de CBOT.
```

Una diferencia de week mapping cambia:

```text
promedios históricos;
curva acumulada;
bandas;
fechas de cruce.
```

El calendario es parte del modelo, no infraestructura auxiliar.

---

## 25. YTD actual

El rendimiento YTD puede reconstruirse como:

\[
YTDPerf_{y,w}
=
\prod_{j=1}^{w}
(1+r_{y,j})
-1
\]

o equivalentemente, si la base está bien definida:

\[
YTDPerf_{y,w}
=
\frac{P_{y,w}}{P_{y,0}}-1
\]

`P_{y,0}` debe ser el cierre de referencia anterior al inicio del año.

---

## 26. Bandas

La revista indica que se **añaden** porcentajes a `CumPerf`.

\[
TopBand_{w,t}
=
CumPerf_{w,t} + 0.14
\]

\[
LowBand_{w,t}
=
CumPerf_{w,t} - 0.17
\]

No parece utilizar:

\[
(1+CumPerf)(1+Band)-1
\]

sino una distancia aditiva en puntos de retorno.

La anchura total es:

\[
0.14 - (-0.17) = 0.31
\]

o 31 puntos porcentuales.

---

## 27. Señales

### Long

```text
si YTDPerf cruza hacia arriba:
    - TopBand
    o
    - LowBand
entonces comprar en la apertura de la semana siguiente.
```

Formalmente:

\[
crossUp(YTDPerf, TopBand)
\lor
crossUp(YTDPerf, LowBand)
\]

### Short

\[
crossDown(YTDPerf, TopBand)
\lor
crossDown(YTDPerf, LowBand)
\]

### Posición previa

La revista no especifica completamente:

```text
si una señal opuesta revierte inmediatamente;
si sólo entra estando flat;
qué prioridad tiene una señal frente a una salida de precio;
si se ignoran cruces repetidos durante una posición.
```

El informe de trades debe usarse como checksum.

---

## 28. Salidas y problema de auto-inclusión

Long:

```text
salir en la apertura siguiente
si Close cae por debajo del lowest low de las últimas 2 barras.
```

Si las dos barras incluyen la actual:

\[
Close_t < Lowest(Low,2)_t
\]

es imposible porque:

\[
Low_t \le Close_t
\]

La reconstrucción probable es:

\[
Close_t <
\min(Low_{t-1}, Low_{t-2})
\]

Short:

\[
Close_t >
\max(High_{t-1}, High_{t-2})
\]

Debe verificarse contra la estrategia original.

---

## 29. El indicador omite la semana actual

El artículo explica que no dibuja un valor para la última barra aún incompleta.

Esto es una buena práctica visual:

```text
la semana actual no debe tratarse como cerrada;
la señal sólo se conoce al cierre semanal;
la entrada ocurre en la apertura siguiente.
```

TSIS debe distinguir:

```text
current_partial_week
completed_week
decision_timestamp
```

---

## 30. Continuous futures y contaminación estacional

La estrategia usa:

```text
@S.C=11INN
sin back adjustment
roll cuando existe un día consecutivo de mayor open interest
```

Éste es uno de los riesgos más importantes del número.

En commodities agrícolas:

```text
los contratos vencen en meses predefinidos;
los rolls ocurren en ventanas estacionales;
la curva de futuros presenta contango/backwardation;
los gaps entre contratos pueden repetirse por época del año.
```

Una serie continua sin back adjustment puede convertir el roll en un retorno semanal artificial.

Como la estrategia busca precisamente patrones por semana del año:

> puede aprender la mecánica del continuo y del calendario de roll, no un patrón explotable del precio del activo.

Debe separarse:

```text
spot/nearby price seasonality;
roll yield;
contract switch gap;
PnL de una posición física;
serie analítica.
```

---

## 31. Discrepancia documental de historia

La tabla del artículo dice:

```text
History = 11 years ending 9/30/15
```

Pero el informe mostrado en la figura 3 indica:

```text
@S.C=11INN Weekly
9/27/2002–9/25/2015
```

y el campo `Trading Period` muestra:

```text
12 Yrs, 13 Days
```

La curva de capital también usa un rango que comienza en 2002.

Estas tres referencias no son equivalentes.

Posibles explicaciones:

```text
historia cargada adicional para aprendizaje;
MaxBarsBack;
periodo sin señales;
redondeo editorial;
error en la tabla;
diferencia entre chart span y trading span.
```

No puede cerrarse sin código o reporte exportado.

Estado:

```text
SOURCE_DATE_RANGE_CONFLICT
```

---

## 32. Resultados publicados

### 32.1 Agregado

| Métrica | Resultado |
|---|---:|
| Beneficio neto | $66,779.08 |
| Beneficio bruto | $88,530.20 |
| Pérdida bruta | -$21,751.12 |
| Profit Factor | 4.07 |
| Operaciones | 31 |
| Ganadoras | 15 |
| Perdedoras | 16 |
| Percent Profitable | 48.39% |
| Expectativa media | $2,154.16 |
| Ganancia media | $5,902.01 |
| Pérdida media | -$1,359.44 |
| Ratio ganancia/pérdida | 4.34 |
| Mayor ganancia | $31,143.68 |
| Mayor pérdida | -$5,981.32 |
| Máx. ganadoras consecutivas | 3 |
| Máx. perdedoras consecutivas | 3 |
| Barras medias ganadoras | 11.47 |
| Barras medias perdedoras | 4.63 |
| Return on Initial Capital | 333.90% |
| Annual Rate of Return | 12.19% |
| RINA Index | 72.53 |
| Percent of Time in Market | 34.37% |
| Drawdown semanal aproximado | 40% |

### 32.2 Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Beneficio neto | $40,805.20 | $25,973.88 |
| Beneficio bruto | $50,236.80 | $38,293.40 |
| Pérdida bruta | -$9,431.60 | -$12,319.52 |
| Profit Factor | 5.33 | 3.11 |
| Operaciones | 15 | 16 |
| Ganadoras | 10 | 5 |
| Perdedoras | 5 | 11 |
| Percent Profitable | 66.67% | 31.25% |
| Expectativa media | $2,720.35 | $1,623.37 |
| Ganancia media | $5,023.68 | $7,658.68 |
| Pérdida media | -$1,886.32 | -$1,119.96 |
| Ratio ganancia/pérdida | 2.66 | 6.84 |
| Mayor ganancia | $12,293.68 | $31,143.68 |
| Mayor pérdida | -$5,981.32 | -$2,856.32 |
| Barras medias ganadoras | 12.00 | 10.40 |
| Barras medias perdedoras | 4.40 | 4.73 |

---

## 33. Dependencia del outlier

La mayor operación gana:

\[
\$31,143.68
\]

Proporción del beneficio bruto:

\[
31,143.68 / 88,530.20
\approx 35.18\%
\]

Proporción del beneficio neto:

\[
31,143.68 / 66,779.08
\approx 46.64\%
\]

Es decir:

```text
una sola operación representa:
≈ 35% del gross profit
≈ 47% del net profit
```

### 33.1 Resultado total sin el outlier

\[
66,779.08 - 31,143.68
=
35,635.40
\]

El agregado seguiría siendo positivo, pero mucho menos extraordinario.

Profit Factor aproximado sin esa ganancia:

\[
(88,530.20 - 31,143.68) / 21,751.12
\approx 2.64
\]

### 33.2 Rama short sin el outlier

El outlier pertenece al lado short.

\[
25,973.88 - 31,143.68
=
-5,169.80
\]

Por tanto:

> Sin una sola operación, toda la rama short pasa de +$25,973.88 a aproximadamente -$5,169.80.

Éste es el hallazgo cuantitativo más importante del Issue 11.

---

## 34. Interpretación de la rama long y short

La rama long:

```text
10 ganadoras / 5 perdedoras
PF 5.33
net $40,805.20
```

La rama short:

```text
5 ganadoras / 11 perdedoras
PF 3.11 sólo por payoff extremo
net negativo al retirar el mayor trade.
```

No existe evidencia suficiente para mantener la rama short como un módulo robusto independiente.

---

## 35. Curva de capital

La curva:

```text
empieza con pérdidas;
salta en pocos bloques;
alcanza aproximadamente $70,000;
entra en mesetas prolongadas;
sufre drawdowns cercanos al 40%.
```

No es una curva uniforme.

El artículo describe el primer tramo débil como posible “learning phase”. Científicamente deben separarse:

```text
periodo sin señales usado para aprender;
primeros trades con estimador pobre;
pérdidas reales del sistema.
```

Una fase de aprendizaje correctamente aislada no debería producir PnL.

---

## 36. Sensibilidad

Superficie:

```text
Top_Band × Low_Band
```

Hallazgos de la revista:

```text
dos ridges;
picos alrededor de Top_Band = 0.07 y Low_Band = -0.17;
configuración publicada = 0.14 / -0.17;
grandes caídas con cambios pequeños;
superficie poco atractiva.
```

Elegir un punto apartado del pico es mejor que escoger el máximo puntual, pero no resuelve:

```text
inestabilidad;
muestra de 31 trades;
selección sobre la misma historia;
múltiples mercados potencialmente revisados;
ausencia de OOS.
```

---

## 37. ¿Dónde podría estar el edge?

Hipótesis económica:

> Cuando la trayectoria anual actual de soybeans se separa o vuelve a cruzar una trayectoria estacional histórica, el sentido del cruce contiene información sobre el movimiento posterior.

Mecanismos posibles:

```text
ciclo de siembra y cosecha;
inventarios;
clima;
demanda exportadora;
roll yield;
positioning;
persistencia estacional;
mean reversion hacia el patrón medio.
```

La regla mezcla:

```text
breakout;
reentrada;
trend following;
mean reversion.
```

Por ello, no identifica un único mecanismo causal.

---

## 38. Riesgos científicos

### 38.1 Sólo 31 operaciones

No permite estimar bien:

```text
win rate;
colas;
drawdown;
estabilidad;
seasonality por década.
```

### 38.2 Un único commodity

No hay panel de commodities.

### 38.3 Aprendizaje inicial de un año

Demasiado escaso para estimar una media estacional.

### 38.4 Expanding logic no certificada

Debe demostrarse que no usa datos futuros.

### 38.5 Week alignment

Puede alterar toda la curva.

### 38.6 Rolls estacionales

Pueden fabricar la señal.

### 38.7 Serie no back-adjusted

Los saltos de contrato contaminan los retornos.

### 38.8 Sin slippage

Una orden semanal al open puede gapear.

### 38.9 Physical contract mapping

El continuo no es operable.

### 38.10 Outlier dominante

La rama short no sobrevive a su eliminación.

### 38.11 Superficie inestable

Los parámetros no generalizan localmente con claridad.

### 38.12 Discrepancia de fechas

Impide definir el periodo exacto sin reconciliación.

### 38.13 Multiple testing

La estrategia podría haberse explorado en muchos mercados, bandas y reglas antes de escoger soybeans.

### 38.14 `Top_Band` y `Low_Band` asimétricos

La asimetría puede ser económica o seleccionada; debe testarse.

### 38.15 Exit de dos barras

Muy corta frente al horizonte estacional y posiblemente seleccionada.

---

## 39. Contrato TSIS

### 39.1 Datos

```text
soybean physical futures contracts
weekly canonical bars
open interest
roll calendar
exchange calendar
contract specifications
```

### 39.2 Series separadas

```text
seasonal_signal_series
physical_execution_series
roll_return_series
spot_proxy_if_available
```

### 39.3 Estado

```text
calendar_year
week_bucket
week_start
week_end
is_complete_week
weekly_return
ytd_return
historical_years_available
seasonal_week_mean_return
seasonal_cumulative_return
top_band
low_band
cross_top_up
cross_top_down
cross_low_up
cross_low_down
position
prior_two_week_low
prior_two_week_high
active_contract
roll_state
```

### 39.4 Estados de indisponibilidad

```text
WEEK_MAPPING_UNRESOLVED
INSUFFICIENT_SEASONAL_YEARS
CURRENT_YEAR_LEAKAGE_RISK
ROLL_MAPPING_UNRESOLVED
CONTRACT_GAP_CONTAMINATION
DATE_RANGE_CONFLICT
MISSING_NEXT_WEEK_OPEN
EXIT_SELF_INCLUSION_UNRESOLVED
```

---

## 40. Pseudocódigo causal

```python
for each completed week t:

    y = calendar_year(t)
    w = canonical_week_bucket(t)

    # Only history known before current year
    historical_years = years strictly earlier than y

    if len(historical_years) < minimum_learning_years:
        mark_unavailable()

    mean_return_by_week = expanding_weekly_mean(
        returns=weekly_returns,
        years=historical_years,
        week_bucket=w
    )

    seasonal_curve = compound_from_week_1_to_w(
        mean_return_by_week
    )

    ytd = compound_actual_returns_for_year(y, through_week=w)

    top = seasonal_curve + 0.14
    low = seasonal_curve - 0.17

    if crosses_up(ytd, top) or crosses_up(ytd, low):
        schedule_long(next_week_open)

    elif crosses_down(ytd, top) or crosses_down(ytd, low):
        schedule_short(next_week_open)

    if long and close[t] < min(low[t-1], low[t-2]):
        schedule_exit(next_week_open)

    if short and close[t] > max(high[t-1], high[t-2]):
        schedule_exit(next_week_open)
```

`minimum_learning_years=1` reproduce la intención publicada, pero una investigación científica debería comparar valores mayores sin seleccionar sobre el test final.

---

## 41. Plan de réplica y falsificación

### Fase 1 — Reconciliación de fechas

Determinar por qué aparecen:

```text
11 años;
9/27/2002–9/25/2015;
12 años y 13 días.
```

### Fase 2 — Reconciliación de aprendizaje

Comparar:

```text
expanding prior-year only;
full-sample hindsight;
rolling N years;
actual-year incorporation inmediata;
actual-year incorporation al finalizar año.
```

### Fase 3 — Week mapping

```text
TradeStation week;
ISO week;
exchange week;
week ending Friday;
week ending por sesión.
```

### Fase 4 — Checksums

```text
31 trades
15 long
16 short
net ≈ $66,779.08
largest win ≈ $31,143.68
```

### Fase 5 — Roll decomposition

Comparar:

```text
unadjusted continuous;
back-adjusted;
ratio-adjusted;
physical held-contract returns;
roll-neutral signal;
roll yield separado.
```

### Fase 6 — Outlier stress

```text
remove largest trade
winsorize
bootstrap by year
block bootstrap
leave-one-trade-out
```

### Fase 7 — Long-only y short-only

La rama short debe superar OOS sin el trade extremo.

### Fase 8 — Learning years

Preregistrar:

```text
1
3
5
10
```

No escoger el mejor sobre la misma muestra.

### Fase 9 — Panel de commodities

```text
soybeans
corn
wheat
soybean meal
soybean oil
live cattle
crude oil
natural gas
gold
```

### Fase 10 — Baselines

| Baseline | Pregunta |
|---|---|
| seasonal mean sign | ¿las bandas añaden valor? |
| buy-and-hold | ¿la señal supera beta/commodity drift? |
| calendar-only | ¿YTD actual es necesario? |
| random bands | ¿los thresholds contienen información? |
| fixed yearly curve | ¿expanding learning mejora? |
| long-only | ¿short aporta algo? |

### Fase 11 — Postpublicación

Desde noviembre de 2015, inputs congelados:

```text
1 / 10 / 2 / 0.14 / -0.17
```

### Fase 12 — Costes físicos

```text
commissions
spread
roll slippage
limit up/down
first notice
delivery avoidance
open gaps
```

---

## 42. Decisión — Seasonality Bands

```text
IMPLEMENTAR:
sí, como objeto de investigación estacional

ACEPTAR COMO EDGE:
no

VALOR PRINCIPAL:
referencia histórica expanding
+
calendario semanal
+
separación señal/roll

PRIORIDAD:
alta para investigación causal

RIESGO PRINCIPAL:
roll contamination y outlier dependence

SIGUIENTE GATE:
SCC-023-SEASONAL-LEARNING-ROLL-AND-OUTLIER-GATE
```

---

# Parte III — Ideas transversales del Issue 11

## 43. Un benchmark dinámico es estado

Measured Moves demuestra que no basta con calcular una feature por barra.

Se necesita conservar:

```text
high benchmark;
low benchmark;
evento que causó el reset;
orden activa;
posición;
niveles de salida.
```

---

## 44. El gráfico retrospectivo no es la señal

Las líneas del ShowMe aparecen después de completarse el measured move.

No deben usarse como input porque:

```text
son una anotación retrospectiva;
su endpoint final no existe antes del evento.
```

---

## 45. Alta win rate no compensa cualquier payoff

Measured Moves:

```text
70.25% ganadoras
ratio win/loss 0.49
PF 1.16
```

Una reducción pequeña de la tasa de acierto destruye el edge.

---

## 46. Una estrategia puede tener muchos trades y poca evidencia

1,015 operaciones no solucionan:

```text
un único activo;
un único año;
autocorrelación intradía;
dependencia de régimen;
selección de parámetros;
fills idealizados.
```

El número de trades no equivale al número de observaciones independientes.

---

## 47. El calendario es parte del estado de mercado

Seasonality Bands necesita:

```text
año;
semana;
semana completa;
feriados;
week 53;
roll;
años históricos disponibles.
```

---

## 48. Un modelo expanding debe guardar la versión de su referencia

Cada señal necesita trazabilidad de:

```text
años incluidos;
retornos semanales usados;
curva estacional calculada;
bandas;
timestamp.
```

No basta con guardar el valor final.

---

## 49. Los continuos pueden fabricar estacionalidad

En una estrategia de calendario sobre futuros:

```text
el roll no es sólo un problema de ejecución;
puede contaminar directamente la feature.
```

---

## 50. Un outlier puede sostener una rama completa

Seasonality Bands short:

```text
net publicado = +$25,973.88
sin mayor trade = -$5,169.80
```

La atribución por dirección debe incluir leave-one-out.

---

## 51. Elegir una meseta no elimina el multiple testing

La selección de `0.14/-0.17` lejos del máximo es metodológicamente mejor que escoger el pico, pero sigue siendo in-sample.

---

## 52. La historia cargada y el periodo efectivo deben coincidir

La discrepancia 11 años / 12 años / 2002–2015 debe bloquear la reproducción exacta.

---

## 53. Ideas secundarias de backtesting del número

1. Relacionar intervalo y frecuencia de señales.
2. Reducir intervalo cuando existen múltiples trades por barra.
3. Separar parámetros long y short.
4. Evaluar breakeven stops como nueva hipótesis.
5. No habilitar pyramiding sin rediseñar riesgo.
6. Usar expanding learning point-in-time.
7. Versionar week mapping.
8. Descomponer roll y seasonal return.
9. Aplicar leave-one-out a estrategias de pocos trades.
10. No aceptar PF elevado sin inspeccionar concentración.
11. Registrar el periodo real de aprendizaje y trading.
12. Tratar plots retrospectivos como visualización, no evidencia causal.

---

# Parte IV — Registro para TSIS

## 54. Eventos candidatos

### Measured Moves

```text
event_type:
intraday_percent_move_down_completed

subject_scope:
single_security_intraday

attributes:
benchmark_high
move_pct
time_since_reset
number_of_resets_today
position_before
```

```text
event_type:
intraday_percent_move_up_completed
```

```text
event_type:
benchmark_extended
```

### Seasonality Bands

```text
event_type:
ytd_crosses_seasonal_top_up
```

```text
event_type:
ytd_crosses_seasonal_top_down
```

```text
event_type:
ytd_crosses_seasonal_low_up
```

```text
event_type:
ytd_crosses_seasonal_low_down
```

```text
event_type:
seasonal_reference_updated
```

---

## 55. Priorización

| Prioridad | Candidato | Motivo |
|---:|---|---|
| 1 | Measured Moves intrabar replay | stress test extremo para órdenes y benchmarks |
| 2 | Seasonality roll decomposition | puede invalidar la hipótesis completa |
| 3 | Seasonality postpublication long-only | rama más defendible |
| 4 | Measured Moves cost stress | expectativa muy pequeña |
| 5 | Seasonality week/calendar reconciliation | requisito previo para cualquier réplica |

---

## 56. Gates

### SCC-022-A — Benchmark State Contract

Debe fijar exactamente:

```text
actualización de high/low;
reset tras move;
reset tras reversal;
bar-first/bar-last;
orden de evaluación.
```

### SCC-022-B — Intrabar Arbitration

Debe resolver:

```text
entry;
target;
stop;
reversal;
EOD;
same-minute conflicts.
```

### SCC-022-C — Cost Survival

Debe superar un modelo realista de quotes y fills.

### SCC-022-D — Cross-sectional OOS

Parámetros congelados.

### SCC-023-A — Date Range Reconciliation

Debe cerrar la discrepancia de historia.

### SCC-023-B — Point-in-Time Learning

Debe demostrar que no se usa el año actual ni el futuro.

### SCC-023-C — Week Mapping

Debe congelar calendario.

### SCC-023-D — Roll Contamination

Debe separar return de contrato y roll.

### SCC-023-E — Outlier Dependence

Debe publicar leave-one-out y bootstrap.

### SCC-023-F — Postpublication OOS

Inputs congelados.

---

# Conclusión

El Issue 11 contiene dos estrategias nuevas y un duplicado de archivos del Issue 10.

## Measured Moves

La estrategia es una máquina de estados intradía contraria:

```text
benchmarks dinámicos
→ move de 1.25%
→ entrada limit contraria
→ target 0.5%
→ stop 1.5%
→ posible reversal
→ cierre EOD
```

El resultado publicado:

```text
1,015 trades
70.25% ganadoras
PF 1.16
$10.11 por trade
```

es demasiado estrecho para aceptar edge sin quotes, slippage y replay intrabar.

Su mayor valor inmediato es:

```text
validar el motor de eventos y órdenes de TSIS.
```

## Seasonality Bands

La estrategia:

```text
aprende una curva semanal expanding
→ calcula YTD actual
→ añade bandas +14% / -17%
→ opera el sentido de cada cruce
→ sale por ruptura de 2 semanas
```

El PF 4.07 parece atractivo, pero:

```text
sólo hay 31 trades;
una operación aporta 46.64% del neto;
sin esa operación la rama short es negativa;
la superficie es inestable;
las fechas publicadas no concuerdan;
los rolls pueden fabricar estacionalidad.
```

No debe tratarse como una estrategia validada.

## Estado final

```text
ISSUE_11_STATUS:
DOCUMENTALLY_CLOSED

CORRECT_PDF_SOURCE:
FOUND_INSIDE_ZIP

WRONG_STANDALONE_PDF:
DUPLICATE_ISSUE_10

NEW_STRATEGIES_EXTRACTED:
2

DUPLICATE_STRATEGIES:
1

SCIENTIFICALLY_VALIDATED:
0

LIVE_ELIGIBLE:
0
```

Siguientes gates recomendados:

```text
1. SCC-022-INTRABAR-BENCHMARK-AND-COST-GATE
2. SCC-023-SEASONAL-LEARNING-ROLL-AND-OUTLIER-GATE
```
