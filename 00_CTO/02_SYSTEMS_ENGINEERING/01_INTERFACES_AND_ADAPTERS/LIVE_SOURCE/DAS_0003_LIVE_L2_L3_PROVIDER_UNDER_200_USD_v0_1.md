# DAS 0003 - Live L2/L3 Provider Under 200 USD

Fecha: 2026-07-09
Destino: `DAS_0003` / realtime first impulse detection
Presupuesto maximo: 200 USD/mes

## Respuesta corta

Con presupuesto de 200 USD/mes, la opcion viable encontrada para capturar **live L2 real** en US equities es **Interactive Brokers (IBKR)** usando TWS o IB Gateway API + suscripciones de market data depth-of-book.

No queda demostrado, con fuentes publicas y precio cerrado, que exista una opcion de **live L3/MBO completo** de US equities por menos de 200 USD/mes. Para ese presupuesto, la decision tecnica honesta es disenar la captura como **L2/MBP real**, no como L3/MBO real.

Hay un candidato adicional que merece validacion directa: **Futu/Moomoo OpenD**. Su documentacion muestra order book realtime para US stocks y una estructura `OrderBookDetail` con `orderID`, marcada como unica para `HK SF, US LV2 market`. Esto puede ser L3-like, pero no lo doy por cerrado hasta probar entitlement real, precio, pais/cuenta y si el callback entrega eventos incrementales suficientes para entrenar modelos grandes.

## Opcion principal: Interactive Brokers

IBKR es la opcion mas realista bajo 200 USD/mes para capturar L2 en vivo.

Capacidades confirmadas:

- API: TWS API / IB Gateway.
- Metodo: `reqMktDepth` / `reqMarketDepth`.
- Callbacks: `updateMktDepth` y `updateMktDepthL2`.
- Campos utiles: posicion/nivel, operacion insert/update/remove, lado bid/ask, precio, size, exchange/market maker cuando aplique.
- Puede usarse desde API, no solo desde pantalla.
- Permite Smart Depth/agregacion segun entitlements, pero no sustituye un feed raw directo completo.

Limitaciones:

- Es **L2 / MBP**, no L3/MBO.
- No entrega order IDs NASDAQ ITCH-style para reconstruir el libro orden por orden.
- La concurrencia de simbolos depth esta limitada.
- El default para deep book es 3 simbolos simultaneos. Cada Quote Booster cuesta 30 USD/mes y suma 1 simbolo depth simultaneo adicional, ademas de 100 lineas Level I.

Estimacion de coste mensual non-professional:

| Item | Precio aprox. |
| --- | ---: |
| NASDAQ TotalView-OpenView L1/L2 | 16.50 USD |
| NYSE OpenBook L2 | 25.00 USD |
| NYSE ArcaBook L1/L2 | 11.00 USD |
| Cboe BZX L1/L2 | 8.00 USD |
| Network A/B/C L1/NBBO basico | 4.50 USD |
| **Base estimada** | **65.00 USD/mes** |

Ejemplos dentro de presupuesto:

| Configuracion | Simbolos depth simultaneos aprox. | Coste aprox. |
| --- | ---: | ---: |
| Base sin boosters | 3 | 65 USD/mes |
| Base + 3 boosters | 6 | 155 USD/mes |
| Base + 4 boosters | 7 | 185 USD/mes |

Notas:

- IBKR exige saldo minimo para activar market data; para cuentas individuales la pagina de IBKR lista 500 USD de minimum equity balance.
- Algunas fees pueden estar sujetas a waivers por comisiones o reglas de exchange. No conviene depender de eso para presupuesto.
- Para small caps, conviene activar como minimo NASDAQ TotalView, NYSE OpenBook, ArcaBook, Cboe BZX y L1 consolidated/network donde proceda.

## Databento Standard

Databento Standard no cierra el requisito de live L2/L3 para este caso.

Lo que si aporta:

- Plan Standard: 179 USD/mes.
- Live data incluido, pero en US equities Standard live esta limitado a la cobertura visible en la tabla de planes: Databento US Equities Mini.
- En la tabla de live data mostrada localmente, Standard incluye L0/L1 como OHLCV, definitions, statistics, status, MBP-1, TBBO, BBO y trades.
- Standard no incluye live `MBP-10`, `MBO` ni `Imbalance`.
- Standard incluye 1 mes de historia L2/L3; mas historia es pay-as-you-go.

Conclusion:

- Sirve para prototipo L1/trades y para algo de historia.
- No sirve como fuente live L2/L3 completa para `DAS_0003`.
- Para live L2/L3 real en Databento habria que subir a Plus/Unlimited o licencias equivalentes, fuera del presupuesto: Plus muestra 1,500 USD/mes de license fees y Unlimited 4,000 USD/mes.

Referencia local de la tabla revisada:

`C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\databento\live_data.png`

## IEX

IEX tiene feeds interesantes para microestructura, pero queda fuera de presupuesto:

- TOPS real-time: 500 USD/mes.
- DEEP real-time: 2,500 USD/mes.
- DEEP+ real-time: 3,500 USD/mes.

Conclusion:

- No cumple el limite de 200 USD/mes.
- Puede servir como referencia teorica o futura alternativa institucional, pero no como proveedor operativo actual.

## Futu/Moomoo OpenD

Candidato a validar, no cerrado.

Puntos a favor:

- La API `get_order_book` devuelve order book realtime para US stocks durante la sesion.
- Requiere suscripcion previa.
- La estructura `OrderBook` incluye precio, volumen, numero de ordenes y `detailList`.
- `OrderBookDetail` incluye `orderID` y volumen.
- La documentacion marca `detailList` como unico para `HK SF, US LV2 market`.

Riesgos / dudas:

- No queda cerrado el precio real bajo 200 USD/mes para cuenta USA/Espana/entitlement concreto.
- No queda cerrado si OpenD permite uso estable de API para captura continua a escala.
- Hay que probar si el callback realtime entrega eventos incrementales suficientes o solo snapshots/updates agregados.
- Aunque tenga `orderID`, puede no ser equivalente a un raw ITCH MBO feed completo.

Validacion minima necesaria:

1. Abrir cuenta o usar cuenta existente con market data US LV2 activo.
2. Ejecutar OpenD localmente.
3. Suscribirse a `US.AAPL` y small caps reales.
4. Llamar `get_order_book(code, num=...)`.
5. Activar realtime order book callback.
6. Confirmar si `detailList` llega poblado con `orderID` para US symbols.
7. Medir frecuencia, latencia, limites, throttling y estabilidad 1 sesion completa.
8. Confirmar terms/licencia para almacenamiento y entrenamiento interno.

Si Futu/Moomoo pasa esas pruebas y el precio real esta por debajo de 200 USD/mes, podria convertirse en la unica via L3-like barata. Hasta entonces, no se debe documentar como fuente L3 confirmada.

## Decision recomendada para DAS 0003

Implementar dos caminos:

1. **Camino operativo inmediato: IBKR L2/MBP live**
   - Capturar `market_depth_l2_ibkr`.
   - Guardar deltas/snapshots con timestamp local y provider timestamp cuando exista.
   - Entrenar features de imbalance, depth pressure, spread, top-of-book, queue pressure aproximada, cancel/update intensity proxy.
   - Etiquetarlo claramente como L2/MBP, no L3/MBO.

2. **Spike de validacion: Futu/Moomoo OpenD**
   - Objetivo: confirmar si hay L3-like barato con order IDs en US LV2.
   - No bloquear el pipeline principal por esta validacion.
   - Si funciona, crear un segundo adapter `market_depth_l3like_futu`.

No basar `DAS_0003` en un requisito duro de L3/MBO completo mientras el presupuesto siga en 200 USD/mes. El requisito correcto para produccion bajo este presupuesto es:

> Live L2/MBP real obligatorio; L3/MBO completo opcional si aparece proveedor verificable bajo presupuesto.

## Fuentes revisadas

- IBKR Market Data Pricing: https://www.interactivebrokers.com/en/pricing/market-data-pricing.php
- IBKR TWS API Market Depth: https://interactivebrokers.github.io/tws-api/market_depth.html
- Databento Pricing: https://databento.com/pricing#us-equities
- IEX Fee Schedule: https://www.iex.io/resources/trading/fee-schedule
- Futu OpenD Get Real-time Order Book: https://openapi.futunn.com/futu-api-doc/en/quote/get-order-book.html
- Futu OpenD Quotation Definitions / OrderBook: https://openapi.futunn.com/futu-api-doc/en/quote/quote.html

