# Naming Authority - Modulo 01

## 1. Rol del documento

Este documento define la autoridad de nombrado para activos institucionales del modulo:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps`

Su objetivo es evitar:

- nombres ambiguos;
- colisiones semanticas;
- duplicacion de conceptos;
- y deriva de convenciones locales no gobernadas.

## 2. Principio rector

Un nombre institucional no es una etiqueta visual.

Es una declaracion semantica minima.

Por tanto, todo nombre institucional debe ayudar a responder:

- que es el objeto;
- a que capa pertenece;
- cual es su alcance;
- cual es su estado de promocion;
- y, cuando aplique, cual es su version logica.

## 3. Que cubre esta autoridad

Este documento aplica a:

- dataset identities;
- contract names;
- policy names;
- schema names;
- validator names;
- manifests;
- promotion states;
- artefactos institucionales promovidos;
- y outputs que aspiren a ser consumidos sistemicamente.

No aplica automaticamente a:

- notebooks historicos heredados;
- nombres legacy preservados en zonas congeladas;
- outputs runtime protegidos ya existentes;
- o evidencia historica que no se vaya a promover.

## 4. Reglas generales de nombrado

Las reglas base son:

- usar nombres descriptivos y compactos;
- evitar nombres personales o contextuales como `alex_fix` o `nuevo_bueno`;
- evitar `final`, `final2`, `definitivo`, `ok_ahora`;
- evitar siglas no definidas por contrato;
- evitar mezclar idioma, estado y version sin orden semantico.

Los nombres nuevos institucionales deben preferir:

- minusculas;
- separacion por guion bajo;
- prefijos de dominio claros;
- y sufijos de version o estado solo cuando aporten semantica real.

## 5. Convenciones por tipo de objeto

### Dataset identities

Formato recomendado:

`<dominio_principal>_<alcance_o_politica>_v<version_logica>`

Ejemplos:

- `quotes_core_v0_1`
- `trades_certified_v0_2`
- `reference_lifecycle_v0_1`

La identidad no debe depender solo del path fisico.

Debe poder vivir en registry y policy de forma estable.

### Contract names

Formato recomendado:

`<dominio>_<tipo_de_contrato>`

Ejemplos:

- `quotes_dataset_contract`
- `trades_policy_contract`
- `universe_schema_contract`

### Policy names

Las policies institucionales deben nombrarse por consumidor o ambito de consumo, no por gusto local.

Ejemplos:

- `backtest_core`
- `backtest_extended`
- `ml_primary`
- `ml_flagged`
- `research_only`
- `forensic_only`

### Schema names

Formato recomendado:

`<objeto>_<nivel>_schema`

Ejemplos:

- `quotes_file_schema`
- `trades_event_schema`
- `universe_snapshot_schema`

### Validator names

Formato recomendado:

`<objeto_o_regla>_<tipo>_validator`

Ejemplos:

- `quotes_schema_validator`
- `dataset_registry_validator`
- `promotion_state_validator`

## 6. Estados de promocion en nombres

El estado de promocion no debe improvisarse en cada equipo o carpeta.

Los estados canonicos deben vivir en `promotion_states/`.

Cuando el nombre de un objeto necesite expresar su estado, debe usar solo estados reconocidos localmente, por ejemplo:

- `exploratory`
- `provisional`
- `validated`
- `institutional`
- `deprecated`
- `archived`

No deben introducirse estados informales como:

- `semi_ok`
- `usable_mas_o_menos`
- `almost_final`
- `casi_certificado`

## 7. Versionado logico en nombres

Cuando un activo institucional cambie semantica, policy o schema de forma material, debe reflejar version logica.

La version debe ser:

- semantica;
- explicita;
- y controlada por contrato, no por intuicion local.

Ejemplos validos:

- `quotes_core_v0_1`
- `quotes_core_v0_2`

Ejemplos a evitar:

- `quotes_new`
- `quotes_latest`
- `quotes_fix`

## 8. Relacion entre naming y legacy

Las zonas congeladas del modulo contienen nombres legacy que no deben reescribirse solo para alinearlos cosmeticamente.

La regla es:

- preservar el naming historico donde ya forma parte de la evidencia;
- introducir naming canonico solo en la nueva capa institucional;
- y mapear equivalencias cuando sea necesario.

## 9. Autoridad de decision

En caso de conflicto, la autoridad de nombrado para activos nuevos institucionales debe venir de:

1. contratos raiz de TSIS
2. `VERSIONING_STANDARDS.md`
3. `01_foundations/module_contracts/`
4. contracts especificos del dominio afectado

No debe decidirse por:

- costumbre local;
- comodidad de notebook;
- o necesidad puntual de una estrategia.

## 10. Regla final

Si un nombre nuevo no permite inferir minimamente su dominio, funcion o estado, no esta listo para promocion institucional.
