# Events Are Discovered, Not Assumed

Fecha: 2026-07-05
Estado: principle_initial

## Tesis

TSIS no parte de eventos oficiales.

TSIS parte de experimentos para descubrir fenomenos repetibles.

## Regla

```text
sampling probe != event validated
sampling window != window validated
scanner candidate != causal signal
strategy setup != market phenomenon
```

## Ejemplo

```text
+50% intradia
```

Lectura correcta:

```text
sampling_probe_human_seed
```

No:

```text
evento oficial
edge
estrategia
threshold optimo
```

```text
pre_event_30m / post_event_30m
```

Lectura correcta:

```text
sampling_window_controlled_seed
```

No:

```text
ventana demostrada estadisticamente
```

## Flujo Correcto

```text
sampling_probe
-> parameter_sweep
-> exploratory_statistics
-> event_family_candidate
-> validation_protocol
-> validated_event_definition
-> operational_component
```
