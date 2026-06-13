# Shared Validation Principles

Fecha: 2026-06-12
Estado: principles seed v0.1
Ambito: todos los Harness TSIS

## 0. Principio base

Un agente no valida su propio trabajo por opinion.

Valida porque sus artefactos pasan checks estructurales, porque las dudas quedan
registradas y porque los puntos de alto impacto entran en revision humana.

## 1. Capas de validacion

1. Existencia de artefactos obligatorios.
2. Parseo estructural: JSON, CSV, YAML, Markdown esperado.
3. Consistencia cruzada entre manifest, inputs, outputs, reglas y reportes.
4. Checks de dominio: muestra, evidencia, semantica de datos, realismo de
   ejecucion y no promocion indebida.
5. Revision humana para reglas criticas, cambios de doctrina y gates live.

## 2. Decisiones permitidas

- `pass`
- `pass_with_warnings`
- `needs_human_review`
- `fail`
- `blocked`

## 3. Regla de parada

Un Harness debe parar cuando:

- pasa contrato;
- falla contrato;
- necesita revision humana;
- o alcanza el limite de iteraciones definido por su runbook.

No existe "seguir en bucle hasta que parezca terminado" como modo valido.
