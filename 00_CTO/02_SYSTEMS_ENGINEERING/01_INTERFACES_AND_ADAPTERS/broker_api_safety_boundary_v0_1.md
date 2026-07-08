# Broker API Safety Boundary v0.1

Fecha de creacion: 2026-07-07
Estado: candidate_policy
Owner layer: `00_CTO/02_SYSTEMS_ENGINEERING/01_INTERFACES_AND_ADAPTERS`

## Proposito

Definir el limite de seguridad para cualquier API de broker o plataforma live
conectada a TSIS.

La regla base es:

```text
read-only/data-only by default
```

Cualquier capacidad de ordenes, cancels, replaces, locates, route actions o
cambios de cuenta requiere contrato separado, aprobacion explicita y entorno
controlado.

## Separacion De Capas

```text
live data capture
!= execution bridge
!= order router
!= risk monitor
!= account operations
```

Una app de captura puede leer datos, subscriptions, status y telemetria permitida.
No debe ejecutar acciones de trading por accidente.

## Default Permitido

Por defecto, un broker/source adapter puede implementar solo capacidades de
observacion si su contrato lo permite:

- conectividad TCP/socket;
- handshake no sensible;
- subscriptions de market data;
- queries read-only de symbol status;
- route/status read-only si no revela secretos no necesarios;
- transcript redacted;
- heartbeat/progress;
- raw event logging;
- final summary.

## Default Bloqueado

Quedan bloqueados por defecto:

- new orders;
- cancels;
- replaces;
- complex orders;
- short locate orders/actions;
- route actions;
- account-modifying operations;
- credential persistence;
- automatic login with secrets unless a future contract lo autorice;
- cualquier comando que pueda cambiar posicion, riesgo, ordenes o cuenta.

## Secretos Y Telemetria Sensible

No se debe escribir en Git ni en evidencia compartida:

- passwords;
- tokens;
- account IDs si no estan redacted;
- buying power/account balances si no son necesarios para el scope;
- private routes/configs sensibles;
- screenshots con informacion de cuenta;
- transcripts con credenciales o datos privados.

Si una captura necesita account telemetry, el contrato debe declarar:

- por que se captura;
- que campos se permiten;
- como se redacted;
- donde se escribe;
- quien puede consumirla;
- como se separa de market-data evidence.

## Long-running Safety

Todo run largo debe escribir progreso incremental:

- pre-manifest antes de capturar;
- pid/process manifest si aplica;
- heartbeat mientras corre;
- transcript/event log append-only;
- summary final si termina limpio;
- run id unico;
- no overwrite del run interrumpido.

Si se corta la luz, se conserva lo ya flushed y el siguiente intento debe usar
nuevo run id o una politica explicita de resume. No se debe sobreescribir una
captura parcial sin decision consciente.

## Promotion Gate

Una integracion broker/API no puede alimentar state/features model-facing hasta
que existan:

- contrato de captura;
- data catalog o source inventory;
- root fisico declarado;
- policy de secretos;
- source parity/cutoff semantics;
- tests/smoke o evidencia minima;
- documentacion de interrupciones y final summary.

## Relacion Con Execution

Este documento no habilita ejecucion.

La ejecucion pertenece a boundaries futuros como:

```text
02_TSIS_webSocket_SmallCaps/05_execution_bridge/
02_TSIS_webSocket_SmallCaps/06_risk_monitor/
```

Hasta que esos contracts existan y esten aprobados, el trabajo en APIs de broker
se interpreta como data capture/read-only.
