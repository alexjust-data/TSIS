# SEC PIT Predownload Control Validators `v0_2`

Required hard gates:

- exactly one universe row per requested ticker;
- exactly one target instrument row when the runner is ticker-scoped;
- universe source ID and paths match the governed config;
- preferred/depositary names cannot pass as common stock;
- every accession preserves CIK, accession, filing/acceptance date and URL;
- CIK-only linkage cannot emit a proven security-class match;
- temporal state is one of target, opening prehistory, post-window or review;
- Item 2.02-only 8-K has no automatic O/S/restriction role;
- 6-K has only a content-probe role before extraction;
- required evidence count above capacity fails closed;
- external authorization hashes match the exact probe and plan;
- authorized tickers are a subset of technical class-pass tickers;
- resume skips only prior `FETCHED` rows with a non-null SHA-256;
- parent-universe execution remains unauthorized until a separate full-scope probe.

The versioned seven-case probe must retain six class passes and one expected
CNOBP class halt. Any different result invalidates the probe.
