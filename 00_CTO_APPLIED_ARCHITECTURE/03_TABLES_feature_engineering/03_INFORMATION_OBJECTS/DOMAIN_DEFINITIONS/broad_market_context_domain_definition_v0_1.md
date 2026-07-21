# Broad Market Context - Domain Definition v0.1

Status: `domain_definition_v0_1`
Date: `2026-07-20`
Scope: `context_pre_landscape_pre_admission`

Este documento define el dominio semantico `Broad Market Context`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona modelos finales.
No autoriza variables para `Market State` ni `Event State`.
No modifica tablas, schemas, builders, contratos ni datasets.

## Nombre Del Dominio

```text
Broad Market Context
```

## Que Informacion Intenta Preservar

```text
Objeto que preserva el entorno general de mercado observable as-of que condiciona la interpretacion del instrumento.
```

## Por Que Este Dominio Merece Existir

```text
El comportamiento de small caps puede depender del contexto general: index return, rango, risk-on/off proxy y regimen de mercado disponible en t.
```

## Que Perderia TSIS Si Este Dominio Desapareciera

```text
Perderia contexto que modifica la interpretacion de estados aparentemente equivalentes.
```

## Que No Representa

```text
precio individual, actividad, liquidez, order flow, outcome futuro, decision del scanner, ni permiso administrativo de consumo.
```

## Capacidades Derivables Relacionadas

Core candidatas:

```text
regime__intraday_return, regime__close_to_previous_close_return, regime__high_to_open_return, regime__low_to_open_return, regime__intraday_range_pct
```

Extension o infraestructura relacionada:

```text
regime__bar_coverage_state, risk_on_off_state candidate, volatility proxy candidate, macro/economic context candidates
```

## Tabla Que Aporta Evidencia

```text
012_regime_context_table
```

## Decision De Dominio

```text
decision = ready_for_representation_landscape
```
