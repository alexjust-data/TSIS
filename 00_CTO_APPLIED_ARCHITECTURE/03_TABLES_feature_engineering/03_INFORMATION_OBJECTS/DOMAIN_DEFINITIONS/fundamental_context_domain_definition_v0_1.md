# Fundamental Context - Domain Definition v0.1

Status: `domain_definition_v0_1`
Date: `2026-07-20`
Scope: `external_context_pre_landscape_pre_admission`

Este documento define el dominio semantico `Fundamental Context`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona modelos finales.
No autoriza variables para `Market State` ni `Event State`.
No modifica tablas, schemas, builders, contratos ni datasets.

## Nombre Del Dominio

```text
Fundamental Context
```

## Que Informacion Intenta Preservar

```text
Objeto que preserva contexto fundamental point-in-time sobre estructura economica, financiera o societaria del instrumento.
```

## Por Que Este Dominio Merece Existir

```text
El significado de precio, liquidez, actividad y eventos cambia segun tamano, estructura de capital, disponibilidad de filings y recencia fundamental.
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
fundamentals__filing_age_days, fundamentals__statement_recency_days, fundamentals__statement_value_FIELD
```

Extension/bloqueadas:

```text
fundamentals__ratio_FORMULA, reference__float_pit_state, market cap / shares candidates
```

## Tabla Que Aporta Evidencia

```text
009_fundamentals_asof_table
```

## Decision De Dominio

```text
decision = ready_for_representation_landscape
```
