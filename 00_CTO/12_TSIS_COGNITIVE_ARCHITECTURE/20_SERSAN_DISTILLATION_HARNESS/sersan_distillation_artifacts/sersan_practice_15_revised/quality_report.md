# Quality Report: sersan_practice_15_revised

## 1. Summary

| Metric | Value |
|---|---:|
| lesson_id | sersan_practice_15_revised |
| status | translated |
| md_lines | 3175 |
| sections | 20 |
| image_refs_total | 206 |
| images_resolved | 206 |
| images_resolved_lesson_fallback | 206 |
| images_missing | 0 |
| images_read | 66 |
| code_artifacts | 4 |
| rules_extracted | 23 |
| translations_created | 23 |
| open_questions | 8 |
| blocking_issues | 0 |

## 2. Input Coverage

The complete markdown was sectionized from line 1 to line 3175. The
four EasyLanguage/TradeStation code artifacts are inventoried as associated
artifacts. PDFs are duplicate layout artifacts and subtitles/video are out of
scope per project instruction.

## 3. Asset Resolution

All 206 image references resolve to local files under
`02_workshops/25-practice-15/img`. The source markdown uses `../img/...`
references, so all local assets are recorded as `resolved_lesson_fallback`.
The resolver URL-decodes refs such as `008%20-%20copia.png` before matching the
local file.

## 4. Sectionization Quality

The source has a small number of formal headings and long teaching segments.
This pilot uses semantic line ranges that are non-overlapping and cover the
whole file.

## 5. Image Reading Quality

All images are indexed. Images with `medium`, `high` or `critical` doctrine
relevance have notes in `image_evidence_notes/`. Low-relevance images are
structurally indexed but not individually OCR-read.

## 6. Mechanical Rule Quality

All rules in `mechanical_rules.yaml` include trigger, action, failure mode and
source anchors. No rule is marked `promoted`.

## 7. TSIS Translation Quality

Each rule has one translation candidate in `tsis_translation_map.csv`. Critical
and high-priority gates require human review before implementation.

## 8. Open Questions

Eight open questions are tracked in `open_questions.md`, mainly around
drawdown bands, volatility floors, risk conversion, costs/borrow, method
comparison and AlphaEvolve stress tests.

## 9. Blocking Issues

None.

## 10. Acceptance Decision

`pass_with_warnings`

Warnings:

- Code artifacts are inventoried but not compiled or semantically parsed.
- Low-relevance images are not individually OCR-read.
- Money-management rules are candidate doctrine until human review.
- Numeric examples come from the course context and should not be promoted as
  universal TSIS constants.
