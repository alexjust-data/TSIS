# 13_configs

## Objetivo

Guardar todos los archivos de configuración del sistema.

Esta carpeta permite que el framework sea reproducible, modificable y auditable sin tocar código.

---

# Qué va aquí

## Configs de universo

- small caps
- microcaps
- low float
- price filters
- volume filters
- exchange filters

## Configs de estrategias

- Gap&Go
- Gap&Crap
- First Green Day
- Breakout
- Parabolic Fade

## Configs de ejecución

- slippage model
- commission model
- max participation volume
- fill model
- halt behavior
- SSR rules

## Configs de ML/RL

- model parameters
- training windows
- validation method
- reward function
- action space
- state space

## Configs de sesiones

- premarket
- regular session
- after-hours
- holidays
- half days

---

# Ejemplos

universe_low_float.yaml  
strategy_gap_and_go_v01.yaml  
execution_realistic_v02.yaml  
ml_catboost_meta_labeling_v03.yaml  
offline_rl_reward_r_multiple.yaml  
market_sessions_us_equities.yaml  

---

# Filosofía

Nada importante debe estar hardcodeado.

Si un parámetro cambia, debe cambiarse aquí, no dentro del código.

---

# Objetivo final

Permitir reproducir exactamente cualquier experimento pasado.