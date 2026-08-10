# SEC PIT Owner-Exclusion Methodology Contract v0_1

## Decision

~~~
methodology_id = officer_director_explicit_affiliate_v0_1
experimental_execution = AUTHORIZED
canonical_promotion = NOT_AUTHORIZED
~~~

This contract authorizes the experimental methodology, not any individual
source position and not a canonical historical float.

## Excluded roles

A unique issued-common economic position may be excluded only when its holder
is supported as a current officer, current director, explicit affiliate or
control person at the session cutoff.

A generic 5%, 10% or 20% ownership threshold is not an automatic exclusion in
this methodology. Institutional ownership is not automatically excluded.

## Share treatment

~~~
issued common shares = eligible candidate input
options/warrants/convertibles = not deducted before common issuance
aggregate management group rows = non-additive
direct/indirect duplicate representations = deduct once
unresolved overlap = block point estimate
missing ownership = NULL, never zero
~~~

## Output boundary

The methodology may calculate FLOAT_OWNER_EXCLUSION_ESTIMATE_AS_KNOWN only
after source coverage, holder roles, share class, issued-common treatment and
economic-position deduplication pass. Before then, it must emit
BLOCKED_BY_INPUT_GATES and preserve a null estimate.

Evidence-based upper bounds or scenarios must use separate output names and
must not be substituted for the point estimate.

## Partial daily resolution policy

A complete, causally available DEF 14A ownership table may establish a daily
baseline after issued-common components and economic overlaps pass row-level
resolution.

~~~
before complete baseline
= OWNERSHIP_BASELINE_UNAVAILABLE
= NULL

baseline available and no later unresolved ownership event
= CALCULATED or CALCULATED_WITH_SOURCE_CONFLICT

first later ownership event not yet applied temporally
= POST_BASELINE_OWNERSHIP_EVENT_UNRESOLVED
= NULL from that session forward
~~~

A selected source-conflict precedence must remain visible in
`ownership_component_state` and `ownership_conflict_state`. Partial daily
coverage may receive `PASS_WITH_RESTRICTIONS`; it does not imply complete
temporal resolution or canonical promotion.
## Post-baseline Form 3/4/5 update policy

For a methodology-relevant holder absent from the admitted proxy baseline, TSIS
may add a post-baseline account snapshot only when holder CIK, transaction date,
security class, direct/indirect account and issued-common balance are resolved.
Multiple snapshots for the same account are ordered by transaction date,
eligible session, accession and filing-row sequence; only the latest snapshot is
used.

An event for a holder already represented in the proxy baseline remains blocked
unless TSIS can prove the complete account set needed to replace that baseline
position. Sequential balances must never be added together.