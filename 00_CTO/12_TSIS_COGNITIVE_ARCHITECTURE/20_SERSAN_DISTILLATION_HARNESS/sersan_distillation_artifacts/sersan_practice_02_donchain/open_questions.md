# Open Questions: sersan_practice_02_donchain

Fecha: 2026-06-11

## 1. Thresholds de filtros

La clase menciona 30-50 operaciones afectadas como minimo practico para evaluar
un filtro. TSIS debe decidir thresholds por frecuencia, asset class, universo y
tipo de sistema.

## 2. Traduccion a small caps

La parte de contratos continuos aplica directamente a futuros. Para small caps,
la traduccion debe hacerse a splits, dividendos, halts, delistings, liquidez,
survivorship y semantica adjusted/unadjusted.

## 3. Benchmark canonico

Para acciones individuales aparece buy and hold. TSIS debe definir benchmarks
por estrategia: buy and hold del activo, equal-weight universe, benchmark
sectorial, Russell 2000, microcap index o cash.

## 4. Eventos de salida minimos

El contrato debe fijar cuantos eventos por motivo de salida bastan para decir
que stop, target, trailing o time exit han sido evaluados.

## 5. Ruta de validacion para sistemas simples

La clase permite forward testing o muestra amplia cuando hay pocos parametros.
TSIS debe decidir cuando esa ruta sustituye a walk-forward y cuando no.

## 6. OCR de imagenes

Este piloto lee manualmente las capturas criticas. El Harness futuro debe
definir si usa OCR/vision model, doble lectura humana o ambos.

## 7. Costes y realismo

La practica no cierra una politica canonica de comisiones, slippage, liquidez o
halts. Para small caps, esta politica debe ser gate antes de AlphaEvolve.
