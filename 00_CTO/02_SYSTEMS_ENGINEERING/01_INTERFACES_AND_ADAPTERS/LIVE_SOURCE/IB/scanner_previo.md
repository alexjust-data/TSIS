He revisado la documentación oficial actual de la **TWS API Market Scanner**. La conclusión importante es esta:

> **IBKR sí puede filtrar en sus servidores el universo de acciones estadounidenses antes de enviarte resultados.**
>
> Pero el scanner no equivale a un screener profesional completo de small caps. Puede resolver bien los filtros básicos de mercado; otros filtros solo pueden aproximarse mediante un `scanCode`; y muchos filtros importantes —float, noticias, volumen premarket preciso, oferta registrada, dilution, halts, etc.— tendrían que calcularse o incorporarse fuera de IBKR.

Además, el scanner **solo devuelve contratos/símbolos y su ranking**. No devuelve en ese mismo mensaje bid, ask, volumen, L1 o L2. Una vez recibidos los aproximadamente 20 símbolos, vuestro sistema tendría que solicitar por separado los datos de mercado de esos símbolos. IBKR confirma explícitamente esta separación. ([IBKR Campus US][1])

# 1. Cómo funciona realmente

La arquitectura sería:

```text
Universo de acciones estadounidenses
              ↓
Scanner ejecutado por IBKR
              ↓
Filtros y ranking de IBKR
              ↓
Máximo 50 símbolos devueltos
              ↓
Vuestro programa selecciona, por ejemplo, 20
              ↓
reqMktData / reqTickByTickData / reqMktDepth
              ↓
L1, trades o L2 únicamente de esos símbolos
```

Por tanto, **no tenéis que transmitir a vuestra máquina los datos de todas las acciones para filtrarlas localmente**.

IBKR mantiene la suscripción del scanner abierta y envía actualizaciones periódicas hasta que se cancela. Cada scanner devuelve como máximo 50 resultados y pueden mantenerse como máximo 10 scanners de API simultáneos. ([IBKR Campus US][1])

---

# 2. Tres tipos de condiciones en IBKR

Conviene distinguir:

## A. Universo o localización

Define dónde busca:

```text
STK.US
STK.US.MAJOR
STK.NASDAQ
STK.NYSE
STK.AMEX
```

La disponibilidad exacta debe leerse del XML que devuelve vuestra propia sesión de TWS mediante:

```python
reqScannerParameters()
```

## B. `scanCode`

No es exactamente un filtro. Es principalmente la variable con la que IBKR:

* encuentra una categoría;
* ordena los resultados;
* devuelve los primeros 50.

Ejemplos:

```text
TOP_PERC_GAIN
MOST_ACTIVE
HOT_BY_VOLUME
TOP_OPEN_PERC_GAIN
TOP_TRADE_RATE
TOP_VOLUME_RATE
```

## C. Filtros

Son restricciones aplicadas en los servidores de IBKR:

```text
precio mínimo
precio máximo
volumen mínimo
capitalización mínima/máxima
tipo de acción
etc.
```

Los filtros genéricos se envían como `TagValue`. La propia documentación pone como ejemplo:

```python
TagValue("usdMarketCapAbove", "10000")
```

IBKR indica que la lista vigente debe obtenerse mediante `reqScannerParameters()`, porque puede depender de la versión de TWS, el instrumento y la localización. ([IBKR Campus US][1])

---

# 3. Matriz de filtros relevantes para small caps

## Precio actual

| Condición                    | Servidor IBKR | Calidad |
| ---------------------------- | ------------: | ------- |
| Precio mínimo                |            Sí | Directo |
| Precio máximo                |            Sí | Directo |
| Rango, por ejemplo $0,50–$20 |            Sí | Directo |

Campos tradicionales:

```python
subscription.abovePrice = 0.50
subscription.belowPrice = 20.00
```

O equivalentes genéricos presentes en el XML actual.

**Veredicto:** no hace falta recibir datos de todo el mercado para aplicar este criterio.

---

## Volumen acumulado de la sesión

| Condición                      |                     Servidor IBKR | Calidad             |
| ------------------------------ | --------------------------------: | ------------------- |
| Volumen diario por encima de X |                                Sí | Directo             |
| Volumen diario por debajo de X | Depende del filtro XML disponible | Probable            |
| Ranking por volumen            |                                Sí | Mediante `scanCode` |

El objeto clásico `ScannerSubscription` incorpora `AboveVolume`. La documentación histórica de la clase confirma los campos de precio, volumen, capitalización y tipo de acción. ([interactivebrokers.github.io][2])

Ejemplo conceptual:

```python
subscription.aboveVolume = 500_000
```

**Limitación:** hay que determinar con una prueba de mercado qué sesión y qué consolidación exacta usa IBKR para el campo. No conviene asumir sin validación que “volume” significa exactamente lo mismo que el volumen total que muestra DAS, Nasdaq TotalView o vuestro proveedor actual.

---

## Variación porcentual intradía

| Condición                                           |                          Servidor IBKR | Calidad          |
| --------------------------------------------------- | -------------------------------------: | ---------------- |
| Acciones con mayor subida porcentual                |                                     Sí | Ranking          |
| Acciones con mayor caída porcentual                 |                                     Sí | Ranking          |
| Cambio porcentual mínimo exacto, por ejemplo `>20%` | Posible según filtros actuales del XML | Debe verificarse |
| Rango de cambio, por ejemplo 20–100%                |                      Posible según XML | Debe verificarse |

El scanner dispone de códigos como:

```text
TOP_PERC_GAIN
TOP_PERC_LOSE
```

Pero esto significa principalmente:

```text
ordena por porcentaje de cambio
y devuelve los primeros resultados
```

No significa automáticamente:

```text
devuelve todas las acciones con cambio > 20%
```

Para imponer un umbral exacto debe existir en el XML una etiqueta equivalente a cambio porcentual mínimo/máximo compatible con ese scanner.

**Clasificación:** IBKR puede detectar los principales gainers en servidor, pero debéis validar el umbral exacto en vuestra versión.

---

## Gap respecto al cierre anterior

Aquí hay que ser muy cuidadosos.

| Condición                                                    |  Servidor IBKR | Calidad |
| ------------------------------------------------------------ | -------------: | ------- |
| Ranking de mayores gaps en apertura                          |             Sí | Parcial |
| Gap exacto premarket en cualquier momento                    | No garantizado |         |
| Gap calculado con último precio premarket vs cierre anterior |    Mejor local |         |
| Gap a las 04:05, 07:00 o 09:20 ET                            |          Local |         |

IBKR dispone de scanners de apertura como:

```text
TOP_OPEN_PERC_GAIN
TOP_OPEN_PERC_LOSE
```

Esto puede servir para encontrar acciones con apertura fuerte, pero **no debe confundirse con un scanner continuo de gap premarket calculado como**:

```text
(last premarket - previous close) / previous close
```

Antes de la apertura oficial, “open percentage gain” puede no representar exactamente el criterio de vuestro screener discrecional.

Para small caps, yo calcularía localmente:

```python
gap_pct = (reference_premarket_price / previous_close - 1) * 100
```

IBKR podría entregar una primera lista candidata mediante un scanner de ganadores, pero el gap exacto debería confirmarse con L1.

---

## Relative volume o RVOL

| Condición                                            |              Servidor IBKR | Calidad             |
| ---------------------------------------------------- | -------------------------: | ------------------- |
| “Hot by volume”                                      |                         Sí | Ranking propietario |
| Volumen relativo exacto                              | No como fórmula controlada |                     |
| RVOL frente al volumen diario medio                  |                      Local |                     |
| RVOL ajustado por hora del día                       |                      Local |                     |
| RVOL de premarket                                    |                      Local |                     |
| Volumen actual / media de la misma franja de 20 días |                      Local |                     |

IBKR dispone de categorías como:

```text
HOT_BY_VOLUME
MOST_ACTIVE
```

Sin embargo, `HOT_BY_VOLUME` es una métrica definida por IBKR. No os permite controlar necesariamente:

```text
ventana histórica
número de días
ajuste por minuto del día
inclusión de premarket
tratamiento de días sin negociación
fuente de volumen
```

Para investigación seria, usaría:

```python
rvol_daily = volume_today / average_daily_volume_n

rvol_time_adjusted =
    cumulative_volume_today_at_t
    / mean_cumulative_volume_at_t_over_previous_n_sessions
```

**Conclusión:** IBKR puede hacer una preselección server-side basada en actividad anómala, pero no sustituye un RVOL científicamente definido por vosotros.

---

## Average daily volume

| Condición                                  |                             Servidor IBKR | Calidad       |
| ------------------------------------------ | ----------------------------------------: | ------------- |
| Volumen acumulado de hoy                   |                                        Sí | Directo       |
| Volumen medio histórico mínimo             | Posiblemente disponible según filtro/scan | Verificar XML |
| ADV con ventana exacta de 20, 30 o 90 días |                                     Local |               |
| ADV en dólares                             |                       Local o combinación |               |
| ADV excluyendo sesiones anómalas           |                                     Local |               |

Incluso cuando IBKR muestra columnas de volumen medio en TWS, la API no garantiza que todas las columnas de TWS estén disponibles como filtros de scanner. La documentación advierte expresamente que **no todos los parámetros devueltos o disponibles en TWS son utilizables mediante el scanner de la API**. ([interactivebrokers.github.io][3])

---

## Market capitalization

| Condición                           |             Servidor IBKR | Calidad      |
| ----------------------------------- | ------------------------: | ------------ |
| Market cap mínima                   |                        Sí | Directo      |
| Market cap máxima                   |                        Sí | Directo      |
| Microcap por capitalización         |                        Sí | Directo      |
| Capitalización actualizada intradía | Depende de la fuente IBKR | Aproximación |

Campos tradicionales:

```python
subscription.marketCapAbove
subscription.marketCapBelow
```

El sistema genérico moderno usa etiquetas como:

```text
usdMarketCapAbove
usdMarketCapBelow
```

La documentación oficial muestra expresamente `usdMarketCapAbove` como filtro genérico. ([IBKR Campus US][1])

**Atención con las unidades:** el ejemplo oficial utiliza `10000`, pero la unidad o escala efectiva debe confirmarse leyendo la definición del filtro en el XML. No conviene asumir dólares absolutos, miles o millones sin inspeccionar:

```xml
<code>usdMarketCapAbove</code>
<unit>...</unit>
```

---

## Tipo de instrumento: common stock, ADR, ETF, REIT…

| Condición                            |                      Servidor IBKR | Calidad             |
| ------------------------------------ | ---------------------------------: | ------------------- |
| Solo corporaciones/common stocks     |                                 Sí | Directo             |
| Excluir ETF                          |                                 Sí | Directo             |
| Excluir REIT                         |                                 Sí | Directo             |
| Excluir closed-end funds             |                                 Sí | Directo             |
| Incluir/excluir ADR                  |                                 Sí | Directo             |
| Distinguir SPAC de operating company |                  No necesariamente |                     |
| Excluir warrants y units             | En parte mediante tipo contractual | Requiere validación |

El filtro clásico `StockTypeFilter` contempla:

```text
CORP
ADR
ETF
REIT
CEF
```

([interactivebrokers.github.io][2])

Para vuestro caso podría utilizarse:

```python
subscription.stockTypeFilter = "CORP"
```

Esto ayudaría a evitar ETF, REIT y CEF.

Pero para small caps aún habría que estudiar localmente:

```text
SPAC
shell company
unit
right
warrant
preferred stock
foreign ordinary share
ADR
```

No confiaría únicamente en `CORP` para definir un universo limpio de acciones operativas.

---

## Exchange y mercado de cotización

| Condición                                         |                          Servidor IBKR | Calidad                   |
| ------------------------------------------------- | -------------------------------------: | ------------------------- |
| Solo NASDAQ                                       |                                     Sí | Localización              |
| Solo NYSE                                         |                                     Sí | Localización              |
| Solo AMEX/NYSE American                           |                                     Sí | Localización              |
| Todos los mercados principales de EE. UU.         |                                     Sí | Localización              |
| Excluir OTC                                       | Sí, seleccionando mercados principales | Directo                   |
| Filtrar por venue donde se ejecuta cada operación |                                     No | No es función del scanner |

Usaríais una localización de acciones estadounidenses compatible, por ejemplo:

```text
STK.US.MAJOR
```

La lista exacta y vigente debe extraerse de:

```xml
<LocationTree>
```

mediante `reqScannerParameters()`. ([IBKR Campus US][1])

---

## Precio por encima del cierre, open, high o low

| Condición                         |                          Servidor IBKR | Calidad |
| --------------------------------- | -------------------------------------: | ------- |
| Ranking de ganadores              |                                     Sí |         |
| Ranking de nuevos máximos         |                   Sí, según scan codes |         |
| Cerca de máximos/mínimos          | Probablemente mediante scan específico |         |
| Distancia exacta al high of day   |                            Mejor local |         |
| Ruptura exacta del premarket high |                                  Local |         |
| Precio sobre VWAP                 |         No como filtro estándar fiable |         |
| Distancia porcentual a VWAP       |                                  Local |         |

IBKR tiene numerosos `scanCode` de características de precio, pero la lista es dinámica y debe obtenerse de vuestra TWS. El scanner puede encontrar categorías como máximos, mínimos o movimientos, pero no ofrece una lógica arbitraria como:

```text
last > premarket_high
AND
last < premarket_high * 1.03
AND
volume_last_1m > 3 × average
```

Ese tipo de condición pertenece a vuestro motor local.

---

## Trade rate y volume rate

| Condición                                           |                     Servidor IBKR | Calidad |
| --------------------------------------------------- | --------------------------------: | ------- |
| Acciones con mayor tasa de operaciones              |              Sí, mediante scanner |         |
| Acciones con mayor tasa de volumen                  |              Sí, mediante scanner |         |
| Trades por segundo exactos                          | No como dato completo del scanner |         |
| Shares por segundo exactos                          | No como dato completo del scanner |         |
| Umbral sobre ventana propia de 10, 30 o 60 segundos |                             Local |         |

Existen scanners asociados a:

```text
TOP_TRADE_RATE
TOP_VOLUME_RATE
```

Son útiles para detectar acciones que están acelerando.

Pero IBKR solo devuelve el contrato y el ranking, no la serie utilizada para construir ese ranking. La documentación especifica que `scannerData` no incluye bid, ask, last ni volume. ([IBKR Campus US][1])

Por eso no podréis auditar directamente:

```text
qué ventana utiliza IBKR
qué mercados agrega
cómo trata correcciones
cómo trata odd lots
cómo normaliza la tasa
```

Para investigación reproducible, deberíais calcular vuestra propia tasa a partir del feed recibido una vez que el símbolo entra en el universo candidato.

---

## Spread

| Condición                       |                 Servidor IBKR | Calidad |
| ------------------------------- | ----------------------------: | ------- |
| Spread máximo en céntimos       | No como filtro general fiable |         |
| Spread máximo porcentual        |                         Local |         |
| Spread medio durante N segundos |                         Local |         |
| Spread premarket                |                         Local |         |
| Spread por venue                |     Local con datos adecuados |         |

Aunque IBKR conoce bid y ask, el scanner no devuelve esos campos y no se debe asumir que existe un filtro genérico de spread disponible para todos los scanners.

Después de recibir candidatos:

```python
spread_abs = ask - bid
spread_bps = (ask - bid) / midpoint * 10_000
```

---

## Float

| Condición                                     |                                                       Servidor IBKR | Calidad |
| --------------------------------------------- | ------------------------------------------------------------------: | ------- |
| Float máximo                                  |                               No confirmado como filtro API general |         |
| Float mínimo                                  |                                                       No confirmado |         |
| Shares outstanding                            | Puede existir como fundamental, no como scanner operativo universal |         |
| Float ajustado por insiders/restricted shares |                                                             Externo |         |
| Float histórico point-in-time                 |                                                             Externo |         |

Este es uno de los mayores problemas para small caps.

**Market capitalization no equivale a float.**

```text
market cap = precio × shares outstanding

float = acciones teóricamente disponibles para negociación pública
```

Una empresa puede tener:

```text
shares outstanding = 30M
float = 5M
```

IBKR puede filtrar market cap, pero no he encontrado soporte oficial sólido que permita afirmar que el scanner de API ofrece un filtro universal de `floatAbove` o `floatBelow` para acciones estadounidenses.

**Clasificación:** tratad el float como dato externo o local hasta que vuestro XML de TWS demuestre lo contrario.

---

## Shares outstanding

| Condición                 |                          Servidor IBKR scanner | Calidad |
| ------------------------- | ---------------------------------------------: | ------- |
| Shares outstanding máximo |                                 No garantizado |         |
| Shares outstanding actual | Posible mediante datos fundamentales separados |         |
| Histórico point-in-time   |                                             No |         |
| Fully diluted share count |                                             No |         |

Puede que IBKR muestre información fundamental, pero eso no significa que pueda aplicarla como filtro server-side en Market Scanner. IBKR recalca que no todas las características de TWS están disponibles mediante scanners API. ([interactivebrokers.github.io][3])

---

## Noticias

| Condición                                 |               Servidor IBKR scanner | Calidad |
| ----------------------------------------- | ----------------------------------: | ------- |
| Tiene noticias hoy                        | No como filtro universal confirmado |         |
| Noticia publicada hace menos de X minutos |                                  No |         |
| Tipo de catalyst                          |                                  No |         |
| Earnings, FDA, offering, merger, contract |    No como clasificación de scanner |         |
| Sentimiento de la noticia                 |                                  No |         |
| Headline count                            |     Local usando news API/proveedor |         |

IBKR dispone de funcionalidades de noticias separadas, pero eso no convierte el Market Scanner en un screener de catalysts.

El flujo tendría que ser:

```text
IBKR scanner
      ↓
símbolos candidatos
      ↓
request/news provider
      ↓
clasificador local del catalyst
```

---

## Premarket volume

| Condición                              |                                  Servidor IBKR | Calidad |
| -------------------------------------- | ---------------------------------------------: | ------- |
| Volumen total premarket > X            | No como filtro estándar claramente documentado |         |
| Ranking de actividad durante premarket |    Puede aproximarse con scanners de actividad |         |
| Volumen desde las 04:00 ET             |                                          Local |         |
| Volumen desde las 07:00 ET             |                                          Local |         |
| Volumen antes de la primera noticia    |                                          Local |         |

Para vuestro caso, este filtro es crítico.

No asumiría que `AboveVolume` significa volumen exclusivamente premarket. Es más seguro:

1. usar IBKR para obtener candidatos activos;
2. solicitar L1/ticks de esos candidatos;
3. acumular localmente los prints de la sesión extendida.

---

## Premarket high y ruptura del premarket high

| Condición                         |              Servidor IBKR | Calidad |
| --------------------------------- | -------------------------: | ------- |
| Premarket high                    | No como salida del scanner |         |
| Precio dentro del 2% del PM high  |                      Local |         |
| Ruptura del PM high               |                      Local |         |
| Número de intentos contra PM high |                      Local |         |
| Tiempo desde el último test       |                      Local |         |

Requiere construir estado intradía:

```python
premarket_high = max(trade_price between 04:00 and 09:30 ET)
```

---

## Halt, LULD y reanudación

| Condición                 |             Servidor IBKR scanner | Calidad |
| ------------------------- | --------------------------------: | ------- |
| Acción actualmente halted | No confiar como scanner principal |         |
| Reanudación inminente     |                                No |         |
| Halt code                 |          Datos separados/externos |         |
| Historial de halts        |                           Externo |         |
| Número de halts del día   |       Local más fuente de estados |         |

IBKR puede emitir ciertos estados de negociación mediante datos de mercado, pero no convertiría esto en el filtro principal de un scanner de small caps.

---

## Shortable y disponibilidad de préstamo

| Condición                       |            Servidor IBKR scanner | Calidad |
| ------------------------------- | -------------------------------: | ------- |
| Shortable en IBKR               | No como filtro scanner universal |         |
| Número de shares disponibles    |      Datos separados y variables |         |
| Fee rate                        |                  Datos separados |         |
| Easy-to-borrow / hard-to-borrow |                Datos de préstamo |         |
| Disponibilidad en otros brokers |                               No |         |

Esto depende además del inventario de IBKR y no representa el mercado completo de locates.

---

## SSR

| Condición                      |          Servidor IBKR scanner | Calidad |
| ------------------------------ | -----------------------------: | ------- |
| SSR activo                     | No como filtro scanner general |         |
| Caída ≥10% desde cierre previo |    Puede calcularse localmente |         |
| Estado regulatorio oficial     |       Confirmar con feed/venue |         |

---

## Oferta, ATM, warrants y dilution

| Condición                       | Servidor IBKR scanner | Calidad |
| ------------------------------- | --------------------: | ------- |
| Tiene ATM activo                |                    No |         |
| S-1/S-3 efectivo                |                    No |         |
| Offering reciente               |                    No |         |
| Warrants ejercitables           |                    No |         |
| Precio de ejercicio de warrants |                    No |         |
| Shelf capacity                  |                    No |         |
| Cash runway                     |                    No |         |
| Dilution risk                   |                    No |         |

Necesitaríais SEC filings, proveedor especializado o procesamiento propio.

---

## Earnings y eventos corporativos

| Condición                          |                                  Servidor IBKR scanner | Calidad |
| ---------------------------------- | -----------------------------------------------------: | ------- |
| Earnings hoy                       |     Puede existir en herramientas de eventos separadas |         |
| Earnings antes/después del mercado |                   No como scanner universal confirmado |         |
| Biotech catalyst                   |                                                     No |         |
| Split/reverse split reciente       |                                No como filtro estándar |         |
| IPO reciente                       | Puede haber scans especializados, no lógica arbitraria |         |
| Días desde IPO                     |                                                  Local |         |

IBKR ofrece datos de eventos de Wall Street Horizon mediante una suscripción específica, pero es otra API y otro producto; no debe confundirse con Market Scanner. ([interactivebrokers.github.io][4])

---

# 4. Qué filtros ejecutaría yo en IBKR

Para reducir todo el mercado a una primera lista pequeña:

```text
Instrument: STK
Location: mercados principales de EE. UU.
Stock type: CORP
Price: 0.50–20 USD
Volume: por encima de un mínimo
Market cap: por debajo de vuestro límite
Scan code: ganadores / actividad / trade rate / volume rate
Rows: 50
```

Ejemplo conceptual:

```python
scanner = ScannerSubscription()
scanner.instrument = "STK"
scanner.locationCode = "STK.US.MAJOR"
scanner.scanCode = "TOP_PERC_GAIN"
scanner.numberOfRows = 50
scanner.abovePrice = 0.50
scanner.belowPrice = 20.00
scanner.aboveVolume = 100_000
scanner.stockTypeFilter = "CORP"
```

Y filtros genéricos cuando aparezcan como compatibles en vuestro XML:

```python
filters = [
    TagValue("usdMarketCapBelow", "valor_correcto"),
    TagValue("usdMarketCapAbove", "valor_correcto"),
]
```

No copiaría literalmente los nombres o unidades sin leer vuestro `scanner.xml`.

---

# 5. Qué filtros calcularía después localmente

Una vez IBKR os devuelve entre 20 y 50 candidatos, vuestro motor calcularía:

```text
gap premarket exacto
premarket volume
RVOL temporal
float
shares outstanding
spread
premarket high
distancia al premarket high
VWAP
distancia a VWAP
volumen de 1 minuto
aceleración del tape
trades por segundo
shares por segundo
número de halts
SSR
noticias y catalyst
offering/dilution
shortability/fee
estructura del chart diario
ATR
resistencias históricas
```

Eso no requiere suscribirse a miles de símbolos. Podéis calcularlo solo sobre la lista reducida.

---

# 6. Una arquitectura mejor que depender de un único scanner

IBKR solo permite diez scanners API simultáneos y cada uno devuelve como máximo 50 resultados. ([IBKR Campus US][1])

Usaría varios scanners complementarios:

```text
Scanner 1: TOP_PERC_GAIN
Scanner 2: HOT_BY_VOLUME
Scanner 3: TOP_VOLUME_RATE
Scanner 4: TOP_TRADE_RATE
Scanner 5: TOP_OPEN_PERC_GAIN
```

Después:

```text
unión de resultados
        ↓
deduplicación por conId
        ↓
filtros básicos adicionales
        ↓
suscripción temporal a L1
        ↓
cálculo local avanzado
        ↓
selección de aproximadamente 20
        ↓
suscripción L2 solo para esos 20 o para un subconjunto
```

Esto sería más robusto que confiar exclusivamente en `TOP_PERC_GAIN`, porque una acción puede volverse muy activa antes de aparecer entre las principales subidas porcentuales.

---

# 7. Limitación importante con L2

Aunque el scanner os devuelva 20 acciones, eso no significa necesariamente que podáis abrir simultáneamente veinte suscripciones distintas de profundidad de mercado.

Los límites de:

```text
scanner results
Level 1 market data lines
tick-by-tick subscriptions
market depth subscriptions
```

son límites diferentes.

Por tanto, una arquitectura razonable sería:

```text
20 candidatos con L1
5–10 finalistas dinámicos
3 o más L2 simultáneos, según vuestra asignación real
```

El número exacto de L2 disponible depende de las líneas de mercado y de la configuración de la cuenta, no del scanner.

---

# 8. Lo que todavía no puede determinarse solo desde la web

La lista **exacta y vigente, uno por uno**, de filtros compatibles con vuestra cuenta no está publicada como una tabla estática completa. IBKR obliga a obtenerla dinámicamente desde TWS o IB Gateway:

```python
reqScannerParameters()
```

La respuesta es un XML que contiene:

```xml
<InstrumentList>
<LocationTree>
<ScanTypeList>
<FilterList>
```

y, dentro de los filtros:

```xml
<RangeFilter>
    <AbstractField>
        <code>...</code>
```

IBKR indica oficialmente que esos códigos son los que deben usarse como `scannerSubscriptionFilterOptions`. También advierte que no todos los parámetros mostrados o devueltos están disponibles en todos los scanners API. ([IBKR Campus US][1])

Por tanto, la clasificación más rigurosa es:

| Grupo                              | Resultado                  |
| ---------------------------------- | -------------------------- |
| Precio                             | **Sí, servidor**           |
| Volumen actual                     | **Sí, servidor**           |
| Market cap                         | **Sí, servidor**           |
| Exchange/localización              | **Sí, servidor**           |
| Tipo de acción                     | **Sí, servidor**           |
| Top gainers/losers                 | **Sí, ranking servidor**   |
| Actividad, trade rate, volume rate | **Sí, ranking servidor**   |
| Gap exacto premarket               | **Local**                  |
| RVOL definido por vosotros         | **Local**                  |
| Volumen premarket exacto           | **Local**                  |
| Float                              | **Externo/local**          |
| Noticias/catalyst                  | **API separada o externo** |
| Spread                             | **Local**                  |
| PM high/VWAP/patrones              | **Local**                  |
| Halts/LULD                         | **Datos separados/local**  |
| Shortability/fee                   | **Datos separados**        |
| Dilution/offerings/warrants        | **Externo**                |
| L2 de los seleccionados            | **Solicitud separada**     |

# Veredicto para vuestro screener

**Sí podéis utilizar IBKR como primera capa server-side para pasar de todo el mercado estadounidense a una lista pequeña, sin descargar los datos de todas las acciones.**

Pero el resultado no sería aún vuestro screener discrecional final:

```text
IBKR scanner = discovery y prefiltrado

Vuestro sistema = validación y selección avanzada

IBKR L1/L2 = datos de los candidatos seleccionados
```

Para small caps, una estimación realista sería:

```text
IBKR puede ejecutar directamente:
30–50% de la lógica básica del screener

IBKR puede aproximar mediante rankings:
10–20%

Debe calcularse localmente o externamente:
el resto de la lógica especializada
```

La pieza definitiva sería ejecutar `reqScannerParameters()` en vuestra TWS actual y auditar el XML resultante. Sin ese archivo, cualquiera que afirme conocer la lista exacta de filtros disponibles para vuestra versión, cuenta, región e instrumento estaría generalizando más de lo que permite la documentación oficial.

[1]: https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/ "TWS API Documentation | IBKR API | IBKR Campus"
[2]: https://interactivebrokers.github.io/tws-api/classIBApi_1_1ScannerSubscription.html "TWS API v9.72+: ScannerSubscription Class Reference"
[3]: https://interactivebrokers.github.io/tws-api/scanner_parameters.html "TWS API v9.72+: Scanner Parameters"
[4]: https://interactivebrokers.github.io/tws-api/fundamentals.html?utm_source=chatgpt.com "TWS API v9.72+: Fundamental Data"
