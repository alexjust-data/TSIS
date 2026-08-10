# Daily PIT Fundamental Context Outputs Reference v0_1

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `daily_pit_fundamental_context_outputs_reference` |
| `document_version` | `v0_1` |
| `document_role` | `DAILY_HUMAN_REFERENCE` |
| `document_status` | `ACTIVE_REFERENCE` |
| `scope` | `Fundamental Context / Universe Resolver / scanner context` |
| `created_at` | `2026-08-09` |

## 1. Respuesta corta

Con evidencia SEC, precios gobernados por TSIS y resolvers causales podemos
construir, para cada instrumento y sesion, la mejor estimacion diaria PIT
reproducible que era calculable antes del cutoff.

```text
FLOAT DIARIO EXACTO OBSERVADO
= NO

ESTIMACION DIARIA PIT REPRODUCIBLE DEL FLOAT
= SI

FLOAT % DIARIO ESTIMADO
= SI

INSIDER / AFFILIATE OWNERSHIP %
= SI, con deduplicacion y cobertura explicita

LARGE-HOLDER OWNERSHIP %
= SI

INSTITUTIONAL OWNERSHIP % AS-KNOWN
= SI, como estado derivado de vintages 13F
  y no como portfolio institucional diario real

SHARES OUTSTANDING PIT
= SI, como estimacion basada en anchors y eventos

MARKET CAP PRESESION
= SI

ENTERPRISE VALUE Y NET CASH / SHARE
= SI, como estimaciones PIT con metodologia y staleness
```

## 2. Outputs diarios objetivo

Para cada `instrument_id x session_date`, antes del cutoff gobernado:

```text
SHARES_OUTSTANDING_ESTIMATE_AS_KNOWN
FLOAT_OWNER_EXCLUSION_ESTIMATE_AS_KNOWN
FLOAT_TRADABILITY_ELIGIBILITY_ESTIMATE_AS_KNOWN
FLOAT_PERCENT_ESTIMATE_AS_KNOWN
INSIDER_AFFILIATE_OWNERSHIP_PERCENT_AS_KNOWN
LARGE_BENEFICIAL_OWNER_PERCENT_AS_KNOWN
INSTITUTIONAL_OWNERSHIP_PERCENT_AS_KNOWN
PRESESSION_REFERENCE_MARKET_CAP
ENTERPRISE_VALUE_ESTIMATE_AS_KNOWN
NET_CASH_PER_SHARE_ESTIMATE_AS_KNOWN
```

Cada output debe conservar o referenciar:

```text
measurement_at
effective_at
available_at
presession_cutoff
source_accession
source_hash
methodology_id
methodology_version
coverage_state
quality_state
freshness_state
conflict_state
causality_state
```

## 3. Shares outstanding

```text
SHARES_OUTSTANDING_ESTIMATE_AS_KNOWN
= ultimo anchor reportado disponible
  + eventos intermedios causalmente soportados
  + transformaciones corporativas deterministas
```

No utilizar como sustitutos canonicos:

```text
basic weighted-average shares
diluted weighted-average shares
valor actual aplicado retrospectivamente
```

Los anchors posteriores no pueden reescribir el estado PIT que era conocible
antes de su publicacion.

## 4. Float owner-exclusion

```text
FLOAT_OWNER_EXCLUSION_ESTIMATE
= SHARES_OUTSTANDING_ESTIMATE
  - acciones comunes emitidas unicas excluidas
```

Las exclusiones dependen de una metodologia versionada y pueden comprender:

```text
officers
directors
affiliates o control persons
grandes beneficial owners segun threshold congelado
```

```text
FLOAT_PERCENT_ESTIMATE
= FLOAT_OWNER_EXCLUSION_ESTIMATE
  / SHARES_OUTSTANDING_ESTIMATE
  * 100
```

Ejemplo:

```text
shares outstanding = 6.84M
acciones excluidas = 3.01M
float estimado     = 3.83M
float estimado %   = 56.0%
```

## 5. Float tradability eligibility

```text
OWNER-EXCLUSION FLOAT
!= TRADABILITY-ELIGIBILITY FLOAT
```

El segundo puede incorporar evidencia de lockups, restricted shares, resale
registrations, Rule 144 eligibility, selling-stockholder registrations y
restricciones contractuales. Elegibilidad para reventa no demuestra oferta
negociable efectiva.

## 6. Ownership percentages

```text
INSIDER_AFFILIATE_OWNERSHIP_PERCENT
= acciones unicas de officers, directors y affiliates
  / shares outstanding estimate
  * 100

LARGE_HOLDER_OWNERSHIP_PERCENT
= acciones unicas de grandes holders
  / shares outstanding estimate
  * 100

institutional_pct_of_os
= institutional shares as-known / shares outstanding estimate

institutional_pct_of_float
= institutional shares as-known / float estimate
```

El ownership institucional procede de posiciones 13F trimestrales publicadas
posteriormente. El estado diario es el ultimo vintage publicamente disponible,
no la cartera institucional real de ese dia.

## 7. Deduplicacion obligatoria

No sumar directamente filas de `DEF 14A`, `13D/G`, Forms `3/4/5` y `13F`.
Una misma posicion puede aparecer bajo un individuo, una entidad controlada y
un grupo.

```text
canonical_holder_id
canonical_holder_group_id
economic_position_id
overlap_group_id
```

La misma posicion economica debe contarse una sola vez dentro de cada
metodologia.

## 8. Market cap presesion

```text
PRESESSION_REFERENCE_MARKET_CAP
= PRESESSION_REFERENCE_PRICE
  * SHARES_OUTSTANDING_ESTIMATE_AS_KNOWN
```

SEC aporta evidencia de shares. TSIS aporta el precio causal gobernado antes
del cutoff. Conservar `REFERENCE` si se utiliza prior eligible close.

## 9. Enterprise value

Metodologia candidata, sujeta a contrato exacto:

```text
ENTERPRISE_VALUE_ESTIMATE
= market cap
  + total debt
  + preferred equity
  + non-controlling interests
  - cash and cash equivalents
```

Cada componente debe ser PIT, conservar antiguedad y no mezclar definiciones
contables incompatibles.

## 10. Net cash por accion

```text
NET_CASH_PER_SHARE_ESTIMATE
= (cash and cash equivalents - total debt)
  / shares outstanding estimate
```

Mantener separados `cash_per_share`, `net_cash_per_share` y
`net_current_asset_value_per_share`.

## 11. Por que el estado es diario

SEC no publica todos estos valores cada dia. TSIS resuelve una funcion
escalonada a partir de eventos dispersos:

```text
nuevo filing o evento disponible
-> actualizar knowledge state

dia sin nueva evidencia
-> conservar el ultimo estado causalmente disponible

amendment posterior
-> actualizar desde su available_at
   sin reescribir retrospectivamente el conocimiento previo
```

```text
DAILY PIT STATE
= estado resuelto para cada sesion

DAILY OBSERVED FACT
= NO
```

## 12. Limites epistemicos

La evidencia publica normalmente no permite garantizar:

```text
float economico exacto de cada dia
acciones efectivamente disponibles para vender
legend removal real
ventas privadas aun no divulgadas
cambios de holder antes de publicacion
portfolio institucional diario real
```

La afirmacion institucional permitida es:

```text
BEST REPRODUCIBLE DAILY PIT ESTIMATE
SUPPORTED BY PUBLIC INFORMATION AVAILABLE
BEFORE EACH GOVERNED SESSION CUTOFF
```

No se permite afirmar `EXACT HISTORICAL DAILY FLOAT`.

## 13. Fuentes principales

```text
shares outstanding:
10-K, 10-Q, 20-F, 40-F, 8-K/6-K relevantes,
registration statements, prospectuses y XBRL

owner exclusion:
DEF 14A, 13D/G, Forms 3/4/5 y ownership disclosures

tradability eligibility:
resale registrations, EFFECT, lockups, Rule 144 evidence
y selling-stockholder disclosures

institutional ownership:
13F + mapeo historico CUSIP / security class

cash and debt:
Company Facts + financial-statement XBRL

price:
fuente de mercado gobernada por TSIS
```

## 14. Dependencias activas

Este artefacto es una referencia diaria. No sustituye:

```text
SEC_PIT_FUNDAMENTAL_ACQUISITION_AND_RESOLUTION_CONTRACT_v0_1.md
FLOAT_CONTEXT_SOURCE_AUDIT_PLAN_v0_1.md
POPULATION_TARGET_PIT_RECOVERY_AND_GOVERNANCE_PLAN_v0_1.md
contratos futuros de shares, ownership, float, EV y net cash
source gates y readouts ejecutados
```
