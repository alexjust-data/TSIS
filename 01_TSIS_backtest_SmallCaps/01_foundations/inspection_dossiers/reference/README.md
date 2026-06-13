# Reference Inspection Dossier

Fecha de referencia: 2026-06-12.

## Rol

Esta carpeta gobierna la lectura institucional de `reference_v0_1`.

`reference` no es una tabla unica. Es una familia upstream de:

- identidad de ticker;
- snapshots de presencia;
- tipos de instrumento;
- exchanges;
- splits;
- dividends;
- eventos de continuidad;
- provenance operacional de descarga.

Su funcion dentro de TSIS es impedir que backtest, ML, price views, auditoria de market data y event overlays razonen sobre identidad, corporate actions o continuidad desde memoria conversacional.

## Estado actual

Estado correcto a 2026-06-12:

- `reference` esta promovido como foundation layer contractual minima.
- Ya existen dataset contract, registry entry, consumption policy, validators contract, canonical schemas y closeout institucional compacto.
- La evidencia historica fuerte existe y esta preservada bajo `01_research`.
- La evidencia pesada tambien existe en caches historicos `cache_v2`.
- El dossier moderno todavia no esta al nivel inspector de `daily`, `quotes`, `trades`, `minute` o `1m_split_normalized`.

Por tanto, la lectura precisa es:

```text
reference = contractualmente institucionalizado, pero pendiente de upgrade inspector moderno general-a-particular
```

No debe venderse como dossier visual maduro hasta que tenga population overview, manifests activos, casepacks y readout v0.2.

## Autoridad documental

Documentos actuales de `01_foundations`:

- `reference_institutional_closeout_v0_1.md`
- `reference_modernization_gap_audit_2026-06-12.md`
- `reference_upgrade_agent_prompt_2026-06-12.md`
- `../../contract_registry/dataset_contracts/reference_dataset_contract_v0_1.md`
- `../../data_consumption_policies/reference_consumption_policy.md`
- `../../dataset_registry/reference/reference_registry_entry.yaml`
- `../../validators/reference/reference_validators.md`
- `../../canonical_schemas/reference/`

Fuentes historicas obligatorias:

- `../../..//01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/`
- `../../..//01_research/01_auditoria_RAW_DATA/00_data_certification/certification/reference/`

## Evidencia historica disponible

Auditoria:

- `04_reference_closeout.md`
- `04_reference_causal_overlay_closeout.md`
- `03_reference_root_cause_audit_phase1_closeout.md`
- `cache_v2/manifest.json`
- caches parquet de identidad, presencia, splits, dividends, events y overlays causales.

Certification:

- `00_reference_current_state.md`
- `01_reference_causal_value.md`
- `02_reference_closeout.md`

La regla de source hierarchy aplica aqui igual que en `daily`, `quotes` y `trades`: no basta leer `auditoria/`; tambien hay que absorber `certification/`.

## Benchmark de madurez

Comparacion estructural observada el 2026-06-12:

| Dossier | Dirs | Files | MD | IPYNB | PNG | CSV | Parquet |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `daily` | 18 | 374 | 9 | 0 | 181 | 172 | 7 |
| `minute` | 7 | 93 | 4 | 7 | 73 | 7 | 2 |
| `1m_split_normalized` | 6 | 58 | 6 | 2 | 44 | 5 | 1 |
| `quotes` | 101 | 720 | 103 | 0 | 611 | 5 | 1 |
| `trades` | 24 | 533 | 19 | 2 | 495 | 9 | 7 |
| `reference` | 0 | 1 | 1 | 0 | 0 | 0 | 0 |

La diferencia importante no es solo numerica. Los dossiers maduros tienen:

- readout principal;
- README local;
- builder o scripts;
- evidence assets versionados;
- population visual overview;
- manifests;
- casepacks por familia;
- imagenes embebidas;
- lectura `Que muestra / Responde / No responde / Consecuencia`;
- auditoria de trazabilidad de casepacks cuando aplica.

`reference` todavia no.

## Target structure

El upgrade moderno debe aterrizar, como minimo:

```text
inspection_dossiers/reference/
  README.md
  build_reference_inspection_pack.md
  reference_institutional_closeout_v0_1.md
  reference_inspection_readout_v0_2.md
  reference_modernization_gap_audit_2026-06-12.md
  reference_casepacks_traceability_audit_v0_1.md
  evidence_assets/
    historical_cache_inventory/
    physical_root_audit/
    population_visual_overview/
    identity/
    corporate_actions/
    causal_overlays/
  good_justification/
  flagged_case_evidence_packs/
  bad_case_evidence_packs/
  causal_case_evidence_packs/
  coverage_case_evidence_packs/
```

Scripts esperados:

```text
scripts/inspection/reference/
  audit_reference_foundation_physical_root.py
  export_reference_population_visuals.py
  export_reference_casepacks.py
  build_reference_visual_readout.py
```

## Preguntas que debe responder el upgrade

1. Cual es la poblacion fisica actual de `E:/TSIS/data/reference`?
2. Que parte de la poblacion es identidad buena, review o bad?
3. Que peso tienen payloads vacios frente a eventos reales en splits/dividends/events?
4. Que muestra `all_tickers` como timeline de presencia?
5. Que familias de `overview_404` quedan abiertas?
6. Que splits alimentan realmente price views y que splits quedan como no-payload/review?
7. Que dividends son `good_dividend_event` y que cola no `CD` o no-payload exige review?
8. Que fuerza causal tienen `events -> halts`, `events -> quotes`, `splits -> trades`, `splits -> daily/1m` e `identity -> trades`?
9. Que casos concretos deben mostrarse como good, review y bad?
10. Que consumidores quedan permitidos, restringidos o bloqueados despues de leer la evidencia?

## Regla de consumo

Hasta que exista `reference_inspection_readout_v0_2.md` con assets y casepacks:

- `reference` puede seguir usandose como foundation layer bajo sus contratos actuales;
- no debe describirse como dossier visual maduro;
- no debe promoverse a feature, alpha, remap continuity service, live o RL;
- no debe usarse `ticker_change` como continuidad economica cerrada;
- no debe usarse `all_tickers` como universe final;
- no debe usarse `overview.market_cap` como membership diaria fully point-in-time.

## Regla final

`reference` esta a la altura minima contractual de `01_foundations`, pero no a la altura inspector-forense de `quotes`, `trades`, `daily` o `1m`.

El siguiente trabajo no es reescribir la auditoria historica. Es convertirla en un dossier moderno reproducible, visible y navegable.