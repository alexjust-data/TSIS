
I reviewed Massive’s **current Stocks documentation as of 20 August 2026**, including REST, Flat Files, WebSockets, pricing, the official Python client, the changelog, and trade-specific FAQs.

The central conclusion is important: for **4,824 stocks and full tick-level history, REST should not be the primary historical acquisition mechanism**. Massive explicitly designs **Flat Files for bulk history**. REST should complement them for reference/fundamental/corporate/SEC/news datasets and for targeted validation. ([Massive][1])

# 1. What Massive actually provides for Stocks

Massive currently documents **48 Stocks REST endpoints**. In addition, Stocks has **4 historical Flat File datasets** and several live WebSocket feeds. ([Massive][2])

Before the endpoint tree, there are several global properties that we absolutely must treat as data contracts.

### Market coverage

Massive says its U.S. equities coverage includes the 19 major exchanges, dark pools, FINRA Trade Reporting Facilities and OTC trade reporting. Exchange trades and quotes are included; FINRA/OTC facilities contribute trades but not quotes. ([Massive][3])

### Sessions

The documented stock sessions are:

* Pre-market: **04:00–09:30 ET**
* Regular: **09:30–16:00 ET**
* After-hours: **16:00–20:00 ET**

ET must be implemented as the IANA timezone `America/New_York`, not as a permanent UTC−5 offset, because daylight saving changes the UTC offset. Massive timestamps are Unix/UTC; the individual trade REST schema explicitly specifies **nanosecond** timestamps. ([Massive][3])

There is actually an important API-contract nuance: **timestamp units are surface-specific**. REST trades document nanoseconds, while the Stocks WebSocket trade schema documents millisecond fields such as `t` and `pt`. Never infer units from a generic “Unix timestamp” statement; record the unit in each ingestion schema. ([Massive][4])

### Historical coverage

For trades, Massive documents records back to **10 September 2003**. Stocks Advanced provides all available trade history; Developer provides 10 years. Quotes all-history requires Advanced. ([Massive][4])

### Raw vs adjusted

Massive's Flat Files are explicitly **unadjusted**. Prices and volumes are not changed for splits, dividends, etc. REST aggregates can offer adjusted data, while split data can be used to build your own adjustment layer. For scientific storage, this is exactly what we want: retain immutable unadjusted observations and construct adjusted representations downstream. ([Massive][5])

---

# 2. Complete REST parent → child endpoint tree

## A. TICKERS / SECURITY IDENTITY

1. **All Tickers**
`GET /v3/reference/tickers`

2. **Ticker Overview**
`GET /v3/reference/tickers/{ticker}`

3. **Ticker Types**
`GET /v3/reference/tickers/types`

4. **Related Tickers**
`GET /v1/related-companies/{ticker}`

These are not trivial metadata endpoints. `All Tickers` supports date/as-of queries, active/inactive securities, CIK, FIGI, exchange, asset type, locale, etc. It also lets you discover delisted symbols. ([Massive][6])

Ticker Overview can return:

* `active`
* `ticker`
* `ticker_root`
* `ticker_suffix`
* `name`
* `type`
* `market`
* `locale`
* `currency_name`
* `primary_exchange`
* `cik`
* `composite_figi`
* `share_class_figi`
* `market_cap`
* `share_class_shares_outstanding`
* `weighted_shares_outstanding`
* `round_lot`
* `sic_code`
* `sic_description`
* `list_date`
* `delisted_utc`
* `description`
* `homepage_url`
* `phone_number`
* `total_employees`
* address:

* `address1`
* `city`
* `state`
* `postal_code`
* branding:

* `logo_url`
* `icon_url`

([Massive][7])

There is a major PIT warning here: Massive documents that a historical ticker-details query can associate SEC information using the **period-of-report date**, even where the filing was submitted later. Their example says information from a filing submitted 31 July 2019 can appear in a query dated 29 June 2019 because that is the filing's period-of-report date. Therefore, **Ticker Overview must not automatically be interpreted as causally available-at-t PIT data**. ([Massive][8])

---

## B. AGGREGATE BARS / OHLCV

5. **Custom Bars**
`GET /v2/aggs/ticker/{stocksTicker}/range/{multiplier}/{timespan}/{from}/{to}`

6. **Daily Market Summary**
`GET /v2/aggs/grouped/locale/us/market/stocks/{date}`

7. **Daily Ticker Summary / Open-Close**
`GET /v1/open-close/{stocksTicker}/{date}`

8. **Previous Day Bar**
`GET /v2/aggs/ticker/{stocksTicker}/prev`

Custom bars support user-defined multipliers/timespans and include extended sessions. Bars are generated only from qualifying trades; a period with no qualifying trade can legitimately have **no bar at all**. ([Massive][3])

Typical aggregate information includes OHLC, volume, VWAP, transaction count and timestamps.

---

## C. SNAPSHOTS

9. **Single Ticker Snapshot**
`GET /v2/snapshot/locale/us/markets/stocks/tickers/{stocksTicker}`

10. **Full Market Snapshot**
`GET /v2/snapshot/locale/us/markets/stocks/tickers`

11. **Unified Snapshot**
`GET /v3/snapshot`

12. **Top Market Movers**
`GET /v2/snapshot/locale/us/markets/stocks/{direction}`

The stock snapshot combines current trade, current quote, minute bar, current day and previous day information. Full Market Snapshot covers 10,000+ active tickers in one response.

These are **state snapshots**, not historical event archives. Massive clears stock snapshot state around **03:30 AM ET** and starts repopulating when activity begins, potentially around 04:00 AM ET. Top movers return the 20 biggest gainers/losers, subject to a 10,000-share volume threshold. ([Massive][3])

---

## D. TRADES & QUOTES

13. **Trades**
`GET /v3/trades/{stockTicker}`

14. **Last Trade**
`GET /v2/last/trade/{stocksTicker}`

15. **Quotes**
`GET /v3/quotes/{stockTicker}`

16. **Last Quote / NBBO**
`GET /v2/last/nbbo/{stocksTicker}`

([Massive][3])

I analyse Trades separately below because this is the most important part of the acquisition.

---

## E. TECHNICAL INDICATORS

17. **SMA**
`GET /v1/indicators/sma/{stockTicker}`

18. **EMA**
`GET /v1/indicators/ema/{stockTicker}`

19. **MACD**
`GET /v1/indicators/macd/{stockTicker}`

20. **RSI**
`GET /v1/indicators/rsi/{stockTicker}`

These are vendor-derived representations of underlying price data, not new raw market observations. ([Massive][3])

---

## F. MARKET OPERATIONS / DICTIONARIES

21. **Exchanges**
`GET /v3/reference/exchanges`

22. **Market Holidays**
`GET /v1/marketstatus/upcoming`

23. **Current Market Status**
`GET /v1/marketstatus/now`

24. **Condition Codes**
`GET /v3/reference/conditions`

These are essential to correctly interpret trades and quotes. ([Massive][3])

Exchange records include, among other things:

* Massive exchange `id`
* acronym
* name
* MIC
* operating MIC
* SIP participant ID
* asset class
* locale
* type: exchange / SIP / TRF
* URL

([Massive][9])

Condition records include:

* condition `id`
* name
* abbreviation
* description
* asset class
* data types
* exchange restrictions
* `legacy`
* SIP mappings
* condition type
* importantly, **aggregation/update rules**

This dictionary is indispensable when reconstructing bars or deciding which trades affect OHLC/volume. ([Massive][10])

Market Holidays is **forward-looking only**. It provides date, holiday name, exchange, status and special open/close times. Current Market Status exposes pre-market/after-hours flags, exchange states, whole-market status and server time. ([Massive][11])

---

# G. CORPORATE ACTIONS

25. **IPOs**
`GET /vX/reference/ipos`

26. **Splits — deprecated**
`GET /v3/reference/splits`

27. **Splits — current**
`GET /stocks/v1/splits`

28. **Dividends — deprecated**
`GET /v3/reference/dividends`

29. **Dividends — current**
`GET /stocks/v1/dividends`

30. **Ticker Events**
`GET /vX/reference/tickers/{id}/events`

([Massive][3])

IPOs include historical/upcoming offering information and history beginning around 2008. Splits provide execution dates, ratios and adjustment factors. Dividends provide declaration/ex/record/payment dates, amount and adjustment information.

Ticker Events is especially important for our 4,824-name universe because it exposes ticker/name changes. Massive currently labels this endpoint **experimental**. ([Massive][3])

---

# H. FUNDAMENTALS / OWNERSHIP / SHORT DATA

31. **Balance Sheets**
`GET /stocks/financials/v1/balance-sheets`

32. **Cash Flow Statements**
`GET /stocks/financials/v1/cash-flow-statements`

33. **Income Statements**
`GET /stocks/financials/v1/income-statements`

34. **Financial Ratios**
`GET /stocks/financials/v1/ratios`

35. **Short Interest**
`GET /stocks/v1/short-interest`

36. **Short Volume**
`GET /stocks/v1/short-volume`

37. **Float**
`GET /stocks/vX/float`

([Massive][3])

The important frequencies/semantics are:

* Balance sheet: quarterly/annual point-in-time financial position.
* Cash flow: quarterly/annual/TTM flows.
* Income statement: quarterly/annual/TTM.
* Ratios: vendor-derived valuation/profitability/liquidity/leverage metrics.
* Short interest: FINRA, approximately twice monthly.
* Short volume: daily FINRA off-exchange/ATS short-sale activity.
* Float: **latest free float**, not a historical daily float series.

Massive's float definition excludes strategic/locked/affiliate holdings and owners of 5%+, subject to reporting lag. The documentation explicitly warns that it is derived from public ownership disclosures rather than real-time ownership changes. ([Massive][3])

---

# I. SEC FILINGS & DISCLOSURES

38. **EDGAR Index**
`GET /stocks/filings/vX/index`

39. **10-K Sections**
`GET /stocks/filings/10-K/vX/sections`

40. **8-K Text**
`GET /stocks/filings/8-K/vX/text`

41. **8-K Disclosures**
`GET /stocks/filings/8-K/vX/disclosures`

42. **Disclosure Categories / Taxonomy**
`GET /stocks/taxonomies/vX/disclosures`

43. **13-F Filings**
`GET /stocks/filings/vX/13-F`

44. **Risk Factors**
`GET /stocks/filings/vX/risk-factors`

45. **Risk Categories / Taxonomy**
`GET /stocks/taxonomies/vX/risk-factors`

46. **Form 3**
`GET /stocks/filings/vX/form-3`

47. **Form 4**
`GET /stocks/filings/vX/form-4`

The EDGAR index includes form, filing date, CIK, ticker, company name, accession and original SEC document links. Massive additionally provides extracted 10-K/8-K text, structured disclosure classifications, risk-factor classifications, institutional 13-F holdings, initial insider ownership via Form 3 and insider transactions via Form 4. ([Massive][3])

---

# J. NEWS

48. **News**
`GET /v2/reference/news`

It provides articles associated with tickers, publisher metadata, publication information, summaries, URLs, associated tickers and Massive sentiment/reasoning data. ([Massive][12])

That gives us the complete current **48-endpoint REST Stocks tree**.

---

# 3. Trades: exactly what we can acquire

The primary endpoint is:

`GET /v3/trades/{stockTicker}`

It is **one ticker per endpoint call**. There is no REST call where we submit all 4,824 symbols and receive all their historical trades. ([Massive][4])

## Trade record

A REST trade can contain:

```text
conditions[]
correction
decimal_size
exchange
id
participant_timestamp
price
sequence_number
sip_timestamp
size
tape
trf_id
trf_timestamp
```

Plus response-level:

```text
status
request_id
next_url
```

([Massive][4])

### `conditions`

Array of Massive condition IDs.

Do **not** discard these. They tell us whether a print is regular, average-price, out-of-sequence, extended-hours, etc., and how it participates in aggregates.

Resolve them through:

`GET /v3/reference/conditions`

### `correction`

Trade-correction indicator.

Massive explicitly says canceled trades **remain in the data feed**. Cancellation is represented through the correction field. Therefore:

> RAW trades must retain corrections/cancellations exactly as received.

Never physically delete the original event. Build a separate corrected interpretation downstream. ([Massive][13])

### `decimal_size`

Exact fractional quantity represented as a decimal string.

This is particularly important because Massive introduced improved fractional-share precision in February 2026. REST added `decimal_size`; Flat File `size` now supports decimal quantities, while old historical files remain unchanged. Your schema therefore has to tolerate historical integer sizes and newer fractional sizes without truncation. ([Massive][14])

### `exchange`

Massive integer exchange ID.

Resolve through:

`GET /v3/reference/exchanges`

### `id`

Trade ID.

Massive warns that uniqueness is scoped to the combination of ticker/exchange/TRF. You should **not treat `id` alone as a universal primary key**. ([Massive][4])

### `participant_timestamp`

Nanosecond UTC timestamp representing when the trade was generated at the exchange.

### `sip_timestamp`

Nanosecond UTC timestamp when the SIP received the trade.

This should be kept independently from participant time. Their difference is useful information:

[
\Delta_{\text{SIP}} =
t_{\text{sip}}-t_{\text{participant}}
]

### `trf_timestamp`

For applicable off-exchange trades, timestamp when the Trade Reporting Facility received the event.

### `sequence_number`

Increasing and unique for a ticker during a trading day/session, but:

* gaps are valid;
* it is not required to be 1,2,3,4...;
* it resets each trading day.

Therefore a gap in sequence numbers is **not by itself evidence of missing data**. ([Massive][4])

### `tape`

* `1` → Tape A → NYSE listed
* `2` → Tape B → NYSE Arca / NYSE American
* `3` → Tape C → Nasdaq listed

### `trf_id`

Identifies the Trade Reporting Facility.

Massive gives a useful dark-pool rule: a trade with `exchange = 4` and a `trf_id` is an off-exchange/dark-pool print. ([Massive][15])

---

# 4. REST pagination for trades

The query supports:

* `timestamp`: date or nanosecond timestamp
* timestamp filter modifiers
* `order`
* `sort`
* `limit`

Maximum page size:

**50,000 trades**

The response returns a `next_url` cursor. ([Massive][4])

Massive's official Python client automatically follows pagination by default. Its own performance recommendation is to use the maximum endpoint page size for large extractions to reduce request count. It also supports the standard comparison modifiers `.gt`, `.gte`, `.lt`, `.lte` where supported. ([GitHub][16])

For one small ticker/day, REST is perfectly reasonable.

For:

**4,824 tickers × ~23 years × millions/billions of individual prints**

REST becomes the wrong physical transport.

---

# 5. Massive already has a better trades interface: Flat Files

The historical stock-trades dataset is:

```text
S3
us_stocks_sip/trades_v1
```

A daily file looks like:

```text
us_stocks_sip/trades_v1/YYYY/MM/YYYY-MM-DD.csv.gz
```

Each daily file contains **all stocks for that trading day**. ([Massive][17])

The documented Flat File trade schema is:

```text
ticker
conditions
correction
exchange
id
participant_timestamp
price
sequence_number
sip_timestamp
size
tape
trf_id
trf_timestamp
```

([Massive][18])

Massive gives a real example where one April 2024 trade file was approximately **1.35 GB compressed and 6.2 GB decompressed**. This tells us that blindly expanding thousands of daily CSVs onto disk would be wasteful; we should stream/filter/convert. ([Massive][18])

The published annual compressed trade files currently add up to roughly **4 TB of whole-market trade history** through 2026 YTD. That is the whole U.S. universe—not merely our 4,824 securities. ([Massive][17])

---

# 6. REST versus Flat Files for the 4,824 stocks

My choice is unambiguous:

| Requirement                     |                REST Trades |            Flat Files |
| ------------------------------- | -------------------------: | --------------------: |
| One ticker                      |                  Excellent |           Inefficient |
| 10 tickers                      |                       Good |               Depends |
| 4,824 tickers                   |                       Poor |         **Excellent** |
| All available history           |   Huge pagination workload | **Designed for this** |
| Exact raw trade fields          |                        Yes |               **Yes** |
| All exchanges/TRFs/dark pools   |                        Yes |               **Yes** |
| Bulk compression                |                  HTTP JSON |          **gzip CSV** |
| Request overhead                |                  Very high |    **One object/day** |
| Auditable source objects        |                   Moderate |         **Excellent** |
| Parallel historical acquisition | Possible but request-heavy |           **Natural** |

Massive itself states that Flat Files are intended for extensive historical downloads and specifically recommends them instead of thousands of REST requests. ([Massive][1])

---

# 7. The 4,824-ticker identity problem must come before trades

I would **not start downloading trades immediately from a file containing 4,824 literal ticker strings**.

First construct:

```text
INSTRUMENT
├── instrument_id
├── cik
├── composite_figi
├── share_class_figi
└── SYMBOL_INTERVALS
        ├── ticker
        ├── valid_from
        ├── valid_to
        ├── source
        └── confidence
```

Why?

Consider:

```text
ABC
↓ ticker change
XYZ
```

If `XYZ` is on our current list and we filter historical Flat Files only for `"XYZ"`, the earlier `"ABC"` history disappears.

We therefore need to combine:

* All Tickers
* inactive/delisted tickers
* historical `date` queries
* CIK
* Composite FIGI
* Share-Class FIGI
* Ticker Events

before declaring the symbol universe complete. ([Massive][6])

Ticker Events is experimental, so I would not make it the sole authority.

---

# 8. Proposed complete download architecture

I would split the acquisition into **seven layers**.

## Layer 0 — Acquisition contracts

Before data:

```text
massive/
├── 00_contracts/
│   ├── provider_version
│   ├── endpoint_catalog
│   ├── schema_catalog
│   ├── plan_entitlements
│   ├── timezone_contract
│   ├── adjustment_contract
│   └── acquisition_manifest
```

Every downloaded dataset should record:

```text
source
endpoint_or_s3_key
request_parameters
retrieved_at_utc
provider_schema_version
provider_response/request_id where applicable
source_file_size
etag/checksum where available
row_count
min_timestamp
max_timestamp
schema_hash
ingestion_version
```

---

## Layer 1 — Identity + dictionaries

Download first:

```text
/v3/reference/tickers
/v3/reference/tickers/{ticker}
/v3/reference/tickers/types
/vX/reference/tickers/{id}/events

/v3/reference/exchanges
/v3/reference/conditions

/v1/marketstatus/upcoming
```

Build the stable 4,824-instrument universe plus historical ticker aliases.

---

## Layer 2 — Raw market history via Flat Files

Massive exposes four Stocks Flat File datasets:

```text
us_stocks_sip/day_aggs_v1
us_stocks_sip/minute_aggs_v1
us_stocks_sip/trades_v1
us_stocks_sip/quotes_v1
```

([Massive][5])

For a **strict complete Massive market-data acquisition**, download all four.

Priority:

```text
1. trades_v1
2. quotes_v1
3. minute_aggs_v1
4. day_aggs_v1
```

Trades and quotes are irreducible raw information.

Aggregates are redundant in theory but valuable as a vendor-supplied validation layer.

---

# 9. How I would physically download the trade files

Do not:

```text
download
→ gunzip into giant CSV
→ filter
→ save
```

Instead:

```text
Massive S3 .csv.gz
    ↓
verified download
    ↓
stream/decompress
    ↓
ticker hash-set filter
    ↓
schema normalization
    ↓
Parquet
    ↓
validation
    ↓
manifest commit
```

The ticker filter should contain **all historical aliases**, not just 4,824 current ticker strings.

Massive's S3-compatible endpoint is:

```text
https://files.massive.com
```

Bucket:

```text
flatfiles
```

and Massive officially supports AWS CLI, Rclone, MinIO and Boto3. ([Massive][1])

For production I would use the S3 API/Boto3 or a high-throughput S3 client rather than manually downloading from the browser.

---

# 10. Parallelism

The unit of parallelization should be the **daily compressed object**, not the ticker.

For example:

```text
Downloader workers
Day A ─┐
Day B ─┼─→ local compressed staging
Day C ─┤
Day D ─┘

Processing workers
.csv.gz
    ↓
decompression
    ↓
filter 4,824 + aliases
    ↓
Parquet
```

Start with perhaps 4–8 simultaneous historical files and dynamically benchmark:

* network saturation
* gzip CPU load
* disk write throughput
* RAM
* Massive S3 response behaviour.

Do not hard-code 50 or 100 concurrent jobs merely because the API pricing says “unlimited calls.”

---

# 11. Correct trade storage schema

I would not store only:

```text
timestamp
price
size
```

That would throw away much of what we are paying Massive for.

Minimum canonical schema:

```text
instrument_id
ticker_as_reported
session_date_et

conditions
correction

exchange
trf_id
tape

trade_id
sequence_number

participant_timestamp_ns
trf_timestamp_ns
sip_timestamp_ns

price
size
decimal_size / normalized_exact_size

source_file
source_row_or_ingestion_id
ingested_at
```

And derived—not replacing original:

```text
participant_datetime_utc
participant_datetime_et

sip_datetime_utc
sip_datetime_et

session ∈ {
PREMARKET,
REGULAR,
AFTERHOURS,
OTHER
}

sip_latency_ns
trf_latency_ns
is_off_exchange
is_dark_pool_candidate
```

The raw nanosecond integers should remain immutable.

---

# 12. Fractional-share schema change

This deserves an explicit schema-version boundary.

Massive announced on **23 February 2026** that fractional-share precision changed across Stocks data:

* REST Trades: `decimal_size`
* WebSocket trades: `ds`
* Flat Files: `size` can now be decimal
* historical Flat Files remain unchanged.

([Massive][14])

Therefore this would be wrong:

```text
size INT64
```

as the sole representation for every historical and future record.

Use an exact decimal representation.

---

# 13. Validation I would require before declaring a trade day PASS

For every downloaded S3 day:

```text
SOURCE FILE
↓
download completed
↓
gzip integrity PASS
↓
expected schema PASS
↓
all input columns retained PASS
↓
ticker filtering completed
↓
output row_count recorded
↓
min/max timestamps recorded
↓
null profile recorded
↓
exchange IDs resolvable
↓
condition IDs resolvable
↓
sequence monotonicity audit
↓
duplicate/correction audit
↓
REST sample reconciliation
↓
aggregate reconciliation
↓
manifest CLOSED_PASS
```

Two important qualifications:

**Sequence gaps must not fail validation**, because Massive explicitly says gaps are legitimate. ([Massive][4])

And raw volume must not be naively compared with OHLC aggregate volume before applying trade-condition eligibility rules, because not every trade necessarily updates every aggregate field. `/v3/reference/conditions` contains the information needed for those interpretations. ([Massive][10])

---

# 14. Remaining historical/non-market datasets

After raw market data:

### Corporate actions

Download all available:

```text
IPOs
splits
dividends
ticker events
```

Do **not** mutate RAW prices after this. Create a separate adjusted layer.

### Fundamentals

Download:

```text
balance sheets
income statements
cash-flow statements
ratios
short interest
short volume
float
```

### SEC

Download the complete relevant records from:

```text
EDGAR index
10-K sections
8-K text
8-K disclosures
13-F
risk factors
Form 3
Form 4
classification taxonomies
```

### News

Download all ticker-associated history exposed by:

```text
/v2/reference/news
```

These can all be ingested using endpoint pagination and ticker/date filters where available. Unlike tick trades, their record counts are manageable enough for REST. ([Massive][3])

---

# 15. What “download absolutely everything” cannot literally mean

There is one important conceptual issue.

Several Massive endpoints produce **parameterized derived data**.

For example:

```text
1-minute bars
2-minute bars
3-minute bars
5-minute bars
...
```

and:

```text
SMA(10)
SMA(20)
SMA(21)
SMA(50)
...
```

So “download every possible response Massive can generate” is not finite.

The scientifically meaningful definition of a **complete Massive archive** should therefore be:

> Download every irreducible source dataset and every finite provider-authored historical record; preserve provider reference/dictionary/corporate/fundamental/filing/news data; separately capture ephemeral/current-state products; derive arbitrary bars and indicators locally.

That gives us **information completeness**, rather than wasting terabytes storing different mathematical transformations of the same data.

---

# 16. Live-only information also exists

Massive's Stocks WebSocket surface currently includes:

```text
WS/stocks/AM      minute aggregates
WS/stocks/A       second aggregates
WS/stocks/T       trades
WS/stocks/Q       quotes
WS/stocks/LULD    Limit Up / Limit Down
WS/stocks/NOI     Net Order Imbalance
WS/business/stocks/FMV
                Fair Market Value
```

([Massive][19])

This matters because **LULD, NOI and FMV are not part of the four historical Stocks Flat File datasets**.

So there are really two meanings of “complete”:

```text
HISTORICAL COMPLETE
REST historical datasets
+ Flat Files
```

versus:

```text
PROVIDER-SURFACE COMPLETE GOING FORWARD
REST
+ Flat Files
+ WebSocket capture
```

For a true future Massive archive, I would add WebSocket capture for information that cannot later be reconstructed from the historical files.

---

# 17. Subscription required

For an individual/non-professional user, the current pricing is roughly:

* Basic: 2 years, no trades/quotes bulk history.
* Starter $29/month: aggregates, but no historical trades.
* Developer $79/month: trades and 10 years of trade history; no historical quotes.
* **Advanced $199/month: 20+ years/all available history, trades, quotes, Flat Files and Financials & Ratios.**

([Massive][20])

For the stated objective—**everything available for all 4,824 instruments**—the relevant individual tier is therefore **Stocks Advanced**.

---

# 18. My proposed acquisition sequence

I would execute it in this exact order:

```text
MASSIVE COMPLETE ACQUISITION
│
├── 00 PROVIDER CONTRACT
│
├── 01 MARKET DICTIONARIES
│   ├── exchanges
│   ├── condition codes
│   ├── ticker types
│   ├── market sessions
│   └── timezone semantics
│
├── 02 SECURITY MASTER
│   ├── all tickers
│   ├── delisted tickers
│   ├── ticker overview
│   └── ticker events
│
├── 03 HISTORICAL IDENTITY RESOLUTION
│   └── 4,824 instruments → all historical symbols
│
├── 04 RAW MARKET DATA
│   ├── trades_v1
│   ├── quotes_v1
│   ├── minute_aggs_v1
│   └── day_aggs_v1
│
├── 05 CORPORATE ACTIONS
│   ├── IPOs
│   ├── splits
│   └── dividends
│
├── 06 FUNDAMENTALS
│   ├── balance sheets
│   ├── income statements
│   ├── cash flows
│   ├── ratios
│   ├── short interest
│   ├── short volume
│   └── float
│
├── 07 SEC
│   ├── EDGAR index
│   ├── 10-K
│   ├── 8-K
│   ├── disclosures
│   ├── risk factors
│   ├── 13-F
│   ├── Form 3
│   └── Form 4
│
├── 08 NEWS
│
├── 09 CURRENT / EPHEMERAL STATE
│   ├── snapshots
│   ├── last trade
│   ├── last quote
│   ├── market status
│   └── upcoming holidays
│
└── 10 LIVE-ONLY CAPTURE
├── LULD
├── NOI
└── other desired WebSocket feeds
```

## Final recommendation

For the **Trades backfill**, I would use:

**Massive Advanced → S3 Flat Files → daily `trades_v1` files → parallel download → filter against 4,824 instruments plus historical aliases → lossless Parquet → exhaustive validation.**

I would **not** use `/v3/trades/{ticker}` to build the 23-year 4,824-symbol master dataset. I would reserve REST Trades for **auditing, isolated repair of missing partitions, small targeted queries and reconciliation**.

For the **complete Massive acquisition**, use a hybrid:

**Flat Files = bulk market history**
**REST = reference + corporate + fundamentals + SEC + short + float + news + current-state products**
**WebSocket = information that exists only live or needs same-day capture.**

That architecture gives us the fastest route without sacrificing even the small fields—exchange IDs, TRF information, condition codes, correction events, fractional quantities, all timestamps, ticker history, session semantics or timezone information.

[1]: https://massive.com/docs/flat-files/quickstart?utm_source=chatgpt.com "Flat Files Quickstart | Massive"
[2]: https://massive.com/docs/rest/quickstart?utm_source=chatgpt.com "REST API Quickstart | Massive"
[3]: https://massive.com/docs/rest/stocks/overview "Overview | Stocks REST API - Massive"
[4]: https://massive.com/docs/rest/stocks/trades-quotes/trades "Trades | Stocks REST API - Massive"
[5]: https://massive.com/docs/flat-files/stocks/overview?assetClass=stocks&license=personal&name=stocks_basic&utm_source=chatgpt.com "Overview | Stocks Flat Files - Massive"
[6]: https://massive.com/docs/rest/stocks/tickers/all-tickers "All Tickers | Stocks REST API - Massive"
[7]: https://massive.com/docs/rest/stocks/tickers/ticker-overview?auth=login&utm_source=chatgpt.com "Overview | Stocks REST API - Massive"
[8]: https://massive.com/docs/rest/stocks/tickers/ticker-overview "Overview | Stocks REST API - Massive"
[9]: https://massive.com/docs/rest/stocks/market-operations/exchanges "Exchanges | Stocks REST API - Massive"
[10]: https://massive.com/docs/rest/stocks/market-operations/condition-codes "Condition Codes | Stocks REST API - Massive"
[11]: https://massive.com/docs/rest/stocks/market-operations/market-holidays "Market Holidays | Stocks REST API - Massive"
[12]: https://massive.com/docs/rest/stocks/news?utm_source=chatgpt.com "News | Stocks REST API - Massive"
[13]: https://massive.com/knowledge-base/categories/trades?utm_source=chatgpt.com "Trades FAQs | Massive"
[14]: https://massive.com/changelog?utm_source=chatgpt.com "Changelog | Massive"
[15]: https://massive.com/knowledge-base/article/does-polygon-offer-dark-pool-data?utm_source=chatgpt.com "Does Massive offer dark pool data? | Massive"
[16]: https://github.com/massive-com/client-python?utm_source=chatgpt.com "GitHub - massive-com/client-python: The official Python client library for the Massive.com REST and WebSocket API. · GitHub"
[17]: https://massive.com/docs/flat-files/stocks/trades "Trades | Stocks Flat Files - Massive"
[18]: https://massive.com/blog/insights-from-trade-level-data?utm_source=chatgpt.com "Deep Dive into Trade-Level Data with Flat Files | Massive"
[19]: https://massive.com/docs/websocket/stocks/overview "Overview | Stocks WebSocket - Massive"
[20]: https://massive.com/pricing?utm_source=chatgpt.com "Pricing | Massive"




## Float de Massive

Sí. El otro agente tiene razón en la ubicación: Massive coloca Float dentro de Fundamentals.

Endpoint:

GET /stocks/vX/float

Campos:

ticker
effective_date
free_float
free_float_percent

Pero la respuesta importante es: Massive solo documenta el último free float disponible. El endpoint es experimental,
se actualiza cuando es necesario y su documentación dice expresamente que el histórico “no aplica”. No admite un
parámetro de fecha histórica. Massive Float (https://massive.com/docs/rest/stocks/fundamentals/float).

Por tanto:

Massive Float ≠ float anual 2005–2026
No como familia explícita de Massive Float.
-----


Sí, Massive puede ayudarnos bastante, pero no debe sustituir el pipeline SEC que ya hemos construido. El otro agente acierta en que Massive tiene una nueva capa EDGAR muy interesante, pero decir que “tiene los documentos que descargamos” es impreciso.

La arquitectura correcta sería:

```text
SEC EDGAR primary documents
= evidencia autoritativa

Massive EDGAR/ownership
= descubrimiento + extracción estructurada
  + reconciliación + reparación selectiva
```

## Qué ofrece realmente Massive

### 1. EDGAR Index: muy útil

```text
GET /stocks/filings/vX/index
```

Devuelve:

```text
CIK
ticker
form_type
filing_date
accession_number
issuer_name
filing_url de SEC
```

Es un índice de descubrimiento que enlaza al documento original en SEC.gov; no debemos asumir que entrega una copia íntegra de cada filing. Massive lo considera todavía early-access beta. [Massive EDGAR Index](https://massive.com/docs/rest/stocks/filings/index)

Para TSIS puede servir para:

- auditar si nuestro inventario SEC omitió accessions;
- localizar documentos históricos faltantes;
- comprobar familias de amendments;
- descubrir forms relevantes sin repetir tanto trabajo de metadata;
- reparar selectivamente huecos;
- comparar `SEC submissions → Massive index`.

Esto podría mejorar especialmente:

```text
OWNERSHIP_BASELINE_UNAVAILABLE
BASELINE_DOCUMENT_PARTIAL
AMENDMENT_FAMILY_UNRESOLVED
SHARES_OUTSTANDING_UNAVAILABLE
```

Pero no resolverá automáticamente la clase del instrumento.

## 2. Forms 3 y 4 estructurados: probablemente lo más útil para nuestro float

Massive devuelve campos que actualmente extraemos y reconciliamos nosotros:

```text
accession
issuer_cik
owner_cik
owner_name
security_title
security_type
direct_or_indirect
nature_of_ownership
shares_owned
shares_owned_following_transaction
transaction_shares
transaction_code
underlying_security_shares
roles
footnotes
filing_date
period_of_report
```

También diferencia derivados y no derivados, amendments y posiciones directas/indirectas. [Massive Form 3](https://massive.com/docs/rest/stocks/filings/form-3), [Massive Form 4](https://massive.com/docs/rest/stocks/filings/form-4)

Esto puede ayudarnos a:

- reducir fallos de parsing XML/HTML;
- identificar options frente a issued common shares;
- reconstruir eventos posteriores al baseline;
- enlazar al owner mediante `owner_cik`;
- detectar direct/indirect ownership;
- contrastar nuestras extracciones;
- reenviar únicamente discrepancias a revisión del filing original.

Afectaría potencialmente a:

```text
POST_BASELINE_EVENT_IDENTITY_OR_DATE_UNRESOLVED
HOLDER_OVERLAP_UNRESOLVED
ECONOMIC_POSITION_OVERLAP_UNRESOLVED
```

Pero no podemos sumar esos registros directamente. Sigue siendo obligatorio reconciliar:

```text
common vs derivative
direct vs indirect
transferencias internas
entidades controladas
amendments
posición económica única
share class
```

Como fija nuestro contrato:

```text
FORM_4_TRANSACTION_SIZE
!=
AUTOMATIC_FLOAT_DELTA
```

## 3. 13F: sí puede cerrar G12 mucho más deprisa

Esta es posiblemente la aportación más valiosa.

Massive ofrece filas estructuradas con:

```text
filer_cik
accession
filing_date
period
CUSIP
title_of_class
shares
value
put_call
investment_discretion
other_managers
voting_authority
form_type 13F-HR / 13F-HR/A
```

[Massive 13-F](https://massive.com/docs/rest/stocks/filings/13-f-filings)

Esto encaja casi exactamente con el pipeline global que habíamos diseñado:

```text
adquisición global 13F
→ CUSIP histórico
→ amendments
→ deduplicación de managers
→ eligible_from_session
→ posiciones trimestrales
```

Podría evitarnos descargar y parsear manualmente miles de information tables como primera ruta.

Aun necesitaríamos:

- medir desde qué fecha tiene cobertura;
- comprobar completitud contra SEC;
- resolver amendments;
- deduplicar managers y `other_managers`;
- diferenciar acciones, principal y put/call;
- enlazar CUSIP histórico con nuestros instrumentos;
- aplicar la fecha de publicación, no retrospectivamente el quarter end.

Los documentos de Massive no fijan claramente en la página una fecha inicial garantizada para toda esta familia. Antes de confiar en ella debemos medir cobertura real.

## 4. Massive Float: útil como benchmark, no como fuente PIT

El endpoint:

```text
GET /stocks/vX/float
```

solo proporciona el último float:

```text
ticker
effective_date
free_float
free_float_percent
```

Es experimental y la definición incluye insiders, founders, afiliados, restricciones y holders del 5% o más. [Massive Float](https://massive.com/docs/rest/stocks/fundamentals/float)

Por tanto:

```text
Massive Float
!=
float histórico 2005–2026

effective_date
!= necesariamente available_at demostrado

vendor free float
!= nuestra metodología explícita
```

Lo usaría para:

```text
validación externa actual
comparación metodológica
detección de outliers
priorización de auditorías
```

No para rellenar sesiones históricas ni para sustituir `NULL` de TSIS.

## Qué no resuelve Massive

### Share class

Los endpoints pueden devolver:

```text
tickers = ["ABC", "ABC.A"]
security_title = "Common Stock"
```

pero eso no demuestra por sí solo que una posición pertenezca al instrumento exacto de nuestro `share_class_figi`.

Massive puede aportar evidencia candidata, pero no cerrar automáticamente:

```text
SHARE_CLASS_ALLOCATION_UNRESOLVED
```

La resolución seguirá necesitando:

```text
instrument ledger
+ historical security title
+ CUSIP
+ accession
+ class-specific filing evidence
```

### Instrument interval

El ticker de Massive tampoco debe aplicarse retrospectivamente sin control. Su documentación reconoce incluso que algunas consultas históricas de ticker details pueden mostrar información usando `period_of_report`, aunque el filing se presentara después. Esto no es seguro para PIT. [Massive Ticker Overview](https://massive.com/docs/rest/stocks/tickers/ticker-overview)

Por tanto, Massive no puede reemplazar nuestro:

```text
CIK
+ FIGI/share-class FIGI
+ ticker interval
+ CUSIP interval
+ lifecycle reconciliation
```

### Disponibilidad PIT

Muchos endpoints ofrecen:

```text
filing_date
period_of_report
```

pero nuestro sistema necesita:

```text
accepted_at
public_dissemination_at/state
eligible_from_session
```

Para determinarlo, tendremos que conservar el accession y volver al documento/metadata SEC original.

## Tampoco cubre todo nuestro corpus mediante endpoints estructurados

Massive ofrece parsing específico para:

```text
10-K
8-K
Form 3
Form 4
13F
risk factors
```

Pero nuestro owner-exclusion depende también de:

```text
DEF 14A
10-Q
20-F / 20-F/A
SC 13D/G y amendments
Forms 5
S-1 / F-1
424B*
selling-stockholder tables
registration statements
exhibits
```

El EDGAR Index puede descubrirlos, pero no existe en la lista presentada un endpoint estructurado especializado para todos ellos.

Por eso no sustituye nuestro selector ni nuestro parser general.

## Mi recomendación concreta

No abandonaría ni reiniciaría el trabajo actual. Tampoco esperaría hasta haber descargado todo para probar Massive.

Añadiría ahora una lane acotada:

```text
MASSIVE SEC RECONCILIATION PROBE
```

Con los mismos 100 casos y sin modificar resultados:

1. Descargar desde Massive el EDGAR Index de los 99 casos.
2. Compararlo por `CIK + accession + form + filing_date`.
3. Medir accessions:

```text
SEC_ONLY
MASSIVE_ONLY
BOTH_EXACT
METADATA_CONFLICT
```

4. Descargar Forms 3/4 estructurados para esos casos.
5. Compararlos con nuestros eventos normalizados.
6. Probar 13F global sobre una ventana pequeña y varios CUSIP históricos.
7. Consultar Massive Float para los casos calculados como benchmark externo.
8. No permitir todavía que Massive cambie un `NULL` por un número.
9. Auditar cobertura histórica, amendments, fechas y términos de almacenamiento/licencia.
10. Solo después decidir qué campos pueden convertirse en evidencia secundaria admitida.

## Prioridad que le daría

| Fuente Massive | Utilidad para TSIS | Rol |
|---|---:|---|
| EDGAR Index | Alta | Descubrimiento y auditoría de completitud |
| Form 3 | Alta | Baseline insider estructurado |
| Form 4 | Muy alta | Eventos posteriores y reconciliación |
| 13F | Muy alta | Implementar G12 global |
| Float actual | Media | Benchmark externo |
| 10-K sections | Media | Reparación/extracción auxiliar |
| 8-K text | Media | Eventos de capital auxiliares |
| Risk factors | Baja para float | Otro Information Object |

## Veredicto

```text
¿Debemos seguir con SEC primary?             SÍ
¿Massive puede mejorar el proceso?           SÍ, bastante
¿Debe reemplazar nuestros documentos SEC?    NO
¿Puede reducir parsing y descargas?           SÍ
¿Puede ayudar a G12/13F?                      MUCHO
¿Puede rellenar float histórico directamente? NO
¿Puede resolver clase/intervalo por sí solo?  NO
```

Mi elección sería:

```text
SEC primary documents
        = source of truth

Massive EDGAR index
        = discovery/completeness lane

Massive Forms 3/4/13F
        = structured secondary evidence
          + parser reconciliation

Massive latest float
        = external benchmark only
```

No cambiaría el camino hacia los 4.824. Añadiría Massive como acelerador y control de calidad antes de autorizar la adquisición primaria de cada cohorte. Eso puede reducir descargas innecesarias y, sobre todo, darnos una vía bastante más rápida para Forms 3/4 y G12, sin sacrificar causalidad ni auditabilidad.