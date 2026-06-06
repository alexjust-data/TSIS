# `quotes` Acceptance Policy Explained

## Purpose

This document explains the `quotes` acceptance policy in plain but rigorous language.

The formal sources remain:

- `01_foundations/contract_registry/dataset_contracts/quotes_label_taxonomy_and_cut_policy.md`
- `01_foundations/data_consumption_policies/quotes_consumption_policy.md`

This document does not replace them.
It explains them.

## Core Principle

`quotes` answers one primary question:

- what state of the observed `bid / ask` book was present during the session?

It does **not** answer by itself:

- whether a halt existed
- whether a corporate action happened
- whether the ticker identity was correct
- or why the episode happened in external causal terms

Because of that, the policy must separate:

1. local book quality
2. external causal explanation

## Three Final Local States

The local policy of `quotes` closes into:

- `good`
- `review`
- `bad`

These states are about the operational cleanliness of the observed book, not about the narrative explanation of the day.

## What `good` means

`good` means:

- the local book remains acceptable for the strictest institutional use of the block

This includes families where:

- the book is clean
- or the residual crossed behavior remains minor enough not to break core use

## What `review` means

`review` means:

- the file is not clean enough for `good`
- but it is not uniformly severe enough to be classified as `bad`

This is the operational caution zone of `quotes`.

It typically means:

- use only with explicit flag, explanation or controlled context

## What `bad` means

`bad` means:

- crossed behavior remains too aggressive for normal core use
- even after allowing for plausible external explanation

These files remain useful for forensics, but not for the normal core of the block.

## Why external explanation does not automatically rehabilitate `quotes`

This is one of the most important rules in the block.

A halt, a news shock or another external event can explain **why** the book looks stressed.
But it does not automatically prove that the book is operationally clean.

This avoids a major mistake:

- confusing causal explanation with local book quality

In `quotes`, the local book still matters.

## Why positive crossed with `ask > 0` matters so much

The historical closeout showed that the crucial severity signal is not crossed in the abstract.

It is:

- economically material positive crossed with `ask > 0`

That is why the policy is organized around:

- `mild`
- `moderate`
- `severe`

and around whether the crossed survives as a real positive crossed rather than a degenerate `ask = 0` artifact.

## Why `ask = 0` must be read carefully

`ask = 0` can create visually dramatic episodes.
But those episodes do not always mean the same thing as a positive economic crossed with a live ask.

So `quotes` must separate:

- degenerate or structural artifacts
- from truly economic crossed states

This avoids a second mistake:

- calling every strange book shape equally harmful.

## Why `good` is not just “no crossed at all”

Some `good` families still contain:

- minor crossed noise
- low persistent crossed
- rollover-like artifacts

The point is not to demand visual perfection.
The point is to decide whether the residual distortion still leaves the book usable for the intended institutional consumers.

## Why `review` is not just “soft fail”

`review` is not a generic middle bucket.
It is where the book is still too stressed for `good`, but the evidence does not justify uniform `bad`.

This is why buckets such as:

- `persistent_soft_crossed_mid_large_scale`
- `large_file_threshold_edge_hard_many_crosses`

remain in `review`.

## Why `bad` is reserved for the aggressive open families

The final `bad` families are:

- `medium_file_threshold_edge_hard_many_crosses`
- `high_hard_crossed_10_to_20`

They stay in `bad` because the crossed remains:

- economically stronger
- harder to contextualize benignly
- and too risky for normal core use

## Why the policy must be explained image by image

In `quotes`, one image may prove:

- a local economic crossed state
- a degenerate `ask = 0` artifact
- a threshold-edge mixed family
- or an externally explained but still operationally stressed book

So the dossier must explain:

- what the image proves
- what it does not prove
- whether the stress is economic, structural or mixed
- and what decision changes because of what is seen

## Relation To The General Standard

The transversal rule that requires this explanatory layer lives in:

- `01_foundations/module_contracts/policy_explanation_standard.md`
