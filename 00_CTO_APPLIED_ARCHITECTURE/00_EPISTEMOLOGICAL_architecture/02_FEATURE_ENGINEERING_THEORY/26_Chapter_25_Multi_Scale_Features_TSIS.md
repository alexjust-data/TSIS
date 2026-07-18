# TSIS Market Representation Architecture

## PART II --- Feature Engineering Theory

### Chapter 25 --- Multi-Scale Features

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 25. Multi-Scale Features

## 25.1 Purpose

Markets evolve simultaneously across multiple temporal scales.

A feature computed over a single horizon captures only one projection of
market behaviour.

TSIS therefore treats scale as a first-class architectural dimension.

------------------------------------------------------------------------

## 25.2 Fundamental Principle

A feature is incomplete until its observation scale has been explicitly
declared.

Examples:

``` text
Trade Count Rate
250 ms
1 s
5 s
30 s
```

These are different canonical features sharing the same semantic family.

------------------------------------------------------------------------

## 25.3 Scale hierarchy

Typical horizons:

``` text
Micro
100 ms
250 ms
500 ms

Short
1 s
2 s
5 s
10 s

Medium
30 s
60 s
5 m

Long
15 m
Daily
Multi-day
```

------------------------------------------------------------------------

## 25.4 Temporal consistency

Comparisons across scales are legal only when both features satisfy
identical:

-   timestamp semantics,
-   eligibility policy,
-   alignment policy,
-   quality requirements.

------------------------------------------------------------------------

## 25.5 Cross-scale relationships

New knowledge emerges from relationships between scales.

Examples:

``` text
TradeRate_1s / TradeRate_30s

Spread_1s - Spread_30s

OFI_5s vs OFI_60s

Microprice_250ms relative to Microprice_5s
```

These are multi-scale features.

------------------------------------------------------------------------

## 25.6 Scale invariance

Whenever possible, feature semantics should remain invariant across
scales.

Only the observation horizon changes.

The mathematical meaning remains stable.

------------------------------------------------------------------------

## 25.7 Scale metadata

Every multi-scale feature shall declare:

``` text
base_feature
window
window_units
lookback_policy
sampling_policy
version
```

------------------------------------------------------------------------

## 25.8 Multi-scale representations

Representations may combine several horizons.

Example:

``` text
Microstructure Representation

Trade Rate 250 ms
Trade Rate 1 s
Trade Rate 5 s
Trade Rate 30 s

Spread 250 ms
Spread 1 s
Spread 5 s
```

The representation captures temporal structure rather than isolated
measurements.

------------------------------------------------------------------------

## 25.9 Illegal scale mixing

Forbidden examples:

-   comparing features built with incompatible eligibility rules;
-   mixing regular-session and full-session windows without declaration;
-   mixing point-in-time and hindsight-normalized windows.

------------------------------------------------------------------------

## 25.10 Constitutional rule

Time scale is part of a feature's identity.

Changing the observation horizon creates a distinct canonical feature
rather than a different implementation of the same feature.
