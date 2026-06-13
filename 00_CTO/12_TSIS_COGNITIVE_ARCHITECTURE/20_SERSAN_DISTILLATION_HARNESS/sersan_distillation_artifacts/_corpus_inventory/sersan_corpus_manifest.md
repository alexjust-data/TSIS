# Sersan Corpus Manifest

Generated at UTC: `2026-06-11T19:49:50Z`
Contract: `sersan_lesson_pack_contract_v0_1`
Corpus root: `C:\TSIS_Data\00_CTO\99_REFERENCE_LIBRARY\SersanSistemas`
Artifact root: `C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\20_SERSAN_DISTILLATION_HARNESS\sersan_distillation_artifacts`

## Summary

| Metric | Value |
|---|---:|
| lesson packs | 17 |
| assets_resolved lesson packs | 16 |
| inventory_only lesson packs | 1 |
| image references | 2108 |
| unresolved local image references | 0 |
| external image references | 1 |
| code artifacts | 183 |
| xlsx artifacts | 11 |
| pdf files | 101 |

## Interpretation

This is an inventory artifact, not a full distillation.

The generated per-lesson manifests satisfy the `lesson_pack_manifest.json`
contract and set the starting state for future Sersan Distillation Harness
agents. Sectionization, image reading, mechanical rule extraction and TSIS
translation are intentionally left at zero until the pilot phase.

## Lesson Packs

| lesson_id | status | source_md | images | missing | code | xlsx | pdf |
|---|---|---|---:|---:|---:|---:|---:|
| `sersan_practice_02_donchain` | `assets_resolved` | `03_only_md_revised/practica_02_donchain.md` | 60 | 0 | 4 | 0 | 3 |
| `sersan_practice_03_donchain` | `assets_resolved` | `03_only_md_revised/practica_03_donchain.md` | 97 | 0 | 8 | 0 | 4 |
| `sersan_practice_04_donchain` | `assets_resolved` | `03_only_md_revised/practica_04_donchain.md` | 196 | 0 | 2 | 0 | 1 |
| `sersan_practice_05_donchain` | `assets_resolved` | `03_only_md_revised/practica_05_donchain.md` | 119 | 0 | 3 | 1 | 1 |
| `sersan_practice_06_orb` | `assets_resolved` | `03_only_md_revised/practica_06_ORB.md` | 76 | 0 | 6 | 0 | 9 |
| `sersan_practice_07_orb` | `assets_resolved` | `03_only_md_revised/practica_07_ORB.md` | 86 | 0 | 6 | 0 | 10 |
| `sersan_practice_08_orb` | `assets_resolved` | `03_only_md_revised/practica_08_ORB.md` | 95 | 0 | 12 | 0 | 12 |
| `sersan_practice_09_revision_apolo` | `assets_resolved` | `03_only_md_revised/practica_09_revision_apolo.md` | 171 | 0 | 1 | 1 | 1 |
| `sersan_practice_10_bollinger_bands` | `assets_resolved` | `03_only_md_revised/practica_10_bollinger_bands.md` | 176 | 0 | 13 | 0 | 6 |
| `sersan_practice_11_bollinger_aberration` | `assets_resolved` | `03_only_md_revised/practica_11_bollinger_Aberration.md` | 66 | 0 | 9 | 0 | 6 |
| `sersan_practice_12_revised` | `assets_resolved` | `03_only_md_revised/practica_12_revised.md` | 175 | 0 | 8 | 2 | 1 |
| `sersan_practice_13_revised` | `assets_resolved` | `03_only_md_revised/practica_13_revised.md` | 184 | 0 | 87 | 5 | 24 |
| `sersan_practice_14_revised` | `assets_resolved` | `03_only_md_revised/practica_14_revised.md` | 144 | 0 | 7 | 0 | 2 |
| `sersan_practice_15_revised` | `assets_resolved` | `03_only_md_revised/practica_15_revised.md` | 206 | 0 | 4 | 0 | 1 |
| `sersan_practice_16_revised` | `assets_resolved` | `03_only_md_revised/practica_16_revised.md` | 91 | 0 | 2 | 0 | 10 |
| `sersan_practice_17_revised` | `assets_resolved` | `03_only_md_revised/practica_17_revised.md` | 166 | 0 | 11 | 2 | 10 |
| `sersan_unmapped_xxx_revised` | `inventory_only` | `03_only_md_revised/xxx_revised.md` | 0 | 0 | 0 | 0 | 0 |

## Known Issues

- `sersan_unmapped_xxx_revised`: no practice number detected; lesson is unmapped

## Next Step

Run the three-lesson pilot required by the contract:

1. `sersan_practice_02_donchain`
2. `sersan_practice_09_revision_apolo`
3. `sersan_practice_15_revised`
