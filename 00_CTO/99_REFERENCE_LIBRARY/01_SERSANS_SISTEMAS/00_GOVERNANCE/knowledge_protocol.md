# Knowledge Protocol v0.2

## 1. Objetivo

Convertir las fuentes de SersanSistemas en una base de conocimiento gobernada, trazable y reutilizable para:

- comprender el curso sin perder conocimiento explícito o tácito;
- construir el libro vivo;
- contrastar posteriormente el contenido con libros, papers y otras fuentes;
- derivar componentes, decisiones, pruebas y tareas para TSIS;
- conservar hallazgos cuyo destino todavía no se conoce.

Este proyecto no es un resumen del curso ni una colección de notas. Es un sistema de adquisición, consolidación y materialización de conocimiento.

## 2. Principio fundamental

La unidad canónica de captura es el `Evidence Item`.

```text
Source
  ↓
Source Fragment
  ↓
Evidence Item
  ↓
Interpretation / Consolidation
  ├─ Topic
  ├─ Knowledge Record
  ├─ Asset
  ├─ External Reference
  ├─ Open Finding
  ├─ TSIS Decision / Task
  └─ Book View
```

`Topic` y `Asset` siguen siendo estructuras fundamentales, pero no son destinos obligatorios para toda evidencia:

```text
Evidence Item = conserva sin pérdida
Topic         = organiza
Knowledge Record = consolida e interpreta
Asset         = materializa conocimiento reutilizable
TSIS Decision = adopta una implicación
Book View     = comunica el conocimiento
```

## 3. Regla de no pérdida

Durante la captura:

```text
Nada se fuerza.
Todo se ancla a una fuente.
Lo desconocido puede permanecer sin clasificar.
Lo repetido puede consolidarse.
Lo útil puede materializarse.
Lo dudoso queda en revisión.
```

Una evidencia no necesita tener todavía un destino final. Para ser admitida en la capa de captura debe:

1. estar anclada a una fuente identificable;
2. conservar suficiente contexto para entenderla;
3. explicar qué se observó, sin confundirlo con la interpretación;
4. indicar quién realizó la afirmación cuando sea relevante.

## 4. Regla de promoción

Solo un elemento promovido a conocimiento canónico o materializado debe responder:

```text
¿Qué es?
¿Por qué importa?
¿Qué evidencia lo sostiene?
¿Cuál es su alcance?
¿Qué grado de confianza tiene?
¿Dónde puede utilizarse?
¿Qué artefacto o decisión produce, si produce alguno?
```

Ser interesante permite capturarlo; no basta para promoverlo.

## 5. Separación obligatoria de capas

### 5.1 Evidencia

Representa lo que aparece en la fuente:

- fragmento textual;
- afirmación del profesor;
- pregunta de un alumno;
- respuesta;
- imagen;
- gráfico;
- código;
- configuración;
- menú;
- parámetro;
- ejemplo;
- recomendación;
- comportamiento observado en una herramienta.

La evidencia debe conservarse sin convertir automáticamente su contenido en verdad general.

### 5.2 Interpretación

Representa lo que el extractor cree que significa la evidencia.

Debe declararse como interpretación y puede ser:

- provisional;
- discutida;
- contradictoria;
- incompleta;
- pendiente de validación externa.

### 5.3 Conocimiento consolidado

Integra una o varias evidencias relacionadas en una representación estable, deduplicada y revisada.

### 5.4 Materialización

Convierte conocimiento consolidado en un resultado utilizable:

- Asset;
- decisión de ingeniería;
- tarea;
- prueba;
- procedimiento;
- checklist;
- entrada bibliográfica;
- sección del libro;
- pregunta de investigación.

## 6. Evidencia frente a autoridad

Las afirmaciones del profesor se preservarán por su valor experto, pero se distinguirán de:

- hechos verificables;
- fórmulas;
- convenciones de mercado;
- opiniones;
- heurísticas;
- experiencias profesionales;
- preferencias personales;
- hipótesis;
- afirmaciones que requieren contraste.

La autoridad del emisor aumenta el valor de la evidencia, pero no elimina la necesidad de validación cuando una afirmación vaya a convertirse en regla científica, decisión arquitectónica o requisito de TSIS.

## 7. Taxonomía evolutiva

La taxonomía es abierta, versionada y evolutiva.

Las categorías existentes son semillas de clasificación, no límites de extracción. Se admite crear una categoría nueva cuando exista:

- recurrencia suficiente;
- un hallazgo singular de alto valor;
- un riesgo crítico;
- una estructura común entre varios elementos;
- una necesidad clara de recuperación o gobierno;
- un destino que no pueda representarse correctamente con categorías existentes.

La repetición es una señal para promover una categoría, pero no una condición obligatoria.

Los estados `Unknown`, `Unclassified` y `Pending Review` son válidos.

## 8. Principio de no duplicación

No se duplicará conocimiento canónico porque reaparezca en otra práctica.

```text
Nueva evidencia
  ↓
¿Existe un registro canónico equivalente?
  ├─ Sí → enriquecerlo y añadir trazabilidad
  └─ No → crear un candidato nuevo
```

La evidencia nunca se elimina por duplicación: se conserva como soporte adicional. Lo que se consolida es el conocimiento derivado.

## 9. Estados del ciclo de vida

### 9.1 Evidence Item

```text
Captured
Anchored
Interpreted
Reviewed
Consolidated
Rejected
```

### 9.2 Knowledge Record

```text
Candidate
Classified
Validated
Linked
Canonical
Superseded
Rejected
```

### 9.3 Materialización

```text
Proposed
Approved
Materialized
Implemented
Verified
Deprecated
```

Los estados no deben utilizarse para fingir certeza. Un elemento puede permanecer en revisión mientras conserve valor potencial.

## 10. Trazabilidad mínima

Todo elemento promovido debe permitir recorrer:

```text
Materialización
  ↓
Knowledge Record
  ↓
Evidence Item
  ↓
Source Fragment
  ↓
Source
```

Cuando una decisión se apoye en varias fuentes, deben conservarse todas las evidencias relevantes, incluidas las contradictorias.

## 11. Regla de contradicción

Las contradicciones no se resolverán silenciosamente.

Cuando dos evidencias discrepen:

1. se conservan ambas;
2. se registra el alcance de cada una;
3. se indica si la diferencia depende de contexto, fecha, mercado o herramienta;
4. se crea un `Open Finding` si no puede resolverse;
5. solo después de revisión se adopta una posición canónica.

## 12. Control contra la acumulación infinita

La apertura de captura no autoriza una colección ilimitada de notas sin gobierno.

El control se realiza mediante:

- anclaje obligatorio;
- revisión por lotes;
- deduplicación;
- consolidación;
- caducidad de candidatos sin valor;
- rechazo explícito;
- separación entre evidencia y conocimiento canónico;
- materialización solo cuando existe utilidad demostrable.

Una observación aislada puede conservarse como evidencia sin convertirse en un documento independiente.

## 13. Regla sobre el libro

El libro no es la fuente canónica. Es una vista narrativa derivada de conocimiento consolidado y evidencia trazable.

Cada afirmación técnica relevante del libro debe poder enlazarse con:

- evidencia del curso;
- fuentes externas utilizadas para contrastarla;
- decisiones específicas de TSIS, cuando existan.

## 14. Regla sobre TSIS

Nada observado en SersanSistemas se convierte automáticamente en requisito de TSIS.

Debe distinguirse:

```text
Lo que muestra la fuente
Lo que inferimos
Lo que proponemos
Lo que TSIS aprueba
Lo que finalmente se implementa
```

Esta separación evita confundir ingeniería inversa de TradeStation, experiencia profesional del profesor y arquitectura aprobada para TSIS.

