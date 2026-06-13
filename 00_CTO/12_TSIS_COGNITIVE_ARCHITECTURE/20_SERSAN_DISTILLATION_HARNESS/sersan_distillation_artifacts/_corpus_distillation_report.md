# Sersan Corpus-Level Distillation Report

Generated at UTC: `2026-06-12T15:20:07Z`
Readiness status: `pass_with_warnings`
Execution command: `python 00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/harness_toolchain/sersan_distillation/run_sersan_corpus_distillation.py --process-all`

## Summary

| Metric | Value |
|---|---:|
| lesson packs processed | 17 |
| pass | 0 |
| pass_with_warnings | 16 |
| blocked | 1 |
| fail | 0 |
| needs_human_review | 0 |
| mechanical rules extracted | 225 |
| TSIS maps created | 225 |
| images indexed | 2108 |
| images requiring human review | 2105 |

## Lesson Pack Results

| lesson_id | status | sections | images | rules | translations | blockers |
|---|---|---:|---:|---:|---:|---:|
| `sersan_practice_02_donchain` | `pass_with_warnings` | 12 | 60 | 11 | 11 | 0 |
| `sersan_practice_03_donchain` | `pass_with_warnings` | 31 | 97 | 31 | 31 | 0 |
| `sersan_practice_04_donchain` | `pass_with_warnings` | 24 | 196 | 23 | 23 | 0 |
| `sersan_practice_05_donchain` | `pass_with_warnings` | 14 | 119 | 13 | 13 | 0 |
| `sersan_practice_06_orb` | `pass_with_warnings` | 7 | 76 | 6 | 6 | 0 |
| `sersan_practice_07_orb` | `pass_with_warnings` | 11 | 86 | 10 | 10 | 0 |
| `sersan_practice_08_orb` | `pass_with_warnings` | 18 | 95 | 17 | 17 | 0 |
| `sersan_practice_09_revision_apolo` | `pass_with_warnings` | 25 | 171 | 24 | 24 | 0 |
| `sersan_practice_10_bollinger_bands` | `pass_with_warnings` | 10 | 176 | 9 | 9 | 0 |
| `sersan_practice_11_bollinger_aberration` | `pass_with_warnings` | 12 | 66 | 12 | 12 | 0 |
| `sersan_practice_12_revised` | `pass_with_warnings` | 7 | 175 | 7 | 7 | 0 |
| `sersan_practice_13_revised` | `pass_with_warnings` | 16 | 184 | 14 | 14 | 0 |
| `sersan_practice_14_revised` | `pass_with_warnings` | 17 | 144 | 17 | 17 | 0 |
| `sersan_practice_15_revised` | `pass_with_warnings` | 7 | 206 | 7 | 7 | 0 |
| `sersan_practice_16_revised` | `pass_with_warnings` | 19 | 91 | 19 | 19 | 0 |
| `sersan_practice_17_revised` | `pass_with_warnings` | 6 | 166 | 5 | 5 | 0 |
| `sersan_unmapped_xxx_revised` | `blocked` | 1 | 0 | 0 | 0 | 1 |

## Repeated Warnings

- Automated numeric OCR not implemented.
- Code artifacts inventoried but not semantically parsed.
- XLSX artifacts inventoried but not semantically parsed.
- High-impact image evidence requires human review before doctrine promotion.

## Contract Debt

- Human visual review/OCR remains required for images carrying parameter, risk, optimization or execution evidence.
- Code and XLSX semantic parsing remain pending.
- Sersan outputs are mechanical-rule candidates only; no doctrine is promoted by this run.
- The inventory_only lesson sersan_unmapped_xxx_revised remains blocked until mapped or explicitly reclassified.

## Promotion Recommendation

Do not promote to canonical TSIS doctrine yet. Proceed to human doctrine review and domain consolidation after validating high-impact image evidence.
