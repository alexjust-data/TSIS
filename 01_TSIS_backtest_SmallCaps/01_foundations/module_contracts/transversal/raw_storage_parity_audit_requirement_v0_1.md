# RAW Storage Parity Audit Requirement v0.1

## Purpose

This contract defines the final Data Foundation audit required to close the
legacy `D:/` raw data storage state.

The target rule is:

```text
Every raw/source-preserved folder that remains relevant under D:/ must have an
equivalent governed landing under E:/TSIS/data before the data layer can be
treated as operationally converged.
```

This is a final storage and lineage audit. It is separate from per-family data
quality certification. A folder can be byte-identical and still have quality
issues; parity only proves that the physical raw evidence was preserved during
landing or migration.

## Authority Rule

The official TSIS market-data database root is:

```text
E:/TSIS/data
```

Legacy paths such as `D:/...` and `C:/TSIS_Data/data/...` can remain as
provenance, recovery or historical-audit paths, but new downstream contracts
must not use them as primary roots unless an explicit exception is documented.

## Minimum D-to-E Scope

The final parity audit must cover, at minimum, every relevant raw/source folder
observed under `D:/` that has or should have an `E:/TSIS/data` landing.

Initial required family map:

| Legacy/source root | E landing root | Status requirement |
| --- | --- | --- |
| `D:/quotes` | `E:/TSIS/data/quotes_` staging first; promoted root only after audit | Must be equivalent before any promotion or merge decision |
| `D:/trades_ticks_prod_2005_2026` | `E:/TSIS/data/trades_ticks_prod_2005_2026` | Must be equivalent or explicitly reconciled |
| `D:/ohlcv_daily` | `E:/TSIS/data/ohlcv_daily` | Must be equivalent or explicitly reconciled |
| `D:/ohlcv_1m` | `E:/TSIS/data/ohlcv_1m` | Must be equivalent or explicitly reconciled |
| `D:/Halts` | `E:/TSIS/data/Halts` | Must be equivalent or explicitly reconciled |
| `D:/reference` | `E:/TSIS/data/reference` | Must be equivalent or explicitly reconciled |
| `D:/financial` | `E:/TSIS/data/financial` | Must be equivalent or explicitly reconciled |
| `D:/regime_indicators` | `E:/TSIS/data/regime_indicators` | Must be equivalent or explicitly reconciled |

If another raw/source-preserved folder is found under `D:/`, the auditor must
add it to this map or document why it is out of scope.

## Definition Of Equivalent

For this audit, equivalent means:

- same relative file paths, unless a documented path normalization rule exists;
- same file count;
- same total bytes;
- same per-file byte length;
- same per-file content hash for every file, or an explicit temporary deferral
  that blocks promotion until full hashing is complete;
- no missing source files;
- no unexplained target-only files;
- no robocopy or filesystem errors left unresolved.

Directory timestamps are not a sufficient equivalence proof.

## Required Evidence

Each family audit must produce:

- source root;
- target root;
- run id;
- auditor version or script path;
- file count source vs target;
- byte count source vs target;
- missing-in-target list;
- target-only list;
- size mismatch list;
- hash mismatch list when hashing is enabled;
- final verdict;
- date/time;
- operator or agent;
- notes for any exception.

Heavy manifests should live under a governed data-ops manifest root, for
example:

```text
E:/TSIS/data/data_ops_manifests/raw_storage_parity/
```

Repository documentation must keep the compact summary and the promotion
decision, not millions of per-file rows.

## Verdicts

Allowed verdicts:

```text
parity_pass
parity_fail_missing_files
parity_fail_extra_files
parity_fail_size_mismatch
parity_fail_hash_mismatch
parity_deferred_hashing
parity_out_of_scope_documented
```

`parity_deferred_hashing` is not a pass. It exists only so long-running audits
can be resumed without pretending completion.

## Promotion Rule

No raw/source-preserved `E:/TSIS/data` family may be represented as fully
converged from `D:/` until its parity verdict is `parity_pass` or a documented
exception has been approved in the relevant family contract and changelog.

For `quotes`, the current staging target:

```text
E:/TSIS/data/quotes_
```

is not the official root. It is a staging location used to recover and inspect
the `D:/quotes` tree without mutating:

```text
E:/TSIS/data/quotes
```

Only a later promotion decision can decide whether `quotes_` is merged,
renamed, discarded or used to build a new candidate quotes root.

## Relationship To Data Quality

Storage parity is not data quality.

The final Data Foundation closeout requires both:

```text
physical parity / preservation evidence
```

and:

```text
family-level data quality audit and consumption policy
```

A family that passes storage parity can still remain blocked, scoped, review
only, or unsuitable for a downstream table if its data quality policy says so.
