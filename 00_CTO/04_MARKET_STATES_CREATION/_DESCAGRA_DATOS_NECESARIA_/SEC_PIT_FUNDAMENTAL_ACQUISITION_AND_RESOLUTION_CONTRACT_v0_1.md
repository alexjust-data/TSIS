# SEC PIT Fundamental Acquisition and Resolution Contract v0_1

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `sec_pit_fundamental_acquisition_and_resolution_contract` |
| `document_version` | `v0_1` |
| `document_role` | `SOURCE_ACQUISITION_AND_PIT_RESOLUTION_CONTRACT` |
| `document_status` | `DRAFT_FOR_ONE_TICKER_EXECUTION` |
| `review_verdict` | `ACCEPTED_WITH_REQUIRED_CORRECTIONS` |
| `one_ticker_pilot` | `AUTHORIZED_FOR_DESIGN_AND_EXECUTION` |
| `fifty_ticker_revalidation` | `REQUIRED_AFTER_ONE_TICKER` |
| `full_scale_4821` | `NOT_AUTHORIZED` |
| `storage_budget_certification` | `NOT_EXECUTED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-09` |

## 1. Objetivo y afirmacion permitida

Gobernar la adquisicion, extraccion, resolucion causal, validacion, retencion y
materializacion diaria de evidencia fundamental y de ownership.

```text
TSIS construye estimaciones diarias PIT reproducibles de shares outstanding,
float y ownership mediante metodologias explicitas, utilizando exclusivamente
evidencia publica elegible antes de cada cutoff y preservando cobertura,
staleness, conflictos, incertidumbre, identidad de clase y procedencia.
```

```text
DAILY PIT ESTIMATE != DAILY OBSERVED FACT
REPRODUCIBLE FLOAT ESTIMATE != EXACT HISTORICAL DAILY FLOAT
```

Outputs objetivo:

```text
SHARES_OUTSTANDING_ESTIMATE_AS_KNOWN
FLOAT_OWNER_EXCLUSION_ESTIMATE_AS_KNOWN
FLOAT_TRADABILITY_ELIGIBILITY_ESTIMATE_AS_KNOWN
FLOAT_PERCENT_ESTIMATE_AS_KNOWN
INSIDER_AFFILIATE_OWNERSHIP_PERCENT_AS_KNOWN
LARGE_BENEFICIAL_OWNER_PERCENT_AS_KNOWN
INSTITUTIONAL_OWNERSHIP_ESTIMATE_AS_KNOWN
PRESESSION_REFERENCE_MARKET_CAP_ESTIMATE_AS_KNOWN
ENTERPRISE_VALUE_ESTIMATE_AS_KNOWN
NET_CASH_PER_SHARE_ESTIMATE_AS_KNOWN
```

## 2. Orden de ejecucion

```text
metadata and identity
-> O/S anchors
-> capital events
-> daily PIT O/S resolver
-> neutral ownership ledger
-> holder deduplication
-> owner-exclusion float
-> restriction and tradability eligibility
-> presession market cap
-> global 13F context
-> cash/debt PIT, EV and net cash/share
-> end-to-end validation
-> capacity certification
```

EV y net cash/share no bloquean el gate inicial de float.

## 3. Arquitectura de adquisicion

### Nivel 1 - Metadata

Conservar submissions root y supplements, Company Facts, filing index,
accession, form, items, filing/report dates, acceptance datetime, URLs e
identidad del emisor.

### Nivel 2 - Payload selectivo

Descargar por defecto solo primary HTML/XML, XBRL relevante, ownership XML y
13F information tables seleccionadas. No descargar complete submission por
defecto.

### Nivel 3 - Evidencia estructurada

Conservar valor o evento, `measurement_at`, `effective_at`,
`eligible_from_session`, accession, URL, hash, concepto, contexto, share class,
metodo de extraccion, metodologia, excerpt, quality, conflicts y lineage.

### Nivel 4 - Raw bajo demanda

Descargar complete submissions o exhibits solo si el primary es insuficiente,
falla la extraccion, el filing es pre-XBRL, falta una tabla, un exhibit contiene
terminos necesarios, existe conflicto o el caso entra en auditoria.

## 4. Disponibilidad EDGAR

`filing_accepted_at` no equivale automaticamente a `available_at`.

Conservar:

```text
filing_transmitted_at, when observable
filing_accepted_at
filing_date
public_dissemination_at, when demonstrable
public_dissemination_state
eligible_from_session
availability_policy_id and version
```

Regla de consumo:

```text
eligible_from_session <= session_date
```

La mayoria de filings transmitidos despues de 17:30 ET pueden difundirse el
siguiente dia habil. Forms 3/4/5 y otras excepciones admitidas pueden difundirse
el mismo dia hasta 22:00 ET. La politica debe versionarse historicamente.

Fuentes iniciales:

```text
https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data
https://www.sec.gov/submit-filings/filer-support-resources/how-do-i-guides/determine-status-my-filing
```

## 5. Shares outstanding PIT

Fuentes: 10-K/Q, 20-F, 40-F y amendments; Company Facts; cover-page XBRL/text;
8-K/6-K de capital; registration statements; prospectuses; EFFECT/POS AM; y
corporate actions.

```text
SHARES_OUTSTANDING_ESTIMATE_AS_KNOWN
= latest admitted reported anchor
  + causally supported intermediate events
  + deterministic corporate-action transformations
```

Estados:

```text
OS_REPORTED_ANCHOR
OS_EVENT_SUPPORTED_ESTIMATE
OS_SPLIT_TRANSFORMED
OS_STALE_ANCHOR
OS_UNRECONCILED
OS_SOURCE_CONFLICT
OS_UNAVAILABLE
```

Conservar last anchor, supported net delta, estimate, next anchor y diferencia
de reconciliacion ex-post. Un anchor posterior mide error, pero no reescribe el
estado PIT anterior.

No usar weighted-average shares ni current shares aplicadas retrospectivamente.

```text
TECHNICAL_FEASIBILITY = PASS
EMPIRICAL_RELIABILITY = PENDING
```

## 6. Ownership evidence ledger

Fuentes: DEF 14A, 10-K Item 12, SC 13D/G y amendments, Forms 3/4/5,
selling-stockholder tables, registration statements y exhibits relevantes.

El ledger es neutral y conserva holder/group/economic-position/overlap IDs,
instrument and share class, issued common shares, derivatives separados,
direct/indirect ownership, roles, percentages, measurement/effective times,
eligible session y accession.

No sumar filas de diferentes fuentes sin resolver solapamientos.

## 7. Form 4

```text
FORM_4_TRANSACTION_SIZE != AUTOMATIC_FLOAT_DELTA
```

Recalcular la posicion economica unica posterior considerando common shares
versus derivatives, acquisition/disposition, post-transaction holdings,
direct/indirect ownership, transfers internos, holders excluidos y entidades
controladas.

## 8. Owner-exclusion float

```text
FLOAT_OWNER_EXCLUSION_ESTIMATE_AS_KNOWN[d, methodology]
= SHARES_OUTSTANDING_ESTIMATE_AS_KNOWN[d]
  - UNIQUE_SUPPORTED_EXCLUDED_ISSUED_COMMON_SHARES_AS_KNOWN[d, methodology]
```

```text
UNIQUE    = union de posiciones economicas
SUPPORTED = exclusion respaldada por evidencia publica
ISSUED    = no potential dilution
COMMON    = no derivatives sin emitir
AS_KNOWN  = evidencia elegible antes del cutoff
```

El ledger permanece neutral. Metodologias de explicit affiliates, officers and
directors, thresholds de 10/20 por ciento o vendor-comparable se aplican
downstream y se versionan.

## 9. Missing ownership y bounds

Antes de cobertura suficiente:

```text
SHARES_OUTSTANDING_ESTIMATE = value, if available
FLOAT_OWNER_EXCLUSION_POINT_ESTIMATE = UNAVAILABLE
```

No asumir `float = O/S`.

```text
FLOAT_EVIDENCE_UPPER_BOUND
= O/S estimate - shares provably excluded
```

El lower bound solo se publica si puede demostrarse que las shares estan
emitidas, unrestricted, non-affiliate-held y unlocked. Escenarios conservador,
base y permisivo permanecen separados de bounds matematicos.

## 10. Tradability eligibility

```text
OWNER_EXCLUSION_FLOAT != TRADABILITY_ELIGIBILITY_FLOAT
```

EFFECT, Rule 144 eligibility, lockup expiration y resale registration son
evidencia de elegibilidad, no entrada confirmada en supply negociable. La
restrictive legend puede requerir transfer agent y consentimiento del emisor.

Fuente:

```text
https://www.sec.gov/reports/rule-144-selling-restricted-control-securities
```

## 11. Market cap presesion

```text
PRESESSION_REFERENCE_MARKET_CAP_ESTIMATE_AS_KNOWN
= CORPORATE_ACTION_ALIGNED_REFERENCE_PRICE_AS_KNOWN
  * SHARES_OUTSTANDING_ESTIMATE_AS_KNOWN
```

El precio inicial candidato es prior eligible RTH close. Precio y shares deben
estar en la misma split basis. No usar current-session close antes de existir ni
current shares con precios historicos.

Congelar si el constructo es `LISTED_SHARE_CLASS_REFERENCE_MARKET_CAP` o
`ISSUER_EQUITY_REFERENCE_VALUE`.

La columna legacy puede conservarse como proxy ex-post, pero no es market cap
presesion PIT certificado si utiliza cierre del propio dia o weighted-average
shares.

## 12. Institutional ownership 13F

13F es contexto independiente y no se resta automaticamente del float.

```text
global 13F acquisition once
-> historical CUSIP matching
-> retain matched TSIS positions
-> aggregate by eligible filing vintage
```

Conservar manager CIK, accession, eligible session, period end, historical
CUSIP, shares, value, discretion, voting authority, amendment y coverage.

Las posiciones son trimestrales y pueden presentarse hasta 45 dias despues. No
aplicar retrospectivamente al cierre del trimestre.

Fuentes:

```text
https://www.sec.gov/rules-regulations/staff-guidance/division-investment-management-frequently-asked-questions/frequently-asked-questions-about-form-13f
https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets
```

## 13. Identidad historica

Conservar un ledger de instrument, issuer CIK, security class, ticker interval,
CUSIP interval, FIGI, effective interval, eligible session, source y quality.
No aplicar ticker, CUSIP, FIGI o share class actuales retrospectivamente sin
evidencia.

## 14. Cash, debt, EV y net cash/share

Resolver despues del float inicial desde Company Facts y financial-statement
XBRL. Congelar debt, leases, restricted cash, marketable securities, preferred
equity y minority-interest semantics.

```text
EV_ESTIMATE
= market cap + debt + preferred equity
  + non-controlling interests - cash and equivalents

NET_CASH_PER_SHARE_ESTIMATE
= (cash and equivalents - debt) / O/S estimate
```

## 15. Retencion y capacidad

```text
ALWAYS_KEEP
= metadata + accessions + timestamps + normalized facts/events
  + hashes/excerpts + selected compact primary files + lineage

KEEP_CONDITIONALLY
= complete submissions + exhibits + contracts
  + pre-XBRL, conflicts and forensic cases

REACQUIRE_ON_DEMAND
= deterministically addressable raw evidence
```

Requisitos: content-addressed storage, SHA-256 deduplication, gzip/zstd y no
duplicar documentos por ticker o pipeline.

```text
AVAILABLE_CAPACITY = approximately 900 GB
ARCHITECTURE_COMPATIBLE = PLAUSIBLE
CAPACITY_CERTIFIED = NO
```

Un ticker demuestra funcionamiento, no distribucion de storage. Despues debe
reprocesarse el piloto de 50 y medir bytes p50/p95/max por CIK, utilizacion de
primary, fallback a complete/exhibits, compression, deduplication y coverage.

## 16. Quality dimensions

Conservar separadamente source coverage, estimation, freshness, conflict,
causality e identity states. No colapsarlos en una unica confidence label.

Estados causales minimos:

```text
PIT_VALID
AVAILABILITY_SESSION_RESOLVED
AVAILABILITY_UNCERTAIN
RETROSPECTIVELY_DERIVED
LOOKAHEAD_PROHIBITED
```

## 17. Gates del piloto

```text
G0  IDENTITY_AND_SECURITY_CLASS
G1  EDGAR_METADATA_COMPLETENESS
G2  AVAILABILITY_POLICY
G3  OS_ANCHOR_EXTRACTION
G4  OS_EVENT_RECONCILIATION
G5  OWNERSHIP_SOURCE_COVERAGE
G6  HOLDER_DEDUPLICATION
G7  OWNER_EXCLUSION_METHODOLOGY
G8  RESTRICTION_AND_TRADABILITY
G9  CORPORATE_ACTION_ALIGNMENT
G10 PRESESSION_MARKET_CAP
G11 HISTORICAL_CUSIP
G12 INSTITUTIONAL_13F
G13 CASH_DEBT_AND_EV
G14 DAILY_PIT_RESOLUTION
G15 STORAGE_AND_REACQUISITION
G16 MANUAL_CHANGE_EXPLANATION
```

Cada cambio debe explicar que cambio, evento, effective time, eligible session,
source, metodologia y si el output es observado, resuelto, estimado o
unavailable.

## 18. Autorizacion

```text
ONE-TICKER END-TO-END = AUTHORIZED
OPTIMIZED 50-TICKER REPLAY = REQUIRED NEXT
4,821-INSTRUMENT SCALE-OUT = NOT AUTHORIZED
CANONICAL FLOAT PROMOTION = NOT AUTHORIZED
PREDICTIVE SCANNER CONSUMPTION = NOT AUTHORIZED
```

Secuencia:

```text
one-ticker readout
-> optimized 50-ticker replay
-> empirical storage and coverage distribution
-> methodology corrections
-> capacity certification
-> human scale-out decision
```

## 19. Dependencias

```text
DAILY_PIT_FUNDAMENTAL_CONTEXT_OUTPUTS_REFERENCE_v0_1.md
../VARIABLES_FEATURES/FLOAT_CONTEXT_SOURCE_AUDIT_PLAN_v0_1.md
../VARIABLES_FEATURES/POPULATION_TARGET_PIT_RECOVERY_AND_GOVERNANCE_PLAN_v0_1.md
```

La referencia diaria resume outputs. Este contrato gobierna como adquirir,
resolver y validar la evidencia que los produce.
