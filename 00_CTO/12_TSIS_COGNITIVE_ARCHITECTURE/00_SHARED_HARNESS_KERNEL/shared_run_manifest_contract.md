# Shared Run Manifest Contract

Fecha: 2026-06-12
Estado: contract seed v0.1
Ambito: todos los Harness TSIS

## 0. Proposito

Este contrato define el minimo comun que debe tener cualquier `run_manifest.json`
emitido por un Harness TSIS.

Un run no es aceptable si no puede reconstruirse desde:

- contrato aplicable;
- inputs declarados;
- toolchain residente en proyecto;
- outputs declarados;
- hashes;
- decision de aceptacion.

## 1. Campos minimos

Todo manifest debe declarar:

```json
{
  "run_id": "...",
  "mode": "pilot|replay|shadow_live|live|manual_repair",
  "status": "pass|pass_with_warnings|needs_human_review|fail|blocked",
  "contract_version": "...",
  "toolchain_traceability_contract": "...",
  "execution_command": "...",
  "toolchain_artifacts": [],
  "input_artifacts": [],
  "output_artifacts": [],
  "non_project_artifacts_used": [],
  "known_limitations": [],
  "acceptance_decision": "..."
}
```

## 2. Reglas

- `toolchain_artifacts` debe apuntar a rutas de proyecto.
- `input_artifacts` debe incluir fuentes, contratos y runbooks relevantes.
- `output_artifacts` debe incluir hashes de outputs no autorreferenciales.
- `run_manifest.json` no se auto-hashea dentro de si mismo.
- cualquier excepcion debe aparecer en `known_limitations`.

## 3. Relacion con otros contratos

Este contrato es comun. Cada Harness puede extenderlo, pero no relajarlo.
