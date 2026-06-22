# Event Engine Tests

Este directorio valida la semantica de eventos del modulo SmallCaps.

## Ambito

Aqui deben vivir tests sobre:

- offerings;
- filings SEC;
- newswires;
- halts;
- corporate actions;
- ticker changes;
- eventos con timestamp causal;
- alertas en tiempo real;
- alineacion entre evento, simbolo, sesion y precio.

## Reglas

Los eventos deben ser causales. Una estrategia no puede usar informacion que no
estaba disponible en el timestamp del evento.

Cada evento institucional debe distinguir:

- `event_time`;
- `published_time`;
- `received_time` si existe;
- fuente;
- latencia conocida o desconocida;
- ticker o instrumento afectado;
- estado de confianza.

## Pruebas esperadas

Pruebas candidatas:

- `test_event_time_ordering.py`
- `test_no_event_lookahead.py`
- `test_real_time_alert_contract.py`
- `test_sec_filing_event_reconciliation.py`
- `test_halts_event_alignment.py`

## Fuentes externas

Cuando aplique, las pruebas deben poder contrastar muestras contra SEC EDGAR,
NYSE/Nasdaq u otro proveedor certificado. La ejecucion por defecto debe ser
offline mediante evidencia cacheada.

