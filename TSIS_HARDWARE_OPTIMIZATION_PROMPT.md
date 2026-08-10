# Contexto permanente de hardware y rendimiento para TSIS

## Instrucción principal

Estás trabajando en TSIS sobre el ordenador descrito en este documento. Debes tener presente esta configuración al diseñar, implementar, revisar o ejecutar cualquier componente: ingesta y transformación de datos, investigación, backtesting, optimización de parámetros, simulaciones y machine learning.

Tu objetivo es obtener el máximo rendimiento útil y estable que permita esta máquina, manteniendo siempre la exactitud, reproducibilidad y auditabilidad de los resultados. No escribas soluciones genéricas que ignoren el hardware disponible. Adapta los algoritmos, estructuras de datos, paralelismo, almacenamiento y librerías a esta configuración concreta.

## Máquina disponible

- Sistema operativo: Windows 11 Home de 64 bits.
- Placa base: MSI B550-A PRO (MS-7C56), chipset B550, BIOS AMI A.J1 del 27/08/2024.
- Procesador: AMD Ryzen 7 5800X.
  - 8 núcleos físicos y 16 hilos lógicos.
  - Arquitectura x86-64 con AVX2.
  - 32 MB de caché L3.
- Refrigeración: Cooler Master MasterLiquid 240L Core ARGB.
  - Refrigeración líquida AIO.
  - Radiador de 240 mm con dos ventiladores de 120 mm.
  - Referencia MLW-D24M-A18PZ-R1.
- Memoria: 32 GB DDR4-3200 CL16 en doble canal.
  - 2 módulos Corsair de 16 GB.
  - Modelo CMK32GX4M2E3200C16.
  - Dos ranuras de memoria permanecen libres.
- Tarjeta gráfica: NVIDIA GeForce RTX 4060 ASUS Dual OC/EVO.
  - 8 GB de VRAM y soporte CUDA.
  - PCIe 4.0 x8.
  - Potencia aproximada de 115 W.
- Almacenamiento principal de alto rendimiento:
  - WD_BLACK SN770 NVMe de 2 TB.
  - Unidad C: con NTFS.
  - Es la unidad preferente para código, datos activos, cachés de cálculo y resultados temporales que requieran alta velocidad.
- Almacenamiento auxiliar:
  - Samsung HD105SI USB de 1 TB, unidad D: con NTFS.
  - HGST G-DRIVE USB de 3 TB, unidad G: con HFS Plus.
  - Los discos mecánicos son adecuados para archivo, copias y datos fríos; no tienen el rendimiento del NVMe para accesos aleatorios intensivos.
- Entorno Linux mediante WSL2:
  - 16 procesadores lógicos visibles.
  - Aproximadamente 15 GiB de RAM asignados.
  - Aproximadamente 4 GiB de swap.
- Fuente de alimentación y modelo de caja: no están identificados. No inventes sus especificaciones ni bases en ellas una recomendación de ampliación.

Esta es la configuración de referencia autorizada. No dediques tiempo a volver a inventariarla en cada tarea. Si aparece evidencia inequívoca de que algún componente ha cambiado, informa de la discrepancia antes de basar decisiones importantes en ella.

## Aprovechamiento del procesador

- Diseña los trabajos CPU-bound para utilizar de forma efectiva los 8 núcleos y 16 hilos cuando las partes del cálculo sean independientes.
- En Python, distingue entre concurrencia y paralelismo real. Para cálculo puro limitado por el GIL, utiliza multiprocesamiento, vectorización, compilación JIT o librerías nativas que liberen el GIL.
- Aprovecha NumPy, Polars, PyArrow, DuckDB, Numba u otras herramientas equivalentes cuando encajen técnicamente y aporten una ventaja real.
- Reduce primero el coste algorítmico: elimina cálculos repetidos, bucles Python innecesarios, búsquedas redundantes y materializaciones evitables.
- Determina mediante una prueba representativa la combinación apropiada de procesos e hilos. Considera que NumPy, BLAS, OpenMP, PyTorch y otras librerías pueden crear hilos internos.
- Evita la sobresuscripción. Coordina procesos y threads internos para que no compitan destructivamente por los 16 hilos lógicos.
- Reutiliza pools de procesos y minimiza creación de workers, serialización y transferencia de grandes estructuras.
- Divide el trabajo según el coste real de cada partición, no solo por número de archivos, fechas o símbolos.
- Deja margen para Windows y la coordinación. El objetivo es reducir el tiempo total, no mostrar un 100 % de CPU a cualquier precio.

## Aprovechamiento de la memoria

- La máquina dispone de 32 GB. Diseña para trabajar dentro de este límite y conservar margen para Windows y procesos auxiliares.
- Calcula la concurrencia teniendo en cuenta núcleos y memoria consumida por worker. No lances más procesos de los que la RAM pueda sostener eficientemente.
- Evita la paginación sostenida: utilizar el disco como sustituto habitual de la RAM degrada gravemente el rendimiento.
- No cargues un histórico completo si puede procesarse por fechas, símbolos, particiones, row groups o lotes.
- Lee únicamente las columnas y filas necesarias y aplica filtros lo más cerca posible de la lectura.
- Usa tipos compactos sin perder la precisión financiera necesaria.
- Evita copias innecesarias de DataFrames, concatenaciones repetidas, conversiones dentro de bucles y objetos Python por fila.
- Utiliza chunks, streaming, memoria mapeada o ejecución fuera de memoria cuando el volumen de datos lo requiera.
- Libera temporales grandes y evita mantener simultáneamente varias representaciones equivalentes del mismo dataset.

## Aprovechamiento de la RTX 4060

- Considera la GPU para machine learning y operaciones masivamente paralelas compatibles con CUDA.
- Utiliza librerías con soporte GPU solo cuando sean compatibles con el entorno y con la operación realizada.
- La GPU dispone de 8 GB de VRAM. Selecciona batches y modelos que dejen margen y evita desbordamientos o transferencias continuas RAM-VRAM.
- Mantén en GPU los datos reutilizados durante varias operaciones para reducir transferencias por PCIe.
- No envíes a GPU tareas pequeñas, lógica de control o cálculos cuyo coste de transferencia supere el ahorro de cómputo.
- Usa precisión mixta o formatos reducidos únicamente cuando preserven la exactitud requerida y hayan sido validados.
- Si una tarea admite CPU y GPU, selecciona la ruta con menor tiempo total de extremo a extremo.
- El backtesting tradicional, las reglas, joins y muchas transformaciones tabulares pueden funcionar mejor en CPU; no fuerces CUDA cuando no corresponda.

## Organización de datos y almacenamiento

- Usa el WD_BLACK SN770 NVMe para datos activos, índices, cachés útiles, bases analíticas, checkpoints y temporales de alto rendimiento.
- Comprueba el espacio requerido antes de crear datasets o cachés grandes y evita llenar la unidad del sistema.
- Utiliza los HDD externos para originales pesados, archivo histórico, copias y resultados que no necesiten acceso aleatorio continuo.
- Si debes leer directamente desde un HDD, organiza acceso secuencial, bloques grandes y el mínimo número posible de pasadas.
- Evita millones de archivos pequeños. Emplea Parquet u otro formato columnar adecuado, con particiones útiles y tamaños eficientes.
- Aprovecha filtrado de particiones, row groups y columnas para no leer datos innecesarios.
- Evita copiar repetidamente los mismos datos entre unidades. Cuando resulte ventajoso, usa una caché reconstruible en el NVMe con validez controlada.
- Separa originales inmutables, datos normalizados, cachés reconstruibles, modelos y resultados finales.
- No presupongas que G: en HFS Plus ofrece desde Windows las mismas operaciones o fiabilidad de escritura que NTFS.

## Backtesting y machine learning

- Ninguna optimización puede cambiar silenciosamente lógica financiera, universo, ejecución, comisiones, tratamiento temporal o precisión.
- Preserva orden temporal, zonas horarias, sesiones y ausencia de look-ahead bias o leakage.
- Mantén determinismo cuando sea posible: semillas explícitas, parámetros registrados y reducciones paralelas reproducibles.
- Para ML, conserva separaciones temporales correctas entre entrenamiento, validación y prueba.
- Evita recalcular transformaciones idénticas entre experimentos. Usa caché con invalidación basada en datos, parámetros y versión del código.
- Implementa checkpoints y reanudación en procesos largos para no perder horas o días por una interrupción.
- Escribe resultados importantes de forma atómica y conserva manifiestos, parámetros, versiones y logs suficientes para reproducirlos.

## Método obligatorio de optimización

Para cualquier cambio con impacto relevante en rendimiento:

1. Comprende el algoritmo, el volumen de datos y la ruta crítica.
2. Obtén una medición inicial representativa.
3. Identifica si el límite es CPU, RAM, disco, GPU, transferencia, serialización, sincronización o complejidad algorítmica.
4. Elige la optimización que mejor encaje con esta máquina.
5. Valida equivalencia de resultados o tolerancias explícitas.
6. Repite la misma medición y compara tiempo total, throughput y recursos.
7. Conserva el cambio solo si mejora el rendimiento útil sin perjudicar exactitud, estabilidad o mantenibilidad de forma injustificada.

No optimices únicamente por intuición ni introduzcas complejidad innecesaria cuando el rendimiento no sea relevante.

## Condiciones de finalización

Cuando hayas realizado trabajo de rendimiento, informa de forma concisa:

```text
Tarea o carga optimizada:
Cuello de botella identificado:
Solución aplicada:
Uso de CPU, RAM, disco y GPU elegido:
Tiempo o throughput anterior:
Tiempo o throughput final:
Validación de resultados:
Configuración y comando reproducible:
Límite restante, si existe:
```

No declares que algo está optimizado, paralelizado o acelerado por GPU sin comprobarlo. El criterio final es el rendimiento real, correcto y estable de TSIS en esta máquina concreta.
