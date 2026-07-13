# TSIS Market Representation Architecture

## PART II --- Feature Engineering Theory

### Chapter 26 --- Contextual Features

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 26. Contextual Features

## 26.1 Purpose

An observable property has little scientific meaning when interpreted in
isolation.

Contextual features describe the environment in which an observation
occurs.

Their purpose is not to replace primary features but to explain their
significance.

------------------------------------------------------------------------

## 26.2 Fundamental Principle

A measurement becomes meaningful only within its context.

Example:

``` text
Trade Count Rate = 120 trades/s
```

Without context this value is incomplete.

With context:

``` text
Price = 0.65 USD
Time = 09:31 ET
RVOL = 18.4
Spread = 0.01 USD
Gap = +42%
```

the same measurement becomes interpretable.

------------------------------------------------------------------------

## 26.3 Definition

A contextual feature is any feature that characterizes the environment
surrounding another observable property rather than the property itself.

Context does not replace observations.

Context explains observations.

------------------------------------------------------------------------

## 26.4 Context dimensions

Typical dimensions include:

``` text
Temporal
Instrument
Market
Microstructure
Fundamental
News
Regime
Execution
```

------------------------------------------------------------------------

## 26.5 Temporal context

Examples:

``` text
Minute from Open
Time Since Open
Lunch Session
Minutes to Close
Day of Week
Month
Quarter
```

Temporal context provides seasonal structure.

------------------------------------------------------------------------

## 26.6 Instrument context

Examples:

``` text
Price
Market Cap
Float
Listing Age
Exchange
Security Type
```

These describe the economic identity of the instrument.

------------------------------------------------------------------------

## 26.7 Market context

Examples:

``` text
SPY Return
QQQ Return
VIX
Market Breadth
Sector Strength
Small-Cap Activity
```

The same local feature may have different meaning under different market
regimes.

------------------------------------------------------------------------

## 26.8 Microstructure context

Examples:

``` text
Spread
Top Depth
Quote Update Rate
Trade Rate
Signed Flow
OFI
```

Microstructure often acts as context for price behaviour rather than as
a direct prediction.

------------------------------------------------------------------------

## 26.9 Event context

Examples:

``` text
Trading Halt
News Publication
Scanner Qualification
Corporate Action
Strategy Candidate
```

Events define governed observational environments.

------------------------------------------------------------------------

## 26.10 Historical context

Examples:

``` text
20-Day Percentile
Historical Z-Score
Previous Halt Count
Days Since Last Event
Prior Breakout Frequency
```

Historical context must always remain point-in-time.

------------------------------------------------------------------------

## 26.11 Context versus target

Context shall never contain future information.

Future outcomes are evaluation objects.

Context remains observable.

------------------------------------------------------------------------

## 26.12 Context metadata

Every contextual feature shall declare:

``` text
context_family
reference_object
observation_scope
timestamp_semantics
lookback_policy
version
```

------------------------------------------------------------------------

## 26.13 Constitutional rule

Contextual features enrich the interpretation of observable properties.

They never introduce future knowledge.

Context remains descriptive rather than predictive and therefore belongs
entirely to the Representation Layer.
