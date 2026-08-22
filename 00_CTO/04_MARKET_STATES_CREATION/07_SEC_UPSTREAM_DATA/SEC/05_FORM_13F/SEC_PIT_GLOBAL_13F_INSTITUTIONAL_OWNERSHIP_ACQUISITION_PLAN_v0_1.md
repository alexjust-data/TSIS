# SEC PIT Global 13F Institutional Ownership Acquisition Plan v0_1

## Control del artefacto

```text
document_id                  = sec_pit_global_13f_institutional_ownership_acquisition_plan
document_version             = v0_1
status                       = PENDING_PARKED_PENDING_TRADING_ACTIVITY_CLOSE
g12_status                   = BLOCKED_BY_SOURCE_NOT_ACQUIRED
physical_acquisition         = NOT_EXECUTED
long_materialization         = NOT_AUTHORIZED
canonical_promotion          = NOT_AUTHORIZED
scanner_backtest_consumption = NOT_AUTHORIZED
scope                        = ALL_GOVERNED_INSTRUMENT_IDENTITIES
```

## 1. Decision de arquitectura

La adquisicion 13F no debe repetirse ticker por ticker. TSIS debe adquirir una
vez cada vintage global de filings 13F e information tables, normalizarlo bajo
un ledger comun y despues resolver las posiciones que correspondan a todos los
tickers mediante CUSIP historico y clase de security.

```text
GLOBAL 13F ACQUISITION ONCE PER VINTAGE
-> MANAGER / ACCESSION / AMENDMENT LEDGER
-> INFORMATION TABLE POSITIONS
-> HISTORICAL CUSIP + SECURITY-CLASS MATCH
-> ELIGIBLE FILING SESSION
-> ALL-TICKER PIT AGGREGATION
```

Los filings del issuer no sustituyen esta fuente porque los 13F son presentados
por los investment managers bajo el CIK del manager.

## 2. Secuencia pendiente obligatoria

Una vez cerrado y certificado el trabajo activo de Trading Activity, y solo tras
una autorizacion humana separada, el carril G12 debe:

1. descargar globalmente los filings 13F y sus information tables para todos los
   gestores/vintages dentro del periodo gobernado;
2. extraer cada information table conservando manager CIK, accession, report
   period, filing acceptance, amendment y source hash;
3. buscar cada posicion por CUSIP historico y reconciliarla contra la identidad,
   share class e intervalo temporal TSIS correctos;
4. deduplicar managers, accessions, reenvios y cadenas de amendments sin sumar
   dos veces una misma posicion economica reportada;
5. aplicar la fecha de disponibilidad publica y la `eligible_from_session` de
   cada filing; `period_end` nunca puede utilizarse como fecha de disponibilidad;
6. agregar las posiciones admitidas por instrumento, ticker, clase, vintage y
   sesion elegible para todo el universo gobernado, emitiendo cobertura y
   missingness explicitas.

## 3. Grain y outputs minimos

### Ledger fuente

```text
manager_cik x accession_number x report_period x information_table_row
```

Campos minimos:

```text
manager_cik
accession_number
form
amendment_type
report_period
filing_accepted_at
eligible_from_session
issuer_name_reported
class_title_reported
cusip_reported
shares_reported
share_type
value_reported
investment_discretion
voting_authority
source_url
source_sha256
quality_state
```

### Resolucion TSIS

```text
instrument_id x security_class_id x report_period x eligible_filing_vintage
```

Outputs minimos:

```text
institutional_shares_reported_as_known
institutional_ownership_percent_as_known
matched_manager_count
matched_position_count
historical_cusip_match_state
amendment_resolution_state
coverage_state
estimation_state
blocker_codes
```

`UNAVAILABLE` y `UNMATCHED_CUSIP` deben permanecer distintos de cero.

## 4. Semantica PIT y limites

- Una posicion 13F representa un snapshot trimestral reportado con retraso; no
  es la cartera diaria real del manager.
- La posicion solo puede consumirse desde la sesion en la que el filing era
  publicamente elegible, nunca retrospectivamente desde `period_end`.
- Un amendment no debe reescribir silenciosamente lo que TSIS podia conocer
  antes de su propia disponibilidad.
- Confidential treatment, securities fuera del universo 13F, posiciones no
  reportables y CUSIP no resueltos deben exponerse como limites de cobertura.
- Institutional ownership es contexto independiente. No se resta
  automaticamente de owner-exclusion float ni resuelve G8 tradability.

## 5. Gates antes de materializacion larga

```text
13F-G0  SOURCE INVENTORY AND PERIOD SCOPE
13F-G1  GLOBAL ACQUISITION PLAN / RESULT PARITY AND HASHES
13F-G2  INFORMATION-TABLE SCHEMA AND ROW AUDIT
13F-G3  MANAGER / ACCESSION / AMENDMENT DEDUPLICATION
13F-G4  HISTORICAL CUSIP AND SECURITY-CLASS MATCH
13F-G5  PIT AVAILABILITY AND ELIGIBLE SESSION
13F-G6  INSTRUMENT AGGREGATION AND MISSINGNESS
13F-G7  ALL-TICKER COVERAGE AND STRATIFIED ERROR AUDIT
13F-G8  HUMAN SCALE AUTHORIZATION
```

Antes de autorizar una adquisicion o materializacion larga se debe ejecutar un
probe production-equivalent acotado por cada shard previsto, usando el mismo
codigo, config, schema, fuentes y policies. La auditoria debe revisar variable
por variable, incluir amendments, CUSIP changes, ticker reuse, unmatched CUSIP,
zero/NULL y una muestra legible de valores. Un fallo invalida todos los probes
de esa version.

## 6. Contrato de operacion larga y recuperacion

La ejecucion fisica futura debe cumplir `LONG_RUNNING_OPERATIONS_CONTRACT.md`:

```text
pre-manifest
exact source/vintage inventory
PID and wrapper identity
heartbeat and live log
content-addressed immutable objects
append-only acquisition ledger
separate monitor
free-space gate
resume with source/config/schema fingerprint
final manifest and audit readout
```

Un resume solo puede reutilizar objetos cuyo hash y lineage coincidan. No puede
mezclar versiones de schema, politicas de amendment o mapeos CUSIP.

## 7. Criterio de cierre

G12 puede pasar como maximo a `PASS_WITH_RESTRICTIONS` cuando la adquisicion
global, deduplicacion, disponibilidad PIT, mapeo CUSIP/clase, agregacion y
cobertura estratificada hayan sido ejecutadas y auditadas. El cierre no implica
portfolio diario exacto, promocion canonica ni autorizacion de consumo.

