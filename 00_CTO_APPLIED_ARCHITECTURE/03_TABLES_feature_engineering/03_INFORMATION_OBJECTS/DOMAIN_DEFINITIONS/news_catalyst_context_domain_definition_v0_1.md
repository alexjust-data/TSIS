# News / Catalyst Context - Domain Definition v0.1

Status: `domain_definition_v0_1`
Date: `2026-07-20`
Scope: `external_context_pre_landscape_pre_admission`

Este documento define el dominio semantico `News / Catalyst Context`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona modelos finales.
No autoriza variables para `Market State` ni `Event State`.
No modifica tablas, schemas, builders, contratos ni datasets.

## Nombre Del Dominio

```text
News / Catalyst Context
```

## Que Informacion Intenta Preservar

```text
Objeto que preserva informacion externa publicada o disponible as-of que puede alterar la interpretacion del instrumento, evento o sesion.
```

## Por Que Este Dominio Merece Existir

```text
La presencia, edad, tipo, novedad y relevancia de noticias/catalizadores puede cambiar la interpretacion del estado observable y la respuesta futura.
```

## Que Perderia TSIS Si Este Dominio Desapareciera

```text
Perderia contexto externo/as-of necesario para interpretar estados tecnicos que, aislados, pueden tener significados distintos.
```

## Que No Representa

```text
precio, volumen, liquidez, order flow, volatilidad, decision del scanner, outcome futuro, ni dato sin politica as-of.
```

## Preguntas Cientificas Que Permite Formular

```text
Existe contexto externo observable antes de t?  Que antiguedad, relevancia o lag tiene?  Cambia la respuesta del mercado cuando este contexto esta presente?  Debe entrar en core State o solo en extension/context profile?
```

## Capacidades Derivables Relacionadas

Core candidatas:

```text
news__published_utc, news__as_of_utc, news__article_count_WINDOW, news__freshness_minutes
```

Extension/bloqueadas:

```text
news__keyword_flag, news__sentiment_score, news__novelty_score
```

## Tabla Que Aporta Evidencia

```text
010_news_context_table
```

## Decision De Dominio

```text
decision = ready_for_representation_landscape
```
