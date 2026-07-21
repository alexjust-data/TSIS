# 004 master_daily_table - Lectura De Representacion

Status: `representation_reading_v0_2_concise`

Date: `2026-07-16`

Este documento es deliberadamente corto.

No intenta certificar la tabla ni repetir contratos.
Solo responde que familia de informacion representa la tabla, por que esas variables merecen existir y quien las consumira downstream.

## Ser De La Tabla

```text
Contexto diario canonico del instrumento.
```

## Familias Relevantes

### Precio

Fenomeno del mercado que representa:
```text
Nivel,
rango y
localizacion diaria del precio.
```

Hipotesis cientifica:
```text
El comportamiento intradia depende de donde esta el precio respecto a referencias diarias.
```

Preguntas que permite responder:
```text
Cual fue open/high/low/close?
Hay gap?
Donde esta el precio respecto al dia previo?
```

Variables minimas:
```text
daily open,
high,
low,
close,
prior_close,
gap_percent,
daily_range.
```

Tabla donde deben vivir:
```text
Deben vivir en 004 para contexto diario;
derivados intradia deben vivir en 014/016.
```

Consumidores:
```text
Market State,
Event State,
scanners,
backtests,
ML/RL.
```

### Liquidez / Participacion

Fenomeno del mercado que representa:
```text
Actividad y tradabilidad diaria.
```

Hipotesis cientifica:
```text
Volumen y dollar volume condicionan si un movimiento es operable o solo visible.
```

Preguntas que permite responder:
```text
Hubo participacion suficiente?
Es un dia anormalmente activo?
```

Variables minimas:
```text
daily_volume,
dollar_volume,
relative_daily_volume,
liquidity_bucket.
```

Tabla donde deben vivir:
```text
Base en 004;
features rolling o intradia en 014/015/016.
```

Consumidores:
```text
Scanners,
Market State,
Event State,
execution research,
backtests.
```

### Volatilidad

Fenomeno del mercado que representa:
```text
Amplitud e inestabilidad diaria.
```

Hipotesis cientifica:
```text
Rangos diarios altos o comprimidos modifican riesgo y respuesta futura.
```

Preguntas que permite responder:
```text
El dia esta expandido, comprimido o normal?
```

Variables minimas:
```text
daily_range,
range_pct,
true_range_proxy,
volatility_bucket.
```

Tabla donde deben vivir:
```text
004 para contexto diario;
016 para estado agregado.
```

Consumidores:
```text
Market State,
Event State,
risk controls,
ML/RL.
```

## Lectura Final

```text
La tabla debe mantenerse solo en las familias indicadas. Cualquier variable nueva debe justificar familia, hipotesis y consumidor antes de entrar.
```


