# Offline RL Preparation Tests

Este directorio valida la preparacion de datasets para offline reinforcement
learning.

## Ambito

Aqui deben vivir tests sobre:

- estados;
- acciones;
- rewards;
- episodios;
- splits temporales;
- leakage;
- compatibilidad con contratos de Data Foundation;
- trazabilidad desde raw/derived data hasta dataset RL.

## Reglas

Offline RL no debe inventar una fuente de verdad distinta. Debe consumir tablas
gobernadas, manifests y policies oficiales.

Los rewards no deben contener informacion futura que no estaria disponible para
la politica en el momento de decision.

## Pruebas esperadas

Pruebas candidatas:

- `test_rl_dataset_uses_governed_sources.py`
- `test_episode_boundaries_follow_calendar.py`
- `test_no_future_reward_leakage.py`
- `test_state_action_schema.py`
- `test_rl_split_temporal_integrity.py`

## Criterio de promocion

Un dataset RL solo debe considerarse promocionable si puede responder:

- que tablas Data Foundation uso;
- que version de features uso;
- como definio estado, accion y reward;
- como evito leakage;
- que periodo cubre;
- que manifest y run id lo reconstruyen.

