# `daily` Acceptance Policy Explained

## Purpose

This document explains the `daily` acceptance policy in plain but rigorous language.

The formal sources remain:

- `01_foundations/contract_registry/dataset_contracts/daily_dataset_contract_v0_1.md`
- `01_foundations/contract_registry/dataset_contracts/daily_label_taxonomy_and_cut_policy.md`
- `01_foundations/data_consumption_policies/daily_consumption_policy.md`

This document does not replace them.
It explains them.

## Core Principle

`daily` is not a microstructure tape.

It is a bar-based daily layer whose primary semantic authority lives in:

- parse integrity
- session date integrity
- `open / high / low / close`
- `volume`
- and coverage

`vw` is important, but it is a secondary diagnostic layer rather than the single truth of the dataset.

## Two Axes, Not One

`daily` cannot be read through a single axis.

It has:

1. a `quality` axis
2. a `coverage` axis

The final certification state comes from combining both.

This avoids a common mistake:

- confusing a visually simple `good / flagged / bad` split with the real operational semantics of the block.

## Quality States

The quality axis is:

- `good`
- `recoverable_with_flag`
- `bad`

### What `good` means

`good` means:

- the daily bar remains institutionally usable without a material quality caveat

It does **not** mean:

- every auxiliary field is perfect

In `daily`, a file can stay `good` even if `vw` has small edge behavior, as long as the primary bar semantics remain sound.

### What `recoverable_with_flag` means

This means:

- the bar is not pristine
- but the dominant issue is still compatible with controlled use under an explicit warning

This is where the historical `review` band of `daily` is translated contractually.

### What `bad` means

This means:

- parse or price integrity is broken strongly enough that the bar should not enter normal downstream use

This is the hard exclusion tail.

## Coverage States

The coverage axis is:

- `recoverable_without_penalty`
- `recoverable_with_flag`
- `review_not_rehabilitated`

### What `recoverable_without_penalty` means

Coverage gaps look compatible with valid absences rather than harmful data failure.

This answers:

- "Is the missingness still acceptable without degrading core use?"

### What `recoverable_with_flag` means in coverage

Coverage ambiguity exists, but the block can still be used if the ambiguity travels explicitly as a flag.

This answers:

- "Can the missingness be tolerated with declared caution?"

### What `review_not_rehabilitated` means in coverage

Coverage remains too problematic or unexpected to be quietly rehabilitated.

This answers:

- "Which coverage gaps remain open enough that the dataset should not silently consume them?"

## Why `vw` does not dominate the whole policy

The historical audit showed that much of the `vw` residue in `daily` comes from:

- edge cases
- illiquid regimes
- threshold effects

That matters, but it does **not** mean the whole daily bar is broken.

So the policy avoids this mistake:

- treating every `vw` conflict as if it invalidated the entire daily object

Instead, `vw` is used to:

- open inspection
- justify flags
- and isolate the small hard tail

## Why coverage must stay separate from quality

A file can be high quality in the bars it does contain and still have a coverage issue.

Likewise, a file can have acceptable coverage but fail in hard parse or price integrity.

That is why the final reading of `daily` is not:

- only quality

and not:

- only coverage

but a combination of both.

## Why `hard_invalid_parse_or_price` is the true hard tail

This family exists because some daily objects fail at the level of:

- parsing
- price plausibility
- or basic OHLC consistency

Those are not merely `vw` disagreements or coverage ambiguities.
They damage the bar itself.

## Why the policy must be explained image by image

In `daily`, a chart is not enough by itself.
The inspector must know:

- whether the image is proving a quality issue
- a coverage issue
- or a combined operational consequence

The dossier must therefore explain:

- what the image proves
- what it does not prove
- and what state transition it supports

## Relation To The General Standard

The transversal rule that requires this explanatory layer lives in:

- `01_foundations/module_contracts/policy_explanation_standard.md`
