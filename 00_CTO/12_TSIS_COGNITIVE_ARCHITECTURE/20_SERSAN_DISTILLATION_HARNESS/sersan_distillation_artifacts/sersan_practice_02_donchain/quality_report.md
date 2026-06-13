# Quality Report: sersan_practice_02_donchain

## 1. Summary

| Metric | Value |
|---|---:|
| lesson_id | sersan_practice_02_donchain |
| status | translated |
| md_lines | 1154 |
| sections | 13 |
| image_refs_total | 60 |
| images_resolved | 60 |
| images_missing | 0 |
| images_read | 12 |
| rules_extracted | 13 |
| translations_created | 13 |
| open_questions | 7 |
| blocking_issues | 0 |

## 2. Input Coverage

The complete markdown was sectionized from line 1 to line 1154. The source
code artifact is referenced but not analyzed in this pilot. PDFs are duplicate
layout artifacts and remain out of scope per protocol.

## 3. Asset Resolution

All 60 image references resolve to local files under
`02_workshops/12-practice-02/img`. The duplicated reference to `055.png` is
kept as a separate indexed reference for traceability.

## 4. Sectionization Quality

The source has few markdown headings, so the pilot uses semantic line ranges
inside long sections. Ranges are non-overlapping and cover the whole file.

## 5. Image Reading Quality

All images are indexed. Images with `medium`, `high` or `critical` relevance
have notes in `image_evidence_notes/`. Low-relevance images are structurally
indexed but not promoted as doctrinal evidence.

## 6. Mechanical Rule Quality

All rules in `mechanical_rules.yaml` include trigger, action, failure mode and
source anchors. No rule is marked `promoted`.

## 7. TSIS Translation Quality

Each rule has one translation candidate in `tsis_translation_map.csv`. Critical
gates require human review.

## 8. Open Questions

Seven open questions are tracked in `open_questions.md`, mainly around filter
thresholds, small-cap translation, benchmark policy and image OCR.

## 9. Blocking Issues

None.

## 10. Acceptance Decision

`pass_with_warnings`

Warnings:

- This is the first pilot and should be human-reviewed before the contract is
  reused at scale.
- Code artifacts are inventoried but not parsed.
- Low-relevance images are not individually OCR-read.
