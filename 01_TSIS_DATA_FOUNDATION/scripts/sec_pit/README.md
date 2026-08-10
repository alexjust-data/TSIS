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
