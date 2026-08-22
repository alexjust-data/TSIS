# Wake-Up RTH Discovery Variables and Blind-Panel Construction v0.1

Estado: `provisional`

Scope: `development-only`, `representation-neutral`, `candidate-reduction-only`

Experimento: `EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001`

Este documento describe las variables experimentales que produjeron el pool de
4.447 candidatos y la seleccion estratificada de 240 casos. No define un
detector Wake-Up congelado, no implementa Binding A o Binding B y no autoriza
la comparacion A/B.

# 1. Quien creo las variables de descubrimiento

La autoridad ejecutable esta en:

- `03_TSIS_Lab/04_experiments/EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001/scripts/wake_up_rth_core.py:228`
- `03_TSIS_Lab/04_experiments/EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001/scripts/build_wake_up_rth_candidate_pool.py`
- `03_TSIS_Lab/04_experiments/EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001/configs/wake_up_rth_calibration_v0_1.json`
- `03_TSIS_Lab/04_experiments/EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001/scripts/build_wake_up_blind_panel.py`

Operativamente fueron creadas como parte de:

```text
EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001
```

Pero existe una carencia de gobierno:

```text
scientific_owner = no declarado
author = no declarado
threshold_decision_owner = no declarado
```

La configuracion declara:

```text
status = DEVELOPMENT_ONLY_NOT_FROZEN
```

Por tanto, esas variables y parametros son una implementacion experimental
trazable por codigo, pero no son todavia una definicion cientifica congelada de
Wake-Up.

---

# 2. Datos fuente utilizados

El discovery no consumio Binding A ni Binding B.

Consumio directamente:

```text
trades raw gobernados
+
trade-condition eligibility policy
+
market calendar
+
2.400 target sessions congeladas
```

Columnas raw leidas:

```text
ticker
date
timestamp
price
size
exchange
conditions
```

La elegibilidad de cada trade se determino mediante la policy de Data
Foundation.

Solo despues se agregaron los trades elegibles sobre una rejilla RTH por
segundo.

---

# 3. Rejilla temporal

Para cada sesion se construyo:

```text
calendar open + 1 segundo
->
calendar close - 1 segundo
```

Cada trade se hacia disponible mediante:

```text
available_timestamp
=
source_timestamp + 1.000 ms de latencia simulada
```

Despues se asignaba al primer segundo de decision legal:

```text
decision_timestamp
=
ceil(available_timestamp, 1 segundo)
```

Esto produjo una fila por cada symbol-second RTH elegible.

---

# 4. Variables base calculadas por segundo

El codigo construyo seis variables principales.

## `trade_count`

Numero de trades elegibles disponibles en el segundo.

Responde a:

```text
¿Aumento el ritmo de participacion?
```

## `share_volume`

Suma del tamano de los trades elegibles.

Responde a:

```text
¿Cuantas acciones participaron?
```

Se calculo y conservo, pero no entro directamente en el score que produjo los
candidatos.

## `dollar_volume`

```text
Σ(price x size)
```

Solo para trades con elegibilidad nocional.

Responde a:

```text
¿La actividad tiene alguna materialidad economica?
```

Importante: no se uso la trayectoria del precio como patron. El precio se
utilizo unicamente para calcular valor nocional.

## `distinct_timestamp_clusters`

Numero de timestamps raw distintos con trades elegibles.

Responde a:

```text
¿La actividad procede de varios eventos
o solamente de uno o varios prints empatados?
```

No afirma orden causal dentro de trades que comparten timestamp.

## `duplicate_trade_count`

Numero de trades que forman duplicados exactos.

Responde a:

```text
¿El supuesto movimiento puede ser un artefacto de duplicacion?
```

## `restricted_or_unknown_trade_count`

Numero de trades rechazados o no clasificables por la policy.

Responde a:

```text
¿La evidencia posee calidad suficiente?
```

---

# 5. Como se construyo un candidato

Para cada segundo `t` se combinaron ventanas anteriores y posteriores.

## Ventanas de regimen previo

```text
15 minutos = 900 segundos
30 minutos = 1.800 segundos
60 minutos = 3.600 segundos
```

Estas ventanas intentan representar el regimen anterior:

```text
¿El instrumento estaba dormido
o tenia una determinada actividad contextual?
```

## Horizontes retrospectivos de confirmacion

```text
30 segundos
60 segundos
120 segundos
300 segundos
```

Estos horizontes miran despues de `t`.

Por eso:

```text
future_window_used = true
consumption_legality = OUTCOME_ONLY
```

No son variables utilizables por un detector live.

---

# 6. Variables anteriores y posteriores

Para cada combinacion de ventanas se calcularon:

```text
prior_trade_count
prior_cluster_count
prior_dollar_volume

confirmation_trade_count
confirmation_cluster_count
confirmation_dollar_volume
```

Habia:

```text
3 dormancy windows
x
4 confirmation windows
=
12 configuraciones por segundo
```

---

# 7. Normalizacion del contexto anterior

No se comparaban directamente totales de ventanas con duraciones distintas.

Para cada dimension se estimaba cuanto cabria esperar durante el horizonte de
confirmacion:

```text
expected_trade
=
prior_trade_count
x confirmation_seconds
/ prior_observed_seconds
```

Lo mismo para clusters y dollar volume:

```text
expected_cluster
=
prior_cluster_count
x confirmation_seconds
/ prior_observed_seconds
```

```text
expected_dollar
=
prior_dollar_volume
x confirmation_seconds
/ prior_observed_seconds
```

Esto convierte el regimen previo en una expectativa comparable.

---

# 8. Score exacto de descubrimiento

El score fue:

```text
candidate_reduction_score
=
log1p(confirmation_trade_count)
- log1p(expected_trade_count)

+
log1p(confirmation_cluster_count)
- log1p(expected_cluster_count)

+
log1p(confirmation_dollar_volume)
- log1p(expected_dollar_volume)
```

Conceptualmente:

```text
sorpresa en numero de trades
+
sorpresa en eventos temporalmente distintos
+
sorpresa en valor nocional
```

Un score alto significa:

> Durante el horizonte posterior aparecio mucha mas actividad de la esperada a
> partir del regimen anterior.

No significa todavia:

> Este segundo es definitivamente un Wake-Up.

---

# 9. Filtros minimos aplicados

Para ser candidato se exigia:

```text
confirmation_trade_count >= 2
confirmation_cluster_count >= 2
al menos 60 segundos de sesion observados
```

La exigencia de dos clusters buscaba evitar que un unico timestamp o print
aislado produjera un candidato.

Sin embargo, no existia todavia:

```text
threshold cientifico congelado del score
de-minimis dollar threshold congelado
Wake-Up classification threshold
```

El sistema seleccionaba los scores mas altos, no los casos que superaban una
definicion final.

---

# 10. Reduccion y deduplicacion

Para cada una de las 12 combinaciones:

```text
se conservaban los 4 scores mas altos
```

Despues:

```text
candidatos separados por <= 300 segundos
-> se consideraban parte de la misma zona
-> se conservaba el de mayor score
```

Limite final:

```text
maximo 12 candidatos por sesion
```

Resultado:

```text
2.400 sesiones
-> 4.447 candidatos no etiquetados
```

El estado escrito en los candidatos es explicito:

```text
UNLABELED_CANDIDATE_REDUCTION_ONLY
```

---

# 11. Los 4.447 candidatos no se convirtieron directamente en 240 casos

Los 240 casos contienen:

```text
40 candidatos de transicion
+
200 controles
```

La composicion exacta fue:

```text
4 cohorts
x
6 roles
x
10 casos
=
240 casos
```

Los cuatro cohorts fueron:

```text
D1
D2
D3
D4
```

Los seis roles fueron:

```text
CANDIDATE_ACTIVITY_TRANSITION
CONTROL_DORMANT
CONTROL_ONE_CLUSTER
CONTROL_CONTEXT_NORMAL_ACTIVITY
CONTROL_QUALITY_OR_ARTIFACT
CONTROL_RANDOM_ELIGIBLE
```

Por tanto:

```text
CANDIDATE_ACTIVITY_TRANSITION
4 cohorts x 10
=
40 casos
```

Y:

```text
5 tipos de control
x 4 cohorts
x 10
=
200 controles
```

Esto es importante: solo 40 de los 240 casos proceden del pool de posibles
transiciones.

---

# 12. Como se crearon los controles

## `CONTROL_DORMANT`

```text
prior_trade_count_900s == 0
confirmation_trade_count_60s == 0
```

Representa:

```text
regimen dormido
-> continua dormido
```

## `CONTROL_ONE_CLUSTER`

```text
confirmation_cluster_count_60s == 1
confirmation_trade_count_60s >= 1
```

Representa:

```text
actividad procedente de un solo timestamp cluster
```

Sirve para comprobar si los revisores confunden un print aislado con Wake-Up.

## `CONTROL_CONTEXT_NORMAL_ACTIVITY`

Se calculan tasas:

```text
prior_rate  = prior_trades_900s / 900
future_rate = future_trades_60s / 60
ratio       = future_rate / prior_rate
```

Se exige:

```text
prior_trade_count_900s >= 10
confirmation_trade_count_60s >= 2
0.5 <= rate_ratio <= 2.0
```

Representa:

```text
actividad existente
-> continua aproximadamente dentro de su regimen normal
```

## `CONTROL_QUALITY_OR_ARTIFACT`

```text
duplicate_trade_count
+
restricted_or_unknown_trade_count
>
0
```

Representa casos donde la evidencia puede estar contaminada.

## `CONTROL_RANDOM_ELIGIBLE`

Segundo aleatorio que:

```text
source_state == OBSERVED
posicion >= open + 900 segundos
posicion < close - 300 segundos
```

Sirve para estimar falsas activaciones sobre exposicion ordinaria.

---

# 13. Variables utilizadas para estratificar los 240 casos

Estas variables no encontraron Wake-Up. Solo aseguraron diversidad en la
muestra.

## Momento RTH

```text
OPEN_0_60M
MID_60_240M
CLOSE_240M_PLUS
```

## Precio presesion

```text
$0.50-1
$1-2
$2-5
$5-10
$10-20
```

## Market-cap proxy

```text
< $10M
$10-25M
$25-50M
$50-100M
```

## Actividad anterior

```text
PRIOR_ZERO
PRIOR_LOW
PRIOR_ACTIVE
```

## Calidad

```text
QUALITY_CLEAR
QUALITY_FLAGGED
```

La seleccion utilizo semilla determinista:

```text
20260817
```

---

# 14. Por que se eligieron estas variables

La logica cientifica fue:

| Necesidad | Variable experimental |
|---|---|
| Regimen dormido anterior | `prior_trade_count`, `prior_cluster_count`, `prior_dollar_volume` |
| Aparicion de actividad | equivalentes `confirmation_*` |
| Sorpresa relativa | diferencia logaritmica frente a expectativa |
| Corroboracion multievento | `distinct_timestamp_clusters` |
| Materialidad economica | `dollar_volume` |
| Rechazo de artefactos | duplicados y condiciones restringidas |
| Cobertura y abstencion | `source_state` |
| Diversidad de calibracion | strata temporal, precio, market cap, actividad y calidad |

Se eligieron porque son:

```text
simples
interpretables
representation-neutral
de alta sensibilidad
calculables directamente desde trades gobernados
independientes de Binding A y Binding B
```

Pero hay que ser rigurosos: la documentacion no demuestra todavia por que los
valores exactos `15/30/60m`, `30/60/120/300s`, minimo 2 trades, minimo 2
clusters o merge de 300s son cientificamente optimos.

Son una rejilla amplia de discovery:

```text
development-only
not frozen
candidate reduction only
```

Precisamente los 240 casos se crearon para obtener evidencia humana con la que
decidir posteriormente los parametros definitivos.

---

# 15. Que falta definir despues de revisar los 240 casos

Las variables anteriores solo generan candidatos. La revision debe resolver:

```text
WUL-D01 = horizonte retrospectivo de confirmacion
WUL-D02 = estimador/lookback de regimen dormido
WUL-D03 = regla de anomalia relativa
WUL-D04 = suelo economico de minimis
WUL-D05 = quorum de clusters/fuentes
WUL-D06 = cobertura y resolucion minimas
WUL-D07 = cierre, reset y rearm del episodio
WUL-D08 = oracle primario determinista o adjudicado
```

Estas son las decisiones que convertiran la busqueda amplia en una definicion
formal del evento.
