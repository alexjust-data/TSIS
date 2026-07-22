# Trades | Recovery | Síntesis

Con lo revisado hasta ahora, `trades` ya no debe leerse como un bloque donde casi todo `review` queda perdido.

## Buckets con recuperación posible

- `review_no_1m_reference`
  - recuperación fuerte `with_flag`
- `reference_scale_mismatch`
  - recuperación potencial, pero pendiente de demostrar reconciliación de escala
- `review_microstructure`
  - recuperación parcial según uso
- `review_1m_reference_alignment`
  - recuperación limitada según uso
- `review`
  - recuperación grande `with_flag` mediante regla simple

## Bucket no recuperable por defecto

- `bad_data`
  - sigue en `bad`

## Lectura práctica

La jerarquía provisional de recuperación queda así:

1. `review_no_1m_reference`
2. `review`
3. `review_microstructure`
4. `review_1m_reference_alignment`
5. `reference_scale_mismatch`

Razón:

- los dos primeros ya tienen perfiles muy limpios frente a `daily`
- `review_microstructure` y `review_1m_reference_alignment` se recuperan por tolerancia de uso
- `reference_scale_mismatch` necesita todavía una prueba activa de corrección

## Conclusión

En `trades`, el trabajo ya no es decidir si existe recuperación.

Sí existe.

El trabajo que queda es:

- formalizar la regla exacta de recuperación
- separar `recoverable_with_flag` de `review` no rehabilitado
- y decidir qué parte de esa recuperación puede entrar en `backtest_extended` y cuál solo en `ml_flagged`
