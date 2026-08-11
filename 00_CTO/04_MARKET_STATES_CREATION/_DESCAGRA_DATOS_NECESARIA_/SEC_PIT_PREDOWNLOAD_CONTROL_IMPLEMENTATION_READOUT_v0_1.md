# SEC PIT Predownload Control Implementation Readout `v0_1`

Date: 2026-08-11
Status: `IMPLEMENTED_AND_SEVEN_CASE_PROBE_PASS_DOWNLOAD_NOT_AUTHORIZED`

The defects identified in the document-selection audit now have an executable,
fail-closed control path:

- universe authority is `lt1b_universe_v0_1`, not `instrument_master`;
- instrument master is only the target identity projection;
- source intervals remain separate and comparable;
- accession metadata never proves ticker/security class by CIK alone;
- 8-K and 6-K no longer receive blanket O/S/restriction roles;
- the fixed newest-first 300 cap is rejected;
- required evidence exceeding capacity fails explicitly;
- issuer prehistory and post-window evidence receive explicit states;
- CNOBP halts before primary acquisition;
- the old broad coordinator is blocked;
- the new acquisition path is hash-authorized and resume-safe.

The seven-case offline probe passed its expected behavior, but neither the six
eligible primary-document downloads nor scale-out to 4,824 tickers is authorized
by this readout. The next human/governed decision is whether to authorize the
exact six-ticker selection hashes for a bounded physical replay.

G8 and G12 remain separate downstream acquisition/resolution problems. G8 may
emit conservative estimates or unavailable states, never exact freely tradable
supply without exercise/release/legend evidence. G12 requires the global 13F
manager information-table lane already recorded in the dedicated plan.
