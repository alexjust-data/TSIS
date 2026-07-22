# Daily Adjusted Full-Universe Promotion Plan `v0_1`

## 1. Decision

La direccion objetivo de `daily_adjusted` ya no es quedarse como piloto estrecho.

La direccion objetivo recomendada es:

- cobertura completa del universo `daily`
- para el rango historico operativo `2005-2026`

Ruta canonica objetivo:

- `E:\TSIS\data\ohlcv_daily_adjusted`

## 2. Por que aqui si tiene sentido full-universe

En `daily`, una promocion full-universe es razonable porque:

- la capa representa verdad economica lenta;
- sirve a labels, benchmark, returns y evaluacion;
- no depende de microestructura fina;
- y una vez validada semantica y operativamente, su coste conceptual es bajo y su valor transversal es alto.

## 3. Que ya esta cerrado

Ya estan cerradas estas piezas:

- contrato de dataset
- schema minimo
- materializador ejecutable
- smoke test tecnico
- piloto semantico `v0_2`
- primer consumidor real:
  - `daily_return_labels`

Por tanto, `daily_adjusted` ya no esta en fase de descubrimiento.

## 4. Que sigue faltando antes de declararlo full-universe oficial

Faltan solo capas de promocion operativa:

- plan de corrida completa
- estrategia de manifests y provenance
- validacion de outputs agregados
- y actualizacion del registry a estado activo cuando proceda

El estado real actual de coverage ya queda medido en:

- [daily_adjusted_full_universe_audit_v0_1.md](../inspection_dossiers/daily/daily_adjusted_full_universe_audit_v0_1.md)
- [daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md](../inspection_dossiers/daily/daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md)

Ese audit deja explicitamente fijado que la deuda pendiente ya no es semantica base, sino expansion materializada amplia:

- `10` tickers ajustados frente a `12,494` raw
- `177` archivos anuales ajustados frente a `125,438` raw

Y el audit de cola compleja fija ademas que la frontera metodologica real hoy no es una masa desconocida de `spin-offs`, sino sobre todo:

- `ticker_change` como problema de continuidad corporativa;
- y una cola pequena `SC` dentro de dividendos no `CD`.

## 5. Estrategia recomendada

La promocion no debe hacerse como una corrida ciega sin trazabilidad.

Debe hacerse en dos escalones:

### Escalon A

Expansion amplia controlada:

- por `ticker-year`
- con manifests de materializacion
- y resumen agregado de filas / archivos / tickers cubiertos

### Escalon B

Una vez cubierto todo `2005-2026` y verificada la integridad:

- elevar `daily_adjusted` a capa full-universe institucional activa

## 6. Verificaciones minimas obligatorias

Antes de declarar la promocion completa deben verificarse:

- conteo de `ticker-year` esperados frente a `D:\ohlcv_daily`
- ausencia de caidas de cobertura no explicadas
- columnas `*_split_normalized` y `*_adjusted` presentes en todos los outputs
- factores `future_split_factor` y `future_dividend_factor` plausibles
- neutralidad en tickers control sin corporate actions

## 7. Relacion con los consumidores

Esta promocion completa no se hace solo por almacenamiento.

Se hace porque los siguientes consumidores la necesitan como base estable:

- `daily_return_labels`
- `backtest_core`
- benchmark interno
- research diario de señal

## 8. Veredicto

`daily_adjusted` ya tiene suficiente madurez para planear cobertura full-universe `2005-2026`.

La fase pendiente ya no es semantica.

Es promocion operativa disciplinada.
