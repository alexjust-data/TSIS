After reviewing the proposal and the evidence package, I would build the screener as a **separate scientific subsystem with two very different clocks**:

1. **once per session:** decide *who TSIS is legally allowed to observe*;
2. **during the session:** decide *who is becoming interesting now*.

And only **after that** would strategy-specific scanners decide whether that activation is relevant to DAS/frontside, parabolic short, breakout, backside, etc.

That distinction is the key.

The current proposal is fundamentally sound: independent Screener Engine, Data Foundation upstream, Backtest as consumer, frozen artifacts, versioned definitions, PIT legality and full denominator accounting.  The evidence package also shows that the previous scanner work already separated base eligibility, generic profiles, intraday candidate discovery and strategy overlays. 

## 1. I would structure the system like this

```text
                  TSIS DATA FOUNDATION
                         │
                         │ governed PIT inputs
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    SCREENER ENGINE                           │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  LAYER 1 — DAILY ELIGIBLE UNIVERSE                    │  │
│  │                                                        │  │
│  │  Parent Frame: lt1b_universe_v0_1                     │  │
│  │                   4,824                                │  │
│  │                     │                                  │  │
│  │                     ▼                                  │  │
│  │            04:00 ET PIT resolution                    │  │
│  │                     │                                  │  │
│  │                     ▼                                  │  │
│  │     Daily Eligible Universe [FROZEN FOR SESSION]      │  │
│  └─────────────────────┬──────────────────────────────────┘  │
│                        │                                     │
│                        ▼                                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  LAYER 2 — CONTINUOUS OBSERVATION                     │  │
│  │                                                        │  │
│  │  all ELIGIBLE symbols                                  │  │
│  │       │                                                │  │
│  │       ├── price movement                               │  │
│  │       ├── volume pace                                  │  │
│  │       ├── dollar-volume pace                           │  │
│  │       ├── relative activity                            │  │
│  │       ├── range expansion                              │  │
│  │       └── generic tradability                          │  │
│  │                                                        │  │
│  │                  LIGHT STATE                           │  │
│  └─────────────────────┬──────────────────────────────────┘  │
│                        │                                     │
│                        │ anomalous activation                │
│                        ▼                                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  LAYER 3 — MARKET ACTIVATION / WAKE-UP                │  │
│  │                                                        │  │
│  │       DORMANT → ACTIVATING → WAKE-UP EVENT            │  │
│  │                          │                             │  │
│  │                          ▼                             │  │
│  │                  ACTIVE SYMBOL SET                     │  │
│  └─────────────────────┬──────────────────────────────────┘  │
│                        │                                     │
│                        ▼                                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  LAYER 4 — HEAVY OBSERVATION                          │  │
│  │                                                        │  │
│  │  richer state only for activated instruments          │  │
│  │                                                        │  │
│  │  microstructure / order flow / liquidity / news /     │  │
│  │  halts / fundamentals / short context / etc.          │  │
│  └─────────────────────┬──────────────────────────────────┘  │
│                        │                                     │
│            ┌───────────┼───────────┬───────────┐             │
│            ▼           ▼           ▼           ▼             │
│       MOMENTUM     DAS/FRONTSIDE PARABOLIC  BACKSIDE         │
│        SCANNER        SCANNER      SCANNER    SCANNER        │
│            │           │           │           │             │
│            └───────────┴───────────┴───────────┘             │
│                        │                                     │
│                        ▼                                     │
│              STRATEGY CANDIDATES                            │
│                                                              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
               SEALED SCREENER ARTIFACT
                  │               │
                  ▼               ▼
             BACKTEST          RESEARCH
                  │
                  ▼
             future LIVE
```

That is the architecture I would pursue.

---

# 2. Layer 1 is practically already solved

I **would not redesign or recalculate** the first layer.

You already have:

```text
population_target_presession_4824_candidate_v0_1_experimental
```

with approximately:

```text
4,824 parent instruments
5,328 sessions
7,369,699 instrument-session rows
2005-01-03 → 2026-03-09
21/21 validation checks PASS
```

and a clear PIT policy. 

At `04:00 America/New_York`:

```text
PRESESSION_REFERENCE_PRICE
=
prior eligible RTH close
```

and:

```text
PRESESSION_REFERENCE_MARKET_CAP_PROXY
=
prior eligible RTH close
×
selected weighted-average shares proxy
```

with the validated policy:

```text
0.50 <= price <= 20.00

market-cap proxy < $100,000,000

shares:
    diluted weighted-average
    else basic weighted-average

TTL:
    180 days

availability:
    as_of_date < session_date
```

I would make that an **immutable daily snapshot**.

Meaning that at 04:00:

```text
SESSION 2026-08-12
        ↓
Daily Eligible Universe vX
        ↓
HASH
        ↓
FROZEN
```

The Backtester must see exactly that snapshot.

It must never run its own:

```text
if market_cap < 100m...
```

logic.

That is one of the strongest decisions in your proposal. 

---

# 3. And I would retain the entire denominator

This is extremely important scientifically.

For every parent instrument:

```text
ELIGIBLE
INELIGIBLE_PRICE
INELIGIBLE_CAP
UNAVAILABLE_PRICE
UNAVAILABLE_SHARES
STALE_SHARES
CORPORATE_ACTION_REVIEW
...
```

Never:

```text
missing -> deleted
```

because otherwise, five years later, you cannot distinguish:

```text
not eligible

from

we didn't know whether it was eligible
```

The proposal gets this exactly right. 

---

# 4. I would NOT use float here yet

Despite how important float is to the microcap phenomenon.

Not yet.

Your current available object is:

```text
weighted-average shares proxy
```

not historical float.

Therefore:

```text
float < X
```

should **not** determine Daily Eligible Universe membership until your SEC PIT float work reaches a governed promotion state.

The proposal explicitly establishes that distinction. 

Later:

```text
Daily Eligible Universe
        │
        ├── float_available = TRUE
        ├── float_estimate = ...
        ├── float_quality = ...
        └── float_asof = ...
```

could enrich the row.

But it should not silently change what `eligible_v0_1` meant.

---

# 5. Here is where I would modify the proposal slightly

The document says:

> there should not be one universal In-Play engine; there should be a family of strategy-specific In-Play scanners.

I agree **partially**.

I would keep:

```text
Strategy In-Play Scanner
```

strategy-specific.

But I would insert one strategy-neutral concept before it:

# `MARKET ACTIVATION / WAKE-UP`

This is not:

```text
DAS In-Play
momentum In-Play
short In-Play
```

It simply answers:

> **Has this previously dormant eligible instrument begun behaving anomalously enough that TSIS should start observing it more intensely?**

That's a market phenomenon.

Not a strategy.

So I would use this taxonomy:

```text
Daily Eligible
      ↓
Generic Observation
      ↓
Market Activation / Wake-Up
      ↓
Active Symbol Set
      ↓
Heavy Market State
      ↓
Strategy-specific In-Play
      ↓
Strategy
```

This reconciles your newer architectural decision with the best part of the earlier scanner work.

---

# 6. The biggest mistake would be to make `500,000 volume` the wake-up trigger

Your earlier evidence already identified this problem.

The legacy human scanner:

```text
volume >= 500,000
rank % change
top 25
```

is useful for reconstructing:

> "What would Alex have seen in his conventional hot list?"

But it is **not** a good scientific activation detector.

Because by the time:

```text
volume = 500,000
```

the phenomenon may already have been underway for several minutes.

The earlier scanner material explicitly recognizes this limitation and proposes activity **pace/acceleration** rather than raw cumulative volume as a generic observation mechanism. 

That is exactly what I would do.

---

# 7. I would observe all eligible symbols using a LIGHT STATE

Suppose the presession universe gives approximately 250–300 eligible instruments on a typical day.

There is no reason to construct the complete expensive Market State for all of them continuously.

I would calculate only very cheap observables:

```text
PRICE
─────
price
move_vs_prior_close
move_vs_04_open
return_1m
return_3m
return_5m
high_since_04
distance_from_high

ACTIVITY
────────
volume_1m
volume_3m
volume_5m
volume_since_04
volume_velocity
volume_acceleration
volume_to_time

ECONOMIC ACTIVITY
─────────────────
dollar_volume_1m
dollar_volume_3m
dollar_volume_since_04
dollar_volume_velocity

RANGE
─────
range_1m
range_3m
range_expansion
range_vs_baseline

GENERIC LIQUIDITY
─────────────────
only whatever is legally available
and governed at timestamp t
```

And crucially:

```text
relative to the instrument's PIT historical baseline
```

not just absolute thresholds.

---

# 8. This gives you a very different scanner from a normal market scanner

A normal scanner asks:

```text
who has traded >500k?
who is +30%?
who is top-20?
```

TSIS should eventually ask:

```text
WHO IS CHANGING STATE?
```

Example.

At 07:13:

```text
XYZ

volume_since_04     = only 73,000
price change        = +9%
```

A traditional scanner may ignore it.

But TSIS might observe:

```text
normal volume by 07:13      = 4,000
actual volume               = 73,000

volume pace                 = extreme
volume acceleration         = increasing
dollar-volume acceleration  = increasing
range expansion             = abnormal
price response              = coherent
```

So:

```text
DORMANT
   ↓
ACTIVATING
   ↓
WAKE-UP 07:13:24
```

Even though it has nowhere near 500k shares yet.

**That is the screener I think you actually want to build.**

---

# 9. But I would not initially turn that into a mysterious `activation_score`

At least not in v0.1.

I would preserve independent reasons:

```text
reason_volume_pace_anomaly
reason_volume_acceleration
reason_dollar_volume_acceleration
reason_price_acceleration
reason_range_expansion
reason_gap_expansion
reason_premarket_high
reason_activity_regime_shift
...
```

One instrument can therefore say:

```text
XYZ
07:13:24

WAKE_UP_CANDIDATE = TRUE

reasons:
    volume_pace_anomaly
    dollar_volume_acceleration
    range_expansion
```

rather than:

```text
activation_score = 82.7
```

whose economic meaning nobody understands.

A learned composite could come much later.

---

# 10. Then promote only activated symbols to the expensive layer

This is where your overall Market State architecture fits beautifully.

Before wake-up:

```text
300 eligible symbols
×
LIGHT STATE
```

After wake-up:

```text
perhaps 3–15 symbols
×
HEAVY STATE
```

Then you can bring in:

```text
trades
quotes
spread
depth if available
order-flow pressure
microstructure
halt context
news
fundamentals
short context
share structure
float when governed
dilution context
previous runs
intraday levels
VWAP
turnover
etc.
```

This creates an architecture that is both computationally rational and conceptually clean.

---

# 11. Now the Strategy In-Play scanners make sense

An activated symbol is **not necessarily In-Play for every strategy**.

For example:

```text
                       WAKE-UP
                          │
          ┌───────────────┼─────────────────┐
          │               │                 │
          ▼               ▼                 ▼
 DAS/FRONTSIDE       PARABOLIC SHORT     BREAKOUT
     scanner             scanner          scanner
          │               │                 │
       TRUE             FALSE             TRUE
```

Same market event.

Different strategy relevance.

This is where I strongly agree with the new proposal's decision to avoid one universal strategy-level `In-Play`. 

---

# 12. I would preserve the old +50% scanner — but demote its meaning

Your earlier work had approximately:

```text
first 1m cross +50% vs prior close
+
tradability
```

as an intraday momentum candidate.

I wouldn't delete it.

I would transform it into:

```text
inplay_momentum_scanner_v0_1
```

or:

```text
strong_momentum_observation_profile_v0_1
```

depending on its final purpose.

It becomes one detector among many.

It no longer defines what **In-Play itself** universally means.

This is precisely the kind of historical artifact that the evidence package says should be retained but reinterpreted rather than silently reused as universal doctrine. 

---

# 13. There is another important issue: do not materialize every scanner state every minute

You have:

```text
1,417,316 ELIGIBLE instrument-session rows
```

in the current materialization. 

If you naïvely stored every eligible symbol for every minute from:

```text
04:00 → 20:00
= 960 minutes
```

you would potentially create approximately:

```text
1,417,316 × 960
≈ 1.36 billion rows
```

before adding scanner families.

I wouldn't design the institutional artifact like that.

Instead:

### Dense computation, sparse persistence

Internally:

```text
evaluate every minute/event
```

but persist primarily:

```text
state transitions
threshold crossings
activation events
candidate changes
reason changes
periodic checkpoints
```

Example:

```text
07:12:00 DORMANT
07:13:00 ACTIVATING
07:13:24 WAKE_UP
07:16:00 MOMENTUM_INPLAY
07:21:00 FRONTSIDE_TRACKING
...
```

This is much more natural for the phenomenon you're studying.

---

# 14. Therefore I would split the proposed `scanner_candidates.parquet`

Instead of one overloaded artifact, I'd have something conceptually like:

```text
screener_run_manifest.json

daily_eligible_universe.parquet

generic_observation_events.parquet

market_activation_events.parquet

strategy_scanner_candidates.parquet

screener_validation_report.json
```

Possibly also:

```text
scanner_checkpoints.parquet
```

for reproducibility/research.

That separation matters.

Because:

```text
Daily Eligible membership
```

is fundamentally different from:

```text
a wake-up transition at 07:13:24
```

which is fundamentally different again from:

```text
DAS scanner says TRUE at 07:19:07
```

---

# 15. The clocks must also be explicitly different

I would make this a first-class architectural concept.

### CLOCK A — Eligibility clock

```text
once/session
04:00 ET

Daily Eligible Universe
```

Frozen.

### CLOCK B — Observation clock

Initially with your currently evidenced infrastructure:

```text
1-minute/event-time replay
04:00 → 20:00 ET
```

The package already contains an intraday 1m scanner precedent and the quote-guarded repair architecture, including the rule that a raw +50% cross not confirmed by the repaired view should not become an In-Play selection. 

### CLOCK C — Strategy scanner clock

Can be:

```text
on activation
on every new minute
on relevant state transition
on halt/reopen
...
```

depending on scanner contract.

Eventually, if governed trades/quotes support it, Wake-Up can run below one minute.

But that should be a **new physical-binding version**, not something we pretend the current 1m source provides.

---

# 16. And this is where quote-guarding matters

For an intraday screener, a bad one-minute wick can create:

```text
+80%
```

for one bar.

If you promote that immediately:

```text
fake wake-up
→ fake in-play
→ fake episode
→ contaminated Market State dataset
→ contaminated labels
→ contaminated ML/RL
```

Your earlier evidence already established the correct idea:

```text
raw OHLCV
+
quote-guarded repair manifest
=
governed intraday price view
```

So I would put the price-view selection in `InputManifestResolver`, never inside a scanner definition.

A strategy shouldn't be able to say:

```text
I'll use raw because this ticker passes my rule that way.
```

---

# 17. What I would call each concept

I would be extremely strict with the names:

```text
PARENT FRAME
lt1b_universe_v0_1
        │
        ▼
DAILY ELIGIBLE UNIVERSE
who TSIS may observe today
        │
        ▼
GENERIC OBSERVATION PROFILES
what is changing / ranking / anomalous
        │
        ▼
MARKET ACTIVATION EVENT
a market phenomenon has awakened
        │
        ▼
ACTIVE SYMBOL SET
symbols deserving expensive observation
        │
        ▼
MARKET STATE
what TSIS knows about the market now
        │
        ▼
STRATEGY IN-PLAY SCANNER
is this state relevant to strategy X?
        │
        ▼
STRATEGY POLICY
what should we do?
        │
        ▼
ORDER / FILL / PNL
what happened?
```

That taxonomy prevents almost every architectural contamination we've been discussing.

---

# 18. What should the **first actual implementation** be?

I wouldn't start by implementing DAS.

I would do it in this exact order:

```text
SCREENER-GATE-001
Daily Eligible Universe adoption
        ↓
SCREENER-GATE-002
Daily snapshot + manifest + validator
        ↓
SCREENER-GATE-003
1m generic observation replay
        ↓
SCREENER-GATE-004
Wake-Up / Activation Event framework
        ↓
SCREENER-GATE-005
Active Symbol Set lifecycle + dedup/rearm
        ↓
SCREENER-GATE-006
first strategy scanner:
Momentum / +50% historical baseline
        ↓
SCREENER-GATE-007
DAS / Frontside scanner
        ↓
BT-GATE-016
Backtest consumes sealed screener artifacts
```

Why first reproduce the +50% momentum scanner?

Because you already have previous evidence for it.

That gives you a **control scanner**.

Then when the new Wake-Up detector says:

```text
TSIS detected XYZ at 07:13 with 73k shares
```

and the historical scanner says:

```text
traditional In-Play detected XYZ at 07:31 with 521k shares
```

you can scientifically measure:

```text
lead time
false activations
coverage
precision
episode capture
tradability at detection
subsequent evolution
```

Now your statement:

> "our scanner detects activation earlier"

becomes empirically falsifiable rather than intuition.

---

# 19. The Daily Eligible Universe is not the screener

This is perhaps the conceptual point I would emphasize most.

Your current 7.37-million-row asset answers:

```text
WHO COULD WE HAVE LOOKED AT?
```

Excellent.

But the real screener you're trying to invent answers:

```text
WHO SHOULD WE START LOOKING AT
RIGHT NOW?
```

And the strategy scanner answers:

```text
DOES WHAT IS HAPPENING NOW
BELONG TO MY PARTICULAR PHENOMENON?
```

Those are three separate scientific questions.

---

# 20. So my final architecture would be

```text
                    FIXED GOVERNED PARENT FRAME
                              4,824
                                │
                                ▼
                   DAILY PIT ELIGIBILITY @ 04:00
                                │
                                ▼
                    DAILY ELIGIBLE UNIVERSE
                       ≈ hundreds/session
                                │
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
            LIGHT OBSERVATION          AUDIT DENOMINATOR
                    │
                    ▼
         ANOMALOUS ACTIVITY DETECTION
                    │
                    ▼
               WAKE-UP EVENT
                    │
                    ▼
             ACTIVE SYMBOL SET
                    │
                    ▼
              HEAVY MARKET STATE
                    │
          ┌─────────┼─────────┬────────────┐
          │         │         │            │
          ▼         ▼         ▼            ▼
      Momentum   Frontside  Parabolic   Backside
       Scanner    Scanner    Scanner     Scanner
          │         │         │            │
          └─────────┴─────────┴────────────┘
                    │
                    ▼
          STRATEGY-SPECIFIC CANDIDATE
                    │
                    ▼
                 STRATEGY
                    │
                    ▼
                  ACTION
```

And I would preserve the proposal's institutional separation:

```text
01_TSIS_DATA_FOUNDATION
        ↓ supplies facts

07_TSIS_SCREENER_ENGINE
        ↓ decides observation/candidates

02_TSIS_BACKTEST_ENGINE
        ↓ replays sealed decisions

Strategy layer
        ↓ decides action
```

The evidence package supports the first three boundaries very strongly.  

**So I would approve most of `SCREENER_ENGINE_ARCHITECTURE_PROPOSAL_v0_1`, but I would make one architectural amendment before freezing it: insert an explicit, strategy-neutral `Market Activation / Wake-Up` layer between Generic Observation and Strategy In-Play scanners.** That layer is, in my view, the missing bridge between the screener architecture you have written and the actual scientific problem TSIS is trying to solve: detecting the transition from dormant to materially anomalous activity as early and causally as possible.
