# Pipeline Price View Policy - Modulo 01

## 1. Rol del documento

Este documento fija, a nivel transversal del modulo, que vista de precio debe usar cada pipeline o departamento funcional.

No redefine las vistas.

Se apoya en:

- `price_views_registry.md`
- `price_semantics_and_adjustment_policy.md`
- `corporate_actions_adjustment_methodology.md`

Companions explicativos:

- `pipeline_price_view_policy_explained.md`
- `pipeline_price_view_rules_line_by_line.md`

Su funcion es convertir la semantica de precio en reglas operativas de consumo.

## 2. Principio rector

No existe una unica vista de precio valida para todos los usos.

La decision correcta depende de:

- si el pipeline modela ejecucion o retorno economico;
- si el objetivo es auditoria, reconciliacion o produccion de senales;
- y si la comparabilidad buscada es:
  - microestructural
  - mecanica de escala
  - o economica

## 3. Vistas relevantes

Las vistas institucionales hoy reconocidas son:

- `quotes_raw`
- `trades_raw`
- `daily_raw`
- `split_normalized`
- `adjusted`
- `adjusted_proxy`

## 4. Mapa por pipeline

### 4.1 Vendor audit y forensic reconciliation

Vista primaria:

- `daily_raw`
- `quotes_raw`
- `trades_raw`

Vistas auxiliares:

- `split_normalized`
- `adjusted_proxy`

Objetivo:

- explicar discrepancias;
- distinguir error real de mismatch por semantica de precio;
- reconciliar `quotes` vs `daily`;
- y reconciliar interno vs plataformas externas.

No usar por defecto:

- `adjusted` como unica vista, porque puede ocultar la escala mecanica observada.

#### Por que esta regla es correcta

La reconciliacion forense no intenta producir un retorno economico comparable.

Intenta responder:

- que se observo realmente;
- si hay mismatch de escala;
- si la discrepancia es mecanica o economica;
- y si un chart externo esta mostrando otra semantica de precio.

Por eso necesita:

- `daily_raw`
  - para comparar con tablas raw del vendor o con OHLC historico sin reinterpretacion economica;
- `split_normalized`
  - para distinguir si el conflicto es solo de escala por split;
- `adjusted_proxy`
  - para ver si la discrepancia externa puede explicarse por dividendos o por una serie ajustada.

Esta separacion es consistente con:

- CRSP y su distincion entre precio observado y series ajustadas;
- la practica institucional de reconciliar primero la escala mecanica y despues la semantica economica;
- y la necesidad, enfatizada por Lopez de Prado, de no colapsar sin declarar capas distintas del dato cuando se investiga calidad o leakage.

### 4.2 Execution research y simulacion microestructural

Vista primaria:

- `quotes_raw`
- `trades_raw`

Vistas auxiliares:

- `split_normalized` cuando haga falta alinear escalas historicas con `daily`
- `halts` como capa causal y operativa

Objetivo:

- spread real
- crossed real
- slippage
- disponibilidad del libro
- secuencia temporal observada

No usar como vista principal:

- `adjusted`
- `adjusted_proxy`

porque no representan el libro ejecutable observado.

#### Por que esta regla es correcta

La ejecucion ocurre contra:

- el libro observado;
- los prints observados;
- y las condiciones temporales reales de sesion, halt, spread y crossed.

El simulador o research de ejecucion necesita medir:

- spread real;
- slippage;
- disponibilidad del libro;
- secuencia temporal;
- y riesgo microestructural.

Ni `adjusted` ni `adjusted_proxy` sirven aqui como vista principal porque:

- no representan lo que podia ejecutarse;
- pueden suavizar o reinterpretar precios por corporate actions posteriores;
- y destruyen la semantica local del libro que queremos estudiar.

Esto esta alineado con:

- la practica sistematica de AQR y Man AHL de separar señal de implementacion;
- el principio de microstructure-first para costes de trading;
- y la distincion entre observed execution prices y economic return series comun en market microstructure.

### 4.3 Signal research diario y factor research

Vista primaria:

- `adjusted`

Vistas auxiliares:

- `daily_raw` para control vendor
- `split_normalized` para diagnostico

Objetivo:

- retornos comparables
- momentum
- mean reversion
- cross-sectional signals
- benchmarking

No usar por defecto:

- `quotes_raw`
- `trades_raw`

como base de retorno economico multi-dia.

#### Por que esta regla es correcta

La investigacion diaria y factor requiere retornos comparables a traves del tiempo y entre activos.

Si se usan series `raw` sin ajuste:

- un split puede parecer un shock de precio;
- un dividendo puede parecer una caida o gap con falsa informacion predictiva;
- y el modelo o backtest puede aprender corporate actions como si fueran alpha.

La vista `adjusted` evita ese problema porque:

- preserva continuidad economica;
- permite comparar retornos de forma homogenea;
- y alinea mejor el research con asset pricing clasico y con labels de ML defendibles.

Esta regla esta apoyada por:

- Fama-French y la necesidad de retornos comparables;
- Gu/Kelly/Xiu para ML en asset pricing;
- y Lopez de Prado, en el sentido de que la etiqueta debe corresponder a la variable economica que realmente se quiere predecir.

### 4.4 Portfolio valuation y benchmark interno

Vista primaria:

- `adjusted`

Objetivo:

- equity curve
- drawdown
- PnL historico comparable
- comparacion con benchmarks

No usar por defecto:

- `daily_raw`

cuando el resultado deba ser economicamente comparable a traves de corporate actions.

#### Por que esta regla es correcta

Valoracion y benchmarking no quieren saber solo que precio se observo.

Quieren saber:

- como evoluciona economicamente una posicion;
- como cambia el PnL historico;
- y como se compara una estrategia contra un benchmark en la misma base economica.

Si la valoracion usa `raw`:

- corporate actions mecanicas distorsionan la curva;
- drawdowns y retornos dejan de ser comparables;
- y el benchmark puede parecer desalineado sin que exista error de estrategia.

Por eso la vista primaria debe ser `adjusted`.

### 4.5 ML - features microestructurales

Vista primaria:

- `quotes_raw`
- `trades_raw`

Vistas auxiliares:

- `halts`
- `news`
- `short_volume`

Objetivo:

- features del libro
- liquidez
- crossed
- intensidad de actividad
- venue structure

#### Por que esta regla es correcta

Las features microestructurales describen:

- forma del libro;
- deterioro local;
- crossed;
- tamano;
- intensidad;
- venue mix;
- y secuencia temporal.

Todo eso vive en el dato observado, no en una serie ajustada por corporate actions futuras.

Usar `adjusted` aqui seria incorrecto porque reescribiría retrospectivamente el libro y desalinearia la microestructura respecto a la realidad operativa del instante.

### 4.6 ML - features diarios y labels de retorno

Vista primaria:

- `adjusted`

Vistas auxiliares:

- `daily_raw` para QC
- `split_normalized` para reconciliacion

Objetivo:

- labels de retorno
- features daily comparables
- evitar leakage o shocks artificiales por dividends/splits

Regla fuerte:

- los labels de retorno no deben construirse sobre `raw` si el corporate action puede aparecer como falso alpha.

#### Por que esta regla es correcta

En ML diario hay dos riesgos graves si se usan labels `raw`:

- leakage semantico:
  el modelo aprende corporate actions como si fueran senal;
- inconsistencia entre features y target:
  los features intentan describir dinamica economica, pero el target incluye saltos no economicos o no comparables.

La vista `adjusted` minimiza ese problema y acerca el target a la variable economica relevante:

- retorno comparable;
- continuidad para horizontes de prediccion;
- y mejor compatibilidad con backtest posterior.

Esta decision esta alineada con:

- Lopez de Prado en la construccion disciplinada de labels;
- Gu/Kelly/Xiu en ML de retornos;
- y la practica institucional de separar feature basis y target basis.

### 4.7 External platform comparison

Vista primaria:

- `daily_raw`
- `adjusted_proxy`

Vistas auxiliares:

- `adjusted`
- `split_normalized`

Objetivo:

- explicar por que una plataforma externa no coincide;
- distinguir:
  - raw vs adjusted
  - split-normalized vs adjusted
  - remap nominal vs continuidad economica

Regla:

- ninguna comparacion externa es valida sin declarar explicitamente la vista interna y la vista externa inferida.

#### Por que esta regla es correcta

Las plataformas externas pueden mostrar:

- `raw`
- `split adjusted`
- `fully adjusted`
- o una cadena propia no completamente transparente

Por eso una comparacion directa de:

- precio interno
- vs chart externo

puede ser falsa o ambigua.

La triada:

- `daily_raw`
- `split_normalized`
- `adjusted_proxy`

permite separar tres preguntas distintas:

1. la discrepancia es solo de escala mecanica;
2. la discrepancia se explica por dividendos/corporate actions;
3. o sigue abierta incluso despues de distinguir ambas capas.

Esta es la forma correcta de no confundir:

- error de dato;
- mismatch de semantica;
- y ajuste vendor-specific.

## 5. Regla de precedencia

Cuando un pipeline combine varias vistas, debe declararse:

- `signal_price_view`
- `execution_price_view`
- `valuation_price_view`
- `benchmark_price_view`

o, en ML:

- `feature_price_view`
- `target_price_view`

Si no se declara, el pipeline no debe considerarse institucionalmente cerrado.

## 6. Regla por defecto para nuevos trabajos

Si un nuevo trabajo no declara su vista y trabaja sobre retornos:

- asumir `adjusted`

Si un nuevo trabajo no declara su vista y trabaja sobre libro o ejecucion:

- asumir `quotes_raw` y/o `trades_raw`

Si un nuevo trabajo no declara su vista y trabaja sobre reconciliacion:

- asumir `daily_raw` + `split_normalized` + `adjusted_proxy`

## 7. Relacion con datasets

Esta policy debe aterrizarse por dataset en:

- `daily_consumption_policy.md`
- `quotes_consumption_policy.md`
- futuras policies de `trades` y `1m`

## 8. Relacion con la literatura y practica institucional

La separacion entre:

- precio de ejecucion observado
- precio de retorno economico comparable
- y capas de reconciliacion

es consistente con:

- CRSP y su tratamiento de corporate actions
- asset pricing research tipo Fama-French
- ML financiero disciplinado tipo Lopez de Prado
- asset pricing via ML tipo Gu/Kelly/Xiu
- practica sistematica institucional tipo AQR y Man AHL

La idea central es simple:

- una arquitectura de hedge fund seria no mezcla sin declarar la semantica de precio con la que investiga, ejecuta, etiqueta o valora.

## 9. Regla de excelencia documental

Toda decision futura que altere:

- la vista primaria de un pipeline;
- la semantica de labels;
- la politica de ajuste;
- o la reconciliacion externa

debe dejar por escrito:

- que vista se usa;
- por que se usa;
- que riesgo metodologico evita;
- y que literatura o practica institucional respalda la decision.
