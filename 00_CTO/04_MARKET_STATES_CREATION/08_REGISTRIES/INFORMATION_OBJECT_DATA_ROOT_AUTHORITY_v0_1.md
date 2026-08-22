# Information Object Data Root Authority v0.1

`D:/TSIS/IO` is the active physical authority for all
experimental and canonical Information Object and Representation Model data.

Upstream raw and governed Data Foundation sources remain at their existing
authoritative roots, including `G:/TSIS/data`.

Required hierarchy:

```text
representation_profile_id/
  information_object_id/
    representation_model_id/
      binding_id/
        runs/run_id=<run_id>/
```

This root includes Binding A/B/C development data, temporal OOS data,
comparisons, future admitted full-history representations, manifests,
validation and lineage.

Rules:

1. New representation runs must not write heavy outputs to `G:/TSIS/data`.
2. Experimental and canonical datasets require different governed identities.
3. Existing outputs on `G:` remain historical evidence until explicit disposal.
4. Binding B should store incremental dimensions when composition with A is
   semantically valid, avoiding unnecessary duplication.
5. Backtests consume admitted versioned representations; they do not rebuild
   raw-event windows on every request.

Active Trading Activity root:

```text
D:/TSIS/IO/
  wake_up/
    trading_activity/
      pit_multiscale_marked_activity/
        binding_a_v0_2/
```

Current authorization:

```text
Binding A v0.2 experimental writes = AUTHORIZED
canonical promotion                = NOT_AUTHORIZED
full-history materialization       = NOT_AUTHORIZED
```


Physical directories may use governed short aliases to remain below Windows path limits; full profile, object, model, binding and run IDs remain mandatory inside manifests.
