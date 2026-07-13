Sí, **TradeStation tiene Scanner y RadarScreen**, pero para tu arquitectura hay una diferencia decisiva:

> **TradeStation Desktop puede filtrar el universo completo, pero la API pública no ofrece un endpoint de screener que reciba filtros y devuelva automáticamente los tickers candidatos.**

Por tanto, para un sistema automático como TSIS, **el scanner tendría que ejecutarse en TradeStation Desktop/EasyLanguage o construirlo vosotros con datos obtenidos mediante API**.

# 1. Scanner de TradeStation Desktop

La aplicación **Scanner** permite seleccionar un universo y aplicar filtros sobre:

* campos de cotización;
* campos fundamentales;
* indicadores técnicos;
* estudios `ShowMe`;
* estudios `PaintBar`;
* distintos intervalos, desde ticks hasta mensual.

TradeStation afirma expresamente que Scanner puede recorrer “todo el universo de símbolos” para encontrar los que cumplen los criterios. También permite encadenar scans: un primer filtro amplio reduce el universo y un segundo scan aplica reglas más costosas. ([help.tradestation.com][1])

Por ejemplo, podrías construir:

```text
Universo:
NASDAQ + NYSE American + NYSE

Filtros iniciales:
Price >= 0.50
Price <= 20
Volume > 100,000
Market cap < 100 M
Gap % > 10 %
```

Y un segundo scan:

```text
Premarket volume > 250,000
Relative volume > 3
Float < 20 M
Intraday range > X
Precio sobre VWAP
```

Los resultados pueden guardarse como una **Custom Symbol List**, y esa lista puede alimentar otro scan posterior. ([help.tradestation.com][2])

## ¿Se ejecuta realmente “en origen”?

No de la misma forma que el scanner server-side de IBKR.

La documentación de TradeStation muestra que Scanner:

1. se ejecuta dentro de TradeStation Desktop;
2. solicita a la TradeStation Data Network los datos necesarios;
3. evalúa los criterios del scan;
4. puede descartar símbolos si la solicitud de datos tarda demasiado.

De hecho, Scanner tiene un parámetro de timeout de entre 10 segundos y 2 minutos, descrito como el tiempo que espera una solicitud de datos antes de descartar el símbolo. Esto indica que no estamos ante una consulta única del tipo:

```text
servidor:
SELECT symbols
WHERE gap > 10
AND market_cap < 100M
```

sino ante un proceso que solicita datos para los símbolos y ejecuta la lógica de Scanner dentro del entorno TradeStation. ([help.tradestation.com][3])

Por tanto:

```text
TradeStation Scanner
≠
screener REST server-side accesible por API
```

# 2. RadarScreen

RadarScreen tampoco descubre necesariamente los símbolos desde cero.

Su funcionamiento normal es:

```text
lista de símbolos conocida
        ↓
cargar datos por símbolo
        ↓
calcular indicadores EasyLanguage
        ↓
ordenar, filtrar y generar alertas
```

Cada fila funciona prácticamente como un pequeño chart, con datos históricos y tiempo real. Puede manejar cientos de símbolos y la documentación histórica señala hasta 2.000 símbolos por ventana. ([help.tradestation.com][4])

RadarScreen es especialmente útil para una segunda fase:

```text
Scanner amplio
    ↓
100–300 candidatos
    ↓
RadarScreen en tiempo real
    ↓
ranking y alertas
    ↓
5–6 símbolos para L2
```

RadarScreen permite hasta cinco expresiones de filtrado por página y admite indicadores personalizados en EasyLanguage. ([help.tradestation.com][5])

Pero nuevamente:

> RadarScreen forma parte de TradeStation Desktop; no es un servicio de scanning expuesto en la API REST.

# 3. Qué ofrece realmente la API pública

La API pública de TradeStation expone servicios de:

* quotes;
* streaming quotes;
* barras históricas;
* market depth;
* market depth aggregates;
* opciones;
* órdenes;
* posiciones y cuentas.

La especificación pública no contiene un endpoint equivalente a:

```http
POST /marketdata/scanner
```

con algo como:

```json
{
  "price_min": 0.5,
  "price_max": 20,
  "market_cap_max": 100000000,
  "gap_percent_min": 10,
  "premarket_volume_min": 200000
}
```

La API está orientada a pedir datos de **símbolos que ya conoces**, no a descubrir automáticamente el universo que cumple tus filtros. ([TradeStation API][6])

Por eso, este flujo no está disponible directamente:

```text
TradeStation REST API
        ↓
envío filtros
        ↓
TradeStation filtra todo el mercado
        ↓
devuelve 20 tickers
        ↓
abro MBP-10
```

# 4. Hot Lists

TradeStation también tiene **Hot Lists** predefinidas:

* mayores subidas;
* mayores bajadas;
* más activas por volumen;
* más activas por número de trades;
* listas separadas por Nasdaq, NYSE y AMEX.

Estas listas históricamente se actualizan cada 30 segundos. ([help.tradestation.com][7])

Pero tienen dos problemas:

1. los criterios son principalmente predefinidos;
2. no he encontrado un endpoint público en la API que entregue esas Hot Lists.

No puedes asumir que desde Python podrás pedir:

```text
top gainers Nasdaq
```

y después combinarlo con tus filtros propios mediante un endpoint oficial.

# 5. Opciones reales para TSIS

## Opción A — Scanner de TradeStation Desktop

Puedes configurar Scanner en Desktop:

```text
Universe:
US stocks

Filtro 1:
0.50 <= price <= 20

Filtro 2:
market cap < 100 M

Filtro 3:
gap >= 10 %

Filtro 4:
premarket volume >= 100,000

Filtro 5:
relative volume >= 2
```

Después:

```text
Scanner
   ↓
Custom Symbol List
   ↓
RadarScreen
   ↓
ranking
   ↓
selección 5–6
   ↓
API MarketDepthAggregates
```

### Ventaja

No tendrías que descargar localmente datos para miles de símbolos mediante la API.

### Problema

La automatización queda encerrada parcialmente en TradeStation Desktop:

* dependencia de Windows;
* dependencia de una sesión activa;
* lógica EasyLanguage;
* difícil integración limpia con Python;
* resultados no expuestos oficialmente mediante REST;
* posible necesidad de exportación, archivos compartidos o un puente local.

Esto puede servir para trading discrecional, pero es menos atractivo como componente reproducible de TSIS.

---

## Opción B — Scanner propio local

Construirías tu propio scanner:

```text
universo diario de símbolos
        ↓
quotes/bars/fundamentals
        ↓
filtros locales
        ↓
ranking
        ↓
5–6 símbolos
        ↓
TradeStation MarketDepthAggregates
```

La ventaja es que tienes:

* lógica versionada;
* timestamps controlados;
* reproducibilidad;
* auditoría;
* mismo código en backtest y live;
* integración directa con TSIS;
* independencia de EasyLanguage.

El problema es obtener eficientemente datos de miles de acciones.

La API de TradeStation no parece diseñada para ejecutar un scanner de mercado completo de baja latencia sobre 5.000–10.000 símbolos. Habría que analizar:

* límite de símbolos por petición de quotes;
* límite de conexiones streaming;
* rate limits;
* coste de pedir barras para todo el universo;
* disponibilidad de fundamentals como float y market cap;
* comportamiento durante premarket.

Por ello, probablemente no usaría TradeStation como proveedor del **universo inicial completo**.

---

## Opción C — Scanner externo + TradeStation sólo para L2

Para TSIS, ésta me parece la arquitectura más sólida:

```text
Polygon / proveedor de referencia
        ↓
scanner de todo el mercado
        ↓
20 candidatos
        ↓
filtros y ranking TSIS
        ↓
5–6 candidatos finales
        ↓
TradeStation MarketDepthAggregates
        ↓
captura MBP-10-like
```

El proveedor inicial sólo necesita entregar:

* trades;
* quotes L1;
* barras de 1 minuto;
* premarket volume;
* gap;
* previous close;
* market cap;
* float;
* exchange;
* halted/status;
* news, cuando proceda.

No necesita entregar profundidad.

Eso permite reservar las conexiones L2 de TradeStation exclusivamente para los cinco o seis candidatos finales.

# 6. Comparación con IBKR Scanner API

Aquí IBKR tiene una ventaja arquitectónica concreta.

IBKR sí expone en la API:

```text
reqScannerSubscription()
```

Puedes enviar criterios como:

* instrumento;
* ubicación/exchange;
* scan code;
* precio mínimo/máximo;
* volumen;
* market cap;
* filtros adicionales disponibles mediante scanner parameters.

IBKR ejecuta el scanner y devuelve un ranking limitado de contratos. No necesitas descargar previamente L1 de todo el universo.

En TradeStation:

```text
Scanner potente
pero dentro de Desktop
```

En IBKR:

```text
Scanner más limitado
pero accesible programáticamente por API
```

Esta diferencia es importante:

| Capacidad                                 |       TradeStation |                           IBKR |
| ----------------------------------------- | -----------------: | -----------------------------: |
| Scanner de universo completo              |        Sí, Desktop |                             Sí |
| Scanner accesible por API                 |  **No encontrado** |                         **Sí** |
| Indicadores personalizados                |       EasyLanguage |                   Muy limitado |
| Filtros técnicos complejos                |        Sí, Desktop | Limitados a filtros soportados |
| Devuelve candidatos a Python directamente |    No oficialmente |                             Sí |
| Puede descubrir tickers antes de pedir L2 | Desktop sí; API no |                             Sí |
| Integración headless                      |               Mala |                          Mejor |
| Reproducibilidad en TSIS                  |    Requiere puente |                    Más directa |

# Veredicto

**TradeStation sí tiene un scanner potente, pero no está integrado en su API pública como servicio server-side.**

Para uso manual o semiautomático:

```text
TradeStation Scanner
→ RadarScreen
→ 5–6 tickers
→ MarketDepthAggregates
```

es completamente viable.

Para una arquitectura automática de ML:

```text
Python
→ enviar filtros a TradeStation
→ recibir candidatos
→ abrir L2
```

**no está soportado directamente**.

La arquitectura que recomendaría es:

```text
IBKR Scanner API o scanner propio con Polygon
        ↓
lista de 20 candidatos
        ↓
ranking TSIS local
        ↓
5–6 símbolos
        ↓
TradeStation MarketDepthAggregates
```

Así aprovecharías cada proveedor para aquello en lo que realmente es mejor:

* **IBKR/Polygon:** descubrimiento del universo.
* **TSIS local:** filtros, ranking y trazabilidad.
* **TradeStation:** profundidad agregada de los símbolos finales.

[1]: https://help.tradestation.com/10_00/eng/tradestationhelp/scanner/about_scanner.htm?utm_source=chatgpt.com "About Scanner"
[2]: https://help.tradestation.com/10_00/eng/tradestationhelp/scanner/advanced_scan_features.htm?utm_source=chatgpt.com "Advanced Scanning Features"
[3]: https://help.tradestation.com/10_00/eng/tradestationhelp/scanner/scan_preferences_advanced.htm?utm_source=chatgpt.com "Scanner Preferences - Advanced"
[4]: https://help.tradestation.com/10_00/eng/tradestationhelp/rs/about_radarscreen.htm?utm_source=chatgpt.com "About RadarScreen"
[5]: https://help.tradestation.com/10_00/eng/tradestationhelp/rs/filter_bar_rs.htm?utm_source=chatgpt.com "Filter Bar in RadarScreen"
[6]: https://api.tradestation.com/docs/?utm_source=chatgpt.com "TradeStation API Docs"
[7]: https://help.tradestation.com/09_01/tradestationhelp/data_network/about_ts_data_network.htm?utm_source=chatgpt.com "About the TradeStation Data Network"
