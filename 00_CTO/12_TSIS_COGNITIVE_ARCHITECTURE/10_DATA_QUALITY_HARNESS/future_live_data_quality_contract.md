# Future Live Data Quality Contract

Fecha: 2026-06-12
Estado: planned contract seed v0.1
Ambito: futuro Data Quality Harness live

## 0. Proposito

Este documento reserva el contrato futuro para convertir la auditoria historica
de `01_foundations` en control diario o intradia de data live.

No es aun contrato operativo.

## 1. Condiciones antes de activarlo

Antes de escribir la version operativa, Data Quality Harness debe:

- reproducir la auditoria historica existente;
- fijar vocabulario canonico de estados;
- definir outputs live;
- definir thresholds por dataset;
- declarar consumers bloqueables;
- producir `run_manifest.json`;
- producir quality report diario o por batch.

## 2. Relacion con contratos compartidos

Este contrato futuro debe cumplir:

- `00_SHARED_HARNESS_KERNEL/harness_toolchain_traceability_contract.md`;
- `00_SHARED_HARNESS_KERNEL/shared_run_manifest_contract.md`;
- `00_SHARED_HARNESS_KERNEL/shared_validation_principles.md`.

## 3. Estado

Pendiente de desarrollo despues de cerrar el modelo offline/replay.
