# Quotes Validators - Modulo 01

## 1. Rol

Este documento define el conjunto base de validators para `quotes_core_v0_1`.

Su funcion es traducir la semantica del contrato y de la policy a verificaciones reproducibles.

La taxonomia exacta de etiquetas y la politica de corte para `quotes` viven en:

- `01_foundations/contract_registry/dataset_contracts/quotes_label_taxonomy_and_cut_policy.md`

## 2. Principio rector

En `quotes`, los validators no deben colapsar todo crossed en corrupcion total.

Deben separar:

- integridad estructural minima del libro;
- crossed leve o micro-ruido;
- crossed contextualizable pero no limpio;
- crossed economicamente demasiado agresivo;
- y explicacion causal externa.

La regla institucional correcta es:

- el validator principal de `quotes` evalua calidad local del libro;
- el contexto externo puede ayudar a explicar;
- pero no debe reescribir por si solo el veredicto local del libro.

Las verificaciones de este documento deben leerse siempre contra:

- `01_foundations/contract_registry/dataset_contracts/quotes_label_taxonomy_and_cut_policy.md`
- `01_foundations/module_contracts/market_session_scope.md`

## 3. Validators minimos requeridos

### schema_validator

Debe verificar:

- presencia de campos requeridos del schema logico;
- parseabilidad de `quote_timestamp`;
- parseabilidad numerica de `bid` y `ask`;
- coherencia basica de claves logicas.

### book_integrity_validator

Debe verificar:

- `bid >= 0`
- `ask >= 0`
- coherencia minima de tamaños cuando existan;
- y materializacion local del libro suficiente para clasificar el caso.

No debe colapsar `ask = 0` en crossed economico material sin separar antes:

- zero-ask structural artifact;
- zero-ask contextual;
- y crossed positivo real con `ask > 0`.

### crossed_severity_validator

Debe verificar:

- presencia de `bid > ask`;
- persistencia del crossed;
- severidad economica del crossed cuando `ask > 0`;
- y escala relativa del episodio dentro del file.

Debe separar como minimo:

- crossed leve o micro-ruido;
- crossed persistente bajo;
- crossed persistente medio o grande;
- crossed duro en files medianos;
- crossed duro extremo.

### timestamp_and_session_validator

Debe verificar:

- parseabilidad de `quote_timestamp`;
- consistencia con la sesion institucional `04:00-20:00 America/New_York`;
- rollover UTC cuando aplique;
- y coherencia minima entre file, fecha de sesion y contenido temporal.

### integerization_and_encoding_validator

Debe verificar:

- patrones de integerization o encoding anomalo que afecten la lectura local del libro;
- columnas o materializaciones que den senal de schema defectuoso;
- y si el caso sigue siendo interpretable tras esa anomalia.

### context_crosswalk_validator

Debe verificar:

- si el caso dispone de contexto en `halts`, `reference`, `news`, `ipos` o `crosswalk`;
- y registrar esa explicacion como capa adicional.

No debe rehabilitar automaticamente el libro.

Su funcion correcta es:

- explicar;
- no absolver.

### exclusion_tail_validator

Debe materializar o verificar el exclusion set duro:

- `medium_file_threshold_edge_hard_many_crosses`
- `high_hard_crossed_10_to_20`

Debe garantizar que esos objetos queden fuera de:

- `backtest_core`
- `backtest_extended`
- `ml_flagged`

Y disponibles para:

- `forensic_only`

## 4. Outputs minimos esperados

Los validators de `quotes` deben poder producir, como minimo:

- clasificacion local `good / review / bad`;
- evidencia del crossed y su severidad economica;
- evidencia de consistencia temporal y de sesion;
- senales de integerization o schema problematico;
- y una capa separada de explicacion contextual externa cuando exista.

Para casos `review` y `bad`, cuando la unidad de analisis lo permita, tambien deben poder producir:

- evidencia inspeccionable por `ticker-date-file`;
- resumen del motivo local del veredicto;
- resumen de contexto externo relevante;
- y soporte para decidir si el caso queda:
  - explicado pero no rehabilitado
  - o confirmado como exclusion dura

## 5. Criterio de aprobacion

`quotes_core_v0_1` pasa validacion institucional minima cuando:

- el schema logico requerido se satisface;
- la integridad minima del libro se sostiene;
- el crossed queda clasificado por severidad y no por intuicion;
- la sesion y el timestamp quedan gobernados bajo el alcance institucional;
- y el contexto externo queda separado del veredicto local del libro.

## 6. Regla final

Un validator de `quotes` correcto no solo detecta episodios raros.

Tambien preserva la interpretacion institucional de que:

- `quotes` es la verdad primaria del libro observado;
- crossed leve no equivale automaticamente a corrupcion;
- contexto explicativo no equivale a libro limpio;
- y la exclusión dura solo debe activarse cuando la calidad local del libro sigue siendo economicamente demasiado agresiva.
