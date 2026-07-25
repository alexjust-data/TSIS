Esta imagen vale oro.

No porque podamos leer todo el código (no podemos), sino porque **revela la organización mental del proyecto**.

Voy a separar **hechos observables**, **inferencias fuertes** e **hipótesis**.

---

# 1. El proyecto es Python puro

Esto ya es prácticamente seguro.

Se ven imports como:

```python
import json5
```

y

```python
from pathlib import Path
```

Eso significa:

* Python moderno.
* No C#.
* No Java.
* No Node.

---

# 2. Usan JSON5

No JSON.

JSON5.

Eso me gusta muchísimo.

Porque permite:

```text
comentarios

comas finales

más legibilidad
```

Para configuraciones grandes es mucho mejor.

---

# 3. Existe un módulo llamado

```python
src.utils.zonas_horarias
```

e importa:

```python
ZONA_HORARIA
```

Eso me parece MUY interesante.

¿Por qué?

Porque demuestra que:

```text
la zona horaria

NO

está repartida por el código.
```

Existe un sitio único.

Muy buena práctica.

---

# 4. TYPE_CHECKING

Aparece:

```python
if TYPE_CHECKING:
```

Eso significa:

* usan typing
* probablemente mypy
* anotaciones

No es código "rápido".

Es código bastante cuidado.

---

# 5. AsyncBridge

Aquí aparece una de las piezas más interesantes.

```python
AsyncBridge
```

No sabemos qué hace.

Pero el nombre es muy revelador.

Yo creo que sirve para comunicar:

```text
Qt

↓

asyncio
```

Porque normalmente:

Qt

tiene

```text
Event Loop
```

y

asyncio

tiene otro.

Necesitas un puente.

---

# 6. Widgets

Se ven imports.

Algo parecido a:

```python
ConsoleWidget

StatusCard

StrategyList
```

Eso significa que la GUI es modular.

No hay un único:

```python
main.py
```

Gigante.

---

# 7. Dialogs

Aparece:

```python
dialogs
```

Eso implica separación:

```text
widgets

dialogs

utils
```

Muy buena organización.

---

# 8. bannerlog

Creo leer algo parecido a:

```python
bannerlog
```

o

```python
bannerlogs
```

No estoy seguro.

Pero podría ser una utilidad para:

```text
cabeceras

mensajes

logos
```

---

# 9. La ruta

Aquí viene algo MUY interesante.

```python
RUTA_ORQUESTADOR

=

...

config

orquestador.json5
```

Eso confirma definitivamente:

Existe un:

```text
Orchestrator
```

Y además:

NO está hardcodeado.

Se configura.

---

# 10. Función

Se lee:

```python
leer_inicio_automatico()
```

Después:

```python
actualizar_inicio_automatico()
```

Eso ya nos dice mucho.

No hacen:

```python
settings["..."]=...
```

Hacen:

Funciones.

Es decir.

Hay una capa de acceso.

---

# 11. Lee JSON5

Se ve claramente.

```python
json5.load(...)
```

Después:

```python
datos.get(...)
```

Muy limpio.

---

# 12. Escriben JSON mediante Regex

Esto me sorprendió.

Se ve:

```python
re.compile(...)
```

Después:

```python
pattern.search(...)
```

Después:

```python
pattern.sub(...)
```

Eso significa que modifican el fichero.

No reescriben todo el JSON.

Interesante.

---

# 13. DashboardTab

Aquí aparece.

```python
class DashboardTab(...)
```

Eso confirma.

Cada pestaña es una clase.

No:

```python
if tab==...
```

---

# 14. **init**

El constructor recibe:

```python
master

bridge

**kwargs
```

La palabra:

```python
bridge
```

vuelve a aparecer.

Muy probablemente:

```text
GUI

↓

Bridge

↓

Runtime
```

---

# 15. master

Esto huele muchísimo a:

Qt.

---

# 16. self.bridge

Dentro.

```python
self.bridge
```

Eso significa que el Dashboard habla con el Runtime mediante:

```text
Bridge
```

NO directamente.

Eso es arquitectura.

---

# 17. Grid

Aparece:

```python
grid_columnconfigure(...)
```

Eso es claramente:

Tkinter...

Pero espera.

Aquí hay algo raro.

Porque antes parecía PySide.

Y aquí:

```python
grid_columnconfigure
```

es de Tk.

Entonces...

---

# 18. Esto cambia bastante

Creo que NO usan Qt.

Creo que usan:

```text
CustomTkinter
```

Y arriba del todo veo algo parecido a:

```python
import customtkinter as ctk
```

¡¡Eso cambia muchísimo!!

---

# Entonces

El Dashboard hereda de algo parecido a:

```python
ctk.CTkFrame
```

No de Qt.

Eso encaja perfectamente con:

```python
grid_columnconfigure
```

---

# Si eso es correcto

La arquitectura sería:

```text
Python

↓

CustomTkinter

↓

AsyncIO

↓

Bridge

↓

Runtime
```

No PySide.

---

# 19. Ruta del proyecto

Abajo se ve.

```text
DAS_API
```

Parece el nombre del repositorio.

Muy interesante.

---

# 20. Organización

Yo reconstruiría algo parecido.

```text
src/

gui/

    widgets/

    dialogs/

    utils/

runtime/

scanner/

strategies/

execution/

config/

    orquestador.json5
```

---

# Lo más importante

Esta imagen confirma algo que llevaba sospechando.

NO parece un proyecto de trading.

Parece un proyecto de software.

Y eso cambia completamente la forma de estudiarlo.

---

# Lo que copiaría literalmente para TSIS

No el código.

La estructura.

```text
src/

runtime/

adapters/

scanner/

universe/

state/

strategies/

risk/

orders/

execution/

accounting/

analytics/

gui/

config/

tests/

docs/
```

---

# Pero ahora viene lo que más me ha llamado la atención

La palabra:

```text
ORQUESTADOR
```

Hasta ahora hablábamos de:

```text
Runtime
```

Pero ellos no lo llaman así.

Lo llaman:

```text
Orquestador
```

Y creo que es un nombre muy acertado.

Porque realmente NO decide estrategias.

NO hace backtesting.

NO calcula indicadores.

Hace otra cosa.

Coordina.

Es decir.

```text
Scanner

↓

Runtime

↓

Risk

↓

Orders

↓

Watchdog

↓

Logs
```

Todo eso necesita alguien que diga:

```text
ahora

espera

reanuda

reinicia

abre mercado

cierra mercado
```

Eso es un:

```text
Orchestrator
```

Y sinceramente...

creo que esa palabra es muchísimo mejor que:

```text
Engine
```

para esa pieza.

---

## Hay una conclusión arquitectónica que creo que merece la pena destacar

Hasta ahora hablábamos del **Runtime** como un bloque.

Después de esta imagen, yo lo dividiría explícitamente en dos componentes distintos:

```text
Runtime
```

que contiene la lógica de negocio (scanner, estrategias, riesgo, órdenes, ejecución...)

y por encima:

```text
Orchestrator
```

que coordina el ciclo de vida del sistema:

* inicio;
* parada;
* estados de sesión;
* reconexiones;
* heartbeats;
* carga de configuración;
* activación de estrategias;
* transición entre premarket, mercado abierto y cierre.

Esa separación me parece muy elegante y encaja perfectamente con lo que se observa tanto en el código (`orquestador.json5`, `AsyncBridge`, `DashboardTab`) como en la interfaz (botones de iniciar, pausar, reiniciar y detener). En mi opinión, es una de las ideas arquitectónicas más valiosas que podemos extraer de esta captura.
