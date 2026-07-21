# Short-Side Context - Domain Definition v0.1

Status: `domain_definition_v0_1`
Date: `2026-07-20`
Scope: `external_context_pre_landscape_pre_admission`

Este documento define el dominio semantico `Short-Side Context`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona modelos finales.
No autoriza variables para `Market State` ni `Event State`.
No modifica tablas, schemas, builders, contratos ni datasets.

## Nombre Del Dominio

```text
Short-Side Context
```

## Que Informacion Intenta Preservar

```text
Objeto que preserva informacion observable con lag sobre presion, crowding o restricciones del lado short.
```

## Por Que Este Dominio Merece Existir

```text
La actividad short, days-to-cover, restricciones y crowding pueden cambiar la interpretacion de squeezes, continuidad, fallos y riesgo de ejecucion.
```

## Que Perderia TSIS Si Este Dominio Desapareciera

```text
Perderia contexto externo/as-of necesario para interpretar estados tecnicos que, aislados, pueden tener significados distintos.
```

## Que No Representa

```text
precio, volumen, liquidez, order flow, volatilidad, decision del scanner, outcome futuro, ni dato sin politica as-of.
```

## Preguntas Cientificas Que Permite Formular

```text
Existe contexto externo observable antes de t?  Que antiguedad, relevancia o lag tiene?  Cambia la respuesta del mercado cuando este contexto esta presente?  Debe entrar en core State o solo en extension/context profile?
```

## Capacidades Derivables Relacionadas

Core candidatas:

```text
short__days_to_cover, short__short_volume_ratio
```

Extension/bloqueadas:

```text
short__short_interest_z_WINDOW, short__borrow_availability_state, short__locate_state, short__ssr_state
```

## Tabla Que Aporta Evidencia

```text
011_short_context_table
```

## Decision De Dominio

```text
decision = ready_for_representation_landscape
```
