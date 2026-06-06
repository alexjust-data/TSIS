# Module Contracts - README

## 1. Rol

Esta carpeta concentra hoy contratos, policies, standards, consumers, snapshots y documentos de madurez institucional del modulo.

Su problema actual no es falta de contenido.

Su problema empieza a ser:

- mezcla de dominios;
- crecimiento de volumen;
- y coste de navegacion para humanos, agentes e inspectores.

## 2. Decision actual

Por ahora:

- no se mueve ningun documento;
- no se rompen rutas;
- no se cambian referencias internas;
- y no se hace una migracion fisica prematura.

En esta fase se introduce primero una **capa de navegacion**:

- indices por dominio;
- indices por categoria transversal;
- y una propuesta de subcarpetas futuras aun vacias.

## 3. Indices por dominio

- [daily_contracts_index.md](./daily_contracts_index.md)
- [quotes_contracts_index.md](./quotes_contracts_index.md)
- [trades_contracts_index.md](./trades_contracts_index.md)
- [1m_contracts_index.md](./1m_contracts_index.md)
- [transversal_contracts_index.md](./transversal_contracts_index.md)

## 4. Estructura futura prevista

La reestructuracion fisica futura, si se promueve, deberia converger hacia carpetas como:

- `module_contracts/daily/`
- `module_contracts/quotes/`
- `module_contracts/trades/`
- `module_contracts/minute/`
- `module_contracts/transversal/`
- `module_contracts/consumers/`
- `module_contracts/governance/`

## 5. Tarea pendiente explicitamente abierta

La migracion fisica **todavia no se ejecuta**.

Queda pendiente porque antes hay que trabajar con cuidado en:

- inventariar referencias cruzadas entre markdowns;
- inventariar enlaces desde notebooks y readouts;
- revisar menciones en `CHANGELOG.md`, `AGENTS.md`, `README.md` e indices;
- y evitar romper rutas que hoy ya funcionan para humanos y para agentes.

La regla institucional correcta es:

- primero anadir navegacion;
- despues mapear dependencias;
- y solo al final, si compensa, migrar fisicamente.

No debe hacerse una reorganizacion cosmetica que deje referencias rotas o documentos huerfanos.

## 6. Compatibilidad de paths y referencias

Mientras no se ejecute una migracion fisica real:

- la ruta canonica vigente de cada documento sigue siendo su path actual en `module_contracts/`;
- cualquier referencia interna o externa a esos paths antiguos sigue siendo valida;
- y no debe reinterpretarse ninguna ruta por intuicion.

Si en el futuro se promueve la migracion fisica a subcarpetas, deberan cumplirse estas reglas:

1. cada documento movido debe tener path antiguo y path nuevo definidos explicitamente;
2. debe existir un mapa de migracion origen -> destino;
3. deben revisarse referencias desde:
   - markdowns
   - notebooks
   - readouts
   - `CHANGELOG.md`
   - `AGENTS.md`
   - indices
   - y cualquier generador automatico
4. no debe darse por hecho que un agente o inspector conoce la migracion oralmente.

La nota de compatibilidad futura que debe asumir cualquier lector o agente es esta:

- si un documento del proyecto se refiere a un path antiguo de `module_contracts`, hay que tratar esa referencia como historicamente valida;
- y, si ya existiera migracion fisica aprobada, hay que resolverla mediante el mapa oficial de migracion, no por heuristica.

Mapa de migracion previsto:

- [module_contracts_migration_map_v0_1.md](./module_contracts_migration_map_v0_1.md)

Pre-auditoria de referencias vigente:

- [module_contracts_reference_pre_audit_v0_1.md](./module_contracts_reference_pre_audit_v0_1.md)

Plan de ejecucion segura para otro agente:

- [module_contracts_migration_execution_plan_v0_1.md](./module_contracts_migration_execution_plan_v0_1.md)

## 7. Criterio de efectividad

Esta carpeta sigue siendo usable hoy, pero ya no es la forma final ideal para crecimiento largo.

La capa de indices existe para:

- mejorar descubribilidad;
- reducir coste cognitivo;
- y preparar una futura reorganizacion sin romper el sistema antes de tiempo.
