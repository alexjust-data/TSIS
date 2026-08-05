# BT-GATE-015 Owner Review Correction Diff

```text
BASE_CONTRACT_RAW_SHA256 = 4c9560b24e3c7a9f30f917accde8326c50cbb2ac1b1f8f2588e0bd9fa7b0f552
CORRECTED_CONTRACT_RAW_SHA256 = 94fd027e4c7571f2c38327d7050935fbb3d13d6aed8df6824c46c34ad53adba2
BASE_CONTRACT_LF_NORMALIZED_SHA256 = 638a37a0a014d143f4d3e30d8fc00ce972c7965631d01365aa0b771a612b9295
CORRECTED_CONTRACT_LF_NORMALIZED_SHA256 = 497e92fc0ce31c86d66f88beec44ed0ed831d1cf0459c6d29496cb26bf0bb70f
COMPARISON_FORMAT = unified diff
COMPARISON_NORMALIZATION = UTF-8 bytes, CRLF normalized to LF
```

```diff
--- BASE/20_BT_GATE_015_POINT_IN_TIME_EVENT_STATE_CONSUMER_CONTRACT_V0_1.md
+++ CORRECTED/20_BT_GATE_015_POINT_IN_TIME_EVENT_STATE_CONSUMER_CONTRACT_V0_1.md
@@ -4,7 +4,7 @@
 
 ```text
 BT-GATE-015 = NOT_OPEN
-CONTRACT_STATUS = CORRECTED_READY_PENDING_OWNER_REVIEW
+CONTRACT_STATUS = CONTRACT_CORRECTED_PENDING_FINAL_OWNER_CONFIRMATION
 CONTRACT_OWNER_REVIEW = NOT_STARTED
 BT-GATE-015_IMPLEMENTATION = NOT_AUTHORIZED
 EVENT_STATE_PHYSICAL_READ = NOT_AUTHORIZED
@@ -110,7 +110,13 @@
 2021-01-19T14:30:00Z
 
 window_definition_id =
+session_opened_at_anchor_context_v0_1
+
+historical_window_definition_id =
 event_window_definition:market_data:session_opened:at_open_v0_1
+
+historical_window_definition_role =
+HISTORICAL_PROVIDER_PROVENANCE_ONLY
 ```
 
 Selection is based on operational coverage and existing governed evidence, not
@@ -134,7 +140,6 @@
 market_state_state_output_fingerprint =
 9430c9903b6172c9183e8cce264bfdfcb0da83d391becc05eb7ef56f11509685
 
-event_state_record_ordinal = 1
 
 event_state_record_id =
 e71cad82e71783bbc50ebb8df1e44e2f9118dd4843c3cb4f0fbf2ee5a2a8ca76
@@ -148,15 +153,54 @@
 market_state_availability_evidence_dataset_fingerprint =
 516a27d0f8f53762fbd8e7be151c84577544c056b093b859ab1fbce45dbac416
 
-cross_dataset_binding =
+market_state_cross_dataset_binding =
 EXACT_ROW_ID_AND_FINGERPRINT_EQUIVALENCE
 ```
 
 Missing, empty, duplicate or conflicting identities must fail closed.
 
 The identities from the first handoff (`47102c58...`, `4ab9bda...`,
-`0061ac40...`, `793fc860...`, `5bbdbfdb...`, `ab048da6...`) are
-`HISTORICAL_PROVIDER_PROVENANCE_ONLY` and must never select runtime content.
+`0061ac40...`, `793fc860...`, `5bbdbfdb...`, `ab048da6...`) and its
+`event_state_record_ordinal = 1` are
+`HISTORICAL_PROVIDER_PROVENANCE_ONLY`. They must never select runtime content
+or be asserted for the executable `e71cad...` row.
+
+### 5.1 Physical row to sidecar join
+
+The future bounded consumer must establish a complete 1:1 bijection before
+constructing an event:
+
+| Physical Event State field | Sidecar or consumer field |
+|---|---|
+| `state_output_fingerprint` | `event_state_record_fingerprint` |
+| `event_state_instrument_session_projection_id` | `instrument_projection_id` |
+| `consumption_legality` | `state_replay_consumption_legality` |
+| parsed `restriction_codes_json` | `event_state_provenance_restriction_codes` |
+| `source_market_state_value_snapshot_json` | closed 17-field scientific payload |
+
+The exact Market State dependency fingerprint is sourced from the governed
+Market State replay-availability sidecar row:
+
+```text
+Market State sidecar field = state_output_fingerprint
+Event State sidecar field = market_state_state_output_fingerprint
+required relation = exact equality
+```
+
+Join cardinality is exactly one physical row to exactly one sidecar record.
+Missing rows, orphan sidecars, duplicate keys, reused sidecars or conflicting
+values fail closed.
+
+`source_market_state_value_snapshot_json` is hashed as the exact original
+UTF-8 byte sequence before parsing:
+
+```text
+source_market_state_value_snapshot_sha256 =
+SHA256(original UTF-8 bytes)
+```
+
+The original bytes and hash remain audit lineage. Parsing, normalization or
+re-serialization must not replace the original-byte hash.
 
 ## 6. Provider Authorities
 
@@ -195,6 +239,9 @@
 
 replay availability sidecar manifest =
 fded92d3f213f926cae9024a6aa31379c87e4485ac25afd51ea30ac848eec8f6
+
+replay availability sidecar schema =
+7d814dcb50fdd9b0da604e4f443497f3b733082070ccc2ed8ff89293e773ad77
 
 typed payload binding =
 320fc3e9dfb532aad0e12a48af6117d50a214642b2b827a4628265808d4d3d43
@@ -222,8 +269,28 @@
 physical schema/fingerprint validation = PROVEN
 ```
 
-The provider reports 36 validation cases with zero failures and no physical
-read by the handoff preparation.
+The evidence chronology is:
+
+```text
+initial contract handoff:
+validation = 36/36 PASS
+provider physical files opened = 0
+provider physical rows read = 0
+
+provider completion:
+validation = 52/52 PASS
+provider candidate files opened = 1
+provider candidate rows scanned = 8
+provider candidate rows selected = 1
+Market State Parquet opened = false
+
+backtester consumer:
+Event State physical files opened = 0
+Event State physical rows read = 0
+```
+
+The provider completion read is immutable provider evidence. It is not a
+backtester consumer read and does not authorize one.
 
 ## 8. Provider Evidence Closure
 
@@ -404,21 +471,11 @@
 
 ## 13. Restriction Domains
 
-The consumer must preserve separate domains:
+The bounded provider sidecar materializes exactly two row-level domains:
 
 ```text
 event_state_provenance_restriction_codes
-event_state_replay_consumption_restriction_codes
-component_replay_restriction_codes
-```
-
-Components include:
-
-```text
-Event Instance
-Event Window
-Instrument Projection
-Market State dependency
+replay_consumption_restriction_codes
 ```
 
 The exact bounded replay-consumption restrictions are:
@@ -431,10 +488,32 @@
 research_only
 ```
 
-Provenance restrictions remain audit lineage. Replay restrictions govern
-delivery. Component restrictions must be labelled and cannot be weakened,
-discarded or silently converted into another domain.
-
+Provenance restrictions remain immutable audit lineage. Replay-consumption
+restrictions govern delivery and must match the frozen sidecar exactly as a
+closed set: duplicates, omissions and additions fail closed.
+
+The provider architecture describes a possible third domain:
+
+```text
+component_replay_restriction_codes
+```
+
+However, the accepted bounded sidecar does not materialize row-addressable
+values for Event Instance, Event Window, Instrument Projection and Market
+State components. Therefore:
+
+```text
+component_replay_restriction_codes =
+NOT_MATERIALIZED_NOT_AUTHORIZED_IN_V0_1
+
+implicit union or inference =
+PROHIBITED
+```
+
+V0.1 may validate component identities, timestamps and the row-level
+`research_only` legality already proven, but it must not claim component-level
+restriction propagation. Introducing that capability requires a separate
+provider binding and owner-approved contract correction.
 ## 14. Fail-Closed Conditions
 
 At minimum:
@@ -449,6 +528,7 @@
 FAIL_EVENT_STATE_TEMPORAL_AVAILABILITY_VIOLATION
 FAIL_EVENT_STATE_PAYLOAD_CONTRACT_MISSING
 FAIL_EVENT_STATE_RESTRICTION_DOMAIN_MISMATCH
+FAIL_EVENT_STATE_COMPONENT_RESTRICTIONS_NOT_AUTHORIZED
 FAIL_EVENT_STATE_EARLY_STORE_INSERT
 FAIL_DUPLICATE_EVENT_STATE_EVENT
 FAIL_CONFLICTING_EVENT_STATE_EVENT
@@ -507,7 +587,7 @@
 availability-sidecar validation
 payload-contract validation
 identity and fingerprint report
-restriction-domain report
+two-domain restriction report
 state-aware event sequence
 EventStateStore trace
 bounded probe observations
@@ -541,7 +621,7 @@
 
 ```text
 BT-GATE-015 = NOT_OPEN
-CONTRACT_STATUS = CORRECTED_READY_PENDING_OWNER_REVIEW
+CONTRACT_STATUS = CONTRACT_CORRECTED_PENDING_FINAL_OWNER_CONFIRMATION
 CONTRACT_OWNER_REVIEW = NOT_STARTED
 BT-GATE-015_IMPLEMENTATION = NOT_AUTHORIZED
 EVENT_STATE_PHYSICAL_READ = NOT_AUTHORIZED
```
