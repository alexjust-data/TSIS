# Validators

`validators/` contiene los contratos de validacion institucional de los datasets y capas de `01_foundations`.

Un validador, en esta carpeta, no significa necesariamente "script ejecutable". Significa contrato reproducible de validacion: que debe comprobarse, con que unidad de analisis, que salidas minimas deben emitirse, que separa `good`, `review`, `bad` o estados recuperables, y que evidencia hace falta antes de permitir consumo, promocion o cierre documental.

## Rol dentro de 01_foundations

Los validadores traducen a controles concretos lo que ya definen otras piezas:

- `canonical_schemas/`: estructura esperada de columnas, tipos logicos, claves y semantica de campos.
- `contract_registry/dataset_contracts/`: contrato del dataset, alcance, version, invariantes y obligaciones.
- `data_consumption_policies/`: quien puede consumir el dataset y bajo que condiciones.
- `dataset_registry/`: identidad operacional, ubicaciones, estado de promocion y evidencias asociadas.
- `inspection_dossiers/`: lectura empirica, casos buenos, casos malos, readouts, paneles y cierre forense.
- `module_contracts/`: reglas transversales de autoridad, evidencia, rehabilitacion, validacion por capas y semantica institucional.

Por tanto, `validators/` no sustituye a esas carpetas. Es el puente entre la definicion documental y la comprobacion objetiva.

## Que debe responder un validador

Cada documento de validacion debe dejar claro:

1. Que dataset o capa gobierna.
2. Que contrato, schema, policy y registry entry aplica.
3. Cual es la unidad de validacion: fila, fichero, ticker-dia, ticker-mes, dataset completo, universo temporal, capa derivada.
4. Que inputs necesita para ejecutarse o auditarse.
5. Que condiciones son invalidantes duras.
6. Que condiciones son de revision, bandera, recuperacion o consumo limitado.
7. Que salidas minimas debe producir.
8. Que evidencia debe quedar trazable.
9. Que significa pasar la validacion.
10. Que cosas no puede concluir el validador por si solo.

La regla central es: un validador no debe emitir mas significado del que puede probar.

## Que no es esta carpeta

`validators/` no es:

- un schema canonico;
- una politica de consumo;
- un dossier de inspeccion;
- un changelog;
- una prueba suficiente de que un dataset es productivo;
- una explicacion completa de un caso `bad`;
- una autorizacion automatica para ML o backtest.

Un dataset puede tener schema conforme y seguir sin ser consumible. Tambien puede tener warnings y ser consumible con flags, si la politica de consumo y la evidencia lo permiten.

## Autoridades que gobiernan validators

Los documentos de esta carpeta deben leerse junto con:

- `module_contracts/semantic_authority.md`
- `module_contracts/layer_validation_standard_v0_1.md`
- `module_contracts/bad_evidence_and_rehabilitation.md`
- `module_contracts/evidence_model.md`
- `module_contracts/inspection_dossier_model.md`
- `module_contracts/dataset_contract_template.md`

La autoridad semantica impide usar terminos como `bad`, `good`, `recoverable`, `review_not_rehabilitated` o `promoted` de forma informal.

La validacion por capas impide declarar una capa derivada como validada solo porque existe output en disco o porque un script termino.

## Estructura actual

La estructura actual es:

```text
validators/
  daily/
    daily_validators.md
  ohlcv_1m/
    ohlcv_1m_raw_validators.md
  quotes/
    quotes_validators.md
  trades/
    trades_validators.md
```

La carpeta usa nombres orientados al dataset o familia de dataset. Cuando el nombre fisico del dataset sea mas explicito que el alias operativo, debe preferirse el nombre fisico en nuevos documentos: por ejemplo `ohlcv_1m`, `ohlcv_1m_split_normalized`, `ohlcv_daily`, `ohlcv_daily_adjusted`.

## Capas de validacion

Los validadores deben separar, como minimo, estas dimensiones:

- `schema`: columnas, tipos logicos, parseabilidad, claves, particiones.
- `identity`: ticker, fecha, particion, fichero, root, universo y version.
- `value_integrity`: reglas fisicas basicas como precios positivos, high/low coherentes, volumen no negativo.
- `temporal_integrity`: orden, duplicados, sesion, calendario, cobertura temporal.
- `coverage`: huecos, universo esperado, casos recuperables, casos no observados.
- `semantic_quality`: flags que afectan interpretacion economica o microestructural.
- `policy_acceptance`: si el dataset o caso puede entrar en backtest, ML, research o solo inspeccion.
- `evidence`: trazabilidad suficiente para reproducir y explicar el dictamen.

La salida final no debe mezclar estas capas en un unico veredicto opaco.

## Estados y significado

Los estados deben respetar la semantica institucional del proyecto:

- `good`: cumple el contrato para el uso declarado.
- `review`: necesita lectura o consumo condicionado; no equivale a corrupcion.
- `bad`: requiere evidencia fuerte y trazable; no puede derivarse solo de una alerta generica.
- `recoverable_without_penalty`: desviacion explicada o reparable sin penalizar el dataset.
- `recoverable_with_flag`: consumible solo manteniendo bandera explicita.
- `review_not_rehabilitated`: caso bajo revision sin rehabilitacion cerrada.
- `forensic_only`: no apto para consumo productivo; solo lectura o investigacion.

Si aparece `bad`, el validador debe emitir evidencia compatible con `bad_evidence_and_rehabilitation.md`.

## Salidas minimas

Un validador institucional debe poder emitir, directa o indirectamente:

- dataset id y version;
- run timestamp;
- source root;
- universo o scope validado;
- unidad de validacion;
- conteos de ficheros, tickers, fechas y filas;
- conteos y porcentajes por estado;
- hard failures;
- warnings y flags;
- reason codes;
- ejemplos o punteros a casos afectados;
- paths de evidencia;
- version de contrato/schema/policy usada;
- informacion suficiente para reproducir la lectura.

Cuando el output sea un markdown, debe contener enlaces o paths a los assets relevantes. Cuando el output sea parquet/csv/json/yaml, debe poder rastrearse desde un readout o dossier.

## Daily

`daily/daily_validators.md` gobierna `daily_core_v0_1`.

Su funcion es separar:

- integridad primaria de barras OHLCV;
- parseo de fechas y unicidad temporal;
- consistencia fichero/particion/contenido;
- cobertura del universo;
- residuos recuperables;
- issues de `vw` o `vwap` como diagnostico secundario;
- cola de exclusion dura.

En daily, OHLC, volumen, fecha y claves tienen autoridad primaria. `vw` no debe convertirse automaticamente en causa de exclusion si el contrato y la evidencia lo tratan como campo secundario o diagnostico.

El validador daily debe impedir dos errores:

- aceptar barras con errores fisicos duros;
- rechazar dataset completo por residuos explicables, secundarios o recuperables.

## Quotes

`quotes/quotes_validators.md` gobierna `quotes_core_v0_1`.

Su funcion es evaluar calidad local del libro y separar esa lectura de la explicacion contextual.

Debe comprobar:

- schema y parseabilidad;
- bid/ask y tamanos;
- crossed/locked markets por severidad;
- timestamps y sesion;
- encoding e integerizacion;
- contexto externo como halts, reference, news, IPOs o eventos;
- cola de exclusion dura.

La regla importante es que el contexto explica, pero no borra el veredicto local. Un halt, una corporate action o un evento puede justificar una lectura, pero no convierte automaticamente un libro roto en `good`.

## Trades

`trades/trades_validators.md` formaliza una validacion por capas para trades.

La separacion principal es:

- validadores de integridad: timestamp, precio, size, identidad de fichero;
- validadores de comparabilidad: fuera de rango daily, fuera de rango 1m, duplicados, sesion, odd-lot, condition codes, scale mismatch;
- validadores de aceptacion: filtros conservadores para `good`, reference-scale-mismatch, microstructure review, no-1m-reference, 1m-reference-alignment y residual bad data.

La regla critica es que un desacuerdo con daily o 1m no prueba por si solo corrupcion de tape. Puede haber problemas de escala, microestructura, odd-lots, cobertura o referencia. El dictamen final debe combinar senales con una politica conservadora.

## Ohlcv 1m raw

`ohlcv_1m/ohlcv_1m_raw_validators.md` gobierna `ohlcv_1m_raw_v0_1`.

Debe validar:

- lectura parquet;
- campos requeridos por schema canonico;
- identidad ticker/particion;
- timestamp de minuto;
- coercion numerica;
- OHLC positivo y coherente;
- volumen y transactions no negativos;
- duplicados ticker-minuto;
- null rates;
- familias de problemas `vw`;
- asserts de universo `<1B>` con interseccion temporal, no solo pertenencia de ticker.

Este validador distingue raw de split-normalized. Que `ohlcv_1m_raw` este reconciliado no significa que `ohlcv_1m_split_normalized` este validado o promovido para el mismo scope.

La promocion no puede ir mas alla de lo que dice la evidencia vigente: si el cierre es `institutional_raw_closeout_reconciled_lt1b`, ese es el limite hasta que una validacion posterior amplie calidad, scope o consumo.

## Validacion de capas derivadas

Para cualquier capa derivada, no basta con comprobar schema y existencia de ficheros.

Segun `layer_validation_standard_v0_1.md`, una capa necesita:

1. validacion semantica;
2. validacion de implementacion;
3. controles negativos;
4. validacion visual o inspectorial;
5. validacion de consumidor real o equivalente;
6. reproducibilidad;
7. trazabilidad documental.

Por eso datasets como labels, features, split-normalized, adjusted views o regime features deben tener validadores que prueben la ausencia de leakage, la semantica temporal, la alineacion con inputs y la interpretacion por consumidores.

## Relacion con inspection_dossiers

Los validadores dicen que comprobar y que salidas exigir.

Los dossiers muestran que se comprobo, que se observo, que casos se inspeccionaron y que lectura institucional se cerro.

Un validador sin dossier puede ser suficiente para una comprobacion tecnica preliminar, pero no para cerrar una auditoria institucional de calidad si el contrato exige inspeccion visual, casos malos, paneles, readouts o rehabilitacion.

## Relacion con data_consumption_policies

Los validadores producen senales.

Las politicas deciden consumo.

Ejemplos:

- `schema_pass` no implica `ml_primary`.
- `review` puede permitir `research_only`.
- `recoverable_with_flag` puede permitir backtest condicionado.
- `bad` puede ser `forensic_only`.
- una capa piloto puede estar documentada y aun asi no sugerir consumo productivo.

Ningun README, validador o dossier debe saltarse la politica de consumo.

## Cuando crear un nuevo validador

Debe crearse o actualizarse un validador cuando:

- se institucionaliza un nuevo dataset;
- se crea un schema canonico;
- se crea o cambia un dataset contract;
- se define una nueva politica de consumo;
- se promueve un dataset a full-universe o `<1B>`;
- se crea una capa derivada;
- un consumidor empieza a depender de una senal;
- se descubre una familia nueva de errores;
- se modifica el significado de `good`, `review`, `bad` o flags.

Si existe data en `E:\TSIS\data` pero no hay validador, no debe asumirse que esta institucionalizada.

## Plantilla recomendada

Cada nuevo documento de validacion deberia incluir:

```text
# <dataset> validators v0.1

## Scope
## Governed dataset
## Linked contract/schema/policy/registry
## Unit of validation
## Required inputs
## Validator families
## Hard failures
## Review/recoverable states
## Output fields
## Evidence requirements
## Pass criteria
## Non-goals / what this validator cannot prove
## Promotion implications
```

Esta plantilla puede adaptarse, pero no debe eliminar la separacion entre checks, estados, evidencia y consumo.

## Checklist antes de modificar un validador

Antes de cambiar un validador:

1. Leer el schema canonico afectado.
2. Leer el dataset contract afectado.
3. Leer la politica de consumo.
4. Leer el registry entry.
5. Leer el dossier o readout vigente.
6. Ver si hay modulo transversal en `module_contracts/`.
7. Determinar si el cambio modifica solo implementacion, o tambien semantica institucional.

Si cambia la semantica, tambien deben revisarse contrato, policy, registry, dossier y changelog.

## Errores que esta carpeta debe evitar

- Usar `bad` para cualquier warning.
- Declarar `good` por simple existencia de parquet.
- Tratar schema conformity como calidad suficiente.
- Mezclar raw, adjusted y split-normalized.
- Convertir contexto externo en absolucion automatica.
- Usar ticker membership como validacion temporal de universo.
- Promover un piloto como full-universe sin evidencia.
- Ocultar hard failures dentro de medias agregadas.
- Emitir estados sin reason codes.
- Cambiar thresholds sin documentar impacto.
- Crear validadores que no indiquen outputs minimos.

## Regla de changelog

Crear o modificar un validador institucional debe dejar entrada en `CHANGELOG.md` cuando:

- cambia el significado de consumo;
- cambia el estado de promocion;
- cambia un hard fail;
- se anade un dataset nuevo;
- se cierra una auditoria;
- se modifica una regla usada por backtest o ML.

Cambios puramente editoriales pueden no requerir changelog, salvo que afecten a trazabilidad del hito.

## Regla final

Un dataset esta mejor validado cuando sus checks estan separados, sus estados tienen semantica estable, sus fallos son reproducibles y su consumo esta gobernado por policy.

`validators/` existe para impedir que el proyecto confunda "la data existe" con "la data esta lista para ser consumida".
