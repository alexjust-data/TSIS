Sí, podemos construir ahora exactamente esa Layer 1 sin esperar al trabajo SEC.

Porque su contrato declara expresamente:

```text
market-cap proxy
```

y no pretende ser todavía el market cap económico definitivo.

La Layer 1 quedaría:

```text
Parent Frame: lt1b_universe_v0_1
4.824 instrumentos
        ↓
resolución PIT a las 04:00 ET
        ↓
prior eligible RTH close
×
últimas weighted-average shares disponibles
        ↓
filtros de precio y market-cap proxy
        ↓
Daily Eligible Universe
congelado para toda la sesión
```

Política exacta:

```text
0.50 <= presession_reference_price <= 20.00

presession_reference_market_cap_proxy_usd
< 100,000,000

shares selection:
    diluted weighted-average
    else basic weighted-average

shares TTL:
    <= 180 días

availability:
    shares_as_of_date < session_date

price:
    prior eligible RTH close
```

## Qué representa

Esta Layer 1 responderá legítimamente:

> ¿Qué instrumentos habrían pertenecido, antes de abrir la sesión, a nuestro universo experimental aplicando el proxy histórico disponible?

Es adecuada para:

- construir el Screener Engine;
- congelar el universo diario;
- ejecutar Light Observation;
- desarrollar Wake-Up;
- reproducir scanners históricos;
- realizar experimentos comparativos;
- alimentar backtests explícitamente provisionales.

## Qué no representa

No debemos presentarla como:

```text
market cap real PIT
```

porque weighted-average shares no son exactamente O/S.

Por eso recomiendo que los campos sean inequívocos:

```text
presession_reference_market_cap_proxy_usd
market_cap_proxy_filter_passed
shares_proxy_value
shares_proxy_basis
shares_proxy_as_of_date
shares_proxy_age_days
eligibility_semantics_version
```

Y no simplemente:

```text
market_cap_usd
```

## Estados obligatorios

Los 4.824 instrumentos deben conservarse diariamente con estados como:

```text
ELIGIBLE_PROXY
INELIGIBLE_PRICE
INELIGIBLE_MARKET_CAP_PROXY
UNAVAILABLE_PRICE
UNAVAILABLE_SHARES_PROXY
STALE_SHARES_PROXY
INSTRUMENT_INTERVAL_INACTIVE
SECURITY_CLASS_EXCLUDED
QUALITY_REVIEW
```

No debemos eliminar las filas no elegibles o desconocidas.

## Autoridad y versionado

Podemos llamarla:

```text
daily_eligible_universe_proxy_v0_1
```

con:

```text
promotion_state = EXPERIMENTAL_VALIDATED_FOR_PROXY_SCOPE
```

Y congelar cada sesión mediante:

```text
session_date
cutoff_at = 04:00 ET
input_manifest_hash
policy_version
output_hash
```

Cuando SEC proporcione O/S PIT fiable, no sobrescribiremos este universo. Crearemos:

```text
daily_eligible_universe_sec_os_pit_v0_1
```

y compararemos ambos.

## Decisión

```text
Construir Layer 1 ahora                  SÍ
Usarla para la fase 1 del Screener       SÍ
Congelarla por sesión                    SÍ
Usar market-cap proxy <100M              SÍ
Esperar a terminar ownership/float       NO
Llamarlo market cap real                 NO
Promoverlo como universo definitivo      NO
```

Así que sí: **la Layer 1 que has mostrado es exactamente el siguiente trabajo que podemos realizar ahora**, siempre que permanezca explícitamente versionada como universo basado en `market-cap proxy`.
