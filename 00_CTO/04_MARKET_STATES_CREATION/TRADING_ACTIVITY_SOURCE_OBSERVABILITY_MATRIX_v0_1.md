# TRADING_ACTIVITY_SOURCE_OBSERVABILITY_MATRIX_v0_1

> **Artefacto de auditoría de observabilidad física** para el Objeto de Información `Trading Activity` dentro del perfil candidato `Wake-up`.
>
> Este documento no admite todavía variables canónicas, no define la tabla de salida y no autoriza consumo downstream.

---

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `trading_activity_source_observability_matrix` |
| `document_version` | `v0_1` |
| `document_role` | `SOURCE_OBSERVABILITY_HARD_GATE` |
| `document_status` | `DRAFT` |
| `review_verdict` | `PASS_WITH_REQUIRED_REVISIONS` |
| `workflow_status` | `READY_FOR_SOURCE_AUDIT` |
| `freeze_status` | `NOT_READY_FOR_FREEZE` |
| `source_audit_status` | `NOT_EXECUTED` |
| `information_object_id` | `trading_activity` |
| `representation_profile_id` | `wake_up_information_object_profile_candidate_v0_1` |
| `representation_model_candidate_id` | `absolute_and_pit_relative_multiscale_marked_activity_process` |
| `input_source_binding_status` | `REQUIRES_EVIDENCE` |
| `output_table_mapping_status` | `NOT_STARTED` |
| `canonical_feature_promotion_status` | `NOT_AUTHORIZED` |
| `downstream_consumption_status` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-06` |
| `owner` | `TBD` |

```text
CURRENT VERDICT
===============

PASS_WITH_REQUIRED_REVISIONS
READY_FOR_SOURCE_AUDIT
NOT_READY_FOR_FREEZE
```

---

## 1. Propósito

Este artefacto determina si las fuentes físicas de trades disponibles para TSIS permiten observar, reconstruir y reproducir causalmente la información necesaria para implementar experimentalmente el modelo de representación candidato de `Trading Activity`.

Responde exclusivamente a esta pregunta:

```text
¿Las fuentes físicas realmente disponibles contienen
los hechos, timestamps, condiciones, secuencias,
revisiones y evidencia de cobertura necesarios
para construir los bindings experimentales de
Trading Activity sin inventar observabilidad,
sin confundir ausencia de datos con actividad cero
y sin utilizar información futura?
```

La secuencia gobernada es:

```text
INFORMATION OBJECT
Trading Activity
↓
REPRESENTATION MODEL CANDIDATE
Absolute-and-PIT-Relative Multiscale Marked Activity Process
↓
SOURCE OBSERVABILITY HARD GATE
este documento
↓
EXPERIMENTAL PHYSICAL BINDINGS
A / B / C1 / C2
↓
COMPARACIÓN EXPERIMENTAL OOS
↓
BINDING SELECCIONADO
↓
PROMOTION VALIDATION
↓
SELECCIÓN INDIVIDUAL DE VARIABLES PROMOVIBLES
↓
CANONICAL PHYSICAL IMPLEMENTATION
```

---

## 2. Frontera de responsabilidad

```text
INPUT SOURCE BINDING
=
SE DEFINE Y AUDITA AHORA
```

```text
OUTPUT TABLE MAPPING
=
SE DEFINE POSTERIORMENTE
```

### 2.1 Incluido en este documento

- fuentes físicas candidatas de trades;
- campos físicos y semántica de cada campo;
- `event_time`, `observed_at` y `available_at`;
- identidad, secuencia y ordenación determinista;
- precio, tamaño, valor nocional y condiciones de trade;
- correcciones, cancelaciones, duplicados y mensajes tardíos;
- cobertura, gaps, outages y evidencia para declarar actividad cero;
- soporte histórico necesario para baselines PIT;
- soporte mínimo de cardinalidad por familia de variables;
- observabilidad requerida por Binding A, B, C1 y C2;
- veredicto `OBSERVABLE`, `OBSERVABLE_WITH_RESTRICTIONS`, `REQUIRES_EVIDENCE` o `NOT_OBSERVABLE`.

### 2.2 Excluido de este documento

- selección final de ventanas;
- thresholds del detector;
- definición final de episodios positivos y negativos;
- comparación OOS;
- selección del binding ganador;
- promoción automática de todas las variables del binding ganador;
- esquema canónico de salida;
- tabla física donde vivirán las variables;
- autorización de Market State, Event State o backtest;
- Tradability, Entry Eligibility, órdenes, fills o PnL.

---

## 3. Binding semántico upstream

### 3.1 Information Object

```text
TRADING ACTIVITY
```

Pregunta semántica del perfil `Wake-up`:

```text
¿Cómo cambia la participación transaccional
respecto al régimen previo del instrumento
y a su baseline contextual PIT?
```

### 3.2 Representation Model Candidate

```text
ABSOLUTE-AND-PIT-RELATIVE
MULTISCALE MARKED ACTIVITY PROCESS
```

### 3.3 Dimensiones que debe poder implementar la fuente

```text
1. ABSOLUTE ACTIVITY
2. EVENT INTENSITY
3. ACTIVITY MARKS
4. TEMPORAL CONCENTRATION
5. PIT-RELATIVE SURPRISE
6. TRANSITION AND ANTI-ARTIFACT PERSISTENCE
```

La sexta dimensión se limita a conservar persistencia suficiente para distinguir una activación multievento de un print aislado. No representa la persistencia económica posterior del episodio, que pertenece a `In-Play` o al seguimiento del `Episode Instance`.

### 3.4 Fronteras semánticas

`Trading Activity` no debe apropiarse de:

```text
Price Movement
Liquidity
Market Microstructure State
Order Flow Pressure
In-Play
Tradability
Entry Eligibility
Continuation
Expected Return
```

Relación correcta con `Market Microstructure State`:

```text
Trading Activity
=
representa directamente la transición de actividad

Market Microstructure State
=
aporta representación contemporánea
y corroboración candidata

PROFILE MEMBERSHIP
≠
MANDATORY DETECTOR PREDICATE
```

---

## 4. Experimental Physical Bindings bajo auditoría

El documento no compara tres modelos conceptuales distintos. Audita si una única representación conceptual puede materializarse mediante varios bindings físicos experimentales.

| Binding | Nombre | Alcance experimental | Estado inicial |
|---|---|---|---|
| `A` | `Minimal Multiscale Activity` | Counts, volumen, dollar volume, intensidad básica, sorpresa PIT y transición mínima antinartefacto | `REQUIRES_SOURCE_AUDIT` |
| `B` | `Marked Duration and Concentration` | Binding A más duraciones, distribución de tamaños y concentración temporal | `REQUIRES_SOURCE_AUDIT` |
| `C1` | `Conditional Duration / ACD` | Extensión condicional basada en duraciones | `DEFERRED_PENDING_SOURCE_AND_ESTIMATOR_EVIDENCE` |
| `C2` | `Self-Exciting Intensity / Hawkes` | Extensión autoexcitada basada en procesos puntuales | `DEFERRED_PENDING_SOURCE_AND_ESTIMATOR_EVIDENCE` |

```text
BINDING SELECCIONADO
↓
ELEGIBLE PARA PROMOTION VALIDATION
↓
NO implica promoción automática
ni del binding completo
ni de todas sus variables
```

---

## 5. Conjunto causal de trades

### 5.1 Tiempos gobernados

| Símbolo | Significado |
|---|---|
| `t_d` | `decision_timestamp`: instante de mercado que se representa |
| `t_a` | `state_available_at` o instante de conocimiento legal usado para construir el estado |
| `W` | ventana histórica cerrada en `t_d` |
| `event_time_i` | instante económico atribuido al trade por la fuente |
| `available_at_i` | primer instante desde el que TSIS puede consumir legalmente el registro o mensaje |

### 5.2 Definición causal

```text
T_W(t_d, t_a)
=
{
  i:
  eligible_i_as_of(t_a)
  AND t_d - W < event_time_i <= t_d
  AND available_at_i <= t_a
}
```

Debe cumplirse además:

```text
t_a <= decision_clock
future_window_used = false
outcome_dependency = false
```

### 5.3 Significado de `eligible_i_as_of(t_a)`

La elegibilidad no puede evaluarse utilizando el estado final retrospectivo del trade. Debe reflejar exclusivamente lo conocido hasta `t_a`:

```text
eligible_i_as_of(t_a)
=
resultado de aplicar la política de elegibilidad
sobre la versión del evento y sus revisiones
que ya estaban disponibles en t_a
```

### 5.4 Regla no negociable sobre revisiones

```text
NO SILENT RETROACTIVE MUTATION
```

Un trade tardío, una corrección o una cancelación conocida después de publicar un estado no puede modificar silenciosamente el estado que fue legalmente consumible antes.

Deben existir dos vistas institucionalmente separadas:

```text
DECISION-SAFE AS-KNOWN STATE
=
reconstrucción con la información disponible en t_a

RECONCILED RESEARCH VIEW
=
reconstrucción posterior con revisiones conocidas después
```

La vista reconciliada puede utilizarse para auditoría o investigación, pero no para simular que una decisión pasada conocía una revisión futura.

---

## 6. Vocabulario de veredictos

| Veredicto | Significado |
|---|---|
| `OBSERVABLE` | La fuente aporta evidencia física y temporal suficiente para reconstruir el hecho de forma causal y reproducible |
| `OBSERVABLE_WITH_RESTRICTIONS` | El hecho puede observarse solo bajo restricciones explícitas de cobertura, sesión, periodo, resolución o política |
| `REQUIRES_EVIDENCE` | La capacidad no puede confirmarse todavía porque faltan esquema, documentación, muestras o pruebas |
| `NOT_OBSERVABLE` | La fuente no contiene la información necesaria o solo conserva una versión retrospectiva incompatible con el uso PIT |
| `NOT_APPLICABLE` | El requisito no aplica al binding o fuente evaluados |

Regla fail-closed:

```text
UNKNOWN
=
REQUIRES_EVIDENCE

UNKNOWN no puede convertirse en OBSERVABLE por inferencia.
```

---

# 7. Source Observability Matrix

## 7.1 Identidad, tiempo y orden causal

| ID | Hecho físico requerido | Binding(s) | Evidencia mínima exigida | Mapping físico | Veredicto inicial | Restricción / pregunta de auditoría |
|---|---|---:|---|---|---|---|
| `TA-SO-001` | Identidad canónica del instrumento | A/B/C1/C2 | Campo estable y mapping a `instrument_id` PIT | `TBD` | `REQUIRES_EVIDENCE` | ¿Cómo se resuelven ticker changes, reutilización de símbolos y corporate actions? |
| `TA-SO-002` | Identidad única del trade o mensaje | A/B/C1/C2 | `trade_id`, message id o clave de deduplicación documentada | `TBD` | `REQUIRES_EVIDENCE` | ¿La identidad es estable entre revisiones y particiones? |
| `TA-SO-003` | `event_time` del trade | A/B/C1/C2 | Campo, timezone, precisión, semántica y origen documentados | `TBD` | `REQUIRES_EVIDENCE` | ¿Es exchange time, SIP time, participant time o timestamp reconstruido? |
| `TA-SO-004` | `available_at` | A/B/C1/C2 | Timestamp real o regla reproducible del primer instante de consumo legal | `TBD` | `REQUIRES_EVIDENCE` | Si no existe, ¿puede reconstruirse sin usar conocimiento futuro? |
| `TA-SO-005` | `observed_at` / ingest time | A/B/C1/C2 | Timestamp de observación por la plataforma o evidencia equivalente | `TBD` | `REQUIRES_EVIDENCE` | Debe distinguirse de `event_time` y `available_at` |
| `TA-SO-006` | Ordenación determinista | A/B/C1/C2 | Sequence id o tie-break estable y documentado | `TBD` | `REQUIRES_EVIDENCE` | ¿Cómo se ordenan mensajes con el mismo timestamp? |
| `TA-SO-007` | Resolución temporal | A/B/C1/C2 | Unidad y precisión efectiva verificadas con datos | `TBD` | `REQUIRES_EVIDENCE` | Resolución insuficiente puede bloquear C1/C2 aunque permita A |
| `TA-SO-008` | Timezone y calendario | A/B/C1/C2 | UTC normalizado + reglas DST + calendario/sesión | `TBD` | `REQUIRES_EVIDENCE` | Debe permitir separar premarket, regular y after-hours |
| `TA-SO-009` | Session phase as-of | A/B/C1/C2 | Regla determinista basada en calendario autorizado | `TBD` | `REQUIRES_EVIDENCE` | No debe inferirse solo por hora local sin calendario de sesión |

## 7.2 Hechos económicos y marcas del trade

| ID | Hecho físico requerido | Binding(s) | Evidencia mínima exigida | Mapping físico | Veredicto inicial | Restricción / pregunta de auditoría |
|---|---|---:|---|---|---|---|
| `TA-SO-010` | Precio del trade | A/B/C1/C2 | Campo numérico, unidad, precisión y semántica documentadas | `TBD` | `REQUIRES_EVIDENCE` | Necesario para dollar volume; no debe confundirse con precio ajustado retrospectivo |
| `TA-SO-011` | Tamaño del trade | A/B/C1/C2 | Campo numérico, unidad y tratamiento de lotes documentados | `TBD` | `REQUIRES_EVIDENCE` | ¿Acciones, lotes, unidades fraccionarias o tamaño agregado? |
| `TA-SO-012` | Valor nocional reconstruible | A/B | Precio y tamaño válidos en la misma versión del evento | `TBD` | `REQUIRES_EVIDENCE` | No usar columna vendor-derived sin equivalencia demostrada |
| `TA-SO-013` | Condiciones del trade | A/B/C1/C2 | Códigos completos + documentación oficial/versionada | `TBD` | `REQUIRES_EVIDENCE` | Necesario para decidir qué eventos son elegibles |
| `TA-SO-014` | Venue / exchange / TRF / tape | A/B/C1/C2 | Campos o metadata suficientes para identidad y dedupe | `TBD` | `REQUIRES_EVIDENCE` | No siempre será feature, pero puede ser imprescindible para calidad y duplicados |
| `TA-SO-015` | Estado original/corrección/cancelación | A/B/C1/C2 | Campo de acción o mensajes separados preservados | `TBD` | `REQUIRES_EVIDENCE` | Una tabla final corregida sin historial puede fallar el gate PIT |
| `TA-SO-016` | Referencia al evento original | A/B/C1/C2 | `original_trade_id`, correction id o linkage determinista | `TBD` | `REQUIRES_EVIDENCE` | Debe permitir aplicar revisiones as-of sin doble conteo |
| `TA-SO-017` | Late / out-of-sequence indicator | A/B/C1/C2 | Flag, condition code o evidencia reproducible | `TBD` | `REQUIRES_EVIDENCE` | Un trade tardío no puede insertarse retrospectivamente en un estado anterior |

## 7.3 Calidad, cobertura y reproducibilidad

| ID | Hecho físico requerido | Binding(s) | Evidencia mínima exigida | Mapping físico | Veredicto inicial | Restricción / pregunta de auditoría |
|---|---|---:|---|---|---|---|
| `TA-SO-018` | Evidencia de cobertura temporal | A/B/C1/C2 | Heartbeats, secuencias, manifests, logs de outage o control equivalente | `TBD` | `REQUIRES_EVIDENCE` | Sin cobertura demostrable no puede declararse `OBSERVED_ZERO` |
| `TA-SO-019` | Inicio y fin de cobertura por sesión | A/B/C1/C2 | Intervalos explícitos y versionados | `TBD` | `REQUIRES_EVIDENCE` | Debe detectar ventanas parcialmente observadas |
| `TA-SO-020` | Gaps y outages conocidos | A/B/C1/C2 | Registro físico de incidencias y regla de propagación | `TBD` | `REQUIRES_EVIDENCE` | El silencio del feed no equivale a ausencia de trades |
| `TA-SO-021` | Completitud de partición | A/B/C1/C2 | Conteos, checksums, manifests o validación equivalente | `TBD` | `REQUIRES_EVIDENCE` | Una partición presente no implica que esté completa |
| `TA-SO-022` | Política de duplicados | A/B/C1/C2 | Identificador o algoritmo de dedupe versionado y testeado | `TBD` | `REQUIRES_EVIDENCE` | No deduplicar por aproximación sin conservar evidencia |
| `TA-SO-023` | Política de mensajes fuera de orden | A/B/C1/C2 | Semántica documentada y test reproducible | `TBD` | `REQUIRES_EVIDENCE` | Debe separar pertenencia por `event_time` de legalidad por `available_at` |
| `TA-SO-024` | Historial de revisiones | A/B/C1/C2 | Mensajes originales + revisiones o snapshot bitemporal | `TBD` | `REQUIRES_EVIDENCE` | El estado final retrospectivo no basta para replay causal |
| `TA-SO-025` | Versionado del dataset | A/B/C1/C2 | `source_dataset_id`, versión, fecha y fingerprint | `TBD` | `REQUIRES_EVIDENCE` | Debe poder reconstruirse el mismo input exacto |
| `TA-SO-026` | Versionado de esquema | A/B/C1/C2 | Schema id/hash y fechas de vigencia | `TBD` | `REQUIRES_EVIDENCE` | Cambios de tipo o significado deben quedar detectados |
| `TA-SO-027` | Lineage y hashes de artefactos | A/B/C1/C2 | Source refs, content hashes y builder inputs | `TBD` | `REQUIRES_EVIDENCE` | Requisito de reproducibilidad y promoción posterior |
| `TA-SO-028` | Política raw/adjusted | A/B/C1/C2 | Declaración de si precio/tamaño son raw, corrected o adjusted | `TBD` | `REQUIRES_EVIDENCE` | No aplicar ajustes actuales retrospectivos sin contrato PIT |

---

## 8. Matriz de elegibilidad de trades

La política final debe mapear **cada código físico real de la fuente**. Esta matriz no puede cerrarse con categorías genéricas únicamente.

### 8.1 Acciones permitidas

| Acción | Significado |
|---|---|
| `INCLUDE` | El evento cuenta como trade elegible bajo la política indicada |
| `EXCLUDE` | El evento no cuenta como actividad transaccional elegible |
| `INCLUDE_WITH_RESTRICTIONS` | Solo se incluye bajo sesión, fuente o condición explícita |
| `REQUIRES_RESEARCH` | No existe evidencia suficiente para decidir todavía |
| `UNKNOWN_FAIL_CLOSED` | Código desconocido; no se incluye silenciosamente y degrada la ventana según contrato |

### 8.2 Matriz conceptual previa al mapping de códigos

| Clase de mensaje observada | Tratamiento causal candidato | ¿Cuenta como nuevo trade? | Efecto sobre estados anteriores | Evidencia pendiente |
|---|---|---:|---|---|
| Trade original elegible | Incluir desde su `available_at` si su condición está admitida | Sí | Ninguno | Mapping completo de condition codes |
| Trade original no elegible | Excluir | No | Ninguno | Regla por código |
| Trade tardío u out-of-sequence | Solo puede consumirse desde su `available_at`; pertenece a una ventana futura únicamente si su `event_time` aún cae dentro de esa ventana | Sí, cuando corresponda | No reescribe silenciosamente estados ya publicados | Semántica física de late flags y timestamps |
| Mensaje de corrección | Actualiza la versión as-of del trade original desde el `available_at` de la corrección | No | No muta el estado decision-safe anterior | Link al trade original y bitemporalidad |
| Mensaje de cancelación/delete | Invalida el trade original para construcciones posteriores a su `available_at` | No | No muta el estado decision-safe anterior | Link al original y acción física |
| Duplicado demostrado | Excluir mediante regla determinista | No | Ninguno | Identidad estable o dedupe verificable |
| Condición desconocida | `UNKNOWN_FAIL_CLOSED` | No por defecto | Ventana `DEGRADED` cuando afecte materialmente | Documentación oficial y versión |
| Registro agregado por proveedor | No asumir equivalencia con un trade individual | `TBD` | `TBD` | Debe demostrarse granularidad y semántica |

### 8.3 Regla de historial

Para un trade con revisiones:

```text
trade_version_as_of(t_a)
=
última versión del evento
cuyo available_at <= t_a
```

Nunca debe utilizarse:

```text
final_trade_version
```

para construir retrospectivamente un estado anterior si esa versión no estaba disponible en `t_a`.

---

## 9. Cobertura y estados de observación

### 9.1 Estados mínimos obligatorios

```text
OBSERVED_ZERO
OBSERVED_NONZERO
DEGRADED
UNAVAILABLE
```

| Estado | Condición mínima |
|---|---|
| `OBSERVED_ZERO` | Cobertura suficiente demostrada durante toda la ventana y cero trades elegibles |
| `OBSERVED_NONZERO` | Cobertura suficiente demostrada y uno o más trades elegibles |
| `DEGRADED` | Existe observación parcial o evidencia de gaps, condiciones desconocidas, partición incompleta o cobertura insuficiente para una afirmación plena |
| `UNAVAILABLE` | No existe evidencia física suficiente para representar la ventana |

Regla crítica:

```text
NO TRADES OBSERVED
+
NO COVERAGE EVIDENCE
≠
OBSERVED_ZERO
```

### 9.2 Denominador de intensidad

La variable estándar no debe dividir silenciosamente por los segundos observados de una ventana incompleta.

```text
IF coverage_state = SUFFICIENT:

    trade_arrival_rate_W
    =
    eligible_trade_count_W / elapsed_window_seconds_W

ELSE:

    trade_arrival_rate_W
    =
    NULL

    observation_state
    =
    DEGRADED or UNAVAILABLE
```

Una tasa ajustada por cobertura, si se investiga, debe ser una variable separada y explícita:

```text
coverage_adjusted_trade_arrival_rate_W
```

No pertenece automáticamente al Binding A ni sustituye a la tasa estándar.

### 9.3 Evidencia aceptable de cobertura

La auditoría debe determinar qué combinación de estas evidencias existe realmente:

- heartbeats del feed;
- secuencia continua de mensajes;
- manifests de captura;
- logs de inicio y fin de suscripción;
- logs de outage;
- checksums y completitud de particiones;
- comparación contra una fuente de control;
- ventanas de mercado oficialmente abiertas;
- contador de registros o mensajes esperado;
- metadata del proveedor sobre disponibilidad histórica.

La mera existencia de un archivo o partición no prueba cobertura suficiente.

---

## 10. Soporte para baselines con masa en cero

El baseline PIT no puede asumir distribuciones continuas con mediana y MAD positivos. En microcaps dormidas puede ocurrir:

```text
baseline_median = 0
MAD = 0
```

Por tanto, la fuente debe permitir reconstruir dos componentes separados:

```text
1. ACTIVITY PRESENCE PROCESS

   P(activity_W > 0 | PIT context)

2. POSITIVE ACTIVITY DISTRIBUTION

   F(activity_W | activity_W > 0, PIT context)
```

Requisitos de observabilidad para el documento posterior `TRADING_ACTIVITY_PIT_BASELINE_POLICY_v0_1.md`:

| ID | Requisito | Evidencia física necesaria | Veredicto inicial |
|---|---|---|---|
| `TA-BL-001` | Ventanas históricas realmente observadas con cero actividad | Cobertura suficiente por ventana | `REQUIRES_EVIDENCE` |
| `TA-BL-002` | Ventanas históricas con actividad positiva | Trades elegibles y coverage state | `REQUIRES_EVIDENCE` |
| `TA-BL-003` | Separación por premarket, regular y after-hours | Calendario y session phase reproducibles | `REQUIRES_EVIDENCE` |
| `TA-BL-004` | Bucket horario contextual | Timestamps normalizados y política DST | `REQUIRES_EVIDENCE` |
| `TA-BL-005` | Historial PIT sin revisiones futuras | Versionado as-of o replay de mensajes | `REQUIRES_EVIDENCE` |
| `TA-BL-006` | Días de referencia suficientes | Cobertura longitudinal y manifests | `REQUIRES_EVIDENCE` |
| `TA-BL-007` | Distinción sparse / zero-mass / unavailable | Estados de cobertura por ventana | `REQUIRES_EVIDENCE` |

No se autoriza todavía:

```text
arbitrary epsilon
arbitrary scale_floor
forced z-score when median = 0 and MAD = 0
```

La política de hurdle, percentiles empíricos y fallbacks se cerrará en el artefacto de baseline PIT.

---

## 11. Cardinalidad mínima y boundary censoring

La fuente puede contener los campos necesarios y aun así no permitir calcular una variable en una ventana concreta. Cada feature debe conservar un estado de suficiencia de muestra.

### 11.1 Estados de cálculo permitidos

```text
VALUE_AVAILABLE
OBSERVED_ZERO
INSUFFICIENT_SAMPLE
NOT_APPLICABLE
DEGRADED
UNAVAILABLE
```

### 11.2 Matriz inicial

| Familia candidata | Mínimo matemático | Umbral experimental | Boundary censoring | Estado si no cumple | Requisito de fuente |
|---|---:|---|---|---|---|
| `eligible_trade_count_W` | 0 trades | No aplica | No aplica | `OBSERVED_ZERO` solo con cobertura suficiente | Conteo completo de eventos elegibles |
| `eligible_share_volume_W` | 0 trades | No aplica | No aplica | `OBSERVED_ZERO` solo con cobertura suficiente | Tamaño válido de cada trade |
| `eligible_dollar_volume_W` | 0 trades | No aplica | No aplica | `OBSERVED_ZERO` solo con cobertura suficiente | Precio y tamaño válidos |
| `trade_arrival_rate_W` | 0 trades | No aplica | No aplica | `NULL + DEGRADED/UNAVAILABLE` si falla cobertura | Ventana completa y elapsed seconds |
| `median_intertrade_duration_W` | 2 trades in-window bajo política estricta | `TBD_BY_BINDING_SPEC` | No usar evento previo a la ventana hasta aprobar política | `INSUFFICIENT_SAMPLE` | Orden temporal y timestamps suficientes |
| `p10_intertrade_duration_W` | Al menos 1 duración | `N_MIN_P10_DURATION = TBD` | Política explícita obligatoria | `INSUFFICIENT_SAMPLE` | Precisión temporal y cardinalidad |
| `median_trade_size_W` | 1 trade | `N_MIN_MEDIAN_SIZE = TBD` | No aplica | `INSUFFICIENT_SAMPLE` bajo umbral gobernado | Tamaños válidos |
| `p90_trade_size_W` | 1 trade | `N_MIN_P90_SIZE = TBD` | No aplica | `INSUFFICIENT_SAMPLE` | Tamaños válidos y estimador de cuantiles versionado |
| `max_subwindow_trade_share_W_w` | Total trades > 0 | `TBD` | Bins cerrados causalmente | `NOT_APPLICABLE` cuando total = 0 | Event time y asignación a subventanas |
| `max_subwindow_volume_share_W_w` | Total volume > 0 | `TBD` | Bins cerrados causalmente | `NOT_APPLICABLE` cuando total = 0 | Tamaños y event time |
| `event_time_entropy_W_w` | Actividad positiva + binning definido | `N_MIN_ENTROPY_EVENTS = TBD` | Política de bins obligatoria | `NOT_APPLICABLE` o `INSUFFICIENT_SAMPLE` | Event time con resolución suficiente |
| `consecutive_active_subwindows_W_w` | Número mínimo de subventanas | `K_MIN_SUBWINDOWS = TBD` | Ventana completa | `INSUFFICIENT_SAMPLE` | Coverage state por subventana |
| Binding C1 / ACD | Estimador específico | `TBD_C1` | Left/right censoring explícito | `FIT_NOT_AVAILABLE` | Duraciones suficientes y convergencia |
| Binding C2 / Hawkes | Estimador específico | `TBD_C2` | Historia inicial explícita | `FIT_NOT_AVAILABLE` | Timestamps finos, secuencia y convergencia |

Regla crítica:

```text
0 trades
≠
median_intertrade_duration = 0
```

```text
1 trade
≠
intertrade duration = 0
```

La ausencia de cardinalidad suficiente debe conservarse como estado explícito, no convertirse en cero ni imputarse silenciosamente.

---

## 12. Requisitos por Experimental Physical Binding

### 12.1 Binding A — Minimal Multiscale Activity

| Capacidad fuente | Obligatoria | Estado |
|---|---:|---|
| Identidad canónica del instrumento | Sí | `REQUIRES_EVIDENCE` |
| `event_time` causal | Sí | `REQUIRES_EVIDENCE` |
| `available_at` o reconstrucción defendible | Sí | `REQUIRES_EVIDENCE` |
| Precio y tamaño | Sí | `REQUIRES_EVIDENCE` |
| Condiciones de trade | Sí | `REQUIRES_EVIDENCE` |
| Duplicados, correcciones y cancelaciones | Sí | `REQUIRES_EVIDENCE` |
| Cobertura suficiente para distinguir cero de unavailable | Sí | `REQUIRES_EVIDENCE` |
| Historial longitudinal para baseline PIT | Sí | `REQUIRES_EVIDENCE` |
| Resolución temporal suficiente para ventanas multiescala mínimas | Sí | `REQUIRES_EVIDENCE` |

**Regla de salida:** Binding A no puede pasar a especificación exacta hasta que todos sus requisitos obligatorios sean `OBSERVABLE` u `OBSERVABLE_WITH_RESTRICTIONS` compatibles.

### 12.2 Binding B — Marked Duration and Concentration

Requiere todo Binding A más:

| Capacidad fuente | Obligatoria | Estado |
|---|---:|---|
| Ordenación estable de eventos | Sí | `REQUIRES_EVIDENCE` |
| Resolución temporal suficiente para duraciones | Sí | `REQUIRES_EVIDENCE` |
| Cardinalidad suficiente por ventana | Sí | `REQUIRES_EVIDENCE` |
| Tamaños no agregados o granularidad demostrada | Sí | `REQUIRES_EVIDENCE` |
| Binning causal reproducible | Sí | `REQUIRES_EVIDENCE` |
| Boundary censoring gobernable | Sí | `REQUIRES_EVIDENCE` |

### 12.3 Binding C1 — Conditional Duration / ACD

Requiere todo Binding B más:

| Capacidad fuente | Obligatoria | Estado |
|---|---:|---|
| Duraciones suficientemente densas por unidad de ajuste | Sí | `REQUIRES_EVIDENCE` |
| Política de censoring y session reset | Sí | `REQUIRES_EVIDENCE` |
| Estado de ajuste, parámetros y convergencia | Sí | `REQUIRES_EVIDENCE` |
| Cobertura continua compatible con el estimador | Sí | `REQUIRES_EVIDENCE` |
| Reproducibilidad numérica del fit | Sí | `REQUIRES_EVIDENCE` |

### 12.4 Binding C2 — Self-Exciting Intensity / Hawkes

Requiere todo Binding B más:

| Capacidad fuente | Obligatoria | Estado |
|---|---:|---|
| Resolución temporal fina sin colapso masivo de timestamps | Sí | `REQUIRES_EVIDENCE` |
| Orden causal determinista para empates | Sí | `REQUIRES_EVIDENCE` |
| Historia inicial y truncamiento gobernados | Sí | `REQUIRES_EVIDENCE` |
| Estado de ajuste, parámetros y convergencia | Sí | `REQUIRES_EVIDENCE` |
| Tests de estabilidad y no explosión | Sí | `REQUIRES_EVIDENCE` |
| Reproducibilidad numérica del fit | Sí | `REQUIRES_EVIDENCE` |

C1 y C2 deben conservar artefactos de ajuste separados. No pueden combinarse en un único bundle opaco.

---

## 13. Política causal para eventos tardíos y revisiones

| Caso | Pertenencia por `event_time` | Consumible desde | Efecto en estado ya publicado | Efecto en estados futuros |
|---|---|---|---|---|
| Trade recibido a tiempo | Sí, si cae en `W` | `available_at_i` | Ninguno | Se incluye mientras caiga en la ventana |
| Trade tardío | Sí, si su `event_time` cae en la ventana consultada | Su `available_at_i`, nunca antes | No reescribe el estado anterior | Puede incluirse en un estado posterior si aún pertenece a su ventana causal |
| Corrección | Mantiene referencia al evento original | `available_at_correction` | No muta el estado decision-safe previo | La versión corregida rige para construcciones as-of posteriores |
| Cancelación | Invalida el evento original desde la cancelación | `available_at_cancel` | No muta el estado decision-safe previo | El original deja de ser elegible as-of posterior |
| Duplicado detectado posteriormente | Depende de cuándo se conoció la identidad duplicada | Desde la evidencia de dedupe | No muta silenciosamente | Se aplica a construcciones as-of posteriores |
| Mensaje fuera de secuencia | `event_time` gobierna pertenencia; `available_at` gobierna legalidad | `available_at` | No reordena retrospectivamente decisiones ya tomadas | Se procesa con tie-break determinista en futuros estados |

### 13.1 Requisito de materialización de revisiones

Una implementación válida debe conservar como mínimo:

```text
state_id
state_revision_id
supersedes_state_revision_id, cuando aplique
decision_timestamp
state_available_at
source_as_of
revision_reason
consumption_legality
```

La política exacta de revisión se cerrará en el `Temporal and Missingness Contract`, pero la fuente debe demostrar desde ahora que la reconstrucción as-of es físicamente posible.

---

## 14. Casos de prueba obligatorios para la auditoría

| Test ID | Escenario | Resultado obligatorio |
|---|---|---|
| `TA-ST-001` | Ventana completa sin trades y cobertura demostrada | `OBSERVED_ZERO` |
| `TA-ST-002` | Ventana sin trades pero con outage o gap | `DEGRADED` o `UNAVAILABLE`, nunca `OBSERVED_ZERO` |
| `TA-ST-003` | Un único trade elegible | Count/volume válidos; duraciones `INSUFFICIENT_SAMPLE` |
| `TA-ST-004` | Dos trades con el mismo timestamp | Orden determinista o restricción explícita |
| `TA-ST-005` | Trade tardío con `event_time` dentro de una ventana ya publicada | No altera silenciosamente el estado anterior |
| `TA-ST-006` | Corrección posterior de precio o tamaño | Versionado as-of reproducible |
| `TA-ST-007` | Cancelación posterior | Elegibilidad cambia solo desde `available_at_cancel` |
| `TA-ST-008` | Duplicado entre particiones | Dedupe determinista sin pérdida de lineage |
| `TA-ST-009` | Condition code desconocido | `UNKNOWN_FAIL_CLOSED` y degradación según contrato |
| `TA-ST-010` | Partición presente pero incompleta | No declarar cobertura suficiente |
| `TA-ST-011` | Cruce de premarket a regular session | Baselines y ventanas respetan session phase |
| `TA-ST-012` | Cambio DST | Normalización UTC reproducible |
| `TA-ST-013` | Empate de `available_at` entre mensajes | Tie-break estable y reproducible |
| `TA-ST-014` | Fuente que solo ofrece snapshot final corregido | `NOT_OBSERVABLE` para replay PIT si no existe historial equivalente |
| `TA-ST-015` | Timestamp redondeado que colapsa muchos eventos | Restricción explícita; posible bloqueo de C1/C2 |

---

## 15. Evidence Package exigido

La auditoría no puede cerrarse únicamente con nombres de columnas. Se requiere el siguiente paquete de evidencia física:

```text
01. Physical schema
02. Data dictionary
03. Sample records
04. Timestamp semantics
05. Timezone and precision documentation
06. Trade condition code documentation
07. Correction and cancellation semantics
08. Late / out-of-sequence semantics
09. Sequence and deterministic ordering policy
10. Duplicate policy
11. Coverage and outage evidence
12. Partition completeness evidence
13. Dataset version and content hashes
14. Schema version history
15. Historical revision behavior
16. Session/calendar mapping
17. Raw versus adjusted policy
18. Source license or consumption restrictions, when relevant
```

### 15.1 Muestra mínima recomendada

La muestra de auditoría debe incluir deliberadamente:

- una microcap dormida;
- una activación intensa;
- premarket;
- sesión regular;
- after-hours;
- una sesión con cero trades observados;
- una ventana con outage o gap;
- trades tardíos;
- correcciones;
- cancelaciones;
- duplicados;
- mensajes con condition codes poco frecuentes;
- varios eventos con timestamp idéntico;
- al menos un cambio de partición o día.

---

## 16. Procedimiento de auditoría

```text
STEP 1
Inventariar fuentes físicas candidatas
↓
STEP 2
Leer esquema y documentación oficial
↓
STEP 3
Mapear cada requisito TA-SO-001 ... TA-SO-028
↓
STEP 4
Inspeccionar muestras reales y edge cases
↓
STEP 5
Validar event_time / observed_at / available_at
↓
STEP 6
Validar condiciones, late, corrections y cancels
↓
STEP 7
Validar cobertura y legalidad de OBSERVED_ZERO
↓
STEP 8
Ejecutar TA-ST-001 ... TA-ST-015
↓
STEP 9
Emitir veredictos por requisito y por binding
↓
STEP 10
Emitir Source Observability Readout
```

### 16.1 Readout esperado

```text
TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_1.md
```

Debe declarar como mínimo:

```text
source_id
source_version
schema_fingerprint
coverage_scope
time_scope
session_scope
binding_A_status
binding_B_status
binding_C1_status
binding_C2_status
mandatory_failures
restrictions
unresolved_evidence
source_observability_gate
next_authorized_step
```

---

## 17. Reglas de decisión del hard gate

### 17.1 PASS para Binding A

```text
BINDING_A_SOURCE_OBSERVABILITY = PASS
```

solo cuando:

1. todos los campos obligatorios de Binding A sean `OBSERVABLE` o `OBSERVABLE_WITH_RESTRICTIONS` compatibles;
2. exista legalidad causal de `event_time` y `available_at`;
3. la fuente permita aplicar elegibilidad as-of;
4. correcciones y cancelaciones no exijan usar una versión final futura;
5. pueda distinguirse `OBSERVED_ZERO` de `DEGRADED` y `UNAVAILABLE`;
6. exista historial suficiente para comenzar el diseño del baseline PIT;
7. las pruebas obligatorias relevantes produzcan el resultado esperado;
8. dataset, esquema y lineage sean reproducibles.

### 17.2 PASS_WITH_RESTRICTIONS

Puede emitirse cuando Binding A sea viable, pero exista alguna limitación explícita como:

- periodo histórico acotado;
- sesión no cubierta;
- resolución insuficiente para Binding B, C1 o C2;
- ausencia parcial de venue metadata;
- C1/C2 no soportados;
- condition codes pendientes fuera de un subconjunto controlado.

Toda restricción debe quedar codificada. No puede permanecer como comentario informal.

### 17.3 FAIL

El gate debe fallar, entre otros casos, si:

```text
available_at is not observable or reproducible
```

```text
only final corrected history exists
and as-of reconstruction is impossible
```

```text
zero activity cannot be distinguished from missing coverage
```

```text
trade eligibility cannot be reconstructed
```

```text
duplicates or revisions can materially inflate activity
without deterministic treatment
```

```text
source identity, schema or version cannot be reproduced
```

### 17.4 Estado actual

```text
OVERALL SOURCE OBSERVABILITY GATE
=
REQUIRES_EVIDENCE

reason
=
physical trade schema, timestamp semantics,
condition-code policy, revision behavior
and coverage evidence have not yet been audited
```

---

## 18. Criterio de salida de este artefacto

Este documento puede pasar a `SOURCE_AUDIT_CLOSED` cuando se hayan completado:

```text
1. Source Observability Matrix
2. Trade Eligibility Mapping
3. Coverage Evidence Assessment
4. Late / Correction / Cancellation Assessment
5. Binding A Source Verdict
6. Restrictions Register
7. Source Observability Readout
```

El cierre de este documento autoriza únicamente el siguiente trabajo:

```text
TRADING_ACTIVITY_PIT_BASELINE_POLICY_v0_1.md
↓
TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_1.md
↓
TRADING_ACTIVITY_TEMPORAL_AND_MISSINGNESS_CONTRACT_v0_1.md
```

No autoriza todavía:

```text
canonical implementation
output table creation
Market State consumption
Event State consumption
backtest consumption
production
downstream
```

---

## 19. Registro de decisiones pendientes

| Decision ID | Pregunta | Autoridad futura | Estado |
|---|---|---|---|
| `TA-DEC-001` | ¿Qué fuente física de trades será primaria? | Source Audit Readout | `OPEN` |
| `TA-DEC-002` | ¿Cómo se deriva o registra `available_at`? | Temporal Contract | `OPEN` |
| `TA-DEC-003` | ¿Qué condition codes son elegibles? | Trade Eligibility Policy | `OPEN` |
| `TA-DEC-004` | ¿Qué evidencia basta para declarar cobertura suficiente? | Coverage Contract | `OPEN` |
| `TA-DEC-005` | ¿Qué política exacta gobierna state revisions? | Temporal and Missingness Contract | `OPEN` |
| `TA-DEC-006` | ¿Se permite left-boundary carry-in para duraciones? | Binding B Specification | `OPEN` |
| `TA-DEC-007` | ¿Cuáles son los mínimos de cardinalidad por feature? | Binding A/B Exact Specifications | `OPEN` |
| `TA-DEC-008` | ¿Qué estructura hurdle/zero-inflated se utiliza? | PIT Baseline Policy | `OPEN` |
| `TA-DEC-009` | ¿La resolución soporta C1? | C1 Source/Estimator Assessment | `OPEN` |
| `TA-DEC-010` | ¿La resolución soporta C2? | C2 Source/Estimator Assessment | `OPEN` |
| `TA-DEC-011` | ¿Qué variables concretas son elegibles para promoción? | Promotion Validation | `NOT_STARTED` |
| `TA-DEC-012` | ¿Dónde se materializan las variables promovidas? | Output Table Mapping | `NOT_STARTED` |

---

## 20. Trazabilidad con la arquitectura TSIS

Este artefacto implementa la frontera:

```text
FENÓMENO OBSERVABLE
↓
INFORMATION OBJECT
↓
REPRESENTATION MODEL
↓
VARIABLES / FEATURES
↓
TABLES
```

pero se detiene deliberadamente antes del mapping de salida:

```text
CURRENT STEP
=
SOURCE OBSERVABILITY FOR EXPERIMENTAL PHYSICAL BINDINGS

NOT YET
=
CANONICAL FEATURES OR OUTPUT TABLES
```

Principios preservados:

```text
Information Object
=
significado estable

Representation Model
=
dimensiones conceptuales

Experimental Physical Binding
=
variables, fórmulas y fuentes candidatas

Canonical Physical Implementation
=
solo variables promovidas después de validación

Table
=
lugar posterior de materialización
```

---

## 21. Referencias internas de autoridad

- `00_TABLES_MARKET_STATE_EVENT_STATE(20260806-132625).md`
  - perfil candidato de objetos para `Wake-up`;
  - modelo candidato de `Trading Activity`;
  - temporalidad causal;
  - calidad y cobertura;
  - transición hacia `VARIABLES / FEATURES`.

- `00_TABLES_MARKET_STATE_EVENT_STATE.md`
  - principio fundacional `Information Objects → Models → Variables → Tables`;
  - separación entre implementación física y materialización en tablas;
  - lineage, disponibilidad temporal y consumo fail-closed.

---

## 22. Change Log

| Versión | Fecha | Cambio |
|---|---|---|
| `v0_1` | `2026-08-06` | Creación inicial del hard gate de observabilidad física para `Trading Activity`; separación A/B/C1/C2; causal set bitemporal; cobertura; zero-mass baselines; cardinalidad; revisiones; tests y exit criteria |

---

```text
END STATE OF THIS VERSION
=========================

DOCUMENT_STATUS                = DRAFT
WORKFLOW_STATUS                = READY_FOR_SOURCE_AUDIT
SOURCE_AUDIT_STATUS            = NOT_EXECUTED
SOURCE_OBSERVABILITY_GATE      = REQUIRES_EVIDENCE
BINDING_A_EXACT_SPECIFICATION  = NOT_AUTHORIZED_YET
OUTPUT_TABLE_MAPPING           = NOT_STARTED
CANONICAL_PROMOTION            = NOT_AUTHORIZED
FREEZE_STATUS                  = NOT_READY_FOR_FREEZE
```
