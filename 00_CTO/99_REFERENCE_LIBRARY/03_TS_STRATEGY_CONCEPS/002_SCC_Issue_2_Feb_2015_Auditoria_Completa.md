# Auditoría completa — TradeStation Strategy Concepts Club, Issue 2 (febrero de 2015)

## 0. Alcance del artefacto

Este es el **único Markdown de la revista completa**. Integra:

```text
1. The Auto-Trendline Strategy
2. The VIX Pivot Strategy
3. ideas secundarias de backtesting presentes en el issue
4. auditoría temporal, matemática y metodológica
5. contratos de réplica para TSIS
6. planes de falsificación y validación postpublicación
```

No se generan archivos separados por estrategia.

### Fuentes examinadas

- PDF completo de 14 páginas: `SCC Issue 2 Feb 2015.pdf`
- ZIP original de apoyo: `2015-02.zip`
- Workspace y `.ELD` de ambas estrategias
- Imágenes renderizadas de todas las páginas, incluidas las tablas de resultados, curvas de capital y tabla de optimización
- El Markdown del Issue 1, utilizado como **modelo de profundidad y organización**, no como autoridad factual sobre este número

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
| 003 | Auto-Trendline | Ruptura de trendlines basada en swings; AAPL daily | PF 1.78, 127 trades, 10 años cargados | pivotes confirmados con barras futuras, ángulo no invariante, inputs optimizados, 97.4% del beneficio en longs | Replicar con auditoría anti-repainting y normalización de escala |
| 004 | VIX Pivot | Señal contrarian de volatilidad; long-only en ES | 12/12 ganadoras, $34,667.50, 2012–2015 | muestra diminuta, selección tras optimización, sin stop, $7,400 de trade drawdown, continuo sintético | Falsificación post-2015 antes de cualquier mejora |

## 0.1 Veredicto global

El Issue 2 es más valioso como **laboratorio de errores sutiles de backtesting** que como demostración de edge.

La estrategia Auto-Trendline obliga a resolver correctamente:

```text
pivotes que sólo se conocen tras varias barras futuras
versionado de líneas dinámicas
cruces contra una línea proyectada
ángulos dependientes de unidades
stops diarios intrabar
corporate actions
```

La estrategia VIX Pivot obliga a resolver:

```text
señal en un índice no operable
operación en otro instrumento
alineación entre sesiones VIX y ES
continuous futures frente a contratos físicos
thresholds de régimen
riesgo de selección con 12 operaciones
```

El resultado más llamativo del issue —12 operaciones ganadoras de 12— es precisamente el que debe tratarse con mayor desconfianza, porque fue seleccionado dentro de una superficie de optimización y no existe una muestra independiente publicada.

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

# Parte I — Estrategia 003: The Auto-Trendline Strategy

## 1) Identificación y rendimiento

- **ID de estrategia:** `SCC-2015-02-STRAT-003`
- **Revista:** *Strategy Concepts Club* — TradeStation Labs
- **Issue:** 2
- **Fecha declarada del issue:** febrero de 2015
- **Metadata de creación del PDF:** 11 de febrero de 2015
- **Artículo:** *The Auto-Trendline Strategy*
- **Autor:** **Frederic Palmliden, CMT**
- **Páginas físicas del PDF:** 4–7
- **Páginas impresas del artículo:** 2–5
- **Estilo declarado:** Trend following
- **Mercados declarados:** Equities, futures, forex
- **Horizonte declarado:** Swing trading
- **Frecuencia del ejemplo:** Daily
- **Activo del backtest:** Apple Inc. (`AAPL`)
- **Archivos auxiliares del ZIP:** estrategia `.ELD` y workspace `.tsw`

### Inputs publicados

| Input | Default | Función declarada |
|---|---:|---|
| `SHStren` | 3 | Barras anteriores y posteriores requeridas para un swing high |
| `SLStren` | 6 | Barras anteriores y posteriores requeridas para un swing low |
| `LXTrailbar` | 2 | Barras utilizadas para el lowest low del stop long |
| `SXTrailbar` | 2 | Barras utilizadas para el highest high del stop short |
| `DownTrendAngle` | -10 | Ángulo máximo de la downtrend line para permitir compra |
| `UpTrendAngle` | 20 | Ángulo mínimo de la uptrend line para permitir short |

El artículo declara explícitamente que los valores por defecto fueron encontrados mediante **strategy testing optimization** y que otros activos probablemente exigirían ajustes.

### Resultados destacados publicados

- **Beneficio neto:** $5,451.52
- **Profit Factor:** 1.78
- **Operaciones:** 127
- **Percent Profitable:** 35.43%
- **RINA Index:** 311.02
- **Retorno sobre capital inicial:** 77.88%
- **Annual Rate of Return mostrado:** 5.97%
- **Percent of Time in the Market:** 18.97%
- **Periodo de trading efectivo:** 9 años, 7 meses y 19 días
- **Comentario visual:** curva ascendente a largo plazo con drawdown cercano al 10% al inicio del test

### Evidencia adicional del ZIP

El workspace `TSL Auto-Trendline.tsw` contiene metadatos binarios parcialmente legibles que confirman:

```text
chart principal:
AAPL Daily [NASDAQ] Apple Inc

analysis technique:
TSL: Auto-Trendline

inputs registrados:
SHStren
SLStren
LXTrailbar
SXTrailbar
DownTrendAngle
UpTrendAngle
```

El `.ELD` es un contenedor binario de TradeStation. En este entorno no equivale a una exportación legible del código EasyLanguage. Por ello, el paquete confirma identidad, instrumento y nombres de inputs, pero no permite auditar directamente cada rama del algoritmo.

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí**, pero sólo si se gobierna la confirmación temporal de los swings. |
| ¿Puede replicarse aproximadamente con el PDF? | **Sí.** |
| ¿La réplica exacta exige importar el `.ELD` o exportar el código? | **Sí**, para resolver selección de pivotes, igualdad, actualización de líneas y semántica de órdenes. |
| ¿El artículo demuestra científicamente un edge? | **No.** Es un único activo con seis inputs optimizados in-sample. |
| ¿La tesis económica es plausible? | **Sí**, como familia de breakout/reversal técnico. |
| ¿El uso de grados es portable? | **No.** El ángulo depende de dólares por barra y de la escala del precio. |
| ¿Existe riesgo de look-ahead? | **Sí, crítico**, si los pivotes se usan antes de quedar confirmados. |
| ¿Está preparada para real? | **No.** |

Clasificación TSIS:

```text
SOURCE_REPRODUCTION_CANDIDATE
PIVOT_CONFIRMATION_CRITICAL
SCALE_NON_INVARIANT
CORPORATE_ACTION_SENSITIVE
POSTPUBLICATION_OOS_AVAILABLE
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 2. Qué estrategia es realmente

No es una estrategia que dibuje una línea discrecional “a ojo”. Automatiza cuatro operaciones distintas:

```text
1. detectar swing highs y swing lows confirmados
2. seleccionar dos puntos compatibles con una línea descendente o ascendente
3. proyectar la línea hasta la barra actual
4. operar cuando el cierre cruza la línea y su ángulo supera un filtro
```

La lógica long y short es asimétrica:

```text
LONG:
romper al alza una downtrend line suficientemente descendente

SHORT:
romper a la baja una uptrend line suficientemente ascendente
```

Esto se parece más a una estrategia de **transición de tendencia por ruptura de estructura** que a una estrategia de continuación pura.

La posición se abre en la apertura siguiente y no tiene profit target. Sale mediante un stop construido con los últimos mínimos o máximos.

El artículo indica que la estrategia conserva únicamente la uptrend line y la downtrend line vigentes y borra las obsoletas del gráfico. Para backtesting científico eso no debe significar eliminar su historia: TSIS necesita conservar cada versión de línea y el intervalo durante el que fue observable.

---

## 3. Reconstrucción matemática

### 3.1 Swing high

Sea `s_H = SHStren` y sea `p` una barra candidata.

La definición textual y la semántica estándar de `SwingHigh` en EasyLanguage son compatibles con:

$$
H_p \geq \max(H_{p-s_H},\ldots,H_{p-1})
$$

$$
H_p > \max(H_{p+1},\ldots,H_{p+s_H})
$$

Con el default:

```text
s_H = 3
```

El máximo de la barra candidata debe ser al menos tan alto como los tres máximos anteriores y estrictamente superior a los tres posteriores. TradeStation documenta esta asimetría de igualdad para sus funciones estándar de swings. ([Ayuda TradeStation][TS-SWINGHIGH])

### 3.2 Swing low

Sea `s_L = SLStren`.

$$
L_p \leq \min(L_{p-s_L},\ldots,L_{p-1})
$$

$$
L_p < \min(L_{p+1},\ldots,L_{p+s_L})
$$

Con el default:

```text
s_L = 6
```

TradeStation utiliza igualmente barras a ambos lados del pivot. ([Ayuda TradeStation][TS-SWINGLOW])

### 3.3 Momento de confirmación

El pivot no es observable en `p`.

```text
swing high p:
confirmed_at = p + SHStren

swing low p:
confirmed_at = p + SLStren
```

Por tanto:

```text
un swing high tarda 3 sesiones en confirmarse
un swing low tarda 6 sesiones en confirmarse
```

Ésta es una asimetría temporal real. La rama short recibe información estructural con una latencia distinta de la rama long.

> Dibujar posteriormente una línea desde el pivot no autoriza a fingir que la línea era conocida en la fecha del pivot.

### 3.4 Selección de puntos para la downtrend line

El artículo dice que conecta:

```text
swing high más reciente
con
siguiente swing high anterior que sea más alto
```

Sean:

```text
p_1 = swing high más reciente
p_0 = swing high anterior seleccionado
p_0 < p_1
H_p0 > H_p1
```

La pendiente es:

$$
m_D=\frac{H_{p_1}-H_{p_0}}{p_1-p_0}<0
$$

La línea proyectada en la barra `t` es:

$$
D_t=H_{p_0}+m_D(t-p_0)
$$

### 3.5 Selección de puntos para la uptrend line

El artículo conecta:

```text
swing low más reciente
con
siguiente swing low anterior que sea más bajo
```

Sean:

```text
q_1 = swing low más reciente
q_0 = swing low anterior seleccionado
q_0 < q_1
L_q0 < L_q1
```

$$
m_U=\frac{L_{q_1}-L_{q_0}}{q_1-q_0}>0
$$

$$
U_t=L_{q_0}+m_U(t-q_0)
$$

### 3.6 “Últimos 10 swings”

La estrategia mantiene los diez swings más recientes de cada clase.

El PDF no resuelve:

```text
si busca el primer anchor compatible dentro de esos diez
si busca el más lejano
si usa una función propia de TradeStation
cómo trata pivots con mismo precio
qué ocurre si no encuentra un segundo punto compatible
```

Estas decisiones pueden cambiar sustancialmente la línea y el número de operaciones. Deben salir del código exportado o reconciliarse trade a trade.

### 3.7 Ángulo

TradeStation documenta `TLAngle` como:

$$
\theta=\arctan\left(\frac{\Delta Price}{\Delta Bars}\right)
$$

El cálculo utiliza precios y números de barra, no retornos normalizados. ([Ayuda TradeStation][TS-TLANGLE])

Para las líneas anteriores:

$$
\theta_D=\arctan(m_D)
$$

$$
\theta_U=\arctan(m_U)
$$

Reglas publicadas:

```text
long permitido si theta_D < -10°
short permitido si theta_U > +20°
```

### 3.8 Problema de unidades

El argumento del arcotangente es:

```text
dólares por barra
```

No es:

```text
porcentaje por barra
log-return por barra
ATR por barra
volatilidad normalizada
```

Por ello, dos tendencias económicamente idénticas pueden producir ángulos distintos:

```text
Activo a $10 que sube $0.20 por día:
+2% por día

Activo a $100 que sube $0.20 por día:
+0.2% por día

TLSlope absoluto en ambos:
$0.20 por barra
```

El filtro angular no distingue esos casos.

También sucede lo contrario: una pendiente de `$1 por barra` no representa el mismo fenómeno a $20 que a $200.

### 3.9 Corporate actions

El backtest cubre AAPL desde finales de 2004 hasta finales de 2014. Apple confirma splits de 2:1 el 28 de febrero de 2005 y 7:1 el 9 de junio de 2014. ([Apple Investor Relations][APPLE-SPLITS])

Una serie no ajustada produciría discontinuidades mecánicas incompatibles con la lógica. Una serie ajustada evita el salto, pero reescala toda la historia pasada y puede cambiar retrospectivamente:

```text
pendientes absolutas
ángulos
líneas
stops
número de acciones
```

Por ello la estrategia no puede gobernarse únicamente con “precio ajustado sí/no”. Debe versionarse la vista de ajuste utilizada y congelar el dataset de cada réplica.

---

## 4. Reglas exactas de entrada y salida

### 4.1 Entrada long

La formulación mínima es:

```text
close actual cruza por encima de la downtrend line
AND
ángulo de la downtrend line < -10°
THEN
buy next bar at market
```

Matemáticamente:

$$
C_{t-1}\leq D_{t-1}
$$

$$
C_t>D_t
$$

$$
\theta_D<-10^\circ
$$

Ejecución:

```text
apertura de t+1
```

### 4.2 Entrada short

$$
C_{t-1}\geq U_{t-1}
$$

$$
C_t<U_t
$$

$$
\theta_U>20^\circ
$$

Ejecución:

```text
sell short en la apertura de t+1
```

### 4.3 Stop long

Con `LXTrailbar = 2`:

$$
Stop^L_t=\min(L_t,L_{t-1})
$$

La reconstrucción probable en EasyLanguage es una orden para la barra siguiente:

```text
sell next bar at Lowest(Low, 2) stop
```

### 4.4 Stop short

Con `SXTrailbar = 2`:

$$
Stop^S_t=\max(H_t,H_{t-1})
$$

Reconstrucción probable:

```text
buy to cover next bar at Highest(High, 2) stop
```

### 4.5 El stop sólo es “trailing” bajo una semántica concreta

Si el stop calculado al cierre de `t` sólo entra en vigor durante `t+1`, entonces, condicionado a que la posición sobreviva, el stop long no debería alejarse hacia abajo y el short no debería alejarse hacia arriba.

Pero hay que demostrarlo con el motor:

```text
1. stop previo activo durante la barra
2. evaluación de gap de apertura
3. evaluación del rango intrabar
4. sólo después, cálculo del stop siguiente
```

Usar el low de la misma barra para decidir un stop ejecutable dentro de esa misma barra introduciría auto-referencia y look-ahead intrabar.

### 4.6 Sin profit target

No existe:

```text
profit target
salida por cruce inverso
salida temporal
salida de fin de semana
```

La duración queda determinada por el stop.

### 4.7 Re-entries

La estrategia publicada no especifica una regla especial de re-entry. El artículo propone permitir re-entries como mejora futura debido a whipsaws y pullbacks.

No debe incorporarse en la réplica original.

---

## 5. Legalidad temporal y riesgo de repainting

### 5.1 El pivot usa barras “futuras” respecto de su fecha

Esto no es automáticamente look-ahead.

Es legal si:

```text
pivot_date = p
confirmation_date = p + right_strength
first_eligible_decision >= confirmation_date
```

Es ilegal si:

```text
la línea se considera activa desde p
porque visualmente se dibuja hacia atrás hasta p
```

### 5.2 La captura del gráfico no prueba la legalidad

En la página física 5, la línea aparece dibujada desde swings históricos. La imagen muestra geometría, no el timestamp en que el algoritmo conoció cada punto.

La réplica necesita registrar:

```text
pivot_timestamp
pivot_confirmed_at
trendline_created_at
trendline_version
trendline_active_from
trendline_retired_at
```

### 5.3 Test anti-repainting obligatorio

Para cada fecha `t`:

```text
1. ejecutar el detector usando datos sólo hasta t
2. guardar pivots y líneas observables
3. avanzar una barra
4. comprobar que ningún estado pasado ha cambiado
```

Puede cambiar la interpretación histórica del gráfico, pero no el estado que alimentó una decisión pasada.

### 5.4 Borrado de líneas obsoletas

TradeStation borra del gráfico las líneas anteriores. TSIS debe hacer lo contrario a nivel de evidencia:

```text
no borrar
versionar
cerrar vigencia
mantener lineage
```

Sin ello no puede reconciliarse por qué una señal existió en una fecha concreta.

---

## 6. Resultados publicados

### 6.1 Configuración

```text
Activo: AAPL
Bar interval: Daily
History cargada: 10 años, hasta 31/12/2014
Capital inicial: $7,000
Nominal por operación: $5,000
Redondeo: 1 acción
Comisión: $0.01 por acción
Slippage: $0.01 por acción
Profit target: ninguno
Stop: trailing según reglas
```

El report muestra:

```text
rango cargado:
31/12/2004–31/12/2014

periodo efectivo de trading:
9 años, 7 meses, 19 días

curva detallada:
11/05/2005–31/12/2014
```

La diferencia es compatible con un warm-up considerable para reunir swings y construir líneas, pero debe reconciliarse exactamente.

### 6.2 Resultado agregado

| Métrica | Resultado |
|---|---:|
| Beneficio neto | $5,451.52 |
| Gross Profit | $12,430.35 |
| Gross Loss | -$6,978.83 |
| Profit Factor | 1.78 |
| Operaciones | 127 |
| Ganadoras | 45 |
| Perdedoras | 82 |
| Percent Profitable | 35.43% |
| Ganancia media por trade | $42.93 |
| Ganancia media ganadora | $276.23 |
| Pérdida media | -$85.11 |
| Ratio avg win / avg loss | 3.25 |
| Mayor ganadora | $1,338.58 |
| Mayor perdedora | -$362.94 |
| Máx. ganadoras consecutivas | 4 |
| Máx. perdedoras consecutivas | 9 |
| Barras medias en ganadoras | 8.29 |
| Barras medias en perdedoras | 2.79 |
| Return on Initial Capital | 77.88% |
| Annual Rate of Return | 5.97% |
| Return Retracement Ratio | 0.19 |
| RINA Index | 311.02 |
| Tiempo en mercado | 18.97% |

Con un nominal de $5,000:

$$
\frac{42.93}{5000}\approx0.008586
$$

La esperanza publicada equivale aproximadamente a:

```text
85.9 puntos básicos por operación
```

antes de considerar diferencias entre el modelo de apertura diario y una ejecución real.

### 6.3 Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Beneficio neto | $5,311.31 | $140.21 |
| Profit Factor | 2.80 | 1.03 |
| Operaciones | 65 | 62 |
| Percent Profitable | 43.08% | 27.42% |
| Avg. Trade Net Profit | $81.71 | $2.26 |
| Avg. Winning Trade | $295.23 | $244.93 |
| Avg. Losing Trade | -$79.87 | -$89.41 |
| Ratio avg win / avg loss | 3.70 | 2.74 |
| Mayor ganadora | $825.58 | $1,338.58 |
| Mayor perdedora | -$191.01 | -$362.94 |

El lado long produjo:

$$
\frac{5311.31}{5451.52}=97.43\%
$$

El lado short produjo sólo:

```text
$140.21 totales
$2.26 por operación
≈ 4.5 puntos básicos por trade sobre $5,000
```

Ese resultado short es prácticamente indistinguible de cero ante cambios modestos de:

```text
datos
slippage
spread
borrow
dividendos
precio de apertura
```

### 6.4 Qué significa realmente el 35.43% ganador

La tasa de acierto es coherente con una estrategia de payoff asimétrico:

```text
muchas pérdidas pequeñas
pocas ganancias grandes
```

Pero esa forma no demuestra edge. Un sistema puede mostrar la forma clásica de trend following y seguir teniendo expectativa nula o negativa fuera de muestra.

### 6.5 Curva de capital

La página física 7 muestra:

```text
drawdown inicial aproximado de 10%
ascenso general posterior
varios retrocesos y mesetas
```

El propio artículo destaca el problema de iniciar una estrategia en un momento desfavorable. Científicamente, el punto correcto no es escoger una fecha mejor, sino medir la distribución de resultados para todas las fechas de inicio posibles.

---

## 7. ¿Dónde podría estar el edge?

La hipótesis operacional puede expresarse así:

> Cuando una secuencia de lower highs o higher lows define una tendencia suficientemente inclinada, el cierre que rompe esa estructura contiene información sobre una transición persistente de dirección.

Posibles mecanismos:

```text
acumulación de órdenes stop alrededor de líneas visibles
confirmación colectiva de ruptura
inercia posterior a cambio de estructura
sub-reacción a nueva información
salida rápida de falsas rupturas mediante stop corto
```

Pero el backtest no identifica cuál de ellos opera.

La literatura sí ha estudiado la automatización de patrones técnicos y el trend following como familias generales, pero eso no valida esta línea concreta, sus seis inputs ni el uso de ángulos absolutos. ([Lo, Mamaysky y Wang][LO-TECHNICAL]; [Moskowitz, Ooi y Pedersen][MOP-TSM])

### Hipótesis alternativas que explican el PnL

```text
AAPL tuvo una fuerte deriva alcista durante gran parte de la muestra
el lado long concentra 97.4% del beneficio
los parámetros fueron optimizados en el mismo activo y periodo
la escala ajustada del precio favoreció ciertos ángulos
el stop de dos barras captura un perfil convex-like sin que la línea aporte información
```

La prueba central será comparar la estrategia contra modelos más simples con iguales fechas y riesgo.

---

## 8. Problemas científicos y técnicos

### 8.1 Seis inputs optimizados in-sample

Se optimizaron:

```text
SHStren
SLStren
LXTrailbar
SXTrailbar
DownTrendAngle
UpTrendAngle
```

No se publica:

```text
rango de cada input
paso de búsqueda
número de combinaciones
criterio de selección
resultados descartados
periodo de validación
walk-forward
corrección por multiple testing
```

La literatura sobre reglas técnicas advierte precisamente que evaluar muchas configuraciones y presentar la seleccionada infla el resultado aparente. ([Sullivan, Timmermann y White][STW-DATASNOOP])

### 8.2 Un único activo

El claim editorial dice que puede aplicarse a equities, futures y forex, pero el resultado publicado corresponde sólo a:

```text
AAPL daily
```

No se demuestra portabilidad.

### 8.3 Concentración casi total en longs

Un Profit Factor agregado de 1.78 oculta:

```text
long PF = 2.80
short PF = 1.03
```

La estrategia publicada no ha demostrado un edge short.

### 8.4 Ángulo no invariante

`TLAngle` aplica arcotangente a una pendiente de precio por barra. ([Ayuda TradeStation][TS-TLANGLE])

El resultado cambia con:

```text
nivel nominal del precio
split adjustment
moneda
point value
timeframe
```

Un input expresado como “20 grados” no representa un fenómeno económico estable.

### 8.5 Riesgo de repainting

Los pivotes requieren barras posteriores. Si la línea se activa retroactivamente, el backtest queda invalidado.

Éste es el gate más importante de la réplica.

### 8.6 Ambigüedad del motor de stops con OHLC diario

Con una barra diaria sólo conocemos:

```text
open
high
low
close
```

No conocemos el camino intradía. Cuando coinciden:

```text
gap
stop
posible nueva señal
cambio de línea
```

el orden de eventos puede alterar el PnL.

### 8.7 Corporate actions

AAPL sufrió dos splits dentro del periodo cargado. ([Apple Investor Relations][APPLE-SPLITS])

Hay que separar:

```text
vista ajustada para señal
vista raw para ejecución
factor de ajuste vigente
cantidad de acciones
```

### 8.8 Short real incompleto

El backtest no acredita:

```text
locate
hard-to-borrow
borrow fee
dividendos pagados por la posición short
restricciones de venta en corto
```

En AAPL el problema puede ser pequeño comparado con small caps, pero el lado short ya tiene sólo $2.26 de esperanza publicada.

### 8.9 Warm-up no documentado

El test carga datos desde diciembre de 2004, pero la curva efectiva comienza en mayo de 2005.

No se publica:

```text
MaxBarsBack
cuántos pivots exige antes de operar
estado inicial de las líneas
```

### 8.10 Ties y pivots simultáneos

La desigualdad es asimétrica, pero no sabemos cómo resuelve el código:

```text
dos swing highs con mismo precio
un nuevo swing high y swing low confirmados el mismo día
múltiples anchors válidos entre los últimos diez
```

### 8.11 Re-entry como grado de libertad adicional

El artículo propone re-entry, ángulos de 45 grados y exits distintos por lado.

Cada sugerencia crea nuevas decisiones. No son mejoras gratuitas: deben tratarse como nuevas hipótesis con presupuesto de búsqueda.

---

## 9. Cómo debe implementarse en TSIS

### 9.1 Separación de vistas

```text
SIGNAL VIEW:
OHLC diario ajustado y versionado

EXECUTION VIEW:
open raw operable de la sesión siguiente
```

En la arquitectura TSIS actual, la señal podría consumir una vista diaria gobernada equivalente a `004_master_daily_table`, mientras que la ejecución realista debería mapearse a la vista raw/quote-guarded autorizada.

### 9.2 Registro de pivots

Campos mínimos:

```text
symbol
pivot_id
pivot_type
pivot_timestamp
pivot_price
left_strength
right_strength
confirmed_at
source_price_view
adjustment_version
status
```

### 9.3 Registro de trendlines

```text
trendline_id
trendline_type
anchor_older_pivot_id
anchor_recent_pivot_id
created_at
active_from
retired_at
slope_price_per_bar
angle_degrees
value_at_decision
source_lineage
```

### 9.4 Estado de decisión

```text
session_date
decision_timestamp
active_downtrendline_id
active_uptrendline_id
downtrend_value
downtrend_angle
uptrend_value
uptrend_angle
close
cross_up
cross_down
long_eligible
short_eligible
signal
```

### 9.5 Estados de no decisión

```text
INSUFFICIENT_HISTORY
NO_CONFIRMED_SWING_HIGH
NO_CONFIRMED_SWING_LOW
NO_COMPATIBLE_SECOND_ANCHOR
CORPORATE_ACTION_BOUNDARY_UNRESOLVED
PRICE_VIEW_UNAVAILABLE
EXECUTION_SESSION_UNAVAILABLE
```

No deben convertirse en `False` genérico.

### 9.6 Política de corporate actions

Cada decisión debe indicar:

```text
adjustment_factor_as_of_t
adjustment_policy
raw_open_t_plus_1
adjusted_signal_prices
```

Un nuevo split no debe cambiar silenciosamente los artefactos ya validados.

### 9.7 Política de fills

Para entrada market next bar:

```text
base replication:
daily official open

realistic replication:
opening auction / first valid quote / first 1m executable price
```

Para stop:

```text
if gap beyond stop:
fill at open or governed first executable price

if intraday touch:
fill at stop plus slippage model
```

### 9.8 Lineage visual

La imagen del chart es sólo una representación. El objeto científico es:

```text
qué línea existía
cuándo existía
qué valor tenía en t
qué datos la justificaban
```

---

## 10. Pseudocódigo de referencia

```python
for t in daily_sessions:

    # 1. Confirmar nuevos pivots solamente con datos disponibles hasta t.
    confirm_swing_highs(
        current_session=t,
        right_strength=SHStren,
        left_strength=SHStren,
    )

    confirm_swing_lows(
        current_session=t,
        right_strength=SLStren,
        left_strength=SLStren,
    )

    # 2. Construir o actualizar líneas a partir de pivots ya confirmados.
    down_line = build_downtrend_line(
        confirmed_swing_highs=last_10_confirmed_highs,
        selection_rule="recent_plus_next_older_higher",
    )

    up_line = build_uptrend_line(
        confirmed_swing_lows=last_10_confirmed_lows,
        selection_rule="recent_plus_next_older_lower",
    )

    # 3. Gestionar primero las órdenes activas durante la barra.
    process_existing_stop_orders(t)

    # 4. Al cierre, calcular señales para la apertura siguiente.
    if position_is_flat_at_close(t):

        if down_line.is_available:
            d_now = down_line.value_at(t)
            d_prev = down_line.value_at(t - 1)

            long_signal = (
                close[t - 1] <= d_prev
                and close[t] > d_now
                and down_line.angle_degrees < DownTrendAngle
            )

            if long_signal:
                schedule_long_market(entry_session=t + 1)

        if up_line.is_available:
            u_now = up_line.value_at(t)
            u_prev = up_line.value_at(t - 1)

            short_signal = (
                close[t - 1] >= u_prev
                and close[t] < u_now
                and up_line.angle_degrees > UpTrendAngle
            )

            if short_signal:
                schedule_short_market(entry_session=t + 1)

    # 5. El stop calculado con información de t sólo será activo en t+1.
    if position_is_long_at_close(t):
        stop = min(low[t], low[t - 1])
        schedule_long_stop(session=t + 1, price=stop)

    elif position_is_short_at_close(t):
        stop = max(high[t], high[t - 1])
        schedule_short_stop(session=t + 1, price=stop)
```

Este pseudocódigo no resuelve las ambigüedades del `.ELD`; las hace visibles.

---

## 11. Cómo demostrar o destruir el supuesto edge

### Fase 1 — Réplica histórica exacta

```text
AAPL daily
31/12/2004–31/12/2014
inputs publicados sin modificación
$5,000 por trade
costes publicados
```

Checksums de resultado:

```text
127 trades
65 longs
62 shorts
$5,451.52 netos
PF 1.78
35.43% ganadoras
```

### Fase 2 — Gate anti-repainting

Para cada trade:

```text
pivots disponibles en decision_timestamp
fecha real de confirmación
línea activa
valor y ángulo
cruce del cierre
```

Cualquier trade que dependa de un pivot no confirmado invalida la réplica.

### Fase 3 — Reconciliación de corporate actions

Comparar:

```text
TradeStation adjusted
split-adjusted propio
raw + corporate-action ledger
```

Las fechas de señal deben coincidir; el PnL raw debe reconciliarse por separado.

### Fase 4 — Verdadero OOS postpublicación

Para evitar dudas sobre el día exacto de distribución del número, congelar la especificación y comenzar en:

```text
02/03/2015
```

hasta la última sesión completa disponible.

No modificar:

```text
strengths
trailbars
angles
selección de anchors
```

### Fase 5 — Descomposición long/short

Informar separadamente:

```text
long original
short original
long-only
short-only
```

El lado short debe superar un test independiente; no puede esconderse detrás del resultado long.

### Fase 6 — Placebos estructurales

Comparar las mismas fechas y riesgos con:

| Placebo | Pregunta |
|---|---|
| Donchian breakout | ¿La trendline aporta algo frente a romper máximos/mínimos? |
| Moving-average crossover | ¿Es sólo una transición de tendencia genérica? |
| Ruptura horizontal del último pivot | ¿El ángulo es necesario? |
| Señal sin filtro angular | ¿Los grados mejoran OOS? |
| Fechas aleatorias con mismo holding profile | ¿La selección temporal tiene información? |
| Long AAPL con stop de 2 barras | ¿La línea aporta algo frente al drift alcista? |

### Fase 7 — Invariancia

Repetir con:

```text
precio original
log-precio
slope porcentual
slope / ATR
slope / rolling volatility
```

No para escoger retrospectivamente el mejor, sino para determinar si el fenómeno sobrevive a una representación económicamente coherente.

### Fase 8 — Robustez de parámetros

Estudiar vecindarios alrededor de:

```text
SHStren = 3
SLStren = 6
LXTrailbar = 2
SXTrailbar = 2
DownTrendAngle = -10
UpTrendAngle = 20
```

El objetivo es una meseta, no un máximo puntual.

Si se prueban muchas configuraciones deben aplicarse técnicas de control de selección como [DSR][DSR], [PBO][PBO] y [White Reality Check][WHITE-RC].

### Fase 9 — Ejecución

Escenarios:

```text
official daily open
opening auction
first valid 1m quote
5 / 10 / 20 / 50 bps de slippage
gap-through-stop
```

### Fase 10 — MFE/MAE y whipsaw

Medir antes de diseñar re-entries:

```text
maximum favorable excursion
maximum adverse excursion
días hasta máximo favorable
pérdida devuelta antes del stop
continuación tras stop
```

---

## 12. Variantes que merecen estudiarse después de la réplica

### Variante A — Slope porcentual

$$
m^{pct}=\frac{\log(P_1)-\log(P_0)}{\Delta bars}
$$

Ventaja:

```text
invariante al nivel nominal del precio
compatible entre activos
```

### Variante B — Slope normalizado por ATR

$$
m^{ATR}=\frac{P_1-P_0}{\Delta bars\cdot ATR}
$$

Interpreta la inclinación en unidades de volatilidad.

### Variante C — Sin filtro angular

Permite medir si:

```text
el breakout tiene edge
```

frente a:

```text
el breakout + filtro optimizado tiene edge adicional
```

### Variante D — Re-entry preregistrado

Ejemplo:

```text
máximo una re-entry
misma línea
ventana máxima N barras
sin reoptimizar el stop
```

### Variante E — Exits diferentes por lado

El artículo lo sugiere debido al pobre short.

Debe evaluarse como dos estrategias separadas, no como una única regla simétrica.

### Variante F — Regresión robusta

Sustituir dos puntos por:

```text
regresión sobre pivots
Theil-Sen
RANSAC
```

Esto reduce sensibilidad a un anchor puntual, pero aumenta complejidad y grados de libertad.

### Variante G — Portfolio de activos

Congelar la regla y probar un universo predefinido con:

```text
survivorship-free membership
corporate actions
costes
borrow
```

---

## 13. Encaje en Market State y Event State

### Market State observable en `t`

```text
last_confirmed_swing_high
last_confirmed_swing_low
swing_high_age
swing_low_age
active_downtrend_slope
active_uptrend_slope
active_downtrend_angle
active_uptrend_angle
distance_to_downtrend
distance_to_uptrend
corporate_action_state
```

### Eventos

```text
event_type:
swing_high_confirmed

event_type:
swing_low_confirmed

event_type:
auto_trendline_constructed

event_type:
auto_trendline_breakout
```

### Outcome

```text
forward_return_1d_5d_10d
MFE
MAE
time_to_stop
continuation_after_break
false_break_probability
reentry_opportunity
```

### Distinción clave

```text
Evento:
ruptura de una trendline observable y versionada

Estrategia:
entrar next open y salir con stop de dos barras
```

El evento puede contener información aunque la respuesta operativa publicada no sea la mejor.

---

## 14. Transferencia a small caps, futuros y forex

### Small caps

No debe trasladarse directamente con grados absolutos.

Problemas adicionales:

```text
gaps grandes
halts
splits y reverse splits
baja liquidez
spreads
borrow
catalizadores idiosincráticos
```

En TSIS sería más útil como:

```text
detector de cambio de estructura
```

condicionado por:

```text
news_catalyst_context
liquidity
halt_context
short_side_context
volatility_range_state
```

### Futuros

La pendiente debe expresarse en:

```text
ticks por barra
ATR por barra
retorno logarítmico por barra
```

Y debe resolverse el roll de contratos.

### Forex

Debe gobernarse:

```text
zona horaria
cierre diario
fin de semana
moneda de cotización
pip value
```

La afirmación editorial de portabilidad no queda demostrada por el test en AAPL.

---

## 15. Veredicto de Auto-Trendline

| Cuestión | Decisión |
|---|---|
| ¿Implementar? | **Sí**, como réplica y prueba anti-repainting. |
| ¿Aceptar PF 1.78 como edge? | **No.** |
| ¿Mantener grados como representación final? | **No sin comparación normalizada.** |
| ¿Optimizar de nuevo antes del OOS? | **No.** |
| ¿Operar el lado short? | **No; el resultado publicado es marginal.** |
| ¿Valor para TSIS? | **Alto como prueba de pivots, event sourcing y corporate actions.** |

Siguiente gate propuesto:

```text
AUTO-TRENDLINE-PIVOT-CONFIRMATION-AND-SCALE-INVARIANCE-GATE
```

---

# Parte II — Estrategia 004: The VIX Pivot Strategy

## 1) Identificación y rendimiento

- **ID de estrategia:** `SCC-2015-02-STRAT-004`
- **Artículo:** *The VIX Pivot Strategy*
- **Autor:** **Michael Burke**
- **Páginas físicas del PDF:** 9–13
- **Páginas impresas del artículo:** 7–11
- **Estilo declarado:** Bar pattern
- **Mercados declarados:** Major Market Index Futures and ETFs
- **Horizonte declarado:** Swing trading
- **Dirección:** Long-only
- **Instrumento operado en el backtest:** e-mini S&P 500 continuous contract (`@ES`)
- **Fuente de señal:** CBOE Volatility Index (`$VIX.X`)
- **Frecuencia:** Daily
- **Archivos auxiliares:** `.ELD` y workspace `.tsw`

### Inputs publicados

| Input | Default | Función declarada |
|---|---:|---|
| `VIXSymbol` | `"$VIX.X"` | Símbolo del índice de volatilidad |
| `VIXHighestHighLen` | 13 | Lookback del highest high para entradas |
| `VIXLowestHighLen` | 21 | Lookback del lowest high para salidas |
| `EntryVIXThreshold` | 17 | VIX mínimo para permitir entrada |
| `ExitVIXThreshold` | 15 | VIX máximo para permitir salida |
| `StopLoss` | 10000 | Stop monetario opcional; efectivamente desactivado en el test |

### Evidencia adicional del ZIP

El workspace `TSL.VIX Pivot.tsw` confirma:

```text
chart principal:
@ES Daily [CME] E-mini S&P 500 Continuous Contract [Mar15]

analysis technique:
TSL:VIX Pivot

VIXSymbol:
"$VIX.X"

inputs registrados:
VIXHighestHighLen
VIXLowestHighLen
EntryVIXThreshold
ExitVIXThreshold
StopLoss

referencia secundaria visible:
$VIX.X
CBOE Volatility Index
```

El workspace también confirma que el chart principal utiliza el continuous root `@ES`, no un contrato físico individual.

El `.ELD` sigue siendo binario y no permite leer el código fuente en este entorno.

### Resultados destacados publicados

- **Total Net Profit:** $34,667.50
- **Operaciones:** 12
- **Ganadoras:** 12
- **Perdedoras:** 0
- **Percent Profitable:** 100.00%
- **Avg. Trade Net Profit:** $2,888.96
- **Largest Winning Trade:** $4,752.50
- **Avg. Bars in Winning Trades:** 31.25
- **Return on Initial Capital:** 173.34%
- **Percent of Time in the Market:** 53.67%
- **Maximum Trade Drawdown:** -$7,400
- **RINA Index:** 24.18

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse? | **Sí**, con datos diarios VIX y contratos físicos ES. |
| ¿La revista demuestra un edge? | **No.** Doce trades seleccionados tras optimización son evidencia muy débil. |
| ¿La tesis es plausible? | **Sí:** reversión de picos de volatilidad y recuperación de equities. |
| ¿El 100% de aciertos es creíble como estimador futuro? | **No.** |
| ¿Existe riesgo de cola? | **Sí, explícito:** no se usó stop y el trade drawdown llegó a $7,400. |
| ¿Puede replicarse sólo con el PDF? | **Aproximadamente.** La sesión diaria de `@ES` y el objeto de datos VIX requieren confirmación. |
| ¿Está lista para real? | **No.** |

Clasificación TSIS:

```text
SOURCE_REPRODUCTION_CANDIDATE
MULTI_SOURCE_SIGNAL
ABSOLUTE_THRESHOLD_REGIME_RISK
TINY_SAMPLE
OPTIMIZATION_SELECTION_RISK
TAIL_RISK_UNBOUNDED_IN_PUBLICATION
CONTINUOUS_FUTURES_RISK
POSTPUBLICATION_OOS_AVAILABLE
NOT_LIVE_ELIGIBLE
```

---

## 2. Qué estrategia es realmente

La estrategia no opera el VIX.

```text
OBSERVA:
$VIX.X

OPERA:
@ES
```

Cboe define el VIX como una medida de volatilidad esperada derivada de precios de opciones SPX. El índice no es directamente operable. ([Cboe][CBOE-VIX])

La lógica intenta identificar dos estados:

```text
ENTRADA:
un pico local del high diario del VIX comienza a revertir

SALIDA:
un mínimo local del high diario del VIX comienza a repuntar
```

La estrategia es:

```text
long-only
contrarian respecto del miedo/volatilidad
sin filtro de precio de ES
sin short
sin stop en los resultados publicados
```

No espera que el VIX caiga hasta un target concreto para entrar. Entra cuando un high extremo queda confirmado por un high inferior en la barra siguiente.

Tampoco usa el low del VIX para salir. Usa el **mínimo de los highs diarios**, porque el autor considera que el high de VIX es más significativo.

---

## 3. Reconstrucción matemática

Sea:

```text
V_t = high diario de $VIX.X en la sesión t
```

### 3.1 Pivot-high de entrada

La barra candidata es `t-1`.

Con `N_H = VIXHighestHighLen = 13`:

$$
V_{t-1}>\max(V_{t-2},V_{t-3},\ldots,V_{t-1-N_H})
$$

Y la barra actual confirma la reversión:

$$
V_t<V_{t-1}
$$

Además:

$$
V_{t-1}>EntryVIXThreshold
$$

Con default:

```text
VIX pivot high > 17
```

La señal se conoce al finalizar la barra `t`.

### 3.2 Pivot-low de salida

De nuevo, la barra candidata es `t-1`, pero se estudia la serie de **highs**.

Con `N_L = VIXLowestHighLen = 21`:

$$
V_{t-1}<\min(V_{t-2},V_{t-3},\ldots,V_{t-1-N_L})
$$

Y:

$$
V_t>V_{t-1}
$$

Threshold:

$$
V_{t-1}<ExitVIXThreshold
$$

Con default:

```text
VIX pivot low < 15
```

### 3.3 Pivot asimétrico

No es un pivot simétrico de 13 barras a la izquierda y 13 a la derecha.

Es:

```text
left strength entrada = 13
right confirmation = 1

left strength salida = 21
right confirmation = 1
```

La señal tiene una latencia de una barra respecto del máximo o mínimo local.

### 3.4 Igualdades

El texto usa:

```text
greater than
lower than
```

Por tanto, la reconstrucción usa desigualdad estricta. El `.ELD` debe confirmar qué ocurre con highs iguales.

### 3.5 Entrada

Al cierre de `t`:

```text
pivot_high_entry = True
AND
VIX pivot high > 17
```

Orden:

```text
buy @ES at market on open of t+1
```

### 3.6 Salida

Al cierre de `t`:

```text
pivot_low_exit = True
AND
VIX pivot high candidate < 15
```

Orden:

```text
sell @ES at market on open of t+1
```

### 3.7 Histeresis

Los thresholds crean dos regiones distintas:

```text
entrada por encima de 17
salida por debajo de 15
```

Esto evita entrar y salir en el mismo nivel y crea una banda de histéresis.

Pero también convierte la estrategia en dependiente del régimen absoluto de VIX.

### 3.8 StopLoss

```text
StopLoss = 10000
```

El artículo explica que un valor tan grande lo vuelve irrelevante y que **no se utilizó stop en los resultados publicados**.

Por tanto, la réplica original debe mantener:

```text
stop disabled
```

Una réplica con stop ya sería otra estrategia.

---

## 4. Cronología exacta y ambigüedad de sesiones

### 4.1 Decision timestamp

La señal usa el high completo de la barra VIX actual. Por tanto, no puede conocerse antes de finalizar el periodo de cálculo del VIX de esa sesión.

TSIS debe imponer:

```text
VIX bar finalized
AND
ES signal bar finalized
BEFORE
order scheduling
```

### 4.2 ¿Qué es “open of next bar” en `@ES Daily`?

El workspace muestra:

```text
@ES Daily
sin extensión .D
```

TradeStation distingue el continuous root y la extensión `.D` para sesión electrónica diurna. ([TradeStation Futures Symbology][TS-FUTURES])

El PDF no publica:

```text
session template del chart
hora de cierre de la barra diaria
hora de apertura de la barra siguiente
zona horaria
```

En un futuro casi 24 horas, “next daily open” puede significar una apertura Globex, no la apertura cash de 9:30 ET.

Eso cambia:

```text
retorno capturado
slippage
gap
legalidad temporal
comparación con SPY
```

### 4.3 Alineación VIX–ES

El VIX procede de la sesión de opciones SPX; ES opera durante más horas.

Se necesita una unión explícita:

```text
vix_session_date
vix_finalized_at
es_session_id
es_daily_bar_open
es_daily_bar_close
execution_timestamp
```

No debe alinearse sólo por una etiqueta de fecha.

### 4.4 Ausencia de barra

Si existe sesión ES pero no barra VIX válida:

```text
signal = NO_DECISION
```

No se permite forward-fill del high de VIX.

---

## 5. Resultados publicados

### 5.1 Configuración

```text
Símbolo: @ES con $VIX.X
Bar interval: Daily
Capital inicial: $20,000
Trade size: 1 contrato
Comisión: $2.50 por contrato
Slippage: $2.50 por contrato
Stop loss: ninguno
Date range publicado: 01/01/2012–27/01/2015
```

La curva detallada muestra:

```text
15/03/2012–28/01/2015
```

La discrepancia de fechas puede proceder de warm-up, primera operación o ejecución next-bar, pero debe reconciliarse.

### 5.2 Tabla completa publicada

| Métrica | Resultado |
|---|---:|
| Total Net Profit | $34,667.50 |
| Gross Profit | $34,667.50 |
| Gross Loss | $0.00 |
| Total Trades | 12 |
| Winning Trades | 12 |
| Losing Trades | 0 |
| Percent Profitable | 100.00% |
| Avg. Trade Net Profit | $2,888.96 |
| Avg. Winning Trade | $2,888.96 |
| Largest Winning Trade | $4,752.50 |
| Max. Consecutive Winning Trades | 12 |
| Avg. Bars in Winning Trades | 31.25 |
| Max. Contracts Held | 1 |
| Return on Initial Capital | 173.34% |
| Return Retracement Ratio | 9.84 |
| RINA Index | 24.18 |
| Max. Equity Run-up | $45,505.00 |
| Percent of Time in the Market | 53.67% |
| Net Profit as % of Drawdown | 438.83% |
| Max. Trade Drawdown | -$7,400.00 |

### 5.3 Profit Factor no es “infinito” como evidencia

El report muestra `n/a` porque:

```text
gross loss = 0
```

No existe un estimador estable de Profit Factor con cero pérdidas observadas. No debe reemplazarse por infinito ni compararse con PF normales.

### 5.4 Doce de doce

Incluso ignorando selección y dependencia, 12 éxitos de 12 siguen siendo una muestra pequeña. Un intervalo binomial exacto bilateral del 95% permite una tasa real muy inferior al 100%.

Pero el problema principal es todavía mayor:

```text
los 12 trades no fueron una muestra pre-registrada
los thresholds fueron seleccionados tras optimización
```

### 5.5 Drawdown por trade

$$
\frac{7400}{20000}=37\%
$$

El máximo trade drawdown equivale al 37% del capital inicial declarado.

También equivale aproximadamente al 21.3% del beneficio neto final.

El artículo lo describe como la métrica de mayor preocupación.

### 5.6 El stop sugerido de $10,000

El texto propone considerar un stop cercano a $10,000 para dar margen a la estrategia.

Sobre $20,000 de capital inicial:

```text
stop sugerido = 50% del capital
```

Esto no es una protección ligera. Revela que el sistema necesita soportar movimientos adversos muy grandes para conservar los resultados publicados.

### 5.7 Tiempo en mercado

```text
53.67% del tiempo
31.25 barras por trade
```

La estrategia captura una parte sustancial de la exposición long al mercado. Por ello debe compararse con un benchmark de beta y con ventanas long aleatorias de duración similar.

---

## 6. Optimización publicada

La figura 6 muestra una tabla de optimización de:

```text
EntryVIXThreshold
ExitVIXThreshold
```

La fila correspondiente a los defaults:

```text
17 / 15
```

presenta:

```text
12 trades
100% profitable
$34,667.50 netos
TS Index 56.26
```

El artículo afirma que no escogió simplemente el mayor beneficio, sino una combinación con:

```text
TS Index alto
cero pérdidas
más de 10 trades
```

Eso es mejor que escoger únicamente el máximo PnL, pero sigue siendo **selección in-sample**.

### 6.1 Muchas filas ganadoras no equivalen a muchos experimentos independientes

Las configuraciones cercanas comparten:

```text
mismas crisis
mismos rallies
mismas ventanas de holding
mismos trades o trades muy solapados
```

La aparente robustez visual de la tabla puede exagerar la cantidad de evidencia independiente.

### 6.2 Periodic optimization

El artículo sugiere optimizaciones periódicas para adaptar los thresholds al nivel cambiante del VIX.

Eso transforma la regla en:

```text
estrategia adaptativa
```

Y requiere definir:

```text
ventana de training
frecuencia de recalibración
criterio objetivo
embargo
parámetros permitidos
fecha de activación
```

Sin esas reglas, “reoptimizar periódicamente” introduce discrecionalidad retrospectiva.

---

## 7. ¿Dónde podría estar el edge?

La tesis puede formularse así:

> Un máximo reciente y elevado del high de VIX, seguido de un high inferior, señala que la fase de pánico está remitiendo; la recuperación posterior de la renta variable persiste hasta que el VIX alcanza un régimen bajo y empieza a repuntar.

Cboe describe tres propiedades generales relevantes:

```text
relación normalmente inversa con SPX
mean reversion del VIX
movimientos más rápidos y grandes que el índice
```

Pero también advierte que la relación inversa no se cumple siempre. ([Cboe][CBOE-VIX])

La investigación académica ha encontrado que el VIX y la prima de varianza contienen información sobre retornos y riesgo, pero no valida estos pivots, lookbacks ni thresholds exactos. ([Bekaert y Hoerova][BEKAERT-VIX])

### Hipótesis alternativas

El PnL podría proceder de:

```text
prima estructural long de equities
bull market 2012–2015
comprar después de drawdowns de SPX
permanecer long 53.67% del tiempo
selección de thresholds
continuous contract construction
```

La relación con el pivot VIX sólo queda demostrada si supera esos placebos.

---

## 8. Problemas científicos y técnicos

### 8.1 Sólo 12 operaciones

No permiten estimar con fiabilidad:

```text
probabilidad de pérdida
colas
drawdown de cartera
estabilidad de thresholds
comportamiento en distintos regímenes
```

### 8.2 Selección tras optimización

Los thresholds 17 y 15 fueron seleccionados dentro de una tabla de alternativas.

No existe:

```text
OOS publicado
walk-forward
corrección por búsqueda
```

### 8.3 Muestra 2012–2015

La propia revista describe 2012–2014 como periodo relativamente tranquilo y reconoce que 2008–2012 habría exigido ajustar inputs.

Una estrategia que necesita cambiar sus thresholds para atravesar el régimen difícil no ha demostrado estabilidad.

### 8.4 Long-only y beta

No existe short side.

El backtest debe informar:

```text
beta a ES
alpha frente a exposición equivalente
captura de buy-and-hold
```

### 8.5 Sin stop en el resultado

El sistema asume que una fase de volatilidad extrema terminará antes de producir una pérdida intolerable.

El propio autor excluye eventos catastróficos del entorno normal para el que fue diseñado.

Eso no elimina el riesgo; lo deja fuera del backtest.

### 8.6 Maximum Trade Drawdown de $7,400

Un sistema con 100% de cierres ganadores puede experimentar pérdidas flotantes enormes.

Por tanto:

```text
win rate = 100%
```

no significa:

```text
riesgo pequeño
```

### 8.7 Continuous futures

TradeStation documenta que `@ES` enlaza contratos históricos en rollovers y que el root continuous no es directamente automatizable. ([TradeStation][TS-FUTURES])

Una réplica científica necesita:

```text
regla de roll
back adjustment
contrato físico operado
coste de roll
P&L por contrato real
```

### 8.8 Sesión diaria no publicada

Sin session template no sabemos a qué hora se ejecuta “next bar at market”.

### 8.9 High de VIX como dato sensible

El high diario puede depender de:

```text
picos breves
quotes de opciones
metodología del índice
calidad del proveedor
```

Cboe calcula el VIX a partir de midpoints de quotes de opciones SPX. ([Cboe][CBOE-VIX])

La réplica debe usar una fuente oficial o gobernada y registrar revisiones.

### 8.10 Thresholds absolutos

```text
17
15
```

no representan el mismo percentil ni el mismo régimen en todas las épocas.

### 8.11 Dependencia serial

Con 31.25 barras medias por trade y 53.67% de exposición, las observaciones no son doce ensayos independientes de un día.

### 8.12 Costes mínimos

```text
$2.50 comisión
$2.50 slippage
```

son pequeños frente a un contrato ES y no cubren necesariamente:

```text
gap de sesión
roll
latencia
spread en la hora exacta de apertura
```

### 8.13 SPY no es una simple reducción de tamaño

El artículo propone SPY como alternativa menor.

Cambiar ES por SPY modifica:

```text
horario
open
dividendos
financiación
tracking
session gaps
```

Debe ser otro contrato de réplica.

### 8.14 Inconsistencia menor de frecuencia

Doce trades entre 2012 y enero de 2015 equivalen aproximadamente a cuatro trades anuales, mientras el texto habla de cinco o seis. No cambia el veredicto, pero confirma que las cifras narrativas deben reconciliarse con el report y no tomarse como autoridad superior.

---

## 9. Cómo debe implementarse en TSIS

### 9.1 Dos instrumentos, dos roles

```text
signal_subject:
$VIX.X

execution_subject:
ES physical contract
```

### 9.2 Fuente VIX gobernada

Campos:

```text
vix_symbol
vix_session_date
vix_high
vix_source
vix_methodology_version
vix_bar_finalized_at
data_quality_status
```

### 9.3 Estado del pattern

```text
entry_lookback_high
entry_pivot_candidate_high
entry_pivot_confirmed
entry_threshold_pass

exit_lookback_low_of_highs
exit_pivot_candidate_high
exit_pivot_confirmed
exit_threshold_pass
```

### 9.4 Estado de posición

```text
position_state
entry_signal_date
entry_execution_timestamp
entry_contract
entry_price
current_MFE
current_MAE
exit_signal_date
exit_execution_timestamp
```

### 9.5 Mapeo continuous → físico

```text
continuous_symbol
continuous_construction
roll_trigger
adjustment_method
physical_contract_at_t
roll_event
roll_cost
```

### 9.6 Calendario y timestamps

```text
vix_close/finalization
es_session_close
es_next_session_open
cash_market_open
```

La réplica exacta y la versión operable deben poder diferir, pero no confundirse.

### 9.7 Stop

Para réplica:

```text
STOP_DISABLED_BY_SOURCE
```

Para investigación posterior:

```text
stop_variant_id
stop_defined_before_test
```

### 9.8 Estado de indisponibilidad

```text
VIX_BAR_UNAVAILABLE
VIX_BAR_NOT_FINAL
SESSION_ALIGNMENT_UNRESOLVED
PHYSICAL_CONTRACT_UNRESOLVED
ROLL_BOUNDARY
EXECUTION_PRICE_UNAVAILABLE
```

### 9.9 Encaje ontológico

La señal pertenece principalmente a:

```text
broad_market_context
volatility_range_state
```

No debería convertirse en una feature aislada sin lineage.

---

## 10. Pseudocódigo de referencia

```python
for t in aligned_daily_sessions:

    vix_high_t = vix_high[t]
    vix_high_prev = vix_high[t - 1]

    prior_entry_highs = [
        vix_high[t - k]
        for k in range(2, VIXHighestHighLen + 2)
    ]

    prior_exit_highs = [
        vix_high[t - k]
        for k in range(2, VIXLowestHighLen + 2)
    ]

    entry_pivot = (
        vix_high_prev > max(prior_entry_highs)
        and vix_high_t < vix_high_prev
        and vix_high_prev > EntryVIXThreshold
    )

    exit_pivot = (
        vix_high_prev < min(prior_exit_highs)
        and vix_high_t > vix_high_prev
        and vix_high_prev < ExitVIXThreshold
    )

    if position_is_flat_at_close(t) and entry_pivot:
        physical_contract = resolve_es_contract(next_session=t + 1)

        schedule_long_market(
            contract=physical_contract,
            execution_timestamp=governed_next_daily_open(t),
        )

    elif position_is_long_at_close(t) and exit_pivot:
        schedule_exit_market(
            execution_timestamp=governed_next_daily_open(t),
        )

    # La réplica publicada no activa el stop monetario.
```

Ambigüedades pendientes:

```text
inclusión exacta de las 13/21 barras
tratamiento de igualdad
session template
datos VIX mediante objetos
pyramiding / re-entry por Strategy Properties
```

---

## 11. Cómo demostrar o destruir el supuesto edge

### Fase 1 — Réplica 2012–2015

Objetivo:

```text
12 trades
12 ganadoras
$34,667.50 netos
31.25 barras medias
$7,400 max trade drawdown
```

Reconciliar fechas exactas y contratos.

### Fase 2 — Reconciliación temporal

Para cada señal:

```text
VIX pivot date
confirmation date
VIX finalized_at
ES bar close
ES next open
physical contract
```

### Fase 3 — Verdadero OOS postpublicación

Congelar:

```text
13 / 21 / 17 / 15
sin stop
sin scaling
una entrada
```

OOS conservador:

```text
02/03/2015 → última sesión completa disponible
```

### Fase 4 — Segmentación temporal

```text
2015–2017
2018–2020
2021–2023
2024–2026
```

Informar por periodo y agregado.

### Fase 5 — Benchmarks

| Benchmark | Pregunta |
|---|---|
| Buy-and-hold ES | ¿El sistema añade algo frente a estar long? |
| Long aleatorio 53.67% del tiempo | ¿La selección temporal supera exposición equivalente? |
| VIX > 17 sin pivot | ¿El pivot aporta información? |
| Pivot VIX sin threshold | ¿El threshold aporta información? |
| Drawdown SPX + rebote | ¿VIX añade algo al propio precio del índice? |
| Fechas de entrada reales + salida temporal fija | ¿La salida VIX mejora? |
| Entradas aleatorias + salida VIX | ¿La salida explica el resultado? |

### Fase 6 — Descomposición de retorno

Separar:

```text
next Globex open → cash open
cash open → cash close
cash close → next Globex open
roll return
```

### Fase 7 — Ejecución física

```text
contratos ES reales
roll gobernado
comisión realista
slippage por hora
margen y capital
```

Y una réplica separada en SPY.

### Fase 8 — Tail stress

Medir:

```text
MAE por trade
worst open loss
worst close-to-close loss
capital necesario
probabilidad de margin call
```

El resultado no debe eliminar trades difíciles mediante un stop descubierto a posteriori.

### Fase 9 — Superficie de thresholds

Reproducir la superficie sin seleccionar un nuevo máximo.

Después aplicar:

```text
walk-forward
DSR
PBO / CSCV
White Reality Check o Hansen SPA
```

### Fase 10 — Régimen VIX

Comparar thresholds absolutos con:

```text
percentil rolling
z-score robusto
ratio a mediana
MAD
```

Sólo después de cerrar el OOS original.

### Fase 11 — Prueba de high contaminado

Comparar:

```text
VIX high
VIX close
high persistente N minutos
percentil intradía
```

Para medir si una sola impresión extrema domina la señal.

---

## 12. Variantes que merecen estudiarse después de la réplica

### Variante A — Threshold percentil

```text
entrada:
VIX en percentil alto rolling

salida:
VIX en percentil bajo rolling
```

Más estable entre regímenes, pero no es la estrategia publicada.

### Variante B — Magnitud del spike

$$
Spike_t=\frac{VIXHigh_t-Median(VIX)}{MAD(VIX)}
$$

### Variante C — Pivot sobre close

Reduce sensibilidad a highs breves.

### Variante D — Exit trailing sobre ES

Permite separar:

```text
entrada informativa por VIX
salida adaptativa por precio
```

### Variante E — Scale-in

El artículo propone añadir otra posición si llega un segundo spike.

Es especialmente peligroso porque aumenta exposición precisamente durante eventos adversos. Debe incluir:

```text
máximo de entradas
capital total
espaciado
stop de cartera
```

### Variante F — VIX term structure

Añadir:

```text
VIX spot
front future
second future
contango/backwardation
```

Puede aportar información de régimen, pero exige datos nuevos y otro presupuesto de investigación.

### Variante G — Portfolio de índices

```text
SPX / VIX
NDX / VXN
Russell / RVX
```

Debe usarse una especificación común y no recalibrar libremente cada mercado sin control de selección.

---

## 13. Encaje en Market State y Event State

### Market State

```text
vix_level
vix_high
vix_percentile
vix_entry_lookback_high
vix_exit_lookback_low_of_highs
vix_regime
es_contract_state
broad_market_drawdown
```

### Event State de entrada

```text
event_type:
volatility_spike_pivot_high_confirmed

subject_scope:
broad_market

signal_subject:
$VIX.X

execution_subject:
ES
```

### Event State de salida

```text
event_type:
volatility_compression_pivot_low_confirmed
```

### Outcomes

```text
ES forward return
SPY forward return
MFE
MAE
max trade drawdown
time to volatility normalization
cash-session component
overnight component
```

### Uso en small caps

El VIX Pivot es probablemente más útil para TSIS como:

```text
broad_market_context
```

que como estrategia directa.

Puede condicionar:

```text
probabilidad de gap continuation
liquidez
short squeeze risk
halt frequency
mercado risk-on / risk-off
```

Pero una small cap con catalizador puede desacoplarse completamente del SPX.

---

## 14. Veredicto de VIX Pivot

| Cuestión | Decisión |
|---|---|
| ¿Implementar? | **Sí**, como réplica cross-asset y OOS post-2015. |
| ¿Aceptar 12/12 como edge? | **No.** |
| ¿Optimizar thresholds antes del OOS? | **No.** |
| ¿Añadir stop antes de replicar? | **No**, porque cambiaría la estrategia. |
| ¿Operar live sin stop? | **No.** |
| ¿Valor para TSIS? | **Alto como prueba de broad_market_context, calendarios y futures físicos.** |

Siguiente gate propuesto:

```text
VIX-PIVOT-POSTPUBLICATION-OOS-AND-PHYSICAL-FUTURES-GATE
```

---

# Parte III — Ideas adicionales de backtesting contenidas en el issue

## 1. Automatización de objetos visuales

Auto-Trendline muestra una idea general importante:

```text
convertir una herramienta gráfica discrecional
en un objeto computable y falsable
```

Para hacerlo científicamente deben fijarse:

```text
definición de pivot
selección de anchors
momento de confirmación
métrica de pendiente
regla de ruptura
```

## 2. Los dibujos deben convertirse en estados versionados

Una línea borrada del chart no puede desaparecer de la evidencia.

Patrón arquitectónico:

```text
DRAWING OBJECT
↓
VERSIONED INFORMATION OBJECT
↓
DECISION STATE
↓
EVENT
```

## 3. Señal en un instrumento y ejecución en otro

VIX Pivot formaliza:

```text
signal instrument != execution instrument
```

Esto exige contratos separados de:

```text
datos
calendario
latencia
ejecución
```

## 4. Acceso programático a datos secundarios

El artículo indica que el workspace muestra VIX como referencia visual, pero que la estrategia accede programáticamente mediante objetos EasyLanguage y no requiere un chart multi-data.

Lección TSIS:

```text
la visualización no es la fuente contractual
```

## 5. Histeresis de thresholds

Entrada 17 y salida 15 ilustran una técnica útil:

```text
usar umbrales diferentes para entrar y salir
```

Reduce switching, pero introduce dos parámetros y dependencia de régimen.

## 6. 100% de aciertos puede ocultar enorme riesgo

VIX Pivot combina:

```text
12/12 winners
con
$7,400 de drawdown por trade
```

Es una lección clara para no evaluar estrategias únicamente con win rate.

## 7. TS Index frente a maximizar PnL

La revista recomienda no elegir sólo el máximo beneficio y usa TS Index, número mínimo de trades y ausencia de pérdidas.

La intuición es razonable, pero sigue faltando una muestra independiente. Un criterio de selección más sofisticado no elimina el sesgo de selección.

## 8. Re-entries y scaling

Las dos estrategias proponen aumentar entradas:

```text
Auto-Trendline:
re-entry tras whipsaw

VIX Pivot:
scale-in tras segundo spike
```

Ambas ideas incrementan exposición después de un resultado adverso inicial. Deben incluir límites de capital y evaluación de colas.

## 9. VWAP intradía e históricos

La página física 8 vuelve a presentar el producto VWAP de TradeStation Labs:

```text
VWAP actual
reset por sesión
hasta cuatro VWAP históricos
posibles soportes/resistencias
```

Clasificación:

```text
RESEARCH_NOTE
NOT_A_STRATEGY
NO_RULES
NO_BACKTEST
NO_EDGE_EVIDENCE
```

## 10. “Código disponible” no significa “evidencia disponible”

El ZIP contiene `.ELD`, pero no:

```text
source export legible
trade list
strategy properties completas
session template
optimization ranges
```

El paquete ayuda a reproducir dentro de TradeStation, pero no sustituye el contrato científico.

---

# Parte IV — Priorización para TSIS

## 1. Orden recomendado

### Prioridad A — Auto-Trendline como gate de legalidad temporal

Motivos:

```text
127 trades
pivots confirmados con barras posteriores
versionado de líneas
corporate actions
stop diario
descomposición long/short
```

Es un excelente test para:

```text
point-in-time legality
anti-repainting
event sourcing
adjusted signal / raw execution
```

### Prioridad B — VIX Pivot como gate multi-source

Motivos:

```text
VIX externo
ES continuous
futures físicos
alineación de sesiones
verdadero OOS largo desde 2015
```

Su evidencia de edge es más débil, pero su valor arquitectónico es alto.

## 2. Estado respecto de los datos actuales de TSIS

Auto-Trendline requiere una historia diaria gobernada del activo a probar.

VIX Pivot requiere adicionalmente:

```text
VIX daily point-in-time
ES continuous para reproducción
ES physical contracts para validación realista
roll calendar
```

Esas fuentes no deben darse por disponibles hasta quedar vinculadas mediante contratos físicos.

## 3. Artefactos futuros derivados

Cuando se autorice implementación:

```text
SCC_2015_02_AUTO_TRENDLINE_REPLICATION_CONTRACT.md
SCC_2015_02_VIX_PIVOT_REPLICATION_CONTRACT.md
```

Serían artefactos TSIS, no nuevos resúmenes de la revista.

## 4. Qué material adicional haría falta

El ZIP de este issue es suficiente para cerrar la auditoría documental.

Para una réplica exacta todavía sería útil obtener desde una instalación TradeStation:

```text
EasyLanguage exportado como texto
Strategy Properties
MaxBarsBack
session template
optimization ranges
trade list
performance report exportado
```

No es necesario pedirlo ahora. Se solicitaría sólo al abrir el gate físico correspondiente.

---

# Apéndice A — Integridad del paquete

## Archivos relevantes

```text
SCC Issue 2 Feb 2015.pdf
2015-02/Auto-Trendline/TSL AUTO-TRENDLINE.ELD
2015-02/Auto-Trendline/TSL Auto-Trendline.tsw
2015-02/VIX Pivot Strategy/TSL VIX PIVOT.ELD
2015-02/VIX Pivot Strategy/TSL.VIX Pivot.tsw
```

## Tamaños

```text
PDF: 4,010,940 bytes
ZIP: 4,026,342 bytes
Auto-Trendline .ELD: 10,320 bytes
Auto-Trendline .tsw: 49,152 bytes
VIX Pivot .ELD: 12,020 bytes
VIX Pivot .tsw: 24,064 bytes
```

## SHA-256

```text
PDF:
73d9eaa3985e2a2d16aded1becd7f86ba5ab69df2d6a13fd88bf82175f5ac292

ZIP:
0a36fae7c13938534c9ee6962d2728dc7994c81ae0c24edbe37de94b83f05a81

Auto-Trendline .ELD:
6219b1b5bdcd82755347cde3f2e34720901c838251d453fc10fcfcc7a4f7e3fb

Auto-Trendline .tsw:
a2b339097b30c6db3a97f7e2d1a899c603319c19abd529a82037e037f81c9177

VIX Pivot .ELD:
a4219320c571825157ffeb0ca2b9a4f84f497cc3628bc80ff074c7cf3082f0a8

VIX Pivot .tsw:
88418ca9be28de9f8683b83869345655c364012ff66df8258a1570a516c8334b
```

## Limitación del paquete

```text
.tsw:
workspace OLE binario con streams y metadatos parcialmente legibles

.ELD:
contenedor propietario no legible como source EasyLanguage
en este entorno
```

La evidencia máxima requeriría importar los archivos en una versión compatible de TradeStation y exportar:

```text
source code
inputs
properties
trade list
report
session settings
```

---

# Referencias externas

Las referencias siguientes contextualizan la auditoría. No forman parte de la evidencia publicada por la revista.

[TS-SWINGHIGH]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/swinghigh_function_.htm
[TS-SWINGLOW]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/swinglow_function_.htm
[TS-TLANGLE]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/tlangle_function_.htm
[TS-TLVALUE]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/tlvalue_function_.htm
[TS-FUTURES]: https://help.tradestation.com/10_00/eng/tradestationhelp/symbology/futures_symbology.htm
[TS-CONTINUOUS]: https://help.tradestation.com/10_00/eng/tradestationhelp/symbology/custom_continous_futures_symbology.htm
[APPLE-SPLITS]: https://investor.apple.com/faq/default.aspx
[CBOE-VIX]: https://www.cboe.com/tradable-products/volatility-trading/
[CBOE-VIX-DATA]: https://www.cboe.com/tradable_products/vix/vix_historical_data
[LO-TECHNICAL]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=228099
[MOP-TSM]: https://docs.lhpedersen.com/TimeSeriesMomentum.pdf
[STW-DATASNOOP]: https://ideas.repec.org/a/bla/jfinan/v54y1999i5p1647-1691.html
[BEKAERT-VIX]: https://www.nber.org/papers/w18995
[DSR]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551
[PBO]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
[WHITE-RC]: https://www.ssc.wisc.edu/~bhansen/718/White2000.pdf
