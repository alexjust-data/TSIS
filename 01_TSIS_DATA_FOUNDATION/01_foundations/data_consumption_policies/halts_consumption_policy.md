# Halts Consumption Policy v0.1

## 1. Rol

Esta policy gobierna como puede consumirse `halts_v0_1`.

El contrato asociado es:

- `01_foundations/contract_registry/dataset_contracts/halts_dataset_contract_v0_1.md`

La registry entry asociada es:

- `01_foundations/dataset_registry/halts/halts_registry_entry.yaml`

## 2. Principio rector

`halts` es infraestructura oficial de eventos y contexto regulatorio.

No es precio, no es tape, no es liquidez normal y no es alpha.

Su consumo correcto exige declarar:

- fuente oficial usada;
- unidad de evento;
- estado de taxonomia;
- granularidad temporal disponible;
- si se usa como contexto, mask, overlay o evidencia forense;
- y que flags deben viajar downstream.

## 3. Mapa de subfamilias a usos

| Subfamilia | Uso permitido | Restriccion principal |
| --- | --- | --- |
| raw official downloads | provenance y trazabilidad | no consumir directamente en modelos |
| source-specific outputs | reconciliacion por fuente | no mezclar sin dedup multisource |
| master multisource | event engine, audit overlay | respetar source y taxonomia |
| event taxonomy summaries | governance y reporting | no sustituye evento unitario |
| universe coverage summaries | cobertura `<1B>` y contexto | ausencia no prueba missing data |
| quotes/trades visual overlays | evidencia forense | no reemplaza evento oficial |
| SEC suspensions | contexto regulatorio | no usar como ventana intradia si faltan timestamps |

## 4. Consumidores permitidos

### `event_engine`

Permitido para:

- registrar eventos oficiales;
- construir calendars/masks;
- anotar ventanas de halt;
- enlazar contexto SEC.

Condicion:

- distinguir `good_full_intraday_event`, `good_date_level_event`, `regulatory_context_only`, `review_partial_identity` y `bad_unusable_event`.

### `data_audit_overlay`

Permitido para:

- explicar o priorizar casos de `quotes`, `trades`, `daily`, `minute` y `1m_split_normalized`;
- contextualizar gaps o anomalias de microestructura;
- leer bucket visual junto con evento oficial.

Condicion:

- contexto externo puede explicar, pero no rehabilita automaticamente market data local.

### `forensic_review`

Permitido para:

- inspeccion humana;
- casepacks;
- root-cause analysis;
- contraste contra auditoria historica.

Condicion:

- cada visual relevante debe declarar que muestra, que responde, que no responde y consecuencia.

### `quotes_halt_overlay`, `trades_halt_overlay`, `minute_halt_overlay`

Permitidos para:

- marcar ventanas de evento;
- estudiar coherencia de microestructura;
- separar anomalia local de mercado bajo evento.

Condicion:

- el overlay no cambia por si solo el estado de calidad del tape/libro/barra; debe viajar como factor explicativo o flag.

### `daily_event_context`

Permitido para:

- explicar dias con evento;
- anotar dias de trading especiales;
- apoyar readouts de cobertura o corporate/event context.

Condicion:

- no convertir evento intradia en retorno ni en precio ajustado.

## 5. Consumidores condicionados

### `backtest_event_mask_candidate`

Permitido solo si:

- se declara decision-time availability;
- se define si el evento excluye, enmascara, etiqueta o solo contextualiza;
- los estados `review` no entran como `good`;
- SEC date-level/context se trata separado de ventana intradia.

### `backtest_extended`

Permitido para analisis de sensibilidad con flags.

Condicion:

- mantener `halt_event_state`, `source`, `halt_date`, `halt_start_et`, `resume_trade_et` y `event_granularity`.

### `ml_flagged`

Permitido solo si:

- hay contrato de features posterior;
- se evita leakage temporal;
- cada feature declara lag;
- `review` viaja como flag/mask/sample weight, no como verdad limpia.

### `execution_simulator`

No queda habilitado por defecto.

Puede usar `halts` como:

- contexto de suspension;
- overlay de no-trade/no-quote windows;
- input para reglas futuras.

Pero la verdad de ejecucion vive en:

- `trades_raw`;
- `quotes_raw`;
- policies de ejecucion futuras.

## 6. Consumidores bloqueados

Bloqueados hasta contrato posterior:

- `live_downstream_candidate`;
- `rl_allowed`;
- `strategy_alpha`;
- cualquier proceso que tradee la presencia de halt sin protocolo de disponibilidad, latencia, execution feasibility y validacion.

## 7. Estados y consumo

| Estado | Consumo |
| --- | --- |
| `good_full_intraday_event` | event engine, audit overlay, masks condicionadas |
| `good_date_level_event` | contexto date-level, no ventana intradia exacta |
| `confirmed_halt_microstructure_coherent` | evidencia forense fuerte de coherencia |
| `regulatory_context_only` | contexto SEC, no simulacion intradia |
| `review_partial_identity` | forensic/research only |
| `halt_with_trades_signal_only` | review overlay, requiere lectura |
| `halt_with_quotes_signal_only` | review overlay, requiere lectura |
| `halt_present_but_market_clean` | review/coverage, no error automatico |
| `market_signal_without_clear_halt_window` | review, no evento oficial confirmado |
| `bad_unusable_event` | forensic only, excluir de consumo operativo |

## 8. Temporalidad y leakage

Reglas:

- `halt_date`, `halt_start_et`, `resume_quote_et`, `resume_trade_et`, release time e ingestion time no son intercambiables.
- Para backtest y ML debe declararse la fecha/hora disponible en decision time.
- Un halt publicado o conocido despues de una decision no puede usarse como feature causal de esa decision.
- SEC date-level/context no puede imputarse como hora intradia.
- Las ventanas deben expresarse en Eastern Time salvo contrato posterior.

## 9. Flags obligatorias

Deben preservarse como metadata o flags:

- `halt_event_state`;
- `event_taxonomy`;
- `visual_case_bucket` cuando aplique;
- `source`;
- `source_priority`;
- `halt_date`;
- `halt_start_et`;
- `resume_quote_et`;
- `resume_trade_et`;
- `halt_code`;
- `halt_type`;
- `is_sec_suspension`;
- `event_granularity`;
- `identity_review_flag`;
- `market_overlay_state`;
- `evidence_path`.

## 10. Usos no implicados

Esta policy no habilita:

- strategy alpha;
- RL;
- live trading;
- execution simulation final;
- automatic data repair;
- ticker identity continuity;
- price adjustment;
- ni declaracion de mercado limpio por ausencia de halt.

## 11. Condiciones para promocion futura

Para abrir consumidores mas sensibles, hace falta:

- contrato de event masks para backtest;
- contrato de event features si entra en ML;
- validadores ejecutables por consumidor;
- prueba de disponibilidad temporal;
- politica de SEC/context/date-level;
- evidence dossier actualizado si cambia taxonomia;
- changelog cuando cambie allowed consumption.

## 12. Regla final

`halts` debe viajar como capa oficial de evento gobernada.

Si un pipeline usa halts sin declarar granularidad temporal, estado, fuente y flags, esta rompiendo el contrato.
