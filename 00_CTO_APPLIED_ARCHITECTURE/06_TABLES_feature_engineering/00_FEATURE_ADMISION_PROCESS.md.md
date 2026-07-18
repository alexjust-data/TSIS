**PLANTILLA**

ESPECIFICACIÓN Y CRITERIOS DE ADMISIÓN  
DE `OBJETOS DE INFORMACIÓN`  
PARA LA REPRESENTACIÓN DEL ESTADO
=== 

Status: `template_v0_4_information_driven`  
Date: `2026-07-17`  

Usar una copia de esta plantilla para cada `Objeto de Información` candidato
a formar parte de la representación del estado.   
* Este documento ***no diseña tablas***.    
* Sí decide si una determinada información merece formar parte del estado del mercado.  
* No debe repetir contratos, schemas ni manifests.  
* Sí debe referenciar los documentos, contratos, tablas, artefactos y literatura que justifican su existencia.  

**Qué es este documento**

Es un proceso reproducible para identificar, justificar y representar  
`objetos de información` que pueden formar parte del estado del mercado.  

Las tablas y sus atributos serán una consecuencia de ese proceso.

Responde:

```
¿Qué objeto de información existe?  
¿Por qué existe?  
¿Cómo se representa?  
¿Qué variables lo implementan?  
¿Dónde vive?  
¿Quién lo consume?  
¿Merece formar parte del estado?  
```

## Filosofía

Pregunta inical

```
¿Qué información necesita conocer el agente
para representar correctamente el estado del mercado?
```

No diseñamos variables.  
Una variable no tiene valor por sí misma.   
Su valor depende exclusivamente de la información que representa dentro del *estado* del mercado.  

Diseñamos representaciones físicas de **objetos de información** del mercado.



**Concepto: `Objeto de Información` :** 
```
Representación de una propiedad observable del mercado:

- que aporte conocimiento nuevo sobre el estado del mercado
  en un decision_timestamp.

. que ayude a representar su estado de forma más completa
  para tomar una decisión óptima.
```
Una variable no entra en TSIS porque sea un indicador conocido.  
Una variable entra únicamente si ayuda a preservar `información` relevante del mercado para la toma de decisiones. 

El objetivo no es construir muchas variables.  
El objetivo es construir la **representación mínima del mercado** que conserve la máxima información útil.


Cada vez que alguien quiera añadir una variable, la primera pregunta debería ser:
```
¿Esta variable incorpora información nueva sobre el estado del mercado
o solo es otra forma de representar información que ya tenemos?
```

**Ejemplos:**
```
VARIABLES:
- Spread
- Depth
- Quote Count
- OFI
- Microprice

Pero juntas representan INFORMACION:
- Liquidez instantánea.
```

```
VARIABLES:
- Gap
- Premarket Volume
- Relative Volume
- Float
- News

Pero juntas representan INFORMACION:
- Potencial de expansión.
```

```
VARIABLES:
- Return 1m
- Slope
- Higher High
- VWAP Distance

Pero juntas representan INFORMACION:
- Momentum.
```

**Hay tres niveles**

Nivel 1 
```
Objeto de INFORMACION (Concepto científico) :
- Liquidez
- Participación
- Momentum
- Régimen
- Contexto
- Presión compradora
- Agresividad
```
Nivel 2
```
VARIABLES (Representación física de la INFORMACION) :
- Spread
- Gap
- RVOL
- Float
```

Nivel 3 

```
ESTADO (Toda la INFORMACION en un momento t): 
- Liquidez + 
- Participación + 
- Momentum + 
- Régimen + 
- Contexto + 
...
```

**Proceso inicial**

Te has de preguntar:

```
¿Qué "información" del mercado todavía no está representada?
¿Y cómo podemos representar esa información?
```
Ejemplo

```
---
Información : La liquidity
---
Representación:
- Spread
- Quoted Depth
- Dollar Volume
- Microprice
- OFI
- Bid Ask Imbalance
```

* No elegimos variables.  
* Elegimos información.  
* Después buscamos la representación mínima de esa información.

**Proceso completo**

```
Information Families
↓
Information Objects (Concepto científico)
↓
Variables (Representación)
```
Ejemplos

```
FAMILIA:
- Microstructure

INFORMACION  (Concepto científico): 
- Liquidity

VARIABLES (Representación) :
- Spread
- Depth
- Quote Count
- OFI
- Microprice
```
```
FAMILIA:
- Participation

INFORMACION  (Concepto científico): 
- Trading Activity

VARIABLES (Representación) :
- Relative Volume
- Trade Count
- Dollar Volume
- Turnover
```
```
FAMILIA:
- Price Structure

INFORMACION  (Concepto científico): 
- Momentum

VARIABLES (Representación):
- Slope
- Returns
- VWAP Distance
- HH HL Structure
```

**Concepto final**

**El significado no está en una variable aislada**, sino en la `información`que emerge de una o varias variables conjuntamente.   
Las tablas no deberían preguntarse "¿qué columnas añadimos?", sino "**¿qué información necesitamos preservar?**"   
y solo después decidir cuál es la representación física mínima y más robusta para conservar esa información.

Arquitectura

```
Mercado
↓
Fenómenos - ¿Qué información existe?
↓
Objeto de Información - ¿Cómo representamos esa información?
↓
Representación Física - ¿Qué variables implementan esa representación?
↓
Tablas
↓
Market State - ¿cómo está el mercado en un timestamp?
↓
Event State - ¿cómo está el mercado respecto a un evento?
```

## Proceso de admisión

```
Nuevo "Objeto de Información" candidato
↓
¿Qué queremos representar?
↓
¿Qué fenómeno del mercado representa?
↓
¿Qué significado tiene?
↓
¿Por qué merece existir?
↓
¿Existe evidencia científica?
¿Qué hipótesis científica representa?
¿Qué preguntas científicas permite responder?
↓
¿Qué consumidores necesitan esta Objeto de Información?
↓
¿Cuál es la representación mínima de esa Objeto de Información en variables?
¿Qué variables necesitamos?
↓
¿Qué atributos físicos la implementan?
↓
¿Existe ya otra representación equivalente?
↓
¿Puede calcularse legalmente en decision_timestamp?
↓
¿Cuál es su coste computacional?
↓
¿Cuánto ruido introduce?
↓
¿Cuál es su ganancia informativa?
↓
¿Debe admitirse dentro de la representación del estado?
```


# Objeto de Información

## Nombre

### Familia

```text
<Nombre de la familia>
```
Ejemplo
```
Familia : Microstructure
Objeto : Liquidity
```
```
Familia : Price Structure
Objeto : Momentum
```


### Información que se desea preservar

```text
¿Qué Objeto de Información del mercado queremos conservar?
```


### Fenómeno del mercado observado

```text
¿Qué fenómeno observable describe?
```


### Hipótesis científica

```text
¿Qué hipótesis representa?
```


### Justificación científica

```text
¿Por qué esta Objeto de Información merece formar parte del estado del mercado?
```


### Preguntas científicas

```text
¿Qué preguntas permite responder?
•
•
•
```

## Evidencia científica

Literatura relevante:

```text
papers
libros
autores
referencias
```

### Representación propuesta

#### Variables mínimas

```text
Variable 1
Variable 2
Variable 3
```

No listar variantes redundantes.  
Solo el conjunto mínimo que preserve esta Objeto de Información.  

#### Variables descartadas


### Representación equivalente

```text
¿Existe otra familia o variable que represente prácticamente la misma Objeto de Información?

Si existe:

¿Debe reutilizarse?
¿Debe eliminarse alguna variable?
```

### Pérdida de información

```
¿Qué información se pierde si eliminamos este objeto?
```

### Tablas donde debe vivir

```text
Tabla principal
Tablas consumidoras
Tablas derivadas
```


### Consumidores

```text
Market State
Event State
Scanners
Pattern Mining
Clustering
Machine Learning
Imitation Learning
Offline RL
Decision Transformer
AlphaEvolve
Execution
Risk Engine
```

### Legalidad temporal

```text
¿Puede conocerse completamente en decision_timestamp?
¿Necesita as-of?
¿Existe riesgo de leakage?
```

### Evaluación técnica

### Complejidad del estado
Una variable puede ser barata pero aumentar mucho :
* dimensionalidad
* correlacion
* overfitting

### Estabilidad temporal

```
¿Esta representación
es estable
entre distintos regímenes?
```


### Ganancia informativa esperada

```text
¿Qué incertidumbre reduce?
```

---

### Decisión

```text
Aceptada
Aceptada con restricciones
Pendiente de evidencia
Rechazada
```

Justificación:

```text
...
```

### Condiciones de revisión futura

Ejemplo

```
Revisar si aparece L3.
Revisar cuando exista Depth real.
Revisar con OFI real.
Revisar tras nuevos papers.
```

## Referencias TSIS

```text
Contratos
Schemas
Builders
Validators
Tables
Artifacts
Research
README
Otros documentos relacionados
```

