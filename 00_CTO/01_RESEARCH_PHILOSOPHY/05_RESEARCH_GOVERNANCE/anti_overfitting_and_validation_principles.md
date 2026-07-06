# Anti-Overfitting And Validation Principles

Fecha: 2026-07-05
Estado: principles_initial

## Tesis

AlphaEvolve amplifica el evaluator.

Si el evaluator mide ruido, amplifica overfitting.

Si el evaluator mide evidencia robusta, amplifica descubrimiento.

## Regla Financiera

En trading, muchas pruebas sobre historia finita aumentan el riesgo de falso positivo.

Por tanto, TSIS debe separar:

```text
evolution/train
validation
sealed_holdout
paper_or_shadow
production_monitoring
```

Las validaciones vistas durante el loop no son evidencia final.

## Lopez De Prado Como Sistema Inmunologico

```text
AlphaEvolve = generador de hipotesis
Lopez de Prado / statistical validation = sistema inmunologico contra autoengano
```

DSR, PBO, CSCV, purged CV, walk-forward y baselines no deben ser decoracion.

Deben operar como:

```text
gates
penalties
selection-bias accounting
promotion requirements
```

## Regla

No se promociona conocimiento sin registrar el historial de intentos relevantes.

Si no se registra lo que se probo y fallo, no se puede medir bien el riesgo de seleccion.
