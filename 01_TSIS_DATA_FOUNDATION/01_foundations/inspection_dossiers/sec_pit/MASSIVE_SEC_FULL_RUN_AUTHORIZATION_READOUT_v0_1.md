# Massive SEC full-run authorization readout v0.1

Status: **NOT_AUTHORIZED**

A full run is prohibited until:

1. written license/retention evidence is confirmed;
2. the 250-case production-equivalent probe is COMPLETE;
3. offline artifact audit passes;
4. endpoint schema/value/coverage audit passes;
5. storage/time projection fits the 200 GiB reserve;
6. worker/rate settings are frozen in a new hash-bound config if changed;
7. a human creates a separate authorization with
   authorization_scope=FULL_AFTER_PROBE_PASS;
8. that authorization binds the exact 4,824 cases, 4,288 CIKs, direct endpoint
   IDs, config, objective, target manifest/data and executable bundle hashes.

No full authorization file exists at preparation close. The probe template
cannot authorize FULL execution.
