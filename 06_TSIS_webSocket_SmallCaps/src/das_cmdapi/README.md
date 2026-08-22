# das_cmdapi

Status: v0 terminal app for DAS/Sage CMD API read-only live capture.

This package opens a DAS CMD API socket from a terminal command, asks for credentials in the terminal, runs the governed initial screener, prints the filter process live in the terminal, and then asks whether to start full data capture for PASS candidates.

The app writes under `E:/TSIS/data_DAS_live`:

- `raw_cmdapi/runs/<run_id>/pre_manifest.json`
- `raw_cmdapi/runs/<run_id>/heartbeat.json`
- `raw_cmdapi/runs/<run_id>/command_transcript.jsonl`
- `raw_cmdapi/runs/<run_id>/events.jsonl`
- `raw_cmdapi/runs/<run_id>/candidate_registry.jsonl`
- `raw_cmdapi/runs/<run_id>/subscription_state.json`
- `raw_cmdapi/runs/<run_id>/final_summary.json`
- `screener/runs/<run_id>/screener_manifest.json`
- `screener/runs/<run_id>/candidates.jsonl`
- `screener/runs/<run_id>/candidates.csv`

Normal command from PowerShell:

```powershell
$env:PYTHONPATH = "C:\TSIS_Data\04_TSIS_webSocket_SmallCaps\src"
python -m das_cmdapi.capture --config "C:\TSIS_Data\04_TSIS_webSocket_SmallCaps\configs\das_cmdapi_capture_v0_1.example.json"
```

Flow:

1. Prompts for DAS username, password, and account.
2. Sends `LOGIN` through the socket; the command is redacted in transcript.
3. Sends read-only session setup commands.
4. Captures TOPLIST/Lv1 evidence and applies the initial denominator:
   market cap `< 100,000,000`, price `0.50..20.00`, volume `>= 300,000`, sessions `premarket`, `regular_market`, `afterhours`.
5. Evaluates at most `100` screener symbols by contract and prints each PASS/FAIL decision with price, volume, market cap, session and failure reasons.
6. Writes screener outputs.
7. Asks whether to download full data for PASS candidates.
8. If accepted, subscribes PASS candidates to configured live channels and prints subscription/stream heartbeat lines until `Ctrl+C` unless `capture_seconds` is configured.
9. On close, unsubscribes, sends `QUIT`, and writes `final_summary.json`.

Dry-run command:

```powershell
$env:PYTHONPATH = "C:\TSIS_Data\04_TSIS_webSocket_SmallCaps\src"
python -m das_cmdapi.capture --dry-run --config "C:\TSIS_Data\04_TSIS_webSocket_SmallCaps\configs\das_cmdapi_capture_v0_1.example.json"
```

Monitor command:

```powershell
$env:PYTHONPATH = "C:\TSIS_Data\04_TSIS_webSocket_SmallCaps\src"
python -m das_cmdapi.monitor "E:\TSIS\data_DAS_live\raw_cmdapi\runs\<run_id>"
```

For a bounded test after accepting download, add for example `--capture-seconds 300`.

Do not use this package for order entry, cancels, replaces, complex orders or locate actions.