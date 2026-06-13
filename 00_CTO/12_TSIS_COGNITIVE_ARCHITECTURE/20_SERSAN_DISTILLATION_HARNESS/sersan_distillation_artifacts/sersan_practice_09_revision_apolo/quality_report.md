# Quality Report: sersan_practice_09_revision_apolo

## 1. Summary

| Metric | Value |
|---|---:|
| lesson_id | sersan_practice_09_revision_apolo |
| status | translated |
| md_lines | 2400 |
| sections | 16 |
| image_refs_total | 171 |
| images_resolved | 171 |
| images_missing | 0 |
| images_read | 26 |
| rules_extracted | 18 |
| translations_created | 18 |
| open_questions | 8 |
| blocking_issues | 0 |

## 2. Input Coverage

The complete markdown was sectionized from line 1 to line 2400. The
EasyLanguage artifact and XLSX map are inventoried as associated artifacts but
are not parsed deeply in this pilot. PDFs remain duplicate layout artifacts and
subtitles/video are out of scope per project instruction.

## 3. Asset Resolution

All 171 image references resolve to local files under
`02_workshops/19-practice-09/img`. Duplicated references are preserved as
separate indexed references for traceability.

## 4. Sectionization Quality

The source has meaningful headings but several long teaching segments. The
pilot uses semantic line ranges that are non-overlapping and cover the whole
file.

## 5. Image Reading Quality

All images are indexed. Images with `medium`, `high` or `critical` relevance
have notes in `image_evidence_notes/`. Low-relevance images are structurally
indexed but not individually OCR-read.

## 6. Mechanical Rule Quality

All rules in `mechanical_rules.yaml` include trigger, action, failure mode and
source anchors. No rule is marked `promoted`.

## 7. TSIS Translation Quality

Each rule has one translation candidate in `tsis_translation_map.csv`. Critical
and high-priority gates require human review before implementation.

## 8. Open Questions

Eight open questions are tracked in `open_questions.md`, mainly around
increment thresholds, filter significance, candidate-count scaling, portfolio
selection and validation alternatives.

## 9. Blocking Issues

None.

## 10. Acceptance Decision

`pass_with_warnings`

Warnings:

- The XLSX map is inventoried but not parsed into structured surfaces.
- Low-relevance images are not individually OCR-read.
- Short-equity live translation needs borrow, liquidity, halts and small-cap
  execution constraints before operational use.
- Candidate rules require human doctrine review before promotion.
