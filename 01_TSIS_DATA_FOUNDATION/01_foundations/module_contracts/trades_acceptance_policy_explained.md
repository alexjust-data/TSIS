# `trades` Acceptance Policy Explained

## Purpose

This document explains the `trades` acceptance policy in plain but rigorous language.

The formal sources remain:

- `01_foundations/contract_registry/dataset_contracts/trades_dataset_contract_v0_1.md`
- `01_foundations/contract_registry/dataset_contracts/trades_label_taxonomy_and_cut_policy.md`
- `01_foundations/data_consumption_policies/trades_consumption_policy.md`

This document does not replace them.
It explains them.

Compact companion:

- `01_foundations/module_contracts/trades_rules_explained_line_by_line.md`

## Core Principle

`trades` is a tape of executions.

Each row is supposed to represent:

- a real executed event
- at a real timestamp
- at a real price
- for a real positive size

Because of that, the policy must distinguish between:

1. disagreement against arbiters
2. intrinsic corruption of the tape

Those are not the same thing.

## Final Operational States

Historically, `trades` closes into four operational states:

- `good`
- `recoverable_with_flag`
- `review_not_rehabilitated`
- `bad`

The file-level labels such as:

- `review`
- `reference_scale_mismatch`
- `review_microstructure`
- `review_no_1m_reference`
- `review_1m_reference_alignment`
- `bad_data`

help explain the path, but they are not the final operational meaning by themselves.

## What `good` really means

`good` means:

- clean enough to be used without material tape-level concern under a conservative policy

It does **not** mean:

- "all useful data"

That is why `good` is tiny in the final closeout.

Question it answers:

- "Which files can be treated as clean without caveat?"

Question it does **not** answer:

- "How much of `trades` is still economically useful?"

That second question is answered by rehabilitation.

## What `recoverable_with_flag` means

This state means:

- the file is not pristine
- but a conservative rule says it can still be used if the warning remains attached

It answers:

- "How much of the stressed review mass is still usable under explicit caution?"

It does **not** answer:

- "Is the file clean?"

No.
It means:

- not clean
- but still usable in controlled contexts

## What `review_not_rehabilitated` means

This state means:

- the file is not proved bad enough for hard exclusion
- but it also cannot be rehabilitated confidently

It answers:

- "Which files remain materially ambiguous after conservative recovery?"

## What `bad` means

`bad` is the true hard-negative tail.

It means:

- the file is best explained as intrinsically untrustworthy tape material
- not merely as a scale mismatch
- not merely as a microstructure corner
- not merely as a missing-reference problem

It answers:

- "Which files fail the tape itself strongly enough that downstream use is unsafe?"

## Why `size = 0` is not valid in `trades`

`size` in `trades` is executed quantity.

A real trade must exchange a positive quantity.

So a row with `size = 0` suggests one of these:

- technical artifact
- parse error
- corruption
- wrong semantic object inside the tape

This matters because it answers:

- "Does the row still behave like a real execution?"

It does **not** merely answer:

- "Does the price path look plausible?"

A file can look almost normal in price and still fail this basic semantic test.

## Why exact duplicates matter

Heavy exact duplication suggests:

- replayed rows
- duplicated ingestion
- mechanical bursts
- or structurally suspicious tape handling

This does not always destroy the price path visually.
But it weakens confidence that the file behaves like a clean stream of executions.

Question it answers:

- "Is the tape behaving like an execution stream or like a duplicated artifact stream?"

## Why `outside_daily_regular_pct` matters

This metric asks:

- what share of regular-session trades falls outside the daily `[low, high]` range?

It answers:

- "How much of the tape contradicts the daily arbiter?"

It does **not** answer by itself:

- "Is the tape intrinsically broken?"

Large disagreement can still come from:

- scale mismatch
- reference construction
- comparability problems

## Why `outside_1m_regular_pct` matters

This metric asks:

- what share of regular-session trades falls outside the minute-level range?

It answers:

- "Does the tape survive comparison against finer intraday structure?"

Again, this is powerful but not sufficient alone to prove intrinsic corruption.

## Why scale mismatch must stay separate

One of the major historical findings is that many stressed files disagree with arbiters because they live on an incompatible scale.

That answers:

- "Is the dominant problem comparability and scaling rather than tape corruption?"

Without this distinction, a reviewer would wrongly call many files `bad_data` when the tape may still be internally plausible.

## Why microstructure review must stay separate

Some files are stressed by:

- odd-lot concentration
- sparse prints
- tape texture
- non-benchmark-like print structure

This answers:

- "Is the disagreement better explained by tape texture and market microstructure than by intrinsic failure?"

Without this distinction, hard comparability would be confused with corruption.

## Why missing `1m` support must stay separate

`review_no_1m_reference` is fundamentally a coverage problem.

It answers:

- "Do we lack enough intraday reference support to decide cleanly?"

It does **not** mean:

- "The tape is bad."

## Why the policy must be explained image by image

A family name is not enough.
Metrics are not enough either.

Each visual case shown to an inspector must explain:

- what the image proves
- what it does not prove
- where the problem is visible
- whether the current panel is sufficient
- what decision changes because of what is seen

If the real cause is structural rather than geometric, then a price-only panel is insufficient.
In those cases, the dossier must add integrity evidence such as:

- `size <= 0`
- duplicate groups
- invalid-row examples

## Relation To The General Standard

The transversal rule that requires this explanatory layer lives in:

- `01_foundations/module_contracts/policy_explanation_standard.md`
