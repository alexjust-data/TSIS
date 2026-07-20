# 010 news_context_table - Lectura De Representacion

Status: `representation_reading_v0_2_concise`

Date: `2026-07-16`

Este documento es deliberadamente corto.

No intenta certificar la tabla ni repetir contratos.
Solo responde que familia de informacion representa la tabla, por que esas variables merecen existir y quien las consumira downstream.

## Ser De La Tabla

```text
Contexto de flujo de informacion/noticias observable.
```

## Familias Relevantes

### Noticias

Fenomeno del mercado que representa:
```text
Llegada de informacion publica asociada a un instrumento.
```

Hipotesis cientifica:
```text
Noticias cambian atencion,
participacion,
volatilidad y respuesta a eventos.
```

Preguntas que permite responder:
```text
Hubo noticia antes de t?
De que fuente?
Cuanto tiempo antes?
Esta deduplicada?
```

Variables minimas:
```text
news_context_id,
article_id,
news_timestamp,
article_url_hash,
title_hash,
source_type,
topic/category.
```

Tabla donde deben vivir:
```text
Deben vivir en 010 news_context_table;
features textuales derivadas deberian vivir en una tabla feature dedicada o registry.
```

Consumidores:
```text
Market State,
Event State,
clustering,
ML/IRL/RL/AlphaEvolve con timestamp legality.
```

### Eventos

Fenomeno del mercado que representa:
```text
Noticia como ancla o contexto de evento.
```

Hipotesis cientifica:
```text
Un evento con noticia no equivale a un evento puramente tape-driven.
```

Preguntas que permite responder:
```text
La noticia crea evento?
Solo explica contexto?
Cae dentro de la ventana?
```

Variables minimas:
```text
article_id,
event_source,
published_at/as_of,
ticker/instrument_id.
```

Tabla donde deben vivir:
```text
010 para contexto;
007 para ventanas;
017 para event state.
```

Consumidores:
```text
Event State,
outcomes,
research experiments y scanners.
```

## Lectura Final

```text
La tabla debe mantenerse solo en las familias indicadas. Cualquier variable nueva debe justificar familia, hipotesis y consumidor antes de entrar.
```

