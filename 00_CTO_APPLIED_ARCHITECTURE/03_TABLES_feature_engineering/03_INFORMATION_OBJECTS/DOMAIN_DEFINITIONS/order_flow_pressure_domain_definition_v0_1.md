# Order Flow Pressure - Domain Definition v0.1

Status: `domain_definition_v0_1`
Date: `2026-07-20`
Scope: `cluster_6b_pre_landscape_pre_admission`

Este documento define el dominio semantico `Order Flow Pressure`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona modelos finales.
No autoriza variables para `Market State` ni `Event State`.
No modifica tablas, schemas, builders, contratos ni datasets.

## Nombre Del Dominio

```text
Order Flow Pressure
```

## Que Informacion Intenta Preservar

```text
La presion direccional inferida desde trades y quotes: quien parece iniciar la negociacion, que lado consume liquidez, y si el flujo observado esta desequilibrado.
```

La informacion central es:

```text
direccion e imbalance del flujo negociado, no solo intensidad.
```

## Por Que Este Dominio Merece Existir

```text
Porque dos estados con la misma actividad total pueden tener significados opuestos si la actividad proviene de agresion compradora o agresion vendedora.
```

## Que Perderia TSIS Si Este Dominio Desapareciera

```text
Perderia capacidad para separar actividad neutral de presion direccional, trade intensity de imbalance, y liquidez disponible de liquidez consumida.
```

## Que No Representa

```text
actividad total no direccional, liquidez como coste/disponibilidad, quote state general, precio como movimiento, outcomes futuros, ni decisiones de ejecucion.
```

## Preguntas Cientificas Que Permite Formular

```text
La actividad observada esta dominada por compras o ventas agresivas?  El flujo firmado confirma o contradice el movimiento de precio?  Hay consumo visible de liquidez en un lado del book?  Los eventos producen imbalance direccional o solo volumen neutral?
```

## Candidatos Incluidos

```text
Order Flow Pressure signed flow aggressor imbalance bid-hit / ask-lift OFI candidates liquidity consumption
```

Lectura actual:

```text
Order Flow Pressure = candidato principal a Objeto de Informacion.  Signed flow, aggressor imbalance y OFI son modelos. Pero todos dependen de alignment/classification governance.
```

## Capacidades Derivables Relacionadas

### Capacidades Principales

```text
trades__bid_hit_ask_lift_WINDOW trades__signed_flow_WINDOW trades__aggressor_imbalance_WINDOW trade_quote__ofi_l1_WINDOW trade_quote__alignment_confidence
```

### Capacidades De Soporte

```text
trade_quote__alignment_lag_ms quotes__bid_price quotes__ask_price trades__price trades__size
```

### Capacidades Que No Son Este Dominio

```text
trades__trade_count_WINDOW trades__total_volume_WINDOW quotes__spread_bps_median_WINDOW quotes__top_depth_mean_WINDOW future__future_return_H
```

## Tablas Que Aportan Evidencia

```text
015_microstructure_features_table = superficie candidata para signed flow/aggressor/OFI, pero aun requiere alignment y classifier governance.
```

## Decision De Dominio

```text
decision = ready_for_representation_landscape
```

Motivo:

```text
El dominio es cientificamente distinto, pero su implementacion actual esta mas bloqueada que otros dominios por falta de alignment/classification oficial.
```
