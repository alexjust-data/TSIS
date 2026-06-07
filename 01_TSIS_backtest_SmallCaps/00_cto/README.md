# 00_cto - SmallCaps Module

`00_cto/` es la memoria tecnica, estrategica y conceptual local del modulo `01_TSIS_backtest_SmallCaps`.

No es el CTO global de TSIS.
No es la autoridad activa del proyecto.
No es una carpeta de data productiva.
No es una carpeta de outputs runtime.

Su funcion es conservar el conocimiento fuente especifico del modulo SmallCaps/backtesting:

- decisiones sobre proveedores de datos;
- inventarios historicos de data;
- visiones de pipeline y arquitectura;
- mappings conceptuales con frameworks externos;
- roadmaps iniciales;
- playbooks discrecionales;
- notas que pueden alimentar futuras taxonomias, labels, features, eventos, simuladores o contratos.

## Autoridad activa

`00_cto/` es fuente, memoria y direccion local.

La autoridad activa del modulo vive en:

- `README.md`
- `AGENTS.md`
- `LOCAL_RULES.md`
- `CHANGELOG.md`
- `01_foundations/`

Regla:

```text
00_cto conserva conocimiento fuente.
01_foundations institucionaliza significado operativo.
```

Si una idea de `00_cto/` pasa a gobernar data, backtest, ML, RL, simulacion, labels, eventos o consumo, debe promocionarse explicitamente a `01_foundations/` o a implementacion gobernada.

## Estructura

```text
00_cto/
  data_source_strategy/
  architecture_blueprints/
  roadmap/
  trading_playbooks/
  reference_artifacts/
  _archive_binary/
```

## `data_source_strategy/`

Contiene memoria local sobre proveedores, endpoints, permisos, familias de datos y tratamiento de data externa.

Uso esperado:

- Polygon/Massive endpoints;
- inventarios historicos de data;
- constancias de tratamiento de raw data;
- criterios fuente para decidir que datasets deben auditarse.

Contenido actual:

- `polygon_massive_endpoints.md`
- `historical_data_inventory.md`
- `polygon_data_treatment_constancia.md`

No sustituye:

- `01_foundations/module_contracts/`;
- `01_foundations/canonical_schemas/`;
- `01_foundations/dataset_registry/`;
- `01_foundations/data_consumption_policies/`.

## `architecture_blueprints/`

Contiene visiones arquitectonicas, blueprints y mappings conceptuales para el modulo.

Uso esperado:

- pipeline objetivo;
- capas del proyecto;
- traduccion de conceptos externos a SmallCaps;
- decisiones fuente antes de convertirse en contrato operativo.

Contenido actual:

- `pipeline_app.md`
- `project_layers.md`
- `pysystemtrade_mapping.md`

No sustituye:

- `PROJECT_OPERATING_SYSTEM.md`;
- `ARCHITECTURE_OVERVIEW.md`;
- `01_foundations/module_contracts/`.

## `roadmap/`

Contiene objetivos, fases y rutas de construccion especificas del modulo.

Uso esperado:

- vision inicial;
- secuenciacion;
- prioridades;
- deuda tecnica local;
- pasos de maduracion.

Contenido actual:

- `module_roadmap_initial_vision.md`

No debe contener research conceptual completo ni playbooks.

## `trading_playbooks/`

Contiene fuente discrecional humana sobre trading SmallCaps.

Uso esperado:

- reglas discrecionales;
- lectura visual;
- setups;
- filtros;
- reglas de entrada/salida;
- contexto humano de mercado;
- material que puede alimentar labels, eventos, features, imitation learning o RL.

No es:

- `strategy_engine`;
- contrato productivo;
- senal activa;
- dataset validado;
- politica de consumo.

Todo lo que se extraiga de aqui debe pasar por promocion explicita antes de llegar a backtest, ML o RL:

```text
playbook humano
-> promotion_candidates.md
-> 01_foundations taxonomy/contract/schema/policy
-> implementacion gobernada
-> dataset o consumidor validado
```

## `reference_artifacts/`

Contiene artefactos de referencia locales preservados.

Uso esperado:

- snapshots ligeros;
- manifests;
- indices que explican una decision historica;
- material que todavia no ha sido absorbido por `01_foundations/`.

Advertencia:

- no debe convertirse en una carpeta de data raw;
- los parquets siguen siendo payload y no deben tratarse como documentacion institucional;
- si un artifact se vuelve fuente oficial, debe moverse o formalizarse en la capa correspondiente.

Contenido actual:

- `reference_listing_status.csv`
- `reference_listing_status.parquet`

## `_archive_binary/`

Contiene binarios preservados que no son autoridad activa.

Uso esperado:

- PDFs derivados;
- exports historicos;
- material auxiliar que conviene conservar localmente.

Contenido actual:

- `pysystemtrade_mapping.pdf`

La fuente activa legible debe ser preferentemente Markdown.

## Regla de promocion

Una pieza de `00_cto/` puede estar en estos estados:

1. `source`: fuente preservada.
2. `interpreted`: lectura o extraccion local.
3. `candidate`: candidata a formalizacion.
4. `promoted`: incorporada a `01_foundations/` o implementacion gobernada.

No se debe saltar de `source` a consumo ML/RL/backtest sin contrato intermedio.

## Regla final

`00_cto/` debe preservar la memoria inteligente del modulo sin contaminar la autoridad activa.

Si algo empieza a gobernar comportamiento real del sistema, debe salir de `00_cto/` y vivir donde corresponda.
