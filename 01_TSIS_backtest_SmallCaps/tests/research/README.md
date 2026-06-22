# Research Tests

Este directorio valida que la investigacion no se convierta en autoridad
institucional sin promocion.

## Ambito

Aqui deben vivir tests sobre:

- notebooks de research cuando generan outputs usados aguas abajo;
- indices de experimentos;
- promotion barriers desde exploracion a contrato;
- reproducibilidad minima de resultados promocionados;
- separacion entre hallazgo exploratorio y tabla institucional.

## Reglas

Los notebooks pueden explorar, visualizar y prototipar. No deben ser la unica
fuente de verdad de:

- schema canonico;
- validador;
- politica de consumo;
- tabla oficial;
- decision de universo;
- evento institucional.

## Pruebas esperadas

Pruebas candidatas:

- `test_notebook_outputs_are_not_authoritative.py`
- `test_research_promotions_have_contract.py`
- `test_event_research_has_reproducible_inputs.py`
- `test_research_artifacts_link_to_manifests.py`

## Criterio de auditoria

Cuando research promocione una idea, el test debe poder encontrar:

- notebook o script exploratorio;
- contrato promocionado;
- manifest o dataset version;
- changelog;
- owner o area responsable;
- estado de promocion.

