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
C:/TSIS_Data/00_TSIS_Lab/LOCAL_RULES.md
```

Resumen:

```text
ohlcv_1m raw no es verdad visual ni tabla oficial por si solo.
Toda vela 1m debe declarar vista, repair/guard state, lineage y scale guard raw/quotes cuando aplique.
```


## Ruta Oficial Actual De Ejecucion

Para construir el denominador del scanner no se usa `candidate_events.parquet` ni ningun run antiguo del notebook DAS.

La ruta oficial de `EXP_DAS_FRONTSIDE_DISCOVERY_0002` empieza en datos historicos y contratos del laboratorio:

```text
E:/TSIS/data/ohlcv_1m
+
repair shards / repair_manifest_lt1b_v0_1
+
master_daily_table_v0_1 para prior_close
+
E:/TSIS/data/reference/overview para market_cap declarado
-> scanner denominator reproducible
```

Script oficial actual:

```text
scripts/build_2026_scanner_from_quote_guarded_1m_v0_1.py
```

Los scripts que consumen outputs antiguos del DAS quedan como referencia historica o visual, no como fuente normativa del denominador cientifico.
