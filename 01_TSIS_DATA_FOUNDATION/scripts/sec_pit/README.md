# SEC PIT Pipeline v0_1

Implements the one-ticker execution authorized by
`SEC_PIT_FUNDAMENTAL_ACQUISITION_AND_RESOLUTION_CONTRACT_v0_1.md`.

## Plan only

```powershell
python scripts\sec_pit\run_one_ticker_pilot.py --ticker BNAI --run-id sec_pit_bnai_plan
```

## Execute

Set a truthful SEC contact header first:

```powershell
$env:SEC_USER_AGENT = "TSIS Research contact@example.com"
python scripts\sec_pit\run_one_ticker_pilot.py --ticker BNAI --execute --max-primary-documents 300 --run-id sec_pit_bnai_v0_1
```

The command prints its monitor command before acquisition. Complete submissions
and exhibits are not downloaded by default.

## Current boundary

The runner resolves G7 owner-exclusion float only for sessions covered by a
complete causal ownership baseline and before any unapplied later ownership
event. Earlier and later unsupported sessions remain NULL with explicit states.
G8 writes neutral registration component, selling-holder lot and component-condition
ledgers. EFFECT is treated only as registration-effectiveness evidence; it never
authorizes tradable supply. Tradability remains blocked until issuance/O/S,
lockup, legend, resale-condition and methodology gates pass. The governed BNAI
pilot requires `--max-primary-documents 300`; smaller caps are diagnostic only.
Global 13F and EV remain gated.

## Full-universe descending acquisition preparation

The governed 4,824-row preflight uses:

```powershell
python scripts\sec_pit\build_4824_descending_acquisition_preflight.py --config configs\sec_pit_4824_descending_acquisition_preflight_v0_1.json --output <new-versioned-runtime-root>
```

It performs no network requests. It freezes five cohorts of
`824/1000/1000/1000/1000` ordered by `last_observed_date DESC, ticker ASC`,
preserves ticker aliases explicitly, assigns the governed four-shard function
and emits launch/monitor/resume commands. The current PASS root is documented in
the SEC PIT inspection dossier.

`run_submissions_metadata_profile.py` is the first long-run lane. It is
metadata-only, supports `--resume`, rejects input/object-root drift and live
duplicate writers, prints the required control header and reuses the existing
content-addressed store. Metadata completion never authorizes primary documents.

The only active object root is
`D:/TSIS/fundamental_context/sec_pit_v0_1/objects`.
`D:/sec_float_pit_v0_1` is immutable pilot provenance and the metadata runner
rejects it as a destination before network access.

After one cohort reaches metadata `COMPLETE`,
`build_4824_cohort_metadata_gate.py` produces the network-free selection,
identity/lifecycle review, request-quality and storage-projection readout. It
uses `sec_pit_predownload_control_v0_2`, reports filing-size upper bounds and
keeps primary acquisition explicitly unauthorized.

The later authorized-primary runner uses a `200 GiB` minimum-free-space gate at
start and before each document. Low disk persists `STOPPED_LOW_DISK`, terminal
manifests and exact resume instructions.

## Active C01 primary tranche

The only active governed primary scope as of `2026-08-14` is
`C01-T01-0250`: the exact first 250 eligible rows and 127,946 documents bound to
the v0.2 probe, selection-plan and gate-matrix hashes. Its run root is:

```text
D:/TSIS/fundamental_context/sec_pit_v0_1/runs/sec_pit_c01_primary_t01_0250_v0_1_20260814
```

Monitor:

```powershell
& "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\monitor_authorized_primary_acquisition_v0_2.ps1" -RunRoot "D:\TSIS\fundamental_context\sec_pit_v0_1\runs\sec_pit_c01_primary_t01_0250_v0_1_20260814" -AuthorizationPath "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\sec_pit_primary_download_authorization_c01_t01_0250_v0_1_20260814.json" -IntervalSeconds 10 -Compact -Watch
```

The monitor treats `COMPLETE`, `FAILED`, `STOPPED_LOW_DISK` and `INTERRUPTED`
as terminal. Recovery reruns the exact acquisition command with `--resume`;
hash drift and a concurrent writer fail closed. No remaining C01 row or later
cohort is implicitly admitted. Supplying the authorization path adds exact
`ticker_ordinal`, `tickers_completed` and `tickers_remaining` fields against
the authorized 250-row scope.
