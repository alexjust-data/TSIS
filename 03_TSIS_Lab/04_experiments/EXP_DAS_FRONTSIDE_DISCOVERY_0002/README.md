# EXP_DAS_FRONTSIDE_DISCOVERY_0002

Fecha: 2026-07-06
Estado: draft_operativo
Tipo: research experiment

## Objetivo

Este experimento continua la linea DAS/frontside, pero cambia el foco.

`EXP_DAS_FRONTSIDE_DISCOVERY_0001` nos ayudo a fijar y auditar anchors visuales:

```text
scanner gate
first push
first push high
first dip low
rebreak / fake rebreak
```

`EXP_DAS_FRONTSIDE_DISCOVERY_0002` usa esos anchors para responder la pregunta cientifica principal:

```text
?Por que algunos tickers recuperan el primer dip y otros se destruyen?
```

Y la pregunta operativa asociada:

```text
?Que umbral y que filtros capturan mejor los tickers frontside sin destruir demasiado coste de oportunidad?
```

## Lectura Correcta

Este experimento no busca todavia validar una estrategia completa.

Busca medir la poblacion completa de tickers cazados por scanner y clasificar que ocurre despues:

```text
scanner gate
-> first push
-> first dip
-> recovery / no recovery
-> rebreak / fake rebreak
-> continuation / destruction
```

La regla discrecional humana:

```text
si supera el primer dip / recupera estructura, esta in-play
```

se trata aqui como hipotesis investigable, no como verdad final.

## Relacion Con Otros Experimentos

```text
EXP_DAS_FRONTSIDE_DISCOVERY_0001
= anchors visuales y gramatica basica DAS/frontside

EXP_DAS_FRONTSIDE_DISCOVERY_0002
= estadistica de recuperacion/destruccion, sensibilidad de threshold y coste de oportunidad

EXP_DAS_TICKER_INPLAY_0001
= futuro experimento para definir cuando un ticker ya cazado pasa a estrategia in-play
```

No se debe saltar a `EXP_DAS_TICKER_INPLAY_0001` hasta que `0002` entregue una primera lectura de:

```text
1. que captura el scanner
2. que destruye oportunidades
3. que recupera el primer dip
4. que queda explotable antes y despues del rebreak
```

## Documentos

```text
research_design.md
  pregunta cientifica, hipotesis, denominador y no-goals

execution_protocol.md
  pasos de ejecucion historica, sweeps y salidas esperadas

measurement_contract.md
  definiciones de anchors, outcomes, MFE/MAE, recovery, destruction y opportunity decomposition

visual_audit_protocol.md
  reglas para pintar y auditar labels 1m sin colocar marcas a ojo

data_and_lineage_policy.md
  politica 1m, quote-guard, scale guard y trazabilidad minima

subminute_15s_30s_research_layer.md
  capa exploratoria para construir barras 15s/30s desde quotes/trades, nunca desde partir velas 1m
```

## Regla De Datos 1m

Antes de ejecutar este experimento leer:

```text
C:/TSIS_Data/03_TSIS_Lab/LOCAL_RULES.md
```

Resumen:

```text
ohlcv_1m raw no es verdad visual ni tabla oficial por si solo.
Toda vela 1m debe declarar vista, repair/guard state, lineage y scale guard raw/quotes cuando aplique.
```



## Ruta Oficial Actual De Ejecucion

Para construir el denominador del scanner no se usa `candidate_events.parquet` ni ningun run antiguo del notebook DAS.

Como 2026 ya existe saneado/materializado, la ruta oficial actual de `EXP_DAS_FRONTSIDE_DISCOVERY_0002` empieza aqui:

```text
C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_1
+
master_daily_table_v0_1 para prior_close
+
E:/TSIS/data/reference/overview para market_cap declarado
-> scanner denominator reproducible
```

Script oficial actual:

```text
scripts/build_2026_scanner_from_qg_full_universe_1m_v0_2.py
```

Wrapper monitorizado para run largo:

```text
scripts/run_scanner_2026_qg_full_universe_monitored_v0_2.py
```

La ruta anterior `raw 1m + repair shards durante el scanner` queda como referencia pre-materializacion. Los scripts que consumen outputs antiguos del DAS quedan como referencia historica o visual, no como fuente normativa del denominador cientifico.

## Estado Actual - Denominador Scanner 2026 Congelado

Fecha: 2026-07-07

Primer denominador valido generado desde 1m quote-guarded full-universe:

```text
evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z/outputs/scanner_2026_qg_full_universe_denominator_v0_2.parquet
```

Lectura correcta:

```text
152 candidatos = tickers/sesiones que el scanner habria cazado bajo esta configuracion
152 candidatos != casos buenos DAS
152 candidatos != entradas validas
152 candidatos != outcomes de estrategia
```

Este denominador representa el embudo operativo inicial:

```text
universo 1m quote-guarded 2026
-> scanner +50% vs prior_close
-> volumen acumulado >= 500k
-> precio entre $0.50 y $20
-> market cap <100M con fuente marcada
-> 152 candidatos capturados
```

Despues, y solo despues, se estudiara que parte de esos 152:

```text
forma estructura DAS
recupera el primer dip
rompe first_push_high
entra in-play
continua
falla
se destruye
```

Auditoria del denominador:

```text
evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z/audit/denominator_audit_v0_1.md
```

Hallazgo critico de lineage:

```text
144/152 candidatos usan market_cap_source_state = future_snapshot_review
8/152 candidatos usan market_cap_source_state = asof
```

Por tanto, este denominador es valido para research exploratorio declarado, pero no debe confundirse con un dataset legal-as-of listo para tablas de estado oficiales.

## Estado Actual - Anchor Worklist 2026

Fecha: 2026-07-07

A partir del denominador congelado se creo la worklist de anchors:

```text
evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z/anchor_worklist/anchor_worklist_from_denominator_v0_1.parquet
```

Resumen:

```text
rows = 152
unique_tickers = 130
unique_sessions = 43
source_input_1m_files_missing = 0
```

Lectura correcta:

```text
anchor_worklist = casos pendientes de deteccion de estructura
anchor_worklist != DAS validado
anchor_worklist != in-play
anchor_worklist != outcomes
```

## Estado Actual - Anchor Candidates 2026

Fecha: 2026-07-07

A partir de la `anchor_worklist` de 152 casos se materializo la primera capa de anchors candidatos:

```text
evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z/anchor_candidates_v0_1/das_frontside_anchor_candidates_v0_1.parquet
```

Output largo de eventos/anchors:

```text
evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z/anchor_candidates_v0_1/das_frontside_anchor_events_long_v0_1.parquet
```

Resumen:

```text
input_rows = 152
case_rows = 152
event_rows = 716
errors = 0
rebreak_confirmed = 97
no_rebreak_in_window = 40
fake_rebreak_no_confirmation = 11
no_rebreak_search_window = 4
```

Lectura correcta:

```text
anchor_candidates = deteccion candidata de estructura desde el denominador scanner
anchor_candidates != DAS bueno
anchor_candidates != in-play oficial
anchor_candidates != trade
anchor_candidates != edge
```

Regla candidata v0.1:

```text
first_push_high = running high del push relevante, congelado solo despues de que el running high sea al menos scanner_gate_price y luego exista un retroceso minimo declarado
first_dip_low = low minimo despues de first_push_high y antes del primer toque posterior de first_push_high
rebreak_confirmed = high posterior cruza first_push_high con confirmacion candidata de volumen y vela verde
fake_rebreak = high posterior cruza first_push_high pero falla la confirmacion candidata
no_rebreak = no hay toque posterior de first_push_high en la ventana analizada
```

Todas estas reglas siguen siendo candidatas y deben pasar por auditoria visual. No se promociona ninguna definicion de in-play ni de estrategia desde este output.

## Estado Actual - Visual Audit PNGs 2026

Fecha: 2026-07-07

Se generaron PNGs de inspeccion visual para los 152 `anchor_candidates_v0_1`.

```text
evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z/visual_audit_png_v0_1/
```

Manifest:

```text
evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z/visual_audit_png_v0_1/visual_inspection_manifest_v0_1.parquet
evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z/visual_audit_png_v0_1/visual_inspection_manifest_v0_1.csv
```

Resumen:

```text
png_count = 152
errors = 0
rebreak_confirmed = 97
no_rebreak_in_window = 40
fake_rebreak_no_confirmation = 11
no_rebreak_search_window = 4
```

Lectura correcta:

```text
visual_audit_png_v0_1 = evidencia humana/maquina para revisar anchors candidatos
visual_audit_png_v0_1 != validacion de estrategia
visual_audit_png_v0_1 != in-play oficial
visual_audit_png_v0_1 != edge
```

El renderer usa coordenadas compartidas para velas, marcas, lineas y cajas. Ningun anchor se pinta a ojo.
