# Data Consumption Policies

## Rol de esta carpeta

`data_consumption_policies/` contiene las reglas operativas que traducen contratos de dataset a uso real por consumidores.

Su funcion principal es responder:

- que puede consumir cada pipeline;
- que estados son aptos para cada consumidor;
- que estados requieren flag;
- que queda limitado a research;
- que queda limitado a forensic;
- que queda prohibido;
- que price view debe usarse;
- que condiciones deben viajar downstream;
- y que promocion adicional hace falta antes de abrir usos mas sensibles.

Esta carpeta no dice simplemente si un dataset existe.

Dice como puede usarse sin romper semantica, calidad, coverage, lineage o control de leakage.

## Autoridades relacionadas

Estas policies deben leerse junto con:

- `01_foundations/module_contracts/consumer_classes.md`
- `01_foundations/module_contracts/policy_explanation_standard.md`
- `01_foundations/module_contracts/dataset_contract_template.md`
- `01_foundations/module_contracts/promotion_pipeline.md`
- `01_foundations/module_contracts/pipeline_price_view_policy.md`
- `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`
- `01_foundations/contract_registry/dataset_contracts/`
- `01_foundations/canonical_schemas/`
- `01_foundations/dataset_registry/`
- `01_foundations/validators/`
- `01_foundations/inspection_dossiers/`

Regla de autoridad:

- el dataset contract define que es el dataset;
- el schema define su forma;
- el validator define que debe comprobarse;
- el inspection dossier muestra por que la evidencia sostiene el estado;
- el dataset registry localiza la capa;
- la consumption policy decide quien puede consumirla y bajo que condiciones.

## Que es una consumption policy

Una consumption policy es el puente entre la clasificacion institucional de un dataset y su uso en pipelines.

Debe responder:

- que dataset o capa gobierna;
- que contrato operacionaliza;
- que estados o buckets reconoce;
- que consumidor puede usar cada estado;
- que consumidor no puede usarlo;
- que flags o condiciones deben preservarse;
- que price view aplica;
- que usos quedan fuera de scope;
- que riesgo metodologico evita;
- y que condiciones habilitarian una promocion futura.

Una policy correcta no es una lista decorativa de consumidores.

Es una barrera de seguridad entre evidencia auditada y consumo downstream.

## Que no es esta carpeta

`data_consumption_policies/` no es:

- un reemplazo del dataset contract;
- un schema;
- un validator ejecutable;
- una registry entry;
- una evidencia de auditoria;
- una autorizacion general para todos los usos;
- ni una forma de promover un dataset por costumbre.

Si una policy no declara un consumidor, ese consumidor no queda habilitado por inferencia.

Si una policy permite un estado solo con flag, esa flag debe viajar con el dato o con la seleccion downstream.

Si una policy restringe un estado a `forensic_only`, no puede entrar en backtest, ML o features como si fuera mercado limpio.

## Vocabulario de consumidores

Las policies deben usar las clases definidas en:

- `01_foundations/module_contracts/consumer_classes.md`

Clases principales:

### `backtest_core`

Consumidor principal para evaluacion historica defendible.

Exige semantica cerrada, calidad estable y riesgo acotado.

No debe recibir casos `review`, `recoverable_with_flag` o coverage ambigua salvo que una policy especifica lo habilite de forma explicita.

### `backtest_extended`

Consumidor para sensibilidad, ampliacion controlada o analisis complementario.

Tolera mas limitaciones que `backtest_core`, pero solo si la policy las declara y las flags viajan downstream.

### `event_engine`

Consumidor de objetos de eventos, causalidad o estructura temporal.

Requiere consistencia temporal, semantica clara y lineage.

### `execution_simulator`

Consumidor de ejecucion, liquidez, slippage, colas, halts o microestructura operacional.

Tiene umbral alto. No queda habilitado automaticamente porque un dataset sea valido para `backtest_core`.

### `ml_primary`

Consumidor ML sin flags especiales obligatorias.

Requiere semantica estable, control de leakage y calidad compatible con uso sistematico.

### `ml_flagged`

Consumidor ML que puede usar estados condicionados si la limitacion viaja explicitamente como feature, mask, sample weight, exclusion marker o metadata equivalente.

No es equivalente a `ml_primary`.

### `rl_allowed`

Consumidor RL potencial.

Debe tratarse como umbral alto y requiere contrato explicito adicional.

No se infiere desde `ml_primary` ni desde `ml_flagged`.

### `causal_only`

Consumidor contextual o causal.

Puede usar datos para anotacion o interpretacion, pero no como fuente cuantitativa principal salvo policy explicita.

### `research_only`

Uso exploratorio, diagnostico o acotado.

No implica autorizacion para backtest ni ML sistematico.

### `forensic_only`

Uso de auditoria, diagnostico, reconciliacion y preservacion de evidencia.

Puede ver estados malos, pero no los convierte en mercado usable.

### `live_downstream_candidate`

Consumidor potencial fuera del modulo 01.

Debe requerir cierre contractual adicional.

## Clases no transitivas

Las clases de consumidor no son automaticamente transitivas.

Reglas criticas:

- `backtest_core` no implica `execution_simulator`;
- `ml_primary` no implica `rl_allowed`;
- `research_only` no implica `backtest_extended`;
- `forensic_only` no implica consumo cuantitativo;
- `institutional` no implica todos los consumidores;
- `validated` no implica consumo live;
- una capa piloto no implica full-universe.

Todo consumidor sensible debe estar escrito de forma explicita.

## Estados de calidad y consumo

Las policies suelen mapear estados como:

- `good`;
- `review`;
- `recoverable_without_penalty`;
- `recoverable_with_flag`;
- `review_not_rehabilitated`;
- `bad`;
- `bad_data`;
- `forensic_only`;
- estados especificos de certificacion o lifecycle.

Regla general:

- `good` puede habilitar consumidores principales si el contrato lo permite;
- `recoverable_without_penalty` puede no degradar el uso principal si la policy lo declara;
- `recoverable_with_flag` exige que la condicion viaje downstream;
- `review` no debe leerse como `good`;
- `review_not_rehabilitated` no debe entrar en consumo principal;
- `bad` debe quedar fuera de backtest/ML/productivo y normalmente limitado a `forensic_only`.

## Coverage no es calidad

Muchas policies separan calidad del dato y coverage.

Ejemplo conceptual:

- una barra puede ser limpia pero estar en una frontera de coverage problematica;
- un gap puede ser esperado, recuperable, ambiguo o realmente problematico;
- un ticker puede pertenecer al universo, pero no todos sus dias o meses son automaticamente esperados;
- un file puede existir, pero no ser healthy ni usable.

La decision final de consumo debe combinar:

- estado de calidad;
- estado de coverage;
- scope temporal;
- universo;
- y consumidor.

Cuando calidad y coverage entren en conflicto, debe prevalecer la interpretacion mas restrictiva salvo que exista policy especifica.

## Price views por consumidor

Las policies deben respetar la semantica de price views.

No todos los consumidores necesitan la misma vista:

- `daily_raw` sirve para auditoria vendor y reconciliacion raw;
- `adjusted` sirve para retornos economicos multi-dia, labels diarios, portfolio valuation y benchmarks;
- `split_normalized` sirve para comparabilidad a traves de splits;
- `trades_raw` sirve para tape, ejecucion y microestructura;
- `quotes_raw` sirve para libro observado;
- `adjusted_proxy` puede servir para diagnostico, pero no debe confundirse con adjusted institucional si no lo es.

Regla:

- un pipeline debe declarar que price view consume;
- un raw tape no debe convertirse en target economico por accidente;
- una vista adjusted no debe sustituir observacion microestructural local cuando la verdad local es raw.

## Flags y condiciones downstream

Cuando una policy permite consumo condicionado, la condicion debe preservarse.

Ejemplos de condicion:

- `recoverable_with_flag`;
- `review`;
- coverage ambigua;
- limited window;
- source scope;
- split-sensitive;
- provisional rehabilitation;
- ticker reuse;
- reference conflict;
- no 1m reference;
- semantic pilot only.

Formas validas de preservar condicion:

- columna flag;
- mask;
- sample metadata;
- manifest de inclusion;
- registry/evidence reference;
- exclusion list;
- split de train/test;
- policy de filtrado reproducible.

No es valido consumir un estado condicionado como si fuera `good`.

## Labels, features y leakage

Las policies deben distinguir:

- datos raw;
- vistas de precio;
- labels;
- features;
- universos;
- provenance;
- y evidence layers.

Reglas importantes:

- `daily_return_labels` son `y`, no `X`;
- labels forward-looking no pueden consumirse antes de estar temporalmente disponibles;
- features cross-session deben declarar la vista de precio usada;
- features piloto no son automaticamente full-universe;
- provenance no es feature productiva salvo contrato explicito;
- un universo ayuda a definir `expected`, pero no decide por si solo `present`, `healthy` ni `usable`.

## Estructura actual

La carpeta contiene actualmente:

```text
data_consumption_policies/
  additional_consumption_policy.md
  daily_consumption_policy.md
  daily_return_labels_consumption_policy.md
  intraday_regime_features_consumption_policy.md
  lt1b_universe_consumption_policy.md
  ohlcv_1m_raw_consumption_policy.md
  quotes_consumption_policy.md
  short_consumption_policy.md
  short_review_consumption_policy.md
  trades_consumption_policy.md
```

## Lectura por policy actual

### `daily_consumption_policy.md`

Gobierna `daily_core_v0_1`.

Distingue:

- calidad del bar;
- coverage;
- `good`;
- `recoverable_with_flag`;
- `bad`;
- `recoverable_without_penalty`;
- `review_not_rehabilitated`;
- price view por pipeline.

Regla clave:

- `daily` es ampliamente usable, pero la decision final no sale de un unico bucket; combina calidad y coverage.

### `quotes_consumption_policy.md`

Gobierna `quotes_core_v0_1`.

Distingue:

- calidad local del libro;
- contexto externo;
- `good`;
- `review`;
- `bad`;
- price view de libro observado.

Regla clave:

- un evento externo puede explicar un episodio, pero no rehabilita automaticamente el libro como limpio.

### `trades_consumption_policy.md`

Gobierna `trades` como raw execution tape y microstructure layer.

Distingue:

- `trades_raw`;
- ejecucion;
- microestructura;
- reconciliacion;
- daily labels;
- benchmark;
- ML labels;
- final states;
- file-level labels;
- rehabilitacion cuantitativa.

Regla clave:

- `trades` no es una vista economica diaria generica; es tape raw para ejecucion, microestructura y reconciliacion bajo semantica explicita.

### `ohlcv_1m_raw_consumption_policy.md`

Gobierna `ohlcv_1m_raw`.

Distingue:

- raw intraday bars;
- alcance `<1B>`;
- schema-only rescue;
- VW severity;
- split-sensitive consumption;
- y necesidad de usar `ohlcv_1m_split_normalized` cuando se cruza frontera de splits.

Regla clave:

- raw 1m puede estar institucionalmente entendido sin estar globalmente limpio para todos los consumidores.

### `daily_return_labels_consumption_policy.md`

Gobierna `daily_return_labels_v0_1`.

Distingue:

- target layer;
- piloto;
- `y` frente a `X`;
- disponibilidad temporal;
- fuente `daily_adjusted`;
- prohibicion de usar `c raw`.

Regla clave:

- labels forward-looking no son features y no prueban edge por si mismos.

### `intraday_regime_features_consumption_policy.md`

Gobierna `intraday_regime_features_v0_1`.

Distingue:

- consumidor piloto de `ohlcv_1m_split_normalized`;
- feature/state research;
- preguntas de contexto;
- no autorizacion full-universe;
- no evidencia de alpha;
- price view cross-session.

Regla clave:

- esta capa valida arquitectura y semantica de normalizacion; no es por si sola el bloque central del backtest base.

### `lt1b_universe_consumption_policy.md`

Gobierna `lt1b_universe_v0_1`.

Distingue:

- corte operativo `<1B>`;
- ticker membership;
- ventana PTI;
- expected coverage;
- no membership diaria fully point-in-time por market cap.

Regla clave:

- para afirmar `<1B>` no basta con ticker; hace falta interseccion temporal con la ventana PTI.

### `additional_consumption_policy.md`

Gobierna familias adicionales como soporte contextual.

Debe preservar:

- source scope;
- semantica de cada subfamilia;
- limites de causalidad;
- y separacion entre soporte contextual y feature/label productivo.

Regla clave:

- `additional` puede ser valioso, pero no debe entrar en consumidores principales sin subcontrato o interpretacion especifica cuando el uso sea sensible.

### `short_consumption_policy.md`

Gobierna `short` y su relacion con `short_review`.

Distingue:

- certification status;
- limited windows;
- ticker reuse;
- reference conflicts;
- FINRA official/free source limits;
- short volume;
- short interest.

Regla clave:

- short data es util, pero debe conservar estado de certificacion, scope de fuente y ventana temporal.

### `short_review_consumption_policy.md`

Gobierna `short_review` como capa de revision/provenance.

Distingue:

- validacion de fuente;
- coverage comparison;
- forensic review;
- reconstruccion futura;
- no sustitucion silenciosa de `short`.

Regla clave:

- provenance y logs no son automaticamente features de modelo.

## Campos recomendados para una policy

Una policy madura deberia incluir, cuando aplique:

```text
1. Rol
2. Dataset o capa gobernada
3. Contratos y companions relacionados
4. Principio rector
5. Estados o buckets reconocidos
6. Mapa estado -> consumidores permitidos
7. Consumidores restringidos o prohibidos
8. Condiciones/flags obligatorias
9. Price view por pipeline
10. Coverage/universe semantics
11. Reglas de leakage temporal
12. Usos no implicados
13. Condiciones para promocion futura
14. Regla final
```

No todas las policies necesitan la misma longitud.

Pero toda policy debe dejar claro que uso habilita y que uso no habilita.

## Criterios para crear una policy nueva

Debe crearse una policy nueva cuando:

- un dataset recibe contrato institucional;
- una capa derivada pasa a uso repetible;
- un label set queda disponible;
- una feature layer deja de ser solo exploratoria;
- un universo gobierna expected coverage;
- una price view se abre a pipelines;
- un dataset de soporte empieza a afectar backtest o ML;
- un consumidor nuevo necesita reglas propias;
- o una auditoria cambia el estado de consumo.

No debe crearse una policy para:

- un notebook aislado;
- un output temporal;
- una muestra sin consumo repetible;
- una feature experimental sin contrato;
- o una carpeta de data que no tenga semantica institucional cerrada.

## Checklist antes de permitir consumo

Antes de habilitar un consumidor:

1. Identificar dataset/capa exacta.
2. Leer dataset contract.
3. Leer schema canonico si aplica.
4. Leer registry entry.
5. Leer inspection dossier o evidencia.
6. Verificar validators o validation standard.
7. Identificar price view.
8. Identificar estado de calidad.
9. Identificar estado de coverage.
10. Identificar universo/scope temporal.
11. Identificar leakage temporal si hay labels/features.
12. Confirmar que la policy menciona el consumidor.
13. Confirmar que flags/condiciones viajan downstream.
14. Excluir estados prohibidos.

Si falta cualquiera de estas piezas para un consumidor sensible, el consumo debe quedar bloqueado o limitado a `research_only`/`forensic_only`.

## Checklist de modificacion

Al modificar una policy:

1. Determinar si el cambio es editorial u operativo.
2. Si cambia allowed consumers, revisar dataset contract y registry.
3. Si cambia estado/bucket, revisar taxonomy/cut policy.
4. Si cambia price view, revisar price semantics y pipeline price view policy.
5. Si cambia universe/scope, revisar registry y coverage evidence.
6. Si habilita ML, revisar leakage y train/test temporal.
7. Si habilita execution/RL/live, exigir contrato adicional.
8. Si cambia restricciones, actualizar inspection dossier si la evidencia cambia.
9. Registrar en `CHANGELOG.md` si el cambio altera consumo real.

## Errores que debe evitar esta carpeta

No debe ocurrir que:

- `research_only` se use como si fuera `backtest_extended`;
- `ml_flagged` se use como si fuera `ml_primary`;
- `backtest_core` habilite automaticamente execution simulator;
- `ml_primary` habilite automaticamente RL;
- un estado `review` viaje sin flag;
- un `bad` entre en training o backtest;
- un label forward-looking se use como feature;
- una capa piloto se trate como full-universe;
- un raw tape se use como retorno economico diario;
- una vista adjusted se use como microestructura local sin justificacion;
- un universo se use como prueba de calidad;
- o una policy contradiga su dataset contract.

## Relacion con `CHANGELOG.md`

Un cambio en policy requiere trazabilidad cuando altera consumo operativo.

Debe registrarse si:

- se habilita o bloquea un consumidor;
- cambia el tratamiento de un estado;
- cambia la regla de flags;
- cambia la vista de precio exigida;
- cambia una condicion de leakage;
- cambia una promocion de piloto a full-universe;
- cambia el scope `<1B>`;
- o cambia una prohibicion relevante.

Cambios editoriales menores, enlaces o aclaraciones sin impacto operativo pueden no requerir entrada propia.

## Regla final

Un dataset no esta listo para consumo institucional serio solo porque exista, tenga schema o este registrado.

Debe tener una policy que diga quien puede usarlo, bajo que estado, con que vista, con que flags, en que scope y para que queda prohibido.
