# Semantic Authority - Modulo 01

## 1. Rol del documento

Este documento define la autoridad semantica del modulo:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps`

Su funcion es fijar el significado operativo de terminos que no pueden quedar a interpretacion local, conversacional o contextual.

## 2. Principio rector

Una palabra institucional no es una sugerencia.

Es un contrato de interpretacion minima.

Por tanto, cuando un termino tenga impacto en:

- consumo de datasets;
- validacion;
- promocion;
- simulacion;
- ML;
- o trazabilidad;

su significado debe estar fijado explicitamente.

## 3. Alcance

Esta autoridad aplica a:

- estados de calidad;
- estados de promocion;
- clases de consumo;
- categorias de evidencia;
- y terminos usados en contracts, policies, schemas y validators.

## 4. Terminos base de calidad

### good

Significa:

- que el objeto o conjunto cumple la politica principal de calidad aplicable;
- que no presenta limitaciones materiales conocidas incompatibles con su uso previsto principal;
- y que puede entrar en consumo permitido sin bandera especial adicional, salvo policy mas restrictiva.

No significa:

- perfeccion absoluta;
- ausencia total de residuos;
- ni garantia de universalidad para cualquier consumidor.

### review

Significa:

- que el objeto requiere tratamiento prudente;
- que existen limitaciones, dudas o desalineaciones conocidas;
- y que su consumo depende de una policy explicita y no de confianza informal.

No significa automaticamente:

- inutilizable;
- ni aceptable por defecto.

### bad

Significa:

- que el objeto no debe consumirse en los flujos permitidos principales del modulo;
- o que su degradacion conocida invalida su uso para los consumidores relevantes definidos.

Puede preservarse por:

- trazabilidad;
- auditoria;
- o investigacion forense.

`bad` no debe usarse como etiqueta opaca ni como vertedero semantico.

Siempre que sea posible, un caso `bad` debe contar con:

- identidad trazable del objeto afectado;
- motivo explicito de exclusión;
- bucket causal o interpretativo;
- evidencia suficiente para inspeccion humana;
- y evaluacion de si existe o no una recuperacion defendible.

Cuando el volumen y la unidad de analisis lo permitan, la exclusión debe poder cotejarse visualmente por:

- file;
- ticker;
- fecha;
- o unidad equivalente afectada.

El hecho de que un proveedor sea serio o de alta calidad no impide que un subconjunto concreto caiga en `bad`.

En TSIS, `bad` no describe necesariamente la calidad global del proveedor.

Describe la falta de autorizacion operativa para un subconjunto concreto, porque existe:

- invalidez dura;
- interpretacion no defendible para el consumidor;
- o riesgo material de contaminar backtest, ML o consumo institucional equivalente.

## 5. Terminos de recuperabilidad

### recoverable

Significa:

- que el objeto no es apto para consumo principal directo;
- pero existe una justificacion metodologica explicita para habilitar consumo restringido bajo condiciones definidas.

Para usar `recoverable` deben existir, como minimo:

- causa conocida de la limitacion;
- condicion explicita de uso;
- consumidor permitido definido;
- y flag o policy de control asociada.

### review_not_rehabilitated

Significa:

- que el objeto se mantiene en zona de revision;
- y que, en el estado actual del modulo, no existe rehabilitacion formal aprobada para su consumo operativo.

### recoverable_with_flag

Significa:

- que el objeto solo puede ser consumido si la bandera de condicion o limitacion viaja con el objeto o con la policy de consumo.

No debe tratarse como equivalente a `good`.

## 6. Terminos de consumo

### backtest_core

Consumo principal del modulo para investigacion historica defendible y evaluacion base.

Exige:

- calidad suficientemente estable;
- semantica cerrada;
- y limitaciones no materiales para el uso base previsto.

### backtest_extended

Consumo permitido para ampliar cobertura o sensibilidad con restricciones explicitas.

No es automaticamente equivalente a `core`.

### ml_primary

Consumo permitido para pipelines ML donde el dataset cumple condiciones primarias de uso sin banderas especiales obligatorias.

### ml_flagged

Consumo permitido para ML solo si las limitaciones conocidas permanecen visibles y controladas.

No significa:

- ML libre;
- ni autorizacion implicita para RL.

### research_only

Consumo permitido solo para exploracion, analisis o investigacion local no promocionada.

### forensic_only

Consumo permitido solo para auditoria, diagnostico y trazabilidad.

### causal_only

Consumo permitido cuando la semantica del objeto sirve como evidencia causal o contextual, pero no como fuente cuantitativa principal de simulacion o aprendizaje.

## 7. Terminos de promocion

### exploratory

Objeto no cerrado semantica ni operativamente.

### provisional

Objeto util y repetible, pero todavia sin cierre institucional suficiente.

### validated

Objeto con validacion suficiente para consumo gobernado limitado.

No significa todavia:

- autoridad institucional final;
- ni permiso de redefinicion upstream.

### certified

En este modulo, `certified` significa:

- que existe una interpretacion operativa suficientemente cerrada sobre calidad, cobertura o uso;
- pero no implica por si sola que el objeto ya sea autoridad institucional global del modulo.

### institutional

Significa:

- que el objeto ya forma parte del sistema operativo oficial del modulo;
- que tiene contrato, semantica y trazabilidad suficientemente cerrados;
- y que puede ser tratado como referencia local vigente.

### diferencia entre certified e institutional

`certified` cierra interpretacion operativa.

`institutional` cierra adopcion contractual dentro del sistema operativo del modulo.

Por tanto:

- puede existir algo `certified` que aun no este plenamente `institutional`;
- no debe existir algo `institutional` sin base de certificacion o validacion suficiente.

## 8. Regla de tratamiento del bad

La clasificacion `bad` debe sostenerse con un estandar de prueba mas alto que una simple alerta automatica.

Por tanto:

- un validador por si solo no basta como explicacion institucional completa;
- el caso debe poder explicarse logicamente;
- el inspector debe poder revisar la anomalia subyacente;
- y, cuando sea razonable, debe evaluarse una recuperacion que no degrade la integridad del backtest ni del ML.

Si existe una recuperacion defendible, debe documentarse como:

- `reclassified`;
- `recoverable_with_flag`;
- o categoria equivalente aprobada por contrato.

Si no existe recuperacion defendible, el caso debe permanecer en `bad` con justificacion trazable.

## 9. Regla de precedencia semantica

En caso de ambiguedad, la interpretacion correcta debe venir de:

1. contratos raiz de TSIS
2. `01_foundations/module_contracts/`
3. dataset contracts y policy contracts especificos
4. validators institucionales

No debe venir de:

- conversaciones;
- costumbre local;
- notebook comments;
- ni nombres heredados ambiguos.

## 10. Regla final

Si un termino critico no tiene significado estable y compartido, no puede sostener un contrato institucional serio.
