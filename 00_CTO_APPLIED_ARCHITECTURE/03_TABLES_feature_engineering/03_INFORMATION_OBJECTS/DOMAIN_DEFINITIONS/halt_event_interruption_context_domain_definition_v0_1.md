# Halt / Event Interruption Context - Domain Definition v0.1

Status: `domain_definition_v0_1`
Date: `2026-07-20`
Scope: `context_pre_landscape_pre_admission`

Este documento define el dominio semantico `Halt / Event Interruption Context`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona modelos finales.
No autoriza variables para `Market State` ni `Event State`.
No modifica tablas, schemas, builders, contratos ni datasets.

## Nombre Del Dominio

```text
Halt / Event Interruption Context
```

## Que Informacion Intenta Preservar

```text
Dominio que separa interrupciones observables de mercado, como halts, de infraestructura temporal de eventos.
```

## Por Que Este Dominio Merece Existir

```text
La presencia, tipo y recencia de interrupciones alteran radicalmente la interpretacion de precio, liquidez, actividad y outcomes alrededor de eventos.
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
halts__halt_type, halts__is_halted_at_t, halts__minutes_since_halt_start, halts__minutes_since_resume
```

Extension o infraestructura relacionada:

```text
halt clustering, post-resumption state, event window role, event relative time
```

## Tabla Que Aporta Evidencia

```text
006_halts_table, 007_event_windows_table
```

## Decision De Dominio

```text
decision = ready_for_representation_landscape
```
