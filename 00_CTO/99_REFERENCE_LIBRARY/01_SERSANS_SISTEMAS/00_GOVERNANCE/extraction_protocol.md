# Extraction Protocol v0.2

## 1. Objetivo

Definir un procedimiento repetible para extraer el máximo conocimiento de cada práctica sin:

- reducirla a un resumen;
- forzar todo a Topics o Assets existentes;
- perder comentarios, ejemplos o conocimiento tácito;
- duplicar conocimiento;
- convertir opiniones en hechos;
- producir miles de notas sin destino ni trazabilidad.

## 2. Unidad de trabajo

La unidad de captura es el `Evidence Item`, anclado a un `Source Fragment`.

Un Source Fragment puede ser:

- un intervalo de líneas;
- un turno de conversación;
- una pregunta y su respuesta;
- una imagen completa;
- una zona de una imagen;
- un bloque de código;
- una tabla;
- una configuración;
- una secuencia de pasos;
- una demostración realizada con una herramienta.

## 3. Pipeline por práctica

### Paso 0 — Preservación de la fuente

1. Registrar el archivo original y su versión.
2. Calcular o conservar un identificador estable.
3. No modificar la fuente durante la extracción.
4. Registrar archivos auxiliares, imágenes y código asociado.

### Paso 1 — Inventario

Crear:

- manifiesto de archivos;
- manifiesto de figuras;
- relación entre imágenes y posiciones del texto;
- lista de imágenes no referenciadas;
- lista de referencias rotas;
- anomalías de numeración, transcripción o formato.

Toda imagen debe revisarse, esté o no enlazada desde el Markdown.

### Paso 2 — Segmentación

Dividir la práctica en Source Fragments suficientemente pequeños para conservar contexto, pero no necesariamente línea por línea.

Los límites pueden venir dados por:

- cambio de tema;
- nueva demostración;
- pregunta de un alumno;
- cambio de herramienta;
- aparición de una regla;
- ejemplo concreto;
- explicación de una imagen;
- cambio entre teoría y práctica.

### Paso 3 — Captura abierta

Extraer Evidence Items sin exigir que encajen en una categoría previa.

En cada fragmento buscar activamente:

- hechos;
- conceptos;
- afirmaciones expertas;
- heurísticas;
- trucos prácticos;
- procedimientos;
- formas de trabajar;
- decisiones profesionales;
- advertencias;
- errores;
- limitaciones;
- preguntas;
- respuestas;
- malentendidos frecuentes;
- ejemplos y contraejemplos;
- casos concretos;
- código;
- fórmulas;
- parámetros;
- métricas;
- gráficos;
- menús;
- columnas;
- configuraciones;
- aplicaciones;
- capacidades y limitaciones de herramientas;
- recomendaciones de libros, papers, personas o recursos;
- hipótesis;
- contradicciones;
- asuntos pendientes;
- implicaciones posibles para TSIS.

La lista anterior es orientativa y no exhaustiva.

### Paso 4 — Anclaje

Cada Evidence Item debe registrar, cuando sea posible:

```yaml
evidence_id:
source_id:
practice_id:
source_fragment:
figure_id:
speaker:
captured_content:
context:
capture_status:
```

La cita literal debe distinguirse de la paráfrasis. Si se captura una imagen, se indicará si el hallazgo procede de texto visible, estructura visual o interpretación funcional.

### Paso 5 — Interpretación provisional

Después de capturar, y nunca antes, pueden añadirse:

```yaml
form:
knowledge_nature:
subject:
possible_use:
epistemic_status:
confidence:
requires_validation:
notes:
```

No se fuerza una clasificación. `Unknown` y `Pending Review` son valores válidos.

### Paso 6 — Descubrimiento y actualización de Topics

Los Topics se descubren a partir del contenido completo de la práctica.

Un Topic:

- organiza un dominio de aprendizaje;
- puede recibir evidencia procedente de varias prácticas;
- no es necesariamente una sección del documento;
- puede solaparse con otros Topics;
- no obliga a materializar un Asset.

Los Topics iniciales son hipótesis de organización y pueden:

- dividirse;
- fusionarse;
- renombrarse;
- ampliarse;
- quedar obsoletos.

### Paso 7 — Consolidación

Comparar cada Evidence Item con el conocimiento existente:

```text
¿Apoya un registro existente?
¿Lo contradice?
¿Añade contexto?
¿Define una excepción?
¿Repite exactamente lo ya conocido?
¿Revela una categoría o relación nueva?
```

Varias evidencias pueden consolidarse en un único Knowledge Record. Una evidencia puede apoyar varios registros si las relaciones están justificadas.

### Paso 8 — Evaluación epistemológica

Antes de validar conocimiento, distinguir:

- hecho observable;
- definición;
- fórmula;
- convención;
- resultado de un ejemplo;
- afirmación del profesor;
- experiencia profesional;
- opinión;
- heurística;
- recomendación;
- hipótesis;
- afirmación externa no comprobada.

Registrar si requiere contraste con:

- documentación oficial;
- libro;
- paper;
- datos;
- experimento;
- código;
- otra práctica del curso.

### Paso 9 — Propuesta de materialización

Un Knowledge Record puede producir uno o varios destinos:

- Asset;
- Best Practice;
- Warning;
- procedimiento;
- checklist;
- decisión de ingeniería candidata;
- tarea;
- test;
- entrada bibliográfica;
- comparación de herramientas;
- pregunta de investigación;
- sección del libro;
- referencia sin materialización.

No toda evidencia debe materializarse.

### Paso 10 — Revisión TSIS

Para una implicación TSIS, separar explícitamente:

```text
SOURCE OBSERVATION
INTERPRETATION
TSIS PROPOSAL
TSIS DECISION
IMPLEMENTATION
```

Solo `TSIS DECISION` aprobada puede incorporarse como arquitectura o requisito canónico.

### Paso 11 — Generación de vistas

Los resúmenes, capítulos y mapas se generan después de consolidar.

No deben introducir afirmaciones sin evidencia ni ocultar:

- contradicciones;
- incertidumbre;
- limitaciones;
- contexto;
- procedencia.

## 4. Protocolo específico para imágenes

Cada imagen se tratará como posible evidencia independiente.

### 4.1 Inspección visual

Registrar:

- qué ventana o herramienta aparece;
- título;
- pestañas;
- menús;
- columnas;
- métricas;
- valores;
- parámetros;
- unidades;
- controles;
- gráficos;
- ejes;
- leyendas;
- estados;
- advertencias;
- relaciones visibles.

### 4.2 Preguntas funcionales

```text
¿Qué necesidad muestra?
¿Qué datos necesita?
¿Qué cálculo puede existir detrás?
¿Qué configuración admite?
¿Qué output produce?
¿Qué comportamiento del sistema revela?
¿Es una capacidad, una presentación o ambas?
¿Podría implicar un requisito para TSIS?
```

Las respuestas a estas preguntas son interpretaciones, no evidencia literal, y deben marcarse como tales.

### 4.3 Imágenes huérfanas

Una imagen no referenciada:

- no se descarta;
- se inspecciona;
- se intenta vincular por proximidad, contenido y secuencia;
- se marca como `Orphan Figure` si no puede resolverse;
- puede generar un `Open Finding`.

## 5. Protocolo para preguntas y respuestas

Las preguntas de alumnos pueden revelar:

- dudas frecuentes;
- supuestos no explicitados;
- errores de uso;
- límites del método;
- necesidad de ejemplos;
- vocabulario alternativo;
- requisitos funcionales.

Pregunta y respuesta deben conservarse relacionadas, pero como evidencias diferenciables.

No se asumirá que la premisa de la pregunta es correcta.

## 6. Protocolo para recomendaciones externas

Cuando aparezca un libro, paper, autor, aplicación o recurso:

1. registrar exactamente cómo se nombra;
2. conservar el contexto de la recomendación;
3. distinguir recomendación positiva, mención neutral y crítica;
4. marcar nombres dudosos producidos por transcripción;
5. crear una tarea de resolución si la identidad no es segura;
6. no atribuir contenido al recurso sin haberlo consultado.

## 7. Protocolo para ejemplos

Un ejemplo no se generaliza automáticamente.

Debe registrar:

- instrumento;
- periodo;
- timeframe;
- parámetros;
- costes;
- universo;
- reglas;
- resultado;
- propósito pedagógico;
- limitaciones conocidas.

Se distinguirá:

```text
Ejemplo demostrativo
Evidencia empírica
Benchmark
Contraejemplo
Caso de validación
```

## 8. Protocolo para conocimiento práctico y tácito

Las frases del tipo:

```text
“Yo normalmente hago…”
“En caso de duda…”
“Esto en real suele…”
“Nosotros hemos dejado de…”
“La manera más sencilla es…”
```

se capturarán como posibles:

- Practitioner Workflow;
- Expert Judgment;
- Heuristic;
- Best Practice;
- Warning;
- Decision Pattern.

No se descartarán por no contener una fórmula o un componente software.

## 9. Criterios de promoción

Un hallazgo puede promoverse por:

- recurrencia;
- poder explicativo;
- utilidad operativa;
- impacto arquitectónico;
- riesgo;
- capacidad de generar una prueba;
- valor pedagógico;
- necesidad de investigación;
- conexión con varias fuentes.

La recurrencia no es obligatoria para hallazgos singulares críticos.

## 10. No hacer

- No resumir línea por línea como método principal.
- No extraer únicamente lo que encaje en categorías conocidas.
- No convertir automáticamente cada evidencia en Asset.
- No confundir interfaz con requisito.
- No confundir ejemplo con validación.
- No confundir opinión experta con hecho científico.
- No corregir silenciosamente la fuente.
- No eliminar contradicciones.
- No crear un archivo independiente por cada observación.
- No duplicar conocimiento canónico.
- No rellenar campos con conjeturas para cerrar un registro.
- No escribir el libro antes de consolidar.

## 11. Criterio de cierre de una práctica

Una práctica se considera extraída cuando:

- todos los archivos han sido inventariados;
- todas las imágenes han sido inspeccionadas;
- los Evidence Items están anclados;
- los hallazgos dudosos están registrados;
- los Topics han sido descubiertos o actualizados;
- se ha realizado deduplicación;
- las contradicciones permanecen visibles;
- se han propuesto materializaciones sin forzarlas;
- existe trazabilidad desde las propuestas hasta las fuentes.

No es necesario que todos los Evidence Items estén materializados para cerrar la extracción.

