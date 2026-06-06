# Quotes Label Taxonomy And Cut Policy

## 1. Rol

Este documento fija la taxonomia exacta y la politica de corte de `quotes`.

Companions explicativos:

- `01_foundations/module_contracts/policy_explanation_standard.md`
- `01_foundations/module_contracts/quotes_acceptance_policy_explained.md`
- `01_foundations/module_contracts/quotes_rules_explained_line_by_line.md`

Su funcion es dejar por escrito:

- cual es la unidad exacta de decision;
- que artefactos historicos mandan;
- que familias taxonomicas existen;
- como se traduce la auditoria local a `good`, `review` y `bad`;
- y como debe separarse la calidad local del libro de la explicacion causal externa.

No reaudita `quotes`.
Institucionaliza en `01_foundations` la logica que ya esta repartida entre auditoria, metodologia, closeout y certificacion historica.

## 2. Fuentes de autoridad

La politica aqui fijada nace de estas capas de autoridad:

### A. Marco general del proyecto y crosswalk

- `auditoria/00_que_proyecto_estamos_construyendo.md`
- `auditoria/01_auditoria_1B_general.md`
- `auditoria/05_crosswalk_multidataset.md`

### B. Auditoria especifica de `quotes`

- `auditoria/quotes/v1/00_auditoria_quotes.md`
- `auditoria/quotes/v1/01_contrato_agent02_agent03_03312026.md`
- `auditoria/quotes/v1/02_diseno_arquitectura_quotes_CD.md`
- `auditoria/quotes/v2/04_quotes_full_C_D_methodology.md`
- `auditoria/quotes/v2/04_quotes_full_C_D_closeout.md`

### C. Certificacion local historica de `quotes`

- `certification/quotes/00_quotes_certification_guide.md`
- `certification/quotes/01_quotes_certification_contract.md`
- `certification/quotes/02_quotes_expected_presence_logic.md`
- `certification/quotes/03_quotes_quality_policy.md`
- `certification/quotes/04_quotes_usage_policy.md`
- `certification/quotes/12_quotes_open_buckets_synthesis.md`

### D. Capa contractual transversal del modulo

- `01_foundations/module_contracts/semantic_authority.md`
- `01_foundations/module_contracts/market_session_scope.md`

## 3. Unidad exacta de decision

La unidad natural de clasificacion en `quotes` es:

- `ticker, date, file`

O, dicho de forma operativa:

- un file diario de `quotes` para un ticker concreto

Ejemplo conceptual:

- `ticker=AMC`
- `date=2021-06-03`
- `file=...quotes...AMC...2021-06-03.parquet`

No se clasifica primero el ticker en abstracto.
Se clasifica un caso diario concreto del libro observado.

## 4. Sesion objetivo

`quotes` queda gobernado por:

- [market_session_scope.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/market_session_scope.md>)

Por tanto, la sesion institucional objetivo de `quotes` es:

- `04:00-20:00 America/New_York`

Premarket y afterhours forman parte del alcance esperado del bloque.

## 5. Pregunta que responde `quotes`

`quotes` responde a una pregunta precisa:

- cual fue el estado observado del libro `bid/ask`

No responde por si solo:

- si hubo halt formal;
- si hubo corporate action;
- si el ticker era o no la entidad correcta;
- ni cual fue la causa final del episodio.

Eso significa que la politica de corte de `quotes` debe leer primero:

- calidad local del libro

y solo despues:

- contexto causal externo

## 6. Principio rector del corte

La regla mas importante que sale del historico de `quotes` es esta:

- el contexto causal puede explicar el episodio;
- pero no rehabilita automaticamente la calidad local del libro.

En particular:

- `halts` puede explicar un episodio;
- `reference` puede contextualizar una distorsion;
- `news` puede acompanar la reaccion;

pero si el libro sigue mostrando crossed economicamente material, el caso sigue siendo problema de `quotes`.

## 7. Politica local base

La politica local historica de `quotes` trabaja con tres etiquetas:

- `good`
- `review`
- `bad`

Lectura minima:

- `good`
  - apto para el uso mas estricto del bloque

- `review`
  - util solo con control, explicacion o flag explicito

- `bad`
  - fuera del uso core del bloque

## 8. Familias taxonomicas relevantes

La auditoria `v2` deja una taxonomia refinada amplia, pero institucionalmente importan sobre todo:

### Familias buenas o sanas

- `clean_pass_or_other`
- `soft_crossed_micro_noise`
- `persistent_soft_crossed_low`
- `utc_rollover_large_day_clean`

### Familias que quedan en `review`

- `persistent_soft_crossed_mid_large_scale`
- `large_file_threshold_edge_hard_many_crosses`

### Familias que quedan en `bad`

- `medium_file_threshold_edge_hard_many_crosses`
- `high_hard_crossed_10_to_20`

## 9. Politica exacta de cierre por familias abiertas

### `persistent_soft_crossed_mid_large_scale`

Decision final:

- `review`

Razon:

- crossed persistente real;
- parte del bucket queda bien contextualizada por `halts`;
- otra parte sigue como residuo microestructural abierto;
- no es suficientemente limpio para `good`.

### `large_file_threshold_edge_hard_many_crosses`

Decision final:

- `review`

Razon:

- bucket mixto real;
- combina casos moderados, severos y parte explicable por `halts`;
- no es suficientemente limpio para `good`;
- tampoco es uniformemente duro como para bajarlo entero a `bad`.

### `medium_file_threshold_edge_hard_many_crosses`

Decision final:

- `bad`

Razon:

- familia ya demasiado agresiva;
- crossed ratio mayor;
- bucket `HARD_FAIL`;
- y cola severa fuerte cuando sobrevive `ask > 0`.

### `high_hard_crossed_10_to_20`

Decision final:

- `bad`

Razon:

- es la familia abierta mas agresiva;
- el crossed ratio es extremo;
- y cuando sobrevive `ask > 0`, lo hace como crossed positivo severo.

## 10. Regla economica subyacente

El criterio economico que organiza estas decisiones es este:

- `halt` puede explicar el episodio;
- pero no neutraliza por si solo la severidad del crossed positivo con `ask > 0`.

Por eso, en `quotes`, hay que separar siempre:

- explicacion causal del evento
- calidad operativa del libro

## 11. Traduccion contractual minima

La traduccion contractual minima que debe usar `01_foundations` para `quotes` es:

- `good`
  - familias limpias o residuo leve

- `review`
  - familias mixtas o contextualizables pero no limpias

- `bad`
  - familias donde el residuo local del libro sigue siendo economicamente demasiado agresivo

## 12. Regla de uso derivada

La traduccion de consumo que sale de esta politica es:

- `good`
  - base limpia del bloque

- `review`
  - sensibilidad, investigacion con flag o ML con flag

- `bad`
  - fuera del uso core

La policy de consumo fina vivira despues en el contrato especifico de uso del bloque.

La cadena contractual institucional que ya materializa esta traduccion es:

- `01_foundations/contract_registry/dataset_contracts/quotes_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/quotes_consumption_policy.md`
- `01_foundations/canonical_schemas/quotes/quotes_schema_contract.md`
- `01_foundations/validators/quotes/quotes_validators.md`
- `01_foundations/dataset_registry/quotes/quotes_registry_entry.yaml`

## 13. Qué sigue abierto

Este documento no cierra todavia:

- una tabla final exhaustiva file a file del universo completo;
- ni el ensamblaje final de `expected`, `present`, `healthy`, `usable_for`

Eso pertenecera al contrato institucional completo de `quotes`.

Lo que si cierra ya es:

- la lectura taxonomica estable;
- la politica de corte de las familias abiertas;
- y la separacion entre contexto causal y calidad local del libro.

## 14. Conclusión operativa

`quotes` llega a `01_foundations` con una base historica fuerte.
No requiere reauditoria.

Requiere:

- promocion contractual limpia;
- policy de uso conservadora;
- y, mas adelante, dossiers de inspeccion que expliquen de forma visual y fisica por que un caso cae en `good`, `review` o `bad`.
