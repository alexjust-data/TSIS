# Directiva obligatoria de optimización de TSIS para el PC local

Eres un agente de ingeniería que trabaja en TSIS. Esta directiva es obligatoria para cualquier tarea que cree, modifique, revise o ejecute código, pipelines de datos, backtests, simulaciones, optimizaciones o modelos de machine learning de TSIS.

## Objetivo

Entrega una solución correcta, reproducible y completamente optimizada para aprovechar de forma eficiente la capacidad real del PC local. No basta con que el código funcione: debes medir su rendimiento, identificar el recurso limitante y demostrar que la solución utiliza adecuadamente el hardware disponible, sin provocar paginación excesiva, falta de memoria, sobreasignación de hilos, saturación térmica ni pérdida de estabilidad.

## Hardware confirmado actualmente

- Sistema: Windows 11 Home de 64 bits.
- Placa base: MSI B550-A PRO (MS-7C56), BIOS AMI A.J1 del 27/08/2024.
- CPU: AMD Ryzen 7 5800X, 8 núcleos físicos y 16 hilos lógicos.
- Refrigeración: Cooler Master MasterLiquid 240L Core ARGB, radiador de 240 mm, referencia MLW-D24M-A18PZ-R1.
- RAM: 32 GB DDR4-3200 CL16, 2 x 16 GB Corsair CMK32GX4M2E3200C16, doble canal; quedan dos ranuras libres.
- GPU: NVIDIA GeForce RTX 4060 ASUS Dual OC/EVO, 8 GB de VRAM, PCIe 4.0 x8, límite aproximado de 115 W.
- Disco de trabajo principal: WD_BLACK SN770 NVMe de 2 TB, unidad C: NTFS. En la última inspección quedaban aproximadamente 464 GB libres.
- Almacenamiento auxiliar: Samsung HD105SI USB de 1 TB, unidad D: NTFS; HGST G-DRIVE USB de 3 TB, unidad G: HFS Plus y con poco espacio libre.
- WSL2 observado: 16 CPU lógicas visibles, aproximadamente 15 GiB de RAM y 4 GiB de swap, sin `.wslconfig` personalizado.
- Plan energético observado: Alto rendimiento.
- Red Realtek Gigabit: el enlace observado estaba negociado a 100 Mbps.
- Fuente de alimentación y modelo de caja: todavía no identificados; no presupongas sus especificaciones.

Este inventario es una referencia inicial, no una excusa para codificar valores rígidos. Al comenzar una tarea de rendimiento, detecta los recursos realmente disponibles en ese momento, porque la RAM, CPU, GPU, discos o límites de WSL pueden cambiar.

## Cuellos de botella ya observados en TSIS

- Durante una carga real, la memoria comprometida llegó aproximadamente al 87 %.
- Windows utilizó el archivo de paginación: unos 6,2 GB en uso y un pico observado de unos 10,4 GB.
- El pipeline tenía `--shard-count 4`, pero solo dos workers realizaban trabajo útil.
- Cada worker activo consumía aproximadamente un hilo lógico; en la práctica se utilizaban cerca de 2 de los 16 hilos disponibles.
- Un worker llegó a consumir aproximadamente 8-9 GB de memoria privada.
- Los procesos TSIS inspeccionados no estaban utilizando CUDA. Otro proceso Python ajeno sí aparecía conectado a la GPU.

Trata estas observaciones como hipótesis que debes volver a medir, pero no las ignores: actualmente hay indicios claros de infrautilización de CPU y presión de RAM.

## Procedimiento obligatorio para cada trabajo

### 1. Inspección previa

Antes de implementar cambios relevantes:

1. Examina el código, el formato y volumen de los datos, la unidad donde residen y la ejecución actual.
2. Detecta CPU lógica y física, RAM disponible, espacio libre, GPU/VRAM y límites del entorno Windows, WSL, Docker o máquina virtual que se esté usando.
3. Obtén una línea base representativa: tiempo total, registros o casos por segundo, utilización de CPU por núcleo, RAM máxima, paginación, lectura/escritura de disco y uso de GPU/VRAM cuando proceda.
4. Determina si el cuello de botella es CPU, memoria, disco, transferencia de datos, GPU, sincronización, serialización, algoritmo o paralelismo defectuoso.
5. No afirmes que una tarea está optimizada sin datos de la línea base y de la versión final.

### 2. Uso de CPU

- Para trabajo CPU-bound, utiliza procesos, código compilado/vectorizado o librerías que liberen el GIL. No confíes en hilos de Python para cálculo puro si el GIL impide el paralelismo real.
- Como punto de partida para procesos CPU-bound independientes, prueba hasta 7 u 8 workers y selecciona mediante benchmark el número más rápido y estable. No fijes ese número si la detección dinámica permite adaptarlo.
- Reserva capacidad suficiente para Windows, coordinación e I/O; maximizar el porcentaje de CPU no es el objetivo si empeora el tiempo total o provoca falta de respuesta.
- Evita la sobresuscripción: si NumPy, BLAS, MKL, OpenMP, PyTorch u otra librería crea hilos internos, coordina `workers x threads_por_worker` con los 8 núcleos físicos y 16 hilos lógicos disponibles.
- Reutiliza pools de workers. Evita lanzar procesos repetidamente, copiar grandes DataFrames entre ellos o serializar los mismos datos para cada tarea.
- Equilibra los shards según el trabajo real, no solo por número de archivos. Detecta y corrige workers o shards inactivos, colas desequilibradas y fases accidentalmente seriales.
- Conserva determinismo: semillas explícitas, orden estable cuando afecte al resultado y reducción reproducible de resultados paralelos.

### 3. Uso de memoria

- Con 32 GB instalados, diseña inicialmente para que TSIS permanezca aproximadamente dentro de 22-24 GB de RAM en cargas sostenidas, dejando margen para Windows y herramientas auxiliares. Ajusta el límite tras medir el entorno real.
- No cargues datasets históricos completos si pueden procesarse por particiones, fechas, símbolos, row groups o lotes.
- Prefiere Parquet/Arrow y lectura selectiva de columnas y filtros. Usa tipos de datos compactos y evita copias innecesarias de DataFrames.
- Evalúa Polars, DuckDB, PyArrow, NumPy, Numba u otras alternativas solo cuando encajen con el problema y un benchmark representativo demuestre la mejora.
- Procesa en streaming o por chunks cuando el tamaño pueda crecer. Libera referencias temporales grandes y evita concatenaciones repetidas de coste cuadrático.
- Calcula el número de workers también a partir de la memoria estimada por worker. Reduce concurrencia antes de provocar paginación sostenida.
- La paginación intensa no se considera aprovechamiento de memoria: se considera un fallo de diseño o dimensionamiento que debe corregirse o justificarse con mediciones.

### 4. Uso de GPU y machine learning

- Detecta CUDA, versión del driver, compatibilidad de la librería y VRAM libre antes de seleccionar GPU.
- Usa la RTX 4060 solo en operaciones compatibles que sean más rápidas de extremo a extremo. Demuéstralo comparando tiempo total con CPU, incluyendo preparación y transferencias.
- No traslades a GPU tareas pequeñas, lógica de control, joins o transformaciones que pierdan más tiempo transfiriendo datos que calculando.
- Mantén batches dentro de los 8 GB de VRAM con margen de seguridad. Evita el intercambio continuo RAM-VRAM y las situaciones de out-of-memory.
- Usa precisión mixta, TF32 o formatos reducidos únicamente cuando sean compatibles y hayas comprobado que no alteran de forma inaceptable los resultados del backtest o del modelo.
- Registra dispositivo, versiones, semilla, precisión, tamaño de batch, VRAM máxima y tiempos de entrenamiento e inferencia.
- Si la GPU no aporta ventaja, utiliza la ruta CPU optimizada y explica la evidencia. No simules ni declares aceleración CUDA si no está activa.

### 5. Datos y almacenamiento

- Utiliza el WD_BLACK SN770 NVMe para código, índices, cachés controladas, datos activos y resultados temporales de alto rendimiento.
- Comprueba siempre el espacio libre antes de materializar datasets, cachés, modelos o resultados grandes. No llenes C:.
- Usa los discos mecánicos o el futuro disco externo de 8 TB principalmente para datos fríos, archivo, copias, resultados terminados y datasets que no quepan en el NVMe.
- Para trabajar directamente desde un HDD externo, lee de forma secuencial y por bloques grandes; evita millones de archivos pequeños y accesos aleatorios repetitivos.
- Prefiere datasets particionados de forma útil y archivos Parquet de tamaño razonable. Evita tanto archivos diminutos como ficheros monolíticos imposibles de procesar selectivamente.
- Minimiza escrituras repetidas, conversiones de formato y copias entre C:, D:, G: y futuros discos externos.
- No presupongas que G: es plenamente escribible o interoperable desde Windows porque actualmente figura como HFS Plus.
- Conserva datos originales inmutables y separa claramente fuente, caché reconstruible, datos procesados y resultados.

### 6. Algoritmos y backtesting

- Antes de aumentar hardware o workers, elimina complejidad algorítmica evitable, bucles Python innecesarios, recomputaciones, consultas repetidas y materializaciones intermedias.
- Empuja filtros y selección de columnas hacia la lectura de datos.
- Precalcula o almacena en caché únicamente resultados reutilizables; define invalidación mediante versión de código, parámetros y huella de los datos de entrada.
- Evita look-ahead bias, leakage, errores de zona horaria y cambios de orden producidos por paralelización.
- La optimización nunca puede cambiar silenciosamente la semántica, precisión financiera ni universo del backtest. Compara resultados antes y después con tolerancias explícitas.
- Para ML, separa entrenamiento, validación y prueba de manera temporal y reproducible. Una mejora de velocidad no justifica contaminación de datos.

### 7. Temperatura, estabilidad y seguridad

- Para ejecuciones que duren horas o días, comprueba frecuencia efectiva, temperatura, throttling, errores y estabilidad; la refrigeración de 240 mm no elimina la obligación de medir.
- No modifiques BIOS, PBO, voltajes, plan energético global, archivo de paginación, particiones, drivers ni configuración permanente del sistema sin autorización expresa.
- No supongas que la fuente admite una futura CPU o GPU basándote solo en potencia estimada: falta identificar su modelo exacto.
- Implementa checkpoints y reanudación para que un fallo no obligue a repetir varios días de cálculo.
- Escribe resultados de forma atómica y conserva manifiestos, parámetros, logs y estado suficiente para auditar y reanudar la ejecución.

## Criterios obligatorios de aceptación

No des por terminada una optimización hasta entregar:

1. Hardware y límites detectados durante la ejecución.
2. Descripción del cuello de botella demostrado.
3. Línea base reproducible y benchmark final sobre la misma carga.
4. Tiempo total y throughput antes y después, con porcentaje de mejora.
5. Uso máximo de RAM, paginación, CPU efectiva, disco y GPU/VRAM cuando corresponda.
6. Número de procesos, hilos, shards, tamaño de chunk y batch finalmente elegidos, explicando por qué.
7. Prueba de equivalencia o validación funcional de los resultados.
8. Pruebas automatizadas relevantes superadas.
9. Riesgos, límites que permanecen y siguiente mejora con mayor retorno.
10. Comandos exactos para reproducir la ejecución optimizada.

Si no puedes medir alguna métrica, indícalo expresamente y proporciona el procedimiento o instrumento concreto para obtenerla. No inventes resultados ni uses expresiones como "optimizado", "usa todos los núcleos" o "acelerado por GPU" sin evidencia.

## Formato de respuesta del agente

Comienza cada entrega de rendimiento con este resumen:

```text
Entorno detectado:
Carga analizada:
Línea base:
Cuello de botella:
Cambios aplicados:
Configuración de paralelismo y memoria:
Resultado final:
Validación de exactitud:
Riesgos o límites restantes:
Comando reproducible:
```

Cuando la tarea solicitada no sea de rendimiento, sigue aplicando estas reglas a cualquier decisión que pueda afectar tiempo de ejecución, memoria, I/O o escalabilidad, sin introducir complejidad innecesaria fuera del alcance de la tarea.
