# Massive / SEC Lifecycle Window Reconciliation Contract v0_1

## Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `massive_sec_lifecycle_window_reconciliation_contract` |
| `document_version` | `v0_1` |
| `document_role` | `LIFECYCLE_SOURCE_RECONCILIATION_CONTRACT` |
| `status` | `ACTIVE_CANDIDATE` |
| `promotion_status` | `NOT_AUTHORIZED` |
| `parent_universe_scale_status` | `NOT_AUTHORIZED` |

## Hecho preservado

TSIS ya dispone de ventanas temporales por ticker procedentes de la historia de referencia suministrada por Polygon/Massive.

```text
MASSIVE / POLYGON SNAPSHOTS
        |
        +-- first_seen_date
        +-- last_seen_date / last_observed_date
        +-- list_date, cuando el proveedor lo informa
        +-- delisted_utc, cuando el proveedor lo informa
        +-- source_final_delisted_utc
```

`first_seen_date` y `last_seen_date` se obtuvieron recorriendo los snapshots historicos del proveedor. No son fechas inventadas por el proceso SEC actual. Cuando `delisted_utc` no estaba disponible para un instrumento inactivo, la fundacion permitio un fallback separado y trazable: `source_final_delisted_utc = inferred_last_seen`.

## Fuentes TSIS

```text
01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/00_descarga_universo.md
01_TSIS_DATA_FOUNDATION/01_research/LT1B_UNIVERSE_SOURCE_OF_TRUTH_CERTIFICATION.md
01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/universes/lt1b_universe_schema_contract.md
01_TSIS_DATA_FOUNDATION/01_foundations/contract_registry/dataset_contracts/instrument_master_dataset_contract_v0_1.md
```

Materializacion vigente declarada:

```text
G:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet
build_run_id = instrument_master_v0_1_20260621T145725Z
```

## Distincion semantica obligatoria

```text
VENDOR OBSERVED WINDOW
= primera y ultima observacion dentro de snapshots del proveedor

VENDOR REPORTED LIFECYCLE DATE
= list_date o delisted_utc informado por el proveedor

SEC REGULATORY EVIDENCE
= filing y evento regulatorio de una clase identificada

MARKET PRESENCE BOUND
= primera o ultima observacion en daily/trades

LEGAL LISTING / DELISTING DATE
= fecha admitida solamente tras evidencia suficiente
```

Estas autoridades pueden coincidir, diferir o no ser comparables. Una diferencia no demuestra automaticamente un error del proveedor ni de SEC.

## Auditoria futura obligatoria por identidad

Cuando exista evidencia SEC suficiente, debe materializarse una fila por `instrument_id + security_class_id + ticker interval` con:

```text
ticker
cik
instrument_id
security_class_id
vendor_first_seen_date
vendor_last_observed_date
vendor_list_date
vendor_delisted_utc
vendor_delisted_source
sec_registration_date
sec_exchange_trading_end_date
sec_form25_filing_date
sec_legal_delist_date
sec_source_accessions
market_first_daily_date
market_last_daily_date
market_first_trade_at
market_last_trade_at
start_delta_calendar_days
end_delta_calendar_days
comparison_state
identity_match_state
class_match_state
quality_state
```

Estados minimos:

```text
EXACT_MATCH
WITHIN_TOLERANCE
VENDOR_EARLIER
SEC_EARLIER
MARKET_PRESENCE_ONLY
NON_TARGET_SECURITY_CLASS
TICKER_REUSE_CONFLICT
SOURCE_DATE_UNAVAILABLE
NOT_COMPARABLE
```

## Regla de no sobrescritura

La evidencia SEC no debe sobrescribir silenciosamente las ventanas Massive/Polygon. Deben coexistir, conservar su provenance y producir un readout de comparacion. Solo un contrato de promocion posterior podra seleccionar una autoridad lifecycle canonica.

## Caso conocido: BBBY

La fila vigente de `instrument_master_v0_1` conserva una ventana ticker-wide que comienza en `2016-10-25`, mientras que la identidad objetivo SEC actual se observa desde 2025. Esto exige reconciliacion por identidad/clase y demuestra por que no debe compararse SEC contra el ticker string sin intervalos.

## Gate de cierre

```text
PASS solamente si:
1. identidad y clase coinciden;
2. cada fecha conserva fuente y semantica;
3. NULL no se convierte en coincidencia;
4. suspension no se convierte en delisting legal;
5. fecha programada exige confirmacion posterior;
6. diferencias quedan cuantificadas ticker por ticker;
7. no se sobrescribe ninguna autoridad fuente.
```