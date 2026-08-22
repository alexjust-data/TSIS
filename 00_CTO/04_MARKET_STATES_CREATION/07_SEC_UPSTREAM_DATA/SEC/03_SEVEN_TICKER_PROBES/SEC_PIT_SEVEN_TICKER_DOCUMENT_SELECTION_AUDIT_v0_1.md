# SEC PIT Seven-Ticker Document Selection Audit v0_1

## Artifact control

```text
document_status                 = EXECUTED
authoritative_metadata_run      = sec_pit_7t_metadata_v0_2
document_selection_gate         = FAIL
physical_replay_authorization   = NOT_AUTHORIZED
parent_universe_scale           = NOT_AUTHORIZED
```

## Scope

This audit evaluates the 1,595 primary-document candidates emitted by the
seven-ticker metadata preflight. No primary documents were downloaded by the
preflight.

## Results by case

| Ticker | Inventory | Role-eligible | Selected | Coverage | Selected date range | Filing-size ceiling |
|---|---:|---:|---:|---:|---|---:|
| BNAI | 349 | 270 | 270 | 100.0% | 2021-02-09 to 2026-07-27 | 0.455 GiB |
| DOMH | 1,288 | 1,071 | 300 | 28.0% | 2016-08-08 to 2026-07-28 | 0.268 GiB |
| BBBY | 2,265 | 2,070 | 300 | 14.5% | 2018-12-28 to 2026-08-07 | 0.533 GiB |
| BGM | 150 | 103 | 103 | 100.0% | 2019-11-04 to 2026-07-30 | 0.221 GiB |
| CNOBP | 1,918 | 1,740 | 300 | 17.2% | 2018-09-04 to 2026-08-04 | 0.790 GiB |
| ALUR | 314 | 253 | 253 | 100.0% | 2023-07-07 to 2026-07-24 | 0.686 GiB |
| PGAC | 87 | 69 | 69 | 100.0% | 2024-07-24 to 2026-08-06 | 0.057 GiB |

```text
total inventory                 = 6,371
total selected                  = 1,595
filing-size upper bound         = 3.012 GiB
primary documents downloaded    = 0
```

## Blocking findings

### Fixed 300-document cap truncates history

The selector sorts newest-first and round-robins semantic roles. For DOMH,
BBBY and CNOBP, the cap removes most older history instead of producing a
causally and temporally representative sample. A successful run would therefore
look complete while silently lacking historical anchors and ownership events.

### Form membership is too broad

Every 8-K and 6-K is currently classified as an O/S and restriction candidate.
This includes many pure earnings, listing, meeting and investor-update filings.
The selection therefore over-acquires noisy event forms while missing old
history because of the global cap.

### Security-class gate is not operational

CNOBP was selected as a non-common-equity negative control. The governed
instrument-master row nevertheless has:

```text
ticker_type_code = CS
is_common_stock  = true
name             = Depositary Shares representing 1/40 interest in
                   Series A perpetual preferred stock
```

This is a source contradiction. The metadata-only runner currently emits
`G0_IDENTITY = PASS_WITH_RESTRICTIONS` unconditionally and would permit deep
issuer-level acquisition. The negative control must instead stop before O/S,
float or market-cap resolution for the listed preferred class.

### Issuer history and instrument history are not interchangeable

CIK-level filings predate several ticker/class validity intervals. Some of that
prehistory is required for SPAC and registration lineage, but it cannot be
included blindly. Selection needs an explicit lifecycle bridge and prehistory
policy, not either all-CIK history or a strict ticker-validity cutoff.

## Storage evidence

Crossing selected accessions with the previous raw pilot shows that primary
HTML/XML is materially smaller than SEC filing-size metadata:

```text
observed primary / filing-size ratios = approximately 13% to 46%
old raw primary bytes for the seven    = 696.89 MiB
```

This evidence is incomplete for the new selection and does not authorize a
forecast as fact, but it demonstrates that storage is not the current blocker.
Selection validity is the blocker.

## Required v0_2 policy

```text
G0 SECURITY-CLASS ELIGIBILITY
- reconcile ticker type, security name, FIGI/class identity and filing evidence
- halt negative controls before deep acquisition

TEMPORAL COVERAGE
- replace the global newest-first 300 cap
- preserve required anchors and events across the governed lifecycle
- expose earliest/latest covered availability and uncovered intervals

CORE FORMS
- retain periodic O/S anchors and ownership baselines across time
- retain 13D/G and Forms 3/4/5 under explicit holder/event policy
- retain registration evidence through accession relationships

EVENT FORM PROBES
- filter 8-K using Item metadata before acquisition
- treat 6-K as a separate content-probe lane because Item metadata is absent
- do not classify every 8-K/6-K as automatically relevant

REGISTRATION LINKAGE
- connect S/F registration statements, amendments, EFFECT and prospectuses
- avoid repeated prospectus acquisition without accession/registration purpose

CAPACITY
- estimate selected primary bytes after the v0_2 selection is frozen
- retain the 100 GiB free-space gate and sequential execution
```

## Verdict

```text
METADATA ACQUISITION             = PASS
IDENTITY RESOLUTION              = PASS_WITH_BLOCKING_CONFLICTS
CURRENT DOCUMENT SELECTION       = FAIL
CURRENT 300-DOCUMENT CAP         = REJECT
PHYSICAL SEVEN-TICKER REPLAY     = NOT_AUTHORIZED
NEXT ACTION                      = IMPLEMENT_AND_TEST_SELECTION_POLICY_V0_2
```
## Lifecycle coverage correction

The initial audit described the newest-first 300-document cap as a temporal
coverage failure. That statement was too broad. Comparison against the 3,109
`all_tickers` snapshots shows that every selected SEC date range covers the
currently observed ticker interval for its case.

The cap still omits older CIK/issuer history for DOMH, BBBY and CNOBP, but this
is not automatically a defect. It becomes a defect only where omitted evidence
is required to resolve the opening O/S, ownership or restriction state at the
first target cutoff. See `SEC_PIT_SEVEN_TICKER_LIFECYCLE_COVERAGE_READOUT_v0_1.md`.

Accordingly:

```text
CURRENT_TICKER_TEMPORAL_COVERAGE = PASS_WITH_RESTRICTIONS
ISSUER_PREHISTORY_SUFFICIENCY     = NOT_DETERMINED
DOCUMENT_SELECTION_GATE          = FAIL_FOR_POLICY_AND_IDENTITY_REASONS
```

## Lifecycle lane disposition - 2026-08-10

Selection policy v0_1 now recognizes 8-A*, 25/25-NSE and 8-K Item 3.01
as a separate high-priority lifecycle evidence role. The metadata-only audit
found 52 candidates and halted CNOBP at the security-class gate.

This closes only lifecycle candidate observability. It does not repair the
broader O/S, ownership, restriction and issuer-prehistory selection defects.
Accordingly:

~~~text
LIFECYCLE METADATA SELECTION = PASS_WITH_RESTRICTIONS
BROAD DOCUMENT SELECTION     = FAIL
PHYSICAL BROAD REPLAY        = NOT_AUTHORIZED
~~~