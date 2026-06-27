# Multi-Day Top Risk Reward Strategy - Duxinator Source Draft v0.1

Fecha: 2026-06-27
Estado: source_note / strategy draft.
Fuente primaria: Steven Dux - Duxinator - `8 - The Risk Reward on Multi-day Top`.

## 1. Proposito

Este documento define la lectura inicial de TSIS para `Multi-Day Top Risk
Reward` segun el material Duxinator.

No es un setup aislado. Es una capa de filtro para:

```text
Maximum Dollar Block
Double Intraday Top
Multi-Day Top shorts
```

## 2. Resumen tecnico

Dux plantea que, en low floats, no basta con encontrar top.

Debe existir suficiente reward hasta el siguiente soporte/consolidacion.

La tesis:

```text
si entre el top y el soporte inferior hay mucho aire, el short tiene reward
si el soporte esta demasiado cerca, el trade se vuelve lento/peligroso
```

## 3. Caso ideal

Ejemplo fuente:

```text
base/consolidacion = 5
top/consolidacion alta = 20
support fade esperado = 6-7
```

Hay rango suficiente.

## 4. Caso a evitar

Ejemplo fuente:

```text
base/consolidacion = 5-8
top/consolidacion = 9-11
entry = 9.5-10
support cercano = 8
reward maximo ~= 1.5
```

Aunque haya top, no hay enough risk-reward.

## 5. Peligro del slow fade

Cuando el reward es pequeno:

- el fade puede ser lento;
- el volumen se seca;
- un cover grande puede generar spike;
- el soporte cercano atrae buyers;
- el short puede quedar atrapado.

## 6. Formulas candidatas

### 6.1. Available downside reward

```text
available_reward =
  entry_reference_price - nearest_support_price

available_reward_pct =
  available_reward / entry_reference_price * 100
```

### 6.2. Risk to top

```text
risk_to_top =
  top_resistance_price - entry_reference_price

risk_to_top_pct =
  risk_to_top / entry_reference_price * 100
```

### 6.3. Reward/risk ratio

```text
reward_risk_ratio =
  available_reward / risk_to_top
```

### 6.4. Air gap between consolidations

```text
consolidation_air_gap =
  top_consolidation_low - lower_consolidation_high

consolidation_air_gap_pct =
  consolidation_air_gap / top_consolidation_low * 100
```

## 7. Estados candidatos

```text
multi_day_top_candidate
reward_sufficient_top
reward_insufficient_top
near_support_short_avoid
slow_fade_risk_context
large_air_gap_short_candidate
```

## 8. Campos minimos para candidate_table

```text
candidate_id
ticker
exchange
company_name
session_date
top_consolidation_high
top_consolidation_low
lower_consolidation_high
lower_consolidation_low
nearest_support_price
entry_reference_price
available_reward
available_reward_pct
risk_to_top
risk_to_top_pct
reward_risk_ratio
consolidation_air_gap
consolidation_air_gap_pct
slow_fade_risk_flag
strategy_state
review_bucket
```

## 9. Charts requeridos para notebook

### 9.1. Multi-day top range chart

Debe mostrar:

- base inferior;
- top/consolidacion alta;
- soporte inferior mas cercano;
- aire entre estructuras.

### 9.2. Risk/reward detail

Debe mostrar:

- entry reference;
- top risk;
- reward disponible;
- reward/risk ratio.

## 10. Diferencia con eventos

Este documento es Strategy Library porque filtra decisiones operativas.

Eventos futuros:

```text
Multi_Day_Top_Context_Event
Large_Air_Gap_Below_Top_Event
Near_Support_Reward_Insufficient_Context
Slow_Fade_Risk_Context
```

## 11. Imagenes deseadas del propio video

Solo se deben usar capturas de `8 - The Risk Reward on Multi-day Top`.

Capturas deseadas:

```text
00:44-02:22  caso ideal: base 5, top 20, reward hasta 6-7
02:35-03:33  caso malo: soporte cercano 5-8 y top 9-11
03:33-05:04  slow fade, cover spike y riesgo de no tener reward
```

## 12. Regla final

La pregunta correcta no es:

```text
hay top?
```

La pregunta correcta es:

```text
hay suficiente aire estadistico entre el top y el soporte inferior para que el
short tenga reward real antes de entrar en zona de rebote/slow fade?
```
