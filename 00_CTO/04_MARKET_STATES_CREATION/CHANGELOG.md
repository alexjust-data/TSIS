# Market States Creation Changelog

## 2026-08-10 | SEC PIT seven-ticker metadata preflight

- Froze a seven-case stratified replay: BNAI, DOMH, BBBY, BGM, CNOBP, ALUR and PGAC.
- Added a sequential, resumable coordinator with a 100 GiB free-space floor.
- Executed plan-only and metadata-only preflights without downloading primary documents.
- Inventoried 6,371 filings and selected 1,595 primary-document candidates.
- Established a conservative 3.012 GiB filing-size upper bound; the deduplicated metadata store occupies 10.54 MiB.
- Classified `sec_pit_7t_metadata_v0_1` byte forecasting as non-authoritative due to an incorrect field binding; `v0_2` uses `filing_size_bytes`.
- Full physical replay and parent-universe scale-out remain unauthorized pending review.

Este changelog conserva hitos semanticos, contractuales y experimentales de
`00_CTO/04_MARKET_STATES_CREATION`.

No sustituye Git, los readouts versionados, `00_CTO/CHANGELOG.md` ni los
changelogs de Data Foundation.

## Unreleased

## 2026-08-10 | SEC PIT fundamental context | BNAI G8 registration/O/S reconciliation

- Completed governed run `sec_pit_bnai_g8_os_reconciliation_v0_40_20260810`.
- Versioned the registration-scope clause extractor to v0.2 after correcting four derivative/issuable components previously classified as issued.
- Final scope: 18 contingent/future components, six reported-current candidates and four non-components.
- Added `registration_component_os_reconciliation_ledger.parquet` and its machine-readable readout.
- Reconciled all six reported-current candidates against causal O/S capacity: six consistent, zero conflicts, zero unavailable; two rely on stale O/S anchors.
- Preserved zero O/S inclusion confirmations, zero tradable-supply confirmations and zero non-null daily tradability estimates.
- G7 remains `PASS_WITH_RESTRICTIONS`; G8 remains `BLOCKED_BY_INPUT_GATES` pending lockup, legend, resale-condition and methodology gates.

### 2026-08-10 - SEC PIT BNAI G7/G8 executed handoff

- Added `CURRENT_STATUS_AND_HANDOFF_v0_10.md`, superseding `v0_9` as the current handoff.
- Registered authoritative run `sec_pit_bnai_g8_condition_gate_v0_38_20260810` under `D:/TSIS/fundamental_context/sec_pit_v0_1`.
- Recorded G7 `PASS_WITH_RESTRICTIONS`: 82 non-null owner-exclusion estimates and 414 causal-baseline-unavailable NULL sessions.
- Recorded the G8 component-condition subgate: 28 components, 24/24 applicable EFFECT links, 14 unconfirmed future/contingent components and 10 effective-registration components with restrictions unresolved.
- Preserved G8 as `BLOCKED_BY_INPUT_GATES`, with zero tradable-supply confirmations and zero non-null tradability estimates.
- Marked `v0_37` non-authoritative due to its insufficient 100-document acquisition cap; the governed BNAI scope uses 300.
- Kept canonical promotion, 50-ticker replay and 4,821-instrument scale-out unauthorized.

### 2026-08-10 - Information Object physical data-root authority

- Added `INFORMATION_OBJECT_DATA_ROOT_AUTHORITY_v0_1.md`.
- Established `D:/TSIS/information_objects` as the exclusive physical root for experimental and canonical Information Object / Representation Model data.
- Required profile -> object -> model -> binding -> run hierarchy.
- Preserved `G:/TSIS/data` as upstream source authority.
- Redirected Trading Activity Binding A v0.2 outputs to `D:` and passed the 240-block TA-3 preflight.

### 2026-08-09 - TA-3 Binding A provisional conformance audit

- Added `VARIABLES_FEATURES/TRADING_ACTIVITY_TA3_BINDING_A_SPEC_IMPLEMENTATION_CONFORMANCE_READOUT_v0_1.md`.
- Added the repeatable finalized-block schema auditor and machine-readable JSON evidence.
- Confirmed all eleven current-state variables and the multiscale activity-rate contrast in finalized outputs.
- Found `intertrade_duration_compression` specified but not implemented.
- Found stale `v0_1` feature/binding lineage, two data-dependent baseline schemas, and missing `duplicate_policy_id` / `coverage_mode` metadata.
- Kept the active TA-3 execution running; canonical promotion remains unauthorized.

### 2026-08-09 - SEC PIT acquisition and resolution contract

- Added `_DESCAGRA_DATOS_NECESARIA_/SEC_PIT_FUNDAMENTAL_ACQUISITION_AND_RESOLUTION_CONTRACT_v0_1.md`.
- Governed metadata-first acquisition, selective primary/XML retention,
  structured evidence, and complete-submission fallback.
- Separated EDGAR acceptance from eligible consumption session.
- Formalized O/S anchors, ownership deduplication, supported-exclusion float,
  tradability eligibility, corporate-action-aligned market cap and 13F context.
- Authorized one-ticker execution while prohibiting full 4,821-instrument
  acquisition until optimized 50-ticker replay and capacity certification.

### 2026-08-09 - Daily PIT fundamental-context reference

- Added `_DESCAGRA_DATOS_NECESARIA_/DAILY_PIT_FUNDAMENTAL_CONTEXT_OUTPUTS_REFERENCE_v0_1.md`.
- Frozen the daily human reference for shares outstanding, owner-exclusion
  float, tradability eligibility, ownership percentages, presession reference
  market cap, enterprise value and net cash per share.
- Recorded that these outputs are daily PIT estimates resolved from sparse
  public events, not exact daily observed facts.
- Preserved methodology, deduplication, provenance, freshness, conflict and
  epistemic-limit requirements.

### 2026-08-08 - Experimental-to-canonical lifecycle clarification

- Added `EXPERIMENTAL_TO_CANONICAL_REPRESENTATION_LIFECYCLE_v0_1.md` as the
  active lifecycle contract for all Market State representation work.
- Distinguished feature horizon, PIT baseline lookback and calendar
  materialization coverage.
- Recorded that TA-3 Binding A is a restricted experimental development
  materialization, not the final canonical 2005-2026 history.
- Defined the sequence from Binding A/B/justified C through development,
  temporal OOS, admission, canonical builder promotion and a separate governed
  full-history production materialization.
- Established that backtests normally consume validated versioned
  representation rows and quality states instead of recalculating raw-event
  windows for every request.
- Required reusable event, coverage, rolling-window and PIT-baseline
  infrastructure across bindings and Information Objects.

### 2026-08-08 - TA-3 broad execution recovery

- Added current handoff `CURRENT_STATUS_AND_HANDOFF_v0_9.md`.
- Broad Binding A execution moved from `READY_FOR_HUMAN_LAUNCH` to
  `RUNNING_WITH_CONTROLLED_TWO_WORKER_CONCURRENCY`.
- Recorded loss of parent orchestrators for shards 0, 2 and 3 while preserving
  completed block outputs.
- Corrected resume dispatch: complete blocks are skipped, partial blocks receive
  `--resume`, and new blocks start normally.
- Recorded the failed first recovery of shard 2 caused by forwarding `--resume`
  to a new second block.
- Reduced concurrency from four workers to two after observing approximately
  6 GB per worker during PIT baseline materialization on a 31.9 GB host.
- Upgraded the monitor to expose nested stage/session/row/partition progress,
  elapsed time, CPU, heartbeat freshness and process liveness.
- Snapshot: shard 0 `6/60`, shard 1 `15/60`, shard 2 queued with one complete
  block, and shard 3 queued with five complete block outputs.
- Confirmed that the parallel SEC filing lane uses governed
  `instrument_master_v0_1` and does not block Trading Activity TA-3.

### Added

- External independent-review handoff `handoffs/EXTERNAL_REVIEW_TRADING_ACTIVITY_PIT_20260807_v0_1.zip`, with a reproducible builder, reading order, prior-review record, provider-source findings and SHA-256 package manifest.
- Superseded handoff `CURRENT_STATUS_AND_HANDOFF_v0_8.md`, retained as historical evidence.
- Current roadmap `TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_3.md`.
- Source dependency readout `TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_5.md`.
- TA-3 preregistration
  `TRADING_ACTIVITY_STRATIFIED_DEVELOPMENT_SAMPLE_PLAN_v0_1.md`.
- PIT dependency plan
  `POPULATION_TARGET_PIT_RECOVERY_AND_GOVERNANCE_PLAN_v0_1.md`.
- Float audit plan `FLOAT_CONTEXT_SOURCE_AUDIT_PLAN_v0_1.md`.
- Parallel-lane authority
  `TRADING_ACTIVITY_PARALLEL_WORKSTREAM_COORDINATION_v0_1.md`.
- Parent integration handoff `PENDING_PARENT_REGISTRY_UPDATES_v0_4.md`.

### Confirmed physical evidence

```text
master_daily_table_v0_1
= 4,824 tickers
  7,369,699 expected daily contexts per price view
  2005-01-03 through 2026-03-09

fundamentals_asof_table_v0_1
= 621,756 statement observations
  4,813 tickers
  2010-04-22 through 2026-04-03
```

### Changed

- TA-3 sample and G-only source gate are frozen and validated for the restricted
  experimental profile.
- Broad TA-3 Binding A execution is active under a two-worker capacity limit.
- The target development sample is frozen at 240 ten-session blocks and 2,400
  target instrument-sessions, with validation and final-test lockboxes.
- Market-cap eligibility is separated from last-observed instrument metadata.
- Float is separated from shares outstanding and placed in a parallel
  event-driven source-audit lane.
- README and AGENTS now resolve to handoff v0_9 and roadmap v0_3.

### Current boundary

```text
TA-1 / TA-2
= PASS_WITH_RESTRICTIONS

TA-3 DESIGN
= FROZEN_AND_VALIDATED

POPULATION TARGET PIT SELECTOR GATE
= PASS_WITH_RESTRICTIONS_FOR_FROZEN_TA3_SAMPLE

TA-3 BROAD EXECUTION
= RUNNING_WITH_CONTROLLED_TWO_WORKER_CONCURRENCY

FLOAT SOURCE GATE
= NOT_EXECUTED

OOS / MODEL ADMISSION / CANONICAL PROMOTION
= NOT_AUTHORIZED
```

The previously completed AACT run, long-path correction, 46-test regression
and independent validation remain recorded by their versioned readouts.

## 2026-08-07

### Binding A implementation milestone

- Se congelo `TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md` para el
  piloto determinista con unidad `symbol-second`, ventanas 5, 15, 30, 60 y 300
  segundos, subventanas right-anchored y denominadores completos.
- Se implementaron current state, contraste multiescala y baseline PIT.
- La cobertura inicial alcanzo `37 passed`.
- Se ejecuto un smoke fisico sobre `AAGR / 2023-12-11 RTH` con 5,130 trades
  fuente, 5,126 elegibles, 4 no elegibles y 0 conditions desconocidas.
- Se congelo el plan de 130 sesiones AACT, con 125 sesiones de warmup, 5 de
  evaluacion y dos early closes.
- El set posterior de runner y monitor elevo la regresion a `45 passed` y
  supero un segundo smoke fisico normal/early-close.

### Current authorization

```text
MULTISESSION PILOT RUN PLAN          = COMPLETE
RUNNER, CONFIG AND MONITOR           = IMPLEMENTED_AND_TESTED
PRELAUNCH TEST GATE                  = PASS
FULL DETERMINISTIC SYMBOL-SECOND RUN = READY_FOR_HUMAN_LAUNCH, NOT_STARTED
STRATIFIED OR OOS COMPARISON         = NOT_AUTHORIZED
TABLE MAPPING                        = NOT_STARTED
WAKE-UP DETECTOR                     = NOT_STARTED
CANONICAL PROMOTION                  = NOT_AUTHORIZED
```

## 2026-08-06

### Scientific and semantic framing

- Se definio el proceso humano `Dormancy -> activation -> In-Play -> Frontside
  -> deterioration -> termination -> Backside`.
- Se separaron fenomeno, Information Object, Representation Model, Physical
  Implementation, detector, policy y execution.
- `WAKE_UP_EVENT_CANDIDATE_DEFINITION_V0_2` quedo como candidato semantico, no
  como Event Type operacional.
- Wake-up quedo definido por episodio y separado de In-Play, Frontside,
  Tradability, outcomes y edge.

### Information Object and Representation Model

- Se definio el perfil candidato de Information Objects para Wake-up.
- `Trading Activity` fue seleccionado como primer objeto.
- La enmienda de alineacion fijo:

```text
ABSOLUTE-AND-PIT-RELATIVE
MULTISCALE MARKED ACTIVITY PROCESS

TRANSITION DYNAMICS
AND MINIMAL ANTI-ARTIFACT CORROBORATION
```

- Se resolvieron frontera Binding A/B, estados de observacion y calculo,
  denominador fijo, cardinalidades de baseline y naming multiescala.
- Se rectifico que el conflicto de naming no estaba en
  `00_TABLES_MARKET_STATE_EVENT_STATE.md`.

### Source audit and interim RTH scope

- `TRADING_ACTIVITY_AUDIT_CONTRACT_v0_2.md` establecio la auditoria fisica.
- Se autorizo trabajo provisional sobre
  `LEGACY RTH RECONCILED EVENT-TIME RESEARCH-ONLY`.
- La semantica se limito a `first observable transition during RTH`.
- Premarket, after-hours, revision awareness y latencia historica medida
  quedaron fuera del scope legacy.
- Se registro latencia simulada primaria de 1,000 ms y sensibilidades de 100 ms
  y 5,000 ms.

### Coverage and provider reference evidence

- Se auditaron 100 tareas: 83 `DOWNLOADED_OK`, 17 `DOWNLOADED_EMPTY` y 100
  `PASS_WITH_RESTRICTIONS`.
- Las 83 particiones presentes pasaron lectura, schema y row-count.
- Se versionaron 55 condition codes y 27 stock exchanges de Massive sin
  persistir API keys.

### Trade eligibility evidence

- La policy v0_2 separo activity event, share volume, dollar volume, causal
  arrival y price forming.
- Se revisaron 14 condition codes observados; otros 41 permanecen fail-closed.
- Se evaluaron 23,855 trades: 23,604 elegibles, 251 no elegibles y 0 unknown.
- Se preservaron 98 flags de duplicado exacto.
- El source gate alcanzo
  `PASS_WITH_RESTRICTIONS_FOR_DETERMINISTIC_PILOT`.

### Massive future acquisition

- `_MASSIVE_TRADES_FULL_BACKFILL_REQUIREMENTS.md` fijo universo completo,
  historia accesible completa, todas las sesiones y payload completo.
- El RTH legacy se preserva y no se sobrescribe.
- El backfill sigue `NOT_STARTED` y activa revalidacion obligatoria.

## Historical path note

`TRADING_ACTIVITY_SOURCE_OBSERVABILITY_MATRIX_v0_1.md` fue una denominacion
temprana. El contrato activo es
`VARIABLES_FEATURES/TRADING_ACTIVITY_AUDIT_CONTRACT_v0_2.md`; no recrear el
pathname antiguo como autoridad paralela.

## 2026-08-07 - Documentation chain consolidation

- Removed superseded handoffs `CURRENT_STATUS_AND_HANDOFF_v0_1.md` through `v0_6.md`.
- Removed superseded parent-registry notes `PENDING_PARENT_REGISTRY_UPDATES_v0_1.md` through `v0_3.md`.
- Retained `CURRENT_STATUS_AND_HANDOFF_v0_8.md` and `PENDING_PARENT_REGISTRY_UPDATES_v0_4.md` as the active authorities.
- Preserved governed execution evidence in `VARIABLES_FEATURES` readouts; no scientific evidence was deleted.
- Consolidated the complete Trading Activity/Wake-up roadmap into `TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_3.md` and removed roadmap v0_1/v0_2.
- Removed superseded v0_1 documents for Binding A exact specification, multisession runner implementation readout, RTH coverage sidecar and trade eligibility after redirecting active references to v0_2.
- Preserved the Source Observability readout chain because each revision records distinct executed evidence or a source-gate decision.
- Reduced `handoffs/` to the verified immutable `EXTERNAL_REVIEW_TRADING_ACTIVITY_PIT_20260807_v0_1.zip` and its SHA-256 sidecar.
- Removed the stale expanded builder package and the unversioned preliminary ZIP after verifying the retained package hash.


## 2026-08-10 - SEC PIT G8 event reconciliation v0_43

- Normalized Assignment Agreement narrative dates to ISO and fixed a
  case-sensitive effective-date extraction defect discovered by tests.
- Added a source-authority reconciliation ledger that reduces 23 filing
  observations to five economic events while preserving all corroboration.
- Preserved one SEC numeric conflict without silent correction.
- Confirmed zero tradable-supply events and zero non-null daily tradability
  estimates; G8 remains `BLOCKED_BY_INPUT_GATES`.
- Recorded authoritative run
  `sec_pit_bnai_g8_assignment_reconciled_v0_43_20260810` on `D:`.
## 2026-08-10 - SEC PIT targeted exhibits and lot linkage v0_45

- Acquired only ex10-1/ex10-2 under the governed exhibit-on-demand policy.
- Added semantic schedule extraction and purchaser-to-selling-lot linkage.
- Linked 7/7 purchasers and exact quantities totaling 1,185,000 shares.
- Preserved the BEN 2,000,000/200,000 numeric conflict with raw and resolved fields.
- Emitted zero tradable-supply confirmations; G8 remains blocked.
## 2026-08-10 - August funding evidence v0_49

The sentence-bounded extractor resolves the November 13, 2024 disclosure as:

```text
gross proceeds = 550,000 USD
combined shares reported = 220,000
contract rule = one SPA share + one Sponsor share per 5 USD
SPA shares supported = 110,000
Sponsor shares supported = 110,000
failed required funding = 1,250,000 USD
tradable-supply confirmations = 0
```

Authoritative run: `sec_pit_bnai_g8_august_funding_evidence_v0_49_20260810`.
Runs v0_46, v0_47 and v0_48 are preserved as `QUARANTINED` because audit found
cross-transaction/cross-sentence matches to the May SPA. They are prohibited as
downstream evidence. The 110,000 Sponsor shares are aggregate condition-supported
releases as of the disclosure, but purchaser allocation and cancellation amounts
remain unavailable. G8 remains `BLOCKED_BY_INPUT_GATES`.
## 2026-08-10 - August funding multivintage resolver v0_53

The governed multivintage builder scanned the acquired primary-document set and
reconciled 24 source observations into seven PIT vintages. Authoritative run:
`sec_pit_bnai_g8_august_multivintage_v0_53_20260810`.

```text
2024-09-13 / eligible 2024-09-16: 50,000 escrow shares, lot unattributed
2024-11-13 / eligible 2024-11-15: 220,000 combined shares / $550,000, equation consistent
2025-02-14 / eligible 2025-02-17: 110,000 / rendered $550, source numeric conflict
2025-03-27 / eligible 2025-04-01: 110,000 / rendered $550, source numeric conflict
2025-03-31 / eligible 2025-06-05: partial termination, purchasers unidentified
2025-06-30 / eligible 2025-10-13: partial termination reiterated
2025-09-30 / eligible 2025-11-26: partial termination reiterated
```

v0_51 is `FAILED` due an unsupported numeric token. v0_52 is
`SUPERSEDED_INCOMPLETE_QUALITY_CLASSIFICATION`. Neither is authorized downstream.
The 2025 `$550` renderings are not silently changed to `$550,000`; they remain
`SOURCE_NUMERIC_CONFLICT`. Cancellation quantities and purchaser allocation stay
NULL. Tradable-supply confirmations remain zero and G8 stays
`BLOCKED_BY_INPUT_GATES`.
## 2026-08-10 - Lockup lifecycle, corporate actions and presession market cap v0_54-v0_58

G8 lockup evidence now resolves the six ex10-2 schedule rows totaling 1,252,500
shares. The contract reports a release of the prior lockup, subject to side-letter
execution and initiation of transfer to escrow, plus a 25% ADV transfer limit.
The later 10-Q supports the 1,185,000-share Sponsor transfer only from its own
public availability date. Neither legend-removal instruction nor registration
proves completed tradability.

```text
v0_54 lockup lots = 6; reported total = 1,252,500
v0_55 daily lifecycle rows = 2,976 (496 sessions x 6 lots)
tradability confirmations = 0
G8 = BLOCKED_BY_INPUT_GATES
```

G9 consumed only the primary `reference` split row from the governed corporate
actions table. The duplicate `additional` row was retained as corroboration but
not applied twice. BNAI's 10-for-1 reverse split effective 2025-12-12 transforms
58 stale pre-split O/S rows from that session onward.

```text
v0_56 daily O/S rows = 496
primary splits applied = 1
secondary duplicates ignored = 1
G9 = PASS_WITH_RESTRICTIONS
```

G10 proved from BNAI's physical downloader checkpoint that the source under
`G:/TSIS/data/ohlcv_daily` was requested with `adjusted=true`. It therefore must
not be multiplied directly by historical-basis O/S. The builder recovers the
historical price basis with future split factors and then aligns prior eligible
RTH close to the target session basis before multiplication.

Run v0_57 was rejected during mandatory first-output audit because pandas `NaN`
O/S was treated as available. A regression test was added and v0_58 supersedes
it. v0_57 is `NOT_AUTHORIZED` downstream.

```text
v0_58 daily rows = 496
market cap estimated = 485
market cap unavailable due O/S = 10
market cap unavailable due price = 1
duplicates = 0
non-finite resolved prices = 0
non-positive market caps = 0
provisional price-and-cap eligible sessions = 212
SEC PIT tests = 67/67 PASS
ruff = PASS
G10 = PASS_WITH_RESTRICTIONS
```

Authoritative run:
`sec_pit_bnai_g10_presession_market_cap_v0_58_20260810`.

This is a one-instrument pipeline pilot, not authorization to scale blindly.
The next scale gate requires a stratified filing/issuer sample and an explicit
parent-universe manifest resolution (4824 vs later references to 4821).
## 2026-08-10 - Historical CUSIP, 13F source gate, core EV and change explanations v0_59-v0_62

G11 extracted CUSIP observations only from SEC objects already acquired. Checksum
validation rejects narrative false positives. The issuer-number gate excludes the
pre-combination SPAC CUSIP `G2758T109` from the BNAI share class.

```text
source observations = 16
admitted BNAI observations = 3
104932108 = 2024-07-29 through 2025-12-11
104932207 = 2025-12-12 through 2026-03-09
pre-first-supported interval = CUSIP_UNAVAILABLE
G11 = PASS_WITH_RESTRICTIONS
```

G12 audited the official local data roots and found no acquired global 13F
information-table source. Institutional ownership remains `UNAVAILABLE`, never
zero. Run `sec_pit_bnai_g12_13f_source_audit_v0_60_20260810` records:

```text
G12 = BLOCKED_BY_SOURCE_NOT_ACQUIRED
required source = GLOBAL_SEC_13F_INFORMATION_TABLE_ACQUISITION
```

G13 resolves only same-measurement-date, causally eligible Company Facts for
cash, ConvertibleNotesPayable and ShortTermBorrowings. Facts measured before the
BNAI instrument valid interval are excluded. The output is deliberately named
`CORE_EV_ESTIMATE`; it is not represented as complete enterprise value.

```text
daily rows = 496
core EV calculated = 391
incomplete/unavailable = 105
lookahead rows = 0
non-finite core EV rows = 0
G13 = PASS_WITH_RESTRICTIONS
```

G16 emits one explanation row per daily state. The split session 2025-12-12 is
explained by corporate-action basis change, prior-close update and CUSIP interval
change. Counts are:

```text
prior-close updates = 495
O/S anchor vintage changes = 2
balance-sheet vintage changes = 6
CUSIP interval changes = 2
corporate-action basis changes = 1
G16 = PASS_WITH_RESTRICTIONS
```

Authoritative runs are v0_59 through v0_62 under
`D:/TSIS/fundamental_context/sec_pit_v0_1/runs`. This closes the executable BNAI
pilot except G8 tradability and G12 institutional ownership. Scale-out is not
authorized until the optimized stratified replay and parent-universe identity
scope are frozen.

## 2026-08-10 - SEC PIT lifecycle metadata lane v0_1

- Added a dedicated source-selection role for 8-A*, 25/25-NSE and
  8-K Item 3.01.
- Executed sec_pit_7t_lifecycle_v0_1 against SEC metadata and governed
  G:/TSIS/data/reference/all_tickers snapshots.
- Classified 52 candidates: 14 registration, 2 Form 25 and 36 Item 3.01.
- Passed six security classes and correctly halted CNOBP as the preferred-class
  negative control.
- Preserved all events as unresolved pending primary-document extraction and
  market-presence reconciliation.
- Kept broad physical replay and canonical promotion unauthorized.

## 2026-08-10 - SEC PIT lifecycle primary acquisition v0_1

- Added a lifecycle-only SEC primary-document runner with immutable manifests,
  heartbeat, content-addressed storage, free-space gate and URL-level resume.
- Downloaded exactly 50 admitted primary documents across six cases.
- Excluded CNOBP before network acquisition under HALT_SECURITY_CLASS.
- Acquired 1,300,708 uncompressed response bytes with zero failures.
- Passed byte-level SHA-256, size, object-readability, parity, duplicate and SEC
  error-page checks.
- Confirmed zero complete submissions and zero exhibits.
- Full explicit SEC PIT suite reached 80/80 PASS.
- Kept extraction, lifecycle resolution, market reconciliation and canonical
  promotion unauthorized.

## 2026-08-10 - SEC PIT lifecycle extraction and market reconciliation v0_2

- Materialized 50 neutral lifecycle source observations and 44 security/class/
  exchange mentions from the acquired primary documents.
- First-output audit rejected v0_1 because the Item 3.01 heading inflated event
  labels and BBBY ticker reuse contaminated the target identity interval.
- Rebuilt the metadata gate by share-class FIGI with CIK fallback.
- Correctly moved BBBY 2023 Overstock filings to pre-target-identity evidence.
- Located 36/36 Item 3.01 sections without promoting filing dates to events.
- Reconciled six daily market-presence bounds and four tape bounds from G:.
- Preserved missing tape for ALUR/DOMH and boundary differences for BNAI/PGAC.
- Populated zero legal list/delist dates and zero first/last trade authority
  fields.
- Added non-destructive supersession sidecars for three rejected v0_1 runs.
- Full explicit SEC PIT suite reached 90/90 PASS.
## 2026-08-10 - Massive/SEC lifecycle reconciliation contract and target filing review

- Preserved the Massive/Polygon provenance of existing ticker windows.
- Added `MASSIVE_SEC_LIFECYCLE_WINDOW_RECONCILIATION_CONTRACT_v0_1.md`.
- Reviewed 12/12 target-interval lifecycle filings and materialized `sec_pit_7t_target_interval_filing_review_v0_1`.
- Classified ten filings with no boundary authority, one observed exchange trading-end candidate and one scheduled candidate.
- Admitted zero legal list dates and zero legal delist dates; parent-universe scale remains unauthorized.
- Materialized `sec_pit_6i_lifecycle_window_reconciliation_v0_1` for six pilot identities.
- Preserved vendor, SEC and market-presence dates as separate authorities.
- Found two exact vendor/daily starts, one BBBY ticker-reuse conflict, one ALUR SEC exchange-end candidate and two non-comparable source-date cases.