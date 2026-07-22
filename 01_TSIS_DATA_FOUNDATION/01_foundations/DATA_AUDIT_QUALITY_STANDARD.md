# Data Audit Quality Standard

## 1. Rol

Este documento fija el estandar generico que deben seguir las proximas auditorias de capas de data dentro de `01_foundations`.

Su objetivo es impedir que futuras auditorias sean menos exigentes que los bloques ya cerrados o avanzados:

- `trades`
- `quotes`
- `daily`
- `daily_adjusted`
- `ohlcv_1m_split_normalized`

Este documento no reemplaza los contratos especificos de cada dataset.
Define el nivel minimo de profundidad, estructura, evidencia y reporte humano que debe existir antes de presentar una auditoria como institucionalmente defendible.

La regla general para decidir si una familia esta terminada dentro de
`01_foundations` vive en:

- `FOUNDATIONS_FAMILY_COMPLETION_STANDARD.md`

Este documento responde:

- cuan profunda debe ser la auditoria;
- que evidencia minima debe existir;
- que debe poder entender un inspector.

`FOUNDATIONS_FAMILY_COMPLETION_STANDARD.md` responde:

- cuando la familia completa, cruzando todas las carpetas de `01_foundations`,
  puede llamarse `human_inspector_ready`.

## 2. Principio Rector

Una auditoria institucional de TSIS no se considera completa porque exista un notebook, un parquet, un grafico o un resultado atractivo.

Debe poder demostrar, con evidencia trazable:

- que se entiende que es la capa;
- que se entiende que no es la capa;
- que se conoce su schema, coverage, lineage y semantica temporal;
- que se separan calidad, coverage, consumo y price view;
- que los casos buenos, condicionados y malos estan explicados;
- que existe un reporte final legible por un auditor humano;
- y que el consumo downstream queda gobernado por policy, no por intuicion.

La regla minima es:

```text
ninguna auditoria futura debe quedar por debajo del nivel de lectura, evidencia y explicacion ya alcanzado por trades, quotes, daily, daily_adjusted y 1m normalizado.
```

Esta regla incluye explicitamente la capa visual. No basta con tener tablas,
manifests y readouts si una familia puede producir imagenes utiles para
inspeccion humana.

Regla visual:

```text
Toda auditoria futura debe producir un visual inspector pack al nivel de
trades/quotes/daily/1m, o documentar un waiver visual explicito y defendible.
```

El waiver visual no puede ser implicito. Debe vivir dentro del dossier de la
familia y explicar por que las imagenes no aportan informacion adicional sobre
estructura, cobertura, calidad, errores o consecuencias de consumo.

Regla adicional:

```text
un veredicto conocido sobre la data no equivale a una familia terminada en 01_foundations.
```

El auditor debe separar siempre:

- `data_quality_verdict`;
- `foundations_completion_status`.

## 3. Cadena De Autoridad Obligatoria

Toda auditoria nueva debe construir o verificar esta cadena:

```text
canonical schema
-> dataset contract
-> taxonomy / cut policy, si aplica
-> consumption policy
-> dataset registry entry
-> validators
-> inspection dossier
-> evidence assets
-> final human audit readout
-> changelog, si cambia estado institucional
```

Ninguna pieza aislada es suficiente.

Reglas:

- un schema no certifica calidad;
- un registry no autoriza consumo por si solo;
- un validator produce senales, no decisiones finales;
- un notebook no sustituye un readout institucional;
- un grafico sin interpretacion no es evidencia institucional;
- una policy no habilita consumidores no mencionados explicitamente;
- una capa piloto no debe leerse como full-universe;
- una muestra no reemplaza conteos poblacionales si el universo es grande.

## 4. Carpetas Y Funcion Esperada

### `canonical_schemas/`

Debe responder:

- cual es la unidad logica;
- cual es el grano;
- cuales son las claves;
- que columnas o campos son obligatorios;
- que aliases fisicos son aceptados;
- que tipos semanticos se esperan;
- que reglas estructurales minimas aplican;
- que formas sentinel existen, si aplica;
- y que no puede inferirse solo desde la forma del dataset.

No debe responder:

- si la data es buena;
- si esta completa;
- si puede entrar a backtest;
- si esta promovida;
- si sirve para ML;
- si no hay leakage.

### `contract_registry/dataset_contracts/`

Debe responder:

- que es el dataset o capa;
- que no es;
- cual es su identidad logica y version;
- que estado institucional tiene;
- que source lineage lo sostiene;
- que coverage declara;
- que quality policy aplica;
- que consumidores estan permitidos o restringidos;
- que limitaciones conocidas existen;
- y que cambios obligan a versionar.

Si existe taxonomia o cut policy, debe declarar:

- unidad exacta de decision;
- ejes separados de clasificacion;
- senales upstream;
- umbrales literales;
- buckets intermedios;
- etiquetas finales;
- traduccion a estados contractuales.

### `data_consumption_policies/`

Debe responder:

- que puede consumir cada pipeline;
- que estados requieren flag;
- que queda en `research_only`;
- que queda en `forensic_only`;
- que queda prohibido;
- que price view debe usarse;
- que condiciones deben viajar downstream;
- y que promocion futura haria falta para abrir consumidores mas sensibles.

Regla:

- las clases de consumidor no son transitivas.
- `backtest_core` no implica `execution_simulator`.
- `ml_primary` no implica `rl_allowed`.
- `research_only` no implica `backtest_extended`.
- `forensic_only` no implica consumo cuantitativo.

### `dataset_registry/`

Debe responder:

- donde vive fisicamente la capa;
- que version o identidad operacional registra;
- que root, layout o manifest la localiza;
- que contrato, schema, policy, validator y dossier la gobiernan;
- que estado de materializacion o promocion tiene;
- y que evidencia sostiene ese estado.

Un manifest puede enlazarse desde el registry.
Un manifest no reemplaza al registry.

### `validators/`

Debe responder:

- que condiciones estructurales se comprueban;
- que condiciones son invalidantes duras;
- que condiciones son warning, review o flag;
- que salidas minimas debe producir el validador;
- que evidencia deja;
- y que cosas no puede concluir por si solo.

Regla:

```text
un validador no debe emitir mas significado del que puede probar.
```

### `inspection_dossiers/`

Debe ser la capa humana de inspeccion.

Debe responder:

- cual es el veredicto institucional;
- que estados existen;
- que masa tiene cada estado;
- que casos explican cada familia;
- que evidencia visual o tabular sostiene la decision;
- que partes pueden consumirse;
- que partes requieren flag;
- que partes quedan excluidas;
- que partes siguen abiertas;
- y que errores metodologicos evita la policy.

El dossier no sustituye schema, contract, policy, registry o validator.
El dossier muestra por que esas piezas son defendibles.

El dossier debe incluir, salvo waiver explicito:

- mapa visual poblacional;
- mapa visual de coverage;
- visuales de calidad/estado;
- visuales de casos buenos o aceptables;
- visuales de casos flagged/review;
- visuales de casos malos o bloqueantes;
- manifest visual reproducible;
- audit de assets visuales.

### `evidence_assets/`

Debe contener artefactos persistidos y trazables:

- manifests;
- tablas CSV o parquet;
- imagenes;
- snapshots JSON;
- summaries;
- run manifests;
- muestras estratificadas;
- filas problematicas;
- auditorias de assets;
- y cualquier output usado por el readout.

Regla:

- ningun asset debe quedar mudo;
- todo asset activo debe estar consumido por un readout, casepack, notebook, builder, contrato o audit summary;
- assets obsoletos deben archivarse con nota o eliminarse.

## 4.1 Analisis Tecnico De La Data En Si

Toda auditoria nueva debe separar claramente cuatro niveles de informacion. Si estos niveles se mezclan, el auditor humano no puede distinguir entre contrato esperado, observacion real, criterio de aceptacion y evidencia.

### Nivel 1: Que estructura debe tener cada file

Debe vivir en:

- `canonical_schemas/<family>/`
- `contract_registry/dataset_contracts/`
- `module_contracts/`, si la familia expone contratos downstream.

Debe especificar, como minimo:

- columnas canonicas;
- columnas obligatorias y opcionales;
- tipos fisicos esperados;
- tipos semanticos esperados;
- unidad de tiempo;
- timezone;
- granularidad;
- clave primaria logica;
- particionado esperado;
- reglas de ordenamiento;
- rango temporal esperado;
- valores nulos permitidos y no permitidos;
- valores sentinela prohibidos;
- aliases aceptados y no aceptados;
- semantica de precio, volumen, size, bid, ask, OHLC, adjustment factors o cualquier campo equivalente.

Este nivel responde: "que deberia contener cada file para ser interpretable".

### Nivel 2: Como se valida automaticamente esa estructura

Debe vivir en:

- `validators/<family>/`
- scripts de inspeccion institucionales cuando el validador aun no este promocionado.

Debe cubrir, como minimo:

- files ilegibles;
- files vacios;
- schemas divergentes;
- columnas faltantes;
- columnas inesperadas;
- tipos incompatibles;
- parsing ambiguo de fechas o timestamps;
- duplicados exactos;
- duplicados por clave logica;
- orden temporal roto;
- rangos imposibles;
- valores negativos o cero donde no apliquen;
- nulos en campos no-null;
- strings vacios o sentinels;
- valores infinitos o NaN no gobernados;
- outliers tecnicos;
- inconsistencias de particion frente al contenido real;
- drift de formato entre vendors, anos, meses, tickers o batches.

Este nivel responde: "como demostramos de forma repetible que el file cumple o falla".

### Nivel 3: Que se encontro al inspeccionar la data real

Debe vivir en:

- `inspection_dossiers/<family>/`
- `inspection_dossiers/<family>/*readout*`
- `inspection_dossiers/<family>/evidence_assets/`

Debe incluir, como minimo:

- inventario poblacional de files inspeccionados;
- conteo de filas por file, ticker, fecha, periodo o particion relevante;
- files vacios;
- files corruptos o no legibles;
- distribucion de columnas reales observadas;
- diferencias de schema entre files;
- null profile por columna;
- empty-string profile por columna cuando aplique;
- duplicate profile;
- outlier profile;
- rango minimo/maximo por campos numericos y temporales;
- ejemplos concretos de casos buenos, condicionados, recuperables y malos;
- lectura humana de por que un caso es aceptable o no;
- impacto downstream de cada defecto.

Este nivel responde: "como esta realmente la data que tenemos".

### Nivel 4: Que conclusion puede usar un auditor humano

Debe vivir en:

- el readout final de la familia;
- el dossier de auditoria promocionado;
- manifests que conecten tablas, graficos y casos con el run.

Debe decir explicitamente:

- si la data es limpia, usable, usable con flags, recuperable o no usable;
- para que consumidores es apta;
- para que consumidores no es apta;
- que defects son ruido tolerable;
- que defects cambian semantica;
- que defects exigen quarantine;
- que defects exigen version nueva;
- que defects son bloqueantes para features, labels, execution, RL o live.

Este nivel responde: "que puede hacer o no hacer TSIS con esta data".

Regla de cierre: ninguna familia debe considerarse auditada solo porque exista schema o coverage. Debe existir analisis tecnico real de contenido: estructura fisica, limpieza, nulos, vacios, formato, duplicados, outliers, rangos, interpretabilidad y ejemplos trazables.

## 5. Estructura Minima De Una Nueva Auditoria

Una auditoria madura debe tender a esta estructura:

```text
inspection_dossiers/<dataset>/
  README.md
  build_<dataset>_inspection_pack.md
  <dataset>_inspection_readout_v0_1.md
  population_evidence_packs/
  good_justification/
  flagged_case_evidence_packs/
  bad_case_evidence_packs/
  coverage_case_evidence_packs/
  family_case_evidence_packs/
  causal_case_evidence_packs/
  visual_inspector_pack/
  evidence_assets/
    technical_profile/
    schema_profile/
    quality_tables/
    population_tables/
    coverage_tables/
    case_manifests/
```

No todas las carpetas son obligatorias para todos los datasets.
Si una carpeta no aplica, el README local debe explicar por que no aplica.

`visual_inspector_pack/` si es obligatoria por defecto. Solo puede omitirse con
un waiver versionado dentro del dossier.

Ejemplos:

- una capa de eventos puede necesitar `causal_case_evidence_packs`;
- una capa de tape o calidad heterogenea puede necesitar `family_case_evidence_packs`;
- una capa con gaps debe tener `coverage_case_evidence_packs`;
- una capa derivada debe tener evidencia de validacion, controles negativos y consumidor real o equivalente.

## 6. Orden Obligatorio Del Reporte Humano

El reporte final para auditor humano debe avanzar de lo general a lo particular.

Orden esperado:

```text
1. rol del dataset o capa
2. estado institucional
3. autoridad documental
4. source lineage
5. unidad logica y unidad de decision
6. file structure and technical profile
7. schema esperado y schema observado
8. coverage y universo esperado
9. price view o temporal semantics, si aplica
10. mapa poblacional
11. taxonomia de estados o familias
12. data cleanliness: vacios, nulos, formatos, duplicados, outliers
13. good / usable / pass justification
14. flagged / review / recoverable evidence
15. bad / exclusion evidence
16. coverage evidence
17. visual inspector pack
18. family casepacks o causal overlays, si aplica
19. validators y checks minimos
20. consumers permitidos y restringidos
21. limitaciones conocidas
22. deudas abiertas
23. veredicto operativo final
```

El auditor humano debe poder entender el estado de la data sin abrir conversaciones previas ni ejecutar notebooks.

## 7. Preguntas Que Todo Reporte Debe Responder

Todo readout final debe responder explicitamente:

- Que data se audito?
- Donde vive?
- Que version o identidad logica tiene?
- Cual es la unidad exacta de decision?
- Que estructura real tiene cada file?
- Que estructura esperada aplica a todos los files de esta familia?
- Que columnas son canonicas, opcionales, derivadas, vendor-specific o prohibidas?
- Que tipos fisicos se observaron y cuales son incompatibles con el contrato?
- Hay files vacios, corruptos o no legibles?
- Hay filas vacias o registros sin interpretacion semantica?
- Hay campos vacios, nulos, NaN, inf, strings vacios o sentinels?
- Hay outliers tecnicos o economicos que cambien la utilidad de la data?
- Hay drift de formato entre tickers, fechas, vendors, anos, meses o batches?
- Existe una tabla de perfil tecnico que permita reconstruir lo anterior sin leer el codigo?
- Cual es el universo o scope temporal?
- Cuanta masa existe?
- Cuanta masa esta sana?
- Cuanta masa esta condicionada?
- Cuanta masa esta excluida?
- Cuanta masa esta pendiente?
- Que problemas dominan?
- Que problemas son cola dura?
- Que problemas son recuperables?
- Que problemas son solo de coverage?
- Que problemas son de semantica o price view?
- Que consumidores pueden usar cada estado?
- Que consumidores no pueden usarlo?
- Que flags deben viajar downstream?
- Que evidencia visual o tabular sostiene cada decision?
- Que no demuestra la evidencia?
- Que queda como deuda futura?

Si el reporte no puede contestar estas preguntas, la auditoria no esta cerrada.

## 8. Modelo De Evidencia Por Grafico, Tabla O Caso

Cada grafico, tabla, caso o asset importante debe incluir:

### Que muestra

Descripcion literal del contenido.

### Responde

Pregunta concreta que permite contestar.

### No responde

Limites de interpretacion.

### Consecuencia

Decision operacional o error metodologico que evita.

Regla:

```text
ninguna imagen debe quedar como decoracion muda.
ninguna tabla debe presentarse como si se explicara sola.
ningun bucket debe justificarse solo por su nombre.
```

## 9. Mapa Poblacional Obligatorio

Toda auditoria sobre un universo grande debe incluir mapa poblacional antes de bajar a casos.

Debe mostrar, cuando aplique:

- conteos por estado;
- conteos por familia;
- distribucion temporal;
- coverage esperado vs presente;
- healthy vs usable;
- missing outputs;
- read errors;
- schema failures;
- flags dominantes;
- severidad por bucket;
- y relacion entre labels heredados y estados finales.

Una muestra visual no sustituye el mapa poblacional.
El mapa poblacional no sustituye los casos forenses.
Ambos deben coexistir si la capa es compleja.

## 10. Good, Review, Recoverable Y Bad

### `good`

Debe explicar:

- por que es usable;
- que warnings residuales puede tolerar;
- que consumidores permite;
- y por que no representa necesariamente toda la masa util.

### `recoverable_with_flag`

Debe explicar:

- que falla o que queda ambiguo;
- por que no es `good`;
- por que tampoco es `bad`;
- que flag debe viajar downstream;
- y que consumidores pueden aceptarlo.

### `review_not_rehabilitated`

Debe explicar:

- por que no se puede promover;
- por que no se condena automaticamente como `bad`;
- que evidencia falta;
- y que trabajo futuro podria rehabilitarlo.

### `bad`

Debe explicar:

- identidad exacta del objeto;
- motivo primario de exclusion;
- evidencia estructural o economica;
- por que no es ruido aceptable;
- por que danaria backtest, ML, execution o inferencia;
- y si se evaluo rehabilitacion.

## 11. Coverage No Es Calidad

Toda auditoria debe separar:

- calidad del dato;
- coverage;
- expected universe;
- present data;
- healthy data;
- usable data.

Un objeto puede ser sano donde existe y tener coverage incompleto.
Un objeto puede tener coverage amplia y calidad mala.

Cuando calidad y coverage entren en conflicto, debe prevalecer la lectura mas restrictiva, salvo policy explicita.

## 12. Price Views Y Semantica Temporal

Si la capa toca precios, retornos, labels, ejecucion o comparacion externa, debe declarar:

- `price_basis`;
- `adjustment_policy`;
- `corporate_action_scope`;
- `time_scope`;
- `consumer_intent`.

Debe distinguir:

- `quotes_raw`;
- `trades_raw`;
- `daily_raw`;
- `split_normalized`;
- `adjusted`;
- `adjusted_proxy`.

Reglas:

- ejecucion y microestructura usan raw book/tape;
- retornos economicos, labels diarios y benchmark usan adjusted;
- reconciliacion usa raw, split-normalized y adjusted_proxy segun la pregunta;
- una comparacion externa no prueba error interno si no se declara la vista externa.

## 13. Capas Derivadas

Una capa derivada no queda validada porque el script corra.

Debe demostrar:

- definicion semantica;
- implementacion correcta;
- controles positivos;
- controles negativos;
- coverage de outputs;
- ausencia de read errors;
- columnas requeridas;
- invariantes;
- evidencia visual o inspectiva;
- consumidor real o prueba equivalente;
- reproducibilidad;
- y trazabilidad documental.

Niveles esperados:

- `Nivel 1 - Definida`
- `Nivel 2 - Implementada`
- `Nivel 3 - Pilotada`
- `Nivel 4 - Auditada`
- `Nivel 5 - Consumida`
- `Nivel 6 - Promovida`

No debe decirse `promovida` si solo existe piloto.

## 14. Sampling Y Casepacks

Cuando el universo sea grande, los casepacks deben generarse por estrategia defendible.

Reglas:

- no cherry-picking;
- no seleccionar solo casos visualmente llamativos;
- no esconder colas;
- cubrir centro y extremos;
- cubrir anos distintos;
- cubrir subfirmas causales;
- dejar manifest reproducible.

Patron recomendado:

- bucket pequeno: enumeracion completa;
- bucket mediano: enumeracion completa si es legible o muestra fuerte;
- bucket grande: muestra estratificada;
- bucket complejo: muestra estratificada por familia, severidad, tiempo y firma.

Todo casepack debe enlazar:

- manifest;
- imagen;
- metadatos;
- decision;
- explicacion;
- y consecuencia de consumo.

Cuando la evidencia principal sea tabular, el casepack debe decir si existe
visual asociado. Si no existe, debe enlazar el waiver visual. Una tabla no debe
ser usada como sustituto silencioso de un visual casepack.

## 15. Builders, Scripts Y Notebooks

Los notebooks sirven para exploracion e inspeccion manual.

Para auditoria institucional final debe existir, cuando sea viable:

- builder documentado;
- script reproducible;
- manifest de outputs;
- instrucciones de regeneracion;
- y readout persistido.

Regla:

- un notebook puede apoyar;
- un notebook no debe ser la unica autoridad.

## 16. Audit De Assets

Toda auditoria que publique casepacks debe comprobar:

- filas esperadas vs filas exportadas;
- manifest vs markdown;
- menu entries vs casos;
- imagenes referenciadas existentes;
- assets faltantes;
- assets extra;
- rutas rotas;
- y estado PASS/FAIL del audit.

Si el audit de assets falla, el dossier no debe presentarse como cerrado.

## 17. Consumer Matrix Obligatoria

El reporte final debe incluir o enlazar una matriz de consumo.

Debe distinguir, como minimo:

- `backtest_core`;
- `backtest_extended`;
- `event_engine`;
- `execution_simulator`;
- `ml_primary`;
- `ml_flagged`;
- `rl_allowed`;
- `causal_only`;
- `research_only`;
- `forensic_only`;
- `live_downstream_candidate`.

Para cada estado debe decir:

- permitido;
- permitido con flag;
- restringido;
- prohibido;
- pendiente de contrato;
- o forensic only.

## 18. Deudas Y Limitaciones

Toda auditoria debe cerrar con una seccion de deuda abierta.

Debe separar:

- deuda metodologica;
- deuda de coverage;
- deuda de source lineage;
- deuda de price view;
- deuda de identidad;
- deuda de validator;
- deuda de consumidor;
- deuda de evidencia visual;
- deuda de materializacion;
- y deuda de documentacion.

No debe esconderse una deuda bajo un veredicto positivo.

## 19. Criterios De Cierre

Una auditoria puede considerarse razonablemente cerrada cuando cumple:

1. contrato o semantica explicita;
2. schema canonico o equivalente;
3. registry entry o localizacion operacional clara;
4. policy de consumo;
5. validators o checks minimos;
6. mapa poblacional;
7. readout humano;
8. casepacks segun familias relevantes;
9. evidence assets trazables;
10. visual inspector pack o waiver visual versionado;
11. audit de assets cuando aplique;
12. builders o scripts reproducibles;
13. deudas abiertas declaradas;
14. changelog si cambia estado institucional.

## 20. Red Flags De Auditoria Incompleta

Una auditoria debe rechazarse o quedar como provisional si ocurre cualquiera de estos casos:

- no declara unidad de decision;
- no declara scope temporal;
- no perfila la estructura tecnica real de los files;
- no distingue schema esperado de schema observado;
- no documenta files vacios, files corruptos o files no legibles;
- no audita nulos, strings vacios, sentinels, formatos, duplicados y outliers;
- no separa coverage de calidad;
- no separa raw de adjusted;
- no tiene mapa poblacional para universo grande;
- solo muestra ejemplos positivos;
- no muestra casos malos;
- no tiene visual inspector pack ni waiver visual explicito;
- usa imagenes sin explicacion;
- no enlaza manifests;
- no prueba que los assets existan;
- no declara consumers;
- no declara flags;
- usa `review` como si fuera `good`;
- usa `bad` sin protocolo de evidencia;
- confunde piloto con full-universe;
- confunde labels con features;
- deja conocimiento solo en notebook o conversacion.

## 21. Plantilla Recomendada De Veredicto Final

Cada readout debe terminar con un veredicto operativo en esta forma:

```text
Dataset / capa:
Estado institucional:
Unidad de decision:
Scope temporal:
Coverage observado:
Estados finales:
Masa usable sin flag:
Masa usable con flag:
Masa forensic only:
Masa pendiente:
Consumers permitidos:
Consumers prohibidos:
Price view aplicable:
Deuda principal:
Veredicto:
```

El veredicto debe ser entendible por un auditor humano no presente en las conversaciones previas.

## 22. Relacion Con Bloques Ya Cerrados

Las proximas auditorias deben usar como referencia minima:

- `daily`: separacion quality axis / coverage axis, hard invalid tail, daily adjusted full-universe.
- `quotes`: calidad local del libro, contexto externo no rehabilitante, audit PASS de casepacks abiertos.
- `trades`: poblacion 57f, familias semanticas, rehabilitacion, casepacks estratificados, raw tape no equivalente a retorno economico.
- `daily_adjusted`: validacion semantica, full-universe coverage, factores positivos, consumidor real `daily_return_labels`.
- `ohlcv_1m_split_normalized`: capa derivada que exige piloto, controles, auditoria full-universe y lectura de madurez.

La vara minima es esa.

## 23. Regla Final

Una auditoria futura solo es aceptable si otro humano o agente puede reconstruir:

- que se audito;
- con que evidencia;
- bajo que contrato;
- con que schema;
- con que validators;
- con que policy de consumo;
- con que manifests;
- con que casos visuales;
- con que deudas;
- y con que veredicto final.

Si el auditor humano no puede entender con detalle como esta la data en cada apartado sin depender de memoria conversacional, la auditoria no esta terminada.
