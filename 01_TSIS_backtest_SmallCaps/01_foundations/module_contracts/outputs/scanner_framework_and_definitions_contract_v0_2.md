# Scanner Framework And Definitions Contract v0.2

## Estado

Tipo: module contract.

Modulo: `01_TSIS_backtest_SmallCaps`.

Ambito: `CAPA 1 - DATA FOUNDATION`.

Status:

```text
builder_implemented_controlled_replay_not_official
```

## Cambio Frente A v0.1

`v0.1` separaba dos scanners:

```text
trade_station_like_scanner_v0_1
broad_in_play_discovery_scanner_v0_1
```

Esa forma era util para demostrar que `volume_today > 500000` y `% change 1D`
pueden llegar tarde para research DAS, pero generaba una ambiguedad: parecia
que TSIS tenia dos universos distintos.

La decision `v0.2` es:

```text
base_in_play_universe_scanner_v0_2
  -> trade_station_like_profile_v0_2
  -> relative_volume_profile_v0_2
  -> percent_change_profile_v0_2
  -> dollar_volume_tradability_profile_v0_2
  -> das_research_profile_v0_2
```

Hay un solo denominador base. Los perfiles seleccionan, rankean o etiquetan
visibilidad dentro de ese denominador.

## Base Universe

El denominador base es:

```text
is_common_stock = true
market_cap_usd < 100000000
0.5 < last_price <= 20
data_quality in usable/review states
```

Reglas:

- `market_cap_usd < 100M` es hard filter comun;
- `volume_today >= 500k` no es hard filter comun;
- `% change 1D top 25` no es hard filter comun;
- `float` no se usa como hard filter hasta tener fuente point-in-time auditada;
- cada fila debe declarar `as_of_utc`, source lineage, price view, quality
  flags y si es replay historico o snapshot/live.

## Perfiles Gobernados

### `trade_station_like_profile_v0_2`

Reproduce visibilidad operativa humana:

```text
base universe
volume_today >= 500000
rank pct_chg_1d desc
top_n = 25
```

Responde:

```text
Que habria visto el operador en una hot list tipo TradeStation?
```

### `relative_volume_profile_v0_2`

Estudia atencion/participacion relativa dentro de la base.

En replay diario controlado, `rvol_to_time` se aproxima con `rvol_20d` de
`master_daily_table`. Para intradia real exige cutoff/as-of propio.

### `percent_change_profile_v0_2`

Estudia momentum por variacion diaria sin convertir `volume_today >= 500k` en
filtro universal.

### `dollar_volume_tradability_profile_v0_2`

Estudia tradability/liquidez economica aproximada. No prueba setup sano por si
solo.

### `das_research_profile_v0_2`

Perfil de denominador para investigacion DAS/frontside. Puede marcar candidatos
por:

```text
pct_chg_1d
gap_pct
volume_acceleration
rvol_to_time
composite_in_play_score
future afterhours/premarket/news/halt reasons when scoped sources exist
```

No es una senal DAS.
No contiene labels, outcomes, rewards, fills ni PnL.

## Relacion Con Estados

La ruta correcta sigue siendo:

```text
daily_scanner_candidates_table
  -> das_candidate_state_table_experimental
  -> market_state_table
  -> event_state_table
  -> ML/RL/backtest/evaluator datasets
```

El scanner dice donde mirar.
El estado dice que sabia TSIS legalmente en un timestamp.
La estrategia estudia transiciones y outcomes fuera del scanner.

## Configs Versionadas

Configs activas `v0.2`:

```text
configs/data_foundation_outputs/scanner_definitions/base_in_play_universe_scanner_v0_2.yaml
configs/data_foundation_outputs/scanner_definitions/trade_station_like_profile_v0_2.yaml
configs/data_foundation_outputs/scanner_definitions/relative_volume_profile_v0_2.yaml
configs/data_foundation_outputs/scanner_definitions/percent_change_profile_v0_2.yaml
configs/data_foundation_outputs/scanner_definitions/dollar_volume_tradability_profile_v0_2.yaml
configs/data_foundation_outputs/scanner_definitions/das_research_profile_v0_2.yaml
```

Builder controlado:

```text
scripts/materialize_daily_scanner_candidates_table_v0_2.py
tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder_v0_2.py
```

## Scientific And Institutional Basis

Este contrato implementa la linea cientifica ya documentada en:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/scanner_base_universe_and_profiles_contract_v0_2.md
```

Principios:

- Offline RL no debe aprender solo de casos buenos; necesita soporte de datos,
  coberturas y denominadores observados. Referencia: Levine et al.,
  *Offline Reinforcement Learning: Tutorial, Review, and Perspectives on Open
  Problems*.
- Aprender de demostraciones expertas no elimina la necesidad de negativos,
  estados no seleccionados y transiciones de baja calidad. Referencia: Hester
  et al., *Deep Q-learning from Demonstrations*.
- Causal ML exige separar proxies observados, mecanismos y outcomes para evitar
  aprender correlaciones espurias. Referencia: Scholkopf et al.,
  *Causality for Machine Learning*.
- La microestructura relevante no se reduce a OHLCV; atencion, liquidez,
  spread/order-flow y limit order book importan. Referencias: DeepLOB; Kyle
  1985; Easley, Lopez de Prado and O'Hara on flow toxicity.

## Prohibited Uses

Queda prohibido:

- tratar `trade_station_like_profile_v0_2` como universo completo;
- tratar `das_research_profile_v0_2` como senal DAS;
- filtrar globalmente por float sin fuente point-in-time auditada;
- entrenar ML/RL directamente con scanner rows como estado final;
- mezclar labels/outcomes/rewards/fills/PnL dentro del scanner;
- esconder seleccion manual como si fuera scanner automatico;
- afirmar `full_universe_claim=true` sin prueba de denominador.

## Final Rule

`v0.2` convierte el scanner en una capa de denominador comun mas perfiles.

Esto permite estudiar:

```text
que entraria por el scanner humano
que entraria por atencion relativa
que entraria por momentum diario
que entraria por tradability
que entraria por research DAS
```

sin confundir ninguno de esos perfiles con estado, senal, label o reward.
