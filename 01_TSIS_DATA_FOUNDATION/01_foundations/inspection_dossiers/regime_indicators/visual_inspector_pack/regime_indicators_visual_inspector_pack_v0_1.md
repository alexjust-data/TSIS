# Regime Indicators Visual Inspector Pack v0.1

Fecha: 2026-06-20
Estado: `visual_complete_v0_1`

## 1. Verdict

This pack closes the missing visual evidence layer for:

```text
regime_indicators_v0_1
```

The correct institutional state is:

```text
data_quality_verdict = blocked_daily_scoped_minute_review
foundations_completion_status = human_inspector_ready
visual_inspection_status = visual_complete
```

Daily regime bars remain blocked. Minute bars remain review/scoped. Metadata is
useful for inspection and repair planning only.

## 2. Visual Asset Index

| Visual | State | Main question |
| --- | --- | --- |
| [Daily date collapse panel](images/regime_indicators_daily_date_collapse_panel_v0_1.png) | `blocking` | Is the daily defect isolated or structural? |
| [Daily file date heatmap](images/regime_indicators_daily_file_date_heatmap_v0_1.png) | `blocking` | Which daily files have invalid date keys? |
| [Minute high/low inversion panel](images/regime_indicators_minute_high_low_inversion_panel_v0_1.png) | `review` | Is the minute layer clean enough for production features? |
| [Minute coverage/readability map](images/regime_indicators_minute_coverage_readability_map_v0_1.png) | `scoped` | What part of the family is still usable for inspection? |
| [Metadata good examples](images/regime_indicators_metadata_good_examples_v0_1.png) | `scoped` | Can metadata make the broken daily files usable? |
| [Blocked vs scoped consumption panel](images/regime_indicators_blocked_vs_scoped_consumption_panel_v0_1.png) | `policy` | What may consume regime indicators right now? |

Machine-readable manifests:

- `regime_indicators_visual_case_manifest_v0_1.csv`
- `regime_indicators_visual_asset_audit_v0_1.csv`

Builder:

- `build_regime_indicators_visual_inspector_pack.py`

## 3. Daily Date Collapse Panel

Image:

```text
images/regime_indicators_daily_date_collapse_panel_v0_1.png
```

What it shows:

- 34 daily files are present and readable;
- all 34 daily files have only `1970-01-01` as `date`;
- affected daily rows total 153,397;
- sample ETF and index daily rows show real OHLC values attached to invalid
  calendar dates.

Responds:

```text
Is the daily defect isolated or structural?
```

Answer:

```text
Structural.
```

Consequence:

Daily ETF/index bars cannot be used as calendar-keyed regime features, master
daily table inputs, model features or live context until regenerated or repaired.

## 4. Daily File Date Heatmap

Image:

```text
images/regime_indicators_daily_file_date_heatmap_v0_1.png
```

What it shows:

- every daily file has `date_unique = 1`;
- every daily file is marked as 1970-only;
- `datetime` varies per row, but it is still clustered in 1970;
- rows and affected files are visible by `etfs/` and `indices/`.

Responds:

```text
Which daily files are affected by the invalid date key?
```

Answer:

```text
All inspected daily ETF and index files.
```

Consequence:

This is not a one-symbol exception. The daily layer is blocked as a whole.

## 5. Minute High/Low Inversion Panel

Image:

```text
images/regime_indicators_minute_high_low_inversion_panel_v0_1.png
```

What it shows:

- minute files have large readable row populations;
- scoped checks found no duplicate timestamp rows and no non-monotonic files;
- 204 `high < low` rows are present in `etfs/UVXY/minute.parquet`;
- sample UVXY rows show concrete OHLC violations.

Responds:

```text
Is the minute layer clean enough for production features?
```

Answer:

```text
No.
```

Consequence:

Minute bars may support source validation, forensic review and scoped research
inspection. They are not production feature inputs until OHLC sanity and broader
minute validation are complete.

## 6. Minute Coverage And Readability Map

Image:

```text
images/regime_indicators_minute_coverage_readability_map_v0_1.png
```

What it shows:

- minute timestamp ranges span real historical windows;
- 33 minute files are readable in scoped review;
- duplicate timestamp, non-monotonic and negative volume checks are clean in the
  scoped evidence;
- the 204 `high < low` rows remain visible as unresolved review debt.

Responds:

```text
What part of the family is still usable for inspection?
```

Answer:

```text
Minute files are useful for audit and repair planning, not production features.
```

Consequence:

Consumers must preserve the distinction:

```text
daily = blocked
minute = review/scoped
metadata = inspection context
```

## 7. Metadata Good Examples

Image:

```text
images/regime_indicators_metadata_good_examples_v0_1.png
```

What it shows:

- `download_metadata.json` is readable;
- `ticker_ranges.json` is readable and has 34 top-level symbol keys;
- metadata can explain scope/range but cannot repair broken daily dates.

Responds:

```text
Can metadata make the broken daily files usable?
```

Answer:

```text
No.
```

Consequence:

Metadata is a repair aid, not a substitute for valid `symbol + date` keys.

## 8. Blocked Vs Scoped Consumption Panel

Image:

```text
images/regime_indicators_blocked_vs_scoped_consumption_panel_v0_1.png
```

What it shows:

- audit/reporting, source validation and repair planning are allowed;
- minute research inspection is restricted;
- daily regime features, master daily table, backtest core, ML, RL and live
  candidates are blocked.

Responds:

```text
What may consume regime_indicators right now?
```

Answer:

```text
Only audit, validation, repair planning and scoped minute inspection.
```

Consequence:

No downstream system should treat `regime_indicators_v0_1` as a production
calendar-keyed regime source.

## 9. What This Pack Does Not Prove

This visual pack does not prove:

- that daily bars are repaired;
- that minute bars are fully clean;
- that metadata provides point-in-time safe features;
- that UVXY high/low inversions are harmless;
- that regime indicators can enter backtest, ML, RL or live systems.

It proves only:

```text
the blocked/scoped verdict is now visually inspectable and reproducible.
```

## 10. Closure

The regime indicators family now has the required visual inspection layer:

```text
population map: yes
coverage map: yes
quality-state distribution: yes
good/pass visual cases: yes, through minute and metadata scoped panels
flagged/review visual cases: yes, through minute high/low and coverage panels
bad/blocking visual cases: yes, through daily date collapse and file heatmap
manifest: yes
asset audit: yes
builder: yes
```

Final operational reading:

```text
human_inspector_ready, but daily_bars_blocked_minute_bars_review_only
```
