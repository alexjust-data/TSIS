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

---

# 9. Capacidad despues del scanner y coste IBKR

La respuesta practica es:

```text
Scanner IBKR:
devuelve candidatos/ranking, normalmente top 50 por scan en TWS.

L1 streaming despues del scanner:
100 simbolos simultaneos minimo por usuario/cuenta, compartidos entre TWS y API.

Tick-by-tick:
5% de las lineas de mercado. Con 100 lineas = 5 simbolos tick-by-tick.

L2 / market depth:
minimo 3 simbolos simultaneos con la asignacion base de 100 lineas.
Escala aproximadamente a 1 simbolo L2 por cada 100 lineas de mercado,
con maximo operativo publicado de 60.
```

Por tanto, frente a una API que limita a 100 tickers, **IBKR tambien empieza con 100 lineas simultaneas de L1**, no con "todo el mercado" en streaming. La diferencia importante es que el scanner de IBKR filtra en servidor y solo despues se consumen lineas L1/L2 para los candidatos seleccionados.

Ejemplo operativo:

```text
5 scanners x hasta 50 resultados = hasta 250 filas brutas
deduplicacion por conId
20-100 candidatos con L1, segun lineas disponibles
5 candidatos maximos con tick-by-tick con asignacion base
3 candidatos maximos con L2 con asignacion base
```

Si TWS ya muestra 40 simbolos en watchlists, quedan aproximadamente:

```text
100 lineas base - 40 usadas en TWS = 60 lineas para la API
```

## Como aumentar capacidad

IBKR asigna siempre un minimo de 100 lineas. Despues del primer mes, la asignacion puede subir segun:

```text
max(
    comisiones_mensuales_USD / 8,
    equity_USD * 100 / 1_000_000,
    100
)
```

Tambien existen **Quote Booster packs**. Cada pack cuesta 30 USD/mes y anade 100 lineas L1. La parte importante es no sumar L2 como:

```text
3 L2 base + numero_de_boosters
```

IBKR publica una tabla separada de **Specialized Market Data Lines**. En esa tabla, tick-by-tick escala aproximadamente al 5% de las lineas totales, pero market depth no sube con los tres primeros boosters:

```text
100 lineas:      5 tick-by-tick, 3 depth
101-200 lineas: 10 tick-by-tick, 3 depth
201-300 lineas: 15 tick-by-tick, 3 depth
301-400 lineas: 20 tick-by-tick, 3 depth
401-500 lineas: 25 tick-by-tick, 4 depth
501-600 lineas: 30 tick-by-tick, 5 depth
1001-1100 lineas: 55 tick-by-tick, 10 depth
```

Por tanto, con 3 Quote Boosters:

```text
100 base + 300 boosters = 400 lineas
400 lineas = 20 tick-by-tick y 3 depth, no 6 depth
```

Coste solo de capacidad:

| Configuracion | L1 aprox. | Tick-by-tick aprox. | L2/depth aprox. | Coste extra capacidad |
| --- | ---: | ---: | ---: | ---: |
| Base IBKR | 100 | 5 | 3 | 0 USD/mes |
| +1 Quote Booster | 200 | 10 | 3 | 30 USD/mes |
| +3 Quote Boosters | 400 | 20 | 3 | 90 USD/mes |
| +4 Quote Boosters | 500 | 25 | 4 | 120 USD/mes |
| +5 Quote Boosters | 600 | 30 | 5 | 150 USD/mes |
| +10 Quote Boosters | 1100 | 55 | 10 | 300 USD/mes |

Los Quote Boosters solo aumentan capacidad. No sustituyen las suscripciones de datos de mercado. Para L2/depth ademas hay que tener contratado el paquete de profundidad correspondiente del mercado.

## Coste de datos de mercado US equities

El scanner/API no parece tener una tarifa separada propia; el coste real viene de las suscripciones de market data. IBKR indica que las suscripciones se pagan por mes calendario, no se prorratean, y tras suscribirse no hay cargos adicionales de uso salvo snapshots.

Para acciones estadounidenses, IBKR incluye gratis datos real-time no consolidados de Cboe One e IEX. Eso no es NBBO consolidado. Para un screener serio de small caps, conviene presupuestar datos consolidados de acciones US.

Coste mensual orientativo IBKR, segun tabla oficial vigente consultada el 2026-07-11:

| Datos | Non-Pro | Pro |
| --- | ---: | ---: |
| NYSE Network A L1 | 1.50 USD/mes | 45.00 USD/mes |
| NYSE American/BATS/ARCA/IEX/Regional Network B L1 | 1.50 USD/mes | 25.00 USD/mes |
| NASDAQ Network C L1 | 1.50 USD/mes | 25.00 USD/mes |
| Total L1 US equities A+B+C | **4.50 USD/mes** | **95.00 USD/mes** |
| US Securities Snapshot and Futures Value Bundle | 10.00 USD/mes, waiver por actividad | 10.00 USD/mes, waiver por actividad |
| US Equity and Options Add-On Streaming Bundle | 4.50 USD/mes | 125.00 USD/mes |

Para L2/depth hay que sumar paquetes de profundidad por mercado. Ejemplos relevantes:

| L2/depth | Non-Pro | Pro |
| --- | ---: | ---: |
| NASDAQ TotalView-OpenView | 16.50 USD/mes | 90.00 USD/mes |
| NASDAQ TotalView-OpenView EDS API/off-platform | 1.00 USD/mes | 10.00 USD/mes |
| NYSE ArcaBook depth | 11.00 USD/mes | 65.00 USD/mes |
| NYSE OpenBook depth | 25.00 USD/mes | 64.50 USD/mes |

Para NASDAQ depth o tick data via API, IBKR especifica que se necesita L1 US completo y tambien NASDAQ TotalView-OpenView + NASDAQ TotalView-OpenView EDS.

## Veredicto numerico

Para vuestro caso:

```text
Minimo razonable:
IBKR base + L1 US equities
= 100 simbolos L1 simultaneos
= 5 tick-by-tick
= 3 L2
= 4.50 USD/mes non-pro para L1 US equities
```

Configuracion mas realista para operar candidatos small caps:

```text
IBKR + L1 US equities + 3 Quote Boosters
= unas 400 lineas L1
= unos 20 tick-by-tick
= 3 L2
= 4.50 USD/mes de L1 non-pro + 90 USD/mes boosters
= 94.50 USD/mes antes de L2/depth/news
```

Si necesitais L2 NASDAQ por API:

```text
L1 US equities non-pro: 4.50 USD/mes
NASDAQ TotalView-OpenView: 16.50 USD/mes
NASDAQ TotalView-OpenView EDS: 1.00 USD/mes
Total datos NASDAQ L1+L2 API: 22.00 USD/mes
```

Esto no cambia el limite de cuantos L2 simultaneos podeis abrir; solo da derecho al dato. La simultaneidad L2 sigue dependiendo de las lineas/boosters.

Conclusion: IBKR no debe modelarse como "me da miles de tickers live despues del scanner". Debe modelarse como:

```text
Scanner server-side para descubrir candidatos
+ 100 lineas L1 base como minimo
+ capacidad ampliable con comisiones/equity/Quote Boosters
+ L2 muy limitado y reservado para finalistas
```


---

# 10. Comparacion con Databento Standard

Esta comparacion debe hacerse **solo contra Databento Standard**, porque es el plan que entra en presupuesto. No debe mezclarse con Plus ni Unlimited:

| Plan Databento | Precio oficial | Lectura para este proyecto |
| --- | ---: | --- |
| Standard | 179 USD/mes | Opcion viable a evaluar |
| Plus | 1.500 USD/mes de license fees, contrato anual | Fuera de presupuesto |
| Unlimited | 4.000 USD/mes de license fees, contrato anual | Fuera de presupuesto |

## Que incluye Standard segun precio actual

Para Databento US Equities, la tabla oficial de precios indica que Standard incluye:

```text
179 USD/mes
Live data
No license fees
16+ anos de historico L0
1 ano de historico L1
1 mes de historico L2/L3
Pay-as-you-go para mas historico
```

Traduccion operativa:

| Necesidad | Standard sirve | Comentario |
| --- | ---: | --- |
| Live feed para scanner local | Si | Mucho mas apto que IBKR para universo amplio |
| Historico OHLCV largo, L0 | Si | La pagina indica 16+ anos |
| Historico L1 largo, varios anos | No incluido | Standard solo incluye 1 ano; mas historico seria PAYG |
| Historico L2/L3 largo | No incluido | Standard solo incluye 1 mes; Plus/Unlimited no entran en presupuesto |
| Backtest de small caps con barras 1m/1d | Probablemente si | Si basta L0/OHLCV |
| Backtest de tape/tick/BBO 2019-2025 | No como base incluida | Habra coste extra historico |

## Diferencia estructural contra IBKR

```text
IBKR:
filtra en servidor con scanner
+ devuelve top candidatos
+ consume lineas solo para seleccionados
+ coste bajo
- no da universo live completo a la API con la cuenta base
- 100 lineas L1 base, tick-by-tick y L2 muy limitados

Databento Standard:
feed amplio para construir scanner local
+ live data incluido en Standard
+ API permite ALL_SYMBOLS/None para seleccionar todos los simbolos de un dataset
+ historico y live usan los mismos esquemas
+ mejor para reproducibilidad investigadora
- coste minimo 179 USD/mes
- no trae scanner server-side estilo IBKR
- requiere CPU, red, storage y logica local para filtrar todo el universo
```

La diferencia no es solo precio. Es arquitectura:

```text
IBKR = discovery server-side barato + ejecucion broker + candidatos limitados
Databento Standard = feed para discovery local + investigacion reproducible
```

## Capacidad live

IBKR tiene una restriccion muy concreta:

```text
100 lineas L1 base
5 tick-by-tick con base de 100 lineas
3 L2 con base de 100 lineas
```

Databento no debe modelarse como "100 tickers". En la API live, el parametro `symbols` puede recibir `ALL_SYMBOLS` o `None`, lo que selecciona todos los simbolos del dataset. Eso cambia el diseno: con Databento se puede intentar construir un scanner local de universo amplio, pero el limite real pasa a ser:

```text
throughput de mensajes
ancho de banda
CPU de decodificacion
memoria/estado intradia
almacenamiento si se persiste el feed
calidad de filtros propios
```

Para small caps, eso es una ventaja fuerte: gap, premarket volume, RVOL temporal, aceleracion de volumen, spreads y rupturas de PM high pueden calcularse de forma uniforme, sin depender de que IBKR incluya el simbolo en un top 50.

## Cuidado con que dataset significa que dato

Databento Standard no significa automaticamente "NBBO SIP completo historico ilimitado" ni "L2 ilimitado historico".

Ejemplos relevantes:

| Dataset / producto | Lectura tecnica |
| --- | --- |
| Databento US Equities Mini (`EQUS.MINI`) | Dataset top-of-book derivado/agregado; BBO unico agregado por instrumento; no identifica venues originales |
| Databento US Equities Summary (`EQUS.SUMMARY`) | Volumen consolidado y estadisticas/end-of-day; solo `ohlcv-1d`, `statistics`, `definition` |
| Nasdaq Basic with NLS Plus (`XNAS.BASIC`) | Trades de varios venues Nasdaq/TRF, pero quotes solo Nasdaq; no equivale por si solo a todo el NBBO SIP |

Por tanto, antes de cerrar arquitectura hay que decidir:

```text
queremos scanner local barato y amplio: EQUS.MINI / Standard puede ser suficiente
queremos NBBO consolidado regulatorio exacto: revisar dataset/licencia exacta
queremos L2 profundo historico multianual: Standard no basta sin PAYG o plan superior
```

## Comparacion de coste mensual viable

| Configuracion | Coste mensual aproximado | Que compra realmente |
| --- | ---: | --- |
| IBKR L1 US equities non-pro | 4.50 USD | Datos L1 US, pero solo 100 lineas base |
| IBKR + 3 Quote Boosters | 94.50 USD | Unas 400 lineas L1, 20 tick-by-tick, 3 L2 |
| Databento Standard | 179.00 USD | Live feed y paquete historico incluido, sin license fees separados en Standard |
| IBKR + 10 Quote Boosters | 304.50 USD | Unas 1100 lineas L1, pero sigue siendo arquitectura por lineas |

Conclusion de coste:

```text
IBKR es mas barato si solo necesitamos candidatos y ejecucion.
Databento Standard es mas caro que IBKR + 3 boosters, pero cambia el problema:
permite scanner local amplio y mejor investigacion historico/live.
```

## Decision recomendada

Para este sistema de small caps, la decision mas limpia seria:

```text
Databento Standard = fuente primaria de discovery local e investigacion
IBKR = broker, ejecucion, backup, y posible scanner secundario barato
```

No usaria Databento Plus/Unlimited para la decision actual porque contaminan el analisis de precio. Standard es el unico Databento comparable con vuestro presupuesto.

Fuentes Databento principales: [8], [9], [10], [11], [12].
Fuentes IBKR principales: [5], [6], [7].

[1]: https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/ "TWS API Documentation | IBKR API | IBKR Campus"
[2]: https://interactivebrokers.github.io/tws-api/classIBApi_1_1ScannerSubscription.html "TWS API v9.72+: ScannerSubscription Class Reference"
[3]: https://interactivebrokers.github.io/tws-api/scanner_parameters.html "TWS API v9.72+: Scanner Parameters"
[4]: https://interactivebrokers.github.io/tws-api/fundamentals.html?utm_source=chatgpt.com "TWS API v9.72+: Fundamental Data"
[5]: https://ibkrguides.com/traderworkstation/create-a-market-scanner.htm "Advanced Market Scanner | Trader Workstation User Guide"
[6]: https://ibkrcampus.com/campus/ibkr-api-page/market-data-subscriptions/ "Market Data Subscriptions | IBKR API | IBKR Campus"
[7]: https://www.interactivebrokers.com/en/pricing/market-data-pricing.php "Market Data Pricing | Interactive Brokers"
[8]: https://databento.com/pricing "Pricing | Databento"
[9]: https://databento.com/docs/api-reference-live/basics/connection-limits "Connection limits | Databento Live API"
[10]: https://databento.com/docs/venues-and-datasets/equs-mini "Databento US Equities Mini | Databento APIs"
[11]: https://databento.com/docs/venues-and-datasets/equs-summary "Databento US Equities Summary | Databento APIs"
[12]: https://databento.com/docs/venues-and-datasets/xnas-basic "Nasdaq Basic with NLS Plus | Databento APIs"