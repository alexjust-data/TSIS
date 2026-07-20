# 012 regime_context_table - Lectura De Representacion

Status: `representation_reading_v0_2_concise`

Date: `2026-07-16`

Este documento es deliberadamente corto.

No intenta certificar la tabla ni repetir contratos.
Solo responde que familia de informacion representa la tabla, por que esas variables merecen existir y quien las consumira downstream.

## Ser De La Tabla

```text
Contexto de regimen externo al instrumento.
```

## Familias Relevantes

### Regimen

Fenomeno del mercado que representa:
```text
Entorno amplio de mercado,
indice,
sector,
volatilidad o risk-on/risk-off.
```

Hipotesis cientifica:
```text
El mismo evento smallcap puede comportarse distinto bajo distintos regimenes externos.
```

Preguntas que permite responder:
```text
Que regimen habia en t?
El evento iba a favor o contra mercado?
Cambia la distribucion de outcomes?
```

Variables minimas:
```text
regime_symbol,
regime_proxy_role,
index_return,
volatility_proxy,
risk_on_off_state,
regime_quality.
```

Tabla donde deben vivir:
```text
Deben vivir en 012 regime_context_table;
agregaciones en 016/017.
```

Consumidores:
```text
Market State,
Event State,
clustering,
backtests,
ML,
IRL,
RL y AlphaEvolve.
```

### Temporalidad

Fenomeno del mercado que representa:
```text
Legalidad as-of del proxy de regimen.
```

Hipotesis cientifica:
```text
Usar datos EOD de regimen al inicio intradia filtra futuro.
```

Preguntas que permite responder:
```text
El proxy estaba disponible en t?
Es diario, intradia o EOD?
```

Variables minimas:
```text
trading_date,
session_open_utc,
as_of_utc,
as_of_date,
as_of_semantics,
source_granularity.
```

Tabla donde deben vivir:
```text
012 para contexto;
016/017 para estado consumible.
```

Consumidores:
```text
Market State,
Event State,
ML/RL y research con as-of enforcement.
```

## Lectura Final

```text
La tabla debe mantenerse solo en las familias indicadas. Cualquier variable nueva debe justificar familia, hipotesis y consumidor antes de entrar.
```

