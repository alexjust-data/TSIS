# Live Source Adapter Topology v0.1

Fecha de creacion: 2026-07-07
Estado: candidate_system_map
Owner layer: `00_CTO/02_SYSTEMS_ENGINEERING/01_INTERFACES_AND_ADAPTERS`

## Proposito

Definir la topologia comun para incorporar fuentes live en TSIS sin contaminar
Data Foundation, research, ML/RL ni execution bridge.

Este documento es arquitectonico. No implementa ningun adapter.

## Principio Central

```text
External source != adapter != captured payload != governed feature/state
```

Cada capa responde una pregunta distinta:

| Capa | Responde | No responde |
| --- | --- | --- |
| External source | que ofrece el proveedor/broker | que debe consumir TSIS |
| Reference library | que evidencia/manual crudo existe | que esta aprobado |
| Source adapter contract | que se permite capturar y como | como operar trades |
| Adapter implementation | como se conecta/captura | que semantica canonica tiene el campo |
| Physical data root | donde queda evidencia materializada | si el dato es model-facing |
| Source parity audit | si el campo existe historico/live | si hay edge |
| Governed state/features | que puede consumir downstream | payload crudo completo |
| Execution bridge | acciones autorizadas bajo contrato | captura de datos general |

## Topologia Canonica

```text
Vendor/Broker/API reference
-> Reference Library entry
-> Systems Engineering interface map
-> Module-owned source adapter contract
-> Module-owned implementation
-> Long-running run contract
-> Physical data root
-> Source parity/certification audit
-> Governed live-compatible state/features
-> Research / ML / RL / monitoring / execution consumers
```

## Ubicaciones Por Responsabilidad

### 1. Referencia Externa

Lugar natural:

```text
C:/TSIS_Data/00_CTO/99_REFERENCE_LIBRARY/<source_name>/
```

Contenido permitido:

- manuales;
- ejemplos oficiales;
- zips del proveedor;
- notebooks exploratorios;
- dumps/transcripts locales si no se versionan;
- notas privadas locales.

No-goals:

- no gobierna produccion;
- no define schemas canonicos;
- no contiene credenciales versionadas;
- no sustituye un contrato de modulo.

### 2. Mapa De Sistema

Lugar natural:

```text
C:/TSIS_Data/00_CTO/02_SYSTEMS_ENGINEERING/01_INTERFACES_AND_ADAPTERS/
```

Contenido permitido:

- mapa de capas;
- ownership de paths;
- safety boundaries;
- decisiones de arquitectura;
- relaciones entre modulo, reference library y data plane.

No-goals:

- no incluye payloads;
- no incluye codigo runtime;
- no declara campos model-facing finales por si solo.

### 3. Contrato De Adapter Live

Lugar natural para SmallCaps live:

```text
C:/TSIS_Data/04_TSIS_webSocket_SmallCaps/01_data_ingestion_live/<vendor_or_broker>/
```

Debe declarar como minimo:

- commands/subscriptions permitidos;
- payload classes esperadas;
- run artifacts obligatorios;
- heartbeat/progress semantics;
- final summary semantics;
- manejo de interrupciones;
- limites read-only o execution-disabled;
- data root fisico.

### 4. Implementacion

Lugar natural:

```text
C:/TSIS_Data/04_TSIS_webSocket_SmallCaps/src/<adapter_name>/
```

Debe seguir el contrato del modulo y escribir evidence/run artifacts de forma
incremental para sobrevivir interrupciones.

### 5. Data Plane Fisico

Lugar natural:

```text
E:/TSIS/<declared_data_root>/
```

Regla:

```text
runtime payloads and large live captures do not live in Git
```

El data root debe tener README o manifest que explique que contiene, quien lo
puede escribir y que artifacts produce.

### 6. Source Parity Gate

Lugar natural para live-compatible features:

```text
C:/TSIS_Data/04_TSIS_webSocket_SmallCaps/01_data_ingestion_live/source_parity_audit/
```

Debe decidir, campo por campo:

- fuente historica;
- fuente live;
- timestamp/cutoff;
- latencia/arrival semantics;
- null/missing behavior;
- si el campo es trainable, live-only, broker-only o forbidden.

## Reglas De Consumo Downstream

- ML/RL no consume payloads crudos sin contrato de state/features.
- Research no promueve live-only fields como historicamente entrenables.
- Execution bridge no se mezcla con ingestion read-only.
- Broker/account telemetry no se copia a evidencias compartidas sin scope.
- Un adapter no redefine Data Foundation ni schemas canonicos historicos.

## Estado Actual

`04_TSIS_webSocket_SmallCaps` es el modulo natural para live ingestion,
streaming state preparation, event routing, execution bridge, risk monitoring y
live exports.

Polygon/Massive tiene evidencia prototipo historica bajo el modulo live.
Broker-specific adapters locales quedan ignorados por Git por defecto salvo que
el usuario apruebe publicar un subset sanitizado.
