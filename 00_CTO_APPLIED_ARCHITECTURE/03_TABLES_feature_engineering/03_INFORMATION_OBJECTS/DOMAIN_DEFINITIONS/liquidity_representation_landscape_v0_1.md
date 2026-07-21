# Liquidity - Representation Landscape v0.1

Status: `representation_landscape_v0_1`
Date: `2026-07-20`
Scope: `post_domain_definition_pre_object_admission`

Este documento revisa modelos posibles para `Liquidity`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona el modelo final.
No autoriza variables para `Market State` ni `Event State`.

## Dominio

```text
Liquidity
```

## Candidatos A Objeto Dentro Del Dominio 

| Candidato | Lectura cientifica | Decision pre-admision |
| --- | --- | --- |
| `Liquidity` | Candidato principal. Preserva coste/facilidad/disponibilidad de negociar. | `forward_to_object_admission` |
| `Displayed Liquidity` | Modelo L1 basado en spread/depth. | `representation_model_candidate` |
| `Tradability Proxy` | Modelo incompleto basado en dollar volume/trade count. | `proxy_model_only` |
| `Effective Spread` | Modelo avanzado dependiente de alignment/side. | `candidate_extension` |
| `Realized Spread` | Usa horizonte posterior. | `outcome_or_research_only` |
| `OFI / Consumption` | Presion/consumo direccional. | `move_to_order_flow_pressure` |

## Paisaje De Modelos De Representacion 

| Modelo candidato | Que intenta medir | Capacidades derivables relacionadas | Fuentes / tablas | Estado | Riesgo principal |
| --- | --- | --- | --- | --- | --- |
| `quoted_spread_cost_model` | Coste observable de cruzar top-of-book. | `quotes__spread_bps_row`, `quotes__spread_bps_median_WINDOW`, `quotes__spread_bps_p90_WINDOW` | Quotes L1; `015` | `formula_defined_existing_window` | Spread invalido si quotes crossed/locked no se gobiernan. |
| `displayed_depth_model` | Liquidez visible en top-of-book. | `quotes__bid_size`, `quotes__ask_size`, `quotes__top_depth_mean_WINDOW` | Quotes L1; `015` | `existing` | L1 no captura hidden depth ni profundidad L2/MBO. |
| `quote_availability_model` | Disponibilidad y continuidad de quotes. | `quotes__two_sided_rows_WINDOW`, `quotes__quote_count_WINDOW`, `quotes__quote_update_rate_WINDOW` | Quotes L1; `015` | `existing_plus_requires_variant` | Quote rate puede medir actividad de quote, no necesariamente liquidez real. |
| `quote_integrity_context_model` | Estado locked/crossed como condicion de interpretabilidad. | `quotes__locked_ratio_pct_two_sided_WINDOW`, `quotes__crossed_ratio_pct_two_sided_WINDOW` | Quotes L1; `015` | `existing` | Puede pertenecer a Quality/Microstructure mas que Liquidity core. |
| `tradability_proxy_model` | Capacidad aproximada de negociar usando actividad economica. | `daily__dollar_volume`, `intraday__session_dollar_volume_to_time`, `trades__dollar_volume_WINDOW`, `trades__trade_count_WINDOW` | `004`, `014`, `015` | `proxy_existing` | No confundir actividad con liquidez real. |
| `effective_spread_model` | Coste efectivo alrededor de trades alineados. | `trade_quote__effective_spread_bps_WINDOW` | Trades + Quotes; future `021` / `015` | `candidate` |
Requiere alignment, side classifier y no usar informacion futura. |
| `price_impact_model` | Impacto de trade/flujo sobre precio observable. | `trade_quote__price_impact_proxy_WINDOW` | Trades + Quotes | `candidate` | Puede pertenecer a Order Flow/Impact; formula debe ser causal. |
| `realized_spread_model` | Coste realizado con horizonte posterior. | `trade_quote__realized_spread_bps_WINDOW` | Trades + future mid | `candidate_outcome_only` | Usa futuro; no puede ser State input. |

## Modelos Que Podrian Ser Redundantes

```text
Quote count vs Quote update rate:  Ambos hablan de actividad del quote stream, pero rate normaliza por tiempo y count no.
```

```text
Dollar volume proxy vs Trading Activity:  La misma variable tiene distinto significado. En Liquidity solo puede ser proxy de tradability, no prueba de coste o profundidad.
```

## Modelos Que
Requieren Separacion

```text
Order Flow Pressure: OFI, signed flow y aggressor imbalance no son Liquidity core.
```

```text
Market Microstructure State: locked/crossed, staleness y quote lifetime pueden ser estado del book, no necesariamente liquidez admitida.
```

```text
Execution Outcomes: realized slippage/PnL/fill quality no son Liquidity observable en t.
```

## Modelos Bloqueados O No Listos

```text
L2_depth_model: blocked_reason:  no existe fuente L2/MBO gobernada.
```

```text
borrow_availability_liquidity_model: blocked_reason:  no existe fuente borrow/locate gobernada.
```

```text
effective_spread_model: blocked_reason:  requiere trade-quote alignment y side classifier gobernados.
```

## Decision Del Landscape

```text
decision = ready_to_define_candidate_object
```

Motivo:

```text
Existe un Objeto candidato coherente: Liquidity. Los modelos principales pueden representarse con Quotes L1 y proxies gobernados, pero deben entrar con restricciones por falta de L2/MBO y por frontera con Activity/Order Flow.
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\liquidity_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\015\table_representation_audit_ES.md
```
