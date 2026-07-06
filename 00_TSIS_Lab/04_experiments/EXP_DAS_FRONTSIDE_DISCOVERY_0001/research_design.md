# Research Design - EXP_DAS_FRONTSIDE_DISCOVERY_0001

Fecha: 2026-07-05
Estado: draft

## 1. Pregunta General

```text
Dentro de small/micro caps que el screener humano podia ver en premarket,
que estructura observable diferencia un frontside/DAS sano de un push que se destruye?
```

Este experimento no pregunta todavia si DAS gana dinero. Pregunta primero si podemos convertir una observacion visual humana en fenomenos medibles, reproducibles y separables.

## 2. Origen Humano Del Experimento

Este experimento nace de la estrategia humana DAS (`Dips After Squeeze`) documentada en:

```text
C:/TSIS_Data/00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/STRATEGY.md
C:/TSIS_Data/00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/notebooks/das_case_explorer.ipynb
C:/TSIS_Data/00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/scripts/das_widgets.py
```

El flujo original era visual y discrecional:

```text
screener small/micro cap
-> ticker visible/in-play
-> push agresivo en premarket
-> imagen/chart
-> revision humana de frontside
-> estudio de primer push, primer dip, rebreak y secuencia DAS
```

Por tanto, este experimento no es una busqueda ciega de cualquier momentum intradia. Es un experimento `strategy_seeded`: usa una intuicion humana como semilla, pero no acepta esa intuicion como verdad.

## 3. Que Queremos Convertir En Ciencia

La estrategia humana dice, de forma aproximada:

```text
small cap despierta con push violento
-> primer dip no destruye estructura
-> precio recupera o rompe el high del primer push
-> shorts quedan bajo presion
-> aparecen dips posteriores operables dentro del frontside
```

La version cientifica debe separar:

```text
universo / dominio
scanner / visibilidad
sampling probe
objetos frontside
lectura DAS
outcomes
validacion
```

## 4. Capas Del Experimento

### 4.1. Dominio

```text
market_cap < 100M
```

Esta condicion define la linea de investigacion small/micro cap. En v0.1 queda fija. Si TSIS quiere estudiar movimientos similares en empresas mayores, eso debe ser otro experimento o una extension versionada.

### 4.2. Screener / Visibilidad

Valores semilla del notebook/script:

```text
session_volume >= 500000
0.5 <= price <= 20
session_scope = premarket
```

Estos valores no son verdad cientifica. Son la forma historica en la que el humano buscaba tickers negociables/visibles. Deben estudiarse como parametros investigables.

### 4.3. Sampling Probe

Valor humano historico:

```text
momentum_trigger_pct = 50
```

El `+50%` fue una herramienta para cazar movimientos frontside visualmente interesantes. No es evento validado, no es edge, no es threshold optimo y no debe entrar como verdad base de estado.

### 4.4. Objetos Frontside

Objetos que debe medir el experimento:

```text
AwakeningEpisode
FirstPush
FirstPullback
StructuralRebreak
DASSequence
MomentumEnd
FailureMode
```

Estos objetos pertenecen al laboratorio de investigacion. No son todavia `market_state_table` oficial ni `event_state_table` oficial.

### 4.5. Lectura DAS

DAS no empieza en cualquier dip. DAS empieza cuando un primer push demuestra despertar, el primer dip no destruye estructura y el mercado recupera o rompe el high estructural del primer push.

## 5. Parametros Semilla Y Mutabilidad

| Parametro | Valor semilla | Lectura v0.1 | Mutable en research |
| --- | ---: | --- | --- |
| `max_market_cap_usd` | 100000000 | frontera de dominio small/micro cap | no en este experimento |
| `min_session_volume` | 500000 | gate humano de liquidez/visibilidad | si |
| `min_price` | 0.5 | piso operativo humano | si |
| `max_price` | 20.0 | techo operativo humano para esta estrategia | si, dentro de investigacion controlada |
| `session_scope` | premarket | origen principal de la estrategia | si, en sweep posterior |
| `push_label_pct` | 20 | detector humano de primer push | si |
| `dip_label_pct` | 3 | detector humano de primer dip | si |
| `momentum_trigger_pct` | 50 | criba humana de operabilidad frontside | si |

La regla es:

```text
seed_value != verdad cientifica
seed_value != parametro optimo
seed_value = punto de partida reproducible
```

## 6. Por Que El Primer Sweep Busca La Frontera De Operabilidad Frontside

El primer sweep no intenta encontrar el mejor porcentaje para operar. Tampoco trata `+50%` como entrada, evento validado o verdad cientifica.

La pregunta correcta es:

```text
Donde empieza la zona minima de operabilidad del frontside para estudiar longs DAS?
```

La filosofia humana detras del `+50%` era una criba practica:

```text
si el movimiento no es suficientemente fuerte,
no entra en la posibilidad real de estudiar long DAS/frontside.
```

Por eso, en `SWEEP_001`, los valores por debajo de `50%` no son candidatos long DAS por defecto. Son grupo de control para comprobar si la criba humana excluia correctamente movimientos insuficientes. El `50%` es el suelo humano historico a auditar. Los valores por encima de `50%` miden intensidad creciente del frontside y tambien posible sobreextension o llegada tarde.

Lectura del sweep:

```text
20/30/40 = control bajo la frontera humana de operabilidad
50       = frontera humana historica
60/75/100/150 = intensidad frontside creciente y posible sobreextension
```

La razon de empezar aqui es que `+50%` fue el filtro visual humano mas cargado conceptualmente. Si no entendemos si ese corte separa ruido, frontside operable o sobreextension, cualquier estadistica posterior sobre dip, rebreak, volumen o outcome queda contaminada.

## 7. Que No Responde El Primer Sweep

No responde:

- si DAS tiene edge operable;
- si `50%` es el threshold optimo;
- si la estrategia es valida;
- si el mejor rango de volumen es `500k`;
- si el mejor rango de precio es `0.5-20`;
- si afterhours o regular son mejores que premarket;
- si `push_label_pct=20` o `dip_label_pct=3` son buenos;
- si AlphaEvolve debe mutar esta estrategia.

## 8. Caveat Tecnico Sobre El Script DAS Actual

El script historico `das_widgets.py` incluye `momentum_trigger_pct`, pero la seleccion principal de candidatos DAS/frontside se apoya en la secuencia:

```text
first push
-> first dip
-> structural rebreak
```

Por tanto, no debemos asumir que cambiar `momentum_trigger_pct` en el widget historico equivale automaticamente a ejecutar un sweep poblacional correcto.

El ejecutor del Lab debe implementar explicitamente el sampling probe:

```text
primer timestamp donde high 1m >= reference_price * (1 + threshold_pct / 100)
```

y despues medir si aparece o no la estructura DAS/frontside.

## 9. Relacion Con State Tables

El experimento consume estado y outcomes, pero no los redefine:

```text
X = estado legal/as-of, scanner lineage y objetos frontside bajo cutoff
y = outcomes separados
experimento = forma declarativa de mirar X e y
```

Nunca debe copiar outcomes dentro del estado.

## 10. Denominador Correcto

El run DAS actual sirve para aprender forma y depurar detector:

```text
das_scanner_appearance_20260628T114046Z
candidate_count = 679
scope = conditional_on_current_das_detector
```

Pero no es denominador poblacional completo. Para estadistica institucional hace falta:

```text
daily_scanner_candidates_table_v0_2_or_successor
```

o un denominador equivalente que diga todos los tickers que estaban vivos/visibles/in-play, no solo los que el detector DAS ya encontro.

## 11. Gramatica DAS De Objetos Medibles

La secuencia DAS no debe tratarse como una imagen unica ni como un unico threshold.
Debe convertirse en objetos medibles:

```text
scanner seed
-> awakening
-> first push
-> first dip
-> rebreak
-> DAS sequence
-> outcome
```

Cada objeto debe producir observables propios.

### 11.1. Scanner Seed

Representa que el ticker podia ser visible para el humano o para un scanner gobernado.

Ejemplos de observables:

```text
market_cap
price_at_visibility
session_volume_at_visibility
time_of_day
scanner_trigger_ts
scanner_trigger_quality
```

Lectura:

```text
scanner seed = donde mirar
scanner seed != DAS
scanner seed != edge
```

### 11.2. Awakening

Representa el paso desde estado dormido a actividad relevante.

Ejemplos de observables:

```text
awakening_start_ts
awakening_start_price
volume_expansion
range_expansion
minutes_from_premarket_open
```

### 11.3. First Push

Representa el primer impulso que cambia el estado del ticker.

Ejemplos de observables:

```text
first_push_start_ts
first_push_high_ts
first_push_high
first_push_pct_from_pm_open
first_push_pct_from_push_start
first_push_duration_minutes
first_push_volume
first_push_slope
first_push_wick_body_structure
```

Parametros investigables:

```text
push_label_pct
reference_price
maximum_allowed_duration
minimum_volume_during_push
```

### 11.4. First Dip / First Pullback

Representa la primera correccion tras el primer push.

Ejemplos de observables:

```text
first_dip_low_ts
first_dip_low
first_dip_depth_pct
first_dip_duration_minutes
first_push_retention_pct
vwap_respected
structure_destroyed
seller_volume
```

Parametros investigables:

```text
dip_label_pct
retention_threshold
vwap_respect_policy
maximum_dip_duration
```

### 11.5. Structural Rebreak

Representa si el precio recupera o rompe el nivel estructural relevante despues del dip.

Ejemplos de observables:

```text
rebreak_ts
rebreak_price
rebreak_type
minutes_to_rebreak
rebreak_volume
close_above_required_level
vwap_reclaim
```

Tipos iniciales:

```text
first_push_high_break
last_red_high_break
single_candle_rebreak
ascending_flag_break
flat_shelf_break
vwap_reclaim_rebreak
multi_candle_flag_break
unclear
```

### 11.6. Momentum State

Representa el tamano y velocidad del movimiento, sin convertir un threshold en verdad.

Ejemplos de observables:

```text
momentum_trigger_pct
momentum_trigger_ts
max_momentum_pct_from_pm_open
max_momentum_pct_from_push_start
time_to_momentum_trigger
momentum_end_ts
momentum_end_reason
```

El `+50%` vive aqui como sampling probe humano o como parametro investigable, no como evento validado.

### 11.7. DAS Sequence

Representa si, despues del rebreak, el ticker entra en una secuencia frontside donde los dips posteriores pueden estudiarse.

Ejemplos de observables:

```text
das_sequence_active
das_entry_count
first_green_wick_dip_ts
frontside_state
momentum_end_ts
backside_damage_reason
```

### 11.8. Outcome

Representa lo que paso despues y siempre debe quedar separado de X.

Ejemplos:

```text
MFE
MAE
return_30m
continuation
failure
backside_damage
halt_after_event
```

Regla:

```text
X = objetos observables bajo cutoff legal
y = outcomes separados
```

## 12. Como Descubriremos Que Factores Importan

No vamos a decidir a mano que factor es el mas importante.
Primero medimos todos los objetos de la secuencia y despues dejamos que la evidencia ordene la importancia.

La ruta correcta es:

```text
1. medicion base de objetos DAS
2. estadistica univariable
3. sweeps de sensibilidad de un parametro cada vez
4. interacciones simples entre objetos
5. modelos interpretables como brujula, no como verdad final
6. AlphaEvolve solo despues de executor, validators y evaluadores versionados
```

### 12.1. Medicion Base

Para cada ticker/session candidato se deben medir observables neutrales:

```text
push_pct
push_duration_minutes
dip_depth_pct
first_push_retention_pct
minutes_to_rebreak
rebreak_type
volume_at_push
volume_at_rebreak
time_of_day
price_bucket
liquidity_bucket
momentum_trigger_pct_bucket
coverage_state
quality_state
outcome
```

### 12.2. Estadistica Univariable

Primero se estudia cada variable por separado:

```text
outcome vs push_pct
outcome vs dip_depth_pct
outcome vs retention_pct
outcome vs rebreak_type
outcome vs minutes_to_rebreak
outcome vs time_of_day
outcome vs volume/liquidity
outcome vs price_bucket
outcome vs momentum_threshold
```

Esto no valida edge. Sirve para saber donde hay estructura.

### 12.3. Sweeps De Sensibilidad

Despues se cambia un parametro cada vez:

```text
momentum_trigger_pct
min_session_volume
price_bucket
push_label_pct
dip_label_pct
session_scope
```

Si cambiamos todo a la vez, no sabremos que produjo el cambio.

### 12.4. Interacciones Simples

Cuando existan resultados univariables, se estudian pares:

```text
push_pct + dip_depth_pct
push_pct + rebreak_type
dip_depth_pct + retention_pct
volume + time_of_day
price_bucket + liquidity
momentum_threshold + rebreak_speed
```

### 12.5. Modelos Interpretables

Solo despues se pueden usar modelos interpretables para ranking de importancia:

```text
logistic regression regularizada
arboles simples
gradient boosting con constraints de leakage
permutation importance
SHAP exploratorio
```

Lectura correcta:

```text
modelo interpretable = brujula de investigacion
modelo interpretable != verdad causal
modelo interpretable != estrategia validada
```

### 12.6. AlphaEvolve

AlphaEvolve no debe empezar optimizando entradas.
Debe poder proponer cambios declarativos sobre:

```text
sampling probes
parametros de objetos DAS
representaciones de estado
reglas de deteccion
interacciones entre objetos
evaluadores exploratorios
```

Pero solo cuando existan:

```text
executor reproducible
validators de leakage/calidad/lineage
evidence reports
promotion gates
fitness/evaluator versionado
```

## 13. Ruta De Sweeps DAS/Frontside

La ruta inicial queda:

```text
SWEEP_001 frontside_operability_boundary / momentum_trigger_pct
SWEEP_002 min_session_volume
SWEEP_003 price buckets dentro de 0.5-20
SWEEP_004 push_label_pct
SWEEP_005 dip_label_pct / retention
SWEEP_006 session_scope / time of day
SWEEP_007 rebreak_type / timing
SWEEP_008 interaccion push + dip + rebreak
SWEEP_009 ranking interpretable de factores
```

Cada sweep debe declarar:

```text
pregunta cientifica
parametro que cambia
variables que quedan fijas
outcomes medidos
que no responde
como interpretar resultados
por que no promueve automaticamente evento/estrategia
```

### 13.1. Lectura Especial De SWEEP_001

`SWEEP_001_frontside_operability_boundary` debe leerse como auditoria de frontera de operabilidad, no como optimizacion de threshold.

```text
threshold < 50%  = grupo de control bajo la frontera humana
threshold = 50%  = suelo operativo humano a auditar
threshold > 50%  = intensidad frontside creciente y posible sobreextension
```

La medicion importante no es solo retorno final. Tambien hay que medir el embudo:

```text
scanner seed
-> momentum trigger
-> first push
-> first dip
-> rebreak
-> DAS sequence
-> continuation/failure
```

Si los thresholds bajos producen muchos casos pero pocos llegan a rebreak o a DAS sequence, eso apoyaria la intuicion humana de que bajo cierto movimiento no hay frontside operable. Si thresholds altos llegan a rebreak pero dejan poco upside posterior o mucho MAE, eso indicaria posible sobreextension.

## 14. Resultado Esperado De Esta Fase

Esta fase debe producir:

```text
parameter_space.yaml
SWEEP_001_frontside_operability_boundary.yaml
ejecutor SmallCaps pendiente
manifest por run pendiente
evidence report pendiente
```

Hasta que no exista evidencia, nada se promueve a evento validado, estrategia validada ni evaluador bloqueado.





