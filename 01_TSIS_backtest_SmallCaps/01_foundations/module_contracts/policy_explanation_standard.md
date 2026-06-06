# Policy Explanation Standard

## Purpose

This document defines a transversal institutional rule:

- a formal policy is necessary,
- but by itself it is not enough.

Every important operational policy must also have an explanatory layer.

The formal layer tells the reader:

- what the rule is.

The explanatory layer tells the reader:

- what the rule means,
- why it exists,
- what question it answers,
- what question it does not answer,
- what mistake it avoids,
- and what operational consequence it has.

## Scope

This standard applies to:

- acceptance policies
- certification policies
- rehabilitation policies
- data-consumption policies
- price-view policies
- reconciliation policies
- and any future rule that changes how data is interpreted or consumed

## Required Two-Layer Structure

Every important policy should be represented in two layers.

### 1. Formal policy layer

This is the contractual or operational document.

It defines:

- labels
- states
- thresholds
- cut logic
- allowed uses
- prohibited uses

### 2. Explanatory companion layer

This is the didactic but rigorous companion.

It explains:

- what each state really means
- why each metric matters
- what misuse the rule prevents
- and what downstream decision changes because of the rule

## Minimum Required Questions

For each important state, metric or rule, the explanatory layer must say:

- `what it is`
- `what question it answers`
- `what question it does not answer`
- `why it matters`
- `what methodological error it avoids`
- `what operational consequence it has`

If a document only lists labels or thresholds, it is incomplete as an institutional explanation.

## Example Of The Expected Level

Weak statement:

- `size <= 0 rows trigger bad_data`

Institutionally acceptable explanatory statement:

- `size` in `trades` is executed quantity
- a real execution must have positive size
- therefore `size = 0` is not just a noisy value but a semantic violation of the tape
- this does not merely answer whether price looks plausible
- it answers whether the row still behaves like a real execution
- treating the file as clean would contaminate execution research and tape-level features

This is the expected level for future explanatory companions.

## Relation With Inspection Dossiers

Inspection dossiers follow the same philosophy.

Graphs and examples must not stop at:

- bucket name
- metric list
- visual description

They must also explain:

- what the image proves
- what it does not prove
- where the problem is visible
- and what decision changes because of what is seen

## Scientific And Institutional Alignment

This standard is aligned with the literature already adopted in the module:

- O'Hara (1995)
- Hasbrouck (2007)
- Menkveld (2013)
- Lopez de Prado

The shared principle is simple:

- formal labels without semantic explanation are not enough for serious research governance.
