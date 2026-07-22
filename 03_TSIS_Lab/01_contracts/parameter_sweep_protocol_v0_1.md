# Parameter Sweep Protocol v0.1

Fecha: 2026-07-05
Estado: protocol_defined_initial

## Objetivo

Definir como TSIS explora parametros sin convertir el proceso en busqueda caotica de falsos edges.

Un `parameter_sweep` no busca demostrar una estrategia. Busca observar como cambia un fenomeno cuando se modifica una variable.

## Regla Base

```text
parameter_sweep = instrumento de medicion
no = optimizacion final de estrategia
```

## Metodo Por Capas

Capa 1:

```text
modificar un solo parametro
```

Capa 2:

```text
modificar un parametro principal + una referencia
```

Capa 3:

```text
modificar parametro + referencia + ventana
```

Capa 4:

```text
anadir contexto: float, gap, volumen, regime, news, microestructura
```

No se empieza por combinaciones masivas sin haber entendido la sensibilidad basica.

## Reglas

```text
cada variante tiene ID unico
cada variante guarda config completa
cada resultado guarda lineage
no se selecciona el mejor sin validacion posterior
no se reutiliza sealed holdout para iterar
se registran tambien resultados malos
se comparan contra baseline
se penaliza complejidad
```

## Ejemplo Intraday Momentum Extension

```text
threshold_pct: 20, 30, 40, 50, 70, 100
reference_price: prior_close, session_open, segment_open, premarket_low, vwap
post_event_window: 1m, 5m, 15m, 30m, 60m, end_of_session
```

El objetivo no es encontrar el mejor porcentaje. El objetivo inicial es responder:

```text
existe un cambio de comportamiento al aumentar el umbral?
el cambio es gradual o hay zona de ruptura?
es estable por anos, regimenes y subgrupos?
depende de float, gap, volumen o hora?
```
