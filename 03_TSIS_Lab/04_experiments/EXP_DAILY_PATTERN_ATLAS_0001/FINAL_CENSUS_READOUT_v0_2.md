# Final Census Readout v0.2

- status: `pass`
- mode: `full`
- terminal certification: `pass`
- independent audit: `pass`
- operational closure: `pass`
- final root: `C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAILY_PATTERN_ATLAS_0001\runs\20260825_full_v0_1\final`
- sessions: 9,290,966
- tickers: 4,824
- dates: 2005-01-03 to 2026-03-06
- activation labels: 9,728,326
- episodes: 422,042
- trajectory rows: 8,817,239
- event rows: 2,529,142

This is an exploratory descriptive census. It contains no inference,
trading signal, execution rule or PnL claim.

## Episode observation

- tickers represented: 4,824
- complete D0-D20 horizons: 98.9518% observed share
- right-censored horizons: 1.0482% observed share
- median observed sessions: 21

## Activation-label census

| family | label | rows | tickers |
|---|---|---:|---:|
| resistance_breakout | high_breakout_previous_day | 4,055,449 | 4,824 |
| resistance_breakout | high_breakout_previous_week | 1,831,385 | 4,824 |
| relative_volume | relative_volume_ge_3x | 884,206 | 4,821 |
| resistance_breakout | high_breakout_previous_month | 809,298 | 4,817 |
| relative_volume | relative_volume_ge_5x | 447,894 | 4,813 |
| resistance_breakout | high_breakout_previous_quarter | 415,818 | 4,732 |
| resistance_breakout | high_breakout_previous_half_year | 272,396 | 4,562 |
| range | range_ge_20pct | 207,126 | 4,171 |
| relative_volume | relative_volume_ge_10x | 198,052 | 4,771 |
| resistance_breakout | high_breakout_previous_year | 170,615 | 4,030 |
| relative_volume | relative_volume_ge_20x | 96,782 | 4,552 |
| range | range_ge_30pct | 76,009 | 3,737 |
| gap | gap_ge_10pct | 69,758 | 4,064 |
| close_advance | close_advance_ge_20pct | 52,366 | 3,911 |
| range | range_ge_50pct | 26,046 | 2,931 |
| close_advance | close_advance_ge_30pct | 24,820 | 3,401 |
| gap | gap_ge_20pct | 22,451 | 3,338 |
| gap | gap_ge_30pct | 13,488 | 2,765 |
| close_advance | close_advance_ge_50pct | 11,393 | 2,639 |
| range | range_ge_100pct | 8,553 | 2,019 |
| gap | gap_ge_50pct | 8,129 | 2,283 |
| gap | gap_ge_75pct | 5,824 | 1,998 |
| close_advance | close_advance_ge_100pct | 5,743 | 1,993 |
| gap | gap_ge_100pct | 4,827 | 1,836 |
| gap | gap_ge_150pct | 3,760 | 1,671 |
| gap | gap_ge_200pct | 3,265 | 1,579 |
| gap | gap_ge_300pct | 2,873 | 1,495 |

## Event census

| event | rows | episodes |
|---|---:|---:|
| horizon_peak | 422,042 | 422,042 |
| first_day_without_new_episode_high | 421,715 | 421,715 |
| first_lower_close | 421,627 | 421,627 |
| first_lower_high | 421,603 | 421,603 |
| first_red_candle | 421,197 | 421,197 |
| first_red_candle_after_d0 | 420,958 | 420,958 |

## Coverage by year

| year | rows | tickers | min date | max date |
|---:|---:|---:|---|---|
| 2005 | 243,274 | 1,094 | 2005-01-03 | 2005-12-30 |
| 2006 | 254,598 | 1,136 | 2006-01-03 | 2006-12-29 |
| 2007 | 269,667 | 1,222 | 2007-01-03 | 2007-12-31 |
| 2008 | 282,375 | 1,238 | 2008-01-02 | 2008-12-31 |
| 2009 | 282,576 | 1,243 | 2009-01-02 | 2009-12-31 |
| 2010 | 293,564 | 1,290 | 2010-01-04 | 2010-12-31 |
| 2011 | 305,804 | 1,329 | 2011-01-03 | 2011-12-30 |
| 2012 | 311,692 | 1,374 | 2012-01-03 | 2012-12-31 |
| 2013 | 332,784 | 1,454 | 2013-01-02 | 2013-12-31 |
| 2014 | 368,800 | 1,621 | 2014-01-02 | 2014-12-31 |
| 2015 | 400,389 | 1,746 | 2015-01-02 | 2015-12-31 |
| 2016 | 419,375 | 1,825 | 2016-01-04 | 2016-12-30 |
| 2017 | 441,490 | 1,971 | 2017-01-03 | 2017-12-29 |
| 2018 | 472,628 | 2,111 | 2018-01-02 | 2018-12-31 |
| 2019 | 499,505 | 2,227 | 2019-01-02 | 2019-12-31 |
| 2020 | 525,238 | 2,437 | 2020-01-02 | 2020-12-31 |
| 2021 | 646,453 | 3,297 | 2021-01-04 | 2021-12-31 |
| 2022 | 752,357 | 3,466 | 2022-01-03 | 2022-12-30 |
| 2023 | 710,918 | 3,371 | 2023-01-03 | 2023-12-29 |
| 2024 | 690,135 | 3,183 | 2024-01-02 | 2024-12-31 |
| 2025 | 672,307 | 3,042 | 2025-01-02 | 2025-12-31 |
| 2026 | 115,037 | 2,746 | 2026-01-02 | 2026-03-06 |

## Selected daily cohorts

All values below are observed descriptive summaries relative to D0.

| label | offset | obs. | activation cases | tickers | mean close | median close | P10 | P90 | red-candle share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gap_ge_30pct | D+0 | 13,488 | 13,488 | 2,765 | 0.00% | 0.00% | 0.00% | 0.00% | 62.42% |
| gap_ge_30pct | D+1 | 13,410 | 13,410 | 2,758 | 21.05% | -3.36% | -27.86% | 17.65% | 50.82% |
| gap_ge_30pct | D+3 | 13,340 | 13,340 | 2,749 | 48.61% | -6.95% | -38.86% | 25.00% | 48.96% |
| gap_ge_30pct | D+5 | 13,250 | 13,250 | 2,739 | 298.40% | -8.42% | -43.33% | 32.14% | 48.32% |
| gap_ge_30pct | D+10 | 13,101 | 13,101 | 2,727 | 515.16% | -11.54% | -50.32% | 43.34% | 48.40% |
| gap_ge_30pct | D+20 | 12,840 | 12,840 | 2,698 | 1417.83% | -15.27% | -60.00% | 63.78% | 46.56% |
| gap_ge_50pct | D+0 | 8,129 | 8,129 | 2,283 | 0.00% | 0.00% | 0.00% | 0.00% | 58.96% |
| gap_ge_50pct | D+1 | 8,067 | 8,067 | 2,279 | 29.44% | -3.72% | -33.33% | 19.23% | 49.75% |
| gap_ge_50pct | D+3 | 8,027 | 8,027 | 2,274 | 72.16% | -7.84% | -45.32% | 25.08% | 47.35% |
| gap_ge_50pct | D+5 | 7,965 | 7,965 | 2,270 | 472.75% | -9.46% | -50.00% | 33.33% | 46.74% |
| gap_ge_50pct | D+10 | 7,864 | 7,864 | 2,259 | 807.65% | -14.00% | -56.96% | 45.44% | 46.81% |
| gap_ge_50pct | D+20 | 7,684 | 7,684 | 2,240 | 2045.32% | -18.18% | -65.61% | 64.85% | 45.48% |
| high_breakout_previous_day | D+0 | 4,055,449 | 4,055,449 | 4,824 | 0.00% | 0.00% | 0.00% | 0.00% | 33.65% |
| high_breakout_previous_day | D+1 | 4,053,760 | 4,053,760 | 4,824 | 0.56% | -0.00% | -4.19% | 4.00% | 49.23% |
| high_breakout_previous_day | D+3 | 4,049,333 | 4,049,333 | 4,824 | 1.45% | -0.12% | -7.20% | 6.86% | 48.86% |
| high_breakout_previous_day | D+5 | 4,045,716 | 4,045,716 | 4,824 | 2.33% | -0.20% | -9.42% | 8.84% | 48.94% |
| high_breakout_previous_day | D+10 | 4,035,609 | 4,035,609 | 4,824 | 4.59% | -0.31% | -13.51% | 12.69% | 48.79% |
| high_breakout_previous_day | D+20 | 4,015,198 | 4,015,198 | 4,824 | 8.74% | -0.54% | -19.53% | 18.49% | 48.64% |
| high_breakout_previous_month | D+0 | 809,298 | 809,298 | 4,817 | 0.00% | 0.00% | 0.00% | 0.00% | 27.49% |
| high_breakout_previous_month | D+1 | 808,848 | 808,848 | 4,817 | 0.19% | 0.00% | -4.47% | 4.17% | 49.81% |
| high_breakout_previous_month | D+3 | 807,910 | 807,910 | 4,814 | 0.56% | -0.12% | -7.63% | 6.85% | 49.02% |
| high_breakout_previous_month | D+5 | 807,028 | 807,028 | 4,813 | 0.85% | -0.20% | -9.79% | 8.69% | 48.92% |
| high_breakout_previous_month | D+10 | 805,060 | 805,060 | 4,812 | 1.66% | -0.31% | -13.66% | 12.26% | 48.76% |
| high_breakout_previous_month | D+20 | 801,131 | 801,131 | 4,812 | 3.74% | -0.62% | -19.23% | 17.51% | 48.73% |
| high_breakout_previous_week | D+0 | 1,831,385 | 1,831,385 | 4,824 | 0.00% | 0.00% | 0.00% | 0.00% | 29.07% |
| high_breakout_previous_week | D+1 | 1,830,549 | 1,830,549 | 4,824 | 0.53% | -0.02% | -4.34% | 4.13% | 49.65% |
| high_breakout_previous_week | D+3 | 1,828,653 | 1,828,653 | 4,824 | 1.19% | -0.16% | -7.40% | 6.88% | 49.13% |
| high_breakout_previous_week | D+5 | 1,826,941 | 1,826,941 | 4,824 | 1.80% | -0.26% | -9.58% | 8.76% | 49.02% |
| high_breakout_previous_week | D+10 | 1,822,298 | 1,822,298 | 4,824 | 3.21% | -0.37% | -13.57% | 12.54% | 48.86% |
| high_breakout_previous_week | D+20 | 1,813,861 | 1,813,861 | 4,824 | 7.04% | -0.61% | -19.36% | 18.12% | 48.73% |

## Tail-shape caution

Gap cohorts contain extreme right tails. Means can be orders of magnitude above medians;
therefore the readout presents both and no single central statistic should be treated as
a complete description of the observed distribution.

## Direct event timing

Offsets use the kth available ticker observation; they are not calendar days.

| label | event | cases | observed | median | P25 | P75 | P90 |
|---|---|---:|---:|---:|---:|---:|---:|
| gap_ge_30pct | first_day_without_new_episode_high | 13,488 | 13,431 | D+1 | D+1 | D+1 | D+2 |
| gap_ge_30pct | first_lower_close | 13,488 | 13,354 | D+1 | D+1 | D+2 | D+3 |
| gap_ge_30pct | first_lower_high | 13,488 | 13,398 | D+1 | D+1 | D+1 | D+2 |
| gap_ge_30pct | first_red_candle | 13,488 | 13,062 | D+0 | D+0 | D+1 | D+3 |
| gap_ge_30pct | first_red_candle_after_d0 | 13,488 | 12,936 | D+1 | D+1 | D+3 | D+5 |
| gap_ge_30pct | horizon_peak | 13,488 | 13,488 | D+0 | D+0 | D+8 | D+16 |
| gap_ge_50pct | first_day_without_new_episode_high | 8,129 | 8,093 | D+1 | D+1 | D+1 | D+2 |
| gap_ge_50pct | first_lower_close | 8,129 | 8,031 | D+1 | D+1 | D+2 | D+3 |
| gap_ge_50pct | first_lower_high | 8,129 | 8,063 | D+1 | D+1 | D+1 | D+2 |
| gap_ge_50pct | first_red_candle | 8,129 | 7,812 | D+0 | D+0 | D+1 | D+3 |
| gap_ge_50pct | first_red_candle_after_d0 | 8,129 | 7,721 | D+1 | D+1 | D+3 | D+5 |
| gap_ge_50pct | horizon_peak | 8,129 | 8,129 | D+1 | D+0 | D+7 | D+16 |
| high_breakout_previous_day | first_day_without_new_episode_high | 4,055,449 | 4,052,686 | D+1 | D+1 | D+2 | D+3 |
| high_breakout_previous_day | first_lower_close | 4,055,449 | 4,052,395 | D+1 | D+0 | D+2 | D+3 |
| high_breakout_previous_day | first_lower_high | 4,055,449 | 4,051,804 | D+1 | D+1 | D+2 | D+4 |
| high_breakout_previous_day | first_red_candle | 4,055,449 | 4,049,290 | D+1 | D+0 | D+2 | D+3 |
| high_breakout_previous_day | first_red_candle_after_d0 | 4,055,449 | 4,047,562 | D+2 | D+1 | D+3 | D+4 |
| high_breakout_previous_day | horizon_peak | 4,055,449 | 4,055,449 | D+8 | D+2 | D+16 | D+19 |
| high_breakout_previous_month | first_day_without_new_episode_high | 809,298 | 808,563 | D+1 | D+1 | D+2 | D+3 |
| high_breakout_previous_month | first_lower_close | 809,298 | 808,436 | D+1 | D+1 | D+2 | D+3 |
| high_breakout_previous_month | first_lower_high | 809,298 | 808,311 | D+1 | D+1 | D+2 | D+4 |
| high_breakout_previous_month | first_red_candle | 809,298 | 807,804 | D+1 | D+0 | D+2 | D+4 |
| high_breakout_previous_month | first_red_candle_after_d0 | 809,298 | 807,416 | D+2 | D+1 | D+3 | D+4 |
| high_breakout_previous_month | horizon_peak | 809,298 | 809,298 | D+7 | D+1 | D+16 | D+19 |
| high_breakout_previous_week | first_day_without_new_episode_high | 1,831,385 | 1,830,019 | D+1 | D+1 | D+2 | D+3 |
| high_breakout_previous_week | first_lower_close | 1,831,385 | 1,829,811 | D+1 | D+1 | D+2 | D+3 |
| high_breakout_previous_week | first_lower_high | 1,831,385 | 1,829,594 | D+1 | D+1 | D+2 | D+4 |
| high_breakout_previous_week | first_red_candle | 1,831,385 | 1,828,427 | D+1 | D+0 | D+2 | D+3 |
| high_breakout_previous_week | first_red_candle_after_d0 | 1,831,385 | 1,827,651 | D+2 | D+1 | D+3 | D+4 |
| high_breakout_previous_week | horizon_peak | 1,831,385 | 1,831,385 | D+8 | D+1 | D+16 | D+19 |

## Direct activations versus cooldown cycles

Primary cohorts contain all activations. Cooldown cycles are a separate secondary view.

| label | all activations | cooldown cycles | cooldown share |
|---|---:|---:|---:|
| gap_ge_30pct | 13,488 | 1,113 | 8.2518% |
| gap_ge_50pct | 8,129 | 698 | 8.5865% |
| high_breakout_previous_day | 4,055,449 | 388,896 | 9.5895% |
| high_breakout_previous_month | 809,298 | 50,252 | 6.2093% |
| high_breakout_previous_week | 1,831,385 | 120,529 | 6.5813% |
