Sí. Vamos a tratar esta imagen como una **pieza de evidencia arquitectónica**, no solo como una captura bonita.

Mi conclusión general, antes de entrar por zonas, es esta:

> La imagen parece mostrar una aplicación de escritorio propia, escrita en Python con Qt/PySide, que funciona como panel de control de un runtime algorítmico conectado simultáneamente a DAS para ejecución y a Massive para datos de mercado.

No parece una interfaz nativa de DAS. Tampoco parece una web app clásica.

# 1. Tipo de aplicación

En la parte derecha se ve código Python con imports que parecen incluir componentes de `PySide6`, por ejemplo elementos equivalentes a:

```python
from PySide6.QtCore import ...
from PySide6.QtWidgets import ...
```

También se distinguen nombres como:

```text
Dashboard
AsyncBridge
ConsoleWidget
StatusCard
StrategyList
```

Eso apunta con bastante fuerza a:

```text
Aplicación de escritorio Python
+
PySide6 / Qt
```

No a:

```text
React
Angular
Django web
Streamlit
```

Además, la ventana tiene barra de título propia de Windows:

```text
DAS Trading Framework - Control Panel
```

Por tanto, la hipótesis más probable es:

```text
Python backend
+
GUI desktop Qt
+
procesamiento asíncrono
```

## ¿Por qué usar PySide6?

Porque permite:

* interfaz gráfica local;
* integración muy directa con Python;
* timers;
* señales y slots;
* múltiples widgets;
* tablas complejas;
* actualización periódica;
* procesos o hilos en segundo plano;
* poca latencia entre backend e interfaz.

Para un framework de trading local tiene bastante sentido.

---

# 2. Nombre: “DAS Trading Framework”

Esto parece una marca interna puesta por Sersan.

No significa necesariamente que DAS les proporcione el framework.

Más probablemente significa:

```text
Framework de Sersan
diseñado alrededor de DAS
```

La evidencia:

* aparecen configuraciones propias;
* proveedor Massive separado;
* scanner propio;
* watchdog;
* orquestador;
* GUI escrita en Python;
* consola de aplicación;
* estrategias cargables.

DAS probablemente es solo:

```text
broker/execution gateway
```

La aplicación completa parece de ellos.

---

# 3. Barra de navegación

En la zona superior aparecen:

```text
Dashboard
Operativa
Símbolos
Mercado
Deslizamientos
Configuración
Logs
```

Esto permite inferir varios módulos internos.

## Dashboard

Estado global del runtime:

* conexiones;
* proveedor;
* estrategias;
* watchdog;
* buffer;
* scanner;
* consola.

## Operativa

Por las otras imágenes, contiene:

* cuenta;
* ejecuciones;
* posiciones;
* locates;
* análisis;
* órdenes;
* trades;
* trazabilidad.

## Símbolos

Probablemente:

* universo actual;
* símbolos operables;
* candidatos;
* bloqueados;
* datos por ticker;
* estado de suscripción;
* disponibilidad de short.

## Mercado

Podría contener:

* estado de sesión;
* reloj de mercado;
* premarket;
* open;
* after-hours;
* halts;
* estado del feed;
* posiblemente datos generales.

## Deslizamientos

Esta pestaña es muy reveladora.

Probablemente permite comparar:

```text
precio esperado
vs.
precio real ejecutado
```

y estudiar:

* slippage por ticker;
* slippage por ruta;
* slippage por estrategia;
* slippage por hora;
* slippage por liquidez;
* diferencia backtest-real.

Esto indica que el framework no solo ejecuta. También hace **post-trade attribution**.

## Configuración

En otras imágenes vimos JSON5. Por tanto, probablemente permite editar:

* estrategias;
* scanner;
* locates;
* orquestador;
* logs;
* notificaciones;
* GUI.

## Logs

Registro técnico:

* errores;
* warnings;
* reconexiones;
* mensajes DAS;
* mensajes Massive;
* órdenes;
* fills;
* watchdog;
* excepciones.

# 4. Tarjeta “Conexión DAS”

Se ve:

```text
Conectado
localhost:9910
```

Esto es muy significativo.

## Qué implica `localhost`

La GUI no parece conectarse directamente a servidores remotos del broker desde cada pantalla.

Probablemente existe un proceso local:

```text
DAS API / DAS Trader Pro
    ↓
servicio local
    ↓
localhost:9910
    ↓
framework Python
```

Puede ser:

* un socket local;
* TCP;
* una API local de DAS;
* un bridge propio;
* un proceso intermediario.

La arquitectura probable:

```text
DAS Trader Pro
    ↓
DAS API local
    ↓
DAS Adapter
    ↓
Framework
```

## Por qué es importante

Porque separan:

```text
interfaz
```

de:

```text
conexión de ejecución
```

Si la GUI se cierra, quizá el runtime puede seguir activo, dependiendo de cómo esté implementado.

No podemos asegurarlo, pero arquitectónicamente tendría sentido.

# 5. “Data Provider: MASSIVE — LIVE”

Esta parte confirma casi con seguridad:

```text
Massive = Polygon/Massive
```

No es el nombre de un scanner interno.

La palabra `LIVE` indica que están consumiendo datos en tiempo real.

Separación probable:

```text
Massive:
datos de mercado
scanner
quotes
trades
bars
```

```text
DAS:
órdenes
cuenta
locates
fills
posiciones
```

Este diseño evita depender del feed de DAS para toda la investigación o el scanner.

# 6. “Buffer Datos — Vacío — 0 barras | 0.0 MB”

Esta tarjeta es una pista muy valiosa.

Parece existir un **buffer temporal en memoria** o posiblemente en disco para almacenar barras.

Campos:

```text
Vacío
0 barras
0.0 MB
```

## Qué puede ser el buffer

Varias posibilidades:

### A. Buffer de datos intradía reciente

```text
Massive WebSocket
↓
barra/trade/quote
↓
buffer en memoria
↓
estrategias
```

### B. Precarga histórica

Antes de arrancar una estrategia pueden descargar, por ejemplo:

```text
últimas 100 barras
```

para inicializar indicadores.

### C. Buffer de recuperación

Si se desconecta una estrategia o la GUI, pueden conservar datos temporales.

### D. Cache compartida entre estrategias

En lugar de que cada estrategia descargue el mismo ticker:

```text
un feed
↓
un buffer
↓
varias estrategias
```

Esto sería muy razonable.

## Por qué aparece vacío

La aplicación está:

```text
Escaneando PreMarket
```

pero no hay estrategias cargadas.

Tal vez aún no ha comenzado la suscripción profunda a barras de los operables.

Eso apoya la idea del embudo:

```text
scanner global barato
↓
símbolos operables
↓
cargar buffer detallado
↓
iniciar estrategias
```

# 7. “Estrategias 0/0 — Sin iniciar”

Puede significar:

```text
estrategias activas / estrategias configuradas
```

o:

```text
estrategias iniciadas / estrategias elegibles
```

Al mostrar `0/0`, parece no haber ninguna cargada.

Eso encaja con el panel inferior:

```text
Sin estrategias cargadas
```

## Arquitectura inferida

Las estrategias parecen ser plugins o clases configurables.

Posiblemente:

```text
estrategias.json5
↓
cargador de estrategias
↓
instancias Strategy
↓
runtime
```

No parece que toda la aplicación sea una única estrategia hardcodeada.

# 8. Watchdog activo

Se ve:

```text
Watchdog
Activo
Monitoreando
```

Este es uno de los elementos más profesionales de la captura.

Un watchdog puede comprobar:

* conexión DAS viva;
* feed Massive vivo;
* último mensaje recibido;
* GUI viva;
* estrategias respondiendo;
* memoria;
* CPU;
* bloqueos;
* heartbeats;
* latencia;
* colas acumuladas;
* hilos muertos.

## Posible comportamiento

```text
cada X segundos:
comprobar heartbeat
comprobar feed
comprobar DAS
comprobar estrategias
```

Si falla:

```text
reintentar
reiniciar componente
detener trading
enviar alerta
```

En otra configuración vimos campos como:

```text
intervalo_heartbeat_segundos
timeout_lectura_segundos
reintento_inicial_segundos
reintento_maximo_segundos
max_reintentos
```

Eso encaja perfectamente con esta tarjeta.

# 9. Botones de control

Aparecen:

```text
INICIAR TRADING
PAUSAR
REINICIAR
DETENER
```

No son cuatro botones equivalentes. Probablemente representan estados diferentes del runtime.

## Iniciar Trading

Podría:

* activar estrategias;
* permitir nuevas órdenes;
* iniciar scanner operativo;
* conectar módulos;
* comenzar timers;
* habilitar ejecución.

## Pausar

Lo profesional sería que:

```text
no abra nuevas posiciones
```

pero:

```text
siga gestionando posiciones existentes
```

No sabemos si funciona así, pero debería.

Es importante distinguir:

```text
pause signals
```

de:

```text
stop process
```

## Reiniciar

Probablemente:

```text
detener módulos
limpiar estado transitorio
reconectar
recargar configuración
reiniciar scanner y estrategias
```

No debería necesariamente cerrar posiciones, aunque eso dependería del contrato.

## Detener

Podría:

* bloquear nuevas órdenes;
* detener estrategias;
* cancelar órdenes abiertas;
* quizá cerrar posiciones;
* desconectar feeds.

Aquí debería existir una política explícita:

```text
STOP_SOFT
STOP_HARD
EMERGENCY_STOP
```

No se puede saber si la tienen, pero el botón rojo sugiere un stop operacional.

# 10. “Inicio automático al abrir la GUI”

Esta casilla es muy informativa.

Se ve código a la derecha que parece leer y escribir algo parecido a:

```text
inicio_automatico_gui
```

Eso indica:

* configuración persistida;
* la GUI puede arrancar automáticamente el orquestador;
* el valor se guarda en `orquestador.json5`.

## Riesgo de diseño

Si la GUI controla el inicio del runtime, hay dos posibilidades:

### Diseño A

```text
GUI y runtime son el mismo proceso
```

Más sencillo, pero menos robusto.

### Diseño B

```text
GUI
↓
manda comandos
↓
runtime separado
```

Más profesional.

La imagen no permite demostrar cuál usan.

Pero por el código visible, parece que la clase `Dashboard` recibe algo como:

```python
master
bridge
```

y aparece `AsyncBridge`.

Eso podría indicar que la GUI controla un loop asíncrono separado.

# 11. Estado: “Escaneando PreMarket”

Esto demuestra que existe una **máquina de estados operativa**.

No solo:

```text
running / stopped
```

Sino estados de sesión:

```text
Inicializando
Conectando
Escaneando PreMarket
Esperando apertura
Operando
Gestionando cierres
Fin de sesión
```

Para small caps, esto es crucial.

## Posible orquestación por sesión

```text
04:00 ET
PREMARKET_SCAN
```

```text
09:25 ET
PREOPEN_PREPARATION
```

```text
09:30 ET
REGULAR_SESSION
```

```text
15:50 ET
CLOSE_MANAGEMENT
```

```text
16:00 ET
SESSION_END
```

El framework parece tener conciencia explícita del calendario de mercado.

# 12. Panel “Estrategias activas”

Está vacío y dice:

```text
Sin estrategias cargadas
```

Esto probablemente sería una lista de tarjetas con:

* nombre;
* símbolo;
* estado;
* posición;
* P&L;
* última señal;
* latencia;
* errores;
* botón de parada.

El pequeño botón azul arriba podría servir para:

* refrescar;
* cargar;
* expandir;
* abrir gestión de estrategias.

No se distingue con suficiente claridad.

# 13. Consola

Esta es la zona más reveladora.

Se ve algo parecido a:

```text
[06:51:30] [INFO] [premarket.scanner_massive]
Ciclo 343: 1.5s | operables=6 | pendientes=2072 | próximo ciclo en 29s
```

Después:

```text
[06:52:30] [INFO] [premarket.scanner_massive]
Operable (tipo1): TDIC volumen=920123 (shares)
```

Y luego:

```text
operables=7
pendientes=2072
```

# 14. Qué significa el ciclo de scanner

Parece ejecutar un barrido aproximadamente cada 30 segundos.

El ciclo dura:

```text
1.4–1.8 segundos
```

Después espera:

```text
28–29 segundos
```

Eso es perfectamente coherente con:

```text
snapshot Massive
↓
filtrado de ~2072 símbolos
↓
detección de candidatos
```

## Importante

`pendientes=2072` no parece significar cola de datos atrasada.

Más probablemente significa:

```text
símbolos todavía no operables
pero todavía bajo evaluación
```

Porque el valor permanece estable mientras `operables` cambia.

Podría ser:

```text
universo total evaluado = pendientes + operables
```

Ejemplo:

```text
2072 pendientes
7 operables
```

Total aproximado:

```text
2079 símbolos
```

# 15. “Operable (tipo1)”

Este texto sugiere que tienen varias categorías de operabilidad:

```text
tipo1
tipo2
tipo3
```

Podrían corresponder a reglas distintas:

```text
tipo1:
volumen > X

tipo2:
gap + volumen

tipo3:
movimiento intradía
```

O diferentes grupos de estrategias.

Eso indica que el scanner no devuelve solo:

```text
true / false
```

Sino una clasificación.

En TSIS podría modelarse como:

```text
UniverseMembershipReason
```

o:

```text
CandidateClass
```

# 16. Volumen como criterio

La línea:

```text
TDIC volumen=920123 shares
```

indica que al menos una regla de operabilidad depende del volumen.

En premarket probablemente calculan:

* volumen acumulado;
* precio;
* gap;
* quizá capitalización;
* quizá rango.

La consola solo imprime la razón principal, no necesariamente todas.

# 17. Tiempo de ejecución del scanner

El ciclo tarda cerca de 1.5 segundos para unos 2.000 símbolos.

Eso refuerza que probablemente usan:

```text
Full Market Snapshot REST
```

y no procesan quotes tick-by-tick de 2.000 símbolos.

El patrón probable:

```text
cada 30 segundos:
solicitar snapshot
recorrer resultados
aplicar filtros
actualizar candidatos
```

Mientras que para operables podrían activar WebSockets específicos.

# 18. Botones “Copiar” y “Limpiar”

Son controles de observabilidad.

No aportan trading, pero sí soporte operativo:

* copiar logs para debugging;
* limpiar visualización sin borrar el archivo;
* inspeccionar incidentes.

Esto muestra que la consola está pensada para uso humano diario.

# 19. Barra inferior

Se distinguen aproximadamente:

```text
Status: Escaneando PreMarket
Exposición: 0%
Retorno flotante sobre equity inicial: 0.00%
DAS
To Market Open 02:34:05
EDT: 06:55:54
CPU: 6.2%
Memoria: 440 MB
```

Cada elemento revela un subsistema.

## Exposición 0%

Existe un portfolio/risk engine que calcula exposición.

## Retorno flotante

Mantienen:

* equity inicial;
* P&L no realizado;
* retorno en tiempo real.

## Indicador DAS

Un heartbeat visual de conexión.

## Countdown a apertura

Existe un market clock.

## EDT

La zona horaria está explícita.

Esto es especialmente importante tras lo que ellos mismos escriben sobre errores horarios.

## CPU y memoria

Monitorización de recursos integrada.

Eso tiene sentido si procesan feeds en tiempo real y quieren detectar degradación.

# 20. Código visible a la derecha

Aunque no se puede leer todo, sí se distinguen pistas:

* `json5`;
* `AsyncBridge`;
* `PySide6`;
* widgets personalizados;
* ruta `config/orquestador.json5`;
* funciones para leer y escribir `inicio_automatico_gui`;
* clase `Dashboard`.

## Lo que esto confirma

### Configuración externa

No todo está dentro del código.

```text
config/
orquestador.json5
```

### GUI modular

Hay widgets separados.

### Bridge asíncrono

Probablemente tienen:

```text
Qt event loop
+
asyncio event loop
```

y necesitan una capa para comunicarlos.

Esto es habitual porque Qt y `asyncio` tienen loops propios.

# 21. Arquitectura inferida de esta única imagen

Mi reconstrucción sería:

```text
┌───────────────────────────────────────────┐
│ Desktop GUI — PySide6                    │
│ Dashboard / Operativa / Config / Logs    │
└───────────────────┬───────────────────────┘
                │ commands + status
                ▼
┌───────────────────────────────────────────┐
│ Runtime Orchestrator                     │
│ state machine / session / lifecycle      │
└───────┬──────────────┬──────────────┬─────┘
    │              │              │
    ▼              ▼              ▼
Massive Adapter    DAS Adapter     Watchdog
    │              │              │
    ▼              ▼              ▼
Premarket Scanner  Orders/Fills   Health checks
    │
    ▼
Universe/Candidates
    │
    ▼
Strategy Loader
    │
    ▼
Risk + OMS
    │
    ▼
DAS Execution
```

Paralelamente:

```text
Logs
Metrics
Buffer
Portfolio state
GUI updates
```

# 22. ¿Es parecido a NautilusTrader?

En responsabilidades, sí:

```text
data
runtime
strategy
risk
execution
portfolio
monitoring
```

Pero no parece necesariamente construido encima de Nautilus.

Hay varias pistas contra esa hipótesis:

* nomenclatura totalmente propia;
* GUI propia;
* scanner Massive propio;
* JSON5 propio;
* DAS bridge propio;
* no aparecen identificadores de Nautilus;
* el código visible parece usar clases internas de `src.gui`.

Lo más probable es:

> Framework propio inspirado en patrones estándar de sistemas event-driven, no una simple capa visual sobre Nautilus.

# 23. Qué podemos aprender para TSIS

Esta imagen sugiere que el runtime mínimo de TSIS necesitaría al menos:

```text
RuntimeOrchestrator
MarketClock
MassiveAdapter
DASAdapter
PremarketScanner
UniverseState
StrategyRegistry
RiskEngine
OrderManager
PortfolioState
Watchdog
MetricsMonitor
LogBus
ConfigurationManager
DesktopControlPanel
```

Pero hay una distinción importante:

> No deberíamos comenzar copiando la GUI.

Primero:

```text
runtime headless
```

Después:

```text
observability API
```

Y por último:

```text
GUI
```

La interfaz debe ser una ventana al runtime, no el propio runtime.

# 24. Lo que todavía no podemos saber

Con esta imagen no podemos determinar:

* si usan multiproceso o multihilo;
* si el runtime sobrevive al cierre de la GUI;
* si Massive usa REST, WebSocket o ambos;
* si guardan eventos en una base de datos;
* si usan PostgreSQL, SQLite o archivos;
* si el OMS es verdaderamente event-sourced;
* si su backtester comparte código con live;
* si el scanner usa 2.072 símbolos fijos o dinámicos;
* cómo realizan locates;
* cómo modelan la reconciliación con DAS;
* si su risk engine está centralizado;
* si las estrategias son plugins dinámicos.

Pero sí tenemos evidencias suficientes para sostener:

```text
GUI Python propia
+
runtime propio
+
Massive como data feed
+
DAS como ejecución
+
scanner premarket recurrente
+
watchdog
+
configuración externa
+
observabilidad operativa
```

# Veredicto de la imagen 1

Esta no es simplemente una pantalla de control de un bot.

Parece la capa visible de un sistema con al menos cinco planos:

```text
Control plane
Data plane
Strategy plane
Execution plane
Observability plane
```

Y el detalle más revelador no son los botones.

Es esta combinación:

```text
Massive LIVE
localhost:9910 DAS
scanner_massive
watchdog
buffer
orquestador.json5
AsyncBridge
```

Eso apunta a una arquitectura modular y separada, construida específicamente para operar small caps automáticamente desde una máquina local.
