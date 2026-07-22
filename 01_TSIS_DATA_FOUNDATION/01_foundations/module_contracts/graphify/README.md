# Graphify Governance - Modulo 01 Foundations

## Rol de esta carpeta

Esta carpeta gobierna como debe usarse Graphify para `01_foundations` y para
la transicion desde auditoria/certificacion historica hacia tablas
institucionales de CAPA 1.

La operacion de build y refresco vive en la raiz del scope:

```text
01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_foundations/.graphifyignore
```

Esta carpeta define la metodologia institucional, no el runtime del build.

No contiene outputs de Graphify.
No contiene `graphify-out/`.
No contiene grafos manuales.

Contiene contratos de trabajo para que humanos y agentes sepan:

- que grafos independientes construir;
- que corpus entra en cada grafo;
- que corpus queda excluido por defecto;
- como separar mapa semantico, evidencia auditada y profiling fisico de datos;
- y como pasar desde arquitectura hacia tablas reales sin inventar source of
  truth desde una conversacion.

## Autoridad

La autoridad operativa de esta carpeta es:

```text
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts
```

La autoridad de Graphify como herramienta se limita al flujo oficial de
Graphify: la skill/CLI debe producir los outputs. Ningun agente debe escribir
`graph.json`, `GRAPH_REPORT.md` o `graph.html` manualmente y presentarlos como
Graphify oficial.

## Modo operativo sin APIs

TSIS no asume APIs externas disponibles para Graphify.

Regla:

```text
Sin GEMINI_API_KEY/GOOGLE_API_KEY no se pide otra API.
```

Para corpus de CAPA 1 con markdown, contratos, policies, dossiers, papers o
imagenes, el flujo esperado en Codex es usar la skill Graphify con
subagentes/host agent para la extraccion semantica. Un `graphify update` CLI
code-only o AST-only no prueba cobertura semantica de esos documentos.

Antes de usar un grafo para justificar tablas, el agente debe comprobar en su
`BUILD_MANIFEST.md`:

- version instalada de Graphify;
- fuente/version de la skill usada;
- upstream de referencia;
- modo sin APIs;
- modo de extraccion semantica;
- corpus exacto cubierto;
- diagnostics.

Si falta esa metadata, el grafo puede ser util como ayuda de navegacion, pero
no debe tratarse como baseline institucional completo.

## Documentos activos

- `data_foundation_graph_and_table_design_protocol.md`

## Regla principal

Graphify es mapa semantico.

No es:

- profiler de parquet/CSV;
- sustituto de contratos;
- source of truth de schemas;
- prueba de calidad de datos;
- ni mecanismo para decidir tablas solo desde arquitectura.

La decision correcta para CAPA 1 requiere:

```text
arquitectura 00_CTO
  + contratos 01_foundations
  + auditoria/certification
  + profiling fisico de datos reales
  -> tabla institucional justificada
```

## Grafos esperados

La construccion futura debe separar, como minimo:

```text
data_foundation_root_graph
foundations_authority_graph
certification_decisions_graph
reference_identity_graph
daily_ohlcv_graph
microstructure_quotes_trades_graph
additional_fundamentals_news_graph
```

Estos nombres no son carpetas. Son nombres de grafos/slices oficiales.

No construir un unico grafo gigante de todo `01_foundations` ni de todo
`00_data_certification` salvo instruccion explicita y justificacion tecnica.

La cobertura completa de `01_foundations` se consigue por combinacion de leaves
semanticos, no por un escaneo monolitico inicial.

## Runtime

`graphify-out/` es runtime reconstruible y esta ignorado por Git en TSIS.

Si un build se considera relevante, el resultado operativo puede existir en
`graphify-out/`, pero la memoria institucional debe quedar aqui como:

- protocolo;
- scope de corpus;
- manifest de build, si se promueve;
- fecha;
- commit;
- Graphify version;
- ruta del output runtime;
- y decision de uso.

## Regla final

Un agente nuevo debe leer primero:

1. `../../GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md`;
2. `../../GRAPHIFY_REFRESH_QUEUE.md`;
3. este `README.md`;
4. `data_foundation_graph_and_table_design_protocol.md`;
5. `../README.md`;
6. `../auditoria_and_certification_source_hierarchy.md`;
7. `../data_storage_topology_and_target_state.md`;
8. los contratos concretos de la familia que vaya a tocar.

Despues puede decidir si corresponde construir o actualizar un grafo.
