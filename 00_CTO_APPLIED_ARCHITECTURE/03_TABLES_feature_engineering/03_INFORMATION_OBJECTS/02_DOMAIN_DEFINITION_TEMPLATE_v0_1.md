# Domain Definition Template v0.1

Status: `domain_definition_template_v0_1`
Date: `2026-07-20`
Scope: `post_semantic_consolidation_pre_object_admission`

Este template se usa para definir un dominio semantico antes de abrir expedientes formales de `Objeto de Informacion`.

No admite Objetos.
No rechaza Objetos.
No selecciona variables finales.
No autoriza consumo en `Market State` ni `Event State`.

## Nombre Del Dominio

```text
<domain_name>
```

## Que Informacion Intenta Preservar

```text
Responder en lenguaje semantico.
No listar columnas todavia.
```

## Por Que Este Dominio Merece Existir

```text
Que informacion preserva este dominio
que no queda preservada de forma suficiente
por otros dominios existentes?
```

## Que Perderia TSIS Si Este Dominio Desapareciera

```text
Que capacidad de descripcion, explicacion, prediccion,
auditoria o investigacion perderia TSIS
si este dominio no existiera?
```

## Que No Representa

```text
Fronteras negativas:
que queda fuera del dominio.
```

## Preguntas Cientificas Que Permite Formular

```text
Pregunta 1
Pregunta 2
Pregunta 3
```

## Candidatos Incluidos

```text
candidate_a
candidate_b
candidate_c
```

## Posibles Objetos Dentro Del Dominio

```text
possible_information_object_a
possible_information_object_b
```

## Posibles Modelos De Representacion

```text
model_a
model_b
model_c
```

## Fronteras Con Otros Dominios

| Dominio vecino | Frontera |
| --- | --- |
| `<domain>` | `<donde termina este dominio y empieza el otro>` |

## Riesgos De Fusion O Division

```text
Que podria estar duplicado.
Que podria necesitar dividirse.
Que podria ser solo una especializacion temporal.
```

## Decision De Dominio

Valores permitidos:

```text
ready_to_define_candidate_object
ready_for_representation_landscape
needs_split
needs_merge
needs_more_evidence
not_a_market_information_domain
```

Decision:

```text
<decision>
```

## Siguiente Paso

```text
<next_step>
```

