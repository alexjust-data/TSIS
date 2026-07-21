# Liquidity - Domain Definition v0.1

Status: `domain_definition_v0_1`
Date: `2026-07-20`
Scope: `cluster_5_pre_landscape_pre_admission`

Este documento define el dominio semantico `Liquidity`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona modelos finales.
No autoriza variables para `Market State` ni `Event State`.
No modifica tablas, schemas, builders, contratos ni datasets.

## Nombre Del Dominio

```text
Liquidity
```

## Que Informacion Intenta Preservar

```text
La facilidad, coste y disponibilidad observable para negociar un instrumento en una escala temporal declarada.
```

La informacion central es:

```text
cuanto cuesta cruzar, cuanta liquidez visible existe, si el libro esta disponible, y si la negociacion observada sugiere tradability suficiente.
```

No es simplemente:

```text
volumen, precio, movimiento, order flow, outcome, ni calidad del dataset.
```

## Por Que Este Dominio Merece Existir

```text
Porque una senal o estado puede ser cientificamente interesante pero operativamente inutil si no existe liquidez suficiente o si el coste esperado de negociar domina el efecto investigado.
```

En small caps, liquidez es estructural:

```text
spreads amplios, profundidad escasa, quotes discontinuas, locked/crossed states, y tradeability variable pueden cambiar totalmente la interpretacion de cualquier estado.
```

## Que Perderia TSIS Si Este Dominio Desapareciera

```text
Perderia capacidad para distinguir:  actividad alta pero costosa de ejecutar; precio moviendose con book fino; spreads normales vs anomalo amplios; mercado disponible vs quote state deteriorado; y alpha teorico vs oportunidad operable.
```

## Que No Representa

```text
participacion negociada como fenomeno principal, direccion del precio, volatilidad, order-flow direction, short crowding, noticias, fundamentales, outcomes futuros, ni decision del scanner.
```

Una misma variable puede aparecer en varios dominios:

```text
dollar_volume en Trading Activity = cantidad economica negociada.  dollar_volume en Liquidity = proxy incompleto de tradability.
```

## Preguntas Cientificas Que Permite Formular

```text
Es operable el estado observado?  El spread esperado es compatible con la hipotesis investigada?  Hay profundidad visible suficiente?  El mercado esta two-sided y actualizando quotes?  La respuesta a eventos cambia en estados de baja vs alta liquidez?  El performance aparente desaparece cuando se condiciona por liquidez?
```

## Candidatos Incluidos

```text
Liquidity spread spread bps top depth quote count quote update rate dollar volume proxy trade count proxy effective spread candidates
```

Lectura actual:

```text
Liquidity = candidato principal a Objeto de Informacion.  Spread y depth son modelos. Dollar volume y trade count son proxies, no liquidez completa. Effective spread es candidato avanzado y requiere alignment/side policy.
```

## Posibles Modelos De Representacion

```text
quoted spread cost model displayed depth model quote availability model tradability proxy model effective spread candidate model price impact candidate model liquidity recovery candidate model
```

## Capacidades Derivables Relacionadas

### Capacidades Imprescindibles

```text
quotes__spread_bps_row quotes__spread_bps_median_WINDOW quotes__spread_bps_p90_WINDOW quotes__top_depth_mean_WINDOW quotes__two_sided_rows_WINDOW quotes__quote_count_WINDOW
```

### Capacidades Complementarias

```text
quotes__quote_update_rate_WINDOW quotes__locked_ratio_pct_two_sided_WINDOW quotes__crossed_ratio_pct_two_sided_WINDOW daily__dollar_volume intraday__session_dollar_volume_to_time trades__dollar_volume_WINDOW trades__trade_count_WINDOW
```

### Capacidades Fronterizas O No Listas

```text
trade_quote__effective_spread_bps_WINDOW trade_quote__realized_spread_bps_WINDOW trade_quote__price_impact_proxy_WINDOW trade_quote__ofi_l1_WINDOW borrow availability L2 / MBO depth
```

Lectura:

```text
realized spread usa horizonte futuro y no puede ser state input. OFI pertenece mejor a Order Flow Pressure. Borrow/L2/MBO no tienen fuente gobernada actual.
```

## Tablas Que Aportan Evidencia

```text
015_microstructure_features_table = spread, depth, quote count, quote quality y trade-window proxies.  004_master_daily_table = daily dollar_volume / rvol como proxy historico de tradability.  014_master_intraday_bar_table = intraday dollar volume / transaction count como proxy intradia.
```

## Fronteras Con Otros Dominios 

| Dominio vecino | Frontera |
| --- | --- |
| `Trading Activity` | Activity mide participacion. Liquidity mide facilidad/coste/disponibilidad de negociar. |
| `Market Microstructure State` | Microstructure describe estado operativo del book/tape. Liquidity extrae coste/disponibilidad para negociar. |
| `Order Flow Pressure` | Order Flow mide direccion/agresion. Liquidity no necesita signo para existir. |
| `Volatility / Range State` | Volatility mide variabilidad. Liquidity mide friccion/ejecutabilidad. |
| `Execution` | Liquidity informa ejecutabilidad; no es fill, slippage realizado ni PnL. |
| `Outcome Layer` | Realized spread futuro y price impact posterior pueden ser outcomes/research, no inputs sin cutoff. |

## Decision De Dominio

```text
decision = ready_for_representation_landscape
```

Motivo:

```text
El dominio tiene identidad propia: preserva coste, facilidad y disponibilidad observable de negociacion. No queda reducido a actividad ni microestructura general.
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\015\table_representation_audit_ES.md
```
