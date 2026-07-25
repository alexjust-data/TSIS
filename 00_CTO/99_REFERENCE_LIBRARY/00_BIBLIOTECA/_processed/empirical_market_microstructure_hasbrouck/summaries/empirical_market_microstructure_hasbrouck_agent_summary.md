# Empirical Market Microstructure - Joel Hasbrouck

Resumen operativo para agentes TSIS.

## Menu

- [Resumen ejecutivo](#resumen-ejecutivo)
- [Rol dentro de TSIS](#rol-dentro-de-tsis)
- [Mapa rapido](#mapa-rapido)
- [Part I - Precios, spreads y modelos univariantes](#part-i---precios-spreads-y-modelos-univariantes)
- [Part II - Trades, precios y VAR](#part-ii---trades-precios-y-var)
- [Part III - Limit orders](#part-iii---limit-orders)
- [Part IV - Liquidez y asset pricing](#part-iv---liquidez-y-asset-pricing)
- [Blueprint TSIS derivado](#blueprint-tsis-derivado)
- [Quality gates](#quality-gates)
- [Limitaciones](#limitaciones)

## Resumen ejecutivo

Hasbrouck es una fuente academica seria para entender que ocurre dentro del mercado cuando se observan trades, quotes, spreads, order flow y limit orders. No ensena a programar un backtester, pero si define el lenguaje conceptual para construir un `ExecutionSimulator` que no sea ingenuo.

Para TSIS small caps es especialmente valioso porque obliga a separar:

```text
efficient price
observed transaction price
bid/ask quote
trade direction
inventory/liquidity effect
information effect
noise
```

La idea central para backtesting profesional es que el precio observado no es "el precio verdadero". El trade price contiene microstructure noise, spread, direccion de la orden, informacion y efectos de inventario. Por tanto, un fill model serio no puede limitarse a "ejecutar al close" o "ejecutar al ultimo trade".

## Rol dentro de TSIS

Encaja en:

```text
QuoteEvent
TradeEvent
OrderFlowBuilder
NBBOState
SpreadModel
SlippageModel
PriceImpactModel
AdverseSelectionAudit
OrderBookFeatureStore
MicrostructureResearch
```

No debe usarse como guia principal para:

- disenar la cola event-driven;
- implementar OMS;
- crear arquitectura Python;
- validar overfitting tipo PBO/DSR.

## Mapa rapido

| Parte | Contenido | Uso TSIS |
|---|---|---|
| Part I | martingales, Roll model, MA/AR, asymmetric information, random-walk decomposition | `SpreadModel`, `EfficientPriceEstimate`, `MicrostructureNoiseModel` |
| Part II | trade direction, inventory control, VAR, impulse response, structural trade/price models, PIN, cointegration | `OrderFlowBuilder`, `PriceImpactModel`, `InformationAsymmetryFeature` |
| Part III | economics of limit orders, execution uncertainty, submission strategies, dynamic equilibrium | `LimitOrderFillModel`, `QueueApproximation`, `HiddenLiquidityModel` |
| Part IV | fixed transaction costs, liquidity premia, liquidity measures, stochastic liquidity | `LiquidityGate`, `CapacityModel`, `AssetPricingLiquidityFeature` |

## Part I - Precios, spreads y modelos univariantes

Hasbrouck empieza con la propiedad martingala de precios eficientes y despues muestra por que los precios observados de mercado se desvien de ese proceso ideal. El modelo de Roll introduce una representacion simple:

```text
transaction_price = efficient_price + spread_component * trade_direction
```

Para TSIS, esto significa que el backtester debe mantener separadas estas entidades:

```text
midprice
bid
ask
last_trade_price
trade_direction
spread
microstructure_noise
```

El libro tambien usa el Roll model para introducir representaciones MA/AR y descomposiciones random-walk/noise. Esto es importante para interpretar datos intradia: la autocorrelacion negativa de cambios de precio puede ser pura mecanica de bid/ask bounce, no alpha.

## Part II - Trades, precios y VAR

La parte multivariante conecta trade direction y price changes. La herramienta principal es VAR/VMA con impulse response y forecast variance decomposition.

Aplicacion TSIS:

```text
signed_trade_flow -> price_response
```

Esto permite distinguir:

- impacto transitorio;
- impacto permanente;
- informacion incorporada al precio;
- noise que revierte.

Para small caps, donde un solo comprador agresivo puede mover el tape, esta parte es clave para disenar:

```text
aggressor_side_inference
order_flow_imbalance
adverse_selection_score
price_impact_estimate
```

La seccion de cointegracion y price discovery tambien ayuda cuando el mismo activo cotiza en varios venues, o cuando se comparan ETF/componentes, ADR/listing local, o derivados/subyacente.

## Part III - Limit orders

Las limit orders no son simples "ordenes al precio limite". Tienen incertidumbre de ejecucion, seleccion adversa y decisiones estrategicas de colocacion.

Para TSIS:

```text
limit_order_fill_probability != deterministic
```

Un fill model de limit orders debe declarar:

- si asume prioridad en cola;
- si usa bid/ask solamente;
- si consume trades impresos;
- si simula hidden liquidity;
- si estima probabilidad de ejecucion;
- si penaliza seleccion adversa tras fill.

En v0.1 puede ser simple, pero el supuesto debe quedar escrito.

## Part IV - Liquidez y asset pricing

La liquidez tiene precio. No es solo coste de ejecucion puntual; tambien puede afectar expected returns. Hasbrouck repasa medidas como liquidity ratio, illiquidity ratio y reversal measures.

Para TSIS small caps:

```text
liquidity is a strategy condition, not a report-only metric
```

Campos recomendados:

```text
quoted_spread_bps
effective_spread_bps
realized_spread_bps
depth_proxy
dollar_volume
amihud_illiq
reversal_after_trade
time_to_fill
```

## Blueprint TSIS derivado

```text
Raw trades/quotes
    -> QuoteEvent / TradeEvent
    -> NBBOState
    -> TradeDirectionClassifier
    -> OrderFlowBuilder
    -> SpreadEstimator
    -> EfficientPriceEstimator
    -> PriceImpactModel
    -> FillModel
    -> AdverseSelectionAudit
```

## Quality gates

- No usar `last_price` como precio ejecutable sin justificarlo.
- Separar bid, ask, mid y last.
- Marcar si trade direction es observado o inferido.
- Medir spread y liquidez antes de aceptar fills small caps.
- Distinguir impacto permanente y transitorio cuando se mida order flow.
- Declarar si limit orders tienen o no prioridad de cola.
- No tratar autocorrelacion intradia como alpha sin descartar bid/ask bounce.

## Limitaciones

Es academico y orientado a modelos empiricos. No proporciona una arquitectura de software, ni un OMS, ni codigo Python moderno. Se debe cruzar con Johnson para ejecucion/DMA, Harris para ordenes/liquidez y Nautilus/LEAN para arquitectura de motor.

