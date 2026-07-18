# 00_CTO_APPLIED_ARCHITECTURE - Mapa Simple

Esta carpeta es un mapa de trabajo de TSIS.

No es donde viven los datos grandes.
No es donde se ejecutan los builders.
No es una carpeta de resultados finales.

Sirve para ordenar las ideas principales del proyecto:

```text
como pensamos el mercado
como convertimos ideas en tablas
como auditamos datos
como conectamos tablas, experimentos y estrategias
```

La forma simple de leerla es esta:

```text
00_EPISTEMOLOGICAL_architecture
  -> 01_REPRESENTATION_MATERIALIZATION_REVIEW
  -> 02_MATERIALIZATION_GOVERNANCE_REVIEW
  -> 04_DATA_Raw_audit
  -> 05_DATA_Live_Source
  -> 03_TABLES_feature_engineering
  -> 06_STRATEGIES_know
  -> 07_NEW_STRATEGIES_by_Experiments
  -> 08_EXPERIMENTS
```

---

## 00_EPISTEMOLOGICAL_architecture

Esta es la base teorica.

Explica como TSIS entiende el mercado:

* que es una representacion;
* que es una feature;
* que es un evento;
* que es un estado;
* que es un outcome;
* como se descubre conocimiento.

En palabras simples:

```text
Aqui definimos el idioma mental de TSIS.
```

No crea tablas. Dice que significan las cosas antes de construirlas.

---

## 01_REPRESENTATION_MATERIALIZATION_REVIEW

Este es el libro que intenta responder:

```text
Como pasamos de una idea teorica a algo fisico?
```

Por ejemplo:

```text
Market State
Event State
Outcome
Decision
```

son ideas del sistema.

Pero para usarlas en codigo necesitamos decidir si deben convertirse en:

```text
tablas
schemas
builders
validators
manifests
```

En palabras simples:

```text
Aqui se explica como una representacion puede llegar a ser una tabla.
```

---

## 02_MATERIALIZATION_GOVERNANCE_REVIEW

Esta carpeta nace porque no bastaba con escribir el libro anterior.

Habia que comprobar si realmente servia.

Entonces aqui hicimos la prueba practica:

```text
Market State
Event State
```

Preguntamos:

```text
Debe existir?
Debe materializarse?
Como se traduce a tabla?
Podemos construir una candidata?
```

En palabras simples:

```text
Aqui convertimos la teoria del libro en un proceso real de decision.
```

Resultado importante:

```text
Event State ya tiene permiso para construir una tabla candidata controlada.
```

Eso no significa tabla oficial. Significa:

```text
podemos construir una version candidata para probar y validar.
```

No significa:

```text
tabla oficial
promocion
fuente de verdad definitiva
```

Esas decisiones solo pueden tomarse despues de completar el proceso de validacion y gobernanza.

---

## 04_DATA_Raw_audit

Aqui se revisa la data original.

Incluye cosas como:

```text
trades
quotes
daily
1 minute
reference
halts
short
additional data
```

En palabras simples:

```text
Antes de construir tablas buenas, miramos si la data de origen es fiable.
```

Esta carpeta ayuda a responder:

```text
Que datos tenemos?
Estan completos?
Tienen errores?
Se pueden usar?
Para que se pueden usar?
```

---

## 05_DATA_Live_Source

Aqui se estudian fuentes live o casi live.

Por ejemplo:

```text
DAS
Interactive Brokers
TradeStation
L2
L3
scanners
```

En palabras simples:

```text
Aqui miramos de donde podria venir la informacion en tiempo real.
```

Se separa de `04_DATA_Raw_audit` porque una cosa es data historica y otra cosa
es data live.

---

## 06_STRATEGIES_know

Esta carpeta es para conocimiento de estrategias.

En palabras simples:

```text
Aqui van ideas o conocimiento sobre estrategias que ya conocemos o queremos ordenar.
```

No deberia confundirse con experimentos validados.

Una estrategia puede empezar como idea, pero para volverse seria debe pasar por
investigacion, experimentacion y evidencia.

---

## 03_TABLES_feature_engineering

Esta es la carpeta de tablas.

Aqui se ordenan las tablas que TSIS tiene o quiere construir:

```text
000_instrument_master
001_market_calendar
002_expected_data_calendar
003_dataset_certification_matrix
007_event_windows_table
008_outcomes_table
016 market_state_table
017 event_state_table
...
```

En palabras simples:

```text
Aqui aterrizan las representaciones en especificaciones de tablas concretas.
```

No todas las tablas estan implementadas.

Algunas son conceptuales.

Otras estan en fase candidata.

Otras han sido certificadas.

Esta carpeta conecta con todo lo anterior:

```text
epistemologia -> representaciones -> gobernanza -> data audit -> tablas
```

Si queremos construir una tabla, normalmente acabamos aqui.

---

## 07_NEW_STRATEGIES_by_Experiments

Esta carpeta es para estrategias nuevas que salen de experimentos.

En palabras simples:

```text
No inventamos una estrategia y ya esta.
La estrategia debe surgir de evidencia obtenida mediante investigacion y experimentacion.
```

Sirve para separar:

```text
ideas conocidas
```

de:

```text
estrategias nuevas nacidas de evidencia experimental
```

---

## 08_EXPERIMENTS

Aqui viven experimentos concretos.

Un experimento intenta responder una pregunta concreta, por ejemplo:

```text
Funciona este detector?
Este evento tiene comportamiento repetible?
Esta representacion ayuda a encontrar edge?
```

En palabras simples:

```text
Aqui se prueban hipotesis de forma reproducible.
```

Los experimentos deberian conectar con:

```text
tablas
features
eventos
outcomes
estrategias
```

---

## Como Se Complementan

La relacion completa es:

```text
00_EPISTEMOLOGICAL_architecture
    define el idioma y la teoria

01_REPRESENTATION_MATERIALIZATION_REVIEW
    explica como una idea puede convertirse en algo fisico

02_MATERIALIZATION_GOVERNANCE_REVIEW
    comprueba y gobierna esa conversion con casos reales

04_DATA_Raw_audit
    revisa si los datos de origen sirven

05_DATA_Live_Source
    estudia fuentes para tiempo real

03_TABLES_feature_engineering
    organiza las especificaciones y el estado de las tablas

06_STRATEGIES_know
    conserva conocimiento de estrategias

07_NEW_STRATEGIES_by_Experiments
    guarda estrategias nuevas nacidas de evidencia experimental

08_EXPERIMENTS
    prueba hipotesis concretas
```

La idea mas importante:

```text
No empezamos por tablas.

Empezamos por significado.

Luego decidimos que merece existir.

Luego comprobamos los datos.

Luego construimos representaciones y tablas candidatas.

Luego investigamos.

La investigacion genera conocimiento.

Parte de ese conocimiento se valida mediante experimentos.

Solo cuando existe evidencia suficiente pueden surgir nuevas estrategias.
```

---

## Fuente de Verdad

Cada carpeta tiene un proposito distinto.

No todas contienen la fuente de verdad del proyecto.

En general:

```text
la autoridad de un documento depende de la gobernanza correspondiente.
```

Una tabla candidata no tiene la misma autoridad que una tabla certificada.

Un documento de trabajo no sustituye a una especificacion oficial.

---

## Sobre Los Zip

Los `.zip` son copias comprimidas de algunas carpetas.

En general:

```text
si existe una carpeta y tambien un zip con el mismo nombre,
trabaja con la carpeta.
```

El zip es una copia o snapshot, no el lugar natural para leer o editar.




