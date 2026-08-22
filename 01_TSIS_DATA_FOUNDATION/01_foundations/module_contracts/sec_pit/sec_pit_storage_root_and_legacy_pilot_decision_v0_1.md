# SEC PIT Storage Root And Legacy Pilot Decision `v0_1`

Date: `2026-08-14`

Status: `ACTIVE_OPERATIONAL_CONTRACT`

## Role

Resolve the apparent conflict between the original SEC float pilot root and
the governed SEC PIT content-addressed store before cohort `C01_0824` starts.
This decision controls new writes; it does not rewrite historical manifests.

## Binding root decision

There is one active SEC PIT v0.1 repository for every new metadata or primary
acquisition:

```text
active SEC root:   D:/TSIS/fundamental_context/sec_pit_v0_1
active object CAS: D:/TSIS/fundamental_context/sec_pit_v0_1/objects
```

The earlier path is frozen as immutable pilot provenance:

```text
legacy pilot root: D:/sec_float_pit_v0_1
state:             IMMUTABLE_READ_ONLY_PROVENANCE_NO_NEW_WRITES
```

No active runner may write new data, resumes, manifests or derived outputs to
the legacy pilot root. `run_submissions_metadata_profile.py` enforces the exact
active object root and fails before network access if another path is supplied.

## Physical evidence behind the decision

Read-only inventory on `2026-08-14`:

| Root | Role | Files | Physical bytes |
|---|---|---:|---:|
| `D:/sec_float_pit_v0_1` | closed 50-CIK pilot provenance | 22,783 | 28,682,785,827 |
| `D:/TSIS/fundamental_context/sec_pit_v0_1` | active governed SEC PIT root | 8,084 | 145,008,137 |
| active `objects/` subtree | SHA-256 content-addressed objects | 6,613 | 104,546,277 |

The legacy pilot manifest records `11,321` inventory rows, `22,642` primary
plus complete-submission resources and `28,516,711,055` acquired bytes for 50
CIKs. It is not a partially populated copy of the active CAS: it is a prior
layout with raw logical files and independent manifests.

## Migration rule

The migration decision is semantic, not a blind physical copy:

1. all new writes go only to the active CAS;
2. historical legacy manifests remain immutable provenance;
3. legacy payloads may be reused only through a future audited importer that
   verifies source bytes, computes SHA-256, deduplicates into the CAS and emits
   a source-to-object migration manifest;
4. no direct folder merge, move, rename or deletion is authorized here;
5. until that importer exists, the legacy tree is excluded from resume and
   active acquisition counts.

This prevents two active writers while preserving the expensive historical
evidence. It also makes potential legacy-versus-CAS duplication visible rather
than pretending the two layouts are already equivalent.

## Cohort 01 effect

`C01_0824` metadata is authorized to write SEC submissions root and supplements
only to the active CAS. Primary documents and complete submissions remain
`NOT_AUTHORIZED`.

The post-metadata gate must report:

- exact `824/824` completeness;
- requests, retries, HTTP 429 and failures;
- reused identity, cross-CIK and lifecycle review counts;
- the document set selected by `sec_pit_predownload_control_v0_2`;
- filing-size upper-bound P50/P95/MAX and a full-universe projection;
- pre-XBRL proxy and the fact that fallback frequency is not certifiable before
  primary requests occur.

## Primary storage hard-stop

Every later primary run must use:

```text
minimum_free_space_gib = 200
```

The runner checks at start and before every document. Crossing the threshold
must produce `STOPPED_LOW_DISK`, `final_manifest.json`, terminal heartbeat/PID
state and exact `--resume` instructions. A low-disk stop cannot authorize
another cohort or institutional promotion.

## Allowed and prohibited consumers

Allowed:

- human-launched `C01_0824` submissions metadata;
- network-free post-metadata selection and capacity audit;
- read-only legacy forensic comparison.

Prohibited:

- new writes to `D:/sec_float_pit_v0_1`;
- primary acquisition without a new hash-bound human authorization;
- automatic cohort 02-05 scale-out;
- treating the C01 storage projection as historically representative;
- deleting or silently importing the legacy pilot.

