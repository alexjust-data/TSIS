# 01 Foundations Local Rules

Estado: regla local obligatoria para agentes que trabajen dentro de
`01_TSIS_DATA_FOUNDATION/01_foundations`.

## 1. Rol

`01_foundations/` es la capa institucional de gobierno de datos del modulo
`01_TSIS_DATA_FOUNDATION`.

Su funcion es definir, localizar, validar y explicar datasets, vistas,
universos, labels, features, policies, validators, dossiers y contratos.

No es una carpeta para:

- runs pesados;
- parquets grandes;
- outputs promovidos;
- experimentos temporales;
- scripts ejecutables principales;
- ni exploracion historica.

## 2. Autoridad

La autoridad superior sigue este orden:

1. documentos raiz de `C:/TSIS_Data`;
2. `01_TSIS_DATA_FOUNDATION/AGENTS.md`;
3. `01_TSIS_DATA_FOUNDATION/LOCAL_RULES.md`;
4. este documento;
5. contratos, schemas, policies, registries, validators y dossiers vivos dentro
   de `01_foundations`.

Si un documento historico o una nota contradice un contrato vivo de
`01_foundations`, manda el contrato vivo.

## 3. Donde Escribir

Usar la superficie institucional correcta:

- `canonical_schemas/<family>/`: estructura fisica/logica esperada.
- `contract_registry/dataset_contracts/`: identidad, scope y limites del
  dataset.
- `dataset_registry/<family>/`: paths, estado, lineage y artefactos activos.
- `data_consumption_policies/`: allowed/restricted/prohibited consumers.
- `validators/<family>/`: checks obligatorios y criterios de fallo.
- `inspection_dossiers/<family>/`: evidencia, readouts, casepacks y verdicts.
- `data_quality_report/families/`: estado resumido por familia.
- `module_contracts/<topic>/`: semantica transversal, incidentes, runbooks y
  protocolos que cruzan varias superficies.

No crear un nuevo source of truth en una ruta generica si ya existe una
superficie canonica para ese tipo de decision.

## 4. Changelog Local

`01_foundations/CHANGELOG.md` registra el detalle local de cambios en:

- contratos;
- schemas;
- registries;
- policies;
- validators;
- dossiers;
- data-quality reports;
- module contracts;
- protocolos operativos y recovery docs.

El changelog padre `01_TSIS_DATA_FOUNDATION/CHANGELOG.md` sigue siendo
obligatorio cuando el cambio tenga impacto institucional, operativo,
downstream, de reproducibilidad o promocion.

Regla practica:

- detalle local en `01_foundations/CHANGELOG.md`;
- resumen institucional en el changelog padre cuando aplique.

## 5. Regla De Familias

Una familia no puede llamarse terminada si no cumple
`FOUNDATIONS_FAMILY_COMPLETION_STANDARD.md`.

Como minimo deben revisarse estas superficies:

1. `canonical_schemas/<family>/`
2. `contract_registry/dataset_contracts/`
3. `data_consumption_policies/`
4. `dataset_registry/<family>/`
5. `validators/<family>/`
6. `inspection_dossiers/<family>/`
7. `data_quality_report/families/`
8. `module_contracts/` cuando haya semantica transversal
9. README/index updates
10. changelog local y, si aplica, changelog padre
11. visual-inspection pack o waiver explicito

Los porcentajes del README no sustituyen estos gates.

## 6. Regla De Contratos

Todo contrato o protocolo nuevo debe declarar:

- rol;
- scope;
- no-goals;
- source artifacts;
- allowed consumers;
- restricted/prohibited consumers cuando aplique;
- lineage;
- estado;
- validators o gates;
- limites conocidos;
- comandos seguros si es operativo;
- comandos prohibidos si hay riesgo de scope o promocion incorrecta.

Evitar lenguaje ambiguo cuando una frase gobierna consumo downstream.

## 7. Regla De Evidencia

Ninguna conclusion institucional debe depender de memoria conversacional.

Debe poder reconstruirse desde:

- contrato;
- registry;
- policy;
- validator;
- dossier/readout;
- evidence asset;
- run manifest;
- changelog.

Si una decision no puede citar evidencia persistida, aun no esta lista para
gobernar.

## 8. Graphify

Graphify es mapa semantico, no source of truth.

La operacion Graphify de `01_foundations` vive en:

- `GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md`;
- `GRAPHIFY_REFRESH_QUEUE.md`;
- `module_contracts/graphify/`.

No hacer rebuild monolitico por defecto. Usar slices/leaf graphs y registrar
refreshes segun severidad.

## 9. Incidentes Operativos

Incidentes como scope incorrecto, promocion bloqueada, recovery tras caida de
luz o reparaciones de larga duracion deben documentarse en:

```text
module_contracts/<topic>/
```

El documento debe incluir:

- que ocurrio;
- que artefacto queda invalido o restringido;
- que artefacto puede reutilizarse;
- comandos seguros;
- comandos prohibidos;
- gates de cierre;
- recovery si se interrumpe la operacion.

Si el incidente afecta outputs o consumidores, tambien debe quedar en
`01_foundations/CHANGELOG.md` y en el changelog padre.

## 10. Regla Final

`01_foundations` existe para que un inspector humano pueda abrir la carpeta,
seguir el mapa documental y reconstruir el significado institucional sin
preguntar a nadie.

Si una regla, decision o reparacion importa, debe terminar como documento
versionado, contrato, policy, validator, manifest o changelog.
