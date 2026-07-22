# LOCAL_RULES - 02_TSIS_BACKTEST_ENGINE

This module owns future backtest engine implementation, not Data Foundation governance.

Rules:

- consume certified or explicitly restricted Data Foundation outputs;
- never bypass `01_TSIS_DATA_FOUNDATION/01_foundations` contracts;
- never assume raw 1m bars are corrected in place;
- declare price view, corporate-action semantics and fill model in every run;
- preserve deterministic event ordering and run manifests;
- keep architecture/theory decisions in `00_CTO/14_BACKTEST_ENGINE` until promoted.