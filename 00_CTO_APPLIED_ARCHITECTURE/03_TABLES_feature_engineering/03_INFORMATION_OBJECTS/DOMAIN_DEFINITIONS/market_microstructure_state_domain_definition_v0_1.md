# Market Microstructure State - Domain Definition v0.1

Status: `domain_definition_v0_1`
Date: `2026-07-20`
Scope: `cluster_6a_pre_landscape_pre_admission`

Este documento define el dominio semantico `Market Microstructure State`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona modelos finales.
No autoriza variables para `Market State` ni `Event State`.
No modifica tablas, schemas, builders, contratos ni datasets.

## Nombre Del Dominio

```text
Market Microstructure State
```

## Que Informacion Intenta Preservar

```text
El estado observable del top-of-book y del tape que condiciona la interpretabilidad del mercado en ventanas temporales declaradas.
```

Incluye informacion sobre:

```text
quote availability, two-sidedness, locked/crossed state, quote update intensity, quote staleness/lifetime, top-of-book condition, y calidad/estructura observable del tape cuando afecta interpretacion.
```

No es principalmente:

```text
liquidez como coste/facilidad, actividad negociada, presion direccional, evento regulatorio, outcome, ni quality gate administrativo.
```

## Por Que Este Dominio Merece Existir

```text
Porque el mismo precio, volumen o spread no significa lo mismo si el book esta estable, stale, locked, crossed, one-sided o con condiciones microestructurales deterioradas.
```

## Que Perderia TSIS Si Este Dominio Desapareciera

```text
Perderia capacidad para saber si una observacion intradia es interpretable bajo condiciones normales del top-of-book/tape, o si debe tratarse como contexto microestructural especial.
```

## Que No Representa

```text
coste esperado de ejecucion como foco principal, profundidad como liquidez completa, signed flow/agresion, volumen como participacion, halts como evento regulatorio, outcomes futuros, ni permiso administrativo de consumo.
```

## Preguntas Cientificas Que Permite Formular

```text
El book esta two-sided y estable?  Hay locked/crossed states relevantes?  Las quotes se actualizan a ritmo suficiente?  La observacion de price/liquidity/activity es interpretable dado el estado microestructural?  Los eventos o candidatos ocurren bajo microestructura normal o deteriorada?
```

## Candidatos Incluidos

```text
Market Microstructure State quote condition top-of-book state locked/crossed state quote update state quote staleness / lifetime microstructure interruption partial
```

Lectura actual:

```text
Market Microstructure State = candidato principal a Objeto de Informacion.  Quote condition / locked-crossed / update/staleness = modelos internos.  Halts/interruption = frontera con Halt Context.
```

## Capacidades Derivables Relacionadas

### Capacidades Imprescindibles

```text
quotes__two_sided_rows_WINDOW quotes__locked_rows_WINDOW quotes__crossed_rows_WINDOW quotes__locked_ratio_pct_two_sided_WINDOW quotes__crossed_ratio_pct_two_sided_WINDOW quotes__quote_count_WINDOW
```

### Capacidades Complementarias

```text
quotes__quote_update_rate_WINDOW quotes__staleness_WINDOW quotes__lifetime_WINDOW quotes__top_depth_mean_WINDOW trades__duplicate_exact_ratio_pct_WINDOW trades__off_regular_session_ratio_pct_WINDOW
```

### Capacidades Fronterizas

```text
quotes__spread_bps_median_WINDOW trade_quote__ofi_l1_WINDOW halts__is_halted_at_t quality__coverage_ratio
```

Lectura:

```text
spread/depth pueden pertenecer a Liquidity. OFI pertenece mejor a Order Flow Pressure. Halt pertenece a Halt Context. Coverage pertenece a Quality/Governance.
```

## Tablas Que Aportan Evidencia

```text
015_microstructure_features_table = quotes, locked/crossed, two-sided rows, update/staleness candidates, and tape quality context.  006_halts_table = interrupciones reguladas como frontera, no core microestructura continua.
```

## Decision De Dominio

```text
decision = ready_for_representation_landscape
```

Motivo:

```text
El dominio preserva informacion microestructural distinta de liquidez, actividad y order flow direccional.
```
